# Auth And Security System

## Current Scope

The local SaaS prototype uses `server.py` for authentication, sessions and progress APIs.

This is suitable for local MVP testing. Before production, move secrets, sessions and migrations into a production-grade framework or service.

## Data Storage

SQLite database path:

```text
data/learnify.sqlite3
```

Tables:

- `users`: name, email, class level, password hash, salt, created time
- `sessions`: token, user id, CSRF token, expiry
- `progress_events`: user id, activity id, type, difficulty, score, selected count

Runtime SQLite files are ignored by git.

## Passwords

Passwords are hashed with:

- PBKDF2-HMAC-SHA256
- per-user random salt
- 220,000 iterations

Signup password validation requires:

- at least 8 characters
- one uppercase letter
- one lowercase letter
- one number

## Sessions

Sessions use:

- random URL-safe token
- HttpOnly cookie
- SameSite=Lax
- 7-day expiry

Session API:

```text
GET /api/session
```

## CSRF

The session response includes a CSRF token.

Progress writes require:

```text
X-CSRF-Token: <token>
```

Protected route:

```text
POST /api/progress
```

## API Routes

- `POST /api/signup`
- `POST /api/login`
- `POST /api/logout`
- `GET /api/session`
- `GET /api/practice-data`
- `GET /api/progress`
- `POST /api/progress`

## Security Headers

The server sends:

- `Content-Security-Policy`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: same-origin`
- `Permissions-Policy`

## Current Validation Status

Verified manually:

- invalid signup rejected
- valid signup creates session
- login works
- logout clears session
- progress write requires authenticated session and CSRF
