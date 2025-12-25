# Witness Primitive - Quick Reference

## TL;DR

```tsx
import { Witness } from '@/primitives/Witness';

const evidence = {
  tier: "confident",  // confident | uncertain | speculative
  items: [
    { id: "e1", content: "Text", confidence: 0.9, source: "ASHC" }
  ],
  causalGraph: [
    { from: "e1", to: "e2", influence: 0.85 }
  ]
};

<Witness evidence={evidence} showCausal={true} />
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `evidence` | `EvidenceCorpus` | required | Evidence data |
| `showCausal` | `boolean` | `false` | Show causal graph |
| `compact` | `boolean` | `false` | Inline badge mode |
| `onEvidenceClick` | `(id: string) => void` | - | Click handler |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Size variant |

## Confidence Tiers

| Tier | Range | Color | Icon |
|------|-------|-------|------|
| `confident` | > 0.80 | Green | ● |
| `uncertain` | 0.50-0.80 | Yellow | ◐ |
| `speculative` | < 0.50 | Red | ◯ |

## Common Patterns

### Inline Badge
```tsx
<p>
  This has <Witness evidence={e} compact={true} size="sm" /> confidence
</p>
```

### With Causal Graph
```tsx
<Witness evidence={e} showCausal={true} />
```

### Clickable Items
```tsx
<Witness
  evidence={e}
  onEvidenceClick={(id) => console.log('Clicked:', id)}
/>
```

## Type Reference

```typescript
type EvidenceTier = "confident" | "uncertain" | "speculative";

interface Evidence {
  id: string;
  content: string;
  confidence: number;  // 0-1
  source: string;
}

interface CausalEdge {
  from: string;  // evidence.id
  to: string;    // evidence.id
  influence: number;  // 0-1
}

interface EvidenceCorpus {
  tier: EvidenceTier;
  items: Evidence[];
  causalGraph: CausalEdge[];
}
```

## Styling

Uses STARK biome variables:
- `--surface-1`, `--surface-2` - Backgrounds
- `--border` - Base borders
- `--text-1`, `--text-2` - Text colors
- `--accent` - Highlights
- `--success-border`, `--warning-border`, `--error-border` - Tier colors

## Files

```
/primitives/Witness/
  Witness.tsx         Component
  Witness.css         Styles
  WitnessExample.tsx  Demos
  README.md           Full docs
  QUICK_REF.md        This file
  index.ts            Exports
```
