"""Application config."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


def _get_app_key_from_file() -> str:
    secrets_files = (f for f in ["/run/secrets/app_key", "./.secrets/app_key.txt"])

    app_key: str | None = None

    # check list of paths for key
    for path in secrets_files:
        try:
            with open(path, "r") as key_file:
                app_key = str(key_file.readline())
                # exit iteration when first key is found
                break
        except FileNotFoundError:
            pass

    if app_key is None:
        raise ValueError(
            "No value for backend Application Key found in enviornment or secrets."
        )

    return app_key


class Config(BaseSettings):
    """Application configuration object."""

    # database connection parameters
    # configuration values come from /docker-compose.yml
    db_host: str = Field("localhost")
    db_port: int = Field(5432)
    db_name: str = Field("finance")
    db_user: str = Field("postgres")
    db_password: str = Field("postgres")
    # load jwt key from env or from secrets file
    jwt_key: str = Field(_get_app_key_from_file())


@lru_cache
def get_config() -> Config:
    """Provide app config for dependency injection.

    Caches to build only once, then provide the same Config instance on
    subsequent calls.
    """
    return Config()
