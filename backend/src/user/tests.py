"""Tests for the /user router endpoints."""

from src.auth import CredentialsException

from unittest import main, IsolatedAsyncioTestCase as TestCase
from uuid import uuid4

from src.database import DuplicateError
from src.shared.testing_fixtures import setup, get_fake_token_header

from .model import UserOut


USER_PATH = "/user"


class TestPostUser(TestCase):
    """Tests for the POST /user endpoint."""

    async def test_valid_data_returns_201_with_user_out(self) -> None:
        """POST /user with valid data returns 201 and a UserOut body.

        The response body should contain the submitted field values plus a
        newly generated `id` field.
        """
        expected = UserOut(
            id=uuid4(),
            handle="testuser",
            full_name="Test User",
            preferred_name="Test",
        )
        async with setup(db_value=expected) as (client, _, _):
            response = await client.post(
                USER_PATH,
                json={
                    "handle": "testuser",
                    "full_name": "Test User",
                    "preferred_name": "Test",
                    "password": "password123",
                },
            )

        body = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(UserOut(**body), expected)
        self.assertNotIn("password", body)

    async def test_missing_fields_returns_422_with_field_details(self) -> None:
        """POST /user with missing required fields returns 422.

        The response body should describe which fields are missing.
        """
        async with setup() as (client, _, _):
            response = await client.post(
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

    async def test_invalid_field_type_returns_422_with_field_details(self) -> None:
        """POST /user with a field of an invalid type returns 422.

        The response body should identify the invalid field.
        """
        async with setup() as (client, _, _):
            response = await client.post(
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

    async def test_duplicate_handle_returns_409(self) -> None:
        """POST /user with a handle that already exists returns 409."""
        async with setup() as (client, _, set_db_res):
            # mock db raises DuplicateError if query is executed
            set_db_res(DuplicateError("testuser already exists"), True)
            response = await client.post(
                USER_PATH,
                json={
                    "handle": "testuser",
                    "full_name": "Test User",
                    "preferred_name": "Test",
                    "password": "password123",
                },
            )

        self.assertEqual(response.status_code, 409)


class TestGetUser(TestCase):
    """Tests for the GET /user endpoint."""

    def setUp(self) -> None:
        """Set up the test client with the application."""
        self.expected = UserOut(
            id=uuid4(),
            handle="testuser",
            full_name="Test User",
            preferred_name="Test",
        )
        self.headers = get_fake_token_header(self.expected.id)

    async def test_valid_id_returns_200_with_user_out(self) -> None:
        """GET /user with a valid UUID returns 200 and a UserOut body."""
        async with setup(db_value=self.expected, authd_user=self.expected.id) as (
            client,
            _,
            __,
        ):
            response = await client.get(
                USER_PATH,
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(UserOut(**data), self.expected)

    async def test_get_without_auth_returns_401(self) -> None:
        """GET /user with without auth returns 401."""
        async with setup(db_value=self.expected, authd_user=CredentialsException()) as (
            client,
            _,
            _,
        ):
            response = await client.get(
                USER_PATH,
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 401)

    async def test_missing_id_returns_404(self) -> None:
        """GET /user with a UUID not in db returns 404."""
        async with setup(db_value=[], authd_user=self.expected.id) as (client, _, _):
            response = await client.get(
                USER_PATH,
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 404)


class TestPutUser(TestCase):
    """Tests for the PUT /user endpoint."""

    def setUp(self) -> None:
        """Set up the test client with the application."""
        self.expected = UserOut(
            id=uuid4(),
            handle="updateduser",
            full_name="Updated User",
            preferred_name="Updated",
        )
        self.headers = get_fake_token_header(self.expected.id)

    async def test_valid_handle_update_returns_200_with_updated_user_out(self) -> None:
        """PUT /user with a valid handle change returns 200 and updated UserOut body."""
        async with setup(db_value=self.expected, authd_user=self.expected.id) as (
            client,
            _,
            _,
        ):
            response = await client.put(
                USER_PATH,
                json={"handle": "updateduser"},
                headers=self.headers,
            )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["id"], str(self.expected.id))
        self.assertEqual(data["handle"], "updateduser")

    async def test_update_without_auth_returns_401(self) -> None:
        """PUT /user with without auth returns 401."""
        async with setup(db_value=self.expected, authd_user=CredentialsException()) as (
            client,
            _,
            _,
        ):
            response = await client.put(
                USER_PATH,
                json={"handle": "updateduser"},
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 401)


class TestDeleteUser(TestCase):
    """Tests for the DELETE /user endpoint."""

    def setUp(self) -> None:
        """Set up the test client with the application."""
        self.expected = UserOut(
            id=uuid4(),
            handle="testuser",
            full_name="Test User",
            preferred_name="Test",
        )
        self.headers = get_fake_token_header(self.expected.id)

    async def test_valid_id_returns_200_with_deleted_user_out(self) -> None:
        """DELETE /user with a valid UUID returns 200 and the deleted UserOut body."""
        async with setup(db_value=self.expected, authd_user=self.expected.id) as (
            client,
            _,
            _,
        ):
            response = await client.delete(
                USER_PATH,
                headers=self.headers,
            )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["id"], str(self.expected.id))
        self.assertEqual(body["handle"], "testuser")

    async def test_delete_without_auth_returns_401(self) -> None:
        """DELETE /user with without auth returns 401."""
        async with setup(db_value=self.expected, authd_user=CredentialsException()) as (
            client,
            _,
            _,
        ):
            response = await client.delete(USER_PATH, headers=self.headers)

        self.assertEqual(response.status_code, 401)


class TestPutPassword(TestCase):
    """Tests for the PUT /user/password endpoint."""

    def setUp(self) -> None:
        """Set up the test client with the application."""
        self.expected = UserOut(
            id=uuid4(),
            handle="testuser",
            full_name="Test User",
            preferred_name="Test",
        )
        self.headers = get_fake_token_header(self.expected.id)

    async def test_valid_request_returns_200_with_user_out(self) -> None:
        """PUT /user/password with valid data returns 200 and a UserOut body."""
        async with setup(db_value=self.expected, authd_user=self.expected.id) as (
            client,
            _,
            _,
        ):
            response = await client.put(
                "/user/password",
                json={"new_password": "newpass123"},
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], str(self.expected.id))
        self.assertEqual(data["handle"], "testuser")

    async def test_missing_new_password_field_returns_422(self) -> None:
        """PUT /user/password with a missing `new_password` field returns 422."""
        async with setup(db_value=self.expected, authd_user=self.expected.id) as (
            client,
            _,
            _,
        ):
            response = await client.put(
                "/user/password",
                json={},
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        missing_fields = {err["loc"][-1] for err in detail}
        self.assertIn("new_password", missing_fields)

    async def test_update_without_auth_returns_401(self) -> None:
        """PUT /user with without auth returns 401."""
        async with setup(db_value=self.expected, authd_user=CredentialsException()) as (
            client,
            _,
            _,
        ):
            response = await client.put(
                "/user/password",
                json={"new_password": "newpass123"},
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    main()
