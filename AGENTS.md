# AGENTS.md — rules for agents working in this repo

This repo is a text distribution system, not an app: `BODY.md` + `META.json` per skill, rendered into each
agent's skills directory by `dist.mjs`. Read `README.md` for the layout and `CONTRIBUTING.md` for the flow.

## Hard rules

- Never edit a generated `SKILL.md` or `assets/` file; edit `BODY.md` / `META.json` / `<name>/assets/**`
  in the repo, then run `node dist.mjs`.
- No personal, company or secret information. `tools/verify.mjs` and the pre-commit hook both scan for it.
- Agent-specific wording (tool names, invocation syntax, absolute side paths) belongs in `TOOL-MAP.md`,
  never in a body.
- Keep the Chinese body as the default (`BODY.md`) and mirror headings in `BODY.<lang>.md`; the verify
  script compares heading levels.
- A new skill gets: `BODY.md`, `META.json` with at least a `pi` side, and one row in `commander/BODY.md`.

## Commands

```bash
node dist.mjs            # render every existing side
node dist.mjs --check    # drift check (language-aware: follows .skill-lang)
node tools/verify.mjs    # structure, placeholders, heading parity, leak scan
./install.sh --dry-run   # what a fresh install would write
```

`install.sh` writes `.skill-lang` / `.installed` (both gitignored); leave them out of commits.

## Style

- Imperative, one rule per line; a concrete number or path beats an adjective.
- Do not weaken a negation to save words.
- When a rule exists because of a specific past failure, say what the failure was in one clause.
