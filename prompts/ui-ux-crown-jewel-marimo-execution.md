# UI/UX Crown Jewel Execution: Marimo-Native

> *"The field does not display state; it is state made visible. The garden does not show growth; it grows."*

## The Mission

Transform kgents I-gent into a **marimo-native living substrate** where:
- Terminal users get ASCII stigmergic fields in Textual TUI
- Notebook users get rich interactive marimo notebooks
- Web users get WASM-powered static sites
- Documentation readers get live interactive examples
- **All share the same underlying AGENTESE ontology**

---

## Phase: IMPLEMENT ← RESEARCH

/hydrate

### Handles
```
scope=UI/UX Crown Jewel v2.0: Marimo-Native Implementation
chunks=[Wave0:MarimoFoundation, Wave1:CoreWidgets, Wave2:AGENTESEBridge, Wave3:FullDemo]
exit=marimo run notebooks/kgents_demo.py shows full garden + anywidgets work in both surfaces
ledger=PLAN:touched, RESEARCH:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:in_progress
entropy=0.10 (high novelty—marimo integration is new territory)
branches=[Web-deploy:parallel-future, Mobile:deferred, Accessibility:parallel-future]
```

### Mission
Implement the marimo-kgents synthesis. Make AGENTESE tangible through reactive cells and anywidgets that work in both marimo AND Textual.

### Actions

**Wave 0: Marimo Foundation (NOW)**:
```bash
# Add dependencies
uv add marimo anywidget traitlets

# Create package structure
mkdir -p impl/claude/agents/i/marimo/widgets
touch impl/claude/agents/i/marimo/__init__.py
touch impl/claude/agents/i/marimo/widgets/__init__.py
touch impl/claude/agents/i/marimo/widgets/base.py

# Create demo notebook
mkdir -p notebooks
touch notebooks/kgents_demo.py
```

**Wave 1: Core anywidget Implementation**:
```python
# impl/claude/agents/i/marimo/widgets/base.py
import anywidget
import traitlets

class KgentsWidget(anywidget.AnyWidget):
    """Base class for kgents anywidgets."""
    _esm = """
    export function render({ model, el }) {
      el.innerHTML = '<div>Override in subclass</div>';
    }
    """

# impl/claude/agents/i/marimo/widgets/stigmergic_field.py
class StigmergicFieldWidget(KgentsWidget):
    """Stigmergic field rendered as interactive canvas."""
    _esm = """..."""  # See strategy doc for full implementation

    entities = traitlets.List([]).tag(sync=True)
    pheromones = traitlets.List([]).tag(sync=True)
    clicked_pos = traitlets.List([0, 0]).tag(sync=True)
```

**Wave 2: AGENTESE Bridge**:
```python
# impl/claude/agents/i/marimo/logos_cell.py
import marimo as mo
from impl.claude.protocols.agentese import logos

def create_logos_cell(handle: str):
    """Create a marimo cell that executes an AGENTESE handle."""
    @mo.cell
    def _():
        result = logos.invoke(handle)
        return mo.md(f"**{handle}**: {result}")
    return _
```

**Wave 3: Demo Notebook**:
```python
# notebooks/kgents_demo.py
import marimo

app = marimo.App()

@app.cell
def garden():
    import kgents as kg
    return kg.Garden.from_bootstrap()

@app.cell
def field_view(garden):
    from impl.claude.agents.i.marimo.widgets import StigmergicFieldWidget
    return StigmergicFieldWidget(garden)

@app.cell
def controls():
    import marimo as mo
    agent = mo.ui.dropdown(options=["robin", "forge", "flux"], label="Agent")
    aspect = mo.ui.dropdown(options=["manifest", "witness", "refine"], label="Aspect")
    return agent, aspect

@app.cell
def execute(garden, agent, aspect):
    import marimo as mo
    from impl.claude.protocols.agentese import logos
    handle = f"world.{agent.value}.{aspect.value}"
    result = logos.invoke(handle)
    return mo.md(f"**Result**: {result}")
```

### Exit Criteria
- `uv add marimo anywidget` succeeds
- `marimo run notebooks/kgents_demo.py` opens without error
- Basic widget renders in marimo notebook
- Ledger: `IMPLEMENT=touched`

### Continuation → QA
```markdown
/hydrate
# QA ← IMPLEMENT
handles: widgets=${widget_list}; notebook=${demo_notebook}; ledger=${phase_ledger}
mission: verify type safety (mypy); lint (ruff); test widgets render in both marimo and TUI.
actions: uv run mypy impl/claude/agents/i/marimo/; uv run ruff check; manual marimo test.
exit: clean lint/type; manual verification pass; ledger.QA=touched; continuation → TEST.
```

---

## Alternative Entry Points

### If Wave 0 is complete (marimo installed):

/hydrate
# Wave 1: Core Widgets

**Context**: marimo and anywidget installed. Now build the widget layer.

**Actions**:
1. Implement `StigmergicFieldWidget`:
   - Canvas-based rendering of entities and pheromones
   - Click handling synced to Python
   - Brownian motion animation loop

2. Implement `DialecticWidget`:
   - Three-panel layout (thesis/antithesis/synthesis)
   - Model-bound state updates
   - Color theming for each panel

3. Implement `TimelineWidget`:
   - Horizontal scrollable timeline
   - State snapshots on hover
   - Play/pause controls

**Exit**: All three widgets render in marimo; click events fire.

---

### If focusing on AGENTESE-marimo bridge:

/hydrate
# Wave 2: AGENTESE Bridge

**Context**: Widgets exist. Now wire AGENTESE paths to marimo reactivity.

**Actions**:
1. Create `LogosCell` wrapper:
   ```python
   class LogosCell:
       def __init__(self, handle: str):
           self.handle = handle

       def __call__(self, observer=None):
           return logos.invoke(self.handle, observer)
   ```

2. Create `ObserverContext` for marimo:
   ```python
   @mo.cell
   def observer_context():
       return mo.state({"observer": "default", "perturbation_count": 0})
   ```

3. Wire affordance generation:
   ```python
   @mo.cell
   def affordances(agent):
       affs = agent.affordances()
       buttons = [mo.ui.button(label=a.name, on_click=lambda: logos.invoke(a.handle))
                  for a in affs]
       return mo.hstack(buttons)
   ```

**Exit**: AGENTESE handles trigger marimo cell updates; affordances render as buttons.

---

### If focusing on Textual wrapper layer:

/hydrate
# Wave 1B: Textual ASCII Projections

**Context**: anywidgets exist. Now create ASCII versions for TUI.

**Actions**:
1. Create `StigmergicFieldTUI`:
   - Renders entities as single characters (K, R, F, etc.)
   - Background colors for pheromone intensity
   - Wraps anywidget data model

2. Create `DialecticTUI`:
   - Three-column Textual layout
   - Rich text rendering
   - Subscribes to same traitlets as anywidget

3. Ensure bidirectional sync:
   - Changes in TUI update anywidget state
   - Changes in marimo propagate to TUI (if both running)

**Exit**: `kg garden` shows TUI field; same data model works in marimo.

---

## The Ground (Always Available)

```
/hydrate → spec/principles.md → correctness
/hydrate → plans/skills/n-phase-cycle/README.md → process
/hydrate → plans/ui-ux-crown-jewel-strategy-v2.md → strategy
/hydrate → docs/Radical Redesign Proposal...pdf → vision
/hydrate → docs/Reimagining Generative UI...pdf → frameworks
```

---

## Implementation Checklist

### Wave 0: Foundation
- [ ] `uv add marimo anywidget traitlets`
- [ ] Create `impl/claude/agents/i/marimo/` package
- [ ] Create `notebooks/` directory
- [ ] Basic `kgents_demo.py` that imports marimo

### Wave 1: Core Widgets
- [ ] `StigmergicFieldWidget` (anywidget)
- [ ] `DialecticWidget` (anywidget)
- [ ] `TimelineWidget` (anywidget)
- [ ] `StigmergicFieldTUI` (Textual wrapper)
- [ ] Tests for widget rendering

### Wave 2: AGENTESE Bridge
- [ ] `LogosCell` wrapper class
- [ ] `ObserverContext` state management
- [ ] Affordance → button generation
- [ ] Handle autocomplete in marimo

### Wave 3: Full Demo
- [ ] Complete `kgents_demo.py` notebook
- [ ] All widgets integrated
- [ ] AGENTESE handles work as navigation
- [ ] `marimo run notebooks/kgents_demo.py` is compelling

### Wave 4: Polish
- [ ] WASM export works
- [ ] Documentation island example
- [ ] `kg notebook` command added
- [ ] Kent says "this is amazing"

---

## The Manifesto

```
I will make marimo and kgents ONE system with multiple projections.
I will build anywidgets FIRST, then wrap for Textual.
I will respect the convergent evolution: marimo's DAG IS AGENTESE reactivity.
I will show the accursed share (pheromones, entropy) as beauty in both surfaces.
I will delight Kent. This is the hard requirement.
```

---

## Quick Start Command

```bash
# Clone and setup
cd /Users/kentgang/git/kgents
uv add marimo anywidget traitlets

# Create structure
mkdir -p impl/claude/agents/i/marimo/widgets notebooks

# Start implementing
# (Use TodoWrite to track each widget)
```

---

*"The noun is a lie. There is only the rate of change. And now, the rate of change is visible—in terminal, notebook, and browser alike."*
