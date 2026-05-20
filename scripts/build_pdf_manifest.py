from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_ROOT = Path(r"D:\LX\all class pdf")
DEFAULT_OUTPUT = Path("data/manifest/class-6-12-pdf-manifest.json")


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def short_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]


def parse_class(part: str) -> int | None:
    match = re.search(r"class\s*(\d{1,2})", part, re.IGNORECASE)
    if not match:
        return None
    class_level = int(match.group(1))
    return class_level if 6 <= class_level <= 12 else None


def parse_subject_book(parts: list[str]) -> tuple[str | None, str]:
    if not parts:
        return None, "Unknown Book"
    book = parts[-1]
    subject = book.split("-")[0].strip() or book
    return subject, book


def chapter_from_pdf(pdf_path: Path, index: int) -> tuple[int, str]:
    stem = pdf_path.stem
    match = re.search(r"(\d{2,3})$", stem)
    number = int(match.group(1)[-2:]) if match else index
    title = f"Chapter {number}"
    return number, title


def detect_stream(relative_parts: list[str]) -> str | None:
    known = {"arts", "commerce", "science", "pcb", "pcm", "humanities"}
    for part in relative_parts:
        value = part.lower().strip()
        if value in known:
            return part
    return None


def build_manifest(source_root: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    if not source_root.exists():
        return {
            "version": 1,
            "sourceRoot": str(source_root),
            "generatedCount": 0,
            "entries": [],
            "warnings": [f"Source root not found: {source_root}"],
        }

    pdfs = sorted(path for path in source_root.rglob("*.pdf") if not path.name.lower().endswith("ps.pdf"))
    for index, pdf_path in enumerate(pdfs, start=1):
        relative = pdf_path.relative_to(source_root)
        relative_key = str(relative).replace("\\", "/")
        parts = list(relative.parts)
        class_level = next((parse_class(part) for part in parts if parse_class(part)), None)
        if class_level is None:
            continue
        stream = detect_stream(parts)
        subject, book = parse_subject_book(parts[:-1])
        chapter_number, chapter = chapter_from_pdf(pdf_path, index)
        entry_id = "-".join(
            [
                f"class-{class_level}",
                slugify(stream) if stream else "",
                slugify(subject or "subject"),
                slugify(book),
                f"chapter-{chapter_number}",
                slugify(pdf_path.stem),
                short_hash(relative_key),
            ]
        ).replace("--", "-")
        entries.append(
            {
                "id": entry_id,
                "classLevel": class_level,
                "stream": stream,
                "subject": subject or "Unknown",
                "book": book,
                "chapter": chapter,
                "chapterNumber": chapter_number,
                "pdfPath": str(pdf_path),
                "relativePath": str(relative),
                "outputPath": str(
                    Path("data")
                    / "practice"
                    / f"class-{class_level}"
                    / (slugify(stream) if stream else slugify(book))
                    / f"{slugify(chapter)}-{slugify(pdf_path.stem)}-{short_hash(relative_key)}.json"
                ),
            }
        )

    return {
        "version": 1,
        "sourceRoot": str(source_root),
        "generatedCount": len(entries),
        "entries": entries,
        "warnings": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan class 6-12 NCERT PDFs into a Learnify generation manifest.")
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = build_manifest(args.source_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"PDF entries: {manifest['generatedCount']}")
    for warning in manifest.get("warnings", []):
        print(f"Warning: {warning}")
    return 0 if not manifest.get("warnings") else 1


if __name__ == "__main__":
    raise SystemExit(main())
