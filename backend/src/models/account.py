"""Account* data objects."""

from uuid import UUID

from typing import Optional

from pydantic import BaseModel

from .dummy_model import DummyModel


class AccountBase(BaseModel):
    """Common fields for user Accounts."""

    name: str
    closed: bool


class AccountIn(AccountBase):
    """Fields needed from user to create an Account."""

    closed: bool = False


class AccountChanges(AccountBase):
    """Fields used when updating an Account, all are optional."""

    name: Optional[str] = None
    closed: Optional[bool] = None


class AccountNewDb(AccountBase):
    """Information needed to save a new account to the database."""

    user_id: UUID


class AccountOut(AccountNewDb):
    """Fields returned by Account queries."""

    id: UUID


class AccountModel(DummyModel):
    """Dummy ORM for Account objects."""

    class Read(DummyModel.Read):
        """Add read many by user method."""

        async def many_by_user(
            self, user_id: UUID, closed: bool = False
        ) -> list[AccountOut]:
            """Return accounts for the given user, filtered by closed status."""
            raise NotImplementedError("TODO...")

    read: Read

    def __init__(self) -> None:
        super().__init__()
        self.read = AccountModel.Read()
