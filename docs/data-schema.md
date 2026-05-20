# Practice Data Schema Notes

## Dataset Location

Current pilot JSON:

```text
data/practice/class-7/science-curiosity/life-processes-in-animals.json
```

Schema reference:

```text
schema/practice-activity.schema.json
```

## Root Fields

The dataset includes:

- `version`
- `generatedBy`
- `source`
- `coverage`
- `layoutProfiles`
- `chapterQuestions`
- `activities`

## Activity Fields

Each activity includes:

- `id`
- `type`
- `difficulty`
- `classLevel`
- `stream`
- `subject`
- `book`
- `chapter`
- `chapterNumber`
- `marks`
- `question`
- `instructions`
- `structureHelp`
- `sourceTextSummary`
- `sourceChapter`
- `sourcePdf`
- `correctItems`
- `distractors`
- `answerSlots`
- `answerKey`
- `correctSequence`, where applicable
- `hints`
- `modelAnswer`
- `scoringRubric`

Generated chapter answer-builder activities also include:

- `questionGroupId`
- `chapterQuestionNumber`
- `questionIdentifier`

## Question Identifier

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

The frontend can use this object to choose the best layout for a question.

## Exact Sequence Rule

For `easy` and `moderate`:

- `answerKey.orderedItemIds` is the source of truth
- slot index must match item index
- correct item in wrong slot is wrong

For `difficult`:

- `answerKey.requiredConceptIds` is the source of truth
- order can be looser because the student builds a phrase-based answer

## Validation

Run:

```powershell
python scripts/validate_practice_json.py
python scripts/validate_all_practice_json.py
```

Current validator checks:

- required root fields
- required activity fields
- 21 core question types
- 3 answer-builder modes
- source traceability
- activity count consistency

## Dataset Manifest

The class 6-12 manifest is written to:

```text
data/manifest/class-6-12-pdf-manifest.json
```

Each manifest entry includes:

- `id`
- `classLevel`
- `stream`
- `subject`
- `book`
- `chapter`
- `chapterNumber`
- `pdfPath`
- `relativePath`
- `outputPath`

The server exposes generated datasets through:

```text
GET /api/datasets
GET /api/practice-data?dataset=<id-or-jsonPath>
```

## Content Catalog

The catalog is written to:

```text
data/catalog/content-catalog.json
```

It is built from:

- `data/manifest/class-6-12-pdf-manifest.json`
- generated JSON files under `data/practice`
- active approvals in `data/catalog/active-datasets.json`

Dataset statuses:

- `scanned`: PDF indexed, no JSON yet
- `generated`: JSON exists but is not student-facing
- `needs_revision`: review found issues
- `active`: approved and student-facing
- `failed`: source PDF extraction failed and the PDF must be repaired/replaced

Student dataset discovery returns active datasets by default.
Teacher/admin discovery can request the full catalog with:

```text
GET /api/datasets?includeAll=1
```
