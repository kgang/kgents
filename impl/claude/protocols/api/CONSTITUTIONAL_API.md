# Constitutional API Implementation

## Overview

The Constitutional API provides REST endpoints for Phase 1 Witness constitutional enforcement. It exposes constitutional health metrics, alignment history, and real-time constitutional evaluation events.

**Philosophy**: "Trust is earned through demonstrated alignment." — Article V: Trust Accumulation

## Endpoints

### 1. GET /api/witness/constitutional/{agent_id}

Get constitutional health for an agent.

**Response Model**: `ConstitutionalHealthResponse`

```json
{
  "agent_id": "claude",
  "trust_level": "BOUNDED",
  "trust_level_value": 1,
  "total_marks_analyzed": 150,
  "average_alignment": 0.75,
  "violation_rate": 0.08,
  "trust_capital": 0.3,
  "principle_averages": {
    "ETHICAL": 0.85,
    "COMPOSABLE": 0.72,
    "JOY_INDUCING": 0.68,
    "TASTEFUL": 0.78,
    "CURATED": 0.71,
    "HETERARCHICAL": 0.75,
    "GENERATIVE": 0.73
  },
  "dominant_principles": ["ETHICAL", "TASTEFUL", "HETERARCHICAL"],
  "reasoning": "Meets L1 criteria. For L2: alignment needs 0.05 more; violations need to drop below 5%; capital needs 0.20 more",
  "recommendations": [
    "Improve average alignment from 0.75 to 0.9+ for L3",
    "Reduce violation rate from 8.0% to <1% for L3",
    "Accumulate 0.70 more trust capital for L3"
  ]
}
```

**Usage**:
```typescript
const response = await fetch('/api/witness/constitutional/claude');
const health = await response.json();
console.log(`Trust level: ${health.trust_level}`);
```

### 2. GET /api/witness/constitutional/{agent_id}/history

Get constitutional alignment history for an agent.

**Query Parameters**:
- `days`: Number of days to retrieve (1-90, default 7)
- `limit`: Maximum trajectory points (1-500, default 100)

**Response Model**: `ConstitutionalHistoryResponse`

```json
{
  "agent_id": "claude",
  "days": 7,
  "trajectory": [
    {
      "timestamp": "2025-12-25T10:30:00Z",
      "alignment": 0.82,
      "crystal_id": "mark-abc123",
      "level": "MARK"
    },
    {
      "timestamp": "2025-12-25T11:15:00Z",
      "alignment": 0.78,
      "crystal_id": "mark-def456",
      "level": "MARK"
    }
  ],
  "crystals": [
    {
      "id": "session-claude-1735125000",
      "level": "SESSION",
      "insight": "150 marks analyzed",
      "constitutional_meta": {
        "dominant_principles": ["ETHICAL", "TASTEFUL", "HETERARCHICAL"],
        "alignment_trajectory": [0.82, 0.78, 0.85, 0.72],
        "average_alignment": 0.75,
        "violations_count": 12,
        "trust_earned": 0.3,
        "principle_trends": {
          "ETHICAL": 0.85,
          "COMPOSABLE": 0.72
        }
      }
    }
  ],
  "total_marks": 150,
  "total_violations": 12,
  "average_alignment": 0.75
}
```

**Usage**:
```typescript
// Get last 7 days
const response = await fetch('/api/witness/constitutional/claude/history?days=7');
const history = await response.json();

// Render sparkline
const sparkline = history.trajectory.map(p => p.alignment);
```

### 3. GET /api/witness/constitutional/stream

SSE stream for constitutional events.

**Event Types**:
- `constitutional_evaluated`: New mark with constitutional alignment
- `heartbeat`: Keepalive event (every 30s)
- `connected`: Initial connection event
- `disconnected`: Stream closed

**Event Format**:
```
event: constitutional_evaluated
data: {"type":"constitutional_evaluated","mark_id":"mark-abc123","alignment":0.82,"principles":["ETHICAL","COMPOSABLE"]}

event: heartbeat
data: {"type":"heartbeat","time":"2025-12-25T10:30:00Z"}
```

**Usage**:
```typescript
const eventSource = new EventSource('/api/witness/constitutional/stream');

eventSource.addEventListener('constitutional_evaluated', (e) => {
  const data = JSON.parse(e.data);
  console.log(`New evaluation: ${data.alignment}`);
  // Update dashboard
});

eventSource.addEventListener('heartbeat', (e) => {
  console.log('Stream alive');
});
```

## Integration

### Backend Services

The Constitutional API integrates with:

1. **ConstitutionalTrustComputer** (`services/witness/trust/constitutional_trust.py`)
   - Computes trust levels from constitutional history
   - Applies escalation criteria (L0→L1→L2→L3)

2. **ConstitutionalCrystalMeta** (`services/witness/crystal.py`)
   - Aggregates constitutional metadata during compression
   - Preserves alignment trends through hierarchy

3. **WitnessSynergyBus** (`services/witness/bus.py`)
   - Publishes `CONSTITUTIONAL_EVALUATED` events
   - Enables real-time streaming to frontend

### Frontend Integration

Example React hook for constitutional dashboard:

```typescript
import { useEffect, useState } from 'react';

interface ConstitutionalHealth {
  trust_level: string;
  average_alignment: number;
  violation_rate: number;
  // ... other fields
}

export function useConstitutionalHealth(agentId: string) {
  const [health, setHealth] = useState<ConstitutionalHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHealth() {
      const response = await fetch(`/api/witness/constitutional/${agentId}`);
      const data = await response.json();
      setHealth(data);
      setLoading(false);
    }
    fetchHealth();
  }, [agentId]);

  return { health, loading };
}
```

## Event Bus Topics

New topics added to `WitnessTopics`:

```python
# Constitutional events (Phase 1: Constitutional Enforcement)
CONSTITUTIONAL_EVALUATED = "witness.constitutional.evaluated"

# Wildcard
CONSTITUTIONAL_ALL = "witness.constitutional.*"
```

## Files Modified

1. **CREATE**: `protocols/api/constitutional.py`
   - Router factory with 3 endpoints
   - Pydantic models for request/response
   - SSE streaming for real-time events

2. **MODIFY**: `services/witness/bus.py`
   - Added `CONSTITUTIONAL_EVALUATED` topic
   - Added `CONSTITUTIONAL_ALL` wildcard

3. **MODIFY**: `protocols/api/app.py`
   - Registered constitutional router
   - Mounted at `/api/witness/constitutional`

## Trust Level Criteria

The trust level computation uses these thresholds:

| Level | Name | Criteria |
|-------|------|----------|
| L0 | READ_ONLY | Default, no history |
| L1 | BOUNDED | avg_alignment ≥ 0.6, violation_rate < 10% |
| L2 | SUGGESTION | avg_alignment ≥ 0.8, violation_rate < 5%, trust_capital ≥ 0.5 |
| L3 | AUTONOMOUS | avg_alignment ≥ 0.9, violation_rate < 1%, trust_capital ≥ 1.0 |

**Trust Capital**: Accumulated from high-alignment marks (+0.02 per mark with alignment > 0.8)

## Design Patterns

### 1. Router Factory Pattern

```python
def create_constitutional_router() -> "APIRouter | None":
    """Create router, returns None if FastAPI not installed."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/witness/constitutional", tags=["witness"])
    # ... define endpoints
    return router
```

### 2. SSE Streaming Pattern

```python
async def generate() -> AsyncGenerator[str, None]:
    bus = get_synergy_bus()
    event_queue: asyncio.Queue[tuple[str, Any]] = asyncio.Queue()

    async def on_event(topic: str, event: Any) -> None:
        await event_queue.put((topic, event))

    unsub = bus.subscribe(WitnessTopics.MARK_CREATED, on_event)

    try:
        while True:
            topic, event = await asyncio.wait_for(event_queue.get(), timeout=30.0)
            yield f"event: {event_type}\ndata: {json.dumps(event)}\n\n"
    finally:
        unsub()
```

### 3. Graceful Degradation

All Pydantic models handle missing FastAPI:

```python
try:
    from pydantic import BaseModel, Field
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    BaseModel = object  # type: ignore
    Field = lambda *args, **kwargs: None  # type: ignore
```

## Testing

See `protocols/api/_tests/test_constitutional.py` for:
- Router creation tests
- Model validation tests
- Bus topic registration tests
- App router registration tests

## Future Enhancements

1. **ConstitutionalAdvisor**: Generate personalized recommendations
2. **Crystal Querying**: Implement `persistence.get_crystals(since=...)` for real crystal data
3. **WebSocket Support**: Add `/ws/constitutional/{agent_id}` for bidirectional updates
4. **Historical Trends**: Add `/api/witness/constitutional/{agent_id}/trends` for long-term analysis
5. **Comparative Analysis**: Add `/api/witness/constitutional/compare` to compare multiple agents

## References

- [CONSTITUTION.md](../../../../spec/principles/CONSTITUTION.md) - Article V: Trust Accumulation
- [constitutional_trust.py](../../services/witness/trust/constitutional_trust.py) - Trust computation
- [crystal.py](../../services/witness/crystal.py) - ConstitutionalCrystalMeta
- [witness.py](./witness.py) - Existing witness API pattern
