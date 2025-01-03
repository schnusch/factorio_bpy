from enum import IntEnum
from decimal import Decimal
from typing import List, Literal, NewType, Tuple, TypedDict, Union

from sympy.logic.boolalg import And, Or

# re-export
from .core import Quality  # noqa: F401
from .signal import Signal

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


# Decider Combinator

class _DeciderOutput(TypedDict, total=True):
    signal: Signal


class DeciderOutput(_DeciderOutput, total=False):
    copy_count_from_input: bool
    # TODO red/green wires


class DeciderConditions(TypedDict, total=True):
    conditions: Union[And, Or]
    outputs: List[DeciderOutput]


class DeciderCombinator(Entity, total=True):
    name: Literal["decider-combinator"]
    control_behavior: TypedDict(
        "DeciderControlBehaviour", {"decider_conditions": DeciderConditions}, total=True
    )
