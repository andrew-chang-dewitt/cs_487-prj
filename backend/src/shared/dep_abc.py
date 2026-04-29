"""ABC for objects capable of being used for dependency injection in FastAPI."""

from abc import ABC

from src.shared.optional import expect


class Dep[T](ABC):
    """Default behaviour for shared dependency object."""

    _item: T | None = None

    @classmethod
    def set(cls, item: T) -> None:
        """Set value for shared dependency."""
        cls._item = item

    @classmethod
    def get(cls) -> T:
        """Get value of shared dependency."""
        return expect(
            cls._item,
            "Dependency must be set (using `Dep.set(item)`) before "
            + "it can be referenced via `Depends(Dep.get)`.",
        )
