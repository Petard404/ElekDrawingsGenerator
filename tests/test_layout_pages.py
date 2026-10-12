"""Page roots, Naar and Van links, detail page head, page numbers (docs/layout-notes.md 4.1 to 4.6)."""
import copy
from collections import Counter
from pathlib import Path

import pytest
from test_layout import APPROX, S, circuit_dict, node

from huiselek.errors import HuiselekError
from huiselek.layout import layout
from huiselek.model import build_model
from huiselek.primitives import Line, Text
from huiselek.reader import read
from huiselek.render_svg import render_svg

ROOT = Path(__file__).parent.parent
TWO = ROOT / "tests" / "data" / "layout_pages.yaml"
THREE = ROOT / "tests" / "data" / "layout_pages3.yaml"
GOLDEN = Path(__file__).parent / "golden"
EXAMPLES = sorted((ROOT / "examples").glob("*.yaml"))
LIMIT = 276.6 - 3.0                 # content limit of a title block of two rows
FEEDER_END = LIMIT - 16.8
STEM_1 = 63.53 + 34.76 + 7.66       # slot index 1
ID_2 = 63.53 + 34.76 + 2 * 7.66 - 1.0   # ID x of slot index 2


def pages_of(path):
    return layout(build_model(read(path)), S)


def raw(path):
    return copy.deepcopy(read(path))


def texts(page):
    return [p for p in page.primitives if isinstance(p, Text)]


def text(page, txt):
    found = [t for t in texts(page) if t.text == txt]
    assert len(found) == 1, txt
    return found[0]


def lines_at(page, y):
    return [(p.x1, p.x2) for p in page.primitives
            if isinstance(p, Line) and p.y1 == p.y2 == APPROX(y)]


def error_of(data):
    with pytest.raises(HuiselekError) as exc:
        layout(build_model(data), S)
    return exc.value


# --- two pages: a moved differential --------------------------------------------------------


@pytest.fixture(scope="module")
def two():
    return pages_of(TWO)


def test_naar_end_of_the_moved_differential(two):
    p1 = two[0]
    # the feeder runs from the first row to the feeder end, then right to the arrow tip at 63.9
    assert (APPROX(34.57), APPROX(FEEDER_END)) in [(ln.x1, ln.y2) for ln in p1.primitives
                                                    if isinstance(ln, Line) and ln.x1 == ln.x2 == APPROX(34.57)]
    assert (APPROX(34.57), APPROX(63.9)) in lines_at(p1, FEEDER_END)
    first, second = text(p1, "Naar Pg 2"), text(p1, "Ref Diff 2")
    assert (first.x, first.y) == APPROX((63.9 + 6.1, FEEDER_END + 0.7))
    assert (second.x, second.y) == APPROX((first.x, first.y + 3.6))
    assert [k[-1] for k in p1.links] == [2]
    x0, y0, x1, y1, _ = p1.links[0]
    assert x0 < 63.9 < first.x < x1 and y0 < FEEDER_END < y1  # arrow and both texts


def test_the_group_keeps_its_first_child_inline(two):
    p1 = two[0]
    assert (APPROX(42.4), APPROX(45.7)) in lines_at(p1, 57.43)
    assert text(p1, "Diff 1").y == APPROX(57.43 + 6.8 + 2 * 3.6)
    assert not [t for t in texts(p1) if t.text in ("X", "Y")]  # circuits of Diff 2 are on page 2


def test_van_end_and_head_of_the_moved_differential(two):
    p2 = two[1]
    assert (APPROX(8.66), APPROX(42.4)) in lines_at(p2, 57.43)   # Van wire to the differential
    last, first = text(p2, "Ref Diff 2"), text(p2, "Van pg 1")
    assert (last.x, last.y) == APPROX((8.66, 57.43 - 3.1))
    assert (first.x, first.y) == APPROX((8.66, 57.43 - 3.1 - 3.6))
    assert [k[-1] for k in p2.links] == [1]
    # Diff 2 as the last head level: texts at group_x + 4.7, bus at bus_x from the first row
    label = text(p2, "Diff 2")
    assert (label.x, label.y) == APPROX((42.4 + 4.7, 57.43 + 6.8 + 2 * 3.6))
    assert any(isinstance(ln, Line) and ln.x1 == ln.x2 == APPROX(63.53) and ln.y1 == APPROX(57.43)
               and ln.y2 == APPROX(72.78) for ln in p2.primitives)
    assert text(p2, "X").y == APPROX(57.43) and text(p2, "Y").y == APPROX(72.78)


def test_page_numbers(two):
    for i, page in enumerate(two, start=1):
        number = text(page, f"Pagina {i} van 2")
        assert (number.x, number.y) == APPROX((193.86, 286.95 + 1.125))
        assert (number.anchor, number.size) == ("middle", 4.23)


def test_labels_override_link_and_page_number_templates():
    data = raw(TWO)
    data["labels"].update(link_to="Verder op {page}", link_from="Terug naar {page}",
                          page_number="{number}/{total}")
    one, two_ = layout(build_model(data), S)
    text(one, "Verder op 2")
    text(one, "1/2")
    text(two_, "Terug naar 1")


# --- three pages: a detail page --------------------------------------------------------------


@pytest.fixture(scope="module")
def three():
    return pages_of(THREE)


def test_naar_end_of_a_circuit_with_a_detail_page(three):
    p2 = three[1]
    first, second = text(p2, "Naar Pg 3"), text(p2, "verlichting gelijkvloers")
    assert (first.x, first.y) == APPROX((ID_2, 57.43 + 0.7))
    assert second.y == APPROX(first.y + 3.6)
    assert (APPROX(63.53 + 13.3), APPROX(STEM_1)) in lines_at(p2, 57.43)  # breaker to the arrow tip
    assert any(t.text == "16A" and t.y == APPROX(57.43 - 5.65) for t in texts(p2)) and text(p2, "XVB 3x1.5")
    assert [k[-1] for k in p2.links if k[-1] == 3] == [3]
    assert not [t for t in texts(p2) if t.text in ("A1", "A2")]  # lights are on page 3


def test_van_end_and_header_of_a_detail_page(three):
    p3 = three[2]
    start = 71.48 - 14.6
    assert (APPROX(start), APPROX(71.48)) in lines_at(p3, 57.43)
    last, first = text(p3, "verlichting gelijkvloers"), text(p3, "Van pg 2")
    assert (last.x, last.y) == APPROX((start, 57.43 - 3.1))
    assert (first.x, first.y) == APPROX((start, 57.43 - 3.1 - 3.6))
    header = text(p3, "A")
    assert (header.x, header.y, header.size) == APPROX((141.30, 57.43 - 4.9, 2.88))
    assert [k[-1] for k in p3.links] == [2]


BUS = 71.48
ROWS = [57.43 + i * 15.35 for i in range(5)]
BLADE = (BUS + 21.95, BUS + 21.95 + 5.62)


def blades(page, y):
    return [p for p in page.primitives if isinstance(p, Line) and p.x1 == APPROX(BLADE[0])
            and p.x2 == APPROX(BLADE[1]) and p.y1 == APPROX(y) and p.y2 == APPROX(y + 3.14)]


def test_detail_rows_lie_on_the_grid_and_the_bus_joins_them(three):
    p3 = three[2]
    ys = [text(p3, t).y for t in ("A1 Garage voor", "A2 Garage achter", "A3 Gang", "A4 Spots zithoek", "A5")]
    assert ys == APPROX(ROWS)
    assert any(isinstance(p, Line) and p.x1 == p.x2 == APPROX(BUS) and p.y1 == APPROX(ROWS[0])
               and p.y2 == APPROX(ROWS[-1]) for p in p3.primitives)


def test_the_contact_is_drawn_only_for_a_switched_light(three):
    p3 = three[2]
    assert [bool(blades(p3, y)) for y in ROWS] == [True, True, False, True, False]
    # without a contact the wire runs straight from the bus to the light centre
    assert (APPROX(BUS), APPROX(BUS + 47.87)) in lines_at(p3, ROWS[2])
    # with one it stops at the contact and resumes 6.38 further
    assert (APPROX(BUS), APPROX(BUS + 21.95)) in lines_at(p3, ROWS[0])
    assert (APPROX(BUS + 21.95 + 6.38), APPROX(BUS + 47.87)) in lines_at(p3, ROWS[0])


def test_detail_row_text_and_light(three):
    p3 = three[2]
    label = text(p3, "A1 Garage voor")
    assert (label.x, label.y, label.size) == APPROX((141.30, ROWS[0], 2.88))
    assert text(p3, "A5").x == APPROX(141.30)  # a light without a name: just the ID
    cross = [p for p in p3.primitives if isinstance(p, Line) and p.y1 != p.y2
             and p.x1 != p.x2 and abs(p.y1 - ROWS[2]) < 3 and p.x1 > BUS + 40]
    assert len(cross) == 2 and all(min(p.x1, p.x2) < BUS + 47.87 < max(p.x1, p.x2) for p in cross)
    assert not [t for t in texts(p3) if t.text in ("A1", "A2")]  # no separate ID


def test_detail_count_text(three):
    p3 = three[2]
    count = text(p3, "2")
    assert (count.x, count.y, count.size) == APPROX((BUS + 47.87 + 2.2, ROWS[3] + 0.6, 1.73))
    assert [t.text for t in texts(p3) if t.text.isdigit()] == ["2"]


def test_detail_row_text_follows_the_template():
    data = raw(THREE)
    data.setdefault("labels", {})["detail_row"] = "{name} ({id})"
    p3 = layout(build_model(data), S)[2]
    named = [t.text for t in texts(p3) if "(" in t.text]
    assert named and all(t.endswith(")") for t in named)


def test_a_child_that_is_not_a_light_is_unsupported_on_a_detail_page():
    data = raw(THREE)
    node(data, "A")["children"].append({"kind": "socket", "id": "A9"})
    err = error_of(data)
    assert (err.code, err.element_id) == ("layout_unsupported", "A9")


def test_too_many_detail_rows_are_page_full():
    data = raw(THREE)
    node(data, "A")["children"] = [{"kind": "light", "id": f"L{i}"} for i in range(20)]
    err = error_of(data)
    assert (err.code, err.element_id) == ("page_full", "pg3")
    assert err.params["element"] == "L14"  # rows 0..13 fit; row 14 (y 272.3) has its text past the content limit 273.6


# --- pairing -----------------------------------------------------------------------------------


def link_ends(pages):
    """(kind, own page, other page, link text lines) per link rectangle, read from the output only."""
    ends = []
    for page in pages:
        for x0, y0, x1, y1, target in page.links:
            inside = sorted((t for t in texts(page) if x0 <= t.x <= x1 and y0 <= t.y <= y1),
                            key=lambda t: t.y)
            kind, number = inside[0].text.split()[0], inside[0].text.split()[-1]
            assert kind in ("Naar", "Van") and number == str(target), inside[0].text
            ends.append((kind, page.number, target, tuple(t.text for t in inside[1:])))
    return ends


@pytest.mark.parametrize("path", [TWO, THREE, *EXAMPLES], ids=lambda p: p.name)
def test_every_naar_has_exactly_one_van_and_the_reverse(path):
    ends = link_ends(pages_of(path))
    naar = Counter((src, dst, extra) for kind, src, dst, extra in ends if kind == "Naar")
    van = Counter((dst, src, extra) for kind, src, dst, extra in ends if kind == "Van")
    assert naar == van
    assert all(n == 1 for n in naar.values())


def test_the_two_page_files_have_links():
    assert len(link_ends(pages_of(TWO))) == 2
    assert len(link_ends(pages_of(THREE))) == 4


# --- errors ---------------------------------------------------------------------------------------


def moved_diff(did, children):
    return {"kind": "differential", "id": did, "page": "pg2", "sensitivity_ma": 30, "rating_a": 40,
            "poles": "4P", "type": "A", "children": children}


def test_two_roots_on_one_page_are_unsupported():
    data = raw(TWO)
    node(data, "D0")["children"].append(moved_diff("D3", [circuit_dict("Z")]))
    err = error_of(data)
    assert (err.code, err.element_id) == ("layout_unsupported", "D3")


def test_two_detail_circuits_on_one_page_are_unsupported():
    data = raw(THREE)
    node(data, "B")["children_page"] = "pg3"
    err = error_of(data)
    assert (err.code, err.element_id) == ("layout_unsupported", "B")


def test_circuit_with_a_detail_page_and_devices_on_its_own_page_is_unsupported():
    data = raw(THREE)
    node(data, "A")["children"].append({**circuit_dict("A9"), "page": "pg2"})
    err = error_of(data)
    assert (err.code, err.element_id) == ("layout_unsupported", "A")


def test_a_second_moved_sibling_is_unsupported():
    data = raw(TWO)
    data["pages"].append({"id": "pg3", "title": "Pagina 3"})
    d3 = moved_diff("D3", [circuit_dict("Z")])
    d3["page"] = "pg3"
    node(data, "D0")["children"].append(d3)
    err = error_of(data)
    assert (err.code, err.element_id) == ("layout_unsupported", "D3")


def add_page(data, pid):
    data["pages"].append({"id": pid, "title": f"Pagina {pid}"})


def test_a_second_moved_sibling_has_its_own_message():
    data = raw(TWO)
    add_page(data, "pg3")
    d3 = moved_diff("D3", [circuit_dict("Z")])
    d3["page"] = "pg3"
    node(data, "D0")["children"].append(d3)
    assert "meerdere onderliggende elementen op een andere pagina" in str(error_of(data))


def test_a_single_moved_child_directly_under_the_supply_is_unsupported():
    data = raw(TWO)
    data["installation"]["children"] = [{"kind": "breaker", "id": "Q1", "rating_a": 16, "page": "pg2",
                                         "children": [circuit_dict("Z")]}]
    err = error_of(data)
    assert (err.code, err.element_id) == ("layout_unsupported", "Q1")
    assert "verwijzing naar een andere pagina" in str(err)


def test_a_moved_child_next_to_a_kept_child_under_the_supply_is_unsupported():
    data = raw(TWO)
    sup = node(data, "SUP")
    sup["children"].append({"kind": "breaker", "id": "Q9", "rating_a": 16, "page": "pg2",
                            "children": [circuit_dict("Z")]})
    err = error_of(data)
    assert (err.code, err.element_id) == ("layout_unsupported", "SUP")


def test_a_moved_sibling_under_a_breaker_in_the_head_chain_gets_its_naar_and_van():
    data = raw(TWO)
    node(data, "Q0")["children"] = node(data, "D0")["children"]  # SUP > Q0 > [D1, D2 on pg2]
    ends = link_ends(layout(build_model(data), S))
    assert sorted((kind, own, other) for kind, own, other, _ in ends) == [("Naar", 1, 2), ("Van", 2, 1)]


def test_a_moved_child_under_a_group_member_is_unsupported():
    data = raw(TWO)
    add_page(data, "pg3")
    node(data, "D1")["children"].append({"kind": "breaker", "id": "Q9", "rating_a": 16, "page": "pg3",
                                         "children": [circuit_dict("Z")]})
    err = error_of(data)
    assert (err.code, err.element_id) == ("layout_unsupported", "Q9")


def test_a_moved_child_under_a_nested_breaker_is_unsupported():
    data = raw(TWO)
    add_page(data, "pg3")
    moved = {"kind": "breaker", "id": "Q9", "rating_a": 16, "page": "pg3", "children": [circuit_dict("Z")]}
    nested = {"kind": "breaker", "id": "Q8", "rating_a": 16, "children": [circuit_dict("N"), moved]}
    node(data, "D1")["children"].append(nested)
    err = error_of(data)
    assert (err.code, err.element_id) == ("layout_unsupported", "Q9")


def test_a_moved_root_that_moves_a_child_is_unsupported():
    data = raw(TWO)
    add_page(data, "pg3")
    d3 = moved_diff("D3", [circuit_dict("Z")])
    d3["page"] = "pg3"
    node(data, "D2")["children"] = [circuit_dict("Y"), d3]
    err = error_of(data)
    assert (err.code, err.element_id) == ("layout_unsupported", "D3")


def socket_circuit(i):
    return circuit_dict(f"C{i}", [{"kind": "socket", "id": f"S{i}"}])


def test_thirteen_rows_clear_the_feeder_end():
    data = raw(TWO)
    node(data, "D1")["children"] = [socket_circuit(i) for i in range(13)]
    layout(build_model(data), S)


def test_a_row_past_the_feeder_end_is_page_full():
    data = raw(TWO)
    node(data, "D1")["children"] = [socket_circuit(i) for i in range(14)]  # row 13 lies at y 257.0
    err = error_of(data)
    assert (err.code, err.element_id) == ("page_full", "pg1")
    assert err.params["element"] == "D2"


def test_the_same_rows_fit_without_a_moved_sibling():
    data = raw(TWO)
    node(data, "D0")["children"] = node(data, "D0")["children"][:1]
    node(data, "D1")["children"] = [socket_circuit(i) for i in range(14)]
    del data["pages"][1]
    layout(build_model(data), S)


# --- golden ---------------------------------------------------------------------------------------


@pytest.mark.parametrize("n", [1, 2])
def test_two_page_file_matches_golden(n):
    golden = GOLDEN / f"layout_pages_pg{n}.svg"
    if not golden.exists():
        pytest.skip(f"{golden.name} does not exist yet: copy out/golden/{golden.name} there once approved")
    assert render_svg(pages_of(TWO)[n - 1], S).encode("utf-8") == golden.read_bytes()


def test_detail_page_matches_golden():
    golden = GOLDEN / "layout_pages3_pg3.svg"
    if not golden.exists():
        pytest.skip(f"{golden.name} does not exist yet: copy out/golden/{golden.name} there once approved")
    assert render_svg(pages_of(THREE)[2], S).encode("utf-8") == golden.read_bytes()
