#!/usr/bin/env python3
"""The World in One Day -- 23 November 2026 (illustrated broadsheet).

A real vintage newspaper front page, drawn by hand in pure Python 3
standard library: a hand-written PNG encoder, an embedded 5x10 bitmap
font, and engraved-style illustrations made from shapes, stipple and
cross-hatching -- no photos, no network, no assets.

This is a SPECIAL EDITION on Jensen Huang's return to Nvidia: the
masthead carries a special-edition banner, the lead headline is the
chief's return, and a LARGE halftone-style keynote picture (the chief
back on stage, a giant GPU behind him) dominates the upper half. The
rest of the page is the IMPACT of the return -- stocks, crypto, the
chip industry -- with dense body columns underneath, a small market
chart, and period-style advertisement boxes along the bottom.

Only six stories, all dated Monday 23 November 2026 and verified
against real reporting (see NEWS.md), each with a headline and 3-5
lines of real body copy. Nothing invented.

Writes the image to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
Runs with no network. Deterministic: two runs write identical bytes.

Entry for make.fun competition news-image-20261123.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- font ----
# 5x10 bitmap font: 10 rows of 5 cells ("#" = ink). Taller than the usual
# 5x7, so letters get real stems, curves and counters instead of blocks.
# All page text is set in capitals. Authored here from scratch.
FONT = {
    "A": (".###.", "#...#", "#...#", "#...#", "#####", "#...#", "#...#",
          "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "#...#", "####.", "#...#", "#...#",
          "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", "#....",
          "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#",
          "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "#....", "####.", "#....", "#....",
          "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "#....", "####.", "#....", "#....",
          "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#....", "#..##", "#...#", "#...#",
          "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#...#", "#####", "#...#", "#...#",
          "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..",
          "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "...#.", "...#.",
          "#..#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "##...", "#.#..", "#..#.",
          "#...#", "#...#", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#....",
          "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#",
          "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#.#.#", "#..##", "#..##",
          "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#",
          "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "#...#", "####.", "#....", "#....",
          "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#",
          "#...#", "#.#..", "..##."),
    "R": ("####.", "#...#", "#...#", "#...#", "####.", "#.#..", "#..#.",
          "#...#", "#...#", "#...#"),
    "S": (".####", "#....", "#....", "#....", ".###.", "....#", "....#",
          "....#", "#...#", ".###."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..",
          "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#",
          "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#",
          ".#.#.", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", "#.#.#",
          "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", "#...#", ".#.#.", ".#.#.", "..#..", "..#..", ".#.#.",
          ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", ".#.#.", "..#..", "..#..", "..#..",
          "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", ".#...",
          ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", "#...#",
          "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "..#..",
          "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "....#", "...#.", "..#..", ".#...",
          "#....", "#....", "#####"),
    "3": ("####.", "....#", "....#", "....#", ".###.", "....#", "....#",
          "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#..#.", "#####", "...#.",
          "...#.", "...#.", "...#."),
    "5": ("#####", "#....", "#....", "####.", "....#", "....#", "....#",
          "#...#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "#....", "####.", "#...#", "#...#",
          "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#..",
          "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", "#...#", ".###.", "#...#", "#...#",
          "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", "#...#", ".####", "....#", "....#",
          "....#", "#...#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", ".....",
          ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", ".....",
          ".....", "..##.", "..##."),
    ",": (".....", ".....", ".....", ".....", ".....", ".....", ".....",
          ".....", "..##.", ".#..."),
    ":": (".....", "..##.", "..##.", ".....", ".....", ".....", ".....",
          "..##.", "..##.", "....."),
    ";": (".....", "..##.", "..##.", ".....", ".....", ".....", ".....",
          "..##.", "..##.", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", ".....",
          ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".....", ".###.", ".....", ".....",
          ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..",
          ".....", "..#..", "....."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", "..#..", ".....",
          ".....", "..#..", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", ".#...", ".#...",
          ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "...#.", "...#.",
          "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", "..#..", ".#...",
          ".#...", "#....", "#...."),
    "&": (".###.", "#...#", "#...#", ".#...", "#.#..", "#..#.", "#.#.#",
          "#..#.", "#.#..", ".##.#"),
    "%": ("##...", "##...", "..#..", "..#..", ".#...", ".#...", "#....",
          "#....", "...##", "...##"),
    "+": (".....", "..#..", "..#..", "..#..", ".###.", "..#..", "..#..",
          "..#..", ".....", "....."),
    "=": (".....", ".....", ".....", ".####", ".....", ".####", ".....",
          ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", ".....",
          ".....", ".....", "....."),
    "*": (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", ".....",
          ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", "#.#..", ".###.", "..#.#", "..#.#",
          ".####", "..#..", "....."),
}

GLYPH_W, GLYPH_H = 5, 10

# ------------------------------------------------------------- palette ----
PAPER = (246, 239, 219)   # cream newsprint
INK = (25, 21, 18)        # black ink
ACCENT = (124, 45, 30)    # muted oxblood, used only for the date line
FAINT = (120, 110, 92)    # faint tone for the distant ship and rules

W, H = 1024, 1024


def _hash(x, y, seed):
    """Deterministic integer hash in 0..99, for stipple patterns."""
    v = (x * 2654435761) ^ (y * 40503) ^ (seed * 2246822519)
    v &= 0xFFFFFFFF
    v ^= v >> 13
    v &= 0xFFFFFFFF
    return v % 100


class Page:
    """An RGB canvas with newspaper drawing primitives."""

    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.px = bytearray(PAPER * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            for x in range(x0, x1 + 1):
                self.set(x, y + t, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            for y in range(y0, y1 + 1):
                self.set(x + t, y, color)

    def frame(self, x0, y0, x1, y1, color, thick=1):
        self.hline(x0, x1, y0, color, thick)
        self.hline(x0, x1, y1 - thick + 1, color, thick)
        self.vline(x0, y0, y1, color, thick)
        self.vline(x1 - thick + 1, y0, y1, color, thick)

    def diamond(self, cx, cy, r, color):
        for d in range(-r, r + 1):
            span = r - abs(d)
            self.hline(cx - span, cx + span, cy + d, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color, fill=True):
        """Filled or outline circle (scanline)."""
        for dy in range(-r, r + 1):
            span = int((r * r - dy * dy) ** 0.5)
            if fill:
                self.hline(cx - span, cx + span, cy + dy, color)
            else:
                self.set(cx - span, cy + dy, color)
                self.set(cx + span, cy + dy, color)

    def ellipse(self, cx, cy, rx, ry, color, fill=True):
        """Filled or outline ellipse (scanline)."""
        for dy in range(-ry, ry + 1):
            span = int(rx * (1 - (dy * dy) / float(ry * ry)) ** 0.5)
            if fill:
                self.hline(cx - span, cx + span, cy + dy, color)
            else:
                self.set(cx - span, cy + dy, color)
                self.set(cx + span, cy + dy, color)

    def poly(self, points, color):
        """Fill a polygon (scanline, even-odd)."""
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / float(y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, color)

    def stipple(self, x0, y0, x1, y1, density, color, seed=1, step=2):
        """Halftone dots: density 0..100 of the pixels in the box."""
        for y in range(y0, y1, step):
            for x in range(x0, x1, step):
                if _hash(x, y, seed) < density:
                    self.set(x, y, color)

    def hatch(self, x0, y0, x1, y1, spacing, color):
        """Diagonal engraving lines, clipped exactly to the box.

        A pixel is on a line when (x + y) is a multiple of spacing, so
        nothing spills outside the rectangle.
        """
        for y in range(y0, y1):
            for x in range(x0, x1):
                if (x + y) % spacing == 0:
                    self.set(x, y, color)

    def stipple_ellipse(self, cx, cy, rx, ry, density, color, seed=1):
        """Halftone dots clipped to an ellipse (smoke, clouds)."""
        for y in range(cy - ry, cy + ry + 1, 2):
            for x in range(cx - rx, cx + rx + 1, 2):
                inside = ((x - cx) * (x - cx)) / float(rx * rx) + \
                    ((y - cy) * (y - cy)) / float(ry * ry) <= 1.0
                if inside and _hash(x, y, seed) < density:
                    self.set(x, y, color)

    # -- text -------------------------------------------------------------
    def char_w(self, ch, scale, gap=1):
        if ch == " ":
            return 4 * scale + gap
        return GLYPH_W * scale + gap

    def text_w(self, s, scale, gap=1):
        if not s:
            return 0
        return sum(self.char_w(c, scale, gap) for c in s) - gap

    def text(self, s, x, y, scale, color, gap=1):
        """Draw text; returns the x just past the last glyph."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                raise ValueError("no glyph for %r" % ch)
            cols = 4 if ch == " " else GLYPH_W
            for row in range(GLYPH_H):
                bits = glyph[row]
                for col in range(cols):
                    if bits[col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += self.char_w(ch, scale, gap)
        return cx

    def text_c(self, s, cx, y, scale, color, gap=1):
        """Draw text centred on cx."""
        self.text(s, cx - self.text_w(s, scale, gap) // 2, y, scale, color,
                  gap)

    def text_bold(self, s, x, y, scale, color, gap=1, dx=1):
        """Draw text twice, dx px apart, for a bold headline face."""
        self.text(s, x, y, scale, color, gap)
        self.text(s, x + dx, y, scale, color, gap)

    def text_c_bold(self, s, cx, y, scale, color, gap=1, dx=1):
        self.text_bold(s, cx - self.text_w(s, scale, gap) // 2, y, scale,
                       color, gap, dx)

    def wrap(self, s, max_chars):
        """Greedy word wrap into lines of at most max_chars characters."""
        lines, cur = [], ""
        for word in s.split(" "):
            trial = (cur + " " + word).strip()
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def write_png(page, path):
    """Encode the page as a 24-bit RGB PNG (filter 0, zlib level 9)."""
    raw = bytearray()
    for y in range(page.h):
        raw.append(0)
        raw += page.px[y * page.w * 3:(y + 1) * page.w * 3]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", page.w, page.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------ the news ----
# Seven stories, all dated Monday 23 November 2026 and verified against
# real reporting (BBC, Reuters, AP, Al Jazeera, CNN, Ukrinform,
# BusinessWorld). The full 40-story list with sources is in NEWS.md;
# these are the day's most newsworthy items, each with a headline and
# 3-5 lines of real body copy. Nothing invented.

# (headline, body) -- body wraps to at most 28 characters a line in a
# 312 px column at scale 2. Special edition: the lead is Huang's
# return; the rest of the page is its impact -- stocks, crypto, chips.
STORIES = {
    "huang": (
        "HUANG BACK AT NVIDIA",
        "THE BOARD BROUGHT ITS CHIEF BACK 11 DAYS AFTER HE RESIGNED, "
        "AFTER PRESSURE FROM PRESIDENT TRUMP. SHARES JUMPED BY ABOUT "
        "A THIRD."),
    "nasdaq": (
        "NASDAQ SOARS 6 PERCENT",
        "THE NASDAQ ROSE 6 PERCENT ON THE AI RALLY AS NVIDIA "
        "REBOUNDED. CHIP STOCKS LED THE GAINS."),
    "bitcoin": (
        "BITCOIN DIPS, THEN RECOVERS",
        "BITCOIN DIPPED, THEN RECOVERED, AS CRYPTO FOLLOWED THE "
        "RALLY."),
    "asia": (
        "ASIA STEADIES THE MARKET",
        "ASIAN STATES STEADIED THE MARKET AFTER THE AI SELL-OFF."),
    "shirudo": (
        "OPENAI LAUNCHES SHIRUDO",
        "OPENAI LAUNCHED SHIRUDO, AN AI SECURITY TOOL FOR LINUX "
        "SERVERS, BUILT WITH CISCO."),
    "labs": (
        "AI LABS URGED TO SET LIMITS",
        "AI LABS WERE URGED TO SET SHARED SAFETY LIMITS AS THE "
        "INDUSTRY RACES AHEAD."),
    "oil": (
        "OIL SLIDES TO A LOW",
        "OIL SLID TO A THREE-MONTH LOW AS SUPPLY GREW."),
}

MARKET_WIRES = ("MARKET WIRES - SOUTH AFRICA UNVEILS A $5.7M AI PLAN "
                "AFTER A SILICON VALLEY TRIP.")


# --------------------------------------------------------- illustrations ----
def draw_keynote(p, x0, y0, x1, y1):
    """The lead picture: Huang back on stage, a giant GPU behind him.

    A keynote scene in engraved halftone style: a stippled stage
    backdrop with spotlight beams, a giant microchip with pins and
    radiating lines on the right, and the chief in his black leather
    jacket at a podium on the left. Bold and simple, so it reads at
    a glance as the chip chief back on stage.
    """
    p.frame(x0, y0, x1, y1, INK, 2)
    ix0, iy0, ix1, iy1 = x0 + 2, y0 + 2, x1 - 2, y1 - 2
    # Stage backdrop: light stipple, denser towards the top.
    p.stipple(ix0, iy0, ix1, iy0 + 90, 8, INK, seed=11)
    p.stipple(ix0, iy0 + 90, ix1, iy1, 4, INK, seed=12)
    # Spotlight beams from the top corners down to the stage.
    p.line(ix0 + 60, iy0, 250, iy1 - 30, INK)
    p.line(ix0 + 90, iy0, 280, iy1 - 30, INK)
    p.line(ix1 - 60, iy0, 700, iy1 - 30, INK)
    p.line(ix1 - 90, iy0, 670, iy1 - 30, INK)
    # Radiating lines out from behind the chip, upper right.
    cx, cy = 765, 410
    for (tx, ty) in ((ix1, iy0 + 10), (ix1, iy0 + 80), (ix1, iy0 + 170),
                     (ix1, iy1 - 20), (700, iy0), (830, iy0),
                     (950, iy0)):
        p.line(cx, cy, tx, ty, INK)
    # The giant GPU: black slab with pins on all four sides, a paper
    # die in the middle with circuit traces and the letters GPU.
    p.rect(580, 315, 370, 190, INK)
    for px in range(596, 944, 18):
        p.rect(px, 303, 9, 12, INK)
        p.rect(px, 505, 9, 12, INK)
    for py in range(331, 494, 18):
        p.rect(568, py, 12, 9, INK)
        p.rect(950, py, 12, 9, INK)
    p.rect(620, 345, 290, 130, PAPER)
    p.hline(640, 890, 375, INK)
    p.hline(640, 890, 445, INK)
    p.vline(700, 365, 455, INK)
    p.vline(820, 365, 455, INK)
    p.text("GPU", 734, 395, 4, INK)
    # The chief: black leather jacket, white shirt, at the podium.
    p.circle(330, 372, 19, INK, fill=True)
    p.rect(322, 390, 16, 14, INK)
    p.poly([(286, 404), (374, 404), (394, 472), (266, 472)], INK)
    p.poly([(316, 404), (344, 404), (330, 440)], PAPER)
    p.line(330, 404, 302, 468, PAPER)
    p.line(330, 404, 358, 468, PAPER)
    # The podium with the company name, and a gooseneck microphone.
    p.rect(248, 472, 184, 58, INK)
    p.rect(262, 484, 156, 34, PAPER)
    p.text("NVIDIA", 323, 496, 1, INK)
    p.line(398, 472, 370, 414, INK)
    p.circle(368, 411, 5, INK, fill=True)


def draw_chart(p, x, y, w, h):
    """A small market chart: the index dips, then soars on the rally."""
    p.frame(x, y, x + w - 1, y + h - 1, INK, 1)
    ix, iy = x + 1, y + 1
    iw, ih = w - 2, h - 2
    for gy in (iy + ih // 3, iy + 2 * ih // 3):
        for gx in range(ix, ix + iw, 6):
            p.set(gx, gy, FAINT)
    pts = [(ix + 6, iy + ih - 18), (ix + 50, iy + ih - 26),
           (ix + 90, iy + ih - 14), (ix + 130, iy + ih - 34),
           (ix + 170, iy + 40), (ix + 210, iy + 26),
           (ix + 250, iy + 18), (ix + iw - 6, iy + 10)]
    for a, b in zip(pts, pts[1:]):
        p.line(a[0], a[1], b[0], b[1], INK)
        p.line(a[0], a[1] + 1, b[0], b[1] + 1, INK)
    p.text("NASDAQ +6%", ix + 8, iy + 6, 1, INK)


def draw_photo(p, x0, y0, x1, y1):
    """The lead picture: a corvette at sea, engraved halftone style.

    Sky with stipple and clouds, a sea drone in the air, the corvette
    with smoke from its funnel, waves and a distant ship on the horizon.
    Coordinates are relative to the photo box.
    """
    p.frame(x0, y0, x1, y1, INK, 2)
    ix0, iy0, ix1, iy1 = x0 + 2, y0 + 2, x1 - 2, y1 - 2
    horizon = iy0 + 108
    # Sky: light stipple, denser near the horizon.
    p.stipple(ix0, iy0, ix1, horizon - 30, 5, INK, seed=11)
    p.stipple(ix0, horizon - 30, ix1, horizon, 10, INK, seed=12)
    # Clouds: paper ellipses (cut out of the stipple) with a light
    # stipple of their own and ink rims, so they read as shaded clouds.
    for cx, cy, rx, ry, seed in ((210, iy0 + 34, 74, 13, 61),
                                 (540, iy0 + 22, 92, 15, 62),
                                 (840, iy0 + 42, 62, 11, 63)):
        p.ellipse(cx, cy, rx, ry, PAPER, fill=True)
        p.stipple_ellipse(cx, cy, rx, ry, 10, INK, seed=seed)
        p.ellipse(cx, cy, rx, ry, INK, fill=False)
    # A sea drone in the sky, upper right.
    dx, dy = 770, iy0 + 62
    p.rect(dx - 8, dy - 3, 16, 7, INK)
    p.line(dx - 20, dy - 12, dx - 6, dy - 4, INK)
    p.line(dx + 6, dy - 4, dx + 20, dy - 12, INK)
    p.line(dx - 20, dy + 12, dx - 6, dy + 4, INK)
    p.line(dx + 6, dy + 4, dx + 20, dy + 12, INK)
    p.hline(dx - 24, dx - 2, dy - 13, INK)
    p.hline(dx + 2, dx + 24, dy - 13, INK)
    p.hline(dx - 24, dx - 2, dy + 13, INK)
    p.hline(dx + 2, dx + 24, dy + 13, INK)
    # Sea: stipple deepening towards the bottom of the picture.
    for (ya, yb, dens, seed) in ((horizon, horizon + 38, 8, 21),
                                 (horizon + 38, horizon + 76, 14, 22),
                                 (horizon + 76, horizon + 114, 20, 23),
                                 (horizon + 114, iy1, 28, 24)):
        p.stipple(ix0, ya, ix1, yb, dens, INK, seed=seed)
    # Wave lines: short dotted strokes that rise and fall.
    for wy in (horizon + 16, horizon + 44, horizon + 72, horizon + 100,
               horizon + 128):
        x = ix0 + 8
        while x < ix1 - 30:
            off = ((x * 7 + wy * 13) % 5) - 2
            p.hline(x, x + 16, wy + off, INK)
            x += 34
    # Distant ship on the horizon, left, in a faint tone.
    fx, fy = ix0 + 90, horizon - 8
    p.poly([(fx, fy + 4), (fx + 84, fy + 4), (fx + 78, fy + 14),
            (fx + 6, fy + 14)], FAINT)
    p.rect(fx + 34, fy - 10, 6, 14, FAINT)
    p.rect(fx + 52, fy - 6, 4, 10, FAINT)
    # The corvette herself, centre: hull, deck, superstructure, funnel
    # with smoke, masts, a gun turret forward, portholes, foam at the bow.
    hx0, hx1 = 300, 720
    deck = horizon + 66
    p.poly([(hx0 + 10, deck), (hx1 - 10, deck), (hx1 + 5, deck + 8),
            (hx1 - 15, deck + 35), (hx0 + 35, deck + 35),
            (hx0, deck + 18)], INK)
    p.hline(hx0 + 12, hx1 - 12, deck + 1, PAPER)
    for px in range(hx0 + 42, hx1 - 30, 40):
        p.rect(px, deck + 18, 4, 4, PAPER)
    p.rect(420, deck - 30, 110, 30, INK)
    for wx in range(432, 520, 22):
        p.rect(wx, deck - 22, 10, 8, PAPER)
    p.rect(445, deck - 42, 60, 12, INK)
    p.rect(560, deck - 55, 30, 28, INK)
    p.hline(560, 589, deck - 48, PAPER, 2)
    p.vline(450, deck - 78, deck - 42, INK, 2)
    p.poly([(452, deck - 78), (470, deck - 73), (452, deck - 68)], INK)
    p.vline(650, deck - 68, deck - 30, INK, 2)
    p.rect(640, deck - 18, 34, 18, INK)
    p.line(674, deck - 12, 700, deck - 16, INK)
    # Smoke from the funnel, drifting right, as stippled clouds.
    for cx, cy, rx, ry, seed in ((575, deck - 70, 26, 12, 31),
                                 (602, deck - 86, 30, 13, 32),
                                 (634, deck - 100, 34, 14, 33)):
        p.ellipse(cx, cy, rx, ry, PAPER, fill=True)
        p.stipple_ellipse(cx, cy, rx, ry, 42, INK, seed=seed)
        p.ellipse(cx, cy, rx, ry, INK, fill=False)
    # Foam where the hull meets the water.
    p.ellipse(hx0 + 30, deck + 36, 46, 6, PAPER, fill=True)
    p.ellipse(hx1 - 10, deck + 36, 40, 6, PAPER, fill=True)
    p.ellipse(hx0 + 330, deck + 38, 120, 5, PAPER, fill=True)


def hatch_poly(p, points, spacing, color):
    """Diagonal engraving lines clipped to a polygon (map land)."""
    ys = [q[1] for q in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / float(y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                if (x + y) % spacing == 0:
                    p.set(x, y, color)


def draw_map(p, x, y, w, h):
    """A small schematic map of the eastern Mediterranean.

    Hatched land north and south, a stippled sea between them, and a
    diamond marking Benghazi on the Libyan coast.
    """
    p.frame(x, y, x + w - 1, y + h - 1, INK, 1)
    ix, iy = x + 1, y + 1
    iw, ih = w - 2, h - 2
    p.stipple(ix, iy, ix + iw, iy + ih, 6, INK, seed=41)
    # Northern land (Europe): hatched polygon along the top.
    north = [(ix, iy), (ix + iw, iy), (ix + iw, iy + 26),
             (ix + 230, iy + 34), (ix + 180, iy + 22), (ix + 120, iy + 30),
             (ix + 60, iy + 20), (ix, iy + 28)]
    p.poly(north, PAPER)
    hatch_poly(p, north, 7, INK)
    p.line(ix, iy + 28, ix + 60, iy + 20, INK)
    p.line(ix + 60, iy + 20, ix + 120, iy + 30, INK)
    p.line(ix + 120, iy + 30, ix + 180, iy + 22, INK)
    p.line(ix + 180, iy + 22, ix + 230, iy + 34, INK)
    p.line(ix + 230, iy + 34, ix + iw, iy + 26, INK)
    # Southern land (Africa): hatched polygon along the bottom.
    south = [(ix, iy + ih), (ix + iw, iy + ih), (ix + iw, iy + 78),
             (ix + 240, iy + 70), (ix + 170, iy + 82), (ix + 90, iy + 72),
             (ix, iy + 80)]
    p.poly(south, PAPER)
    hatch_poly(p, south, 7, INK)
    p.line(ix, iy + 80, ix + 90, iy + 72, INK)
    p.line(ix + 90, iy + 72, ix + 170, iy + 82, INK)
    p.line(ix + 170, iy + 82, ix + 240, iy + 70, INK)
    p.line(ix + 240, iy + 70, ix + iw, iy + 78, INK)
    # Labels and the Benghazi mark.
    p.text("EUROPE", ix + 10, iy + 6, 1, INK)
    p.text("AFRICA", ix + 10, iy + ih - 14, 1, INK)
    p.text("MEDITERRANEAN SEA", ix + 84, iy + 46, 1, INK)
    bx, by = ix + 228, iy + 74
    p.diamond(bx, by, 5, ACCENT)
    p.text("BENGHAZI", bx + 10, by - 4, 1, INK)
    # Compass rose, upper right.
    cx, cy = ix + iw - 26, iy + 20
    p.circle(cx, cy, 10, INK, fill=False)
    p.line(cx, cy - 10, cx, cy + 10, INK)
    p.line(cx - 10, cy, cx + 10, cy, INK)
    p.text("N", cx - 3, cy - 20, 1, INK)


def icon_cup(p, x, y):
    """A steaming teacup for the tea advertisement."""
    p.line(x + 8, y + 6, x + 12, y + 14, INK)
    p.line(x + 28, y + 6, x + 24, y + 14, INK)
    p.poly([(x + 4, y + 16), (x + 32, y + 16), (x + 29, y + 30),
            (x + 7, y + 30)], INK)
    p.hline(x + 2, x + 34, y + 33, INK, 2)
    p.rect(x + 32, y + 19, 6, 8, INK)
    p.rect(x + 34, y + 21, 2, 4, PAPER)


def icon_bottle(p, x, y):
    """A tonic bottle for the elixir advertisement."""
    p.rect(x + 14, y + 2, 8, 4, INK)
    p.rect(x + 16, y + 6, 4, 8, INK)
    p.rect(x + 10, y + 14, 16, 22, INK)
    p.rect(x + 13, y + 20, 10, 10, PAPER)
    p.text("E", x + 15, y + 21, 1, INK)


def icon_steamer(p, x, y):
    """A small steamship for the steamship-line advertisement."""
    p.poly([(x + 2, y + 24), (x + 34, y + 24), (x + 30, y + 32),
            (x + 6, y + 32)], INK)
    p.rect(x + 12, y + 14, 12, 10, INK)
    p.rect(x + 16, y + 4, 5, 10, INK)
    p.stipple(x + 12, y - 6, x + 26, y + 2, 45, INK, seed=51)
    p.hline(x, x + 36, y + 36, INK)

# ------------------------------------------------------------- layout ----
M = 26            # side margin inside the frame
COLW = 312        # body column width (18 px gutters)
COLX = [M, 356, 686]
PHOTO_Y0, PHOTO_Y1 = 292, 532
BODY_Y0, BODY_Y1 = 570, 880

ADS = [
    ("THE WORLD'S FINEST TEA", "PURE CEYLON LEAF TEA",
     "SOLD BY ALL GROCERS", icon_cup),
    ("TINCTORIAL ELIXIR", "FOR THE NERVES",
     "A SPOONFUL AT BEDTIME", icon_bottle),
    ("OCEAN STEAMSHIP LINE", "WEEKLY SAILINGS",
     "TO ALL THE WORLD'S PORTS", icon_steamer),
]


def story_block(p, x, y, key):
    """Headline bold at scale 2, then 3-5 lines of body copy below it."""
    headline, body = STORIES[key]
    p.text_bold(headline, x, y, 2, INK)
    y += 22
    for line in p.wrap(body, 28):
        p.text(line, x, y, 2, INK)
        y += 21
    return y + 4


def draw_body(p):
    heights = []
    # Column 1: the return itself, then the Nasdaq rally.
    y = BODY_Y0
    y = story_block(p, COLX[0], y, "huang")
    y = story_block(p, COLX[0], y + 6, "nasdaq")
    heights.append(y)
    # Column 2: crypto, Asia, then the market chart.
    y = BODY_Y0
    y = story_block(p, COLX[1], y, "bitcoin")
    y = story_block(p, COLX[1], y + 6, "asia")
    y += 6
    p.text_c("THE MARKET REBOUNDS", COLX[1] + COLW // 2, y, 1, INK)
    y += 14
    draw_chart(p, COLX[1], y, COLW, 84)
    y += 84 + 4
    p.text_c("NASDAQ +6 PERCENT ON THE AI RALLY", COLX[1] + COLW // 2, y,
             1, INK)
    y += 10
    heights.append(y)
    # Column 3: the AI industry -- OpenAI, safety limits, oil.
    y = BODY_Y0
    y = story_block(p, COLX[2], y, "shirudo")
    y = story_block(p, COLX[2], y + 6, "labs")
    y = story_block(p, COLX[2], y + 6, "oil")
    heights.append(y)
    for i, h in enumerate(heights):
        if h > BODY_Y1:
            raise SystemExit("column %d overflows by %d px"
                             % (i, h - BODY_Y1))
    print("column end heights: %s (limit %d)" % (heights, BODY_Y1))


def draw_ads(p):
    for i, (title, line1, line2, icon) in enumerate(ADS):
        x = COLX[i]
        y = 920
        p.frame(x, y, x + COLW - 1, y + 77, INK, 1)
        icon(p, x + 10, y + 20)
        p.text_bold(title, x + 56, y + 10, 2, INK)
        p.text(line1, x + 56, y + 36, 1, INK)
        p.text(line2, x + 56, y + 50, 1, INK)


def draw_page():
    p = Page()
    # Double frame, like a broadsheet's border.
    p.frame(12, 12, 1011, 1011, INK, 2)
    p.frame(19, 19, 1004, 1004, INK, 1)
    # Top meta line: issue number, volume, price.
    p.text("NO. 14,832", M, 25, 1, INK)
    p.text_c("VOL. I - NO. 327", W // 2, 25, 1, INK)
    p.text("PRICE ONE CENT", W - M - p.text_w("PRICE ONE CENT", 1), 25, 1,
           INK)
    # Masthead: big and bold, double-struck for a blackletter feel.
    p.text_c_bold("THE WORLD IN ONE DAY", W // 2, 38, 7, INK, gap=2, dx=2)
    # Ornamental rule with diamonds.
    p.hline(M, W - M - 1, 114, INK, 2)
    p.hline(M, W - M - 1, 120, INK, 1)
    for cx in (300, 512, 724):
        p.diamond(cx, 117, 6, INK)
    # Dateline in oxblood, with flanking rules, then the special
    # edition banner.
    p.hline(M, 340, 137, ACCENT, 2)
    p.hline(684, W - M - 1, 137, ACCENT, 2)
    p.text_c_bold("MONDAY, NOVEMBER 23, 2026", W // 2, 128, 2, ACCENT)
    p.text_c_bold("SPECIAL EDITION", W // 2, 152, 2, ACCENT)
    p.hline(M, W - M - 1, 166, INK, 2)
    # The lead headline, full width, two lines.
    p.text_c_bold("HUANG BACK AT NVIDIA", W // 2, 176, 4, INK)
    p.text_c_bold("THE CHIEF RETURNS", W // 2, 224, 4, INK)
    p.text_c("THE BOARD BRINGS ITS CHIEF BACK 11 DAYS AFTER HE RESIGNED",
             W // 2, 272, 1, INK)
    # The big picture and its caption.
    draw_keynote(p, M, PHOTO_Y0, W - M - 1, PHOTO_Y1)
    p.text_c("JENSEN HUANG, BACK ON STAGE AT NVIDIA.", W // 2, 540, 1,
             INK)
    p.hline(M, W - M - 1, 558, INK, 2)
    # Body columns, then the late-news bar and the advertisements.
    draw_body(p)
    p.hline(M, W - M - 1, 888, INK, 1)
    p.text_c(MARKET_WIRES, W // 2, 896, 1, INK)
    p.hline(M, W - M - 1, 912, INK, 1)
    draw_ads(p)
    return p


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    page = draw_page()
    size = write_png(page, path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
