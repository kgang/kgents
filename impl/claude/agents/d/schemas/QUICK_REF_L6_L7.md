# L6-L7 Schemas Quick Reference

**Files**: `reflection.py`, `invocation.py`
**Tests**: `_tests/test_reflection.py`, `_tests/test_invocation.py`
**Created**: 2025-12-25

## At a Glance

| Schema | Layer | Purpose | Key Fields |
|--------|-------|---------|-----------|
| **ReflectionCrystal** | L6 | "What did we learn?" | `target_ids`, `reflection_type`, `insight`, `recommendations` |
| **InterpretationCrystal** | L7 | "What patterns over time?" | `artifact_pattern`, `time_range`, `insight_type`, `confidence` |
| **LLMInvocationMark** | - | "The trace IS the causality" | `causal_parent_id`, `state_changes`, `galois_loss`, `ripple_magnitude` |

## ReflectionCrystal (L6)

```python
ReflectionCrystal(
    id="refl_001",
    target_ids=("artifact1", "artifact2"),      # What we're reflecting on
    reflection_type="synthesis",                # synthesis/comparison/delta/audit
    insight="Core learning",                    # What we learned
    recommendations=("action1", "action2"),     # What to do next
    derived_from=("parent1",),                  # Lineage
    proof=GaloisWitnessedProof(...),           # Self-justification
)
```

**Types**: `synthesis`, `comparison`, `delta`, `audit`

## InterpretationCrystal (L7)

```python
InterpretationCrystal(
    id="interp_001",
    artifact_pattern="impl/**/*.py",            # Glob pattern
    time_range=(start_time, end_time),          # Time window
    insight_type="trend",                       # trend/pattern/prediction
    content="Narrative of the interpretation",  # The story
    confidence=0.85,                            # [0, 1]
    supporting_ids=("s1", "s2"),               # Evidence
    proof=GaloisWitnessedProof(...),           # Self-justification
)
```

**Types**: `trend`, `pattern`, `prediction`

## LLMInvocationMark

```python
LLMInvocationMark(
    id="inv_001",
    action="Generate analysis",
    reasoning="User requested",

    # LLM metrics
    model="claude-opus-4-5",
    prompt_tokens=2000,
    completion_tokens=1000,
    latency_ms=3500,
    temperature=0.7,

    # Content
    system_prompt_hash="sha256...",
    user_prompt="Full prompt",
    response="Full response",

    # Causality (THE KEY)
    causal_parent_id="inv_000",                 # Parent invocation (None if root)
    triggered_by="cascade",                     # user_input/agent_decision/scheduled/cascade

    # Ripple effects
    state_changes=(StateChange(...), ...),
    crystals_created=("c1", "c2"),
    crystals_modified=("c3",),

    # Quality
    galois_loss=0.05,                           # [0, 1]

    invocation_type="analysis",                 # generation/analysis/classification/embedding
    tags=frozenset(["tag1"]),
)
```

## Computed Properties

```python
mark.coherence           # 1 - galois_loss
mark.total_tokens        # prompt + completion
mark.tokens_per_second   # completion / (latency_ms / 1000)
mark.is_cascade          # causal_parent_id is not None
mark.is_root             # causal_parent_id is None
mark.ripple_magnitude    # len(changes) + len(created) + len(modified)
```

## StateChange

```python
StateChange(
    entity_type="crystal",                      # crystal/kblock/edge/mark
    entity_id="c123",
    change_type="created",                      # created/updated/deleted/linked
    before_hash=None,                           # None for creation
    after_hash="abc123",
)
```

## Key Patterns

### Reflection Pattern

```python
# 1. Analyze artifacts
artifacts = ["impl/a.py", "impl/b.py", "impl/c.py"]

# 2. Extract insight
insight = "All follow polynomial pattern"

# 3. Create reflection
reflection = ReflectionCrystal(
    id=generate_id(),
    target_ids=tuple(artifacts),
    reflection_type="synthesis",
    insight=insight,
    recommendations=("Extract base class", "Document pattern"),
    derived_from=(),
    proof=create_proof(insight),
)
```

### Interpretation Pattern

```python
# 1. Define time range
now = datetime.now(UTC)
six_months_ago = now - timedelta(days=180)

# 2. Analyze pattern
pattern = "Code complexity increasing"

# 3. Create interpretation
interpretation = InterpretationCrystal(
    id=generate_id(),
    artifact_pattern="impl/**/*.py",
    time_range=(six_months_ago, now),
    insight_type="trend",
    content=pattern,
    confidence=0.85,
    supporting_ids=tuple(evidence_ids),
    proof=create_proof(pattern),
)
```

### LLM Invocation Pattern

```python
# 1. Record invocation
mark = LLMInvocationMark(
    id=generate_id(),
    action="Generate code",
    reasoning="User requested feature X",
    model="claude-opus-4-5",
    prompt_tokens=count_tokens(prompt),
    completion_tokens=count_tokens(response),
    latency_ms=measure_latency(),
    temperature=0.7,
    system_prompt_hash=hash_prompt(system),
    user_prompt=prompt,
    response=response,
    causal_parent_id=None,                      # Root invocation
    triggered_by="user_input",
    state_changes=(),                           # Record changes
    crystals_created=(),                        # Record created
    crystals_modified=(),                       # Record modified
    galois_loss=calculate_loss(response),
    invocation_type="generation",
    tags=frozenset(["user-initiated"]),
)

# 2. Store mark
store_mark(mark)

# 3. If triggers cascade, set parent_id
if cascade_needed:
    cascade_mark = LLMInvocationMark(
        ...
        causal_parent_id=mark.id,               # Link to parent
        triggered_by="cascade",
        ...
    )
```

## Causal Chain Reconstruction

```python
def reconstruct_chain(mark_id: str) -> list[LLMInvocationMark]:
    """Walk causal chain from root to given mark."""
    chain = []
    current = get_mark(mark_id)
    while current:
        chain.append(current)
        if current.causal_parent_id:
            current = get_mark(current.causal_parent_id)
        else:
            break
    return list(reversed(chain))

# Usage
chain = reconstruct_chain("inv_005")
print(f"Chain depth: {len(chain)}")
print(f"Total tokens: {sum(m.total_tokens for m in chain)}")
print(f"Total latency: {sum(m.latency_ms for m in chain)}ms")
print(f"Average loss: {sum(m.galois_loss for m in chain) / len(chain)}")
```

## Cost Attribution

```python
def attribute_cost(root_mark_id: str) -> dict:
    """Attribute cost to root user action."""
    chain = reconstruct_chain(root_mark_id)

    return {
        "root_action": chain[0].action,
        "total_invocations": len(chain),
        "total_tokens": sum(m.total_tokens for m in chain),
        "total_latency_ms": sum(m.latency_ms for m in chain),
        "average_coherence": sum(m.coherence for m in chain) / len(chain),
        "total_ripple": sum(m.ripple_magnitude for m in chain),
    }

# Usage
cost = attribute_cost("inv_001")
print(f"User action '{cost['root_action']}' caused:")
print(f"  - {cost['total_invocations']} LLM calls")
print(f"  - {cost['total_tokens']} tokens")
print(f"  - {cost['total_latency_ms']}ms latency")
print(f"  - {cost['total_ripple']} state changes")
```

## Schema Registration

All schemas are registered with D-gent Universe:

```python
from agents.d.schemas.reflection import (
    REFLECTION_CRYSTAL_SCHEMA,
    INTERPRETATION_CRYSTAL_SCHEMA,
)
from agents.d.schemas.invocation import (
    LLM_INVOCATION_MARK_SCHEMA,
    STATE_CHANGE_SCHEMA,
)
```

## Testing

```bash
# Run all schema tests
uv run pytest agents/d/schemas/_tests/test_reflection.py -v
uv run pytest agents/d/schemas/_tests/test_invocation.py -v

# Type check
uv run mypy agents/d/schemas/reflection.py
uv run mypy agents/d/schemas/invocation.py
```

## Philosophy

```
"L6 reflects on what we learned. L7 interprets what it means over time.
 LLM invocations are not black boxes—they are traced, causal, witnessed."
```

- **Reflection** = Specific insight from specific artifacts
- **Interpretation** = Pattern across artifacts and time
- **Invocation** = Full LLM trace with causality and ripple effects

All carry `GaloisWitnessedProof` for self-justification.
All are frozen, immutable, versioned contracts.
All serialize cleanly to/from JSON.

**Key Insight**: By tracking causal chains and ripple effects, we can attribute cost, debug cascades, and detect patterns in LLM behavior that Datadog cannot see.
