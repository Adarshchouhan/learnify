from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from generate_class12_commerce_practice import dataset, make_topic, slugify  # noqa: E402


DEFAULT_DB_PATH = Path(r"C:\Users\acer\Downloads\Data Abstractor\Data Abstractor\data\learnify_cbse.sqlite")
SOURCE_ROOT = Path(r"C:\Users\acer\Downloads\Data Abstractor\Data Abstractor")
CATALOG_PATH = ROOT / "data" / "catalog" / "content-catalog.json"
ACTIVE_PATH = ROOT / "data" / "catalog" / "active-datasets.json"


SUBJECT_ALIASES = {
    "English Core": "English",
    "English Elective": "English",
    "English Language and Literature": "English",
    "English Communicative": "English",
    "Englishcore": "English",
    "Englishelective": "English",
    "Englishcomm": "English",
    "Englishl": "English",
    "Hindi Core": "Hindi",
    "Hindi Elective": "Hindi",
    "Hindi A": "Hindi",
    "Hindi B": "Hindi",
    "Hindicore": "Hindi",
    "Hindielective": "Hindi",
    "Hindicoursea": "Hindi",
    "Hindicourseb": "Hindi",
    "Mathematics Basic": "Mathematics",
    "Mathematics Standard": "Mathematics",
    "Maths": "Mathematics",
    "Mathsbasic": "Mathematics",
    "Mathsstandard": "Mathematics",
    "Applied Maths": "Applied Mathematics",
    "Applied Mathsvic": "Applied Mathematics",
    "Computerapplication": "Computer Application",
    "Socialscience": "Social Science",
    "Polsci": "Political Science",
    "Polscihi": "Political Science",
    "Ncc": "NCC",
    "Homescience": "Home Science",
}


CORE_SUBJECTS_BY_CLASS = {
    6: {"English", "Hindi", "Mathematics", "Sanskrit", "Science", "Social Science"},
    7: {"English", "Hindi", "Mathematics", "Sanskrit", "Science", "Social Science"},
    8: {"English", "Hindi", "Mathematics", "Sanskrit", "Science", "Social Science"},
    9: {"Computer Application", "English", "Hindi", "Mathematics", "Sanskrit", "Science", "Social Science"},
    10: {"Computer Application", "English", "Hindi", "Mathematics", "Science", "Social Science"},
    11: {
        "Accountancy",
        "Biology",
        "Business Studies",
        "Chemistry",
        "Computer Science",
        "Economics",
        "English",
        "Geography",
        "History",
        "Mathematics",
        "Physical Education",
        "Physics",
        "Political Science",
    },
    12: {
        "Accountancy",
        "Biology",
        "Business Studies",
        "Chemistry",
        "Computer Science",
        "Economics",
        "English",
        "Geography",
        "History",
        "Mathematics",
        "Physical Education",
        "Physics",
        "Political Science",
    },
}


BAD_QUESTION_PATTERNS = [
    r"\bthis question paper contains\b",
    r"\ball questions are compulsory\b",
    r"\bpart\s*-\s*[ab]\b.*\bcompulsory\b",
    r"\bthere is no overall choice\b",
    r"\binternal choice has been provided\b",
    r"\bquestion nos?\.?\s*\d+",
    r"\bquestions?\s+from\s+\d+",
    r"\bquestions?\s+nos?\.?\s+from\b",
    r"\bmaximum marks\b",
    r"\btime allowed\b",
    r"\bgeneral instructions\b",
    r"\bexplain the significance of\b.*\bwith a practical example\b",
    r"\bhow does\b.*\baffect real-life systems studied in\b",
    r"\bdifferentiate between two important aspects related to\b",
    r"\bidentify and correct three common grammar errors\b",
    r"\btopic:\s*[a-z ]+\.\s*",
    r"\brelated to\b.*\bin\s+[a-z ]+\b",
    r"\bstay updated on exams\b",
    r"\bnew study materials\b",
    r"\bhindi antra\b",
    r"\bto bank a/c\b",
    r"\bby balance b/d\b",
]


def canonical_subject(subject: str) -> str:
    cleaned = re.sub(r"\s+", " ", subject or "").strip()
    return SUBJECT_ALIASES.get(cleaned, cleaned)


def clean_text(value: str | None, limit: int = 420) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    text = text.replace("\uf02d", "-").replace("\uf0a7", "-")
    text = text.strip(" \t\r\n")
    if len(text) > limit:
        text = text[:limit].rstrip(" ,;:-") + "..."
    if text and text[-1] not in ".?!":
        text += "."
    return text


def is_usable_question_row(row: sqlite3.Row, class_level: int, subject: str) -> bool:
    question = clean_text(row["question_text"], 1200).lower()
    solution = clean_text(row["solution_text"], 1200).lower()
    if len(question) < 35:
        return False
    if not solution or solution.startswith("model solution for"):
        return False
    subject_names = {
        "accountancy",
        "biology",
        "business studies",
        "chemistry",
        "economics",
        "english",
        "geography",
        "history",
        "mathematics",
        "physics",
        "political science",
    }
    if solution.strip(" .:-") in subject_names:
        return False
    if re.fullmatch(r"[a-z ]{3,30}", solution.strip(" .:-")):
        return False
    if "can be explained as a core idea in" in solution:
        return False
    combined = f"{question} {solution}"
    if any(re.search(pattern, combined, re.IGNORECASE) for pattern in BAD_QUESTION_PATTERNS):
        return False
    if class_level >= 11 and "class 12" in solution and class_level == 11:
        return False
    normalized_subject = subject.lower()
    mismatch_terms = {
        "accountancy": ["cold war", "human geography", "plant physiology", "chemical bonding", "chemistry", "genetics", "ecology"],
        "business studies": ["cold war", "human geography", "plant physiology", "chemical bonding", "genetics", "ecology"],
        "physics": ["human geography", "cold war", "genetics", "ecology", "photosynthesis"],
        "chemistry": ["human geography", "cold war", "genetics", "ecology", "photosynthesis"],
        "biology": ["cold war", "human geography"],
        "mathematics": ["ecology", "grammar errors"],
        "english": ["vectors", "ecology"],
    }
    for key, terms in mismatch_terms.items():
        if key in normalized_subject and any(term in combined for term in terms):
            return False
    other_subject_markers = [
        "english vistas",
        "english flamingo",
        "human geography",
        "cold war",
        "ecology in physics",
        "ecology in chemistry",
        "ecology in biology",
    ]
    if not any(key in normalized_subject for key in ("english", "geography", "history", "biology")):
        if any(marker in combined for marker in other_subject_markers):
            return False
    return True


def make_points(row: sqlite3.Row, class_level: int, subject: str) -> list[str]:
    question = clean_text(row["question_text"], 260)
    solution = clean_text(row["solution_text"], 300)
    if not solution or solution.lower().startswith("model solution"):
        solution = (
            "The answer should directly address the command word, use the relevant concept, "
            "and keep the explanation clear and sequenced."
        )
    try:
        steps = json.loads(row["answer_sequence_json"] or "[]")
    except json.JSONDecodeError:
        steps = []
    if not isinstance(steps, list) or not steps:
        steps = ["Understand the question", "Select the right concept", "Support the answer", "Conclude"]
    step_text = ", ".join(str(step) for step in steps[:4])
    return [
        f"The Class {class_level} {subject} question asks: {question}",
        f"The accepted answer direction is: {solution}",
        f"A strong response follows this sequence: {step_text}.",
        "The answer should stay within the topic and avoid unsupported extra points.",
        "Marks are earned by matching the command word with the correct fact, reason, evidence, or working.",
    ]


def make_distractors(class_level: int, subject: str) -> list[str]:
    return [
        f"A Class {class_level} {subject} answer can ignore the command word if a keyword is present.",
        "One copied word is enough for full marks.",
        "Adding unrelated examples is better than staying focused.",
        "Order, evidence, and calculation steps do not affect the answer.",
    ]


def row_to_topic(row: sqlite3.Row, class_level: int, subject: str, index: int) -> dict[str, Any]:
    question = clean_text(row["question_text"], 360)
    answer_format = str(row["suggested_answer_format"] or "pointwise_answer").replace("_", " ")
    title = clean_text(question, 80).strip(".?!") or f"{subject} question {index}"
    return make_topic(
        title,
        f"Answer this Class {class_level} {subject} question: {question}",
        f"Build a complete answer using the {answer_format} format.",
        f"A Class {class_level} student is attempting a {row['paper_kind']} from {row['academic_session'] or 'a practice session'}.",
        make_points(row, class_level, subject),
        make_distractors(class_level, subject),
        [subject, f"Class {class_level}", "command word", answer_format, "model answer", "final answer"],
    )


def fetch_question_rows(con: sqlite3.Connection, class_level: int, raw_subjects: list[str], limit: int) -> list[sqlite3.Row]:
    placeholders = ",".join("?" for _ in raw_subjects)
    sql_limit = "" if limit <= 0 else "LIMIT ?"
    params: list[Any] = [str(class_level), *raw_subjects]
    if limit > 0:
        params.append(limit * 30)
    rows = con.execute(
        f"""
        SELECT q.id, p.class_level, p.subject, p.title, p.academic_session, p.paper_kind,
               q.question_number, q.question_text, q.solution_text,
               q.suggested_answer_format, q.answer_sequence_json
        FROM papers p
        JOIN questions q ON q.paper_id = p.id
        WHERE p.class_level = ?
          AND p.subject IN ({placeholders})
          AND LENGTH(q.question_text) BETWEEN 20 AND 1200
          AND q.question_text NOT LIKE '%TIME:%'
          AND q.question_text NOT LIKE '%M.M.%'
          AND q.question_text NOT LIKE '%General Instructions%'
          AND q.question_text NOT LIKE '%Maximum Marks%'
        ORDER BY
          CASE WHEN q.solution_text IS NOT NULL AND LENGTH(q.solution_text) > 8 THEN 0 ELSE 1 END,
          p.academic_session DESC,
          LENGTH(q.question_text)
        {sql_limit}
        """,
        params,
    ).fetchall()
    seen: set[str] = set()
    picked: list[sqlite3.Row] = []
    for row in rows:
        if not is_usable_question_row(row, class_level, canonical_subject(row["subject"])):
            continue
        normalized = clean_text(row["question_text"], 260).lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        picked.append(row)
        if limit > 0 and len(picked) >= limit:
            break
    return picked


def make_payload(class_level: int, subject: str, raw_subjects: list[str], rows: list[sqlite3.Row], relative: str) -> dict[str, Any]:
    meta = {
        "root": str(SOURCE_ROOT),
        "pdfPath": str(DEFAULT_DB_PATH),
        "classLevel": class_level,
        "stream": None,
        "subject": subject,
        "book": f"{subject} Data Abstractor Question Bank",
        "chapter": "Solved Question Practice",
        "chapterNumber": 900,
    }
    topics = [row_to_topic(row, class_level, subject, index) for index, row in enumerate(rows, start=1)]
    payload = dataset(meta, topics, ROOT / relative)
    payload["source"]["sourceTextSummary"] = (
        f"Class {class_level} {subject} solved-question practice generated from the local Data Abstractor database."
    )
    payload["source"]["dataAbstractorDatabase"] = str(DEFAULT_DB_PATH)
    payload["source"]["dataAbstractorSubjects"] = raw_subjects
    payload["coverage"]["generationMode"] = "all-class-data-abstractor-question-bank"
    payload["coverage"]["sourceQuestionCount"] = len(rows)
    payload["coverage"]["label"] = f"Class {class_level} {subject} Answer Builder"
    replace_class12_text(payload, class_level, subject)
    return payload


def replace_class12_text(value: Any, class_level: int, subject: str) -> None:
    replacement = f"Class {class_level} {subject}"
    if isinstance(value, dict):
        for key, item in list(value.items()):
            if isinstance(item, str):
                value[key] = item.replace("Class 12 Commerce", replacement).replace("Class 12", f"Class {class_level}")
            else:
                replace_class12_text(item, class_level, subject)
    elif isinstance(value, list):
        for item in value:
            replace_class12_text(item, class_level, subject)


def load_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def upsert_catalog(path: str, payload: dict[str, Any]) -> None:
    catalog = load_json(CATALOG_PATH, {"datasets": []})
    source = payload["source"]
    entry = {
        "id": path.removesuffix(".json"),
        "jsonPath": path,
        "hasJson": True,
        "activityCount": len(payload["activities"]),
        "classLevel": source["classLevel"],
        "stream": source.get("stream"),
        "subject": source["subject"],
        "book": source["book"],
        "chapter": source["chapter"],
        "chapterNumber": source["chapterNumber"],
        "pdfPath": source["pdfPath"],
        "status": "active",
        "approvedBy": "data-abstractor-all-class-question-bank",
        "notes": "Generated from local Data Abstractor solved-question database.",
    }
    datasets = catalog.setdefault("datasets", [])
    for index, existing in enumerate(datasets):
        if existing.get("jsonPath") == path:
            datasets[index] = {**existing, **entry}
            break
    else:
        datasets.append(entry)
    catalog["generatedAt"] = int(time.time())
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def upsert_active(path: str, class_level: int, subject: str) -> None:
    payload = load_json(ACTIVE_PATH, {"version": 1, "activeDatasets": []})
    entry = {
        "id": path.removesuffix(".json"),
        "jsonPath": path,
        "status": "active",
        "approvedBy": "data-abstractor-all-class-question-bank",
        "notes": f"Class {class_level} {subject} question-bank practice generated from local Data Abstractor database.",
    }
    active = payload.setdefault("activeDatasets", [])
    for index, existing in enumerate(active):
        if existing.get("jsonPath") == path:
            active[index] = entry
            break
    else:
        active.append(entry)
    ACTIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def discover_subject_groups(con: sqlite3.Connection, core_only: bool) -> dict[int, dict[str, list[str]]]:
    groups: dict[int, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    rows = con.execute(
        """
        SELECT class_level, subject, COUNT(*) AS papers, SUM(question_count) AS question_count
        FROM papers
        GROUP BY class_level, subject
        HAVING question_count > 0
        ORDER BY CAST(class_level AS INTEGER), subject
        """
    ).fetchall()
    for row in rows:
        try:
            class_level = int(row["class_level"])
        except (TypeError, ValueError):
            continue
        subject = canonical_subject(row["subject"])
        if core_only and subject not in CORE_SUBJECTS_BY_CLASS.get(class_level, set()):
            continue
        groups[class_level][subject].append(row["subject"])
    return groups


def generate(args: argparse.Namespace) -> list[str]:
    db_path = Path(args.db_path)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    groups = discover_subject_groups(con, args.core_only)
    written: list[str] = []
    for class_level in sorted(groups):
        if args.class_level and class_level != args.class_level:
            continue
        for subject in sorted(groups[class_level]):
            raw_subjects = sorted(set(groups[class_level][subject]))
            rows = fetch_question_rows(con, class_level, raw_subjects, args.questions_per_subject)
            if not rows:
                continue
            relative = (
                f"data/practice/class-{class_level}/"
                f"{slugify(subject)}-data-abstractor-question-bank/"
                "solved-question-practice.json"
            )
            payload = make_payload(class_level, subject, raw_subjects, rows, relative)
            output = ROOT / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            upsert_catalog(relative, payload)
            upsert_active(relative, class_level, subject)
            written.append(relative)
            print(f"Wrote {relative} ({len(rows)} source questions, {len(payload['activities'])} activities)")
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Learnify question banks from the Data Abstractor SQLite database.")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="Path to learnify_cbse.sqlite.")
    parser.add_argument(
        "--questions-per-subject",
        type=int,
        default=100,
        help="Solved questions to convert per class/subject. Use 0 to convert every usable row.",
    )
    parser.add_argument("--class-level", type=int, default=0, help="Optional single class to generate.")
    parser.add_argument("--core-only", action="store_true", help="Generate only main/core school subjects.")
    return parser.parse_args()


def main() -> int:
    written = generate(parse_args())
    print(f"Wrote {len(written)} all-class Data Abstractor dataset(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
