#!/usr/bin/env python3
"""The World in One Day -- 23 November 2026 (readability redesign).

An old-fashioned broadsheet front page, drawn by hand in pure Python 3
standard library: a hand-written PNG encoder, an embedded 5x10 bitmap
font, and a vintage newspaper layout -- large serif-style masthead with
ornamental rules, black ink on cream paper, thin column rules, small-caps
section headers, a price line and a weather line.

This revision fixes the first version's legibility: the old 5x7 font is
replaced by a 5x10 face (taller, narrower glyphs with real letterforms),
word spaces are widened, every text line gets real leading, headlines
are clearly larger than body text, and every brief is cut to one short
line so the columns breathe instead of packing three wrapped lines.

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
FAINT = (120, 110, 92)    # faint rule / ornament tone

W, H = 1024, 1024


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

    # -- text -------------------------------------------------------------
    def char_w(self, ch, scale, gap=1):
        # A word space is narrower than a letter but clearly wider than
        # the 1 px gap between letters, so words separate at a glance.
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
# 40 stories, all dated 23 November 2026, verified against real reporting
# (BBC, Reuters, AP, Al Jazeera, CNN, Ukrinform, BusinessWorld). Two items
# the first draft brief got wrong were dropped: the Nepal earthquake and
# the Shenzhou-24 crew unveiling both happened on 24 November, not the
# 23rd. Two aggregator-only claims (a Shenzhen summit; 258 House seats)
# were dropped as unverified.
#
# Readability rule for this revision: every headline fits one line and
# every brief fits one line at scale 2 in a 312 px column (at most 28
# characters). Briefs are cut to their sharpest fact, never invented.

LEADS = [
    ("UKRAINE SINKS", "RUSSIAN WARSHIP",
     "SEA DRONES SINK THE MERKURY OFF LIBYA.", "ship"),
    ("COP31 ENDS WITH", "NO DEAL",
     "EU REJECTS A TEXT SILENT ON FOSSIL FUELS.", "globe"),
    ("HUANG BACK AT", "NVIDIA",
     "CEO BACK AFTER TRUMP PRESSES BOARD.", "chip"),
]

# (section, headline, brief) -- 29 stories in the body columns.
BODY = [
    ("UKRAINE WAR", "KYIV REGION HIT HARD",
     "RUSSIAN STRIKES KILL 15."),
    ("UKRAINE WAR", "NATO MEETS ON POLAND",
     "MISSILES ENTER POLAND."),
    ("UKRAINE WAR", "EU UNVEILS 22ND PACKAGE",
     "SWIFT CUT, SHIPS LISTED."),
    ("UKRAINE WAR", "SPARTA II HIT AT SEA",
     "FINLAND SUMMONS ENVOY."),
    ("UKRAINE WAR", "161 CLASHES IN A DAY",
     "7,475 DRONES IN ONE DAY."),
    ("UKRAINE WAR", "ZELENSKYY VOWS MORE",
     "MORE SEA STRIKES VOWED."),
    ("EUROPE", "BELGIUM GROUNDED",
     "429 FLIGHTS AXED."),
    ("EUROPE", "MARBLES DEMAND RENEWED",
     "ATHENS RENEWS CALL."),
    ("EUROPE", "FIRMS WARN BRUSSELS",
     "DON'T CUT FUNDS, FIRMS URGE."),
    ("EUROPE", "ORBAN TO VISIT",
     "HEADS FOR TRANSCARPATHIA."),
    ("EUROPE", "PROTESTS OVER PRICES",
     "MARCHES IN PORTUGAL, SPAIN."),
    ("MIDDLE EAST", "TANKERS HIT, IRAN SAYS",
     "IRAN CLAIM UNVERIFIED."),
    ("MIDDLE EAST", "US SANCTIONS TEHRAN",
     "SHADOW BANKING HIT."),
    ("MIDDLE EAST", "SINGER FLOGGED IN QOM",
     "74 LASHES EACH."),
    ("MIDDLE EAST", "GAZA TRUCK STRUCK",
     "THREE KILLED."),
    ("MIDDLE EAST", "SETTLER ARSON CONDEMNED",
     "EISENKOT DENOUNCES ARSON."),
    ("ASIA-PACIFIC", "24 DEAD IN FACTORY FIRE",
     "30 STILL MISSING."),
    ("ASIA-PACIFIC", "INDIA AIDS NEPAL",
     "$1.62BN FOR NEPAL."),
    ("ASIA-PACIFIC", "MINISTER QUITS IN SEOUL",
     "EXAM-CHEATING CHAOS."),
    ("ASIA-PACIFIC", "THAI TERM HALVED",
     "ROYAL-INSULT TERM CUT."),
    ("ASIA-PACIFIC", "BORDER TALKS IN ARUNACHAL",
     "INDIA, CHINA TALK."),
    ("AFRICA", "KENYA, CONGO RECONCILE",
     "FULL TIES RESTORED."),
    ("AFRICA", "24 KILLED IN S. SUDAN",
     "WARRAP STATE ATTACK."),
    ("AFRICA", "VILLA LOSES POWER",
     "WATER, POWER OUT."),
    ("AMERICAS", "AMTRAK DERAILS",
     "FOUR TAKEN TO HOSPITAL."),
    ("AMERICAS", "US WANTS CHAPO ISIDRO",
     "EXTRADITION SOUGHT."),
    ("AMERICAS", "DRONES HIT POLICE BASE",
     "60 HOMES HIT."),
    ("AMERICAS", "IOWA BLAST DELAYED",
     "ARMY DELAYS BLAST."),
    ("AMERICAS", "MEXICO, CHINA TALK TRADE",
     "TRADE GROUP AGREED."),
]

# Short wire items for the bottom strip, one line each (at most 20 chars).
WIRES = [
    "NASDAQ UP 6 PCT",
    "BITCOIN RECOVERS",
    "OPENAI SHIRUDO",
    "AI SAFETY LIMITS",
    "OIL AT 3-MO LOW",
    "ASIA STEADIES MKT",
    "DELTA FIXES GLITCH",
    "S. AFRICA AI PLAN",
]

# -------------------------------------------------------------- icons ----
def icon_ship(p, x, y, s=1):
    # A corvette at sea: hull, bow, mast, flag, waves.
    p.rect(x + 2 * s, y + 8 * s, 28 * s, 4 * s, INK)
    p.rect(x + 5 * s, y + 12 * s, 22 * s, 3 * s, INK)
    p.vline(x + 14 * s, y + 1 * s, y + 8 * s, INK, 2 * s)
    p.rect(x + 16 * s, y + 1 * s, 7 * s, 3 * s, INK)
    p.rect(x + 8 * s, y + 5 * s, 4 * s, 3 * s, INK)
    for i, wx in enumerate((0, 10, 20)):
        p.hline(x + wx * s, x + (wx + 6) * s, y + 17 * s + (i % 2) * 2 * s, INK)


def icon_globe(p, x, y, s=1):
    # A globe: solid ink disc with paper meridians, and a small
    # oxblood leaf for the climate talks.
    cx, cy, r = x + 14 * s, y + 10 * s, 9 * s
    for dy in range(-r, r + 1):
        span = int((r * r - dy * dy) ** 0.5)
        p.hline(cx - span, cx + span, cy + dy, INK)
    p.vline(cx, cy - r * s, cy + r * s, PAPER)
    p.hline(cx - r * s, cx + r * s, cy, PAPER)
    p.hline(cx - 6 * s, cx + 6 * s, cy - 5 * s, PAPER)
    p.hline(cx - 6 * s, cx + 6 * s, cy + 5 * s, PAPER)
    p.rect(x + 23 * s, y + 1 * s, 5 * s, 2 * s, ACCENT)
    p.rect(x + 25 * s, y + 3 * s, 2 * s, 4 * s, ACCENT)


def icon_chip(p, x, y, s=1):
    # A microchip: square body, inner die, pins on four sides.
    p.frame(x + 6 * s, y + 3 * s, x + 24 * s, y + 15 * s, INK, 2 * s)
    p.rect(x + 11 * s, y + 7 * s, 8 * s, 5 * s, INK)
    for i in range(4):
        px = x + (9 + i * 4) * s
        p.vline(px, y, y + 3 * s, INK)
        p.vline(px, y + 15 * s, y + 18 * s, INK)
    for i in range(3):
        py = y + (6 + i * 4) * s
        p.hline(x + 2 * s, x + 6 * s, py, INK)
        p.hline(x + 24 * s, x + 28 * s, py, INK)


ICONS = {"ship": icon_ship, "globe": icon_globe, "chip": icon_chip}


# ------------------------------------------------------------- layout ----
M = 26            # side margin inside the frame
COLW = 312        # body column width (18 px gutters)
COLX = [M, 356, 686]
LEAD_Y0 = 200
BODY_Y0 = 348
BODY_Y1 = 912


def section_header(p, x, y, w, title):
    # Rule, then the title, then a clear gap: the title is 20 px tall
    # starting at y + 4, so the next block must not start before y + 28.
    p.hline(x, x + w - 1, y + 1, INK)
    p.text_c(title, x + w // 2, y + 4, 2, INK)
    return y + 28


def story_block(p, x, y, headline, brief):
    # Headline bold at scale 2, then the brief one line below it, with
    # real leading between the two lines and a gap to the next story.
    p.text_bold(headline, x, y, 2, INK)
    y += 22
    for line in p.wrap(brief, 28):
        p.text(line, x, y, 2, INK)
        y += 24
    return y + 2


def draw_leads(p):
    for i, (h1, h2, brief, kind) in enumerate(LEADS):
        x = COLX[i]
        ICONS[kind](p, x + COLW // 2 - 14, LEAD_Y0 + 2)
        y = LEAD_Y0 + 26
        p.text_c_bold(h1, x + COLW // 2, y, 3, INK)
        p.text_c_bold(h2, x + COLW // 2, y + 32, 3, INK)
        y += 66
        for line in p.wrap(brief, 28):
            p.text_c(line, x + COLW // 2, y, 2, INK)
            y += 22
        if i < 2:
            p.vline(COLX[i] + COLW + 9, LEAD_Y0, LEAD_Y0 + 134, INK)


def draw_body(p):
    # Three columns: 10 / 10 / 9 stories, sections flowing across columns.
    groups = [BODY[0:10], BODY[10:20], BODY[20:29]]
    for col, stories in enumerate(groups):
        x = COLX[col]
        y = BODY_Y0
        cur_section = None
        for section, headline, brief in stories:
            if section != cur_section:
                y = section_header(p, x, y, COLW, section)
                cur_section = section
            y = story_block(p, x, y, headline, brief)
        if y > BODY_Y1:
            raise SystemExit("column %d overflows by %d px" % (col, y - BODY_Y1))


def draw_wires(p):
    y = section_header(p, M, 924, W - 2 * M,
                       "TECH AND WORLD - THE LATEST WIRES")
    cols = [WIRES[0:2], WIRES[2:4], WIRES[4:6], WIRES[6:8]]
    for col, items in enumerate(cols):
        x = M + col * 247
        yy = y
        for item in items:
            p.text(item, x, yy, 2, INK)
            yy += 20


def draw_page():
    p = Page()
    # Double frame, like a broadsheet's border.
    p.frame(12, 12, 1011, 1011, INK, 2)
    p.frame(19, 19, 1004, 1004, INK, 1)
    # Top meta line: day, volume, price (small folio type).
    p.text("MONDAY", M, 25, 1, INK)
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
    # Date line in oxblood, with flanking rules.
    p.hline(M, 300, 148, ACCENT, 2)
    p.hline(724, W - M - 1, 148, ACCENT, 2)
    p.text_c_bold("23 NOVEMBER 2026", W // 2, 128, 4, ACCENT)
    p.text_c("ALL THE NEWS OF THE DAY FROM EVERY CORNER OF THE EARTH",
             W // 2, 176, 1, INK)
    p.hline(M, W - M - 1, 192, INK, 2)
    # Leads, body, wires.
    draw_leads(p)
    p.hline(M, W - M - 1, 340, INK, 2)
    draw_body(p)
    p.hline(M, W - M - 1, 918, INK, 1)
    draw_wires(p)
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
