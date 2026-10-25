# agents-skills

Skills that give any repository a shared foundation for AI coding agents: Claude Code, Codex, Cursor, Gemini CLI, Antigravity, Copilot, OpenCode, and others that read `AGENTS.md` and `.agents/`.

| Skill | What it does |
|---|---|
| [`project-agent-bootstrap`](skills/project-agent-bootstrap/SKILL.md) | Detects the stack (JS/TS, Python, Go, Rust, Java, C/C++, monorepos) and deploys `AGENTS.md`, `CLAUDE.md`, and `.agents/` rules, skills, and subagents: UI/UX browser testing for frontends, database-safety rules tailored to the ORM in use, wiki and knowledge-graph rules. Merges a legacy `.agent/` folder without losing anything. |
| [`wiki-init`](skills/wiki-init/SKILL.md) | Creates an LLM-maintained project wiki (Obsidian vault + [qmd](https://www.npmjs.com/package/@tobilu/qmd) search) with a schema every agent reads, a task/anomaly backlog, and a first ingest of the existing docs. |

## Install

With the [`skills`](https://github.com/vercel-labs/skills) CLI, which installs into the right folder for each agent:

```bash
npx skills add zephmontcheu/agents-skills                                # pick skills and agents interactively
npx skills add zephmontcheu/agents-skills --skill project-agent-bootstrap -g -a claude-code   # one skill, globally, for Claude Code
```

Or by hand: copy `skills/<name>/` into your agent's skills folder, for example `~/.claude/skills/` (Claude Code, global) or `<project>/.agents/skills/` (Codex, Cursor, Gemini CLI, Antigravity).

## Use

Ask your agent in plain words, for example:

- "Set up this repo for AI coding agents."
- "We have both a `.agent` and a `.agents` folder, clean it up without losing anything."
- "Create a wiki for this project."

`project-agent-bootstrap` inspects the repo, shows what it would install, scaffolds without overwriting existing files, fills in the project-specific parts of `AGENTS.md`/`CLAUDE.md` from the code, and verifies the result. Its CLI can also be run directly:

```bash
python3 skills/project-agent-bootstrap/scripts/bootstrap_cli.py inspect  --target path/to/repo
python3 skills/project-agent-bootstrap/scripts/bootstrap_cli.py scaffold --target path/to/repo --dry-run
```

## Requirements

- Python 3.9+ (standard library only) for the bootstrap CLI.
- Optional: [`qmd`](https://www.npmjs.com/package/@tobilu/qmd) for the wiki (`npm install -g @tobilu/qmd`), [`graphify`](https://pypi.org/project/graphifyy/) for the code graph (`uv tool install graphifyy`), and [`ui-ux-pro-max`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) for design suggestions in frontend projects. Modules whose tool is missing stay off unless forced.

## Development

```bash
python3 tests/test_bootstrap_cli.py   # CLI self-check
```

Behavioural test cases for the skill live in `skills/project-agent-bootstrap/evals/` (the `claude plugin eval` layout).

## License

MIT
# agents-skills
# agents-skills
