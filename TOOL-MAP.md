# 工具与调用方式对照（Pi / DSH / Cursor）

公共 skill 的正文只有一份（`~/.agents/skill-src/<name>/BODY.md`）。三家允许出现的差异只有本表这两类；
正文里不写某一侧的路径或工具名，需要时用 `{{SKILL_DIR}}` / `{{SKILLS_ROOT}}` 占位，由 `dist.mjs` 按侧替换。

| 能力 | Pi | DSH | Cursor |
|---|---|---|---|
| 读文件 | `read` | `read` | `Read` |
| 显式加载 skill | `/skill:<name>`，或 `read` 打开 SKILL.md | `skill` 工具 | `@<name>`，或 `Read` 打开 SKILL.md |
| 自动挂载 | 按 description 加载 | 按 description 加载 | 按 description，`disable-model-invocation: true` 可关 |
| skill 根目录 | `~/.pi/agent/skills/<name>/` | `~/.dsh/skills/<name>/` | `~/.cursor/skills/<name>/` |
| 共享发现目录 | `~/.agents/skills`、`<repo>/.agents/skills` | 同左 | 同左 |
| 步骤清单 | 无 todo 工具，步骤写在回复里 | `todo_write` | 可用 todo |
| 派子 agent | 无内建，需 SDK / codemode | 未确认 | 可用 subagent |
| 用户级规则入口 | `~/.pi/agent/AGENTS.md` | `~/.dsh/AGENTS.md` | Cursor User Rules + `~/.cursor/rules/*.mdc` |

正文里出现本表之外的第二类差异，说明该处其实不是 agent 差异，回正文统一写法。

## 不要写进正文

- 某一侧的绝对路径、工具名（`read` / `Read`）、显式调用语法（`/skill:` / `@` / `skill` 工具）。
- 「Pi 没有 X」「DSH 才有 Y」这类判断：写进本表，正文只写中立说法。
