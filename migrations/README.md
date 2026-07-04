# Database migrations (Alembic)

The local desktop/demo build uses a lightweight SQLite schema created on demand.
Alembic here targets the **future SQL backend** (Postgres/Timescale) behind the
`Repository` protocol, so the schema has a versioned, reversible history.

```bash
pip install -e ".[migrations]"
alembic -c migrations/alembic.ini upgrade head     # apply
alembic -c migrations/alembic.ini downgrade -1     # rollback one
python migrations/seed.py                           # seed demo data
```

Status: ✅ Generated (config + initial revision + seed). ⚠ Requires
`alembic`/`sqlalchemy` (extra `[migrations]`); not executed in this sandbox.
