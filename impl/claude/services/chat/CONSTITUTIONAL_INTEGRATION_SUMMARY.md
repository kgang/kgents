# Constitutional Reward Integration Summary

**Date**: 2025-12-25
**Status**: ✅ Complete

## Overview

Integrated Constitutional Reward and PolicyTrace into ChatSession. Every turn now:
1. Computes constitutional reward scores
2. Creates a ChatMark witness
3. Updates the ChatPolicyTrace
4. Links evidence updates to constitutional scores

## Changes Made

### 1. Updated `session.py`

**Imports Added**:
```python
from .evidence import TurnResult
from .reward import PrincipleScore, constitutional_reward
from .witness import ChatMark, ChatPolicyTrace
```

**New Field**:
```python
@dataclass
class ChatSession:
    # ... existing fields
    policy_trace: ChatPolicyTrace = field(
        default_factory=lambda: ChatPolicyTrace(session_id="")
    )
```

**Enhanced `add_turn` Method**:
- Now accepts optional `tools_used` and `turn_result` parameters
- Computes `constitutional_reward()` for every turn
- Creates a `ChatMark` with:
  - User message and assistant response
  - Tools used
  - Constitutional scores
  - Evidence snapshot
- Adds mark to policy_trace (immutable append)
- Updates evidence based on constitutional weighted total
  - Success threshold: weighted_total >= 7.5 (~0.8 * 9.7 max score)

**New Method**:
```python
def get_constitutional_history(self) -> list[PrincipleScore]:
    """Get constitutional scores for all turns."""
```

**Serialization**:
- `to_dict()`: Includes `policy_trace.to_dict()`
- `from_dict()`: Restores `ChatPolicyTrace` from dict
- `create()`: Initializes policy_trace with correct session_id

### 2. Created `test_session_constitutional.py`

**Test Coverage** (15 tests, all passing):

#### Basic Integration
- ✅ `test_add_turn_creates_chat_mark`: Verifies ChatMark creation
- ✅ `test_add_turn_computes_constitutional_reward`: Verifies score computation
- ✅ `test_policy_trace_grows_with_turns`: Verifies trace accumulation
- ✅ `test_constitutional_scores_affect_evidence`: Verifies evidence update

#### Constitutional Scoring
- ✅ `test_very_short_response_lowers_joy`: Joy penalty for short responses
- ✅ `test_many_tools_lower_composable`: Composable penalty for >5 tools

#### PolicyTrace Features
- ✅ `test_get_constitutional_history`: History retrieval works
- ✅ `test_evidence_snapshot_in_mark`: Evidence captured in marks
- ✅ `test_tools_used_recorded_in_mark`: Tools tracked in marks
- ✅ `test_session_id_matches_trace_id`: IDs match
- ✅ `test_empty_session_has_empty_trace`: Initial state correct

#### Serialization
- ✅ `test_serialization_includes_policy_trace`: Round-trip works

#### Evidence Integration
- ✅ `test_constitutional_score_determines_evidence_success`: Constitutional score drives success
- ✅ `test_weighted_total_used_for_success_threshold`: Threshold applied correctly
- ✅ `test_multiple_turns_accumulate_evidence`: Evidence accumulates

## Design Decisions

### Constitutional Score → Evidence Success

The implementation uses **constitutional weighted total** (not `tools_passed`) to determine success:

```python
total_score = constitutional_scores.weighted_total()
success = total_score >= 7.5  # ~0.8 * 9.7 (max weighted score)
```

**Rationale**: Constitutional principles are the ground truth for success. A turn might have `tools_passed=True` but fail constitutional checks (e.g., very short response, too many tools, unacknowledged mutations).

### Immutable PolicyTrace

PolicyTrace uses the Writer monad pattern:
```python
self.policy_trace = self.policy_trace.add_mark(mark)
```

Each `add_mark()` returns a **new** ChatPolicyTrace with the mark appended. This ensures:
- Append-only semantics
- No mutation bugs
- Easy serialization

### Evidence Snapshot in ChatMark

Each ChatMark includes `evidence_snapshot: dict[str, Any]` capturing the evidence state at turn time. This enables:
- Replay: reconstruct conversation state at any turn
- Analysis: see how confidence evolved
- Debugging: trace evidence updates

## Integration Points

### Existing Files Used

1. **`reward.py`**:
   - `constitutional_reward(action, turn_result, has_mutations) -> PrincipleScore`
   - Computes 7-principle scores

2. **`witness.py`**:
   - `ChatMark`: Witness for a single turn
   - `ChatPolicyTrace`: Append-only trace of all marks

3. **`evidence.py`**:
   - `TurnResult`: Turn execution result
   - `ChatEvidence`: Bayesian evidence state

### Future Integration

When LLM integration is added:
1. Capture `reasoning` from LLM response → ChatMark.reasoning
2. Detect mutations from tool execution → `has_mutations` parameter
3. Track context utilization → reduce `generative` score if >90%

## Test Results

```bash
cd impl/claude
uv run pytest services/chat/_tests/ -v

# Result: 101 passed, 2 skipped, 13 warnings in 2.71s
```

All tests pass, including:
- 15 new constitutional integration tests
- 86 existing chat tests (no regressions)

## Example Usage

```python
from services.chat.session import ChatSession

# Create session
session = ChatSession.create()

# Add turns
session.add_turn("Hello", "Hi there! How can I help?")
session.add_turn("What is 2+2?", "The answer is 4.")

# Get constitutional history
history = session.get_constitutional_history()
for i, scores in enumerate(history):
    print(f"Turn {i}: ethical={scores.ethical:.2f}, joy={scores.joy_inducing:.2f}")

# Check evidence
print(f"Confidence: {session.evidence.confidence:.2f}")
print(f"Succeeded: {session.evidence.tools_succeeded}")

# Serialize
data = session.to_dict()
restored = ChatSession.from_dict(data)
assert restored.policy_trace.turn_count == session.policy_trace.turn_count
```

## Files Modified

1. `/Users/kentgang/git/kgents/impl/claude/services/chat/session.py`
   - Added policy_trace field
   - Enhanced add_turn with constitutional scoring
   - Added get_constitutional_history method
   - Updated serialization

2. `/Users/kentgang/git/kgents/impl/claude/services/chat/_tests/test_session_constitutional.py` (new)
   - 15 comprehensive tests

## Next Steps

1. **LLM Integration**: Capture reasoning and mutations from real LLM responses
2. **Context Utilization**: Add context_utilization to TurnResult for generative score
3. **UI Display**: Show constitutional scores in ChatPanel
4. **Analytics**: Dashboard showing constitutional score trends over session
5. **Persistence**: Store ChatPolicyTrace in D-gent for session replay

---

**Summary**: ChatSession now computes constitutional reward on every turn, creates witnessed ChatMarks, and maintains a complete PolicyTrace. Evidence updates are driven by constitutional scores, ensuring every turn is evaluated against the 7 principles.
