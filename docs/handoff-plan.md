# Huis Elek – Single-line generator: handoff plan

Version 2 · 12 October 2026 · Owner

> Version 2 merges the plan review of 11 October (`docs/plan-review.md`, now history only) and the decisions in `docs/decisions.md`. This file is the single source for what we build; the decision log records why.

Version 1 is a Python command-line tool that reads one YAML file describing a household installation and writes an AREI single-line diagram (eendraadschema) as a multi-page A4 portrait PDF. The user types the full structure, including the pages; the tool only draws it. Two test cases drive the work: House A, an existing four-page diagram that is redrawn and compared (M2 to M5), and House B, a new design that is the final acceptance test (M7 and M8).

## Decisions

| Topic | Decision | Note |
| --- | --- | --- |
| Language | Python 3.11 or newer, on Windows | This machine has only Python 3.14 |
| Input | One YAML file per installation | Nesting in YAML matches the tree of the installation |
| Interface | Command line for now; messages in Dutch | The reader sits behind a neutral data model so Excel or a form can replace it |
| Output | One SVG per page, and one PDF with selectable text drawn from those SVGs | svglib converts each page onto one ReportLab canvas; no merge step |
| Pages | A4 portrait; pages are typed in the YAML, each with its own title; no automatic flow | Confirmed 12 Oct; automatic flow is a possible later extension |
| Scope | Single-line diagram only | Position plan, panel layout and material list come later |
| Intelligence | None: the tool draws what is typed | No circuit assignment and no AREI rule checks in version 1 |
| Test cases | House A (redraw, M2–M5), House B (final test, M7 power, M8 lighting and control) | Order M1–M5, M7, M6, M8 |
| Symbols | AREI symbols, generated from the ShadowHunter library by a converter | AREI Book 1 table 2.23 is the ground truth |
| Labels | Dutch; text formats are templates | House A keeps its original formats, House B uses the official ones |
| Font | Helvetica in SVG and PDF; text widths from ReportLab's metrics | Same result on every PC |
| Way of working | CLAUDE.md in the repository root | Covers pacing, models, token use and the decision log |

Runtime dependencies are PyYAML, pydantic, svglib and reportlab; pytest and pypdf are development dependencies. Versions are pinned in `pyproject.toml`. Scripts in `tools/` use the standard library only. Each dependency is logged in docs/decisions.md when first used.

## House A: existing diagram

The target is four A4 portrait pages holding 16 circuits and 20 lighting detail rows (25 light points in total with K6, K7, K8, C4 and H1). Three of its features change the input format and layout.

1. **Pages follow content, not overflow.** Page 1 holds the supply and differential 1, page 2 holds differential 2, and pages 3 and 4 detail one lighting circuit each. Arrows with "Naar Pg 3" and "Van Pagina 2" link them.
2. **Breakers nest.** A 32 A breaker feeds a second bus of four circuits over XVB 5x6, and circuit P branches off the end of circuit O.
3. **Lighting detail pages use a different row.** There is no breaker: each row has one switch contact, one light and a name such as "A1 Garage voor".

The supply is 3x230 V with a 40 A main breaker and a 300 mA 4x40 A differential ahead of two 30 mA 4x40 A differentials. A number in brackets is the count shown beside a socket.

| Page | Circuit | Breaker | Cable | Description | Devices |
| --- | --- | --- | --- | --- | --- |
| 1, Diff 1 | I | 20 A | XVB 3x2.5 | Gang + poort | Sockets I1, I2, I3 |
| 1, Diff 1 | J | 20 A | XVB 3x2.5 | Badkamer + slaapkamer 2 | Sockets J1 (2), J2 (2), J3, J4, J5, J6 |
| 1, Diff 1 | K | 16 A | XVB 3x2.5 | Garage + lichten buiten en WC | Sockets K1 to K5; light with switch mark K6; lights K7 and K8, each behind a square-with-triangle symbol |
| 1, Diff 1 | 32 A breaker | 32 A | XVB 5x6 | Labelled "Hoofd auto 1" | Feeds N, L, M and O |
| 1, behind 32 A | N | 20 A | XVB 3x2.5 | Keuken | Sockets N1 (2), N2, N3, N4 (2), N5 (3), N6 (2), N7 (2) |
| 1, behind 32 A | L | 20 A | XVB 3x2.5 | Werkplaats | Sockets L1, L2 |
| 1, behind 32 A | M | 20 A | XVB 3x2.5 | Wasmachine | Socket M1 |
| 1, behind 32 A | O | 20 A | XVB 3x2.5 | Fornuis en oven | Sockets O1 (marked 3ph), O2 |
| 1, behind O | P | 20 A | XVB 3x2.5 | stopcontact onder wasbak | Socket P3 (2) |
| 2, Diff 2 | A | 16 A | XVB 3x1.5 | lichtkring gelijkvloers | Detailed on page 3 |
| 2, Diff 2 | B | 20 A | XVB 3x2.5 | CV | One socket, labelled J1 |
| 2, Diff 2 | C | 20 A | XVB 3x2.5 | Bureau + zithoek | Sockets C1 (2), C2 (2), C3, C6 (2), C7 (2), C8 (2); light with switch mark C4; box C9 Rolluik |
| 2, Diff 2 | D | 20 A | XVB 3x2.5 | Zithoek, eethoek, Veranda | Sockets D1 (2), D2 (2), D3, D4 (2), D5 (4) |
| 2, Diff 2 | E | 20 A | XVB 3x2.5 | Hobby / slaapkamer 1 | Sockets E1, E2 (2), E3, E4, E5 (2), E6 (2) |
| 2, Diff 2 | F | 6 A | XVB 3x2.5 | Transformators | Transformer F1, converter F2 |
| 2, Diff 2 | G | 16 A | XVB 3x2.5 | verlichting 2de Verdiep | Detailed on page 4 |
| 2, Diff 2 | H | 16 A | XVB 5x6 | verlichting zolder | Light H1 behind a square-with-triangle symbol |
| 3 | A1 to A11 | none | none | Verlichting gelijkvloers | 11 rows of switch and light: Garage voor, Garage achter, gang en 1ste, werkplaats, zithoek, eethoek, bureau, spots zithoek, spots eethoek, keuken, terras |
| 4 | G1 to G9 | none | none | Verlichting 2de verdiep | 9 rows of switch and light: Badkamer, Gang, Hobbykamer, Slaapkamer 1, Muurverlichting A and B slaapkamer 1, Slaapkamer 2, Muurverlichting A and B slaapkamer 2 |

What the review of the reference pages found:

- **Most of each reference SVG is off-page.** Single layer, nothing hidden, but PLC blocks, an older version of the diagram and copies of other pages sit outside the 210 x 297 viewBox. Visible texts: pg1 78 of 237, pg2 67 of 205, pg3 17 of 142, pg4 15 of 137. Anything that reads these files applies the transforms and keeps only elements inside x 0..210, y 0..297.
- **Link texts vary:** "Naar Pg 2 Ref Diff 2", "Van pg 1", "Naar Pg 3", "Van Pagina 2 verlichting gelijkvloers". Links therefore take an optional reference text.
- **Row height is not constant.** Page 2 rows sit at y 57, 72, 88, 104, 118, 134, then 165 and 180. The 32 A breaker with its vertical 5x6 cable takes two rows; devices that hang lower (K7/K8, H1, F1/F2) take extra height.
- **Detail pages have a circuit letter header** ("A" or "G" at x 141, y 52).
- The title block and names on the reference pages are replaced by placeholders; the repository holds no personal names or addresses.

The original has points that look like slips. The tool draws what is typed, so the owner decides for each one whether the YAML copies or corrects it. Answers are needed before M5.

- [ ] The title block of page 2 reads "Pagina 1: aansluiting".
- [ ] The socket on circuit B is labelled J1.
- [ ] The only socket on circuit P is labelled P3.
- [ ] Circuit C has no C5.
- [ ] "Hoofd auto 1" labels three devices: the 40 A main breaker, the 300 mA differential and the 32 A breaker.
- [ ] Lighting circuit H shows cable XVB 5x6, and G shows XVB 3x2.5 where A shows XVB 3x1.5.
- [ ] The title block has the typos "Geteken" and "verlicthting".
- [ ] The pages show no earthing, date or version; the file name says V1_00.
- [ ] What is the square-with-triangle symbol ahead of lights K7, K8 and H1?
- [ ] What do the small grey marks above each cable mean?
- [ ] Off-page leftovers name the K lights "K6 Tuin, K7 Werkplaats, K8 Wc". Use those names?

## House B: final test

The design overview is `docs/testcase/house-b-overzicht-v4.md`; the values it leaves open are fixed provisionally in `docs/decisions.md`. There is no existing drawing, so the check compares the PDF with the overview.

| Part | Content |
| --- | --- |
| Supply | 3N400V; DIFF-ALG 300 mA type A, 40 A, 4-pole, which is also the main switch |
| Differentials | D1–D5 30 mA type A, 4-pole, 40 A; D5 serves only circuit G |
| Main board | 22 circuits A–Y (H, I, O and Z unused); A and J sit directly behind DIFF-ALG |
| Sub-board | BRD-TUIN, fed by circuit J (XVB 5G6), with DIFF-TUIN 30 mA type A 40 A and circuits T1–T3 |
| Devices | Sockets with 1 to 4 mechanisms, appliances with their AREI symbol, EV charger, reserve circuits Y and T3 |
| Later (M8) | Lighting circuits 1–35 through a push-button controller; 70 light points |
| Not drawn | Earthing, surge protection, installation marks, phases |

Structures House A does not have, and the model and layout must support: 3P+N circuits with curve, differential type, a sub-board on its own page, circuits directly behind the 300 mA, reserve circuits, appliances and the EV charger on the circuit line, an impulse relay ahead of V's sockets, and a title block with version and date.

## Pipeline

Five steps, each a separate module so any one can be swapped.

1. **Read**: load the YAML file into plain Python data.
2. **Validate**: build the data model and report errors with an error code, the element ID and a plain Dutch message. Check for duplicate IDs, unknown element kinds, unknown keys, missing fields and references to pages that do not exist.
3. **Lay out**: turn the tree into styled drawing primitives placed in millimetres on each page. This step knows nothing about SVG or PDF.
4. **Render**: write one SVG per page from the primitives.
5. **Export**: convert each SVG with svglib and draw it as one page of a single ReportLab canvas.

The command is `huiselek build installatie.yaml -o schema.pdf`. A second command, `huiselek symbols -o symbolen.pdf`, prints the symbol review sheet.

## Input format

The file holds one tree for the whole installation, plus a list of pages with their titles. The example is cut down from House A and shows the constructs that case needs; House B adds the fields and kinds in the table below.

```yaml
project:
  address: "Straat A 1, 0000 Gemeente"
  drawn_by: "Ontwerper"
  executed_by: "Installateur"

pages:
  - {id: pg1, title: "Pagina 1: aansluiting"}
  - {id: pg2, title: "Pagina 2: differentieel 2"}
  - {id: pg3, title: "Pagina 3: Verlichting gelijkvloers A"}

installation:
  kind: supply
  id: SUP
  page: pg1
  label: "Aansluiting en teller"
  voltage: "3*230 V"
  children:
    - kind: breaker
      id: Q0
      rating_a: 40
      label: "Hoofd auto 1"
      children:
        - kind: differential
          id: D0
          sensitivity_ma: 300
          rating_a: 40
          poles: 4
          children:
            - kind: differential
              id: D1
              label: "Diff 1"
              sensitivity_ma: 30
              rating_a: 40
              poles: 4
              children:
                - kind: circuit
                  id: K
                  description: "Garage + lichten buiten en WC"
                  rating_a: 16
                  cable: "XVB 3x2.5"
                  children:
                    - {kind: socket, id: K1}
                    - {kind: light, id: K6, switch: true}
                - kind: breaker            # nested breaker with its own bus
                  id: Q1
                  rating_a: 32
                  cable: "XVB 5x6"
                  children:
                    - kind: circuit
                      id: O
                      description: "Fornuis en oven"
                      rating_a: 20
                      cable: "XVB 3x2.5"
                      children:
                        - {kind: socket, id: O1, note: "3ph"}
                        - kind: circuit    # branches off the end of O
                          id: P
                          description: "stopcontact onder wasbak"
                          rating_a: 20
                          cable: "XVB 3x2.5"
                          children:
                            - {kind: socket, id: P3, count: 2}
            - kind: differential
              id: D2
              label: "Diff 2"
              page: pg2                    # drawn on page 2, link arrow on page 1
              sensitivity_ma: 30
              rating_a: 40
              poles: 4
              children:
                - kind: circuit
                  id: A
                  description: "lichtkring gelijkvloers"
                  rating_a: 16
                  cable: "XVB 3x1.5"
                  children_page: pg3       # children drawn one per row on page 3
                  children:
                    - {kind: light, id: A1, switch: true, name: "Garage voor"}
                - kind: circuit
                  id: C
                  description: "Bureau + zithoek"
                  rating_a: 20
                  cable: "XVB 3x2.5"
                  children:
                    - {kind: socket, id: C1, count: 2}
                    - {kind: box, id: C9, label: "Rolluik"}
```

| Kind | Fields | Children |
| --- | --- | --- |
| project | address, drawn_by, executed_by, optional version, date | none |
| labels (top level, optional) | overrides of label templates for this project | none |
| supply | label, voltage | breakers, differentials |
| breaker | rating_a, optional label, curve, poles, cable, conductors | differentials, breakers, circuits |
| differential | sensitivity_ma, rating_a, poles, type (AC, A, F, B), optional selective, label | differentials, breakers, circuits |
| circuit | description, rating_a, optional curve (default C), poles, cable, conductors, children_page | devices, circuits, board |
| board | label | differentials, breakers, circuits |
| reserve | optional rating_a, curve, poles; without a rating it is a free place | none |
| socket | optional count (mechanisms), variant (default protective conductor with child protection; or protective conductor, waterproof), note | none |
| light | optional switch, name, count | none |
| appliance | type (oven, dishwasher, washing_machine, dryer, stove, water_heater, heating_device, ev_charger, …), optional note | none |
| impulse_relay | none beyond id | devices |
| transformer, converter | none beyond id | none |
| box | label | none |

Rules that keep the format stable:

- IDs are unique across the file and always strings; a number typed as an ID is converted. Unknown keys are an error.
- `page` moves a node and everything under it to that page; `children_page` moves only its children. Both draw the "Naar" and "Van" link arrows automatically, with an optional reference text.
- Children that stay on their circuit's page are drawn along the circuit line; children moved to their own page are drawn one per row with their name.
- Label formats are templates in `labels.py`; a project's `labels` section overrides them. No format is hard-coded in layout or symbols.
- The square-with-triangle device ahead of lights K7, K8 and H1 gets its own kind once the owner has named it.

Field names are a proposal. Task 1.3 fixes them against House A and House B together and logs them.

## Symbols

Symbols come from the ShadowHunter AREI library in `docs/reference/arei/`; its licence allows use and modification and stays with the files. Sources rank as follows:

1. AREI Book 1 table 2.23, the ground truth (`docs/reference/arei/official/`, with notes).
2. The 2023 Visio stencils (`visio-2023-nl/`), for example "Differentieel 2023" and the EV charger.
3. The older SVG set (`svg-en/`), single-line variant.
4. Measurements of the House A pages, only for symbols with no AREI source.

Symbols are generated, not hand-coded:

- `tools/vssx_to_svg.py` converts the needed 2023 masters to SVG.
- `tools/svg_to_symbol.py` turns a library SVG into primitives in millimetres, flattens curves to polylines, normalises line width, and writes one data file per symbol to `src/huiselek/symbol_data/`. The data files are committed.
- `src/huiselek/symbol_table.yaml` gives per symbol: source file, size, anchor and named connection points. It is written by hand.
- `symbols.py` loads the data files and the table. Only the page link arrow and the square-with-triangle are drawn in code.

| Group | Symbols | Needed for |
| --- | --- | --- |
| Protection | Breaker, differential (2023), fuse | Both |
| Supply | kWh meter, three-phase mark | Both |
| Lines | Conductors in a cable (n slash) | Both |
| Sockets | Protective conductor with child protection, protective conductor, waterproof; count beside the stem | Both |
| Lights and switches | Light point, light with built-in switch, switch contact, impulse relay | Both |
| Appliances | Oven, dishwasher, washing machine, dryer, stove, water heater, heating device, EV charger, general appliance | House B |
| Other | Transformer, converter, box, distribution board (sub-board frame) | Both |
| Code-drawn | Page link arrow, square-with-triangle | House A |
| M8 | Push button, motion sensor, domotica control unit, motor | House B lighting |

The symbol sheet shows three columns per symbol, official image, library source and generated symbol, and the owner approves it before layout work starts. Before the House B dossier is used, an installer or inspection body reviews the approved sheet.

## Layout

The diagram reads top to bottom: a vertical bus on the left, each circuit a horizontal row to the right, devices hanging below the circuit line. The values below were measured from the House A pages and are the starting settings.

| Item | Value (mm) |
| --- | --- |
| Page | 210 x 297, frame line 0.8 thick |
| Title block | Top edge at y 276.5, two rows of 10, split at x 105 |
| Title block cells | Page title and address on the first row; drawn by and executed by on the second; version and date when given |
| First circuit row | y 57 |
| Row pitch | 15.4 minimum, which gives about 14 rows per page |
| Main bus | x 63.5 |
| Breaker | x 69 to 76, rating text above |
| Cable text | x 78, below the line |
| First device | x 97.5 |
| Device pitch | 7.6, which gives about 8 devices per circuit line |
| Circuit letter and description | x 161, letter above the description |
| Detail page | Bus at x 71.5, switch at x 93 to 99, light at x 119, name at x 141, same row pitch, circuit letter header at y 52 |
| Text | Helvetica; 2.9 for circuit text, 1.8 for device IDs, 4.2 in the title block |
| Lines | 0.26 |

The supply chain on page 1 (supply, main breaker, 300 mA differential and their texts) is measured in task 3.4.

Rules:

- A row is as tall as the row pitch or its content, whichever is larger.
- A differential sits on the bus with its text below it; its circuits branch from the bus after it.
- A nested breaker starts a new bus segment below itself for its children; its vertical cable takes the rows it needs.
- A circuit nested in a circuit starts at the end of its parent's line, one row lower, with its own breaker and cable text.
- A device with a count above 1 is drawn once with the number beside its stem.
- A subtree moved to another page leaves a "Naar" arrow on the source page and a "Van" arrow at the top of the target page.
- Pages never flow automatically. If the rows or devices of a page do not fit, the build stops with an error naming the page and the element.
- Text widths come from ReportLab's Helvetica metrics.
- All values live in one settings file.

House B constructs (circuits directly behind the 300 mA, the sub-board page and frame, reserve circuits, appliances, the impulse relay) are designed in task 7.1.

## Code architecture

The package is eleven small modules in one line of dependency: each module uses only the ones above it in the table, and the layout never touches SVG or PDF.

| Module | Responsibility | Takes | Gives |
| --- | --- | --- | --- |
| errors.py | One exception type carrying an error code, an optional element ID and parameters | none | HuiselekError |
| settings.py | Every dimension, with defaults and an optional override file | optional settings YAML | Settings |
| labels.py | Every Dutch string: drawing texts, label templates and error messages, with project overrides | optional overrides | text lookups, formatted labels |
| primitives.py | Styled drawing primitives and the page that holds them | none | Line, Polyline, Arc, Circle, Rect, Text, Page |
| model.py | The installation as validated classes | plain dict | Installation |
| reader.py | Read the YAML file, report file and syntax errors | file path | plain dict |
| symbols.py | Load symbol data and table; the two code-drawn symbols | Settings | dict of Symbol |
| layout.py | Place every element on its page | Installation, symbols, Settings | list of Page |
| render_svg.py | Turn one page of primitives into SVG text, with fixed number formatting and element order | Page, Settings | SVG string |
| export_pdf.py | Convert each SVG with svglib onto one ReportLab canvas | SVG strings, output path | one PDF file |
| cli.py | Parse arguments, run the pipeline, print Dutch messages, set the exit code | command line | files and messages |

Every primitive carries a style: stroke width, fill and dash. Text also carries anchor, rotation and size. The data model is a tree of nodes, one pydantic class per kind, selected by the `kind` field, with unknown keys forbidden.

```python
class Project:       address, drawn_by, executed_by, version, date
class PageDef:       id, title
class Node:          kind, id, page | None                     # base class
class Supply:        label, voltage, children
class Breaker:       rating_a, label, curve, poles, cable, conductors, children
class Differential:  sensitivity_ma, rating_a, poles, type, selective, label, children
class Circuit:       description, rating_a, curve, poles, cable, conductors, children_page, children
class Board:         label, children
class Reserve:       rating_a, curve, poles
class Socket:        count, variant, note
class Light:         switch, name, count
class Appliance:     type, note
class ImpulseRelay:  children
class Transformer, Converter:    (id only)
class Box:           label
class Installation:  project, pages, labels, root

class Symbol:        primitives, bbox, points      # points: name -> (x, y)
class Page:          id, number, title, primitives
```

Pydantic reports error locations as list indexes; `build_model` maps them back to the element ID.

Six functions are the whole interface between modules, so each can be built and tested by a separate task.

```python
def read(path: Path) -> dict                                            # reader
def build_model(data: dict) -> Installation                             # model, raises HuiselekError
def load_symbols(s: Settings) -> dict[str, Symbol]                      # symbols
def layout(inst: Installation, sym: dict[str, Symbol], s: Settings) -> list[Page]   # layout
def render_svg(page: Page, s: Settings) -> str                          # render_svg
def export_pdf(svgs: list[str], out: Path) -> None                      # export_pdf
```

Because the layout produces only styled primitives, a second renderer that draws them straight into a PDF is a small addition. That is the fallback if SVG conversion misbehaves on Windows.

## Repository setup

One Python package in a `src` layout, with documents, tools, examples and tests beside it.

```text
huiselek/
  CLAUDE.md                  way of working
  README.md                  install and usage
  pyproject.toml             package, pinned dependencies, the huiselek command
  .gitignore                 .venv, out, __pycache__, full reference PDFs
  docs/
    handoff-plan.md          this plan
    decisions.md             decision log
    progress.md              state and next step, updated per milestone
    plan-review.md           review of 11 October, history only
    user-guide.md            written in M6
    background/              scope and requirements of the full idea
    reference/               House A pages; arei/ library, official table extract and notes
    testcase/                House B design overview
  src/huiselek/
    __init__.py  cli.py  reader.py  model.py  errors.py
    primitives.py  symbols.py  layout.py
    render_svg.py  export_pdf.py
    settings.py  labels.py
    symbol_table.yaml        anchor, size and points per symbol
    symbol_data/             generated symbol primitives, committed
  tools/                     standard library only, not part of the package
    vssx_to_svg.py  svg_to_symbol.py
    svg_visible_text.py      on-page text of a reference SVG
    compare_text.py  check_house_b.py
  examples/
    minimal.yaml             one differential, three circuits
    house-a.yaml             written in M5
    house-b.yaml             written in M7
  tests/
    test_model.py  test_reader.py  test_cli.py
    test_symbols.py  test_layout.py  test_render.py  test_export.py
    data/                    broken YAML files for error tests
    golden/                  approved SVG pages
  out/                       generated files, not committed
```

Setup on Windows, in PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
huiselek build examples\minimal.yaml -o out\minimal.pdf
```

Git uses one branch, main, on GitHub, with one commit per approved milestone. The repository is checked for personal names and addresses before every push. Full reference documents stay local; only extracts are committed.

## Milestones and tasks

Seven milestones in the order M1–M5, M7, M6, with M8 later. Each task fits a brief of a few lines: goal, files to read, exact output and the check. The model column follows CLAUDE.md: Opus plans and reviews in the main session, Sonnet codes, Haiku does mechanical work. Small repetitive items are batched about five per brief.

| Task | What | Model | Check |
| --- | --- | --- | --- |
| 1.1 | Repository skeleton as in Repository setup: empty modules, pyproject with pinned versions, one smoke test that imports the package; extend the existing .gitignore | Haiku | `pip install -e ".[dev]"` on Python 3.14 under Windows and `pytest -q` pass |
| 1.2 | PDF route trial: a hand-written sample SVG with text, an arc, fill, dashes and thin lines, two pages on one canvas with svglib and ReportLab | Sonnet | PDF opens at A4 with two pages, selectable text and correct lines; result logged |
| 1.3 | Fix field names, kinds, error codes and the list of label templates against House A and House B | Opus, main session | Owner agrees; logged in decisions.md |
| 1.4 | model.py and errors.py for every kind, pages, `page` and `children_page`; error location mapped to element ID | Sonnet | Valid example loads; each broken file gives the expected error code and element ID |
| 1.5 | reader.py, cli.py `build` up to validation with Dutch messages, examples/minimal.yaml | Sonnet | A broken file exits non-zero with a one-line Dutch message |
| 2.1 | primitives.py with styles and Page; render_svg.py; a command that writes golden candidates to out/ | Sonnet | Golden test of one page holding one of each primitive and style |
| 2.2 | tools/vssx_to_svg.py for the needed 2023 masters, plus a list of symbols that differ between the old and 2023 sets | Sonnet | Each converted symbol rendered next to its official image and checked by eye |
| 2.3 | tools/svg_to_symbol.py and the generated symbol_data files | Sonnet | Every symbol in the table converts; output is identical on a second run |
| 2.4 | symbol_table.yaml entries: size, anchor, connection points | Haiku, batched | Each symbol stays inside its bounding box; points lie on its outline |
| 2.5 | symbols.py: load data and table; code-drawn page link and square-with-triangle | Sonnet | Parametrised test over all symbols |
| 2.6 | `huiselek symbols` sheet with three columns: official, library, generated | Sonnet | Owner approves the sheet |
| 3.1 | Layout design note: variable row height, nested breaker, branching circuit, text metrics | Opus, main session | Owner agrees; logged in decisions.md |
| 3.2 | Rows for one differential with plain circuits (I, J, K) | Sonnet | Golden SVG; positions match the Layout table |
| 3.3 | Nested breaker with its bus, and a circuit branching off a circuit (N, L, M, O, P) | Sonnet | Golden SVG |
| 3.4 | Measure and draw frame, title block (with optional version and date), supply, main breaker, 300 mA differential | Sonnet | Page 1 complete as SVG and PDF |
| 3.5 | Overflow errors for too many rows or devices | Sonnet | One test per error |
| 4.1 | Page assignment from `page` and `children_page`, link arrows with optional reference text | Sonnet | Minimal two-page example links both ways |
| 4.2 | Lighting detail rows: header letter, switch contact, light, name | Sonnet | Golden SVG of a detail page |
| 4.3 | export_pdf.py: all pages on one canvas | Sonnet | PDF has the right page count, every page A4 |
| 4.4 | Docstrings and README usage | Haiku | README commands run as written |
| 5.1 | Type examples/house-a.yaml from the inventory, applying the owner's answers on the slips | Sonnet | Loads without errors; 16 circuits, 20 detail rows, 25 light points |
| 5.2 | tools/svg_visible_text.py and tools/compare_text.py: on-page text of each original against the regenerated page | Sonnet | List of missing and extra texts per page |
| 5.3 | Fix the differences found | Sonnet, small fixes in main session | No missing text apart from the allow-list of agreed corrections and format differences |
| 7.1 | Layout design note for House B constructs | Opus, main session | Owner agrees; logged in decisions.md |
| 7.2 | Build the House B constructs | Sonnet | Golden SVG per construct on a small example |
| 7.3 | tools/check_house_b.py part 1: expected list of circuits, devices and values read from the overview tables plus the provisional values, written before the YAML | Sonnet | Totals match the overview: 22 + 3 circuits, 74 + 4 sockets, 6 differentials |
| 7.4 | Type examples/house-b.yaml from the overview, after the parked data questions are answered | Sonnet | Loads without errors |
| 7.5 | check_house_b.py part 2: compare the PDF text with the expected list; fix differences | Sonnet | No differences apart from agreed ones |
| 6.1 | Edge cases from M5 and M7; decide whether long circuits should wrap | Opus decides, Sonnet builds | Logged in decisions.md |
| 6.2 | Golden files for the House A and House B pages; tests complete | Sonnet | `pytest -q` green |
| 6.3 | docs/user-guide.md with every kind and field | Sonnet | A new example written only from the guide builds |
| 8.x | Lighting circuits 1–35 and the controller; planned when the source xlsx and a drawing decision are in | Opus plans | To be planned |

Every milestone closes the same way: tests pass, an agent that has not seen the work reviews it, the planning session verifies it independently, the owner sees the PDF and approves, then one commit and an update of docs/progress.md.

| Milestone | Done when |
| --- | --- |
| M1 Skeleton | The example file loads, a broken file gives a clear Dutch error, and the PDF route is proven on Windows |
| M2 Symbols | The owner has approved the three-column symbol sheet |
| M3 One page | Page 1 of House A is drawn correctly from a hand-typed excerpt |
| M4 Multi-page | A multi-page example prints cleanly on A4 with working page links |
| M5 House A | The four new pages carry the same information as the originals |
| M7 House B power | Main board and BRD-TUIN drawn; the check script finds no differences with the overview |
| M6 Hardening | Tests pass and the guide lets a new user draw their own installation |
| M8 House B lighting | Lighting circuits and controller drawn; 70 light points |

## Test plan

Eight kinds of test, each tied to the milestone that introduces it. A milestone is accepted when its tests pass, the review agent has reported, the planning session has verified, and the owner has approved the PDF.

| Test | What it proves | How | From |
| --- | --- | --- | --- |
| Validation | Missing fields, duplicate IDs, unknown kinds, unknown keys and unknown pages are refused | Broken YAML files in tests/data; assert error code and element ID, not message text | M1 |
| Command line | Exit codes and messages are right | Run the command in a subprocess | M1 |
| Symbols | Every symbol converts the same way twice, stays inside its bounding box and has its connection points | One parametrised test over the symbol table | M2 |
| Layout | Rows follow the row algorithm, text boxes on a page do not overlap, overflow raises an error | Assertions on the primitive lists, with no SVG involved | M3 |
| Rendering | SVG is well-formed, A4 sized and byte-identical for identical input | Golden files in tests/golden | M3 |
| Export | The PDF has the expected page count, A4 pages of 595 x 842 pt and extractable text | Read the PDF back with pypdf | M4 |
| House A | Every on-page text of an original appears on the regenerated page | compare_text.py with an allow-list | M5 |
| House B | Every circuit, device and value in the overview appears in the PDF | check_house_b.py against a list built from the overview, independent of the YAML | M7 |

Golden files change only on purpose: a test run never rewrites them, a separate command writes candidates to out/, and a golden file is committed only after the owner has approved the page it shows. Tests run quietly, showing failures and the summary line.

## Risks and fallbacks

| Risk | First sign | Fallback |
| --- | --- | --- |
| SVG to PDF conversion behaves differently on Windows, or mangles text or arcs | Task 1.2 gives a wrong page | Draw the primitives straight into the PDF with ReportLab; SVG stays as a second output |
| Python 3.14 lacks a wheel for a dependency | Task 1.1 install fails | Install Python 3.12 or 3.13 beside it, or choose another version of that dependency |
| Visio geometry converts wrongly, mostly arcs and text | Task 2.2 symbol differs from the official image | Draw that symbol from the official table image by hand |
| Library and official table differ | Three-column sheet shows a difference | The official table wins |
| Field names change after YAML has been typed | Rework of examples and tests | Task 1.3 fixes them against both cases first; later changes go through the decision log |
| The square-with-triangle symbol stays unidentified | Owner cannot name it | Draw it as in the original under a neutral name and rename it later |
| Golden files churn while layout is tuned | Each tweak breaks many tests | Keep golden files to small examples until task 6.2 |
| Slips and format differences make "same information" unclear | Task 5.2 reports differences that are corrections | The slips are answered before M5 and feed the allow-list |
| The House B check repeats a typing error | Expected list and YAML agree on a wrong value | The expected list is built from the overview tables before the YAML is typed |
| A typed page overflows as the installation grows | Build error naming the page | The owner moves a subtree with `page`; automatic flow stays out of scope |
| The YAML nests too deep to type comfortably | Indentation mistakes while typing a case | Consider a flat form in M6, with circuits listed at top level and a `parent` field |
| Two sessions edit the same files | Unexpected changes in git status | The coding session owns src, tests, tools and examples; the planning session edits only docs, and checks git status first |
| Usage limits are hit mid-milestone | Limit warning | Stop at a task boundary, update docs/progress.md and continue in the next window |

## Out of scope and open answers

Version 1 leaves out the position plan, panel layout, material list, automatic circuit assignment, AREI rule checking, Excel input, automatic page flow (a possible later extension), a graphical interface, and on the drawing: earthing, surge protection, installation marks and phases.

Answers needed from the owner:

- [x] Pages are typed in the YAML and never flow automatically (confirmed 12 October).
- [ ] The House A slips under House A: copy or correct each (before M5).
- [ ] Name the square-with-triangle symbol and the grey marks above the cables (before task 2.6).
- [ ] House B data, before task 7.4: which circuits besides J are XVB (the rest is VOB in conduit); VOB label text, official "H07V-U Eca 2.5²" or "VOB 3x2.5"; confirm DIFF-TUIN 4-pole and D1–D5 40 A.
- [ ] The House B source xlsx and how the controller is drawn (before M8).

## Handoff prompt

Paste this as the first message of the coding session.

```markdown
Read CLAUDE.md, docs/handoff-plan.md and docs/decisions.md first.
CLAUDE.md is how we work; the plan is what we build; the decision log
is why. docs/plan-review.md is history and need not be read.

Build "huiselek" as the plan describes. Start with milestone M1 only: give
me your short plan for M1 and wait for my go.

The reference pages in docs/reference/ are large and mostly off-page, so do
not read them whole. Use the inventory and measurements in the plan and the
notes in docs/reference/arei/official/notes.md.
```
