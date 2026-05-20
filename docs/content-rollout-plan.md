# Content Rollout Plan

## Content States

Learnify content moves through four states:

- `scanned`: the PDF exists in the class 6-12 manifest, but no app-ready JSON has been generated.
- `generated`: JSON exists under `data/practice`, but it is not yet approved for students.
- `needs_revision`: a teacher/admin reviewed the content and found issues to fix.
- `active`: the dataset is approved and student-facing.
- `failed`: the source PDF could not be extracted and must be replaced or repaired.

Only `active` datasets should appear for normal student practice.

## Source Files

- PDF source root: `D:\LX\all class pdf`
- Manifest: `data/manifest/class-6-12-pdf-manifest.json`
- Generated JSON root: `data/practice`
- Active dataset list: `data/catalog/active-datasets.json`
- Full content catalog: `data/catalog/content-catalog.json`

## Current Catalog Status

- Manifest entries: 1,434
- Generated datasets: 1,441
- Active datasets: 1
- Draft generated datasets: 1,440
- Failed/scanned datasets: 0
- Fixed source issue: replaced corrupted Class 12 Chemistry `lech102.pdf` from the official NCERT PDF URL and regenerated its JSON.

## Rollout Commands

1. Scan PDFs:

```powershell
python scripts/build_pdf_manifest.py
```

2. Build the current catalog:

```powershell
python scripts/build_content_catalog.py
```

3. Generate a tiny batch for review:

```powershell
python scripts/batch_generate_practice_data.py --dry-run --limit 5
python scripts/batch_generate_practice_data.py --limit 5
```

Resume without recreating existing JSON:

```powershell
python scripts/batch_generate_practice_data.py --limit 0 --skip-existing
```

4. Validate generated JSON:

```powershell
python scripts/validate_practice_json.py path\to\chapter.json
python scripts/validate_all_practice_json.py
```

5. Review in the app as teacher/admin.

6. Add approved datasets to `data/catalog/active-datasets.json`.

Or use:

```powershell
python scripts/activate_dataset.py data/practice/class-7/science-curiosity/chapter-1.json --approved-by "teacher-name"
```

7. Rebuild the catalog:

```powershell
python scripts/build_content_catalog.py
python scripts/content_status.py
```

## Safe Batch Order

Recommended first rollout:

1. Class 7 Science pilot, already active.
2. Review generated Class 6-8 core chapters and activate approved datasets.
3. Review generated Class 9-10 core subjects.
4. Review generated Class 11-12 stream-specific books.
5. Replace or repair any future `failed` PDF sources before activation.

## Important Constraint

The current generator can write datasets for any manifest entry, but chapter-specific factual quality still depends on reviewed question sets. Do not run `--limit 0` and mark everything active until the chapter-specific generation quality gate is passed.
