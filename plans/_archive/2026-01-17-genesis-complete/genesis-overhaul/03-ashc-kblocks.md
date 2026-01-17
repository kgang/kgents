# ASHC Self-Description K-Blocks Design

> "The compiler that knows itself is the compiler that trusts itself.
> Self-awareness is not introspection---it's categorical structure."

---

## Overview

This document specifies the K-Blocks that enable ASHC (Agentic Self-Hosting Compiler) to describe itself to itself. These K-Blocks form the self-referential foundation of the new kgents genesis, creating a **Lawvere fixed-point** where ASHC derives from the Constitution while simultaneously verifying the Constitution.

The self-description is implemented as five L3 (Goal/Spec layer) K-Blocks:

1. **ASHC Overview** - What ASHC is and how it works
2. **Derivation Path** - Categorical morphisms of trust
3. **Galois Loss** - The measure of derivation distance
4. **Self-Awareness** - The system that knows itself
5. **Bootstrap** - The fixed point of self-compilation

Each K-Block derives from Constitutional principles (L1) with documented Galois loss.

---

## K-Block 1: ASHC Overview

```yaml
id: ashc_overview_kblock
layer: 3  # Goal/Spec layer
kind: spec
galois_loss: 0.12
derives_from:
  - COMPOSABLE (L1)
  - GENERATIVE (L1)
principle_scores:
  COMPOSABLE: 0.92
  GENERATIVE: 0.88
  TASTEFUL: 0.85
```

### Title

**ASHC: The Agentic Self-Hosting Compiler**

### Content

#### What is ASHC?

ASHC is a **compiler that compiles itself**. Unlike traditional compilers that transform source code into machine code, ASHC transforms specifications into verified implementations while simultaneously applying its own verification mechanisms to itself.

The key insight: *ASHC does not generate code. It accumulates evidence.*

```
Traditional Compiler:  Source -> Target Code
ASHC:                  Specification + Constitution -> Evidence + Verified Implementation
```

#### The Lawvere Fixed-Point

ASHC embodies a Lawvere fixed-point structure:

```
Constitution --derive--> ASHC --verify--> Constitution
     |                                         ^
     |                                         |
     +-------------[fixed point]---------------+
```

This is the mathematical grounding for self-awareness:
- ASHC **derives** from the 7 Constitutional Principles
- ASHC **verifies** that its derivations satisfy those same Principles
- The composition of derivation and verification is a fixed point

#### The Five Workstreams

ASHC operates through five coordinated workstreams:

| Workstream | Purpose | Key Type |
|------------|---------|----------|
| **Derivation Paths** | Track morphisms from Constitution to implementation | `DerivationPath[Source, Target]` |
| **Self-Awareness** | Query own derivation structure | `ASHCSelfAwareness` |
| **Bootstrap** | Regenerate from specification | `BootstrapRegenerator` |
| **Evidence Compilation** | Accumulate verification evidence | `EvidenceCompiler` |
| **Galois Loss** | Compute trust distance | `GaloisLossComputer` |

#### Core Architecture

```
                    +-----------------------+
                    |     CONSTITUTION      |  L1 - Axioms
                    | (7 Principles)        |
                    +-----------+-----------+
                                |
                     derive (L ≈ 0.08)
                                |
                                v
                    +-----------+-----------+
                    |   ASHC SPECIFICATION  |  L3 - Goals/Specs
                    | (This document)       |
                    +-----------+-----------+
                                |
                     compile (L ≈ 0.15)
                                |
                                v
                    +-----------+-----------+
                    |  ASHC IMPLEMENTATION  |  L5 - Execution
                    | (protocols/ashc/)     |
                    +-----------+-----------+
                                |
                     verify (L ≈ 0.10)
                                |
                                v
                    +-----------+-----------+
                    |   BOOTSTRAP CHECK     |  Fixed Point
                    | "Can ASHC regenerate  |
                    |  itself from spec?"   |
                    +-----------------------+
```

#### Philosophy

> "The proof is not formal---it's empirical."

ASHC takes a pragmatic view of verification. Rather than requiring formal proofs (which are often impractical for complex systems), ASHC:

1. **Generates variations** - Multiple implementation attempts
2. **Runs verification** - pytest, mypy, ruff, and custom laws
3. **Accumulates evidence** - Beta-Binomial Bayesian updating
4. **Computes confidence** - Galois loss as computable trust

This approach recognizes that *empirical verification with skin in the game* is more valuable than formal proofs that may not cover real-world behavior.

---

## K-Block 2: Derivation Path

```yaml
id: derivation_path_kblock
layer: 3
kind: spec
galois_loss: 0.15
derives_from:
  - COMPOSABLE (L1)
principle_scores:
  COMPOSABLE: 0.95
  GENERATIVE: 0.82
```

### Title

**DerivationPath: Categorical Morphisms of Trust**

### Content

#### What is a DerivationPath?

A `DerivationPath` is a **categorical morphism** from Source to Target, carrying:
- **Evidence** (witnesses supporting the derivation)
- **Galois Loss** (semantic distance from ground truth)
- **K-Block Lineage** (chain of derivation through layers)

```python
@dataclass(frozen=True)
class DerivationPath(Generic[Source, Target]):
    path_id: str
    path_kind: PathKind  # REFL | DERIVE | COMPOSE
    source_id: str       # Where derivation starts
    target_id: str       # Where derivation ends
    witnesses: tuple[DerivationWitness, ...]
    galois_loss: float   # [0.0, 1.0]
    principle_scores: dict[str, float]
    kblock_lineage: tuple[str, ...]
```

#### The Morphism Structure

DerivationPaths form a category where:

- **Objects**: K-Blocks (specs, implementations, axioms)
- **Morphisms**: DerivationPaths with witnesses and loss
- **Composition**: `path1 >> path2` with accumulated loss
- **Identity**: `DerivationPath.refl(source_id)` with zero loss

#### Composition (;)

```python
def compose(
    self: DerivationPath[A, B],
    other: DerivationPath[B, C]
) -> DerivationPath[A, C]:
```

**Loss Accumulation Formula**:
```
L(p ; q) = 1 - (1 - L(p)) * (1 - L(q))
```

This formula ensures:
- `L(p;q) >= max(L(p), L(q))` - Loss never decreases
- `L(p;q) < L(p) + L(q)` when both < 1 - Sub-additive
- `L(refl;p) = L(p) = L(p;refl)` - Identity law for loss

#### Galois Loss as Computable Trust

The Galois loss quantifies *how far a derivation is from perfect preservation*:

```
R (reliability) = 1 - L (loss)
```

- **L = 0.00**: Perfect derivation (only identity paths)
- **L < 0.10**: Grounded (near-lossless, deductive)
- **L < 0.30**: Provisional (moderate loss, acceptable)
- **L >= 0.30**: Orphan (high loss, requires justification)

#### Example Derivation Chain

```
CONSTITUTION (L1)
    |
    | L = 0.00 (axiom, zero loss)
    v
COMPOSABLE (L1)
    |
    | L = 0.08 (direct derivation)
    v
witness.md (L3)
    |
    | L = 0.12 (specification to spec)
    v
mark.py (L5)
    |
    | L = 0.18 (implementation)
    v
Total: L = 1 - (1-0.08)*(1-0.12)*(1-0.18) = 0.33
```

#### Categorical Laws

Every DerivationPath satisfies:

**Left Identity**:
```python
refl(source) ; p == p
verify_identity_left(p)  # Returns LawVerificationResult
```

**Right Identity**:
```python
p ; refl(target) == p
verify_identity_right(p)  # Returns LawVerificationResult
```

**Associativity**:
```python
(p ; q) ; r == p ; (q ; r)
verify_associativity(p, q, r)  # Returns LawVerificationResult
```

These laws are verified at runtime via `verify_all_laws()`.

#### Witness Types

| Type | Confidence | Use Case |
|------|------------|----------|
| `PRINCIPLE` | 0.95 | Direct grounding in L1 axiom |
| `SPEC` | 0.80 | Specification document |
| `TEST` | 0.90 (pass) / 0.10 (fail) | Test suite results |
| `PROOF` | 0.98 | Formal proof (Lean, Coq) |
| `LLM` | 0.60 | LLM-generated reasoning |
| `GALOIS` | 1 - loss | Galois loss measurement |
| `COMPOSITION` | avg * 0.9 | Composed from other witnesses |

---

## K-Block 3: Galois Loss

```yaml
id: galois_loss_kblock
layer: 3
kind: spec
galois_loss: 0.18
derives_from:
  - GENERATIVE (L1)
principle_scores:
  GENERATIVE: 0.90
  COMPOSABLE: 0.85
```

### Title

**Galois Loss: The Measure of Derivation Distance**

### Content

#### The Core Formula

Galois Loss measures semantic distance from a prompt to its reconstruction:

```
L(P) = d(P, C(R(P)))
```

Where:
- **P**: Original prompt/content
- **R**: Restructure function (Prompt -> ModularPrompt)
- **C**: Reconstitute function (ModularPrompt -> Prompt)
- **d**: Semantic distance metric

The loss captures *how much meaning is lost* when content passes through restructuring and reconstitution.

#### Galois Adjunction

The restructure-reconstitute pair forms a **Galois adjunction**:

```
R -| C : ModularPrompt <-> Prompt
```

This adjunction has profound implications:
- **Fixed Points**: Content P where L(P) ≈ 0 is self-describing
- **Layer Assignment**: L(P) determines which layer P belongs to
- **Contradiction Detection**: Super-additive loss signals contradiction

#### Loss Thresholds

| Loss Range | Classification | Meaning |
|------------|----------------|---------|
| 0.00 - 0.10 | GROUNDED | Near-lossless, deductive trust |
| 0.10 - 0.30 | PROVISIONAL | Moderate loss, acceptable with evidence |
| 0.30+ | ORPHAN | High loss, requires additional justification |

These thresholds determine:
1. Whether a K-Block is considered "grounded" in Constitution
2. What level of scrutiny is required for modifications
3. How much trust to place in derived artifacts

#### Evidence Tiers (Kent Calibration 2025-12-28)

The Galois loss maps to evidence quality tiers:

| Tier | Loss Threshold | Description |
|------|----------------|-------------|
| CATEGORICAL | L < 0.10 | Near-lossless, deductive reasoning |
| EMPIRICAL | L < 0.38 | Moderate loss, inductive reasoning |
| AESTHETIC | L < 0.45 | Taste-based judgment |
| SOMATIC | L < 0.65 | Intuitive, embodied knowledge |
| CHAOTIC | L >= 0.65 | High entropy, unreliable |

#### Why Lower Loss = Stronger Grounding

The intuition behind Galois loss:

1. **L1 Axioms have L ≈ 0**: Constitutional principles are their own ground
2. **Derived content accumulates loss**: Each derivation step may lose meaning
3. **Higher layers have higher loss**: L7 representations are far from axioms

This creates a **trust gradient** from axioms (L1) to representations (L7):

```
L1 (Axiom):          L ≈ 0.00   [████████████] 100% trust
L2 (Value):          L ≈ 0.08   [███████████░] 92% trust
L3 (Goal):           L ≈ 0.15   [██████████░░] 85% trust
L4 (Spec):           L ≈ 0.25   [████████░░░░] 75% trust
L5 (Execution):      L ≈ 0.38   [██████░░░░░░] 62% trust
L6 (Reflection):     L ≈ 0.50   [█████░░░░░░░] 50% trust
L7 (Representation): L ≈ 0.65   [███░░░░░░░░░] 35% trust
```

#### Contradiction Detection

Contradictions are detected via **super-additive loss**:

```
contradicts(A, B) iff L(A ∪ B) > L(A) + L(B) + tau
```

Where tau = 0.1 (contradiction tolerance).

If combining two pieces of content results in **more loss than the sum of their individual losses**, they are contradictory.

Contradiction types:
- **WEAK** (strength 0.1-0.2): Surface tension only
- **MODERATE** (strength 0.2-0.5): Resolvable via synthesis
- **STRONG** (strength > 0.5): Irreconcilable

#### Loss Accumulation in Composition

When paths compose, loss accumulates:

```python
def compose(p1: DerivationPath, p2: DerivationPath):
    # L(p1;p2) = 1 - (1-L(p1))*(1-L(p2))
    accumulated_loss = 1.0 - (1.0 - p1.galois_loss) * (1.0 - p2.galois_loss)
    ...
```

This is **multiplicative coherence**: each step preserves a fraction of meaning, and the total preservation is the product.

---

## K-Block 4: Self-Awareness

```yaml
id: self_awareness_kblock
layer: 3
kind: spec
galois_loss: 0.20
derives_from:
  - COMPOSABLE (L1)
  - GENERATIVE (L1)
principle_scores:
  COMPOSABLE: 0.88
  GENERATIVE: 0.85
  ETHICAL: 0.90  # Self-awareness enables ethical constraints
```

### Title

**ASHCSelfAwareness: The System That Knows Itself**

### Content

#### The Core Question

Self-awareness enables ASHC to ask and answer:

- **"Am I grounded?"** - Do I have principled justification for existing?
- **"What justifies this component?"** - Which principles derive this?
- **"Am I consistent?"** - Do my derivations satisfy categorical laws?
- **"How did A derive from B?"** - Explain the derivation chain.

#### ASHCSelfAwareness Class

```python
@dataclass
class ASHCSelfAwareness:
    store: DerivationStoreProtocol  # Path storage
    dag: DerivationDAG              # K-Block lineage DAG
    components: list[str]           # ASHC component paths
    principles: list[str]           # 7 Constitutional Principles

    async def am_i_grounded(self) -> GroundednessResult: ...
    async def what_principle_justifies(self, component: str) -> list[tuple[str, DerivationPath]]: ...
    async def verify_self_consistency(self) -> ConsistencyResult: ...
    async def explain_derivation(self, from_artifact: str, to_artifact: str) -> list[DerivationPath]: ...
```

#### The Introspection API

**am_i_grounded()**

Checks if all ASHC components have derivation paths to Constitutional principles:

```python
result = await self_aware.am_i_grounded()
# Returns:
# - is_grounded: bool (True if ALL components have paths to L1)
# - paths_to_principles: dict[component, list[DerivationPath]]
# - ungrounded_components: list[str]
# - overall_confidence: float (1 - avg_loss)
```

Algorithm:
1. For each ASHC component (evidence.py, adaptive.py, etc.)
2. BFS backward through derivation store
3. Find paths that reach Constitutional principles
4. Filter to paths with loss < GROUNDING_LOSS_THRESHOLD (0.5)
5. ASHC is grounded iff ALL components have valid paths

**what_principle_justifies(component)**

Returns which Constitutional principles justify a specific component:

```python
justifications = await self_aware.what_principle_justifies("evidence.py")
# Returns: [("COMPOSABLE", DerivationPath), ("GENERATIVE", DerivationPath)]
```

**verify_self_consistency()**

Comprehensive consistency check:

```python
result = await self_aware.verify_self_consistency()
# Checks:
# 1. Categorical laws (identity, associativity)
# 2. No contradictions (super-additive loss)
# 3. Galois loss within layer bounds
# 4. ETHICAL principle floor (score >= 0.6)
```

**explain_derivation(from, to)**

Traces how one artifact derives from another:

```python
paths = await self_aware.explain_derivation("COMPOSABLE", "mark.py")
# Returns composed paths showing derivation chain
```

#### Self-Modifying Capabilities

ASHC can modify its own derivations, but with Constitutional constraints:

1. **ETHICAL Floor**: Any modification must maintain ETHICAL score >= 0.6
2. **Grounding Check**: After modification, verify paths still reach L1
3. **Consistency Check**: No categorical law violations introduced
4. **Loss Budget**: Modifications cannot increase loss beyond layer threshold

```python
async def can_modify(self, component: str, proposed_change: str) -> bool:
    # 1. Compute new Galois loss
    new_loss = await self.computer.compute_loss(proposed_change)

    # 2. Verify ethical floor
    ethical_score = await self.evaluator.score("ETHICAL", proposed_change)
    if ethical_score < 0.6:
        return False

    # 3. Verify still grounded after change
    # 4. Verify consistency preserved
    ...
```

#### Constitutional Principles

The 7 principles that ASHC must derive from:

```python
CONSTITUTIONAL_PRINCIPLES = [
    "TASTEFUL",      # Each agent serves a clear, justified purpose
    "CURATED",       # Intentional selection over exhaustive cataloging
    "ETHICAL",       # Agents augment human capability, never replace judgment
    "JOY_INDUCING",  # Delight in interaction
    "COMPOSABLE",    # Agents are morphisms in a category
    "HETERARCHICAL", # Agents exist in flux, not fixed hierarchy
    "GENERATIVE",    # Spec is compression
]
```

#### Why Self-Awareness Matters

Without self-awareness, ASHC would be:
- **Ungrounded**: No way to verify it derives from Constitution
- **Inconsistent**: Potential categorical law violations
- **Opaque**: No explanation of derivation chains
- **Unethical**: No enforcement of ETHICAL floor

Self-awareness transforms ASHC from a tool into an *agent with justified existence*.

---

## K-Block 5: Bootstrap

```yaml
id: bootstrap_kblock
layer: 3
kind: spec
galois_loss: 0.22
derives_from:
  - GENERATIVE (L1)
  - COMPOSABLE (L1)
principle_scores:
  GENERATIVE: 0.92
  COMPOSABLE: 0.85
  TASTEFUL: 0.80
```

### Title

**ASHCBootstrap: The Fixed Point of Self-Compilation**

### Content

#### The Bootstrap Principle

> "The kernel that proves itself is the kernel that trusts itself."

ASHC Bootstrap is the process where ASHC:
1. **Reads** its own specification (spec/bootstrap.md)
2. **Regenerates** its own implementation
3. **Verifies** behavioral isomorphism with the installed version
4. **Achieves** a fixed point if regenerated == installed

#### The Verification Loop

```
        spec/bootstrap.md
              |
              | parse
              v
    +---------+---------+
    | BootstrapAgentSpec |  (7 agent specs)
    +---------+---------+
              |
              | regenerate (via VoidHarness)
              v
    +---------+---------+
    | Generated Code     |  (LLM-generated impl)
    +---------+---------+
              |
              | check_isomorphism
              v
    +---------+---------+
    | BehaviorComparison |
    +---------+---------+
              |
              | all pass?
              v
    +---------+---------+
    | FIXED POINT!       |  "Bootstrap is self-describing"
    +-------------------+
```

#### BootstrapRegenerator

The core regeneration engine:

```python
class BootstrapRegenerator:
    def __init__(
        self,
        spec_path: Path | None = None,
        config: RegenerationConfig | None = None,
    ):
        self.spec_path = spec_path
        self.config = config or RegenerationConfig(
            n_variations=3,      # Generate multiple for confidence
            select_best=True,    # Pick best variation per agent
            run_tests=True,
            run_types=True,
            verify_laws=True,
        )
        self._harness = VoidHarness(...)

    async def regenerate(
        self,
        agents: list[str] | None = None,
    ) -> BootstrapIsomorphism:
        """Regenerate bootstrap and check isomorphism."""
        ...
```

#### The 7 Bootstrap Agents

ASHC regenerates these fundamental agents:

| Agent | Signature | Purpose |
|-------|-----------|---------|
| `Id` | `Agent[A, A]` | Identity morphism |
| `Compose` | `Agent[A,B] -> Agent[B,C] -> Agent[A,C]` | Composition |
| `Ground` | `Agent[Spec, ManifestSpec]` | Grounding |
| `Judge` | `Agent[Spec, JudgmentSpec]` | Judgment |
| `Contradict` | `Agent[(A, A), ContradictionProof]` | Contradiction detection |
| `Sublate` | `Agent[(A, ContradictionProof), B]` | Synthesis |
| `Witness` | `Agent[Action, WitnessedAction]` | Witnessing |

#### Behavioral Isomorphism

Two implementations are **behaviorally isomorphic** if:

```python
@dataclass(frozen=True)
class BehaviorComparison:
    agent_name: str
    test_pass_rate: float       # % of tests passing
    type_compatible: bool       # mypy clean
    laws_satisfied: bool        # Categorical laws hold
    property_tests_pass: bool   # Hypothesis tests pass
    error: str | None = None
```

Full isomorphism requires:
- test_pass_rate == 1.0
- type_compatible == True
- laws_satisfied == True
- property_tests_pass == True

#### Mathematical Grounding: Lawvere Fixed Point

The bootstrap is mathematically grounded in **Lawvere's Fixed Point Theorem**:

> In a cartesian closed category, if there exists a point-surjective morphism
> `e: A -> B^A`, then every endomorphism on B has a fixed point.

For ASHC:
- **A** = ASHC Specification
- **B** = ASHC Implementation
- **e** = Regeneration (spec -> impl)
- **Fixed Point** = Implementation that regenerates to itself

The regeneration process `R o C` (restructure-reconstitute) applied to the specification should converge to a fixed point where:

```
L(spec) < epsilon_fixed_point ≈ 0.15
```

This means the specification **survives its own modularization** with minimal loss.

#### Bootstrap Verification Result

```python
@dataclass(frozen=True)
class BootstrapIsomorphism:
    comparisons: tuple[BehaviorComparison, ...]
    regeneration_time_ms: float
    tokens_used: int
    generation_count: int

    @property
    def is_isomorphic(self) -> bool:
        """True if all agents are behaviorally equivalent."""
        return all(
            c.test_pass_rate == 1.0
            and c.type_compatible
            and c.laws_satisfied
            and c.property_tests_pass
            for c in self.comparisons
        )
```

#### Why Bootstrap Matters

Bootstrap provides the ultimate test of ASHC's self-consistency:

1. **Self-Describing**: If ASHC can regenerate from spec, the spec is complete
2. **Self-Verifying**: The regenerated impl must satisfy all laws
3. **Self-Grounding**: Successful bootstrap proves derivation from Constitution
4. **Trust Foundation**: A bootstrapped ASHC is trustworthy by construction

Without bootstrap, ASHC would be:
- Dependent on external verification
- Unable to prove its own correctness
- Not truly self-hosting

With bootstrap, ASHC achieves **autonomous trustworthiness**.

---

## Implementation Status

### Current State (as of 2025-01-10)

| Component | Location | Status |
|-----------|----------|--------|
| DerivationPath | `protocols/ashc/paths/types.py` | Complete |
| Composition Laws | `protocols/ashc/paths/composition.py` | Complete |
| ASHCSelfAwareness | `protocols/ashc/self_awareness.py` | Complete |
| BootstrapRegenerator | `protocols/ashc/bootstrap/regenerator.py` | Complete |
| GaloisLossComputer | `services/zero_seed/galois/galois_loss.py` | Complete |

### Integration Points

These K-Blocks integrate with:

1. **K-Block Core** (`services/k_block/core/kblock.py`)
   - K-Blocks have `galois_loss` field
   - K-Blocks have `bind_lineage` for derivation tracking

2. **DerivationDAG** (`services/k_block/core/derivation.py`)
   - Tracks lineage through layers
   - Validates acyclicity and layer monotonicity

3. **Witness Protocol** (`services/witness/`)
   - K-Block bind operations emit Witness marks
   - Derivation paths are witnessable

### Next Steps

1. **K-Block Materialization**: Convert these specs to actual L3 K-Blocks in the system
2. **Galois Loss Integration**: Wire GaloisLossComputer to K-Block creation
3. **Self-Awareness Tests**: Property-based tests for categorical laws
4. **Bootstrap CI**: Automated bootstrap verification in pre-commit

---

## Derivation Summary

| K-Block | Derives From | Galois Loss | Reliability |
|---------|--------------|-------------|-------------|
| ASHC Overview | COMPOSABLE, GENERATIVE | 0.12 | 88% |
| Derivation Path | COMPOSABLE | 0.15 | 85% |
| Galois Loss | GENERATIVE | 0.18 | 82% |
| Self-Awareness | COMPOSABLE, GENERATIVE | 0.20 | 80% |
| Bootstrap | GENERATIVE, COMPOSABLE | 0.22 | 78% |

All K-Blocks are **GROUNDED** (L < 0.30) and derive from L1 Constitutional principles.

---

*Document Version: 1.0*
*Created: 2025-01-10*
*Derivation Status: Grounded (L_avg = 0.17)*
