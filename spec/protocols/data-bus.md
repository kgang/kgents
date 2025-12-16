# Data Bus Protocol: Reactive Data Flow

> *"Data flows through the bus. Agents subscribe to what they care about."*

**Status**: NEW — Bridges D-gent, M-gent, and the reactive substrate.

---

## Purpose

The Data Bus provides **reactive data flow** between D-gent (storage), M-gent (memory), and any agent that needs to observe data changes. It unifies:

- **Reactive Signals** — Local, synchronous change propagation
- **Synergy Events** — Cross-jewel, async event emission
- **Causal Traces** — History with dependency tracking

---

## The Core Abstraction

```python
@dataclass(frozen=True)
class DataEvent:
    """
    An event representing a data change.

    Emitted by D-gent on every write/delete.
    Consumed by M-gent, UI, tracing, etc.
    """
    event_id: str              # Unique event ID
    event_type: DataEventType  # PUT | DELETE | UPGRADE | DEGRADE
    datum_id: str              # ID of affected datum
    timestamp: float           # When it happened
    source: str                # Who caused it (agent ID)
    causal_parent: str | None  # Previous event this depends on
    metadata: dict[str, str]   # Additional context

class DataEventType(Enum):
    PUT = "put"           # New datum stored
    DELETE = "delete"     # Datum removed
    UPGRADE = "upgrade"   # Datum promoted to higher tier
    DEGRADE = "degrade"   # Datum demoted (graceful degradation)
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Data Bus                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Event Stream                          │    │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐               │    │
│  │  │ PUT │→│ PUT │→│ DEL │→│ UPG │→│ PUT │→ ...          │    │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              ▼               ▼               ▼                  │
│         ┌─────────┐    ┌─────────┐    ┌─────────┐              │
│         │ M-gent  │    │  Trace  │    │   UI    │              │
│         │Listener │    │Listener │    │Listener │              │
│         └─────────┘    └─────────┘    └─────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    ┌─────────┴─────────┐
                    │      D-gent       │
                    │  (emits events)   │
                    └───────────────────┘
```

---

## The Bus Protocol

```python
class DataBus:
    """
    Central bus for data events.

    Features:
    - Multiple subscribers per event type
    - Async, non-blocking emission
    - Replay capability (for late subscribers)
    - Causal ordering guarantees
    """

    def __init__(self, buffer_size: int = 1000):
        self._subscribers: dict[DataEventType, list[Subscriber]] = defaultdict(list)
        self._buffer: deque[DataEvent] = deque(maxlen=buffer_size)
        self._lock = asyncio.Lock()

    # --- Publishing ---

    async def emit(self, event: DataEvent) -> None:
        """
        Emit an event to all subscribers.

        Non-blocking: subscribers run in background.
        """
        async with self._lock:
            self._buffer.append(event)

        # Notify subscribers (non-blocking)
        subscribers = self._subscribers.get(event.event_type, [])
        for sub in subscribers:
            asyncio.create_task(self._safe_notify(sub, event))

    # --- Subscribing ---

    def subscribe(
        self,
        event_type: DataEventType,
        handler: Callable[[DataEvent], Awaitable[None]],
    ) -> Callable[[], None]:
        """
        Subscribe to events of a specific type.

        Returns unsubscribe function.
        """
        sub = Subscriber(handler=handler)
        self._subscribers[event_type].append(sub)

        def unsubscribe():
            if sub in self._subscribers[event_type]:
                self._subscribers[event_type].remove(sub)

        return unsubscribe

    def subscribe_all(
        self,
        handler: Callable[[DataEvent], Awaitable[None]],
    ) -> Callable[[], None]:
        """Subscribe to ALL event types."""
        unsubs = []
        for event_type in DataEventType:
            unsubs.append(self.subscribe(event_type, handler))

        def unsubscribe_all():
            for unsub in unsubs:
                unsub()

        return unsubscribe_all

    # --- Replay ---

    async def replay(
        self,
        handler: Callable[[DataEvent], Awaitable[None]],
        since: float | None = None,
    ) -> int:
        """
        Replay buffered events to a handler.

        Useful for late subscribers to catch up.
        Returns count of replayed events.
        """
        count = 0
        async with self._lock:
            for event in self._buffer:
                if since is None or event.timestamp >= since:
                    await handler(event)
                    count += 1
        return count
```

---

## Integration with D-gent

D-gent automatically emits to the bus:

```python
class BusEnabledDgent:
    """
    D-gent that emits events to the Data Bus.
    """

    def __init__(self, backend: DgentProtocol, bus: DataBus):
        self.backend = backend
        self.bus = bus
        self._last_event_id: str | None = None

    async def put(self, datum: Datum) -> str:
        id = await self.backend.put(datum)

        await self.bus.emit(DataEvent(
            event_id=uuid4().hex,
            event_type=DataEventType.PUT,
            datum_id=id,
            timestamp=time.time(),
            source=datum.metadata.get("source", "unknown"),
            causal_parent=self._last_event_id,
            metadata=datum.metadata,
        ))

        self._last_event_id = id
        return id

    async def delete(self, id: str) -> bool:
        success = await self.backend.delete(id)

        if success:
            await self.bus.emit(DataEvent(
                event_id=uuid4().hex,
                event_type=DataEventType.DELETE,
                datum_id=id,
                timestamp=time.time(),
                source="dgent",
                causal_parent=self._last_event_id,
                metadata={},
            ))

        return success
```

---

## Integration with M-gent

M-gent listens to the bus to maintain its semantic index:

```python
class BusListeningMgent:
    """
    M-gent that listens to D-gent events via the Data Bus.
    """

    def __init__(self, mgent: MgentProtocol, bus: DataBus):
        self.mgent = mgent
        self.bus = bus

        # Subscribe to relevant events
        bus.subscribe(DataEventType.PUT, self._on_put)
        bus.subscribe(DataEventType.DELETE, self._on_delete)

    async def _on_put(self, event: DataEvent) -> None:
        """Handle new datum: add to semantic index."""
        # Only index if it's a "memory" type datum
        if event.metadata.get("type") == "memory":
            # The datum is already stored by D-gent
            # M-gent just needs to index it
            await self.mgent._index_datum(event.datum_id)

    async def _on_delete(self, event: DataEvent) -> None:
        """Handle deleted datum: remove from index."""
        await self.mgent._remove_from_index(event.datum_id)
```

---

## Integration with Reactive Signals

The bus bridges to the Signal network:

```python
class SignalBridge:
    """
    Bridge between DataBus (async events) and Signals (sync state).
    """

    def __init__(self, bus: DataBus):
        self.bus = bus

        # Signals for each event type
        self.puts = Signal.of([])      # list[DataEvent]
        self.deletes = Signal.of([])   # list[DataEvent]
        self.latest = Signal.of(None)  # DataEvent | None

        # Subscribe to bus
        bus.subscribe(DataEventType.PUT, self._on_put)
        bus.subscribe(DataEventType.DELETE, self._on_delete)

    async def _on_put(self, event: DataEvent) -> None:
        self.puts.update(lambda events: events[-99:] + [event])
        self.latest.set(event)

    async def _on_delete(self, event: DataEvent) -> None:
        self.deletes.update(lambda events: events[-99:] + [event])
        self.latest.set(event)
```

---

## Integration with TraceMonoid

The bus feeds the causal trace:

```python
class TraceBridge:
    """
    Bridge between DataBus and TraceMonoid.

    Every data event becomes a trace event with causal dependencies.
    """

    def __init__(self, bus: DataBus, trace: TraceMonoid):
        self.bus = bus
        self.trace = trace

        # Subscribe to all events
        bus.subscribe_all(self._on_event)

    async def _on_event(self, event: DataEvent) -> None:
        """Record data event in trace with causality."""
        depends_on = None
        if event.causal_parent:
            depends_on = {event.causal_parent}

        self.trace.append_mut(
            Event(
                id=event.event_id,
                source=f"dgent:{event.source}",
                timestamp=event.timestamp,
                payload={
                    "type": event.event_type.value,
                    "datum_id": event.datum_id,
                    "metadata": event.metadata,
                },
            ),
            depends_on=depends_on,
        )
```

---

## Integration with Synergy Bus

Data events can propagate to the cross-jewel synergy bus:

```python
class SynergyBridge:
    """
    Bridge between DataBus (local) and SynergyBus (cross-jewel).

    Only significant events are promoted to synergy:
    - Large data stores
    - Memory consolidation
    - Tier upgrades
    """

    def __init__(self, data_bus: DataBus, synergy_bus: SynergyEventBus):
        self.data_bus = data_bus
        self.synergy_bus = synergy_bus

        data_bus.subscribe(DataEventType.UPGRADE, self._on_upgrade)

    async def _on_upgrade(self, event: DataEvent) -> None:
        """Promote tier upgrades to synergy bus."""
        await self.synergy_bus.emit(SynergyEvent(
            event_type=SynergyEventType.DATA_UPGRADED,
            source_jewel=Jewel.DGENT,
            target_jewel=Jewel.ANY,
            payload={
                "datum_id": event.datum_id,
                "from_tier": event.metadata.get("from_tier"),
                "to_tier": event.metadata.get("to_tier"),
            },
        ))
```

---

## AGENTESE Paths

The Data Bus exposes these paths under `self.bus.*`:

| Path | Description |
|------|-------------|
| `self.bus.subscribe[type, handler]` | Subscribe to event type |
| `self.bus.unsubscribe[subscription_id]` | Unsubscribe |
| `self.bus.replay[since]` | Replay buffered events |
| `self.bus.latest` | Get most recent event |
| `self.bus.stats` | Get bus statistics |

---

## Guarantees

1. **At-least-once delivery**: Subscribers receive every event at least once.
2. **Causal ordering**: If A caused B, subscribers see A before B.
3. **Non-blocking emission**: Publishers never wait for subscribers.
4. **Bounded buffer**: Old events are dropped when buffer is full.

---

## What the Data Bus Is NOT

- **Not a message queue** — No persistence, no acknowledgments
- **Not RPC** — Fire-and-forget, no responses
- **Not transactional** — Events may be delivered during rollback
- **Not cross-process** — Single process only (use Synergy for cross-jewel)

---

## See Also

- `spec/d-gents/architecture.md` — D-gent emits events
- `spec/m-gents/architecture.md` — M-gent listens to events
- `spec/protocols/synergy.md` — Cross-jewel event bus
- `impl/claude/weave/trace_monoid.py` — Causal trace integration
