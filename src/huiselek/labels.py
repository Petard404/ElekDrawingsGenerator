"""Dutch strings: drawing texts, label templates and error messages."""

from __future__ import annotations

from decimal import Decimal

from .errors import HuiselekError

# Names of the label templates a project's `labels` section may override.
# The texts themselves are written from M3 (drawing texts and label templates
# will be added to this module then).
TEMPLATE_NAMES: tuple[str, ...] = (
    "breaker",
    "differential",
    "differential_type",
    "reserve",
    "free_place",
    "link_to",
    "link_from",
    "page_number",
    "supply_voltage",
    "title_address",
    "title_drawn_by",
    "title_executed_by",
    "title_version",
    "title_date",
)

# Default text per template (the official forms); a project's `labels` section overrides it. Fields
# are the node's own (rating_a, curve, ...); an unset field is empty. Derived fields: sensitivity_a
# (sensitivity_ma / 1000 without trailing zeros) and pole_count (4P -> 4). Title templates get {value}.
# A text with line breaks is drawn one line each; an empty text is not drawn at all. Templates the
# layout does not use yet have no default.
TEMPLATES: dict[str, str] = {
    "breaker": "{curve}{rating_a}",
    "differential": "{rating_a}/{sensitivity_a}A",
    "differential_type": "type {type}",
    "supply_voltage": "{voltage}",
    "title_address": "{value}",
    "title_drawn_by": "Getekend door: {value}",
    "title_executed_by": "Uitgevoerd door: {value}",
    "title_version": "Versie: {value}",
    "title_date": "Datum: {value}",
}
TITLE_EXTRA = "{label}: {value}"  # an `extra` item of the project

POLE_COUNT = {"1P": 1, "1P+N": 2, "2P": 2, "3P": 3, "3P+N": 4, "4P": 4}


def _fields(node) -> dict:
    """Template fields of a node (or of a plain mapping): own fields plus the derived ones."""
    fields = dict(node) if isinstance(node, dict) else node.model_dump()
    if fields.get("sensitivity_ma") is not None:
        amps = format(Decimal(fields["sensitivity_ma"]) / 1000, "f")
        fields["sensitivity_a"] = amps.rstrip("0").rstrip(".") if "." in amps else amps
    if fields.get("poles") is not None:
        fields["pole_count"] = POLE_COUNT[fields["poles"]]
    return {k: ("" if v is None else v) for k, v in fields.items()}


def format_template(name: str, overrides: dict[str, str], node) -> str:
    """Text of a label template for a node or mapping: the project's override, else the default."""
    template = overrides.get(name, TEMPLATES[name])
    try:
        return template.format_map(_Params(_fields(node)))
    except (ValueError, KeyError, IndexError, AttributeError, TypeError):
        raise HuiselekError("invalid_template", None, section="labels", name=name) from None


# Error messages, one line each, plain Dutch. ERRORS holds the default text per
# code; ERROR_VARIANTS holds more specific texts, selected by the error's
# "variant" param as "code.variant". {id} is the element ID; without one it is
# the "section" param (project, pages, labels) or "bestand". The other fields
# come from the error's params.
ERRORS: dict[str, str] = {
    "file_unreadable": "Bestand niet gevonden of niet leesbaar: {path}",
    "yaml_syntax": "YAML-fout op regel {line}: {detail}",
    "missing_field": "{id}: verplicht veld '{field}' ontbreekt",
    "unknown_field": "{id}: onbekend veld '{field}'",
    "unknown_kind": "{id}: 'kind' (soort) ontbreekt of is onbekend",
    "invalid_value": "{id}: ongeldige waarde {value} voor veld '{field}'",
    "duplicate_id": "{id}: {what} komt meer dan eens voor",
    "unknown_page": "{id}: pagina '{page}' in veld '{field}' bestaat niet",
    "unused_page": "Pagina '{id}' bevat geen enkel element",
    "child_not_allowed": "{id}: soort '{kind}' is niet toegestaan onder '{parent_kind}'",
    "unknown_label": "Onbekende labelnaam '{name}' in 'labels'",
    "invalid_template": "Ongeldige tekstindeling voor '{name}' in 'labels'",
    "link_text_without_page": "{id}: 'link_text' vereist 'page' of 'children_page'",
    "layout_unsupported": "{id}: soort '{kind}' wordt nog niet getekend",
    "too_many_devices": "{id}: te veel toestellen op één lijn; het laatste past niet meer voor de beschrijving",
    "page_full": "Pagina '{id}' is vol: '{element}' past er niet meer op",
}

_BAD_ID_UNDER = "een element onder '{id}' heeft geen geldige 'id'"
_BAD_ID_ROOT = "het hoofdelement heeft geen geldige 'id'"
_BAD_ID_PAGE = "een pagina heeft geen geldige 'id'"

ERROR_VARIANTS: dict[str, str] = {
    "reference_missing.dir": "Referentiemap niet gevonden: {path}",
    "reference_missing.file": "{id}: bronbestand niet gevonden: {path}",
    "reference_missing.data": "{id}: symboolbestand niet gevonden: {path}",
    "missing_field.id": _BAD_ID_UNDER,
    "missing_field.root_id": _BAD_ID_ROOT,
    "missing_field.page_id": _BAD_ID_PAGE,
    "invalid_value.id": _BAD_ID_UNDER,
    "invalid_value.root_id": _BAD_ID_ROOT,
    "invalid_value.page_id": _BAD_ID_PAGE,
    "invalid_value.file": (
        "Het bestand moet de onderdelen 'project', 'pages' en 'installation' bevatten."
    ),
    "invalid_value.shape_top": "'{field}' heeft de verkeerde vorm; verwacht: {expected}",
    "invalid_value.shape": "{id}: veld '{field}' heeft de verkeerde vorm; verwacht: {expected}",
    "invalid_value.empty": "De lijst '{field}' mag niet leeg zijn",
    "invalid_value.novalue": "{id}: ongeldige waarde voor veld '{field}'",
    "unknown_field.kind": "{id}: veld '{field}' hoort niet bij soort '{kind}'",
    "unknown_field.section": "veld '{field}' hoort niet bij '{section_name}'",
    "unknown_field.file": (
        "Onbekend onderdeel '{field}' in het bestand; "
        "toegestaan zijn 'project', 'pages', 'labels' en 'installation'"
    ),
    "layout_unsupported.nested": (
        "{id}: een automaat met onderliggende elementen moet het laatste element van zijn bus zijn"
    ),
    "layout_unsupported.detector": "{id}: een fotocel met meer dan één lamp wordt nog niet getekend",
    "layout_unsupported.mixed": (
        "{id}: kringen naast differentiëlen of automaten onder één element worden nog niet getekend"
    ),
    "layout_unsupported.group": (
        "{id}: meerdere differentiëlen of automaten onder één element worden nog niet getekend"
    ),
    "child_not_allowed.root": (
        "{id}: het hoofdelement moet soort 'supply' zijn, niet '{kind}'"
    ),
}

# What a section or list should look like, for errors about the wrong shape.
SHAPES: dict[str, str] = {
    "project": "een reeks met 'address', 'drawn_by' en 'executed_by'",
    "pages": "een lijst van pagina's, elk met 'id' en 'title'",
    "labels": "een reeks 'naam: tekst'",
    "installation": "een element met 'kind' en 'id'",
    "extra": "een lijst van paren met 'label' en 'value'",
    "children": "een lijst van elementen, elk met 'kind' en 'id'",
    "list": "een lijst",
    "mapping": "een reeks 'veld: waarde'",
}


class _Params(dict):
    def __missing__(self, key: str) -> str:
        return "?"


def error_message(code: str, element_id: str | None, params: dict) -> str:
    """Dutch one-line message for an error code; missing params show as '?'."""
    variant = params.get("variant")
    template = ERROR_VARIANTS.get(f"{code}.{variant}") if variant else None
    template = template or ERRORS.get(code, "Onbekende fout ({code})")
    values = _Params(params)
    values.setdefault("code", code)
    values["id"] = element_id if element_id is not None else params.get("section", "bestand")
    return template.format_map(values)


# Dutch details for common YAML syntax errors: (regex on "context: problem" as
# PyYAML words it, text with the regex groups as {0}, report the line where the
# construct starts). Anything else gets the fallback with PyYAML's own wording.
YAML_PROBLEMS: list[tuple[str, str, bool]] = [
    (r"found character '\\t'", "een tabteken is niet toegestaan; spring in met spaties", False),
    (r"mapping values are not allowed here",
     "onjuiste inspringing, of een ':' op een plaats waar dat niet mag", False),
    (r"could not find expected ':'",
     "achter een sleutel ontbreekt een ':', of de inspringing klopt niet", False),
    (r"expected <block end>", "onjuiste inspringing", False),
    (r"quoted scalar.*end of stream", "een aanhalingsteken is niet gesloten", True),
    (r"expected ',' or '[\]}]'",
     "een haakje of accolade is niet gesloten, of er ontbreekt een komma", False),
    (r"found undefined alias '(.*)'", "verwijzing naar onbekend anker '*{0}'", False),
    (r"could not determine a constructor for the tag '(.*)'", "onbekende tag '{0}'", False),
]  # fmt: skip
YAML_FALLBACK = "syntaxfout ({0})"

# Command-line texts.
CLI_DESCRIPTION = "Maakt een eendraadschema (AREI) als PDF uit een YAML-beschrijving."
CLI_BUILD_HELP = "Lees een YAML-bestand en maak het schema."
CLI_FILE_HELP = "YAML-bestand met de beschrijving van de installatie"
CLI_OUTPUT_HELP = "pad van het PDF-bestand dat gemaakt wordt"
CLI_ERROR_PREFIX = "Fout: "
CLI_TOO_DEEP = "het bestand is te diep genest"
CLI_WRITE_ERROR = "Kan het bestand niet schrijven: {path}"
CLI_OK = "Schema geschreven: {path} ({pages} pagina's)"

# `symbols` subcommand (symbol review sheet).
CLI_SYMBOLS_HELP = "Maak het controleblad met alle symbolen (officieel, bibliotheek, gegenereerd)."
CLI_SYMBOLS_OUTPUT_HELP = "pad van het PDF-bestand (standaard: out/symbolen.pdf)"
CLI_SYMBOLS_OK = "Controleblad geschreven: {path} ({pages} pagina's)"

# Symbol review sheet texts.
SHEET_TITLE = "AREI symbolen – controleblad"
SHEET_COLUMNS: tuple[str, str, str] = (
    "Officiële afbeelding",
    "Bibliotheek (bron)",
    "Gegenereerd symbool",
)
SHEET_NO_OFFICIAL = "geen officiële afbeelding"
SHEET_PAGE = "Pagina {n} van {total}"
SHEET_SCALE = "schaal {k}x"
SHEET_NOTES: tuple[str, ...] = (
    "Kolom 1: afbeelding uit de officiële AREI-tabel (eigen schaal). Kolom 2: bronbestand uit de "
    "AREI-bibliotheek, ongewijzigd. Kolom 3: het symbool zoals de tool het tekent.",
    "Kolom 2 en 3 staan op dezelfde schaal (per rij vermeld); lijndikte in kolom 3 is vast. "
    "Rode cirkel: verbindingspunt met naam. Blauwe stip: ankerpunt, het punt dat de indeling plaatst.",
)

# Symbol groups of the sheet, in order (ids as in symbol_table.yaml and symbols.CODE_DRAWN).
SYMBOL_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Beveiliging", ("breaker", "differential", "fuse")),
    ("Voeding", ("kwh_meter", "single_phase", "three_phase")),
    ("Leidingen", ("conductors",)),
    ("Stopcontacten", (
        "socket_protective_conductor", "socket_protective_conductor_n", "socket_child_protection",
        "socket_child_protection_n", "socket_waterproof", "socket_waterproof_plain",
    )),
    ("Verlichting en schakelaars", ("light", "light_with_switch", "switch", "impulse_relay")),
    ("Toestellen", (
        "oven", "dishwasher", "washing_machine", "dryer", "stove", "water_heater",
        "heating_device", "ev_charger", "appliance_general",
    )),
    ("Overige", ("transformer", "converter_ac_dc", "converter_dc_ac", "box", "junction_box", "board")),
    ("In code getekend", ("page_link", "photo_detector")),
    ("Domotica (M8)", (
        "push_button", "domotica_detection", "domotica_clock", "domotica_push_button",
        "domotica_wireless", "motor",
    )),
    ("Installatietekens", ("line_in_conduit", "line_in_conduit_in_wall", "line_in_wall", "line_on_wall")),
)
SHEET_OTHER_GROUP = "Niet ingedeeld"

# Dutch symbol names. Where a symbol has an official image the name is the wording of AREI
# table 2.23 (official/images/index.csv, line breaks of the table joined; "Algemene voorstelling"
# etc. kept, "differential" gets a hyphen so it can wrap, "voorgesteld met elektrische toevoerleiding" dropped from the light point).
# Ours, with no official image or wording: page_link, photo_detector, the four domotica_* (named
# after the legend lines of table J), socket_protective_conductor_n and socket_child_protection_n
# (the official wording plus "met aantal (n)").
SYMBOL_NAMES: dict[str, str] = {
    "appliance_general": "Vast elektrisch huishoudtoestel",
    "board": "Algemene voorstelling van een schakel- en verdeelbord",
    "box": "Doos",
    "breaker": "Automatische schakelaar of vermogensschakelaar",
    "conductors": "Elektrische leiding met n geleiders",
    "converter_ac_dc": "Gelijkrichter/omvormer AC <-> DC",
    "converter_dc_ac": "Omvormer DC -> AC",
    "differential": "Differentieelstroom-beschermingsinrichting",
    "dishwasher": "Afwasmachine",
    "domotica_clock": "Domotica: geprogrammeerde sturing",
    "domotica_detection": "Domotica: sturing door detectie",
    "domotica_push_button": "Domotica: lokale sturing door drukknop",
    "domotica_wireless": "Domotica: draadloze sturing",
    "dryer": "Droogkast",
    "ev_charger": "Laadinrichting voor elektrische wegvoertuigen",
    "fuse": "Smeltzekering",
    "heating_device": "Verwarmingstoestel",
    "impulse_relay": "Impulsschakelaar",
    "junction_box": "Verbindingsdoos, aftakdoos, aansluitdoos",
    "kwh_meter": "kWh-teller",
    "light": "Aansluitpunt voor een verlichtingstoestel",
    "light_with_switch": "Verlichtingstoestel met ingebouwde eenpolige schakelaar",
    "line_in_conduit": "Elektrische leiding in een buis",
    "line_in_conduit_in_wall": "Elektrische leiding geplaatst in een buis in een wand",
    "line_in_wall": "Elektrische leiding in een wand",
    "line_on_wall": "Elektrische leiding op een wand",
    "motor": "Motor",
    "oven": "Elektrische oven",
    "page_link": "Paginaverwijzing",
    "photo_detector": "Fotocel (schemerschakelaar)",
    "push_button": "Drukknop",
    "single_phase": "Eenfasige wisselstroom",
    "socket_child_protection": (
        "Contactdoos met contact voor beschermingsgeleider en met kinderbescherming"
    ),
    "socket_child_protection_n": (
        "Contactdoos met contact voor beschermingsgeleider en met kinderbescherming, "
        "met aantal (n)"
    ),
    "socket_protective_conductor": "Contactdoos met contact voor beschermingsgeleider",
    "socket_protective_conductor_n": (
        "Contactdoos met contact voor beschermingsgeleider, met aantal (n)"
    ),
    "socket_waterproof": (
        "Waterdichte contactdoos met contact voor beschermingsgeleider en met kinderbescherming"
    ),
    "socket_waterproof_plain": "Half-waterdichte, waterdichte of hermetische contactdoos",
    "stove": "Elektrisch fornuis",
    "switch": "Schakelaar",
    "three_phase": "Driefasige wisselstroom",
    "transformer": "Transformator",
    "washing_machine": "Wasmachine",
    "water_heater": "Boiler",
}
SHEET_NO_SOURCE = "in code getekend"
