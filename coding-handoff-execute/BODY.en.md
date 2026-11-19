# coding-handoff-execute

Executes a Handoff that is already written. No redesign.

## Boundaries

- Change only what the Handoff's "Files" and "Steps" name. Read the file with the read tool before editing, edit with edit / write, run commands with bash, and track multi-step progress with a step list.
- Do not add files, dependencies, behavior or refactors that the steps do not contain.
- If "Repo" lies outside the current session workspace, say so first and ask the user to widen the sandbox (workspace-write → danger-full-access); stop if refused instead of failing silently.
- Do not fill in decisions the Handoff lacks by reading the chat history.
- If the user wants the plan changed, stop and say to name `coding-handoff-plan`.

## Order

0. When the Handoff points at a task document, run its two gates before touching anything:
   `python3 {{SKILLS_ROOT}}prd-to-task/scripts/validate_task_doc.py <task doc in docs> --repo <repo root> --nodes <nodes.tsv> --manifest <asset manifest>` and
   `bash {{SKILLS_ROOT}}prd-to-task/scripts/check_assets.sh --repo <repo root> <asset manifest>`.
   On any FAIL, stop and paste the output as is (never fix the document yourself); wait until the document is complete.
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
- When a step names a Figma node and the document ships a `nodes.tsv`, check the frame and visibility against the dump first (does the parent chain belong to this design version, and is the node not `hidden`) before writing code.
- When a step names a Figma node, read that node once for its values (size / type size / color / radius / gaps / asset logical size) before writing code; never take framework defaults: no `TextField` without a `style`, no container without radius and padding, no eyeballed thumbnail size.
- When the handoff gives a node link but no visual values: treat it as "Open" per Order step 3, stop and ask for the visual spec table instead of guessing (guessing is how a 154px example image ships as 67px and a 0-alpha app bar renders black).
- Before delivering a UI step, put the node export and the implementation screenshot side by side and run three must-checks: is the app bar / status bar fill visible, is any copy cut off with an ellipsis, do thumbnail logical sizes match the design. Fix the differences yourself; anything you cannot fix goes under "Next" in the reply.

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
