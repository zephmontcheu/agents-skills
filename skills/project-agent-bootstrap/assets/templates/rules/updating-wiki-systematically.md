---
trigger: always_on
description: A dev task is not finished until the project wiki is updated.
---

# Wiki Updates Are Part of "Done"

Before saying a feature, fix, or plan is done, update `{{WIKI_DIR}}/` directly, without asking for approval. The full procedure is the `updating-wiki-systematically` skill (`.agents/skills/updating-wiki-systematically/SKILL.md`):

1. From your diff, identify the concepts, flows, decisions, or tools that changed.
2. Update the matching pages in `wiki/`, or create one for a new concept. If a page describes code that changed, rewrite it and cite the code path.
3. Backlog: delete the `wiki/next/` item you just completed. Add new follow-ups or tech debt to `wiki/next/`, and anomalies or decisions needing human review to `wiki/keep/`.
4. Link new pages, including `next/` and `keep/` items, from `index.md`.
5. Append `## [YYYY-MM-DD] ingest | Wiki updated for <feature>` to `log.md`.
6. Run `qmd update`.

If there is truly nothing to document (pure refactor, a test, a dependency bump), say why in one line instead.
