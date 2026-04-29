"""Backend API Server entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_swagger import patch_fastapi

from .config import Config
from .database import Database
from .shared.todo import TodoError
from .status.router import status
# from .routers import (
#     create_account,
#     create_status,
#     create_user,
# )


def create_app(cfg: Config) -> FastAPI:
    """Application factory to create server instance from given config."""
    # configure database
    Database.configure(cfg)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        """Load database on startup & cleanup on shutdown."""
        await Database.create_pool()
        yield
        await Database.destroy_pool()

    app = FastAPI(
        lifespan=lifespan,
        root_path=cfg.root_path,
        # disable built-in docs/static paths, then...
        docs_url=None,
        swagger_ui_oauth2_redirect_url=None,
    )
    # ...replace them w/ locally hosted paths
    patch_fastapi(app)

    @app.exception_handler(TodoError)
    async def todo_sends_501(req: Request, exc: TodoError) -> JSONResponse:
        print(repr(exc))

        return JSONResponse(
            status_code=501,
            content={
                "error": str(exc),
                "request": {
                    "url": str(req.url),
                    "method": req.method,
                    "headers": str(req.headers),
                    "query_parameters": str(req.query_params),
                },
            },
        )

    app.include_router(status, prefix="/status")
    # app.include_router(create_user(cfg))
    # app.include_router(create_account(cfg))

    return app
