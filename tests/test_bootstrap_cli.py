"""Self-check for project-agent-bootstrap's CLI. Run: python3 tests/test_bootstrap_cli.py"""

import importlib.util
import json
from pathlib import Path
import tempfile

CLI = Path(__file__).resolve().parent.parent / 'skills/project-agent-bootstrap/scripts/bootstrap_cli.py'
spec = importlib.util.spec_from_file_location('bootstrap_cli', CLI)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
cli.shutil.which = lambda _: None  # deterministic: pretend qmd/graphify are absent

AUTO = {'frontend': 'auto', 'database': 'auto', 'wiki': 'auto', 'graphify': 'auto'}


def write(root: Path, files: dict) -> None:
  for rel, content in files.items():
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content if isinstance(content, str) else json.dumps(content))


def scaffold(root, **kw):
  flags = {**AUTO, **kw.pop('flags', {})}
  return cli.scaffold_target(str(root), kw.get('name'), None, flags,
                             kw.get('dry_run', False), kw.get('consolidate', False))


def test_python_repo(root: Path) -> None:
  write(root, {
      'pyproject.toml': '[project]\nname = "api"\ndescription = "upgrade tool"\n'
                        'dependencies = ["fastapi", "sqlalchemy>=2", "alembic"]\n'
                        '[dependency-groups]\ndev = ["pytest", "ruff"]\n',
      'uv.lock': '', 'src/api/main.py': '', 'tests/test_x.py': '',
  })
  report = scaffold(root)
  assert report['modules'] == {'frontend': False, 'database': True, 'wiki': False,
                               'graphify': False}, report['modules']
  agents = (root / 'AGENTS.md').read_text()
  claude = (root / 'CLAUDE.md').read_text()
  db_rule = (root / '.agents/rules/database.md').read_text()
  assert '`uv run pytest`' in agents and '`uv sync`' in agents, agents
  assert 'TypeScript' not in agents and 'npm' not in agents, agents
  assert 'qmd' not in agents and 'graphify' not in agents, agents
  assert '`sqlalchemy`' in db_rule and 'alembic downgrade base' in db_rule, db_rule
  assert 'prisma migrate' not in db_rule and 'Row-Level' not in db_rule, db_rule
  assert db_rule.count('alembic downgrade base') == 1 and db_rule.count('DROP') == 1, db_rule
  assert 'Prisma' not in db_rule, db_rule
  assert '`pg`' not in db_rule  # "upgrade" must not match the `pg` driver
  assert '@AGENTS.md' in claude and '@.agents/rules/database.md' in claude, claude
  assert '- `.agents/rules/database.md`' in agents, agents
  assert 'skills' not in claude.split('@.agents/rules/database.md')[1], claude  # no skills deployed
  assert report['project_name'] == 'api', report['project_name']
  assert '.agents/bootstrap.json' in report['actions']['created_files']
  assert not (root / '.agents/rules/ui-ux-testing.md').exists()
  assert '{{' not in agents + claude + db_rule
  assert cli.verify_target(str(root))['overall_status'] == 'WARN'  # TODOs left to fill


def test_pnpm_monorepo(root: Path) -> None:
  write(root, {
      'package.json': {'name': 'mono', 'private': True},
      'pnpm-lock.yaml': '',
      'apps/web/package.json': {'dependencies': {'next': '15', 'react': '19'},
                                'scripts': {'dev': 'next dev', 'build': 'next build'}},
      'packages/db/package.json': {'dependencies': {'drizzle-orm': '1', 'pg': '8'}},
  })
  dry = scaffold(root, flags={'wiki': 'true'}, dry_run=True)
  assert '.claude/skills/ui-ux-testing' in dry['actions']['linked_for_claude'], dry
  report = scaffold(root, flags={'wiki': 'true'})
  assert report['project_name'] == 'mono', report
  assert report['modules']['frontend'] and report['modules']['database'], report
  agents = (root / 'AGENTS.md').read_text()
  assert '`pnpm run dev`' in agents and 'npm install' not in agents.replace('pnpm install', ''), agents
  assert agents.count('`pnpm install`') == 1, agents  # root install covers the workspace
  assert '`apps/web/`' in (root / '.agents/rules/ui-ux-testing.md').read_text()
  assert 'Row-Level Security' in (root / '.agents/rules/database.md').read_text()
  # A later default run keeps the modules chosen before (wiki stays forced on).
  assert scaffold(root)['modules']['wiki'] is True
  assert f"{report['project_name']}-wiki" in (root / '.agents/rules/use-wiki.md').read_text()
  link = root / '.claude/skills/ui-ux-testing'
  assert (link / 'SKILL.md').is_file(), 'skill not exposed to Claude Code'
  manifest = json.loads((root / '.agents/bootstrap.json').read_text())
  assert manifest['modules']['wiki'] is True
  # verify honours the manifest: forced wiki is expected even though qmd is absent.
  verify = cli.verify_target(str(root))
  assert verify['failures'] == [], verify
  assert any('qmd' in w for w in verify['warnings']), verify


def test_existing_docs_and_legacy_conflict(root: Path) -> None:
  write(root, {
      'go.mod': 'module example.com/svc\n\nrequire gorm.io/gorm v1.25.0\n',
      'CLAUDE.md': '# My notes\nHand-written architecture.\n',
      '.agents/skills/shared/SKILL.md': '---\nname: shared\ndescription: v2\n---\n',
      '.agent/skills/shared/SKILL.md': '---\nname: shared\ndescription: v1\n---\n',
      '.agent/skills/only-legacy/SKILL.md': '---\nname: only-legacy\ndescription: x\n---\n',
      '.agent/notes.txt': 'keep me',
      '.agent/rules/money.md': 'Never use float64 for money.\n',
  })
  before = (root / 'CLAUDE.md').read_text()
  dry = scaffold(root, consolidate=True, dry_run=True)
  assert not (root / 'AGENTS.md').exists() and not (root / '.agents/bootstrap.json').exists()
  assert dry['actions']['legacy_conflicts'] == ['.agent/skills/shared'], dry

  report = scaffold(root, consolidate=True)
  assert (root / 'CLAUDE.md').read_text() == before, 'existing CLAUDE.md was modified'
  assert report['actions']['pending_root_merges'], report
  assert (root / '.agents/pending-root-updates.md').is_file()
  assert (root / '.agent').is_dir(), '.agent/ deleted despite a conflict'
  assert (root / '.agents/skills/only-legacy/SKILL.md').is_file()
  assert (root / '.agents/notes.txt').read_text() == 'keep me'
  assert '`go test ./...`' in (root / 'AGENTS.md').read_text()
  assert report['project_name'] == 'svc', report['project_name']
  pending = (root / '.agents/pending-root-updates.md').read_text()
  assert '@.agents/rules/money.md' in pending, 'moved legacy rule not imported'

  # Once the user resolves the conflict, consolidation removes .agent/.
  (root / '.agent/skills/shared/SKILL.md').write_text(
      (root / '.agents/skills/shared/SKILL.md').read_text())
  scaffold(root, consolidate=True)
  assert not (root / '.agent').exists()


if __name__ == '__main__':
  for test in (test_python_repo, test_pnpm_monorepo, test_existing_docs_and_legacy_conflict):
    with tempfile.TemporaryDirectory() as tmp:
      test(Path(tmp))
    print(f'ok  {test.__name__}')
