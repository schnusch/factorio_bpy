import pprint
from functools import reduce
from typing import Mapping  # noqa: F401
from typing import Iterator, Tuple, Union

from .types import Comparator, Condition, Signal


class Verum(Condition):
    """A condition that is always true."""

    def __init__(self) -> None:
        pass

    def __iter__(self) -> Iterator[Condition]:
        # TODO
        return iter(())

    def __eq__(self, other) -> bool:
        return isinstance(other, Verum)

    def __invert__(self) -> "Falsum":
        return Falsum()

    def __and__(self, other: Condition) -> Condition:
        return other

    def __or__(self, other: Condition) -> "Verum":
        return self

    def to_list(self):
        return [
            {
                "first_signal": Signal(name="signal-T", type="virtual"),
                "comparator": "=",
                "second_signal": Signal(name="signal-T", type="virtual"),
            },
        ]

    def __repr__(self) -> str:
        return "Verum()"


class Falsum(Condition):
    """A condition that is always false."""

    def __init__(self) -> None:
        pass

    def __iter__(self) -> Iterator[Condition]:
        # TODO
        return iter(())

    def __eq__(self, other) -> bool:
        return isinstance(other, Falsum)

    def __invert__(self) -> "Verum":
        return Verum()

    def __and__(self, other: Condition) -> "Falsum":
        return self

    def __or__(self, other: Condition) -> Condition:
        return other

    def to_list(self):
        return [
            {
                "first_signal": Signal(name="signal-F", type="virtual"),
                "comparator": "≠",
                "second_signal": Signal(name="signal-F", type="virtual"),
            },
        ]

    def __repr__(self) -> str:
        return "Falsum()"


class Comparison(Condition):
    """A basic condition of a Decider Combinator."""

    first_signal: Signal
    comparator: Comparator
    second_signal: Union[int, Signal]

    def __init__(
        self,
        first_signal: Signal,
        comparator: Comparator,
        second_signal: Union[int, Signal],
    ):
        self.first_signal = first_signal
        self.comparator = comparator
        self.second_signal = second_signal

    def __iter__(self) -> Iterator["Condition"]:
        yield self

    def __eq__(self, other) -> bool:
        return isinstance(other, Comparison) and (
            self.first_signal,
            self.comparator,
            self.second_signal,
        ) == (
            other.first_signal,
            other.comparator,
            other.second_signal,
        )

    def __invert__(self) -> "Condition":
        opposite = {
            "=": "≠",
            "≠": "=",
            "<": "≥",
            ">": "≤",
            "≤": ">",
            "≥": "<",
        }  # type: Mapping[Comparator, Comparator]
        return Comparison(
            self.first_signal,
            opposite[self.comparator],
            self.second_signal,
        )

    def __and__(self, other: "Condition") -> "Condition":
        if isinstance(other, (Verum, Falsum)):
            return other & self
        elif isinstance(other, Conjunction):
            return Conjunction(self, *other.parts)
        elif isinstance(other, Disjunction):
            # AND self with every condition in the other
            return Disjunction(*(self & part for part in other.parts))
        elif self == other:
            return self
        elif self == ~other:
            return Falsum()
        else:
            return Conjunction(self, other)

    def __or__(self, other: "Condition") -> "Condition":
        if isinstance(other, (Verum, Falsum)):
            return other | self
        elif isinstance(other, Disjunction):
            return Disjunction(self, *other.parts)
        elif self == other:
            return self
        elif self == ~other:
            return Verum()
        else:
            # disjunctive normal form
            return Disjunction(self, other)

    def to_list(self):
        x = {
            "first_signal": self.first_signal,
            "comparator": self.comparator,
        }
        if isinstance(self.second_signal, int):
            x["constant"] = self.second_signal
        else:
            x["second_signal"] = self.second_signal
        return [x]

    def __repr__(self) -> str:
        return f"Condition({self.first_signal!r}, {self.comparator!r}, {self.second_signal!r})"


class Conjunction(Condition):
    """An AND-clause of comparisons."""

    parts: Tuple[Condition, ...]

    def __init__(self, *parts: Condition):
        for part in parts:
            assert isinstance(part, Comparison), f"{part} is not a plain Condition"
        self.parts = parts

    def __iter__(self) -> Iterator[Condition]:
        for part in self.parts:
            yield from iter(part)

    def __eq__(self, other) -> bool:
        raise NotImplementedError

    def __invert__(self) -> "Disjunction":
        return Disjunction(*(~x for x in self.parts))

    def __and__(self, other: Condition) -> Condition:
        if isinstance(other, (Verum, Falsum)):
            return other & self
        elif isinstance(other, Conjunction):
            return Conjunction(*self.parts, *other.parts)
        elif isinstance(other, Disjunction):
            # disjunctive normal form: (A & B) | (C & D) | ...
            # AND self to every disjunct term
            return Disjunction(*(self & part for part in other.parts))
        else:
            return Conjunction(*self.parts, other)

    def __or__(self, other: "Condition") -> "Condition":
        if isinstance(other, (Verum, Falsum)):
            return other | self
        elif isinstance(other, Disjunction):
            return Disjunction(self, *other.parts)
        else:
            # disjunctive normal form
            return Disjunction(self, other)

    def to_list(self):
        xs = []
        for i, part in enumerate(self.parts):
            ys = part.to_list()
            assert len(ys) == 1
            xs.append(ys[0])
            if i > 0:
                xs[i]["compare_type"] = "and"
        return xs

    def __repr__(self) -> str:
        return ", ".join(repr(x) for x in self.parts).join(("Conjunction(", ")"))


class Disjunction(Condition):
    """An OR-clause of comparisons or conjunctions (AND-clauses)."""

    parts: Tuple[Condition, ...]

    def __init__(self, *parts: Condition):
        for part in parts:
            assert not isinstance(
                part, Disjunction
            ), f"{part} is already a Disjunction:\n{parts}"
        self.parts = parts

    def __iter__(self) -> Iterator[Condition]:
        for part in self.parts:
            yield from iter(part)

    def __eq__(self, other) -> bool:
        raise NotImplementedError

    def __invert__(self) -> Condition:
        return reduce(
            lambda a, b: a & b,
            (~p for p in self.parts),
        )

    def __and__(self, other: Condition) -> Condition:
        # disjunctive normal form: (A & B) | (C & D) | ...
        if isinstance(other, (Verum, Falsum)):
            return other & self
        elif isinstance(other, Disjunction):
            # product
            # (A | B) & (C | D) = (A & C) | (A & D) | (B & C) | (B & D)
            return Disjunction(
                *(left & right for left in self.parts for right in other.parts)
            )
        else:
            # AND self to every disjunct term
            # (A | B) & C = (A & C) | (B & C)
            return Disjunction(*(left & other for left in self.parts))

    def __or__(self, other: Condition) -> Condition:
        if isinstance(other, (Verum, Falsum)):
            return other | self
        elif isinstance(other, Disjunction):
            return Disjunction(*self.parts, *other.parts)
        else:
            return Disjunction(*self.parts, other)

    def to_list(self):
        xs = []
        for part in self.parts:
            xs.extend(part.to_list())
        return xs

    def __repr__(self) -> str:
        return ", ".join(repr(x) for x in self.parts).join(("Disjunction(", ")"))


def _pprint_condition_clause(self, object, stream, indent, allowance, context, level):
    cls = object.__class__
    stream.write(cls.__name__ + "(")
    self._format_items(
        object.parts,
        stream,
        indent + len(cls.__name__),
        allowance + 1,
        context,
        level,
    )
    stream.write(")")


pprint.PrettyPrinter._dispatch[Conjunction.__repr__] = _pprint_condition_clause  # type: ignore[attr-defined]
pprint.PrettyPrinter._dispatch[Disjunction.__repr__] = _pprint_condition_clause  # type: ignore[attr-defined]
