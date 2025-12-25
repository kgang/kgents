# Loss Gradient Visualization

> *"Navigate toward stability. The gradient IS the guide."*

**Created**: 2025-12-24
**Status**: Scoped, Ready for Implementation
**Effort**: Option A: 2-4h, Option B: 6-10h

---

## Vision

Visualize gradient vectors pointing toward lower-loss neighbors in the Zero Seed hypergraph. Users can "follow the gradient to stability" - navigating from high-loss (yellow, unstable) nodes toward low-loss (purple, stable) axioms.

---

## Current State: Surprisingly Advanced

The infrastructure already exists:

### Backend (Ready)
- `GradientVector` defined in `protocols/api/zero_seed.py`
  - Fields: `x`, `y`, `magnitude`, `target_node`
- `TelescopeResponse.gradients: dict[str, GradientVector]`
- `/api/zero-seed/telescope` returns gradient data

### Frontend (Ready)
- `GradientField.tsx` - SVG gradient arrow renderer (exists!)
- `useLoss.ts` - Loss fetching with `lossToColor()`, `lossToHue()`
- `LossBadge.tsx`, `LossNode.tsx`, `LossLegend.tsx` - complete vocabulary
- PixiJS in dependencies (`pixi.js@7.4.2`, `@pixi/react@7.1.2`)
- `d3-force` for graph layout

---

## Options

### Option A: SVG Overlay (Recommended for MVP)

**Effort**: 2-4 hours
**Risk**: Low

**What exists**: `GradientField.tsx` is production-ready SVG component.

**What to do**:
1. Wire `GradientField.tsx` into `GaloisTelescope.tsx`
2. Transform API `GradientVector[x, y]` to SVG coordinates
3. Add render path in main telescope SVG

**Pros**:
- Zero new dependencies
- Familiar DOM debugging/CSS styling
- Works with existing SVG infrastructure

**Cons**:
- May struggle with 100+ vectors (SVG repaint)
- No animation smoothing

### Option B: Canvas Layer Over SVG

**Effort**: 6-10 hours
**Risk**: Medium

**What exists**: `AstronomicalChart.tsx` proves PixiJS pattern.

**What to do**:
1. Copy canvas pattern from `AstronomicalChart.tsx`
2. Create `GradientFieldPixi.tsx` rendering to PIXI.Graphics
3. Position above SVG layer (z-index)
4. Reuse `StarRenderer.ts` utilities

**Pros**:
- Smooth 60fps with 1000+ vectors
- GPU-accelerated (WebGL)
- Can animate with PIXI tweens

**Cons**:
- More complex coordinate mapping
- Canvas write-only (no devtools inspection)

### Option C: Full PixiJS (Deferred)

**Effort**: 2-3 weeks
**Risk**: High

Merge entire Zero Seed graph into unified PixiJS viewport. Not recommended until Options A/B validated.

---

## Implementation: Option A

### Step 1: Locate Components (15 min)
```
web/src/components/zero-seed/GradientField.tsx   # Exists, ready
web/src/components/zero-seed/GaloisTelescope.tsx # Container
web/src/hooks/useLoss.ts                         # Loss colors
```

### Step 2: Wire GradientField into Telescope (1h)

**File**: `web/src/components/zero-seed/GaloisTelescope.tsx`

```typescript
import { GradientField } from './GradientField';

// In render:
<svg viewBox={viewBox}>
  {/* Existing nodes */}
  <NodesLayer nodes={nodes} />

  {/* Add gradient field */}
  <GradientField
    gradients={telescopeData.gradients}
    nodePositions={nodePositions}
    scale={scale}
  />
</svg>
```

### Step 3: Coordinate Transform (1h)

**File**: `web/src/components/zero-seed/GradientField.tsx`

Ensure gradient vectors transform correctly:
```typescript
function transformGradient(
  gradient: GradientVector,
  nodePos: { x: number; y: number },
  scale: number
): { x1: number; y1: number; x2: number; y2: number } {
  return {
    x1: nodePos.x,
    y1: nodePos.y,
    x2: nodePos.x + gradient.x * scale,
    y2: nodePos.y + gradient.y * scale,
  };
}
```

### Step 4: Style Arrows (30 min)

**File**: `web/src/components/zero-seed/GradientField.css`

```css
.gradient-arrow {
  stroke: var(--viridis-teal);
  stroke-width: 2;
  fill: none;
  opacity: 0.7;
}

.gradient-arrow:hover {
  opacity: 1;
  stroke-width: 3;
}

.gradient-arrowhead {
  fill: var(--viridis-teal);
}
```

### Step 5: Test (30 min)

1. Start API: `uv run uvicorn protocols.api.app:create_app --factory --reload`
2. Start frontend: `cd web && npm run dev`
3. Navigate to Zero Seed page
4. Verify gradient arrows appear
5. Check that arrows point toward lower-loss nodes

---

## Files to Modify

| File | Change |
|------|--------|
| `web/src/components/zero-seed/GaloisTelescope.tsx` | Add `GradientField` component |
| `web/src/components/zero-seed/GradientField.tsx` | Coordinate transform (if needed) |
| `web/src/components/zero-seed/GradientField.css` | Arrow styling |

---

## Success Criteria

- [ ] Gradient arrows render in telescope view
- [ ] Arrows point from high-loss to low-loss nodes
- [ ] Arrows scale correctly with zoom
- [ ] TypeScript + lint pass
- [ ] Kent says "this feels right"

---

## Future Enhancements

If Option A validated:
- Add animation (arrows pulse/flow)
- Add toggle in UI to show/hide gradients
- Upgrade to Option B for performance if needed

---

*"The gradient IS the guide. The loss IS the landscape."*
