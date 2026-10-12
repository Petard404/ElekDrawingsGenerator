"""Installation marks on cables (`mounting`, docs/layout-notes.md 4.8) and the page number cell."""
import pytest
from test_layout import APPROX, BRANCH, BUS, DATA, LOOP_X, NESTED, S, drawn, grid, node
from test_layout_head import HOUSE_A, vertical

from huiselek.primitives import Line, Polyline, Text, bbox
from huiselek.reader import read
from huiselek.symbols import load_symbols

MOUNTINGS = ["in_wall", "on_wall", "in_conduit", "in_conduit_in_wall"]
SYM = load_symbols(S)
ROW_Y = grid(0)          # circuit I of tests/data/layout_rows.yaml
CABLE = "XVB 3x2.5"


def _pts(p):
    return [(p.x1, p.y1), (p.x2, p.y2)] if isinstance(p, Line) else list(p.points)


def mark(m, cx, y):
    """The expected primitives of a mark: the symbol centred at (cx, y) without its flat line."""
    return [p for p in SYM[f"line_{m}"].place(cx, y, 0)
            if not (isinstance(p, (Line, Polyline)) and all(abs(q[1] - y) < 1e-6 for q in _pts(p)))]


def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def with_mounting(m, nid="I", path=DATA):
    data = read(path)
    node(data, nid)["mounting"] = m
    return drawn(data)


def extra(prims, base):
    """Mark primitives of prims that base does not have (texts moved by the mark are left out)."""
    return [p for p in prims if p not in base and not isinstance(p, Text)]


def cable_text(prims):
    return next(p for p in prims if isinstance(p, Text) and p.text == CABLE and ROW_Y < p.y < ROW_Y + 8)


@pytest.fixture(scope="module")
def base():
    return drawn(read(DATA))


@pytest.mark.parametrize("m", MOUNTINGS)
def test_circuit_row_draws_the_symbol(base, m):
    new = extra(with_mounting(m), base)
    assert new == mark(m, BUS + S.mounting_dx, ROW_Y)


def test_no_mark_without_the_field(base):
    assert extra(drawn(read(DATA)), base) == []
    marks = [p for p in base if isinstance(p, Polyline) and p.style.stroke_width == S.symbol_stroke_mm
             and BUS + 14 < p.points[0][0] < BUS + 24 and ROW_Y - 2.3 < p.points[0][1] < ROW_Y - 0.5]
    assert marks == []


def test_in_wall_marks_span_14_3_to_23_8_and_sit_above_the_line(base):
    boxes = [bbox(p) for p in extra(with_mounting("in_wall"), base)]
    assert min(b[0] for b in boxes) == APPROX(BUS + 14.3, abs=0.01)
    assert max(b[2] for b in boxes) == APPROX(BUS + 23.8, abs=0.01)
    assert max(b[3] for b in boxes) < ROW_Y - 0.5
    assert min(b[1] for b in boxes) == APPROX(ROW_Y - 2.1 * 0.83)


def test_mark_is_drawn_black_at_symbol_stroke(base):
    for p in extra(with_mounting("in_wall"), base):
        assert p.style.stroke == "#000000" and p.style.stroke_width == S.symbol_stroke_mm


@pytest.mark.parametrize("m", MOUNTINGS)
def test_mark_keeps_clear_of_slashes_and_cable_text(base, m):
    prims = with_mounting(m)
    cable = cable_text(prims)
    slashes = [p for p in base if isinstance(p, Polyline) and len(p.points) == 3
               and abs(p.points[1][0] - (BUS + S.conductors_dx)) < 0.01 and abs(p.points[1][1] - ROW_Y) < 0.01]
    assert slashes
    count = next(p for p in prims if isinstance(p, Text) and p.text == "3" and p.y < ROW_Y)
    for p in extra(prims, base):
        assert not overlap(bbox(p), bbox(count))
        assert not overlap(bbox(p), bbox(cable))
        assert not any(overlap(bbox(p), bbox(sl)) for sl in slashes)


def test_count_sits_above_the_marks_centred_on_the_slash(base):
    count = next(p for p in with_mounting("in_wall") if isinstance(p, Text) and p.text == "3" and p.y < ROW_Y)
    assert (count.x, count.y) == APPROX((BUS + S.conductors_dx, ROW_Y + S.conductors_count_marked_dy))
    assert count.anchor == "middle"
    plain = next(p for p in base if isinstance(p, Text) and p.text == "3" and p.y < ROW_Y)   # as before without a mark
    assert (plain.x, plain.y) == APPROX((BUS + S.conductors_dx + S.conductors_count_dx, ROW_Y + S.conductors_count_dy))


def test_on_wall_mark_pushes_the_cable_text_below_it(base):
    prims = with_mounting("on_wall")
    low = max(bbox(p)[3] for p in mark("on_wall", BUS + S.mounting_dx, ROW_Y))
    cable = cable_text(prims)
    assert low > ROW_Y + 1.0                                   # it hangs under the line
    assert cable.y > ROW_Y + S.cable_dy
    assert bbox(cable)[1] == APPROX(low + S.mounting_text_gap)


def test_in_wall_leaves_the_cable_text_where_it_was():
    assert cable_text(with_mounting("in_wall")).y == APPROX(ROW_Y + S.cable_dy)


def test_branching_circuit_mark_is_measured_from_the_branch_x():
    base = drawn(read(NESTED))
    data = read(NESTED)
    node(data, "P")["mounting"] = "in_wall"
    assert extra(drawn(data), base) == mark("in_wall", BRANCH + S.mounting_dx, grid(9))


def test_nested_breaker_mark_is_on_the_return_line():
    base = drawn(read(NESTED))
    data = read(NESTED)
    node(data, "Q32")["mounting"] = "in_wall"
    new = extra(drawn(data), base)
    assert new == mark("in_wall", BUS + S.nested_mounting_dx, grid(3) + S.loop_drop)
    boxes = [bbox(p) for p in new]
    assert max(b[2] for b in boxes) < LOOP_X - 0.5            # clear of the loop wire
    slash = BUS + S.nested_conductors_dx
    arches = sorted((b[0], b[2]) for b in boxes if b[2] - b[0] > 2)
    assert arches[0][1] < slash - 0.5 and slash + 0.5 < arches[1][0]   # the conductors slash lies between
    count = next(p for p in drawn(data) if isinstance(p, Text) and p.text == "5" and p.y < grid(3) + 12.56)
    assert count.x == APPROX(slash) and count.y == APPROX(grid(3) + S.loop_drop + S.conductors_count_marked_dy)
    assert not any(overlap(bbox(count), b) for b in boxes)


def test_house_a_grey_marks_are_not_copied():
    for p in drawn(read(HOUSE_A)):
        if isinstance(p, (Line, Polyline)):
            assert p.style.stroke_width > 0.1


# --- page number cell ---------------------------------------------------------------------


def test_page_number_in_its_own_cell():
    prims = drawn(read(HOUSE_A))
    right = 0.25 + 209.61
    cell_x = right - 32.0
    assert (APPROX(276.6), APPROX(297.3)) in vertical(prims, cell_x)
    number = next(p for p in prims if isinstance(p, Text) and p.text == "Pagina 1 van 1")
    assert number.anchor == "middle" and number.size == S.title_text_size
    assert number.x == APPROX((cell_x + right) / 2)
    assert number.y == APPROX((276.6 + 297.3) / 2 + 1.125)
    mid = [(p.x1, p.x2) for p in prims if isinstance(p, Line) and p.y1 == p.y2 == APPROX(286.95)]
    assert mid == APPROX([(0.25, cell_x)])                    # the line between the base rows stops at the cell


def test_extra_rows_keep_the_full_width():
    data = read(HOUSE_A)
    data["project"].update(version="1.0", date="2026-10-12", extra=[{"label": "Keuring", "value": "ja"}])
    prims = drawn(data)
    top = 297.3 - 4 * 10.35
    right = 0.25 + 209.61
    lines = {round(p.y1, 2): (p.x1, p.x2) for p in prims
             if isinstance(p, Line) and p.y1 == p.y2 and p.x1 == APPROX(0.25)}
    assert lines[round(top + 10.35, 2)] == APPROX((0.25, right))          # above the version/date row
    assert lines[round(top + 20.7, 2)] == APPROX((0.25, right))           # above the page title row
    assert lines[round(top + 31.05, 2)] == APPROX((0.25, right - 32.0))   # between the base rows
    cell = vertical(prims, right - 32.0)
    assert cell == [(APPROX(top + 20.7), APPROX(297.3))]                  # the cell starts at the page title row
