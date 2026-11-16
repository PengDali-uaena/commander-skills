[English](README.md) | **中文**

# commander-skills

一套给编码 agent 用的 skill：路由入口（commander）+ 每个动作一个 skill（找文件、讲代码路径、查故障、
写交接稿、拆需求、整理埋点、写 commit message 等）。

正文只写一份，`BODY.md` 是唯一源，`dist.mjs` 把它渲染成各 agent 侧可发现的 `SKILL.md`。
本仓不含任何个人信息、公司信息与密钥；机器相关的路径与仓库名一律由使用者在自己的规则文件里补。

## 适配状态

| Agent | 状态 | 说明 |
|---|---|---|
| Pi | 完整适配 | 目录、`/skill:` 命令、`{{SKILL_DIR}}` 附件、`disable-model-invocation` 均实机验证过 |
| Cursor | 部分适配 | 目录与 frontmatter 可用；附件路径与自动路由行为未逐条验证 |
| Codex | 未验证 | 按官方文档写了目录（`~/.agents/skills`）与 frontmatter，行为未实测 |
| Claude Code | 未验证 | 只认 `~/.claude/skills`，需单独一份；行为未实测 |

正文目前只有中文版；英文版与其余 agent 的实测按需补。

## 目录

```
<name>/BODY.md     # 正文（判据、流程、输出合同），唯一要改的地方
<name>/META.json   # 每一侧的 frontmatter（name / description / 开关）
dist.mjs           # 渲染器：BODY.md + META.json → 各侧 SKILL.md
TOOL-MAP.md        # 各侧工具名与显式调用方式的对照，正文里不写某侧的写法
```

`migrate.mjs`、`normalize.mjs`、`add-side.mjs` 是建立本仓时的一次性脚本，保留只为可追溯，日常不用。

## 安装

本仓按「源目录」使用：clone 到一个固定位置，再让 `dist.mjs` 把正文渲染进 agent 的 skills 目录。

```bash
git clone <repo-url> ~/.agents/skill-src
node ~/.agents/skill-src/dist.mjs
```

默认输出三侧，目标目录不存在就跳过；想换位置用环境变量覆盖：

| 环境变量 | 默认输出目录 |
|---|---|
| `PI_SKILLS_DIR` | `~/.pi/agent/skills` |
| `DSH_SKILLS_DIR` | `~/.dsh/skills` |
| `CURSOR_SKILLS_DIR` | `~/.cursor/skills` |
| `SKILL_SRC` | `~/.agents/skill-src`（源目录） |

渲染完让 agent 重新扫描：Pi 里 `/reload`（改 skill 后同样适用），或重开一次会话。
`/skill:<name>` 可以直接点名加载某个 skill。

Pi、Cursor、Codex 都读 `~/.agents/skills`，想只维护一份就把它当唯一目标（`PI_SKILLS_DIR=~/.agents/skills` 之类）；
Claude Code 只认 `~/.claude/skills`，要支持它就再渲染一份。默认仍按上表三处输出，可按需覆盖。

只装一侧也可以，把不需要的变量指向不存在的目录即可跳过，例如：

```bash
CURSOR_SKILLS_DIR= DSH_SKILLS_DIR= node dist.mjs
```

## 更新与检查

```bash
git -C ~/.agents/skill-src pull
node ~/.agents/skill-src/dist.mjs
node ~/.agents/skill-src/dist.mjs --check   # 生成物与 BODY.md 不一致时非 0 退出
```

`--check` 适合挂进 CI 或 pre-commit：它只比对，不写文件。

## 改哪里

| 想改的 | 改这里 |
|---|---|
| 判据 / 流程 / 输出合同 | `<name>/BODY.md` |
| 某一侧的 frontmatter（description 语言、`disable-model-invocation`） | `<name>/META.json` |
| 工具名 / 显式调用方式 | `TOOL-MAP.md`（不写进 BODY） |
| 只有某一侧才有的 skill | 各自的 skills 目录，不进本仓 |

`BODY.md` 里可写两个占位符，渲染时按侧替换：

- `{{SKILL_DIR}}` → 本 skill 在该侧的目录，如 `~/.pi/agent/skills/reply-brief/`
- `{{SKILLS_ROOT}}` → 该侧 skills 根目录，如 `~/.pi/agent/skills/`

直接改各侧的 `SKILL.md` 属于无效修改：下一次 `dist.mjs` 会覆盖，`--check` 也会报 drift。
各侧目录里除 `SKILL.md` 之外的附件（脚本、`references/`）由各侧自己维护，跨侧共用时请提 PR 进本仓。

## 提交前自查

```bash
git config core.hooksPath .githooks   # 启用一次即可
```

`.githooks/pre-commit` 做两件事：扫个人信息 / 公司信息 / 密钥类关键词（命中即拦），
以及跑 `dist.mjs --check`（改了 BODY 忘了重跑就拦）。

## 说明

skill 只是提示词层：它不执行代码，也不承诺安全边界。引入别人的 skill 前先读一遍正文和它附带的脚本。
各侧行为差异只允许出现在 `TOOL-MAP.md` 那张表里；正文里出现某一侧的路径或工具名就是 bug。
