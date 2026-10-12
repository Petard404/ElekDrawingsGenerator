import os
import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

from huiselek.primitives import Arc, Circle, Line, Polyline, Rect, Style, Text
from huiselek.settings import Settings
from huiselek.symbol_sheet import scale_primitives, wrap_text
from huiselek.symbols import load_symbols

ROOT = Path(__file__).parent.parent


def _run(*args):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    p = subprocess.run(
        [sys.executable, "-m", "huiselek", *map(str, args)],
        capture_output=True, env=env, cwd=ROOT,
    )
    return p.returncode, p.stdout.decode("utf-8"), p.stderr.decode("utf-8")


@pytest.fixture(scope="module")
def sheet(tmp_path_factory):
    out = tmp_path_factory.mktemp("sheet") / "symbolen.pdf"
    code, stdout, stderr = _run("symbols", "-o", out)
    return code, stdout, stderr, out


def test_command_ok(sheet):
    code, stdout, stderr, out = sheet
    assert code == 0, stderr
    assert out.exists()
    assert len(stdout.splitlines()) == 1
    assert f"({len(PdfReader(str(out)).pages)} pagina's)" in stdout


def test_pages_a4(sheet):
    pdf = PdfReader(str(sheet[3]))
    assert len(pdf.pages) > 1
    for page in pdf.pages:
        assert page.mediabox.width == pytest.approx(595.28, abs=0.5)
        assert page.mediabox.height == pytest.approx(841.89, abs=0.5)


def test_every_symbol_id_in_text(sheet):
    text = "\n".join(p.extract_text() for p in PdfReader(str(sheet[3])).pages)
    for sid in load_symbols(Settings()):
        assert sid in text, sid


def test_unwritable_output_is_one_error_line(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x")
    code, stdout, stderr = _run("symbols", "-o", blocker / "sub" / "x.pdf")
    assert code == 1
    assert stderr.startswith("Fout: ") and len(stderr.splitlines()) == 1


def test_scale_primitives():
    thin = Style(stroke_width=0.1)
    prims = (
        Line(1, 2, 3, 4, thin),
        Polyline(((0, 0), (1, 1)), True, Style(stroke_width=0.1, fill="#000000")),
        Arc(1, 1, 2, 10, 90, thin),
        Circle(2, 3, 0.5, thin),
        Rect(1, 1, 2, 3, thin),
        Text(1, 2, "x", 1.5, "middle", 90.0),
    )
    line, poly, arc, circle, rect, text = scale_primitives(prims, 3, 10, 20, stroke_mm=0.3)
    assert (line.x1, line.y1, line.x2, line.y2) == (13, 26, 19, 32)
    assert poly.points == ((10, 20), (13, 23)) and poly.style.fill == "#000000"
    assert (arc.cx, arc.cy, arc.r, arc.start_deg, arc.end_deg) == (13, 23, 6, 10, 90)
    assert (circle.cx, circle.cy, circle.r) == (16, 29, 1.5)
    assert (rect.x, rect.y, rect.w, rect.h) == (13, 23, 6, 9)
    assert (text.x, text.y, text.size, text.anchor, text.rotation) == (13, 26, 4.5, "middle", 90.0)
    for p in (line, poly, arc, circle, rect):
        assert p.style.stroke_width == 0.3  # fixed, not scaled
    assert scale_primitives(prims[:1], 2)[0].style.stroke_width == 0.1  # kept when not given


def test_wrap_text():
    lines = wrap_text("Stopcontact met beschermgeleider en kinderbeveiliging", 34, 2.8)
    assert len(lines) > 1 and " ".join(lines) == "Stopcontact met beschermgeleider en kinderbeveiliging"
    assert wrap_text("Onbreekbaarlangwoord", 5, 2.8) == ["Onbreekbaarlangwoord"]


def test_wrap_text_breaks_long_word_after_hyphen():
    lines = wrap_text("Half-waterdichte, waterdichte of hermetische contactdoos", 20, 2.8)
    assert lines[0] == "Half-" or lines[0].startswith("Half-")
    assert "".join(lines).replace(" ", "") == "Half-waterdichte,waterdichteofhermetischecontactdoos"
    lines = wrap_text("Differentieelstroom-beschermingsinrichting", 34, 2.8)
    assert lines == ["Differentieelstroom-", "beschermingsinrichting"]


def test_missing_source_svg_is_an_error(monkeypatch, tmp_path):
    from huiselek import symbol_sheet
    from huiselek.errors import HuiselekError

    monkeypatch.setattr(symbol_sheet, "REFERENCE_DIR", tmp_path)
    monkeypatch.setattr(symbol_sheet, "OFFICIAL_DIR", tmp_path)
    with pytest.raises(HuiselekError) as err:
        symbol_sheet.build_sheet()
    assert "bronbestand niet gevonden" in str(err.value)


def test_missing_symbol_data_is_an_error(monkeypatch, tmp_path):
    from huiselek import symbols
    from huiselek.errors import HuiselekError

    real = symbols.resources.files("huiselek")
    monkeypatch.setattr(
        symbols.resources, "files",
        lambda pkg: _Pkg(real, tmp_path),
    )
    with pytest.raises(HuiselekError) as err:
        symbols.load_symbols(Settings())
    assert "symboolbestand niet gevonden" in str(err.value)


class _Pkg:
    """The package dir, but with an empty symbol_data folder."""

    def __init__(self, real, empty):
        self._real, self._empty = real, empty

    def __truediv__(self, name):
        return self._empty / name if name == "symbol_data" else self._real / name
