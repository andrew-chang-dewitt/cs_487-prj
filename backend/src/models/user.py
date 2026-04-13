"""User* data objects."""

from uuid import UUID

from typing import Optional

from pydantic import BaseModel

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

    class Update(DummyModel.Update):
        """Adds password method."""

        async def password(self, id: UUID, pwd: str) -> UserOut:
            raise NotImplementedError("TODO...")

    update: Update
