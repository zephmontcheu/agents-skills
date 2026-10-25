#!/usr/bin/env python3
"""CLI helper for the project-agent-bootstrap skill.

Provides three subcommands:
- inspect: Detects repository stack and audits existing agent customizations.
- scaffold: Deploys or merges `.agents/` rules, skills, agents, workflows, and root docs.
- verify: Validates the installed customization foundation, wiki vault, and graphify state.

Uses Python 3.9+ stdlib only, on Linux, macOS and Windows. Prints JSON to
stdout, or writes it to --output.
"""

import argparse
import json
from pathlib import Path
import re
import shutil
import sys


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_ROOT / 'assets' / 'templates'
BUNDLE_DIR = SKILL_ROOT / 'assets' / 'bundle'
MANIFEST = Path('.agents') / 'bootstrap.json'

SKIP_DIRS = {
    'node_modules', 'venv', '.venv', 'env', 'dist', 'build', 'target',
    'vendor', '__pycache__', 'graphify-out', 'coverage', 'out',
}

MANIFEST_FILES = (
    'package.json', 'pyproject.toml', 'requirements.txt', 'setup.py',
    'Pipfile', 'go.mod', 'Cargo.toml', 'pom.xml', 'build.gradle',
    'build.gradle.kts', 'Gemfile', 'composer.json', 'CMakeLists.txt', 'Makefile',
)

FRONTEND_DEPS = {
    'react', 'react-dom', 'vite', 'next', 'vue', 'nuxt', 'svelte',
    '@sveltejs/kit', 'astro', '@angular/core', 'solid-js', 'preact',
    '@remix-run/react', '@builder.io/qwik', 'tailwindcss',
}

# Tool -> example destructive commands for the database rule (on top of the
# generic `DROP`/`TRUNCATE` in the template). Keys are matched against
# package.json dependency names and manifest tokens.
DATABASE_TOOLS = {
    'prisma': '`prisma migrate reset`, `prisma db push --accept-data-loss`',
    '@prisma/client': '`prisma migrate reset`, `prisma db push --accept-data-loss`',
    '@supabase/supabase-js': '`supabase db reset --linked`, disabling RLS',
    'supabase': '`supabase db reset --linked`, disabling RLS',
    'drizzle-orm': '`drizzle-kit push` against a shared database',
    'typeorm': '`typeorm schema:drop`, `synchronize: true` in production',
    'sequelize': '`sequelize db:drop`, `sync({ force: true })`',
    'knex': '`knex migrate:rollback --all`',
    'kysely': 'dropping tables in ad-hoc migrations',
    'pg': '',
    'mysql2': '',
    'better-sqlite3': 'deleting the database file',
    '@neondatabase/serverless': 'deleting branches',
    'mongoose': '`dropDatabase()`, `deleteMany({})`',
    'mongodb': '`dropDatabase()`, `deleteMany({})`',
    'sqlalchemy': '`alembic downgrade base`, `metadata.drop_all()`',
    'sqlmodel': '`alembic downgrade base`, `metadata.drop_all()`',
    'alembic': '`alembic downgrade base`',
    'django': '`manage.py flush`, `manage.py migrate <app> zero`',
    'psycopg': '',
    'psycopg2': '',
    'psycopg2-binary': '',
    'asyncpg': '',
    'peewee': '`drop_tables()`',
    'tortoise-orm': '`Tortoise.drop_databases()`',
    'pymongo': '`drop_database()`, `delete_many({})`',
    'gorm.io': '`Migrator().DropTable()`',
    'pgx': '',
    'sqlx': '`sqlx database reset`, `sqlx database drop`',
    'diesel': '`diesel database reset`',
    'sea-orm': '`sea-orm-cli migrate fresh`',
    'activerecord': '`rails db:drop`, `rails db:reset`',
}

POSTGRES_TOOLS = {
    'prisma', '@prisma/client', '@supabase/supabase-js', 'supabase', 'pg',
    '@neondatabase/serverless', 'psycopg', 'psycopg2', 'psycopg2-binary',
    'asyncpg', 'pgx',
}

FORMATTER_CONFIGS = (
    '.editorconfig', '.prettierrc', '.prettierrc.json', '.prettierrc.js',
    '.prettierrc.cjs', '.prettierrc.yaml', 'prettier.config.js',
    'prettier.config.mjs', 'biome.json', 'biome.jsonc', 'eslint.config.js',
    'eslint.config.mjs', 'eslint.config.ts', '.eslintrc', '.eslintrc.json',
    '.eslintrc.js', '.eslintrc.cjs', 'ruff.toml', '.ruff.toml', 'setup.cfg',
    '.flake8', 'rustfmt.toml', '.rustfmt.toml', '.golangci.yml',
    '.golangci.yaml', 'checkstyle.xml', '.rubocop.yml', '.clang-format',
)

NODE_SCRIPTS = ('dev', 'start', 'build', 'test', 'test:e2e', 'lint', 'typecheck',
                'format', 'generate', 'migrate', 'db:generate', 'db:migrate')
MAKE_TARGETS = ('dev', 'run', 'build', 'test', 'lint', 'check', 'format')

MODULE_RULES = {
    'wiki': ['use-wiki.md', 'updating-wiki-systematically.md'],
    'graphify': ['graphify.md'],
    'frontend': ['ui-ux-testing.md'],
    'database': ['database.md'],
}
MODULE_SKILLS = {
    'wiki': ['updating-wiki-systematically'],
    'frontend': ['ui-ux-testing', 'ux-optimizer'],
}
MODULE_AGENTS = {'frontend': ['ux-optimizer']}
MODULE_WORKFLOWS = {'graphify': ['graphify.md']}


def emit(data: dict, output_file) -> None:
  """Prints JSON to stdout, or writes it to output_file with a status line."""
  text = json.dumps(data, indent=2, ensure_ascii=False)
  if not output_file:
    print(text)
    return
  try:
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding='utf-8')
    print(f'Success! Data written to: {output_file}')
  except OSError as e:
    print(f'Error writing to file {output_file}: {e}', file=sys.stderr)
    sys.exit(1)


def resolve_target(target_str: str) -> Path:
  target = Path(target_str).resolve()
  if not target.is_dir():
    print(f'Error: Target directory does not exist: {target}', file=sys.stderr)
    sys.exit(1)
  return target


def visible_subdirs(path: Path) -> list:
  return [
      p for p in sorted(path.iterdir())
      if p.is_dir() and not p.name.startswith('.') and p.name not in SKIP_DIRS
  ]


def read_text(path: Path) -> str:
  try:
    return path.read_text(encoding='utf-8', errors='ignore')
  except OSError:
    return ''


def manifest_tokens(path: Path) -> set:
  """Lower-cased package-name-like tokens of a text manifest.

  Exact tokens instead of substrings, so `pg` does not match `upgrade`.
  """
  return set(re.findall(r'[a-z0-9_.@\-]+', read_text(path).lower()))


def parse_package_json(pkg_path: Path) -> dict:
  """Safely reads a package.json file and extracts dependencies and scripts."""
  try:
    raw = json.loads(pkg_path.read_text(encoding='utf-8'))
  except (OSError, json.JSONDecodeError):
    return {'deps': set(), 'scripts': {}}

  deps = set()
  for section in ('dependencies', 'devDependencies', 'peerDependencies'):
    section_data = raw.get(section)
    if isinstance(section_data, dict):
      deps.update(section_data.keys())

  scripts = raw.get('scripts') if isinstance(raw.get('scripts'), dict) else {}
  return {'deps': deps, 'scripts': scripts}


def first_existing(dirs, names):
  for d in dirs:
    for name in names:
      if (d / name).exists():
        return name
  return None


def describe_project(proj: Path, target: Path) -> dict:
  """Detects languages, frameworks, and real commands of one project dir."""
  rel = '.' if proj == target else proj.relative_to(target).as_posix()
  lock_dirs = [proj, target]

  def in_workspace(lock) -> bool:
    # A lockfile only at the root means the root install covers this package.
    return proj != target and bool(lock) and not (proj / lock).exists()
  languages = []
  commands = []
  frontend = set()
  database = set()

  if (proj / 'package.json').is_file():
    pkg = parse_package_json(proj / 'package.json')
    lock = first_existing(
        lock_dirs,
        ['pnpm-lock.yaml', 'yarn.lock', 'bun.lockb', 'bun.lock', 'package-lock.json'],
    )
    pm = {'pnpm-lock.yaml': 'pnpm', 'yarn.lock': 'yarn', 'bun.lockb': 'bun',
          'bun.lock': 'bun'}.get(lock, 'npm')
    languages.append(f'node ({pm})')
    if not in_workspace(lock):
      commands.append(f'{pm} install')
    commands += [f'{pm} run {s}' for s in NODE_SCRIPTS if s in pkg['scripts']]
    frontend |= pkg['deps'] & FRONTEND_DEPS
    database |= pkg['deps'] & DATABASE_TOOLS.keys()

  py_files = [f for f in ('pyproject.toml', 'requirements.txt', 'setup.py', 'Pipfile')
              if (proj / f).is_file()]
  if py_files:
    tokens = set().union(*(manifest_tokens(proj / f) for f in py_files))
    lock = first_existing(lock_dirs, ['uv.lock', 'poetry.lock', 'Pipfile.lock'])
    runner, install = {
        'uv.lock': ('uv run ', 'uv sync'),
        'poetry.lock': ('poetry run ', 'poetry install'),
        'Pipfile.lock': ('pipenv run ', 'pipenv install --dev'),
    }.get(lock, ('', 'pip install -r requirements.txt'
                 if 'requirements.txt' in py_files else 'pip install -e .'))
    languages.append('python')
    if not in_workspace(lock):
      commands.append(install)
    if 'pytest' in tokens or (proj / 'tests').is_dir():
      commands.append(f'{runner}pytest')
    if 'ruff' in tokens:
      commands.append(f'{runner}ruff check .')
    if 'mypy' in tokens:
      commands.append(f'{runner}mypy .')
    if (proj / 'manage.py').is_file():
      commands.append(f'{runner}python manage.py test')
    database |= tokens & DATABASE_TOOLS.keys()

  if (proj / 'go.mod').is_file():
    languages.append('go')
    commands += ['go build ./...', 'go test ./...']
    database |= manifest_tokens(proj / 'go.mod') & DATABASE_TOOLS.keys()

  if (proj / 'Cargo.toml').is_file():
    languages.append('rust')
    commands += ['cargo build', 'cargo test', 'cargo clippy']
    database |= manifest_tokens(proj / 'Cargo.toml') & DATABASE_TOOLS.keys()

  if (proj / 'pom.xml').is_file():
    languages.append('java (maven)')
    commands.append('mvn verify')
  elif (proj / 'build.gradle').is_file() or (proj / 'build.gradle.kts').is_file():
    gradle = './gradlew' if (proj / 'gradlew').is_file() else 'gradle'
    languages.append('jvm (gradle)')
    commands += [f'{gradle} build', f'{gradle} test']

  if (proj / 'Gemfile').is_file():
    languages.append('ruby')
    commands.append('bundle install')
    database |= manifest_tokens(proj / 'Gemfile') & DATABASE_TOOLS.keys()

  if (proj / 'composer.json').is_file():
    languages.append('php')
    commands.append('composer install')

  if (proj / 'CMakeLists.txt').is_file():
    languages.append('c/c++ (cmake)')
    commands += ['cmake -B build', 'cmake --build build', 'ctest --test-dir build']

  if (proj / 'Makefile').is_file():
    makefile = read_text(proj / 'Makefile')
    commands += [f'make {t}' for t in MAKE_TARGETS
                 if re.search(rf'^{t}\s*:', makefile, re.M)]

  if (proj / 'prisma' / 'schema.prisma').is_file():
    database.add('prisma')
  if (proj / 'supabase').is_dir():
    database.add('supabase')

  return {
      'path': rel,
      'languages': languages,
      'commands': commands,
      'frontend_deps': sorted(frontend),
      'database_tools': sorted(database),
  }


def detect_stack(target: Path) -> dict:
  """Scans the root and two directory levels for project manifests."""
  candidates = [target]
  for child in visible_subdirs(target):
    candidates.append(child)
    candidates += visible_subdirs(child)

  def is_project(d: Path) -> bool:
    found = {m for m in MANIFEST_FILES if (d / m).is_file()}
    # A nested CMakeLists.txt/Makefile is part of its parent's build.
    if found and found <= {'CMakeLists.txt', 'Makefile'} and d != target:
      return not any((d.parent / f).is_file() for f in found)
    return bool(found) or (d / 'prisma' / 'schema.prisma').is_file()

  projects = [describe_project(d, target) for d in candidates if is_project(d)]
  # A root `supabase/` folder belongs to the root even without a manifest.
  if (target / 'supabase').is_dir() and not any(p['path'] == '.' for p in projects):
    projects.insert(0, describe_project(target, target))

  frontend_dirs = [p['path'] for p in projects if p['frontend_deps']]
  if not frontend_dirs and (target / 'frontend').is_dir():
    frontend_dirs = ['frontend']
  database_tools = sorted({t for p in projects for t in p['database_tools']})
  formatter_configs = sorted(
      f for f in FORMATTER_CONFIGS
      if (target / f).is_file() or any((target / p['path'] / f).is_file() for p in projects)
  )
  if '[tool.ruff]' in read_text(target / 'pyproject.toml'):
    formatter_configs.append('pyproject.toml [tool.ruff]')

  return {
      'has_frontend': bool(frontend_dirs),
      'has_database': bool(database_tools),
      'frontend_dirs': frontend_dirs,
      'database_tools': database_tools,
      'languages': sorted({l for p in projects for l in p['languages']}),
      'formatter_configs': formatter_configs,
      'projects': projects,
  }


def find_wiki_dirs(target: Path) -> list:
  """Finds existing Obsidian/qmd wiki vaults inside the target repository."""
  vaults = []
  for child in visible_subdirs(target):
    if child.name.endswith('-wiki') or child.name.endswith('-brain'):
      vaults.append(child.name)
    elif (child / 'wiki').is_dir() and (child / 'log.md').is_file():
      vaults.append(child.name)
  if (target / 'wiki').is_dir() and (target / 'log.md').is_file():
    vaults.append('.')
  return vaults


def tools_available() -> dict:
  return {
      'qmd': shutil.which('qmd') is not None,
      'graphify': shutil.which('graphify') is not None,
  }


def auto_modules(target: Path, stack: dict) -> dict:
  """Modules that `auto` resolves to, with the reason for each."""
  tools = tools_available()
  wiki_vaults = find_wiki_dirs(target)
  has_graph = (target / 'graphify-out' / 'graph.json').is_file()
  return {
      'frontend': stack['has_frontend'],
      'database': stack['has_database'],
      'wiki': bool(wiki_vaults) or tools['qmd'],
      'graphify': has_graph or tools['graphify'],
  }


def read_manifest(target: Path):
  try:
    return json.loads((target / MANIFEST).read_text(encoding='utf-8'))
  except (OSError, json.JSONDecodeError):
    return None


def expected_items(modules: dict) -> dict:
  def pick(table):
    return sorted({x for m, items in table.items() if modules.get(m) for x in items})
  return {
      'rules': pick(MODULE_RULES),
      'skills': pick(MODULE_SKILLS),
      'agents': pick(MODULE_AGENTS),
      'workflows': pick(MODULE_WORKFLOWS),
  }


def list_names(path: Path, dirs: bool) -> list:
  if not path.is_dir():
    return []
  if dirs:
    return sorted(p.name for p in path.iterdir() if p.is_dir())
  return sorted(p.name for p in path.glob('*.md'))


def audit_customizations(target: Path, modules: dict) -> dict:
  """Audits existing agent customization files and detects duplicates or gaps."""
  dot_agents = target / '.agents'
  legacy = target / '.agent'

  existing = {
      'rules': list_names(dot_agents / 'rules', dirs=False),
      'skills': list_names(dot_agents / 'skills', dirs=True),
      'agents': list_names(dot_agents / 'agents', dirs=True),
      'workflows': list_names(dot_agents / 'workflows', dirs=False),
  }
  expected = expected_items(modules)
  legacy_skills = list_names(legacy / 'skills', dirs=True)

  return {
      'has_agents_md': (target / 'AGENTS.md').is_file(),
      'has_claude_md': (target / 'CLAUDE.md').is_file(),
      'dot_agents_exists': dot_agents.is_dir(),
      'legacy_dot_agent_exists': legacy.is_dir(),
      'legacy_dot_agent_details': {
          'skills_in_dot_agent': legacy_skills,
          'agents_in_dot_agent': list_names(legacy / 'agents', dirs=True),
          'skills_only_in_legacy': sorted(set(legacy_skills) - set(existing['skills'])),
          'duplicated_skills': sorted(set(legacy_skills) & set(existing['skills'])),
      },
      'existing': existing,
      'expected_for_modules': expected,
      'missing_in_dot_agents': {
          k: sorted(set(expected[k]) - set(existing[k])) for k in expected
      },
      'wiki_vaults': find_wiki_dirs(target),
      'has_graphify_graph': (target / 'graphify-out' / 'graph.json').is_file(),
      'tools_available': tools_available(),
  }


def manifest_name(target: Path) -> str:
  """Project name from the root manifest, else the folder name."""
  try:
    name = json.loads(read_text(target / 'package.json') or '{}').get('name')
  except (json.JSONDecodeError, AttributeError):
    name = None
  for manifest, pattern in (('pyproject.toml', r'^name\s*=\s*["\']([^"\']+)'),
                            ('Cargo.toml', r'^name\s*=\s*["\']([^"\']+)'),
                            ('go.mod', r'^module\s+(\S+)')):
    match = re.search(pattern, read_text(target / manifest), re.M)
    if not name and match:
      name = match.group(1)
  parts = (name or target.name).split('/')
  # Go modules end in /v2, /v3... for major versions.
  if len(parts) > 1 and re.fullmatch(r'v\d+', parts[-1]):
    parts.pop()
  return slugify(parts[-1])


def slugify(name: str) -> str:
  return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'project'


def inspect_target(target_str: str) -> dict:
  """Runs full stack detection and customization audit on target directory."""
  target = resolve_target(target_str)
  stack = detect_stack(target)
  manifest = read_manifest(target)
  modules = manifest['modules'] if manifest else auto_modules(target, stack)
  audit = audit_customizations(target, modules)

  project_slug = (manifest or {}).get('project_name') or manifest_name(target)
  recommended_wiki = (
      audit['wiki_vaults'][0] if audit['wiki_vaults'] else f'{project_slug}-wiki'
  )

  recommendations = []
  if audit['legacy_dot_agent_exists']:
    recommendations.append(
        'Consolidate legacy `.agent/` into `.agents/` using --consolidate-dot-agent.'
    )
  if not audit['has_agents_md'] or not audit['has_claude_md']:
    recommendations.append('Generate root `AGENTS.md` and `CLAUDE.md` files.')
  for kind, items in audit['missing_in_dot_agents'].items():
    if items:
      recommendations.append(
          f"Install missing {kind} in `.agents/{kind}/`: {', '.join(items)}"
      )
  if modules['wiki'] and not audit['wiki_vaults']:
    recommendations.append(
        f'Initialize knowledge wiki `{recommended_wiki}/` via the `wiki-init` skill.'
    )
  if modules['graphify'] and not audit['has_graphify_graph']:
    recommendations.append(
        'Build the initial knowledge graph via the `graphify` skill.'
    )
  for tool, module in (('qmd', 'wiki'), ('graphify', 'graphify')):
    if not audit['tools_available'][tool]:
      recommendations.append(
          f'`{tool}` is not installed, so the {module} module stays off unless forced.'
      )

  return {
      'target': str(target),
      'project_name_suggestion': project_slug,
      'wiki_dir_suggestion': recommended_wiki,
      'modules': modules,
      'modules_source': 'manifest' if manifest else 'auto-detected',
      'stack': stack,
      'audit': audit,
      'recommendations': recommendations,
  }


def section(enabled: bool, text: str) -> str:
  return text if enabled else ''


def render_context(target: Path, project_name: str, wiki_dir: str,
                   modules: dict, stack: dict, rules: list, skills: list) -> dict:
  """Builds the {{PLACEHOLDER}} values shared by every template."""
  projects = stack['projects']

  structure = []
  for p in projects:
    if p['path'] == '.':
      continue
    tags = ', '.join(p['languages'] + p['frontend_deps'][:2] + p['database_tools'][:2])
    structure.append(f"- `{p['path']}/`" + (f' ({tags})' if tags else '') + ': TODO one-line purpose.')
  listed = {p['path'].split('/')[0] for p in projects}
  for d in visible_subdirs(target):
    if d.name not in listed and d.name != wiki_dir:
      structure.append(f'- `{d.name}/`: TODO one-line purpose.')
  if modules['wiki']:
    structure.append(f'- `{wiki_dir}/`: Obsidian knowledge vault indexed with `qmd`.')
  structure.append('- `.agents/`: Shared agent rules, skills, workflows, and subagents.')

  commands = [
      f"- `{p['path']}` ({', '.join(p['languages']) or 'make'}): "
      + ', '.join(f'`{c}`' for c in p['commands'])
      for p in projects if p['commands']
  ] or ['- TODO: document how to install, run, lint, and test this project.']

  if stack['formatter_configs']:
    configs = ', '.join(f'`{c}`' for c in stack['formatter_configs'])
    style = (f'Match the conventions of the surrounding code. Formatting and lint '
             f'rules are defined in {configs}: run those tools instead of '
             f'formatting by hand.')
  else:
    style = ('Match the conventions of the surrounding code. TODO: no formatter or '
             'linter config was detected; document the style rules here.')
  if any(l == 'go' for l in stack['languages']):
    style += ' Go code is formatted with `gofmt`.'
  if any(l == 'rust' for l in stack['languages']):
    style += ' Rust code is formatted with `cargo fmt`.'

  db_tools = stack['database_tools']
  destructive = list(dict.fromkeys(
      c for t in db_tools for c in DATABASE_TOOLS.get(t, '').split(', ') if c))
  frontend_dirs = ', '.join(f'`{d}/`' for d in stack['frontend_dirs']) or 'the frontend'
  uses_postgres = bool(set(db_tools) & POSTGRES_TOOLS)

  return {
      'PROJECT_NAME': project_name,
      'WIKI_DIR': wiki_dir,
      'STRUCTURE_SUMMARY': '\n'.join(structure),
      'COMMANDS_SUMMARY': '\n'.join(commands),
      'CODING_STYLE': style,
      'ARCHITECTURE_NOTES': 'TODO: describe the main components, how they talk to '
                            'each other, and where the entry points are.',
      'FRONTEND_DIRS': frontend_dirs,
      'DB_STACK': ', '.join(f'`{t}`' for t in db_tools) or 'its database client',
      'DESTRUCTIVE_EXAMPLES': ', '.join(destructive) or 'resetting or dropping the database',
      'RLS_NOTE': (': if the database uses PostgreSQL Row-Level Security (RLS), preserve '
                   'its policies and never disable RLS to make a query work' if uses_postgres else
                   ': never weaken permissions, roles, or auth checks to make a query work'),
      'FRONTEND_TESTING_RULE': section(
          modules['frontend'],
          f'\nAfter any UI change in {frontend_dirs}, run the `ui-ux-testing` skill '
          '(see `.agents/rules/ui-ux-testing.md`) before calling the task done.'),
      'DATABASE_SECURITY_TIPS': section(
          modules['database'],
          '\n## Security & Database Safety\n\n'
          f'Follow `.agents/rules/database.md`. Never run destructive commands '
          f'({", ".join(destructive) or "resets, drops"}) without explicit approval.'
          + (' If the database uses Row-Level Security (RLS), preserve its policies.'
             if uses_postgres else '')),
      'WIKI_SECTION': section(modules['wiki'], (TEMPLATES_DIR / 'sections' / 'wiki.md')
                              .read_text(encoding='utf-8')),
      'GRAPHIFY_SECTION': section(modules['graphify'], (TEMPLATES_DIR / 'sections' /
                                  'graphify.md').read_text(encoding='utf-8')),
      'RULE_LIST': '\n'.join(f'- `.agents/rules/{r}`' for r in rules)
                   or '- None deployed yet.',
      'RULE_IMPORTS': '\n'.join(f'@.agents/rules/{r}' for r in rules),
      'CLAUDE_SKILLS_NOTE': section(bool(skills), 'Project skills in `.agents/skills/` are '
                                    'linked into `.claude/skills/`, where Claude Code finds them.'),
  }


def render(text: str, context: dict) -> str:
  # Two passes: sections may themselves contain placeholders.
  for _ in range(2):
    for key, value in context.items():
      text = text.replace('{{' + key + '}}', value)
  return re.sub(r'\n{3,}', '\n\n', text)


def tree_bytes(path: Path) -> dict:
  if path.is_file():
    return {'': path.read_bytes()}
  return {
      f.relative_to(path).as_posix(): f.read_bytes()
      for f in path.rglob('*') if f.is_file() and '__pycache__' not in f.parts
  }


def consolidate_legacy(target: Path, dry_run: bool, actions: dict) -> None:
  """Moves `.agent/` items into `.agents/`; deletes `.agent/` only if nothing is lost.

  Items are the children of each `.agent/<sub>/` folder (one skill, one rule...)
  plus loose top-level files. An item already present in `.agents/` with
  different content is a conflict: `.agent/` is then kept for the user to decide.
  """
  legacy = target / '.agent'
  if not legacy.is_dir():
    return
  items = [c for e in sorted(legacy.iterdir())
           for c in (sorted(e.iterdir()) if e.is_dir() else [e])]
  for item in items:
    rel = item.relative_to(legacy)
    dest = target / '.agents' / rel
    if not dest.exists():
      actions['consolidated_from_legacy'].append(f'.agents/{rel.as_posix()}')
      if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if item.is_dir():
          shutil.copytree(item, dest)
        else:
          shutil.copy2(item, dest)
    elif tree_bytes(item) != tree_bytes(dest):
      actions['legacy_conflicts'].append(f'.agent/{rel.as_posix()}')

  if actions['legacy_conflicts']:
    actions['notes'].append(
        'Kept `.agent/`: the conflicting items differ from their `.agents/` '
        'counterparts. Ask the user which version to keep, then delete `.agent/`.'
    )
  else:
    if not dry_run:
      shutil.rmtree(legacy)
    actions['consolidated_from_legacy'].append('Removed legacy .agent/ directory')


def link_for_claude(target: Path, names: list, dry_run: bool, actions: dict) -> None:
  """Exposes `.agents/skills/*` in `.claude/skills/`, which Claude Code reads.

  Uses relative symlinks, falling back to a copy where symlinks are not
  allowed (Windows without developer mode).
  """
  for name in names:
    skill = target / '.agents' / 'skills' / name
    link = target / '.claude' / 'skills' / name
    if link.exists() or link.is_symlink() or not (dry_run or skill.is_dir()):
      continue
    actions['linked_for_claude'].append(f'.claude/skills/{name}')
    if dry_run:
      continue
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
      link.symlink_to(Path('..', '..', '.agents', 'skills', name),
                      target_is_directory=True)
    except OSError:
      shutil.copytree(skill, link)


def resolve_flag(flag: str, auto_value: bool) -> bool:
  return auto_value if flag == 'auto' else flag == 'true'


def scaffold_target(target_str: str, project_name, wiki_dir, flags: dict,
                    dry_run: bool, consolidate_dot_agent: bool) -> dict:
  """Deploys or merges the customization foundation into the target repo."""
  target = resolve_target(target_str)
  stack = detect_stack(target)
  auto = auto_modules(target, stack)
  # A previous run's choices win over auto-detection; explicit flags win over both.
  previous = read_manifest(target) or {}
  defaults = {**auto, **previous.get('modules', {})}
  modules = {m: resolve_flag(flags[m], defaults[m]) for m in auto}
  project_name = project_name or previous.get('project_name') or manifest_name(target)
  wiki_dir = (wiki_dir or previous.get('wiki_dir')
              or (find_wiki_dirs(target) or [f'{project_name}-wiki'])[0])

  actions = {
      'created_files': [],
      'skipped_existing': [],
      'consolidated_from_legacy': [],
      'legacy_conflicts': [],
      'linked_for_claude': [],
      'pending_root_merges': [],
      'notes': [],
  }
  dot_agents = target / '.agents'
  expected = expected_items(modules)
  context = {}

  def deploy(src: Path, dst: Path, templated: bool = False) -> None:
    rel = dst.relative_to(target).as_posix()
    if dst.exists():
      actions['skipped_existing'].append(rel)
      return
    actions['created_files'].append(rel)
    if dry_run:
      return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
      shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__'))
    elif templated:
      dst.write_text(render(src.read_text(encoding='utf-8'), context), encoding='utf-8')
    else:
      shutil.copy2(src, dst)

  if consolidate_dot_agent:
    consolidate_legacy(target, dry_run, actions)

  # Root docs list every rule and skill that will exist, including ones moved
  # over from `.agent/` or written by the team.
  def planned(kind: str, dirs: bool) -> list:
    moved = [Path(p).name for p in actions['consolidated_from_legacy']
             if p.startswith(f'.agents/{kind}/')]
    existing = list_names(dot_agents / kind, dirs=dirs)
    return sorted(set(expected[kind]) | set(existing) | set(moved))

  rules, skills = planned('rules', dirs=False), planned('skills', dirs=True)
  context.update(render_context(target, project_name, wiki_dir, modules, stack,
                                rules, skills))

  for rule in expected['rules']:
    deploy(TEMPLATES_DIR / 'rules' / rule, dot_agents / 'rules' / rule, templated=True)
  for wf in expected['workflows']:
    deploy(BUNDLE_DIR / 'workflows' / wf, dot_agents / 'workflows' / wf)
  for skill in expected['skills']:
    deploy(BUNDLE_DIR / 'skills' / skill, dot_agents / 'skills' / skill)
  for agent in expected['agents']:
    deploy(BUNDLE_DIR / 'agents' / agent, dot_agents / 'agents' / agent)

  link_for_claude(target, skills, dry_run, actions)

  rendered = {
      name: render((TEMPLATES_DIR / f'{name}.tpl').read_text(encoding='utf-8'), context)
      for name in ('AGENTS.md', 'CLAUDE.md')
  }
  for filename, text in rendered.items():
    root_file = target / filename
    if not root_file.exists():
      actions['created_files'].append(filename)
      if not dry_run:
        root_file.write_text(text, encoding='utf-8')
      continue
    existing_text = read_text(root_file).lower()
    checks = [
        (modules['graphify'], 'graphify', 'graphify section'),
        (modules['wiki'], wiki_dir.lower(), f'Wiki ({wiki_dir}) & qmd workflow section'),
        (modules['frontend'], 'ui-ux-testing', 'UI/UX Testing rule reference'),
        (modules['database'], 'database.md', 'Database safety rule reference'),
        (filename == 'AGENTS.md', '.agents/', 'Shared agent setup (`.agents/`) section'),
        (filename == 'CLAUDE.md', '@agents.md', '`@AGENTS.md` import'),
        (filename == 'CLAUDE.md' and bool(rules), '@.agents/rules/',
         'Always-on rule imports (`@.agents/rules/...`)'),
    ]
    missing = [label for on, needle, label in checks if on and needle not in existing_text]
    actions['skipped_existing'].append(filename)
    if missing:
      actions['pending_root_merges'].append({'file': filename, 'missing_topics': missing})

  if actions['pending_root_merges']:
    patch_file = dot_agents / 'pending-root-updates.md'
    actions['created_files'].append(patch_file.relative_to(target).as_posix())
    if not dry_run:
      dot_agents.mkdir(exist_ok=True)
      patch_file.write_text(
          '# Pending Root Documentation Sections\n\n'
          'Merge the missing sections below into the existing `AGENTS.md` / '
          '`CLAUDE.md`, keeping all project-specific content, then delete this file.\n\n'
          + ''.join(
              f'## Suggested `{name}`\n\n````markdown\n{text}\n````\n\n'
              for name, text in rendered.items()
          ),
          encoding='utf-8',
      )

  manifest = {'project_name': project_name, 'wiki_dir': wiki_dir, 'modules': modules}
  if not (target / MANIFEST).exists():
    actions['created_files'].append(MANIFEST.as_posix())
  if not dry_run:
    dot_agents.mkdir(exist_ok=True)
    (target / MANIFEST).write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

  return {
      'target': str(target),
      'dry_run': dry_run,
      'project_name': project_name,
      'wiki_dir': wiki_dir,
      'modules': modules,
      'modules_auto_detected': auto,
      'actions': actions,
  }


def has_valid_frontmatter(md_path: Path) -> bool:
  """Checks if a SKILL.md file starts with YAML frontmatter containing name and description."""
  text = read_text(md_path).replace('\r\n', '\n')
  if not text.startswith('---\n'):
    return False
  end_idx = text.find('\n---', 4)
  if end_idx == -1:
    return False
  fm = text[4:end_idx]
  return 'name:' in fm and 'description:' in fm


def verify_target(target_str: str) -> dict:
  """Verifies the integrity of the agent customization foundation in target."""
  target = resolve_target(target_str)
  manifest = read_manifest(target)
  stack = detect_stack(target)
  modules = manifest['modules'] if manifest else auto_modules(target, stack)
  audit = audit_customizations(target, modules)

  checks = []
  warnings = []
  failures = []

  if not manifest:
    warnings.append('No `.agents/bootstrap.json`; modules were auto-detected.')

  for doc in ('AGENTS.md', 'CLAUDE.md'):
    if (target / doc).is_file():
      checks.append(f'{doc} is present.')
    else:
      failures.append(f'Missing root `{doc}`.')

  if audit['legacy_dot_agent_exists']:
    warnings.append(
        'Legacy `.agent/` folder exists alongside `.agents/`. Run `scaffold --consolidate-dot-agent` to unify.'
    )
  else:
    checks.append('No duplicate `.agent/` directory detected.')

  missing = audit['missing_in_dot_agents']
  if missing['rules']:
    failures.append(f"Missing rules in `.agents/rules/`: {', '.join(missing['rules'])}")
  else:
    checks.append('All expected `.agents/rules/` files are present.')
  for kind in ('skills', 'agents', 'workflows'):
    if missing[kind]:
      warnings.append(f"Missing {kind} in `.agents/{kind}/`: {', '.join(missing[kind])}")

  skills_dir = target / '.agents' / 'skills'
  for skill_folder in (sorted(skills_dir.iterdir()) if skills_dir.is_dir() else []):
    if not skill_folder.is_dir():
      continue
    if has_valid_frontmatter(skill_folder / 'SKILL.md'):
      checks.append(f'Skill `{skill_folder.name}` has valid YAML frontmatter.')
    else:
      failures.append(f'Skill `{skill_folder.name}` is missing a valid `SKILL.md` frontmatter.')
    if not (target / '.claude' / 'skills' / skill_folder.name).exists():
      warnings.append(f'Skill `{skill_folder.name}` is not linked in `.claude/skills/`.')

  docs = [target / 'AGENTS.md', target / 'CLAUDE.md']
  docs += sorted((target / '.agents' / 'rules').glob('*.md'))
  for doc in docs:
    text = read_text(doc)
    rel = doc.relative_to(target).as_posix()
    if re.search(r'\{\{[A-Z_]+\}\}', text):
      failures.append(f'Unrendered `{{{{PLACEHOLDER}}}}` left in `{rel}`.')
    if re.search(r'\bTODO\b', text) and doc.parent == target:
      warnings.append(f'`{rel}` still contains TODO lines to fill in.')

  if (target / '.agents' / 'pending-root-updates.md').exists():
    warnings.append('`.agents/pending-root-updates.md` has not been merged and deleted yet.')

  if modules.get('wiki'):
    if audit['wiki_vaults']:
      checks.append(f"Wiki vault detected: {', '.join(audit['wiki_vaults'])}")
    else:
      warnings.append('No wiki vault yet. Run the `wiki-init` skill to create it.')
    if not audit['tools_available']['qmd']:
      warnings.append('Wiki module is on but `qmd` is not installed.')

  if modules.get('graphify'):
    if audit['has_graphify_graph']:
      checks.append('Knowledge graph `graphify-out/graph.json` is present.')
    else:
      warnings.append('No `graphify-out/graph.json`. Run the `graphify` skill to build it.')
    if not audit['tools_available']['graphify']:
      warnings.append('Graphify module is on but `graphify` is not installed.')

  overall = 'FAIL' if failures else 'WARN' if warnings else 'PASS'
  return {
      'target': str(target),
      'overall_status': overall,
      'modules': modules,
      'checks_passed': checks,
      'warnings': warnings,
      'failures': failures,
      'tools_available': audit['tools_available'],
  }


def main():
  parser = argparse.ArgumentParser(
      description='Bootstrap, audit, and synchronize multi-agent project customizations.'
  )
  subparsers = parser.add_subparsers(dest='command', required=True)

  def common(p):
    p.add_argument('--target', default='.', help='Project root (default: current directory).')
    p.add_argument('--output', help='Write the JSON report to this file instead of stdout.')

  common(subparsers.add_parser(
      'inspect', help='Detect repository stack and audit existing agent customizations.'))
  common(subparsers.add_parser(
      'verify', help='Verify the installed agent customization foundation.'))

  p_scaffold = subparsers.add_parser(
      'scaffold', help='Deploy or merge .agents/ customizations and root documentation.')
  common(p_scaffold)
  p_scaffold.add_argument('--project-name', help='Project name (default: target folder name).')
  p_scaffold.add_argument('--wiki-dir', help='Wiki vault folder (default: existing vault or <project>-wiki).')
  for module, what in (
      ('frontend', 'UI/UX testing rule, skills, and ux-optimizer subagent'),
      ('database', 'database safety rule'),
      ('wiki', 'qmd wiki rules and updating-wiki-systematically skill'),
      ('graphify', 'graphify rule and workflow'),
  ):
    p_scaffold.add_argument(f'--{module}', choices=['auto', 'true', 'false'],
                            default='auto', help=f'Deploy the {what} (default: auto).')
  p_scaffold.add_argument('--dry-run', action='store_true',
                          help='Report planned changes without writing anything.')
  p_scaffold.add_argument('--consolidate-dot-agent', action='store_true',
                          help='Move unique items from legacy .agent/ into .agents/; '
                               'remove .agent/ only if nothing would be lost.')

  args = parser.parse_args()
  if args.command == 'inspect':
    data = inspect_target(args.target)
  elif args.command == 'scaffold':
    data = scaffold_target(
        target_str=args.target,
        project_name=args.project_name,
        wiki_dir=args.wiki_dir,
        flags={m: getattr(args, m) for m in ('frontend', 'database', 'wiki', 'graphify')},
        dry_run=args.dry_run,
        consolidate_dot_agent=args.consolidate_dot_agent,
    )
  else:
    data = verify_target(args.target)
  emit(data, args.output)


if __name__ == '__main__':
  main()
