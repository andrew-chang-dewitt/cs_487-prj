"""User* data objects."""

from typing import Any, Dict, List, Optional, Tuple, Type
from uuid import UUID

from db_wrapper.client import AsyncClient
from db_wrapper.model import (
    sql,
    AsyncModel,
    AsyncCreate,
    AsyncRead,
    AsyncUpdate,
    AsyncDelete,
    RealDictRow,
)
from db_wrapper.model.base import NoResultFound

from .base import Base, BaseDb


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

    handle: Optional[str] = None
    full_name: Optional[str] = None
    preferred_name: Optional[str] = None

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


def create_user_out(user: Dict[str, Any]) -> UserOut:
    """Strip extraneous values from dictionary to create UserOut."""
    return UserOut(
        id=user["id"],
        handle=user["handle"],
        full_name=user["full_name"],
        preferred_name=user["preferred_name"],
    )


class UserCreator(AsyncCreate[UserOut]):
    """User creation methods."""

    async def one(self, item: UserOut) -> UserOut:
        """Un-implemented to force use of create.new method."""
        raise NotImplementedError()

    async def new(self, user: UserIn) -> UserOut:
        """Replace default create.one to change input types."""
        query = sql.SQL("""
            INSERT INTO {table}(
                handle,
                password,
                full_name,
                preferred_name
            )
            VALUES (
                {handle},
                crypt({password}, gen_salt('bf')),
                {full_name},
                {preferred_name}
            )
            RETURNING id, handle, full_name, preferred_name;
        """).format(
            table=self._table,
            handle=sql.Literal(user.handle),
            password=sql.Literal(user.password),
            full_name=sql.Literal(user.full_name),
            preferred_name=sql.Literal(user.preferred_name),
        )

        query_result: List[RealDictRow] = await self._client.execute_and_return(query)

        return UserOut(**query_result[0])


class UserReader(AsyncRead[UserOut]):
    """Extended read methods for UserModel."""

    async def one_by_id(self, id_value: UUID) -> UserOut:
        """Override default behavior to hide password on output."""
        query = self._query_one_by_id(id_value)
        query_result = await self._client.execute_and_return(query)

        return create_user_out(query_result[0])

    async def authenticate(self, handle: str, password: str) -> UserOut:
        """Authorize user via given username & password, return User."""
        query = sql.SQL("""
            SELECT
                id, handle, full_name, preferred_name
            FROM
                {table}
            WHERE
                handle = {handle} AND
                password = crypt({password}, password);
        """).format(
            table=self._table,
            handle=sql.Literal(handle),
            password=sql.Literal(password),
        )

        query_result = await self._client.execute_and_return(query)

        try:
            return UserOut(**query_result[0])
        except IndexError as err:
            raise NoResultFound from err


class UserUpdater(AsyncUpdate[UserOut]):
    """Extended Updater for UserModel."""

    async def one_by_id(self, id_value: UUID, changes: Dict[str, Any]) -> UserOut:
        """Un-implemented to force use of update.changes method."""
        raise NotImplementedError()

    async def changes(self, user_id: UUID, changes: UserChanges) -> UserOut:
        """Update only the given fields for the given user."""

        def compose_one_change(change: Tuple[str, Any]) -> sql.Composed:
            key = change[0]
            value = change[1]

            return sql.SQL("{key} = {value}").format(
                key=sql.Identifier(key), value=sql.Literal(value)
            )

        def compose_changes(changes: Dict[str, Any]) -> sql.Composed:
            return sql.SQL(",").join(
                [compose_one_change(change) for change in changes.items() if change[1]]
            )

        query = sql.SQL("""
            UPDATE {table}
            SET {changes}
            WHERE id = {id_value}
            RETURNING id, handle, full_name, preferred_name;
        """).format(
            table=self._table,
            changes=compose_changes(changes.model_dump()),
            id_value=sql.Literal(str(user_id)),
        )
        query_result = await self._client.execute_and_return(query)

        try:
            return UserOut(**query_result[0])
        except IndexError as err:
            raise NoResultFound from err

    async def password(self, user_id: UUID, new_password: str) -> UserOut:
        """Update the given user's password."""
        query = sql.SQL("""
            UPDATE {table}
            SET password = crypt({password}, gen_salt('bf'))
            WHERE id = {user_id}
            RETURNING id, handle, full_name, preferred_name;
        """).format(
            table=self._table,
            password=sql.Literal(new_password),
            user_id=sql.Literal(str(user_id)),
        )
        query_result = await self._client.execute_and_return(query)

        try:
            return UserOut(**query_result[0])
        except IndexError as err:
            raise NoResultFound from err


class UserDeleter(AsyncDelete[UserOut]):
    """Extend default delete behavior."""

    async def one_by_id(self, id_value: str) -> UserOut:
        """Override default behavior to hide password on output."""
        query = self._query_one_by_id(id_value)
        query_result = await self._client.execute_and_return(query)

        return create_user_out(query_result[0])


class UserModel(AsyncModel[UserOut]):
    """Database queries for User objects."""

    create: UserCreator
    read: UserReader
    update: UserUpdater
    delete: UserDeleter

    def __init__(self, client: AsyncClient) -> None:
        """Replace built-in Creator & Reader with extended versions."""
        super().__init__(client, "app_user", UserOut)
        self.create = UserCreator(client, self.table, UserOut)
        self.read = UserReader(client, self.table, UserOut)
        self.update = UserUpdater(client, self.table, UserOut)
        self.delete = UserDeleter(client, self.table, UserOut)
