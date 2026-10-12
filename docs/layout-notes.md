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
| Grey marks (two "⊓") | 14.3 .. 23.8 | −2.5 | stroke 0.07; "in de wand" mark, drawn since M4 (4.8) |
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
3. Conductors mark centred at + 18.5 if `conductors` is set, with the count beside the slash (above the marks when `mounting` is set). Installation mark from `mounting` (4.8). Cable text at (+ 14.4, + 2.3), from `cable` as typed.
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
- Values: sockets 0.85, lights 0.8, conductors mark 0.5 (at 1.0 its slash crosses the cable text; House A's slashes are about 1 mm tall), installation marks (`line_*`) 0.83 (4.8), all others 1.0.
- The scale also applies on the M2 symbol sheet, so the sheet shows these symbols smaller than the official images. Shapes are unchanged.

### 2.7 Head texts and title block

- Differential texts start at the symbol origin + 4.7, below the line from + 6.8, one line per 3.6: template, type, label.
- Every breaker (circuit, nested, head level) puts its rating at the circuit-row offsets (+ 3.2, − 5.65) and its label below. House A placed the 40 A and 32 A ratings differently (section 1); one rule for all breakers was chosen in task 3.4.
- Title block as measured.
  - Row 1: page title, address. Row 2: drawn by, executed by. The page number has its own cell at the right end of these two rows (4.5).
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

## 3. Measurements, House A pages 2 to 4

Measured once in task 4.0 on 12 October 2026 by script (transforms applied, only on-page elements) from `docs/reference/houseA_eendraads_v1_00_pg2.svg`, `_pg3.svg` and `_pg4.svg`. Work from this section; do not reread the reference pages. Same conventions as section 1: mm, origin top-left, y down. "Row y" is the y where the row's stub leaves the bus (the junction). Many wires are skewed: the right end lies 0.1 to 0.3 higher than the junction (e.g. row A 57.43 to 57.28); treat that as drawing noise, not a rule. Arrows are SVG markers (Inkscape Arrow2): about 2.04 long and 1.49 high.

### Page 2: page frame

| Item | Value |
| --- | --- |
| Frame, title block | as page 1 (frame 0.49..209.71 x 0.40..297.10) |
| Title block texts | same cells and positions as page 1; the page title cell still reads "Pagina 1: aansluiting" (copy of page 1, not updated). No other page number |

### Page 2: Van link and Diff 2 head

| Item | Value |
| --- | --- |
| Van line | horizontal at y 57.12, from x 8.66 to 42.42 (33.76), stroke 0.2 |
| Van arrow | at the left end x 8.66; points right, into the page (toward Diff 2). Body x 6.99..9.04, tip at 9.04, 0.38 beyond the line end |
| Van text | "Van pg 1", one line, size 2.88, start (9.23, 53.98): 0.57 right of the line end, baseline 3.14 above the line |
| Diff 2 | horizontal at y 57.12 from x 42.42: stub to 48.55 (+6.13), arm to (54.16, 60.36) (+11.74, +3.24), black rect 2.84 x 2.17 at x 51.36..54.20, y 59.06..61.23; line resumes at x 55.67 (+13.25) on y 57.43 and runs to the bus. Same shape as page 1 Diff 1 |
| Diff 2 slashes | 4 grey slashes (stroke 0.07, about 0.7 x 1.0) at x 49.0..51.2, y 57.2..59.2 |
| Diff 2 texts | start x 47.09; baselines 63.95, 67.55, 71.15 ("30 mA", "4x40 A", "Diff 2"); size 2.88 |
| Triangle mark | outline, stroke 0.2, base x 43.01..46.31 at y 64.67, apex (44.66, 61.81): 3.3 wide, 2.86 high, +0.6 from the Diff start, below the line |
| Bus | x 63.53; top 57.43 (row A), bottom 180.43 (row H). The Diff 2 row is row A: no extra row for the head |

### Page 2: circuit rows

| Row | Junction y | Step | Grid (pitch 15.375) | Letter baseline (dy) | Lowest symbol (dy) | ID baseline (dy) |
| --- | --- | --- | --- | --- | --- | --- |
| A | 57.43 | | 0 | -0.43 | (link only) | |
| B | 72.85 | 15.42 | 1 | -0.44 | +5.6 | +9.04 |
| C | 88.21 | 15.36 | 2 | +0.01 | +5.6 (C9 box +8.0) | +9.1 |
| D | 103.62 | 15.41 | 3 | -0.15 | +5.6 | +9.15 |
| E | 118.93 | 15.31 | 4 | -0.43 | +5.6 | +9.0 |
| F | 134.40 | 15.47 | 5 | -0.11 | +7.8 | +10.6 |
| G | 165.17 | 30.77 | 7 | -0.44 | (link only) | |
| H | 180.43 | 15.26 | 8 | -0.11 | +12.4 (light) | +15.87 |

- Pitch over the whole page: (180.43 - 57.43) / 8 = 15.375. Every row lies within 0.02 of a grid line.
- G sits two pitches below F (F1/F2 reach +10.6, so one grid line is skipped). H is one pitch below G and has the tallest lower device; nothing lies under it.
- Letter: x 160.32..161.05 (hand placed, page 1: 160.95), size 2.88; description lines at +3.6 from the letter baseline.
- Rating text: rows A..D at bus +4.1, dy -4.87; rows E..H at bus +3.1..3.3, dy -5.65 (hand placed; page 1: +3.2, -5.65). Size 2.88.
- Cable text: bus +14.3..14.5 (C and D: +16.2, +16.3), dy +2.3..2.4, size 1.8. Same as page 1.
- Breaker (stub, arm, black rect, line resumes at +13.3): same as the page 1 circuit row.
- Device slots: stem x = bus + 34.76..34.86 (98.29..98.39), then pitch 7.66 (one slot is +7.78). Count labels size 1.73 at stem +0.6, dy +3.0..3.3. Device IDs size 1.8 at stem -1.0..-1.2, dy +9.0..9.2.

### Page 2: Naar links (circuits A and G)

| Item | Circuit A ("Naar Pg 3") | Circuit G ("Naar Pg 4") |
| --- | --- | --- |
| Row y | 57.43 | 165.17 |
| Circuit line | from the breaker (x 76.95) to x 106.25; right end y 57.28 | to x 106.05; right end y 165.06 |
| End x | bus + 42.7, slot 2 (stem x 106.05) | bus + 42.5, slot 2 |
| Arrow | at the line end, points right (away from the circuit, toward the other page); body x 104.58..106.62, tip 0.37 beyond the line end | points right; body x 105.67..107.72, tip 1.67 beyond the line end (another Arrow2 variant, so 1.1 further right) |
| Text | "Naar Pg 3", one line, size 2.88, start (112.70, 58.16): line end + 6.45, baseline row y + 0.73 | "Naar Pg 4", start (112.49, 165.94): line end + 6.44, baseline row y + 0.77 |
| Rest of the row | rating "16A", cable "XVB 3x1.5", letter "A", description "lichtkring / gelijkvloers" | rating "16A", cable "XVB 3x2.5", letter "G", description "verlichting 2de Verdiep" |

- The text x is the ID x of slot 3 (stem 113.70 - 1.0). Neither row has devices.
- Circuit H is not linked: it has its own light H1 (below).

### Page 2: lower devices

| Item | Value |
| --- | --- |
| F1 transformer | stem at x 98.29, y +0 .. +2.81. Two circles r 1.55, centres +4.36 and +6.28 (1.92 apart, overlapping), lowest point +7.83. ID "F1" at (97.27, row + 10.63), size 1.8 |
| F2 converter | stem at x 106.05, +0 .. +2.81. Box 5.0 x 5.0 at x 103.55..108.55, y +2.81 .. +7.81. Inside: a diagonal from bottom-left to top-right; above it a small wave (x 104.07..106.14, y +3.85); below it a solid line (x 105.71..107.88, y +6.43) and a dashed line (x 105.68..107.88, y +7.16, dash 0.6/0.2). ID "F2" at (104.91, row + 10.59) |
| H1 photo detector | stem x 106.05, +0 .. +2.87. Box 3.43 wide x 3.30 high at x 104.33..107.76, y +2.87 .. +6.17; inside a triangle (apex top centre, base on the bottom edge) plus a small chevron from the apex to the side midpoints. Stem on to +9.25 |
| H1 light | centre (106.14, row + 10.86), circle r 1.55 (diameter 3.1), cross +/-0.81. ID "H1" at (105.03, row + 15.87), size 1.8 |

Same offsets as K7/K8 on page 1 (box +3.0..+6.3, light about +11, ID +16.0).

### Pages 3 and 4: link, header, bus

| Item | Page 3 (circuit A) | Page 4 (circuit G) |
| --- | --- | --- |
| Link line | y 57.43, x 56.88 .. 71.48 (14.6), stroke 0.2 | y 57.33, x 56.88 .. 71.48 |
| Arrow | none: the stored page has no marker on the page (the Arrow2 markers in the file belong to off-page copies) | none |
| Link text | "Van Pagina 2" size 2.86 at (62.82, 49.79); "verlichting gelijkvloers" size 2.47 at (62.82, 53.00). Line step 3.21 | "Van Pagina 2" size 2.86 at (57.52, 51.54); "verlichting 2de verdiep" size 2.47 at (57.52, 54.76). Line step 3.22 |
| Text against the line | start 5.94 right of the line start; baselines 7.64 and 4.43 above the line | start 0.64 right of the line start; baselines 5.79 and 2.57 above the line |
| Header | "A", size 2.88, at (141.30, 52.50) | "G", size 2.88, at (141.30, 52.39) |
| Header against row 1 | 4.93 above the first junction y; 4.84 above the first name baseline | 4.94 and 4.85 |
| Bus | x 71.48; top 57.43 (row 1); bottom 211.00 (row 11) | x 71.48; top 57.33; bottom 180.17 (row 9) |
| Rows | 11 (A1..A11) | 9 (G1..G9) |

- The link text is hand placed, differently on the two pages. Both pages share the line start x 56.88 and the bus x 71.48 (7.95 right of the page 2 bus).
- Page 4 sits 0.10 higher than page 3 (every row y is 0.10 smaller).
- Frame on pages 3 and 4: rect 0.40..209.62 x 0.40..297.10 (page 1 and 2: 0.49..209.71). Title block as page 1.
- Title block texts: page 3 "Pagina 3: Verlichting gelijkvloers A", page 4 "Pagina 4: verlicthting 2de verdiep" (typo in the original); the other cells as page 1. No other page number or mark.

### Pages 3 and 4: row y

Junction y on the bus. The wire right of the contact is 0.10 higher; the name baseline and the light centre are within 0.03 of that wire y.

| Row | Page 3 | Page 4 |
| --- | --- | --- |
| 1 | 57.43 | 57.33 |
| 2 | 72.79 | 72.69 |
| 3 | 88.16 | 88.05 |
| 4 | 103.52 | 103.41 |
| 5 | 118.88 | 118.78 |
| 6 | 134.24 | 134.14 |
| 7 | 149.60 | 149.50 |
| 8 | 164.96 | 164.86 |
| 9 | 180.28 | 180.17 |
| 10 | 195.64 | |
| 11 | 211.00 | |

- Pitch 15.36 (steps 15.31..15.37). Page 3: 10 pitches = 153.57 (15.357). Page 4: 8 pitches = 122.84 (15.355). Same as the design pitch 15.35.
- Nothing lies below the line in any row, so no row needs extra height.

### Pages 3 and 4: row contents (offsets from the bus x 71.48 and the junction y)

| Item | Offset x | Offset y | Note |
| --- | --- | --- | --- |
| Stub | 0 .. 6.13 | 0 | stroke 0.2 |
| Wire to contact | 6.13 .. 15.83 | 0 to -0.10 | slightly tilted line, 9.7 long |
| Contact: stub | 15.83 .. 21.95 | -0.10 | horizontal |
| Contact: blade | 21.95 .. 27.57 | -0.10 .. +3.14 | one line going down-right (open contact). Same arm as the page 2 breaker arm (6.13 stub, 5.62 x 3.24 blade) but no black rect and no rating |
| Wire to the light | 28.33 .. 45.14 | -0.10 | stroke 0.2; ends 0.11 inside the circle (circle left edge 45.25) |
| Grey line | 28.33 .. 41.64 | -0.10 | stroke 0.07, laid on the wire (like the grey marks of page 1) |
| Light circle | centre 47.87 (x 119.35), r 2.62 (diameter 5.24) | -0.07 | stroke 0.2, no fill |
| Light cross | x 46.49 .. 49.20, y -1.38 .. +1.38 around the centre line | | two diagonals, half extent 1.36, stroke 0.2; ends do not reach the circle (a circle point at 45 degrees is 1.85 out) |
| Name text | x 141.30 (bus + 69.82) | baseline -0.09 (= wire y) | size 2.88; "A1 Garage voor": ID and name in one text, no separate device ID |

- No breaker, rating, cable text, conductor slashes, device stems or count labels on these pages.
- The light is 5.24 across: bigger than on page 1 (3.2) and than the library light (4.0).
- Page 3 names: A1 Garage voor, A2 Garage achter, A3 gang en 1ste, A4 werkplaats, A5 zithoek, A6 eethoek, A7 bureau, A8 spots zithoek, A9 spots eethoek, A10 keuken, A11 terras. Page 4: G1 Badkamer, G2 Gang, G3 Hobbykamer, G4 Slaapkamer 1, G5 Muurverlichting A slaapkamer 1, G6 Muurverlichting B slaapkamer 1, G7 Slaapkamer 2, G8 Muurverlichting A slaapkamer 2, G9 Muurverlichting B slaapkamer 2. One line each, no wrapping.

### No counterpart in section 1

- The arrows (page 2 only), the "Van" and "Naar" texts, the Diff 2 head without a feeder loop, circuit rows A and G without devices.
- The detail pages have a contact and a big light instead of breaker plus devices, and put ID and name in one text at x 141.30, 19.65 left of the page 1 description column (160.95).
- Faults in the original that are not copied: the page 2 title still says page 1, the page 4 title has a typo, the frame on pages 3 and 4 is 0.09 further left.

## 4. Design for pages 2 to 4 (M4)

### 4.1 Page roots

- Every page has one root: the installation root (first page unless it has `page`), a node with `page` pointing there, or the children of a circuit with `children_page` pointing there. A second root on the same page raises `layout_unsupported` for now.
- A moved differential is drawn on its page as the last head level without supply: on the first row at `group_x`, its bus at `bus_x` (page 2: Diff 2 on row A, as measured).
- The children of a circuit with `children_page` become detail rows (4.4).

### 4.2 Naar link (on the source page)

- One rule for every Naar end: a wire ends in the `page_link` arrow pointing right; the texts start after the tip, first baseline at line y + 0.7, further lines 3.6 below. Lines: `link_to`, then `link_text` when given.
- A moved differential: the feeder at x 34.57 runs down to the feeder end y, then right to 63.9 with the arrow. The feeder end y is House A's 256.8, kept as `content limit − 16.8` so it follows a taller title block. A row that would pass it gives `page_full`.
- A circuit with `children_page`: the circuit line runs from the breaker to the second slot's stem x (106.0) and ends in the arrow; texts start at the third slot's ID x (112.5), as measured. Devices that stay on the page are an error (`layout_unsupported`): such a circuit has no devices on the line.
- House A page 1 put "Naar Pg 2 / Ref Diff 2" above the line; one rule (texts after the tip, as on page 2) is used instead.

### 4.3 Van link (on the target page)

- A wire on the root's first row enters from the left and starts with the `page_link` arrow pointing right (into the page). Texts above the line from the arrow tail x: last line baseline at line y − 3.1, earlier lines 3.6 higher. Lines: `link_from`, then `link_text`.
- Start x: 8.66 for a moved differential (line to 42.42); bus − 14.6 (56.88) on a detail page.
- House A has no arrow on pages 3 and 4; the arrow is drawn on every Van end for one rule.

### 4.4 Detail rows

- Header: the circuit ID at (141.30, first row − 4.9), size 2.88.
- Bus at x 71.48 from the first to the last row; rows on the same grid (15.35), first row 57.43.
- Per row, from the bus: wire to + 21.95, open contact + 21.95..27.57 (drop 3.14), wire on to the light's `in` point; light centred at + 47.87.
- Text from template `detail_row` (default "{id} {name}") at x 141.30 on the row line, size 2.88. No separate ID.
- Children other than lights raise `layout_unsupported`. A light with `count` > 1 shows the count beside the light, as on circuit rows.
- The open contact is code-drawn as `switch_contact` (the House A blade without the breaker's mark), like `page_link`. AREI's `switch` (wall switch) is not used here.
- The light keeps scale 0.8 (3.2 mm), not House A's 5.24 on these pages: one size per symbol. A change belongs with the visual design proposals after M5.

### 4.5 Page numbers and clickable links

- Template `page_number` ("Pagina {number} van {total}") in its own cell at the right end of the title block, spanning the two base rows (page title/address and drawn by/executed by). `title_number_w` (32 mm) wide, so the vertical line stands at 177.86 (block right edge 209.86). The line between the two base rows stops there; the address and executed-by cells end at the new line. The text is centred on the cell horizontally (`title_number_dx` 0) and vertically (baseline `title_number_dy` 1.125 below the middle of the two rows, the same optical position as the row texts), title text size 4.23. When the block grows upward for version, date or `extra` rows, those rows keep the full width and the cell stays two rows high. The House A titles drop their own "Pagina n:" prefix.
- In the PDF each Naar end (arrow and texts) links to its target page and each Van end to its source page. Layout returns the link rectangles with the page; `export_pdf` writes them with ReportLab `bookmarkPage` and `linkRect`.

### 4.6 Defaults

- `link_to` "Naar Pg {page}", `link_from` "Van pg {page}" (the plan's values), `{page}` being the page number. House A gives `link_text` ("Ref Diff 2", "verlichting gelijkvloers", "verlichting 2de verdiep").

### 4.7 Checks added after the M4 review

- After all pages are laid out, every Van must have its Naar on the source page. A moved node in a place the layout does not draw a Naar for (directly under the supply, under a group member, under a nested breaker, a moved node inside a moved page) stops the build with `layout_unsupported` (variant `link`) and the node's ID.
- Two moved siblings under one element: `layout_unsupported` (variant `moved_siblings`).
- `children_page` equal to the circuit's own page: `unknown_page` (variant `own_page`).

### 4.8 Installation marks (`mounting`)

- A circuit or breaker with `mounting` (`in_wall`, `on_wall`, `in_conduit`, `in_conduit_in_wall`) gets the AREI symbol `line_<mounting>` on its cable. No default: without the field nothing is drawn. Detail rows have no cable and no mark.
- House A: every circuit row of pages 1 and 2 (I, J, K, N, L, M, O, P; A to H) and the nested 32 A breaker carry two grey "pi" marks (stroke 0.07, 2.5 wide, 1.3 high, 2.5 above the line), one 9.5 mm group at + 14.3 .. + 23.8 from the row origin (+ 4.96 .. + 14.4 on the return line of the 32 A breaker). They mean "in de wand". The head breakers have none. House A's marks are not copied as grey; the AREI mark is drawn in normal black at symbol stroke.
- The four symbols are 19 long with their own line; `scale` 0.83 in `symbol_table.yaml` makes the in_wall marks span 11.45 x 0.83 = 9.5 mm. Their height above the line is 2.1 x 0.83 = 1.74 (House A: 2.5). The mark's own flat line is not drawn: the cable line is there already (it would lie over the breaker, which ends at + 13.3).
- Placement: the symbol's centre point at origin + `mounting_dx` 16.75, so the in_wall marks span 14.3 .. 23.8. The same x offset is used for every circuit row, also a branching circuit (origin = branch x). The other three symbols are placed by the same centre point; their marks lie where the AREI symbol has them (`on_wall`: under the line and 4.6 further left; `in_conduit`: one circle above the centre; `in_conduit_in_wall`: one arch left, one circle right).
- On the return line of a nested breaker (and of a head level): centre at origin + `nested_mounting_dx` 11.7, so the marks span 9.25 .. 18.75 around the conductors slash (+ 14.0, in the gap between the two marks) and stay 0.9 from the loop wire at + 19.64.
- Conductors mark: the slash lies between the marks (rows: gap 16.83 .. 21.27, slash at 18.5). With a mark the count no longer sits beside the slash (it would touch a mark) but centred above the marks (`conductors_count_marked_dy` -2.5). Without a mark the count stays beside the slash.
- Cable text: a mark above the line does not touch it. A mark hanging under the line (`on_wall`) pushes the cable text down until its top is `mounting_text_gap` (0.3) below the mark.
- The grey 0.07 line on the wire of the detail rows (pages 3 and 4, + 28.33 .. + 41.64, 13.3 long) lies exactly on the wire and has no marks above it: most likely the cable line of an installation mark whose marks were deleted. It carries no information and is not drawn; detail rows get no mark.

