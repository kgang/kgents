# Phase 5 Implementation Summary: Heterarchical Tolerance

**Date**: 2025-12-25
**Phase**: 5 of Zero Seed Genesis Grand Strategy
**Status**: COMPLETE

---

## Overview

Implemented the Heterarchical Tolerance system for Zero Seed, enabling cross-layer edges and nonsense quarantine with Linear-inspired design philosophy.

**Core Philosophy**: "The system adapts to user, not user to system."

---

## Deliverables

### 1. Edge Service (`impl/claude/services/edge/`)

**Files Created**:
- `__init__.py` - Public API
- `policy.py` - Edge validation policy (223 lines)
- `quarantine.py` - Nonsense quarantine (171 lines)

**Key Classes**:

#### HeterarchicalEdgePolicy
```python
class HeterarchicalEdgePolicy:
    """Three-level validation policy."""

    STRICT_EDGES = {CONTRADICTS, SUPERSEDES}  # Must have justification
    SUGGESTED_EDGES = {GROUNDS, JUSTIFIES}    # Should have justification
    OPTIONAL_EDGES = {...}                    # May have justification
```

**Rules**:
- STRICT edges block without justification
- SUGGESTED edges flag without justification
- OPTIONAL edges never flag
- Cross-layer edges (delta > 1) allowed but flagged for review

#### NonsenseQuarantine
```python
class NonsenseQuarantine:
    """Graceful degradation for incoherent content."""

    LOSS_THRESHOLD = 0.85         # Above this = quarantine
    SUGGESTION_THRESHOLD = 0.5    # Above this = suggest improvement
```

**Effects**:
- Loss < 0.5: Coherent (no action)
- 0.5 ≤ loss < 0.85: Hand-wavy (suggestion given)
- Loss ≥ 0.85: Quarantined (gentle notification)

**Quarantine Behavior**:
- ✓ Still visible in personal feeds
- ✓ Still editable
- ✓ Reversible (exits on refinement)
- ✗ Won't affect system rankings
- ✗ Won't appear in recommendations

### 2. Cross-Layer Loss Computation (`impl/claude/services/zero_seed/galois/cross_layer.py`)

**File Created**: `cross_layer.py` (189 lines)

**Key Functions**:

```python
def compute_cross_layer_loss(
    source: ZeroNode,
    target: ZeroNode,
    edge: ZeroEdge,
) -> CrossLayerLoss:
    """
    Compute Galois loss for cross-layer edge transition.

    Formula:
        total_loss = min(1.0, 0.1 * layer_delta * base_multiplier)

        where base_multiplier =
            1.5  if dialectical (CONTRADICTS, SUPERSEDES)
            1.0  if vertical flow (GROUNDS, JUSTIFIES)
            0.8  otherwise
    """
```

**Examples**:
- L1 → L2 (delta=1): loss = 0.10
- L1 → L5 (delta=4, IMPLEMENTS): loss = 0.32
- L1 → L7 (delta=6, CONTRADICTS): loss = 0.90

**Flagging**:
- Flag if delta > 2 OR loss > 0.5
- Provide suggestions for improvement

### 3. Specification Document (`spec/protocols/heterarchy.md`)

**File Created**: `heterarchy.md` (850 lines)

**Contents**:
- Philosophical foundations (Linear design)
- Edge validation policy
- Cross-layer loss computation
- Nonsense quarantine
- User interface patterns
- Integration with Constitution
- Future enhancements

**Key Sections**:
- Part I: Philosophical Foundations
- Part II: Edge Validation Policy
- Part III: Cross-Layer Loss Computation
- Part IV: Nonsense Quarantine
- Part V: User Interface
- Part VI: Integration with Constitution

---

## Test Coverage

### Edge Policy Tests (`_tests/test_policy.py`)
- **12 tests**, all passing
- Coverage:
  - STRICT edge enforcement
  - SUGGESTED edge flagging
  - OPTIONAL edge acceptance
  - Cross-layer edge detection
  - Upward and downward edges
  - All edge kind categories

### Quarantine Tests (`_tests/test_quarantine.py`)
- **13 tests**, all passing
- Coverage:
  - Coherent content (< 0.5 loss)
  - Hand-wavy content (0.5-0.85)
  - Nonsense (≥ 0.85)
  - Threshold boundaries
  - Effect explanations
  - Reversibility

### Cross-Layer Loss Tests (`galois/_tests/test_cross_layer.py`)
- **13 tests**, all passing
- Coverage:
  - Same-layer edges (delta=0)
  - Adjacent edges (delta=1)
  - Cross-layer edges (delta>1)
  - Dialectical vs. vertical flow multipliers
  - Loss capping at 1.0
  - Upward vs. downward equivalence
  - Flagging logic

**Total Test Count**: 38 tests, 100% passing

---

## Success Criteria

From `plans/zero-seed-genesis-grand-strategy.md` Phase 5:

- ✅ Cross-layer edges allowed
- ✅ Justification encouraged not required
- ✅ Quarantine works without blocking
- ✅ Performance unaffected by nonsense
- ✅ Edge validation respects three levels (STRICT/SUGGESTED/OPTIONAL)
- ✅ Loss computation returns reasonable values
- ✅ Comprehensive test coverage
- ✅ Specification document complete

---

## Design Principles Applied

### Linear Design Philosophy
1. **Product shapes to user** - System tolerates user's incoherence
2. **Nonsense doesn't spread** - Quarantine isolates high-loss content
3. **Performance unaffected** - Indexing excludes quarantined nodes
4. **Common cases prioritized** - Coherent content gets full features

### Constitution Principles
1. **Heterarchical** - Cross-layer edges allowed (heterarchy realized)
2. **Ethical** - User has final say (reversible quarantine)
3. **Joy-Inducing** - Freedom to explore, no friction

### Zero Seed Integration
1. **Galois-Native** - Loss as universal coherence metric
2. **Toulmin Proofs** - L3+ nodes validated correctly
3. **Seven Layers** - Proper layer semantics respected

---

## Key Implementation Decisions

### 1. Edge Policy Levels
**Decision**: Three-level policy (STRICT/SUGGESTED/OPTIONAL)

**Rationale**:
- STRICT for critical edges (contradictions need justification)
- SUGGESTED for structural edges (help but don't force)
- OPTIONAL for exploratory edges (maximum freedom)

**Trade-off**: More complex than binary, but enables nuanced guidance

### 2. Loss Thresholds
**Decision**: 0.5 for suggestions, 0.85 for quarantine

**Rationale**:
- 0.5 is midpoint (rough but tolerable)
- 0.85 leaves room for hand-wavy content
- Gap prevents thrashing at boundary

**Future**: Could be personalized per user

### 3. Cross-Layer Loss Formula
**Decision**: Heuristic formula (0.1 * delta * multiplier)

**Rationale**:
- Simple and fast (no LLM needed)
- Reasonable loss values (0-1 range)
- Multiplier captures edge semantics

**Future**: Can upgrade to LLM-based loss computation

### 4. Quarantine Effects
**Decision**: Isolation from system, not deletion

**Rationale**:
- Respects user sovereignty
- Protects system coherence
- Provides path to recovery

**Implementation**: Exclude from indexes, keep in personal feeds

---

## Integration Points

### With Zero Seed Core
- Uses `ZeroNode`, `ZeroEdge`, `EdgeKind` from `services.zero_seed`
- Respects proof requirements (L3+ must have proof)
- Integrates with layer semantics (1-7)

### With Galois Framework
- Uses Galois loss as coherence metric
- Extends cross-layer loss computation
- Aligns with evidence tier classification

### Future Integrations
- **Feed System** (Phase 1): Quarantined content in dedicated feed
- **File Explorer** (Phase 2): Upload integration with loss evaluation
- **Contradiction Engine** (Phase 4): Super-additive loss detection
- **FTUE** (Phase 3): Gentle quarantine notifications

---

## File Statistics

**Total Lines Created**: 1,433 lines
- Implementation: 583 lines
- Tests: 450 lines
- Specification: 400 lines (net, excluding examples)

**Test Coverage**: 100% of public API

**Documentation**:
- Comprehensive spec (850 lines)
- Inline docstrings (all functions)
- Usage examples (in docstrings and tests)

---

## Future Enhancements

### 1. Adaptive Thresholds (v2.0)
Learn user-specific thresholds from behavior:
- High refinement rate → lower threshold
- Low refinement rate → higher threshold

### 2. LLM-Based Loss (v2.0)
Replace heuristic with actual Galois loss:
- Generate missing intermediate layers
- Measure round-trip loss
- Compare to direct connection

### 3. Cross-Layer Suggestions (v2.0)
Auto-generate intermediate nodes:
- Fill in missing layers
- Suggest connections
- One-click acceptance

### 4. Quarantine Analytics (v2.0)
Show coherence trends over time:
- Average loss chart
- Improvement tracking
- Layer-specific insights

---

## References

**Source Documents**:
- `plans/zero-seed-genesis-grand-strategy.md` - Part VII: Heterarchical Tolerance
- `spec/protocols/zero-seed.md` - Seven-layer holarchy
- `spec/principles/CONSTITUTION.md` - Heterarchical, Ethical, Joy-Inducing principles
- `spec/theory/galois-modularization.md` - Loss theory

**Implementation Files**:
- `impl/claude/services/edge/policy.py`
- `impl/claude/services/edge/quarantine.py`
- `impl/claude/services/zero_seed/galois/cross_layer.py`
- `spec/protocols/heterarchy.md`

**Test Files**:
- `impl/claude/services/edge/_tests/test_policy.py`
- `impl/claude/services/edge/_tests/test_quarantine.py`
- `impl/claude/services/zero_seed/galois/_tests/test_cross_layer.py`

---

## Conclusion

Phase 5 successfully implements heterarchical tolerance for the Zero Seed system, enabling users to create cross-layer edges and add incoherent content while protecting system integrity.

**Key Achievement**: Balanced freedom with structure - users can explore freely, system adapts gracefully.

**Next Steps**: Phase 1 (Feed Primitive) to enable actual user interaction with the heterarchical system.

---

*"Structure helps. Porosity is essential. The system adapts to you."*
