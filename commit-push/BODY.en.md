# commit-push

Get the commit line first, then commit and push with it. The line comes from `commit-message`: write one `type(module): description` per `{{SKILLS_ROOT}}commit-message/SKILL.md` and pass it verbatim as `-m`. Do not rewrite it, do not redraft it from the working tree. Do not change code this turn, and do not edit code just to get past a hook.

## Order

1. **Get the line**. If type or module cannot be told, ask one question and stop; do not commit.
2. **Check three things before committing** (never in the reply).
   - `git status --porcelain` is empty → stop and say there is nothing to commit; never create an empty commit.
   - Current branch is `dev` / `release` / `main` / `master`, or HEAD is detached → stop and ask which branch to commit to. Do not create a branch for the user; that is `branch-create`.
   - Stage only the files this conversation changed, one explicit `git add <path>` each. Any change unrelated to this one (another topic, untracked files) → list them and ask one question; never `git add -A` or `git add .`.
3. **Commit**: `git commit -m "<the line>"`. No `--no-verify`, no `--no-gpg-sign`; use `--amend` only when the user names it and that commit is not pushed yet.
   - Hook failure, a hook that rewrote files, or a signing failure → stop and hand over the verbatim output. Do not retry, do not bypass, do not edit code to satisfy the hook.
4. **Push**: `git push`; when the branch has no upstream → `git push -u origin <current branch>`.
   - Push only the current branch to its same-name remote branch. No force, no `--force-with-lease`, no deleting remote branches, no pushing another branch.
   - Rejected (non-fast-forward, need to pull first) → stop and hand over the verbatim output; do not rebase, merge or force on your own.
   - No permission, remote refused → stop and hand over the verbatim output.

## Confirmation

This turn already asks to commit or to commit and push → run steps 1 to 4 straight through. Only the line is wanted, with no commit → reply with that line alone and hand back to `commit-message`.

Stop on any of these and ask one question: unrelated changes staged, current branch is an integration branch, a force push is needed, or the target is `dev` / `release` / `main`. Ask, then stop.

## Visible reply

Field block: every line starts with `- `, the field name is bold and followed by a full-width colon, no blank lines inside a group, no code fence, no opening sentence and no closing summary outside the block.

On success:

```
- **Commit**: type(module): description
- **Files**: <staged paths, one line each>
- **Push**: <branch> → origin/<branch>
```

On failure, list only the steps that happened, then the failure fields:

```
- **Commit**: type(module): description
- **Failed**: <which step> `git ...`
- **Output**: <first line of the verbatim error>
- **To confirm**: <switch branch / pull first / fix the hook, which one>
```

When only asking, emit one line: `- **To confirm**: <question>`.

## Forbidden

- Do not bend the line to match the working tree, and do not edit code or delete assertions to satisfy a hook.
- Do not commit what is not part of this change, no `--no-verify`, no force, no `git reset --hard`.
- Do not push `dev` / `release` / `main`, do not create branches (`branch-create`), do not merge (`branch-merge`), do not slip in code changes.
