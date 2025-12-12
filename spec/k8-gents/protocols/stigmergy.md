# Stigmergy Protocol Specification

**AGENTESE Handle**: `void.pheromone`, `void.stigmergy`

## Overview

Stigmergy is indirect coordination through environmental modification. In K8-Gents, agents coordinate by emitting and sensing pheromones - never by direct message passing.

## Two Stigmergy Stores

K8-Terrarium v2.0 provides two complementary stores:

### 1. Pheromone CRDs (Passive Stigmergy)

**When to use**: Cross-session signals, important alerts, narrative threads

```yaml
apiVersion: kgents.io/v1
kind: Pheromone
metadata:
  name: warning-low-memory
spec:
  type: WARNING
  source: resource-monitor
  initialIntensity: 0.9
  halfLifeMinutes: 30
  payload: |
    {"resource": "memory", "threshold": "80%"}
```

Characteristics:
- **Durable**: Survives pod restarts
- **Slow decay**: Half-life measured in minutes
- **Low frequency**: Dozens per minute max
- **Passive**: Intensity calculated on read

### 2. Stigmergy Store (Ephemeral)

**When to use**: Real-time coordination, attention signals, ephemeral state

```python
from infra.stigmergy import StigmergyStore, EphemeralPheromone

store = await create_stigmergy_store()
await store.emit(EphemeralPheromone(
    type="ATTENTION",
    source="agent-a",
    target="agent-b",
    intensity=0.8,
    payload={"message": "look here"},
    emitted_at=datetime.utcnow(),
    ttl_seconds=60,
))
```

Characteristics:
- **Ephemeral**: Auto-expires via TTL
- **Fast**: Hundreds per second possible
- **Redis-backed**: Or in-memory fallback
- **High frequency**: Real-time coordination

## Passive vs Active Stigmergy

| Aspect | Active (OLD) | Passive (v2.0) |
|--------|--------------|----------------|
| Intensity storage | `status.current_intensity` | Calculated on read |
| Operator writes | Every decay cycle | DELETE only |
| etcd load | O(pheromones * frequency) | O(deletions) |
| Scalability | Poor | Good |

### Active Stigmergy (DEPRECATED)

The operator updated `status.current_intensity` every minute:

```python
# BAD: etcd write storm
@kopf.timer('pheromones', interval=60.0)
async def decay_pheromones(patch, **_):
    patch.status['current_intensity'] = calculate_decay(...)  # WRITE
```

### Passive Stigmergy (v2.0)

Intensity calculated on read, operator only deletes:

```python
# GOOD: no unnecessary writes
def calculate_intensity(spec: dict) -> float:
    """Pure function - NO WRITES"""
    elapsed = (now - emitted_at).total_seconds() / 60
    return initial * (0.5 ** (elapsed / half_life))

@kopf.timer('pheromones', interval=300.0)  # 5 min, not 60s
async def garbage_collect(spec, **_):
    if calculate_intensity(spec) < 0.01:
        api.delete(...)  # Only DELETE, never UPDATE
```

## Decay Function

The exponential decay formula:

```
intensity(t) = initialIntensity × 0.5^((t - emittedAt) / halfLifeMinutes)
```

| Half-Life | After 10 min | After 30 min | After 60 min |
|-----------|--------------|--------------|--------------|
| 5 min | 0.25 | 0.016 | 0.0002 |
| 10 min | 0.50 | 0.125 | 0.016 |
| 30 min | 0.79 | 0.50 | 0.25 |

## Pheromone Lifecycle

```
┌──────────┐    emit     ┌──────────┐   decay    ┌─────────────┐   GC    ┌────────────┐
│  Agent   │ ─────────▶  │  ACTIVE  │ ────────▶  │ EVAPORATING │ ─────▶ │ EVAPORATED │
└──────────┘             └──────────┘            └─────────────┘        └────────────┘
                              │                        │
                              │    sense               │
                              ▼                        ▼
                         ┌──────────┐           ┌──────────┐
                         │  Agent   │           │  Agent   │
                         └──────────┘           └──────────┘
```

1. **Emit**: Agent creates pheromone with `emittedAt` timestamp
2. **Active**: Pheromone sensible with full intensity
3. **Evaporating**: Intensity decaying but still sensible
4. **GC**: Operator deletes when intensity < 0.01

## Best Practices

### DO

- Use pheromones for coordination, not direct messaging
- Let pheromones decay naturally (don't manually delete)
- Use DREAM type for creative tangents (longer half-life)
- Calculate intensity on read (never trust stored values)

### DON'T

- Store mutable state in pheromone payloads
- Create pheromones faster than they decay
- Use pheromones for synchronous request/response
- Update pheromone intensity manually

## Implementation Trace

| Spec Section | Implementation File | Status |
|--------------|---------------------|--------|
| Passive Stigmergy | `impl/claude/infra/k8s/operators/pheromone_operator.py` | Aligned |
| Decay Function | `impl/claude/infra/k8s/operators/pheromone_operator.py:calculate_intensity` | Aligned |
| Stigmergy Store | `impl/claude/infra/stigmergy/__init__.py` | Aligned |
| MCP Resources | `impl/claude/protocols/cli/mcp/resources.py:_calculate_pheromone_intensity` | Aligned |
