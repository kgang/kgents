# Loss-Native Components: Technical Treatment

> *"Loss = Difficulty. Every node carries a Galois loss value."*

**Created**: 2025-12-24
**Depends on**: `radical-redesign-vision.md`, `spec/theory/galois-modularization.md`

---

## Core Abstraction: The Loss Signature

Every UI element should expose its semantic stability. This is not optional metadata—it is the fundamental quality signal.

### The `LossSignature` Type

```typescript
interface LossSignature {
  // Total loss: semantic drift from restructure-reconstitute cycle
  total: number;  // [0, 1]

  // Decomposed loss components
  components: {
    content: number;   // Text/data integrity after compression
    proof: number;     // Justification chain strength (L3+)
    edge: number;      // Relationship coherence
    metadata: number;  // Context preservation
  };

  // Derived status
  status: 'stable' | 'transitional' | 'unstable';

  // Fixed-point indicator
  isAxiomatic: boolean;  // total < FIXED_POINT_THRESHOLD (0.01)

  // Layer in epistemic hierarchy
  layer: 1 | 2 | 3 | 4 | 5 | 6 | 7;
}
```

### The `useLoss()` Hook

```typescript
function useLoss(nodeId: string): {
  signature: LossSignature | null;
  loading: boolean;
  error: Error | null;
  refresh: () => void;
}

// Usage
function AxiomCard({ nodeId }: { nodeId: string }) {
  const { signature, loading } = useLoss(nodeId);

  if (loading) return <Skeleton />;

  return (
    <div
      className="axiom-card"
      style={{
        '--loss-hue': lossToHue(signature.total),
        '--loss-pulse': signature.status === 'unstable' ? '1s' : '0s'
      }}
    >
      <LossBadge signature={signature} />
      {/* ... */}
    </div>
  );
}
```

---

## Visual Encoding: The Viridis System

### Color Palette

Viridis is perceptually uniform and colorblind-safe:

```css
:root {
  /* Loss gradient stops */
  --viridis-0: #440154;   /* L = 0.0, deep purple (axiomatic) */
  --viridis-25: #31688e;  /* L = 0.25, teal-blue (stable) */
  --viridis-50: #35b779;  /* L = 0.50, green (transitional) */
  --viridis-75: #90d743;  /* L = 0.75, lime (warning) */
  --viridis-100: #fde725; /* L = 1.0, bright yellow (critical) */

  /* Semantic aliases */
  --loss-axiomatic: var(--viridis-0);
  --loss-stable: var(--viridis-25);
  --loss-transitional: var(--viridis-50);
  --loss-warning: var(--viridis-75);
  --loss-critical: var(--viridis-100);
}
```

### CSS Loss Integration

```css
.loss-aware {
  /* Dynamic hue from loss value */
  background: linear-gradient(
    135deg,
    hsl(var(--loss-hue), 60%, 20%) 0%,
    hsl(var(--loss-hue), 50%, 15%) 100%
  );

  /* Pulse animation for unstable nodes */
  animation: loss-pulse var(--loss-pulse, 0s) ease-in-out infinite;
}

@keyframes loss-pulse {
  0%, 100% { box-shadow: 0 0 0 0 hsla(var(--loss-hue), 70%, 50%, 0.4); }
  50% { box-shadow: 0 0 20px 4px hsla(var(--loss-hue), 70%, 50%, 0.6); }
}
```

### The `<LossBadge />` Component

```tsx
interface LossBadgeProps {
  signature: LossSignature;
  size?: 'sm' | 'md' | 'lg';
  showComponents?: boolean;
}

export function LossBadge({
  signature,
  size = 'md',
  showComponents = false
}: LossBadgeProps) {
  const hue = lossToHue(signature.total);

  return (
    <div
      className={`loss-badge loss-badge--${size} loss-badge--${signature.status}`}
      style={{ '--loss-hue': hue }}
      title={`Loss: ${(signature.total * 100).toFixed(1)}%`}
    >
      {signature.isAxiomatic && <span className="axiom-marker">A</span>}
      <span className="loss-value">{formatLoss(signature.total)}</span>

      {showComponents && (
        <div className="loss-components">
          <ComponentBar label="C" value={signature.components.content} />
          <ComponentBar label="P" value={signature.components.proof} />
          <ComponentBar label="E" value={signature.components.edge} />
          <ComponentBar label="M" value={signature.components.metadata} />
        </div>
      )}
    </div>
  );
}
```

---

## Gradient Field Visualization

### The `useGradientField()` Hook

```typescript
interface GradientVector {
  nodeId: string;
  direction: { x: number; y: number };
  magnitude: number;  // Strength of gradient
  targetId: string;   // Lowest-loss neighbor
}

function useGradientField(visibleNodes: string[]): {
  vectors: Map<string, GradientVector>;
  loading: boolean;
}

// Compute gradient direction toward stability
function computeGradient(node: LossSignature, neighbors: LossSignature[]): GradientVector {
  const lowest = neighbors.reduce((a, b) => a.total < b.total ? a : b);
  const direction = normalizeVector(
    lowest.position.x - node.position.x,
    lowest.position.y - node.position.y
  );
  return {
    nodeId: node.id,
    direction,
    magnitude: node.total - lowest.total,
    targetId: lowest.id
  };
}
```

### SVG Gradient Overlay

```tsx
export function GradientFieldOverlay({
  vectors,
  bounds
}: {
  vectors: Map<string, GradientVector>;
  bounds: { width: number; height: number };
}) {
  return (
    <svg
      className="gradient-field-overlay"
      viewBox={`0 0 ${bounds.width} ${bounds.height}`}
    >
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7"
                refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="currentColor" />
        </marker>
      </defs>

      {Array.from(vectors.values()).map(vector => (
        <GradientArrow key={vector.nodeId} vector={vector} />
      ))}
    </svg>
  );
}

function GradientArrow({ vector }: { vector: GradientVector }) {
  const opacity = Math.min(1, vector.magnitude * 2);
  const length = 20 + vector.magnitude * 30;

  return (
    <line
      x1={vector.position.x}
      y1={vector.position.y}
      x2={vector.position.x + vector.direction.x * length}
      y2={vector.position.y + vector.direction.y * length}
      stroke={`rgba(255, 255, 255, ${opacity})`}
      strokeWidth={1 + vector.magnitude}
      markerEnd="url(#arrowhead)"
    />
  );
}
```

---

## Loss-Aware Navigation

### The `gl` / `gh` Commands

```typescript
// In useKeyHandler.ts
function handleLossNavigation(key: string, currentNode: string) {
  const neighbors = getNeighborLosses(currentNode);

  if (key === 'gl') {
    // Go to lowest-loss neighbor
    const target = neighbors.reduce((a, b) =>
      a.signature.total < b.signature.total ? a : b
    );
    navigate(target.id);
  } else if (key === 'gh') {
    // Go to highest-loss neighbor (investigate instability)
    const target = neighbors.reduce((a, b) =>
      a.signature.total > b.signature.total ? a : b
    );
    navigate(target.id);
  }
}
```

### Loss Threshold Filter

```tsx
export function LossThresholdSlider({
  value,
  onChange
}: {
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="loss-threshold-control">
      <label>
        Show nodes with loss ≤ {(value * 100).toFixed(0)}%
      </label>
      <input
        type="range"
        min={0}
        max={1}
        step={0.05}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{
          '--gradient': `linear-gradient(to right,
            var(--viridis-0) 0%,
            var(--viridis-50) 50%,
            var(--viridis-100) 100%
          )`
        }}
      />
    </div>
  );
}
```

---

## Component Stratification

### Layer-Based Component Registry

```typescript
const COMPONENT_LAYERS: Record<string, number> = {
  // L1-L2: Immutable primitives
  'ColorTokens': 1,
  'TypographyScale': 1,
  'LayoutGrid': 2,
  'Icon': 2,

  // L3: Stable scaffold
  'NavigationShell': 3,
  'CommandPalette': 3,
  'WitnessSidebar': 3,

  // L4: Evolving features
  'HypergraphEditor': 4,
  'AnalysisQuadrant': 4,
  'TelescopeControls': 4,

  // L5: Session interactions
  'SelectionState': 5,
  'FocusRing': 5,
  'ContextMenu': 5,

  // L6-L7: Ephemeral projections
  'RenderedContent': 6,
  'AnimationOverlay': 7,
  'TransientToast': 7,
};

// Dependency validation
function validateDependency(component: string, dependency: string): boolean {
  const componentLayer = COMPONENT_LAYERS[component];
  const dependencyLayer = COMPONENT_LAYERS[dependency];
  return dependencyLayer <= componentLayer;  // Can only depend on lower layers
}
```

---

## Integration Points

### With Zero Seed

The ZeroSeedPage becomes a lens on the loss landscape:

```tsx
// Before: Page with tabs
<ZeroSeedPage>
  <Tabs>
    <Tab>Axioms</Tab>
    <Tab>Proofs</Tab>
    <Tab>Health</Tab>
    <Tab>Telescope</Tab>
  </Tabs>
</ZeroSeedPage>

// After: Telescope focal distance
<TelescopeShell focalDistance={state.focalDistance}>
  {/* Content adapts to focal distance automatically */}
  <LossTopography nodes={visibleNodes} />
  <GradientFieldOverlay vectors={gradients} />
  <FocalPointMarker node={focalPoint} />
</TelescopeShell>
```

### With Analysis Operad

Each analysis mode gets a loss-aware panel:

```tsx
<AnalysisQuadrant mode="categorical">
  <LossBadge signature={categoricalLoss} showComponents />
  {categoricalReport.violations.map(v => (
    <ViolationCard key={v.id} violation={v} />
  ))}
</AnalysisQuadrant>
```

---

## Performance Considerations

1. **Batch loss computation**: Compute losses for visible nodes only
2. **Memoize gradients**: Recalculate only when nodes change
3. **Virtualize large graphs**: Render only nodes in viewport
4. **Debounce threshold changes**: Avoid re-renders during slider drag

---

*Filed: 2025-12-24 | Loss-Native Components Technical Treatment*
