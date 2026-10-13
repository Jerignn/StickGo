"""Draws the enemy sprite sheets (pictures/foe_<kind>.png) in the same pixel style as the yellow hero.

Each sheet is 8 frames wide and 5 rows tall, every frame 128x64 with the feet on the bottom row and
the figure facing right (the game flips it): idle (4), walk (8), attack (6), hit (2), death (6).
Run:  python tools/make_enemy_sprites.py
"""
import math
import os
from PIL import Image, ImageDraw

W, H = 128, 64
CX, GROUND = 64, 63
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pictures")
BLACK = (0, 0, 0, 255)

# body, back-limb shadow, limb width, head radius, extra
KINDS = {
    "grunt":  dict(body=(232, 72, 72), shade=(172, 40, 40), width=5, head=6),
    "ninja":  dict(body=(78, 90, 168), shade=(46, 54, 112), width=5, head=6),
    "guard":  dict(body=(150, 162, 178), shade=(100, 112, 128), width=5, head=6),
    "brute":  dict(body=(240, 140, 50), shade=(180, 95, 25), width=7, head=8),
    "archer": dict(body=(84, 174, 84), shade=(52, 122, 58), width=5, head=6),
    "bomber": dict(body=(218, 172, 72), shade=(162, 122, 42), width=5, head=6),
    "ghost":  dict(body=(150, 218, 255), shade=(100, 170, 220), width=5, head=6, alpha=175),
    "boss":   dict(body=(172, 62, 202), shade=(112, 32, 142), width=7, head=8),
}


def limb(p, ang, ln):
    return (p[0] + math.sin(ang) * ln, p[1] + math.cos(ang) * ln)


def make_pose(lean, legs, arms, lift=0.0):
    """Joint positions. Angles: 0 = straight down, positive = forwards (right)."""
    thigh = shin = 13
    torso, upper, fore = 17, 10, 10
    drop = lambda t, b: thigh * math.cos(t) + shin * math.cos(t - b)
    hip = (CX - 2, GROUND - max(drop(*legs[0]), drop(*legs[1])) - lift)
    neck = limb(hip, math.pi - lean, torso)
    head = limb(neck, math.pi - lean, 7)
    shoulder = limb(neck, -lean, 3)
    p = dict(hip=hip, neck=neck, head=head, shoulder=shoulder)
    for side, i in (("F", 0), ("B", 1)):
        t, b = legs[i]
        p["knee" + side] = limb(hip, t, thigh)
        p["foot" + side] = limb(p["knee" + side], t - b, shin)
        u, e = arms[i]
        p["elbow" + side] = limb(shoulder, u, upper)
        p["hand" + side] = limb(p["elbow" + side], u + e, fore)
        p["fa" + side] = u + e   # forearm angle, for holding things
    return p


def stroke(d, pts, color, width):
    d.line([(round(x), round(y)) for x, y in pts], fill=color, width=width, joint="curve")
    r = width / 2 - 0.5
    for x, y in pts:
        d.ellipse([round(x) - r, round(y) - r, round(x) + r, round(y) + r], fill=color)


def circle(d, c, r, color):
    d.ellipse([round(c[0]) - r, round(c[1]) - r, round(c[0]) + r, round(c[1]) + r], fill=color)


def weapon_at(d, hand, ang, ln, width=2):
    tip = limb(hand, ang, ln)
    stroke(d, [hand, tip], BLACK, width)
    return tip


STEEL, STEEL_D, GOLD = (206, 214, 228, 255), (132, 144, 164, 255), (226, 176, 56, 255)
WOOD, WOOD_D = (140, 94, 48, 255), (88, 58, 30, 255)


def wpoly(d, hand, ang, pts, fill, outline=BLACK):
    """A polygon in weapon space: x runs along the weapon from the hand, y across it."""
    s_, c_ = math.sin(ang), math.cos(ang)
    world = [(hand[0] + s_ * lx + c_ * ly, hand[1] + c_ * lx - s_ * ly) for lx, ly in pts]
    d.polygon([(round(x), round(y)) for x, y in world], fill=fill, outline=outline)


def draw_sword(d, hand, ang, length=19, thick=1.8):
    wpoly(d, hand, ang, [(-5, -1.3), (3, -1.3), (3, 1.3), (-5, 1.3)], WOOD_D)                      # grip
    wpoly(d, hand, ang, [(-7, -2), (-5, -2), (-5, 2), (-7, 2)], GOLD)                               # pommel
    wpoly(d, hand, ang, [(3, -4.5), (5, -4.5), (5, 4.5), (3, 4.5)], GOLD)                           # cross guard
    wpoly(d, hand, ang, [(5, -thick), (length, -thick), (length + 3, 0), (length, thick), (5, thick)], STEEL)   # blade
    wpoly(d, hand, ang, [(5.5, -0.3), (length, -0.3), (length + 1, 0), (length, 0.3), (5.5, 0.3)], STEEL_D, STEEL_D)  # fuller


def draw_katana(d, hand, ang):
    wpoly(d, hand, ang, [(-8, -1.4), (4, -1.4), (4, 1.4), (-8, 1.4)], (40, 44, 72, 255))             # wrapped grip
    for lx in (-6, -3, 0):
        wpoly(d, hand, ang, [(lx, -1.4), (lx + 1, -1.4), (lx + 1, 1.4), (lx, 1.4)], (200, 40, 40, 255), None)
    wpoly(d, hand, ang, [(4, -3.6), (5.6, -3.6), (5.6, 3.6), (4, 3.6)], BLACK)                       # guard
    wpoly(d, hand, ang, [(5.6, -1.1), (27, -1.1), (32, 0), (27, 0.8), (5.6, 1.1)], (226, 234, 248, 255))  # long, thin blade


def draw_club(d, hand, ang, big=False):
    r = 6 if big else 4.5
    wpoly(d, hand, ang, [(-3, -1.6), (12, -2.2), (19, -r), (25, -r), (27, 0), (25, r), (19, r), (12, 2.2), (-3, 1.6)], WOOD)
    wpoly(d, hand, ang, [(12, -2.2), (14, -2.4), (14, 2.4), (12, 2.2)], WOOD_D, None)                  # iron band
    for lx in (20.5, 24):                                                                                # studs
        for side in (-1, 1):
            wpoly(d, hand, ang, [(lx - 1.5, side * r), (lx, side * (r + 3.5)), (lx + 1.5, side * r)], STEEL)
    wpoly(d, hand, ang, [(26, -1), (30, 0), (26, 1)], STEEL)                                           # tip spike


def draw_axe(d, hand, ang):
    wpoly(d, hand, ang, [(-8, -1.6), (30, -1.6), (30, 1.6), (-8, 1.6)], WOOD)                          # long haft
    wpoly(d, hand, ang, [(21, -1.6), (19, -13), (28, -15), (35, -8), (33, -2), (28, 0)], STEEL)        # blade
    wpoly(d, hand, ang, [(24, -3), (24, -12), (30, -11), (31, -6)], STEEL_D, None)                     # edge shading
    wpoly(d, hand, ang, [(22, 1.6), (21, 8), (28, 3)], STEEL)                                          # back spike
    wpoly(d, hand, ang, [(30, -1.6), (34, 0), (30, 1.6)], STEEL)


def draw_claws(d, hand, ang):
    for k in (-1, 0, 1):
        wpoly(d, hand, ang, [(0, k * 3 - 1.2), (9, k * 3.4 - 2), (16, k * 4 + 2), (10, k * 3.4 + 0.4), (0, k * 3 + 1.2)],
              (236, 252, 255, 255), (120, 190, 235, 255))


def draw_shield(d, c):
    d.ellipse([c[0] - 7, c[1] - 13, c[0] + 7, c[1] + 13], fill=STEEL_D, outline=BLACK)
    d.ellipse([c[0] - 4, c[1] - 10, c[0] + 4, c[1] + 10], fill=STEEL, outline=None)
    d.ellipse([c[0] - 2, c[1] - 2, c[0] + 2, c[1] + 2], fill=GOLD, outline=BLACK)


def draw_bow(d, hand, hb, pull):
    c = (hand[0] + 3, hand[1])
    arc = [(c[0] + 9 * math.cos(a) - 3, c[1] + 15 * math.sin(a)) for a in [(-1.25 + 2.5 * i / 10) for i in range(11)]]
    stroke(d, arc, WOOD_D, 4)
    stroke(d, arc, WOOD, 2)
    top, bot = arc[0], arc[-1]
    nock = hb if pull > 0.05 else (c[0] - 4, c[1])
    d.line([top, nock, bot], fill=(236, 236, 226, 255), width=1)
    if pull > 0.05:   # an arrow drawn back on the string
        tip = (c[0] + 11, c[1])
        d.line([nock, tip], fill=WOOD_D, width=1)
        d.polygon([(round(tip[0]) + 4, round(tip[1])), (round(tip[0]) - 1, round(tip[1]) - 3), (round(tip[0]) - 1, round(tip[1]) + 3)], fill=STEEL, outline=BLACK)
        d.line([(nock[0], nock[1] - 2), (nock[0] + 3, nock[1])], fill=(210, 60, 60, 255), width=1)
        d.line([(nock[0], nock[1] + 2), (nock[0] + 3, nock[1])], fill=(210, 60, 60, 255), width=1)


def draw_bomb(d, b):
    circle(d, b, 5, BLACK)
    circle(d, b, 4, (52, 54, 66, 255))
    d.point([(round(b[0]) - 2, round(b[1]) - 2)], fill=(150, 156, 176, 255))                             # highlight
    d.line([(round(b[0]) + 1, round(b[1]) - 5), (round(b[0]) + 4, round(b[1]) - 8)], fill=(150, 112, 60, 255), width=1)   # fuse
    d.point([(round(b[0]) + 5, round(b[1]) - 9), (round(b[0]) + 4, round(b[1]) - 9)], fill=(255, 190, 50, 255))
    d.point([(round(b[0]) + 5, round(b[1]) - 10)], fill=(255, 240, 160, 255))


def draw_figure(kind, p, extra=None):
    """One frame. `extra` is a dict of per-frame details (weapon, bow, bomb...)."""
    k = KINDS[kind]
    extra = extra or {}
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = k["body"] + (255,)
    shade = k["shade"] + (255,)
    w = k["width"]
    # far side first
    stroke(d, [p["hip"], p["kneeB"], p["footB"]], shade, w)
    stroke(d, [p["shoulder"], p["elbowB"], p["handB"]], shade, w)
    if extra.get("shield"):   # held out in front on the far arm
        draw_shield(d, (p["handB"][0] + 5, p["handB"][1] - 3))
    stroke(d, [p["neck"], p["shoulder"], p["hip"]], body, w)
    stroke(d, [p["hip"], p["kneeF"], p["footF"]], body, w)
    stroke(d, [p["shoulder"], p["elbowF"], p["handF"]], body, w)
    circle(d, p["head"], k["head"], body)
    # accessories
    hx, hy = p["head"]
    if kind == "ninja":
        d.line([(hx - 6, hy - 1), (hx + 6, hy - 1)], fill=(226, 32, 32, 255), width=2)
        d.line([(hx - 6, hy - 1), (hx - 13, hy + 2)], fill=(226, 32, 32, 255), width=2)
        d.line([(hx - 6, hy), (hx - 12, hy - 3)], fill=(226, 32, 32, 255), width=1)
    if kind == "archer":
        d.polygon([(hx - 6, hy - 3), (hx + 3, hy - 12), (hx + 7, hy - 2)], fill=(45, 110, 50, 255))
    if kind == "guard":
        d.pieslice([hx - 6, hy - 7, hx + 6, hy + 5], 180, 360, fill=(120, 130, 145, 255))
    if kind == "bomber":
        d.line([(p["shoulder"][0] - 5, p["shoulder"][1]), (p["hip"][0] + 4, p["hip"][1] - 2)], fill=(120, 80, 30, 255), width=2)
    if kind == "boss":
        for s in (-1, 1):
            d.polygon([(hx + s * 5, hy - 5), (hx + s * 12, hy - 15), (hx + s * 9, hy - 2)], fill=(236, 228, 200, 255))
    # weapon in the front hand
    hand, fa = p["handF"], p["fa" + "F"]
    wp, ang = extra.get("weapon"), p["faF"] + extra.get("wa", 0.3)
    if wp == "sword":
        draw_sword(d, hand, ang, 24 if kind == "guard" else 19, 2.2 if kind == "guard" else 1.8)
    elif wp == "club":
        if kind == "boss":
            draw_axe(d, hand, ang)
        else:
            draw_club(d, hand, ang, big=kind == "brute")
    elif wp == "katana":
        draw_katana(d, hand, ang)
    elif wp == "claw":
        draw_claws(d, hand, p["faF"])
    elif wp == "bow":
        draw_bow(d, hand, p["handB"], extra.get("pull", 0))
    if extra.get("bomb"):
        draw_bomb(d, (p["handF"][0] + 1, p["handF"][1] - 6))
    if "alpha" in k:
        px = img.load()
        for y in range(H):
            for x in range(W):
                r, g, b, a = px[x, y]
                if a:
                    px[x, y] = (r, g, b, k["alpha"] if (r, g, b) != (0, 0, 0) else 200)
    return img


# --- animations ---------------------------------------------------------------------------
def idle_frames(kind):
    out = []
    for i in range(4):
        lift = 0.6 + 0.6 * math.sin(i / 4 * 2 * math.pi)
        p = make_pose(0.1, [[0.14, 0.12], [-0.14, 0.12]], [[0.3, 0.5], [-0.25, 0.5]], lift)
        out.append(draw_figure(kind, p, held(kind)))
    return out


def held(kind, **kw):
    e = {}
    if kind in ("grunt", "ghost"):
        e["weapon"] = "sword" if kind == "grunt" else "claw"
    if kind == "ninja":
        e["weapon"] = "katana"
    if kind in ("brute", "boss"):
        e["weapon"] = "club"
    if kind == "guard":
        e["weapon"] = "sword"
        e["shield"] = True
    if kind == "archer":
        e["weapon"] = "bow"
    if kind == "bomber":
        e["bomb"] = True
    e.update(kw)
    return e


def walk_frames(kind):
    out = []
    for i in range(8):
        ph = i / 8 * 2 * math.pi
        legs = [[0.65 * math.sin(ph + off), 0.2 + 1.35 * max(0, math.cos(ph + off - 0.5))] for off in (0, math.pi)]
        arms = [[-0.75 * math.sin(ph + off) + 0.2, 1.4] for off in (0, math.pi)]
        lift = 1.5 * max(0, -math.cos(ph * 2))
        p = make_pose(0.25, legs, arms, lift)
        out.append(draw_figure(kind, p, held(kind)))
    return out


def attack_frames(kind):
    """Frames 0-2 are the wind-up (held until the strike), 3-5 are the strike and follow-through."""
    out = []
    if kind == "archer":   # draw the bow, release, relax
        for i, pull in enumerate([0.0, 0.5, 1.0, 0.0, 0.0, 0.0]):
            legs = [[0.5, 0.3], [-0.45, 0.3]]
            arms = [[1.57, 0.0], [-1.2 + 0.9 * pull, 0.2 + 0.5 * pull]] if i < 3 else [[1.57, 0.0], [-0.3 - 0.2 * (i - 3), 1.0]]
            p = make_pose(0.12, legs, arms)
            out.append(draw_figure(kind, p, dict(weapon="bow", pull=pull)))
        return out
    if kind == "bomber":   # lift the bomb overhead, throw it, follow through
        for i in range(6):
            raise_ = [0.3, 0.7, 1.0, 0.2, -0.1, 0.0][i]
            legs = [[0.35, 0.4], [-0.4, 0.2]]
            arms = [[0.4 + 2.6 * raise_, 0.5], [-0.5, 0.8]]
            lean = [0.1, 0.0, -0.1, 0.5, 0.55, 0.3][i]
            p = make_pose(lean, legs, arms)
            out.append(draw_figure(kind, p, dict(bomb=i < 3)))
        return out
    crouch = kind == "ninja"
    for i in range(6):
        up = [2.2, 3.0, 3.6, 1.5, 0.3, 0.1][i]
        elbow = [0.8, 0.4, 0.2, 0.1, 0.1, 0.4][i]
        lean = [0.1, -0.05, -0.15, 0.55, 0.65, 0.4][i]
        legs = [[1.0, 0.9], [-0.7, 0.2]] if i >= 3 else ([[0.9, 1.5], [-0.5, 1.4]] if crouch else [[0.3, 0.3], [-0.3, 0.2]])
        arms = [[up, elbow], [0.8, 1.0]]
        p = make_pose(lean, legs, arms)
        out.append(draw_figure(kind, p, held(kind, wa=[1.6, 1.4, 1.1, 0.5, 0.5, 0.6][i])))   # raised behind the head, then forward
    return out


def hit_frames(kind):
    out = []
    for i, lean in enumerate([-0.35, -0.5]):
        p = make_pose(lean, [[0.3, 0.6], [-0.5, 0.4]], [[-0.5, 0.4], [-1.0, 0.5]])
        out.append(draw_figure(kind, p, held(kind, weapon=None, bomb=False, shield=False)))
    return out


def death_frames(kind):
    out = []
    base = hit_frames(kind)[1]
    for i, ang in enumerate([0, 25, 55, 80, 90, 90]):
        rot = base.rotate(ang, resample=Image.NEAREST, center=(CX - 6, GROUND))
        if i >= 4:
            rot = rot.transform(rot.size, Image.AFFINE, (1, 0, 0, 0, 1, 0))
        out.append(rot)
    return out


def sheet(kind):
    rows = [idle_frames(kind), walk_frames(kind), attack_frames(kind), hit_frames(kind), death_frames(kind)]
    img = Image.new("RGBA", (W * 8, H * len(rows)), (0, 0, 0, 0))
    for r, frames in enumerate(rows):
        for c, f in enumerate(frames):
            img.alpha_composite(f, (c * W, r * H))
    return img


if __name__ == "__main__":
    for kind in KINDS:
        sheet(kind).save(os.path.join(OUT, f"foe_{kind}.png"))
        print("wrote", kind)
