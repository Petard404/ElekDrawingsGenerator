#!/usr/bin/env python
"""Extract the symbol images from the official AREI table 2.23 PDF.

Input : docs/reference/arei/official/arei-boek1-tabel-2.23-grafische-symbolen.pdf
Output: docs/reference/arei/official/images/p<page>_<nn>.<ext>   (page 1-based, nn 1-based in content order)
        docs/reference/arei/official/images/index.csv  (file, page, nn, width_px, height_px, guess)

`guess` is the description text on the same table row, taken from the page text by
position: the first line of the description block whose vertical span is nearest to the
image. It is a best guess and may be wrong or empty (side-by-side images in one row
share a guess; long descriptions with several example images are the weak spot).

Needs pypdf only. JPEG streams are written as-is; Flate gray images are written as PNG
with zlib/struct (no Pillow).
"""
from __future__ import annotations

import csv
import re
import struct
import sys
import zlib
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import ContentStream

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "docs" / "reference" / "arei" / "official" / "arei-boek1-tabel-2.23-grafische-symbolen.pdf"
OUT = ROOT / "docs" / "reference" / "arei" / "official" / "images"

LINE_TOL = 2.0      # pt: fragments within this vertical distance are one text line
ENTRY_GAP = 20.0    # pt: a larger baseline gap starts a new description entry
SYMBOL_COL_X = 340.0  # text starting right of this x is not description text
HEADER_Y = 745.0    # page-space y above/below which text is running header/footer
FOOTER_Y = 45.0


def mmul(a, b):
    """PDF matrix product: a applied first, then b."""
    return [a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3],
            a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3],
            a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5]]


def page_images(page, reader):
    """[(name, x, y, w, h)] in content order (page space, y up)."""
    cs = ContentStream(page.get_contents(), reader)
    ctm = [1, 0, 0, 1, 0, 0]
    stack = []
    found = []
    for args, op in cs.operations:
        if op == b"q":
            stack.append(ctm)
        elif op == b"Q":
            ctm = stack.pop() if stack else [1, 0, 0, 1, 0, 0]
        elif op == b"cm":
            ctm = mmul([float(v) for v in args], ctm)
        elif op == b"Do":
            found.append((str(args[0]), ctm[4], ctm[5], abs(ctm[0]), abs(ctm[3])))
    return found


def text_lines(page):
    """Description-column text lines as [(y, text)] sorted top to bottom (page-space y)."""
    frags = []

    def visit(text, cm, tm, font_dict, font_size):
        if not text.strip():
            return
        x = cm[0] * tm[4] + cm[2] * tm[5] + cm[4]
        y = cm[1] * tm[4] + cm[3] * tm[5] + cm[5]
        frags.append((x, y, text.replace("\n", " ")))

    page.extract_text(visitor_text=visit)
    frags = [f for f in frags if f[0] < SYMBOL_COL_X and FOOTER_Y < f[1] < HEADER_Y]
    frags.sort(key=lambda f: (-f[1], f[0]))
    lines: list[list] = []
    for x, y, t in frags:
        if lines and abs(lines[-1][0] - y) <= LINE_TOL:
            lines[-1][1].append((x, t))
        else:
            lines.append([y, [(x, t)]])
    result = []
    for y, parts in lines:
        text = " ".join(t.strip() for _, t in sorted(parts)).strip()
        text = re.sub(r"\s+", " ", text)
        if not text or text in ("Beschrijving", "Voorbeelden:", "Voorbeeld:") or re.match(r"^[A-Z]\. \S", text) and len(text) < 40:
            continue  # table header and section titles are not row descriptions
        result.append((y, text))
    return result


def image_rows(imgs):
    """Group images that share a table row (vertical bands overlap by more than half) -> [[index, ...]]."""
    order = sorted(range(len(imgs)), key=lambda i: -(imgs[i][2] + imgs[i][4] / 2))
    rows: list[list[int]] = []
    for i in order:
        top, bot = imgs[i][2] + imgs[i][4], imgs[i][2]
        for row in rows:
            r_top = max(imgs[j][2] + imgs[j][4] for j in row)
            r_bot = min(imgs[j][2] for j in row)
            overlap = min(top, r_top) - max(bot, r_bot)
            if overlap > 0.5 * min(top - bot, r_top - r_bot):
                row.append(i)
                break
        else:
            rows.append([i])
    return rows


def guesses(lines, imgs):
    """Image index -> guess.

    Each text line goes to the nearest image row. In a row, the line nearest the row centre is
    the anchor, and the lines around it (gap <= ENTRY_GAP, same row) are its cluster. The
    description starts at the top of the paragraph holding the anchor: walk up over lines
    (gap <= ENTRY_GAP) that are not in another row's cluster, stopping at a "Voorbeeld" line.
    """
    rows = image_rows(imgs)
    centres = [sum(imgs[j][2] + imgs[j][4] / 2 for j in row) / len(row) for row in rows]
    owner = [min(range(len(rows)), key=lambda r: abs(centres[r] - y)) for y, _ in lines]
    anchors, clusters = [], []
    for k in range(len(rows)):
        mine = [i for i, o in enumerate(owner) if o == k]
        if not mine:
            anchors.append(min(range(len(lines)), key=lambda i: abs(lines[i][0] - centres[k])) if lines else None)
            clusters.append(set())
            continue
        a = min(mine, key=lambda i: abs(lines[i][0] - centres[k]))
        c = {a}
        i = a
        while i - 1 in mine and lines[i - 1][0] - lines[i][0] <= ENTRY_GAP:
            i -= 1
            c.add(i)
        i = a
        while i + 1 in mine and lines[i][0] - lines[i + 1][0] <= ENTRY_GAP:
            i += 1
            c.add(i)
        anchors.append(a)
        clusters.append(c)
    out = {}
    for k, row in enumerate(rows):
        first = anchors[k]
        guess = ""
        if first is not None:
            others = set().union(*(clusters[r] for r in range(len(rows)) if r != k)) if len(rows) > 1 else set()
            while (first > 0 and lines[first - 1][0] - lines[first][0] <= ENTRY_GAP and first - 1 not in others
                   and not lines[first][1].startswith("Voorbeeld")):
                first -= 1
            guess = lines[first][1]
        for j in row:
            out[j] = guess
    return out


def png_gray(width, height, raw):
    rows = b"".join(b"\x00" + raw[r * width:(r + 1) * width] for r in range(height))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def image_bytes(xobj):
    """(extension, bytes) for an image XObject without Pillow."""
    filt = xobj.get("/Filter")
    if isinstance(filt, list):
        filt = filt[-1] if filt else None
    w, h = int(xobj["/Width"]), int(xobj["/Height"])
    if filt == "/DCTDecode":
        data = xobj.get_data()
        if data[:2] != b"\xff\xd8":
            data = xobj._data
        return "jpg", data
    if filt == "/FlateDecode" and xobj.get("/ColorSpace") == "/DeviceGray" and int(xobj.get("/BitsPerComponent", 8)) == 8:
        if "/Decode" in xobj:
            print(f"WARNING: image with /Decode array {xobj['/Decode']} written without inversion")
        return "png", png_gray(w, h, xobj.get_data())
    raise ValueError(f"unsupported image: filter={filt} colourspace={xobj.get('/ColorSpace')}")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    reader = PdfReader(str(PDF))
    OUT.mkdir(parents=True, exist_ok=True)
    for old in list(OUT.glob("p*_*.jpg")) + list(OUT.glob("p*_*.png")):
        old.unlink()  # keep the folder deterministic across reruns
    rows = []
    for pno, page in enumerate(reader.pages, start=1):
        xobjs = page["/Resources"].get("/XObject", {})
        imgs = page_images(page, reader)
        guess = guesses(text_lines(page), imgs)
        for nn, img in enumerate(imgs, start=1):
            xobj = xobjs[img[0]].get_object()
            ext, data = image_bytes(xobj)
            name = f"p{pno}_{nn:02d}.{ext}"
            (OUT / name).write_bytes(data)
            rows.append([name, pno, nn, int(xobj["/Width"]), int(xobj["/Height"]), guess[nn - 1]])
    with open(OUT / "index.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["file", "page", "nn", "width_px", "height_px", "guess"])
        w.writerows(rows)
    empty = sum(1 for r in rows if not r[5])
    print(f"extracted {len(rows)} images from {len(reader.pages)} pages to {OUT}; {empty} without guess")
    return 0


if __name__ == "__main__":
    sys.exit(main())
