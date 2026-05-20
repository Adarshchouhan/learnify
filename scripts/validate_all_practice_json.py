from __future__ import annotations

import sys
from pathlib import Path

from validate_practice_json import validate


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/practice")
    paths = sorted(root.rglob("*.json"))

    failed: list[tuple[Path, list[str]]] = []
    for path in paths:
        errors = validate(path)
        if errors:
            failed.append((path, errors))

    if failed:
        print(f"Validation failed: {len(failed)} of {len(paths)} dataset(s)")
        for path, errors in failed[:25]:
            print(f"\n{path}")
            for error in errors[:20]:
                print(f"- {error}")
            if len(errors) > 20:
                print(f"- ... {len(errors) - 20} more error(s)")
        if len(failed) > 25:
            print(f"\n... {len(failed) - 25} more failed dataset(s)")
        return 1

    print(f"Validation passed: {len(paths)} dataset(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
