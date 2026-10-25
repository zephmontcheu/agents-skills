# Repository Guidelines — {{PROJECT_NAME}}

## Project Structure & Module Organization

{{STRUCTURE_SUMMARY}}

## Architecture Overview

{{ARCHITECTURE_NOTES}}

## Build, Test, and Development Commands

{{COMMANDS_SUMMARY}}

## Coding Style & Naming Conventions

{{CODING_STYLE}}

## Testing Guidelines

Test behavior, failures, and data isolation; mock external services. Target >80% coverage on core business logic.
{{FRONTEND_TESTING_RULE}}

## Commit & Pull Request Guidelines

Use Conventional Commits, e.g., `feat(scope): add feature description`. Keep commits focused. PRs should describe changes, link issues, and list validation results.
{{DATABASE_SECURITY_TIPS}}

## Shared Agent Setup (`.agents/`)

Reusable skills live in `.agents/skills/<name>/SKILL.md` and subagents in `.agents/agents/`: open a skill when its description matches the task. Always-on rules live in `.agents/rules/`. Many agents (Codex, Cursor) don't load that folder on their own, so read these rules before starting work and follow them:

{{RULE_LIST}}
{{WIKI_SECTION}}
{{GRAPHIFY_SECTION}}
