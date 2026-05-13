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

## Future Layout Behavior

Use `questionIdentifier` to choose specialized layouts:

- `sequence`: numbered vertical placeholders
- `compare`: two-column compare table
- `cause_effect`: paired cause/effect builder
- `experiment`: aim, observation, reason and inference
- `data`: table/chart workspace
- `definition`: definition parts
- `assertion_reason`: assertion/reason truth and link checker
- `explain`: structured answer builder
