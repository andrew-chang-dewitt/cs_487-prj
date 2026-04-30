"""User* data objects."""

from fastapi import Depends

from functools import lru_cache
from typing import Any, Annotated
from uuid import UUID

from db_wrapper.model import (
    sql,
    AsyncModel,
    AsyncCreate,
    AsyncRead,
    AsyncUpdate,
    AsyncDelete,
    RealDictRow,
)

from src.database import get_db_client, NoResultFound, DbClient

from .types import (
    UserChanges,
    UserIn,
    UserOut,
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

        query_result: list[RealDictRow] = await self._client.execute_and_return(query)

        try:
            return UserOut(**query_result[0])
        except IndexError as err:
            raise NoResultFound() from err


class UserReader(AsyncRead[UserOut]):
    """Extended read methods for UserModel."""

    async def one_by_id(self, id_value: UUID) -> UserOut:
        """Override default behavior to hide password on output."""
        query = sql.SQL(
            "SELECT id, handle, full_name, preferred_name "
            "FROM {table} "
            "WHERE id = {id_value};"
        ).format(table=self._table, id_value=sql.Literal(str(id_value)))
        query_result = await self._client.execute_and_return(query)

        try:
            return UserOut(**query_result[0])
        except IndexError as err:
            raise NoResultFound() from err

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
            raise NoResultFound() from err


class UserUpdater(AsyncUpdate[UserOut]):
    """Extended Updater for UserModel."""

    async def one_by_id(self, id_value: UUID, changes: dict[str, Any]) -> UserOut:
        """Un-implemented to force use of update.changes method."""
        raise NotImplementedError()

    async def changes(self, user_id: UUID, changes: UserChanges) -> UserOut:
        """Update only the given fields for the given user."""

        def compose_one_change(change: tuple[str, Any]) -> sql.Composed:
            key = change[0]
            value = change[1]

            return sql.SQL("{key} = {value}").format(
                key=sql.Identifier(key), value=sql.Literal(value)
            )

        def compose_changes(changes: dict[str, Any]) -> sql.Composed:
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
            raise NoResultFound() from err

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
            raise NoResultFound() from err


class UserDeleter(AsyncDelete[UserOut]):
    """Extend default delete behavior."""

    async def one_by_id(self, id_value: str) -> UserOut:
        """Override default behavior to hide password on output."""
        query = self._query_one_by_id(id_value)
        query_result = await self._client.execute_and_return(query)

        try:
            return UserOut(**query_result[0])
        except IndexError as err:
            raise NoResultFound() from err


class UserModel(AsyncModel[UserOut]):
    """Database queries for User objects."""

    create: UserCreator
    read: UserReader
    update: UserUpdater
    delete: UserDeleter

    def __init__(self, client: DbClient) -> None:
        """Replace built-in Creator & Reader with extended versions."""
        super().__init__(client, "app_user", UserOut)
        self.create = UserCreator(client, self.table, UserOut)
        self.read = UserReader(client, self.table, UserOut)
        self.update = UserUpdater(client, self.table, UserOut)
        self.delete = UserDeleter(client, self.table, UserOut)


@lru_cache
def get_user_model(db: Annotated[DbClient, Depends(get_db_client)]) -> UserModel:
    """Provide UserModel instance for dep injection."""
    return UserModel(db)
