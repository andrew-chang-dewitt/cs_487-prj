"""Account* data objects."""

from typing import Any, Optional
from uuid import UUID

from db_wrapper.client import AsyncClient
from db_wrapper.model import (
    sql,
    AsyncCreate,
    AsyncRead,
    AsyncUpdate,
    AsyncModel,
)
from db_wrapper.model.base import NoResultFound

from .base import Base, BaseDb
from .filters import build_query_equality_filters


class AccountBase(Base):
    """Common fields for user Accounts."""

    name: str
    closed: bool


class AccountIn(AccountBase):
    """Fields needed from user to create an Account."""

    closed: bool = False


class AccountChanges(AccountBase):
    """Fields used when updating an Account, all are optional."""

    closed: Optional[bool] = None
    name: Optional[str] = None


class AccountNew(AccountBase):
    """Information needed to save a new account to the database."""

    user_id: UUID


class AccountOut(AccountNew, BaseDb):
    """Fields returned by Account queries."""


class AccountCreator(AsyncCreate[AccountOut]):
    """Extended create methods."""

    async def new(self, data: AccountNew) -> AccountOut:
        """Create a new Account."""
        query = sql.SQL("""
                INSERT INTO {table}(user_id, name)
                VALUES ({user_id}, {name})
                RETURNING *;
                """).format(
            table=self._table,
            user_id=sql.Literal(str(data.user_id)),
            name=sql.Literal(data.name),
        )

        query_result = await self._client.execute_and_return(query)

        return AccountOut(**query_result[0])


class AccountReader(AsyncRead[AccountOut]):
    """Extended read methods."""

    async def many_by_user(self, user_id: UUID, **kwargs: Any) -> list[AccountOut]:
        """Get list of accounts for user."""
        filter_values = AccountChanges(
            **{  # type: ignore
                # default to filtering by accounts not marked as closed
                "closed": False,
                # and override default if it's present in kwargs
                **kwargs,
            }
        )

        query = sql.SQL("""
            SELECT * FROM {table}
            WHERE user_id = {user_id}
            {filters};
        """).format(
            table=self._table,
            user_id=sql.Literal(str(user_id)),
            filters=build_query_equality_filters(filter_values),
        )
        query_result = await self._client.execute_and_return(query)

        return [AccountOut(**account) for account in query_result]


class AccountUpdater(AsyncUpdate[AccountOut]):
    """Extended update methods."""

    async def one_by_id(self, id_value: UUID, changes: dict[str, Any]) -> AccountOut:
        """Un-implemented to force use of update.changes method."""
        raise NotImplementedError()

    async def changes(
        self, account_id: UUID, user_id: UUID, changes: AccountChanges
    ) -> AccountOut:
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
            WHERE id = {account_id}
            AND user_id = {user_id}
            RETURNING *;
        """).format(
            table=self._table,
            changes=compose_changes(changes.model_dump()),
            account_id=sql.Literal(account_id),
            user_id=sql.Literal(user_id),
        )
        query_result = await self._client.execute_and_return(query)

        try:
            return AccountOut(**query_result[0])
        except IndexError as err:
            raise NoResultFound from err


class AccountModel(AsyncModel[AccountOut]):
    """Account ORM."""

    create: AccountCreator
    read: AccountReader
    update: AccountUpdater

    def __init__(self, client: AsyncClient) -> None:
        """Create Account Model."""
        super().__init__(client, "account", AccountOut)
        self.create = AccountCreator(client, self.table, AccountOut)
        self.read = AccountReader(client, self.table, AccountOut)
        self.update = AccountUpdater(client, self.table, AccountOut)
