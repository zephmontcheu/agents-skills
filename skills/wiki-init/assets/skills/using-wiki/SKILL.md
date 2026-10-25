---
name: using-wiki
description: Use when answering questions about project context, architecture, history, when asked to search the wiki, when the user explicitly mentions 'wiki', 'knowledge base', or 'qmd', or whenever starting a new task to check for existing documentation.
---

# Using the Wiki

## Overview

This skill defines the mandatory workflow for interacting with the `qmd`-based wiki (the "brain" or knowledge base). It enforces the use of semantic search over file-system grep, proper citation syntax, and continuous synthesis of new knowledge.

## When to Use

- Answering questions about the project, its context, or its architecture.
- The user asks you to search the wiki, knowledge base, or brain.
- You are starting a new task and need to check for existing documentation before coding.
- The user explicitly mentions `wiki`, `qmd`, or `brain`.

## Core Pattern: Locating and Querying

To use the wiki effectively, you first need to find it, then combine the high-level index with semantic search.

1. **Locate the Vault:** If the wiki is not in the current folder, read the root `AGENTS.md` (or `CLAUDE.md` / `GEMINI.md`) of the current project. It will point to the vault's location (e.g., `../project-brain/AGENTS.md`). You can also run `qmd collection list` to find the collection name (`qmd://slug/`) associated with this project.
2. **Start with the Index:** Read `<vault>/index.md` to get a high-level catalog of the available knowledge. This file maps out the concepts and structure of the wiki.
3. **Semantic Search:** Use `qmd query "<question>"` or the qmd MCP tools (`query`, `get`, `multi_get`) to search the semantic index. This is superior to keyword search as it understands intent.
4. **Drill Down:** Read the specific markdown files returned by the search and index.



**Do NOT:**
- Do not use `grep`, `find`, or `ripgrep` as your primary search method for the wiki. These are fragile and miss semantic connections.

## Core Pattern: Responding and Citing

When answering based on wiki content, you must cite your sources and offer to expand the knowledge base.

1. **Cite Sources:** Every non-obvious claim MUST trace to a source using the `[[wikilink]]` syntax.
   - ✅ `The backend uses Prisma [[prisma]] and Express [[01-backend-setup]].`
   - ❌ `The backend uses Prisma [prisma.md](wiki/tools/prisma.md).`

2. **File Syntheses:** If the user asks a complex question that requires synthesizing multiple sources, **always offer** to file the answer back as a `synthesis` page. This ensures exploration compounds instead of dying in chat history.
   - **Example phrasing:** "Would you like me to file this answer as a synthesis page in the wiki?"
   - If the user accepts: write it in `wiki/syntheses/`, link it to related concepts, update `index.md`, and append an entry to `log.md`.

## Rationalization Table

| Excuse | Reality |
|---|---|
| "I'll just grep the folder, it's faster." | `grep` misses semantic relationships. `qmd query` is the required tool for the brain. |
| "Markdown links work fine, wikilinks are unnecessary." | Wikilinks (`[[link]]`) are the standard format for this vault and are required for the graph to function properly. |
| "The answer was simple, no need to offer a synthesis." | If the answer required combining multiple sources or insights, it belongs in the wiki. Always offer. |

## Red Flags - STOP and Start Over

- Using `grep` on the wiki directory instead of `qmd`.
- Formatting citations as `[Link](file)` instead of `[[Link]]`.
- Answering a complex, multi-source question without offering to create a `synthesis` page.

**All of these mean: Stop, delete your response plan, and re-read this skill before answering.**
