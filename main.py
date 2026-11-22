#!/usr/bin/env python3
"""news-image-20261122: sum up Sunday 22 November 2026 in one image.

Draws a newspaper front page (1024x1024 PNG) with seven verified stories
from 22 November 2026. Pure Python 3.13 standard library: own PNG encoder
and own 5x7 bitmap font. No network, no randomness, no clock: running the
program twice writes byte-identical files.
"""
import os
import struct
import zlib
from binascii import crc32

W, H = 1024, 1024

# ---- palette (warm newspaper paper, dark ink, red + blue accents) ----
PAPER = (245, 240, 225)
PAPER2 = (255, 252, 240)
INK = (26, 26, 46)
RED = (192, 57, 43)
BLUE = (31, 78, 121)
GOLD = (176, 124, 18)
GREY = (120, 116, 104)
WHITE = (255, 255, 255)


def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", crc32(ctype + data) & 0xFFFFFFFF)
    return out


def encode_png(rgb, w, h):
    """Encode a flat RGB bytes buffer as a PNG (filter 0 per row)."""
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.fill(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, filled=True):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            if filled:
                self.fill(cx - dx, cy + dy, 2 * dx + 1, 1, c)
            else:
                self.set(cx - dx, cy + dy, c)
                self.set(cx + dx, cy + dy, c)

    def ring(self, cx, cy, r, c, t=3):
        for k in range(t):
            rr = r - k
            for a in range(360):
                import math
                x = cx + int(rr * math.cos(math.radians(a)))
                y = cy + int(rr * math.sin(math.radians(a)))
                self.set(x, y, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        # filled triangle via scanline
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / max(1, by - ay)
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / max(1, cy - by)
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / max(1, cy - ay)
            xb = ax + (cx - ax) * t2
            x0s, x1s = int(min(xa, xb)), int(max(xa, xb))
            self.fill(x0s, y, x1s - x0s + 1, 1, c)


# ---- 5x7 bitmap font (uppercase only; each glyph = 7 rows of 5 bits) ----
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
}

FONT.update({
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "-": (0, 0, 0, 0x1F, 0, 0, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    "*": (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
})


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    """Draw uppercase text; unknown chars become '?'."""
    s = s.upper()
    for ci, ch in enumerate(s):
        glyph = FONT.get(ch, FONT["?"])
        ox = x + ci * 6 * scale
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.fill(ox + col * scale, y + row * scale,
                            scale, scale, color)
    return x + text_w(s, scale)


def draw_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, max_chars):
    """Word-wrap to lines of at most max_chars characters."""
    words, lines, cur = s.upper().split(), [], ""
    for w in words:
        nxt = (cur + " " + w).strip() if cur else w
        if len(nxt) <= max_chars:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(cv, x, y, s, scale, color, max_chars, lh=None):
    """Draw wrapped paragraph; returns y after the last line."""
    if lh is None:
        lh = 9 * scale
    for line in wrap(s, max_chars):
        draw_text(cv, x, y, line, scale, color)
        y += lh
    return y


# ---- pictograms (each drawn in a ~120x120 box, origin = top-left) ----
def pic_handcuffs(cv, x, y, c):
    # two rings joined by a short chain bar
    cv.ring(x + 32, y + 60, 24, c, 5)
    cv.ring(x + 88, y + 60, 24, c, 5)
    cv.line(x + 52, y + 48, x + 68, y + 48, c, 5)
    cv.line(x + 52, y + 72, x + 68, y + 72, c, 5)
    cv.circle(x + 32, y + 60, 4, c)
    cv.circle(x + 88, y + 60, 4, c)


def pic_screen_crack(cv, x, y, c):
    # monitor with a zigzag crack and warning triangle
    cv.rect(x + 14, y + 22, 92, 62, c, 4)
    cv.line(x + 40, y + 22, x + 52, y + 44, c, 4)
    cv.line(x + 52, y + 44, x + 44, y + 62, c, 4)
    cv.line(x + 44, y + 62, x + 58, y + 84, c, 4)
    cv.line(x + 60, y + 84, x + 78, y + 40, c, 4)
    cv.line(x + 46, y + 84, x + 74, y + 84, c, 5)
    cv.line(x + 60, y + 84, x + 60, y + 100, c, 5)
    cv.fill(x + 46, y + 100, 28, 5, c)


def pic_parliament(cv, x, y, c):
    # pediment + columns + steps
    cv.triangle(x + 60, y + 14, x + 16, y + 44, x + 104, y + 44, c)
    cv.fill(x + 20, y + 50, 10, 40, c)
    cv.fill(x + 44, y + 50, 10, 40, c)
    cv.fill(x + 66, y + 50, 10, 40, c)
    cv.fill(x + 90, y + 50, 10, 40, c)
    cv.fill(x + 12, y + 94, 96, 5, c)
    cv.fill(x + 8, y + 102, 104, 5, c)


def pic_aid_box(cv, x, y, c):
    # aid crate with a cross, water drop above
    cv.rect(x + 22, y + 44, 76, 60, c, 4)
    cv.fill(x + 52, y + 56, 16, 36, c)
    cv.fill(x + 36, y + 66, 48, 14, c)
    cv.circle(x + 60, y + 26, 12, c)
    cv.triangle(x + 60, y + 6, x + 48, y + 26, x + 72, y + 26, c)


def pic_megaphone(cv, x, y, c):
    # megaphone cone + handle
    cv.triangle(x + 96, y + 20, x + 96, y + 84, x + 30, y + 52, c)
    cv.fill(x + 14, y + 44, 18, 18, c)
    cv.line(x + 96, y + 20, x + 96, y + 84, c, 5)
    cv.line(x + 40, y + 62, x + 30, y + 96, c, 7)
    cv.line(x + 30, y + 96, x + 58, y + 96, c, 5)
    # sound arcs
    cv.line(x + 104, y + 30, x + 112, y + 52, c, 3)
    cv.line(x + 104, y + 74, x + 112, y + 52, c, 3)


def pic_quake_house(cv, x, y, c):
    # house with a zigzag crack, wavy ground
    cv.triangle(x + 60, y + 12, x + 16, y + 46, x + 104, y + 46, c)
    cv.rect(x + 24, y + 46, 72, 48, c, 4)
    cv.line(x + 62, y + 12, x + 54, y + 34, c, 4)
    cv.line(x + 54, y + 34, x + 66, y + 52, c, 4)
    cv.line(x + 66, y + 52, x + 56, y + 74, c, 4)
    cv.line(x + 56, y + 74, x + 64, y + 94, c, 4)
    cv.line(x + 10, y + 102, x + 34, y + 94, c, 4)
    cv.line(x + 34, y + 94, x + 58, y + 102, c, 4)
    cv.line(x + 58, y + 102, x + 82, y + 94, c, 4)
    cv.line(x + 82, y + 94, x + 110, y + 102, c, 4)


def pic_health_cross(cv, x, y, c):
    # medical cross inside a ring, small virus spikes
    cv.ring(x + 60, y + 58, 44, c, 5)
    cv.fill(x + 52, y + 34, 16, 48, c)
    cv.fill(x + 36, y + 50, 48, 16, c)
    for (dx, dy) in ((-34, -34), (34, -34), (-34, 34), (34, 34)):
        cv.circle(x + 60 + dx, y + 58 + dy, 4, c)


# ---- layout: a newspaper front page, 1024x1024 ----
STORIES = [
    # (kicker, headline, sub, pictogram)
    ("UNITED STATES", "FBI PROBES HACK OF ITS NATIONAL CRIME DATABASE",
     "NCIC CRIME DATABASE PROBED", pic_screen_crack),
    ("ISRAEL", "EISENKOT INVITES LIKUD TO COALITION TALKS",
     "TALKS BEGIN ON SUNDAY", pic_parliament),
    ("GAZA", "FOUR NATIONS URGE ISRAEL TO LET AID REACH FLOODED GAZA",
     "AUSTRALIA, CANADA, ITALY, UK", pic_aid_box),
    ("FRANCE", "COST-OF-LIVING PROTESTS ROLL INTO ANOTHER WEEKEND",
     "FOURTH WEEKEND OF MARCHES", pic_megaphone),
    ("PERU", "152 HOMES UNINHABITABLE AFTER PERU QUAKE",
     "LIMA RESIDENTS FLED", pic_quake_house),
    ("AFRICA", "LAST EBOLA PATIENT GOES HOME AS DRC TOLL PASSES 5,300",
     "KENYA DISCHARGES LAST CASE", pic_health_cross),
]


def build():
    cv = Canvas(W, H, PAPER)
    cv.rect(10, 10, 1004, 1004, INK, 3)

    # masthead
    cv.fill(24, 26, 976, 6, RED)
    draw_centered(cv, 512, 44, "THE WORLD IN ONE DAY", 4, INK)
    draw_centered(cv, 512, 88, "SUNDAY 22 NOVEMBER 2026", 3, RED)
    draw_centered(cv, 512, 128, "SEVEN STORIES FROM FIVE CONTINENTS",
                  1, GREY)
    cv.fill(24, 148, 976, 2, INK)

    # hero: Mexico, cartel boss arrested
    draw_text(cv, 48, 164, "TOP STORY - MEXICO", 2, RED)
    cv.rect(48, 190, 180, 180, INK, 3)
    cv.fill(52, 194, 172, 172, PAPER2)
    pic_handcuffs(cv, 78, 226, INK)
    draw_text(cv, 252, 200, "'EL CHAPO ISIDRO'", 3, INK)
    draw_text(cv, 252, 230, "ARRESTED IN SINALOA", 3, INK)
    draw_text(cv, 252, 260, "FBI MOST WANTED", 3, RED)
    draw_text(cv, 252, 306, "MEXICAN ARMY STORMED HIS HIDEOUT", 2, INK)
    draw_text(cv, 252, 332, "VIOLENCE FLARES AFTER THE ARREST", 2, GREY)
    cv.fill(24, 388, 976, 2, INK)

    # grid: 2 columns x 3 rows
    for i, (kicker, headline, sub, pic) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = 24 + col * 496
        y0 = 404 + row * 182
        if i % 2 == 0:
            cv.fill(x0, y0, 480, 172, PAPER2)
        cv.rect(x0, y0, 480, 172, GREY, 1)
        cv.rect(x0 + 10, y0 + 24, 124, 124, INK, 2)
        cv.fill(x0 + 12, y0 + 26, 120, 120, PAPER)
        pic(cv, x0 + 8, y0 + 22, INK)
        draw_text(cv, x0 + 150, y0 + 32, kicker, 2, RED)
        y_end = para(cv, x0 + 150, y0 + 58, headline, 2, INK, 26, 18)
        draw_text(cv, x0 + 150, y_end + 8, sub, 1, GREY)

    # footer
    cv.fill(24, 952, 976, 2, INK)
    draw_centered(cv, 512, 966,
                  "SUNDAY 22 NOVEMBER 2026 - SEVEN STORIES - FIVE CONTINENTS",
                  2, INK)
    cv.fill(24, 994, 976, 4, RED)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    data = encode_png(bytes(cv.px), W, H)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
