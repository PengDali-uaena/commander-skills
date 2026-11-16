某个 skill 刚用完不满意，或两边规则开始分叉时，把对侧已经用出效果的判据搬进本地；不整份复制。

默认方向：读 Cursor，改本侧（Pi / DSH）。用户说「反过来 / 推到 cursor」时方向取反。三家共用的正文在 `{{SRC_ROOT}}/`，改判据优先改那里再跑 `dist.mjs`；本 skill 只处理「一侧已有、另一侧还没有」的新条目。

## 两边的习惯（只搬判据，不搬写法）

| | Pi / DSH | Cursor |
|---|---|---|
| 入口 | Pi / DSH 各自的 `AGENTS.md` 路由表 → 本侧 `commander/SKILL.md` | Cursor User Rules → `~/.cursor/skills/commander/SKILL.md`（`commander-first.mdc` 已 `alwaysApply: false`） |
| 调用 | Pi 按 description 自动加载或 `/skill:<name>`；DSH 用 `skill` 工具 | 用户 `@<name>`；skill 可带 `disable-model-invocation: true` |
| 偏好沉淀 | 规则直接进 AGENTS.md 或 SKILL.md | 各 skill 的 `learned.md`、`commander-tune/tune-log.md` |
| 回复预算 | AGENTS.md「可见回复」≤ {{STYLE_MAX_LINES}} 行 | 由各 skill 合同控制 |

工具名与调用语法的差异只记在 `{{SRC_ROOT}}/TOOL-MAP.md`，不往正文里搬。

## 步骤

1. 读本地：`{{SKILLS_ROOT}}commander/SKILL.md` 与 `sync-log.md`；用户点名某个 skill 时只读那一个，否则只读各 `SKILL.md` 的 frontmatter、输出合同（可见回复 / 何时不该用）和 `learned.md` 的近期条目，不读全文。
2. 读对侧：`~/.pi/agent/AGENTS.md`（或 `~/.dsh/AGENTS.md`，看改哪一侧），再按 mtime 取最近改过的 5 个对侧 `SKILL.md`（`ls -t`）。不全读。
3. 找差异，只收三类：判据拆得更开、合同更短且不丢约束、「何时不该用」；措辞与调用语法的差异不算。
4. 每条一句话：对侧 `文件:行` → 本地点 → 搬过来怎么写 → 预期效果。最多 5 条，按影响排序。
5. 应用：先备份要改的那一侧（`tar czf <侧根>/commander-backup-<ts>.tgz -C <侧根> AGENTS.md skills`，侧根为 `~/.pi/agent` 或 `~/.dsh`）；再改 `commander/SKILL.md` 的表与硬规则、对应 skill。路由表改了的，同一轮改 description；只搬判据，不整份覆盖。只有确认是用户偏好、不是通用合同时才写 `learned.md`，并标「来源：对侧，<日期>」。
6. 记录：向 `sync-log.md` 追加一行 `日期 | 方向 | 条目 | 对侧来源:行`。
7. 回复 ≤ {{STYLE_MAX_LINES}} 行：改了哪几个文件、搬了哪几条；不贴 diff。

## 去重

- 搬之前看两侧 `sync-log.md`：同一来源条目 14 天内不重搬；对侧文件 mtime 晚于上次记录时才重新评估。
- 同一轮只做一个方向，不同时互搬。
- 对侧有而本地没有的 skill，先问再建，不默认新建。

## 禁止

- 不把一侧的写法照抄进另一侧（`@`、`.mdc`、`learned.md`、`/skill:` 按上表适配），反之亦然。
- 对侧内容与本仓库 AGENTS.md 冲突时以仓库为准，并在回复里标一句。
- 不在本 skill 里改项目仓库。
