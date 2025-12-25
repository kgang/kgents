# The Telescope as Shell: Unified Navigation Architecture

> *"The file is a lie. There is only the graph."*
> *"Surfaces are not applications. They are focal distances."*

**Created**: 2025-12-24
**Depends on**: `radical-redesign-vision.md`, `spec/protocols/zero-seed1/navigation.md`

---

## The Core Insight

The current architecture treats `/editor`, `/director`, `/zero-seed`, `/brain`, `/chart` as separate applications sharing a navigation bar. This is the antithesis of our philosophy.

**The radical alternative**: There is one application—the Telescope. Every "surface" is a focal distance on the same hypergraph. Zooming out shows axioms as constellations. Zooming in shows the current document as editable text.

---

## Focal Distance Model

### The Spectrum

```
Focal Distance    Layer   Visible Content             Interaction Mode
──────────────────────────────────────────────────────────────────────────
∞ (Cosmic)        L1      Axiom constellations        Pan/zoom, select
1000              L2      Value clusters              Filter by principle
100               L3      Goal networks               Navigate edges
10                L4      Specification trees         Expand/collapse
1                 L5-L6   Action/reflection trails    Timeline scroll
0 (Ground)        L7      Document content            Full editing (vim)
```

### State Representation

```typescript
interface TelescopeState {
  // Current focal distance (0 = ground, ∞ = cosmic)
  focalDistance: number;

  // Focal point (the node we're centered on)
  focalPoint: NodeId | null;

  // Visible layers at current distance
  visibleLayers: number[];

  // Loss threshold filter
  lossThreshold: number;

  // Gradient field visibility
  showGradients: boolean;

  // Selected nodes (for multi-select operations)
  selection: Set<NodeId>;
}
```

---

## Unified Shell Component

### The `<TelescopeShell />`

```tsx
export function TelescopeShell({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useTelescopeState();
  const { gradients } = useGradientField(state.visibleNodes);

  return (
    <TelescopeContext.Provider value={{ state, dispatch }}>
      <div className="telescope-shell">
        {/* Gradient field overlay (always visible, intensity varies) */}
        <GradientFieldOverlay
          vectors={gradients}
          opacity={state.focalDistance > 10 ? 1 : 0.3}
        />

        {/* Focal distance indicator */}
        <FocalDistanceRuler
          value={state.focalDistance}
          onChange={(d) => dispatch({ type: 'SET_FOCAL_DISTANCE', distance: d })}
        />

        {/* Loss threshold control */}
        <LossThresholdSlider
          value={state.lossThreshold}
          onChange={(t) => dispatch({ type: 'SET_LOSS_THRESHOLD', threshold: t })}
        />

        {/* Dynamic content based on focal distance */}
        <TelescopeViewport focalDistance={state.focalDistance}>
          {children}
        </TelescopeViewport>

        {/* Focal point breadcrumb trail */}
        <DerivationTrail focalPoint={state.focalPoint} />

        {/* Command line (always accessible) */}
        <CommandLine />
      </div>
    </TelescopeContext.Provider>
  );
}
```

### Automatic View Selection

```tsx
function TelescopeViewport({
  focalDistance,
  children
}: {
  focalDistance: number;
  children: React.ReactNode;
}) {
  // Select view based on focal distance
  if (focalDistance >= 1000) {
    return <CosmicView />;  // L1 axiom constellations
  } else if (focalDistance >= 100) {
    return <ClusterView />;  // L2-L3 value/goal clusters
  } else if (focalDistance >= 10) {
    return <TreeView />;  // L4 specification trees
  } else if (focalDistance >= 1) {
    return <TrailView />;  // L5-L6 action trails
  } else {
    return <GroundView>{children}</GroundView>;  // L7 full editor
  }
}
```

---

## Navigation Commands

### Zoom Commands

| Key | Action | Effect |
|-----|--------|--------|
| `gL` | Zoom out | `focalDistance *= 10` (max ∞) |
| `gH` | Zoom in | `focalDistance /= 10` (min 0) |
| `g1`..`g7` | Jump to layer | Set focal distance for that layer |
| `g0` | Ground | `focalDistance = 0` (full editor) |
| `g∞` | Cosmic | `focalDistance = Infinity` (axiom view) |

### Focal Point Commands

| Key | Action | Effect |
|-----|--------|--------|
| `gf` | Focus | Set current node as focal point |
| `gd` | Derivation | Navigate to derivation parent |
| `gc` | Children | Show children menu |
| `gr` | Root | Jump to axiom root (L1) |
| `g↵` | Trail | Show full derivation path |

### Loss Navigation

| Key | Action | Effect |
|-----|--------|--------|
| `gl` | Low | Jump to lowest-loss neighbor |
| `gh` | High | Jump to highest-loss neighbor |
| `gL` | Stable | Jump to most stable region (global low) |
| `gH` | Unstable | Jump to most unstable region (investigate) |

---

## Transition Animations

### Zoom Transitions

```css
.telescope-viewport {
  transition:
    transform 400ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 200ms ease-out;
}

.telescope-viewport--zooming-out {
  transform: scale(0.8);
  opacity: 0.7;
}

.telescope-viewport--zooming-in {
  transform: scale(1.2);
  opacity: 0.7;
}
```

### Focal Point Transitions

```tsx
function useFocalPointTransition(from: NodeId, to: NodeId) {
  // Calculate path between nodes
  const path = computeDerivationPath(from, to);

  // Animate through intermediate nodes
  return {
    keyframes: path.map((node, i) => ({
      offset: i / (path.length - 1),
      transform: `translate(${node.x}px, ${node.y}px)`,
      opacity: i === 0 || i === path.length - 1 ? 1 : 0.5
    })),
    duration: 300 + path.length * 100  // Longer paths take longer
  };
}
```

---

## Context Preservation

### The Problem

In the current architecture, navigating from `/zero-seed` (viewing an axiom) to `/editor` (editing a spec) loses the axiom context. The user forgets what grounded the spec.

### The Solution: Ghost Context

When zooming in from L1→L7, the higher-layer context appears as a "ghost":

```tsx
function GroundView({ children }: { children: React.ReactNode }) {
  const { focalHistory } = useTelescope();

  // Show ghost of axiom context
  const axiomGhost = focalHistory.find(n => n.layer <= 2);

  return (
    <div className="ground-view">
      {axiomGhost && (
        <GhostContext node={axiomGhost}>
          <span className="ghost-label">Grounded in: {axiomGhost.title}</span>
        </GhostContext>
      )}

      {/* Full editor content */}
      {children}
    </div>
  );
}
```

```css
.ghost-context {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  padding: 8px 16px;
  background: linear-gradient(
    to bottom,
    rgba(var(--viridis-0-rgb), 0.9) 0%,
    rgba(var(--viridis-0-rgb), 0) 100%
  );
  pointer-events: none;
  z-index: 100;
}
```

---

## Replacing React Router

### Current (Route-Based)

```tsx
// App.tsx
<Routes>
  <Route path="/editor/*" element={<HypergraphEditorPage />} />
  <Route path="/director" element={<DirectorPage />} />
  <Route path="/zero-seed" element={<ZeroSeedPage />} />
  <Route path="/brain" element={<BrainPage />} />
</Routes>
```

### Radical (Telescope-Based)

```tsx
// App.tsx
<TelescopeShell>
  <Routes>
    {/* Routes become focal distance hints, not page switches */}
    <Route path="/axioms" element={<FocalDistanceHint distance={1000} />} />
    <Route path="/values" element={<FocalDistanceHint distance={500} />} />
    <Route path="/specs/*" element={<FocalDistanceHint distance={10} />} />
    <Route path="/doc/*" element={<FocalDistanceHint distance={0} />} />
  </Routes>
</TelescopeShell>

function FocalDistanceHint({ distance }: { distance: number }) {
  const { dispatch } = useTelescope();

  useEffect(() => {
    dispatch({ type: 'SET_FOCAL_DISTANCE', distance });
  }, [distance]);

  return null;  // No UI, just state effect
}
```

URLs become bookmarks into telescope state, not page switches:
- `kgents.app/axioms` → Telescope at cosmic view
- `kgents.app/doc/spec/theory/galois.md` → Telescope at ground view, focused on galois.md

---

## AGENTESE Integration

The telescope becomes a projection surface for AGENTESE:

```typescript
// Navigation via AGENTESE
logos.invoke('void.telescope.focus', {
  path: 'self.memory.crystal',
  focalDistance: 10
});

// The telescope reacts to AGENTESE invocations
useEffect(() => {
  const unsubscribe = logos.subscribe('void.telescope.*', (event) => {
    if (event.path === 'void.telescope.focus') {
      dispatch({
        type: 'FOCUS_NODE',
        nodeId: event.payload.path,
        distance: event.payload.focalDistance
      });
    }
  });
  return unsubscribe;
}, []);
```

---

## Migration Path

### Phase 1: Parallel Shell

Keep existing pages but wrap in TelescopeShell:

```tsx
<TelescopeShell>
  <Routes>
    <Route path="/editor/*" element={<HypergraphEditorPage />} />
    {/* ... existing routes ... */}
  </Routes>
</TelescopeShell>
```

### Phase 2: Unified State

Extract navigation state from individual pages into telescope context.

### Phase 3: View Fusion

Replace page components with focal-distance-aware views that share the same graph state.

### Phase 4: Route Elimination

Remove explicit routes; let telescope state drive URL (reverse binding).

---

## The End State

There is no "Director page" or "Zero Seed page." There is only the hypergraph, viewed through a telescope. The user never "switches apps"—they zoom in and out of the knowledge landscape, always grounded by visible axioms, always guided by loss gradients toward stability.

*"The file is a lie. There is only the graph."*
*Now the app is the graph.*

---

*Filed: 2025-12-24 | Telescope as Shell Architecture*
