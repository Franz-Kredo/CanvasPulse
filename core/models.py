from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime, timedelta, timezone

from utils.iso_parser import _parse_iso


def _as_tuple(xs: Optional[List[Any]]) -> Tuple[Any, ...]:
    if not xs:
        return ()
    return tuple(xs)


@dataclass(frozen=True)
class Course:
    id: int
    name: str
    workflow_state: str
    enrollment_term_id: Optional[int] = None

    @staticmethod
    def from_api(d: dict) -> "Course":
        return Course(
            id=int(d["id"]),
            name=d.get("name", ""),
            workflow_state=d.get("workflow_state", ""),
            enrollment_term_id=d.get("enrollment_term_id"),
        )

    def get_present_vars(self) -> tuple:
        return (
            self.id,
            self.name,
            self.workflow_state,
            self.enrollment_term_id
        )

    def __str__(self) -> str:
        term = self.enrollment_term_id if self.enrollment_term_id is not None else "-"
        return f"{self.id} · {self.name} [{self.workflow_state}] (term {term})"


@dataclass(frozen=True)
class Assignment:
    """A clean, immutable representation of a Canvas assignment."""

    # Core
    id: int
    title: str
    course_name: str
    url: Optional[str]
    points: Optional[float]
    published: bool
    due_at: Optional[datetime]

    # Extras from API
    course_id: Optional[int] = None
    description: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    unlock_at: Optional[datetime] = None
    lock_at: Optional[datetime] = None

    has_overrides: bool = False
    only_visible_to_overrides: bool = False
    important_dates: bool = False

    submission_types: Tuple[str, ...] = ()
    allowed_extensions: Tuple[str, ...] = ()
    grading_type: Optional[str] = None
    grading_standard_id: Optional[int] = None
    grade_group_students_individually: bool = False
    group_category_id: Optional[int] = None

    peer_reviews: bool = False
    automatic_peer_reviews: bool = False
    moderated_grading: bool = False
    omit_from_final_grade: bool = False
    has_submitted_submissions: bool = False

    all_dates_raw: Tuple[Dict[str, Any], ...] = ()
    all_dates_due_ats: Tuple[Optional[datetime], ...] = ()

    # per-user submission snapshot (when include[]=submission)
    submission_workflow_state: Optional[str] = None
    submission_submitted_at: Optional[datetime] = None
    submission_graded_at: Optional[datetime] = None
    submission_score: Optional[float] = None
    submission_late: Optional[bool] = None
    submission_missing: Optional[bool] = None

    @classmethod
    def from_api_dict(cls, data: Dict[str, Any], course_name: str) -> "Assignment":
        """Create an Assignment from a raw Canvas API dict."""
        all_dates = data.get("all_dates") or []
        parsed_due_dates = tuple(
            _parse_iso(d.get("due_at")) if isinstance(d, dict) else None
            for d in all_dates
        )

        sub = data.get("submission") or {}
        wf = sub.get("workflow_state")
        submitted_at = _parse_iso(sub.get("submitted_at"))
        graded_at = _parse_iso(sub.get("graded_at"))
        score = (float(sub["score"]) if sub.get("score") is not None else None)

        return cls(
            id=int(data.get("id")),
            title=data.get("name", "Untitled"),
            course_name=course_name,
            url=data.get("html_url"),
            points=(float(data["points_possible"])
                    if data.get("points_possible") is not None else None),
            published=bool(data.get("published", False)),
            due_at=_parse_iso(data.get("due_at")),

            course_id=(int(data["course_id"])
                       if data.get("course_id") is not None else None),
            description=data.get("description"),

            created_at=_parse_iso(data.get("created_at")),
            updated_at=_parse_iso(data.get("updated_at")),
            unlock_at=_parse_iso(data.get("unlock_at")),
            lock_at=_parse_iso(data.get("lock_at")),

            has_overrides=bool(data.get("has_overrides", False)),
            only_visible_to_overrides=bool(
                data.get("only_visible_to_overrides", False)
            ),
            important_dates=bool(data.get("important_dates", False)),

            submission_types=tuple(
                str(x) for x in _as_tuple(data.get("submission_types"))
            ),
            allowed_extensions=tuple(
                str(x) for x in _as_tuple(data.get("allowed_extensions"))
            ),
            grading_type=(str(data["grading_type"])
                          if data.get("grading_type") is not None else None),
            grading_standard_id=(int(data["grading_standard_id"])
                                 if data.get("grading_standard_id")
                                 is not None else None),
            grade_group_students_individually=bool(
                data.get("grade_group_students_individually", False)
            ),
            group_category_id=(int(data["group_category_id"])
                               if data.get("group_category_id")
                               is not None else None),

            peer_reviews=bool(data.get("peer_reviews", False)),
            automatic_peer_reviews=bool(data.get("automatic_peer_reviews", False)),
            moderated_grading=bool(data.get("moderated_grading", False)),
            omit_from_final_grade=bool(data.get("omit_from_final_grade", False)),
            has_submitted_submissions=bool(
                data.get("has_submitted_submissions", False)
            ),

            all_dates_raw=tuple(d for d in all_dates if isinstance(d, dict)),
            all_dates_due_ats=parsed_due_dates,

            submission_workflow_state=(str(wf) if wf is not None else None),
            submission_submitted_at=submitted_at,
            submission_graded_at=graded_at,
            submission_score=score,
            submission_late=(
                bool(sub.get("late")) if sub.get("late") is not None else None
            ),
            submission_missing=(
                bool(sub.get("missing"))
                if sub.get("missing") is not None else None
            ),
        )

    def get_present_vars(self) -> tuple:
        return (
            self.id,
            self.title,
            self.course_name,
            self.url,
            self.due_at,
        )

    def is_overdue(self, window_days: int) -> bool:
        """
        Checks if the assignment is overdue but still within display window.
        """
        now = datetime.now(timezone.utc)
        windows_end = now - timedelta(days=window_days)

        is_due_and_in_window = (
            self.due_at is not None and
            windows_end <= self.due_at < now
        )
        return is_due_and_in_window

    def is_submitted(self) -> bool:
        """
        Checks the submission status from the raw API dictionary.
        """
        if self.submission_submitted_at:
            return True
        state = (self.submission_workflow_state or "").lower()
        return state in {"submitted", "graded", "pending_review"}

    def __str__(self) -> str:
        pts = "-" if self.points is None else f"{self.points:g} pts"
        pub = "published" if self.published else "unpublished"
        due = self.due_at.strftime("%Y-%m-%d %H:%M") if self.due_at else "—"
        return (
            f"{self.id} · {self.title} ({self.course_name}) — "
            f"due {due} · {pts} · {pub}"
        )
