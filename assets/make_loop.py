"""Render assets/night-terminal.gif: an original 6 s seamless pixel-art loop.

A figure in a hoodie codes at night: rain on the window, scrolling code,
blinking cursor, steam from a mug. Every motion has a period dividing
FRAMES, so frame FRAMES equals frame 0 and the GIF loops without a seam.

    python assets/make_loop.py      # needs only Pillow
"""

import math
import pathlib

from PIL import Image, ImageDraw

WIDTH, HEIGHT = 240, 96
SCALE = 2
FRAMES = 75
FRAME_MS = 80

BG = (11, 18, 32)
WALL = (16, 26, 46)
WINDOW_SKY = (8, 14, 28)
FRAME_DARK = (30, 45, 72)
RAIN = (56, 98, 150)
CITY = (40, 70, 110)
CITY_LIT = (125, 180, 230)
DESK = (24, 36, 60)
SCREEN = (7, 16, 30)
CODE = (56, 189, 248)
CODE_DIM = (37, 99, 150)
GLOW = (60, 110, 160)
HOODIE = (28, 42, 68)
HOODIE_LIT = (46, 78, 120)
HAIR = (14, 20, 34)
SKIN = (176, 160, 150)
MUG = (70, 90, 120)
STEAM = (90, 120, 160)

WINDOW = (14, 10, 74, 58)
MONITOR = (128, 22, 206, 70)
CODE_LINES = [(4, 38), (8, 30), (8, 46), (4, 22), (12, 34)]
LINE_PERIOD = FRAMES // len(CODE_LINES)
RAIN_DROPS = [(17, 3), (23, 31), (30, 12), (37, 40), (44, 7), (51, 26), (58, 18), (65, 35), (70, 2)]
CITY_DOTS = [(20, 50, 0), (27, 47, 25), (35, 52, 0), (41, 45, 15), (49, 49, 0), (56, 46, 25), (63, 51, 15)]


def draw_window(d: ImageDraw.ImageDraw, t: int) -> None:
    x0, y0, x1, y1 = WINDOW
    d.rectangle(WINDOW, fill=WINDOW_SKY, outline=FRAME_DARK)
    d.line([(x0 + 30, y0), (x0 + 30, y1)], fill=FRAME_DARK)
    for i, (cx, cy, period) in enumerate(CITY_DOTS):
        lit = period == 0 or (t + i * 7) % period < period // 2
        d.point((cx, cy), fill=CITY_LIT if lit else CITY)
    span = y1 - y0 - 2
    for x, phase in RAIN_DROPS:
        # two window heights per loop: integer wrap at t == FRAMES
        y = y0 + 1 + (phase + t * 2 * span // FRAMES) % span
        d.line([(x, y), (x, min(y + 3, y1 - 1))], fill=RAIN)


def draw_monitor(d: ImageDraw.ImageDraw, t: int) -> None:
    x0, y0, x1, y1 = MONITOR
    d.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), fill=FRAME_DARK)
    d.rectangle(MONITOR, fill=SCREEN)
    d.rectangle((x0 + 30, y1 + 2, x1 - 30, y1 + 6), fill=FRAME_DARK)
    shift = t // LINE_PERIOD
    typed = (t % LINE_PERIOD + 1) / LINE_PERIOD
    rows = len(CODE_LINES)
    for row in range(rows):
        indent, length = CODE_LINES[(row + shift) % rows]
        if row == rows - 1:
            length = max(2, int(length * typed))
        y = y0 + 6 + row * 9
        d.line([(x0 + 5 + indent, y), (x0 + 5 + indent + length, y)], fill=CODE if row == rows - 1 else CODE_DIM, width=2)
        if row == rows - 1 and t % 15 < 8:
            d.rectangle((x0 + 7 + indent + length, y - 2, x0 + 9 + indent + length, y + 2), fill=CODE)


def draw_figure(d: ImageDraw.ImageDraw, t: int) -> None:
    bob = round(math.sin(2 * math.pi * t / FRAMES) * 0.8)
    type_lift = 1 if t % 5 < 2 else 0
    d.rounded_rectangle((88, 52 + bob, 122, 90), radius=8, fill=HOODIE)
    d.line([(121, 58 + bob), (121, 88)], fill=HOODIE_LIT, width=2)
    d.line([(116, 66 + bob), (134, 74 - type_lift)], fill=HOODIE_LIT, width=4)
    d.ellipse((92, 30 + bob, 116, 56 + bob), fill=HAIR)
    d.polygon([(93, 38 + bob), (88, 30 + bob), (99, 33 + bob)], fill=HAIR)
    d.polygon([(101, 31 + bob), (104, 23 + bob), (109, 31 + bob)], fill=HAIR)
    d.polygon([(110, 34 + bob), (118, 28 + bob), (115, 39 + bob)], fill=HAIR)
    d.rectangle((113, 42 + bob, 117, 50 + bob), fill=SKIN)
    d.point((117, 44 + bob), fill=GLOW)


def draw_desk(d: ImageDraw.ImageDraw, t: int) -> None:
    d.rectangle((80, 76, 236, 80), fill=DESK)
    d.rectangle((136, 73, 186, 76), fill=FRAME_DARK)
    d.rectangle((212, 66, 220, 76), fill=MUG)
    d.arc((218, 68, 224, 74), 270, 90, fill=MUG)
    for k in range(3):
        rise = (t * 3 // 5 + k * 5) % 15
        x = 215 + round(math.sin(2 * math.pi * (t + k * 25) / FRAMES) * 1.5)
        d.point((x, 64 - rise), fill=STEAM)


def render_frame(t: int) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, WIDTH, 80), fill=WALL)
    draw_window(d, t)
    draw_monitor(d, t)
    draw_desk(d, t)
    draw_figure(d, t)
    return img.resize((WIDTH * SCALE, HEIGHT * SCALE), Image.NEAREST)


def main() -> None:
    out = pathlib.Path(__file__).resolve().parent / "night-terminal.gif"
    frames = [render_frame(t) for t in range(FRAMES)]
    assert render_frame(FRAMES).tobytes() == frames[0].tobytes(), "loop seam"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=FRAME_MS, loop=0, optimize=True, disposal=1)
    print("%s %d frames %d bytes" % (out.name, FRAMES, out.stat().st_size))


if __name__ == "__main__":
    main()
