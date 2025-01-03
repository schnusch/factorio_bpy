import base64
import json
import zlib
from typing import Iterable, List, Tuple

from sympy import Integer
from sympy.core.relational import Eq, Ne, Lt, Le, Gt, Ge, Rel
from sympy.logic.boolalg import And, Not, Or, to_dnf

from .types import Blueprint, Entity, EntityNumber, Signal, Root, WireConnectorID


def json_dumps(o, compact: bool = True) -> str:
    def default(o):
        if isinstance(o, Signal):
            return o.json
        elif isinstance(o, Rel):
            try:
                op = {
                    Eq: "=",
                    Ne: "≠",
                    Lt: "<",
                    Le: "≤",
                    Gt: ">",
                    Ge: "≥",
                }[o.func]
            except KeyError:
                # TODO
                raise
            assert len(o.args) == 2
            assert isinstance(o.args[0], Signal)
            assert isinstance(o.args[1], (Signal, Integer))
            condition = {
                "first_signal": default(o.args[0]),
                "comparator": op,
            }
            if isinstance(o.args[1], Integer):
                condition["constant"] = int(o.args[1])
            else:
                condition["second_signal"] = default(o.args[1])
            return [condition]
        elif isinstance(o, (And, Not, Or)):
            dnf = to_dnf(o, simplify=False)
            if isinstance(dnf, Not):
                raise NotImplementedError("unexpected {o!r} in disjunctive normal form")
            conditions = []
            for conj in dnf.args if isinstance(dnf, Or) else (dnf,):
                first = True
                for term in conj.args if isinstance(conj, And) else (conj,):
                    condition = default(term)
                    if first:
                        first = False
                    else:
                        condition[0]["compare_type"] = "and"
                    conditions.extend(condition)
            return conditions
        else:
            raise TypeError(f"cannot JSON serialize {type(o)!r}: {o!r}")

    return json.dumps(
        o,
        separators=(",", ":") if compact else (",", ": "),
        indent=None if compact else 2,
        ensure_ascii=False,
        sort_keys=True,
        default=default,
    )


def bp_load(bp: str) -> Root:
    """Decode a blueprint string."""
    assert bp.startswith("0")
    return json.loads(
        zlib.decompress(base64.standard_b64decode(bp[1:])).decode("utf-8")
    )


def bp_dump(bp: Root) -> str:
    """Encode blueprint string."""
    return "0" + base64.standard_b64encode(
        zlib.compress(
            json_dumps(bp).encode("utf-8")
        )
    ).decode("ascii")


def add_wire(
    bp: Blueprint,
    start: Tuple[EntityNumber, WireConnectorID],
    end: Tuple[EntityNumber, WireConnectorID],
) -> None:
    """Create a wire connection between two entities."""
    assert any(
        e["entity_number"] == start[0] for e in bp["entities"]
    ), f"entity start={start!r} not in blueprint"
    assert any(
        e["entity_number"] == end[0] for e in bp["entities"]
    ), f"entity end={end!r} not in blueprint"
    bp.setdefault("wires", []).append((*start, *end))


def hstack(
    entities: Iterable[Entity],
    xstep: int = 1,
    ystep: int = 1,
) -> List[Entity]:
    """Place entites horizontally next to each other."""
    return [
        {
            "position": {
                "x": i * xstep - xstep / 2,
                "y": ystep / 2,
            },
            "entity_number": EntityNumber(i),
            **e,
        }
        for i, e in enumerate(entities, start=1)
    ]
