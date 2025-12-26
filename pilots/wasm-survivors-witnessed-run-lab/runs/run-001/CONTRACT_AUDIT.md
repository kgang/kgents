# Run 001 - Contract Audit

**Pilot**: wasm-survivors-witnessed-run-lab
**Date**: 2025-12-26
**Decision**: **GO** (with amendments)

## Required Contracts Analysis

### 1. Galois Loss Contracts (EXISTS - shared-primitives/contracts/galois.ts)

| Field | TypeScript | Python (services/zero_seed/galois) | Status |
|-------|------------|-------------------------------------|--------|
| GaloisLossRequest.content | string | str | MATCH |
| GaloisLossRequest.use_cache | boolean? | bool = True | MATCH |
| GaloisLossResponse.loss | number | float | MATCH |
| GaloisLossResponse.method | string | str | MATCH |
| GaloisLossResponse.metric_name | string | str | MATCH |
| GaloisLossResponse.cached | boolean | bool | MATCH |
| GaloisLossResponse.evidence_tier | EvidenceTier | str | MATCH |
| ContradictionRequest.content_a | string | str | MATCH |
| ContradictionRequest.content_b | string | str | MATCH |
| ContradictionRequest.tolerance | number? | float = 0.1 | MATCH |
| ContradictionResponse.is_contradiction | boolean | bool | MATCH |
| ContradictionResponse.strength | number | float | MATCH |
| ContradictionResponse.loss_a | number | float | MATCH |
| ContradictionResponse.loss_b | number | float | MATCH |
| ContradictionResponse.loss_combined | number | float | MATCH |
| ContradictionResponse.contradiction_type | ContradictionType | str | MATCH |

**Verdict**: All Galois contracts exist and match. Type guards and normalizers present.

### 2. Witness Contracts (EXISTS - shared-primitives/witness/)

| Component | TypeScript | Python (services/witness/) | Status |
|-----------|------------|---------------------------|--------|
| Mark | MarkCaptureInput types | mark.py:Mark | PARTIAL |
| Crystal | CrystalCard:Crystal | crystal.py:Crystal | PARTIAL |
| Trail | TrailTimeline:TrailMark | daily_lab.py:Trail | MATCH |
| CompressionHonesty | CrystalCard:CompressionHonesty | crystal.py | MATCH |

**Partial Match Details**:
- Mark: Frontend expects simplified structure; backend Mark has full provenance
- Crystal: Frontend Crystal is projection of backend Crystal (acceptable)

### 3. Run-Specific Contracts (NEEDED - Define for this pilot)

For the wasm-survivors pilot, we need additional contracts:

#### 3a. RunMark (Build Shift Marking - L1)

```typescript
/** Mark for a build shift during a run */
interface RunMark {
  mark_id: string;
  run_id: string;
  timestamp: string;
  // Build state
  build_before: BuildState;
  build_after: BuildState;
  // Shift metadata
  shift_type: 'upgrade_taken' | 'upgrade_skipped' | 'build_pivot' | 'risk_taken';
  justification?: string;
  // Galois coherence
  galois_loss: number;
  is_drift: boolean;
}

interface BuildState {
  upgrades: string[];
  synergies: string[];
  risk_level: 'low' | 'medium' | 'high';
  tempo: 'slow' | 'normal' | 'fast';
}
```

#### 3b. GhostAlternative (L3 Ghost Commitment)

```typescript
/** Unchosen path recorded as ghost */
interface GhostAlternative {
  ghost_id: string;
  run_id: string;
  decision_point_id: string;  // Links to RunMark
  // What was offered but not taken
  unchosen_upgrade: string;
  unchosen_synergies: string[];
  // Counterfactual reasoning
  hypothetical_impact: 'beneficial' | 'neutral' | 'harmful' | 'unknown';
  reasoning?: string;
}
```

#### 3c. RunCrystal (L5 Proof Compression)

```typescript
/** Compressed proof of a run */
interface RunCrystal {
  crystal_id: string;
  run_id: string;
  // Temporal bounds
  started_at: string;
  ended_at: string;
  // Outcome
  outcome: 'victory' | 'defeat' | 'abandoned';
  waves_survived: number;
  // Build identity claim
  build_claim: string;  // e.g., "Aggressive glass cannon with late defensive pivot"
  // Causal summary
  key_pivots: RunMark[];
  ghost_count: number;
  // Coherence metrics
  average_galois_loss: number;
  total_drift_events: number;
  // Constitutional alignment
  style_descriptors: string[];  // Descriptive, not judgmental
}
```

### 4. Contract Verification Checklist

| Requirement | Status | Notes |
|-------------|--------|-------|
| All required fields present in TypeScript | PARTIAL | Need Run-specific contracts |
| All required fields present in Python | YES | Backend has full Mark/Crystal/Galois |
| Types structurally equivalent | YES | Arrays match, optionals have defaults |
| API paths match | YES | /api/galois/*, /api/witness/* |
| Type guards exist | YES | isGaloisLossResponse, etc. |
| Normalizers exist | YES | normalizeGaloisLossResponse, etc. |

## Decision: GO

**Rationale**:
1. Core Galois contracts are complete and tested
2. Witness contracts have necessary overlap
3. Run-specific contracts (RunMark, GhostAlternative, RunCrystal) can be added as extensions
4. No breaking changes needed to existing infrastructure

## Amendments Required Before Full Implementation

### Amendment 1: Define wasm-survivors contract file

Create `shared-primitives/contracts/wasm-survivors.ts` with:
- RunMark interface
- GhostAlternative interface
- RunCrystal interface
- Type guards
- Normalizers

### Amendment 2: Backend service for run witnessing

Create `services/witness/run_lab.py` following the pattern of `daily_lab.py`:
- RunMarkCapture (analogous to DailyMarkCapture)
- RunTrail (analogous to Trail)
- RunCrystallizer (analogous to DailyCrystallizer)
- Ghost alternative recording

### Amendment 3: Galois integration for build drift

Connect `services/zero_seed/galois/distance.py` to run marks:
- BuildState -> string representation for distance computation
- Drift threshold configuration (from PROTO_SPEC)

## Evidence for GO Decision

1. **Galois contracts fully operational** - already serving other pilots
2. **Witness primitives proven** - daily_lab.py demonstrates the pattern
3. **Contract coherence pattern established** - can follow existing examples
4. **No breaking changes** - additive contracts only

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Latency from Galois computation | Medium | Use fallback metrics, cache aggressively |
| Build state serialization overhead | Low | Lightweight BuildState structure |
| Ghost layer complexity | Medium | Start with single-ghost-per-pivot, expand later |

---

*Audited: 2025-12-26*
*Verdict: GO with amendments*
