# Agent Town Track B: Instrumentation Spine - Implementation Summary

**Status**: COMPLETE
**Date**: 2025-12-15
**Tests Passing**: 39/39 (100%)

---

## Mission

Build the instrumentation infrastructure for metrics and tracing to enable:
- Unit economics validation
- Revenue tracking
- SLO enforcement
- Ethics monitoring

**Key Principle**: "Margin before magic. Safety before speed. Instrument before monetize."

---

## Implementation

### 1. Core Infrastructure

**File**: `/Users/kentgang/git/kgents/impl/claude/protocols/api/action_metrics.py`

#### ActionMetric Dataclass
```python
@dataclass
class ActionMetric:
    action_type: str         # lod3, lod4, lod5, branch, inhabit, force, dialogue
    user_id: str
    town_id: str
    citizen_id: str | None
    tokens_in: int
    tokens_out: int
    model: str               # haiku, sonnet, opus, template, cached
    latency_ms: int
    credits_charged: int
    timestamp: datetime
    metadata: dict[str, Any]
```

**Properties**:
- `total_tokens`: Sum of input + output tokens
- `estimated_cost_usd`: Raw cost based on model pricing
- `revenue_usd`: Revenue from credits charged
- `gross_margin`: (revenue - cost) / revenue

**Methods**:
- `to_otel_span()`: Export as OpenTelemetry span attributes
- `to_dict()`: Export as JSON for storage/dashboard

#### MetricsStore
In-memory store with query and aggregation capabilities:
- `emit(metric)`: Store a metric
- `query(**filters)`: Query with user_id/town_id/action_type/since filters
- `aggregate(**filters)`: Compute aggregates (count, avg, p50, p95, by_model)

#### @instrument_action Decorator
Automatic instrumentation for async/sync functions:
```python
@instrument_action("lod3", model="haiku", credits_charged=10)
async def query_citizen_memory(citizen_id: str) -> dict:
    # Implementation
    return {"tokens_in": 100, "tokens_out": 50}
```

Captures:
- Execution time (latency_ms)
- Tokens from result
- Error handling (no charge on errors)
- OTEL span creation

#### OTEL Integration
- `setup_otel_tracing()`: Configure OpenTelemetry
- `get_tracer()`: Get tracer for span creation
- Console export for local debugging
- Ready for production collector integration

---

### 2. Integration Points

#### Town API Endpoints

**LOD Queries** (`/v1/town/{town_id}/citizen/{name}`):
- Emit metrics for LOD 3-5 queries
- Track latency of manifest() calls
- Model = "template" (no LLM)
- Credits: LOD3=10, LOD4=100, LOD5=400

**Metrics Query** (`/v1/town/{town_id}/metrics`):
- Dashboard query endpoint
- Filters: action_type, time_window
- Returns: count, tokens, credits, latency, margin, by_model

#### Dialogue Engine
File: `/Users/kentgang/git/kgents/impl/claude/agents/town/dialogue_engine.py`

Emits metrics after LLM generation:
- Tracks dialogue tokens by model (haiku/sonnet/template)
- Records speaker/listener/operation metadata
- Zero credits (part of INHABIT session cost)

#### Town Flux
File: `/Users/kentgang/git/kgents/impl/claude/agents/town/flux.py`

Emits metrics for all flux operations:
- greet, gossip, trade, solo
- Tracks dialogue tokens when engine enabled
- System user (not billable)
- Includes phase/participants metadata

---

### 3. Unit Economics Validation

**Model Costs** (from unified-v2.md §1):
```python
MODEL_COSTS_PER_1M = {
    ModelName.HAIKU: (0.25, 1.25),    # (input, output) per 1M tokens
    ModelName.SONNET: (3.00, 15.00),
    ModelName.OPUS: (15.00, 75.00),
}
```

**Credit Costs**:
```python
ACTION_CREDITS = {
    ActionType.LOD3: 10,      # Haiku - high margin
    ActionType.LOD4: 100,     # Sonnet - 30-70% margin
    ActionType.LOD5: 400,     # Opus - 0-73% margin
    ActionType.BRANCH: 150,   # State storage
    ActionType.INHABIT: 100,  # Per 10 minutes
    ActionType.FORCE: 50,     # Ethics premium
}
```

**Revenue Calculation**:
- Conservative: $0.006/credit (Adventurer tier)
- Used for margin calculations
- Actual revenue varies by user tier

---

### 4. Dashboard Queries

Example queries enabled:

**Q**: "What was the average LOD3 latency today?"
```python
store.aggregate(
    action_type="lod3",
    since=datetime.today()
)
# Returns: avg_latency_ms, p50, p95
```

**Q**: "What's the gross margin for LOD4 this week?"
```python
store.aggregate(
    action_type="lod4",
    since=datetime.now() - timedelta(days=7)
)
# Returns: total_cost_usd, total_revenue_usd, avg_margin
```

**Q**: "Which model is being used most?"
```python
agg = store.aggregate(town_id="xyz")
# Returns: by_model breakdown with counts
```

---

### 5. Test Coverage

**File**: `/Users/kentgang/git/kgents/impl/claude/protocols/api/_tests/test_action_metrics.py`
- 33 tests covering all ActionMetric functionality
- MetricsStore query/aggregation
- Decorator async/sync
- Error handling
- Constants validation
- Dashboard use cases
- SLO tracking
- Ethics monitoring

**File**: `/Users/kentgang/git/kgents/impl/claude/protocols/api/_tests/test_metrics_integration.py`
- 6 integration tests
- LOD query emission
- Flux operations
- Unit economics validation
- OTEL span export

**Total**: 39/39 tests passing (100%)

---

## Exit Criteria Status

| Criterion | Status | Evidence |
|-----------|--------|----------|
| ActionMetric captures type/tokens/model/latency/credits | ✅ COMPLETE | action_metrics.py:115-153 |
| @instrument_action works on async functions | ✅ COMPLETE | action_metrics.py:437-538 |
| Every LLM call emits metric | ✅ COMPLETE | dialogue_engine.py:476-498, flux.py:174-210 |
| OTEL spans exported | ✅ COMPLETE | action_metrics.py:381-417 |
| 30+ tests passing | ✅ COMPLETE | 39 tests (33 + 6) |
| Can query "average LOD3 latency today" | ✅ COMPLETE | test_action_metrics.py:783-814 |

---

## Non-Goals Deferred

| Item | Reason | When to Revisit |
|------|--------|-----------------|
| Grafana/dashboard UI | Focus on API first | Post-launch |
| Billing integration | Track C dependency | Next phase |
| Alert rules | Need production data | Post-launch |
| TimescaleDB/ClickHouse | In-memory sufficient for MVP | Scale milestone |
| OTEL collector config | Console export for dev | Production deployment |

---

## Key Files

### Core Infrastructure
- `impl/claude/protocols/api/action_metrics.py` (650 lines)
- `impl/claude/protocols/api/_tests/test_action_metrics.py` (925 lines)
- `impl/claude/protocols/api/_tests/test_metrics_integration.py` (200 lines)

### Integration Points
- `impl/claude/protocols/api/town.py` (metrics endpoint added)
- `impl/claude/agents/town/dialogue_engine.py` (metrics emission)
- `impl/claude/agents/town/flux.py` (flux operation metrics)

---

## Next Steps (Track C)

With instrumentation complete, Track C can proceed with:

1. **BudgetStore** - Credit balance tracking
2. **Paywall** - LOD 3-5 upgrade enforcement
3. **Stripe Integration** - Payment processing
4. **Kill-switch** - CAC/churn thresholds

The metrics infrastructure is now ready to validate business hypotheses.

---

## Example Usage

### Dashboard Query
```bash
curl http://localhost:8000/v1/town/abc123/metrics?action_type=lod3&since_hours=24
```

```json
{
  "town_id": "abc123",
  "action_type": "lod3",
  "time_window_hours": 24,
  "metrics": {
    "count": 150,
    "total_tokens": 22500,
    "total_credits": 1500,
    "avg_latency_ms": 125.3,
    "p50_latency_ms": 120,
    "p95_latency_ms": 180,
    "avg_margin": 0.95,
    "by_model": {
      "haiku": {
        "count": 150,
        "total_tokens": 22500,
        "avg_latency_ms": 125.3
      }
    }
  }
}
```

### Manual Emission
```python
from protocols.api.action_metrics import emit_action_metric

metric = emit_action_metric(
    action_type="lod4",
    user_id="user-123",
    town_id="town-456",
    citizen_id="citizen-789",
    tokens_in=500,
    tokens_out=300,
    model="sonnet",
    latency_ms=1000,
    credits_charged=100,
)

print(f"Cost: ${metric.estimated_cost_usd:.6f}")
print(f"Revenue: ${metric.revenue_usd:.2f}")
print(f"Margin: {metric.gross_margin:.1%}")
```

---

*"Without metrics, we cannot validate business hypotheses. Track B provides the foundation for Track C (monetization) and data-driven decision making."*
