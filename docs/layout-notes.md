# Layout notes

Task 3.1, 12 October 2026. Measurements of House A page 1, taken once from `docs/reference/houseA_eendraads_v1_00_pg1.svg` (transforms applied, only on-page elements), and the layout design built on them. Work from this file; do not reread the reference page.

All values are mm, origin top-left, y down. "Row y" is the y of a circuit's horizontal line.

## 1. Measurements, House A page 1

### Page and title block

| Item | Value |
| --- | --- |
| Frame | rect 0.5..209.7 x 0.4..297.1, stroke 0.8 |
| Title block | rect 0.25..209.86 x 276.6..297.3, stroke 0.5; middle line y 286.96; split x 105.06 |
| Title block text | size 4.23; x 3.9 (left cells), 108.9 (right cells); baselines 283.1 and 293.1 |
| Cells | row 1: page title, address; row 2: "Geteken door: …", "Uitgevoerd door: …" |
| Wires | stroke 0.2 |

### Supply chain (head)

| Item | Value |
| --- | --- |
| Supply box | rect 5.7..31.0 x 5.2..20.1, stroke 0.46; inner rect 8.3..20.0 x 6.4..8.8, stroke 0.38 |
| Supply texts | voltage "3*230 V" size 2.12 at (20.7, 8.4); label size 3.53 at x 8.1, baselines 13.2 and 17.6 (two lines) |
| Feed | vertical x 13.45 from box bottom 20.1 down to 31.05 |
| Level 1: main breaker 40 A | horizontal at y 31.05 from x 13.5; arm to 25.2; rating "40A" at (22.6, 28.6); label at (13.3, 38.3) |
| Return loop | right to x 32.94, down to y 43.61, left to x 13.4, down to y 57.1 |
| Level 2: 300 mA | horizontal at y 57.1 from x 13.4, ends 26.7; text "300 mA" / "4x40 A" at x 18.1, baselines 63.9 and 67.5; label at (13.2, 73.1); House A triangle mark at x 13.6..16.9 |
| Feeder to Diff 2 | junction x 34.57 on y 57.1, vertical down to 256.8, then right to 63.9 ("Naar Pg 2" / "Ref Diff 2" at x 43.1, baselines 247.9 and 251.5) |
| Diff 1 (30 mA) | horizontal from x 42.4, ends 55.7; texts at x 47.1, baselines 64.0, 67.6, 71.2 ("30 mA", "4x40 A", "Diff 1") |
| Bus of Diff 1 | x 63.53, from y 57.43 down to the 32 A row |

### Circuit row (offsets from the bus x 63.53 and the row y)

| Item | Offset x | Offset y | Note |
| --- | --- | --- | --- |
| Breaker | 0 .. 13.3 | 0 | stub to 6.1, arm 6.1..11.7; line resumes at 13.3 (x 76.85) |
| Rating text | 3.2 | −5.65 | size 2.88 |
| Grey marks (two "⊓") | 14.3 .. 23.8 | −2.5 | stroke 0.07; meaning open, not drawn |
| Conductor slashes (3) | 17.6 .. 19.1 | 0 | stroke 0.07 |
| Cable text | 14.4 | +2.3 | size 1.8 |
| First device stem | 34.76 | | x 98.29 |
| Device pitch | 7.66 | | 8 slots up to x 151.9 |
| Device stem | | 0 .. +3.9 | socket arc below, width 3.4 |
| Count / note ("2", "3ph") | stem + 0.6 | +3.6 | size 1.73 |
| Device ID | stem − 1.1 (start) | +9.0 | size 1.8 |
| Circuit letter | x 160.95 absolute | 0 | size 2.88 |
| Description | x 160.95 absolute | +3.6, +7.2 per line | size 2.88; wrapped by hand in the original |

Row y on page 1: 57.43 (I), 72.69 (J), 88.21 (K), 103.57 (32 A), 134.19 (N), 149.60 (L), 164.86 (M), 180.38 (O), 195.74 (P). Steps are 15.26 to 15.52: one pitch of 15.35, two pitches after the 32 A breaker.

### Lower devices on circuit K

- Light with switch mark K6: stem 0..+3.1, light centre about +4.7, circle diameter about 3.2.
- Photo detector K7 and K8: stem 0..+3.0, box +3.0..+6.3 (3.4 wide), stem +6.3..+9.4, light centre about +11, ID baseline +16.0.
- K8 sits in slot 8 (x 152.0). The 32 A row below it is not moved down; nothing of that row lies under x 140.

### Nested breaker 32 A (row 103.57)

- Breaker from the bus as in a circuit row. Rating "32A" at (72.9, 101.1); label "Hoofd auto 1" at (63.5, 110.8), below the breaker.
- Loop: right to x 83.17, down to y 116.13 (+12.56), left to the bus x, then the bus continues down at the same x to the last child row (180.38).
- Cable text "XVB 5x6" at (68.6, 118.5): under the return line, +5.0 from the bus. The conductor slashes are on the return line.
- The first child row (N) is at +30.62, two pitches.

### Branching circuit P (child of O)

- O's line runs on to x 113.6, which is O's third device slot (O has two devices).
- A vertical line drops from there to P's row (+15.36), and P's breaker starts at x 113.6.
- P's breaker, rating (117.7, 190.9) and cable text (128.0, 198.1) have the same offsets as a normal row, measured from x 113.6 instead of the bus.
- P3's stem is at about 146.8, so the offset is 33.2 against 34.76 in a normal row. The description stays at x 160.95.

### Library symbols against House A

| Symbol | Library size | House A | Scale |
| --- | --- | --- | --- |
| Breaker, differential (identical, as in the official table; the text tells them apart) | 10 along the line | arm about 6, 13.3 bus to line | 1.0 |
| Socket (child protection) | 4.01 wide | 3.4 wide | 0.85 |
| Light, light with switch | 4.0 diameter | about 3.2 | 0.8 |
| Photo detector | code-drawn from House A | | 1.0 |
| Conductors mark | 19 long, one slash | three short slashes | 1.0; the count is written beside the slash |

## 2. Design

### 2.1 Page structure

A page has a head at the top-left, then one or more buses, each a vertical line with one row per child.

**Head.** Starting at the root supply, follow the chain while each node has exactly one child on this page and that child is a breaker or a differential. The chain stops at its first differential, which becomes the last level. With this rule the 300 mA and Diff 1 share a row whether or not Diff 2 is on the page (clarified in task 3.4). Each node in the chain is a level, drawn horizontally from x 13.4:

- The supply box is at the top. Each level below it sits one loop lower (26.05: the return loop as measured).
- The last level is on the first row (y 57.4). If the chain is longer, the first row moves down with it.

The last level ends in one of two ways:

- **Group.** All its children are differentials, or breakers with children. The first child continues on the same row from x 42.4 and opens its own bus. Each further child hangs from a feeder line at x 34.57 and starts on the first free row below the previous bus. That child is drawn the same way: a horizontal device from x 42.4, then its own bus. A child moved to another page leaves a feeder end with a link; the links themselves are M4.
- **Bus.** Its children include circuits. It opens a bus at x 63.53 on its own row.

Mixed children (circuits next to differentials, House B's DIFF-ALG), reserves, boards, appliances and impulse relays raise the layout error `layout_unsupported` with the element ID until task 7.1 designs them.

**Bus.** The bus is a vertical line at bus x, from the owner's row down to its last child row. Each child is a row:

- A circuit takes one row, plus one row per branching circuit (2.4).
- A breaker with children (nested breaker, 2.3) takes two rows and continues the bus below itself. Nesting is recursive: a nested breaker under a nested breaker continues the bus again (rare, but allowed). At every level a nested breaker must be the last child of its bus; otherwise the build stops with `layout_unsupported`.

### 2.2 Rows and row height

- Rows sit on a fixed grid: row y = first row y + n x `row_pitch` (15.35). Owner, 12 October: no free distances between rows.
- The next row takes the next grid line. The nested breaker takes two grid lines.
- **Overlap rule:** if a symbol or text box of the new row overlaps a box already placed on the page, the row moves down by whole pitches until it is clear. Wires are left out of the check.
- On page 1 every row stays on its own grid line, because K7/K8 lie in an empty part of the next row. On page 2 the lower devices (F1/F2, H1) skip one grid line; the original's 31 mm step before G is about two pitches.
- Boxes come from `bbox()` in `primitives.py`. Text boxes use ReportLab's Helvetica `stringWidth`, an ascent of 0.72 x size and a descent of 0.21 x size, rotated with the text.

### 2.3 Nested breaker

As measured (section 1):

- Breaker from the bus, rating above, label below.
- Loop right to bus + 19.64, down `loop_drop` (12.56), back left to the bus.
- Cable text and conductor mark go under and on the return line, and the bus continues.
- Children start two grid lines below the breaker row. The same applies at deeper levels.

The same loop shape joins the head levels (with `head_loop_drop` 12.56 and `head_loop_x` 32.94).

### 2.4 Circuit row

All x offsets are from the row origin. The origin is the bus x, or the branch x for a branching circuit.

1. Breaker symbol on the line, rotated so terminal `a` faces the origin, from origin + 3.3 to + 13.3. The rating text comes from the `breaker` template.
2. The line runs from + 13.3 to the end x: the last device slot, or the branch x if the circuit has child circuits.
3. Conductors mark centred at + 18.5 if `conductors` is set, with the count beside the slash. Cable text at (+ 14.4, + 2.3), from `cable` as typed.
4. Device slot i has its stem at `origin + 34.76 + i * 7.66`.
   - Each end device hangs on a stem of `device_drop` 3.9.
   - The symbol is placed with point `in` on the stem end. Sockets are placed as they are; devices whose lead comes from the left are rotated 90°.
   - The ID is centred under the device at + 9.0 below the line, or below the lowest symbol of the slot.
   - A count above 1, and the `note`, go at the symbol's `label` point (or stem + 0.6, + 3.6), joined with a space when there are both.
5. Circuit letter (the circuit ID) at x 160.95 on the row line. Description at + 3.6 per line, wrapped at `description_width` (46). An explicit line break in the YAML is kept.
6. **Branching circuits** (circuit children of a circuit):
   - The parent's line runs on to its next free slot x, the branch x.
   - One vertical line drops from there.
   - Each child circuit is a row with origin = branch x, one row below the previous.
   - Its devices use the same offsets, so they start at branch x + 34.76.

### 2.5 Model to symbol

| Model | Symbol | Note |
| --- | --- | --- |
| breaker, circuit | `breaker` | text from template `breaker` |
| differential | `differential` | templates `differential`, `differential_type`; label below the texts |
| socket, variant v | `socket_<v>` | count > 1 written as the number, as in House A (not the `_n` symbol) |
| light | `light`, or `light_with_switch` when `switch` | |
| photo_detector | code-drawn `photo_detector`, child light below it in the same slot | more than one light: `layout_unsupported` for now |
| box | `box` | label as typed, centred one line below the ID |
| transformer, converter | `transformer`, `converter_ac_dc` | page 2, measured in M5 |
| supply | House A box, drawn in code | template `supply_voltage`; the kWh meter and the House B supply are task 7.1 |

### 2.6 Symbol scale

- `symbol_table.yaml` gets an optional `scale` per symbol (default 1.0). `symbols.py` applies it to geometry, points, size and text size.
- Values: sockets 0.85, lights 0.8, conductors mark 0.5 (at 1.0 its slash crosses the cable text; House A's slashes are about 1 mm tall), all others 1.0.
- The scale also applies on the M2 symbol sheet, so the sheet shows these symbols smaller than the official images. Shapes are unchanged.

### 2.7 Head texts and title block

- Differential texts start at the symbol origin + 4.7, below the line from + 6.8, one line per 3.6: template, type, label.
- Every breaker (circuit, nested, head level) puts its rating at the circuit-row offsets (+ 3.2, − 5.65) and its label below. House A placed the 40 A and 32 A ratings differently (section 1); one rule for all breakers was chosen in task 3.4.
- Title block as measured.
  - Row 1: page title, address. Row 2: drawn by, executed by.
  - Version, date and `extra` entries fill further rows of two cells, each 10.35 high. The block grows upward.
  - The content limit of the page is the top of the title block minus 3.
- Captions come from the `title_*` templates. The default reads "Getekend door:", which corrects House A's typo.

### 2.8 Overflow (task 3.5)

| Error | When | ID |
| --- | --- | --- |
| `too_many_devices` | the last device of a row ends past `description_x` − 2 | the circuit |
| `page_full` | a row or the feeder end passes the content limit | the page, with the element that did not fit |

### 2.9 Settings

All of the above values go into `Settings` as named fields: head, bus and row offsets, pitches, text sizes and wire stroke 0.2. The code holds no numbers except 0 and 1.

### 2.10 What M3 leaves out

- Page links and the Diff 2 feeder end (M4, task 4.1). The page 1 excerpt holds Diff 1 only.
- House A's grey marks (meaning open) and the differential triangle (AREI writes the text instead).
- Automatic wrapping of long circuits (task 6.1).
- A single word wider than its column (description, title cell, supply label) runs past the column without an error; task 6.1.
- The House B constructs (task 7.1).
