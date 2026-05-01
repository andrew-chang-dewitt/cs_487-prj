"""Tests for the /token router endpoints."""

from unittest import IsolatedAsyncioTestCase as TestCase, main
from uuid import uuid4

from src.database import NoResultFound
from src.shared.testing_fixtures import setup

from src.user.types import UserOut


TOKEN_PATH = "/token"


class TestPostToken(TestCase):
    """Tests for the POST /token endpoint."""

    async def test_valid_credentials_returns_200_with_token(self) -> None:
        """POST /token with valid credentials returns 200 and a Token body.

        The response body should contain an `access_token` string and
        `token_type` of `bearer`.
        """
        user_id = uuid4()
        expected_user = UserOut(
            id=user_id,
            handle="testuser",
            full_name="Test User",
            preferred_name="Test",
        )

        async with setup(db_value=expected_user) as (client, _, _):
            response = await client.post(
                TOKEN_PATH,
                data={"username": "testuser", "password": "password123"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("access_token", body)
        self.assertIsInstance(body["access_token"], str)
        self.assertEqual(body["token_type"], "bearer")

    async def test_invalid_credentials_returns_401(self) -> None:
        """POST /token with invalid credentials returns 401 Unauthorized."""
        async with setup() as (client, _, set_db_res):
            set_db_res(NoResultFound(), True)
            response = await client.post(
                TOKEN_PATH,
                data={"username": "testuser", "password": "wrongpassword"},
            )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    main()
