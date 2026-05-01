"""Database connection helpers."""

from db_wrapper import AsyncClient as DbClient, ConnectionParameters
from fastapi import Request

from src.config import Config

from .errors import DuplicateError, NoResultFound
from .types import DbClientProtocol

__all__ = [
    "DbClient",
    "DbClientProtocol",
    "DuplicateError",
    "NoResultFound",
    "get_db_client",
]


def build_client(cfg: Config) -> DbClient:
    return DbClient(
        ConnectionParameters(
            host=cfg.db_host,
            port=cfg.db_port,
            user=cfg.db_user,
            password=cfg.db_password,
            database=cfg.db_name,
        )
    )


async def get_db_client(req: Request) -> DbClient:
    """Provide database client for dep injection.

    Caches to build only once, then provide the same instance on
    subsequent calls.
    """
    return req.app.state.db
