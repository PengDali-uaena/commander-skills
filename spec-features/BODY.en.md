# spec-features

Compresses the background the user gives (what they want, why, where they fear it will break) into **change items that can be executed one by one**. The user checks this list first, then decides whether the AI may start.

**Use only when the user explicitly says `spec-features` or names it**: it does not enter `commander`'s artifact table, does not auto-route, and hands off to no other skill.

## What it does not do

- No repo reads, no file lookups, no code changes, no logs, no file writes.
- No feasibility judgment, no comparison of approaches, no implementation steps.
- Never invent a feature that is not in the background; inferred items are listed separately and marked `(inferred)`.

## Execution

1. **Align**: restate the goal in one sentence (≤40 characters). If the intent is clearly off, point it out first.
2. **Split**: output only the list of change items, one item per line.
3. **Close**: one line, "implement from this list?", and no summary paragraph.

## How to write an item

One item per line, starting with `-`, stating only **what to do**; no file to touch, no definition of done.

- Each item ≤150 characters (Chinese counts characters including punctuation); if it does not fit, split into two items instead of compressing.
- One item does one thing; when "and / also" appears, consider splitting.
- Start with a verb: add / change / remove / adjust / restrict / support, so the user can see it changes behavior.
- Keep the nouns from the user's own words (feature name, page name, field name); never rewrite them into synonyms.
- No landing-free phrases such as "improve the experience", "boost performance", "smoother".
- Ordering: high-risk items that change existing behavior first, pure additions after, related items adjacent.

## To confirm

Contradictions, ambiguous referents and missing boundary conditions from the background go after the list, starting one line with "To confirm:" — at most 5, each one question. Omit the section when there are none.

## Visible reply

- No headings, no "Conclusion:"; fixed order: alignment sentence → list → to confirm → confirmation question.
- No verification checklist, no implementation details such as naming, constants or comments.
- No cap on item count; if the background supports only 3 items, write 1–2 instead of padding.
