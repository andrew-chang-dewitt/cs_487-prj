"""Errors that can be raised at the Data Model layer."""


class DuplicateError(Exception):
    """Raised if a duplicate record already exists."""

    msg: str

    def __init__(self, msg: str) -> None:
        self.msg = msg
