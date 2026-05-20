from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = Path("data/manifest/class-6-12-pdf-manifest.json")


def load_manifest(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(payload.get("entries", []))


def build_command(entry: dict[str, Any]) -> list[str]:
    command = [
        sys.executable,
        "scripts/build_practice_data.py",
        "--pdf",
        entry["pdfPath"],
        "--class-level",
        str(entry["classLevel"]),
        "--subject",
        entry["subject"],
        "--book",
        entry["book"],
        "--chapter",
        entry["chapter"],
        "--chapter-number",
        str(entry["chapterNumber"]),
        "--output",
        entry["outputPath"],
    ]
    if entry.get("stream"):
        command.extend(["--stream", entry["stream"]])
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch generate Learnify practice JSON from a PDF manifest.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--limit", type=int, default=1, help="Number of manifest rows to generate. Use 0 for all rows.")
    parser.add_argument("--class-level", type=int, default=None)
    parser.add_argument("--subject", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--report", type=Path, default=Path("data/catalog/batch-generation-report.json"))
    args = parser.parse_args()

    entries = load_manifest(args.manifest)
    if args.class_level:
        entries = [entry for entry in entries if int(entry["classLevel"]) == args.class_level]
    if args.subject:
        entries = [entry for entry in entries if entry["subject"].lower() == args.subject.lower()]
    if args.limit > 0:
        entries = entries[: args.limit]

    if args.skip_existing:
        entries = [entry for entry in entries if not Path(entry["outputPath"]).exists()]

    if not entries:
        print("No manifest entries matched.")
        return 1

    report: list[dict[str, Any]] = []
    for entry in entries:
        command = build_command(entry)
        print(" ".join(command))
        if not args.dry_run:
            try:
                subprocess.run(command, check=True)
                report.append({"id": entry["id"], "outputPath": entry["outputPath"], "status": "generated"})
            except subprocess.CalledProcessError as error:
                report.append({"id": entry["id"], "outputPath": entry["outputPath"], "status": "failed", "returnCode": error.returncode})
        else:
            report.append({"id": entry["id"], "outputPath": entry["outputPath"], "status": "planned"})

    print(f"{'Planned' if args.dry_run else 'Generated'} {len(entries)} dataset(s).")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({"entries": report}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
