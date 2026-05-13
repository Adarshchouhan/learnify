# Learnify Chapter Practice Generation System

## Purpose

This document describes the repeatable system for turning any chapter PDF into app-ready practice data.

The goal is to generate:

- all major possible questions from inside the chapter
- textbook exercise questions
- three answer-builder modes for each question
- layout identifiers so the UI can choose the correct practice layout automatically
- correct answer chunks, distractors, sequence keys, hints and model answers

## Source Flow

1. Read the chapter PDF from `D:\LX\all class pdf`.
2. Extract text with PyMuPDF, with pdfplumber as fallback.
3. Identify chapter metadata:
   - class
   - stream, if any
   - subject
   - book
   - chapter number
   - chapter title
   - PDF path
4. Create a chapter question set:
   - major conceptual questions from inside the chapter
   - textbook exercise questions
   - important experiment, diagram, table or sequence questions
5. Generate activities for each question.

## Question Set Shape

Each question should be represented as:

```json
{
  "slug": "breathing-mechanism",
  "question": "Describe the mechanism of breathing in humans.",
  "structure": ["Inhalation", "Chest movement", "Diaphragm", "Exhalation"],
  "sentences": [
    "During inhalation, the ribs move up and outwards.",
    "The diaphragm moves downward and increases space inside the chest.",
    "Because of this, air enters the lungs."
  ],
  "wrong": [
    "During inhalation, the diaphragm moves upward first.",
    "Air enters the stomach during breathing."
  ]
}
```

## Three Difficulty Modes

Every answer-builder question should generate:

- `easy`: full sentence sequencing
- `moderate`: half-sentence sequencing
- `difficult`: phrase/key-point construction

For `easy` and `moderate`, order is strict.

A correct sentence in the wrong placeholder is wrong.

The answer is perfect only when:

- all required correct items are selected
- every item is in the exact matching slot
- no distractors are selected

## Question Identifier System

Each question receives a `questionIdentifier` object.

Example:

```json
{
  "layoutProfileId": "sequence",
  "layoutLabel": "Sequence Builder",
  "primaryPracticeType": "process_sequence",
  "slotStrategy": "ordered_placeholders",
  "recommendedLayout": "numbered vertical slots with exact-order validation"
}
```

The identifier tells the UI which layout to use.

## Layout Profiles

Current layout profiles:

- `sequence`: ordered placeholders for processes, pathways, timelines and journeys
- `explain`: structured answer with introduction, key points and conclusion
- `compare`: two-column compare/contrast table
- `cause_effect`: paired cause-effect connections with explanation
- `experiment`: aim, observation, reason and inference layout
- `data`: table/chart interpretation layout
- `definition`: term and definition-part builder
- `assertion_reason`: assertion, reason and relationship checker

## Identifier Heuristics

The generator currently identifies layouts using question wording and structure labels.

Examples:

- contains `journey`, `arrange`, `sequence`, `steps`, `pathway` -> `sequence`
- contains `compare`, `different`, `not the same` -> `compare`
- contains `why`, `reason`, `because` -> `cause_effect`
- contains `experiment`, `test`, `iodine`, `lime water`, `observation` -> `experiment`
- contains `percentage`, `table`, `data`, `chart` -> `data`
- contains `what is`, `define`, `meaning` -> `definition`
- contains `assertion`, `reason` -> `assertion_reason`
- fallback -> `explain`

## Adding a New Chapter

For a new chapter:

1. Add or generate a list of question sets.
2. Include both in-chapter major questions and textbook exercise questions.
3. Keep each model answer factual and age-appropriate.
4. Add plausible distractors based on common misconceptions.
5. Run:

```powershell
python scripts/build_practice_data.py
python scripts/validate_practice_json.py
```

6. Open the app and verify:
   - Next Question cycles through all chapter questions
   - Easy and Moderate require exact sequence
   - Correct/distractor colors reveal only after submission
   - Layout identifiers appear in the JSON for every generated question

## Current Pilot Coverage

Pilot chapter:

`Class 7 > Science - Curiosity > Chapter 9 - Life Processes in Animals`

Current coverage includes:

- 10 textbook exercise-style questions
- 10 major in-chapter conceptual questions
- 3 difficulty modes for each chapter question
- 21 additional interactive question-type examples
- layout identifiers for generated chapter questions
