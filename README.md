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
| en | 21 skills — every skill except `receiving-code-review` and `requesting-code-review`, whose bodies are already English |

Switching language overwrites the same `SKILL.md`, so re-render instead of keeping both side by
side — two languages in one skills directory collide by name.

`install.sh` records the chosen language in `.skill-lang` (gitignored), so later `dist.mjs` runs and
the pre-commit drift check keep using it without repeating `--lang`.

## Layout

```
<name>/BODY.md           # the text: criteria, flow, output contract — the only place to edit
<name>/BODY.<lang>.md    # localized body (e.g. BODY.en.md), optional
<name>/META.json         # per-agent frontmatter
<name>/META.<lang>.json  # localized frontmatter, optional
<name>/assets/**         # scripts and references, synced next to SKILL.md verbatim
install.sh               # one-shot installer: detects agents, creates dirs, renders, sets the hook
dist.mjs                 # renderer: BODY + META + assets -> per-agent skill directory
TOOL-MAP.md              # tool names and invocation syntax per agent; never inlined into a body
TOOL-MAP.en.md           # English version of the same table
VERSION                  # release number, printed by install.sh --version
```

`migrate.mjs`, `normalize.mjs` and `add-side.mjs` are one-off scripts from building this repo. They
are kept for traceability and are not needed day to day.

## Install

Treat this repo as the source directory: clone it to a fixed location, then let `dist.mjs` render the
bodies into your agent's skills directory.

```bash
git clone <repo-url> ~/.agents/skill-src
cd ~/.agents/skill-src && ./install.sh
```

`install.sh` detects which agents are installed, creates the skill directories it needs, renders them,
sets `core.hooksPath`, and re-runs the drift check at the end. Useful flags:

```bash
./install.sh --dry-run          # print what it would do
./install.sh --lang en          # render English
./install.sh --dirs agents,claude   # write only these (pi / cursor / dsh / agents / claude)
./install.sh --no-hooks         # leave git config alone
./install.sh --uninstall        # remove the generated files again (local skill files stay)
./install.sh --version          # print VERSION
```

Requirements: `bash` and `node` (>= 18). macOS, Linux and WSL are supported; native Windows is not —
`install.sh` is a bash script and the side directories are POSIX paths. Run it from WSL or Git Bash.

Where it writes when you pass no `--dirs`: a single detected agent gets its own directory; two or more
of Pi / Cursor / DSH get the shared `~/.agents/skills` (so one skill is not discovered twice); nothing
detected falls back to `~/.agents/skills`. `~/.claude/skills` is added whenever `~/.claude` exists,
because Claude Code reads no other location.

Rendering by hand works too — `dist.mjs` skips any target directory that does not exist:

```bash
node dist.mjs --lang en
node dist.mjs --check
```

By default it renders to the three locations below and skips any that do not exist. Override with
environment variables:

| Variable | Default output directory |
|---|---|
| `AGENTS_SKILLS_DIR` | `~/.agents/skills` (shared by Pi, Cursor and Codex) |
| `CLAUDE_SKILLS_DIR` | `~/.claude/skills` |
| `PI_SKILLS_DIR` | `~/.pi/agent/skills` |
| `DSH_SKILLS_DIR` | `~/.dsh/skills` |
| `CURSOR_SKILLS_DIR` | `~/.cursor/skills` |
| `SKILL_SRC` | `~/.agents/skill-src` (the source directory) |

Then let the agent rescan: `/reload` in Pi (also applies after editing a skill), or start a new
session. `/skill:<name>` loads a named skill directly.

Pi, Cursor and Codex all read `~/.agents/skills`, so `--dirs agents` is enough for all three.
Codex has no separate skills directory of its own; it also accepts a project `.agents/skills`.
Claude Code only reads `~/.claude/skills`, so add `claude` when you want it too.

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
| Tool names and invocation syntax | `TOOL-MAP.md` / `TOOL-MAP.en.md` (never in a body) |
| A skill only one agent has | that agent's skills directory, not this repo |

Two placeholders may appear in a body and are replaced per agent at render time:

- `{{SKILL_DIR}}` -> this skill's directory on that agent, e.g. `~/.pi/agent/skills/reply-brief/`
- `{{SKILLS_ROOT}}` -> that agent's skills root, e.g. `~/.pi/agent/skills/`

Editing a rendered `SKILL.md` or a file under `assets/` is a no-op: the next `dist.mjs` run overwrites
it and `--check` reports drift. Anything else in an agent's skill directory (`learned.md`,
`tune-log.md`, local notes) is yours and is never touched.

## Profile (your own defaults)

`profile.default.json` ships the defaults; `profile.local.json` (gitignored) overrides them per machine.
The renderer flattens both into placeholders — camelCase becomes `_`, so `style.maxLines` is
`{{STYLE_MAX_LINES}}`:

| Key | Placeholder | Default |
|---|---|---|
| `docPrefix` | `{{DOC_PREFIX}}` | `""` — document paths render as `docs/task-<date>-<feature>.md` |
| `style.maxLines` | `{{STYLE_MAX_LINES}}` | `8` — the reply line budget in the visible-reply contract |
| `style.maxBold` | `{{STYLE_MAX_BOLD}}` | `5` — how many bold spots a reply may carry |
| `lang` | — | `zh`; `--lang` wins |

```bash
echo '{"docPrefix":"myname-","style":{"maxLines":6}}' > profile.local.json
node dist.mjs
```

An undefined placeholder fails the render with the skill name and token, so a half-configured profile
never ships silently.

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

## Scope and limits

- Five sides are supported, but only Pi is verified in real sessions here. Cursor, Codex and Claude Code
  are verified at the directory and frontmatter level; `TOOL-MAP.md` marks each cell as measured or pending.
- Three skills — `multi-model-review`, `receiving-code-review`, `requesting-code-review` — need a second
  model or a subagent, so they ship for Pi only and are skipped when rendering Cursor/DSH.
- Those two review skills have no English body yet: `--lang en` falls back to Chinese and prints which
  skills fell back. `--strict` turns the fallback into an error.
- `prd-to-task` uses the codegraph MCP server and asks for Figma node IDs; without them it stops and asks
  instead of guessing.
- Uninstall: `./install.sh --uninstall` deletes exactly what `.generated` (a per-skill list `dist.mjs`
  writes) names on every side it installed to; files a skill owns locally (`learned.md`, `tune-log.md`) stay, and a skill directory is only
  removed when it is empty. The only thing written outside a skills directory is
  `git config core.hooksPath .githooks`, which `--uninstall` also clears.

## Layout notes

- `_template/` is the starting point for a new skill; directories starting with `_` are never rendered.
- `legacy/` holds one-off scripts from building the repo (the first migration and normalisation passes). They are kept for traceability and are not used day to day.
- `tools/verify.mjs` is the structural check: five-side frontmatter, heading parity between languages, placeholder definitions, leak scan.

## Contributing

See `CONTRIBUTING.md`. The short version: no personal or company information, agent differences only in
`TOOL-MAP.md`, one new row in `commander` per new skill, and `node tools/verify.mjs && node dist.mjs --check`
before pushing.

## License

MIT — see `LICENSE`.
