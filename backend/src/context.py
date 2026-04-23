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
