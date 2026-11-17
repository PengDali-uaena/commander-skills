# bugfix-probe

Localizing a failure: read code against hypotheses first. If the evidence is thin, add diagnostic logs and stop, handing the filter to the user. Only when logs or a stack trace already point at a line do you make the minimal fix and write the root cause.

## Start

Write down the symptom, the reproduction path and the platform. If the symptom or path is missing, ask at most 2 questions, then continue with what you have and mark the assumptions in the interim conclusion.

Write 1–3 falsifiable hypotheses, each tied to the file or symbol you will read. Paths the user named and files from the stack trace come first. Directories outside the list are not scanned.

## Reading code

- No keyword-free repo-wide search as the first step.
- Outside the hypothesis list, read at most 5 more files. For each extra file you must be able to say which hypothesis it belongs to.
- Support, refutation and open questions for a hypothesis stay inside the tool steps. The visible reply carries no hypothesis table unless the user says "show me the hypotheses" or "expand the hypotheses" in this message.
- "The code looks like it" only: write an interim conclusion, no root cause, no business-logic change. Order multiple open branches by likelihood, most likely first; do not lay them out by line number or file order.
- Logs or a stack trace already prove causality or point at a line: you may make the minimal fix and write the root cause. Changes follow the current repo's rules.

## Diagnostic logs

When evidence is still thin you must write code, not just suggest logs in the reply.

- One primary Tag per investigation. First look at how logs are written in the files you are editing and in the repo, reuse that API, and use debug level.
- When the repo has no logging facility, use the platform's own debug output; add no dependencies.
- When no existing probe Tag exists, use `Probe/<module>`.
- Cross-platform chains (Flutter / H5 / Android / iOS) share one primary Tag, with identical literals on every platform; filters are listed per platform.
- Every log line carries `phase=<token>`. Tokens are snake_case, unique within the task, and appear in the filter.
- No untagged prints, and never dump whole objects.
- Use info or warning only when the user needs the logs in production too, and state in the interim conclusion that the logs must be removed afterwards.

If the user already pasted logs that still leave a branch open: state what the existing logs rule out, which one is missing, and add one round per "cover everything at once" below.

## Cover everything at once (never one log per round)

A reproduction is expensive for the user; "add one log → wait → guess the next layer" is this skill's most common failure.

- Before adding logs, list which fields are needed to settle the cause, and cover every open branch in this round: at least one `phase` per hypothesis, not spread over rounds.
- If one round of logs still cannot separate the branches, the second round must add every remaining discriminator at once, and the reply must include the reading: which `phase` / field value maps to which conclusion. A reply without the reading counts as undelivered.
- If logs can be added, do not make the user run a controlled experiment; when one is unavoidable, state "do it once in the healthy state and once in the broken state, and which field to check each time".
- Three consecutive rounds with no conclusion on the same problem: stop and change method (controlled experiment, re-read the code, hand the boundary back to Native / backend). Do not add a fourth log.
- Once logs point at a specific line, add no more logs; give the root cause and the minimal fix.

## Filters

Output only the platforms you actually need. If the user named one, give only that one. When they did not: an obviously Web-only repo gets Web; an obviously Apple-only repo gets iOS; otherwise give both Android and iOS. Never invent a subsystem or category.

- Android: one line. Join the primary Tag and this round's phases with `|`, no spaces around `|`. `|` means or. This line is for the logcat search box and also works as the `adb logcat -e` regex.
- iOS: one line per string to search, at least one line with the primary Tag. When the phase and the Tag always land on the same line, do not split the phase out. If the user says the iOS Regex toggle is on, switch to one line `- iOS Regex:` joined with `|`, unsplit.
- Web: same shape as iOS, prefixed `- Web:`. The browser console matches by substring.

Every token in the filter must match the literal in the code.

## Visible reply

One field per line, following `commander`'s "field-block layout": the field name is bold (`- **Interim conclusion**: …`), **there is a blank line between fields**, and inside a value at most 2 more bold spots mark verdict words. Here every field is its own group. No code fences, no text outside the block. Write paths, numbers, Tags and tokens in full.

When the interim conclusion has several branches, repeat the field on consecutive lines with no blank line between them, ordered most likely to least likely; never pack several branches into one line.

Evidence is thin:

```
- **Interim conclusion**: …

- **Android**: Tag|phase_a|phase_b

- **iOS**: Tag

- **Web**: Tag

- **Steps**: …

- **Reading**: `phase_a` plus `hasX: false` = conclusion A; only `phase_b` = conclusion B

- **Changes**: …

- **Tag**: Tag
```

Omit whole lines for platforms that do not apply; repeat the iOS or Web line when there are several strings; omit the reading line when no reading is needed.

Root cause proven:

```
- **Interim conclusion**: …

- **Root cause**: …

- **Tag**: Tag

- **Changes**: …
```

Omit "Changes" when no repo file was edited. Omit "Tag" when this round added no diagnostic Tag. With a root cause, do not output filters or steps.

If the user says "show me the hypotheses" or "expand the hypotheses": after the field block, at most 3 lines of `- Hypothesis:`, and list the phase names.

## Example

The example only shows the shape. Tags, tokens and paths follow the current repo's code.

```
- **Interim conclusion**: The list is empty; the code looks like the callback fires before the subscription, logs have not confirmed it yet.

- **Android**: Probe/Inbox|phase_subscribe|phase_callback

- **iOS**: Probe/Inbox

- **Steps**: Kill the process, cold start into the list, wait 10 seconds, paste the filter output back.

- **Reading**: `phase_callback` before `phase_subscribe` = the subscription is late; normal order = the hypothesis is wrong.

- **Changes**: One debug line before and after the subscription in InboxController.

- **Tag**: Probe/Inbox
```
