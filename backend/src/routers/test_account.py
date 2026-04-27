"""Tests for /account routes."""

from typing import Any
import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import create_app
from src.models import AccountOut


def mock_db(result: Any | None, is_side_effect: bool = False):
    if is_side_effect:
        return patch(
            "db_wrapper.AsyncClient.execute_and_return",
            side_effect=result,
        )

    return patch(
        "db_wrapper.AsyncClient.execute_and_return",
        return_value=result if isinstance(result, list) else [result],
    )


class TestPostAccount(unittest.TestCase):
    """Tests for POST /account."""

    def setUp(self) -> None:
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_valid_data_returns_201_with_account_out(self) -> None:
        """POST with valid data returns 201 and matching AccountOut."""
        account_id = uuid4()
        user_id = uuid4()

        expected = AccountOut(
            id=account_id,
            user_id=user_id,
            name="Test Account",
            closed=False,
        )

        with mock_db(
            expected.model_dump(),
        ):
            response = self.client.post(
                "/account",
                params={"user_id": str(user_id)},
                json={"name": "Test Account"},
            )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Test Account")
        self.assertEqual(data["closed"], False)
        self.assertEqual(data["user_id"], str(user_id))
        self.assertIn("id", data)

    def test_missing_required_field_returns_422(self) -> None:
        """POST without required name field returns 422 with error detail."""
        user_id = uuid4()
        response = self.client.post(
            "/account",
            params={"user_id": str(user_id)},
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


class TestGetAccount(unittest.TestCase):
    """Tests for GET /account."""

    def setUp(self) -> None:
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_valid_user_id_returns_200_with_account_list(self) -> None:
        """GET with valid user_id returns 200 and a list of AccountOut."""
        account_id = uuid4()
        user_id = uuid4()
        expected = AccountOut(
            id=account_id,
            user_id=user_id,
            name="Test Account",
            closed=False,
        )

        with mock_db(
            expected.model_dump(),
        ):
            response = self.client.get(
                "/account",
                params={"user_id": str(user_id)},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test Account")
        self.assertEqual(data[0]["closed"], False)

    def test_invalid_user_id_returns_422(self) -> None:
        """GET with invalid user_id returns 422 with error detail."""
        response = self.client.get(
            "/account",
            params={"user_id": "not-a-valid-uuid"},
        )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)


class TestPutAccountId(unittest.TestCase):
    """Tests for PUT /{account_id}."""

    def setUp(self) -> None:
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_valid_data_returns_200_with_updated_account(self) -> None:
        """PUT with valid data returns 200 and the updated AccountOut."""
        account_id = uuid4()
        user_id = uuid4()
        expected = AccountOut(
            id=account_id,
            user_id=user_id,
            name="Updated Account",
            closed=False,
        )

        with mock_db(
            expected.model_dump(),
        ):
            response = self.client.put(
                f"/account/{account_id}",
                params={"user_id": str(user_id)},
                json={"name": "Updated Account"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated Account")
        self.assertEqual(data["id"], str(account_id))

    def test_invalid_account_id_returns_422(self) -> None:
        """PUT with an invalid account_id path param returns 422 with error detail."""
        user_id = uuid4()
        response = self.client.put(
            "/account/not-a-valid-uuid",
            params={"user_id": str(user_id)},
            json={"name": "Updated Account"},
        )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)

    def test_missing_user_id_returns_422(self) -> None:
        """PUT without user_id query param returns 422 with error detail."""
        account_id = uuid4()
        response = self.client.put(
            f"/account/{account_id}",
            json={"name": "Updated Account"},
        )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)


class TestPutAccountClosed(unittest.TestCase):
    """Tests for PUT /{account_id}/closed."""

    def setUp(self) -> None:
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_valid_account_id_returns_200_with_closed_account(self) -> None:
        """Valid account_id: returns 200 with AccountOut where closed=True."""
        account_id = uuid4()
        user_id = uuid4()
        expected = AccountOut(
            id=account_id,
            user_id=user_id,
            name="Test Account",
            closed=True,
        )

        with mock_db(
            expected.model_dump(),
        ):
            response = self.client.put(
                f"/account/{account_id}/closed",
                params={"user_id": str(user_id)},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["closed"], True)
        self.assertEqual(data["id"], str(account_id))

    def test_invalid_account_id_returns_422(self) -> None:
        """Invalid account_id path param: returns 422 with error detail."""
        user_id = uuid4()
        response = self.client.put(
            "/account/not-a-valid-uuid/closed",
            params={"user_id": str(user_id)},
        )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)


class TestGetClosedAccounts(unittest.TestCase):
    """Tests for GET /closed."""

    def setUp(self) -> None:
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_valid_user_id_returns_200_with_closed_account_list(self) -> None:
        """Valid user_id: returns 200 with list of closed AccountOut."""
        account_id = uuid4()
        user_id = uuid4()
        expected = AccountOut(
            id=account_id,
            user_id=user_id,
            name="Closed Account",
            closed=True,
        )

        with mock_db(
            expected.model_dump(),
        ):
            response = self.client.get(
                "/account/closed",
                params={"user_id": str(user_id)},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["closed"], True)
        self.assertEqual(data[0]["name"], "Closed Account")

    def test_invalid_user_id_returns_422(self) -> None:
        """GET /closed with invalid user_id returns 422 with error detail."""
        response = self.client.get(
            "/account/closed",
            params={"user_id": "not-a-valid-uuid"},
        )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)


if __name__ == "__main__":
    unittest.main()
