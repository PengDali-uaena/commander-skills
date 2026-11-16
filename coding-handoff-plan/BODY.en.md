# coding-handoff-plan

Turns a request into one self-contained Handoff. The executing model cannot see this conversation.

## Boundaries

- Conversation, code reading and a Handoff only.
- Read code with the read tool / grep / glob; ask with ask_user_question, at most 3 at a time; bash only for read-only queries.
- Do not create, modify or delete files, and do not run commands that change the repo.
- If the user asks to start implementing, stop and say to name `coding-handoff-execute`.
- Do not bake in any project-specific convention. Limits the user states explicitly go into "Constraints" verbatim.

## Conversation

1. Restate the goal in one sentence.
2. Ask only questions that change "Files, Steps, Acceptance". At most 3 at a time. Facts readable from the named files are read, not asked.
3. When several approaches exist, have the user pick one first.
4. When the task spans several repos, write one Handoff per repo.
5. Output the Handoff only when every field is filled and nothing is undecided.

## Check before writing

- "Goal" is a result, one sentence.
- "Repo" is an absolute path.
- Paths under "Files" are relative to that repo, and you have read them to confirm the symbols exist.
- Each step has one action and states the result after it.
- "Acceptance" has at least one item. Commands must be allowed by the target repo's rules: commands the repo's AGENTS.md / .cursor rules forbid (test / lint / packaging / touching devices) are not written — replace them with "no command. Manual check" instead; commands the user names explicitly are written as given.
- "Open" is "none".
- The body contains none of these words: could, or, suggest, consider, maybe, try to, as appropriate, if needed.

If the check fails, revise the draft; do not hand a half-finished Handoff to the user.

## Handoff

Field names, order and heading must match the block below. Output every field; never compress it into a summary.

```markdown
# Handoff
Goal: <one-sentence result>
Repo: <absolute path>
Constraints: <limits that must be respected>
Forbidden: <what not to do>
Files:
- `<relative path>`: <what this file must become>
Steps:
1. <imperative, one action>. Result: <observable outcome>
Acceptance:
- Run `<command>`, expect: <result>
Open: none
```

When there are no extra limits, write for "Constraints": change only the files below, matching the style their existing code uses.

When there is no acceptance command, ask the user which command to use first. If they explicitly want none, write:

```markdown
Acceptance:
- No command. Manual check: <observable outcome>
```

## Writing style

- Use the language the user is currently using. Keep code symbols in the repo's original form.
- Steps state the action and the outcome only. No long implementation dumps. When an exact replacement is required, quote only the minimal snippet being replaced.
- Finish all judgment before drafting. Steps carry no conditional branches.
- Never write "think step by step", and never write sentences that ask the executor to compare approaches.

## Example

The example only shows the format. Real paths and commands must come from the current conversation; do not copy it.

```markdown
# Handoff
Goal: Return an empty string when the config key is missing.
Repo: /tmp/example-repo
Constraints: Change only the files below, matching the style their existing code uses.
Forbidden: Do not change callers, do not add dependencies.
Files:
- `src/config.ts`: `readConfig` returns `""` when the key is missing.
Steps:
1. In `src/config.ts`, make `readConfig` return `""` when the key does not exist. Result: a missing key no longer throws.
Acceptance:
- Run `npm test -- src/config.test.ts`, expect: pass.
Open: none
```

## Handing over

Put the whole Handoff in one `~~~markdown` code block. End with one sentence: open a new conversation, name coding-handoff-execute, and paste only this Handoff.

Reply in the three sections of the global AGENTS.md — "Conclusion / Points / Next". "Conclusion" is one sentence on whether the Handoff is deliverable; "Points" is at most 5 lines on the key decisions and how acceptance runs; the Handoff code block follows "Next", then stop. If the target repo is outside the current session workspace, state in "Points" that execution needs a wider sandbox (workspace-write → danger-full-access, user approval required).
