---
trigger: always_on
description: Consult the project wiki for product, history, and "why" questions.
---

# Project Wiki (`{{WIKI_DIR}}/`)

`{{WIKI_DIR}}/` is an Obsidian vault documenting the product, its decisions, and the reasons behind them. Its schema (`AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` inside the vault) holds the folder roles and the ingest/query/lint workflows: read it before writing to the wiki.

**Using it** for product, history, and "why" questions (for "where/how is it coded", use the code or graphify):
1. `qmd search "<keywords>" -c {{WIKI_DIR}}` (instant) or `qmd query "<question>" -c {{WIKI_DIR}}` (slower, semantic); otherwise start from `{{WIKI_DIR}}/index.md`.
2. Read the matching `wiki/` pages and follow their `[[wikilinks]]`; go to `raw/` only when a page is thin.
3. Cite the pages you used with `[[wikilinks]]`. Acknowledge `> [!warning] Contradiction` blocks when relevant.
4. When starting a task, check `wiki/next/` (backlog) and `wiki/keep/` (known anomalies, items for human review) for related entries.

The wiki lags the code. Status claims like "not implemented yet" are often outdated, so check the code before repeating them.

`raw/` holds immutable source documents: never edit it. Ignore `inbox/` unless asked. Writing to `wiki/` follows `.agents/rules/updating-wiki-systematically.md`.
