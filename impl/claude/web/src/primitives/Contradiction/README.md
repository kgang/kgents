# Contradiction Primitives

**"Contradictions aren't bugs—they're opportunities for synthesis."**

Three primitives for visualizing and resolving contradictions in kgents.

## Components

### ContradictionBadge

Lightning bolt indicator for contradictions.

```tsx
import { ContradictionBadge } from '@/primitives/Contradiction';

<ContradictionBadge
  hasContradiction={true}
  severity="medium"
  onClick={() => showResolutionPanel()}
  tooltip="Productive tension detected"
/>
```

**Props:**
- `hasContradiction`: Whether contradiction exists
- `severity`: `'low' | 'medium' | 'high'` (affects color)
- `onClick`: Optional click handler
- `tooltip`: Optional tooltip text
- `size`: `'sm' | 'md' | 'lg'`

**Visual encoding:**
- **Low** (steel-blue): Apparent contradiction
- **Medium** (life-sage): Productive tension
- **High** (glow-spore): Genuine contradiction

---

### ContradictionPolaroid

Side-by-side comparison of contradicting elements.

```tsx
import { ContradictionPolaroid } from '@/primitives/Contradiction';

<ContradictionPolaroid
  thesis={{
    content: "All agents should be stateless",
    source: "spec/principles.md"
  }}
  antithesis={{
    content: "Memory is essential for agent learning",
    source: "impl/services/brain/README.md"
  }}
  contradictionType="productive"
  onResolve={(strategy) => handleResolution(strategy)}
/>
```

**Props:**
- `thesis`: Object with `content` and optional `source`
- `antithesis`: Object with `content` and optional `source`
- `contradictionType`: `'genuine' | 'productive' | 'apparent'`
- `onResolve`: Called with selected `ResolutionStrategy`
- `showActions`: Whether to show resolution buttons (default: true)

---

### ResolutionPanel

Modal-like panel with 5 resolution strategies.

```tsx
import { ResolutionPanel } from '@/primitives/Contradiction';

<ResolutionPanel
  thesis="All agents should be stateless"
  antithesis="Memory is essential for agent learning"
  onSelectStrategy={(strategy) => {
    console.log('Selected:', strategy);
    // Handle resolution...
  }}
  suggestedStrategy="synthesis"
  onClose={() => setShowPanel(false)}
/>
```

**Props:**
- `thesis`: Thesis statement (string)
- `antithesis`: Antithesis statement (string)
- `onSelectStrategy`: Called with selected strategy
- `suggestedStrategy`: Optional strategy to highlight
- `onClose`: Optional close handler
- `loading`: Loading state (default: false)

---

## Resolution Strategies

Five strategies for resolving contradictions:

| Strategy | Icon | Description | Example |
|----------|------|-------------|---------|
| **Synthesis** | ⊕ | Create a third thing, better than either | Thesis + Antithesis → Novel insight |
| **Scope** | ⊂ | Narrow the scope of one or both claims | "X is always true" → "X is true in domain D" |
| **Temporal** | ⏱ | Both true, but at different times | "X was true then, Y is true now" |
| **Context** | ⊞ | Both true, but in different contexts | "X for context A, Y for context B" |
| **Supersede** | → | One claim supersedes the other | "New evidence shows Y supersedes X" |

---

## Complete Example

```tsx
import { useState } from 'react';
import {
  ContradictionBadge,
  ContradictionPolaroid,
  ResolutionPanel,
  type ResolutionStrategy,
} from '@/primitives/Contradiction';

function ContradictionDemo() {
  const [showPanel, setShowPanel] = useState(false);

  const handleResolve = (strategy: ResolutionStrategy) => {
    console.log('Resolving with strategy:', strategy);
    // Send to backend, update state, etc.
    setShowPanel(false);
  };

  return (
    <div>
      {/* Badge in content */}
      <div>
        Some text with a contradiction
        <ContradictionBadge
          hasContradiction={true}
          severity="medium"
          onClick={() => setShowPanel(true)}
        />
      </div>

      {/* Polaroid view */}
      <ContradictionPolaroid
        thesis={{
          content: "Agents should be pure functions",
          source: "spec/principles.md"
        }}
        antithesis={{
          content: "State machines are necessary for complex behavior",
          source: "impl/agents/polynomial.py"
        }}
        contradictionType="productive"
        onResolve={(strategy) => {
          console.log('Quick resolve:', strategy);
        }}
      />

      {/* Resolution panel (modal) */}
      {showPanel && (
        <ResolutionPanel
          thesis="Agents should be pure functions"
          antithesis="State machines are necessary for complex behavior"
          onSelectStrategy={handleResolve}
          suggestedStrategy="synthesis"
          onClose={() => setShowPanel(false)}
        />
      )}
    </div>
  );
}
```

---

## Philosophy

**Contradictions are features, not bugs:**
- Apparent contradictions → Clarification opportunities
- Productive tensions → Creative synthesis
- Genuine contradictions → System evolution

**Design principles:**
- Make tension **visible** (lightning bolt, side-by-side)
- Make synthesis **inviting** (clear strategies, guided flow)
- Preserve **productive tension** (don't force premature resolution)

**STARK BIOME aesthetic:**
- Frames stay humble (steel palette)
- Contradictions glow (earned color on severity)
- Clear affordances (button states, hover effects)

---

## Integration with Backend

These primitives expect contradiction data from the backend API:

```typescript
// Expected from: GET /api/contradiction/detect
interface Contradiction {
  id: string;
  thesis: { content: string; source?: string };
  antithesis: { content: string; source?: string };
  type: 'genuine' | 'productive' | 'apparent';
  severity: 'low' | 'medium' | 'high';
  resolved: boolean;
  resolution?: {
    strategy: ResolutionStrategy;
    synthesis?: string;
  };
}
```

See `impl/claude/protocols/api/contradiction.py` for backend implementation.

---

*Created: 2025-12-25 | Part of the Contradiction Detection system*
