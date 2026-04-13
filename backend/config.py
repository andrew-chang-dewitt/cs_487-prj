"""Application config."""

from dataclasses import dataclass
import os


@dataclass
class Config:
    """Application configuration object."""

    root_path: str = os.getenv("API_ROOT_PATH", default="")
