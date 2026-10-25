---
trigger: always_on
---

# Database Safety

This project reaches its database through {{DB_STACK}}. Unless the user says otherwise, assume the configured connection may point at **production data**.

1. **No destructive operations without explicit approval**: {{DESTRUCTIVE_EXAMPLES}}, `DROP`/`TRUNCATE`, or deleting migration files.
2. **Schema changes go through migrations** committed to the repo, never manual edits on a shared database.
3. **Inspect safely**: read-only `SELECT` with a `LIMIT` (or the ORM's equivalent); no full-table dumps.
4. **No unprompted writes**: do not insert, update, or delete records unless the user asked for it.
5. **Keep access control intact**{{RLS_NOTE}}.
6. If skills for these tools are installed (for example `supabase` or a Postgres best-practices skill), load them before touching the database.

Be meticulous: a mistake here can destroy data that no code change brings back.
