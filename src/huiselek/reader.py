"""Read the YAML installation description file."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from . import labels
from .errors import HuiselekError


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate keys in a mapping (safe_load keeps the last)."""

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
            seen = set()
            for key_node, _ in node.value:
                try:
                    key = self.construct_object(key_node, deep=True)
                    hash(key)
                except TypeError:
                    break  # unhashable key: let the base class report it
                if key in seen:
                    raise HuiselekError(
                        "yaml_syntax",
                        None,
                        line=key_node.start_mark.line + 1,
                        detail=f"sleutel '{key}' komt meer dan eens voor",
                    )
                seen.add(key)
        return super().construct_mapping(node, deep=deep)


def _describe(err: yaml.YAMLError) -> tuple[object, str]:
    """(1-based line, Dutch detail) for a PyYAML error."""
    problem = " ".join(str(getattr(err, "problem", None) or err).split())
    text = f"{getattr(err, 'context', None) or ''}: {problem}"
    mark = getattr(err, "problem_mark", None)
    for pattern, template, at_start in labels.YAML_PROBLEMS:
        m = re.search(pattern, text)
        if m:
            if at_start and getattr(err, "context_mark", None) is not None:
                mark = err.context_mark  # an unclosed quote: report where it starts
            detail = template.format(*m.groups())
            break
    else:
        detail = labels.YAML_FALLBACK.format(problem)
    return (mark.line + 1 if mark is not None else "?"), detail


def read(path: Path) -> dict:
    """Parse a YAML file; returns whatever YAML gives (build_model checks the shape).

    Raises HuiselekError: file_unreadable (missing, directory, unreadable, not UTF-8)
    or yaml_syntax (parse error or duplicate key, with the 1-based line).
    """
    path = Path(path)
    try:
        # utf-8-sig: UTF-8 with or without BOM (Notepad adds one).
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, ValueError):  # ValueError covers UnicodeDecodeError
        raise HuiselekError("file_unreadable", None, path=str(path)) from None
    try:
        return yaml.load(text, Loader=_UniqueKeyLoader)
    except yaml.YAMLError as err:
        line, detail = _describe(err)
        raise HuiselekError("yaml_syntax", None, line=line, detail=detail) from None
