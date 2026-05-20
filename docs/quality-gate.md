# Chapter Quality Gate

Use this checklist before moving a dataset from `generated` to `active`.

## Source Traceability

- `sourcePdf` points to the correct PDF.
- `sourceChapter` matches the chapter title.
- class, stream, subject, book and chapter number are correct.
- generated questions are based on chapter content, not another chapter.

## Answer Builder

- Every major chapter question has `easy`, `moderate` and `difficult` variants.
- Easy mode uses full sentences.
- Moderate mode uses half-sentences.
- Difficult mode uses phrases or key points.
- Easy and moderate order is exact.
- A correct sentence in the wrong placeholder is marked wrong.
- Distractors are plausible but clearly incorrect.

## Question Types

All 21 types should exist:

- Explain
- Compare/Contrast
- Cause/Effect
- Process/Sequence
- Pros/Cons
- Problem/Solution
- Fill Blanks
- True/False/Not Given
- Short Answer Key Points
- Match Following
- Data/Chart/Table
- Paragraph/Essay Structure
- Definition/Term
- Timeline/Chronological Order
- Main Idea
- Evidence/Support
- Sequencing Steps
- Correct Ending
- Multiple Correct Answers
- Formulate Question
- Assertion/Reason

## Layout Fit

- Sequence questions use ordered placeholders.
- Compare questions use two-column tables.
- Cause/effect questions use paired connections.
- Experiment questions use aim, observation and inference.
- Data/table questions use a data or inference layout.
- Assertion/reason questions check truth and relationship.

## Language And Scoring

- Language is age-appropriate for the class.
- Model answers are complete but not overlong.
- Hints support thinking without revealing the full answer.
- Rubrics match the marks.
- Feedback tells the student what to fix.

## Activation

Only after the checklist passes:

1. Add the dataset to `data/catalog/active-datasets.json`.
2. Run `python scripts/build_content_catalog.py`.
3. Run validation and smoke tests.
4. Confirm the dataset appears in the student Library.
