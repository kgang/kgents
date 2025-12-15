# Enhanced Systems Vision: H-gents as Hybrid Minds

**Status:** Specification Draft v3.0
**Phase:** STRATEGIZE
**Prerequisites:** `../principles.md`, `spec/h-gents/README.md`, `docs/vision-unified-systems-enhancements.md`
**Guard [phase=STRATEGIZE][entropy=0.08][law_check=true]:** This is strategy, not implementation.

---

## The Core Insight

> *"The agent must always be able to decide for itself how to approach the situation."*

This document proposes extending H-gents from their current "Hegelian/Hermeneutic" semantics to encompass a second interpretation: **Hybrid Minds**—the dual-process architecture of learned policies (fast) and LLM actors (slow).

**The Dual H**: H-gents retain their dialectical introspection capabilities while gaining a new operational dimension:

| H-gent Interpretation | Purpose | Mechanism |
|----------------------|---------|-----------|
| **Hegelian** (existing) | Dialectical synthesis, shadow integration | Thesis + Antithesis → Synthesis |
| **Hybrid** (new) | Cost-effective inference through progressive downgrade | Policy + Actor → Behavior |

**Constraint:** To avoid category explosion, we implement **sparse projections**—the full theoretical richness exists, but practice uses constrained instantiations.

---

## Part I: The Two Minds Architecture

### 1.1 The Hybrid Mind Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           H-GENT: HYBRID MINDS                              │
│                                                                              │
│   ┌─────────────────────────────────────┐   ┌─────────────────────────────┐ │
│   │         LEARNED POLICIES            │   │          ACTOR              │ │
│   │         (System 1: Fast)            │   │      (System 2: Slow)       │ │
│   │                                     │   │                             │ │
│   │  ┌───────────┐   ┌───────────────┐  │   │  ┌───────────────────────┐  │ │
│   │  │ Predictor │   │ Value Function│  │   │  │  LLM-backed Operator  │  │ │
│   │  │           │   │   Operator    │  │   │  │                       │  │ │
│   │  │ P(a|s,π)  │   │   V(s) / Q(s,a)│ │   │  │  Deliberation, Novel  │  │ │
│   │  └───────────┘   └───────────────┘  │   │  │  Situations, Creation │  │ │
│   │                                     │   │  └───────────────────────┘  │ │
│   └─────────────────────────────────────┘   └─────────────────────────────┘ │
│                                                                              │
│   PRINCIPLE: Category-theoretic substitutability enables progressive        │
│   downgrade from Actor → Policies as data accumulates.                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

The dual-process theory (Kahneman's System 1/System 2) maps naturally to agent architectures:

| System | Characteristics | H-gent Implementation |
|--------|----------------|----------------------|
| **System 1** | Fast, automatic, low-cost | Decision trees, lookup tables, fine-tuned small models |
| **System 2** | Slow, deliberate, expensive | Full LLM calls with reasoning chains |

**The Key Insight:** These systems are **categorically substitutable**. If a policy produces outputs equivalent to the actor for a given input distribution, they are interchangeable morphisms.

### 1.2 The Progressive Downgrade Functor

**The Categorical Insight:** If two morphisms `f: A → B` and `g: A → B` produce equivalent outputs for the same inputs (within tolerance), they are **substitutable**. The category doesn't care which one you use.

This enables a **precision functor** that maps between implementation spaces:

```
Precision: ImplementationSpace → ImplementationSpace

Where ImplementationSpace has objects:
  - LLM-backed (expensive, high-precision, novel-capable)
  - Fine-tuned (moderate, domain-specific)
  - Policy-based (cheap, fast, verifiable)

And morphisms are verified-equivalent transformations.
```

**The Protocol:**

```python
class HybridMind(Functor[Agent, Agent]):
    """
    H-gent functor that progressively substitutes expensive operations
    with cheaper equivalents as evidence accumulates.

    This is the operational dual of Hegelian H-gents:
    - Hegelian: Thesis + Antithesis → Synthesis (dialectic on ideas)
    - Hybrid: Actor + Evidence → Policy (dialectic on computation)

    Both are synthesis operations; both preserve categorical laws.
    """

    def lift(self, agent: Agent[A, B]) -> Agent[A, B]:
        """Wrap agent with hybrid mind capability."""
        return HybridAgent(
            actor=agent,  # System 2: The expensive, deliberate mind
            precision_ladder=[
                self.try_decision_tree,   # Cheapest, fastest, interpretable
                self.try_finetuned,       # Middle ground
                self.try_cached,          # Pattern match
                agent.invoke,             # Fallback to full LLM
            ],
            evidence=SubstitutionEvidence(),
        )

    async def try_decision_tree(
        self,
        input: A,
        evidence: SubstitutionEvidence
    ) -> B | NotConfident:
        """
        Attempt decision tree resolution.

        Decision trees are EXTRACTED from LLM traces:
        1. Collect (input, LLM_reasoning, output) triples
        2. Fit decision tree to predict output from input features
        3. Use tree for high-confidence cases

        This is the pragmatic starting point. Future work may
        graduate to differentiable logic or neural theorem provers.
        """
        if evidence.tree_confidence(input) > 0.9:
            return self.decision_tree.predict(input)
        return NotConfident()
```

### 1.3 Research Foundation: Policy Distillation

The Two Minds architecture draws on established research in making LLMs more cost-effective:

#### 1.3.1 Knowledge Distillation (Hinton et al.)

The foundational technique: train a smaller "student" model to match the soft probability distributions of a larger "teacher" model, not just its hard labels.

```
Student Loss = α × CrossEntropy(student, labels) + (1-α) × KL(student_soft, teacher_soft)
```

**Relevance to H-gents:** The "actor" (LLM) is the teacher; the "policy" (decision tree, fine-tuned model) is the student.

#### 1.3.2 Step-by-Step Distillation

Rather than distilling only final outputs, capture the reasoning chain:

```python
# Anti-pattern: Outcome-only distillation
student.train(inputs=queries, targets=llm_final_answers)

# Pattern: Process distillation
student.train(
    inputs=queries,
    targets=llm_reasoning_chains,  # Include the "why"
    process_reward=True,           # Reward correct intermediate steps
)
```

**Relevance to H-gents:** Policies learn not just "what" but "how"—preserving explainability.

#### 1.3.3 Router Models (Speculative Decoding)

Use a small model to predict when a large model is necessary:

```python
class HybridRouter:
    """Decide which mind to use."""

    def route(self, input: A) -> Mind:
        complexity = self.small_model.estimate_complexity(input)
        if complexity < THRESHOLD_TRIVIAL:
            return Mind.POLICY  # Decision tree handles this
        elif complexity < THRESHOLD_MODERATE:
            return Mind.FINETUNED  # Small LLM handles this
        else:
            return Mind.ACTOR  # Full LLM required
```

**Relevance to H-gents:** The router itself is a learned policy—meta-cognition about which mind to invoke.

#### 1.3.4 Process Reward Models (PRMs)

Instead of rewarding only correct final answers, reward correct reasoning steps:

```python
# Outcome Reward Model (ORM)
reward = 1.0 if final_answer_correct else 0.0

# Process Reward Model (PRM)
reward = sum(step_correctness for step in reasoning_chain) / len(chain)
```

**Relevance to H-gents:** PRMs enable training policies that reason correctly, not just produce correct outputs by luck.

### 1.4 The Elaborateness Metric

**Observation:** The "precision" of a response can be proxied by:
1. **Elaborateness of invocation** — How many sub-agents were spawned?
2. **Expensiveness of model** — Opus vs Sonnet vs Haiku vs Policy
3. **Token metabolism** — How much entropy was consumed?

As data accumulates, these metrics should trend downward for common situations while maintaining output quality.

```python
@dataclass
class ElaboratenessMetric:
    """Track the cost of agent responses over time."""

    agent_spawns: int        # How many sub-agents were called?
    model_tier: ModelTier    # OPUS > SONNET > HAIKU > POLICY
    tokens_consumed: int     # Total token usage
    wall_time_ms: float      # Response latency

    @property
    def cost_score(self) -> float:
        """Lower is better. Tracks efficiency improvement."""
        return (
            self.agent_spawns * 10 +
            self.model_tier.value * 5 +
            self.tokens_consumed * 0.001 +
            self.wall_time_ms * 0.01
        )
```

**The Goal:** For a mature H-gent system, the average `cost_score` decreases over time while output quality remains constant or improves.

---

## Part II: H-gent as Hybrid Mind Polynomial

### 2.1 The H-MIND Polynomial

Extending AD-002 (Polynomial Generalization), we define the Hybrid Mind polynomial:

```python
H_MIND_POLYNOMIAL = PolyAgent(
    positions=frozenset([
        HMindPhase.ROUTING,      # Deciding which mind to use
        HMindPhase.POLICY_EXEC,  # Executing learned policy
        HMindPhase.ACTOR_EXEC,   # Executing LLM actor
        HMindPhase.LEARNING,     # Updating policies from actor traces
        HMindPhase.VALIDATING,   # Verifying policy ≅ actor equivalence
    ]),
    directions=lambda phase: VALID_INPUTS[phase],
    transition=h_mind_transition,
)

VALID_INPUTS = {
    HMindPhase.ROUTING: frozenset([
        RouteInput,      # Query to classify
    ]),
    HMindPhase.POLICY_EXEC: frozenset([
        PolicyInput,     # Execute learned policy
    ]),
    HMindPhase.ACTOR_EXEC: frozenset([
        ActorInput,      # Execute LLM actor
    ]),
    HMindPhase.LEARNING: frozenset([
        TraceInput,      # (input, actor_trace, output) triple
    ]),
    HMindPhase.VALIDATING: frozenset([
        ValidationInput, # Compare policy vs actor outputs
    ]),
}
```

### 2.2 The H-MIND Operad

The composition grammar for Hybrid Mind operations:

```python
H_MIND_OPERAD = Operad(
    operations={
        "route": Operation(
            arity=1,
            signature="Query → Mind",
            description="Decide which mind handles the query",
        ),
        "execute": Operation(
            arity=2,
            signature="(Mind, Query) → Response",
            description="Execute the selected mind on the query",
        ),
        "learn": Operation(
            arity=1,
            signature="Trace → PolicyUpdate",
            description="Extract policy from actor trace",
        ),
        "validate": Operation(
            arity=2,
            signature="(Policy, Actor) → EquivalenceEvidence",
            description="Verify policy produces same outputs as actor",
        ),
        "downgrade": Operation(
            arity=2,
            signature="(Agent, Evidence) → Agent",
            description="Replace expensive ops with cheap equivalents",
        ),
    },
    laws=[
        # Idempotence: validating twice is same as once
        Law("validate(validate(p, a), a) ≡ validate(p, a)"),
        # Monotonicity: more evidence → more downgrade
        Law("evidence₁ ⊆ evidence₂ ⟹ cost(downgrade(a, e₁)) ≥ cost(downgrade(a, e₂))"),
    ],
)
```

### 2.3 Integration with Existing H-gents

The Hybrid Mind interpretation **composes** with existing Hegelian H-gents:

```python
class UnifiedHGent(Agent[HGentInput, HGentOutput]):
    """
    H-gent that combines both interpretations:
    - Hegelian: Dialectical synthesis on concepts
    - Hybrid: Cost-effective inference through policy learning

    The synthesis: Use cheap policies to detect when expensive
    dialectic synthesis is actually needed.
    """

    def __init__(
        self,
        hegelian: HegelAgent,
        hybrid_mind: HybridMind,
    ):
        self.hegelian = hegelian
        self.hybrid_mind = hybrid_mind

    async def invoke(self, input: HGentInput) -> HGentOutput:
        # Hybrid decides if we need full dialectic
        routing = await self.hybrid_mind.route(input)

        if routing.mind == Mind.POLICY:
            # Fast path: Learned policy handles common tensions
            return await self.hybrid_mind.policy.invoke(input)
        else:
            # Slow path: Full Hegelian synthesis for novel tensions
            return await self.hegelian.invoke(input)
```

**The Meta-Insight:** The Hybrid Mind is itself a dialectic:
- **Thesis:** Expensive, thorough LLM reasoning (Actor)
- **Antithesis:** Cheap, fast learned behavior (Policy)
- **Synthesis:** Adaptive selection that preserves quality while minimizing cost

---

## Part III: The Hidden Internal Model

### 3.1 Beyond Polynomial Functors

**Current AD-002 (Polynomial Generalization):**

```python
PolyAgent[S, A, B]:
    positions: FrozenSet[S]              # Valid states (modes)
    directions: Callable[[S], FrozenSet[A]]  # State-dependent valid inputs
    transition: Callable[[S, A], tuple[S, B]]  # State × Input → (State, Output)
```

**The Extension:** This captures state-dependent behavior, but misses the **hidden internal disposition** that colors how behavior manifests.

**Example:**
- Position: "Customer Service Agent"
- Direction: "Respond to complaint"
- **Hidden disposition**: "Feeling generous" vs "Feeling strict"

The disposition isn't another position—it's a **modifier** on how the position→direction mapping works.

### 3.2 Constrained Disposition Space

**Constraint:** To avoid category explosion, we define a **small, compatible** disposition space.

#### The Compatibility Relation

Not all dispositions compose meaningfully. We define a compatibility relation `~`:

```python
# Core dispositions (kept small)
class Disposition(Enum):
    NEUTRAL = "neutral"      # Default, no modification
    GENEROUS = "generous"    # Expand affordances, reduce friction
    STRICT = "strict"        # Contract affordances, increase rigor
    PLAYFUL = "playful"      # Increase entropy tolerance, humor
    FOCUSED = "focused"      # Reduce entropy, increase precision

# Compatibility relation (symmetric)
COMPATIBLE: set[tuple[Disposition, Disposition]] = {
    (NEUTRAL, d) for d in Disposition  # Neutral composes with anything
} | {
    (GENEROUS, PLAYFUL),    # Both expansive
    (STRICT, FOCUSED),      # Both contractive
}

def are_compatible(d1: Disposition, d2: Disposition) -> bool:
    return (d1, d2) in COMPATIBLE or (d2, d1) in COMPATIBLE
```

#### Composition Rule

```python
def compose_dispositions(d1: Disposition, d2: Disposition) -> Disposition:
    """
    Compose two dispositions if compatible.

    NEUTRAL is identity. Incompatible dispositions don't compose—
    the agent must choose one.
    """
    if d1 == Disposition.NEUTRAL:
        return d2
    if d2 == Disposition.NEUTRAL:
        return d1
    if are_compatible(d1, d2):
        # Compatible dispositions blend (implementation-specific)
        return blend(d1, d2)
    # Incompatible: agent chooses, no automatic composition
    raise IncompatibleDispositions(d1, d2)
```

#### Simplified Implementation

```python
@dataclass(frozen=True)
class DispositionModifiedPoly(Generic[S, A, B]):
    """
    Polynomial agent with single active disposition.

    Constraint: One disposition at a time. No composition explosion.
    """
    base: PolyAgent[S, A, B]
    active_disposition: Disposition = Disposition.NEUTRAL

    def with_disposition(self, d: Disposition) -> "DispositionModifiedPoly":
        """Switch disposition (not compose)."""
        return DispositionModifiedPoly(
            base=self.base,
            active_disposition=d,
        )

    @property
    def directions(self) -> Callable[[S], FrozenSet[A]]:
        """Disposition-modified direction function."""
        base_dirs = self.base.directions
        match self.active_disposition:
            case Disposition.GENEROUS:
                return lambda s: expand_affordances(base_dirs(s))
            case Disposition.STRICT:
                return lambda s: contract_affordances(base_dirs(s))
            case _:
                return base_dirs
```

### 3.3 The Indirection Layer

**The Key Insight:**

> "This acts as an extension to polynomial functions by adding indirection to the postures and directions of interaction → the hidden internal model."

The indirection is this: **We can't know if a person is feeling generous on the inside, but if they are feeling generous, for the different category theory roles they inhabit, we expect something different.**

This means:
1. **External observers** see positions and directions (the polynomial)
2. **Internal state** includes disposition (hidden from observers)
3. **Behavior** emerges from disposition × position × input
4. **Substitutability** still holds at the behavioral level (same outputs)

```python
class HiddenInternalModel:
    """
    The hidden internal model that colors all polynomial behavior.

    From the outside: You see an agent responding to inputs.
    From the inside: The disposition modifies every response.

    The category theory guarantees: If two agents with different
    internal dispositions produce identical outputs, they are
    substitutable at the behavioral level.
    """

    disposition: Disposition  # Hidden from external observers

    def manifest_through(self, poly: PolyAgent) -> PolyAgent:
        """Apply disposition to polynomial, yielding modified behavior."""
        return DispositionModifiedPoly(
            base=poly,
            active_disposition=self.disposition,
        )
```

---

## Part IV: AGENTESE as Re-Derivable Seed

### 4.1 Fully Open, Re-Derivable In Situ

**Your Insight:**

> "AGENTESE openness: fully open, and even further, it's most functional when re-derived in situ."

This is profound. AGENTESE is not a fixed protocol to adopt—it's a **generative grammar** that should be re-derived from principles in each context.

### 4.2 The Minimal Seed

What is the minimal seed that enables re-derivation?

**Candidate Seed (The DNA):**

```markdown
# AGENTESE DNA

1. **No View From Nowhere**: Every observation requires an observer.

2. **Five Contexts Only**: world.* | self.* | concept.* | void.* | time.*

3. **Handles Are Functors**: A path is a morphism Observer → Interaction.

4. **Affordances Are Polymorphic**: Same path, different observer, different actions.

5. **Category Laws Hold**: Identity and associativity must be verified.

6. **Nouns Are Frozen Verbs**: To read is to invoke.

7. **The Accursed Share**: Entropy budget exists; agents sip and tithe. Gratitude for waste.
```

**The Re-Derivation Protocol:**

```python
async def rederive_agentese(
    context: DerivationContext,
    seed: AGENTESEDna = DEFAULT_DNA,
) -> Logos:
    """
    Re-derive AGENTESE from first principles in this context.

    The spec is generative—each implementation derives it anew,
    constrained only by the DNA seed. This ensures:

    1. Context-appropriate instantiation
    2. No cargo-culting of irrelevant features
    3. The principles are understood, not just copied

    Many will attach to the first derivation, but the most
    functional implementations re-derive from principles.
    """
    # Start from the seven DNA axioms
    axioms = seed.axioms

    # Derive context resolvers from axioms + local constraints
    resolvers = await derive_context_resolvers(axioms, context)

    # Derive affordance grammar from axioms + observer types
    affordances = await derive_affordance_grammar(axioms, context.observers)

    # Verify category laws hold in this derivation
    await verify_laws(resolvers, affordances)

    return Logos(resolvers=resolvers, affordances=affordances)
```

### 4.3 Why Re-Derivation Matters

**The Anti-Pattern:** Copy-paste the AGENTESE implementation.

**The Pattern:** Understand the principles, derive the implementation.

Benefits of re-derivation:
1. **Context fit**: The derived implementation fits the local context perfectly
2. **Deep understanding**: You can't derive what you don't understand
3. **Evolution**: Each derivation can improve on the previous
4. **No legacy debt**: No carrying features that don't apply

---

## Part V: Integration with Workshop Manager

### 5.1 The Full System

The H-gent Hybrid Mind architecture integrates with the existing Workshop Manager to enable generative completion on objectives:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE ARCHITECTURE                                     │
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                      WORKSHOP MANAGER                                  │ │
│   │   Scout → Sage → Spark → Steady → Sync                                │ │
│   │   (5 Builder archetypes coordinate on user objectives)                 │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                       H-GENT HYBRID MINDS                              │ │
│   │                                                                        │ │
│   │   ┌─────────────────────────────────────────────────────────────────┐ │ │
│   │   │  POLICY (System 1)          ACTOR (System 2)                    │ │ │
│   │   │  ├─ Decision Trees           ├─ Full LLM Reasoning              │ │ │
│   │   │  ├─ Cached Patterns          ├─ Novel Situation Handling        │ │ │
│   │   │  └─ Fine-tuned Models        └─ Creative Generation             │ │ │
│   │   └─────────────────────────────────────────────────────────────────┘ │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │              DISPOSITION-MODIFIED POLYNOMIAL AGENTS                    │ │
│   │   PolyAgent[S, A, B] + Disposition → Modified Behavior                │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                 AGENTESE (Re-derived in situ)                          │ │
│   │   world.* | self.* | concept.* | void.* | time.*                      │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                    PROTOCOL ADAPTERS                                   │ │
│   │   MCP (tool access) | A2A (inter-agent) | [Future: ACP, ANP]          │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Generative Completion on Objectives

**The Loop:**

1. **User states objective** → Workshop Manager assigns builders
2. **Builders decompose** → Tasks for each builder archetype
3. **Each task invokes** → H-gent Hybrid Mind (router selects Policy or Actor)
4. **Progressive downgrade** → As patterns emerge, cheaper implementations
5. **Disposition colors** → Hidden internal model modifies behavior
6. **AGENTESE resolves** → Semantic paths to concrete operations
7. **Protocols execute** → MCP/A2A for external operations

---

## Part VI: Work Organization

### Wave 1: H-gent Hybrid Mind Foundation

**Scope:** Extend H-gents with Hybrid Mind architecture.

#### Chunk 1.1: Hybrid Mind Core
- **Task:** Define `HybridMind` functor with precision ladder
- **Task:** Implement `SubstitutionEvidence` accumulator
- **Task:** Create `HMindPhase` polynomial positions

#### Chunk 1.2: Decision Tree Extraction
- **Task:** Collect (input, LLM_reasoning, output) triples
- **Task:** Fit decision trees to predict output from input features
- **Task:** Wire trees to precision functor as cheapest option
- **Task:** Define confidence threshold for tree vs LLM fallback

#### Chunk 1.3: Router Model
- **Task:** Train small model to predict query complexity
- **Task:** Implement routing logic (Policy vs FineTuned vs Actor)
- **Task:** Add elaborateness metric tracking

---

### Wave 2: Disposition Layer

**Scope:** Add hidden internal model to polynomial agents.

#### Chunk 2.1: Disposition Algebra
- **Task:** Define `Disposition` type with composition laws
- **Task:** Implement `DispositionModifiedPoly` dataclass
- **Task:** Verify disposition composition preserves polynomial laws

#### Chunk 2.2: K-gent Integration
- **Task:** Add disposition field to K-gent eigenvector space
- **Task:** Implement `manifest_through` for disposition coloring
- **Task:** Wire disposition to Gatekeeper reasoning

---

### Wave 3: Protocol Adapters

**Scope:** AGENTESE as semantic layer above MCP/A2A.

#### Chunk 3.1: MCP Adapter
- **Task:** Complete U-gent HTTP/SSE transport
- **Task:** Map MCP tool calls → `world.tool.{name}.invoke`
- **Task:** Verify category laws across bridge

#### Chunk 3.2: A2A Adapter
- **Task:** Implement Agent Card generator from L-gent registry
- **Task:** Map A2A tasks → AGENTESE paths
- **Task:** Test inter-agent discovery

#### Chunk 3.3: AGENTESE Publication
- **Task:** Extract minimal DNA seed document
- **Task:** Write re-derivation guide
- **Task:** Publish spec as standalone repository

---

### Wave 4: Federation Substrate

**Scope:** Prepare for multi-town without building prematurely.

**Trigger:** $1K MRR

#### Chunk 4.1: Town Identity
- **Task:** Ensure stable Town UUIDs
- **Task:** Add `home_town` to Citizen model
- **Task:** Define `TownReference` for cross-town links

#### Chunk 4.2: Event Export
- **Task:** Ensure TownFlux events are serializable
- **Task:** Define federation event schema
- **Task:** Stub federation bus interface

---

## Part VII: Resolved Questions

### Q1: Disposition Composition → Compatibility Relation

**Resolution:** Use a tightly-scoped compatibility relation.

- 5 core dispositions: NEUTRAL, GENEROUS, STRICT, PLAYFUL, FOCUSED
- NEUTRAL is identity (composes with anything)
- Compatible pairs: (GENEROUS, PLAYFUL), (STRICT, FOCUSED)
- Incompatible pairs don't compose—agent must choose

This bounds the combinatorial space to ~10 valid combinations.

### Q2: Two Minds vs Full LLM → Progressive Downgrade

**Resolution:** Not a binary choice. The precision ladder enables graceful degradation:

1. **Decision Tree**: Fastest, cheapest, most interpretable
2. **Cached Pattern**: Fast, cheap, requires exact match
3. **Fine-tuned Model**: Moderate cost, domain-specific
4. **Full LLM**: Expensive, handles novel situations

Evidence accumulates → more queries handled at cheaper levels.

### Q3: Minimal Seed for Re-Derivation → 7 Axioms

**Resolution:** 7 axioms including Accursed Share:

1. No View From Nowhere
2. Five Contexts Only
3. Handles Are Functors
4. Affordances Are Polymorphic
5. Category Laws Hold
6. Nouns Are Frozen Verbs
7. **The Accursed Share** (entropy budget, sip, tithe)

### Q4: H-gent Dual Interpretation → Composition

**Resolution:** The Hegelian and Hybrid interpretations compose:

- **Hegelian H-gent**: Dialectic synthesis on concepts (thesis + antithesis → synthesis)
- **Hybrid H-gent**: Dialectic on computation (actor + evidence → policy)

Both are synthesis operations that preserve categorical structure.

### Q5: Federation at $1K MRR → Minimum Viable

**Resolution:** Approved minimum viable federation:

- **YES:** Cross-town citizen passport (visit, not migrate)
- **YES:** Public event visibility (see other town's events)
- **NO:** Cross-town economy, consensus, governance

This provides federation value without coordination complexity.

---

## Part VIII: Principles Alignment Check

| Principle | H-gent Hybrid Mind Alignment |
|-----------|------------------------------|
| **Tasteful** | Two minds—not kitchen sink; policy + actor only |
| **Curated** | Progressive downgrade curates which implementation handles each query |
| **Ethical** | Hidden disposition doesn't hide ethics (gatekeeper still applies) |
| **Joy-Inducing** | Disposition layer enables personality; cost savings → more interactions |
| **Composable** | Disposition is natural transformation (preserves composition) |
| **Heterarchical** | Agent decides which mind to use, not predetermined |
| **Generative** | Re-derivation in situ is ultimate generativity |

---

## Appendix A: Formal Definitions

### A.1 Disposition Algebra (Constrained)

```
Disposition = {NEUTRAL, GENEROUS, STRICT, PLAYFUL, FOCUSED}

Compatibility relation ~:
  NEUTRAL ~ d  for all d           (identity)
  GENEROUS ~ PLAYFUL               (expansive pair)
  STRICT ~ FOCUSED                 (contractive pair)

Composition (partial):
  NEUTRAL ∘ d = d                  (identity law)
  d ∘ NEUTRAL = d                  (identity law)
  d₁ ∘ d₂ = blend(d₁, d₂)  if d₁ ~ d₂
  d₁ ∘ d₂ = ⊥ (undefined)  if ¬(d₁ ~ d₂)

Constraint: At most 10 valid combinations (bounded).
```

### A.2 Progressive Downgrade Functor

```
PD: Agent[A,B] → Agent[A,B]

Where PD(f) tries in order:
  1. DecisionTree(f)   if confidence > θ_tree (0.9)
  2. FineTuned(f)      if confidence > θ_ft
  3. Cached(f)         if exact match
  4. f                 otherwise

Laws:
  PD(f) ≅ f            (behaviorally equivalent)
  PD(f >> g) = PD(f) >> PD(g)  (composition preserved)
```

### A.3 AGENTESE DNA (7 Axioms)

```
1. ObserverRequired:     ∀ invocation i. ∃ observer o. i(o)
2. FiveContexts:         Context ∈ {world, self, concept, void, time}
3. HandlesAreFunctors:   Handle: Observer → Interaction
4. PolymorphicAffordances: affordances(h, o₁) ≠ affordances(h, o₂) possible
5. CategoryLaws:         Id >> f ≡ f ≡ f >> Id; (f >> g) >> h ≡ f >> (g >> h)
6. NounsAreFrozenVerbs:  read(x) ≡ invoke(x.manifest)
7. AccursedShare:        ∃ budget b. sip(b) ∧ tithe(b) (entropy management)
```

### A.4 H-gent Dual Interpretation

```
H-GENT = HEGELIAN ⊕ HYBRID

Where:
  HEGELIAN: (Thesis, Antithesis) → Synthesis     (dialectic on concepts)
  HYBRID:   (Actor, Evidence) → Policy           (dialectic on computation)

Composition law:
  The result of HYBRID can be input to HEGELIAN:
  HEGELIAN(Policy₁, Policy₂) → SynthesizedPolicy

  The process of HEGELIAN can be optimized by HYBRID:
  HYBRID(HEGELIAN) → CheapDialectic (for common tensions)
```

---

*"The agent must always be able to decide for itself how to approach the situation."*
