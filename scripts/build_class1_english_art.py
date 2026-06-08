from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "question-art" / "class1-english"


SCENES = {
    "hands-clap": ("What can my hands do?", ["hands", "clap", "hold"], "#ffcf4a", "#8bd3ff"),
    "legs-walk": ("What can my legs do?", ["legs", "walk", "run"], "#9ee6a8", "#ffd6a5"),
    "eyes-ears": ("What can my eyes and ears do?", ["eyes", "ears", "see", "hear"], "#b8c0ff", "#caffbf"),
    "body-parts": ("What are the parts of my body?", ["body", "hands", "legs"], "#ffc6ff", "#fdffb6"),
    "hello-meet": ("What do we say when we meet?", ["hello", "smile", "friend"], "#a0c4ff", "#ffd6a5"),
    "good-morning": ("What do we say in the morning?", ["sun", "morning", "greet"], "#fdffb6", "#9bf6ff"),
    "thank-you": ("What do we say when someone helps us?", ["thank", "help", "kind"], "#caffbf", "#ffd6e0"),
    "goodbye": ("What do we say when we leave?", ["bye", "wave", "leave"], "#bdb2ff", "#ffc6ff"),
    "living-things": ("What living things do we see?", ["plants", "animals", "birds"], "#caffbf", "#9bf6ff"),
    "plants-need": ("What do plants need?", ["water", "sun", "soil"], "#95d5b2", "#ffe066"),
    "animals-need": ("What do animals need?", ["food", "water", "care"], "#ffd6a5", "#a0c4ff"),
    "care-living": ("How should we care for living things?", ["kind", "water", "clean"], "#caffbf", "#ffd6e0"),
    "cap-seller-caps": ("What did the cap-seller carry?", ["caps", "seller", "walk"], "#ffadad", "#fdffb6"),
    "monkeys-caps": ("What did the monkeys do?", ["monkeys", "caps", "tree"], "#ffd6a5", "#caffbf"),
    "caps-back": ("How did the cap-seller get his caps back?", ["throw", "copy", "caps"], "#bdb2ff", "#ffd6a5"),
    "story-learn": ("What do we learn from the story?", ["think", "solve", "clever"], "#a0c4ff", "#ffc6ff"),
    "farm-see": ("What do we see on a farm?", ["farm", "plants", "animals"], "#caffbf", "#ffd6a5"),
    "farmer-works": ("Who works on a farm?", ["farmer", "crop", "care"], "#95d5b2", "#fdffb6"),
    "farm-animals": ("What animals can live on a farm?", ["cow", "goat", "hen"], "#ffd6a5", "#9bf6ff"),
    "farm-useful": ("Why is a farm useful?", ["food", "crops", "farmer"], "#caffbf", "#ffe066"),
    "need-food": ("Why do we need food?", ["energy", "grow", "healthy"], "#ffd6a5", "#caffbf"),
    "eat-food": ("What food do we eat?", ["rice", "fruit", "veg"], "#ffadad", "#fdffb6"),
    "clean-food": ("How do we keep food clean?", ["wash", "cover", "clean"], "#9bf6ff", "#caffbf"),
    "not-waste-food": ("Why should we not waste food?", ["share", "save", "food"], "#fdffb6", "#ffd6a5"),
    "why-eat-food": ("Why do we eat food?", ["energy", "grow", "play"], "#ffd6a5", "#a0c4ff"),
    "healthy-food": ("Which foods are healthy?", ["fruits", "vegetables", "milk"], "#caffbf", "#ffadad"),
    "when-eat": ("When do we eat food?", ["breakfast", "lunch", "dinner"], "#fdffb6", "#bdb2ff"),
    "how-eat": ("How should we eat?", ["wash", "chew", "clean"], "#9bf6ff", "#caffbf"),
    "summer": ("What happens in summer?", ["sun", "water", "light clothes"], "#ffe066", "#ffadad"),
    "rainy-days": ("What happens on rainy days?", ["rain", "umbrella", "plants"], "#9bf6ff", "#a0c4ff"),
    "winter": ("What happens in winter?", ["cold", "warm clothes", "night"], "#caf0f8", "#bdb2ff"),
    "season-clothes": ("Why do seasons change our clothes?", ["weather", "summer", "winter"], "#fdffb6", "#9bf6ff"),
    "rainbow-see": ("What do we see in a rainbow?", ["rainbow", "colours", "sky"], "#ffc6ff", "#9bf6ff"),
    "rainbow-when": ("When can we see a rainbow?", ["rain", "sun", "sky"], "#a0c4ff", "#fdffb6"),
    "rainbow-colours": ("What colours can a rainbow have?", ["red", "yellow", "green", "blue"], "#ffc6ff", "#caffbf"),
    "rainbow-like": ("Why do children like a rainbow?", ["bright", "pretty", "happy"], "#fdffb6", "#bdb2ff"),
}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def svg(scene_id: str, title: str, items: list[str], c1: str, c2: str) -> str:
    chips = "\n".join(
        f'<g transform="translate({170 + (i % 2) * 210},{430 + (i // 2) * 92})"><rect width="170" height="54" rx="27" fill="white" opacity=".82"/><text x="85" y="35" text-anchor="middle" font-size="24" font-weight="800" fill="#102044">{item}</text></g>'
        for i, item in enumerate(items[:4])
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="3840" height="2160" viewBox="0 0 3840 2160">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset=".52" stop-color="#f8fbff"/>
      <stop offset="1" stop-color="{c2}"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="36" stdDeviation="34" flood-color="#3a4a78" flood-opacity=".18"/></filter>
  </defs>
  <rect width="3840" height="2160" fill="url(#bg)"/>
  <circle cx="3080" cy="430" r="310" fill="#fff" opacity=".38"/>
  <circle cx="3270" cy="820" r="520" fill="#fff" opacity=".28"/>
  <circle cx="560" cy="1640" r="360" fill="#fff" opacity=".35"/>
  <g filter="url(#shadow)" transform="translate(470 430)">
    <rect width="1680" height="1110" rx="110" fill="#fff" opacity=".86"/>
    <circle cx="410" cy="420" r="180" fill="{c2}" opacity=".72"/>
    <circle cx="780" cy="365" r="220" fill="{c1}" opacity=".58"/>
    <rect x="250" y="670" width="1180" height="120" rx="60" fill="#eef5ff"/>
    <rect x="250" y="830" width="880" height="120" rx="60" fill="#f5efff"/>
    {chips}
  </g>
  <g transform="translate(2380 580)" filter="url(#shadow)">
    <circle cx="360" cy="360" r="350" fill="#ffffff" opacity=".9"/>
    <circle cx="260" cy="260" r="72" fill="#1e4fff"/>
    <circle cx="460" cy="260" r="72" fill="#ff8f3d"/>
    <path d="M220 470 Q360 590 510 470" fill="none" stroke="#102044" stroke-width="42" stroke-linecap="round"/>
    <rect x="110" y="720" width="520" height="170" rx="85" fill="#102044" opacity=".92"/>
    <text x="370" y="832" text-anchor="middle" font-family="Arial, sans-serif" font-size="58" font-weight="900" fill="#fff">Learn</text>
  </g>
  <text x="260" y="1950" font-family="Arial, sans-serif" font-size="62" font-weight="900" fill="#102044" opacity=".82">{title}</text>
</svg>'''


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for scene_id, (title, items, c1, c2) in SCENES.items():
        path = OUT / f"{scene_id}.svg"
        path.write_text(svg(scene_id, title, items, c1, c2), encoding="utf-8")
        manifest[title] = str(path.relative_to(ROOT)).replace("\\", "/")
    print(f"Wrote {len(SCENES)} Class 1 English question art files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

