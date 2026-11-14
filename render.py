#!/usr/bin/env python3
"""Draw entry.png: a steaming bowl of tonkotsu ramen, painted with PIL.

Top-down-ish view: dark warm backdrop, lacquered bowl, glossy golden
broth, wavy noodles, chashu, a jammy ajitama egg, nori, scallions and a
lift of noodles on chopsticks, with soft steam rising. Deterministic:
no timestamps, no random numbers, no network. Pure PIL drawing on a
1024x1024 canvas."""

import math

from PIL import Image, ImageDraw, ImageFilter

W, H = 1024, 1024

# ---------------------------------------------------------------- palette --
BG_TOP = (26, 15, 10)          # near-black warm brown
BG_BOT = (58, 32, 18)
GLOW = (255, 176, 92)          # warm light behind the bowl
TABLE_TOP = (74, 47, 28)
TABLE_BOT = (43, 25, 14)
BOWL_OUT = (24, 10, 8)         # black lacquer outside
BOWL_RIM = (168, 32, 26)       # deep red rim
BOWL_IN = (52, 16, 12)
BROTH = (196, 128, 48)
BROTH_DARK = (148, 88, 30)
BROTH_LIGHT = (238, 176, 84)
OIL = (255, 214, 130)
NOODLE = (244, 214, 140)
NOODLE_SH = (214, 168, 88)
CHASHU = (196, 96, 74)
CHASHU_DK = (140, 58, 44)
CHASHU_LT = (236, 172, 140)
EGG_WHITE = (250, 244, 228)
YOLK = (240, 138, 28)
YOLK_DK = (206, 102, 12)
YOLK_LT = (255, 186, 92)
NORI = (18, 34, 22)
NORI_HI = (48, 84, 52)
SCALLION = (96, 168, 72)
SCALLION_DK = (52, 112, 40)
MENMA = (214, 158, 74)
CHOP = (178, 118, 58)
CHOP_DK = (128, 80, 36)
STEAM = (255, 244, 224)

CX, CY = 512, 560            # bowl centre
BOWL_RX, BOWL_RY = 330, 262  # outer bowl ellipse
RIM_RX, RIM_RY = 296, 232    # broth surface ellipse


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(img, top, bottom):
    """Vertical gradient over the whole canvas."""
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=lerp(top, bottom, y / (H - 1)))
    return img


def glow_layer():
    """Soft warm radial glow centred on the bowl, on its own layer."""
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    for r in range(520, 0, -4):
        t = 1.0 - r / 520.0
        c = tuple(int(GLOW[i] * t * t * 0.85) for i in range(3))
        d.ellipse([CX - r, CY - 60 - int(r * 0.78), CX + r,
                   CY - 60 + int(r * 0.78)], fill=c)
    return layer.filter(ImageFilter.GaussianBlur(18))


def wood_grain(draw):
    """Subtle plank lines and knots on the table area."""
    for y in (700, 788, 872, 956):
        draw.line([(0, y), (W, y)], fill=(30, 17, 9), width=3)
        draw.line([(0, y + 3), (W, y + 3)], fill=(96, 62, 36), width=1)
    for x, y, r in ((150, 760, 26), (880, 900, 30), (760, 990, 22)):
        draw.ellipse([x - r, y - r // 2, x + r, y + r // 2],
                     outline=(52, 30, 16), width=3)


def noodle_strand(draw, x0, y0, x1, y1, amp, waves, width, colour):
    """One wavy noodle strand from (x0,y0) to (x1,y1)."""
    pts = []
    n = 60
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length
    for i in range(n + 1):
        t = i / n
        off = amp * math.sin(t * waves * math.pi * 2)
        pts.append((x0 + dx * t + nx * off, y0 + dy * t + ny * off))
    draw.line(pts, fill=colour, width=width, joint="curve")


def steam_layer():
    """Three soft rising steam columns, blurred."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for cx0, amp, phase, alpha in (
            (400, 26, 0.0, 110), (512, 34, 1.9, 130), (624, 24, 3.6, 100)):
        pts = []
        for i in range(61):
            t = i / 60.0
            y = 470 - t * 330
            x = cx0 + amp * math.sin(t * 5.2 + phase) * (0.4 + t)
            pts.append((x, y))
        d.line(pts, fill=STEAM + (alpha,), width=26, joint="curve")
    return layer.filter(ImageFilter.GaussianBlur(16))


def main():
    img = Image.new("RGB", (W, H), BG_TOP)
    vgrad(img, BG_TOP, BG_BOT)
    img = Image.blend(img, glow_layer(), 0.55)

    draw = ImageDraw.Draw(img)

    # ---- table (bottom third) -----------------------------------------
    draw.rectangle([0, 660, W, H], fill=TABLE_TOP)
    for y in range(660, H):
        draw.line([(0, y), (W, y)],
                  fill=lerp(TABLE_TOP, TABLE_BOT, (y - 660) / (H - 660)))
    wood_grain(draw)

    # ---- bowl shadow ----------------------------------------------------
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.ellipse([CX - BOWL_RX - 18, CY - BOWL_RY + 96, CX + BOWL_RX + 18,
                CY + BOWL_RY + 116], fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    img.paste(sh, (0, 0), sh)
    draw = ImageDraw.Draw(img)

    # ---- bowl body: vertical lacquer gradient clipped to the ellipse ----
    body = Image.new("RGB", (W, H), (0, 0, 0))
    vgrad(body, (64, 22, 16), (10, 5, 4))
    mask = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(mask)
    dm.ellipse([CX - BOWL_RX, CY - BOWL_RY + 40, CX + BOWL_RX,
                CY + BOWL_RY + 150], fill=255)
    img.paste(body, (0, 0), mask)
    draw = ImageDraw.Draw(img)
    # foot ring at the base of the bowl
    draw.ellipse([CX - 118, CY + BOWL_RY + 88, CX + 118,
                  CY + BOWL_RY + 132], outline=(150, 60, 44), width=5)
    draw.ellipse([CX - 118, CY + BOWL_RY + 88, CX + 118,
                  CY + BOWL_RY + 132], outline=(40, 14, 10), width=1)
    # lacquer sheen on the left flank
    sheen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dsh = ImageDraw.Draw(sheen)
    dsh.ellipse([CX - BOWL_RX + 26, CY - BOWL_RY + 96, CX - 120,
                 CY + BOWL_RY + 90], fill=(255, 210, 160, 34))
    sheen = sheen.filter(ImageFilter.GaussianBlur(14))
    img.paste(sheen, (0, 0), sheen)
    draw = ImageDraw.Draw(img)

    # rim ring + inner wall
    draw.ellipse([CX - BOWL_RX, CY - BOWL_RY, CX + BOWL_RX, CY + BOWL_RY],
                 fill=BOWL_RIM)
    draw.ellipse([CX - RIM_RX, CY - RIM_RY, CX + RIM_RX, CY + RIM_RY],
                 fill=BOWL_IN)
    # thin gold line on the rim
    draw.ellipse([CX - BOWL_RX + 8, CY - BOWL_RY + 8, CX + BOWL_RX - 8,
                  CY + BOWL_RY - 8], outline=(232, 178, 92), width=3)

    # ---- broth ----------------------------------------------------------
    broth = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(broth)
    db.ellipse([CX - RIM_RX, CY - RIM_RY, CX + RIM_RX, CY + RIM_RY],
               fill=BROTH + (255,))
    # soft light: warm pool top-left, deep shadow bottom-right
    hi = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dh = ImageDraw.Draw(hi)
    dh.ellipse([CX - 300, CY - 260, CX + 60, CY + 40],
               fill=BROTH_LIGHT + (110,))
    hi = hi.filter(ImageFilter.GaussianBlur(40))
    broth.paste(hi, (0, 0), hi)
    lo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lo)
    dl.ellipse([CX - 60, CY + 40, CX + 320, CY + 260],
               fill=BROTH_DARK + (120,))
    lo = lo.filter(ImageFilter.GaussianBlur(40))
    broth.paste(lo, (0, 0), lo)
    db = ImageDraw.Draw(broth)
    # oil droplets catching the light
    for x, y, r in ((380, 500, 12), (470, 620, 9), (620, 470, 10),
                    (660, 600, 8), (540, 690, 11), (430, 660, 7),
                    (590, 540, 6), (350, 580, 7)):
        db.ellipse([x - r, y - r, x + r, y + r], fill=OIL + (235,))
        db.ellipse([x - r // 2, y - r // 2, x, y], fill=(255, 244, 210, 255))
    # a few red chilli-oil drops for a warm colour pop
    for x, y, r in ((520, 500, 8), (660, 660, 7), (380, 600, 6)):
        db.ellipse([x - r, y - r, x + r, y + r], fill=(198, 58, 22, 235,))
        db.ellipse([x - r // 2, y - r // 2, x, y],
                   fill=(255, 140, 80, 255))
    broth = broth.filter(ImageFilter.GaussianBlur(2))
    img.paste(broth, (0, 0), broth)
    draw = ImageDraw.Draw(img)

    # ---- nori sheet standing at the back-left ---------------------------
    # drawn right after the broth so the noodle bed overlaps its base
    nori = Image.new("RGBA", (110, 170), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nori)
    dn.rounded_rectangle([5, 5, 105, 165], radius=9, fill=NORI + (255,),
                         outline=NORI_HI + (255,), width=3)
    for i in range(5):
        y = 26 + i * 28
        dn.line([(14, y), (96, y)], fill=NORI_HI + (180,), width=2)
    nori = nori.rotate(-12, resample=Image.BICUBIC, expand=True)
    img.paste(nori, (300, 340), nori)
    draw = ImageDraw.Draw(img)

    # ---- noodle bed (denser, tighter waves) -----------------------------
    strands = [
        # (x0, y0, x1, y1, amp, waves, width)
        (300, 520, 700, 500, 13, 7, 13),
        (300, 545, 720, 530, 14, 8, 13),
        (300, 570, 720, 555, 13, 7, 12),
        (310, 595, 700, 590, 15, 8, 12),
        (320, 620, 690, 620, 14, 7, 12),
        (340, 645, 670, 645, 13, 8, 11),
        (360, 670, 640, 670, 12, 7, 11),
        (380, 690, 620, 690, 11, 6, 10),
        (300, 530, 640, 660, 16, 6, 12),
        (380, 500, 720, 640, 15, 7, 12),
        (420, 500, 700, 560, 11, 9, 10),
        (340, 580, 600, 700, 13, 6, 10),
        (460, 700, 700, 580, 12, 7, 10),
        (300, 610, 560, 500, 12, 8, 10),
        (560, 500, 730, 620, 11, 7, 10),
        (330, 560, 560, 660, 12, 8, 10),
        (480, 520, 680, 700, 12, 6, 10),
        (400, 680, 660, 540, 11, 8, 9),
    ]
    for i, (x0, y0, x1, y1, amp, waves, wd) in enumerate(strands):
        colour = NOODLE if i % 2 == 0 else NOODLE_SH
        noodle_strand(draw, x0, y0, x1, y1, amp, waves, wd, colour)

    # ---- menma (bamboo shoots) ------------------------------------------
    for x, y, ang in ((330, 640, 18), (352, 662, -12), (640, 660, 24)):
        draw.rounded_rectangle([x, y, x + 64, y + 18], radius=8,
                               fill=MENMA, outline=(170, 116, 44), width=2)

    # ---- chashu slices ----------------------------------------------------
    for cx0, cy0, rx, ry, rot in ((400, 640, 78, 62, -14),
                                  (468, 676, 70, 56, 8)):
        # draw on a small rotated layer for a natural tilt
        layer = Image.new("RGBA", (260, 220), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        dl.ellipse([30, 30, 30 + 2 * rx, 30 + 2 * ry], fill=CHASHU + (255,),
                   outline=CHASHU_DK + (255,), width=4)
        dl.ellipse([30 + rx // 2, 30 + ry // 2, 30 + 3 * rx // 2,
                    30 + 3 * ry // 2], fill=CHASHU_LT + (255,))
        dl.ellipse([30 + rx // 2 + 8, 30 + ry // 2 + 8, 30 + rx,
                    30 + ry], fill=(244, 196, 168, 255))
        layer = layer.rotate(rot, resample=Image.BICUBIC, expand=True)
        img.paste(layer, (cx0 - layer.width // 2, cy0 - layer.height // 2),
                  layer)
    draw = ImageDraw.Draw(img)

    # ---- ajitama egg (halved, jammy yolk) --------------------------------
    ex, ey = 640, 600
    draw.ellipse([ex - 66, ey - 56, ex + 66, ey + 56], fill=EGG_WHITE,
                 outline=(214, 200, 178), width=3)
    draw.ellipse([ex - 40, ey - 40, ex + 40, ey + 40], fill=YOLK,
                 outline=YOLK_DK, width=3)
    draw.ellipse([ex - 26, ey - 30, ex + 6, ey - 2], fill=YOLK_LT)
    draw.ellipse([ex - 12, ey + 12, ex + 16, ey + 32], fill=YOLK_DK)

    # ---- scallion rings ---------------------------------------------------
    for x, y, r in ((360, 540, 9), (420, 520, 8), (560, 520, 9),
                    (600, 660, 8), (520, 700, 9), (480, 540, 7),
                    (680, 540, 8), (380, 680, 8), (540, 640, 7)):
        draw.ellipse([x - r, y - r, x + r, y + r], fill=SCALLION,
                     outline=SCALLION_DK, width=2)
        draw.ellipse([x - r // 2, y - r // 2, x + r // 2, y + r // 2],
                     fill=(30, 60, 24))

    # ---- chopsticks lifting noodles (upper right) -------------------------
    # a loose clump of noodles hanging from the chopstick tips down
    # into the broth, drawn as several S-curved strands
    lift = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lift)
    for i, (x0, y0, x1, y1, amp, waves) in enumerate((
            (716, 316, 700, 500, 18, 3),
            (732, 312, 716, 506, 20, 3),
            (748, 314, 736, 498, 16, 4),
            (762, 320, 756, 492, 18, 3),
            (724, 320, 690, 470, 14, 4),
            (756, 326, 770, 480, 14, 3))):
        noodle_strand(dl, x0, y0, x1, y1, amp, waves, 11,
                      NOODLE if i % 2 == 0 else NOODLE_SH)
    lift = lift.filter(ImageFilter.GaussianBlur(1))
    img.paste(lift, (0, 0), lift)
    draw = ImageDraw.Draw(img)
    # chopsticks: two parallel sticks, tips pinching the noodle clump
    for off in (0, 16):
        draw.line([(716 + off, 306 + off // 2), (956 + off, 196 + off // 2)],
                  fill=CHOP, width=12)
        draw.line([(716 + off, 310 + off // 2), (956 + off, 200 + off // 2)],
                  fill=CHOP_DK, width=3)

    # ---- steam (single layer, pasted once) --------------------------------
    steam = steam_layer()
    img.paste(steam, (0, 0), steam)

    # ---- vignette ---------------------------------------------------------
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dv = ImageDraw.Draw(vig)
    dv.ellipse([-160, -160, W + 160, H + 160], outline=(0, 0, 0, 120),
               width=260)
    vig = vig.filter(ImageFilter.GaussianBlur(30))
    img.paste(vig, (0, 0), vig)

    img.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
