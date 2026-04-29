"""Manage database connection as shared resource.

Stores database connection & provides access to it via function for dependency
injection in FastAPI app.
"""

from db_wrapper import AsyncClient as Client, ConnectionParameters

from src.config import Config
from src.shared.dep_abc import Dep
from src.shared.optional import expect


class Database(Dep[Client]):
    """Provide database client for dependency injection."""

    @classmethod
    def configure(cls, cfg: Config) -> None:
        """Configure a database client from given Config object."""
        client = Client(
            ConnectionParameters(
                cfg.db_host, cfg.db_port, cfg.db_user, cfg.db_password, cfg.db_name
            )
        )

        cls.set(client)

    @classmethod
    async def create_pool(cls) -> None:
        """Create database connection pool."""
        await expect(
            cls._item,
            "Database must be set w/ Database.set(Client) before pool can be created",
        ).connect()

    @classmethod
    async def destroy_pool(cls) -> None:
        """Destroy database connection pool."""
        await expect(
            cls._item,
            "Database must be set w/ Database.set(Client) before pool can be destroyed",
        ).disconnect()
