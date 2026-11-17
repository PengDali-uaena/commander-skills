# prd-to-task

Turns a PRD into one `task-<feature>.md` that can be developed from, through several rounds of Q&A.

Conversation only, code reading only, and only this one document. No business code.

Triggers: importing a PRD / splitting requirements / pinning down requirement details / listing feature points / adding events or copy to a task / the user names prd-to-task.

## Boundaries

- No business code, no editing the PRD source, no branches, no builds.
- Read only code the PRD points at: pages and components it names, same-name or adjacent features, API definitions, l10n files, event constants. Stop once the current question is answered.
- Write one file only: `docs/{{DOC_PREFIX}}<date>-task-<feature>.md`. `<date>` is `YYYYMMDD`, `<feature>` is a short English kebab-case name; create `docs/` when the project has none.
- **When the same feature has a document in several clones**, write only this repo's copy; never copy to or track the others, and when sharing is needed write "read-only reference to this document" in the current one. Same-name documents must keep an empty diff, or differ only in repo-local paths.
- Document state machine: `in progress` → `pending input` → `executable` → `implemented` → `verified`. The state is never written by hand; derive it from the counts and check results of "check before writing".
- Events and bilingual text may be `pending`; logic and UI must reach a conclusion on every item, and undecided APIs still need their fallback written down.
- Values marked "suggested / candidate / to verify" in the backend contract (message type numbers, field names, content structure) are listed as **blockers** in the document and must be filled in before integration; when the contract changes during development, write the change back into the document and the change log on the spot.
- When the user says "start implementing" → stop and say this round only produces the document; execution is a separate turn.

## No information means pending (hard constraint)

When the PRD, backend contract, copy, events table or Figma is missing, **record it as pending — no association, no confirmation**.

- Write what is missing as `pending (missing X; owner: product / backend / design / analytics; action after it arrives: …)` and keep a row in the pending table.
- Never turn a missing field into a conclusion with "as usual / like the existing page / default first". Suggestions may only live inside the pending row, never as a conclusion.
- When the backend gives no value list, state machine or enum, all state mapping is pending. **Never** backfill each state into some known value (mapping every review-card state to `okay` is exactly this failure), and never improvise a mapping from a nearby enum.
- Copy without a key, without zh/en: `pending (missing copy key)`; do not substitute existing similar copy. Events without a table are pending — never invent event names.
- A verbal "it should be / probably" → `pending (verbal, not in the contract)`, never promoted to a conclusion.
- Tag every pending item with a blocking level: **blocks development** / **blocks integration** (no effect on coding, must be filled before release) / **not blocking**.
- The document header always carries `Blockers: dev <X> / integration <Y> / none <Z>`, counted from the pending table; recount on the spot after editing that table, never from memory.
- When state and counts disagree, the counts win: `X>0` → in progress (or pending input); `X=0 and Y>0` → executable (fill before integration); `X=Y=0` → executable. When a hand-written "executable" is overruled, change the state and note it in the change log.

## Change boundary (challenge it while writing: decide what changes first)

Unexpected edits during execution happen because the boundary never made it into the document. Check the blast radius before writing each feature point and put the boundary in the table:

1. **Find callers**: use codegraph (`codegraph_explore`) first for the callers and reuse points of the target symbol / component / state-mapping function; with no index or no hit, use one targeted `rg`. Record only the call sites whose behavior changes because of this work, and do not lay out file lists.
2. **Challenge first**: turn "changing it this way also touches N call sites / shared component X / shared mapping Y follows along" into one question in the four-line format. At most one scope question per feature point; never stack scope questions into a list.
3. **Fill the table**: after the user decides, write it into the task document's "Change boundary" table. Files outside the table are not to be touched by default.
4. **Conservative by default**: reuse the existing components, state mapping and event report points; no opportunistic refactors, no extracting shared components, no changing shared call sites' styles or defaults. Touching a shared point requires its own row with the blast radius written down.
5. **Obey the table during execution**: only rows marked `change` / `add` may be edited; a diff anywhere else is out of bounds — go back, add the decision row, then act.

## Question layout (hard constraint)

Every question to the user must use the **blank line between blocks + bold labels** shape below — never compressed into four consecutive lines:

These four blocks are exempt from commander's "≤3 supports" and "≤{{STYLE_MAX_LINES}} lines" budget (they are listed as a field-block structure in commander's hard constraint 1 and AGENTS "field-block output" rule 6); still ask only 1 question per turn.

**Question**: <one sentence, landing on a field or a branch>

**Basis**: <evidence from code or PRD: file:line / API path / existing key or event name>

**Suggestion**: <what happens when the user gives no answer>

**Alternatives**: <A / B / C>

Example:

**Question**: Does the support invitation card go out as an IM message or a backend push?

**Basis**: `chat_page` already has a custom message type; the support-side source is undecided.

**Suggestion**: send it as an IM message and make the backend delivery a separate task.

**Alternatives**: A IM message / B backend push / C both

Layout notes: labels are written bold as `**Question**`, not `Question:`; one blank line between the four blocks; full-width colon after the label. This counts as a field block (commander "field-block layout" rule 8 exception: no `- ` prefix, blank line between blocks) and is not bound by the ≤{{STYLE_MAX_LINES}}-line body limit.

## What one turn does

1. **Read the document**: read an existing task document first; never re-ask what is answered.
2. **Read the current state**: check whether what the PRD wants exists today, plus field names, API paths, existing l10n keys and existing event names.
3. **List the gaps**: where PRD and code disagree, and what development must decide but the PRD does not say.
4. **Ask only 1**: pick the one that blocks most, ask it in the four-line format, then stop and wait.
5. **Back-propagate and write**: after the answer, run the impact pass below, edit the body, clear the queue, record the change.
6. **Ask the next 1**: advance one question per turn, never several at once.

Write to disk at the end of every Q&A round; never batch it to the last round.

## After an answer, back-propagate first

Answers and extra information can overturn earlier conclusions. Do these four steps before editing the document:

1. **Scope the impact**: which feature points, APIs, field mappings, UI, events, copy and acceptance items this answer touches.
2. **Edit the body**: rewrite the affected fields directly; the body never keeps old and new versions, and old conclusions go only into the change log.
3. **Clear the queue**: delete void questions, drop or rewrite invalidated `pending` items, and queue newly discovered gaps as the next question.
4. **Record it**: write `<old conclusion> → <new conclusion>` in the change log, then ask the next single question.

When the impact reaches "goal and scope", change the scope first, then the feature points. No round may skip back-propagation and go straight to a question.

## How to ask

All four labels are mandatory; layout per the section above.

- Do not ask what code or the PRD can answer; look it up first.
- Never ask "should we add an event"; ask "use the existing `xxx` event with a new parameter, or add an event".
- Never ask "should it be greyed out when out of quota"; ask "when the quota is used up and the user taps, is it silent or a `xxx` toast".
- Never ask "what is the selected effect"; ask "does it change color on tap, or after the response arrives".
- Never ask "will new enum values appear"; read the existing mapping and ask "when a value outside the document appears, drop it or render read-only".
- Never ask "what if the API fails"; ask "when the review-card detail API fails, does the card show error copy + Retry (refetching that card only), or does the whole page become an error page".
- Never ask "should we retry"; ask "is Retry single-flight disabled or can it be tapped repeatedly; what fallback after N failed retries".
- Never ask "what if the response lacks fields"; ask "when PATCH returns only `permissions` and not `selection`, keep the local selection or clear it, and do we merge permissions before judging business fields".
- Never ask "which id"; ask "the sending side uses `peerId` and the receiving side uses `conversationID` — are they equal, and if not, which one do we change".
- Never ask "should we cache"; ask "on a cache hit do we still send GET; when the same object fires 5 requests within a second which key merges them; which keys are cleared on logout".
- Never ask "is there a timeout"; ask "how many seconds at most do we wait for the send receipt; after the timeout which field resets and what does the user see".
- "Don't know / later" → record `pending` with the owner and what is missing, then continue to the next question without stalling.
- A vague answer → ask once more; still vague → `pending (answer was vague)` plus the suggested default.
- One answer covering several questions or extra information: land each item into its field by impact, back-propagate, then ask the next single question.
- The same question twice with no conclusion: write the suggestion into the document and mark `pending (defaulted to the suggestion)`.

## Splitting feature points

- One item = one entry point + one outcome, verifiable by the user on its own.
- Number them `F1 / F2`; when it spans two pages or changes more than 3 files, split into sub-items `F1.1`.
- Never split client and backend into two items; backend dependencies go under "data sources and APIs".
- API failure states do not become their own feature point, but every API must leave one failure path in acceptance (offline / 5xx / timeout).
- List high-risk items that change old behavior first, pure additions after.

## Four question categories

### Logic

Must state: current state (file:line), what changes, trigger entry point, data source (API method + path, request timing, parameters), whether fields are new or changed, field→UI mapping, empty data / failure / unauthenticated / repeated taps, caching and refresh timing, whether shared call sites are affected, whether an experiment or rollout is needed.

Two more are missed most often and must be their own sentences:

- **Repeated tap on the same value**: tapping an already-selected option — does it send a request, does the client block it locally, and is the user told when it is blocked.
- **In-flight race**: for "read then write" on the same object (detail GET in parallel with submit PATCH), can a stale response overwrite a new submission; choose and pin down one of request sequence number, in-flight marker, or discarding stale responses.

### Features and UI

UI and interaction cannot be written apart: the same element needs both "what it looks like" and "what happens when tapped". Three steps per feature point:

1. **List the elements**: derive what interactive elements this page needs from three sources — actions mentioned in the PRD copy, blocks and icons in the Figma frame, and buttons / options / inputs / scroll containers / dialogs / placeholders already present in existing components. One element per line, at the start of the feature point.
2. **Walk the matrix**: every element in the list must have a row in the "interaction state matrix"; a missing row is not done, and "same as above" may never absorb a different element's differences.
3. **Tag the assets**: every icon / image / illustration gets its source in the "UI assets and icons" table; never leave "use a similar icon".

Must state: page and area position, appearance conditions, layout structure (horizontal scroll / list / fixed height / dialog height), spacing and size units, reused shared components, loading / empty / error states, scrolling and keyboard, interactions (tap / long press / swipe / back / second confirmation / toast), tap targets, Figma link including node-id.

Style and state are written apart: color values, borders and radii are only what it looks like "after the response"; the tap instant, pre-response and failure rollback are unfinished if unwritten — fill them per the "required tables" below, control by control.
The API layer goes through tables too: every request (including detail, stats and recommendation slots fetched inside a card) needs its failure landing spot, copy and retry conclusion, per "4. API failure and degradation".

**Figma is mandatory**: when a link exists and Figma tools (figma MCP) are available, read the node first and put sizes, spacing, radii, colors, font sizes, weights, icon names and node-ids into "layout" and "UI assets and icons"; when it cannot be read (no permission / node missing / login needed) write `pending (missing figma node <id>)` and do not guess pixels from PRD prose.

**Four common UI-restoration traps, pinned down in this section**:

- **Wrong icon**: only three sources — an icon inside Figma (node-id) / an existing repo asset or iconfont (file:line) / to be added (size, format, naming). No free improvisation beyond the third.
- **Wrong state mapping**: **every** value of a backend field needs a visual and a tappability; never write only the normal state, and never backfill an unknown value into a valid state — see "6. State → visual mapping".
- **Missed interaction**: the element list and the matrix row count must match; non-tap behaviors such as closing a dialog, going back, scrolling to the end, keyboard occlusion and second confirmation are elements too.
- **Anchor drift**: any element positioned by copy width or by "the content area" (badges, indicators, bubbles, dividers) must state its position in both en and id copy, or be re-anchored to the icon / fixed coordinates; "relative to the content area" is not pinned down — `Messages` and `Pesan` have different widths, so the element shifts, and a geometry fix is only found in self-test.

### Events (linked with tracking-doc-format, may be pending)

Must state: whether they are needed, event name (reused or new), report timing, non-report conditions (dedup / re-entry / collapsed / unauthenticated), parameters and their value sources, impression criteria (visible ratio / dwell time), reporting channel, report point.

Write per tracking-doc-format's layout and flow, with the content going straight into the task document — see "Events linked with tracking-doc-format" below. When the PRD ships an events table, follow it; when it does not, ask the owner and record pending — never invent event names.

### Bilingual (may be pending)

Must state: which copy is new, whether user-visible, whether keys already exist, that a shared call point with only the current page changing gets **a new key rather than editing the old one**, key naming suggestions, whether en / id both need translation, placeholders and concatenation, date and currency formats, whether backend copy is multilingual.

List keys in three categories; writing only the first is incomplete:

1. **Backend-delivered copy**: API field name + whether it varies with the `locale` parameter; the fallback when the backend does not deliver.
2. **Client fallback copy**: local enum fallbacks, empty data, placeholders after an unknown value is dropped, single-field degraded defaults — every fallback branch needs a key, otherwise `pending (missing fallback copy key)`.
3. **Error and toast copy**: network failure, timeout, business error codes, insufficient permission, retry button — one line each.

Hardcoded strings are forbidden: never write bare `'Retry'` or `'OK'` in code; fallback copy goes through l10n too.

## Required tables (every tappable control, every API, every async chain)

Filling the visuals does not mean the states are clear. Single choice, multi-select, exclusive groups, switches and submit buttons all need the first three tables; every API (including ones nested in a card) needs the fourth; every icon / image needs the fifth; every backend state field needs the sixth; every API with a write operation needs the seventh; every id passed across platforms or built into a URL needs the eighth; every request that can fire repeatedly needs the ninth; every chain waiting on an external callback needs the tenth; every constant / resolver / factory added by this requirement and referenced from several places needs the eleventh. A missing table is not done.

Tables 7–11 cause the most incidents in this repo: "succeeded but missing fields", "wrong id", "request storm", "callback never returns" and "a new abstraction's default value splitting one meaning into two algorithms" are not API failures and the first six tables cannot cover them.

### 1. Interaction state matrix

One row per control:

| Control | Type | Tap instant | Before response | After response | Failure / over limit | Repeated tap on selected |

- **Tap instant**: optimistic selection (color changes immediately) or wait for the API. If it waits, state what tells the user the tap was received (pressed state / loading / whole group disabled).
- **Before response**: can other options be tapped, can the user scroll away, can the server data be overwritten right now.
- **After response**: does the rendered selection follow the API or keep the local one; when the returned selection differs from local, which side renders.
- **Failure / over limit**: roll back to which version (pre-tap / last success), which toast, which copy key.
- **Repeated tap on selected**: send / block locally / deselect — pick one and pin it; also state whether tapping the selected option in a single-choice group equals deselecting.
- **Multi-select**: any cap, any select-all / clear, are existing selections kept after a rejection.
- **Group switching**: when the tier, tab or filter changes, is the other group's selection cleared or kept (cross-field coupling is the easiest to miss).

### 2. Permission and capacity field states

Backend `permissions`, `can_*`, `*_limit`, `*_count`, `expired` and `status` must never be dismissed as "reference only". One row per field:

| Field | Source API | UI when false / exhausted | Feedback when tapped anyway |

- "Tapped anyway" needs a conclusion: silent no-op / toast (copy key) / send the request and let the backend reject.
- Local locks and backend rejections must give the same feedback: never greyed out in one place and silent in another, and never blocked locally without telling the user.
- Client-derived lock states (computed from count and limit) need their rule written down, plus the default when the API omits the field.

### 3. Backend enums and unknown values

| Field | Values | Unknown value handling |

- Unknown enums default to **dropped or read-only**; backfilling into a valid business value is forbidden (dirty data then impersonates a real choice — icon, highlight and submitted value all go wrong).
- Client hardcoded mappings (icons, colors, event parameters) get one extra sentence: what the client does when the backend adds a value.
- When the PRD or plan assumes "enums only ever merge, never grow", record it under "risks and dependencies" instead of treating it as fact.

### 4. API failure and degradation

One row per API; APIs fetched separately inside a card or module (review-card detail, product-card stats, order-card status, recommendation slot) each need their own row — a page-level error alone is not enough:

| API | Failure landing spot | Copy (key) | Retry | Refresh scope after retry |

- **Failure landing spot**: whole-page error / block error / error inside the card / single-field degraded default — pick one and pin it. "API fails means page error" is not allowed by default; for a card-internal failure also state whether the rest of the rendered card stays and whether the skeleton holds its height.
- **Copy**: primary and secondary l10n keys, never reusing the list-page error copy; also state what shows at the instant of failure (skeleton / stale cache / placeholder).
- **Retry**: whether there is one; whether the entry is inside the card or page-level; whether retry shows skeleton / button loading / whole component disabled; anti double-tap (single-flight + minimum interval); retry cap and the fallback once exhausted.
- **Refresh scope after retry**: that card only / whole page / back to the list; whether the failure cache is cleared and dependent fields (counts, badges, quota) are refreshed too.
- **Automatic retry**: whether pull-to-refresh, page re-visible or network recovery re-sends; not writing it means it does not.
- **Empty vs failure**: 200 + empty data is the empty state, not a failure; write their copy and retry buttons separately.
- **Business error codes skip retry**: no permission, deleted, delisted get a degraded or navigation path, never the network-failure copy set.
- **Jitter threshold**: how long under a slow network before the failure state shows (so skeleton → error → data does not flash three times); write milliseconds or "no delay".
- **Events**: whether failures and retry taps are reported; goes in the events section.

When the PRD only says "show a failure toast" with no landing spot or retry, ask row by row through the table above; that is not confirmed.

### 5. UI assets and icons

One row per icon, image, illustration or placeholder:

| Control / area | Reused component (file or class) | Icon / image | Source | Size and theme |

- **Source is one of three**: a Figma icon (node-id) / an existing repo asset or iconfont (file:line) / to be added (format, naming, size). None of the three → `pending (missing icon source)`.
- **Forbidden**: "use a similar icon", "download one", "placeholder for now", and naming something yourself so development has to guess.
- Selected / disabled / light-dark theme adaptation goes on the same row; the default state alone is not done.
- Reused components must name the existing file and class; components written in this iteration are marked `new` and added to the "Change boundary" table.
- **Bitmap acceptance**: every new bitmap states "transparent background (no white fill / no full-frame white `rect` after export) + real pixels = design logical size × scale + lossless-compressed". When the Figma frame itself carries a white fill, the export steps must say how the white is removed or that the PNG is exported transparent; "the two files have different md5" alone is not an acceptance criterion.

### 6. State → visual mapping

One row per backend state field:

| Backend field | Values (all enums) | Visual (color / icon / copy key) | Tappable | Reported |

- **List every known value**, one per row; Loading, empty, failure, no permission and expired must be covered.
- **Unknown value / null / missing field gets its own row** with "dropped or read-only" plus the concrete behavior (e.g. default icon, no dialog, not tappable).
- **Never backfill an unknown or unconfirmed value into a valid business state** (e.g. rendering everything as an `okay` green check); with no value list, write `pending (missing backend enum, blocks integration)` and keep a row in the pending table.
- Copy is l10n keys, never hardcoded Chinese; the same state behaving differently at different entry points gets separate rows.
- Client-derived states (e.g. a lock computed from count and limit) need the rule and the default behavior when the field is missing.

### 7. Partial responses and missing fields

"Succeeded but the fields are incomplete" is easier to get wrong than a failure: when the server returns only `permissions`, only `selection`, or a single status field, whether the client keeps old values or clears them must be pinned down field by field. Every `PATCH` / `POST` / incremental update API needs a row:

| API | Response field combination | Missing field handling | May it overwrite a newer local value |

- List at least "A without B" and "B without A" combinations; without this row the implementation defaults to whole-payload replacement and drops the new permissions it just received.
- **Parse order**: merge `permissions` / state fields first, then judge business fields (`selection` / detail body); never `return` the original object just because a business field is missing.
- **Overwrite rule**: state whether a response older than the local version/timestamp is dropped or wins, and who wins between an in-flight request and a newer local write.
- **List and cache sync**: after a single-item update, whether the list is rewritten, reordered, and whether parent caches are invalidated.

### 8. Identifiers and external input

Any value passed across platforms, built into a URL, used as a cache key or used to locate a message goes through this table (a historic bug hotspot in this repo):

| Identifier / input | Source field (sending side) | Same key on the receiving side | Format constraints | Encoding and sanitizing | When missing / invalid |

- **Send and receive must use the same key**: state whether "send with A, receive with B" really are equal; when unsure write `pending (needs one on-device log comparison)` and never assume equality.
- **Message locator**: which key recall / dedup / ordering / navigation each use (`conversationId + msgSeq` or `messageId`); three inconsistent choices will mismatch.
- **URL building**: the id must be `encode`d; write one sentence each for length limits, allowed character set, and handling of whitespace and control characters.
- **External message bodies**: which shapes are accepted (string / JSON object / array / deep nesting), whether an abnormal shape drops the whole message or degrades, and no unbounded recursive parsing.
- **Cache key composition**: `<domain>:<userId>:<id>`, with the cross-user isolation stated.

### 9. Request budget and cache lifetime

| Trigger | Requests | Dedup key | Cache TTL / freshness | Cleanup timing |

- **Who fires the request**: first entry / list change / state change / returning to foreground / pull-to-refresh — write each; if "does a state change refetch" is unwritten it gets implemented as a full refetch.
- **Does a cache hit still fetch**: pin "hit means use" or "hit still refreshes"; for refresh, state the minimum interval and single-flight (concurrent merge).
- **Dedup key**: which key merges repeated triggers for the same object in a short window.
- **Cache lifetime**: write timing, expiry, capacity cap, and what is cleared on logout / account switch / session end / successful submit; cross-user data must be isolated by userId — no `clearAll` wiping other accounts, and in-memory state resets too.
- **What renders first**: when cache-then-remote, what shows before the response (skeleton / cache / empty), and whether the response rebuilds everything or updates locally.

### 10. Timeouts and recovery while waiting on external callbacks

Every "tap and wait for someone to answer" chain (HTTP, IM send receipt, `Completer`, platform channel, animation end) needs a row; an HTTP timeout alone is not enough:

| Chain | Waiting on | Timeout | State restored after timeout | User-visible feedback |

- **Timeout**: in seconds; also cover queue drops, network loss and background suspension — cases where nothing ever comes back.
- **State restore**: after a timeout the "requesting / disabled / single-flight lock" must be reset in `finally`; entry-level locks are the easiest to wedge permanently — name the fields restored.
- **User-visible feedback**: silent recovery / toast (copy key) / in-card error state — pick one and pin it.
- **Retry and idempotency**: is resending after a timeout safe (is there an idempotency key); if not, only manual retry is allowed.

### 11. New-abstraction contract

Whenever the document tells the implementer to "add a centralized X" (index resolution, state mapping, route / URL building, cache-key factory), it must pass this table. As soon as the same meaning has two algorithms, a default value quietly decides for the second one:

| New abstraction | Consumers (every call site) | Default parameter allowed | How it stays in sync with the single source of truth | Out of range / invalid |

- **Default parameter**: a default is allowed only when there is no second layout or second enum; with a second shape it is forbidden — every call site passes it explicitly, and a missing argument must fail to compile or trip an assertion, never silently compute the old shape.
- **List every call site**: `rg` all references into this table and mark each "passes it / to wire"; a call site missing from the table is a miss.
- **Same source of truth**: state who renders, who resolves, and whether both read the same value (same provider / same snapshot / same argument); one side reading the live value while the other reads a default is not allowed.
- **Range checks**: bounds, indices and limits follow the length of the set actually rendered — never a hardcoded constant or a carried-over default.
- **Files added during implementation are boundary too**: any class / file created while executing (central constant, resolver, registry) must be added to the document as a `add` row before it is written; a "add centralized X" instruction must have a placeholder row in the change-boundary table, not only in the implementation steps.

## Events linked with tracking-doc-format

When writing the `### Events` section, use tracking-doc-format's layout and flow, but **the output lands in the task document**:

- **Layout unchanged**: the event name is bold on its own line; `**Report timing:**`; `**Params:**`; parameter rows `- **name**: type. description`; value rows `  - Value: <expression> (<file>:<line>)`. Segments are separated by `-----------` with a blank line above and below.
- **One at a time unchanged**: confirm one event per turn, then the next; the conversation carries only the current event plus the task document path.
- **No separate document**: do not create `docs/{{DOC_PREFIX}}<date>-tracking-<feature>.md` and do not print the full events text in the conversation. Only when the user explicitly says "events should be their own document" does tracking-doc-format's own writing rule apply.
- **The report point is the boundary**: every event states its `Report point` — an existing `file:line`, or `to be added` (naming which feature point's which entry). A file outside the "Change boundary" table may not be edited just to add an event.
- **No invented parameters**: values need code evidence (`rg` the report key, then read the arguments); when nothing is found write `Value: not found` / `to implement (candidate X)` and never substitute an approximate field.
- When the events table itself is missing, record pending first and do not fill the section with assumed parameters.

## The task document

Copy field names and order exactly. When there is no content write `pending` or `none`, never leave blank placeholders.

```markdown
# task-<feature>

State: in progress | pending input | executable | implemented | verified

Blockers: dev <X> / integration <Y> / none <Z>
Requirement source: <PRD file / link / Figma node-id>
Updated: <YYYY-MM-DD> turn <N>

## Goal and scope
Goal: <one sentence>
In scope: <F1, F2…>
Out of scope: <explicitly excluded>
Affected modules: <page / component / API / events / copy>

## Change boundary
| # | Feature point | File / module | Action | What this iteration does | Blast radius (call sites / sharers) | Decision source |

Action is only `change` / `add` / `read-only reference` / `forbidden`. Execution may touch only `change` / `add` rows; `forbidden` rows must name the shared components, mappings and configs that must not move.

## F1 <feature name>
State: confirmed | partly pending | implemented | verified

### Logic
- Current state:
- Change:
- Data sources and APIs:
- Mapping to UI:
- Boundaries and exceptions:
- Blast radius:

### Features and UI
- Position:
- Trigger:
- Layout:
- Components:
- States:
- Interaction:
- Figma:

### Element list
- <button / option / icon / input / scroll container / dialog / placeholder>: behavior in one line

### Interaction states
| Control | Type | Tap instant | Before response | After response | Failure / over limit | Repeated tap on selected |

### Permission and capacity
| Field | Source API | UI when false / exhausted | Feedback when tapped anyway |

### Enums and fallbacks
| Field | Values | Unknown value handling |

### State → visual
| Backend field | Values | Visual (color / icon / copy key) | Tappable | Reported |

### UI assets and icons
| Control / area | Reused component | Icon / image | Source | Size and theme |

### API failure and degradation
| API | Failure landing spot | Copy (key) | Retry | Refresh scope after retry |

### Partial responses and missing fields
| API | Response field combination | Missing field handling | May it overwrite a newer local value |

### Identifiers and external input
| Identifier / input | Source field (sending side) | Same key on the receiving side | Format constraints | Encoding and sanitizing | When missing / invalid |

### Request budget and cache
| Trigger | Requests | Dedup key | Cache TTL / freshness | Cleanup timing |

### Callback timeouts
| Chain | Waiting on | Timeout | State restored after timeout | User-visible feedback |

### New-abstraction contract
| New abstraction | Consumers (every call site) | Default parameter allowed | How it stays in sync with the single source of truth | Out of range / invalid |

### Events

Conclusion: needed or not / reused or new

**<event_key>** (<name>)

**Report timing:** <one sentence>

**Params:**

- **<param>**: <type> type. <description>

  - Value: <expression> (<file>:<line>)

- **Report point**: <file:line> or to be added (<which feature point / entry>)

-----------

(next event, same format)

Non-report conditions: <dedup / re-entry / collapsed / unauthenticated>; write `none` when there are none.

### Bilingual
- Conclusion:
- Fields:
- Key plan:

### Acceptance
- <tap what → see what>, every line tappable into a result; sentences like "as the API returns" are not acceptance items

## Pending items
| # | Feature point | Category | What is missing | Blocking level | Owner | Action after it arrives |

## Risks and dependencies
- <risk / external dependency / party to integrate with>

## Change log
- <YYYY-MM-DD> turn <N>: <what was added or changed this turn>
```

The change log keeps a rolling 20 turns; earlier ones are compressed into one line `<YYYY-MM-DD> turns 1–<N-20>: <one-line theme>`, without dropping the source of old conclusions.

## Check before writing (run every turn, never from memory)

Run the table after writing the document and put the result on this turn's first line; failing any row blocks the state change:

| Check | Command / criterion | When it fails |
|---|---|---|
| Blocker counts | count `blocks development` / `blocks integration` / `not blocking` rows in the pending table and compare with the header `Blockers:` line | rewrite the header |
| Valid state | with a dev blocker → only "in progress / pending input"; otherwise "executable" is allowed | change the state + one line in the change log |
| Pending items listed | `grep -c 'pending'` matches the pending table rows; every row has a blocking level / owner / follow-up action | fill it in before writing |
| Tables not empty | every feature point's required tables 1–11 have a header row; when not applicable write `none (because …)` instead of an empty table | add the table or the not-applicable reason |
| Tappable acceptance | acceptance contains no unobservable sentences such as "as the API returns" or "displays normally" | rewrite as "tap what → see what" |
| Boundary obeys the table | every file mentioned in the document appears in the "Change boundary" table | add the row |
| Assets deliverable | every new bitmap states transparent background, scale and size basis; when the Figma node carries a white fill, the export steps say how it is removed | write the acceptance criterion |
| One behaviour, one definition | the same behaviour may appear only once across "body / implementation steps / forbidden list / acceptance / request budget": `grep` the keyword (loading, retry, pull-to-refresh, auto-refresh…) and check every hit against the last change-log turn | delete the old wording, keep only the decided one |
| Handoff section not stale | walk every step of "Handoff to the implementing agent" and the "forbidden" list against the last change-log turn; anything a later turn overturned is rewritten on the spot | rewrite the steps; never keep an overturned conclusion as history |

Do not pile check results into the document body; only the counts go into the header and the first line.

## Definition of done

Ten conditions must all hold before the state becomes "executable":

1. Every feature point has conclusions for logic, UI and acceptance; items without information are marked pending and no "blocks development" item remains.
2. The change boundary table has at least one row per feature point, with `change` / `add` / `forbidden` stated; the blast radius comes from codegraph or a targeted search, not from guessing.
3. Every control in the element list has an interaction-state row; every icon has a source (Figma node-id / existing asset / to be added), with no "similar icon".
4. Every backend state field has a full-enum "state → visual" mapping, and unknown values have a drop-or-read-only conclusion; without the backend enum, it cannot be marked executable.
5. Events are written into this document per tracking-doc-format's layout, each with a report point and value evidence; no events table means pending.
6. Every API has a failure landing spot / copy / retry / refresh scope; every acceptance line is "tap what → see what", and every API has at least one failure path; when visuals are added or changed, acceptance carries one line each for en and id copy (badges, indicators and copy-anchored button widths need both).
7. Every API with a write operation has a "partial responses and missing fields" row stating the parse order (permissions/state first, business fields after).
8. Every cross-platform id has an "identifiers and external input" row: same key on both sides, encoding, abnormal shapes, cache key; anything uncertain is pending rather than assumed equal.
9. Every request that can fire repeatedly has a "request budget and cache" row (dedup key / freshness / cleanup / cross-user), and every chain waiting on a callback has its timeout and state restore.
10. Every abstraction added in this requirement and referenced from several places has a "new-abstraction contract" row: default-parameter policy, every call site, sync with the single source of truth, range handling; a document that says "add a centralized X" without that row may not be marked executable.

When these do not hold, keep "in progress" or "pending input" and name the highest blocking level items on the first line of the reply.

## Implementation check (when the user says it is implemented / asks for a review)

A finished document does not mean the code followed it. Both cases use this section, read-only: the user says "implemented / review it / anything missing"; or the document has been handed to an implementer (including another agent) — write "run the implementation check yourself before committing" into the handoff, so it does not wait for the user to ask; then output the W/I list and write the feature-point states back.

1. **Locate**: read the document's "Change boundary" table first, then `rg` each row for its real location (`file:line`); any change not in the table is one out-of-bounds finding.
2. **Check table by table**: go through required tables 1–10 against the code — interaction matrix against `onTap` and disable conditions; permission table against whether `can_*` is really enforced; enum table against unknown values being backfilled as valid; partial responses against parse order; identifiers against send/receive key equality; request budget against duplicate fetches; timeout table against `finally` restoring state.
3. **Numbered output**: `W-001` (causes wrong behavior) / `I-001` (inconsistent or to confirm), one line each: symptom + `file:line` + what the document requires; give the numbered list first and let the user pick — never start fixing.
4. **Conflict call**: when code and document disagree, first decide whether the implementation or the document is right; when the document is wrong, write it back on the spot (change log `<old conclusion> → <new conclusion>`); list W only for implementation errors.
5. **Wrap up**: after checking, set each feature point's state to `implemented` (code exists, not checked item by item) or `verified` (all tables checked, W items cleared), and record the open items under "risks and dependencies".

## Later additions

- After the user provides events or copy: change only the matching sections, turn `pending` into conclusions, sync the pending table and change log, and re-derive the state.
- An out-of-table change during execution: stop, add that file to the "Change boundary" table with its decision source, then continue; never widen scope by verbal permission.
- When the backend contract or product definition changes during development (field names, message type numbers, content structure, state machine, enum values): immediately write back the affected feature points, required tables, change boundary and change log, with `<old conclusion> → <new conclusion>`.
- Backfill after development: classify the fixed bugs by "which table was missing", add them to the matching sections so the next similar requirement can fill the table directly, and add a same-kind check to the definition of done for each missing table.
- Continuing in another session: read the task document header (state, blocker counts) and pending table first, then the last few change log turns, and resume from the first unfinished field so the user never re-answers.
- When the user wants to develop from the document: say this round only produces the document and execution is a separate turn; pin "the implementer runs the implementation check before committing and writes the W/I list plus feature-point states back" into the handoff, then review it after execution.

## Visible reply

- First line: one sentence of progress — how many items confirmed / how many remain + blocker counts + document path.
- Then only this turn's 1 question, in the four-line format with bold labels and blank lines between blocks; no second question, no preview of later ones.
- In an events turn, that 1 question is the current event itself, written out per tracking-doc-format's layout (event name / report timing / params / values / report point) instead of the four lines.
- A check turn asks nothing: give the numbered W/I list first (wrong-behavior items first, at most 5 plus a total count), each line `W-00N symptom (file:line) → what the document requires`, and wait for the user to pick — never start fixing.
- Right after the change boundary is set, add one line `- Change boundary: change N / add M / forbidden K`, naming the shared points that will be affected.
- Never paste the whole document, never restate the PRD, no summary paragraph.
- When there is no question, close with one line: document executable + path + next step (fill pending / start development in another turn).
