
from __future__ import annotations
from typing import Any, Dict, List, Optional, Iterable
from .ports import ICanvasClient
from .models import Course, Assignment

from datetime import datetime, timezone, timedelta

from utils.iso_parser import _parse_iso


class CourseService:
    """
    Application/use-case layer for course-related operations.
    Depends only on the ICanvasClient port.
    """

    def __init__(self, client: ICanvasClient):
        self._client = client

    def _select_current_term_id(
        self, courses_payload: Iterable[Dict[str, Any]]
    ) -> Optional[int]:
        """
        Determine the current enrollment term id by scanning the 'term' object
        attached to each course (when requested via include[]=term).

        If multiple match, chooses the one with the latest start_at.
        Falls back to most-common term id if no active window matches.
        """
        now = datetime.now(tz=timezone.utc)
        terms_by_id: Dict[int, Dict[str, Any]] = {}
        counts: Dict[int, int] = {}

        for c in courses_payload:
            term = c.get("term")
            if not isinstance(term, dict):
                continue
            tid = term.get("id")
            if tid is None:
                continue

            # Keep a canonical copy and count usage
            if tid not in terms_by_id:
                terms_by_id[tid] = term
            counts[tid] = counts.get(tid, 0) + 1

        # 1) Prefer terms where now is within [start_at, end_at]
        active: List[Dict[str, Any]] = []
        for term in terms_by_id.values():
            start = _parse_iso(term.get("start_at"))
            end = _parse_iso(term.get("end_at"))
            if start and ((end and start <= now <= end)
                          or (not end and start <= now)):
                active.append(term)

        if active:
            # Choose the one with the latest start_at
            def start_key(t: Dict[str, Any]) -> datetime:
                return _parse_iso(t.get("start_at")) or now

            best = max(active, key=start_key)
            best_id = best.get("id")
            return int(best_id) if best_id is not None else None

        # 2) Fallback: pick the most common term id across courses
        if counts:
            most_common_id = max(counts, key=counts.get)
            return int(most_common_id)

        return None

    def list_courses(self, include_archived: bool) -> List[Course]:
        """
        Returns current-term courses by default.
        If include_archived=True, returns all courses.
        """
        params: Dict[str, Any] = {
            "per_page": 100,
            "state[]": "available",
            "include[]": "term",
        }

        # Materialize once; reuse for term detection and model mapping.
        raw = self._client.get_paginated("/api/v1/courses", params=params)
        courses = [Course.from_api(c) for c in raw if isinstance(c, dict)]

        # Skip filtering courses by term if desired
        if include_archived:
            return courses

        current_term_id = self._select_current_term_id(raw)
        if current_term_id is None:
            # Could not determine a current term, return everything rather
            return courses

        return [c for c in courses if c.enrollment_term_id == current_term_id if isinstance(c, Course)]

    def get_assignments(self) -> List[Assignment]:
        """Fetch all assignments for current-term courses, excluding submitted ones."""
        assignments: List[Assignment] = []

        curr_courses: List[Course] = self.list_courses(include_archived=False)
        for course in curr_courses:
            course_id = course.id
            course_name = course.name  # we already have it

            assignment_path = f"/api/v1/courses/{course_id}/assignments"
            assignment_params = {"include[]": ["submission"], "per_page": 100}

            try:
                pages = self._client.get_paginated(
                    assignment_path, params=assignment_params
                )
            except Exception as e:
                print(
                    f"Warning: Failed to fetch assignments for course "
                    f"{course_id} ({course_name}): {e}"
                )
                continue

            for data in pages:
                assignment: Assignment = Assignment.from_api_dict(data, course_name)
                assignments.append(assignment)

        return assignments

    def get_unsubmitted_assignments(self, window_days: int) -> List[Assignment]:
        """
        Fetches all most recent unsubmitted assignments
        """
        all_assignments: List[Assignment] = self.get_assignments()
        unsubmitted: List[Assignment] = []

        now = datetime.now(timezone.utc)
        for assignment in all_assignments:
            if not assignment.due_at:
                continue

            window_end = assignment.due_at + timedelta(days=window_days)

            # If assignment has been submitted or passed window, then skip
            if assignment.is_submitted() or now > window_end:
                continue

            unsubmitted.append(assignment)

        return unsubmitted
