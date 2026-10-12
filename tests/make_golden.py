"""Write the candidate golden SVGs and viewable PDFs into out/golden/.

Never writes into tests/golden/; copy a candidate there by hand once approved.
"""
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

from golden_pages import primitives_page
from huiselek.layout import layout
from huiselek.model import build_model
from huiselek.reader import read
from huiselek.render_svg import render_svg
from huiselek.settings import Settings

OUT = Path(__file__).parent.parent / "out" / "golden"
DATA = Path(__file__).parent / "data"
EXAMPLES = Path(__file__).parent.parent / "examples"


def write(name: str, svg: str) -> None:
    svg_path = OUT / f"{name}.svg"
    svg_path.write_text(svg, encoding="utf-8", newline="\n")
    c = canvas.Canvas(str(OUT / f"{name}.pdf"), pagesize=A4)
    renderPDF.draw(svg2rlg(str(svg_path)), c, 0, 0)
    c.showPage()
    c.save()
    print(f"wrote {svg_path} and {OUT / f'{name}.pdf'}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s = Settings()
    write("primitives_page", render_svg(primitives_page(), s))
    sources = {"layout_rows": DATA / "layout_rows.yaml", "layout_nested": DATA / "layout_nested.yaml",
               "house_a_pg1": EXAMPLES / "house-a-pg1.yaml"}
    for name, path in sources.items():
        write(name, render_svg(layout(build_model(read(path)), s)[0], s))


if __name__ == "__main__":
    main()
