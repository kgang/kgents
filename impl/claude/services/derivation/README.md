# DerivationService - Crown Jewel for Causal Lineage Tracking

**Status**: MVP Complete
**Layer**: L5 (Actions)
**Dependencies**: Universe, GaloisLossComputer, KBlockEdge

## Philosophy

> *"The proof IS the decision. The derivation IS the lineage."*

Every Crystal in the taxonomy has a derivation path tracing back to foundational axioms. The DerivationService tracks these relationships, forming a causal DAG from:

```
Constitution (L1) → Value (L2) → Prompt (L3) → Spec (L4)
→ Code (L5) → Test (L5) → Reflection (L6) → Interpretation (L7)
```

## Core Capabilities

### 1. Lineage Tracing

Trace any crystal back to its axiomatic ground:

```python
service = DerivationService(universe, galois)
chain = await service.trace_to_axiom("function-abc123")

print(f"Grounded: {chain.is_grounded}")
print(f"Total loss: {chain.total_galois_loss:.3f}")
print(f"Coherence: {chain.coherence():.3f}")

for ref in chain.chain:
    print(f"  L{ref.layer} {ref.crystal_type}: {ref.id} (loss: {ref.galois_loss:.3f})")
```

**Output**:
```
Grounded: True
Total loss: 0.234
Coherence: 0.766
  L5 function: function-abc123 (loss: 0.120)
  L4 spec: spec-def456 (loss: 0.089)
  L2 value: value-ghi789 (loss: 0.025)
  L1 axiom: axiom-jkl012 (loss: 0.000)
```

### 2. Derivation Trees

Get full ancestry AND descendants:

```python
tree = await service.get_derivation_tree("spec-abc123")

print(f"Ancestors: {len(tree.ancestors)}")
for ref in tree.ancestors:
    print(f"  ↑ L{ref.layer} {ref.crystal_type}: {ref.id}")

print(f"Descendants: {len(tree.descendants)}")
for ref in tree.descendants:
    print(f"  ↓ L{ref.layer} {ref.crystal_type}: {ref.id}")
```

### 3. Drift Detection

Find spec/impl divergence:

```python
reports = await service.detect_drift("spec-abc123")

for report in reports:
    print(f"Drift in {report.impl_id}:")
    print(f"  Severity: {report.drift_severity:.3f}")
    print(f"  Type: {report.drift_type}")
    print(f"  Details: {report.details}")
```

**Output**:
```
Drift in function-xyz789:
  Severity: 0.456
  Type: impl_diverged
  Details: Galois loss: 0.456 (impl_diverged)
```

### 4. Coherence Checking

Measure coherence along derivation chain:

```python
coherence = await service.coherence_check("function-abc123")
print(f"Coherence: {coherence:.1%}")

if coherence < 0.7:
    print("⚠️  Low coherence - consider refactoring")
```

### 5. Orphan Detection

Find crystals with no axiomatic grounding:

```python
orphans = await service.find_orphans()
print(f"Found {len(orphans)} orphaned crystals:")
for orphan_id in orphans:
    print(f"  {orphan_id} - needs justification")
```

### 6. Edge Creation

Link crystals with derivation edges:

```python
edge_id = await service.link_derivation(
    source_id="function-abc123",
    target_id="spec-def456",
    edge_kind="IMPLEMENTS",
    context="Implements Section 3.2: User Authentication",
    mark_id="mark-witness-789"  # Optional witness mark
)
```

## Edge Kinds

The service recognizes five semantic edge types:

| Kind | Meaning | Example |
|------|---------|---------|
| `GROUNDS` | Axiomatic grounding | Axiom → Value |
| `JUSTIFIES` | General justification | Value → Goal |
| `SPECIFIES` | Specification defines | Spec → Implementation |
| `IMPLEMENTS` | Implementation of spec | Code → Spec |
| `TESTS` | Test coverage | Test → Code |
| `DERIVES` | General derivation | Any → Any |

These map to internal `KBlockEdge` types:
- `GROUNDS` → `justifies`
- `JUSTIFIES` → `justifies`
- `SPECIFIES` → `derives_from`
- `IMPLEMENTS` → `implements`
- `TESTS` → `tests`
- `DERIVES` → `derives_from`

## Data Structures

### CrystalRef

Reference to a crystal in a derivation chain:

```python
@dataclass(frozen=True)
class CrystalRef:
    id: str                 # Crystal ID in Universe
    layer: int              # Zero Seed layer (1-7)
    crystal_type: str       # axiom, value, prompt, spec, function, etc.
    edge_kind: str          # GROUNDS, JUSTIFIES, IMPLEMENTS, etc.
    galois_loss: float      # Loss at this edge
```

### DerivationChain

Path from target to axioms:

```python
@dataclass
class DerivationChain:
    target_id: str              # Crystal being traced
    chain: list[CrystalRef]     # Ordered target → ancestors
    total_galois_loss: float    # Accumulated loss
    is_grounded: bool           # Reaches L1/L2?

    def coherence(self) -> float:
        return 1.0 - self.total_galois_loss
```

### DerivationTree

Full ancestry + descendants:

```python
@dataclass
class DerivationTree:
    crystal_id: str                 # Root crystal
    ancestors: list[CrystalRef]     # Parents, grandparents, ...
    descendants: list[CrystalRef]   # Children, grandchildren, ...
    is_grounded: bool               # Reaches axioms?
    total_loss_to_axioms: float     # Accumulated loss upward
```

### DriftReport

Spec/impl divergence report:

```python
@dataclass
class DriftReport:
    spec_id: str            # Specification crystal
    impl_id: str            # Implementation crystal
    drift_severity: float   # [0, 1], higher = more drift
    drift_type: str         # minimal_drift, impl_diverged, spec_changed, missing_impl
    details: str            # Human-readable explanation
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  DerivationService                                          │
│                                                             │
│  ┌──────────────┐  ┌─────────────────┐  ┌───────────────┐ │
│  │   Universe   │  │ GaloisComputer  │  │  KBlockEdge   │ │
│  │  (storage)   │  │  (coherence)    │  │ (relationships)│ │
│  └──────────────┘  └─────────────────┘  └───────────────┘ │
│                                                             │
│  • trace_to_axiom() ──────────────────────────────────────┐│
│  • get_derivation_tree() ─────────────────────────────────┐│
│  • detect_drift() ────────────────────────────────────────┐│
│  • coherence_check() ─────────────────────────────────────┐│
│  • find_orphans() ────────────────────────────────────────┐│
│  • link_derivation() ─────────────────────────────────────┐│
└─────────────────────────────────────────────────────────────┘
```

## Layer Taxonomy

The service understands the Zero Seed holarchy:

| Layer | Name | Crystal Types | Grounded? |
|-------|------|---------------|-----------|
| L1 | Axiom | `AxiomCrystal` | Yes (root) |
| L2 | Value | `ValueCrystal` | Yes (root) |
| L3 | Prompt | `PromptCrystal`, `InvocationCrystal` | No |
| L4 | Spec | `SpecCrystal` | No |
| L5 | Code | `FunctionCrystal`, `TestCrystal`, `KBlockCrystal` | No |
| L6 | Reflection | `ReflectionCrystal` | No |
| L7 | Interpretation | `InterpretationCrystal` | No |

**Grounded** = Has derivation path to L1 or L2.

## Teaching Notes

### Gotcha: Explicit Edge Creation

Crystals don't automatically know their parents. You must call `link_derivation()` to establish relationships:

```python
# ✗ BAD: Crystals are isolated
func_id = await universe.store(func)
spec_id = await universe.store(spec)

# ✓ GOOD: Link them explicitly
await service.link_derivation(func_id, spec_id, "IMPLEMENTS")
```

**Evidence**: `service.py::link_derivation()`

### Gotcha: Galois is Optional

The service works without `GaloisLossComputer`, but loss-dependent methods return 0.0:

```python
# Without Galois
service = DerivationService(universe, galois=None)
coherence = await service.coherence_check("crystal-abc")  # Returns 1.0

# With Galois
galois = GaloisLossComputer(metric="token")
service = DerivationService(universe, galois)
coherence = await service.coherence_check("crystal-abc")  # Computes actual loss
```

**Evidence**: `service.py::__init__`, `service.py::_compute_edge_loss`

### Gotcha: Layer Monotonicity

Parent layer must be < child layer:

```python
# ✓ VALID: L5 function → L4 spec → L2 value → L1 axiom
# ✗ INVALID: L3 prompt → L5 function (upward derivation)
```

**Evidence**: `k_block/core/derivation.py::validate_derivation`

### Gotcha: is_grounded Checks L1/L2

A crystal is grounded if its lineage reaches L1 (axioms) or L2 (values):

```python
chain = await service.trace_to_axiom("function-abc")
print(chain.is_grounded)  # True if reaches L1 or L2
```

**Evidence**: `service.py::trace_to_axiom`, `k_block/core/derivation.py::DerivationDAG.is_grounded`

## Integration Points

### With Universe

DerivationService queries crystals from Universe using schema-aware retrieval:

```python
crystal = await universe.get(crystal_id)  # Returns typed object
```

### With GaloisLossComputer

Computes coherence via Galois connection:

```python
loss = await galois.compute(content)  # R → C round-trip loss
coherence = 1.0 - loss
```

### With KBlockEdge

Uses KBlockEdge for relationship tracking:

```python
edge = KBlockEdge(
    id="edge-abc",
    source_id="func-123",
    target_id="spec-456",
    edge_type="implements",
    mark_id="mark-789"  # Witness mark
)
```

### With Witness Marks

Edges can reference witness marks for traceability:

```python
edge_id = await service.link_derivation(
    source_id="func-abc",
    target_id="spec-def",
    edge_kind="IMPLEMENTS",
    mark_id="mark-123"  # Links to WitnessMark
)
```

## Testing

Run tests:

```bash
cd impl/claude
uv run pytest services/derivation/_tests/test_service.py -v
```

Tests cover:
- ✓ Simple lineage tracing (function → value → axiom)
- ✓ Coherence computation
- ✓ Derivation tree queries
- ✓ Edge creation
- ✓ Service without Galois

## Future Enhancements

### Phase 2: Full Orphan Detection

Current `find_orphans()` is a placeholder. Full implementation:

1. Build complete DAG from all edges
2. Find connected components via graph traversal
3. Identify components with no L1/L2 nodes
4. Return crystal IDs in ungrounded components

### Phase 3: Multi-Parent Support

Current implementation follows first parent edge only. Enhance to:

1. Support crystals with multiple parents (composition)
2. Compute loss across all paths
3. Return all derivation chains (not just first)

### Phase 4: Edge Persistence

Current edges are cached in memory. Add:

1. Persist edges to Universe
2. Query edges efficiently (index by source/target)
3. Support edge deletion/updates

### Phase 5: Drift Remediation

Enhance drift detection with remediation suggestions:

1. Identify which part of spec/impl drifted
2. Generate refactoring plan
3. Track drift over time (trend analysis)

## References

- **Spec**: `spec/protocols/zero-seed.md` - Zero Seed holarchy
- **Skills**: `docs/skills/crown-jewel-patterns.md` - Service patterns
- **K-Block**: `services/k_block/core/derivation.py` - DAG implementation
- **Edges**: `services/k_block/core/edge.py` - Edge semantics
- **Galois**: `agents/d/galois.py` - Loss computation
- **Universe**: `agents/d/universe/universe.py` - Storage layer

---

*Created: 2025-12-25*
*Status: MVP Complete*
*Next: Phase 2 (Full Orphan Detection)*
