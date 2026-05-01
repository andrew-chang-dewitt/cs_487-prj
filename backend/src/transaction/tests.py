"""Tests for /transaction routes."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from unittest import main, IsolatedAsyncioTestCase as TestCase

from src.shared.testing_fixtures import setup, get_fake_token_header

from .types import TransactionOut

BASE_URL = "/transaction"


class TestRoutePostRoot(TestCase):
    """Tests for `POST /transaction`."""

    async def test_valid_request(self) -> None:
        """Testing a valid request's response."""
        user_id = uuid4()
        account_id = uuid4()
        transaction_id = uuid4()

        expected = TransactionOut(
            id=transaction_id,
            amount=Decimal("1.23"),
            description="a description",
            payee="payee",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=account_id,
        )
        headers = get_fake_token_header(expected.id)

        async with setup(
            db_value=expected, authd_user=user_id, authd_accts=[account_id]
        ) as (client, _, _):
            response = await client.post(
                BASE_URL,
                headers=headers,
                json={
                    "amount": 1.23,
                    "description": "a description",
                    "payee": "payee",
                    "timestamp": "2019-12-10T08:12-05:00",
                    "account_id": str(account_id),
                },
            )

            with self.subTest(msg="Responds with a status code of 201."):
                self.assertEqual(201, response.status_code)

            with self.subTest(msg="Responds with new Transaction's information."):
                body = response.json()
                self.assertEqual(TransactionOut(**body), expected)

    async def test_cant_create_transactions_if_not_own_account(self) -> None:
        """Return 401 attempting to create transaction for other account."""
        user_id = uuid4()
        other_account = uuid4()
        transaction_id = uuid4()
        new_tran = TransactionOut(
            id=transaction_id,
            amount=Decimal("1.23"),
            description="a description",
            payee="payee",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=other_account,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=new_tran, authd_user=user_id, authd_accts=[]) as (
            client,
            _,
            _,
        ):
            response = await client.post(
                BASE_URL,
                headers=headers,
                json={
                    "amount": 1.23,
                    "description": "a description",
                    "payee": "payee",
                    "timestamp": "2019-12-10T08:12-05:00",
                    "account_id": str(other_account),
                },
            )

            self.assertEqual(401, response.status_code)


class TestRouteGetRoot(TestCase):
    """Tests for `GET /transaction`."""

    async def test_valid_request(self) -> None:
        """Testing a valid request's response."""
        user_id = uuid4()
        account_one_id = uuid4()
        account_two_id = uuid4()
        transactions = [
            TransactionOut(
                id=uuid4(),
                amount=Decimal("1.23"),
                payee="a payee",
                description="a description",
                timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
                account_id=account_one_id,
            ),
            TransactionOut(
                id=uuid4(),
                amount=Decimal("456"),
                payee="a payee",
                description="a description",
                timestamp=datetime.fromisoformat("2019-12-10T09:12-05:00"),
                account_id=account_two_id,
            ),
            TransactionOut(
                id=uuid4(),
                amount=Decimal("789.10"),
                payee="a payee",
                description="a description",
                timestamp=datetime.fromisoformat("2019-12-11T06:12-05:00"),
                account_id=account_one_id,
            ),
        ]
        db_rows = [t.model_dump() for t in transactions]
        headers = get_fake_token_header(user_id)

        async with setup(
            db_value=db_rows,
            authd_user=user_id,
            authd_accts=[account_one_id, account_two_id],
        ) as (client, _, _):
            response = await client.get(BASE_URL, headers=headers)

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(msg="Returns requested transactions."):
            body = response.json()
            self.assertIsInstance(body, list)
            results = [TransactionOut(**t) for t in body]
            self.assertIn(transactions[0], results)
            self.assertIn(transactions[1], results)
            self.assertIn(transactions[2], results)

    async def test_filter_by_account(self) -> None:
        """Requests can filter by account."""
        user_id = uuid4()
        account1 = uuid4()
        transaction = TransactionOut(
            id=uuid4(),
            amount=Decimal("1.23"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=account1,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=transaction, authd_user=user_id) as (client, _, _):
            response = await client.get(
                f"{BASE_URL}?account_id={account1}", headers=headers
            )

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(
            msg="Only returns Transactions belonging to requested Account."
        ):
            for item in response.json():
                self.assertEqual(item["account_id"], str(account1))

    async def test_filter_payee(self) -> None:
        """Requests can filter by payee."""
        user_id = uuid4()
        account_id = uuid4()
        transaction = TransactionOut(
            id=uuid4(),
            amount=Decimal("1.23"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=account_id,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=transaction, authd_user=user_id) as (client, _, _):
            response = await client.get(f"{BASE_URL}?payee=a%20payee", headers=headers)

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(msg="Only returns Transactions with matching payee."):
            for item in response.json():
                self.assertEqual(item["payee"], "a payee")

    async def test_filter_minimum_amount(self) -> None:
        """Requests can filter by minimum amount."""
        user_id = uuid4()
        account_id = uuid4()
        transaction = TransactionOut(
            id=uuid4(),
            amount=Decimal("1.23"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=account_id,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=transaction, authd_user=user_id) as (client, _, _):
            response = await client.get(
                f"{BASE_URL}?minimum_amount=1.00", headers=headers
            )

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(msg="Only returns Transactions >= to given amount."):
            for item in response.json():
                self.assertGreaterEqual(item["amount"], 1)

    async def test_filter_maximum_amount(self) -> None:
        """Requests can filter by maximum amount."""
        user_id = uuid4()
        account_id = uuid4()
        transaction = TransactionOut(
            id=uuid4(),
            amount=Decimal("0.23"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=account_id,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=transaction, authd_user=user_id) as (client, _, _):
            response = await client.get(
                f"{BASE_URL}?maximum_amount=1.00", headers=headers
            )

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(msg="Only returns Transactions <= to given amount."):
            for item in response.json():
                self.assertLessEqual(item["amount"], 1)

    async def test_filter_minimum_and_maximum_amount(self) -> None:
        """Requests can filter by both minimum and maximum amount."""
        user_id = uuid4()
        account_id = uuid4()
        transaction = TransactionOut(
            id=uuid4(),
            amount=Decimal("0.23"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=account_id,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=transaction, authd_user=user_id) as (client, _, _):
            response = await client.get(
                f"{BASE_URL}?minimum_amount=0.00&maximum_amount=1.00",
                headers=headers,
            )

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(msg="Only returns Transactions inclusive between amounts."):
            body = response.json()
            for item in body:
                with self.subTest(msg="Greater than/equal to minimum."):
                    self.assertGreaterEqual(item["amount"], 0)
                with self.subTest(msg="Less than/equal to maximum."):
                    self.assertLessEqual(item["amount"], 1)

    async def test_filter_minimum_timestamp(self) -> None:
        """Requests can filter by minimum timestamp."""
        user_id = uuid4()
        account_id = uuid4()
        after = "2020-01-01T00:00-00:00"
        transaction = TransactionOut(
            id=uuid4(),
            amount=Decimal("1.00"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2020-12-10T08:12-05:00"),
            account_id=account_id,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=transaction, authd_user=user_id) as (client, _, _):
            response = await client.get(f"{BASE_URL}?after={after}", headers=headers)

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(msg="Only returns Transactions >= to given timestamp."):
            for item in response.json():
                self.assertGreaterEqual(
                    datetime.fromisoformat(item["timestamp"]),
                    datetime.fromisoformat(after),
                )

    async def test_filter_maximum_timestamp(self) -> None:
        """Requests can filter by maximum timestamp."""
        user_id = uuid4()
        account_id = uuid4()
        before = "2020-01-01T00:00-00:00"
        transaction = TransactionOut(
            id=uuid4(),
            amount=Decimal("1.00"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=account_id,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=transaction, authd_user=user_id) as (client, _, _):
            response = await client.get(f"{BASE_URL}?before={before}", headers=headers)

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(msg="Only returns Transactions <= to given timestamp."):
            for item in response.json():
                self.assertLessEqual(
                    datetime.fromisoformat(item["timestamp"]),
                    datetime.fromisoformat(before),
                )

    async def test_filter_minimum_and_maximum_timestamp(self) -> None:
        """Requests can filter by both minimum and maximum timestamp."""
        user_id = uuid4()
        account_id = uuid4()
        after = "2020-01-01T00:00-00:00"
        before = "2021-01-01T00:00-00:00"
        transaction = TransactionOut(
            id=uuid4(),
            amount=Decimal("1.00"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2020-12-10T08:12-05:00"),
            account_id=account_id,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=transaction, authd_user=user_id) as (client, _, _):
            response = await client.get(
                f"{BASE_URL}?after={after}&before={before}", headers=headers
            )

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(
            msg="Only returns Transactions inclusive between timestamps."
        ):
            body = response.json()
            for item in body:
                with self.subTest(msg="Greater than/equal to minimum."):
                    self.assertGreaterEqual(
                        datetime.fromisoformat(item["timestamp"]),
                        datetime.fromisoformat(after),
                    )
                with self.subTest(msg="Less than/equal to maximum."):
                    self.assertLessEqual(
                        datetime.fromisoformat(item["timestamp"]),
                        datetime.fromisoformat(before),
                    )

    async def test_pagination(self) -> None:
        """Requests can be paginated with number of results & page number."""
        user_id = uuid4()
        account_id = uuid4()
        all_transactions = [
            TransactionOut(
                id=uuid4(),
                amount=Decimal("1.00"),
                payee="a payee",
                description="a description",
                timestamp=datetime.fromisoformat(f"2019-12-10T08:{12 + i:02d}-05:00"),
                account_id=account_id,
            )
            for i in range(10)
        ]
        page1_rows = [t.model_dump() for t in all_transactions[:5]]
        page2_rows = [t.model_dump() for t in all_transactions[5:]]
        limit = 5
        headers = get_fake_token_header(user_id)

        async with setup(authd_user=user_id) as (client, _, set_db_res):
            set_db_res(page1_rows)
            response1 = await client.get(
                f"{BASE_URL}?limit={limit}&page=0", headers=headers
            )

            with self.subTest(msg="Responds with a status code of 200."):
                self.assertEqual(200, response1.status_code)

            with self.subTest(
                msg="Responds with number of Transactions specified by limit."
            ):
                body1 = response1.json()
                self.assertEqual(len(body1), limit)

            with self.subTest(msg=f"Can get next {limit} Transactions using page."):
                set_db_res(page2_rows)
                response2 = await client.get(
                    f"{BASE_URL}?limit={limit}&page=1", headers=headers
                )
                body2 = response2.json()
                first_page = [tran["id"] for tran in body1]
                for tran in body2:
                    with self.subTest():
                        self.assertNotIn(tran["id"], first_page)


class TestRoutePutId(TestCase):
    """Tests for `PUT /transaction/{id}`."""

    async def test_valid_request(self) -> None:
        """Testing a valid request's response."""
        user_id = uuid4()
        account_id = uuid4()
        tran_id = uuid4()
        changes = {"description": "something new"}
        expected = TransactionOut(
            id=tran_id,
            amount=Decimal("1.23"),
            payee="a payee",
            description="something new",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=account_id,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=expected, authd_user=user_id) as (client, _, _):
            response = await client.put(
                f"{BASE_URL}/{tran_id}",
                headers=headers,
                json=changes,
            )

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(msg="Returns the updated transaction."):
            body = response.json()
            self.assertEqual(body["description"], changes["description"])

    async def test_cant_update_transactions_if_not_own_account(self) -> None:
        """Return 401 attempting to update transaction for other account."""
        user_id = uuid4()
        other_account = uuid4()
        tran_id = uuid4()
        other_transaction = TransactionOut(
            id=tran_id,
            amount=Decimal("1.23"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=other_account,
        )
        changes = {"description": "new description"}
        headers = get_fake_token_header(user_id)

        async with setup(db_value=other_transaction, authd_user=user_id) as (
            client,
            _,
            _,
        ):
            response = await client.put(
                f"{BASE_URL}/{tran_id}",
                headers=headers,
                json=changes,
            )

            self.assertEqual(401, response.status_code)


class TestRouteDeleteId(TestCase):
    """Test DELETE /transaction/{id}."""

    async def test_valid_request(self) -> None:
        """Testing a valid request's response."""
        user_id = uuid4()
        account_id = uuid4()
        tran_id = uuid4()
        expected = TransactionOut(
            id=tran_id,
            amount=Decimal("1.23"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=account_id,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=expected, authd_user=user_id) as (client, _, _):
            response = await client.delete(
                f"{BASE_URL}/{tran_id}",
                headers=headers,
            )

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

    async def test_cant_delete_transactions_if_not_own_account(self) -> None:
        """Return 401 attempting to delete transaction for other account."""
        user_id = uuid4()
        other_account = uuid4()
        tran_id = uuid4()
        other_transaction = TransactionOut(
            id=tran_id,
            amount=Decimal("1.23"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=other_account,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=other_transaction, authd_user=user_id) as (
            client,
            _,
            _,
        ):
            response = await client.delete(
                f"{BASE_URL}/{tran_id}",
                headers=headers,
            )

            self.assertEqual(401, response.status_code)


class TestRoutePutSpentFrom(TestCase):
    """Test PUT /transaction/{id}/spent_from/{spent_from_id}."""

    async def test_valid_request(self) -> None:
        """Testing a valid request's response."""
        user_id = uuid4()
        account_id = uuid4()
        tran_id = uuid4()
        envelope_id = uuid4()
        expected = TransactionOut(
            id=tran_id,
            amount=Decimal("1.23"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=account_id,
            spent_from=envelope_id,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=expected, authd_user=user_id) as (client, _, _):
            response = await client.put(
                f"{BASE_URL}/{tran_id}/spent_from/{envelope_id}",
                headers=headers,
            )

        with self.subTest(msg="Responds with a status code of 200."):
            self.assertEqual(200, response.status_code)

        with self.subTest(msg="Responds with updated Transaction."):
            body = response.json()
            self.assertEqual(UUID(body["spent_from"]), envelope_id)

    async def test_cant_update_transactions_if_not_own_account(self) -> None:
        """Return 401 attempting to update transaction for other account."""
        user_id = uuid4()
        other_account = uuid4()
        tran_id = uuid4()
        envelope_id = uuid4()
        other_transaction = TransactionOut(
            id=tran_id,
            amount=Decimal("1.23"),
            payee="a payee",
            description="a description",
            timestamp=datetime.fromisoformat("2019-12-10T08:12-05:00"),
            account_id=other_account,
        )
        headers = get_fake_token_header(user_id)

        async with setup(db_value=other_transaction, authd_user=user_id) as (
            client,
            _,
            _,
        ):
            response = await client.put(
                f"{BASE_URL}/{tran_id}/spent_from/{envelope_id}",
                headers=headers,
            )

            self.assertEqual(401, response.status_code)


if __name__ == "__main__":
    main()
