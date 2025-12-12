# Skill: Agent Observability

> Add metrics, mirrors, pheromones, and debugging support to agents.

**Difficulty**: Medium
**Prerequisites**: Understanding of Agent[A, B] protocol, FluxAgent basics
**Files Touched**: `impl/claude/protocols/terrarium/`, `impl/claude/agents/i/`, `impl/claude/agents/flux/`
**References**: `protocols/terrarium/mirror.py`, `agents/i/semantic_field.py`, `agents/flux/metabolism.py`

---

## Overview

kgents has three observability systems that work together:

| System | Purpose | Key Files |
|--------|---------|-----------|
| **Mirror Protocol** | Real-time UI streaming | `protocols/terrarium/mirror.py` |
| **Metabolism** | Resource tracking (entropy, temperature) | `agents/flux/metabolism.py` |
| **SemanticField** | Inter-agent pheromone signaling | `agents/i/semantic_field.py` |

**Key Principle**: "To Observe is to Disturb" (AGENTESE). 50 observers should NOT cost the agent 50x entropy. The Mirror Protocol decouples observation from computation.

---

## Mirror Protocol (Terrarium TUI)

The HolographicBuffer enables fire-and-forget event emission:

```python
from protocols.terrarium.mirror import HolographicBuffer

# Agent side: emit events once
buffer = HolographicBuffer(max_history=100)

async def my_agent_work():
    result = compute_something()

    # Fire and forget - never blocks
    await buffer.reflect({
        "type": "result",
        "agent_id": "my-agent",
        "data": result,
        "timestamp": datetime.now().isoformat(),
    })

# Observer side: attach to buffer
async def websocket_handler(websocket):
    await buffer.attach_mirror(websocket)
    # Late joiners receive history ("The Ghost")
    # All future events broadcast automatically

    # Cleanup when done
    buffer.detach_mirror(websocket)
```

### Design Principles

1. **reflect() is fire-and-forget**: Agent never waits for observers
2. **Broadcast failures don't propagate**: Slow clients are cleaned up automatically
3. **Late joiners receive history**: "The Ghost" provides catch-up
4. **Disconnected observers auto-cleaned**: No manual cleanup needed

### Buffer Properties

```python
buffer.observer_count   # Number of active mirrors
buffer.history_length   # Current history length
buffer.events_reflected # Total events emitted

# REST endpoint support
snapshot = buffer.get_snapshot()  # Get current history without WebSocket
```

---

## Metabolism (Resource Tracking)

FluxMetabolism connects FluxAgents to the MetabolicEngine for entropy tracking:

```python
from agents.flux import Flux, FluxConfig
from agents.flux.metabolism import FluxMetabolism, create_flux_metabolism
from protocols.agentese.metabolism import MetabolicEngine, FeverEvent

# Create metabolism adapter
engine = MetabolicEngine(critical_threshold=0.5)
metabolism = create_flux_metabolism(
    engine=engine,
    input_tokens=50,    # Estimated input tokens per event
    output_tokens=100,  # Estimated output tokens per event
)

# Attach to FluxAgent
flux = Flux.lift(my_agent)
flux.attach_metabolism(metabolism)

# Process events - metabolism tracked automatically
async for result in flux.start(event_stream):
    print(metabolism.status())
    # {
    #   "pressure": 0.35,
    #   "temperature": 0.5,
    #   "in_fever": False,
    #   "events_metabolized": 42,
    #   "fevers_triggered": 0,
    # }
```

### Fever Handling

When metabolic pressure exceeds threshold, fever triggers:

```python
async def on_fever(event: FeverEvent) -> None:
    """Creative interruption - system running hot."""
    print(f"Fever! Intensity: {event.intensity}")
    print(f"Oblique strategy: {event.oblique_strategy}")
    # Take creative action, tithe, or cool down

metabolism = FluxMetabolism(
    engine=engine,
    on_fever=on_fever,  # Callback when fever triggers
)
```

### Voluntary Discharge (Tithe)

```python
# Voluntarily discharge pressure (gratitude pattern)
result = metabolism.tithe(amount=0.1)
# {
#   "discharged": 0.1,
#   "remaining_pressure": 0.25,
#   "gratitude": "The Accursed Share accepts your tithe.",
# }
```

### Key Insight

Two types of entropy:

- **Flux entropy** (J-gent): Per-agent computational budget (local)
- **Metabolic entropy** (void.entropy): System-wide activity pressure (global)

They work together—flux bounds individual computation, metabolism tracks overall "heat".

---

## Metrics Emission (Terrarium)

The MetricsManager emits periodic metabolism events for visualization:

```python
from protocols.terrarium.metrics import MetricsManager, emit_metrics_loop
from protocols.terrarium.mirror import HolographicBuffer

manager = MetricsManager(default_interval=1.0)

# Start metrics emission for an agent
manager.start_metrics(
    agent_id="flux-001",
    flux_agent=flux,
    buffer=buffer,
    interval=1.0,  # Emit every second
)

# Events emitted to buffer:
# {
#   "event_type": "metabolism",
#   "agent_id": "flux-001",
#   "pressure": 35.0,     # Queue backlog (0-100)
#   "flow": 10.5,         # Events/second throughput
#   "temperature": 0.42,  # Entropy consumption rate (0-1)
#   "state": "running",
# }

# Stop when done
manager.stop_metrics("flux-001")
```

### Metric Calculations

| Metric | Meaning | Calculation |
|--------|---------|-------------|
| `pressure` | Queue backlog | Output queue fullness + perturbation backlog |
| `flow` | Throughput | Events processed / time delta |
| `temperature` | Entropy rate | Consumed entropy ratio OR metabolic temperature |

### Fever Alerts

```python
from protocols.terrarium.metrics import emit_fever_alert

# Emit when temperature exceeds threshold
await emit_fever_alert(
    agent_id="flux-001",
    buffer=buffer,
    temperature=0.92,
    threshold=0.8,
)
# Emits: {"event_type": "fever", "severity": "high", ...}
```

---

## SemanticField (Pheromone Communication)

Agents communicate indirectly via pheromones deposited in a shared field:

```python
from agents.i.semantic_field import (
    SemanticField,
    SemanticPheromoneKind,
    FieldCoordinate,
    MetaphorPayload,
    WarningPayload,
)

field = SemanticField()

# Agent A emits a pheromone
pheromone_id = field.emit(
    emitter="psi-gent",
    kind=SemanticPheromoneKind.METAPHOR,
    payload=MetaphorPayload(
        source_domain="database query",
        target_domain="topological sort",
        confidence=0.8,
    ),
    position=FieldCoordinate(domain="optimization"),
    intensity=1.0,
)

# Agent B senses nearby pheromones (doesn't know about A)
pheromones = field.sense(
    position=FieldCoordinate(domain="optimization"),
    kinds={SemanticPheromoneKind.METAPHOR},
)

for p in pheromones:
    print(f"Found metaphor: {p.payload.description}")
```

### Pheromone Types

| Kind | Emitter | Purpose | Decay Rate |
|------|---------|---------|------------|
| `METAPHOR` | Psi-gent | Functor[P,K] for pattern matching | Slow (0.1) |
| `INTENT` | F-gent | Artifact creation intent | Moderate (0.2) |
| `WARNING` | J-gent | Safety alerts (broadcast widely) | Fast (0.3) |
| `OPPORTUNITY` | B-gent | Economic signals | Moderate (0.15) |
| `CAPABILITY` | L-gent | Agent capability advertisement | Very slow (0.02) |
| `STATE` | D-gent | Data state changes | Medium (0.15) |
| `TEST` | T-gent | Test results | Fast (0.25) |

### Decay and Sensing

```python
# Pheromones decay over time
field.tick(dt=1.0)  # Apply time decay

# Sense with radius
pheromones = field.sense(
    position=my_position,
    radius=0.5,  # Semantic distance in embedding space
    kinds={SemanticPheromoneKind.WARNING},  # Filter by type
    min_intensity=0.1,  # Ignore faded pheromones
)

# Subscribe to deposit events
def on_deposit(pheromone):
    print(f"New pheromone from {pheromone.emitter}")

field._on_deposit.append(on_deposit)
```

### Stigmergic Coordination

Agents coordinate without knowing each other:

```python
# Psi-gent deposits metaphor (doesn't know F exists)
field.emit(
    emitter="psi-gent",
    kind=SemanticPheromoneKind.METAPHOR,
    payload=MetaphorPayload(
        source_domain="file system",
        target_domain="tree traversal",
        confidence=0.9,
    ),
    position=FieldCoordinate(domain="data_structures"),
)

# F-gent senses metaphors (doesn't know Psi exists)
metaphors = field.sense(
    position=FieldCoordinate(domain="data_structures"),
    kinds={SemanticPheromoneKind.METAPHOR},
)

# Result: Complete decoupling via shared environment
```

---

## Integration Example

Combining all three systems:

```python
from protocols.terrarium.mirror import HolographicBuffer
from protocols.terrarium.metrics import MetricsManager
from agents.flux import Flux, FluxConfig
from agents.flux.metabolism import create_flux_metabolism
from agents.i.semantic_field import SemanticField, SemanticPheromoneKind

# 1. Create infrastructure
buffer = HolographicBuffer()
metrics = MetricsManager()
field = SemanticField()
engine = MetabolicEngine()

# 2. Create metabolized FluxAgent
metabolism = create_flux_metabolism(engine=engine)
flux = Flux.lift(my_agent)
flux.attach_metabolism(metabolism)

# 3. Start metrics emission
metrics.start_metrics("my-agent", flux, buffer)

# 4. Process with pheromone emission
async for result in flux.start(event_stream):
    # Emit result to mirror (for UI)
    await buffer.reflect({
        "type": "result",
        "agent_id": "my-agent",
        "data": result,
    })

    # Emit pheromone to field (for other agents)
    if result.is_significant:
        field.emit(
            emitter="my-agent",
            kind=SemanticPheromoneKind.STATE,
            payload={"changed": result.key},
            position=FieldCoordinate(domain="state_updates"),
        )

# 5. Clean up
metrics.stop_metrics("my-agent")
```

---

## Debugging Patterns

### Status Inspection

```python
# Metabolism status
print(metabolism.status())

# Buffer status
print(f"Observers: {buffer.observer_count}")
print(f"Events: {buffer.events_reflected}")

# Field status
print(f"Active pheromones: {len([p for p in field._pheromones.values() if p.is_active])}")
```

### Event Tracing

```python
# Log all pheromone deposits
def trace_deposits(pheromone):
    print(f"[{pheromone.emitter}] {pheromone.kind.name}: {pheromone.payload}")

field._on_deposit.append(trace_deposits)
```

### Mirror Snapshots

```python
# Get current state without WebSocket
events = buffer.get_snapshot()
for event in events[-10:]:  # Last 10 events
    print(event)
```

---

## Quick Reference

### HolographicBuffer

```python
buffer = HolographicBuffer(max_history=100)
await buffer.reflect(event)         # Fire and forget
await buffer.attach_mirror(ws)      # Connect observer
buffer.detach_mirror(ws)            # Disconnect
buffer.get_snapshot()               # REST-friendly
buffer.clear_history()              # Reset
```

### FluxMetabolism

```python
metabolism = create_flux_metabolism(engine=engine)
flux.attach_metabolism(metabolism)
await metabolism.consume(event)     # Called per event
metabolism.tithe(0.1)               # Voluntary discharge
metabolism.status()                 # Full status dict
metabolism.pressure                 # Current pressure
metabolism.temperature              # Token ratio
metabolism.in_fever                 # Fever state
```

### SemanticField

```python
field = SemanticField()
field.emit(emitter, kind, payload, position)  # Deposit
field.sense(position, radius, kinds)          # Query
field.tick(dt)                                # Apply decay
field.deposit(pheromone)                      # Direct deposit
```

---

## Related Skills

- [building-agent](building-agent.md) - Creating well-formed agents
- [flux-agent](flux-agent.md) - Streaming agents
- [test-patterns](test-patterns.md) - Testing with observability

---

## Changelog

- 2025-12-12: Initial version synthesizing Mirror, Metabolism, and SemanticField patterns
