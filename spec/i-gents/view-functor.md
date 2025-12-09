# The View Functor: Widget Ontology

> The form reveals the function; the widget speaks the agent's truth.

---

## The Theory

Agents need visual representation. Rather than ad-hoc rendering, we define a **View Functor** that maps agents to contextually adaptive UI components deterministically.

```
View: Agent[A, B] → Widget[Agent[A, B]]
```

This is deterministic: the same agent always produces the same widget structure (though content varies with state).

---

## The View Functor

```python
class ViewFunctor:
    """
    Maps any agent to a contextually adaptive UI component.

    View: Agent[A, B] → Widget[Agent[A, B]]

    This is deterministic: the same agent always produces
    the same widget structure (though content varies with state).
    """

    def lift(self, agent: Agent[A, B], context: ViewContext) -> Widget:
        """
        Map agent to widget based on:
        - Agent's declared interface (A, B types)
        - Agent's credo/personality
        - View context (mobile, desktop, terminal, paper)
        - Interaction mode (observe, invoke, compose)
        """
        widget_type = self.ontology.classify(agent)
        return widget_type.render(agent, context)
```

---

## View Context

```python
@dataclass
class ViewContext:
    """Where and how the widget will be rendered."""
    medium: Literal["terminal", "browser", "mobile", "paper"]
    width: int              # Available characters/pixels
    height: int             # Available characters/pixels
    color: bool             # Color available?
    interactive: bool       # Can user interact?
    streaming: bool         # Can update in real-time?

    # Semantic context
    interaction_mode: Literal["observe", "invoke", "compose"]
    detail_level: Literal["minimal", "standard", "detailed"]

# Common contexts
TERMINAL_CONTEXT = ViewContext(
    medium="terminal",
    width=80,
    height=24,
    color=True,
    interactive=True,
    streaming=True,
    interaction_mode="invoke",
    detail_level="standard"
)

BROWSER_CONTEXT = ViewContext(
    medium="browser",
    width=1200,
    height=800,
    color=True,
    interactive=True,
    streaming=True,
    interaction_mode="observe",
    detail_level="detailed"
)
```

---

## The Widget Ontology

Widgets form a semiotics of agent-to-agent and agent-to-human communication:

| Widget Type | Agent Pattern | Visual Manifestation |
|-------------|---------------|----------------------|
| `GlyphWidget` | Any agent | Moon phase + letter (● A) |
| `CardWidget` | Agent with metrics | Bordered box with stats |
| `PageWidget` | Agent with history | Full document view |
| `StreamWidget` | Streaming agent | Live updating text |
| `GraphWidget` | Composed agents | Node-edge diagram |
| `FormWidget` | Agent awaiting input | Input fields + submit |
| `DialogWidget` | Messenger agent | Chat bubble interface |
| `GaugeWidget` | Metered agent | Progress/budget indicators |
| `TimelineWidget` | Narrative agent | Event sequence |

---

## Widget Protocol

```python
class Widget(Protocol):
    """Base widget protocol."""

    def render(self, context: ViewContext) -> str | HTML | bytes:
        """Render to appropriate format for context."""
        ...

    def accepts_input(self) -> bool:
        """Can this widget receive user input?"""
        ...

    def get_actions(self) -> list[WidgetAction]:
        """Available user actions."""
        ...

@dataclass
class WidgetAction:
    """An action the user can take on a widget."""
    name: str
    shortcut: str | None
    description: str
    handler: Callable
```

---

## Core Widget Types

### GlyphWidget (Minimal)

The simplest representation—a single character or symbol:

```python
class GlyphWidget(Widget):
    """
    Minimal agent representation.

    Format: [phase][letter]
    Examples: ● A (active A-gent), ○ K (dormant K-gent)
    """

    def render(self, context: ViewContext) -> str:
        phase = self.get_phase_glyph()
        letter = self.agent.genus[0].upper()
        return f"{phase} {letter}"

    def get_phase_glyph(self) -> str:
        match self.agent.state:
            case "active": return "●"
            case "dormant": return "○"
            case "error": return "✗"
            case "waiting": return "◐"
```

### CardWidget (Standard)

A bordered box with key information:

```python
class CardWidget(Widget):
    """
    Standard agent card with metrics.
    """

    def render(self, context: ViewContext) -> str:
        if context.medium == "terminal":
            return self.render_terminal(context)
        return self.render_html(context)

    def render_terminal(self, context: ViewContext) -> str:
        return f"""
┌─ {self.agent.name} ─────────────────────┐
│ Type: {self.agent.genus}                │
│ State: {self.agent.state}               │
│ Invocations: {self.agent.metrics.count} │
│ Last: {self.agent.metrics.last_invoke}  │
└─────────────────────────────────────────┘
"""
```

### StreamWidget (Real-time)

For streaming agents:

```python
class StreamWidget(Widget):
    """
    Live updating stream visualization.
    """

    def render(self, context: ViewContext) -> str:
        content = self.stream.accumulated
        cursor = "█" if not self.stream.done else ""

        if context.medium == "terminal":
            return f"{content}{cursor}"
        return f"<div class='stream'>{content}<span class='cursor'>{cursor}</span></div>"

    async def update_loop(self):
        """Continuously update as stream progresses."""
        async for chunk in self.stream:
            self.accumulated += chunk.delta
            yield self.render(self.context)
```

### GraphWidget (Composition)

For visualizing agent composition:

```python
class GraphWidget(Widget):
    """
    Node-edge diagram for composed agents.
    """

    def render(self, context: ViewContext) -> str:
        if context.medium == "terminal":
            return self.render_ascii()
        return self.render_svg()

    def render_ascii(self) -> str:
        # ASCII art composition graph
        return f"""
    ┌───┐     ┌───┐     ┌───┐
    │ A │ ──▶ │ B │ ──▶ │ C │
    └───┘     └───┘     └───┘
"""
```

---

## The Semiotics

Widgets are *signs* that communicate agent state:

| Sign | Signifier | Signified |
|------|-----------|-----------|
| ● | Filled circle | Agent is active |
| ○ | Empty circle | Agent is dormant |
| ◐ | Half circle | Agent is waiting |
| ✗ | Cross | Agent has error |
| ███░░ | Progress bar | Completion percentage |
| ⚡ | Lightning | Tension/conflict |
| █ | Streaming cursor | Output in progress |
| ↻ | Cycle | Agent is retrying |
| ◆ | Diamond | Decision point |
| ▶ | Arrow | Data flow direction |

---

## Context Adaptation

The same agent renders differently in different contexts:

```python
# Same agent, different contexts
agent = CodeReviewAgent()

# Terminal: Compact card
terminal_widget = ViewFunctor().lift(agent, TERMINAL_CONTEXT)
# ┌─ CodeReviewer ──────┐
# │ ● Active | 42 runs  │
# └─────────────────────┘

# Browser: Rich interactive card
browser_widget = ViewFunctor().lift(agent, BROWSER_CONTEXT)
# <div class="agent-card">
#   <h3>CodeReviewer</h3>
#   <div class="metrics">...</div>
#   <button>Invoke</button>
# </div>

# Mobile: Minimal glyph
mobile_widget = ViewFunctor().lift(agent, MOBILE_CONTEXT)
# ● C
```

---

## Determinism Guarantee

```python
# Same agent + same context = same widget structure
widget1 = ViewFunctor().lift(agent, ctx)
widget2 = ViewFunctor().lift(agent, ctx)
assert widget1.structure == widget2.structure

# Different context = different rendering, same semantics
terminal_widget = ViewFunctor().lift(agent, TERMINAL_CONTEXT)
browser_widget = ViewFunctor().lift(agent, BROWSER_CONTEXT)
assert terminal_widget.semantic_content == browser_widget.semantic_content
```

---

## Widget Composition

Widgets compose like agents:

```python
# Composed pipeline
pipeline = agent_a >> agent_b >> agent_c

# Composed widget (automatic)
pipeline_widget = GraphWidget(pipeline)

# Nested composition
outer_widget = CardWidget(
    agent=pipeline,
    children=[
        GlyphWidget(agent_a),
        GlyphWidget(agent_b),
        GlyphWidget(agent_c),
    ]
)
```

---

## Integration with Observable

Agents implementing `Observable` get richer widgets:

```python
@runtime_checkable
class Observable(Protocol):
    def render_state(self) -> Renderable:
        """Agent-provided state visualization."""
        ...

    def render_thought(self) -> Renderable:
        """Agent-provided thought visualization."""
        ...

class ViewFunctor:
    def lift(self, agent: Agent, context: ViewContext) -> Widget:
        if isinstance(agent, Observable):
            # Use agent's self-representation
            return CustomWidget(
                state=agent.render_state(),
                thought=agent.render_thought()
            )
        else:
            # Fall back to generic widget
            return self.default_widget(agent, context)
```

---

## Anti-Patterns

- **Ad-hoc rendering per agent type**: Use the ontology
- **Widgets that lie about agent state**: Truth is paramount
- **Context-unaware rendering**: Check the medium
- **Non-deterministic widget selection**: Same input → same output
- **Ignoring Observable protocol**: Let agents self-represent

---

*Zen Principle: The form reveals the function; the widget speaks the agent's truth.*

---

## See Also

- [i-gents/README.md](README.md) - I-gent overview
- [messenger.md](messenger.md) - Streaming for StreamWidget
- [anatomy.md](../anatomy.md) - Observable protocol
- [w-gents/stigmergy.md](../w-gents/stigmergy.md) - Pheromone map visualization
