"""The spear, axe, dagger and scythe designs drawn by tools/make_new_weapons.py (see weapon_art.py
for how a part is described). Each design returns (parts, length, grip_u): grip_u is where along
the weapon his hand holds it."""
import math
from weapon_art import Part, Disc, hsh, mix

PI = math.pi

# Palettes: (dark, mid, light, shine)
WOOD = ((70, 42, 22), (118, 74, 38), (156, 104, 58), (186, 136, 86))
DARKWOOD = ((40, 24, 18), (72, 44, 30), (102, 66, 44), (130, 90, 60))
LEATHER = ((52, 30, 20), (88, 54, 34), (120, 78, 50), (146, 100, 66))
IRON = ((64, 68, 80), (112, 118, 132), (164, 170, 184), (226, 232, 240))
STEEL = ((84, 92, 110), (146, 156, 176), (202, 210, 226), (250, 252, 255))
RUST = ((90, 46, 24), (140, 80, 44), (176, 118, 72), (206, 160, 112))
GOLD = ((136, 86, 8), (212, 158, 38), (250, 208, 88), (255, 246, 196))
BRONZE = ((104, 60, 22), (164, 104, 44), (206, 148, 76), (240, 196, 130))
BONE = ((140, 128, 100), (200, 190, 162), (232, 224, 200), (255, 252, 238))
REDCLOTH = ((110, 14, 20), (180, 30, 36), (226, 70, 64), (255, 140, 120))
ICE = ((50, 110, 170), (110, 184, 232), (186, 232, 255), (244, 252, 255))
FIRE = ((150, 30, 8), (232, 92, 20), (255, 168, 40), (255, 240, 150))
LAVA = ((120, 16, 4), (220, 64, 10), (255, 150, 30), (255, 236, 140))
VOID = ((28, 8, 58), (78, 28, 148), (140, 80, 222), (224, 186, 255))
SHADOW = ((18, 14, 28), (44, 38, 62), (78, 70, 108), (140, 128, 182))
OBSIDIAN = ((14, 12, 20), (34, 30, 44), (58, 52, 74), (110, 100, 140))
TOXIC = ((18, 84, 36), (46, 164, 76), (116, 228, 136), (208, 255, 214))
VENOM = ((40, 70, 20), (90, 140, 30), (150, 200, 60), (220, 250, 140))
BOLT = ((150, 116, 0), (240, 208, 36), (255, 240, 116), (255, 255, 232))
STORM = ((22, 44, 96), (46, 96, 186), (96, 160, 240), (200, 230, 255))
NEON = ((0, 110, 150), (36, 212, 255), (150, 244, 255), (255, 255, 255))
PINKNEON = ((140, 0, 110), (255, 60, 200), (255, 150, 230), (255, 240, 252))
BLOOD = ((80, 0, 10), (160, 12, 28), (222, 46, 58), (255, 136, 136))
COSMIC = ((14, 10, 50), (40, 30, 110), (78, 60, 180), (170, 150, 255))
GHOST = ((40, 120, 90), (90, 220, 160), (170, 255, 210), (240, 255, 248))
MOON = ((96, 106, 140), (170, 182, 214), (220, 228, 248), (255, 255, 255))
WHITE = ((170, 176, 196), (220, 224, 236), (245, 247, 252), (255, 255, 255))
PURPLECLOTH = ((50, 14, 80), (96, 30, 150), (140, 70, 200), (190, 140, 240))
EMBER = ((120, 30, 10), (200, 70, 20), (255, 130, 40), (255, 220, 120))
GREENCLOTH = ((24, 70, 30), (44, 120, 52), (80, 170, 84), (150, 220, 150))


# --- Paint helpers ---------------------------------------------------------------------------
def bands(length, period, col, width=2, start=0.0, end=1.0):
    """Wrapped bands across a handle."""
    def f(t, s, x, y, c):
        if start <= t <= end and int(t * length) % period < width:
            return col
    return f


def stars(seed, col=(255, 255, 255), dens=0.06):
    """Little stars scattered inside a blade (cosmic)."""
    def f(t, s, x, y, c):
        if abs(s) < 0.8 and hsh(x, y, seed) < dens:
            return col if hsh(x, y, seed + 1) < 0.5 else mix(col, c, 0.4)
    return f


def cracks(seed, col, dens=0.16):
    """Glowing cracks (lava in stone, runes)."""
    def f(t, s, x, y, c):
        n = hsh(x // 2, y // 2, seed)
        if abs(s) < 0.85 and (n < dens or (abs(s) < 0.15 and n < 0.5)):
            return col
    return f


def rune_line(length, period, col):
    """A glowing dashed line down the middle (runes)."""
    def f(t, s, x, y, c):
        if abs(s) < 0.22 and int(t * length) % period < period - 2:
            return col
    return f


def zigzag(length, col, amp=0.5, freq=5):
    """A lightning line down the blade."""
    def f(t, s, x, y, c):
        z = amp * (2 * abs((t * freq) % 1 - 0.5) * 2 - 1)
        if abs(s - z) < 0.24:
            return col
    return f


def tip_fade(col, start=0.7):
    """The colour shifts towards col near the end of the part."""
    def f(t, s, x, y, c):
        if t > start:
            return mix(c, col, min(1, (t - start) / (1 - start)) * 0.7)
    return f


def chain(*fs):
    def f(t, s, x, y, c):
        for g in fs:
            r = g(t, s, x, y, c)
            if r is not None:
                c = r
        return c
    return f


# --- Building blocks -------------------------------------------------------------------------
def handle(length, w, pal, wrap=None, period=6):
    return Part(0, 0, 0, length, w, pal, paint=bands(length, period, wrap[0]) if wrap else None)


def leaf(u, length, wmax, pal, edge=0, ridge=True, paint=None, sharp=1.0):
    """A spear / dagger head: widens quickly, then narrows to a point."""
    def w(t):
        return max(0.0, wmax * (math.sin(PI * min(1.0, t * 1.6)) if t < 0.31 else (1 - t) ** sharp / (0.69 ** sharp)))
    return Part(u, 0, 0, length, w, pal, edge=edge, ridge=ridge, paint=paint)


def blade(u, length, w0, w1, pal, edge=0, ridge=True, paint=None, point=0.18, v=0.0, ang=0.0, center=None):
    """A straight blade from width w0 to w1, coming to a point over its last `point`."""
    def w(t):
        base = w0 + (w1 - w0) * t
        return base * min(1.0, (1 - t) / point) if t > 1 - point else base
    return Part(u, v, ang, length, w, pal, edge=edge, ridge=ridge, paint=paint, center=center)


def guard(u, half, w, pal, curve=0.0):
    """A crossguard across the weapon at u."""
    return Part(u, -half, PI / 2, half * 2, w, pal, center=lambda t: -curve * (2 * t - 1) ** 2)


def crescent(u, v, ang, length, w0, pal, bend, edge=-1, paint=None, w_end=0.6):
    """A curved blade (scythe, axe edge): bends sideways by `bend` at its far end."""
    return Part(u, v, ang, length, lambda t: w_end + (w0 - w_end) * (1 - t) ** 0.85, pal,
                center=lambda t: bend * t * t, edge=edge, ridge=False, paint=paint)


def axe_head(u, v_dir, reach, w_in, w_out, pal, edge_pal=None, paint=None, roundness=0.35, offset=1.5):
    """An axe blade sticking out sideways (v_dir = +1 or -1), widening to a rounded edge."""
    ang = PI / 2 * v_dir
    parts = [Part(u, offset * v_dir, ang, reach, lambda t: w_in + (w_out - w_in) * t ** 1.3, pal,
                  round_end=roundness, edge=None, paint=paint)]
    if edge_pal:   # a bright honed edge along the rim
        parts.append(Part(u, (offset + reach * 0.84) * v_dir, ang, reach * 0.16,
                          lambda t: w_out * 0.98, edge_pal, round_end=roundness * 3.2, edge=None))
    return parts


def gem(u, v, r, pal):
    return Disc(u, v, r, pal)


def flame(u, v, ang, length, w0, pal, seed=0, wiggle=2.0):
    """A licking flame: tapers and wobbles."""
    return Part(u, v, ang, length, lambda t: w0 * (1 - t) ** 0.7 + 0.4, pal,
                center=lambda t: wiggle * math.sin(t * 7 + seed) * t, edge=None, ridge=False)


def wing(u, v_dir, length, pal, feathers=5, fan=1.1, w=4.2):
    """A feathered wing on the guard: feathers fan out sideways and sweep back towards the handle,
    the first (outermost) one longest."""
    parts = []
    for i in range(feathers):
        a = (PI / 2 + 0.25 + i * fan / feathers) * v_dir
        parts.append(Part(u - i * 1.2, 1.5 * v_dir, a, length * (1 - i * 0.13), lambda t, w=w: w * (1 - t) ** 0.6 + 0.8,
                          pal, center=lambda t, d=v_dir: -d * 2.5 * t * t, edge=1 if v_dir > 0 else -1, ridge=False))
    return parts


def spikes(u, v_dir, n, length, gap, pal, ang=0.5, w=3.4):
    """A row of spikes along one side (serrations, thorns, crown points)."""
    return [Part(u + i * gap, 0, (PI / 2 - ang) * v_dir, length, lambda t, w=w: w * (1 - t) + 0.3, pal, ridge=False)
            for i in range(n)]




# --- The designs (name = weapon id) -----------------------------------------------------------
def GLOWY(c):
    """A flat, single-colour palette (energy, the cores of gems)."""
    return (c,) * 4


# SPEARS ------------------------------------------------------------------------------------------
def wooden_spear():
    return [handle(92, 3.4, WOOD, (DARKWOOD[0],), 11), Part(86, 0, 0, 7, 4.6, LEATHER),
            leaf(92, 20, 8, IRON)], 112, 22


def iron_pike():
    return [handle(96, 3.2, DARKWOOD, (IRON[0],), 14), Disc(1.5, 0, 2.6, IRON), Part(88, 0, 0, 10, 5, IRON),
            leaf(97, 26, 9, STEEL, sharp=1.4)], 122, 22


def bronze_glaive():
    return [handle(90, 3.4, DARKWOOD, (BRONZE[1],), 10), Disc(1.5, 0, 2.8, BRONZE), Part(84, 0, 0, 9, 5.4, BRONZE),
            crescent(90, 0, 0.06, 30, 11, BRONZE, 4, edge=1)], 120, 22


def frost_lance():
    return [handle(92, 3.4, ICE, (WHITE[2],), 9), Disc(1.5, 0, 3, ICE), Part(86, 0, 0, 8, 6, WHITE),
            *spikes(87, 1, 2, 6, 3, ICE, 0.9), *spikes(87, -1, 2, 6, 3, ICE, 0.9),
            leaf(93, 28, 10, ICE, paint=tip_fade((255, 255, 255), 0.5))], 124, 22


def storm_trident():
    def tine(v, ln):
        return Part(98, v, 0, ln, lambda t: 3.4 * (1 - t) + 0.6, STORM, ridge=True)
    return [handle(92, 3.6, STORM, (BOLT[1],), 9), Disc(1.5, 0, 3, STORM),
            Part(86, -8, PI / 2, 16, 4, STORM, center=lambda t: -2.5 * (2 * t - 1) ** 2),
            tine(-7, 22), tine(7, 22), tine(0, 30),
            Part(104, 0, 0, 20, 1.6, GLOWY(BOLT[2]), center=lambda t: 1.2 * math.sin(t * 18))], 132, 24


def crimson_halberd():
    return [handle(98, 3.6, OBSIDIAN, (BLOOD[1],), 10), Disc(1.5, 0, 3, BLOOD),
            *axe_head(84, 1, 16, 10, 22, BLOOD, edge_pal=GLOWY((255, 150, 150))),
            Part(88, -2, -PI / 2, 9, lambda t: 5 * (1 - t) + 0.4, OBSIDIAN),
            leaf(98, 28, 9, BLOOD, sharp=1.3)], 130, 24


def gungnir():
    sun = GLOWY((255, 236, 140))
    return [handle(104, 4.4, GOLD, (WHITE[1],), 9), Disc(2.2, 0, 4.6, GOLD), Disc(2.2, 0, 2.2, FIRE),
            *wing(98, 1, 42, WHITE, 7, 1.3, 7), *wing(98, -1, 42, WHITE, 7, 1.3, 7),
            Part(94, 0, 0, 14, 11, GOLD, ridge=True),
            leaf(104, 56, 28, WHITE, paint=tip_fade((255, 226, 110), 0.45), sharp=1.25),
            leaf(108, 44, 11, GOLD, ridge=False, paint=rune_line(44, 5, sun[0])),
            Disc(100, 0, 8, GOLD), gem(100, 0, 6, FIRE), gem(100, 0, 2.6, sun)], 166, 30


def abyss_lance():
    core = GLOWY((235, 190, 255))
    return [handle(104, 4.2, OBSIDIAN, (VOID[2],), 7), Disc(2, 0, 4.4, VOID), Disc(2, 0, 2, core),
            *[Part(70 + i * 9, -6 - i, PI / 2, 12 + 2 * i, 2.6, VOID, center=lambda t: 3 * math.sin(t * PI)) for i in range(3)],
            Part(94, 0, 0, 12, 12, OBSIDIAN, ridge=True),
            *spikes(94, 1, 4, 18, 4, VOID, 1.05, 5), *spikes(94, -1, 4, 18, 4, VOID, 1.05, 5),
            leaf(104, 58, 26, VOID, paint=chain(stars(7, (255, 230, 255), 0.07), rune_line(58, 4, core[0])), sharp=1.1),
            gem(100, 0, 6.4, VOID), gem(100, 0, 3, core)], 168, 30


def dragonfire_pike():
    return [handle(102, 4.4, LAVA, (OBSIDIAN[1],), 6), Disc(2, 0, 4.6, OBSIDIAN),
            flame(96, 5, 1.9, 36, 9, FIRE, 1, 4), flame(96, -5, -1.9, 36, 9, FIRE, 2, 4),
            flame(92, 6, 2.4, 28, 8, EMBER, 3, 3.5), flame(92, -6, -2.4, 28, 8, EMBER, 4, 3.5),
            Part(92, 0, 0, 14, 13, OBSIDIAN, ridge=True, paint=cracks(3, LAVA[2], 0.2)),
            leaf(104, 56, 25, LAVA, paint=chain(cracks(5, (255, 240, 160), 0.1), tip_fade((255, 240, 160), 0.6)), sharp=1.2),
            gem(98, 0, 6, FIRE), gem(98, 0, 2.6, GLOWY((255, 250, 200)))], 166, 30


def zeus_trident():
    def tine(v, ln, bend):
        return Part(104, v, 0, ln, lambda t: 9 * (1 - t) ** 0.8 + 0.8, BOLT, center=lambda t: bend * t * t,
                    ridge=True, paint=zigzag(ln, (255, 255, 255), 0.4, 3))
    return [handle(100, 4.4, STORM, (BOLT[1],), 7), Disc(2, 0, 4.6, BOLT),
            Part(92, -20, PI / 2, 40, 8, GOLD, center=lambda t: -7 * (2 * t - 1) ** 2),
            tine(-17, 40, -8), tine(17, 40, 8), tine(0, 58, 0),
            Part(94, 0, 0, 12, 10, STORM, ridge=True),
            gem(98, 0, 6.4, STORM), gem(98, 0, 3, GLOWY((255, 255, 230)))], 168, 30


# AXES --------------------------------------------------------------------------------------------
def hatchet():
    return [handle(70, 4, WOOD, (DARKWOOD[0],), 12), *axe_head(58, 1, 13, 8, 15, IRON, edge_pal=GLOWY(STEEL[3])),
            Part(56, 0, 0, 16, 5, IRON)], 82, 14


def woodcutter_axe():
    return [handle(84, 4.4, WOOD, (RUST[0],), 14), Disc(1.6, 0, 3, WOOD),
            *axe_head(68, 1, 17, 9, 21, RUST, edge_pal=GLOWY(RUST[3])), Part(64, 0, 0, 20, 6, RUST),
            Part(76, -2, -PI / 2, 6, 5, RUST)], 96, 16


def bearded_axe():
    return [handle(86, 4.4, DARKWOOD, (STEEL[1],), 9), Disc(1.6, 0, 3, STEEL),
            Part(62, 2, PI / 2 + 0.25, 18, lambda t: 9 + 14 * t ** 1.6, STEEL, round_end=0.4, center=lambda t: -5 * t * t),
            Part(64, 0, 0, 22, 6.4, STEEL), Part(80, -2, -PI / 2, 8, lambda t: 6 * (1 - t) + 0.5, STEEL)], 100, 16


def bone_axe():
    return [handle(84, 5, BONE, (BONE[0],), 7), Disc(2, 0, 4, BONE),
            *axe_head(64, 1, 17, 11, 23, BONE, edge_pal=GLOWY(BONE[3])),
            *spikes(66, -1, 3, 8, 5, BONE, 0.7, 4), Part(62, 0, 0, 24, 7, BONE)], 98, 16


def frostbite_axe():
    return [handle(88, 4.6, ICE, (WHITE[1],), 8), Disc(2, 0, 3.6, ICE),
            *axe_head(66, 1, 19, 11, 26, ICE, edge_pal=GLOWY(WHITE[3]), paint=tip_fade((255, 255, 255), 0.6)),
            *spikes(72, 1, 3, 8, 6, WHITE, -0.2, 3), Part(64, 0, 0, 26, 7, WHITE),
            Part(80, -2, -PI / 2, 10, lambda t: 7 * (1 - t) + 0.5, ICE)], 104, 16


def ember_axe():
    return [handle(88, 4.6, OBSIDIAN, (EMBER[1],), 8), Disc(2, 0, 3.6, EMBER),
            *axe_head(66, 1, 19, 11, 26, EMBER, edge_pal=GLOWY((255, 236, 150)), paint=cracks(9, (255, 220, 120), 0.12)),
            flame(70, 22, 0.4, 14, 5, FIRE, 1, 2), flame(78, 20, 0.2, 12, 4, FIRE, 2, 2),
            Part(64, 0, 0, 26, 7, OBSIDIAN)], 104, 16


def titans_wrath():
    rune = (255, 230, 120)

    def head(d):
        return axe_head(72, d, 30, 18, 46, GOLD, edge_pal=GLOWY(WHITE[3]), paint=rune_line(30, 5, rune), roundness=0.42)
    return [handle(110, 6, OBSIDIAN, (GOLD[1],), 8), Disc(2.4, 0, 5.4, GOLD), gem(2.4, 0, 2.6, FIRE),
            *head(1), *head(-1),
            Part(66, 0, 0, 40, 11, GOLD, ridge=True, paint=rune_line(40, 6, rune)),
            leaf(104, 18, 9, GOLD), gem(86, 0, 6, FIRE), gem(86, 0, 3, GLOWY((255, 250, 200)))], 128, 20


def void_reaver():
    def head(d):
        return [Part(70, 2 * d, PI / 2 * d, 30, lambda t: 16 + 30 * t ** 1.4, VOID, round_end=0.5,
                     center=lambda t: 6 * t * t * d, paint=stars(11 + d, (255, 220, 255), 0.06)),
                *spikes(78, d, 2, 10, 10, SHADOW, -0.3, 5)]
    return [handle(108, 6, SHADOW, (VOID[2],), 7), Disc(2.4, 0, 5.2, VOID),
            *head(1), *head(-1), Part(64, 0, 0, 42, 11, SHADOW, ridge=True),
            leaf(104, 20, 10, VOID), gem(86, 0, 6.6, SHADOW), gem(86, 0, 4.4, GLOWY((255, 90, 220))),
            gem(86, 0, 1.8, GLOWY((20, 0, 30)))], 126, 20


def worldsplitter():
    return [handle(112, 7, OBSIDIAN, (LAVA[1],), 9), Disc(2.6, 0, 6, OBSIDIAN, paint=cracks(4, LAVA[2], 0.25)),
            Part(66, 2, PI / 2, 40, lambda t: 26 + 30 * t, OBSIDIAN, round_end=0.32, paint=cracks(21, LAVA[2], 0.2)),
            Part(66 + 34, 2, PI / 2, 8, 56, GLOWY(LAVA[2]), round_end=1.0),
            Part(70, -2, -PI / 2, 18, lambda t: 18 * (1 - t) + 0.6, OBSIDIAN, paint=cracks(23, LAVA[2], 0.2)),
            flame(86, 40, 0.3, 22, 7, FIRE, 1, 3), flame(74, 42, 0.5, 18, 6, FIRE, 2, 3), flame(96, 36, 0.1, 16, 5, EMBER, 3, 2),
            Part(62, 0, 0, 46, 13, OBSIDIAN, ridge=True, paint=cracks(25, LAVA[2], 0.22)),
            gem(86, 0, 5, LAVA)], 128, 20


def stormbreaker():
    return [handle(110, 6, STORM, (BOLT[1],), 8), Disc(2.4, 0, 5, STEEL), gem(2.4, 0, 2.4, NEON),
            Part(66, 2, PI / 2, 34, lambda t: 20 + 24 * t ** 1.3, STEEL, round_end=0.4, paint=zigzag(34, BOLT[2], 0.6, 4)),
            Part(66 + 28, 2, PI / 2, 6, 44, GLOWY(NEON[2]), round_end=1.1),
            Part(70, -2, -PI / 2, 16, lambda t: 14 * (1 - t) + 0.6, STEEL, paint=zigzag(16, BOLT[2], 0.5, 3)),
            Part(64, 0, 0, 44, 11, STORM, ridge=True), gem(84, 0, 5, NEON), gem(84, 0, 2.2, GLOWY((255, 255, 255)))], 128, 20


# DAGGERS -----------------------------------------------------------------------------------------
def rusty_shiv():
    return [handle(14, 4, LEATHER, (LEATHER[0],), 3), Part(13, 0, 0, 3, 7, RUST), blade(16, 30, 6, 5, RUST, point=0.35)], 46, 6


def kunai():
    return [Disc(-2, 0, 4, IRON, hole=2.2), handle(15, 3.4, REDCLOTH, (REDCLOTH[0],), 3),
            leaf(15, 30, 9, IRON, sharp=1.1)], 46, 7


def wavy_kris():
    return [handle(15, 4.4, DARKWOOD, (GOLD[1],), 4), Disc(1.6, 0, 3.6, GOLD),
            Part(14, -7, PI / 2, 14, 3.4, GOLD, center=lambda t: 2 * (2 * t - 1) ** 2),
            Part(17, 0, 0, 38, lambda t: 7.5 * min(1, (1 - t) / 0.25) if t > 0.75 else 7.5, STEEL,
                 center=lambda t: 2.6 * math.sin(t * PI * 4), edge=0, ridge=True)], 58, 7


def venom_fang():
    return [handle(15, 4.6, GREENCLOTH, (VENOM[0],), 4), Disc(1.6, 0, 3.6, VENOM),
            guard(15, 7, 3.4, VENOM, 2.5),
            Part(18, 0, 0, 34, lambda t: 9 * (1 - t) ** 0.8 + 0.6, VENOM, center=lambda t: -5 * t * t, edge=-1,
                 paint=tip_fade((220, 255, 120), 0.6)),
            Part(20, 0, 0, 22, 1.6, GLOWY((210, 255, 120)), center=lambda t: -2.5 * t * t)], 56, 7


def night_dirk():
    return [handle(16, 4.4, SHADOW, (VOID[1],), 4), Disc(1.8, 0, 3.8, SHADOW), gem(1.8, 0, 1.6, VOID),
            guard(16, 9, 3.4, SHADOW, 3),
            blade(19, 40, 9, 7, SHADOW, point=0.32, paint=rune_line(40, 6, VOID[3]))], 62, 8


def ice_stiletto():
    return [handle(16, 4.4, ICE, (WHITE[2],), 4), Disc(1.8, 0, 3.6, WHITE),
            guard(16, 8, 3.6, ICE, -2), blade(19, 44, 6, 4, ICE, point=0.5, paint=tip_fade((255, 255, 255), 0.3)),
            *spikes(26, 1, 3, 5, 8, WHITE, -0.4, 2.4)], 66, 8


def demon_fang():
    eye = GLOWY((255, 220, 60))
    red = GLOWY((255, 40, 40))
    return [handle(18, 5.4, OBSIDIAN, (BLOOD[1],), 4), Disc(2, 0, 4.4, BLOOD), gem(2, 0, 2, eye),
            Part(15, -14, PI / 2, 28, 6, OBSIDIAN, center=lambda t: 7 * (2 * t - 1) ** 2),     # horned guard
            Part(24, 0, 0, 52, lambda t: 15 * (1 - t) ** 0.75 + 0.6, BLOOD, center=lambda t: 9 * t * t, edge=1,
                 paint=cracks(31, (255, 120, 80), 0.08)),
            *spikes(32, -1, 4, 7, 9, OBSIDIAN, 0.2, 4),
            gem(19, 0, 6, BONE), gem(18.2, 2.6, 1.6, red), gem(18.2, -2.6, 1.6, red)], 84, 8


def starfall():
    return [handle(18, 5, COSMIC, (GOLD[1],), 4), Disc(2, 0, 4.6, GOLD), gem(2, 0, 2.4, GLOWY((255, 255, 255))),
            *wing(20, 1, 16, GOLD, 4, 0.9, 3.4), *wing(20, -1, 16, GOLD, 4, 0.9, 3.4),
            Part(22, 0, 0, 56, lambda t: 14 * (1 - t) ** 0.9 + 0.6, COSMIC, edge=0,
                 paint=chain(stars(5, (255, 255, 255), 0.1), tip_fade((200, 180, 255), 0.6))),
            Part(24, 0, 0, 40, 2, GLOWY((210, 200, 255))), gem(22, 0, 5, COSMIC), gem(22, 0, 2.4, GLOWY((255, 250, 220)))], 84, 8


def phoenix_talon():
    return [handle(18, 5, EMBER, (GOLD[1],), 4), Disc(2, 0, 4.4, GOLD),
            *wing(20, 1, 22, FIRE, 5, 1.0, 4.2), *wing(20, -1, 22, FIRE, 5, 1.0, 4.2),
            Part(22, 0, 0, 54, lambda t: 13 * (1 - t) ** 0.7 + 0.6, GOLD, center=lambda t: -6 * t * t, edge=-1,
                 paint=tip_fade((255, 120, 40), 0.35)),
            flame(30, 6, 0.25, 28, 6, FIRE, 2, 2.5), flame(26, 4, 0.12, 36, 4, EMBER, 4, 2),
            gem(21, 0, 4.4, FIRE), gem(21, 0, 2, GLOWY((255, 245, 190)))], 84, 8


def phase_blade():
    def straight(w):
        return lambda t: w * min(1, (1 - t) / 0.3) if t > 0.7 else w
    return [handle(20, 5, OBSIDIAN, (NEON[1],), 3), Disc(2, 0, 4, STEEL), gem(2, 0, 2, PINKNEON),
            Part(19, -10, PI / 2, 20, 5, STEEL, center=lambda t: -3 * (2 * t - 1) ** 2),
            Part(24, 0, 0, 58, straight(13), NEON, ridge=False, edge=0),
            Part(24, 0, 0, 56, straight(6), GLOWY((255, 255, 255))),
            Part(26, 7, 0.02, 40, 1.6, GLOWY(PINKNEON[1]), center=lambda t: 1.4 * math.sin(t * 20)),
            Part(26, -7, -0.02, 40, 1.6, GLOWY(PINKNEON[1]), center=lambda t: 1.4 * math.sin(t * 20 + 2)),
            gem(21, 0, 4, PINKNEON)], 86, 9


# SCYTHES ------------------------------------------------------------------------------------------
def scythe_blade(top, reach, w0, bend, pal, paint=None, edge_col=None, tilt=0.18):
    """The curved blade: out sideways from the top of the haft, bending back towards the handle."""
    return [crescent(top, 1, PI / 2 + tilt, reach, w0, pal, bend, edge=1, paint=paint)]


def farm_scythe():
    return [Part(0, 0, 0, 100, 3.4, WOOD, center=lambda t: 3 * math.sin(t * PI), paint=bands(100, 30, DARKWOOD[0], 3)),
            Part(46, 2, PI / 2, 6, 3, WOOD), *scythe_blade(97, 34, 8, 12, IRON)], 104, 30


def iron_scythe():
    return [handle(104, 3.6, DARKWOOD, (IRON[1],), 12), Disc(1.6, 0, 3, IRON),
            Part(98, 0, 0, 7, 6, IRON), *scythe_blade(101, 40, 10, 14, STEEL)], 110, 30


def bone_scythe():
    hole = GLOWY((30, 20, 20))
    return [handle(104, 4.6, BONE, (BONE[0],), 6), Disc(2, 0, 4.4, BONE),
            *scythe_blade(103, 42, 11, 15, BONE),
            gem(100, 0, 6, BONE), gem(101, 2.4, 1.6, hole), gem(101, -2.4, 1.6, hole)], 112, 30


def thorn_scythe():
    return [Part(0, 0, 0, 104, 4, GREENCLOTH, center=lambda t: 2 * math.sin(t * PI * 3), paint=bands(104, 9, TOXIC[0], 2)),
            *spikes(20, 1, 6, 5, 13, VENOM, 0.4, 2.6), *spikes(26, -1, 5, 5, 14, VENOM, 0.4, 2.6),
            *scythe_blade(101, 42, 11, 15, VENOM)], 112, 30


def crescent_moon():
    return [handle(106, 4.4, MOON, (WHITE[3],), 9), Disc(2, 0, 4, MOON),
            *scythe_blade(103, 48, 14, 22, MOON, paint=tip_fade((255, 255, 255), 0.4)),
            gem(102, 0, 4.4, NEON), gem(102, 0, 2, GLOWY((255, 255, 255)))], 116, 30


def winter_reaper():
    return [handle(106, 4.6, ICE, (WHITE[2],), 7), Disc(2, 0, 4, WHITE),
            *scythe_blade(103, 48, 14, 20, ICE, paint=tip_fade((255, 255, 255), 0.5)),
            *spikes(96, -1, 3, 8, 4, WHITE, 0.4, 3), gem(102, 0, 4, ICE)], 116, 30


def grim_death():
    soul = GLOWY((200, 255, 230))
    red = GLOWY((255, 40, 60))
    return [Part(0, 0, 0, 120, 6, SHADOW, center=lambda t: 3 * math.sin(t * PI * 2), paint=bands(120, 12, VOID[1], 2)),
            Disc(2.4, 0, 5.6, BONE), gem(1.6, 2.4, 1.4, red), gem(1.6, -2.4, 1.4, red),
            *scythe_blade(116, 88, 30, 44, SHADOW, paint=chain(stars(41, VOID[3], 0.05), tip_fade(VOID[2], 0.55)), tilt=0.12),
            *[gem(108 - i * 2, 6 + i * 4, 3.8, BONE) for i in range(3)],
            *[gem(107 - i * 2, 7 + i * 4, 1, red) for i in range(3)],
            flame(112, -4, -2.6, 20, 6, GHOST, 1, 3), gem(114, 0, 7, BONE), gem(115, 2.6, 2, soul), gem(115, -2.6, 2, soul)], 148, 34


def blood_moon():
    moon = GLOWY((255, 90, 90))
    return [handle(122, 6, OBSIDIAN, (BLOOD[1],), 8), Disc(2.4, 0, 5.4, BLOOD), gem(2.4, 0, 2.6, moon),
            *scythe_blade(116, 88, 30, 44, BLOOD, paint=cracks(51, (255, 150, 140), 0.07), tilt=0.12),
            *scythe_blade(110, 44, 10, 18, OBSIDIAN, tilt=-0.35),
            Disc(116, 0, 10, BLOOD), Disc(116, 0, 7.6, GLOWY((40, 0, 8))), Disc(117.4, 1.6, 6.8, moon)], 148, 34


def soul_harvester():
    return [Part(0, 0, 0, 120, 6, OBSIDIAN, center=lambda t: 2.4 * math.sin(t * PI * 2.5), paint=bands(120, 10, GHOST[1], 2)),
            Disc(2.4, 0, 5.6, GHOST), gem(2.4, 0, 2.6, GLOWY((255, 255, 255))),
            *scythe_blade(116, 88, 30, 44, GHOST, paint=chain(cracks(61, (255, 255, 255), 0.06), tip_fade((240, 255, 250), 0.5)), tilt=0.12),
            flame(104, -6, -2.3, 28, 8, GHOST, 2, 3), flame(94, -6, -2.0, 22, 6, GHOST, 3, 3), flame(84, 6, 2.1, 20, 6, GHOST, 4, 3),
            gem(114, 0, 7, OBSIDIAN), gem(114, 0, 4, GHOST), gem(114, 0, 1.8, GLOWY((255, 255, 255)))], 148, 34


def eclipse_scythe():
    corona = GLOWY((255, 236, 140))
    return [handle(122, 6, OBSIDIAN, (GOLD[1],), 7), Disc(2.4, 0, 5.4, GOLD), gem(2.4, 0, 2.4, corona),
            *scythe_blade(116, 88, 30, 44, GOLD, paint=chain(rune_line(70, 6, corona[0]), tip_fade((255, 252, 220), 0.55)), tilt=0.12),
            *scythe_blade(110, 40, 9, 16, OBSIDIAN, tilt=-0.4),
            *[Part(116, 0, a, 15, lambda t: 3.4 * (1 - t) + 0.4, GOLD) for a in [i * PI / 4 for i in range(8)]],
            Disc(116, 0, 9.6, corona), Disc(116, 0, 7.4, GLOWY((10, 6, 16)))], 148, 34


DESIGNS = {
    "spear": ["wooden_spear", "iron_pike", "bronze_glaive", "frost_lance", "storm_trident", "crimson_halberd",
              "gungnir", "abyss_lance", "dragonfire_pike", "zeus_trident"],
    "axe": ["hatchet", "woodcutter_axe", "bearded_axe", "bone_axe", "frostbite_axe", "ember_axe",
            "titans_wrath", "void_reaver", "worldsplitter", "stormbreaker"],
    "dagger": ["rusty_shiv", "kunai", "wavy_kris", "venom_fang", "night_dirk", "ice_stiletto",
               "demon_fang", "starfall", "phoenix_talon", "phase_blade"],
    "scythe": ["farm_scythe", "iron_scythe", "bone_scythe", "thorn_scythe", "crescent_moon", "winter_reaper",
               "grim_death", "blood_moon", "soul_harvester", "eclipse_scythe"],
}
