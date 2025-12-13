---
path: devex/dashboard
status: planned
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
uses: [devex/trace]  # TRACES panel uses TraceRenderer
session_notes: |
  Plan created from strategic recommendations.
  Priority 3 of 6 DevEx improvements.
---

# Live Metrics Dashboard: `kgents dashboard`

> *"Make the system's metabolism visible."*

**Goal**: Real-time TUI dashboard showing Cortex, Metabolism, Stigmergy, and K-gent state.
**Priority**: 3 (high impact, medium effort)

---

## The Problem

Metrics exist in code (Cortex tokens, Metabolism pressure, Stigmergy pheromones) but aren't visualized. Users can't see the system breathing.

---

## The Solution

```
┌─────────────────────────────────────────────────────────────────┐
│ kgents dashboard                                    [q] quit    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CORTEX                           METABOLISM                     │
│  ├─ LLM calls: 127/1000          ├─ Pressure: ████░░░░ 42%      │
│  ├─ Tokens (in): 45,231          ├─ Temperature: 0.72           │
│  └─ Tokens (out): 12,847         └─ Fever: No                   │
│                                                                  │
│  STIGMERGY                        K-GENT                         │
│  ├─ Active pheromones: 3         ├─ Mode: DIALOGUE              │
│  ├─ Total intensity: 0.87        ├─ Garden patterns: 12         │
│  └─ Decay rate: 0.01/s           └─ Last dream: 2h ago          │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  RECENT TRACES                                                   │
│  ├─ self.soul.challenge ("singleton") → REJECT     [23ms]       │
│  ├─ world.cortex.invoke (gpt-4) → success          [1.2s]       │
│  └─ void.entropy.tithe (0.1) → discharged          [1ms]        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Research & References

### Textual TUI Framework
- Built on Rich, supports async reactive updates
- CSS-like styling for widgets
- TreeView, Table, and custom widgets
- Source: [Textual Documentation](https://textual.textualize.io/)
- Source: [Real Python - Textual Tutorial](https://realpython.com/python-textual/)

### TUI Dashboard Patterns
- Reactive attributes for real-time updates
- Docking and grid layout systems
- Source: [DEV.to - Textual Guide](https://dev.to/wiseai/textual-the-definitive-guide-part-1-1i0p)

### Existing I-gent Assets
- `agents/i/widgets/sparkline.py` — Sparkline graphs
- `agents/i/widgets/timeline.py` — Timeline display
- `agents/i/widgets/triad_health.py` — Health indicators
- `agents/i/widgets/entropy.py` — Entropy visualization
- `agents/i/screens/flux.py` — Flux screen (template)

---

## Implementation Outline

### Phase 1: Data Collectors (~100 LOC)
```python
# agents/i/data/dashboard_collectors.py
@dataclass
class DashboardMetrics:
    cortex: CortexMetrics
    metabolism: MetabolismMetrics
    stigmergy: StigmergyMetrics
    kgent: KgentMetrics
    traces: list[TraceEntry]

async def collect_metrics() -> DashboardMetrics:
    """Collect metrics from all subsystems."""
```

### Phase 2: Dashboard Screen (~150 LOC)
```python
# agents/i/screens/dashboard.py
class DashboardScreen(Screen):
    """Real-time metrics dashboard."""

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            CortexPanel(),
            MetabolismPanel(),
            StigmergyPanel(),
            KgentPanel(),
            id="metrics-grid",
        )
        yield TracesPanel()
        yield Footer()

    def on_mount(self) -> None:
        self.set_interval(1.0, self.refresh_metrics)
```

### Phase 3: Individual Panels (~200 LOC)
```python
class CortexPanel(Static):
    """Cortex metrics panel."""

    def update_metrics(self, metrics: CortexMetrics) -> None:
        self.query_one("#llm-calls").update(f"LLM calls: {metrics.calls}")
        self.query_one("#tokens-in").update(f"Tokens (in): {metrics.tokens_in:,}")

class MetabolismPanel(Static):
    """Metabolism pressure gauge."""
    # Reuse existing entropy widget
```

### Phase 4: CLI Handler (~50 LOC)
```python
# protocols/cli/handlers/dashboard.py
@expose(help="Live metrics dashboard")
async def dashboard(self, ctx: CommandContext) -> None:
    from agents.i.screens.dashboard import DashboardScreen
    app = DashboardApp()
    await app.run_async()
```

---

## File Structure

```
agents/i/
├── screens/
│   └── dashboard.py    # Main dashboard screen
├── data/
│   └── dashboard_collectors.py  # Metrics collection
└── widgets/
    └── (existing widgets)

protocols/cli/handlers/
└── dashboard.py        # CLI entry point
```

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| Refresh rate | 1 Hz minimum |
| Startup time | < 500ms |
| Memory overhead | < 50MB |
| Kent's approval | "I can see it breathing" |

---

## Testing Strategy

| Test Type | Coverage |
|-----------|----------|
| Unit | Metric collectors |
| Integration | Dashboard rendering |
| Smoke | `kgents dashboard` starts |
| Manual | Kent watches system under load |

---

## Dependencies

- `textual` (already installed) — TUI framework
- Existing I-gent widgets
- Existing metrics infrastructure (Cortex, Metabolism, Stigmergy)

---

## Cross-References

- **Strategic Recommendations**: `plans/ideas/strategic-recommendations-2025-12-13.md`
- **I-gent Widgets**: `plans/agents/i-gent-widgets.md`
- **Metabolism**: `plans/void/entropy.md`
- **Textual Docs**: https://textual.textualize.io/

---

*"What you can see, you can tend."*
