# cli/presenter_console.py
from __future__ import annotations
from typing import Any, List, Sequence, Iterable, Tuple, Union, Dict
from core.ports import IPresenter
from core.models import Course


class ConsolePresenter(IPresenter):
    def display_table():
        pass

    def _print_table(
        headers: Sequence[str],
        rows: Sequence[Sequence[Any]],
        padding: int = 2,
    ) -> None:
        """
        Print a simple left-aligned table.

        :param headers: Column names.
        :param rows:    Iterable of row values (each row is a sequence).
        :param padding: Spaces between columns.
        """
        if not rows:
            print("No data.")
            return

        columns = list(zip(*([headers] + list(rows))))
        widths = [max(len(str(x)) for x in col) for col in columns]
        sep = " " * padding

        header_line = sep.join(
            str(val).ljust(widths[i]) for i, val in enumerate(headers)
        )
        divider = sep.join("-" * w for w in widths)
        print(header_line)
        print(divider)

        for row in rows:
            line = sep.join(
                str(val).ljust(widths[i]) for i, val in enumerate(row)
            )
            print(line)

    def display_courses(
        self,
        courses: Iterable[Union[Dict[str, Any], Course]],
    ) -> None:
        """
        Prepare rows from Course instances and render via print_table().
        Only Course items are shown.
        """
        headers: Tuple = ("ID", "Name", "State", "Term")

        rows: List[Tuple] = [
            tuple(c.get_present_vars())
            for c in courses
            if isinstance(c, Course)
        ]

        if not rows:
            print("No courses found.")
            return

        self.print_table(headers, rows)

    def display_terms(self, terms):
        raise NotImplementedError

    def display_assignments(self, overdue, upcoming):
        raise NotImplementedError
