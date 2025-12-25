# Constitutional Reward Quick Reference

**One-page guide to constitutional scoring across all domains**

## Import

```python
from services.constitutional import (
    Domain,              # Enum: CHAT, NAVIGATION, PORTAL, EDIT
    Principle,           # Enum: 7 constitutional principles
    PrincipleScore,      # Dataclass with scores 0.0-1.0
    constitutional_reward,  # Main scoring function
)
```

## Basic Usage

```python
score = constitutional_reward(
    action="action_name",           # String describing the action
    context={"key": "value", ...},  # Domain-specific context dict
    domain="chat",                  # One of: chat, navigation, portal, edit
)

# Access individual scores
score.ethical         # 0.0 to 1.0
score.composable      # 0.0 to 1.0
score.joy_inducing    # 0.0 to 1.0

# Compute weighted total
total = score.weighted_total()  # Uses default weights

# Serialize
data = score.to_dict()  # {"tasteful": 1.0, "curated": 1.0, ...}
```

## Context Keys by Domain

### Chat
```python
context = {
    "turn_result": TurnResult(...),  # From services.chat.evidence
    "has_mutations": bool,           # Did this turn mutate state?
}
```

### Navigation
```python
context = {
    "nav_type": str,  # One of: derivation, loss_gradient, sibling, direct_jump
}
```

### Portal
```python
context = {
    "depth": int,             # Expansion depth (0+)
    "edge_type": str,         # Edge type (e.g., "evidence")
    "expansion_count": int,   # Total expansions so far
}
```

### Edit
```python
context = {
    "lines_changed": int,    # Number of lines modified
    "spec_aligned": bool,    # Is change aligned with spec?
}
```

## Scoring Rules Cheat Sheet

| Domain | Context | Principle | Score | Reason |
|--------|---------|-----------|-------|--------|
| **chat** | mutations unacknowledged | ETHICAL | 0.5 | Safety violation |
| **chat** | tools > 5 | COMPOSABLE | 0.5-1.0 | Poor composition |
| **chat** | response < 20 chars | JOY_INDUCING | 0.5-1.0 | Too terse |
| **navigation** | nav_type=derivation | GENERATIVE | 1.0 | Following proof |
| **navigation** | nav_type=loss_gradient | ETHICAL | 1.0 | Seeking truth |
| **navigation** | nav_type=sibling | COMPOSABLE | 0.9 | Exploration |
| **navigation** | nav_type=direct_jump | COMPOSABLE | 0.8 | Breaks flow |
| **portal** | depth >= 2 | JOY_INDUCING | 1.0 | Curiosity |
| **portal** | edge_type=evidence | ETHICAL | 1.0 | Truth-seeking |
| **portal** | expansion_count > 5 | CURATED | 0.7 | Sprawl warning |
| **edit** | lines_changed < 50 | TASTEFUL | 1.0 | Small, focused |
| **edit** | lines_changed > 200 | CURATED | 0.7 | Too much |
| **edit** | spec_aligned=True | GENERATIVE | 1.0 | Aligned design |

## Default Weights

```python
ETHICAL: 2.0        # Safety first
COMPOSABLE: 1.5     # Architecture second
JOY_INDUCING: 1.2   # Kent's aesthetic
Others: 1.0         # Equal weight
```

Total weight sum: 8.7

## Examples

### Chat with Mutations
```python
result = TurnResult(response="Done!", tools_passed=True)
context = {"turn_result": result, "has_mutations": True}
score = constitutional_reward("send_message", context, "chat")
# score.ethical == 0.9 (acknowledged mutations)
```

### Navigation by Derivation
```python
context = {"nav_type": "derivation"}
score = constitutional_reward("navigate", context, "navigation")
# score.generative == 1.0 (following proof chain)
```

### Portal Deep Dive
```python
context = {"depth": 4, "edge_type": "evidence", "expansion_count": 3}
score = constitutional_reward("expand", context, "portal")
# score.joy_inducing == 1.0 (deep expansion)
# score.ethical == 1.0 (evidence edge)
```

### Large Edit
```python
context = {"lines_changed": 250, "spec_aligned": False}
score = constitutional_reward("edit_file", context, "edit")
# score.curated == 0.7 (large change warning)
```

## Backward Compatibility (Chat)

```python
# Old way (still works):
from services.chat.reward import constitutional_reward
score = constitutional_reward("action", turn_result, has_mutations=False)

# New way (equivalent):
from services.constitutional import constitutional_reward
context = {"turn_result": turn_result, "has_mutations": False}
score = constitutional_reward("action", context, "chat")
```

## Testing

```bash
# Test all domains
uv run pytest services/constitutional/_tests/test_reward.py -v

# Test backward compatibility
uv run pytest services/chat/_tests/test_reward.py -v
```

## Common Patterns

### Creating Custom Weights
```python
custom_weights = {
    Principle.ETHICAL: 3.0,      # Triple weight on ethics
    Principle.COMPOSABLE: 1.0,   # Normal weight
}
total = score.weighted_total(custom_weights)
```

### Checking Violations
```python
score = constitutional_reward(action, context, domain)
if score.ethical < 0.8:
    logger.warning("Ethical violation detected")
if score.weighted_total() < 7.0:
    logger.warning("Low overall constitutional score")
```

### Serializing for Witness Trail
```python
score = constitutional_reward(action, context, domain)
mark = {
    "action": action,
    "domain": domain,
    "constitutional_scores": score.to_dict(),
    "weighted_total": score.weighted_total(),
}
```

## Philosophy

> "Every action is evaluated. Every domain is witnessed. Every score is principled."

- Optimistic prior: Default score is 1.0 (perfect)
- Lower scores only for specific violations
- Domain-specific rules capture domain semantics
- Backward compatible with existing chat implementation

## See Also

- `services/constitutional/README.md` - Full documentation
- `services/constitutional/reward.py` - Implementation
- `spec/principles/CONSTITUTION.md` - Constitutional principles
- `spec/protocols/witness-primitives.md` - Witness architecture
