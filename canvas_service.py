# canvas_service.py
"""
Service layer to fetch and process Canvas data.
This orchestrates API calls and data transformation.
"""
from typing import List, Dict
from datetime import datetime, timezone
from api_client import CanvasAPIClient
from models import Assignment, parse_due_date

class CanvasService:
    """Fetches and filters courses and assignments."""

    def __init__(self, client: CanvasAPIClient, course_ids: List[int], avoid_assignment_ids: List[int], avoid_course_ids: List[int] = None):
        self.client = client
        self.course_ids = set(course_ids)
        # Consistently use the full name for clarity
        self.avoid_assignment_ids = set(avoid_assignment_ids)
        self.avoid_course_ids = set(avoid_course_ids) if avoid_course_ids is not None else set()

    def get_all_courses(self) -> List[Dict[str, any]]:
        """
        Fetches all available courses for the user, including term data.
        """
        params = {"state[]": "available", "include[]": "term"}
        courses_data = self.client.get_paginated("/api/v1/courses", params=params)
        courses = [course for course in courses_data if course.get("id") and course.get("name")]
        courses.sort(key=lambda course: course['name'])
        return courses

    def get_enrollment_terms(self) -> List[Dict[str, any]]:
        """
        Fetches all unique enrollment terms by extracting them from the user's courses.
        """
        all_courses = self.get_all_courses()
        unique_terms = {term["id"]: term for course in all_courses if (term := course.get("term")) and term.get("id")}
        return list(unique_terms.values())

    def get_current_semester_courses(self) -> List[Dict[str, any]]:
        """
        Identifies the current enrollment term and returns all courses from that term,
        excluding any specified in `self.avoid_course_ids`.
        """
        all_courses = self.get_all_courses()
        all_terms = self.get_enrollment_terms()
        now = datetime.now(timezone.utc)
        current_term_id = None

        for term in all_terms:
            start_date = parse_due_date(term.get("start_at"))
            end_date = parse_due_date(term.get("end_at"))
            if start_date and start_date <= now and (not end_date or now <= end_date):
                current_term_id = term.get("id")
                break
        
        if not current_term_id:
            return []

        # Filter courses by term ID and check against the avoid list
        return [
            course for course in all_courses
            if course.get("enrollment_term_id") == current_term_id
            and course.get("id") not in self.avoid_course_ids
        ]

    def get_unsubmitted_assignments(self) -> List[Assignment]:
        """
        Fetches all unsubmitted assignments from the courses specified in `self.course_ids`.
        """
        assignments = []
        for course_id in self.course_ids:
            try:
                course_data = next(self.client.get_paginated(f"/api/v1/courses/{course_id}"))
                course_name = course_data.get("name", f"Course {course_id}")
            except (StopIteration, Exception):
                print(f"Warning: Could not fetch details for course ID {course_id}. Skipping.")
                continue

            assignment_path = f"/api/v1/courses/{course_id}/assignments"
            assignment_params = {"include[]": ["submission"]}
            for assign_data in self.client.get_paginated(assignment_path, params=assignment_params):
                # Use the consistent parameter name here
                if (assign_data.get("id") in self.avoid_assignment_ids or Assignment.is_submitted(assign_data)):
                    continue
                assignments.append(Assignment.from_api_dict(assign_data, course_name))
        return assignments

