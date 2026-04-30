"""Routes under `/account`."""

from typing import Annotated

from uuid import UUID

from fastapi import status as status_code, Depends
from fastapi.routing import APIRouter

from src.auth import get_auth

from .model import get_account_model, AccountModel
from .types import (
    AccountChanges,
    AccountIn,
    AccountNew,
    AccountOut,
)


# set up account router
account = APIRouter(tags=["Account"])


# add routes
@account.post(
    "",
    response_model=AccountOut,
    status_code=status_code.HTTP_201_CREATED,
    summary="Create a new Account for the currently authenticated User.",
)
async def post(
    new_account: AccountIn,
    user_id: Annotated[UUID, Depends(get_auth)],
    model: Annotated[AccountModel, Depends(get_account_model)],
) -> AccountOut:
    """Create a new account for given User."""
    return await model.create.new(
        AccountNew(**new_account.model_dump(), user_id=user_id)
    )


@account.get(
    "",
    response_model=list[AccountOut],
    summary="Get the Accounts for the currently authenticated User.",
)
async def get(
    user_id: Annotated[UUID, Depends(get_auth)],
    model: Annotated[AccountModel, Depends(get_account_model)],
) -> list[AccountOut]:
    """Read all open accounts for given User."""
    return await model.read.many_by_user(user_id)


@account.put(
    "/{account_id}", response_model=AccountOut, summary="Update the given Account."
)
async def put_id(
    account_id: UUID,
    changes: AccountChanges,
    user_id: Annotated[UUID, Depends(get_auth)],
    model: Annotated[AccountModel, Depends(get_account_model)],
) -> AccountOut:
    """Update the given account with the given changes."""
    return await model.update.changes(account_id, user_id, changes)


@account.put(
    "/{account_id}/closed",
    response_model=AccountOut,
    summary="Mark the given Account as closed.",
)
async def put_closed(
    account_id: UUID,
    user_id: Annotated[UUID, Depends(get_auth)],
    model: Annotated[AccountModel, Depends(get_account_model)],
) -> AccountOut:
    """Mark the given account as closed."""
    return await model.update.changes(account_id, user_id, AccountChanges(closed=True))


@account.get(
    "/closed",
    response_model=list[AccountOut],
    summary="Get all closed Accounts for current User.",
)
async def get_closed(
    user_id: Annotated[UUID, Depends(get_auth)],
    model: Annotated[AccountModel, Depends(get_account_model)],
) -> list[AccountOut]:
    """Mark the given account as closed."""
    return await model.read.many_by_user(user_id, closed=True)
