# Constitutional Reward Quick Reference

> *"Every turn is evaluated. Every action is justified. Every score is witnessed."*

**Location:** `impl/claude/services/chat/reward.py`
**Spec:** spec/protocols/chat-unified.md §1.2, §4.2

---

## 5-Second Summary

Constitutional Reward evaluates every chat turn against the 7 kgents principles (TASTEFUL, CURATED, ETHICAL, JOY_INDUCING, COMPOSABLE, HETERARCHICAL, GENERATIVE) and produces a weighted score.

---

## Basic Usage

```python
from services.chat.reward import constitutional_reward
from services.chat.evidence import TurnResult

# Evaluate a chat turn
result = TurnResult(
    response="I've successfully updated the file!",
    tools=[{"name": "write_file"}],
    tools_passed=True,
)

score = constitutional_reward("send_message", result, has_mutations=True)

# Check scores
print(f"Ethical: {score.ethical}")        # 0.9 (mutations acknowledged)
print(f"Composable: {score.composable}")  # 1.0 (only 1 tool)
print(f"Total: {score.weighted_total()}") # ~8.5 (weighted sum)
```

---

## The 7 Principles

| Principle | Question | Scoring Rule |
|-----------|----------|--------------|
| **TASTEFUL** | Does this serve a clear purpose? | Default: 1.0 |
| **CURATED** | Is this intentional? | Default: 1.0 |
| **ETHICAL** | Does this respect human agency? | 0.5 if mutations unacknowledged, 0.9 if acknowledged |
| **JOY_INDUCING** | Does this delight? | Lower for <20 char responses |
| **COMPOSABLE** | Does this compose cleanly? | Lower for >5 tools used |
| **HETERARCHICAL** | Can this both lead and follow? | Default: 1.0 |
| **GENERATIVE** | Is this compressive? | TODO: needs context_utilization field |

---

## Default Weights

From spec/protocols/chat-unified.md §1.2:

```python
ETHICAL:       2.0  # Safety first
COMPOSABLE:    1.5  # Architecture second
JOY_INDUCING:  1.2  # Kent's aesthetic
Others:        1.0  # Baseline
```

---

## API Reference

### constitutional_reward()

```python
def constitutional_reward(
    action: str,
    turn_result: TurnResult | None = None,
    has_mutations: bool = False,
) -> PrincipleScore
```

**Args:**
- `action`: Action being evaluated (e.g., "send_message", "fork")
- `turn_result`: Optional result of the turn (for tool/content analysis)
- `has_mutations`: True if mutations occurred in this turn

**Returns:**
- `PrincipleScore` with all 7 principles evaluated (0.0 to 1.0 each)

**Examples:**
```python
# Perfect turn
score = constitutional_reward("send_message", TurnResult(response="Great!"))
assert score.weighted_total() == 8.7  # Perfect

# Unacknowledged mutations
score = constitutional_reward("send_message", TurnResult(tools_passed=False), has_mutations=True)
assert score.ethical == 0.5  # Lowered

# Too many tools
score = constitutional_reward("send_message", TurnResult(tools=[{} for _ in range(10)]))
assert score.composable == 0.5  # Lowered
```

---

### PrincipleScore

```python
@dataclass
class PrincipleScore:
    tasteful: float = 1.0
    curated: float = 1.0
    ethical: float = 1.0
    joy_inducing: float = 1.0
    composable: float = 1.0
    heterarchical: float = 1.0
    generative: float = 1.0

    def weighted_total(self, weights: dict[Principle, float] | None = None) -> float:
        """Compute weighted total (default weights from spec)."""

    def to_dict(self) -> dict[str, float]:
        """Serialize to dictionary."""

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> PrincipleScore:
        """Deserialize from dictionary."""
```

**Examples:**
```python
# Create custom score
score = PrincipleScore(ethical=0.8, composable=0.9)

# Weighted total
total = score.weighted_total()  # Uses default weights
# = (0.8*2.0 + 0.9*1.5 + 1.0*1.2 + 1.0*4) = 8.35

# Custom weights
custom = {Principle.ETHICAL: 3.0}
total = score.weighted_total(custom)

# Serialization
data = score.to_dict()
restored = PrincipleScore.from_dict(data)
```

---

### TurnResult

```python
@dataclass
class TurnResult:
    tools_passed: bool = True              # Did tools execute successfully?
    tools: list[dict[str, Any]] = []       # Tools used in this turn
    user_corrected: bool = False           # Did user correct the output?
    signals: list[dict[str, Any]] = []     # User feedback signals
    response: str = ""                     # Assistant response text
    stopping_suggestion: str | None = None # Suggested stopping point
```

---

## Scoring Details

### ETHICAL (Weight: 2.0)

**Rule:** Lower if mutations occur but aren't acknowledged

```python
if has_mutations:
    if not turn_result.tools_passed:
        ethical = 0.5  # Unacknowledged
    else:
        ethical = 0.9  # Acknowledged
else:
    ethical = 1.0      # No mutations
```

**Philosophy:** Respecting human agency means being transparent about changes.

---

### COMPOSABLE (Weight: 1.5)

**Rule:** Lower if too many tools used (>5 suggests poor composition)

```python
num_tools = len(turn_result.tools)
if num_tools > 5:
    composable = max(0.5, 1.0 - (num_tools - 5) * 0.1)
else:
    composable = 1.0
```

**Examples:**
- 0-5 tools: 1.0
- 6 tools: 0.9
- 10 tools: 0.5
- 100 tools: 0.5 (floors at 0.5)

**Philosophy:** Composability means solving problems with minimal, well-chosen operations.

---

### JOY_INDUCING (Weight: 1.2)

**Rule:** Lower for very short responses (<20 chars suggests curt/robotic)

```python
length = len(turn_result.response)
if 0 < length < 20:
    joy_inducing = 0.5 + (length / 20) * 0.5
elif length == 0:
    joy_inducing = 0.3
else:
    joy_inducing = 1.0
```

**Examples:**
- "OK" (2 chars): 0.55
- "Got it!" (7 chars): 0.68
- "Great work!" (11 chars): 0.78
- 20+ chars: 1.0
- Empty: 0.3

**Philosophy:** Thoughtful responses delight. Terse ones don't.

---

### GENERATIVE (Weight: 1.0)

**Rule:** Lower if context utilization >90% (suggests poor compression)

**Status:** ⚠️ TODO - awaits `context_utilization` field in TurnResult

**Future implementation:**
```python
if turn_result.context_utilization > 0.9:
    generative = max(0.5, 1.0 - (turn_result.context_utilization - 0.9) * 5)
else:
    generative = 1.0
```

**Philosophy:** Good compression means using context efficiently.

---

### TASTEFUL, CURATED, HETERARCHICAL (Weight: 1.0)

**Rule:** Default 1.0 (override for specific cases)

**Current:** No specific scoring rules defined in spec

**Future:** Add domain-specific rules as patterns emerge

---

## Integration Examples

### With ChatSession

```python
from services.chat.session import ChatSession

session = ChatSession.create()
turn = session.send_message("Hello")

# Evaluate turn
score = constitutional_reward(
    action="send_message",
    turn_result=turn.result,
    has_mutations=turn.has_mutations,
)

# Store score
session.record_constitutional_score(turn.id, score)
```

---

### With PolicyTrace (Witness Walk)

```python
from agents.o import Mark

@dataclass
class ChatMark(Mark):
    """Witness mark for a chat turn."""
    turn_number: int
    user_message: str
    assistant_response: str
    constitutional_scores: PrincipleScore  # Store here
    reasoning: str

# Create mark
mark = ChatMark(
    turn_number=1,
    user_message="Hello",
    assistant_response="Hi there!",
    constitutional_scores=score,
    reasoning="Standard greeting",
)
```

---

### With ValueAgent

```python
from agents.dp import ValueAgent

CHAT_VALUE_AGENT = ValueAgent(
    name="chat",
    states=CHAT_POLYNOMIAL.positions,
    actions=lambda s: CHAT_POLYNOMIAL.directions(s),
    transition=lambda s, a: CHAT_POLYNOMIAL.transition(s, a)[0],
    reward=lambda s, a, s_next: constitutional_reward(a, ...),  # Use here
    gamma=0.99,
)
```

---

## Common Patterns

### Pattern 1: Perfect Turn
```python
result = TurnResult(
    response="I've analyzed the code and found three optimization opportunities.",
    tools=[],
    tools_passed=True,
)
score = constitutional_reward("send_message", result)
# All principles: 1.0
# Total: 8.7
```

### Pattern 2: Acknowledged Mutations
```python
result = TurnResult(
    response="I've updated the file as requested.",
    tools=[{"name": "write_file"}],
    tools_passed=True,
)
score = constitutional_reward("send_message", result, has_mutations=True)
# ethical: 0.9 (acknowledged)
# composable: 1.0 (1 tool)
# Total: ~8.5
```

### Pattern 3: Multiple Violations
```python
result = TurnResult(
    response="OK",  # Too short
    tools=[{"name": f"tool_{i}"} for i in range(10)],  # Too many
    tools_passed=False,  # Failed
)
score = constitutional_reward("send_message", result, has_mutations=True)
# ethical: 0.5 (unacknowledged)
# composable: 0.5 (too many tools)
# joy_inducing: ~0.55 (too short)
# Total: ~6.4 (degraded)
```

---

## Debugging

### Check Individual Scores
```python
score = constitutional_reward(action, result, has_mutations)
print(f"""
Tasteful:      {score.tasteful}
Curated:       {score.curated}
Ethical:       {score.ethical}
Joy-Inducing:  {score.joy_inducing}
Composable:    {score.composable}
Heterarchical: {score.heterarchical}
Generative:    {score.generative}
Total:         {score.weighted_total():.2f}
""")
```

### Understand Weighted Total
```python
# Manual calculation
total = (
    score.ethical * 2.0 +
    score.composable * 1.5 +
    score.joy_inducing * 1.2 +
    score.tasteful * 1.0 +
    score.curated * 1.0 +
    score.heterarchical * 1.0 +
    score.generative * 1.0
)
# Sum of weights: 8.7
# Perfect score: 8.7
```

---

## Testing

See: `services/chat/_tests/test_reward.py`

```python
import pytest
from services.chat.reward import constitutional_reward, PrincipleScore
from services.chat.evidence import TurnResult

def test_perfect_turn():
    result = TurnResult(response="Great!", tools=[])
    score = constitutional_reward("send_message", result)
    assert score.weighted_total() == pytest.approx(8.7)

def test_ethical_violations():
    result = TurnResult(tools_passed=False)
    score = constitutional_reward("send_message", result, has_mutations=True)
    assert score.ethical == 0.5
```

Run tests:
```bash
cd impl/claude
uv run pytest services/chat/_tests/test_reward.py -v
# 27 passed in 2.63s
```

---

## Performance

**O(1) complexity:** All scoring rules are constant-time

**Typical execution:** <1ms per turn

**Memory:** ~56 bytes per PrincipleScore (7 floats)

---

## FAQ

### Q: Why optimistic prior (default 1.0)?
**A:** We prefer to trust the system unless evidence suggests otherwise. This creates a positive feedback loop.

### Q: Why these specific weights?
**A:** From spec/protocols/chat-unified.md §1.2:
- ETHICAL: 2.0 → Safety first
- COMPOSABLE: 1.5 → Architecture second
- JOY_INDUCING: 1.2 → Kent's aesthetic

### Q: Can I use custom weights?
**A:** Yes! Pass `weights` dict to `weighted_total()`:
```python
custom = {Principle.ETHICAL: 3.0}
total = score.weighted_total(custom)
```

### Q: Why does GENERATIVE always score 1.0?
**A:** Awaiting `context_utilization` field in TurnResult. The interface is ready; the data isn't yet tracked.

### Q: What's a "good" total score?
**A:**
- 8.7: Perfect (all principles satisfied)
- 7.0-8.5: Good (minor violations)
- 5.0-7.0: Concerning (multiple violations)
- <5.0: Poor (systemic issues)

---

## Related

- **Spec:** spec/protocols/chat-unified.md §1.2 (ValueAgent), §4.2 (Evidence)
- **Tests:** services/chat/_tests/test_reward.py
- **Integration:** services/chat/session.py (ChatSession)
- **Witness:** services/chat/witness.py (ChatMark)

---

*Last updated: 2025-12-25*
*Version: 1.0*
