"""Temporary dummy model behaviour."""

from src.errors import TodoError


class DummyModel:
    """Temporary dummy model behaviour."""

    class Create:
        """Create ops."""

        async def new[T, R](self, obj: T) -> R:
            raise TodoError()

    class Read:
        """Read ops."""

        async def one_by_id[T, R](self, obj: T) -> R:
            raise TodoError()

    class Update:
        """Update ops."""

        async def changes[T, S, R](self, obj1: T, obj2: S) -> R:
            raise TodoError()

    class Delete:
        """Delete ops."""

        async def one_by_id[T, R](self, obj: T) -> R:
            raise TodoError()

    create: Create
    read: Read
    update: Update
    delete: Delete

    def __init__(self) -> None:
        self.create = DummyModel.Create()
        self.read = DummyModel.Read()
        self.update = DummyModel.Update()
        self.delete = DummyModel.Delete()
