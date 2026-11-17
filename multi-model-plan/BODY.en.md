# multi-model-plan

Use when the user needs a plan they can act on, or does not trust the plan they have (missing pieces, unsupported assumptions): several models draft independently or blind-review the same draft, then the parent agent calibrates item by item into a v2.

Use only when the user explicitly names this skill (or this side's explicit load syntax in `{{SRC_ROOT}}/TOOL-MAP.md`) or clearly asks for a multi-model plan, a plan cross-review, or plan calibration. By default **no code changes, nothing written to disk**; when the user wants an executable handoff, use `coding-handoff-plan`.

## 1) Pick the mode

- **Blind review (default, a v1 exists)**: the prompt is the brief plus the full v1 plus the five questions. Each reviewer sees only the brief and the v1, never the other reviewers' opinions.
- **Parallel drafting (no draft yet, or the user says "this plan is not trustworthy / think again")**: the prompt holds only the brief and the five questions, nobody's draft. Anchoring collapses three models into one and hides the real disagreements.
- When unsure, ask one question — "review the existing plan, or have them each draft one?" — then stop. Do not pick for the user and start.

## 2) Write the brief (more important than the plan itself)

Reviewers have no tools, so anything missing from the brief gets guessed, and guessed gaps are indistinguishable from real ones at calibration time.

- Must contain: goal and acceptance criteria, hard constraints (platform / version / modules that must not change / dependencies not to add), known facts (`file:line`, interface names, verbatim error text, data shapes), known unknowns.
- Write facts and guesses as two separate blocks; anything unsupported is marked `(guess)`, so a guess never turns into a constraint.
- Size: keep the brief around 120KB or less; above 30 files, compress it into a subsystem-plus-constraints list instead of pasting source. Input is not the bottleneck (measured: 137KB in, 6–14s out); output length and tool turns are.

## 3) Pick models

- One `pi --list-models` plus one `pi auth check --provider <p>`; do not trial-run every slug — that burns the budget during setup.
- Inline the candidates with numbers plus slugs, presented neutrally: no recommendation, no sorting, no preselection, no omissions, no "(Recommended)"; skip `not_ready` providers and 403 models, and write one line, "<slug> skipped, 403 unavailable".
- Two models by default, three at most; keep one per vendor generation, since two models from the same family are not two independent opinions.
- If the user already named models, use them; when a slug is rejected at run time, substitute the closest valid slug and say what changed.

## 4) Run in parallel (no tools / hard timeout / no waiting for everyone)

Start one headless reviewer per slug, read-only, foreground, in parallel:

```
pi -p --no-session -nt --no-mcp -nc -ns --mode text \
  --append-system-prompt "You have no tools in this session. Never emit tool calls or tool_call XML; answer directly in markdown." \
  --model <provider/model> < /tmp/mmp-<ts>/prompt.md
```

- **Never give a reviewer tools**: no `--tools`, no `-t read,bash`, and no "you may read the repo / run commands" in the prompt. Measured: the run that granted `read,bash` spent 13 minutes to produce 5.3KB, while the same input volume without tools returned in 6 seconds; tools also push conclusions outside the plan.
- **Hard timeout of 300s per model**: macOS has no `timeout`, so use the codemode `tools.bash` `timeout`, or `gtimeout`, or launch in the background and `kill` at the deadline. On expiry record "no response (timeout)"; no rerun and no substituting another model.
- **Parallel is mandatory**: fire every call at once with `Promise.allSettled` inside one `codemode` script; never await one by one, never `sleep 120/180` waiting on the slowest one.
- **Calibrate in stages**: as soon as ≥2 results are in, publish the first v2 and top up within the deadline (6 minutes for the whole round); with only 1 result, say plainly "the other N did not respond" rather than standing in for a model to fake a multi-model round.
- A failure (403 / timeout / empty output) is recorded as no response and does not affect the other reviewers.

The `prompt.md` must also pin down:

- **Output budget**: at most 8 items, each `[P0|P1|P2] conclusion → evidence → impact`, at most 3 sentences; no restating the brief, no closing summary. Without a cap one model writes 12KB, which at 30–120 chars/sec is 2–7 minutes of pure generation.
- **Five mandatory questions** (left open, each model picks its own angle and the results cannot be merged):
  1. What is missing: boundaries, states, failure paths, ordering of dependencies;
  2. Which assumption has no evidence;
  3. Where is the order or dependency wrong, and which step stalls first;
  4. What is the worst case, and how do we roll back;
  5. Is there a simpler approach, and which steps can be deleted.
- Every conclusion must land on a `file:line`, an interface, verbatim error text or a reproducible step; otherwise mark it `(guess)`. When there is nothing to report, write "no findings" explicitly.

## 5) Calibrate (parent agent; the step most often skipped)

- Judge every item: accept / partially accept / reject, each with one reason; a rejection always states why, and nothing is dropped silently.
- **Evidence beats votes**: two models pointing at the same thing without evidence is still `(guess)`; an item becomes a change only when it lands on a `file:line`, an interface, verbatim error text or a reproducible step.
- Record disagreements as `2:1` / `1:1` with each side's grounds; never close with "most models think", since votes are not evidence.
- One round per plan. A second round happens only when the disagreement sits on the critical path or the user asks, and only the disputed points are redistributed — never the whole package. No third round.
- The v2 must answer: what changed (old → new), which items were rejected, and which assumptions are still unverified.
- **Record the calibration quality**: how many answered out of how many asked (`3/3` / `2/3` / `1/3·low`) plus the silent `<slug>`s, written into the §6 gate group; at `1/3` also list the items you did not re-check.

## 6) Delivery

By default the v2 goes in the reply only — no code changes, nothing written to disk, no self-initiated test run. When the user wants an executable handoff, use `coding-handoff-plan`.

Answer as a field block (one field per line, each starting with `- `, field name in bold, one blank line between groups). The first group is the gate: reading it is enough to decide whether to act, without reading the plan first.

- **Executability**: `yes` / `no` / `needs N items`, pick one
- **Blocker**: only with `no`, one sentence on where it stalls
- **Items to add**: only with `needs N items`, one per line, the count must match N
- **Biggest risk step**: the step that stalls first when the v2 is executed, one sentence; no "overall risk" generalities
- **Missing evidence**: the unsupported items standing in front of executability (the ones inside `Unverified` that block action); write `none` when there are none

- **Calibration quality**: `3/3` / `2/3` / `1/3·low`, followed by the silent `<slug>`s

Gate rules:

- The gate only follows evidence: the bar is whether an item lands on a `file:line`, an interface, verbatim error text or a reproducible step (see §5), not the vote count; a single model with evidence still counts.
- At `1/3`, `Missing evidence` is mandatory: the silent slugs plus the items you did not re-check. Do not mark `yes` just because one answered, and do not downgrade to `no` just because the vote count is low.
- When the dispute sits on the `Biggest risk step`, executability is not `yes`: write `needs N items` and list which ones.
- When the gate and `Verdict` contradict each other, the gate wins.

- **Verdict**: what the v2 is in one line + accepted N / rejected M / disputed K; must not contradict `Executability`
- **Plan**: core steps, one per line; changed ones written as `old → new`
- **Accepted**: `<model>` — item + anchor (`file:line`)
- **Rejected**: item — reason
- **Disputed**: `2:1` / `1:1` + each side's grounds
- **Unverified**: assumption + how to check it
- **Next**: handoff doc / implement now / one more round on the disputed points only

## Not doing

- No code changes, no files, no tests, unless the user says otherwise.
- Never let one model play two roles to fake a multi-model round; one result is reported as one.
- Never copy a reviewer's wording into the conclusion: uncalibrated output is raw material.
- Never invent steps the brief does not support; mark missing information `(to verify)`.
