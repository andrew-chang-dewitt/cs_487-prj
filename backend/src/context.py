"""Shared state used accross the application."""

from .config import Config
from .database import Client, create_client, create_conn_config


class Context:
    """Object containing shared application context used at runtime.

    Includes items such as:

    - database client
    """

    database: Client
    root_path: str
    jwt_key: str

    def __init__(self, config: Config = Config()) -> None:
        self.database = create_client(
            create_conn_config(
                user=config.db_user,
                password=config.db_password,
                host=config.db_host,
                port=config.db_port,
                database=config.db_name,
            )
        )
        self.root_path = config.root_path

        if config.jwt_key is None:
            self.jwt_key = _get_app_key_from_file()
        else:
            self.jwt_key = config.jwt_key


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
