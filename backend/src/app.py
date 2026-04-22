"""Backend API Server entry point."""

from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_swagger import patch_fastapi

from .config import Config
from src.errors import TodoError
from .routers import (
    status,
    create_user,
    create_account,
)


def create_app(config: Optional[Config] = None) -> FastAPI:
    """Application factory to create server instance from given config."""
    if config is None:
        config = Config()

    app = FastAPI(
        # openapi_url="/api/openapi.json",
        root_path=config.root_path,
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

    app.include_router(status)
    app.include_router(create_user(config))
    app.include_router(create_account(config))

    return app
