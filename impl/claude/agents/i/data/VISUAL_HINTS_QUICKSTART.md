# Visual Hints - Quick Reference

A quick reference for using the Visual Hint Protocol in kgents.

---

## For Agent Developers

### Emit a Simple Text Hint

```python
from impl.claude.agents.i.data import VisualHint

hint = VisualHint(
    type="text",
    data={"text": "Hello from my agent!"},
    position="footer",
    agent_id=self.id,
)
# yield hint or emit to stream
```

### Emit a Table (B-gent style)

```python
hint = VisualHint(
    type="table",
    data={
        "Assets": 1000,
        "Liabilities": 300,
        "Net Worth": 700,
    },
    position="sidebar",
    priority=10,
    agent_id=self.id,
)
```

### Emit a Density Field (K-gent style)

```python
hint = VisualHint(
    type="density",
    data={
        "activity": 0.75,
        "phase": "ACTIVE",
        "name": "K",
    },
    position="main",
    priority=20,
    agent_id=self.id,
)
```

### Emit a Sparkline (Activity History)

```python
hint = VisualHint(
    type="sparkline",
    data={
        "values": [0.3, 0.5, 0.7, 0.8, 0.75],
        "width": 20,
    },
    position="footer",
    agent_id=self.id,
)
```

### Emit a Graph (Y-gent style)

```python
hint = VisualHint(
    type="graph",
    data={
        "nodes": ["Agent-A", "Agent-B", "Agent-C"],
        "edges": [("Agent-A", "Agent-B"), ("Agent-B", "Agent-C")],
    },
    position="main",
    priority=15,
    agent_id=self.id,
)
```

---

## For UI Developers

### Use HintContainer in a Screen

```python
from impl.claude.agents.i.widgets import HintContainer
from textual.app import ComposeResult

class MyScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield HintContainer(id="agent-hints")
        yield Footer()
```

### Add Hints to Container

```python
container = self.query_one("#agent-hints", HintContainer)
container.add_hint(hint)
```

### Update All Hints at Once

```python
container.hints = [hint1, hint2, hint3]
# Container auto-renders
```

### Remove Hints from Specific Agent

```python
container.remove_hints_by_agent("agent-123")
```

### Clear All Hints

```python
container.clear_hints()
```

---

## Hint Types Reference

| Type | Description | Data Format |
|------|-------------|-------------|
| `"text"` | Simple text | `{"text": str}` |
| `"table"` | Key-value table | `{key: value, ...}` or `{"columns": [...], "rows": [[...]]}` |
| `"density"` | Density field | `{"activity": float, "phase": str, "name": str}` |
| `"sparkline"` | Activity graph | `{"values": [float, ...], "width": int}` |
| `"graph"` | Node-edge graph | `{"nodes": [...], "edges": [(a, b), ...]}` |
| `"loom"` | Cognitive tree | `{"tree": CognitiveTree, "current_id": str}` |
| `"custom"` | Custom widget | `{...}` (agent-defined) |

---

## Positions Reference

| Position | Description | Layout |
|----------|-------------|--------|
| `"main"` | Main content | 75% width, left side |
| `"sidebar"` | Right panel | 25% width, right side |
| `"overlay"` | Modal | Layered on top, centered |
| `"footer"` | Footer | Docked bottom, full width |

---

## Priority System

- **Higher values render first** within each position
- Default priority: `0`
- Typical ranges:
  - `20+`: Critical/primary content
  - `10-19`: Important content
  - `1-9`: Supporting content
  - `0`: Default content
  - `<0`: Low-priority content

---

## Custom Hint Types

### Register a Custom Factory

```python
from impl.claude.agents.i.data import get_hint_registry
from textual.widgets import Static

def my_custom_factory(hint: VisualHint) -> Widget:
    return Static(f"Custom: {hint.data}")

registry = get_hint_registry()
registry.register("my_type", my_custom_factory)
```

### Use Custom Hint Type

```python
hint = VisualHint(
    type="custom",  # Use "custom" for validation
    data={"widget_type": "my_type", ...},
    position="main",
    agent_id=self.id,
)
# After emitting, override type for rendering
hint.type = "my_type"
```

---

## Common Patterns

### Multi-Zone Layout

```python
hints = [
    # Main: Primary visualization
    VisualHint(type="density", data={...}, position="main", priority=20),

    # Sidebar: Supporting data
    VisualHint(type="table", data={...}, position="sidebar", priority=10),

    # Footer: Activity history
    VisualHint(type="sparkline", data={...}, position="footer", priority=5),
]

container.hints = hints
```

### Dynamic Updates

```python
# Update hint stream as agent state changes
async def update_hints(self):
    while running:
        current_hints = self.generate_current_hints()
        container.hints = current_hints
        await asyncio.sleep(1.0)
```

### Agent-Specific Filtering

```python
# Get all hints from K-gent
kgent_hints = container.get_hints_by_agent("k-gent-1")

# Remove all hints from stopped agent
container.remove_hints_by_agent("stopped-agent-id")
```

---

## Validation

Hints are validated at construction:

```python
# ✅ Valid
hint = VisualHint(type="text", data={"text": "OK"})

# ❌ Invalid type
hint = VisualHint(type="invalid_type", data={})
# Raises: ValueError: Unknown hint type

# ❌ Invalid position
hint = VisualHint(type="text", position="invalid", data={})
# Raises: ValueError: Unknown position

# ❌ Invalid data type
hint = VisualHint(type="text", data="not a dict")
# Raises: TypeError: data must be dict
```

---

## Testing

### Test Hint Creation

```python
from impl.claude.agents.i.data import VisualHint

def test_my_hint():
    hint = VisualHint(
        type="table",
        data={"key": "value"},
        position="sidebar",
    )
    assert hint.type == "table"
    assert hint.data["key"] == "value"
```

### Test Hint Rendering

```python
from impl.claude.agents.i.data import get_hint_registry

def test_rendering():
    registry = get_hint_registry()
    hint = VisualHint(type="text", data={"text": "Test"})
    widget = registry.render(hint)
    assert widget is not None
```

---

## Examples

See `/Users/kentgang/git/kgents/impl/claude/agents/i/data/flux_hint_integration.py` for comprehensive examples including:

- B-gent balance sheet tables
- Y-gent topology graphs
- K-gent cognitive state
- Multi-agent orchestration
- FluxAgent integration patterns

---

## Philosophy

> *"The I-gent is not a dashboard—it's a BROWSER that renders agent-emitted layout hints."*

Agents define their representation. The framework listens and renders. This is the heterarchical principle in action.

---

**Happy hinting!**
