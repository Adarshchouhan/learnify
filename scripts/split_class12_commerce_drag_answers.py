from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = 1

COMMERCE_DIR_NAMES = {
    "accountancy-computerised-accounting-system",
    "accountancy-financial-accounting-1",
    "accountancy-financial-accounting-2",
    "accountancy-syllabus-question-bank",
    "business-studies-part-1",
    "business-studies-part-2",
    "commerce",
    "economics",
    "economics-introductory-macroeconomics",
    "economics-introductory-microeconomics",
}

SKIP_TYPES = {
    "assertion_reason",
    "cause_effect",
    "match_following",
}


def words(text: str) -> list[str]:
    return re.findall(r"\S+", re.sub(r"\s+", " ", text).strip())


def split_text(text: str) -> list[str]:
    parts = words(text)
    if len(parts) <= 7:
        return [" ".join(parts)]
    chunk_size = 4 if len(parts) <= 14 else 5
    chunks: list[str] = []
    index = 0
    while index < len(parts):
        remaining = len(parts) - index
        if remaining <= 2 and chunks:
            chunks[-1] = f"{chunks[-1]} {' '.join(parts[index:])}"
            break
        take = min(chunk_size, remaining)
        chunks.append(" ".join(parts[index : index + take]))
        index += take
    return chunks


def replace_ids(ids: list[str], replacements: dict[str, list[str]]) -> list[str]:
    output: list[str] = []
    for item_id in ids:
        output.extend(replacements.get(item_id, [item_id]))
    return output


def split_items(items: list[dict[str, Any]], ordered_ids: list[str]) -> tuple[list[dict[str, Any]], dict[str, list[str]], bool]:
    ordered_set = set(ordered_ids)
    new_items: list[dict[str, Any]] = []
    replacements: dict[str, list[str]] = {}
    changed = False

    for item in items:
        item_id = str(item.get("id", ""))
        if item_id not in ordered_set:
            new_items.append(item)
            continue

        pieces = split_text(str(item.get("text", "")))
        if len(pieces) == 1:
            new_items.append(item)
            replacements[item_id] = [item_id]
            continue

        changed = True
        replacements[item_id] = []
        for part_index, piece in enumerate(pieces, start=1):
            new_id = f"{item_id}-part-{part_index}"
            replacements[item_id].append(new_id)
            new_item = {**item, "id": new_id, "text": piece}
            if "order" in new_item:
                new_item["order"] = len(new_items) + 1
            new_items.append(new_item)

    return new_items, replacements, changed


def activity_expected_ids(activity: dict[str, Any]) -> list[str]:
    key = activity.get("answerKey") or {}
    for field in ("orderedItemIds", "requiredConceptIds", "requiredItemIds", "acceptedItemIds", "answers"):
        value = key.get(field)
        if isinstance(value, list):
            return [str(item_id) for item_id in value]
    return [str(item.get("id")) for item in activity.get("correctItems", []) if item.get("id")]


def update_answer_key(activity: dict[str, Any], replacements: dict[str, list[str]]) -> None:
    key = activity.get("answerKey") or {}
    for field in ("orderedItemIds", "requiredConceptIds", "requiredItemIds", "acceptedItemIds", "answers"):
        if isinstance(key.get(field), list):
            key[field] = replace_ids([str(item_id) for item_id in key[field]], replacements)
    activity["answerKey"] = key
    if isinstance(activity.get("correctSequence"), list):
        activity["correctSequence"] = replace_ids([str(item_id) for item_id in activity["correctSequence"]], replacements)


def update_slots(activity: dict[str, Any]) -> None:
    key = activity.get("answerKey") or {}
    ordered = key.get("orderedItemIds")
    if not isinstance(ordered, list):
        return
    if len(activity.get("answerSlots", [])) == 1 and activity.get("type") in {"explain", "definition_term", "evidence_support_statement"}:
        return
    labels = activity.get("structureHelp") or []
    activity["answerSlots"] = [
        {"id": f"slot-{index}", "label": labels[(index - 1) % len(labels)] if labels else f"Part {index}"}
        for index, _item_id in enumerate(ordered, start=1)
    ]


def split_activity(activity: dict[str, Any]) -> bool:
    if activity.get("answerPartsSplitVersion") == VERSION:
        return False
    if activity.get("type") in SKIP_TYPES:
        return False
    if not activity.get("correctItems") or not activity.get("answerSlots"):
        return False
    if activity.get("tableData", {}).get("dropMode") == "table-cells":
        return False
    if activity.get("answerKey", {}).get("pairs"):
        return False

    expected_ids = activity_expected_ids(activity)
    if not expected_ids:
        return False
    new_items, replacements, changed = split_items(activity["correctItems"], expected_ids)
    if not changed:
        activity["answerPartsSplitVersion"] = VERSION
        return False

    activity["correctItems"] = new_items
    update_answer_key(activity, replacements)
    update_slots(activity)
    activity["instructions"] = (
        "Drag or click the small answer parts in order. The selected parts join to build the full answer."
    )
    activity["answerPartsSplitVersion"] = VERSION
    return True


def is_commerce_payload(path: Path, payload: dict[str, Any]) -> bool:
    if path.parent.name in COMMERCE_DIR_NAMES:
        return True
    source = payload.get("source") or {}
    return source.get("classLevel") == 12 and source.get("stream") == "Commerce"


def main() -> int:
    changed_files = 0
    changed_activities = 0
    for path in sorted((ROOT / "data/practice/class-12").glob("*/*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not is_commerce_payload(path, payload):
            continue
        file_changes = 0
        for activity in payload.get("activities", []):
            if split_activity(activity):
                file_changes += 1
        if not file_changes:
            continue
        coverage = payload.setdefault("coverage", {})
        coverage["answerPartsSplitVersion"] = VERSION
        coverage["answerPartStyle"] = "small ordered cards joined into full answers"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        changed_files += 1
        changed_activities += file_changes
        print(f"Updated {path.relative_to(ROOT)} ({file_changes} activities)")
    print(f"Updated {changed_files} files and {changed_activities} activities.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
