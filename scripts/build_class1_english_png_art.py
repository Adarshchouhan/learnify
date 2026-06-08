from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build_class1_english_art import SCENES


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "question-art" / "class1-english-png"
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


FONT_TITLE = font(116, True)
FONT_LABEL = font(54, True)
FONT_SMALL = font(42, True)


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def draw_background(draw: ImageDraw.ImageDraw, c1: str, c2: str) -> None:
    start = hex_to_rgb(c1)
    end = hex_to_rgb(c2)
    for y in range(SIZE[1]):
        t = y / SIZE[1]
        color = tuple(lerp(start[i], end[i], t * 0.72) for i in range(3))
        draw.line([(0, y), (SIZE[0], y)], fill=color)
    draw.ellipse((2600, -320, 4280, 1360), fill=(255, 255, 255, 82))
    draw.ellipse((-380, 1180, 920, 2480), fill=(255, 255, 255, 88))
    draw.rounded_rectangle((150, 145, 3690, 2015), radius=150, outline=(255, 255, 255, 145), width=7)


def add_texture(image: Image.Image, seed: int) -> None:
    rng = random.Random(seed)
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    for _ in range(950):
        x = rng.randint(0, SIZE[0])
        y = rng.randint(0, SIZE[1])
        r = rng.randint(2, 12)
        shade = rng.choice([(255, 255, 255, 16), (44, 73, 125, 8), (255, 228, 146, 14)])
        draw.ellipse((x - r, y - r, x + r, y + r), fill=shade)
    for _ in range(42):
        x = rng.randint(-200, SIZE[0])
        y = rng.randint(-200, SIZE[1])
        w = rng.randint(220, 620)
        h = rng.randint(90, 240)
        draw.ellipse((x, y, x + w, y + h), fill=(255, 255, 255, rng.randint(12, 34)))
    image.alpha_composite(overlay)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill, outline=None, width=1, radius=40) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_center(draw: ImageDraw.ImageDraw, box, text: str, fill, fnt) -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    x = box[0] + ((box[2] - box[0]) - (bbox[2] - bbox[0])) / 2
    y = box[1] + ((box[3] - box[1]) - (bbox[3] - bbox[1])) / 2
    draw.text((x, y), text, fill=fill, font=fnt)


def draw_shadow(draw, box, alpha=42) -> None:
    draw.ellipse(box, fill=(28, 45, 72, alpha))


def draw_person(draw, x: int, y: int, scale: float = 1.0, shirt=(93, 92, 255), pose="wave") -> None:
    s = scale
    draw_shadow(draw, (x - 185 * s, y + 280 * s, x + 185 * s, y + 365 * s), 34)
    draw.ellipse((x - 80 * s, y - 300 * s, x + 80 * s, y - 140 * s), fill=(255, 208, 161), outline=(38, 54, 88), width=int(8 * s))
    draw.arc((x - 42 * s, y - 250 * s, x + 42 * s, y - 185 * s), 20, 160, fill=(38, 54, 88), width=int(5 * s))
    draw.ellipse((x - 36 * s, y - 240 * s, x - 18 * s, y - 222 * s), fill=(38, 54, 88))
    draw.ellipse((x + 18 * s, y - 240 * s, x + 36 * s, y - 222 * s), fill=(38, 54, 88))
    rounded(draw, (int(x - 110 * s), int(y - 145 * s), int(x + 110 * s), int(y + 125 * s)), shirt, radius=int(58 * s))
    if pose == "wave":
        draw.line((x - 105 * s, y - 60 * s, x - 230 * s, y - 190 * s), fill=(255, 208, 161), width=int(34 * s))
        draw.ellipse((x - 266 * s, y - 230 * s, x - 204 * s, y - 168 * s), fill=(255, 208, 161))
        draw.line((x + 105 * s, y - 60 * s, x + 210 * s, y + 40 * s), fill=(255, 208, 161), width=int(34 * s))
    elif pose == "clap":
        draw.line((x - 95 * s, y - 55 * s, x - 18 * s, y - 24 * s), fill=(255, 208, 161), width=int(34 * s))
        draw.line((x + 95 * s, y - 55 * s, x + 18 * s, y - 24 * s), fill=(255, 208, 161), width=int(34 * s))
        draw.ellipse((x - 48 * s, y - 54 * s, x - 2 * s, y - 4 * s), fill=(255, 208, 161))
        draw.ellipse((x + 2 * s, y - 54 * s, x + 48 * s, y - 4 * s), fill=(255, 208, 161))
    else:
        draw.line((x - 105 * s, y - 55 * s, x - 230 * s, y + 20 * s), fill=(255, 208, 161), width=int(34 * s))
        draw.line((x + 105 * s, y - 55 * s, x + 230 * s, y + 20 * s), fill=(255, 208, 161), width=int(34 * s))
    draw.line((x - 45 * s, y + 120 * s, x - 90 * s, y + 300 * s), fill=(52, 73, 122), width=int(38 * s))
    draw.line((x + 45 * s, y + 120 * s, x + 95 * s, y + 300 * s), fill=(52, 73, 122), width=int(38 * s))


def draw_tree(draw, x: int, y: int, scale: float = 1.0) -> None:
    s = scale
    rounded(draw, (int(x - 45 * s), int(y - 20 * s), int(x + 45 * s), int(y + 270 * s)), (138, 84, 55), radius=int(30 * s))
    for dx, dy, r, color in [(-100, -80, 150, (64, 173, 96)), (70, -120, 170, (55, 155, 87)), (0, -230, 160, (88, 191, 118))]:
        draw.ellipse((x + (dx - r) * s, y + (dy - r) * s, x + (dx + r) * s, y + (dy + r) * s), fill=color)
        draw.ellipse((x + (dx - r * .55) * s, y + (dy - r * .7) * s, x + (dx + r * .15) * s, y + (dy - r * .2) * s), fill=(255, 255, 255, 38))


def draw_sun(draw, x: int, y: int, r: int) -> None:
    for angle in range(0, 360, 30):
        x1 = x + math.cos(math.radians(angle)) * (r + 30)
        y1 = y + math.sin(math.radians(angle)) * (r + 30)
        x2 = x + math.cos(math.radians(angle)) * (r + 120)
        y2 = y + math.sin(math.radians(angle)) * (r + 120)
        draw.line((x1, y1, x2, y2), fill=(255, 188, 48), width=18)
    draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 215, 87), outline=(255, 172, 52), width=8)


def draw_cloud(draw, x: int, y: int, scale: float = 1.0, rain: bool = False) -> None:
    s = scale
    color = (245, 250, 255)
    draw.ellipse((x - 220 * s, y - 60 * s, x - 60 * s, y + 110 * s), fill=color)
    draw.ellipse((x - 95 * s, y - 140 * s, x + 105 * s, y + 90 * s), fill=color)
    draw.ellipse((x + 50 * s, y - 40 * s, x + 250 * s, y + 120 * s), fill=color)
    rounded(draw, (int(x - 230 * s), int(y + 20 * s), int(x + 260 * s), int(y + 145 * s)), color, radius=int(55 * s))
    if rain:
        for dx in [-150, -40, 70, 170]:
            draw.line((x + dx * s, y + 185 * s, x + (dx - 48) * s, y + 310 * s), fill=(74, 153, 255), width=int(16 * s))


def draw_book(draw, x: int, y: int, scale: float = 1.0, cover=(91, 114, 255)) -> None:
    s = scale
    rounded(draw, (int(x - 250 * s), int(y - 180 * s), int(x + 250 * s), int(y + 180 * s)), (255, 255, 255, 238), outline=(169, 190, 225), width=int(7 * s), radius=int(42 * s))
    draw.line((x, y - 165 * s, x, y + 165 * s), fill=(169, 190, 225), width=int(6 * s))
    rounded(draw, (int(x - 225 * s), int(y - 155 * s), int(x - 25 * s), int(y + 155 * s)), cover, radius=int(32 * s))
    for yy in [-82, -28, 28, 84]:
        draw.line((x + 45 * s, y + yy * s, x + 210 * s, y + yy * s), fill=(130, 151, 190), width=int(5 * s))


def draw_hand(draw, x: int, y: int, scale: float = 1.0, angle: float = 0) -> None:
    s = scale
    rounded(draw, (int(x - 62 * s), int(y - 20 * s), int(x + 62 * s), int(y + 230 * s)), (255, 206, 158), outline=(142, 87, 54), width=int(7 * s), radius=int(45 * s))
    for i, dx in enumerate([-82, -32, 18, 68]):
        rounded(draw, (int(x + dx * s), int(y - (160 + i * 8) * s), int(x + (dx + 48) * s), int(y + 35 * s)), (255, 206, 158), outline=(142, 87, 54), width=int(6 * s), radius=int(25 * s))
    rounded(draw, (int(x - 140 * s), int(y + 20 * s), int(x - 52 * s), int(y + 128 * s)), (255, 206, 158), outline=(142, 87, 54), width=int(6 * s), radius=int(38 * s))


def draw_leg_pair(draw, x: int, y: int, scale: float = 1.0) -> None:
    s = scale
    draw_shadow(draw, (x - 220 * s, y + 315 * s, x + 260 * s, y + 405 * s), 36)
    draw.line((x - 70 * s, y - 160 * s, x - 130 * s, y + 180 * s), fill=(62, 90, 150), width=int(62 * s))
    draw.line((x + 80 * s, y - 160 * s, x + 180 * s, y + 165 * s), fill=(62, 90, 150), width=int(62 * s))
    rounded(draw, (int(x - 220 * s), int(y + 150 * s), int(x - 40 * s), int(y + 230 * s)), (255, 122, 74), radius=int(35 * s))
    rounded(draw, (int(x + 100 * s), int(y + 135 * s), int(x + 310 * s), int(y + 218 * s)), (255, 122, 74), radius=int(35 * s))


def draw_cow(draw, x: int, y: int, scale: float = 1.0) -> None:
    s = scale
    draw_shadow(draw, (x - 270 * s, y + 205 * s, x + 320 * s, y + 300 * s), 34)
    draw.ellipse((x - 270 * s, y - 120 * s, x + 220 * s, y + 170 * s), fill=(255, 255, 245), outline=(79, 82, 72), width=int(8 * s))
    draw.ellipse((x - 140 * s, y - 55 * s, x + 15 * s, y + 70 * s), fill=(74, 72, 62))
    draw.ellipse((x + 95 * s, y - 80 * s, x + 355 * s, y + 115 * s), fill=(255, 255, 245), outline=(79, 82, 72), width=int(8 * s))
    for dx in [-150, 90]:
        draw.line((x + dx * s, y + 120 * s, x + (dx - 30) * s, y + 270 * s), fill=(79, 82, 72), width=int(18 * s))
    draw.ellipse((x + 178 * s, y - 20 * s, x + 202 * s, y + 4 * s), fill=(35, 35, 35))


def draw_goat(draw, x: int, y: int, scale: float = 1.0) -> None:
    s = scale
    draw_shadow(draw, (x - 220 * s, y + 190 * s, x + 230 * s, y + 270 * s), 32)
    draw.ellipse((x - 190 * s, y - 95 * s, x + 130 * s, y + 125 * s), fill=(236, 205, 148), outline=(94, 76, 55), width=int(8 * s))
    draw.ellipse((x + 80 * s, y - 160 * s, x + 255 * s, y + 18 * s), fill=(236, 205, 148), outline=(94, 76, 55), width=int(8 * s))
    draw.arc((x + 95 * s, y - 235 * s, x + 180 * s, y - 110 * s), 190, 330, fill=(94, 76, 55), width=int(10 * s))
    draw.arc((x + 170 * s, y - 235 * s, x + 255 * s, y - 110 * s), 210, 350, fill=(94, 76, 55), width=int(10 * s))
    for dx in [-110, 60]:
        draw.line((x + dx * s, y + 85 * s, x + (dx - 25) * s, y + 230 * s), fill=(94, 76, 55), width=int(16 * s))


def draw_hen(draw, x: int, y: int, scale: float = 1.0) -> None:
    s = scale
    draw_shadow(draw, (x - 150 * s, y + 135 * s, x + 150 * s, y + 200 * s), 30)
    draw.ellipse((x - 145 * s, y - 90 * s, x + 120 * s, y + 145 * s), fill=(250, 250, 238), outline=(91, 76, 58), width=int(7 * s))
    draw.ellipse((x + 50 * s, y - 170 * s, x + 178 * s, y - 42 * s), fill=(250, 250, 238), outline=(91, 76, 58), width=int(7 * s))
    draw.polygon([(x + 173 * s, y - 105 * s), (x + 270 * s, y - 78 * s), (x + 173 * s, y - 50 * s)], fill=(255, 175, 58))
    draw.ellipse((x + 85 * s, y - 210 * s, x + 150 * s, y - 155 * s), fill=(228, 62, 70))


def draw_food(draw, x: int, y: int, kind: str) -> None:
    if kind == "fruit":
        draw.ellipse((x - 105, y - 95, x + 105, y + 115), fill=(236, 77, 86), outline=(132, 35, 45), width=7)
        draw.line((x, y - 100, x + 35, y - 170), fill=(82, 98, 48), width=12)
        draw.ellipse((x + 18, y - 190, x + 115, y - 130), fill=(76, 167, 93))
    elif kind == "rice":
        rounded(draw, (x - 150, y - 70, x + 150, y + 95), (255, 255, 255), outline=(95, 115, 145), width=7, radius=70)
        draw.arc((x - 150, y - 160, x + 150, y + 60), 0, 180, fill=(95, 115, 145), width=8)
    elif kind == "milk":
        rounded(draw, (x - 90, y - 170, x + 90, y + 130), (255, 255, 255), outline=(87, 117, 163), width=8, radius=32)
        rounded(draw, (x - 55, y - 210, x + 55, y - 150), (111, 181, 255), radius=18)
        rounded(draw, (x - 62, y - 30, x + 62, y + 35), (111, 181, 255), radius=18)


def draw_rainbow(draw, x: int, y: int, scale: float = 1.0) -> None:
    colors = [(235, 66, 82), (255, 146, 59), (255, 215, 80), (76, 186, 94), (60, 150, 245), (123, 94, 220)]
    for index, color in enumerate(colors):
        w = int(78 * scale)
        box = (int(x - (520 - index * 78) * scale), int(y - (520 - index * 78) * scale), int(x + (520 - index * 78) * scale), int(y + (520 - index * 78) * scale))
        draw.arc(box, 180, 360, fill=color, width=w)


def draw_scene(draw: ImageDraw.ImageDraw, scene_id: str) -> None:
    ground = (193, 236, 204)
    draw.ellipse((-350, 1460, 4300, 2500), fill=ground)
    if "hands" in scene_id:
        draw_book(draw, 2580, 1060, 1.35, (103, 137, 255))
        draw_person(draw, 1200, 1330, 1.55, pose="clap", shirt=(255, 154, 74))
        draw_hand(draw, 2020, 1080, 1.6)
        draw.arc((1730, 570, 2420, 1270), 210, 330, fill=(73, 92, 255), width=28)
        draw.arc((1600, 670, 2300, 1390), 210, 330, fill=(255, 190, 55), width=22)
    elif "legs" in scene_id:
        draw_leg_pair(draw, 1320, 1220, 2.2)
        draw_person(draw, 2300, 1350, 1.35, pose="arms", shirt=(82, 174, 238))
        for x in [1850, 2100, 2350]:
            draw.ellipse((x - 120, 1580, x + 120, 1665), fill=(90, 111, 155, 70))
    elif "eyes" in scene_id:
        rounded(draw, (680, 620, 1910, 1340), (255, 255, 255, 225), outline=(118, 146, 208), width=12, radius=90)
        draw.ellipse((935, 825, 1250, 1140), fill=(255, 255, 255), outline=(28, 43, 70), width=11)
        draw.ellipse((1330, 825, 1645, 1140), fill=(255, 255, 255), outline=(28, 43, 70), width=11)
        draw.ellipse((1055, 940, 1145, 1030), fill=(55, 93, 255))
        draw.ellipse((1450, 940, 1540, 1030), fill=(55, 93, 255))
        draw.arc((2160, 770, 2600, 1235), 70, 290, fill=(255, 180, 120), width=60)
        draw.arc((2260, 870, 2480, 1130), 70, 290, fill=(170, 96, 66), width=18)
    elif "body" in scene_id:
        draw_person(draw, 1300, 1360, 1.95, pose="arms", shirt=(145, 92, 255))
        for xy in [(980, 760), (1580, 760), (880, 1600), (1740, 1600)]:
            draw.ellipse((xy[0]-42, xy[1]-42, xy[0]+42, xy[1]+42), fill=(255, 215, 87))
    elif "hello" in scene_id or "goodbye" in scene_id or "thank" in scene_id:
        draw_person(draw, 1050, 1350, 1.65, pose="wave", shirt=(92, 120, 255))
        draw_person(draw, 1780, 1350, 1.65, pose="wave", shirt=(255, 154, 74))
        rounded(draw, (1160, 430, 2100, 650), (255, 255, 255, 230), outline=(185, 204, 235), width=6, radius=80)
        draw.line((1390, 640, 1290, 780), fill=(255, 255, 255, 210), width=28)
    elif "good-morning" in scene_id:
        draw_sun(draw, 910, 610, 220)
        draw_person(draw, 1640, 1390, 1.7, pose="wave", shirt=(255, 171, 64))
    elif "plant" in scene_id or "living" in scene_id or "care-living" in scene_id:
        draw_sun(draw, 2850, 450, 190)
        for x in [760, 1050, 1370]:
            draw.line((x, 1450, x, 1160), fill=(54, 145, 86), width=32)
            draw.ellipse((x - 170, 1090, x + 10, 1280), fill=(86, 185, 110))
            draw.ellipse((x - 10, 1050, x + 180, 1245), fill=(100, 203, 128))
        draw_cloud(draw, 2000, 590, 1.05, rain="plant" in scene_id)
    elif "animal" in scene_id:
        draw_tree(draw, 690, 1130, 1.25)
        draw_cow(draw, 1530, 1340, 1.15)
        draw_goat(draw, 2300, 1345, 1.0)
        draw_hen(draw, 2860, 1420, .9)
    elif "cap" in scene_id or "monkey" in scene_id or "story" in scene_id:
        draw_tree(draw, 1520, 980, 1.55)
        for x, y in [(800, 1220), (1900, 830), (2200, 1160)]:
            draw.ellipse((x - 120, y - 90, x + 120, y + 120), fill=(147, 93, 52), outline=(78, 52, 35), width=8)
            draw.ellipse((x - 86, y - 40, x + 86, y + 80), fill=(231, 167, 102))
            draw.arc((x - 55, y, x + 55, y + 55), 20, 160, fill=(55, 42, 35), width=6)
            rounded(draw, (x - 105, y - 160, x + 110, y - 95), (238, 61, 88), radius=38)
        if "seller" in scene_id:
            draw_person(draw, 2720, 1420, 1.45, shirt=(88, 156, 245))
    elif "farm" in scene_id or "farmer" in scene_id:
        draw_sun(draw, 3050, 500, 160)
        rounded(draw, (660, 790, 1510, 1510), (235, 84, 78), outline=(148, 54, 48), width=10, radius=34)
        draw.polygon([(575, 810), (1085, 430), (1610, 810)], fill=(92, 123, 190))
        draw.rectangle((1040, 1130, 1220, 1450), fill=(89, 57, 43))
        for x in [1900, 2110, 2320, 2530]:
            draw.arc((x - 110, 1280, x + 110, 1620), 180, 360, fill=(65, 150, 84), width=22)
        draw_cow(draw, 2220, 1250, .75)
        draw_hen(draw, 2830, 1350, .7)
        if "farmer" in scene_id:
            draw_person(draw, 2580, 1370, 1.45, shirt=(80, 174, 96))
    elif "food" in scene_id or "eat" in scene_id or "healthy" in scene_id:
        rounded(draw, (650, 750, 2360, 1520), (255, 255, 255, 230), outline=(198, 214, 238), width=8, radius=90)
        for i, kind in enumerate(["fruit", "rice", "milk"]):
            draw_food(draw, 1040 + i * 510, 1120, kind)
        if "clean" in scene_id or "how-eat" in scene_id:
            draw_cloud(draw, 2600, 610, .7, rain=True)
    elif "summer" in scene_id:
        draw_sun(draw, 1220, 620, 260)
        draw_person(draw, 2050, 1430, 1.55, shirt=(255, 136, 75))
        draw.ellipse((2420, 1520, 2860, 1780), fill=(85, 183, 255))
    elif "rainy" in scene_id:
        draw_cloud(draw, 1200, 530, 1.6, rain=True)
        draw.arc((1880, 1020, 2640, 1600), 180, 360, fill=(255, 91, 118), width=70)
        draw.line((2260, 1320, 2260, 1660), fill=(54, 68, 100), width=24)
    elif "winter" in scene_id or "season-clothes" in scene_id:
        draw_cloud(draw, 1150, 580, 1.2, rain=False)
        draw_person(draw, 1730, 1400, 1.6, shirt=(95, 126, 255))
        for x in [900, 2380, 2620]:
            draw.line((x, 820, x, 1040), fill=(255, 255, 255), width=16)
            draw.line((x - 70, 930, x + 70, 930), fill=(255, 255, 255), width=16)
    elif "rainbow" in scene_id:
        draw_cloud(draw, 850, 1280, 1.0)
        draw_cloud(draw, 2280, 1280, 1.0)
        draw_rainbow(draw, 1560, 1410, 1.6)
        if "children" in scene_id or "like" in scene_id:
            draw_person(draw, 1060, 1540, 1.05, shirt=(255, 148, 79))
            draw_person(draw, 2100, 1540, 1.05, shirt=(103, 128, 255))
    else:
        draw_person(draw, 1350, 1380, 1.65)


def render(scene_id: str, title: str, c1: str, c2: str) -> Image.Image:
    image = Image.new("RGBA", SIZE, "#ffffff")
    draw = ImageDraw.Draw(image, "RGBA")
    draw_background(draw, c1, c2)
    add_texture(image, abs(hash(scene_id)) % 100000)
    draw_scene(draw, scene_id)
    draw.ellipse((2380, 70, 3950, 1540), fill=(255, 255, 255, 34))
    return image.convert("RGB")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for scene_id, (title, _items, c1, c2) in SCENES.items():
        image = render(scene_id, title, c1, c2)
        image.save(OUT / f"{scene_id}.png", optimize=True)
    print(f"Generated {len(SCENES)} 4K PNG question images in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
