# Decision log

One entry per decision: date, decision, alternatives considered, reason.

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
