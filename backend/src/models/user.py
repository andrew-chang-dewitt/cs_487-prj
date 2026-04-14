"""User* data objects."""

from typing import Optional
from uuid import UUID

from psycopg2.errors import UniqueViolation  # type: ignore
from pydantic import BaseModel

from .errors import DuplicateError
from .dummy_model import DummyModel


class UserBase(BaseModel):
    """Common fields to all User objects."""

    handle: str
    full_name: str
    preferred_name: str


class UserIn(UserBase):
    """Fields required to create a new User."""

    password: str


class UserChanges(BaseModel):
    """Fields used when updating a User, all are optional."""

    handle: Optional[str] = None
    full_name: Optional[str] = None
    preferred_name: Optional[str] = None


class UserOut(UserBase):
    """Fields returned by queries on User Model."""

    id: UUID


class UserDb(UserIn):
    """All fields on User in database records."""

    id: UUID


class UserModel(DummyModel):
    """Dummy ORM for User objects."""

    class Create(DummyModel.Create):
        """Create ops."""

        async def new(self, obj: UserIn) -> UserOut:
            """Save a new User to the database & return the new information."""
            try:
                return await super().new(obj)
            except UniqueViolation as exc:
                raise DuplicateError(
                    f"User with handle {obj.handle} already exists."
                ) from exc

    class Update(DummyModel.Update):
        """Adds password method."""

        async def password(self, id: UUID, pwd: str) -> UserOut:
            """Update the password for the User identified by `id`."""
            raise NotImplementedError("TODO...")

    update: Update

    def __init__(self) -> None:
        super().__init__()
        self.update = UserModel.Update()
