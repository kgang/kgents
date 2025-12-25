# Phase 1: Unified Crystal Taxonomy - COMPLETE

## Summary

Successfully implemented Phase 1 of the Unified Crystal Taxonomy for code artifacts. This extends D-gent's Crystal system to track code at function-level granularity, enabling precise derivation tracking, coherence analysis, and ghost detection.

## Created Files

### 1. `agents/d/schemas/code.py`

**FunctionCrystal** - Function-level code tracking

Every function in the codebase becomes a self-justifying crystal with:

- **Identity**: `qualified_name`, `file_path`, `line_range`
- **Content**: `signature`, `docstring`, `body_hash`
- **Dependencies**: `imports`, `calls`, `called_by`
- **Derivation**: `spec_id`, `derived_from`
- **Context**: `layer` (Zero Seed level), `kblock_id` (coherence window)
- **Ghost status**: `is_ghost`, `ghost_reason`
- **Proof**: `GaloisWitnessedProof` (self-justification)

**ParamInfo** - Function parameter metadata

Captures full signature information:
- `name`, `type_annotation`, `default`
- `is_variadic` (*args), `is_keyword` (**kwargs)

Example:
```python
func = FunctionCrystal(
    id="func_create_mark",
    qualified_name="services.witness.store.MarkStore.create_mark",
    file_path="services/witness/store.py",
    line_range=(42, 58),
    signature="def create_mark(self, action: str, reasoning: str) -> Mark",
    imports=frozenset(["dataclasses.dataclass", "datetime.datetime"]),
    calls=frozenset(["uuid.uuid4", "datetime.now"]),
    called_by=frozenset(["services.witness.api.mark_action"]),
    layer=5,  # L5: Actions
    spec_id="spec/protocols/witness.md#mark-creation",
    proof=proof,
)
```

### 2. `agents/d/schemas/kblock.py`

**KBlockCrystal** - Coherence window aggregation

A K-block aggregates functions into a coherent unit (~500-5000 tokens, target 2000):

- **Identity**: `id`, `name`, `path`
- **Membership**: `function_ids` (functions in this block)
- **Hierarchy**: `child_kblock_ids`, `parent_kblock_id`
- **Boundary**: `boundary_type`, `boundary_confidence`
- **Metrics**: `function_count`, `total_lines`, `estimated_tokens`
- **Coherence**: `internal_coherence`, `external_coupling`
- **Layer distribution**: `dominant_layer`, `layer_distribution`
- **Proof**: `GaloisWitnessedProof`

**Boundary Types**:
- `file`: Functions in a single file
- `module`: Functions in a Python module
- `feature`: Functions implementing a feature (cross-file)
- `bulkhead`: Explicit isolation boundary
- `custom`: User-defined boundary

**Size Analysis Properties**:
- `needs_split`: True if > max_tokens (5000)
- `is_undersized`: True if < min_tokens (500)
- `is_optimal_size`: True if in target range (~2000 ± 25%)

Example:
```python
kblock = KBlockCrystal(
    id="kblock_witness_store",
    name="witness.store",
    path="services/witness/store.py",
    function_ids=frozenset(["func_create_mark", "func_get_mark", "func_list_marks"]),
    boundary_type="file",
    function_count=3,
    total_lines=150,
    estimated_tokens=1800,
    internal_coherence=0.92,
    external_coupling=0.15,
    proof=proof,
)
```

### 3. `agents/d/schemas/ghost.py`

**GhostFunctionCrystal** - Missing code detection

Tracks functions that should exist but don't:

- **Identity**: `id`, `suggested_name`, `suggested_location`
- **Reason**: `ghost_reason` (why we think this should exist)
- **Source**: `source_id` (what implied this ghost)
- **Expectation**: `expected_signature`, `expected_behavior`
- **Derivation**: `spec_id` (if spec-implied)
- **Resolution**: `resolved`, `resolved_to`, `resolved_at`

**Ghost Reasons**:
- `SPEC_IMPLIES`: Spec describes unimplemented function
- `CALL_REFERENCES`: Code calls undefined function
- `TODO`: User marked TODO/FIXME/HACK
- `SUGGESTED`: Analysis suggests missing abstraction

**State Properties**:
- `is_pending`: Not yet resolved
- `was_implemented`: Resolved by implementation
- `was_dismissed`: Resolved by dismissal (not needed)

Example:
```python
ghost = GhostFunctionCrystal(
    id="ghost_validate_mark",
    suggested_name="validate_mark",
    suggested_location="services/witness/validation.py",
    ghost_reason="SPEC_IMPLIES",
    source_id="spec/protocols/witness.md#validation",
    expected_signature="def validate_mark(mark: Mark) -> bool",
    expected_behavior="Validate mark has required fields and valid reasoning",
    spec_id="spec/protocols/witness.md#validation",
)
```

### 4. Updated `agents/d/schemas/__init__.py`

Added exports for all new schemas:
- `ParamInfo`, `FunctionCrystal`, `FUNCTION_CRYSTAL_SCHEMA`
- `KBLOCK_SIZE_HEURISTICS`, `KBlockCrystal`, `KBLOCK_CRYSTAL_SCHEMA`
- `GhostFunctionCrystal`, `GHOST_FUNCTION_SCHEMA`

## Key Features

### ✓ All schemas are frozen dataclasses
- Immutable by design (thread-safe, hashable)
- Structural pattern matching support
- Clear value semantics

### ✓ All have to_dict() and from_dict() methods
- Universe serialization support
- JSON-compatible representation
- Preserves frozenset → list → frozenset conversions

### ✓ All have DataclassSchema instances
- `FUNCTION_CRYSTAL_SCHEMA = DataclassSchema(name="code.function", type_cls=FunctionCrystal)`
- `KBLOCK_CRYSTAL_SCHEMA = DataclassSchema(name="code.kblock", type_cls=KBlockCrystal)`
- `GHOST_FUNCTION_SCHEMA = DataclassSchema(name="code.ghost", type_cls=GhostFunctionCrystal)`

### ✓ All support GaloisWitnessedProof integration
- Every crystal can carry a self-justifying proof
- Coherence = 1 - galois_loss
- Toulmin argumentation + Galois loss quantification

### ✓ All pass mypy type checking
- Full type annotations
- No type errors in new files
- Compatible with existing D-gent infrastructure

## Verification

Created `agents/d/schemas/verify_phase1.py` demonstrating:

1. **FunctionCrystal round-trip**
   - Create → to_dict() → from_dict() → verify equality
   - All fields preserved (imports, calls, proof, etc.)

2. **KBlockCrystal size analysis**
   - `needs_split`, `is_undersized`, `is_optimal_size` properties
   - Token estimation using KBLOCK_SIZE_HEURISTICS

3. **GhostFunctionCrystal state machine**
   - `is_pending`, `was_implemented`, `was_dismissed` properties
   - Resolution tracking

Run: `uv run python agents/d/schemas/verify_phase1.py`

## Design Decisions

### Why frozen dataclasses?
- **Immutability**: Crystals never mutate (sheaf coherence)
- **Hashability**: Can use as dict keys, set members
- **Thread-safety**: No race conditions
- **Value semantics**: Equality by structure, not identity

### Why frozenset for collections?
- **Immutability**: Consistent with frozen dataclass
- **Set semantics**: No duplicates, fast membership tests
- **Serialization**: Convert to list for JSON, back to frozenset on load

### Why separate ParamInfo?
- **Composability**: Reusable across function signatures
- **Type safety**: Structured parameter metadata
- **Clarity**: Better than dict[str, Any]

### Why layer field?
- **Zero Seed integration**: Every artifact has epistemic layer
- **Proof requirements**: L3+ requires Toulmin proof
- **Categorical composition**: Layer-preserving morphisms

### Why proof field?
- **Self-justification**: Every crystal answers "why?"
- **Galois loss**: Quantify coherence, not just existence
- **Derivation tracking**: Audit trail for decisions

## Patterns Followed

### From `proof.py`
- Frozen dataclass with datetime fields
- to_dict() converts tuples → lists
- from_dict() converts lists → tuples
- DataclassSchema for Universe registration

### From `witness.py`
- Multiple schemas in single file (grouped by domain)
- Clear docstrings explaining purpose
- Default values for optional fields
- Context dict for extensibility

### From `crystal.py`
- CrystalMeta pattern for schema envelope
- Generic type parameter for typed values
- Property methods for derived values
- Upgrade tracking via crystallized_from

## Integration Points

### Universe Backend
- All schemas registered via DataclassSchema
- to_dict()/from_dict() enable JSON storage
- Compatible with Postgres JSONB columns

### Zero Seed System
- `layer` field integrates with epistemic layers
- Proof requirements for L3+ artifacts
- Galois loss computation for coherence

### Brain/Director
- FunctionCrystal enables code archaeology
- KBlockCrystal guides refactoring decisions
- GhostFunctionCrystal surfaces missing code

### AGENTESE
- Can expose via `code.*` context
- `code.function.list` → list functions
- `code.kblock.analyze` → compute coherence
- `code.ghost.pending` → show unresolved ghosts

## Next Phases

### Phase 2: AST Parser
- Extract FunctionCrystals from Python source
- Compute qualified_name, signature, line_range
- Detect imports, calls, called_by
- Hash function bodies for change detection

### Phase 3: K-Block Detection
- Cluster functions into coherent K-blocks
- Compute internal_coherence, external_coupling
- Detect boundary types and confidence
- Recommend splits/merges based on size

### Phase 4: Ghost Detection
- Parse specs for implied functions
- Analyze call graphs for undefined references
- Detect TODO comments suggesting extractions
- Suggest missing abstractions via code analysis

### Phase 5: Brain/Director Integration
- Store crystals in Universe (Postgres)
- Expose via AGENTESE protocol
- Build code archaeology UI (React)
- Enable spec ↔ impl drift detection

## Success Criteria

- [x] All schemas are frozen dataclasses
- [x] All have to_dict() and from_dict() methods
- [x] All have DataclassSchema instances for Universe registration
- [x] Type hints are complete
- [x] Docstrings explain the purpose
- [x] All schemas import successfully
- [x] Round-trip serialization works
- [x] No mypy errors in new files
- [x] Verification script demonstrates all features

## Files Created

```
agents/d/schemas/
├── code.py                 # FunctionCrystal, ParamInfo
├── kblock.py               # KBlockCrystal, KBLOCK_SIZE_HEURISTICS
├── ghost.py                # GhostFunctionCrystal
├── verify_phase1.py        # Verification script
├── PHASE1_COMPLETE.md      # This document
└── __init__.py             # Updated with new exports
```

## Philosophy

> "Every function is a crystal. Every crystal has a proof. Every crystal exists in a K-block. Ghost crystals mark implied functions."

The Unified Crystal Taxonomy extends the metaphysical fullstack to code artifacts:

```
Spec (L4) → Proof (L3) → Function (L5) → K-Block (aggregation) → Ghost (absence)
```

Code archaeology becomes:
- "Why does this function exist?" → proof.claim
- "What spec justifies it?" → spec_id
- "Is it coherent?" → proof.galois_loss
- "What's missing?" → ghost crystals

---

**Status**: ✓ Phase 1 Complete
**Date**: 2025-12-25
**Author**: Claude Opus 4.5 + Kent Gang
