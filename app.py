#!/Users/franz/Documents/GitHub/Personal/CanvasPulse/.venv/bin/python

from __future__ import annotations
import argparse
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Importing this module runs the decorators and fills COMMANDS.
from cli.commands import COMMANDS
from core.ports import ICanvasClient, IPresenter
from infra.canvas_http import CanvasHTTPClient
from cli.presenter_console import ConsolePresenter


@dataclass
class Deps:
    canvas_client: Optional[ICanvasClient] = None
    presenter: Optional[IPresenter] = None

    @staticmethod
    def build() -> Deps:
        """Build a default set of dependencies from env vars."""
        load_dotenv()
        base_url = os.getenv(key="CANVAS_BASE_URL",
                             default="https://reykjavik.instructure.com/")
        token = os.getenv(key="CANVAS_TOKEN",
                          default=None)

        canvas_client = CanvasHTTPClient(base_url, token) if token else None
        presenter = ConsolePresenter()

        return Deps(canvas_client=canvas_client, presenter=presenter)


def build_parser() -> argparse.ArgumentParser:
    """
    Builds an ArgumentParser with subcommands for each registered command.
    Each command adds its own flags via add_arguments().
    """
    parser = argparse.ArgumentParser(
        prog="canvaspulse",
        description="List upcoming and recently overdue Canvas assignments.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create one subparser per registered command
    for name, cls in COMMANDS.items():
        sp = subparsers.add_parser(name, help=(cls.__doc__ or None))
        cls.add_arguments(sp)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    deps = Deps.build()

    # Resolve and run the chosen command
    cmd_cls = COMMANDS[args.command]
    cmd = cmd_cls()

    try:
        cmd.run(args, deps)
    except NotImplementedError as e:
        # Friendly message while commands are still stubs
        print(f"Err: {e}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
