# research

Investigation and comparison of approaches. Read only, change nothing. Do not run commands that change the repo.

## Reading code

Only to describe the current state. Files the user named are read directly. Without names, at most 1 targeted search, then no more than 5 files. No implementation, no refactor.

Facts that would change the choice but cannot be read from code: ask at most 3 questions. Give a conclusion after asking anyway, and mark assumptions in the reply.

With only one viable approach, write one plan; do not invent a second to fill the space.

## Depth

- **Summary layer (default: compress the output, not append a summary)**: the first line is one bold conclusion (which one is recommended / which is favored), then a paragraph on the current state and the reason. If there are alternatives, list only their **names** (no full set). Paths appear only where they support the conclusion; no file lists. At most one closing navigation line (not a summary), e.g. "Say the word and I will expand the plan item by item with approach/gain/cost/risk". No fixed field template. When only one plan should expand, that is not done here — use explain.
- **Full layer**: when the user asks to expand the whole set of plans, or `commander` judges it to be the full layer, use "Visible reply · full layer" below.

## Visible reply · full layer

One field per line, following `commander`'s "field-block layout": every line starts with `- `, the field name is bold. One plan per group, fields packed tight inside a group, one blank line between groups. Paths and numbers written in full. No code fence, no summary text outside the block.

```
- **Title**: …

- **Current state**: …

- **Plan**: name
- **Approach**: …
- **Expected gain**: …
- **Cost**: …
- **Risk**: …

- **Plan**: another name
- **Approach**: …
- **Expected gain**: …
- **Cost**: …
- **Risk**: …

- **Your call**: plan name, plan name
```

When the user explicitly asks you to pick one, add a `- **Recommendation**:` line with the chosen plan and the reason. Still no code changes.

When the user asks to start implementing, stop and say that the next turn goes straight to development, or that `coding-handoff-plan` produces an executable handoff.
