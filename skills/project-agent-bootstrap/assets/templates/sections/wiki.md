
## Using & Updating the Wiki (`{{WIKI_DIR}}/`)

Read `{{WIKI_DIR}}/index.md` first. Search with `qmd search "<keywords>" -c {{WIKI_DIR}}` or `qmd query "<question>" -c {{WIKI_DIR}}`, read matching pages, and cite `[[wikilinks]]`.

**Maintaining the wiki: a dev task is not finished until the wiki is updated.**
1. Identify the concepts, flows, or decisions changed in your diff.
2. Update or create matching pages in `{{WIKI_DIR}}/wiki/` (never modify `raw/`).
3. Manage backlog & review items in `{{WIKI_DIR}}/wiki/next/` and `{{WIKI_DIR}}/wiki/keep/`.
4. Refresh `{{WIKI_DIR}}/index.md`, append to `{{WIKI_DIR}}/log.md`, and run `qmd update`.
