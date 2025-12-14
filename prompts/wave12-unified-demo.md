---
path: reactive-substrate/wave12
status: pending
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [agent-dashboard-product, reactive-substrate-v1]
session_notes: |
  Wave 12: Unified Demo - Single widget definitions rendering to CLI, TUI, Notebook.
  Crown Jewel: Full 11-phase ceremony. Prove the functor.
  From Wave 11: Marimo adapter complete. All 3 RenderTargets now have production adapters.
phase_ledger:
  PLAN: complete  # This prompt
  RESEARCH: pending  # Verify adapter parity, identify gaps
  DEVELOP: pending  # UnifiedApp contract
  STRATEGIZE: pending  # Demo structure
  CROSS-SYNERGIZE: pending  # Link to agent observability, AGENTESE paths
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending  # README, video-ready script
  MEASURE: pending  # Render time comparison
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.00
  sip_allowed: true
---

# ⟿[IMPLEMENT] Reactive Substrate Wave 12 — Unified Demo

> *"One widget definition. Three targets. Zero rewrites. Pure composition. The functor is visible."*

---

## Quick Wield

```
ATTACH /hydrate
handles: world.reactive.unified.manifest[wave=12]; void.entropy.sip[amount=0.05]
mission: Prove KgentsWidget renders identically across CLI, TUI, Notebook from single definition.
ledger: IMPLEMENT=in_progress | entropy.spent += 0.05
actions: UnifiedApp, target switcher, side-by-side demo, performance comparison
exit: 1450+ reactive tests | all 3 targets rendering same widgets | ⟿[QA] or ⟂[BLOCKED]
```

---

## Vision: The Functor Made Visible

Wave 11 completed the trifecta:
- **Wave 9**: CLI rendering (`RenderTarget.CLI`)
- **Wave 10**: TUI rendering (`RenderTarget.TUI` via `TextualAdapter`)
- **Wave 11**: Notebook rendering (`RenderTarget.MARIMO` via `MarimoAdapter`)

Wave 12 proves the architecture by **demonstrating the same widget across all three**:

```python
# The definition
card = AgentCardWidget(AgentCardState(
    name="Universal Agent",
    phase="active",
    activity=(0.2, 0.5, 0.8, 0.6, 0.9),
    capability=0.85,
))

# The projections (SAME card, different targets)
print(card.to_cli())           # ◉ Universal Agent\n▂▄▇▅█\n████████░░
TextualAdapter(card)           # Textual Static widget
mo.ui.anywidget(MarimoAdapter(card))  # marimo reactive widget
```

This is the **functor made visible**:
```
project : KgentsWidget[S] → Target → Renderable[Target]
```

---

## Context from Wave 11

### Artifacts Available
- `adapters/textual_widget.py`: `TextualAdapter`, `ReactiveTextualAdapter`
- `adapters/textual_layout.py`: `FlexContainer` for layout
- `adapters/textual_theme.py`: `ThemeBinding` for CSS
- `adapters/marimo_widget.py`: `MarimoAdapter` for anywidget
- `adapters/marimo_theme.py`: `NotebookTheme` for CSS
- `adapters/marimo_trace.py`: `AgentTraceWidget` for observability
- `demo/tui_dashboard.py`: TUI demo (Wave 10)
- `demo/marimo_agents.py`: Notebook demo (Wave 11)

### Test Baseline
- 1409 reactive tests passing
- All adapters have >90% coverage

---

## Implementation Chunks

### 1. UnifiedApp Module (`demo/unified_app.py`)

A single Python module that can run in any mode:

```python
"""
UnifiedApp: Same widgets, any target.

Usage:
    # CLI mode
    python -m agents.i.reactive.demo.unified_app --target=cli

    # TUI mode
    python -m agents.i.reactive.demo.unified_app --target=tui

    # Notebook mode
    marimo run impl/claude/agents/i/reactive/demo/unified_app.py
"""

from dataclasses import dataclass
from typing import Literal

from agents.i.reactive.primitives.agent_card import AgentCardWidget, AgentCardState
from agents.i.reactive.primitives.sparkline import SparklineWidget, SparklineState
from agents.i.reactive.primitives.bar import BarWidget, BarState
from agents.i.reactive.widget import RenderTarget


@dataclass
class UnifiedDashboard:
    """
    A dashboard of widgets that renders to any target.

    This is the proof: define once, render everywhere.
    """

    agents: list[AgentCardWidget]
    metrics: list[SparklineWidget]
    capacities: list[BarWidget]

    def render(self, target: RenderTarget) -> list[str | object]:
        """Render all widgets to target."""
        results = []
        for agent in self.agents:
            results.append(agent.project(target))
        for metric in self.metrics:
            results.append(metric.project(target))
        for capacity in self.capacities:
            results.append(capacity.project(target))
        return results


def create_sample_dashboard() -> UnifiedDashboard:
    """Create sample dashboard for demo."""
    return UnifiedDashboard(
        agents=[
            AgentCardWidget(AgentCardState(
                agent_id="kgent-1",
                name="Primary Agent",
                phase="active",
                activity=(0.3, 0.5, 0.7, 0.8, 0.6, 0.9),
                capability=0.9,
            )),
            AgentCardWidget(AgentCardState(
                agent_id="kgent-2",
                name="Secondary Agent",
                phase="waiting",
                activity=(0.2, 0.3, 0.4, 0.3, 0.2),
                capability=0.7,
            )),
        ],
        metrics=[
            SparklineWidget(SparklineState(
                values=tuple(i/20 for i in range(20)),
                label="Throughput",
            )),
        ],
        capacities=[
            BarWidget(BarState(value=0.75, width=20, label="Memory")),
            BarWidget(BarState(value=0.45, width=20, label="CPU")),
        ],
    )
```

### 2. CLI Runner (`demo/unified_app.py` continued)

```python
def run_cli(dashboard: UnifiedDashboard) -> None:
    """Run in CLI mode - plain text output."""
    print("=" * 50)
    print("UNIFIED DEMO - CLI MODE")
    print("=" * 50)

    print("\n## Agents\n")
    for agent in dashboard.agents:
        print(agent.to_cli())
        print()

    print("## Metrics\n")
    for metric in dashboard.metrics:
        print(metric.to_cli())

    print("\n## Capacities\n")
    for capacity in dashboard.capacities:
        print(capacity.to_cli())
```

### 3. TUI Runner (Textual App)

```python
def run_tui(dashboard: UnifiedDashboard) -> None:
    """Run in TUI mode - interactive Textual app."""
    from textual.app import App
    from textual.containers import Horizontal, Vertical
    from agents.i.reactive.adapters import TextualAdapter

    class UnifiedTUI(App):
        CSS = """
        Screen { layout: grid; grid-size: 2; }
        .agent-panel { height: auto; }
        """

        def compose(self):
            with Vertical():
                yield Static("UNIFIED DEMO - TUI MODE", classes="header")
                with Horizontal():
                    for agent in dashboard.agents:
                        yield TextualAdapter(agent, classes="agent-panel")
                # ... metrics and capacities

    UnifiedTUI().run()
```

### 4. Notebook Runner (marimo cells)

```python
# When run as marimo notebook
import marimo

app = marimo.App()

@app.cell
def render_dashboard():
    from agents.i.reactive.adapters import MarimoAdapter
    import marimo as mo

    dashboard = create_sample_dashboard()

    widgets = []
    for agent in dashboard.agents:
        widgets.append(mo.ui.anywidget(MarimoAdapter(agent)))

    return mo.hstack(widgets)
```

### 5. Side-by-Side Comparison Screenshot Script

```python
def capture_comparison():
    """Generate comparison screenshots for documentation."""
    dashboard = create_sample_dashboard()

    # CLI: capture to string
    cli_output = "\n".join(
        agent.to_cli() for agent in dashboard.agents
    )

    # JSON: capture structure
    json_output = [agent.to_json() for agent in dashboard.agents]

    # HTML: capture marimo output
    html_output = "\n".join(
        agent.to_marimo() for agent in dashboard.agents
    )

    return {
        "cli": cli_output,
        "json": json_output,
        "html": html_output,
    }
```

### 6. Performance Comparison Tests

```python
def test_render_performance():
    """Compare render times across targets."""
    import time

    card = AgentCardWidget(AgentCardState(
        name="Perf Test",
        activity=tuple(i/100 for i in range(100)),
    ))

    iterations = 1000

    # CLI
    start = time.perf_counter()
    for _ in range(iterations):
        card.to_cli()
    cli_time = time.perf_counter() - start

    # JSON
    start = time.perf_counter()
    for _ in range(iterations):
        card.to_json()
    json_time = time.perf_counter() - start

    # MARIMO
    start = time.perf_counter()
    for _ in range(iterations):
        card.to_marimo()
    marimo_time = time.perf_counter() - start

    print(f"CLI: {cli_time:.3f}s ({iterations/cli_time:.0f}/s)")
    print(f"JSON: {json_time:.3f}s ({iterations/json_time:.0f}/s)")
    print(f"MARIMO: {marimo_time:.3f}s ({iterations/marimo_time:.0f}/s)")
```

---

## Creative Explorations (Entropy Budget)

### `void.entropy.sip(0.03)` — Target Auto-Detection

What if the app detected its environment automatically?

```python
def detect_target() -> RenderTarget:
    """Auto-detect rendering target."""
    try:
        import marimo
        if marimo.running_in_notebook():
            return RenderTarget.MARIMO
    except ImportError:
        pass

    if sys.stdout.isatty() and os.environ.get("TERM"):
        # Could be TUI
        return RenderTarget.TUI

    return RenderTarget.CLI
```

### `void.entropy.sip(0.02)` — Responsive Rendering

What if widgets adapted based on available space?

```python
# In CLI
card.project(RenderTarget.CLI, width=40)  # Compact
card.project(RenderTarget.CLI, width=80)  # Full

# In notebook
card.project(RenderTarget.MARIMO, width="100%")  # Responsive
```

---

## Exit Criteria

| Criterion | Verification |
|-----------|--------------|
| UnifiedApp runs in CLI mode | `python -m ... --target=cli` |
| UnifiedApp runs in TUI mode | `python -m ... --target=tui` |
| UnifiedApp runs in notebook | `marimo run ...` |
| Same widgets, same state | Visual comparison screenshot |
| Performance documented | Render time table |
| Tests added | ≥1450 reactive tests |
| Types clean | `uv run mypy .` |
| Lint clean | `uv run ruff check .` |

---

## Dependencies

All dependencies already installed from Waves 10-11:
- `textual` (TUI)
- `rich` (TUI styling)
- `anywidget` (Notebook)
- `marimo` (Notebook)

---

## Sequencing Strategy

1. **UnifiedDashboard** (data structure) — foundation
2. **CLI runner** (simplest) — verify widget works
3. **TUI runner** (Textual) — verify adapter works
4. **Notebook runner** (marimo) — verify marimo adapter works
5. **Side-by-side script** — documentation artifact
6. **Performance tests** — measurement

**Parallel tracks**: Tests can run alongside implementation. Documentation can start once CLI works.

---

## Branch Candidates (check at exit)

| Branch | Type | Priority | Notes |
|--------|------|----------|-------|
| Agent Dashboard Product | Product | High | Ship as standalone tool |
| Reactive Substrate v1.0 | Release | High | Tag stable version |
| AGENTESE `world.reactive.*` | Enhancement | Medium | Full path registration |
| Widget Composition Operators | Enhancement | Medium | `hstack`, `vstack` for widgets |
| Real-time Agent Streaming | Research | Low | WebSocket → Signal |

---

## Continuation Generator

### Normal Exit (Wave 12 → REFLECT)
```markdown
⟿[REFLECT]
/hydrate
handles: code=demo/unified_app.py; tests=_tests/test_unified*.py; results=+50; summary="Unified Demo proving functor across 3 targets"; laws=render_target_functor_laws_upheld; ledger={IMPLEMENT:complete,QA:complete,TEST:complete}; branches=[agent_dashboard_product, reactive_v1_release]
mission: Capture learnings, seed next cycle, consider release.
actions: Write epilogue, update _forest.md, tag milestone.
exit: Epilogue written; branches classified; ⟂[DETACH:cycle_complete] or next wave prompt.
```

### Halt Conditions
```markdown
⟂[BLOCKED:tui_adapter] TextualAdapter not composing correctly
⟂[BLOCKED:marimo_adapter] MarimoAdapter state sync broken
⟂[BLOCKED:performance] Render times unacceptable (>100ms per widget)
⟂[ENTROPY_DEPLETED] Exploration budget exhausted
⟂[DETACH:awaiting_human] Architecture decision on responsive rendering
```

---

## Next N-Phase Continuation Template

After Wave 12 completes (REFLECT phase), generate Wave 13 or release prompt:

```markdown
---
path: reactive-substrate/release-v1
status: pending
phase_ledger:
  PLAN: touched
  RESEARCH: pending  # API surface review
  DEVELOP: pending  # Breaking change check
  IMPLEMENT: pending  # Version bump
  EDUCATE: pending  # Release notes, README update
  REFLECT: pending
---

# ⟿[PLAN] Reactive Substrate v1.0 Release

> *"Waves complete. Time to ship."*

## Quick Wield
```
ATTACH /hydrate
handles: world.reactive.release[version=1.0]; void.entropy.sip[amount=0.03]
mission: Prepare reactive substrate for v1.0 release. API freeze, docs, changelog.
ledger: PLAN=in_progress | entropy.spent += 0.03
actions: API review, version bump, CHANGELOG, README badges
exit: v1.0.0 tagged | pypi-ready | ⟿[EDUCATE] or ⟂[BLOCKED]
```

## Context
**From Waves 9-12**: Complete reactive substrate with CLI, TUI, Notebook support.
**Test Coverage**: 1450+ tests
**API Surface**: KgentsWidget, Signal, adapters, primitives

## Release Checklist
- [ ] API surface documented
- [ ] No breaking changes from v0.x
- [ ] CHANGELOG updated
- [ ] Version in pyproject.toml
- [ ] README badges
- [ ] Example notebooks
- [ ] Type stubs if needed

[Continue with release-specific content...]
```

---

## Related

- Wave 11 Epilogue: `impl/claude/plans/_epilogues/2025-12-14-reactive-substrate-wave11.md`
- Wave 10 TUI Demo: `impl/claude/agents/i/reactive/demo/tui_dashboard.py`
- Wave 11 Notebook Demo: `impl/claude/agents/i/reactive/demo/marimo_agents.py`
- N-Phase Cycle Skills: `plans/skills/n-phase-cycle/README.md`
- AGENTESE Spec: `spec/protocols/agentese.md`

---

*"I will render the same widget three ways, not describe how to render it."*

*"The functor is visible. The architecture is proven. Ship it."*
