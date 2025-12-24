# DP Components Integration Guide

Quick guide to integrate DP visualization components into your kgents application.

## 1. Import Components

```typescript
import {
  ValueFunctionChart,
  PolicyTraceView,
  ConstitutionScorecard,
  type ValueScore,
  type PolicyTrace,
} from '@/components/dp';
```

## 2. Backend API Endpoint

Add to your FastAPI router:

```python
# impl/claude/protocols/api/router.py (or similar)

from services.categorical.dp_bridge import (
    ValueFunction,
    DPSolver,
    Principle,
)

@router.get("/dp/evaluate/{agent_name}")
async def evaluate_agent(agent_name: str) -> dict:
    """Evaluate agent composition using DP value function."""

    # Create value function with principle evaluators
    vf = ValueFunction(
        principle_evaluators={
            Principle.TASTEFUL: lambda a, s, act: evaluate_tasteful(a, s, act),
            Principle.ETHICAL: lambda a, s, act: evaluate_ethical(a, s, act),
            # ... other principles
        },
        evidence_generators={
            Principle.TASTEFUL: lambda a, s, act: generate_evidence(a, s, act),
            # ... other principles
        }
    )

    # Evaluate
    score = vf.evaluate(agent_name, state="current", action=None)

    # Optionally: solve DP problem for policy trace
    # solver = DPSolver(formulation=..., value_function=vf)
    # value, trace = solver.solve()

    return {
        "value_score": score.to_dict(),
        # "policy_trace": trace.to_marks() if trace else None
    }
```

## 3. Frontend Data Fetching

Create a custom hook:

```typescript
// hooks/useDPEvaluation.ts

import { useEffect, useState } from 'react';
import type { ValueScore, PolicyTrace } from '@/components/dp';

export function useDPEvaluation(agentName: string) {
  const [valueScore, setValueScore] = useState<ValueScore | null>(null);
  const [policyTrace, setPolicyTrace] = useState<PolicyTrace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchEvaluation() {
      try {
        setLoading(true);
        const response = await fetch(`/api/dp/evaluate/${agentName}`);
        if (!response.ok) throw new Error('Failed to fetch evaluation');

        const data = await response.json();
        setValueScore(data.value_score);
        setPolicyTrace(data.policy_trace || null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setLoading(false);
      }
    }

    if (agentName) {
      fetchEvaluation();
    }
  }, [agentName]);

  return { valueScore, policyTrace, loading, error };
}
```

## 4. Use in a Page

```typescript
// pages/DPAnalysisPage.tsx

import { useDPEvaluation } from '@/hooks/useDPEvaluation';
import {
  ValueFunctionChart,
  PolicyTraceView,
  ConstitutionScorecard,
} from '@/components/dp';

export function DPAnalysisPage() {
  const agentName = 'Compose(Brain, Town)'; // Could come from URL params
  const { valueScore, policyTrace, loading, error } = useDPEvaluation(agentName);

  if (loading) return <div>Loading DP evaluation...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="dp-analysis-page">
      <h1>DP Analysis: {agentName}</h1>

      <section className="dp-analysis-page__overview">
        <ValueFunctionChart valueScore={valueScore} />
        <ConstitutionScorecard valueScore={valueScore} />
      </section>

      {policyTrace && (
        <section className="dp-analysis-page__trace">
          <PolicyTraceView trace={policyTrace} />
        </section>
      )}
    </div>
  );
}
```

## 5. Add to Router

```typescript
// App.tsx or router.tsx

import { DPAnalysisPage } from '@/pages/DPAnalysisPage';

const routes = [
  // ... other routes
  {
    path: '/dp/analysis/:agentName?',
    element: <DPAnalysisPage />,
  },
];
```

## 6. Navigation Link

Add link to your navigation:

```typescript
// NavigationSidebar.tsx or similar

<NavLink to="/dp/analysis">
  DP Analysis
</NavLink>
```

## 7. Live Updates (Optional)

For real-time updates during DP solving:

```typescript
// hooks/useDPEvaluationLive.ts

import { useEffect, useState } from 'react';
import type { ValueScore, PolicyTrace } from '@/components/dp';

export function useDPEvaluationLive(agentName: string) {
  const [valueScore, setValueScore] = useState<ValueScore | null>(null);
  const [policyTrace, setPolicyTrace] = useState<PolicyTrace | null>(null);

  useEffect(() => {
    const eventSource = new EventSource(`/api/dp/evaluate/${agentName}/stream`);

    eventSource.addEventListener('value_score', (e) => {
      setValueScore(JSON.parse(e.data));
    });

    eventSource.addEventListener('trace_update', (e) => {
      setPolicyTrace(JSON.parse(e.data));
    });

    return () => eventSource.close();
  }, [agentName]);

  return { valueScore, policyTrace };
}
```

Backend SSE endpoint:

```python
from fastapi.responses import StreamingResponse

@router.get("/dp/evaluate/{agent_name}/stream")
async def evaluate_agent_stream(agent_name: str):
    """Stream DP evaluation updates via SSE."""

    async def event_generator():
        # Initial score
        score = vf.evaluate(agent_name, ...)
        yield f"event: value_score\ndata: {score.to_dict()}\n\n"

        # Solve with trace updates
        for step in solver.solve_iterative():
            yield f"event: trace_update\ndata: {step.to_dict()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

## 8. Testing

Test with mock data from `example.tsx`:

```typescript
import { DPExample } from '@/components/dp/example';

// Render in dev mode:
<DPExample />
```

## Styling Notes

Components use design tokens from `hypergraph/design-system.css`. Ensure the design system CSS is imported in your app:

```typescript
// App.tsx or main layout
import '@/hypergraph/design-system.css';
```

## Health Colors

Components automatically use the health gradient:

- **Green** (>= 80%): `--health-healthy`
- **Yellow** (60-80%): `--health-degraded`
- **Orange** (40-60%): `--health-warning`
- **Red** (< 40%): `--health-critical`

No additional configuration needed.

## Accessibility

All components support:
- ✅ Keyboard navigation (Tab, Enter, Space)
- ✅ ARIA labels and roles
- ✅ Focus indicators
- ✅ Tooltips on hover

## Performance

For large traces (>100 entries), use `maxEntries` prop:

```typescript
<PolicyTraceView trace={trace} maxEntries={50} />
```

Components are pure and memoization-friendly.

## Next Steps

1. Implement backend `/api/dp/evaluate` endpoint
2. Create `useDPEvaluation` hook
3. Add DP analysis page to router
4. Test with real DP solver results
5. Add export functionality (JSON/CSV)

---

**Status**: Ready for integration
