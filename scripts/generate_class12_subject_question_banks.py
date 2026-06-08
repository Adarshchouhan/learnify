from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Any

from generate_class12_commerce_practice import dataset, make_topic, slugify


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(r"C:\Users\acer\Downloads\Data Abstractor\Data Abstractor\data\learnify_cbse.sqlite")
SOURCE_ROOT = Path(r"C:\Users\acer\Downloads\Data Abstractor\Data Abstractor")


SUBJECT_SPECS: dict[str, dict[str, Any]] = {
    "English": {
        "dbSubjects": ["English Core", "Englishcore", "English Elective", "Englishelective"],
        "book": "English Board Practice Question Bank",
        "folder": "english-board-question-bank",
        "chapters": [
            ("Reading Comprehension", ["passage", "read the following", "answer the following questions"]),
            ("Creative Writing Skills", ["notice", "invitation", "letter", "article", "report", "application"]),
            ("Literature Extracts and Themes", ["poem", "extract", "prose", "flamingo", "vistas", "character"]),
            ("Grammar and Expression", ["sentence", "phrase", "analogy", "complete", "suitably"]),
        ],
    },
    "Business Studies": {
        "dbSubjects": ["Business Studies"],
        "book": "Business Studies Board Practice Question Bank",
        "folder": "business-studies-board-question-bank",
        "chapters": [
            ("Nature and Principles of Management", ["management", "principle", "science", "profession", "art"]),
            ("Planning Organising Staffing Directing Controlling", ["planning", "organising", "staffing", "directing", "controlling"]),
            ("Business Finance and Marketing", ["financial", "capital", "marketing", "consumer", "stock exchange", "sebi"]),
            ("Case Studies and Competency Questions", ["case", "identify", "assertion", "reason", "manager"]),
        ],
    },
    "Economics": {
        "dbSubjects": ["Economics"],
        "book": "Economics Board Practice Question Bank",
        "folder": "economics-board-question-bank",
        "chapters": [
            ("Macroeconomics and National Income", ["national income", "aggregate", "gva", "domestic", "income"]),
            ("Money Banking and Government Budget", ["central bank", "money", "budget", "securities", "deflationary"]),
            ("Balance of Payments and Exchange Rate", ["balance of payments", "exchange rate", "foreign", "bop"]),
            ("Indian Economic Development", ["development", "poverty", "human capital", "rural", "liberalisation"]),
        ],
    },
}


def clean_text(value: str, limit: int = 420) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    text = text.replace("\uf02d", "-").replace("\uf0a7", "-")
    return text[:limit].rstrip(" ,;:-") + ("." if text and text[-1] not in ".?!" else "")


def short_title(text: str, fallback: str) -> str:
    text = clean_text(text, 90)
    text = re.sub(r"^(read|attempt|choose|identify|state|explain|analyse)\b\s*", "", text, flags=re.I)
    return text.strip(" .:;")[:70] or fallback


def make_points(question: str, solution: str, answer_format: str, sequence_json: str, subject: str) -> list[str]:
    q = clean_text(question, 240)
    solution = clean_text(solution, 260)
    if not solution or solution.lower().startswith(f"model solution for {subject.lower()}"):
        solution = "The response should use the exact command word, relevant textbook concept and a concise board-style explanation."
    try:
        steps = json.loads(sequence_json or "[]")
    except json.JSONDecodeError:
        steps = []
    if not isinstance(steps, list) or not steps:
        steps = ["Identify the demand of the question", "Select relevant concept", "Write support", "Conclude"]
    step_text = ", ".join(str(step) for step in steps[:4])
    return [
        f"The question focus is: {q}",
        f"The accepted answer direction is: {solution}",
        f"A strong answer follows this format: {step_text}.",
        "The final response should be precise, sequenced and free from unsupported extra points.",
        "Marks are gained by matching the command word with evidence, concept or calculation as required.",
    ]


def make_distractors(subject: str) -> list[str]:
    return [
        f"A {subject} answer can ignore the command word if the topic name is mentioned.",
        "Only copying one keyword is enough for full marks.",
        "The response should add unrelated examples even if they are not supported.",
        "Order and evidence do not matter in a board-style answer.",
    ]


def fetch_rows(con: sqlite3.Connection, db_subjects: list[str], keywords: list[str], used: set[str], limit: int = 4) -> list[sqlite3.Row]:
    subject_marks = ",".join("?" for _ in db_subjects)
    params: list[Any] = [*db_subjects]
    keyword_clause = ""
    if keywords:
        keyword_clause = " AND (" + " OR ".join("LOWER(q.question_text) LIKE ?" for _ in keywords) + ")"
        params.extend([f"%{keyword.lower()}%" for keyword in keywords])
    rows = con.execute(
        f"""
        SELECT q.id, p.subject, p.title, p.academic_session, p.paper_kind,
               q.question_number, q.question_text, q.solution_text,
               q.suggested_answer_format, q.answer_sequence_json
        FROM papers p
        JOIN questions q ON q.paper_id = p.id
        WHERE p.class_level = '12'
          AND p.subject IN ({subject_marks})
          AND LENGTH(q.question_text) BETWEEN 80 AND 900
          AND q.question_text NOT LIKE '%TIME:%'
          AND q.question_text NOT LIKE '%M.M.%'
          {keyword_clause}
        ORDER BY
          CASE WHEN q.solution_text IS NOT NULL AND LENGTH(q.solution_text) > 8 THEN 0 ELSE 1 END,
          p.academic_session DESC,
          LENGTH(q.question_text)
        LIMIT {limit * 5}
        """,
        params,
    ).fetchall()
    picked: list[sqlite3.Row] = []
    for row in rows:
        if row["id"] in used:
            continue
        used.add(row["id"])
        picked.append(row)
        if len(picked) >= limit:
            break
    return picked


def fallback_rows(con: sqlite3.Connection, db_subjects: list[str], used: set[str], limit: int) -> list[sqlite3.Row]:
    return fetch_rows(con, db_subjects, [], used, limit)


def row_topic(row: sqlite3.Row, subject: str, chapter: str, index: int) -> dict[str, Any]:
    question = clean_text(row["question_text"], 360)
    answer_format = row["suggested_answer_format"] or "pointwise_answer"
    title = short_title(question, f"{chapter} practice {index}")
    points = make_points(question, row["solution_text"] or "", answer_format, row["answer_sequence_json"] or "", subject)
    return make_topic(
        title,
        f"Answer this Class 12 {subject} question: {question}",
        f"Build a complete board-style answer for the {chapter} question.",
        f"A student is attempting a {row['paper_kind']} from {row['academic_session'] or 'a board practice session'} and must write a marks-focused response.",
        points,
        make_distractors(subject),
        [
            chapter,
            "command word",
            "source question",
            answer_format.replace("_", " "),
            "board-style sequence",
            "final answer",
        ],
    )


def make_payload(subject: str, spec: dict[str, Any], chapter_number: int, chapter_name: str, topics: list[dict[str, Any]], relative: str) -> dict[str, Any]:
    meta = {
        "root": str(SOURCE_ROOT),
        "pdfPath": str(DB_PATH),
        "classLevel": 12,
        "stream": "Commerce",
        "subject": subject,
        "book": spec["book"],
        "chapter": chapter_name,
        "chapterNumber": chapter_number,
    }
    payload = dataset(meta, topics, ROOT / relative)
    payload["source"]["dataAbstractorDatabase"] = str(DB_PATH)
    payload["source"]["dataAbstractorSubjects"] = spec["dbSubjects"]
    payload["coverage"]["generationMode"] = f"class-12-{slugify(subject)}-data-abstractor-question-bank"
    payload["coverage"]["sourceQuestionCount"] = len(topics)
    return payload


def upsert_catalog(path: str, payload: dict[str, Any]) -> None:
    catalog_path = ROOT / "data/catalog/content-catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path.exists() else {"datasets": []}
    source = payload["source"]
    entry = {
        "id": path.removesuffix(".json"),
        "jsonPath": path,
        "hasJson": True,
        "activityCount": len(payload["activities"]),
        "classLevel": source["classLevel"],
        "stream": source["stream"],
        "subject": source["subject"],
        "book": source["book"],
        "chapter": source["chapter"],
        "chapterNumber": source["chapterNumber"],
        "pdfPath": source["pdfPath"],
        "status": "active",
        "approvedBy": "data-abstractor-question-bank",
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
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def upsert_active(path: str, subject: str) -> None:
    active_path = ROOT / "data/catalog/active-datasets.json"
    payload = json.loads(active_path.read_text(encoding="utf-8")) if active_path.exists() else {"activeDatasets": []}
    entry = {
        "id": path.removesuffix(".json"),
        "jsonPath": path,
        "status": "active",
        "approvedBy": "data-abstractor-question-bank",
        "notes": f"Class 12 {subject} board-style practice generated from local Data Abstractor database.",
    }
    active = payload.setdefault("activeDatasets", [])
    for index, existing in enumerate(active):
        if existing.get("jsonPath") == path:
            active[index] = entry
            break
    else:
        active.append(entry)
    active_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    written: list[str] = []
    for subject, spec in SUBJECT_SPECS.items():
        used: set[str] = set()
        for chapter_number, (chapter_name, keywords) in enumerate(spec["chapters"], start=1):
            rows = fetch_rows(con, spec["dbSubjects"], keywords, used, 4)
            if len(rows) < 4:
                rows.extend(fallback_rows(con, spec["dbSubjects"], used, 4 - len(rows)))
            topics = [row_topic(row, subject, chapter_name, index) for index, row in enumerate(rows, start=1)]
            relative = f"data/practice/class-12/{spec['folder']}/{chapter_number:02d}-{slugify(chapter_name)}.json"
            payload = make_payload(subject, spec, chapter_number, chapter_name, topics, relative)
            output = ROOT / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            upsert_catalog(relative, payload)
            upsert_active(relative, subject)
            written.append(relative)
            print(f"Wrote {relative} ({len(payload['activities'])} activities)")
    print(f"Wrote {len(written)} subject question-bank datasets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
