**English** | [中文](README.zh-CN.md)

# commander-skills

A set of skills for coding agents: one router (`commander`) plus one skill per action — find a file,
explain a code path, diagnose a failure, write a handoff, split a PRD, format analytics events,
write a commit message, and so on.

The text lives in exactly one place. `BODY.md` is the single source; `dist.mjs` renders it into the
`SKILL.md` files each agent discovers. This repo contains no personal or company information and no
secrets — machine-specific paths and repository names belong in your own rules file.

## Agent support

| Agent | Status | Notes |
|---|---|---|
| Pi | Full | Skill dirs, `/skill:` commands, `{{SKILL_DIR}}` attachments and `disable-model-invocation` all verified in practice |
| Cursor | Partial | Directory layout and frontmatter work; attachment paths and auto-routing not verified case by case |
| Codex | Unverified | Directory (`~/.agents/skills`) and frontmatter follow the official docs; behavior untested |
| Claude Code | Unverified | Only reads `~/.claude/skills`, so it needs a second copy; behavior untested |

Skill bodies are Chinese by default, with English available for the skills listed under Languages.

## Languages

A localized body sits next to the original as `BODY.<lang>.md`, with its own frontmatter in
`META.<lang>.json`. The renderer picks the language per run; a skill with no localized body falls
back to Chinese.

```bash
node dist.mjs --lang en            # render English, fall back to Chinese per skill
node dist.mjs --lang en --strict   # exit non-zero instead of falling back
SKILL_LANG=en node dist.mjs        # same via environment variable
```

| Language | Coverage |
|---|---|
| zh (default) | all 23 skills |
| en | commander, reply-brief, file-locate, code-logic, commit-message, bugfix-probe, coding-handoff-plan, coding-handoff-execute |

Switching language overwrites the same `SKILL.md`, so re-render instead of keeping both side by
side — two languages in one skills directory collide by name.

## Layout

```
<name>/BODY.md     # the text: criteria, flow, output contract — the only place to edit
<name>/META.json   # per-agent frontmatter (name / description / flags)
dist.mjs           # renderer: BODY.md + META.json -> per-agent SKILL.md
TOOL-MAP.md        # tool names and invocation syntax per agent; never inlined into a body
```

`migrate.mjs`, `normalize.mjs` and `add-side.mjs` are one-off scripts from building this repo. They
are kept for traceability and are not needed day to day.

## Install

Treat this repo as the source directory: clone it to a fixed location, then let `dist.mjs` render the
bodies into your agent's skills directory.

```bash
git clone <repo-url> ~/.agents/skill-src
node ~/.agents/skill-src/dist.mjs
```

By default it renders to the three locations below and skips any that do not exist. Override with
environment variables:

| Variable | Default output directory |
|---|---|
| `PI_SKILLS_DIR` | `~/.pi/agent/skills` |
| `DSH_SKILLS_DIR` | `~/.dsh/skills` |
| `CURSOR_SKILLS_DIR` | `~/.cursor/skills` |
| `SKILL_SRC` | `~/.agents/skill-src` (the source directory) |

Then let the agent rescan: `/reload` in Pi (also applies after editing a skill), or start a new
session. `/skill:<name>` loads a named skill directly.

Pi, Cursor and Codex all read `~/.agents/skills`, so point every variable at that one directory if
you want a single copy (`PI_SKILLS_DIR=~/.agents/skills CURSOR_SKILLS_DIR=~/.agents/skills ...`).
Claude Code only reads `~/.claude/skills`, so supporting it means rendering a second copy.

Installing a single agent is fine too — point the unused variables at a directory that does not
exist and those sides are skipped:

```bash
CURSOR_SKILLS_DIR= DSH_SKILLS_DIR= node dist.mjs
```

## Update and check

```bash
git -C ~/.agents/skill-src pull
node ~/.agents/skill-src/dist.mjs
node ~/.agents/skill-src/dist.mjs --check   # exits non-zero when output drifted from BODY.md
```

`--check` only compares, never writes — suitable for CI or a pre-commit hook.

## What to edit

| Goal | Edit |
|---|---|
| Criteria, flow, output contract | `<name>/BODY.md` |
| One agent's frontmatter (description language, `disable-model-invocation`) | `<name>/META.json` |
| Tool names and invocation syntax | `TOOL-MAP.md` (never in a body) |
| A skill only one agent has | that agent's skills directory, not this repo |

Two placeholders may appear in a body and are replaced per agent at render time:

- `{{SKILL_DIR}}` -> this skill's directory on that agent, e.g. `~/.pi/agent/skills/reply-brief/`
- `{{SKILLS_ROOT}}` -> that agent's skills root, e.g. `~/.pi/agent/skills/`

Editing a rendered `SKILL.md` is a no-op: the next `dist.mjs` run overwrites it and `--check` reports
drift. Files other than `SKILL.md` in an agent's skill directory (scripts, `references/`) are owned by
that agent; to share them across agents, send a PR here.

## Before you commit

```bash
git config core.hooksPath .githooks   # once per clone
```

`.githooks/pre-commit` does two things: scans for personal / company / secret-like keywords (blocks
the commit on a hit) and runs `dist.mjs --check` (blocks when a body changed without re-rendering).

## Notes

A skill is prompt layer only: it runs no code and makes no security promises. Read the body and any
bundled scripts before adopting someone else's skill.

Agent differences are allowed only in the `TOOL-MAP.md` table. An agent-specific path or tool name
inside a body is a bug.
