---
path: reactive-substrate/release-v1
status: pending
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [agent-dashboard-cli, pypi-package]
session_notes: |
  Wave 13: Reactive Substrate v1.0 Release
  From Wave 12: Unified demo complete. Functor proven across CLI, TUI, Notebook.
  Test baseline: 1460 tests passing.
phase_ledger:
  PLAN: complete  # This prompt
  RESEARCH: pending  # API surface audit
  DEVELOP: pending  # Version bump, changelog
  STRATEGIZE: pending  # Release checklist
  CROSS-SYNERGIZE: pending  # Integration with kg CLI
  IMPLEMENT: pending  # Final polish
  QA: pending  # Release candidate testing
  TEST: pending  # Regression suite
  EDUCATE: pending  # README, examples
  MEASURE: pending  # Coverage report
  REFLECT: pending
entropy:
  planned: 0.05
  spent: 0.00
  sip_allowed: true
---

# ⟿[IMPLEMENT] Reactive Substrate Wave 13 — v1.0 Release

> *"Waves complete. Time to ship."*

---

## Quick Wield

```
ATTACH /hydrate
handles: world.reactive.release[version=1.0]; void.entropy.sip[amount=0.03]
mission: Prepare reactive substrate for v1.0 release. API freeze, docs, changelog.
ledger: IMPLEMENT=in_progress | entropy.spent += 0.03
actions: API audit, version bump, CHANGELOG, README, examples
exit: v1.0.0 tagged | release notes complete | ⟿[EDUCATE] or ⟂[BLOCKED]
```

---

## Context from Wave 12

### Proven Architecture
- **CLI**: ASCII art rendering via `to_cli()`
- **TUI**: Textual widgets via `TextualAdapter`
- **Notebook**: marimo/anywidget via `MarimoAdapter`
- **JSON**: Serializable dicts for APIs

### Test Baseline
- **1460 tests** passing
- All adapters have comprehensive coverage
- Performance: >4,000 renders/sec on all targets

### Key Files
```
impl/claude/agents/i/reactive/
├── widget.py              # KgentsWidget[S], RenderTarget
├── signal.py              # Signal[T], Computed[T], Effect
├── primitives/
│   ├── glyph.py           # GlyphWidget (atom)
│   ├── bar.py             # BarWidget (progress)
│   ├── sparkline.py       # SparklineWidget (time-series)
│   └── agent_card.py      # AgentCardWidget (composite)
├── adapters/
│   ├── textual_widget.py  # TextualAdapter
│   ├── marimo_widget.py   # MarimoAdapter
│   └── ...
└── demo/
    ├── unified_app.py     # Multi-target demo
    └── unified_notebook.py # marimo notebook
```

---

## Implementation Chunks

### 1. API Surface Audit

Review and document the public API:

```python
# Core exports (from agents.i.reactive)
from agents.i.reactive import (
    # Base classes
    KgentsWidget,
    CompositeWidget,
    RenderTarget,

    # Reactive primitives
    Signal,
    Computed,
    Effect,

    # Widgets
    GlyphWidget, GlyphState,
    BarWidget, BarState,
    SparklineWidget, SparklineState,
    AgentCardWidget, AgentCardState,

    # Adapters
    TextualAdapter,
    MarimoAdapter,
)
```

**Checklist:**
- [ ] All public classes have docstrings
- [ ] All public methods have type hints
- [ ] No internal APIs exposed accidentally
- [ ] Deprecation warnings for any v0.x removals

### 2. Version Bump

Update version in `pyproject.toml`:

```toml
[project]
name = "kgents"
version = "1.0.0"  # Bump from 0.x.x
```

### 3. CHANGELOG Entry

```markdown
## [1.0.0] - 2025-12-14

### Added
- Reactive substrate with target-agnostic widgets
- `KgentsWidget[S]` base class with `project(target)` functor
- `Signal[T]`, `Computed[T]`, `Effect` reactive primitives
- Widget primitives: Glyph, Bar, Sparkline, AgentCard
- `TextualAdapter` for TUI rendering
- `MarimoAdapter` for notebook rendering
- Unified demo with CLI, TUI, and notebook support
- 1460+ tests with comprehensive coverage

### Changed
- Widget rendering now uses functor pattern
- Adapters pass Rich renderables directly (no string conversion)

### Fixed
- TUI adapter now correctly renders Panel objects
- Notebook theme uses light colors for better contrast
```

### 4. README Section

Add to main README or create `impl/claude/agents/i/reactive/README.md`:

```markdown
# Reactive Substrate

Target-agnostic reactive widgets for agent visualization.

## Quick Start

\`\`\`python
from agents.i.reactive import AgentCardWidget, AgentCardState

# Define once
card = AgentCardWidget(AgentCardState(
    name="My Agent",
    phase="active",
    activity=(0.3, 0.5, 0.7, 0.9),
    capability=0.85,
))

# Render anywhere
print(card.to_cli())      # Terminal
card.to_tui()             # Textual app
card.to_marimo()          # Notebook
card.to_json()            # API response
\`\`\`

## Architecture

The reactive substrate implements a **functor pattern**:

\`\`\`
project : KgentsWidget[S] → Target → Renderable[Target]
\`\`\`

Same widget state, different projections. Zero rewrites.

## Demos

\`\`\`bash
# CLI mode
python -m agents.i.reactive.demo.unified_app

# TUI mode
python -m agents.i.reactive.demo.unified_app --target=tui

# Notebook mode
marimo run impl/claude/agents/i/reactive/demo/unified_notebook.py
\`\`\`
```

### 5. Export Cleanup

Ensure `__init__.py` exports are clean:

```python
# impl/claude/agents/i/reactive/__init__.py
"""
Reactive Substrate v1.0

Target-agnostic reactive widgets for agent visualization.
"""

from agents.i.reactive.widget import (
    KgentsWidget,
    CompositeWidget,
    RenderTarget,
)
from agents.i.reactive.signal import Signal, Computed, Effect

# Re-export primitives
from agents.i.reactive.primitives import (
    GlyphWidget, GlyphState,
    BarWidget, BarState,
    SparklineWidget, SparklineState,
    AgentCardWidget, AgentCardState,
)

# Re-export adapters
from agents.i.reactive.adapters import (
    TextualAdapter,
    MarimoAdapter,
    is_anywidget_available,
)

__version__ = "1.0.0"

__all__ = [
    # Core
    "KgentsWidget",
    "CompositeWidget",
    "RenderTarget",
    "Signal",
    "Computed",
    "Effect",
    # Widgets
    "GlyphWidget", "GlyphState",
    "BarWidget", "BarState",
    "SparklineWidget", "SparklineState",
    "AgentCardWidget", "AgentCardState",
    # Adapters
    "TextualAdapter",
    "MarimoAdapter",
    "is_anywidget_available",
    # Meta
    "__version__",
]
```

### 6. Integration with kg CLI

Add dashboard command to kgents CLI:

```python
# In CLI handlers
@cli.command()
def dashboard():
    """Launch the agent dashboard."""
    from agents.i.reactive.demo.unified_app import run_tui, create_sample_dashboard
    dashboard = create_sample_dashboard()
    run_tui(dashboard)
```

Usage: `kg dashboard`

---

## Exit Criteria

| Criterion | Verification |
|-----------|--------------|
| API documented | All public exports have docstrings |
| Version bumped | `__version__ == "1.0.0"` |
| CHANGELOG updated | Entry for v1.0.0 |
| README complete | Quick start + architecture |
| Exports clean | `__all__` matches public API |
| Tests pass | 1460+ tests green |
| Types clean | `uv run mypy` passes |
| Lint clean | `uv run ruff check` passes |

---

## Creative Explorations (Entropy Budget)

### `void.entropy.sip(0.02)` — kg dashboard Command

What if `kg dashboard` launched a live agent monitor?

```bash
kg dashboard              # TUI mode
kg dashboard --web        # Browser mode (future)
kg dashboard --json       # JSON stream (future)
```

### `void.entropy.sip(0.01)` — Widget Gallery

A showcase of all available widgets:

```bash
python -m agents.i.reactive.gallery
```

---

## Halt Conditions

```markdown
⟂[BLOCKED:breaking_change] API change required that breaks v0.x
⟂[BLOCKED:test_failure] Regression in existing tests
⟂[BLOCKED:dependency] Missing required dependency
⟂[DETACH:awaiting_human] Need decision on public API surface
```

---

## Continuation Generator

### Normal Exit (v1.0 Release → EDUCATE)
```markdown
⟿[EDUCATE]
/hydrate
handles: code=reactive/__init__.py; docs=README.md; version=1.0.0
mission: Write tutorials, record demo video script, update main README.
actions: Tutorial notebook, video script, badge updates.
exit: Docs complete; tutorials tested; ⟂[DETACH:release_ready]
```

### Post-Release (Agent Dashboard Product)
```markdown
⟿[PLAN] Agent Dashboard CLI

/hydrate
handles: world.dashboard.manifest; void.entropy.sip[amount=0.05]
mission: Ship `kg dashboard` as standalone agent monitoring tool.
actions: CLI command, live agent feed, keyboard navigation.
exit: `kg dashboard` ships; real agents visualized; ⟂[DETACH:product_ready]
```

---

## Related

- Wave 12 Epilogue: `impl/claude/plans/_epilogues/2025-12-14-reactive-substrate-wave12.md`
- Unified Demo: `impl/claude/agents/i/reactive/demo/unified_app.py`
- N-Phase Cycle: `plans/skills/n-phase-cycle/README.md`

---

*"The waves brought us here. Now we ship."*
