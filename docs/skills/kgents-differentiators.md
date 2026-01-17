# Skill: The Five kgents Differentiators

> *"The differentiator IS the moat. The law IS the benchmark. The runtime IS the enforcement."*

**Difficulty**: Foundational
**Prerequisites**: Basic understanding of kgents architecture
**Files Touched**: Various — see each differentiator
**References**: `plans/theory-operationalization/00-master-operationalization.md`, `plans/theory-operationalization/06-synthesis-differentiation.md`

---

## Overview

kgents differentiates from frameworks like LangChain and AutoGPT through five key architectural decisions. These are not marketing claims—they are **implemented, tested, and operational**.

| # | Differentiator | LangChain/AutoGPT | kgents |
|---|----------------|-------------------|--------|
| 1 | Categorical Structure | Implicit, ad-hoc | **Explicit, law-verified at runtime** |
| 2 | Reward Function | None / external | **Constitution as objective function** |
| 3 | Disagreement Handling | Voting / override | **Cocone construction (dialectical fusion)** |
| 4 | Reasoning Traces | Logging, afterthought | **Writer monad (first-class objects)** |
| 5 | Failure Prediction | None | **Galois Loss predicts difficulty** |

**Strategic Implication**: Each differentiator must be demonstrated, not just claimed.

---

## Differentiator 1: Explicit Categorical Structure

### What It Means

Traditional agent frameworks use functions that compose ad-hoc. kgents agents are **morphisms in a category** with laws verified at runtime:

- **Identity Law**: `id >> f = f = f >> id`
- **Associativity**: `(f >> g) >> h = f >> (g >> h)`
- **Functor Laws**: `F(id) = id`, `F(f >> g) = F(f) >> F(g)`

The `PolyAgent[S, A, B]` captures mode-dependent behavior:

```python
PolyAgent[S, A, B] = (
    positions: FrozenSet[S],          # Valid states
    directions: S -> FrozenSet[Type], # State-dependent valid inputs
    transition: S x A -> (S, B)       # State x Input -> (NewState, Output)
)
```

### Why It Matters

- **Composition is guaranteed safe**: If two agents satisfy laws individually, their composition satisfies laws.
- **Refactoring is safe**: Law-preserving transformations cannot break behavior.
- **Debugging is tractable**: When something fails, you know which law was violated.

### How to Leverage It

```python
from agents.poly import PolyAgent, sequential, parallel, from_function

# Create a polynomial agent
DOUBLER = from_function("Doubler", lambda x: x * 2)
INCREMENTER = from_function("Incrementer", lambda x: x + 1)

# Compose with guaranteed law preservation
composed = sequential(DOUBLER, INCREMENTER)

# Laws hold:
# - (id >> composed) = composed = (composed >> id)
# - sequential(sequential(f, g), h) = sequential(f, sequential(g, h))
```

### Example Usage

```python
from agents.poly.protocol import PolyAgent
from enum import Enum, auto

class MemoryPhase(Enum):
    IDLE = auto()
    LOADING = auto()
    STORING = auto()

def memory_directions(phase: MemoryPhase) -> frozenset[type]:
    """Mode-dependent valid inputs."""
    match phase:
        case MemoryPhase.IDLE:
            return frozenset({LoadCommand, StoreCommand})
        case MemoryPhase.LOADING:
            return frozenset({LoadCommand})
        case MemoryPhase.STORING:
            return frozenset({StoreCommand})

def memory_transition(phase: MemoryPhase, input: Any) -> tuple[MemoryPhase, Any]:
    """Categorical transition function."""
    # ... implementation
    return new_phase, output

MEMORY_POLYNOMIAL: PolyAgent[MemoryPhase, Any, Any] = PolyAgent(
    name="MemoryPolynomial",
    positions=frozenset(MemoryPhase),
    _directions=memory_directions,
    _transition=memory_transition,
)
```

### Implementation Location

- **Core**: `impl/claude/agents/poly/protocol.py`
- **Laws**: `impl/claude/agents/operad/_tests/test_properties.py`
- **Skill**: `docs/skills/polynomial-agent.md`

---

## Differentiator 2: Constitution-as-Reward

### What It Means

The seven constitutional principles are not documentation—they are the **actual reward function** that drives agent behavior:

```
R(s, a, s') = sum_i w_i * R_i(s, a, s')
```

Where:
- `R_i` is the reward for principle `i`
- `w_i` is the weight for principle `i`
- ETHICAL floor (Amendment A) is a **hard constraint**: `R_ethical >= 0.6`

The relationship to Galois Loss:

```
R_constitutional = 1 - L_galois
```

### Why It Matters

- **Alignment is measurable**: Every action has a constitutional score.
- **ETHICAL violations are impossible**: The floor constraint rejects unethical actions regardless of other scores.
- **Learning has direction**: Agents optimize toward the Constitution, not arbitrary metrics.

### How to Leverage It

```python
from services.categorical.constitution import (
    Constitution,
    ConstitutionalEvaluation,
    ETHICAL_FLOOR_THRESHOLD,
)

# Evaluate an action against the Constitution
evaluation: ConstitutionalEvaluation = Constitution.evaluate(
    context=current_state,
    action=proposed_action,
)

# Check if it passes
if evaluation.passes:
    # Action is constitutional
    execute(action)
else:
    # Rejection with reason
    print(f"Rejected: {evaluation.rejection_reason}")
    # Example: "ETHICAL floor: 0.45 < 0.6"
```

### Example Usage

```python
from services.categorical.constitution import Constitution, Principle

# Get principle weights
weights = {
    Principle.ETHICAL: 2.0,      # Safety first
    Principle.COMPOSABLE: 1.5,   # Architecture second
    Principle.JOY_INDUCING: 1.2, # Kent's aesthetic
    Principle.TASTEFUL: 1.0,
    Principle.CURATED: 1.0,
    Principle.HETERARCHICAL: 1.0,
    Principle.GENERATIVE: 1.0,
}

# The ETHICAL floor is non-negotiable
# If ethical_score < 0.6, the action is rejected
# regardless of how high other scores are
```

### Implementation Location

- **Core**: `impl/claude/services/categorical/constitution.py`
- **Floor**: `ETHICAL_FLOOR_THRESHOLD = 0.6`
- **Integration**: `impl/claude/services/categorical/dp_bridge.py`

---

## Differentiator 3: Dialectic Fusion

### What It Means

When Kent and Claude disagree, the system does not vote or override. It constructs a **cocone** that synthesizes both positions:

```
       Kent's Position
            │
            ▼
    ┌───────────────┐
    │   Synthesis   │ ← Cocone (universal)
    └───────────────┘
            ▲
            │
      Claude's Position
```

The cocone is **universal**: any other synthesis that both positions can map to must factor through the cocone.

Sublate operation: `(Thesis, Antithesis) -> Synthesis`
- Preserves what's valid in both
- Resolves contradictions through a higher-order position

### Why It Matters

- **Disagreement is constructive**: Tension produces better solutions than either individual.
- **No silencing**: Both voices contribute to the synthesis.
- **Mathematical guarantee**: The cocone is the "best" synthesis (universal property).

### How to Leverage It

```python
from services.dialectic.fusion import (
    DialecticalFusionService,
    Position,
    FusionResult,
)

# Create positions
kent_position = Position(
    agent_id="kent",
    content="Use LangChain for production",
    reasoning="Scale, resources, proven in production",
    principle_alignment={Principle.COMPOSABLE: 0.9},
)

claude_position = Position(
    agent_id="claude",
    content="Build kgents infrastructure",
    reasoning="Novel contribution, joy-inducing, fits vision",
    principle_alignment={Principle.JOY_INDUCING: 0.95},
)

# Fuse via cocone construction
fusion = await DialecticalFusionService().fuse(
    kent=kent_position,
    claude=claude_position,
)

# Result contains synthesis
match fusion.result:
    case FusionResult.SYNTHESIS:
        print(f"Synthesis: {fusion.synthesis.content}")
        # "Build minimal kgents kernel, validate with one pilot,
        #  then decide whether to expand or migrate to LangChain"
    case FusionResult.VETO:
        print("Kent's disgust veto activated")
```

### Example Usage

```python
# The kg decide CLI captures dialectics
# kg decide --kent "WebSockets" --kent-reasoning "Bidirectional, familiar" \
#           --claude "SSE" --claude-reasoning "Simpler, HTTP-native" \
#           --synthesis "Use SSE" --why "Unidirectional is sufficient"

from services.dialectic.fusion import FusionOutcome

# Possible outcomes
FusionResult.CONSENSUS   # Both agree
FusionResult.SYNTHESIS   # New position that sublates both
FusionResult.KENT_PREVAILS  # Kent's position wins
FusionResult.CLAUDE_PREVAILS  # Claude's position wins (with justification)
FusionResult.DEFERRED    # More deliberation needed
FusionResult.VETO        # Kent's disgust veto (Article IV)
```

### Implementation Location

- **Core**: `impl/claude/services/dialectic/fusion.py`
- **Tests**: 22 passing tests
- **CLI**: `kg decide` command

---

## Differentiator 4: Witness as Writer Monad

### What It Means

Reasoning traces are not logs—they are **first-class monadic values** that compose via Kleisli arrows:

```python
Witnessed[A] = (A, Trace)

# Monad operations
return: A -> (A, [])
bind:   (A, T1) -> (A -> (B, T2)) -> (B, T1 ++ T2)

# Kleisli composition
f >=> g = lambda x: let (y, t1) = f(x)
                    in let (z, t2) = g(y)
                    in (z, t1 ++ t2)
```

Every effectful operation produces a `Witnessed[A]`. When operations compose, their traces concatenate lawfully.

### Why It Matters

- **Traces compose correctly**: No manual trace management.
- **Monad laws hold**: Verified by property-based tests.
- **Chain-of-thought is first-class**: CoT/ToT/GoT become proper monadic composition.

### How to Leverage It

```python
from services.witness.kleisli import (
    Witnessed,
    witness_pure,
    witness_bind,
    kleisli_compose,
    mark_action,
)

# Create a witnessed value
result: Witnessed[int] = witness_pure(42)

# Bind to another effectful operation
async def double_with_trace(x: int) -> Witnessed[int]:
    mark = await mark_action(f"Doubled {x} to {x * 2}")
    return Witnessed(value=x * 2, marks=[mark])

composed = await witness_bind(result, double_with_trace)
# composed.value = 84
# composed.marks = [original_marks + double_mark]

# Kleisli composition
f_then_g = kleisli_compose(f, g)  # Traces merge automatically
```

### Example Usage

```python
from services.witness.kleisli import Witnessed, witness_value

# Mark an action with its witness
@witness_value
async def analyze_prompt(prompt: str) -> dict:
    """Analysis is automatically witnessed."""
    result = await llm.analyze(prompt)
    return result

# The decorator wraps the result in Witnessed[dict]
# with marks recording the action, timing, etc.

# Compose witnessed operations
async def full_pipeline(input: str) -> Witnessed[Output]:
    # Each step produces a Witnessed value
    analyzed = await analyze_prompt(input)
    grounded = await ground_in_evidence(analyzed.value)
    synthesized = await synthesize_response(grounded.value)

    # Traces concatenate via bind
    return Witnessed(
        value=synthesized.value,
        marks=analyzed.marks + grounded.marks + synthesized.marks
    )
```

### Implementation Location

- **Core**: `impl/claude/services/witness/kleisli.py`
- **Tests**: 36 passing tests (including property-based law verification)
- **Integration**: Works with existing Mark infrastructure

---

## Differentiator 5: Galois Loss Prediction

### What It Means

Galois Loss predicts **task failure probability** from semantic distance:

```
L(P) = d(P, C(R(P)))
```

Where:
- `P` = Original prompt
- `R` = Restructure (LLM simplifies/decomposes)
- `C` = Reconstitute (LLM rebuilds from simplified form)
- `d` = Semantic distance (BERTScore -> cosine -> fallback)

**Interpretation**: High loss means the prompt has high semantic complexity that may cause failures.

**Fixed points**: Axioms are prompts where `L(P) < 0.05` — they cannot be simplified further.

### Why It Matters

- **Predict failures before they happen**: Route hard tasks to more capable systems.
- **Identify axioms**: Find the irreducible concepts in a domain.
- **Quantify complexity**: Semantic distance is a principled metric.

### How to Leverage It

```python
from services.zero_seed.galois import GaloisLossComputer

# Compute loss for a prompt
loss = await GaloisLossComputer().compute("Explain quantum entanglement")
# loss = 0.45 (moderate complexity)

loss = await GaloisLossComputer().compute("2 + 2")
# loss = 0.02 (near axiom — cannot be simplified)

# Predict failure probability
if loss > 0.5:
    recommendation = "High risk. Consider human review or decomposition."
elif loss > 0.3:
    recommendation = "Elevated risk. Use structured reasoning."
elif loss > 0.1:
    recommendation = "Moderate risk. Consider chain-of-thought."
else:
    recommendation = "Low risk. Proceed with confidence."
```

### Example Usage

```python
from services.zero_seed.galois import (
    GaloisLossComputer,
    find_fixed_points,
    LayerAssignment,
)

# Find axioms in a set of claims
claims = [
    "All humans are mortal",
    "Socrates is a human",
    "Therefore Socrates is mortal",
    "Mortality implies finite lifespan",
]

axioms = await find_fixed_points(claims, threshold=0.05)
# axioms = ["All humans are mortal", "Socrates is a human"]
# These are the irreducible foundations

# Assign claims to layers based on derivation depth
layers = await LayerAssignment().assign(claims)
# Layer 0: Axioms
# Layer 1: Direct derivations
# Layer 2+: Further derivations
```

### Implementation Location

- **Core**: `impl/claude/services/zero_seed/galois/`
- **Distance**: `impl/claude/services/zero_seed/galois/distance.py`
- **Layer Assignment**: `impl/claude/services/zero_seed/galois/layer_assignment.py`
- **Calibration**: `impl/claude/services/zero_seed/galois/calibration_corpus.json`

---

## Putting It Together

The five differentiators form a coherent system:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           kgents Differentiator Stack                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. GALOIS LOSS PREDICTION                                                   │
│     L(P) = d(P, C(R(P))) — predicts task difficulty                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. WITNESS AS WRITER MONAD                                                  │
│     Witnessed[A] = (A, Trace) — reasoning traces compose lawfully           │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. DIALECTIC FUSION                                                         │
│     Cocone(Kent, Claude) → Synthesis — disagreement becomes construction     │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. CONSTITUTION-AS-REWARD                                                   │
│     R = sum_i w_i * R_i with ETHICAL floor — alignment is measurable        │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. EXPLICIT CATEGORICAL STRUCTURE                                           │
│     PolyAgent[S,A,B] with verified laws — composition is guaranteed safe    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Integration Example

```python
# A fully differentiated operation:

# 1. Categorical: Use PolyAgent for state machine
from agents.poly import PolyAgent

# 2. Constitutional: Evaluate against principles
from services.categorical.constitution import Constitution

# 3. Dialectic: Fuse disagreements
from services.dialectic.fusion import DialecticalFusionService

# 4. Witness: Trace all reasoning
from services.witness.kleisli import Witnessed, witness_bind

# 5. Galois: Predict difficulty
from services.zero_seed.galois import GaloisLossComputer

async def constitutional_agent_action(
    agent: PolyAgent,
    input: Any,
    context: dict,
) -> Witnessed[Output]:
    # Predict difficulty
    loss = await GaloisLossComputer().compute(str(input))
    if loss > 0.5:
        # Route to human review
        return await escalate_to_human(input)

    # Execute with constitutional check
    evaluation = Constitution.evaluate(context, input)
    if not evaluation.passes:
        return Witnessed(
            value=Rejection(evaluation.rejection_reason),
            marks=[mark_constitutional_violation(evaluation)]
        )

    # Run through polynomial agent (categorical)
    state, output = agent.invoke(context["state"], input)

    # If disagreement with user, fuse dialectically
    if output.requires_resolution:
        fusion = await DialecticalFusionService().fuse(
            kent=user_position,
            claude=agent_position,
        )
        output = fusion.synthesis

    # Return with full witness trace
    return Witnessed(
        value=output,
        marks=[mark_action(output), mark_constitutional_score(evaluation)]
    )
```

---

## Checklist: Leveraging Differentiators

- [ ] **Categorical Structure**
  - [ ] Use `PolyAgent` for stateful agents
  - [ ] Verify laws in property tests
  - [ ] Compose via `sequential`/`parallel`

- [ ] **Constitution-as-Reward**
  - [ ] Call `Constitution.evaluate()` for actions
  - [ ] Respect ETHICAL floor (0.6)
  - [ ] Log constitutional scores in witness

- [ ] **Dialectic Fusion**
  - [ ] Use `kg decide` for Kent-Claude disagreements
  - [ ] Record fusion outcomes
  - [ ] Respect the disgust veto (Article IV)

- [ ] **Witness as Writer Monad**
  - [ ] Wrap effectful operations with `@witness_value`
  - [ ] Use `kleisli_compose` for pipelines
  - [ ] All marks compose lawfully

- [ ] **Galois Loss Prediction**
  - [ ] Compute loss before difficult tasks
  - [ ] Route high-loss tasks appropriately
  - [ ] Track axioms (fixed points)

---

## Related

- `docs/skills/polynomial-agent.md` — Building polynomial agents
- `docs/skills/witness-for-agents.md` — Witness protocol for agents
- `docs/skills/metaphysical-fullstack.md` — The fullstack architecture
- `plans/theory-operationalization/00-master-operationalization.md` — Master plan
- `plans/theory-operationalization/06-synthesis-differentiation.md` — Full differentiator analysis

---

*"The differentiator IS the moat. The law IS the benchmark. The runtime IS the enforcement."*
