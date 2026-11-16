# Changelog

Format: newest first. Versions follow `VERSION`; every release is tagged.

## 1.1.1

- `install.sh` records every side it has written to (`.installed`) and warns when a rerun drops a side,
  since two directories holding the same skill means the agent discovers it twice; `--clean-old` removes
  exactly those stale copies.
- `--uninstall` and `--clean-old` share one manifest-based removal routine.

## 1.1.0

- Both code-review skills now ship a Chinese body (`BODY.md`) next to the English one (`BODY.en.md`),
  with `META.en.json`, so an English install no longer falls back to Chinese for them.
- Removed the remaining project-specific verification rule from `receiving-code-review`; it now defers to
  the consuming repo's `AGENTS.md`.
- Added `AGENTS.md` / `CLAUDE.md` so an agent editing this repo has an entry point, and `CHANGELOG.md`.
- README: platform limits (bash; macOS / Linux / WSL) documented in both languages; the Chinese README now
  explains the `.generated` manifest behind `--uninstall`.

## 1.0.0

- Five distribution sides: Pi, DSH, Cursor, Codex (shared `~/.agents/skills`) and Claude Code.
- `install.sh` with detection, `--lang`, `--dirs`, `--dry-run`, `--no-hooks`, `--uninstall`, `--version`.
- `dist.mjs` renders from `BODY[.<lang>].md` + `META[.<lang>].json`, syncs `<name>/assets/**`, resolves the
  source repo from its own location, honours `{{SKILL_DIR}}` / `{{SKILLS_ROOT}}` / `{{SRC_ROOT}}` and the
  `profile.default.json` placeholders, and fails loudly on an undefined placeholder.
- `profile.default.json` + gitignored `profile.local.json` for per-machine values (`docPrefix`,
  `style.maxLines`, `style.maxBold`).
- `tools/verify.mjs` (structure, heading parity, placeholders, leak scan) plus a GitHub Actions workflow
  that renders and drift-checks both languages.
- Bilingual README, `TOOL-MAP.md` / `TOOL-MAP.en.md`, `CONTRIBUTING.md`, MIT `LICENSE`, `_template/`.
