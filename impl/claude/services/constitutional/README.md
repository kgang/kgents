# Constitutional Reward System (Generalized)

**Stream 3 of Witness Architecture Orchestration**

## Overview

This module generalizes constitutional scoring beyond chat to all domains:
- `chat` - Conversational interactions
- `navigation` - Graph navigation (derivation, loss_gradient, sibling, direct_jump)
- `portal` - Portal expansion and exploration
- `edit` - Code/spec editing operations

## Architecture

```
services/constitutional/
├── __init__.py              # Module exports
├── reward.py                # Core implementation
└── _tests/
    └── test_reward.py       # Comprehensive domain tests
```

## The Seven Principles

All domains are scored against the Constitutional principles:

1. **TASTEFUL** - Does this serve a clear purpose?
2. **CURATED** - Is this intentional?
3. **ETHICAL** - Does this respect human agency?
4. **JOY_INDUCING** - Does this delight?
5. **COMPOSABLE** - Does this compose cleanly?
6. **HETERARCHICAL** - Can this both lead and follow?
7. **GENERATIVE** - Is this compressive?

## Usage

### Chat Domain

```python
from services.constitutional import constitutional_reward
from services.chat.evidence import TurnResult

result = TurnResult(response="Great work!", tools=[])
context = {"turn_result": result, "has_mutations": False}
score = constitutional_reward("send_message", context, "chat")
```

### Navigation Domain

```python
context = {"nav_type": "derivation"}
score = constitutional_reward("navigate", context, "navigation")
# derivation navigation → GENERATIVE = 1.0
```

### Portal Domain

```python
context = {"depth": 3, "edge_type": "evidence", "expansion_count": 2}
score = constitutional_reward("expand_portal", context, "portal")
# depth >= 2 → JOY_INDUCING = 1.0
# edge_type == "evidence" → ETHICAL = 1.0
```

### Edit Domain

```python
context = {"lines_changed": 20, "spec_aligned": True}
score = constitutional_reward("edit_file", context, "edit")
# lines_changed < 50 → TASTEFUL = 1.0
# spec_aligned → GENERATIVE = 1.0
```

## Domain-Specific Rules

### Chat Rules
- ETHICAL: Lower if mutations unacknowledged
- COMPOSABLE: Lower if >5 tools used
- JOY_INDUCING: Lower for short responses (<20 chars)

### Navigation Rules
- `derivation` → GENERATIVE = 1.0 (following proof chains)
- `loss_gradient` → ETHICAL = 1.0 (seeking truth)
- `sibling` → COMPOSABLE = 0.9 (exploring related)
- `direct_jump` → TASTEFUL = 1.0, COMPOSABLE = 0.8 (intentional but breaks flow)

### Portal Rules
- depth >= 2 → JOY_INDUCING = 1.0 (deliberate curiosity)
- edge_type == "evidence" → ETHICAL = 1.0 (seeking truth)
- expansion_count > 5 → CURATED = 0.7 (sprawl warning)

### Edit Rules
- lines_changed < 50 → TASTEFUL = 1.0 (small, focused)
- lines_changed > 200 → CURATED = 0.7 (might be doing too much)
- spec_aligned → GENERATIVE = 1.0 (aligned with design)

## Backward Compatibility

The `services.chat.reward` module now re-exports from this generalized module:

```python
# These are identical:
from services.constitutional import Principle, PrincipleScore
from services.chat.reward import Principle, PrincipleScore

# Chat-specific wrapper maintains original signature:
from services.chat.reward import constitutional_reward
score = constitutional_reward("send_message", turn_result, has_mutations=False)
```

All existing chat tests pass unchanged.

## Weighted Scoring

Default weights (from spec/protocols/chat-unified.md §1.2):
- ETHICAL: 2.0 (safety first)
- COMPOSABLE: 1.5 (architecture second)
- JOY_INDUCING: 1.2 (Kent's aesthetic)
- Others: 1.0

```python
score = constitutional_reward("action", context, domain)
total = score.weighted_total()  # Uses default weights
```

Custom weights:
```python
custom = {
    Principle.ETHICAL: 3.0,
    Principle.COMPOSABLE: 1.0,
}
total = score.weighted_total(custom)
```

## Testing

Comprehensive test suite covers:
- Domain-agnostic PrincipleScore tests
- Domain-specific scoring rules for all 4 domains
- Cross-domain integration
- Backward compatibility with chat
- All 7 principles

```bash
cd impl/claude
uv run pytest services/constitutional/_tests/test_reward.py -v
uv run pytest services/chat/_tests/test_reward.py -v  # Backward compat
```

All 39 constitutional tests pass.
All 27 chat tests pass (backward compatible).

## Philosophy

> "Every action is evaluated. Every domain is witnessed. Every score is principled."

This generalization enables constitutional scoring across the entire system:
- Chat turns are witnessed
- Navigation choices are witnessed
- Portal explorations are witnessed
- Edit operations are witnessed

The proof IS the decision. The mark IS the witness.

## Next Steps

1. Wire constitutional scoring into navigation (Stream 3)
2. Wire constitutional scoring into portal (Stream 3)
3. Wire constitutional scoring into edit (Stream 3)
4. Create unified witness dashboard showing scores across domains

See: spec/protocols/witness-primitives.md
See: services/categorical/dp_bridge.py (PolicyTrace pattern)
