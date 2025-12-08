# Bootstrap Regeneration Validation Guide

**Phase 6 (Optional): Validate that BOOTSTRAP_PROMPT.md is sufficient to regenerate the bootstrap system**

## Overview

This guide provides a practical approach to validating that the bootstrap documentation (`BOOTSTRAP_PROMPT.md` and `AUTONOMOUS_BOOTSTRAP_PROTOCOL.md`) contains sufficient information to regenerate the 7 bootstrap agents with behavior equivalence.

## Test Strategy

Rather than full deletion and regeneration (which is high-risk), we use a **behavior snapshot approach**:

1. **Capture Reference Behavior**: Run test cases against current implementation and save outputs
2. **Regenerate (Optional)**: Follow docs to regenerate one agent at a time
3. **Validate**: Run same tests against regenerated agent and compare outputs
4. **Report**: Document differences and assess equivalence

## Quick Start

### Step 1: Capture Reference Behavior

```bash
cd /Users/kentgang/git/kgents/impl/claude
/Users/kentgang/git/kgents/.venv/bin/python -c "
import asyncio
import json
from pathlib import Path

# Test each bootstrap agent
async def test_agents():
    from bootstrap import Id, Ground, Judge, JudgeInput, make_default_principles

    results = {}

    # Test Id
    id_agent = Id[str]()
    results['id'] = {
        'test': 'identity',
        'input': 'test_value',
        'output': await id_agent.invoke('test_value')
    }

    # Test Ground
    ground = Ground()
    ground_result = await ground.invoke(None)
    results['ground'] = {
        'test': 'ground',
        'has_facts': hasattr(ground_result, 'persona') and hasattr(ground_result, 'world')
    }

    # Test Judge
    judge = Judge()
    verdict = await judge.invoke(JudgeInput(agent=id_agent, principles=make_default_principles()))
    results['judge'] = {
        'test': 'judge_id',
        'verdict_type': verdict.type.value if hasattr(verdict, 'type') else str(type(verdict))
    }

    # Save results
    Path('bootstrap_reference').mkdir(exist_ok=True)
    Path('bootstrap_reference/behavior_snapshot.json').write_text(json.dumps(results, indent=2, default=str))
    print('✓ Reference behavior captured')
    print(json.dumps(results, indent=2, default=str))

asyncio.run(test_agents())
"
```

### Step 2: Manual Test Cases

For each bootstrap agent, verify these behaviors:

#### Id Agent
```python
from bootstrap import Id

# Test 1: Identity law
id_agent = Id[str]()
result = await id_agent.invoke("test")
assert result == "test", "Id must return input unchanged"
assert result is "test", "Id must return the same object (identity)"

# Test 2: Composition laws
from bootstrap import compose
composed = id_agent >> id_agent
result2 = await composed.invoke("test")
assert result2 == "test", "Id >> Id must be identity"
```

#### Ground Agent
```python
from bootstrap import Ground

# Test 1: Returns Facts
ground = Ground()
facts = await ground.invoke(None)
assert hasattr(facts, 'persona'), "Ground must return Facts with persona"
assert hasattr(facts, 'world'), "Ground must return Facts with world"
assert facts.persona is not None, "Persona must be grounded"
```

#### Judge Agent
```python
from bootstrap import Judge, JudgeInput, make_default_principles, Id

# Test 1: Evaluates agents
judge = Judge()
verdict = await judge.invoke(JudgeInput(
    agent=Id[str](),
    principles=make_default_principles()
))
assert hasattr(verdict, 'type'), "Judge must return Verdict"
assert verdict.type.value in ['accept', 'reject', 'revise'], "Verdict must have valid type"
```

#### Compose Agent
```python
from bootstrap import Id, compose

# Test 1: Composes agents
id1 = Id[str]()
id2 = Id[str]()
composed = compose(id1, id2)
result = await composed.invoke("test")
assert result == "test", "Composed Ids must be identity"

# Test 2: Associativity
id3 = Id[str]()
left_assoc = compose(compose(id1, id2), id3)
right_assoc = compose(id1, compose(id2, id3))
# Both should produce equivalent behavior
```

#### Contradict Agent
```python
from bootstrap import Contradict, ContradictInput

# Test 1: Detects no tension in identical values
contradict = Contradict()
result = await contradict.invoke(ContradictInput(a="test", b="test"))
assert result.tension is None or result.tension == None, "Identical values should not conflict"

# Test 2: May detect tension in different values
result2 = await contradict.invoke(ContradictInput(a="test1", b="test2"))
# Result depends on detection logic - just verify it returns something
assert result2 is not None, "Contradict must return ContradictResult"
```

#### Sublate Agent
```python
from bootstrap import Sublate, Tension, TensionMode

# Test 1: Resolves or holds tension
sublate = Sublate()
# Create a test tension
tension = Tension(
    thesis="approach A",
    antithesis="approach B",
    mode=TensionMode.PRAGMATIC,
    severity=0.7,
    description="Test tension"
)
result = await sublate.invoke([tension])
assert hasattr(result, 'resolution_type'), "Sublate must return Synthesis"
```

#### Fix Agent
```python
from bootstrap import Fix

# Test 1: Finds fixed point
async def increment_until_10(x: int) -> int:
    if x >= 10:
        return x
    return x + 1

fix = Fix[int]()
result = await fix.invoke((increment_until_10, 5))
assert result.value == 10, "Fix should find stable point"
assert result.converged, "Fix should converge"
assert result.iterations > 0, "Fix should track iterations"
```

## Success Criteria

The regenerated bootstrap system is considered **behaviorally equivalent** if:

### Required (Must Pass)
- ✓ All identity laws hold (Id works correctly)
- ✓ Composition is associative
- ✓ Ground returns Facts with persona and world
- ✓ Judge returns Verdict with valid type
- ✓ Fix converges for convergent functions
- ✓ No runtime errors for valid inputs

### Acceptable Differences (OK to differ)
- Variable names
- Code formatting
- Comments and docstrings (style)
- Internal implementation details
- Performance characteristics (within reason)

### Unacceptable Differences (Must match)
- Type signatures (Agent[A,B] must match spec)
- Behavior for standard inputs
- Error handling for invalid inputs
- Composition laws
- Return value types

## Regeneration Process (If Desired)

To actually regenerate an agent:

1. **Backup original**:
   ```bash
   cp bootstrap/id.py bootstrap/id.py.backup
   ```

2. **Read documentation**:
   - `spec/bootstrap.md` - Agent specification
   - `docs/BOOTSTRAP_PROMPT.md` - Implementation guide
   - Look at dependency graph

3. **Regenerate from spec**:
   - Follow BOOTSTRAP_PROMPT.md step-by-step
   - Use the spec as ground truth
   - Don't look at original implementation

4. **Test**:
   ```bash
   # Run manual tests from Step 2 above
   # Compare with reference behavior from Step 1
   ```

5. **Compare**:
   ```python
   # Load reference
   import json
   ref = json.loads(Path('bootstrap_reference/behavior_snapshot.json').read_text())

   # Test regenerated
   # ... run same tests ...

   # Compare outputs
   ```

## Current Status

As of Dec 8, 2025:
- ✓ Test harness created (`test_regeneration.py`)
- ✓ Manual test cases documented (this file)
- ✓ Basic reference behavior capturable
- ⚠️ Full regeneration not attempted (optional)

## Recommendations

For validating documentation sufficiency:

1. **Incremental approach**: Test one agent at a time
2. **Start with simplest**: Id, then Ground, then more complex
3. **Use manual tests**: More reliable than full automation
4. **Focus on behavior**: Not line-by-line code matching
5. **Document learnings**: If docs are unclear, improve them

## Notes

- Pickle serialization issues with lambdas prevented full automation
- Manual testing is more appropriate for this validation
- The test strategy focuses on **behavior equivalence** not **implementation equivalence**
- This is consistent with the kgents philosophy: "Regenerable from spec"

---

**See also:**
- `docs/BOOTSTRAP_PROMPT.md` - Full implementation guide
- `AUTONOMOUS_BOOTSTRAP_PROTOCOL.md` - Meta-level protocol
- `spec/bootstrap.md` - Agent specifications
