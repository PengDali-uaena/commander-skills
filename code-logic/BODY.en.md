# code-logic

Explains only how the code flows. No logs, no file edits.

If the user only asks for a file path and not the execution flow → this skill does not apply; `commander` picks **file-locate**.

If the user only asks whether it is the same component / same UI / same implementation and does not ask for entry points, mount chain, branches or flow → this skill does not apply; `commander` picks **reply-brief**.

## Reading the code

1. The user gave a path, class or function name: read only those plus one layer of direct callers and callees, at most 5 files.
2. No path given: at most 1 targeted search using keywords from the user's description, then read no more than 3 files. No repo-wide scanning.
3. If logs, a Tag or a filter are needed, this skill does not apply; `commander` switches to bugfix-probe. When the user names code-logic explicitly, still explain without changing anything.

## Depth

- **Summary layer (default)**: the first line is one bold conclusion — where it enters and what it finally produces; then 2–4 sentences on the main path, at most 6 lines for the turn, no per-API enumeration. Branches are summarized as "N gating/async points", not expanded one by one. The minimal path that supports the conclusion may be mentioned inline. If the question is answerable with a single yes/no, do not expand it into multiple scenarios or modules. At most one closing line: "Say the word and I will write the branches as entry / flow / key branch".
- **Full layer**: when the user asks to expand the code, expand the branches, or go finer, or when `commander`'s intent is the full layer, use "Visible reply · full layer" below.

## Visible reply · full layer

One field per line, following `commander`'s "field-block layout": every line starts with `- `, the field name is bold, and there is no blank line between fields. Write symbols and paths in full. Do not merge away gates or branches just to be shorter.

```
- **Entry**: who triggers it, where it enters
- **Flow**: steps chained with →
- **Key branch**: one gate, branch or async point
- **Key branch**: …
```

Write as many `- **Key branch**:` lines as there are branches — consecutive, no blank lines, no indentation. If the user asks "where does it break", add a final `- **Fragile**:` line.

No assumption table, no fix plan, no code blocks.

## Example (full-layer shape)

```
- **Entry**: open the live room → CommentList.refresh
- **Flow**: fetch blocklist → ready=true → filter the list by blocked
- **Key branch**: the list is cleared before ready
- **Key branch**: an unauthenticated user still triggers the request; if it fails, ready stays false
```
