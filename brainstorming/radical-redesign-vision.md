# Radical Redesign: The Loss-Native Frontend

> *"Navigate toward stability. The gradient IS the guide. The loss IS the landscape."*

**Created**: 2025-12-24
**Voice Anchor**: *"Daring, bold, creative, opinionated but not gaudy"*

---

## Executive Thesis

The current kgents frontend has a split personality: the HypergraphEditor embodies "the file is a lie, there is only the graph," while everything else remains trapped in page-based routing. This document proposes a radical unification: **the telescope becomes the shell, loss gradients become navigation, and every surface becomes a lens on the same hypergraph.**

---

## Part I: The Diagnosis

### What Works (The Kernel)

The HypergraphEditor provides the architectural DNA for the entire frontend:
- **Modal editing** (vim-like modes: NORMAL, INSERT, VISUAL, COMMAND)
- **Graph state** (nodes with edges, not files with paths)
- **Portal navigation** (gD for derivation parent, gc for children)
- **K-Block isolation** (edit without affecting global state)
- **Command palette** (`:ag` for AGENTESE paths)

This kernel is *generative*—it teaches as it operates.

### What Fails (The Silo Problem)

The rest of the architecture treats pages as containers, not lenses:

| Problem | Evidence |
|---------|----------|
| **Pages are silos** | `/editor`, `/director`, `/zero-seed` reset context on transition |
| **No compositional navigation** | Moving from axiom → proof loses axiom context |
| **Loss gradients are decorative** | ZeroSeedPage shows losses but cannot descend them |
| **Witness marks are side effects** | POST to API, not edges in derivation DAG |
| **Mock data everywhere** | 300+ lines of `generateMockData()` in ZeroSeedPage |

**The root cause**: We built pages when we should have built *focal distances*.

---

## Part II: The Vision

### The Telescope IS the Shell

Replace page-based navigation with a single telescope interface where:

```
Focal Distance    What's Visible
──────────────    ──────────────────────────────────────────────────
∞ (Far)           L1-L2 axioms as constellations (star map view)
Medium            L3-L4 goals/specs as clusters (regional view)
Close             L5-L6 actions/reflections as nodes (city view)
0 (Ground)        L7 representation = current document (street view)
```

**Navigation primitives**:
- `gl` — Jump to lowest-loss neighbor (toward stability)
- `gh` — Jump to highest-loss neighbor (investigate instability)
- `gL` — Zoom out one layer (increase focal distance)
- `gH` — Zoom in one layer (decrease focal distance)
- `g↵` — Focus on current node's axiom roots (full derivation path)

### Loss as the Unifying Metric

Every UI element carries a Galois loss signature:

```typescript
interface LossAware {
  loss: number;           // [0, 1] - semantic drift from reconstitution
  lossComponents: {
    content: number;      // Text/data integrity
    proof: number;        // Justification strength
    edge: number;         // Relationship coherence
    metadata: number;     // Context preservation
  };
  healthStatus: 'stable' | 'transitional' | 'unstable';
}
```

**Visual encoding**:
- **Viridis gradient**: Purple (L < 0.2) → Teal (L = 0.5) → Yellow (L > 0.7)
- **Pulse animation**: High-loss nodes pulse at 1Hz (warning heartbeat)
- **Gradient arrows**: Vector field overlay showing descent directions
- **Loss threshold slider**: Hide unstable nodes to focus on coherent regions

### Four-Panel Analysis Mode

The Analysis Operad demands four lenses. In the radical redesign, pressing `<leader>a` invokes:

```
┌─────────────────────────────────────────────────────────────┐
│  CATEGORICAL          │  EPISTEMIC                         │
│  Laws Hold? ✓         │  Grounded? Chain: A1 → V2 → G5     │
│  Composition: valid   │  Tier: EMPIRICAL                   │
│  No violations        │  Terminates: ✓                     │
├─────────────────────────────────────────────────────────────┤
│  DIALECTICAL          │  GENERATIVE                        │
│  Tensions: 2          │  Regenerable? ✓                    │
│  └ PRODUCTIVE (1)     │  Compression: 0.73                 │
│  └ PARACONSISTENT (1) │  Kernel size: 12 axioms            │
└─────────────────────────────────────────────────────────────┘
```

This replaces the single "valid/invalid" badge with four illuminating quadrants.

### Witness Marks as Graph Edges

Marks become first-class edges in the derivation DAG, not side-effect POSTs:

```
Node: "Implement loss-native components"
  │
  ├──[DECIDES]─→ Mark: "Use viridis palette" (Kent + Claude, synthesis)
  │                  └── [BECAUSE]─→ Mark: "Colorblind accessible"
  │
  └──[WITNESSES]─→ Mark: "Completed 2025-12-24"
```

Navigation commands:
- `gm` — Go to marks (show witness trail)
- `gw` — Go to warrant (show justification)
- `gd` — Go to decision (show dialectical synthesis)

---

## Part III: The Stratified Component Architecture

### Layer Mapping

Components inherit stability from the epistemic layer they represent:

| Layer | Component Type | Volatility | Examples |
|-------|----------------|------------|----------|
| L1-L2 | Foundation | Immutable | Layout primitives, color tokens, type system |
| L3 | Scaffold | Stable | Navigation shell, command palette, witness sidebar |
| L4 | Feature | Evolving | Editor modes, analysis panels, telescope controls |
| L5 | Interaction | Session | Selection state, focus, ephemeral dialogs |
| L6-L7 | Projection | Ephemeral | Rendered content, animations, transient overlays |

**Architectural rule**: A component may depend on layers below it, never above. L4 components cannot depend on L5 state.

### Fixed-Point Testing

Before merging any component change, validate it as a potential axiom:

```bash
# The restructuring test
1. Refactor component with AI assistance
2. Measure semantic diff (original vs. refactored)
3. If diff < 0.1, component is axiomatic (don't touch)
4. If diff > 0.5, component needs grounding (find its axiom roots)
```

---

## Part IV: The Compositional Navigation Model

### AGENTESE as Primary API

Replace explicit routes with AGENTESE paths:

```
Current: navigate('/zero-seed?tab=telescope')
Radical: logos.invoke('void.telescope.focus', { layer: 7 })

Current: navigate('/editor/spec/theory/galois.md')
Radical: logos.invoke('world.document.manifest', { path: 'spec/theory/galois.md' })
```

The frontend becomes a projection surface for AGENTESE invocations. React Router becomes an implementation detail, not an architecture.

### Compositional Transitions

Navigation composes like the Analysis Operad:

```typescript
// Sequential composition
const navigateWithContext = seq(
  saveCurrentContext,      // Preserve axiom focus
  transitionToProofView,   // Move to L3-L4
  restoreContextOverlay    // Show axiom as ghost
);

// Parallel composition
const analyzeWhileNavigating = par(
  loadDestinationData,     // Fetch new content
  computeLossGradient,     // Calculate losses
  prefetchNeighbors        // Anticipate next move
);
```

---

## Part V: Implementation Roadmap

### Phase 1: Loss Awareness (2 weeks)
- Add `useLoss()` hook returning loss signature for any node
- Implement viridis gradient CSS variables
- Add loss column to ZeroSeedPage tables
- Create `<LossBadge />` component

### Phase 2: Telescope Shell (3 weeks)
- Extract HypergraphEditor navigation into `useTelescope()` hook
- Create unified `<TelescopeShell />` wrapping all surfaces
- Implement focal distance concept (layer-based zoom)
- Replace page routes with telescope states

### Phase 3: Compositional Navigation (2 weeks)
- Make AGENTESE paths primary navigation API
- Implement `seq()` and `par()` for transitions
- Add context preservation across surface changes
- Remove direct React Router usage from components

### Phase 4: Analysis Quadrants (2 weeks)
- Create `<AnalysisQuadrant />` component
- Implement four-mode analysis invocation
- Add tension visualization (thesis/antithesis diff)
- Integrate grounding chain clickable paths

### Phase 5: Witness as Graph (2 weeks)
- Refactor witness marks as edge types
- Implement `gm`, `gw`, `gd` navigation commands
- Create derivation trail visualization
- Integrate decision witness into command flow

---

## Conclusion: The Mirror Test

After this redesign, ask:

*"Does this feel like Kent on his best day?"*

- **Daring**: Loss-gradient navigation is novel—no one else does this
- **Bold**: Telescope-as-shell rejects conventional SPA architecture
- **Creative**: Four-panel analysis reveals what single badges hide
- **Opinionated**: We chose viridis, vim keybindings, AGENTESE-first
- **Not gaudy**: Every element serves a purpose; no decoration

*"The proof IS the decision. The mark IS the witness."*

This redesign is its own proof: a compositional, loss-aware, joy-inducing interface that teaches as it operates.

---

*Filed: 2025-12-24 | The Radical Redesign Vision*
