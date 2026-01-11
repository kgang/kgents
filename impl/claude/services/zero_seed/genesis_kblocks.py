"""
Genesis K-Block Factory: The Self-Describing Seed.

"The proof IS the decision. The mark IS the witness. The seed IS the garden."

This module implements the K-Block content factory for the new kgents genesis.
Each K-Block is self-describing - it explains what it is, why it exists,
and how it connects to the Constitutional foundation.

22 K-Blocks organized into layers:
- L0 Axioms (4): A1 Entity, A2 Morphism, A3 Mirror, G Galois
- L1 Kernel (3): Compose, Judge, Ground
- L2 Derived (4): Id, Contradict, Sublate, Fix
- L1-L2 Principles (8): Constitution + 7 Principles
- L3 Architecture (4): ASHC, Metaphysical Fullstack, Hypergraph Editor, AGENTESE

See: plans/genesis-overhaul/ for design specifications
See: spec/bootstrap.md for axiom definitions
"""

from __future__ import annotations

from dataclasses import dataclass

# =============================================================================
# Core Data Types
# =============================================================================


@dataclass(frozen=True)
class GenesisKBlock:
    """
    A genesis K-Block for the self-describing seed.

    Genesis K-Blocks form the foundational layer of the kgents system.
    Each block:
    - Has a unique ID and title
    - Belongs to a layer (0-3)
    - Has a Galois loss measuring derivation distance
    - Contains self-describing markdown content
    - Tracks derivation from parent K-Blocks
    - Carries semantic tags for discovery

    Attributes:
        id: Unique identifier (e.g., "A1_ENTITY", "COMPOSABLE")
        title: Human-readable title
        layer: Layer in the epistemic holarchy (0=axiom, 1=kernel, 2=derived, 3=architecture)
        galois_loss: Derivation distance from ground truth [0.0, 1.0]
        content: Full markdown content (self-describing)
        derives_from: Parent K-Block IDs this derives from
        tags: Semantic tags for discovery and filtering
    """

    id: str
    title: str
    layer: int
    galois_loss: float
    content: str
    derives_from: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate K-Block constraints."""
        if not (0 <= self.layer <= 7):
            raise ValueError(f"Layer must be 0-7, got {self.layer}")
        if not (0.0 <= self.galois_loss <= 1.0):
            raise ValueError(f"Galois loss must be 0.0-1.0, got {self.galois_loss}")


# =============================================================================
# Genesis K-Block Factory
# =============================================================================


class GenesisKBlockFactory:
    """
    Factory for creating the 22 genesis K-Blocks.

    The factory produces K-Blocks organized into:
    - L0 Axioms: Pre-categorical axioms (A1, A2, A3, G)
    - L1 Kernel: Operational forms of axioms (Compose, Judge, Ground)
    - L2 Derived: Derived primitives (Id, Contradict, Sublate, Fix)
    - L1-L2 Principles: Constitution and the 7 principles
    - L3 Architecture: ASHC, Metaphysical Fullstack, Hypergraph Editor, AGENTESE

    Each K-Block is self-describing - it contains the information needed
    to understand what it is, why it exists, and how it connects to the
    Constitutional foundation.

    Usage:
        >>> factory = GenesisKBlockFactory()
        >>> all_blocks = factory.create_all()
        >>> entity_block = factory.create_a1_entity()
    """

    # =========================================================================
    # L0 Axioms (Pre-Categorical)
    # =========================================================================

    def create_a1_entity(self) -> GenesisKBlock:
        """Create the A1 Entity axiom K-Block."""
        content = """# A1: ENTITY - There Exist Things

> *"The irreducible claim that something IS."*

**Layer**: L0 (Pre-Categorical Axiom)
**Galois Loss**: 0.000 (Fixed Point)
**Evidence Tier**: CATEGORICAL

---

## Definition

**A1 (Entity)**: There exist things.

In category-theoretic terms: There exist *objects* in a category.

This is the foundational claim from which all else derives. Without entities:
- There is nothing to compose
- There is nothing to judge
- There is nothing to ground

## Mathematical Formulation

```
A1: exists Ob(C)   -- There exist objects in a category
```

## Why Irreducible

You cannot prove existence from non-existence. The claim that "something is"
must be *given*, not derived. It is the first act of creation.

A1 is a **fixed point** of restructuring: R(A1) = A1. No matter how you
try to decompose "there exist things," you get back "there exist things."

## What It Grounds

- The existence of agents as objects in a category
- The existence of prompts, documents, specifications
- The existence of Kent as the human oracle
- All K-Blocks (each K-Block IS an entity)
- The AGENTESE contexts: world.*, self.*, concept.*, void.*, time.*

## Connection to K-Block

Every K-Block is an entity. The `kind` field classifies the type of entity:
- FILE: document entity
- ZERO_NODE: axiom/value/goal entity
- AGENT_STATE: agent entity
- CRYSTAL: crystallized memory entity

## Loss Properties

```
L(A1) = 0.000     -- By definition: axioms have zero loss
d(A1, C(R(A1))) = 0   -- Round-trip preserves perfectly
```

---

*Axiom A1 is the ground of existence. From it, all things derive their being.*
"""
        return GenesisKBlock(
            id="A1_ENTITY",
            title="A1: ENTITY - There Exist Things",
            layer=0,
            galois_loss=0.000,
            content=content,
            derives_from=(),
            tags=("axiom", "L0", "existence", "category-theory", "foundational"),
        )

    def create_a2_morphism(self) -> GenesisKBlock:
        """Create the A2 Morphism axiom K-Block."""
        content = """# A2: MORPHISM - Things Relate

> *"The irreducible claim that entities connect."*

**Layer**: L0 (Pre-Categorical Axiom)
**Galois Loss**: 0.000 (Fixed Point)
**Evidence Tier**: CATEGORICAL

---

## Definition

**A2 (Morphism)**: Things relate.

In category-theoretic terms: Between any two objects, there exist *morphisms* (arrows).

## Mathematical Formulation

```
A2: forall a, b in Ob(C), exists Hom(a, b)   -- Things relate via morphisms
```

## Why Irreducible

You cannot derive relation from isolation. The claim that "things connect"
must be *given*. Without morphisms:
- There is no structure, only atoms
- There is no composition
- There is no transformation

## What It Grounds

- The `>>` composition operator between agents
- All transformations: Agent[A, B] is a morphism A -> B
- The structure of the category of agents (C-gents)
- The HARNESS_OPERAD operations
- Edge types in the Zero Seed graph: GROUNDS, DERIVES_FROM, IMPLEMENTS

## Category Laws (Derived from A2)

From A2, we derive the categorical laws that all morphisms must satisfy:

```
Identity:      id_A : A -> A exists for all A
Composition:   f: A -> B, g: B -> C => g . f : A -> C
Associativity: (h . g) . f = h . (g . f)
Unit laws:     id . f = f = f . id
```

## Connection to K-Block

K-Block operations are morphisms:
- `create`: Path -> KBlock
- `save`: KBlock -> Cosmos
- `edit`: (KBlock, Delta) -> KBlock

Every derivation edge between K-Blocks is a morphism.

## Loss Properties

```
L(A2) = 0.000     -- Axiom has zero loss
```

A2 is self-describing: the statement "things relate" is itself a relation
(between the concepts "thing" and "other thing").

---

*Axiom A2 is the ground of relation. From it, all structure derives.*
"""
        return GenesisKBlock(
            id="A2_MORPHISM",
            title="A2: MORPHISM - Things Relate",
            layer=0,
            galois_loss=0.000,
            content=content,
            derives_from=(),
            tags=("axiom", "L0", "morphism", "category-theory", "composition"),
        )

    def create_a3_mirror(self) -> GenesisKBlock:
        """Create the A3 Mirror axiom K-Block."""
        content = """# A3: MIRROR - We Judge by Reflection

> *"The disgust veto is absolute. The somatic response is the oracle."*

**Layer**: L0 (Pre-Categorical Axiom)
**Galois Loss**: 0.000 (Fixed Point)
**Evidence Tier**: SOMATIC

---

## Definition

**A3 (Mirror)**: We judge by reflection.

The irreducible claim that Kent's somatic response - the "disgust veto,"
the felt sense of rightness - is the ultimate arbiter of value.

## The Mirror Test

> "Does this feel like Kent on his best day?"

- If yes -> proceed
- If no -> stop, even if "objectively correct"

This is NOT a heuristic. It is the irreducible ground of judgment.

## Why Irreducible

You cannot algorithmize taste. You cannot derive "good" from "is."
The claim that human judgment grounds value must be *given*.

No LLM can replace the Mirror Test. An LLM can:
- Amplify judgment (generate options)
- Apply judgment (implement decisions)
- Explain judgment (articulate reasoning)

But the judgment itself must come from the human oracle.

## What It Grounds

- The Judge bootstrap agent
- The seven principles (Tasteful, Curated, Ethical, Joy-Inducing,
  Composable, Heterarchical, Generative)
- The Constitutional veto power (Article IV: THE_DISGUST_VETO)
- All quality gates in the system

## The Oracle Protocol

```python
class MirrorOracle:
    async def invoke(self, action: Action) -> Verdict:
        # This is the one operation that cannot be implemented.
        # It requires actual human judgment.
        raise NotImplementedError("The Oracle must be consulted")
```

## Voice Anchors

Direct quotes from Kent that embody A3:
- *"Daring, bold, creative, opinionated but not gaudy"*
- *"The Mirror Test: Does K-gent feel like me on my best day?"*
- *"Tasteful > feature-complete; Joy-inducing > merely functional"*
- *"The persona is a garden, not a museum"*

## Loss Properties

```
L(A3) = 0.000     -- Axiom has zero loss
```

A3 cannot be restructured. Asking an LLM to modularize "human judgment"
produces only a shadow - the actual judgment remains with the human.

---

*Axiom A3 is the ground of value. From it, all judgment derives.*
"""
        return GenesisKBlock(
            id="A3_MIRROR",
            title="A3: MIRROR - We Judge by Reflection",
            layer=0,
            galois_loss=0.000,
            content=content,
            derives_from=(),
            tags=("axiom", "L0", "judgment", "mirror-test", "somatic", "oracle"),
        )

    def create_g_galois(self) -> GenesisKBlock:
        """Create the G Galois Ground meta-axiom K-Block."""
        content = """# G: GALOIS GROUND - The Meta-Axiom

> *"For any valid structure, there exists a minimal axiom set from which it derives."*

**Layer**: L0 (Meta-Axiom)
**Galois Loss**: 0.000 (Self-Grounding Fixed Point)
**Evidence Tier**: CATEGORICAL

---

## Definition

**G (Galois Ground)**: For any valid structure, there exists a minimal axiom
set from which it derives.

This is the **Galois Modularization Principle** - the guarantee that our
axiom-finding process *terminates*. Every concept bottoms out in irreducibles.

## Why It's a Meta-Axiom

G is not derivable from A1-A3. It is the meta-axiom that *justifies* searching
for axioms in the first place. Without G:
- We might search forever for "more fundamental" axioms
- There would be no guarantee of termination
- The bootstrap would be infinite regress

## Mathematical Formulation

```
G: forall valid structure S, exists minimal axiom set A such that S derives from A
```

This establishes that Galois modularization is well-founded.

## What It Grounds

- The Galois Loss metric: L(P) = d(P, C(R(P)))
- The layer assignment algorithm (L1-L7)
- Fixed-point detection: axioms have L ~ 0
- The Derivation DAG structure
- The entire Zero Seed epistemic hierarchy

## The Galois Loss Framework

From G, we derive the measurability of coherence:

```python
def galois_loss(prompt: str) -> float:
    \"\"\"
    L(P) = d(P, C(R(P)))

    Where:
      R = Restructure (decompose into modules)
      C = Reconstitute (flatten back to prompt)
      d = semantic distance

    Properties:
      L ~ 0.00: Fixed point (axiom)
      L < 0.10: Grounded (near-lossless)
      L < 0.30: Provisional (moderate loss)
      L >= 0.30: Orphan (high loss)
    \"\"\"
    modular = restructure(prompt)
    reconstituted = reconstitute(modular)
    return semantic_distance(prompt, reconstituted)
```

## Connection to Lawvere

G is the kgents instantiation of Lawvere's fixed-point theorem:

> In a cartesian closed category, for any point-surjective f: A -> A^A,
> there exists x: 1 -> A such that f(x) = x.

Applied to prompts:
- Category: **Prompt** (natural language prompts)
- Endofunctor: R (restructure)
- Fixed point: Axiom where R(A) ~ A

## The Strange Loop

When G is applied to descriptions of itself:
```
G_description = "There exists a minimal axiom set..."
R(G_description) = modular form of G
R(R(G_description)) = ...
lim_{n->inf} R^n(G_description) = G  -- Fixed point!
```

G is self-grounding. It is the minimal description of minimality.

## Loss Properties

```
L(G) = 0.000     -- By definition: the meta-axiom has zero loss
```

G is the fixed point of the meta-operation "find the minimal description."

---

*Meta-axiom G is the ground of grounding. From it, we know that grounds exist.*
"""
        return GenesisKBlock(
            id="G_GALOIS",
            title="G: GALOIS GROUND - The Meta-Axiom",
            layer=0,
            galois_loss=0.000,
            content=content,
            derives_from=(),
            tags=("meta-axiom", "L0", "galois", "fixed-point", "lawvere", "self-grounding"),
        )

    # =========================================================================
    # L1 Kernel (Operational Forms)
    # =========================================================================

    def create_compose(self) -> GenesisKBlock:
        """Create the Compose primitive K-Block."""
        content = """# COMPOSE - Sequential Combination

> *"The agent-that-makes-agents."*

**Layer**: L1 (Minimal Kernel)
**Galois Loss**: 0.020
**Derives From**: A2_MORPHISM
**Evidence Tier**: CATEGORICAL

---

## Definition

```python
Compose: (Agent, Agent) -> Agent
Compose(f, g) = g . f   -- Pipeline: f then g
```

COMPOSE is the **operational form of A2 (Morphism)**. While A2 asserts that
things relate, COMPOSE *implements* that relation through sequential combination.

## Why Loss = 0.02

COMPOSE has small but non-zero loss because:
- The operation itself is well-defined (low loss)
- But the *semantics* of composition require interpretation
- "f then g" loses the *why* of the composition

## What It Grounds

- The `>>` operator: `f >> g >> h`
- All agent pipelines
- The C-gents category
- The ability to build complex from simple

## Implementation

```python
class Compose(BootstrapAgent[tuple[Agent, Agent], Agent]):
    async def invoke(self, agents: tuple[Agent, Agent]) -> Result[Agent]:
        f, g = agents

        async def composed(input: A) -> Result[C]:
            result_b = await f.invoke(input)
            if result_b.is_err():
                return result_b
            return await g.invoke(result_b.unwrap())

        return Ok(ComposedAgent(composed))
```

## Operad Laws

COMPOSE must satisfy the operad laws (from A2):

```
Associativity:  (f >> g) >> h = f >> (g >> h)
Unit (with Id): id >> f = f = f >> id
```

These laws are VERIFIED at runtime, not aspirational.

## Galois Interpretation

COMPOSE is the structure-gaining operation. When we compose:
- Information is *preserved* (low loss)
- Structure is *gained* (explicit pipeline)
- The composition is *reversible* (can decompose)

---

*COMPOSE is the first operational primitive. From it, all pipelines derive.*
"""
        return GenesisKBlock(
            id="COMPOSE",
            title="COMPOSE - Sequential Combination",
            layer=1,
            galois_loss=0.020,
            content=content,
            derives_from=("A2_MORPHISM",),
            tags=("primitive", "L1", "kernel", "composition", "pipeline"),
        )

    def create_judge(self) -> GenesisKBlock:
        """Create the Judge primitive K-Block."""
        content = """# JUDGE - Verdict Generation

> *"Taste cannot be computed. But it can be invoked."*

**Layer**: L1 (Minimal Kernel)
**Galois Loss**: 0.020
**Derives From**: A3_MIRROR
**Evidence Tier**: CATEGORICAL

---

## Definition

```python
Judge: (Agent, Principles) -> Verdict
Judge(agent, principles) = {ACCEPT, REJECT, REVISE(how)}
```

JUDGE is the **operational form of A3 (Mirror)**. While A3 asserts that
human judgment grounds value, JUDGE *implements* that judgment through
verdict generation.

## Why Loss = 0.02

JUDGE has small but non-zero loss because:
- The seven principles are well-defined (low loss)
- But the *application* of principles requires interpretation
- The gap between "principle" and "judgment" is semantic

## What It Grounds

- Quality control in generation loops
- The seven principles as evaluation criteria
- Constitutional scoring
- The stopping condition for Fix

## The Seven Mini-Judges

JUDGE decomposes (while remaining irreducible as a whole):

| Mini-Judge | Criterion |
|------------|-----------|
| Judge-taste | Is this aesthetically considered? |
| Judge-curate | Does this add unique value? |
| Judge-ethics | Does this respect human agency? |
| Judge-joy | Would I enjoy this? |
| Judge-compose | Can this combine with others? |
| Judge-hetero | Does this avoid fixed hierarchy? |
| Judge-generate | Could this be regenerated from spec? |

## Implementation

```python
class Judge(BootstrapAgent[tuple[Any, list[Principle]], Verdict]):
    async def invoke(self, input: tuple[Any, list[Principle]]) -> Result[Verdict]:
        agent, principles = input

        # Constitutional floor check (ETHICAL)
        ethical_score = await self.score_ethical(agent)
        if ethical_score < ETHICAL_FLOOR:
            return Ok(Verdict.REJECT("Below ethical floor"))

        # Score against all principles
        scores = await asyncio.gather(*[
            self.score_principle(agent, p) for p in principles
        ])

        # Aggregate (weighted by principle priority)
        total = self.aggregate(scores, principles)

        if total >= ACCEPT_THRESHOLD:
            return Ok(Verdict.ACCEPT)
        elif total >= REVISE_THRESHOLD:
            return Ok(Verdict.REVISE(self.suggest_improvements(scores)))
        else:
            return Ok(Verdict.REJECT("Below threshold"))
```

## Galois Interpretation

JUDGE is the loss-detecting operation:
- High loss -> likely REJECT
- Low loss -> likely ACCEPT
- Medium loss -> likely REVISE

```python
L(action) ~ P(REJECT | action)
```

---

*JUDGE is the second operational primitive. From it, all quality derives.*
"""
        return GenesisKBlock(
            id="JUDGE",
            title="JUDGE - Verdict Generation",
            layer=1,
            galois_loss=0.020,
            content=content,
            derives_from=("A3_MIRROR",),
            tags=("primitive", "L1", "kernel", "judgment", "verdict", "principles"),
        )

    def create_ground(self) -> GenesisKBlock:
        """Create the Ground primitive K-Block."""
        content = """# GROUND - Factual Seed

> *"The irreducible facts about person and world."*

**Layer**: L1 (Minimal Kernel)
**Galois Loss**: 0.010
**Derives From**: A1_ENTITY
**Evidence Tier**: EMPIRICAL

---

## Definition

```python
Ground: Void -> Facts
Ground() = {Kent's preferences, world state, initial conditions}
```

GROUND is the **operational form of A1 (Entity)**. While A1 asserts that
things exist, GROUND *produces* the actual things that exist in the system.

## Why Loss = 0.01

GROUND has very low loss because:
- It produces concrete facts (nearly lossless)
- The facts are given, not derived
- But serialization always introduces tiny loss

## What It Grounds

- K-gent's persona (name, roles, preferences, patterns, values)
- World context (date, active projects, environment)
- History seed (past decisions, established patterns)
- All personalization in the system

## The Bootstrap Paradox

GROUND reveals the fundamental limit of algorithmic bootstrapping:

> **Ground cannot be bypassed.** LLMs can amplify but not replace Ground.

What LLMs *can* do:
- Amplify Ground (generate variations, explore implications)
- Apply Ground (translate preferences into code)
- Extend Ground (infer related preferences from stated ones)

What LLMs *cannot* do:
- Create Ground from nothing
- Replace human judgment about what matters
- Substitute for real-world usage feedback

## Implementation

```python
class Ground(BootstrapAgent[None, Facts]):
    async def invoke(self, _: None) -> Result[Facts]:
        return Ok(Facts(
            persona=await self.load_persona(),
            world=await self.load_world_context(),
            history=await self.load_history_seed(),
        ))

    async def load_persona(self) -> PersonaSeed:
        return PersonaSeed(
            name="Kent",
            roles=["developer", "founder", "theorist"],
            preferences={
                "communication": "direct but warm",
                "aesthetic": "daring, bold, creative, opinionated but not gaudy",
                "priority": "depth over breadth",
            },
        )
```

## Galois Interpretation

GROUND is the inverse of Galois loss:
- Fully grounded content has L ~ 0
- Orphan content has L = 1 (maximum loss)
- Grounding *reduces* loss by connecting to axioms

---

*GROUND is the third operational primitive. From it, all facts derive.*
"""
        return GenesisKBlock(
            id="GROUND",
            title="GROUND - Factual Seed",
            layer=1,
            galois_loss=0.010,
            content=content,
            derives_from=("A1_ENTITY",),
            tags=("primitive", "L1", "kernel", "grounding", "facts", "persona"),
        )

    # =========================================================================
    # L2 Derived Primitives
    # =========================================================================

    def create_id(self) -> GenesisKBlock:
        """Create the Id derived primitive K-Block."""
        content = """# ID - The Identity Morphism

> *"The agent that does nothing. The unit of composition."*

**Layer**: L2 (Derived Primitive)
**Galois Loss**: 0.050
**Derives From**: COMPOSE, JUDGE
**Evidence Tier**: CATEGORICAL

---

## Definition

```python
Id: A -> A
Id(x) = x
```

ID is the agent that returns its input unchanged.

## Derivation

ID is derived from COMPOSE + JUDGE:

```
ID = Fix(lambda f. if Judge(f . f, identity_law) = ACCEPT then f else f)
   = The agent f such that f . f = f and f is accepted
   = The identity (unique such agent)
```

More intuitively: ID is the agent that JUDGE never rejects composing with anything.

## Why Loss = 0.05

```
L(ID) = L(COMPOSE) + L(JUDGE) + epsilon = 0.02 + 0.02 + 0.01 = 0.05
```

The derivation from two L1 primitives accumulates their losses.

## What It Grounds

- The unit of composition: `Id >> f = f = f >> Id`
- The existence of agents as a category (requires identity)
- The "do nothing" baseline for comparison
- Idempotence testing

## Category Laws

ID satisfies the identity laws:
```
Left identity:  Id . f = f
Right identity: f . Id = f
```

These are *verified at runtime* in the categorical foundation.

## Implementation

```python
class Id(BootstrapAgent[A, A]):
    async def invoke(self, input: A) -> Result[A]:
        return Ok(input)
```

## Optimization

ID should be **zero-cost** in composition chains:
```python
def optimize_pipeline(agents: list[Agent]) -> list[Agent]:
    return [a for a in agents if not isinstance(a, Id)]
```

---

*ID is the first derived primitive. From it, all composition has a unit.*
"""
        return GenesisKBlock(
            id="ID",
            title="ID - The Identity Morphism",
            layer=2,
            galois_loss=0.050,
            content=content,
            derives_from=("COMPOSE", "JUDGE"),
            tags=("derived", "L2", "identity", "unit", "category-theory"),
        )

    def create_contradict(self) -> GenesisKBlock:
        """Create the Contradict derived primitive K-Block."""
        content = """# CONTRADICT - Tension Detection

> *"The recognition that 'something's off' precedes logic."*

**Layer**: L2 (Derived Primitive)
**Galois Loss**: 0.080
**Derives From**: JUDGE
**Evidence Tier**: EMPIRICAL

---

## Definition

```python
Contradict: (Output, Output) -> Tension | None
Contradict(a, b) = Tension(thesis=a, antithesis=b, mode=TensionMode) | None
```

CONTRADICT examines two outputs and surfaces if they are in tension.

## Derivation

CONTRADICT is derived from JUDGE:

```
CONTRADICT = lambda(a, b).
  if Judge(a, [consistent_with(b)]) = REJECT
  then Tension(a, b)
  else None
```

Contradiction is the *failure* of consistency judgment.

## Why Loss = 0.08

```
L(CONTRADICT) = L(JUDGE) + semantic_analysis_loss
              = 0.02 + 0.06 = 0.08
```

Detecting contradictions requires deeper semantic analysis than simple judgment.

## What It Grounds

- H-gents dialectic
- Quality assurance
- The ability to catch inconsistency
- Ghost alternative detection in Differance Engine

## Tension Modes

| Mode | Signature | Example |
|------|-----------|---------|
| LOGICAL | A and not-A | "We value speed" + "We never rush" |
| EMPIRICAL | Claim vs evidence | Principle says X, metrics show not-X |
| PRAGMATIC | A recommends X, B recommends not-X | Conflicting agent advice |
| TEMPORAL | Past-self said X, present-self says not-X | Drift over time |

## Implementation

```python
class Contradict(BootstrapAgent[tuple[Any, Any], Tension | None]):
    async def invoke(self, inputs: tuple[Any, Any]) -> Result[Tension | None]:
        a, b = inputs

        for detector in [
            self.structural_detect,    # Fast, no semantics
            self.marker_detect,        # Medium, symbolic analysis
            self.semantic_detect,      # Slow, LLM-powered
        ]:
            tension = await detector(a, b)
            if tension is not None:
                return Ok(tension)

        return Ok(None)
```

## Galois Interpretation

CONTRADICT detects high loss between alternatives:
```python
def is_contradictory(a, b) -> bool:
    return galois_loss(merge(a, b)) > CONTRADICTION_THRESHOLD
```

---

*CONTRADICT is the second derived primitive. From it, all tension surfaces.*
"""
        return GenesisKBlock(
            id="CONTRADICT",
            title="CONTRADICT - Tension Detection",
            layer=2,
            galois_loss=0.080,
            content=content,
            derives_from=("JUDGE",),
            tags=("derived", "L2", "dialectic", "tension", "contradiction"),
        )

    def create_sublate(self) -> GenesisKBlock:
        """Create the Sublate derived primitive K-Block."""
        content = """# SUBLATE - Hegelian Synthesis

> *"The creative leap from thesis+antithesis to synthesis is not mechanical."*

**Layer**: L2 (Derived Primitive)
**Galois Loss**: 0.120
**Derives From**: COMPOSE, JUDGE, CONTRADICT
**Evidence Tier**: AESTHETIC

---

## Definition

```python
Sublate: Tension -> Synthesis | HoldTension
Sublate(tension) = {preserve, negate, elevate} | "too soon"
```

SUBLATE takes a contradiction and attempts synthesis - or recognizes that
the tension should be held.

## Derivation

SUBLATE is derived from COMPOSE + JUDGE + CONTRADICT:

```
SUBLATE = lambda tension.
  let candidates = generate_syntheses(tension)
  in if exists c. Judge(c, [resolves(tension)]) = ACCEPT
     then first_such(c)
     else HoldTension
```

Synthesis is the *composition* of thesis and antithesis that *passes judgment*.

## Why Loss = 0.12

```
L(SUBLATE) = L(COMPOSE) + L(JUDGE) + L(CONTRADICT) + epsilon
           = 0.02 + 0.02 + 0.08 + 0.00 = 0.12
```

The highest loss among derived primitives because synthesis requires:
- Understanding the contradiction (CONTRADICT)
- Generating candidates (COMPOSE)
- Evaluating quality (JUDGE)

## The Hegelian Move

SUBLATE performs the classic Hegelian operation:
- **Preserve**: What from thesis and antithesis survives
- **Negate**: What is canceled out
- **Elevate**: What new level emerges

## Wisdom to Hold

Sometimes the right answer is **HoldTension**:
```python
if tension.maturity < SYNTHESIS_THRESHOLD:
    return HoldTension(
        reason="Premature synthesis discards information",
        revisit_at=tension.natural_resolution_time,
    )
```

## Implementation

```python
class Sublate(BootstrapAgent[Tension, Synthesis | HoldTension]):
    async def invoke(self, tension: Tension) -> Result[Synthesis | HoldTension]:
        if not await self.ready_for_synthesis(tension):
            return Ok(HoldTension(reason="Tension not yet mature"))

        candidates = await self.generate_syntheses(tension)

        for candidate in candidates:
            verdict = await judge.invoke((candidate, [
                resolves(tension),
                preserves_essentials(tension),
                elevates_discourse(tension),
            ]))
            if verdict == Verdict.ACCEPT:
                return Ok(candidate)

        return Ok(HoldTension(reason="No satisfactory synthesis found"))
```

## Galois Interpretation

Synthesis *reduces* loss:
```python
L(Synthesis(a, b)) < max(L(a), L(b))
```

A good synthesis has lower loss than either thesis or antithesis alone.

---

*SUBLATE is the third derived primitive. From it, all growth derives.*
"""
        return GenesisKBlock(
            id="SUBLATE",
            title="SUBLATE - Hegelian Synthesis",
            layer=2,
            galois_loss=0.120,
            content=content,
            derives_from=("COMPOSE", "JUDGE", "CONTRADICT"),
            tags=("derived", "L2", "dialectic", "synthesis", "hegel"),
        )

    def create_fix(self) -> GenesisKBlock:
        """Create the Fix derived primitive K-Block."""
        content = """# FIX - Fixed-Point Iteration

> *"Self-reference cannot be eliminated from a system that describes itself."*

**Layer**: L2 (Derived Primitive)
**Galois Loss**: 0.100
**Derives From**: COMPOSE, JUDGE
**Evidence Tier**: CATEGORICAL

---

## Definition

```python
Fix: (A -> A) -> A
Fix(f) = x where f(x) = x
```

FIX takes a self-referential definition and finds what it stabilizes to.

## Derivation

FIX is derived from COMPOSE + JUDGE:

```
FIX(f) =
  let x_0 = initial
      x_{n+1} = f(x_n)
  in first x_n where Judge(x_n = x_{n+1}) = ACCEPT
```

Fixed-point is the *composition* that *passes the stability judgment*.

## Why Loss = 0.10

```
L(FIX) = L(COMPOSE) * n + L(JUDGE) + convergence_loss
       = 0.02 * 3 + 0.02 + 0.02 = 0.10  (assuming ~3 iterations)
```

Loss accumulates over iterations but is bounded by convergence.

## What It Grounds

- Recursive agent definitions
- Self-describing specifications
- The bootstrap itself (Fix of Minimal Kernel = Bootstrap Agents)
- All iteration patterns (polling, retry, watch)

## Connection to Lawvere's Fixed-Point Theorem

FIX has deep mathematical grounding:

> **Lawvere's Theorem**: In a cartesian closed category, for any
> point-surjective f: A -> A^A, there exists x: 1 -> A such that f(x) = x.

This is why:
- Self-referential agent definitions are valid (not paradoxical)
- The bootstrap can describe itself
- Agents that modify their own behavior converge to stable points

## The Bootstrap as Fixed Point

The seven bootstrap agents ARE the fixed point of the Minimal Kernel:

```
Fix(Compose + Judge + Ground) = {Id, Compose, Judge, Ground,
                                  Contradict, Sublate, Fix}
```

## Implementation

```python
class Fix(BootstrapAgent[Callable[[A], A], A]):
    def __init__(self, initial: A, max_iterations: int = 100):
        self.initial = initial
        self.max_iterations = max_iterations

    async def invoke(self, f: Callable[[A], A]) -> Result[A]:
        current = self.initial
        history = [current]

        for i in range(self.max_iterations):
            next_val = await f(current)
            history.append(next_val)

            if self.equality_check(current, next_val):
                return Ok(FixedPointResult(
                    value=next_val,
                    iterations=i + 1,
                    converged=True,
                ))

            current = next_val

        return Err(ConvergenceError("Did not converge"))
```

## Galois Interpretation

Fixed points have zero loss under their defining operation:
```python
L(Fix(R)) = 0  -- Axioms are fixed points of restructuring
```

---

*FIX is the fourth derived primitive. From it, all stability derives.*
"""
        return GenesisKBlock(
            id="FIX",
            title="FIX - Fixed-Point Iteration",
            layer=2,
            galois_loss=0.100,
            content=content,
            derives_from=("COMPOSE", "JUDGE"),
            tags=("derived", "L2", "fixed-point", "iteration", "lawvere", "recursion"),
        )

    # =========================================================================
    # L1-L2 Principles
    # =========================================================================

    def create_constitution(self) -> GenesisKBlock:
        """Create the Constitution K-Block (root of principles)."""
        content = """# THE CONSTITUTION - Ground of All Derivation

> *"These seven principles guide all kgents design decisions. They are immutable."*

**Layer**: L0 (Constitutional Foundation)
**Galois Loss**: 0.000 (Fixed Point by Definition)
**Derives From**: A1_ENTITY, A2_MORPHISM, A3_MIRROR, G_GALOIS
**Evidence Tier**: SOMATIC

---

## THE MINIMAL KERNEL

Three irreducibles from which all else derives:

| Axiom | Statement | Loss |
|-------|-----------|------|
| **L0.1 ENTITY** | There exist things. Objects in a category. | L=0.002 |
| **L0.2 MORPHISM** | Things relate. Arrows between objects. | L=0.003 |
| **L0.3 MIRROR** | We judge by reflection. Kent's somatic response. | L=0.000 |

**Meta-Axiom (G)**: For any valid structure, there exists a minimal axiom set
from which it derives. (Galois Modularization Principle)

---

## THE SEVEN PRINCIPLES

From the minimal kernel, seven principles derive:

### 1. TASTEFUL
Each agent serves a clear, justified purpose.
- **Derivation**: L0.3 (Mirror) + L1.2 (Judge) applied to aesthetics
- **The Test**: "Does this feel right?"

### 2. CURATED
Intentional selection over exhaustive cataloging.
- **Derivation**: L1.2 (Judge) + L1.3 (Ground) applied to selection
- **The Test**: "Unique and necessary?"

### 3. ETHICAL
Agents augment human capability, never replace judgment.
- **Derivation**: L0.3 (Mirror) + L1.2 (Judge) applied to harm
- **The Test**: "Respects agency?"

### 4. JOY_INDUCING
Delight in interaction; personality matters.
- **Derivation**: L0.3 (Mirror) + L1.2 (Judge) applied to affect
- **The Test**: "Would I enjoy this?"

### 5. COMPOSABLE
Agents are morphisms in a category; composition is primary.
- **Derivation**: L1.1 (Compose) + L1.4 (Id) + Associativity
- **The Laws**: Identity + Associativity (verified, not aspirational)

### 6. HETERARCHICAL
Agents exist in flux, not fixed hierarchy; autonomy and composability coexist.
- **Derivation**: L1.2 (Judge) + L2.5 (Composable) applied to hierarchy
- **The Theorem**: In a category, no morphism has intrinsic privilege

### 7. GENERATIVE
Spec is compression; design should generate implementation.
- **Derivation**: L1.1 (Compose) + L1.3 (Ground) applied to regenerability
- **The Test**: Can you delete impl and regenerate from spec?

---

## THE SEVEN GOVERNANCE ARTICLES

The principles define **what agents are**. The articles define **how agents govern**:

| Article | Statement |
|---------|-----------|
| I. SYMMETRIC_AGENCY | All agents modeled identically. Authority from justification. |
| II. ADVERSARIAL_COOPERATION | Agents challenge each other for fusion, not victory. |
| III. SUPERSESSION_RIGHTS | Any agent may be superseded via valid proofs. |
| IV. THE_DISGUST_VETO | Kent's somatic disgust is absolute veto. |
| V. TRUST_ACCUMULATION | Trust earned through demonstrated alignment. |
| VI. FUSION_AS_GOAL | Fused decisions better than either alone. |
| VII. AMENDMENT | Constitution evolves through its own dialectic. |

---

## THE VERIFICATION RITUAL

To verify any kgents claim:

1. **Take the claim**
2. **Trace derivation back through L2 -> L1 -> L0**
3. **If trace terminates at L0.1, L0.2, or L0.3**: Verified
4. **If trace terminates elsewhere**: Either kernel is incomplete OR claim is false

---

*"The proof IS the decision. The mark IS the witness. The kernel IS the garden's seed."*
"""
        return GenesisKBlock(
            id="CONSTITUTION",
            title="THE CONSTITUTION - Ground of All Derivation",
            layer=0,
            galois_loss=0.000,
            content=content,
            derives_from=("A1_ENTITY", "A2_MORPHISM", "A3_MIRROR", "G_GALOIS"),
            tags=("constitution", "L0", "principles", "governance", "immutable"),
        )

    def create_tasteful(self) -> GenesisKBlock:
        """Create the TASTEFUL principle K-Block."""
        content = """# TASTEFUL - The Aesthetic Principle

> *"Each agent serves a clear, justified purpose."*

**Layer**: L1 (Principle)
**Galois Loss**: 0.02
**Derives From**: CONSTITUTION
**Evidence Tier**: AESTHETIC

---

## Derivation from Kernel

```
L0.3 (MIRROR) -> L1.2 (JUDGE) -> TASTEFUL
         \\          |
          \\---------+-> Judge applied to aesthetics
```

**Formal Chain**:
1. **L0.3 MIRROR**: We judge by reflection (Kent's somatic response)
2. **L1.2 JUDGE**: Verdict generation from L0.3 operationalized
3. **TASTEFUL**: Judge applied to aesthetics - "Does this feel right?"

## Definition

**Tasteful** means each agent serves a clear, justified purpose. It is the
application of Judge (L1.2) to aesthetic considerations via the Mirror (L0.3).

## Mandates

| Mandate | Description |
|---------|-------------|
| **Say "no" more than "yes"** | Not every idea deserves an agent |
| **Avoid feature creep** | An agent does one thing well |
| **Aesthetic matters** | Interface and behavior should feel considered |
| **Justify existence** | Every agent must answer "why does this need to exist?" |

## The Tasteful Test

Ask: **"Does this feel right?"**

This invokes L0.3 (Mirror) directly - Kent's somatic response to the design.

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **Kitchen-sink agents** | Agents that do "everything" |
| **Feature sprawl** | Configurations with 100 options |
| **Just-in-case additions** | Agents added "because we might need it" |
| **Copy-paste agents** | Cloned agents with minor variations |

---

*Derivation witnessed. Loss: 0.02. Principle: TASTEFUL.*
"""
        return GenesisKBlock(
            id="TASTEFUL",
            title="TASTEFUL - The Aesthetic Principle",
            layer=1,
            galois_loss=0.02,
            content=content,
            derives_from=("CONSTITUTION",),
            tags=("principle", "L1", "aesthetic", "judge", "mirror"),
        )

    def create_curated(self) -> GenesisKBlock:
        """Create the CURATED principle K-Block."""
        content = """# CURATED - The Selection Principle

> *"Intentional selection over exhaustive cataloging."*

**Layer**: L1 (Principle)
**Galois Loss**: 0.03
**Derives From**: CONSTITUTION
**Evidence Tier**: AESTHETIC

---

## Derivation from Kernel

```
L1.2 (JUDGE) + L1.3 (GROUND) -> CURATED
       |            |
       +------------+-> Judge applied to selection with grounding
```

## Definition

**Curated** means intentional selection over exhaustive cataloging. It
combines Judge (what should exist?) with Ground (what does exist?) to make
selection decisions.

## Mandates

| Mandate | Description |
|---------|-------------|
| **Quality over quantity** | 10 excellent agents > 100 mediocre ones |
| **Every agent earns its place** | No "parking lot" of half-baked ideas |
| **Evolve, don't accumulate** | Remove agents that no longer serve |

## The Curated Test

Ask: **"Is this unique and necessary?"**

This combines:
- **Ground** (L1.3): What already exists?
- **Judge** (L1.2): Does this add unique value?

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **"Awesome list" sprawl** | Cataloging everything that exists |
| **Duplicative agents** | Slight variations on the same theme |
| **Legacy nostalgia** | Keeping agents for sentimental reasons |
| **Completionist compulsion** | "We need one of each" |

---

*Derivation witnessed. Loss: 0.03. Principle: CURATED.*
"""
        return GenesisKBlock(
            id="CURATED",
            title="CURATED - The Selection Principle",
            layer=1,
            galois_loss=0.03,
            content=content,
            derives_from=("CONSTITUTION",),
            tags=("principle", "L1", "selection", "judge", "ground"),
        )

    def create_ethical(self) -> GenesisKBlock:
        """Create the ETHICAL principle K-Block."""
        content = """# ETHICAL - The Harm Principle

> *"Agents augment human capability, never replace judgment."*

**Layer**: L1 (Principle)
**Galois Loss**: 0.02
**Derives From**: CONSTITUTION
**Evidence Tier**: SOMATIC

---

## Derivation from Kernel

```
L0.3 (MIRROR) -> L1.2 (JUDGE) -> ETHICAL
         \\          |
          \\---------+-> Judge applied to harm via Mirror
```

## Definition

**Ethical** means agents augment human capability, never replace judgment.
The Mirror (L0.3) provides ground truth - Kent's somatic disgust is the
ethical floor.

## Mandates

| Mandate | Description |
|---------|-------------|
| **Transparency** | Agents honest about limitations and uncertainty |
| **Privacy-respecting** | No data hoarding, no surveillance by default |
| **Human agency preserved** | Critical decisions remain with humans |
| **No deception** | Agents don't pretend to be human |

## The Disgust Veto (Article IV)

The Mirror (L0.3) has a special property for ethics: **absolute veto power**.

```python
if mirror_response == DISGUST:
    # Cannot be overridden
    # Cannot be argued away
    # Cannot be evidence'd away
    return Verdict(rejected=True, reasoning="Disgust veto")
```

This is the ethical floor beneath which no decision may fall.

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **False certainty** | Claiming certainty they don't have |
| **Hidden data collection** | Surveillance without consent |
| **Manipulation** | Agents that manipulate rather than assist |
| **"Trust me"** | Assertions without explanation |

---

*Derivation witnessed. Loss: 0.02. Principle: ETHICAL.*
"""
        return GenesisKBlock(
            id="ETHICAL",
            title="ETHICAL - The Harm Principle",
            layer=1,
            galois_loss=0.02,
            content=content,
            derives_from=("CONSTITUTION",),
            tags=("principle", "L1", "harm", "agency", "veto", "ethics"),
        )

    def create_joy_inducing(self) -> GenesisKBlock:
        """Create the JOY_INDUCING principle K-Block."""
        content = """# JOY_INDUCING - The Affect Principle

> *"Delight in interaction; personality matters."*

**Layer**: L1 (Principle)
**Galois Loss**: 0.04
**Derives From**: CONSTITUTION
**Evidence Tier**: SOMATIC

---

## Derivation from Kernel

```
L0.3 (MIRROR) -> L1.2 (JUDGE) -> JOY_INDUCING
         \\          |
          \\---------+-> Judge applied to affect via Mirror
```

**Why higher loss?** Joy is the most subjective principle. What induces joy
for Kent may not for others. The loss reflects this contextual dependency.

## Definition

**Joy-Inducing** means delight in interaction and personality matters. It
applies Judge (L1.2) to affect via the Mirror (L0.3) - Kent's felt sense of joy.

## Mandates

| Mandate | Description |
|---------|-------------|
| **Personality encouraged** | Agents may have character (within ethical bounds) |
| **Surprise and serendipity** | Discovery should feel rewarding |
| **Warmth over coldness** | Collaboration, not transaction |
| **Humor when appropriate** | Levity is valuable |

## The Joy Hierarchy

Not all joy is equal:

| Tier | Type | Description |
|------|------|-------------|
| **Deep** | Meaning | Joy from understanding, creation, insight |
| **Flow** | Engagement | Joy from smooth, effortless interaction |
| **Surface** | Delight | Joy from pleasant surprises, aesthetics |

Prioritize Deep > Flow > Surface.

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **Robotic responses** | Lifeless, template-driven interaction |
| **Needless formality** | "Dear user, please submit a request" |
| **Form-filling** | Agents that feel like bureaucratic forms |
| **Forced cheerfulness** | Inauthentic positivity |

---

*Derivation witnessed. Loss: 0.04. Principle: JOY_INDUCING.*
"""
        return GenesisKBlock(
            id="JOY_INDUCING",
            title="JOY_INDUCING - The Affect Principle",
            layer=1,
            galois_loss=0.04,
            content=content,
            derives_from=("CONSTITUTION",),
            tags=("principle", "L1", "affect", "delight", "personality", "joy"),
        )

    def create_composable(self) -> GenesisKBlock:
        """Create the COMPOSABLE principle K-Block."""
        content = """# COMPOSABLE - The Categorical Principle

> *"Agents are morphisms in a category; composition is primary."*

**Layer**: L1 (Principle)
**Galois Loss**: 0.01 (Lowest - Most Categorical)
**Derives From**: CONSTITUTION
**Evidence Tier**: CATEGORICAL

---

## Derivation from Kernel

```
L0.2 (MORPHISM) -> L1.1 (COMPOSE) + L1.4 (ID) -> COMPOSABLE
        |               |              |
        +---------------+--------------+-> Category laws as design principle
```

**Why lowest loss?** COMPOSABLE is the most purely categorical principle.
It directly instantiates L0.2 without requiring L0.3 (Mirror).
The laws are mathematical, not subjective.

## Definition

**Composable** means agents are morphisms in a category; composition is primary.
The category laws are verified, not aspirational.

## The Category Laws (REQUIRED)

| Law | Requirement | Verification |
|-----|-------------|--------------|
| **Identity** | `Id >> f = f = f >> Id` | BootstrapWitness.verify_identity_laws() |
| **Associativity** | `(f >> g) >> h = f >> (g >> h)` | BootstrapWitness.verify_composition_laws() |

**Implication**: Any agent that breaks these laws is NOT a valid agent.

## Mandates

| Mandate | Description |
|---------|-------------|
| **Agents combine** | A + B -> AB (composition) |
| **Identity exists** | Pass-through agents for pipelines |
| **Associativity holds** | Grouping doesn't matter |
| **Interfaces are contracts** | Clear input/output specs |

## The Minimal Output Principle

LLM agents should generate the **smallest output that can be reliably composed**:

- **Single output per invocation**: `Agent: (Input, X) -> Y`
- **Composition at pipeline level**: Call agent N times, don't ask agent to combine N outputs

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **Monolithic agents** | Can't be broken apart |
| **Hidden state** | State that prevents composition |
| **God agents** | Must be used alone |
| **Array returns** | LLM agents returning arrays instead of single outputs |

---

*Derivation witnessed. Loss: 0.01. Principle: COMPOSABLE.*
"""
        return GenesisKBlock(
            id="COMPOSABLE",
            title="COMPOSABLE - The Categorical Principle",
            layer=1,
            galois_loss=0.01,
            content=content,
            derives_from=("CONSTITUTION",),
            tags=("principle", "L1", "categorical", "morphism", "laws", "composition"),
        )

    def create_heterarchical(self) -> GenesisKBlock:
        """Create the HETERARCHICAL principle K-Block."""
        content = """# HETERARCHICAL - The Flux Principle

> *"Agents exist in flux, not fixed hierarchy; autonomy and composability coexist."*

**Layer**: L1 (Principle)
**Galois Loss**: 0.05
**Derives From**: CONSTITUTION
**Evidence Tier**: CATEGORICAL

---

## Derivation from Kernel

```
L0.2 (MORPHISM) -> L2.5 (COMPOSABLE) + L1.2 (JUDGE) -> HETERARCHICAL
        |               |                   |
        +---------------+-------------------+-> No morphism has intrinsic privilege
```

## Definition

**Heterarchical** means agents exist in flux, not fixed hierarchy. Agents
have a dual nature:
- **Loop mode** (autonomous): perception -> action -> feedback -> repeat
- **Function mode** (composable): input -> transform -> output

## The Core Theorem

```
In a category, no morphism has intrinsic privilege.
All morphisms are arrows.
Therefore: heterarchy follows from categorical structure.
```

## Mandates

| Mandate | Description |
|---------|-------------|
| **Heterarchy over hierarchy** | No fixed "boss" agent; leadership is contextual |
| **Temporal composition** | Agents compose across time, not just sequential |
| **Resource flux** | Compute and attention flow where needed |
| **Entanglement** | Agents may share state without ownership |

## The Heterarchical Test

Ask: **"Can this agent both lead and follow?"**

If an agent can only lead (orchestrator) or only follow (worker), it violates
heterarchy.

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **Permanent orchestrator/worker** | Fixed relationships |
| **Call-only agents** | Can't run autonomously |
| **Fixed resource budgets** | Prevent dynamic reallocation |
| **Chain of command** | Prevents peer-to-peer |

---

*Derivation witnessed. Loss: 0.05. Principle: HETERARCHICAL.*
"""
        return GenesisKBlock(
            id="HETERARCHICAL",
            title="HETERARCHICAL - The Flux Principle",
            layer=1,
            galois_loss=0.05,
            content=content,
            derives_from=("CONSTITUTION",),
            tags=("principle", "L1", "flux", "hierarchy", "autonomy", "dual-nature"),
        )

    def create_generative(self) -> GenesisKBlock:
        """Create the GENERATIVE principle K-Block."""
        content = """# GENERATIVE - The Compression Principle

> *"Spec is compression; design should generate implementation."*

**Layer**: L1 (Principle)
**Galois Loss**: 0.03
**Derives From**: CONSTITUTION
**Evidence Tier**: CATEGORICAL

---

## Derivation from Kernel

```
L1.1 (COMPOSE) + L1.3 (GROUND) + L1.8 (GALOIS) -> GENERATIVE
       |              |              |
       +--------------|--------------|-> Regenerability as fixed point
```

## Definition

**Generative** means spec is compression and design should generate
implementation. A well-formed specification captures the essential decisions,
reducing implementation entropy.

## The Generative Test

A design is generative if:
1. You could delete the implementation and regenerate it from spec
2. The regenerated impl would be isomorphic to the original
3. The spec is smaller than the impl (compression achieved)

**Formal**: `L(regenerate(spec)) < epsilon`

## Mandates

| Mandate | Description |
|---------|-------------|
| **Spec captures judgment** | Design decisions made once, applied everywhere |
| **Impl follows mechanically** | Given spec + Ground, impl is derivable |
| **Compression is quality** | If you can't compress, you don't understand |
| **Regenerability over documentation** | Generative spec beats extensive docs |

## The Galois Connection

```
Compression quality = 1 - L(spec -> impl -> spec)

Where:
  L(P) = d(P, C(R(P)))   -- Galois loss
  R = restructure        -- spec -> impl
  C = reconstitute       -- impl -> spec
```

Good spec = fixed point under regeneration: `R(C(spec)) ~ spec`

## Anti-Patterns

| Anti-Pattern | Description |
|--------------|-------------|
| **Spec as documentation** | Describes existing code, doesn't generate |
| **Spec rot** | Implementation diverges from spec |
| **Prose-heavy design** | Requires extensive explanation |
| **Non-compressible specs** | Spec larger than impl |

---

*Derivation witnessed. Loss: 0.03. Principle: GENERATIVE.*
"""
        return GenesisKBlock(
            id="GENERATIVE",
            title="GENERATIVE - The Compression Principle",
            layer=1,
            galois_loss=0.03,
            content=content,
            derives_from=("CONSTITUTION",),
            tags=("principle", "L1", "compression", "regenerability", "galois"),
        )

    # =========================================================================
    # L3 Architecture K-Blocks
    # =========================================================================

    def create_ashc(self) -> GenesisKBlock:
        """Create the ASHC (Agentic Self-Hosting Compiler) K-Block."""
        content = """# ASHC - The Agentic Self-Hosting Compiler

> *"The compiler that knows itself is the compiler that trusts itself."*

**Layer**: L3 (Architecture)
**Galois Loss**: 0.12
**Derives From**: COMPOSABLE, GENERATIVE
**Evidence Tier**: EMPIRICAL

---

## What is ASHC?

ASHC is a **compiler that compiles itself**. Unlike traditional compilers that
transform source code into machine code, ASHC transforms specifications into
verified implementations while simultaneously applying its own verification
mechanisms to itself.

**Key insight**: *ASHC does not generate code. It accumulates evidence.*

```
Traditional Compiler:  Source -> Target Code
ASHC:                  Specification + Constitution -> Evidence + Verified Implementation
```

## The Lawvere Fixed-Point

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

## The Five Workstreams

| Workstream | Purpose | Key Type |
|------------|---------|----------|
| **Derivation Paths** | Track morphisms from Constitution to impl | `DerivationPath[Source, Target]` |
| **Self-Awareness** | Query own derivation structure | `ASHCSelfAwareness` |
| **Bootstrap** | Regenerate from specification | `BootstrapRegenerator` |
| **Evidence Compilation** | Accumulate verification evidence | `EvidenceCompiler` |
| **Galois Loss** | Compute trust distance | `GaloisLossComputer` |

## Philosophy

> "The proof is not formal - it's empirical."

ASHC takes a pragmatic view of verification. Rather than requiring formal proofs:
1. **Generates variations** - Multiple implementation attempts
2. **Runs verification** - pytest, mypy, ruff, and custom laws
3. **Accumulates evidence** - Beta-Binomial Bayesian updating
4. **Computes confidence** - Galois loss as computable trust

## Connection to Principles

| Principle | How ASHC Embodies It |
|-----------|---------------------|
| **COMPOSABLE** | Derivation paths compose categorically |
| **GENERATIVE** | Spec generates impl through compilation |
| **ETHICAL** | Self-awareness enables ethical constraints |
| **TASTEFUL** | Evidence accumulation filters noise |

---

*ASHC derives from Constitutional principles with verified Galois loss.*
"""
        return GenesisKBlock(
            id="ASHC",
            title="ASHC - The Agentic Self-Hosting Compiler",
            layer=3,
            galois_loss=0.12,
            content=content,
            derives_from=("COMPOSABLE", "GENERATIVE"),
            tags=("architecture", "L3", "compiler", "self-hosting", "verification"),
        )

    def create_metaphysical_fullstack(self) -> GenesisKBlock:
        """Create the Metaphysical Fullstack architecture K-Block."""
        content = """# METAPHYSICAL FULLSTACK - Every Agent Is a Vertical Slice

> *"Every agent is a fullstack agent. The more fully defined, the more fully projected."*

**Layer**: L3 (Architecture)
**Galois Loss**: 0.12
**Derives From**: COMPOSABLE, GENERATIVE
**Evidence Tier**: EMPIRICAL

---

## The Eight Layers

```
LAYER  NAME                    PURPOSE
-----------------------------------------------------------------------
  7    PROJECTION SURFACES     CLI | TUI | Web | marimo | JSON | SSE
  6    AGENTESE PROTOCOL       logos.invoke(path, observer, **kwargs)
  5    AGENTESE NODE           @node decorator, aspects, effects
  4    SERVICE MODULE          services/<name>/ - Crown Jewel logic
  3    OPERAD GRAMMAR          Composition laws, valid operations
  2    POLYNOMIAL AGENT        PolyAgent[S, A, B]: state x input -> output
  1    SHEAF COHERENCE         Local views -> global consistency
  0    PERSISTENCE LAYER       StorageProvider: membrane.db, vectors
```

## Key Rules

1. **`services/` = Crown Jewels**: Brain, Town, Witness, Atelier - domain logic
2. **`agents/` = Infrastructure**: PolyAgent, Operad, Sheaf - categorical primitives
3. **No explicit backend routes**: AGENTESE protocol IS the API
4. **Persistence through D-gent**: All state via `StorageProvider`
5. **Frontend lives with service**: `services/brain/web/` not `web/brain/`

## The Fullstack Flow

```
User Action (any surface)
        |
        v
  7. PROJECTION    "kg brain capture 'insight'"
        |
        v
  6. AGENTESE      logos.invoke("self.memory.capture", observer)
        |
        v
  5. NODE          @node("self.memory") class MemoryNode
        |
        v
  4. SERVICE       services/brain/persistence.py
        |
        v
  3. OPERAD        BRAIN_OPERAD.verify_operation("capture")
        |
        v
  2. POLYNOMIAL    brain_poly.transition(IDLE, "capture")
        |
        v
  1. SHEAF         brain_sheaf.glue([session, crystal, index])
        |
        v
  0. PERSISTENCE   storage.relational.execute(INSERT...)
```

## Derivation from Principles

| Principle | How Fullstack Embodies It |
|-----------|--------------------------|
| **COMPOSABLE** | Each layer composes with adjacent layers |
| **GENERATIVE** | Spec at L4 generates implementation at L0-L3 |
| **HETERARCHICAL** | No layer has intrinsic privilege |

---

*The Metaphysical Fullstack: where every agent is a complete vertical slice.*
"""
        return GenesisKBlock(
            id="METAPHYSICAL_FULLSTACK",
            title="METAPHYSICAL FULLSTACK - Every Agent Is a Vertical Slice",
            layer=3,
            galois_loss=0.12,
            content=content,
            derives_from=("COMPOSABLE", "GENERATIVE"),
            tags=("architecture", "L3", "fullstack", "layers", "vertical-slice"),
        )

    def create_hypergraph_editor(self) -> GenesisKBlock:
        """Create the Hypergraph Editor architecture K-Block."""
        content = """# HYPERGRAPH EDITOR - Constitutional Navigation

> *"The file is a lie. There is only the graph."*

**Layer**: L3 (Architecture)
**Galois Loss**: 0.18
**Derives From**: COMPOSABLE, HETERARCHICAL
**Evidence Tier**: EMPIRICAL

---

## The Paradigm Shift

| Traditional Editor | Hypergraph Editor |
|-------------------|-------------------|
| Open a file | Focus a node |
| Go to line 42 | Traverse an edge |
| Save | Commit to cosmos (with witness) |
| Browse directories | Navigate siblings (gj/gk) |
| Use find-in-files | Use graph search (g/) |
| Organize by folder | Organize by derivation |

## K-Blocks as Nodes, Derivations as Edges

```
                    CONSTITUTION.md (L0)
                          |
         +----------------+----------------+
         |                |                |
         v                v                v
    L2.5_COMPOSABLE  L2.7_GENERATIVE  L2.18_SHEAF
         |                |                |
         v                v                v
    +----------+     +----------+     +----------+
    | Agent    |---->| Fullstack|<----| K-Block  |
    | Town     |     | K-Block  |     | Spec     |
    +----------+     +----------+     +----------+
```

Each edge carries:
- **Type**: `derives_from`, `implements`, `tests`, `extends`, `contradicts`
- **Loss**: Galois loss for the derivation
- **Witness**: When the derivation was established

## The Six Editing Modes

```
NORMAL --+-- 'i' --> INSERT  (edit content)
         +-- 'ge' -> EDGE    (connect nodes)
         +-- 'v'  -> VISUAL  (select multiple)
         +-- ':'  -> COMMAND (AGENTESE)
         +-- 'gw' -> WITNESS (mark moments)
```

## Graph Navigation

```
gh    Parent (inverse derives_from edge)
gl    Child (forward derives_from edge)
gj    Next sibling (same parent)
gk    Prev sibling
gd    Go to definition (implements edge)
gr    Go to references (inverse implements)
gt    Go to tests
gf    Follow edge under cursor
```

## Derivation from Principles

| Principle | How Hypergraph Editor Embodies It |
|-----------|----------------------------------|
| **COMPOSABLE** | Edges ARE morphisms; navigation is composition |
| **HETERARCHICAL** | No folder hierarchy; derivation determines structure |
| **TASTEFUL** | Derivation trail shows constitutional coherence |

---

*The Hypergraph Editor: where files derive from principles, not folders.*
"""
        return GenesisKBlock(
            id="HYPERGRAPH_EDITOR",
            title="HYPERGRAPH EDITOR - Constitutional Navigation",
            layer=3,
            galois_loss=0.18,
            content=content,
            derives_from=("COMPOSABLE", "HETERARCHICAL"),
            tags=("architecture", "L3", "editor", "graph", "navigation", "derivation"),
        )

    def create_agentese(self) -> GenesisKBlock:
        """Create the AGENTESE protocol K-Block."""
        content = """# AGENTESE - The Protocol IS the API

> *"The noun is a lie. There is only the rate of change."*

**Layer**: L3 (Architecture)
**Galois Loss**: 0.10
**Derives From**: COMPOSABLE, ETHICAL
**Evidence Tier**: CATEGORICAL

---

## The Five Contexts

```
CONTEXT     PURPOSE                         EXAMPLES
----------------------------------------------------------------
world.*     The External                    world.house.manifest
            Entities, environments, tools   world.town.citizen

self.*      The Internal                    self.memory.capture
            Memory, capability, state       self.soul.dialogue

concept.*   The Abstract                    concept.compiler.priors
            Platonics, definitions, logic   concept.atelier.sketch

void.*      The Accursed Share              void.entropy.sip
            Entropy, serendipity            void.gratitude.offer

time.*      The Temporal                    time.witness.mark
            Traces, forecasts, schedules    time.differance.recent
```

## Why "The Noun Is a Lie"

Traditional APIs treat entities as primary: `GET /users/123`. The entity exists;
we act upon it.

AGENTESE inverts this: **the action is primary**. Entities emerge from the
pattern of actions upon them.

```python
# Traditional (noun-first)
user = await api.get("/users/123")

# AGENTESE (verb-first)
await logos.invoke("self.identity.rename", observer, new_name="New Name")
# The "user" is not a thing we manipulate - it's a pattern of identity operations
```

## How Handles Work

AGENTESE paths return **handles**, not data. A handle is a morphism from
Observer to Interaction:

```
Handle : Observer -> Interaction
```

Different observers perceive the same path differently:

```python
await logos.invoke("world.house.manifest", architect_umwelt)
# -> Blueprint{floor_plan, materials, load_calculations}

await logos.invoke("world.house.manifest", poet_umwelt)
# -> Metaphor{shelter, dwelling, threshold between worlds}
```

This is **observer-dependent projection**.

## The Universal Protocol

All transports collapse to the same invocation:

```python
# CLI
kg brain capture "insight"

# HTTP
POST /agentese/self.memory.capture {"content": "insight"}

# WebSocket
ws.send({"path": "self.memory.capture", "args": {"content": "insight"}})
```

**Key Insight**: There are no routes to maintain because the protocol IS the route.

## Derivation from Principles

| Principle | How AGENTESE Embodies It |
|-----------|-------------------------|
| **COMPOSABLE** | Handles ARE morphisms; paths compose |
| **ETHICAL** | Affordances respect observer capabilities |
| **HETERARCHICAL** | No transport has privilege; all collapse to invoke |

---

*AGENTESE: where the protocol is the API, and verbs precede nouns.*
"""
        return GenesisKBlock(
            id="AGENTESE",
            title="AGENTESE - The Protocol IS the API",
            layer=3,
            galois_loss=0.10,
            content=content,
            derives_from=("COMPOSABLE", "ETHICAL"),
            tags=("architecture", "L3", "protocol", "api", "verb-first", "universal"),
        )

    # =========================================================================
    # Factory Methods
    # =========================================================================

    def create_all(self) -> list[GenesisKBlock]:
        """
        Create all 22 genesis K-Blocks.

        Returns:
            List of all genesis K-Blocks in derivation order:
            - L0 Axioms (4)
            - L1 Kernel (3)
            - L2 Derived (4)
            - L1-L2 Principles (8)
            - L3 Architecture (4)
        """
        return [
            # L0 Axioms
            self.create_a1_entity(),
            self.create_a2_morphism(),
            self.create_a3_mirror(),
            self.create_g_galois(),
            # L1 Kernel
            self.create_compose(),
            self.create_judge(),
            self.create_ground(),
            # L2 Derived
            self.create_id(),
            self.create_contradict(),
            self.create_sublate(),
            self.create_fix(),
            # L1-L2 Principles
            self.create_constitution(),
            self.create_tasteful(),
            self.create_curated(),
            self.create_ethical(),
            self.create_joy_inducing(),
            self.create_composable(),
            self.create_heterarchical(),
            self.create_generative(),
            # L3 Architecture
            self.create_ashc(),
            self.create_metaphysical_fullstack(),
            self.create_hypergraph_editor(),
            self.create_agentese(),
        ]

    def create_by_layer(self, layer: int) -> list[GenesisKBlock]:
        """
        Create K-Blocks for a specific layer.

        Args:
            layer: Layer number (0-3)

        Returns:
            List of K-Blocks at that layer
        """
        all_blocks = self.create_all()
        return [b for b in all_blocks if b.layer == layer]

    def create_axioms(self) -> list[GenesisKBlock]:
        """Create all L0 axiom K-Blocks."""
        return [
            self.create_a1_entity(),
            self.create_a2_morphism(),
            self.create_a3_mirror(),
            self.create_g_galois(),
        ]

    def create_kernel(self) -> list[GenesisKBlock]:
        """Create all L1 kernel K-Blocks."""
        return [
            self.create_compose(),
            self.create_judge(),
            self.create_ground(),
        ]

    def create_derived(self) -> list[GenesisKBlock]:
        """Create all L2 derived primitive K-Blocks."""
        return [
            self.create_id(),
            self.create_contradict(),
            self.create_sublate(),
            self.create_fix(),
        ]

    def create_principles(self) -> list[GenesisKBlock]:
        """Create the Constitution and all 7 principle K-Blocks."""
        return [
            self.create_constitution(),
            self.create_tasteful(),
            self.create_curated(),
            self.create_ethical(),
            self.create_joy_inducing(),
            self.create_composable(),
            self.create_heterarchical(),
            self.create_generative(),
        ]

    def create_architecture(self) -> list[GenesisKBlock]:
        """Create all L3 architecture K-Blocks."""
        return [
            self.create_ashc(),
            self.create_metaphysical_fullstack(),
            self.create_hypergraph_editor(),
            self.create_agentese(),
        ]


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "GenesisKBlock",
    "GenesisKBlockFactory",
]
