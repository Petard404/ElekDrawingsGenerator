# Progress

## 2026-10-12 · M1 Skeleton done

- Package skeleton in `src/huiselek/`, pinned dependencies, started with `python -m huiselek` (the `huiselek.exe` launcher is blocked by Windows Application Control on this PC).
- PDF route proven: svglib onto one ReportLab canvas, two A4 pages, selectable text (`tests/test_pdf_route.py`, `out/pdf_route_trial.pdf`).
- Input format fixed (task 1.3, plan section Input format): kinds incl. `photo_detector`, poles as text (1P … 4P), differential `type` required, 12 error codes, label template names.
- `model.py` validates every kind and rule; `reader.py` adds YAML syntax and duplicate-key errors; `cli.py build` stops after validation with one Dutch line. `examples/minimal.yaml` builds.
- 287 tests pass. Review by a fresh agent done; fixes applied; decisions logged.
- Supply `voltage` is typed: `230V`, `3x230V`, `3N400V`.
- Known gaps, deliberately left: IDs typed as numbers lose leading zeros (`01` becomes "1"), to be documented in the user guide; `labels` values are not yet checked as templates (M3); `conductors` and `cable` can contradict (no intelligence in version 1); argparse's own words are English.

**Next step:** M2 Symbols, starting with task 2.1 (primitives with styles, `render_svg.py`, golden candidate command). Read CLAUDE.md, the plan's Symbols, Code architecture and M2 rows, and the decision log entries of 12 October.
