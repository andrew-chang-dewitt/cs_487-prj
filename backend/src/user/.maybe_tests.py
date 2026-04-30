"""Tests for the /user router endpoints."""

from typing import Any
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import create_app
from src.context import Context
from src.database import DuplicateError, DbClientProtocol
from src.shared.models.base import BaseDb


from .model import UserOut


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


def setup(
    *, db_value: Any | None = None, db_raises: bool = False
) -> tuple[TestClient, MockDbClient]:
    """Create test app & expose methods for controlling mock db."""
    db = MockDbClient()
    if db_value is not None:
        if db_raises:
            db.set_raises_value(db_value)
        else:
            db.set_return_value(db_value)
    else:
        db._returns = None
        db._raises = None
    # print(f"[setup] mock db client created {db, db.__class__}")
    ctx = Context("", db)
    # print(f"[setup] test context {ctx, ctx.root_path, ctx.db_client}")
    app = create_app(ctx)

    return TestClient(app), db


USER_PATH = "/user"


class TestPostUser(unittest.TestCase):
    """Tests for the POST /user endpoint."""

    def test_post_user(self) -> None:
        """POST /user behaves as expected."""
        mock_user = UserOut(
            id=uuid4(),
            handle="testuser",
            full_name="Test User",
            preferred_name="Test",
        )
        client, db = setup()

        # first test creating a new user
        with self.subTest("valid data returns 201 and a UserOut body."):
            # mock db responds w/ new user if query is executed
            db.set_return_value(mock_user)
            response = client.post(
                USER_PATH,
                json={
                    "handle": "testuser",
                    "full_name": "Test User",
                    "preferred_name": "Test",
                    "password": "password123",
                },
            )

            body = response.json()
            # print(f"response body: {body}")
            self.assertEqual(response.status_code, 201)
            self.assertEqual(UserOut(**body), mock_user)
            self.assertNotIn("password", body)

        with self.subTest("missing fields returns 422."):
            response = client.post(
                USER_PATH,
                # Omits full_name, preferred_name, and password.
                json={"handle": "testuser"},
            )

            self.assertEqual(response.status_code, 422)
            detail = response.json()["detail"]
            missing_fields = {err["loc"][-1] for err in detail}
            self.assertIn("full_name", missing_fields)
            self.assertIn("preferred_name", missing_fields)
            self.assertIn("password", missing_fields)

        with self.subTest("invalid field types returns 422."):
            response = client.post(
                USER_PATH,
                json={
                    # A list cannot be coerced to str; validation must fail.
                    "handle": ["invalid", "type"],
                    "full_name": "Test User",
                    "preferred_name": "Test",
                    "password": "password123",
                },
            )

            self.assertEqual(response.status_code, 422)
            detail = response.json()["detail"]
            invalid_fields = {err["loc"][-1] for err in detail}
            self.assertIn("handle", invalid_fields)

        with self.subTest("req with a handle that already exists returns 409."):
            # mock db raises DuplicateError if query is executed
            db.set_raises_value(DuplicateError("testuser already exists"))
            response = client.post(
                USER_PATH,
                json={
                    "handle": "testuser",
                    "full_name": "Test User",
                    "preferred_name": "Test",
                    "password": "password123",
                },
            )

            self.assertEqual(response.status_code, 409)


# class TestGetUser(unittest.TestCase):
#     """Tests for the GET /user endpoint."""
#
#     def setUp(self) -> None:
#         """Set up the test client with the application."""
#         self.app = create_app()
#         self.client = TestClient(self.app)
#         self.mock_user = UserOut(
#             id=uuid4(),
#             handle="testuser",
#             full_name="Test User",
#             preferred_name="Test",
#         )
#
#     def test_valid_id_returns_200_with_user_out(self) -> None:
#         """GET /user with a valid UUID returns 200 and a UserOut body."""
#         with mock_db(
#             self.mock_user.model_dump(),
#         ):
#             response = self.client.get(
#                 USER_PATH, params={"user_id": str(self.mock_user.id)}
#             )
#
#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertEqual(UserOut(**data), self.mock_user)
#
#     def test_invalid_uuid_returns_422(self) -> None:
#         """GET /user with an invalid UUID query parameter returns 422."""
#         response = self.client.get(USER_PATH, params={"user_id": "not-a-uuid"})
#
#         self.assertEqual(response.status_code, 422)
#         detail = response.json()["detail"]
#         invalid_fields = {err["loc"][-1] for err in detail}
#         self.assertIn("user_id", invalid_fields)
#
#     def test_missing_id_returns_404(self) -> None:
#         """GET /user with a UUID not in db returns 404."""
#         with mock_db(
#             self.mock_user.model_dump(),
#         ):
#             response = self.client.get(
#                 USER_PATH, params={"user_id": str(self.mock_user.id)}
#             )
#
#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertEqual(UserOut(**data), self.mock_user)
#
#
# class TestPutUser(unittest.TestCase):
#     """Tests for the PUT /user endpoint."""
#
#     def setUp(self) -> None:
#         """Set up the test client with the application."""
#         self.app = create_app()
#         self.client = TestClient(self.app)
#         self.mock_user = UserOut(
#             id=uuid4(),
#             handle="updateduser",
#             full_name="Updated User",
#             preferred_name="Updated",
#         )
#
#     def test_valid_handle_update_returns_200_with_updated_user_out(self) -> None:
#         """PUT /user with a valid handle change returns 200 and updated UserOut body."""
#         with mock_db(
#             self.mock_user.model_dump(),
#         ):
#             response = self.client.put(
#                 USER_PATH,
#                 params={"user_id": str(self.mock_user.id)},
#                 json={"handle": "updateduser"},
#             )
#
#         data = response.json()
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data["id"], str(self.mock_user.id))
#         self.assertEqual(data["handle"], "updateduser")
#
#     def test_invalid_uuid_returns_422(self) -> None:
#         """PUT /user with an invalid UUID query parameter returns 422."""
#         response = self.client.put(
#             USER_PATH,
#             params={"user_id": "not-a-uuid"},
#             json={"handle": "updateduser"},
#         )
#
#         self.assertEqual(response.status_code, 422)
#         detail = response.json()["detail"]
#         invalid_fields = {err["loc"][-1] for err in detail}
#         self.assertIn("user_id", invalid_fields)
#
#
# class TestDeleteUser(unittest.TestCase):
#     """Tests for the DELETE /user endpoint."""
#
#     def setUp(self) -> None:
#         """Set up the test client with the application."""
#         self.app = create_app()
#         self.client = TestClient(self.app)
#         self.mock_user = UserOut(
#             id=uuid4(),
#             handle="testuser",
#             full_name="Test User",
#             preferred_name="Test",
#         )
#
#     def test_valid_id_returns_200_with_deleted_user_out(self) -> None:
#         """DELETE /user with a valid UUID returns 200 and the deleted UserOut body."""
#         with mock_db(
#             self.mock_user.model_dump(),
#         ):
#             response = self.client.delete(
#                 USER_PATH, params={"user_id": str(self.mock_user.id)}
#             )
#
#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertEqual(data["id"], str(self.mock_user.id))
#         self.assertEqual(data["handle"], "testuser")
#
#     def test_invalid_uuid_returns_422(self) -> None:
#         """DELETE /user with an invalid UUID query parameter returns 422."""
#         response = self.client.delete(USER_PATH, params={"user_id": "not-a-uuid"})
#
#         self.assertEqual(response.status_code, 422)
#         detail = response.json()["detail"]
#         invalid_fields = {err["loc"][-1] for err in detail}
#         self.assertIn("user_id", invalid_fields)
#
#
# class TestPutPassword(unittest.TestCase):
#     """Tests for the PUT /user/password endpoint."""
#
#     def setUp(self) -> None:
#         """Set up the test client with the application."""
#         self.app = create_app()
#         self.client = TestClient(self.app)
#         self.user_id = uuid4()
#         self.mock_user = UserOut(
#             id=self.user_id,
#             handle="testuser",
#             full_name="Test User",
#             preferred_name="Test",
#         )
#
#     def test_valid_request_returns_200_with_user_out(self) -> None:
#         """PUT /user/password with valid data returns 200 and a UserOut body."""
#         with mock_db(
#             self.mock_user.model_dump(),
#         ):
#             response = self.client.put(
#                 "/user/password",
#                 params={"user_id": str(self.user_id)},
#                 json={"new_password": "newpass123"},
#             )
#
#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertEqual(data["id"], str(self.user_id))
#         self.assertEqual(data["handle"], "testuser")
#
#     def test_missing_new_password_field_returns_422(self) -> None:
#         """PUT /user/password with a missing `new_password` field returns 422."""
#         response = self.client.put(
#             "/user/password",
#             params={"user_id": str(self.user_id)},
#             json={},
#         )
#
#         self.assertEqual(response.status_code, 422)
#         detail = response.json()["detail"]
#         missing_fields = {err["loc"][-1] for err in detail}
#         self.assertIn("new_password", missing_fields)
#
#     def test_invalid_uuid_returns_422(self) -> None:
#         """PUT /user/password with an invalid UUID query parameter returns 422."""
#         response = self.client.put(
#             "/user/password",
#             params={"user_id": "not-a-uuid"},
#             json={"new_password": "newpass123"},
#         )
#
#         self.assertEqual(response.status_code, 422)
#         detail = response.json()["detail"]
#         invalid_fields = {err["loc"][-1] for err in detail}
#         self.assertIn("user_id", invalid_fields)


if __name__ == "__main__":
    unittest.main()
