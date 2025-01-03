import base64
import json
import zlib
from typing import Iterable, List, Tuple

from .types import Blueprint, Entity, EntityNumber, Root, WireConnectorID


def json_dumps(o, compact: bool = True) -> str:
    def default(o):
        try:
            to_list = getattr(o, "to_list")
        except AttributeError:
            raise TypeError
        return to_list()

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
