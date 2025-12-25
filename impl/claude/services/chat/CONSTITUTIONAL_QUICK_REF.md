# Constitutional Reward Quick Reference

## Quick Import

```python
from services.chat.session import ChatSession
from services.chat.reward import PrincipleScore, constitutional_reward
from services.chat.witness import ChatMark, ChatPolicyTrace
from services.chat.evidence import TurnResult
```

## Basic Usage

```python
# Create session
session = ChatSession.create()

# Add turn (automatic constitutional scoring)
session.add_turn("Hello", "Hi there! How can I help you?")

# Add turn with tools
session.add_turn(
    "Search for documentation",
    "I found 5 relevant documents.",
    tools_used=["search", "rank"]
)

# Add turn with custom result
turn_result = TurnResult(
    tools_passed=True,
    response="Here's the answer!",
    tools=[{"name": "calculator", "result": 42}]
)
session.add_turn("What is 6*7?", "Here's the answer!", turn_result=turn_result)
```

## Access Constitutional Data

```python
# Get all constitutional scores
history = session.get_constitutional_history()
for i, scores in enumerate(history):
    print(f"Turn {i}:")
    print(f"  Ethical: {scores.ethical:.2f}")
    print(f"  Joy-inducing: {scores.joy_inducing:.2f}")
    print(f"  Weighted total: {scores.weighted_total():.2f}")

# Get latest mark
latest = session.policy_trace.latest_mark
if latest:
    print(f"Latest turn: {latest.summary}")
    print(f"Constitutional scores: {latest.constitutional_scores}")

# Get specific mark
mark = session.policy_trace.get_mark(turn_number=0)
if mark:
    print(f"User: {mark.user_message}")
    print(f"Assistant: {mark.assistant_response}")
    print(f"Tools: {mark.tools_used}")
```

## Evidence Integration

```python
# Check evidence state
print(f"Confidence: {session.evidence.confidence:.2f}")
print(f"Should stop: {session.evidence.should_stop}")
print(f"Successes: {session.evidence.tools_succeeded}")
print(f"Failures: {session.evidence.tools_failed}")

# Evidence updates based on constitutional scores
# Success threshold: weighted_total >= 7.5 (~0.8 * 9.7 max score)
```

## Serialization

```python
# Save session
data = session.to_dict()
with open("session.json", "w") as f:
    json.dump(data, f)

# Restore session
with open("session.json") as f:
    data = json.load(f)
restored = ChatSession.from_dict(data)

# PolicyTrace is preserved
assert restored.policy_trace.turn_count == session.policy_trace.turn_count
```

## Constitutional Scoring Rules

### Default Scoring (All 1.0)
- Perfect turn: all principles = 1.0
- Weighted total: 8.7 (max: 9.7)

### Penalties Applied

#### Ethical (weight: 2.0)
- Unacknowledged mutations: 0.5
- Acknowledged mutations: 0.9

#### Composable (weight: 1.5)
- >5 tools used: max(0.5, 1.0 - (num_tools - 5) * 0.1)

#### Joy-inducing (weight: 1.2)
- Very short response (<20 chars): 0.5 + (length / 20) * 0.5
- Empty response: 0.3

#### Generative (weight: 1.0)
- Context utilization >90%: penalty (not yet implemented)

## PolicyTrace Features

```python
# Get all marks
marks = session.policy_trace.get_marks()
print(f"Total turns: {len(marks)}")

# Get recent marks
recent = session.policy_trace.get_recent_marks(n=5)
for mark in recent:
    print(mark.summary)

# Get mark by turn number
mark = session.policy_trace.get_mark(turn_number=2)

# Check turn count
assert session.policy_trace.turn_count == session.turn_count
```

## Testing Pattern

```python
# Test constitutional scoring
def test_short_response_penalty():
    session = ChatSession.create()
    session.add_turn("Hi", "OK")  # Very short

    mark = session.policy_trace.latest_mark
    assert mark.constitutional_scores.joy_inducing < 1.0

# Test policy trace accumulation
def test_trace_grows():
    session = ChatSession.create()
    session.add_turn("First", "Response 1")
    session.add_turn("Second", "Response 2")

    assert session.policy_trace.turn_count == 2
    marks = session.policy_trace.get_marks()
    assert marks[0].turn_number == 0
    assert marks[1].turn_number == 1
```

## Key Insights

### Constitutional Score Drives Success
- Evidence updates use **constitutional weighted total**, not `tools_passed`
- Threshold: >= 7.5 = success (0.8 of max 9.7)
- This ensures alignment with 7 principles

### Immutable PolicyTrace
- `add_mark()` returns new trace (Writer monad)
- Append-only semantics
- No mutation bugs

### Evidence Snapshot
- Each mark captures evidence state at turn time
- Enables session replay and debugging
- Shows confidence evolution

## Default Weights

```python
weights = {
    Principle.ETHICAL: 2.0,       # Safety first
    Principle.COMPOSABLE: 1.5,    # Architecture second
    Principle.JOY_INDUCING: 1.2,  # Kent's aesthetic
    Principle.TASTEFUL: 1.0,
    Principle.CURATED: 1.0,
    Principle.HETERARCHICAL: 1.0,
    Principle.GENERATIVE: 1.0,
}
```

Total weight: 9.7

## Files

- Implementation: `services/chat/session.py`
- Reward logic: `services/chat/reward.py`
- Witness structures: `services/chat/witness.py`
- Evidence model: `services/chat/evidence.py`
- Tests: `services/chat/_tests/test_session_constitutional.py`
