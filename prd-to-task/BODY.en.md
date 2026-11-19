# prd-to-task

Turns a PRD into one `task-<feature>.md` that can be developed from, through several rounds of Q&A.

Conversation only, code reading only, and only this document, the question queue, the node evidence dump and the new assets. No business code.

Triggers: importing a PRD / splitting requirements / pinning down requirement details / listing feature points / adding events or copy to a task / pasting a Figma link with a page description / the user names prd-to-task.

**`Implement this design from Figma` changes nothing**: while the round is about requirements, documents or the design, only the task document and its assets change — never `lib/`. Writing code waits for an explicit "start implementing".

## Boundaries

- No business code, no editing the PRD source, no branches, no builds.
- Read only code the PRD points at: pages and components it names, same-name or adjacent features, API definitions, l10n files, event constants. Stop once the current question is answered.
- Write exactly four places: the task document `docs/{{DOC_PREFIX}}<date>-task-<feature>.md`, the question queue `docs/{{DOC_PREFIX}}<date>-queue-<feature>.md` (this round's questions plus the open list, kept short), the node evidence `docs/<feature>/nodes.tsv`, and the new `assets/`. Existing assets are read-only.
- **When the same feature has a document in several clones**, write only this repo's copy; never copy to or track the others.
- Document state machine: `in progress` → `pending input` → `executable` → `implemented` → `verified`. The state is never written by hand; derive it from the "check before writing" scripts.
- Events and bilingual text may be `pending`; logic and UI must reach a conclusion on every item, and undecided APIs still need their fallback written down.
- Values marked "suggested / candidate / to verify" in the backend contract are **blockers** and must be filled in before integration; when the contract changes during development, write it back on the spot.
- When the user says "start implementing" → stop and say this round only produces the document; execution is a separate turn.

## No information means pending (hard constraint)

When the PRD, backend contract, copy, events table or Figma is missing, **record it as pending — no association, no confirmation**.

- Write what is missing as `pending (missing X; owner: product / backend / design / analytics; action after it arrives: …)` and keep a row in the pending table.
- Never turn a missing field into a conclusion with "as usual / like the existing page / default first". Suggestions may only live inside the pending row.
- When the backend gives no value list, state machine or enum, all state mapping is pending. **Never** backfill each state into some known value (mapping every review-card state to `okay` is exactly this failure).
- Copy without a key, without zh/en: `pending (missing copy key)`; events without a table are pending — never invent event names.
- A verbal "it should be / probably" → `pending (verbal, not in the contract)`, never promoted to a conclusion.
- Tag every pending item with a blocking level: **blocks development** / **blocks integration** / **not blocking**.
- The document header always carries `Blockers: dev <X> / integration <Y> / none <Z>`, counted from the pending table, recounted on the spot.
- When state and counts disagree, counts win: `X>0` → in progress (or pending input); `X=0` → executable.

**Exception: implementation details are not missing information.** Missing route params the app builds itself, URL / query length, external deep-link compatibility, toast component choice, retry counts, naming and layering only change how something is written: never ask, write the default and mark it `implementation default (no confirmation needed)`.

## Skeleton first (the first two rounds do only this)

Expanding into per-control tables before the structure is settled makes the implementer invent the layering — a transparent app bar over nothing, stacked cards, content under a fixed bar. Before per-control work, any feature point with a Figma design does three things:

1. **Draw the layering**: list every layer bottom-up (page fill / gradient / fixed bar / scroll area / overlay / keyboard bar), and state which one scrolls, which is fixed, which is pushed up by the keyboard, which shows the layer below.
2. **List the card order**: one row per card top-down inside the scroll area, marking which ones are their own container (white card / radius / padding); never flatten them into one row.
3. **Confirm once with the user**: describe that skeleton in plain language (no node ids), and only then fill the per-control and asset tables.

Write it into `### Visual skeleton`:

| Layer / block | Position | Scrolls / fixed | Container (fill / radius / padding) | Relation to the neighbour layer |

Do not fill `### Visual spec` or `### UI assets and icons` before the skeleton is complete. When the user already gave the structure (e.g. "gradient at the bottom, then TitleBar / ScrollView / BottomBar"), record it as given — do not re-ask.

## Change boundary (challenge it while writing: decide what changes first)

Unexpected edits during execution happen because the boundary never made it into the document. Before writing each feature point:

1. **Find callers**: use codegraph (`codegraph_explore`) first for callers and reuse points of the target symbol / component / state-mapping function; with no index or no hit, use one targeted `rg`. Record only the call sites whose behavior changes.
2. **Challenge first**: turn "changing it this way also touches N call sites / shared component X" into one question in the four-line format. At most one scope question per feature point.
3. **Fill the table**: after the user decides, write it into the "Change boundary" table. Files outside the table are not to be touched.
4. **Conservative by default**: reuse existing components, state mapping and event report points; no opportunistic refactors, no extracting shared components.
5. **Respect the table while executing**: only rows marked `change` / `add` may be touched; a diff elsewhere is out of bounds and needs a decision row in the document first.

## Question layout (hard constraint)

Every question to the user uses this blank-line separated, bold-label layout — never four consecutive lines:

These four blocks are exempt from commander's "≤3 supports" and "≤{{STYLE_MAX_LINES}} lines" budgets; at most 3 questions per round, one block each, one blank line between blocks.

**Question**: <one line, pinned to a field or a branch>

**Evidence**: <evidence from code or PRD: file:line / API path / existing key or event name; for UI, name the block, the control and the state in plain words>

**Suggested**: <what to take when the user gives no answer>

**Options**: <A / B / C>

Layout rules: bold labels as `**Question**`, blank line between blocks, full-width colon.

**No node ids in the conversation**: questions and evidence use plain descriptions (which block, which control, which state, which design version); node ids and Figma links belong in the task document. When the user says the reference is unclear, restate the same question in plain language instead of explaining the node tree.

## One round at a time

0. **Read the queue**: read `-queue-<feature>.md` (this round's questions plus the open list) and the document header first; `grep` only the feature sections being touched this round, never the whole document.
1. **Read the current state**: does what the PRD wants exist already, field names, API paths, existing l10n keys, existing events.
2. **List the gaps**: where the PRD and the code disagree, and what the PRD never said but development needs; sort by blocking level.
3. **At most 3 questions**: take the most blocking ones only, four-line format, then stop. With no blocking-development item, ask one question or close with defaults — never pad with non-blocking ones.
4. **Write the queue first**: the moment a question is sent, record it in the queue file (keyword + `asked, awaiting answer`).
5. **Write back after the answer**: run the backtracking below, edit the body, clear the queue, log the change, turn the queue row into a conclusion.
6. **Move to the next batch**: `grep` the queue keywords before asking; anything already answered or defaulted is off the table.

**Round budget**: a feature point gets **≤ 15 rounds** in the document phase. Still blocked at 15 rounds → write the suggested defaults, mark them `pending (defaulted by suggestion)`, and hand the remaining questions to the user in one go — another single-question round-trip costs more than the default. Only extend when the user explicitly says "keep asking".

Three questions per round is the ceiling; answering one of three is fine — update what came back and do not resend the rest.

## Backtrack after every answer

An answer can overrule earlier conclusions. Before editing the document, do four steps:

1. **Scope the impact**: which feature points, APIs, field mappings, UI, events, copy and acceptance items this answer touches.
2. **Rewrite the body**: rewrite the affected fields in place; the body never keeps two versions, only the change log keeps history.
3. **Clear the queue**: delete voided questions, drop or rewrite `pending` items that no longer matter, queue the new gaps.
4. **Log it**: `<old conclusion> → <new conclusion>` in the change log, set the queue row to `answered`, then ask the next batch (max 3).

When the impact reaches "goal and scope", rewrite the scope first, then the feature points. Never skip backtracking and jump straight to the next question.

## How to ask

All four labels are mandatory; layout as above.

- Never ask what the code or PRD already answers — look it up first.
- Never ask "should we add an event"; ask "does this exposure reuse `xxx` with a param, or a new event".
- Never ask "should we grey it out"; ask "after the quota runs out, is a tap silent or does it show toast `xxx`".
- Never ask "what does selection look like"; ask "does it recolor on tap, or wait for the response".
- Never ask "might the enum grow"; read the existing mapping, then ask "on a value outside the document, drop it or read-only".
- Never ask "what if the API fails"; ask "when the detail API fails, is it in-card error copy + Retry (that card only) or a full-page error page".
- Never ask "what if the response is partial"; ask "when PATCH returns `permissions` but not `selection`, keep the local selection or clear it".
- Never ask "do we need caching"; ask "does a cache hit still fire the GET; which key merges 5 triggers in a second".
- Never ask "is there a timeout"; ask "how many seconds do we wait for the ack; which field resets, and what does the user see".
- An answer of "not sure / later" → record `pending` with owner and what is missing, move on.
- Several answers or extra context at once: apply each by blast radius, backtrack, then ask the next batch (max 3).
- Two rounds without a conclusion on the same question: write the suggestion into the document and mark `pending (defaulted by suggestion)`.

### What not to ask (decide implementation details yourself)

Anything that only changes how it is written, not what the user sees:

- **App-built route params**: a missing `orderId` / `productId` is an implementation bug — write "required, treat as implementation error", no toast / error-page branch.
- **URL and query length**: in-app navigation has no hard limit, always `encodeComponent`, no `extra` fallback.
- **Route compatibility**: replace the old entry point; no redirect, dual-track or param repair for external deep links.
- **Toast component choice** (SnackBar / CenterToast / dialog), retry counts, skeleton style: follow the repo convention, mark `implementation default`.
- **Code structure and naming** (extract or not, class names, file locations): follow the repo rules, never a question.

One rule: changes what the user sees, what the backend receives or how data is computed → ask; only changes how it is written → do not.

## Splitting feature points

- One item = one entry point + one outcome the user can verify alone.
- Number them `F1 / F2`; split into `F1.1` when it spans two pages or touches more than 3 files.
- Never split client and backend into two items; the backend dependency goes under "data source and API".
- A failure state is not its own item, but every API gets a failure path in acceptance (offline / 5xx / timeout).
- List the items that change existing behavior first, pure additions after.

## The four question classes

**Logic**: current state (file:line), what changes, entry point, data source (method + path, request timing, params), new field or changed field, field → UI mapping, empty / failure / logged-out / repeated tap, cache and refresh timing, shared call sites affected, experiment or rollout needed.

**Function and UI**: UI and interaction are written together. Three steps — list the elements (PRD copy, Figma blocks, existing interactive elements: one row each); run the matrix (every element gets a row in "interaction state"; a missing row is unfinished, and "same as above" never covers a difference); tag the assets (every icon / image gets its source in the "UI assets and icons" table; a lookalike is never a source).

**Events**: whether, event name (reuse or new), report timing, non-report conditions, params and where values come from, exposure rule, channel, report point. Layout per tracking-doc-format.

**Bilingual**: three classes of keys — backend-provided copy, client fallback copy, error and hint copy. Writing only the first is a gap; a fallback branch without a key is `pending (missing fallback copy key)`.

Full criteria, counter-examples and the four recurring traps (wrong icon / wrong state mapping / missing interaction / drifting anchor) live in {{SKILL_DIR}}references/checklists.md.

## Required tables (checklist in references/checklists.md)

Eleven tables plus 6b visual spec. Headers and criteria are not duplicated here; read the matching section of {{SKILL_DIR}}references/checklists.md when filling one:

1. Interaction state matrix · 2. Permission and quota two-state · 3. Backend enum and unknown value · 4. API failure and degradation · 5. UI assets and icons · 6. State → visual · 6b. Visual spec per block · 7. Partial response and missing fields · 8. Identifiers and external input · 9. Request budget and cache · 10. Awaiting an external callback · 11. New abstraction contract

A table that does not apply is not deleted and not padded: write `Table applicability: skip permission (no backend field in this feature)` and `validate_task_doc.py` accepts it; a skip without a reason is a WARN.

## Figma evidence and asset pipeline

**Evidence first, conclusions after.** With a Figma link and Figma tools (figma MCP) available:

1. **Dump once**: dump every node the document needs per {{SKILL_DIR}}references/figma-node-dump.md into `docs/<feature>/nodes.tsv` (id / type / visible / name / parent chain / text / fills / size / position).
2. **Read the dump before writing**: `type=TEXT` with text is copy, not an asset; `visible=hidden` is reference only and never a source of copy or visuals; the parent chain must name this feature's frame — a mixed frame is invented UI.
3. When the node cannot be read (no permission / missing node / login required) write `pending (missing figma node <id>)` and never guess pixels from PRD prose. When MCP copy conflicts with the user or the visible frame, the user wins — note the source.

**Compare and land the assets** (done in the document phase, never deferred):

1. `download_assets { fileKey, nodeId, defaultScale: 3 }`, read back `export.sizeBytes` (PNG@3x) and `svgAssets[0].sizeBytes`.
2. **Compare bytes only**: take the smaller one (SVG on a tie).
3. **PNG** → download the @3x original from `rawImages` (alpha preserved); **never** the flattened `export` (no alpha, white or black baked in). Then run `{{SKILLS_ROOT}}figma-mcp-assets/scripts/optimize_png.sh` (lossless only); the file must not grow.
4. **SVG** → download as is, no compression, no PNG conversion.
5. Land under `assets/images/<feature>/...`; subdirectories must be declared in `pubspec.yaml`; filenames match the asset table.
6. **Run the gate**: write a manifest (path / logical width / logical height / `alpha` or `opaque`) and run
   `bash {{SKILL_DIR}}scripts/check_assets.sh --repo <repo root> <manifest>`, pasting the output into the reply.
   `RGBA + transparent pixels + size = logical × 3` passes; `no alpha channel = flattened export` must not land — go back to `rawImages` or ask design for a transparent export.
   When the node itself is an opaque screenshot (a full example photo), mark it `opaque` in the manifest and note "container clips the radius" in the asset table; never treat it as a transparent asset.

## When the environment lacks a tool

Without shell / network / Figma tools, neither pretend nor leave a command template and call it done:

- Mark the step `pending (no <shell / network / figma> tool in this session; owner: implementation round; action: …)` with blocking level **blocks development** — assets that never landed block the work.
- Say plainly in the reply that assets were not landed this round and that the implementation round must run the pipeline and `check_assets` first; write the same line into the handoff.
- The implementation round starts by filling that step (see "Implementation check"), not by writing UI.

## Events via tracking-doc-format

Writing `### Events` follows tracking-doc-format's layout and flow, but the output lands in this task document:

- **Same layout**: the event name in bold on its own line; `**Report timing:**`; `**Params:**`; param rows `- **name**: type. description`; value rows `  - value: <expression> (file:line)`. Separate events with `-----------`.
- **Same one-at-a-time review**: one event per round, next one after the user confirms; the conversation shows only that event plus the document path.
- **No separate document**: no `docs/{{DOC_PREFIX}}<date>-tracking-<feature>.md` unless the user explicitly asks.
- **The report point is the boundary**: every event names its report point — an existing `file:line`, or `to be added`; a file outside the change boundary table may not be edited for an event.
- **Never invent params**: values need code evidence; when there is none write `value: not found` / `to implement (candidate X)`.

## The task document

Copy the field names and order. Write `pending` or `none` instead of leaving a placeholder.

```markdown
# task-<feature>

State: in progress | pending input | executable | implemented | verified
Blockers: dev <X> / integration <Y> / none <Z>
Source: <PRD file / link / Figma node-id>
Updated: <YYYY-MM-DD> round <N>

## Goal and scope
Goal: <one line>
In scope: <F1, F2…>
Out of scope: <explicitly excluded>
Modules affected: <page / component / API / events / copy>

## Change boundary
| # | Feature point | File / module | Action | What changes here | Blast radius (call sites / shared) | Decision source |

Action is only `change` / `add` / `read-only reference` / `forbidden`.

## F1 <feature name>
State: confirmed | partly pending | implemented | verified
Table applicability: skip <table> (<reason>)

### Logic
- Current state:
- Change:
- Data source and API:
- Mapping to UI:
- Edges and errors:
- Blast radius:

### Function and UI
- Position:
- Trigger:
- Layout:
- Components:
- States:
- Interaction:
- Figma:

### Element list
- <button / option / icon / input / scroll container / dialog / placeholder>: behaviour in one line

### Visual skeleton
| Layer / block | Position | Scrolls / fixed | Container (fill / radius / padding) | Relation to the neighbour layer |

### Visual spec
| Block | Figma node | Text (size / line height / weight / colour) | Size and radius | Padding and gap | Asset logical size |

### Interaction state
| Control | Type | On tap | Before response | After response | Failure / over quota | Re-tap on selected |

### Permission and quota
| Field | Source API | UI when false / used up | Feedback when the user still taps |

### Enum and fallback
| Field | Values | Unknown value handling |

### State → visual
| Backend field | Values | Visual (colour / icon / copy key) | Tappable | Reported |

### UI assets and icons
| Control / area | Reused component | Icon / image | Source | Export | Size and theme fit |

### API failure and degradation
| API | Failure scope | Copy (key) | Retry | Refresh range after retry |

### Partial response and missing fields
| API | Response field set | Missing field handling | May override newer local value |

### Identifiers and external input
| Identifier / input | Source field (sender) | Same key on the receiver | Format constraint | Encoding and sanitation | Missing / invalid |

### Request budget and cache
| Trigger | Requests | Dedupe key | Cache TTL / freshness | Cleanup timing |

### Awaiting an external callback
| Chain | Waits for | Timeout | State restored after timeout | User-visible feedback |

### New abstraction contract
| New abstraction | Consumers (all call sites) | Default params allowed | Same source as the single truth | Out of range / invalid |

### Events

Conclusion: needed or not / reuse or new

**<event_key>** (<short name>)

**Report timing:** <one line>

**Params:**

- **<param>**: <type>. <description>

  - value: <expression> (<file>:<line>)

**Report point**: <file>:<line> or to be added (<feature point / entry>)

-----------

Non-report conditions: <dedupe / second visit / collapsed / logged out>; write `none` when there are none.

### Bilingual
- Conclusion:
- Fields:
- Key plan:

### Acceptance
- <tap this → see that>, every line reproducible by tapping; sentences such as "per the API response" are not acceptance criteria

## Pending items
| # | Feature point | Category | What is missing | Blocking level | Owner | Action after it arrives |

## Question log
| Round | Question keyword | State | Conclusion / landing point |

State is only `answered` / `defaulted` / `asked, awaiting answer` / `void`.

## Risks and dependencies
- <risk / external dependency / party to integrate with>

## Change log
- <YYYY-MM-DD> round <N>: <what this round added or changed>
```

The queue file `docs/{{DOC_PREFIX}}<date>-queue-<feature>.md` holds only two sections and stays under 40 lines: `## This round` (at most 3 questions) and `## Open questions` (sorted by blocking level). The question log stays in the task document; the queue is a short-lived progress cache, cleared when the round closes.

The change log keeps the last 20 rounds; older ones collapse into one line `<YYYY-MM-DD> rounds 1–<N-20>: <one-line theme>`.

## Check before writing (run the scripts, never self-attest)

After editing the document **run the scripts and paste the output into the reply**; do not tick boxes from memory:

```bash
python3 {{SKILL_DIR}}scripts/validate_task_doc.py docs/<task document> \
  --repo <repo root> [--nodes docs/<feature>/nodes.tsv] [--manifest <asset manifest>]
bash {{SKILL_DIR}}scripts/check_assets.sh --repo <repo root> <asset manifest>
```

- On `validator: N fail` the state may **not** change; fix each FAIL. `--legacy` downgrades structural problems for old documents only — assets, nodes and sizes are never downgraded.
- Two things the scripts do not judge, check by hand and note in the reply: (1) each behaviour has exactly one definition across body / steps / forbidden list / acceptance / request budget; (2) the handoff steps do not contradict the last change-log round.

## Definition of done

All eleven must hold before the state becomes `executable`:

1. Every feature point has conclusions for logic, UI and acceptance; missing input is marked pending and no "blocks development" item remains.
2. `### Visual skeleton` is filled layer by layer and confirmed once by the user; every fixed bar, scroll area and overlay has an owner.
3. The change boundary table has at least one row per feature point with `change` / `add` / `forbidden`; the blast radius comes from codegraph or a targeted search.
4. Every listed element has an interaction-state row; every icon has a source and an export; every `add` asset **has landed** and passes `check_assets.sh` (RGBA + transparent pixels + size = logical × 3).
5. Every backend status field has a full "state → visual" mapping with a decision for unknown values; without the enum the document cannot be executable.
6. Events follow tracking-doc-format inside this document, each with a report point and value evidence.
7. Every API has failure scope / copy / retry / refresh range; every acceptance line is "tap this → see that", with one failure path per API.
8. Every write API has a "partial response" row and states the parse order (permissions and state first, business fields second).
9. Every cross-boundary id has an "identifiers" row; unknown ones are pending, never assumed equal.
10. Every repeatable request has a "request budget" row, every awaited chain has a timeout and state restoration, and every new abstraction has a contract row.
11. `validate_task_doc.py` reports 0 fail; every node in the document exists in `nodes.tsv` and its parent chain belongs to this feature's frame.

## Implementation check

A written document does not mean the code followed it. Both cases use this section, read-only: the user says "implemented / review it / anything missing", or the document has been handed to an implementer.

**Three things at the start of the implementation round** (written into the handoff, not waiting for the user):

1. Run `validate_task_doc.py` and `check_assets.sh` and paste the output; on FAIL stop and fix the document first — never start with known defects.
2. Walk the change boundary table with `rg` for every real landing point (`file:line`); a change not in the table is one out-of-bounds finding.
3. Compare block by block against the visual spec: is the app bar / status bar fill visible, is copy cut off with an ellipsis, do thumbnails match the design's logical size.

Then check the code table by table (matrix against `onTap` and disable conditions, permissions against enforced `can_*`, enums against values backfilled as valid, partial responses against parse order, identifiers against send/receive key equality, request budget against duplicate fetches, timeouts against `finally` restoring state) and number the findings:

- `W-001` (causes wrong behavior) / `I-001` (inconsistent or to confirm), one line each: symptom + `file:line` + what the document requires; give the list and let the user pick — never start fixing.
- When code and document disagree, first decide whether the implementation or the document is right; when the document is wrong, write it back on the spot (`<old conclusion> → <new conclusion>`); list W only for implementation errors.
- After checking, set each feature point to `implemented` or `verified` and record open items under "risks and dependencies".

## Later additions

- After the user provides events or copy: change only the matching sections, turn `pending` into conclusions, sync the pending table and the change log, re-derive the state.
- An out-of-table change during execution: stop, add that file to the change boundary table with its decision source, then continue.
- When the backend contract or product definition changes: immediately write back the affected feature points, required tables, change boundary and change log as `<old conclusion> → <new conclusion>`.
- Backfill after development: classify the fixed bugs by "which table was missing", add them to the matching sections, and add a same-kind check to the definition of done.
- Continuing in another session: read the queue file and the document header (state, blocker counts), the pending table, then the last few change-log rounds; resume from the first `asked, awaiting answer` row so the user never re-answers.
- When the edit is larger than a third of the document, re-run `validate_task_doc.py` instead of reusing an old PASS.

## Visible reply

- First line: one sentence of progress — how many items confirmed / how many remain + blocker counts + document path.
- Then this round's questions (at most 3, sorted by blocking level; with no blocking-development item, one question or a direct close) in the four-line format, bold labels, blank lines between blocks, no preview of later ones.
- A skeleton round shows only the skeleton table plus one line "is this the structure to build", never mixed with per-control questions.
- In an events round that one question is the event itself, in tracking-doc-format's layout instead of the four lines.
- A check round asks nothing: numbered W/I list first (wrong-behavior items first, at most 5 plus a total count).
- A document-round reply carries three hard evidence lines: `validator: N fail / M warn`, `check_assets: N fail`, and the path of the added / changed document; whenever a script or an asset changed, add its generated path and write time.
- Right after the change boundary is set, add one line `- Change boundary: change N / add M / forbidden K`, naming the shared points affected.
- Never paste the whole document, never restate the PRD, no summary paragraph.
- With no questions, close with one line: document executable + path + next step.
