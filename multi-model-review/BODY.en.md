# multi-model-review

The user wants adversarial multi-model code review: several independent models each review once, then the parent agent synthesizes the conclusions. Use only when the user explicitly names this skill (or this side's explicit load syntax in `{{SRC_ROOT}}/TOOL-MAP.md`) or clearly asks for a parallel multi-model review.

By default **no file changes and no automatic fixes**, unless the user says otherwise.

## 1) Pick models

Run `pi --list-models` first to get the slugs that actually work right now (shaped `provider/model`). Pi has no structured multiple-choice tool: **inline** the candidates in the reply (number + slug), ask in one sentence for a number or slug, and launch only after the answer. Never invent a tool call.

- Keep the list in `pi --list-models` order and present it neutrally: no recommendation, no sorting, no preselection, no omissions, no "(Recommended)".
- List only what can really run: skip providers whose `pi auth check --provider <p>` is `not_ready`, and skip models whose probe returns `permission_error` / `Model access is disabled` (write one line, "<slug> skipped, 403 unavailable").
- If the user **already** chose models in the invocation or the conversation and has no objection, the question may be skipped; otherwise still ask.
- When a slug is rejected at execution time, use the closest valid slug from `pi --list-models` and tell the user what was substituted.

## 2) Scope and intent

1. Determine the review scope: paths or a diff the user specified; otherwise `git diff main...HEAD` (or the repo's default base...HEAD); otherwise local staged+unstaged; otherwise the files and symbols from the conversation.
2. Write one **intent** paragraph: what this change is meant to achieve (from the message, the commit messages or the code).
3. Drop the shared material for all reviewers into a temp file, `/tmp/mmr-<timestamp>/prompt.md`: intent + full diff (or the key fragments) + the review instructions from step 3 below. Every reviewer reads that same file.

## 3) Launch one reviewer per selected model (parallel only)

Start one headless reviewer per selected slug, **read-only in the foreground**: `-nt` (all tools disabled) + `--no-session -nc -ns --no-mcp`, with the prompt on stdin.

```
pi -p --no-session -nt --no-mcp -nc -ns --mode text \
  --append-system-prompt "You have no tools in this session. Never emit tool calls or tool_call XML; answer directly in markdown." \
  --model <provider/model> < /tmp/mmr-<ts>/prompt.md
```

`--append-system-prompt` is not optional: without tools, some models emit `tool_calls` XML as body text.

When this side has no headless CLI, use its parallel read-only reviewer mechanism to fan the same `prompt.md` out to different models; which mechanism each side uses is in `{{SRC_ROOT}}/TOOL-MAP.md`. Never wait serially; synthesis rules are unchanged.

**Parallel is mandatory**: in one `codemode` script, fire every call at once with `Promise.allSettled`; never await them one by one. Differences must come from the models, not from swapping personas.

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

`prompt.md` must contain:

- the intent paragraph above;
- the code / diff under review;
- the adversarial review instructions: bugs, correctness, security and maintainability first; each finding carries severity (critical | warning | nit), a concrete location (`file:line`), evidence and an optional suggestion; write "no findings" explicitly when there are none.

A single model failing (403 / timeout / empty output) is recorded as "no response"; it does not affect the other reviewers, and you never silently retry with the same model.

## 4) Synthesize (parent agent)

Merge the reviewer results: **consensus** (≥2 models pointing at the same thing), single-model findings, deduplicated overlaps, and disagreements flagged. Classify for the user as act on / consider / noted / dismissed, each with one reason. Keep `file:line` and severity, order by severity descending, and never change code automatically.
