# Huis Elek – Scope & Requirements

11 October 2026 · Owner

> Background only. This describes the full Huis Elek idea. Version 1, the single-line generator, is defined in docs/handoff-plan.md, and that plan wins wherever the two differ.

## Purpose

Huis Elek turns a floor plan and a room-by-room device list into a complete, AREI-compliant electrical dossier for a Belgian house. One shared data model drives all four outputs, so a change made once shows up everywhere.

The dossier must be good enough to hand to an approved inspection body (erkend keuringsorganisme) for the conformity check of a household installation. AREI Book 1 requires the single-line diagram and the position plan in the installation dossier, and inspectors record their absence as an infringement.

## Scope

Version 1 covers new or fully renewed household installations (huishoudelijke installaties) under AREI Book 1, for a single dwelling fed from one grid connection.

| In scope | Out of scope for version 1 |
| --- | --- |
| Single-family house or apartment, one main distribution board plus optional sub-boards | Non-household installations and common parts of apartment buildings |
| Single-phase 230 V and three-phase 3x230 V or 3x400 V+N connections | High voltage, and anything under AREI Book 2 or 3 |
| Lighting, sockets, fixed appliances, bathroom and outdoor circuits | Documenting existing pre-2020 installations under the derogations of Part 8 |
| Earthing and equipotential bonding shown on the diagrams | Cable and short-circuit calculation reports |
| EV charger, solar PV and home battery as optional modules (phase 2) | Home automation programming, data and audio cabling design |
| Dutch output, with French as a later option | Quotes, labour pricing and supplier ordering |

The tool produces documents. It does not replace the installer's responsibility or the inspection itself.

## Inputs

Two inputs are combined: the floor plan gives the geometry, the room and device list gives the electrical content.

| Input | Format | What the tool takes from it |
| --- | --- | --- |
| Floor plan file | PDF, DWG/DXF or image, one per floor | Scale, walls, doors, rooms and their areas, as the background for the position plan |
| Room and device list | Spreadsheet or form, one row per device | Room, device type, quantity, power, mounting height, switching relation, special needs |
| Project data | Form | Address, owner, installer, grid connection type, main fuse rating, earthing system |

The device list is the leading source. Where the plan and the list disagree, the tool reports the conflict and asks, it does not guess.

## Outputs

Four deliverables come from the same model, each printable as PDF and exportable as editable data.

| Output | Dutch name | Must contain |
| --- | --- | --- |
| Single-line diagram | Eendraadschema | Grid connection, main and additional differentials, every circuit with breaker rating, poles, cable type and cross-section, connected devices by symbol and count, earthing |
| Position plan | Situatieschema / situatieplan | Each floor to scale with boards, sockets, light points, switches, fixed appliances and junction boxes, each tagged with its circuit ID |
| Panel layout | Verdeelbord | Rows and module positions of every component, total module count, spare capacity, circuit labels for the board |
| Material list | Materiaallijst | Components per board, devices per type, cable lengths per type and cross-section, with quantities |

Both diagrams carry a title block with address, installer, date, version and a signature field. Inspection reports state that the diagrams were dated and signed.

## Functional requirements

The tool runs as a pipeline: import, build the model, assign circuits, check the rules, generate the outputs.

| ID | Requirement | Priority |
| --- | --- | --- |
| F1 | Import a floor plan per floor and set its scale from one known dimension | Must |
| F2 | Define rooms with name, type (dry, bathroom, kitchen, outdoor, technical) and area | Must |
| F3 | Import the room and device list from a spreadsheet template and validate every row | Must |
| F4 | Place each device on the plan, by hand or by auto-placement that the user can correct | Must |
| F5 | Group devices into circuits automatically, by room, type and load | Must |
| F6 | Give dedicated circuits to fixed appliances such as oven, hob, washing machine, dryer, dishwasher and boiler | Must |
| F7 | Select breaker rating, cable type and cross-section per circuit from the rule set | Must |
| F8 | Assign circuits to differentials and balance loads across phases on three-phase connections | Must |
| F9 | Run all compliance checks and list every violation with the device, the circuit and the rule it breaks | Must |
| F10 | Let the user override any automatic choice, then re-check | Must |
| F11 | Generate the four outputs with identical IDs and labels | Must |
| F12 | Estimate cable lengths from plan routes plus a configurable margin | Should |
| F13 | Keep versions of a project and show what changed between two versions | Should |
| F14 | Export PDF for print, DXF or SVG for drawings, XLSX or CSV for lists | Should |
| F15 | Read rooms and walls from the plan automatically | Could |
| F16 | Add EV charger, solar PV and battery modules | Could |

## AREI compliance requirements

Rules live in a separate, versioned rule set, not in the code, because Book 1 has been amended at least twice since 2020 and reportedly again in 2026.

| ID | Requirement |
| --- | --- |
| C1 | Every rule is a data record with a value, the Book 1 article it comes from, and the date it took effect |
| C2 | Every project stores the rule set version it was checked against |
| C3 | A violation blocks the final export unless the user records a reason for the override |
| C4 | The rule set is reviewed by a qualified installer or inspection body before first use |
| C5 | Symbols on both diagrams follow the standard symbols that inspection bodies accept |

The starter rule set below comes from secondary sources and inspection reports. Each value must be confirmed against the consolidated Book 1 text before it goes live.

| Rule | Starter value | Status |
| --- | --- | --- |
| General differential at the start of the installation | Max 300 mA, sealable input terminals | Consistent across sources |
| Additional differential for bathrooms and wet appliances | Max 30 mA | Consistent across sources |
| 30 mA protection for general-use sockets | Required since the 2023 amendment | Forum source only, confirm |
| Final circuits behind one 30 mA differential | Max 8 | Sources conflict, confirm |
| Sockets per circuit | Max 8, single or multiple | Consistent across sources |
| Mixed circuit of sockets and lights | Each light point counts as a socket, 2.5 mm² throughout | Consistent across sources |
| Socket circuit protection | Max 20 A on 2.5 mm² | Secondary source, confirm |
| Lighting circuit protection | Max 16 A on 1.5 mm² | Secondary source, confirm |
| Differential type | Type AC not allowed | Seen in an inspection report |
| Earth electrode resistance | Max 30 ohm as the standard case | Seen in an inspection report |
| Bathroom volumes and sockets | Rules changed on 1 March 2025 | Details to take from Book 1 |
| Board labelling | Every circuit clearly marked on the board | Seen in inspection reports |

Amendments to track: royal decree of 5 March 2023 (in force 1 June 2023), royal decree of 3 October 2024 (in force 1 March 2025), and a reported royal decree of 6 October 2025 (in force 1 April 2026) that extends the rules to DC installations such as PV, batteries and chargers. The last one is from a single non-official source and is not yet confirmed.

## Data reference model

Every object gets one stable ID that appears unchanged on the single-line diagram, the position plan, the panel layout and the material list.

| Entity | Example ID | Key fields | Belongs to |
| --- | --- | --- | --- |
| Project | P-001 | Address, owner, installer, connection type, rule set version | none |
| Floor | F0, F1 | Name, plan file, scale | Project |
| Room | R-0.03 | Name, type, area, bathroom volumes | Floor |
| Board | B1 | Location, rows, modules per row | Room |
| Protective device | B1-Q3 | Kind, rating, poles, curve, sensitivity, modules, row and position | Board |
| Circuit | A, B, C | Type, breaker, differential, cable, phase, design load | Protective device |
| Cable | W-A | Type, cores, cross-section, estimated length | Circuit |
| Device | A3 | Type, symbol, power, height, x and y on plan, IP rating | Circuit and Room |
| Switching link | S-A3-A4 | Which switch controls which light points | Devices |
| Catalogue item | K-0142 | Description, brand, article number, unit | Used by devices, cables, protective devices |

Circuit letters with numbered points (A1, A2, A3) follow common Belgian practice, so the labels on paper match the labels on the board.

## Non-functional requirements

| ID | Requirement |
| --- | --- |
| N1 | The same inputs and rule set version always give the same outputs |
| N2 | Every value on an output traces back to one model record |
| N3 | Drawings stay legible when printed on A4 and A3 |
| N4 | A full regeneration of a typical house (about 150 devices) takes under 30 seconds |
| N5 | Project data is stored in an open, readable format such as JSON |
| N6 | The interface is in Dutch, with all labels held in a translation file |
| N7 | Personal data is limited to the names and address needed on the title block |

## Assumptions and open questions

These assumptions were made to write this draft: new household installations only, one dwelling per project, Dutch output, and the device list wins over the plan.

Seven questions decide the design and should be answered before the architecture phase.

- [ ] Who uses the tool: you for your own house, or installers for many projects?
- [ ] Is it a desktop tool, a web app, or a script that runs on files?
- [ ] Which floor plan format do you actually have: vector PDF, DWG or a scan?
- [ ] Must the tool place devices on the plan itself, or do you place them and it draws the rest?
- [ ] Should the material list use a specific brand catalogue, such as Niko, Legrand or Hager?
- [ ] Are EV charger, solar PV and battery needed in version 1?
- [ ] Who confirms the rule set against the official Book 1 text?

## Sources

The official FOD Economie page could not be opened automatically, so the rule values above rest on the secondary sources below and need confirming.

- [Volta: AREI Book 1 annex with change history, 2025](https://volta-org.be/media/lizdradw/arei-bijlage-boek-1-installaties-op-laagspanning-en-op-zeer-lage-spanning-2025.pdf)
- [Forum for the Future: new AREI rules in force since 1 March 2025](https://blog.forumforthefuture.be/nl/article/algemeen-reglement-op-de-elektrische-installaties-focus-op-de-nieuwe-regels/26487)
- [Elektramat: what is the AREI, 2023 and 2024 amendments](https://www.elektramat.be/kennisbank/wat-is-het-arei)
- [Housing Service: AREI guide 2026, reported decree of 6 October 2025](https://www.housing-service.be/?p=1049)
- [Stad Gent: control sheet for household electrical installations](https://apidg.gent.be/supporting/dss-public/v1/sharedfiles/0da5d123-a2d9-4eaf-96cc-96d768094941)
- [E-Ctrl inspection report, May 2026: dossier, dated and signed diagrams](https://immo.notaris.be/immoplatform-public-service_v1/api/attachments/110833/298952/800037.pdf)
- [E-Ctrl inspection report, October 2025: infringement codes for missing diagrams](https://immo.notaris.be/immoplatform-public-service_v1/api/attachments/131078/297652/792390.pdf)
- [Inspection report: type AC differentials and 30 ohm earth limit](https://immo.notaire.be/immoplatform-public-service_v1/api/attachments/350777/295837/778641.pdf)
- [Volta: cable calculation article, household installations](https://volta-org.be/media/xoph2v23/de-kabelberekening-van-uitdaging-naar-uitkomst.pdf)
- [Circuits Online forum: 30 mA rules after the 2023 amendment](https://www.circuitsonline.net/forum/view/161578/1)
