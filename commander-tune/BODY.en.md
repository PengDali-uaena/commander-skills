# commander-tune

**Invoking this runs a session audit**: first scan all recent sessions (across every repo) for the actual commander and skill calls plus your reactions, then combine that with this conversation to produce a problem list and fixes. Never judge from "what this turn happened to be about".

**While this skill is active**: no routing through commander; this file governs the turn.

## Default actions (in order, none skipped)

### 1. Run the audit script

```bash
python3 {{SKILL_DIR}}audit.py                # last 14 days, all repos (default)
python3 {{SKILL_DIR}}audit.py --days 30      # wider window
python3 {{SKILL_DIR}}audit.py --repo <name>  # one repo only (matches the session dir name)
python3 {{SKILL_DIR}}audit.py --skill explain
```

The script reads one side's `sessions/**/*.jsonl` (Pi's `~/.pi/agent/sessions` by default; point it elsewhere with `--sessions` / `--skills`) and reports: session count and real request count, how many turns each skill was read, what you said right after each call (continue / push back), repeated reads within one turn, the share of bold first lines / over-8-line replies / absolute paths, and the share of turns with no skill.

- Script missing or failing: recompute with `rg` / `python3 -c` per "Manual recipe" below, and **never skip the evidence and go straight to a conclusion**. The script is a Pi-side attachment (like `tune-log.md`, not produced by `dist.mjs`); on dsh / cursor where it does not exist, use the manual recipe.
- **Non-Pi sides (Cursor / DSH) have no parsable session logs**: do not run pi's `audit.py`; use the external stats you paste plus this conversation as evidence and mark the first line of the diagnosis "sample provided by the user" (with no external stats, audit this conversation only and state that coverage is limited).
- Coverage: the script counts Pi sessions only (`~/.pi/agent/sessions`). When you paste Cursor / DSH stats, write both sets of numbers side by side and mark the smaller sample "insufficient sample".

### 2. Read the current state (only what is relevant)

| Order | Path | Purpose |
|------|------|---------|
| 1 | `{{SKILLS_ROOT}}commander/SKILL.md` | routing table, hard constraints, "continuing from the last turn" |
| 2 | the `SKILL.md` of skills the audit flagged | that skill's description and "visible reply" contract |
| 3 | the last 3 entries of `{{SKILL_DIR}}tune-log.md` | avoid repeating proposals, see what was rejected last time |

No directory scans: read only the skills whose metrics are off (few calls / push-back / format violations).

### 3. Judgment criteria

| Signal | Conclusion |
|---|---|
| Few calls, your next message is "continue / ok / go" | Rare scenario, **leave it**, do not delete or merge |
| Your next message pushes back (too long / wrong / redo / cannot understand) | Effectiveness problem, **fix the contract or tighten length first** |
| The skill was read but that turn's answer is no different from not reading it | False trigger; narrow the trigger surface or drop its name from the constraints |
| An artifact clearly matches a row, yet zero calls | Coverage gap; add a routing row or write the criteria into commander |
| The same skill read twice in one turn | Wasteful read; state "already in context, no need to re-read" at the top of commander or in that skill |
| No bold first line / over 8 lines / many absolute paths, concentrated in turns with no skill | Execution-layer problem; low payoff from text edits, so record it as an observation |

Few calls is never a problem by itself; being opened without benefit, or being opened and then told to shorten, is.

### 4. Proposals and applying them

Each change item states: **where** (file + section), **what** (before → after), **why** (which signal above, with numbers), **risk** (could it misroute).

- By default output the diagnosis plus the list, and end with one question: "Apply the list? (yes / no / only item N)"
- If you already said "just change it / apply / write it": execute only the items you explicitly approved.
- Editing a `SKILL.md` produced by `dist.mjs` is a no-op: edit `{{SRC_ROOT}}/<name>/BODY.md`, run `node {{SRC_ROOT}}/dist.mjs`, then finish with `--check`.
- New skill: `{{SRC_ROOT}}/<kebab-name>/{BODY.md,META.json}` + one row in commander's artifact table + `dist.mjs`.
- After applying, append a section to `{{SKILL_DIR}}tune-log.md`: date, trigger summary, files changed, rejected proposals.

## Manual recipe (when the script is unavailable)

```bash
# 1. which skills each turn read (scan toolCall entries for skills/<name>/SKILL.md)
rg -o 'skills/[a-z0-9-]+/SKILL\.md' -N ~/.pi/agent/sessions | awk -F/ '{print $(NF-1)}' | sort | uniq -c | sort -rn

# 2. what you said right after a skill call (read it back to judge continue vs push back)
rg -n 'skills/explain/SKILL.md' ~/.pi/agent/sessions

# 3. share of turns with no skill: count role=user messages, subtract turns that read a skill
rg -c '"role":"user"' ~/.pi/agent/sessions | awk -F: '{s+=$2} END {print s}'
```

The recipe only has to match the script's definition and the numbers must reconcile; when they do not, state which definition was used and why.

## Visible reply shape

Paragraphs plus lists; never the "conclusion / basis / boundary" template:

1. One or two sentences: the main problem the audit numbers show (not a vague "basically fine")
2. **Session diagnosis** (3–8 bullets, each with a number)
3. **Change list** (numbered: where / what / why / risk)
4. One confirmation question (when not yet authorised to apply)

When the user only wants the one-line "which skill should be used" answer, still give the audit conclusion first, then one line `Suggested: <name>`.

## Boundary with commander

- **Changing commander**: routing table, hard rules, "continuing from the last turn", "when unsure ask one question", precedence notes.
- **Changing downstream skills**: visible reply, depth layers, repo-read limits, prohibitions; add a `learned.md` entry when needed (noting the source conversation summary).
- **Not changed**: the repo's `AGENTS.md`, project rule directories, built-in directories such as `skills-cursor/`; cross-agent sync goes through `skill-sync`.

## Example triggers

- `commander-tune` (scans all sessions from the last 14 days by default)
- `commander-tune --days 30 look at the long-term trend`
- `commander-tune last turn should have gone to code-logic but it added logs instead`
- `commander-tune apply directly: add a "find file" row → file-locate`
