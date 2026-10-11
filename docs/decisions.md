# Decision log

One entry per decision: date, decision, alternatives considered, reason.

## 2026-10-11 · Final acceptance test is House B

- **Decision:** The final acceptance test is the design overview `docs/testcase/house-b-overzicht-v4.md` (House B). House A stays the reference for symbols and layout style and the test case for M2 to M5.
- **Alternatives:** House A only, as in the original plan; House B replacing House A entirely.
- **Reason:** House B is the real target, but it has no existing drawing. House A is the only case with an original to compare against, so it stays the yardstick while symbols and layout are built.

## 2026-10-11 · House B lighting and control come later

- **Decision:** Lighting circuits 1 to 35 and the control system (push buttons, motion sensors, controller inputs) are in scope, but in a later milestone (M8), after the power circuits (M7).
- **Alternatives:** Include them in M7; leave them out of scope.
- **Reason:** The owner's choice. The circuit content is only in the source xlsx, and how the controller is drawn is not yet decided.

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
- **Reason:** The owner's choice. 32 A on 5G4 was rejected because 4 mm² is protected at no more than 25 A. A charging point without any 30 mA fails inspection (overview §4.1).

## 2026-10-11 · Field names are designed against both cases

- **Decision:** Task 1.3 fixes the YAML field names against House A and House B (power circuits) together. See `docs/plan-review.md`, section "House B needs".
- **Alternatives:** Fix names for House A only and extend later.
- **Reason:** Avoid renaming fields after examples and tests have been typed (plan risk "field names change").
