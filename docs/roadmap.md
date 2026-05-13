# Learnify Roadmap

## Completed

- Local Python server
- Landing page
- Signup/login
- SQLite user/session/progress storage
- Security headers
- CSRF-protected progress writes
- Practice dashboard
- Answer-builder drag/drop UI
- Easy, moderate and difficult modes
- Exact sequence validation for easy/moderate
- Correct/distractor reveal only after submission
- Previous/next chapter question navigation
- Class 7 Science Chapter 9 pilot dataset
- 84 generated pilot activities
- Question identifier and layout profile system
- Repeatable chapter-generation documentation

## Next

- Make `scripts/build_practice_data.py` accept CLI arguments for class, subject, chapter and PDF path.
- Generate a manifest for all class 6-12 PDFs.
- Add real specialized layouts for:
  - compare/contrast
  - cause/effect
  - experiment
  - data/table
  - assertion/reason
  - definition
- Add browser tests for:
  - signup/login
  - drag/drop
  - swapped correct sentence is marked wrong
  - next question navigation
  - progress saving
- Add teacher/admin review workflow.
- Add import/export for generated chapter JSON.

## Later

- Move from local SQLite prototype to production database.
- Add roles: student, teacher, admin.
- Add classroom assignment flow.
- Add analytics dashboard.
- Add AI-assisted generation and review.
- Add class 6-12 batch generation.
- Add deployment pipeline.
