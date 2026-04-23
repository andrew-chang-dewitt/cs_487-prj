"""Application config."""

from dataclasses import dataclass
import os


@dataclass
class Config:
    """Application configuration object."""

    # specify url prefix to use before the api route (e.g. a `root_path` of
    # "/api" means a route defined in app to be at "/some/path" will actually
    # be at "/api/some/path")
    root_path: str = os.getenv("API_ROOT_PATH", default="")

    # database connection parameters
    # configuration values come from /docker-compose.yml
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_name: str = os.getenv("DB_NAME", "finance")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")

    # application key used for auth token signing
    jwt_key: str | None = os.getenv("APP_KEY")
