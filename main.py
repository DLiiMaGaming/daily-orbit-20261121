#!/usr/bin/env python3
"""Daily Orbit - 21 November 2026.

Draws a one-page newspaper front page summing up the world's news of
Saturday 21 November 2026 and writes it as entry.png.

Pure Python 3 standard library: a small raster canvas, a hand-drawn 5x7
bitmap font, shape helpers and a hand-rolled PNG encoder. No network, no
assets, no randomness, no clock: two runs write byte-identical output.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import math
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
CARD = (255, 253, 246)
INK = (26, 35, 64)
RED = (179, 39, 30)
BLUE = (32, 80, 140)
TEAL = (15, 118, 110)
AMBER = (180, 83, 9)
GREY = (91, 100, 114)
LIGHT_BLUE = (232, 238, 247)
LIGHT_RED = (247, 232, 229)
LIGHT_TEAL = (228, 242, 238)
WHITE = (255, 255, 255)
DARK = (18, 28, 52)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 bits, '1' = ink. Drawn from scratch here.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px per glyph cell)."""
    return len(text) * 6 * scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(' ')
    lines = []
    current = ''
    for word in words:
        trial = word if not current else current + ' ' + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.px = bytearray(background * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, length, color, thick=1):
        self.fill_rect(x, y, length, thick, color)

    def vline(self, x, y, length, color, thick=1):
        self.fill_rect(x, y, thick, length, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line with square brush of side `thick`."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def rect(self, x, y, w, h, color, thick=2):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def filled_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            half = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.hline(cx - half, yy, half * 2 + 1, color)

    def circle(self, cx, cy, r, color, thick=2):
        steps = max(24, r * 6)
        prev = None
        for s in range(steps + 1):
            ang = 2 * 3.141592653589793 * s / steps
            px = cx + int(r * 0.999 * math.cos(ang) + 0.5)
            py = cy + int(r * 0.999 * math.sin(ang) + 0.5)
            if prev is not None:
                self.line(prev[0], prev[1], px, py, color, thick)
            prev = (px, py)

    def filled_poly(self, points, color):
        """Scanline fill of a simple polygon."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for yy in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    t = (yy - y0) / (y1 - y0)
                    xs.append(int(x0 + t * (x1 - x0)))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.hline(xs[k], yy, xs[k + 1] - xs[k] + 1, color)

    def polyline(self, points, color, thick=2):
        for a, b in zip(points, points[1:]):
            self.line(a[0], a[1], b[0], b[1], color, thick)

    # ---------------------------------------------------------------- text
    def glyph(self, x, y, char, scale, color):
        rows = FONT.get(char.upper(), FONT['?'])
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == '1':
                    self.fill_rect(x + rx * scale, y + ry * scale,
                                   scale, scale, color)

    def text(self, x, y, string, scale, color):
        cx = x
        for ch in string:
            self.glyph(cx, y, ch, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, string, scale, color):
        self.text(cx - text_width(string, scale) // 2, y, string, scale, color)

    def paragraph(self, x, y, string, scale, color, max_width, leading=None):
        """Wrapped left-aligned paragraph; returns y after the last line."""
        gap = leading if leading is not None else 7 * scale + 4
        for line in wrap_text(string, scale, max_width):
            self.text(x, y, line, scale, color)
            y += gap
        return y


# -------------------------------------------------------------- PNG write
def _chunk(kind, data):
    out = struct.pack('>I', len(data)) + kind + data
    out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    ihdr = struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[yy * stride:(yy + 1) * stride]
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', ihdr)
    png += _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += _chunk(b'IEND', b'')
    return png

# ------------------------------------------------------------ pictograms
def draw_missile(cv, x, y, w, h):
    """Cruise missile arcing down over a ridge, with a compass star."""
    # sky glow
    cv.filled_circle(x + w // 2, y + h // 2, 62, (210, 222, 240))
    # ridge
    cv.filled_poly([(x, y + h), (x + 60, y + h - 42), (x + 130, y + h - 18),
                    (x + w, y + h - 34), (x + w, y + h)], (120, 130, 150))
    # missile body, nose up-right
    cv.line(x + 28, y + 78, x + 132, y + 22, INK, 16)
    cv.filled_poly([(x + 132, y + 22), (x + 158, y + 12), (x + 146, y + 34)],
                   RED)
    cv.filled_poly([(x + 34, y + 66), (x + 52, y + 88), (x + 66, y + 70)],
                   INK)
    cv.filled_poly([(x + 44, y + 84), (x + 30, y + 104), (x + 58, y + 94)],
                   INK)
    # exhaust flame + motion dashes
    cv.filled_poly([(x + 24, y + 82), (x + 2, y + 96), (x + 28, y + 98)],
                   (240, 140, 40))
    cv.hline(x + 8, y + 60, 26, GREY, 3)
    cv.hline(x + 96, y + 8, 26, GREY, 3)
    # four-point compass star (NATO)
    sx, sy = x + w - 52, y + h - 46
    cv.filled_poly([(sx, sy - 26), (sx + 7, sy - 7), (sx + 26, sy),
                    (sx + 7, sy + 7), (sx, sy + 26), (sx - 7, sy + 7),
                    (sx - 26, sy), (sx - 7, sy - 7)], BLUE)


def draw_chart(cv, x, y, w, h):
    """Falling market line with red arrowhead and bars."""
    cv.fill_rect(x, y, w, h, LIGHT_RED)
    # bars
    bars = [46, 58, 52, 40, 30, 18]
    bw = 16
    gap = (w - 24 - len(bars) * bw) // (len(bars) - 1)
    bx = x + 12
    for v in bars:
        cv.fill_rect(bx, y + h - 16 - v, bw, v, (190, 120, 112))
        bx += bw + gap
    # falling line
    pts = [(x + 14, y + 22), (x + 48, y + 34), (x + 82, y + 30),
           (x + 116, y + 58), (x + 150, y + 76), (x + 184, y + 104)]
    cv.polyline(pts, RED, 5)
    ex, ey = pts[-1]
    cv.filled_poly([(ex, ey + 12), (ex - 12, ey - 4), (ex + 2, ey - 12)], RED)
    cv.text(x + 12, y + 6, "-3.7%", 2, RED)


def draw_cyclone(cv, x, y, w, h):
    """Spiral storm over a coastline."""
    cx, cy = x + w // 2, y + h // 2 - 6
    cv.filled_circle(cx, cy, 58, (205, 225, 240))
    for r in (48, 38, 28, 18):
        cv.circle(cx, cy, r, BLUE, 4)
    cv.filled_circle(cx, cy, 10, BLUE)
    # spiral arms
    cv.line(cx - 44, cy - 30, cx - 10, cy - 6, TEAL, 5)
    cv.line(cx + 44, cy + 28, cx + 8, cy + 6, TEAL, 5)
    # coastline
    cv.filled_poly([(x, y + h), (x + w, y + h - 22), (x + w, y + h),
                    (x, y + h)], (120, 150, 120))


def draw_shield(cv, x, y, w, h):
    """Shield with a padlock: banks hit by a vendor breach."""
    cx = x + w // 2
    cv.filled_poly([(cx - 52, y + 8), (cx + 52, y + 8), (cx + 52, y + 62),
                    (cx, y + 108), (cx - 52, y + 62)], BLUE)
    cv.filled_poly([(cx - 40, y + 18), (cx + 40, y + 18), (cx + 40, y + 58),
                    (cx, y + 94), (cx - 40, y + 58)], (232, 238, 247))
    # padlock
    cv.fill_rect(cx - 20, y + 48, 40, 32, INK)
    cv.line(cx - 14, y + 48, cx - 14, y + 34, INK, 5)
    cv.line(cx + 14, y + 48, cx + 14, y + 34, INK, 5)
    cv.hline(cx - 14, y + 32, 28, INK, 5)
    cv.filled_circle(cx, y + 60, 5, CARD)
    cv.vline(cx, y + 62, 10, CARD, 4)
    # crack
    cv.line(cx - 40, y + 20, cx - 18, y + 40, RED, 3)
    cv.line(cx - 18, y + 40, cx - 30, y + 56, RED, 3)


def draw_flame(cv, x, y, w, h):
    """Flame over a gavel block: the arson verdict."""
    cx = x + w // 2
    cv.fill_rect(x, y + h - 18, w, 10, (150, 110, 70))
    # outer flame
    cv.filled_poly([(cx, y + 4), (cx + 34, y + 44), (cx + 40, y + 74),
                    (cx + 18, y + 100), (cx - 18, y + 100), (cx - 40, y + 74),
                    (cx - 34, y + 44)], (240, 120, 30))
    # inner flame
    cv.filled_poly([(cx, y + 38), (cx + 18, y + 62), (cx + 20, y + 82),
                    (cx, y + 96), (cx - 20, y + 82), (cx - 18, y + 62)],
                   (245, 200, 60))
    cv.filled_poly([(cx, y + 62), (cx + 9, y + 76), (cx, y + 90),
                    (cx - 9, y + 76)], (250, 240, 200))


def draw_globe(cv, x, y, w, h):
    """Globe with meridians and a leaf: climate talks."""
    cx, cy = x + w // 2, y + h // 2 - 4
    cv.filled_circle(cx, cy, 52, (200, 228, 210))
    cv.circle(cx, cy, 52, TEAL, 4)
    cv.circle(cx, cy, 52, TEAL, 4)
    # meridians: two upright ellipses inside the globe
    for a in (26, 48):
        pts = []
        for s in range(41):
            ang = 2 * math.pi * s / 40
            pts.append((cx + int(a * math.cos(ang)),
                        cy + int(52 * math.sin(ang))))
        cv.polyline(pts, TEAL, 2)
    # leaf
    cv.filled_poly([(cx + 30, cy - 44), (cx + 62, cy - 58), (cx + 56, cy - 26),
                    (cx + 28, cy - 20)], (40, 140, 70))
    cv.line(cx + 32, cy - 40, cx + 58, cy - 34, (20, 90, 50), 3)


# -------------------------------------------------------------- page parts
def kicker(cv, x, y, label, color):
    cv.text(x, y, label, 2, color)
    return y + 18


def headline(cv, x, y, title, scale, color, max_width):
    for line in wrap_text(title, scale, max_width):
        cv.text(x, y, line, scale, color)
        y += 7 * scale + 4
    return y


def panel(cv, x, y, w, h, bg):
    cv.fill_rect(x, y, w, h, bg)
    cv.rect(x, y, w, h, INK, 2)


def lead_story(cv, x, y, w, h):
    panel(cv, x, y, w, h, LIGHT_BLUE)
    ix, iy, iw, ih = x + 16, y + 16, 250, h - 32
    draw_missile(cv, ix, iy, iw, ih)
    tx = x + 286
    tw = w - 306
    yy = kicker(cv, tx, y + 18, "POLAND * NATO", RED)
    yy = headline(cv, tx, yy + 6, "MISSILES HIT POLAND", 5, INK, tw)
    yy = cv.paragraph(tx, yy + 8,
                      "Rutte in Warsaw as allies answer 'provocation'; "
                      "jets scrambled, no one hurt", 2, INK, tw)
    cv.text(tx, y + h - 34, "WARSAW * 21 NOV", 2, GREY)


def mid_story(cv, x, y, w, h, draw, tag, color, title, deck):
    panel(cv, x, y, w, h, CARD)
    draw(cv, x + 14, y + 14, 150, h - 28)
    tx = x + 180
    tw = w - 196
    yy = kicker(cv, tx, y + 16, tag, color)
    yy = headline(cv, tx, yy + 6, title, 3, INK, tw)
    cv.paragraph(tx, yy + 6, deck, 2, INK, tw)


def small_story(cv, x, y, w, h, draw, tag, color, title, deck):
    panel(cv, x, y, w, h, CARD)
    draw(cv, x + (w - 130) // 2, y + 8, 130, 104)
    yy = kicker(cv, x + 16, y + 118, tag, color)
    yy = headline(cv, x + 16, yy + 4, title, 3, INK, w - 32)
    cv.paragraph(x + 16, yy + 4, deck, 2, INK, w - 32)


# ------------------------------------------------------------------ page
def build_page():
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    mx = 28  # margin
    inner = WIDTH - 2 * mx

    # masthead
    cv.text_center(WIDTH // 2, 34, "THE DAILY ORBIT", 7, INK)
    cv.hline(mx, 96, inner, INK, 3)
    cv.hline(mx, 102, inner, INK, 1)
    cv.text_center(WIDTH // 2, 114, "SATURDAY 21 NOVEMBER 2026", 4, RED)
    cv.text_center(WIDTH // 2, 148,
                   "THE WORLD IN ONE PAGE - MAKE.FUN NEWS-IMAGE-20261121",
                   2, GREY)

    # lead story: Poland / NATO
    lead_story(cv, mx, 176, inner, 250)

    # middle row: markets + cyclone
    gap = 16
    mid_w = (inner - gap) // 2
    mid_story(cv, mx, 442, mid_w, 216, draw_chart, "MARKETS * NEW YORK",
              RED, "WALL ST SLUMPS",
              "S&P 500 slides into correction as AI shares sell off")
    mid_story(cv, mx + mid_w + gap, 442, mid_w, 216, draw_cyclone,
              "WEATHER * INDIA", BLUE, "AKVAN LANDFALL",
              "Cyclone crosses Odisha coast; thousands evacuated")

    # bottom row: cyber, palisades, COP31
    sm_w = (inner - 2 * gap) // 3
    small_story(cv, mx, 674, sm_w, 216, draw_shield, "CYBER * GLOBAL",
                BLUE, "BANKS HACKED",
                "JPMorgan, Visa, Mastercard breached")
    small_story(cv, mx + sm_w + gap, 674, sm_w, 216, draw_flame,
                "JUSTICE * LOS ANGELES", RED, "ARSONIST GUILTY",
                "Rinderknecht convicted; 12 died in 2025 fire")
    small_story(cv, mx + 2 * (sm_w + gap), 674, sm_w, 216, draw_globe,
                "CLIMATE * TURKEY", TEAL, "COP31: ENDGAME",
                "Climate talks in final stage")

    # ticker
    ty = 906
    cv.fill_rect(mx, ty, inner, 90, DARK)
    cv.text(mx + 16, ty + 12, "ALSO TODAY:", 2, (245, 200, 60))
    cv.text(mx + 16, ty + 34,
            "UFO FILES DECLASSIFIED - MAMDANI: CLOSE RIKERS BY 2032",
            2, WHITE)
    cv.text(mx + 16, ty + 58,
            "FRENCH POLICE SENTENCED - INDIA LEAD NZ TEST - ANTHROPIC MATHS CLAIM",
            2, WHITE)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build_page())
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
