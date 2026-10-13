"""Finds the head (centre x, y and radius, in frame pixels) in every hero sprite frame.
Prints the HERO_HEADS table that index.html uses to place accessories."""
import json
from PIL import Image

SHEETS = {"idle": 4, "run": 10, "jump": 3, "jump_peak": 3, "fall": 4, "dash": 11,
          "attack1": 10, "attack2": 8, "attack3": 10, "skill1": 9, "skill2": 19, "skill3": 25,
          "start_skill3": 3, "hit1": 3, "hit3": 3, "death": 10}
W, H = 128, 64

def yellow(p):
    return p[3] > 128 and p[0] > 150 and p[1] > 140 and p[2] < 130

def head_of(im, f):
    px = im.load()
    rows = []
    for y in range(H):
        best = None; run = 0; start = 0
        for x in range(W):
            if yellow(px[f * W + x, y]):
                if run == 0: start = x
                run += 1
                if run >= 9 and (best is None or run > best[1]): best = (start, run)
            else:
                run = 0
        rows.append(best)
    y0 = next((y for y, r in enumerate(rows) if r), None)
    if y0 is None: return None
    y1 = y0
    while y1 + 1 < H and rows[y1 + 1] and y1 - y0 < 13: y1 += 1
    if y1 - y0 < 6: return None
    cs = [rows[y][0] + rows[y][1] / 2 for y in range(y0, y1 + 1)]
    return [round(sum(cs) / len(cs)), round((y0 + y1 + 1) / 2)]

out = {}
for name, n in SHEETS.items():
    im = Image.open(f"pictures/hero_{name}.png").convert("RGBA")
    out[name] = [head_of(im, f) for f in range(n)]
    for f in range(n):   # a frame with no clear head (rotated poses) borrows the nearest one that has one
        if out[name][f] is None:
            near = sorted((abs(g - f), g) for g in range(n) if out[name][g])
            out[name][f] = out[name][near[0][1]] if near else [58, 15]
print(json.dumps(out, separators=(",", ":")))

if __name__ == "__main__" and len(__import__("sys").argv) > 1:   # debug: draw the found heads onto a contact sheet
    from PIL import ImageDraw
    rows = []
    for name, n in SHEETS.items():
        im = Image.open(f"pictures/hero_{name}.png").convert("RGBA")
        bg = Image.new("RGBA", im.size, (200, 220, 255, 255)); bg.alpha_composite(im)
        d = ImageDraw.Draw(bg)
        for f, (x, y) in enumerate(out[name]):
            d.ellipse([f * W + x - 6, y - 6, f * W + x + 6, y + 6], outline=(255, 0, 0, 255))
        rows.append(bg)
    sheet = Image.new("RGBA", (W * 12, H * len(rows)), (255, 255, 255, 255))
    for i, r in enumerate(rows): sheet.paste(r.crop((0, 0, min(r.width, W * 12), H)), (0, i * H))
    sheet.save(__import__("sys").argv[1])
