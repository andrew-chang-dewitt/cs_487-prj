"""Expose the package-level application instance for import by the server."""

from src.config import Config
from src.app import create_app

# create app using default config
app = create_app(Config())
