#!/usr/bin/env python3
import pprint
from typing import Dict, List

from factorio_bpy import bp_dump, add_wire, hstack, WireConnectorID
from factorio_bpy.logic import Comparison
from factorio_bpy.table import DeciderTable, html_pre, json_dumps, md_pre
from factorio_bpy.types import DeciderOutput, Signal


have = {}  # type: Dict[str, Condition]
have["iron-ore"] = Comparison(Signal(name="iron-ore"), "≥", 200)
have["carbon"] = Comparison(Signal(name="carbon"), "≥", 50)
have["ice"] = Comparison(Signal(name="ice"), "≥", 100)
have["calcite"] = Comparison(Signal(name="calcite"), "≥", 50)

have["metallic-asteroid-chunk"] = Comparison(Signal(name="metallic-asteroid-chunk"), ">", 0)
have["carbonic-asteroid-chunk"] = Comparison(Signal(name="carbonic-asteroid-chunk"), ">", 0)
have["oxide-asteroid-chunk"] = Comparison(Signal(name="oxide-asteroid-chunk"), ">", 0)


def recipe(name: str) -> DeciderOutput:
    return DeciderOutput(
        copy_count_from_input=False,
        signal=Signal(
            name=name,
            type="recipe",
        ),
    )


table = DeciderTable(
    # Passing conditions to DeciderTable is completely optional, but useful
    # to manually order the columns.
    have["metallic-asteroid-chunk"],
    have["carbonic-asteroid-chunk"],
    have["oxide-asteroid-chunk"],
    have["iron-ore"],
    have["carbon"],
    have["ice"],
    have["calcite"],
)

# set conditions for each output
table.add_combinator(
    [recipe("advanced-oxide-asteroid-crushing")],
    have["oxide-asteroid-chunk"]
    & ~have["calcite"],
)
table.add_combinator(
    [recipe("oxide-asteroid-crushing")],
    have["oxide-asteroid-chunk"]
    & ~have["ice"]
    & have["calcite"],
)
table.add_combinator(
    [recipe("metallic-asteroid-crushing")],
    have["metallic-asteroid-chunk"]
    & ~have["iron-ore"]
    & (
        ~have["oxide-asteroid-chunk"]
        | (have["calcite"] & have["ice"])
    ),
)
table.add_combinator(
    [recipe("carbonic-asteroid-crushing")],
    have["carbonic-asteroid-chunk"]
    & ~have["carbon"]
    & (
        ~have["oxide-asteroid-chunk"]
        | (have["calcite"] & have["ice"])
    )
    & (
        ~have["metallic-asteroid-chunk"]
        | have["iron-ore"]
    ),
)

# set conditions for recprocessing
table.add_combinator(
    [recipe("metallic-asteroid-reprocessing")],
    have["metallic-asteroid-chunk"]
    & (
        ~(have["oxide-asteroid-chunk"] | (have["calcite"] & have["ice"]))
        | ~(have["carbonic-asteroid-chunk"] | have["carbon"])
    ),
)
table.add_combinator(
    [recipe("carbonic-asteroid-reprocessing")],
    have["carbonic-asteroid-chunk"]
    & (
        ~(have["metallic-asteroid-chunk"] | have["iron-ore"])
        | ~(have["oxide-asteroid-chunk"] | (have["calcite"] & have["ice"]))
    ),
)
table.add_combinator(
    [recipe("oxide-asteroid-reprocessing")],
    have["oxide-asteroid-chunk"]
    & (
        ~(have["metallic-asteroid-chunk"] | have["iron-ore"])
        | ~(have["carbonic-asteroid-chunk"] | have["carbon"])
    ),
)

bp = {
    "entities": hstack(table.get_combinators(), ystep=2),
}

# create wire connections between decider combinators
prev = None  # type: Optional[int]
for e in bp["entities"]:
    if prev is not None:
        # connect inputs with red wires
        add_wire(
            bp,
            (prev, WireConnectorID.combinator_input_red),
            (e["entity_number"], WireConnectorID.combinator_input_red),
        )
        # connect outputs with red wires
        add_wire(
            bp,
            (prev, WireConnectorID.combinator_output_red),
            (e["entity_number"], WireConnectorID.combinator_output_red),
        )
    prev = e["entity_number"]

if __name__ == "__main__":
    import sys

    print(WireConnectorID.combinator_output_red, file=sys.stderr)

    # write the blueprint and the HTML table to stdout
    sys.stdout.write(
        html_pre(
            bp_dump({"blueprint": bp}),
            None,
            "word-break: break-all; white-space: pre-wrap;",
        )
    )
    sys.stdout.write("\n")
    table.write_html(sys.stdout)
    sys.stdout.write(
        html_pre(
            pprint.pformat({"blueprint": bp}),
            "python",
        )
    )

    # write README.md if it does not exist
    try:
        fp = open("README.md", "x", encoding="utf-8")
    except FileNotFoundError:
        pass
    else:
        try:
            fp.write("# Advanced Asteroid Crushing")
            fp.write(md_pre(bp_dump({"blueprint": bp})))
            table.write_gfm(fp)
            fp.write("\n")
            fp.write(md_pre(pprint.pformat({"blueprint": bp}), "python").strip())
            fp.write("\n")
        finally:
            fp.close()
