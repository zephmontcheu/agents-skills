# {{VAULT_NAME}} — wiki schema

You are the maintainer of this wiki. Read this file before any operation in this vault.

## Roles

- `raw/` — immutable sources. Read them, never edit or delete them.
- `wiki/` — yours. You create, update, cross-reference, and keep consistent. The human reads; you write.
{{FR_ROLE_LINE}}- `inbox/` — staging only. Scan proposals waiting for the human's decision. Never a source, never cited by a wiki page, never treated as knowledge.
- `index.md` / `log.md` — yours, maintained on every operation.
- The human curates sources, directs analysis, and asks questions. They do not write wiki pages.

Domain: {{DOMAIN}}

Source root: `{{SOURCE_ROOT}}`

## Page types

`type:` frontmatter is one of:

{{PAGE_TYPES_TABLE}}

## File conventions

- Flat in `wiki/` by default. When one `type` reaches **{{PROMOTION_THRESHOLD}} pages**, move that type into `wiki/<type>s/`. Wikilinks resolve by filename, so promotion needs no link edits.
- Filenames: kebab-case, {{FILENAME_LANG}}. Source pages only: `YYYY-MM-DD-slug.md`.
- Frontmatter on every page, minimal:
  ```yaml
  ---
  type: {{EXAMPLE_TYPE}}
  updated: {{TODAY}}
  sources: []
  ---
  ```
- Language: {{LANGUAGE_RULE}}

## Linking

- Every page links to at least one other page. No orphans.
- Every non-obvious claim traces to a `[[source-page]]`.
- New information contradicting an existing claim is **never** silently overwritten. Add:
  ```
  > [!warning] Contradiction
  > [[source-a]] says X; [[source-b]] (date) says Y. Unresolved.
  ```
  Resolve it only when a source settles it, then note which one did.
- Mention a concept {{PROMOTION_THRESHOLD}}+ times across pages without a page of its own → propose creating it.

## Workflow: ingest

{{INGEST_MODE_LINE}}

1. Source lands in `raw/` — the human drops it, or you copy it there from the source tree (copy, never move).
2. Read it in full.
3. Report: key takeaways, plus a **touch-list** naming every page you'd create or update and what changes in each.
{{INGEST_APPROVAL_STEP}}
5. One pass:
   - `wiki/YYYY-MM-DD-<slug>.md` — the source summary (`type: source`)
   - create/update every page on the touch-list
   - rewrite `index.md`
{{FR_INGEST_STEP}}   - append to `log.md`
6. `qmd update`
7. Report the diff: created, changed, contradictions raised.

## Workflow: query

1. `qmd query "<question>"` — or the qmd MCP tools (`query`, `get`, `multi_get`).
2. Read `index.md`, then drill into the pages it points at. Wiki pages first, `raw/` only when the wiki is thin on the topic.
3. Answer with `[[wikilink]]` citations.
4. **Always offer** to file the answer back as a `synthesis` page. This is how exploration compounds instead of dying in chat history. If the human accepts: write it, link it, update `index.md`, append to `log.md`.

## Workflow: scan

On request, or automatically when the `wiki-scan` skill and its `SessionStart` hook are installed: the hook diffs the source tree since the last `scan` or `ingest` entry in `log.md`, at most once per calendar day, and injects what changed. Without them, run a scan by hand: diff the source tree since that entry (`git log --since`) and follow the steps below.

The scan **proposes, it never ingests.** It writes one file — `inbox/YYYY-MM-DD-scan.md` — listing what changed, which wiki pages are now wrong, and a suggested touch-list. `wiki/`{{FR_SCAN_MENTION}} is never touched by a scan.

Turning a proposal into wiki pages is an **ingest**, and follows the ingest workflow above. Once ingested, the proposal is deleted or moved to `inbox/done/`.

Rationale: the tedious half of maintenance (noticing that something changed and working out what it invalidates) is automated; the judgement half stays human.

## Workflow: lint

On request. Report only — no edits without approval. Check:

- contradictions between pages
- claims a newer source has superseded
- orphan pages (no inbound links)
- concepts mentioned {{PROMOTION_THRESHOLD}}+ times with no page
- broken wikilinks
- gaps a web search or a missing source could fill

End with suggested next questions and sources worth finding.

## index.md and log.md

- `index.md` — catalog grouped by page type, one line each: `- [[page]] — one-line summary`. Rewritten on every ingest.
- `log.md` — append-only. Every entry starts `## [YYYY-MM-DD] <ingest|query|scan|lint> | <title>` so `grep "^## \[" log.md | tail -5` works. Never rewrite past entries.

{{FR_RULE_SECTION}}
## Search

qmd indexes this vault as collection `{{COLLECTION}}`. After any write pass: `qmd update`. After a large batch: `qmd embed -c {{COLLECTION}}`.

## Agent Rules

You must check the wiki (`qmd query`) before starting any architectural task.
You must follow the rules in `.agents/skills/using-wiki` and `.agents/skills/updating-wiki-systematically`.

Whenever you identify tasks, ideas, or steps to be done later during brainstorming or development (even if not immediately next), you MUST create a new markdown file in `wiki/next/` named `YYYY-MM-DD-<slug>.md`. Include YAML frontmatter `type: task`, `status: open`, `updated: YYYY-MM-DD`. Document the details and `[[wikilink]]` to relevant context. When the task is completed, you must update the file to `status: completed` and append a "Resolution" section linking to the relevant PR, commit, or updated documentation.

Whenever you encounter a discrepancy, something that contradicts previous decisions, something suspicious/abnormal, or anything that requires human review, you MUST create a new markdown file in `wiki/keep/` named `YYYY-MM-DD-<slug>.md`. Include YAML frontmatter `type: anomaly`, `status: open`, `updated: YYYY-MM-DD`. Document the issue in detail and `[[wikilink]]` to relevant context. Once a human or agent makes a decision, document the decision in the wiki (e.g. updating a `concept` or creating a `decision` page), update the anomaly file to `status: resolved`, and append a "Resolution" section linking to the new decision or updated pages.

