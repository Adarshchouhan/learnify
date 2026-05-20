# Production Readiness Plan

The current Learnify build is a localhost MVP. This file defines what changes before public production.

## Already Implemented Locally

- Signup/login
- PBKDF2 password hashing
- HttpOnly SameSite sessions
- CSRF for writes
- Security headers
- SQLite persistence
- Dataset catalog
- Teacher/admin roles
- Review API
- Assignment and analytics tables
- `.env.example` contract

## Required Before Public Launch

- Move from local SQLite to a managed database such as PostgreSQL.
- Store secrets outside source control.
- Add HTTPS and secure cookies.
- Add email verification and password reset.
- Add tenant/school boundaries.
- Add audit logs for admin/review actions.
- Add background jobs for PDF extraction and generation.
- Add object storage for PDFs and generated JSON.
- Add rate limiting backed by shared storage.
- Add browser automation for drag/drop workflows.

## Environment Contract

See `.env.example`.

Important variables:

- `LEARNIFY_PORT`
- `LEARNIFY_HOST`
- `LEARNIFY_ENV`
- `LEARNIFY_DATABASE_URL`
- `LEARNIFY_CONTENT_ROOT`
- `LEARNIFY_CATALOG_PATH`
- `LEARNIFY_SESSION_TTL_SECONDS`

## Deployment Shape

Recommended production architecture:

- web app/API server
- managed PostgreSQL
- object storage for PDFs and generated datasets
- worker process for content generation
- CDN/static hosting for frontend assets
- monitoring and logs

## Database Migration Path

Current SQLite tables:

- `users`
- `sessions`
- `progress_events`
- `content_reviews`
- `content_datasets`
- `assignments`

## Current Limitation

The local MVP now has the required table and API shape for production migration, but it is not deployed publicly. Treat this as production-ready scaffolding, not a hosted production environment.

These map directly to PostgreSQL tables. Keep `progress_events`, `content_reviews` and `assignments` append-friendly so teacher analytics can be computed reliably.
