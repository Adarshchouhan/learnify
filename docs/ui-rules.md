# Learnify UI Rules

## Visual Direction

The app uses a clean SaaS learning-product style:

- white panels
- soft borders
- purple primary actions
- compact left sidebar
- clear active navigation state
- question hero banner
- structured builder workspace
- right-side option bank

The UI references the uploaded images for layout direction, but it should remain original.

## Landing Page

The landing page must immediately explain:

- this is an answer-writing practice platform
- it supports Class 6-12
- students build answers through structured practice
- signup/login is available

Landing sections:

- hero
- features
- question formats
- SaaS/security foundation
- auth form

## Dashboard

Dashboard sections:

- Practice
- Question Types
- Progress
- Library
- Review, only for teacher/admin users

Sidebar includes:

- brand
- nav
- daily goal/progress card
- user profile card
- logout action

## Practice UI

The practice page includes:

- question hero
- marks card
- difficulty tabs
- builder panel
- answer placeholders
- option bank
- hint/clear/check actions
- previous/next question controls
- feedback panel
- question-type preview grid

## Correctness Reveal Rule

Before submission:

- options must look neutral
- do not show green/red correctness
- do not show correct/distractor labels as answers

After submission:

- correct item in correct placeholder becomes green
- distractor becomes red
- correct item in wrong placeholder becomes red
- feedback explains exact slot-order score

## Sequence Rule

For full sentences and half-sentences:

- sequence is strict
- placeholder order matters
- swapping two correct sentences makes the answer wrong

## Specialized Layout Behavior

Use `questionIdentifier` to choose specialized layouts:

- `sequence`: numbered vertical placeholders
- `compare`: two-column compare table
- `cause_effect`: paired cause/effect builder
- `experiment`: aim, observation, reason and inference
- `data`: table/chart workspace
- `definition`: definition parts
- `assertion_reason`: assertion/reason truth and link checker
- `explain`: structured answer builder

Current implemented detail renderers:

- compare/contrast cards use two columns
- cause/effect cards use paired rows
- process/timeline cards use ordered sequence blocks
- assertion/reason cards use assertion, reason and option panels
- data/table cards use an inference table
- other formats fall back to a generic correct/distractor layout
- all standard type detail views include click-to-place slots and a format checker

## Review UI

Teacher/admin review should be compact and fast:

- show activity type, question and status control
- save review status through the protected API
- support `draft`, `approved`, `needs_revision` and `rejected`
- do not expose review navigation to student users

## Teacher UI

Teacher/admin users can:

- review generated activities
- create an assignment from the current dataset
- set a due date
- view aggregate attempt analytics

These controls should remain compact and work-focused.

## Student Assignments

Students can:

- open the Assignments view
- see class-level assignments
- view teacher name and due date
- launch the assigned dataset into Practice
