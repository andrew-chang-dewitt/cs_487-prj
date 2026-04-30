"""Functions for working w/ Optional or Union[_, None] types."""

from typing import Optional, Union, TypeGuard


class PanicUnwrap[T](Exception):
    """Raised when attempting to unwrap Optional[T] that is None."""

    def __init__(self, msg: str = "Attempted to unwrap Optional that is None.") -> None:
        super().__init__(msg)


def expect[T](opt: Optional[T] | Union[T, None], msg: str) -> T:
    """Get T from Optional[T] or raise PanicUnwrap with provided message if None."""
    if is_some(opt):
        return opt

    raise PanicUnwrap(msg)


def unwrap[T](opt: Optional[T] | Union[T, None]) -> T:
    """Get T from Optional[T] or raise PanicUnwrap if None."""
    if is_some(opt):
        return opt

    raise PanicUnwrap()


def is_some[T](opt: Optional[T] | Union[T, None]) -> TypeGuard[T]:
    """Check if given Option is Some."""
    return opt is not None


def some_or_default[T](opt: Optional[T] | Union[T, None], default: T) -> T:
    """Return the contained 'Some' value, or the provided default."""
    if is_some(opt):
        return opt

    return default
