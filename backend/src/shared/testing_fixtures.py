"""Fixtures to aid in unit testing."""

from copy import deepcopy

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Annotated
from uuid import UUID

from fastapi import Depends
from httpx import ASGITransport, AsyncClient as TestClient

from src.app import app
from src.auth import (
    CredentialsException,
    get_auth,
    oauth2_scheme,
)
from src.config import Config, get_config
from src.database import get_db_client, DbClientProtocol
from src.user.model import get_user_model, UserModel

from .models.base import BaseDb


BASE_URL: str = "http://testserver"
FAKE_KEY = "fake_key"


class MockDbClient(DbClientProtocol[Any, Any, list[dict]]):
    """Inherit from DbClient, but overrides functions that talk to db server."""

    _returns: list[Any] | None = None
    _raises: Any | None = None
    _execute_and_return_calls: list[tuple[Any, Any | None]] = []

    def set_return_value(self, value: Any) -> None:
        """Set return value for following calls to database client."""
        match value:
            case list():
                self._returns = value
            case BaseDb():
                self._returns = [value.model_dump()]
            case _:
                self._returns = [value]

        self._raises = None

    def set_raises_value(self, value: Any) -> None:
        """Set exception to be raised during following calls to database client."""
        self._raises = value
        self._returns = None

    async def execute_and_return(
        self,
        query: Any,
        params: Any | None = None,
    ) -> list[dict]:
        """Override to return _returns or raise _raises."""
        # print(f"[MockDbClient.execute_and_return] called with ({query, params})")
        self._execute_and_return_calls.append((query, params))

        if self._raises is not None:
            # print(
            #     f"[MockDbClient.execute_and_return] _raises set, raising {self._raises}"
            # )
            raise self._raises
        if self._returns is not None:
            # print(
            #     f"[MockDbClient.execute_and_return] _returns set, raising {self._returns}"
            # )
            return self._returns

        raise ValueError("Either return value or raises must be set in Mock!")

    async def connect(self):
        """Override to a noop."""
        # print("[user.tests.MockDbClient.connect] called")
        pass

    async def disconnect(self):
        """Override to a noop."""
        # print("[user.tests.MockDbClient.disconnect] called")
        pass


def build_mock_db(
    *, db_value: Any | None, db_raises: bool
) -> tuple[DbClientProtocol, Callable[[Any, bool], None]]:
    """Set up mock db client using given query results, if provided."""
    # mock db client
    db = MockDbClient()

    if db_value is not None:
        if db_raises:
            db.set_raises_value(db_value)
        else:
            db.set_return_value(db_value)

    def set_result(val: Any, raises: bool = False) -> None:
        if raises:
            db.set_raises_value(val)
        else:
            db.set_return_value(val)

    return db, set_result


@asynccontextmanager
async def setup(
    *,
    db_value: Any | None = None,
    db_raises: bool = False,
    authd_user: UUID | CredentialsException | None = None,
) -> AsyncGenerator[tuple[TestClient, DbClientProtocol, Callable[[Any, bool], None]]]:
    """Create test app & expose methods for controlling mock db."""
    # save copy of original deps
    original_deps = deepcopy(app.dependency_overrides)

    def get_mock_auth(
        _: Annotated[Config, Depends(get_config)],
        __: Annotated[str, Depends(oauth2_scheme)],
        ___: Annotated[UserModel, Depends(get_user_model)],
    ) -> UUID:
        match authd_user:
            case UUID():
                return authd_user
            case CredentialsException():
                raise authd_user
            case _:
                raise Exception("This should never happen")

    if authd_user is not None:
        app.dependency_overrides[get_auth] = get_mock_auth

    db, set_result = build_mock_db(db_value=db_value, db_raises=db_raises)

    def get_mock_db(_: Annotated[Config, Depends(get_config)]) -> DbClientProtocol:
        return db

    app.dependency_overrides[get_db_client] = get_mock_db

    async with TestClient(transport=ASGITransport(app), base_url=BASE_URL) as client:
        yield client, db, set_result

    # restore original dependencies to ensure tests stay isolated
    app.dependency_overrides = original_deps


def get_fake_token_header(user_id: UUID) -> dict[str, str]:
    """Get an authentication token header."""
    tok_str = f"totallyrealtokenfor{user_id}.{FAKE_KEY}"
    tok_byt = tok_str.encode()

    return {"Authorization": f"Bearer {tok_byt}.{tok_byt}.{tok_byt}.{tok_byt}"}
