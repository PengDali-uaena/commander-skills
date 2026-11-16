# Contributing

Thanks for trying these skills. The repo is small on purpose: text lives in one place, everything else
is generated.

## Ground rules

- No personal, company or secret information. The pre-commit hook and CI both scan for it; a hit blocks
  the build. Write "a private repo", "an internal service" instead of real names, and use placeholders
  for paths.
- Agent differences belong in `TOOL-MAP.md`, never inside a body. A body that names one agent's tool
  (`read`, `@name`, `/skill:name`) is a bug.
- Bodies state judgments, flow and the output contract. Installation, versions and packaging stay out.
- Keep a new skill reachable: add one row to `commander/BODY.md` (and `BODY.en.md` when you write the
  English version) describing the artifact it produces.

## Adding a skill

1. `cp -r _template <name>`, then edit `<name>/BODY.md` and `<name>/META.json`.
2. Put the trigger words first in every `description`; Codex shortens descriptions under budget.
3. Only `{{SKILL_DIR}}` and `{{SKILLS_ROOT}}` are built in. Anything else must exist in
   `profile.default.json`; an unknown placeholder fails the render instead of shipping as-is.
4. Scripts and references go under `<name>/assets/`; they are copied verbatim and checked for drift.
5. `node dist.mjs` then `node dist.mjs --check`.

## English bodies

- English lives in `BODY.en.md` with `META.en.json`; Chinese is the default and keeps the plain names.
- Translate the criteria, not the wording: Chinese trigger phrases ("which is better") must become the
  phrase an English speaker would actually use.
- Keep the heading tree identical to the Chinese body; `tools/verify.mjs` compares them.

## Before you open a PR

```bash
git config core.hooksPath .githooks   # once per clone
node tools/verify.mjs                 # structure, placeholders, heading parity, leak scan
node dist.mjs --check                 # rendered output matches the sources
```

The same two commands run in CI. If you installed the skills locally with a non-default language, the
check follows `.skill-lang`, so no extra flags are needed.

## Style of the text

- Imperative, one rule per line. Prefer a concrete number or a concrete path over an adjective.
- Never weaken a negation to save words.
- When a rule exists because of a specific past failure, say what the failure was in one clause; future
  readers keep the rule only if they know what it prevents.
