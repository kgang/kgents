# Contract Coherence Protocol

> *"The interface IS the proof. Drift IS the contradiction."*

## The Problem We Solve

**Bug witnessed (2025-12-26)**: Frontend crashed with `trail.gaps is undefined` because:
- Frontend expected `TrailResponse.gaps: TimeGap[]`
- Backend returned `TrailResponse.gap_minutes: int` (different field!)
- No verification caught this drift before runtime

This is a **PROBLEMATIC tension** (dialectical analysis): two systems evolved separately without contract enforcement. Super-additive loss—the combined system broke where either alone worked.

---

## The Law

### L6: Contract Coherence Law

> **Every pilot API contract MUST have a single source of truth, and both frontend and backend MUST verify against it.**

This law derives from:
- **Composability (Principle 5)**: `Frontend >> Backend` must compose without runtime surprises
- **Compression Honesty (L4)**: The interface definition IS the compression; drift corrupts it
- **Provenance (L5)**: Every API claim must link to its contract definition

---

## The Protocol

### 1. Contract Source of Truth

For each pilot, define contracts in `shared-primitives/src/contracts/<pilot>.ts`:

```typescript
// shared-primitives/src/contracts/daily-lab.ts

/**
 * TrailResponse Contract
 *
 * @layer L4 (Specification)
 * @backend protocols/api/daily_lab.py:TrailResponse
 * @frontend pilots-web/src/api/witness.ts:TrailResponse
 */
export interface TrailResponse {
  marks: TrailMark[];
  gaps: TimeGap[];     // REQUIRED: array of gaps, not scalar
  date: string;        // ISO date string
  // Optional fields (have defaults)
  total?: number;
  position?: number;
  gap_minutes?: number;  // Legacy, deprecated
  review_prompt?: string;
}

// Contract invariants (verified at test time)
export const TRAIL_RESPONSE_INVARIANTS = {
  'gaps is array': (r: TrailResponse) => Array.isArray(r.gaps),
  'marks is array': (r: TrailResponse) => Array.isArray(r.marks),
  'date is ISO string': (r: TrailResponse) => /^\d{4}-\d{2}-\d{2}$/.test(r.date),
} as const;
```

### 2. Backend Contract Verification

Add to `protocols/api/_tests/test_contracts.py`:

```python
"""
Contract Coherence Tests

Verifies backend responses match shared contract definitions.
Run: uv run pytest protocols/api/_tests/test_contracts.py -v
"""

import pytest
from protocols.api.daily_lab import TrailResponse

class TestTrailResponseContract:
    """Verify TrailResponse matches shared contract."""

    def test_gaps_is_list(self):
        """Contract: gaps must be a list, not scalar."""
        # This test WOULD HAVE caught the bug
        response = TrailResponse(
            marks=[],
            date="2025-12-26",
            gaps=[],  # Must be present and be a list
        )
        assert isinstance(response.gaps, list)

    def test_required_fields_present(self):
        """Contract: marks, gaps, date are required."""
        # Pydantic will raise if required fields missing
        with pytest.raises(Exception):
            TrailResponse(marks=[])  # Missing gaps and date
```

### 3. Frontend Contract Verification

Add to `pilots-web/src/api/__tests__/contracts.test.ts`:

```typescript
import { TrailResponse, TRAIL_RESPONSE_INVARIANTS } from '@kgents/shared-primitives/contracts/daily-lab';

describe('TrailResponse Contract', () => {
  test('invariants hold for valid response', () => {
    const response: TrailResponse = {
      marks: [],
      gaps: [],
      date: '2025-12-26',
    };

    for (const [name, check] of Object.entries(TRAIL_RESPONSE_INVARIANTS)) {
      expect(check(response)).toBe(true);
    }
  });

  test('defensive handling for malformed response', () => {
    // Simulate backend returning wrong shape
    const malformed = { marks: [], gap_minutes: 0 } as unknown as TrailResponse;

    // Frontend should handle gracefully
    const gaps = malformed.gaps ?? [];
    expect(Array.isArray(gaps)).toBe(true);
  });
});
```

### 4. Integration Verification (CI Gate)

Add to `.github/workflows/contract-coherence.yml`:

```yaml
name: Contract Coherence

on: [push, pull_request]

jobs:
  verify-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Backend contract tests
        run: |
          cd impl/claude
          uv run pytest protocols/api/_tests/test_contracts.py -v

      - name: Frontend contract tests
        run: |
          cd impl/claude/pilots-web
          npm test -- --testPathPattern=contracts

      - name: Contract drift detection
        run: |
          # Compare TypeScript and Python type definitions
          # Flag any drift as CI failure
          ./scripts/check-contract-drift.sh
```

---

## Qualitative Assertions (New)

Add to each pilot's PROTO_SPEC.md:

- **QA-5**: API contracts must have a single source of truth in `shared-primitives/contracts/`.
- **QA-6**: Both frontend and backend must have contract verification tests.
- **QA-7**: Contract drift must be caught at CI time, not runtime.

---

## The Minimal Kernel

From Zero Seed axioms, this protocol derives from:

| Axiom | Application |
|-------|-------------|
| **A2 (Morphism)** | API calls are morphisms; contracts define their types |
| **G (Galois Ground)** | Contract drift = information loss = super-additive Galois loss |
| **Composition Law** | `Frontend(Backend(x))` must equal `Expected(x)` |

The **Galois loss** interpretation:
- `L(contract_alone) = 0` (well-defined)
- `L(frontend_impl) ≈ 0` (matches contract)
- `L(backend_impl) ≈ 0` (matches contract)
- `L(frontend + backend) >> L(frontend) + L(backend)` when they **drift**

Super-additivity signals contradiction. Contract tests prevent this.

---

## Horizontal Quality Gates (Added 2025-12-26)

These gates apply to ALL pilots. They were discovered during zero-seed run-001 and are now mandatory:

### HQ-1: Request Model Law

All API endpoints accepting complex inputs MUST use Pydantic request models:

```python
# ❌ WRONG - bare list parameter causes validation errors to leak as objects
@router.post("/discover")
async def discover(items: list[str]):
    ...

# ✅ RIGHT - Pydantic model properly handles JSON body
class DiscoverRequest(BaseModel):
    items: list[str]

@router.post("/discover")
async def discover(request: DiscoverRequest):
    ...
```

**Why**: FastAPI treats bare `list[str]` as expecting the body to BE a list, not an object containing a list. This causes 422 errors with `{type, loc, msg}` format that renders as `[object Object]` in React.

### HQ-2: Error Normalization Law

Frontend MUST normalize all API errors before rendering:

```typescript
function extractErrorMessage(error: unknown, fallback: string): string {
  const e = error as Record<string, unknown>;

  // String detail (normal error)
  if (typeof e?.detail === 'string') return e.detail;

  // Array detail (FastAPI validation errors)
  if (Array.isArray(e?.detail)) {
    return e.detail.map(i => i.msg).filter(Boolean).join('; ');
  }

  return fallback;
}
```

**Why**: FastAPI returns validation errors as `{detail: [{type, loc, msg}...]}`. Rendering `error.detail` directly causes "Objects are not valid as a React child" crashes.

### HQ-3: Semantic Baseline Law

Universal human values MUST always be acceptable as axiom candidates:

- "love", "courage", "honesty", "compassion", etc. should never be rejected
- Even if Galois loss > 0.05, these are pre-approved as "baseline values"
- Maintain a canonical list in `shared-primitives/src/constants/baseline-values.ts`

**Why**: Gatekeeping universal values creates the anti-pattern of "technical gatekeeping" where the system rejects obviously valid beliefs.

### HQ-4: No Demo Data Law

Pilots MUST be self-contained and fully-functional for first-time users!
You are not creating an experimental prototype, you are making a production, consumer grade experience!

**Why**: Enforces the building of things wanting building.

### HQ-5: Component Wiring Law (Added 2025-12-26)

Generated components MUST be wired into the component tree:

- A file on disk is NOT a feature until it's integrated
- Every component must be: imported, rendered, connected to props
- Stage 3.5 (Wire) explicitly audits this before smoke testing
- Common failure: component generated but never imported into parent

**Why**: Code files that exist but aren't integrated provide zero value to users.

### HQ-6: Core Loop Smoke Test (Added 2025-12-26)

Smoke tests MUST verify core loop advancement, not just compilation:

- Typecheck passing is NECESSARY but NOT SUFFICIENT
- Integration tests must simulate actual usage (60+ seconds for games)
- The test must EXECUTE the core loop and verify state changes
- For games: waves must advance, enemies must spawn, mechanics must function
- "Tests pass but game doesn't play" is a FAIL condition

**Why**: Runs 005-008 of wasm-survivors compiled successfully but had broken core loops. Static analysis verifies structure; smoke tests must verify behavior.

---

## Universal Implementation Laws (L-IMPL)

These laws apply to ALL pilots generating TypeScript/JavaScript code. They encode debugging wisdom that prevents predictable failures.

> *"The pattern IS the prevention. The before/after IS the proof."*

### L-IMPL-1: Testable Time

> **All time-based logic MUST use simulated time, not Date.now() or performance.now().**

```typescript
// ✅ RIGHT - Testable: time advances with simulation
let gameTime = 0;

update(deltaMs: number) {
  gameTime += deltaMs;  // Always advance, even during pauses

  if (gameTime - waveStartTime > waveTimeLimit) {
    advanceWave();
  }
}

// ❌ WRONG - Tests will fail: real time doesn't advance during simulation
update(deltaMs: number) {
  const now = Date.now();

  if (now - waveStartTime > waveTimeLimit) {
    advanceWave();  // Never triggers: Date.now() advances ~300ms while simulating 60s
  }
}
```

**Rationale**: Tests simulate 60 seconds of gameplay in ~300ms real time. `Date.now()` doesn't advance proportionally. This bug caused wave progression failures in wasm-survivors run-005 and run-006.

**Detection**: `grep -r "Date.now()\|performance.now()" src/ --include="*.ts"` should return 0 matches in game logic.

**Game Loop Note (Added 2025-12-26)**: For game pilots, simulation time != real time. When integration tests simulate 60 seconds of gameplay, the simulation advances rapidly (e.g., 300ms wall-clock time) while game time advances 60,000ms. Code using `Date.now()` will observe ~300ms passing while expecting 60,000ms. Always pass `deltaMs` as a parameter and accumulate it in a `gameTime` variable. This pattern ensures tests can validate wave progression, enemy spawning, and time-based mechanics by controlling the time parameter directly.

### L-IMPL-2: ES Module Patterns

> **Use ES imports exclusively. No CommonJS. No bare require().**

```typescript
// ✅ RIGHT - ES modules
import { GameState } from './types';
import type { Config } from './config';  // Type-only import
export function createGame() { ... }
export default GameEngine;

// ❌ WRONG - CommonJS (will fail in modern bundlers)
const { GameState } = require('./types');
module.exports = { createGame };
module.exports.default = GameEngine;
```

**Rationale**: Modern bundlers (Vite, esbuild) expect ES modules. CommonJS causes build failures and prevents tree-shaking.

### L-IMPL-3: Exhaustive Exports

> **Every function called cross-file MUST be explicitly exported.**

```typescript
// utils.ts
// ✅ RIGHT - Exported, callable from other files
export function calculateDamage(base: number, multiplier: number): number {
  return base * multiplier;
}

// ❌ WRONG - Not exported, invisible to other files
function calculateDamage(base: number, multiplier: number): number {
  return base * multiplier;
}
```

**Detection**: If `grep -r "calculateDamage" src/` finds usage in multiple files but `grep "export.*calculateDamage"` returns nothing, this law is violated.

### L-IMPL-4: Type-Only Imports

> **Use `import type` for imports only used in type annotations.**

```typescript
// ✅ RIGHT - Explicit type import, no runtime cost, no unused warnings
import { type GameState, type PlayerState } from './types';
import { UPGRADES, createPlayer } from './game';

function update(state: GameState): PlayerState { ... }

// ❌ WRONG - May trigger TS6133 "unused variable" if only used as type
import { GameState, PlayerState, UPGRADES, createPlayer } from './types';
```

**Rationale**: Run-005 had 32 unused variable errors, most from type-only imports. Explicit `type` keyword eliminates these at source and improves tree-shaking.

### L-IMPL-5: Test Dependencies

> **Test frameworks MUST have all required dependencies in package.json.**

```json
{
  "devDependencies": {
    "vitest": "^1.1.0",
    "jsdom": "^24.0.0",   // Required for DOM environment
    "@testing-library/react": "^14.0.0"  // If testing React
  }
}
```

**Rationale**: Run-005 and run-006 both failed initially with "Cannot find dependency jsdom". This is a predictable requirement that should never be missing.

**Detection**: If `vitest.config.ts` contains `environment: 'jsdom'`, then `jsdom` MUST be in devDependencies.

### L-IMPL-6: No Dynamic Require (Added 2025-12-26)

> **All imports MUST be static ES imports at file top. No dynamic require() in ES module contexts.**

```typescript
// ✅ RIGHT - Static imports at file top
import { UPGRADES } from './upgrades';
import { EnemyType } from './types';

function getUpgrade(id: string) {
  return UPGRADES.find(u => u.id === id);
}

// ❌ WRONG - Dynamic require in ES module context
function getUpgrade(id: string) {
  const { UPGRADES } = require('./upgrades');  // FAILS at runtime!
  return UPGRADES.find(u => u.id === id);
}
```

**Rationale**: Dynamic require statements in ES module contexts cause runtime failures that static analysis (TypeScript, ESLint) cannot detect. The pattern may work in CommonJS but fails silently in ES modules, causing smoke tests to pass compilation but fail execution. Witnessed in wasm-survivors run-009.

**Detection**: `grep -r "require(" src/ --include="*.ts" --include="*.tsx"` should return 0 matches in ES module projects.

---

## Anti-Patterns

| Anti-Pattern | Symptom | This Protocol Prevents |
|--------------|---------|------------------------|
| **Dual source of truth** | TypeScript and Python define same type differently | Single contract definition |
| **Runtime discovery** | Crashes in production reveal drift | CI-time verification |
| **Silent degradation** | Frontend shows blank UI, no error | Invariant assertions |
| **Copy-paste contracts** | Types duplicated, then diverge | Import from shared source |
| **Bare list parameters** | FastAPI validation errors leak to React | Request model law (HQ-1) |
| **Raw error rendering** | "Objects are not valid as React child" | Error normalization (HQ-2) |
| **Strict value thresholds** | "Love" rejected as non-axiom | Semantic baseline (HQ-3) |
| **Cold start friction** | Users don't know what to do | Demo data law (HQ-4) |
| **Dynamic require()** | Runtime module failures in ES context | No dynamic require (L-IMPL-6) |
| **Typecheck-only validation** | Code compiles but core loop broken | Smoke test core loop simulation |

---

## Implementation Checklist

For each pilot API endpoint:

- [ ] Contract type defined in `shared-primitives/src/contracts/`
- [ ] Backend Pydantic model imports or matches contract
- [ ] Frontend API client imports contract type
- [ ] Backend has contract verification test
- [ ] Frontend has contract verification test
- [ ] CI runs both contract test suites
- [ ] Optional: Generate Python from TypeScript (or vice versa)

---

## The Fix Applied (2025-12-26)

**Immediate fix**:
1. Backend `daily_lab.py` now returns `gaps: list[TimeGapItem]`
2. Frontend uses defensive `trail.gaps ?? []`

**Principled fix** (this protocol):
1. Add `shared-primitives/src/contracts/daily-lab.ts` with canonical types
2. Add contract tests to both backend and frontend
3. Add CI workflow to verify contract coherence

---

*"The contract IS the composition. Verify the contract, verify the composition."*

*Filed: 2025-12-26 | Witnessed by: trail.gaps is undefined*
