from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PATHS = [
    "data/practice/class-12/accountancy-computerised-accounting-system/computerised-accounting-practice-3332e8d9.json",
    "data/practice/class-12/accountancy-financial-accounting-1/partnership-accounting-practice-1ddc2781.json",
    "data/practice/class-12/accountancy-financial-accounting-2/company-accounts-and-analysis-practice-76eb6c97.json",
    "data/practice/class-12/business-studies-part-1/management-functions-practice-141fa764.json",
    "data/practice/class-12/business-studies-part-2/finance-marketing-and-consumer-practice-05d9c4f0.json",
    "data/practice/class-12/economics-introductory-macroeconomics/macroeconomics-practice-08391c21.json",
    "data/practice/class-12/economics-introductory-microeconomics/microeconomics-practice-f6fb2797.json",
    "data/practice/class-12/english-flamingo-and-vistas/class-12-english-practice-f5cd2640.json",
]

PLACEHOLDERS = {
    "state the concept",
    "explain its importance",
    "add one example",
    "relevant definition",
    "clear reason",
    "exam keyword",
    "correct assertion",
    "correct reason",
    "reason explains assertion",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ids_from_key(key: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for name in ["orderedItemIds", "requiredConceptIds", "requiredItemIds", "acceptedItemIds", "answers"]:
        value = key.get(name)
        if isinstance(value, list):
            ids.extend(str(item) for item in value)
    if isinstance(key.get("pairs"), list):
        for pair in key["pairs"]:
            if isinstance(pair, list):
                ids.extend(str(item) for item in pair)
    for value in key.values():
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            ids.extend(value)
    return ids


def audit_dataset(path: Path) -> list[str]:
    data = load(path)
    errors: list[str] = []
    activities = data.get("activities", [])
    if len(activities) < 90:
        errors.append(f"{path.name}: expected at least 90 activities, found {len(activities)}")

    questions = Counter(str(activity.get("question", "")).strip().lower() for activity in activities)
    excessive_duplicates = [question for question, count in questions.items() if question and count > 3]
    if excessive_duplicates:
        errors.append(f"{path.name}: repeated question prompts too often: {excessive_duplicates[:3]}")

    table_activities = [activity for activity in activities if activity.get("type") == "data_chart_table"]
    real_tables = [activity for activity in table_activities if activity.get("tableData")]
    if len(real_tables) < 18:
        errors.append(f"{path.name}: expected at least 18 real table activities, found {len(real_tables)}")

    grouped_modes: dict[str, set[str]] = defaultdict(set)
    grouped_questions: dict[str, set[str]] = defaultdict(set)

    for activity in activities:
        label = activity.get("id", "unknown")
        if not activity.get("question") or not activity.get("modelAnswer"):
            errors.append(f"{path.name}: {label} missing question/modelAnswer")
        if any(text in str(activity.get("modelAnswer", "")).lower() for text in PLACEHOLDERS):
            errors.append(f"{path.name}: {label} contains placeholder model answer")

        item_ids = {item.get("id") for item in activity.get("correctItems", []) + activity.get("distractors", [])}
        missing = [item_id for item_id in ids_from_key(activity.get("answerKey", {})) if item_id not in item_ids]
        if missing:
            errors.append(f"{path.name}: {label} answerKey references missing ids {missing[:4]}")

        if activity.get("type") == "data_chart_table" and activity.get("tableData"):
            table = activity["tableData"]
            headers = table.get("headers", [])
            rows = table.get("rows", [])
            if len(headers) < 2 or len(rows) < 3:
                errors.append(f"{path.name}: {label} table too small")
            for row in rows:
                if len(row) != len(headers) or any(str(cell).strip() == "" for cell in row):
                    errors.append(f"{path.name}: {label} malformed table row")

        group_id = activity.get("questionGroupId")
        if activity.get("type") == "answer_builder" and group_id:
            grouped_modes[group_id].add(activity.get("difficulty", ""))
            grouped_questions[group_id].add(activity.get("question", ""))

    for group_id, modes in grouped_modes.items():
        if {"easy", "moderate", "difficult"} - modes:
            errors.append(f"{path.name}: {group_id} missing modes {sorted({'easy', 'moderate', 'difficult'} - modes)}")
        if len(grouped_questions[group_id]) < 3:
            errors.append(f"{path.name}: {group_id} easy/moderate/difficult questions are not distinct")

    return errors


def main() -> int:
    all_errors: list[str] = []
    for relative in ACTIVE_PATHS:
        all_errors.extend(audit_dataset(ROOT / relative))
    if all_errors:
        print("Class 12 Commerce audit failed")
        for error in all_errors:
            print(f"- {error}")
        return 1
    print("Class 12 Commerce audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
