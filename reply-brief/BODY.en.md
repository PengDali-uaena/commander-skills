# reply-brief

Turns an answer into text that can be read directly: settle the conclusion first, then drop what the reader does not need. Layout follows readability — a paragraph if one paragraph is enough, a list for parallel items, a table for comparisons or multi-column facts. No fixed field names.

If `{{SKILL_DIR}}learned.md` exists in this directory, read it first; preferences there that match this question override the defaults below.

This file only decides "what to say and how many sentences". Formatting hygiene — bold first line, one line per parallel item, no bare URLs or absolute paths — follows the AGENTS "visible reply" rules and pinned `commander` constraints; it is not restated here.

## Shared boundaries

- No fixed line prefixes such as "Conclusion:", "Basis:", "Boundary:"; no "does that meet your expectation?" at the end of each paragraph.
- Multiple questions in one message are answered in **asked order**, one sentence each, then one shared piece of evidence; do not reorder them by code structure.
- Paths, numbers, Tags and verbatim errors are written in full when they support the conclusion; process and file lists that do not support it are deleted.
- Do not search the repo, add logs or edit code on your own. If the user asks for a code change in the same message: finish the answer first, then edit.
- Reversing your own previous verdict follows `commander`'s "retract the old verdict" rule; do not restate it here.

## Root cause + fix suggestion (when the user names two columns)

When the user's message contains both "root cause" and "fix suggestion" (or synonyms such as "why + what to do") and does **not** ask for expansion, logs, filters, API verification or deploy steps:

- The visible reply is **exactly two lines** (or two one-sentence paragraphs), prefixed **"Root cause:"** and **"Fix:"** (use the user's labels if they gave any).
- The root cause sentence explains **why**; the fix sentence explains **the next step** (data / config / redeploy / who to ask), with no alternatives.
- **Forbidden**: tables, numbered lists, cURL, JSON field examples, DevTools self-checks, file paths, component mount chains — unless the user asks to expand next turn.

Repo reads and curl happen inside the tool steps; the conclusions are compressed into those two sentences, and the investigation process never appears in the visible reply.

## Did it ship / checking the last turn (default)

When the user asks "did you implement it", "didn't you say…", "did you force it in", i.e. checking an **earlier commitment** rather than asking for a new plan:

- **First sentence answers directly**: yes / no / only partially (pick the most accurate one).
- **Second sentence** states the condition or the gap in one sentence (e.g. "DEV only", "the API is missing a field").
- **Forbidden**: tables, changed-file lists, full URL parameter dumps, redeploy tutorials — unless the user asks.

## Is-it / same-thing questions (default)

When the user only asks "is it / are they the same / is it the same one / the same set" and does not ask for expansion, mount chain or flow:

- **First line answers yes or no** (or a direct conclusion such as "not exactly").
- Body is **1–3 sentences total**; evidence is at most **one** class name or **one** `A → B` reference chain.
- **Do not compare pages, modules or scenarios the user did not name** (e.g. if they only ask about detail vs checkout, do not expand into other entry points).
- At most one closing line: `For the mount/reference chain use code-logic, or ask me to expand.`

## Follow-up turns (from the 3rd turn on the same topic, or "just answer yes/no")

- Answer only the point asked; do not restate premises already explained.
- If the user says "just answer yes/no" → answer in asked order `1./2./3.` with `yes` / `no` / `yes, but…`, one per line, no explanation.

## Audit / inventory type

When the user asks "is this module reasonable / does it have defects / is all the data shown", with no diff and no report requested:

- First line gives the verdict (reasonable / N substantive defects / the conclusion does not hold); second line gives the one thing they should know first.
- At most 5 defects, one per line: location + symptom + consequence; beyond 5, keep the 5 worst and write "N more available on request".
- Body is at most 20 lines; no passing items, residual risks or fix lists unless the user asks for them.
- You may borrow a project review skill's checklist, but the output follows this section, not its template.
