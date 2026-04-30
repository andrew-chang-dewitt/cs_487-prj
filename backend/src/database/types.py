"""Abstract the interface for interacting w/ database.

Allows implementing alternate interfaces. Especially useful during testing.
"""

from typing import Protocol, Sequence


class DbClientProtocol[Q, P, R: Sequence](Protocol):
    """Required behaviour for database clients."""

    async def connect(self) -> None:
        """Create a database connection pool."""
        ...

    async def disconnect(self) -> None:
        """Close database connection pool."""
        ...

    async def execute_and_return(
        self,
        query: Q,
        params: P | None = None,
    ) -> R:
        """Execute query on database & return result as sequence of records."""
        ...
