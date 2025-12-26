# Run 001 Learnings

**Pilot**: wasm-survivors-witnessed-run-lab
**Run**: 001 (Initial Generation)
**Date**: 2025-12-26

## Key Insights

### 1. Galois Loss as Style Signal, Not Error Metric

**Insight**: The Galois loss in game contexts measures **style coherence**, not correctness. High loss = risky/adaptive play, not bad play.

**Evidence**: The `_generate_build_claim()` function interprets high-loss runs as "pushed too far" rather than "made mistakes". This reframing is critical for QA-2 (style is SEEN, not judged).

**Implication**: When integrating with the game, present Galois loss as a **drift indicator** (player is exploring/adapting) not a **quality score** (player is doing well/poorly).

### 2. Ghost Alternatives Enable Counterfactual Reasoning

**Insight**: Recording unchosen paths (L3) creates a natural foundation for the counterfactual analysis the PROTO_SPEC envisions. The ghost is not "what you should have done" but "the road that remains open."

**Evidence**: `GhostAlternative.hypothetical_impact` defaults to "unknown" - we don't assume unchosen paths were better or worse.

**Implication**: The ghost layer could enable a "what-if" mode where players can mentally simulate unchosen branches without judgment.

### 3. Latency is the Make-or-Break Requirement

**Insight**: All four anti-success patterns that mention perception (surveillance creep, speed tax) come down to **latency**. If witnessing adds any perceptible delay, the pilot fails.

**Evidence**: The implementation uses:
- Synchronous operations only
- Fallback distance metrics (no API calls)
- Latency tracking in every public method

**Implication**: Any production integration MUST include latency monitoring. Consider:
- Web Worker for witness computations
- Adaptive disabling if latency exceeds threshold
- Caching of Galois loss for similar build states

### 4. Crystal Compression is Narrative Compression

**Insight**: L5 (Proof Compression Law) is not just about reducing data - it's about extracting the **narrative** of the run. The `build_claim` is a story, not a summary.

**Evidence**: `_generate_build_claim()` synthesizes pivot patterns into phrases like "aggressive risk-taker with adaptive pivots who pushed too far."

**Implication**: Crystal generation could eventually use LLM to create richer narratives, but the current pattern-based approach validates the concept without latency cost.

### 5. Daily Lab Pattern Transfers Well

**Insight**: The `daily_lab.py` pattern (Mark -> Trail -> Crystal -> Export) transfers directly to game runs. The main adaptation is domain-specific: `DailyMark` -> `RunMark`, `DailyTag` -> `ShiftType`.

**Evidence**: `RunLab` structure mirrors `DailyLab`:
- `mark_shift()` ~ `capture.quick()`
- `record_ghost()` ~ new (game-specific)
- `get_trail()` ~ `trail.for_today()`
- `crystallize()` ~ `crystallize.crystallize_day()`

**Implication**: Future pilots can follow this pattern. The witnessed-regeneration protocol creates a reusable skeleton.

## Prompt Improvements for Run 002

### 1. Include Canary Testing Framework

The current implementation lacks automated canary success criteria testing. Run 002 should include:

```python
class CanaryTest:
    def test_explain_run_30_seconds(self, crystal: RunCrystal, trail: list[RunMark]) -> bool:
        """Canary 1: Crystal + trail can explain run in 30s."""
        # Metric: word count of crystal.build_claim + key_pivot briefs < 50 words
        pass

    def test_one_ghost_per_pivot(self, marks: list[RunMark], ghosts: list[GhostAlternative]) -> bool:
        """Canary 3: At least one ghost per major pivot."""
        pivots = [m for m in marks if m.shift_type == ShiftType.BUILD_PIVOT]
        linked_ghosts = {g.decision_point_id for g in ghosts}
        return all(p.mark_id in linked_ghosts for p in pivots)
```

### 2. Add AGENTESE Node Registration

The current implementation is a standalone service. Run 002 should add:

```python
@node(
    "witness.run_lab",
    description="Run Lab - Witnessed game run with Galois drift detection",
    contracts={...}
)
class RunLabNode(BaseLogosNode):
    ...
```

### 3. Integrate with Actual Galois Distance

Currently using fallback distance. Run 002 should:
- Import `services.zero_seed.galois.distance.CanonicalSemanticDistance`
- Add async support for `BidirectionalEntailmentDistance`
- Measure latency impact and fall back if needed

## Contract Amendments Needed

### 1. Add to shared-primitives/contracts/

Move `contracts/wasm-survivors.ts` to the shared package:
- `impl/claude/shared-primitives/src/contracts/wasm-survivors.ts`
- Export from `impl/claude/shared-primitives/src/contracts/index.ts`

### 2. Add Backend API Routes

Create `impl/claude/protocols/api/run_lab.py`:
- POST `/api/witness/run/mark`
- POST `/api/witness/run/ghost`
- GET `/api/witness/run/{run_id}/trail`
- POST `/api/witness/run/crystallize`

## Pattern Recognition

### This is Run 001, so no cross-run patterns yet.

Future runs should watch for:
- Recurring latency issues with specific Galois metrics
- Ghost recording friction (too many clicks?)
- Crystal claim quality degradation with high-mark runs
- Style descriptor accuracy vs. player perception

## Success Patterns (Preserve in Future Runs)

### 1. Warmth Response Pattern

Every user-facing method returns a warmth response. This pattern works:
```python
return mark, warmth, latency
```

The triplet (result, warmth, metrics) should be standard for all witnessed operations.

### 2. Fallback Distance Pattern

The fallback pattern prevents latency spikes:
```python
try:
    return self._distance_metric.distance(a, b)
except Exception:
    return self._fallback_distance(a, b)
```

This should be standard for any metric that could incur API latency.

### 3. Compression Disclosure Pattern

Amendment G compliance is clean:
```python
def _generate_compression_disclosure(self, dropped, total):
    if dropped == 0:
        return "All moments preserved."
    # Progressive framing based on ratio
```

This should be extracted as a utility for all crystallization operations.

## Next Steps for Run 002

1. **Integrate with game**: Create test harness that simulates game events
2. **Add persistence**: Move from in-memory to SQLite/Postgres
3. **Add AGENTESE**: Register as a node for universal protocol access
4. **Performance test**: Measure actual latency under game-like load
5. **User validation**: Test QA-1 through QA-4 with real players

---

*Crystallized: 2025-12-26*
*Run 001 Learnings Complete*
