---
path: plans/ui-ux-crown-jewel-strategy-v2
status: active
progress: 0
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables: [dashboard-textual-refactor, i-gent-radical-redesign, marimo-integration]
session_notes: |
  Enhanced Crown Jewel Strategy v2.0
  Integrates: Radical Redesign Proposal + Generative UI Frameworks Report + Marimo
  Key insight: marimo + kgents = convergent evolution toward same vision
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: pending
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched  # marimo integration discovered!
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.07
  returned: 0.0
---

# UI/UX Crown Jewel Grand Strategy v2.0

## The Marimo-Native Evolution

> *"The field does not display state; it is state made visible. The garden does not show growth; it grows."*

**Source Documents**:
1. `docs/Radical Redesign Proposal for the Kgents UI_UX Ecosystem.pdf`
2. `docs/Reimagining Generative UI Frameworks in Developer Tools.pdf`

**Grounding**: `spec/principles.md`
**Method**: Full 11-Phase N-Cycle Ceremony (AD-005)
**Key Addition**: Marimo as native reactive substrate

---

## The Convergent Evolution

Reading both PDFs reveals something profound: **marimo and kgents are solving the same problem from different angles**. They converge on identical principles:

| Concept | Marimo | Kgents | Convergence |
|---------|--------|--------|-------------|
| Reactivity | DAG-based cell dependencies | AGENTESE "viewing changes what is viewed" | **Identical philosophy** |
| State | No hidden state, deterministic | Polynomial agents with explicit modes | **Isomorphic** |
| Storage | Pure .py files, Git-friendly | Spec-driven, regenerable | **Same principle** |
| Composition | Cells as composable units | Agents as morphisms (>>) | **Category-theoretic** |
| AI-Native | Built-in LLM integration | K-gent persona, LLM-backed agents | **Same goal** |
| Widgets | anywidget for custom UI | Textual widgets | **Can unify via anywidget** |

**The Insight**: Marimo IS what kgents I-gent wants to become. Rather than building parallel infrastructure, we should make kgents **marimo-native**.

---

## The Marimo-Kgents Synthesis

### What Marimo Brings to Kgents

1. **Reactive DAG Execution**: Instead of polling or manual refresh, agent state changes automatically propagate to UI
2. **WASM Deployment**: Export kgents notebooks to static HTML—run anywhere without backend
3. **anywidget Ecosystem**: Leverage existing widgets, create custom kgents widgets that work in both TUI and marimo
4. **Marimo Islands**: Embed reactive kgents cells in documentation, blogs, tutorials
5. **AI-Native Editor**: Generate kgents pipelines from natural language

### What Kgents Brings to Marimo

1. **AGENTESE Ontology**: Verb-first paths as cell dependencies (`world.robin.manifest` triggers downstream cells)
2. **Stigmergic Visualization**: Pheromone traces as reactive anywidgets
3. **Polynomial Agents**: State machines as marimo cells with explicit modes
4. **Dialectic Process**: Thesis/antithesis/synthesis as marimo's reactive flow
5. **Category-Theoretic Composition**: Law-verified agent wiring diagrams

---

## The Three-Surface Architecture

### Surface 1: TUI (Textual) — The Terminal Garden

The existing I-gent TUI becomes the **terminal-native view**:

```
┌─ KGENTS GARDEN ──────────────────────── t: 00:14:32 ─┐
│                                                       │
│  [ENTROPY ████████████░░░░░░] 72%                    │
│  [HEAT    ███████░░░░░░░░░░░] 35%                    │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │       I                                         │ │
│  │            C              *                     │ │
│  │                     J                           │ │
│  │        X                                        │ │
│  │                  S                              │ │
│  │              F                                  │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  PHASE: FLUX                                          │
│  [1]FIELD [2]FORGE [3]MARIMO [o]OBSERVE [q]QUIT      │
└───────────────────────────────────────────────────────┘
```

**Key**: Press `3` to open marimo notebook view within TUI (via embedded browser or marimo CLI).

### Surface 2: Marimo Notebook — The Reactive Garden

Kgents as a marimo notebook:

```python
import marimo as mo
import kgents as kg

# Cell 1: Define the garden
@app.cell
def garden():
    return kg.Garden.from_bootstrap()

# Cell 2: Stigmergic field widget (anywidget)
@app.cell
def field_view(garden):
    return mo.ui.anywidget(kg.StigmergicFieldWidget(garden))

# Cell 3: Agent control panel
@app.cell
def controls(garden):
    agent_selector = mo.ui.dropdown(
        options=[a.name for a in garden.agents],
        label="Focus Agent"
    )
    action = mo.ui.dropdown(
        options=["manifest", "invoke", "refine", "witness"],
        label="Action"
    )
    return agent_selector, action

# Cell 4: Execute AGENTESE (reactive to controls)
@app.cell
def execute(garden, agent_selector, action):
    handle = f"world.{agent_selector.value}.{action.value}"
    result = kg.logos.invoke(handle)
    return mo.md(f"**Result**: {result}")
```

**Key**: The notebook IS the agent interaction. Cell dependencies ARE AGENTESE paths.

### Surface 3: Marimo Islands — The Embeddable Garden

Embed reactive kgents in any webpage:

```html
<!-- marimo islands for kgents documentation -->
<marimo-island>
  <marimo-cell>
    import kgents as kg
    garden = kg.Garden.demo()
    kg.widgets.StigmergicField(garden)
  </marimo-cell>
</marimo-island>
```

**Key**: Documentation becomes interactive. Readers can experiment with agents in-browser.

---

## The anywidget Bridge

The critical technical piece: **kgents widgets as anywidgets**.

### StigmergicFieldWidget

```python
import anywidget
import traitlets

class StigmergicFieldWidget(anywidget.AnyWidget):
    """Stigmergic field rendered as interactive canvas."""

    _esm = """
    export function render({ model, el }) {
      const canvas = document.createElement('canvas');
      canvas.width = 800;
      canvas.height = 600;
      el.appendChild(canvas);

      const ctx = canvas.getContext('2d');

      function draw() {
        const entities = model.get('entities');
        const pheromones = model.get('pheromones');

        // Clear
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, 800, 600);

        // Draw pheromone gradients
        for (const p of pheromones) {
          ctx.fillStyle = `rgba(${p.color}, ${p.intensity * 0.3})`;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
          ctx.fill();
        }

        // Draw entities with Brownian motion
        for (const e of entities) {
          ctx.fillStyle = e.color;
          ctx.font = '20px monospace';
          ctx.fillText(e.glyph, e.x, e.y);
        }

        requestAnimationFrame(draw);
      }
      draw();

      // Handle clicks -> update Python
      canvas.addEventListener('click', (e) => {
        model.set('clicked_pos', [e.offsetX, e.offsetY]);
        model.save_changes();
      });
    }
    """

    entities = traitlets.List([]).tag(sync=True)
    pheromones = traitlets.List([]).tag(sync=True)
    clicked_pos = traitlets.List([0, 0]).tag(sync=True)

    def __init__(self, garden):
        super().__init__()
        self._garden = garden
        self._update_state()

    def _update_state(self):
        self.entities = [e.to_dict() for e in self._garden.entities]
        self.pheromones = [p.to_dict() for p in self._garden.pheromone_grid.traces]
```

### DialecticWidget

```python
class DialecticWidget(anywidget.AnyWidget):
    """Three-panel thesis/antithesis/synthesis view."""

    _esm = """
    export function render({ model, el }) {
      el.innerHTML = `
        <div style="display: flex; gap: 10px;">
          <div class="panel thesis" style="flex: 1; border: 1px solid #4a9;">
            <h3>Thesis</h3>
            <div id="thesis-content"></div>
          </div>
          <div class="panel antithesis" style="flex: 1; border: 1px solid #a49;">
            <h3>Antithesis</h3>
            <div id="antithesis-content"></div>
          </div>
          <div class="panel synthesis" style="flex: 1; border: 1px solid #94a;">
            <h3>Synthesis</h3>
            <div id="synthesis-content"></div>
          </div>
        </div>
      `;

      model.on('change:dialectic_state', () => {
        const state = model.get('dialectic_state');
        el.querySelector('#thesis-content').innerHTML = state.thesis;
        el.querySelector('#antithesis-content').innerHTML = state.antithesis;
        el.querySelector('#synthesis-content').innerHTML = state.synthesis;
      });
    }
    """

    dialectic_state = traitlets.Dict({
        'thesis': '',
        'antithesis': '',
        'synthesis': ''
    }).tag(sync=True)
```

---

## Revised Wave Structure

### Wave 0: Marimo Foundation (NEW)

**Purpose**: Establish marimo as first-class citizen in kgents stack

| Task | Description | Files |
|------|-------------|-------|
| Add marimo dependency | `uv add marimo` | `pyproject.toml` |
| Create kgents-marimo package | Bridge module for integration | `impl/claude/agents/i/marimo/` |
| Basic anywidget infrastructure | Base class for kgents widgets | `impl/claude/agents/i/marimo/widgets/base.py` |
| Demo notebook | Proof of concept | `notebooks/kgents_demo.py` |

**Exit Criteria**: `marimo run notebooks/kgents_demo.py` shows basic stigmergic field

### Wave 1: The Foundation (Revised)

Add marimo-awareness to existing architecture:

| Component | Original | Marimo Extension |
|-----------|----------|------------------|
| EventBus | Phase 1 | Events trigger marimo cell updates |
| KgentsScreen | Phase 2 | Can embed marimo islands |
| Services | Phase 4 | `MarimoReactiveService` for state sync |

### Wave 2: The Widget Layer (Revised)

Build kgents widgets as **anywidgets first**, then wrap for Textual:

| Widget | anywidget | Textual Wrapper |
|--------|-----------|-----------------|
| StigmergicField | `StigmergicFieldWidget` | `StigmergicFieldTUI` (ASCII renderer) |
| DialecticPanel | `DialecticWidget` | `DialecticTUI` |
| Timeline | `TimelineWidget` | `TimelineTUI` |
| CompositionCanvas | `CompositionWidget` | `CompositionTUI` |

**Key Insight**: anywidget is the source of truth. Textual widgets are ASCII projections.

### Wave 3: The AGENTESE-Marimo Bridge

Map AGENTESE concepts to marimo's reactive model:

| AGENTESE | Marimo Equivalent |
|----------|-------------------|
| `world.*` paths | Cell inputs/outputs |
| `manifest` aspect | Cell execution producing Rich output |
| `witness` aspect | Cell that reads from history/logs |
| `refine` aspect | Multi-cell dialectic flow |
| Observer context | Marimo session state |

```python
# AGENTESE as marimo cells
@app.cell
def world_robin_manifest(robin: kg.Agent):
    """Equivalent to logos.invoke('world.robin.manifest')"""
    return robin.manifest(observer=kg.current_observer())

@app.cell
def world_robin_witness(robin: kg.Agent):
    """Equivalent to logos.invoke('world.robin.witness')"""
    return robin.witness()  # Returns narrative log
```

### Wave 4: Full Integration

| Feature | Implementation |
|---------|----------------|
| `kg garden` | Launches either TUI or marimo based on env |
| `kg notebook` | Opens marimo notebook for current project |
| `kg export --wasm` | Exports project as static WASM site |
| Marimo islands in docs | All kgents docs become interactive |

---

## Cross-Synergies Discovered

### Marimo + K-gent Persona

K-gent's personality can be expressed as marimo's AI integration:

```python
@app.cell
def kgent_dialogue():
    prompt = mo.ui.text_area(placeholder="Ask K-gent anything...")
    return prompt

@app.cell
def kgent_response(prompt, kgent: kg.Kgent):
    if prompt.value:
        response = kgent.dialogue(prompt.value)
        return mo.md(f"**K-gent**: {response}")
```

### Marimo + Polynomial Agents

Polynomial agent state machines map to marimo's lazy reactivity:

```python
@app.cell
def memory_agent():
    # D-gent memory polynomial: IDLE → LOADING → QUERYING → STORING
    agent = kg.MemoryAgent()
    mode_selector = mo.ui.dropdown(
        options=["IDLE", "LOADING", "QUERYING", "STORING"],
        label="Mode"
    )
    return agent, mode_selector

@app.cell(lazy=True)  # Lazy = only run when explicitly requested
def memory_operation(agent, mode_selector):
    """State-dependent behavior via polynomial."""
    agent.transition_to(mode_selector.value)
    return agent.current_state_output()
```

### Marimo Islands + Documentation

All kgents documentation becomes interactive:

```markdown
# K-gent Soul Interface

Here's a live demo of the soul polynomial:

<marimo-island>
  import kgents as kg
  soul = kg.Soul.demo()
  kg.widgets.SoulDashboard(soul)
</marimo-island>

Try changing the eigenvector context and watch the personality shift!
```

---

## The Generative UI Framework Vision

From the second PDF, the key principles apply perfectly:

### Terminal-First (with GUI as Progressive Enhancement)

1. **TUI is primary**: `kg garden` works in any terminal
2. **Marimo is enhancement**: Rich reactive UI when available
3. **WASM is deployment**: Static sites for sharing

### Functional Reactive Backbone

1. **DAG execution**: Marimo provides this natively
2. **No hidden state**: Both marimo and kgents enforce this
3. **Deterministic**: Same inputs → same outputs

### Agent as Co-worker

1. **Transparent actions**: Plans visible in dialectic dashboard
2. **Inspectable state**: All agent state in marimo cells
3. **Reversible**: Timeline scrubbing through history

---

## Implementation Roadmap

### Phase 1: Foundation (1-2 sessions)

```bash
# Add marimo to kgents
uv add marimo anywidget

# Create bridge package
mkdir -p impl/claude/agents/i/marimo
touch impl/claude/agents/i/marimo/__init__.py
touch impl/claude/agents/i/marimo/widgets/__init__.py

# Create demo notebook
touch notebooks/kgents_demo.py
```

### Phase 2: Core Widgets (2-3 sessions)

1. `StigmergicFieldWidget` (anywidget)
2. `GardenWidget` (container)
3. `AgentCardWidget` (single agent view)
4. Textual wrappers for all

### Phase 3: AGENTESE Bridge (2 sessions)

1. `LogosCell` - marimo cell that executes AGENTESE path
2. `ObserverContext` - marimo-native observer management
3. `AffordanceUI` - dynamic action generation

### Phase 4: Full Demo (1-2 sessions)

1. Complete demo notebook
2. WASM export working
3. Documentation islands
4. `kg garden` unified launcher

---

## Exit Criteria (Revised)

1. `marimo run notebooks/kgents_demo.py` shows full stigmergic garden
2. Widgets work in BOTH marimo AND Textual TUI
3. AGENTESE paths trigger reactive updates in marimo cells
4. `kg export --wasm` produces working static site
5. At least one doc page has live marimo island
6. Kent says "this is amazing" (HARD REQUIREMENT)

---

## The Enlightened Vision

The final state is a **unified reactive substrate** where:

- **Terminal users** get ASCII stigmergic fields in Textual TUI
- **Notebook users** get rich interactive marimo notebooks
- **Web users** get WASM-powered static sites
- **Documentation readers** get live interactive examples
- **All share the same underlying AGENTESE ontology**

The interface truly becomes what it always wanted to be: **"the field does not display state; it is state made visible."**

This is not two systems (Textual + marimo) bolted together. It's **one system with multiple projections**—the same category-theoretic principle that governs agent composition now governs UI rendering.

---

## Sources

Research incorporated from:
- [marimo documentation](https://docs.marimo.io/)
- [marimo anywidget integration](https://docs.marimo.io/api/inputs/anywidget/)
- [marimo WASM deployment](https://docs.marimo.io/guides/wasm/)
- [marimo islands](https://docs.marimo.io/guides/island_example/)
- [GitHub: marimo-team/marimo](https://github.com/marimo-team/marimo)
- [Real Python: marimo tutorial](https://realpython.com/marimo-notebook/)
- [Textual documentation](https://textual.textualize.io/)

---

*"The noun is a lie. There is only the rate of change. And now, the rate of change is visible."*
