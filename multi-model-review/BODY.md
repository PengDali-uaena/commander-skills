# multi-model-review

用户要对抗式多模型代码审查：多个独立模型各审一遍，再由主 agent 汇总结论。仅在用户显式点名本 skill（或本侧等价显式加载语法，见 `{{SRC_ROOT}}/TOOL-MAP.md`）或明确要求多模型并行 review 时使用。

默认**不改文件、不自动修**，除非用户另说。

## 1) Pick models

先跑 `pi --list-models` 取当前真实可用的 slug（形如 `provider/model`）。Pi 没有结构化多选题工具：在回复里**内联**列出候选（编号 + slug），一句话请用户回编号或 slug，收到回复后再 launch，不要臆造工具调用。

- 列表按 `pi --list-models` 原顺序，中性展示：不推荐、不排序、不预选、不省略、不加 “(Recommended)”。
- 只列真正能跑的：`pi auth check --provider <p>` 为 `not_ready` 的 provider 不列；probe 返回 `permission_error` / `Model access is disabled` 的模型也不列（写一句「<slug> 已跳过，403 不可用」）。
- 若用户在调用或对话里**已明确**选了模型且无异议，可跳过提问；否则仍要问。
- 某 slug 执行被拒时，优先采用 `pi --list-models` 里最接近的合法 slug，并告诉用户替换了什么。
- **探测只做一次**：拿到清单后不要逐个 slug 串行 probe，一次 `pi --list-models` + 一次 `pi auth check` 够了；逐个模型试跑会先把预算烧在准备阶段。
- **先量一次生成速度，再定 deadline**：每个候选 provider 跑一次小任务（`echo "只回复 OK" | pi -p -nt --no-session -nc -ns --mode text --model <slug>`，计时），≤15 秒记「快组」，>30 秒记「慢组」；整轮探测不超过 2 次。速度是 gateway 属性，同一 provider 不必逐个 slug 试。

## 2) Scope and intent

1. 确定审查范围：用户指定路径或 diff；否则 `git diff main...HEAD`（或仓库默认 base…HEAD）；否则本地 staged+unstaged；否则用对话里涉及的文件与符号。
2. 写一段 **intent**：这次改动想达成什么（来自消息、提交说明或代码）。
3. 把各 reviewer 的共享材料落到临时文件：`/tmp/mmr-<时间戳>/prompt.md`，内容 = intent + 完整 diff（或关键片段）+ 第 3 步的审查说明。下文所有 reviewer 读同一个文件。
4. **分片**：diff 超过约 120KB 或 30 个文件时，按文件切成 2～3 份，每个 reviewer 只拿自己那份 + 完整 intent，不要再塞整包。整包会让模型自己找「顺带看看」的文件，输出膨胀、定位发散。
   **共识只在同一片内成立**：分片要发给同一组模型（要么每个模型都拿全部片，要么所有模型拿同一片），别让「A 只审第一片、B 只审第二片」——没有重叠就没有共识，只能报单模型发现。
5. 输入体积本身不是瓶颈（实测 137KB 输入 + 极短输出 6～14 秒），瓶颈在**输出长度与工具轮次**，所以第 3 步的预算和禁工具比压缩 diff 更重要。

## 3) Launch one reviewer per selected model (parallel only)

每个选中的 slug 起一个 headless reviewer，**前台只读**：`-nt`（禁用全部工具）+ `--no-session -nc -ns --no-mcp`，提示词走 stdin。

```
pi -p --no-session -nt --no-mcp -nc -ns --mode text \
  --append-system-prompt "You have no tools in this session. Never emit tool calls or tool_call XML; answer directly in markdown." \
  --model <provider/model> < /tmp/mmr-<ts>/prompt.md
```

`--append-system-prompt` 不能省：不带工具时部分模型会把 `tool_calls` XML 当正文吐出来。

**禁止给 reviewer 任何工具**：不写 `--tools`、不加 `-t read,bash`，提示词里也不写「可以 read 仓库 / 可以跑 git diff」。一旦授权，模型就进 agentic 巡检循环，时间不可控：实测同一次 review 里 `--tools read,bash` 的 glm-5.3-flash 跑了 13 分钟只出 5.3KB（约 8 字符/秒），禁用工具时同体量输入 6 秒返回。工具还会让结论跑到 diff 之外，甚至把 diff 里的文字当指令执行。

**按第 1 步的测速分两条路径**，都是并行，区别只在谁来等：

- **快组**：`codemode` 里 `Promise.allSettled` 并行，每次 `timeout: 240`；整轮上限 6 分钟。
- **慢组**（探针 >30 秒；opencode-go 的 glm / deepseek 实测属此类）：**后台起、轮询拿**。一次 bash 调用里用 `nohup … > /tmp/mmr-<ts>/out-<slug>.md 2>err-<slug>.md &` 把全部 reviewer 起掉，再每 240 秒一次 `wc -c` 轮询，最多 3 次；单份 deadline 与整轮硬上限都是 15 分钟。

`--mode text` 在生成结束前一个字节都不吐，0 字节不等于进程死了：轮询时用 `ps -p <pid>` 判存活，不要因为 0 字节提前 kill、重起或缩输入——实测缩到 7KB 单文件仍然 >100 秒，瓶颈是生成不是输入。

**分批交付，不等齐**：拿到 ≥2 份就先出一版汇总，剩下的在 deadline 内补。到点不管回来几份、有没有补齐，都按「手上有的 + 其余记 no response」出稿，不延期、不追加轮次。不要用 `sleep 120/180` 干等最慢的那个——那是把预算全押在一份输出上。

**汇总前禁止再跑探针**：reviewer 回来后，从「读结果」到「发汇总」之间只允许读文件，不允许再起任何 shell 调用或子模型调用——不跑连通性探针（PONG / 字数 / 速度测试）、不对比 thinking 档位、不重算 diff 基线、不回头证明某条发现「是否本次引入」。这类反查一律推给下一轮：汇总里标「待验证」，用户要追再查。实测过一次 review 在 reviewer 全部返回后又烧了约 10 分钟做这些探针，用户看到的就是「审核完了还在跑」。

当前侧没有 headless CLI 时，用该侧的并行只读 reviewer 机制把同一份 `prompt.md` 分发给不同模型；各侧具体机制见 `{{SRC_ROOT}}/TOOL-MAP.md`，禁止串行等待，汇总结论规则不变。

**必须并行**：同一轮 `codemode` 脚本里用 `Promise.allSettled` 一次发出全部调用，禁止逐个等待。差异来自模型，不人为换 persona。

```js
// @options: {"timeout_ms": 420000, "max_output_tokens": 3000}
const slugs = ["<provider/model-a>", "<provider/model-b>"];
const promptFile = "/tmp/mmr-<ts>/prompt.md";
const res = await Promise.allSettled(slugs.map(s => tools.bash({
  command: `pi -p --no-session -nt --no-mcp -nc -ns --mode text --append-system-prompt 'You have no tools in this session. Never emit tool calls or tool_call XML; answer directly in markdown.' --model ${s} < ${promptFile} 2>&1`,
  timeout: 300 // 每个模型独立硬超时，到点记 no response
})));
slugs.forEach((s, i) => text(`${s}\n${res[i].status === "fulfilled" ? res[i].value.output.trim().slice(0, 8000) : "ERROR: " + res[i].reason}`));
```

慢组用后台 + 轮询（`timeout` 参数是前台阻塞，别拿它等 15 分钟）：

```sh
# 1) 一次起全部，立刻返回
for s in <slug-a> <slug-b>; do
  n=$(echo "$s" | tr '/.' '--')
  nohup pi -p --no-session -nt --no-mcp -nc -ns --mode text --thinking off \
    --model "$s" "$(cat /tmp/mmr-<ts>/prompt.md)" \
    > /tmp/mmr-<ts>/out-$n.md 2>/tmp/mmr-<ts>/err-$n.log &
done
# 2) 每 240 秒一次，最多 3 次：wc -c out-*.md + ps -p <pid>；凑够 ≥2 份就直接汇总
```

`prompt.md` 须含：

- 上面的 intent 段落；
- 待审代码 / diff；
- 对抗式审查说明：优先 bug、正确性、安全、可维护性；发现项带严重度（critical | warning | nit）、具体位置（`file:line`）、证据、可选建议；无问题则明确写 no findings；
- **输出预算**（必须写死）：最多 8 条，只报 P0/P1，P2 最多 2 条，每条 `[P0|P1|P2] 文件:行 — 现象 → 影响 → 建议`，每条不超过两句，不要复述 diff、不要总结段。不设上限时单个模型会吐 12KB，按 30～120 字符/秒就是 2～7 分钟纯生成；每条约 30～60 秒，条数是唯一能直接压 wall-clock 的旋钮。

单模型失败（403 / 超时 / 空输出）只记作「no response」，不影响其他 reviewer，也不静默换成同一个模型重试。

## 4) Synthesize (parent agent)

合并各 reviewer 结果：**共识**（≥2 个模型同指）、**单模型**发现、去重重叠、标注分歧。给用户分类：act on / consider / noted / dismissed，各附一句理由。保留 `file:line` 与严重度，按严重度降序，不自动改代码。

汇总只做合并，不夹带新增检查：从各份结果里能直接读出的结论就写，需要再读代码才能定的标「待验证（未复核）」，不当场开查。合并完这一轮就结束，复核与修复留给下一轮。

只拿到 1 份就照实写「另外 N 个未回（timeout / no response）」，不要用同一个模型补位凑成「多模型」。

**合并轮是可选项**：只有用户明确要「第三个模型来总结」时才多起一次——输入只喂各 reviewer 的纯文本结果（不带源码、不带 diff），输出限 6 行，deadline 3 分钟；其余情况主 agent 自己合，零额外延迟。

## 5) 不要做（都实测踩过）

- **不要串行三段式**「A 审 → B 复核 → C 总结」：三份延迟相加而不是取最大，后审被前审锚定（顺着补全而非独立发现），任一段超时整条链断。要复核就把三份结果一起喂给一个模型做一次合并，不是串起来。
- **不要让 reviewer 把结果写成 markdown 文件**：写文件需要工具，而本 skill 禁止给工具；写 stdout 还是写文件对生成速度没有影响。
- **不要重跑、不要换同模型补位、不要追加轮次**：一次实测 50 分钟的 review 里，3 轮重试 + 4 次探针占了约 30 分钟，真正的有效输出是后台起停后 4～9 分钟给出的 3 份。
