# app.py
"""
The main application class that orchestrates the entire process.
"""
import argparse
from datetime import datetime, timezone

import config
from api_client import CanvasAPIClient
from canvas_service import CanvasService
from presenter import ConsolePresenter

class Application:
    """Orchestrates fetching and displaying Canvas data."""

    def __init__(self):
        """Initializes the application and its components."""
        self.parser = self._create_parser()
        self.api_client = CanvasAPIClient(config.CANVAS_BASE_URL, config.CANVAS_TOKEN)
        self.presenter = ConsolePresenter()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Creates and configures the command-line argument parser."""
        parser = argparse.ArgumentParser(
            description="A CLI tool to fetch upcoming Canvas assignments or list available courses."
        )
        parser.add_argument(
            "-l", "--list",
            type=str,
            choices=['courses', 'terms'],
            help="List resources. Use 'courses' for all courses, or 'terms' for all enrollment terms."
        )
        return parser

    def run(self):
        """The main entry point to run the application."""
        args = self.parser.parse_args()
        if args.list == 'courses':
            self._list_courses()
        elif args.list == 'terms':
            self._list_terms()
        else:
            self._show_assignments()

    def _list_courses(self):
        """Handles the logic for listing courses."""
        print("Fetching available courses...")
        # FIX: Use the correct keyword 'avoid_assignment_ids'
        service = CanvasService(self.api_client, course_ids=[], avoid_assignment_ids=[])
        all_courses = service.get_all_courses()
        self.presenter.display_courses(all_courses)

    def _list_terms(self):
        """Handles the logic for listing enrollment terms."""
        print("Fetching enrollment terms...")
        # FIX: Use the correct keyword 'avoid_assignment_ids'
        service = CanvasService(self.api_client, course_ids=[], avoid_assignment_ids=[])
        all_terms = service.get_enrollment_terms()
        self.presenter.display_terms(all_terms)

    def _show_assignments(self):
        """
        Handles the logic for showing assignments for the current semester.
        """
        print("Finding courses for the current semester...")
        # Pass the AVOID_COURSE_IDS from config to the service
        temp_service = CanvasService(
            self.api_client,
            course_ids=[],
            avoid_assignment_ids=config.AVOID_ASSIGNMENT_IDS,
            avoid_course_ids=config.AVOID_COURSE_IDS
        )
        current_courses = temp_service.get_current_semester_courses()

        if not current_courses:
            print("\nCould not find any active, non-excluded courses for the current semester.")
            return

        current_course_ids = [course['id'] for course in current_courses]
        course_names = ", ".join([course['name'] for course in current_courses])
        print(f"Fetching assignments for: {course_names}\n")

        # Initialize the main service with the dynamically found course IDs
        service = CanvasService(
            self.api_client,
            current_course_ids,
            # FIX: Use the correct keyword 'avoid_assignment_ids'
            avoid_assignment_ids=config.AVOID_ASSIGNMENT_IDS
        )
        all_assignments = service.get_unsubmitted_assignments()
        
        now = datetime.now(timezone.utc)

        # Classification and Sorting...
        overdue = [a for a in all_assignments if a.due_at and a.due_at < now and a.is_overdue(now, config.OVERDUE_WINDOW_DAYS)]
        upcoming = [a for a in all_assignments if not (a.due_at and a.due_at < now)]
        overdue.sort(key=lambda a: a.due_at)
        upcoming.sort(key=lambda a: (a.due_at is None, a.due_at))

        self.presenter.display_assignments(overdue, upcoming)

