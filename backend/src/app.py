"""Backend API Server entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_swagger import patch_fastapi

from src.context import Context
from src.errors import TodoError
from src.routers import (
    create_account,
    create_status,
    create_user,
)


def create_app(ctx: Context = Context()) -> FastAPI:
    """Application factory to create server instance from given config."""
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Load database on startup & cleanup on shutdown."""
        await ctx.database.connect()
        yield
        await ctx.database.disconnect()

    app = FastAPI(
        lifespan=lifespan,
        root_path=ctx.root_path,
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

    app.include_router(create_status(ctx))
    app.include_router(create_user(ctx))
    app.include_router(create_account(ctx))

    return app
