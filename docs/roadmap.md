# Learnify Roadmap

## Completed

- Local Python server
- Landing page
- Signup/login
- SQLite user/session/progress/review storage
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
- CLI generation arguments for class, subject, chapter, PDF and output path
- Class 6-12 PDF manifest scanner
- Manifest batch generation runner
- Dataset discovery API and library switching
- Active dataset catalog so scanned/generated content is not automatically live
- Specialized question type detail layouts
- Student/teacher/admin role support
- Teacher/admin activity review API and UI
- Teacher assignment creation
- Teacher aggregate analytics
- Student assignment inbox and due-date tracking
- Class 6-12 draft dataset generation
- All 1,441 generated practice JSON datasets validated
- Corrupted Class 12 Chemistry `lech102.pdf` replaced from NCERT and regenerated
- Local server smoke test

## Next

- Add browser tests for:
  - drag/drop
  - swapped correct sentence is marked wrong
  - next question navigation
- Review and enrich chapter-specific question sets before activation.
- Activate approved generated chapters in batches.
- Add import/export for generated chapter JSON.
- Add teacher analytics for reviewed/approved content quality.

## Later

- Move from local SQLite prototype to production database.
- Add class groups and full classroom assignment flow.
- Add deeper analytics dashboard.
- Add AI-assisted generation and review.
- Add deployment pipeline.
