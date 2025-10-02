# main.py
"""
Main entrypoint for the Canvas Assignment Fetcher.
Initializes and wires together the components to fetch and display assignments.
"""
from datetime import datetime, timezone
import config
from api_client import CanvasAPIClient
from canvas_service import CanvasService
from presenter import ConsolePresenter

def main():
    """Main execution function."""
    # 1. Initialization
    api_client = CanvasAPIClient(config.CANVAS_BASE_URL, config.CANVAS_TOKEN)
    service = CanvasService(api_client, config.COURSE_IDS, config.AVOID_ASSIGNMENT_IDS)
    presenter = ConsolePresenter()

    # 2. Data Fetching and Processing
    print("Fetching assignments from Canvas...")
    all_assignments = service.get_unsubmitted_assignments()
    now = datetime.now(timezone.utc)

    # 3. Classification
    overdue = []
    upcoming = []
    for assign in all_assignments:
        if assign.due_at and assign.due_at < now:
            if assign.is_overdue(now, config.OVERDUE_WINDOW_DAYS):
                overdue.append(assign)
        else:
            # Includes assignments with future due dates and those with no due date
            upcoming.append(assign)

    # 4. Sorting
    # Sort overdue by due date (earliest first)
    overdue.sort(key=lambda a: a.due_at)
    # Sort upcoming with "no due date" last, then by earliest due date
    upcoming.sort(key=lambda a: (a.due_at is None, a.due_at))

    # 5. Presentation
    presenter.display_assignments(overdue, upcoming)

if __name__ == "__main__":
    main()