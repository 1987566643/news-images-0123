#!/usr/bin/env python3
"""The World in One Day -- 23 November 2026.

An old-fashioned broadsheet front page, drawn by hand in pure Python 3
standard library: a hand-written PNG encoder, an embedded 5x7 bitmap
font, and a vintage newspaper layout -- large serif-style masthead with
ornamental rules, black ink on cream paper, thin column rules, small-caps
section headers, dense justified columns, a price line and a weather line.

Writes the image to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
Runs with no network. Deterministic: two runs write identical bytes.

Entry for make.fun competition news-image-20261123.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, one glyph per character: 7 rows of 5 bits ("1" = ink).
# Authored here from scratch; all page text is set in capitals.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}

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
    def text_w(self, s, scale, gap=1):
        return len(s) * (5 * scale + gap) - gap if s else 0

    def text(self, s, x, y, scale, color, gap=1):
        """Draw text; returns the x just past the last glyph."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                raise ValueError("no glyph for %r" % ch)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 5 * scale + gap
        return cx

    def text_c(self, s, cx, y, scale, color, gap=1):
        """Draw text centred on cx."""
        self.text(s, cx - self.text_w(s, scale, gap) // 2, y, scale, color, gap)

    def text_bold(self, s, x, y, scale, color, gap=1):
        """Draw text twice, 1 px apart, for a bold headline face."""
        self.text(s, x, y, scale, color, gap)
        self.text(s, x + 1, y, scale, color, gap)

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
# were dropped as unverified. Headlines fit one 26-character line;
# briefs fit two 26-character lines at scale 2.

LEADS = [
    ("UKRAINE SINKS", "RUSSIAN WARSHIP",
     "SEA DRONES SINK THE MERKURY OFF LIBYA.", "ship"),
    ("COP31 ENDS WITH", "NO DEAL",
     "EU REJECTS A TEXT SILENT ON FOSSIL FUELS.", "globe"),
    ("HUANG BACK AT", "NVIDIA",
     "CEO BACK AFTER TRUMP PRESSES BOARD.", "chip"),
]

# (section, headline, brief)
BODY = [
    ("UKRAINE WAR", "KYIV REGION HIT HARD",
     "RUSSIAN STRIKES KILL 15 IN KYIV REGION."),
    ("UKRAINE WAR", "NATO MEETS ON POLAND",
     "EMERGENCY TALKS AS MISSILES ENTER POLAND."),
    ("UKRAINE WAR", "EU UNVEILS 22ND PACKAGE",
     "60 BANKS OFF SWIFT; 70 SHIPS LISTED; CRYPTO HIT."),
    ("UKRAINE WAR", "SPARTA II HIT AT SEA",
     "RUSSIAN CARGO SHIP HIT; FINLAND SUMMONS ENVOY."),
    ("UKRAINE WAR", "161 CLASHES IN A DAY",
     "7,475 KAMIKAZE DRONES IN ONE DAY, KYIV SAYS."),
    ("UKRAINE WAR", "ZELENSKYY VOWS MORE",
     "MORE SEA STRIKES VOWED AS NEW ATTACKS LOOM."),
    ("EUROPE", "BELGIUM GROUNDED",
     "429 FLIGHTS AXED AS STRIKE HALTS BRUSSELS AIRPORTS."),
    ("EUROPE", "MARBLES DEMAND RENEWED",
     "ATHENS REOPENS MUSEUM, RENEWS CALL FOR MARBLES."),
    ("EUROPE", "FIRMS WARN BRUSSELS",
     "FIRMS URGE THE EU NOT TO CUT COMPETITIVENESS FUNDS."),
    ("EUROPE", "ORBAN TO VISIT",
     "HUNGARY'S PM HEADS FOR TRANSCARPATHIA."),
    ("EUROPE", "PROTESTS OVER PRICES",
     "PRICE MARCHES SPREAD IN PORTUGAL, SPAIN."),
    ("MIDDLE EAST", "TANKERS HIT, IRAN SAYS",
     "IRAN CLAIMS THREE TANKERS HIT MINES; UNVERIFIED."),
    ("MIDDLE EAST", "US SANCTIONS TEHRAN",
     "TREASURY TARGETS IRAN'S SHADOW BANKING NETWORK."),
    ("MIDDLE EAST", "SINGER FLOGGED IN QOM",
     "SINGER, FOUR AIDES GET 74 LASHES EACH IN QOM."),
    ("MIDDLE EAST", "GAZA TRUCK STRUCK",
     "ISRAELI STRIKE KILLS THREE, WITNESSES SAY."),
    ("MIDDLE EAST", "SETTLER ARSON CONDEMNED",
     "EISENKOT DENOUNCES SETTLER ARSON IN THE WEST BANK."),
    ("ASIA-PACIFIC", "24 DEAD IN FACTORY FIRE",
     "24 DEAD AT A CANDY PLANT; 30 STILL MISSING."),
    ("ASIA-PACIFIC", "INDIA AIDS NEPAL",
     "NEW DELHI OFFERS $1.62BN TO FLOOD-HIT NEPAL."),
    ("ASIA-PACIFIC", "MINISTER QUITS IN SEOUL",
     "EDUCATION MINISTER QUITS OVER EXAM-CHEATING CHAOS."),
    ("ASIA-PACIFIC", "THAI TERM HALVED",
     "COURT HALVES A LAWMAKER'S ROYAL-INSULT TERM."),
    ("ASIA-PACIFIC", "BORDER TALKS IN ARUNACHAL",
     "INDIA, CHINA HOLD BORDER TALKS TO EASE TENSIONS."),
    ("AFRICA", "KENYA, CONGO RECONCILE",
     "KENYA AND CONGO TO RESTORE FULL DIPLOMATIC TIES."),
    ("AFRICA", "24 KILLED IN S. SUDAN",
     "AT LEAST 24 CIVILIANS KILLED IN WARRAP STATE."),
    ("AFRICA", "VILLA LOSES POWER",
     "VILLA IN ABUJA LOSES WATER AND POWER."),
    ("AMERICAS", "AMTRAK DERAILS",
     "TRAIN HITS A STUCK TRUCK; FOUR TAKEN TO HOSPITAL."),
    ("AMERICAS", "US WANTS CHAPO ISIDRO",
     "US SEEKS EXTRADITION OF THE CAPTURED CARTEL BOSS."),
    ("AMERICAS", "DRONES HIT POLICE BASE",
     "DRONES HIT A BASE IN CUCUTA; 60 HOMES HIT."),
    ("AMERICAS", "IOWA BLAST DELAYED",
     "ARMY DELAYS LEAD-EXPLOSIVE BLAST AFTER OUTCRY."),
    ("AMERICAS", "MEXICO, CHINA TALK TRADE",
     "MEXICO AND CHINA AGREE A TRADE WORKING GROUP."),
]

# Short wire items for the bottom strip, one line each.
WIRES = [
    "NASDAQ UP 6 PCT IN AI RALLY",
    "BITCOIN DIPS THEN RECOVERS",
    "OPENAI LAUNCHES SHIRUDO",
    "AI LABS URGED TO SET LIMIT",
    "OIL SLIDES TO 3-MONTH LOW",
    "ASIAN STATES STEADY MARKET",
    "DELTA FIXES TRAVEL GLITCH",
    "S. AFRICA UNVEILS AI PLAN",
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
COLW = 316        # column width
COLX = [M, 354, 682]
LEAD_Y0, LEAD_Y1 = 202, 300
BODY_Y0, BODY_Y1 = 314, 836


def section_header(p, x, y, w, title):
    p.hline(x, x + w - 1, y + 1, INK)
    p.text_c(title, x + w // 2, y + 4, 2, INK)
    return y + 20


def story_block(p, x, y, headline, brief):
    p.text_bold(headline, x, y, 2, INK)
    y += 15
    for line in p.wrap(brief, 26):
        p.text(line, x, y, 2, INK)
        y += 15
    return y + 1


def draw_leads(p):
    for i, (h1, h2, brief, kind) in enumerate(LEADS):
        x = COLX[i]
        ICONS[kind](p, x + COLW // 2 - 16, LEAD_Y0 + 2)
        y = LEAD_Y0 + 24
        p.text_c(h1, x + COLW // 2, y, 3, INK)
        p.text_c(h2, x + COLW // 2, y + 21, 3, INK)
        y += 45
        for line in p.wrap(brief, 26):
            p.text_c(line, x + COLW // 2, y, 2, INK)
            y += 15
        if i < 2:
            p.vline(COLX[i] + COLW + 6, LEAD_Y0, LEAD_Y1, INK)


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
    y = section_header(p, M, 852, W - 2 * M, "TECH AND WORLD - THE LATEST WIRES")
    cols = [WIRES[0:3], WIRES[3:6], WIRES[6:8]]
    for col, items in enumerate(cols):
        x = COLX[col]
        yy = y
        for item in items:
            p.text(item, x, yy, 2, INK)
            yy += 20


def draw_page():
    p = Page()
    # Double frame, like a broadsheet's border.
    p.frame(12, 12, 1011, 1011, INK, 2)
    p.frame(19, 19, 1004, 1004, INK, 1)
    # Top meta line: day, volume, price.
    p.text("MONDAY", M, 30, 2, INK)
    p.text_c("VOL. I - NO. 327", W // 2, 30, 2, INK)
    p.text("PRICE ONE CENT", W - M - p.text_w("PRICE ONE CENT", 2), 30, 2, INK)
    # Masthead.
    p.text_c("THE WORLD IN ONE DAY", W // 2, 54, 8, INK)
    # Ornamental rule with diamonds.
    p.hline(M, W - M - 1, 122, INK, 2)
    p.hline(M, W - M - 1, 128, INK, 1)
    for cx in (300, 512, 724):
        p.diamond(cx, 125, 6, INK)
    # Date line in oxblood, with flanking rules.
    p.hline(M, 300, 152, ACCENT, 2)
    p.hline(724, W - M - 1, 152, ACCENT, 2)
    p.text_c("23 NOVEMBER 2026", W // 2, 140, 4, ACCENT)
    p.text_c("ALL THE NEWS OF THE DAY FROM EVERY CORNER OF THE EARTH",
             W // 2, 174, 2, INK)
    p.hline(M, W - M - 1, 194, INK, 2)
    # Leads, body, wires.
    draw_leads(p)
    p.hline(M, W - M - 1, 306, INK, 2)
    draw_body(p)
    p.hline(M, W - M - 1, 844, INK, 1)
    draw_wires(p)
    # Footer rule and line.
    p.hline(M, W - M - 1, 956, INK, 1)
    p.text_c("THE WORLD IN ONE DAY - 23 NOVEMBER 2026 - ALL THE NEWS IN ONE PAGE",
             W // 2, 962, 2, INK)
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
