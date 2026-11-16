When a skill just disappointed you, or the two sides' rules start to diverge, bring over the criteria the other side has already proven; never copy a whole file.

Default direction: read Cursor, change this side (Pi / DSH). When the user says "the other way / push it to cursor", invert the direction. Shared bodies live in `~/.agents/skill-src/`; criteria changes go there first, then run `dist.mjs`. This skill handles only "the other side has a new item, this side does not".

## Conventions of both sides (carry criteria, not syntax)

| | Pi / DSH | Cursor |
|---|---|---|
| Entry | the side's `AGENTS.md` routing table → this side's `commander/SKILL.md` | Cursor User Rules → `~/.cursor/skills/commander/SKILL.md` (`commander-first.mdc` has `alwaysApply: false`) |
| Invocation | Pi auto-loads by description or `/skill:<name>`; DSH uses the `skill` tool | the user's `@<name>`; a skill may carry `disable-model-invocation: true` |
| Preference capture | rules go straight into AGENTS.md or SKILL.md | each skill's `learned.md`, plus `commander-tune/tune-log.md` |
| Reply budget | AGENTS.md "visible reply" ≤ {{STYLE_MAX_LINES}} lines | controlled by each skill's contract |

Tool names and invocation syntax differ only in `~/.agents/skill-src/TOOL-MAP.md` and never move into a body.

## Steps

1. Read local: `{{SKILLS_ROOT}}commander/SKILL.md` and `sync-log.md`; when the user names a skill, read only that one, otherwise read only each `SKILL.md`'s frontmatter, output contract (visible reply / when not to use) and recent `learned.md` entries — never the whole file.
2. Read the other side: `~/.pi/agent/AGENTS.md` (or `~/.dsh/AGENTS.md`, whichever is being changed), then take the 5 most recently modified opposing `SKILL.md` files by mtime (`ls -t`). Never read all of them.
3. Find differences and take only three kinds: sharper criteria, a shorter contract that loses no constraint, and "when not to use". Wording and invocation syntax are not differences.
4. One line per item: opposing `file:line` → local spot → how to write it here → expected effect. At most 5 items, ordered by impact.
5. Apply: back up the side being changed first (`tar czf <side-root>/commander-backup-<ts>.tgz -C <side-root> AGENTS.md skills`, where the side root is `~/.pi/agent` or `~/.dsh`); then edit `commander/SKILL.md`'s table and hard rules, plus the affected skill. When the routing table changes, change descriptions in the same turn; carry criteria only, never overwrite a whole file. Write `learned.md` only when the item is confirmed to be a user preference rather than a general contract, and tag it `source: other side, <date>`.
6. Record: append one line to `sync-log.md` — `date | direction | item | opposing source:line`.
7. Reply in ≤{{STYLE_MAX_LINES}} lines: which files changed, which items were carried over; no diff.

## Dedup

- Before carrying anything, check both sides' `sync-log.md`: the same source item is not re-carried within 14 days; re-evaluate only when the opposing file's mtime is later than the last record.
- One direction per turn; never carry both ways at once.
- A skill that exists on the other side but not here: ask before creating it, never create by default.

## Forbidden

- Do not copy one side's syntax into the other (`@`, `.mdc`, `learned.md`, `/skill:` are adapted per the table above), or the reverse.
- When opposing content conflicts with this repo's AGENTS.md, the repo wins; say so in the reply.
- Do not touch a project repo from this skill.
