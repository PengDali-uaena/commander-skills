# Changelog

Format: newest first. Versions follow `VERSION`; every release is tagged.

## 1.6.0

- `prd-to-task`: new "UI gate" — whenever a round touches UI, three inputs come first and nothing starts without them: structure (layering, what scrolls, what the keyboard pushes, card order), position (which layer / card / section, not "there is a button on the page"), and nodes (node id + frame name; without Figma, a screenshot plus logical sizes, never eyeballed pixels). Missing one, the skill asks only for that one and stays in progress; when the user pastes node links only, it reads the node tree and reads its candidate structure back for confirmation.
- `validate_task_doc.py`: an empty `视觉骨架` table is now a FAIL, not a WARN — the gate artifact cannot be a header with no rows. Verified with a negative fixture (removing the single skeleton row fails the doc while the compliant fixture stays at 0 fail).
- `coding-handoff-execute`: a UI step missing structure / position / nodes stops as "Open" and asks for those three only, instead of shipping a first draft to be corrected.
- `commander` gained hard rule 11: any UI request needs structure / position / nodes first, so the gate fires even on turns that pick no skill or edit code directly — it lives in the skill layer, not in a repo's AGENTS.md.

## 1.5.0

- `prd-to-task`: version stamping. The document header now carries `技能版本：<SKILL.md md5 first 8> / <time>` and the first round re-reads the installed skill's write time, telling the user which version it runs on. Reason: the three review rounds all ran inside one long Cursor session, so skill edits made on disk never reached it — a stale snapshot silently disables every new rule.
- `prd-to-task`: complexity tiers. `复杂度档位：S / M / L` is decided in round one from feature-point count, node count and new-page count, and it decides how much is mandatory — S may skip six tables with a reasoned `表适用性` line, M requires all eleven plus a six-row visual spec, L requires splitting, a separate implementation session and an eight-row visual spec. The validator enforces the L/node>20 case and WARNs when an S document skips a table outside the S list. Reason: a 10-feature, 42-node page was graded with the same checklist as a 3-feature page.
- `prd-to-task`: a document session no longer implements — the handoff says implementation runs in its own session and the implementer opens with both gates; writing the document and editing `lib/` in one session counts as out of bounds (self-graded work is not a review).
- `prd-to-task`: closing reply carries three comparable numbers — rounds used, validator fails, implementation-check W count — so "it feels worse" becomes a trend.
- New `references/input-spec.md`: the requester-side input spec (structure first, node list with the frame version, change labels, acceptance as tap → see, version check, rework-to-missing-input table). The skill points to it instead of restating it in chat.

## 1.4.0

- `prd-to-task`: the self-check is now a script, not a tick-box. New `scripts/validate_task_doc.py` fails the document when a feature block misses a required section, a table header misses a column, the header blocker counts disagree with the pending table, the state is illegal for those counts, an asset row says `export`, a listed asset file is absent, a node id is missing from the evidence dump, an acceptance line is unverifiable, or a question keyword is logged twice. `--legacy` downgrades structural problems for old documents only; assets, nodes and sizes are never downgraded. First run against the real 2026-11 review document: 30+ FAIL, including `视觉规格` and `导出方式` missing everywhere while the document had been marked executable.
- `prd-to-task`: new `scripts/check_assets.sh` (+ `check_assets.py`, pure python3) gates every new bitmap: alpha channel with real transparent pixels, size = logical × 3, volume not larger than baseline, corner pixels printed. Run on the shipped review assets it fails both example images with "no alpha channel" and corners `#1e1e1e` — the white-background symptom the user had been reporting for rounds.
- `prd-to-task`: "skeleton first" — the first two rounds only settle layering, scroll ownership, fixed bars and card order into `### 视觉骨架`, and `视觉规格` / `UI assets` cannot be filled before it. Expanding into per-control tables before the structure exists is what produced a black-backed app bar and stacked cards.
- `prd-to-task`: round budget — at most 15 rounds per feature point; at the cap the suggestions are written and marked `pending (defaulted by suggestion)` instead of another single-question round trip (the triggering document ran 69 rounds). Open questions moved to `docs/<prefix><date>-queue-<feature>.md` so each round reads a 40-line queue instead of an 800-line document.
- `prd-to-task`: Figma evidence dump — every node the document mentions must exist in `docs/<feature>/nodes.tsv` (id / type / visible / name / parent chain / text / fills / size), dumped once with `references/figma-node-dump.md`; the parent chain must name this feature's frame, which stops `8699` vs `8773` frame mixing, and `type=TEXT` nodes stop being sliced as icons.
- `prd-to-task`: tables no longer apply by coercion — a feature writes `表适用性：跳过 X（原因）` and the validator accepts it by that line, so non-UI features stop inventing permission tables.
- `prd-to-task`: missing-tool degradation is explicit — no shell / network / figma means `pending (no tool; owner: implementation round)` with blocking level **blocks development**, never a "command template" left behind as delivery.
- `prd-to-task`: body split — the eleven required tables plus the four question classes moved to `assets/references/checklists.md`, read on demand; `BODY.md` 563 → 396 lines.
- `coding-handoff-execute`: the implementation round now opens by running both gates and pasting the output; on FAIL it stops and reports instead of building on a defective document. Figma steps also check frame and visibility against `nodes.tsv` first.
- `commander`: the prd-to-task row names skeleton-first and the two scripts.
- New personal skill `figma-mcp-assets`: the Figma MCP asset pipeline now lives only on this machine (five sides rendered), not in any repo. It merges the old repo skill, its `reference.md` and `examples.md`: per-node `download_assets` at scale 3, PNG only from `rawImages` (the export is flattened), SVGs downloaded as is, byte comparison, lossless `optimize_png.sh`, and the `check_assets.sh` gate pasted into the reply. Whole-screenshot nodes are recorded as `opaque` and clipped in code instead of pretending to be transparent. Reason: it is a tool-specific skill (the only one in the repo depending on an external MCP), so a teammate without Figma MCP could not follow it and its `alwaysApply: true` pointer turned into noise; the measurement that shipped two opaque example images sat in a file nobody could verify.
- `prd-to-task` now points at `{{SKILLS_ROOT}}figma-mcp-assets/scripts/optimize_png.sh` instead of a repo copy.
- App repo side: the Figma asset skill's examples recorded a wrong conclusion ("export is RGBA here, usable") that shipped two opaque 462×442 PNGs; corrected to the measured `hasAlpha: no` / corner `#1e1e1e` plus the `opaque` + container-clip rule, and the resource rule now requires the asset gate. The triggering task document's `curl "<export.url>"` template was replaced with the measured conclusion.

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
