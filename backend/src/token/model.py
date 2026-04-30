"""Token data Models."""

from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    """Token fields."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload."""

    user_id: UUID
