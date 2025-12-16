# Continuation: Layout Projection Functor

> *"Content projection is lossy compression. Layout projection is structural isomorphism."*

**Origin**: Elastic UI Audit session (2025-12-16)
**Status**: ✅ COMPLETED (2025-12-16)
**Target**: `spec/protocols/projection.md`

**Deliverable**: New "Layout Projection" section added to `spec/protocols/projection.md` (lines 213-424), covering:
- The Two Functors (Content vs Layout)
- Structural Isomorphism
- Layout Primitives (Split, Panel, Actions)
- Three-Stage Layout Pattern (Mobile/Tablet/Desktop)
- Physical Constraints (touch targets, minimum sizes)
- Density-Parameterized Constants
- Composition Laws (// preserves, >> transforms)
- Connection to AGENTESE (layout as observer capacity)
- Component Density Propagation
- Layout Hints interface

---

## Context

During an Elastic UI audit of the kgents web frontend, we discovered patterns that extend beyond the current Projection Protocol's "Density Projection" section. The existing spec covers **content-level** density (how much detail to show), but misses **layout-level** density (how to arrange components structurally).

### The Audit Findings

We refactored 4 pages (Brain, Town, Workshop, Inhabit) to match the Gestalt.tsx gold standard. Key pattern discovered:

**Mobile layouts are not "compressed desktop" — they are structurally different.**

```
Desktop: Sidebar | MainContent (resizable divider)
Mobile:  FullscreenContent + FloatingActions + BottomDrawer
```

This is not content degradation. This is a **layout functor** — a different mapping from widget tree to rendered structure.

---

## The Core Insight

The current spec says:
```
P[T] : State → Renderable[T]
```

But there are actually TWO functors:

```
Content[D] : State → ContentDetail[D]      (lossy compression)
Layout[D]  : WidgetTree → Structure[D]     (structural isomorphism)
```

Where `D ∈ {compact, comfortable, spacious}`.

**Content projection** removes information (fewer labels, smaller numbers).
**Layout projection** rearranges information (sidebar → drawer, buttons → floating actions).

The distinction matters because:
- Content projection is about **fidelity** (how much to show)
- Layout projection is about **affordance** (how to interact)

---

## Patterns to Formalize

### 1. The Three-Stage Layout Functor

```typescript
// Observed pattern across all refactored pages
if (isMobile) {
  return <MobileLayout>       // Canvas + FloatingActions + BottomDrawer
} else {
  return <ElasticSplit        // Two-pane with optional resize
    resizable={isDesktop}     // Only desktop gets drag handle
    collapseAt={768}          // Tablet collapses secondary
  />
}
```

This is a **case analysis** on density that yields **structurally different** output.

### 2. Density-Parameterized Constants

```typescript
// The canonical pattern for density-dependent values
const MAX_ITEMS = { compact: 5, comfortable: 8, spacious: 12 } as const;
const SHOW_LABELS = { compact: false, comfortable: true, spacious: true } as const;
const TOUCH_TARGET = { compact: 48, comfortable: 44, spacious: 36 } as const;

// Usage
const maxItems = MAX_ITEMS[density];
```

This is a **lookup table functor**: `Density → Value`.

### 3. Component Density Propagation

```typescript
// Anti-pattern: External conditionals
{isMobile ? <CompactPanel /> : <FullPanel />}

// Pattern: Internal adaptation
<Panel density={density} />  // Component decides what density means

// Inside Panel:
function Panel({ density }) {
  const isDrawer = density === 'compact';
  // Component owns its density interpretation
}
```

This is about **encapsulation** of the density functor within components.

### 4. Physical Constraints

Touch targets have a **minimum physical size** (48px) that doesn't scale with content. This is a constraint from the physical world that the projection must respect:

```
TouchTarget[compact] ≥ 48px   (physical constraint)
TouchTarget[spacious] ≥ 36px  (comfort minimum)
```

### 5. Panel-to-Drawer Transformation

```typescript
interface PanelProjection {
  desktop: 'sidebar';      // Visible, resizable
  tablet: 'collapsible';   // Visible, fixed width
  mobile: 'drawer';        // Hidden, slides up from bottom
}
```

The **same logical panel** projects to **different interaction modalities**.

---

## Questions to Explore

### Categorical Questions

1. **Is Layout[D] a functor?** Does it preserve composition?
   - If `A // B` (vertical composition) on desktop, what is `Layout[compact](A // B)`?
   - Is it `Layout[compact](A) // Layout[compact](B)` or something else?

2. **What is the relationship between Content[D] and Layout[D]?**
   - Are they independent (product)?
   - Does one determine the other (dependent)?
   - Is there a natural transformation between them?

3. **Is "drawer vs sidebar" an isomorphism or a lossy projection?**
   - Same information, different arrangement = isomorphism
   - But drawer requires explicit open action = different affordance
   - Is affordance change information loss?

### Practical Questions

4. **Where does the Layout functor live?**
   - In the widget definition? (widget knows its layout options)
   - In the projection target? (target decides layout)
   - In a separate layout layer? (new abstraction)

5. **How do ElasticSplit/BottomDrawer/FloatingActions map to the spec?**
   - Are these "layout primitives" that the protocol should name?
   - Or implementation details of the web target?

6. **Should the Projection Gallery demonstrate layout projection?**
   - Show same widget in sidebar vs drawer vs floating
   - Prove the structural isomorphism claim

### AGENTESE Questions

7. **Is layout projection a form of `manifest`?**
   - `manifest` yields observer-dependent view
   - Layout projection yields density-dependent structure
   - Same concept, different axis?

8. **Does the observer's umwelt include layout preference?**
   - Mobile user's umwelt: prefers drawers, floating actions
   - Desktop user's umwelt: prefers sidebars, drag handles
   - Or is this target-level, not observer-level?

---

## Files to Study

### Existing Spec
- `spec/protocols/projection.md` — Current projection protocol (especially lines 139-210)
- `spec/principles.md` — AD-008 Simplifying Isomorphisms

### Implementation Patterns
- `impl/claude/web/src/pages/Gestalt.tsx` — Gold standard (mobile layout ~lines 984-1080)
- `impl/claude/web/src/components/elastic/ElasticSplit.tsx` — Two-pane primitive
- `impl/claude/web/src/components/elastic/BottomDrawer.tsx` — Mobile drawer
- `impl/claude/web/src/components/elastic/FloatingActions.tsx` — Mobile actions
- `impl/claude/web/src/hooks/useWindowLayout.ts` — Density context provider

### Audit Artifacts
- `plans/web-refactor/elastic-audit-report.md` — Full audit findings
- `docs/skills/elastic-ui-patterns.md` — Practical patterns
- `docs/skills/ui-isomorphism-detection.md` — Meta-skill for finding isomorphisms

---

## Deliverable

Enhance `spec/protocols/projection.md` with a new section (after "Density Projection") that:

1. **Names the Layout Functor** — Formally distinguish content vs layout projection
2. **Defines Layout Primitives** — ElasticSplit, Drawer, FloatingActions as categorical objects
3. **States the Structural Isomorphism** — Same content, different arrangement, preserved affordances
4. **Documents the Three-Stage Pattern** — Mobile/Tablet/Desktop as canonical layout modes
5. **Addresses Physical Constraints** — Touch targets, minimum sizes
6. **Shows the Composition Law** — How layout projection interacts with widget composition (`//`, `>>`)
7. **Connects to AGENTESE** — Layout as observer-capacity, parallel to umwelt

### Optional Extensions

- Add layout projection to the Projection Gallery
- Define `LayoutHints` interface (like existing `WidgetLayoutHints` but for structure)
- Create a "Layout Primitives" section in the spec

---

## Style Notes

The projection protocol spec uses:
- Mathematical notation (`P[T] : State → Renderable[T]`)
- Commutative diagrams (ASCII)
- Tables for mappings
- "The Three Truths" pattern for key principles
- Quotes at section boundaries

Match this style. The spec is conceptual and implementation-agnostic — don't include React/TypeScript code directly, but reference implementation patterns abstractly.

---

*"The sidebar and the drawer are the same panel. Only the observer's capacity to receive differs."*
