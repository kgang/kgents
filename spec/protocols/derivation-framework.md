# Derivation Framework: Bootstrap Proofs as Axiom Base

> *"The bootstrap is the seed. The derivation is the growth. The evidence is the sunlight. The proof is the fruit."*

**Status:** Complete (Phase 7 implemented, 306 tests passing)
**Heritage:** ASHC (empirical proofs), Bootstrap (axioms), Agent-as-Witness (justification), Exploration Harness (trail evidence), Portal Tokens (trust), Typed-Hypergraph (navigation), File Operad (operations)
**Created:** 2025-12-22
**Updated:** 2025-12-22
**Phase:** Phase 7 complete — CLI (`kg derivation`) & AGENTESE paths (`concept.derivation.*`)

---

## Purpose

Formalize how larger agents **derive** their justification from bootstrap primitives.

Why this needs to exist: The 7 bootstrap agents have categorical proofs. But K-gent, Crown Jewels, and app-level agents can't be proven the same way. They need a **derivation chain** that:

1. Inherits confidence from bootstrap axioms
2. Accumulates empirical evidence via ASHC
3. Tracks which principles are drawn upon
4. Degrades gracefully under challenge
5. Updates via stigmergic feedback

The derivation framework is **Bayesian proof theory for agents**.

---

## Core Insight

```
Bootstrap agents : Axioms :: Derived agents : Theorems

But the proof system is probabilistic:
  - Axioms have confidence 1.0 (categorical)
  - Theorems inherit confidence from premises
  - Evidence accumulates, decays, and updates
```

---

## The Derivation DAG

```
                    BOOTSTRAP (Axioms, confidence = 1.0)
                    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐
                    │ Id  │Comp │Judge│Ground│Contra│Subl │ Fix │
                    └──┬──┴──┬──┴──┬──┴──┬───┴──┬───┴──┬──┴──┬──┘
                       │     │     │     │      │      │     │
           ┌───────────┴─────┴─────┴─────┴──────┴──────┴─────┴───────────┐
           ▼                                                              ▼
    FUNCTORS (Tier 1, conf ≈ 0.95)                              POLYNOMIALS (Tier 1)
    ┌────────────────────────────┐                              ┌─────────────────────┐
    │ Flux, Cooled, Either,      │                              │ SOUL_POLYNOMIAL,    │
    │ Superposed, Logged         │                              │ MEMORY_POLYNOMIAL   │
    └─────────────┬──────────────┘                              └──────────┬──────────┘
                  │                                                        │
           ┌──────┴──────┐                                          ┌──────┴──────┐
           ▼             ▼                                          ▼             ▼
    FLUX AGENTS    FUNCTOR         OPERADS              SOUL AGENTS    MEMORY AGENTS
    (Tier 2)       COMPOSITIONS    (Tier 2)             (Tier 2)       (Tier 2)
    conf ≈ 0.85    (Tier 2)        ┌──────────┐         ┌──────────┐   ┌──────────┐
                                   │TOWN_OPERAD│        │ K-gent   │   │ M-gent   │
                                   │SOUL_OPERAD│        │          │   │          │
                                   └─────┬─────┘        └─────┬────┘   └────┬─────┘
                                         │                    │             │
                   ┌─────────────────────┴────────────────────┴─────────────┴─────────────┐
                   ▼                                                                       ▼
            CROWN JEWELS (Tier 3, conf ≈ 0.75)                            SIMULATION (Tier 3)
            ┌───────────────────────────────────┐                         ┌────────────────┐
            │ Brain, Witness, Forge, Conductor  │                         │ Town, Park     │
            └────────────────┬──────────────────┘                         └───────┬────────┘
                             │                                                    │
                             ▼                                                    ▼
                      APP AGENTS (Tier 4, conf ≈ 0.60)              CITIZENS (Tier 4)
                      ┌────────────────────────────┐                ┌──────────────────┐
                      │ Morning Coffee, Gardener   │                │ CitizenPolynomial│
                      └────────────────────────────┘                └──────────────────┘
```

---

## Formal Definition

### The Derivation Type

```python
@dataclass(frozen=True)
class Derivation:
    """
    A derivation is a morphism from bootstrap axioms to a derived agent.

    It carries:
    - The chain of agents this derives from
    - The principles drawn upon with their evidence strength
    - The accumulated confidence from inheritance + evidence
    """

    # Identity
    agent_name: str
    tier: DerivationTier  # BOOTSTRAP, FUNCTOR, POLYNOMIAL, JEWEL, APP

    # The derivation chain (ancestors in the DAG)
    derives_from: tuple[str, ...]  # ("Fix", "Flux") for FluxPolynomial

    # Principle draws with evidence
    principle_draws: tuple[PrincipleDraw, ...]

    # Confidence components
    inherited_confidence: float      # From derivation chain
    empirical_confidence: float      # From ASHC evidence
    stigmergic_confidence: float     # From usage patterns

    @property
    def total_confidence(self) -> float:
        """
        Combined confidence with diminishing returns.

        Not a simple average—empirical evidence can boost
        but not exceed inherited confidence by more than 20%.
        """
        base = self.inherited_confidence
        boost = min(0.2, self.empirical_confidence * 0.3)
        stigmergy = self.stigmergic_confidence * 0.1
        return min(1.0, base + boost + stigmergy)


class DerivationTier(Enum):
    """
    Tiers in the derivation hierarchy.

    Each tier has a confidence ceiling—no matter how much evidence,
    an APP agent can't exceed JEWEL confidence.
    """
    BOOTSTRAP = "bootstrap"      # Ceiling: 1.00
    FUNCTOR = "functor"          # Ceiling: 0.98
    POLYNOMIAL = "polynomial"    # Ceiling: 0.95
    OPERAD = "operad"            # Ceiling: 0.92
    JEWEL = "jewel"              # Ceiling: 0.85
    APP = "app"                  # Ceiling: 0.75
```

### Principle Draws

```python
@dataclass(frozen=True)
class PrincipleDraw:
    """
    Evidence that an agent instantiates a principle.

    Principles: Tasteful, Curated, Ethical, Joy-Inducing,
                Composable, Heterarchical, Generative
    """

    principle: str
    draw_strength: float           # 0.0-1.0
    evidence_type: EvidenceType
    evidence_sources: tuple[str, ...]  # IDs of supporting evidence
    last_verified: datetime

    @property
    def is_categorical(self) -> bool:
        """Categorical draws don't decay."""
        return self.evidence_type == EvidenceType.CATEGORICAL

    def decay(self, days_elapsed: float, rate: float = 0.02) -> "PrincipleDraw":
        """
        Empirical and aesthetic evidence decays.
        Categorical evidence doesn't.
        """
        if self.is_categorical:
            return self

        decayed_strength = self.draw_strength * (1 - rate) ** days_elapsed
        return replace(self, draw_strength=max(0.1, decayed_strength))


class EvidenceType(Enum):
    """Types of evidence for principle draws."""

    CATEGORICAL = "categorical"   # Laws verified (no decay)
    EMPIRICAL = "empirical"       # ASHC runs (slow decay)
    AESTHETIC = "aesthetic"       # Hardy criteria (medium decay)
    GENEALOGICAL = "genealogical" # Git archaeology (slow decay)
    SOMATIC = "somatic"           # Mirror test (no formalization)
```

### The Derivation Registry

```python
class DerivationRegistry:
    """
    Global registry of agent derivations.

    Think of this as the theorem database—every agent has
    a derivation that traces back to bootstrap axioms.
    """

    def __init__(self) -> None:
        self._derivations: dict[str, Derivation] = {}
        self._dag: DerivationDAG = DerivationDAG()
        self._seed_bootstrap()

    def _seed_bootstrap(self) -> None:
        """Seed with bootstrap axioms (confidence = 1.0)."""
        for name in ("Id", "Compose", "Judge", "Ground",
                     "Contradict", "Sublate", "Fix"):
            self._derivations[name] = Derivation(
                agent_name=name,
                tier=DerivationTier.BOOTSTRAP,
                derives_from=(),
                principle_draws=BOOTSTRAP_PRINCIPLE_DRAWS[name],
                inherited_confidence=1.0,
                empirical_confidence=1.0,
                stigmergic_confidence=1.0,
            )

    def register(
        self,
        agent_name: str,
        derives_from: tuple[str, ...],
        principle_draws: tuple[PrincipleDraw, ...],
        tier: DerivationTier,
    ) -> Derivation:
        """
        Register a new agent derivation.

        Computes inherited confidence from the derivation chain.
        """
        inherited = self._compute_inherited_confidence(derives_from)

        derivation = Derivation(
            agent_name=agent_name,
            tier=tier,
            derives_from=derives_from,
            principle_draws=principle_draws,
            inherited_confidence=inherited,
            empirical_confidence=0.0,  # Starts at zero
            stigmergic_confidence=0.0,
        )

        self._derivations[agent_name] = derivation
        self._dag.add_edge(derives_from, agent_name)

        return derivation

    def _compute_inherited_confidence(
        self,
        derives_from: tuple[str, ...],
    ) -> float:
        """
        Inherited confidence = product of ancestor confidences.

        With a floor to prevent vanishing confidence.
        """
        if not derives_from:
            return 1.0

        confidences = [
            self._derivations[name].total_confidence
            for name in derives_from
            if name in self._derivations
        ]

        if not confidences:
            return 0.5  # Unknown ancestors

        # Product with floor
        product = 1.0
        for c in confidences:
            product *= c

        return max(0.3, product)  # Floor of 0.3

    def update_evidence(
        self,
        agent_name: str,
        ashc_evidence: Evidence | None = None,
        usage_count: int | None = None,
    ) -> Derivation:
        """
        Update derivation with new evidence.

        Propagates confidence changes to dependents.
        """
        derivation = self._derivations[agent_name]

        # Update empirical confidence from ASHC
        if ashc_evidence:
            empirical = ashc_evidence.equivalence_score()
            derivation = replace(derivation, empirical_confidence=empirical)

        # Update stigmergic confidence from usage
        if usage_count is not None:
            # Logarithmic growth: 100 uses → 0.5, 1000 uses → 0.75, 10000 → 0.9
            stigmergic = min(0.95, 0.25 * math.log10(max(1, usage_count)))
            derivation = replace(derivation, stigmergic_confidence=stigmergic)

        self._derivations[agent_name] = derivation

        # Propagate to dependents
        self._propagate_confidence(agent_name)

        return derivation

    def _propagate_confidence(self, source: str) -> None:
        """
        When an agent's confidence changes, propagate to dependents.

        This is why it's a DAG—cycles would cause infinite propagation.
        """
        for dependent in self._dag.dependents(source):
            dep_derivation = self._derivations[dependent]
            new_inherited = self._compute_inherited_confidence(
                dep_derivation.derives_from
            )
            updated = replace(dep_derivation, inherited_confidence=new_inherited)
            self._derivations[dependent] = updated

            # Recursive propagation
            self._propagate_confidence(dependent)
```

---

## Laws

### Law 1: Derivation Monotonicity

```
∀ derivation D:
  tier(D) >= tier(parent(D))  # (where BOOTSTRAP < FUNCTOR < ... < APP)

  Derived agents must be at same or higher tier (less foundational) than parents.
  FUNCTOR can derive from BOOTSTRAP, APP can derive from JEWEL.
  You can't derive a FUNCTOR from an APP agent (reverse direction).

  In code: tier.rank >= parent.tier.rank (higher rank = less foundational)
```

### Law 2: Confidence Ceiling

```
∀ derivation D:
  D.total_confidence ≤ tier_ceiling(D.tier)

  No amount of evidence lets an APP agent exceed 0.75 confidence.
```

### Law 3: Bootstrap Indefeasibility

```
∀ bootstrap agent B:
  B.inherited_confidence = 1.0
  ¬∃ evidence E. E defeats B

  Bootstrap agents are axioms—they don't decay or get defeated.
```

### Law 4: Acyclicity

```
∀ derivation D:
  D ∉ transitive_closure(derives_from(D))

  The derivation graph is a DAG. No cycles allowed.
```

### Law 5: Propagation Correctness

```
∀ agent A with derivation D:
  confidence_change(parent(A)) → recompute(D.inherited_confidence)

  Confidence changes propagate through the DAG.
```

---

## Bootstrap Principle Draws

Each bootstrap agent instantiates specific principles:

```python
BOOTSTRAP_PRINCIPLE_DRAWS = {
    "Id": (
        PrincipleDraw("Composable", 1.0, CATEGORICAL, ("identity-law",)),
    ),
    "Compose": (
        PrincipleDraw("Composable", 1.0, CATEGORICAL, ("associativity-law",)),
        PrincipleDraw("Generative", 0.9, CATEGORICAL, ("pipelines-derive",)),
    ),
    "Judge": (
        PrincipleDraw("Tasteful", 1.0, CATEGORICAL, ("judgment-function",)),
        PrincipleDraw("Curated", 1.0, CATEGORICAL, ("selection-function",)),
        PrincipleDraw("Ethical", 1.0, CATEGORICAL, ("ethics-embedded",)),
    ),
    "Ground": (
        PrincipleDraw("Generative", 1.0, CATEGORICAL, ("facts-seed-generation",)),
        PrincipleDraw("Ethical", 0.9, CATEGORICAL, ("human-values-source",)),
    ),
    "Contradict": (
        PrincipleDraw("Heterarchical", 0.9, CATEGORICAL, ("tension-detection",)),
    ),
    "Sublate": (
        PrincipleDraw("Heterarchical", 1.0, CATEGORICAL, ("synthesis-function",)),
        PrincipleDraw("Joy-Inducing", 0.7, AESTHETIC, ("creative-leap",)),
    ),
    "Fix": (
        PrincipleDraw("Composable", 0.95, CATEGORICAL, ("fixed-point-enables-recursion",)),
        PrincipleDraw("Generative", 1.0, CATEGORICAL, ("self-reference",)),
    ),
}
```

---

## Example Derivations

### Flux (Tier 1: Functor)

```python
FLUX_DERIVATION = Derivation(
    agent_name="Flux",
    tier=DerivationTier.FUNCTOR,
    derives_from=("Fix", "Compose"),
    principle_draws=(
        PrincipleDraw(
            principle="Composable",
            draw_strength=0.95,
            evidence_type=EvidenceType.CATEGORICAL,
            evidence_sources=("flux-associativity-test",),
        ),
        PrincipleDraw(
            principle="Heterarchical",
            draw_strength=0.85,
            evidence_type=EvidenceType.EMPIRICAL,
            evidence_sources=("flux-dual-mode-ashc-runs",),
        ),
        PrincipleDraw(
            principle="Generative",
            draw_strength=0.78,
            evidence_type=EvidenceType.AESTHETIC,
            evidence_sources=("flux-spec-regeneration",),
        ),
    ),
    inherited_confidence=0.95,  # Fix(1.0) * Compose(1.0) * tier_factor(0.95)
    empirical_confidence=0.88,  # From ASHC runs
    stigmergic_confidence=0.72, # log10(5000 uses) * 0.25
)

# total_confidence ≈ 0.95 + min(0.2, 0.88*0.3) + 0.72*0.1 ≈ 0.95 + 0.2 + 0.07 = 1.0
# But capped at tier ceiling: min(1.0, 0.98) = 0.98
```

### K-gent (Tier 2: Polynomial)

```python
KGENT_DERIVATION = Derivation(
    agent_name="K-gent",
    tier=DerivationTier.POLYNOMIAL,
    derives_from=("Ground", "Judge", "SOUL_POLYNOMIAL"),
    principle_draws=(
        PrincipleDraw(
            principle="Ethical",
            draw_strength=0.92,
            evidence_type=EvidenceType.EMPIRICAL,
            evidence_sources=("persona-alignment-ashc", "gatekeeper-tests"),
        ),
        PrincipleDraw(
            principle="Joy-Inducing",
            draw_strength=0.88,
            evidence_type=EvidenceType.AESTHETIC,
            evidence_sources=("mirror-test-sessions",),
        ),
        PrincipleDraw(
            principle="Generative",
            draw_strength=0.75,
            evidence_type=EvidenceType.GENEALOGICAL,
            evidence_sources=("persona-spec-regeneration",),
        ),
        PrincipleDraw(
            principle="Tasteful",
            draw_strength=0.85,
            evidence_type=EvidenceType.SOMATIC,
            evidence_sources=(),  # Kent's judgment, not formalized
        ),
    ),
    inherited_confidence=0.88,  # Ground * Judge * SOUL_POLY degradation
    empirical_confidence=0.82,
    stigmergic_confidence=0.65,
)
```

### Brain (Tier 3: Crown Jewel)

```python
BRAIN_DERIVATION = Derivation(
    agent_name="Brain",
    tier=DerivationTier.JEWEL,
    derives_from=("M-gent", "K-gent", "Différance", "MEMORY_OPERAD"),
    principle_draws=(
        PrincipleDraw(
            principle="Composable",
            draw_strength=0.82,
            evidence_type=EvidenceType.EMPIRICAL,
            evidence_sources=("brain-pipeline-tests",),
        ),
        PrincipleDraw(
            principle="Generative",
            draw_strength=0.78,
            evidence_type=EvidenceType.GENEALOGICAL,
            evidence_sources=("teaching-crystal-regeneration",),
        ),
        PrincipleDraw(
            principle="Curated",
            draw_strength=0.85,
            evidence_type=EvidenceType.EMPIRICAL,
            evidence_sources=("deduplication-tests", "decay-tests"),
        ),
    ),
    inherited_confidence=0.72,  # Product of 4 ancestors with degradation
    empirical_confidence=0.85,
    stigmergic_confidence=0.80,
)
```

---

## Integration with ASHC

### Evidence → Derivation Updates

```python
async def update_derivation_from_ashc(
    registry: DerivationRegistry,
    agent_name: str,
    ashc_output: ASHCOutput,
) -> Derivation:
    """
    When ASHC compiles an agent, update its derivation.

    Flow:
    1. Extract principle evidence from ASHC runs
    2. Update principle draws
    3. Update empirical confidence
    4. Propagate through DAG
    """
    # Extract principle evidence from chaos tests
    principle_draws = extract_principle_evidence(ashc_output)

    # Update derivation
    current = registry.get(agent_name)
    updated = replace(
        current,
        principle_draws=merge_principle_draws(
            current.principle_draws,
            principle_draws,
        ),
    )

    # Update with ASHC evidence
    return registry.update_evidence(
        agent_name,
        ashc_evidence=ashc_output.evidence,
    )


def extract_principle_evidence(output: ASHCOutput) -> tuple[PrincipleDraw, ...]:
    """
    Extract principle draws from ASHC evidence.

    Pattern matching on chaos test results:
    - Composition tests → Composable principle
    - Identity tests → Composable principle
    - Mode switching tests → Heterarchical principle
    - Spec regeneration tests → Generative principle
    """
    draws = []

    # Composition tests
    if output.evidence.chaos_report.composition_pass_rate >= 0.95:
        draws.append(PrincipleDraw(
            principle="Composable",
            draw_strength=output.evidence.chaos_report.composition_pass_rate,
            evidence_type=EvidenceType.EMPIRICAL,
            evidence_sources=tuple(
                r.id for r in output.evidence.runs
                if "composition" in r.test_name
            ),
        ))

    # ... similar for other principles

    return tuple(draws)
```

### Lemma → Derivation Bridge

```python
async def lemma_strengthens_derivation(
    registry: DerivationRegistry,
    lemma: VerifiedLemma,
) -> None:
    """
    When a lemma is verified, it can strengthen derivations.

    Lemmas are formal proofs (Dafny, Lean4, Verus).
    They provide CATEGORICAL evidence for principle draws.
    """
    # Find which agents this lemma applies to
    affected_agents = find_agents_for_lemma(lemma)

    for agent_name in affected_agents:
        derivation = registry.get(agent_name)

        # Lemma provides categorical evidence
        new_draw = PrincipleDraw(
            principle=lemma_to_principle(lemma),
            draw_strength=1.0,  # Verified lemmas are certain
            evidence_type=EvidenceType.CATEGORICAL,
            evidence_sources=(lemma.id,),
        )

        updated = replace(
            derivation,
            principle_draws=derivation.principle_draws + (new_draw,),
        )

        registry._derivations[agent_name] = updated
```

---

## Integration with Witness

### Marks as Evidence

```python
async def mark_updates_stigmergy(
    registry: DerivationRegistry,
    mark: Mark,
) -> None:
    """
    When an action is witnessed, update stigmergic confidence.

    Marks are the atomic unit of witness.
    Successful marks reinforce; challenged marks decay.
    """
    # Extract which agents were involved
    agents_used = extract_agents_from_mark(mark)

    for agent_name in agents_used:
        # Increment usage count
        usage = registry.get_usage_count(agent_name)
        registry.update_evidence(agent_name, usage_count=usage + 1)

        # If mark was challenged, apply penalty
        if mark.challenged:
            derivation = registry.get(agent_name)
            updated = replace(
                derivation,
                stigmergic_confidence=derivation.stigmergic_confidence * 0.95,
            )
            registry._derivations[agent_name] = updated
```

### Differential Denial → Derivation Update

```python
async def denial_weakens_derivation(
    registry: DerivationRegistry,
    denial: DifferentialDenial,
) -> None:
    """
    When a proof is defeated, weaken the relevant derivations.

    Differential denials are learning opportunities.
    """
    # Find which agents' proofs were defeated
    affected = find_agents_for_trace(denial.original_trace_id)

    for agent_name in affected:
        derivation = registry.get(agent_name)

        # Decay the principle that was violated
        violated_principle = denial.heuristic_update  # e.g., "Composable"
        new_draws = tuple(
            replace(d, draw_strength=d.draw_strength * 0.8)
            if d.principle == violated_principle else d
            for d in derivation.principle_draws
        )

        updated = replace(derivation, principle_draws=new_draws)
        registry._derivations[agent_name] = updated
        registry._propagate_confidence(agent_name)
```

---

## AGENTESE Paths

```
concept.derivation.*
  .register         # Register new agent derivation
  .query            # Query derivation for an agent
  .dag              # Visualize the derivation DAG
  .confidence       # Get confidence breakdown
  .propagate        # Force confidence propagation

self.derivation.*
  .my_confidence    # Current agent's derivation confidence
  .my_principles    # Which principles I draw on
  .my_ancestors     # My derivation chain

time.derivation.*
  .history          # Confidence over time
  .decay            # Apply decay to all derivations
  .refresh          # Refresh empirical evidence
```

---

## CLI Commands

```bash
# View derivation for an agent
kg derive show K-gent
# → K-gent (Tier: POLYNOMIAL, Confidence: 0.82)
# → Derives from: Ground, Judge, SOUL_POLYNOMIAL
# → Principles:
# →   Ethical: 0.92 (empirical)
# →   Joy-Inducing: 0.88 (aesthetic)
# →   Generative: 0.75 (genealogical)
# →   Tasteful: 0.85 (somatic)

# View the derivation DAG
kg derive dag --tier JEWEL
# → Shows DAG from bootstrap to Crown Jewels

# Check confidence propagation
kg derive propagate Brain --verbose
# → Brain confidence: 0.78 → 0.81 (M-gent evidence updated)
# → Propagating to: Morning Coffee, Gardener

# Register a new derivation
kg derive register MyAgent \
    --derives-from K-gent,Compose \
    --tier APP \
    --principle Composable:0.8:empirical \
    --principle Joy-Inducing:0.7:aesthetic
```

---

## Anti-patterns

- **Circular derivation**: Agents can't derive from each other circularly
- **Tier violation**: Deriving from lower tiers (APP → FUNCTOR)
- **Confidence inflation**: More evidence shouldn't exceed tier ceiling
- **Bootstrap mutation**: Trying to update bootstrap agent confidence
- **Orphan agents**: Agents with no derivation chain (must trace to bootstrap)
- **Evidence hoarding**: Not propagating confidence changes
- **Decay denial**: Not applying decay to non-categorical evidence

---

## Teaching Notes (Gotchas from Implementation)

The following were discovered during Phase 1 implementation:

### Gotcha: Tier Ordering is Counterintuitive

```python
# BOOTSTRAP < FUNCTOR < ... < APP (by tier.rank)
# Lower rank = MORE foundational, HIGHER confidence ceiling
# Higher rank = LESS foundational, LOWER confidence ceiling

DerivationTier.BOOTSTRAP.rank == 0  # Most foundational
DerivationTier.APP.rank == 5        # Least foundational

# So when checking monotonicity:
tier >= parent.tier  # ✓ APP can derive from BOOTSTRAP
tier < parent.tier   # ✗ FUNCTOR cannot derive from APP
```

### Gotcha: Inherited Confidence Uses Product, Not Average

```python
# Product with floor:
inherited = product(parent.total_confidence for parent in derives_from)
inherited = max(0.3, inherited)  # Floor prevents vanishing

# NOT average:
# inherited = mean(parent.total_confidence for parent in derives_from)  # Wrong!
```

### Gotcha: Empirical Boost is Capped

```python
# Empirical evidence can boost at most 0.2:
boost = min(0.2, empirical_confidence * 0.3)

# So even with empirical_confidence = 1.0:
# boost = min(0.2, 1.0 * 0.3) = min(0.2, 0.3) = 0.2
```

### Gotcha: Evidence Decay Has a Floor

```python
# Evidence never decays below 0.1:
decayed_strength = max(0.1, original * (1 - rate) ** days)

# This prevents complete disappearance of evidence over time
```

### Gotcha: Somatic Evidence is Special

```python
# EvidenceType.SOMATIC has no evidence_sources tuple
# Kent's judgment (the Mirror Test) isn't formalized
# It's the ethical floor from Constitution Article IV: The Disgust Veto

PrincipleDraw(
    principle="Tasteful",
    draw_strength=0.85,
    evidence_type=EvidenceType.SOMATIC,
    evidence_sources=(),  # Empty! Not formalized.
)
```

### Gotcha: ASHC Bridge Uses Duck Typing

```python
# The bridge uses hasattr() checks, not isinstance()
# This enables testing with mock types without importing real ASHC

# Check for AdaptiveEvidence pattern:
if hasattr(output, "posterior_mean"):
    return _extract_from_adaptive(output)

# Check for ASHCOutput pattern:
if hasattr(output, "evidence") and hasattr(output.evidence, "runs"):
    evidence = output.evidence

# This pattern is intentional - not a code smell!
# It decouples derivation from ASHC import order.
```

### Gotcha: Stigmergic Decay ≠ Evidence Decay

```python
# These are DIFFERENT mechanisms:

# Evidence decay: principle draws lose strength over time
# Rate: EvidenceType.decay_rate (e.g., EMPIRICAL: 0.02/day)
# Floor: 0.1 (never fully disappears)
apply_evidence_decay(days_elapsed=7)

# Stigmergic decay: unused agents lose stigmergic confidence
# Mechanism: half-life based on INACTIVITY, not time
# Grace period: 14 days (no decay during grace period)
# Half-life: 30 days (after grace period)
apply_stigmergic_decay()

# Common mistake: running one but not the other
# Correct: run_decay_cycle() runs BOTH + optional ASHC refresh
```

### Gotcha: Categorical Evidence is IMMUNE to Denials

```python
# DifferentialDenial NEVER weakens categorical evidence
# This is by design, not a bug

denial = DifferentialDenial(
    original_trace_id="mark-123",
    challenged_principle="Composable",
    severity=0.5,
)

# If the agent has categorical evidence for Composable:
draw = PrincipleDraw("Composable", 1.0, EvidenceType.CATEGORICAL, ...)
# → Denial is logged but draw_strength stays at 1.0

# Philosophical justification:
# If a categorical proof "fails", the proof was never valid.
# The denial reveals a bug in the proof system, not a flaw in derivation.
```

### Gotcha: Origin → Agent Name Mapping

```python
# Mark origins are lowercase, derivation agent names are titlecase

mark.origin = "brain"  # From Mark
agent_name = "Brain"   # In DerivationRegistry

# extract_agents_from_mark() handles this mapping:
#   "witness" → ("Witness",)
#   "brain" → ("Brain",)
#   "logos" → ("Logos",)
#   "k-gent" → ("K-gent",)

# Partial matches also work:
#   "brain_crystal" → ("Brain",)  # Contains "brain"

# Unknown origins get titlecased:
#   "custom_thing" → ("Custom_thing",)
```

### Gotcha: Activity Store vs Registry Usage Count

```python
# Two different usage tracking mechanisms:

# Registry.get_usage_count(): Total cumulative usage
# → Used for stigmergic confidence: log10(count) * 0.25

# ActivityStore.get().usage_at_last_active: Snapshot at last activity
# → Used for stigmergic DECAY: days since last_active

# Confusion point: Registry tracks total, ActivityStore tracks recency
# Both are needed for correct stigmergic behavior
```

---

## Implementation Phases

### Phase 1: Registry Core ✅ (2025-12-22)
- [x] `Derivation` dataclass with tier ceiling enforcement
- [x] `PrincipleDraw` dataclass with decay
- [x] `EvidenceType` enum with decay rates
- [x] `DerivationTier` enum with ordering and ceilings
- [x] `DerivationRegistry` with bootstrap seeding
- [x] Inherited confidence computation (product with floor)
- [x] DAG with cycle detection (Law 4)
- [x] Confidence propagation through DAG (Law 5)
- [x] Evidence update methods (ASHC, usage counts)
- [x] 51 tests covering all laws

**Location:** `impl/claude/protocols/derivation/`

### Phase 2: ASHC Integration ✅ (2025-12-22)
- [x] `extract_principle_evidence()` from ASHC output
- [x] `update_derivation_from_ashc()` bridge
- [x] `merge_principle_draws()` with proper categorical/empirical handling
- [x] `sync_from_principle_registry()` for causal penalty integration
- [x] `sync_to_principle_registry()` for reverse updates
- [x] `lemma_strengthens_derivation()` for categorical evidence
- [x] 33 tests covering all bridge functions

**Location:** `impl/claude/protocols/derivation/ashc_bridge.py`

**Key Design Decisions:**
- Duck typing for ASHC types (enables testability)
- Categorical evidence never demoted by empirical
- Empirical evidence weighted average with 60% recency bias
- PrincipleRegistry credibility modulates draw_strength

### Phase 3: Witness Integration ✅ (2025-12-22)
- [x] Mark → stigmergic update (mark_updates_stigmergy)
- [x] DifferentialDenial → derivation weakening (denial_weakens_derivation)
- [x] Walk → aggregate updates (walk_updates_derivations)
- [x] 26 tests covering all bridge functions

**Location:** `impl/claude/protocols/derivation/witness_bridge.py`

**Key Design Decisions:**
- Duck typing for Mark/Walk (enables testability without full witness import)
- Categorical immunity: DifferentialDenials never weaken categorical evidence
- Origin → Agent mapping: handles lowercase origin → Titlecase derivation names
- Batch over incremental: walk_updates_derivations is preferred for efficiency

### Phase 4: Decay & Refresh ✅ (2025-12-22)
- [x] Time-based decay for non-categorical evidence (apply_evidence_decay)
- [x] Stigmergic decay for unused agents (apply_stigmergic_decay)
- [x] Periodic ASHC refresh mechanism (apply_ashc_refresh)
- [x] Full decay cycle orchestration (run_decay_cycle)
- [x] Activity tracking for stigmergic decay (ActivityRecord, ActivityStore)
- [x] Refresh scheduling for ASHC (RefreshSchedule, RefreshStore)
- [x] 31 tests covering all decay functions

**Location:** `impl/claude/protocols/derivation/decay.py`

**Key Design Decisions:**
- DecayConfig for tunable parameters (half-life, thresholds)
- Stigmergic decay uses last_active timestamp, not just usage count
- Grace period (14 days default) before stigmergic decay begins
- ASHC refresh is optional—if no runner, skips without failure
- run_decay_cycle is idempotent (safe to run multiple times)

**Teaching Notes:**
- gotcha: Stigmergic decay ≠ evidence decay (different mechanisms)
- gotcha: Run decay cycle daily via cron or scheduler
- gotcha: ActivityStore and RefreshStore can be backed by D-gent for persistence

### Phase 5: Visualization ✅
- [x] DAG visualization (web component) — `DerivationDAG.tsx`
- [x] Confidence timeline charts — `ConfidenceTimeline.tsx`
- [x] Confidence breakdown (stacked bar) — `ConfidenceBreakdown.tsx`
- [x] Principle draw radar chart — `PrincipleRadar.tsx`
- [x] Portal token navigation — `DerivationPortal.tsx`
- [x] AGENTESE integration — `concept.derivation.*` paths

**Implementation Summary:**
- Backend: `protocols/agentese/contexts/concept_derivation.py` — 20 tests
- Frontend: `web/src/components/derivation/` — 5 visualization components
- Types: `web/src/api/types.ts` — DerivationDAG*, DerivationPortalToken, etc.
- Total: 161 derivation framework tests passing

**AGENTESE Paths:**
```
concept.derivation.manifest      — View DAG structure and overall confidence
concept.derivation.query         — Query a specific agent's derivation
concept.derivation.dag           — Get DAG structure for visualization
concept.derivation.confidence    — Get confidence breakdown for an agent
concept.derivation.propagate     — Force confidence propagation
concept.derivation.timeline      — Get confidence history over time
concept.derivation.principles    — Get principle draw breakdown
concept.derivation.navigate      — Navigate the derivation hypergraph
```

### Phase 6: Cross-Protocol Integration

> *"The protocols are not separate systems. They are projections of the same structure."*

This phase connects derivation to the broader kgents ecosystem. The insight: derivation is not just an internal bookkeeping system—it is the **trust backbone** that other protocols depend on. Each protocol contributes evidence; derivation synthesizes it into confidence.

#### 6.0 Architectural Principle: Evidence Convergence

All protocols produce evidence. Derivation consumes evidence. This is a many-to-one functor:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  EVIDENCE SOURCES                           EVIDENCE SINK               │
│                                                                          │
│  Exploration Harness ──── trails ───┐                                   │
│                                     │                                   │
│  Portal Tokens ─────── expansions ──┼───► DerivationRegistry ───► Trust │
│                                     │           │                       │
│  Typed-Hypergraph ─── navigation ───┤           │                       │
│                                     │           ▼                       │
│  File Operad ────────── traces ─────┘    ConfidenceUpdate               │
│                                                 │                       │
│                                                 ▼                       │
│                                          Propagation → DAG              │
└──────────────────────────────────────────────────────────────────────────┘
```

**The Flow Invariant:** Evidence flows *toward* derivation, never away. Derivation synthesizes, never generates evidence. This preserves the property that derivation confidence is *earned*, not claimed.

#### 6.1 Exploration Harness → Derivation Bridge

The Exploration Harness (spec/protocols/exploration-harness.md) collects evidence via trails. Trails *are* evidence.

**Core Insight:** Exploration patterns reveal principle instantiation:

| Trail Pattern | Principle Signaled | Strength |
|---------------|-------------------|----------|
| Long, diverse edges | Composable | 0.7-0.9 |
| Avoids loops | Generative | 0.6-0.8 |
| Depth before breadth | Curated | 0.5-0.7 |
| Committed claims | Ethical | 0.8-1.0 |
| Backtrack recovery | Heterarchical | 0.5-0.7 |

```python
@dataclass(frozen=True)
class TrailEvidence:
    """
    Bridge between exploration trails and derivation updates.

    Trails are *behavioral* evidence—they show what the agent actually did,
    not what it claimed. This is EvidenceType.EMPIRICAL.
    """

    trail_id: str
    agent_name: str
    principles_signaled: tuple[tuple[str, float], ...]  # (principle, strength)
    commitment_level: str  # "tentative" | "moderate" | "strong" | "definitive"

    @classmethod
    def from_trail(cls, trail: Trail, claim: Claim) -> "TrailEvidence":
        """Extract derivation evidence from an exploration trail."""
        principles = []

        # Long trails with diverse edge types → Composable
        if len(trail.steps) > 5:
            edge_diversity = len(set(s.edge_taken for s in trail.steps)) / len(trail.steps)
            if edge_diversity > 0.3:
                principles.append(("Composable", 0.5 + edge_diversity * 0.4))

        # Trails that avoid loops → Generative (novel exploration)
        visited = set()
        revisits = 0
        for step in trail.steps:
            if step.node in visited:
                revisits += 1
            visited.add(step.node)
        if revisits == 0 and len(trail.steps) > 3:
            principles.append(("Generative", 0.8))

        # Committed claims → Ethical (agent stands behind claim)
        if claim.commitment_level == "definitive":
            principles.append(("Ethical", 0.9))

        return cls(
            trail_id=trail.id,
            agent_name=trail.created_by.name,
            principles_signaled=tuple(principles),
            commitment_level=claim.commitment_level,
        )


async def apply_trail_evidence(
    evidence: TrailEvidence,
    registry: DerivationRegistry,
) -> Derivation | None:
    """
    Apply trail evidence to derivation.

    Law (Trail Evidence Additivity):
        Trails can only increase principle draw strength, not decrease.
        This reflects "evidence accumulates" from ASHC.
    """
    if not registry.exists(evidence.agent_name):
        return None

    derivation = registry.get(evidence.agent_name)
    if derivation.is_bootstrap:
        return derivation  # Bootstrap agents don't change

    # Merge principle draws, only increasing strength
    existing_draws = {d.principle: d for d in derivation.principle_draws}

    for principle, strength in evidence.principles_signaled:
        if principle in existing_draws:
            existing = existing_draws[principle]
            if strength > existing.draw_strength:
                existing_draws[principle] = replace(
                    existing,
                    draw_strength=strength,
                    evidence_sources=existing.evidence_sources + (f"trail:{evidence.trail_id}",),
                )
        else:
            existing_draws[principle] = PrincipleDraw(
                principle=principle,
                draw_strength=strength,
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=(f"trail:{evidence.trail_id}",),
            )

    updated = derivation.with_principle_draws(tuple(existing_draws.values()))
    registry._derivations[evidence.agent_name] = updated
    registry._propagate_confidence(evidence.agent_name)

    return updated
```

**Law 6.1: Trail Evidence Additivity**
```
∀ trail T, derivation D:
  apply_trail_evidence(T, D).principle_strength >= D.principle_strength

Trails can only strengthen, never weaken. (Negative evidence comes via Witness denials.)
```

**Integration Points:**
- `ExplorationHarness.commit()` → `apply_trail_evidence()`
- `Trail.serialize()` → `Evidence.evidence_sources`
- `ASHCCommitment.can_commit()` gates evidence strength

**Location:** `impl/claude/protocols/derivation/exploration_bridge.py`

#### 6.2 Portal Token → Derivation Sync

Portal Tokens (spec/protocols/portal-token.md) carry trust levels. But this is a *bidirectional* relationship:

1. **Portal → Derivation**: Expansion events contribute to stigmergic evidence
2. **Derivation → Portal**: Confidence gates portal trust level

```python
@dataclass(frozen=True)
class PortalDerivationSync:
    """
    Bidirectional sync between portal tokens and derivation confidence.

    The insight: portals are *used* by agents. Usage patterns
    (expansions, depth, frequency) signal that an agent is useful.
    This is stigmergic evidence.
    """

    @staticmethod
    async def portal_expansion_to_derivation(
        signal: PortalOpenSignal,
        registry: DerivationRegistry,
    ) -> None:
        """
        Portal expansion events contribute stigmergic evidence.

        Law 6.2a: Expansion events increment usage count.
        """
        for path in signal.paths_opened:
            # Extract agent name from path (e.g., "world.brain" → "Brain")
            agent_name = _path_to_agent_name(path)
            if registry.exists(agent_name):
                registry.increment_usage(agent_name)

    @staticmethod
    def derivation_to_portal_trust(
        agent_name: str,
        registry: DerivationRegistry,
    ) -> float:
        """
        Compute portal trust from derivation confidence.

        Law 6.2b: Portal trust is bounded by derivation confidence.

        Trust = min(total_confidence, tier.ceiling * 0.9)

        The 0.9 factor ensures portals are slightly more conservative
        than raw confidence—trust must be earned through use.
        """
        if not registry.exists(agent_name):
            return 0.3  # Unknown agents get low trust

        derivation = registry.get(agent_name)
        return min(
            derivation.total_confidence,
            derivation.tier.ceiling * 0.9,
        )
```

**Laws:**

**Law 6.2a: Portal Usage Accumulates**
```
∀ portal expansion E on agent A:
  registry.usage_count(A)' = registry.usage_count(A) + 1
```

**Law 6.2b: Trust Bounded by Confidence**
```
∀ agent A:
  portal_trust(A) <= derivation_confidence(A)
```

**Location:** `impl/claude/protocols/derivation/portal_bridge.py`

#### 6.3 Typed-Hypergraph → Derivation as Context

The Typed-Hypergraph (spec/protocols/typed-hypergraph.md) provides navigation. Derivation becomes a *layer* in this hypergraph:

```python
class DerivationHyperedgeResolver:
    """
    Hyperedge resolver for derivation relationships.

    Adds three edge types to the typed-hypergraph:
    - derives_from: Direct ancestry
    - shares_principle: Agents that draw on the same principle
    - confidence_flows_to: Confidence propagation path
    """

    EDGE_TYPES = frozenset({"derives_from", "shares_principle", "confidence_flows_to"})

    def __init__(self, registry: DerivationRegistry):
        self._registry = registry

    async def resolve(
        self,
        source: str,
        edge_type: str,
        observer: Observer,
    ) -> list[ContextNode]:
        """
        Resolve derivation hyperedges.

        Observer-dependent: architects see all edges,
        developers see derives_from only.
        """
        if edge_type not in self.EDGE_TYPES:
            return []

        derivation = self._registry.get(source)
        if derivation is None:
            return []

        match edge_type:
            case "derives_from":
                return [
                    ContextNode(path=f"concept.agent.{name}")
                    for name in derivation.derives_from
                ]

            case "shares_principle" if observer.archetype in ("architect", "analyst"):
                # Find agents sharing principles
                shared = []
                for draw in derivation.principle_draws:
                    for other_name in self._registry.list_agents():
                        if other_name == source:
                            continue
                        other = self._registry.get(other_name)
                        if any(d.principle == draw.principle for d in other.principle_draws):
                            shared.append(ContextNode(path=f"concept.agent.{other_name}"))
                return shared

            case "confidence_flows_to":
                return [
                    ContextNode(path=f"concept.agent.{name}")
                    for name in self._registry.dependents(source)
                ]

        return []
```

**Integration:**

The resolver registers with the typed-hypergraph's resolver registry:

```python
# In protocols/agentese/contexts/hyperedge_resolvers.py
def register_derivation_resolvers(registry: DerivationRegistry):
    """Wire derivation edges into the typed-hypergraph."""
    resolver = DerivationHyperedgeResolver(registry)

    # Register for concept.agent.* paths
    for edge_type in resolver.EDGE_TYPES:
        register_resolver(f"concept.agent.*:{edge_type}", resolver.resolve)
```

**Law 6.3: Hyperedge Consistency**
```
∀ agent A:
  |resolve(A, "derives_from")| == |A.derives_from|

Hyperedge resolution is consistent with the derivation DAG.
```

**Location:** `impl/claude/protocols/derivation/hypergraph_bridge.py`

#### 6.4 File Operad → Confidence-Gated Operations

The File Operad (spec/protocols/file-operad.md) uses derivation confidence to gate dangerous operations.

**The Insight:** Not all agents should have the same privileges. Derivation confidence is the natural trust measure.

```python
@dataclass(frozen=True)
class OperationThresholds:
    """
    Confidence thresholds for file operations.

    These are calibrated to tier ceilings:
    - read: 0.3 (anyone can read)
    - annotate: 0.4 (low bar for notes)
    - write: 0.5 (needs some trust)
    - delete: 0.7 (only trusted agents)
    - execute: 0.8 (only highly trusted)
    - promote: 0.85 (JEWEL tier minimum)
    """

    read: float = 0.3
    annotate: float = 0.4
    write: float = 0.5
    delete: float = 0.7
    execute: float = 0.8
    promote: float = 0.85

    def threshold_for(self, operation: str) -> float:
        return getattr(self, operation, 0.5)


@dataclass(frozen=True)
class ConfidenceGateResult:
    """Result of checking operation against confidence."""

    allowed: bool
    agent_confidence: float
    threshold: float
    reason: str

    @classmethod
    def check(
        cls,
        operation: str,
        agent_name: str,
        registry: DerivationRegistry,
        thresholds: OperationThresholds = OperationThresholds(),
    ) -> "ConfidenceGateResult":
        """
        Check if agent can perform operation.

        Law 6.4: Confidence gates operations.
        """
        threshold = thresholds.threshold_for(operation)

        if not registry.exists(agent_name):
            return cls(
                allowed=False,
                agent_confidence=0.0,
                threshold=threshold,
                reason=f"Unknown agent '{agent_name}' has no derivation",
            )

        derivation = registry.get(agent_name)
        confidence = derivation.total_confidence

        if confidence >= threshold:
            return cls(
                allowed=True,
                agent_confidence=confidence,
                threshold=threshold,
                reason=f"Confidence {confidence:.2f} >= threshold {threshold:.2f}",
            )
        else:
            return cls(
                allowed=False,
                agent_confidence=confidence,
                threshold=threshold,
                reason=f"Confidence {confidence:.2f} < threshold {threshold:.2f}",
            )
```

**Law 6.4: Monotonic Trust**
```
∀ operation O₁, O₂ where threshold(O₁) < threshold(O₂):
  allowed(A, O₂) → allowed(A, O₁)

If an agent can delete, it can also read.
```

**Integration:**

```python
# In protocols/file_operad/core.py
async def apply_with_confidence_gate(
    operation: FileOperadOperation,
    registry: DerivationRegistry,
) -> FileOperadResult:
    """Apply operation with confidence gating."""

    gate_result = ConfidenceGateResult.check(
        operation=operation.operation_type,
        agent_name=operation.requester,
        registry=registry,
    )

    if not gate_result.allowed:
        # Record denied operation for audit
        await witness_mark(
            action="file_operation_denied",
            target=operation.path,
            reason=gate_result.reason,
            requester=operation.requester,
        )
        return FileOperadResult.denied(gate_result.reason)

    # Proceed with operation
    result = await operation.execute()

    # Record successful operation
    await witness_mark(
        action=f"file_{operation.operation_type}",
        target=operation.path,
        confidence=gate_result.agent_confidence,
    )

    return result
```

**Location:** `impl/claude/protocols/derivation/file_operad_bridge.py`

#### 6.5 Teaching Notes (Gotchas)

**Gotcha: Bridge Order Matters**

```python
# The bridges should be wired in this order during bootstrap:
# 1. Exploration → Derivation (trails feed evidence)
# 2. Derivation → Portal (confidence gates trust)
# 3. Derivation → Hypergraph (resolver registration)
# 4. Derivation → File Operad (operation gating)

# Wrong order can cause:
# - Portals with incorrect trust (if wired before derivation)
# - File operations failing (if gating before evidence flows)
```

**Gotcha: Evidence vs. Confidence**

```python
# Evidence is ACCUMULATED (trails, marks, expansions)
# Confidence is COMPUTED (from evidence + inheritance)

# Don't try to set confidence directly:
derivation.stigmergic_confidence = 0.8  # Wrong!

# Let evidence flow:
registry.increment_usage(agent_name)  # Right!
```

**Gotcha: Bootstrap Agents are Immune**

```python
# All bridges must check for bootstrap agents:
if derivation.is_bootstrap:
    return  # Bootstrap agents don't change

# This is Law 3 (Bootstrap Indefeasibility) enforced at every bridge.
```

**Gotcha: Hyperedge Caching**

```python
# The hypergraph resolver should cache results:
# - derives_from: stable unless new agent registered
# - shares_principle: stable unless evidence changes
# - confidence_flows_to: stable unless DAG changes

# Invalidate cache on:
# - registry.register()
# - registry.update_evidence()
# - Any confidence propagation
```

#### 6.6 Implementation Summary

| Bridge | Source | Sink | Evidence Type |
|--------|--------|------|---------------|
| Exploration | Trails | principle_draws | EMPIRICAL |
| Portal | Expansions | usage_count | STIGMERGIC |
| Hypergraph | Navigation | N/A (read-only) | N/A |
| File Operad | Operations | usage_count | STIGMERGIC |

**Total Phase 6 Tests Target:** 60 tests across 4 bridge modules

**Location:** `impl/claude/protocols/derivation/`
```
exploration_bridge.py   # 15 tests
portal_bridge.py        # 15 tests
hypergraph_bridge.py    # 15 tests
file_operad_bridge.py   # 15 tests
```

---

### Phase 7: CLI & AGENTESE Paths

> *"If you can't query it, you don't have it."*

This phase exposes derivation through the standard kgents interfaces: CLI commands for humans, AGENTESE paths for agents. The goal is to make derivation confidence **visible and queryable** everywhere.

#### 7.0 Design Principles

1. **Consistent with existing CLI** — Follow `kg brain`, `kg witness` patterns
2. **AGENTESE-first** — CLI routes to AGENTESE paths (thin handler pattern)
3. **Rich output by default** — Use Rich for terminal visualization
4. **Plain text fallback** — Work without Rich installed
5. **Observer-aware** — Different views for different archetypes

#### 7.1 CLI Commands

The `kg derivation` command family exposes derivation to humans.

**Command Structure:**

```bash
kg derivation [subcommand] [args] [flags]
```

**Subcommands:**

| Command | AGENTESE Path | Description |
|---------|---------------|-------------|
| `show <agent>` | `concept.derivation.manifest` | Show derivation with confidence breakdown |
| `ancestors <agent>` | `concept.derivation.ancestors` | Trace lineage to bootstrap |
| `dependents <agent>` | `concept.derivation.dependents` | What derives from this agent? |
| `principles <agent>` | `concept.derivation.principles` | Principle draw details |
| `tree` | `concept.derivation.tree` | ASCII DAG of all derivations |
| `list [--tier T]` | `concept.derivation.list` | List agents by tier |
| `why <agent>` | `concept.derivation.why` | Natural language explanation |

**Examples:**

```bash
# Show Brain's derivation with confidence breakdown
$ kg derivation show Brain

  Brain (JEWEL tier)
  ══════════════════════════════════════════════════
  Confidence: 0.78 (ceiling: 0.85)

  Components:
    inherited:   0.65  (from Flux, Compose)
    empirical:   0.10  (ASHC: 0.33 × 0.3)
    stigmergic:  0.03  (usage: 847 marks)

  Derives from: Flux, Compose
  Dependents:   MorningCoffee, GhostAgent

  Principle Draws:
    Composable    ███████░░░  0.72  [EMPIRICAL]  trail:abc123
    Curated       █████░░░░░  0.54  [AESTHETIC]  code-review
    Joy-Inducing  ████░░░░░░  0.41  [AESTHETIC]  user-feedback

# Trace ancestry to bootstrap
$ kg derivation ancestors Brain

  Brain ← Flux ← Fix, Compose ← (bootstrap)
       └─────← Compose ← (bootstrap)

# ASCII tree of all derivations
$ kg derivation tree --tier jewel

  BOOTSTRAP
  ├── Id
  ├── Compose
  │   ├── Flux (FUNCTOR, 0.95)
  │   │   └── Brain (JEWEL, 0.78)
  │   └── Witness (JEWEL, 0.82)
  ├── Judge
  │   └── Gatekeeper (JEWEL, 0.80)
  └── ...

# Natural language explanation
$ kg derivation why Brain

  Brain derives its authority from Compose and Flux.

  Its confidence (0.78) comes from:
  - High inheritance from trusted ancestors
  - Moderate empirical evidence (33% ASHC pass rate)
  - Growing usage (847 Witness marks)

  Brain instantiates Composable (0.72) based on trail evidence,
  and Curated (0.54) based on aesthetic assessment.

  As a JEWEL-tier agent, Brain cannot exceed 0.85 confidence.
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON (for scripting) |
| `--verbose` | Include evidence sources |
| `--tier <tier>` | Filter by tier (bootstrap, functor, polynomial, operad, jewel, app) |
| `--min-confidence <n>` | Filter by minimum confidence |

#### 7.2 AGENTESE Paths

Derivation exposes through `concept.derivation.*` paths.

**Path Structure:**

```
concept.derivation.manifest      — Current derivation status (default)
concept.derivation.ancestors     — Full ancestry chain
concept.derivation.dependents    — Agents that derive from this
concept.derivation.confidence    — Confidence breakdown
concept.derivation.principles    — Principle draw details
concept.derivation.tree          — DAG visualization
concept.derivation.list          — List all agents
concept.derivation.why           — Natural language explanation
concept.derivation.navigate      — Hypergraph navigation (via §6.3)
```

**Node Registration:**

```python
@node(
    "concept.derivation.manifest",
    dependencies=("derivation_registry",),
)
class DerivationManifestNode(BaseLogosNode):
    """
    Manifest the derivation status for an agent.

    AGENTESE: concept.derivation.manifest

    Observer-dependent output:
    - developer: confidence + tier + ancestry
    - architect: + principle draws + evidence sources
    - analyst: + full DAG navigation
    """

    def __init__(self, derivation_registry: DerivationRegistry):
        self._registry = derivation_registry

    @aspect("manifest", category=AspectCategory.INTROSPECTIVE)
    async def manifest(
        self,
        agent_name: str,
        observer: Observer,
    ) -> Renderable:
        """Show derivation status for an agent."""
        derivation = self._registry.get(agent_name)
        if derivation is None:
            return BasicRendering(
                content=f"Unknown agent: {agent_name}",
                format="text",
            )

        return DerivationRendering(
            derivation=derivation,
            observer=observer,
            verbose=observer.archetype in ("architect", "analyst"),
        )
```

**Rendering Strategy:**

```python
@dataclass
class DerivationRendering(Renderable):
    """
    Multi-format rendering of derivation status.

    Supports:
    - CLI: Rich-formatted terminal output
    - JSON: Structured data for scripting
    - marimo: Interactive notebook widget
    """

    derivation: Derivation
    observer: Observer
    verbose: bool = False

    def to_cli(self) -> str:
        """Rich terminal output."""
        lines = []
        d = self.derivation

        # Header
        lines.append(f"  {d.agent_name} ({d.tier.value.upper()} tier)")
        lines.append("  " + "═" * 50)

        # Confidence breakdown
        lines.append(f"  Confidence: {d.total_confidence:.2f} (ceiling: {d.tier.ceiling:.2f})")
        lines.append("")
        lines.append("  Components:")
        lines.append(f"    inherited:   {d.inherited_confidence:.2f}")
        lines.append(f"    empirical:   {min(0.2, d.empirical_confidence * 0.3):.2f}")
        lines.append(f"    stigmergic:  {d.stigmergic_confidence * 0.1:.2f}")

        # Ancestry
        if d.derives_from:
            lines.append("")
            lines.append(f"  Derives from: {', '.join(d.derives_from)}")

        # Principle draws (if verbose or architect)
        if self.verbose and d.principle_draws:
            lines.append("")
            lines.append("  Principle Draws:")
            for draw in d.principle_draws:
                bar = self._confidence_bar(draw.draw_strength)
                lines.append(
                    f"    {draw.principle:<14} {bar}  {draw.draw_strength:.2f}  "
                    f"[{draw.evidence_type.value.upper()}]"
                )

        return "\n".join(lines)

    def to_json(self) -> dict:
        """Structured JSON output."""
        d = self.derivation
        return {
            "agent_name": d.agent_name,
            "tier": d.tier.value,
            "confidence": {
                "total": d.total_confidence,
                "ceiling": d.tier.ceiling,
                "inherited": d.inherited_confidence,
                "empirical": d.empirical_confidence,
                "stigmergic": d.stigmergic_confidence,
            },
            "derives_from": list(d.derives_from),
            "principle_draws": [
                {
                    "principle": draw.principle,
                    "strength": draw.draw_strength,
                    "evidence_type": draw.evidence_type.value,
                    "sources": list(draw.evidence_sources),
                }
                for draw in d.principle_draws
            ],
        }

    @staticmethod
    def _confidence_bar(confidence: float, width: int = 10) -> str:
        """ASCII confidence bar."""
        filled = int(confidence * width)
        return "█" * filled + "░" * (width - filled)
```

#### 7.3 CLI Handler Implementation

**Pattern: Thin Routing Shim**

Following the `brain_thin.py` pattern, the CLI handler routes to AGENTESE paths:

```python
"""
Derivation Handler: CLI for querying agent derivations.

"Every agent can trace its lineage to Id, Compose, or Ground."

AGENTESE Path Mapping:
    kg derivation            -> concept.derivation.manifest
    kg derivation show ...   -> concept.derivation.manifest
    kg derivation ancestors  -> concept.derivation.ancestors
    kg derivation dependents -> concept.derivation.dependents
    kg derivation principles -> concept.derivation.principles
    kg derivation tree       -> concept.derivation.tree
    kg derivation list       -> concept.derivation.list
    kg derivation why        -> concept.derivation.why

See: spec/protocols/derivation-framework.md §7
"""

DERIVATION_SUBCOMMAND_TO_PATH = {
    "show": "concept.derivation.manifest",
    "ancestors": "concept.derivation.ancestors",
    "dependents": "concept.derivation.dependents",
    "principles": "concept.derivation.principles",
    "tree": "concept.derivation.tree",
    "list": "concept.derivation.list",
    "why": "concept.derivation.why",
}

DEFAULT_PATH = "concept.derivation.manifest"


def cmd_derivation(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Derivation Framework: Route to concept.derivation.* paths.

    All business logic is in protocols/derivation/. This handler only routes.
    """
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    subcommand = _parse_subcommand(args)
    path = route_to_path(subcommand, DERIVATION_SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    return project_command(path, args, ctx)
```

#### 7.4 Laws

**Law 7.1: CLI-AGENTESE Isomorphism**
```
∀ CLI command C:
  ∃ AGENTESE path P such that C routes to P

The CLI is a projection of AGENTESE, not a separate system.
```

**Law 7.2: Observer Consistency**
```
∀ observer O, agent A:
  CLI output for A with observer O ≡ AGENTESE output for A with observer O

Same observer, same output, regardless of interface.
```

**Law 7.3: JSON Roundtrip**
```
∀ derivation D:
  from_json(D.to_json()) ≡ D (for serializable fields)

JSON output is complete and reversible.
```

#### 7.5 Teaching Notes (Gotchas)

**Gotcha: Agent Name Resolution**

```python
# CLI accepts flexible agent names:
kg derivation show brain      # lowercase
kg derivation show Brain      # capitalized
kg derivation show BRAIN      # uppercase

# The handler normalizes:
def normalize_agent_name(name: str) -> str:
    """Normalize to Title case for registry lookup."""
    return name.title()
```

**Gotcha: Observer from Context**

```python
# CLI infers observer from invocation context:
def get_observer_from_ctx(ctx: InvocationContext) -> Observer:
    """Infer observer archetype from context."""
    if ctx and ctx.user_archetype:
        return Observer(id=ctx.user_id, archetype=ctx.user_archetype)
    return Observer(id="cli", archetype="developer")  # default
```

**Gotcha: Rich Fallback**

```python
# Always provide plain text fallback:
def render_output(rendering: Renderable, use_rich: bool) -> str:
    """Render with Rich if available, else plain text."""
    if use_rich and HAS_RICH:
        return rendering.to_rich()
    return rendering.to_plain()
```

**Gotcha: Cyclic Import Avoidance**

```python
# Don't import derivation registry at module level in CLI:
def cmd_derivation(args, ctx):
    from protocols.derivation import get_registry  # Import inside function
    registry = get_registry()
```

#### 7.6 Implementation Summary

| Component | Location | Description |
|-----------|----------|-------------|
| CLI Handler | `protocols/cli/handlers/derivation.py` | Thin routing shim |
| AGENTESE Nodes | `protocols/agentese/contexts/derivation_context.py` | 8 nodes |
| Rendering | `protocols/derivation/rendering.py` | Multi-format output |
| Tests | `protocols/derivation/_tests/test_cli.py` | 20 tests |

**Total Phase 7 Tests Target:** 40 tests
- CLI handler routing: 10 tests
- AGENTESE node rendering: 20 tests
- Rendering formats: 10 tests

**Dependencies:**
- Phase 6 bridges (for hypergraph navigation)
- Rich (optional, for terminal formatting)
- CLI projection infrastructure

---

## Connection to Heritage

| Heritage | Connection |
|----------|------------|
| ASHC | Empirical evidence source |
| Bootstrap | Axiom base (confidence = 1.0) |
| Agent-as-Witness | Stigmergic evidence via marks |
| Polynomial Functors | Tier structure mirrors category |
| Kleppmann | LLM proofs with mechanical verification |
| TextGRAD | Gradual refinement of confidence |
| Exploration Harness | Trail evidence → principle draws (§6.1) |
| Portal Tokens | Trust ↔ stigmergic confidence bidirectional sync (§6.2) |
| Typed-Hypergraph | `derives_from`, `shares_principle`, `confidence_flows_to` hyperedges (§6.3) |
| File Operad | Confidence-gated operations with thresholds (§6.4) |

---

## The Philosophical Stance

This framework embodies Kent's insight:

> *"An agent is a thing that justifies its behavior."*

The derivation IS the justification. An agent without derivation is not an agent—it's a mystery.

The confidence is Bayesian, not Boolean. We don't prove correctness; we accumulate evidence. The bootstrap provides the axiom base. Everything else is a theorem with probabilistic confidence.

> *"The proof IS the decision."*

Having a derivation is constitutive of agency. The derivation doesn't just describe the agent—it IS part of what makes the agent an agent.

---

## Philosophical Clarifications (Fusion Session 2025-12-22)

### Derivation IS Identity

The derivation is not metadata *about* the agent—it IS the agent's identity. Think of yourself as your coherent self. The derivation chain plus behavior is what constitutes the agent.

```
Agent ≠ Code + Derivation
Agent = Derivation (which includes behavior specification)
```

### Categorical Evidence is Moot by Construction

Q: "Should 1000 failing ASHC runs challenge categorical proofs?"

A: By construction, categorical laws ARE laws. If 1000 pieces of negative evidence existed, the "law" wasn't a law. This scenario is moot—it would indicate a bug in the proof system, not a challenge to the framework.

The hierarchy `Categorical > Empirical` stands, but not because we're being rigid—because categorical proofs that fail weren't categorical.

### Discredited Principles Are Still Drawable

Agents CAN and SHOULD draw from discredited principles. The PrincipleRegistry tracks *predictiveness*, not *permissibility*. An agent drawing on a discredited principle is making a choice with eyes open.

The bridge flow is correct:
```
PrincipleRegistry.credibility → modulates → PrincipleDraw.draw_strength
```

This means: "This agent draws on Principle X, but we've learned X isn't predictive of success, so we weight it accordingly."

### Somatic Evidence: Placeholder

Somatic evidence (Kent's Mirror Test, Constitution Article IV) will be engineered into the system when needed. The type exists; the input mechanism is TBD.

### Generativity: Honest Assessment

The spec may not yet be fully generative—deleting `ashc_bridge.py` might not regenerate identically from spec alone. This is acknowledged technical debt, not a design flaw.

---

*"Bootstrap confidence is given. Derived confidence is earned."*

*"Every agent can trace its lineage to Id, Compose, or Ground."*

---

**Filed:** 2025-12-22
**Updated:** 2025-12-22
**Status:** Complete — 306 tests passing (244 derivation + 20 AGENTESE + 42 CLI)
