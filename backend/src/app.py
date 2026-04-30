"""Backend API Server entry point."""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi_swagger import patch_fastapi

from .config import get_config
from .database import NoResultFound, build_client
from .shared.todo import TodoError

from .account.router import account
from .status.router import status
from .token.router import token
from .user.router import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load database on startup & cleanup on shutdown."""
    # grab dep injector fn's directly from app instance provided
    # workaround from https://github.com/fastapi/fastapi/discussions/8208#discussioncomment-7862193
    cfg = app.dependency_overrides.get(get_config, get_config)()
    app.state.db = build_client(cfg)

    try:
        await app.state.db.connect()
        yield
    finally:
        # cleanup in finally to ensure graceful shutdown even when app instance crashes
        await app.state.db.disconnect()


app = FastAPI(
    lifespan=lifespan,
    # seems hacky to get root_path straight from env instead of through Config,
    # but it's the only way i've found that doesn't instantiate Config first before
    # dependency overrides can be set (if needed in testing)
    root_path=os.getenv("API_ROOT_PATH", default=""),
    # disable built-in docs/static paths, then...
    docs_url=None,
    swagger_ui_oauth2_redirect_url=None,
)
# ...replace them w/ locally hosted paths
patch_fastapi(app)


@app.exception_handler(NoResultFound)
async def no_result_sends_404(_: Request, exc: NoResultFound) -> JSONResponse:
    """Return 404 when db fails to find requested item & it propagates up to here."""
    raise HTTPException(
        status_code=404, detail="The requested resource does not exist."
    )


@app.exception_handler(TodoError)
async def todo_sends_501(_: Request, exc: TodoError) -> JSONResponse:
    """Return more specific code for endpoints that have incomplete implementation."""
    raise HTTPException(status_code=501, detail=str(exc))


app.include_router(status, prefix="/status")
app.include_router(user, prefix="/user")
app.include_router(account, prefix="/account")
app.include_router(token, prefix="/token")
