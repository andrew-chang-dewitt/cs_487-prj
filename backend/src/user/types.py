"""User data types."""

from pydantic import BaseModel

from src.shared.models.base import Base, BaseDb


class UserBase(Base):
    """Common fields to all User objects."""

    handle: str
    full_name: str
    preferred_name: str


class UserIn(UserBase):
    """Fields required to create a new User."""

    password: str


class UserChanges(Base):
    """Fields used when updating a User, all are optional."""

    handle: str | None = None
    full_name: str | None = None
    preferred_name: str | None = None

    class Config:
        """Configure UserChanges Pydantic features."""

        # will now throw validation error if extra fields are given
        extra = "forbid"


class UserOut(UserBase, BaseDb):
    """Fields returned by queries on User Model."""

    def __eq__(self, other: object, /) -> bool:
        """Compare UserOut objects for equality."""
        match other:
            case UserOut():
                return (
                    self.handle == other.handle
                    and self.full_name == other.full_name
                    and self.preferred_name == other.preferred_name
                    and self.id == other.id
                )
            case _:
                raise TypeError(f"Cannot compare type {type(self)} to {type(other)}")


class UserDb(UserIn, BaseDb):
    """All fields on User in database records."""


class PasswordChange(BaseModel):
    """Request body for updating the current user's password."""

    new_password: str
