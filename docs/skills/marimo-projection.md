# Skill: marimo Projection Patterns

> *"State is a lie. There is only the getter function."*

**Difficulty**: Medium
**Prerequisites**: Python closures, reactive programming basics
**Files**: `demos/agent_explorer.py`, `demos/foundry_showcase.py`
**References**: [marimo State docs](https://docs.marimo.io/api/state/), [marimo Button docs](https://docs.marimo.io/api/inputs/button/)

---

## Overview

marimo is the **interactive exploration target** in the Alethic Architecture. It projects agents as reactive notebooks with real-time state visualization. However, Python's closure semantics create subtle bugs when combining `mo.state` with UI callbacks.

**Key insight**: `mo.state()` returns getter/setter FUNCTIONS. You must CALL the getter to get the value.

---

## The Getter Function Trap

### Understanding mo.state()

```python
# mo.state() returns a tuple of (getter_function, setter_function)
get_count, set_count = mo.state(0)

# WRONG: get_count is a function, not the value!
value = get_count  # This is the function object

# RIGHT: Call the getter to get the value
value = get_count()  # This is the actual value (0)
```

### The Bug

```python
@app.cell
def _(mo, poly_state, selected_poly, set_poly_state):
    _current = poly_state  # BUG: poly_state is a GETTER FUNCTION, not the value!

    def _make_button(cmd):
        def _on_click(_):
            # _current is the getter function, not the state value
            _new_state, _output = selected_poly.invoke(_current, cmd)  # FAILS!
            set_poly_state(_new_state)
        return mo.ui.button(label=cmd, on_click=_on_click)
```

**Error**: `ValueError: Invalid state: <marimo._runtime.state.State object at 0x...>`

### The Fix: Call the Getter + Capture Value

```python
@app.cell
def _(mo, poly_state, selected_poly, set_poly_state):
    # CALL the getter to get the actual value
    _current = poly_state()  # <-- Note the ()!

    # Capture the value via function parameters (not closure)
    def make_handler(state_value, command):
        def handler(_):
            new_state, output = selected_poly.invoke(state_value, command)
            set_poly_state(new_state)
        return handler

    buttons = [
        mo.ui.button(label=cmd, on_change=make_handler(_current, cmd))
        for cmd in valid_inputs
    ]
```

**Two fixes applied**:
1. Call `poly_state()` to get the value, not the getter function
2. Pass value as function parameter to capture it (avoids late-binding closure issues)

---

## on_click vs on_change

### on_click: Value Transformation

```python
# on_click receives current value, returns NEW value
button = mo.ui.button(
    value=0,
    on_click=lambda value: value + 1,  # Increment
    label="Count"
)
# button.value is now the counter
```

### on_change: Side Effects

```python
# on_change receives value, triggers side effects (state updates)
get_state, set_state = mo.state("initial")

button = mo.ui.button(
    label="Reset",
    on_change=lambda _: set_state("reset"),  # Side effect
)
```

**Rule**: Use `on_change` for buttons that update `mo.state`. Use `on_click` for buttons that transform their own value.

---

## Dynamic UI Elements

### The Problem

UI elements created dynamically (in loops, list comprehensions) don't fire callbacks unless wrapped:

```python
# BAD: Callbacks won't fire!
mo.vstack([
    mo.ui.button(on_change=lambda _: print(i))
    for i in range(10)
])
```

### The Fix: mo.ui.array

```python
# GOOD: Wrap in mo.ui.array
buttons = mo.ui.array([
    mo.ui.button(
        label=f"Button {i}",
        on_change=lambda _, i=i: print(i)  # Note: i=i binding!
    )
    for i in range(10)
])
mo.vstack(buttons)
```

**Rule**: Dynamic UI elements require `mo.ui.array`, `mo.ui.dictionary`, or `mo.ui.batch`.

---

## Patterns

### Pattern 1: State Machine with Buttons

```python
@app.cell
def _(mo):
    get_state, set_state = mo.state("idle")
    get_history, set_history = mo.state([])
    return get_state, set_state, get_history, set_history

@app.cell
def _(mo, get_state, set_state, set_history):
    # CALL the getter to get the actual value
    current = get_state()

    def make_transition(cmd, from_state):
        # Capture from_state as parameter (not closure)
        def handler(_):
            next_state = {"idle": "active", "active": "done", "done": "idle"}[from_state]
            set_state(next_state)
            set_history(lambda h: h + [(from_state, cmd, next_state)])
        return handler

    return mo.hstack([
        mo.ui.button(label="NEXT", on_change=make_transition("next", current)),
        mo.callout(mo.md(f"State: **{current}**"), kind="info"),
    ])
```

### Pattern 2: PolyAgent Explorer

```python
@app.cell
def _(mo, poly_agent):
    get_state, set_state = mo.state(poly_agent.initial_state)
    return get_state, set_state

@app.cell
def _(mo, poly_agent, get_state, set_state):
    # CALL getter to get value
    current = get_state()
    valid_inputs = list(poly_agent.directions(current))

    # Factory function captures value via parameters
    def make_handler(state_value, cmd):
        def on_change(_):
            new_state, output = poly_agent.invoke(state_value, cmd)
            set_state(new_state)
        return on_change

    buttons = [
        mo.ui.button(label=cmd.upper(), on_change=make_handler(current, cmd))
        for cmd in valid_inputs
    ]
    return mo.vstack([
        mo.md(f"**State**: `{current}`"),
        mo.hstack(buttons, gap=1),
    ])
```

### Pattern 3: Synchronized Sliders

```python
@app.cell
def _(mo):
    get_value, set_value = mo.state(50)
    return get_value, set_value

@app.cell
def _(mo, get_value, set_value):
    # CALL getter for initial value
    current = get_value()

    # Both sliders stay in sync
    slider1 = mo.ui.slider(0, 100, value=current, on_change=set_value)
    slider2 = mo.ui.slider(0, 100, value=current, on_change=set_value)

    mo.vstack([slider1, slider2, mo.md(f"Value: {current}")])
```

---

## Anti-Patterns

### Forgetting to Call the Getter

```python
# BAD: get_state is a function, not the value!
current = get_state
invoke(current, cmd)  # Passes function object, not value

# GOOD: Call the getter
current = get_state()
invoke(current, cmd)  # Passes the actual value
```

### Loop Variable Capture

```python
# BAD: Every callback prints 9 (last value of i)
buttons = [mo.ui.button(on_change=lambda _: print(i)) for i in range(10)]

# GOOD: Bind i explicitly via default argument
buttons = [mo.ui.button(on_change=lambda _, i=i: print(i)) for i in range(10)]

# BETTER: Use factory function
def make_handler(index):
    return lambda _: print(index)
buttons = [mo.ui.button(on_change=make_handler(i)) for i in range(10)]
```

### Getter in Closure (Double Trap)

```python
# BAD: Captures getter function AND has late-binding issue
current = get_state  # Wrong: didn't call getter
def on_click(_):
    invoke(current, cmd)  # current is a function!

# ALSO BAD: Called getter but closure captures variable reference
current = get_state()
def on_click(_):
    invoke(current, cmd)  # current may be stale when callback fires

# GOOD: Call getter AND pass value as parameter
current = get_state()
def make_handler(state_value, command):
    def handler(_):
        invoke(state_value, command)
    return handler
button = mo.ui.button(on_change=make_handler(current, cmd))
```

### Using on_click for State Updates

```python
# BAD: on_click is for value transformation
mo.ui.button(on_click=lambda _: set_state("new"))

# GOOD: on_change is for side effects
mo.ui.button(on_change=lambda _: set_state("new"))
```

---

## Debugging Checklist

When marimo callbacks fail with `<State object>` errors:

- [ ] **Did you CALL the getter?** `get_state()` not `get_state`
- [ ] **Did you capture the value?** Pass to factory function, don't close over variable
- [ ] Are loop variables captured with default argument binding (`i=i`)?
- [ ] Are dynamic buttons wrapped in `mo.ui.array`?
- [ ] Using `on_change` (not `on_click`) for state updates?
- [ ] Is the button bound to a global variable (not inline)?

### Quick Diagnostic

```python
# Add this to debug State object issues
print(f"Type: {type(my_var)}, Value: {my_var}")

# If you see: Type: <class 'function'>, Value: <function ...>
# → You forgot to call the getter: use my_var() instead of my_var

# If you see: Type: <class 'marimo._runtime.state.State'>
# → You're in a closure capturing the State wrapper
# → Pass the value as a function parameter instead
```

---

## marimo + kgents Integration

| kgents Concept | marimo Projection |
|----------------|-------------------|
| PolyAgent state | `mo.state()` tuple |
| Valid inputs | Button per `directions(state)` |
| Transition | `on_change` → `invoke()` → `set_state()` |
| History trace | Append to `mo.state([])` list |
| Halo capabilities | `mo.callout()` badges |

---

## Related Skills

- [projection-target](projection-target.md) — Custom projection targets (marimo is fidelity 0.8)
- [polynomial-agent](polynomial-agent.md) — PolyAgent state machine patterns
- [elastic-ui-patterns](elastic-ui-patterns.md) — Density-aware UI (applies to marimo widgets)

---

## Source Reference

- `demos/agent_explorer.py` — Interactive PolyAgent explorer
- `demos/foundry_showcase.py` — Foundry synthesis demo
- [marimo docs: State](https://docs.marimo.io/api/state/)
- [marimo docs: Button](https://docs.marimo.io/api/inputs/button/)
- [marimo docs: Recipes](https://docs.marimo.io/recipes/)

---

*Skill created: 2025-12-21 | Lesson learned from agent_explorer.py late-binding bug*
