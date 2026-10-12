# Decision log

One entry per decision: date, decision, alternatives considered, reason.

## 2026-10-12 · Title block without signature field

- **Decision:** The title block has no signature field. It keeps spare cells for extra entries such as name and location, typed as `project.extra` (label and value pairs). Version and date are optional fields.
- **Alternatives:** An empty signature field, as inspection reports suggest.
- **Reason:** The owner's choice.

## 2026-10-12 · House A slips are corrected

- **Decision:** The House A YAML corrects the slips of the original. Task 5.1 lists every correction; the owner checks the list by hand, and it is the allow-list for the comparison in task 5.2.
- **Alternatives:** Copy the original as it is, slips included.
- **Reason:** The owner's choice; a manual check keeps the corrections visible.

## 2026-10-12 · Pages are typed, no automatic flow

- **Decision:** Pages are typed in the YAML with `page` and `children_page`. The tool never flows pages; an overfull page stops the build with an error naming the page and element. Automatic flow is kept as a possible later extension.
- **Alternatives:** Automatic page flow with page-break rules.
- **Reason:** Pages by content, as in House A; predictable output and page numbers; simpler code and tests.

## 2026-10-12 · Plan consolidated into version 2

- **Decision:** `docs/handoff-plan.md` version 2 merges the plan review and the decisions of 11 October; it is the single source for what we build. `docs/plan-review.md` is kept as history only.
- **Alternatives:** Keep the plan plus a review that amends it.
- **Reason:** Three documents that contradict each other in places cost the coding session tokens and invite mistakes.

## 2026-10-11 · Final acceptance test is House B

- **Decision:** The final acceptance test is the design overview `docs/testcase/house-b-overzicht-v4.md` (House B). House A stays the reference for symbols and layout style and the test case for M2 to M5.
- **Alternatives:** House A only, as in the original plan; House B replacing House A entirely.
- **Reason:** House B is the real target, but it has no existing drawing. House A is the only case with an original to compare against, so it stays the yardstick while symbols and layout are built.

## 2026-10-11 · House B lighting and control come later

- **Decision:** Lighting circuits 1 to 35 and the control system (push buttons, motion sensors, controller inputs) are in scope, but in a later milestone (M8), after the power circuits (M7).
- **Alternatives:** Include them in M7; leave them out of scope.
- **Reason:** The owner's choice. The circuit content is only in the source xlsx, and how the controller is drawn is not yet decided.

## 2026-10-11 · Milestone order

- **Decision:** M1–M5, then M7 (House B power), then M6 (hardening), then M8 (House B lighting and control).
- **Alternatives:** M6 before M7, as numbered.
- **Reason:** M6 writes the user guide and final tests; doing House B first means they cover its features and are not redone.

## 2026-10-11 · Open design values get one concrete value

- **Decision:** Where the design leaves a choice open, the test YAML holds one provisional value, marked with a YAML comment. Rating fields stay numeric.
- **Alternatives:** Free text such as "20 A / 32 A" in rating fields.
- **Reason:** Keeps fields typed and validation simple; a later decision changes one value.

## 2026-10-11 · Provisional values for House B

- **Decision:**
  - DIFF-ALG: 300 mA.
  - Circuit G (EV charging point): 3P+N 25 A, cable 5G4, its own 30 mA type A differential `D5` that shares with nothing. This assumes a wallbox with built-in 6 mA DC detection.
  - Circuit A cable: 5G2,5.
  - Bureaupunten in slaapkamer 2 and 3: sockets on circuit U. The light count drops from 72 to 70.
- **Alternatives:** 100 mA general differential; G at 20 A + 5G4 or 32 A + 5G6; G behind DIFF-ALG only; type B for G; bureaupunten as light points.
  - DIFF-TUIN: 30 mA type A, 40 A, as in the overview (confirmed). Poles: 4 (assumption: it is fed by J, 3P+N; to confirm).
  - DIFF-ALG: 300 mA type A, 40 A, 4-pole. It is also the main switch; there is no separate main breaker.
  - D1–D5: 30 mA type A, 4-pole, 40 A (assumption: the owner's "40 A" applies to these too; to confirm).
  - Earthing: not drawn in M7. The earthing design itself still has to be checked (owner action, outside the tool).
  - Surge protection: not drawn for now.
- **Reason:** The owner's choice. 32 A on 5G4 was rejected because 4 mm² is protected at no more than 25 A. A charging point without any 30 mA fails inspection (overview §4.1).

## 2026-10-11 · Appliances get their own AREI symbols

- **Decision:** Oven, dishwasher, washing machine, dryer, CV boiler, water heater and IR panel are separate device kinds, each drawn with its AREI symbol, which is mandatory. Hood, fridge and combi microwave stay plain sockets (assumption: the owner did not list them).
- **Alternatives:** Draw appliances as a socket with a note.
- **Reason:** AREI requires the appliance symbols. House A stays as typed (its washing machine and stove are drawn as sockets in the original).

## 2026-10-11 · Symbols come from the ShadowHunter AREI library

- **Decision:** Symbols are drawn from the AREI library in `docs/reference/arei/`. Where a 2023 version exists (only in the Visio stencils), it wins over the older SVG, in particular "Differentieel 2023". Visio is not available, so a script converts the needed 2023 shapes from `.vssx` to SVG. The CV boiler uses Verwarmingstoestel. The library's licence text stays in the repo.
- **Alternatives:** Redraw symbols from the House A pages (original plan); use only the older SVG set; export from Visio by hand.
- **Reason:** AREI symbols are mandatory for a dossier that goes to inspection, and House A's symbols are the owner's own drawing. The licence allows use and modification. No Visio licence.

## 2026-10-11 · Symbols generated from the library by a converter

- **Decision:** A converter turns library SVG into primitive data files per symbol, with a hand-written table for anchor and connection points. Only House A's own symbols are hand-coded.
- **Alternatives:** One hand-coded function per symbol from measurements (original plan).
- **Reason:** About 30 symbols; conversion is more faithful to the AREI shapes and needs far fewer briefs.

## 2026-10-11 · Official label formats for House B

- **Decision:** House B follows the label formats of AREI table 2.23 (`docs/reference/arei/official/notes.md`): breaker "C20", differential "40/0.3A" with "type A", cable as type, fire class and cores x section with a decimal point. Default breaker curve is C. House A keeps the texts of its original, because it is the comparison case.
- **Alternatives:** House A formats everywhere; official formats for both cases.
- **Reason:** The official table prescribes these formats; curve C is standard practice. Changing House A would break the M5 comparison with its original.

## 2026-10-11 · Cabling in House B

- **Decision:** Most House B circuits are VOB conductors in flexible plastic conduit (Elflex); cables are XVB. Circuit J is XVB 5G6 in a conduit (overview). Which other circuits are XVB, and the exact label for VOB, are open.
- **Alternatives:** XVB Cca for every circuit, as in the official examples.
- **Reason:** The owner's information on how the house is wired.

## 2026-10-11 · Only extracts of reference documents are committed

- **Decision:** Full reference documents (the 314-page AREI 2026 PDF) stay local and are ignored by git. Only extracts and notes are committed, such as `docs/reference/arei/official/`.
- **Alternatives:** Commit the full PDF (9.9 MB).
- **Reason:** The owner's choice; keeps the repository small.

## 2026-10-11 · Default socket variant

- **Decision:** Sockets default to "protective conductor with child protection". Other variants are typed explicitly.
- **Alternatives:** Protective conductor only as default.
- **Reason:** Sockets without child protection are rare in current installations.

## 2026-10-11 · Error messages in Dutch

- **Decision:** CLI and validation messages are in Dutch and live in `labels.py`. Code, comments, docs and commit messages stay in English. Tests check element ID and error code, not message text.
- **Alternatives:** English messages.
- **Reason:** Interface parts are Dutch, like the drawing. This extends the CLAUDE.md convention, which only named drawing text.

## 2026-10-11 · No phase field

- **Decision:** Circuits get no `phase` field.
- **Alternatives:** Optional L1/L2/L3 per circuit.
- **Reason:** Phases are rarely shown on a single-line diagram, and the distribution follows from the prefabricated busbars, so it is not chosen per circuit.

## 2026-10-11 · Field names are designed against both cases

- **Decision:** Task 1.3 fixes the YAML field names against House A and House B (power circuits) together. See `docs/plan-review.md`, section "House B needs".
- **Alternatives:** Fix names for House A only and extend later.
- **Reason:** Avoid renaming fields after examples and tests have been typed (plan risk "field names change").

## 2026-10-12 · Square-with-triangle is a photo detector

- **Decision:** The square-with-triangle symbol ahead of lights K7, K8 and H1 in House A is a photo detector that switches the light. It gets its own element kind (name fixed in task 1.3) and stays a code-drawn symbol as in the original, because AREI table 2.23 has no photo detector.
- **Alternatives:** A neutral placeholder name until identified (plan fallback); the AREI bewegingssensor symbol.
- **Reason:** The owner identified it. A motion sensor is a different device, so its symbol would misstate the installation.

## 2026-10-12 · Start the tool with python -m huiselek

- **Decision:** The documented way to start the tool is `python -m huiselek` (via `src/huiselek/__main__.py`). The `huiselek` console script stays in `pyproject.toml` for PCs that allow it. Tests and docs use the `-m` form.
- **Alternatives:** Allow the pip-generated `huiselek.exe` in Windows security; document both forms equally.
- **Reason:** Windows Application Control on the owner's PC blocks `.venv\Scripts\huiselek.exe` (task 1.1). `python.exe` is signed and runs; changing security settings is not wanted.

## 2026-10-12 · Dependency versions pinned

- **Decision:** PyYAML 6.0.3, pydantic 2.14.1, svglib 2.3.0, reportlab 5.0.1; dev: pytest 9.1.1, pypdf 6.20.0. Pinned with `==` in `pyproject.toml`.
- **Alternatives:** Version ranges.
- **Reason:** The newest versions that install from wheels on Python 3.14 under Windows (task 1.1); pinning keeps golden files stable.

## 2026-10-12 · PDF route proven on Windows

- **Decision:** Keep the route svglib to one ReportLab canvas. Task 1.2 converted two hand-written A4 SVG pages (user units in mm) with thin and dashed lines, fill, circle, arc, three text anchors, rotated text and the characters ² Ø é –. The PDF has two pages of 595.28 x 841.89 pt, extractable text in Helvetica, and the geometry is correct by eye.
- **Alternatives:** Draw primitives straight into the PDF with ReportLab (the fallback).
- **Reason:** Nothing failed and no SVG feature had to be avoided. One harmless side effect: `renderPDF.draw` adds an unused Times-Roman font resource.

## 2026-10-12 · Field names, kinds, error codes and label templates fixed (task 1.3)

- **Decision:** The input format, value rules, error codes and label template names in the plan's Input format section are fixed. Choices beyond plan version 2: a `photo_detector` kind holding the lights it switches; `page` and `link_text` only on containers, and `link_text` without a page move is an error; differential `type` is required (House A's original omits it; task 5.1 lists that as a correction); `poles` is text, one of 1P, 1P+N, 2P, 3P, 3P+N, 4P; fixed lists for curve and appliance type; node IDs and page IDs unique within their own set; every "Naar" link has one matching "Van" link. Naming is checked again for consistency at the end of M1.
- **Alternatives:** `poles` as a number 1 to 4, or only 1, 3 and 4; optional differential type; `page` on every node.
- **Reason:** Designed against House A and House B and for reuse on other houses. A number cannot tell 1P+N from 2P or 3P+N from 4P, and single-phase and 3x230 V installations need 2-pole devices.

## 2026-10-12 · Root page default, unused pages, file error name

- **Decision:** The root supply goes on the first page in `pages` unless it has `page`. A page that holds no node is an error (`unused_page`). Error code `file_not_found` is renamed `file_unreadable`. Light keeps `switch` (not `switched`).
- **Alternatives:** `page` required on the root; unused pages allowed (printed empty); keep `file_not_found`; rename `switch` to `switched`.
- **Reason:** Owner's choice after the M1 review. An empty sheet is always a mistake. The code also covers folders, unreadable and non-UTF-8 files. `switch` can grow from a yes/no into a switch kind in M8 without a rename.

## 2026-10-12 · pydantic for the data model

- **Decision:** The data model uses pydantic 2 classes with a discriminated union on `kind`, unknown keys forbidden, and a post-pass for parent/child rules, unique IDs and page references. Its error locations are mapped to element IDs and Dutch messages.
- **Alternatives:** Dataclasses with hand-written validation; cattrs.
- **Reason:** In the plan from the start; gives typed fields, defaults and unknown-key errors with little code. Logged at first use (M1 review).

## 2026-10-12 · Supply voltage is a typed network type

- **Decision:** `supply.voltage` is one of `230V` (single-phase, two conductors), `3x230V`, `3N400V`. The text on the drawing comes from the label template `supply_voltage`, so House A can keep "3*230 V".
- **Alternatives:** Free text (as in task 1.3); a separate `system` field next to free-text voltage.
- **Reason:** Owner's choice after the M1 review. Later tools such as the PLC design need the network type without parsing text; one field avoids two values that can contradict.

## 2026-10-12 · M2 scope adjustments

- **Decision:** (1) No difference list between the old SVG set and the 2023 set; every needed symbol comes from the 2023 stencils and is compared with the official table image on the sheet. (2) Scripts in `tools/` may use the development dependencies (pypdf extracts the official table images). (3) M8 symbols and installation mark symbols are converted in M2 and approved on the same sheet. (4) A minimal `export_pdf.py` is written in task 2.6 for the sheet; task 4.3 completes it.
- **Alternatives:** Keep the difference list; standard library only with a one-off extraction; convert M8 symbols in M8; a separate sheet export.
- **Reason:** Owner's choice; less work, one approval for all symbols, and the official table already checks the 2023 changes.

## 2026-10-12 · Installation marks in scope, later

- **Decision:** Installation marks (in wall, on wall, in conduit in wall) are in scope for the tool, in a later milestone. Their symbols are converted in M2; the model field and layout come later.
- **Alternatives:** Out of version 1 (plan version 2).
- **Reason:** Owner's choice; they belong on a complete single-line diagram.

## 2026-10-12 · Symbol conversion rules: the official image wins

- **Decision:** Library symbols are converted with per-symbol table fields: `rotate` and `mirror` to match the orientation of the official image, `keep_text` to keep only text that is part of the symbol (placeholders such as "20A" or "XVB Cca 3G2.5²" are dropped; the layout writes values), `drop` to remove library geometry the official image lacks (the count slash on installation marks), `text_at` to place kept text as in the official image. Line widths are not stored; symbols use `symbol_stroke_mm` (0.26, the House A value). Both converters come from the library's "AC → DC" master, which is really DC → AC (input top-left); AC → DC is the same master rotated 180°. The library's "DC → AC" master is broken and unused.
- **Alternatives:** Use library masters unchanged; redraw differing symbols by hand.
- **Reason:** AREI table 2.23 is the ground truth; the differences are in the library, and small general options fix them without hand-drawn geometry.

## 2026-10-12 · Symbol connection points

- **Decision:** Every symbol has named points and an anchor in `symbol_table.yaml`: `a`/`b` for two-terminal devices on a line, `in` (and `out` for the transformer) for end devices, `center` for marks placed on a cable, `label` beside socket stems for the count. `Symbol.place(x, y, rotation)` puts the anchor on (x, y) with rotation 0/90/180/270 clockwise. Sizes stay at library scale until M3 (optional `scale` field). Socket ids follow the model variants (`socket_protective_conductor`). The model gets appliance type `general` (vast elektrisch huishoudtoestel).
- **Alternatives:** Points computed in the layout per symbol; Haiku-batched point entry (plan); scale fixed now.
- **Reason:** One table keeps symbol geometry knowledge out of the layout. Points need judgement and checking against geometry, so one Sonnet task did table and loader together. Scale depends on the layout, measured in M3.

## 2026-10-12 · Symbol review sheet via image overlays

- **Decision:** `symbol_sheet.py` (a twelfth module) builds the sheet as pages of primitives; official images and library SVGs are drawn by `export_pdf` as overlays on the same canvas (`export_pdf(svgs, out, overlays=None)`). The sheet reads `docs/reference/arei` from the repository and fails with one Dutch line (`reference_missing`) when that is absent, as in an installed package. Helper scripts `tools/contact_sheet.py` and `tools/symbol_points.py` are kept as development aids.
- **Alternatives:** `<image>` elements inside the SVG; drawing the whole sheet directly with ReportLab.
- **Reason:** svglib refuses absolute image references. Overlays keep the sheet's own content on our SVG route and keep the sheet module free of PDF code.

## 2026-10-12 · Symbol names, waterproof socket, phase marks (sheet review)

- **Decision:** (1) Symbol names on the sheet and in labels use the wording of AREI table 2.23 where the table has the symbol; our own names only for symbols it lacks (photo detector, page link, domotica parts, n-count sockets). (2) A waterproof socket with protective conductor and child protection (bar, feet and "h") is added; it is what `variant: waterproof` draws, the current default for waterproof sockets. The table's plain waterproof socket becomes `variant: waterproof_plain`. (3) The 1~ and 3~ marks use the official arc shape (half circle up, half circle down) instead of the library's sine. (4) The impulse relay's contact marks move up, closer to the official image. Photo detector and page link are approved as measured from House A.
- **Alternatives:** Library names; plain waterproof socket as `waterproof`; keep the library's sine wave and mark positions.
- **Reason:** Owner's review of the symbol sheet; the sheet is approved with these changes.

## 2026-10-12 · Layout design for one page (task 3.1)

- **Decision:** The layout follows `docs/layout-notes.md`.
  - Rows sit on a fixed grid of 15.35 mm. A row that would overlap placed symbols or text moves down by whole pitches.
  - The chain from the supply is drawn as horizontal head levels joined by House A's return loop. Sibling differentials hang from a feeder at x 34.57. A differential with circuits opens a bus at x 63.53.
  - A nested breaker takes two grid lines and continues the bus below itself. Nesting is recursive; at each level it must be the last child of its bus.
  - A branching circuit hangs from its parent's next free device slot.
  - Symbols get an optional `scale` (sockets 0.85, lights 0.8).
  - The differential is drawn with the same AREI switch as the breaker and told apart by its text, as in the official table; House A's triangle is not drawn.
  - New layout errors: `layout_unsupported` (constructs left for task 7.1), `too_many_devices`, `page_full`.
  - The title block grows upward for version, date and extra entries.
- **Alternatives:** Free row height (pitch or content, or 0.5 mm steps); a nested breaker with an indented bus; House A's symbol sizes and triangle.
- **Reason:** Owner's choice of fixed pitches. The rules reproduce the measured page 1 and keep the design general enough for other houses, while the House B constructs wait for task 7.1.

## 2026-10-12 · M3 adjustments after building and review

- **Decision:**
  - The conductors mark is drawn at scale 0.5.
  - All breaker ratings use the circuit-row offsets, also for head levels and nested breakers.
  - A box label goes one line below its ID.
  - The head chain stops at its first differential.
  - A malformed label template is a Dutch one-line error (`invalid_template`).
  - Words wider than their column are left for task 6.1.
- **Alternatives:** Scale 1.0, whose slash crosses the cable text; House A's own rating positions per breaker; the label beside the ID; checking word widths now.
- **Reason:** The page renders legibly and matches the original's information. One rule is simpler than per-case House A positions. The independent review found the template crash.

## 2026-10-12 · Visual design proposals are welcome

- **Decision:** Proposals that improve the look of the drawing beyond House A's original are welcome. They are collected and proposed after M5, when the House A text comparison is done, or with task 7.1 for House B constructs. Each one is a change to settings or templates, approved by the owner on one rendered page, and it updates the golden files on purpose.
- **Alternatives:** Stay strictly with House A's look; change the look during M4/M5.
- **Reason:** The owner's wish (M3 approval). Changing the look before M5 would mix layout changes into the House A comparison.

## 2026-10-12 · Layout design for pages 2 to 4 (M4)

- **Decision:** The design follows `docs/layout-notes.md` section 4.
  - Every page has one root; a second root on a page is `layout_unsupported` for now.
  - One rule for every Naar end: arrow pointing right, texts after the tip (House A page 1 put them above the line). The Diff 2 feeder end stays at House A's distance above the title block.
  - A Van arrow on every target page, also on the detail pages where House A has none.
  - Detail rows use a code-drawn `switch_contact` (House A's open blade), not AREI's wall `switch`. Detail lights keep scale 0.8 (House A: 5.24 mm).
  - Page numbers ("Pagina {number} van {total}") right-aligned in the page-title cell; House A titles drop their "Pagina n:" prefix.
  - Links are clickable in the PDF.
  - The M4 example is House A pages 1 to 4 without circuit F (transformer and converter wait for M5).
  - A circuit with `children_page` has no devices on its own page.
- **Alternatives:** House A's positions per link; no arrow on detail pages; the AREI wall switch; House A's light size on detail pages; no page numbers; plain (non-clickable) links; a reduced example.
- **Reason:** Owner's choice (M4 plan and design approval). One rule per construct keeps the layout general; the look stays House A's until the visual design proposals after M5.

## 2026-10-12 · M4 adjustments after review

- **Decision:**
  - The layout checks after all pages that every Van has its Naar; a moved node in a place without a drawn Naar is `layout_unsupported` (variant `link`). Two moved siblings under one element are `layout_unsupported` too.
  - `children_page` equal to the circuit's own page is an error (`unknown_page`, variant `own_page`); no new error code.
  - The detail-row text is the label template `detail_row` ("{id} {name}").
  - The PDF title "Eendraadschema" lives in `labels.py`; the code-drawn `switch_contact` keeps its measured values in code, like `page_link` and `photo_detector`.
  - The page title is not checked against the page number's width; task 6.1 checks word widths.
- **Alternatives:** Draw a Naar end in every position now; a new error code; a hard-coded detail format; symbol values in settings.
- **Reason:** The independent review found one-sided links in tree positions House A does not use. An error keeps the pairing rule true until those positions are designed; the House A output is unchanged.

## 2026-10-12 · Installation marks on cables moved into M4; page number in its own cell

- **Decision:**
  - Circuits and breakers with a cable get an optional field `mounting`: `in_wall`, `on_wall`, `in_conduit`, `in_conduit_in_wall`. Its AREI mark is drawn on the cable where House A has its grey marks (+14.3 to +23.8 from the row origin). No default: without the field, no mark. House A's grey "⊓⊓" marks are the "in de wand" mark.
  - The page number gets its own cell at the right end of the title block, about 32 mm wide, spanning the two base rows; the address and executed-by cells get shorter.
- **Alternatives:** Marks in a later milestone (decision of 11 October); a separate task after M4; the page number split from the title cell or in its own row.
- **Reason:** Owner's review of M4: the marks belong on the drawing now, and the page number should not share the title cell. This departs from the plan (input format change during M4).
