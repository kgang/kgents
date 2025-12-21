# Layout Sheaf: Global Coherence from Local Components

> *"The river that knows its course flows without thinking."*

## Overview

A Layout Sheaf provides **stable global layout** from **locally varying components**. When a component's internal state changes (hover, expand, animate), the global layout constraints remain satisfied.

**The Core Insight**: UI layout is a sheaf gluing problem. Local component states are sections over a topology of layout regions. The global layout is the glued section that satisfies all constraints.

---

## The Problem

Components with conditional content cause **layout reflow**:

```tsx
// Anti-pattern: Layout shifts on hover
{isHovered && <Description text={desc} />}
```

When `isHovered` toggles, the container height changes, causing:
- Buttons to jump
- Panels to resize
- User disorientation
- Failed "joy-inducing" principle

**Current Mitigations** (ad-hoc):
- Fixed heights (works but inflexible)
- Absolute positioning (works but disconnected from flow)
- CSS transitions (masks the problem, doesn't solve it)

---

## The Solution: Layout Sheaf

### Categorical Structure

```
LayoutSheaf : ComponentTopology → ConstraintSatisfaction

Where:
  ComponentTopology = DAG of layout regions (slots)
  ConstraintSatisfaction = All slots sum to stable dimensions
```

**The Three Layers**:

| Layer | Purpose | Example |
|-------|---------|---------|
| **Slots** | Named layout regions with constraints | `header-description: { minHeight: 16, maxHeight: 32 }` |
| **Claims** | Components claim space in slots | `ObserverSwitcher.claim('header-description', 16)` |
| **Gluing** | Resolve claims into stable layout | `totalHeight = sum(max(claims[slot]))` |

### The Sheaf Condition

For layout to be coherent:

```
∀ slot s, ∀ state changes σ:
  height(s, before(σ)) = height(s, after(σ))
```

**Translation**: Slot heights don't change when components re-render. Components may change content, but the slot height is pre-reserved.

---

## Specification

### 1. LayoutSlot

A named region in the layout with constraints:

```typescript
interface LayoutSlot {
  id: string;
  constraints: {
    minHeight?: number;
    maxHeight?: number;
    minWidth?: number;
    maxWidth?: number;
  };
  priority: number; // Higher = resolved first
}
```

### 2. LayoutClaim

A component's request for space in a slot:

```typescript
interface LayoutClaim {
  slotId: string;
  componentId: string;
  requestedHeight: number;
  requestedWidth?: number;
  isTransient: boolean; // true = hover/tooltip state
}
```

**Key Property**: Transient claims reserve space even when inactive. The space is claimed at mount, not at activation.

### 3. LayoutSheaf Context

The gluing context that manages global coherence:

```typescript
interface LayoutSheafContext {
  // Registration
  registerSlot(slot: LayoutSlot): void;
  unregisterSlot(slotId: string): void;

  // Claims
  claim(slotId: string, height: number, options?: ClaimOptions): ClaimHandle;
  release(handle: ClaimHandle): void;

  // Resolution
  getSlotHeight(slotId: string): number;
  getSlotStyle(slotId: string): CSSProperties;

  // Debugging
  getLayoutMap(): Map<string, ResolvedSlot>;
}

interface ClaimHandle {
  slotId: string;
  release: () => void;
  update: (newHeight: number) => void;
}

interface ClaimOptions {
  transient?: boolean;  // Reserve even when inactive
  animated?: boolean;   // Allow height transitions
  priority?: number;    // Higher wins ties
}
```

### 4. ReservedSlot Component

The render primitive for sheaf-aware layout:

```tsx
interface ReservedSlotProps {
  id: string;
  constraints?: LayoutSlot['constraints'];
  className?: string;
  children: React.ReactNode;
  fallback?: React.ReactNode; // Shown when no content
}

function ReservedSlot({ id, constraints, className, children, fallback }: ReservedSlotProps) {
  const { getSlotStyle } = useLayoutSheaf();
  const style = getSlotStyle(id);

  return (
    <div className={className} style={style}>
      {children ?? fallback}
    </div>
  );
}
```

---

## Gluing Algorithm

When multiple claims exist for a slot:

```python
def resolve_slot(slot: LayoutSlot, claims: list[LayoutClaim]) -> int:
    """
    Resolve claims into final slot height.

    Sheaf gluing: take the maximum claim (all must fit).
    Apply constraints to bound the result.
    """
    if not claims:
        return slot.constraints.get('minHeight', 0)

    # Maximum claim wins (all content must fit)
    max_claim = max(c.requestedHeight for c in claims)

    # Apply constraints
    if slot.constraints.get('maxHeight'):
        max_claim = min(max_claim, slot.constraints['maxHeight'])
    if slot.constraints.get('minHeight'):
        max_claim = max(max_claim, slot.constraints['minHeight'])

    return max_claim
```

**Why Maximum?** If component A claims 16px and component B claims 24px for the same slot, the slot must be 24px to fit both. This is the sheaf gluing condition: compatible local sections glue to a global section that contains all of them.

---

## Usage Patterns

### Pattern 1: Transient Content (Hover Descriptions)

```tsx
function ObserverSwitcher({ available, current, onChange }) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const descriptionRef = useLayoutClaim('observer-description', 16, { transient: true });

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <span>Observer</span>
        <ReservedSlot id="observer-description" className="text-xs text-gray-400">
          <FadeTransition show={!!hoveredId}>
            {hoveredId && available.find(o => o.id === hoveredId)?.description}
          </FadeTransition>
        </ReservedSlot>
      </div>
      {/* Pills */}
    </div>
  );
}
```

**Result**: Description slot always has 16px height. Content fades in/out without layout shift.

### Pattern 2: Expandable Sections

```tsx
function ExpandablePanel({ title, children }) {
  const [isExpanded, setExpanded] = useState(false);
  const contentHeight = isExpanded ? 200 : 0;

  // Claim full height at mount, animate to it
  useLayoutClaim('panel-content', contentHeight, { animated: true });

  return (
    <div>
      <button onClick={() => setExpanded(!isExpanded)}>{title}</button>
      <ReservedSlot
        id="panel-content"
        constraints={{ maxHeight: 200 }}
        className="overflow-hidden transition-all"
      >
        {isExpanded && children}
      </ReservedSlot>
    </div>
  );
}
```

### Pattern 3: Competing Claims (Multiple Components, Same Slot)

```tsx
// Component A
useLayoutClaim('shared-status', 20);

// Component B
useLayoutClaim('shared-status', 32);

// Result: slot height = 32 (maximum claim)
```

---

## Connection to Existing Architecture

### AD-008: Simplifying Isomorphisms

Layout stability IS a dimension like density:

```typescript
// Before: scattered conditionals
const height = isHovered ? 32 : 16;

// After: dimension-parameterized
const SLOT_HEIGHTS = {
  'header-description': 16,
  'panel-content': { min: 0, max: 200 },
};
```

### elastic-ui-patterns.md

Add `ReservedSlot` to the primitive taxonomy:

| Primitive | Use Case | Density Behavior |
|-----------|----------|------------------|
| `ReservedSlot` | Transient content | Fixed height per density |

### Sheaf Protocol (agents/sheaf/)

Extend to UI:

```typescript
// Backend: AgentSheaf<Context>
// Frontend: LayoutSheaf<SlotId>

// Same structure:
// - Local sections (component claims)
// - Gluing (resolve to stable layout)
// - Restriction (get slot style)
```

---

## Laws

### Law 1: Stability

```
∀ slot s, ∀ re-render r:
  getSlotHeight(s, before(r)) = getSlotHeight(s, after(r))
```

Height doesn't change on re-render (unless claim explicitly updated).

### Law 2: Containment

```
∀ claim c in slot s:
  c.requestedHeight ≤ getSlotHeight(s)
```

All claims fit within resolved height.

### Law 3: Monotonicity

```
claims(s) ⊆ claims'(s) → getSlotHeight(s) ≤ getSlotHeight'(s)
```

Adding claims can only increase height, never decrease.

### Law 4: Idempotence

```
claim(s, h); claim(s, h) ≡ claim(s, h)
```

Duplicate claims have no additional effect.

---

## Anti-Patterns

### Anti-Pattern 1: Conditional Render Without Reservation

```tsx
// BAD: Layout shifts
{isHovered && <Description />}

// GOOD: Reserved slot with transient claim
<ReservedSlot id="desc">
  {isHovered && <Description />}
</ReservedSlot>
```

### Anti-Pattern 2: Dynamic Height Without Animation

```tsx
// BAD: Jarring height change
const height = isExpanded ? 200 : 0;
<div style={{ height }} />

// GOOD: Animated transition
<ReservedSlot
  id="content"
  constraints={{ maxHeight: 200 }}
  className="transition-all duration-300"
/>
```

### Anti-Pattern 3: Unclaimed Dynamic Content

```tsx
// BAD: Height depends on content
<div>{dynamicList.map(item => <Item />)}</div>

// GOOD: Bounded with scroll
<ReservedSlot
  id="list"
  constraints={{ maxHeight: 400 }}
  className="overflow-y-auto"
/>
```

---

## Implementation Phases

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| **Phase 1** | `LayoutSheafContext` + `useLayoutClaim` | 2 |
| **Phase 2** | `ReservedSlot` component | 1 |
| **Phase 3** | Migrate `ObserverSwitcher` | 1 |
| **Phase 4** | Migrate elastic primitives | 2 |
| **Phase 5** | Animation support | 2 |

---

## Testing Strategy

### Unit Tests

```typescript
describe('LayoutSheaf', () => {
  it('resolves single claim to requested height', () => {
    const { claim, getSlotHeight } = createLayoutSheaf();
    claim('slot-a', 16);
    expect(getSlotHeight('slot-a')).toBe(16);
  });

  it('resolves multiple claims to maximum', () => {
    const { claim, getSlotHeight } = createLayoutSheaf();
    claim('slot-a', 16);
    claim('slot-a', 24);
    expect(getSlotHeight('slot-a')).toBe(24);
  });

  it('applies constraints', () => {
    const { registerSlot, claim, getSlotHeight } = createLayoutSheaf();
    registerSlot({ id: 'slot-a', constraints: { maxHeight: 20 } });
    claim('slot-a', 30);
    expect(getSlotHeight('slot-a')).toBe(20);
  });

  it('maintains height after release if other claims exist', () => {
    const { claim, getSlotHeight } = createLayoutSheaf();
    const handle1 = claim('slot-a', 16);
    claim('slot-a', 24);
    handle1.release();
    expect(getSlotHeight('slot-a')).toBe(24);
  });
});
```

### Integration Tests

```typescript
describe('ObserverSwitcher with LayoutSheaf', () => {
  it('does not change height on hover', async () => {
    render(
      <LayoutSheafProvider>
        <ObserverSwitcher available={observers} current="technical" onChange={vi.fn()} />
      </LayoutSheafProvider>
    );

    const initialHeight = screen.getByTestId('observer-header').offsetHeight;

    await userEvent.hover(screen.getByText('Security'));

    const hoverHeight = screen.getByTestId('observer-header').offsetHeight;
    expect(hoverHeight).toBe(initialHeight);
  });
});
```

---

## Relation to Principles

| Principle | How Layout Sheaf Embodies It |
|-----------|------------------------------|
| **Tasteful** | Stable layouts feel considered, not accidental |
| **Joy-Inducing** | No jarring jumps; smooth, predictable UI |
| **Composable** | Slots compose; claims are morphisms |
| **Generative** | Spec generates implementation; constraints derive behavior |
| **Heterarchical** | No fixed hierarchy; components negotiate via claims |

---

*"Local components, global stability. The sheaf glues them all."*
