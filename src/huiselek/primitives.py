"""Styled drawing primitives and the Page container.

Units are mm in page coordinates: origin top left, x to the right, y down.
Angles are in degrees, positive = clockwise on the page, measured from +x.
"""
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional, Union

from reportlab.pdfbase.pdfmetrics import stringWidth


@dataclass(frozen=True)
class Style:
    stroke: str = "#000000"
    stroke_width: float = 0.25
    fill: Optional[str] = None
    dash: Optional[tuple[float, ...]] = None  # lengths in mm, or None for solid


@dataclass(frozen=True)
class Line:
    x1: float
    y1: float
    x2: float
    y2: float
    style: Style = field(default_factory=Style)


@dataclass(frozen=True)
class Polyline:
    points: tuple[tuple[float, float], ...]
    closed: bool = False
    style: Style = field(default_factory=Style)


@dataclass(frozen=True)
class Arc:
    """Arc drawn from start_deg to end_deg in increasing angle (clockwise on the page).

    end_deg may exceed 360. A span of 360 or more draws a full circle outline.
    """

    cx: float
    cy: float
    r: float
    start_deg: float
    end_deg: float
    style: Style = field(default_factory=Style)


@dataclass(frozen=True)
class Circle:
    cx: float
    cy: float
    r: float
    style: Style = field(default_factory=Style)


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    w: float
    h: float
    style: Style = field(default_factory=Style)


@dataclass(frozen=True)
class Text:
    """Text with its baseline at y. rotation is clockwise degrees about (x, y)."""

    x: float
    y: float
    text: str
    size: float
    anchor: Literal["start", "middle", "end"] = "start"
    rotation: float = 0.0
    fill: str = "#000000"


Primitive = Union[Line, Polyline, Arc, Circle, Rect, Text]

TEXT_FONT = "Helvetica"
TEXT_ASCENT = 0.72   # of the font size, above the baseline
TEXT_DESCENT = 0.21  # of the font size, below the baseline
QUARTER_TURNS = (0, 90, 180, 270)


def _points_box(points) -> tuple[float, float, float, float]:
    xs = [q[0] for q in points]
    ys = [q[1] for q in points]
    return min(xs), min(ys), max(xs), max(ys)


def _arc_box(a: Arc) -> tuple[float, float, float, float]:
    def at(deg: float) -> tuple[float, float]:
        return a.cx + a.r * math.cos(math.radians(deg)), a.cy + a.r * math.sin(math.radians(deg))

    if a.end_deg - a.start_deg >= 360:
        return a.cx - a.r, a.cy - a.r, a.cx + a.r, a.cy + a.r
    pts = [at(a.start_deg), at(a.end_deg)]
    for q in QUARTER_TURNS:
        k = math.ceil((a.start_deg - q) / 360)  # first q + 360 k at or after the start
        if q + 360 * k <= a.end_deg:
            pts.append(at(q + 360 * k))
    return _points_box(pts)


def _text_box(t: Text) -> tuple[float, float, float, float]:
    w = stringWidth(t.text, TEXT_FONT, t.size)
    x0 = {"start": 0.0, "middle": -w / 2, "end": -w}[t.anchor]
    corners = [(x0, -TEXT_ASCENT * t.size), (x0 + w, -TEXT_ASCENT * t.size),
               (x0 + w, TEXT_DESCENT * t.size), (x0, TEXT_DESCENT * t.size)]
    if t.rotation:
        c, s = math.cos(math.radians(t.rotation)), math.sin(math.radians(t.rotation))
        corners = [(dx * c - dy * s, dx * s + dy * c) for dx, dy in corners]
    x0, y0, x1, y1 = _points_box(corners)
    return t.x + x0, t.y + y0, t.x + x1, t.y + y1


def bbox(p: Primitive) -> tuple[float, float, float, float]:
    """(x0, y0, x1, y1) of a primitive, stroke width ignored.

    Text: Helvetica width, ascent 0.72 and descent 0.21 of the size, honouring anchor and rotation.
    """
    if isinstance(p, Line):
        return _points_box([(p.x1, p.y1), (p.x2, p.y2)])
    if isinstance(p, Polyline):
        return _points_box(p.points)
    if isinstance(p, Arc):
        return _arc_box(p)
    if isinstance(p, Circle):
        return p.cx - p.r, p.cy - p.r, p.cx + p.r, p.cy + p.r
    if isinstance(p, Rect):
        return p.x, p.y, p.x + p.w, p.y + p.h
    if isinstance(p, Text):
        return _text_box(p)
    raise TypeError(f"unknown primitive {p!r}")


@dataclass(frozen=True)
class Page:
    id: str
    number: int
    title: str
    primitives: tuple[Primitive, ...] = ()
    content_limit_y: float | None = None  # lowest y that content may reach (above the title block)
    # Clickable page links: (x0, y0, x1, y1, number of the target page), mm, y down.
    links: tuple[tuple[float, float, float, float, int], ...] = ()


# A picture drawn onto a page after its SVG: (file path, x_mm, y_mm, w_mm, h_mm). The box is on
# the page, y counted from the top; the picture keeps its aspect ratio and is centred in the box.
# A .svg path is drawn as vector graphics. Only export_pdf draws these.
Overlay = tuple[Union[str, Path], float, float, float, float]
