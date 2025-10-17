# cli/presenter_console.py
from __future__ import annotations
from typing import Any, List
from core.ports import IPresenter
from core.models import Course


class ConsolePresenter(IPresenter):
    def display_table():
        pass

    def display_courses(self,
                        courses: List[dict[str, Any]] | List[Course]) -> None:

        headers = ("ID", "Name", "State", "Term")

        rows = [c.get_present_vars() for c in courses if isinstance(c, Course)]

        if not rows:
            print("No courses found.")
            return

        columns = list(zip(*([headers] + rows)))
        widths = [max(len(str(x)) for x in col) for col in columns]

        def fmt(row: tuple[Any, Any, Any, Any]) -> str:
            parts = (str(val).ljust(widths[i]) for i, val in enumerate(row))
            return "  ".join(parts)

        print(fmt(headers))
        print("  ".join("-" * w for w in widths))
        for r in rows:
            print(fmt(r))

    def display_terms(self, terms):
        raise NotImplementedError

    def display_assignments(self, overdue, upcoming):
        raise NotImplementedError
