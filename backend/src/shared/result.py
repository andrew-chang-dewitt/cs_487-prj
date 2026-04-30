"""Functions for working w/ falliable Result types."""

from typing import Protocol


class Result[T, E]:
    """Falliable type of T or E."""

    _ok: T | None = None
    _err: E | None = None


class Ok[T]:
    """Shortcut to creating an Ok Result[T,_]."""

    def __new__(_, val: T):
        res = Result()
        res._ok = val

        return res
