# Constitutional Dashboard Components

Pure SVG visualization of constitutional alignment and trust, following the established brutalist design patterns.

## Components

### ConstitutionalDashboard

Main composite component that fetches and displays constitutional data.

```tsx
import { ConstitutionalDashboard } from '@/components/constitutional';

function MyPage() {
  return (
    <ConstitutionalDashboard
      agentId="claude"
      layout="vertical"
      showRadar={true}
      showScorecard={true}
      showTrust={true}
      subscribe={false}
    />
  );
}
```

**Props:**
- `agentId` (required): Agent ID to fetch data for
- `layout`: `'horizontal'` | `'vertical'` (default: `'vertical'`)
- `showRadar`: Show radar chart (default: `true`)
- `showScorecard`: Show scorecard table (default: `true`)
- `showTrust`: Show trust badge (default: `true`)
- `subscribe`: Subscribe to SSE updates (default: `false`)

### ConstitutionalRadar

7-principle radar chart (pure SVG, no dependencies).

```tsx
import { ConstitutionalRadar } from '@/components/constitutional';

<ConstitutionalRadar
  alignment={alignmentData}
  width={400}
  height={400}
  showLabels={true}
  showGrid={true}
/>
```

**Features:**
- Pure SVG implementation
- Color-coded scores (green >0.8, yellow 0.5-0.8, red <0.5)
- Tooltips on hover
- Responsive sizing

### ConstitutionalScorecard

Detailed table showing per-principle scores.

```tsx
import { ConstitutionalScorecard } from '@/components/constitutional';

<ConstitutionalScorecard
  alignment={alignmentData}
  trust={trustData}
  compact={false}
  warningThreshold={0.5}
/>
```

**Features:**
- Score bars with health colors
- Expandable rows
- Trust averages (when available)
- Dominant/weakest principle insights

### TrustLevelBadge

Trust level indicator (L0-L3).

```tsx
import { TrustLevelBadge } from '@/components/constitutional';

<TrustLevelBadge
  level="L2"
  reasoning="High alignment, low violations"
  size="md"
  showLabel={true}
/>
```

**Trust Levels:**
- **L0** (Gray): Read-Only, default
- **L1** (Blue): Bounded, earned trust
- **L2** (Green): Suggestion, high trust
- **L3** (Gold): Autonomous, maximum trust

### useConstitutional Hook

Data fetching hook for constitutional data.

```tsx
import { useConstitutional } from '@/components/constitutional';

function MyComponent() {
  const { data, alignment, trust, loading, error, refresh } = useConstitutional({
    agentId: 'claude',
    autoFetch: true,
    subscribe: false,
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>Trust Level: {trust?.trust_level}</div>;
}
```

## Data Types

### ConstitutionalAlignment

```typescript
interface ConstitutionalAlignment {
  principle_scores: Record<string, number>;  // 0.0 to 1.0
  weighted_total: number;
  galois_loss: number | null;
  tier: string;                               // EMPIRICAL, NOETHERIAN, GALOIS
  threshold: number;
  is_compliant: boolean;
  violation_count: number;
  dominant_principle: string;
  weakest_principle: string;
}
```

### ConstitutionalTrustResult

```typescript
interface ConstitutionalTrustResult {
  trust_level: 'L0' | 'L1' | 'L2' | 'L3';
  trust_level_value: number;
  total_marks_analyzed: number;
  average_alignment: number;
  violation_rate: number;
  trust_capital: number;
  principle_averages: Record<string, number>;
  dominant_principles: string[];
  reasoning: string;
}
```

## The 7 Principles

1. **TASTEFUL** - Clear, justified purpose
2. **CURATED** - Intentional selection
3. **ETHICAL** - Augments, never replaces
4. **JOY_INDUCING** - Delight in interaction
5. **COMPOSABLE** - Morphisms in a category
6. **HETERARCHICAL** - Flux, not hierarchy
7. **GENERATIVE** - Spec as compression

## API Endpoint

The dashboard fetches from:

```
GET /api/witness/constitutional/{agentId}
```

Returns:

```json
{
  "alignment": { /* ConstitutionalAlignment */ },
  "trust": { /* ConstitutionalTrustResult */ },
  "agent_id": "claude",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

## Design Philosophy

Following the established brutalist design patterns:

- **Pure SVG**: No chart libraries (recharts, d3), just SVG primitives
- **Steel colors**: `--steel-900` through `--steel-200`
- **Health colors**: `--health-healthy`, `--health-degraded`, `--health-warning`, `--health-critical`
- **Monospace fonts**: `var(--font-mono)` for all text
- **Minimal decoration**: Function over form
- **Keyboard navigation**: j/k for selection (where applicable)

## Integration Example

```tsx
import { ConstitutionalDashboard } from '@/components/constitutional';

export default function ConstitutionalPage() {
  return (
    <div className="page-container">
      <h1>Constitutional Alignment</h1>
      <ConstitutionalDashboard
        agentId="claude"
        subscribe={true}
      />
    </div>
  );
}
```

## Notes

- Components follow the same pattern as `components/dp/`
- Uses `useDirector`-style hook pattern for data fetching
- SSE subscription available for real-time updates
- All components are fully typed with TypeScript
- CSS is co-located with components (no global styles)
