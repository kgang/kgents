# Witness Primitive

Evidence display with confidence tiers and causal graphs.

## Purpose

The Witness primitive consolidates evidence display components across the kgents UI:
- **ASHCEvidence.tsx** - ASHC compilation evidence
- **ConfidenceIndicator.tsx** - Per-response confidence
- **ContextIndicator.tsx** (evidence parts) - Session-level evidence

## Features

1. **Confidence Tiers**
   - Confident (green): P > 0.80
   - Uncertain (yellow): P 0.50-0.80
   - Speculative (red): P < 0.50

2. **Evidence Items**
   - Display evidence with source attribution
   - Show individual confidence scores
   - Clickable items for drill-down

3. **Causal Influence Graph**
   - Optional causal edges between evidence items
   - High-influence edges (>70%) have breathing animation
   - Shows influence percentages

4. **Display Modes**
   - **Compact**: Badge + count only
   - **Full**: Complete evidence list with optional causal graph
   - **Sizes**: sm, md (default), lg

## Usage

### Basic Example

```tsx
import { Witness } from '@/primitives/Witness';
import type { EvidenceCorpus } from '@/types/theory';

const evidence: EvidenceCorpus = {
  tier: "confident",
  items: [
    {
      id: "e1",
      content: "All 15 test cases passed with 100% success rate",
      confidence: 0.95,
      source: "ASHC",
    },
    {
      id: "e2",
      content: "Bayesian posterior mean: 0.94 (α=47, β=3)",
      confidence: 0.94,
      source: "Bayesian",
    },
  ],
  causalGraph: [
    { from: "e1", to: "e2", influence: 0.85 },
  ],
};

function MyComponent() {
  return (
    <Witness
      evidence={evidence}
      showCausal={true}
      onEvidenceClick={(id) => console.log('Clicked:', id)}
    />
  );
}
```

### Compact Mode

```tsx
<Witness
  evidence={evidence}
  compact={true}
  size="sm"
/>
// Renders: ● High Confidence (2)
```

### With Causal Graph

```tsx
<Witness
  evidence={evidence}
  showCausal={true}
  size="lg"
/>
```

## Integration with Existing Components

### From ASHCEvidence

```tsx
// Before
<ASHCEvidence data={ashcData} />

// After - convert to EvidenceCorpus
const evidence: EvidenceCorpus = {
  tier: ashcData.is_verified ? "confident" : "speculative",
  items: [
    {
      id: "ashc-eq",
      content: `Equivalence score: ${(ashcData.equivalence_score * 100).toFixed(0)}%`,
      confidence: ashcData.confidence,
      source: "ASHC",
    },
    {
      id: "ashc-runs",
      content: `${ashcData.runs_passed}/${ashcData.runs_completed} runs passed`,
      confidence: ashcData.pass_rate,
      source: "ASHC",
    },
  ],
  causalGraph: [],
};

<Witness evidence={evidence} />
```

### From ConfidenceIndicator

```tsx
// Before
<ConfidenceIndicator
  confidence={0.85}
  evidenceDelta={delta}
  showDetails={true}
/>

// After
const evidence: EvidenceCorpus = {
  tier: confidence > 0.8 ? "confident" : confidence > 0.5 ? "uncertain" : "speculative",
  items: [
    {
      id: "conf",
      content: `P(success) = ${confidence.toFixed(2)}`,
      confidence,
      source: "Bayesian",
    },
  ],
  causalGraph: [],
};

<Witness evidence={evidence} compact={true} />
```

### From ChatEvidence

```tsx
import type { ChatEvidence } from '@/components/chat/store';

function chatEvidenceToCorpus(evidence: ChatEvidence): EvidenceCorpus {
  const tier: EvidenceTier =
    evidence.confidence > 0.8 ? "confident" :
    evidence.confidence > 0.5 ? "uncertain" : "speculative";

  return {
    tier,
    items: [
      {
        id: "bayesian",
        content: `Bayesian posterior: α=${evidence.prior_alpha}, β=${evidence.prior_beta}`,
        confidence: evidence.confidence,
        source: "Bayesian",
      },
      {
        id: "tools",
        content: `Tools: ${evidence.tools_succeeded} succeeded, ${evidence.tools_failed} failed`,
        confidence: evidence.tools_succeeded / (evidence.tools_succeeded + evidence.tools_failed),
        source: "Tools",
      },
    ],
    causalGraph: [],
  };
}

<Witness evidence={chatEvidenceToCorpus(session.evidence)} />
```

## Styling

The Witness primitive uses the STARK biome design system:
- Steel background surfaces (`--surface-1`, `--surface-2`)
- Tier-specific border colors with subtle glow on hover
- Brutalist foundation: no decoration, just data
- Berkeley Mono / JetBrains Mono monospace font
- Breathing animation for high-influence causal edges

## Props

```typescript
interface WitnessProps {
  evidence: EvidenceCorpus;      // Required: evidence corpus
  showCausal?: boolean;           // Show causal graph (default: false)
  compact?: boolean;              // Compact mode (default: false)
  onEvidenceClick?: (id: string) => void;  // Click handler
  size?: 'sm' | 'md' | 'lg';     // Size variant (default: 'md')
}
```

## Design Philosophy

**"The proof IS the decision. The mark IS the witness."**

The Witness primitive makes evidence visible, traceable, and composable. It replaces scattered confidence indicators with a unified evidence display that:
- Shows confidence tiers at a glance
- Reveals causal structure when needed
- Degrades gracefully (compact → full → causal)
- Maintains brutalist clarity (no decoration, just data)

Total LOC: ~280 (component + styles)
