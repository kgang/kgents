# Feed Feedback Persistence Implementation

**Status**: ✅ Complete
**Priority**: P2 (Medium)
**Date**: 2025-12-25

## Overview

Added persistent storage for feed user interactions to enable the ranking algorithm to improve over time through learning from user behavior.

## What Was Implemented

### 1. Database Schema (`models/feed_feedback.py`)

Two tables for tracking feed interactions:

#### `feed_interactions` Table
Append-only log of every user interaction with K-Blocks:

```sql
CREATE TABLE feed_interactions (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    kblock_id VARCHAR(64) NOT NULL,
    action VARCHAR(32) NOT NULL,  -- view, engage, dismiss, contradict
    dwell_time_ms INTEGER,         -- Time spent viewing (milliseconds)
    interaction_type VARCHAR(64),   -- Specific action: edit, comment, link, copy
    interaction_metadata TEXT,      -- JSON metadata
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Indexes for common queries
CREATE INDEX idx_user_kblock ON feed_interactions(user_id, kblock_id);
CREATE INDEX idx_user_timestamp ON feed_interactions(user_id, created_at);
CREATE INDEX idx_kblock_action ON feed_interactions(kblock_id, action);
CREATE INDEX idx_timestamp ON feed_interactions(created_at);
```

#### `feed_engagement_stats` Table
Pre-computed aggregate statistics per K-Block (updated incrementally):

```sql
CREATE TABLE feed_engagement_stats (
    kblock_id VARCHAR(64) PRIMARY KEY,
    view_count INTEGER DEFAULT 0,
    engage_count INTEGER DEFAULT 0,
    dismiss_count INTEGER DEFAULT 0,
    attention_score FLOAT DEFAULT 0.0,  -- Computed: (engagements*2 + views*0.5 - dismissals) / (total+1)
    last_viewed_at TIMESTAMP,
    last_engaged_at TIMESTAMP,
    avg_dwell_time_sec FLOAT,
    unique_viewers INTEGER DEFAULT 0,
    unique_engagers INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_attention_score ON feed_engagement_stats(attention_score);
CREATE INDEX idx_last_engaged ON feed_engagement_stats(last_engaged_at);
```

### 2. Persistence Layer (`services/feed/persistence.py`)

**Class**: `FeedFeedbackPersistence`

Provides async CRUD operations for feed feedback:

```python
async def record_interaction(
    user_id: str,
    kblock_id: str,
    action: FeedbackAction,
    dwell_time_ms: int | None = None,
    interaction_type: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> str
```

- Records interaction to `feed_interactions` table
- Updates aggregate stats in `feed_engagement_stats` table (upsert)
- Recomputes attention score incrementally
- Returns interaction ID

```python
async def get_attention_score(user_id: str, kblock_id: str) -> float
```

- Retrieves pre-computed attention score (0.0 to 1.0)
- Formula: `(engagements * 2 + views * 0.5 - dismissals) / (total + 1)`
- Normalized to [0, 1] range

```python
async def get_analytics(limit: int = 20, min_interactions: int = 1) -> dict
```

- Returns feed engagement analytics:
  - Most engaged K-Blocks (top N by attention score)
  - Total interaction counts (views, engagements, dismissals)
  - Average dwell time
  - Recent activity (24-hour window)

### 3. Updated AttentionTracker (`services/feed/feedback.py`)

Added three implementations:

1. **`AttentionTrackerProtocol`**: Interface for attention tracking
2. **`InMemoryAttentionTracker`**: Original in-memory MVP (backward compatible)
3. **`PersistentAttentionTracker`**: New database-backed implementation

```python
class PersistentAttentionTracker:
    """
    Database-backed attention tracking.

    Persists all interactions to PostgreSQL for:
    - Cross-session tracking
    - Analytics
    - ML training data
    """

    def __init__(self, persistence: FeedFeedbackPersistence): ...

    async def record_view(self, user_id: str, kblock_id: str) -> None
    async def record_engagement(self, user_id: str, kblock_id: str) -> None
    async def record_dismissal(self, user_id: str, kblock_id: str) -> None
    async def get_attention_score(self, user_id: str, kblock_id: str) -> float
    async def get_stats(self, user_id: str, kblock_id: str) -> dict[str, int]
```

### 4. REST API Endpoints (`protocols/api/feed.py`)

**Router**: `create_feed_router()` mounted at `/api/feed`

#### POST `/api/feed/feedback/record`
Record user interaction with a K-Block.

**Request**:
```json
{
  "user_id": "user_123",
  "kblock_id": "kb_abc",
  "action": "view",  // view | engage | dismiss | contradict
  "dwell_time_ms": 5000,  // Optional
  "interaction_type": "edit",  // Optional: edit, comment, link, copy
  "metadata": {}  // Optional: additional context
}
```

**Response**:
```json
{
  "success": true,
  "interaction_id": "uuid"
}
```

#### GET `/api/feed/analytics`
Get feed engagement analytics.

**Query Parameters**:
- `limit`: Maximum K-Blocks to return (default: 20, max: 100)
- `min_interactions`: Minimum interactions to include (default: 1)

**Response**:
```json
{
  "most_engaged_kblocks": [
    {
      "kblock_id": "kb_abc",
      "attention_score": 0.85,
      "view_count": 42,
      "engage_count": 15,
      "dismiss_count": 2,
      "last_engaged_at": "2025-12-25T10:30:00Z"
    }
  ],
  "totals": {
    "views": 1234,
    "engagements": 456,
    "dismissals": 23,
    "avg_dwell_time_sec": 12.5
  },
  "recent_activity": {
    "interactions_24h": 89
  }
}
```

#### GET `/api/feed/cosmos`
Get all K-Blocks (existing endpoint, included for completeness).

**Query Parameters**:
- `user_id`: User identifier (default: "guest")
- `offset`: Pagination offset (default: 0)
- `limit`: Max items (default: 20, max: 100)
- `ranking`: Ranking strategy (default: "chronological")

#### GET `/api/feed/coherent`
Get low-loss K-Blocks (existing endpoint, included for completeness).

**Query Parameters**:
- `user_id`: User identifier (default: "guest")
- `offset`: Pagination offset (default: 0)
- `limit`: Max items (default: 20, max: 100)
- `max_loss`: Maximum Galois loss threshold (default: 0.2)

### 5. Dependency Injection (`services/providers.py`)

Added provider function for DI:

```python
async def get_feed_feedback_persistence() -> FeedFeedbackPersistence:
    """Get the FeedFeedbackPersistence for user interaction tracking."""
    session_factory = await get_session_factory()
    return FeedFeedbackPersistence(session_factory=session_factory)
```

Registered in `setup_providers()`:
```python
container.register("feed_feedback_persistence", get_feed_feedback_persistence, singleton=True)
```

## Architecture

### Storage Pattern

```
┌──────────────────┐
│  User Action     │  (view, engage, dismiss)
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  FeedFeedbackPersistence             │
│  ├─ record_interaction()             │
│  │  ├─ INSERT INTO feed_interactions │
│  │  └─ UPDATE feed_engagement_stats  │  (upsert + recompute score)
│  ├─ get_attention_score()            │
│  └─ get_analytics()                  │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  PostgreSQL (via SQLAlchemy async)   │
│  ├─ feed_interactions (append-only)  │
│  └─ feed_engagement_stats (upsert)   │
└──────────────────────────────────────┘
```

### Data Flow

1. **Recording Interaction**:
   - User interacts with K-Block in feed
   - Frontend calls `POST /api/feed/feedback/record`
   - Persistence layer:
     - Inserts row into `feed_interactions`
     - Updates/inserts `feed_engagement_stats` (upsert)
     - Recomputes `attention_score` incrementally
   - Returns interaction ID

2. **Retrieving Analytics**:
   - Frontend calls `GET /api/feed/analytics`
   - Persistence queries pre-computed stats
   - Returns aggregated metrics (fast read)

3. **Ranking Algorithm**:
   - Feed service queries `feed_engagement_stats`
   - Uses `attention_score` as ranking signal
   - Combines with principles, recency, coherence

## Performance Characteristics

### Writes
- **Append-only log**: Fast inserts to `feed_interactions`
- **Incremental updates**: O(1) upsert to `feed_engagement_stats`
- **Score recomputation**: O(1) update (not re-aggregating all rows)

### Reads
- **Attention scores**: O(1) lookup (pre-computed)
- **Analytics**: O(log N) with indexes
- **Top K-Blocks**: O(K log N) with index on `attention_score`

### Indexes
All common query patterns are indexed:
- User-specific interactions: `(user_id, kblock_id)`
- Temporal queries: `(user_id, created_at)`
- K-Block metrics: `(kblock_id, action)`
- Top engaged: `(attention_score DESC)`

## Testing

Tests created in `services/feed/_tests/test_feedback_persistence.py`:

- ✅ `test_record_view_interaction`: Records view and updates stats
- ✅ `test_record_engage_interaction`: Records engagement
- ✅ `test_attention_score_computation`: Validates score formula
- ✅ `test_dismiss_lowers_score`: Dismissals reduce attention
- ✅ `test_analytics`: Analytics endpoint returns correct data

**Note**: Tests require database migrations to be run first.

## Migration Required

To use this feature, run database migration to create tables:

```bash
cd impl/claude
alembic revision --autogenerate -m "Add feed feedback tables"
alembic upgrade head
```

Or manually create tables:
```bash
# Import models to register tables
uv run python -c "from models import FeedInteraction, FeedEngagementStats; from models.base import init_db; import asyncio; asyncio.run(init_db())"
```

## Usage Examples

### Recording Feedback (Frontend)

```typescript
// User views a K-Block
await fetch('/api/feed/feedback/record', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: currentUser.id,
    kblock_id: kblock.id,
    action: 'view',
    dwell_time_ms: Date.now() - viewStartTime
  })
});

// User edits a K-Block
await fetch('/api/feed/feedback/record', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: currentUser.id,
    kblock_id: kblock.id,
    action: 'engage',
    interaction_type: 'edit'
  })
});
```

### Getting Analytics (Dashboard)

```typescript
const analytics = await fetch('/api/feed/analytics?limit=50&min_interactions=5')
  .then(r => r.json());

console.log('Most engaged K-Blocks:', analytics.most_engaged_kblocks);
console.log('Total views:', analytics.totals.views);
console.log('Avg dwell time:', analytics.totals.avg_dwell_time_sec);
```

### Using Persistent Tracker (Backend)

```python
from services.providers import get_feed_feedback_persistence
from services.feed.feedback import PersistentAttentionTracker, FeedbackAction

# Get persistence layer
persistence = await get_feed_feedback_persistence()

# Create persistent tracker
tracker = PersistentAttentionTracker(persistence)

# Record interactions
await tracker.record_view("user_123", "kb_abc")
await tracker.record_engagement("user_123", "kb_abc")

# Get attention score
score = await tracker.get_attention_score("user_123", "kb_abc")
print(f"Attention score: {score}")  # 0.0 to 1.0
```

## Future Enhancements

### Phase 1 (Current)
- ✅ Record all interactions
- ✅ Compute attention scores
- ✅ Basic analytics

### Phase 2 (Next)
- [ ] Per-user personalization (currently global scores)
- [ ] Temporal decay (recent interactions weighted higher)
- [ ] A/B testing framework for ranking algorithms

### Phase 3 (Future)
- [ ] ML model training on interaction logs
- [ ] Collaborative filtering (users with similar tastes)
- [ ] Anomaly detection (spam, bots)

## Related Files

- `models/feed_feedback.py` - Database schema
- `services/feed/persistence.py` - Persistence layer
- `services/feed/feedback.py` - AttentionTracker implementations
- `protocols/api/feed.py` - REST API endpoints
- `services/providers.py` - Dependency injection
- `services/feed/_tests/test_feedback_persistence.py` - Tests

## References

- Original request: "Add feed feedback persistence (P2)"
- Feed ranking algorithm: `services/feed/ranking.py`
- Feed service: `services/feed/service.py`
- Zero Seed Grand Strategy: `plans/zero-seed-genesis-grand-strategy.md` (Part IV)
