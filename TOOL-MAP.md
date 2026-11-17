# 工具与调用方式对照（Pi / DSH / Cursor / Codex / Claude Code）

公共 skill 的正文只有一份（源仓里的 `<name>/BODY.md`；正文里用 `{{SRC_ROOT}}` 指回源仓，克隆在哪都对）。各家允许出现的差异只有本表这两类；
正文里不写某一侧的路径或工具名，需要时用 `{{SKILL_DIR}}` / `{{SKILLS_ROOT}}` / `{{SRC_ROOT}}` 占位，由 `dist.mjs` 按侧替换。

| 能力 | Pi | DSH | Cursor | Codex | Claude Code |
|---|---|---|---|---|---|
| 读文件 | `read` | `read` | `Read` | `shell`（无独立读文件工具） | `Read` |
| 显式加载 skill | `/skill:<name>`，或 `read` 打开 SKILL.md | `skill` 工具 | `@<name>`，或 `Read` 打开 SKILL.md | 自动匹配或 skill 选择器 | `/<skill-name>` |
| 自动挂载 | 按 description 加载 | 按 description 加载 | 按 description，`disable-model-invocation: true` 可关 | 按 description 加载，超预算会先截短 description | 按 description 加载，`disable-model-invocation: true` 可关 |
| skill 根目录 | `~/.pi/agent/skills/<name>/` | `~/.dsh/skills/<name>/` | `~/.cursor/skills/<name>/` | `~/.agents/skills/<name>/` | `~/.claude/skills/<name>/` |
| 共享发现目录 | `~/.agents/skills`、`<repo>/.agents/skills` | 同左 | 同左，且顺带读 `~/.claude/skills`、`~/.codex/skills` | `<repo>/.agents/skills`（从 cwd 向上到仓库根）、`~/.agents/skills` | 不读 `.agents/skills` |
| 名字与目录名 | 不强制一致 | 未确认 | 必须一致 | 未确认（同名两份都会列出，不合并） | 目录名或 frontmatter `name` 决定命令名 |
| 步骤清单 | 无 todo 工具，步骤写在回复里 | `todo_write` | 可用 todo | 有（待验证） | 有（TodoWrite） |
| 派子 agent | 无内建，需 SDK / codemode | 未确认 | 可用 subagent | 无（待验证） | 可用 Task |
| 并行只读评审 | `pi -p` 子进程（同一脚本 `Promise.allSettled` 一次发） | 未验证 | subagent，只读、并行（待验证具体参数） | 无（待验证） | Task 并行（只读） |
| 用户级规则入口 | `~/.pi/agent/AGENTS.md` | `~/.dsh/AGENTS.md` | Cursor User Rules + `~/.cursor/rules/*.mdc` | `~/.codex/AGENTS.md` | `~/.claude/CLAUDE.md` |
| 本仓实测程度 | 完整 | 未验证 | 部分 | 未验证 | 未验证 |

正文里出现本表之外的第二类差异，说明该处其实不是 agent 差异，回正文统一写法。

## 不要写进正文

- 某一侧的绝对路径、工具名（`read` / `Read`）、显式调用语法（`/skill:` / `@` / `skill` 工具）。
- 「Pi 没有 X」「DSH 才有 Y」这类判断：写进本表，正文只写中立说法。
- 「Codex 会截短 description」这类行为差异：写进本表；正文只保证把触发条件写在 description 最前面。
