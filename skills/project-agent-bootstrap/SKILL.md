---
name: project-agent-bootstrap
description: >-
  Bootstraps, audits, and syncs a repository's AI-agent foundation for any stack
  (JS/TS, Python, Go, Rust, Java, monorepos): `AGENTS.md`, `CLAUDE.md`, and a
  shared `.agents/` folder (rules, skills, subagents, workflows) that Claude
  Code, Codex, Cursor, Gemini CLI, Antigravity and Copilot all pick up. Detects
  the stack and turns on matching modules: real-browser UI/UX testing for
  frontends, database-safety rules when an ORM or database client is found, an
  LLM-maintained wiki (`qmd`, via `wiki-init`), and a `graphify` code graph.
  Use it whenever the user wants to set up, onboard, or standardize a project
  for AI coding agents, write or refresh AGENTS.md/CLAUDE.md, add agent rules or
  skills to a repo, merge a legacy `.agent/` folder into `.agents/`, or audit why
  agents ignore a project's conventions, even if they don't name this skill.
---

# Project Agent Bootstrap

Deploys a shared, non-destructive agent foundation into any repository, then hands you the parts a script can't do well: describing what the code actually does and merging into documentation the team already wrote.

## What gets installed

| Module | Turned on (`auto`) when | Files |
|---|---|---|
| core | always | `AGENTS.md`, `CLAUDE.md`, `.agents/bootstrap.json` |
| frontend | a frontend dependency is found (React, Vue, Svelte, Angular, Next, Nuxt, Astro, Vite, Solid…) | `.agents/rules/ui-ux-testing.md`, `.agents/skills/{ui-ux-testing,ux-optimizer}/`, `.agents/agents/ux-optimizer/` |
| database | an ORM or DB client (Prisma, Drizzle, TypeORM, SQLAlchemy, Django, GORM, sqlx…) or a `prisma/`/`supabase/` folder is found | `.agents/rules/database.md`, tailored to the detected tools |
| wiki | a wiki vault already exists, or `qmd` is installed | `.agents/rules/{use-wiki,updating-wiki-systematically}.md`, `.agents/skills/updating-wiki-systematically/` |
| graphify | `graphify-out/graph.json` exists, or `graphify` is installed | `.agents/rules/graphify.md`, `.agents/workflows/graphify.md` |

`AGENTS.md` is the single source of shared guidelines and lists every always-on rule by name, because Codex and Cursor read `AGENTS.md` but not `.agents/rules/`. `.agents/skills/` is the project skills folder for Codex, Cursor, Gemini CLI, Antigravity, Copilot, and OpenCode. Claude Code reads only `CLAUDE.md` and `.claude/skills/`. So the generated `CLAUDE.md` imports `@AGENTS.md` and each `@.agents/rules/<rule>.md`, and every skill in `.agents/skills/` is symlinked into `.claude/skills/` (copied where symlinks aren't allowed).

Nothing that already exists is overwritten. Existing files are skipped, and existing `AGENTS.md`/`CLAUDE.md` get a merge proposal instead. The chosen modules, project name, and wiki folder are saved in `.agents/bootstrap.json`; `verify` and later `scaffold` runs reuse them unless a flag overrides them.

## The CLI

`<skill-dir>` below means the directory containing this SKILL.md. The script needs Python 3.9+ and the standard library only (Linux, macOS, Windows; use `python` instead of `python3` where that's the name). It prints a JSON report to stdout, or writes it to `--output <file>`.

```bash
python3 <skill-dir>/scripts/bootstrap_cli.py inspect  --target .
python3 <skill-dir>/scripts/bootstrap_cli.py scaffold --target . --dry-run
python3 <skill-dir>/scripts/bootstrap_cli.py scaffold --target .
python3 <skill-dir>/scripts/bootstrap_cli.py verify   --target .
```

`scaffold` options (all optional):

| Option | Default | Meaning |
|---|---|---|
| `--project-name` | name in the root manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`), else the folder name | Name used in the docs |
| `--wiki-dir` | existing vault, else `<project>-wiki` | Wiki vault folder |
| `--frontend/--database/--wiki/--graphify` | `auto` | `true`/`false` force a module on or off |
| `--dry-run` | off | Report what would change, write nothing |
| `--consolidate-dot-agent` | off | Move items from a legacy `.agent/` into `.agents/`. `.agent/` is deleted only if every item was moved or is identical; conflicts are reported and `.agent/` is kept |

## Workflow

### 1. Inspect

Run `inspect` and summarize for the user, briefly:
- the stack per project folder (`stack.projects`: languages, frameworks, DB tools, detected commands);
- which modules would turn on and why (`modules`), plus any missing tool (`qmd`, `graphify`);
- what already exists, what's missing, and whether a legacy `.agent/` folder is there;
- the wiki and graph status.

### 2. Confirm scope when there's something to decide

Ask before writing when:
- the project already has `AGENTS.md`/`CLAUDE.md`, or a legacy `.agent/` (should it be consolidated?);
- a module may be unwanted. For example, the database rule assumes production data, which may be overkill for a local SQLite toy;
- the wiki module is on but no vault exists yet: ask whether they want one now. Yes means running `wiki-init`, which interviews them, in step 4; no means `--wiki false`, otherwise the rules would point agents at a vault that doesn't exist;
- the graphify module is on but no graph exists: building one takes a while and spends tokens, so confirm, or pass `--graphify false`.

If the user already said what to skip ("no wiki today"), that's the answer: pass the flag without asking. Confirm the project name and wiki folder only if the suggestions look wrong. For a fresh repo with clear detection, a `--dry-run` summary followed by the real run is enough.

### 3. Scaffold, then finish what the script can't

Run `scaffold` with the agreed flags, read the report, then:

1. **Fill in the TODOs** in files the run *created*, mostly `AGENTS.md` (`CLAUDE.md` just imports it). The script only sees manifest files; you can read the code. Replace each `TODO` with real facts: one line per folder saying what it holds, and a short architecture overview (main components, how they talk, entry points). Take the facts from the README, manifests, and a quick look at the source. Keep commands the script detected, and add one only if you saw it in a manifest, Makefile, CI file, or README. An invented command that fails is worse than a missing one.
2. **Merge into existing root docs** if `actions.pending_root_merges` is non-empty. Those files belong to the team: add only the missing sections listed (taken from `.agents/pending-root-updates.md`), keep everything else as is, then delete `.agents/pending-root-updates.md`.
3. **Resolve legacy conflicts** if `actions.legacy_conflicts` is non-empty. Show the user how each `.agent/` item differs from its `.agents/` counterpart and let them choose; `.agent/` was kept on purpose until they decide.

### 4. Wiki and knowledge graph (only for modules that are on)

- **wiki**: if no vault exists, follow the `wiki-init` skill (it ships in the same repository as this skill), naming the vault after `wiki_dir`; it interviews the user, so don't skip that. If a vault exists, run `qmd update`.
- **graphify**: if `graphify-out/graph.json` is missing, follow the `graphify` skill to build it; otherwise run `graphify update .`.
- If a tool is missing, tell the user how to install it rather than pretending the step ran:
  - `qmd`: `npm install -g @tobilu/qmd`
  - `wiki-init`: `npx skills add zephmontcheu/agents-skills --skill wiki-init`
  - `graphify`: `uv tool install graphifyy` (or `pipx install graphifyy`), then `graphify install`
- **frontend**: `ux-optimizer` gets better design suggestions from the separate `ui-ux-pro-max` skill. Offer `npx skills add nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max` if it isn't installed.

### 5. Verify and report

Run `verify` and report `overall_status` (`PASS`/`WARN`/`FAIL`), with each remaining warning or failure and the step that fixes it.

## Common mistakes

1. **Both `.agent/` and `.agents/`**: always deploy into `.agents/` (plural, the cross-agent convention). Two folders make agents load duplicate or conflicting versions of the same skill.
2. **Overwriting team docs**: existing `AGENTS.md`/`CLAUDE.md` often hold architecture notes that took months to write. Merge sections in; never regenerate the file.
3. **Leaving TODOs or inventing facts**: an agent reading `AGENTS.md` trusts it. Vague placeholders waste that trust, and wrong commands break it.
4. **Forcing modules the project doesn't use**: a wiki rule without `qmd` installed, or a production-database warning on a repo without a database, teaches agents to ignore the rules.
