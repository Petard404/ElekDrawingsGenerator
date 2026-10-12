"""Hand-built pages that exercise the renderer."""
from huiselek.primitives import Arc, Circle, Line, Page, Polyline, Rect, Style, Text

LABEL_X = 15.0
ITEM_X = 80.0
LABEL_SIZE = 3.0


def primitives_page() -> Page:
    prims: list = []
    y = 20.0

    def label(txt: str, yy: float) -> None:
        prims.append(Text(LABEL_X, yy, txt, LABEL_SIZE))

    prims.append(Text(LABEL_X, y, "Primitieven", 5.0))
    y += 12

    # Lines: thin, thick, dashed, dash-dot
    for txt, st in [
        ("Lijn dun 0,18 mm", Style(stroke_width=0.18)),
        ("Lijn dik 0,5 mm", Style(stroke_width=0.5)),
        ("Lijn gestreept", Style(dash=(2.0, 1.0))),
        ("Lijn streep-punt", Style(stroke="#cc0000", dash=(3.0, 1.0, 0.5, 1.0))),
    ]:
        label(txt, y + 1)
        prims.append(Line(ITEM_X, y, 190.0, y, st))
        y += 8

    # Rects
    y += 2
    label("Rechthoek, leeg en gevuld", y + 5)
    prims.append(Rect(ITEM_X, y, 30.0, 8.0, Style()))
    prims.append(Rect(ITEM_X + 45.0, y, 30.0, 8.0, Style(fill="#cccccc")))
    y += 16

    # Circles
    label("Cirkel, leeg en gevuld", y + 5)
    prims.append(Circle(ITEM_X + 5.0, y + 4.0, 4.0, Style()))
    prims.append(Circle(ITEM_X + 50.0, y + 4.0, 4.0, Style(fill="#000000")))
    prims.append(Text(ITEM_X + 57.0, y + 5.0, "gevuld", LABEL_SIZE))
    y += 14

    # Polylines
    label("Polylijn, open en gesloten", y + 5)
    prims.append(Polyline(((ITEM_X, y + 8), (ITEM_X + 10, y), (ITEM_X + 20, y + 8),
                           (ITEM_X + 30, y)), False, Style()))
    prims.append(Polyline(((ITEM_X + 50, y + 8), (ITEM_X + 60, y), (ITEM_X + 70, y + 8)),
                          True, Style(fill="#ffdd88")))
    y += 16

    # Arcs
    y += 2
    arcs = [("Boog 90°", 0, 90), ("Boog 180°", 0, 180), ("Boog 270°", 0, 270),
            ("Boog 300° tot 60°", 300, 420)]
    label("Bogen", y + 8)
    for i, (txt, a0, a1) in enumerate(arcs):
        cx = ITEM_X + 8 + i * 30
        prims.append(Arc(cx, y + 8, 8.0, a0, a1, Style()))
        prims.append(Text(cx, y + 22, txt, 2.5, "middle"))
    y += 30

    # Text anchors
    label("Tekst met ankers", y)
    prims.append(Line(ITEM_X + 40, y - 6, ITEM_X + 40, y + 3, Style(stroke_width=0.1)))
    prims.append(Text(ITEM_X + 40, y, "start", 4.0, "start"))
    y += 10
    prims.append(Line(ITEM_X + 40, y - 6, ITEM_X + 40, y + 3, Style(stroke_width=0.1)))
    prims.append(Text(ITEM_X + 40, y, "middle", 4.0, "middle"))
    y += 10
    prims.append(Line(ITEM_X + 40, y - 6, ITEM_X + 40, y + 3, Style(stroke_width=0.1)))
    prims.append(Text(ITEM_X + 40, y, "end", 4.0, "end"))
    y += 10

    # Rotated text
    y += 30
    label("Tekst gedraaid", y)
    prims.append(Text(ITEM_X + 10, y, "Gedraaid 45", 4.0, "start", 45.0))
    prims.append(Text(ITEM_X + 50, y, "Gedraaid -90", 4.0, "start", -90.0))
    y += 32

    # Special characters
    label("Speciale tekens", y)
    prims.append(Text(ITEM_X, y, "XVB Cca 3G2.5² Ø é – & <", 4.0))

    return Page("primitives", 1, "Primitieven", tuple(prims))
