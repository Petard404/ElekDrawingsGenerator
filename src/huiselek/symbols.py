"""Load symbols (symbol_table.yaml + symbol_data/*.json) and place them on a page.

A symbol lives in its own frame: mm, origin top left of its geometry, y down. It has named
connection points and an anchor (one of them). place() puts the anchor on a page position,
optionally rotated clockwise by 0/90/180/270 degrees about the anchor.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Callable

import yaml

from .errors import HuiselekError
from .primitives import Arc, Circle, Line, Polyline, Primitive, Rect, Style, Text
from .settings import Settings

CODE_DRAWN = ("page_link", "photo_detector")
ROTATIONS = (0, 90, 180, 270)


@dataclass(frozen=True)
class Symbol:
    id: str
    primitives: tuple[Primitive, ...]
    width: float
    height: float
    points: dict[str, tuple[float, float]]
    anchor: str

    def _mover(self, x: float, y: float, rotation: int) -> Callable[[float, float], tuple[float, float]]:
        if rotation not in ROTATIONS:
            raise ValueError(f"rotation must be one of {ROTATIONS}, got {rotation!r}")
        ax, ay = self.points[self.anchor]

        def move(px: float, py: float) -> tuple[float, float]:
            dx, dy = px - ax, py - ay
            if rotation == 90:      # clockwise on the page (y down): (1, 0) -> (0, 1)
                dx, dy = -dy, dx
            elif rotation == 180:
                dx, dy = -dx, -dy
            elif rotation == 270:
                dx, dy = dy, -dx
            return x + dx, y + dy

        return move

    def point(self, name: str, x: float, y: float, rotation: int = 0) -> tuple[float, float]:
        """Where the named point lands when the symbol is placed at (x, y) with this rotation."""
        px, py = self.points[name]
        return self._mover(x, y, rotation)(px, py)

    def place(self, x: float, y: float, rotation: int = 0) -> tuple[Primitive, ...]:
        """Primitives in page coordinates, anchor on (x, y). Text keeps its own rotation (upright)."""
        move = self._mover(x, y, rotation)
        return tuple(_transform(p, move, rotation) for p in self.primitives)


def _transform(p: Primitive, move: Callable[[float, float], tuple[float, float]], rotation: int) -> Primitive:
    if isinstance(p, Line):
        x1, y1 = move(p.x1, p.y1)
        x2, y2 = move(p.x2, p.y2)
        return Line(x1, y1, x2, y2, p.style)
    if isinstance(p, Polyline):
        return Polyline(tuple(move(*q) for q in p.points), p.closed, p.style)
    if isinstance(p, Circle):
        cx, cy = move(p.cx, p.cy)
        return Circle(cx, cy, p.r, p.style)
    if isinstance(p, Arc):
        cx, cy = move(p.cx, p.cy)
        return Arc(cx, cy, p.r, p.start_deg + rotation, p.end_deg + rotation, p.style)
    if isinstance(p, Rect):
        xa, ya = move(p.x, p.y)
        xb, yb = move(p.x + p.w, p.y + p.h)
        return Rect(min(xa, xb), min(ya, yb), abs(xb - xa), abs(yb - ya), p.style)
    if isinstance(p, Text):
        x, y = move(p.x, p.y)
        return Text(x, y, p.text, p.size, p.anchor, p.rotation, p.fill)
    raise TypeError(f"unknown primitive {p!r}")


def _from_json(d: dict, style: Style) -> Primitive:
    t = d["type"]
    if t == "line":
        return Line(d["x1"], d["y1"], d["x2"], d["y2"], style)
    if t == "polyline":
        return Polyline(tuple((x, y) for x, y in d["points"]), d["closed"], _filled(style, d["fill"]))
    if t == "circle":
        return Circle(d["cx"], d["cy"], d["r"], _filled(style, d["fill"]))
    if t == "arc":
        return Arc(d["cx"], d["cy"], d["r"], d["start_deg"], d["end_deg"], style)
    if t == "text":
        return Text(d["x"], d["y"], d["text"], d["size"], d["anchor"], d["rotation"])
    raise ValueError(f"unknown primitive type {t!r}")


def _filled(style: Style, fill: str | None) -> Style:
    return Style(style.stroke, style.stroke_width, fill, style.dash)


def _page_link(style: Style) -> Symbol:
    """Arrowhead of the "Naar"/"Van" page links of House A, pointing right, tip at the right.

    Measured from the Inkscape marker (Arrow2, scale 0.7, stroke 0.204): the path
    M -2,-4 9,0 -2,4 c 2,-2.33 2,-5.66 0,-8 z, one path unit being 0.18561 mm.
    """
    u = 0.18561
    p0, p1, p2, p3 = (-2.0, 4.0), (0.0, 1.67), (0.0, -1.66), (-2.0, -4.0)
    back = []
    for i in range(1, 8):  # concave back, from (-2, 4) to (-2, -4), end points excluded
        t = i / 8
        w = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        back.append((sum(a * q[0] for a, q in zip(w, (p0, p1, p2, p3))),
                     sum(a * q[1] for a, q in zip(w, (p0, p1, p2, p3)))))
    shape = [(-2.0, -4.0), (9.0, 0.0), (-2.0, 4.0)] + back
    pts = tuple((round((x + 2) * u, 3), round((y + 4) * u, 3)) for x, y in shape)
    tail = pts[3 + 3]  # t = 0.5, the middle of the concave back
    return Symbol(
        "page_link",
        (Polyline(pts, True, _filled(style, "#000000")),),
        round(11 * u, 3),
        round(8 * u, 3),
        {"tip": pts[1], "tail": tail},
        "tip",
    )


def _photo_detector(style: Style) -> Symbol:
    """Square with a roof-shaped double chevron, on a vertical line (a top, b bottom); House A K7, K8, H1."""
    w, h = 3.426, 3.294
    prims = (
        Polyline(((0.0, 0.0), (w, 0.0), (w, h), (0.0, h)), True, style),
        Polyline(((w, h), (w / 2, 0.0), (0.0, h)), False, style),
        Polyline(((0.0, h / 2), (w / 2, 0.0), (w, h / 2)), False, style),
    )
    return Symbol("photo_detector", prims, w, h, {"a": (w / 2, 0.0), "b": (w / 2, h)}, "a")


def load_symbols(s: Settings) -> dict[str, Symbol]:
    """Every symbol of the table plus the code-drawn ones, keyed by id (sorted)."""
    pkg = resources.files("huiselek")
    table = yaml.safe_load((pkg / "symbol_table.yaml").read_text(encoding="utf-8"))
    style = Style(stroke_width=s.symbol_stroke_mm)
    out: dict[str, Symbol] = {}
    for sid in sorted(table):
        entry = table[sid]
        if "scale" in entry:
            raise ValueError(f"{sid}: scale is not supported yet")
        data_file = pkg / "symbol_data" / f"{sid}.json"
        if not data_file.is_file():
            raise HuiselekError("reference_missing", sid, variant="data", path=f"symbol_data/{sid}.json")
        data = json.loads(data_file.read_text(encoding="utf-8"))
        points = {name: (float(xy[0]), float(xy[1])) for name, xy in entry["points"].items()}
        if entry["anchor"] not in points:
            raise ValueError(f"{sid}: anchor {entry['anchor']!r} is not one of its points")
        out[sid] = Symbol(
            sid,
            tuple(_from_json(d, style) for d in data["primitives"]),
            data["width"],
            data["height"],
            points,
            entry["anchor"],
        )
    for sym in (_page_link(style), _photo_detector(style)):
        out[sym.id] = sym
    return dict(sorted(out.items()))
