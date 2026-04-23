"""Routes under `/user`."""

from src.models.errors import DuplicateError

from uuid import UUID

from fastapi import status as status_code
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel

from src.context import Context
from src.models import (
    UserChanges,
    UserIn,
    UserOut,
    UserModel,
)


class PasswordChange(BaseModel):
    """Request body for updating the current user's password."""

    new_password: str


def create_user(ctx: Context) -> APIRouter:
    """Create a user router & model from given config."""
    model = UserModel(ctx.database)

    user = APIRouter(prefix="/user", tags=["User"])

    @user.post(
        "",
        status_code=status_code.HTTP_201_CREATED,
        response_model=UserOut,
        summary="Create a new User.",
    )
    async def post_user(new_user: UserIn) -> UserOut:
        """Save a new User to the database & return the new information."""
        try:
            return await model.create.new(new_user)
        except DuplicateError as exc:
            raise HTTPException(
                409,
                detail=exc.msg,
            ) from exc

    @user.get(
        "", response_model=UserOut, summary="Get the currently authenticated User."
    )
    async def get_user(user_id: UUID) -> UserOut:
        """Get the current user's information."""
        return await model.read.one_by_id(user_id)

    @user.put(
        "",
        response_model=UserOut,
        summary="Update the currently authenticated User's information.",
    )
    async def put_user(changes: UserChanges, user_id: UUID) -> UserOut:
        """Update the current user's information."""
        return await model.update.changes(user_id, changes)

    @user.put(
        "/password",
        response_model=UserOut,
        summary="Update the currently authenticated User's password.",
    )
    async def put_password(
        user_id: UUID,
        password_change: PasswordChange,
    ) -> UserOut:
        """Update the current user's password."""
        result = await model.update.password(user_id, password_change.new_password)

        return result

    @user.delete(
        "", response_model=UserOut, summary="Delete the currently authenticated User."
    )
    async def delete_user(user_id: UUID) -> UserOut:
        """Delete the current user from the database."""
        return await model.delete.one_by_id(str(user_id))

    return user
