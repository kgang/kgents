---
path: plans/_continuations/foundation-4-synergy-bus
status: complete
progress: 100
last_touched: 2025-12-16
touched_by: claude-opus-4
blocking: []
enables:
  - Wave 1 Hero Path completion
  - Cross-jewel integration
session_notes: |
  Foundation 4 COMPLETE!

  Implementation:
  - SynergyEventBus with pub/sub pattern
  - SynergyEvent + SynergyEventType + Jewel enums
  - Factory functions for common events
  - GestaltToBrainHandler (auto-capture architecture snapshots)
  - CLI visibility: Shows synergy notifications after Gestalt analysis
  - 34 passing tests for events, bus, and handlers

  Files created:
  - protocols/synergy/__init__.py
  - protocols/synergy/events.py
  - protocols/synergy/bus.py
  - protocols/synergy/handlers/__init__.py
  - protocols/synergy/handlers/base.py
  - protocols/synergy/handlers/gestalt_brain.py
  - protocols/synergy/_tests/test_events.py
  - protocols/synergy/_tests/test_bus.py
  - protocols/synergy/_tests/test_handlers.py

  Integration:
  - Gestalt handler now emits synergy events after analysis
  - CLI shows: "Synergy: Architecture snapshot captured to Brain"
---

# Foundation 4: Synergy Event Bus - Continuation Prompt

> *"Jewels that talk to each other without being asked."*

## Context

You are the **Crown Jewel Executor** continuing Wave 0 of the Enlightened Crown strategy.

### Completed Foundations
- ✅ **Foundation 1**: AGENTESE Path Visibility (27 tests)
- ✅ **Foundation 2**: Observer Switcher (ObserverSwitcher component, hooks)
- ✅ **Foundation 3**: Polynomial Diagram (34 tests, PolynomialDiagram component)

### Current Foundation
**Foundation 4: Cross-Jewel Synergy (Synergy Event Bus)**

## The Problem

From `plans/crown-jewels-enlightened.md`:

> **The Problem**: Jewels operate in isolation. No automatic data flow.
>
> **The Solution**: Automatic synergies with visible notifications.
>
> ```
> ✓ Gestalt analysis complete
> ↳ Synergy: Architecture snapshot captured to Brain
> ↳ Crystal: "impl/claude/ architecture 2025-12-16"
> ```

Currently, each Crown Jewel (Brain, Gestalt, Gardener, etc.) operates independently. When a user runs `kg gestalt analyze`, the architecture insights don't automatically flow to Brain for memory. When a Gardener session creates artifacts, they aren't captured to Brain. This breaks the unified experience.

## Requirements

### Core Infrastructure

1. **SynergyEventBus** - Central event bus for cross-jewel communication
   - Publish/subscribe pattern
   - Event types: `ANALYSIS_COMPLETE`, `CRYSTAL_FORMED`, `SESSION_STARTED`, `ARTIFACT_CREATED`, etc.
   - Async handlers that don't block the source operation

2. **SynergyEvent** - Event payload structure
   ```python
   @dataclass
   class SynergyEvent:
       source_jewel: str      # "gestalt", "brain", "gardener", etc.
       target_jewel: str      # Target jewel or "*" for broadcast
       event_type: str        # "architecture_snapshot", "crystal_formed", etc.
       source_id: str         # ID of the source artifact
       payload: dict          # Event-specific data
       timestamp: datetime
       correlation_id: str    # For tracing related events
   ```

3. **Synergy Handlers** - Per-jewel handlers that respond to events
   - `GestaltToBrainHandler` - Captures architecture snapshots to Brain
   - `GardenerToBrainHandler` - Captures session artifacts to Brain
   - `BrainToGardenerHandler` - Surfaces relevant crystals for context

### Integration Points

| Source | Event | Target | Action |
|--------|-------|--------|--------|
| Gestalt | `ANALYSIS_COMPLETE` | Brain | Auto-capture architecture snapshot |
| Gardener | `SESSION_COMPLETE` | Brain | Capture learnings as crystals |
| Gardener | `ARTIFACT_CREATED` | Brain | Capture artifact metadata |
| Brain | `CRYSTAL_FORMED` | Gardener | Surface as session context |
| Atelier | `PIECE_CREATED` | Brain | Capture creation metadata |

### CLI Visibility

When synergy occurs, show it in CLI output:
```
✓ Gestalt analysis complete
  ↳ 🔗 Synergy: Architecture captured to Brain
  ↳ Crystal: "gestalt-impl-claude-2025-12-16"
```

### Web UI Visibility

- Toast notifications for synergy events
- Synergy indicator in jewel cards
- Cross-jewel links in detail views

## Implementation Guide

### File Structure

```
impl/claude/protocols/synergy/
├── __init__.py
├── bus.py              # SynergyEventBus implementation
├── events.py           # Event types and SynergyEvent dataclass
├── handlers/
│   ├── __init__.py
│   ├── base.py         # BaseSynergyHandler
│   ├── gestalt_brain.py
│   ├── gardener_brain.py
│   └── brain_gardener.py
├── _tests/
│   ├── __init__.py
│   ├── test_bus.py
│   ├── test_events.py
│   └── test_handlers.py
```

### Key Patterns

1. **Singleton Bus** - One bus instance per process
   ```python
   _bus: SynergyEventBus | None = None

   def get_synergy_bus() -> SynergyEventBus:
       global _bus
       if _bus is None:
           _bus = SynergyEventBus()
           _bus.register_default_handlers()
       return _bus
   ```

2. **Non-blocking Emission** - Don't slow down the source
   ```python
   async def emit(self, event: SynergyEvent) -> None:
       # Fire and forget - handlers run in background
       asyncio.create_task(self._dispatch(event))
   ```

3. **Graceful Degradation** - Synergy failures shouldn't break source
   ```python
   async def _dispatch(self, event: SynergyEvent) -> None:
       for handler in self._handlers.get(event.event_type, []):
           try:
               await handler.handle(event)
           except Exception as e:
               logger.warning(f"Synergy handler failed: {e}")
               # Continue - don't break other handlers
   ```

### Integration with Existing Code

1. **Gestalt Handler** (`impl/claude/protocols/gestalt/handler.py`)
   - After analysis completes, emit `ANALYSIS_COMPLETE` event
   - Include module count, health grade, timestamp in payload

2. **Gardener Session** (`impl/claude/agents/gardener/session.py`)
   - On `complete()`, emit `SESSION_COMPLETE` event
   - On artifact recording, emit `ARTIFACT_CREATED` event

3. **Brain Cortex** (`impl/claude/agents/m/__init__.py`)
   - On crystal formation, emit `CRYSTAL_FORMED` event
   - Handler for incoming events creates appropriate crystals

### Web Components

```tsx
// src/components/synergy/SynergyToast.tsx
// Toast notification when synergy occurs

// src/components/synergy/SynergyBadge.tsx
// Badge showing recent synergies on jewel cards

// src/hooks/useSynergyStream.ts
// Hook for subscribing to synergy events via SSE
```

## Success Criteria

- [ ] `SynergyEventBus` with pub/sub pattern
- [ ] At least 3 working synergy handlers
- [ ] CLI shows synergy notifications
- [ ] Web UI shows synergy toasts
- [ ] Tests for bus, events, and handlers
- [ ] Gestalt → Brain synergy works end-to-end
- [ ] Non-blocking (source operations not slowed)

## Session Protocol

1. Read `plans/crown-jewels-enlightened.md` for full context
2. Check existing gestalt and brain implementations
3. Create synergy infrastructure
4. Integrate with gestalt handler first (quickest win)
5. Add CLI visibility
6. Add web UI components
7. Write tests

## Reference Files

| File | Purpose |
|------|---------|
| `plans/crown-jewels-enlightened.md` | Master plan (Foundation 4 section) |
| `impl/claude/protocols/gestalt/handler.py` | Gestalt CLI handler |
| `impl/claude/agents/m/__init__.py` | Brain/Memory agent |
| `impl/claude/agents/gardener/session.py` | Gardener session |
| `impl/claude/protocols/cli/path_display.py` | Path display utilities |

---

*"The garden tends itself, but only because the plants talk to each other."*
