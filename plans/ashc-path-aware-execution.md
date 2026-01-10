# ASHC Path-Aware Rewrite: Parallel Execution Plan

**Status**: READY FOR EXECUTION
**Created**: 2025-01-10
**Orchestrator**: Claude + Kent
**Philosophy**: "Depth over breadth. Radical, transformative improvement."

---

## Executive Summary

Transform the ASHC planning document into reality through **5 parallel workstreams** that can execute concurrently, converging at key integration points.

**The Radical Insight**: The infrastructure already exists but is **disconnected**:
- Galois loss computation: ✅ Production-ready
- Constitutional evaluator: ✅ Production-ready
- 35 Lean theorems: ✅ Verified, NO SORRY
- ASHC evidence system: ✅ Exists
- **But**: `Run.witnesses = ()` always. Zero marks emitted. No paths tracked.

**The Transformation**: Connect these existing systems through DerivationPath as the **universal witness carrier**.

---

## Parallel Workstream Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ASHC PATH-AWARE ORCHESTRATION                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  WORKSTREAM A              WORKSTREAM B              WORKSTREAM C               │
│  ═════════════            ═════════════             ═════════════              │
│  Core Types               Witness Bridge            Lean Formalization          │
│  (Pure Python)            (Integration)             (Formal Proofs)             │
│                                                                                 │
│  ┌───────────┐            ┌───────────┐             ┌───────────┐              │
│  │ Derivation │            │ ASHC Mark │             │ Derivation │              │
│  │ Path Types │────────────│ Emission  │─────────────│ Paths.lean │              │
│  └───────────┘            └───────────┘             └───────────┘              │
│       │                        │                          │                     │
│       │                        │                          │                     │
│       ▼                        ▼                          ▼                     │
│  ┌───────────┐            ┌───────────┐             ┌───────────┐              │
│  │Composition│            │ Run.wit   │             │ Transport │              │
│  │   Laws    │────────────│ =witnesses│─────────────│  Lemmas   │              │
│  └───────────┘            └───────────┘             └───────────┘              │
│       │                        │                          │                     │
│       └────────────────────────┼──────────────────────────┘                     │
│                                │                                                │
│                                ▼                                                │
│                     ╔═════════════════════╗                                     │
│                     ║  INTEGRATION POINT  ║                                     │
│                     ║    (Phase Gate)     ║                                     │
│                     ╚═════════════════════╝                                     │
│                                │                                                │
│           ┌────────────────────┼────────────────────┐                           │
│           │                    │                    │                           │
│           ▼                    ▼                    ▼                           │
│  WORKSTREAM D              WORKSTREAM E                                         │
│  ═════════════            ═════════════                                        │
│  Self-Awareness           Bootstrap                                             │
│  (Queries)                (Fixed Point)                                         │
│                                                                                 │
│  ┌───────────┐            ┌───────────┐                                        │
│  │am_i_grounded│           │ derive_self │                                       │
│  │what_justifies│───────────│ constitution│                                       │
│  │verify_cons │           │  → impl    │                                        │
│  └───────────┘            └───────────┘                                        │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Workstream A: Core Types (Using K-Block DAG + D-gent)

**Goal**: Build DerivationPath type system USING existing K-block DAG infrastructure
**Dependencies**: None (can start immediately)
**Parallelizable**: YES

**Key Principle**: Don't reinvent—REUSE. K-Block's `DerivationDAG` already has:
- Layer monotonicity enforcement (L1→L7)
- `get_lineage()`, `is_grounded()`, `validate_acyclic()`
- Edge confidence scoring via `EdgeDiscoveryService`

### A.1 DerivationPath Core Types (Wrapping K-Block DAG)

**Files to Create**:
```
impl/claude/protocols/ashc/paths/
├── __init__.py
├── types.py           # DerivationPath wrapping K-Block's DerivationDAG
├── witness.py         # DerivationWitness (stores as SelfJustifyingCrystal)
└── composition.py     # compose() using K-Block's validated operations
```

**Files to REUSE (not recreate)**:
```
impl/claude/services/k_block/core/derivation.py  # DerivationDAG, DerivationNode
impl/claude/agents/d/crystal/self_justifying.py  # SelfJustifyingCrystal for proofs
impl/claude/services/derivation/service.py       # DerivationChain, CrystalRef
```

**Key Deliverables**:
- [ ] `DerivationPath[Source, Target]` generic dataclass
- [ ] `DerivationWitness` with confidence, grounding_principle, evidence
- [ ] `PathKind` enum: REFL, DERIVE, COMPOSE, TRANSPORT, UNIVALENCE
- [ ] `WitnessType` enum: PRINCIPLE, SPEC, TEST, PROOF, LLM, COMPOSITION, GALOIS
- [ ] `Layer` enum with loss bounds (from existing Galois infra)

**Success Criteria**:
```python
# This must work:
path1 = DerivationPath.derive(constitution, spec, witnesses=[...])
path2 = DerivationPath.derive(spec, impl, witnesses=[...])
composed = path1.compose(path2)

assert composed.source == constitution
assert composed.target == impl
assert composed.galois_loss >= path1.galois_loss  # Loss accumulates
```

### A.2 Composition Laws Verification

**Files to Modify/Create**:
```
impl/claude/protocols/ashc/paths/
├── laws.py            # verify_associativity(), verify_identity()
└── _tests/
    ├── __init__.py
    ├── test_derivation_path.py
    └── test_composition_laws.py
```

**Key Deliverables**:
- [ ] `verify_identity_left(path)` - refl.compose(path) == path
- [ ] `verify_identity_right(path)` - path.compose(refl) == path
- [ ] `verify_associativity(p, q, r)` - (p.q).r == p.(q.r)
- [ ] Property-based tests with hypothesis

**Success Criteria**:
```python
@given(derivation_paths())
def test_associativity(p, q, r):
    # (p ; q) ; r ≡ p ; (q ; r)
    left = p.compose(q).compose(r)
    right = p.compose(q.compose(r))
    assert left.source == right.source
    assert left.target == right.target
    # Loss may differ slightly due to float arithmetic
    assert abs(left.galois_loss - right.galois_loss) < 0.001
```

### A.3 Storage via D-gent Universe + K-Block

**Files to Create**:
```
impl/claude/agents/d/schemas/
└── derivation.py      # DerivationPathCrystal schema for Universe storage
```

**Key Deliverables** (using existing infrastructure):
- [ ] `DerivationPathCrystal` frozen dataclass (Schema contract)
- [ ] Register with Universe: `universe.register_schema(DERIVATION_PATH_SCHEMA)`
- [ ] Store via: `await universe.store(path_crystal, "ashc.derivation_path")`
- [ ] Lineage via K-Block's `DerivationDAG.get_lineage()`

**Storage Pattern** (D-gent, NOT raw SQL):
```python
from agents.d.crystal import Schema, SelfJustifyingCrystal
from agents.d.universe import get_universe

@dataclass(frozen=True)
class DerivationPathCrystal:
    """Frozen contract for DerivationPath persistence."""
    source_id: str
    target_id: str
    path_kind: str  # REFL, DERIVE, COMPOSE, TRANSPORT
    galois_loss: float
    principle_scores: dict[str, float]
    witness_ids: tuple[str, ...]  # References to witness crystals
    kblock_lineage: tuple[str, ...]  # K-Block IDs in derivation chain

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "DerivationPathCrystal": ...

DERIVATION_PATH_SCHEMA = Schema(
    name="ashc.derivation_path",
    version=1,
    contract=DerivationPathCrystal,
    migrations={},
)

# Storage via Universe (automatic backend selection)
async def store_derivation_path(path: DerivationPath) -> str:
    universe = get_universe()
    crystal = DerivationPathCrystal.from_path(path)
    return await universe.store(crystal, "ashc.derivation_path")
```

**Why D-gent over raw SQL**:
- Graceful degradation (Postgres → SQLite → Memory)
- Schema versioning with migrations
- Causal lineage via `Datum.causal_parent`
- Integration with existing Universe infrastructure

---

## Workstream B: Witness Bridge (Integration)

**Goal**: Connect ASHC to existing Witness/Mark infrastructure
**Dependencies**: Workstream A (types)
**Parallelizable**: YES (can start type definitions while A progresses)

### B.1 ASHC Mark Emission

**Files to Modify**:
```
impl/claude/protocols/ashc/
├── evidence.py        # Add Mark emission, populate Run.witnesses
└── paths/
    └── witness_bridge.py  # Bridge DerivationWitness ↔ Mark
```

**Key Changes to evidence.py**:

```python
# BEFORE (current state - line 457-469):
return Run(
    ...
    witnesses=(),  # ← HARDCODED EMPTY
    ...
)

# AFTER:
from services.witness.mark import Mark, MarkStore
from protocols.ashc.paths.witness_bridge import derivation_to_mark

# Collect witnesses during compilation
witnesses: list[TraceWitnessResult] = []
marks_emitted: list[Mark] = []

# ... during each verification step ...
witness = TraceWitnessResult(...)
witnesses.append(witness)

# Create Mark for audit trail
mark = derivation_to_mark(witness, run_context)
marks_emitted.append(mark)
await mark_store.append(mark)

return Run(
    ...
    witnesses=tuple(witnesses),  # ← POPULATED
    ...
)
```

**Key Deliverables**:
- [ ] `WitnessBridge.derivation_to_mark()` - Convert DerivationWitness to Mark
- [ ] `WitnessBridge.mark_to_derivation()` - Convert Mark back (for queries)
- [ ] Modify `EvidenceCompiler.compile()` to emit marks
- [ ] Modify `AdaptiveCompiler.compile()` to emit marks
- [ ] Connect to `MarkConstitutionalEvaluator` for principle scoring

### B.2 Run.witnesses Population

**Files to Modify**:
```
impl/claude/protocols/ashc/
├── evidence.py        # Main compilation logic
├── adaptive.py        # Bayesian sampling - add witness on stopping
└── economy.py         # Economic bets - add witness on resolve
```

**Integration Points**:

1. **Evidence Compilation** - Each run gets witnesses:
   ```python
   # evidence.py: After each verification step
   witness = DerivationWitness(
       witness_id=str(uuid.uuid4()),
       witness_type=WitnessType.TEST if test_passed else WitnessType.LLM,
       evidence={"test_results": verification.test_report},
       confidence=0.95 if all_passed else 0.6,
       grounding_principle="L2.5 COMPOSABLE" if composable else None,
       reasoning_trace=f"Verified {len(tests)} tests"
   )
   ```

2. **Adaptive Stopping** - Decision gets witnessed:
   ```python
   # adaptive.py: When stopping decision made
   witness = DerivationWitness(
       witness_type=WitnessType.LLM,
       evidence={"stopping_reason": "convergence", "samples": n},
       confidence=posterior_confidence,
       reasoning_trace=f"Stopped after {n} samples, P(success)={prob}"
   )
   ```

3. **Economic Resolution** - Bet outcomes witnessed:
   ```python
   # economy.py: When bet resolved
   witness = DerivationWitness(
       witness_type=WitnessType.COMPOSITION,
       evidence={"bet_id": bet.id, "outcome": outcome},
       confidence=1.0 if outcome == "success" else 0.0,
       reasoning_trace=f"Bet resolved: {outcome}"
   )
   ```

### B.3 Constitutional Integration

**Files to Modify**:
```
impl/claude/protocols/ashc/paths/
└── constitutional_bridge.py  # Connect to Constitutional Evaluator
```

**Key Deliverables**:
- [ ] `score_path_constitutional(path)` - Get principle scores for path
- [ ] Integrate existing `MarkConstitutionalEvaluator`
- [ ] Compute Galois loss using existing `compute_galois_loss_async()`
- [ ] Tier assignment using existing `classify_evidence_tier()`

**Integration**:
```python
from services.witness.constitutional_evaluator import MarkConstitutionalEvaluator

async def enrich_path_with_constitutional(
    path: DerivationPath,
    evaluator: MarkConstitutionalEvaluator,
) -> DerivationPath:
    """Add constitutional alignment to derivation path."""
    # Convert path witnesses to marks
    marks = [witness_to_mark(w) for w in path.witnesses]

    # Evaluate each mark
    alignments = [await evaluator.evaluate(m) for m in marks]

    # Aggregate principle scores (conservative - take minimum)
    principle_scores = aggregate_scores(alignments)

    # Compute overall Galois loss
    galois_loss = await compute_galois_loss_async(path_content(path))

    return path._replace(
        galois_loss=galois_loss,
        principle_scores=principle_scores,
    )
```

---

## Workstream C: Lean Formalization

**Goal**: Formal verification of DerivationPath laws in Lean 4
**Dependencies**: None (can start immediately)
**Parallelizable**: YES

### C.1 DerivationPaths.lean

**Files to Create**:
```
impl/claude/proofs/kgents_proofs/KgentsProofs/
├── DerivationPaths.lean   # Core types and laws
├── Transport.lean         # Transport lemmas
└── LossMonotonicity.lean  # Loss accumulation proofs
```

**DerivationPaths.lean Structure**:
```lean
/-
  kgents DerivationPaths - Formally Verified

  This module proves:
  1. Path composition is associative
  2. Identity paths satisfy left/right identity
  3. Loss is monotonic under composition
  4. Transport preserves properties within tolerance

  NO SORRY ALLOWED
-/
import Mathlib.CategoryTheory.Category.Basic
import KgentsProofs.CategoryLaws
import KgentsProofs.OperadLaws

namespace Kgents.DerivationPath

/-- The 7 layers from Galois convergence depth -/
inductive Layer where
  | axiom | value | goal | spec | execution | reflection | representation
  deriving DecidableEq, Repr

/-- Layer ordering (lower = more abstract) -/
def Layer.toNat : Layer → ℕ
  | .axiom => 1 | .value => 2 | .goal => 3 | .spec => 4
  | .execution => 5 | .reflection => 6 | .representation => 7

instance : LE Layer where le a b := a.toNat ≤ b.toNat

/-- Loss value in [0,1] -/
structure Loss where
  val : ℝ
  nonneg : 0 ≤ val
  bounded : val ≤ 1

/-- Zero loss (perfect preservation) -/
def Loss.zero : Loss := ⟨0, le_refl 0, by norm_num⟩

/-- Add losses (capped at 1) -/
def Loss.add (a b : Loss) : Loss :=
  ⟨min 1 (a.val + b.val),
   le_min (by norm_num) (add_nonneg a.nonneg b.nonneg),
   min_le_left 1 _⟩

/-- Derivation path with loss tracking -/
structure Path (α : Type) where
  source : α
  target : α
  loss : Loss
  witness : String

/-- Identity path (reflexivity) -/
def Path.refl (a : α) : Path α :=
  ⟨a, a, Loss.zero, "refl"⟩

/-- Path composition -/
def Path.comp (p₁ p₂ : Path α) (h : p₁.target = p₂.source) : Path α :=
  ⟨p₁.source, p₂.target, Loss.add p₁.loss p₂.loss,
   s!"{p₁.witness} >> {p₂.witness}"⟩

end Kgents.DerivationPath
```

### C.2 Categorical Law Proofs

**Key Theorems to Prove**:
```lean
namespace Kgents.DerivationPath

/-- Composition is associative -/
theorem comp_assoc (p q r : Path α)
    (hpq : p.target = q.source) (hqr : q.target = r.source) :
    let pq := Path.comp p q hpq
    let hpq_r : pq.target = r.source := by simp [Path.comp, hqr]
    let qr := Path.comp q r hqr
    let hp_qr : p.target = qr.source := by simp [Path.comp, hpq]
    (Path.comp pq r hpq_r).source = (Path.comp p qr hp_qr).source ∧
    (Path.comp pq r hpq_r).target = (Path.comp p qr hp_qr).target := by
  simp [Path.comp]

/-- Left identity: refl ; p = p -/
theorem refl_comp (p : Path α) :
    let r := Path.refl p.source
    let h : r.target = p.source := rfl
    (Path.comp r p h).source = p.source ∧
    (Path.comp r p h).target = p.target := by
  simp [Path.comp, Path.refl]

/-- Right identity: p ; refl = p -/
theorem comp_refl (p : Path α) :
    let r := Path.refl p.target
    let h : p.target = r.source := rfl
    (Path.comp p r h).source = p.source ∧
    (Path.comp p r h).target = p.target := by
  simp [Path.comp, Path.refl]

/-- Loss is monotonic under composition -/
theorem loss_monotonic (p₁ p₂ : Path α) (h : p₁.target = p₂.source) :
    p₁.loss.val ≤ (Path.comp p₁ p₂ h).loss.val := by
  simp [Path.comp, Loss.add]
  apply le_min
  · exact le_trans p₁.loss.bounded (le_refl 1)
  · exact le_add_of_nonneg_right p₂.loss.nonneg

end Kgents.DerivationPath
```

### C.3 Python-Lean Bridge

**Files to Modify**:
```
impl/claude/services/verification/
├── lean_export.py     # Add DerivationPath export
└── lean_import.py     # Add DerivationPath theorem import
```

**Export Function**:
```python
def export_derivation_path(path: DerivationPath) -> str:
    """Generate Lean representation of a derivation path."""
    return f"""
def {path.path_id} : Kgents.DerivationPath.Path String :=
  ⟨"{path.source}", "{path.target}",
   ⟨{path.galois_loss}, by norm_num, by norm_num⟩,
   "{path.path_kind.value}"⟩
"""
```

**Import Verification**:
```python
async def verify_path_laws(path: DerivationPath) -> VerificationResult:
    """Verify that a path satisfies categorical laws via Lean."""
    # Generate Lean file with path and law applications
    lean_code = generate_path_verification(path)

    # Run lake build
    result = await run_lake_build(lean_code)

    if result.success:
        return VerificationResult(
            verified=True,
            witness=DerivationWitness(
                witness_type=WitnessType.PROOF,
                evidence={"lean_theorem": result.theorem_name},
                confidence=1.0,  # Categorical - no decay
                grounding_principle="CATEGORICAL",
            )
        )
```

---

## Workstream D: Self-Awareness Interface

**Goal**: Enable ASHC to query its own derivation structure
**Dependencies**: Workstreams A + B (needs paths and witnesses)
**Parallelizable**: Can define interfaces while A+B progress

### D.1 Self-Awareness Queries

**Files to Create**:
```
impl/claude/protocols/ashc/
├── self_awareness.py     # ASHCSelfAwareness class
├── groundedness.py       # am_i_grounded() implementation
├── consistency.py        # verify_self_consistency()
└── explanation.py        # explain_derivation()
```

**ASHCSelfAwareness Interface**:
```python
@dataclass
class GroundednessResult:
    is_grounded: bool
    paths_to_principles: dict[str, list[DerivationPath]]
    ungrounded_components: list[str]
    overall_confidence: float

@dataclass
class ConsistencyResult:
    is_consistent: bool
    law_violations: list[dict]      # Categorical law failures
    contradictions: list[dict]      # Super-additive loss
    galois_violations: list[dict]   # Loss threshold exceeded
    principle_violations: list[dict] # Constitutional misalignment

class ASHCSelfAwareness:
    """Interface for ASHC to query its own derivation structure."""

    def __init__(self, store: DerivationStore):
        self.store = store

    async def am_i_grounded(self) -> GroundednessResult:
        """
        Check if ASHC has complete derivation path from Constitution.

        ASHC asking: "Do I have principled justification for existing?"

        Algorithm: BFS from Constitution principles to ASHC components
        """
        ...

    async def what_principle_justifies(
        self, component: str
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
        self, from_artifact: str, to_artifact: str
    ) -> list[DerivationPath]:
        """
        Explain how one artifact derives from another.

        Returns the composition of paths from source to target.
        """
        ...
```

### D.2 Groundedness Implementation

**Algorithm**:
```python
async def am_i_grounded(self) -> GroundednessResult:
    """BFS from Constitution to all ASHC components."""
    # Start with the 7 constitutional principles
    principles = [
        "TASTEFUL", "CURATED", "ETHICAL", "JOY_INDUCING",
        "COMPOSABLE", "HETERARCHICAL", "GENERATIVE"
    ]

    # Get all ASHC components
    ashc_components = await self._get_ashc_components()

    # For each component, find paths from any principle
    paths_to_principles: dict[str, list[DerivationPath]] = {}
    ungrounded: list[str] = []

    for component in ashc_components:
        paths = await self._find_paths_to(component, principles)
        if paths:
            paths_to_principles[component] = paths
        else:
            ungrounded.append(component)

    # Compute overall confidence
    if ungrounded:
        confidence = 1.0 - (len(ungrounded) / len(ashc_components))
    else:
        confidence = min(
            min(p.galois_loss for p in paths)
            for paths in paths_to_principles.values()
        )
        confidence = 1.0 - confidence  # Invert loss to confidence

    return GroundednessResult(
        is_grounded=len(ungrounded) == 0,
        paths_to_principles=paths_to_principles,
        ungrounded_components=ungrounded,
        overall_confidence=confidence,
    )
```

### D.3 AGENTESE Nodes

**Files to Create**:
```
impl/claude/protocols/agentese/contexts/ashc_self.py
```

**AGENTESE Paths**:
```python
@node("concept.derivation.grounded", dependencies=("self_awareness",))
class GroundednessNode:
    """Check if ASHC is grounded in Constitution."""

    async def invoke(self, observer: Observer) -> GroundednessResult:
        return await self.self_awareness.am_i_grounded()

@node("concept.derivation.explain", dependencies=("self_awareness",))
class ExplanationNode:
    """Explain derivation between artifacts."""

    async def invoke(
        self, observer: Observer, from_: str, to: str
    ) -> list[DerivationPath]:
        return await self.self_awareness.explain_derivation(from_, to)

@node("self.ashc.consistency", dependencies=("self_awareness",))
class ConsistencyNode:
    """Verify ASHC self-consistency."""

    async def invoke(self, observer: Observer) -> ConsistencyResult:
        return await self.self_awareness.verify_self_consistency()
```

---

## Workstream E: Bootstrap (Fixed Point)

**Goal**: ASHC derives itself from Constitution
**Dependencies**: All previous workstreams
**Parallelizable**: NO (final integration)

### E.1 Bootstrap Implementation

**Files to Create**:
```
impl/claude/protocols/ashc/
├── bootstrap.py       # ASHCBootstrap class
└── fixed_point.py     # Fixed-point verification
```

**Bootstrap Algorithm**:
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
        1. Constitution → ASHC Principles (instantiation)
        2. ASHC Principles → ASHC Spec (refinement)
        3. ASHC Spec → ASHC Implementation (compilation)

        The composed path is ASHC's "birth certificate".
        """
        # Phase 1: Principle instantiation
        # Constitution principles → ASHC-specific principles
        principle_path = await self._derive_principles(constitution)

        # Phase 2: Spec refinement
        # ASHC principles → spec/protocols/proof-generation.md
        spec_path = await self._derive_spec(
            principle_path.target, ashc_spec
        )

        # Phase 3: Implementation compilation
        # ASHC spec → protocols/ashc/*.py
        impl_path = await self._compile_implementation(spec_path.target)

        # Compose the full path
        # (principle ; spec) ; impl
        full_path = principle_path.compose(spec_path).compose(impl_path)

        # Verify fixed-point property
        # The spec should be Galois-stable (loss < 0.10)
        spec_loss = await self._compute_galois_loss(ashc_spec)
        if spec_loss > 0.10:
            raise BootstrapError(
                f"ASHC spec not a fixed point: loss={spec_loss}"
            )

        # Store the birth certificate
        await self.store.save(full_path)

        return full_path
```

### E.2 Fixed Point Verification

**Algorithm** (from existing Galois infrastructure):
```python
async def verify_fixed_point(content: str) -> FixedPointResult:
    """
    Verify content is a Galois fixed point.

    A fixed point satisfies: L(P) = d(P, C(R(P))) < epsilon
    where epsilon = 0.05 for axioms, 0.10 for specs
    """
    max_iterations = 7  # By design, 7 layers is sufficient

    current = content
    for i in range(max_iterations):
        # R: restructure
        modular = await restructure(current)
        # C: reconstitute
        reconstituted = await reconstitute(modular)
        # d: semantic distance
        loss = await semantic_distance(current, reconstituted)

        if loss < FIXED_POINT_THRESHOLD:  # 0.05
            return FixedPointResult(
                is_fixed_point=True,
                iterations=i + 1,
                final_loss=loss,
                is_axiom=loss < 0.05,
            )

        current = reconstituted

    return FixedPointResult(
        is_fixed_point=False,
        iterations=max_iterations,
        final_loss=loss,
    )
```

### E.3 CLI Command

**Files to Modify**:
```
impl/claude/protocols/cli/commands/
└── ashc.py    # Add 'kg ashc bootstrap' command
```

**Command**:
```python
@ashc.command()
async def bootstrap():
    """
    Run ASHC bootstrap - derive ASHC from Constitution.

    This creates ASHC's "birth certificate": a complete derivation path
    from Constitutional principles to implementation.
    """
    constitution = load_constitution()
    ashc_spec = load_ashc_spec()

    bootstrap = ASHCBootstrap(store=get_derivation_store())

    with console.status("Deriving ASHC from Constitution..."):
        path = await bootstrap.derive_self(constitution, ashc_spec)

    console.print(f"[green]✓ Bootstrap complete[/green]")
    console.print(f"  Path ID: {path.path_id}")
    console.print(f"  Galois Loss: {path.galois_loss:.4f}")
    console.print(f"  Witnesses: {len(path.witnesses)}")

    # Print principle scores
    console.print("\n[bold]Constitutional Alignment:[/bold]")
    for principle, score in sorted(path.principle_scores.items()):
        bar = "█" * int(score * 20)
        console.print(f"  {principle:15} {bar} {score:.2f}")
```

---

## Phase Gates (Synchronization Points)

### Gate 1: Types Complete
**When**: Workstreams A.1 + A.2 complete
**Verification**:
- All types compile without errors
- Property-based tests pass
- Categorical laws verified

### Gate 2: Integration Ready
**When**: Workstream B complete
**Verification**:
- `Run.witnesses` populated (not `()`)
- Marks emitted for every compilation
- Constitutional scores computed

### Gate 3: Formal Verification
**When**: Workstream C complete
**Verification**:
- All Lean proofs compile with NO SORRY
- Python-Lean round-trip works
- Verified theorems become max-confidence witnesses

### Gate 4: Self-Aware
**When**: Workstream D complete
**Verification**:
- `am_i_grounded()` returns accurate result
- `verify_self_consistency()` catches law violations
- AGENTESE nodes respond correctly

### Gate 5: Bootstrap
**When**: Workstream E complete
**Verification**:
- `derive_self()` produces valid path
- ASHC spec verified as fixed point (loss < 0.10)
- `kg ashc bootstrap` CLI works

---

## Parallel Execution Schedule

```
Week 1-2:
  A.1 (Types)        ████████████████████
  A.2 (Laws)         ░░░░░░░░░░████████████
  C.1 (Lean Types)   ████████████████████

Week 2-3:
  A.3 (Storage)      ░░░░░░░░░░████████████
  B.1 (Mark Emit)    ░░░░░░░░░░████████████
  C.2 (Lean Proofs)  ████████████████████

Week 3-4:
  B.2 (Run.wit)      ████████████████████
  B.3 (Const Integ)  ████████████████████
  C.3 (Lean Bridge)  ░░░░░░░░░░████████████

Week 4-5:
  [GATE 1+2]         ▓▓▓▓▓▓▓▓▓▓
  D.1 (Self-Aware)   ░░░░░░░░░░████████████
  D.2 (Grounded)     ░░░░░░░░░░████████████

Week 5-6:
  D.3 (AGENTESE)     ████████████████████
  [GATE 3+4]         ▓▓▓▓▓▓▓▓▓▓
  E.1 (Bootstrap)    ░░░░░░░░░░████████████

Week 6-7:
  E.2 (Fixed Point)  ████████████████████
  E.3 (CLI)          ████████████████████
  [GATE 5]           ▓▓▓▓▓▓▓▓▓▓

Legend:
  ████ Active work
  ░░░░ Blocked/waiting
  ▓▓▓▓ Phase gate
```

---

## Success Metrics

### Functional
| Metric | Target | Measurement |
|--------|--------|-------------|
| Path composition correctness | 100% | Property tests pass |
| Lean proofs complete | 0 sorry | `lake build` output |
| Witness coverage | 100% ASHC ops | Marks per compile > 0 |
| Self-awareness accuracy | 95% | Manual verification |
| Bootstrap success | 100% | CI test |

### Performance
| Metric | Target | Measurement |
|--------|--------|-------------|
| Path composition | <10ms | Benchmark |
| Path storage | <50ms | Benchmark |
| Groundedness check | <1s | Benchmark |
| Lean verification | <30s | CI timing |

### Quality
| Metric | Target | Measurement |
|--------|--------|-------------|
| Test coverage | >90% | pytest-cov |
| Type coverage | 100% | mypy strict |
| Doc coverage | 100% public | docstring check |

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Lean proofs too complex | Start simple, escalate. Use existing 35 theorems as template. |
| Integration breaks existing | Feature flags. Gradual rollout. Don't touch Run creation until witnesses work. |
| Performance issues | Lazy evaluation. Caching. Async where possible. |
| Bootstrap infinite loop | Depth limit (7). Fixed-point detection before recursion. |
| Galois loss unstable | Use existing robust implementation. Fall back to BERTScore. |

---

## Agent Assignment (For Parallel Execution)

When launching parallel agents:

```
AGENT-A: Core Types (Workstream A)
  - Focus: Pure Python, no external dependencies
  - Can run immediately
  - Deliverable: protocols/ashc/paths/*.py with tests

AGENT-B: Witness Bridge (Workstream B)
  - Focus: Integration with existing Mark system
  - Depends on: A.1 types (can mock initially)
  - Deliverable: evidence.py modifications, witness_bridge.py

AGENT-C: Lean Formalization (Workstream C)
  - Focus: Formal proofs in Lean 4
  - Can run immediately (separate codebase)
  - Deliverable: KgentsProofs/DerivationPaths.lean

AGENT-D: Self-Awareness (Workstream D)
  - Focus: Query interface
  - Depends on: A+B complete
  - Deliverable: self_awareness.py, AGENTESE nodes

AGENT-E: Bootstrap (Workstream E)
  - Focus: Fixed-point derivation
  - Depends on: All previous
  - Deliverable: bootstrap.py, CLI command
```

---

*"The proof IS the decision. The mark IS the witness. The path IS the derivation."*
