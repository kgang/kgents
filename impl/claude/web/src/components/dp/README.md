# DP Visualization Components

Web UI components for visualizing Dynamic Programming value functions and policy traces from the DP-Agent bridge.

**Backend**: `impl/claude/services/categorical/dp_bridge.py`

## Components

### 1. ValueFunctionChart

Radar/spider chart showing the 7 core kgents principles:

```tsx
import { ValueFunctionChart } from '@/components/dp';

<ValueFunctionChart
  valueScore={myValueScore}
  width={400}
  height={400}
  showLabels
  showGrid
/>
```

**Props**:
- `valueScore: ValueScore | null` - Principle scores to visualize
- `width?: number` - Chart width (default 400)
- `height?: number` - Chart height (default 400)
- `showLabels?: boolean` - Show axis labels (default true)
- `showGrid?: boolean` - Show grid circles (default true)
- `compact?: boolean` - Compact mode (smaller)

**Visual encoding**:
- Area fill: overall satisfaction
- Color: health gradient (green → yellow → red)
- Dots: individual principle scores

### 2. PolicyTraceView

Timeline visualization of DP solution traces:

```tsx
import { PolicyTraceView } from '@/components/dp';

<PolicyTraceView
  trace={myPolicyTrace}
  showCumulative
  maxEntries={20}
/>
```

**Props**:
- `trace: PolicyTrace | null` - Policy trace to visualize
- `compact?: boolean` - Compact mode (hide state transitions)
- `maxEntries?: number` - Limit displayed entries
- `showCumulative?: boolean` - Show cumulative values (default true)

**Features**:
- Click entries to expand rationale
- Color-coded by value (health gradient)
- Timeline with connectors

### 3. ConstitutionScorecard

Detailed per-principle scorecard:

```tsx
import { ConstitutionScorecard } from '@/components/dp';

<ConstitutionScorecard
  valueScore={myValueScore}
  showWeights
  warningThreshold={0.5}
/>
```

**Props**:
- `valueScore: ValueScore | null` - Value score to visualize
- `compact?: boolean` - Compact mode (hide evidence)
- `showWeights?: boolean` - Show principle weights (default true)
- `warningThreshold?: number` - Threshold for warnings (default 0.5)

**Features**:
- Click rows to view evidence
- Warning indicators for low scores
- Overall score + minimum score
- Health status per principle

### 4. DPDashboard (Example)

Composite view combining all three:

```tsx
import { DPDashboard } from '@/components/dp/DPDashboard';

<DPDashboard
  valueScore={myValueScore}
  policyTrace={myPolicyTrace}
  layout="vertical"
/>
```

**Props**:
- `valueScore: ValueScore | null`
- `policyTrace: PolicyTrace | null`
- `layout?: 'horizontal' | 'vertical'` (default 'vertical')
- `showRadar?: boolean` (default true)
- `showScorecard?: boolean` (default true)
- `showTrace?: boolean` (default true)

## Types

All types mirror the backend `dp_bridge.py`:

```typescript
interface ValueScore {
  agent_name: string;
  principle_scores: PrincipleScore[];
  total_score: number;
  min_score: number;
  timestamp: string;
}

interface PrincipleScore {
  principle: Principle;
  score: number; // 0.0 to 1.0
  evidence: string;
  weight: number;
  weighted_score: number;
}

interface PolicyTrace {
  value: unknown;
  log: TraceEntry[];
  total_value?: number;
}

interface TraceEntry {
  state_before: unknown;
  action: string;
  state_after: unknown;
  value: number;
  rationale: string;
  timestamp: string;
}

enum Principle {
  TASTEFUL = 'TASTEFUL',
  CURATED = 'CURATED',
  ETHICAL = 'ETHICAL',
  JOY_INDUCING = 'JOY_INDUCING',
  COMPOSABLE = 'COMPOSABLE',
  HETERARCHICAL = 'HETERARCHICAL',
  GENERATIVE = 'GENERATIVE',
}
```

## Design Philosophy

**Stark, minimal. The structure reveals itself.**

- 90% steel (grays), 10% earned glow (health colors)
- No decoration, pure information
- Uses design tokens from `hypergraph/design-system.css`
- Responsive health gradients:
  - >= 80%: `--health-healthy` (green)
  - 60-80%: `--health-degraded` (yellow)
  - 40-60%: `--health-warning` (orange)
  - < 40%: `--health-critical` (red)

## Integration Example

Fetching data from backend:

```typescript
import { useEffect, useState } from 'react';
import { ValueFunctionChart, PolicyTraceView } from '@/components/dp';
import type { ValueScore, PolicyTrace } from '@/components/dp';

function MyComponent() {
  const [valueScore, setValueScore] = useState<ValueScore | null>(null);
  const [trace, setTrace] = useState<PolicyTrace | null>(null);

  useEffect(() => {
    // Fetch from backend API
    fetch('/api/dp/evaluate?agent=my_agent')
      .then(res => res.json())
      .then(data => {
        setValueScore(data.value_score);
        setTrace(data.policy_trace);
      });
  }, []);

  return (
    <div>
      <ValueFunctionChart valueScore={valueScore} />
      <PolicyTraceView trace={trace} />
    </div>
  );
}
```

## Testing

The components are type-safe and should pass TypeScript strict mode:

```bash
cd impl/claude/web
npm run typecheck
```

## Files

- `types.ts` - TypeScript types mirroring backend
- `ValueFunctionChart.tsx` - Radar chart component
- `ValueFunctionChart.css` - Radar chart styles
- `PolicyTraceView.tsx` - Timeline component
- `PolicyTraceView.css` - Timeline styles
- `ConstitutionScorecard.tsx` - Scorecard component
- `ConstitutionScorecard.css` - Scorecard styles
- `DPDashboard.tsx` - Example composite view
- `DPDashboard.css` - Dashboard styles
- `index.ts` - Public exports
- `README.md` - This file
