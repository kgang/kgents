# Chat Persistence Migration Guide

## Overview

This guide explains how to migrate from in-memory chat storage to persistent D-gent storage.

## What Changed

### Before (In-Memory)
```python
# protocols/api/chat.py
_sessions: dict[str, ChatSession] = {}  # Lost on restart
```

### After (Persistent)
```python
# services/chat/persistence.py
class ChatPersistence:
    """StorageProvider-backed persistence."""
    async def save_session(self, session: ChatSession) -> None
    async def load_session(self, session_id: str) -> ChatSession | None
```

## Migration Steps

### 1. Update FastAPI App Startup

Add persistence initialization to your app lifespan:

```python
# protocols/api/app.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from protocols.api.chat_persistent import initialize_persistence

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan manager."""
    # Initialize persistence on startup
    await initialize_persistence()

    yield

    # Cleanup on shutdown (optional)
    # await get_persistence().close()

app = FastAPI(lifespan=lifespan)
```

### 2. Switch Router

Replace the in-memory router with the persistent router:

```python
# Before
from protocols.api.chat import create_chat_router

# After
from protocols.api.chat_persistent import create_chat_router

router = create_chat_router()
app.include_router(router)
```

### 3. Database Configuration

#### SQLite (Default)
No configuration needed. Uses XDG paths automatically:
- `~/.local/share/kgents/membrane.db`

#### PostgreSQL
Set environment variable:
```bash
export KGENTS_DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/kgents"
```

Or create `~/.config/kgents/infrastructure.yaml`:
```yaml
profile: production
providers:
  relational:
    type: postgres
    connection: "postgresql+asyncpg://user:pass@localhost:5432/kgents"
```

### 4. Run Migrations

Migrations run automatically on first `ChatPersistence.create()`.

To verify:
```bash
sqlite3 ~/.local/share/kgents/membrane.db ".schema chat_sessions"
```

### 5. Test Persistence

```python
import pytest
from services.chat.persistence import ChatPersistence
from services.chat import ChatSession

@pytest.mark.asyncio
async def test_session_survives_restart():
    # Create persistence
    persistence = await ChatPersistence.create()

    # Create session
    session = ChatSession.create()
    session.add_turn("Hello", "Hi there!")

    # Save
    await persistence.save_session(session)
    session_id = session.id

    # Simulate restart: close and recreate
    await persistence.close()
    persistence = await ChatPersistence.create()

    # Load
    loaded = await persistence.load_session(session_id)

    # Verify
    assert loaded is not None
    assert loaded.turn_count == 1
```

## API Endpoint Changes

### New Endpoints

```
GET  /api/chat/sessions          # List all sessions (paginated)
DELETE /api/chat/:id              # Delete session
POST /api/chat/:id/crystal        # Crystallize session
GET  /api/chat/:id/crystal        # Get crystal
```

### Unchanged Endpoints

```
POST /api/chat/session            # Create session
GET  /api/chat/session/:id        # Get session
POST /api/chat/:id/send           # Send message (SSE)
POST /api/chat/:id/fork           # Fork session
POST /api/chat/:id/rewind         # Rewind session
GET  /api/chat/:id/evidence       # Get evidence
```

## Data Schema

### chat_sessions
```sql
CREATE TABLE chat_sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    parent_id TEXT REFERENCES chat_sessions(id),
    fork_point INTEGER,
    branch_name TEXT NOT NULL DEFAULT 'main',
    state TEXT NOT NULL DEFAULT 'idle',
    turn_count INTEGER NOT NULL DEFAULT 0,
    context_size INTEGER NOT NULL DEFAULT 0,
    evidence_json TEXT NOT NULL DEFAULT '{}',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    is_merged INTEGER NOT NULL DEFAULT 0,
    merged_into TEXT,
    created_at TEXT NOT NULL,
    last_active TEXT NOT NULL
);
```

### chat_turns
```sql
CREATE TABLE chat_turns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    turn_number INTEGER NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    user_linearity TEXT NOT NULL DEFAULT 'preserved',
    assistant_linearity TEXT NOT NULL DEFAULT 'preserved',
    tools_json TEXT,
    evidence_delta_json TEXT,
    confidence REAL,
    started_at TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    UNIQUE(session_id, turn_number)
);
```

### chat_crystals
```sql
CREATE TABLE chat_crystals (
    session_id TEXT PRIMARY KEY REFERENCES chat_sessions(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    key_decisions_json TEXT,
    artifacts_json TEXT,
    final_evidence_json TEXT,
    final_turn_count INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
```

### chat_checkpoints
```sql
CREATE TABLE chat_checkpoints (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    turn_count INTEGER NOT NULL,
    context_json TEXT NOT NULL,
    evidence_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

## Performance Considerations

### Indexing
All critical queries are indexed:
- `idx_chat_sessions_project` - Filter by project
- `idx_chat_sessions_parent` - Find branches
- `idx_chat_sessions_active` - Sort by activity
- `idx_chat_turns_session` - Load turns efficiently

### Atomic Operations
Sessions and turns are saved atomically:
1. Upsert session metadata
2. Delete old turns
3. Insert new turns
4. Upsert checkpoints

All in a single transaction (implicitly via SQLite).

### Caching
Consider adding Redis/in-memory cache for:
- Active sessions (currently being chatted)
- Recent sessions (reduce DB hits)

Example:
```python
class CachedChatPersistence:
    def __init__(self, persistence: ChatPersistence):
        self.persistence = persistence
        self.cache: dict[str, ChatSession] = {}

    async def load_session(self, session_id: str) -> ChatSession | None:
        if session_id in self.cache:
            return self.cache[session_id]

        session = await self.persistence.load_session(session_id)
        if session:
            self.cache[session_id] = session
        return session
```

## Rollback Plan

If persistence causes issues:

1. Keep old `chat.py` as `chat_inmemory.py`
2. Switch import back:
   ```python
   from protocols.api.chat_inmemory import create_chat_router
   ```
3. Remove lifespan initialization

## Testing

Run persistence tests:
```bash
cd impl/claude
pytest services/chat/test_persistence.py -v
```

Run API tests (if available):
```bash
pytest protocols/api/test_chat_persistent.py -v
```

## Troubleshooting

### "ChatPersistence not initialized"
- Ensure `initialize_persistence()` is called in app lifespan
- Check that `create_chat_router()` is called AFTER initialization

### Database locked (SQLite)
- Enable WAL mode (done automatically)
- Check for long-running transactions
- Consider PostgreSQL for high concurrency

### Missing tables
- Migrations run automatically on first init
- Check `schema_version` table for applied migrations
- Manually run schema if needed:
  ```python
  from services.chat.persistence import CHAT_SCHEMA_V1
  await storage.relational.execute(CHAT_SCHEMA_V1)
  ```

### Session not found after save
- Check transaction commit (SQLite auto-commits)
- Verify session ID matches between save/load
- Check database file permissions

## Next Steps

1. **Monitor Performance**: Track save/load times
2. **Add Metrics**: Session count, turn count, storage size
3. **Implement Cleanup**: Archive old sessions
4. **Add Search**: Full-text search on turns
5. **Implement Sync**: Multi-instance session sharing

## See Also

- `spec/protocols/chat-web.md` - Chat protocol specification
- `docs/skills/metaphysical-fullstack.md` - Architecture pattern
- `services/witness/persistence.py` - Similar persistence pattern
