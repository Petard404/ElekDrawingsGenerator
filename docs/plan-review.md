# Plan review

11 October 2026 · planning session.

> **History only.** Everything below was merged into `docs/handoff-plan.md` version 2 on 12 October 2026. Read the plan and `docs/decisions.md`, not this file.

The inventory in the plan was checked against the text that is visible on the four reference pages: circuits, ratings, cables, device IDs, counts and the listed slips all match. Measured positions also match: first device x 97.5, device pitch 7.6, cable text x 78, circuit text x 161, detail names x 141 at pitch 15.4.

## Fix before or in M1

1. **Reference SVGs hold mostly off-page content.** Single layer, nothing hidden, but most elements sit outside the 210 x 297 viewBox: PLC blocks (`IX.0 … Input 0.x`), an older version (B1–B9, "Diff A1/A2", "K6 Tuin", "Check situatieschets zolder") and copies of other pages. Visible texts: pg1 78 of 237, pg2 67 of 205, pg3 17 of 142, pg4 15 of 137. Task 2.2 and task 5.2 must apply transforms and keep only elements inside x 0..210, y 0..297.
2. **Python 3.11 is not installed; only 3.14 is.** Use `py -3 -m venv .venv` with `requires-python = ">=3.11"`. Task 1.1 confirms that pydantic-core and lxml (pulled in by svglib) install from wheels on 3.14 under Windows.
3. **Task 1.1 check:** `pytest -q` with no tests exits with code 5. Add one smoke test that imports the package.

## Plan vs original (tasks 1.3, 2.2, 3.1)

4. **Link texts vary:** "Naar Pg 2 Ref Diff 2", "Van pg 1", "Naar Pg 3", "Van Pagina 2 verlichting gelijkvloers". Either links get an optional reference text, or the differences go on the 5.2 allow-list. Decide in 1.3.
5. **Row height is not constant.** Page 2 rows sit at y 57, 72, 88, 104, 118, 134, then 165 and 180. On page 1 the 32 A breaker with its vertical 5x6 cable takes two rows (K at y 88, N at y 134), not one. Devices that hang lower (K7/K8, H1, F1/F2) take extra height. Task 3.1: row height is the larger of the pitch and the content; the layout test "rows sit at the row pitch" is too strict.
6. **Page 1 supply chain has no measurements** in the Layout table: supply, 40 A, 300 mA, Diff 1 text. Add them to the task 2.2 scope.
7. **Detail pages have a circuit letter header** ("A" or "G" at x 141, y 52). It is not in the plan.
8. **Task 5.1 "20 lighting points"** means detail rows A1–A11 and G1–G9. With K6, K7, K8, C4 and H1 the total is 25. Make the check state which count it means.

## Smaller points

- Golden SVGs: fix number formatting (for example two decimals) and element order in `render_svg`, or byte-identical output will not hold.
- PDF route: the direct ReportLab renderer (the plan's fallback) is about as small as the SVG route and drops svglib and lxml. The owner keeps SVG to PDF unless task 1.2 fails.

## House B needs (input for task 1.3)

The final test is `docs/testcase/house-b-overzicht-v4.md`, with the provisional values in `docs/decisions.md`. Field names fixed in 1.3 must cover:

| Need | Plan v1 |
| --- | --- |
| `poles` and `curve` on circuits (A, G, J are 3P+N; A is curve C) | Circuit has neither |
| Differential `type` (A, B, S) | Missing |
| Sub-board BRD-TUIN fed by circuit J, with its own differential and circuits T1–T3 | Only a nested breaker; no board kind or label |
| Circuits A and J directly behind the 300 mA with no 30 mA | Allowed by the model; no layout rule yet |
| Reserve circuits Y and T3 (breaker without devices, or empty place) | Missing |
| Appliances with a mandatory AREI symbol: oven, dishwasher, washing machine, dryer, CV boiler, water heater (W.W.), IR panel | One device kind and symbol each; symbol shapes from AREI references (to supply) |
| Fixed connection box (kookplaat), wallbox | Own kinds; symbols from AREI references |
| Hood, fridge, combi microwave | Plain sockets (assumption, see decisions) |
| Sockets with 2, 3 or 4 mechanisms (counts as 1 box) | `socket.count` covers it |
| V's sockets switched through a teleruptor | No symbol |
| Title block with version (v4) and date | Missing |
| Cable notation "3G2,5 mm²", "XVB 5G6 mm²" | `cable` is free text, fine |

Lighting circuits 1–35 use numbers, not letters, and are switched through a controller. They come in M8 and do not need fields in 1.3.

## Symbols from the AREI library (replaces the plan's Symbols section where they differ)

The owner supplied the ShadowHunter AREI library, now in `docs/reference/arei/` (see its README). It changes M2:

- **New task 2.0 (Sonnet):** a script in `tools/` that converts named masters from the 2023 `.vssx` stencils to SVG (Visio geometry: MoveTo, LineTo, ArcTo, EllipticalArcTo, Ellipse; text). Output in `docs/reference/arei/svg-2023/`. Check: each converted symbol is rendered and compared by eye with its name; arcs and text are the risk.
- **Task 2.2** measures each symbol from the library (single-line variant), not from the House A pages. House A's pages are still used for sizes in the layout and for the House A comparison.
- **Task 2.3** builds each symbol as primitives from its notes entry, as planned.
- **Symbol set** grows from 13 to the House A set plus House B needs: Differentieel 2023, breaker, fuse, kWh meter, socket with protective conductor (n-count), outdoor waterproof socket, conductors-in-cable marks, oven, dishwasher, washing machine, dryer, kookfornuis, boiler, Verwarmingstoestel (IR panel and CV boiler), laadinrichting, impulsschakelaar, schakel- en verdeelbord, aftakdoos, earthing (aardingsonderbreker, aardingsstrip, aardinrichting) if earthing is in M7. M8 adds drukknop, bewegingssensor, domotica sturingseenheid, motor (rolluik).
- House A symbols with no library match (square-with-triangle, converter, transformer as drawn) stay as measured from the House A pages.

## Software review (amends Code architecture, Symbols and tasks 2.0–2.3)

1. **Symbols are generated, not hand-coded.** One converter in `tools/` turns library SVG (and the SVG converted from the 2023 `.vssx`) into primitives in mm and writes one data file per symbol, committed to the repo. A small hand-written table per symbol gives anchor, connection points and size. `symbols.py` loads the data files. Only House A's own symbols (square-with-triangle, converter as drawn) are hand-made. Tasks 2.0, 2.2 and 2.3 become: converter (Sonnet), metadata table (Haiku), the few hand-made symbols (Haiku).
2. **Primitives carry style.** Line, Polyline (open or closed), Arc, Circle, Rect and Text, each with stroke width, fill and dash; Text with anchor, rotation and size. Bézier curves are flattened to polylines by the converter. `Page` lives in `primitives.py` so the one-direction import rule holds. Fixed in task 2.1.
3. **Text widths from ReportLab's Helvetica metrics** (`stringWidth`), in the layout and in the overlap and overflow checks. SVG and PDF both use Helvetica.
4. **Model (tasks 1.3, 1.4):**
   - One `appliance` kind with a `type` field (oven, dishwasher, washing_machine, dryer, stove, water_heater, heating_device), not seven kinds.
   - Differential `type` (AC, A, F, B) and `selective` (bool) as separate fields.
   - Socket `variant`: default "protective conductor with child protection"; other values: protective conductor only, waterproof.
   - `board` is allowed as a child of a circuit (J feeds BRD-TUIN).
   - IDs are converted to strings (YAML reads `20` as a number; M8 circuits are numbered).
   - Pydantic reports error locations as list indexes; task 1.4 maps them back to the element ID. `HuiselekError` allows no ID for file and syntax errors.
   - Error messages are Dutch and live in `labels.py` with the drawing texts. Tests assert on the element ID and error code, not on the message text.
5. **Export:** all pages drawn into one ReportLab canvas with `showPage()`; no merge step. pypdf becomes a test-only dependency.
6. **Pin dependency versions** in `pyproject.toml` so a library update cannot change golden files.
7. **Golden files:** a separate command writes candidate files to `out/` for approval; tests never write golden files. Specified in task 2.1.
8. **Label formats are templates.** House A and House B write the same values differently ("20A" vs "C20", "300 mA 4x40 A" vs "40/0.3A type A", "XVB 3x2.5" vs "XVB Cca 3G2.5²"). Format strings live in `labels.py`, and a project can override them from its YAML or a settings file. No label format is hard-coded in layout or symbols.
9. **Installation marks** (conduit, in or on a wall) are out of version 1.
10. **Batch small tasks** about five per brief (symbol metadata, broken test files) to save main-session tokens.

## Validating the symbol library

The converter proves only that our symbol matches the library file, not that the library matches AREI. Four checks:

1. **Against the official text.** The symbol sheet (task 2.4) shows three columns per symbol: the official AREI image, the library source, our generated symbol. The official images come from the AREI Book 1 text (FOD Economie) or the Volta annex listed in the background sources; to be obtained.
2. **Old set against the 2023 set.** A script lists symbols that differ between `svg-en/` and `visio-2023-nl/`. Each difference is a symbol the 2023 amendment may have changed, and is checked first against the official text.
3. **Conversion check.** Each converted 2023 shape is rendered next to its source geometry; arcs and text are the risk.
4. **Practice check.** Before the House B dossier is used, an installer or inspection body reviews the approved symbol sheet (scope requirement C4/C5).

## Slips in the overview v4

- Letter O is not used, but the overview says only H, I and Z are unused.
- "3N400V + N" names the neutral twice.
- G (wallbox) counts as 1 socket in the 74.
- If A becomes a 3N400V socket behind D1, D1 has to be 4-pole; poles of D1–D4 are not given.

## Milestones added

Order: M1–M5, then M7, then M6 (hardening, guide and final tests cover House B), then M8.

| Milestone | Done when |
| --- | --- |
| M7 House B power | Main board and BRD-TUIN with all circuits A–Y and T1–T3, DIFF-ALG, D1–D5 and DIFF-TUIN. A script checks that every circuit, device and value in the overview (with the provisional values) appears on the PDF |
| M8 House B lighting and control | Lighting circuits 1–35 and controller inputs drawn. Needs the source xlsx and a decision on how the controller is drawn. Expected total: 70 lighting points |

## Parked data questions (for typing the House B YAML in M7; they do not change the software)

- Which House B circuits are XVB besides J; all others are VOB in conduit.
- VOB label text: official "H07V-U Eca 2.5²" or "VOB 3x2.5".
- The two assumptions in `docs/decisions.md`: DIFF-TUIN 4-pole, D1–D5 40 A.

## Open questions for the owner

- House B values are now in `docs/decisions.md`. Two assumptions to confirm by M7: DIFF-TUIN 4-pole, D1–D5 40 A.
- Earthing is not drawn in M7; the owner checks the earthing design separately.

- Off-page leftovers name the K lights "K6 Tuin, K7 Werkplaats, K8 Wc". Use those names on House A?
- Earlier plan questions still stand: confirm that pages never flow automatically (before M1); the slips in the original (before M5); the square-with-triangle symbol and the grey cable marks.
