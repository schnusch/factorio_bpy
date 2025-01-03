import json
import re
from typing import Callable, List, Optional, TextIO, Tuple

from . import json_dumps
from .logic import Conjunction, Disjunction
from .types import (
    Condition,
    ControlBehavior,
    DeciderCombinator,
    DeciderConditions,
    DeciderOutput,
)


def html_escape(s: str) -> str:
    def repl(m: re.Match) -> str:
        return "&#%d;" % ord(m[0])

    return re.sub(
        r"[^" r" !#$%" r"(-;" r"=" r"?-~" r"]",
        repl,
        s,
        re.UNICODE,
    )


def html_pre(
    content: str,
    lang: Optional[str] = None,
    style: Optional[str] = None,
) -> str:
    pre = f'<pre style="{html_escape(style)}">' if style else "<pre>"
    return pre + html_escape(content) + "</pre>"


def md_escape(s: str) -> str:
    # TODO
    return s


def md_pre(
    content: str,
    lang: Optional[str] = None,
    style: Optional[str] = None,
) -> str:
    return "\n\n```" + (lang or "") + "\n" + content + "\n```\n\n"


class DeciderTable(object):
    """Create a list of configured decider combinators and an accompanying
    truth table."""

    conditions: List[str]
    combinators: List[Tuple[List[DeciderOutput], Condition]]

    def __init__(self, *conditions: Condition) -> None:
        self.conditions = []
        self.combinators = []
        for condition in conditions:
            self.add_condition(condition)

    def add_condition(self, condition: Condition) -> int:
        """Add a condition to the table header."""
        added = 0
        for cond in condition:
            if (
                json_dumps(cond.to_list()[0], compact=False) not in self.conditions
                and json_dumps((~cond).to_list()[0], compact=False) not in self.conditions
            ):
                self.conditions.append(json_dumps(cond.to_list()[0], compact=False))
                added += 1
        return added

    def add_combinator(
        self,
        outputs: List[DeciderOutput],
        condition: Condition,
    ) -> None:
        """Add a new row to the table. If a condition and its inverse are both
        missing from the columns, they are automatically added."""
        for cond in condition:
            if (
                json_dumps(cond.to_list()[0], compact=False) not in self.conditions
                and json_dumps((~cond).to_list()[0], compact=False) not in self.conditions
            ):
                self.conditions.append(json_dumps(cond.to_list()[0], compact=False))
        self.combinators.append((outputs, condition))

    def get_table_rows(self, disj: Condition) -> List[List[Tuple[str, str]]]:
        rows = []  # type: List[List[Tuple[str, str]]]
        for conj in disj.parts if isinstance(disj, Disjunction) else [disj]:
            assert isinstance(conj, Conjunction)
            parts = conj.parts if isinstance(conj, Conjunction) else [conj]

            cols = [("", "")] * len(self.conditions)  # type: List[Tuple[str, str]]
            for cond in parts:
                x = json_dumps(cond.to_list()[0], compact=False)
                try:
                    i = self.conditions.index(x)
                except ValueError:
                    i = self.conditions.index(json_dumps((~cond).to_list()[0], compact=False))
                    cols[i] = (
                        "text-align: center; background: salmon;",
                        "❌",
                    )
                else:
                    cols[i] = (
                        "text-align: center; background: lime;",
                        "✅",
                    )

            rows.append(cols)
        return rows

    def write_html(
        self,
        fp: TextIO,
        *,
        escape: Callable[[str], str] = html_escape,
        pre: Callable[[str, str, str], str] = html_pre,
        colspan: bool = False,
    ) -> None:
        """Write HTML truth table."""
        fp.write('<table style="border-collapse: collapse;">\n')

        fp.write("  <thead>\n")
        if colspan:
            for i, condition in enumerate(reversed(self.conditions)):
                fp.write("    <tr>\n")
                fp.write('      <td colspan="%d"></td>\n' % (len(self.conditions) - i,))
                fp.write('      <td colspan="%d">' % (i + 1,))
                fp.write(pre(condition, "json", "margin: 0;"))
                fp.write("</td>\n")
                fp.write("    </tr>\n")
        else:
            fp.write("    <tr>\n")
            fp.write("      <td></td>\n")
            for condition in self.conditions:
                fp.write('      <th style="text-align: left;">')
                fp.write(pre(condition, "json", "margin: 0;"))
                fp.write("</th>\n")
            fp.write("    </tr>\n")
        fp.write("  </thead>\n")
        fp.write("  <tbody>\n")

        for signal, disj in self.combinators:
            first = True
            rows = self.get_table_rows(disj)
            for cols in rows:
                fp.write("    <tr>\n")
                if first:
                    style = "border-top: 1px solid black; "
                    fp.write(
                        '      <td style="text-align: left; %s" rowspan="%d">'
                        % (style, len(rows))
                    )
                    fp.write(pre(json_dumps(signal, compact=False), "json", "margin: 0;"))
                    fp.write("</td>\n")
                    first = False
                else:
                    style = ""
                for tdstyle, tdcontent in cols:
                    fp.write('    <td style="')
                    fp.write(escape(style))
                    fp.write(escape(tdstyle))
                    fp.write('">')
                    fp.write(escape(tdcontent))
                    fp.write("</td>\n")
                fp.write("    </tr>\n")

        fp.write("  </tbody>\n")
        fp.write("</table>\n")

    def write_gfm(
        self,
        fp: TextIO,
    ) -> None:
        """Write the truth table in GitHub-flavored markdown."""
        self.write_html(
            fp,
            escape=md_escape,
            pre=md_pre,
            colspan=True,
        )

    def get_combinators(self) -> List[DeciderCombinator]:
        """Return decider combinators."""
        return [
            DeciderCombinator(
                name="decider-combinator",
                control_behavior=ControlBehavior(
                    decider_conditions=DeciderConditions(
                        conditions=condition,
                        outputs=outputs,
                    )
                ),
            )
            for outputs, condition in self.combinators
        ]
