# branch-merge

Merging has two stages: first state what each side of the conflict is trying to preserve and give a merge opinion, then stop. Only after the user confirms explicitly do you resolve the conflicts per that opinion and finish the merge.

## Before confirmation

Read the conflict itself; change no files; do not run `git merge`, `git add`, `git commit` or `git checkout --ours/--theirs`.

- Conflicts already exist: read only the conflict hunks and the adjacent code needed to understand intent. Use the two branches currently being merged.
- Merge not started yet: read only the overlap between the two branches the user named. If they named none, ask which two branches and stop.
- Describe intent as behavior; do not restate the whole diff. Write symbols, paths and branch names in full.

The visible reply is only these lines, following `commander`'s "field-block layout": every line starts with `- `, the field name is bold, fields inside a group are packed tight with no blank lines, and **there is one blank line between conflict groups**. No code fence, no opening line or summary outside the block.

One conflict per group, fixed order inside the group: conflict → current branch intent → target branch intent → merge opinion, five fields at the same level; never number `Conflict` or nest it. The confirmation field closes the block, stands on its own line, one blank line after the last group.

```
- **Conflict**: path or symbol
- **Current branch intent**: what `<current branch>` is trying to preserve
- **Target branch intent**: what `<target branch>` is trying to preserve
- **Merge opinion**: how to merge, which behavior survives, or how to combine them

- **Conflict**: a second path or symbol
- **Current branch intent**: …
- **Target branch intent**: …
- **Merge opinion**: …

- **To confirm**: files change and the merge completes only after confirmation
```

The turn ends here.

## After confirmation

Execute only when the user explicitly confirms this merge opinion. If the user changed the opinion without confirming: rewrite the fields above per the new opinion and still do not execute. If the same message both changes the opinion and confirms clearly: execute the new one.

- Implement only the merge opinion already written; do not touch other code on the way.
- Clear the conflict markers and stage the resolved files.
- Merge already in progress: finish it with Git's default merge message; do not write a `type(module): description` message.
- Merge not started: run the merge for the two confirmed branches; if a new conflict appears that the opinion does not cover, stop and go back to "Before confirmation" instead of guessing.
- No push, no `--no-verify`, no force or hard reset.

Visible reply after executing:

```
- **Merged**: which opinion, which paths changed
- **Result**: merge complete, or the new conflict it stopped at
```
