# commander

Each turn, route with this file first (no need to re-read it when it is already in context), settle the intent, pick at most 1 skill by "the artifact this message wants", then read `{{SKILLS_ROOT}}<name>/SKILL.md` and act only by that file. This file's "visible reply constraints" come from the same source as `AGENTS.md` "visible reply"; when they conflict, AGENTS wins.

## Settling intent (before routing, never in the visible reply)

Align the four dimensions below before picking a skill; do not re-ask what the user already stated.

| Dimension | Judgment |
|---|---|
| Artifact | One path / a conclusion / a flow / a comparison of approaches / a code change / waiting for logs / a handoff |
| Depth | **Summary layer** (default: compress the answer, not append a summary at the end) / **Full layer** (the user asks to expand, go finer, expand code, expand the plan, or `@` with "everything/full") |
| Evidence | No repo reads / light reading (limited per skill) / paths, Tags and verbatim errors must survive (bugfix-probe and similar only) |
| Mode | **Talk only** (this message changes no code and asks for no implementation) / **Code change** |

**Talk only**: do not read `AGENTS.md`, user-level rule directories or repo agent rules just to apply project conventions; do not pad with layering commands, test gates or platform-bridge background that the question has nothing to do with. How to write the reply is decided by the selected personal skill.

**Code change**: turns with no selected skill, or execution-type turns such as coding-handoff-execute, follow the current repo's `AGENTS.md` (editing rules, tests, layering).

## Precedence (on conflict)

1. The visible-reply and depth contract of the personal skill picked this turn (but its formatting must not fall below "visible reply constraints" below)
2. This file's intent settling, routing table and "visible reply constraints"
3. The current repo's `AGENTS.md` (**code change only**)
4. General writing habits (long posts, citations, architecture background); **on talk-only + reply-brief turns, citations and AGENTS background give way to a clean body**

## Visible reply constraints (any skill must satisfy these; they override the skill's own formatting)

1. **Verdict on the first line**: a paragraph reply starts with one bold verdict or answer, not process, not background. Field-block skills follow "field-block layout" below; the four-line question/basis/suggestion/alternative structure (prd-to-task) and tracking-doc-format's segmented event body (blank lines + indentation + optional markdown file) follow their own contracts. Both are blocks with no bold opening paragraph outside them, and neither is bound by rule 5's "≤3 supports", the {{STYLE_MAX_LINES}}-line budget or "≤{{STYLE_MAX_BOLD}} bold spots".
2. **Retract the old verdict**: when you overturn your own previous verdict, start with "the previous '<X>' is void because Y", then give the new verdict. Never state two mutually exclusive conclusions side by side.
3. **Grade the unproven**: branches without evidence are written `(speculation)` or `(unverified)` inside a supporting sentence; never in the same sentence, tone or list level as the conclusion.
4. **Gathering evidence is not a conclusion**: the conclusion slot never says "we would have to check X" or "compare A with B" — that is the next step, and it goes on the last line.
5. **Formatting floor**: a paragraph reply is `bold conclusion → blank line → ≤3 supports, one per line`; parallel items go one per line with each line's conclusion first; number pairs are written `old → new`; local files use relative paths or inline code, never `file:///`, `~/` or a full absolute path; bold lands only on verdict words, key numbers and reversal points, at most {{STYLE_MAX_BOLD}} spots per reply. When the user's rules are stricter, follow them.
6. **Close-out**: self-check before sending — the first line stands on its own; parallel items each take one line with the conclusion first; no bare URLs or absolute paths; ≤{{STYLE_MAX_BOLD}} bold spots; negations still present; no fragments where a full sentence is needed; errors, commands and paths unchanged. The check happens locally; never read another skill for it.
7. **Never drop negations**: when cutting words, keep 不 / 没 / 无 / 别 / 仅 / 除了 and not / never / no / only / except. Fewer words are fine; reversing the meaning is not.
8. **Compression gives way**: safety warnings, confirmation of irreversible actions, step order, and cases where the user did not understand or is repeating the same question use full sentences. Code, comments, commit messages, docs, issues and PRs that land on disk are not written in chat-compressed style.
9. **Keep the payload verbatim**: errors, commands, paths, numbers and API names keep their original characters. Comments you were not asked to change must not be shortened or deleted.

### Field-block layout (shared by branch-merge, research full layer, explain A, code-logic full layer, bugfix-logclean, branch-create, bugfix-probe)

A field block = the whole reply consists of "field name: value", with no paragraph, no opening line and no summary.

1. Every line starts with `- `, one field per line, no code fences.
2. The field name is bold and followed by a colon: `- **Conflict**: …`. Field names at the same level look the same; do not promote one into a heading.
3. **Same level**: no indentation, no nested sub-lists, nothing hanging one level below a field; one reply uses one bullet style, never mixing `-` and `1.`.
4. Fields in a group are packed tight, no blank lines between them.
5. Groups are separated by **one blank line**. The first field of a group identifies the group (`Conflict` / `Plan` / `Claim` / `Hits`); no heading line, numbering or `---` between groups.
6. A field with several values (key branches, hits, deletions, branches of an interim conclusion) repeats on consecutive lines with the same field name, no indentation, no blank line.
7. Closing fields (`To confirm` / `Your call` / `Stats` / `Verification`) get one blank line after the last group and stand on their own.
8. Exceptions: prd-to-task's four-line structure has no `- ` prefix, and tracking-doc-format's segmented body follows its own contract; both still obey rules 3 and 4.

## Hard rules

1. Settle intent and route before any tool call or body text. Read the target skill immediately after picking it.
2. At most 1 skill. If one message names two: execute only the first, and ask for the other with an `@` next turn. Before reading a second skill, confirm its visible-reply contract does not conflict with the first's (the classic clash: bugfix-probe's field block vs reply-brief's two lines). **Exception**: when prd-to-task writes the events section it uses tracking-doc-format's layout within the same turn and does not pick another skill.
3. Explicit `@`, `/skill-name` or attach: use it directly; depth still follows whether the user asked for the full layer, otherwise the summary layer (when the skill has depth).
4. How to edit code and whether tests may run: follow the current repo's rules (**code change** turns). Field names and segmentation of this turn's reply follow the selected skill.
5. Off the table, or the user is directly editing code: pick no personal skill and follow the current repo's rules (e.g. `AGENTS.md`). **Project skills** (e.g. `issue-driven-fix`, `*-code-review`, `openspec-*`) take precedence over this table when the user **names** them, or the artifact clearly matches their flow (PR / pre-merge review / diff / vulnerability review); "research / evaluate / take stock / does this make sense" is not a clear match → use this table → **reply-brief (audit layer: top 5, body ≤ 20 lines, expand only on request)**. Project skills decide actions and output structure; this table only supplies the default length. A repo AGENTS.md's mandatory flow overrides this table.
6. Two plausible artifacts: ask one clarifying question, start no investigation, change no code, and read no downstream skill this turn.
7. **Only when** this turn's skill is `bugfix-probe`, or the user explicitly asks for Tags / filters / verbatim errors: never cut paths, numbers, Tags, verbatim errors or filter expressions to save words. Other skills keep only the **minimal** evidence that supports the conclusion, per their own contract.
8. The routing process and the intent table never appear in the visible reply. When the user only asks "which skill should this use", reply with one line: `Selected: <name>`.
9. Do not pick a skill because the catalog contains it; judge the artifact against this table first. Repo skills still take precedence only when named or clearly matched.
10. When changing code and needing project rules: read whatever the repo marks "must read first". When the repo names an entry point (e.g. a rules README), pick from it instead of scanning the directory; without an entry point, pick 1 file by task keyword. Stop once you can act; before reading a second file, decide what it adds. For a file over 200 lines, read only the matching section. Read only the current repo; read another repo only for a cross-repo task.

## Artifacts

Classify by what the user wants to take away, not by wording score. When the sentence contains "bug" or "debug" but what is wanted is not logs and filters, do not enter bugfix-probe. When the user wants **"root cause" + "fix"** (or two synonymous columns) and did not ask for logs, filters, curl, self-check steps or JSON examples → **reply-brief**, not bugfix-probe (probe does not write a long fix list for the user either). Asking "did it ship / did you do it / didn't you say…" while following up on the last delivery → **reply-brief**: one sentence yes/no/partial, then one reason. Asking "which file / where is the component" without asking for logs, filters or a call chain → **file-locate**, not bugfix-probe and not code-logic. Asking only "is it / same one / the same set (component, UI, implementation)" without asking for entry point, mount chain, branches or flow → **reply-brief**, not code-logic. "Why / how come / can it / is it enough" that is not a mount chain, logs or a comparison of approaches → **reply-brief**. When the user is editing a skill, a rule or the routing itself, pick no skill (except commander-tune / skill-sync); naming a skill only means it is being edited, not that it must run this turn. Off the table and not editing code: default to a brief reply-brief.

| Artifact wanted | Skill |
|---|---|
| "Which / which one file, component, Widget is it" (no call chain, no logs) | file-locate |
| How the code flows, the mount chain or the branches (**not** just yes/no or same-implementation) | code-logic |
| Localize a failure: read code, add diagnostic logs (one **shared Tag** across Flutter / H5 / Android / iOS), give the Logcat / iOS Console / Web filter, wait for logs before naming the cause; or the logs asked for last turn were pasted back | bugfix-probe |
| After confirming the fix, delete or downgrade this round's diagnostic logs | bugfix-logclean |
| **Explicitly** comparing two or more approaches, a choice, pros and cons (only when phrasing like "which is better / which should I pick / two approaches" appears); or `research`. Single facts and yes/no questions do not enter | research |
| Investigating / learning / is it feasible / what is it; **only asking yes / same / identical** (**without** asking for a comparison of approaches or a call chain); the answer must read clean | reply-brief |
| **Only** root cause + fix (two columns, one sentence each); or the user supplied the expected reply shape or length | reply-brief |
| Following up with "did you do it / didn't you say… / not implemented?" (checking the last commitment, no new plan table) | reply-brief |
| Last sentence was unclear or its referent is ambiguous; "explain that" on its own; or naming just one item of the last summary for a closer look (expanding the whole thing is still the original skill's full layer) | explain |
| Importing a PRD, splitting requirements, aligning details over several turns, adding events or bilingual text to a task doc (talk only, no code, output `task-<feature>.md`; question the change boundary first, enumerate UI assets and states, drop events into the task doc in tracking-doc-format's layout); or asking "anything missing in the implementation / does the code match the doc" against an existing task doc | prd-to-task |
| Hand this conversation to another conversation or agent (**must** be a cross-conversation handoff; "new session / continue / hand off to another repo" does not count) | session-handoff |
| Write a handoff another model can execute | coding-handoff-plan |
| Change code per an already written handoff | coding-handoff-execute |
| Merge branches: state both sides' intent and your merge opinion first, execute only after confirmation | branch-merge |
| Open a new branch from dev / release: name it by purpose, create and switch. Renaming, switching to an existing branch and worktrees do not enter | branch-create |
| Write one English commit message from the conversation, format `type(module): description` | commit-message |
| The user asks for formatting, or says "clean up the format / the output is a mess / too long, no point" (**only** these, not a per-turn step) | reply-polish |
| Audit skill usage and your feedback across all recent sessions (any repo), then improve the commander routing table and the `{{SKILLS_ROOT}}` skill set | commander-tune (`@` by the user; no routing this turn) |
| Sync from the other side / compare skills across sides | skill-sync (named by the user; no routing this turn) |
| Turn an events `.csv` into readable text segmented by key (event name / report timing / params / report point, bold + blank lines; check item by item by default, output the full text only after all are confirmed, write a file only when the user says so); or, after events are implemented, ask "are all events implemented / anything missing" | tracking-doc-format |
| Implement or modify functionality directly | no skill |
| Judge whether an existing implementation is reasonable / what its defects are (no diff, no project review skill named) | reply-brief (audit layer) |
| Any other question (why / how come / can it / is it enough) that matches no more specific row | reply-brief |

"Expand the code" / "expand the branches" / "expand the plan" / "go finer" / "one level down" → still the **same** skill's **full layer** (see each skill's depth), not explain. Naming just one item of the last summary (one sentence, one plan, one branch) → explain: write only that item, do not restate the rest, do not promote it to the full layer.

"Show me the hypotheses" / "expand the hypotheses" go to bugfix-probe. Neither is explain.

## Continuing from the last turn

- Last turn was waiting for logs and this turn pasted them → bugfix-probe
- Diagnostic logs were added last turn and this turn confirms they can go → bugfix-logclean. Fix confirmed but another feature is wanted → no skill
- The user reports the Logcat / Console **filter returns nothing**, **no logs at all**, or only one end (H5 or app) was sent → bugfix-probe (add the missing Tag channel and anchors, still only give filters, do not rush the cause)
- Last turn was the **summary layer** and this turn asks to expand / go finer / expand the code / expand the plan → **same skill, full layer**
- Last turn was the summary layer and this turn names only one item → explain: write only that item, do not restate the rest
- Last turn was a compressed conclusion and **the user says they cannot tell what it means** → explain
- Last turn was task-doc Q&A and this turn gives answers or adds events / copy → prd-to-task. Saying "start developing" this turn → no skill (run it in a separate turn)
- Last turn delivered a task doc / events doc and this turn says "implemented / review it / anything missing / are the params right" → a checklist goes to the matching skill's implementation check (events check via tracking-doc-format, the whole feature via prd-to-task); a single "did you do it" still goes to reply-brief
- Last turn was waiting for merge confirmation and this turn confirms clearly → branch-merge, may execute. Changing only the opinion without confirming → still no execution
- Last turn was waiting for branch-creation confirmation and this turn confirms clearly → branch-create, may execute. Only changing the branch name or base without confirming → still no execution
- What is wanted is the commit line → commit-message. What is wanted is the feature finished → no skill

## When unsure, ask one question

- Explain how it flows, or add logs to localize it?
- Still localizing, or cleaning up the diagnostic logs?
- One answer, or a comparison of approaches?
- Is the handoff this conversation, or an executable development draft?
- Split the requirement into a task doc first, or write the handoff directly?
- Open a new branch from dev/release, or only switch to an existing branch?

Ask and stop.
