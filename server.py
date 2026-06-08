from __future__ import annotations

import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import subprocess
import sys
import time
from copy import deepcopy
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
IS_SERVERLESS = bool(
    os.environ.get("VERCEL")
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    or str(ROOT).replace("\\", "/").startswith("/var/task")
)


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file(ROOT / ".env")
if not IS_SERVERLESS:
    load_env_file(ROOT / ".env.example")

DATABASE_URL = os.environ.get("LEARNIFY_DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:////tmp/learnify.sqlite3" if IS_SERVERLESS else "sqlite:///data/learnify.sqlite3"
if DATABASE_URL.startswith("sqlite:///"):
    configured_db = Path(DATABASE_URL.removeprefix("sqlite:///"))
    DB_PATH = configured_db if configured_db.is_absolute() else ROOT / configured_db
else:
    DB_PATH = DATA_DIR / "learnify.sqlite3"
PRACTICE_JSON = DATA_DIR / "practice" / "class-7" / "science-curiosity" / "life-processes-in-animals.json"
MANIFEST_JSON = DATA_DIR / "manifest" / "class-6-12-pdf-manifest.json"
CATALOG_JSON = DATA_DIR / "catalog" / "content-catalog.json"
ACTIVE_DATASETS_JSON = DATA_DIR / "catalog" / "active-datasets.json"
REMOTE_DATA_BASE = os.environ.get(
    "LEARNIFY_REMOTE_DATA_BASE",
    "https://raw.githubusercontent.com/Adarshchouhan/learnify/main/",
).rstrip("/") + "/"
MIN_CLASS_LEVEL = 1
MAX_CLASS_LEVEL = 12
HOST = os.environ.get("LEARNIFY_HOST", "127.0.0.1")
PORT = int(os.environ.get("LEARNIFY_PORT", "5173"))
SESSION_TTL_SECONDS = int(os.environ.get("LEARNIFY_SESSION_TTL_SECONDS", str(60 * 60 * 24 * 7)))
MAX_BODY_BYTES = 128 * 1024
IMAGE_GENERATOR_SCRIPT = ROOT / "scripts" / "generate_sdxl_lightning.py"
IMAGE_OUTPUT_DIR = ROOT / os.environ.get("LEARNIFY_IMAGE_OUTPUT_DIR", "assets/generated/sdxl-lightning")
IMAGE_PYTHON = os.environ.get("LEARNIFY_IMAGE_PYTHON", sys.executable)
IMAGE_GENERATION_TIMEOUT_SECONDS = int(os.environ.get("LEARNIFY_IMAGE_TIMEOUT_SECONDS", "900"))
STUDENT_CATALOG_STATUSES = {
    status.strip()
    for status in os.environ.get("LEARNIFY_STUDENT_CATALOG_STATUSES", "active").split(",")
    if status.strip()
}
MIN_ANSWER_BUILDER_GROUPS = int(os.environ.get("LEARNIFY_MIN_ANSWER_BUILDER_GROUPS", "24"))
MAX_SYNTHETIC_ANSWER_GROUPS = int(os.environ.get("LEARNIFY_MAX_SYNTHETIC_ANSWER_GROUPS", "24"))
MIN_STANDARD_QUESTIONS_PER_TYPE = int(os.environ.get("LEARNIFY_MIN_STANDARD_QUESTIONS_PER_TYPE", "12"))
MAX_SYNTHETIC_STANDARD_PER_TYPE = int(os.environ.get("LEARNIFY_MAX_SYNTHETIC_STANDARD_PER_TYPE", "12"))
STANDARD_TYPE_TASKS = {
    "assertion_reason": "judge the assertion and reason, then explain the relationship",
    "cause_effect": "connect the cause with its effect and justify the link",
    "choose_correct_ending": "complete the answer with the most accurate ending",
    "compare_contrast": "compare the two ideas with clear similarities and differences",
    "data_chart_table": "interpret the given information and draw a reasoned conclusion",
    "definition_term": "define the key term and explain its important features",
    "evidence_support_statement": "select evidence and explain how it supports the statement",
    "explain": "write a detailed board-style explanation",
    "fill_blanks": "complete the answer using accurate subject vocabulary",
    "formulate_question": "frame a focused question and answer it with evidence",
    "identify_main_idea": "identify the main idea and support it with details",
    "match_following": "match related ideas and explain why each pair belongs together",
    "multiple_correct_answers": "choose all valid points and justify each selection",
    "paragraph_essay_structure": "organise the answer into introduction, body and conclusion",
    "problem_solution": "state the problem, explain the solution and support it",
    "process_sequence": "arrange the process in logical order and explain each step",
    "pros_cons": "explain advantages, limitations and a balanced conclusion",
    "sequencing_steps_process": "place the steps in order and explain the sequence",
    "short_answer_key_points": "write concise key points with brief explanation",
    "timeline_chronological_order": "arrange events chronologically and explain their importance",
    "true_false_not_given": "decide whether the statement is supported and give reasons",
}
SENIOR_SUBJECT_FOCUS = {
    "accountancy": [
        "journal entries, ledgers and financial statement treatment",
        "partnership adjustment, goodwill treatment and capital account logic",
        "share capital, debenture or company account classification",
        "ratio analysis, cash flow interpretation and reporting conclusion",
    ],
    "business studies": [
        "management principle, function and case-study application",
        "planning, organising, staffing, directing or controlling decision",
        "marketing, finance or consumer protection case analysis",
        "entrepreneurial decision-making with reasoned justification",
    ],
    "economics": [
        "demand, supply and market equilibrium reasoning",
        "national income, money, banking or government budget analysis",
        "balance of payments, exchange rate or development indicator interpretation",
        "Indian economic development with cause, effect and conclusion",
    ],
    "physics": [
        "laws of motion, work-energy reasoning or force analysis",
        "thermodynamics, waves or oscillation with step-by-step explanation",
        "electricity, magnetism or optics concept application",
        "formula selection, units, calculation steps and final inference",
    ],
    "chemistry": [
        "chemical bonding, structure or periodic trend explanation",
        "stoichiometry, equilibrium or thermodynamics calculation reasoning",
        "organic reaction, mechanism or functional group identification",
        "solution, electrochemistry or kinetics data interpretation",
    ],
    "biology": [
        "cell structure, biomolecules or physiology explanation",
        "genetics, evolution or biotechnology reasoning",
        "plant and human physiology with labelled process steps",
        "ecology, environment and evidence-based conclusion",
    ],
    "mathematics": [
        "algebraic method with each calculation step shown",
        "calculus concept, derivative or integral interpretation",
        "coordinate geometry, vectors or probability reasoning",
        "formula selection, substitution, simplification and final answer",
    ],
    "english": [
        "theme, character, tone and textual evidence",
        "literary device, context and interpretation",
        "writing task structure, audience and clarity",
        "extract-based inference with quoted evidence and explanation",
    ],
}
GENERIC_QUESTION_PATTERNS = [
    re.compile(r"^build a clear answer about chapter\s+\d+\.?$", re.IGNORECASE),
    re.compile(r"^use the information from chapter\s+\d+\s+to answer clearly\.?$", re.IGNORECASE),
    re.compile(r"^build a definition from chapter\s+\d+", re.IGNORECASE),
    re.compile(r"^connect causes and effects from chapter\s+\d+", re.IGNORECASE),
    re.compile(r"^compare two important ideas from chapter\s+\d+", re.IGNORECASE),
    re.compile(r"^explain the main idea of chapter\s+\d+", re.IGNORECASE),
    re.compile(r"business/accounting/economics", re.IGNORECASE),
    re.compile(r"\b(human geography|cold war|plant physiology|chemical bonding)\b.*\bin\s+(accountancy|business studies|physics)\b", re.IGNORECASE),
]

RATE_LIMIT: dict[tuple[str, str], list[float]] = {}


def now() -> int:
    return int(time.time())


def json_dumps(data: object) -> bytes:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def remote_data_enabled() -> bool:
    return bool(IS_SERVERLESS or os.environ.get("LEARNIFY_REMOTE_DATA_BASE"))


def load_json_resource(path: Path) -> object:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    if not remote_data_enabled():
        raise FileNotFoundError(path)
    relative = str(path.relative_to(ROOT)).replace("\\", "/")
    request = Request(f"{REMOTE_DATA_BASE}{relative}", headers={"User-Agent": "Learnify/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError) as exc:
        raise FileNotFoundError(path) from exc


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              email TEXT NOT NULL UNIQUE COLLATE NOCASE,
              class_level INTEGER NOT NULL,
              password_hash TEXT NOT NULL,
              salt TEXT NOT NULL,
              created_at INTEGER NOT NULL
            )
            """
        )
        ensure_column(conn, "users", "role", "TEXT NOT NULL DEFAULT 'student'")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
              token TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
              csrf_token TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              expires_at INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS content_reviews (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              reviewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
              dataset_path TEXT NOT NULL,
              activity_id TEXT NOT NULL,
              status TEXT NOT NULL CHECK(status IN ('draft', 'approved', 'needs_revision', 'rejected')),
              notes TEXT NOT NULL DEFAULT '',
              updated_at INTEGER NOT NULL,
              UNIQUE(dataset_path, activity_id, reviewer_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS content_datasets (
              id TEXT PRIMARY KEY,
              class_level INTEGER NOT NULL,
              stream TEXT,
              subject TEXT NOT NULL,
              book TEXT NOT NULL,
              chapter TEXT NOT NULL,
              chapter_number INTEGER NOT NULL,
              json_path TEXT NOT NULL UNIQUE,
              source_pdf TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'generated',
              updated_at INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS assignments (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
              title TEXT NOT NULL,
              dataset_path TEXT NOT NULL,
              class_level INTEGER NOT NULL,
              due_at INTEGER,
              created_at INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
              activity_id TEXT NOT NULL,
              activity_type TEXT NOT NULL,
              difficulty TEXT NOT NULL,
              score INTEGER NOT NULL,
              marks INTEGER NOT NULL,
              selected_count INTEGER NOT NULL,
              created_at INTEGER NOT NULL
            )
            """
        )


def ensure_column(conn: sqlite3.Connection, table: str, column: str, declaration: str) -> None:
    columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 220_000)
    return digest.hex(), salt


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    actual_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(actual_hash, expected_hash)


def validate_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)) and len(email) <= 254


def validate_password(password: str) -> list[str]:
    errors: list[str] = []
    if len(password) < 8:
        errors.append("Use at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        errors.append("Add one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Add one lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Add one number.")
    return errors


def create_session(user_id: int) -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(24)
    with db() as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, csrf_token, created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
            (token, user_id, csrf, now(), now() + SESSION_TTL_SECONDS),
        )
    return token, csrf


def delete_session(token: str) -> None:
    with db() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def cleanup_sessions() -> None:
    with db() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (now(),))


def user_payload(row: sqlite3.Row) -> dict[str, object]:
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "classLevel": row["class_level"],
        "role": row["role"],
    }


def load_active_paths() -> set[str]:
    try:
        payload = load_json_resource(ACTIVE_DATASETS_JSON)
    except FileNotFoundError:
        return {str(PRACTICE_JSON.relative_to(ROOT)).replace("\\", "/")}
    return {str(item.get("jsonPath", "")).replace("\\", "/") for item in payload.get("activeDatasets", [])}


def discover_datasets(include_all: bool = False) -> list[dict[str, object]]:
    try:
        catalog = load_json_resource(CATALOG_JSON)
    except FileNotFoundError:
        catalog = None
    if catalog:
        datasets = [dict(item) for item in catalog.get("datasets", [])]
        if not include_all:
            datasets = [item for item in datasets if item.get("status") in STUDENT_CATALOG_STATUSES and item.get("hasJson")]
        return datasets

    entries: list[dict[str, object]] = []
    active_paths = load_active_paths()
    if MANIFEST_JSON.exists():
        manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        for entry in manifest.get("entries", []):
            json_path = ROOT / str(entry.get("outputPath", ""))
            json_rel = str(json_path.relative_to(ROOT)).replace("\\", "/") if ROOT in json_path.resolve().parents else str(entry.get("outputPath", ""))
            if json_path.exists() and (include_all or json_rel in active_paths or "generated" in STUDENT_CATALOG_STATUSES):
                status = "active" if json_rel in active_paths else "generated"
                entries.append({**entry, "jsonPath": json_rel, "status": status, "hasJson": True})
    for path in sorted((DATA_DIR / "practice").rglob("*.json")):
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        if any(entry.get("jsonPath") == relative for entry in entries):
            continue
        status = "active" if relative in active_paths else "generated"
        if not include_all and status not in STUDENT_CATALOG_STATUSES:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            source = payload.get("source", {})
            entries.append(
                {
                    "id": relative.replace("\\", "/").removesuffix(".json"),
                    "classLevel": source.get("classLevel"),
                    "stream": source.get("stream"),
                    "subject": source.get("subject"),
                    "book": source.get("book"),
                    "chapter": source.get("chapter"),
                    "chapterNumber": source.get("chapterNumber"),
                    "pdfPath": source.get("pdfPath"),
                    "jsonPath": relative,
                    "status": status,
                    "hasJson": True,
                }
            )
        except (json.JSONDecodeError, OSError):
            continue
    return entries


def resolve_dataset_path(dataset: str | None) -> Path | None:
    if not dataset:
        return PRACTICE_JSON
    for entry in discover_datasets(include_all=True):
        if dataset in {str(entry.get("id")), str(entry.get("jsonPath"))}:
            candidate = (ROOT / str(entry.get("jsonPath"))).resolve()
            if ROOT in candidate.parents and (candidate.exists() or remote_data_enabled()):
                return candidate
    return None


def ordered_item_ids(activity: dict[str, object]) -> list[str]:
    answer_key = activity.get("answerKey") if isinstance(activity.get("answerKey"), dict) else {}
    if not isinstance(answer_key, dict):
        return []
    for key in ("orderedItemIds", "requiredItemIds", "requiredConceptIds"):
        value = answer_key.get(key)
        if isinstance(value, list) and value:
            return [str(item) for item in value]
    return []


def answer_group_count(activities: list[dict[str, object]]) -> int:
    groups = {
        str(activity.get("questionGroupId") or activity.get("question") or activity.get("id"))
        for activity in activities
        if activity.get("type") == "answer_builder"
    }
    return len(groups)


def clean_display_text(value: object, class_level: int | None = None) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = text.replace("Â·", "-").replace("â—", "-").replace("â€™", "'")
    if class_level == 11:
        text = text.replace("Class 12", "Class 11")
    return text


def is_generic_question(question: object) -> bool:
    text = clean_display_text(question).strip()
    if len(text) < 12:
        return True
    return any(pattern.search(text) for pattern in GENERIC_QUESTION_PATTERNS)


def source_focus(activity: dict[str, object], fallback: str, class_level: int | None = None) -> str:
    candidates: list[str] = []
    for key in ("question", "modelAnswer", "sourceTextSummary"):
        value = clean_display_text(activity.get(key), class_level)
        if value and not is_generic_question(value):
            candidates.append(value)
    for item in activity.get("correctItems") or []:
        if isinstance(item, dict):
            value = clean_display_text(item.get("text"), class_level)
            if value and not is_generic_question(value):
                candidates.append(value)
    for candidate in candidates:
        candidate = re.sub(r"^(The Class \d+ [^:]+ question asks:|The accepted answer direction is:)\s*", "", candidate).strip()
        if len(candidate) > 22:
            suffix = "..." if len(candidate) > 260 else ""
            return candidate[:260].rstrip(" ,;:-") + suffix
    return clean_display_text(fallback, class_level) or "the selected concept"


def detailed_points_from_activity(activity: dict[str, object], fallback: str, count: int, class_level: int | None = None) -> list[str]:
    text = clean_display_text(activity.get("modelAnswer"), class_level)
    if not text or is_generic_question(text):
        text = " ".join(
            clean_display_text(item.get("text"), class_level)
            for item in activity.get("correctItems") or []
            if isinstance(item, dict)
        )
    if not text or len(text) < 30:
        text = clean_display_text(fallback, class_level)
    pieces = [piece.strip(" -") for piece in re.split(r"(?<=[.!?])\s+", text) if len(piece.strip()) > 12]
    if len(pieces) < count:
        focus = source_focus(activity, fallback, class_level)
        pieces.extend(
            [
                f"Start by identifying the exact demand of the question: {focus}.",
                "Use the relevant concept, formula, provision, event or textual evidence before writing the final point.",
                "Explain each point in full sentences so the examiner can see the reasoning.",
                "End with a conclusion that directly answers the command word and avoids unrelated material.",
            ]
        )
    return pieces[:count]


def detailed_question(activity_type: str, donor: dict[str, object], source: dict[str, object], index: int) -> str:
    class_level = int(source.get("classLevel") or donor.get("classLevel") or 0)
    subject = clean_display_text(source.get("subject") or donor.get("subject") or "the subject", class_level)
    chapter = clean_display_text(source.get("chapter") or donor.get("chapter") or "this chapter", class_level)
    focus = source_focus(donor, chapter, class_level)
    if "board-style practice for" in focus.lower() or focus.lower() == chapter.lower():
        subject_key = subject.lower()
        options = next((items for key, items in SENIOR_SUBJECT_FOCUS.items() if key in subject_key), [])
        if options:
            focus = options[(index - 1) % len(options)]
    task = STANDARD_TYPE_TASKS.get(activity_type, "write a detailed answer")
    return f"Class {class_level} {subject}: {task} for question {index} - {focus}"


def rewrite_activity_items_from_donor(activity: dict[str, object], donor: dict[str, object], source: dict[str, object]) -> None:
    class_level = int(source.get("classLevel") or donor.get("classLevel") or activity.get("classLevel") or 0)
    fallback = clean_display_text(source.get("chapter") or activity.get("chapter") or "this topic", class_level)
    correct_items = activity.get("correctItems") if isinstance(activity.get("correctItems"), list) else []
    distractors = activity.get("distractors") if isinstance(activity.get("distractors"), list) else []
    points = detailed_points_from_activity(donor, fallback, max(1, len(correct_items)), class_level)
    for index, item in enumerate(correct_items):
        if isinstance(item, dict):
            item["text"] = points[index % len(points)]
    wrong = [
        "This point is too general and does not answer the command word.",
        "This option adds unrelated information instead of using the given concept.",
        "This answer skips reasoning, evidence or working needed for senior-class marks.",
        "This statement may sound relevant, but it does not support the selected question.",
    ]
    for index, item in enumerate(distractors):
        if isinstance(item, dict):
            item["text"] = wrong[index % len(wrong)]
            item["misconception"] = "Generic or unsupported answer."


def make_synthetic_answer_builder(
    source_activity: dict[str, object],
    source: dict[str, object],
    group_number: int,
    difficulty: str,
) -> dict[str, object]:
    activity = deepcopy(source_activity)
    source_id = str(source_activity.get("id") or f"source-{group_number}")
    group_id = f"synthetic-q{group_number:02d}-{source_id}"
    activity["id"] = f"{group_id}-answer-builder-{difficulty}"
    activity["type"] = "answer_builder"
    activity["difficulty"] = difficulty
    activity["classLevel"] = source_activity.get("classLevel") or source.get("classLevel")
    activity["stream"] = source_activity.get("stream") or source.get("stream")
    activity["subject"] = source_activity.get("subject") or source.get("subject")
    activity["book"] = source_activity.get("book") or source.get("book")
    activity["chapter"] = source_activity.get("chapter") or source.get("chapter")
    activity["chapterNumber"] = source_activity.get("chapterNumber") or source.get("chapterNumber")
    activity["questionGroupId"] = group_id
    activity["chapterQuestionNumber"] = group_number
    activity["marks"] = source_activity.get("marks") or 5
    activity["sourceTextSummary"] = source_activity.get("sourceTextSummary") or f"Practice question for {source.get('chapter', 'this chapter')}."
    activity["sourceChapter"] = source_activity.get("sourceChapter") or source.get("chapter")
    activity["sourcePdf"] = source_activity.get("sourcePdf") or source.get("pdfPath")
    activity["hints"] = source_activity.get("hints") or [
        "Read the question first.",
        "Choose only cards that directly answer it.",
        "Keep the answer in a clear order.",
    ]
    activity["questionIdentifier"] = source_activity.get("questionIdentifier") or {
        "layoutProfileId": "explain",
        "layoutLabel": "Explanation Builder",
        "primaryPracticeType": "explain",
        "slotStrategy": "structured_answer",
        "recommendedLayout": "introduction, key points, conclusion",
    }

    correct_items = activity.get("correctItems") if isinstance(activity.get("correctItems"), list) else []
    correct_ids = [str(item.get("id")) for item in correct_items if isinstance(item, dict) and item.get("id")]
    if difficulty == "moderate":
        activity["instructions"] = "Put the answer parts in the correct order."
        activity["answerKey"] = {"orderedItemIds": ordered_item_ids(activity) or correct_ids}
        activity["correctSequence"] = activity["answerKey"]["orderedItemIds"]
        activity["answerSlots"] = [
            {"id": f"slot-{index}", "label": f"Part {index}"}
            for index in range(1, max(2, len(activity["answerKey"]["orderedItemIds"])) + 1)
        ]
    elif difficulty == "difficult":
        activity["instructions"] = "Choose the key cards that answer the question."
        activity["answerKey"] = {"requiredConceptIds": correct_ids}
        activity["correctSequence"] = correct_ids
        activity["answerSlots"] = [
            {"id": "intro", "label": "Opening"},
            {"id": "body", "label": "Main answer"},
            {"id": "end", "label": "Finish"},
        ]
    else:
        activity["instructions"] = "Drag the answer cards into the boxes. Leave wrong cards outside."
        activity["answerKey"] = {"orderedItemIds": ordered_item_ids(activity) or correct_ids}
        activity["correctSequence"] = activity["answerKey"]["orderedItemIds"]
        activity["answerSlots"] = [
            {"id": f"slot-{index}", "label": f"Sentence {index}"}
            for index in range(1, max(2, len(activity["answerKey"]["orderedItemIds"])) + 1)
        ]
    return activity


def make_synthetic_standard_activity(
    template: dict[str, object],
    donor: dict[str, object],
    source: dict[str, object],
    index: int,
) -> dict[str, object]:
    activity = deepcopy(template)
    activity_type = str(template.get("type") or "practice")
    class_level = int(source.get("classLevel") or donor.get("classLevel") or template.get("classLevel") or 0)
    is_upper_grade = class_level >= 11
    donor_question = (
        detailed_question(activity_type, donor, source, index)
        if is_upper_grade
        else str(donor.get("question") or template.get("question") or source.get("chapter") or "this chapter")
    )
    source_id = str(template.get("id") or activity_type)
    activity["id"] = f"{source_id}-extra-{index:02d}"
    activity["question"] = donor_question
    if is_upper_grade:
        points = detailed_points_from_activity(donor, donor_question, 4, class_level)
        activity["modelAnswer"] = " ".join(points)
        activity["instructions"] = f"Build a detailed Class {class_level} answer. Include concept, reasoning, evidence or working, and a direct conclusion."
        rewrite_activity_items_from_donor(activity, donor, source)
    else:
        activity["modelAnswer"] = donor.get("modelAnswer") or template.get("modelAnswer") or donor_question
    activity["sourceTextSummary"] = donor.get("sourceTextSummary") or template.get("sourceTextSummary") or f"Extra {activity_type} practice for {source.get('chapter', 'this chapter')}."
    activity["sourceChapter"] = template.get("sourceChapter") or source.get("chapter")
    activity["sourcePdf"] = template.get("sourcePdf") or source.get("pdfPath")
    activity["classLevel"] = template.get("classLevel") or donor.get("classLevel") or source.get("classLevel")
    activity["stream"] = template.get("stream") or donor.get("stream") or source.get("stream")
    activity["subject"] = template.get("subject") or donor.get("subject") or source.get("subject")
    activity["book"] = template.get("book") or donor.get("book") or source.get("book")
    activity["chapter"] = template.get("chapter") or donor.get("chapter") or source.get("chapter")
    activity["chapterNumber"] = template.get("chapterNumber") or donor.get("chapterNumber") or source.get("chapterNumber")
    activity["hints"] = template.get("hints") or donor.get("hints") or [
        "Read the question carefully.",
        "Use only the cards that match the question.",
    ]
    return activity


def expand_standard_activity_types(payload: dict[str, object], activities: list[dict[str, object]]) -> list[dict[str, object]]:
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    if not isinstance(source, dict):
        source = {}
    standard = [activity for activity in activities if activity.get("type") != "answer_builder"]
    answer_builders = [activity for activity in activities if activity.get("type") == "answer_builder"]
    donors = [
        activity
        for activity in [*answer_builders, *standard]
        if activity.get("question") and activity.get("modelAnswer")
    ]
    if not donors:
        return activities

    by_type: dict[str, list[dict[str, object]]] = {}
    for activity in standard:
        by_type.setdefault(str(activity.get("type")), []).append(activity)

    expanded = list(activities)
    for activity_type, items in by_type.items():
        if not activity_type or len(items) >= MIN_STANDARD_QUESTIONS_PER_TYPE:
            continue
        target_count = min(MAX_SYNTHETIC_STANDARD_PER_TYPE, MIN_STANDARD_QUESTIONS_PER_TYPE)
        needed = max(0, target_count - len(items))
        template = items[0]
        existing_ids = {str(activity.get("id")) for activity in expanded}
        written = 0
        donor_index = 0
        while written < needed and donor_index < len(donors) * 2:
            donor = donors[donor_index % len(donors)]
            donor_index += 1
            if donor.get("id") == template.get("id"):
                continue
            synthetic = make_synthetic_standard_activity(template, donor, source, len(items) + written + 1)
            if str(synthetic.get("id")) in existing_ids:
                synthetic["id"] = f"{synthetic.get('id')}-{written + 1}"
            existing_ids.add(str(synthetic.get("id")))
            expanded.append(synthetic)
            written += 1
    return expanded


def improve_upper_grade_activities(payload: dict[str, object], activities: list[dict[str, object]]) -> list[dict[str, object]]:
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    if not isinstance(source, dict):
        source = {}
    class_level = int(source.get("classLevel") or 0)
    if class_level < 11:
        return activities
    improved: list[dict[str, object]] = []
    seen_by_type: dict[str, set[str]] = {}
    answer_group_questions: dict[str, str] = {}
    donors = [activity for activity in activities if activity.get("modelAnswer") or activity.get("correctItems")] or activities
    for index, activity in enumerate(activities, start=1):
        item = deepcopy(activity)
        activity_type = str(item.get("type") or "practice")
        seen = seen_by_type.setdefault(activity_type, set())
        normalized_question = clean_display_text(item.get("question"), class_level).lower()
        group_id = str(item.get("questionGroupId") or "")
        duplicate_or_generic = is_generic_question(normalized_question) or (activity_type != "answer_builder" and normalized_question in seen)
        if duplicate_or_generic:
            donor = donors[(index - 1) % len(donors)]
            if activity_type == "answer_builder" and group_id in answer_group_questions:
                item["question"] = answer_group_questions[group_id]
            else:
                item["question"] = detailed_question(activity_type, donor, source, len(seen) + 1)
                if activity_type == "answer_builder" and group_id:
                    answer_group_questions[group_id] = str(item["question"])
            item["modelAnswer"] = " ".join(detailed_points_from_activity(donor, item["question"], 4, class_level))
            item["instructions"] = f"Write a detailed Class {class_level} answer with concept clarity, step-by-step explanation, and a final conclusion."
            rewrite_activity_items_from_donor(item, donor, source)
        else:
            item["question"] = clean_display_text(item.get("question"), class_level)
            item["modelAnswer"] = clean_display_text(item.get("modelAnswer"), class_level)
            item["instructions"] = clean_display_text(item.get("instructions"), class_level)
            item["hints"] = [clean_display_text(hint, class_level) for hint in item.get("hints") or []]
        seen.add(clean_display_text(item.get("question"), class_level).lower())
        improved.append(item)
    return improved


def expand_answer_builder_payload(payload: object) -> object:
    if not isinstance(payload, dict):
        return payload
    activities = payload.get("activities")
    if not isinstance(activities, list):
        return payload
    typed_activities = [activity for activity in activities if isinstance(activity, dict)]
    existing_groups = answer_group_count(typed_activities)
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    if not isinstance(source, dict):
        source = {}
    candidates = [
        activity
        for activity in typed_activities
        if activity.get("type") != "answer_builder"
        and activity.get("question")
        and isinstance(activity.get("correctItems"), list)
        and len(activity.get("correctItems") or []) >= 2
    ]
    augmented = dict(payload)
    augmented_activities = expand_standard_activity_types(augmented, [deepcopy(activity) for activity in typed_activities])
    if candidates and existing_groups < MIN_ANSWER_BUILDER_GROUPS:
        target_groups = min(MAX_SYNTHETIC_ANSWER_GROUPS, max(MIN_ANSWER_BUILDER_GROUPS, existing_groups))
        needed_groups = max(0, target_groups - existing_groups)
        for offset, candidate in enumerate(candidates[:needed_groups], start=1):
            group_number = existing_groups + offset
            for difficulty in ("easy", "moderate", "difficult"):
                augmented_activities.append(make_synthetic_answer_builder(candidate, source, group_number, difficulty))
    augmented_activities = improve_upper_grade_activities(augmented, augmented_activities)
    augmented["activities"] = augmented_activities
    coverage = dict(augmented.get("coverage") if isinstance(augmented.get("coverage"), dict) else {})
    coverage["activityCount"] = len(augmented_activities)
    coverage["chapterQuestionCount"] = max(int(coverage.get("chapterQuestionCount") or 0), answer_group_count(augmented_activities))
    coverage["answerBuilderExpanded"] = answer_group_count(augmented_activities) > existing_groups
    coverage["standardTypesExpanded"] = len(augmented_activities) > len(typed_activities)
    augmented["coverage"] = coverage
    return augmented


class LearnifyHandler(BaseHTTPRequestHandler):
    server_version = "LearnifyLocal/1.0"

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'",
        )
        super().end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {self.address_string()} {fmt % args}")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/session":
            return self.handle_session()
        if parsed.path == "/api/status":
            return self.handle_status()
        if parsed.path == "/api/datasets":
            return self.handle_datasets(parsed)
        if parsed.path == "/api/practice-data":
            return self.handle_practice_data(parsed)
        if parsed.path == "/api/progress":
            return self.handle_progress()
        if parsed.path == "/api/student/assignments":
            return self.handle_student_assignments()
        if parsed.path == "/api/admin/activities":
            return self.handle_admin_activities(parsed)
        if parsed.path == "/api/admin/reviews":
            return self.handle_admin_reviews(parsed)
        if parsed.path == "/api/teacher/analytics":
            return self.handle_teacher_analytics()
        if parsed.path == "/api/teacher/assignments":
            return self.handle_assignments()
        return self.serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if not self.check_rate_limit(parsed.path):
            return self.send_json({"error": "Too many requests. Try again in a minute."}, HTTPStatus.TOO_MANY_REQUESTS)
        if parsed.path == "/api/signup":
            return self.handle_signup()
        if parsed.path == "/api/login":
            return self.handle_login()
        if parsed.path == "/api/logout":
            return self.handle_logout()
        if parsed.path == "/api/progress":
            return self.handle_save_progress()
        if parsed.path == "/api/admin/reviews":
            return self.handle_save_review()
        if parsed.path == "/api/teacher/assignments":
            return self.handle_create_assignment()
        if parsed.path == "/api/admin/image-generation":
            return self.handle_admin_image_generation()
        return self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def check_rate_limit(self, path: str) -> bool:
        key = (self.client_address[0], path)
        window_start = time.time() - 60
        hits = [stamp for stamp in RATE_LIMIT.get(key, []) if stamp >= window_start]
        hits.append(time.time())
        RATE_LIMIT[key] = hits
        limit = 18 if path in {"/api/login", "/api/signup"} else 60
        return len(hits) <= limit

    def read_json_body(self) -> dict[str, object] | None:
        length_header = self.headers.get("Content-Length")
        if not length_header:
            self.send_json({"error": "Missing request body."}, HTTPStatus.BAD_REQUEST)
            return None
        try:
            length = int(length_header)
        except ValueError:
            self.send_json({"error": "Invalid Content-Length."}, HTTPStatus.BAD_REQUEST)
            return None
        if length > MAX_BODY_BYTES:
            self.send_json({"error": "Request body too large."}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return None
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON."}, HTTPStatus.BAD_REQUEST)
            return None

    def get_cookie(self, name: str) -> str | None:
        raw = self.headers.get("Cookie", "")
        for part in raw.split(";"):
            if "=" not in part:
                continue
            key, value = part.strip().split("=", 1)
            if key == name:
                return value
        return None

    def current_user(self) -> tuple[sqlite3.Row, sqlite3.Row] | None:
        token = self.get_cookie("learnify_session")
        if not token:
            return None
        with db() as conn:
            session = conn.execute("SELECT * FROM sessions WHERE token = ? AND expires_at >= ?", (token, now())).fetchone()
            if not session:
                return None
            user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
            if not user:
                return None
            return user, session

    def require_auth(self) -> tuple[sqlite3.Row, sqlite3.Row] | None:
        auth = self.current_user()
        if not auth:
            self.send_json({"error": "Authentication required."}, HTTPStatus.UNAUTHORIZED)
            return None
        return auth

    def require_csrf(self, session: sqlite3.Row) -> bool:
        token = self.headers.get("X-CSRF-Token")
        if not token or not hmac.compare_digest(token, session["csrf_token"]):
            self.send_json({"error": "Invalid CSRF token."}, HTTPStatus.FORBIDDEN)
            return False
        return True

    def require_reviewer(self) -> tuple[sqlite3.Row, sqlite3.Row] | None:
        auth = self.require_auth()
        if not auth:
            return None
        user, session = auth
        if user["role"] not in {"teacher", "admin"}:
            self.send_json({"error": "Teacher or admin access required."}, HTTPStatus.FORBIDDEN)
            return None
        return user, session

    def handle_session(self) -> None:
        auth = self.current_user()
        if not auth:
            return self.send_json({"authenticated": False, "user": None, "csrfToken": None})
        user, session = auth
        return self.send_json({"authenticated": True, "user": user_payload(user), "csrfToken": session["csrf_token"]})

    def handle_status(self) -> None:
        catalog = {}
        try:
            catalog = load_json_resource(CATALOG_JSON)
        except FileNotFoundError:
            catalog = {}
        with db() as conn:
            user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            attempt_count = conn.execute("SELECT COUNT(*) FROM progress_events").fetchone()[0]
            assignment_count = conn.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
        return self.send_json(
            {
                "ok": True,
                "server": "LearnifyLocal/1.0",
                "catalog": catalog.get("totals", {}),
                "studentCatalogStatuses": sorted(STUDENT_CATALOG_STATUSES),
                "database": {
                    "users": user_count,
                    "attempts": attempt_count,
                    "assignments": assignment_count,
                },
            }
        )

    def handle_datasets(self, parsed) -> None:
        query = parse_qs(parsed.query)
        include_all = query.get("includeAll", ["0"])[0] == "1"
        if include_all:
            auth = self.current_user()
            include_all = bool(auth and auth[0]["role"] in {"teacher", "admin"})
        self.send_json({"datasets": discover_datasets(include_all=include_all)})

    def handle_signup(self) -> None:
        body = self.read_json_body()
        if body is None:
            return
        name = str(body.get("name", "")).strip()
        email = str(body.get("email", "")).strip().lower()
        password = str(body.get("password", ""))
        class_level = int(body.get("classLevel", 7) or 7)
        requested_role = str(body.get("role", "student")).strip().lower()

        errors: dict[str, object] = {}
        if len(name) < 2 or len(name) > 80:
            errors["name"] = "Enter a name between 2 and 80 characters."
        if not validate_email(email):
            errors["email"] = "Enter a valid email address."
        password_errors = validate_password(password)
        if password_errors:
            errors["password"] = password_errors
        if class_level < MIN_CLASS_LEVEL or class_level > MAX_CLASS_LEVEL:
            errors["classLevel"] = f"Choose a class from {MIN_CLASS_LEVEL} to {MAX_CLASS_LEVEL}."
        if errors:
            return self.send_json({"error": "Validation failed.", "fields": errors}, HTTPStatus.BAD_REQUEST)

        password_hash, salt = hash_password(password)
        try:
            with db() as conn:
                user_count = int(conn.execute("SELECT COUNT(*) FROM users").fetchone()[0])
                role = "admin" if user_count == 0 else ("teacher" if requested_role == "teacher" else "student")
                cursor = conn.execute(
                    "INSERT INTO users (name, email, class_level, password_hash, salt, created_at, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, email, class_level, password_hash, salt, now(), role),
                )
                user_id = int(cursor.lastrowid)
        except sqlite3.IntegrityError:
            return self.send_json({"error": "An account with this email already exists."}, HTTPStatus.CONFLICT)

        token, csrf = create_session(user_id)
        return self.send_json(
            {
                "authenticated": True,
                "csrfToken": csrf,
                "user": {"id": user_id, "name": name, "email": email, "classLevel": class_level, "role": role},
            },
            HTTPStatus.CREATED,
            cookies=[self.session_cookie(token)],
        )

    def handle_login(self) -> None:
        body = self.read_json_body()
        if body is None:
            return
        email = str(body.get("email", "")).strip().lower()
        password = str(body.get("password", ""))
        with db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user or not verify_password(password, user["salt"], user["password_hash"]):
            return self.send_json({"error": "Invalid email or password."}, HTTPStatus.UNAUTHORIZED)
        token, csrf = create_session(int(user["id"]))
        return self.send_json({"authenticated": True, "csrfToken": csrf, "user": user_payload(user)}, cookies=[self.session_cookie(token)])

    def handle_logout(self) -> None:
        token = self.get_cookie("learnify_session")
        if token:
            delete_session(token)
        return self.send_json({"ok": True}, cookies=["learnify_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"])

    def handle_practice_data(self, parsed) -> None:
        query = parse_qs(parsed.query)
        dataset_path = resolve_dataset_path(query.get("dataset", [None])[0])
        if not dataset_path:
            return self.send_json({"error": "Practice JSON has not been generated."}, HTTPStatus.NOT_FOUND)
        try:
            payload = load_json_resource(dataset_path)
        except FileNotFoundError:
            return self.send_json({"error": "Practice JSON has not been generated."}, HTTPStatus.NOT_FOUND)
        return self.send_json(expand_answer_builder_payload(payload))

    def handle_admin_activities(self, parsed) -> None:
        auth = self.require_reviewer()
        if not auth:
            return
        query = parse_qs(parsed.query)
        dataset_path = resolve_dataset_path(query.get("dataset", [None])[0])
        if not dataset_path:
            return self.send_json({"error": "Dataset not found."}, HTTPStatus.NOT_FOUND)
        try:
            payload = load_json_resource(dataset_path)
        except FileNotFoundError:
            return self.send_json({"error": "Dataset not found."}, HTTPStatus.NOT_FOUND)
        activities = payload.get("activities", [])
        return self.send_json(
            {
                "dataset": str(dataset_path.relative_to(ROOT)),
                "source": payload.get("source"),
                "activities": [
                    {
                        "id": activity.get("id"),
                        "type": activity.get("type"),
                        "difficulty": activity.get("difficulty"),
                        "question": activity.get("question"),
                        "questionIdentifier": activity.get("questionIdentifier"),
                    }
                    for activity in activities
                ],
            }
        )

    def handle_admin_reviews(self, parsed) -> None:
        auth = self.require_reviewer()
        if not auth:
            return
        query = parse_qs(parsed.query)
        dataset = query.get("dataset", [""])[0]
        with db() as conn:
            rows = conn.execute(
                """
                SELECT r.id, r.dataset_path, r.activity_id, r.status, r.notes, r.updated_at,
                       u.name AS reviewer_name
                FROM content_reviews r
                JOIN users u ON u.id = r.reviewer_id
                WHERE (? = '' OR r.dataset_path = ?)
                ORDER BY r.updated_at DESC
                LIMIT 100
                """,
                (dataset, dataset),
            ).fetchall()
        return self.send_json({"reviews": [dict(row) for row in rows]})

    def handle_teacher_analytics(self) -> None:
        auth = self.require_reviewer()
        if not auth:
            return
        with db() as conn:
            rows = conn.execute(
                """
                SELECT activity_type, difficulty, COUNT(*) AS attempts,
                       ROUND(AVG(CAST(score AS REAL) / marks) * 100) AS average_percent
                FROM progress_events
                GROUP BY activity_type, difficulty
                ORDER BY attempts DESC
                LIMIT 20
                """
            ).fetchall()
            assignment_count = conn.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
        return self.send_json({"rows": [dict(row) for row in rows], "assignmentCount": assignment_count})

    def handle_assignments(self) -> None:
        auth = self.require_reviewer()
        if not auth:
            return
        with db() as conn:
            rows = conn.execute(
                """
                SELECT id, title, dataset_path, class_level, due_at, created_at
                FROM assignments
                ORDER BY created_at DESC
                LIMIT 50
                """
            ).fetchall()
        return self.send_json({"assignments": [dict(row) for row in rows]})

    def handle_student_assignments(self) -> None:
        auth = self.require_auth()
        if not auth:
            return
        user, _session = auth
        with db() as conn:
            rows = conn.execute(
                """
                SELECT a.id, a.title, a.dataset_path, a.class_level, a.due_at, a.created_at,
                       u.name AS teacher_name
                FROM assignments a
                JOIN users u ON u.id = a.teacher_id
                WHERE a.class_level = ?
                ORDER BY COALESCE(a.due_at, a.created_at) ASC, a.created_at DESC
                LIMIT 50
                """,
                (user["class_level"],),
            ).fetchall()
        return self.send_json({"assignments": [dict(row) for row in rows]})

    def handle_create_assignment(self) -> None:
        auth = self.require_reviewer()
        if not auth:
            return
        user, session = auth
        if not self.require_csrf(session):
            return
        body = self.read_json_body()
        if body is None:
            return
        title = str(body.get("title", "")).strip()[:140]
        dataset_path = str(body.get("datasetPath", "")).strip()[:240]
        class_level = int(body.get("classLevel", 7) or 7)
        due_at = body.get("dueAt")
        if not title or not dataset_path or class_level < MIN_CLASS_LEVEL or class_level > MAX_CLASS_LEVEL:
            return self.send_json({"error": "Invalid assignment payload."}, HTTPStatus.BAD_REQUEST)
        if not resolve_dataset_path(dataset_path):
            return self.send_json({"error": "Dataset not found."}, HTTPStatus.BAD_REQUEST)
        with db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO assignments (teacher_id, title, dataset_path, class_level, due_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user["id"], title, dataset_path, class_level, int(due_at) if due_at else None, now()),
            )
        return self.send_json({"ok": True, "id": cursor.lastrowid}, HTTPStatus.CREATED)

    def handle_admin_image_generation(self) -> None:
        auth = self.require_reviewer()
        if not auth:
            return
        _user, session = auth
        if not self.require_csrf(session):
            return
        body = self.read_json_body()
        if body is None:
            return

        prompt = str(body.get("prompt", "")).strip()
        negative_prompt = str(body.get("negativePrompt", "")).strip()
        name = str(body.get("name", "")).strip()
        try:
            width = int(body.get("width", 1024))
            height = int(body.get("height", 1024))
            steps = int(body.get("steps", 4))
            seed_value = body.get("seed", None)
            seed = int(seed_value) if seed_value not in (None, "") else None
        except (TypeError, ValueError):
            return self.send_json({"error": "Invalid image generation settings."}, HTTPStatus.BAD_REQUEST)

        if not prompt or len(prompt) > 1200:
            return self.send_json({"error": "Prompt must be between 1 and 1200 characters."}, HTTPStatus.BAD_REQUEST)
        if width < 512 or height < 512 or width > 1536 or height > 1536 or width % 8 or height % 8:
            return self.send_json({"error": "Width and height must be multiples of 8 between 512 and 1536."}, HTTPStatus.BAD_REQUEST)
        if steps not in {2, 4, 8}:
            return self.send_json({"error": "SDXL-Lightning steps must be 2, 4, or 8."}, HTTPStatus.BAD_REQUEST)

        IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        command = [
            IMAGE_PYTHON,
            str(IMAGE_GENERATOR_SCRIPT),
            prompt,
            "--negative-prompt",
            negative_prompt,
            "--name",
            name,
            "--out-dir",
            str(IMAGE_OUTPUT_DIR),
            "--width",
            str(width),
            "--height",
            str(height),
            "--steps",
            str(steps),
        ]
        if seed is not None:
            command.extend(["--seed", str(seed)])

        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=IMAGE_GENERATION_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return self.send_json({"error": "Image generation timed out. Try a smaller size or use CUDA."}, HTTPStatus.REQUEST_TIMEOUT)

        if result.returncode != 0:
            message = (result.stderr or result.stdout or "Image generation failed.").strip()
            return self.send_json({"error": message[-1200:]}, HTTPStatus.INTERNAL_SERVER_ERROR)

        try:
            payload = json.loads(result.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            return self.send_json({"error": "Image generator returned an invalid response."}, HTTPStatus.INTERNAL_SERVER_ERROR)
        return self.send_json({"ok": True, "image": payload}, HTTPStatus.CREATED)

    def handle_save_review(self) -> None:
        auth = self.require_reviewer()
        if not auth:
            return
        user, session = auth
        if not self.require_csrf(session):
            return
        body = self.read_json_body()
        if body is None:
            return
        dataset_path = str(body.get("datasetPath", ""))[:240]
        activity_id = str(body.get("activityId", ""))[:180]
        status = str(body.get("status", "draft")).strip()
        notes = str(body.get("notes", ""))[:2000]
        if status not in {"draft", "approved", "needs_revision", "rejected"} or not dataset_path or not activity_id:
            return self.send_json({"error": "Invalid review payload."}, HTTPStatus.BAD_REQUEST)
        with db() as conn:
            conn.execute(
                """
                INSERT INTO content_reviews (reviewer_id, dataset_path, activity_id, status, notes, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(dataset_path, activity_id, reviewer_id)
                DO UPDATE SET status = excluded.status, notes = excluded.notes, updated_at = excluded.updated_at
                """,
                (user["id"], dataset_path, activity_id, status, notes, now()),
            )
        return self.send_json({"ok": True})

    def handle_progress(self) -> None:
        auth = self.require_auth()
        if not auth:
            return
        user, _session = auth
        with db() as conn:
            rows = conn.execute(
                """
                SELECT activity_id, activity_type, difficulty, score, marks, selected_count, created_at
                FROM progress_events
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 20
                """,
                (user["id"],),
            ).fetchall()
        events = [dict(row) for row in rows]
        attempts = len(events)
        average = round(sum(row["score"] / row["marks"] for row in events) * 100 / attempts) if attempts else 0
        return self.send_json({"events": events, "attempts": attempts, "averagePercent": average})

    def handle_save_progress(self) -> None:
        auth = self.require_auth()
        if not auth:
            return
        user, session = auth
        if not self.require_csrf(session):
            return
        body = self.read_json_body()
        if body is None:
            return
        activity_id = str(body.get("activityId", ""))[:160]
        activity_type = str(body.get("activityType", ""))[:80]
        difficulty = str(body.get("difficulty", ""))[:40]
        score = int(body.get("score", 0) or 0)
        marks = int(body.get("marks", 5) or 5)
        selected_count = int(body.get("selectedCount", 0) or 0)
        if not activity_id or score < 0 or marks < 1 or score > marks:
            return self.send_json({"error": "Invalid progress payload."}, HTTPStatus.BAD_REQUEST)
        with db() as conn:
            conn.execute(
                """
                INSERT INTO progress_events
                (user_id, activity_id, activity_type, difficulty, score, marks, selected_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user["id"], activity_id, activity_type, difficulty, score, marks, selected_count, now()),
            )
        return self.send_json({"ok": True})

    def serve_static(self, request_path: str) -> None:
        safe_path = unquote(request_path).split("?", 1)[0]
        if safe_path in {"", "/"}:
            safe_path = "/index.html"
        candidate = (ROOT / safe_path.lstrip("/")).resolve()
        if ROOT not in candidate.parents and candidate != ROOT:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not candidate.exists() or not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        content = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        if candidate.suffix in {".html", ".js", ".css"}:
            self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def session_cookie(self, token: str) -> str:
        return f"learnify_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_TTL_SECONDS}"

    def send_json(self, data: object, status: HTTPStatus = HTTPStatus.OK, cookies: list[str] | None = None) -> None:
        payload = json_dumps(data)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        for cookie in cookies or []:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    print("Initializing Learnify...", flush=True)
    init_db()
    cleanup_sessions()
    print(f"Opening server on {HOST}:{PORT}...", flush=True)
    httpd = ThreadingHTTPServer((HOST, PORT), LearnifyHandler)
    print(f"Learnify running at http://{HOST}:{PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
