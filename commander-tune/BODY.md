# commander-tune

**一调用就跑会话审计**：先扫最近全部会话（跨所有仓库）里 commander 与各 skill 的实际调用与你的反馈，再结合本对话，给出问题清单和改法。不是只凭「这一轮聊了什么」下判断。

**本 skill 生效时**：不走路由 commander；本轮以本文件为准。

## 默认动作（按顺序，不跳过）

### 1. 跑审计脚本

```bash
python3 {{SKILL_DIR}}audit.py                # 默认近 14 天、全部仓库
python3 {{SKILL_DIR}}audit.py --days 30      # 扩大窗口
python3 {{SKILL_DIR}}audit.py --repo <name>  # 只看某个仓库（匹配会话目录名）
python3 {{SKILL_DIR}}audit.py --skill explain
```

脚本读某一侧的 `sessions/**/*.jsonl`（默认 Pi 的 `~/.pi/agent/sessions`，别的侧用 `--sessions`／`--skills` 指过去），输出：会话数与真实请求数、每个 skill 被读的轮次、调用后你下一条的反应（继续 / 打回）、同轮重复读、首句加粗 / 超 8 行 / 绝对路径比例、无 skill 轮次占比。

- 脚本缺失或报错：按下面「手工口径」用 `rg` / `python3 -c` 重算，**不得跳过证据直接给结论**。脚本是 pi 侧附属文件（同 `tune-log.md`，不进 `dist.mjs` 生成物），dsh / cursor 侧没有就走手工口径。
- **非 Pi 侧（Cursor / DSH）没有可解析的会话日志**：不要跑 pi 的 `audit.py`，改为以你贴的外部统计 + 本对话作证据，并在诊断首行标「样本来自用户提供」（无外部统计时就只审计本对话，并写明覆盖率有限）。
- 覆盖面：脚本只统计 Pi 会话（`~/.pi/agent/sessions`）。你贴了 Cursor / DSH 侧统计时，两边数字并排写；样本量小的那侧标「样本不足」。

### 2. 读现状（只读相关的）

| 顺序 | 路径 | 目的 |
|------|------|------|
| 1 | `{{SKILLS_ROOT}}commander/SKILL.md` | 路由表、硬约束、「接着上一轮」 |
| 2 | 审计里命中的下游 skill 的 `SKILL.md` | 该 skill 的 description 与「可见回复」合同 |
| 3 | `{{SKILL_DIR}}tune-log.md` 最近 3 条 | 避免重复提案、看上次未采纳项 |

不整目录扫：只读指标里出现异常（低调用 / 打回 / 格式违约）的那几个。

### 3. 判定口径

| 信号 | 结论 |
|---|---|
| 调用次数少，下一条是「继续 / 好的 / 执行」 | 场景稀有，**不动**，不删不并 |
| 调用后下一条打回（太长 / 不对 / 重新 / 看不懂） | 效果问题，**优先**修合同或收紧篇幅 |
| skill 被读但那一轮答案与不读时无差别 | 误触发，收窄触发面或从硬约束里摘掉名字 |
| 产物明确对上某行，却零调用 | 覆盖缺口，补路由行或把判据写进 commander |
| 同一轮里重复读同一 skill | 读取浪费，在 commander 顶部或该 skill 里点明「已在上下文不必重读」 |
| 首句不加粗 / 超 8 行 / 绝对路径多，且集中在无 skill 轮次 | 执行层问题，改文本收益低，写明观察项即可 |

次数少本身永远不算问题；被打开却无收益、被打开却被你要求缩短，才算。

### 4. 提案与落盘

变更清单每条写：**改哪**（文件 + 章节）、**改什么**（改前 → 改后）、**为什么**（对应上表哪一条信号，带数字）、**风险**（会不会误路由）。

- 默认只输出诊断 + 清单，末尾问一句：「按清单改吗？（是 / 否 / 只改第 N 条）」
- 你已说「直接改 / apply / 落盘」：只执行你明确同意的条目。
- 改由 `dist.mjs` 生成的 `SKILL.md` 无效：改 `{{SRC_ROOT}}/<name>/BODY.md`，再跑 `node {{SRC_ROOT}}/dist.mjs`，收尾跑 `--check`。
- 新增 skill：`{{SRC_ROOT}}/<kebab-name>/{BODY.md,META.json}` + commander 产物表加一行 + `dist.mjs`。
- 落盘后追加一节到 `{{SKILL_DIR}}tune-log.md`：日期、触发摘要、改了哪些文件、未采纳的提案。

## 手工口径（脚本不可用时）

```bash
# 1. 每轮读了哪些 skill（按会话逐条扫 toolCall 里的 skills/<name>/SKILL.md）
rg -o 'skills/[a-z0-9-]+/SKILL\.md' -N ~/.pi/agent/sessions | awk -F/ '{print $(NF-1)}' | sort | uniq -c | sort -rn

# 2. 某 skill 调用后你下一条说了什么（人工读回来判断是继续还是打回）
rg -n 'skills/explain/SKILL.md' ~/.pi/agent/sessions

# 3. 无 skill 轮次占比：先数会话里 role=user 的消息总数，再减掉读过 skill 的轮次
rg -c '"role":"user"' ~/.pi/agent/sessions | awk -F: '{s+=$2} END {print s}'
```

口径与脚本一致即可，数字要能对上；对不上就写明用哪种口径、为什么。

## 可见回复形状

自然段 + 列表，不要套「结论 / 依据 / 边界」模板：

1. 一两句：审计数字说明的主要问题（不是泛泛的「基本合理」）
2. **会话诊断**（3～8 条 bullet，每条带数字）
3. **变更清单**（编号，改哪 / 改什么 / 为什么 / 风险）
4. 一句确认问句（未授权落盘时）

用户只要「该用哪个 skill」式的一行答案时，仍先给审计结论，再补一行 `建议选用：<name>`。

## 与 commander 的边界

- **改 commander**：路由表、硬规则、「接着上一轮」、「分不清时只问一句」、优先级说明。
- **改下游 skill**：可见回复、递进层、读仓限额、禁止项；必要时加 `learned.md` 条目（注明来源对话摘要）。
- **不改**：仓库 `AGENTS.md`、项目规则目录、`skills-cursor/` 这类内建目录；跨 agent 同步走 `skill-sync`。

## 示例触发语

- `commander-tune`（默认扫近 14 天全部会话）
- `commander-tune --days 30 看看长期趋势`
- `commander-tune 上一轮应该走 code-logic 却加了日志`
- `commander-tune 直接改：产物表加「找文件」→ file-locate`
