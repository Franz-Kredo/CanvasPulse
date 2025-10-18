from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta

from utils.iso_parser import _parse_iso


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


@dataclass(frozen=True)
class Assignment:
    """A clean, immutable representation of a Canvas assignment."""
    id: int
    title: str
    course_name: str
    url: str
    points: Optional[float]
    published: bool
    due_at: Optional[datetime]

    @classmethod
    def from_api_dict(cls, data: dict, course_name: str) -> Assignment:
        """Factory method to create an Assignment from a raw API dictionary."""
        return cls(
            id=data.get("id"),
            title=data.get("name", "Untitled"),
            course_name=course_name,
            url=data.get("html_url"),
            points=data.get("points_possible"),
            published=data.get("published", False),
            due_at=_parse_iso(data.get("due_at")),
        )

    def is_overdue(self, now: datetime, window_days: int) -> bool:
        """
        Checks if the assignment is overdue but still within display window.
        """
        if self.due_at is None or self.due_at > now:
            return False

        window_end = self.due_at + timedelta(days=window_days)
        return now <= window_end

    @staticmethod
    def is_submitted(data: dict) -> bool:
        """
        Checks the submission status from the raw API dictionary.
        """
        submission = data.get("submission") or {}
        workflow_state = submission.get("workflow_state")
        return bool(submission.get("submitted_at")) or workflow_state in {
            "submitted", "graded", "pending_review"
        }
