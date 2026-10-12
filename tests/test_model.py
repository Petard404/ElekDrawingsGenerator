import datetime
from pathlib import Path

import pytest

from huiselek import labels
from huiselek.errors import HuiselekError
from huiselek.model import ALLOWED_CHILDREN, Installation, build_model
from huiselek.reader import read

DATA = Path(__file__).parent / "data"

# file -> (expected error code, expected element id)
BAD = {
    "bad_missing_field_project_address": ("missing_field", None),
    "bad_missing_field_circuit_rating": ("missing_field", "K"),
    "bad_missing_field_differential_type": ("missing_field", "D1"),
    "bad_missing_field_differential_poles": ("missing_field", "D1"),
    "bad_missing_field_node_id": ("missing_field", "K"),  # parent's id
    "bad_unknown_field_top_level": ("unknown_field", None),
    "bad_unknown_field_socket_page": ("unknown_field", "K1"),
    "bad_unknown_field_typo": ("unknown_field", "K"),
    "bad_unknown_kind_typo": ("unknown_kind", "K1"),
    "bad_unknown_kind_missing": ("unknown_kind", "K1"),
    "bad_invalid_value_poles_text_2": ("invalid_value", "D1"),
    "bad_invalid_value_poles_number": ("invalid_value", "D1"),
    "bad_invalid_value_curve": ("invalid_value", "K"),
    "bad_invalid_value_voltage": ("invalid_value", "SUP"),
    "bad_invalid_value_rating_negative": ("invalid_value", "K"),
    "bad_invalid_value_rating_text": ("invalid_value", "K"),
    "bad_invalid_value_differential_type": ("invalid_value", "D1"),
    "bad_invalid_value_pages_empty": ("invalid_value", None),
    "bad_invalid_value_socket_count_zero": ("invalid_value", "K1"),
    "bad_duplicate_id_node": ("duplicate_id", "K1"),
    "bad_duplicate_id_page": ("duplicate_id", "pg1"),
    "bad_unknown_page_page": ("unknown_page", "D1"),
    "bad_unknown_page_children_page": ("unknown_page", "K"),
    "bad_child_not_allowed_socket_under_differential": ("child_not_allowed", "S1"),
    "bad_child_not_allowed_nested_impulse_relay": ("child_not_allowed", "IR2"),
    "bad_child_not_allowed_root_not_supply": ("child_not_allowed", "SUP"),
    "bad_unknown_label": ("unknown_label", None),
    "bad_link_text_without_page": ("link_text_without_page", "K"),
    "bad_unused_page_pg2": ("unused_page", "pg2"),
    "bad_invalid_value_project_scalar": ("invalid_value", None),
    "bad_invalid_value_labels_list": ("invalid_value", None),
    "bad_invalid_value_date_datetime": ("invalid_value", None),
    "bad_invalid_value_file_list": ("invalid_value", None),
    "bad_invalid_value_file_empty": ("invalid_value", None),
    "bad_invalid_value_node_id_list": ("invalid_value", "K"),  # parent's id
    "bad_missing_field_root_id": ("missing_field", None),
    "bad_unknown_field_children_page_on_breaker": ("unknown_field", "Q1"),
    "bad_child_not_allowed_children_on_leaf": ("child_not_allowed", "K2"),
}

# Codes that build_model does not raise, so they need no bad_*.yaml: the reader codes (task 1.5,
# tested in test_reader.py) and the layout codes (tested in test_layout*.py).
READER_CODES = {"file_unreadable", "yaml_syntax", "layout_unsupported", "too_many_devices",
                "page_full", "invalid_template"}


# valid_minimal.yaml: node id -> page id (page inherited, `page` overrides,
# `children_page` applies to the children of that circuit only).
PAGES = {
    **dict.fromkeys(
        ["SUP", "Q0", "D0", "D1", "K", "K1", "K6", "K7", "IR1", "IR1S", "PD1", "PD1L",
         "TR1", "CV1", "Q1", "O", "O1", "P", "P3", "R1", "R2"], "pg1"),
    **dict.fromkeys(["D2", "A", "C", "C1", "C9", "7"], "pg2"),
    "A1": "pg3",
    **dict.fromkeys(["BD", "D3", "T"], "4"),
}


def load(name: str) -> dict:
    return read(DATA / f"{name}.yaml")


def raw_nodes(node: dict):
    yield node
    for child in node.get("children", []):
        yield from raw_nodes(child)


def test_valid_minimal_builds():
    data = load("valid_minimal")
    inst = build_model(data)
    assert isinstance(inst, Installation)
    nodes = list(inst.nodes())
    assert len(nodes) == len(list(raw_nodes(data["installation"]))) == 31
    assert inst.root.id == "SUP"
    assert all(isinstance(n.id, str) for n in nodes)
    assert "7" in {n.id for n in nodes}  # numeric id typed in YAML
    assert [p.id for p in inst.pages] == ["pg1", "pg2", "pg3", "4"]
    board = next(n for n in nodes if n.id == "BD")
    assert board.page == "4"
    assert {n.id: inst.page_of(n.id) for n in nodes} == PAGES
    assert inst.project.date == datetime.date(2026, 10, 12)
    assert inst.project.extra[0].label == "Keuring"
    assert inst.labels == {"breaker": "{rating_a}A"}


def test_defaults():
    nodes = {n.id: n for n in build_model(load("valid_minimal")).nodes()}
    assert nodes["K"].curve == "C"
    assert nodes["K1"].count == 1 and nodes["K1"].variant == "child_protection"
    assert nodes["K6"].switch is True and nodes["K6"].count == 1
    assert nodes["A1"].count == 1
    assert nodes["D1"].selective is False and nodes["D0"].selective is True
    assert nodes["Q1"].curve == "D"
    assert nodes["R2"].rating_a is None


def test_bad_table_matches_files():
    on_disk = {p.stem for p in DATA.glob("bad_*.yaml")}
    assert on_disk == set(BAD)
    covered = {code for code, _ in BAD.values()}
    assert covered == set(labels.ERRORS) - READER_CODES


@pytest.mark.parametrize("name", sorted(BAD))
def test_bad_file(name):
    code, element_id = BAD[name]
    with pytest.raises(HuiselekError) as exc:
        build_model(load(name))
    assert exc.value.code == code
    assert exc.value.element_id == element_id
    assert str(exc.value)  # message renders


def test_every_error_code_has_message():
    for code, text in labels.ERRORS.items():
        assert text.strip() and "\n" not in text
        assert labels.error_message(code, "X1", {}).strip()


def test_numbers_in_text_fields_become_text():
    data = load("valid_minimal")
    data["project"]["version"] = 4
    data["project"]["extra"][0]["value"] = 1000
    data["pages"][0]["title"] = 1.5
    data["installation"]["label"] = 230
    data["labels"]["breaker"] = 20
    inst = build_model(data)
    assert inst.project.version == "4"
    assert inst.project.extra[0].value == "1000"
    assert inst.pages[0].title == "1.5"
    assert inst.root.label == "230"
    assert inst.labels["breaker"] == "20"


def test_bool_in_text_field_is_invalid():
    data = load("valid_minimal")
    next(n for n in raw_nodes(data["installation"]) if n["id"] == "K")["description"] = True
    with pytest.raises(HuiselekError) as exc:
        build_model(data)
    assert (exc.value.code, exc.value.element_id) == ("invalid_value", "K")


# --- shapes, pages, nesting -------------------------------------------------


def base() -> dict:
    return {
        "project": {"address": "a", "drawn_by": "b", "executed_by": "c"},
        "pages": [{"id": "pg1", "title": "P1"}],
        "installation": {
            "kind": "supply", "id": "SUP", "label": "l", "voltage": "3x230V",
            "children": [{
                "kind": "differential", "id": "D1", "sensitivity_ma": 30,
                "rating_a": 40, "poles": "2P", "type": "A",
                "children": [{
                    "kind": "circuit", "id": "K", "description": "d", "rating_a": 16,
                    "children": [{"kind": "socket", "id": "K1"}],
                }],
            }],
        },
    }


def find(data: dict, node_id: str) -> dict:
    return next(n for n in raw_nodes(data["installation"]) if n["id"] == node_id)


def error_of(data) -> HuiselekError:
    with pytest.raises(HuiselekError) as exc:
        build_model(data)
    return exc.value


def test_base_builds():
    assert len(list(build_model(base()).nodes())) == 4


@pytest.mark.parametrize("data", [None, [], ["a"], "x", 5])
def test_data_not_a_mapping(data):
    err = error_of(data)
    assert (err.code, err.element_id) == ("invalid_value", None)


@pytest.mark.parametrize("section", ["project", "pages", "labels", "installation"])
def test_section_wrong_shape(section):
    data = base()
    data[section] = "A"
    err = error_of(data)
    assert (err.code, err.element_id) == ("invalid_value", None)
    assert err.params["field"] == section


def test_date_datetime_names_field():
    data = base()
    data["project"]["date"] = datetime.datetime(2026, 10, 12, 10, 0)
    err = error_of(data)
    assert (err.code, err.params["field"]) == ("invalid_value", "date")


def test_children_page_on_breaker_is_unknown_field():
    data = base()
    data["installation"]["children"][0] = {
        "kind": "breaker", "id": "Q1", "rating_a": 16, "children_page": "pg1"}
    err = error_of(data)
    assert (err.code, err.element_id, err.params["field"]) == (
        "unknown_field", "Q1", "children_page")


def test_empty_children_on_leaf_is_unknown_field():
    data = base()
    find(data, "K1")["children"] = []
    err = error_of(data)
    assert (err.code, err.element_id) == ("unknown_field", "K1")


def test_link_text_with_children_page_is_valid():
    data = base()
    data["pages"].append({"id": "pg2", "title": "P2"})
    k = find(data, "K")
    k["children_page"] = "pg2"
    k["link_text"] = "zie pagina 2"
    inst = build_model(data)
    assert inst.page_of("K") == "pg1"
    assert inst.page_of("K1") == "pg2"  # child of a children_page circuit


def test_root_defaults_to_first_page():
    data = base()
    data["pages"].append({"id": "pg2", "title": "P2"})
    find(data, "D1")["page"] = "pg2"
    inst = build_model(data)
    assert inst.page_of("SUP") == "pg1"
    assert inst.page_of("D1") == inst.page_of("K") == inst.page_of("K1") == "pg2"


def test_root_page_overrides_default():
    data = base()
    data["pages"].append({"id": "pg2", "title": "P2"})
    data["installation"]["page"] = "pg2"
    find(data, "D1")["page"] = "pg1"
    inst = build_model(data)
    assert inst.page_of("SUP") == "pg2"
    assert inst.page_of("D1") == "pg1"


def test_unused_page():
    data = base()
    data["pages"].append({"id": "pg2", "title": "P2"})
    err = error_of(data)
    assert (err.code, err.element_id) == ("unused_page", "pg2")


def test_examples_minimal_builds():
    inst = build_model(read(Path(__file__).parent.parent / "examples" / "minimal.yaml"))
    assert len(inst.pages) == 1
    assert {inst.page_of(n.id) for n in inst.nodes()} == {"pg1"}


# --- parent/child matrix ----------------------------------------------------

# The spec's kind table, typed out independently of the model.
DEVICES = {"socket", "light", "appliance", "impulse_relay", "photo_detector",
           "transformer", "converter", "box"}
PROTECTION = {"differential", "breaker", "circuit", "reserve"}
SPEC_ALLOWED = {
    "supply": {"breaker", "differential"},
    "breaker": PROTECTION,
    "differential": PROTECTION,
    "board": PROTECTION,
    "circuit": DEVICES | {"circuit", "board"},
    "impulse_relay": DEVICES - {"impulse_relay", "photo_detector"},
    "photo_detector": DEVICES - {"impulse_relay", "photo_detector"},
}
KINDS = sorted(DEVICES | PROTECTION | {"supply", "board"})
MIN_FIELDS = {
    "supply": {"label": "l", "voltage": "3x230V"},
    "breaker": {"rating_a": 16},
    "differential": {"sensitivity_ma": 30, "rating_a": 40, "poles": "2P", "type": "A"},
    "circuit": {"description": "d", "rating_a": 16},
    "board": {"label": "l"},
    "appliance": {"type": "oven"},
    "box": {"label": "l"},
}
# Kinds above a parent, from the root down, so that the parent itself is legal.
ANCESTORS = {
    "supply": [], "breaker": ["supply"], "differential": ["supply"],
    "circuit": ["supply", "breaker"], "reserve": ["supply", "breaker"],
    "board": ["supply", "breaker", "circuit"],
    **{kind: ["supply", "breaker", "circuit"] for kind in DEVICES},
}


def node(kind: str, node_id: str, children=None) -> dict:
    d = {"kind": kind, "id": node_id, **MIN_FIELDS.get(kind, {})}
    if children is not None:
        d["children"] = children
    return d


def tree_with(parent: str, child: str) -> dict:
    top = node(parent, "P", [node(child, "X")])
    for i, kind in reversed(list(enumerate(ANCESTORS[parent]))):
        top = node(kind, f"a{i}", [top])
    data = base()
    data["installation"] = top
    return data


def test_allowed_children_match_spec():
    assert ALLOWED_CHILDREN == SPEC_ALLOWED


@pytest.mark.parametrize("child", KINDS)
@pytest.mark.parametrize("parent", KINDS)
def test_parent_child_matrix(parent, child):
    data = tree_with(parent, child)
    if child in SPEC_ALLOWED.get(parent, set()):
        assert "X" in {n.id for n in build_model(data).nodes()}
    else:
        err = error_of(data)
        assert (err.code, err.element_id) == ("child_not_allowed", "X")


def test_appliance_type_general():
    from huiselek.model import Appliance

    assert Appliance(kind="appliance", id="X1", type="general").type == "general"


def test_socket_variant_waterproof_plain():
    from huiselek.model import Socket

    assert Socket(kind="socket", id="X1", variant="waterproof_plain").variant == "waterproof_plain"
