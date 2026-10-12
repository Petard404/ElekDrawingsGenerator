"""Command-line entry point: `python -m huiselek build FILE -o OUT`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import labels
from .errors import HuiselekError
from .model import build_model
from .reader import read


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="huiselek", description=labels.CLI_DESCRIPTION)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help=labels.CLI_BUILD_HELP, description=labels.CLI_BUILD_HELP)
    build.add_argument("file", metavar="FILE", type=Path, help=labels.CLI_FILE_HELP)
    build.add_argument("-o", "--output", metavar="OUT", type=Path, help=labels.CLI_OUTPUT_HELP)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI; returns the exit code (usage errors exit 2 via argparse)."""
    args = _parser().parse_args(argv)
    try:
        installation = build_model(read(args.file))
    except HuiselekError as err:
        print(labels.CLI_ERROR_PREFIX + str(err), file=sys.stderr)
        return 1
    except RecursionError:
        print(labels.CLI_ERROR_PREFIX + labels.CLI_TOO_DEEP, file=sys.stderr)
        return 1
    print(
        labels.CLI_OK.format(
            file=args.file,
            elements=sum(1 for _ in installation.nodes()),
            pages=len(installation.pages),
        )
    )
    return 0
