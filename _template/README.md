# Skill template

Copy this directory when adding a skill:

```bash
cp -r _template my-skill
# then edit my-skill/BODY.md, my-skill/META.json, optionally my-skill/META.en.json
node dist.mjs
```

Rules the renderer and the checks enforce:

- The directory name is the skill name; it must match `name` in every frontmatter and use lowercase,
  digits and hyphens only.
- `BODY.md` holds the text with no frontmatter. `META.json` holds one `frontmatter` string per agent
  side (`pi`, `cursor`, `dsh`, `agents`, `claude`). If a side is missing, that side is skipped.
- Put the trigger conditions first in every `description`: Codex shortens descriptions under budget.
- Only two built-in placeholders exist: `{{SKILL_DIR}}` and `{{SKILLS_ROOT}}`. Anything else must be a
  key from `profile.default.json` (uppercased, camelCase becomes `_`), otherwise rendering fails.
- Scripts and references go under `assets/`; they are copied verbatim next to `SKILL.md`.
- A localized body is `BODY.<lang>.md` with its matching `META.<lang>.json`.

Directories whose name starts with `_` are never rendered, so this template stays inert.
