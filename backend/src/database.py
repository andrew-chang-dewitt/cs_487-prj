"""Provide methods for managing database connections."""

from db_wrapper import AsyncClient as Client, ConnectionParameters

# import NoResultFound to re-export
from db_wrapper.model.base import NoResultFound  # noqa W0611


def create_conn_config(
    *,
    user: str,
    password: str,
    host: str,
    port: int,
    database: str,
) -> ConnectionParameters:
    """Create database Connection Parameters."""
    return ConnectionParameters(
        user=user, password=password, host=host, port=port, database=database
    )


def create_client(conn_params: ConnectionParameters) -> Client:
    """Create & return a database client."""
    return Client(conn_params)
