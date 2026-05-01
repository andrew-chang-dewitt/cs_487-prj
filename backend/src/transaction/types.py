"""Transaction data types."""

from typing import Annotated

from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import Field

from src.shared.models.base import Base, BaseDb


type Amount = Annotated[Decimal, Field(max_places=2)]


class TransactionBase(Base):
    """Base Transaction fields."""

    amount: Amount
    description: str
    payee: str
    timestamp: datetime
    account_id: UUID
    spent_from: UUID | None = None


class TransactionIn(TransactionBase):
    """Fields used when creating a new Transaction."""

    # simply a copy of TransactionBase for now


class TransactionOut(TransactionBase, BaseDb):
    """Fields used when reading a Transaction."""

    # adds `id` from BaseDb


class TransactionChanges(Base):
    """Object for changing any of the fields on an existing Transaction."""

    amount: Amount | None = None
    description: str | None = None
    payee: str | None = None
    timestamp: datetime | None = None
    account_id: UUID | None = None
    spent_from: UUID | None = None
