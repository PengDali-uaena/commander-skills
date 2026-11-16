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

正文默认中文，另有英文版的 skill 见下方「语言」。

## 语言

翻译放在原文旁边：正文 `BODY.<lang>.md`，对应的 frontmatter 放 `META.<lang>.json`。渲染时按语言选取，没有对应语言版的 skill 回落中文。

```bash
node dist.mjs --lang en            # 渲染英文，缺英文版的逐个回落中文
node dist.mjs --lang en --strict   # 缺英文版就非 0 退出，不回落
SKILL_LANG=en node dist.mjs        # 同一个开关的环境变量写法
```

| 语言 | 覆盖 |
|---|---|
| zh（默认） | 全部 23 个 skill |
| en | 21 个，只有 `receiving-code-review`、`requesting-code-review` 没有英文版（正文原本就是英文） |

切语言是覆盖同一个 `SKILL.md`，所以要用重渲染而不是两种语言并存——同一个 skills 目录里两种语言会同名冲突。

`install.sh` 会把选定的语言写进 `.skill-lang`（已 gitignore），之后 `dist.mjs` 与预提交的漂移检查都沿用它，不用每次带 `--lang`。

## 目录

```
<name>/BODY.md           # 正文（判据、流程、输出合同），唯一要改的地方
<name>/BODY.<lang>.md    # 译文正文，可选（如 BODY.en.md）
<name>/META.json         # 每一侧的 frontmatter（name / description / 开关）
<name>/META.<lang>.json  # 译文 frontmatter，可选
<name>/assets/**         # 脚本与 references，原样同步到 SKILL.md 旁边
install.sh               # 一键安装：探测 agent、建目录、渲染、设 hook
dist.mjs                 # 渲染器：BODY + META + assets → 各侧 skill 目录
TOOL-MAP.md              # 各侧工具名与显式调用方式的对照，正文里不写某侧的写法
TOOL-MAP.en.md           # 同一张表的英文版
VERSION                  # 版本号，install.sh --version 读取
```

`migrate.mjs`、`normalize.mjs`、`add-side.mjs` 是建立本仓时的一次性脚本，保留只为可追溯，日常不用。

## 安装

本仓按「源目录」使用：clone 到一个固定位置，再让 `dist.mjs` 把正文渲染进 agent 的 skills 目录。

```bash
git clone <repo-url> ~/.agents/skill-src
cd ~/.agents/skill-src && ./install.sh
```

`install.sh` 会探测本机装了哪些 agent、建出需要的 skill 目录、渲染、设 `core.hooksPath`，最后再跑一次漂移检查。常用参数：

```bash
./install.sh --dry-run               # 只打印将要做什么
./install.sh --lang en               # 渲染英文
./install.sh --dirs agents,claude    # 只写这两处（pi / cursor / dsh / agents / claude）
./install.sh --no-hooks              # 不动 git 配置
./install.sh --uninstall             # 撤掉生成物（本机自有文件不动）
./install.sh --version               # 打印 VERSION
```

不给 `--dirs` 时的落点规则：只探测到一个 agent 就写它自己的目录；Pi / Cursor / DSH 探到两个及以上就写共享的
`~/.agents/skills`（避免同一个 skill 被两个目录各发现一次）；一个都没探到也回落到 `~/.agents/skills`。
只要 `~/.claude` 存在就额外写 `~/.claude/skills`，因为 Claude Code 不读别的位置。

也可以手工渲染，`dist.mjs` 会跳过不存在的目标目录：

```bash
node dist.mjs --lang en
node dist.mjs --check
```

| 环境变量 | 默认输出目录 |
|---|---|
| `AGENTS_SKILLS_DIR` | `~/.agents/skills`（Pi / Cursor / Codex 共用） |
| `CLAUDE_SKILLS_DIR` | `~/.claude/skills` |
| `PI_SKILLS_DIR` | `~/.pi/agent/skills` |
| `DSH_SKILLS_DIR` | `~/.dsh/skills` |
| `CURSOR_SKILLS_DIR` | `~/.cursor/skills` |
| `SKILL_SRC` | `~/.agents/skill-src`（源目录） |

渲染完让 agent 重新扫描：Pi 里 `/reload`（改 skill 后同样适用），或重开一次会话。
`/skill:<name>` 可以直接点名加载某个 skill。

Pi、Cursor、Codex 都读 `~/.agents/skills`，所以 `--dirs agents` 一份就够三家；Codex 没有自己独立的 skills 目录，
项目内也认 `.agents/skills`。Claude Code 只认 `~/.claude/skills`，需要它就加上 `claude`。

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
| 工具名 / 显式调用方式 | `TOOL-MAP.md` / `TOOL-MAP.en.md`（不写进 BODY） |
| 只有某一侧才有的 skill | 各自的 skills 目录，不进本仓 |

`BODY.md` 里可写两个占位符，渲染时按侧替换：

- `{{SKILL_DIR}}` → 本 skill 在该侧的目录，如 `~/.pi/agent/skills/reply-brief/`
- `{{SKILLS_ROOT}}` → 该侧 skills 根目录，如 `~/.pi/agent/skills/`

直接改各侧的 `SKILL.md` 或 `assets/` 下的文件属于无效修改：下一次 `dist.mjs` 会覆盖，`--check` 也会报 drift。
各侧目录里其它文件（`learned.md`、`tune-log.md`、本机笔记）属于你自己，渲染不会碰。

## profile（本机默认值）

`profile.default.json` 是进仓的默认值，`profile.local.json`（已 gitignore）按机器覆盖。渲染器把两者拍平成占位符，
camelCase 会变成 `_`，所以 `style.maxLines` 对应 `{{STYLE_MAX_LINES}}`：

| 键 | 占位符 | 默认值 |
|---|---|---|
| `docPrefix` | `{{DOC_PREFIX}}` | `""`，文档路径渲染成 `docs/task-<date>-<feature>.md` |
| `style.maxLines` | `{{STYLE_MAX_LINES}}` | `8`，可见回复的行数预算 |
| `style.maxBold` | `{{STYLE_MAX_BOLD}}` | `5`，一条回复最多几处加粗 |
| `lang` | — | `zh`；`--lang` 优先 |

```bash
echo '{"docPrefix":"myname-","style":{"maxLines":6}}' > profile.local.json
node dist.mjs
```

占位符没定义时渲染直接报错并点名 skill 与 token，不会把半配置的产物悄悄发出去。

## 提交前自查

```bash
git config core.hooksPath .githooks   # 启用一次即可
```

`.githooks/pre-commit` 做两件事：扫个人信息 / 公司信息 / 密钥类关键词（命中即拦），
以及跑 `dist.mjs --check`（改了 BODY 忘了重跑就拦）。

## 说明

skill 只是提示词层：它不执行代码，也不承诺安全边界。引入别人的 skill 前先读一遍正文和它附带的脚本。
各侧行为差异只允许出现在 `TOOL-MAP.md` 那张表里；正文里出现某一侧的路径或工具名就是 bug。

## 适用范围与已知限制

- 支持五侧，但真实会话里只验证过 Pi。Cursor / Codex / Claude Code 只验证到「目录与 frontmatter 能落」，
  `TOOL-MAP.md` 里逐格标了「已验证 / 未验证」。
- `multi-model-review`、`receiving-code-review`、`requesting-code-review` 需要第二个模型或子 agent，
  所以只分发给 Pi，渲染 Cursor / DSH 时跳过。
- 后两个 review skill 还没有英文正文：`--lang en` 会回落中文并打印回落清单；`--strict` 让回落直接报错。
- `prd-to-task` 依赖 codegraph MCP，并会要 Figma node-id；没有这两个工具时它停下来问，不猜。
- 卸载：`./install.sh --uninstall` 会清掉它写过的各侧 `SKILL.md` 与 `assets/`；本机自有文件（`learned.md`、
  `tune-log.md`）保留，目录空了才删。除 skills 目录外只写过一个东西——`git config core.hooksPath .githooks`，
  `--uninstall` 也会把它清掉。

## 目录约定

- `_template/` 是新增 skill 的起点；以 `_` 开头的目录不会被渲染。
- `legacy/` 放建仓时的一次性脚本（最初的迁移与归一化），只为可追溯，日常不用。
- `tools/verify.mjs` 是结构自检：五侧 frontmatter、两语文档的标题树一致、占位符有定义、敏感词扫描。

## 贡献

见 `CONTRIBUTING.md`。短版：不带个人信息与公司信息；agent 差异只写进 `TOOL-MAP.md`；每加一个 skill 就在
`commander` 里加一行；推之前跑 `node tools/verify.mjs && node dist.mjs --check`。

## 许可证

MIT，见 `LICENSE`。
