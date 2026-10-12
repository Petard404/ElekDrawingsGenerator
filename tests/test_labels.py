"""Label templates: official defaults, project overrides, derived fields, empty templates."""
import copy

import pytest

from huiselek import labels
from huiselek.errors import HuiselekError
from huiselek.layout import layout
from huiselek.model import build_model
from huiselek.reader import read
from huiselek.settings import Settings
from test_layout import DATA

INST = build_model(read(DATA))
NODES = {n.id: n for n in INST.nodes()}


def fmt(name, node, overrides=None):
    return labels.format_template(name, overrides or {}, node)


def test_official_defaults():
    assert fmt("breaker", NODES["K"]) == "C16"
    assert fmt("differential", NODES["D0"]) == "40/0.3A"
    assert fmt("differential", NODES["D1"]) == "40/0.03A"
    assert fmt("differential_type", NODES["D1"]) == "type A"
    assert fmt("supply_voltage", NODES["SUP"]) == "3x230V"
    assert fmt("title_drawn_by", {"value": "Jan"}) == "Getekend door: Jan"
    assert fmt("title_executed_by", {"value": "Piet"}) == "Uitgevoerd door: Piet"
    assert fmt("title_address", {"value": "Straat 1"}) == "Straat 1"
    assert fmt("title_version", {"value": "1.0"}) == "Versie: 1.0"
    assert fmt("title_date", {"value": "2026-10-12"}) == "Datum: 2026-10-12"
    assert labels.TITLE_EXTRA.format(label="Keuring", value="ja") == "Keuring: ja"


@pytest.mark.parametrize("ma, amps", [(300, "0.3"), (30, "0.03"), (10, "0.01"), (500, "0.5"),
                                      (1000, "1"), (1500, "1.5"), (10000, "10")])
def test_sensitivity_a_has_no_trailing_zeros(ma, amps):
    assert labels.format_template("differential", {}, {"sensitivity_ma": ma, "rating_a": 40}) == f"40/{amps}A"


@pytest.mark.parametrize("poles, count", [("1P", 1), ("1P+N", 2), ("2P", 2), ("3P", 3), ("3P+N", 4), ("4P", 4)])
def test_pole_count(poles, count):
    out = labels.format_template("differential", {"differential": "{pole_count}"}, {"poles": poles})
    assert out == str(count)


def test_project_override_wins_and_keeps_line_breaks():
    overrides = {"differential": "{sensitivity_ma} mA\n{pole_count}x{rating_a} A"}
    assert fmt("differential", NODES["D0"], overrides) == "300 mA\n4x40 A"
    assert fmt("breaker", NODES["K"], INST.labels) == "16A"  # layout_rows.yaml overrides breaker


def test_empty_template_gives_empty_text():
    assert fmt("differential_type", NODES["D1"], {"differential_type": ""}) == ""


# --- malformed templates in the project file ------------------------------------------------

BAD_TEMPLATES = ["{rating_a", "{}", "{0}", "{rating_a.foo}", "{rating_a[0]}", "{voltage!x}", "}"]


def layout_with(templates):
    data = copy.deepcopy(read(DATA))
    data["labels"] = templates
    return layout(build_model(data), Settings())


@pytest.mark.parametrize("template", BAD_TEMPLATES)
def test_malformed_template_is_an_error_not_a_traceback(template):
    with pytest.raises(HuiselekError) as exc:
        layout_with({"breaker": template})
    assert exc.value.code == "invalid_template"
    assert exc.value.element_id is None and exc.value.params["name"] == "breaker"
    msg = str(exc.value)
    assert "\n" not in msg and "breaker" in msg and "labels" in msg


def test_malformed_template_of_another_name():
    with pytest.raises(HuiselekError) as exc:
        layout_with({"supply_voltage": "{voltage!x}"})
    assert (exc.value.code, exc.value.params["name"]) == ("invalid_template", "supply_voltage")
