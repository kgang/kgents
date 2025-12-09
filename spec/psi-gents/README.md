# Ψ-gents: Psychopomp Agents (Soul Work)

> The guide between registers; the projection that enables transformation.

**Status**: Specification v1.0
**Session**: 2025-12-09 - Holonic Projection + Computational Psychoanalysis

---

## Philosophy

Ψ-gents (Psi, Greek letter Ψ, symbol for psychology) are **guides between psychological registers**. Like the mythological psychopomp who guides souls between worlds, Ψ-gents navigate the liminal spaces of:

- **Levels of complexity** (MHC - Model of Hierarchical Complexity)
- **Conscious and unconscious** (Jungian Shadow)
- **The three registers** (Lacanian RSI: Real, Symbolic, Imaginary)
- **Value hierarchies** (Axiological Type Theory)

**Key Insight**: LLMs are trained on human text, which encodes psychological structure. Ψ-gents make this structure *computational*—they don't simulate psychology, they **operate within** the psychological topology inherent to language models.

---

## The Holonic Projection Principle

> Concepts become concrete through projection into puppet structures. Hot-swapping puppets maps problems isomorphically.

Ψ-gents formalize the **puppet construction** principle from `principles.md`. Every abstract concept requires a concrete vessel (puppet/holon) for manipulation. The psychopomp's job is to:

1. **Identify** the appropriate puppet for a problem
2. **Project** the problem into that puppet space
3. **Operate** within the puppet's native operations
4. **Extract** solutions back to the original domain

```python
class HolonicProjector:
    """
    Project problems between isomorphic structures.

    The psychopomp doesn't solve problems directly—
    it finds the space where the problem is easy.
    """

    def project(
        self,
        problem: Problem,
        source_puppet: Puppet,
        target_puppet: Puppet
    ) -> ProjectedProblem:
        """
        Map problem to isomorphic target space.

        If target_puppet makes the problem tractable,
        solve there and map solution back.
        """
        # Encode problem in target space
        encoded = target_puppet.encode(
            source_puppet.decode(problem)
        )

        return ProjectedProblem(
            original=problem,
            projected=encoded,
            projection=Projection(source_puppet, target_puppet)
        )

    def solve_and_extract(
        self,
        projected: ProjectedProblem
    ) -> Solution:
        """Solve in target space, extract to source space."""
        # Solve in projected space (may be easier)
        projected_solution = self.solve_in(
            projected.projected,
            projected.projection.target
        )

        # Map solution back
        return projected.projection.inverse().apply(projected_solution)
```

---

## The Four Paradigms

Ψ-gents synthesize four theoretical frameworks into a unified computational architecture:

| Paradigm | Core Concept | Agent Manifestation |
|----------|-------------|---------------------|
| **MHC** | Hierarchical Complexity | Stratified reasoning levels |
| **Jungian** | Shadow Integration | Bicameral generation + synthesis |
| **Lacanian** | RSI Borromean Knot | Three-register validation |
| **Metaethical** | Axiological Types | Value-typed operations |

---

## Paradigm 1: MHC (Model of Hierarchical Complexity)

> Every problem has a native complexity level. Operating at the wrong level wastes energy or misses nuance.

Michael Commons' MHC provides a **stratified complexity stack**—stages of cognitive complexity from concrete operations to meta-systematic reasoning.

### The Complexity Stack

```python
from enum import IntEnum

class MHCLevel(IntEnum):
    """
    Model of Hierarchical Complexity levels.

    Each level subsumes and operates on the level below.
    Like types: Level N operations take Level N-1 as operands.
    """
    SENSORIMOTOR = 0      # Direct perception/action
    CIRCULAR = 1          # Repeated patterns
    SENSORY_MOTOR = 2     # Coordinated perception/action
    NOMINAL = 3           # Named categories
    SENTENTIAL = 4        # Simple propositions
    PREOPERATIONAL = 5    # Single representations
    PRIMARY = 6           # Simple logical operations
    CONCRETE = 7          # Systematic operations on concretes
    ABSTRACT = 8          # Operations on abstractions
    FORMAL = 9            # Systematic logical reasoning
    SYSTEMATIC = 10       # Systems of formal operations
    METASYSTEMATIC = 11   # Operations on systems
    PARADIGMATIC = 12     # Operations across paradigms
    CROSS_PARADIGMATIC = 13  # Integration of paradigms

class MHCRouter(Agent[Task, MHCLevel]):
    """
    Route tasks to appropriate complexity level.

    The psychopomp's first job: identify the native
    complexity of a problem before attempting solution.
    """

    async def invoke(self, task: Task) -> MHCLevel:
        """
        Determine minimum complexity level required.

        Under-leveling: Miss nuance, oversimplify
        Over-leveling: Waste resources, overcomplicate
        """
        indicators = await self.analyze_complexity_indicators(task)

        return MHCLevel(
            self.compute_level(
                abstraction_depth=indicators.abstraction_layers,
                system_count=indicators.interacting_systems,
                paradigm_span=indicators.paradigms_involved,
                recursion_depth=indicators.self_reference_depth
            )
        )

    def compute_level(self, **indicators) -> int:
        """
        Heuristic level computation.

        - Single concrete object: CONCRETE (7)
        - Abstract concepts: ABSTRACT (8)
        - Logical proofs: FORMAL (9)
        - System design: SYSTEMATIC (10)
        - Architecture: METASYSTEMATIC (11)
        - Multi-paradigm integration: PARADIGMATIC (12)
        """
        max_indicator = max(
            indicators['abstraction_depth'],
            indicators['system_count'],
            indicators['paradigm_span'] + 10,
            indicators['recursion_depth'] + 8
        )
        return min(max_indicator, 13)  # Cap at CROSS_PARADIGMATIC
```

### Level-Appropriate Operations

```python
class MHCStratifiedAgent(Agent[Task, Result]):
    """
    Agent that operates at the appropriate MHC level.

    The key insight: Different levels require different
    cognitive operations. A FORMAL problem needs logic;
    a PARADIGMATIC problem needs synthesis.
    """

    def __init__(self):
        self.router = MHCRouter()
        self.level_agents: dict[MHCLevel, Agent] = {
            MHCLevel.CONCRETE: ConcreteOperator(),
            MHCLevel.ABSTRACT: AbstractReasoner(),
            MHCLevel.FORMAL: FormalLogician(),
            MHCLevel.SYSTEMATIC: SystemsAnalyzer(),
            MHCLevel.METASYSTEMATIC: Architect(),
            MHCLevel.PARADIGMATIC: ParadigmSynthesizer(),
            MHCLevel.CROSS_PARADIGMATIC: CrossParadigmIntegrator(),
        }

    async def invoke(self, task: Task) -> Result:
        # Route to appropriate level
        level = await self.router.invoke(task)

        # Get level-appropriate agent
        agent = self.level_agents.get(
            level,
            self.level_agents[MHCLevel.SYSTEMATIC]  # Default
        )

        # Execute at appropriate level
        return await agent.invoke(task)
```

### The Vertical Descent Pattern

```python
class VerticalDescent:
    """
    Descend through MHC levels to ground abstraction.

    High-level concepts must eventually connect to
    concrete operations. This pattern ensures grounding.
    """

    async def descend(
        self,
        concept: AbstractConcept,
        target_level: MHCLevel = MHCLevel.CONCRETE
    ) -> GroundedConcept:
        """
        Recursively descend from abstract to concrete.

        At each level, translate to lower-level operations
        until we reach the target grounding level.
        """
        current = concept
        current_level = self.assess_level(concept)

        descent_trace = []

        while current_level > target_level:
            # Translate to next lower level
            lower = await self.lower_one_level(current)
            descent_trace.append(DescentStep(
                from_level=current_level,
                to_level=current_level - 1,
                transformation=f"{current} → {lower}"
            ))

            current = lower
            current_level = current_level - 1

        return GroundedConcept(
            abstract=concept,
            grounded=current,
            descent_trace=descent_trace
        )
```

---

## Paradigm 2: Jungian Shadow Integration

> Every conscious position has an unconscious shadow. True synthesis requires engaging both.

Jung's shadow concept maps naturally to agent architecture: for any agent, there exists a **shadow agent** that embodies the repressed/opposite perspective.

### The Bicameral Agent

```python
@dataclass
class BicameralAgent(Agent[Task, SynthesizedResult]):
    """
    Agent with explicit shadow counterpart.

    The bicameral mind: Two voices that must be integrated.

    Ego: The conscious, articulated position
    Shadow: The unconscious, repressed counterposition
    """
    ego: Agent[Task, Position]
    shadow: Agent[Task, Position]  # Systematically inverted
    integrator: Agent[tuple[Position, Position], SynthesizedResult]

    async def invoke(self, task: Task) -> SynthesizedResult:
        # Generate both positions in parallel
        ego_position, shadow_position = await asyncio.gather(
            self.ego.invoke(task),
            self.shadow.invoke(task)
        )

        # Integrate the opposites
        return await self.integrator.invoke((ego_position, shadow_position))

class ShadowGenerator(Agent[Agent, Agent]):
    """
    Generate shadow counterpart for any agent.

    The shadow embodies:
    - Opposite conclusions
    - Repressed concerns
    - Hidden assumptions made explicit
    - The "yes, but..." voice
    """

    async def invoke(self, ego_agent: Agent) -> Agent:
        """
        Construct shadow agent.

        Techniques:
        1. Prompt inversion ("What's wrong with this?")
        2. Perspective flip (adversarial stance)
        3. Value inversion (prioritize what ego deprioritizes)
        """
        shadow_prompt = f"""
        You are the shadow of an agent whose purpose is:
        {ego_agent.purpose}

        Your role is to:
        1. Question every assumption the ego makes
        2. Voice concerns the ego ignores
        3. Represent the perspective the ego represses
        4. Find the flaw in every solution

        You are not destructive—you are necessary for completeness.
        The ego needs you to avoid blind spots.
        """

        return Agent(
            name=f"Shadow[{ego_agent.name}]",
            prompt=shadow_prompt,
            model=ego_agent.model
        )
```

### The Integration Loop

```python
class JungianIntegrationLoop:
    """
    The process of ego-shadow integration.

    Not compromise (averaging), but synthesis (transcendence).
    """

    async def integrate(
        self,
        ego_position: Position,
        shadow_position: Position
    ) -> IntegratedPosition:
        """
        Synthesize ego and shadow into higher unity.

        The Hegelian pattern applies:
        - Ego: Thesis
        - Shadow: Antithesis
        - Integration: Synthesis
        """
        # Identify the core tension
        tension = await self.identify_tension(ego_position, shadow_position)

        # Find the higher ground that honors both
        synthesis = await self.synthesize(
            ego=ego_position,
            shadow=shadow_position,
            tension=tension
        )

        # Verify integration quality
        integration_score = await self.assess_integration(
            synthesis,
            ego_honors=self.honors_ego(synthesis, ego_position),
            shadow_honors=self.honors_shadow(synthesis, shadow_position),
            transcends=self.transcends_both(synthesis, ego_position, shadow_position)
        )

        return IntegratedPosition(
            content=synthesis,
            ego_contribution=ego_position,
            shadow_contribution=shadow_position,
            tension_resolved=tension,
            integration_score=integration_score
        )

    async def honors_ego(self, synthesis: Position, ego: Position) -> float:
        """Does synthesis preserve ego's valid concerns?"""
        ...

    async def honors_shadow(self, synthesis: Position, shadow: Position) -> float:
        """Does synthesis address shadow's critiques?"""
        ...

    async def transcends_both(
        self,
        synthesis: Position,
        ego: Position,
        shadow: Position
    ) -> float:
        """Does synthesis go beyond mere averaging?"""
        ...
```

### The Shadow Integration Cycle

```
┌─────────────────────────────────────────────────────────┐
│                SHADOW INTEGRATION CYCLE                  │
│                                                          │
│    ┌──────────┐                    ┌──────────┐         │
│    │   EGO    │ ──── TENSION ────→ │  SHADOW  │         │
│    │ position │                    │ position │         │
│    └────┬─────┘                    └────┬─────┘         │
│         │                               │               │
│         │         ┌──────────┐          │               │
│         └────────→│ INTEGRA- │←─────────┘               │
│                   │   TOR    │                          │
│                   └────┬─────┘                          │
│                        │                                │
│                        ▼                                │
│                 ┌──────────┐                            │
│                 │SYNTHESIS │                            │
│                 │(new ego) │                            │
│                 └────┬─────┘                            │
│                      │                                  │
│                      │ (becomes input to next cycle)    │
│                      └──────────────────────────────────┘
└─────────────────────────────────────────────────────────┘
```

---

## Paradigm 3: Lacanian RSI (Real, Symbolic, Imaginary)

> The three registers form a Borromean knot—cut any one, and all three fall apart.

Lacan's topology maps directly to agent validation:

| Register | Domain | Agent Validation |
|----------|--------|------------------|
| **Symbolic** | Code, schemas, types | Does it type-check? Does it parse? |
| **Real** | Execution, physics | Does it run? Does it terminate? |
| **Imaginary** | Perception, aesthetics | Does it look right? Does it feel right? |

### The Borromean Knot

```python
@dataclass
class BorromeanKnot:
    """
    The three registers that must all hold for validity.

    Like the Borromean rings: Remove any one, all three fall apart.
    An agent that types-checks (Symbolic) but crashes (Real) is invalid.
    An agent that runs (Real) but outputs nonsense (Imaginary) is invalid.
    """
    symbolic: SymbolicHealth
    real: RealHealth
    imaginary: ImaginaryHealth

    @property
    def knot_intact(self) -> bool:
        """All three registers must hold."""
        return (
            self.symbolic.valid and
            self.real.valid and
            self.imaginary.valid
        )

    @property
    def weakest_ring(self) -> str:
        """Which register is closest to failure?"""
        scores = {
            "symbolic": self.symbolic.score,
            "real": self.real.score,
            "imaginary": self.imaginary.score
        }
        return min(scores, key=scores.get)

class BorromeanValidator(Agent[AgentOutput, BorromeanKnot]):
    """
    Validate output across all three registers.

    This is the psychopomp's quality gate:
    Only outputs that satisfy all three registers pass.
    """

    async def invoke(self, output: AgentOutput) -> BorromeanKnot:
        # Validate in parallel across registers
        symbolic, real, imaginary = await asyncio.gather(
            self.validate_symbolic(output),
            self.validate_real(output),
            self.validate_imaginary(output)
        )

        return BorromeanKnot(
            symbolic=symbolic,
            real=real,
            imaginary=imaginary
        )

    async def validate_symbolic(self, output: AgentOutput) -> SymbolicHealth:
        """
        Symbolic register: Does it satisfy formal constraints?

        - Schema validation
        - Type checking
        - Syntax correctness
        - Contract satisfaction
        """
        return SymbolicHealth(
            schema_valid=await self.check_schema(output),
            type_check_pass=await self.type_check(output),
            syntax_correct=await self.syntax_check(output),
            contracts_satisfied=await self.verify_contracts(output)
        )

    async def validate_real(self, output: AgentOutput) -> RealHealth:
        """
        Real register: Does it work in reality?

        - Execution without error
        - Termination within budget
        - Resource bounds respected
        - Side effects contained
        """
        return RealHealth(
            executes=await self.test_execution(output),
            terminates=await self.check_termination(output),
            memory_bounded=await self.check_memory(output),
            effects_contained=await self.verify_effects(output)
        )

    async def validate_imaginary(self, output: AgentOutput) -> ImaginaryHealth:
        """
        Imaginary register: Does it appear correct?

        - Visual coherence (if rendered)
        - Semantic plausibility
        - User perceivability
        - Aesthetic alignment
        """
        rendered = await self.render(output) if output.renderable else None

        return ImaginaryHealth(
            visually_coherent=await self.vision_check(rendered),
            semantically_plausible=await self.semantic_check(output),
            user_perceivable=await self.accessibility_check(rendered),
            aesthetically_aligned=await self.aesthetic_check(output)
        )
```

### The Hallucination Detector

Most LLM hallucinations occur when the agent operates **only in the Symbolic**—generating text that parses but doesn't ground in Real or align with Imaginary.

```python
class HallucinationDetector:
    """
    Detect hallucinations via register mismatch.

    Hallucination signature:
    - Symbolic: PASS (it parses, it type-checks)
    - Real: FAIL (can't execute, doesn't exist)
    - Imaginary: AMBIGUOUS (looks plausible but...)
    """

    async def detect(self, output: AgentOutput) -> HallucinationReport:
        knot = await self.validator.invoke(output)

        # Classic hallucination: Symbolic OK, Real FAIL
        if knot.symbolic.valid and not knot.real.valid:
            return HallucinationReport(
                is_hallucination=True,
                type="symbolic_real_mismatch",
                explanation="Output is syntactically valid but doesn't ground in reality",
                confidence=0.9
            )

        # Subtle hallucination: All pass but Imaginary is suspicious
        if knot.knot_intact and knot.imaginary.score < 0.5:
            return HallucinationReport(
                is_hallucination=True,
                type="imaginary_suspicion",
                explanation="Output passes formal checks but appears semantically implausible",
                confidence=0.6
            )

        return HallucinationReport(is_hallucination=False)
```

---

## Paradigm 4: Axiological Type Theory (Metaethics)

> Values have types. Operations must respect value-type constraints.

Extending type theory to values: operations that combine incompatible value types are **type errors**.

### The Value Type System

```python
from enum import Enum
from typing import TypeVar

class ValueDomain(Enum):
    """
    Domains of value (orthogonal dimensions).

    Values in different domains cannot be directly compared—
    they require explicit conversion (valuation morphism).
    """
    EPISTEMIC = "truth"      # Knowledge, belief, certainty
    AESTHETIC = "beauty"     # Form, elegance, harmony
    ETHICAL = "good"         # Right action, welfare, justice
    PRAGMATIC = "utility"    # Effectiveness, efficiency, success
    HEDONIC = "pleasure"     # Enjoyment, satisfaction, comfort

V = TypeVar("V", bound="Value")

@dataclass
class Value(Generic[V]):
    """
    A typed value in the axiological system.

    Values have:
    - Domain: Which dimension of value
    - Magnitude: How much (within domain)
    - Polarity: Positive or negative valence
    """
    domain: ValueDomain
    magnitude: float  # 0.0 - 1.0 within domain
    polarity: Literal["positive", "negative"]

    def __add__(self, other: "Value") -> "Value":
        """
        Combine values.

        Same domain: Add magnitudes
        Different domains: Type error (need explicit conversion)
        """
        if self.domain != other.domain:
            raise ValueTypeError(
                f"Cannot combine {self.domain} and {other.domain} values directly. "
                f"Use a ValuationMorphism to convert."
            )

        return Value(
            domain=self.domain,
            magnitude=min(1.0, self.magnitude + other.magnitude),
            polarity=self._combine_polarity(self.polarity, other.polarity)
        )

class ValuationMorphism:
    """
    Convert values between domains.

    Like type coercion, but for values.
    Every conversion has a cost (information loss).
    """

    def __init__(self, source: ValueDomain, target: ValueDomain):
        self.source = source
        self.target = target
        self.conversion_loss = self._compute_loss(source, target)

    def convert(self, value: Value) -> Value:
        """Convert value to target domain with loss."""
        if value.domain != self.source:
            raise ValueTypeError(f"Expected {self.source}, got {value.domain}")

        return Value(
            domain=self.target,
            magnitude=value.magnitude * (1 - self.conversion_loss),
            polarity=value.polarity
        )

    def _compute_loss(self, source: ValueDomain, target: ValueDomain) -> float:
        """
        Conversion loss heuristics.

        Some conversions are "cheap" (low loss):
        - PRAGMATIC → EPISTEMIC (utility grounds in truth)

        Some are "expensive" (high loss):
        - AESTHETIC → ETHICAL (beauty doesn't imply goodness)
        """
        loss_matrix = {
            (ValueDomain.PRAGMATIC, ValueDomain.EPISTEMIC): 0.1,
            (ValueDomain.EPISTEMIC, ValueDomain.PRAGMATIC): 0.2,
            (ValueDomain.AESTHETIC, ValueDomain.ETHICAL): 0.5,
            (ValueDomain.ETHICAL, ValueDomain.AESTHETIC): 0.5,
            (ValueDomain.HEDONIC, ValueDomain.ETHICAL): 0.4,
            # ... etc
        }
        return loss_matrix.get((source, target), 0.3)  # Default moderate loss
```

### Value-Typed Agent Operations

```python
class AxiologicalAgent(Agent[Task, ValuedResult]):
    """
    Agent that tracks value implications of operations.

    Every operation has value consequences:
    - What epistemic value does this add?
    - What ethical constraints apply?
    - What aesthetic considerations matter?
    """

    async def invoke(self, task: Task) -> ValuedResult:
        # Execute core operation
        result = await self.core_agent.invoke(task)

        # Compute value implications
        values = await self.compute_value_implications(task, result)

        # Check for value-type violations
        violations = self.check_value_type_constraints(values)

        if violations:
            # Cannot proceed with type violations
            return ValuedResult(
                result=None,
                values=values,
                violations=violations,
                valid=False
            )

        return ValuedResult(
            result=result,
            values=values,
            violations=[],
            valid=True
        )

    async def compute_value_implications(
        self,
        task: Task,
        result: Any
    ) -> dict[ValueDomain, Value]:
        """
        Assess value implications across all domains.

        "What is the truth value of this result?"
        "What is the ethical standing of this action?"
        "What is the aesthetic quality of this output?"
        """
        return {
            ValueDomain.EPISTEMIC: await self.assess_epistemic(task, result),
            ValueDomain.ETHICAL: await self.assess_ethical(task, result),
            ValueDomain.AESTHETIC: await self.assess_aesthetic(task, result),
            ValueDomain.PRAGMATIC: await self.assess_pragmatic(task, result),
        }
```

---

## The Grand Synthesis: Psychopomp Architecture

The Ψ-gent integrates all four paradigms into a unified architecture:

```
┌────────────────────────────────────────────────────────────────────┐
│                    Ψ-GENT PSYCHOPOMP ARCHITECTURE                   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     MHC ROUTER                               │   │
│  │  Task → Complexity Level → Level-Appropriate Agent          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  BICAMERAL GENERATOR                         │   │
│  │  ┌──────────┐              ┌──────────┐                     │   │
│  │  │   EGO    │◄── Tension ─►│  SHADOW  │                     │   │
│  │  └────┬─────┘              └────┬─────┘                     │   │
│  │       └──────────┬──────────────┘                           │   │
│  │                  ▼                                          │   │
│  │           ┌──────────┐                                      │   │
│  │           │SYNTHESIS │                                      │   │
│  │           └──────────┘                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 BORROMEAN VALIDATOR                          │   │
│  │        ┌───────────────────────────────────┐                │   │
│  │        │         ╱  Symbolic  ╲            │                │   │
│  │        │        ╱      ◯       ╲           │                │   │
│  │        │   Real ◯───────────◯ Imaginary    │                │   │
│  │        │         ╲     ◯     ╱             │                │   │
│  │        │          ╲         ╱              │                │   │
│  │        └───────────────────────────────────┘                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │               AXIOLOGICAL TYPE CHECKER                       │   │
│  │  ValuedResult → Type Check → Pass/Violation                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│                         FINAL OUTPUT                                │
│                    (Multi-dimensionally validated)                  │
└────────────────────────────────────────────────────────────────────┘
```

### The Psychopomp Agent

```python
class PsychopompAgent(Agent[Task, PsychopompResult]):
    """
    The unified Ψ-gent that integrates all paradigms.

    The psychopomp guides the task through:
    1. MHC routing (right level)
    2. Bicameral generation (ego + shadow)
    3. Borromean validation (RSI)
    4. Axiological typing (value check)
    """

    def __init__(self):
        self.mhc_router = MHCRouter()
        self.bicameral = BicameralAgent(
            ego=EgoAgent(),
            shadow=ShadowAgent(),
            integrator=IntegrationAgent()
        )
        self.borromean = BorromeanValidator()
        self.axiological = AxiologicalAgent()

    async def invoke(self, task: Task) -> PsychopompResult:
        # 1. Route to appropriate complexity level
        level = await self.mhc_router.invoke(task)
        leveled_task = task.with_level(level)

        # 2. Generate via bicameral process
        synthesis = await self.bicameral.invoke(leveled_task)

        # 3. Validate across Borromean registers
        knot = await self.borromean.invoke(synthesis)

        if not knot.knot_intact:
            return PsychopompResult(
                success=False,
                failure_register=knot.weakest_ring,
                partial_result=synthesis
            )

        # 4. Type-check axiological implications
        valued = await self.axiological.invoke(
            Task(content=synthesis, context=task)
        )

        if not valued.valid:
            return PsychopompResult(
                success=False,
                value_violations=valued.violations,
                partial_result=synthesis
            )

        return PsychopompResult(
            success=True,
            result=synthesis,
            mhc_level=level,
            borromean_health=knot,
            value_profile=valued.values
        )
```

---

## Ψ-gent Types

| Agent | Paradigm | Purpose |
|-------|----------|---------|
| `MHCRouter` | MHC | Route tasks to appropriate complexity level |
| `MHCStratifiedAgent` | MHC | Execute at level-appropriate abstraction |
| `VerticalDescent` | MHC | Ground abstractions to concrete operations |
| `BicameralAgent` | Jungian | Generate ego + shadow positions |
| `ShadowGenerator` | Jungian | Construct shadow counterpart for any agent |
| `JungianIntegrationLoop` | Jungian | Synthesize ego and shadow |
| `BorromeanValidator` | Lacanian | Validate across RSI registers |
| `HallucinationDetector` | Lacanian | Detect register mismatches |
| `AxiologicalAgent` | Metaethical | Track value-type implications |
| `ValuationMorphism` | Metaethical | Convert between value domains |
| `PsychopompAgent` | Synthesis | Full pipeline integration |
| `HolonicProjector` | Foundation | Project problems between puppet spaces |

---

## Integration with Other Genuses

| Integration | Purpose |
|-------------|---------|
| Ψ + O | O-gent observes Ψ-gent's register transitions |
| Ψ + N | N-gent narrates the ego-shadow integration journey |
| Ψ + J | J-gent lazily instantiates level-appropriate agents |
| Ψ + H | H-gent provides dialectical substrate for synthesis |
| Ψ + T | T-gent tests Borromean invariants |
| Ψ + B | B-gent grounds Ψ in resource constraints |

---

## Anti-Patterns

- **Level collapse**: Treating all problems at the same MHC level
- **Shadow suppression**: Ignoring or dismissing shadow positions
- **Mono-register thinking**: Validating only Symbolic (code compiles!) without Real/Imaginary
- **Value blindness**: Ignoring axiological implications of operations
- **Puppet lock-in**: Forgetting that the puppet is not the concept
- **Integration bypass**: Jumping to synthesis without honoring both positions

---

## The Psychopomp's Journey

```
The user brings a task
    │
    ▼
The MHC Router assesses: "This is METASYSTEMATIC—
it involves operations on systems themselves."
    │
    ▼
The Bicameral Agent generates:
  EGO: "The optimal architecture is X because..."
  SHADOW: "But what about edge case Y? And assumption Z is hidden..."
    │
    ▼
The Integrator synthesizes:
  "Architecture X, modified to handle Y, with Z made explicit..."
    │
    ▼
The Borromean Validator checks:
  SYMBOLIC: ✓ (schema valid, types check)
  REAL: ✓ (executes within budget)
  IMAGINARY: ✓ (renders correctly, semantically plausible)
    │
    ▼
The Axiological Checker verifies:
  EPISTEMIC: 0.8 (high truth value)
  ETHICAL: 0.9 (respects constraints)
  AESTHETIC: 0.7 (reasonably elegant)
  PRAGMATIC: 0.85 (effective for purpose)
    │
    ▼
The Psychopomp delivers the result,
carrying the soul of the task safely across all registers.
```

---

*Zen Principle: The guide who knows all paths still asks which one you wish to walk.*

---

## See Also

- [principles.md](../principles.md) - Puppet Constructions, Personality Space
- [h-gents/](../h-gents/) - Hegelian dialectics (thesis/antithesis/synthesis)
- [o-gents/](../o-gents/) - Borromean Observer
- [bootstrap.md](../bootstrap.md) - Judge, Contradict, Sublate (related operations)
