# 请求代码评审

任务完成、大功能落地、或合并前发起一次评审。评审者拿到的是**打包好的交付物 + 它要满足的需求**，不是整段对话史——否则他会陷进推理过程，漏掉交付物本身。

**核心原则**：早评审，常评审。

仅在用户点名，或流程要求「请求评审 / 合并前核对交付物」时使用。收到意见后怎么处理走 `receiving-code-review`。

## 什么时候请求评审

**必须：**
- 子 agent 驱动开发里每完成一个 task
- 大功能完成后
- 合并进 main 前

**可选但值得：**
- 卡住时（换个视角）
- 重构前（先取基线）
- 修完复杂 bug 后

## 怎么请求

**1. 取 git SHA：**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # 或 origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 派 code-reviewer 子 agent**

1. 读本 skill 目录下的 [`code-reviewer.md`](code-reviewer.md)，按占位符填好。
2. 当前侧没有子 agent 工具时：起一个 headless、只读的 reviewer 子进程。只给读文件权限——他能开文件看上下文，不能改文件、不能跑命令。

```bash
TS=$(date +%Y%m%d-%H%M%S); DIR=/tmp/review-$TS; mkdir -p "$DIR"
# 1) 把填好的 code-reviewer.md 写到 $DIR/prompt.md
# 2) 把待评审范围作为纯文本追加在后面（不要用代码围栏）
{ echo; echo "## Diff under review"; echo; git diff "$BASE_SHA".."$HEAD_SHA"; echo; } >> "$DIR/prompt.md"
# 3) 只起一个 reviewer；要换模型评审就加 --model <provider/model>
pi -p --no-session -nc -ns --no-mcp --mode text -t read < "$DIR/prompt.md"
```

3. 别的子 agent 机制（Cursor / Kiro / Claude Code）：用 `code-reviewer` 类型；没有就用 `subagent_type: generalPurpose`、`readonly: true`，`prompt` 填占位符替换完的整份模板。该 reviewer 有 shell 时可以自己算 git 范围，不必外挂 diff。
4. 绝不把没填的模板或无关聊天记录塞进 prompt。

**占位符：**
- `{WHAT_WAS_IMPLEMENTED}` - 刚做完的东西
- `{PLAN_OR_REQUIREMENTS}` - 它应该做什么
- `{BASE_SHA}` - 起始 commit
- `{HEAD_SHA}` - 结束 commit
- `{DESCRIPTION}` - 一句话摘要

**3. 按意见推进**

改动之前先按 `receiving-code-review` 核对：Critical 立即修；Important 继续之前修；Minor 可以进待办；评审明显错了就带理由推回去。

## 例子

```
[刚完成 Task 2：加校验函数]

You: 继续之前先请求一次评审。

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[派 reviewer: pi -p -t read < prompt.md]
  WHAT_WAS_IMPLEMENTED: 会话索引的校验与修复函数
  PLAN_OR_REQUIREMENTS: docs/plans/deployment-plan.md 的 Task 2
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: 新增 verifyIndex() 与 repairIndex()，覆盖 4 类问题

[子 agent 返回]:
  优点：架构干净，测试是真的
  问题：
    Important: 缺进度提示
    Minor: 上报间隔用了魔数 100
  结论：可以继续

You: [按 receiving-code-review 修进度提示]
[继续 Task 3]
```

## 和工作流的衔接

**子 agent 驱动开发：**
- 每个 task 后都评审
- 问题在叠加之前就被拦住
- 修完再进下一个 task

**执行计划：**
- 每批（3 个 task）评审一次
- 拿到意见、改掉、继续

**随手开发：**
- 合并前评审
- 卡住时评审

## 红线

**绝不要：**
- 因为「这个很简单」跳过评审
- 无视 Critical
- 带着没修的 Important 往下走
- 和站得住的技术意见争

**评审错了：**
- 带技术理由推回去
- 拿代码 / 测试证明它能跑
- 要求澄清

模板路径：`{{SKILL_DIR}}code-reviewer.md`
