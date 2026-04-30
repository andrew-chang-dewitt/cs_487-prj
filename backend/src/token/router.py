"""Routes under `/token`."""

from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import CredentialsException, encode_token
from src.config import Config, get_config
from src.database import NoResultFound
from src.user.model import UserModel, get_user_model

from .model import Token

token = APIRouter(tags=["Authentication"])


# add post_token route
@token.post(
    "",
    response_model=Token,
    summary="Get an authentication Token via an OAuth2 Request Form.",
)
async def post(
    cfg: Annotated[Config, Depends(get_config)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    model: Annotated[UserModel, Depends(get_user_model)],
) -> Token:
    """POST `/token` handler."""
    # get user by username & password, return token if auth'd
    # send 401 Unauthorized if model returns no result
    try:
        user = await model.read.authenticate(
            handle=form_data.username, password=form_data.password
        )
    except NoResultFound as exc:
        raise CredentialsException() from exc

    token = encode_token(user_id=user.id, key=cfg.jwt_key)

    return Token(access_token=token)
