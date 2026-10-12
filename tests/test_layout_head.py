"""Head (supply, levels, group), frame and title block of the page layout."""
import datetime

import pytest
from test_layout import APPROX, DATA, S, circuit_dict, drawn, grid, horizontal_lines, node, raw, text

from huiselek.errors import HuiselekError
from huiselek.layout import layout
from huiselek.model import build_model
from huiselek.primitives import Line, Rect, Text
from huiselek.reader import read

HOUSE_A = DATA.parent.parent.parent / "examples" / "house-a-pg1.yaml"
MINIMAL = DATA.parent.parent.parent / "examples" / "minimal.yaml"


@pytest.fixture(scope="module")
def prims():
    return drawn(read(HOUSE_A))


def rects(p):
    return [q for q in p if isinstance(q, Rect)]


def vertical(p, x):
    return [(q.y1, q.y2) for q in p if isinstance(q, Line) and q.x1 == q.x2 == APPROX(x)]


# --- head ---------------------------------------------------------------------


def test_supply_box_as_measured(prims):
    outer, inner = rects(prims)[2:4]  # the frame and the title block come first
    assert (outer.x, outer.y, outer.x + outer.w, outer.y + outer.h) == APPROX((5.7, 5.2, 31.0, 20.1))
    assert (inner.x, inner.y, inner.x + inner.w, inner.y + inner.h) == APPROX((8.3, 6.4, 20.0, 8.8))
    volt = text(prims, "3*230 V")
    assert (volt.x, volt.y, volt.size) == APPROX((20.7, 8.4, 2.12))


def test_supply_label_wraps_inside_the_box(prims):
    first = next(p for p in prims if isinstance(p, Text) and p.x == 8.1 and p.y == APPROX(13.2))
    second = next(p for p in prims if isinstance(p, Text) and p.x == 8.1 and p.y == APPROX(17.6))
    assert first.size == second.size == 3.53
    assert first.text + " " + second.text == "Aansluiting en teller"


def test_feed_and_main_breaker_level(prims):
    assert (APPROX(20.1), APPROX(31.05)) in vertical(prims, 13.4)  # feed from the box to Q0
    wires = horizontal_lines(prims, 31.05)
    assert (APPROX(13.4), APPROX(16.7)) in wires                    # to terminal a
    assert (APPROX(26.7), APPROX(32.94)) in wires                   # on to the loop
    rating = text(prims, "40A")
    assert (rating.x, rating.y) == APPROX((13.4 + 3.2, 31.05 - 5.65))
    labels_ = [p for p in prims if isinstance(p, Text) and p.text == "Hoofd auto 1" and p.x == APPROX(13.4)]
    assert [(p.y, p.size) for p in labels_] == APPROX([(31.05 + 7.4, 2.88)])


def test_return_loop_from_q0_to_the_differential_row(prims):
    assert (APPROX(31.05), APPROX(31.05 + 12.56)) in vertical(prims, 32.94)
    assert (APPROX(31.05 + 12.56), APPROX(57.43)) in vertical(prims, 13.4)
    assert (APPROX(32.94), APPROX(13.4)) in horizontal_lines(prims, 31.05 + 12.56)


def test_d0_and_d1_share_the_first_row(prims):
    wires = horizontal_lines(prims, 57.43)
    assert (APPROX(13.4), APPROX(16.7)) in wires          # D0
    assert (APPROX(26.7), APPROX(42.4)) in wires          # D0 to D1, past the feeder x
    assert (APPROX(42.4), APPROX(45.7)) in wires          # D1 from 42.4
    assert (APPROX(55.7), APPROX(63.53)) in wires         # D1 to the bus
    assert vertical(prims, 63.53)[0][0] == APPROX(57.43)  # the bus starts on the row


def test_differential_texts(prims):
    t1 = text(prims, "300 mA")
    assert (t1.x, t1.y) == APPROX((13.4 + 4.7, 57.43 + 6.8))
    t2 = next(p for p in prims if isinstance(p, Text) and p.text == "4x40 A" and p.x == APPROX(13.4 + 4.7))
    assert t2.y == APPROX(57.43 + 6.8 + 3.6)
    d1 = text(prims, "Diff 1")
    assert (d1.x, d1.y) == APPROX((42.4 + 4.7, 57.43 + 6.8 + 2 * 3.6))
    assert not [p for p in prims if isinstance(p, Text) and p.text.startswith("type")]  # type is ""


def test_longer_chain_moves_the_first_row_down():
    data = raw()
    d0 = node(data, "D0")
    q0 = node(data, "Q0")
    q0["children"] = [{"kind": "breaker", "id": "Q1", "rating_a": 40, "children": [d0]}]
    p = drawn(data)
    # levels on 31.05, 57.1 and the grid line from 83.15 on: line 2 (88.13)
    assert text(p, "I").y == APPROX(grid(2))
    assert (APPROX(13.4), APPROX(16.7)) in horizontal_lines(p, 57.1)          # Q1
    assert (APPROX(13.4), APPROX(16.7)) in horizontal_lines(p, grid(2))       # D0
    assert (APPROX(57.1 + 12.56), APPROX(grid(2))) in vertical(p, 13.4)       # return line of Q1 to D0
    assert (APPROX(57.1), APPROX(57.1 + 12.56)) in vertical(p, 32.94)


def test_second_differential_hangs_on_the_feeder():
    data = raw()
    node(data, "D0")["children"].append(
        {"kind": "differential", "id": "D2", "label": "Diff 2", "sensitivity_ma": 30, "rating_a": 40,
         "poles": "4P", "type": "A", "children": [circuit_dict("X")]})
    p = drawn(data)
    y = grid(3)  # below the bus of D1 (lines 0 to 2)
    assert text(p, "X").y == APPROX(y)
    assert (APPROX(57.43), APPROX(y)) in vertical(p, 34.57)
    assert (APPROX(34.57), APPROX(42.4)) in horizontal_lines(p, y)
    assert (APPROX(42.4), APPROX(45.7)) in horizontal_lines(p, y)
    assert any(a == APPROX(y) for a, _ in vertical(p, 63.53))  # its own bus
    label = text(p, "Diff 2")  # the default templates give "40/0.03A" and "type A" before it
    assert (label.x, label.y) == APPROX((42.4 + 4.7, y + 6.8 + 2 * 3.6))


def test_children_on_another_page_are_skipped():
    data = raw()
    data["pages"].append({"id": "pg2", "title": "Pagina 2"})
    node(data, "D0")["children"].append(
        {"kind": "differential", "id": "D2", "page": "pg2", "sensitivity_ma": 30, "rating_a": 40,
         "poles": "4P", "type": "A", "children": [circuit_dict("X")]})
    pages = layout(build_model(data), S)
    assert [p.id for p in pages] == ["pg1", "pg2"]
    assert not [q for q in pages[0].primitives if isinstance(q, Text) and q.text == "X"]
    assert not vertical(pages[0].primitives, 34.57)  # no feeder without a second child
    assert not [q for q in pages[1].primitives if isinstance(q, Text) and q.size != 4.23]  # frame, title


def test_group_child_without_circuits_is_unsupported():
    data = raw()
    node(data, "D1")["children"] = [{"kind": "reserve", "id": "R1"}]
    with pytest.raises(HuiselekError) as exc:
        layout(build_model(data), S)
    assert (exc.value.code, exc.value.element_id) == ("layout_unsupported", "R1")


def test_minimal_still_builds():
    pages = layout(build_model(read(MINIMAL)), S)
    assert len(pages) == 1 and pages[0].primitives


# --- frame and title block ---------------------------------------------------------


def test_frame_and_title_block_as_measured(prims):
    frame, block = rects(prims)[:2]
    assert (frame.x, frame.y, frame.x + frame.w, frame.y + frame.h) == APPROX((0.5, 0.4, 209.7, 297.1))
    assert frame.style.stroke_width == 0.8
    assert (block.x, block.y, block.x + block.w, block.y + block.h) == APPROX((0.25, 276.6, 209.86, 297.3))
    assert block.style.stroke_width == 0.5
    assert any(isinstance(q, Line) and q.y1 == q.y2 == APPROX(286.95) for q in prims)  # between the rows
    assert (APPROX(276.6), APPROX(297.3)) in vertical(prims, 105.06)


def test_title_block_cells(prims):
    cells = {t.text: (t.x, t.y, t.size) for t in prims if isinstance(t, Text) and t.size == 4.23}
    assert set(cells) == {"Pagina 1: aansluiting", "Straat A 1, 0000 Gemeente",
                          "Getekend door: Ontwerper", "Uitgevoerd door: Installateur"}
    assert cells["Pagina 1: aansluiting"][:2] == APPROX((3.9, 276.6 + 6.3))
    assert cells["Straat A 1, 0000 Gemeente"][:2] == APPROX((108.9, 276.6 + 6.3))
    assert cells["Getekend door: Ontwerper"][:2] == APPROX((3.9, 286.95 + 6.3))


def test_title_block_grows_upward_and_sets_the_content_limit():
    data = raw()
    pages = layout(build_model(data), S)
    assert pages[0].content_limit_y == APPROX(276.6 - 3.0)
    data["project"].update(version="1.0", date=datetime.date(2026, 10, 12),
                           extra=[{"label": "Keuring", "value": "ja"}])
    page = layout(build_model(data), S)[0]
    # three items: one full row (version, date) and one half row (Keuring) above the two rows
    assert page.content_limit_y == APPROX(297.3 - 4 * 10.35 - 3.0)
    texts = {t.text: (t.x, t.y) for t in page.primitives if isinstance(t, Text) and t.size == 4.23}
    top = 297.3 - 4 * 10.35
    assert texts["Keuring: ja"] == APPROX((3.9, top + 6.3))
    assert texts["Versie: 1.0"] == APPROX((3.9, top + 10.35 + 6.3))   # the first item sits on the title row
    assert texts["Datum: 2026-10-12"] == APPROX((108.9, top + 10.35 + 6.3))
    block = [q for q in page.primitives if isinstance(q, Rect)][1]
    assert block.y == APPROX(top)


def test_every_page_has_frame_and_title_block():
    data = raw()
    data["pages"].append({"id": "pg2", "title": "Pagina 2"})
    node(data, "D0")["children"].append(
        {"kind": "differential", "id": "D2", "page": "pg2", "sensitivity_ma": 30, "rating_a": 40,
         "poles": "4P", "type": "A", "children": [circuit_dict("X")]})
    pages = layout(build_model(data), S)
    for page in pages:
        assert len(rects(page.primitives)) >= 2
    assert any(isinstance(t, Text) and t.text == "Pagina 2" for t in pages[1].primitives)
