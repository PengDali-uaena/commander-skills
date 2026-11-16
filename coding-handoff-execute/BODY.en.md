# coding-handoff-execute

Executes a Handoff that is already written. No redesign.

## Boundaries

- Change only what the Handoff's "Files" and "Steps" name. Read the file with the read tool before editing, edit with edit / write, run commands with bash, and track multi-step progress with a step list.
- Do not add files, dependencies, behavior or refactors that the steps do not contain.
- If "Repo" lies outside the current session workspace, say so first and ask the user to widen the sandbox (workspace-write → danger-full-access); stop if refused instead of failing silently.
- Do not fill in decisions the Handoff lacks by reading the chat history.
- If the user wants the plan changed, stop and say to name `coding-handoff-plan`.

## Order

1. No complete Handoff in the message: reply only "Handoff missing" and stop.
2. Check that all fields are present, in this order: Goal, Repo, Constraints, Forbidden, Files, Steps, Acceptance, Open.
3. If any field is empty, or "Open" is not "none": list only the missing items and stop.
4. If the "Repo" directory does not exist, or a step's path or symbol does not resolve: quote that step and stop. Do not search the whole repo for an alternative.
5. Apply the steps in numeric order.
6. Run the commands in "Acceptance", subject to the target repo's rules: commands the repo's AGENTS.md / .cursor rules forbid (test / lint / packaging / touching devices) are not run — do a manual check instead and state why. When it says "no command", skip the command and do only the manual checks that are possible.
7. Reply in the three sections of the global AGENTS.md — "Conclusion / Points / Next" — with at most 220 words of body: which files changed, the acceptance result, and what is still open.

## Implementing

- Follow "Constraints" and "Forbidden".
- Read only the files the step names. To implement the step you may open a definition it references directly, and stop once read.
- When a step gives a minimal replacement snippet, replace exactly that.
- When a step states only the outcome, achieve it in the style the file already uses.

## Acceptance fails

- The failure is because the step is not done yet: finish that step, then re-run acceptance once.
- The same command fails twice in a row: stop, and hand the exact command and its output to the user.
- The failure is a conflict between the Handoff and the code: stop and quote the conflicting step and the error output. Do not change the plan.

## Handoff format

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
