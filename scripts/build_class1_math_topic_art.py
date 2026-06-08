from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ENGLISH_AI = ROOT / "assets" / "question-art" / "class1-english-ai"
OUT = ROOT / "assets" / "question-art" / "class1-math-question-ai"
SIZE = (3840, 2160)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


FONT_NUM = font(96, True)
FONT_BIG = font(150, True)
FONT_SMALL = font(54, True)


SCENES = [
    ("ch01-cat-room-places", "cat-room", "hello-meet"),
    ("ch01-position-words", "positions", "good-morning"),
    ("ch01-cat-movement", "movement", "legs-walk"),
    ("ch01-find-hidden-cat", "hidden-cat", "living-things"),
    ("ch02-long-things", "long", "farm-see"),
    ("ch02-round-things", "round", "healthy-food"),
    ("ch02-shape-sort", "shape-sort", "body-parts"),
    ("ch02-shape-check", "shape-check", "eyes-ears"),
    ("ch03-count-mangoes", "mango-count", "eat-food"),
    ("ch03-compare-mangoes", "mango-compare", "healthy-food"),
    ("ch03-share-mangoes", "mango-share", "care-living"),
    ("ch03-counting-useful", "counting-useful", "good-morning"),
    ("ch04-make-10", "make-10", "hands-clap"),
    ("ch04-pairs-make-10", "pairs-10", "body-parts"),
    ("ch04-learn-making-10", "ten-frame", "hello-meet"),
    ("ch04-check-10", "check-10", "eyes-ears"),
    ("ch05-know-how-many", "many-count", "living-things"),
    ("ch05-count-carefully", "count-careful", "care-living"),
    ("ch05-compare-groups", "compare-groups", "animals-need"),
    ("ch05-count-carefully-why", "careful-why", "good-morning"),
    ("ch06-farm-things", "farm", "farm-see"),
    ("ch06-count-vegetables", "veg-count", "farm-useful"),
    ("ch06-compare-vegetables", "veg-compare", "farmer-works"),
    ("ch06-farmers-count", "farmer-count", "farmer-works"),
    ("ch07-family-members", "family", "hello-meet"),
    ("ch07-count-family", "family-count", "body-parts"),
    ("ch07-compare-families", "family-compare", "living-things"),
    ("ch07-family-do", "family-do", "hands-clap"),
    ("ch08-numbers-help", "numbers-help", "good-morning"),
    ("ch08-see-numbers", "numbers-see", "legs-walk"),
    ("ch08-number-order", "number-order", "rainbow-colours"),
    ("ch08-numbers-fun", "numbers-fun", "rainbow-like"),
    ("ch09-utsav-happens", "utsav", "rainbow-see"),
    ("ch09-count-utsav", "utsav-count", "rainbow-colours"),
    ("ch09-make-groups", "groups", "goodbye"),
    ("ch09-utsav-special", "utsav-special", "rainbow-like"),
    ("ch10-morning", "morning", "good-morning"),
    ("ch10-day", "day", "legs-walk"),
    ("ch10-night", "night", "winter"),
    ("ch10-follow-time", "clock", "when-eat"),
    ("ch11-know-how-many", "times-count", "hands-clap"),
    ("ch11-counting", "repeated-actions", "legs-walk"),
    ("ch11-compare-groups", "repeat-compare", "farm-animals"),
    ("ch11-count-carefully", "repeat-careful", "care-living"),
    ("ch12-use-money", "money-use", "eat-food"),
    ("ch12-before-buying", "money-buy", "healthy-food"),
    ("ch12-count-money", "money-count", "farm-useful"),
    ("ch12-spend-less", "money-less", "not-waste-food"),
    ("ch13-count-toys", "toy-count", "legs-walk"),
    ("ch13-sort-toys", "toy-sort", "body-parts"),
    ("ch13-compare-toys", "toy-compare", "hello-meet"),
    ("ch13-keep-toys", "toy-keep", "care-living"),
]


def load_background(slug: str) -> Image.Image:
    path = ENGLISH_AI / f"{slug}.png"
    if not path.exists():
        path = next(ENGLISH_AI.glob("*.png"))
    with Image.open(path) as source:
        image = source.convert("RGB").resize(SIZE, Image.Resampling.LANCZOS)
    image = ImageEnhance.Color(image).enhance(1.04)
    image = ImageEnhance.Contrast(image).enhance(0.96)
    overlay = Image.new("RGBA", SIZE, (255, 248, 230, 36))
    image = image.convert("RGBA")
    image.alpha_composite(overlay)
    return image


def rounded(draw: ImageDraw.ImageDraw, box, fill, outline=None, width=1, radius=40) -> None:
    draw.rounded_rectangle(tuple(map(int, box)), radius=int(radius), fill=fill, outline=outline, width=int(width))


def shadow(draw: ImageDraw.ImageDraw, box, alpha=70) -> None:
    draw.ellipse(tuple(map(int, box)), fill=(20, 30, 50, alpha))


def text_center(draw: ImageDraw.ImageDraw, box, text: str, fill, fnt) -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    x = box[0] + ((box[2] - box[0]) - (bbox[2] - bbox[0])) / 2
    y = box[1] + ((box[3] - box[1]) - (bbox[3] - bbox[1])) / 2
    draw.text((x, y), text, fill=fill, font=fnt)


def add_focus_panel(image: Image.Image) -> ImageDraw.ImageDraw:
    return ImageDraw.Draw(image, "RGBA")


def draw_mango(draw, x: int, y: int, s: float = 1.0, number: int | None = None) -> None:
    shadow(draw, (x - 110 * s, y + 78 * s, x + 125 * s, y + 142 * s), 46)
    draw.ellipse((x - 92 * s, y - 66 * s, x + 112 * s, y + 96 * s), fill=(247, 190, 47), outline=(117, 78, 24), width=max(4, int(8 * s)))
    draw.ellipse((x - 6 * s, y - 112 * s, x + 92 * s, y - 52 * s), fill=(67, 155, 78))
    draw.arc((x - 58 * s, y - 28 * s, x + 88 * s, y + 95 * s), 25, 210, fill=(255, 226, 116), width=max(3, int(9 * s)))
    if number is not None:
        text_center(draw, (x - 60 * s, y - 35 * s, x + 65 * s, y + 78 * s), str(number), (45, 37, 25), FONT_NUM)


def draw_counter(draw, x: int, y: int, s: float, color, number: int | None = None) -> None:
    shadow(draw, (x - 92 * s, y + 78 * s, x + 92 * s, y + 124 * s), 38)
    rounded(draw, (x - 78 * s, y - 78 * s, x + 78 * s, y + 78 * s), color, outline=(31, 50, 88), width=max(4, int(8 * s)), radius=24 * s)
    rounded(draw, (x - 50 * s, y - 58 * s, x + 34 * s, y - 18 * s), (255, 255, 255, 48), radius=18 * s)
    if number is not None:
        text_center(draw, (x - 70 * s, y - 66 * s, x + 70 * s, y + 70 * s), str(number), (255, 255, 255), FONT_NUM)


def draw_block(draw, x: int, y: int, s: float = 1.0, color=(86, 126, 255), number: int | None = None) -> None:
    shadow(draw, (x - 100 * s, y + 80 * s, x + 105 * s, y + 126 * s), 42)
    rounded(draw, (x - 88 * s, y - 80 * s, x + 88 * s, y + 80 * s), color, outline=(31, 50, 88), width=max(4, int(8 * s)), radius=20 * s)
    draw.polygon(
        [
            (x - 88 * s, y - 80 * s),
            (x - 38 * s, y - 125 * s),
            (x + 138 * s, y - 125 * s),
            (x + 88 * s, y - 80 * s),
        ],
        fill=tuple(min(255, int(c * 1.16)) for c in color[:3]),
        outline=(31, 50, 88),
    )
    draw.line((x + 88 * s, y - 80 * s, x + 138 * s, y - 125 * s), fill=(31, 50, 88), width=max(3, int(6 * s)))
    if number is not None:
        text_center(draw, (x - 75 * s, y - 70 * s, x + 78 * s, y + 76 * s), str(number), (255, 255, 255), FONT_NUM)


def draw_coin(draw, x: int, y: int, s: float = 1.0, value: str = "1") -> None:
    shadow(draw, (x - 86 * s, y + 58 * s, x + 86 * s, y + 105 * s), 48)
    draw.ellipse((x - 74 * s, y - 74 * s, x + 74 * s, y + 74 * s), fill=(242, 190, 54), outline=(116, 79, 18), width=max(4, int(8 * s)))
    draw.ellipse((x - 52 * s, y - 52 * s, x + 52 * s, y + 52 * s), outline=(255, 228, 112), width=max(3, int(7 * s)))
    text_center(draw, (x - 58 * s, y - 56 * s, x + 58 * s, y + 58 * s), value, (86, 62, 20), FONT_NUM)


def draw_person(draw, x: int, y: int, s: float = 1.0, shirt=(86, 126, 255)) -> None:
    shadow(draw, (x - 120 * s, y + 255 * s, x + 130 * s, y + 325 * s), 42)
    draw.ellipse((x - 58 * s, y - 170 * s, x + 58 * s, y - 54 * s), fill=(255, 206, 157), outline=(47, 59, 84), width=max(3, int(6 * s)))
    draw.arc((x - 33 * s, y - 122 * s, x + 33 * s, y - 78 * s), 20, 160, fill=(36, 45, 66), width=max(2, int(4 * s)))
    rounded(draw, (x - 76 * s, y - 54 * s, x + 76 * s, y + 135 * s), shirt, outline=(47, 59, 84), width=max(3, int(5 * s)), radius=42 * s)
    draw.line((x - 52 * s, y + 122 * s, x - 92 * s, y + 275 * s), fill=(47, 72, 125), width=max(6, int(20 * s)))
    draw.line((x + 52 * s, y + 122 * s, x + 94 * s, y + 275 * s), fill=(47, 72, 125), width=max(6, int(20 * s)))
    draw.line((x - 74 * s, y + 2 * s, x - 148 * s, y + 80 * s), fill=(255, 206, 157), width=max(5, int(18 * s)))
    draw.line((x + 74 * s, y + 2 * s, x + 150 * s, y + 74 * s), fill=(255, 206, 157), width=max(5, int(18 * s)))


def draw_cat(draw, x: int, y: int, s: float = 1.0) -> None:
    shadow(draw, (x - 125 * s, y + 68 * s, x + 148 * s, y + 125 * s), 50)
    draw.ellipse((x - 105 * s, y - 45 * s, x + 100 * s, y + 76 * s), fill=(244, 144, 61), outline=(91, 54, 28), width=max(4, int(7 * s)))
    draw.ellipse((x + 58 * s, y - 125 * s, x + 170 * s, y - 16 * s), fill=(244, 144, 61), outline=(91, 54, 28), width=max(4, int(7 * s)))
    draw.polygon([(x + 75 * s, y - 118 * s), (x + 105 * s, y - 178 * s), (x + 122 * s, y - 107 * s)], fill=(244, 144, 61), outline=(91, 54, 28))
    draw.polygon([(x + 124 * s, y - 112 * s), (x + 174 * s, y - 164 * s), (x + 158 * s, y - 88 * s)], fill=(244, 144, 61), outline=(91, 54, 28))
    draw.ellipse((x + 92 * s, y - 82 * s, x + 106 * s, y - 68 * s), fill=(20, 26, 38))
    draw.ellipse((x + 136 * s, y - 82 * s, x + 150 * s, y - 68 * s), fill=(20, 26, 38))
    draw.arc((x - 170 * s, y - 94 * s, x - 32 * s, y + 48 * s), 92, 255, fill=(91, 54, 28), width=max(5, int(13 * s)))


def draw_shape_set(draw, x: int, y: int, s: float = 1.0) -> None:
    draw.rectangle((x - 130 * s, y - 100 * s, x + 20 * s, y + 50 * s), fill=(83, 126, 255), outline=(36, 54, 91), width=max(4, int(8 * s)))
    draw.ellipse((x + 95 * s, y - 100 * s, x + 245 * s, y + 50 * s), fill=(242, 94, 132), outline=(36, 54, 91), width=max(4, int(8 * s)))
    draw.polygon([(x - 15 * s, y + 235 * s), (x + 92 * s, y + 70 * s), (x + 205 * s, y + 235 * s)], fill=(67, 186, 130), outline=(36, 54, 91))


def draw_clock(draw, x: int, y: int, hour: int, minute: int = 0, s: float = 1.0) -> None:
    r = 170 * s
    draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255), outline=(33, 52, 88), width=max(5, int(10 * s)))
    for n in range(1, 13):
        a = math.radians(n * 30 - 90)
        text_center(draw, (x + math.cos(a) * r * .76 - 30 * s, y + math.sin(a) * r * .76 - 28 * s, x + math.cos(a) * r * .76 + 30 * s, y + math.sin(a) * r * .76 + 32 * s), str(n), (33, 52, 88), FONT_SMALL)
    hour_a = math.radians((hour % 12) * 30 + minute * .5 - 90)
    min_a = math.radians(minute * 6 - 90)
    draw.line((x, y, x + math.cos(hour_a) * r * .48, y + math.sin(hour_a) * r * .48), fill=(33, 52, 88), width=max(5, int(12 * s)))
    draw.line((x, y, x + math.cos(min_a) * r * .68, y + math.sin(min_a) * r * .68), fill=(234, 74, 88), width=max(4, int(8 * s)))
    draw.ellipse((x - 12 * s, y - 12 * s, x + 12 * s, y + 12 * s), fill=(234, 74, 88))


def draw_toy(draw, x: int, y: int, kind: str, s: float = 1.0) -> None:
    if kind == "ball":
        shadow(draw, (x - 85 * s, y + 62 * s, x + 85 * s, y + 108 * s), 45)
        draw.ellipse((x - 82 * s, y - 82 * s, x + 82 * s, y + 82 * s), fill=(86, 157, 255), outline=(34, 52, 88), width=max(4, int(8 * s)))
        draw.arc((x - 80 * s, y - 35 * s, x + 80 * s, y + 120 * s), 190, 350, fill=(255, 255, 255), width=max(3, int(8 * s)))
    elif kind == "car":
        shadow(draw, (x - 135 * s, y + 58 * s, x + 145 * s, y + 110 * s), 46)
        rounded(draw, (x - 130 * s, y - 55 * s, x + 130 * s, y + 45 * s), (238, 92, 82), outline=(34, 52, 88), width=max(4, int(7 * s)), radius=36 * s)
        draw.rectangle((x - 50 * s, y - 115 * s, x + 62 * s, y - 55 * s), fill=(162, 217, 255), outline=(34, 52, 88), width=max(3, int(6 * s)))
        draw.ellipse((x - 88 * s, y + 20 * s, x - 28 * s, y + 80 * s), fill=(34, 52, 88))
        draw.ellipse((x + 40 * s, y + 20 * s, x + 100 * s, y + 80 * s), fill=(34, 52, 88))
    else:
        shadow(draw, (x - 95 * s, y + 80 * s, x + 95 * s, y + 128 * s), 45)
        draw.ellipse((x - 62 * s, y - 156 * s, x + 62 * s, y - 32 * s), fill=(164, 103, 58), outline=(34, 52, 88), width=max(4, int(7 * s)))
        rounded(draw, (x - 80 * s, y - 45 * s, x + 80 * s, y + 110 * s), (246, 190, 72), outline=(34, 52, 88), width=max(4, int(7 * s)), radius=44 * s)


def draw_scene(scene_id: str, kind: str, bg_slug: str) -> Image.Image:
    image = load_background(bg_slug)
    draw = add_focus_panel(image)

    if "cat" in kind or kind in {"positions", "movement"}:
        rounded(draw, (520, 1080, 1240, 1545), (174, 214, 255, 235), outline=(35, 55, 92), width=8, radius=55)
        rounded(draw, (2130, 930, 2830, 1545), (255, 228, 173, 235), outline=(35, 55, 92), width=8, radius=55)
        draw_cat(draw, 820, 980, 1.35)
        draw_cat(draw, 2480, 865 if kind == "movement" else 1390, 1.12)
        if kind == "movement":
            draw.line((2970, 1420, 2970, 1035), fill=(236, 72, 87), width=18)
            draw.polygon([(2970, 980), (2928, 1060), (3012, 1060)], fill=(236, 72, 87))
        if kind == "hidden-cat":
            rounded(draw, (2110, 1160, 3020, 1580), (144, 101, 68, 246), outline=(35, 55, 92), width=8, radius=48)
            draw_cat(draw, 2510, 1440, .68)

    elif kind in {"long", "round", "shape-sort", "shape-check"}:
        if kind == "long":
            for y, color in [(700, (246, 190, 54)), (1040, (86, 126, 255)), (1380, (67, 186, 130))]:
                rounded(draw, (700, y, 2810, y + 86), color, outline=(35, 55, 92), width=8, radius=43)
        elif kind == "round":
            for x, color in [(1050, (86, 126, 255)), (1900, (242, 190, 54)), (2750, (242, 94, 132))]:
                shadow(draw, (x - 210, 1340, x + 210, 1465), 42)
                draw.ellipse((x - 210, 760, x + 210, 1180), fill=color, outline=(35, 55, 92), width=10)
        else:
            draw_shape_set(draw, 900, 780, 1.55)
            draw_shape_set(draw, 2020, 780, 1.55)
            if kind == "shape-sort":
                for x, color in [(680, (231, 240, 255)), (1640, (255, 236, 244)), (2600, (231, 255, 241))]:
                    rounded(draw, (x, 1490, x + 560, 1690), color, outline=(35, 55, 92), width=8, radius=50)

    elif "mango" in kind or kind == "counting-useful":
        if kind == "mango-compare":
            for i in range(3):
                draw_mango(draw, 700 + i * 260, 970, 1.15)
            for i in range(5):
                draw_mango(draw, 1900 + i * 220, 970, 1.0)
        elif kind == "mango-share":
            for i in range(6):
                draw_mango(draw, 900 + i * 330, 680, .9)
            for x in [1300, 2470]:
                draw.ellipse((x - 360, 1330, x + 360, 1690), fill=(222, 242, 255, 240), outline=(35, 55, 92), width=8)
                for i in range(3):
                    draw_mango(draw, x - 170 + i * 170, 1450, .62)
        else:
            for i in range(8):
                draw_mango(draw, 850 + (i % 4) * 390, 760 + (i // 4) * 430, .98, i + 1)
            text_center(draw, (2420, 1220, 3210, 1460), "8", (22, 38, 75), FONT_BIG)

    elif "10" in kind or kind == "ten-frame":
        for i in range(10):
            x = 820 + (i % 5) * 420
            y = 750 + (i // 5) * 430
            draw_block(draw, x, y, .9, (86, 126, 255) if i < 5 else (67, 186, 130), i + 1)
        if kind == "pairs-10":
            text_center(draw, (2500, 780, 3380, 1020), "4 + 6", (236, 72, 87), FONT_BIG)
            text_center(draw, (2500, 1160, 3380, 1400), "7 + 3", (236, 72, 87), FONT_BIG)

    elif "veg" in kind or kind in {"farm", "farmer-count"}:
        veg_colors = [(236, 95, 82), (67, 186, 130), (246, 190, 54)]
        for r in range(3):
            for c in range(5):
                x, y = 720 + c * 330, 720 + r * 290
                draw.ellipse((x - 82, y - 58, x + 82, y + 70), fill=veg_colors[(r + c) % 3], outline=(35, 55, 92), width=7)
                draw.polygon([(x - 34, y - 60), (x + 34, y - 60), (x, y - 142)], fill=(62, 152, 82))
        if kind == "farmer-count":
            draw_person(draw, 2840, 1320, 1.35, (67, 186, 130))

    elif "family" in kind:
        for i, s in enumerate([1.28, 1.1, .88, .82, .98]):
            draw_person(draw, 760 + i * 520, 1280, s, [(86, 126, 255), (67, 186, 130), (242, 94, 132), (246, 190, 54), (150, 112, 255)][i])
            if kind == "family-count":
                text_center(draw, (665 + i * 520, 500, 855 + i * 520, 640), str(i + 1), (22, 38, 75), FONT_NUM)

    elif "number" in kind:
        if kind == "number-order":
            for i in range(1, 11):
                draw_block(draw, 520 + i * 285, 1080, .62, (86, 126, 255), i)
            draw.line((770, 1430, 3250, 1430), fill=(236, 72, 87), width=16)
            draw.polygon([(3330, 1430), (3225, 1368), (3225, 1492)], fill=(236, 72, 87))
        else:
            for i in range(9):
                draw_block(draw, 850 + (i % 5) * 430, 850 + (i // 5) * 390, .7, [(86, 126, 255), (67, 186, 130), (242, 94, 132)][i % 3], i + 1)

    elif "utsav" in kind or kind == "groups":
        for i in range(12):
            x = 520 + i * 270
            y = 620 + (i % 2) * 220
            draw.ellipse((x - 58, y - 58, x + 58, y + 58), fill=(255, 198, 58), outline=(35, 55, 92), width=6)
            draw.line((x, y + 58, x, y + 430), fill=(35, 55, 92), width=5)
        if kind == "groups":
            for x in [970, 1900, 2830]:
                rounded(draw, (x - 310, 1360, x + 310, 1680), (255, 255, 255, 205), outline=(86, 126, 255), width=8, radius=80)
                for j in range(3):
                    draw_mango(draw, x - 170 + j * 170, 1510, .42)

    elif kind in {"morning", "day", "night", "clock"}:
        if kind == "clock":
            draw_clock(draw, 980, 1060, 7, 0, 1.0)
            draw_clock(draw, 1930, 1060, 1, 30, 1.0)
            draw_clock(draw, 2880, 1060, 9, 0, 1.0)
        else:
            if kind == "morning":
                draw.ellipse((620, 520, 960, 860), fill=(255, 210, 78), outline=(35, 55, 92), width=8)
                draw_person(draw, 1970, 1300, 1.25, (86, 126, 255))
                draw_clock(draw, 2870, 930, 7, 0, .78)
            elif kind == "day":
                draw.ellipse((630, 380, 980, 730), fill=(255, 210, 78), outline=(35, 55, 92), width=8)
                draw_person(draw, 1600, 1300, 1.1, (67, 186, 130))
                draw_person(draw, 2160, 1300, 1.1, (242, 94, 132))
                draw_clock(draw, 2920, 920, 1, 30, .78)
            else:
                draw.ellipse((580, 430, 930, 780), fill=(80, 118, 220), outline=(35, 55, 92), width=8)
                draw.ellipse((700, 360, 990, 660), fill=(255, 255, 255))
                rounded(draw, (1540, 1320, 2560, 1580), (255, 228, 173), outline=(35, 55, 92), width=8, radius=80)
                draw_clock(draw, 2920, 920, 9, 0, .78)

    elif "money" in kind:
        for i, value in enumerate(["1", "2", "5", "10", "1", "2", "5", "10"]):
            draw_coin(draw, 780 + (i % 4) * 450, 850 + (i // 4) * 420, 1.1, value)
        if kind == "money-buy":
            rounded(draw, (2500, 690, 3220, 1280), (255, 255, 255, 210), outline=(236, 72, 87), width=10, radius=90)
            draw_toy(draw, 2860, 1020, "car", 1.35)
        elif kind == "money-less":
            draw.line((2540, 1320, 3230, 720), fill=(67, 186, 130), width=22)
            draw.polygon([(3280, 675), (3160, 710), (3240, 800)], fill=(67, 186, 130))

    elif "toy" in kind:
        toys = ["ball", "car", "bear", "ball", "car", "bear", "ball", "car"]
        for i, toy in enumerate(toys):
            draw_toy(draw, 700 + (i % 4) * 720, 820 + (i // 4) * 520, toy, 1.05)
            if kind == "toy-count":
                text_center(draw, (610 + (i % 4) * 720, 480 + (i // 4) * 520, 790 + (i % 4) * 720, 610 + (i // 4) * 520), str(i + 1), (22, 38, 75), FONT_NUM)
        if kind == "toy-keep":
            rounded(draw, (2300, 1280, 3240, 1700), (171, 214, 255, 225), outline=(35, 55, 92), width=10, radius=80)

    elif "times" in kind or "repeat" in kind:
        for i in range(5):
            draw_person(draw, 780 + i * 560, 1320, .9, (86, 126, 255))
            draw.arc((690 + i * 560, 650, 870 + i * 560, 830), 20, 330, fill=(236, 72, 87), width=12)
        if "compare" in kind:
            for x in [1040, 2440]:
                rounded(draw, (x - 470, 1420, x + 470, 1710), (255, 255, 255, 190), outline=(67, 186, 130), width=8, radius=70)

    return image.convert("RGB")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for scene_id, kind, bg_slug in SCENES:
        draw_scene(scene_id, kind, bg_slug).save(OUT / f"{scene_id}.png", compress_level=3)
    print(f"Wrote {len(SCENES)} AI-style Class 1 mathematics images to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
