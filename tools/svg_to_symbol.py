#!/usr/bin/env python
"""Convert the AREI symbol SVGs listed in src/huiselek/symbol_table.yaml to JSON primitives.

Input : src/huiselek/symbol_table.yaml (source svg, rotate, keep_text per symbol id) and
        the SVGs under docs/reference/arei/ (made by tools/vssx_to_svg.py).
Output: src/huiselek/symbol_data/<id>.json
        {"id", "source", "width", "height", "primitives": [...]}, units mm at library scale,
        origin = top-left of the bounding box of the geometry (text is not part of the box),
        y down, numbers rounded to 3 decimals, keys sorted, LF line ends.

Primitive types (see src/huiselek/primitives.py; stroke width and colour are not stored):
  line      x1 y1 x2 y2
  polyline  points [[x, y], ...] closed fill
  circle    cx cy r fill
  arc       cx cy r start_deg end_deg (clockwise on the page, from +x)
  text      x y text size anchor rotation   (baseline position; rotation clockwise degrees)
Cubic runs that follow a circle (error <= 0.004 mm) become arc/circle; every other curve,
ellipses included, is flattened to a polyline with chord error <= 0.005 mm.
Table options (all optional): `mirror: vertical|horizontal` flips the symbol (top<->bottom or
left<->right) before `rotate`; `drop: [i, ...]` removes primitives by index into the list
produced from the SVG (after text filtering, in output order, before mirror/rotate/translate);
`text_at: {text: [x, y]}` sets the baseline position of that text in the final (rotated,
translated) symbol frame.
`add: [primitive, ...]` appends primitives (same dict shape as the JSON; text included) in the final
symbol frame, i.e. after drop/mirror/rotate/translate and text_at. If drop leaves no geometry, the
origin stays that of the pre-drop geometry (so the frame of existing points and text is unchanged). Afterwards the symbol is re-translated so the bounding box of
all geometry starts at (0, 0); this shifts everything (text too), so `points` in the table must be
given in the frame after that shift.
Symbol rotation: geometry rotates clockwise by `rotate`; text keeps its own rotation (stays
upright) and only its position moves. Text not listed in keep_text is dropped.
Elements with no fill and no stroke (Visio text boxes) are skipped and counted as "invisible".
Anything else that cannot be converted is reported, nothing is written, and the exit code is 1
(all conversions run first; JSON is written only when every symbol converted cleanly).

Usage: python tools/svg_to_symbol.py [id ...]     (no ids = every id in the table)
Needs PyYAML. Deterministic: a second run gives byte-identical files.
"""
from __future__ import annotations

import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "src" / "huiselek" / "symbol_table.yaml"
REF = ROOT / "docs" / "reference" / "arei"
OUT_DIR = ROOT / "src" / "huiselek" / "symbol_data"

FLAT_TOL = 0.005      # mm, flatten tolerance (control point distance to chord)
CIRCLE_TOL = 0.004    # mm, max deviation of a cubic run from the fitted circle
MAX_RADIUS = 50.0     # mm, larger fitted circles are treated as straight/curvy lines
NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


class Unsupported(Exception):
    pass


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


# ---------------------------------------------------------------- geometry helpers
def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * p0[i] + 3 * u * u * t * p1[i] + 3 * u * t * t * p2[i] + t**3 * p3[i] for i in (0, 1))


def flat_enough(p0, p1, p2, p3):
    ch = dist(p0, p3)
    if ch < 1e-9:
        return max(dist(p0, p1), dist(p0, p2)) <= FLAT_TOL
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    d1 = abs((p1[0] - p0[0]) * dy - (p1[1] - p0[1]) * dx) / ch
    d2 = abs((p2[0] - p0[0]) * dy - (p2[1] - p0[1]) * dx) / ch
    return max(d1, d2) <= FLAT_TOL


def flatten_cubic(p0, p1, p2, p3, out, depth=0):
    """Append the points after p0 (up to and including p3) to out."""
    if depth >= 14 or flat_enough(p0, p1, p2, p3):
        out.append(p3)
        return
    # de Casteljau split at 0.5
    m01 = tuple((p0[i] + p1[i]) / 2 for i in (0, 1))
    m12 = tuple((p1[i] + p2[i]) / 2 for i in (0, 1))
    m23 = tuple((p2[i] + p3[i]) / 2 for i in (0, 1))
    a = tuple((m01[i] + m12[i]) / 2 for i in (0, 1))
    b = tuple((m12[i] + m23[i]) / 2 for i in (0, 1))
    m = tuple((a[i] + b[i]) / 2 for i in (0, 1))
    flatten_cubic(p0, m01, a, m, out, depth + 1)
    flatten_cubic(m, b, m23, p3, out, depth + 1)


def circumcircle(a, b, c):
    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    if abs(d) < 1e-12:
        return None
    ux = ((a[0]**2 + a[1]**2) * (b[1] - c[1]) + (b[0]**2 + b[1]**2) * (c[1] - a[1]) + (c[0]**2 + c[1]**2) * (a[1] - b[1])) / d
    uy = ((a[0]**2 + a[1]**2) * (c[0] - b[0]) + (b[0]**2 + b[1]**2) * (a[0] - c[0]) + (c[0]**2 + c[1]**2) * (b[0] - a[0])) / d
    return (ux, uy), math.hypot(a[0] - ux, a[1] - uy)


def angle(c, p):
    return math.degrees(math.atan2(p[1] - c[1], p[0] - c[0])) % 360.0


def fit_circle_run(start, cubics, closed_run):
    """cubics: list of (c1, c2, p). Return ('circle', c, r) / ('arc', c, r, a0, a1) or None."""
    samples = [start]
    p0 = start
    for c1, c2, p in cubics:
        for k in range(1, 17):
            samples.append(bez(p0, c1, c2, p, k / 16))
        p0 = p
    n = len(samples)
    closed = dist(samples[0], samples[-1]) < 1e-6
    if closed:
        trio = (samples[0], samples[n // 3], samples[2 * n // 3])
    else:
        trio = (samples[0], samples[n // 2], samples[-1])
    fit = circumcircle(*trio)
    if fit is None:
        return None
    c, r = fit
    if r > MAX_RADIUS or r < 1e-6:
        return None
    if max(abs(dist(c, s) - r) for s in samples) > CIRCLE_TOL:
        return None
    if closed:
        return ("circle", c, r)
    a0 = angle(c, samples[0])
    am = angle(c, samples[n // 2])
    a1 = angle(c, samples[-1])
    total = (a1 - a0) % 360.0
    if (am - a0) % 360.0 < total:           # increasing angle (clockwise on the page)
        start_deg, span = a0, total
    else:                                    # traversed the other way round: swap ends
        start_deg, span = a1, (a0 - a1) % 360.0
    if span > 359.5 or span < 1e-6:
        return ("circle", c, r)
    return ("arc", c, r, start_deg, start_deg + span)


# ---------------------------------------------------------------- path parsing
def parse_path(d: str):
    """Return list of subpaths: (start, [segments], closed); segment = ('L', p) | ('C', c1, c2, p)."""
    toks = re.findall(r"[A-Za-z]|" + NUM.pattern, d)
    i = 0
    subs = []
    cur = None
    pos = (0.0, 0.0)
    cmd = None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd not in "MLCZ":
                raise Unsupported(f"path command {cmd}")
            if cmd == "Z":
                if cur is not None:
                    cur[2] = True
                    pos = cur[0]
                continue
        if cmd is None:
            raise Unsupported("path data without command")
        if cmd == "M":
            pos = (float(toks[i]), float(toks[i + 1]))
            i += 2
            cur = [pos, [], False]
            subs.append(cur)
            cmd = "L"
        elif cmd == "L":
            pos = (float(toks[i]), float(toks[i + 1]))
            i += 2
            cur[1].append(("L", pos))
        elif cmd == "C":
            v = [float(x) for x in toks[i:i + 6]]
            i += 6
            pos = (v[4], v[5])
            cur[1].append(("C", (v[0], v[1]), (v[2], v[3]), pos))
        else:
            raise Unsupported(f"path command {cmd}")
    return [tuple(s) for s in subs]


def dedupe(pts):
    out = []
    for p in pts:
        if not out or dist(out[-1], p) > 1e-9:
            out.append(p)
    return out


def subpath_primitives(start, segs, closed, fill):
    """Convert one subpath to primitive dicts (floats, untransformed)."""
    prims = []
    runs = []  # (kind, start, items)
    pos = start
    for s in segs:
        kind = s[0]
        if not runs or runs[-1][0] != kind:
            runs.append([kind, pos, []])
        runs[-1][2].append(s[1:] if kind == "C" else s[1])
        pos = s[-1]
    if not runs:
        return prims
    only_c = len(runs) == 1 and runs[0][0] == "C"
    if only_c:
        fit = fit_circle_run(start, runs[0][2], closed)
        if fit and fit[0] == "circle":
            prims.append({"type": "circle", "cx": fit[1][0], "cy": fit[1][1], "r": fit[2], "fill": fill})
            return prims
        if fit and fit[0] == "arc" and not fill:
            prims.append({"type": "arc", "cx": fit[1][0], "cy": fit[1][1], "r": fit[2], "start_deg": fit[3], "end_deg": fit[4]})
            if closed:
                prims.append({"type": "line", "x1": pos[0], "y1": pos[1], "x2": start[0], "y2": start[1]})
            return prims
    if fill or closed and len(runs) > 1 or only_c:
        # one polygon / polyline with all curves flattened
        pts = [start]
        p0 = start
        for s in segs:
            if s[0] == "L":
                pts.append(s[1])
            else:
                flatten_cubic(p0, s[1], s[2], s[3], pts)
            p0 = s[-1]
        pts = dedupe(pts)
        if closed and len(pts) > 1 and dist(pts[0], pts[-1]) < 1e-9:
            pts.pop()
        prims.append(poly_prim(pts, closed, fill))
        return prims
    # unfilled, open or mixed: one primitive per run
    for kind, rstart, items in runs:
        if kind == "L":
            pts = dedupe([rstart] + items)
            prims.append(poly_prim(pts, False, None))
        else:
            fit = fit_circle_run(rstart, items, False)
            if fit and fit[0] == "arc":
                prims.append({"type": "arc", "cx": fit[1][0], "cy": fit[1][1], "r": fit[2], "start_deg": fit[3], "end_deg": fit[4]})
            elif fit and fit[0] == "circle":
                prims.append({"type": "circle", "cx": fit[1][0], "cy": fit[1][1], "r": fit[2], "fill": None})
            else:
                pts = [rstart]
                p0 = rstart
                for c1, c2, p in items:
                    flatten_cubic(p0, c1, c2, p, pts)
                    p0 = p
                prims.append(poly_prim(dedupe(pts), False, None))
    if closed and dist(pos, start) > 1e-9:
        prims.append({"type": "line", "x1": pos[0], "y1": pos[1], "x2": start[0], "y2": start[1]})
    return prims


def poly_prim(pts, closed, fill):
    if len(pts) == 2 and not closed and not fill:
        return {"type": "line", "x1": pts[0][0], "y1": pts[0][1], "x2": pts[1][0], "y2": pts[1][1]}
    return {"type": "polyline", "points": [list(p) for p in pts], "closed": closed, "fill": fill}


# ---------------------------------------------------------------- svg reading
def fill_of(e):
    f = e.get("fill", "#000000")
    return None if f in ("none", "") else f


def visible(e):
    return not (e.get("fill", "#000000") == "none" and e.get("stroke", "none") == "none")


def parse_rotate(tr):
    m = re.fullmatch(r"\s*rotate\(\s*(NUM)(?:[\s,]+(NUM)[\s,]+(NUM))?\s*\)\s*".replace("NUM", NUM.pattern), tr or "")
    if not m:
        raise Unsupported(f"transform {tr!r}")
    return float(m.group(1))


def read_svg(path: Path, keep_text, problems):
    root = ET.parse(path).getroot()
    prims = []
    stats = {"invisible": 0, "text_dropped": 0}
    for e in root.iter():
        tag = local(e.tag)
        if tag in ("svg", "tspan"):
            continue
        if e.get("transform") and tag != "text":
            problems.append(f"{tag}: transform on a shape not supported")
            continue
        try:
            if tag == "path":
                if not visible(e):
                    stats["invisible"] += 1
                    continue
                fill = fill_of(e)
                for start, segs, closed in parse_path(e.get("d")):
                    prims += subpath_primitives(start, segs, closed, fill)
            elif tag == "circle":
                if not visible(e):
                    stats["invisible"] += 1
                    continue
                prims.append({"type": "circle", "cx": float(e.get("cx")), "cy": float(e.get("cy")),
                              "r": float(e.get("r")), "fill": fill_of(e)})
            elif tag == "ellipse":
                if not visible(e):
                    stats["invisible"] += 1
                    continue
                cx, cy, rx, ry = (float(e.get(k)) for k in ("cx", "cy", "rx", "ry"))
                n = max(8, math.ceil(math.pi / math.acos(1 - FLAT_TOL / max(rx, ry))))
                pts = [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
                prims.append(poly_prim(pts, True, fill_of(e)))
            elif tag == "text":
                size = float(e.get("font-size"))
                anchor = e.get("text-anchor", "start")
                rot = parse_rotate(e.get("transform")) if e.get("transform") else 0.0
                spans = [t for t in e if local(t.tag) == "tspan"]
                items = [(float(t.get("x")), float(t.get("y")), t.text or "") for t in spans] if spans else \
                        [(float(e.get("x")), float(e.get("y")), e.text or "")]
                for x, y, s in items:
                    if s in keep_text:
                        prims.append({"type": "text", "x": x, "y": y, "text": s, "size": size,
                                      "anchor": anchor, "rotation": rot})
                    else:
                        stats["text_dropped"] += 1
            else:
                problems.append(f"unsupported element <{tag}>")
        except Unsupported as ex:
            problems.append(f"<{tag}>: {ex}")
    return prims, stats


# ---------------------------------------------------------------- rotate / bbox / output
def rot_pt(p, rot):
    x, y = p
    return {0: (x, y), 90: (-y, x), 180: (-x, -y), 270: (y, -x)}[rot]


def rotate_prims(prims, rot):
    if rot == 0:
        return prims
    out = []
    for p in prims:
        q = dict(p)
        t = p["type"]
        if t == "line":
            q["x1"], q["y1"] = rot_pt((p["x1"], p["y1"]), rot)
            q["x2"], q["y2"] = rot_pt((p["x2"], p["y2"]), rot)
        elif t == "polyline":
            q["points"] = [list(rot_pt(tuple(pt), rot)) for pt in p["points"]]
        elif t in ("circle", "arc"):
            q["cx"], q["cy"] = rot_pt((p["cx"], p["cy"]), rot)
            if t == "arc":
                q["start_deg"] = (p["start_deg"] + rot) % 360.0
                q["end_deg"] = q["start_deg"] + (p["end_deg"] - p["start_deg"])
        elif t == "text":
            # move the glyph centre, keep the text upright (rotation unchanged)
            cy = p["y"] - 0.35 * p["size"]
            nx, ny = rot_pt((p["x"], cy), rot)
            q["x"], q["y"] = nx, ny + 0.35 * p["size"]
        out.append(q)
    return out


def mirror_prims(prims, mode):
    if mode not in ("vertical", "horizontal"):
        raise ValueError(f"mirror must be vertical or horizontal, got {mode!r}")
    v = mode == "vertical"

    def mp(x, y):
        return (x, -y) if v else (-x, y)

    out = []
    for p in prims:
        q = dict(p)
        t = p["type"]
        if t == "line":
            q["x1"], q["y1"] = mp(p["x1"], p["y1"])
            q["x2"], q["y2"] = mp(p["x2"], p["y2"])
        elif t == "polyline":
            q["points"] = [list(mp(*pt)) for pt in p["points"]]
        elif t in ("circle", "arc"):
            q["cx"], q["cy"] = mp(p["cx"], p["cy"])
            if t == "arc":
                span = p["end_deg"] - p["start_deg"]
                a1 = p["end_deg"]
                q["start_deg"] = ((-a1) if v else (180.0 - a1)) % 360.0
                q["end_deg"] = q["start_deg"] + span
        elif t == "text":  # position only, the text stays upright
            cy = p["y"] - 0.35 * p["size"]
            nx, ny = mp(p["x"], cy)
            q["x"], q["y"] = nx, ny + 0.35 * p["size"]
        out.append(q)
    return out


def bbox(prims):
    xs, ys = [], []
    for p in prims:
        t = p["type"]
        if t == "line":
            xs += [p["x1"], p["x2"]]; ys += [p["y1"], p["y2"]]
        elif t == "polyline":
            xs += [q[0] for q in p["points"]]; ys += [q[1] for q in p["points"]]
        elif t == "circle":
            xs += [p["cx"] - p["r"], p["cx"] + p["r"]]; ys += [p["cy"] - p["r"], p["cy"] + p["r"]]
        elif t == "arc":
            a0, a1 = p["start_deg"], p["end_deg"]
            angs = [a0, a1] + [k for k in range(math.floor(a0 / 90) * 90, math.ceil(a1 / 90) * 90 + 1, 90) if a0 < k < a1]
            for a in angs:
                xs.append(p["cx"] + p["r"] * math.cos(math.radians(a)))
                ys.append(p["cy"] + p["r"] * math.sin(math.radians(a)))
    return min(xs), min(ys), max(xs), max(ys)


def r3(v):
    v = round(v + 0.0, 3)
    return 0.0 if v == 0 else v


def translate_round(prims, dx, dy):
    out = []
    for p in prims:
        q = {}
        for k, v in p.items():
            q[k] = v
        t = p["type"]
        if t == "line":
            for k in ("x1", "x2"): q[k] = r3(p[k] - dx)
            for k in ("y1", "y2"): q[k] = r3(p[k] - dy)
        elif t == "polyline":
            q["points"] = [[r3(a - dx), r3(b - dy)] for a, b in p["points"]]
        elif t in ("circle", "arc"):
            q["cx"], q["cy"], q["r"] = r3(p["cx"] - dx), r3(p["cy"] - dy), r3(p["r"])
            if t == "arc":
                q["start_deg"], q["end_deg"] = r3(p["start_deg"]), r3(p["end_deg"])
        elif t == "text":
            q["x"], q["y"], q["size"], q["rotation"] = r3(p["x"] - dx), r3(p["y"] - dy), r3(p["size"]), r3(p["rotation"])
        out.append(q)
    return out


def convert(sid, entry, problems):
    src = REF / entry["source"]
    keep = set(entry.get("keep_text") or [])
    prims, stats = read_svg(src, keep, problems)
    drop = set(entry.get("drop") or [])
    if drop - set(range(len(prims))):
        raise ValueError(f"{sid}: drop index out of range (0..{len(prims) - 1})")
    if entry.get("mirror"):
        prims = mirror_prims(prims, entry["mirror"])
    rot = int(entry.get("rotate", 0))
    if rot not in (0, 90, 180, 270):
        raise ValueError(f"{sid}: rotate must be 0/90/180/270")
    prims = rotate_prims(prims, rot)
    full_geom = [p for p in prims if p["type"] != "text"]
    prims = [p for i, p in enumerate(prims) if i not in drop]
    geom = [p for p in prims if p["type"] != "text"]
    added = [dict(p) for p in (entry.get("add") or [])]
    if not geom and not added:
        raise ValueError(f"{sid}: no geometry left after conversion")
    x0, y0, x1, y1 = bbox(geom or full_geom)   # no geometry left (all dropped): keep the pre-drop origin
    prims = translate_round(prims, x0, y0)
    for txt, (tx, ty) in (entry.get("text_at") or {}).items():
        hit = [p for p in prims if p["type"] == "text" and p["text"] == txt]
        if not hit:
            raise ValueError(f"{sid}: text_at {txt!r} matches no kept text")
        for p in hit:
            p["x"], p["y"] = r3(tx), r3(ty)
    if added:
        prims = prims + translate_round(added, 0.0, 0.0)
        geom = [p for p in prims if p["type"] != "text"]
        x0, y0, x1, y1 = bbox(geom)
        if abs(x0) > 5e-4 or abs(y0) > 5e-4:
            prims = translate_round(prims, x0, y0)
    data = {"id": sid, "source": entry["source"], "width": r3(x1 - x0), "height": r3(y1 - y0), "primitives": prims}
    return data, stats


def main(argv) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    table = yaml.safe_load(TABLE.read_text(encoding="utf-8"))
    ids = argv[1:] or list(table)
    unknown = [i for i in ids if i not in table]
    if unknown:
        print(f"unknown symbol id(s): {', '.join(unknown)}; known ids are the keys of {TABLE}")
        return 1
    # Phase 1: convert everything. Phase 2: write, only if nothing went wrong.
    results = []
    bad = 0
    for sid in ids:
        problems: list[str] = []
        try:
            data, stats = convert(sid, table[sid], problems)
        except (ValueError, KeyError, OSError, ET.ParseError) as ex:
            print(f"  ERROR {sid}: {type(ex).__name__}: {ex}")
            bad += 1
            continue
        results.append((sid, data, stats))
        kinds: dict[str, int] = {}
        for p in data["primitives"]:
            kinds[p["type"]] = kinds.get(p["type"], 0) + 1
        info = " ".join(f"{k}={v}" for k, v in sorted(kinds.items()))
        print(f"{sid}: {data['width']}x{data['height']} mm  {info}  (invisible skipped {stats['invisible']}, text dropped {stats['text_dropped']})")
        for p in problems:
            print(f"  UNCONVERTED {sid}: {p}")
            bad += 1
    if bad:
        print(f"{bad} problem(s); nothing written")
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for sid, data, _ in results:
        text = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        (OUT_DIR / f"{sid}.json").write_text(text, encoding="utf-8", newline="\n")
    extra = sorted(set(p.stem for p in (REF / "svg-2023").glob("*.svg")) - {Path(e["source"]).stem for e in table.values()})
    if extra and len(argv) == 1:
        print("svg files not used by the table:", ", ".join(extra))
    stale = sorted(p.stem for p in OUT_DIR.glob("*.json") if p.stem not in table)
    if stale and len(argv) == 1:
        print("json files not in the table (stale):", ", ".join(stale))
    print(f"{len(results)} symbols written to {OUT_DIR}, 0 unconverted elements")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
