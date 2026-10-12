"""Installation model as validated pydantic classes."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Annotated, Any, Iterator, Literal, Union

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictBool,
    StringConstraints,
    ValidationError,
)

from . import labels
from .errors import HuiselekError


def _num_to_str(v: Any) -> Any:
    return str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v


Id = Annotated[str, BeforeValidator(_num_to_str), StringConstraints(min_length=1)]
Text = Annotated[str, BeforeValidator(_num_to_str)]  # numbers typed in YAML become text
Positive = Annotated[int, Field(strict=True, gt=0)]
Curve = Literal["B", "C", "D"]
Poles = Literal["1P", "1P+N", "2P", "3P", "3P+N", "4P"]
DiffType = Literal["AC", "A", "F", "B"]
Voltage = Literal["230V", "3x230V", "3N400V"]
Variant = Literal["child_protection", "protective_conductor", "waterproof"]
ApplianceType = Literal[
    "oven", "dishwasher", "washing_machine", "dryer",
    "stove", "water_heater", "heating_device", "ev_charger",
]  # fmt: skip


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExtraItem(_Base):
    label: Text
    value: Text


class Project(_Base):
    address: Text
    drawn_by: Text
    executed_by: Text
    version: Text | None = None
    date: str | datetime.date | None = None  # kept as given
    extra: list[ExtraItem] = []


class PageDef(_Base):
    id: Id
    title: Text


class Node(_Base):
    kind: str
    id: Id


class _Parent(Node):
    children: list[AnyNode] = []


class Container(_Parent):
    page: Id | None = None
    link_text: Text | None = None


class Supply(Container):
    kind: Literal["supply"]
    label: Text
    voltage: Voltage


class Breaker(Container):
    kind: Literal["breaker"]
    rating_a: Positive
    label: Text | None = None
    curve: Curve | None = None
    poles: Poles | None = None
    cable: Text | None = None
    conductors: Positive | None = None


class Differential(Container):
    kind: Literal["differential"]
    sensitivity_ma: Positive
    rating_a: Positive
    poles: Poles
    type: DiffType
    selective: StrictBool = False
    label: Text | None = None


class Circuit(Container):
    kind: Literal["circuit"]
    description: Text
    rating_a: Positive
    curve: Curve = "C"
    poles: Poles | None = None
    cable: Text | None = None
    conductors: Positive | None = None
    children_page: Id | None = None


class Board(Container):
    kind: Literal["board"]
    label: Text


class Reserve(Node):
    kind: Literal["reserve"]
    rating_a: Positive | None = None  # None: a free place
    curve: Curve | None = None
    poles: Poles | None = None


class Socket(Node):
    kind: Literal["socket"]
    count: Positive = 1
    variant: Variant = "child_protection"
    note: Text | None = None


class Light(Node):
    kind: Literal["light"]
    switch: StrictBool = False
    name: Text | None = None
    count: Positive = 1


class Appliance(Node):
    kind: Literal["appliance"]
    type: ApplianceType
    note: Text | None = None


class ImpulseRelay(_Parent):
    kind: Literal["impulse_relay"]


class PhotoDetector(_Parent):
    kind: Literal["photo_detector"]


class Transformer(Node):
    kind: Literal["transformer"]


class Converter(Node):
    kind: Literal["converter"]


class Box(Node):
    kind: Literal["box"]
    label: Text


AnyNode = Annotated[
    Union[Supply, Breaker, Differential, Circuit, Board, Reserve, Socket, Light,
          Appliance, ImpulseRelay, PhotoDetector, Transformer, Converter, Box],
    Field(discriminator="kind"),
]  # fmt: skip

# Parent kind -> kinds allowed as its children. Kinds missing here take none.
_DEVICES = {"socket", "light", "appliance", "impulse_relay", "photo_detector",
            "transformer", "converter", "box"}  # fmt: skip
_PROTECTION = {"differential", "breaker", "circuit", "reserve"}
ALLOWED_CHILDREN: dict[str, set[str]] = {
    "supply": {"breaker", "differential"},
    "breaker": _PROTECTION,
    "differential": _PROTECTION,
    "board": _PROTECTION,
    "circuit": _DEVICES | {"circuit", "board"},
    "impulse_relay": _DEVICES - {"impulse_relay", "photo_detector"},
    "photo_detector": _DEVICES - {"impulse_relay", "photo_detector"},
}

for _cls in (_Parent, Container, Supply, Breaker, Differential, Circuit, Board,
             ImpulseRelay, PhotoDetector):  # fmt: skip
    _cls.model_rebuild()


class _File(_Base):
    project: Project
    pages: list[PageDef] = Field(min_length=1)
    labels: dict[str, Text] = {}
    installation: AnyNode


@dataclass(frozen=True)
class Installation:
    project: Project
    pages: list[PageDef]
    labels: dict[str, str]
    root: Supply
    node_pages: dict[str, str] = field(default_factory=dict, repr=False)  # node id -> page id

    def nodes(self) -> Iterator[Node]:
        """All nodes, depth first, parents before children."""

        def walk(node: Node) -> Iterator[Node]:
            yield node
            for child in getattr(node, "children", ()):
                yield from walk(child)

        return walk(self.root)

    def page_of(self, node_id: str) -> str:
        """ID of the page the node is drawn on (own `page`, else inherited)."""
        return self.node_pages[node_id]


# --- error mapping -------------------------------------------------------

_KIND_ERRORS = {"union_tag_not_found", "union_tag_invalid"}
_SHAPE_ERRORS = {"model_type", "model_attributes_type", "dict_type", "list_type"}
_SECTIONS = ("project", "pages", "labels")


def _usable_id(v: Any) -> str | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return str(v)
    return v if isinstance(v, str) and v else None


def _show(v: Any) -> str | None:
    """A scalar as it is typed in YAML, or None for lists and mappings."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "leeg"
    if isinstance(v, str):
        return f"'{v}'"
    if isinstance(v, (int, float, datetime.date)):
        return str(v)
    return None


def _convert(err: ValidationError, data: dict) -> HuiselekError:
    """First pydantic error -> HuiselekError with the nearest enclosing element ID."""
    e = err.errors()[0]
    etype = e["type"]
    loc = list(e["loc"])
    if etype == "missing":
        code = "missing_field"
    elif etype == "extra_forbidden":
        code = "unknown_field"
    elif etype in _KIND_ERRORS:
        code = "unknown_kind"
    else:
        code = "invalid_value"
    # The failing key itself (absent or unknown) does not enclose anything.
    path = loc[:-1] if code in ("missing_field", "unknown_field") else loc
    element_id = None
    last_key = ""
    cur: Any = data
    for part in path:  # union tags and branch names in loc are not data keys: skipped
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
            last_key = part
        elif isinstance(cur, list) and isinstance(part, int) and part < len(cur):
            cur = cur[part]
        else:
            continue
        if isinstance(cur, dict) and _usable_id(cur.get("id")):
            element_id = _usable_id(cur["id"])
    # cur is now the value at the end of path; for missing/unknown keys that is
    # the mapping that holds (or should hold) the key.
    if code in ("missing_field", "unknown_field"):
        field_name = str(loc[-1])
    elif code == "unknown_kind":
        field_name = "kind"
    else:
        field_name = last_key
    params: dict[str, Any] = {"field": field_name}
    if loc and loc[0] in _SECTIONS:
        params["section"] = loc[0]
    in_tree = bool(loc) and loc[0] == "installation"

    if field_name == "id" and code in ("missing_field", "invalid_value") and (
        in_tree or loc[0] == "pages"
    ):
        params["variant"] = (
            "page_id" if loc[0] == "pages" else "root_id" if element_id is None else "id"
        )
    elif code == "unknown_field":
        children = cur.get("children") if isinstance(cur, dict) else None
        if field_name == "children" and isinstance(children, list) and children:
            first = children[0]
            first_id = _usable_id(first.get("id")) if isinstance(first, dict) else None
            first_kind = first.get("kind") if isinstance(first, dict) else None
            return HuiselekError(
                "child_not_allowed",
                first_id or element_id,
                kind=first_kind if isinstance(first_kind, str) else "?",
                parent_kind=cur.get("kind", "?"),
            )
        if not path:
            params["variant"] = "file"
        elif in_tree:
            params.update(variant="kind", kind=cur.get("kind", "?"))
        else:
            params.update(variant="section", section_name=last_key)
    elif code == "invalid_value":
        if etype in _SHAPE_ERRORS:
            params["expected"] = labels.SHAPES.get(field_name) or labels.SHAPES[
                "list" if etype == "list_type" else "mapping"
            ]
            params["variant"] = "shape_top" if len(loc) == 1 else "shape"
        elif etype == "too_short":
            params["variant"] = "empty"
        elif _show(e.get("input")) is None:
            params["variant"] = "novalue"
        else:
            params["value"] = _show(e.get("input"))
    return HuiselekError(code, element_id, **params)


# --- semantic checks -----------------------------------------------------


def _check(f: _File) -> dict[str, str]:
    """Cross-reference checks; returns node id -> page id."""
    page_ids: set[str] = set()
    for p in f.pages:
        if p.id in page_ids:
            raise HuiselekError("duplicate_id", p.id, what="pagina")
        page_ids.add(p.id)
    for name in f.labels:
        if name not in labels.TEMPLATE_NAMES:
            raise HuiselekError("unknown_label", None, name=name)

    seen: set[str] = set()
    node_pages: dict[str, str] = {}

    def walk(node: Node, parent_kind: str, inherited_page: str) -> None:
        if parent_kind == "installation":
            allowed = {"supply"}
        else:
            allowed = ALLOWED_CHILDREN.get(parent_kind, set())
        if node.kind not in allowed:
            raise HuiselekError(
                "child_not_allowed",
                node.id,
                kind=node.kind,
                parent_kind=parent_kind,
                variant="root" if parent_kind == "installation" else None,
            )
        if node.id in seen:
            raise HuiselekError("duplicate_id", node.id, what="element")
        seen.add(node.id)
        for field_name in ("page", "children_page"):
            ref = getattr(node, field_name, None)
            if ref is not None and ref not in page_ids:
                raise HuiselekError("unknown_page", node.id, field=field_name, page=ref)
        if getattr(node, "link_text", None) is not None and not (
            getattr(node, "page", None) or getattr(node, "children_page", None)
        ):
            raise HuiselekError("link_text_without_page", node.id)
        # `page` overrides what the parent hands down; `children_page` applies
        # to the children only.
        page = getattr(node, "page", None) or inherited_page
        node_pages[node.id] = page
        child_page = getattr(node, "children_page", None) or page
        for child in getattr(node, "children", ()):
            walk(child, node.kind, child_page)

    walk(f.installation, "installation", f.pages[0].id)
    used = set(node_pages.values())
    for p in f.pages:
        if p.id not in used:
            raise HuiselekError("unused_page", p.id)
    return node_pages


def build_model(data: dict) -> Installation:
    """Validate a plain dict and build the Installation; raises HuiselekError only."""
    if not isinstance(data, dict):  # empty file, list, scalar
        raise HuiselekError("invalid_value", None, variant="file")
    try:
        f = _File.model_validate(data)
    except ValidationError as err:
        if any(e["type"] == "recursion_loop" for e in err.errors()):
            raise RecursionError from None  # too deeply nested; the CLI reports it
        raise _convert(err, data) from None
    node_pages = _check(f)
    return Installation(f.project, f.pages, f.labels, f.installation, node_pages)
