"""Database related errors."""

from db_wrapper.model.base import NoResultFound


class DuplicateError(Exception):
    """Raised if a duplicate record already exists."""

    msg: str

    def __init__(self, msg: str) -> None:
        self.msg = msg


__all__ = ["DuplicateError", "NoResultFound"]
