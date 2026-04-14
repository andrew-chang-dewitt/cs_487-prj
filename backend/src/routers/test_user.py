"""Tests for the /user router endpoints."""

import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import create_app
from src.models.user import UserOut


class TestPostUser(unittest.TestCase):
    """Tests for the POST /user endpoint."""

    def setUp(self) -> None:
        """Set up the test client with the application."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_valid_data_returns_201_with_user_out(self) -> None:
        """POST /user with valid data returns 201 and a UserOut body.

        The response body should contain the submitted field values plus a
        newly generated ``id`` field.
        """
        user_id = uuid4()
        mock_user = UserOut(
            id=user_id,
            handle="testuser",
            full_name="Test User",
            preferred_name="Test",
        )

        with patch(
            "src.models.dummy_model.DummyModel.Create.new",
            new_callable=AsyncMock,
            return_value=mock_user,
        ):
            response = self.client.post(
                "/user",
                json={
                    "handle": "testuser",
                    "full_name": "Test User",
                    "preferred_name": "Test",
                    "password": "password123",
                },
            )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["handle"], "testuser")
        self.assertEqual(data["full_name"], "Test User")
        self.assertEqual(data["preferred_name"], "Test")
        self.assertEqual(data["id"], str(user_id))

    def test_missing_fields_returns_422_with_field_details(self) -> None:
        """POST /user with missing required fields returns 422.

        The response body should describe which fields are missing.
        """
        response = self.client.post(
            "/user",
            # Omits full_name, preferred_name, and password.
            json={"handle": "testuser"},
        )

        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        missing_fields = {err["loc"][-1] for err in detail}
        self.assertIn("full_name", missing_fields)
        self.assertIn("preferred_name", missing_fields)
        self.assertIn("password", missing_fields)

    def test_invalid_field_type_returns_422_with_field_details(self) -> None:
        """POST /user with a field of an invalid type returns 422.

        The response body should identify the invalid field.
        """
        response = self.client.post(
            "/user",
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


if __name__ == "__main__":
    unittest.main()
