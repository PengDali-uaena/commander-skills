# bugfix-logclean

After the fix is confirmed, retire this round's diagnostic logs. Find the Tag yourself first, then search, judge and edit the repo.

## Finding the Tag

In order; stop at the first hit and never send the user digging:

1. The Tag in this message.
2. `Tag:` in this conversation, or in a session-handoff the user pasted.
3. Diagnostic Tags added by this work in uncommitted changes — including `Probe/`, and any log Tag newly appearing in the diff.

Several unrelated Tags: ask one question about which to retire. None anywhere: state that the message, the conversation and the diff were searched, then stop without editing code.

## Searching

For each Tag, search the string and the adjacent log calls. Never claim there are no logs without searching.

Old logs that only gained parameters and added no new log call: leave them alone.

## Handling

| Situation | Action |
|---|---|
| An old log only gained parameters | Leave it |
| A level raised temporarily for debugging | Restore the original level |
| A one-off new log at a location | Delete the line plus any temporary variable, import or Tag constant that existed only for it |
| Still useful later for timing or state | Keep it, change the level to debug. When the repo has an official Tag convention, switch to that Tag |

Never leave a log that should go at info, warning or error. Never delete logs unrelated to these Tags.

When the user says "just give me the plan, do not change code", list the verdicts only. Otherwise the repo must be edited.

## Verification

Read the repo's rules after editing. Tests, lint, packaging and device commands the rules forbid are not run. Type checks the rules name may be run. When nothing is required, state in the reply that nothing was run.

## Visible reply

One field per line, following `commander`'s "field-block layout": every line starts with `- `, the field name is bold, repeats of the same field go on consecutive lines with no blank lines. Anything written to a file carries `file:line`. Omit categories that did not happen. No code fence, no text outside the block. Hit → untouched form one group; stats and verification each stand alone with one blank line before them.

```
- **Hit**: file:line | summary | added or pre-existing
- **Hit**: …
- **Deleted**: file:line, why
- **Downgraded**: file:line, to which level
- **Kept**: file:line, why it stays
- **Untouched**: file:line, parameters only

- **Stats**: N changed, M untouched
- **Verification**: command result, or why nothing ran
```

Hit, deleted, downgraded, kept and untouched may each appear on several lines.
