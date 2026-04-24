"""Shared state used accross the application."""

from .config import Config


class Context:
    """Object containing shared application context used at runtime.

    Includes items such as:

    - database client
    """

    # FIXME: have this hold a database connection when that's implemented!
    database: bool
    root_path: str

    def __init__(self, config: Config = Config()) -> None:
        self.database = True
        self.root_path = config.root_path
