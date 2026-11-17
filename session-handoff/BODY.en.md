# session-handoff

Hands this conversation to another agent that cannot see it. Compress the length, never the facts. No code changes. By default the handoff is only the reply; write a file when the user asks for one.

## How to write it

- Every category below must appear. When there is nothing, write `not mentioned`; never invent.
- One fact per line. The source goes inline: `user's words`, `file path` or `log`.
- Copy paths, numbers, Tags, errors, commands and filter expressions verbatim.
- Never replace a concrete symbol with "etc." or "the related logic". If it does not fit, add a line instead of merging.

## Visible reply

The whole reply is the handoff: no code fence, no lead-in outside the block. Lines may repeat.

```
- Goal: one-sentence result
- Background: why this is being done. Source
- Confirmed: facts. Source
- Ruled out: judgments that were rejected. Source
- Decisions: what was decided. By whom
- Open: what is still undecided
- Verbatim: errors, Tags, filters, commands or the key sentence
- Next: the receiving side's first action
```
