#!/usr/bin/env python
"""Convert selected masters of the AREI Visio stencils (.vssx) to standalone SVG files.

Usage:  python tools/vssx_to_svg.py            # all symbols
        python tools/vssx_to_svg.py breaker fuse

Input : docs/reference/arei/visio-2023-nl/*.vssx (zip; visio/masters/masterN.xml)
Output: docs/reference/arei/svg-2023/<symbol_id>.svg  (viewBox in mm, y down)

Notes
- Visio internal lengths are inches; V (cached) values are used, never formulas.
- Guide shapes (Type="Guide", construction lines) are skipped; they hold the
  InfiniteLine rows. Any other geometry row type that cannot be converted
  prints a warning.
- Arcs, ellipses and splines are emitted as cubic Beziers (or <ellipse> when
  axis-aligned), so the result does not depend on SVG arc conventions.
- Standard library only.
"""
from __future__ import annotations

import math
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "docs" / "reference" / "arei" / "visio-2023-nl"
OUT_DIR = ROOT / "docs" / "reference" / "arei" / "svg-2023"

NS = "{http://schemas.microsoft.com/office/visio/2012/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
MM = 25.4  # mm per inch
DEFAULT_WEIGHT_MM = 0.25
MARGIN_MM = 0.4
EPS = 1e-6

# symbol_id -> (stencil, master NameU)
SYMBOLS = {
    "breaker": ("Beschermingstoestellen", "Automaat2"),
    "differential": ("Beschermingstoestellen", "Differentieel 2023"),
    "fuse": ("Beschermingstoestellen", "Smeltveiligheid"),
    "kwh_meter": ("Verbruikstoestellen", "kWh-teller"),
    "three_phase": ("Algemeenheden", "Driefasige wisselstroom"),
    "single_phase": ("Algemeenheden", "Eénfasige wisselstroom"),
    "conductors": ("Elektrische leidingen", "Leiding met n geleiders2"),
    "line_in_conduit": ("Elektrische leidingen", "Leiding in buis_2"),
    "line_in_wall": ("Elektrische leidingen", "Leiding in wand"),
    "line_on_wall": ("Elektrische leidingen", "Leiding op wand.38"),
    "line_in_conduit_in_wall": ("Elektrische leidingen", "Leiding in buis in wand"),
    "socket_child_protection": ("Contactdozen", "Stopcontact met beschermgeleider en kinderbeveiliging.21"),
    "socket_child_protection_n": ("Contactdozen", "Contactdoost met beschermgeleider en kinderbeveiliging n-aantal"),
    "socket_protective": ("Contactdozen", "Stopcontact met contact voor beschermingsgeleider.14"),
    "socket_protective_n": ("Contactdozen", "Contactdoos met contact voor bescherming n-aantal"),
    "socket_waterproof": ("Contactdozen", "Waterdicht stopcontact.13"),
    "light": ("Verbruikstoestellen", "Verlichtingstoestel"),
    "light_with_switch": ("Verbruikstoestellen", "Verlichtingsarmatuur met ingebouwde schakelaar"),
    "switch": ("Schakelaars", "Enkelpolige schakelaar"),
    "impulse_relay": ("Schakelaars", "Impulsschakelaar"),
    "push_button": ("Schakelaars", "Drukknop"),
    "appliance_general": ("Verbruikstoestellen", "Algemeen symbool huishoudelijk toestel voor éénsdraadsschema"),
    "stove": ("Verbruikstoestellen", "Kookfornuis voor éénsdraadsschema"),
    "oven": ("Verbruikstoestellen", "Elektrische oven voor éénsdraadsschema"),
    "washing_machine": ("Verbruikstoestellen", "Wasmachine"),
    "dryer": ("Verbruikstoestellen", "Droogkast voor ééndraadsschema"),
    "dishwasher": ("Verbruikstoestellen", "Vaatwasmachine voor ééndraadsschema"),
    "water_heater": ("Verbruikstoestellen", "Boiler"),
    "heating_device": ("Verbruikstoestellen", "Verwarmingstoestel"),
    "ev_charger": ("Verbruikstoestellen", "Laadinrichting voor elektrische wegvoertuigen"),
    "motor": ("Verbruikstoestellen", "Motor"),
    "transformer": ("Verbruikstoestellen", "Transformator"),
    "converter_ac_dc": ("Bronnen", "Gelijkrichter/Omvormer AC → DC"),
    "converter_dc_ac": ("Bronnen", "Gelijkrichter/Omvormer DC → AC"),
    "box": ("Elektrische toestellen", "Inbouwdoos"),
    "junction_box": ("Elektrische toestellen", "Aftakdoos"),
    "board": ("Elektrische toestellen", "Verdeelkast"),
    "domotica_push_button": ("Domotica", "Drukknop"),
    "domotica_wireless": ("Domotica", "Draadloze sturing"),
    "domotica_clock": ("Domotica", "Horloge"),
    "domotica_detection": ("Domotica", "Sturing door detectie"),
}

# Visio standard colour indices 0..15
STD_COLORS = {
    0: "#000000", 1: "#FFFFFF", 2: "#FF0000", 3: "#00FF00", 4: "#0000FF", 5: "#FFFF00",
    6: "#FF00FF", 7: "#00FFFF", 8: "#800000", 9: "#008000", 10: "#000080", 11: "#808000",
    12: "#800080", 13: "#008080", 14: "#C0C0C0", 15: "#E0E0E0",
}

# Visio LinePattern -> dash array in multiples of the line width (None = solid)
DASHES = {1: None, 2: (4, 3), 3: (1, 2), 4: (4, 2, 1, 2), 5: (4, 2, 1, 2, 1, 2), 6: (6, 2, 1, 2), 7: (6, 2, 2, 2)}


# --------------------------------------------------------------------------- warnings
_warned: set[tuple[str, str]] = set()
WARNINGS: list[str] = []
GUIDES_SKIPPED = 0


def warn(symbol: str, msg: str) -> None:
    key = (symbol, msg)
    if key in _warned:
        return
    _warned.add(key)
    line = f"WARNING {symbol}: {msg}"
    WARNINGS.append(line)
    print(line)


# --------------------------------------------------------------------------- 2D affine helpers
# (a, b, c, d, e, f): x' = a*x + c*y + e ; y' = b*x + d*y + f
IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def mmul(m1, m2):
    """m1 applied after m2."""
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (
        a1 * a2 + c1 * b2, b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1,
    )


def mapply(m, p):
    return (m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5])


def translate(x, y):
    return (1.0, 0.0, 0.0, 1.0, x, y)


def rotate(angle):
    c, s = math.cos(angle), math.sin(angle)
    return (c, s, -s, c, 0.0, 0.0)


# --------------------------------------------------------------------------- stencil loading
class Stencil:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.stem
        z = zipfile.ZipFile(path)
        self.zip = z
        doc = ET.fromstring(z.read("visio/document.xml"))
        self.colors: dict[int, str] = {}
        for ce in doc.iter(NS + "ColorEntry"):
            self.colors[int(ce.get("IX"))] = ce.get("RGB").upper()
        self.styles: dict[int, ET.Element] = {}
        for ss in doc.iter(NS + "StyleSheet"):
            self.styles[int(ss.get("ID"))] = ss
        masters = ET.fromstring(z.read("visio/masters/masters.xml"))
        rels = {r.get("Id"): r.get("Target")
                for r in ET.fromstring(z.read("visio/masters/_rels/masters.xml.rels"))}
        self.masters: dict[str, str] = {}
        for m in masters.findall(NS + "Master"):
            rid = m.find(NS + "Rel").get(RNS + "id")
            self.masters[m.get("NameU")] = "visio/masters/" + rels[rid]

    def find_master(self, name_u: str) -> str | None:
        if name_u in self.masters:
            return self.masters[name_u]
        norm = unicodedata.normalize("NFC", name_u)
        for k, v in self.masters.items():
            if unicodedata.normalize("NFC", k) == norm:
                return v
        return None

    def load_master(self, name_u: str) -> ET.Element:
        return ET.fromstring(self.zip.read(self.find_master(name_u)))


# --------------------------------------------------------------------------- cell access
def cell_map(el: ET.Element) -> dict[str, ET.Element]:
    return {c.get("N"): c for c in el.findall(NS + "Cell")}


def fnum(s, default=0.0) -> float:
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


def num(cells: dict, name: str, default=0.0) -> float:
    c = cells.get(name)
    return fnum(c.get("V"), default) if c is not None else default


class Ctx:
    """Per-conversion context: stencil + symbol id for warnings."""

    def __init__(self, stencil: Stencil, symbol: str):
        self.st = stencil
        self.symbol = symbol
        self.guides_skipped = 0
        self.warn = lambda msg: warn(symbol, msg)

    # style cascade ---------------------------------------------------------
    def style_chain(self, shape: ET.Element, kind: str):
        sid = shape.get(kind + "Style")
        seen = set()
        while sid is not None and int(sid) not in seen:
            seen.add(int(sid))
            ss = self.st.styles.get(int(sid))
            if ss is None:
                return
            yield ss
            sid = ss.get(kind + "Style")

    def prop(self, shape: ET.Element, cells: dict, kind: str, name: str, default=None):
        """Shape cell, else stylesheet chain (LineStyle/FillStyle/TextStyle). Returns the V string."""
        if name in cells:
            return cells[name].get("V")
        for ss in self.style_chain(shape, kind):
            c = cell_map(ss).get(name)
            if c is not None:
                return c.get("V")
        return default

    def section_prop(self, shape: ET.Element, kind: str, section: str, name: str, default=None):
        """Row IX=0 of a Character/Paragraph section on the shape or its style chain."""
        for el in [shape, *self.style_chain(shape, kind)]:
            for sec in el.findall(NS + "Section"):
                if sec.get("N") == section:
                    for row in sec.findall(NS + "Row"):
                        if row.get("IX") in (None, "0"):
                            c = cell_map(row).get(name)
                            if c is not None:
                                return c.get("V")
        return default

    def color(self, v, what: str) -> str:
        if v is None:
            return "#000000"
        v = str(v).strip()
        if v.startswith("#"):
            return v.upper()
        idx = int(fnum(v))
        if idx in self.st.colors:
            return self.st.colors[idx]
        if idx in STD_COLORS:
            return STD_COLORS[idx]
        self.warn(f"{what}: unknown colour index {idx}, using black")
        return "#000000"


# --------------------------------------------------------------------------- curve helpers
KAPPA = 0.5522847498307936


def ellipse_beziers(c, a, b):
    """Closed ellipse c + a cos t + b sin t as 4 cubic Bezier segments; returns list of (p1,p2,p3) and start."""
    def P(t):
        return (c[0] + a[0] * math.cos(t) + b[0] * math.sin(t), c[1] + a[1] * math.cos(t) + b[1] * math.sin(t))

    def D(t):
        return (-a[0] * math.sin(t) + b[0] * math.cos(t), -a[1] * math.sin(t) + b[1] * math.cos(t))

    segs = []
    for k in range(4):
        t0, t1 = k * math.pi / 2, (k + 1) * math.pi / 2
        p0, p3 = P(t0), P(t1)
        d0, d1 = D(t0), D(t1)
        segs.append(((p0[0] + KAPPA * d0[0], p0[1] + KAPPA * d0[1]),
                     (p3[0] - KAPPA * d1[0], p3[1] - KAPPA * d1[1]), p3))
    return P(0.0), segs


def arc_beziers(centre, L, r, th0, dth):
    """Arc of the circle (radius r, angles th0..th0+dth) mapped through linear map L=(a,b,c,d) plus centre."""
    def P(t):
        x, y = r * math.cos(t), r * math.sin(t)
        return (centre[0] + L[0] * x + L[2] * y, centre[1] + L[1] * x + L[3] * y)

    def D(t):
        x, y = -r * math.sin(t), r * math.cos(t)
        return (L[0] * x + L[2] * y, L[1] * x + L[3] * y)

    n = max(1, int(math.ceil(abs(dth) / (math.pi / 2) - 1e-9)))
    delta = dth / n
    k = 4.0 / 3.0 * math.tan(delta / 4.0)
    segs = []
    for i in range(n):
        t0 = th0 + i * delta
        t1 = t0 + delta
        p0, p3 = P(t0), P(t1)
        d0, d1 = D(t0), D(t1)
        segs.append(((p0[0] + k * d0[0], p0[1] + k * d0[1]), (p3[0] - k * d1[0], p3[1] - k * d1[1]), p3))
    return segs


def elliptical_arc(start, end, mid, angle, ratio):
    """Visio EllipticalArcTo -> list of cubic segments, or None if degenerate."""
    if ratio <= 0:
        ratio = 1.0
    ca, sa = math.cos(angle), math.sin(angle)

    def to_q(p):  # into the frame where the ellipse is a circle
        ux = ca * p[0] + sa * p[1]
        uy = -sa * p[0] + ca * p[1]
        return (ux, uy * ratio)

    qs, qm, qe = to_q(start), to_q(mid), to_q(end)
    ax, ay = qs
    bx, by = qm
    cx, cy = qe
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return None
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    r = math.hypot(ax - ux, ay - uy)
    ths = math.atan2(ay - uy, ax - ux)
    thm = math.atan2(by - uy, bx - ux)
    the = math.atan2(cy - uy, cx - ux)
    tau = 2 * math.pi
    ccw_m = (thm - ths) % tau
    ccw_e = (the - ths) % tau
    dth = ccw_e if ccw_m < ccw_e else -((ths - the) % tau)
    # centre back in p space, L = R(angle) * diag(1, 1/ratio)
    centre = (ca * ux - sa * uy / ratio, sa * ux + ca * uy / ratio)
    L = (ca, sa, -sa / ratio, ca / ratio)
    return arc_beziers(centre, L, r, ths, dth)


def bow_arc(start, end, bow):
    """Visio ArcTo (circular arc with sagitta |bow|); sign convention unverified."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    chord = math.hypot(dx, dy)
    if chord < 1e-12 or abs(bow) < 1e-12:
        return None
    h = abs(bow)
    r = (chord * chord / 4 + h * h) / (2 * h)
    mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
    nx, ny = dy / chord, -dx / chord  # right-hand normal
    s = 1.0 if bow > 0 else -1.0
    mid = (mx + nx * h * s, my + ny * h * s)
    return elliptical_arc(start, end, mid, 0.0, 1.0)


def nurbs_point(ctrl, weights, knots, degree, t):
    """De Boor for rational B-spline at parameter t."""
    n = len(ctrl)
    # find span
    k = degree
    while k < n - 1 and t >= knots[k + 1]:
        k += 1
    d = [(ctrl[j][0] * weights[j], ctrl[j][1] * weights[j], weights[j]) for j in range(k - degree, k + 1)]
    for r in range(1, degree + 1):
        for j in range(degree, r - 1, -1):
            i = j + k - degree
            den = knots[i + degree - r + 1] - knots[i]
            alpha = 0.0 if den == 0 else (t - knots[i]) / den
            d[j] = tuple((1 - alpha) * d[j - 1][q] + alpha * d[j][q] for q in range(3))
    w = d[degree][2]
    return (d[degree][0] / w, d[degree][1] / w) if w else (d[degree][0], d[degree][1])


def nurbs_beziers(ctrl, weights, knots, degree, npts=24):
    """Approximate a NURBS by Catmull-Rom Beziers through points spaced evenly by arc length."""
    n = len(ctrl)
    if len(knots) < n + degree + 1:
        knots = list(knots) + [knots[-1]] * (n + degree + 1 - len(knots))
    t0, t1 = knots[degree], knots[n]
    if t1 <= t0:
        return None
    dense = 400
    pts = []
    for i in range(dense + 1):
        t = t0 + (t1 - t0) * i / dense
        pts.append(nurbs_point(ctrl, weights, knots, degree, min(t, t1 - 1e-12)) if i < dense else ctrl[-1])
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + ptdist(pts[i], pts[i - 1]))
    total = cum[-1]
    if total < 1e-12:
        return None
    sel = []
    j = 0
    for i in range(npts + 1):
        target = total * i / npts
        while j < len(cum) - 2 and cum[j + 1] < target:
            j += 1
        seg = cum[j + 1] - cum[j]
        f = 0.0 if seg == 0 else (target - cum[j]) / seg
        sel.append((pts[j][0] + f * (pts[j + 1][0] - pts[j][0]), pts[j][1] + f * (pts[j + 1][1] - pts[j][1])))
    sel[0], sel[-1] = pts[0], pts[-1]
    segs = []
    for i in range(npts):
        p0, p1 = sel[i], sel[i + 1]
        pm = sel[i - 1] if i > 0 else p0
        pn = sel[i + 2] if i + 2 <= npts else p1
        c1 = (p0[0] + (p1[0] - pm[0]) / 6, p0[1] + (p1[1] - pm[1]) / 6)
        c2 = (p1[0] - (pn[0] - p0[0]) / 6, p1[1] - (pn[1] - p0[1]) / 6)
        segs.append((c1, c2, p1))
    return segs


def pad_knots(knots, n, degree):
    knots = list(knots)
    while len(knots) < n + degree + 1:
        knots.append(knots[-1])
    return knots


# --------------------------------------------------------------------------- geometry sections
def geometry_items(ctx: Ctx, shape: ET.Element, cells: dict):
    """Return list of ('path', ops, nofill, noline) / ('ellipse', c, a, b, nofill, noline) in local inch coords."""
    W, H = num(cells, "Width"), num(cells, "Height")
    items = []
    for sec in shape.findall(NS + "Section"):
        if sec.get("N") != "Geometry" or sec.get("Del") == "1":
            continue
        sc = cell_map(sec)
        if num(sc, "NoShow") == 1:
            continue
        nofill = num(sc, "NoFill") == 1
        noline = num(sc, "NoLine") == 1
        ops: list = []
        cur = None
        start = None
        spline: dict | None = None  # pending SplineStart/SplineKnot collection

        def flush_path():
            nonlocal ops
            if ops:
                items.append(("path", ops, nofill, noline))
            ops = []

        def close_if_needed():
            if cur is not None and start is not None and len(ops) > 1 and ops and ops[-1][0] != "Z":
                if abs(cur[0] - start[0]) < EPS and abs(cur[1] - start[1]) < EPS:
                    ops.append(("Z",))

        def finish_spline():
            nonlocal cur, spline
            if spline is None:
                return
            sp, spline = spline, None
            ctrl, weights, knots, deg = sp["ctrl"], [1.0] * len(sp["ctrl"]), sp["knots"], sp["deg"]
            knots = list(knots) + [sp["last"]] * (deg + 1)  # clamp end with the last knot
            segs = nurbs_beziers(ctrl, weights, knots, deg)
            if segs is None:
                ctx.warn("degenerate spline, drawn as polyline")
                for p in ctrl[1:]:
                    ops.append(("L", p))
            else:
                for s in segs:
                    ops.append(("C", *s))
            cur = ctrl[-1]

        rows = [r for r in sec.findall(NS + "Row") if r.get("Del") != "1"]
        for row in rows:
            t = row.get("T")
            rc = cell_map(row)
            x, y = num(rc, "X"), num(rc, "Y")
            if t != "SplineKnot":
                finish_spline()
            if t in ("MoveTo", "RelMoveTo"):
                close_if_needed()
                if t == "RelMoveTo":
                    x, y = x * W, y * H
                ops.append(("M", (x, y)))
                cur = start = (x, y)
            elif t in ("LineTo", "RelLineTo"):
                if t == "RelLineTo":
                    x, y = x * W, y * H
                if cur is None:
                    ctx.warn(f"{t} without current point")
                    continue
                ops.append(("L", (x, y)))
                cur = (x, y)
            elif t in ("RelCubBezTo", "CubBezTo"):
                a, b, c, d = num(rc, "A"), num(rc, "B"), num(rc, "C"), num(rc, "D")
                if t == "RelCubBezTo":
                    x, y, a, b, c, d = x * W, y * H, a * W, b * H, c * W, d * H
                ops.append(("C", (a, b), (c, d), (x, y)))
                cur = (x, y)
            elif t in ("RelQuadBezTo", "QuadBezTo"):
                a, b = num(rc, "A"), num(rc, "B")
                if t == "RelQuadBezTo":
                    x, y, a, b = x * W, y * H, a * W, b * H
                p0 = cur
                ops.append(("C", (p0[0] + 2 / 3 * (a - p0[0]), p0[1] + 2 / 3 * (b - p0[1])),
                            (x + 2 / 3 * (a - x), y + 2 / 3 * (b - y)), (x, y)))
                cur = (x, y)
            elif t in ("EllipticalArcTo", "RelEllipticalArcTo"):
                a, b = num(rc, "A"), num(rc, "B")
                if t == "RelEllipticalArcTo":
                    x, y, a, b = x * W, y * H, a * W, b * H
                segs = elliptical_arc(cur, (x, y), (a, b), num(rc, "C"), num(rc, "D", 1.0)) if cur else None
                if segs is None:
                    ctx.warn(f"{t}: degenerate arc, drawn as line")
                    ops.append(("L", (x, y)))
                else:
                    for s in segs:
                        ops.append(("C", *s))
                cur = (x, y)
            elif t == "ArcTo":
                ctx.warn("ArcTo bow sign convention unverified")
                segs = bow_arc(cur, (x, y), num(rc, "A")) if cur else None
                if segs is None:
                    ops.append(("L", (x, y)))
                else:
                    for s in segs:
                        ops.append(("C", *s))
                cur = (x, y)
            elif t == "Ellipse":
                a, b, c, d = num(rc, "A"), num(rc, "B"), num(rc, "C"), num(rc, "D")
                close_if_needed()
                flush_path()
                cur = start = None
                items.append(("ellipse", (x, y), (a - x, b - y), (c - x, d - y), nofill, noline))
            elif t == "SplineStart":
                if cur is None:
                    ctx.warn("SplineStart without current point")
                    continue
                spline = {"ctrl": [cur, (x, y)], "knots": [num(rc, "B"), num(rc, "A")],
                          "last": num(rc, "C"), "deg": int(num(rc, "D"))}
            elif t == "SplineKnot":
                if spline is None:
                    ctx.warn("SplineKnot without SplineStart")
                    continue
                spline["ctrl"].append((x, y))
                spline["knots"].append(num(rc, "A"))
            elif t == "NURBSTo":
                ec = rc.get("E")
                m = re.match(r"\s*NURBS\((.*)\)\s*$", ec.get("V") or "", re.S) if ec is not None else None
                if not m or cur is None:
                    ctx.warn("NURBSTo: cannot parse E cell, drawn as line")
                    ops.append(("L", (x, y)))
                    cur = (x, y)
                    continue
                vals = [float(v) for v in m.group(1).replace("\n", " ").split(",") if v.strip()]
                last_knot, deg, xtype, ytype = vals[0], int(vals[1]), int(vals[2]), int(vals[3])
                quads = [vals[i:i + 4] for i in range(4, len(vals) - 3, 4)]
                ctrl = [cur] + [((q[0] * W if xtype == 0 else q[0]), (q[1] * H if ytype == 0 else q[1])) for q in quads] + [(x, y)]
                weights = [num(rc, "D", 1.0)] + [q[3] for q in quads] + [num(rc, "B", 1.0)]
                knots = [num(rc, "C")] + [q[2] for q in quads] + [num(rc, "A"), last_knot]
                knots = pad_knots(knots, len(ctrl), deg)
                segs = nurbs_beziers(ctrl, weights, knots, deg)
                if segs is None:
                    ctx.warn("NURBSTo: degenerate, drawn as line")
                    ops.append(("L", (x, y)))
                else:
                    for s in segs:
                        ops.append(("C", *s))
                cur = (x, y)
            elif t == "InfiniteLine":
                ctx.warn("InfiniteLine in a visible geometry section not drawn")
            elif t == "PolylineTo":
                ctx.warn("PolylineTo not converted (drawn as straight line to end point)")
                ops.append(("L", (x, y)))
                cur = (x, y)
            else:
                ctx.warn(f"geometry row type {t!r} not converted")
        finish_spline()
        close_if_needed()
        flush_path()
    return items


# --------------------------------------------------------------------------- drawing model
def ptdist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def sample_ops(ops):
    """Points on the path (for bbox)."""
    pts = []
    cur = None
    for op in ops:
        k = op[0]
        if k in ("M", "L"):
            pts.append(op[1])
            cur = op[1]
        elif k == "C":
            p0, p1, p2, p3 = cur, op[1], op[2], op[3]
            for i in range(1, 9):
                t = i / 8
                u = 1 - t
                pts.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
            cur = p3
    return pts


def shape_style(ctx: Ctx, shape: ET.Element, cells: dict) -> dict:
    lw = fnum(ctx.prop(shape, cells, "Line", "LineWeight"), 0.0) * MM
    if lw <= 0:
        lw = DEFAULT_WEIGHT_MM
    pat = int(fnum(ctx.prop(shape, cells, "Line", "LinePattern"), 1))
    stroke = None if pat == 0 else ctx.color(ctx.prop(shape, cells, "Line", "LineColor"), "LineColor")
    dash = None
    if pat not in (0, 1):
        if pat in DASHES:
            dash = tuple(round(d * lw, 3) for d in DASHES[pat])
        else:
            ctx.warn(f"LinePattern {pat} not supported, drawn solid")
    cap = int(fnum(ctx.prop(shape, cells, "Line", "LineCap"), 0))
    fp = int(fnum(ctx.prop(shape, cells, "Fill", "FillPattern"), 1))
    fill = None
    if fp != 0:
        if fp != 1:
            ctx.warn(f"FillPattern {fp} not supported, drawn solid with FillForegnd")
        fill = ctx.color(ctx.prop(shape, cells, "Fill", "FillForegnd"), "FillForegnd")
    for arrow in ("BeginArrow", "EndArrow"):
        if fnum(ctx.prop(shape, cells, "Line", arrow), 0) not in (0.0,):
            ctx.warn(f"{arrow} on shape {shape.get('ID')} not converted")
    return {"stroke": stroke, "sw": lw, "dash": dash, "cap": cap, "fill": fill}


def aligned_ellipse(M, c, a, b):
    """If transformed ellipse is axis-aligned return (cx, cy, rx, ry) else None."""
    cc = mapply(M, c)
    ap = mapply(M, (c[0] + a[0], c[1] + a[1]))
    bp = mapply(M, (c[0] + b[0], c[1] + b[1]))
    av = (ap[0] - cc[0], ap[1] - cc[1])
    bv = (bp[0] - cc[0], bp[1] - cc[1])
    tol = 1e-6 * max(1.0, abs(av[0]) + abs(av[1]) + abs(bv[0]) + abs(bv[1]))
    if abs(av[1]) < tol and abs(bv[0]) < tol:
        return cc[0], cc[1], abs(av[0]), abs(bv[1])
    if abs(av[0]) < tol and abs(bv[1]) < tol:
        return cc[0], cc[1], abs(bv[0]), abs(av[1])
    return None


def walk(ctx: Ctx, shape: ET.Element, parent_m, out: list):
    sid = shape.get("ID")
    stype = shape.get("Type")
    if stype == "Guide":
        ctx.guides_skipped += 1
        return
    if stype == "Foreign":
        ctx.warn(f"Foreign (embedded image) shape {sid} not converted")
        return
    cells = cell_map(shape)
    if fnum(ctx.prop(shape, cells, "Line", "NonPrinting"), 0) == 1:
        return
    W, H = num(cells, "Width"), num(cells, "Height")
    lpx, lpy = num(cells, "LocPinX"), num(cells, "LocPinY")
    flipx, flipy = num(cells, "FlipX") == 1, num(cells, "FlipY") == 1
    if flipx or flipy:
        ctx.warn(f"shape {sid}: FlipX/FlipY applied (pin semantics unverified)")
    local = IDENT
    if flipx or flipy:
        local = (-1.0 if flipx else 1.0, 0.0, 0.0, -1.0 if flipy else 1.0, W if flipx else 0.0, H if flipy else 0.0)
    local = mmul(translate(-lpx, -lpy), local)
    local = mmul(rotate(num(cells, "Angle")), local)
    local = mmul(translate(num(cells, "PinX"), num(cells, "PinY")), local)
    M = mmul(parent_m, local)

    items = geometry_items(ctx, shape, cells)
    if items:
        st = shape_style(ctx, shape, cells)
        for it in items:
            nofill, noline = it[-2], it[-1]
            sty = dict(st)
            if nofill:
                sty["fill"] = None
            if noline:
                sty["stroke"] = None
            if it[0] == "path":
                ops = []
                for op in it[1]:
                    ops.append((op[0], *[mapply(M, p) for p in op[1:]]))
                out.append({"k": "path", "ops": ops, **sty})
            else:
                _, c, a, b = it[0], it[1], it[2], it[3]
                al = aligned_ellipse(M, c, a, b)
                if al:
                    out.append({"k": "ellipse", "cx": al[0], "cy": al[1], "rx": al[2], "ry": al[3], **sty})
                else:
                    p0, segs = ellipse_beziers(c, a, b)
                    ops = [("M", mapply(M, p0))]
                    for s in segs:
                        ops.append(("C", *[mapply(M, p) for p in s]))
                    ops.append(("Z",))
                    out.append({"k": "path", "ops": ops, **sty})

    sub = shape.find(NS + "Shapes")
    if sub is not None:
        for child in sub.findall(NS + "Shape"):
            walk(ctx, child, M, out)

    text_item(ctx, shape, cells, M, W, H, out)


def text_item(ctx: Ctx, shape: ET.Element, cells: dict, M, W, H, out: list):
    te = shape.find(NS + "Text")
    if te is None:
        return
    raw = "".join(te.itertext()).replace("\u2028", "\n").replace("\r", "")
    if raw.endswith("\n"):
        raw = raw[:-1]  # closing paragraph mark, not an extra line
    lines = raw.split("\n")
    if not any(l.strip() for l in lines):
        return
    size_in = fnum(ctx.section_prop(shape, "Text", "Character", "Size"), 0.1111)
    fs = size_in * MM
    color = ctx.color(ctx.section_prop(shape, "Text", "Character", "Color", "0"), "text colour")
    halign = int(fnum(ctx.section_prop(shape, "Text", "Paragraph", "HorzAlign"), 1))
    valign = int(fnum(ctx.prop(shape, cells, "Text", "VerticalAlign"), 1))
    tw = num(cells, "TxtWidth", W) if "TxtWidth" in cells else W
    th = num(cells, "TxtHeight", H) if "TxtHeight" in cells else H
    tpx = num(cells, "TxtPinX", W / 2) if "TxtPinX" in cells else W / 2
    tpy = num(cells, "TxtPinY", H / 2) if "TxtPinY" in cells else H / 2
    tlx = num(cells, "TxtLocPinX", tw / 2) if "TxtLocPinX" in cells else tw / 2
    tly = num(cells, "TxtLocPinY", th / 2) if "TxtLocPinY" in cells else th / 2
    tang = num(cells, "TxtAngle")
    lm = fnum(ctx.prop(shape, cells, "Text", "LeftMargin"), 0.0)
    rm = fnum(ctx.prop(shape, cells, "Text", "RightMargin"), 0.0)
    tm = fnum(ctx.prop(shape, cells, "Text", "TopMargin"), 0.0)
    bm = fnum(ctx.prop(shape, cells, "Text", "BottomMargin"), 0.0)
    # text frame -> shape local -> output
    TM = mmul(M, mmul(translate(tpx, tpy), mmul(rotate(tang), translate(-tlx, -tly))))
    sx = math.hypot(TM[0], TM[1])  # mm per inch of the text frame
    lh = 1.2 * fs
    n = len(lines)
    # in frame units (inches): block height
    block_h = n * lh / sx
    if valign == 0:
        top = th - tm
    elif valign == 2:
        top = bm + block_h
    else:
        top = (th - tm + bm) / 2 + block_h / 2
    if halign == 0:
        bx, anchor = lm, "start"
    elif halign == 2:
        bx, anchor = tw - rm, "end"
    else:
        bx, anchor = (tw + lm - rm) / 2, "middle"
    rot = math.degrees(math.atan2(TM[1], TM[0]))
    if abs(rot) < 1e-6:
        rot = 0.0
    tl = []
    for i, line in enumerate(lines):
        yb_in = top - (i + 0.5) * lh / sx
        x, y = mapply(TM, (bx, yb_in))
        # move from line centre to baseline (in output direction, rotated frame)
        r = math.radians(rot)
        off = 0.36 * fs  # centre of x-height/cap-height to baseline
        x, y = x - off * math.sin(r), y + off * math.cos(r)
        tl.append((line, x, y))
    out.append({"k": "text", "lines": tl, "fs": fs, "anchor": anchor, "rot": rot, "fill": color})


# --------------------------------------------------------------------------- SVG output
def fmt(v: float) -> str:
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def bbox_of(elements: list):
    xs, ys = [], []
    pad = 0.0
    for e in elements:
        half = e.get("sw", 0.0) / 2 if e.get("stroke") else 0.0
        if e["k"] == "path":
            pts = sample_ops(e["ops"])
            for x, y in pts:
                xs += [x - half, x + half]
                ys += [y - half, y + half]
        elif e["k"] == "ellipse":
            xs += [e["cx"] - e["rx"] - half, e["cx"] + e["rx"] + half]
            ys += [e["cy"] - e["ry"] - half, e["cy"] + e["ry"] + half]
        elif e["k"] == "text":
            r = math.radians(e["rot"])
            for line, x, y in e["lines"]:
                w = max(len(line.strip()), 1) * 0.55 * e["fs"]
                x0 = {"start": 0, "middle": -w / 2, "end": -w}[e["anchor"]]
                for cx, cy in ((x0, -0.8 * e["fs"]), (x0 + w, -0.8 * e["fs"]), (x0, 0.25 * e["fs"]), (x0 + w, 0.25 * e["fs"])):
                    xs.append(x + cx * math.cos(r) - cy * math.sin(r))
                    ys.append(y + cx * math.sin(r) + cy * math.cos(r))
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def style_attrs(e: dict) -> str:
    a = []
    a.append(f'fill="{e["fill"]}"' if e["fill"] else 'fill="none"')
    if e["stroke"]:
        a.append(f'stroke="{e["stroke"]}" stroke-width="{fmt(e["sw"])}"')
        if e["dash"]:
            a.append('stroke-dasharray="' + " ".join(fmt(d) for d in e["dash"]) + '"')
        if e["cap"] == 1:
            a.append('stroke-linecap="butt"')
        elif e["cap"] == 2:
            a.append('stroke-linecap="square"')
    else:
        a.append('stroke="none"')
    return " ".join(a)


def build_svg(symbol: str, stencil_name: str, master_name: str, elements: list) -> str | None:
    bb = bbox_of(elements)
    if bb is None:
        return None
    minx, miny, maxx, maxy = bb
    minx -= MARGIN_MM
    miny -= MARGIN_MM
    w = maxx + MARGIN_MM - minx
    h = maxy + MARGIN_MM - miny

    def P(p):
        return f"{fmt(p[0] - minx)} {fmt(p[1] - miny)}"

    body = []
    for e in elements:
        if e["k"] == "path":
            d = []
            for op in e["ops"]:
                if op[0] in ("M", "L"):
                    d.append(f"{op[0]}{P(op[1])}")
                elif op[0] == "C":
                    d.append("C" + " ".join(P(p) for p in op[1:]))
                else:
                    d.append("Z")
            body.append(f'<path d="{" ".join(d)}" {style_attrs(e)} fill-rule="evenodd"/>')
        elif e["k"] == "ellipse":
            if abs(e["rx"] - e["ry"]) < 1e-4:
                body.append(f'<circle cx="{fmt(e["cx"] - minx)}" cy="{fmt(e["cy"] - miny)}" r="{fmt(e["rx"])}" {style_attrs(e)}/>')
            else:
                body.append(f'<ellipse cx="{fmt(e["cx"] - minx)}" cy="{fmt(e["cy"] - miny)}" rx="{fmt(e["rx"])}" ry="{fmt(e["ry"])}" {style_attrs(e)}/>')
        else:
            attrs = (f'font-family="Helvetica" font-size="{fmt(e["fs"])}" text-anchor="{e["anchor"]}" '
                     f'fill="{e["fill"]}" xml:space="preserve"')
            if e["rot"]:
                for line, x, y in e["lines"]:
                    if line.strip():
                        xx, yy = fmt(x - minx), fmt(y - miny)
                        body.append(f'<text x="{xx}" y="{yy}" {attrs} transform="rotate({fmt(e["rot"])} {xx} {yy})">{escape(line)}</text>')
            else:
                spans = "".join(f'<tspan x="{fmt(x - minx)}" y="{fmt(y - miny)}">{escape(line)}</tspan>'
                                for line, x, y in e["lines"] if line.strip())
                if spans:
                    body.append(f"<text {attrs}>{spans}</text>")
    comment = f"AREI Visio stencil {stencil_name}.vssx, master \"{master_name}\" (symbol {symbol}); converted by tools/vssx_to_svg.py"
    comment = comment.replace("--", "- -")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w)}mm" height="{fmt(h)}mm" viewBox="0 0 {fmt(w)} {fmt(h)}" '
        'stroke-linecap="round" stroke-linejoin="round">\n'
        f"<!-- {comment} -->\n" + "\n".join(body) + "\n</svg>\n"
    )


# --------------------------------------------------------------------------- driver
def convert(symbol: str, stencils: dict[str, Stencil]) -> bool:
    stencil_name, master_name = SYMBOLS[symbol]
    st = stencils.get(stencil_name)
    if st is None:
        st = stencils[stencil_name] = Stencil(SRC_DIR / f"{stencil_name}.vssx")
    if st.find_master(master_name) is None:
        print(f"ERROR {symbol}: master {master_name!r} not found in {stencil_name}.vssx. Available NameU values:")
        for n in st.masters:
            print("   ", n)
        sys.exit(2)
    root = st.load_master(master_name)
    ctx = Ctx(st, symbol)
    out: list = []
    base = (MM, 0.0, 0.0, -MM, 0.0, 0.0)  # inches (y up) -> mm (y down)
    shapes = root.find(NS + "Shapes")
    for sh in shapes.findall(NS + "Shape"):
        walk(ctx, sh, base, out)
    global GUIDES_SKIPPED
    GUIDES_SKIPPED += ctx.guides_skipped
    svg = build_svg(symbol, stencil_name, master_name, out)
    if svg is None:
        warn(symbol, "no drawable geometry found, no SVG written")
        return False
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{symbol}.svg").write_text(svg, encoding="utf-8", newline="\n")
    return True


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ids = argv[1:] or list(SYMBOLS)
    bad = [i for i in ids if i not in SYMBOLS]
    if bad:
        print("unknown symbol id(s):", ", ".join(bad))
        return 2
    stencils: dict[str, Stencil] = {}
    done = 0
    for sid in ids:
        if convert(sid, stencils):
            done += 1
    print(f"info: {GUIDES_SKIPPED} Visio guide shape(s) (construction InfiniteLine rows) skipped by design")
    print(f"converted {done}/{len(ids)} symbols to {OUT_DIR}; {len(WARNINGS)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
