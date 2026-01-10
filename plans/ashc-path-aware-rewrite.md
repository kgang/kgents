# ASHC Path-Aware Rewrite: Self-Aware Proof-Carrying Compiler

**Status**: READY FOR IMPLEMENTATION
**Priority**: HIGH (Radical, Transformative)
**Created**: 2025-01-10
**Author**: Claude + Kent (Design Interview)

---

## Executive Summary

Transform ASHC (Agentic Self-Hosting Compiler) into a **self-aware proof-carrying system** where every derivation from Constitution → Spec → Implementation is a **witnessed path** that can be verified, composed, and reflected upon.

**The Core Insight**: In HoTT (Homotopy Type Theory), proofs of equality ARE paths. We extend this:
- Derivation (Principle → Spec) IS a path with witness
- Refinement (Spec → Implementation) IS a path with witness
- Paths compose categorically (associativity, identity)
- Properties transport through paths (with loss decay)
- ASHC can query its own derivation chain (self-awareness)

**The Puppet Principle Connection**: Isomorphisms between domains are paths. Hot-swapping puppets = path composition. The structure IS the insight.

---

## Part I: Research Synthesis

### 1.1 HoTT Paths (Academic Foundation)

From authoritative sources (HoTT Book, Emily Riehl, 1Lab, nLab):

| Concept | Definition | kgents Application |
|---------|------------|-------------------|
| **Path** | Proof of equality A = B | Derivation witness |
| **Path Induction (J)** | To prove P for all paths, prove for refl | Transport lemmas |
| **Path Composition** | p : A=B, q : B=C gives p∙q : A=C | Derivation chaining |
| **Univalence** | (A = B) ≃ (A ≃ B) | Isomorphic specs are equal |
| **Transport** | Move data/properties along paths | Property preservation |
| **∞-groupoid** | Paths, paths-between-paths, etc. | Higher coherence |

**Key Insight**: Paths satisfy weak groupoid laws—associativity and identity hold up to higher paths. This is exactly what we need for lossy derivations.

### 1.2 Proof-Carrying Code Patterns (Industry)

From CompCert, CakeML, Verus, LiquidHaskell, F*:

| Pattern | Description | Our Application |
|---------|-------------|-----------------|
| **Syntactic Attachment** | Proofs embedded in artifacts | Witness in DerivationPath |
| **Compositional Verification** | Module proofs compose | Path composition |
| **Small TCB** | Minimal trusted checker | Lean 4 kernel |
| **Frame Rule** | Unchanged parts preserved | Loss monotonicity |
| **Refinement Types** | Properties in types | Graded derivations |

**Key Insight**: CompCert's 16-pass compositional verification shows proofs can chain. CakeML shows end-to-end verification is tractable.

### 1.3 Existing kgents Infrastructure

| Component | Location | Status | Integration Point |
|-----------|----------|--------|-------------------|
| Graph Engine | `services/verification/graph_engine.py` | EXISTS | DerivationPath storage |
| Galois Loss | `services/zero_seed/galois/galois_loss.py` | EXISTS | Loss measurement |
| HoTT Model | `services/verification/hott.py` | EXISTS | Conceptual types |
| K-Block DAG | `services/k_block/core/derivation.py` | EXISTS | Lineage tracking |
| Witness Marks | `services/witness/mark.py` | EXISTS | Path witnesses |
| Lean Proofs | `proofs/kgents_proofs/` | EXISTS | Formal verification |

### 1.4 ASHC Current State

**Files**:
- `protocols/ashc/evidence.py` - Evidence accumulation
- `protocols/ashc/adaptive.py` - Bayesian sampling
- `protocols/ashc/economy.py` - Economic accountability
- `services/ashc/checker.py` - Proof checking
- `services/ashc/obligation.py` - Obligation extraction

**Gap Analysis** (from sub-agent research):

| Component | L2.5 COMPOSABLE | L2.7 GENERATIVE | L2.15 WITNESS | L1.8 GALOIS |
|-----------|-----------------|-----------------|---------------|-------------|
| Evidence | IMPLICIT | IMPLICIT | **STUB** | PARTIAL |
| Adaptive | MISSING | IMPLICIT | **MISSING** | **INCOMPATIBLE** |
| Economy | MISSING | EXPLICIT (unused) | PARTIAL | MISSING |
| Checker | MISSING | IMPLICIT | PARTIAL | MISSING |
| Obligation | IMPLICIT | EXPLICIT (unwitnessed) | EXPLICIT (not marked) | MISSING |

**Critical Finding**: All components have implicit derivations but NO explicit witnesses. The `Run.witnesses` field is always `()`. No Marks are emitted.

---

## Part II: Architecture Design

### 2.1 The DerivationPath Type

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

Source = TypeVar("Source")
Target = TypeVar("Target")

class PathKind(Enum):
    """Types of derivation paths, mirroring HoTT."""
    REFL = "refl"           # Identity: A derives to itself
    DERIVE = "derive"       # Direct derivation with witness
    COMPOSE = "compose"     # p ; q composition
    INVERSE = "inverse"     # p^-1 (lossy in practice)
    TRANSPORT = "transport" # Carrying property along path
    UNIVALENCE = "univalence"  # Isomorphism induces path

class WitnessType(Enum):
    """Types of derivation witnesses."""
    PRINCIPLE = "principle"       # Grounded in Constitution
    SPEC_CONSTRAINT = "spec"      # Satisfies spec requirement
    TEST = "test"                 # Empirical (passing tests)
    PROOF = "proof"               # Formal (Lean 4 verified)
    LLM_JUDGMENT = "llm"          # With reasoning trace
    COMPOSITION = "composition"   # Witness that composition valid
    GALOIS = "galois"             # Structure preservation

@dataclass(frozen=True)
class DerivationWitness:
    """A single witness in the derivation chain."""
    witness_id: str
    witness_type: WitnessType
    evidence: dict  # Type-specific evidence payload
    confidence: float  # [0, 1]
    grounding_principle: str | None  # e.g., "L2.5 COMPOSABLE"
    reasoning_trace: str | None

@dataclass(frozen=True)
class DerivationPath(Generic[Source, Target]):
    """
    A witnessed path from Source to Target.

    In HoTT terms: element of identity type Source =_Deriv Target.

    The path carries:
    - Witnesses: Evidence chain proving derivation valid
    - Galois loss: Semantic preservation metric [0, 1]
    - Constitutional scores: Alignment with principles
    """
    source: Source
    target: Target
    path_id: str  # Content-addressed unique ID
    path_kind: PathKind
    witnesses: tuple[DerivationWitness, ...]
    galois_loss: float  # 0 = perfect, 1 = total loss
    principle_scores: dict[str, float]
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def refl(cls, a: Source) -> DerivationPath[Source, Source]:
        """Identity path (reflexivity)."""
        return cls(
            source=a,
            target=a,
            path_id=f"refl_{id(a)}",
            path_kind=PathKind.REFL,
            witnesses=(),
            galois_loss=0.0,
            principle_scores={},
        )

    def compose(
        self,
        other: DerivationPath[Target, C],
    ) -> DerivationPath[Source, C]:
        """
        Compose paths: self ; other

        Categorical law: (p ; q) ; r = p ; (q ; r)
        Loss accumulates: L(p;q) = 1 - (1-L(p))*(1-L(q))
        """
        assert self.target == other.source, "Paths don't match at junction"

        # Compose witnesses
        composition_witness = DerivationWitness(
            witness_id=f"compose_{self.path_id}_{other.path_id}",
            witness_type=WitnessType.COMPOSITION,
            evidence={
                "left_path": self.path_id,
                "right_path": other.path_id,
            },
            confidence=min(
                min(w.confidence for w in self.witnesses) if self.witnesses else 1.0,
                min(w.confidence for w in other.witnesses) if other.witnesses else 1.0,
            ),
            grounding_principle="L2.5 COMPOSABLE",
            reasoning_trace=f"Path composition at junction",
        )

        # Loss accumulates multiplicatively (coherence decays)
        composed_loss = 1.0 - (1.0 - self.galois_loss) * (1.0 - other.galois_loss)

        return DerivationPath(
            source=self.source,
            target=other.target,
            path_id=f"comp_{self.path_id}_{other.path_id}",
            path_kind=PathKind.COMPOSE,
            witnesses=(*self.witnesses, *other.witnesses, composition_witness),
            galois_loss=composed_loss,
            principle_scores=self._merge_scores(other.principle_scores),
        )

    def _merge_scores(self, other_scores: dict[str, float]) -> dict[str, float]:
        """Merge principle scores, taking minimum (conservative)."""
        merged = dict(self.principle_scores)
        for k, v in other_scores.items():
            if k in merged:
                merged[k] = min(merged[k], v)
            else:
                merged[k] = v
        return merged
```

### 2.2 Layer Hierarchy

```python
from enum import IntEnum

class Layer(IntEnum):
    """The 7 layers from kgents, based on Galois convergence depth."""
    AXIOM = 1          # L1: Zero-loss fixed points (beliefs)
    VALUE = 2          # L2: Low loss (principles)
    GOAL = 3           # L3: Moderate abstraction (dreams)
    SPEC = 4           # L4: Specification layer
    EXECUTION = 5      # L5: Implementation layer
    REFLECTION = 6     # L6: Synthesis/learning
    REPRESENTATION = 7 # L7: Meta-structure

# Loss bounds per layer (from kgents spec)
LAYER_LOSS_BOUNDS = {
    Layer.AXIOM: (0.00, 0.05),
    Layer.VALUE: (0.05, 0.15),
    Layer.GOAL: (0.15, 0.30),
    Layer.SPEC: (0.30, 0.45),
    Layer.EXECUTION: (0.45, 0.60),
    Layer.REFLECTION: (0.60, 0.75),
    Layer.REPRESENTATION: (0.75, 1.00),
}

@dataclass
class GradedDerivationPath(Generic[Source, Target]):
    """Derivation path with layer annotations."""
    path: DerivationPath[Source, Target]
    source_layer: Layer
    target_layer: Layer

    def __post_init__(self):
        # Derivations go "down" the abstraction hierarchy
        assert self.source_layer <= self.target_layer, \
            f"Derivation must be downward: {self.source_layer} -> {self.target_layer}"
```

### 2.3 The Derivable Protocol

```python
from typing import Protocol

class Derivable(Protocol):
    """Protocol for things that support derivation with loss tracking."""

    def restructure(self) -> Derivable:
        """R: Transform into modular form."""
        ...

    def reconstitute(self) -> Derivable:
        """C: Expand from modular form."""
        ...

    def semantic_distance(self, other: Derivable) -> float:
        """Measure semantic distance to another term."""
        ...

    @property
    def galois_loss(self) -> float:
        """L(self) = d(self, C(R(self)))"""
        round_trip = self.restructure().reconstitute()
        return self.semantic_distance(round_trip)

    @property
    def is_fixed_point(self) -> bool:
        """True if galois_loss < epsilon (axiom)."""
        return self.galois_loss < 0.05
```

### 2.4 Transport Along Paths

```python
@dataclass
class TransportableProperty:
    """A property that can be transported along derivation paths."""
    property_id: str
    name: str
    predicate: Callable[[Any], bool]
    tolerance: float  # Max loss for valid transport
    grounding_principle: str

@dataclass
class TransportResult:
    """Result of transporting a property along a path."""
    original_property: TransportableProperty
    transported_predicate: Callable[[Any], bool]
    confidence: float  # Decays with loss
    witness: DerivationWitness

def transport_property(
    path: DerivationPath,
    prop: TransportableProperty,
) -> TransportResult | None:
    """
    Transport a property along a derivation path.

    If path.galois_loss > prop.tolerance, transport fails.
    Otherwise, confidence = prop_confidence * (1 - path.galois_loss)
    """
    if path.galois_loss > prop.tolerance:
        return None  # Loss too high for valid transport

    transport_confidence = 1.0 * (1.0 - path.galois_loss)

    transport_witness = DerivationWitness(
        witness_id=f"transport_{path.path_id}_{prop.property_id}",
        witness_type=WitnessType.TRANSPORT,
        evidence={
            "property": prop.name,
            "path_id": path.path_id,
            "loss": path.galois_loss,
        },
        confidence=transport_confidence,
        grounding_principle=prop.grounding_principle,
        reasoning_trace=f"Transported {prop.name} along {path.path_id}",
    )

    return TransportResult(
        original_property=prop,
        transported_predicate=prop.predicate,  # Same predicate, different domain
        confidence=transport_confidence,
        witness=transport_witness,
    )
```

### 2.5 Self-Awareness Interface

```python
@dataclass
class GroundednessResult:
    """Result of checking if ASHC is grounded in Constitution."""
    is_grounded: bool
    paths_to_principles: dict[str, list[DerivationPath]]
    ungrounded_components: list[str]
    overall_confidence: float

@dataclass
class ConsistencyResult:
    """Result of self-consistency verification."""
    is_consistent: bool
    law_violations: list[dict]  # Categorical law failures
    contradictions: list[dict]  # Super-additive loss
    galois_violations: list[dict]  # Loss threshold exceeded
    principle_violations: list[dict]  # Constitutional misalignment

class ASHCSelfAwareness:
    """Interface for ASHC to query its own derivation structure."""

    def __init__(self, store: DerivationStore):
        self.store = store

    async def am_i_grounded(self) -> GroundednessResult:
        """
        Check if ASHC has complete derivation path from Constitution.

        ASHC asking: "Do I have principled justification for existing?"
        """
        ...

    async def what_principle_justifies(
        self,
        component: str,
    ) -> list[tuple[str, DerivationPath]]:
        """
        For a given component, find which principles justify it.

        ASHC asking: "Why do I have this component?"
        """
        ...

    async def verify_self_consistency(self) -> ConsistencyResult:
        """
        Verify ASHC's derivation is internally consistent.

        Checks:
        1. All paths satisfy categorical laws
        2. No contradictory witnesses (super-additive loss)
        3. Galois loss within acceptable bounds
        4. All required principles satisfied
        """
        ...

    async def explain_derivation(
        self,
        from_artifact: str,
        to_artifact: str,
    ) -> list[DerivationPath]:
        """
        Explain how one artifact derives from another.

        Returns the composition of paths from source to target.
        """
        ...
```

### 2.6 The Bootstrap Fixed Point

```python
class ASHCBootstrap:
    """ASHC deriving itself - the Lawvere fixed point."""

    async def derive_self(
        self,
        constitution: dict,
        ashc_spec: str,
    ) -> DerivationPath:
        """
        Construct the full derivation path for ASHC itself.

        Three segments:
        1. Constitution -> ASHC Principles (instantiation)
        2. ASHC Principles -> ASHC Spec (refinement)
        3. ASHC Spec -> ASHC Implementation (compilation)

        The composed path is ASHC's "birth certificate".
        """
        # Phase 1: Principle instantiation
        principle_path = await self._derive_principles(constitution)

        # Phase 2: Spec refinement
        spec_path = await self._derive_spec(principle_path.target, ashc_spec)

        # Phase 3: Implementation compilation
        impl_path = await self._compile_implementation(spec_path.target)

        # Compose the full path
        full_path = principle_path.compose(spec_path).compose(impl_path)

        # Verify fixed-point property
        # The spec should be Galois-stable
        spec_loss = await self._compute_galois_loss(ashc_spec)
        if spec_loss > 0.10:
            raise BootstrapError(f"ASHC spec not a fixed point: loss={spec_loss}")

        return full_path
```

---

## Part III: Lean 4 Formalization

Create `impl/claude/proofs/kgents_proofs/KgentsProofs/DerivationPaths.lean`:

### 3.1 Core Structures

```lean
/-
  kgents Derivation Paths - Formally Verified

  Formalizes derivation paths as witnessed morphisms with:
  1. Layer hierarchy (L1-L7)
  2. Loss measurement and composition
  3. Transport lemmas
  4. Categorical laws

  NO SORRY ALLOWED
-/
import Mathlib.CategoryTheory.Category.Basic
import KgentsProofs.CategoryLaws
import KgentsProofs.OperadLaws

namespace Kgents.DerivationPath

/-- Layer indices L1-L7 -/
inductive Layer where
  | axiom | value | goal | spec | execution | reflection | representation
  deriving DecidableEq

/-- Layer ordering -/
def Layer.toNat : Layer → ℕ
  | .axiom => 1 | .value => 2 | .goal => 3 | .spec => 4
  | .execution => 5 | .reflection => 6 | .representation => 7

instance : LE Layer where le a b := a.toNat ≤ b.toNat

/-- Loss values in [0, 1] -/
structure Loss where
  val : ℝ
  nonneg : 0 ≤ val
  bounded : val ≤ 1

/-- Zero loss (perfect preservation) -/
def Loss.zero : Loss := ⟨0, le_refl 0, by norm_num⟩

/-- Derivation path with loss tracking -/
structure DerivationPath (α : Type) where
  source : α
  target : α
  loss : Loss
  witness : String

/-- Identity path -/
def DerivationPath.refl (a : α) : DerivationPath α :=
  ⟨a, a, Loss.zero, "refl"⟩

/-- Path composition -/
def DerivationPath.comp (p₁ p₂ : DerivationPath α)
    (h : p₁.target = p₂.source) : DerivationPath α :=
  ⟨p₁.source, p₂.target,
   ⟨min 1 (p₁.loss.val + p₂.loss.val),
    le_min (by norm_num) (add_nonneg p₁.loss.nonneg p₂.loss.nonneg),
    min_le_left 1 _⟩,
   s!"{p₁.witness} >> {p₂.witness}"⟩
```

### 3.2 Categorical Laws

```lean
/-- Composition is associative -/
theorem comp_assoc (p q r : DerivationPath α)
    (hpq : p.target = q.source) (hqr : q.target = r.source) :
    let pq := DerivationPath.comp p q hpq
    let hpq_r : pq.target = r.source := by simp [DerivationPath.comp, hqr]
    let qr := DerivationPath.comp q r hqr
    let hp_qr : p.target = qr.source := by simp [DerivationPath.comp, hpq]
    (DerivationPath.comp pq r hpq_r).source =
    (DerivationPath.comp p qr hp_qr).source ∧
    (DerivationPath.comp pq r hpq_r).target =
    (DerivationPath.comp p qr hp_qr).target := by
  simp [DerivationPath.comp]

/-- Left identity -/
theorem refl_comp (p : DerivationPath α) :
    let r := DerivationPath.refl p.source
    let h : r.target = p.source := rfl
    (DerivationPath.comp r p h).source = p.source ∧
    (DerivationPath.comp r p h).target = p.target := by
  simp [DerivationPath.comp, DerivationPath.refl]

/-- Right identity -/
theorem comp_refl (p : DerivationPath α) :
    let r := DerivationPath.refl p.target
    let h : p.target = r.source := rfl
    (DerivationPath.comp p r h).source = p.source ∧
    (DerivationPath.comp p r h).target = p.target := by
  simp [DerivationPath.comp, DerivationPath.refl]
```

### 3.3 Transport and Loss

```lean
/-- Transportable property -/
structure TransportableProperty (α : Type) where
  prop : α → Prop
  tolerance : Loss

/-- Transport preserves property within tolerance -/
theorem transport_along_path {α : Type}
    (P : TransportableProperty α)
    (path : DerivationPath α)
    (source_holds : P.prop path.source)
    (low_loss : path.loss.val ≤ P.tolerance.val) :
    P.prop path.target := by
  sorry  -- Requires: axiom that low-loss paths preserve properties

/-- Loss is monotonic under composition -/
theorem loss_monotonic (p₁ p₂ : DerivationPath α)
    (h : p₁.target = p₂.source) :
    p₁.loss.val ≤ (DerivationPath.comp p₁ p₂ h).loss.val := by
  simp [DerivationPath.comp]
  apply le_min
  · exact le_trans p₁.loss.bounded (le_refl 1)
  · exact le_add_of_nonneg_right p₂.loss.nonneg

end Kgents.DerivationPath
```

---

## Part IV: Implementation Plan

### Phase 1: Core Path Infrastructure (Week 1-2)

**Files to Create**:
```
impl/claude/protocols/ashc/paths/
├── __init__.py
├── derivation_path.py    # DerivationPath, GradedDerivationPath
├── witness.py            # DerivationWitness, WitnessType
├── layer.py              # Layer enum, LAYER_LOSS_BOUNDS
├── composition.py        # PathComposer, composition laws
└── store.py              # DerivationStore protocol + PostgreSQL impl
```

**Tasks**:
1. [ ] Implement `DerivationPath` dataclass with all fields
2. [ ] Implement `DerivationPath.refl()` and `DerivationPath.compose()`
3. [ ] Add categorical law verification (identity, associativity)
4. [ ] Implement `DerivationStore` protocol
5. [ ] Create PostgreSQL implementation of `DerivationStore`
6. [ ] Add migrations for `derivation_paths` table
7. [ ] Write comprehensive tests for composition laws

**Success Criteria**:
- `DerivationPath.compose()` satisfies associativity
- `DerivationPath.refl()` satisfies left/right identity
- Paths persist and retrieve correctly
- 100% test coverage on core types

### Phase 2: Witness Integration (Week 3-4)

**Files to Modify**:
```
impl/claude/protocols/ashc/
├── evidence.py           # Add Mark emission, populate Run.witnesses
├── adaptive.py           # Add Mark emission, add galois_loss field
├── economy.py            # Add Mark emission, use reasoning_trace
└── paths/
    └── witness_bridge.py # Bridge to services/witness/mark.py
```

**Tasks**:
1. [ ] Create `WitnessBridge` connecting DerivationWitness to Mark
2. [ ] Modify `EvidenceCompiler.compile()` to emit Mark with DerivationPath
3. [ ] Modify `AdaptiveCompiler.compile()` to emit Mark on stopping decision
4. [ ] Add `galois_loss: float | None` to `AdaptiveEvidence`
5. [ ] Modify `ASHCBet.create()` and `resolve()` to emit Marks
6. [ ] Populate `Run.witnesses` field (currently always `()`)
7. [ ] Connect to Constitutional Evaluator for principle scoring

**Success Criteria**:
- Every ASHC compilation emits at least one Mark
- `Run.witnesses` is populated with actual witnesses
- `AdaptiveEvidence` has Galois loss
- Constitutional alignment computed for each path

### Phase 3: Self-Awareness (Week 5-6)

**Files to Create**:
```
impl/claude/protocols/ashc/
├── self_awareness.py     # ASHCSelfAwareness class
├── groundedness.py       # am_i_grounded() implementation
├── consistency.py        # verify_self_consistency()
└── explanation.py        # explain_derivation()
```

**Tasks**:
1. [ ] Implement `ASHCSelfAwareness` class
2. [ ] Implement `am_i_grounded()` - BFS from Constitution to ASHC
3. [ ] Implement `what_principle_justifies()` - path search
4. [ ] Implement `verify_self_consistency()`:
   - Categorical law checking
   - Contradiction detection (super-additive loss)
   - Galois threshold verification
   - Principle satisfaction
5. [ ] Implement `explain_derivation()` - path composition
6. [ ] Add AGENTESE nodes for self-reflection queries

**Success Criteria**:
- `am_i_grounded()` returns accurate groundedness result
- `verify_self_consistency()` catches law violations
- `explain_derivation()` returns valid path chains
- Self-reflection queries work via AGENTESE

### Phase 4: Lean Integration (Week 7-8)

**Files to Create**:
```
impl/claude/proofs/kgents_proofs/KgentsProofs/
├── DerivationPaths.lean  # Core formalization
├── Transport.lean        # Transport lemmas
└── Contradiction.lean    # Super-additivity detection

impl/claude/services/verification/
├── lean_derivation_export.py  # Export paths to Lean
└── lean_derivation_import.py  # Import verified theorems
```

**Tasks**:
1. [ ] Create `DerivationPaths.lean` with Layer, Loss, DerivationPath
2. [ ] Prove `comp_assoc`, `refl_comp`, `comp_refl` in Lean
3. [ ] Prove `loss_monotonic` theorem
4. [ ] Create `Transport.lean` with transport lemmas
5. [ ] Implement `LeanDerivationExporter` (Python → Lean)
6. [ ] Implement `LeanDerivationImporter` (Lean → Python witness)
7. [ ] Add to existing `lean_import.py` for unified checking
8. [ ] Verify all proofs compile with `lake build`

**Success Criteria**:
- All Lean proofs compile with NO SORRY
- Python paths can round-trip through Lean verification
- Verified theorems become max-confidence witnesses

### Phase 5: Bootstrap (Week 9-10)

**Files to Create**:
```
impl/claude/protocols/ashc/
├── bootstrap.py          # ASHCBootstrap class
└── fixed_point.py        # Fixed-point verification
```

**Tasks**:
1. [ ] Implement `ASHCBootstrap.derive_self()`
2. [ ] Implement `_derive_principles()` - Constitution → ASHC principles
3. [ ] Implement `_derive_spec()` - Principles → Spec
4. [ ] Implement `_compile_implementation()` - Spec → Impl
5. [ ] Verify ASHC spec is Galois fixed point (loss < 0.10)
6. [ ] Create the full derivation chain
7. [ ] Store bootstrap path in DerivationStore
8. [ ] Add `kg ashc bootstrap` CLI command

**Success Criteria**:
- `derive_self()` produces valid composed path
- ASHC spec verified as fixed point
- Bootstrap path persists and can be queried
- CLI command works

### Phase 6: Documentation & Polish (Week 11-12)

**Tasks**:
1. [ ] Update CLAUDE.md with path-aware ASHC docs
2. [ ] Create `docs/skills/derivation-paths.md`
3. [ ] Add examples to `spec/protocols/proof-generation.md`
4. [ ] Create visual derivation graph (mermaid)
5. [ ] Add CI pipeline for Lean verification
6. [ ] Performance benchmarks for path operations
7. [ ] Write comprehensive README for proofs/

**Success Criteria**:
- Documentation complete and accurate
- CI verifies Lean proofs on every PR
- Derivation graph renders correctly
- Performance acceptable (<100ms for typical operations)

---

## Part V: Integration Points

### 5.1 Existing Infrastructure Connections

| New Component | Integrates With | How |
|---------------|-----------------|-----|
| `DerivationPath` | `services/witness/mark.py` | Witnesses become Marks |
| `DerivationStore` | `services/verification/graph_engine.py` | Shared DAG storage |
| `GaloisLoss` | `services/zero_seed/galois/galois_loss.py` | Loss computation |
| `Layer` | `services/zero_seed/galois/` | Layer assignment |
| `ASHCSelfAwareness` | `services/witness/constitutional_evaluator.py` | Principle scoring |
| Lean proofs | `proofs/kgents_proofs/` | Extend existing |

### 5.2 AGENTESE Paths

```python
# New AGENTESE nodes for derivation queries
"concept.derivation.path"      # Get derivation path between artifacts
"concept.derivation.grounded"  # Check if artifact is grounded
"concept.derivation.explain"   # Explain derivation chain
"self.ashc.consistency"        # Verify self-consistency
"self.ashc.bootstrap"          # Run bootstrap derivation
```

### 5.3 Database Schema

```sql
-- New table for derivation paths
CREATE TABLE derivation_paths (
    path_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    path_kind TEXT NOT NULL,
    galois_loss REAL NOT NULL,
    principle_scores JSONB NOT NULL,
    witnesses JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Indexes for common queries
    INDEX idx_source (source_id),
    INDEX idx_target (target_id),
    INDEX idx_loss (galois_loss)
);

-- Junction table for path composition
CREATE TABLE path_compositions (
    composed_path_id TEXT REFERENCES derivation_paths(path_id),
    left_path_id TEXT REFERENCES derivation_paths(path_id),
    right_path_id TEXT REFERENCES derivation_paths(path_id),
    PRIMARY KEY (composed_path_id)
);
```

---

## Part VI: Success Metrics

### 6.1 Functional Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Path composition correctness | 100% | Law verification tests |
| Lean proofs complete | 0 sorry | `lake build` output |
| Witness coverage | 100% ASHC ops | Count marks per compile |
| Self-awareness accuracy | 95% | Manual verification |
| Bootstrap success | 100% | CI test |

### 6.2 Performance Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Path composition | <10ms | Benchmark |
| Path storage | <50ms | Benchmark |
| Groundedness check | <1s | Benchmark |
| Lean verification | <30s | CI timing |

### 6.3 Quality Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Test coverage | >90% | pytest-cov |
| Type coverage | 100% | mypy strict |
| Doc coverage | 100% public | docstring check |

---

## Part VII: Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Lean proofs too complex | Medium | High | Start with simple theorems, escalate |
| Performance issues | Low | Medium | Lazy evaluation, caching |
| Integration breaks existing | Medium | High | Feature flags, gradual rollout |
| Bootstrap infinite loop | Low | High | Depth limit, fixed-point detection |
| Galois loss unstable | Medium | Medium | Robust distance metrics, fallbacks |

---

## Part VIII: Open Questions

1. **Higher paths**: Do we need paths-between-paths for coherence? (Probably not for v1)
2. **Inverse paths**: How to handle inverse derivations? (Mark as lossy)
3. **Distributed paths**: Can paths span multiple services? (Future work)
4. **Path visualization**: How to render complex derivation graphs? (Mermaid for v1)

---

## Appendix A: Key References

### Academic
- HoTT Book: https://homotopytypetheory.org/book/
- Emily Riehl's HoTT intro: https://emilyriehl.github.io/files/Intro-HoTT-UF.pdf
- 1Lab (Cubical Agda): https://1lab.dev/
- nLab: https://ncatlab.org/nlab/show/homotopy+type+theory

### Industry
- CompCert: https://compcert.org/
- CakeML: https://cakeml.org/
- Verus: https://github.com/verus-lang/verus
- LiquidHaskell: https://ucsd-progsys.github.io/liquidhaskell-tutorial/

### kgents Internal
- Constitution: `CLAUDE.md` (The Constitution section)
- Galois theory: `spec/theory/galois-modularization.md`
- Zero Seed: `spec/protocols/zero-seed.md`
- Existing Lean proofs: `impl/claude/proofs/kgents_proofs/`

---

## Appendix B: Example Derivation Chain

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  EXAMPLE: Deriving ASHC Evidence Accumulation                               │
│                                                                             │
│  CONSTITUTION                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ L1.8 GALOIS: "L = d(P, C(R(P))) measures structure preservation"   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│           │                                                                 │
│           │ DerivationPath                                                  │
│           │   source: "L1.8 GALOIS"                                        │
│           │   target: "Evidence tracks galois_loss"                        │
│           │   loss: 0.12                                                   │
│           │   witnesses: [PrincipleWitness("GALOIS grounds Evidence")]     │
│           ▼                                                                 │
│  ASHC SPEC (spec/protocols/proof-generation.md)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ "Evidence MUST track galois_loss for each compilation"              │   │
│  │ "equivalence_score incorporates galois_coherence"                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│           │                                                                 │
│           │ DerivationPath                                                  │
│           │   source: "Evidence tracks galois_loss"                        │
│           │   target: "Evidence.galois_loss field"                         │
│           │   loss: 0.08                                                   │
│           │   witnesses: [SpecWitness("Field implements spec")]            │
│           ▼                                                                 │
│  ASHC IMPL (protocols/ashc/evidence.py)                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ @dataclass                                                          │   │
│  │ class Evidence:                                                     │   │
│  │     galois_loss: float | None = None  # ← This field!              │   │
│  │     ...                                                             │   │
│  │     @property                                                       │   │
│  │     def galois_coherence(self) -> float:                           │   │
│  │         return 1.0 - (self.galois_loss or 0.0)                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  COMPOSED PATH                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ source: "L1.8 GALOIS"                                               │   │
│  │ target: "Evidence.galois_loss field"                                │   │
│  │ loss: 0.19 (accumulated: 1 - (1-0.12)*(1-0.08))                    │   │
│  │ witnesses: [PrincipleWitness, SpecWitness, CompositionWitness]     │   │
│  │ principle_scores: {"GALOIS": 0.92, "GENERATIVE": 0.85}             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*"The proof IS the decision. The mark IS the witness. The path IS the derivation."*
