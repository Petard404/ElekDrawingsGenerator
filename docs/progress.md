# Progress

## 2026-10-12 · M2 Symbols done (sheet approved)

- 2.1 `primitives.py` (styled primitives, Page, Overlay), `render_svg.py` (fixed number format and order), golden `tests/golden/primitives_page.svg` (candidates via `tests/make_golden.py` to `out/golden/`). `.gitattributes` keeps golden and symbol data byte-stable.
- 2.2 `tools/vssx_to_svg.py`: 41 masters from the 2023 Visio stencils to `docs/reference/arei/svg-2023/`. `tools/extract_official.py`: 115 table 2.23 images to `official/images/` with `index.csv`.
- 2.3 `tools/svg_to_symbol.py` + `src/huiselek/symbol_table.yaml` → `symbol_data/*.json`; rules rotate, mirror, keep_text, drop, text_at (official image wins). Deterministic.
- 2.4/2.5 points and anchors per symbol; `symbols.py` with `load_symbols`, `Symbol.place/point`; code-drawn `page_link` and `photo_detector` measured from House A.
- 2.6 `python -m huiselek symbols -o out/symbolen.pdf`: 7-page three-column sheet; `export_pdf.py` with overlays.
- Sheet review: names in AREI wording; new `socket_waterproof` (protective conductor + child protection + h) for `variant: waterproof`, plain one as `waterproof_plain`; 1~/3~ in the official arc shape; impulse relay marks moved up. 42 symbols, 810 tests pass. Fresh-agent review done; decisions logged.
- Notes for M3: symbol sizes are at library scale (tune with `scale`); House A page 1 bus measured at x 34.57, not 63.5 as in the Layout table; model→symbol mapping (socket variant, appliance type incl. `general`) is still to write; child-protection feet are 0.2 × radius against about 0.3 in the official image; the impulse relay box is taller than the official one (2.3:1 against 4.4:1).

**Next step:** M3 One page, starting with task 3.1 (layout design note). Read CLAUDE.md, the plan's Layout and M3 rows, and the decision log entries of 12 October.

## 2026-10-12 · M1 Skeleton done

- Package skeleton in `src/huiselek/`, pinned dependencies, started with `python -m huiselek` (the `huiselek.exe` launcher is blocked by Windows Application Control on this PC).
- PDF route proven: svglib onto one ReportLab canvas, two A4 pages, selectable text (`tests/test_pdf_route.py`, `out/pdf_route_trial.pdf`).
- Input format fixed (task 1.3, plan section Input format): kinds incl. `photo_detector`, poles as text (1P … 4P), differential `type` required, 12 error codes, label template names.
- `model.py` validates every kind and rule; `reader.py` adds YAML syntax and duplicate-key errors; `cli.py build` stops after validation with one Dutch line. `examples/minimal.yaml` builds.
- 287 tests pass. Review by a fresh agent done; fixes applied; decisions logged.
- Supply `voltage` is typed: `230V`, `3x230V`, `3N400V`.
- Known gaps, deliberately left: IDs typed as numbers lose leading zeros (`01` becomes "1"), to be documented in the user guide; `labels` values are not yet checked as templates (M3); `conductors` and `cable` can contradict (no intelligence in version 1); argparse's own words are English.

**Next step:** M2 Symbols, starting with task 2.1 (primitives with styles, `render_svg.py`, golden candidate command). Read CLAUDE.md, the plan's Symbols, Code architecture and M2 rows, and the decision log entries of 12 October.
