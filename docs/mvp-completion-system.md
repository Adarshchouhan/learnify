# Learnify MVP Completion System

## Seven Workstreams

1. Generalized content generation
2. Specialized question layouts
3. Admin/teacher review
4. Student product flow
5. Production-ready storage foundation
6. Testing and validation
7. Scale content pipeline

## Implemented In This Pass

### 1. Generalized Content Generation

- `scripts/build_practice_data.py` accepts chapter metadata arguments.
- Default behavior still regenerates the Class 7 Science pilot.
- Output paths are deterministic from class, stream, book and chapter.

### 2. Specialized Question Layouts

- The question-type library now opens a detail renderer.
- Implemented layouts cover compare/contrast, cause/effect, sequence/timeline, assertion/reason and data/table.
- Standard question types now include a click-to-place checker.
- Remaining full custom surfaces can still be deepened by type, but all standard formats now have an interactive validation path.

### 3. Admin/Teacher Review

- Users have roles: `student`, `teacher`, `admin`.
- The first account in a fresh database becomes `admin`.
- Teacher/admin users can review generated activities from the Review view.
- Review statuses are saved as `draft`, `approved`, `needs_revision` or `rejected`.

### 4. Student Product Flow

- Students can switch generated datasets from the Library view.
- Practice data loads through `/api/practice-data?dataset=...`.
- Progress saving remains tied to authenticated users and CSRF protection.
- Students see active datasets by default; teacher/admin users can inspect all generated/scanned datasets.

### 5. Production Storage Foundation

- SQLite now includes content review and dataset registry tables.
- The server performs lightweight column migration for user roles.
- Dataset discovery reads generated JSON and the manifest.

### 6. Testing And Validation

- `scripts/validate_practice_json.py` validates the generated practice JSON.
- `scripts/validate_all_practice_json.py` validates every JSON dataset under `data/practice`.
- `scripts/smoke_test.py` starts the server, signs up a user, loads practice data, writes progress and verifies progress retrieval.

### 7. Scale Content Pipeline

- `scripts/build_pdf_manifest.py` scans `D:\LX\all class pdf`.
- The current local manifest contains 1,434 class 6-12 PDF entries.
- `scripts/batch_generate_practice_data.py` runs controlled generation batches from the manifest.
- `scripts/build_content_catalog.py` separates scanned, generated and active content.
- `scripts/activate_dataset.py` promotes reviewed generated datasets to active.
- `scripts/content_status.py` reports rollout status by class, subject and status.
- All currently indexed class 6-12 manifest entries have generated draft datasets.
- The previously corrupted Class 12 Chemistry `lech102.pdf` source was replaced from NCERT and regenerated.

### Classroom And Analytics

- Teacher/admin users can create assignments for the current dataset.
- Teacher/admin users can see aggregate attempt analytics by activity type and difficulty.
- Students have an assignment inbox and can launch assigned datasets.
- Teacher assignments support due dates.

## Commands

```powershell
python scripts/build_practice_data.py
python scripts/build_pdf_manifest.py
python scripts/build_content_catalog.py
python scripts/validate_practice_json.py
python scripts/validate_all_practice_json.py
python scripts/smoke_test.py
```

## Next Quality Gate

Before activating generated chapters, review them in the teacher/admin Review view and approve factual quality, JSON shape, layout behavior and scoring rules.

Use `docs/content-rollout-plan.md` and `docs/quality-gate.md` for every new chapter batch.
