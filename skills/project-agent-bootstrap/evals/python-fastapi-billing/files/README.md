# billing-api

FastAPI service that issues and tracks customer invoices for Acme.

- Dev server: `uv run uvicorn billing.main:app --reload`
- Tests: `uv run pytest`
- Migrations: `uv run alembic upgrade head`

Config comes from env vars (`DATABASE_URL`), see `src/billing/settings.py`.
