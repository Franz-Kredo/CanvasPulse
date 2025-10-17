# cli/commands.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Dict, Type, Any

# For type annotations
from argparse import ArgumentParser

# --- Registry ---

COMMANDS: Dict[str, Type["ICommand"]] = {}


def register(name: str) -> Callable[[Type["ICommand"]], Type["ICommand"]]:
    """Decorator to register a command class by name."""
    def _wrap(cls: Type["ICommand"]) -> Type["ICommand"]:
        COMMANDS[name] = cls
        cls.command_name = name
        return cls
    return _wrap


# --- Interface ---
class ICommand(ABC):
    """Each command defines its own args and how to run."""

    @staticmethod
    @abstractmethod
    def add_arguments(p) -> None:
        """Add argparse options to this command's subparser."""
        pass

    @abstractmethod
    def run(self, args, deps: Any) -> None:
        """Execute the command with parsed args and injected deps."""
        pass


# --- Example commands (placeholders that raise for now) ---

@register("list-courses")
class ListCourses(ICommand):
    @staticmethod
    def add_arguments(p: ArgumentParser) -> None:
        # You can add flags here without touching app.py later
        p.add_argument("--include-archived",
                       action="store_true",
                       help="Include archived/ended courses")

    def run(self, args, deps) -> None:
        raise NotImplementedError("ListCourses.run: Not Implemented")


@register("list-terms")
class ListTerms(ICommand):
    @staticmethod
    def add_arguments(p: ArgumentParser) -> None:
        pass

    def run(self, args, deps) -> None:
        raise NotImplementedError("ListTerms.run: Not Implemented")


@register("show-assignments")
class ShowAssignments(ICommand):
    @staticmethod
    def add_arguments(p: ArgumentParser) -> None:
        p.add_argument("--window-days",
                       type=int,
                       default=7,
                       help="Show overdue items up to N days late")
        p.add_argument("--course-id",
                       type=int,
                       action="append",
                       help="Restrict to specific course id(s); repeatable")

    def run(self, args, deps) -> None:
        raise NotImplementedError("ShowAssignments.run: Not Implemented")
