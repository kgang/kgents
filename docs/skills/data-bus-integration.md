# Data Bus Integration

> *"Data flows through the bus. Agents subscribe to what they care about."*

This skill documents the kgents reactive data flow infrastructure—the event-driven backbone that enables agents to communicate and coordinate without tight coupling.

---

## Overview: The Three-Bus Architecture

kgents uses a layered event bus architecture with three distinct bus types:

| Bus | Scope | Purpose | Delivery |
|-----|-------|---------|----------|
| **DataBus** | Single process | D-gent storage events | At-least-once, causal ordering |
| **SynergyBus** | Cross-jewel | Crown Jewel coordination | Fire-and-forget, handler isolation |
| **EventBus** | Fan-out | UI/streaming distribution | Backpressure, bounded queues |

```
┌───────────────────────────────────────────────────────────────────────────┐
│                            Event Flow Architecture                         │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   D-gent (Storage)                                                        │
│       │                                                                   │
│       ▼                                                                   │
│   ┌─────────────┐                                                         │
│   │  DataBus    │ ──────────────┬──────────────┬──────────────┐          │
│   └─────────────┘               │              │              │          │
│                                 ▼              ▼              ▼          │
│                           ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│                           │ M-gent  │    │  Trace  │    │ Bridge  │     │
│                           │Listener │    │Listener │    │→Synergy │     │
│                           └─────────┘    └─────────┘    └────┬────┘     │
│                                                              │           │
│   Crown Jewels (Gestalt, Brain, etc.)                        ▼           │
│       │                                                                   │
│       ▼                                                                   │
│   ┌─────────────┐                                                         │
│   │ SynergyBus  │ ──────────────┬──────────────┬──────────────┐          │
│   └─────────────┘               │              │              │          │
│                                 ▼              ▼              ▼          │
│                           ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│                           │Gestalt→ │    │Atelier→ │    │Garden→  │     │
│                           │ Brain   │    │ Brain   │    │ Brain   │     │
│                           └─────────┘    └─────────┘    └─────────┘     │
│                                                                           │
│   Agent Town (Simulation)                                                 │
│       │                                                                   │
│       ▼                                                                   │
│   ┌─────────────┐                                                         │
│   │ EventBus[T] │ ──────────────┬──────────────┬──────────────┐          │
│   └─────────────┘               │              │              │          │
│                                 ▼              ▼              ▼          │
│                           ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│                           │   SSE   │    │  NATS   │    │ Widget  │     │
│                           │Endpoint │    │ Bridge  │    │Renderer │     │
│                           └─────────┘    └─────────┘    └─────────┘     │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 1. DataBus: Storage-Level Events

The DataBus emits events whenever D-gent stores, deletes, upgrades, or degrades data.

### Event Types

```python
from agents.d.bus import DataEventType

DataEventType.PUT      # New datum stored
DataEventType.DELETE   # Datum removed
DataEventType.UPGRADE  # Datum promoted to higher tier (MEMORY → SQLITE → POSTGRES)
DataEventType.DEGRADE  # Datum demoted (graceful degradation)
```

### DataEvent Structure

```python
from agents.d.bus import DataEvent, DataEventType

@dataclass(frozen=True, slots=True)
class DataEvent:
    event_id: str              # Unique event ID (UUID hex)
    event_type: DataEventType  # PUT | DELETE | UPGRADE | DEGRADE
    datum_id: str              # ID of affected datum
    timestamp: float           # Unix timestamp
    source: str                # Who caused it (agent ID)
    causal_parent: str | None  # Previous event this depends on
    metadata: dict[str, str]   # Additional context
```

### Subscribing to DataBus

```python
from agents.d.bus import get_data_bus, DataEventType

bus = get_data_bus()

# Subscribe to specific event type
async def on_put(event):
    print(f"Data stored: {event.datum_id}")

unsubscribe = bus.subscribe(DataEventType.PUT, on_put)

# Subscribe to ALL events
async def on_any(event):
    print(f"{event.event_type.name}: {event.datum_id}")

unsubscribe_all = bus.subscribe_all(on_any)

# Later: stop receiving events
unsubscribe()
unsubscribe_all()
```

### Replaying Buffered Events

Late subscribers can catch up on missed events:

```python
# Replay all buffered events
count = await bus.replay(handler=my_handler)

# Replay events since timestamp
count = await bus.replay(handler=my_handler, since=1702756800.0)

# Replay only PUT events
count = await bus.replay(handler=my_handler, event_type=DataEventType.PUT)
```

### BusEnabledDgent: Auto-Emit on Storage

Wrap any D-gent backend to auto-emit events:

```python
from agents.d.bus import BusEnabledDgent, get_data_bus
from agents.d.backends.memory import MemoryBackend

backend = MemoryBackend()
bus = get_data_bus()
dgent = BusEnabledDgent(backend, bus, source="my-agent")

# These operations now emit events automatically
await dgent.put(datum)   # → PUT event
await dgent.delete(id)   # → DELETE event (if found)
await dgent.get(id)      # No event (reads are silent)
```

### Guarantees

| Property | Guarantee |
|----------|-----------|
| **Delivery** | At-least-once (subscribers may receive duplicates) |
| **Ordering** | Causal (if A caused B, A delivered before B) |
| **Blocking** | Non-blocking (publishers never wait for subscribers) |
| **Buffer** | Bounded (old events dropped when buffer full, default 1000) |

### AGENTESE Paths

DataBus exposes these paths under `self.bus.*`:

| Path | Description |
|------|-------------|
| `self.bus.manifest` | View current bus state |
| `self.bus.subscribe` | Subscribe to event types |
| `self.bus.unsubscribe` | Unsubscribe by handler ID |
| `self.bus.replay` | Replay buffered events |
| `self.bus.latest` | Get most recent event |
| `self.bus.stats` | Get bus statistics |
| `self.bus.history` | Get recent event history |

---

## 2. SynergyBus: Cross-Jewel Coordination

The SynergyBus enables Crown Jewels to react to each other's significant operations.

### Event Types (Selected)

```python
from protocols.synergy import SynergyEventType, Jewel

# Gestalt events
SynergyEventType.ANALYSIS_COMPLETE
SynergyEventType.DRIFT_DETECTED

# Brain events
SynergyEventType.CRYSTAL_FORMED
SynergyEventType.MEMORY_SURFACED

# Gardener events
SynergyEventType.SEASON_CHANGED
SynergyEventType.GESTURE_APPLIED

# Atelier events
SynergyEventType.PIECE_CREATED
SynergyEventType.BID_ACCEPTED

# Coalition events
SynergyEventType.COALITION_FORMED
SynergyEventType.TASK_ASSIGNED

# D-gent events (bridges from DataBus)
SynergyEventType.DATA_STORED
SynergyEventType.DATA_UPGRADED
SynergyEventType.DATA_DEGRADED
```

### Emitting Synergy Events

```python
from protocols.synergy import (
    get_synergy_bus,
    create_analysis_complete_event,
)

bus = get_synergy_bus()

# Use factory functions for type-safe event creation
event = create_analysis_complete_event(
    source_id="analysis-123",
    module_count=50,
    health_grade="B+",
    average_health=0.84,
    drift_count=2,
    root_path="/path/to/project",
)

# Fire and forget
await bus.emit(event)

# Or wait for all handlers
results = await bus.emit_and_wait(event)
```

### Creating Synergy Handlers

```python
from protocols.synergy import (
    SynergyHandler,
    SynergyEvent,
    SynergyResult,
    SynergyEventType,
    get_synergy_bus,
)

class MyHandler(SynergyHandler):
    @property
    def name(self) -> str:
        return "MyHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        # Process the event
        print(f"Received: {event.event_type.value}")

        return SynergyResult(
            success=True,
            handler_name=self.name,
            message="Processed successfully",
            artifact_id="created-artifact-123",  # Optional
        )

# Register the handler
bus = get_synergy_bus()
unsubscribe = bus.register(SynergyEventType.ANALYSIS_COMPLETE, MyHandler())
```

### Subscribing to Results

The SynergyBus supports result subscriptions for UI notifications:

```python
def on_result(event: SynergyEvent, result: SynergyResult):
    if result.success:
        print(f"✓ {event.event_type.value}: {result.message}")
        if result.artifact_id:
            print(f"  ↳ Crystal: \"{result.artifact_id}\"")

unsubscribe = bus.subscribe_results(on_result)
```

### Built-in Handlers

The SynergyBus comes pre-configured with these handlers:

| Handler | Event | Action |
|---------|-------|--------|
| `GestaltToBrainHandler` | ANALYSIS_COMPLETE | Auto-capture architecture snapshots |
| `AtelierToBrainHandler` | PIECE_CREATED | Auto-capture created pieces |
| `CoalitionToBrainHandler` | TASK_ASSIGNED | Auto-capture task completions |
| `BrainToCoalitionHandler` | COALITION_FORMED | Enrich with context |
| `GardenToBrainHandler` | SEASON_CHANGED, GESTURE_APPLIED | Auto-capture garden state |
| `GestaltToGardenHandler` | ANALYSIS_COMPLETE | Update plot progress |

### Factory Functions (Complete List)

```python
from protocols.synergy import (
    # Gestalt
    create_analysis_complete_event,
    create_drift_detected_event,

    # Brain
    create_crystal_formed_event,

    # Gardener
    create_session_complete_event,
    create_artifact_created_event,
    create_season_changed_event,
    create_gesture_applied_event,
    create_plot_progress_event,

    # Atelier
    create_piece_created_event,
    create_bid_accepted_event,

    # Coalition
    create_coalition_formed_event,
    create_task_complete_event,

    # Domain
    create_drill_complete_event,
    create_drill_started_event,
    create_timer_warning_event,

    # Park
    create_scenario_complete_event,
    create_serendipity_injected_event,
    create_force_used_event,

    # D-gent (data layer)
    create_data_stored_event,
    create_data_deleted_event,
    create_data_upgraded_event,
    create_data_degraded_event,

    # F-gent (flow)
    create_flow_started_event,
    create_flow_completed_event,
    create_turn_completed_event,
    create_hypothesis_created_event,
    create_hypothesis_synthesized_event,
    create_consensus_reached_event,
    create_contribution_posted_event,
)
```

---

## 3. EventBus: Fan-Out Distribution

The generic EventBus provides typed fan-out for streaming scenarios.

### Creating a Typed EventBus

```python
from agents.town.event_bus import EventBus, Subscription

# Create typed bus
bus = EventBus[TownEvent](max_queue_size=1000)

# Publish to all subscribers
delivered_count = await bus.publish(event)

# Create subscription (returns async iterator)
sub = bus.subscribe()
try:
    async for event in sub:
        process(event)
finally:
    sub.close()
```

### Subscription Patterns

```python
# Pattern 1: Async iteration
sub = bus.subscribe()
async for event in sub:
    process(event)

# Pattern 2: Polling with timeout
sub = bus.subscribe()
event = await sub.get(timeout=5.0)  # Returns None on timeout

# Pattern 3: Non-blocking check
if sub.pending_count > 0:
    event = await sub.get(timeout=0)
```

### Backpressure

EventBus handles slow subscribers via bounded queues:

```python
bus = EventBus[MyEvent](max_queue_size=100)

# If subscriber queue is full, events are DROPPED (not blocked)
# Check stats to detect slow subscribers:
stats = bus.stats
print(f"Overflow count: {stats.queue_overflow_count}")
```

### Cleanup

```python
# Close all subscriptions
bus.close()  # Sends None sentinel to unblock waiting subscribers

# Check state
assert bus.is_closed
assert bus.subscriber_count == 0
```

---

## 4. M-gent Bus Listener: Auto-Indexing

M-gent can automatically index data as it's stored via the Bus Listener.

### Setup

```python
from agents.m.bus_listener import create_bus_listener
from agents.m import AssociativeMemory
from agents.d.bus import get_data_bus

mgent = AssociativeMemory(dgent=my_dgent)
bus = get_data_bus()

listener = create_bus_listener(
    mgent=mgent,
    bus=bus,
    auto_index=True,     # Auto-create memories for PUT events
    auto_remove=True,    # Auto-remove on DELETE events
    embedder=my_embedder # Optional custom embedder
)

# Start listening
listener.start()

# Now: any D-gent PUT automatically creates a Memory entry
# And: any D-gent DELETE removes the Memory entry

# Stop when done
listener.stop()
```

### Catching Up

Late-starting listeners can replay missed events:

```python
# Start listener
listener.start()

# Catch up on missed events
count = await listener.replay_and_index(since=last_seen_timestamp)
print(f"Indexed {count} missed events")
```

---

## 5. Bridging DataBus to SynergyBus

Significant data operations can be promoted to the cross-jewel synergy bus:

```python
from protocols.agentese.contexts.self_bus import wire_data_to_synergy

# One-time setup: bridge data events to synergy
wire_data_to_synergy()

# Now DataBus events are forwarded to SynergyBus:
# - PUT → DATA_STORED
# - DELETE → DATA_DELETED
# - UPGRADE → DATA_UPGRADED
# - DEGRADE → DATA_DEGRADED
```

---

## 6. Flux Integration: Event-Driven Streaming

The Flux system integrates with event buses for streaming:

```python
from agents.flux.sources.events import from_events, from_queue, from_iterable

# From an event bus
async for event in from_events(my_bus):
    process(event)

# From an asyncio.Queue
async for item in from_queue(my_queue):
    process(item)

# From any iterable (for testing)
async for item in from_iterable([1, 2, 3]):
    process(item)
```

**Key Principle**: Event-driven sources respond to actual events, not timer ticks.

---

## 7. Testing

### Testing DataBus

```python
import pytest
from agents.d.bus import DataBus, DataEvent, DataEventType, reset_data_bus

@pytest.fixture
def bus():
    return DataBus()

@pytest.fixture(autouse=True)
def cleanup():
    yield
    reset_data_bus()  # Reset global singleton

@pytest.mark.asyncio
async def test_subscription(bus):
    received = []

    async def handler(event):
        received.append(event)

    bus.subscribe(DataEventType.PUT, handler)
    await bus.emit(DataEvent.create(DataEventType.PUT, "test-id"))
    await asyncio.sleep(0.01)  # Give handler time to run

    assert len(received) == 1
```

### Testing SynergyBus

```python
from protocols.synergy import (
    get_synergy_bus,
    reset_synergy_bus,
    create_analysis_complete_event,
)

@pytest.fixture(autouse=True)
def cleanup():
    yield
    reset_synergy_bus()

@pytest.mark.asyncio
async def test_synergy_flow():
    bus = get_synergy_bus()

    event = create_analysis_complete_event(
        source_id="test",
        module_count=10,
        health_grade="A",
        average_health=0.9,
        drift_count=0,
        root_path="/test",
    )

    # Wait for handlers to complete
    results = await bus.emit_and_wait(event)

    # Check results
    for result in results:
        assert result.success
```

---

## 8. Common Patterns

### Pattern: Audit Trail

```python
from agents.d.bus import get_data_bus
from weave.trace_monoid import TraceMonoid, Event

trace = TraceMonoid()
bus = get_data_bus()

async def audit_handler(event):
    trace.append_mut(
        Event(
            id=event.event_id,
            source=f"dgent:{event.source}",
            timestamp=event.timestamp,
            payload={
                "type": event.event_type.value,
                "datum_id": event.datum_id,
            },
        ),
        depends_on={event.causal_parent} if event.causal_parent else None,
    )

bus.subscribe_all(audit_handler)
```

### Pattern: UI Notification Bridge

```python
from protocols.synergy import get_synergy_bus, display_synergy_notification

bus = get_synergy_bus()

def on_result(event, result):
    display_synergy_notification(event, result)

bus.subscribe_results(on_result)
```

### Pattern: Reactive Signal Bridge

```python
from agents.i.reactive import Signal
from agents.d.bus import get_data_bus, DataEventType

bus = get_data_bus()
latest_put = Signal.of(None)

async def bridge(event):
    latest_put.set(event)

bus.subscribe(DataEventType.PUT, bridge)

# Now UI can react to latest_put signal changes
```

---

## 9. What These Buses Are NOT

| Bus | Is NOT | Why |
|-----|--------|-----|
| DataBus | Message queue | No persistence, no acknowledgments |
| DataBus | RPC | Fire-and-forget, no responses |
| DataBus | Cross-process | Single process only |
| SynergyBus | Guaranteed delivery | Handler failures are isolated |
| SynergyBus | Transactional | Events may fire during rollback |
| EventBus | Durable | In-memory only, bounded buffer |

---

## 10. Quick Reference

### Imports

```python
# DataBus
from agents.d.bus import (
    DataBus, DataEvent, DataEventType,
    BusEnabledDgent,
    get_data_bus, reset_data_bus,
)

# SynergyBus
from protocols.synergy import (
    SynergyEventBus, SynergyEvent, SynergyResult,
    SynergyEventType, Jewel,
    SynergyHandler, ResultSubscriber,
    get_synergy_bus, reset_synergy_bus,
    # Factory functions
    create_analysis_complete_event,
    create_crystal_formed_event,
    # ... (see section 2)
)

# EventBus
from agents.town.event_bus import (
    EventBus, EventBusStats, Subscription,
)

# M-gent Listener
from agents.m.bus_listener import (
    MgentBusListener, BusEventHandler,
    create_bus_listener,
)

# AGENTESE Bus Node
from protocols.agentese.contexts.self_bus import (
    BusNode, create_bus_resolver,
    wire_data_to_synergy,
)

# Flux Sources
from agents.flux.sources.events import (
    from_events, from_queue, from_iterable,
    from_stream, empty, single, repeat,
)
```

### Decision Tree

```
Need to react to D-gent storage operations?
  → Use DataBus

Need Crown Jewels to coordinate?
  → Use SynergyBus

Need fan-out to multiple UI/streaming subscribers?
  → Use EventBus[T]

Need M-gent to auto-index stored data?
  → Use MgentBusListener

Need to expose bus via AGENTESE?
  → Use BusNode (self.bus.*)

Need to stream events through Flux pipeline?
  → Use from_events() source
```

---

## See Also

- `spec/protocols/data-bus.md` — Specification
- `spec/d-gents/architecture.md` — D-gent storage
- `spec/m-gents/architecture.md` — M-gent memory
- `impl/claude/agents/d/bus.py` — DataBus implementation
- `impl/claude/protocols/synergy/` — SynergyBus implementation
- `impl/claude/agents/town/event_bus.py` — EventBus implementation
- `impl/claude/agents/m/bus_listener.py` — M-gent listener
- `impl/claude/protocols/agentese/contexts/self_bus.py` — AGENTESE integration
