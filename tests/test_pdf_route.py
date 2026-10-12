"""Route trial: hand-written SVG pages -> svglib -> one ReportLab canvas -> PDF."""
import logging
import shutil
from pathlib import Path

import pytest
from pypdf import PdfReader
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

DATA = Path(__file__).parent / "data"
OUT = Path(__file__).parent.parent / "out"
A4_W, A4_H = A4  # points


def build_pdf(svg_paths, out_path):
    """Draw each SVG on its own A4 page of a single canvas."""
    c = canvas.Canvas(str(out_path), pagesize=A4)
    for p in svg_paths:
        drawing = svg2rlg(str(p))
        if abs(drawing.width - A4_W) > 0.01 or abs(drawing.height - A4_H) > 0.01:
            drawing.scale(A4_W / drawing.width, A4_H / drawing.height)
            drawing.width, drawing.height = A4_W, A4_H
        renderPDF.draw(drawing, c, 0, 0)
        c.showPage()
    c.save()


@pytest.fixture
def built(tmp_path, caplog):
    with caplog.at_level(logging.WARNING):
        out = tmp_path / "trial.pdf"
        build_pdf([DATA / "route_page1.svg", DATA / "route_page2.svg"], out)
    OUT.mkdir(exist_ok=True)
    shutil.copy(out, OUT / "pdf_route_trial.pdf")
    return PdfReader(str(out))


def test_two_pages_a4(built):
    assert len(built.pages) == 2
    for page in built.pages:
        assert page.mediabox.width == pytest.approx(595.28, abs=0.5)
        assert page.mediabox.height == pytest.approx(841.89, abs=0.5)


def test_text_extractable(built):
    t1 = built.pages[0].extract_text()
    assert "XVB Cca 3G2.5²" in t1
    assert "Stopcontact – keukenwerkblad é Ø" in t1
    assert "Rotated -90" in t1
    assert "Pagina 2: verlichting" in built.pages[1].extract_text()


def test_helvetica_and_no_font_warnings(built, caplog):
    fonts = built.pages[0]["/Resources"]["/Font"]
    base = [fonts[k].get_object()["/BaseFont"] for k in fonts]
    assert "/Helvetica" in base
    msgs = [r.getMessage() for r in caplog.records]
    assert not [m for m in msgs if "font" in m.lower()], msgs
