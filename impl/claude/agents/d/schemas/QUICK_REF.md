# Code Artifact Schemas - Quick Reference

## Import

```python
from agents.d.schemas import (
    # Function tracking
    FunctionCrystal,
    ParamInfo,
    FUNCTION_CRYSTAL_SCHEMA,

    # K-block aggregation
    KBlockCrystal,
    KBLOCK_SIZE_HEURISTICS,
    KBLOCK_CRYSTAL_SCHEMA,

    # Ghost detection
    GhostFunctionCrystal,
    GHOST_FUNCTION_SCHEMA,

    # Proof
    GaloisWitnessedProof,
)
```

## Quick Create

### FunctionCrystal

```python
func = FunctionCrystal(
    id="func_xyz",
    qualified_name="module.Class.method",
    file_path="module.py",
    line_range=(10, 20),
    signature="def method(self, x: int) -> str",
    docstring="Method docstring",
    body_hash="abc123",
    parameters=(ParamInfo(name="x", type_annotation="int"),),
    return_type="str",
    imports=frozenset(["typing.Any"]),
    calls=frozenset(["helper_func"]),
    called_by=frozenset(["caller_func"]),
    layer=5,  # L5: Actions
    spec_id="spec/path.md#section",
    kblock_id="kblock_xyz",
    proof=proof,
)
```

### KBlockCrystal

```python
kblock = KBlockCrystal(
    id="kblock_xyz",
    name="module.name",
    path="module/path.py",
    function_ids=frozenset(["func_1", "func_2"]),
    boundary_type="file",  # file, module, feature, bulkhead, custom
    function_count=2,
    total_lines=100,
    estimated_tokens=1200,
    internal_coherence=0.9,
    external_coupling=0.1,
    dominant_layer=5,
    proof=proof,
)

# Properties
kblock.needs_split       # > 5000 tokens
kblock.is_undersized     # < 500 tokens
kblock.is_optimal_size   # ~2000 tokens ± 25%
```

### GhostFunctionCrystal

```python
ghost = GhostFunctionCrystal(
    id="ghost_xyz",
    suggested_name="function_name",
    suggested_location="module/path.py",
    ghost_reason="SPEC_IMPLIES",  # SPEC_IMPLIES, CALL_REFERENCES, TODO, SUGGESTED
    source_id="spec_or_func_id",
    expected_signature="def function_name(x: int) -> str",
    expected_behavior="What it should do",
    spec_id="spec/path.md#section",
)

# Properties
ghost.is_pending         # Not resolved
ghost.was_implemented    # Resolved by implementation
ghost.was_dismissed      # Resolved by dismissal
```

## Serialization

```python
# To dict
data = crystal.to_dict()

# From dict
crystal = FunctionCrystal.from_dict(data)
crystal = KBlockCrystal.from_dict(data)
crystal = GhostFunctionCrystal.from_dict(data)
```

## Schema Registration

```python
# These are already registered for Universe
FUNCTION_CRYSTAL_SCHEMA.name  # "code.function"
KBLOCK_CRYSTAL_SCHEMA.name    # "code.kblock"
GHOST_FUNCTION_SCHEMA.name    # "code.ghost"

# Serialize/deserialize through schema
data = FUNCTION_CRYSTAL_SCHEMA.serialize(func)
func = FUNCTION_CRYSTAL_SCHEMA.deserialize(data)
```

## Common Patterns

### Function with Proof

```python
proof = GaloisWitnessedProof(
    data="Function implements X as specified",
    warrant="Spec requires X behavior",
    claim="Function is necessary and sufficient",
    backing="spec/path.md#section",
    tier="CATEGORICAL",
    galois_loss=0.05,
)

func = FunctionCrystal(
    ...,
    proof=proof,
)

# Check coherence
coherence = func.proof.coherence  # 1 - galois_loss = 0.95
```

### K-Block Hierarchy

```python
# Parent K-block (module)
parent = KBlockCrystal(
    id="kblock_parent",
    name="services.witness",
    path="services/witness/",
    child_kblock_ids=frozenset(["kblock_child_1", "kblock_child_2"]),
    boundary_type="module",
)

# Child K-block (file)
child = KBlockCrystal(
    id="kblock_child_1",
    name="services.witness.store",
    path="services/witness/store.py",
    parent_kblock_id="kblock_parent",
    boundary_type="file",
)
```

### Ghost Resolution

```python
# Create ghost
ghost = GhostFunctionCrystal(
    id="ghost_xyz",
    suggested_name="validate",
    suggested_location="module.py",
    ghost_reason="SPEC_IMPLIES",
    source_id="spec_abc",
)

# Later, mark as implemented
from dataclasses import replace
from datetime import datetime, UTC

resolved_ghost = replace(
    ghost,
    resolved=True,
    resolved_to="func_validate",  # ID of implementing function
    resolved_at=datetime.now(UTC),
)

# Or dismissed
dismissed_ghost = replace(
    ghost,
    resolved=True,
    resolved_to=None,  # None means dismissed
    resolved_at=datetime.now(UTC),
)
```

## Field Reference

### FunctionCrystal

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identifier |
| `qualified_name` | str | Full dotted name |
| `file_path` | str | File location |
| `line_range` | tuple[int, int] | (start, end) lines |
| `signature` | str | Function signature |
| `docstring` | str \| None | Docstring |
| `body_hash` | str | Hash for change detection |
| `parameters` | tuple[ParamInfo, ...] | Parameter metadata |
| `return_type` | str \| None | Return annotation |
| `imports` | frozenset[str] | Used imports |
| `calls` | frozenset[str] | Called functions |
| `called_by` | frozenset[str] | Callers |
| `layer` | int | Zero Seed layer (1-7) |
| `spec_id` | str \| None | Justifying spec |
| `derived_from` | tuple[str, ...] | Parent functions |
| `kblock_id` | str \| None | Containing K-block |
| `is_ghost` | bool | Is placeholder? |
| `ghost_reason` | str \| None | Why ghost? |
| `proof` | GaloisWitnessedProof \| None | Self-justification |

### KBlockCrystal

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identifier |
| `name` | str | Human name |
| `path` | str | File/module path |
| `function_ids` | frozenset[str] | Contained functions |
| `child_kblock_ids` | frozenset[str] | Child K-blocks |
| `parent_kblock_id` | str \| None | Parent K-block |
| `boundary_type` | str | file/module/feature/bulkhead/custom |
| `boundary_confidence` | float | [0, 1] confidence |
| `function_count` | int | Number of functions |
| `total_lines` | int | Total LOC |
| `estimated_tokens` | int | Rough token count |
| `internal_coherence` | float | [0, 1] coherence |
| `external_coupling` | float | [0, 1] coupling |
| `dominant_layer` | int | Most common layer |
| `layer_distribution` | dict[int, int] | {layer: count} |
| `proof` | GaloisWitnessedProof \| None | Self-justification |

### GhostFunctionCrystal

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identifier |
| `suggested_name` | str | Suggested function name |
| `suggested_location` | str | Where it should go |
| `ghost_reason` | str | SPEC_IMPLIES/CALL_REFERENCES/TODO/SUGGESTED |
| `source_id` | str | What implied this |
| `expected_signature` | str \| None | Expected signature |
| `expected_behavior` | str | What it should do |
| `spec_id` | str \| None | Spec reference |
| `resolved` | bool | Has been resolved? |
| `resolved_to` | str \| None | Implementing func ID or None if dismissed |
| `resolved_at` | datetime \| None | When resolved |

## Size Heuristics

```python
from agents.d.schemas import KBLOCK_SIZE_HEURISTICS

KBLOCK_SIZE_HEURISTICS = {
    "chars_per_token": 4,     # 4 chars ≈ 1 token
    "min_tokens": 500,        # Minimum K-block size
    "max_tokens": 5000,       # Maximum before mandatory split
    "target_tokens": 2000,    # Sweet spot ("short essay")
}
```

---

**See Also**:
- Full documentation: `PHASE1_COMPLETE.md`
- Verification: `verify_phase1.py`
- Source: `code.py`, `kblock.py`, `ghost.py`
