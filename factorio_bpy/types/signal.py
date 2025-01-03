from typing import Literal, Optional

from sympy import Symbol

Quality = Literal[
    "normal",
    "uncommon",
    "rare",
    "epic",
    "legendary",
]


def latex_escape(x: str) -> str:
    # TODO implement
    return x


class Signal(Symbol):
    type: str
    name: str
    quality: Quality

    def __new__(
        cls,
        name: str,
        *,
        quality: Quality = "normal",
        type: Optional[str] = None,
    ):
        if type is None:
            type = "item"
        var = {
            "entity": "E",
            "fluid": "F",
            "item": "I",
            "recipe": "R",
            "virtual": "V",
        }[type]
        o = super().__new__(cls, "%s_{%s}" % (var, latex_escape(name)))
        o.json = {"name": name}
        if type != "item":
            o.json["type"] = type
        if quality != "normal":
            o.json["quality"] = quality
        return o
