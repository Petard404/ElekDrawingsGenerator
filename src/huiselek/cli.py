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
    symbols = sub.add_parser(
        "symbols", help=labels.CLI_SYMBOLS_HELP, description=labels.CLI_SYMBOLS_HELP
    )
    symbols.add_argument(
        "-o", "--output", metavar="OUT", type=Path, default=Path("out/symbolen.pdf"),
        help=labels.CLI_SYMBOLS_OUTPUT_HELP,
    )
    symbols.add_argument("--svg-dir", metavar="DIR", type=Path, help=argparse.SUPPRESS)
    return parser


def _symbols(args: argparse.Namespace) -> int:
    from .export_pdf import export_pdf
    from .render_svg import render_svg
    from .settings import Settings
    from .symbol_sheet import build_sheet, svg_with_overlays

    settings = Settings()
    pages, overlays = build_sheet(settings)
    svgs = [render_svg(page, settings) for page in pages]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    export_pdf(svgs, args.output, overlays)
    if args.svg_dir:  # debug output: page SVGs with the overlays embedded as images
        args.svg_dir.mkdir(parents=True, exist_ok=True)
        for n, (svg, over) in enumerate(zip(svgs, overlays), 1):
            (args.svg_dir / f"symbolen_p{n}.svg").write_text(
                svg_with_overlays(svg, over), encoding="utf-8"
            )
    print(labels.CLI_SYMBOLS_OK.format(path=args.output, pages=len(pages)))
    return 0


def _build(args: argparse.Namespace) -> int:
    from .export_pdf import export_pdf
    from .layout import layout
    from .render_svg import render_svg
    from .settings import Settings

    installation = build_model(read(args.file))
    settings = Settings()
    pages = layout(installation, settings)
    svgs = [render_svg(page, settings) for page in pages]
    out = args.output or Path("out") / f"{args.file.stem}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    export_pdf(svgs, out)
    for n, svg in enumerate(svgs, 1):  # one SVG per page next to the PDF
        (out.parent / f"{out.stem}_p{n}.svg").write_text(svg, encoding="utf-8", newline="\n")
    print(labels.CLI_OK.format(path=out, pages=len(pages)))
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the CLI; returns the exit code (usage errors exit 2 via argparse)."""
    args = _parser().parse_args(argv)
    try:
        if args.command == "symbols":
            return _symbols(args)
        return _build(args)
    except HuiselekError as err:
        print(labels.CLI_ERROR_PREFIX + str(err), file=sys.stderr)
        return 1
    except OSError as err:
        path = getattr(err, "filename", None) or getattr(args, "output", "")
        print(labels.CLI_ERROR_PREFIX + labels.CLI_WRITE_ERROR.format(path=path), file=sys.stderr)
        return 1
    except RecursionError:
        print(labels.CLI_ERROR_PREFIX + labels.CLI_TOO_DEEP, file=sys.stderr)
        return 1
