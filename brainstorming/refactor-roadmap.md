# Refactor Roadmap: From Pages to Lenses

> *"Every refactor should pass the Mirror Test."*

**Created**: 2025-12-24
**Priority**: Incremental adoption, no big-bang rewrites

---

## Immediate Refactors (This Sprint)

### 1. Add `useLoss()` Hook

**File**: `impl/claude/web/src/hooks/useLoss.ts`

```typescript
import { useState, useEffect } from 'react';

export interface LossSignature {
  total: number;
  components: {
    content: number;
    proof: number;
    edge: number;
    metadata: number;
  };
  status: 'stable' | 'transitional' | 'unstable';
  isAxiomatic: boolean;
  layer: 1 | 2 | 3 | 4 | 5 | 6 | 7;
}

export function useLoss(nodeId: string | null): {
  signature: LossSignature | null;
  loading: boolean;
  error: Error | null;
} {
  const [signature, setSignature] = useState<LossSignature | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!nodeId) {
      setSignature(null);
      return;
    }

    setLoading(true);
    fetch(`/api/zero-seed/nodes/${encodeURIComponent(nodeId)}`)
      .then(res => res.json())
      .then(data => {
        setSignature({
          total: data.loss.loss,
          components: data.loss.components,
          status: data.loss.health_status,
          isAxiomatic: data.loss.loss < 0.01,
          layer: data.node.layer
        });
        setError(null);
      })
      .catch(err => setError(err))
      .finally(() => setLoading(false));
  }, [nodeId]);

  return { signature, loading, error };
}
```

**Effort**: 1 hour

---

### 2. Add `<LossBadge />` Component

**File**: `impl/claude/web/src/components/zero-seed/LossBadge.tsx`

```tsx
import { memo } from 'react';
import type { LossSignature } from '../../hooks/useLoss';
import './LossBadge.css';

interface LossBadgeProps {
  signature: LossSignature;
  size?: 'sm' | 'md' | 'lg';
  showComponents?: boolean;
}

function lossToHue(loss: number): number {
  // Viridis: purple (280°) → teal (180°) → yellow (60°)
  return 280 - loss * 220;
}

export const LossBadge = memo(function LossBadge({
  signature,
  size = 'md',
  showComponents = false
}: LossBadgeProps) {
  const hue = lossToHue(signature.total);
  const percentage = (signature.total * 100).toFixed(0);

  return (
    <div
      className={`loss-badge loss-badge--${size} loss-badge--${signature.status}`}
      style={{ '--loss-hue': hue } as React.CSSProperties}
      title={`Loss: ${percentage}% (${signature.status})`}
    >
      {signature.isAxiomatic && <span className="loss-badge__axiom">A</span>}
      <span className="loss-badge__value">{percentage}%</span>
      <span className="loss-badge__layer">L{signature.layer}</span>
    </div>
  );
});
```

**Effort**: 2 hours

---

### 3. Integrate Loss into ZeroSeedPage

**File**: `impl/claude/web/src/pages/ZeroSeedPage.tsx`

Add loss badge to axiom cards:

```tsx
// In AxiomExplorer rendering
<div className="axiom-card__header">
  <LossBadge signature={losses.get(node.id)} size="sm" />
  <span className="axiom-card__title">{node.title}</span>
</div>
```

**Effort**: 1 hour

---

### 4. Add Viridis CSS Variables

**File**: `impl/claude/web/src/components/zero-seed/ZeroSeed.css`

Add to existing file:

```css
/* Viridis loss palette */
:root {
  --viridis-0: #440154;
  --viridis-25: #31688e;
  --viridis-50: #35b779;
  --viridis-75: #90d743;
  --viridis-100: #fde725;

  --loss-stable: var(--viridis-0);
  --loss-transitional: var(--viridis-50);
  --loss-unstable: var(--viridis-100);
}

/* Loss-aware node styling */
.loss-aware {
  background: hsl(var(--loss-hue, 280), 40%, 15%);
  border-left: 3px solid hsl(var(--loss-hue, 280), 60%, 50%);
}

.loss-aware--unstable {
  animation: loss-pulse 1s ease-in-out infinite;
}

@keyframes loss-pulse {
  0%, 100% { box-shadow: 0 0 0 0 hsla(var(--loss-hue), 70%, 50%, 0.4); }
  50% { box-shadow: 0 0 12px 2px hsla(var(--loss-hue), 70%, 50%, 0.6); }
}
```

**Effort**: 30 minutes

---

## Near-Term Refactors (Next 2 Weeks)

### 5. Extract `useTelescopeState()` Hook

Extract navigation logic from HypergraphEditor into a reusable hook:

**File**: `impl/claude/web/src/hooks/useTelescopeState.ts`

Key state to extract:
- `focalDistance` (new: layer-based zoom)
- `focalPoint` (currently: `currentNode`)
- `visibleLayers` (derived from focal distance)
- `lossThreshold` (new: filter by loss)

**Effort**: 4 hours

---

### 6. Create `<TelescopeShell />` Wrapper

Wrap AppShell with telescope context:

**File**: `impl/claude/web/src/components/layout/TelescopeShell.tsx`

```tsx
export function TelescopeShell({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useTelescopeState();

  return (
    <TelescopeContext.Provider value={{ state, dispatch }}>
      <AppShell>
        <FocalDistanceIndicator value={state.focalDistance} />
        {children}
      </AppShell>
    </TelescopeContext.Provider>
  );
}
```

**Effort**: 3 hours

---

### 7. Add Gradient Navigation Commands

Add `gl` (go lowest-loss) and `gh` (go highest-loss) to HypergraphEditor:

**File**: `impl/claude/web/src/hypergraph/useKeyHandler.ts`

```typescript
case 'gl':
  // Navigate to lowest-loss neighbor
  const neighbors = await getNeighborLosses(state.currentNode);
  const lowest = neighbors.reduce((a, b) => a.loss < b.loss ? a : b);
  dispatch({ type: 'FOCUS_NODE', nodeId: lowest.id });
  break;

case 'gh':
  // Navigate to highest-loss neighbor (investigate)
  const neighbors = await getNeighborLosses(state.currentNode);
  const highest = neighbors.reduce((a, b) => a.loss > b.loss ? a : b);
  dispatch({ type: 'FOCUS_NODE', nodeId: highest.id });
  break;
```

**Effort**: 2 hours

---

## Medium-Term Refactors (Next Month)

### 8. Four-Panel Analysis View

Create `<AnalysisQuadrant />` component showing all four operad modes:

**Files**:
- `impl/claude/web/src/components/analysis/AnalysisQuadrant.tsx`
- `impl/claude/web/src/components/analysis/CategoricalPanel.tsx`
- `impl/claude/web/src/components/analysis/EpistemicPanel.tsx`
- `impl/claude/web/src/components/analysis/DialecticalPanel.tsx`
- `impl/claude/web/src/components/analysis/GenerativePanel.tsx`

Invoke via `<leader>a` in HypergraphEditor.

**Effort**: 8 hours

---

### 9. Witness Marks as Graph Edges

Refactor witness marks from side-effect POSTs to first-class graph operations:

**Backend**: Add edge types `DECIDES`, `WITNESSES`, `BECAUSE` to graph schema
**Frontend**: Render marks in derivation trail, enable `gm` navigation

**Effort**: 12 hours (significant backend work)

---

### 10. Unified Telescope Navigation

Replace page-based routing with telescope focal distance:

**Before**:
```tsx
<Route path="/zero-seed" element={<ZeroSeedPage />} />
```

**After**:
```tsx
<Route path="/axioms" element={<TelescopeFocus distance={1000} />} />
<Route path="/specs/*" element={<TelescopeFocus distance={10} />} />
```

URLs become bookmarks into telescope state, not page switches.

**Effort**: 16 hours (requires full navigation refactor)

---

## Validation Checklist

After each refactor, verify:

- [ ] **Typecheck passes**: `npm run typecheck`
- [ ] **Lint passes**: `npm run lint`
- [ ] **No regressions**: Manual test of affected flows
- [ ] **Mirror Test**: Does it feel daring, bold, creative?
- [ ] **Loss Test**: Does the component know its stability layer?

---

## Files to Touch (Priority Order)

1. `src/hooks/useLoss.ts` — New
2. `src/components/zero-seed/LossBadge.tsx` — New
3. `src/components/zero-seed/ZeroSeed.css` — Add viridis vars
4. `src/pages/ZeroSeedPage.tsx` — Integrate loss badges
5. `src/hypergraph/useKeyHandler.ts` — Add gl/gh commands
6. `src/hooks/useTelescopeState.ts` — Extract from HypergraphEditor
7. `src/components/layout/TelescopeShell.tsx` — New shell wrapper
8. `src/components/analysis/*` — Four-panel analysis (new)
9. `src/App.tsx` — Route → focal distance migration

---

*Filed: 2025-12-24 | Incremental Refactor Roadmap*
