# Evidence Fix: Hardcoded Values → Bayesian Computation

**Date**: 2025-12-24
**Status**: ✅ Complete

## Problem

The chat API had hardcoded evidence values that ignored actual tool execution results:

1. **Hardcoded EvidenceDelta** (`protocols/api/chat.py` lines 529-533):
   ```python
   evidence_delta = EvidenceDelta(
       tools_executed=0,      # ← Always 0!
       tools_succeeded=0,     # ← Always 0!
       confidence_change=0.1, # ← Hardcoded!
   )
   ```

2. **Evidence update ignores confidence** (lines 221-247):
   - The `_update_evidence()` function accepted a `confidence` parameter
   - Should compute it from Bayesian posterior instead

## Solution

### 1. Extract Tool Results from K-gent Response

Modified `send_message` endpoint to parse tool results from K-gent bridge:

```python
# Extract tool results from K-gent response
tools_executed = len(tools_used)
tools_succeeded = sum(1 for t in tools_used if t.get("success", False))

# Compute confidence change based on tool results
if tools_executed == 0:
    confidence_change = 0.05  # Neutral turn
else:
    # Confidence change is delta from expected 50% success rate
    actual_success_rate = tools_succeeded / tools_executed
    confidence_change = actual_success_rate - 0.5

evidence_delta = EvidenceDelta(
    tools_executed=tools_executed,
    tools_succeeded=tools_succeeded,
    confidence_change=confidence_change,
)
```

### 2. Compute Confidence from Beta Posterior

Updated `_update_evidence()` to compute confidence from Bayesian posterior:

```python
def _update_evidence(
    evidence: ChatEvidence, delta: EvidenceDelta, confidence: float
) -> ChatEvidence:
    """
    Update evidence accumulator with new delta.

    Computes confidence from Beta posterior based on tool success/failure.
    """
    tools_succeeded = evidence.tools_succeeded + delta.tools_succeeded
    tools_failed = evidence.tools_failed + (delta.tools_executed - delta.tools_succeeded)

    # Update beta distribution parameters
    # alpha = successes + 1, beta = failures + 1 (uniform prior)
    prior_alpha = tools_succeeded + 1.0
    prior_beta = tools_failed + 1.0

    # Compute confidence from Beta posterior (mean)
    posterior_mean = prior_alpha / (prior_alpha + prior_beta)

    return ChatEvidence(
        prior_alpha=prior_alpha,
        prior_beta=prior_beta,
        confidence=posterior_mean,  # Computed from posterior, not passed through
        should_stop=posterior_mean > 0.95,  # High confidence threshold
        tools_succeeded=tools_succeeded,
        tools_failed=tools_failed,
    )
```

### 3. Populate ToolUse Objects

Modified turn construction to create ToolUse objects from K-gent response:

```python
turn = Turn(
    turn_number=turn_number,
    user_message=user_message,
    assistant_response=assistant_message,
    tools_used=[
        ToolUse(
            name=t.get("name", "unknown"),
            input=t.get("input", {}),
            output=t.get("output"),
            success=t.get("success", False),
            duration_ms=t.get("duration_ms", 0.0),
        )
        for t in tools_used
    ],
    evidence_delta=evidence_delta,
    confidence=turn_confidence,
    started_at=started_at,
    completed_at=completed_at,
)
```

## Files Modified

1. **`protocols/api/chat.py`**:
   - Lines 221-247: Updated `_update_evidence()` to compute confidence from posterior
   - Lines 515-604: Updated `send_message()` to extract tool results and compute evidence
   - Line 554: Fixed type annotation for `tools_used`
   - Line 81: Added return type annotation

## Tests Added

Created `protocols/api/_tests/test_chat_evidence.py` with comprehensive tests:

- `test_evidence_update_no_tools`: Verify neutral turn handling
- `test_evidence_update_all_success`: All tools succeed → confidence increases
- `test_evidence_update_mixed_results`: Mixed results → confidence remains moderate
- `test_evidence_update_all_failure`: All tools fail → confidence decreases
- `test_evidence_accumulation`: Evidence accumulates across turns
- `test_evidence_should_stop_threshold`: Stopping threshold at 0.95 confidence

**Test Results**: ✅ 17 passed, 2 skipped

## Integration Points

### Current State

- K-gent bridge returns `tools_used` in turn_data (currently empty list)
- Chat API extracts tool info and computes evidence
- Confidence is Bayesian posterior mean: `alpha / (alpha + beta)`

### Future Work (TODO)

```python
# TODO: Integrate ASHC evidence accumulation for spec edits
# See: services.chat.ashc_bridge.ASHCBridge for spec compilation evidence
```

When a spec file is edited:
1. Detect spec edit in K-gent response
2. Call `ASHCBridge.compile_spec()` for evidence
3. Integrate ASHC equivalence score into ChatEvidence
4. Display verification status in UI

## Evidence Model

### Beta Distribution
- **Prior**: `Beta(1, 1)` = uniform (no initial bias)
- **Update**: Add successes to alpha, failures to beta
- **Posterior Mean**: `alpha / (alpha + beta)` = confidence

### Example Trajectory

| Turn | Tools | Success | Fail | Alpha | Beta | Confidence |
|------|-------|---------|------|-------|------|------------|
| 0    | 0     | 0       | 0    | 1.0   | 1.0  | 0.50       |
| 1    | 3     | 3       | 0    | 4.0   | 1.0  | 0.80       |
| 2    | 2     | 1       | 1    | 5.0   | 2.0  | 0.71       |
| 3    | 4     | 4       | 0    | 9.0   | 2.0  | 0.82       |
| 4    | 1     | 0       | 1    | 9.0   | 3.0  | 0.75       |

**Stopping Criterion**: `confidence > 0.95` (high confidence threshold)

## Philosophy

> **"Evidence accumulates. Confidence emerges. Stopping is principled."**

- Every tool execution provides evidence
- Bayesian updates accumulate across turns
- Confidence is probabilistic, not arbitrary
- Stopping is data-driven, not heuristic

## References

- `spec/protocols/chat-web.md` §2.4, §3.3 - Chat evidence model
- `spec/protocols/ASHC-agentic-self-hosting-compiler.md` - Bayesian evidence accumulation
- `services/chat/evidence.py` - Evidence primitives (BetaPrior, ChatEvidence)
- `services/chat/ashc_bridge.py` - ASHC integration for spec edits
