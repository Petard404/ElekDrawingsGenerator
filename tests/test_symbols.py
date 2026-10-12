import math
from importlib import resources

import pytest
import yaml

from huiselek.primitives import Arc, Circle, Line, Polyline, Rect, Text
from huiselek.settings import Settings
from huiselek.symbols import CODE_DRAWN, ROTATIONS, load_symbols

TOL = 0.05
SYMBOLS = load_symbols(Settings())
NOT_ON_GEOMETRY = ("center", "label")


def _segments(p):
    if isinstance(p, Line):
        return [((p.x1, p.y1), (p.x2, p.y2))]
    pts = list(p.points)
    segs = list(zip(pts, pts[1:]))
    if p.closed:
        segs.append((pts[-1], pts[0]))
    return segs


def _dist_segment(pt, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = 0.0 if n == 0 else max(0.0, min(1.0, ((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dy) / n))
    return math.hypot(pt[0] - a[0] - t * dx, pt[1] - a[1] - t * dy)


def _arc_end(a, deg):
    return a.cx + a.r * math.cos(math.radians(deg)), a.cy + a.r * math.sin(math.radians(deg))


def _arc_covers(a, deg):
    if a.end_deg - a.start_deg >= 360:
        return True
    return any(a.start_deg <= deg + k * 360 <= a.end_deg for k in (-1, 0, 1, 2))


def _dist(pt, p):
    if isinstance(p, (Line, Polyline)):
        return min((_dist_segment(pt, a, b) for a, b in _segments(p)), default=math.inf)
    if isinstance(p, Rect):
        corners = [(p.x, p.y), (p.x + p.w, p.y), (p.x + p.w, p.y + p.h), (p.x, p.y + p.h)]
        return min(_dist_segment(pt, corners[i], corners[(i + 1) % 4]) for i in range(4))
    if isinstance(p, Circle):
        return abs(math.hypot(pt[0] - p.cx, pt[1] - p.cy) - p.r)
    if isinstance(p, Arc):
        ang = math.degrees(math.atan2(pt[1] - p.cy, pt[0] - p.cx))
        if _arc_covers(p, ang):
            return abs(math.hypot(pt[0] - p.cx, pt[1] - p.cy) - p.r)
        return min(math.dist(pt, _arc_end(p, d)) for d in (p.start_deg, p.end_deg))
    return math.inf  # text


def _dist_to_all(pt, prims):
    return min(_dist(pt, p) for p in prims)


def _extent(p):
    """(xmin, ymin, xmax, ymax) of a non-text primitive."""
    if isinstance(p, Line):
        return min(p.x1, p.x2), min(p.y1, p.y2), max(p.x1, p.x2), max(p.y1, p.y2)
    if isinstance(p, Polyline):
        xs, ys = [q[0] for q in p.points], [q[1] for q in p.points]
        return min(xs), min(ys), max(xs), max(ys)
    if isinstance(p, Circle):
        return p.cx - p.r, p.cy - p.r, p.cx + p.r, p.cy + p.r
    if isinstance(p, Rect):
        return p.x, p.y, p.x + p.w, p.y + p.h
    if isinstance(p, Arc):
        angles = [p.start_deg, p.end_deg] + [d for d in (0, 90, 180, 270) if _arc_covers(p, d)]
        pts = [_arc_end(p, d) for d in angles]
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        return min(xs), min(ys), max(xs), max(ys)
    raise TypeError(p)


@pytest.fixture(params=sorted(SYMBOLS), ids=sorted(SYMBOLS))
def sym(request):
    return SYMBOLS[request.param]


def test_ids_match_data_files_and_code_drawn():
    pkg = resources.files("huiselek")
    table = yaml.safe_load((pkg / "symbol_table.yaml").read_text(encoding="utf-8"))
    files = {f.name[:-5] for f in (pkg / "symbol_data").iterdir() if f.name.endswith(".json")}
    assert set(table) == files
    assert set(SYMBOLS) == files | set(CODE_DRAWN)


def test_loading_twice_gives_equal_results():
    assert load_symbols(Settings()) == load_symbols(Settings())


def test_symbol_stroke_from_settings():
    syms = load_symbols(Settings(symbol_stroke_mm=0.4))
    for s in syms.values():
        for p in s.primitives:
            if not isinstance(p, Text):
                assert p.style.stroke_width == 0.4


def test_primitives_inside_bounds(sym):
    for p in sym.primitives:
        if isinstance(p, Text):
            continue
        x0, y0, x1, y1 = _extent(p)
        assert x0 >= -TOL and y0 >= -TOL, (sym.id, p)
        assert x1 <= sym.width + TOL and y1 <= sym.height + TOL, (sym.id, p)


def test_anchor_is_a_point(sym):
    assert sym.anchor in sym.points


def test_points_lie_on_geometry(sym):
    for name, pt in sym.points.items():
        if name in NOT_ON_GEOMETRY:
            continue
        assert _dist_to_all(pt, sym.primitives) <= TOL, (sym.id, name, pt)


@pytest.mark.parametrize("rotation", ROTATIONS)
def test_place_puts_anchor_on_target(sym, rotation):
    x, y = 123.4, 56.7
    assert sym.point(sym.anchor, x, y, rotation) == (x, y)


@pytest.mark.parametrize("rotation", ROTATIONS)
def test_point_agrees_with_placed_geometry(sym, rotation):
    x, y = 123.4, 56.7
    placed = sym.place(x, y, rotation)
    assert len(placed) == len(sym.primitives)
    for name in sym.points:
        if name in NOT_ON_GEOMETRY:
            continue
        pt = sym.point(name, x, y, rotation)
        assert _dist_to_all(pt, placed) <= TOL, (sym.id, name, rotation)
    # rigid motion: distances between points are kept
    names = list(sym.points)
    for a in names:
        for b in names:
            d0 = math.dist(sym.points[a], sym.points[b])
            d1 = math.dist(sym.point(a, x, y, rotation), sym.point(b, x, y, rotation))
            assert d1 == pytest.approx(d0, abs=1e-9)


def test_rotation_is_clockwise_and_validated():
    s = SYMBOLS["breaker"]  # a on top, b below a: rotating 90 clockwise puts b to the left of a
    assert s.point("b", 10, 10, 90) == pytest.approx((0.0, 10.0))
    assert s.point("b", 10, 10, 270) == pytest.approx((20.0, 10.0))
    with pytest.raises(ValueError):
        s.place(0, 0, 45)


def test_scale_from_table():
    unscaled = {"breaker": (3.431, 10.0)}
    assert (SYMBOLS["breaker"].width, SYMBOLS["breaker"].height) == unscaled["breaker"]
    sock = SYMBOLS["socket_protective_conductor"]
    assert sock.width == pytest.approx(4.0 * 0.85)
    assert sock.points["in"] == pytest.approx((2.0 * 0.85, 0.0))
    assert SYMBOLS["light"].width == pytest.approx(4.017 * 0.8)
    assert SYMBOLS["light"].points["in"] == pytest.approx((2.017 * 0.8, 2.0 * 0.8))
    h = next(p for p in SYMBOLS["socket_waterproof"].primitives if isinstance(p, Text))
    assert h.size == pytest.approx(1.411 * 0.85)
