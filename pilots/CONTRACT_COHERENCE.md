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

## Anti-Patterns

| Anti-Pattern | Symptom | This Protocol Prevents |
|--------------|---------|------------------------|
| **Dual source of truth** | TypeScript and Python define same type differently | Single contract definition |
| **Runtime discovery** | Crashes in production reveal drift | CI-time verification |
| **Silent degradation** | Frontend shows blank UI, no error | Invariant assertions |
| **Copy-paste contracts** | Types duplicated, then diverge | Import from shared source |

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
