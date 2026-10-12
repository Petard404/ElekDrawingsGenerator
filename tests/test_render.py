"""Renderer tests: golden page, determinism, number format, arc flags."""
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from svglib.svglib import svg2rlg

from golden_pages import primitives_page
from huiselek.primitives import Arc, Line, Page, Style, Text
from huiselek.render_svg import arc_path, fmt, render_svg
from huiselek.settings import Settings

GOLDEN = Path(__file__).parent / "golden" / "primitives_page.svg"
SVG_NS = "{http://www.w3.org/2000/svg}"


def render() -> str:
    return render_svg(primitives_page(), Settings())


def test_matches_golden_byte_for_byte():
    assert render().encode("utf-8") == GOLDEN.read_bytes()


def test_parses_as_a4_svg():
    root = ET.fromstring(render())
    assert root.tag == SVG_NS + "svg"
    assert root.get("width") == "210mm"
    assert root.get("height") == "297mm"
    assert root.get("viewBox") == "0 0 210 297"


def test_deterministic():
    assert render() == render()


def test_svglib_converts_to_a4_points():
    drawing = svg2rlg(str(GOLDEN))
    assert drawing.width == pytest.approx(595.28, abs=0.01)
    assert drawing.height == pytest.approx(841.89, abs=0.01)


def test_text_escaped_and_font_family_set():
    page = Page("t", 1, "t", (Text(1, 2, "a & b < c", 3),))
    svg = render_svg(page, Settings(font_family="Arial"))
    assert ">a &amp; b &lt; c</text>" in svg
    assert 'font-family="Arial"' in svg
    ET.fromstring(svg)


def test_dash_only_when_set():
    page = Page("t", 1, "t", (Line(0, 0, 1, 1, Style()), Line(0, 0, 1, 1, Style(dash=(2, 1)))))
    lines = render_svg(page, Settings()).splitlines()
    assert "stroke-dasharray" not in lines[1]
    assert 'stroke-dasharray="2 1"' in lines[2]
    assert 'fill="none"' in lines[1]


@pytest.mark.parametrize("value, expected", [
    (0.1 + 0.2, "0.3"),
    (-0.001, "0"),
    (2.0, "2"),
    (10.0, "10"),
    (0.0, "0"),
    (1.005, "1"),      # float repr of 1.005 is below the tie
    (-3.456, "-3.46"),
    (297, "297"),
])
def test_fmt(value, expected):
    assert fmt(value) == expected


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_fmt_rejects_non_finite(value):
    with pytest.raises(ValueError):
        fmt(value)


@pytest.mark.parametrize("a0, a1, large", [(0, 90, "0"), (0, 180, "0"), (0, 270, "1"),
                                           (300, 420, "0"), (10, 300, "1")])
def test_arc_large_flag_and_sweep(a0, a1, large):
    d = arc_path(Arc(0, 0, 10, a0, a1))
    flags = d.split(" A ")[1].split()[3:5]
    assert flags == [large, "1"]  # increasing angle = sweep flag 1


def test_arc_endpoints():
    assert arc_path(Arc(10, 10, 5, 0, 90)) == "M 15 10 A 5 5 0 0 1 10 15"


def test_full_arc_split_in_two():
    d = arc_path(Arc(0, 0, 5, 0, 360))
    assert d == "M 5 0 A 5 5 0 0 1 -5 0 A 5 5 0 0 1 5 0"
