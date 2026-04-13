"""Backend API Server entry point."""

from typing import Optional

from fastapi import FastAPI

from .config import Config
from .routers import (
    status,
    create_user,
)


def create_app(config: Optional[Config] = None) -> FastAPI:
    """Application factory to create server instance from given config."""
    if config is None:
        config = Config()

    app = FastAPI(
        # openapi_url="/api/openapi.json",
        root_path=config.root_path,
    )

    @app.get("/")
    def read_root():
        return {"Hello": "World"}

    app.include_router(status)
    app.include_router(create_user(config))

    return app
