"""Expose the package-level application instance for import by the server."""

from src.app import create_app

app = create_app(None)
