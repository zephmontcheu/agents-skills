---
name: wiki-init
description: Creates an LLM-maintained wiki (Obsidian vault + qmd search) for a repository or a folder of documents, with a schema every agent reads, a task/anomaly backlog, and a first ingest of the existing docs. Use when the user wants to create a wiki for a repo, initialize a second brain, set up an Obsidian vault, build a project knowledge base, or document a project so AI agents keep it up to date, even if they don't say "wiki".
---

# wiki-init

## Overview
Initializes a wiki vault on a target directory. The result is an operational vault: schema, structure, qmd search, and initial content if the folder already contained docs. Requires [`qmd`](https://www.npmjs.com/package/@tobilu/qmd) (`npm install -g @tobilu/qmd`).

## When to Use
- The user asks to "create a wiki for this repo", "initialize a second brain", or "setup an Obsidian vault".
- The user wants to document a project and accumulate knowledge.
- The user wants to add a new project to an existing wiki system.
- The user wants to transform a folder of documents into a queryable knowledge base.

**When NOT to use:**
- If `$T/log.md` and `$T/wiki/` already exist, it is an existing vault. Do not re-initialize. Suggest using `/wiki-scan` instead.

## Quick Reference
| Step | Action |
|---|---|
| 1. Diagnostic | Check if the target is a git repo and list existing docs. |
| 2. Placement | Propose creating it "In the repo" or as a "Separate vault". |
| 3. Interview | Ask 4 questions: Domain, Language, Ingest style, Structure. |
| 4. Scaffold | Render `assets/schema-template.md` to `AGENTS.md` (plus `@AGENTS.md` pointers in `CLAUDE.md`/`GEMINI.md`), create folders. |
| 5. Agent Setup | Copy `using-wiki` and `updating-wiki-systematically` skills to `.agents/skills/`, link them for Claude Code. |
| 6. Registration | Add the collection via `qmd` (and, if the `wiki-scan` hook is used, its registry). |
| 7. Ingest | (If docs exist) Read docs/codebase, propose a touch-list (including a central architecture Mermaid diagram), wait for validation. |
| 8. Log | Add the initial entry to `log.md`. |

## Implementation

### 1. Target and Diagnostic
Directory passed as an argument, otherwise the current directory. Before asking anything, look at:

```bash
T=<target>
[ -d "$T/.git" ] && echo "git repo" || echo "not a repo"
find "$T" -name '*.md' -not -path '*/node_modules/*' -not -path '*/.git/*' \
     -not -path '*/site-packages/*' -not -path '*/venv/*' | wc -l
ls -d "$T"/*/ 2>/dev/null | head
```

The diagnostic serves to recommend, not to decide alone: a single git repo with docs leans towards "in the repo"; a folder containing multiple repos leans towards a separate vault.

### 2. Placement
Ask, providing your recommendation from the diagnostic:

- **In the repo** — the wiki lives with the code, versioned alongside it. Good for a single project owned by the user. The vault and the source are the same folder.
- **Separate vault** — `<name>-brain/` next to the target, which remains untouched. Good for documenting a folder that must remain clean, or that contains multiple projects.

### 3. Short Interview
Four questions, all at once. They determine the generated schema:

1. **Domain** — what is this brain about? This determines the page types. For dev: `project`, `concept`, `decision`, `tool`, `source`, `synthesis`, `task`, `anomaly`. For research: `concept`, `method`, `author`, `claim`, `source`, `synthesis`. For personal: `area`, `pattern`, `person`, `insight`, `source`, `synthesis`. Suggest an adapted set rather than forcing the dev one.
2. **Language** — language of the wiki, and possibly a second language for source summaries (`fr/` folder or equivalent). A full mirror doubles the maintenance: discourage it unless explicitly requested.
3. **Ingest style** — interactive (you stop for approval before writing) or autonomous. Interactive is the default: it prevents the synthesis from drifting.
4. **Structure** — minimal and growing organically (subfolders when a type reaches 3 pages), or full scaffold immediately.

### 4. Scaffold
From `assets/schema-template.md`, substituting the `{{...}}` markers. Create:

```
<vault>/
  AGENTS.md    ← the generated schema
  CLAUDE.md    ← one line: @AGENTS.md (Claude Code)
  GEMINI.md    ← one line: @AGENTS.md (Gemini CLI, Antigravity)
  index.md     ← empty catalog, one section per page type
  log.md       ← with the init entry
  raw/  wiki/  inbox/
  wiki/next/   ← tasks and ideas backlog
  wiki/keep/   ← anomalies and human reviews
  architecture/
    1-system-context/
    2-data-flow/
    3-security-boundaries/
  fr/          ← only if a second language was requested
```

Copy `.obsidian/` from another vault of the user's if there is one — this keeps display preferences instead of starting from default settings. Otherwise, let Obsidian create it on the first open.

If the vault is separate, the target's root docs must point to it (see step 5): without this, the schema won't load when the session starts outside the vault.

### 5. Agent Setup
Copy the bundled skills into the target's shared skills folder, `.agents/skills/` (read by Codex, Cursor, Gemini CLI, Antigravity, Copilot). Skip a skill that is already there, for example one installed by `project-agent-bootstrap`:

```bash
for s in using-wiki updating-wiki-systematically; do
  [ -e <target>/.agents/skills/$s ] || { mkdir -p <target>/.agents/skills/$s && cp assets/skills/$s/SKILL.md <target>/.agents/skills/$s/; }
  # Claude Code only reads .claude/skills/: expose the same folder there.
  [ -e <target>/.claude/skills/$s ] || { mkdir -p <target>/.claude/skills && ln -s ../../.agents/skills/$s <target>/.claude/skills/$s; }
done
```

On Windows without symlink rights, copy the folder into `.claude/skills/` instead of linking it.

Then make sure every agent learns the wiki exists. If the target's root `AGENTS.md` and `CLAUDE.md` don't mention the vault yet, append this directive to each (create `AGENTS.md` if neither file exists; Cursor and Codex read it too):

> **CRITICAL:** This project uses an LLM-maintained knowledge base in `<vault>/`. Before answering questions, making architectural decisions, or writing code, read `<vault>/AGENTS.md` to understand the wiki schema, and consult the existing documentation.

### 6. Registration

**qmd** — the collection slug must be unique, check `qmd collection list`:

```bash
qmd collection add <vault> --name <slug>
qmd update
qmd embed -c <slug>
```

Use the vault folder name as the slug when it's free: the rules written by `project-agent-bootstrap` query `qmd ... -c <vault-folder>`.

**Scan registry (optional)** — only if the user runs the `wiki-scan` skill with its `SessionStart` hook. Add a TSV line to the registry that hook reads (`~/.gemini/wiki-vaults` or `~/.claude/wiki-vaults`), verifying there are no duplicates:

```bash
printf '%s\t%s\n' "<vault>" "<source_root>" >> <registry-file>
```

When vault and source are the same folder, both columns are identical — the hook excludes itself.

### 7. First Ingest
**This is where the value lies for an already populated folder.** An empty vault is useless; a vault that already reflects what the repo contains is immediately queryable.

If the diagnostic found docs:

1. Read them — thoroughly, not just skimming. Analyze `README`s, specs, codebase structure, and existing architecture docs.
2. Present the takeaways and a **touch-list**: every page you would create, and what it would contain. **Crucially**, include a plan for the `architecture/` directory. This should include:
   - Three macro architecture files: `1-system-context/_system-context-complete.md`, `2-data-flow/_data-flow-complete.md`, and `3-security-boundaries/_security-complete.md`.
   - 2 to 3 core features identified from the codebase, with a specific `.md` file for each feature in all three subfolders (e.g., `user-authentication.md`).
3. **Stop.** Wait for approval. Even in autonomous ingest mode, the first ingest deserves a look: it sets the shape of the wiki, and a bad initial structure takes a long time to fix.
4. After approval, write in a single pass: source pages, project/concept pages, the architecture macro and feature files, `index.md` (ensuring open items from `wiki/next/` and `wiki/keep/` are listed), summaries in the second language if applicable, `log.md` entry.
   - **Architecture Content:** Each generated file in the `architecture/` directory must contain a Mermaid diagram AND 1-2 paragraphs of explanatory text (e.g., context, components, flow).
   - **Important Tagging:** Ensure every Mermaid diagram generated inside the `architecture/` files is wrapped in HTML comments: `<!-- wiki-diagram: start -->` and `<!-- wiki-diagram: end -->`. The explanatory text MUST be placed **outside** these tags so it can be edited manually by the team without being overwritten by future automated scans.
5. `qmd update`.

If the folder is empty or has no docs, simply state so and explain how to drop a first source. Do not fabricate content to fill it.

### 8. Log Entry and Verification

```markdown
## [YYYY-MM-DD] init | Vault created

Target: <path>. Placement: <in the repo|separate>. Domain: <domain>.
qmd collection: <slug>. Page types: <list>.
```

Do not declare completion without verifying:

- `qmd status` lists the collection with a non-zero document and vector count;
- if a scan registry is used: it contains the new line, without duplicates, and the scan hook (e.g. `bash ~/.gemini/hooks/wiki-scan-check.sh --since=<old date> --vault=<vault>`) produces valid JSON and sees the source;
- all created `[[links]]` resolve to an existing file.

A vault that looks correct but isn't indexed by qmd is a dead vault.

## Common Mistakes
- **Overwriting an existing vault**: A folder that already has a `log.md` and a `wiki/` folder is already a vault. Reinitializing it would overwrite all work. Solution: Always run the diagnostic, and use `/wiki-scan` instead.
- **Creating filler content**: Trying to initialize a wiki on an empty repo by generating fake articles. Solution: Explain to the user how to add real sources.
- **Forgetting the qmd update**: The vault is created but the wiki is not queryable because indexing wasn't done. Solution: Always run `qmd update` after a modification.

## Rationalization Table

| Excuse | Reality |
|---|---|
| "The wiki folder looks corrupted or incomplete, I'll recreate it from scratch." | Overwriting destroys past work. Use `/wiki-scan` or ask for explicit permission. |
| "The project is empty, I'll generate some default concepts to show how it works." | Never fabricate fake content. An empty wiki must remain empty until external sources are added. |
| "The repo is very standard, I'll decide the interview parameters myself to save time." | The user must choose the ingest style and domain. Always ask the 4 questions. |
| "I validated the touch-list myself because it seems obvious." | The first ingest sets the long-term shape of the wiki. The user's approval is **mandatory**. |

## Red Flags - STOP and Start Over

- Asking to overwrite or rewrite an existing `log.md`.
- Starting the ingest or creating files without having the user validate the touch-list.
- Adding unsourced information or pages in a blank folder.

**All these situations mean: Stop the action, re-read the diagnostic, and ask for the user's explicit approval.**
