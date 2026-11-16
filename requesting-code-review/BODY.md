# Requesting Code Review

在任务完成、大功能落地或合并前，主动发起审查。给 reviewer 的是**精心打包的工作产物与需求对照**，不是整段会话历史，避免 reviewer 陷入思路而漏看交付物。

**Core principle:** Review early, review often.

仅在用户显式点名、或 workflow 要求「request review / 合并前审查交付」时使用。收到审查意见后的处理流程走 `receiving-code-review`。

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. Dispatch code-reviewer subagent**

1. 读本 skill 同目录 [`code-reviewer.md`](code-reviewer.md)，填入占位符。
2. Pi（没有 Task/Subagent 工具）：跑一个 headless、只读的 reviewer 子进程，`-t read` 是只读工具集——reviewer 能打开文件看上下文，不能改文件、不能跑命令。

```bash
TS=$(date +%Y%m%d-%H%M%S); DIR=/tmp/review-$TS; mkdir -p "$DIR"
# 1) 填好的 code-reviewer.md 写进 $DIR/prompt.md
# 2) 把待审 range 以纯文本 append 进去（不要包代码围栏）
{ echo; echo "## Diff under review"; echo; git diff "$BASE_SHA".."$HEAD_SHA"; echo; } >> "$DIR/prompt.md"
# 3) 只跑一个 reviewer；换模型审查加 --model <provider/model>
pi -p --no-session -nc -ns --no-mcp --mode text -t read < "$DIR/prompt.md"
```

3. 有其他 subagent 机制（Cursor / Kiro / Claude Code）：用 `code-reviewer` 类型；否则 `subagent_type: generalPurpose`、`readonly: true`，`prompt` 为填好占位符后的模板全文。该 reviewer 有 shell 时可以自己算 git range，不靠 append 的 diff。
4. 勿把未填写的模板或无关聊天记录塞进 prompt。

**Placeholders:**
- `{WHAT_WAS_IMPLEMENTED}` - What you just built
- `{PLAN_OR_REQUIREMENTS}` - What it should do
- `{BASE_SHA}` - Starting commit
- `{HEAD_SHA}` - Ending commit
- `{DESCRIPTION}` - Brief summary

**3. Act on feedback**

按 `receiving-code-review` 核实后再改：Critical 立即修；Important 再继续；Minor 可记 backlog；reviewer 明显错时可带理由 push back。

## Example

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch reviewer: pi -p -t read < prompt.md]
  WHAT_WAS_IMPLEMENTED: Verification and repair functions for conversation index
  PLAN_OR_REQUIREMENTS: docs/plans/deployment-plan.md 的 Task 2
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators per receiving-code-review]
[Continue to Task 3]
```

## Integration with Workflows

**Subagent-Driven Development:**
- Review after EACH task
- Catch issues before they compound
- Fix before moving to next task

**Executing Plans:**
- Review after each batch (3 tasks)
- Get feedback, apply, continue

**Ad-Hoc Development:**
- Review before merge
- Review when stuck

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

模板路径：`{{SKILL_DIR}}code-reviewer.md`
