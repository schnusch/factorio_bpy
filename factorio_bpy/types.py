from enum import IntEnum
from decimal import Decimal
from typing import Iterator, List, Literal, NewType, Tuple, TypedDict, Union

EntityNumber = NewType("EntityNumber", int)


class WireConnectorID(IntEnum):
    circuit_green = 2
    circuit_red = 1
    combinator_input_green = 2
    combinator_input_red = 1
    combinator_output_green = 4
    combinator_output_red = 3
    pole_copper = 5
    power_switch_left_copper = 5
    power_switch_right_copper = 6

    def __repr__(self):
        return repr(self._value_)


WireConnection = Tuple[
    EntityNumber,
    WireConnectorID,
    EntityNumber,
    WireConnectorID,
]


class Position(TypedDict, total=True):
    x: Union[int, float, Decimal]
    y: Union[int, float, Decimal]


class Entity(TypedDict, total=False):
    name: str
    entity_number: EntityNumber
    position: Position


class _Blueprint(TypedDict, total=True):
    item: Literal["blueprint"]


class Blueprint(_Blueprint, total=False):
    entities: List[Entity]
    wires: List[WireConnection]


class Root(TypedDict, total=True):
    blueprint: Blueprint


class _Signal(TypedDict, total=True):
    signal: str


class Signal(_Signal, total=False):
    type: str
    # TODO red/green wires


# Decider Combinator

Comparator = Literal[
    "=",
    "≠",
    "<",
    ">",
    "≤",
    "≥",
]


class Condition(object):
    """Base class of conditions used by the Decider Combinators."""

    def __iter__(self) -> Iterator["Condition"]:
        """Iterate over all simple conditions in a clause."""
        ...

    def __eq__(self, other) -> bool:
        ...

    def __invert__(self) -> "Condition":
        ...

    def __and__(self, other: "Condition") -> "Condition":
        ...

    def __or__(self, other: "Condition") -> "Condition":
        ...

    def to_list(self):
        """Convert to a list of JSON conditions used by Factorio."""
        ...


class _DeciderOutput(TypedDict, total=True):
    signal: Signal


class DeciderOutput(_DeciderOutput, total=False):
    copy_count_from_input: bool
    # TODO red/green wires


class DeciderConditions(TypedDict, total=True):
    conditions: Condition
    outputs: List[DeciderOutput]


class ControlBehavior(TypedDict, total=True):
    decider_conditions: DeciderConditions


class DeciderCombinator(Entity, total=True):
    # name: Literal["decider-combinator"]
    control_behavior: ControlBehavior
