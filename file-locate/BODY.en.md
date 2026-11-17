# file-locate

Answers "**which file** (or Widget)" — by default one **main path** only; no mount chain, no API fields.

No logs, no file edits (if the user asks for a code change in the same message: answer the path first, then edit).

## Reading the repo

1. If the project has `.agents/docs/reference/file-keyword-mapping.md`: read it first; on a hit, open the matching file to confirm the symbol / Widget name.
2. Otherwise: at most **2** targeted searches (keywords from the user's description: page name, card name, domain term), then read no more than **3** files to confirm "this is the UI implementation file".
3. No repo-wide scanning, and no piling up related files (model, sheet, response parsing) unless the user asks.

## Visible reply · default (summary layer)

- **First line**: path relative to the repo root; an optional `→ ClassName` half-sentence goes on the same line.
- **Second line (optional)**: only when an **easily confused** implementation exists, write "not `…/other.dart`" (e.g. product detail and checkout each carry their own consignment UI).
- **Never by default**: mount Section lists, data models, popups, API fields, domain exceptions, multi-heading bullet lists.
- At most one closing line: `For the mount/reference chain use code-logic, or ask me to expand.`

If the user says "expand", "how is it mounted", "who else uses it" → this skill may still give the main path first, then the **full layer** below, or hand over to `code-logic`.

## Visible reply · full layer

When the user explicitly asks for the reference/mount chain, follow the first line with at most **5** bullet lines:

- Each line: `role (entry / wrapper / data) → path`. Do not write API JSON key names unless the user asked where the data comes from.

## Boundary with code-logic

- Only "where is it" → this skill.
- "How does it flow, where does it enter, what are the branches" → `code-logic`, not this skill.
