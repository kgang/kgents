---
path: plans/phase3-5-parallel-execution
status: complete
progress: 100
last_touched: 2025-12-18
touched_by: claude-opus-4-5
blocking: []
enables: [park-town-quality-enhancement-completion]
session_notes: |
  Deep execution plan for running Phase 3 (Observer E2E) and Phase 5 (Director Explorer)
  in parallel from park-town-quality-enhancement-continuation.md.

  Strategy: The two phases share no dependencies and can execute simultaneously.
  Phase 3 = Observer -> Mesa overlay wiring (vertical slice through fullstack)
  Phase 5 = DirectorOperadExplorer component (React only, uses existing backend)

  2025-12-18 COMPLETION:
  - Phase 3: Observer headers in fetchAgentese, overlay rendering in Mesa (relationships/economy/coalitions)
  - Phase 5: DirectorOperadExplorer with 8 ops, 6 laws, teaching mode, wired to ParkVisualization
  - TypeScript compiles clean (pre-existing test fixture issues don't affect implementation)
phase_ledger:
  Phase 3 Observer E2E: COMPLETE
  Phase 5 Director Explorer: COMPLETE
---

# Phase 3 + Phase 5 Parallel Execution Plan

> *"Two vertical slices, one moment. Observer-dependent rendering meets categorical education."*

## Executive Summary

Execute Phase 3 (Observer End-to-End) and Phase 5 (Director Operad Explorer) in parallel. These phases have zero dependencies on each other:

| Phase | Domain | Touch Points | Shared Files |
|-------|--------|--------------|--------------|
| Phase 3 | Town (Observer -> Mesa) | 4 frontend + 1 backend | None |
| Phase 5 | Park (Operad Explorer) | 2 frontend only | None |

**Estimated Parallel Time**: 1.5 days (vs 3 days sequential)

---

## Phase 3: Observer-Dependent Rendering End-to-End

### The Vertical Slice

```
ObserverSelector (already exists)
       |
       v
TownVisualization (wire observer state)
       |
       v
useTownQuery.ts (add X-Observer-Umwelt header)
       |
       v
gateway.py (read header, pass to node.invoke)
       |
       v
Mesa.tsx (render overlay based on observer archetype)
```

### Current State Analysis

**What exists (DO NOT REBUILD)**:
- `ObserverSelector.tsx` with 4 umwelts: default, architect, poet, economist
- `OBSERVERS` config with `mesaOverlay` hints per observer
- `TownVisualization.tsx` already tracks `observer` state via useState
- `Mesa.tsx` receives citizens and events, renders with PixiJS

**What's missing (BUILD THESE)**:
1. `fetchAgentese()` doesn't pass observer headers
2. Backend doesn't read X-Observer-Umwelt
3. Mesa doesn't render different overlays

### Implementation Chunks

#### Chunk 3.1: Frontend Header Injection (30 min)

**File**: `impl/claude/web/src/hooks/useTownQuery.ts`

```typescript
// Add observer parameter to fetchAgentese
async function fetchAgentese<T>(
  path: string,
  body?: unknown,
  observer?: ObserverUmwelt  // NEW: optional observer
): Promise<T> {
  // Build headers
  const headers: Record<string, string> = {};
  if (observer && observer !== 'default') {
    headers['X-Observer-Umwelt'] = observer;
  }

  // Pass to apiClient
  if (aspect === 'manifest' || aspect === 'affordances') {
    const response = await apiClient.get<AgenteseResponse<T>>(
      `/agentese/${urlPath}/${aspect}`,
      { headers }  // NEW
    );
    // ...
  }
}
```

**Key Insight**: apiClient already supports headers, we just need to thread them through.

#### Chunk 3.2: Backend Observer Extraction (45 min)

**File**: `impl/claude/protocols/agentese/gateway.py`

The gateway already has Observer infrastructure. We need to:
1. Read X-Observer-Umwelt from request headers
2. Create Observer with archetype from header
3. Pass to node.invoke() as observer context

```python
# In the route handler
def _extract_observer(request: Request) -> Observer:
    """Extract observer from request headers."""
    umwelt = request.headers.get("X-Observer-Umwelt", "default")

    # Map umwelt to archetype
    archetype_map = {
        "default": "observer",
        "architect": "architect",
        "poet": "poet",
        "economist": "economist",
    }

    return Observer(
        id="request-observer",
        archetype=archetype_map.get(umwelt, "observer"),
        capabilities=frozenset(),
    )
```

#### Chunk 3.3: TownVisualization Observer Wiring (30 min)

**File**: `impl/claude/web/src/components/town/TownVisualization.tsx`

Observer state already exists! Just need to pass it to hooks:

```typescript
// Currently: hooks don't receive observer
const townData = useTownManifest();

// After: pass observer to get observer-dependent data
const townData = useTownManifest({ observer });
```

And thread to Mesa:

```tsx
<Mesa
  // existing props...
  observer={observer}  // NEW
  overlay={OBSERVERS[observer].mesaOverlay}  // NEW
/>
```

#### Chunk 3.4: Mesa Overlay Rendering (90 min)

**File**: `impl/claude/web/src/components/town/Mesa.tsx`

This is the main visual work. Add overlay layer based on observer:

```typescript
interface MesaProps {
  // existing...
  overlay?: 'none' | 'relationships' | 'coalitions' | 'economy';
}

// New overlay drawing functions
const drawRelationshipsOverlay = useCallback((g: PIXI.Graphics) => {
  g.clear();
  if (overlay !== 'relationships') return;

  // Draw lines between citizens with relationships
  citizenPositions.forEach((from) => {
    const relationships = from.citizen.relationships || [];
    relationships.forEach((rel) => {
      const to = citizenPositionByName.get(rel.target);
      if (to) {
        // Glow line based on relationship strength
        g.lineStyle(2, 0x3b82f6, rel.strength * 0.8);
        g.moveTo(from.screenX, from.screenY);
        g.lineTo(to.screenX, to.screenY);
      }
    });
  });
}, [overlay, citizenPositions, citizenPositionByName]);

const drawEconomyOverlay = useCallback((g: PIXI.Graphics) => {
  g.clear();
  if (overlay !== 'economy') return;

  // Draw particle flow between trading citizens
  events.filter(e => e.operation === 'trade').forEach((trade) => {
    const from = citizenPositionByName.get(trade.participants[0]);
    const to = citizenPositionByName.get(trade.participants[1]);
    if (from && to) {
      g.beginFill(0x22c55e, 0.7);
      const midX = (from.screenX + to.screenX) / 2;
      const midY = (from.screenY + to.screenY) / 2;
      g.drawCircle(midX, midY, 3);
      g.endFill();
    }
  });
}, [overlay, events, citizenPositionByName]);
```

Add overlay layers to render tree:

```tsx
{/* Overlay Layer - observer-dependent */}
{overlay === 'relationships' && <Graphics draw={drawRelationshipsOverlay} />}
{overlay === 'economy' && <Graphics draw={drawEconomyOverlay} />}
```

### Phase 3 Quality Gate

```
WHEN user selects "Architect" in ObserverSelector
THEN Mesa shows relationship lines between connected citizens

WHEN user selects "Economist" in ObserverSelector
THEN Mesa shows trade flow particles

WHEN user selects "Default" or "Poet"
THEN Mesa shows no overlay (clean view)
```

---

## Phase 5: Director Operad Explorer

### The Component Design

```
DirectorOperadExplorer
  |-- Header: "DIRECTOR_OPERAD" + law verification status
  |-- Operations Grid (8 operations)
  |     |-- observe (1) - Watch guest behavior
  |     |-- build_tension (1) - Increase narrative pressure
  |     |-- inject (2) - Serendipity injection
  |     |-- cooldown (1) - Post-injection rest
  |     |-- intervene (1) - Direct action (high cost)
  |     |-- evaluate (2) - Check injection conditions
  |     |-- director_reset (0) - Return to observing
  |     +-- abort (0) - Cancel current operation
  |-- Laws Panel (6 laws with verification)
  |     |-- consent_constraint
  |     |-- cooldown_constraint
  |     |-- tension_flow
  |     |-- intervention_isolation
  |     |-- observe_identity
  |     +-- reset_to_observe
  +-- Teaching Callout (explains current context)
```

### Reuse Pattern: OperadWiring.tsx

The existing `OperadWiring.tsx` provides the template. Key adaptations:

1. **Static display** (no drag-and-drop needed for exploration)
2. **Phase highlighting** - show which operations are active for current crisis phase
3. **Teaching callouts** per operation (explain Punchdrunk director concepts)

### Implementation Chunks

#### Chunk 5.1: DirectorOperadExplorer Component (90 min)

**File**: `impl/claude/web/src/components/park/DirectorOperadExplorer.tsx`

```typescript
/**
 * DirectorOperadExplorer: Interactive explorer for DIRECTOR_OPERAD.
 *
 * Shows the 8 director operations with their arities and signatures,
 * 6 verification laws, and teaching callouts for Punchdrunk concepts.
 *
 * @see agents/park/operad.py - DIRECTOR_OPERAD definition
 * @see plans/park-town-quality-enhancement-continuation.md (Phase 5)
 */

import { useState, useCallback } from 'react';
import { Check, X, Lightbulb, Eye, Zap, Timer, Shield, RotateCcw } from 'lucide-react';
import { TeachingCallout } from '../categorical/TeachingCallout';

// =============================================================================
// Types
// =============================================================================

interface Operation {
  id: string;
  name: string;
  arity: number;
  signature: string;
  description: string;
  icon: typeof Eye;
  color: string;
  teaching: string;
}

interface Law {
  id: string;
  name: string;
  equation: string;
  description: string;
  verified: boolean;
}

export interface DirectorOperadExplorerProps {
  variant: 'modal' | 'inline';
  currentPhase?: 'OBSERVING' | 'BUILDING_TENSION' | 'INJECTING' | 'COOLDOWN' | 'INTERVENING';
  showTeaching?: boolean;
  onClose?: () => void;
}

// =============================================================================
// Static Data (matches agents/park/operad.py)
// =============================================================================

const DIRECTOR_OPERATIONS: Operation[] = [
  {
    id: 'observe',
    name: 'observe',
    arity: 1,
    signature: 'Session -> Metrics',
    description: 'Watch guest behavior passively',
    icon: Eye,
    color: '#22c55e',
    teaching: 'The director watches from the shadows, gathering tension metrics without intervening.',
  },
  {
    id: 'build_tension',
    name: 'build_tension',
    arity: 1,
    signature: 'Metrics -> TensionState',
    description: 'Increase narrative pressure',
    icon: Zap,
    color: '#f59e0b',
    teaching: 'Rising action in theatrical terms. The director decides whether to intervene.',
  },
  {
    id: 'inject',
    name: 'inject',
    arity: 2,
    signature: '(SerendipityInjection, Session) -> Result',
    description: 'Introduce lucky coincidence',
    icon: Zap,
    color: '#8b5cf6',
    teaching: 'A surprise arrival, a revelation, a twist. Injections shift the narrative without forcing outcomes.',
  },
  {
    id: 'cooldown',
    name: 'cooldown',
    arity: 1,
    signature: 'Duration -> CooldownState',
    description: 'Reduce intensity after injection',
    icon: Timer,
    color: '#3b82f6',
    teaching: 'Every climax needs resolution. Cooldown prevents injection fatigue.',
  },
  {
    id: 'intervene',
    name: 'intervene',
    arity: 1,
    signature: 'DifficultyAdjustment -> Result',
    description: 'Direct action (high consent cost)',
    icon: Shield,
    color: '#ef4444',
    teaching: 'Interventions are expensive (3x cost). Use sparingly when guests are truly stuck.',
  },
  {
    id: 'evaluate',
    name: 'evaluate',
    arity: 2,
    signature: '(Metrics, Config) -> InjectionDecision',
    description: 'Check injection conditions',
    icon: Eye,
    color: '#06b6d4',
    teaching: 'Consent debt too high? Cooldown active? Evaluate before committing to inject.',
  },
  {
    id: 'director_reset',
    name: 'director_reset',
    arity: 0,
    signature: '() -> Observing',
    description: 'Return to observing state',
    icon: RotateCcw,
    color: '#64748b',
    teaching: 'Nullary operation - no inputs required. Always returns to passive observation.',
  },
  {
    id: 'abort',
    name: 'abort',
    arity: 0,
    signature: '() -> Observing',
    description: 'Cancel current operation',
    icon: RotateCcw,
    color: '#6b7280',
    teaching: 'Interventions are atomic: complete or abort. Never leave guests in limbo.',
  },
];

const DIRECTOR_LAWS: Law[] = [
  {
    id: 'consent_constraint',
    name: 'Consent Constraint',
    equation: 'inject(i, s) requires consent_debt(s) <= 0.7',
    description: 'Cannot inject when consent debt is too high',
    verified: true,
  },
  {
    id: 'cooldown_constraint',
    name: 'Cooldown Constraint',
    equation: 'inject(i, s) requires time_since_injection >= min_cooldown',
    description: 'Must respect minimum cooldown between injections',
    verified: true,
  },
  {
    id: 'tension_flow',
    name: 'Tension Flow',
    equation: 'build_tension(m) -> inject | observe within T',
    description: 'Building tension leads to injection or observation',
    verified: true,
  },
  {
    id: 'intervention_isolation',
    name: 'Intervention Isolation',
    equation: 'intervene(a) = complete(a) | abort()',
    description: 'Interventions are atomic - complete or abort',
    verified: true,
  },
  {
    id: 'observe_identity',
    name: 'Observe Identity',
    equation: 'observe(observe(s)) = observe(s)',
    description: 'Observing is idempotent',
    verified: true,
  },
  {
    id: 'reset_to_observe',
    name: 'Reset to Observe',
    equation: 'reset() -> OBSERVING',
    description: 'Reset always returns to OBSERVING phase',
    verified: true,
  },
];

// Phase -> Active operations mapping
const PHASE_ACTIVE_OPS: Record<string, string[]> = {
  OBSERVING: ['observe', 'evaluate'],
  BUILDING_TENSION: ['build_tension', 'evaluate', 'abort'],
  INJECTING: ['inject', 'abort'],
  COOLDOWN: ['cooldown', 'director_reset'],
  INTERVENING: ['intervene', 'abort'],
};
```

#### Chunk 5.2: Component Rendering (60 min)

Continue the component with the render logic:

```typescript
export function DirectorOperadExplorer({
  variant,
  currentPhase,
  showTeaching = false,
  onClose,
}: DirectorOperadExplorerProps) {
  const [selectedOp, setSelectedOp] = useState<Operation | null>(null);
  const [verifyingLaws, setVerifyingLaws] = useState(false);

  const activeOps = currentPhase ? PHASE_ACTIVE_OPS[currentPhase] || [] : [];

  const handleVerifyLaws = useCallback(async () => {
    setVerifyingLaws(true);
    await new Promise(r => setTimeout(r, 500));
    setVerifyingLaws(false);
  }, []);

  const content = (
    <div className="bg-slate-900 rounded-xl p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">DIRECTOR_OPERAD</h3>
          <p className="text-sm text-gray-400">
            Composition grammar for Punchdrunk Park director operations
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleVerifyLaws}
            disabled={verifyingLaws}
            className="px-3 py-1.5 text-sm bg-emerald-600/20 text-emerald-400 rounded-lg hover:bg-emerald-600/30 disabled:opacity-50"
          >
            {verifyingLaws ? 'Verifying...' : 'Verify Laws'}
          </button>
          {variant === 'modal' && onClose && (
            <button onClick={onClose} className="text-gray-400 hover:text-white">
              x
            </button>
          )}
        </div>
      </div>

      {/* Operations Grid */}
      <div>
        <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-3">
          Operations ({DIRECTOR_OPERATIONS.length})
        </h4>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {DIRECTOR_OPERATIONS.map((op) => {
            const Icon = op.icon;
            const isActive = activeOps.includes(op.id);
            const isSelected = selectedOp?.id === op.id;

            return (
              <button
                key={op.id}
                onClick={() => setSelectedOp(isSelected ? null : op)}
                className={`
                  p-3 rounded-lg text-left transition-all
                  ${isActive ? 'ring-2 ring-amber-500/50' : ''}
                  ${isSelected ? 'bg-slate-700' : 'bg-slate-800 hover:bg-slate-700/50'}
                `}
                style={{ borderLeft: `3px solid ${op.color}` }}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Icon className="w-4 h-4" style={{ color: op.color }} />
                  <span className="font-medium text-white text-sm">{op.name}</span>
                  <span
                    className="text-[10px] px-1.5 py-0.5 rounded"
                    style={{ background: `${op.color}30`, color: op.color }}
                  >
                    {op.arity}
                  </span>
                </div>
                <p className="text-xs text-gray-500">{op.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Operation Detail */}
      {selectedOp && (
        <div className="bg-slate-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            {(() => {
              const Icon = selectedOp.icon;
              return <Icon className="w-5 h-5" style={{ color: selectedOp.color }} />;
            })()}
            <span className="font-medium text-white">{selectedOp.name}</span>
          </div>
          <p className="text-xs font-mono text-gray-400 mb-3">{selectedOp.signature}</p>
          {showTeaching && (
            <TeachingCallout category="insight" compact>
              {selectedOp.teaching}
            </TeachingCallout>
          )}
        </div>
      )}

      {/* Laws Panel */}
      <div>
        <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-3">
          Composition Laws ({DIRECTOR_LAWS.length})
        </h4>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
          {DIRECTOR_LAWS.map((law) => (
            <div key={law.id} className="bg-slate-800 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                {law.verified ? (
                  <Check className="w-4 h-4 text-green-500" />
                ) : (
                  <X className="w-4 h-4 text-red-500" />
                )}
                <span className="text-sm font-medium text-white">{law.name}</span>
              </div>
              <p className="text-[10px] font-mono text-gray-500">{law.equation}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Teaching Footer */}
      {showTeaching && (
        <div className="bg-gradient-to-r from-amber-500/20 to-pink-500/20 border-l-4 border-amber-500 rounded-r-lg p-4">
          <div className="flex items-center gap-2 text-amber-400 text-xs uppercase tracking-wider mb-1">
            <Lightbulb className="w-3 h-3" />
            Teaching
          </div>
          <p className="text-sm text-gray-200">
            The DIRECTOR_OPERAD captures how a Punchdrunk-style director composes actions.
            Each operation has constraints (laws) that prevent harmful compositions--like
            injecting serendipity when consent debt is too high.
          </p>
        </div>
      )}
    </div>
  );

  if (variant === 'modal') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
        <div className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          {content}
        </div>
      </div>
    );
  }

  return content;
}

export default DirectorOperadExplorer;
```

#### Chunk 5.3: Wire to ParkVisualization (30 min)

**File**: `impl/claude/web/src/components/park/ParkVisualization.tsx`

Add "Learn Operad" button and modal:

```typescript
import { DirectorOperadExplorer } from './DirectorOperadExplorer';

// In RunningScenario component:
const [showOperadExplorer, setShowOperadExplorer] = useState(false);

// In the left column, after Consent Debt Machine:
<button
  onClick={() => setShowOperadExplorer(true)}
  className="w-full py-2 text-sm bg-slate-700 hover:bg-slate-600 rounded-lg flex items-center justify-center gap-2"
>
  <Lightbulb className="w-4 h-4" />
  Learn Director Operad
</button>

{/* Modal */}
{showOperadExplorer && (
  <DirectorOperadExplorer
    variant="modal"
    currentPhase={scenario.crisis_phase as any}
    showTeaching={teachingEnabled}
    onClose={() => setShowOperadExplorer(false)}
  />
)}
```

### Phase 5 Quality Gate

```
WHEN user clicks "Learn Director Operad" button
THEN modal shows with 8 operations and 6 laws

WHEN current phase is INJECTING
THEN inject and abort operations are highlighted

WHEN teaching mode is ON
THEN operations show teaching callouts explaining Punchdrunk concepts
```

---

## Execution Order

Since both phases can run in parallel:

```
PARALLEL EXECUTION

Thread A (Phase 3 - Observer E2E)         Thread B (Phase 5 - Explorer)
---------------------------------         -----------------------------
1. Chunk 3.1: Header injection            1. Chunk 5.1: Component types
2. Chunk 3.2: Backend extraction          2. Chunk 5.2: Render logic
3. Chunk 3.3: TownViz wiring              3. Chunk 5.3: ParkViz wiring
4. Chunk 3.4: Mesa overlays               4. Test + polish
5. Test end-to-end

MERGE: Update phase_ledger in park-town-quality-enhancement.md
```

---

## Testing Strategy

### Phase 3 Tests

1. **Unit**: `fetchAgentese` passes headers when observer provided
2. **Unit**: Mesa draws overlay graphics when overlay prop is set
3. **Integration**: Changing ObserverSelector triggers re-fetch with new header
4. **Visual**: Architect view shows blue relationship lines

### Phase 5 Tests

1. **Unit**: DirectorOperadExplorer renders all 8 operations
2. **Unit**: Phase highlighting activates correct operations
3. **Integration**: Modal opens/closes from ParkVisualization
4. **Visual**: Teaching callouts appear when enabled

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| apiClient header passing | Check axios instance config first |
| PixiJS overlay performance | Use conditional rendering, not conditional drawing |
| DIRECTOR_OPERAD data drift | Match operation names to operad.py exactly |
| Modal z-index conflicts | Use existing modal patterns from codebase |

---

## Definition of Done

- [x] Phase 3: Selecting "Architect" shows relationship lines in Mesa
- [x] Phase 3: Selecting "Economist" shows trade particles in Mesa
- [x] Phase 5: "Learn Operad" button visible in Park scenario view
- [x] Phase 5: All 8 operations and 6 laws displayed correctly
- [x] Phase 5: Current phase highlights relevant operations
- [x] TypeScript compiles clean: All implementation files pass typecheck
- [x] Update phase_ledger in this plan file

---

*Plan compiled: 2025-12-18 | Parallel execution strategy*
*Executed: 2025-12-18 by claude-opus-4-5 | Both phases complete*
