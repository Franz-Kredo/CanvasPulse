# models.py
"""
Data models for representing Canvas entities like Assignments.
"""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional

def parse_due_date(dt_str: Optional[str]) -> Optional[datetime]:
    """Parses an ISO 8601 date string from Canvas into a timezone-aware datetime."""
    if not dt_str:
        return None
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


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
    def from_api_dict(cls, data: dict, course_name: str) -> "Assignment":
        """Factory method to create an Assignment from a raw API dictionary."""
        return cls(
            id=data.get("id"),
            title=data.get("name", "Untitled"),
            course_name=course_name,
            url=data.get("html_url"),
            points=data.get("points_possible"),
            published=data.get("published", False),
            due_at=parse_due_date(data.get("due_at")),
        )

    def is_overdue(self, now: datetime, window_days: int) -> bool:
        """
        Checks if the assignment is overdue but still within the display window.
        An assignment is overdue if its due date has passed but not by more than
        the specified window.
        """
        if self.due_at is None or self.due_at > now:
            return False
        
        window_end = self.due_at + timedelta(days=window_days)
        return now <= window_end

    @staticmethod
    def is_submitted(data: dict) -> bool:
        """
        Checks the submission status from the raw API dictionary.
        This is a static method because submission status isn't a core
        property of the assignment itself, but rather of the user's interaction.
        """
        submission = data.get("submission") or {}
        workflow_state = submission.get("workflow_state")
        return bool(submission.get("submitted_at")) or workflow_state in {
            "submitted", "graded", "pending_review"
        }