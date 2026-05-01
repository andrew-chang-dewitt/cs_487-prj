"""Routes under `/transaction`."""

from src.database import NoResultFound

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Callable
from uuid import UUID

from fastapi import status as status_code, Depends, Query
from fastapi.routing import APIRouter

from src.auth import get_auth, CredentialsException, get_authd_accounts
from src.shared.models.filters import (
    Condition,
    Logical,
    equals,
    greater_than_or_equal_to,
    less_than_or_equal_to,
    logical_and,
    FilterModel,
)

from .model import get_transaction_model, TransactionModel
from .types import (
    TransactionChanges,
    TransactionIn,
    TransactionOut,
)

FilterFn = Callable[..., Condition]


def a_b_both_or_none[Value](
    value_a: Value | None,
    value_b: Value | None,
    fn_a: FilterFn,
    fn_b: FilterFn,
    both_fn: Callable[..., Logical],
) -> Condition | Logical | None:
    """Determine filter query depending on given Values A & B."""
    # short circuit to None if both are None
    if value_a is None and value_b is None:
        return None

    # else parse as both function if both are present
    if value_a is not None and value_b is not None:
        return both_fn(fn_a(value_a), fn_b(value_b))

    # and single condition if only one is present
    if value_a is not None and value_b is None:
        return fn_a(value_a)

    if value_a is None and value_b is not None:
        return fn_b(value_b)


transaction = APIRouter(tags=["Transaction"])


@transaction.post(
    "",
    response_model=TransactionOut,
    status_code=status_code.HTTP_201_CREATED,
    summary="Create a new Transaction for the given Account.",
)
async def post_root(
    new_tran: TransactionIn,
    authd_accounts: Annotated[list[UUID], Depends(get_authd_accounts)],
    model: Annotated[TransactionModel, Depends(get_transaction_model)],
) -> TransactionOut:
    """Save given Transaction to database."""
    # ensure user is authorized for associated account
    if new_tran.account_id not in authd_accounts:
        raise CredentialsException()

    return await model.create.new(new_tran)


@transaction.get(
    "",
    response_model=list[TransactionOut],
    summary="Fetch all Transactions for the authenticated User.",
)
async def get_root(
    model: Annotated[TransactionModel, Depends(get_transaction_model)],
    user_id: Annotated[UUID, Depends(get_auth)],
    authd_accounts: Annotated[list[UUID], Depends(get_authd_accounts)],
    account_id: Annotated[
        UUID | None,
        Query(description="Only return Transactions belonging to this Account."),
    ] = None,
    payee: Annotated[
        str | None,
        Query(description="Only return Transactions with matching payee."),
    ] = None,
    minimum_amount: Annotated[
        Decimal | None,
        Query(
            description="Only return Transactions greater than or equal to amount.",
        ),
    ] = None,
    maximum_amount: Annotated[
        Decimal | None,
        Query(description="Only return Transactions less than or equal to amount."),
    ] = None,
    after: Annotated[
        datetime | None,
        Query(description="Only return Transactions after the given date & time."),
    ] = None,
    before: Annotated[
        datetime | None,
        Query(description="Only return Transactions before the given date & time."),
    ] = None,
    limit: Annotated[
        int,
        Query(description="Only return specified number of Transactions."),
    ] = 50,
    page: Annotated[int, Query(description="Return given page of Transactions.")] = 0,
    sort: Annotated[
        str, Query(description="Sort Transactions by given column.")
    ] = "timestamp",
) -> list[TransactionOut]:
    """Get all Transactions."""
    amount = a_b_both_or_none(
        minimum_amount,
        maximum_amount,
        greater_than_or_equal_to,
        less_than_or_equal_to,
        logical_and,
    )
    timestamp = a_b_both_or_none(
        after, before, greater_than_or_equal_to, less_than_or_equal_to, logical_and
    )

    logical_filters: FilterModel = dict()
    if timestamp is not None:
        logical_filters["timestamp"] = timestamp
    if amount is not None:
        logical_filters["amount"] = amount

    return await model.read.many_by_user(
        user_id,
        limit=limit,
        page=page,
        sort=sort,
        account_id=equals(account_id),
        payee=equals(payee),
        **logical_filters,
    )


@transaction.put(
    "/{transaction_id}",
    response_model=TransactionOut,
    summary="Edit the given Transaction.",
)
async def put_id(
    transaction_id: UUID,
    changes: TransactionChanges,
    authd_accounts: Annotated[list[UUID], Depends(get_authd_accounts)],
    model: Annotated[TransactionModel, Depends(get_transaction_model)],
) -> TransactionOut:
    """Edit the given Transaction."""
    # ensure user is authorized for associated accounts
    existing = await model.read.one_by_id(transaction_id)
    if (
        existing.account_id not in authd_accounts
        # even if the account_id is being changed
        or (
            changes.account_id is not None
            and changes.account_id not in authd_accounts
        )
    ):
        raise CredentialsException()

    return await model.update.changes(transaction_id, changes)


@transaction.delete(
    "/{transaction_id}",
    response_model=TransactionOut,
    summary="Delete the given Transaction.",
)
async def delete_id(
    transaction_id: UUID,
    authd_accounts: Annotated[list[UUID], Depends(get_authd_accounts)],
    model: Annotated[TransactionModel, Depends(get_transaction_model)],
) -> TransactionOut:
    """Delete the given Transaction."""
    # ensure user is authorized for associated account
    existing = await model.read.one_by_id(transaction_id)
    if existing.account_id not in authd_accounts:
        raise CredentialsException()

    return await model.delete.one_by_id(str(transaction_id))


@transaction.put(
    "/{transaction_id}/spent_from/{spent_from_id}",
    response_model=TransactionOut,
    summary='Mark Transaction as "spent from" the given Envelope',
)
async def put_spent_from(
    transaction_id: UUID,
    spent_from_id: UUID,
    authd_accounts: Annotated[list[UUID], Depends(get_authd_accounts)],
    model: Annotated[TransactionModel, Depends(get_transaction_model)],
) -> TransactionOut:
    """Mark Transaction as Spent From given Envelope."""
    # ensure user is authorized for associated account
    existing = await model.read.one_by_id(transaction_id)
    if existing.account_id not in authd_accounts:
        raise CredentialsException()

    return await model.update.changes(
        transaction_id, TransactionChanges(spent_from=spent_from_id)
    )
