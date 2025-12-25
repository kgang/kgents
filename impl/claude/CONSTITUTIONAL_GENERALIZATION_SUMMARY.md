# Constitutional Scoring Generalization - Stream 3 Complete

**Date**: 2025-12-25
**Stream**: Witness Architecture Orchestration - Stream 3
**Objective**: Extend constitutional scoring beyond chat to all domains

## What Was Built

### New Services Module: `services/constitutional/`

Created a generalized constitutional reward system that works across all domains:

```
services/constitutional/
├── __init__.py              # Module exports
├── reward.py                # Core implementation (430 lines)
├── README.md                # Full documentation
├── QUICK_REF.md             # One-page developer reference
└── _tests/
    ├── __init__.py
    └── test_reward.py       # Comprehensive tests (450+ lines)
```

### Key Components

1. **Domain Enum** - Four domains: chat, navigation, portal, edit
2. **Principle Enum** - Seven constitutional principles
3. **PrincipleScore** - Dataclass with scoring and serialization
4. **constitutional_reward()** - Main scoring function with domain dispatch
5. **Domain-specific rules** - Four rule functions (_apply_chat_rules, etc.)

### Domain-Specific Scoring Rules

#### Chat Rules
- ETHICAL: Lower if mutations unacknowledged
- COMPOSABLE: Lower if >5 tools used
- JOY_INDUCING: Lower for short responses (<20 chars)

#### Navigation Rules
- derivation → GENERATIVE = 1.0 (following proof chains)
- loss_gradient → ETHICAL = 1.0 (seeking truth)
- sibling → COMPOSABLE = 0.9 (exploring related)
- direct_jump → TASTEFUL = 1.0, COMPOSABLE = 0.8 (intentional but breaks flow)

#### Portal Rules
- depth >= 2 → JOY_INDUCING = 1.0 (deliberate curiosity)
- edge_type == "evidence" → ETHICAL = 1.0 (seeking truth)
- expansion_count > 5 → CURATED = 0.7 (sprawl warning)

#### Edit Rules
- lines_changed < 50 → TASTEFUL = 1.0 (small, focused)
- lines_changed > 200 → CURATED = 0.7 (might be doing too much)
- spec_aligned → GENERATIVE = 1.0 (aligned with design)

## Migration Strategy

### Backward Compatibility

The existing `services.chat.reward` module now re-exports from the generalized module:

```python
# services/chat/reward.py (updated)
from services.constitutional import Principle, PrincipleScore
from services.constitutional import constitutional_reward as _constitutional_reward

def constitutional_reward(action, turn_result=None, has_mutations=False):
    """Chat-specific wrapper maintaining original signature."""
    context = {"turn_result": turn_result, "has_mutations": has_mutations}
    return _constitutional_reward(action, context, domain="chat")
```

**Result**: All existing chat tests pass unchanged (27/27).

### New Usage Pattern

```python
# All domains use the same pattern:
from services.constitutional import constitutional_reward

# Chat
score = constitutional_reward("send_message", context, "chat")

# Navigation
score = constitutional_reward("navigate", context, "navigation")

# Portal
score = constitutional_reward("expand_portal", context, "portal")

# Edit
score = constitutional_reward("edit_file", context, "edit")
```

## Testing Results

### Test Coverage

```
services/constitutional/_tests/test_reward.py:
  ✓ PrincipleScore tests (6 tests)
  ✓ Domain enum tests (2 tests)
  ✓ Chat domain tests (6 tests)
  ✓ Navigation domain tests (5 tests)
  ✓ Portal domain tests (6 tests)
  ✓ Edit domain tests (6 tests)
  ✓ Cross-domain integration tests (3 tests)
  ✓ Backward compatibility tests (3 tests)
  ✓ Principle enum tests (2 tests)

  Total: 39 tests

services/chat/_tests/test_reward.py:
  ✓ All existing tests pass (27 tests)

Grand Total: 66 tests, all passing
```

### Type Safety

```bash
$ uv run mypy services/constitutional/
Success: no issues found in 4 source files
```

### Import Verification

```bash
$ uv run python -c "from services.constitutional import ..."
✓ All imports work correctly
✓ Chat module re-exports from constitutional module
✓ Backward compatibility confirmed
```

## Files Created

1. `/Users/kentgang/git/kgents/impl/claude/services/constitutional/__init__.py`
2. `/Users/kentgang/git/kgents/impl/claude/services/constitutional/reward.py`
3. `/Users/kentgang/git/kgents/impl/claude/services/constitutional/README.md`
4. `/Users/kentgang/git/kgents/impl/claude/services/constitutional/QUICK_REF.md`
5. `/Users/kentgang/git/kgents/impl/claude/services/constitutional/_tests/__init__.py`
6. `/Users/kentgang/git/kgents/impl/claude/services/constitutional/_tests/test_reward.py`

## Files Modified

1. `/Users/kentgang/git/kgents/impl/claude/services/chat/reward.py` - Now a thin wrapper

## Architecture Impact

### Before
```
services/chat/reward.py
  ├── Principle (enum)
  ├── PrincipleScore (dataclass)
  └── constitutional_reward() - chat only
```

### After
```
services/constitutional/reward.py
  ├── Domain (enum) - NEW
  ├── Principle (enum)
  ├── PrincipleScore (dataclass)
  ├── constitutional_reward() - all domains
  ├── _apply_chat_rules()
  ├── _apply_navigation_rules() - NEW
  ├── _apply_portal_rules() - NEW
  └── _apply_edit_rules() - NEW

services/chat/reward.py
  └── constitutional_reward() - wrapper for backward compat
```

## Philosophy

> "Every action is evaluated. Every domain is witnessed. Every score is principled."

This generalization enables constitutional scoring across the entire system:
- Chat turns are witnessed
- Navigation choices are witnessed
- Portal explorations are witnessed
- Edit operations are witnessed

The proof IS the decision. The mark IS the witness.

## Next Steps (Stream 3 Continuation)

1. **Wire constitutional scoring into navigation**
   - Update navigation code to call constitutional_reward()
   - Pass nav_type context
   - Store scores in navigation marks

2. **Wire constitutional scoring into portal**
   - Update portal expansion to call constitutional_reward()
   - Pass depth, edge_type, expansion_count context
   - Store scores in portal marks

3. **Wire constitutional scoring into edit**
   - Update edit operations to call constitutional_reward()
   - Pass lines_changed, spec_aligned context
   - Store scores in edit marks

4. **Create unified witness dashboard**
   - Show constitutional scores across all domains
   - Aggregate by principle (e.g., "How ethical are my actions?")
   - Time-series view of principle adherence

## Success Criteria

✓ All domains use same PrincipleScore type
✓ Domain-specific rules apply correctly
✓ Chat tests still pass (backward compatible)
✓ New tests for navigation/portal/edit pass
✓ Type checking passes
✓ Documentation complete

## References

- `services/constitutional/README.md` - Full documentation
- `services/constitutional/QUICK_REF.md` - Quick reference
- `spec/principles/CONSTITUTION.md` - Constitutional principles
- `spec/protocols/witness-primitives.md` - Witness architecture
- `services/categorical/dp_bridge.py` - PolicyTrace pattern

---

**Status**: COMPLETE
**Tests**: 66/66 passing
**Type Safety**: ✓
**Backward Compatibility**: ✓
**Documentation**: ✓
