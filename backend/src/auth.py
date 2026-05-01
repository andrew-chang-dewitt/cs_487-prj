"""Security constants & methods."""

from src.config import Config, get_config

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from db_wrapper.model.base import NoResultFound
from fastapi import status as status_code, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt

from src.user.model import UserModel, get_user_model


ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class CredentialsException(HTTPException):
    """Throw when unable to process a user's credentials."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status_code.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def encode_token(
    user_id: UUID,
    key: str,
) -> str:
    """Encode & return a new JWT containing the given ID."""
    data = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(data, key, algorithm=ALGORITHM)


async def get_auth(
    cfg: Annotated[Config, Depends(get_config)],
    token: Annotated[str, Depends(oauth2_scheme)],
    user_model: Annotated[UserModel, Depends(get_user_model)],
) -> UUID:
    """Get current user ID from token."""
    try:
        payload = jwt.decode(token, cfg.jwt_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise CredentialsException() from exc

    id_str = payload.get("sub")

    if id_str is None:
        raise CredentialsException()

    user_id = UUID(id_str)

    try:
        await user_model.read.one_by_id(user_id)
    except NoResultFound:
        raise CredentialsException()

    return user_id
