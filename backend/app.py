from typing import Optional

from fastapi import FastAPI


def create_app(config: Optional[str] = None) -> FastAPI:
    """Application factory to create server instance from given config."""

    app = FastAPI()

    @app.get("/")
    def read_root():
        return {"Hello": "World"}

    @app.get("/items/{item_id}")
    def read_item(item_id: int, q: str | None = None):
        return {"item_id": item_id, "q": q}

    return app
