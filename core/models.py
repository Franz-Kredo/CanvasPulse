from dataclasses import dataclass
from typing import Optional


class Assignment:
    pass


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
