from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PATH = ROOT / "data" / "catalog" / "active-datasets.json"


def normalize(path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            path = str(candidate.resolve().relative_to(ROOT))
        except ValueError:
            path = str(candidate)
    return path.replace("\\", "/").removesuffix(".json") + ".json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Mark a generated dataset active for student-facing Learnify practice.")
    parser.add_argument("json_path", help="Path under data/practice, for example data/practice/class-7/.../chapter.json")
    parser.add_argument("--approved-by", default="teacher-review")
    parser.add_argument("--notes", default="Approved for student practice.")
    args = parser.parse_args()

    json_path = normalize(args.json_path)
    candidate = (ROOT / json_path).resolve()
    if not candidate.exists() or ROOT not in candidate.parents:
        print(f"Dataset not found inside project: {json_path}")
        return 1

    payload = {"version": 1, "activeDatasets": []}
    if ACTIVE_PATH.exists():
        payload = json.loads(ACTIVE_PATH.read_text(encoding="utf-8"))
    active = [item for item in payload.get("activeDatasets", []) if normalize(item.get("jsonPath", "")) != json_path]
    active.append(
        {
            "id": json_path.removesuffix(".json"),
            "jsonPath": json_path,
            "status": "active",
            "approvedBy": args.approved_by,
            "notes": args.notes,
        }
    )
    payload["activeDatasets"] = sorted(active, key=lambda item: item["jsonPath"])
    ACTIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Activated {json_path}")
    print("Run: python scripts/build_content_catalog.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
