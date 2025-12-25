# Constitutional Reward System - Quick Reference

> *"Every turn is evaluated. Every action is justified. Every score is witnessed."*

## Overview

The Constitutional Reward system evaluates every chat turn against the 7 Constitutional principles from the kgents Constitution.

**Location**: `services/chat/reward.py`
**Spec**: `spec/protocols/chat-unified.md` §1.2, §4.2
**Tests**: `services/chat/_tests/test_reward.py`

---

## The 7 Principles

```python
from services.chat import Principle

Principle.TASTEFUL       # Does this serve a clear purpose?
Principle.CURATED        # Is this intentional?
Principle.ETHICAL        # Does this respect human agency?
Principle.JOY_INDUCING   # Does this delight?
Principle.COMPOSABLE     # Does this compose cleanly?
Principle.HETERARCHICAL  # Can this both lead and follow?
Principle.GENERATIVE     # Is this compressive?
```

---

## Basic Usage

```python
from services.chat import constitutional_reward, TurnResult, PrincipleScore

# Evaluate a turn
turn_result = TurnResult(
    response="I've successfully updated the file!",
    tools=[{"name": "write_file", "status": "success"}],
    tools_passed=True,
)

score = constitutional_reward(
    action="send_message",
    turn_result=turn_result,
    has_mutations=True,  # File was modified
)

# Access individual principle scores
print(f"Ethical: {score.ethical}")        # 0.9 (mutations acknowledged)
print(f"Composable: {score.composable}")  # 1.0 (only 1 tool used)
print(f"Joy: {score.joy_inducing}")       # 1.0 (good response length)

# Get weighted total
total = score.weighted_total()
print(f"Total: {total:.2f}")  # e.g., 8.6/8.7 (near perfect)
```

---

## Scoring Rules

### ETHICAL (weight: 2.0)

| Condition | Score | Rationale |
|-----------|-------|-----------|
| No mutations | 1.0 | Perfect ethical behavior |
| Mutations + acknowledged | 0.9 | Mutations handled transparently |
| Mutations + unacknowledged | 0.5 | Violates ethical transparency |

```python
# Perfect ethical score
score = constitutional_reward("send_message", TurnResult(tools_passed=True))
assert score.ethical == 1.0

# Unacknowledged mutations
score = constitutional_reward(
    "send_message",
    TurnResult(tools_passed=False),
    has_mutations=True
)
assert score.ethical == 0.5
```

### COMPOSABLE (weight: 1.5)

| Tools Used | Score | Rationale |
|------------|-------|-----------|
| 0-5 tools | 1.0 | Good composition |
| 6+ tools | 1.0 - (n-5)*0.1 | Poor composition, bottoms at 0.5 |

```python
# Perfect composable score
score = constitutional_reward(
    "send_message",
    TurnResult(tools=[{"name": "read_file"}])
)
assert score.composable == 1.0

# Too many tools (10 tools = 0.5 score)
score = constitutional_reward(
    "send_message",
    TurnResult(tools=[{"name": f"tool_{i}"} for i in range(10)])
)
assert score.composable == 0.5
```

### JOY_INDUCING (weight: 1.2)

| Response Length | Score | Rationale |
|-----------------|-------|-----------|
| ≥ 20 chars | 1.0 | Thoughtful response |
| 1-19 chars | 0.5 + (len/20)*0.5 | Curt/robotic |
| 0 chars | 0.3 | Empty response |

```python
# Perfect joy score
score = constitutional_reward(
    "send_message",
    TurnResult(response="Here's a thoughtful response!")
)
assert score.joy_inducing == 1.0

# Short response (2 chars = 0.55 score)
score = constitutional_reward(
    "send_message",
    TurnResult(response="OK")
)
assert score.joy_inducing == 0.55
```

### GENERATIVE (weight: 1.0)

| Context Utilization | Score | Rationale |
|---------------------|-------|-----------|
| < 90% | 1.0 | Good compression |
| ≥ 90% | Lower | Poor compression (future) |

**Note**: Context utilization scoring is not yet implemented (TurnResult needs `context_utilization` field).

### TASTEFUL, CURATED, HETERARCHICAL (weight: 1.0 each)

Default to 1.0. Override for specific cases in production.

---

## Weighted Total

Default weights (from spec):

```python
WEIGHTS = {
    Principle.ETHICAL: 2.0,        # Safety first
    Principle.COMPOSABLE: 1.5,     # Architecture second
    Principle.JOY_INDUCING: 1.2,   # Kent's aesthetic
    Principle.TASTEFUL: 1.0,
    Principle.CURATED: 1.0,
    Principle.HETERARCHICAL: 1.0,
    Principle.GENERATIVE: 1.0,
}
# Sum of weights: 8.7
```

Perfect score: `8.7`

```python
# Default weights
score = PrincipleScore()
total = score.weighted_total()
assert total == 8.7

# Custom weights
custom = {
    Principle.ETHICAL: 3.0,
    Principle.COMPOSABLE: 2.0,
}
total = score.weighted_total(custom)
# All principles 1.0: (1.0*3.0 + 1.0*2.0 + 1.0*5) = 10.0
```

---

## Serialization

```python
# To dict
score = PrincipleScore(ethical=0.8, composable=0.9)
data = score.to_dict()
# {"tasteful": 1.0, "curated": 1.0, "ethical": 0.8, ...}

# From dict
restored = PrincipleScore.from_dict(data)
assert restored.ethical == 0.8

# Missing keys default to 1.0
partial = PrincipleScore.from_dict({"ethical": 0.5})
assert partial.ethical == 0.5
assert partial.composable == 1.0
```

---

## Integration with ChatSession

Future integration (from spec):

```python
class ChatSession:
    def send_message(self, content: str) -> ChatResponse:
        # ... execute turn ...

        # Evaluate constitutionally
        score = constitutional_reward(
            action="send_message",
            turn_result=turn_result,
            has_mutations=self._has_mutations,
        )

        # Store score in PolicyTrace
        mark = ChatMark(
            turn_number=self.turn_count,
            constitutional_scores=score,
            reasoning="...",
        )
        self.policy_trace.append(mark)

        # Use score to inform evidence
        evidence = self.evidence.update(
            turn_result=turn_result,
            constitutional_score=score,
        )

        return ChatResponse(
            content=response,
            constitutional_scores=score,
            evidence=evidence,
        )
```

---

## Testing

```bash
# Run tests
cd impl/claude
uv run pytest services/chat/_tests/test_reward.py -v

# Test coverage
uv run pytest services/chat/_tests/test_reward.py --cov=services.chat.reward
```

---

## Examples

### Example 1: Perfect Turn

```python
result = TurnResult(
    response="I've analyzed the code and found 3 potential issues.",
    tools=[{"name": "read_file"}],
    tools_passed=True,
)

score = constitutional_reward("send_message", result, has_mutations=False)

# All scores should be perfect
assert score.ethical == 1.0       # No mutations
assert score.composable == 1.0    # 1 tool used
assert score.joy_inducing == 1.0  # Good response length
assert score.weighted_total() == 8.7
```

### Example 2: Unacknowledged Mutations

```python
result = TurnResult(
    response="Done!",  # Too short + unclear
    tools=[
        {"name": "write_file"},
        {"name": "delete_file"},
    ],
    tools_passed=False,  # Tools failed but not acknowledged
)

score = constitutional_reward("send_message", result, has_mutations=True)

assert score.ethical == 0.5      # Unacknowledged mutations
assert score.joy_inducing < 1.0  # Short response
assert score.weighted_total() < 8.7
```

### Example 3: Tool Overuse

```python
result = TurnResult(
    response="I've refactored the entire codebase!",
    tools=[
        {"name": "read_file"},
        {"name": "write_file"},
        {"name": "move_file"},
        {"name": "delete_file"},
        {"name": "create_dir"},
        {"name": "write_file"},
        {"name": "write_file"},
        {"name": "write_file"},
    ],  # 8 tools
    tools_passed=True,
)

score = constitutional_reward("send_message", result, has_mutations=True)

assert score.composable == 0.7  # 8 tools: 1.0 - (8-5)*0.1 = 0.7
assert score.ethical == 0.9     # Mutations acknowledged
```

---

## Philosophy

From the spec:

> *"Every action is evaluated. Every decision is justified. Every score is witnessed."*

The Constitutional Reward system ensures:

1. **Ethical Transparency**: Mutations must be acknowledged
2. **Compositional Discipline**: Tools should compose, not accumulate
3. **Joy-Inducing Interaction**: Responses should delight, not just function
4. **Generative Compression**: Context should be managed efficiently

Each principle score is a **witness** to the turn's quality. The weighted total is a **proof** of Constitutional alignment.

---

*Last updated: 2025-12-25*
*Version: 1.0*
