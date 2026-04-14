"""Utility functions."""

from typing import Optional, Union, TypeGuard


def is_some[T](opt: Optional[T] | Union[T, None]) -> TypeGuard[T]:
    """Check if given Option is Some."""
    return opt is not None


def some_or_default[T](opt: Optional[T] | Union[T, None], default: T) -> T:
    """Return the contained 'Some' value, or the provided default."""
    if is_some(opt):
        return opt

    return default
