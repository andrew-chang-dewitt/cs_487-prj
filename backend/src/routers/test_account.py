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


class TestGetAccount(unittest.TestCase):
    """Tests for GET /account."""

    def setUp(self) -> None:
        """Set up test client."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_valid_user_id_returns_200_with_account_list(self) -> None:
        """GET with valid user_id returns 200 and a list of AccountOut."""
        expected = [
            AccountOut(
                id=_TEST_ACCOUNT_ID,
                user_id=_TEST_USER_ID,
                name="Test Account",
                closed=False,
            )
        ]

        with patch(
            "src.models.account.AccountModel.Read.many_by_user",
            new_callable=AsyncMock,
            return_value=expected,
        ):
            response = self.client.get(
                "/account",
                params={"user_id": str(_TEST_USER_ID)},
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
        expected = AccountOut(
            id=_TEST_ACCOUNT_ID,
            user_id=_TEST_USER_ID,
            name="Updated Account",
            closed=False,
        )

        with patch(
            "src.models.dummy_model.DummyModel.Update.changes",
            new_callable=AsyncMock,
            return_value=expected,
        ):
            response = self.client.put(
                f"/account/{_TEST_ACCOUNT_ID}",
                params={"user_id": str(_TEST_USER_ID)},
                json={"name": "Updated Account"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated Account")
        self.assertEqual(data["id"], str(_TEST_ACCOUNT_ID))

    def test_invalid_account_id_returns_422(self) -> None:
        """PUT with an invalid account_id path param returns 422 with error detail."""
        response = self.client.put(
            "/account/not-a-valid-uuid",
            params={"user_id": str(_TEST_USER_ID)},
            json={"name": "Updated Account"},
        )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)

    def test_missing_user_id_returns_422(self) -> None:
        """PUT without user_id query param returns 422 with error detail."""
        response = self.client.put(
            f"/account/{_TEST_ACCOUNT_ID}",
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
        expected = AccountOut(
            id=_TEST_ACCOUNT_ID,
            user_id=_TEST_USER_ID,
            name="Test Account",
            closed=True,
        )

        with patch(
            "src.models.dummy_model.DummyModel.Update.changes",
            new_callable=AsyncMock,
            return_value=expected,
        ):
            response = self.client.put(
                f"/account/{_TEST_ACCOUNT_ID}/closed",
                params={"user_id": str(_TEST_USER_ID)},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["closed"], True)
        self.assertEqual(data["id"], str(_TEST_ACCOUNT_ID))

    def test_invalid_account_id_returns_422(self) -> None:
        """Invalid account_id path param: returns 422 with error detail."""
        response = self.client.put(
            "/account/not-a-valid-uuid/closed",
            params={"user_id": str(_TEST_USER_ID)},
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
        expected = [
            AccountOut(
                id=_TEST_ACCOUNT_ID,
                user_id=_TEST_USER_ID,
                name="Closed Account",
                closed=True,
            )
        ]

        with patch(
            "src.models.account.AccountModel.Read.many_by_user",
            new_callable=AsyncMock,
            return_value=expected,
        ):
            response = self.client.get(
                "/account/closed",
                params={"user_id": str(_TEST_USER_ID)},
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
