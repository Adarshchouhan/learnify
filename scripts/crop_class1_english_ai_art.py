from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SHEETS = ROOT / "assets" / "question-art" / "class1-english-ai-sheets"
OUT = ROOT / "assets" / "question-art" / "class1-english-ai"

SLUGS = [
    ["hands-clap", "legs-walk", "eyes-ears", "body-parts", "hello-meet", "good-morning"],
    ["thank-you", "goodbye", "living-things", "plants-need", "care-living", "animals-need"],
    ["cap-seller-caps", "monkeys-caps", "caps-back", "story-learn", "farm-see", "farmer-works"],
    ["farm-animals", "farm-useful", "need-food", "eat-food", "clean-food", "not-waste-food"],
    ["why-eat-food", "healthy-food", "when-eat", "how-eat", "summer", "rainy-days"],
    ["winter", "season-clothes", "rainbow-see", "rainbow-when", "rainbow-colours", "rainbow-like"],
]


def crop_grid(image: Image.Image, index: int) -> Image.Image:
    width, height = image.size
    col = index % 3
    row = index // 3
    x0 = round(col * width / 3)
    x1 = round((col + 1) * width / 3)
    y0 = round(row * height / 2)
    y1 = round((row + 1) * height / 2)
    crop = image.crop((x0, y0, x1, y1))
    return crop.resize((3840, 2160), Image.Resampling.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    for sheet_index, slugs in enumerate(SLUGS, start=1):
        sheet_path = SHEETS / f"sheet-{sheet_index:02d}.png"
        if not sheet_path.exists():
            raise FileNotFoundError(sheet_path)
        with Image.open(sheet_path) as image:
            rgb = image.convert("RGB")
            for index, slug in enumerate(slugs):
                crop_grid(rgb, index).save(OUT / f"{slug}.png", compress_level=3)
                written += 1
    print(f"Cropped {written} AI-style Class 1 English images into {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
