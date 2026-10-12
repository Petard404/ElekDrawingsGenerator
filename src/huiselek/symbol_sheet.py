"""The symbol review sheet: per symbol the official AREI image, the library SVG and our symbol.

Pages are built from our own primitives (frame, texts, grid, generated symbols); the official
images and the library SVGs come back as overlays for export_pdf. Units are mm, y down.
"""
from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass, replace
from functools import lru_cache
from importlib import resources
from pathlib import Path

import yaml

from . import labels
from .errors import HuiselekError
from .primitives import Arc, Circle, Line, Overlay, Page, Polyline, Primitive, Rect, Style, Text
from .settings import Settings
from .symbols import Symbol, load_symbols

REFERENCE_DIR = Path(__file__).resolve().parents[2] / "docs" / "reference" / "arei"
OFFICIAL_DIR = REFERENCE_DIR / "official" / "images"

# Page grid (mm).
PAGE_W, PAGE_H = 210.0, 297.0
X_NAME, X_C1, X_C2, X_C3, X_END = 10.0, 46.0, 86.0, 143.0, 200.0
Y_TITLE, Y_COLS, Y_TOP, Y_BOTTOM = 17.0, 27.0, 29.0, 268.0
Y_NOTES, Y_PAGE = 272.0, 287.0

BASE_SCALE = 3.0  # generated symbol is shown about 3x
MIN_EXTENT = 15.0  # ...but at least this big on its longest side (tiny symbols)
MAX_SCALE = 10.0
STROKE_MM = 0.3  # fixed line width of the enlarged symbol
OFFICIAL_MM_PER_PX = 0.3  # official images are never drawn larger than this
GROUP_H = 7.0
MIN_ROW_H = 20.0
POINT_R = 0.8
POINT_TEXT = 1.9
RED, BLUE, GREY, LIGHT = "#d40000", "#0057d9", "#666666", "#bbbbbb"


def scale_primitives(
    primitives: tuple[Primitive, ...],
    factor: float,
    dx: float = 0.0,
    dy: float = 0.0,
    stroke_mm: float | None = None,
) -> tuple[Primitive, ...]:
    """Scale coordinates, radii and text sizes by factor, then translate by (dx, dy).

    Line width becomes stroke_mm when given (it is not scaled); otherwise it is kept.
    """

    def style(st: Style) -> Style:
        return st if stroke_mm is None else replace(st, stroke_width=stroke_mm)

    def pt(x: float, y: float) -> tuple[float, float]:
        return x * factor + dx, y * factor + dy

    out: list[Primitive] = []
    for p in primitives:
        if isinstance(p, Line):
            (x1, y1), (x2, y2) = pt(p.x1, p.y1), pt(p.x2, p.y2)
            out.append(Line(x1, y1, x2, y2, style(p.style)))
        elif isinstance(p, Polyline):
            out.append(Polyline(tuple(pt(*q) for q in p.points), p.closed, style(p.style)))
        elif isinstance(p, Arc):
            cx, cy = pt(p.cx, p.cy)
            out.append(Arc(cx, cy, p.r * factor, p.start_deg, p.end_deg, style(p.style)))
        elif isinstance(p, Circle):
            cx, cy = pt(p.cx, p.cy)
            out.append(Circle(cx, cy, p.r * factor, style(p.style)))
        elif isinstance(p, Rect):
            x, y = pt(p.x, p.y)
            out.append(Rect(x, y, p.w * factor, p.h * factor, style(p.style)))
        elif isinstance(p, Text):
            x, y = pt(p.x, p.y)
            out.append(replace(p, x=x, y=y, size=p.size * factor))
        else:
            raise TypeError(f"unknown primitive {p!r}")
    return tuple(out)


def wrap_text(text: str, width_mm: float, size: float) -> list[str]:
    """Greedy word wrap, estimating Helvetica at 0.52 em per character.

    A word longer than a line is broken after its hyphens (it may stay too long if it has none).
    """
    per_line = max(1, int(width_mm / (size * 0.52)))
    lines: list[str] = []
    cur = ""
    for word in text.split():
        pieces = [word]
        if len(word) > per_line:
            pieces = [w for w in re.split(r"(?<=-)", word) if w]
        for i, piece in enumerate(pieces):
            glue = "" if i else " "  # pieces of one word are joined without a space
            trial = f"{cur}{glue}{piece}" if cur else piece
            if len(trial) <= per_line or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = piece
    return lines + [cur] if cur else lines


def _svg_size(path: Path) -> tuple[float, float]:
    """Width and height in mm from the root element of a library SVG."""
    head = path.read_text(encoding="utf-8")[:600]
    w = re.search(r'\bwidth="([\d.]+)mm"', head)
    h = re.search(r'\bheight="([\d.]+)mm"', head)
    if not (w and h):
        raise ValueError(f"{path.name}: no width/height in mm")
    return float(w.group(1)), float(h.group(1))


@dataclass
class _Row:
    group: str | None  # set for a group heading
    height: float
    symbol: Symbol | None = None
    k: float = 1.0
    k_lib: float = 1.0  # scale of the library SVG (k, or less when it does not fit its cell)
    source: Path | None = None
    images: tuple[Path, ...] = ()


def _official_image(stem: str) -> Path | None:
    for ext in (".jpg", ".png"):
        p = OFFICIAL_DIR / (stem + ext)
        if p.exists():
            return p
    return None


def _bbox(sym: Symbol) -> tuple[float, float, float, float]:
    xs = [0.0, sym.width] + [p[0] for p in sym.points.values()]
    ys = [0.0, sym.height] + [p[1] for p in sym.points.values()]
    return min(xs), min(ys), max(xs), max(ys)


def _plan_row(sym: Symbol, entry: dict | None) -> _Row:
    x0, y0, x1, y1 = _bbox(sym)
    bw, bh = max(x1 - x0, 0.5), max(y1 - y0, 0.5)
    source = REFERENCE_DIR / entry["source"] if entry else None
    if source is not None and not source.exists():
        raise HuiselekError("reference_missing", sym.id, variant="file", path=str(source))
    has_source = source is not None
    lw, lh = _svg_size(source) if has_source else (0.0, 0.0)
    images = tuple(
        p for p in (_official_image(s) for s in (entry or {}).get("official", [])) if p
    )
    k = BASE_SCALE
    if max(bw, bh) * k < MIN_EXTENT:
        k = min(MAX_SCALE, MIN_EXTENT / max(bw, bh))
    k = min(k, (X_END - X_C3 - 6) / bw, 30.0 / bh)
    k = math.floor(k * 10) / 10
    k_lib = k
    if has_source:
        k_lib = math.floor(min(k, (X_C3 - X_C2 - 6) / lw, 30.0 / lh) * 10) / 10
    name_lines = len(wrap_text(labels.SYMBOL_NAMES[sym.id], X_C1 - X_NAME - 2, 2.8)) + 1
    img_rows = math.ceil(len(images) / 2) if len(images) > 1 else 1
    height = max(MIN_ROW_H, max(bh * k, lh * k_lib) + 9, name_lines * 3.2 + 4, img_rows * 16 + 4)
    return _Row(None, height, sym, k, k_lib, source if has_source else None, images)


def _ordered(symbols: dict[str, Symbol]) -> list[tuple[str, list[Symbol]]]:
    groups = [(title, [symbols[i] for i in ids]) for title, ids in labels.SYMBOL_GROUPS]
    listed = {i for _, ids in labels.SYMBOL_GROUPS for i in ids}
    rest = [s for i, s in symbols.items() if i not in listed]
    if rest:
        groups.append((labels.SHEET_OTHER_GROUP, rest))
    return groups


def _paginate(rows: list[_Row]) -> list[list[_Row]]:
    pages: list[list[_Row]] = [[]]
    used = 0.0
    avail = Y_BOTTOM - Y_TOP
    for i, row in enumerate(rows):
        need = row.height + (rows[i + 1].height if row.group and i + 1 < len(rows) else 0)
        if used + need > avail and pages[-1]:
            pages.append([])
            used = 0.0
        pages[-1].append(row)
        used += row.height
    return pages


def _points_layer(sym: Symbol, k: float, tx: float, ty: float) -> list[Primitive]:
    out: list[Primitive] = []
    for i, (name, (px, py)) in enumerate(sym.points.items()):
        x, y = tx + px * k, ty + py * k
        anchor = name == sym.anchor
        colour = BLUE if anchor else RED
        out.append(Circle(x, y, POINT_R, Style(colour, 0.25, colour if anchor else None)))
        # names alternate left/right of the point so that close points do not overwrite each other
        left = i % 2 == 0
        dx = -(POINT_R + 0.5) if left else POINT_R + 0.5
        out.append(Text(x + dx, y - POINT_R - 0.4, name, POINT_TEXT, "end" if left else "start", 0.0, colour))
    return out


@lru_cache(maxsize=1)
def _image_sizes() -> dict[str, tuple[int, int]]:
    """Pixel size per official image file name, from index.csv."""
    with open(OFFICIAL_DIR / "index.csv", encoding="utf-8", newline="") as f:
        return {r["file"]: (int(r["width_px"]), int(r["height_px"])) for r in csv.DictReader(f)}


def _fit_image(path: Path, box: tuple[float, float, float, float]) -> Overlay:
    """Centre an official image in box, at most OFFICIAL_MM_PER_PX per pixel."""
    bx, by, bw, bh = box
    pw, ph = _image_sizes()[path.name]
    s = min(bw / pw, bh / ph, OFFICIAL_MM_PER_PX)
    w, h = pw * s, ph * s
    return (path, bx + (bw - w) / 2, by + (bh - h) / 2, w, h)


def _symbol_row(row: _Row, y: float, prims: list[Primitive], over: list[Overlay]) -> None:
    sym, k = row.symbol, row.k
    mid = y + row.height / 2
    prims.append(Line(X_NAME, y + row.height, X_END, y + row.height, Style(LIGHT, 0.15)))
    lines = wrap_text(labels.SYMBOL_NAMES[sym.id], X_C1 - X_NAME - 2, 2.8)
    for n, line in enumerate(lines):
        prims.append(Text(X_NAME + 1, y + 4.5 + n * 3.2, line, 2.8))
    prims.append(Text(X_NAME + 1, y + 4.5 + len(lines) * 3.2, sym.id, 2.3, fill=GREY))

    # Column 1: official images (grid of up to 2 columns).
    cols = 2 if len(row.images) > 1 else 1
    rows_n = math.ceil(len(row.images) / cols) if row.images else 1
    cw, ch = (X_C2 - X_C1 - 4) / cols, (row.height - 4) / rows_n
    for n, img in enumerate(row.images):
        box = (X_C1 + 2 + (n % cols) * cw, y + 2 + (n // cols) * ch, cw - 1, ch - 1)
        over.append(_fit_image(img, box))
    if not row.images:
        prims.append(Text((X_C1 + X_C2) / 2, mid, labels.SHEET_NO_OFFICIAL, 2.4, "middle", fill=GREY))

    # Column 2: library SVG at the same scale as column 3.
    cx2 = (X_C2 + X_C3) / 2
    if row.source:
        lw, lh = _svg_size(row.source)
        kl = row.k_lib
        over.append((row.source, cx2 - lw * kl / 2, mid - lh * kl / 2, lw * kl, lh * kl))
        if kl != k:  # does not fit its cell at the scale of column 3
            note = labels.SHEET_SCALE.format(k=f"{kl:.1f}".replace(".", ","))
            prims.append(Text(X_C3 - 1, y + row.height - 1.2, note, 2.0, "end", fill=GREY))
    else:
        prims.append(Text(cx2, mid, labels.SHEET_NO_SOURCE, 2.4, "middle", fill=GREY))

    # Column 3: generated symbol, connection points marked.
    x0, y0, x1, y1 = _bbox(sym)
    tx = (X_C3 + X_END) / 2 - k * (x0 + x1) / 2
    ty = mid - k * (y0 + y1) / 2
    prims.extend(scale_primitives(sym.primitives, k, tx, ty, STROKE_MM))
    prims.extend(_points_layer(sym, k, tx, ty))
    scale_txt = labels.SHEET_SCALE.format(k=f"{k:.1f}".replace(".", ","))
    prims.append(Text(X_END - 1, y + row.height - 1.2, scale_txt, 2.0, "end", fill=GREY))


def _page(number: int, total: int, rows: list[_Row]) -> tuple[Page, list[Overlay]]:
    prims: list[Primitive] = [Rect(8, 8, PAGE_W - 16, PAGE_H - 16, Style(stroke_width=0.35))]
    over: list[Overlay] = []
    prims.append(Text(X_NAME, Y_TITLE, labels.SHEET_TITLE, 5.0))
    for x, title in zip((X_C1, X_C2, X_C3), labels.SHEET_COLUMNS):
        prims.append(Text(x + 2, Y_COLS, title, 2.8, fill=GREY))
    prims.append(Line(X_NAME, Y_TOP, X_END, Y_TOP, Style(stroke_width=0.2)))
    y = Y_TOP
    for row in rows:
        if row.group:
            prims.append(Rect(X_NAME, y, X_END - X_NAME, row.height, Style("#eeeeee", 0.1, "#eeeeee")))
            prims.append(Text(X_NAME + 1, y + 4.8, row.group, 3.4))
        else:
            _symbol_row(row, y, prims, over)
        y += row.height
    for x in (X_C1, X_C2, X_C3):
        prims.append(Line(x, Y_TOP, x, y, Style(LIGHT, 0.15)))
    n = 0
    for note in labels.SHEET_NOTES:
        for line in wrap_text(note, X_END - X_NAME, 2.2):
            prims.append(Text(X_NAME, Y_NOTES + n * 3.0, line, 2.2, fill=GREY))
            n += 1
    prims.append(Text(X_END, Y_PAGE, labels.SHEET_PAGE.format(n=number, total=total), 2.8, "end"))
    return Page(f"symbols{number}", number, labels.SHEET_TITLE, tuple(prims)), over


def build_sheet(settings: Settings | None = None) -> tuple[list[Page], list[list[Overlay]]]:
    """Pages of the review sheet and, per page, the overlays (official images, library SVGs)."""
    settings = settings or Settings()
    if not OFFICIAL_DIR.is_dir():
        raise HuiselekError("reference_missing", None, variant="dir", path=str(REFERENCE_DIR))
    table = yaml.safe_load(
        (resources.files("huiselek") / "symbol_table.yaml").read_text(encoding="utf-8")
    )
    rows: list[_Row] = []
    for title, syms in _ordered(load_symbols(settings)):
        rows.append(_Row(title, GROUP_H))
        rows.extend(_plan_row(s, table.get(s.id)) for s in syms)
    pages_rows = _paginate(rows)
    built = [_page(n, len(pages_rows), r) for n, r in enumerate(pages_rows, 1)]
    return [b[0] for b in built], [b[1] for b in built]


def svg_with_overlays(svg: str, overlays: list[Overlay]) -> str:
    """Debug view: the page SVG with the overlays embedded as <image> elements."""
    tags = "".join(
        f'<image x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'href="{Path(p).resolve().as_uri()}"/>\n'
        for p, x, y, w, h in overlays
    )
    return svg.replace("</svg>", tags + "</svg>")
