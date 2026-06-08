from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path(r"C:\Users\acer\Downloads\Data Abstractor\Data Abstractor\data\learnify_cbse.sqlite")


def main() -> int:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    print("SUBJECT COUNTS")
    for row in con.execute(
        """
        SELECT subject, COUNT(*) AS paper_count, SUM(question_count) AS question_count
        FROM papers
        WHERE class_level = '12'
        GROUP BY subject
        ORDER BY subject
        """
    ):
        print(dict(row))

    print("SAMPLES")
    for subject in ["English", "Business Studies", "Economics"]:
        print(f"--- {subject}")
        rows = con.execute(
            """
            SELECT p.id AS paper_id, p.subject, p.title, p.academic_session, p.paper_kind,
                   q.question_number, q.question_text, q.solution_text,
                   q.suggested_answer_format, q.answer_sequence_json
            FROM papers p
            JOIN questions q ON q.paper_id = p.id
            WHERE p.class_level = '12'
              AND p.subject LIKE ?
              AND LENGTH(q.question_text) > 40
            LIMIT 5
            """,
            (f"%{subject}%",),
        ).fetchall()
        for row in rows:
            print(dict(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
