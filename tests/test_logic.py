import json
import pprint
import unittest

from factorio_bpy import Signal, json_dumps
from sympy.core.relational import Rel

A = Rel(Signal("signal-A", type="virtual"), 0, "==")
B = Rel(Signal("signal-B", type="virtual"), 0, "==")
C = Rel(Signal("signal-C", type="virtual"), 0, "==")
D = Rel(Signal("signal-D", type="virtual"), 0, "==")


def unjson(x):
    return json.loads(json_dumps(x))


class TestLogic(unittest.TestCase):
    maxDiff = None

    def test_invert(self) -> None:
        """~A"""
        self.assertEqual(
            unjson(~A),
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
            unjson(A | B),
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
            unjson(A | B),
            unjson(A) + unjson(B),
        )

    def test_and(self) -> None:
        """A & B"""
        self.assertEqual(
            unjson(A & B),
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
        self.assertEqual(
            unjson(~(A | B)),
            unjson(~A & ~B),
        )
        self.assertEqual(
            unjson(~(A | B)),
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
        self.assertEqual(
            unjson(~(A & B)),
            unjson(~A | ~B),
        )
        self.assertEqual(
            unjson(~(A & B)),
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
            unjson(~(A & B)),
            unjson(~A) + unjson(~B),
        )

    def test_OR_and(self) -> None:
        """A | (B & C)"""
        self.assertEqual(
            unjson(A | (B & C)),
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
            unjson((A & B) | C),
            [
                {
                    "first_signal": {"name": "signal-C", "type": "virtual"},
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
                    "first_signal": {"name": "signal-B", "type": "virtual"},
                    "comparator": "=",
                    "constant": 0,
                },
            ],
        )

    def test_AND_or(self) -> None:
        """A & (B | C) = (A & B) | (A & C)"""
        self.assertEqual(
            unjson(A & (B | C)),
            unjson((A & B) | (A & C)),
        )
        self.assertEqual(
            unjson(A & (B | C)),
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
        self.assertEqual(
            unjson((A | B) & C),
            unjson((A & C) | (B & C)),
        )
        self.assertEqual(
            unjson((A | B) & C),
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
        self.assertEqual(
            unjson((A | B) & (C | D)),
            unjson((A & C) | (A & D) | (B & C) | (B & D)),
        )
        self.assertEqual(
            unjson((A | B) & (C | D)),
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
        self.assertEqual(
            unjson(~(A & (B | C))),
            unjson(~A | (~B & ~C)),
        )
