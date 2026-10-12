#!/usr/bin/env python
"""Build out/contact/index.html: converted AREI symbols next to the official table images.

Needs the outputs of tools/vssx_to_svg.py (svg-2023/), tools/extract_official.py
(official/images/index.csv) and, for the middle image, tools/svg_to_symbol.py
(src/huiselek/symbol_data/<id>.json, drawn here as inline SVG at the same scale, stroke 0.25 mm).
Plain HTML, no JavaScript. Standard library only.

Section 1: one card per symbol_id: converted SVG (about 4x screen size) and the official
images whose index guess matches the keywords in OFFICIAL_MATCH (several candidates are
shown when the guess is ambiguous). Section 2: every official image with its guess.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG_DIR = ROOT / "docs" / "reference" / "arei" / "svg-2023"
IMG_DIR = ROOT / "docs" / "reference" / "arei" / "official" / "images"
DATA_DIR = ROOT / "src" / "huiselek" / "symbol_data"
# svg master id -> symbol id in symbol_table.yaml where they differ
TABLE_ID = {"socket_protective": "socket_protective_conductor",
            "socket_protective_n": "socket_protective_conductor_n"}
OUT = ROOT / "out" / "contact" / "index.html"

PX_PER_MM = 15.0   # about 4x the CSS size of 1 mm (3.78 px)
MAX_W = 280        # px cap for very wide symbols
MAX_OFFICIAL = 3   # candidates shown per symbol

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vssx_to_svg import SYMBOLS  # noqa: E402  (symbol ids in the order of the converter)

# symbol_id -> prefixes of the official guess (case-insensitive, spaces collapsed); a prefix
# ending in "$" must match the whole guess; "file:<name>" picks an image by file name. Missing id = no official counterpart expected.
OFFICIAL_MATCH = {
    "breaker": ["automatische schakelaar"],
    "differential": ["differentieelstroom"],
    "fuse": ["smeltzekering$"],
    "kwh_meter": ["kwh"],
    "three_phase": ["driefasige wisselstroom"],
    "single_phase": ["eenfasige"],
    "conductors": ["elektrische leiding met n geleiders", "elektrische leiding met 3 geleiders"],
    "line_in_conduit": ["elektrische leiding in een buis"],
    "line_in_wall": ["elektrische leiding in een wand"],
    "line_on_wall": ["elektrische leiding op een wand"],
    "line_in_conduit_in_wall": ["elektrische leiding geplaatst in een buis in een wand"],
    "socket_child_protection": ["contactdoos met contact voor beschermingsgeleider en"],
    "socket_protective": ["contactdoos met contact voor beschermingsgeleider"],
    "socket_waterproof": ["half - waterdichte"],
    "light": ["aansluitpunt voor een verlichtingstoestel"],
    "light_with_switch": ["verlichtingstoestel met ingebouwde"],
    "switch": ["schakelaar$"],
    "impulse_relay": ["impulsschakelaar"],
    "push_button": ["drukknop$"],
    "appliance_general": ["vast elektrisch huishoudtoestel"],
    "stove": ["elektrisch fornuis"],
    "oven": ["elektrische oven"],
    "washing_machine": ["wasmachine"],
    "dryer": ["droogkast"],
    "dishwasher": ["afwasmachine"],
    "water_heater": ["boiler$"],
    "heating_device": ["verwarmingstoestel$"],
    "ev_charger": ["laadinrichting"],
    "motor": ["motor$"],
    "transformer": ["transformator"],
    "converter_ac_dc": ["gelijkrichter"],
    "converter_dc_ac": ["omvormer dc"],
    "box": ["doos$"],
    "junction_box": ["verbindingsdoos"],
    "board": ["algemene voorstelling van een schakel"],
    "domotica_push_button": ["file:p8_09.jpg"],
    "domotica_wireless": ["file:p8_09.jpg"],
    "domotica_clock": ["file:p8_09.jpg"],
    "domotica_detection": ["file:p8_09.jpg"],
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def rel(p: Path) -> str:
    return os.path.relpath(p, OUT.parent).replace("\\", "/")


def svg_size_px(path: Path) -> tuple[float, float]:
    head = path.read_text(encoding="utf-8")[:600]
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', head)
    w, h = (float(m.group(1)), float(m.group(2))) if m else (10.0, 10.0)
    scale = min(PX_PER_MM, MAX_W / w)
    return w * scale, h * scale


def f(v: float) -> str:
    return f"{v:.3f}".rstrip("0").rstrip(".")


def json_svg(sid: str, scale: float) -> str:
    """Draw src/huiselek/symbol_data/<id>.json as an inline SVG (stroke 0.25 mm)."""
    path = DATA_DIR / f"{sid}.json"
    if not path.exists():
        return '<span class="missing">no json</span>'
    d = json.loads(path.read_text(encoding="utf-8"))
    pad = 0.3
    w, h = d["width"], d["height"]
    x0, y0, x1, y1 = 0.0, 0.0, w, h   # view box also covers text that lies outside the geometry
    for p in d["primitives"]:
        if p["type"] == "text":
            half = 0.3 * p["size"] * len(p["text"])
            x0, x1 = min(x0, p["x"] - half), max(x1, p["x"] + half)
            y0, y1 = min(y0, p["y"] - p["size"]), max(y1, p["y"])
    parts = []
    for p in d["primitives"]:
        t = p["type"]
        fill = p.get("fill") or "none"
        if t == "line":
            parts.append(f'<line x1="{f(p["x1"])}" y1="{f(p["y1"])}" x2="{f(p["x2"])}" y2="{f(p["y2"])}"/>')
        elif t == "polyline":
            pts = " ".join(f"{f(x)},{f(y)}" for x, y in p["points"])
            parts.append(f'<{"polygon" if p["closed"] else "polyline"} points="{pts}" fill="{fill}"/>')
        elif t == "circle":
            parts.append(f'<circle cx="{f(p["cx"])}" cy="{f(p["cy"])}" r="{f(p["r"])}" fill="{fill}"/>')
        elif t == "arc":
            a0, a1 = math.radians(p["start_deg"]), math.radians(p["end_deg"])
            ax0, ay0 = p["cx"] + p["r"] * math.cos(a0), p["cy"] + p["r"] * math.sin(a0)
            ax1, ay1 = p["cx"] + p["r"] * math.cos(a1), p["cy"] + p["r"] * math.sin(a1)
            large = 1 if p["end_deg"] - p["start_deg"] > 180 else 0
            parts.append(f'<path d="M{f(ax0)} {f(ay0)} A{f(p["r"])} {f(p["r"])} 0 {large} 1 {f(ax1)} {f(ay1)}" fill="none"/>')
        elif t == "text":
            rot = f' transform="rotate({f(p["rotation"])} {f(p["x"])} {f(p["y"])})"' if p["rotation"] else ""
            parts.append(f'<text x="{f(p["x"])}" y="{f(p["y"])}" font-size="{f(p["size"])}" text-anchor="{p["anchor"]}" '
                         f'font-family="Helvetica" fill="#000" stroke="none"{rot}>{escape(p["text"])}</text>')
    vw, vh = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    return (f'<svg class="mine" width="{vw * scale:.0f}" height="{vh * scale:.0f}" '
            f'viewBox="{f(x0 - pad)} {f(y0 - pad)} {f(vw)} {f(vh)}" fill="none" stroke="#000" '
            f'stroke-width="0.25" stroke-linecap="round" stroke-linejoin="round">{"".join(parts)}</svg>')


def load_index():
    path = IMG_DIR / "index.csv"
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    index = load_index()
    cards = []
    missing_svg = []
    for sid in SYMBOLS:
        svg = SVG_DIR / f"{sid}.svg"
        if svg.exists():
            w, h = svg_size_px(svg)
            gen = json_svg(TABLE_ID.get(sid, sid), w / float(re.search(r'viewBox="0 0 ([\d.]+)', svg.read_text(encoding="utf-8")[:600]).group(1)))
            mine = f'<img class="mine" src="{rel(svg)}" width="{w:.0f}" height="{h:.0f}" alt="{sid}">'
        else:
            mine = '<span class="missing">no svg</span>'
            gen = ""
            missing_svg.append(sid)
        prefixes = [norm(p) for p in OFFICIAL_MATCH.get(sid, [])]
        found = []
        for pre in prefixes:
            for row in index:
                g = norm(row["guess"])
                if pre.startswith("file:"):
                    hit = row["file"] == pre[5:]
                else:
                    hit = g == pre[:-1] if pre.endswith("$") else g.startswith(pre)
                if hit and row not in found:
                    found.append(row)
        found = found[:MAX_OFFICIAL]
        offs = "".join(
            f'<figure><img src="{rel(IMG_DIR / r["file"])}" height="{min(int(r["height_px"]), 110)}" alt="{r["file"]}">'
            f'<figcaption>{r["file"]}</figcaption></figure>' for r in found
        ) or '<span class="missing">no official match</span>'
        cards.append(f'<div class="card"><div class="id">{escape(sid)}</div><div class="pair"><div class="cell">{mine}</div>'
                     f'<div class="cell gen">{gen}</div><div class="cell off">{offs}</div></div></div>')

    allimgs = "".join(
        f'<figure class="o"><img src="{rel(IMG_DIR / r["file"])}" style="max-height:90px;max-width:150px" alt="{r["file"]}">'
        f'<figcaption><b>{r["file"]}</b> {escape(r["guess"])}</figcaption></figure>' for r in index
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>AREI symbols: converted vs official</title>
<style>
body {{ font: 12px/1.3 Helvetica, Arial, sans-serif; margin: 8px; background: #fff; color: #000; }}
h2 {{ margin: 10px 0 6px; font-size: 14px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 6px; }}
.card {{ border: 1px solid #bbb; padding: 4px; }}
.id {{ font: bold 12px monospace; margin-bottom: 2px; }}
.pair {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
.cell {{ background: #f3f3f3; padding: 4px; min-width: 100px; min-height: 40px; display: flex; align-items: center; justify-content: center; flex: none; }}
.mine {{ flex: none; max-width: none; }}
.cell.gen {{ background: #eef4ff; }}
.cell.off {{ background: #fff; flex-wrap: wrap; gap: 4px; justify-content: flex-start; flex: 1 1 120px; }}
.mine {{ display: block; }}
figure {{ margin: 0; text-align: center; }}
figcaption {{ font-size: 10px; color: #555; }}
.missing {{ color: #b00; font-size: 11px; }}
.ogrid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 6px; }}
.o {{ border: 1px solid #ddd; padding: 3px; }}
.o figcaption {{ text-align: left; font-size: 9px; }}
</style></head><body>
<h2>Converted SVG (left, about 4x) | generated from JSON (middle, same scale) | official table images (right)</h2>
<div class="grid">{"".join(cards)}</div>
<h2>All official images with index guess</h2>
<div class="ogrid">{allimgs}</div>
</body></html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(cards)} symbols, {len(index)} official images, {len(missing_svg)} without svg)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
