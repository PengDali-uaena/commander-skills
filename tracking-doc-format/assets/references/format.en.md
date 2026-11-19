# Layout and counter-examples (tracking-doc-format companion)

The body only points here; all layout detail lives in this file.

## Output sample and indentation

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
