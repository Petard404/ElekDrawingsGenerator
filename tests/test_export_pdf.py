"""Multi-page PDF: page size, text, link annotations to the right pages (docs/layout-notes.md 4.5)."""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

ROOT = Path(__file__).parent.parent
EXAMPLE = ROOT / "examples" / "house-a-multipage.yaml"


@pytest.fixture(scope="module")
def pdf(tmp_path_factory):
    out = tmp_path_factory.mktemp("multipage") / "house-a-multipage.pdf"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    p = subprocess.run([sys.executable, "-m", "huiselek", "build", str(EXAMPLE), "-o", str(out)],
                       capture_output=True, env=env, cwd=ROOT)
    assert p.returncode == 0 and p.stderr == b""
    return PdfReader(str(out))


def link_targets(reader, index):
    """Sorted page indexes (0-based) that the link annotations of page ``index`` point to."""
    targets = []
    for ref in reader.pages[index].get("/Annots", []):
        annot = ref.get_object()
        if annot.get("/Subtype") != "/Link":
            continue
        dest = annot["/Dest"]
        page = dest[0] if isinstance(dest, list) else reader.named_destinations[dest].page
        targets.append(reader.get_page_number(page.get_object() if hasattr(page, "get_object") else page))
    return sorted(targets)


def test_four_a4_pages(pdf):
    assert len(pdf.pages) == 4
    for page in pdf.pages:
        assert float(page.mediabox.width) == pytest.approx(595.28, abs=0.5)
        assert float(page.mediabox.height) == pytest.approx(841.89, abs=0.5)


def test_metadata(pdf):
    assert pdf.metadata.title == "Eendraadschema"
    assert pdf.metadata.author == "Ontwerper"
    assert pdf.metadata.creator == "huiselek"


def test_text_is_extractable(pdf):
    text = [page.extract_text() for page in pdf.pages]
    assert "Naar Pg 2" in text[0]
    assert "Van pg 1" in text[1]
    assert "Naar Pg 3" in text[1] and "Naar Pg 4" in text[1]
    assert "Pagina 4 van 4" in text[3]
    assert "A1 Garage voor" in text[2]


def test_links_point_to_the_right_pages(pdf):
    assert link_targets(pdf, 0) == [1]
    assert link_targets(pdf, 1) == [0, 2, 3]
    assert link_targets(pdf, 2) == [1]
    assert link_targets(pdf, 3) == [1]


def test_link_rectangles_are_inside_the_page_and_invisible(pdf):
    for page in pdf.pages:
        for ref in page.get("/Annots", []):
            annot = ref.get_object()
            x0, y0, x1, y1 = (float(v) for v in annot["/Rect"])
            assert 0 <= x0 < x1 <= 595.5 and 0 <= y0 < y1 <= 842
            assert list(annot["/Border"]) == [0, 0, 0]
