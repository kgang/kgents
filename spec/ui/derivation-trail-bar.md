# Derivation Trail Bar: Constitutional Breadcrumb Navigation

> *"Where am I? Where did I come from? The trail reveals what the tree obscures."*

**Status:** Draft
**Implementation:** `impl/claude/web/src/components/derivation/DerivationTrailBar.tsx`
**Heritage:** Derivation Framework, K-Block, Hypergraph Editor, Galois Modularization

---

## Purpose

An ambient UI element showing the user's current position in Constitutional space. Always visible when a K-Block is selected, providing "Where am I?" awareness without demanding attention.

**Philosophy:** Constitutional grounding as UX, not CI. The system illuminates, not enforces.

---

## Core Insight

The trail bar is a **projection of the derivation DAG** onto a linear breadcrumb—the path from CONSTITUTION to the currently focused K-Block. Each hop carries Galois loss (the information lost by moving from abstract principle to concrete implementation). The trail makes this loss visible.

---

## Visual Specification

### Full Display (Wide Screens)

```
┌─ TRAIL ──────────────────────────────────────────────────────────┐
│ CONSTITUTION → COMPOSABLE → witness.md → mark.py → [YOU]         │
│                             L=0.08       L=0.15                  │
└──────────────────────────────────────────────────────────────────┘
```

### Collapsed Display (Narrow Screens)

```
┌─ TRAIL ──────────────────────────────────────────────────┐
│ CONSTITUTION ... [YOU]                       [⋯ 3 hops]  │
└──────────────────────────────────────────────────────────┘
```

---

## Type Signatures

```typescript
/** A single node in the derivation trail */
interface TrailNode {
  id: string;                    // Unique identifier
  label: string;                 // Display name
  type: TrailNodeType;           // constitution | principle | spec | impl
  path: string;                  // AGENTESE path or file path
  galoisLoss: number | null;     // L value from previous hop (null for root)
  confidence: number;            // Derivation confidence at this node
}

type TrailNodeType = 'constitution' | 'principle' | 'spec' | 'impl' | 'current';

/** Complete trail from Constitution to current K-Block */
interface DerivationTrail {
  nodes: TrailNode[];
  totalLoss: number;             // Cumulative Galois loss
  isComplete: boolean;           // true = grounded, false = orphan
  groundingStatus: GroundingStatus;
}

type GroundingStatus = 'grounded' | 'provisional' | 'orphan';

/** Trail bar component props */
interface DerivationTrailBarProps {
  trail: DerivationTrail | null;
  onNodeClick: (node: TrailNode) => void;
  onGroundingRequest?: () => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  className?: string;
}
```

---

## States

### Grounded

Full trail visible from CONSTITUTION to current K-Block. All derivation hops have valid paths.

```typescript
const GROUNDED_STYLE = {
  borderColor: 'var(--color-green-500)',
  backgroundColor: 'var(--color-green-50)',
  iconColor: 'var(--color-green-600)',
};
```

**Visual:** Green accent border, checkmark icon, full breadcrumb visible.

### Provisional

Trail visible but one or more hops have weak derivation (confidence < 0.5 or missing principle draw).

```typescript
const PROVISIONAL_STYLE = {
  borderColor: 'var(--color-amber-500)',
  backgroundColor: 'var(--color-amber-50)',
  iconColor: 'var(--color-amber-600)',
};
```

**Visual:** Amber warning icon, nodes with weak derivation shown with dashed underline.

### Orphan

K-Block has no derivation chain to Constitution. Trail shows "? → [YOU]".

```typescript
const ORPHAN_STYLE = {
  borderColor: 'var(--color-red-500)',
  backgroundColor: 'var(--color-red-50)',
  iconColor: 'var(--color-red-600)',
};
```

**Visual:** Red accent, "?" placeholder, "Click to ground" call-to-action.

---

## Interactions

| Interaction | Trigger | Result |
|-------------|---------|--------|
| Navigate to node | Click breadcrumb | Focus that K-Block in editor |
| View derivation details | Hover breadcrumb (300ms) | Tooltip with confidence, principles, loss |
| Ground orphan | Click "?" | Open grounding dialog |
| Toggle collapse | Click chevron | Expand/collapse to endpoints only |
| View full trail | Click "[N hops]" badge | Expand collapsed trail |

### Hover Preview Content

```typescript
interface TrailNodePreview {
  node: TrailNode;
  derivation: {
    tier: string;
    confidence: number;
    principleDraws: Array<{
      principle: string;
      strength: number;
    }>;
  };
  galoisLossBreakdown: {
    abstractionLoss: number;    // From moving down abstraction levels
    implementationGap: number;  // From spec → impl translation
    contextLoss: number;        // From removed context
  };
}
```

---

## Responsive Behavior

| Breakpoint | Behavior |
|------------|----------|
| ≥1024px (Spacious) | Full trail, all nodes visible, loss indicators shown |
| 768-1023px (Comfortable) | Full trail, loss indicators hidden, hover to reveal |
| <768px (Compact) | Collapsed to endpoints: "CONSTITUTION ... [YOU]" |

### Touch Targets

All interactive elements (breadcrumb nodes, collapse toggle) maintain 48px minimum touch target.

```typescript
const TOUCH_TARGET = {
  minHeight: '48px',
  minWidth: '44px',
  padding: '12px 16px',
};
```

---

## Integration

### Location

Lives in hypergraph editor header area, below the title bar, above the content pane.

```
┌─────────────────────────────────────────────────────────────────┐
│ [Mode] witness.md                                    [Actions]  │ ← Title bar
├─────────────────────────────────────────────────────────────────┤
│ CONSTITUTION → COMPOSABLE → witness.md → mark.py → [YOU]        │ ← Trail bar
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    [Editor Content]                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Sync with K-Block Selection

```typescript
// Hook for trail synchronization
function useDerivationTrail(
  selectedKBlock: KBlock | null,
  registry: DerivationRegistry,
): DerivationTrail | null {
  return useMemo(() => {
    if (!selectedKBlock) return null;
    return buildTrailFromKBlock(selectedKBlock, registry);
  }, [selectedKBlock, registry]);
}
```

### Constitutional Graph View Sync

When trail bar node is clicked, Constitutional Graph View (if open) should highlight the corresponding node.

```typescript
// Event emitted on node click
interface TrailNavigationEvent {
  type: 'trail.navigate';
  nodeId: string;
  nodePath: string;
}
```

---

## Laws

### L1: Trail Visibility

```
∀ selectedKBlock K:
  K ≠ null → trailBar.visible = true

Trail is always visible when a K-Block is selected.
```

### L2: Trail Accuracy

```
∀ trail T, derivationDAG D:
  T.nodes = shortestPath(D, 'CONSTITUTION', T.currentNode)

Trail accurately reflects the derivation path in the DAG.
```

### L3: Update Latency

```
∀ selectionChange S:
  trailBar.updateTime(S) < 100ms

Trail updates within 100ms of selection change.
```

### L4: Loss Consistency

```
∀ node N in trail T:
  N.galoisLoss = galoisLoss(N.parent, N)

Displayed loss values match computed Galois loss between adjacent nodes.
```

---

## React Component Interface

```typescript
import { FC, useState, useCallback } from 'react';

export const DerivationTrailBar: FC<DerivationTrailBarProps> = ({
  trail,
  onNodeClick,
  onGroundingRequest,
  collapsed = false,
  onToggleCollapse,
  className,
}) => {
  // Component implementation in impl/
};

// Supporting hooks
export function useDerivationTrail(
  kblock: KBlock | null,
  registry: DerivationRegistry,
): DerivationTrail | null;

export function useTrailNavigation(
  onNavigate: (path: string) => void,
): {
  handleNodeClick: (node: TrailNode) => void;
  handleGroundingRequest: () => void;
};
```

---

## Anti-Patterns

- **Hiding the trail** — Trail should remain visible even when space is tight; collapse, don't hide
- **Blocking on trail computation** — Use optimistic rendering with placeholder while computing
- **Ignoring orphan state** — Orphan K-Blocks must be clearly indicated, not silently rendered as normal
- **Loss without context** — Never show Galois loss numbers without hover explanation
- **Stale trail** — Trail must invalidate when derivation DAG changes

---

## Galois Loss Calculation

The loss at each hop is computed from the derivation framework:

```python
def galois_loss(parent: TrailNode, child: TrailNode) -> float:
    """
    Compute Galois loss between adjacent trail nodes.

    Loss sources:
    - Abstraction: Moving from principle to spec loses generality
    - Implementation: Moving from spec to impl loses flexibility
    - Context: Information not carried forward in derivation

    Returns: Loss in [0, 1] where 0 = perfect preservation
    """
    parent_conf = parent.confidence
    child_conf = child.confidence

    # Base loss from confidence degradation
    confidence_loss = max(0, parent_conf - child_conf)

    # Additional loss from tier transition
    tier_factor = TIER_LOSS_FACTORS.get(
        (parent.type, child.type),
        0.0
    )

    return min(1.0, confidence_loss + tier_factor)

TIER_LOSS_FACTORS = {
    ('constitution', 'principle'): 0.02,
    ('principle', 'spec'): 0.05,
    ('spec', 'impl'): 0.10,
}
```

---

## Connection to Principles

| Principle | How Trail Bar Embodies It |
|-----------|---------------------------|
| **Tasteful** | Minimal chrome, ambient presence, doesn't demand attention |
| **Curated** | Shows the essential path, not the full DAG |
| **Ethical** | Transparently shows derivation—no hidden authority claims |
| **Joy-Inducing** | Satisfying breadcrumb interaction, clear "where am I" |
| **Composable** | Trail = composition of derivation hops |
| **Heterarchical** | Multiple valid paths to same node shown on hover |
| **Generative** | Trail computable from K-Block + derivation DAG |

---

*"The trail is not the territory. But it's how you find your way home."*

---

**Filed:** 2026-01-10
**Lines:** ~200
