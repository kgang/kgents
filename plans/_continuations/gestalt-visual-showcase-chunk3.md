# Gestalt Visual Showcase: Chunk 3 Continuation

**Plan**: `plans/gestalt-visual-showcase.md`
**Previous**: Chunk 2 (Legend & Tooltips) - COMPLETE
**Current**: Chunk 3 (Edge Styling & Data Flow Animation)
**Date**: 2025-12-16

---

## Goal

Make dependencies visually informative and alive. Transform static gray lines into semantic, animated data flows.

---

## Files to Create/Modify

```
impl/claude/web/src/components/gestalt/
├── AnimatedEdge.tsx       # New: edge with particle animation
├── EdgeStyles.ts          # New: edge styling configuration
└── index.ts               # Update: export new components

impl/claude/web/src/pages/Gestalt.tsx
└── Update DependencyEdgeComponent to use new styles
```

---

## Edge Styling Spec

```typescript
export interface EdgeStyle {
  color: string;
  dash: boolean;
  width: number;
  opacity: number;
  animated?: boolean;
}

export const EDGE_STYLES: Record<string, EdgeStyle> = {
  // Current types
  import: { color: '#6b7280', dash: false, width: 1, opacity: 0.25 },
  violation: { color: '#ef4444', dash: false, width: 2.5, opacity: 0.9 },

  // Future infrastructure types (prep for Phase 5)
  reads: { color: '#3b82f6', dash: false, width: 2, opacity: 0.6 },
  writes: { color: '#ef4444', dash: false, width: 2, opacity: 0.6 },
  calls: { color: '#f97316', dash: true, width: 1.5, opacity: 0.5 },
  publishes: { color: '#8b5cf6', dash: false, width: 1.5, opacity: 0.5, animated: true },
  subscribes: { color: '#8b5cf6', dash: true, width: 1.5, opacity: 0.5 },
};
```

---

## Animation Pattern

```
Static edge:     ─────────────────────────────
Animated edge:   ─●───────●───────●───────●───  (particles flowing)
Violation edge:  ══════════════════════════════  (thicker, red, gentle pulse)
Selected edge:   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  (brighter glow)
```

**Technical approach**:
- Use Three.js `Line` with custom shader for animation
- Particles: small spheres moving along edge path via `useFrame`
- Violation pulse: animate opacity 0.7-1.0 with sine wave
- Selection glow: increase emissive intensity on selected node's edges

---

## Exit Criteria

- [x] Edge styles differentiate import vs violation (color, width)
- [x] Flow animation on selected node's edges (particles moving)
- [x] Violation edges have attention-drawing pulse
- [x] Animation performs well (SmartEdge only animates active edges)
- [x] Animation can be toggled off (showAnimation in FilterState)
- [x] Edge styling extensible for infrastructure types (9 types defined)
- [x] 33 tests (styling config, animation toggle, pulse functions)

## Completion Notes (2025-12-16)

**Files Created:**
- `EdgeStyles.ts` - Semantic edge configuration with 9 edge types
- `AnimatedEdge.tsx` - SmartEdge, AnimatedEdge, StaticEdge components

**Key Design Decisions:**
1. **Performance**: SmartEdge auto-selects between AnimatedEdge and StaticEdge based on context
2. **Selection-driven animation**: Only edges connected to selected node get particles
3. **Dimming non-active**: When a node is selected, unconnected edges dim for focus
4. **Violation glow**: Uses wider line with pulse opacity for attention

**Test Count:** 90 total Gestalt tests (33 new edge-styling tests)

---

## Key Considerations

1. **Performance**: With 500+ edges, use instanced geometry or shader-based animation
2. **Subtlety**: Animation should enhance, not distract. Slow, gentle movement.
3. **Selection context**: Only animate edges connected to selected node
4. **Toggle**: Add `showAnimation: boolean` to FilterState

---

## Reference

- Current edge rendering: `Gestalt.tsx` → `DependencyEdgeComponent`
- drei Line component: `@react-three/drei` Line
- Animation pattern: `useFrame` hook from `@react-three/fiber`
- Existing tests: `tests/unit/gestalt/` (57 passing)

---

*"A living architecture breathes through its connections."*
