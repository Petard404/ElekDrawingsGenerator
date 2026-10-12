# Progress

## 2026-10-12 · M4 Multi-page done (approved)

- 4.0 `docs/layout-notes.md` section 3: House A pages 2 to 4 measured once by script (do not reread the reference SVGs); section 4: approved design for pages 2 to 4; 4.7: checks added after review.
- 4.1 `layout.py`: one root per page; moved differential drawn as a head level on its page; Naar end (feeder end at content limit − 16.8, or a circuit line ending in an arrow for `children_page`); Van end on the target page; `Page.links` for clickable links; page number "Pagina n van m" in the page-title cell; templates `link_to`, `link_from`, `page_number`, `detail_row`.
- 4.2 detail rows: bus x 71.48, code-drawn `switch_contact` (only with `switch: true`), plain light at + 47.87, text "ID name" at x 141.30, header letter.
- 4.3 `export_pdf`: clickable links (bookmarkPage + linkRect), title/author/creator. `examples/house-a-multipage.yaml`: House A pages 1 to 4 without circuit F; corrections listed in its header (B1 for J1, differentials DF0..DF2, page titles).
- 4.4 docstrings; README usage and pages section, commands run as written.
- Review by a fresh agent: one-sided links in untested tree positions now stop with `layout_unsupported` (variant `link`); `children_page` on the own page is an error; detail text is a template. 959 tests pass.
- Owner review additions: optional `mounting` (`in_wall`, `on_wall`, `in_conduit`, `in_conduit_in_wall`) on circuits and breakers draws the AREI installation mark on the cable (scale 0.83, marks +14.3..+23.8; House A's grey marks are `in_wall`, set on every circuit and the 32 A breaker); the page number has its own 32 mm cell at the right of the title block. 984 tests pass.
- Golden files approved by the owner and copied to `tests/golden/`; 990 tests pass.
- Open:
  - texts are not checked against the narrower title cells; "Pagina 10 van 12" would not fit the 32 mm cell (task 6.1, word widths)
  - `on_wall`, `in_conduit`, `in_conduit_in_wall` are tested by geometry, not yet seen in a render
  - Naar ends in other tree positions (under the supply, nested breakers, group members) are `layout_unsupported`
  - circuit F (transformer, converter) waits for M5
  - the M4 example differs from the coming `house-a.yaml` of task 5.1 only by circuit F; 5.1 can start from it

**Next step:** M5, starting with task 5.1 (House A YAML with the correction list), building on `examples/house-a-multipage.yaml`. Read CLAUDE.md, the M5 rows of the plan, `docs/layout-notes.md` and the decision log entries of 12 October.

## 2026-10-12 · M3 One page done (page 1 approved)

- 3.1 `docs/layout-notes.md`: page 1 measured once (do not reread the reference SVG) plus the approved layout design. Rows sit on a fixed 15.35 grid; an overlapping row moves down by whole pitches.
- 3.2–3.5 `layout.py`:
  - head chain (it stops at the first differential), group feeder, buses
  - circuit rows, nested breakers (recursive, last on their bus), branching circuits
  - frame and title block (grows upward), errors `layout_unsupported`, `too_many_devices`, `page_full`, `invalid_template`
- Other modules: `settings.py` holds every value; `labels.py` has the official default templates and House A overrides in its YAML; `scale` per symbol (sockets 0.85, lights 0.8, conductors 0.5); `bbox()` in `primitives.py`.
- `python -m huiselek build examples/house-a-pg1.yaml -o out/house-a-pg1.pdf` writes the PDF and one SVG per page. Golden files `layout_rows`, `layout_nested`, `house_a_pg1` approved; 911 tests pass.
- Review by a fresh agent: template crash and two misleading variants fixed; deviations from the notes put into the notes and the log.
- Open:
  - words wider than their column are not checked (task 6.1)
  - "3ph" touches socket O1
  - the M2 symbol sheet now shows scaled symbols
  - the planning session has not verified M3
- The owner welcomes visual design proposals (decision log); collect them for after M5.

**Next step:** M4 Multi-page, starting with task 4.1 (page assignment from `page` and `children_page`, link arrows with optional reference text, the Diff 2 feeder end on page 1). Read CLAUDE.md, the M4 rows of the plan, `docs/layout-notes.md` and the decision log entries of 12 October.

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
