"""Account data types."""

from uuid import UUID

from src.shared.models.base import Base, BaseDb


class AccountBase(Base):
    """Common fields for user Accounts."""

    name: str
    closed: bool


class AccountIn(AccountBase):
    """Fields needed from user to create an Account."""

    closed: bool = False


class AccountChanges(AccountBase):
    """Fields used when updating an Account, all are optional."""

    closed: bool | None = None
    name: str | None = None


class AccountNew(AccountBase):
    """Information needed to save a new account to the database."""

    user_id: UUID


class AccountOut(AccountNew, BaseDb):
    """Fields returned by Account queries."""
