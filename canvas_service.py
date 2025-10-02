# canvas_service.py
"""
Service layer to fetch and process Canvas data.
This orchestrates API calls and data transformation.
"""
from typing import List
from api_client import CanvasAPIClient
from models import Assignment

class CanvasService:
    """Fetches and filters courses and assignments."""

    def __init__(self, client: CanvasAPIClient, course_ids: List[int], avoid_ids: List[int]):
        self.client = client
        self.course_ids = set(course_ids)
        self.avoid_ids = set(avoid_ids)

    def get_unsubmitted_assignments(self) -> List[Assignment]:
        """
        Fetches all unsubmitted assignments from the specified courses.
        
        Returns:
            A list of Assignment objects.
        """
        assignments = []
        courses = self.client.get_paginated("/api/v1/courses", params={"state[]": "available"})
        
        for course_data in courses:
            course_id = course_data.get("id")
            if course_id not in self.course_ids:
                continue

            course_name = course_data.get("name", f"Course {course_id}")
            assignment_path = f"/api/v1/courses/{course_id}/assignments"
            assignment_params = {"include[]": ["submission"]}

            for assign_data in self.client.get_paginated(assignment_path, params=assignment_params):
                if (assign_data.get("id") in self.avoid_ids or
                    Assignment.is_submitted(assign_data)):
                    continue
                
                assignments.append(Assignment.from_api_dict(assign_data, course_name))
        
        return assignments