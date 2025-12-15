# Skill: Marimo Notebook (Projection Target)

> *"Developers design agents. marimo is a battery, not a burden."*

## Overview

**This skill is for framework developers, not agent developers.**

Agent developers should NOT concern themselves with marimo-specific details. They design state machines and widgets; the Projection Protocol handles the rest. See `spec/protocols/projection.md`.

If you're designing an agent: define your state, extend `KgentsWidget`, and call `.to_marimo()`. That's it.

This skill documents marimo cell semantics for those extending the projection layer or building custom notebook integrations.

---

## The Projection Integration

kgents widgets project to marimo via the `to_marimo()` method:

```python
# Agent developer writes:
widget = TownWidget(town_state)

# And gets marimo output for free:
widget.to_marimo()  # → HTML/anywidget for notebook display
```

The marimo target is one of several (CLI, TUI, JSON, SSE) defined in the Projection Protocol.

---

## Cell Semantics (Framework Details)

Marimo notebooks use a reactive dataflow model where cells automatically re-execute when their dependencies change. Understanding how cell outputs and return values work is critical for building working notebooks.

## The Core Rule

**"The last expression of a cell is its visual output, rendered above the cell."**

This is the most important rule in marimo. Whatever expression evaluates last (before any `return` statement) becomes the cell's displayed output.

## Cell Anatomy: Display vs Export

### Two Distinct Concepts

| Concept | Mechanism | Purpose |
|---------|-----------|---------|
| **Display** | Last expression before `return` | What the user sees |
| **Export** | `return (var,)` tuple | Variables for other cells |

### The Common Mistake

```python
# ❌ WRONG - displays docstring, not vstack!
@app.cell
def my_cell(mo):
    """This docstring becomes the last expression before return!"""
    return mo.vstack([mo.md("Hello")])  # Exported but not displayed
```

In this cell:
1. The docstring `"""..."""` is an expression statement
2. The `return` exports the vstack
3. But the **last expression** before return is the docstring
4. Result: The docstring text is displayed instead of the UI!

### The Correct Patterns

**Pattern 1: Pure Display Cell (no export needed)**
```python
@app.cell
def display_output(mo, data):
    """Documentation for this cell."""
    # Do some computation
    result = process(data)

    # Last expression = displayed output
    mo.vstack([
        mo.md("# Results"),
        mo.md(f"Value: {result}")
    ])
```

**Pattern 2: Export AND Display**
```python
@app.cell
def compute_and_show(mo, data):
    """Compute result and display it."""
    result = process(data)

    # Create the UI
    ui = mo.vstack([mo.md(f"Result: {result}")])

    # Display it (last expression before return)
    ui

    # Also export for other cells
    return (result, ui)
```

**Pattern 3: Pure Compute Cell (no display)**
```python
@app.cell
def compute_only(data):
    """Pure computation, no UI."""
    result = expensive_calculation(data)
    return (result,)  # Only exports, displays nothing
```

## The Docstring Trap

Python docstrings are expression statements. They execute and their value (the string) is discarded—BUT in marimo, if it's the last expression before `return`, it becomes the output!

```python
# ❌ This displays "Cell documentation" not the button!
@app.cell
def broken(mo):
    """Cell documentation"""
    return mo.ui.button(label="Click me")

# ✅ Fixed - make button the last expression
@app.cell
def fixed(mo):
    """Cell documentation"""
    button = mo.ui.button(label="Click me")
    button  # Last expression = displayed
    return (button,)  # Also export for reactivity
```

## Marimo Cell Return Semantics

### Return Tuple Format

```python
return (var1, var2, var3)  # Export multiple variables
return (single_var,)       # Export one variable (note the comma!)
return ()                  # Export nothing (side-effect cell)
```

### What Return Does NOT Do

- Return does **not** display the value
- Return does **not** make the value the cell output
- Return **only** exports variables to the cell graph

### Empty Return for Side-Effect Cells

```python
@app.cell
def handle_click(button, state):
    """Handle button click - pure side effect."""
    if button.value:
        state.increment()
    return ()  # No export, no display
```

## Cell Types Pattern

### 1. Import Cells
```python
@app.cell
def imports():
    import marimo as mo
    import pandas as pd
    return mo, pd
```

### 2. Data/State Cells
```python
@app.cell
def create_data(pd):
    df = pd.DataFrame({"x": [1,2,3], "y": [4,5,6]})
    return (df,)
```

### 3. UI Component Cells
```python
@app.cell
def controls(mo):
    slider = mo.ui.slider(0, 100, value=50)
    button = mo.ui.button(label="Run")
    return slider, button
```

### 4. Display Cells (compose and show)
```python
@app.cell
def main_display(mo, slider, button, chart):
    """Main dashboard layout."""
    mo.vstack([
        mo.md("# Dashboard"),
        mo.hstack([slider, button]),
        chart
    ])
    # No return - pure display, nothing to export
```

### 5. Handler Cells (react to UI)
```python
@app.cell
def handle_slider(slider, data):
    """Update data based on slider."""
    filtered = data[data.value > slider.value]
    return (filtered,)
```

## Reactive Dependencies

Marimo tracks dependencies by analyzing which variables a cell:
- **References** (reads from other cells)
- **Defines** (exports via return)

```python
@app.cell
def cell_a():
    x = 10
    return (x,)

@app.cell
def cell_b(x):  # Depends on cell_a's x
    y = x * 2
    return (y,)

@app.cell
def cell_c(x, y):  # Depends on both
    mo.md(f"x={x}, y={y}")  # Display
```

## Common Pitfalls

### 1. Docstring as Output (The Bug This Skill Addresses!)
```python
# ❌ Displays docstring
@app.cell
def bad(mo):
    """Main layout."""
    return mo.vstack([...])

# ✅ Displays vstack
@app.cell
def good(mo):
    """Main layout."""
    mo.vstack([...])  # Last expression
```

### 2. Returning Non-Tuple
```python
# ❌ Unclear semantics
return mo.vstack([...])

# ✅ Explicit tuple
return (my_vstack,)
```

### 3. Forgetting Comma in Single-Element Tuple
```python
# ❌ Not a tuple!
return (result)

# ✅ Single-element tuple
return (result,)
```

### 4. Console Output vs Cell Output
```python
# ❌ Print goes to console, not cell output
@app.cell
def bad():
    print("Hello")  # Goes to console below cell

# ✅ Use mo.md or mo.output for cell output
@app.cell
def good(mo):
    mo.md("Hello")  # Cell output
```

### 5. Mutations Across Cells
```python
# ❌ Marimo doesn't track mutations
@app.cell
def cell_a():
    data = []
    return (data,)

@app.cell
def cell_b(data):
    data.append(1)  # Mutation not tracked!
    return ()

# ✅ Create new values instead
@app.cell
def cell_b(data):
    new_data = data + [1]  # New value
    return (new_data,)
```

## Layout Patterns

### Dashboard Layout
```python
@app.cell
def dashboard(mo, controls_ui, main_chart, sidebar_data):
    """Full dashboard composition."""
    mo.hstack([
        mo.vstack([
            mo.md("# Dashboard"),
            controls_ui,
            main_chart
        ], gap=2),
        mo.sidebar([
            mo.md("## Info"),
            sidebar_data
        ])
    ])
```

### Conditional Display
```python
@app.cell
def conditional(mo, show_details, data):
    if show_details.value:
        mo.vstack([
            mo.md("## Details"),
            mo.md(f"```{data}```")
        ])
    else:
        mo.md("_Click to show details_")
```

## Debugging Tips

1. **Check last expression**: What's the last line before `return`?
2. **Isolate the cell**: Comment out return, see what displays
3. **Use mo.output.replace()**: For imperative debugging
4. **Check marimo check**: Run `marimo check notebook.py`

## Resources

- [Marimo Outputs Guide](https://docs.marimo.io/guides/outputs/)
- [Marimo Reactivity](https://docs.marimo.io/guides/reactivity.html)
- [Marimo Best Practices](https://docs.marimo.io/guides/best_practices.html)
- [Marimo Layouts API](https://docs.marimo.io/api/layouts/)

---

## Integration with Projection Protocol

The marimo integration is ONE target in the broader Projection Protocol.

### For Agent Developers

You don't need this skill. Use the projection layer:

```python
from agents.i.reactive import AgentCardWidget, AgentCardState

# Define state
state = AgentCardState(name="My Agent", phase="active", activity=(0.3, 0.7), capability=0.85)

# Create widget
widget = AgentCardWidget(state)

# Project to ANY target (marimo is just one)
widget.to_cli()      # Terminal output
widget.to_marimo()   # Notebook output
widget.to_json()     # API response
```

### For Framework Developers

When extending the marimo projection, implement `to_marimo()` in your widget:

```python
class MyWidget(KgentsWidget[MyState]):
    def project(self, target: RenderTarget) -> Any:
        s = self.state.value
        match target:
            case RenderTarget.MARIMO:
                # Return HTML for mo.Html() or anywidget instance
                return f'<div class="my-widget">{s.content}</div>'
            case RenderTarget.CLI:
                return f"[{s.label}] {s.content}"
            case _:
                return str(s)
```

### The Key Insight

From `meta.md`:
> marimo LogosCell pattern IS AgenteseBridge pattern—direct mapping, no adapter layer needed

This means AGENTESE paths work directly in marimo cells without translation.

---

## See Also

- `spec/protocols/projection.md` — The Projection Protocol specification
- `impl/claude/agents/i/reactive/` — Widget implementation
- `impl/claude/protocols/api/turn.py` — Turn projections (to_marimo, to_cli, etc.)

---

*"Export your data. Display your story. Never confuse the two."*
