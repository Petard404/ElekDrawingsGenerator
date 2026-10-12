"""Write the candidate golden SVG and a viewable PDF into out/golden/.

Never writes into tests/golden/; copy the candidate there by hand once approved.
"""
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

from golden_pages import primitives_page
from huiselek.render_svg import render_svg
from huiselek.settings import Settings

OUT = Path(__file__).parent.parent / "out" / "golden"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    svg_path = OUT / "primitives_page.svg"
    svg_path.write_text(render_svg(primitives_page(), Settings()), encoding="utf-8", newline="\n")
    c = canvas.Canvas(str(OUT / "primitives_page.pdf"), pagesize=A4)
    renderPDF.draw(svg2rlg(str(svg_path)), c, 0, 0)
    c.showPage()
    c.save()
    print(f"wrote {svg_path} and {OUT / 'primitives_page.pdf'}")


if __name__ == "__main__":
    main()
