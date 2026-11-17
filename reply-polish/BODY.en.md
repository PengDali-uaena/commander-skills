# reply-polish

Formatting close-out layer. The default close-out already lives in `commander`'s hard rules 5 and 6 and in `AGENTS.md` "visible reply"; this file is used only when the user names it or says "clean up the format / the output is a mess / too long, no point". This layer picks no artifact, reads no repo and changes no verdict — it only touches structure, length and how references are written.

## Relationship with downstream skills

1. Artifacts and conclusions follow the selected skill; this layer changes presentation only, and never a verdict on conflict.
2. Hard-coded downstream layouts win: "exactly two lines", "field block, one field per line", "bugfix-probe must keep Tags and filter expressions" stay as they are — this layer does not merge fields, delete verbatim text or break a line cap.
3. This layer adds only three things: an overall verdict on the first line, parallel items split into lines, and quieter references and emphasis. The result must still fit the downstream length budget.
4. When the downstream output is already fine, do not rewrite it; only check for gaps.

## 1. Overall verdict (summary statements)

- The first line is one bold verdict; reading that line alone gives the conclusion — no background, no process, no "first I looked at".
- That sentence covers the whole message, not just the first paragraph.
- Each point's first sentence is its own conclusion; the first line does not stand in for them.
- A long reply (≥3 points or over 10 lines) may end with **one line** of "so / next"; do not restate points already made and do not add a summary paragraph.
- Field-block replies get no opening line outside the block; the verdict lives in the first field.

## 2. Splitting points (parallel items must be one per line)

Trigger: ≥2 causes, ≥2 plans, ≥2 steps, ≥2 locations or files, ≥2 todos, ≥2 defects.

- One per line, shaped `- **Point's verdict**: one-sentence explanation`; the first sentence is the point's answer, the reason or approach comes after.
- When the detail is long, indent the explanation on its own line; never squeeze two things into one line, and never collapse back into a wall of text.
- A single item stays a paragraph; do not force a list for looks. When item lengths differ wildly, merge the same-kind items first.
- After splitting, use one bullet style at a given level (`-` or `1.`), never mixed.

## 3. Quieter references (no bare URLs)

- Local files use inline code with a relative path, e.g. `lib/features/checkout/x.dart:42`; never `file:///`, never `~/`, never a full absolute path.
- The same path appears once per reply; later refer to it as "that file" or "the service above".
- Commit, PR, issue, doc: give the shortest locatable identifier (short SHA, number, module name). Give the full URL only when the user will copy it elsewhere (curl, API docs, a link for a colleague).
- Tags, log lines and verbatim errors are copied literally: no URL wrapping, no added `http(s)://`, no pasting a whole logcat.
- When a description can locate it, do not quote it: describing where a piece of code sits beats pasting a screenful.

## 4. Emphasis (bold first)

- Bold lands only on verdict words, key numbers, reversal points (`old → new`) and actions that must be followed; 3–5 spots per reply at most.
- Order the means by availability: **bold** > `inline code` > block quote. Plain text and terminals have no color — no ANSI escapes, no HTML `<span>`, no emoji as highlight.
- Bolding a whole sentence is the same as bolding nothing; do not go past two heading levels.

## Check before sending

1. Is the first line a verdict that stands on its own?
2. Are parallel items written as a paragraph? Does each one lead with its conclusion on its own line?
3. Any bare URL, absolute path or droppable reference left?
4. After splitting, do you exceed the downstream skill's line cap, or break its field block apart?
