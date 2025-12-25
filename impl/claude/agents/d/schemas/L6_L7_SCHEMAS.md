# Layer 6-7 Crystal Schemas & LLM Invocation Marks

**Created**: 2025-12-25
**Status**: Complete
**Location**: `agents/d/schemas/`

## Overview

This document describes the Layer 6-7 reflection schemas and the enhanced LLM invocation tracking schema. These schemas enable meta-analysis of artifacts and comprehensive LLM observability beyond what Datadog provides.

## Philosophy

```
L6 (Reflection): "What did we learn?"
L7 (Interpretation): "What does it mean over time?"
LLM Invocation: "The invocation IS the trace. The ripple IS the causality."
```

## Files Created

1. **`reflection.py`** - ReflectionCrystal, InterpretationCrystal (L6-L7)
2. **`invocation.py`** - LLMInvocationMark, StateChange (comprehensive LLM tracking)
3. **`_tests/test_reflection.py`** - Tests for reflection schemas
4. **`_tests/test_invocation.py`** - Tests for invocation schemas

## Layer 6: ReflectionCrystal

### Purpose

Reflections synthesize insights from specific artifacts. They answer: "What did we learn from these artifacts?"

### Schema

```python
@dataclass(frozen=True)
class ReflectionCrystal:
    id: str
    target_ids: tuple[str, ...]           # Artifacts being reflected upon
    reflection_type: str                  # synthesis/comparison/delta/audit
    insight: str                          # The core learning
    recommendations: tuple[str, ...]      # Actionable next steps
    derived_from: tuple[str, ...]         # Lineage
    layer: int = 6                        # Always 6
    proof: GaloisWitnessedProof | None    # Self-justification
    created_at: datetime
```

### Reflection Types

| Type | Purpose | Example |
|------|---------|---------|
| **synthesis** | Combine multiple artifacts | "Unified approach from 3 implementations" |
| **comparison** | Contrast artifacts | "Approach A vs B trade-offs" |
| **delta** | Measure change | "API evolved from v1 to v2" |
| **audit** | Quality evaluation | "Spec coverage: 85%" |

### Usage

```python
from agents.d.schemas.reflection import ReflectionCrystal
from agents.d.schemas.proof import GaloisWitnessedProof

proof = GaloisWitnessedProof(
    data="Analyzed 3 implementations",
    warrant="Common patterns identified",
    claim="Unified pattern exists",
    backing="All 3 follow polynomial structure"
)

reflection = ReflectionCrystal(
    id="refl_001",
    target_ids=("agent_a", "agent_b", "agent_c"),
    reflection_type="synthesis",
    insight="All agents follow polynomial pattern with state machines",
    recommendations=(
        "Extract common pattern into base class",
        "Document pattern in skills/"
    ),
    derived_from=("analysis_001",),
    proof=proof
)
```

## Layer 7: InterpretationCrystal

### Purpose

Interpretations find patterns across artifacts and time. They answer: "What patterns emerge over time?"

### Schema

```python
@dataclass(frozen=True)
class InterpretationCrystal:
    id: str
    artifact_pattern: str                 # Glob pattern (e.g., "impl/**/*.py")
    time_range: tuple[datetime, datetime] # (start, end)
    insight_type: str                     # trend/pattern/prediction
    content: str                          # The interpretation narrative
    confidence: float                     # [0, 1]
    supporting_ids: tuple[str, ...]       # Supporting artifacts
    layer: int = 7                        # Always 7
    proof: GaloisWitnessedProof | None    # Self-justification
    created_at: datetime
```

### Interpretation Types

| Type | Purpose | Example |
|------|---------|---------|
| **trend** | Direction of change | "Code complexity increasing" |
| **pattern** | Recurring structure | "All Crown Jewels follow same architecture" |
| **prediction** | Future forecast | "Will need refactor in 3 months" |

### Usage

```python
from agents.d.schemas.reflection import InterpretationCrystal
from datetime import datetime, UTC, timedelta

now = datetime.now(UTC)
six_months_ago = now - timedelta(days=180)

proof = GaloisWitnessedProof(
    data="6 months of commit history",
    warrant="Cyclomatic complexity metrics",
    claim="Complexity trending upward",
    backing="Average complexity: 5 → 12"
)

interpretation = InterpretationCrystal(
    id="interp_001",
    artifact_pattern="impl/claude/services/**/*.py",
    time_range=(six_months_ago, now),
    insight_type="trend",
    content="Service layer complexity increasing. Need refactoring.",
    confidence=0.85,
    supporting_ids=("metric_001", "metric_002", "metric_003"),
    proof=proof
)
```

## LLM Invocation Tracking

### Purpose

Captures EVERYTHING about an LLM call—more granular than Datadog. Enables:

1. **Causal debugging**: "What cascade led to this?"
2. **Cost attribution**: "Which user action caused 50 LLM calls?"
3. **Quality tracking**: "Which invocations have high galois_loss?"
4. **Pattern detection**: "Do cascades correlate with low coherence?"

### Schema

```python
@dataclass(frozen=True)
class StateChange:
    entity_type: str        # crystal/kblock/edge/mark
    entity_id: str
    change_type: str        # created/updated/deleted/linked
    before_hash: str | None
    after_hash: str

@dataclass(frozen=True)
class LLMInvocationMark:
    id: str
    action: str                           # What was requested
    reasoning: str                        # Why

    # LLM-specific
    model: str                            # "claude-opus-4-5"
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    temperature: float

    # Content
    system_prompt_hash: str               # SHA256 (for deduplication)
    user_prompt: str                      # Full prompt
    response: str                         # Full response

    # Causality (THE KEY)
    causal_parent_id: str | None          # Parent invocation
    triggered_by: str                     # user_input/agent_decision/scheduled/cascade

    # Ripple effects
    state_changes: tuple[StateChange, ...]
    crystals_created: tuple[str, ...]
    crystals_modified: tuple[str, ...]

    # Quality
    galois_loss: float                    # L(invocation) in [0, 1]

    # Classification
    invocation_type: str                  # generation/analysis/classification/embedding

    # Provenance
    timestamp: datetime
    tags: frozenset[str]
```

### Computed Properties

```python
mark.coherence           # 1 - galois_loss
mark.total_tokens        # prompt_tokens + completion_tokens
mark.tokens_per_second   # completion_tokens / (latency_ms / 1000)
mark.is_cascade          # Has parent?
mark.is_root             # No parent?
mark.ripple_magnitude    # len(changes) + len(created) + len(modified)
```

### Usage Example

```python
from agents.d.schemas.invocation import LLMInvocationMark, StateChange

# Create state changes
changes = (
    StateChange(
        entity_type="crystal",
        entity_id="c123",
        change_type="created",
        before_hash=None,
        after_hash="abc123"
    ),
)

# Create invocation mark
mark = LLMInvocationMark(
    id="inv_001",
    action="Generate analysis",
    reasoning="User requested code analysis",
    model="claude-opus-4-5",
    prompt_tokens=2000,
    completion_tokens=1000,
    latency_ms=3500,
    temperature=0.7,
    system_prompt_hash="sha256_hash_here",
    user_prompt="Analyze this codebase",
    response="Here is the analysis...",
    causal_parent_id=None,
    triggered_by="user_input",
    state_changes=changes,
    crystals_created=("c123", "c124"),
    crystals_modified=(),
    galois_loss=0.05,
    invocation_type="analysis",
    tags=frozenset(["user-initiated", "high-quality"])
)

print(f"Coherence: {mark.coherence}")           # 0.95
print(f"Total tokens: {mark.total_tokens}")     # 3000
print(f"Ripple: {mark.ripple_magnitude}")       # 3 (1 change + 2 created)
print(f"Root: {mark.is_root}")                  # True
```

### Causal Chain Reconstruction

LLM invocations can form chains:

```
user_input (inv_001)
  └─> cascade (inv_002)
        └─> cascade (inv_003)
              └─> cascade (inv_004)
```

Each invocation records its `causal_parent_id`, enabling:

```python
def reconstruct_chain(mark_id: str) -> list[LLMInvocationMark]:
    """Reconstruct causal chain from root to given mark."""
    chain = []
    current = get_mark(mark_id)
    while current:
        chain.append(current)
        current = get_mark(current.causal_parent_id) if current.causal_parent_id else None
    return list(reversed(chain))
```

## Integration with Universe

All schemas are registered with the D-gent Universe for persistence:

```python
from agents.d.universe import DataclassSchema

REFLECTION_CRYSTAL_SCHEMA = DataclassSchema(
    name="reflection.crystal",
    type_cls=ReflectionCrystal
)

INTERPRETATION_CRYSTAL_SCHEMA = DataclassSchema(
    name="interpretation.crystal",
    type_cls=InterpretationCrystal
)

LLM_INVOCATION_MARK_SCHEMA = DataclassSchema(
    name="llm.invocation_mark",
    type_cls=LLMInvocationMark
)
```

## Testing

Both schemas have comprehensive test coverage:

```bash
# Run reflection tests
uv run pytest agents/d/schemas/_tests/test_reflection.py -v

# Run invocation tests
uv run pytest agents/d/schemas/_tests/test_invocation.py -v
```

## Key Design Decisions

### 1. Frozen Dataclasses

All schemas are `frozen=True` for immutability. This ensures:
- No accidental mutations
- Safe concurrent access
- Clear versioning semantics

### 2. Tuple vs List

- **Storage**: `tuple` (immutable)
- **Serialization**: `list` (JSON compatible)
- **Conversion**: `to_dict()` converts tuples → lists, `from_dict()` converts lists → tuples

### 3. GaloisWitnessedProof Integration

All Layer 6-7 crystals carry optional `GaloisWitnessedProof` for self-justification:

```python
proof = GaloisWitnessedProof(
    data="What evidence supports this?",
    warrant="Why does the evidence support the claim?",
    claim="What is being claimed?",
    backing="What supports the warrant?",
    galois_loss=0.05,  # Quantified uncertainty
)
```

### 4. Causality Tracking

LLM invocations form DAGs via `causal_parent_id`:

- **Root invocations**: `causal_parent_id = None`, `triggered_by = "user_input"`
- **Cascades**: `causal_parent_id = parent_id`, `triggered_by = "cascade"`

This enables cost attribution: "User action X caused 12 LLM calls totaling 50K tokens"

### 5. Ripple Effects

Every invocation tracks its ripple:

```python
mark.state_changes       # What entities changed?
mark.crystals_created    # What new crystals?
mark.crystals_modified   # What existing crystals changed?
mark.ripple_magnitude    # Total magnitude
```

This enables impact analysis: "Which invocations cause the most state changes?"

## Future Enhancements

### 1. Reflection Chains

Just like LLM invocations chain, reflections could chain:

```
ReflectionCrystal
  └─> derived_from: [ReflectionCrystal, ReflectionCrystal]
        └─> Meta-reflection on reflections
```

### 2. Loss Aggregation

Aggregate galois_loss across invocation chains:

```python
def chain_loss(chain: list[LLMInvocationMark]) -> float:
    """Aggregate loss across causal chain."""
    return 1.0 - prod(1.0 - mark.galois_loss for mark in chain)
```

### 3. Pattern Detection

Use InterpretationCrystals to detect LLM patterns:

```python
interpretation = InterpretationCrystal(
    insight_type="pattern",
    content="High-loss invocations correlate with cascades",
    confidence=0.92,
    supporting_ids=[...],  # All invocations analyzed
)
```

### 4. Cost Attribution Dashboard

Build UI showing:

- **By user action**: Which user actions are most expensive?
- **By cascade depth**: How deep do cascades go?
- **By coherence**: Which invocations have low coherence?

## Summary

These schemas enable:

1. **Meta-analysis** (L6-L7): Reflect on artifacts, interpret patterns over time
2. **LLM observability**: Track every invocation with causal chains and ripple effects
3. **Self-justification**: Every claim carries its proof
4. **Pattern detection**: Find trends, predict future states
5. **Cost attribution**: "User X caused cascade of 50 calls"

The schemas are production-ready:
- Frozen for immutability
- Fully serializable (to_dict/from_dict)
- Universe-registered for persistence
- Comprehensive test coverage
- Type-checked with mypy

**Philosophy**: "The proof IS the decision. The trace IS the causality. The ripple IS the impact."
