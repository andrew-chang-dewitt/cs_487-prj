from typing import Optional

from fastapi import FastAPI

from config import Config


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

    @app.get("/items/{item_id}")
    def read_item(item_id: int, q: str | None = None):
        return {"item_id": item_id, "q": q}

    return app
