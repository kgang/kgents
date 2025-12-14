# Epilogue: FeverOverlay Trigger Wiring

**Date**: 2025-12-13
**Track**: B - FeverOverlay Trigger Integration
**Phase**: IMPLEMENT (complete)

---

## What Shipped

### FeverTriggeredEvent (EventBus)

New event type in `agents/i/services/events.py`:

```python
@dataclass
class FeverTriggeredEvent(Event):
    """Emitted when entropy exceeds threshold and fever overlay should show."""
    entropy: float = 0.0
    pressure: float = 0.0
    trigger: str = "pressure_overflow"
    oblique_strategy: str | None = None
```

### DashboardApp Subscription

In `agents/i/screens/dashboard.py`, `on_mount()` now subscribes to fever events:

```python
self._event_bus.subscribe(FeverTriggeredEvent, self._on_fever_triggered)
```

Handler checks threshold and pushes overlay:

```python
def _on_fever_triggered(self, event: Any) -> None:
    if should_show_fever_overlay(event.entropy):
        overlay = create_fever_overlay(entropy=event.entropy, ...)
        self.push_screen(overlay)
```

### MetricsObservable Threshold Detection

In `agents/i/data/dashboard_collectors.py`:

- Added `FEVER_THRESHOLD = 0.7` class constant
- Track `_previous_pressure` for threshold crossing detection
- Emit `FeverTriggeredEvent` via EventBus when pressure crosses threshold upward
- Only emits on state *change*, not continuously

---

## The Accursed Share Connection

*"Substrate compaction IS entropy spending."*

When metabolic pressure exceeds 0.7:
1. MetricsObservable detects the threshold crossing
2. FeverTriggeredEvent is emitted via EventBus
3. DashboardApp receives event, checks `should_show_fever_overlay()`
4. FeverOverlay appears with entropy gauge + oblique strategy

This makes the Accursed Share **visible**: entropy that cannot be productively used
must be discharged. The FeverOverlay surfaces creative strategies (Eno's Oblique
Strategies) to redirect this energy productively.

---

## Integration Points

| Component | File | Change |
|-----------|------|--------|
| FeverTriggeredEvent | `agents/i/services/events.py` | New event type |
| Services export | `agents/i/services/__init__.py` | Added to `__all__` |
| DashboardApp | `agents/i/screens/dashboard.py` | Subscription + handler |
| MetricsObservable | `agents/i/data/dashboard_collectors.py` | Threshold crossing emission |

---

## Track A Deferred

Memory Substrate wiring (Track A) was researched but not implemented this session.
Key findings documented in agent research output:

- MemoryNode has `_substrate`, `_compactor`, `_router` but often None
- SharedSubstrate has full API (allocate, promote, demote, compact)
- Ghost lifecycle has LifecycleAwareCache but engrams use raw files
- Two parallel crystal systems exist (D-gent + M-gent)
- Main gap: Runtime initialization doesn't wire these together

Ready for next session's IMPLEMENT phase.

---

## Metrics

| Metric | Value |
|--------|-------|
| Files modified | 4 |
| New event type | 1 |
| New methods | 2 |
| Lines added | ~45 |

---

## Distillable Insight

> *"Threshold crossing, not continuous presence, triggers the Accursed Share's visibility."*

The fever event only fires when pressure *crosses* 0.7, not when it stays above.
This matches the thermodynamic insight: it's the phase transition that matters,
not the steady state.

---

*"To read is to invoke. There is no view from nowhere."*
