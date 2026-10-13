"""Draws the four 32x32 pixel-art button icons (dash, slam, spin, ultimate) into pictures/icons/.
Run once; the game just shows the PNGs."""
from PIL import Image, ImageDraw
import math

S = 32
OUT = (22, 20, 30, 255)

def canvas(): return Image.new("RGBA", (S, S), (0, 0, 0, 0))

def outlined(im, draw_fn):
    """Draw the shape, then add a 1px dark outline around it."""
    shape = canvas(); draw_fn(ImageDraw.Draw(shape))
    px = shape.load(); o = canvas(); op = o.load()
    for y in range(S):
        for x in range(S):
            if px[x, y][3]:
                for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < S and 0 <= ny < S and not px[nx, ny][3]: op[nx, ny] = OUT
    im.alpha_composite(o); im.alpha_composite(shape)

def dash():
    im = canvas()
    def f(d):
        for i, x in enumerate((3, 11, 19)):    # three chevrons
            c = [(120,200,255,255), (80,168,255,255), (50,120,230,255)][i]
            d.polygon([(x,6),(x+7,16),(x,26),(x+4,26),(x+11,16),(x+4,6)], fill=c)
        for y in (9, 23): d.rectangle([1,y,6,y+1], fill=(200,230,255,255))   # speed lines
    outlined(im, f); return im

def slam():
    im = canvas()
    def f(d):
        d.polygon([(13,2),(19,2),(19,15),(24,15),(16,25),(8,15),(13,15)], fill=(255,211,77,255))   # down arrow
        d.rectangle([14,3,15,14], fill=(255,240,160,255))
        d.rectangle([3,27,28,29], fill=(190,120,40,255))   # ground
        d.polygon([(3,27),(7,23),(9,27)], fill=(255,150,60,255)); d.polygon([(28,27),(24,23),(22,27)], fill=(255,150,60,255))
    outlined(im, f); return im

def spin():
    im = canvas()
    def f(d):
        cx = cy = 16
        for a0, a1 in ((25, 135), (205, 315)):   # two arcs chasing each other
            for a in range(a0, a1, 4):
                x = cx + 10*math.cos(math.radians(a)); y = cy + 10*math.sin(math.radians(a))
                d.ellipse([x-1.6, y-1.6, x+1.6, y+1.6], fill=(255,211,77,255))
        for ang, (px, py) in ((135, (cx+10*math.cos(math.radians(135)), cy+10*math.sin(math.radians(135)))),
                              (315, (cx+10*math.cos(math.radians(315)), cy+10*math.sin(math.radians(315))))):
            t = math.radians(ang + 90)
            d.polygon([(px + 6*math.cos(t), py + 6*math.sin(t)), (px - 8*math.cos(math.radians(ang)), py - 8*math.sin(math.radians(ang))),
                       (px - 6*math.cos(t), py - 6*math.sin(t))], fill=(255,240,160,255))
        d.ellipse([13,13,18,18], fill=(255,150,60,255))
    outlined(im, f); return im

def ultimate():
    im = canvas()
    def f(d):
        pts = []
        for i in range(16):   # a starburst
            r = 15 if i % 2 == 0 else 7
            a = math.radians(i * 22.5 - 90)
            pts.append((16 + r*math.cos(a), 16 + r*math.sin(a)))
        d.polygon(pts, fill=(255,122,42,255))
        d.ellipse([9,9,22,22], fill=(255,211,77,255))
        d.ellipse([13,13,18,18], fill=(255,250,220,255))
    outlined(im, f); return im

for name, fn in (("dash", dash), ("slam", slam), ("spin", spin), ("ultimate", ultimate)):
    fn().save(f"pictures/icons/{name}.png")
sheet = Image.new("RGBA", (S*4*4, S*4), (200,200,205,255))
for i, n in enumerate(("dash","slam","spin","ultimate")):
    sheet.alpha_composite(Image.open(f"pictures/icons/{n}.png").resize((S*4,S*4), Image.NEAREST), (i*S*4, 0))
sheet.save("C:/Users/Kim/AppData/Local/Temp/icons_preview.png")
