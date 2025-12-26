# KBlockProjection Primitive

> "The projection is not a view. The projection IS the reality."

**Universal K-Block renderer with multi-surface projection.**

## Overview

KBlockProjection is the foundational primitive for rendering K-Blocks across different surfaces while maintaining:

- **Identity Law**: `KBlockProjection(K, Id, Id) ≅ K`
- **Constitutional Coherence**: Principles alignment visible across all projections
- **Galois Loss Awareness**: Layer drift indicators with navigation affordances
- **Contradiction Detection**: Visual badges for logical/temporal/constitutional conflicts
- **Witness Capability**: Mark creation on significant interactions

## Design Philosophy

**STARK BIOME** (90% steel, 10% earned glow):
- Humble steel frames (`--surface-*` backgrounds)
- Earned accent glow (`--accent-*` highlights)
- Consistent indicators across all projections
- Observer-dependent rendering (Umwelt principle)

## Projection Modes

| Mode | Surface | Use Case |
|------|---------|----------|
| `graph` | Hypergraph node | Force-directed spatial view, edge connections |
| `feed` | Feed item | Chronological stream, preview + metadata |
| `chat` | Message bubble | Conversation flow, own/other distinction |
| `portal` | Full detail | Expanded inspection, edges, lineage, proof |
| `genesis` | Cascade lineage | Zero Seed hierarchy, indented by depth |
| `card` | Compact summary | Dashboard tiles, sidebars, grids |
| `inline` | Minimal text | Embedding within text, just title/ID |
| `diff` | Side-by-side | VISUAL mode, content vs. baseContent |
| `proof` | Toulmin structure | Structured argument, claim → grounds → warrant |

## Usage

### Basic Example

```tsx
import { KBlockProjection } from '@/primitives/KBlockProjection';
import type { KBlock, ObserverContext } from '@/primitives/KBlockProjection';

function MyComponent({ kblock, observer }: { kblock: KBlock; observer: ObserverContext }) {
  return (
    <KBlockProjection
      kblock={kblock}
      observer={observer}
      projection="feed"
    />
  );
}
```

### With Callbacks

```tsx
<KBlockProjection
  kblock={kblock}
  observer={observer}
  projection="portal"
  onWitness={(mark) => {
    console.log('Witnessed:', mark);
    // Save mark to backend
  }}
  onNavigateLoss={(direction) => {
    console.log('Navigate Galois loss:', direction);
    // Navigate to lower/higher layer
  }}
/>
```

### With Constitutional Weights

```tsx
const weights: ConstitutionalWeights = {
  tasteful: 0.9,
  curated: 0.85,
  ethical: 1.0,
  joyInducing: 0.75,
  composable: 0.9,
  heterarchical: 0.8,
  generative: 0.85,
};

<KBlockProjection
  kblock={kblock}
  observer={observer}
  projection="card"
  constitutionalWeights={weights}
/>
```

### With Contradiction

```tsx
const contradiction: Contradiction = {
  id: 'contr_123',
  kblockIds: [kblock.id, 'other_id'],
  type: 'logical',
  severity: 'major',
  description: 'Claims A and B contradict',
  resolution: 'Resolve via dialectic',
};

<KBlockProjection
  kblock={kblock}
  observer={observer}
  projection="diff"
  contradiction={contradiction}
/>
```

## Shared Indicators

These indicators are rendered **for all projections**:

### 1. Galois Loss Indicator

- Appears when `loss > 0.2`
- Shows percentage drift (0-100%)
- Click to navigate up/down layers
- Color-coded by severity (green/yellow/red)

### 2. Contradiction Badge

- Shows contradiction type (logical/temporal/constitutional)
- Severity-based coloring (minor/major/critical)
- Tooltip with description

### 3. Constitutional Score

- Appears when average principle alignment < 0.6
- Shows percentage alignment
- Indicates need for review

### 4. Proof Badge

- Green checkmark when `kblock.hasProof === true`
- Links to proof projection

## Projection-Specific Features

### Graph Projection

- **Layer Badge**: Color-coded by Zero Seed layer (L1-L7) or "F" for file
- **Edge Count**: Total incoming + outgoing edges
- **Isolation State**: Visual indicator for DIRTY/STALE/CONFLICTING/ENTANGLED
- **Hover**: Subtle glow on card background

### Feed Projection

- **Timestamp**: Relative time (e.g., "3h ago", "2d ago")
- **Tags**: First 3 tags + count for overflow
- **Preview**: First 200 chars with "..." for longer content
- **Author**: Created by user/system

### Chat Projection

- **Own vs. Other**: Different background colors and alignment
- **Bubble Style**: Rounded corners, one corner sharp (like iMessage)
- **Timestamp**: Bottom-right, compact format

### Portal Projection

- **Full Metadata**: ID, isolation, confidence, created date
- **Content**: Full markdown rendering
- **Edges**: Incoming and outgoing, grouped and labeled
- **Lineage**: Parent K-Block IDs displayed
- **Tags**: All tags shown (not truncated)

### Genesis Projection

- **Depth Indentation**: `padding-left: depth * var(--space-xl)`
- **Depth Indicator**: Arrow chains ("→ → →") for visual hierarchy
- **Lineage Count**: Number of parents shown

### Card Projection

- **Layer Indicator**: Top border color-coded by layer
- **Preview**: First 100 chars, 3-line clamp
- **Footer**: Author + confidence percentage
- **Hover**: Lift effect with shadow

### Inline Projection

- **Minimal**: Just title or ID
- **Dotted Underline**: Indicates clickability
- **Hover**: Accent color change

### Diff Projection

- **Side-by-Side**: Base content (left) vs. current content (right)
- **Line-by-Line**: Unchanged/added/removed/changed indicators
- **Color-Coded**: Green (added), red (removed), yellow (changed)
- **Stats Header**: Count of additions/deletions/changes

### Proof Projection

- **Toulmin Structure**: Claim → Grounds → Warrant → Backing → Qualifiers → Rebuttals
- **Color-Coded Sections**: Claim (green), warrant (gold), backing (muted)
- **List Rendering**: Grounds and rebuttals as bulleted lists
- **No Proof Message**: Graceful fallback when proof is absent

## Type Reference

### KBlock

```typescript
interface KBlock {
  id: string;
  path: string;
  content: string;
  baseContent: string;
  contentHash: string;
  isolation: string; // PRISTINE | DIRTY | STALE | CONFLICTING | ENTANGLED
  zeroSeedLayer: number | null; // 1-7 or null
  zeroSeedKind: string | null; // "axiom", "value", "goal", etc.
  lineage: string[];
  hasProof: boolean;
  toulminProof: ToulminProof | null;
  confidence: number; // 0.0-1.0
  incomingEdges: KBlockEdge[];
  outgoingEdges: KBlockEdge[];
  tags: string[];
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
  notIngested: boolean;
  analysisRequired: boolean;
}
```

### ObserverContext

```typescript
interface ObserverContext {
  id: string;
  type: 'user' | 'agent' | 'system';
  principles: string[];
  capabilities: string[];
  density?: 'compact' | 'comfortable' | 'spacious';
  metadata?: Record<string, unknown>;
}
```

### ConstitutionalWeights

```typescript
interface ConstitutionalWeights {
  tasteful: number;
  curated: number;
  ethical: number;
  joyInducing: number;
  composable: number;
  heterarchical: number;
  generative: number;
}
```

## Helper Functions

### calculateGaloisLoss(kblock: KBlock): GaloisLoss

Calculates loss based on:
- Content drift (content vs. baseContent)
- Confidence penalty (1.0 - confidence)
- Isolation state (CONFLICTING/ENTANGLED = high penalty)

Returns `{ loss: number, sourceLayer?: number, direction?: 'lower' | 'higher' }`

### getDefaultConstitutionalWeights(kblock: KBlock): ConstitutionalWeights

Heuristic weights based on K-Block tags.
Returns 0.9 if tag includes principle keyword, else 0.5.

### getLossColor(loss: number): string

Returns color for loss severity:
- `< 0.2`: Green (HEALTHY)
- `0.2-0.5`: Yellow (WARNING)
- `0.5-0.8`: Red (CRITICAL)
- `> 0.8`: Dark Red (EMERGENCY)

## Design Tokens Used

### Colors
- `--surface-0`, `--surface-1`, `--surface-2`, `--surface-3`: Backgrounds
- `--text-primary`, `--text-secondary`, `--text-muted`: Text hierarchy
- `--accent-primary`, `--accent-primary-bright`: Main accents
- `--accent-success`, `--accent-error`: Status colors
- `--health-healthy`, `--health-degraded`, `--health-warning`, `--health-critical`: Loss colors

### Spacing
- `--space-xs`, `--space-sm`, `--space-md`, `--space-lg`, `--space-xl`: Gaps

### Border Radius
- `--radius-bare` (2px): Cards, containers
- `--radius-soft` (4px): Chat bubbles
- `--radius-pill` (9999px): Badges

### Typography
- `--font-sans`: Inter (UI text)
- `--font-mono`: JetBrains Mono (code, IDs, timestamps)
- `--font-size-xs` to `--font-size-xl`: Size scale
- `--font-weight-normal` to `--font-weight-bold`: Weight scale

### Z-Index
- `--z-sticky` (100): Indicators

### Transitions
- `--transition-fast` (120ms): Hover states
- `--transition-normal` (200ms): Expansions

## Testing

### Identity Law Verification

```tsx
// The projection should preserve the K-Block's essential identity
const kblock: KBlock = { /* ... */ };
const observer: ObserverContext = { id: 'id', type: 'user', ... };

// These should all represent the same K-Block
<KBlockProjection kblock={kblock} observer={observer} projection="graph" />
<KBlockProjection kblock={kblock} observer={observer} projection="feed" />
<KBlockProjection kblock={kblock} observer={observer} projection="portal" />

// Assert: kblock.id is visible in all projections
```

### Observer-Dependent Rendering

```tsx
const userObserver: ObserverContext = { id: 'user_123', type: 'user', ... };
const agentObserver: ObserverContext = { id: 'agent_456', type: 'agent', ... };

// Different observers may see different aspects
<KBlockProjection kblock={kblock} observer={userObserver} projection="chat" />
<KBlockProjection kblock={kblock} observer={agentObserver} projection="chat" />

// Assert: Chat bubbles aligned differently (own vs. other)
```

## Contributing

When adding new projection modes:

1. Create `projections/NewProjection.tsx` and `projections/NewProjection.css`
2. Implement `ProjectionComponentProps` interface
3. Add to `KBlockProjection.tsx` switch statement
4. Export from `index.ts`
5. Update this README with use case and features

## Related Primitives

- **Feed**: Chronological K-Block stream (uses FeedProjection internally)
- **Witness**: Evidence corpus display (complementary to proof projection)
- **Crystal**: Memory compression units (K-Blocks are crystallized into Crystals)
- **Graph**: Hypergraph editor (uses GraphProjection for node rendering)

---

**Spec References**:
- `spec/agents/d-gent.md`: K-Block storage and persistence
- `spec/protocols/zero-seed.md`: 7-layer hierarchy
- `docs/skills/metaphysical-fullstack.md`: Projection as functor
- `docs/skills/elastic-ui-patterns.md`: Responsive design patterns
