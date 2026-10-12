"""Overflow errors: too_many_devices and page_full (docs/layout-notes.md 2.8)."""
import pytest
from test_layout import S, circuit_dict, drawn, node, raw
from test_layout_head import HOUSE_A

from huiselek.errors import HuiselekError
from huiselek.layout import layout
from huiselek.model import build_model
from huiselek.reader import read


def socket(sid, **kw):
    return {"kind": "socket", "id": sid, **kw}


def error_of(data):
    with pytest.raises(HuiselekError) as exc:
        layout(build_model(data), S)
    return exc.value


def d1_with(data, circuits):
    node(data, "D1")["children"] = circuits
    return data


def test_nine_sockets_overflow_the_row():
    data = raw()
    node(data, "I")["children"] = [socket(f"I{i}") for i in range(1, 10)]
    err = error_of(data)
    assert (err.code, err.element_id) == ("too_many_devices", "I")


def test_eight_sockets_fit():
    data = raw()
    node(data, "I")["children"] = [socket(f"I{i}") for i in range(1, 9)]
    drawn(data)


def test_a_wide_note_on_the_last_device_counts():
    data = raw()
    node(data, "I")["children"] = [socket(f"I{i}") for i in range(1, 8)] + [
        socket("I8", note="a very long note")]
    assert error_of(data).code == "too_many_devices"


def test_branch_circuit_overflows_from_the_branch_x():
    data = raw()
    # O with three devices branches at slot 3 (x 121.27); P's second device lands at x 163.7
    o = circuit_dict("O", [socket("O1"), socket("O2"), socket("O3"),
                           circuit_dict("P", [socket("P1"), socket("P2")])])
    d1_with(data, [o])
    err = error_of(data)
    assert (err.code, err.element_id) == ("too_many_devices", "P")


def test_branch_circuit_with_one_device_fits():
    data = raw()
    o = circuit_dict("O", [socket("O1"), socket("O2"), socket("O3"), circuit_dict("P", [socket("P1")])])
    drawn(d1_with(data, [o]))


def test_fifteen_circuits_fill_the_page():
    data = raw()
    d1_with(data, [circuit_dict(f"C{i}", [socket(f"S{i}")]) for i in range(15)])
    err = error_of(data)
    assert (err.code, err.element_id) == ("page_full", "pg1")
    assert err.params["element"] == "C14"


def test_fourteen_circuits_fit():
    data = raw()
    drawn(d1_with(data, [circuit_dict(f"C{i}", [socket(f"S{i}")]) for i in range(14)]))


def test_a_long_description_pushes_the_next_row_past_the_limit():
    data = raw()
    circuits = [circuit_dict(f"C{i}") for i in range(13)]
    circuits[11]["description"] = "\n".join(["regel"] * 12)  # runs on to y 270, a row below at 257 collides
    d1_with(data, circuits)
    err = error_of(data)
    assert (err.code, err.element_id) == ("page_full", "pg1")
    assert err.params["element"] == "C12"


def test_many_title_rows_lower_the_limit_below_house_a():
    data = read(HOUSE_A)
    drawn(data)  # fits as it is
    data["project"]["extra"] = [{"label": f"Veld {i}", "value": "x"} for i in range(16)]
    err = error_of(data)
    assert (err.code, err.element_id) == ("page_full", "pg1")


def test_too_many_levels_run_off_the_page():
    data = raw()
    inner = node(data, "Q0")["children"]
    q = {"kind": "breaker", "id": "Q1", "rating_a": 40, "children": inner}
    for i in range(2, 12):
        q = {"kind": "breaker", "id": f"Q{i}", "rating_a": 40, "children": [q]}
    node(data, "Q0")["children"] = [q]
    assert error_of(data).code == "page_full"


def test_messages_are_one_dutch_line():
    for err in (HuiselekError("too_many_devices", "K"), HuiselekError("page_full", "pg1", element="K")):
        msg = str(err)
        assert "\n" not in msg and err.element_id in msg
