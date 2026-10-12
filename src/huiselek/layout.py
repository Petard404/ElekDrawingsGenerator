"""Place elements on pages.

Frame and title block, the head (supply, chain of levels, group of differentials), and per bus the
circuit rows, nested breakers and branching circuits (docs/layout-notes.md, 2.1 to 2.7); page roots,
page links and detail pages (section 4). All dimensions come from Settings.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from reportlab.pdfbase.pdfmetrics import stringWidth

from . import labels
from .errors import HuiselekError
from .model import Box, Breaker, Circuit, Installation, Light, Node, PhotoDetector, Socket
from .primitives import TEXT_FONT, Line, Page, Polyline, Primitive, Rect, Style, Text, bbox
from .settings import Settings
from .symbols import Symbol, load_symbols

# Rotations (degrees clockwise) that bring a symbol's terminal to the drawing direction.
BREAKER_ROTATION = 270    # terminal a faces the origin, b lies to the right of a
HANGING_ROTATION = 90     # a lead that arrives from the left arrives from above instead
UPRIGHT = 0

Box4 = tuple[float, float, float, float]


@dataclass
class _Row:
    wires: list[Primitive] = field(default_factory=list)   # not checked for overlap
    items: list[tuple[Primitive, ...]] = field(default_factory=list)  # symbols and texts, one box each
    links: list[tuple[Box4, int]] = field(default_factory=list)  # clickable box, number of target page


def _box(prims: tuple[Primitive, ...]) -> Box4:
    """Bounding box (x0, y0, x1, y1) that encloses all the primitives."""
    boxes = [bbox(p) for p in prims]
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def _overlap(a: Box4, b: Box4) -> bool:
    """True when two boxes overlap; boxes that only touch do not overlap."""
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _on_line(p: Primitive, y: float) -> bool:
    """True for a line or polyline that lies flat on the cable line at y."""
    pts = [(p.x1, p.y1), (p.x2, p.y2)] if isinstance(p, Line) else p.points if isinstance(p, Polyline) else []
    return bool(pts) and all(abs(py - y) < 1e-6 for _, py in pts)


def _unsupported(node: Node, variant: str | None = None) -> HuiselekError:
    """The layout_unsupported error for a node, with the variant that says why."""
    return HuiselekError("layout_unsupported", node.id, kind=node.kind, variant=variant)


@dataclass(frozen=True)
class _Root:
    kind: str           # "installation", "moved" (a node with its own page) or "detail" (children_page)
    node: Node          # drawn from here; the circuit for a detail page
    parent: Node | None  # where the Van link comes from; None for the installation root


def _page_roots(inst: Installation) -> dict[str, list[_Root]]:
    """The roots of every page in tree order, the installation root first (docs/layout-notes.md 4.1)."""
    roots: dict[str, list[_Root]] = {inst.page_of(inst.root.id): [_Root("installation", inst.root, None)]}

    def walk(node: Node) -> None:
        """Add a root for each child on another page, then recurse into every child."""
        detail_done = False
        for c in getattr(node, "children", ()):
            page = inst.page_of(c.id)
            if page != inst.page_of(node.id):
                if getattr(node, "children_page", None) == page:
                    if not detail_done:  # all children of the circuit are one root
                        roots.setdefault(page, []).append(_Root("detail", node, node))
                        detail_done = True
                else:
                    roots.setdefault(page, []).append(_Root("moved", c, node))
            walk(c)

    walk(inst.root)
    return roots


# --- what is drawn -------------------------------------------------------


def _check_bus(owner: Node, kids) -> None:
    """Raise layout_unsupported for everything the rows cannot draw yet. kids(node): children on the page."""
    children = kids(owner)
    if any(c.kind == "differential" for c in children):
        raise _unsupported(owner, "group" if all(c.kind == "differential" for c in children) else "mixed")
    for c in children:
        if c.kind == "breaker":
            if c is not children[-1]:
                raise _unsupported(c, "nested")  # the bus continues below it, so nothing may follow
            if not kids(c):
                raise _unsupported(c)
            _check_bus(c, kids)
        elif isinstance(c, Circuit):
            _check_circuit(c, kids)
        else:
            raise _unsupported(c)


def _check_circuit(c: Circuit, kids) -> None:
    """Raise layout_unsupported for anything under a circuit that cannot be drawn yet."""
    for d in kids(c):
        if isinstance(d, Circuit):
            _check_circuit(d, kids)
        elif isinstance(d, PhotoDetector):
            if len(d.children) > 1:
                raise _unsupported(d, "detector")
            for light in d.children:
                if not isinstance(light, Light):
                    raise _unsupported(light)
        elif not isinstance(d, (Socket, Light, Box)):
            raise _unsupported(d)


def wrap_lines(text: str, size: float, width: float) -> list[str]:
    """Text wrapped at width (mm) in Helvetica at this size; explicit line breaks are kept."""
    out: list[str] = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = f"{line} {word}" if line else word
            if line and stringWidth(trial, TEXT_FONT, size) > width:
                out.append(line)
                line = word
            else:
                line = trial
        out.append(line)
    return out


def description_lines(text: str, s: Settings) -> list[str]:
    """Description wrapped at description_width; explicit line breaks are kept."""
    return wrap_lines(text, s.text_size, s.description_width)


# --- one circuit row -----------------------------------------------------


class _Layout:
    def __init__(self, inst: Installation, s: Settings, page_id: str, numbers: dict[str, int]):
        """Set up an empty layout for one page, with the symbols loaded for the settings."""
        self.inst = inst
        self.s = s
        self.page_id = page_id
        self.numbers = numbers         # page id -> page number
        self.links: list[tuple[float, float, float, float, int]] = []
        self.low = 0.0                 # lowest y of the rows committed so far
        self.next_grid = 0             # first grid line below everything placed
        self.content_limit = 0.0       # lowest y the content may reach (set by frame())
        self.sym: dict[str, Symbol] = load_symbols(s)
        self.placed: list[Box4] = []   # boxes of everything drawn so far
        self.out: list[Primitive] = []
        self.naar_ids: set[str] = set()  # IDs of the nodes whose Naar end is drawn on this page

    def wire(self, x1: float, y1: float, x2: float, y2: float) -> Line:
        """Wire line with the wire stroke width from the settings."""
        return Line(x1, y1, x2, y2, Style(stroke_width=self.s.wire_stroke_mm))

    def text(self, x: float, y: float, txt: str, size: float, anchor: str = "start") -> Text:
        """Text primitive at (x, y) with the given size and anchor."""
        return Text(x, y, txt, size, anchor)

    def stem_x(self, origin: float, slot: int) -> float:
        """X of the stem in a slot: the origin, the first stem offset and the slot pitch."""
        return origin + self.s.first_stem_dx + slot * self.s.device_pitch

    def count_text(self, row: _Row, sym: Symbol, x: float, y: float, d: Node, rotation: int,
                   at: tuple[float, float] | None = None) -> None:
        """Count above 1 and the note, at `at`, else the symbol's label point, else beside the stem."""
        parts = []
        if getattr(d, "count", 1) > 1:
            parts.append(str(d.count))
        if getattr(d, "note", None):
            parts.append(d.note)
        if not parts:
            return
        if at is not None:
            lx, ly = at
        elif "label" in sym.points:
            lx, ly = sym.point("label", x, y, rotation)
        else:
            lx, ly = x + self.s.count_dx, y - self.s.device_drop + self.s.count_dy
        row.items.append((self.text(lx, ly, " ".join(parts), self.s.count_text_size),))

    def hang(self, row: _Row, sym: Symbol, x: float, y: float, rotation: int) -> tuple[Primitive, ...]:
        """Symbol with its `in` point at (x, y); returns the placed primitives."""
        prims = sym.place(x, y, rotation)
        row.items.append(prims)
        return prims

    def device(self, row: _Row, d: Node, sx: float, y: float) -> None:
        """One slot: stem, symbol(s), count, ID. y is the line of the row."""
        s = self.s
        end_y = y + s.device_drop
        row.wires.append(self.wire(sx, y, sx, end_y))
        placed: list[tuple[Primitive, ...]] = []
        shown = d  # the node whose ID is written under the slot
        if isinstance(d, Socket):
            sym = self.sym[f"socket_{d.variant}"]
            placed.append(self.hang(row, sym, sx, end_y, UPRIGHT))
            self.count_text(row, sym, sx, end_y, d, UPRIGHT)
        elif isinstance(d, Light):
            sym = self.sym["light_with_switch" if d.switch else "light"]
            placed.append(self.hang(row, sym, sx, end_y, HANGING_ROTATION))
            self.count_text(row, sym, sx, end_y, d, HANGING_ROTATION)
        elif isinstance(d, Box):
            sym = self.sym["box"]
            placed.append(self.hang(row, sym, sx, end_y, HANGING_ROTATION))
        else:  # PhotoDetector, with at most one light
            sym = self.sym["photo_detector"]
            placed.append(self.hang(row, sym, sx, end_y, UPRIGHT))
            if d.children:
                light = d.children[0]
                bx, by = sym.point("b", sx, end_y, UPRIGHT)
                row.wires.append(self.wire(bx, by, bx, by + s.device_drop))
                lsym = self.sym["light_with_switch" if light.switch else "light"]
                placed.append(self.hang(row, lsym, bx, by + s.device_drop, HANGING_ROTATION))
                self.count_text(row, lsym, bx, by + s.device_drop, light, HANGING_ROTATION)
                shown = light
        id_y = y + s.id_dy
        if len(placed) > 1:  # stacked symbols: below the lowest one
            id_y = max(id_y, max(bbox(p)[3] for prims in placed for p in prims) + s.id_gap)
        row.items.append((self.text(sx, id_y, shown.id, s.small_text_size, "middle"),))
        if isinstance(d, Box):
            row.items.append((self.text(sx, id_y + s.description_line_step, d.label,
                                        s.small_text_size, "middle"),))

    def breaker_head(self, row: _Row, c: Node, origin: float, y: float) -> None:
        """Breaker symbol from the origin, with the rating above it (steps 1 of 2.4)."""
        s = self.s
        a_x = origin + s.breaker_start_dx
        row.wires.append(self.wire(origin, y, a_x, y))
        row.items.append(self.sym["breaker"].place(a_x, y, BREAKER_ROTATION))
        rating = labels.format_template("breaker", self.inst.labels, c)
        row.items.append((self.text(origin + s.rating_dx, y + s.rating_dy, rating, s.text_size),))

    def mounting_mark(self, row: _Row, mounting: str, mx: float, y: float) -> float:
        """Installation mark of the cable (4.8): the AREI symbol centred at (mx, y), without its own line.

        The cable line is already drawn, so the symbol's horizontal line along y is dropped. Returns the
        lowest y of the mark (y itself when the mark lies above the line).
        """
        prims = tuple(p for p in self.sym[f"line_{mounting}"].place(mx, y, UPRIGHT)
                      if not _on_line(p, y))
        row.items.append(prims)
        return max([y] + [bbox(p)[3] for p in prims])

    def cable_marks(self, row: _Row, c: Node, cx: float, cy: float, tx: float, ty: float,
                    mx: float | None = None) -> None:
        """Conductors mark centred at (cx, cy) with its count, the cable text at (tx, ty) and, when the
        node has `mounting`, the installation mark centred at (mx, cy). With a mark the count moves above
        it; a mark below the line pushes the cable text down."""
        s = self.s
        marked = bool(c.mounting) and mx is not None
        if c.conductors:
            row.items.append(self.sym["conductors"].place(cx, cy, UPRIGHT))
            if marked:   # beside the slash would hit a mark: the count goes above the marks
                count = self.text(cx, cy + s.conductors_count_marked_dy, str(c.conductors),
                                  s.count_text_size, "middle")
            else:
                count = self.text(cx + s.conductors_count_dx, cy + s.conductors_count_dy,
                                  str(c.conductors), s.count_text_size)
            row.items.append((count,))
        low = self.mounting_mark(row, c.mounting, mx, cy) if marked else cy
        if c.cable:
            t = self.text(tx, ty, c.cable, s.small_text_size)
            gap = low + s.mounting_text_gap - bbox(t)[1]
            if gap > 0:
                t = self.text(tx, ty + gap, c.cable, s.small_text_size)
            row.items.append((t,))

    def circuit_row(self, c: Circuit, origin: float, y: float) -> _Row:
        """Steps 1 to 5 of docs/layout-notes.md 2.4 for one circuit at row line y."""
        s = self.s
        row = _Row()
        self.breaker_head(row, c, origin, y)

        kids = self.kids(c)
        target = self.detail_target(c)
        if target and kids:
            raise _unsupported(c)  # a circuit with a detail page keeps no devices on its own line
        devices = [d for d in kids if not isinstance(d, Circuit)]
        branching = len(devices) < len(kids)
        if target:
            end_x = self.stem_x(origin, s.link_end_slot)
            row.wires.append(self.wire(origin + s.breaker_end_dx, y, end_x, y))
            text_x = self.stem_x(origin, s.link_text_slot) + s.link_text_id_dx
            self.naar_end(row, c, target, end_x, y, text_x)
        elif devices or branching:
            end_slot = len(devices) if branching else len(devices) - 1  # the branch x is the next free slot
            row.wires.append(self.wire(origin + s.breaker_end_dx, y, self.stem_x(origin, end_slot), y))
        self.cable_marks(row, c, origin + s.conductors_dx, y,
                         origin + s.cable_dx, y + s.cable_dy, origin + s.mounting_dx)

        first_device_item = len(row.items)
        for i, d in enumerate(devices):
            self.device(row, d, self.stem_x(origin, i), y)
        right = max((_box(item)[2] for item in row.items[first_device_item:]), default=origin)
        if right > s.description_x - s.device_margin:
            raise HuiselekError("too_many_devices", c.id)

        row.items.append((self.text(s.description_x, y, c.id, s.text_size),))
        for j, line in enumerate(description_lines(c.description, s), start=1):
            row.items.append((self.text(s.description_x, y + j * s.description_line_step, line,
                                        s.text_size),))
        return row

    def nested_row(self, c: Breaker, origin: float, y: float) -> _Row:
        """Breaker with a loop: right, down and back to the bus, where the bus continues (2.3)."""
        s = self.s
        row = _Row()
        self.breaker_head(row, c, origin, y)
        loop_x, return_y = origin + s.loop_dx, y + s.loop_drop
        row.wires += [self.wire(origin + s.breaker_end_dx, y, loop_x, y),
                      self.wire(loop_x, y, loop_x, return_y),
                      self.wire(loop_x, return_y, origin, return_y)]
        if c.label:
            row.items.append((self.text(origin + s.nested_label_dx, y + s.nested_label_dy, c.label,
                                        s.text_size),))
        self.cable_marks(row, c, origin + s.nested_conductors_dx, return_y,
                         origin + s.nested_cable_dx, return_y + s.nested_cable_dy,
                         origin + s.nested_mounting_dx)
        return row

    def guard(self, row: _Row, element: str) -> float:
        """Raise page_full when a box or wire of the row passes the content limit; returns its lowest y."""
        low = max([_box(item)[3] for item in row.items] + [max(w.y1, w.y2) for w in row.wires],
                  default=0.0)
        if low > self.content_limit:
            raise HuiselekError("page_full", self.page_id, element=element)
        return low

    def commit(self, row: _Row, element: str) -> None:
        """Add a row to the page and to the boxes that later rows must keep clear of."""
        self.low = max(self.low, self.guard(row, element))
        self.links.extend((*box, target) for box, target in row.links)
        self.placed.extend(_box(item) for item in row.items)
        self.out.extend(row.wires)
        for item in row.items:
            self.out.extend(item)

    def place(self, make_row, grid: int, element: str) -> tuple[float, int]:
        """Draw the row on the first grid line from `grid` on where it overlaps nothing placed.

        make_row(y) builds the row at line y. Returns (y, next grid line). The loop ends at the latest
        when the row passes the content limit (page_full for `element`).
        """
        s = self.s
        while True:
            y = s.first_row_y + grid * s.row_pitch
            row = make_row(y)
            self.guard(row, element)
            boxes = [_box(item) for item in row.items]
            grid += 1
            if not any(_overlap(b, p) for b in boxes for p in self.placed):
                break
        self.commit(row, element)
        self.next_grid = max(self.next_grid, grid)
        return y, grid

    def circuit(self, c: Circuit, origin: float, grid: int) -> tuple[float, int]:
        """A circuit row, then the rows of its branching circuits from the branch x (2.4 step 6)."""
        y, grid = self.place(lambda row_y: self.circuit_row(c, origin, row_y), grid, c.id)
        kids = self.kids(c)
        branches = [d for d in kids if isinstance(d, Circuit)]
        if branches:
            branch_x = self.stem_x(origin, len(kids) - len(branches))
            last_y = y
            for b in branches:
                last_y, grid = self.circuit(b, branch_x, grid)
            self.out.append(self.wire(branch_x, y, branch_x, last_y))
        return y, grid

    def bus(self, owner: Node, start_y: float, grid: int) -> float:
        """The rows of owner's children on the bus, which runs from start_y to the last row.

        A nested breaker is the last row; its children form the next bus from its return line.
        Returns the y of the last row.
        """
        s = self.s
        at = len(self.out)  # the bus wire goes first
        y = start_y
        for c in self.kids(owner):
            if isinstance(c, Circuit):
                y, grid = self.circuit(c, s.bus_x, grid)
            else:
                y, grid = self.place(lambda row_y: self.nested_row(c, s.bus_x, row_y), grid, c.id)
                self.bus(c, y + s.loop_drop, grid - 1 + s.nested_child_lines)
        self.out.insert(at, self.wire(s.bus_x, start_y, s.bus_x, y))
        return y

    # --- frame and title block ---------------------------------------------

    def frame(self, page_title: str) -> None:
        """Page frame and title block; the block grows upward with version, date and extra items."""
        s, p = self.s, self.inst.project
        cells = [(page_title, labels.format_template("title_address", self.inst.labels, {"value": p.address})),
                 (labels.format_template("title_drawn_by", self.inst.labels, {"value": p.drawn_by}),
                  labels.format_template("title_executed_by", self.inst.labels, {"value": p.executed_by}))]
        items = []
        if p.version is not None:
            items.append(labels.format_template("title_version", self.inst.labels, {"value": p.version}))
        if p.date is not None:
            items.append(labels.format_template("title_date", self.inst.labels, {"value": str(p.date)}))
        items += [labels.TITLE_EXTRA.format(label=e.label, value=e.value) for e in p.extra]
        extra_rows = [tuple(items[i:i + 2]) + ("",) * (2 - len(items[i:i + 2]))
                      for i in range(0, len(items), 2)]
        rows = extra_rows[::-1] + cells  # top to bottom; the first extra row sits on the title row
        top = s.title_bottom - len(rows) * s.title_row_h
        self.content_limit = top - s.content_margin
        style = Style(stroke_width=s.title_stroke_mm)
        self.out.append(Rect(s.frame_x, s.frame_y, s.frame_w, s.frame_h,
                             Style(stroke_width=s.frame_stroke_mm)))
        self.out.append(Rect(s.title_x, top, s.title_w, s.title_bottom - top, style))
        self.out.append(Line(s.title_split_x, top, s.title_split_x, s.title_bottom, style))
        number = labels.format_template("page_number", self.inst.labels,
                                        {"number": self.numbers[self.page_id], "total": len(self.numbers)})
        base = len(extra_rows)          # index of the page title row; the number cell spans it and the next
        right = s.title_x + s.title_w
        cell_x = right - s.title_number_w
        for i, (left, cell) in enumerate(rows):
            row_top = top + i * s.title_row_h
            if i:  # a line between the base rows stops at the page number cell
                end = cell_x if i == base + 1 else right
                self.out.append(Line(s.title_x, row_top, end, row_top, style))
            for x, txt in ((s.title_text_left, left), (s.title_text_right, cell)):
                if txt:
                    t = self.text(x, row_top + s.title_text_dy, txt, s.title_text_size)
                    self.out.append(t)
                    self.placed.append(bbox(t))
        base_top = top + base * s.title_row_h
        self.out.append(Line(cell_x, base_top, cell_x, s.title_bottom, style))
        t = self.text(cell_x + s.title_number_w / 2 + s.title_number_dx,
                      (base_top + s.title_bottom) / 2 + s.title_number_dy, number, s.title_text_size, "middle")
        self.out.append(t)
        self.placed.append(bbox(t))

    # --- head -------------------------------------------------------------

    def kids(self, node: Node) -> list[Node]:
        """Children of node that are drawn on this page."""
        return [c for c in getattr(node, "children", []) if self.inst.page_of(c.id) == self.page_id]

    def lines(self, name: str, node: Node) -> list[str]:
        """Lines of a label template for a node; empty lines (an empty template) are dropped."""
        return [ln for ln in labels.format_template(name, self.inst.labels, node).split("\n") if ln]

    def moved_kids(self, node: Node) -> list[Node]:
        """Children of node that are drawn on another page."""
        return [c for c in getattr(node, "children", ()) if self.inst.page_of(c.id) != self.page_id]

    def detail_target(self, c: Circuit) -> str | None:
        """Page of the children of a circuit with children_page, when they are not on this page."""
        if c.children_page and c.children and c.children_page != self.page_id:
            return c.children_page
        return None

    # --- page links (docs/layout-notes.md 4.2, 4.3) ---------------------------

    def link_lines(self, name: str, node: Node, page_number: int) -> list[str]:
        """The link template, then the node's link_text; {page} is the number of the other page."""
        text = labels.format_template(name, self.inst.labels, {"page": page_number})
        lines = [ln for ln in text.split("\n") if ln]
        link_text = getattr(node, "link_text", None)
        return lines + (link_text.split("\n") if link_text else [])

    def naar_end(self, row: _Row, node: Node, target: str, tip_x: float, y: float, text_x: float) -> None:
        """Arrow with its tip at (tip_x, y), texts from text_x; the row gets the clickable box."""
        s = self.s
        number = self.numbers[target]
        self.naar_ids.add(node.id)
        arrow = self.sym["page_link"].place(tip_x, y, UPRIGHT)
        texts = [self.text(text_x, y + s.link_first_dy + i * s.link_line_step, ln, s.text_size)
                 for i, ln in enumerate(self.link_lines("link_to", node, number))]
        row.items.append(arrow)
        row.items.extend((t,) for t in texts)
        row.links.append((_box(arrow + tuple(texts)), number))

    def van_end(self, node: Node, source: Node, start_x: float, end_x: float, y: float) -> None:
        """Wire from start_x to end_x with the arrow at its left end, link texts above it."""
        s = self.s
        number = self.numbers[self.inst.page_of(source.id)]
        row = _Row()
        row.wires.append(self.wire(start_x, y, end_x, y))
        link = self.sym["page_link"]
        arrow = link.place(start_x - link.point("tail", 0, 0)[0], y, UPRIGHT)  # tail on start_x
        lines = self.link_lines("link_from", node, number)
        texts = [self.text(start_x, y - s.van_text_dy - (len(lines) - 1 - i) * s.link_line_step, ln,
                           s.text_size) for i, ln in enumerate(lines)]
        row.items.append(arrow)
        row.items.extend((t,) for t in texts)
        row.links.append((_box(arrow + tuple(texts)), number))
        self.commit(row, node.id)

    def supply(self) -> None:
        """Draw the supply box with its voltage and label, and add them to the placed boxes."""
        s, root = self.s, self.inst.root
        self.out.append(Rect(s.supply_x, s.supply_y, s.supply_w, s.supply_h,
                             Style(stroke_width=s.supply_stroke_mm)))
        self.out.append(Rect(s.supply_inner_x, s.supply_inner_y, s.supply_inner_w, s.supply_inner_h,
                             Style(stroke_width=s.supply_inner_stroke_mm)))
        texts = [self.text(s.supply_voltage_x, s.supply_voltage_y, ln, s.supply_voltage_size)
                 for ln in self.lines("supply_voltage", root)]
        wrapped = wrap_lines(root.label, s.supply_label_size, s.supply_label_width)
        texts += [self.text(s.supply_label_x, s.supply_label_y + i * s.supply_label_step, ln,
                            s.supply_label_size) for i, ln in enumerate(wrapped)]
        self.out.extend(texts)
        self.placed.extend(bbox(t) for t in texts)

    def level_row(self, node: Node, x: float, y: float) -> _Row:
        """A breaker or differential on a horizontal line from x, with its texts."""
        s = self.s
        row = _Row()
        a_x = x + s.breaker_start_dx
        row.wires.append(self.wire(x, y, a_x, y))
        sym = self.sym["differential" if node.kind == "differential" else "breaker"]
        row.items.append(sym.place(a_x, y, BREAKER_ROTATION))
        if node.kind == "differential":
            texts = self.lines("differential", node) + self.lines("differential_type", node)
            if node.label:
                texts.append(node.label)
            for i, ln in enumerate(texts):
                row.items.append((self.text(x + s.head_text_dx, y + s.head_text_dy + i * s.head_text_step,
                                            ln, s.text_size),))
        else:
            for ln in self.lines("breaker", node):
                row.items.append((self.text(x + s.rating_dx, y + s.rating_dy, ln, s.text_size),))
            if node.label:
                row.items.append((self.text(x + s.nested_label_dx, y + s.nested_label_dy, node.label,
                                            s.text_size),))
        return row

    def head(self) -> None:
        """Supply, the chain of levels, then the group of differentials or the bus of the last level."""
        s = self.s
        self.supply()
        levels = []
        node = self.inst.root
        while True:
            kids = self.kids(node)
            if len(kids) == 1 and kids[0].kind in ("breaker", "differential") and not self.moved_kids(node):
                node = kids[0]
                levels.append(node)
                if node.kind == "differential":
                    break
            else:
                break
        if not levels:
            kids = self.kids(self.inst.root)
            if len(kids) + len(self.moved_kids(self.inst.root)) > 1:
                raise _unsupported(self.inst.root, "group")
            if kids:
                raise _unsupported(kids[0])
            return  # a single child on another page: layout() reports its missing Naar
        top_y = s.head_first_level_y + (len(levels) - 1) * s.head_level_spacing
        grid = max(0, math.ceil((top_y - s.first_row_y) / s.row_pitch))
        last_y = s.first_row_y + grid * s.row_pitch
        ys = [s.head_first_level_y + k * s.head_level_spacing for k in range(len(levels) - 1)] + [last_y]
        self.out.append(self.wire(s.head_x, s.supply_y + s.supply_h, s.head_x, ys[0]))
        for k, (lv, y) in enumerate(zip(levels, ys)):
            self.commit(self.level_row(lv, s.head_x, y), lv.id)
            if k < len(levels) - 1:  # return loop to the next level
                end_x = s.head_x + s.breaker_end_dx
                ret_y = y + s.head_loop_drop
                row = _Row()
                row.wires += [self.wire(end_x, y, s.head_loop_x, y),
                              self.wire(s.head_loop_x, y, s.head_loop_x, ret_y),
                              self.wire(s.head_loop_x, ret_y, s.head_x, ret_y),
                              self.wire(s.head_x, ret_y, s.head_x, ys[k + 1])]
                self.cable_marks(row, lv, s.head_x + s.nested_conductors_dx, ret_y,
                                 s.head_x + s.nested_cable_dx, ret_y + s.nested_cable_dy,
                                 s.head_x + s.nested_mounting_dx)
                self.commit(row, lv.id)
        last = levels[-1]
        end_x = s.head_x + s.breaker_end_dx
        kids = self.kids(last)
        self.next_grid = grid + 1
        if any(isinstance(c, Circuit) for c in kids):
            _check_bus(last, self.kids)
            self.out.append(self.wire(end_x, last_y, s.bus_x, last_y))
            self.bus(last, last_y, grid)
        elif kids or self.moved_kids(last):
            self.group(last, end_x, last_y, grid)

    def moved_root(self, node: Node, parent: Node) -> None:
        """A differential or breaker with its own page: the last head level without supply (4.1)."""
        s = self.s
        if node.kind not in ("differential", "breaker"):
            raise _unsupported(node)
        kids = self.check_member(node)
        y = s.first_row_y
        self.commit(self.level_row(node, s.group_x, y), node.id)
        self.van_end(node, parent, s.van_x, s.group_x, y)
        self.next_grid = 1
        self.member_bus(node, kids, y, 0)

    def detail_page(self, circuit: Circuit) -> None:
        """The page of a circuit's children: Van end, header and the detail rows (4.4)."""
        s = self.s
        y = s.first_row_y
        self.van_end(circuit, circuit, s.detail_bus_x - s.detail_link_dx, s.detail_bus_x, y)
        header = self.text(s.detail_header_x, y + s.detail_header_dy, circuit.id, s.text_size)
        self.out.append(header)
        self.placed.append(bbox(header))
        self.detail(circuit, y)

    def detail_row(self, light: Light, y: float) -> _Row:
        """Bus to light: wire, open contact when the light is switched, wire, light, count, detail_row text (4.4)."""
        s = self.s
        row = _Row()
        contact_x = s.detail_bus_x + s.detail_contact_dx
        light_x = s.detail_bus_x + s.detail_light_dx
        if light.switch:
            contact = self.sym["switch_contact"]
            row.wires.append(self.wire(s.detail_bus_x, y, contact_x, y))
            row.items.append(contact.place(contact_x, y, UPRIGHT))
            row.wires.append(self.wire(contact.point("b", contact_x, y)[0], y, light_x, y))
        else:
            row.wires.append(self.wire(s.detail_bus_x, y, light_x, y))
        sym = self.sym["light"]
        self.hang(row, sym, light_x, y, UPRIGHT)
        self.count_text(row, sym, light_x, y, light, UPRIGHT,
                        (light_x + s.detail_count_dx, y + s.detail_count_dy))
        label = labels.format_template("detail_row", self.inst.labels, light).strip()
        if label:
            row.items.append((self.text(s.detail_text_x, y, label, s.text_size),))
        return row

    def detail(self, circuit: Circuit, first_y: float) -> None:
        """The circuit's children as rows on the detail bus, which runs from the first to the last row."""
        s = self.s
        kids = self.kids(circuit)
        for k in kids:
            if not isinstance(k, Light):
                raise _unsupported(k)
        at = len(self.out)  # the bus wire goes first
        y, grid = first_y, 0
        for light in kids:
            y, grid = self.place(lambda row_y: self.detail_row(light, row_y), grid, light.id)
        self.out.insert(at, self.wire(s.detail_bus_x, first_y, s.detail_bus_x, y))

    def check_member(self, c: Node) -> list[Node]:
        """Children of a group member on this page; raise layout_unsupported for what cannot be drawn."""
        ck = self.kids(c)
        if ck and not any(isinstance(d, Circuit) for d in ck):
            for d in ck:
                if d.kind not in ("differential", "breaker"):
                    raise _unsupported(d)
            raise _unsupported(c, "group")
        if ck:
            _check_bus(c, self.kids)
        return ck

    def member_bus(self, c: Node, ck: list[Node], cy: float, cgrid: int) -> None:
        """The line from a group member to its bus x and the bus itself, when it has circuits."""
        s = self.s
        if ck:
            self.out.append(self.wire(s.group_x + s.breaker_end_dx, cy, s.bus_x, cy))
            self.next_grid = max(self.next_grid, cgrid + 1)
            self.bus(c, cy, cgrid)

    def group(self, owner: Node, end_x: float, y: float, grid: int) -> None:
        """Differentials or breakers under owner: the first inline on the row, the others on the feeder.

        A child on another page leaves a feeder end with a Naar link (4.2); only one is drawn.
        """
        s = self.s
        kids = self.kids(owner)
        moved = self.moved_kids(owner)
        if len(moved) > 1:
            raise _unsupported(moved[1], "moved_siblings")
        for c in kids + moved:
            if c.kind not in ("differential", "breaker"):
                raise _unsupported(c)
        feeder_y = y
        if not kids:
            self.out.append(self.wire(end_x, y, s.feeder_x, y))
        for i, c in enumerate(kids):
            ck = self.check_member(c)
            if i == 0:
                cy, cgrid = y, grid
                self.commit(self.level_row(c, s.group_x, cy), c.id)
                self.out.append(self.wire(end_x, y, s.group_x, y))
            else:
                cy, cgrid = self.place(lambda row_y: self.level_row(c, s.group_x, row_y), self.next_grid, c.id)
                cgrid -= 1
                self.out.append(self.wire(s.feeder_x, cy, s.group_x, cy))
                feeder_y = cy
            self.member_bus(c, ck, cy, cgrid)
        if moved:
            feeder_y = self.content_limit - s.feeder_end_dy
            if self.low > feeder_y:  # a row passes the feeder end
                raise HuiselekError("page_full", self.page_id, element=moved[0].id)
            row = _Row()
            row.wires.append(self.wire(s.feeder_x, feeder_y, s.feeder_arrow_x, feeder_y))
            self.naar_end(row, moved[0], self.inst.page_of(moved[0].id), s.feeder_arrow_x, feeder_y,
                          s.feeder_arrow_x + s.link_text_dx)
            self.commit(row, moved[0].id)
        if feeder_y != y:
            self.out.append(self.wire(s.feeder_x, y, s.feeder_x, feeder_y))


def layout(inst: Installation, s: Settings) -> list[Page]:
    """One Page per page definition. Raises HuiselekError layout_unsupported for what is not drawn yet."""
    numbers = {p.id: i for i, p in enumerate(inst.pages, start=1)}
    roots = _page_roots(inst)
    pages, drawn = [], {}
    for p in inst.pages:
        lay = _Layout(inst, s, p.id, numbers)
        lay.frame(p.title)
        found = roots.get(p.id, [])
        if len(found) > 1:
            raise _unsupported(found[1].node, "roots")
        for r in found:
            if r.kind == "installation":
                lay.head()
            elif r.kind == "moved":
                lay.moved_root(r.node, r.parent)
            else:
                lay.detail_page(r.node)
        drawn[p.id] = lay.naar_ids
        pages.append(Page(p.id, numbers[p.id], p.title, tuple(lay.out), lay.content_limit,
                          tuple(lay.links)))
    for found in roots.values():  # every Van needs its Naar on the source page (4.2)
        for r in found:
            if r.parent is not None and r.node.id not in drawn[inst.page_of(r.parent.id)]:
                raise _unsupported(r.node, "link")
    return pages
