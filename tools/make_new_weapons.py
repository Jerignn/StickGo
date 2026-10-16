"""Draws the spears, axes, daggers and scythes (tools/weapon_designs.py) for the game:
  pictures/weapons/<id>.png   the shop / inventory picture (rare and legendary ones glow and sparkle)
  pictures/hold/w_<id>.png    the small picture in the hero's hand
and adds their grip points to hold-data.js (the swords' entries there come from make_hold.py).
Usage: python tools/make_new_weapons.py [contact-sheet.png]"""
import json, math, os, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import weapon_art
import weapon_designs as D

# How long each kind is in his hand, in sprite pixels (the scythe in his sprites is about 36)
HELD_LEN = {"spear": 54, "axe": 40, "dagger": 26, "scythe": 44}
LEGEND_HELD = 1.18          # legendaries are drawn bigger in his hand too
SHOP_SCALE = {"common": 0.62, "uncommon": 0.64, "rare": 0.68, "legendary": 0.74}
RARITY = ["common", "common", "uncommon", "uncommon", "rare", "rare", "legendary", "legendary", "legendary", "legendary"]
# Glow and sparkle colours of the rare and legendary ones
GLOW = {
    "storm_trident": (120, 190, 255), "crimson_halberd": (255, 60, 70), "gungnir": (255, 214, 90),
    "abyss_lance": (180, 100, 255), "dragonfire_pike": (255, 120, 30), "zeus_trident": (255, 240, 80),
    "frostbite_axe": (150, 220, 255), "ember_axe": (255, 120, 40), "titans_wrath": (255, 210, 80),
    "void_reaver": (200, 90, 255), "worldsplitter": (255, 90, 20), "stormbreaker": (110, 220, 255),
    "night_dirk": (150, 90, 255), "ice_stiletto": (170, 230, 255), "demon_fang": (255, 40, 50),
    "starfall": (170, 150, 255), "phoenix_talon": (255, 140, 40), "phase_blade": (60, 230, 255),
    "crescent_moon": (200, 220, 255), "winter_reaper": (150, 220, 255), "grim_death": (160, 100, 255),
    "blood_moon": (255, 40, 60), "soul_harvester": (120, 255, 190), "eclipse_scythe": (255, 220, 100),
}


def main_colour(img):
    px = [img.getpixel((x, y)) for y in range(img.height) for x in range(img.width)]
    bright = [p for p in px if p[3] > 200 and sum(p[:3]) > 260]
    if not bright:
        return "#cccccc"
    return "#%02x%02x%02x" % tuple(sum(p[i] for p in bright) // len(bright) for i in range(3))


def main():
    with open("hold-data.js") as fh:
        src = fh.read()
    hold = json.loads(src[src.index("{"):src.rindex("}") + 1])
    sheet_rows = []
    for kind, ids in D.DESIGNS.items():
        row = []
        for wid, rarity in zip(ids, RARITY):
            parts, length, grip_u = getattr(D, wid)()
            g = GLOW.get(wid)
            fx = None
            if g:
                legend = rarity == "legendary"
                fx = dict(glow=g, glow_size=4 if legend else 2, spark_count=14 if legend else 6,
                          sparks=[g, (255, 255, 255), tuple(min(255, c + 60) for c in g)])
            shop = weapon_art.render(parts, length, SHOP_SCALE[rarity], fx, seed=len(wid))
            shop.save(f"pictures/weapons/{wid}.png", optimize=True)
            held_len = HELD_LEN[kind] * (LEGEND_HELD if rarity == "legendary" else 1)
            k = held_len / length
            full, (ax, ay), ang, _ = weapon_art.render_uncropped(parts, length, k)
            bb = full.getbbox()
            held = full.crop(bb)
            held.save(f"pictures/hold/w_{wid}.png", optimize=True)
            gx = ax + grip_u * k / math.sqrt(2) - bb[0]
            gy = ay - grip_u * k / math.sqrt(2) - bb[1]
            hold["weapons"][wid] = {"gx": round(gx, 1), "gy": round(gy, 1), "ang": round(ang, 3),
                                    "color": "#%02x%02x%02x" % g if g else main_colour(held),
                                    "blade": round((length - grip_u) * k * 0.95, 1)}   # grip to tip, for the held effects
            row.append(shop)
        sheet_rows.append(row)
    lines = src.split("\n")
    head = [l for l in lines if l.startswith("//")]
    with open("hold-data.js", "w", newline="\n") as fh:
        fh.write("\n".join(head) + "\n")
        fh.write("window.STICKGO_HOLD = " + json.dumps(hold, separators=(",", ":")) + ";\n")
    if len(sys.argv) > 1:
        W = max(sum(i.width + 8 for i in r) for r in sheet_rows)
        H = sum(max(i.height for i in r) + 8 for r in sheet_rows)
        out = Image.new("RGBA", (W, H), (28, 26, 42, 255))
        y = 0
        for r in sheet_rows:
            x, h = 0, max(i.height for i in r)
            for i in r:
                out.alpha_composite(i, (x, y + h - i.height))
                x += i.width + 8
            y += h + 8
        out.resize((out.width * 3, out.height * 3), Image.NEAREST).save(sys.argv[1])
    print("drew", sum(len(r) for r in sheet_rows), "weapons")


main()
