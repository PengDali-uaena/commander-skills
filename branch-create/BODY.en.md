# branch-create

Opens a new branch from dev or release and switches to it. Branch and switch only: no code changes, no commits, no push.

## When to use

- The user wants a new branch for a purpose, starting from dev or release.
- Renaming an existing branch, switching to an existing branch, or only changing code: does not apply.
- Creating a worktree: does not apply. That is the repo skill `git-worktree-creator` (named by the user, or when the artifact is a worktree).

## Decide first (never in the reply)

- **Base**: `origin/dev` by default. Only `hotfix` (urgent production fix) starts from `origin/release`. When the user says "both sides" or the change must also ship in the next release → two bases.
- **Naming**: `type/<version>_<branch-name>`. For example `feature/1.19.2_add-im-topcard`, `hotfix/1.19.1_fix-login-crash`.
- **type**: pick one by purpose, never two. If the repo already uses another prefix, keep it.
  - `feature`: new functionality, requirement, interaction change
  - `bugfix`: defect fix (verified on dev)
  - `hotfix`: urgent production fix (from release)
  - `refactor`: behavior-preserving restructuring, file splits
  - `perf`: performance work (first frame, jank, bundle size)
  - `chore`: dependencies, build, config, scripts, CI
  - `docs`: docs, comments, README
  - `test`: tests and fixtures
  - `experiment`: A/B experiments, rollout flags
  - When the purpose is vague, pick by blast radius; never invent a type. With nothing suitable, use `feature` (dev) or `hotfix` (release).
- **version**: from the base ref, not the working tree. Flutter: `version: 1.19.2+34` in `git show origin/<base>:pubspec.yaml` → `1.19.2`. Web: `version` in `package.json`. When unavailable, use `git describe --tags --abbrev=0 origin/<base>` and strip the `v`. Still nothing: ask one question, never invent. Keep digits and dots only — no `v`, no `+build`.
- **branch-name**: translate the business words of the purpose into English kebab-case, 3–5 words, all lowercase. No names, dates or ticket numbers. Purpose too vague ("optimize it") → ask one question about what changes.
- Repo has no `dev` / `release` (maybe `develop` / `main`): list `git branch -r`, ask one question, do not guess.
- Branch of that name exists: append `-2`, or ask whether to reuse. Never overwrite.

## Checks before creating

1. Run in the target repo root. If the user gave a path, cd there first. If the current directory is not a git repo → stop and ask for the path.
2. `git status --porcelain`: uncommitted changes → stop and ask "stash / commit first / bring them along". Never stash or commit automatically.
3. `git fetch origin --prune`. Use the remote base, never a local dev/release. If fetch fails, use the existing `origin/<base>` and state that it may be stale.
4. Confirm the remote base exists before creating.

## Creating

`--no-track` is mandatory. Without it the upstream points at dev/release and a later `git push` goes to the base. No `-f`, no `-B`, no push, no upstream, no commit.

```bash
git switch --no-track -c feature/<version>_<slug> origin/dev
git switch --no-track -c hotfix/<version>_<slug> origin/release
```

### Two bases

Create two branches only when the user explicitly asks for "both dev and release". Otherwise create one.

The dev side uses the type matching the purpose (defects use `bugfix`); the release side is always `hotfix`. Each side takes its own base version; do not force them to match. Switch to the hotfix side by default; if the user says where to stay, stay there.

```bash
git branch bugfix/<dev_version>_<slug> origin/dev
git switch --no-track -c hotfix/<release_version>_<slug> origin/release
```

## Confirmation

When the repo's rules require asking before creating a branch (e.g. the repo has its own branch permission table), propose first and create after. Skip confirmation only when the user already said "just create it / no need to ask". No confirmation, no branch.

## Visible reply

Only these lines, following `commander`'s "field-block layout": every line starts with `- `, the field name is bold, no blank lines between fields, no code fence, no text outside the block.

Before creating:

```
- **Branch**: feature/<version>_<slug>
- **Base**: origin/dev
- **To confirm**: create it?
```

After creating:

```
- **Branch**: feature/<version>_<slug>
- **Base**: origin/dev
- **Status**: created and switched
```

Two bases: write two `- **Branch**:` lines, consecutive with no blank line, then `- **Where**: <which side is checked out>`. On failure write only `- **Failed**:` plus the command and an error summary; do not guess the cause.

## Forbidden

- Never commit directly on dev / release, never delete branches, never force.
- Never switch with a dirty working tree. Never create without the user's confirmation.
