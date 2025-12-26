# JIT Skill Injection Operationalization Plan

> *"Skills evoked by state, not enumerated in prompts."*

**Created**: 2025-12-26
**Spec**: `spec/protocols/jit-skill-injection.md`
**Theory Chapters**: 14 (Binding), 11 (Meta-DP), 20 (Open Problems)
**Status**: Proposed — Kent validation required

---

## Executive Summary

This plan operationalizes Kent's radical vision for **Just-In-Time Skill Injection**—a system where skills appear dynamically based on agent state and environment, using LLM-optimized naming that maximizes binding fidelity.

### The Vision (Kent's Words)

> "Part of the meta-workflow is creating system prompts... heavily encourage claude code to use sub-agents (i.e. my prompts are meta already)"

> "Using docs like HYDRATE.md is an emergent/approximate implementation of stigmergic and progressive disclosure of procedural knowledge in an opt-in manner"

> "Formalize the accessing of skills in scenarios to be modeled in and defined through state transitions on the PolyAgent definition"

### The Proposals

| ID | Proposal | Priority | Effort | Depends On |
|----|----------|----------|--------|------------|
| **J1** | SkillRegistry with Activation Conditions | **Critical** | 1 week | — |
| **J2** | Meta-Epistemic Naming Registry | **Critical** | 1 week | J1 |
| **J3** | SkillInjector Service | High | 5 days | J1, J2 |
| **J4** | Stigmergic Discovery Engine | High | 1 week | J1, J3 |
| **J5** | BINDING_OPERAD Implementation | Medium | 5 days | J1 |
| **J6** | UniversalSkillBinder (PolyAgent Integration) | High | 1 week | J1, J5 |
| **J7** | AGENTESE Integration (self.skills.jit) | Medium | 3 days | J3, J6 |
| **J8** | Naming Strategy Benchmarks | Medium | 1 week | J2 |
| **J9** | Pilot Integration (trail-to-crystal) | **Critical** | 1 week | J3, J4, J7 |

**Total Effort**: ~7-8 weeks with parallelization

---

## The Core Insight

### The Binding Problem (From Theory)

Chapter 14 identifies that LLMs struggle with novel variable binding but excel at pattern completion. Current skill systems force LLMs to bind arbitrary skill names to behaviors—a binding-heavy task.

**JIT Skill Injection solves this by**:
1. **State-evoked skills**: Skills appear when state triggers them, not when explicitly called
2. **LLM-optimized names**: Names chosen to trigger correct patterns, not human readability
3. **Stigmergic learning**: Usage patterns guide future skill discovery

### The Meta-Epistemic Naming Hypothesis

**Hypothesis J.1**: Names that maximize LLM binding fidelity ("DIALECTIC_SUBLATE") outperform human-readable names ("Dialectical Synthesis Service") for skill invocation accuracy.

**Test Protocol**:
1. Create paired naming (LLM-optimized vs human-readable) for 20 skills
2. Present identical task descriptions to LLM with each naming
3. Measure correct skill invocation rate
4. Compute Galois loss for each naming

**Success Criterion**: LLM-optimized naming achieves >15% higher invocation accuracy.

---

## Detailed Proposals

### J1: SkillRegistry with Activation Conditions

**Theory Source**: Chapter 11 (Meta-DP), Chapter 14 (Binding)

**Specification**:

```python
@dataclass
class ActivationConditions:
    """When is this skill available?"""
    state_predicates: list[StatePredicate]   # e.g., "state.phase == CONTRADICTING"
    env_predicates: list[EnvPredicate]       # e.g., "env.has('thesis')"
    complexity_threshold: int = 3            # Minimum state complexity
    trigger_hint: str = ""                   # Brief description for injection

@dataclass
class SkillRegistration:
    name: MetaEpistemicName
    skill: Skill
    activation_conditions: ActivationConditions
    proxy_handler: ProxyHandler
    version: str
    created_at: datetime

class SkillRegistry:
    """Central registry for JIT skills."""

    async def register(
        self,
        concept: str,
        skill: Skill,
        activation_conditions: ActivationConditions,
        naming_strategy: NamingStrategy,
    ) -> SkillRegistration: ...

    async def query(
        self,
        state: AgentState,
        env: Environment,
        budget: int = 5,
    ) -> list[SkillRegistration]: ...
```

**Location**: `impl/claude/services/jsi/registry.py`

**Tests**:
- `test_registration()` — Skills can be registered with conditions
- `test_query_by_state()` — Query returns skills matching state predicates
- `test_query_by_env()` — Query returns skills matching env predicates
- `test_complexity_threshold()` — Simple agents don't receive complex skills

**Effort**: 1 week

---

### J2: Meta-Epistemic Naming Registry

**Theory Source**: Chapter 14 (Binding), Open Problem 20.A (Softness)

**Specification**:

```python
class NamingStrategy(Enum):
    LLM_OPTIMIZED = "llm"      # e.g., "DIALECTIC_SUBLATE"
    HUMAN_READABLE = "human"   # e.g., "Dialectical Synthesis Service"
    HYBRID = "hybrid"          # e.g., "DIALECTIC_SUBLATE (Synthesis)"

@dataclass
class MetaEpistemicName:
    llm_token: str              # LLM-optimized identifier
    human_description: str      # Human-readable form
    semantic_field: str         # Category for discovery
    binding_loss: float         # Galois loss of this naming

    def trigger_strength(self, context: str) -> float:
        """Measure binding strength in given context."""
        ...

class MetaEpistemicNamingRegistry:
    """Registry of LLM-optimized skill names."""

    async def generate_name(
        self,
        concept: str,
        strategy: NamingStrategy,
    ) -> MetaEpistemicName:
        """Generate LLM-optimized name for concept."""
        ...

    async def compute_binding_loss(
        self,
        name: MetaEpistemicName,
        test_contexts: list[str],
    ) -> float:
        """Measure how well this name binds in test contexts."""
        ...
```

**Location**: `impl/claude/services/jsi/naming.py`

**Tests**:
- `test_generate_llm_optimized()` — Generates concise, tokenizable names
- `test_binding_loss_computation()` — Measures Galois loss correctly
- `test_human_restoration()` — Can restore human-readable from LLM name
- `test_semantic_field_indexing()` — Names indexed by semantic field

**Effort**: 1 week

---

### J3: SkillInjector Service

**Theory Source**: Chapter 11 (Self-Improvement), Chapter 14 (Binding)

**Specification**:

```python
@dataclass
class InjectionResult:
    injected_skills: list[SkillRegistration]
    context_addition: str       # Formatted for system prompt
    binding_quality: float      # Estimated Galois loss
    tokens_used: int

class SkillInjector:
    """Injects skills into agent context Just-In-Time."""

    async def inject(
        self,
        agent: PolyAgent,
        state: AgentState,
        env: Environment,
        context_budget: int = 500,
    ) -> InjectionResult:
        """Inject relevant skills within token budget."""
        ...

    def _format_injection(
        self,
        skills: list[SkillRegistration],
    ) -> str:
        """Format skills for prompt injection."""
        ...
```

**Location**: `impl/claude/services/jsi/injector.py`

**Tests**:
- `test_injection_within_budget()` — Respects token budget
- `test_skill_ranking()` — Most relevant skills first
- `test_format_output()` — Produces valid prompt fragment
- `test_binding_quality_estimate()` — Estimates correlate with actual quality

**Effort**: 5 days

---

### J4: Stigmergic Discovery Engine

**Theory Source**: Kent's HYDRATE insight, Chapter 11 (Meta-DP)

**Specification**:

```python
@dataclass
class StigmergicTrace:
    skill_id: str
    state_features: dict
    env_features: dict
    success: bool
    timestamp: datetime

@dataclass
class StigmergicSuggestion:
    skill_id: str
    confidence: float
    success_rate: float
    similar_traces: int

class StigmergicDiscovery:
    """
    Skills leave traces that guide future discovery.

    This implements Kent's HYDRATE insight as a formal system.
    """

    async def record_usage(
        self,
        skill: SkillRegistration,
        state: AgentState,
        env: Environment,
        success: bool,
    ) -> None:
        """Record skill usage for learning."""
        ...

    async def discover(
        self,
        state: AgentState,
        env: Environment,
        limit: int = 5,
    ) -> list[StigmergicSuggestion]:
        """Discover skills via accumulated traces."""
        ...
```

**Location**: `impl/claude/services/jsi/stigmergy.py`

**Tests**:
- `test_trace_recording()` — Usage recorded correctly
- `test_discovery_by_similarity()` — Similar states find similar skills
- `test_success_rate_ranking()` — Successful skills ranked higher
- `test_convergence()` — Useful patterns emerge within 10 sessions

**Effort**: 1 week

---

### J5: BINDING_OPERAD Implementation

**Theory Source**: Chapter 4 (Operads), Chapter 14 (Binding)

**Specification**:

```python
BINDING_OPERAD = Operad(
    name="Skill Binding",
    operations={
        "instantiate": Operation(...),  # Skill × Input → Bound
        "chain": Operation(...),         # Kleisli composition
        "parallel": Operation(...),      # Parallel execution
        "fallback": Operation(...),      # Fallback on failure
    },
    laws=[
        Law("chain_associativity", ...),
        Law("parallel_commutativity", ...),
        Law("fallback_identity", ...),
    ]
)
```

**Location**: `impl/claude/services/jsi/operad.py`

**Tests**:
- `test_chain_associativity()` — Law holds
- `test_parallel_commutativity()` — Law holds (up to isomorphism)
- `test_fallback_identity()` — Law holds
- Property tests via Hypothesis

**Effort**: 5 days

---

### J6: UniversalSkillBinder (PolyAgent Integration)

**Theory Source**: Kent's "across ALL polyagents of sufficient complexity"

**Specification**:

```python
class UniversalSkillBinder:
    """
    Binds JIT skills to any sufficiently complex PolyAgent.

    "Sufficient complexity" = at least 3 states with non-trivial directions.
    """

    def is_sufficiently_complex(self, agent: PolyAgent) -> bool:
        """Check if agent can receive JIT skills."""
        return (
            len(agent.positions) >= 3
            and not self._has_trivial_directions(agent)
        )

    def bind_to_agent(
        self,
        agent: PolyAgent,
        skill_registry: SkillRegistry,
    ) -> BoundPolyAgent:
        """
        Augment agent with JIT skill injection.

        Original behavior preserved; skills are additive.
        """
        ...
```

**Location**: `impl/claude/services/jsi/binder.py`

**Tests**:
- `test_complexity_check()` — Only complex agents receive skills
- `test_original_behavior_preserved()` — Base transitions unchanged
- `test_skill_invocation_works()` — Skill inputs processed correctly
- `test_bound_agent_composes()` — BoundPolyAgent satisfies category laws

**Effort**: 1 week

---

### J7: AGENTESE Integration

**Theory Source**: AGENTESE spec, AD-012

**Specification**:

```python
@node(
    "self.skills.jit",
    description="JIT-injected skills for current state",
    aspects=("manifest", "invoke", "query", "history"),
    context=AGENTESEContext.SELF,
    dependencies=("skill_injector", "skill_registry", "stigmergic_discovery"),
)
class JITSkillsNode(BaseLogosNode):
    """AGENTESE node for JIT skills."""

    async def manifest(self, observer: Umwelt) -> Manifestation:
        """List available JIT skills."""
        ...

    async def invoke(self, observer: Umwelt, skill_name: str, args: dict) -> Result:
        """Invoke a JIT skill."""
        ...

    async def query(self, observer: Umwelt, state: dict, env: dict) -> list[dict]:
        """Query skills for hypothetical state-env."""
        ...

    async def history(self, observer: Umwelt) -> list[dict]:
        """View stigmergic trace history."""
        ...
```

**Location**: `impl/claude/protocols/agentese/nodes/jit_skills.py`

**Tests**:
- Integration tests via AGENTESE gateway
- Observer-dependent affordances
- Dependency injection

**Effort**: 3 days

---

### J8: Naming Strategy Benchmarks

**Theory Source**: Chapter 14 (Binding), Hypothesis J.1

**Specification**:

```python
@dataclass
class NamingBenchmarkResult:
    llm_optimized_accuracy: float
    human_readable_accuracy: float
    improvement_percentage: float
    galois_loss_difference: float
    statistical_significance: float  # p-value

class NamingBenchmark:
    """Benchmark LLM-optimized vs human-readable naming."""

    async def run(
        self,
        skills: list[tuple[str, str]],  # (llm_name, human_name) pairs
        test_contexts: list[str],
    ) -> NamingBenchmarkResult:
        """
        Compare naming strategies.

        For each skill:
        1. Present task with LLM-optimized name
        2. Present same task with human-readable name
        3. Measure correct invocation
        4. Compute Galois loss for each
        """
        ...
```

**Location**: `impl/claude/services/jsi/_tests/test_naming_benchmark.py`

**Success Criterion**: LLM-optimized achieves >15% higher accuracy

**Effort**: 1 week

---

### J9: Pilot Integration (trail-to-crystal)

**Theory Source**: Pilots Integration Plan, Joy Calibration

**Implementation**:

1. **Register trail-to-crystal skills**:
   - `TRAIL_MARK` — Record moment
   - `TRAIL_REFLECT` — Review day
   - `CRYSTAL_CONDENSE` — Compress to crystal
   - `CRYSTAL_CORRELATE` — Link to past patterns

2. **Define activation conditions**:
   - `TRAIL_MARK`: Any productive state
   - `TRAIL_REFLECT`: Evening hours, low activity
   - `CRYSTAL_CONDENSE`: Many marks accumulated
   - `CRYSTAL_CORRELATE`: View crystal context

3. **Stigmergic learning**:
   - Track which skills succeed in productivity flow
   - Surface successful patterns for future sessions

**Tests**:
- End-to-end flow: mark → reflect → crystal
- Stigmergic emergence over 5+ sessions
- Joy metric: user feels skills "just appear"

**Effort**: 1 week

---

## Execution Schedule

### Week-by-Week

| Week | Focus | Proposals | Depends On |
|------|-------|-----------|------------|
| 1 | Core Infrastructure | J1, J2 (parallel) | — |
| 2 | Injection + Operad | J3, J5 (parallel) | J1, J2 |
| 3 | Stigmergy + Binding | J4, J6 (parallel) | J1, J3, J5 |
| 4 | Integration + Benchmark | J7, J8 (parallel) | J3, J6, J2 |
| 5 | Pilot Integration | J9 | J3, J4, J7 |

### Parallelization

```
Week 1:  J1 ──────────────────────────────────────┐
         J2 ──────────────────────────────────────┤
                                                   │
Week 2:          J3 ──────────────────────────────┼───────────┐
                 J5 ──────────────────────────────┤           │
                                                   │           │
Week 3:                    J4 ────────────────────┤           │
                           J6 ────────────────────┼───────────┤
                                                   │           │
Week 4:                              J7 ──────────┤           │
                                     J8 ──────────┘           │
                                                               │
Week 5:                                           J9 ─────────┘
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Skill invocation accuracy** | > 85% | Test suite |
| **Context reduction** | > 50% tokens | Comparison vs enumeration |
| **Binding loss** | < 0.2 | Galois loss measurement |
| **Stigmergic convergence** | < 10 sessions | User study |
| **Naming benchmark** | > 15% improvement | J8 results |
| **Constitutional compliance** | 100% | Runtime checks |
| **Pilot NPS** | > 40 | User survey |

---

## Risk Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Naming hypothesis fails | Medium | High | Fall back to hybrid naming |
| Binding complexity too high | Medium | Medium | Simplify activation conditions |
| Stigmergic learning slow | Medium | Medium | Seed with curated traces |
| PolyAgent integration breaks laws | Low | High | Property tests + law verification |
| Pilot delayed | Medium | High | Focus on registry only first |

---

## Constitutional Alignment Check

| Principle | How JSI Honors It |
|-----------|-------------------|
| **Tasteful** | Only relevant skills injected, not all |
| **Curated** | Skill registry is intentional selection |
| **Ethical** | All injected skills pass constitutional check |
| **Joy-Inducing** | Skills "just appear" when needed — magic feel |
| **Composable** | BINDING_OPERAD ensures composition laws |
| **Heterarchical** | Skills can come from any source, no fixed hierarchy |
| **Generative** | Spec generates implementation; naming generates binding |

---

## The Mirror Test

> *"Does this feel like Kent on his best day — or did we make it safe?"*

**This plan is daring because**:
- It bets on LLM-optimized naming as a core advantage
- It trusts stigmergic emergence over explicit enumeration
- It applies operad theory to a practical problem

**This plan is tasteful because**:
- 9 proposals, not 50 — each justified by theory
- Critical path is linear and clear
- Pilot grounds everything in user value

**This plan is joy-inducing because**:
- Skills "just appear" when you need them
- Progressive disclosure feels like discovery
- The system learns your patterns

---

> *"The skill doesn't wait to be called. The state evokes the skill."*

**Next Action**: Kent validation of proposals, then J1 implementation begins.

---

**Document Metadata**
- **Lines**: ~500
- **Status**: Proposed
- **Proposals**: 9 (J1-J9)
- **Total Effort**: 7-8 weeks (5 weeks parallelized)
- **Created**: 2025-12-26
