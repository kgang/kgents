# Storage Migration Protocol

> *Research-oriented patterns for transitioning between storage backends.*

## Overview

kgents supports multiple storage tiers, enabling graceful transitions from portable SQLite to production PostgreSQL. This document captures migration patterns, environment semantics, and rollback strategies.

## Storage Tiers

| Tier | Backend | Use Case | Characteristics |
|------|---------|----------|-----------------|
| **Portable** | SQLite `membrane.db` | Local dev, single user | Zero config, XDG-compliant, file-based |
| **Unified** | Docker Postgres | Team dev, production-like | Full SQL, connection pooling, same schema |
| **Production** | Managed Postgres | Cloud deployment | HA, replication, managed backups |

The system auto-detects and gracefully degrades: Production -> Unified -> Portable.

## Environment Variables

### Canonical (v1.0+)

```bash
# Single source of truth for ALL storage
KGENTS_DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db

# SQLite mode (explicit or default)
KGENTS_DATABASE_URL=sqlite+aiosqlite:///~/.local/share/kgents/membrane.db
```

### Legacy (Deprecated)

```bash
# D-gent / Brain auto-detection (converted automatically)
KGENTS_POSTGRES_URL=postgresql://user:pass@host:port/db

# Force D-gent backend (rarely needed)
KGENTS_DGENT_BACKEND=POSTGRES
```

### Resolution Priority

1. `KGENTS_DATABASE_URL` (canonical)
2. `KGENTS_POSTGRES_URL` (legacy, auto-converted)
3. `XDG_DATA_HOME/kgents/membrane.db`
4. `~/.local/share/kgents/membrane.db`

## Migration Procedures

### SQLite to Docker Postgres

```bash
# 1. Start Docker Postgres
docker compose up -d

# 2. Set environment
export KGENTS_DATABASE_URL=postgresql+asyncpg://kgents:kgents@localhost:5432/kgents

# 3. Create schema
uv run alembic upgrade head

# 4. Migrate data (dry run first)
uv run python scripts/migrate_membrane_to_postgres.py --dry-run
uv run python scripts/migrate_membrane_to_postgres.py --execute

# 5. Verify
kg brain status

# 6. Cleanup old SQLite
rm ~/.local/share/kgents/membrane.db
```

### Rollback to SQLite

```bash
# Simply unset the env var
unset KGENTS_DATABASE_URL

# System auto-falls back to XDG SQLite
# Postgres data remains (can re-migrate later)
```

## Schema Management

### Two-Track Architecture

kgents uses a **dual-track storage model**:

1. **SQLAlchemy/Alembic Track** (typed models)
   - Managed by Alembic migrations
   - Tables: `brain_crystals`, `town_citizens`, `garden_ideas`, etc.
   - Full CRUD with foreign keys

2. **D-gent Track** (semantic memory)
   - Dynamic schema creation
   - Tables: `captures` (Brain), `data` (D-gent)
   - Append-only with causal chains

Both tracks coexist in the same database when using Postgres.

### Cross-Database Migrations

Migrations must be database-agnostic. Use dialect detection:

```python
def is_postgres() -> bool:
    from alembic import context
    return context.get_context().dialect.name == "postgresql"

def upgrade():
    if is_postgres():
        # Postgres: SERIAL, NOW(), ON CONFLICT
        op.execute("CREATE TABLE foo (id SERIAL PRIMARY KEY...)")
    else:
        # SQLite: AUTOINCREMENT, datetime('now'), INSERT OR IGNORE
        op.execute("CREATE TABLE foo (id INTEGER PRIMARY KEY AUTOINCREMENT...)")
```

## Research Notes

### Connection Pooling

With unified Postgres, multiple subsystems may create pools:
- SQLAlchemy async engine (5-10 connections)
- D-gent PostgresBackend (2-10 connections)
- Brain PostgresRelationalStore (2-10 connections)

**Future work**: Centralized `ConnectionManager` to share pools.

### Data Coherence

The two-track model means the same "memory" could exist in both:
- `captures` (raw content + embeddings)
- `brain_crystals` (queryable metadata)

**Future work**: TableAdapter bridge to sync coherently.

### Multi-Tenant Considerations

Current design assumes single tenant. For SaaS:
- Add `tenant_id` column to all tables
- Use connection string per tenant
- Consider schema-per-tenant for isolation

## Related

- `docs/skills/unified-storage.md` - Implementation patterns
- `impl/claude/models/base.py` - SQLAlchemy foundation
- `impl/claude/scripts/migrate_membrane_to_postgres.py` - Migration tool
- `impl/claude/system/migrations/` - Alembic versions

---

*Last updated: 2025-12-20 | Protocol version: 1.0*
