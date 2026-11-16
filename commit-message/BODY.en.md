# commit-message

From the part of the conversation that belongs to this change, write one line of English commit message. Do not read the working tree, do not run `git diff`, `git status` or `git log`, and do not open files to make up the sentence. Do not compress the whole chat into it, and leave out topics that are not part of this change.

## Format

The whole line is:

```
type(module): description
```

No extra brackets around type.

- Pick `type` from these 8 only:

| type | Use for |
|---|---|
| `feat` | New functionality, entry point or capability |
| `fix` | Fixing a bug, a regression or wrong behavior |
| `refactor` | Same behavior, different structure / layering / naming |
| `opt` | Same behavior, better experience through implementation; any optimization whose gain you cannot quantify goes here |
| `perf` | Performance work with a measurable gain: latency, bundle size, memory |
| `docs` | Documentation, issues, design notes |
| `style` | CSS / formatting / copy only, no logic change |
| `chore` | Config, logs, dependencies, build / CI scripts, temporary scaffolding |

- Mixed change: pick by the largest change the user can perceive, `feat` > `fix` > `refactor` > `opt` / `perf` > `docs` > `style` > `chore`. The only difference between `opt` and `perf` is whether the gain is quantified.
- If the conversation already used another type, keep that word instead of inventing one; `feature` maps to `feat`, `bugfix` maps to `fix`, and `patch` is no longer used.
- `module` is the module this change touches, written as a short English word using the conversation's naming. For several modules, write what they have in common instead of listing them.
- `description` is one English sentence about the change itself. No period, no second sentence.

If type or module cannot be told from the conversation: ask one question only, do not guess, and do not read the repo for it.

## Visible reply

Only that line: no code fence, no quotes, nothing before or after.

```
fix(live-drawer): keep the native player when a transparent popup covers the home page
```

The example only shows the shape. type, module and description must come from the current conversation.

If the user explicitly asks in the same message to commit: use this line as the message and commit. Still do not rewrite the line from the working tree. Do not push, and do not use `--no-verify`.
