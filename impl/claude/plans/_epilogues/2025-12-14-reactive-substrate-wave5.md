# Wave 5 Epilogue: Reality Wiring

**Date**: 2025-12-14
**Focus**: AGENTESE binding, clock sync, adapters

## Summary

Wave 5 connects the reactive substrate to actual agent state, making the screens "live".

## Artifacts Created

### Clock Module (`wiring/clock.py`)
- `ClockState`: Immutable time snapshot with entropy seeding
- `Clock`: Central time source with pause/resume/rate control
- `create_clock()`: Factory with sensible defaults
- Global clock singleton for shared time

### Subscriptions Module (`wiring/subscriptions.py`)
- `ThrottledSignal`: High-frequency event batching (60fps throttle)
- `EventBus`: Cross-widget communication hub
- `EventType`: Standard events (agent, yield, clock, dashboard)
- `BatchedUpdates`: Queue multiple updates, emit once

### Adapters Module (`wiring/adapters.py`)
- `SoulAdapter`: SoulState → AgentCardState
- `AgentRuntimeAdapter`: Generic agent data → AgentCardState
- `YieldAdapter`: Agent yields → YieldCardState
- `ReactiveDashboardAdapter`: Signal-based dashboard state
- `create_dashboard_state()`: Factory for dashboard state

### Bindings Module (`wiring/bindings.py`)
- `PathBinding`: Individual AGENTESE path subscription
- `AGENTESEBinding`: Coordinated binding manager
- `BindingSpec`: Declarative binding DSL
- `apply_binding_spec()`: Apply spec to create bindings

## Metrics

| Metric | Value |
|--------|-------|
| New tests (Wave 5) | 120 |
| Total reactive tests | 537 |
| New lines of code | ~2,700 |
| Mypy errors | 0 |
| Ruff errors | 0 |

## Key Design Decisions

1. **Central Clock**: All time flows from ONE source. No scattered `time.now()` calls. This enables replay and deterministic testing.

2. **Throttled Updates**: High-frequency events (60fps+) are batched to prevent UI thrashing. EventBus + ThrottledSignal work together.

3. **Adapter Pattern**: Pure transformations from runtime data → widget state. Same input → same output. No side effects.

4. **AGENTESE Bindings**: Declarative path subscriptions with polling. PathBinding wraps individual paths; AGENTESEBinding coordinates multiple.

## Entropy Budget

- Planned: 10%
- Used: ~5%
- Exploration: Considered replay mode with timestamped snapshots, decided to defer to Wave 6+ (ClockState already captures needed data)

## Learnings

1. **TypeVar with Protocol**: Need careful type: ignore for mock objects in tests. Mock objects don't satisfy Protocol requirements.

2. **Sequence vs List**: Use Sequence for covariant parameters to avoid "list is invariant" mypy errors.

3. **Timestamp Types**: YieldCardState expects float timestamp, not string. Convert datetime → epoch milliseconds.

## Architecture Diagram

```
                              ┌──────────────┐
                              │    Clock     │
                              │ (time source)│
                              └──────┬───────┘
                                     │ tick()
                    ┌────────────────┼────────────────┐
                    │                │                │
             ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
             │ PathBinding │  │ PathBinding │  │ PathBinding │
             │ (self.soul) │  │(world.agent)│  │   (...)     │
             └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
                    │                │                │
             ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
             │ SoulAdapter │  │AgentAdapter │  │YieldAdapter │
             └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │     ReactiveDashboardAdapter     │
                    │       (Signal<DashState>)        │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │       DashboardScreen            │
                    │     (renders live state)         │
                    └─────────────────────────────────┘
```

## Wave 6 Readiness

Wave 5 provides all the data plumbing needed for Wave 6: Interactive Behaviors.

The Clock + EventBus + Adapters form a reactive data flow pipeline. Wave 6 adds the input side: keyboard navigation, focus management, and user interactions.
