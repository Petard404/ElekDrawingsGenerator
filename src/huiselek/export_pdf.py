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

A4_W, A4_H = A4  # points
MM = 72 / 25.4


def _draw_overlay(c: canvas.Canvas, overlay: Overlay) -> None:
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


def export_pdf(
    svgs: list[str],
    out: Path,
    overlays: list[list[Overlay]] | None = None,
) -> None:
    """Write one A4 page per SVG string; ``overlays[i]`` is drawn on top of page i."""
    c = canvas.Canvas(str(out), pagesize=A4)
    for i, svg in enumerate(svgs):
        drawing = svg2rlg(BytesIO(svg.encode("utf-8")))
        if abs(drawing.width - A4_W) > 0.01 or abs(drawing.height - A4_H) > 0.01:
            drawing.scale(A4_W / drawing.width, A4_H / drawing.height)
            drawing.width, drawing.height = A4_W, A4_H
        renderPDF.draw(drawing, c, 0, 0)
        for overlay in overlays[i] if overlays else ():
            _draw_overlay(c, overlay)
        c.showPage()
    c.save()
