# Learnify Practice Data Pipeline

This workspace contains the Learnify answer-writing practice platform and the class 6-12 content pipeline.

## Source Coverage

- Source folder: `D:\LX\all class pdf`
- Pilot PDF: `D:\LX\all class pdf\class 7\Science - Curiosity\gecu109.pdf`
- Chapter: Class 7 Science, Chapter 9, `Life Processes in Animals`
- Manifest entries indexed: 1,434
- Generated practice JSON datasets: 1,441
- Active student-facing datasets: 1

## Generate Pilot JSON

```powershell
python scripts/build_practice_data.py
```

Output:

```text
data/practice/class-7/science-curiosity/life-processes-in-animals.json
```

The generator extracts text from the PDF using PyMuPDF, falls back to pdfplumber if needed, and writes a frontend-ready JSON dataset.

You can also pass explicit metadata:

```powershell
python scripts/build_practice_data.py --pdf "D:\LX\all class pdf\class 7\Science - Curiosity\gecu109.pdf" --class-level 7 --subject "Science" --book "Science - Curiosity" --chapter "Life Processes in Animals" --chapter-number 9
```

## Scale Manifest

Scan the class 6-12 PDF folder:

```powershell
python scripts/build_pdf_manifest.py
```

Generate from the manifest in controlled batches:

```powershell
python scripts/batch_generate_practice_data.py --limit 1
```

Use `--dry-run` before large batches.

Resume without recreating existing JSON:

```powershell
python scripts/batch_generate_practice_data.py --limit 0 --skip-existing
```

## Validate JSON

```powershell
python scripts/validate_practice_json.py
python scripts/validate_all_practice_json.py
```

The validator checks:

- required activity fields
- all 21 question types
- the 3 answer-builder modes: easy, moderate, difficult
- source traceability fields
- activity count consistency

## Included Practice Coverage

The pilot JSON and generated class 6-12 drafts include:

- 21 interactive question-builder activity types
- 3 answer-builder mode variants
- major in-chapter questions and textbook exercise questions
- question identifiers that map each question to a recommended UI layout
- correct answer chunks
- distractors
- answer slots
- hints
- model answers
- scoring rubrics

## Repeatable Chapter System

See:

```text
docs/chapter-practice-generation-system.md
```

This document explains how to follow the same system for every chapter, including question-set shape, layout identifiers, exact sequence validation, and the reusable layout profile rules.

## Run The App

```powershell
python server.py
```

Open:

```text
http://127.0.0.1:5173
```

## Smoke Test

```powershell
python scripts/smoke_test.py
```
