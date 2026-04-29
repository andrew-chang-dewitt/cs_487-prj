"""Database connection helpers."""

from .dep import Database
from .errors import DuplicateError, NoResultFound

__all__ = ["Database", "DuplicateError", "NoResultFound"]
