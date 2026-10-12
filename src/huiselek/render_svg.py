"""Render one page of primitives to SVG text.

Deterministic: fixed attribute order, one number formatter, primitives in list order.
"""
import math
from xml.sax.saxutils import escape, quoteattr

from huiselek.primitives import Arc, Circle, Line, Page, Polyline, Rect, Text
from huiselek.settings import Settings


def fmt(v: float) -> str:
    """Round to 2 decimals, strip trailing zeros and dot, never '-0'. NaN and inf raise ValueError."""
    if not math.isfinite(v):
        raise ValueError(f"cannot format non-finite number {v!r}")
    s = f"{round(v, 2):.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _pt(x: float, y: float) -> str:
    return f"{fmt(x)} {fmt(y)}"


def _style(st) -> str:
    parts = [f'fill="{st.fill}"' if st.fill else 'fill="none"',
             f'stroke="{st.stroke}"',
             f'stroke-width="{fmt(st.stroke_width)}"']
    if st.dash:
        parts.append(f'stroke-dasharray="{" ".join(fmt(d) for d in st.dash)}"')
    return " ".join(parts)


def arc_path(a: Arc) -> str:
    """Path data for an arc; a span of 360 or more is split into two half arcs."""
    span = a.end_deg - a.start_deg

    def point(deg: float) -> tuple[float, float]:
        rad = math.radians(deg)
        return a.cx + a.r * math.cos(rad), a.cy + a.r * math.sin(rad)

    r = fmt(a.r)
    x0, y0 = point(a.start_deg)
    d = f"M {_pt(x0, y0)}"
    if span >= 360:
        xm, ym = point(a.start_deg + 180)
        d += f" A {r} {r} 0 0 1 {_pt(xm, ym)} A {r} {r} 0 0 1 {_pt(x0, y0)}"
    else:
        x1, y1 = point(a.end_deg)
        large = 1 if span > 180 else 0
        d += f" A {r} {r} 0 {large} 1 {_pt(x1, y1)}"
    return d


def _element(p, s: Settings) -> str:
    if isinstance(p, Line):
        return (f'<line x1="{fmt(p.x1)}" y1="{fmt(p.y1)}" x2="{fmt(p.x2)}" '
                f'y2="{fmt(p.y2)}" {_style(p.style)}/>')
    if isinstance(p, Polyline):
        tag = "polygon" if p.closed else "polyline"
        pts = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in p.points)
        return f'<{tag} points="{pts}" {_style(p.style)}/>'
    if isinstance(p, Arc):
        return f'<path d="{arc_path(p)}" {_style(p.style)}/>'
    if isinstance(p, Circle):
        return (f'<circle cx="{fmt(p.cx)}" cy="{fmt(p.cy)}" r="{fmt(p.r)}" '
                f'{_style(p.style)}/>')
    if isinstance(p, Rect):
        return (f'<rect x="{fmt(p.x)}" y="{fmt(p.y)}" width="{fmt(p.w)}" '
                f'height="{fmt(p.h)}" {_style(p.style)}/>')
    if isinstance(p, Text):
        rot = ""
        if p.rotation:
            rot = f' transform="rotate({fmt(p.rotation)} {_pt(p.x, p.y)})"'
        return (f'<text x="{fmt(p.x)}" y="{fmt(p.y)}" '
                f'font-family={quoteattr(s.font_family)} font-size="{fmt(p.size)}" '
                f'text-anchor="{p.anchor}"{rot} fill="{p.fill}">{escape(p.text)}</text>')
    raise TypeError(f"unknown primitive: {type(p).__name__}")


def render_svg(page: Page, s: Settings) -> str:
    w, h = fmt(s.page_width_mm), fmt(s.page_height_mm)
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" '
             f'viewBox="0 0 {w} {h}">']
    lines += [_element(p, s) for p in page.primitives]
    lines.append("</svg>")
    return "\n".join(lines) + "\n"
