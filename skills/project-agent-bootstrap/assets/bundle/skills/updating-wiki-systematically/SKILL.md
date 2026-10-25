---
name: updating-wiki-systematically
description: Use when completing a development task, implementing a feature, or executing an implementation plan, before claiming the work is finished or asking the user for review.
---

# updating-wiki-systematically

## Overview
Paths below (`wiki/`, `raw/`, `index.md`, `log.md`) are relative to the project's wiki vault, the `*-wiki/` folder named in `AGENTS.md` and `.agents/rules/use-wiki.md`.

**The task is not finished until the wiki is updated.** This skill enforces the systematic update of the project's knowledge base at the end of every development cycle, ensuring that documentation never falls behind the code.

## When to Use
- You are about to tell the user "I am done" or "The feature is implemented".
- You have completed an implementation plan or a task checklist.
- You have made architectural, conceptual, or significant technical changes to the codebase.

## Quick Reference
| Step | Action |
|---|---|
| 1. Analyze | Identify what concepts, architectures, or features were modified. |
| 2. Edit `wiki/` | Update existing pages in `wiki/` or create new ones for new concepts. |
| 3. Manage `next`/`keep` | Remove completed tasks from `wiki/next/`. Add new tasks/ideas to `wiki/next/`. Log anomalies or human-review items to `wiki/keep/`. |
| 4. Raw Sources | **NEVER modify files in `raw/`.** Raw sources are immutable. |
| 5. Update index | If new pages were created, link them in `index.md`. |
| 6. Trace | Append an entry to `log.md` detailing the update. |
| 7. Index | Run `qmd update` to ensure the wiki remains queryable. |

## Implementation

When you reach the end of a coding task, follow this exact recipe:

1. **Review the diff:** Look at the changes you just made to the codebase. What new concepts were introduced? What existing architecture was modified?
2. **Update the Wiki files:** 
   - Edit the relevant markdown files in the `wiki/` directory.
   - Create new pages if a new major concept or system was added.
   - **CRITICAL RULE:** Do NOT modify any files inside the `raw/` directory. These are immutable source documents. You only write in the `wiki/` directory.
3. **Manage Task Backlog and Anomalies:**
   - If you completed a task tracked in `wiki/next/`, delete its file or mark it done.
   - If you discovered new necessary tasks, follow-up ideas, or technical debt, create a markdown file in `wiki/next/`.
   - If you encountered anomalies or decisions requiring human review, create a markdown file in `wiki/keep/` (which acts as a "keep in mind" / review list).
4. **Update the Index:** If you created new pages (including in `next/` or `keep/`), you must add a link to them in `index.md` so they are not orphaned.
5. **Log the Update:** Append a new entry to `log.md`. Format:
   `## [YYYY-MM-DD] ingest | Wiki updated for <Feature Name>`
6. **Re-index the Vault:** You must run the command `qmd update` in the terminal to index the changes.

## Common Mistakes
- Modifying files in `raw/` instead of `wiki/`.
- Forgetting to run `qmd update` after making the changes.
- Creating orphaned pages without adding them to `index.md`.

## Rationalization Table

| Excuse | Reality |
|---|---|
| "The modification is too minor to warrant a wiki update." | Every change that alters behavior or structure must be documented. If there is truly nothing to document, you must explicitly state *why* to the user. |
| "The code is clean and self-documenting." | Code explains *how*. The wiki explains *why* and the global context. Code does not replace the wiki. |
| "I'll inform the user of the changes and update the wiki later." | The future does not exist. The task is not finished until `qmd update` has been run. |
| "I'll just update the raw specs to reflect the new code." | `raw/` files are immutable. You must only update the synthesis in the `wiki/` folder. |

## Red Flags - STOP and Start Over

- Claiming "The task is completed" without having modified the `wiki/` folder.
- Proposing to "leave the documentation to the user".
- Attempting to edit or overwrite any file inside the `raw/` folder.

**If you catch yourself doing any of the above: Delete your response, stop, and execute the wiki update process immediately.**
