

from abc import ABC, abstractmethod
from typing import Iterable, Any, Optional
from .models import Assignment


class ICanvasClient(ABC):
    """For fetching Canvas data."""

    @abstractmethod
    def get_paginated(self,
                      path: str,
                      params: Optional[dict] = None) -> Iterable[Any]:
        """Yield items from a paginated API endpoint."""
        pass


class IPresenter(ABC):
    """Abstract interface for presenting output (like for console or JSON)."""

    @abstractmethod
    def display_courses(self, courses: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def display_terms(self, terms: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def display_assignments(self,
                            overdue: list[Assignment],
                            upcoming: list[Assignment]) -> None:
        raise NotImplementedError
