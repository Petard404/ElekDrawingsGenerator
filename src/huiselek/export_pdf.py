"""Place SVG pages onto one ReportLab canvas (one A4 page per SVG string).

svglib refuses absolute image references, so images (and whole SVG files) that must appear
on a page are passed as ``overlays`` and drawn straight onto the canvas after the page.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

from .primitives import Overlay

Link = tuple[float, float, float, float, int]  # Page.links entry: mm, y down, target page number

A4_W, A4_H = A4  # points
MM = 72 / 25.4


def _draw_overlay(c: canvas.Canvas, overlay: Overlay) -> None:
    """Draw an overlay image or SVG file, scaled to fit its box in mm on the canvas."""
    path, x_mm, y_mm, w_mm, h_mm = overlay
    x, w, h = x_mm * MM, w_mm * MM, h_mm * MM
    y = A4_H - (y_mm + h_mm) * MM
    if str(path).lower().endswith(".svg"):
        drawing = svg2rlg(str(path))
        s = min(w / drawing.width, h / drawing.height)
        drawing.scale(s, s)
        drawing.width, drawing.height = drawing.width * s, drawing.height * s
        renderPDF.draw(drawing, c, x + (w - drawing.width) / 2, y + (h - drawing.height) / 2)
    else:
        c.drawImage(str(path), x, y, w, h, preserveAspectRatio=True, anchor="c", mask="auto")


def _page_key(number: int) -> str:
    """Name of the PDF destination for a page number; link annotations jump to it."""
    return f"page{number}"


def export_pdf(
    svgs: list[str],
    out: Path,
    overlays: list[list[Overlay]] | None = None,
    links: list[tuple[Link, ...]] | None = None,
    title: str | None = None,
    author: str | None = None,
) -> None:
    """Write one A4 page per SVG string; ``overlays[i]`` is drawn on top of page i.

    ``links[i]`` holds the clickable rectangles of page i (Page.links: mm, y down, target page
    number); each becomes an invisible link annotation to that page.
    """
    c = canvas.Canvas(str(out), pagesize=A4)
    c.setCreator("huiselek")
    if title:
        c.setTitle(title)
    if author:
        c.setAuthor(author)
    for i, svg in enumerate(svgs):
        c.bookmarkPage(_page_key(i + 1))
        drawing = svg2rlg(BytesIO(svg.encode("utf-8")))
        if abs(drawing.width - A4_W) > 0.01 or abs(drawing.height - A4_H) > 0.01:
            drawing.scale(A4_W / drawing.width, A4_H / drawing.height)
            drawing.width, drawing.height = A4_W, A4_H
        renderPDF.draw(drawing, c, 0, 0)
        for overlay in overlays[i] if overlays else ():
            _draw_overlay(c, overlay)
        for x0, y0, x1, y1, target in links[i] if links else ():
            rect = (x0 * MM, A4_H - y1 * MM, x1 * MM, A4_H - y0 * MM)
            c.linkRect("", _page_key(target), rect, relative=0, thickness=0)
        c.showPage()
    c.save()
