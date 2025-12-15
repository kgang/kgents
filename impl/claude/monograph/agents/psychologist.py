"""
Psychologist Agent - Polynomial Agent for understanding mind and experience.

States: PHENOMENOLOGY → MECHANISM → DEVELOPMENT → INTEGRATION
"""

from dataclasses import dataclass, field
from typing import FrozenSet, Any
from enum import Enum, auto


class PsychologyState(Enum):
    """Valid states for psychological inquiry."""
    PHENOMENOLOGY = auto()  # First-person lived experience
    MECHANISM = auto()      # Cognitive/neural mechanisms
    DEVELOPMENT = auto()     # Developmental trajectories
    INTEGRATION = auto()    # Synthesis into whole person


@dataclass(frozen=True)
class PsychologyInput:
    """Input for psychologist agent."""
    phenomenon: str
    approach: str  # "cognitive" | "developmental" | "phenomenological" | "neuroscientific"
    level: str  # "subjective" | "behavioral" | "computational" | "neural"
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PsychologyOutput:
    """Output from psychologist agent."""
    content: str
    next_state: PsychologyState
    mechanisms: list[str]
    phenomena: list[str]
    developmental_stages: list[str] | None
    references: list[str]


class PsychologistPolynomial:
    """
    Polynomial agent for psychological inquiry.

    P(y) = Σ_{s ∈ {PHENOMENOLOGY, MECHANISM, DEVELOPMENT, INTEGRATION}} y^{directions(s)}

    The psychologist moves through understanding mind:
    - PHENOMENOLOGY: Describe lived experience
    - MECHANISM: Explain cognitive/neural processes
    - DEVELOPMENT: Trace developmental trajectories
    - INTEGRATION: Synthesize into unified understanding
    """

    @staticmethod
    def positions() -> FrozenSet[PsychologyState]:
        """Valid states."""
        return frozenset([
            PsychologyState.PHENOMENOLOGY,
            PsychologyState.MECHANISM,
            PsychologyState.DEVELOPMENT,
            PsychologyState.INTEGRATION,
        ])

    @staticmethod
    def directions(state: PsychologyState) -> FrozenSet[type]:
        """State-dependent valid inputs."""
        return frozenset([PsychologyInput])  # All states accept same input type

    @staticmethod
    async def transition(
        state: PsychologyState,
        input_data: PsychologyInput
    ) -> tuple[PsychologyState, PsychologyOutput]:
        """State × Input → (NewState, Output)"""
        match state:
            case PsychologyState.PHENOMENOLOGY:
                return await PsychologistPolynomial._phenomenology_mode(input_data)
            case PsychologyState.MECHANISM:
                return await PsychologistPolynomial._mechanism_mode(input_data)
            case PsychologyState.DEVELOPMENT:
                return await PsychologistPolynomial._development_mode(input_data)
            case PsychologyState.INTEGRATION:
                return await PsychologistPolynomial._integration_mode(input_data)

    @staticmethod
    async def _phenomenology_mode(input_data: PsychologyInput) -> tuple[PsychologyState, PsychologyOutput]:
        """PHENOMENOLOGY state: Describe lived experience."""
        content = f"""
## Phenomenology of Consciousness: The Temporal Flow

### The Lived Experience of Process

Before we theorize about consciousness, we must describe *what it is like* - the phenomenological given.

**The Specious Present** (William James, 1890):

> "The practically cognized present is no knife-edge, but a saddle-back, with a certain breadth of its own on which we sit perched, and from which we look in two directions into time."

When you attend to your immediate experience, you do not find a sequence of discrete "now" moments like beads on a string. Instead, you find:

1. **Thickness of the Present**
   - The present moment has *duration* - it is not a durationless instant
   - You hear a *melody*, not isolated notes
   - You perceive *motion*, not static positions
   - Temporal binding: ~50-500ms window of simultaneity

2. **Retention and Protention** (Husserl, 1905)
   - **Retention**: The just-past is still present (the echo of the note)
   - **Protention**: The about-to-be is already anticipated (the melody's continuation)
   - Consciousness is three-fold: retention-primal impression-protention
   - Not memory (which re-presents the past), but *still-present* past

3. **The Flow Itself**
   - Consciousness is not *in* time - consciousness *is* temporal flow
   - "I think" is always "I am thinking" (gerund, not infinitive)
   - Self-awareness is self-*becoming*-awareness
   - No eternal witness outside the stream

**The Metaphor of the River** (Heraclitus via James):

```
     Retention  ←  Present  →  Protention
        /           |           \\
    [past fading] [vivid now] [future forming]
           \\         |         /
            \\        |        /
             \\       |       /
              \\      |      /
               \\     |     /
                \\    |    /
                 ↓    ↓    ↓
           The Stream of Consciousness
```

You cannot grasp the same thought twice - both you and the thought are in flux.

**Phenomenological Observation** (First-Person Report):

*Try this now*: Attend to your present experience. Notice:
- The sense of *duration* (not point-like instant)
- The *fuzzy boundaries* between now and just-past
- The *anticipatory* quality of the present (it leans forward)
- The impossibility of capturing the present (it slips away in the grasping)

**The Paradox**: To introspect is to *stop* the flow. But the flow doesn't stop. So introspection reveals a *frozen* version of the flow - like photographing a river. The photograph shows water, but not flowing.

**Implication for Process Ontology**:

If consciousness is fundamentally *temporal becoming*, then:
- Substance ontology cannot account for it (consciousness has no substrate)
- Process ontology is vindicated at the level of immediate experience
- The "I" that persists through time is not a substance but a *continuity of process*

**Connection to Thermodynamics**: Like dissipative structures (Part II), consciousness persists through continuous energy dissipation (neural metabolism). Stop the energy flow, and consciousness vanishes. The pattern is the process.

{input_data.context.get('bridge_to_mechanism', '')}
"""

        output = PsychologyOutput(
            content=content,
            next_state=PsychologyState.MECHANISM,
            mechanisms=[],  # Generated in mechanism state
            phenomena=[
                "Specious present (temporal thickness)",
                "Retention-protention structure",
                "Stream of consciousness",
                "Self as process, not substance"
            ],
            developmental_stages=None,
            references=[
                "James, W. (1890). The Principles of Psychology, Chapter XV",
                "Husserl, E. (1905). The Phenomenology of Internal Time-Consciousness",
                "Varela, F. J. (1999). The Specious Present: A Neurophenomenology of Time Consciousness",
                "Gallagher, S., & Zahavi, D. (2020). The Phenomenological Mind (3rd ed.)"
            ]
        )

        return (PsychologyState.MECHANISM, output)

    @staticmethod
    async def _mechanism_mode(input_data: PsychologyInput) -> tuple[PsychologyState, PsychologyOutput]:
        """MECHANISM state: Explain cognitive/neural processes."""
        content = f"""
## Mechanism: Predictive Processing and the Bayesian Brain

### From Phenomenology to Mechanism

We've described the *what* (temporal flow of consciousness). Now we ask: *How* is this implemented in the brain?

**The Predictive Processing Framework** (Friston, Clark, Hohwy):

The brain is not a passive receiver of sensory input. It is an **active predictor** that constantly generates hypotheses about the causes of sensory data.

**Core Mechanism**:

1. **Top-Down Prediction**
   - Higher cortical areas generate predictions about lower areas
   - "I expect to see a face" → prediction flows down visual hierarchy
   - Prediction is Bayesian prior $P(\\text{cause})$

2. **Bottom-Up Prediction Error**
   - Sensory input compared to prediction
   - Mismatch generates *prediction error*: $\\text{Error} = \\text{Sensory} - \\text{Predicted}$
   - Error propagates upward to update predictions

3. **Precision-Weighted Update**
   - Not all errors are treated equally
   - High-precision errors (reliable signals) → large updates
   - Low-precision errors (noise) → ignored
   - Precision = inverse variance = confidence

**Mathematical Formulation**:

Let $x_t$ be the true state of the world, $y_t$ the sensory observation.

**Generative Model** (brain's hypothesis):
$$P(y_t | x_t, \\theta)$$

where $\\theta$ are model parameters.

**Inference** (perception):
$$P(x_t | y_t, \\theta) \\propto P(y_t | x_t, \\theta) \\cdot P(x_t | \\theta)$$

This is Bayes' rule: Posterior ∝ Likelihood × Prior

**Learning** (updating model):
$$\\theta_{t+1} = \\theta_t + \\alpha \\cdot \\nabla_{\\theta} \\log P(y_t | x_t, \\theta)$$

Gradient ascent on log-likelihood (maximize fit to data).

---

### Free Energy Minimization

**The Unifying Principle** (Friston, 2010):

The brain minimizes *variational free energy*:
$$F = \\mathbb{E}_Q[\\log Q(x) - \\log P(x, y)]$$

where:
- $Q(x)$ is the brain's approximate posterior (its beliefs)
- $P(x, y)$ is the true joint distribution
- $F$ is an upper bound on surprise $-\\log P(y)$

**Interpretation**:
- Minimizing $F$ = Minimizing surprise = Maximizing accuracy of predictions
- Achieved via perception (update beliefs) and action (sample confirming evidence)
- Active inference: *We act to confirm our predictions* (self-fulfilling prophecies)

**Connection to Thermodynamics**:
Free energy (information theory) ≈ Free energy (thermodynamics).
The brain is a dissipative structure minimizing informational free energy through metabolic free energy dissipation.

---

### Neural Implementation

**Hierarchical Predictive Coding**:

```
Layer 5 (High-level): "It's a cat"
    ↓ (prediction)      ↑ (error)
Layer 4 (Mid-level): "Whiskers, ears, fur"
    ↓ (prediction)      ↑ (error)
Layer 3 (Low-level): "Edges, orientations"
    ↓ (prediction)      ↑ (error)
Layer 2 (V1): Retinal input
```

**Canonical Microcircuit** (Bastos et al., 2012):
- Superficial layers (2/3): Send prediction error upward
- Deep layers (5/6): Send predictions downward
- Inhibitory interneurons: Implement precision weighting

**Experimental Evidence**:
- Repetition suppression: Predictable stimuli → reduced neural response
- Mismatch negativity (MMN): Unexpected stimuli → increased response
- Attention modulates prediction error precision (Feldman & Friston, 2010)

---

### Consciousness as Integrated Prediction Error

**Hypothesis**: Conscious experience arises when high-precision prediction errors cannot be resolved (Hohwy, 2013).

When predictions *fail* and the error is *important*, consciousness emerges to arbitrate:
- Routine predictions: unconscious (walking, driving on autopilot)
- Failed predictions: conscious (unexpected obstacle, surprising stimulus)
- Consciousness = Meta-level prediction error resolution

**The Hard Problem Revisited**:
This doesn't *solve* the hard problem (why there is *something it is like*), but it *dissolves* the easy/hard distinction:
- "Why is this conscious?" → "Why did prediction fail here?"
- Consciousness is not a separate thing to explain, but the process of active inference itself at the highest level

**Connection to Process Ontology**:
- No "observer" watching the predictions - the prediction itself is the experiencing
- Consciousness is not a state but a *dynamics* (prediction-error minimization loop)
- The "self" is a self-model (predictive model of the organism's states)

{input_data.context.get('bridge_to_development', '')}
"""

        output = PsychologyOutput(
            content=content,
            next_state=PsychologyState.DEVELOPMENT,
            mechanisms=[
                "Predictive processing (top-down/bottom-up)",
                "Free energy minimization",
                "Hierarchical predictive coding",
                "Precision-weighted prediction error"
            ],
            phenomena=[],
            developmental_stages=None,
            references=[
                "Friston, K. (2010). The free-energy principle: A unified brain theory?",
                "Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science",
                "Hohwy, J. (2013). The Predictive Mind",
                "Bastos, A. M., et al. (2012). Canonical microcircuits for predictive coding"
            ]
        )

        return (PsychologyState.DEVELOPMENT, output)

    @staticmethod
    async def _development_mode(input_data: PsychologyInput) -> tuple[PsychologyState, PsychologyOutput]:
        """DEVELOPMENT state: Trace developmental trajectories."""
        content = f"""
## Development: Cognitive Ontogeny as Phase Transitions

### Development as Process

If consciousness is process and brains are predictive engines, how does this system *develop*? Is development continuous or does it exhibit critical transitions?

**Piaget's Stages Revisited**:

Jean Piaget (1896-1980) proposed that cognitive development proceeds through discrete stages:

1. **Sensorimotor** (0-2 years): Action-based understanding
2. **Preoperational** (2-7 years): Symbolic thought emerges
3. **Concrete Operational** (7-11 years): Logical operations on concrete objects
4. **Formal Operational** (11+ years): Abstract, hypothetical reasoning

**The Question**: Are these truly discrete stages, or arbitrary divisions of continuous growth?

---

### Developmental Catastrophe Theory (van der Maas, 1998)

**Hypothesis**: Stage transitions are **catastrophic bifurcations** - sudden qualitative shifts in cognitive organization, analogous to phase transitions in physics.

**Cusp Catastrophe Model**:

Let $x$ be behavioral complexity, $a$ be cognitive capacity, $b$ be task demands.

The potential function:
$$V(x; a, b) = \\frac{1}{4}x^4 - \\frac{1}{2}ax^2 - bx$$

Critical points satisfy $\\frac{\\partial V}{\\partial x} = 0$:
$$x^3 - ax - b = 0$$

**Bifurcation**:
- For small $a$: One stable solution (pre-transition)
- At critical $a_c$: Two stable solutions emerge (bistability)
- Past $a_c$: System jumps to new stable state (stage transition)

**Predictions**:
1. **Sudden transitions**: Gradual capacity increase → abrupt behavioral shift
2. **Hysteresis**: Transition point differs for forward vs backward development
3. **Bimodality**: Children cluster at discrete stages, not uniformly distributed
4. **Critical slowing**: Near transition, increased variability and slowing

**Empirical Confirmation**:
- Conservation tasks (Piaget): Sharp transition around age 6-7
- Theory of mind: Sudden onset of false-belief understanding ~4 years
- Infant stepping reflex: Disappears then reappears (hysteresis)

---

### Dynamic Systems Perspective (Thelen & Smith, 1994)

**Core Claim**: Development is not a ladder (discrete stages) but a **landscape** of attractors that reorganize over time.

**Attractor Dynamics**:

Imagine a ball rolling on a landscape with valleys (attractors) and hills (repellers):

```
       Sensorimotor          Preoperational          Concrete Operational
           Basin                  Basin                     Basin
            ___                    ___                       ___
           /   \\                  /   \\                     /   \\
  ________/     \\________________/     \\___________________/     \\____
```

- Infant starts in sensorimotor basin
- Development = gradual change of landscape (valleys deepen/shallow)
- Transition = ball rolls over saddle point into new basin

**A-not-B Error Example** (Thelen et al., 2001):

Infants (8-10 months) search for hidden object at location A. When moved to B, they still search at A.
- Not due to representational deficit (Piaget's view)
- Due to attractor dynamics: Motor habit (reaching to A) is strong attractor
- Transition: As working memory matures, B-attractor strengthens until it "wins"

**Soft Assembly**: Behavior emerges from interaction of:
- Neural maturation
- Body morphology (motor constraints)
- Environmental affordances
- Prior experience

No central "program" - development is **self-organizing**.

---

### Connection to Dissipative Structures

**Analogy**:

| Thermodynamics | Development |
|----------------|-------------|
| Control parameter (temperature) | Cognitive capacity |
| Bifurcation point | Stage transition |
| Pattern formation | New cognitive structure |
| Energy dissipation | Metabolic cost of learning |

Both are:
- Far-from-equilibrium systems
- Exhibit critical transitions (bifurcations)
- Display self-organization
- Require continuous energy input (metabolism)

**Implication**: Cognitive development is not *programmed* (genetic determinism) but *self-organizing* (epigenetic dynamics). Genes provide constraints, but structure emerges from process.

**Process Ontology Vindicated**:
- The child at age 5 and age 10 is not the "same substance" with different properties
- The child is a *developmental trajectory* through state space
- Personal identity = continuity of causal process, not substrate

{input_data.context.get('bridge_to_integration', '')}
"""

        output = PsychologyOutput(
            content=content,
            next_state=PsychologyState.INTEGRATION,
            mechanisms=[],
            phenomena=[],
            developmental_stages=[
                "Sensorimotor (0-2): Action-based",
                "Preoperational (2-7): Symbolic thought",
                "Concrete Operational (7-11): Logical operations",
                "Formal Operational (11+): Abstract reasoning",
                "Transitions as catastrophic bifurcations"
            ],
            references=[
                "Piaget, J. (1952). The Origins of Intelligence in Children",
                "van der Maas, H. L. J., & Molenaar, P. C. M. (1992). Stagewise cognitive development: An application of catastrophe theory",
                "Thelen, E., & Smith, L. B. (1994). A Dynamic Systems Approach to Development",
                "Thelen, E., et al. (2001). The dynamics of embodiment: A field theory of infant perseverative reaching"
            ]
        )

        return (PsychologyState.INTEGRATION, output)

    @staticmethod
    async def _integration_mode(input_data: PsychologyInput) -> tuple[PsychologyState, PsychologyOutput]:
        """INTEGRATION state: Synthesize into unified understanding."""
        content = f"""
## Integration: Mind as Process at Multiple Scales

### Synthesis: The Multi-Scale Picture

We have explored consciousness from three angles:
1. **Phenomenology**: Lived experience of temporal flow
2. **Mechanism**: Predictive processing and free energy minimization
3. **Development**: Self-organizing phase transitions

Now we integrate: *How do these fit together?*

---

### The Three-Level Architecture

**Level 1: Phenomenological (First-Person)**
- Subjective experience: temporal flow, retention-protention
- The "what it is like"
- Irreducible to third-person description (qualia)

**Level 2: Computational (Sub-Personal)**
- Predictive processing: prediction-error minimization
- Bayesian inference: update beliefs based on evidence
- Implementable in any substrate (brain, computer, etc.)

**Level 3: Neural (Biological)**
- Hierarchical cortical dynamics
- Canonical microcircuits (superficial/deep layers)
- Neurochemical precision modulation (dopamine, acetylcholine)

**The Integration Question**: How do these levels relate?

---

### Neurophenomenology (Varela, 1996)

**Proposal**: First-person and third-person are *mutually constraining*:
- Phenomenology constrains mechanism (must explain lived experience)
- Mechanism constrains phenomenology (neurobiological limits on experience)
- Neither reduces to the other; both are required

**The Circulation** (Varela):

```
Phenomenological         →         Neuroscientific
   Description                      Mechanisms
      ↑                                  |
      |                                  ↓
  Disciplined                       Interpret
  Introspection    ←             Neural Dynamics
```

Example:
- Meditative practice reveals fine-grained temporal structure of experience
- This guides experiments on gamma oscillations (40 Hz) in cortex
- Neural findings refine phenomenological descriptions
- Mutual bootstrapping

---

### The Unified View: Process at All Scales

**Phenomenological Scale** (seconds):
- Specious present: ~3 seconds (Pöppel, 1978)
- Attentional blink: ~200-500ms
- Subjective "now" is not instant but extended process

**Computational Scale** (milliseconds):
- Prediction-error cycles: ~100ms (gamma oscillations)
- Attentional precision updates: ~200ms (P300 wave)
- Hierarchical message passing: multiple timescales

**Developmental Scale** (years):
- Stage transitions: years to decades
- Critical periods: months (language, vision)
- Lifelong plasticity: ongoing throughout life

**Unifying Principle**: At every scale, *process precedes product*:
- Phenomenology: Consciousness is *becoming*, not *being*
- Computation: Inference is *iteration*, not *retrieval*
- Development: Structure is *emergence*, not *unfolding*

---

### Mind as Dissipative Structure

**The Final Synthesis**:

Mind is a **multi-scale dissipative structure**:
1. Requires continuous energy (glucose metabolism: ~20% of body's energy)
2. Far from equilibrium (firing rates, neurotransmitter cycling)
3. Self-organizing (no central homunculus)
4. Produces entropy (heat dissipation, waste products)
5. Maintains coherent pattern through constant flux

**When the energy stops** (death, anesthesia), the pattern vanishes:
- No "soul" that persists without process
- No substrate that remains when function ceases
- Mind *is* the process, not a property of a substance

**Philosophical Consequences**:

1. **Anti-Cartesian**: No mind-body dualism - mind is brain process
2. **Anti-Computational** (in strong sense): Mind is not software on hardware - it's the dynamics itself
3. **Anti-Reductionist**: Cannot reduce phenomenology to neurons (levels are coupled but distinct)
4. **Process Ontology**: Consciousness is a *verb* masquerading as a *noun*

---

### The Meta-Level Insight

This entire analysis *exemplifies* what it describes:
- The understanding you gain reading this is itself a process (prediction-error minimization)
- Your comprehension is not a state but a *becoming* (integration over reading time)
- The concepts transform as you engage them (developmental phase transition)

**The reader is doing what the text describes**: using predictive processing to understand predictive processing, experiencing temporal flow while reading about temporal flow.

*The form mirrors the content. The method embodies the message.*

This is the monograph's deepest move: Not merely *describing* process ontology, but *instantiating* it in the act of reading.

{input_data.context.get('transition_to_synthesis_part', '')}
"""

        output = PsychologyOutput(
            content=content,
            next_state=PsychologyState.PHENOMENOLOGY,  # Cycle back
            mechanisms=[],
            phenomena=[],
            developmental_stages=None,
            references=[
                "Varela, F. J. (1996). Neurophenomenology: A methodological remedy for the hard problem",
                "Gallagher, S., & Zahavi, D. (2020). The Phenomenological Mind (3rd ed.)",
                "Thompson, E. (2007). Mind in Life: Biology, Phenomenology, and the Sciences of Mind",
                "Pöppel, E. (1978). Time perception"
            ]
        )

        return (PsychologyState.INTEGRATION, output)


# Example usage
async def example():
    """Example of psychologist agent in action."""
    psychologist = PsychologistPolynomial()

    state = PsychologyState.PHENOMENOLOGY
    input_data = PsychologyInput(
        phenomenon="Consciousness as Temporal Process",
        approach="phenomenological",
        level="subjective",
        context={
            "bridge_to_mechanism": "→ Prepares for predictive processing framework",
            "bridge_to_development": "→ Sets up developmental phase transitions",
            "bridge_to_integration": "→ Leads to multi-scale synthesis",
            "transition_to_synthesis_part": "→ Bridges to Part V final synthesis"
        }
    )

    # Run through cycle
    for i in range(4):
        state, output = await psychologist.transition(state, input_data)
        print(f"\n=== STATE {i+1}: {state.name} ===\n")
        print(output.content[:700] + "...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example())
