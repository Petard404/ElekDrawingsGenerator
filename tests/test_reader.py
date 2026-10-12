from pathlib import Path

import pytest

from huiselek.errors import HuiselekError
from huiselek.reader import read

DATA = Path(__file__).parent / "data"


def test_valid_file_returns_dict():
    data = read(DATA / "valid_minimal.yaml")
    assert isinstance(data, dict)
    assert data["installation"]["id"] == "SUP"


def test_missing_file():
    with pytest.raises(HuiselekError) as exc:
        read(DATA / "does_not_exist.yaml")
    assert exc.value.code == "file_unreadable"


def test_directory():
    with pytest.raises(HuiselekError) as exc:
        read(DATA)
    assert exc.value.code == "file_unreadable"


def test_not_utf8(tmp_path):
    f = tmp_path / "latin1.yaml"
    f.write_bytes("project: caf\xe9\n".encode("latin-1"))
    with pytest.raises(HuiselekError) as exc:
        read(f)
    assert exc.value.code == "file_unreadable"


def test_syntax_error_line():
    with pytest.raises(HuiselekError) as exc:
        read(DATA / "yaml_syntax_error.yaml")
    assert exc.value.code == "yaml_syntax"
    assert exc.value.params["line"] == 3


def test_duplicate_key_line():
    with pytest.raises(HuiselekError) as exc:
        read(DATA / "yaml_duplicate_key.yaml")
    assert exc.value.code == "yaml_syntax"
    assert exc.value.params["line"] == 4
    assert "regel 4" in str(exc.value)


def test_empty_file_reads_as_none(tmp_path):
    f = tmp_path / "empty.yaml"
    f.write_bytes(b"")
    assert read(f) is None  # build_model reports it


def test_tab_file():
    with pytest.raises(HuiselekError) as exc:
        read(DATA / "yaml_tab.yaml")
    assert exc.value.code == "yaml_syntax"
    assert exc.value.params["line"] == 2


@pytest.mark.parametrize(
    "text, line",
    [
        ("a:\n\tb: 1\n", 2),  # tab
        ("a:\n  b: 1\n   c: 2\n", 3),  # indentation
        ("a: b: c\n", 1),  # colon in the wrong place
        ('a: "abc\nb: 2\n', 1),  # unclosed quote, reported where it starts
        ("a: [1, 2\nb: 2\n", 2),  # unclosed bracket
        ("a: {x: 1\nb: 2\n", 2),  # unclosed brace
        ("a: *foo\n", 1),  # undefined alias
        ("a: !foo bar\n", 1),  # unknown tag
    ],
)
def test_common_syntax_errors_have_dutch_detail(tmp_path, text, line):
    f = tmp_path / "x.yaml"
    f.write_text(text, encoding="utf-8")
    with pytest.raises(HuiselekError) as exc:
        read(f)
    assert exc.value.code == "yaml_syntax"
    assert exc.value.params["line"] == line
    assert not exc.value.params["detail"].startswith("syntaxfout")  # not the fallback


def test_other_syntax_errors_use_fallback(tmp_path):
    f = tmp_path / "x.yaml"
    f.write_text("a: @x\n", encoding="utf-8")
    with pytest.raises(HuiselekError) as exc:
        read(f)
    assert exc.value.params["detail"].startswith("syntaxfout (")
