"""Status data types."""

from dataclasses import dataclass


@dataclass
class Status:
    """Status Response."""

    # pylint: disable=too-few-public-methods

    message: str = "The API is up."
    ok: bool = True
