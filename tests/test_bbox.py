"""bbox() of every primitive."""
import pytest
from reportlab.pdfbase.pdfmetrics import stringWidth

from huiselek.primitives import Arc, Circle, Line, Polyline, Rect, Text, bbox

APPROX = pytest.approx


def test_shapes():
    assert bbox(Line(3, 4, 1, 9)) == (1, 4, 3, 9)
    assert bbox(Polyline(((0, 1), (4, -2), (2, 5)))) == (0, -2, 4, 5)
    assert bbox(Circle(5, 5, 2)) == (3, 3, 7, 7)
    assert bbox(Rect(1, 2, 3, 4)) == (1, 2, 4, 6)


def test_arc_includes_axis_extremes():
    x0, y0, x1, y1 = bbox(Arc(0, 0, 1, 180, 360))  # upper half circle (y down)
    assert (x0, y0, x1) == APPROX((-1, -1, 1)) and y1 == APPROX(0, abs=1e-9)
    assert bbox(Arc(0, 0, 1, 0, 360)) == (-1, -1, 1, 1)
    assert bbox(Arc(0, 0, 1, 350, 370))[2] == APPROX(1)  # passes angle 360


def test_text_anchor_and_height():
    w = stringWidth("Hello", "Helvetica", 3.0)
    assert bbox(Text(10, 20, "Hello", 3.0)) == APPROX((10, 20 - 0.72 * 3, 10 + w, 20 + 0.21 * 3))
    assert bbox(Text(10, 20, "Hello", 3.0, "middle"))[0] == APPROX(10 - w / 2)
    assert bbox(Text(10, 20, "Hello", 3.0, "end"))[2] == APPROX(10)


def test_text_rotation_clockwise():
    w = stringWidth("Hello", "Helvetica", 3.0)
    x0, y0, x1, y1 = bbox(Text(10, 20, "Hello", 3.0, rotation=90))  # reads downwards, ascent to the right
    assert (x0, x1) == APPROX((10 - 0.21 * 3, 10 + 0.72 * 3))
    assert (y0, y1) == APPROX((20, 20 + w))
