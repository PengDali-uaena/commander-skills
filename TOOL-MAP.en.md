# Tool and invocation differences (Pi / DSH / Cursor / Codex / Claude Code)

A shared skill body exists once, in the source repo (`<name>/BODY.md`; a body points back at the repo with
`{{SRC_ROOT}}`, so it works wherever the repo is cloned). Only the two kinds of difference listed here are
allowed to vary per agent. A body never names one side's path or tool; use `{{SKILL_DIR}}`, `{{SKILLS_ROOT}}`
or `{{SRC_ROOT}}` and let `dist.mjs` substitute them per side.

| Capability | Pi | DSH | Cursor | Codex | Claude Code |
|---|---|---|---|---|---|
| Read a file | `read` | `read` | `Read` | `shell` (no dedicated read tool) | `Read` |
| Explicit skill load | `/skill:<name>`, or `read` the SKILL.md | `skill` tool | `@<name>`, or `Read` the SKILL.md | matching or the skill picker | `/<skill-name>` |
| Auto mount | loads by description | loads by description | by description; `disable-model-invocation: true` disables it | loads by description, shortens long ones first | by description; `disable-model-invocation: true` disables it |
| Skill root | `~/.pi/agent/skills/<name>/` | `~/.dsh/skills/<name>/` | `~/.cursor/skills/<name>/` | `~/.agents/skills/<name>/` | `~/.claude/skills/<name>/` |
| Shared discovery dirs | `~/.agents/skills`, `<repo>/.agents/skills` | same | same, plus `~/.claude/skills`, `~/.codex/skills` | `<repo>/.agents/skills` (upwards from cwd), `~/.agents/skills` | does not read `.agents/skills` |
| Name vs directory | not enforced | unconfirmed | must match | unconfirmed (two copies with the same name are both listed, never merged) | the directory name or the frontmatter `name` decides the command |
| Step list | no todo tool; steps go in the reply | `todo_write` | todo available | available (unverified) | available (TodoWrite) |
| Subagents | none built in; needs the SDK / codemode | unconfirmed | subagent available | none (unverified) | Task available |
| Parallel read-only review | `pi -p` subprocesses (all fired in one script via `Promise.allSettled`) | unverified | subagent, read-only, parallel (exact knobs unverified) | none (unverified) | parallel Task, read-only |
| User-level rules | `~/.pi/agent/AGENTS.md` | `~/.dsh/AGENTS.md` | Cursor User Rules + `~/.cursor/rules/*.mdc` | `~/.codex/AGENTS.md` | `~/.claude/CLAUDE.md` |
| Verified here | fully | not verified | partially | not verified | not verified |

If a body carries a difference outside this table, that is not an agent difference — unify the wording instead.

## Never put these in a body

- One side's absolute path, tool name (`read` / `Read`) or explicit-load syntax (`/skill:` / `@` / a `skill` tool).
- Claims like "Pi has no X" or "only DSH has Y": those belong in this table; a body uses neutral wording.
- Behavioural quirks such as "Codex shortens descriptions": recorded here; a body only guarantees that the
  trigger conditions come first in the description.
