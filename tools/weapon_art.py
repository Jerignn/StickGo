"""A tiny procedural pixel-art engine for the shop weapons (spears, axes, daggers, scythes).

A weapon is a list of parts drawn in weapon space: u runs along the weapon from the end of the
handle (u = 0) to the tip, v runs across it (v > 0 is the upper-left side once it is drawn
diagonally, handle bottom-left and tip top-right like the sword sheet). Every part is a shape with
its own little frame, so blades can be angled, curved, widened and rounded; each pixel is shaded
by where it sits across the part (dark on one side, light on the other, a bright cutting edge).
After the parts: a dark outline, then (for the shop picture) glow and sparkles.

render(parts, length, ...) draws at any size, so the same design makes the big shop picture and
the small picture the hero holds."""
import math, random
from PIL import Image

OUTLINE = (16, 12, 24, 255)


def mix(a, b, k):
    return tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))


def hsh(x, y, seed=0):
    """A stable pseudo-random number in [0, 1) for a pixel."""
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536


class Part:
    """A shape along its own axis: starts at (u, v) in weapon space, points `ang` radians away from
    the weapon's axis (0 = towards the tip, +pi/2 = towards +v) and is `length` long.
    width(t) and center(t) (t from 0 to 1 along it) give its thickness and how far its middle bends
    sideways. round_end > 0 rounds the far end (a curved axe edge). pal = (dark, mid, light, shine).
    edge: which side is the sharp one (+1, -1, 0 for both, None for none).
    paint(t, s, x, y, base) may replace the colour (runes, cracks, stars...)."""

    def __init__(self, u, v, ang, length, width, pal, center=None, edge=None, round_end=0.0,
                 round_start=0.0, paint=None, ridge=False, alpha=255):
        self.u, self.v, self.ang, self.length = u, v, ang, length
        self.width = width if callable(width) else (lambda t, w=width: w)
        self.center = center or (lambda t: 0.0)
        self.pal, self.edge, self.round_end, self.round_start = pal, edge, round_end, round_start
        self.paint, self.ridge, self.alpha = paint, ridge, alpha

    def scaled(self, k):
        p = Part(self.u * k, self.v * k, self.ang, self.length * k,
                 (lambda t, f=self.width: max(1.15, f(t) * k)), self.pal,
                 (lambda t, f=self.center: f(t) * k), self.edge, self.round_end, self.round_start,
                 self.paint, self.ridge, self.alpha)
        return p

    def color(self, u, v, x, y):
        du, dv = u - self.u, v - self.v
        ca, sa = math.cos(self.ang), math.sin(self.ang)
        t = du * ca + dv * sa
        off = -du * sa + dv * ca
        if t < -0.5 or t > self.length + 0.5:
            return None
        t01 = min(1.0, max(0.0, t / self.length)) if self.length else 0.0
        w = self.width(t01) / 2
        if w <= 0:
            return None
        s = (off - self.center(t01)) / w
        if abs(s) > 1:
            return None
        if self.round_end and t01 > 1 - self.round_end * s * s:
            return None
        if self.round_start and t01 < self.round_start * s * s:
            return None
        d, m, l, h = self.pal
        if self.edge is not None and ((self.edge >= 0 and s > 0.72) or (self.edge <= 0 and s < -0.72)):
            c = h
        elif s > 0.4:
            c = l
        elif s < -0.45:
            c = d
        else:
            c = m
        if self.ridge and abs(s) < 0.16:
            c = l
        if self.paint:
            c = self.paint(t01, s, x, y, c) or c
        return c


class Disc:
    """A round piece (pommel, gem, ring). hole > 0 makes it a ring."""

    def __init__(self, u, v, r, pal, hole=0.0, paint=None):
        self.u, self.v, self.r, self.pal, self.hole, self.paint = u, v, r, pal, hole, paint

    def scaled(self, k):
        return Disc(self.u * k, self.v * k, max(1.0, self.r * k), self.pal, self.hole * k, self.paint)

    def color(self, u, v, x, y):
        du, dv = u - self.u, v - self.v
        d = math.hypot(du, dv)
        if d > self.r or d < self.hole:
            return None
        dk, m, l, h = self.pal
        # light from the upper left (+v, and towards the tip)
        lit = (du * 0.5 + dv * 0.85) / max(self.r, 0.01)
        c = h if lit > 0.55 and d < self.r * 0.8 else l if lit > 0.1 else m if lit > -0.5 else dk
        if self.paint:
            c = self.paint(d / self.r, lit, x, y, c) or c
        return c


def render(parts, length, scale=1.0, fx=None, seed=1, pad=3):
    """Draws the weapon diagonally (handle bottom-left, tip top-right).
    length: its design length along the axis; scale: size factor for this picture.
    fx: None, or dict(glow=(r, g, b), glow_size=px, sparks=[colours], spark_count=n) for the shop
    picture. Returns the picture, cropped to the weapon."""
    ps = [p.scaled(scale) for p in parts]
    L = length * scale
    # how far the parts reach to either side, to size the picture
    side = 0
    for p in ps:
        if isinstance(p, Disc):
            side = max(side, abs(p.v) + p.r)
        else:
            for i in range(11):
                t = i / 10
                ca, sa = math.cos(p.ang), math.sin(p.ang)
                pt_v = p.v + sa * p.length * t
                side = max(side, abs(pt_v) + abs(ca) * (abs(p.center(t)) + p.width(t) / 2) + 1)
    glow_px = (fx or {}).get("glow_size", 0)
    margin = pad + glow_px + 2
    span = (L + 2 * side) / math.sqrt(2)
    size = int(math.ceil(span + 2 * margin + 2))
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    # handle end sits so the whole weapon is centred
    ax = margin + side / math.sqrt(2) + 1
    ay = size - ax
    dux, duy = 1 / math.sqrt(2), -1 / math.sqrt(2)      # along the weapon
    dvx, dvy = -1 / math.sqrt(2), -1 / math.sqrt(2)     # across it (up-left)
    for y in range(size):
        for x in range(size):
            rx, ry = x + 0.5 - ax, y + 0.5 - ay
            u = rx * dux + ry * duy
            v = rx * dvx + ry * dvy
            col = None
            for p in ps:
                c = p.color(u, v, x, y)
                if c is not None:
                    col = c
            if col is not None:
                px[x, y] = tuple(col[:3]) + (255,)
    # outline
    solid = {(x, y) for y in range(size) for x in range(size) if px[x, y][3]}
    for x, y in list(solid):
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < size and 0 <= ny < size and (nx, ny) not in solid and px[nx, ny][3] == 0:
                px[nx, ny] = OUTLINE
    if fx:
        body = {(x, y) for y in range(size) for x in range(size) if px[x, y][3]}
        g = fx.get("glow")
        if g and glow_px:
            for y in range(size):
                for x in range(size):
                    if px[x, y][3]:
                        continue
                    best = 99
                    for dy in range(-glow_px, glow_px + 1):
                        for dx in range(-glow_px, glow_px + 1):
                            if (x + dx, y + dy) in body:
                                best = min(best, math.hypot(dx, dy))
                    if best <= glow_px:
                        a = int(150 * (1 - (best - 1) / glow_px) ** 1.4)
                        if a > 8:
                            px[x, y] = g + (a,)
        rnd = random.Random(seed)
        sparks = fx.get("sparks") or []
        tries = 0
        placed = 0
        while placed < fx.get("spark_count", 0) and tries < 4000:
            tries += 1
            x, y = rnd.randrange(2, size - 2), rnd.randrange(2, size - 2)
            # near the upper (blade) half, a little away from the weapon
            if y > size * 0.75 and x < size * 0.4:
                continue
            near = min((math.hypot(x - bx, y - by) for bx, by in rnd.sample(sorted(body), min(60, len(body)))), default=99)
            if not (3 <= near <= 9) or px[x, y][3] > 160:
                continue
            c = rnd.choice(sparks) + (255,)
            big = rnd.random() < 0.35
            pts = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)] if big else [(0, 0)]
            if big and rnd.random() < 0.5:
                pts += [(2, 0), (-2, 0), (0, 2), (0, -2)]
            for dx, dy in pts:
                if 0 <= x + dx < size and 0 <= y + dy < size:
                    px[x + dx, y + dy] = c if (dx, dy) == (0, 0) else c[:3] + (200,)
            placed += 1
    return img.crop(img.getbbox())


def render_uncropped(parts, length, scale):
    """Like render() without effects or cropping, returning where the handle end sits."""
    ps = [p.scaled(scale) for p in parts]
    L = length * scale
    side = 0
    for p in ps:
        if isinstance(p, Disc):
            side = max(side, abs(p.v) + p.r)
        else:
            for i in range(11):
                t = i / 10
                ca, sa = math.cos(p.ang), math.sin(p.ang)
                pt_v = p.v + sa * p.length * t
                side = max(side, abs(pt_v) + abs(ca) * (abs(p.center(t)) + p.width(t) / 2) + 1)
    margin = 3
    size = int(math.ceil((L + 2 * side) / math.sqrt(2) + 2 * margin + 2))
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    ax = margin + side / math.sqrt(2) + 1
    ay = size - ax
    s2 = 1 / math.sqrt(2)
    for y in range(size):
        for x in range(size):
            rx, ry = x + 0.5 - ax, y + 0.5 - ay
            u = (rx - ry) * s2
            v = (-rx - ry) * s2
            col = None
            for p in ps:
                c = p.color(u, v, x, y)
                if c is not None:
                    col = c
            if col is not None:
                px[x, y] = tuple(col[:3]) + (255,)
    solid = {(x, y) for y in range(size) for x in range(size) if px[x, y][3]}
    for x, y in list(solid):
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < size and 0 <= ny < size and (nx, ny) not in solid and px[nx, ny][3] == 0:
                px[nx, ny] = OUTLINE
    return img, (ax, ay), -math.pi / 4, L
