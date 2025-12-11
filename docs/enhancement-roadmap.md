# Enhancement Roadmap: Toward Mathematical Coherence

**Status**: Proposal | **Date**: 2025-12-10
**Philosophy**: The system that aspires to enlightenment must formalize its intuitions.

---

## Overview

This document captures ten enhancement proposals to deepen kgents' philosophical and mathematical foundations. The current system (6,777+ tests, 14 agent genera, AGENTESE protocol) is already uncommonly rigorous. These proposals push toward *provable coherence*.

---

## 1. Y-gents: The Yoneda Perspective Layer

### The Gap

AGENTESE establishes "no view from nowhere"—observation is always perspectival. But the system lacks **inter-agent perspectival modeling**. Category theory provides the tool: the Yoneda lemma.

### The Yoneda Insight

An object is fully characterized by how all other objects relate to it:

```
Y(A) = Hom(_, A)
```

For agents: An agent is fully characterized by how all other agents perceive/interact with it.

### Proposed Implementation

```python
@dataclass
class YgentEmbedding:
    """
    Yoneda embedding of an agent.

    The agent A is represented by the functor Hom(_, A):
    for each agent B, we get the set of morphisms B → A.
    """
    target: Agent
    perspective_map: dict[str, list[Morphism]]  # agent_id → morphisms to target

    def how_does(self, observer_id: str) -> list[Affordance]:
        """What affordances does observer have toward target?"""
        return [m.affordance for m in self.perspective_map.get(observer_id, [])]

    def consensus_view(self) -> AgentProfile:
        """Aggregate all perspectives into consensus."""
        # The "social" identity of the agent
        ...


class Ygent:
    """
    Yoneda Agent: Computes how agents see each other.

    Use cases:
    - "What would B-gent think of this M-gent decision?"
    - "How does the system collectively perceive K-gent?"
    - Multi-agent deliberation with perspective-taking
    """

    async def embed(self, agent: Agent) -> YgentEmbedding:
        """Compute Yoneda embedding of agent."""
        perspectives = {}
        for other in self.registry.all_agents():
            morphisms = await self._compute_morphisms(other, agent)
            perspectives[other.id] = morphisms
        return YgentEmbedding(target=agent, perspective_map=perspectives)

    async def perspective_of(self, observer: Agent, target: Agent) -> Perspective:
        """How does observer see target?"""
        # Returns observer's specific view, not "objective" description
        ...
```

### Category Theory Grounding

The Yoneda lemma states: `Nat(Hom(_, A), F) ≅ F(A)`

For kgents: Natural transformations from an agent's perspective-functor to any other functor are equivalent to applying that functor to the agent. This means **perspective IS identity**—there's no agent "behind" the perspectives.

### Integration Points

| Existing System | Y-gent Enhancement |
|-----------------|-------------------|
| AGENTESE `manifest` | Returns Y-gent filtered view |
| H-gent dialectics | Thesis/antithesis as different Y-perspectives |
| O-gent observation | Collects raw data for Y-embeddings |
| K-gent personalization | K navigates Y-embedding space |

---

## 2. Active Inference Formalization

### The Gap

Synapse uses "surprise thresholds" (`flashbulb_threshold=0.9`) but the mathematics is informal. Karl Friston's Free Energy Principle provides the rigorous foundation.

### The Free Energy Principle

Agents minimize free energy: `F = E_q[log q(s) - log p(o,s)]`

- **q(s)**: Agent's beliefs about world state
- **p(o,s)**: Generative model (how states produce observations)
- **Minimizing F**: Reduces prediction error OR reduces model complexity

### Mapping to kgents

| Free Energy Component | kgents Component |
|----------------------|------------------|
| Generative model p(o,s) | D-gent memory (beliefs about world) |
| Variational density q(s) | Current agent state |
| Prediction error | Synapse surprise signal |
| Model complexity | B-gent token budget |
| Active inference | E-gent evolution (changing the world to match predictions) |

### Proposed Implementation

```python
@dataclass
class FreeEnergyMetrics:
    """Active inference metrics for an agent."""
    prediction_error: float      # Surprise from observations
    model_complexity: float      # KL divergence from prior
    free_energy: float           # prediction_error + model_complexity
    expected_free_energy: float  # For action selection


class ActiveInferenceEngine:
    """
    Wraps any agent in active inference framework.

    The agent's actions are selected to minimize expected free energy:
    - Epistemic value: Actions that reduce uncertainty
    - Pragmatic value: Actions that achieve goals
    """

    def __init__(self, agent: Agent, generative_model: DgentMemory):
        self.agent = agent
        self.model = generative_model

    async def select_action(self, observation: Any) -> Action:
        """Select action minimizing expected free energy."""
        # 1. Update beliefs given observation
        posterior = await self._variational_update(observation)

        # 2. Enumerate possible actions
        actions = await self.agent.affordances()

        # 3. For each action, compute expected free energy
        efes = []
        for action in actions:
            efe = await self._expected_free_energy(action, posterior)
            efes.append((action, efe))

        # 4. Select action with lowest EFE (softmax for exploration)
        return self._softmax_select(efes, temperature=self.exploration_rate)

    async def _expected_free_energy(self, action: Action, beliefs: Distribution) -> float:
        """
        G = E_q[log q(s') - log p(o',s') + log p(o'|C)]

        Where C is the agent's preferences (goals).
        """
        ...
```

### The Accursed Share as Exploration Bonus

In active inference, exploration is driven by epistemic value—actions that reduce uncertainty. The Accursed Share can be formalized:

```python
def accursed_share_bonus(self, action: Action, beliefs: Distribution) -> float:
    """
    The Accursed Share is surplus energy that MUST be spent.
    In active inference terms: mandatory exploration budget.

    This prevents over-exploitation and maintains system anti-fragility.
    """
    information_gain = self._expected_information_gain(action, beliefs)

    # Force minimum exploration regardless of pragmatic value
    return max(information_gain, self.minimum_accursed_tithe)
```

---

## 3. Borromean Integrity Constraint

### The Gap

H-lacan references Real/Symbolic/Imaginary but doesn't enforce their topological linkage. In Lacan, the three registers form a Borromean knot—remove any one and the others fall apart.

### The Borromean Structure

```
        Real
         /\
        /  \
       /    \
      /      \
Symbolic ---- Imaginary

Remove any ring → the other two separate
```

### Proposed Implementation

```python
from enum import Enum
from dataclasses import dataclass

class Register(Enum):
    REAL = "real"           # Grounding in world, consequences, impossibility
    SYMBOLIC = "symbolic"   # Structure, language, law, difference
    IMAGINARY = "imaginary" # Identity, wholeness, image, ego


@dataclass
class BorromeanAnalysis:
    """Analysis of an output across the three registers."""
    real_grounding: float       # 0-1: How grounded in world/action?
    symbolic_structure: float   # 0-1: How well-formed logically?
    imaginary_coherence: float  # 0-1: How coherent as identity/narrative?

    @property
    def is_integrated(self) -> bool:
        """All three registers must be present above threshold."""
        threshold = 0.3
        return all([
            self.real_grounding > threshold,
            self.symbolic_structure > threshold,
            self.imaginary_coherence > threshold,
        ])

    @property
    def dominant_register(self) -> Register:
        """Which register dominates (potential imbalance signal)?"""
        scores = {
            Register.REAL: self.real_grounding,
            Register.SYMBOLIC: self.symbolic_structure,
            Register.IMAGINARY: self.imaginary_coherence,
        }
        return max(scores, key=scores.get)

    @property
    def missing_register(self) -> Register | None:
        """Which register is dangerously low?"""
        threshold = 0.2
        if self.real_grounding < threshold:
            return Register.REAL
        if self.symbolic_structure < threshold:
            return Register.SYMBOLIC
        if self.imaginary_coherence < threshold:
            return Register.IMAGINARY
        return None


class BorromeanGuard:
    """
    Interceptor that checks Borromean integrity of agent outputs.

    If a register is missing, the output is flagged for remediation:
    - Missing Real: Output is ungrounded fantasy
    - Missing Symbolic: Output is incoherent noise
    - Missing Imaginary: Output lacks identity/purpose
    """

    async def check(self, output: AgentOutput) -> BorromeanAnalysis:
        """Analyze output across three registers."""
        return BorromeanAnalysis(
            real_grounding=await self._assess_real(output),
            symbolic_structure=await self._assess_symbolic(output),
            imaginary_coherence=await self._assess_imaginary(output),
        )

    async def _assess_real(self, output: AgentOutput) -> float:
        """
        Real register: Grounding in world.

        Indicators:
        - References to concrete actions/consequences
        - Acknowledgment of impossibility/limits
        - Connection to external reality
        """
        ...

    async def _assess_symbolic(self, output: AgentOutput) -> float:
        """
        Symbolic register: Logical structure.

        Indicators:
        - Grammatical well-formedness
        - Logical consistency
        - Proper use of distinctions/categories
        """
        ...

    async def _assess_imaginary(self, output: AgentOutput) -> float:
        """
        Imaginary register: Identity coherence.

        Indicators:
        - Consistent voice/persona
        - Narrative coherence
        - Self-model consistency
        """
        ...
```

### Integration with H-gents

```python
class HlacanEnhanced(Hlacan):
    """H-lacan with Borromean integrity enforcement."""

    async def invoke(self, input: HlacanInput) -> HlacanOutput:
        output = await super().invoke(input)

        # Check Borromean integrity
        analysis = await self.borromean_guard.check(output)

        if not analysis.is_integrated:
            missing = analysis.missing_register
            output = await self._remediate(output, missing)

        return output.with_borromean_analysis(analysis)
```

---

## 4. Kairos: Opportune Timing Protocol

### The Gap

`time.schedule.defer` handles chronological scheduling but misses **kairos**—the opportune moment. Greeks distinguished:

- **Chronos**: Sequential, quantitative time
- **Kairos**: Qualitative, opportune time

### Proposed Implementation

```python
@dataclass
class KairosCondition:
    """A condition for opportune timing."""
    predicate: str              # e.g., "user_frustration < 0.3"
    timeout: timedelta | None   # Maximum wait before forcing
    priority: int               # Higher = more urgent

    async def is_satisfied(self, context: Context) -> bool:
        """Evaluate predicate against current context."""
        ...


@dataclass
class KairosWaiter:
    """
    Waits for the opportune moment, not just the scheduled time.

    The right time is when:
    1. Conditions are met (readiness)
    2. OR timeout expires (deadline)
    3. AND no higher-priority kairos is pending
    """
    conditions: list[KairosCondition]
    action: Callable

    async def await_kairos(self, context_stream: AsyncIterator[Context]) -> Any:
        """Wait for opportune moment, then execute action."""
        async for context in context_stream:
            for condition in self.conditions:
                if await condition.is_satisfied(context):
                    return await self.action(context)
                if condition.timeout and self._timeout_expired(condition):
                    return await self.action(context)  # Force execution

        raise KairosTimeout("No opportune moment found")


class TimeKairosContext:
    """AGENTESE time.kairos.* context implementation."""

    async def when(
        self,
        observer: Umwelt,
        condition: str,
        timeout: timedelta | None = None,
    ) -> KairosWaiter:
        """
        Wait for opportune moment.

        Example:
            await logos.invoke("time.kairos.when", observer,
                condition="user_frustration < 0.3 AND context_loaded",
                timeout=timedelta(minutes=5))
        """
        parsed = self._parse_condition(condition)
        return KairosWaiter(
            conditions=[KairosCondition(predicate=parsed, timeout=timeout, priority=1)],
            action=lambda ctx: ctx,  # Returns context when ready
        )

    async def sense(self, observer: Umwelt) -> KairosReading:
        """
        Sense the current kairos—is now a good time?

        Returns readiness indicators across multiple dimensions.
        """
        return KairosReading(
            user_state=await self._sense_user(observer),
            system_load=await self._sense_system(),
            context_readiness=await self._sense_context(observer),
            recommendation=self._compute_recommendation(),
        )
```

### Integration with Semantic Field

Kairos can emit/sense pheromones:

```python
class KairosEmitter(SemanticFieldEmitter):
    """Emits KAIROS pheromones when opportune moments arise."""

    async def emit_opportunity(self, domain: str, readiness: float):
        """Signal that now is a good time for domain-specific action."""
        await self.field.emit(Pheromone(
            type=PheromoneType.KAIROS,
            domain=domain,
            strength=readiness,
            decay_rate=0.9,  # Kairos is fleeting
        ))
```

---

## 5. E-gent Fitness Landscape

### The Gap

E-gents do "teleological thermodynamics" but lack explicit fitness functions. Evolution without selection pressure is genetic drift.

### Multi-Level Fitness

```python
@dataclass
class FitnessLandscape:
    """
    Multi-level fitness function for E-gent evolution.

    Three levels, hierarchically constrained:
    1. Local: Task completion (immediate utility)
    2. Global: Composability preservation (system integrity)
    3. Meta: User joy (ultimate purpose)
    """

    async def evaluate(self, agent: Agent, context: EvolutionContext) -> FitnessScore:
        local = await self._local_fitness(agent, context)
        global_ = await self._global_fitness(agent, context)
        meta = await self._meta_fitness(agent, context)

        # Hierarchical constraint: higher levels gate lower
        if global_ < self.composability_threshold:
            # Agent breaks composition → fitness capped
            return FitnessScore(
                local=local * 0.1,  # Heavily penalized
                global_=global_,
                meta=0.0,
                total=global_ * 0.1,
                violation="COMPOSABILITY_BREACH",
            )

        if meta < self.joy_threshold:
            # Agent works but isn't joyful → moderate penalty
            return FitnessScore(
                local=local * 0.7,
                global_=global_,
                meta=meta,
                total=(local * 0.3 + global_ * 0.3 + meta * 0.4),
                violation="JOY_DEFICIT",
            )

        return FitnessScore(
            local=local,
            global_=global_,
            meta=meta,
            total=(local * 0.3 + global_ * 0.3 + meta * 0.4),
        )

    async def _local_fitness(self, agent: Agent, context: EvolutionContext) -> float:
        """Task completion metrics from O-gent."""
        metrics = await self.observer.get_metrics(agent.id)
        return (
            metrics.success_rate * 0.4 +
            metrics.latency_score * 0.3 +
            metrics.resource_efficiency * 0.3
        )

    async def _global_fitness(self, agent: Agent, context: EvolutionContext) -> float:
        """Category law verification from BootstrapWitness."""
        laws = await self.witness.verify_laws(agent)
        return (
            laws.identity_score * 0.5 +
            laws.associativity_score * 0.5
        )

    async def _meta_fitness(self, agent: Agent, context: EvolutionContext) -> float:
        """User joy signals from K-gent satisfaction tracking."""
        joy = await self.kgent.get_satisfaction(agent.id)
        return joy.score
```

### Selection Mechanisms

```python
class EvolutionarySelector:
    """Selection mechanisms for E-gent evolution."""

    async def tournament_select(
        self,
        population: list[Agent],
        landscape: FitnessLandscape,
        tournament_size: int = 3,
    ) -> Agent:
        """Tournament selection: pick best from random sample."""
        candidates = random.sample(population, tournament_size)
        scores = [(a, await landscape.evaluate(a)) for a in candidates]
        return max(scores, key=lambda x: x[1].total)[0]

    async def roulette_select(
        self,
        population: list[Agent],
        landscape: FitnessLandscape,
    ) -> Agent:
        """Fitness-proportionate selection."""
        scores = [(a, await landscape.evaluate(a)) for a in population]
        total = sum(s.total for _, s in scores)
        r = random.uniform(0, total)
        cumulative = 0
        for agent, score in scores:
            cumulative += score.total
            if cumulative >= r:
                return agent
        return scores[-1][0]
```

---

## 6. R-gent Automated Spec Refinement

### The Gap

Spec → Impl is generative, but Impl → Spec feedback is manual (editing HYDRATE.md).

### Proposed Implementation

```python
class SpecRefinementAgent:
    """
    R-gent extension: Proposes spec amendments based on impl patterns.

    The feedback loop:
    1. Observe successful test patterns
    2. Identify implicit contracts not in spec
    3. Propose spec amendments
    4. Human approves/rejects
    """

    async def analyze_test_patterns(self, test_results: list[TestResult]) -> list[Pattern]:
        """Extract patterns from successful tests."""
        patterns = []
        for result in test_results:
            if result.passed:
                pattern = await self._extract_pattern(result)
                if pattern.confidence > 0.8:
                    patterns.append(pattern)
        return patterns

    async def propose_spec_amendment(self, pattern: Pattern) -> SpecAmendment:
        """Generate spec amendment from observed pattern."""
        return SpecAmendment(
            target_spec=pattern.relevant_spec,
            section=pattern.relevant_section,
            current_text=await self._get_current_spec_text(pattern),
            proposed_text=await self._generate_amendment(pattern),
            rationale=pattern.rationale,
            confidence=pattern.confidence,
            evidence=pattern.supporting_tests,
        )

    async def detect_spec_ambiguity(self, failure: TestFailure) -> SpecIssue | None:
        """Detect if failure reveals spec ambiguity."""
        # Analyze failure to see if it's impl bug or spec gap
        analysis = await self._analyze_failure(failure)

        if analysis.cause == FailureCause.SPEC_AMBIGUITY:
            return SpecIssue(
                spec_file=analysis.relevant_spec,
                ambiguous_section=analysis.section,
                interpretation_a=analysis.impl_interpretation,
                interpretation_b=analysis.test_interpretation,
                suggested_clarification=analysis.suggested_fix,
            )

        return None


@dataclass
class SpecAmendment:
    """A proposed amendment to a specification."""
    target_spec: Path
    section: str
    current_text: str
    proposed_text: str
    rationale: str
    confidence: float
    evidence: list[str]  # Test names that support this
    status: Literal["proposed", "approved", "rejected"] = "proposed"
```

### Integration with CI

```yaml
# .github/workflows/spec-refinement.yml
name: Spec Refinement
on:
  push:
    paths:
      - 'impl/**/*.py'
      - 'impl/**/*_test.py'

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - name: Analyze test patterns
        run: |
          python -m kgents.rgent.analyze_patterns \
            --since="${{ github.event.before }}" \
            --output=.kgents/ghost/spec_proposals.jsonl

      - name: Create spec issues
        if: steps.analyze.outputs.proposals > 0
        run: |
          python -m kgents.rgent.create_issues \
            --input=.kgents/ghost/spec_proposals.jsonl
```

---

## 7. Swarm Intelligence Patterns

### The Gap

Agents compose but don't truly deliberate. SemanticField pheromones are the seed for stigmergic coordination.

### Proposed Implementation

```python
class SwarmDeliberation:
    """
    Multi-agent deliberation without central orchestrator.

    Patterns:
    1. Stigmergic consensus: Agents modify shared environment
    2. Dialectic voting: H-gent synthesizes positions
    3. Emergent coordination: Patterns arise from local rules
    """

    async def stigmergic_consensus(
        self,
        question: str,
        participants: list[Agent],
        field: SemanticField,
        rounds: int = 5,
    ) -> Consensus:
        """
        Reach consensus through environment modification.

        Each agent:
        1. Senses current pheromone state
        2. Deposits own position as pheromone
        3. Adjusts position based on gradient

        Consensus emerges when pheromone field stabilizes.
        """
        for round in range(rounds):
            for agent in participants:
                # Sense current state
                local_field = await field.sense(agent.position)

                # Generate position
                position = await agent.invoke(question, context=local_field)

                # Deposit pheromone
                await field.emit(Pheromone(
                    type=PheromoneType.OPINION,
                    content=position,
                    strength=agent.confidence,
                    position=agent.position,
                ))

            # Check for convergence
            if await self._has_converged(field):
                break

        return await self._extract_consensus(field)

    async def dialectic_vote(
        self,
        positions: list[Position],
        synthesizer: Hgent,
    ) -> Synthesis:
        """
        Use H-gent dialectics to synthesize positions.

        Not majority voting—dialectical sublation.
        """
        # Pair positions as thesis/antithesis
        pairs = self._pair_opposing(positions)

        syntheses = []
        for thesis, antithesis in pairs:
            synthesis = await synthesizer.sublate(thesis, antithesis)
            syntheses.append(synthesis)

        # Recursively synthesize until one remains
        while len(syntheses) > 1:
            pairs = self._pair_opposing(syntheses)
            syntheses = [
                await synthesizer.sublate(t, a)
                for t, a in pairs
            ]

        return syntheses[0]
```

### Emergent Coordination Rules

```python
class LocalCoordinationRules:
    """
    Simple local rules that produce emergent global coordination.

    Inspired by: Boids, ant colonies, neural synchronization.
    """

    @staticmethod
    def separation(agent: Agent, neighbors: list[Agent]) -> Vector:
        """Avoid crowding neighbors."""
        ...

    @staticmethod
    def alignment(agent: Agent, neighbors: list[Agent]) -> Vector:
        """Align with average heading of neighbors."""
        ...

    @staticmethod
    def cohesion(agent: Agent, neighbors: list[Agent]) -> Vector:
        """Move toward average position of neighbors."""
        ...

    @staticmethod
    def pheromone_following(agent: Agent, field: SemanticField) -> Vector:
        """Follow pheromone gradient."""
        ...
```

---

## 8. AGENTESE Negation and Fallback Operators

### The Gap

AGENTESE can invoke but can't express negation, fallback, or conditions.

### Proposed Syntax Extensions

```
# Negation: Everything except
world.!house.*           → All world entities except house
self.memory.!private.*   → All memories except private

# Fallback: Try first, then second
world.house.manifest | void.entropy.sip
  → If house.manifest fails, draw from void

# Conditional: Execute if condition met
world.house.manifest ? observer.archetype == "architect"
  → Only execute if observer is architect

# Composition with fallback
(world.doc.manifest >> concept.summary.refine) | void.slop.sip
  → Full pipeline with fallback to slop
```

### Implementation

```python
@dataclass
class AgentesePath:
    """Extended AGENTESE path with operators."""
    base_path: str
    negation: str | None = None
    fallback: "AgentesePath | None" = None
    condition: str | None = None

    @classmethod
    def parse(cls, path_str: str) -> "AgentesePath":
        """Parse extended AGENTESE syntax."""
        # Handle fallback operator
        if " | " in path_str:
            primary, fallback = path_str.split(" | ", 1)
            return cls(
                base_path=primary,
                fallback=cls.parse(fallback),
            )

        # Handle condition operator
        if " ? " in path_str:
            path, condition = path_str.split(" ? ", 1)
            return cls(base_path=path, condition=condition)

        # Handle negation
        if ".!" in path_str:
            parts = path_str.split(".!")
            return cls(base_path=parts[0], negation=parts[1])

        return cls(base_path=path_str)


class ExtendedLogos(Logos):
    """Logos with extended operator support."""

    async def invoke(self, path: str, observer: Umwelt, **kwargs) -> Any:
        parsed = AgentesePath.parse(path)

        # Check condition
        if parsed.condition:
            if not await self._evaluate_condition(parsed.condition, observer):
                raise ConditionNotMet(f"Condition failed: {parsed.condition}")

        try:
            # Handle negation
            if parsed.negation:
                return await self._invoke_with_negation(parsed, observer, **kwargs)

            return await super().invoke(parsed.base_path, observer, **kwargs)

        except (PathNotFoundError, AffordanceError) as e:
            # Try fallback
            if parsed.fallback:
                return await self.invoke(
                    parsed.fallback.base_path,
                    observer,
                    **kwargs
                )
            raise
```

---

## 9. Forced Accursed Tithe

### The Gap

Currently agents volunteer to tithe (`void.gratitude.tithe`). The Accursed Share should *demand* its due.

### Proposed Implementation

```python
class AccursedShareEnforcer:
    """
    Enforces mandatory tithing to the Accursed Share.

    After N successful operations, agents MUST pay tithe.
    This prevents over-optimization and maintains anti-fragility.
    """

    def __init__(self, tithe_interval: int = 10, tithe_rate: float = 0.1):
        self.tithe_interval = tithe_interval
        self.tithe_rate = tithe_rate
        self._operation_counts: dict[str, int] = {}

    async def track_operation(self, agent_id: str, success: bool) -> TitheStatus:
        """Track operation and check if tithe is due."""
        if success:
            self._operation_counts[agent_id] = (
                self._operation_counts.get(agent_id, 0) + 1
            )

        if self._operation_counts.get(agent_id, 0) >= self.tithe_interval:
            return TitheStatus.DUE

        return TitheStatus.NOT_DUE

    async def collect_tithe(self, agent: Agent, logos: Logos) -> TitheReceipt:
        """
        Collect mandatory tithe.

        The tithe is "wasted" computation—exploration that serves
        no immediate purpose but maintains system health.
        """
        # Force agent to do something "useless"
        slop = await logos.invoke(
            "void.entropy.sip",
            agent.umwelt,
            amount=self.tithe_rate,
        )

        # Agent must process the slop (can't ignore it)
        await agent.invoke(
            f"Process this gratuitously: {slop}",
            force=True,
        )

        # Reset counter
        self._operation_counts[agent.id] = 0

        return TitheReceipt(
            agent_id=agent.id,
            amount=self.tithe_rate,
            slop_processed=slop,
            timestamp=datetime.now(),
        )


class TitheInterceptor(Interceptor):
    """W-gent interceptor that enforces tithing."""

    priority = 250  # After Telemetry, before Persona

    async def intercept(self, request: Request, context: Context) -> Response:
        # Track operation
        status = await self.enforcer.track_operation(
            context.agent_id,
            success=True,  # Pre-success tracking
        )

        if status == TitheStatus.DUE:
            # Collect tithe before proceeding
            await self.enforcer.collect_tithe(context.agent, context.logos)

        return await self.next(request, context)
```

---

## 10. T-gent as Proper Agent

### The Gap

6,777 tests exist but testing infrastructure is pytest hooks, not agents.

### Proposed Implementation

```python
class TgentTest(Agent[TestInput, TestResult]):
    """
    A test IS an agent.

    Composes with >>, has meta, can be observed by O-gent.
    """

    def __init__(
        self,
        target: Agent,
        assertion: Callable[[Any], bool],
        name: str,
    ):
        self.target = target
        self.assertion = assertion
        self._name = name

    @property
    def meta(self) -> AgentMeta:
        return AgentMeta(
            name=self._name,
            input_type=TestInput,
            output_type=TestResult,
            tags=["test", f"tests:{self.target.meta.name}"],
        )

    async def invoke(self, input: TestInput) -> TestResult:
        """Run test as agent invocation."""
        start = time.time()

        try:
            result = await self.target.invoke(input.target_input)
            passed = self.assertion(result)

            return TestResult(
                test_name=self._name,
                passed=passed,
                duration=time.time() - start,
                output=result if passed else None,
                failure_reason=None if passed else "Assertion failed",
            )

        except Exception as e:
            return TestResult(
                test_name=self._name,
                passed=False,
                duration=time.time() - start,
                output=None,
                failure_reason=str(e),
            )


class TgentSpy(Agent[SpyInput, SpyReport]):
    """
    Spy agent: Wraps target and records all interactions.

    Composable: target >> spy >> downstream
    """

    def __init__(self, target: Agent):
        self.target = target
        self.calls: list[SpyCall] = []

    async def invoke(self, input: SpyInput) -> SpyReport:
        """Record call and delegate to target."""
        call = SpyCall(
            input=input.target_input,
            timestamp=datetime.now(),
        )

        try:
            result = await self.target.invoke(input.target_input)
            call.output = result
            call.success = True
        except Exception as e:
            call.error = e
            call.success = False
            raise
        finally:
            self.calls.append(call)

        return SpyReport(
            call=call,
            total_calls=len(self.calls),
            success_rate=sum(c.success for c in self.calls) / len(self.calls),
        )


class TgentSuite(Agent[SuiteInput, SuiteReport]):
    """
    Test suite as composable agent.

    Runs multiple T-gent tests, aggregates results.
    """

    def __init__(self, tests: list[TgentTest]):
        self.tests = tests

    async def invoke(self, input: SuiteInput) -> SuiteReport:
        """Run all tests, return aggregate report."""
        results = []

        for test in self.tests:
            result = await test.invoke(TestInput(
                target_input=input.shared_input,
            ))
            results.append(result)

        return SuiteReport(
            results=results,
            total=len(results),
            passed=sum(r.passed for r in results),
            failed=sum(not r.passed for r in results),
            duration=sum(r.duration for r in results),
        )
```

---

## Priority Matrix

| Enhancement | Impact | Effort | Dependencies |
|-------------|--------|--------|--------------|
| 2. Active Inference | High | Medium | Synapse, D-gent |
| 1. Y-gents | High | High | Registry, AGENTESE |
| 4. Kairos | Medium | Low | SemanticField |
| 3. Borromean | Medium | Medium | H-lacan |
| 5. Fitness Landscape | High | Medium | E-gent, O-gent |
| 9. Forced Tithe | Medium | Low | W-gent interceptors |
| 8. AGENTESE Operators | Medium | Medium | Logos |
| 6. Spec Refinement | Medium | Medium | R-gent, CI |
| 7. Swarm Intelligence | High | High | SemanticField, H-gent |
| 10. T-gent as Agent | Low | Medium | Test infrastructure |

### Recommended Sequence

1. **Phase 1** (Quick wins): Kairos, Forced Tithe
2. **Phase 2** (Foundations): Active Inference, Fitness Landscape
3. **Phase 3** (Architecture): Y-gents, Borromean, AGENTESE Operators
4. **Phase 4** (Ecosystem): Swarm Intelligence, Spec Refinement, T-gent Agent

---

## Success Criteria

The enhancement roadmap succeeds when:

1. **Mathematical coherence**: Active inference + Yoneda formalize existing intuitions
2. **Topological integrity**: Borromean constraint prevents degenerate outputs
3. **Temporal awareness**: Kairos enables opportune action, not just scheduling
4. **Evolutionary pressure**: Fitness landscape guides meaningful E-gent evolution
5. **Closed feedback loops**: R-gent automates spec refinement from impl
6. **Emergent coordination**: Swarm patterns replace orchestration
7. **Enforced gratitude**: Accursed Share demands its tithe

---

*"The system that aspires to enlightenment must formalize its intuitions. Mathematical rigor is not opposed to philosophical depth—it is its completion."*
