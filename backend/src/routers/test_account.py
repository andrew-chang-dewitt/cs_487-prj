"""Tests for /account routes."""

import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import create_app
from src.models import AccountOut

_TEST_USER_ID = uuid4()
_TEST_ACCOUNT_ID = uuid4()


class TestPostAccount(unittest.TestCase):
    """Tests for POST /account."""

    def setUp(self) -> None:
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_valid_data_returns_201_with_account_out(self) -> None:
        """POST with valid data returns 201 and an AccountOut with matching fields."""
        expected = AccountOut(
            id=_TEST_ACCOUNT_ID,
            user_id=_TEST_USER_ID,
            name="Test Account",
            closed=False,
        )

        with patch(
            "src.models.dummy_model.DummyModel.Create.new",
            new_callable=AsyncMock,
            return_value=expected,
        ):
            response = self.client.post(
                "/account",
                params={"user_id": str(_TEST_USER_ID)},
                json={"name": "Test Account"},
            )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Test Account")
        self.assertEqual(data["closed"], False)
        self.assertEqual(data["user_id"], str(_TEST_USER_ID))
        self.assertIn("id", data)

    def test_missing_required_field_returns_422(self) -> None:
        """POST without required name field returns 422 with error detail."""
        response = self.client.post(
            "/account",
            params={"user_id": str(_TEST_USER_ID)},
            json={},
        )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)

    def test_invalid_field_type_returns_422(self) -> None:
        """POST with an invalid field type returns 422 with error detail."""
        response = self.client.post(
            "/account",
            params={"user_id": "not-a-valid-uuid"},
            json={"name": "Test Account"},
        )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)


if __name__ == "__main__":
    unittest.main()
