#!/usr/bin/env python
"""Print candidate connection points for each symbol (helper for symbol_table.yaml points).

For every src/huiselek/symbol_data/<id>.json: size, a compact primitive list, the free ends
(open line/polyline end points that touch no other primitive) and the extreme points on each
side of the bounding box.

Usage: python tools/symbol_points.py [id ...]     (no ids = all symbols)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "huiselek" / "symbol_data"
EPS = 0.02


def seg_list(p):
    t = p["type"]
    if t == "line":
        return [((p["x1"], p["y1"]), (p["x2"], p["y2"]))]
    if t == "polyline":
        pts = [tuple(q) for q in p["points"]]
        segs = list(zip(pts, pts[1:]))
        if p["closed"]:
            segs.append((pts[-1], pts[0]))
        return segs
    return []


def dist_seg(pt, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((pt[0] - ax) * dx + (pt[1] - ay) * dy) / L))
    return math.hypot(pt[0] - ax - t * dx, pt[1] - ay - t * dy)


def dist_prim(pt, p):
    t = p["type"]
    if t in ("line", "polyline"):
        return min((dist_seg(pt, a, b) for a, b in seg_list(p)), default=1e9)
    if t == "circle":
        return abs(math.hypot(pt[0] - p["cx"], pt[1] - p["cy"]) - p["r"])
    if t == "arc":
        ang = math.degrees(math.atan2(pt[1] - p["cy"], pt[0] - p["cx"])) % 360
        s, e = p["start_deg"], p["end_deg"]
        if e - s >= 360 or any(s <= ang + k * 360 <= e for k in (0, 1)):
            return abs(math.hypot(pt[0] - p["cx"], pt[1] - p["cy"]) - p["r"])
        ends = [(p["cx"] + p["r"] * math.cos(math.radians(a)), p["cy"] + p["r"] * math.sin(math.radians(a))) for a in (s, e)]
        return min(math.hypot(pt[0] - x, pt[1] - y) for x, y in ends)
    return 1e9


def ends(i, p):
    if p["type"] == "line":
        return [(p["x1"], p["y1"]), (p["x2"], p["y2"])]
    if p["type"] == "polyline" and not p["closed"]:
        return [tuple(p["points"][0]), tuple(p["points"][-1])]
    return []


def summarize(p):
    t = p["type"]
    if t == "line":
        return f"line ({p['x1']},{p['y1']})-({p['x2']},{p['y2']})"
    if t == "polyline":
        return f"poly{'*' if p['closed'] else ''}{'#' if p['fill'] else ''} " + " ".join(f"({x},{y})" for x, y in p["points"])
    if t == "circle":
        return f"circle c({p['cx']},{p['cy']}) r{p['r']}{' #' if p['fill'] else ''}"
    if t == "arc":
        return f"arc c({p['cx']},{p['cy']}) r{p['r']} {p['start_deg']}..{p['end_deg']}"
    return f"text {p['text']!r} ({p['x']},{p['y']})"


def main(argv):
    files = sorted(DATA.glob("*.json")) if not argv else [DATA / f"{a}.json" for a in argv]
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        prims = d["primitives"]
        print(f"== {d['id']}  {d['width']} x {d['height']}")
        for i, p in enumerate(prims):
            print(f"  [{i}] {summarize(p)}")
        free = []
        for i, p in enumerate(prims):
            for e in ends(i, p):
                if all(dist_prim(e, q) > EPS for j, q in enumerate(prims) if j != i):
                    free.append(e)
        print("  free ends:", sorted(set(free)))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
