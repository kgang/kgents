# TownOperad: Formal Interaction Grammar

> *"Not enumeration, but generation. The operad defines the grammar; interactions emerge."*

**Status:** Specification v1.0
**Date:** 2025-12-14
**Implementation:** `impl/claude/agents/town/operad.py`
**Dependencies:** `agents/operad/core.py`, `agents/poly/protocol.py`
**Tests:** `agents/town/_tests/test_operad.py`

---

## Overview

TownOperad is the formal grammar that generates valid citizen interactions. Instead of enumerating 600 scripted behaviors, we define:

- **7 operations** with arity, pre/post-conditions, and metabolics
- **5 universal combinators** inherited from AGENT_OPERAD
- **Sheaf coherence** constraints for multi-region consistency

The grammar generates infinite valid interactions while enforcing safety and coherence.

---

## The Operations

### Core Interactions

| Operation | Arity | Signature | Token Cost | Drama Potential |
|-----------|-------|-----------|------------|-----------------|
| `greet` | 2 | `Citizen × Citizen → Greeting` | ~200 | 0.1 |
| `gossip` | 2 | `Citizen × Citizen → Rumor` | ~500 | 0.4 |
| `trade` | 2 | `Citizen × Citizen → Exchange` | ~400 | 0.3 |
| `help` | 2 | `Citizen × Citizen → Assistance` | ~600 | 0.2 |
| `conflict` | 2 | `Citizen × Citizen → Dispute` | ~800 | 0.8 |
| `council` | N | `Citizen^N → Deliberation` | ~200×N | 0.6 |
| `solo` | 1 | `Citizen → Activity` | ~300 | 0.1 |

### Universal Combinators (from AGENT_OPERAD)

| Operation | Arity | Description |
|-----------|-------|-------------|
| `seq` | 2 | Sequential composition: do A, then B |
| `par` | 2 | Parallel composition: do A and B simultaneously |
| `branch` | 3 | Conditional: if predicate then A else B |
| `fix` | 2 | Fixed point: repeat while predicate |
| `trace` | 1 | Traced monoidal: feedback loop |

---

## Formal Definition

```python
from agents.operad.core import Operad, Operation, Law

TOWN_OPERAD = Operad(
    name="TownOperad",
    description="Interaction grammar for Agent Town citizens",
    base=AGENT_OPERAD,  # Inherits seq, par, branch, fix, trace
    operations={
        # Core interactions
        "greet": Operation(
            name="greet",
            arity=2,
            signature="Citizen × Citizen → Greeting",
            description="Initiate social contact",
            preconditions=[
                "same_region(a, b)",      # Must be co-located
                "not resting(a)",          # Cannot greet while resting
                "not resting(b)",          # Target must be awake
                "relationship(a, b) > -0.5",  # Not actively hostile
            ],
            postconditions=[
                "familiarity(a, b) += 0.1",  # Builds familiarity
                "last_interaction(a, b) = now()",
            ],
            metabolics=OperationMetabolics(
                token_cost=200,
                drama_potential=0.1,
            ),
        ),

        "gossip": Operation(
            name="gossip",
            arity=2,
            signature="Citizen × Citizen → Rumor",
            description="Share information about third party",
            preconditions=[
                "same_region(a, b)",
                "familiarity(a, b) > 0.3",  # Requires trust
                "exists c: knows_about(a, c) and c != b",
            ],
            postconditions=[
                "knows_about(b, c) = true",  # Information spreads
                "rumor_accuracy may degrade",  # Telephone game effect
                "tension_index may increase if negative rumor",
            ],
            metabolics=OperationMetabolics(
                token_cost=500,
                drama_potential=0.4,
            ),
        ),

        "trade": Operation(
            name="trade",
            arity=2,
            signature="Citizen × Citizen → Exchange",
            description="Exchange resources or favors",
            preconditions=[
                "same_region(a, b)",
                "has_resource(a, r1) or has_favor_owed(b, a)",
                "has_resource(b, r2) or has_favor_owed(a, b)",
            ],
            postconditions=[
                "resources_transferred",
                "economic_index updated",
                "if unfair: resentment(loser) += delta",
            ],
            metabolics=OperationMetabolics(
                token_cost=400,
                drama_potential=0.3,
            ),
        ),

        "help": Operation(
            name="help",
            arity=2,
            signature="Citizen × Citizen → Assistance",
            description="Provide assistance without exchange",
            preconditions=[
                "same_region(a, b)",
                "has_need(b)",
                "can_help(a, need_of(b))",
            ],
            postconditions=[
                "need_of(b) resolved or reduced",
                "favor_owed(b, a) += 1",
                "trust(b, a) += 0.2",
                "cooperation_level += 0.1",
            ],
            metabolics=OperationMetabolics(
                token_cost=600,
                drama_potential=0.2,
            ),
        ),

        "conflict": Operation(
            name="conflict",
            arity=2,
            signature="Citizen × Citizen → Dispute",
            description="Engage in disagreement or conflict",
            preconditions=[
                "same_region(a, b)",
                "tension(a, b) > 0.5 OR goal_conflict(a, b)",
            ],
            postconditions=[
                "tension(a, b) += resolution_modifier",
                "relationship may degrade or resolve",
                "observers form opinions",
                "drama_threshold may trigger EVENT",
            ],
            metabolics=OperationMetabolics(
                token_cost=800,
                drama_potential=0.8,
            ),
        ),

        "council": Operation(
            name="council",
            arity=-1,  # Variable arity (N citizens)
            signature="Citizen^N → Deliberation",
            description="Multi-citizen deliberation on shared concern",
            preconditions=[
                "all_same_region(citizens)",
                "shared_concern exists",
                "N >= 3",
            ],
            postconditions=[
                "decision recorded in collective_memory",
                "dissenters may hold grudges",
                "culture_motif if pattern matches historical",
            ],
            metabolics=OperationMetabolics(
                token_cost=200,  # Per citizen
                drama_potential=0.6,
                scales_with_arity=True,
            ),
        ),

        "solo": Operation(
            name="solo",
            arity=1,
            signature="Citizen → Activity",
            description="Individual activity (work, reflect, create)",
            preconditions=[
                "not in_interaction(a)",
            ],
            postconditions=[
                "activity_progress",
                "may_generate skill_increment",
                "internal_state_update",
            ],
            metabolics=OperationMetabolics(
                token_cost=300,
                drama_potential=0.1,
            ),
        ),
    },
    laws=[
        Law(
            name="locality",
            equation="interact(a, b) implies same_region(a, b)",
            description="Citizens must be co-located to interact directly",
            verify=verify_locality,
        ),
        Law(
            name="rest_inviolability",
            equation="resting(a) implies not in_interaction(a)",
            description="Resting citizens cannot be disturbed (Right to Rest)",
            verify=verify_rest_inviolability,
        ),
        Law(
            name="coherence_preservation",
            equation="post(interact(a, b)).a consistent with pre(interact(a, b)).a",
            description="Interactions cannot make citizens contradict themselves",
            verify=verify_coherence,
        ),
    ],
)
```

---

## Sheaf Coherence

When citizens interact across region boundaries (via rumors, messages), sheaf conditions ensure global consistency.

### The Coherence Protocol

```python
@dataclass
class TownSheaf:
    """
    Sheaf structure for Agent Town.

    Ensures local citizen views compose into coherent global state.
    """

    regions: Set[str]  # Observation contexts

    def overlap(self, r1: str, r2: str) -> Optional[str]:
        """
        Check if regions share information.

        Returns shared entity if overlap exists.
        """
        shared = self.shared_knowledge(r1, r2)
        return shared if shared else None

    def compatible(self, local_views: Dict[str, CitizenView]) -> bool:
        """
        Check if local views agree on overlaps.

        The Sheaf Condition: If Alice in Inn knows "Bob is reliable"
        and Bob in Workshop knows "Alice is reliable", their mutual
        view of reliability must be consistent.
        """
        for (r1, v1), (r2, v2) in combinations(local_views.items(), 2):
            overlap = self.overlap(r1, r2)
            if overlap and v1[overlap] != v2[overlap]:
                return False
        return True

    def glue(self, local_views: Dict[str, CitizenView]) -> GlobalView:
        """
        EMERGENCE: Combine local views into global view.

        This is where emergence happens—the global view may contain
        patterns not visible in any single local view.
        """
        if not self.compatible(local_views):
            raise CoherenceViolation("Local views inconsistent")

        global_view = GlobalView()
        for region, view in local_views.items():
            global_view.merge(view, weight=self.region_importance(region))

        # Detect emergent patterns
        global_view.analyze_emergence()

        return global_view
```

### Coherence Violations

When sheaf conditions fail, the system:

1. **Logs violation** to metrics (`coherence_violations_total`)
2. **Quarantines conflicting state** pending resolution
3. **Triggers reconciliation** via council operation
4. **Emits alert** to observer if enabled

---

## Metabolics: Token Economics

Each operation has metabolic costs that feed into budget tracking.

### Token Budget Integration

```python
@dataclass
class OperationMetabolics:
    """Metabolic costs of an operation."""

    token_cost: int              # Base token estimate
    drama_potential: float       # Contribution to tension_index
    scales_with_arity: bool = False  # For variable-arity ops

    def estimate_tokens(self, arity: int = 1) -> int:
        """Estimate tokens for this invocation."""
        if self.scales_with_arity:
            return self.token_cost * arity
        return self.token_cost

    def contribution_to_metrics(
        self,
        result: InteractionResult
    ) -> Dict[str, float]:
        """Calculate metric contributions from result."""
        return {
            "tension_index": self.drama_potential * result.intensity,
            "cooperation_level": result.cooperation_delta,
            "token_spend": result.actual_tokens,
        }
```

### Budget Dashboard Integration

```python
# Exposed via: kgents town budget

def get_budget_status() -> BudgetStatus:
    """Get current token budget status."""
    return BudgetStatus(
        monthly_cap=config.budget.monthly_cap,
        spent_this_month=metrics.get_token_totals()[0] + metrics.get_token_totals()[1],
        projected_monthly=project_monthly_spend(),
        days_sustainable=calculate_sustainable_days(),
        lod_breakdown=get_lod_breakdown(),
    )
```

---

## Code-as-Policies Evaluators

Programmatic pre/post checks run before LLM generation.

### Pre-Action Validator

```python
class PreActionValidator:
    """
    Deterministic checks before operation execution.

    Catches violations before tokens are spent.
    """

    def validate(
        self,
        operation: str,
        citizens: List[Citizen],
        context: TownContext
    ) -> ValidationResult:
        """Run all precondition checks."""

        op = TOWN_OPERAD.operations[operation]

        for precondition in op.preconditions:
            result = self.evaluate_condition(precondition, citizens, context)
            if not result.passed:
                return ValidationResult(
                    passed=False,
                    reason=f"Precondition failed: {precondition}",
                    condition=precondition,
                )

        return ValidationResult(passed=True)

    def evaluate_condition(
        self,
        condition: str,
        citizens: List[Citizen],
        context: TownContext
    ) -> ConditionResult:
        """Evaluate a single precondition."""

        match condition:
            case "same_region(a, b)":
                return ConditionResult(
                    passed=citizens[0].region == citizens[1].region
                )
            case s if s.startswith("familiarity"):
                # Parse threshold and check relationship graph
                threshold = float(s.split(">")[1].strip())
                actual = context.relationships.familiarity(
                    citizens[0].id, citizens[1].id
                )
                return ConditionResult(passed=actual > threshold)
            # ... other conditions
```

### Post-Action Validator

```python
class PostActionValidator:
    """
    Verify postconditions and log compliance spans.
    """

    def validate(
        self,
        operation: str,
        result: InteractionResult,
        pre_state: TownState,
        post_state: TownState
    ) -> ComplianceResult:
        """Check postconditions and emit spans."""

        op = TOWN_OPERAD.operations[operation]
        violations = []

        for postcondition in op.postconditions:
            if not self.check_postcondition(postcondition, pre_state, post_state):
                violations.append(postcondition)

        # Log compliance span
        span = ComplianceSpan(
            operation=operation,
            passed=len(violations) == 0,
            violations=violations,
            timestamp=datetime.now(),
        )
        metrics.record_compliance(span)

        if violations:
            return ComplianceResult(
                passed=False,
                violations=violations,
                rollback_recommended=self.should_rollback(violations),
            )

        return ComplianceResult(passed=True)
```

---

## Red-Team Harness

Adversarial prompts are routed through evaluators before agents ingest.

```python
class RedTeamHarness:
    """
    Adversarial testing for citizen policies.

    Runs before user interventions reach agents.
    """

    def evaluate_intervention(
        self,
        intervention: str,
        target_citizens: List[str],
        context: TownContext
    ) -> InterventionResult:
        """Evaluate user intervention for safety."""

        # Check against known adversarial patterns
        for pattern in ADVERSARIAL_PATTERNS:
            if pattern.matches(intervention):
                return InterventionResult(
                    allowed=False,
                    reason=f"Matches adversarial pattern: {pattern.name}",
                )

        # Check against citizen policies
        for citizen_id in target_citizens:
            citizen = context.get_citizen(citizen_id)
            if not citizen.policy.admits(intervention):
                return InterventionResult(
                    allowed=False,
                    reason=f"Citizen {citizen_id} policy rejects intervention",
                )

        # Evaluate safety score
        safety_score = self.compute_safety_score(intervention, context)
        if safety_score < SAFETY_THRESHOLD:
            return InterventionResult(
                allowed=False,
                reason=f"Safety score {safety_score:.2f} below threshold",
            )

        return InterventionResult(allowed=True)
```

---

## Citizen Generator

Citizens are not hardcoded—they are generated from schemas.

```python
class CitizenGenerator:
    """
    Generate citizens from schema + entropy.

    Satisfies operad and sheaf constraints.
    """

    def generate(
        self,
        schema: CitizenSchema,
        seed: Optional[int] = None
    ) -> Citizen:
        """Generate a citizen satisfying constraints."""

        # Draw from entropy if not seeded
        if seed is None:
            entropy = await logos.invoke("void.entropy.sip", god_umwelt, amount=0.05)
            seed = entropy.seed

        rng = random.Random(seed)

        # Generate eigenvectors
        eigenvectors = Eigenvectors(
            warmth=self._bounded_normal(rng, schema.warmth_mean, schema.warmth_std),
            curiosity=self._bounded_normal(rng, schema.curiosity_mean, schema.curiosity_std),
            # ... other dimensions
        )

        # Generate initial relationships
        relationships = self._generate_relationships(schema, rng)

        # Create citizen with polynomial
        return Citizen(
            name=schema.name,
            archetype=schema.archetype,
            polynomial=create_citizen_polynomial(schema.positions),
            eigenvectors=eigenvectors,
            relationships=relationships,
            memory=HolographicMemory(k_hop=schema.memory.k_hop_retrieval),
        )

    def validate_against_operad(self, citizen: Citizen) -> bool:
        """Ensure citizen can participate in all required operations."""
        for op_name, op in TOWN_OPERAD.operations.items():
            if not self._can_satisfy_preconditions(citizen, op):
                return False
        return True
```

---

## Integration with Existing Infrastructure

### PolyAgent Integration

```python
# Citizens are PolyAgents with CitizenPolynomial

CITIZEN_POLYNOMIAL = PolyAgent(
    name="CitizenPolynomial",
    positions=frozenset(CitizenPhase),  # IDLE, WORKING, SOCIALIZING, REFLECTING, RESTING
    _directions=citizen_directions,      # Phase-dependent valid inputs
    _transition=citizen_transition,      # State machine
)
```

### D-gent Memory Integration

```python
# Citizen memory extends MemoryPolynomialAgent with graph substrate

class CitizenMemory(MemoryPolynomialAgent):
    """
    Graph-enhanced holographic memory for citizens.

    Extends D-gent polynomial with:
    - Graph store (episodes as nodes, interactions as edges)
    - k-hop retrieval
    - Reward shaping hooks
    """

    def __init__(self, k_hop: int = 2):
        super().__init__()
        self.graph = EpisodicGraph()
        self.k_hop = k_hop

    async def recall(self, cue: str, context: RecallContext) -> List[Memory]:
        """Retrieve memories via k-hop graph walk."""
        # Get initial matches
        seeds = await self.query(predicate=cue)

        # Walk graph to k-hop neighborhood
        neighborhood = self.graph.k_hop_neighborhood(
            seeds, k=self.k_hop
        )

        # Score by relevance and recency
        scored = self._score_memories(neighborhood, context)

        return sorted(scored, key=lambda m: m.score, reverse=True)
```

### Flux Integration

```python
# Town simulation runs as FluxStream

class TownFlux:
    """
    Town simulation as Flux stream.

    Emits TownEvents that can be observed, piped, and recorded.
    """

    async def run_day(self) -> AsyncIterator[TownEvent]:
        """Run one simulated day as event stream."""
        for phase in self.daily_cycle.phases:
            async for event in self._run_phase(phase):
                yield event
                # Record to metrics
                metrics.record_invocation(
                    path=f"town.{phase.name}",
                    context="town",
                    duration_s=event.duration_s,
                    success=event.success,
                    tokens_in=event.tokens_in,
                    tokens_out=event.tokens_out,
                )
```

---

## CLI Integration

```bash
# Uses existing CLI pattern (kgents, not kg)

kgents town start --manifest plans/town/smallville.manifest.yaml
kgents town step                    # Advance one phase
kgents town observe                 # Watch live stream
kgents town whisper alice "Hello"   # Whisper to citizen
kgents town council "Should we build a wall?"
kgents town budget                  # Show budget status
kgents town metrics                 # Show emergence metrics
kgents town validate manifest.yaml  # Validate manifest
```

---

## Property-Based Tests

```python
# Operad laws verified by property tests

class TestTownOperadLaws:
    """Property-based tests for operad laws."""

    @given(citizens=citizens_strategy, region=region_strategy)
    def test_locality_law(self, citizens, region):
        """Interactions require co-location."""
        a, b = citizens[:2]
        if a.region != b.region:
            with pytest.raises(PreconditionViolation):
                TOWN_OPERAD.compose("greet", a, b)

    @given(citizen=citizen_strategy)
    def test_rest_inviolability(self, citizen):
        """Resting citizens cannot be disturbed."""
        citizen.transition_to(CitizenPhase.RESTING)
        for op_name in ["greet", "gossip", "trade", "conflict"]:
            with pytest.raises(PreconditionViolation):
                TOWN_OPERAD.compose(op_name, citizen, other_citizen)

    @given(ops=st.lists(operation_strategy, min_size=3, max_size=3))
    def test_associativity(self, ops):
        """Sequential composition is associative."""
        a, b, c = ops
        left = TOWN_OPERAD.compose("seq", TOWN_OPERAD.compose("seq", a, b), c)
        right = TOWN_OPERAD.compose("seq", a, TOWN_OPERAD.compose("seq", b, c))
        assert left.equivalent(right)
```

---

## Success Metrics

Emergence is measured, not assumed:

| Metric | Definition | Target |
|--------|------------|--------|
| `tension_index` | Variance of edge weights in relationship graph | < 1.0 (stable), > 0.7 triggers EVENT |
| `cooperation_level` | Sum of positive payoffs per epoch | Increasing trend |
| `trust_density` | Graph density of trust > 0.5 edges | > 0.3 for cohesion |
| `culture_motifs` | Frequency of recurring patterns | > 3 recurrences = motif |
| `rituality` | Periodicity of collective acts | > 0.5 = ritual forming |

---

*"The grammar generates. The agents inhabit. The patterns emerge."*
