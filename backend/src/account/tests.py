"""Tests for /account routes."""

from src.auth import CredentialsException

from unittest import IsolatedAsyncioTestCase as TestCase, main
from uuid import uuid4

from src.shared.testing_fixtures import setup, get_fake_token_header

from .model import AccountOut


ACCOUNT_PATH = "/account"


class TestPostAccount(TestCase):
    """Tests for POST /account."""

    async def test_valid_data_returns_201_with_account_out(self) -> None:
        """POST with valid data returns 201 and matching AccountOut."""
        account_id = uuid4()
        user_id = uuid4()

        expected = AccountOut(
            id=account_id,
            user_id=user_id,
            name="Test Account",
            closed=False,
        )
        headers = get_fake_token_header(expected.id)

        async with setup(db_value=expected, authd_user=user_id) as (client, _, _):
            response = await client.post(
                ACCOUNT_PATH,
                json={"name": "Test Account"},
                headers=headers,
            )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Test Account")
        self.assertEqual(data["closed"], False)
        self.assertEqual(data["user_id"], str(user_id))
        self.assertIn("id", data)

    async def test_missing_required_field_returns_422(self) -> None:
        """POST without required name field returns 422 with error detail."""
        user_id = uuid4()
        headers = get_fake_token_header(user_id)
        async with setup(authd_user=user_id) as (client, _, _):
            response = await client.post(
                ACCOUNT_PATH,
                json={},
                headers=headers,
            )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)

    async def test_invalid_field_type_returns_422(self) -> None:
        """POST with an invalid field type returns 422 with error detail."""
        user_id = uuid4()
        headers = get_fake_token_header(user_id)
        async with setup(authd_user=user_id) as (client, _, _):
            response = await client.post(
                ACCOUNT_PATH,
                json={"name": 12345},
                headers=headers,
            )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)


class TestGetAccount(TestCase):
    """Tests for GET /account."""

    async def test_valid_user_id_returns_200_with_account_list(self) -> None:
        """GET with valid user_id returns 200 and a list of AccountOut."""
        account_id = uuid4()
        user_id = uuid4()
        expected = AccountOut(
            id=account_id,
            user_id=user_id,
            name="Test Account",
            closed=False,
        )
        headers = get_fake_token_header(expected.id)

        async with setup(db_value=expected, authd_user=user_id) as (client, _, _):
            response = await client.get(
                ACCOUNT_PATH,
                headers=headers,
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test Account")
        self.assertEqual(data[0]["closed"], False)


class TestPutAccountId(TestCase):
    """Tests for PUT /{account_id}."""

    async def test_valid_data_returns_200_with_updated_account(self) -> None:
        """PUT with valid data returns 200 and the updated AccountOut."""
        account_id = uuid4()
        user_id = uuid4()
        expected = AccountOut(
            id=account_id,
            user_id=user_id,
            name="Updated Account",
            closed=False,
        )
        headers = get_fake_token_header(expected.id)

        async with setup(db_value=expected, authd_user=user_id) as (client, _, _):
            response = await client.put(
                f"/account/{account_id}",
                json={"name": "Updated Account"},
                headers=headers,
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated Account")
        self.assertEqual(data["id"], str(account_id))

    async def test_invalid_account_id_returns_422(self) -> None:
        """PUT with an invalid account_id path param returns 422 with error detail."""
        user_id = uuid4()
        headers = get_fake_token_header(user_id)
        async with setup(authd_user=user_id) as (client, _, _):
            response = await client.put(
                "/account/not-a-valid-uuid",
                json={"name": "Updated Account"},
                headers=headers,
            )

        body = response.json()
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", body)

    async def test_update_without_auth_returns_401(self) -> None:
        """PUT /account/{account_id} with without auth returns 401."""
        account_id = uuid4()
        async with setup(authd_user=CredentialsException()) as (
            client,
            _,
            _,
        ):
            response = await client.put(
                f"/account/{account_id}",
                json={"name": "Updated Account"},
            )

        self.assertEqual(response.status_code, 401)


class TestPutAccountClosed(TestCase):
    """Tests for PUT /{account_id}/closed."""

    async def test_valid_account_id_returns_200_with_closed_account(self) -> None:
        """Valid account_id: returns 200 with AccountOut where closed=True."""
        account_id = uuid4()
        user_id = uuid4()
        expected = AccountOut(
            id=account_id,
            user_id=user_id,
            name="Test Account",
            closed=True,
        )
        headers = get_fake_token_header(expected.id)

        async with setup(db_value=expected, authd_user=user_id) as (client, _, _):
            response = await client.put(
                f"/account/{account_id}/closed",
                headers=headers,
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["closed"], True)
        self.assertEqual(data["id"], str(account_id))

    async def test_invalid_account_id_returns_422(self) -> None:
        """Invalid account_id path param: returns 422 with error detail."""
        user_id = uuid4()
        headers = get_fake_token_header(user_id)
        async with setup(authd_user=user_id) as (client, _, _):
            response = await client.put(
                "/account/not-a-valid-uuid/closed",
                headers=headers,
            )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)


class TestGetClosedAccounts(TestCase):
    """Tests for GET /closed."""

    async def test_valid_user_id_returns_200_with_closed_account_list(self) -> None:
        """Valid user_id: returns 200 with list of closed AccountOut."""
        account_id = uuid4()
        user_id = uuid4()
        expected = AccountOut(
            id=account_id,
            user_id=user_id,
            name="Closed Account",
            closed=True,
        )
        headers = get_fake_token_header(expected.id)

        async with setup(db_value=expected, authd_user=user_id) as (client, _, _):
            response = await client.get(
                "/account/closed",
                headers=headers,
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["closed"], True)
        self.assertEqual(data[0]["name"], "Closed Account")

    async def test_update_without_auth_returns_401(self) -> None:
        """GET /closed with without auth returns 401."""
        async with setup(authd_user=CredentialsException()) as (
            client,
            _,
            _,
        ):
            response = await client.get(
                "/account/closed",
            )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    main()
