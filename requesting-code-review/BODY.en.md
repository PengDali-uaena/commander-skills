# Requesting Code Review

Initiate a review when a task completes, a major feature lands, or before merging. The reviewer receives a **carefully packaged work product plus the requirement it must meet**, not the whole conversation history — otherwise they get absorbed in the reasoning and miss the deliverable.

**Core principle:** Review early, review often.

Use only when the user names it explicitly or the workflow requires "request review / review the deliverable before merge". Handling feedback you receive goes through `receiving-code-review`.

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. Dispatch code-reviewer subagent**

1. Read `code-reviewer.md` in this skill's directory (in the source repo it lives at `requesting-code-review/assets/code-reviewer.md`) and fill in the placeholders.
2. Pi (no Task/subagent tool): run a headless, read-only reviewer subprocess. `-t read` is the read-only tool set — the reviewer can open files for context, and cannot edit files or run commands.

```bash
TS=$(date +%Y%m%d-%H%M%S); DIR=/tmp/review-$TS; mkdir -p "$DIR"
# 1) write the filled-in code-reviewer.md to $DIR/prompt.md
# 2) append the range under review as plain text (no code fences)
{ echo; echo "## Diff under review"; echo; git diff "$BASE_SHA".."$HEAD_SHA"; echo; } >> "$DIR/prompt.md"
# 3) run one reviewer only; add --model <provider/model> to review with another model
pi -p --no-session -nc -ns --no-mcp --mode text -t read < "$DIR/prompt.md"
```

3. Other subagent mechanisms (Cursor / Kiro / Claude Code): use the `code-reviewer` type; otherwise `subagent_type: generalPurpose`, `readonly: true`, with `prompt` set to the whole template after filling the placeholders. When that reviewer has a shell it can compute the git range itself instead of relying on the appended diff.
4. Never put an unfilled template or unrelated chat history into the prompt.

**Placeholders:**
- `{WHAT_WAS_IMPLEMENTED}` - What you just built
- `{PLAN_OR_REQUIREMENTS}` - What it should do
- `{BASE_SHA}` - Starting commit
- `{HEAD_SHA}` - Ending commit
- `{DESCRIPTION}` - Brief summary

**3. Act on feedback**

Verify per `receiving-code-review` before changing anything: Critical gets fixed immediately; Important before continuing; Minor can go to the backlog; when the reviewer is clearly wrong you may push back with reasons.

## Example

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch reviewer: pi -p -t read < prompt.md]
  WHAT_WAS_IMPLEMENTED: Verification and repair functions for conversation index
  PLAN_OR_REQUIREMENTS: Task 2 of docs/plans/deployment-plan.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators per receiving-code-review]
[Continue to Task 3]
```

## Integration with Workflows

**Subagent-Driven Development:**
- Review after EACH task
- Catch issues before they compound
- Fix before moving to next task

**Executing Plans:**
- Review after each batch (3 tasks)
- Get feedback, apply, continue

**Ad-Hoc Development:**
- Review before merge
- Review when stuck

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

Template path: `{{SKILL_DIR}}code-reviewer.md`
