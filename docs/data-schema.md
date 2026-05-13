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
```

Current validator checks:

- required root fields
- required activity fields
- 21 core question types
- 3 answer-builder modes
- source traceability
- activity count consistency
