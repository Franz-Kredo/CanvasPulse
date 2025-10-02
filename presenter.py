# presenter.py
"""
Handles the presentation of assignments to the console.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from models import Assignment
from config import Colors, OVERDUE_WINDOW_DAYS

class ConsolePresenter:
    """Formats and prints assignment lists to the console."""

    def display_assignments(self, overdue: List[Assignment], upcoming: List[Assignment]):
        """The main display method."""
        print("\n")
        self._display_overdue_section(overdue)
        self._display_upcoming_section(upcoming)
        print("\n")

    def _display_overdue_section(self, assignments: List[Assignment]):
        """Prints the overdue assignments section."""
        print("=== Overdue (unsubmitted: last 7 days) ===")
        if not assignments:
            print(f"{Colors.GREY}None in the last {OVERDUE_WINDOW_DAYS} days.{Colors.RESET}\n")
            return
        
        now = datetime.now(timezone.utc)
        for a in assignments:
            lateness_str = self._human_lateness(now, a.due_at)
            suffix = f"{Colors.RED}({lateness_str}){Colors.RESET}"
            self._print_assignment_details(a, extra_suffix=suffix)

    def _display_upcoming_section(self, assignments: List[Assignment]):
        """Prints the upcoming assignments section."""
        print("=== Upcoming Assignments ===")
        if not assignments:
            print(f"{Colors.GREY}No upcoming assignments found.{Colors.RESET}\n")
            return
            
        for a in assignments:
            self._print_assignment_details(a)

    def _print_assignment_details(self, a: Assignment, extra_suffix: str = ""):
        """Prints the details for a single assignment."""
        due_fmt = self._color_due_date(a.due_at)
        id_col = f"{Colors.BLUE}{a.id}{Colors.RESET}"
        title_col = a.title
        course_col = f"{Colors.ORANGE}[{a.course_name}]{Colors.RESET}"
        points_str = a.points if a.points is not None else "N/A"

        print(f"- [{id_col}] {title_col} {course_col} {extra_suffix}".rstrip())
        print(f"    due: {due_fmt} | points: {points_str} | published: {a.published}")
        print(f"    link: {a.url}\n") # Added newline for spacing

    def _color_due_date(self, due: Optional[datetime]) -> str:
        """Returns a color-coded string for the due date."""
        if due is None:
            return f"{Colors.GREY}—{Colors.RESET}"

        now = datetime.now(timezone.utc)
        delta = due - now

        if delta.total_seconds() <= 0:
            color = Colors.RED
        elif delta <= timedelta(days=2):
            color = Colors.RED
        elif delta <= timedelta(days=7):
            color = Colors.YELLOW
        else:
            color = Colors.GREEN

        return f"{color}{due.strftime('%Y-%m-%d %H:%M')}{Colors.RESET}"
    
    def _human_lateness(self, now: datetime, due: datetime) -> str:
        """Returns a short 'X d Y h late' string."""
        if not due or now < due:
            return ""
        late = now - due
        days, remainder = divmod(late.total_seconds(), 86400)
        hours, _ = divmod(remainder, 3600)
        days, hours = int(days), int(hours)
        
        if days > 0:
            return f"{days}d {hours}h late" if hours > 0 else f"{days}d late"
        if hours > 0:
            return f"{hours}h late"
        
        minutes = int((late.seconds % 3600) // 60)
        return f"{minutes}m late"