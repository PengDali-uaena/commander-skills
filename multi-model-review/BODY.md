# multi-model-review

用户要对抗式多模型代码审查：多个独立模型各审一遍，再由主 agent 汇总结论。仅在用户显式点名本 skill（或本侧等价显式加载语法，见 `{{SRC_ROOT}}/TOOL-MAP.md`）或明确要求多模型并行 review 时使用。

默认**不改文件、不自动修**，除非用户另说。

## 1) Pick models

先跑 `pi --list-models` 取当前真实可用的 slug（形如 `provider/model`）。Pi 没有结构化多选题工具：在回复里**内联**列出候选（编号 + slug），一句话请用户回编号或 slug，收到回复后再 launch，不要臆造工具调用。

- 列表按 `pi --list-models` 原顺序，中性展示：不推荐、不排序、不预选、不省略、不加 “(Recommended)”。
- 只列真正能跑的：`pi auth check --provider <p>` 为 `not_ready` 的 provider 不列；probe 返回 `permission_error` / `Model access is disabled` 的模型也不列（写一句「<slug> 已跳过，403 不可用」）。
- 若用户在调用或对话里**已明确**选了模型且无异议，可跳过提问；否则仍要问。
- 某 slug 执行被拒时，优先采用 `pi --list-models` 里最接近的合法 slug，并告诉用户替换了什么。

## 2) Scope and intent

1. 确定审查范围：用户指定路径或 diff；否则 `git diff main...HEAD`（或仓库默认 base…HEAD）；否则本地 staged+unstaged；否则用对话里涉及的文件与符号。
2. 写一段 **intent**：这次改动想达成什么（来自消息、提交说明或代码）。
3. 把各 reviewer 的共享材料落到临时文件：`/tmp/mmr-<时间戳>/prompt.md`，内容 = intent + 完整 diff（或关键片段）+ 第 3 步的审查说明。下文所有 reviewer 读同一个文件。

## 3) Launch one reviewer per selected model (parallel only)

每个选中的 slug 起一个 headless reviewer，**前台只读**：`-nt`（禁用全部工具）+ `--no-session -nc -ns --no-mcp`，提示词走 stdin。

```
pi -p --no-session -nt --no-mcp -nc -ns --mode text \
  --append-system-prompt "You have no tools in this session. Never emit tool calls or tool_call XML; answer directly in markdown." \
  --model <provider/model> < /tmp/mmr-<ts>/prompt.md
```

`--append-system-prompt` 不能省：不带工具时部分模型会把 `tool_calls` XML 当正文吐出来。

Cursor 等无 `pi -p` 的侧：同一 `prompt.md` 上并行起多个只读 Task（`run_in_background: false`、各选不同 model slug），禁止串行等待；汇总结论规则不变。

**必须并行**：同一轮 `codemode` 脚本里用 `Promise.allSettled` 一次发出全部调用，禁止逐个等待。差异来自模型，不人为换 persona。

```js
// @options: {"timeout_ms": 900000, "max_output_tokens": 3000}
const slugs = ["<provider/model-a>", "<provider/model-b>"];
const promptFile = "/tmp/mmr-<ts>/prompt.md";
const res = await Promise.allSettled(slugs.map(s => tools.bash({
  command: `pi -p --no-session -nt --no-mcp -nc -ns --mode text --append-system-prompt 'You have no tools in this session. Never emit tool calls or tool_call XML; answer directly in markdown.' --model ${s} < ${promptFile} 2>&1`,
  timeout: 600
})));
slugs.forEach((s, i) => text(`${s}\n${res[i].status === "fulfilled" ? res[i].value.output.trim().slice(0, 8000) : "ERROR: " + res[i].reason}`));
```

`prompt.md` 须含：

- 上面的 intent 段落；
- 待审代码 / diff；
- 对抗式审查说明：优先 bug、正确性、安全、可维护性；发现项带严重度（critical | warning | nit）、具体位置（`file:line`）、证据、可选建议；无问题则明确写 no findings。

单模型失败（403 / 超时 / 空输出）只记作「no response」，不影响其他 reviewer，也不静默换成同一个模型重试。

## 4) Synthesize (parent agent)

合并各 reviewer 结果：**共识**（≥2 个模型同指）、**单模型**发现、去重重叠、标注分歧。给用户分类：act on / consider / noted / dismissed，各附一句理由。保留 `file:line` 与严重度，按严重度降序，不自动改代码。
