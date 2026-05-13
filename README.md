# Learnify Practice Data Pipeline

This workspace contains a pilot content pipeline for the Answer Writing Practice platform.

## Pilot Source

- Source folder: `D:\LX\all class pdf`
- Pilot PDF: `D:\LX\all class pdf\class 7\Science - Curiosity\gecu109.pdf`
- Chapter: Class 7 Science, Chapter 9, `Life Processes in Animals`

## Generate Pilot JSON

```powershell
python scripts/build_practice_data.py
```

Output:

```text
data/practice/class-7/science-curiosity/life-processes-in-animals.json
```

The generator extracts text from the PDF using PyMuPDF, falls back to pdfplumber if needed, and writes a frontend-ready JSON dataset.

## Validate JSON

```powershell
python scripts/validate_practice_json.py
```

The validator checks:

- required activity fields
- all 21 question types
- the 3 answer-builder modes: easy, moderate, difficult
- source traceability fields
- activity count consistency

## Included Practice Coverage

The pilot JSON includes:

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
