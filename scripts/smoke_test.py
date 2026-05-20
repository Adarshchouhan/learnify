from __future__ import annotations

import http.cookiejar
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORT = "5184"
BASE_URL = f"http://127.0.0.1:{PORT}"


class Client:
    def __init__(self) -> None:
        self.cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookies))
        self.csrf = ""

    def request(self, path: str, method: str = "GET", payload: dict[str, object] | None = None) -> dict[str, object]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if self.csrf and method != "GET":
            headers["X-CSRF-Token"] = self.csrf
        request = urllib.request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
        with self.opener.open(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))


def wait_for_server() -> None:
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{BASE_URL}/api/session", timeout=1).read()
            return
        except OSError:
            time.sleep(0.25)
    raise RuntimeError("Server did not start in time.")


def main() -> int:
    env = os.environ.copy()
    env["LEARNIFY_PORT"] = PORT
    process = subprocess.Popen([sys.executable, "server.py"], cwd=ROOT, env=env)
    try:
        wait_for_server()
        client = Client()
        signup = client.request(
            "/api/signup",
            "POST",
            {
                "name": "Smoke Tester",
                "email": f"smoke-{int(time.time())}@learnify.test",
                "password": "SmokeTest1",
                "classLevel": 7,
            },
        )
        client.csrf = str(signup["csrfToken"])
        session = client.request("/api/session")
        assert session["authenticated"] is True

        datasets = client.request("/api/datasets")
        assert isinstance(datasets.get("datasets"), list)

        practice = client.request("/api/practice-data")
        activities = practice.get("activities", [])
        assert len(activities) >= 24
        answer_builder = next(activity for activity in activities if activity["type"] == "answer_builder")
        assert answer_builder["answerKey"].get("orderedItemIds") or answer_builder["answerKey"].get("requiredConceptIds")

        progress = client.request(
            "/api/progress",
            "POST",
            {
                "activityId": answer_builder["id"],
                "activityType": answer_builder["type"],
                "difficulty": answer_builder["difficulty"],
                "score": 5,
                "marks": 5,
                "selectedCount": len(answer_builder["correctItems"]),
            },
        )
        assert progress["ok"] is True
        summary = client.request("/api/progress")
        assert int(summary["attempts"]) >= 1

        teacher = Client()
        teacher_signup = teacher.request(
            "/api/signup",
            "POST",
            {
                "name": "Teacher Smoke",
                "email": f"teacher-{int(time.time())}@learnify.test",
                "password": "TeacherTest1",
                "classLevel": 7,
                "role": "teacher",
            },
        )
        teacher.csrf = str(teacher_signup["csrfToken"])
        admin_activities = teacher.request("/api/admin/activities")
        assert len(admin_activities.get("activities", [])) >= 24
        analytics = teacher.request("/api/teacher/analytics")
        assert "rows" in analytics
        assignment = teacher.request(
            "/api/teacher/assignments",
            "POST",
            {
                "title": "Smoke assignment",
                "datasetPath": "data/practice/class-7/science-curiosity/life-processes-in-animals.json",
                "classLevel": 7,
                "dueAt": int(time.time()) + 86_400,
            },
        )
        assert assignment["ok"] is True

        student_assignments = client.request("/api/student/assignments")
        assignments = student_assignments.get("assignments", [])
        assert any(item.get("title") == "Smoke assignment" for item in assignments)
        assert any(item.get("due_at") for item in assignments if item.get("title") == "Smoke assignment")
        print("Smoke test passed.")
        return 0
    except (AssertionError, urllib.error.HTTPError, RuntimeError) as error:
        print(f"Smoke test failed: {error}")
        return 1
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
