# Changelog

Format: newest first. Versions follow `VERSION`; every release is tagged.

## 1.3.1

- `multi-model-plan`: §6 now opens with a gate group — `Executability` (`yes` / `no` / `needs N items`) with `Blocker` / `Items to add` as conditional fields, plus `Biggest risk step` and `Missing evidence` — and a separate `Calibration quality` group (`3/3` / `2/3` / `1/3·low` + the silent slugs), so the reader decides whether to act before reading the plan. `Verdict` may not contradict it.
- The gate follows evidence, not votes: at `1/3` the silent slugs and the items the parent agent did not re-check become mandatory, but executability is still decided by whether an item lands on a `file:line`, an interface or verbatim error text — a single-model plan is neither upgraded because one answered nor downgraded because the vote count is low. A dispute sitting on the biggest risk step can no longer be marked `yes`.
- `old → new` stayed only in `Plan`, and `Missing evidence` now means the `Unverified` subset that blocks action, so the gate does not repeat the body fields.
- `coding-handoff-plan`: no separate gate group — the Handoff field names, order and titles are fixed — so executability rides in the "Conclusion" sentence, where `Open: none` and "Acceptance" already carried it.

## 1.3.0

- `multi-model-review`: the review no longer keeps running after the reviewers are done. The 6-minute round deadline is now a hard cap (publish what is in hand, mark the rest no response), and between "read the outputs" and "publish the synthesis" only file reads are allowed — no connectivity probes, thinking-level comparisons, diff-baseline recomputation, or "was this introduced by this change" spelunking; those go to the next turn marked "to verify". One real run burned ~10 extra minutes on exactly that after all three reviewers had returned.
- `prd-to-task`: a handoff document can no longer contradict itself. The pre-write check gained "one behaviour, one definition" and "handoff section not stale" rows — the same behaviour may appear only once across body / implementation steps / forbidden list / acceptance / request budget, and every handoff step is walked against the last change-log turn. The triggering document had the loading and retry behaviour rewritten in turn 35 while its handoff steps and forbidden list still carried the turn-27/30 version, so the implementer built the retracted one.
- `prd-to-task`: new required table 11, "new-abstraction contract" — for any "add a centralized X" instruction it pins whether the parameter may have a default, every call site, how it stays in sync with the single source of truth, and range handling. Files created during implementation must be added to the change boundary first. A real P0 (a resolver defaulting to the 6-tab layout while the renderer built 5 tabs) came from a document that asked for the abstraction without that contract.
- `prd-to-task`: bitmap acceptance now requires transparent background, scale and size basis per new image (a white-backed error illustration shipped because only "the two icons have different md5" was checked); the UI-restoration traps gained "anchor drift" (elements positioned by copy width must state their en and id position or be re-anchored to the icon); acceptance needs one en and one id line whenever visuals change.
- `prd-to-task`: the implementation check is no longer user-triggered only — a handoff must tell the implementer to run it before committing and write the W/I list back.

## 1.2.0

- New `multi-model-plan`: turn one model's plan into a calibrated v2. A written brief (facts and guesses kept apart) goes to 2–3 reviewers that either blind-review the existing draft or each draft their own without seeing the others; the parent agent then judges every item accept / partial / reject with a reason, weighs evidence over votes, and reports disagreements as 2:1 / 1:1 instead of "most models agree".
- It inherits the hard-won review rules rather than rediscovering them: reviewers get no tools, 300s per-model timeout, `Promise.allSettled` fan-out, staged calibration once two results are in, a 6-minute round deadline, an 8-item output budget, and no self-substitution when a model returns nothing.

## 1.1.4

- `multi-model-review` reviewer runs are now explicitly tool-free: no `--tools`, no `-t read,bash`, and no "you may read the repo" sentence in the prompt. A real review that granted `read,bash` spent 13 minutes producing 5.3KB from one model, while the same input volume without tools returned in 6 seconds.
- Added a per-model hard timeout with "no response (timeout)" handling, staged delivery (publish once two results are in), a 6-minute round deadline, a written output budget (at most 12 findings, P0/P1 only) and diff sharding above ~120KB or 30 files.

## 1.1.3

- `multi-model-review` no longer carries one agent's implementation in its body: the fallback for a side
  without a headless CLI now says "use this side's parallel read-only reviewer mechanism, see `TOOL-MAP.md`".
- Its description lost the implementation detail (`pi -p` / Task subagents) and is now identical per side,
  trigger first.
- `TOOL-MAP.md` / `TOOL-MAP.en.md` gained a "parallel read-only review" row.

## 1.1.2

- `tools/verify.mjs` now compares the side set of `META.<lang>.json` against `META.json`, so an English
  file that silently drops a side fails the check instead of rendering one agent short.
- `requesting-code-review` no longer carries a relative markdown link that only resolves after install;
  the body names the file and its source-repo location instead.

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
