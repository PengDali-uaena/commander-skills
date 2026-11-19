# multi-model-review

The user wants adversarial multi-model code review: several independent models each review once, then the parent agent synthesizes the conclusions. Use only when the user explicitly names this skill (or this side's explicit load syntax in `{{SRC_ROOT}}/TOOL-MAP.md`) or clearly asks for a parallel multi-model review.

By default **no file changes and no automatic fixes**, unless the user says otherwise.

## 1) Pick models

Run `pi --list-models` first to get the slugs that actually work right now (shaped `provider/model`). Pi has no structured multiple-choice tool: **inline** the candidates in the reply (number + slug), ask in one sentence for a number or slug, and launch only after the answer. Never invent a tool call.

- Keep the list in `pi --list-models` order and present it neutrally: no recommendation, no sorting, no preselection, no omissions, no "(Recommended)".
- List only what can really run: skip providers whose `pi auth check --provider <p>` is `not_ready`, and skip models whose probe returns `permission_error` / `Model access is disabled` (write one line, "<slug> skipped, 403 unavailable").
- If the user **already** chose models in the invocation or the conversation and has no objection, the question may be skipped; otherwise still ask.
- When a slug is rejected at execution time, use the closest valid slug from `pi --list-models` and tell the user what was substituted.
- **Probe once**: after the list, do not probe every slug serially; one `pi --list-models` plus one `pi auth check` is enough. Trial runs per model burn the budget in the setup phase.
- **Measure generation speed once, then set the deadline**: run one tiny task per candidate provider (`echo "reply with exactly: OK" | pi -p -nt --no-session -nc -ns --mode text --model <slug>`, timed); ≤15s is the "fast group", >30s the "slow group"; at most 2 probes in total. Speed is a gateway property, so do not try every slug of the same provider.

## 2) Scope and intent

1. Determine the review scope: paths or a diff the user specified; otherwise `git diff main...HEAD` (or the repo's default base...HEAD); otherwise local staged+unstaged; otherwise the files and symbols from the conversation.
2. Write one **intent** paragraph: what this change is meant to achieve (from the message, the commit messages or the code).
3. Drop the shared material for all reviewers into a temp file, `/tmp/mmr-<timestamp>/prompt.md`: intent + full diff (or the key fragments) + the review instructions from step 3 below. Every reviewer reads that same file.
4. **Shard it**: when the diff exceeds roughly 120KB or 30 files, split by file into 2–3 bundles and give each reviewer only its own bundle plus the full intent. Do not hand over the whole package; it makes the models wander into "while I'm here" files, which bloats output and blurs locations.
   **Consensus only exists inside a shard**: send shards to the same set of models (either every model gets all shards, or all models get the same shard). Never let "A reviews shard 1, B reviews shard 2" — no overlap means no consensus, only single-model findings.
5. Input size is not the bottleneck (measured: 137KB input with a very short answer returned in 6–14 seconds). Output length and tool turns are, so the budget and no-tools rule in step 3 matter more than shrinking the diff.

## 3) Launch one reviewer per selected model (parallel only)

Start one headless reviewer per selected slug, **read-only in the foreground**: `-nt` (all tools disabled) + `--no-session -nc -ns --no-mcp`, with the prompt on stdin.

```
pi -p --no-session -nt --no-mcp -nc -ns --mode text \
  --append-system-prompt "You have no tools in this session. Never emit tool calls or tool_call XML; answer directly in markdown." \
  --model <provider/model> < /tmp/mmr-<ts>/prompt.md
```

`--append-system-prompt` is not optional: without tools, some models emit `tool_calls` XML as body text.

**Never give a reviewer tools**: no `--tools`, no `-t read,bash`, and no "you may read the repo / run git diff" in the prompt. Once tools are granted the model enters an agentic inspection loop and its time becomes unbounded: measured in one real review, a glm-5.3-flash run with `--tools read,bash` took 13 minutes to produce 5.3KB (about 8 chars/sec), while the same input volume with tools disabled returned in 6 seconds. Tools also push findings outside the diff, and can make the model treat text inside the diff as instructions.

**Pick a path from the speed probe in step 1**; both are parallel, they differ only in who waits:

- **Fast group**: `Promise.allSettled` inside `codemode`, `timeout: 240` per call; 6-minute round cap.
- **Slow group** (probe >30s; opencode-go's glm / deepseek measured into this group): **launch detached, collect by polling**. Start every reviewer in one bash call with `nohup … > /tmp/mmr-<ts>/out-<slug>.md 2>err-<slug>.md &`, then poll `wc -c` once every 240s, at most 3 times; per-reviewer deadline and round hard cap are both 15 minutes.

`--mode text` emits not a single byte until generation finishes, so 0 bytes does not mean the process is dead: poll with `ps -p <pid>`. Never kill, restart or shrink the input on 0 bytes — measured, shrinking to a single 7KB file still took >100s; the bottleneck is generation, not input.

**Deliver in stages, never wait for everyone**: as soon as ≥2 results are in, publish a first synthesis and top up within the deadline. The 6-minute round deadline is a **hard cap** for the fast group and 15 minutes for the slow group: at the deadline, publish with whatever is in hand and mark the rest "no response" — no extension, no extra round. Do not `sleep 120/180` waiting on the slowest one — that bets the whole budget on a single output.

**No probes between results and synthesis**: once the reviewers return, from "read the outputs" to "publish the synthesis" you may only read files — no shell calls and no sub-model calls: no connectivity probes (PONG / word-count / speed tests), no thinking-level comparisons, no recomputing the diff baseline, no going back to prove whether a finding "was introduced by this change". Push all such follow-ups to the next turn: mark them "to verify" in the synthesis and investigate only if the user asks. One real run burned roughly 10 extra minutes on these probes after every reviewer had already returned; from the user's seat that reads as "the review is done but it is still running".

When this side has no headless CLI, use its parallel read-only reviewer mechanism to fan the same `prompt.md` out to different models; which mechanism each side uses is in `{{SRC_ROOT}}/TOOL-MAP.md`. Never wait serially; synthesis rules are unchanged.

**Parallel is mandatory**: in one `codemode` script, fire every call at once with `Promise.allSettled`; never await them one by one. Differences must come from the models, not from swapping personas.

```js
// @options: {"timeout_ms": 420000, "max_output_tokens": 3000}
const slugs = ["<provider/model-a>", "<provider/model-b>"];
const promptFile = "/tmp/mmr-<ts>/prompt.md";
const res = await Promise.allSettled(slugs.map(s => tools.bash({
  command: `pi -p --no-session -nt --no-mcp -nc -ns --mode text --append-system-prompt 'You have no tools in this session. Never emit tool calls or tool_call XML; answer directly in markdown.' --model ${s} < ${promptFile} 2>&1`,
  timeout: 300 // per-model hard timeout; on expiry record no response
})));
slugs.forEach((s, i) => text(`${s}\n${res[i].status === "fulfilled" ? res[i].value.output.trim().slice(0, 8000) : "ERROR: " + res[i].reason}`));
```

For the slow group, launch detached and poll (`timeout` blocks in the foreground; do not use it to wait 15 minutes):

```sh
# 1) start everything at once, return immediately
for s in <slug-a> <slug-b>; do
  n=$(echo "$s" | tr '/.' '--')
  nohup pi -p --no-session -nt --no-mcp -nc -ns --mode text --thinking off \
    --model "$s" "$(cat /tmp/mmr-<ts>/prompt.md)" \
    > /tmp/mmr-<ts>/out-$n.md 2>/tmp/mmr-<ts>/err-$n.log &
done
# 2) once every 240s, at most 3 times: wc -c out-*.md + ps -p <pid>; synthesize as soon as ≥2 are in
```

`prompt.md` must contain:

- the intent paragraph above;
- the code / diff under review;
- the adversarial review instructions: bugs, correctness, security and maintainability first; each finding carries severity (critical | warning | nit), a concrete location (`file:line`), evidence and an optional suggestion; write "no findings" explicitly when there are none;
- an **output budget** (mandatory): at most 8 findings, P0/P1 only, at most 2 P2s, each shaped `[P0|P1|P2] file:line — symptom → impact → suggestion`, at most two sentences each, no diff restating, no closing summary. Without a cap a single model writes 12KB, which at 30–120 chars/sec is 2–7 minutes of pure generation; each finding costs roughly 30–60s, so the cap is the only lever that directly cuts wall-clock.

A single model failing (403 / timeout / empty output) is recorded as "no response"; it does not affect the other reviewers, and you never silently retry with the same model.

## 4) Synthesize (parent agent)

Merge the reviewer results: **consensus** (≥2 models pointing at the same thing), single-model findings, deduplicated overlaps, and disagreements flagged. Classify for the user as act on / consider / noted / dismissed, each with one reason. Keep `file:line` and severity, order by severity descending, and never change code automatically.

Synthesis only merges; it never adds new checks: write what the results already support, mark anything that needs another code read as "to verify (not re-checked)", and do not start investigating. The turn ends with the synthesis; re-checking and fixing belong to the next turn.

If only one result arrives, say so plainly ("the other N did not respond: timeout / no response"); never pad a "multi-model" review by standing in for a model yourself.

**The merge round is optional**: only start one extra model when the user explicitly asks for "a third model to summarize" — feed it the reviewers' plain-text results only (no source, no diff), cap the output at 6 lines, deadline 3 minutes. Otherwise the parent agent merges for free.

## 5) Do not (all measured the hard way)

- **No serial three-stage chain** (A reviews → B re-checks → C summarizes): the three latencies add up instead of taking the max, the second stage gets anchored by the first (it completes rather than discovers), and any stage timing out breaks the whole chain. If you want a re-check, feed all three result sets to one model as a single merge call, not a chain.
- **Do not have a reviewer write its findings into a markdown file**: writing files requires tools, and this skill never grants tools; stdout vs a file makes no difference to generation speed.
- **No reruns, no substituting the same model, no extra rounds**: in one measured 50-minute review, 3 retry rounds plus 4 probes ate about 30 minutes; the only real output was 3 results delivered 4–9 minutes after a detached launch.
