# tracking-doc-format

Turns a downloaded analytics-events document (`.csv`) into readable text segmented by event key. Format normalization only: never rename an event, never add a parameter, never infer a timing or description that is not written.

If `{{SKILL_DIR}}learned.md` exists in this directory, read it first; its **layout** preferences (bold, indentation, blank lines, divider position, no color and similar details) override the defaults below, but they **must not override the step order or the default mode** — the decision between checking one event at a time and printing the whole document belongs to steps 6 and 7 alone.

Boundaries of `learned.md` (judge before writing any file):

- **Layout only**. Process lines — output path, one-at-a-time vs whole document, whether to write a file — follow this file; ignore any such sentence in `learned.md`, and add one line at the end of this turn's reply: "the process lines in learned.md are void".
- **Conclusions expire**: anchors recorded in `learned.md` (which field, which line) are hints only; re-check with `rg` every turn. When they conflict with this turn's confirmed conclusion, this turn wins, and fix that line in `learned.md` on the spot instead of leaving two versions.
- Each side has its own `learned.md`; `dist.mjs` neither generates nor validates it. Never copy the event list or the parameter table into it (it would fork from the written document).

## Trigger

The user gives an events `.csv` path or pastes the CSV content and asks to "tidy / format / split by key / show it like this". When the user pastes a sample format, the sample wins and this file only fills the defaults.

Also used for the after-development pass: when the events are implemented and the user wants to check "are all events implemented / are the params right / anything missing", use "Implementation check" below and do not re-output the event table.

## Called by prd-to-task (linked mode)

When prd-to-task writes the `### Events` section it uses this skill's layout and one-at-a-time checking, but **the output lands in the task document**:

- Output goes into the task document's `### Events` section; do not write `docs/tracking-<date>-<feature>.md`, and do not print the full text in the conversation — the conversation carries only the current event plus the task document path.
- Checking one at a time is unchanged: one event, wait for confirmation, then the next; after all are done the full text is still not printed separately (the full text is that section of the task document).
- Each event gains one extra line `- **Report point**: <file:line>` or `to be added (<feature point / entry>)`; the report point must exist in prd-to-task's change-boundary table, otherwise record it as undecided.
- Layout, bold, value provenance and counter-examples are all unchanged.
- When the user says "the events should be their own document", leave linked mode and write the file per "Output location" below.

## Steps

1. **Get the data**: `read` the csv the user gave (do not `cat` the whole thing into the reply). When the user pastes content, parse what was pasted.
   - Non-csv forms: for `.xlsx` ask for a csv export first; for online sheets (Google Sheet / Lark) ask for an export or a paste; tables inside PDFs or screenshots are not accepted as the sole source — parse only the readable rows and note on the first line of the reply "source is not csv; columns or merged cells may be lost, please check".
   - Merged cells, event names spanning rows, one sheet holding several tables separated by blank rows: apply fill-down by column position; when the same event appears in two tables of one document, concatenate in order of appearance and do not merge the segments.
2. **Segment**: events documents usually put one event across several rows, with the name and timing only on the first row and parameters below.
   - Non-empty event-name column → start a new segment; empty → a parameter row of the previous segment (fill down).
   - Several consecutive rows with the same event name → merge into one segment.
   - One event per row with parameters crammed into a cell (separated by newlines / `;` / `,`) → split into parameter rows by the separator first.
3. **Identify columns** (by header keyword; first hit wins):

   | Purpose | Header keywords |
   |---|---|
   | Event name | 埋点名, 事件名, 事件, event, event_name, 埋点key, key |
   | Report timing | 上报时机, 触发时机, 触发条件, 上报说明, 场景, 时机 |
   | Param name | 参数名, 参数, 字段, param, 属性 |
   | Type | 类型, 参数类型, 数据类型, type |
   | Description | 说明, 描述, 含义, 备注, desc |

   **Typical product sheet (Event Track - By Version)**: `场景` is mostly a section title or a human label and is not the event key; `事件(Event)` → event name; `参数(Parameter)` → param name; `取值(Value)` is often the type or type+constraint (merge into type / description, do not treat it as value provenance); `备注(Remarks)` → description, and the first parameter row often carries the timing verbatim. When that sheet has no separate timing column, take it from the first parameter's remark; if still empty write `Timing: not specified`.

   When headers do not match, fall back to column order (column 1 event name, column 2 timing, …), note "identified by column order" on the first line of the reply and ask the user to confirm. Columns that cannot be identified are dropped.

4. **Clean**: trim whitespace; join in-cell newlines into one sentence; keep `string` / `int` / `bool` / `json` / `string[]` verbatim, and append "type." after them uniformly (do not repeat when the source already says "string type").
5. **Value provenance (mandatory unless the user only wants formatting)**: every parameter must answer "where does the value come from", not just type and description.
   - Search the engine for the event key first (`rg -n "<event_key>" lib`). If a report point is found → read the arguments of that call, write the field or expression verbatim as the value, with `file:line`.
   - No report point found (not implemented yet) → read the feature's data model and components and give fields usable as-is today; when no field matches, say "needs backend delivery" instead of substituting an approximate field.
   - When unsure write `Value: not found` or `to implement (candidate X)`; inventing field names is forbidden.
   - **Report point is mandatory**: every event segment gets one `- **Report point**: <file:line>` line; when unimplemented write `to be added (<feature point / entry>)`, and `to implement` when even the entry is unknown. An implemented event without a report point counts as unchecked.
   - **Parameter cap check**: when the source or document mentions Firebase's 25-parameter cap, or the event already has a real report point, add up "existing parameters of that event + newly added"; when the total exceeds 25, write at the end of that segment `params: <existing a> + <new b> = <total>, over the cap, must merge or drop` and call it out on the first line of the reply instead of skipping it silently.
6. **Check one at a time (default, not skippable)**: following "Layout" below, **output only one event at a time** and wait for the user's confirmation before the next; **never** send two in one message and **never** dump the whole document. `learned.md` cannot override this step: even when it records "give the whole document at once", that only applies when the user explicitly asks for the whole document this turn.
   - Open with one line of progress and state, not just an index: `N events total, 3/N | confirmed 2, skipped 1 (pdp_video_watch_end), undecided 0`.
   - "right / ok / continue / next" → next event; the user points out an error → **re-output only that event**, never the already-confirmed ones.
   - "skip / skip this one for now" → record it in the skip list, **output the next event right away**, and list skips in every later progress line; a skip must never drop the item from the list. After the full pass, ask once: "want the N skipped ones too?"
   - A change of definition (drop a parameter / change a value / change timing) → re-output only that event, leaving confirmed segments alone; when the same item is changed repeatedly, the **last explicit statement** wins and the check record gets `<old> → <new>`.
   - Continuing across sessions: when the document was written, read its trailing "Check record" table first and resume from the first row that is not `confirmed`; when it was not written, use the last progress line, never restart from the top.
   - **Stop** after writing the current event and hand confirmation back to the user.
7. **Full document**: only after every event is confirmed, output the whole thing once in the layout; segments are separated by one `-----------` with **one blank line above and below** (two newlines). The per-event stage adds **no** divider — `-----------` appears only in the full document. The full text always ends with the "Check record" and "Definition changes" sections (below), which are also the entry point for the later implementation check.

## Layout

Each logical block **occupies its own line**; blocks are **separated by a blank line**. Never cram several segments into one paragraph.

**Bold is mandatory**: the event name, `**Report timing:**`, `**Params:**` and every `**param-name**` must use paired `**` (ASCII). Never use single backticks (`pdp_xxx`) in place of a heading or parameter name. This skill is **not** bound by the User Rules limit of "≤5 bold spots".

**Divider**: appears only in the **full document** — after a segment the next line must be nothing but `-----------`, with a blank line above and below, never omitted; **the per-event stage carries no divider**.

**Indentation (Cursor conversations need lists, otherwise levels disappear)**: under `**Params:**` every parameter takes two list items —

```
**show_card** (card impression)

**Report timing:** reported when the card becomes visible; not repeated within one page; a page refresh resets the logic

**Params:**

- **module_name**: string type. Use the title the backend delivers for the current card

  - Value: product.title (product_detail_v3_model.dart:134)

- **rank**: int type. Current position, starting at 1.

  - Value: _photoIndex + 2 (pdp_video_header.dart:737)

- **Report point**: pdp_video_header.dart:737; when unimplemented write to be added (F1 walkthrough video impression entry)

-----------

(next segment in the full document…)
```

- Lists: parameter rows use `- **name**: type. description`; value rows use one extra space, `  - Value: …` (2 spaces + `-`), **on their own line**, formatted `Value: <expression> (<file>:<line>)`; several sources are joined with ` / `.
- Each segment ends with `- **Report point**: <file:line>` or `- **Report point**: to be added (<feature point / entry>)`, at the same level as parameter rows and not indented.
- Never use plain-space indentation instead of a list (Cursor conversations usually swallow space indentation).
- When the description is missing write only the type and leave no empty colon; when the timing is empty write `Timing: not specified`.
- Keep parameter and event order as in the source: no sorting, no deduplicating same-name different-meaning parameters.

## Check record and definition changes (two fixed sections)

The full document always ends with two sections, not included in the per-event stage; once written they are the only entry point for cross-session continuation and the implementation check.

```
## Check record
| # | Event | Status | Turn | User's confirmation |
| 1 | pdp_video_exp | confirmed | 3 | "the rest is fine, next" |
| 2 | pdp_video_watch_end | skipped | 4 | "skip that too" |
| 3 | pdp_video_load_result | undecided | 6 | "waiting on the backend enum" |

## Definition changes
- <event>: <old definition> → <new definition> (turn N)
```

- Status is only `confirmed` / `skipped` / `undecided`; a changed item is recorded as `undecided` first and becomes `confirmed` only when the user confirms again.
- Update both sections right after each confirmation (reflect it in the progress line when nothing is written yet); never batch them to the end.

## Emphasis (no color)

Neither terminals nor chat channels color text (a bare ANSI ESC is stripped, an HTML span shows as literal text), so the whole document uses bold alone for hierarchy: no color, no span, no ANSI.

- Event name: bold, on its own line
- "Report timing:" and "Params:": bold the label itself
- Parameter name: bold

The written `.md` and the chat body use the **same** plain-bold Markdown, with no HTML.

## Counter-examples (forbidden)

The following is **wrong output** and must not appear:

- A whole line holding only `` `pdp_video_watch_end` `` or `pdp_video_watch_end` without `**pdp_video_watch_end**`
- `Report timing:`, `Params:`, `product_id:` not bold, or mashed into the same paragraph as the description
- No `-----------` between segments
- Backticks used to highlight a parameter name instead of `**product_id**`
- Value crammed onto the parameter line with no `  - Value:` sub-item

## Check before sending (run it in your head before writing the body)

1. Is every event name `**event_key**` (a trailing note in parentheses is fine)?
2. Is there a `-----------` between every two segments, with blank lines above and below?
3. Does every parameter have both a `- **param**:` line and a `  - Value:` line?
4. Does every segment have a `- **Report point**:` line?
5. Is the full text free of code fences?
6. In the per-event stage, is there **only** the current event and does it end waiting for confirmation (no next event dragged in, no early full document)?
7. Does the progress line carry confirmed / skipped / undecided counts, with skipped items named by key?
8. Any color, span, ANSI, or single backtick used as a heading?

## Implementation check (when the user says it is implemented / asks for a review)

When the user asks "are all events implemented / anything missing / any other bugs", do not re-output the event table; check the code instead:

1. **Build the table**: one row per event from the written document's list — never infer the list from the report points that exist in code (that would miss unimplemented events).
2. **Compare four things per row**: does the report point exist (`rg`); are all parameters present with matching types; is the value expression the one the document states; does the timing (first time / every switch / on exit / deduplicated) match.
3. **Numbered output**: `W-001` (would mis-report or drop reports) / `I-001` (inconsistent or to confirm). One line each: symptom + `file:line` + what the document requires; hand over the numbered list and let the user pick — never fix them yourself.
4. **Conflict call**: when code and document disagree, first decide whether the implementation or the document is right; if the document is wrong, write the correction back on the spot (into "Definition changes") and only list W for implementation errors.
5. **Write back**: after checking, fill the implemented report points into the document's `**Report point**` lines (`to implement` → `file:line`), mark those events `confirmed` in the check record, and list the unimplemented ones under "Implementation to add".

## Do not

- Never change an event's spelling, merge two events, or add a parameter the source lacks.
- Never translate descriptions (keep Chinese as Chinese, Indonesian and English likewise).
- Never rewrite a parameter type into a code type (`int type` never becomes `int`), unless the source has only the type with no "type" word and the user asks to keep it verbatim.
- No analysis, no suggestions, no sorting, no sub-headings between segments.
- Never invent a value: a parameter with no code evidence can only be `Value: not found / to implement`; substituting a same-name or approximate field is forbidden.
- **Never** wrap the whole document or a whole segment in a code fence (``` ) — it breaks Markdown rendering in the conversation.

## Visible reply

This skill's **segmented body** is not bound by commander's "≤8 lines" or "≤5 bold spots" (same category as prd-to-task's field blocks), but it still obeys the **blank lines and indentation** of the layout.

- **First line**: one sentence of result (segment count; mention column-order fallback or missing timing if any), then the progress line `N events total, i/N | confirmed a, skipped b (<key>), undecided c`.
- **Per-event stage**: the body holds **only the current event**, written out per the layout; stop there and ask "is this right / next one?". Never preview later segments, never summarize, never say "the full text is somewhere else".
- **Full-document stage**: only after everything is confirmed, print the **full text** in the conversation (including the "Check record" and "Definition changes" sections), `-----------` between segments, no truncation, no skipped segments; then ask "write it to `docs/tracking-<date>-<feature>.md`?" and write the file only after the user clearly agrees in the next message or names the file (path under "Output location"). Never write the file unasked this turn.
- Skip the per-event stage only when the user explicitly says "just give me the whole thing / all at once / no need to check one by one".
- **Implementation-check turn**: do not re-output the event table; give the numbered W/I list first (at most 5 items plus a total count, each with `file:line`) and wait for the user to pick.

## Output location

1. **Default**: print the full text in the conversation first (so the user can review and comment in this session); do not write a file.
2. **Written path (fixed)**: when the user explicitly says "write it as a doc / save it / export it / to markdown / confirm save / write to file", write `docs/tracking-<date>-<feature>.md` in the current repo:
   - Structure: title + source and timestamp + event segments (`-----------` between them) + "Check record" + "Definition changes".
   - When a file of that name exists, read its old "Check record" first, change only the differing segments and add definition changes; never rewrite the whole file, never drop the source of an old conclusion.
   - `<date>` is `YYYYMMDD` (e.g. `20261113`); `<feature>` is a short English kebab-case name (e.g. `pdp-video-perf`).
   - Create `docs/` when the project has none; if cwd is not inside a repo, ask which repo it should land in.
   - The old rule of "`<original-name>-format.md` next to the csv" is no longer used.
3. When the user explicitly says "do not write files / conversation only", nothing is written this turn or later in the same task.
