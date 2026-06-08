from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ACCOUNTANCY_DIR = ROOT / "data/practice/class-12/accountancy-syllabus-question-bank"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def base_path_for(numerical_path: Path) -> Path:
    return ACCOUNTANCY_DIR / numerical_path.name.replace("-numerical-tables", "")


def normalize_activity(activity: dict[str, Any], base_source: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(activity)
    normalized["book"] = base_source["book"]
    normalized["chapter"] = base_source["chapter"]
    normalized["chapterNumber"] = base_source["chapterNumber"]
    normalized["sourceChapter"] = base_source["chapter"]
    normalized["sourcePdf"] = base_source["pdfPath"]
    normalized["sourceTextSummary"] = f"Class 12 Accountancy numerical table practice for {base_source['chapter']}."
    normalized["tableOnlyNumerical"] = True
    return normalized


def merge_dataset(numerical_path: Path) -> str:
    base_path = base_path_for(numerical_path)
    if not base_path.exists():
        raise FileNotFoundError(f"Missing base dataset for {numerical_path.name}: {base_path.name}")

    base = load(base_path)
    numerical = load(numerical_path)
    base_source = base["source"]

    numerical_ids = {activity["id"] for activity in numerical.get("activities", [])}
    existing = [activity for activity in base.get("activities", []) if activity.get("id") not in numerical_ids]
    merged = existing + [normalize_activity(activity, base_source) for activity in numerical.get("activities", [])]
    base["activities"] = merged

    coverage = base.setdefault("coverage", {})
    coverage["activityCount"] = len(merged)
    coverage["tablePracticeMode"] = "continuous-table-drag-drop"
    coverage["numericalTableQuestionCount"] = len(numerical.get("activities", []))
    coverage["numericalTablesMergedIntoDataChartTable"] = True

    chapter_questions = base.setdefault("chapterQuestions", [])
    existing_groups = {question.get("groupId") for question in chapter_questions}
    for question in numerical.get("chapterQuestions", []):
        if question.get("groupId") in existing_groups:
            continue
        chapter_questions.append(
            {
                **question,
                "number": len(chapter_questions) + 1,
                "questionIdentifier": {
                    **question.get("questionIdentifier", {}),
                    "id": "data_chart_table",
                    "primaryType": "data_chart_table",
                    "label": "Data / Chart / Table",
                },
            }
        )

    save(base_path, base)
    return str(base_path.relative_to(ROOT))


def remove_catalog_entries(numerical_paths: set[str]) -> None:
    catalog_path = ROOT / "data/catalog/content-catalog.json"
    if catalog_path.exists():
        catalog = load(catalog_path)
        catalog["datasets"] = [
            dataset
            for dataset in catalog.get("datasets", [])
            if str(dataset.get("jsonPath", "")).replace("\\", "/") not in numerical_paths
        ]
        save(catalog_path, catalog)

    active_path = ROOT / "data/catalog/active-datasets.json"
    if active_path.exists():
        active = load(active_path)
        active["activeDatasets"] = [
            dataset
            for dataset in active.get("activeDatasets", [])
            if str(dataset.get("jsonPath", "")).replace("\\", "/") not in numerical_paths
        ]
        save(active_path, active)


def main() -> int:
    numerical_files = sorted(ACCOUNTANCY_DIR.glob("*-numerical-tables.json"))
    if not numerical_files:
        print("No separate numerical-table datasets found.")
        return 0

    merged_paths = [merge_dataset(path) for path in numerical_files]
    numerical_rel_paths = {str(path.relative_to(ROOT)).replace("\\", "/") for path in numerical_files}
    remove_catalog_entries(numerical_rel_paths)

    for path in numerical_files:
        path.unlink()

    print(f"Merged numerical table questions into {len(merged_paths)} Accountancy chapter dataset(s).")
    print(f"Removed {len(numerical_files)} separate numerical-table dataset file(s) and catalog entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
