---
description: Create all SQLAlchemy model tables in the database
---

# /init-db - Create Database Tables

Create all SQLAlchemy model tables in the database.

## When to Use

Run this when you see `UndefinedTableError` after adding new models:

```
relation "brain_teaching_crystals" does not exist
```

## Protocol

1. Run the init_db command:

```bash
cd /Users/kentgang/git/kgents/impl/claude && uv run python -c "
import asyncio
from models.base import init_db

async def main():
    engine = await init_db()
    print('Tables created successfully')
    await engine.dispose()

asyncio.run(main())
"
```

2. Report result to user

## Notes

- This is idempotent - safe to run multiple times
- Uses `Base.metadata.create_all` which only creates tables that don't exist
- For production migrations, use Alembic instead
- Requires `KGENTS_DATABASE_URL` env var for Postgres (defaults to SQLite otherwise)
