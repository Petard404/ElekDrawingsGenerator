"""Layout of one bus with circuit rows (House A, Diff 1: circuits I, J, K)."""
import copy
from pathlib import Path

import pytest

from huiselek import labels
from huiselek.errors import HuiselekError
from huiselek.layout import description_lines, layout
from huiselek.model import build_model
from huiselek.primitives import Line, Text, bbox
from huiselek.reader import read
from huiselek.render_svg import render_svg
from huiselek.settings import Settings
from huiselek.symbols import load_symbols

DATA = Path(__file__).parent / "data" / "layout_rows.yaml"
NESTED = Path(__file__).parent / "data" / "layout_nested.yaml"
GOLDEN = Path(__file__).parent / "golden" / "layout_rows.svg"
GOLDEN_NESTED = Path(__file__).parent / "golden" / "layout_nested.svg"
HOUSE_A = Path(__file__).parent.parent / "examples" / "house-a-pg1.yaml"
GOLDEN_HOUSE_A = Path(__file__).parent / "golden" / "house_a_pg1.svg"
S = Settings()
APPROX = pytest.approx


def drawn(data, s=S):
    return layout(build_model(data), s)[0].primitives


def raw():
    return copy.deepcopy(read(DATA))


def node(data, node_id):
    """The dict of the node with this ID in the installation tree."""
    todo = [data["installation"]]
    while todo:
        n = todo.pop()
        if n["id"] == node_id:
            return n
        todo.extend(n.get("children", []))
    raise KeyError(node_id)


@pytest.fixture(scope="module")
def prims():
    return drawn(read(DATA))


def text(prims, txt):
    found = [p for p in prims if isinstance(p, Text) and p.text == txt]
    assert len(found) == 1, txt
    return found[0]


def horizontal_lines(prims, y):
    return [(p.x1, p.x2) for p in prims if isinstance(p, Line) and p.y1 == p.y2 == APPROX(y)]


def vertical_lines(prims, y):
    """x of every vertical line that starts at y, sorted."""
    return sorted(p.x1 for p in prims
                  if isinstance(p, Line) and p.x1 == p.x2 and p.y1 == APPROX(y) and p.y2 > p.y1)


def test_one_page_per_page_definition():
    pages = layout(build_model(read(DATA)), S)
    assert [(p.id, p.number, p.title) for p in pages] == [("pg1", 1, "Pagina 1: aansluiting")]


def test_rows_on_the_grid(prims):
    assert [text(prims, c).y for c in "IJK"] == APPROX([57.43, 72.78, 88.13])


def test_bus_runs_from_first_to_last_row(prims):
    bus = [p for p in prims if isinstance(p, Line) and p.x1 == p.x2 == APPROX(63.53)
           and p.y2 - p.y1 > S.row_pitch]
    assert len(bus) == 1
    assert (bus[0].y1, bus[0].y2) == APPROX((57.43, 88.13))


def test_breaker_terminals_at_3_3_and_13_3():
    sym = load_symbols(S)["breaker"]
    origin = (S.bus_x + S.breaker_start_dx, S.first_row_y)
    assert sym.point("a", *origin, 270) == APPROX((63.53 + 3.3, 57.43))
    assert sym.point("b", *origin, 270) == APPROX((63.53 + 13.3, 57.43))


def test_row_wires_and_texts(prims):
    wires = horizontal_lines(prims, 57.43)
    assert (APPROX(63.53), APPROX(66.83)) in wires               # bus to terminal a
    assert (APPROX(76.83), APPROX(113.61)) in wires              # from terminal b to the last stem, I3
    ratings = [p for p in prims if isinstance(p, Text) and p.text == "20A"]
    assert ratings[0].x == APPROX(63.53 + 3.2) and ratings[0].y == APPROX(57.43 - 5.65)
    cable = next(p for p in prims if isinstance(p, Text) and p.text == "XVB 3x2.5")
    assert (cable.x, cable.y) == APPROX((63.53 + 14.4, 57.43 + 2.3))


def test_stems_start_at_98_29_with_pitch_7_66(prims):
    assert vertical_lines(prims, 88.13) == APPROX([98.29 + i * 7.66 for i in range(8)])  # circuit K
    stem = next(p for p in prims if isinstance(p, Line) and p.x1 == p.x2 == APPROX(98.29)
                and p.y1 == APPROX(88.13))
    assert stem.y2 == APPROX(88.13 + 3.9)


def test_circuit_letter_and_description_x(prims):
    for c in "IJK":
        assert text(prims, c).x == 160.95
    desc = text(prims, "Gang + poort")
    assert (desc.x, desc.y) == APPROX((160.95, 57.43 + 3.6))


def test_ids_centred_under_slots(prims):
    for i, name in enumerate(["K1", "K2", "K3", "K4", "K5", "K6"]):
        t = text(prims, name)
        assert t.anchor == "middle"
        assert (t.x, t.y) == APPROX((98.29 + i * 7.66, 88.13 + 9.0))


def test_photo_detector_slot_shows_the_light_below_the_detector(prims):
    k7 = text(prims, "K7")
    assert k7.x == APPROX(98.29 + 6 * 7.66)
    assert k7.y > 88.13 + 9.0 + 5  # lower than the ID of a plain socket
    assert not [p for p in prims if isinstance(p, Text) and p.text == "K7F"]


def test_counts_written_as_number(prims):
    twos = [p for p in prims if isinstance(p, Text) and p.text == "2"]
    assert len(twos) == 2  # J1 and J2
    assert all(p.size == S.count_text_size for p in twos)


def test_conductors_count_beside_the_mark(prims):
    threes = [p for p in prims if isinstance(p, Text) and p.text == "3"]
    assert len(threes) == 3
    assert all(p.x > 63.53 + 18.5 for p in threes)


def test_no_two_text_boxes_overlap(prims):
    boxes = [(p.text, bbox(p)) for p in prims if isinstance(p, Text)]
    for i, (n1, a) in enumerate(boxes):
        for n2, b in boxes[i + 1:]:
            assert not (a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]), (n1, n2)


def test_hanging_low_device_forces_next_row_down_one_pitch():
    tight = Settings(row_pitch=12.0)  # the light under a detector reaches into the next grid line

    def rows(first_children):
        data = raw()
        d1 = node(data, "D1")
        d1["children"] = [c for c in d1["children"] if c["id"] in ("I", "J")]
        node(data, "I")["children"] = first_children
        node(data, "J")["children"] = [{"kind": "socket", "id": "J1"}]
        p = drawn(data, tight)
        return text(p, "I").y, text(p, "J").y

    plain = rows([{"kind": "socket", "id": "I1"}])
    low = rows([{"kind": "photo_detector", "id": "I1F", "children": [{"kind": "light", "id": "I1"}]}])
    assert plain == APPROX((57.43, 57.43 + 12.0))
    assert low == APPROX((57.43, 57.43 + 24.0))


def test_rows_after_a_pushed_row_stay_on_the_grid():
    data = raw()
    node(data, "I")["description"] = "a\nb\nc\nd\ne"  # five lines run into the letter of the next row
    p = drawn(data)
    assert [text(p, c).y for c in "IJK"] == APPROX([57.43, 57.43 + 2 * 15.35, 57.43 + 3 * 15.35])


def test_description_wraps_and_keeps_explicit_breaks():
    lines = description_lines("Garage + lichten buiten en WC voor de tuin en de oprit\nTweede", S)
    assert len(lines) == 3 and lines[-1] == "Tweede"
    assert description_lines("een\nlijn", S) == ["een", "lijn"]


def test_breaker_template_default_and_override():
    inst = build_model(read(DATA))
    circuit = next(n for n in inst.nodes() if n.id == "K")
    assert labels.format_template("breaker", {}, circuit) == "C16"
    assert labels.format_template("breaker", inst.labels, circuit) == "16A"


def test_error_message_names_the_element():
    msg = str(HuiselekError("layout_unsupported", "RES1", kind="reserve"))
    assert "RES1" in msg and "\n" not in msg


# --- layout_unsupported ---------------------------------------------------

CASES = {
    "reserve": ("D1", lambda d: d["children"].append({"kind": "reserve", "id": "R1"}), "R1"),
    "board": ("I", lambda d: d["children"].append({"kind": "board", "id": "B1", "label": "x"}), "B1"),
    "appliance": ("I", lambda d: d["children"].append(
        {"kind": "appliance", "id": "A1", "type": "oven"}), "A1"),
    "impulse_relay": ("I", lambda d: d["children"].append({"kind": "impulse_relay", "id": "IR1"}), "IR1"),
    "detector_two_lights": ("K7F", lambda d: d["children"].append({"kind": "light", "id": "K7B"}), "K7F"),
    "mixed_children": ("D1", lambda d: d["children"].append(
        {"kind": "differential", "id": "D9", "sensitivity_ma": 30, "rating_a": 40,
         "poles": "4P", "type": "A"}), "D1"),
}


@pytest.mark.parametrize("case", CASES)
def test_layout_unsupported(case):
    parent, mutate, element = CASES[case]
    data = raw()
    mutate(node(data, parent))
    with pytest.raises(HuiselekError) as exc:
        layout(build_model(data), S)
    assert exc.value.code == "layout_unsupported"
    assert exc.value.element_id == element


def breaker_dict(bid, children, label=None, rating=32):
    d = {"kind": "breaker", "id": bid, "rating_a": rating, "children": children}
    if label:
        d["label"] = label
    return d


def circuit_dict(cid, children=(), rating=20):
    return {"kind": "circuit", "id": cid, "description": cid.lower(), "rating_a": rating,
            "children": list(children)}


def test_nested_breaker_not_last_is_unsupported():
    data = raw()
    node(data, "D1")["children"].insert(0, breaker_dict("Q9", [circuit_dict("N")]))
    with pytest.raises(HuiselekError) as exc:
        layout(build_model(data), S)
    assert (exc.value.code, exc.value.element_id) == ("layout_unsupported", "Q9")


def test_nested_breaker_not_last_in_a_nested_bus_is_unsupported():
    data = raw()
    inner = breaker_dict("Q8", [circuit_dict("N8")], rating=16)
    node(data, "D1")["children"].append(breaker_dict("Q9", [inner, circuit_dict("N")]))
    with pytest.raises(HuiselekError) as exc:
        layout(build_model(data), S)
    assert (exc.value.code, exc.value.element_id) == ("layout_unsupported", "Q8")


def variant_of(data):
    with pytest.raises(HuiselekError) as exc:
        layout(build_model(data), S)
    return exc.value.element_id, exc.value.params.get("variant")


def test_mixed_variant_only_when_circuits_and_differentials_meet():
    data = raw()
    node(data, "D1")["children"].append(
        {"kind": "differential", "id": "D9", "sensitivity_ma": 30, "rating_a": 40, "poles": "4P", "type": "A"})
    assert variant_of(data) == ("D1", "mixed")


def test_only_differentials_under_a_nested_breaker_is_a_group():
    data = raw()
    node(data, "D1")["children"].append({"kind": "breaker", "id": "Q9", "rating_a": 32, "children": [
        {"kind": "differential", "id": "D9", "sensitivity_ma": 30, "rating_a": 40, "poles": "4P",
         "type": "A"}]})
    assert variant_of(data) == ("Q9", "group")


def test_supply_with_two_children_is_a_group():
    data = raw()
    data["installation"]["children"].append({"kind": "breaker", "id": "Q8", "rating_a": 16})
    assert variant_of(data) == ("SUP", "group")


# --- nested breaker and branching circuits (House A, 32 A and P) -------------------------------

BUS = 63.53
LOOP_X = BUS + 19.64
BRANCH = BUS + 34.76 + 2 * 7.66  # third slot of O


def grid(n):
    return 57.43 + n * 15.35


@pytest.fixture(scope="module")
def nested():
    return drawn(read(NESTED))


def bus_wires(p):
    return sorted((q.y1, q.y2) for q in p
                  if isinstance(q, Line) and q.x1 == q.x2 == APPROX(BUS) and q.y2 - q.y1 > S.row_pitch)


def test_nested_rows_on_the_grid(nested):
    ys = {c: text(nested, c).y for c in "IJKNLMOP"}
    assert ys == APPROX({"I": grid(0), "J": grid(1), "K": grid(2), "N": grid(5), "L": grid(6),
                         "M": grid(7), "O": grid(8), "P": grid(9)})


def test_nested_breaker_texts(nested):
    y = grid(3)
    rating = text(nested, "32A")
    assert (rating.x, rating.y) == APPROX((BUS + 3.2, y - 5.65))
    label = text(nested, "Hoofd auto 1")
    assert (label.x, label.y, label.size) == APPROX((BUS, y + 7.4, 2.88))
    cable = text(nested, "XVB 5x6")
    assert (cable.x, cable.y) == APPROX((BUS + 5.0, y + 12.56 + 2.33))
    count = text(nested, "5")
    assert count.y < y + 12.56  # beside the slash, on the return line


def test_nested_loop_wire(nested):
    y = grid(3)
    assert (APPROX(BUS + 13.3), APPROX(LOOP_X)) in horizontal_lines(nested, y)  # right
    down = [p for p in nested if isinstance(p, Line) and p.x1 == p.x2 == APPROX(LOOP_X)]
    assert [(d.y1, d.y2) for d in down] == APPROX([(y, y + 12.56)])
    back = [tuple(sorted(w)) for w in horizontal_lines(nested, y + 12.56)]
    assert (APPROX(BUS), APPROX(LOOP_X)) in back  # left to the bus


def test_bus_stops_at_the_breaker_and_continues_below_the_return_line(nested):
    assert bus_wires(nested) == APPROX([(grid(0), grid(3)), (grid(3) + 12.56, grid(8))])


def test_branch_x_is_the_third_slot_of_o(nested):
    assert BRANCH == APPROX(113.61, abs=0.01)
    drop = [p for p in nested if isinstance(p, Line) and p.x1 == p.x2 == APPROX(BRANCH)
            and p.y1 == APPROX(grid(8))]
    assert [(d.y1, d.y2) for d in drop] == APPROX([(grid(8), grid(9))])
    assert (APPROX(BUS + 13.3), APPROX(BRANCH)) in horizontal_lines(nested, grid(8))  # O runs on to it


def test_branching_circuit_row_is_measured_from_the_branch_x(nested):
    y = grid(9)
    assert (APPROX(BRANCH), APPROX(BRANCH + 3.3)) in horizontal_lines(nested, y)  # breaker at +3.3
    rating = next(p for p in nested if isinstance(p, Text) and p.text == "20A" and p.y == APPROX(y - 5.65))
    assert rating.x == APPROX(BRANCH + 3.2)
    assert vertical_lines(nested, y) == APPROX([BRANCH + 34.76])  # P3
    assert text(nested, "P").x == 160.95


def test_o_has_a_note_and_p_a_count(nested):
    assert text(nested, "3ph").size == S.count_text_size
    assert text(nested, "P3").x == APPROX(BRANCH + 34.76)


def test_two_level_nested_breaker():
    data = raw()
    inner = breaker_dict("Q2", [circuit_dict("Z", [{"kind": "socket", "id": "Z1"}])], "Binnen", 16)
    outer = breaker_dict("Q1", [circuit_dict("N"), inner], "Buiten")
    node(data, "D1")["children"] = [circuit_dict("A"), outer]  # a sibling, so Q1 is a nested breaker
    p = drawn(data)
    # A on line 0, Q1 on line 1, N on line 3, Q2 on line 4, Z on line 6
    assert [text(p, c).y for c in ("A", "N", "Z")] == APPROX([grid(0), grid(3), grid(6)])
    assert text(p, "Buiten").y == APPROX(grid(1) + 7.4)
    assert text(p, "Binnen").y == APPROX(grid(4) + 7.4)
    assert bus_wires(p) == APPROX([(grid(0), grid(1)), (grid(1) + 12.56, grid(4)),
                                   (grid(4) + 12.56, grid(6))])


def test_nested_branching_circuits():
    data = raw()
    node(data, "I")["children"] = [
        {"kind": "socket", "id": "I1"}, circuit_dict("I2", [circuit_dict("I3")])]
    p = drawn(data)
    assert [text(p, c).y for c in ("I", "I2", "I3", "J")] == APPROX([grid(0), grid(1), grid(2), grid(3)])
    first_branch = BUS + 34.76 + 7.66
    second_branch = first_branch + 34.76  # I2 has no device: its branch x is its first slot
    assert vertical_lines(p, grid(0)) == APPROX([BUS, BUS + 34.76, first_branch])  # bus, I1, branch
    assert vertical_lines(p, grid(1)) == APPROX([second_branch])


def test_a_branch_row_pushed_down_keeps_the_grid():
    data = raw()
    node(data, "I")["children"] = [circuit_dict("I2")]
    node(data, "I")["description"] = "a\nb\nc\nd\ne"  # five lines run into the letter of the next row
    p = drawn(data)
    assert [text(p, c).y for c in ("I", "I2")] == APPROX([grid(0), grid(2)])
    drop = [q for q in p if isinstance(q, Line) and q.x1 == q.x2 == APPROX(BUS + 34.76)
            and q.y1 == APPROX(grid(0))]
    assert [(d.y1, d.y2) for d in drop] == APPROX([(grid(0), grid(2))])


# --- golden ---------------------------------------------------------------


def golden_matches(data_file, golden):
    svg = render_svg(layout(build_model(read(data_file)), S)[0], S)
    assert svg.encode("utf-8") == golden.read_bytes()


@pytest.mark.skipif(not GOLDEN.exists(),
                    reason="tests/golden/layout_rows.svg does not exist yet: copy out/golden/layout_rows.svg "
                           "there once the drawing is approved")
def test_matches_golden_byte_for_byte():
    golden_matches(DATA, GOLDEN)


@pytest.mark.skipif(not GOLDEN_NESTED.exists(),
                    reason="tests/golden/layout_nested.svg does not exist yet: copy "
                           "out/golden/layout_nested.svg there once the drawing is approved")
def test_nested_matches_golden_byte_for_byte():
    golden_matches(NESTED, GOLDEN_NESTED)


@pytest.mark.skipif(not GOLDEN_HOUSE_A.exists(),
                    reason="tests/golden/house_a_pg1.svg does not exist yet: copy "
                           "out/golden/house_a_pg1.svg there once the drawing is approved")
def test_house_a_page_1_matches_golden_byte_for_byte():
    golden_matches(HOUSE_A, GOLDEN_HOUSE_A)
