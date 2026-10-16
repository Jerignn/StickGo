"""Lets the hero hold any shop weapon in place of the black scythe drawn into his sprites.

For every hero frame it finds the scythe (the black pixels touching his body), works out the line
of its haft, which end carries the blade and where his hand grips it, then writes:
  pictures/hold/hero_<sheet>.png     the frames with the scythe taken out (gaps in the body filled)
  pictures/hold/trail_<sheet>.png    the other black pixels (slash trails), tinted per weapon in game
For every shop weapon (pictures/weapons/<id>.png) it keeps only the weapon itself (no particles):
  pictures/hold/w_<id>.png
and it writes hold-data.js with the grip and angle of every frame and every weapon.
The spears, axes, daggers and scythes are drawn by tools/make_new_weapons.py, which writes their own
held pictures, and tools/make_weapon_moves.py draws their bodies: run both again after this script so
their entries are back in hold-data.js.
Usage: python tools/make_hold.py [debug.png]"""
import json, math, os, sys
from PIL import Image, ImageDraw

SHEETS = {"idle": 4, "run": 10, "jump": 3, "jump_peak": 3, "fall": 4, "dash": 11,
          "attack1": 10, "attack2": 8, "attack3": 10, "skill1": 9, "skill2": 19, "skill3": 25,
          "start_skill3": 3, "hit1": 3, "hit3": 3, "death": 10}
W, H = 128, 64
OUT = "pictures/hold"
HELD_LEN = 36   # how long a held weapon is, in sprite pixels (about the scythe's length)

def is_black(p): return p[3] > 0 and p[0] < 30 and p[1] < 30 and p[2] < 30
def is_body(p): return p[3] > 0 and p[0] > 90 and p[1] > 85 and p[2] < 120   # the yellows and their shades

def components(mask):
    """8-connected groups of the (x, y) pixels in the set `mask`."""
    seen, groups = set(), []
    for start in mask:
        if start in seen: continue
        group, todo = [], [start]
        seen.add(start)
        while todo:
            x, y = todo.pop()
            group.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in mask and n not in seen: seen.add(n); todo.append(n)
        groups.append(group)
    return groups

def haft_line(pix):
    """The straight line (2 px wide) that covers the most pixels: returns (angle, offset, members)."""
    best = None
    for deg in range(0, 180, 2):
        a = math.radians(deg)
        nx, ny = -math.sin(a), math.cos(a)
        bins = {}
        for x, y in pix:
            bins.setdefault(round((x * nx + y * ny) / 2), []).append((x, y))
        for off, members in bins.items():
            if best is None or len(members) > len(best[2]): best = (a, off, members)
    return best

def analyse(frame, loose=False):
    """loose: the scythe may lie away from him (flung out of his hand when he dies)."""
    px = frame.load()
    black = {(x, y) for y in range(H) for x in range(W) if is_black(px[x, y])}
    body = {(x, y) for y in range(H) for x in range(W) if is_body(px[x, y])}
    touching = []
    for g in components(black):
        if len(g) < 15: continue
        contact = [p for p in g if any((p[0] + dx, p[1] + dy) in body for dx in (-1, 0, 1) for dy in (-1, 0, 1))]
        if contact or loose: touching.append((len(g), g, contact))
    if not touching: return None, set()
    _, scythe, contact = max(touching)
    a, off, line = haft_line(scythe)
    if len(line) < 10: return None, set()
    dx, dy = math.cos(a), math.sin(a)
    along = sorted(line, key=lambda p: p[0] * dx + p[1] * dy)
    e0, e1 = along[0], along[-1]
    # The blade end is the one with more of the scythe around it
    mass = lambda e: sum(1 for p in scythe if (p[0] - e[0]) ** 2 + (p[1] - e[1]) ** 2 < 100)
    head, tail = (e1, e0) if mass(e1) >= mass(e0) else (e0, e1)
    # His hand: where the haft touches his body, nearest the handle end
    line_set = set(line)
    grips = [p for p in contact if p in line_set] or contact or [tail]
    grip = min(grips, key=lambda p: (p[0] - tail[0]) ** 2 + (p[1] - tail[1]) ** 2)
    ang = math.atan2(head[1] - grip[1], head[0] - grip[0])
    # Pieces of the haft cut off by his body (or his hand) lie on the same line: they go too
    scythe = set(scythe)
    nx, ny = -dy, dx
    c0 = sum(p[0] * nx + p[1] * ny for p in line) / len(line)
    for g in components(black - scythe):
        if sum(1 for p in g if abs(p[0] * nx + p[1] * ny - c0) < 2.5) >= 0.7 * len(g): scythe |= set(g)
    return [grip[0], grip[1], round(ang, 3)], scythe

def fill_gaps(img, removed):
    """Where the haft crossed his body, paint the body back in from the pixels on either side."""
    px = img.load()
    for _ in range(2):
        for x, y in sorted(removed):
            if px[x, y][3]: continue
            for (ax, ay) in ((1, 0), (0, 1), (1, 1), (1, -1)):
                left = next((px[x - ax * k, y - ay * k] for k in range(1, 4)
                             if 0 <= x - ax * k < W and 0 <= y - ay * k < H and is_body(px[x - ax * k, y - ay * k])), None)
                right = next((px[x + ax * k, y + ay * k] for k in range(1, 4)
                              if 0 <= x + ax * k < W and 0 <= y + ay * k < H and is_body(px[x + ax * k, y + ay * k])), None)
                if left and right:
                    px[x, y] = left
                    break

def weapon_hold(path):
    """Keeps the biggest piece of a weapon picture and finds its handle end and its tip."""
    img = Image.open(path).convert("RGBA")
    px = img.load()
    solid = {(x, y) for y in range(img.height) for x in range(img.width) if px[x, y][3] > 0}
    # pieces of the weapon closer than 2 px count as one (guards, gems)
    groups = components({(x + dx, y + dy) for x, y in solid for dx in (-1, 0, 1) for dy in (-1, 0, 1)})
    main = set(max(groups, key=len)) & solid
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    op = out.load()
    for p in main: op[p] = px[p]
    bb = out.getbbox()
    out = out.crop(bb)
    main = {(x - bb[0], y - bb[1]) for x, y in main}
    # the weapons are drawn handle bottom-left, tip top-right
    tail = max(main, key=lambda p: p[1] - p[0])
    tip = max(main, key=lambda p: p[0] - p[1])
    length = math.hypot(tip[0] - tail[0], tip[1] - tail[1])
    ang = math.atan2(tip[1] - tail[1], tip[0] - tail[0])
    # grip a little way up the handle from its end
    g = (tail[0] + math.cos(ang) * length * 0.1, tail[1] + math.sin(ang) * length * 0.1)
    # its main colour (the average of its brighter pixels), used for its slash trail
    bright = [out.getpixel(p) for p in main if sum(out.getpixel(p)[:3]) > 200]
    color = "#%02x%02x%02x" % tuple(sum(c[i] for c in bright) // max(1, len(bright)) for i in range(3))
    # shrink it to the size of the scythe in his sprites, keeping hard pixel edges
    k = HELD_LEN / length
    small = out.resize((max(1, round(out.width * k)), max(1, round(out.height * k))), Image.BOX)
    sp = small.load()
    for y in range(small.height):
        for x in range(small.width):
            r, gg, b, a = sp[x, y]
            sp[x, y] = (min(255, r * 255 // a), min(255, gg * 255 // a), min(255, b * 255 // a), 255) if a > 110 else (0, 0, 0, 0)
    return small, {"gx": round(g[0] * k, 1), "gy": round(g[1] * k, 1), "ang": round(ang, 3), "color": color}

def main():
    os.makedirs(OUT, exist_ok=True)
    data = {"hero": {}, "weapons": {}}
    debug_rows = []
    for name, n in SHEETS.items():
        src = Image.open(f"pictures/hero_{name}.png").convert("RGBA")
        body_sheet = Image.new("RGBA", src.size, (0, 0, 0, 0))
        trail_sheet = Image.new("RGBA", src.size, (0, 0, 0, 0))
        dbg = Image.new("RGBA", src.size, (200, 220, 255, 255))
        grips = []
        for f in range(n):
            frame = src.crop((f * W, 0, (f + 1) * W, H))
            grip, scythe = analyse(frame, loose=name == "death")
            if name == "death" and f >= 5 and scythe:   # once it has landed it lies flat, blade towards him
                end = max(scythe, key=lambda p: (p[0], -p[1]))
                grip = [end[0], end[1], round(math.pi, 3)]
            grips.append(grip)
            clean = frame.copy()
            cp = clean.load()
            for p in scythe: cp[p] = (0, 0, 0, 0)
            fill_gaps(clean, scythe)
            trail = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            tp = trail.load()
            for y in range(H):
                for x in range(W):
                    if is_black(cp[x, y]): tp[x, y] = (255, 255, 255, 255); cp[x, y] = (0, 0, 0, 0)
            body_sheet.paste(clean, (f * W, 0))
            trail_sheet.paste(trail, (f * W, 0))
            dbg.alpha_composite(clean, (f * W, 0))
            if grip:
                d = ImageDraw.Draw(dbg)
                gx, gy, a = grip[0] + f * W, grip[1], grip[2]
                d.line([gx, gy, gx + math.cos(a) * 30, gy + math.sin(a) * 30], fill=(255, 0, 0, 255), width=2)
                d.rectangle([gx - 1, gy - 1, gx + 1, gy + 1], fill=(0, 160, 0, 255))
        body_sheet.save(f"{OUT}/hero_{name}.png", optimize=True)
        trail_sheet.save(f"{OUT}/trail_{name}.png", optimize=True)
        data["hero"][name] = grips
        debug_rows.append(dbg)
    sys.path.insert(0, os.path.dirname(__file__))
    from weapon_designs import DESIGNS
    drawn = {wid for ids in DESIGNS.values() for wid in ids}
    for fname in sorted(os.listdir("pictures/weapons")):
        if not fname.endswith(".png") or fname[:-4] in drawn: continue
        wid = fname[:-4]
        img, info = weapon_hold(f"pictures/weapons/{fname}")
        img.save(f"{OUT}/w_{wid}.png", optimize=True)
        data["weapons"][wid] = info
    with open("hold-data.js", "w") as fh:
        fh.write("// Generated by tools/make_hold.py: where the hero's hand grips his weapon in every frame\n")
        fh.write("// ([x, y, angle] in frame pixels, angle pointing from the hand to the blade; null = no weapon\n")
        fh.write("// in that frame) and where each shop weapon's picture is held (grip point, angle, length).\n")
        fh.write("window.STICKGO_HOLD = " + json.dumps(data, separators=(",", ":")) + ";\n")
    if len(sys.argv) > 1:
        sheet = Image.new("RGBA", (W * 10, H * len(debug_rows)), (255, 255, 255, 255))
        for i, r in enumerate(debug_rows): sheet.paste(r.crop((0, 0, min(r.width, W * 10), H)), (0, i * H))
        sheet.save(sys.argv[1])

main()
