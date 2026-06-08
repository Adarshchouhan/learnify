from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_QUESTION_TYPES = {
    "explain",
    "compare_contrast",
    "cause_effect",
    "process_sequence",
    "pros_cons",
    "problem_solution",
    "fill_blanks",
    "true_false_not_given",
    "short_answer_key_points",
    "match_following",
    "data_chart_table",
    "paragraph_essay_structure",
    "definition_term",
    "timeline_chronological_order",
    "identify_main_idea",
    "evidence_support_statement",
    "sequencing_steps_process",
    "choose_correct_ending",
    "multiple_correct_answers",
    "formulate_question",
    "assertion_reason",
}

REQUIRED_ACTIVITY_FIELDS = {
    "id",
    "type",
    "difficulty",
    "classLevel",
    "subject",
    "book",
    "chapter",
    "chapterNumber",
    "marks",
    "question",
    "instructions",
    "structureHelp",
    "sourceTextSummary",
    "sourceChapter",
    "sourcePdf",
    "correctItems",
    "distractors",
    "answerSlots",
    "answerKey",
    "hints",
    "modelAnswer",
    "scoringRubric",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(path: Path) -> list[str]:
    data = load_json(path)
    errors: list[str] = []

    for field in ["version", "generatedBy", "source", "coverage", "activities"]:
        require(field in data, f"Missing root field: {field}", errors)

    activities = data.get("activities", [])
    coverage = data.get("coverage", {})
    is_table_only_pack = coverage.get("tablePracticeMode") == "continuous-table-drag-drop"
    require(isinstance(activities, list), "activities must be an array", errors)
    if is_table_only_pack:
        require(len(activities) >= 10, "table-only topic pack should include at least 10 table activities", errors)
    else:
        require(len(activities) >= 24, "pilot dataset should include 21 types plus 3 answer-builder modes", errors)

    seen_ids: set[str] = set()
    seen_types: set[str] = set()
    answer_builder_modes: set[str] = set()

    for index, activity in enumerate(activities):
        label = activity.get("id", f"activity[{index}]")
        missing = REQUIRED_ACTIVITY_FIELDS - set(activity)
        require(not missing, f"{label} missing fields: {sorted(missing)}", errors)

        activity_id = activity.get("id")
        require(activity_id not in seen_ids, f"Duplicate activity id: {activity_id}", errors)
        if activity_id:
            seen_ids.add(activity_id)

        activity_type = activity.get("type")
        if activity_type == "answer_builder":
            answer_builder_modes.add(activity.get("difficulty", ""))
        else:
            seen_types.add(activity_type)

        require(bool(activity.get("correctItems")), f"{label} must have correctItems", errors)
        require(bool(activity.get("answerSlots")), f"{label} must have answerSlots", errors)
        require(bool(activity.get("modelAnswer")), f"{label} must have modelAnswer", errors)
        require(activity.get("sourceChapter") == data.get("source", {}).get("chapter"), f"{label} sourceChapter mismatch", errors)
        require(activity.get("sourcePdf") == data.get("source", {}).get("pdfPath"), f"{label} sourcePdf mismatch", errors)

    if is_table_only_pack:
        require(seen_types == {"data_chart_table"}, f"Table-only topic pack should only contain data_chart_table activities, found {sorted(seen_types)}", errors)
    else:
        missing_types = EXPECTED_QUESTION_TYPES - seen_types
        require(not missing_types, f"Missing question types: {sorted(missing_types)}", errors)
        require(
            {"easy", "moderate", "difficult"}.issubset(answer_builder_modes),
            f"Missing answer-builder modes: {sorted({'easy', 'moderate', 'difficult'} - answer_builder_modes)}",
            errors,
        )

    require(coverage.get("activityCount") == len(activities), "coverage.activityCount must match activities length", errors)
    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "data/practice/class-7/science-curiosity/life-processes-in-animals.json"
    )
    errors = validate(path)
    if errors:
        print(f"Validation failed for {path}")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validation passed for {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
