# cli/presenter_console.py
from __future__ import annotations
from typing import Any, List, Sequence, Iterable, Tuple, Union, Dict
from core.ports import IPresenter
from core.models import Course
from datetime import datetime

from shutil import get_terminal_size

ELLIPSIS = "…"


def _ellipsize(text: str, max_len: int) -> str:
    if max_len <= 1:
        return text[:max_len]
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + ELLIPSIS


def _fmt_cell(v: Any) -> str:
    """Render cells; collapse datetimes to 'YYYY-MM-DD HH:MM' (no seconds/ms)."""
    if v is None:
        return ""
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M")
    return str(v)


class ConsolePresenter(IPresenter):
    def display_title(self, title: str) -> None:
        """Print a 50-char banner like '===== TITLE ====='."""
        total = 50
        core = f" {title.strip()} "
        pad = max(0, total - len(core))
        left = pad // 2
        right = pad - left
        line = f"{'=' * left}{core}{'=' * right}"
        print(line[:total])

    def display_table(
        self,
        headers: Sequence[str],
        rows: Sequence[Sequence[Any]],
        padding: int = 2,
        trim_col_index: int | None = None,
        min_trim: int = 8,
    ) -> None:
        """
        Print a simple left-aligned table. If the total width exceeds the
        terminal width, only the column at `trim_col_index` is truncated.

        :param headers: Column names.
        :param rows:    Iterable of row values (each row is a sequence).
        :param padding: Spaces between columns.
        :param trim_col_index: Index of column allowed to shrink (e.g., 1 for
                               "Title"). If None, no trimming happens.
        :param min_trim: Minimum width we allow when trimming.
        """
        if not rows:
            print("No data.")
            return

        str_rows: List[List[str]] = [[_fmt_cell(v) for v in r] for r in rows]
        str_headers: List[str] = [_fmt_cell(h) for h in headers]

        # Natural widths (max of header/data)
        cols = list(zip(*([str_headers] + str_rows)))
        widths = [max(len(s) for s in col) for col in cols]

        # Compute total width
        sep = " " * padding
        total_width = sum(widths) + padding * (len(widths) - 1)

        # Terminal width
        term_width = get_terminal_size(fallback=(120, 20)).columns

        # If too wide, try trimming one column (e.g., Title)
        if trim_col_index is not None and total_width > term_width:
            over_by = total_width - term_width
            # How much we can reduce this column
            max_cut = widths[trim_col_index] - min_trim
            cut = min(over_by, max(0, max_cut))
            if cut > 0:
                widths[trim_col_index] -= cut
                # Apply ellipsis to that column in all rows
                for r in str_rows:
                    r[trim_col_index] = _ellipsize(
                        r[trim_col_index], widths[trim_col_index]
                    )
                # Also trim header if needed
                str_headers[trim_col_index] = _ellipsize(
                    str_headers[trim_col_index], widths[trim_col_index]
                )

        # Print header
        header_line = sep.join(
            str_headers[i].ljust(widths[i]) for i in range(len(widths))
        )
        divider = sep.join("-" * w for w in widths)
        print(header_line)
        print(divider)

        # Print rows
        for row in str_rows:
            line = sep.join(row[i].ljust(widths[i]) for i in range(len(widths)))
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

        self.display_table(headers, rows)

    def display_terms(self, terms):
        raise NotImplementedError

    def display_assignments(self, overdue, upcoming):
        # Column order: ("ID", "Title", "Course", "URL", "Due At")
        title_col = 1

        self.display_title("overdue")
        self.display_table(
            headers=("ID", "Title", "Course", "URL", "Due At"),
            rows=[a.get_present_vars() for a in overdue],
            padding=2,
            trim_col_index=title_col,
            min_trim=12,  # keep at least 12 chars of the title
        )

        self.display_title("upcoming")
        self.display_table(
            headers=("ID", "Title", "Course", "URL", "Due At"),
            rows=[a.get_present_vars() for a in upcoming],
            padding=2,
            trim_col_index=title_col,
            min_trim=12,
        )
