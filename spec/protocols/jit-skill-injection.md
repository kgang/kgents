# JIT Skill Injection Protocol (JSI)

> *"Skills appear when needed, not when enumerated. The agent's state evokes the skill; the skill doesn't wait to be called."*

**Status**: Proposal | **Version**: 0.1
**Related**: `spec/agents/operads.md`, `spec/agents/primitives.md`, `spec/principles.md`
**Theory Chapters**: 14 (Binding), 11 (Meta-DP), 20 (Open Problems)

---

## Purpose

**Why does this need to exist?**

Current skill systems suffer from two fundamental problems:

1. **The Enumeration Problem**: Skills are listed in system prompts, consuming context tokens. As skills grow (24+ in kgents), the prompt bloats. The agent sees all skills always, even when irrelevant.

2. **The Evocation Problem**: Skills like "voodoo-metaphysics" or "dialectical-synthesis" are powerful but non-obvious. When should an agent invoke them? The skill name doesn't self-evidently trigger in relevant contexts.

**The JIT Skill Injection Protocol solves both by**:
- Injecting skills dynamically based on agent state and environment
- Naming skills with LLM-optimized tokens that trigger appropriate invocation
- Modeling skill binding as PolyAgent state transitions with operad composition

---

## The Core Insight

> Skills are not tools to be picked. Skills are **affordances that emerge from agent-environment coupling**.

In Gibson's ecological psychology, an affordance isn't in the object or the observer alone—it's in their meeting. A chair affords sitting to a human but not to a fish.

**Applied to skills**: A skill isn't a static capability. It's a **morphism that becomes available when the agent's PolyAgent state and environment jointly satisfy activation conditions**.

```
Traditional:  Agent has skills S1, S2, S3... Agent picks S1.
JIT:          Agent is in state (s, env). State evokes skill S1 automatically.
```

---

## Formal Definition

### The Skill Functor

A skill is a **functor from the product of PolyAgent state and Environment to morphism availability**:

```python
Skill: PolyAgent × Environment → Maybe[Morphism]

# Only available when conditions met
skill_available(state, env) → Some(morphism) | None
```

### The Skill Operad

Skills compose via an operad JSI_OPERAD:

```python
JSI_OPERAD = Operad(
    name="JIT Skill Injection",
    operations={
        "evoke": Operation(
            name="evoke",
            arity=2,
            signature="PolyAgent × Env → PolyAgent",
            compose=evoke_skill,
            description="Skill emerges from state-environment coupling"
        ),
        "bind": Operation(
            name="bind",
            arity=3,
            signature="Skill × State × Env → BoundSkill",
            compose=bind_skill,
            description="Bind skill to specific state-env configuration"
        ),
        "compose": Operation(
            name="compose",
            arity=2,
            signature="BoundSkill × BoundSkill → BoundSkill",
            compose=compose_skills,
            description="Skills compose when domains/codomains match"
        ),
        "proxy": Operation(
            name="proxy",
            arity=2,
            signature="Skill × ProxyHandler → DelegatedSkill",
            compose=proxy_skill,
            description="Skill execution delegated to external handler"
        ),
    },
    laws=[
        Law(
            name="evocation_determinism",
            equation="evoke(s, env) = evoke(s, env)",
            description="Same state-env always evokes same skills"
        ),
        Law(
            name="composition_associativity",
            equation="compose(compose(a,b),c) = compose(a, compose(b,c))",
            description="Skill composition is associative"
        ),
        Law(
            name="proxy_transparency",
            equation="proxy(skill, handler).invoke = handler.delegate(skill).invoke",
            description="Proxied skill execution equals handler delegation"
        ),
    ]
)
```

### State-Dependent Skill Directions

The PolyAgent's `directions` function now includes skill availability:

```python
def directions(state: AgentState, env: Environment) -> FrozenSet[Type]:
    """
    Valid inputs now include JIT-injected skills.

    Returns:
        Base directions UNION skills available in this state-env.
    """
    base_directions = standard_directions(state)

    # JIT: Query skill registry for available skills
    available_skills = skill_registry.query(state, env)

    # Each skill adds its input type to valid directions
    skill_directions = frozenset(
        skill.input_type for skill in available_skills
    )

    return base_directions | skill_directions
```

---

## The Meta-Epistemic Naming Protocol

### The Binding Problem Applied to Skill Names

From Chapter 14, LLMs struggle with novel variable binding. But they excel at pattern completion on familiar structures.

**Insight**: Skill names should be **tokens that reliably trigger correct usage patterns** in LLMs, not human-readable descriptions.

### The Naming Principle

> Name services and skills with tokens that **inspire correct LLM behavior**, even if those names seem cryptic to humans. Human interpretability can be restored algorithmically.

**Example**:
```python
# Human-readable but doesn't trigger correct pattern
class SocketConnectionManager:
    pass

# LLM-optimized: triggers correct networking patterns
class NetSocket_CONNECT_STREAM:
    pass

# The LLM "binds" this name to networking concepts more reliably
```

### The K-Block Isolation Monoid

Names exist in a **naming monoid** within the K-Block infrastructure:

```python
NamingMonoid = Monoid(
    identity="",  # Empty string
    combine=lambda a, b: f"{a}_{b}",  # Underscore composition

    # Naming axioms
    axioms=[
        "Names should be 1-3 tokens in the LLM vocabulary",
        "Names should trigger the intended semantic field",
        "Names can be parsed back to human-readable form",
    ]
)
```

### The Name-to-Behavior Mapping

```python
@dataclass
class MetaEpistemicName:
    """
    A name optimized for LLM binding.
    """
    llm_token: str            # e.g., "DIALECTIC_FUSE"
    human_description: str     # e.g., "Dialectical synthesis service"
    semantic_field: str        # e.g., "philosophy.hegelian.synthesis"

    # Galois loss of the name (how well it preserves meaning)
    binding_loss: float        # Lower is better

    # Versioned proxy handler for this concept
    proxy_version: str         # e.g., "v1.2.0"

    def to_human(self) -> str:
        """Restore human-readable form via parsing."""
        return self.human_description

    def trigger_strength(self, context: str) -> float:
        """
        Measure: How likely is this name to trigger correct behavior
        in the given context?

        Uses: Embedding similarity, frequency analysis, behavioral testing.
        """
        pass
```

### The Naming Registry

```python
class MetaEpistemicNamingRegistry:
    """
    Registry of LLM-optimized names with versioning and proxy handlers.
    """

    def register_skill(
        self,
        concept: str,
        llm_token: str,
        proxy_handler: ProxyHandler,
        semantic_field: str,
    ) -> MetaEpistemicName:
        """
        Register a skill with its LLM-optimized name.

        The name will be:
        1. Tested for binding loss (does LLM use it correctly?)
        2. Versioned for proxy delegation
        3. Indexed by semantic field for JIT discovery
        """
        pass

    def find_by_state(
        self,
        state: AgentState,
        env: Environment,
    ) -> list[MetaEpistemicName]:
        """
        JIT: Find skills whose semantic fields match this state-env.

        Uses:
        - State transitions as query
        - Environment features as context
        - Semantic field similarity as ranking
        """
        pass
```

---

## The Operad-ified Binding Architecture

### The Binding Operad

Skills aren't just injected—they're **bound** in a categorical structure:

```python
BINDING_OPERAD = Operad(
    name="Skill Binding",
    operations={
        "instantiate": Operation(
            name="instantiate",
            arity=2,
            signature="Skill[A, B] × A → Bound[A, B]",
            compose=instantiate_skill,
            description="Bind skill to specific input"
        ),
        "chain": Operation(
            name="chain",
            arity=2,
            signature="Bound[A, B] × Bound[B, C] → Bound[A, C]",
            compose=chain_bound,
            description="Chain bound skills (Kleisli composition)"
        ),
        "parallel": Operation(
            name="parallel",
            arity=2,
            signature="Bound[A, B] × Bound[A, C] → Bound[A, (B, C)]",
            compose=parallel_bound,
            description="Run bound skills in parallel"
        ),
        "fallback": Operation(
            name="fallback",
            arity=2,
            signature="Bound[A, B] × Bound[A, B] → Bound[A, B]",
            compose=fallback_bound,
            description="Second skill as fallback if first fails"
        ),
    },
    laws=[
        Law(
            name="chain_associativity",
            equation="chain(chain(a,b),c) = chain(a, chain(b,c))",
            description="Chaining is associative"
        ),
        Law(
            name="parallel_commutativity",
            equation="parallel(a, b) ≅ parallel(b, a)",
            description="Parallel order is irrelevant (up to tuple swap)"
        ),
        Law(
            name="fallback_identity",
            equation="fallback(a, fail) = a",
            description="Fallback with fail is identity"
        ),
    ]
)
```

### Cross-PolyAgent Binding

**Key insight from Kent**: This binding architecture applies **across ALL PolyAgents of sufficient complexity**.

```python
class UniversalSkillBinder:
    """
    Any PolyAgent with sufficient complexity can receive JIT skills.

    "Sufficient complexity" = has at least 3 states and non-trivial
    direction functions.
    """

    def bind_to_agent(
        self,
        agent: PolyAgent,
        skill_registry: MetaEpistemicNamingRegistry,
    ) -> BoundPolyAgent:
        """
        Augment agent's transition function with JIT skill injection.

        The agent's original behavior is preserved; skills are additive.
        """
        original_transition = agent.transition

        def augmented_transition(state, input, env):
            # Check if input is a skill invocation
            if isinstance(input, SkillInvocation):
                skill = skill_registry.resolve(input.skill_name)
                return skill.execute(state, input.args, env)

            # Otherwise, original behavior
            return original_transition(state, input)

        return BoundPolyAgent(
            **agent.as_dict(),
            transition=augmented_transition,
        )
```

### Parallel AND Orthogonal to Tool Use

From Kent's specification: JIT skill injection exists **parallel and orthogonal** to conventional tool use.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONVENTIONAL TOOL USE                                                        │
│                                                                              │
│   Agent ──select tool──▶ Tool ──execute──▶ Result                          │
│   (explicit selection)                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ JIT SKILL INJECTION (parallel)                                               │
│                                                                              │
│   (State, Env) ──evokes──▶ Skill ──auto-inject──▶ Augmented Agent          │
│   (state-driven, automatic)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ ORTHOGONALITY                                                                │
│                                                                              │
│   JIT skills can themselves be tool-using.                                   │
│   Tools can trigger JIT skill injection.                                     │
│   Neither subsumes the other.                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Architecture

### The Skill Registry Service

```python
# services/jsi/registry.py

@dataclass
class SkillRegistration:
    """A registered skill with all metadata."""
    name: MetaEpistemicName
    skill: Skill
    activation_conditions: ActivationConditions
    proxy_handler: ProxyHandler
    version: str
    created_at: datetime

class SkillRegistry:
    """
    Central registry for JIT skills.

    Crown Jewel Pattern: This is the authority on skill availability.
    """

    def __init__(self, storage: StorageProvider):
        self._registrations: dict[str, SkillRegistration] = {}
        self._storage = storage

    async def register(
        self,
        concept: str,
        skill: Skill,
        activation_conditions: ActivationConditions,
        naming_strategy: NamingStrategy = NamingStrategy.LLM_OPTIMIZED,
    ) -> SkillRegistration:
        """
        Register a skill for JIT injection.

        Steps:
        1. Generate LLM-optimized name using naming strategy
        2. Compute binding loss for the name
        3. Create proxy handler for versioned execution
        4. Store registration
        """
        pass

    async def query(
        self,
        state: AgentState,
        env: Environment,
        budget: int = 5,  # Max skills to inject
    ) -> list[SkillRegistration]:
        """
        Query for skills available in this state-environment.

        Uses:
        - Activation condition matching
        - Semantic similarity to state
        - Environment feature matching
        - Galois loss ranking

        Returns top `budget` skills, sorted by relevance.
        """
        pass
```

### The Injector Service

```python
# services/jsi/injector.py

class SkillInjector:
    """
    Injects skills into agent context Just-In-Time.

    This service is called by the agent runtime before each decision point.
    """

    def __init__(
        self,
        registry: SkillRegistry,
        naming_registry: MetaEpistemicNamingRegistry,
    ):
        self._registry = registry
        self._naming = naming_registry

    async def inject(
        self,
        agent: PolyAgent,
        state: AgentState,
        env: Environment,
        context_budget: int = 500,  # Token budget for injected skills
    ) -> InjectionResult:
        """
        Inject relevant skills into agent context.

        Returns:
            InjectionResult with:
            - injected_skills: Skills added to context
            - context_addition: Formatted text for system prompt
            - binding_quality: Galois loss estimate for the injection
        """
        # Query available skills
        available = await self._registry.query(state, env)

        # Select skills that fit in context budget
        selected = self._select_within_budget(available, context_budget)

        # Format as context injection
        context_addition = self._format_injection(selected)

        # Estimate binding quality
        binding_quality = await self._estimate_binding_quality(
            selected, state, env
        )

        return InjectionResult(
            injected_skills=selected,
            context_addition=context_addition,
            binding_quality=binding_quality,
        )

    def _format_injection(
        self,
        skills: list[SkillRegistration],
    ) -> str:
        """
        Format skills for injection into system prompt.

        Uses LLM-optimized names, not full descriptions.
        """
        if not skills:
            return ""

        lines = ["## Available Skills (JIT)"]
        for skill in skills:
            # Use LLM-optimized name
            llm_name = skill.name.llm_token
            # Brief trigger hint
            hint = skill.activation_conditions.trigger_hint
            lines.append(f"- `{llm_name}`: {hint}")

        return "\n".join(lines)
```

### Integration with AGENTESE

JIT skills expose themselves via AGENTESE paths:

```python
# Example AGENTESE integration
@node(
    "self.skills.jit",
    description="JIT-injected skills for current state",
    aspects=("manifest", "invoke", "query"),
    context=AGENTESEContext.SELF,
    dependencies=("skill_injector", "skill_registry"),
)
class JITSkillsNode(BaseLogosNode):
    """
    AGENTESE node for accessing JIT skills.

    Paths:
    - self.skills.jit:manifest → List available JIT skills
    - self.skills.jit:invoke → Invoke a JIT skill by name
    - self.skills.jit:query → Query skills for given state
    """
    pass
```

---

## The Stigmergic HYDRATE Pattern

### Progressive Disclosure via State

The HYDRATE.md pattern is formalized as **stigmergic skill discovery**:

```python
class StigmergicDiscovery:
    """
    Skills leave traces (stigmergy) that guide future discovery.

    When a skill is successfully used:
    1. Its usage is recorded
    2. The state-env conditions are indexed
    3. Future similar states find this skill more easily

    This is emergent, opt-in progressive disclosure.
    """

    async def record_usage(
        self,
        skill: SkillRegistration,
        state: AgentState,
        env: Environment,
        success: bool,
    ):
        """Record skill usage for stigmergic learning."""
        trace = StigmergicTrace(
            skill_id=skill.name.llm_token,
            state_features=extract_features(state),
            env_features=extract_features(env),
            success=success,
            timestamp=datetime.utcnow(),
        )
        await self._store_trace(trace)

    async def discover(
        self,
        state: AgentState,
        env: Environment,
    ) -> list[StigmergicSuggestion]:
        """
        Discover skills via accumulated traces.

        Skills that succeeded in similar states are ranked higher.
        """
        features = extract_features(state) + extract_features(env)

        # Query traces for similar features
        similar_traces = await self._query_similar(features)

        # Rank by success rate
        suggestions = self._rank_by_success(similar_traces)

        return suggestions
```

### The Linear Lattice as Initial State

The "linear lattice" Kent mentions is the initial, simple structure:

```
LEVEL 0: Basic skills (shoveling, editing, searching)
         ↓
LEVEL 1: Composition skills (pipeline, parallel)
         ↓
LEVEL 2: Meta skills (reflection, optimization)
         ↓
LEVEL 3: Philosophical skills (dialectic, voodoo-metaphysics)
```

JIT injection moves from Level 0 up as agent state complexity increases.

---

## Connection to Theory

### Chapter 14 (Binding) Connection

The Meta-Epistemic Naming Protocol directly addresses the binding problem:

> "Neural networks struggle with novel variable binding. But they excel at pattern completion."

**Solution**: Names are chosen to be **familiar patterns** that reliably trigger correct LLM behavior, even if the concepts are novel.

### Chapter 11 (Meta-DP) Connection

JIT skill injection is a form of **self-improvement**:

> "The agent modifies its own capabilities based on state."

But crucially, the injection is **grounded in the Constitution**:
- Skills must be Ethical (no injection of harmful capabilities)
- Skills must be Composable (injected skills satisfy operad laws)
- Skills must be Tasteful (only relevant skills are injected)

### Chapter 20 (Open Problems) Connection

This proposal addresses several open problems:

| Problem | How JSI Addresses |
|---------|-------------------|
| **20.A: Softness Problem** | LLM-optimized names reduce binding softness |
| **20.13: Binding Gap** | Stigmergic learning calibrates to actual binding capacity |
| **20.15: Optimal Dialectical Protocols** | Skill injection adapts to dialectic phase |

---

## Integration

### AGENTESE Paths

```
self.skills.jit.manifest         → List available JIT skills
self.skills.jit.invoke           → Invoke a skill
self.skills.jit.history          → View stigmergic traces
concept.naming.meta-epistemic    → Access naming registry
void.entropy.skill-explore       → Exploratory skill discovery
```

### Composition with Existing Agents

JIT skills compose with any PolyAgent:

```python
# Any PolyAgent can receive JIT skills
augmented_citizen = universal_binder.bind_to_agent(
    CITIZEN_POLYNOMIAL,
    skill_registry,
)

# Skills are additive, not replacing
# Original citizen behavior preserved
# Skills available when state-env conditions met
```

### Laws That Must Hold

| Law | Requirement | Verification |
|-----|-------------|--------------|
| **Evocation Determinism** | Same state-env → same skills | Property test |
| **Composition Associativity** | (a ∘ b) ∘ c = a ∘ (b ∘ c) | Law verification |
| **Proxy Transparency** | Proxied skill = delegated execution | Integration test |
| **Constitutional Alignment** | All injected skills pass 7 principles | Runtime check |

---

## Examples

### Example 1: Dialectical Skill Injection

```python
# Agent is in CONTRADICTING state (from dialectic flow)
# Environment contains thesis-antithesis pair

state = AgentState(phase=DialecticPhase.CONTRADICTING)
env = Environment(
    context={"thesis": "Use microservices", "antithesis": "Keep monolith"},
)

# JIT: DIALECTIC_SUBLATE skill is automatically available
injected = await injector.inject(agent, state, env)

# Result includes:
# - skill: DIALECTIC_SUBLATE
# - trigger: "You have thesis-antithesis tension, sublation available"
# - name: "DIALECTIC_SUBLATE" (LLM-optimized, triggers Hegelian patterns)
```

### Example 2: Stigmergic Progressive Disclosure

```python
# Session 1: User asks about "weird metaphysics"
# Agent doesn't know to use VOODOO_METAPHYSICS skill

# Session 5: Similar question, previous successes logged
discovery = await stigmergic.discover(state, env)
# Result: VOODOO_METAPHYSICS suggested (stigmergic trace matched)

# The skill wasn't in the original prompt; it emerged from usage patterns
```

---

## Anti-patterns

| Anti-pattern | Problem | The Right Way |
|--------------|---------|---------------|
| **Enumerate all skills upfront** | Context bloat, irrelevant skills | JIT inject only relevant skills |
| **Human-readable skill names only** | Weak LLM binding | LLM-optimized names with human parsing |
| **Fixed skill sets per agent type** | Brittleness | State-driven skill availability |
| **Skills without composition laws** | Cannot reason about skill combinations | Operad-verified composition |
| **Injection without constitutional check** | Potentially harmful skills | Every injection passes 7 principles |

---

## Research Questions

1. **Optimal naming strategies**: What token patterns maximize LLM binding fidelity?
2. **Stigmergic learning rates**: How fast should skill rankings adapt?
3. **Context budget allocation**: Given N tokens, which skills give best ROI?
4. **Cross-agent skill transfer**: Can skills learned in one PolyAgent help another?
5. **Galois loss of skill composition**: How does composition affect binding quality?

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Skill invocation accuracy** | > 85% | Correct skill invoked when applicable |
| **Context reduction** | > 50% | Tokens saved vs enumeration |
| **Binding loss** | < 0.2 | Galois loss of skill names |
| **Stigmergic convergence** | < 10 sessions | Useful patterns emerge |
| **Constitutional compliance** | 100% | No principle violations |

---

## Next Steps

1. **Implement SkillRegistry** with basic activation conditions
2. **Develop naming strategy benchmarks** (test LLM binding)
3. **Integrate with PolyAgent runtime** (augmented transitions)
4. **Build stigmergic storage** (traces, indexing)
5. **Connect to AGENTESE** (node registration)
6. **Pilot: trail-to-crystal** (first JIT skills for productivity domain)

---

*"The skill doesn't wait to be called. The state evokes the skill."*

---

**Document Metadata**
- **Lines**: ~550
- **Status**: Proposal
- **Theory Basis**: Chapters 11, 14, 20
- **Constitutional Alignment**: Composable, Generative, Tasteful
- **Created**: 2025-12-26
