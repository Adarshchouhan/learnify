# Learnify Docs Index

Start here when continuing the project.

## Current State

- `PROJECT_CONTEXT.md`: product goal, current architecture, verified checks and remaining work.
- `mvp-completion-system.md`: the seven MVP workstreams and what has been implemented.
- `roadmap.md`: completed, next and later priorities.

## Content Pipeline

- `chapter-practice-generation-system.md`: how a chapter PDF becomes practice JSON.
- `content-rollout-plan.md`: how scanned PDFs move to generated, reviewed and active states.
- `quality-gate.md`: review checklist before a chapter goes live.
- `data-schema.md`: JSON fields, manifest fields and dataset API shape.

## Product And Platform

- `ui-rules.md`: UI behavior, correctness reveal rules and specialized layouts.
- `auth-system.md`: auth, sessions, roles, CSRF, review APIs and security headers.

## Rule Of Thumb

Do not treat a chapter as live just because its PDF was scanned or JSON was generated. A chapter becomes student-facing only after it is listed in `data/catalog/active-datasets.json` and the catalog is rebuilt.
