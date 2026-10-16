"""Draws the hero's own body animations for the spear, axe and dagger (their stance and their three
basic attacks), in the same pixel style as his sprite sheets: two yellows, the far arm and leg in the
darker one. The swords and scythes keep the original sheets.

Each animation is a few key poses; frames in between are blended. A pose gives his hip, how far his
body leans, where his feet are, where his hand holds the weapon, the weapon's angle and how far it is
pushed along its length (slide). Arms and legs reach their targets by bending at the elbow and knee.
The frame counts and the frames the hits land on match the original attacks, so the game's timings
(animations.js) still fit.

Writes pictures/hold/<type>_<sheet>.png and, in hold-data.js, types.<type>.<sheet> = one entry per
frame: [grip x, grip y, weapon angle, slide, head x, head y, trail strength 0..1].
Usage: python tools/make_weapon_moves.py [preview.png]"""
import json, math, sys
from PIL import Image, ImageDraw

W, H = 128, 64
LIGHT = (251, 242, 54, 255)
SHADE = (208, 200, 23, 255)
TORSO, NECK_TO_HEAD, HEAD_R = 18, 7, 6
THIGH, SHIN, UPPER, FORE = 11, 11, 9, 9
FRAMES = {"idle": 4, "attack1": 10, "attack2": 8, "attack3": 10}
HITS = {"attack1": 3, "attack2": 1, "attack3": 2}   # the frame each attack lands on (animations.js)

# A pose: hip (x, y), lean (degrees, + = forward), ff / bf = front / back foot, grip = the front hand,
# wang = the weapon's angle (degrees: 0 ahead, -90 up, 90 down), slide, fx = trail strength,
# bhand = where the other hand goes (None: the type's default).
def P(hip, lean, ff, bf, grip, wang, slide=0, fx=0.0, bhand=None):
    return dict(hip=hip, lean=lean, ff=ff, bf=bf, grip=grip, wang=wang, slide=slide, fx=fx, bhand=bhand)


SPEAR_READY = P((58, 41), 5, (66, 63), (50, 63), (60, 34), -40, -10)
AXE_READY = P((57, 41), 3, (64, 63), (50, 63), (60, 25), -140)
DAGGER_READY = P((56, 44), 15, (66, 63), (46, 63), (64, 33), 100, -2)

MOVES = {
    "spear": {
        "two_hands": True,
        "idle": [(0, P((57, 41), 3, (64, 63), (50, 63), (64, 34), -80, -14)),
                 (2, P((57, 42), 3, (64, 63), (50, 63), (64, 35), -80, -14))],
        # a long straight jab
        "attack1": [(0, P((56, 41), -5, (66, 63), (48, 63), (54, 36), -5, -16)),
                    (2, P((60, 42), 15, (72, 63), (48, 63), (70, 33), -3, 6, 0.8)),
                    (3, P((62, 43), 22, (76, 63), (48, 63), (76, 32), -2, 12, 1)),
                    (5, P((62, 43), 20, (76, 63), (48, 63), (74, 32), -2, 10, 0.5)),
                    (9, SPEAR_READY)],
        # a quick second jab, higher
        "attack2": [(0, P((60, 42), 12, (72, 63), (50, 63), (66, 30), -12, -4, 0.3)),
                    (1, P((62, 42), 18, (74, 63), (50, 63), (76, 28), -14, 12, 1)),
                    (3, P((62, 42), 16, (74, 63), (50, 63), (74, 29), -14, 9, 0.5)),
                    (7, SPEAR_READY)],
        # crouch, then spring up driving the spear skyward
        "attack3": [(0, P((56, 46), 25, (68, 63), (46, 63), (62, 44), 20, -14)),
                    (1, P((60, 40), 5, (66, 62), (52, 60), (68, 28), -35, 2, 0.7)),
                    (2, P((62, 34), -5, (66, 56), (56, 58), (70, 18), -50, 16, 1)),
                    (4, P((62, 34), -5, (66, 56), (56, 58), (70, 18), -50, 14, 0.8)),
                    (6, P((60, 40), 0, (68, 63), (52, 63), (64, 26), -60, 0, 0.2)),
                    (9, SPEAR_READY)],
    },
    "axe": {
        "two_hands": True,
        "idle": [(0, AXE_READY), (2, P((57, 42), 3, (64, 63), (50, 63), (60, 26), -142))],
        # raised high behind his head, then chopped down in front
        "attack1": [(0, P((56, 41), -10, (64, 63), (48, 63), (52, 16), -150)),
                    (1, P((57, 41), -12, (64, 63), (48, 63), (50, 14), -165)),
                    (2, P((60, 43), 10, (70, 63), (48, 63), (64, 20), -60, 0, 0.6)),
                    (3, P((62, 45), 30, (72, 63), (48, 63), (72, 38), 50, 0, 1)),
                    (5, P((62, 45), 28, (72, 63), (48, 63), (72, 40), 60, 0, 0.4)),
                    (9, AXE_READY)],
        # an upward swing from low in front
        "attack2": [(0, P((58, 44), 20, (70, 63), (48, 63), (68, 46), 70, 0, 0.3)),
                    (1, P((60, 40), 0, (68, 63), (50, 63), (68, 22), -70, 0, 1)),
                    (2, P((59, 39), -8, (66, 63), (50, 63), (62, 14), -110, 0, 0.6)),
                    (7, AXE_READY)],
        # all the way round behind him and slammed into the ground
        "attack3": [(0, P((56, 42), -15, (64, 63), (48, 63), (46, 22), -200)),
                    (1, P((58, 40), -5, (66, 63), (50, 63), (60, 12), -100, 0, 0.7)),
                    (2, P((62, 45), 30, (74, 63), (48, 63), (74, 40), 60, 0, 1)),
                    (3, P((62, 46), 32, (74, 63), (48, 63), (76, 44), 75, 0, 0.8)),
                    (5, P((62, 46), 32, (74, 63), (48, 63), (76, 44), 75, 0, 0.3)),
                    (9, AXE_READY)],
    },
    "dagger": {
        "two_hands": False,
        "idle": [(0, DAGGER_READY), (2, P((56, 45), 16, (66, 63), (46, 63), (64, 34), 100, -2))],
        # a low lunging stab
        "attack1": [(0, P((56, 44), 15, (66, 63), (46, 63), (58, 34), 10, -4)),
                    (2, P((62, 45), 30, (76, 63), (48, 63), (76, 36), 5, 2, 0.8)),
                    (3, P((64, 45), 32, (78, 63), (48, 63), (80, 36), 5, 4, 1)),
                    (5, P((64, 45), 30, (78, 63), (48, 63), (78, 36), 5, 3, 0.5)),
                    (9, DAGGER_READY)],
        # a rising backhand slash
        "attack2": [(0, P((60, 44), 20, (70, 63), (48, 63), (56, 40), 60, 0, 0.2)),
                    (1, P((62, 43), 15, (72, 63), (48, 63), (74, 26), -45, 2, 1)),
                    (2, P((62, 43), 12, (72, 63), (48, 63), (72, 22), -70, 2, 0.5)),
                    (7, DAGGER_READY)],
        # a leap and a two-handed stab down into the enemy
        "attack3": [(0, P((58, 46), 25, (66, 63), (48, 63), (60, 38), -30, 0, 0, (58, 36))),
                    (1, P((64, 32), 10, (70, 52), (56, 56), (70, 20), -60, 0, 0.3, (67, 22))),
                    (2, P((68, 36), 30, (76, 56), (60, 58), (80, 40), 60, 4, 1, (77, 39))),
                    (4, P((68, 44), 30, (78, 63), (56, 63), (80, 46), 70, 4, 0.6, (77, 45))),
                    (9, DAGGER_READY)],
    },
}


def blend(a, b, k):
    if a is None or b is None:
        return a if k < 0.5 else b
    if isinstance(a, tuple):
        return tuple(x + (y - x) * k for x, y in zip(a, b))
    return a + (b - a) * k


def pose_at(keys, f):
    for (fa, a), (fb, b) in zip(keys, keys[1:]):
        if fa <= f <= fb:
            k = (f - fa) / (fb - fa)
            return {n: blend(a[n], b[n], k) for n in a}
    return dict(keys[-1][1]) if f > keys[-1][0] else dict(keys[0][1])


def reach(start, target, l1, l2, bend):
    """Two-bone reach: returns (joint, end). bend = +1 puts the joint on the side of larger x
    (knees forward), -1 on the side of larger y (elbows down)."""
    sx, sy = start
    dx, dy = target[0] - sx, target[1] - sy
    d = max(0.01, min(math.hypot(dx, dy), l1 + l2 - 0.01))
    base = math.atan2(dy, dx)
    a = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    joints = [(sx + l1 * math.cos(base + s * a), sy + l1 * math.sin(base + s * a)) for s in (1, -1)]
    joint = max(joints, key=(lambda j: j[0]) if bend > 0 else (lambda j: j[1]))
    jx, jy = joint
    ex, ey = target[0] - jx, target[1] - jy
    e = math.hypot(ex, ey) or 1
    return joint, (jx + ex / e * l2, jy + ey / e * l2)


def limb(d, pts, width, color):
    for p, q in zip(pts, pts[1:]):
        d.line([p, q], fill=color, width=width)
    for x, y in pts:
        r = width / 2 - 0.5
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)


def draw_frame(pose, two_hands):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hx, hy = pose["hip"]
    lean = math.radians(pose["lean"])
    up = (math.sin(lean), -math.cos(lean))
    neck = (hx + up[0] * TORSO, hy + up[1] * TORSO)
    head = (neck[0] + up[0] * NECK_TO_HEAD, neck[1] + up[1] * NECK_TO_HEAD)
    shoulder = (neck[0] - up[0] * 3, neck[1] - up[1] * 3)
    wa = math.radians(pose["wang"])
    grip = pose["grip"]
    if pose["bhand"] is not None:
        back_target = pose["bhand"]
    elif two_hands:
        back_target = (grip[0] - math.cos(wa) * 7, grip[1] - math.sin(wa) * 7)
    else:   # a guard up in front of his chest
        back_target = (neck[0] + 5, neck[1] + 5)
    # far side first, in the darker yellow
    bknee, bfoot = reach((hx - 1, hy), pose["bf"], THIGH, SHIN, +1)
    limb(d, [(hx - 1, hy), bknee, bfoot], 5, SHADE)
    belbow, bhand = reach(shoulder, back_target, UPPER, FORE, -1)
    limb(d, [shoulder, belbow, bhand], 4, SHADE)
    limb(d, [(hx, hy), neck], 7, LIGHT)
    d.ellipse([head[0] - HEAD_R, head[1] - HEAD_R, head[0] + HEAD_R, head[1] + HEAD_R], fill=LIGHT)
    fknee, ffoot = reach((hx + 1, hy), pose["ff"], THIGH, SHIN, +1)
    limb(d, [(hx + 1, hy), fknee, ffoot], 5, LIGHT)
    felbow, fhand = reach(shoulder, grip, UPPER, FORE, -1)
    limb(d, [shoulder, felbow, fhand], 4, LIGHT)
    # hard pixel edges: no half-transparent pixels
    px = img.load()
    for y in range(H):
        for x in range(W):
            if 0 < px[x, y][3] < 255:
                px[x, y] = px[x, y][:3] + (255,) if px[x, y][3] > 110 else (0, 0, 0, 0)
    data = [round(fhand[0], 1), round(fhand[1], 1), round(wa, 3), round(pose["slide"], 1),
            round(head[0], 1), round(head[1], 1), round(pose["fx"], 2)]
    return img, data


def main():
    with open("hold-data.js") as fh:
        src = fh.read()
    hold = json.loads(src[src.index("{"):src.rindex("}") + 1])
    hold["types"] = {}
    previews = []
    for wtype, moves in MOVES.items():
        hold["types"][wtype] = {}
        for sheet, n in FRAMES.items():
            strip = Image.new("RGBA", (W * n, H), (0, 0, 0, 0))
            frames = []
            for f in range(n):
                img, data = draw_frame(pose_at(moves[sheet], f), moves["two_hands"])
                strip.alpha_composite(img, (f * W, 0))
                frames.append(data)
            strip.save(f"pictures/hold/{wtype}_{sheet}.png", optimize=True)
            hold["types"][wtype][sheet] = frames
            previews.append((strip, frames))
    head = [l for l in src.split("\n") if l.startswith("//")]
    with open("hold-data.js", "w", newline="\n") as fh:
        fh.write("\n".join(head) + "\n")
        fh.write("window.STICKGO_HOLD = " + json.dumps(hold, separators=(",", ":")) + ";\n")
    if len(sys.argv) > 1:   # every frame with its weapon as a line, for checking
        sheet = Image.new("RGBA", (W * 10, H * len(previews)), (200, 210, 230, 255))
        for i, (strip, frames) in enumerate(previews):
            sheet.alpha_composite(strip.crop((0, 0, min(strip.width, W * 10), H)), (0, i * H))
            d = ImageDraw.Draw(sheet)
            for f, (gx, gy, a, slide, *_r) in enumerate(frames[:10]):
                x0 = f * W + gx + math.cos(a) * slide
                y0 = i * H + gy + math.sin(a) * slide
                d.line([x0 - math.cos(a) * 4, y0 - math.sin(a) * 4, x0 + math.cos(a) * 30, y0 + math.sin(a) * 30], fill=(60, 40, 30, 255), width=2)
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(sys.argv[1])
    print("drew", len(previews), "sheets")


main()
