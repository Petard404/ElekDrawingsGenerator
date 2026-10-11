# Huis Elek – Single-line generator: handoff plan

11 October 2026 · Owner

> Amended on 11 October 2026 by `docs/plan-review.md` and `docs/decisions.md`, which win where they differ from this plan. The main change: the final test is House B (`docs/testcase/house-b-overzicht-v4.md`), added as milestones M7 and M8.

Version 1 is a Python command-line tool that reads one YAML file describing a household installation and writes an AREI-style single-line diagram (eendraadschema) as a multi-page A4 portrait PDF. The user types the full structure, including the pages; the tool only draws it. The target is to regenerate the existing four-page diagram of House A.

## Decisions

| Topic | Decision | Note |
| --- | --- | --- |
| Language | Python 3.11 or newer, running on Windows | Decided |
| Input | One YAML file per installation | Nesting in YAML matches the tree of the installation |
| Interface | Command line for now | Not fixed; the reader sits behind a neutral data model so Excel or a form can replace it |
| Output | One SVG per page, merged into one PDF with selectable text | Decided |
| Pages | A4 portrait; pages are typed in the YAML, each with its own title | Proposed, to confirm. It follows the existing diagram, where pages are organised by content |
| Scope | Single-line diagram only | Position plan, panel layout and material list come later |
| Intelligence | None: the tool draws what is typed | No circuit assignment and no AREI rule checks in version 1 |
| Test case | The existing four-page diagram of House A | Four SVG files, analysed below |
| Symbols | Start with the 13 symbols the existing diagram uses | The diagram is the reference until AREI reference drawings are supplied |
| PDF route | svglib and ReportLab for conversion, pypdf for merging | Installed with pip alone and converted a sample page on Linux on 11 Oct 2026 (svglib 2.3.0, reportlab 5.0.1). Not yet tried on Windows: task 1.2 |
| Diagram language | Dutch labels | Held in one labels file |
| Way of working | CLAUDE.md in the repository root | Covers pacing, models, token use and the decision log |

Runtime dependencies are PyYAML, pydantic, svglib, reportlab and pypdf; pytest is the only development dependency. Each one is logged in docs/decisions.md when first used.

## Existing diagram

The target is four A4 portrait pages holding 16 circuits and 20 lighting points. Three of its features were not in the first plan and change the input format and layout.

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

The original has points that look like slips. The tool draws what is typed, so the owner decides for each one whether the YAML copies or corrects it.

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

## Pipeline

Five steps, each a separate module so any one can be swapped.

1. **Read**: load the YAML file into plain Python data.
2. **Validate**: build the data model and report errors with the element ID and a plain message. Check for duplicate IDs, unknown element kinds, unknown keys, missing fields and references to pages that do not exist.
3. **Lay out**: turn the tree into drawing primitives (line, polyline, arc, circle, rectangle, text) placed in millimetres on each page. This step knows nothing about SVG.
4. **Render**: write one SVG file per page from the primitives.
5. **Export**: convert each SVG to a PDF page and merge the pages into one file.

The command is `huiselek build installatie.yaml -o schema.pdf`. A second command, `huiselek symbols -o symbolen.pdf`, prints every symbol with its name for review.

## Input format

The file holds one tree for the whole installation, plus a list of pages with their titles. The example is cut down from the real case and shows every construct the existing diagram needs.

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
| supply | label, voltage | breakers, differentials |
| breaker | rating_a, optional label, cable, poles | differentials, breakers, circuits |
| differential | sensitivity_ma, rating_a, poles, optional label | differentials, breakers, circuits |
| circuit | description, rating_a, cable | devices and circuits |
| socket | optional count, note | none |
| light | optional switch, name, count | none |
| transformer, converter | none beyond id | none |
| box | label | none |

Four rules keep the format stable:

- IDs are unique across the file, and unknown keys are an error.
- `page` moves a node and everything under it to that page; `children_page` moves only its children. Both draw the "Naar" and "Van" link arrows automatically.
- Children that stay on their circuit's page are drawn along the circuit line; children moved to their own page are drawn one per row with their name.
- The square-with-triangle device ahead of lights K7, K8 and H1 gets its own kind once the owner has named it.

Field names are a proposal. The coding session fixes them at the start of M1 and logs them.

## Symbols

Version 1 needs the 13 symbols the existing diagram uses, not the 30 first assumed. Each is one function that returns primitives in millimetres around an anchor point, with named connection points.

| Symbol | Where in the original | Drawn as |
| --- | --- | --- |
| Supply and meter | Page 1, top left | Rectangle with a small bar, the label and the voltage |
| Breaker | Every circuit | Oblique contact ending in a filled bar, rating above |
| Differential | 300 mA, Diff 1, Diff 2 | Breaker symbol with a triangle and three lines of text: sensitivity, poles x rating, name |
| Cable marker | Every circuit | Conductor ticks across the line, cable type below, small grey marks above |
| Socket | Most circuits | Stem down from the line ending in an arc, count beside the stem, ID below, optional note such as 3ph |
| Light point | Pages 1 to 4 | Circle with a cross |
| Light with switch mark | K6, C4 | Light point with a small switch mark at the top |
| Square with triangle | K7, K8, H1 | Square with a triangle inside, in series above a light; not yet identified |
| Transformer | F1 | Two overlapping circles |
| Converter | F2 | Square with a diagonal and AC and DC marks |
| Labelled box | C9 Rolluik | Empty square with text below |
| Switch contact | Pages 3 and 4 | Open contact in the row, ahead of the light |
| Page link | Pages 1 to 4 | Arrow with "Naar Pg n" or "Van Pagina n" |

Symbols are redrawn from measurements of the existing diagram, not copied from another project, so no licence follows the code. AREI reference drawings override them once supplied. The symbol sheet is approved by the owner before layout work starts.

## Layout

The diagram reads top to bottom: a vertical bus on the left, each circuit a horizontal row to the right, devices hanging below the circuit line. The values below were measured from the original pages and are the starting settings.

| Item | Value (mm) |
| --- | --- |
| Page | 210 x 297, frame line 0.8 thick |
| Title block | Top edge at y 276.5, two rows of 10, split at x 105 |
| Title block cells | Page title and address on the first row; drawn by and executed by on the second |
| First circuit row | y 57 |
| Row pitch | 15.4, which gives about 14 rows per page |
| Main bus | x 63.5 |
| Breaker | x 69 to 76, rating text above |
| Cable text | x 78, below the line |
| First device | x 97.5 |
| Device pitch | 7.6, which gives about 8 devices per circuit line |
| Circuit letter and description | x 161, letter above the description |
| Detail page | Bus at x 71.5, switch at x 93 to 99, light at x 119, name at x 141, same row pitch |
| Text | Sans-serif; 2.9 for circuit text, 1.8 for device IDs, 4.2 in the title block |
| Lines | 0.26 |

Rules:

- A differential sits on the bus with its three text lines below it; its circuits branch from the bus after it.
- A nested breaker takes one row and starts a new bus segment below itself for its children.
- A circuit nested in a circuit starts at the end of its parent's line, one row lower.
- A device with a count above 1 is drawn once with the number beside its stem.
- A subtree moved to another page leaves an arrow with "Naar Pg n" on the source page and "Van Pagina n" at the top of the target page.
- Pages never flow automatically. If the rows or devices of a page do not fit, the build stops with an error naming the page and the element.
- All values live in one settings file.

## Code architecture

The package is eleven small modules in one line of dependency: each module uses only the ones above it in the table, and the layout never touches SVG or PDF.

| Module | Responsibility | Takes | Gives |
| --- | --- | --- | --- |
| errors.py | One exception type carrying an element ID and a message | none | HuiselekError |
| settings.py | Every dimension, with defaults and an optional override file | optional settings YAML | Settings |
| labels.py | Every Dutch string on the drawing | none | text lookups |
| primitives.py | The six things that can be drawn | none | Line, Polyline, Arc, Circle, Rect, Text |
| model.py | The installation as validated classes | plain dict | Installation |
| reader.py | Read the YAML file, report file and syntax errors | file path | plain dict |
| symbols.py | One function per symbol | Settings | Symbol: primitives, bounding box, connection points |
| layout.py | Place every element on its page | Installation, Settings | list of Page |
| render_svg.py | Turn one page of primitives into SVG text | Page, Settings | SVG string |
| export_pdf.py | Convert SVG files and merge them | SVG paths, output path | one PDF file |
| cli.py | Parse arguments, run the pipeline, set the exit code | command line | files and messages |

The data model is a tree of nodes, one pydantic class per kind, selected by the `kind` field.

```python
class Project:      address, drawn_by, executed_by
class PageDef:      id, title
class Node:         kind, id, page | None                      # base class
class Supply:       label, voltage, children
class Breaker:      rating_a, label, cable, poles, children
class Differential: sensitivity_ma, rating_a, poles, label, children
class Circuit:      description, rating_a, cable, children_page, children
class Socket:       count, note
class Light:        switch, name, count
class Transformer, Converter:   (id only)
class Box:          label
class Installation: project, pages, root

class Symbol:       primitives, bbox, points      # points: name -> (x, y)
class Page:         id, number, title, primitives
```

Five functions are the whole interface between modules, so each can be built and tested by a separate task.

```python
def read(path: Path) -> dict                                   # reader
def build_model(data: dict) -> Installation                    # model, raises HuiselekError
def layout(inst: Installation, s: Settings) -> list[Page]      # layout
def render_svg(page: Page, s: Settings) -> str                 # render_svg
def export_pdf(svgs: list[Path], out: Path) -> None            # export_pdf
```

Because the layout produces only six primitive types, a second renderer that draws them straight into a PDF is a small addition. That is the fallback if SVG conversion misbehaves on Windows.

## Repository setup

One Python package in a `src` layout, with documents, examples and tests beside it.

```text
huiselek/
  CLAUDE.md                  way of working
  README.md                  install and usage
  pyproject.toml             package, dependencies, the huiselek command
  .gitignore                 .venv, out, __pycache__
  docs/
    handoff-plan.md          this plan, exported
    decisions.md             decision log
    progress.md              state and next step, updated per milestone
    symbol-notes.md          measurements per symbol, written in task 2.2
    user-guide.md            written in M6
    reference/               the four original SVG pages, AREI drawings
  src/huiselek/
    __init__.py  cli.py  reader.py  model.py  errors.py
    primitives.py  symbols.py  layout.py
    render_svg.py  export_pdf.py
    settings.py  labels.py
  examples/
    minimal.yaml             one differential, three circuits
    house-a.yaml      the real case, written in M5
  tests/
    test_model.py  test_reader.py  test_cli.py
    test_symbols.py  test_layout.py  test_render.py  test_export.py
    data/                    broken YAML files for error tests
    golden/                  approved SVG pages
  out/                       generated files, not committed
```

Setup on Windows, in PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
huiselek build examples\minimal.yaml -o out\minimal.pdf
```

Git uses one branch, main, with one commit per approved milestone. Where the repository lives, GitHub or a local folder, is still the owner's choice.

## Milestones and tasks

Six milestones, 24 tasks. Each task is sized to fit a brief of a few lines: goal, files to read, exact output and the check. The model column follows CLAUDE.md: Opus plans and reviews in the main session, Sonnet codes, Haiku does mechanical work.

| Task | What | Model | Check |
| --- | --- | --- | --- |
| 1.1 | Repository skeleton as in Repository setup, with empty modules and pyproject | Haiku | `pip install -e ".[dev]"` and `pytest -q` run clean on Windows |
| 1.2 | PDF route trial: convert a hand-written sample SVG with text, an arc and thin lines using svglib and ReportLab | Sonnet | PDF opens on Windows at A4 size with selectable text and correct lines; result logged in decisions.md |
| 1.3 | Fix the YAML field names from the proposal in this plan | Opus, main session | Owner agrees; logged in decisions.md |
| 1.4 | model.py and errors.py for every kind, pages, `page` and `children_page` | Sonnet | Valid example loads; each broken file gives an error naming the element ID |
| 1.5 | reader.py, cli.py `build` up to validation, examples/minimal.yaml | Sonnet | A broken file exits non-zero with a one-line message |
| 2.1 | primitives.py and render_svg.py for the six primitives | Sonnet | Golden test of one page holding one of each primitive |
| 2.2 | Measure the 13 symbols once from the original pages | Sonnet | docs/symbol-notes.md lists size, anchor and connection points per symbol |
| 2.3 | One task per symbol, built from its notes entry: 13 short tasks | Haiku | Symbol stays inside its declared bounding box and appears on the sheet |
| 2.4 | `huiselek symbols` sheet with names and marked connection points | Sonnet | Owner compares the sheet with the original and approves |
| 3.1 | Layout design note: row algorithm, nested breaker, branching circuit | Opus, main session | Owner agrees; logged in decisions.md |
| 3.2 | Rows for one differential with plain circuits (I, J, K) | Sonnet | Golden SVG; positions match the Layout table |
| 3.3 | Nested breaker with its bus, and a circuit branching off a circuit (N, L, M, O, P) | Sonnet | Golden SVG |
| 3.4 | Frame, title block, supply, main breaker, 300 mA differential | Sonnet | Page 1 complete as SVG and PDF |
| 3.5 | Overflow errors for too many rows or devices | Sonnet | One test per error |
| 4.1 | Page assignment from `page` and `children_page`, with link arrows | Sonnet | Minimal two-page example links both ways |
| 4.2 | Lighting detail rows: switch contact, light, name | Sonnet | Golden SVG of a detail page |
| 4.3 | export_pdf.py: one SVG per page, convert, merge | Sonnet | PDF has the right page count, every page A4 |
| 4.4 | Docstrings and README usage | Haiku | README commands run as written |
| 5.1 | Type examples/house-a.yaml from the inventory in this plan, applying the owner's answers on the open points | Sonnet | Loads without errors; 16 circuits and 20 lighting points |
| 5.2 | Comparison script: text on each original page against the regenerated page | Sonnet | List of missing and extra texts per page |
| 5.3 | Fix the differences found | Sonnet, small fixes in main session | No missing text apart from agreed corrections |
| 6.1 | Edge cases from M5; decide whether long circuits should wrap | Opus decides, Sonnet builds | Logged in decisions.md |
| 6.2 | Golden files for all four real pages; tests complete | Sonnet | `pytest -q` green |
| 6.3 | docs/user-guide.md with every kind and field | Sonnet | A new example written only from the guide builds |

Every milestone closes the same way: tests pass, an agent that has not seen the work reviews it, the owner sees the PDF and approves, then one commit and an update of docs/progress.md.

| Milestone | Done when |
| --- | --- |
| M1 Skeleton | The example file loads, a broken file gives a clear error, and the PDF route is proven on Windows |
| M2 Symbols | The owner has approved the symbol sheet |
| M3 One page | Page 1 of the real case is drawn correctly from a hand-typed excerpt |
| M4 Multi-page | A multi-page example prints cleanly on A4 with working page links |
| M5 Real case | Side by side, the four new pages carry the same information as the originals |
| M6 Hardening | Tests pass and the guide lets a new user draw their own installation |

## Test plan

Seven kinds of test, each tied to the milestone that introduces it. A milestone is accepted when its tests pass, the review agent has reported and the owner has approved the PDF.

| Test | What it proves | How | From |
| --- | --- | --- | --- |
| Validation | Missing fields, duplicate IDs, unknown kinds, unknown keys and unknown pages are refused | Broken YAML files in tests/data; assert the message names the element ID | M1 |
| Command line | Exit codes and messages are right | Run the command in a subprocess | M1 |
| Symbols | Every symbol stays inside its bounding box and has its connection points | One parametrised test over the symbol list | M2 |
| Layout | Rows sit at the row pitch, text boxes on a page do not overlap, overflow raises an error | Assertions on the primitive lists, with no SVG involved | M3 |
| Rendering | SVG is well-formed, A4 sized and byte-identical for identical input | Golden files in tests/golden | M3 |
| Export | The PDF has the expected page count, A4 pages of 595 x 842 pt and extractable text | Read the PDF back with pypdf | M4 |
| Real case | Every text on an original page appears on the regenerated page | Script comparing the two sets of text, with an allow-list for agreed corrections | M5 |

Golden files change only on purpose: a test run never rewrites them, and a new golden file is committed only after the owner has approved the page it shows. Tests run quietly, showing failures and the summary line.

## Risks and fallbacks

Ten risks, ordered by how early they can bite.

| Risk | First sign | Fallback |
| --- | --- | --- |
| SVG to PDF conversion behaves differently on Windows, or mangles text or arcs | Task 1.2 gives a wrong page | Add a renderer that draws the six primitives straight into a PDF with ReportLab; SVG stays as a second output |
| Fonts differ between machines and shift text | Golden tests fail on another PC | Use only the built-in PDF font Helvetica and compute text widths from ReportLab's metrics |
| Field names change after YAML has been typed | Rework of examples and tests | Task 1.3 fixes the names before any model code; later changes go through the decision log |
| Symbols from separate small tasks look uneven | The symbol sheet has mixed line weights or sizes | symbol-notes.md fixes grid and line widths up front; one Sonnet pass to even them out |
| The square-with-triangle symbol stays unidentified | Owner cannot name it | Draw it as in the original under a neutral name and rename it later |
| Golden files churn while layout is tuned | Each tweak breaks many tests | Keep golden files to the minimal example until M5; add the real pages in task 6.2 |
| Slips in the original make "same information" unclear | Task 5.2 reports differences that are corrections | The open points under Existing diagram are answered before M5 and feed the allow-list |
| A typed page overflows as the installation grows | Build error naming the page | The owner moves a subtree with `page`; automatic flow stays out of scope |
| The YAML nests too deep to type comfortably | Indentation mistakes while typing the real case | Consider a flat form in M6, with circuits listed at top level and a `parent` field |
| Usage limits are hit mid-milestone | Limit warning | Stop at a task boundary, update docs/progress.md and continue in the next window |

## Out of scope and what to bring

Version 1 leaves out the position plan, panel layout, material list, automatic circuit assignment, AREI rule checking, Excel input, automatic page flow and any graphical interface.

Put these in the repository before the first coding session:

- [ ] CLAUDE.md in the root
- [ ] This plan, exported as docs/handoff-plan.md
- [ ] The four original SVG pages in docs/reference/
- [ ] AREI reference drawings for the symbols, if you have them
- [ ] A choice of where the code lives: a new GitHub repository or a local folder

Three answers are needed from the owner, the first before M1 and the others before M5:

- [ ] Confirm that pages are typed in the YAML and never flow automatically.
- [ ] Answer the open points under Existing diagram: copy or correct each slip.
- [ ] Name the square-with-triangle symbol and the grey marks above the cables.

## Handoff prompt

Paste this as the first message of the coding session. The way of working is in CLAUDE.md, so the prompt only points to the two documents and starts M1.

```markdown
Read CLAUDE.md, docs/handoff-plan.md and docs/plan-review.md first.
CLAUDE.md is how we work; the plan is what we build; the review and
docs/decisions.md amend the plan and win where they differ.

Build "huiselek" as the plan describes. Start with milestone M1 only: give
me your short plan for M1 and wait for my go.

The four original pages are in docs/reference/. They are large, so do not
read them whole. Use the inventory and measurements in the plan, and
docs/symbol-notes.md once task 2.2 has written it.
```
