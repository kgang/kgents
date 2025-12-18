# Gallery V2: Living Autopoietic Showcase

> *"The Gallery is not a catalogue of components—it is a living demonstration of the categorical ground."*

**Status:** Proposed
**Spirit Preservation:** ✅ The current Gallery's elegance (category filtering, projection comparison, override controls) is maintained and enhanced.

---

## Purpose (Tasteful Principle)

The Gallery demonstrates the **Projection Protocol** in action. But the current implementation shows only **reactive primitives** (Layer 7: Projection Surfaces). The full kgents system has seven layers (AD-009 Metaphysical Stack), and the Gallery should inspire understanding of all of them.

**Why this needs to exist:**
1. New contributors need to see the categorical ground in action, not just widget rendering
2. Crown Jewel developers need inspiration for how primitives compose
3. The Gallery itself should be a vertical slice (eating our own cooking)

---

## The Core Insight

> *"The Gallery is a meta-vertical-slice: it demonstrates the vertical slice pattern BY being one."*

The current Gallery shows:
- **What**: Widget projections (CLI, HTML, JSON)
- **How**: Override controls (entropy, seed, phase)

The enhanced Gallery shows:
- **What**: Widgets + Polynomials + Operads + Crown Jewels
- **How**: Override controls + State machine simulation + Law verification
- **Why**: AGENTESE paths + Categorical composition + Live introspection

---

## Integration with Autopoietic Architecture

### The Gallery as Vertical Slice (AD-009)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES                                                     │
│     GalleryPage.tsx + PilotCard + ProjectionView (enhanced)                │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE UNIVERSAL PROTOCOL                                             │
│     NEW: world.emergence.gallery.manifest → Gallery data via AGENTESE      │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE                                                           │
│     NEW: @node("world.emergence.gallery") with pilot discovery             │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE                                                          │
│     protocols/projection/gallery/ (exists, enhance)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR                                                          │
│     NEW: GALLERY_OPERAD (show, filter, simulate, verify)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT                                                        │
│     NEW: GalleryPolynomial (BROWSING, INSPECTING, SIMULATING, VERIFYING)   │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE                                                         │
│     Pilot projections must be consistent across targets                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Formal Definition

### GalleryPolynomial

```python
class GalleryPhase(Enum):
    BROWSING = auto()     # Viewing pilot grid
    INSPECTING = auto()   # Viewing pilot detail modal
    SIMULATING = auto()   # Stepping through state machine
    VERIFYING = auto()    # Running operad law checks

# GalleryPolynomial[GalleryPhase, GalleryInput, GalleryOutput]
GALLERY_POLYNOMIAL = PolyAgent(
    name="GalleryPolynomial",
    positions=frozenset(GalleryPhase),
    _directions=gallery_directions,  # What inputs are valid per phase
    _transition=gallery_transition,   # State machine
)

# Directions: mode-dependent inputs
def gallery_directions(phase: GalleryPhase) -> FrozenSet[Type]:
    match phase:
        case GalleryPhase.BROWSING:
            return frozenset([FilterInput, SelectPilotInput, OverrideInput])
        case GalleryPhase.INSPECTING:
            return frozenset([CloseInput, SimulateInput, VerifyInput])
        case GalleryPhase.SIMULATING:
            return frozenset([StepInput, ResetInput, CloseInput])
        case GalleryPhase.VERIFYING:
            return frozenset([CloseInput])
```

### GALLERY_OPERAD

```python
GALLERY_OPERAD = Operad(
    name="GalleryOperad",
    operations={
        # Arity 0: nullary operations
        "reset": Operation(name="reset", arity=0),

        # Arity 1: unary operations
        "filter": Operation(name="filter", arity=1),  # category → filtered pilots
        "select": Operation(name="select", arity=1),  # pilot → detail view
        "override": Operation(name="override", arity=1),  # overrides → re-render

        # Arity 2: binary operations
        "compare": Operation(name="compare", arity=2),  # pilot × pilot → diff
        "compose": Operation(name="compose", arity=2),  # pilot × pilot → combined
    },
    laws=[
        Law("filter_identity", "filter(ALL) = identity"),
        Law("override_deterministic", "override(o) >> override(o) = override(o)"),
        Law("compare_symmetric", "compare(a, b) ≅ compare(b, a)"),
    ],
)
```

---

## New Categories (Maintain Spirit + Extend)

### Current Categories (Preserved)
- **PRIMITIVES** - Glyph, Bar, Sparkline ✅
- **CARDS** - AgentCard, YieldCard ✅
- **CHROME** - ErrorPanel, RefusalPanel ✅
- **STREAMING** - Progress, StreamState ✅
- **COMPOSITION** - HStack, VStack ✅
- **ADAPTERS** - Textual, Marimo ✅
- **SPECIALIZED** - DensityField, DialecticCard ✅

### New Categories (Extending the Breadth)
- **POLYNOMIAL** - State machine visualizations
  - CitizenPolynomial (5 phases: IDLE → SOCIALIZING → WORKING → REFLECTING → RESTING)
  - GardenerPolynomial (3 phases: SENSE → ACT → REFLECT)
  - BrainPolynomial (5 phases: IDLE → CAPTURING → SEARCHING → SURFACING → HEALING)
  - DirectorPolynomial (5 phases: OBSERVING → EVALUATING → INJECTING → INTERVENING → COOLING)

- **OPERAD** - Composition grammar visualizations
  - TOWN_OPERAD (greet, gossip, trade, solo, dispute, celebrate, mourn, teach)
  - SOUL_OPERAD (introspect, shadow, dialectic)
  - BRAIN_OPERAD (capture, search, surface, heal, associate)
  - DESIGN_OPERAD (Layout × Content × Motion naturality)

- **CROWN_JEWELS** - Full vertical slice mini-demos
  - Agent Town (live citizen grid)
  - Punchdrunk Park (crisis phase controls)
  - Holographic Brain (crystal topology)
  - Gestalt (architecture health)
  - Atelier (builder flow)
  - Gardener (N-phase indicator)

- **LAYOUT** - Design Language System
  - ElasticSplit (density-adaptive)
  - BottomDrawer (mobile)
  - FloatingSidebar (compact)
  - CoordinatedDrawers (composition)

---

## New Features

### 1. Polynomial Simulation Panel

When a POLYNOMIAL pilot is selected, show an interactive state machine:

```
┌────────────────────────────────────────────────────────────────┐
│  CitizenPolynomial Simulation                              [×] │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│     ┌──────┐      ┌───────────┐      ┌─────────┐              │
│     │ IDLE │ ───▶ │SOCIALIZING│ ───▶ │ WORKING │              │
│     └──────┘      └───────────┘      └─────────┘              │
│        ▲               │                  │                    │
│        │               ▼                  ▼                    │
│     ┌──────┐      ┌───────────┐      ┌─────────┐              │
│     │RESTING│ ◀── │REFLECTING │ ◀──  │         │              │
│     └──────┘      └───────────┘      └─────────┘              │
│                                                                │
│  Current: [SOCIALIZING]  Valid inputs: [work, rest, reflect]   │
│                                                                │
│  [ Step: work ]  [ Step: rest ]  [ Reset ]                    │
└────────────────────────────────────────────────────────────────┘
```

### 2. Operad Law Verification Panel

When an OPERAD pilot is selected, show law verification:

```
┌────────────────────────────────────────────────────────────────┐
│  TOWN_OPERAD Laws                                          [×] │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Operations: 8 registered                                      │
│  ├─ greet (arity: 2)                                          │
│  ├─ gossip (arity: 2)                                         │
│  ├─ trade (arity: 2)                                          │
│  └─ ...                                                       │
│                                                                │
│  Laws: 3 verified ✅                                           │
│  ├─ locality: greet(a,b) affects only a,b neighbors    ✅     │
│  ├─ rest_inviolability: RESTING only accepts wake      ✅     │
│  └─ coherence_preservation: ops preserve sheaf         ✅     │
│                                                                │
│  [ Verify All ]  [ Show Counterexample ]                      │
└────────────────────────────────────────────────────────────────┘
```

### 3. Crown Jewel Mini-Demo

When a CROWN_JEWELS pilot is selected, show a live mini-demo:

```
┌────────────────────────────────────────────────────────────────┐
│  Agent Town Mini-Demo                                      [×] │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────┐      │
│  │  🧑 Socrates     🧑 Hypatia      🧑 Marcus          │      │
│  │  SOCIALIZING    WORKING         REFLECTING          │      │
│  │                                                     │      │
│  │  🧑 Ada         🧑 Leonardo                         │      │
│  │  IDLE          RESTING                              │      │
│  └─────────────────────────────────────────────────────┘      │
│                                                                │
│  AGENTESE: world.town.manifest                                 │
│  Polynomial: CITIZEN_POLYNOMIAL (5 phases)                     │
│  Operad: TOWN_OPERAD (8 operations, 3 laws)                   │
│                                                                │
│  [ Open Full App ]  [ Show AGENTESE Paths ]                   │
└────────────────────────────────────────────────────────────────┘
```

### 4. AGENTESE Path Browser

A new sidebar showing all registered AGENTESE paths organized by context:

```
┌─────────────────────────────────────────┐
│  AGENTESE Paths (16 registered)         │
├─────────────────────────────────────────┤
│  ▼ self.*                               │
│    ├─ self.memory.manifest              │
│    ├─ self.memory.capture               │
│    ├─ self.chat                         │
│    └─ self.forest                       │
│                                         │
│  ▼ world.*                              │
│    ├─ world.town.manifest               │
│    ├─ world.atelier.manifest            │
│    ├─ world.park.manifest               │
│    ├─ world.codebase.manifest           │
│    └─ world.emergence.manifest          │
│                                         │
│  ▼ concept.*                            │
│    └─ concept.gardener.manifest         │
└─────────────────────────────────────────┘
```

---

## Density-Adaptive Layout

The Gallery uses the Design Language System (AD-008 isomorphisms):

| Density | Layout | Behavior |
|---------|--------|----------|
| **compact** (mobile) | Single column grid + Bottom drawer for detail | Categories collapse to icons |
| **comfortable** (tablet) | 2-column grid + Side panel | Category names visible |
| **spacious** (desktop) | 3-5 column grid + Full sidebar + Detail panel | All features visible |

---

## Implementation Phases

### Phase 1: Backend Vertical Slice (Layer 2-5)
- [ ] Create `agents/gallery/polynomial.py` with GalleryPolynomial
- [ ] Create `agents/gallery/operad.py` with GALLERY_OPERAD
- [ ] Register in OperadRegistry
- [ ] Create `services/gallery/node.py` with @node("world.emergence.gallery")
- [ ] Wire into gateway.py

### Phase 2: New Pilot Categories (Layer 4)
- [ ] Add POLYNOMIAL category with state machine pilots
- [ ] Add OPERAD category with law verification pilots
- [ ] Add CROWN_JEWELS category with mini-demo pilots
- [ ] Add LAYOUT category with design system pilots

### Phase 3: Frontend Enhancement (Layer 7)
- [ ] PolynomialSimulationPanel component
- [ ] OperadLawsPanel component
- [ ] CrownJewelMiniDemo component
- [ ] AGENTESEPathBrowser sidebar
- [ ] Density-adaptive layout integration

### Phase 4: Integration & Polish
- [ ] Connect frontend to AGENTESE gateway (not direct API)
- [ ] Add streaming for simulation steps
- [ ] Add keyboard shortcuts for power users
- [ ] Responsive design validation

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Correct Pattern |
|--------------|---------|-----------------|
| Direct REST API calls | Bypasses AGENTESE | Route through `logos.invoke()` |
| Hardcoded pilot list | Can't discover new pilots | Use pilot registry |
| Scattered density conditionals | Unmaintainable | Density-parameterized constants |
| Monolithic GalleryPage | Hard to test | Decompose into slot/filler pattern |

---

## AGENTESE Integration Points

### Paths to Register

```python
GALLERY_PATHS = {
    "world.emergence.gallery.manifest": {
        "aspect": "manifest",
        "description": "Gallery overview with categories and counts",
        "effects": [],
    },
    "world.emergence.gallery.pilots.manifest": {
        "aspect": "manifest",
        "description": "List all pilots with projections",
        "effects": [],
    },
    "world.emergence.gallery.pilot[name].manifest": {
        "aspect": "manifest",
        "description": "Single pilot detail with all projections",
        "effects": [],
    },
    "world.emergence.gallery.polynomial.simulate": {
        "aspect": "define",
        "description": "Step polynomial simulation forward",
        "effects": ["STATE_TRANSITION"],
    },
    "world.emergence.gallery.operad.verify": {
        "aspect": "manifest",
        "description": "Verify operad laws",
        "effects": [],
    },
}
```

---

## Connection to Other Specs

| Spec | Connection |
|------|------------|
| `spec/protocols/projection.md` | Gallery demonstrates the Projection Protocol |
| `spec/protocols/agentese.md` | Gallery uses AGENTESE for all data fetching |
| `plans/autopoietic-architecture.md` | Gallery is itself a vertical slice |
| `docs/skills/vertical-slice-pattern.md` | Gallery follows the 7-layer pattern |
| `plans/design-language-consolidation.md` | Gallery uses Layout × Content × Motion |

---

## Success Criteria

1. **Educational**: New contributor understands PolyAgent, Operad, Sheaf within 5 minutes of browsing
2. **Inspiring**: Crown Jewel developers see composition patterns they can reuse
3. **Complete**: Gallery is a full vertical slice (passes compliance check)
4. **Joy-Inducing**: Polynomial simulation and law verification are genuinely delightful

---

## The Autopoietic Test

> *"Can you regenerate the Gallery from this spec?"*

If yes, the spec is generative. The Gallery V2 should be derivable from:
1. This spec
2. The existing pilot registry
3. The registered operads in OperadRegistry
4. The polynomial agents in agents/*/polynomial.py
5. The Crown Jewel nodes in services/*/node.py

---

*"The Gallery that shows only widgets is a catalogue. The Gallery that shows the categorical ground is a teacher."*
