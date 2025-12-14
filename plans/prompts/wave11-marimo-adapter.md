---
path: reactive-substrate/wave11
status: pending
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [wave12-unified-demo, agent-observability-notebooks]
session_notes: |
  Wave 11: Marimo Adapter - Bridge reactive widgets to marimo/Jupyter notebooks.
  Crown Jewel: Full 11-phase ceremony. Agent observability meets computational notebooks.
  Research: anywidget (ESM+traitlets), marimo (DAG reactivity), OpenTelemetry traces.
phase_ledger:
  PLAN: complete  # This prompt
  RESEARCH: complete  # anywidget API, marimo integration, agent observability patterns
  DEVELOP: pending  # Contract definitions
  STRATEGIZE: touched  # Sequencing planned below
  CROSS-SYNERGIZE: touched  # OpenTelemetry, Langfuse, dataflow visualization
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending  # Demo notebook, widget gallery
  MEASURE: pending  # Performance metrics, widget render times
  REFLECT: pending
entropy:
  planned: 0.12
  spent: 0.00
  sip_allowed: true
---

# ⟿[IMPLEMENT] Reactive Substrate Wave 11 — Marimo Adapter

> *"The same widgets, now in notebooks. Agents become observable. Dataflow becomes visible."*

---

## Quick Wield

```
ATTACH /hydrate
handles: world.reactive.marimo.manifest[wave=11]; void.entropy.sip[amount=0.08]
mission: Bridge KgentsWidget → anywidget for marimo/Jupyter. Enable agent observability in notebooks.
ledger: IMPLEMENT=in_progress | entropy.spent += 0.08
actions: MarimoAdapter (anywidget.AnyWidget), TraitletsBridge, NotebookTheme, AgentTraceWidget, demo notebook
exit: 1400+ reactive tests | marimo notebook running | ⟿[QA] or ⟂[BLOCKED]
```

---

## Vision: Why This Matters

### The Convergence

Three powerful forces are converging in 2024-2025:

1. **Reactive Notebooks**: [marimo](https://marimo.io/) represents notebooks as directed acyclic graphs (DAGs). Run a cell, and dependent cells automatically re-execute. This is the same reactive model as kgents `Signal[T]`.

2. **Agent Observability**: The rise of AI agents demands new observability tools. [Langfuse](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse), [OpenTelemetry](https://opentelemetry.io/blog/2025/ai-agent-observability/), and Datadog LLM Observability provide traces, but visualization remains primitive.

3. **anywidget Standard**: [anywidget](https://anywidget.dev/) has become the de facto standard for custom Jupyter widgets—endorsed by [marimo](https://docs.marimo.io/api/inputs/anywidget/), used by Altair, and praised for its AI-friendly vanilla JavaScript approach.

### The Opportunity

**kgents widgets are already agent-aware.** `AgentCardWidget` knows about phases, activity sparklines, capability bars, and entropy-based visual distortion. When we bridge these to notebooks:

- **Data scientists can observe agents** in their natural environment
- **Agent developers can debug** with interactive, reactive visualizations
- **The boundary between "agent code" and "notebook code" dissolves**

This is not just "widgets in notebooks." This is **agent observability becoming a first-class citizen of the data science workflow**.

---

## Research Synthesis

### anywidget Architecture

From [anywidget documentation](https://anywidget.dev/en/getting-started/) and [Jupyter Widgets: The Good Parts](https://anywidget.dev/en/jupyter-widgets-the-good-parts/):

```python
import anywidget
import traitlets

class CounterWidget(anywidget.AnyWidget):
    # ECMAScript Module (ESM) - runs in browser
    _esm = """
    function render({ model, el }) {
        let button = document.createElement("button");
        button.innerHTML = `count is ${model.get("value")}`;
        button.addEventListener("click", () => {
            model.set("value", model.get("value") + 1);
            model.save_changes();  // Persist to Python
        });
        model.on("change:value", () => {
            button.innerHTML = `count is ${model.get("value")}`;
        });
        el.appendChild(button);
    }
    export default { render };
    """

    # Traitlet synced between Python ↔ JavaScript
    value = traitlets.Int(0).tag(sync=True)
```

**Key insight**: anywidget's `model.get()` / `model.set()` / `model.on("change:...")` pattern maps directly to our `Signal[T].value` / `Signal[T].set()` / `Signal[T].subscribe()`.

### marimo Integration

From [marimo anywidget docs](https://docs.marimo.io/api/inputs/anywidget/):

```python
import marimo as mo

# Wrap anywidget for marimo's reactive system
widget = mo.ui.anywidget(CounterWidget())
widget.value  # Access synced traits as dict
```

**Key insight**: marimo's `mo.ui.anywidget()` wraps anywidgets and exposes `.value` as a reactive dict. When traits change, dependent cells re-execute automatically.

### Agent Observability Patterns

From [IBM's AI Agent Observability](https://www.ibm.com/think/insights/ai-agent-observability) and [Langfuse Agent Observability](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse):

- **Traces**: End-to-end journey of agent requests
- **Spans**: Individual operations (LLM calls, tool use, retrieval)
- **Agent graphs**: Visualize interactions and dependencies
- **Metrics**: Latency, token usage, cost, error rates

**Key insight**: kgents `AgentCardWidget` already captures phase, activity history, capability, and entropy. We can extend this to render OpenTelemetry spans.

---

## Architecture Decision: Signal ↔ Traitlets Bridge

### Option A: Traitlets as Source of Truth
```
Traitlets (anywidget) ──► Signal[T] (read-only mirror)
```
- Pro: Native anywidget pattern
- Con: Loses Signal composition, breaks functor laws

### Option B: Signal as Source of Truth (CHOSEN)
```
Signal[T] ──► Traitlets (sync layer) ──► JavaScript
```
- Pro: Preserves Signal[T] semantics, functor composition
- Pro: Already battle-tested with 1326 reactive tests
- Con: Slight indirection

### Option C: Bidirectional with Conflict Resolution
```
Signal[T] ←──► Traitlets ←──► JavaScript
```
- Pro: Full interactivity from either side
- Con: Complexity, potential for inconsistency

**Decision**: Start with Option B for read-heavy widgets (AgentCard, Sparkline). Evolve to Option C for interactive widgets (sliders, inputs) in Wave 12.

---

## Implementation Chunks

### 1. MarimoAdapter (`adapters/marimo_widget.py`)

The core bridge between `KgentsWidget` and `anywidget.AnyWidget`:

```python
class MarimoAdapter(anywidget.AnyWidget, Generic[S]):
    """
    Wraps any KgentsWidget for marimo/Jupyter rendering.

    Architecture:
        KgentsWidget.state (Signal[S])
            ↓ subscribe
        MarimoAdapter._state_json (traitlet, sync=True)
            ↓ anywidget protocol
        JavaScript model.get("_state_json")
            ↓ render()
        DOM element
    """

    # ESM module for rendering
    _esm = pathlib.Path(__file__).parent / "marimo_esm" / "widget.js"
    _css = pathlib.Path(__file__).parent / "marimo_esm" / "widget.css"

    # Synced state (JSON-serialized widget projection)
    _state_json = traitlets.Unicode("{}").tag(sync=True)
    _widget_type = traitlets.Unicode("generic").tag(sync=True)

    def __init__(self, kgents_widget: KgentsWidget[S]) -> None:
        super().__init__()
        self._kgents_widget = kgents_widget
        self._unsubscribe: Callable[[], None] | None = None
        self._sync_state()
        self._subscribe_to_signal()

    def _sync_state(self) -> None:
        """Sync KgentsWidget state to traitlet."""
        projection = self._kgents_widget.project(RenderTarget.JSON)
        self._state_json = json.dumps(projection)
        self._widget_type = projection.get("type", "generic")

    def _subscribe_to_signal(self) -> None:
        """Subscribe to Signal changes."""
        if hasattr(self._kgents_widget, "state"):
            state = getattr(self._kgents_widget, "state")
            if isinstance(state, Signal):
                self._unsubscribe = state.subscribe(lambda _: self._sync_state())
```

### 2. ESM Renderer (`adapters/marimo_esm/widget.js`)

Client-side rendering using vanilla JavaScript (AI-friendly):

```javascript
// widget.js - Anywidget Front-End Module (AFM)
function render({ model, el }) {
    const container = document.createElement("div");
    container.className = "kgents-widget";

    function update() {
        const state = JSON.parse(model.get("_state_json"));
        const type = model.get("_widget_type");

        // Dispatch to type-specific renderer
        switch (type) {
            case "agent_card":
                renderAgentCard(container, state);
                break;
            case "sparkline":
                renderSparkline(container, state);
                break;
            case "bar":
                renderBar(container, state);
                break;
            default:
                container.innerHTML = `<pre>${JSON.stringify(state, null, 2)}</pre>`;
        }
    }

    model.on("change:_state_json", update);
    update();
    el.appendChild(container);
}

function renderAgentCard(el, state) {
    const phase_icons = {
        "idle": "○", "active": "◉", "waiting": "◐",
        "complete": "●", "error": "◈", "spawning": "◎"
    };

    el.innerHTML = `
        <div class="agent-card" data-phase="${state.phase}">
            <div class="card-header">
                <span class="phase-icon">${phase_icons[state.phase] || "○"}</span>
                <span class="agent-name">${state.name}</span>
            </div>
            <div class="card-activity">
                ${renderSparklineSVG(state.children?.activity?.values || [])}
            </div>
            <div class="card-capability">
                ${renderCapabilityBar(state.capability || 0)}
            </div>
        </div>
    `;
}

function renderSparklineSVG(values) {
    if (!values.length) return "";
    const width = 100, height = 20;
    const points = values.map((v, i) =>
        `${(i / (values.length - 1)) * width},${height - v * height}`
    ).join(" ");
    return `<svg viewBox="0 0 ${width} ${height}" class="sparkline">
        <polyline points="${points}" fill="none" stroke="currentColor"/>
    </svg>`;
}

export default { render };
```

### 3. AgentTraceWidget (`adapters/marimo_trace.py`)

**Visionary**: Bridge OpenTelemetry spans to reactive widgets:

```python
@dataclass(frozen=True)
class AgentTraceState:
    """State for visualizing agent execution traces."""
    trace_id: str = ""
    spans: tuple[SpanData, ...] = ()
    root_agent: str = ""
    total_latency_ms: float = 0.0
    total_tokens: int = 0
    total_cost_usd: float = 0.0

class AgentTraceWidget(KgentsWidget[AgentTraceState]):
    """
    Visualize agent execution traces in notebooks.

    Renders OpenTelemetry-compatible spans as:
    - Timeline view (horizontal bars)
    - Tree view (nested calls)
    - Metrics summary (latency, tokens, cost)

    Example:
        from opentelemetry import trace
        spans = collect_spans_from_trace(trace_id)

        widget = AgentTraceWidget(AgentTraceState(
            trace_id=trace_id,
            spans=tuple(spans),
            root_agent="kgent-1",
        ))

        mo.ui.anywidget(MarimoAdapter(widget))
    """
```

### 4. NotebookTheme (`adapters/marimo_theme.py`)

CSS variables for notebook context:

```python
class NotebookTheme:
    """Generate CSS for notebook styling, respecting marimo's theme."""

    def to_css(self, theme: Theme) -> str:
        """Generate CSS with marimo-compatible variables."""
        return f"""
        .kgents-widget {{
            --kgents-primary: {self._rgb(theme.primary)};
            --kgents-surface: {self._rgb(theme.surface)};
            --kgents-text: {self._rgb(theme.text)};
            font-family: var(--marimo-monospace-font, monospace);
        }}

        .agent-card {{
            background: var(--kgents-surface);
            border: 1px solid var(--kgents-primary);
            border-radius: 4px;
            padding: 8px;
        }}

        .agent-card[data-phase="active"] {{
            animation: pulse 2s ease-in-out infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.8; }}
        }}
        """
```

### 5. Demo Notebook (`demo/reactive_agents.py`)

marimo notebook showcasing the full integration:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["marimo", "anywidget", "kgents"]
# ///

import marimo as mo

# Cell 1: Create reactive agent cards
from agents.i.reactive.primitives.agent_card import AgentCardWidget, AgentCardState
from agents.i.reactive.adapters import MarimoAdapter

kgent = AgentCardWidget(AgentCardState(
    agent_id="kgent-1",
    name="Kent's Assistant",
    phase="active",
    activity=(0.2, 0.4, 0.8, 0.6, 0.9, 0.7),
    capability=0.85,
))

# Cell 2: Wrap for marimo (reactive!)
mo.ui.anywidget(MarimoAdapter(kgent))

# Cell 3: Interactive controls
phase_select = mo.ui.dropdown(
    options=["idle", "active", "waiting", "complete", "error"],
    value="active",
    label="Agent Phase"
)

# Cell 4: Update agent (reactive chain!)
# When dropdown changes, this cell re-runs, updating the widget
kgent.state.update(lambda s: AgentCardState(
    **{**s.__dict__, "phase": phase_select.value}
))
```

---

## Creative Explorations (Entropy Budget)

### `void.entropy.sip(0.04)` — Widget Composition in Notebooks

What if notebooks could compose widgets categorically?

```python
# Horizontal composition: agent + trace side-by-side
combined = mo.hstack([
    mo.ui.anywidget(MarimoAdapter(agent_card)),
    mo.ui.anywidget(MarimoAdapter(trace_widget)),
])

# Vertical composition: dashboard layout
dashboard = mo.vstack([
    mo.md("# Agent Observability Dashboard"),
    combined,
    mo.ui.anywidget(MarimoAdapter(metrics_widget)),
])
```

This mirrors AGENTESE's compositional philosophy: widgets are morphisms, layout is composition.

### `void.entropy.sip(0.03)` — Live Agent Streaming

What if widgets could stream from live agents?

```python
# Subscribe widget to live agent events
async for event in agent.events():
    kgent.state.update(lambda s: s.with_activity(
        (*s.activity, event.intensity)[-20:]
    ))
    # Widget auto-updates in notebook!
```

This could enable real-time agent debugging in computational notebooks.

### `void.entropy.sip(0.02)` — Notebook as Agent UI

What if marimo notebooks ARE the agent interface?

```python
# Agent receives user input from notebook widgets
user_input = mo.ui.text(label="Ask the agent")
agent_response = await agent.query(user_input.value)

# Response rendered as interactive widget
mo.ui.anywidget(MarimoAdapter(
    ResponseWidget(agent_response)
))
```

The notebook becomes a conversational interface with reactive, observable agents.

---

## Exit Criteria

| Criterion | Verification |
|-----------|--------------|
| MarimoAdapter renders KgentsWidget | Unit test + notebook visual |
| AgentCardWidget displays correctly | SVG sparkline, capability bar |
| State changes propagate | Signal → traitlet → JS → DOM |
| Theme respects marimo dark/light | CSS variable fallback |
| Demo notebook runs | `marimo run demo/reactive_agents.py` |
| Tests pass | `uv run pytest` ≥1400 reactive tests |
| Types clean | `uv run mypy .` |
| Lint clean | `uv run ruff check .` |

---

## Dependencies

```bash
# Verify anywidget available
uv pip show anywidget || uv add anywidget

# Verify marimo for demo
uv pip show marimo || uv add marimo
```

---

## Sequencing Strategy

1. **MarimoAdapter** (core bridge) — must work first
2. **ESM Renderer** (client-side) — enables visual verification
3. **NotebookTheme** (styling) — polish
4. **AgentTraceWidget** (visionary) — if time permits
5. **Demo Notebook** (showcase) — validates all pieces

**Parallel tracks**: Tests can run alongside implementation. Theme work is independent of core adapter.

---

## Branch Candidates (check at exit)

| Branch | Type | Priority | Notes |
|--------|------|----------|-------|
| **Unified Demo** (Wave 12) | Next wave | High | Same widget → CLI, TUI, Notebook |
| **OpenTelemetry Integration** | Enhancement | High | AgentTraceWidget + span collection |
| **Interactive Widgets** | Enhancement | Medium | Bidirectional Signal ↔ traitlets |
| **Widget Gallery** | Documentation | Medium | Notebook showcasing all primitives |
| **Real-time Streaming** | Research | Low | Live agent event subscription |
| **marimo as Agent UI** | Visionary | Low | Notebook as conversational interface |

---

## Continuation Generator

### Normal Exit
```markdown
⟿[QA]
/hydrate
handles: code=adapters/marimo_*.py; tests=_tests/test_marimo_*.py; esm=adapters/marimo_esm/; results=+74; summary="Marimo Adapter bridging KgentsWidget → anywidget with ESM renderer"; laws=compositional_adapter_laws_upheld; ledger={IMPLEMENT:complete}; branches=[opentelemetry_integration, unified_demo]
mission: gate quality/security/lawfulness before broader testing.
actions: uv run mypy .; uv run ruff check; security review (ESM injection); marimo visual check.
exit: QA checklist status + ledger.QA=touched; notes for TEST; continuation → TEST.
```

### Halt Conditions
```markdown
⟂[BLOCKED:anywidget_dep] anywidget not available or version incompatible
⟂[BLOCKED:esm_bundling] JavaScript module loading fails in marimo
⟂[BLOCKED:traitlets_sync] State synchronization broken
⟂[BLOCKED:tests_failing] Core adapter tests failing before QA gate
⟂[ENTROPY_DEPLETED] Exploration budget exhausted without resolution
⟂[DETACH:awaiting_human] Architecture decision on bidirectional sync needed
```

---

## Next N-Phase Continuation Template

After Wave 11 completes, generate Wave 12 prompt:

```markdown
---
path: reactive-substrate/wave12
status: pending
phase_ledger:
  PLAN: touched
  RESEARCH: pending  # Unified rendering research
  DEVELOP: pending
  IMPLEMENT: pending
  ...
---

# ⟿[IMPLEMENT] Reactive Substrate Wave 12 — Unified Demo

> *"One widget definition. Three targets. Zero rewrites. Pure composition."*

## Quick Wield
```
ATTACH /hydrate
handles: world.reactive.unified.manifest[wave=12]; void.entropy.sip[amount=0.05]
mission: Single demo application showcasing CLI, TUI, Notebook from identical KgentsWidget definitions.
ledger: IMPLEMENT=in_progress | entropy.spent += 0.05
actions: UnifiedApp scaffold, target switcher, side-by-side comparison, documentation
exit: 1450+ reactive tests | all 3 targets rendering same widgets | ⟿[REFLECT] or ⟂[BLOCKED]
```

## Context
**From Wave 11**: Marimo adapter complete. All 3 RenderTargets (CLI, TUI, MARIMO) now have production adapters.

## The Demonstration
A single Python module that:
1. Defines `AgentDashboard` using `KgentsWidget` composition
2. Runs as CLI (`python -m demo --target=cli`)
3. Runs as TUI (`python -m demo --target=tui`)
4. Runs as Notebook (`marimo run demo.py`)

Same state, same widgets, different projections. The functor is visible.

[Continue with implementation chunks, exit criteria, etc.]
```

---

## Related

- [anywidget documentation](https://anywidget.dev/en/getting-started/)
- [marimo anywidget API](https://docs.marimo.io/api/inputs/anywidget/)
- [Langfuse Agent Observability](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse)
- [OpenTelemetry AI Agent Standards](https://opentelemetry.io/blog/2025/ai-agent-observability/)
- `plans/skills/n-phase-cycle/implement.md` — Phase skill
- `spec/protocols/agentese.md` — `world.reactive.*` handles
- `impl/claude/agents/i/reactive/widget.py` — `RenderTarget.MARIMO`
- `impl/claude/agents/i/reactive/primitives/agent_card.py` — Existing `_to_marimo()` method
- Wave 10 epilogue: `impl/claude/plans/_epilogues/2025-12-14-reactive-substrate-wave10.md`

---

*"I will render agents in notebooks, not describe how to render them."*

*"The widget is a functor. The notebook is a category. Composition is observation."*
