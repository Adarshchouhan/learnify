from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_CATALOG = Path("data/catalog/content-catalog.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Print Learnify content rollout status from the catalog.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--class-level", type=int, default=None)
    parser.add_argument("--subject", default=None)
    args = parser.parse_args()

    if not args.catalog.exists():
        print(f"Catalog not found: {args.catalog}")
        print("Run: python scripts/build_content_catalog.py")
        return 1

    payload = json.loads(args.catalog.read_text(encoding="utf-8"))
    rows = payload.get("datasets", [])
    if args.class_level:
        rows = [row for row in rows if row.get("classLevel") == args.class_level]
    if args.subject:
        rows = [row for row in rows if str(row.get("subject", "")).lower() == args.subject.lower()]

    status_counts = Counter(row.get("status", "unknown") for row in rows)
    by_class: dict[int, Counter[str]] = defaultdict(Counter)
    by_subject: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        by_class[int(row.get("classLevel") or 0)][row.get("status", "unknown")] += 1
        by_subject[str(row.get("subject") or "Unknown")][row.get("status", "unknown")] += 1

    print(f"Rows: {len(rows)}")
    print("Status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print("By class:")
    for class_level in sorted(key for key in by_class if key):
        summary = ", ".join(f"{status}={count}" for status, count in sorted(by_class[class_level].items()))
        print(f"  Class {class_level}: {summary}")
    print("Top subjects:")
    for subject, counts in sorted(by_subject.items())[:20]:
        summary = ", ".join(f"{status}={count}" for status, count in sorted(counts.items()))
        print(f"  {subject}: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
