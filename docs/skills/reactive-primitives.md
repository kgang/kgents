# Skill: Reactive Primitives Pattern

> Build target-agnostic reactive UIs using Signal, Computed, and Effect.

**Difficulty**: Easy-Medium
**Prerequisites**: Python dataclasses, callbacks
**Files**: `impl/claude/agents/i/reactive/signal.py`
**References**: `agents/i/reactive/_tests/test_wave1_stress.py`, `agents/i/reactive/_tests/test_time_travel.py`

---

## Overview

Signal, Computed, and Effect form the reactive foundation for kgents visualization.
These primitives are target-agnostic: the same code renders to CLI, TUI, marimo, or custom targets.

| Primitive | Purpose | Equivalent |
|-----------|---------|------------|
| `Signal[T]` | Observable state | React `useState`, Solid `createSignal` |
| `Computed[T]` | Derived state (lazy) | React `useMemo`, Solid `createMemo` |
| `Effect` | Side effects | React `useEffect` |

---

## Signal[T]: Observable State

A Signal holds a value and notifies subscribers when it changes.

### Create a Signal

```python
from agents.i.reactive.signal import Signal

count = Signal.of(0)
name = Signal.of("kgent")
items = Signal.of(["a", "b", "c"])
```

### Read and Update

```python
# Read (immutable access)
print(count.value)  # 0

# Set (notifies if changed)
count.set(5)

# Update via function
count.update(lambda x: x + 1)  # Now 6
```

### Subscribe to Changes

```python
def on_change(new_value: int) -> None:
    print(f"Count changed to: {new_value}")

unsub = count.subscribe(on_change)
count.set(10)  # Prints: "Count changed to: 10"

unsub()  # Stop receiving updates
```

### Time Travel (Snapshot/Restore)

Signals support checkpointing for branching exploration:

```python
from agents.i.reactive.signal import Signal, Snapshot

sig = Signal.of(42)
snap = sig.snapshot()  # Capture current state

sig.set(100)  # Explore different path
sig.set(200)
print(sig.value)  # 200

sig.restore(snap)  # Return to checkpoint
print(sig.value)  # 42
```

**Key**: Restore notifies subscribers if value changes, but generation continues forward.

---

## Computed[T]: Derived State

Computed values auto-update when dependencies change. They're lazy (only recompute on access).

### Create from Signal.map()

```python
count = Signal.of(5)
doubled = count.map(lambda x: x * 2)

print(doubled.value)  # 10
count.set(10)
print(doubled.value)  # 20 (auto-updated)
```

### Create with Multiple Sources

```python
from agents.i.reactive.signal import Computed

first = Signal.of("Ada")
last = Signal.of("Lovelace")

full_name = Computed.of(
    compute=lambda: f"{first.value} {last.value}",
    sources=[first, last],
)

print(full_name.value)  # "Ada Lovelace"
first.set("Grace")
print(full_name.value)  # "Grace Lovelace"
```

### Chain Computed Values

```python
count = Signal.of(1)
doubled = count.map(lambda x: x * 2)
message = doubled.map(lambda x: f"Result: {x}")

print(message.value)  # "Result: 2"
count.set(5)
print(message.value)  # "Result: 10"
```

### Cleanup

```python
computed.dispose()  # Unsubscribe from all sources
```

---

## Effect: Side Effects

Effects bridge reactive state and the outside world (logging, network, DOM).

### Create an Effect

```python
from agents.i.reactive.signal import Effect

count = Signal.of(0)

def log_count() -> None:
    print(f"Count is now: {count.value}")
    return None  # No cleanup needed

effect = Effect.of(fn=log_count, sources=[count])
effect.run()  # Prints: "Count is now: 0"

count.set(5)  # Effect is invalidated
effect.run_if_dirty()  # Prints: "Count is now: 5"
```

### Effect with Cleanup

```python
def setup_timer() -> Callable[[], None]:
    timer_id = start_timer()

    def cleanup() -> None:
        stop_timer(timer_id)

    return cleanup

effect = Effect.of(fn=setup_timer, sources=[interval_signal])
effect.run()  # Starts timer

interval_signal.set(1000)  # Change interval
effect.run()  # Cleanup called first, then new timer starts

effect.dispose()  # Final cleanup
```

### Check Dirty State

```python
if effect.dirty:
    effect.run()
```

---

## Snapshot Internals

The `Snapshot[T]` captures:
- `value`: The captured value
- `timestamp`: Monotonic time when captured
- `generation`: How many mutations had occurred

```python
snap = sig.snapshot()
print(snap.value)       # The value
print(snap.timestamp)   # When captured
print(snap.generation)  # Mutation count at capture
```

**Invariant**: Generation is monotonically increasing. Setting the same value does not increment generation.

---

## Patterns

### Branching Exploration

```python
def explore_options(base_signal: Signal[int]) -> tuple[int, int]:
    checkpoint = base_signal.snapshot()

    # Path A
    base_signal.set(1)
    base_signal.update(lambda x: x + 10)
    path_a = base_signal.value  # 11

    # Return and try Path B
    base_signal.restore(checkpoint)
    base_signal.set(2)
    base_signal.update(lambda x: x * 10)
    path_b = base_signal.value  # 20

    return path_a, path_b
```

### Reactive Counter Widget

```python
class Counter:
    def __init__(self) -> None:
        self._count = Signal.of(0)
        self._display = self._count.map(lambda c: f"Count: {c}")

    def increment(self) -> None:
        self._count.update(lambda x: x + 1)

    @property
    def text(self) -> str:
        return self._display.value
```

### Multi-Source Aggregation

```python
def create_dashboard(
    cpu: Signal[float],
    memory: Signal[float],
    disk: Signal[float],
) -> Computed[str]:
    return Computed.of(
        compute=lambda: f"CPU: {cpu.value}% | Mem: {memory.value}% | Disk: {disk.value}%",
        sources=[cpu, memory, disk],
    )
```

---

## Verification

```bash
# Run reactive primitive tests
cd impl/claude
uv run pytest agents/i/reactive/_tests/test_time_travel.py -v

# Run stress tests
uv run pytest agents/i/reactive/_tests/test_wave1_stress.py -v

# Run all reactive tests
uv run pytest agents/i/reactive/_tests/ -v
```

---

## Common Pitfalls

### 1. Mutating Signal Value Directly

**Wrong**:
```python
sig = Signal.of([1, 2, 3])
sig.value.append(4)  # Subscribers not notified!
```

**Right**:
```python
sig.set([*sig.value, 4])  # New list, triggers notification
```

### 2. Forgetting to Dispose

**Risk**: Memory leaks from dangling subscriptions.

**Fix**: Always dispose Computed and Effect when done:
```python
computed.dispose()
effect.dispose()
```

### 3. Circular Dependencies

**Risk**: Stack overflow if Computed depends on itself.

**Fix**: Design acyclic dependency graphs.

---

## Related Skills

- [modal-scope-branching](modal-scope-branching.md) - Git-like context exploration
- [turn-projectors](turn-projectors.md) - Multi-target rendering
- [test-patterns](test-patterns.md) - Testing reactive code

---

## Source Reference

`impl/claude/agents/i/reactive/signal.py:60-343`

---

*Skill created: 2025-12-14 | Wave 1 EDUCATE Phase*
