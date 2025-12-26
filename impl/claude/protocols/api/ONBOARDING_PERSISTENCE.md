# Onboarding Session Persistence

**Status**: Implemented | **Date**: 2025-12-25

---

## The Problem

Onboarding sessions were stored in-memory (`_sessions: dict[str, dict[str, Any]]`) and lost on server restart. This created a poor user experience where:

1. User starts onboarding
2. Server restarts
3. User loses their session and has to start over

---

## The Solution

Migrated onboarding sessions to persistent Postgres storage using SQLAlchemy ORM.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  API Endpoint              → onboarding.py                  │
│  /api/onboarding/start     → Creates OnboardingSession      │
│  /api/onboarding/status    → Queries OnboardingSession      │
│  /api/onboarding/complete  → Updates OnboardingSession      │
│  /api/onboarding/cleanup   → Deletes old sessions (24h)     │
└─────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────┐
│  SQLAlchemy Model          → models/onboarding.py           │
│  OnboardingSession         → Postgres/SQLite table          │
│  - id (PK)                 → Session UUID                   │
│  - user_id                 → Optional user context          │
│  - current_step            → Progress tracking              │
│  - completed               → Completion flag                │
│  - completed_at            → Completion timestamp           │
│  - first_kblock_id         → Created K-Block ID             │
│  - first_declaration       → User's first axiom (preserved) │
│  - created_at/updated_at   → TimestampMixin                 │
└─────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────┐
│  Database                  → Postgres (production)          │
│  Table: onboarding_sessions                                 │
│  Indexes:                                                   │
│  - user_id (FK lookup)                                      │
│  - created_at + completed (cleanup queries)                 │
│  - completed + completed_at (status queries)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### 1. Model Definition

File: `/impl/claude/models/onboarding.py`

```python
class OnboardingSession(TimestampMixin, Base):
    """Onboarding session for Genesis FTUE flow."""

    __tablename__ = "onboarding_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    current_step: Mapped[str] = mapped_column(String(32), default="started", nullable=False)
    completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_kblock_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_declaration: Mapped[str | None] = mapped_column(Text, nullable=True)
```

**Key Features**:
- `TimestampMixin`: Automatic `created_at` and `updated_at` timestamps
- `nullable=True` for optional fields (user_id, completed_at, etc.)
- `String(64)` for UUIDs and IDs
- `Text` for long-form user input (first_declaration)

### 2. API Migration

File: `/impl/claude/protocols/api/onboarding.py`

**Before** (in-memory):
```python
_sessions: dict[str, dict[str, Any]] = {}

@router.post("/start")
async def start_onboarding(request: OnboardingStartRequest):
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "user_id": request.user_id,
        "started_at": datetime.utcnow(),
        "completed": False,
    }
    return OnboardingStartResponse(...)
```

**After** (persistent):
```python
@router.post("/start")
async def start_onboarding(request: OnboardingStartRequest):
    from models import OnboardingSession
    from models.base import get_async_session

    session = OnboardingSession(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        current_step="started",
        completed=False,
    )

    async with get_async_session() as db:
        db.add(session)
        await db.commit()

    return OnboardingStartResponse(...)
```

### 3. Cleanup Mechanism

**Endpoint**: `POST /api/onboarding/cleanup?hours=24`

Removes abandoned sessions older than 24 hours that haven't completed:

```python
@router.post("/cleanup")
async def cleanup_old_sessions(hours: int = 24):
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    async with get_async_session() as db:
        result = await db.execute(
            delete(OnboardingSession).where(
                OnboardingSession.completed == False,
                OnboardingSession.created_at < cutoff_time,
            )
        )
        await db.commit()
        return {"deleted_count": result.rowcount}
```

**SQL Function** (alternative):
```sql
SELECT cleanup_onboarding_sessions(24);  -- Deletes sessions >24h old
```

---

## Migration Path

### Database Table Creation

File: `/impl/claude/system/migrations/002_onboarding_sessions.sql`

Run manually or via `init_db()`:

```sql
CREATE TABLE onboarding_sessions (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64),
    current_step VARCHAR(32) NOT NULL DEFAULT 'started',
    completed BOOLEAN NOT NULL DEFAULT false,
    completed_at TIMESTAMP WITH TIME ZONE,
    first_kblock_id VARCHAR(64),
    first_declaration TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_onboarding_sessions_user_id ON onboarding_sessions(user_id);
CREATE INDEX idx_onboarding_sessions_cleanup ON onboarding_sessions(created_at) WHERE NOT completed;
```

### Deployment

1. **Development**: Table created automatically via `init_db()`
2. **Production**: Run migration SQL before deploying new code
3. **Rollback**: Old code will ignore the new table (safe)

---

## Testing

File: `/impl/claude/protocols/api/_tests/test_onboarding_persistence.py`

```bash
cd impl/claude
uv run pytest protocols/api/_tests/test_onboarding_persistence.py -v
```

**Test Coverage**:
- ✓ Session creation and retrieval
- ✓ Session update with first declaration
- ✓ Cleanup of old abandoned sessions
- ✓ Query for completed sessions

**Results**: 4 passed (all tests green)

---

## Session Lifecycle

```
1. User visits /onboarding
   → POST /api/onboarding/start
   → OnboardingSession created (current_step="started")

2. User enters first declaration
   → POST /api/onboarding/first-declaration
   → Session updated:
     - first_declaration = user input
     - first_kblock_id = created K-Block ID
     - current_step = "first_declaration"
     - completed = true
     - completed_at = now()

3. User enters main studio
   → POST /api/onboarding/complete
   → Session marked complete:
     - current_step = "completed"
     - completed = true
     - completed_at = now()

4. Cleanup (automatic, periodic)
   → POST /api/onboarding/cleanup
   → Old incomplete sessions deleted (>24h)
```

---

## Benefits

1. **Persistence**: Sessions survive server restarts
2. **Auditability**: Can track onboarding completion rates
3. **Cleanup**: Automatic removal of abandoned sessions
4. **History**: Preserves `first_declaration` for user journey tracking
5. **Multi-user**: `user_id` field ready for future multi-tenancy

---

## Future Enhancements

- [ ] Add `cleanup_onboarding_sessions()` to scheduled cron job
- [ ] Track onboarding analytics (completion rate, drop-off points)
- [ ] Add `onboarding_completed_at` to user profile
- [ ] Support resuming incomplete sessions from status endpoint

---

## References

- Model: `/impl/claude/models/onboarding.py`
- API: `/impl/claude/protocols/api/onboarding.py`
- Migration: `/impl/claude/system/migrations/002_onboarding_sessions.sql`
- Tests: `/impl/claude/protocols/api/_tests/test_onboarding_persistence.py`
- Spec: `plans/zero-seed-genesis-grand-strategy.md` §6.2 (FTUE)
