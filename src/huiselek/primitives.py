"""Styled drawing primitives and the Page container.

Units are mm in page coordinates: origin top left, x to the right, y down.
Angles are in degrees, positive = clockwise on the page, measured from +x.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional, Union


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


@dataclass(frozen=True)
class Page:
    id: str
    number: int
    title: str
    primitives: tuple[Primitive, ...] = ()


# A picture drawn onto a page after its SVG: (file path, x_mm, y_mm, w_mm, h_mm). The box is on
# the page, y counted from the top; the picture keeps its aspect ratio and is centred in the box.
# A .svg path is drawn as vector graphics. Only export_pdf draws these.
Overlay = tuple[Union[str, Path], float, float, float, float]
