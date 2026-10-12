"""Dutch strings: drawing texts, label templates and error messages."""

from __future__ import annotations

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
    "link_text_without_page": "{id}: 'link_text' vereist 'page' of 'children_page'",
}

_BAD_ID_UNDER = "een element onder '{id}' heeft geen geldige 'id'"
_BAD_ID_ROOT = "het hoofdelement heeft geen geldige 'id'"
_BAD_ID_PAGE = "een pagina heeft geen geldige 'id'"

ERROR_VARIANTS: dict[str, str] = {
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
CLI_OK = (
    "{file}: geldig, {elements} elementen, aantal pagina's: {pages}. "
    "Tekenen volgt in een latere versie."
)
