"""Draws the skill-tree icons (32x32 white pixel glyphs with a dark outline, a touch of colour here
and there) into one strip, pictures/icons/tree.png, in the order of ORDER below (the game reads
them by that index). Run once; the game just shows the PNG."""
from PIL import Image, ImageDraw
import math

S = 32
OUT = (14, 18, 20, 255)
W1 = (238, 244, 244, 255)    # white
W2 = (176, 188, 192, 255)    # its shade
RED = (232, 60, 60, 255)
BLUE = (90, 170, 255, 255)
GOLD = (250, 200, 70, 255)
GREEN = (100, 220, 130, 255)

ORDER = ["sharp", "cleave", "flurry", "execute", "bloodlust", "berserker",
         "siphon", "efficiency", "spellpower", "surge", "overflow", "archmage",
         "tough", "ironskin", "quickfeet", "regen", "treasure", "undying"]


def canvas():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def outlined(draw_fn):
    shape = canvas()
    draw_fn(ImageDraw.Draw(shape))
    px = shape.load()
    o = canvas()
    op = o.load()
    for y in range(S):
        for x in range(S):
            if px[x, y][3]:
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < S and 0 <= ny < S and not px[nx, ny][3]:
                        op[nx, ny] = OUT
    o.alpha_composite(shape)
    return o


def sword(d, x0=5, y0=27, x1=26, y1=6, w=3):
    d.line([(x0 + 4, y0 - 4), (x1, y1)], fill=W1, width=w)
    d.line([(x0 + 5, y0 - 3), (x1, y1 + 1)], fill=W2, width=1)
    d.line([(x0 + 1, y0 - 9), (x0 + 9, y0 - 1)], fill=W2, width=3)     # guard
    d.line([(x0, y0), (x0 + 4, y0 - 4)], fill=W2, width=3)              # grip


def heart(d, cx, cy, r, fill):
    d.ellipse([cx - 2 * r, cy - r * 1.4, cx, cy + r * 0.6], fill=fill)
    d.ellipse([cx, cy - r * 1.4, cx + 2 * r, cy + r * 0.6], fill=fill)
    d.polygon([(cx - 2 * r + 0.5, cy - 0.2), (cx + 2 * r - 0.5, cy - 0.2), (cx, cy + 2 * r)], fill=fill)


def drop(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    d.polygon([(cx - r + 1, cy - 2), (cx + r - 1, cy - 2), (cx, cy - r * 2.3)], fill=fill)


ICONS = {}


def icon(fn):
    ICONS[fn.__name__] = fn
    return fn


@icon
def sharp(d):
    sword(d)
    d.line([(20, 6), (26, 6)], fill=W1)
    d.point([(27, 3), (29, 5), (24, 2)], fill=W1)


@icon
def cleave(d):
    d.arc([2, 2, 30, 30], 200, 340, fill=W1, width=4)
    d.arc([6, 6, 26, 26], 210, 330, fill=W2, width=2)
    sword(d, 8, 28, 20, 14, 3)


@icon
def flurry(d):
    for i, c in enumerate((W1, W2, W1)):
        o = i * 7
        d.line([(3 + o, 26), (16 + o, 5)], fill=c, width=3)


@icon
def execute(d):
    d.ellipse([6, 3, 26, 22], fill=W1)
    d.rectangle([10, 18, 22, 27], fill=W1)
    d.ellipse([9, 10, 14, 15], fill=OUT)
    d.ellipse([18, 10, 23, 15], fill=OUT)
    d.polygon([(16, 16), (14, 19), (18, 19)], fill=OUT)
    for x in (12, 15, 18, 21):
        d.line([(x, 23), (x, 27)], fill=OUT)


@icon
def bloodlust(d):
    drop(d, 15, 20, 8, RED)
    d.ellipse([11, 16, 14, 19], fill=(255, 150, 150, 255))
    d.rectangle([23, 4, 25, 12], fill=W1)
    d.rectangle([20, 7, 28, 9], fill=W1)


@icon
def berserker(d):
    d.pieslice([5, 9, 27, 31], 180, 360, fill=W1)
    d.rectangle([5, 19, 27, 23], fill=W2)
    d.polygon([(6, 16), (1, 4), (9, 12)], fill=W1)
    d.polygon([(26, 16), (31, 4), (23, 12)], fill=W1)
    d.rectangle([12, 15, 14, 17], fill=RED)
    d.rectangle([18, 15, 20, 17], fill=RED)


@icon
def siphon(d):
    drop(d, 16, 21, 8, BLUE)
    d.ellipse([12, 17, 15, 20], fill=(190, 225, 255, 255))
    d.polygon([(3, 3), (9, 3), (6, 9)], fill=W1)
    d.polygon([(23, 3), (29, 3), (26, 9)], fill=W1)


@icon
def efficiency(d):
    drop(d, 13, 20, 8, BLUE)
    d.rectangle([20, 6, 30, 9], fill=W1)


@icon
def spellpower(d):
    pts = []
    for i in range(16):
        r = 14 if i % 2 == 0 else 6
        a = i * math.pi / 8 - math.pi / 2
        pts.append((16 + r * math.cos(a), 16 + r * math.sin(a)))
    d.polygon(pts, fill=W1)
    d.ellipse([12, 12, 20, 20], fill=BLUE)


@icon
def surge(d):
    d.polygon([(18, 1), (6, 18), (14, 18), (11, 31), (26, 12), (17, 12), (22, 1)], fill=W1)
    d.line([(18, 3), (9, 16)], fill=W2)


@icon
def overflow(d):
    d.rectangle([13, 2, 19, 6], fill=W2)
    d.rectangle([12, 7, 20, 10], fill=W1)
    d.ellipse([6, 9, 26, 30], fill=W1)
    d.chord([8, 13, 24, 28], 0, 180, fill=BLUE)
    d.ellipse([10, 13, 13, 16], fill=(255, 255, 255, 255))


@icon
def archmage(d):
    d.polygon([(16, 1), (6, 24), (26, 24)], fill=W1)
    d.rectangle([2, 23, 30, 27], fill=W2)
    d.polygon([(15, 10), (16, 7), (17, 10), (20, 11), (17, 12), (16, 15), (15, 12), (12, 11)], fill=BLUE)


@icon
def tough(d):
    heart(d, 16, 13, 7, W1)
    d.rectangle([14, 8, 18, 18], fill=RED)
    d.rectangle([11, 11, 21, 15], fill=RED)


@icon
def ironskin(d):
    d.polygon([(16, 2), (28, 6), (27, 18), (16, 30), (5, 18), (4, 6)], fill=W1)
    d.polygon([(16, 5), (25, 8), (24, 17), (16, 26)], fill=W2)
    d.line([(16, 4), (16, 28)], fill=OUT)


@icon
def quickfeet(d):
    d.polygon([(10, 4), (18, 4), (18, 18), (27, 22), (27, 27), (10, 27)], fill=W1)
    d.rectangle([10, 24, 27, 27], fill=W2)
    for y in (9, 15, 21):
        d.line([(1, y), (6, y)], fill=W1, width=2)


@icon
def regen(d):
    heart(d, 16, 13, 7, GREEN)
    d.rectangle([14, 8, 18, 18], fill=W1)
    d.rectangle([11, 11, 21, 15], fill=W1)


@icon
def treasure(d):
    for i, y in enumerate((22, 16, 10)):
        d.ellipse([5 + i, y, 21 + i, y + 7], fill=GOLD if i % 2 == 0 else (220, 160, 40, 255))
    d.ellipse([18, 3, 30, 15], fill=GOLD)
    d.rectangle([23, 6, 25, 12], fill=(170, 110, 20, 255))


@icon
def undying(d):
    d.ellipse([10, 1, 22, 15], fill=W1)
    d.ellipse([13, 4, 19, 12], fill=(0, 0, 0, 0))
    d.rectangle([14, 13, 18, 31], fill=W1)
    d.rectangle([6, 15, 26, 19], fill=W1)
    d.rectangle([15, 14, 17, 30], fill=GOLD)


def main():
    strip = Image.new("RGBA", (S * len(ORDER), S), (0, 0, 0, 0))
    for i, name in enumerate(ORDER):
        strip.alpha_composite(outlined(ICONS[name]), (i * S, 0))
    strip.save("pictures/icons/tree.png", optimize=True)
    big = strip.resize((strip.width * 4, strip.height * 4), Image.NEAREST)
    return big


if __name__ == "__main__":
    import sys
    big = main()
    if len(sys.argv) > 1:
        bg = Image.new("RGBA", big.size, (30, 46, 46, 255))
        bg.alpha_composite(big)
        bg.save(sys.argv[1])
