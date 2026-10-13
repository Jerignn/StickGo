"""Cuts the shop weapons out of the Weapons2d.png sheet (one row per rarity, a dark grid behind
them) into pictures/weapons/<id>.png, with the background made transparent.
Usage: python tools/cut_weapons.py <path to Weapons2d.png> [debug.png]"""
import sys
from PIL import Image, ImageDraw

BG = (17, 22, 34)
BANDS = {   # rarity -> (top, bottom) rows of the sheet, between the divider lines
    "common": (0, 74),
    "uncommon": (85, 160),
    "rare": (170, 246),
    "legendary": (256, 349),
}
CELLS = {   # rarity -> the x edges of each weapon's cell
    "common": [100, 211, 332, 452, 572, 700],
    "uncommon": [100, 211, 332, 452, 572, 700],
    "rare": [100, 222, 367, 517, 700],
    "legendary": [100, 177, 252, 326, 401, 477, 552, 627, 700],
}
IDS = {
    "common": ["rusty", "wooden", "cleaver", "cutlass", "iron"],
    "uncommon": ["serrated", "frost_staff", "void_blade", "vine", "bone"],
    "rare": ["inferno", "shadow", "gale", "glacier"],
    "legendary": ["phoenix", "plasma", "nebula", "seraph", "ember_feather", "thunder", "toxic", "gearblade"],
}

def is_bg(p):
    # the dark navy, its faint grid lines and the near-black shading around it
    return sum(abs(a - b) for a, b in zip(p[:3], BG)) < 34

def drop_specks(img, smallest=4):
    """Clears clusters of fewer than `smallest` pixels (noise left over from the background)."""
    p = img.load()
    seen = set()
    for y in range(img.height):
        for x in range(img.width):
            if (x, y) in seen or p[x, y][3] == 0: continue
            group, todo = [], [(x, y)]
            seen.add((x, y))
            while todo:
                cx, cy = todo.pop()
                group.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < img.width and 0 <= ny < img.height and (nx, ny) not in seen and p[nx, ny][3]:
                        seen.add((nx, ny)); todo.append((nx, ny))
            if len(group) < smallest:
                for g in group: p[g] = (0, 0, 0, 0)

def main():
    src = Image.open(sys.argv[1]).convert("RGBA")
    px = src.load()
    import os
    os.makedirs("pictures/weapons", exist_ok=True)
    debug = Image.new("RGBA", src.size, (0, 0, 0, 0))
    debug.paste(src)
    d = ImageDraw.Draw(debug)
    for rarity, (y0, y1) in BANDS.items():
        edges = CELLS[rarity]
        runs = list(zip(edges, edges[1:]))
        for wid, (a, b) in zip(IDS[rarity], runs):
            box = src.crop((a, y0, b, y1))
            bp = box.load()
            for yy in range(box.height):
                for xx in range(box.width):
                    if is_bg(bp[xx, yy]): bp[xx, yy] = (0, 0, 0, 0)
            drop_specks(box)
            bb = box.getbbox()
            box = box.crop(bb)
            box.save(f"pictures/weapons/{wid}.png")
            d.rectangle([a + bb[0], y0 + bb[1], a + bb[2], y0 + bb[3]], outline=(255, 0, 255, 255))
    if len(sys.argv) > 2:
        debug.save(sys.argv[2])

main()
