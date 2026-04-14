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
        newly generated `id` field.
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


class TestGetUser(unittest.TestCase):
    """Tests for the GET /user endpoint."""

    def setUp(self) -> None:
        """Set up the test client with the application."""
        self.app = create_app()
        self.client = TestClient(self.app)
        self.user_id = uuid4()
        self.mock_user = UserOut(
            id=self.user_id,
            handle="testuser",
            full_name="Test User",
            preferred_name="Test",
        )

    def test_valid_id_returns_200_with_user_out(self) -> None:
        """GET /user with a valid UUID returns 200 and a UserOut body."""
        with patch(
            "src.models.dummy_model.DummyModel.Read.one_by_id",
            new_callable=AsyncMock,
            return_value=self.mock_user,
        ):
            response = self.client.get("/user", params={"user_id": str(self.user_id)})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], str(self.user_id))
        self.assertEqual(data["handle"], "testuser")
        self.assertEqual(data["full_name"], "Test User")
        self.assertEqual(data["preferred_name"], "Test")

    def test_invalid_uuid_returns_422(self) -> None:
        """GET /user with an invalid UUID query parameter returns 422."""
        response = self.client.get("/user", params={"user_id": "not-a-uuid"})

        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        invalid_fields = {err["loc"][-1] for err in detail}
        self.assertIn("user_id", invalid_fields)


class TestPutUser(unittest.TestCase):
    """Tests for the PUT /user endpoint."""

    def setUp(self) -> None:
        """Set up the test client with the application."""
        self.app = create_app()
        self.client = TestClient(self.app)
        self.user_id = uuid4()
        self.mock_user = UserOut(
            id=self.user_id,
            handle="updateduser",
            full_name="Updated User",
            preferred_name="Updated",
        )

    def test_valid_handle_update_returns_200_with_updated_user_out(self) -> None:
        """PUT /user with a valid handle change returns 200 and updated UserOut body."""
        with patch(
            "src.models.dummy_model.DummyModel.Update.changes",
            new_callable=AsyncMock,
            return_value=self.mock_user,
        ):
            response = self.client.put(
                "/user",
                params={"user_id": str(self.user_id)},
                json={"handle": "updateduser"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], str(self.user_id))
        self.assertEqual(data["handle"], "updateduser")

    def test_invalid_uuid_returns_422(self) -> None:
        """PUT /user with an invalid UUID query parameter returns 422."""
        response = self.client.put(
            "/user",
            params={"user_id": "not-a-uuid"},
            json={"handle": "updateduser"},
        )

        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        invalid_fields = {err["loc"][-1] for err in detail}
        self.assertIn("user_id", invalid_fields)


class TestDeleteUser(unittest.TestCase):
    """Tests for the DELETE /user endpoint."""

    def setUp(self) -> None:
        """Set up the test client with the application."""
        self.app = create_app()
        self.client = TestClient(self.app)
        self.user_id = uuid4()
        self.mock_user = UserOut(
            id=self.user_id,
            handle="testuser",
            full_name="Test User",
            preferred_name="Test",
        )

    def test_valid_id_returns_200_with_deleted_user_out(self) -> None:
        """DELETE /user with a valid UUID returns 200 and the deleted UserOut body."""
        with patch(
            "src.models.dummy_model.DummyModel.Delete.one_by_id",
            new_callable=AsyncMock,
            return_value=self.mock_user,
        ):
            response = self.client.delete(
                "/user", params={"user_id": str(self.user_id)}
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], str(self.user_id))
        self.assertEqual(data["handle"], "testuser")

    def test_invalid_uuid_returns_422(self) -> None:
        """DELETE /user with an invalid UUID query parameter returns 422."""
        response = self.client.delete("/user", params={"user_id": "not-a-uuid"})

        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        invalid_fields = {err["loc"][-1] for err in detail}
        self.assertIn("user_id", invalid_fields)


class TestPutPassword(unittest.TestCase):
    """Tests for the PUT /user/password endpoint."""

    def setUp(self) -> None:
        """Set up the test client with the application."""
        self.app = create_app()
        self.client = TestClient(self.app)
        self.user_id = uuid4()
        self.mock_user = UserOut(
            id=self.user_id,
            handle="testuser",
            full_name="Test User",
            preferred_name="Test",
        )

    def test_valid_request_returns_200_with_user_out(self) -> None:
        """PUT /user/password with valid data returns 200 and a UserOut body."""
        with patch(
            "src.models.user.UserModel.Update.password",
            new_callable=AsyncMock,
            return_value=self.mock_user,
        ):
            response = self.client.put(
                "/user/password",
                params={"user_id": str(self.user_id)},
                json={"new_password": "newpass123"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], str(self.user_id))
        self.assertEqual(data["handle"], "testuser")

    def test_missing_new_password_field_returns_422(self) -> None:
        """PUT /user/password with a missing `new_password` field returns 422."""
        response = self.client.put(
            "/user/password",
            params={"user_id": str(self.user_id)},
            json={},
        )

        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        missing_fields = {err["loc"][-1] for err in detail}
        self.assertIn("new_password", missing_fields)

    def test_invalid_uuid_returns_422(self) -> None:
        """PUT /user/password with an invalid UUID query parameter returns 422."""
        response = self.client.put(
            "/user/password",
            params={"user_id": "not-a-uuid"},
            json={"new_password": "newpass123"},
        )

        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        invalid_fields = {err["loc"][-1] for err in detail}
        self.assertIn("user_id", invalid_fields)


if __name__ == "__main__":
    unittest.main()
