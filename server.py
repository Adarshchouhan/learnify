from __future__ import annotations

import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "learnify.sqlite3"
PRACTICE_JSON = DATA_DIR / "practice" / "class-7" / "science-curiosity" / "life-processes-in-animals.json"
HOST = "127.0.0.1"
PORT = int(os.environ.get("LEARNIFY_PORT", "5173"))
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7
MAX_BODY_BYTES = 128 * 1024

RATE_LIMIT: dict[tuple[str, str], list[float]] = {}


def now() -> int:
    return int(time.time())


def json_dumps(data: object) -> bytes:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
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
    }


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
        if parsed.path == "/api/practice-data":
            return self.handle_practice_data()
        if parsed.path == "/api/progress":
            return self.handle_progress()
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
        length = int(length_header)
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

    def handle_session(self) -> None:
        auth = self.current_user()
        if not auth:
            return self.send_json({"authenticated": False, "user": None, "csrfToken": None})
        user, session = auth
        return self.send_json({"authenticated": True, "user": user_payload(user), "csrfToken": session["csrf_token"]})

    def handle_signup(self) -> None:
        body = self.read_json_body()
        if body is None:
            return
        name = str(body.get("name", "")).strip()
        email = str(body.get("email", "")).strip().lower()
        password = str(body.get("password", ""))
        class_level = int(body.get("classLevel", 7) or 7)

        errors: dict[str, object] = {}
        if len(name) < 2 or len(name) > 80:
            errors["name"] = "Enter a name between 2 and 80 characters."
        if not validate_email(email):
            errors["email"] = "Enter a valid email address."
        password_errors = validate_password(password)
        if password_errors:
            errors["password"] = password_errors
        if class_level < 6 or class_level > 12:
            errors["classLevel"] = "Choose a class from 6 to 12."
        if errors:
            return self.send_json({"error": "Validation failed.", "fields": errors}, HTTPStatus.BAD_REQUEST)

        password_hash, salt = hash_password(password)
        try:
            with db() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (name, email, class_level, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, email, class_level, password_hash, salt, now()),
                )
                user_id = int(cursor.lastrowid)
        except sqlite3.IntegrityError:
            return self.send_json({"error": "An account with this email already exists."}, HTTPStatus.CONFLICT)

        token, csrf = create_session(user_id)
        return self.send_json(
            {"authenticated": True, "csrfToken": csrf, "user": {"id": user_id, "name": name, "email": email, "classLevel": class_level}},
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

    def handle_practice_data(self) -> None:
        if not PRACTICE_JSON.exists():
            return self.send_json({"error": "Practice JSON has not been generated."}, HTTPStatus.NOT_FOUND)
        payload = json.loads(PRACTICE_JSON.read_text(encoding="utf-8"))
        return self.send_json(payload)

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
    init_db()
    cleanup_sessions()
    httpd = ThreadingHTTPServer((HOST, PORT), LearnifyHandler)
    print(f"Learnify running at http://{HOST}:{PORT}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
