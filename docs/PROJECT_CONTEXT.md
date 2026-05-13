# Learnify Project Context

## Product Goal

Learnify is a Class 6-12 answer-writing practice platform. Students improve written answers by building answers from structured parts instead of only reading model answers.

The core practice model has three levels:

- `easy`: full sentences arranged in the exact correct sequence
- `moderate`: half-sentence chunks arranged in the exact correct sequence
- `difficult`: phrase/key-point construction

The app should support every major question type used in school practice, including explain, compare/contrast, cause/effect, process/sequence, fill blanks, data/table, definition, timeline, evidence, assertion-reason and more.

## Current Implementation

Local project path:

```text
E:\Learnify
```

Run locally:

```powershell
python server.py
```

Default URL:

```text
http://127.0.0.1:5173
```

Current app type:

- dependency-free Python + HTML/CSS/JS local SaaS prototype
- SQLite-backed auth and progress tracking
- frontend served by `server.py`
- generated practice JSON served from `/api/practice-data`

## Key Files

- `server.py`: localhost server, static hosting, auth APIs, progress APIs, security headers
- `index.html`: landing page, auth form, protected dashboard shell
- `styles.css`: landing, SaaS dashboard and practice UI styling
- `app.js`: auth flow, dashboard state, drag/drop, scoring, feedback, question navigation
- `scripts/build_practice_data.py`: PDF extraction and practice JSON generation
- `scripts/validate_practice_json.py`: JSON validation checks
- `schema/practice-activity.schema.json`: dataset schema
- `data/practice/class-7/science-curiosity/life-processes-in-animals.json`: current pilot dataset
- `docs/chapter-practice-generation-system.md`: repeatable chapter generation system

## Current Dataset

Pilot source:

```text
D:\LX\all class pdf\class 7\Science - Curiosity\gecu109.pdf
```

Pilot chapter:

```text
Class 7 > Science - Curiosity > Chapter 9 - Life Processes in Animals
```

Current generated coverage:

- 84 total activities
- 20 chapter question groups
- 10 textbook/exercise-style questions
- 10 major in-chapter conceptual questions
- 3 answer-builder modes per chapter question
- 21 additional interactive question-type examples
- 8 layout profiles

Layout profiles:

- `sequence`
- `explain`
- `compare`
- `cause_effect`
- `experiment`
- `data`
- `definition`
- `assertion_reason`

## Important Product Rules

- Correct/distractor colors must not be visible before submission.
- Correct/distractor status reveals only after the student checks the answer.
- For `easy` and `moderate`, sequence is strict.
- A correct sentence in the wrong placeholder is wrong.
- Feedback must show exact slot-order score, not just selected-correct score.
- The Next Question control cycles through chapter question groups.
- Difficulty tabs switch modes inside the current question.
- Future chapters should follow `docs/chapter-practice-generation-system.md`.

## Auth And Security

Implemented locally in `server.py`:

- signup/login
- client and server validation
- PBKDF2 password hashing with per-user salt
- SQLite users, sessions and progress events
- HttpOnly SameSite session cookie
- CSRF token required for progress writes
- basic rate limiting for POST routes
- security headers:
  - `Content-Security-Policy`
  - `X-Content-Type-Options`
  - `X-Frame-Options`
  - `Referrer-Policy`
  - `Permissions-Policy`

Local SQLite runtime files are ignored by git.

## Verified Checks

Commands used:

```powershell
python scripts/build_practice_data.py
python scripts/validate_practice_json.py
python -m py_compile server.py scripts/build_practice_data.py scripts/validate_practice_json.py
node --check app.js
```

Live server checks performed:

- landing page returns `200`
- `/api/practice-data` returns current generated JSON
- bad signup validation returns `400`
- signup returns `201`
- session returns authenticated user after signup
- progress POST works with CSRF token
- progress GET returns saved attempt
- logout works
- login works after logout

## Known Next Steps

- Generalize `scripts/build_practice_data.py` to accept class/subject/chapter PDF arguments instead of the current pilot constants.
- Add real layout rendering for non-answer-builder profiles such as compare table, experiment builder and data/table builder.
- Add teacher/admin content review tools.
- Add migrations if moving from SQLite local prototype to production database.
- Add automated browser tests for drag/drop and exact sequence feedback.
- Add all class 6-12 chapters once the pilot system is approved.
