from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRACTICE_ROOT = ROOT / "data" / "practice"
CATALOG_PATH = ROOT / "data" / "catalog" / "content-catalog.json"
ACTIVE_PATH = ROOT / "data" / "catalog" / "active-datasets.json"

CODE_RE = re.compile(r"\b[a-z]{3,6}\d{2,4}\b", re.IGNORECASE)
NOISE_RE = re.compile(
    r"(reprint|isbn|copyright|teacher|note to the teacher|draw learners|page|santoor\s*\|"
    r"|class\s+\d+|chapter\s+\d+|unit\s+\d+|picture reading|let us do|activity|exercise"
    r"|answer the following|fill in the blanks|true or false|match the following)",
    re.IGNORECASE,
)
ALPHABET_RUN_RE = re.compile(r"\bA\s+B\s+C\s+D\s+E\s+F\b", re.IGNORECASE)


QUESTION_BY_TYPE = {
    "explain": "What are the main ideas in {chapter}?",
    "compare_contrast": "How are two ideas in {chapter} similar or different?",
    "cause_effect": "What happens in {chapter}, and why does it happen?",
    "process_sequence": "Put the events or ideas from {chapter} in the correct order.",
    "pros_cons": "What are the helpful and difficult points in {chapter}?",
    "problem_solution": "What problem is shown in {chapter}, and how can it be solved?",
    "fill_blanks": "Complete the sentences using ideas from {chapter}.",
    "true_false_not_given": "Decide which statements match {chapter}.",
    "short_answer_key_points": "Write a short answer using key points from {chapter}.",
    "match_following": "Match the related ideas from {chapter}.",
    "data_chart_table": "Use the information from {chapter} to answer clearly.",
    "paragraph_essay_structure": "Build a clear paragraph about {chapter}.",
    "definition_term": "What important word or idea do we learn in {chapter}?",
    "timeline_chronological_order": "Arrange the events from {chapter} in order.",
    "identify_main_idea": "Choose the main idea of {chapter}.",
    "evidence_support_statement": "Choose the details that support an idea from {chapter}.",
    "sequencing_steps_process": "Place the steps from {chapter} in order.",
    "choose_correct_ending": "Choose the correct endings for sentences from {chapter}.",
    "multiple_correct_answers": "Choose all correct ideas from {chapter}.",
    "formulate_question": "Make a good question about {chapter}.",
    "assertion_reason": "Read the statement and reason about {chapter}.",
    "answer_builder": "Build a clear answer about {chapter}.",
}


def normalize_text(value: str) -> str:
    replacements = {
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\u00a0": " ",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "â”‚": "|",
        "â€†": " ",
        "â€¦": "...",
        "â€“": "-",
        "â€”": "-",
        "â€˜": "'",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_display(value: str) -> str:
    value = normalize_text(value)
    value = CODE_RE.sub("the lesson", value)
    value = re.sub(r"\bChapter\s+the lesson\b", "the lesson", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip(" -:;,.")
    return value


def is_code(value: str) -> bool:
    return bool(re.fullmatch(r"[a-z]{3,6}\d{2,4}", str(value or "").strip(), flags=re.IGNORECASE))


def candidate_title_score(line: str, book: str) -> int:
    line = normalize_text(line).strip(" -:;,.")
    if not (4 <= len(line) <= 70):
        return -100
    if CODE_RE.search(line) or NOISE_RE.search(line) or ALPHABET_RUN_RE.search(line):
        return -100
    words = line.split()
    if len(words) > 8:
        return -20
    lower = line.lower()
    book_words = {word for word in re.split(r"[^a-z]+", book.lower()) if len(word) > 3}
    score = 0
    if 2 <= len(words) <= 5:
        score += 20
    if all(word[:1].isupper() or word.lower() in {"and", "or", "the", "with", "of", "to", "in"} for word in words):
        score += 14
    if not re.search(r"[.!?]$", line):
        score += 8
    if any(word.lower() in {"fun", "friends", "world", "family", "food", "water", "plants", "animals", "numbers", "games"} for word in words):
        score += 8
    if any(word.lower().strip("-") in book_words for word in words):
        score -= 8
    if len(words) == 1:
        score -= 6
    return score


def infer_chapter_title(source: dict[str, Any]) -> str:
    current = clean_display(str(source.get("chapter") or ""))
    if current and not is_code(current) and "the lesson" not in current.lower():
        return current
    preview = str(source.get("extractionPreview") or "")
    lines = [normalize_text(line).strip(" -:;,.") for line in re.split(r"[\r\n]+", preview)]
    lines = [line for line in lines if line]
    book = str(source.get("book") or "")
    scored = sorted(((candidate_title_score(line, book), line) for line in lines), reverse=True)
    for score, line in scored:
        if score > 0:
            return line
    number = source.get("chapterNumber") or 1
    subject = source.get("subject") or "Subject"
    return f"{subject} Lesson {number}"


def clean_points(source: dict[str, Any], chapter: str, count: int = 12) -> list[str]:
    preview = normalize_text(str(source.get("extractionPreview") or ""))
    raw_parts = re.split(r"(?<=[.!?])\s+|[\r\n]+", preview)
    points: list[str] = []
    for part in raw_parts:
        text = normalize_text(part).strip(" -:;,.")
        if not (18 <= len(text) <= 150):
            continue
        if CODE_RE.search(text) or NOISE_RE.search(text) or ALPHABET_RUN_RE.search(text):
            continue
        if re.fullmatch(r"[\d\s.,:-]+", text):
            continue
        if len(text.split()) < 4:
            continue
        if text not in points:
            points.append(text + ("" if text.endswith((".", "?", "!")) else "."))
        if len(points) >= count:
            break
    fallbacks = [
        f"{chapter} has important ideas that students can explain in simple words.",
        f"The answer should use details from {chapter}.",
        f"A clear response should stay connected to {chapter}.",
        f"Students should arrange the points from {chapter} in a sensible order.",
        f"Examples from {chapter} help support the answer.",
    ]
    for fallback in fallbacks:
        if len(points) >= count:
            break
        points.append(fallback)
    return points


def rotate(items: list[str], index: int) -> str:
    return items[index % len(items)]


def update_items(activity: dict[str, Any], points: list[str], chapter: str) -> None:
    correct = activity.get("correctItems") or []
    for index, item in enumerate(correct):
        if isinstance(item, dict):
            item["text"] = rotate(points, index)
    wrong = activity.get("distractors") or []
    clean_wrong = [
        f"This option does not match {chapter}.",
        "This answer ignores the lesson details.",
        "This option is too incomplete for a good answer.",
        "This point is not supported by the lesson.",
    ]
    for index, item in enumerate(wrong):
        if isinstance(item, dict):
            item["text"] = clean_wrong[index % len(clean_wrong)]
            item["misconception"] = "This option is not supported by the lesson."


def repair_payload(payload: dict[str, Any]) -> bool:
    source = payload.get("source") or {}
    chapter = infer_chapter_title(source)
    old_chapter = str(source.get("chapter") or "")
    needs_repair = is_code(old_chapter) or any(
        CODE_RE.search(str(activity.get("question") or ""))
        or "Only one random word" in json.dumps(activity, ensure_ascii=False)
        or "Note to the teacher" in json.dumps(activity, ensure_ascii=False)
        or ALPHABET_RUN_RE.search(json.dumps(activity, ensure_ascii=False))
        for activity in payload.get("activities", [])
    )
    if not needs_repair:
        return False

    source["chapter"] = chapter
    source["sourceTextSummary"] = f"Practice questions generated from {source.get('book', 'the book')}, lesson: {chapter}."
    points = clean_points(source, chapter)

    for question_index, chapter_question in enumerate(payload.get("chapterQuestions", []), start=1):
        slug = str(chapter_question.get("questionIdentifier", {}).get("primaryType") or chapter_question.get("slug") or "answer_builder")
        template = QUESTION_BY_TYPE.get(slug, "Answer clearly using ideas from {chapter}.")
        chapter_question["question"] = template.format(chapter=chapter)
        chapter_question["groupId"] = f"chapter-q{question_index:02d}-{slug}"

    for activity in payload.get("activities", []):
        activity_type = str(activity.get("type") or "answer_builder")
        template = QUESTION_BY_TYPE.get(activity_type, "Answer clearly using ideas from {chapter}.")
        activity["chapter"] = chapter
        activity["sourceChapter"] = chapter
        activity["sourceTextSummary"] = source["sourceTextSummary"]
        activity["question"] = template.format(chapter=chapter)
        activity["instructions"] = "Use the clear lesson points to complete this activity."
        update_items(activity, points, chapter)
        if activity.get("modelAnswer"):
            activity["modelAnswer"] = " ".join(points[: min(4, len(points))])
        if activity.get("hints"):
            activity["hints"] = [f"Look for details from {chapter}.", "Remove options that do not match the lesson."]
    return True


def update_catalog_entries(repaired_paths: set[str]) -> None:
    if not CATALOG_PATH.exists():
        return
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    for entry in catalog.get("datasets", []):
        path = str(entry.get("jsonPath") or "").replace("\\", "/")
        if path not in repaired_paths:
            continue
        payload = json.loads((ROOT / path).read_text(encoding="utf-8"))
        source = payload.get("source", {})
        entry["chapter"] = source.get("chapter")
        entry["notes"] = "Question text cleaned for readable student practice."
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    repaired: set[str] = set()
    for path in sorted(PRACTICE_ROOT.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if repair_payload(payload):
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            repaired.add(str(path.relative_to(ROOT)).replace("\\", "/"))
    update_catalog_entries(repaired)
    print(f"Repaired {len(repaired)} generated dataset(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
