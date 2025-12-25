# Analysis Components

Four-panel visualization for the Analysis Operad.

> *"Analysis is not one thing but four: verification of laws, grounding of claims, resolution of tensions, and regeneration from axioms."*

## Overview

The `AnalysisQuadrant` component displays all four analysis modes simultaneously in a 2x2 grid:

```
┌─────────────────┬─────────────────┐
│  CATEGORICAL    │  EPISTEMIC      │
│  Laws Hold? ✓   │  Grounded? ✓    │
├─────────────────┼─────────────────┤
│  DIALECTICAL    │  GENERATIVE     │
│  Tensions: 2    │  Regenerable? ✓ │
└─────────────────┴─────────────────┘
```

## Usage

### Basic Usage

```tsx
import { AnalysisQuadrant } from '@/components/analysis';

function SpecView({ nodeId }: { nodeId: string }) {
  return <AnalysisQuadrant nodeId={nodeId} />;
}
```

### With Close Handler

```tsx
<AnalysisQuadrant
  nodeId="spec/protocols/witness.md"
  onClose={() => setShowAnalysis(false)}
/>
```

### Individual Panels

You can also use individual panels:

```tsx
import { CategoricalPanel, useAnalysis } from '@/components/analysis';

function MyComponent({ nodeId }: { nodeId: string }) {
  const { categorical, loading } = useAnalysis(nodeId);

  return <CategoricalPanel report={categorical} loading={loading} />;
}
```

## The Four Modes

### 1. Categorical (Laws)

**Question**: Does the spec satisfy its own composition laws?

**What it shows**:
- Law verifications (PASSED, STRUCTURAL, FAILED, UNDECIDABLE)
- Fixed-point indicator for self-referential specs
- Overall pass/fail status

**Icon**: ⊚
**Color**: Teal (`--viridis-30`)

### 2. Epistemic (Grounding)

**Question**: What layer IS this spec? How is it justified?

**What it shows**:
- Layer classification (L1-L7)
- Evidence tier (Somatic, Aesthetic, Empirical, Categorical, Derived)
- Grounding chain (derivation path to axioms)
- Termination status (anchored vs floating)

**Icon**: ◉
**Color**: Green (`--viridis-50`)

### 3. Dialectical (Tensions)

**Question**: What tensions exist? How are they resolved?

**What it shows**:
- Tension count and breakdown
- Tension types:
  - **Apparent** (≈): Seems contradictory but different scopes
  - **Productive** (⇌): Real tension driving design
  - **Problematic** (⚠): Unresolved contradiction
  - **Paraconsistent** (∥): Deliberately tolerated
- Synthesis status

**Icon**: ⇌
**Color**: Lime (`--viridis-60`)

### 4. Generative (Regeneration)

**Question**: Can the spec be regenerated from its axioms?

**What it shows**:
- Regenerability status (Yes/No)
- Compression ratio with quality indicator
  - Excellent: < 0.3
  - Good: 0.3 - 0.7
  - Poor: > 0.7
- Minimal kernel (axiom set)

**Icon**: ⚛
**Color**: Cyan (`--viridis-40`)

## Data Hook

### `useAnalysis(nodeId)`

Fetches analysis data for all four modes.

```tsx
const {
  categorical,   // CategoricalReport | null
  epistemic,     // EpistemicReport | null
  dialectical,   // DialecticalReport | null
  generative,    // GenerativeReport | null
  loading,       // boolean
  error,         // Error | null
  refresh,       // () => void
} = useAnalysis(nodeId);
```

**Data Source**: Fetches from `/api/zero-seed/nodes/{nodeId}/analysis` endpoint. The backend currently returns meaningful mock data; full AnalysisService integration is in progress.

## Styling

### Design Tokens

All panels use the viridis palette:

```css
--viridis-0: #440154;    /* Deep purple (axiomatic) */
--viridis-30: #31688e;   /* Teal (stable) */
--viridis-50: #1f9e89;   /* Green (transitional) */
--viridis-60: #35b779;   /* Lime */
--viridis-70: #6ece58;   /* Yellow (warning) */
--viridis-100: #fde725;  /* Bright yellow (critical) */
```

### Responsive Behavior

- **Desktop**: 2x2 grid
- **Mobile** (< 768px): Stacked vertically

## Backend Integration

### API Endpoint

```
GET /api/zero-seed/nodes/{nodeId}/analysis
```

**Response**:
```json
{
  "nodeId": "zn-axiom-001",
  "categorical": {
    "status": "pass",
    "summary": "All composition laws hold...",
    "items": [
      { "label": "Identity Law", "value": "Id >> f = f", "status": "pass" },
      ...
    ]
  },
  "epistemic": { ... },
  "dialectical": { ... },
  "generative": { ... }
}
```

The hook transforms this simplified backend format into the richer report types expected by the UI panels.

See type definitions in `useAnalysis.ts` and `api/zeroSeed.ts` for complete schema.

## Related

- **Spec**: `spec/theory/analysis-operad.md`
- **Skill**: `docs/skills/analysis-operad.md`
- **Backend**: `services/analysis/`
- **Operad**: `agents/operad/domains/analysis.py`

---

*The proof IS the decision. The mark IS the witness.*
