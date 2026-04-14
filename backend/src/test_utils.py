"""Tests for util functions."""

from typing import reveal_type
from unittest import TestCase

from src.utils import is_some, some_or_default


class TestOptionUtils(TestCase):
    """Tests for Option type narrowing & other utils."""

    def test_is_some(self):
        """Function returns correct value w/ correct associated type."""

        maybe_strs = [
            ["Some string should be True", "some string", True],
            ["None string should be False", None, False],
        ]
        maybe_nums = [
            ["Some int should be True", 1, True],
            ["None int should be False", None, False],
        ]
        maybe_tups = [
            ["Some tuple should be True", ("tup val 1", None), True],
            ["None tuple should be False", None, False],
        ]

        for msg, case, exp in maybe_strs:
            with self.subTest(msg):
                act = is_some(case)

                self.assertEqual(act, exp)

        for msg, case, exp in maybe_nums:
            with self.subTest(msg):
                act = is_some(case)

                self.assertEqual(act, exp)

        for msg, case, exp in maybe_tups:
            with self.subTest(msg):
                act = is_some(case)

                self.assertEqual(act, exp)

    def test_some_or_default(self):
        """Function returns correct value w/ correct associated type."""

        default_str: str = "default str"
        maybe_strs = [
            ["Some string should give self", "some string", "some string"],
            ["None string should give default", None, default_str],
        ]
        default_num: int = 42
        maybe_nums = [
            ["Some int should give self", 1, 1],
            ["None int should give default", None, default_num],
        ]
        default_tup: tuple[str, int] = (default_str, default_num)
        maybe_tups = [
            ["Some tuple should give self", ("tup val 1", None), ("tup val 1", None)],
            ["None tuple should give default", None, default_tup],
        ]

        for msg, case, exp in maybe_strs:
            with self.subTest(msg):
                act = some_or_default(case, default_str)

                self.assertEqual(act, exp)

        for msg, case, exp in maybe_nums:
            with self.subTest(msg):
                act = some_or_default(case, default_num)

                self.assertEqual(act, exp)

        for msg, case, exp in maybe_tups:
            with self.subTest(msg):
                act = some_or_default(case, default_tup)

                self.assertEqual(act, exp)
