"""Builds pictures/hero_death.png: the hero's death animation (10 frames, 128x64, facing right).
Starts from the hit3 flinch frame, then rotates his body (without the scythe) back onto the ground
while the scythe is flung out of his hand. Rotations are done at 4x with nearest-neighbour and
thresholded back down, so every frame stays crisp pixel art."""
import math
from PIL import Image

W, H, S = 128, 64, 4
src = Image.open("pictures/hero_hit3.png").convert("RGBA").crop((0, 0, W, H))
px = src.load()

body = Image.new("RGBA", (W, H)); tool = Image.new("RGBA", (W, H))
for y in range(H):
    for x in range(W):
        p = px[x, y]
        if p[3] < 128: continue
        (tool if p[0] < 70 and p[1] < 70 and p[2] < 70 else body).putpixel((x, y), p)

bb = body.getbbox()                      # feet at the bottom, pivot between the feet
PIV = ((bb[0] + bb[2]) / 2, bb[3])
tb = tool.getbbox()
TC = ((tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2)

def transform(img, pivot, angle, dx, dy):
    """Rotate img by angle degrees counter-clockwise about pivot, then shift by (dx, dy)."""
    big = img.resize((W * S, H * S), Image.NEAREST)
    big = big.rotate(angle, resample=Image.NEAREST, center=(pivot[0] * S, pivot[1] * S))
    out = big.resize((W, H), Image.BOX)
    o = Image.new("RGBA", (W, H))
    po, so = out.load(), o.load()
    for y in range(H):
        for x in range(W):
            p = po[x, y]
            if p[3] > 110:
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H: so[nx, ny] = (p[0], p[1], p[2], 255)
    return o

def lowest(img):
    b = img.getbbox(); return b[3] if b else 0

GROUND = bb[3]
# (body angle, hop, body shift right, scythe angle, scythe centre x, scythe centre y)
# He falls backwards (head to the left); the scythe is tossed up and forward and lands to his right.
FRAMES = [
    (0,   0,  0,    0, None, None),
    (8,   5,  0,  -20,   46,   16),
    (20,  9,  3,  -60,   56,    6),
    (38,  5,  8, -110,   68,    4),
    (60,  1, 14, -170,   80,   14),
    (80,  0, 20, -230,   92,   30),
    (90, -1, 24, -310,  102,   46),   # lands: a squash
    (86,  3, 24, -320,  104,   40),   # small bounce
    (90,  0, 24, -325,  104,   49),
    (90,  0, 24, -325,  104,   49),
]
sheet = Image.new("RGBA", (W * len(FRAMES), H))
for i, (ba, lift, bx, sa, tx, ty) in enumerate(FRAMES):
    b = transform(body, PIV, ba, 0, 0)
    b = transform(b, PIV, 0, bx, GROUND - lowest(b) - lift)    # rest on the ground, minus the hop
    if tx is None: t = tool
    else:
        t = transform(tool, TC, sa, round(tx - TC[0]), round(ty - TC[1]))
        if i >= 8: t = transform(t, TC, 0, 0, GROUND - lowest(t))   # settles on the ground
    f = Image.new("RGBA", (W, H))
    f.alpha_composite(t); f.alpha_composite(b)
    sheet.paste(f, (i * W, 0))
sheet.save("pictures/hero_death.png")
print(sheet.size)
