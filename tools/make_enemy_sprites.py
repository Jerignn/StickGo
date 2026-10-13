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
    if extra.get("shield"):   # a round shield held out in front on the far arm
        c = (p["handB"][0] + 4, p["handB"][1] - 2)
        d.ellipse([c[0] - 6, c[1] - 12, c[0] + 6, c[1] + 12], fill=(205, 212, 224, 255), outline=BLACK)
        circle(d, c, 2, BLACK)
    if extra.get("bandolier"):
        pass
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
    # eyes: two angry dots on the face side (he faces right)
    ec = (255, 255, 255, 255) if kind != "ghost" else (40, 70, 110, 255)
    d.point([(round(hx + 2), round(hy - 1)), (round(hx + 4), round(hy - 1))], fill=ec)
    if kind in ("grunt", "ninja", "brute", "boss", "archer", "bomber", "guard"):
        d.line([(round(hx + 1), round(hy - 3)), (round(hx + 5), round(hy - 2))], fill=BLACK, width=1)
    # weapon in the front hand
    hand, fa = p["handF"], p["fa" + "F"]
    wp = extra.get("weapon")
    if wp == "sword":
        weapon_at(d, hand, fa + extra.get("wa", 0.3), 14)
    elif wp == "club":
        tip = weapon_at(d, hand, fa + extra.get("wa", 0.3), 17, 3 if kind == "grunt" else 4)
        circle(d, tip, 4 if kind == "brute" else 6, (110, 74, 40, 255))
    elif wp == "katana":
        weapon_at(d, hand, fa + extra.get("wa", 0.3), 17)
    elif wp == "claw":
        for off in (-0.25, 0, 0.25):
            weapon_at(d, hand, fa + off, 5, 1)
    elif wp == "bow":
        pull = extra.get("pull", 0)
        c = (hand[0] + 2, hand[1])
        pts = [(c[0] + 8 * math.cos(a), c[1] + 13 * math.sin(a)) for a in [(-1.2 + 2.4 * i / 8) for i in range(9)]]
        stroke(d, pts, (120, 80, 36, 255), 2)
        hb = p["handB"]
        top, bot = pts[0], pts[-1]
        d.line([top, hb if pull > 0.05 else (c[0] - 1, c[1]), bot], fill=BLACK, width=1)
        if pull > 0.05:
            d.line([hb, (c[0] + 8, c[1])], fill=BLACK, width=1)
    if extra.get("bomb"):
        b = (p["handF"][0] + 1, p["handF"][1] - 5)
        circle(d, b, 4, (30, 30, 30, 255))
        d.point([(round(b[0] + 3), round(b[1] - 5))], fill=(255, 176, 46, 255))
        d.line([(round(b[0] + 1), round(b[1] - 4)), (round(b[0] + 3), round(b[1] - 6))], fill=(160, 160, 160, 255), width=1)
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
        out.append(draw_figure(kind, p, held(kind, wa=0.2 if i < 3 else 0.5)))
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
