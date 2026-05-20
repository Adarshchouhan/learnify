from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data" / "manifest" / "class-6-12-pdf-manifest.json"
DEFAULT_ACTIVE = ROOT / "data" / "catalog" / "active-datasets.json"
DEFAULT_OUTPUT = ROOT / "data" / "catalog" / "content-catalog.json"
PRACTICE_ROOT = ROOT / "data" / "practice"


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def generated_datasets() -> dict[str, dict[str, Any]]:
    datasets: dict[str, dict[str, Any]] = {}
    if not PRACTICE_ROOT.exists():
        return datasets
    for json_path in sorted(PRACTICE_ROOT.rglob("*.json")):
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        source = payload.get("source", {})
        json_rel = rel(json_path)
        datasets[json_rel] = {
            "id": json_rel.removesuffix(".json"),
            "jsonPath": json_rel,
            "hasJson": True,
            "activityCount": len(payload.get("activities", [])),
            "classLevel": source.get("classLevel"),
            "stream": source.get("stream"),
            "subject": source.get("subject"),
            "book": source.get("book"),
            "chapter": source.get("chapter"),
            "chapterNumber": source.get("chapterNumber"),
            "pdfPath": source.get("pdfPath"),
        }
    return datasets


def build_catalog(manifest_path: Path, active_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path, {"entries": []})
    active_payload = load_json(active_path, {"activeDatasets": []})
    active_by_path = {item["jsonPath"].replace("\\", "/"): item for item in active_payload.get("activeDatasets", [])}
    generated = generated_datasets()
    catalog: dict[str, dict[str, Any]] = {}

    for entry in manifest.get("entries", []):
        output_path = str(entry.get("outputPath", "")).replace("\\", "/")
        json_path = output_path if output_path.startswith("data/") else output_path
        row = {
            "id": entry.get("id"),
            "jsonPath": json_path,
            "hasJson": False,
            "status": "scanned",
            "activityCount": 0,
            "classLevel": entry.get("classLevel"),
            "stream": entry.get("stream"),
            "subject": entry.get("subject"),
            "book": entry.get("book"),
            "chapter": entry.get("chapter"),
            "chapterNumber": entry.get("chapterNumber"),
            "pdfPath": entry.get("pdfPath"),
            "relativePath": entry.get("relativePath"),
        }
        if json_path in generated:
            row.update(generated[json_path])
            row["status"] = "generated"
        if json_path in active_by_path:
            row["status"] = active_by_path[json_path].get("status", "active")
            row["approvedBy"] = active_by_path[json_path].get("approvedBy")
            row["notes"] = active_by_path[json_path].get("notes", "")
        catalog[json_path] = row

    for json_path, row in generated.items():
        if json_path not in catalog:
            row = dict(row)
            row["status"] = active_by_path.get(json_path, {}).get("status", "generated")
            if json_path in active_by_path:
                row["approvedBy"] = active_by_path[json_path].get("approvedBy")
                row["notes"] = active_by_path[json_path].get("notes", "")
            catalog[json_path] = row

    rows = sorted(catalog.values(), key=lambda item: (int(item.get("classLevel") or 99), str(item.get("subject")), str(item.get("book")), int(item.get("chapterNumber") or 999)))
    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1

    return {
        "version": 1,
        "generatedAt": int(time.time()),
        "manifestPath": rel(manifest_path) if manifest_path.exists() else str(manifest_path),
        "activePath": rel(active_path) if active_path.exists() else str(active_path),
        "totals": {
            "manifestEntries": len(manifest.get("entries", [])),
            "generatedDatasets": sum(1 for row in rows if row.get("hasJson")),
            "activeDatasets": status_counts.get("active", 0),
            "statusCounts": status_counts,
        },
        "datasets": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Learnify content catalog from manifest, generated JSON and active dataset list.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--active", type=Path, default=DEFAULT_ACTIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    catalog = build_catalog(args.manifest, args.active)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Manifest entries: {catalog['totals']['manifestEntries']}")
    print(f"Generated datasets: {catalog['totals']['generatedDatasets']}")
    print(f"Active datasets: {catalog['totals']['activeDatasets']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
