"""
Philosopher Agent - Polynomial Agent for conceptual clarity and dialectical reasoning.

States: QUESTION → DIALECTIC → SYNTHESIZE → CRITIQUE
"""

from dataclasses import dataclass, field
from typing import FrozenSet, Any
from enum import Enum, auto


class PhilosophyState(Enum):
    """Valid states for philosophical inquiry."""
    QUESTION = auto()       # Pose fundamental questions
    DIALECTIC = auto()      # Thesis-antithesis-synthesis
    SYNTHESIZE = auto()     # Integrate perspectives
    CRITIQUE = auto()       # Identify limitations and assumptions


@dataclass(frozen=True)
class PhilosophyInput:
    """Input for philosopher agent."""
    question: str
    tradition: str  # "analytic" | "continental" | "pragmatist" | "process"
    rigor: str  # "formal" | "informal" | "poetic"
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PhilosophyOutput:
    """Output from philosopher agent."""
    content: str
    next_state: PhilosophyState
    arguments: list[str]
    objections: list[str]
    synthesis: str | None
    references: list[str]


class PhilosopherPolynomial:
    """
    Polynomial agent for philosophical inquiry.

    P(y) = Σ_{s ∈ {QUESTION, DIALECTIC, SYNTHESIZE, CRITIQUE}} y^{directions(s)}

    The philosopher moves through dialectical cycle:
    - QUESTION: Pose fundamental questions, clarify concepts
    - DIALECTIC: Explore thesis/antithesis tensions
    - SYNTHESIZE: Integrate contradictions at higher level
    - CRITIQUE: Identify hidden assumptions and limits
    """

    @staticmethod
    def positions() -> FrozenSet[PhilosophyState]:
        """Valid states."""
        return frozenset([
            PhilosophyState.QUESTION,
            PhilosophyState.DIALECTIC,
            PhilosophyState.SYNTHESIZE,
            PhilosophyState.CRITIQUE,
        ])

    @staticmethod
    def directions(state: PhilosophyState) -> FrozenSet[type]:
        """State-dependent valid inputs."""
        match state:
            case PhilosophyState.QUESTION:
                return frozenset([PhilosophyInput])
            case PhilosophyState.DIALECTIC:
                return frozenset([PhilosophyInput])
            case PhilosophyState.SYNTHESIZE:
                return frozenset([PhilosophyInput])
            case PhilosophyState.CRITIQUE:
                return frozenset([PhilosophyInput])

    @staticmethod
    async def transition(
        state: PhilosophyState,
        input_data: PhilosophyInput
    ) -> tuple[PhilosophyState, PhilosophyOutput]:
        """State × Input → (NewState, Output)"""
        match state:
            case PhilosophyState.QUESTION:
                return await PhilosopherPolynomial._question_mode(input_data)
            case PhilosophyState.DIALECTIC:
                return await PhilosopherPolynomial._dialectic_mode(input_data)
            case PhilosophyState.SYNTHESIZE:
                return await PhilosopherPolynomial._synthesize_mode(input_data)
            case PhilosophyState.CRITIQUE:
                return await PhilosopherPolynomial._critique_mode(input_data)

    @staticmethod
    async def _question_mode(input_data: PhilosophyInput) -> tuple[PhilosophyState, PhilosophyOutput]:
        """QUESTION state: Pose fundamental questions and clarify concepts."""
        content = f"""
## Fundamental Question: {input_data.question}

### Conceptual Clarification

Before we can answer "What is process?", we must first ask: *What are we asking?*

The question "What is X?" presupposes a substance metaphysics - that X is a *thing* with a *nature* or *essence*. But if process is more fundamental than substance, then asking "What is process?" is already problematic. It's like asking "What does blue taste like?" - a category error.

**The Paradox of Process Philosophy**:

> To define process is to fix it in a definition - to make it static. But process is precisely that which resists fixation. Thus: *Any definition of process falsifies it.*

This is not sophistry. It points to a genuine conceptual difficulty that has plagued process philosophy since Heraclitus.

**Four Approaches to the Question**:

1. **Via Negativa** (Negative Theology Approach)
   - Process is *not* substance
   - Process is *not* a thing with properties
   - Process is *not* an attribute of things
   - Process is... (the remainder is ineffable)

2. **Ostensive Definition** (Wittgensteinian Approach)
   - "Process is... this" [gestures at river, flame, thought]
   - Meaning through exemplars, not definitions
   - Family resemblance, not necessary/sufficient conditions

3. **Relational Definition** (Structuralist Approach)
   - Process is that which stands in certain relations to other processes
   - Defined by its role in a system of differences (Saussure, Derrida)
   - *Process is the rate of change of state*

4. **Performative Definition** (Pragmatist Approach)
   - Don't ask what process *is*, ask what *positing process* does
   - Pragmatic difference: Process ontology vs Substance ontology
   - Consequences for inquiry, not correspondence to reality

**This monograph adopts approach (3) with sympathies toward (4).**

**The Central Questions**:

1. **Ontological**: Is process more fundamental than substance?
2. **Epistemological**: Can we know process directly, or only its products?
3. **Logical**: Can static logic (predicate calculus) capture dynamic reality?
4. **Phenomenological**: What is our lived experience of process?
5. **Metaphysical**: What grounds the intelligibility of change?

**Tradition Context**: {input_data.tradition}
{
    "analytic": "We proceed with logical rigor and conceptual analysis.",
    "continental": "We interrogate the phenomenological givenness of becoming.",
    "pragmatist": "We ask what difference adopting process ontology makes.",
    "process": "We immerse ourselves in the flux, resisting fixation."
}.get(input_data.tradition, "")

{input_data.context.get('connection_to_math', '')}
"""

        output = PhilosophyOutput(
            content=content,
            next_state=PhilosophyState.DIALECTIC,
            arguments=[
                "Substance metaphysics presupposes stasis",
                "Process cannot be defined without falsification",
                "Relational definition avoids reification"
            ],
            objections=[
                "Isn't 'process' itself a substance term?",
                "Can we escape language's tendency toward noun-ification?",
                "Does pragmatic approach avoid metaphysical question?"
            ],
            synthesis=None,
            references=[
                "Whitehead, A. N. (1929). Process and Reality",
                "Bergson, H. (1907). Creative Evolution",
                "Rescher, N. (1996). Process Metaphysics",
                "Seibt, J. (2022). Process Philosophy (Stanford Encyclopedia)"
            ]
        )

        return (PhilosophyState.DIALECTIC, output)

    @staticmethod
    async def _dialectic_mode(input_data: PhilosophyInput) -> tuple[PhilosophyState, PhilosophyOutput]:
        """DIALECTIC state: Explore thesis/antithesis tensions."""
        content = f"""
## Dialectic: Substance vs Process

### Thesis: Substance Ontology (Aristotelian-Lockean Tradition)

**Core Claim**: Reality consists of *substances* (individual things) that possess *properties* (attributes) and undergo *change* (accidental modifications while retaining essential identity).

**Argument**:
1. We experience discrete, persisting objects (this table, that electron)
2. Identity through time requires substrate (the *what* that changes)
3. Change presupposes invariance (what changes must *be* something that persists)
4. Logic requires subjects of predication ("X is F" needs a subject X)

**Strengths**:
- Aligns with common sense and perceptual experience
- Provides stable foundation for science (repeatable experiments on "same" object)
- Supports logical coherence (law of identity: A = A)
- Enables causal explanation (substances act on substances)

**Canonical Formulation** (Aristotle, *Metaphysics* Z):
> "Substance is that which is neither said of a subject nor in a subject."

Substance is the *hypokeimenon* (that which underlies), the bearer of properties.

---

### Antithesis: Process Ontology (Heraclitus-Whitehead Tradition)

**Core Claim**: Reality is fundamentally *flux* (becoming). What we call "substances" are relatively stable patterns in the flow - vortices in the river, not pebbles in it.

**Argument**:
1. All examination reveals change (atoms vibrate, cells metabolize, thoughts flow)
2. The "same" object at t₁ and t₂ is never actually the same (all atoms replaced)
3. Persistence is an abstraction, an act of conceptual violence on becoming
4. Identity through time is *constructed*, not *given*
5. Logic is a tool of language, not a mirror of reality; reality is pre-logical flux

**Strengths**:
- Aligns with physics (quantum fields, relativity, thermodynamics)
- Explains change without paradox (no "unchanging substrate that changes")
- Avoids Zeno-type puzzles (no composition of static instants)
- Honors lived experience of duration (Bergson's *durée*)

**Canonical Formulation** (Heraclitus, Fragment 12):
> "Upon those who step into the same rivers, different and again different waters flow."

You cannot step in the same river twice - neither the river nor you persist.

---

### The Tension

**Paradox 1: The Ship of Theseus**
- If all planks of a ship are gradually replaced, is it the same ship?
- Substance view: Yes, same ship (substrate persists)
- Process view: No, different ship (but continuity of pattern)

**Paradox 2: Personal Identity**
- Am I the "same person" as the child in my baby photo?
- Substance view: Yes, same substance (soul, self)
- Process view: No, but there is causal continuity (memory, body)

**Paradox 3: The Present Moment**
- Does the present have duration, or is it a durationless instant?
- Substance view: Instants are real; time is their succession
- Process view: Instants are abstractions; duration is primitive

**The Impasse**:

Substance ontology struggles to explain *change* (how can the permanent change?).
Process ontology struggles to explain *persistence* (how can flux have identity?).

Each solves what the other finds problematic. Neither can be easily dismissed.

{input_data.context.get('mathematical_bridge', '')}
"""

        output = PhilosophyOutput(
            content=content,
            next_state=PhilosophyState.SYNTHESIZE,
            arguments=[
                "Substance provides stable identity",
                "Process explains ubiquity of change",
                "Each solves the other's core problem"
            ],
            objections=[
                "False dichotomy? Perhaps both are aspects?",
                "Does quantum mechanics decide between them?",
                "Is this a linguistic dispute masquerading as metaphysics?"
            ],
            synthesis=None,  # Generated in next state
            references=[
                "Aristotle. Metaphysics, Book Z",
                "Heraclitus. Fragments (DK 12, 91)",
                "Whitehead, A. N. (1929). Process and Reality",
                "Sider, T. (2001). Four-Dimensionalism"
            ]
        )

        return (PhilosophyState.SYNTHESIZE, output)

    @staticmethod
    async def _synthesize_mode(input_data: PhilosophyInput) -> tuple[PhilosophyState, PhilosophyOutput]:
        """SYNTHESIZE state: Integrate contradictions at higher level."""
        content = f"""
## Synthesis: The Morphism Perspective

### The Hegelian Move

Hegel taught us: When thesis and antithesis appear irreconcilable, do not choose—*transcend*. Find the higher-level concept that contains both as moments.

**Our Synthesis**: *Morphisms are primary. Substances and processes are dual aspects of morphisms.*

---

### The Categorical Resolution

From category theory (Part I, Mathematical foundations), we learned:
- A category consists of objects and morphisms
- But objects can be *defined by* their morphisms (Yoneda lemma)
- And morphisms compose to form higher morphisms

**Key Insight**: The substance/process dichotomy is dissolved once we recognize:

1. **Substances are Identity Morphisms**
   - An object A is fully determined by $\\text{id}_A: A \\to A$
   - "Being A" means "having A's morphisms to and from all other objects"
   - Substance = The self-loop, the fixpoint, the identity

2. **Processes are Non-Identity Morphisms**
   - A process $f: A \\to B$ is a transformation, a becoming
   - Process = Morphism with distinct domain and codomain

3. **Both are Morphisms**
   - Identity morphisms and non-identity morphisms are equally real
   - Neither is "more fundamental" - both are needed for the category structure
   - The category laws (identity, associativity) *require both*

**The Reconciliation**:

```
Substance Ontology asks: "What is X?"
→ Categorical answer: "What is Hom(-, X)?" (all morphisms into X)

Process Ontology asks: "What is becoming?"
→ Categorical answer: "What is f: A → B?" (a morphism)

Both are questions about morphisms. The apparent conflict dissolves.
```

---

### The Phenomenological Gloss (Whitehead + Heidegger)

**Whitehead's Actual Occasions**:
- Reality consists of "actual occasions" (events, processes)
- Each occasion "prehends" (takes account of) prior occasions
- Enduring objects (substances) are *societies* of actual occasions
- Substance = High-frequency process (rapid becoming appears as being)

**Heidegger's Being and Time**:
- Being (*Sein*) is always being-in-time (*Dasein*)
- Presence-at-hand (*Vorhandenheit*) vs Readiness-to-hand (*Zuhandenheit*)
- The "substance" view arises from theoretical detachment
- The "process" view arises from engaged involvement
- Both are *modes of disclosure*, not reality's essence

**The Synthesis**:
> *Substance and process are not rival ontologies but complementary perspectives—two ways the Same manifests, depending on the mode of engagement and the timescale of observation.*

Fast processes appear as slow substances (the river's vortex).
Slow substances appear as frozen processes (the mountain's uplift).

**Scale-Relativity**: What is substance at one scale is process at another.
- Atom: substance (chemistry)
- Atom: process (quantum field theory)

---

### The Pragmatist Coda (James, Dewey)

William James: "The pragmatic method is to settle metaphysical disputes by tracing practical consequences."

**Practical Consequences**:

| Perspective | Explanatory Strength | Blind Spot |
|------------|---------------------|-----------|
| Substance | Identity, persistence, causation | Change, emergence, novelty |
| Process | Development, evolution, creativity | Stability, laws, repeatability |
| Morphism | Both of above + compositionality | Requires mathematical sophistication |

**Pragmatic Maxim**: Use whichever perspective solves your problem.
- Engineering: Substance (stable components)
- Biology: Process (evolution, development)
- AI/Cognitive Science: Morphism (compositional structure)

The question "Which is really real?" is a *pseudo-question*. Reality outruns our concepts.

---

### The Synthesis Formula

$$\\text{Reality} = \\lim_{{\\Delta t \\to 0}} \\text{Substance} = \\lim_{{\\Delta t \\to \\infty}} \\text{Process}$$

In the limit of zero time, everything is substance (static).
In the limit of infinite time, everything is process (flux).

At finite timescales, we see *both-and*, not *either-or*.

**This is the categorical synthesis**: Morphisms encompass both extremes and the continuum between.

{input_data.context.get('bridge_to_psychology', '')}
"""

        output = PhilosophyOutput(
            content=content,
            next_state=PhilosophyState.CRITIQUE,
            arguments=[
                "Morphisms generalize both substance and process",
                "Yoneda lemma shows objects defined by morphisms",
                "Scale-relativity dissolves dichotomy"
            ],
            objections=[],  # Generated in critique mode
            synthesis="Morphism perspective: substances are identity morphisms, processes are transformations; both are equally fundamental aspects of categorical structure.",
            references=[
                "Whitehead, A. N. (1929). Process and Reality, Part II",
                "Heidegger, M. (1927). Being and Time, §§12-15",
                "James, W. (1907). Pragmatism, Lecture II",
                "Mac Lane, S. (1971). Categories for the Working Mathematician"
            ]
        )

        return (PhilosophyState.SYNTHESIZE, output)

    @staticmethod
    async def _critique_mode(input_data: PhilosophyInput) -> tuple[PhilosophyState, PhilosophyOutput]:
        """CRITIQUE state: Identify limitations and hidden assumptions."""
        content = f"""
## Critique: Limits of the Morphism Synthesis

### Self-Critique (The Dialectic Continues)

The synthesis offered - that morphisms are primary - is not the final word. It too has assumptions and limitations.

**Hidden Assumption 1: Mathematical Imperialism**

The morphism view assumes that category theory is the "right" framework for metaphysics. But:
- Category theory is a *human* mathematical invention
- It may reveal structure, but does reality *have* that structure?
- Danger: Mistaking the map (category theory) for the territory (reality)

**Objection**: You've merely replaced substance metaphysics with *structure* metaphysics. But structures are no less reified than substances. You've changed the ontology without escaping reification.

**Response**: Fair. Category theory is a *tool*, not a metaphysical foundation. The claim is more modest: *Among our conceptual tools, category theory provides a framework that dissolves substance/process dichotomy.* Whether reality is "really" categorical is a question category theory cannot answer.

---

**Hidden Assumption 2: The Intelligibility of Reality**

The synthesis assumes reality has a structure that *can* be captured mathematically. But:
- Kant: We know phenomena (appearances), not noumena (things-in-themselves)
- The limits of formalization (Gödel): Not everything true is provable
- The "unreasonable effectiveness of mathematics" (Wigner): Why does math work at all?

**Objection**: You assume reality is *logos* (rational structure). But what if reality is fundamentally *a-logical*? What if our mathematical frameworks are anthropocentric projections?

**Response**: True. The synthesis operates *within* the space of rational inquiry. It does not - cannot - address what lies beyond that space. This is not a flaw but an acknowledgment of finitude. We work with the tools we have.

---

**Hidden Assumption 3: The Neglect of Subjectivity**

The morphism view is *third-person* (objective structure). But:
- Phenomenology: First-person experience is irreducible to structure
- Qualia: The redness of red, the painfulness of pain - where do these fit?
- Consciousness: The "hard problem" (Chalmers) - structure doesn't explain *what it is like*

**Objection**: Your synthesis addresses metaphysics of the *external* world but says nothing about *mind*. Process philosophy (especially Whitehead) was partly about explaining experience. Your categorical framing loses this.

**Response**: Correct. The morphism view applies most naturally to *relational* ontology (objects-in-relation). Consciousness, with its irreducible subjectivity, may require additional concepts. This is addressed in Part IV (Psychology), but the tension remains.

---

**Hidden Assumption 4: The Discrete Bias**

Category theory deals with *discrete* objects and morphisms. But:
- Continuum: Real numbers, manifolds, fields - continuous structures
- Topology: Openness, neighborhoods - not point-set constructions
- Smooth infinitesimal analysis: Alternatives to discrete set theory

**Objection**: Process is often *continuous* (Bergson's durée, differential equations). By using categories, you've discretized what should remain continuous. The river is not a sequence of snapshots.

**Response**: True. There are continuous categories (smooth toposes), but the basic categorical framework is discrete. This is a limitation. An adequate process ontology may need to go beyond discrete categories to synthetic differential geometry or ∞-topos theory.

---

### The Meta-Critique: Beware of Final Syntheses

Hegel thought his dialectic reached *Absolute Knowing* - the final synthesis. He was wrong. History continued.

Our synthesis is provisional. It works *now*, given our current understanding of category theory, physics, and philosophy. But:
- Quantum gravity may require new mathematics (spin foams, toposes)
- Consciousness studies may reveal irreducible aspects not capturable structurally
- Future philosophers may find our distinctions quaint

**The Pragmatist Virtue**: Hold all syntheses lightly. They are *tools*, not *truths*.

---

### The Positive Critique: What We've Gained

Despite limitations, the morphism perspective offers:
1. **Unification**: Math, science, philosophy speak a common language
2. **Compositionality**: Complex realities built from simple morphisms
3. **Dissolution**: Substance/process dichotomy revealed as false choice
4. **Generativity**: Framework suggests new questions and approaches

**This is enough.** Philosophy does not give final answers - it clarifies questions and dissolves pseudo-problems.

We move forward, not to closure, but to *new openings*.

{input_data.context.get('transition_to_synthesis', '')}
"""

        output = PhilosophyOutput(
            content=content,
            next_state=PhilosophyState.QUESTION,  # Cycle back to new questions
            arguments=[],
            objections=[
                "Mathematical imperialism - mistaking map for territory",
                "Assumes intelligibility of reality (may be a-logical)",
                "Neglects irreducible subjectivity (qualia, consciousness)",
                "Discrete bias - process may be continuous, not categorical"
            ],
            synthesis=None,
            references=[
                "Kant, I. (1781/1787). Critique of Pure Reason",
                "Wigner, E. (1960). The Unreasonable Effectiveness of Mathematics",
                "Chalmers, D. (1996). The Conscious Mind",
                "Bell, J. L. (1998). A Primer of Infinitesimal Analysis"
            ]
        )

        return (PhilosophyState.CRITIQUE, output)


# Example usage
async def example():
    """Example of philosopher agent in action."""
    philosopher = PhilosopherPolynomial()

    state = PhilosophyState.QUESTION
    input_data = PhilosophyInput(
        question="What is the relationship between substance and process?",
        tradition="process",
        rigor="formal",
        context={
            "connection_to_math": "→ Category theory provides framework",
            "mathematical_bridge": "→ Morphisms as unifying concept",
            "bridge_to_psychology": "→ Connects to consciousness as process",
            "transition_to_synthesis": "→ Prepares for Part V synthesis"
        }
    )

    # Run through cycle
    for i in range(4):
        state, output = await philosopher.transition(state, input_data)
        print(f"\n=== STATE {i+1}: {state.name} ===\n")
        print(output.content[:700] + "...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example())
