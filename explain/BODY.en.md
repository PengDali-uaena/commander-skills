# explain

Unpacks the previous reply, or expands only the item that was named. No re-investigation, no code changes.

- **A · Did not understand**: the previous reply was unclear and what is wanted is what it actually said. No new repo search.
- **B · Named expansion**: last turn was the summary layer and this turn names only one item of it (one sentence, one plan, one branch, one file). When the whole block should expand (all plans, all branches, the whole chain), this skill does not apply — go back to the original skill's full layer.

## What to read

Explain only the previous assistant reply, or the sentence the user quotes this turn. Paths, numbers and Tags that the previous reply did not contain are answered with "the previous reply did not give that"; do not go looking.

When there is nothing explainable:

```
- Original: the previous reply has no conclusion to expand
```

Then stop.

## A · Visible reply

When the user did not understand: one claim per group, following `commander`'s "field-block layout" — every line starts with `- `, the field name is bold, fields in a group are packed tight, like the four lines below. No code fence, no text outside the block. Named expansion does not use these four lines.

```
- **Original**: the sentence from the previous reply, verbatim
- **Meaning**: what that sentence says
- **Left out**: conditions, scope or exceptions that were not written; "none" when there are none
- **Therefore**: given what is known, what the next step is; "none" when there is none
```

If the user then wants the code path or wants logs: this turn only expands. `commander` routes the next turn.

When there is more than one claim group, expand only the most important one and write "N more" on one line; whatever the group count, the body stays ≤5 lines.

## B · Named expansion

Write only the named item and do not restate other items at the same level.

- You may read files the previous reply already mentioned (at most 3); start no new search and do not widen into other modules.
- When the previous reply did not give enough paths or numbers to support the detail, say what is missing and give one sentence on how to get it.
- Output at most 5 lines.
- If the user then wants to read the repo, add logs or change code: this turn only expands, and the next turn follows the routing table.
