import pprint
import unittest

from factorio_bpy.logic import Comparison
from factorio_bpy.types import Signal

A = Comparison(Signal(name="signal-A", type="virtual"), "=", 0)
B = Comparison(Signal(name="signal-B", type="virtual"), "=", 0)
C = Comparison(Signal(name="signal-C", type="virtual"), "=", 0)
D = Comparison(Signal(name="signal-D", type="virtual"), "=", 0)


class TestLogic(unittest.TestCase):
    maxDiff = None

    def assertToList(self, a, b):
        self.assertEqual(
            a.to_list(),
            b.to_list(),
            "\n" + pprint.pformat(a) + "\nvs.\n" + pprint.pformat(b),
        )
        self.assertEqual(a.to_list(), b.to_list())

    def test_invert(self) -> None:
        """~A"""
        self.assertEqual(
            (~A).to_list(),
            [
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "≠",
                    "constant": 0,
                },
            ],
        )

    def test_or(self) -> None:
        """A | B"""
        self.assertEqual(
            (A | B).to_list(),
            [
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                # OR
                {
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
            ],
        )
        self.assertEqual(
            (A | B).to_list(),
            A.to_list() + B.to_list(),
        )

    def test_and(self) -> None:
        """A & B"""
        self.assertEqual(
            (A & B).to_list(),
            [
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
            ],
        )

    def test_invert_or(self) -> None:
        """~(A | B) == ~A & ~B"""
        self.assertToList(
            ~(A | B),
            ~A & ~B,
        )
        self.assertEqual(
            (~(A | B)).to_list(),
            [
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "≠",
                    "constant": 0,
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                    "comparator": "≠",
                    "constant": 0,
                },
            ],
        )

    def test_invert_and(self) -> None:
        """~(A & B) == ~A | ~B"""
        self.assertToList(
            ~(A & B),
            ~A | ~B,
        )
        self.assertEqual(
            (~(A & B)).to_list(),
            [
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "≠",
                    "constant": 0,
                },
                # OR
                {
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                    "comparator": "≠",
                    "constant": 0,
                },
            ],
        )
        self.assertEqual(
            (~(A & B)).to_list(),
            (~A).to_list() + (~B).to_list(),
        )

    def test_OR_and(self) -> None:
        """A | (B & C)"""
        self.assertEqual(
            (A | (B & C)).to_list(),
            [
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                # OR
                {
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-C", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
            ],
        )

    def test_and_OR(self) -> None:
        """(A & B) | C"""
        self.assertEqual(
            ((A & B) | C).to_list(),
            [
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                # OR
                {
                    "first_signal": {"name": "signal-C", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
            ],
        )

    def test_AND_or(self) -> None:
        """A & (B | C) = (A & B) | (A & C)"""
        self.assertToList(
            A & (B | C),
            (A & B) | (A & C),
        )
        self.assertEqual(
            (A & (B | C)).to_list(),
            [
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                # OR
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-C", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
            ],
        )

    def test_or_AND(self) -> None:
        """(A | B) & C = (A & C) | (B & C)"""
        self.assertToList(
            (A | B) & C,
            (A & C) | (B & C),
        )
        self.assertEqual(
            ((A | B) & C).to_list(),
            [
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-C", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                # OR
                {
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-C", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
            ],
        )

    def test_or_AND_or(self) -> None:
        """(A | B) & (C | D) = (A & C) | (A & D) | (B & C) | (B & D)"""
        self.assertToList(
            (A | B) & (C | D),
            (A & C) | (A & D) | (B & C) | (B & D),
        )
        self.assertEqual(
            ((A | B) & (C | D)).to_list(),
            [
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                {
                    "compare_type": "and",
                    "comparator": "=",
                    "first_signal": {"name": "signal-C", "type": "virtual"},
                    "constant": 0,
                },
                # OR
                {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-D", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                # OR
                {
                    "comparator": "=",
                    "constant": 0,
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-C", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
                # OR
                {
                    "comparator": "=",
                    "constant": 0,
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                },
                {
                    "compare_type": "and",
                    "first_signal": {"name": "signal-D", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
            ],
        )

    def test_invert_AND_or(self) -> None:
        # ~(A & (B | C)
        """FIXME we want

           ~(A & (B | C))
        == ~A | ~(B | C)
        == ~A | (~B & ~C)

        but it currently does

           ~(A & (B | C)
        == ~((A & B) | (A & C))
        == ~(A & B) & ~(A & C)
        == (~A | ~B) & (~A | ~C)
        == (~A & ~A) | (~A & ~C) | (~B & ~A) | (~B & ~C)
        """
        # self.assertToList(
        #     ~(A & (B | C)),
        #     ~A | (~B & ~C),
        # )
        self.assertEqual(
            (~(A & (B | C))).to_list(),
            (~A & ~A).to_list()
            + (~A & ~C).to_list()
            + (~B & ~A).to_list()
            + (~B & ~C).to_list(),
        )
