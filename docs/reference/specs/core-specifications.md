# Core Specifications

> *The foundational specifications: principles, anatomy, bootstrap process.*

---

## spec.anatomy

## anatomy_of_an_agent

```python
spec Anatomy of an Agent
```

What constitutes an agent in the kgents specification?

### Examples
```python
>>> ┌─────────────────────────────────────┐
│              Agent                  │
│                                     │
│  Input ────→ [Process] ────→ Output │
│                                     │
└─────────────────────────────────────┘
```
```python
>>> Agent[A, B]:
    name: str                     # Identity
    invoke(input: A) -> B         # Behavior
    __rshift__ -> ComposedAgent   # Composition
```
```python
>>> @runtime_checkable
class Observable(Protocol):
    def render_state(self) -> Renderable:
        """Current state visualization."""
        ...

    def render_thought(self) -> Renderable:
        """In-progress reasoning visualization."""
        ...
```
```python
>>> Symbiont[I, O, S]:
    logic: (Input, State) → (Output, NewState)  # Pure
    memory: DataAgent[S]                         # Stateful

    invoke(I) -> O:
        state = await memory.load()
        output, new_state = logic(input, state)
        await memory.save(new_state)
        return output
```
```python
>>> HypnagogicSymbiont[I, O, S]:
    logic: (Input, State) → (Output, NewState)       # Awake state
    memory: DataAgent[S]                              # Shared storage
    consolidator: (State) → State                     # Sleep state (optional)

    # While logic is idle, consolidator can act on memory
    async def consolidate():
        state = await memory.load()
        compressed = consolidator(state)
        await memory.save(compressed)
```

---

## definition

```python
spec Anatomy of an Agent: Definition
```

This definition is deliberately minimal. An agent is not: - Required to use a particular LLM - Required to have memory - Required to use tools - Required to be "intelligent"

---

## the_compositional_core

```python
spec Anatomy of an Agent: The Compositional Core
```

The minimal agent is defined by THREE properties, not operations:

### Examples
```python
>>> Agent[A, B]:
    name: str                     # Identity
    invoke(input: A) -> B         # Behavior
    __rshift__ -> ComposedAgent   # Composition
```

---

## agent_components

```python
spec Anatomy of an Agent: Agent Components
```

Agents MAY include these components:

---

## composition

```python
spec Anatomy of an Agent: Composition
```

The key property that distinguishes kgents agents from arbitrary functions:

### Examples
```python
>>> Agent A: Input_A → Output_A
Agent B: Input_B → Output_B

If Output_A is compatible with Input_B:
  A ∘ B: Input_A → Output_B
```

---

## anti_anatomy_what_an_agent_is_not

```python
spec Anatomy of an Agent: Anti-Anatomy: What An Agent Is Not
```

- **Not a chatbot**: Agents don't require conversational interface - **Not a tool**: Tools are used *by* agents; agents are not tools themselves - **Not a prompt**: A prompt may configure an agent; it is not the agent - **Not a model**: LLMs may power agents; they are not agents themselves - **Not omniscient**: Agents have bounded knowledge and capability

---

## spec.archetypes

## emergent_archetypes

```python
spec Emergent Archetypes
```

Patterns that arise from composition. Not designed, but discovered.

### Examples
```python
>>> # The Consolidator has two modes
class Consolidator:
    logic: Agent[Input, Output]         # Awake mode
    memory: DataAgent[State]            # Shared storage
    consolidator: Agent[State, State]   # Sleep mode

    # Awake: Handle requests
    async def invoke(self, input: Input) -> Output:
        state = await self.memory.load()
        output, new_state = await self.logic.invoke((input, state))
        await self.memory.save(new_state)
        return output

    # Asleep: Compress and reorganize
    async def consolidate(self):
        state = await self.memory.load()
        compressed = await self.consolidator.invoke(state)
        await self.memory.save(compressed)
```
```python
>>> class Questioner:
    judge: Agent[Output, Verdict]

    async def refine(self, worker: Agent, input: Input) -> Output:
        while True:
            output = await worker.invoke(input)
            verdict = await self.judge.invoke(output)

            if verdict.satisfied:
                return output

            # The Questioner never produces—only questions
            input = RefinementRequest(
                original=input,
                attempt=output,
                question=verdict.question,  # "Why did you choose X?"
                hint=verdict.hint           # "Consider Y instead"
            )
```
```python
>>> class Shapeshifter:
    inner: Agent[A, B]

    # The agent decides how it appears
    def render_state(self) -> Renderable:
        state = self.get_current_state()

        match state.phase:
            case "thinking":
                return ThinkingGlyph(intensity=state.depth)
            case "working":
                return ProgressBar(percent=state.progress)
            case "complete":
                return ResultCard(summary=state.output)
            case "error":
                return ErrorPanel(message=state.error)

    def render_thought(self) -> Renderable:
        # Stream current reasoning
        return ThoughtStream(self.current_reasoning)
```
```python
>>> class Spawner:
    decomposer: Agent[Task, list[SubTask]]
    executor: Agent[SubTask, Result]
    aggregator: Agent[list[Result], FinalResult]

    async def invoke(self, task: Task, entropy: EntropyBudget) -> FinalResult:
        # Check if we can still spawn
        if not entropy.can_afford(SPAWN_COST):
            return Ground()  # Collapse to safe fallback

        # Classify the task
        reality = await self.classify(task, entropy)

        if reality == DETERMINISTIC:
            # Leaf node: execute directly
            return await self.executor.invoke(task)

        elif reality == PROBABILISTIC:
            # Branch: decompose and recurse
            subtasks = await self.decomposer.invoke(task)
            child_budgets = entropy.split(len(subtasks))

            results = await asyncio.gather(*[
                self.invoke(sub, budget)
                for sub, budget in zip(subtasks, child_budgets)
            ])

            return await self.aggregator.invoke(results)

        else:  # CHAOTIC
            # Entropy depleted or task unbounded
            return Ground()
```
```python
>>> class Uncertain:
    n: int = 3  # Number of variations to maintain

    async def invoke(self, input: A) -> Superposition[B]:
        # Generate N variations
        variations = await asyncio.gather(*[
            self.inner.invoke(input)
            for _ in range(self.n)
        ])

        return Superposition(variations)

# Usage: Compose uncertain agents, collapse at end
pipeline = (
    Uncertain(brainstorm, n=3) >>
    Uncertain(draft, n=2) >>       # 3 × 2 = 6 variations
    Uncertain(refine, n=1) >>      # Still 6 variations
    Collapse(judge)                 # Now select one
)
```

---

## the_consolidator_睡眠

```python
spec Emergent Archetypes: The Consolidator (睡眠)
```

**Pattern**: Symbiont with background memory processing

---

## the_questioner_問

```python
spec Emergent Archetypes: The Questioner (問)
```

**Pattern**: Type IV Critic in feedback loop

### Examples
```python
>>> class Questioner:
    judge: Agent[Output, Verdict]

    async def refine(self, worker: Agent, input: Input) -> Output:
        while True:
            output = await worker.invoke(input)
            verdict = await self.judge.invoke(output)

            if verdict.satisfied:
                return output

            # The Questioner never produces—only questions
            input = RefinementRequest(
                original=input,
                attempt=output,
                question=verdict.question,  # "Why did you choose X?"
                hint=verdict.hint           # "Consider Y instead"
            )
```

---

## the_shapeshifter_變

```python
spec Emergent Archetypes: The Shapeshifter (變)
```

**Pattern**: Observable protocol + JIT compilation

### Examples
```python
>>> class Shapeshifter:
    inner: Agent[A, B]

    # The agent decides how it appears
    def render_state(self) -> Renderable:
        state = self.get_current_state()

        match state.phase:
            case "thinking":
                return ThinkingGlyph(intensity=state.depth)
            case "working":
                return ProgressBar(percent=state.progress)
            case "complete":
                return ResultCard(summary=state.output)
            case "error":
                return ErrorPanel(message=state.error)

    def render_thought(self) -> Renderable:
        # Stream current reasoning
        return ThoughtStream(self.current_reasoning)
```

---

## the_spawner_分

```python
spec Emergent Archetypes: The Spawner (分)
```

**Pattern**: Entropy-constrained recursive decomposition

### Examples
```python
>>> class Spawner:
    decomposer: Agent[Task, list[SubTask]]
    executor: Agent[SubTask, Result]
    aggregator: Agent[list[Result], FinalResult]

    async def invoke(self, task: Task, entropy: EntropyBudget) -> FinalResult:
        # Check if we can still spawn
        if not entropy.can_afford(SPAWN_COST):
            return Ground()  # Collapse to safe fallback

        # Classify the task
        reality = await self.classify(task, entropy)

        if reality == DETERMINISTIC:
            # Leaf node: execute directly
            return await self.executor.invoke(task)

        elif reality == PROBABILISTIC:
            # Branch: decompose and recurse
            subtasks = await self.decomposer.invoke(task)
            child_budgets = entropy.split(len(subtasks))

            results = await asyncio.gather(*[
                self.invoke(sub, budget)
                for sub, budget in zip(subtasks, child_budgets)
            ])

            return await self.aggregator.invoke(results)

        else:  # CHAOTIC
            # Entropy depleted or task unbounded
            return Ground()
```

---

## the_uncertain_疑

```python
spec Emergent Archetypes: The Uncertain (疑)
```

**Pattern**: Superposed functor with delayed collapse

---

## the_witness_見

```python
spec Emergent Archetypes: The Witness (見)
```

**Pattern**: Pure observation with narrative generation

---

## the_dialectician_辯

```python
spec Emergent Archetypes: The Dialectician (辯)
```

**Pattern**: Contradict/Sublate loop with optional hold

### Examples
```python
>>> class Dialectician:
    contradict: Agent[Pair, Tension | None]
    sublate: Agent[Tension, Synthesis | HoldTension]

    async def invoke(self, thesis: A, antithesis: B) -> DialecticOutput:
        # Detect tension
        tension = await self.contradict.invoke((thesis, antithesis))
        if tension is None:
            return DialecticOutput(synthesis=thesis, productive_tension=False)

        # Attempt synthesis (or hold)
        result = await self.sublate.invoke(tension)
        if isinstance(result, HoldTension):
            return DialecticOutput(
                synthesis=None,
                productive_tension=True,
                held=result.why_held,
            )

        return DialecticOutput(
            synthesis=result.result,
            productive_tension=False,
            sublation_notes=result.explanation,
        )
```

---

## the_introspector_省

```python
spec Emergent Archetypes: The Introspector (省)
```

**Pattern**: Multi-perspective pipeline (Hegel → Lacan → Jung)

### Examples
```python
>>> class Introspector:
    hegel: DialecticianAgent    # What contradictions exist?
    lacan: RegisterAnalyzer     # Where does this live in the registers?
    jung: ShadowAnalyzer        # What has been exiled?

    async def invoke(self, input: IntrospectionInput) -> IntrospectionOutput:
        # Step 1: Dialectic analysis
        dialectic = await self.hegel.invoke(input.thesis, input.antithesis)

        # Step 2: Register analysis (Symbolic/Imaginary/Real)
        register = await self.lacan.invoke(
            dialectic.synthesis or dialectic.sublation_notes
        )

        # Step 3: Shadow analysis
        shadow = await self.jung.invoke(
            system_self_image=input.self_image,
            behavioral_patterns=register.gaps,
        )

        # Step 4: Meta-synthesis
        return IntrospectionOutput(
            dialectic=dialectic,
            register_analysis=register,
            shadow_analysis=shadow,
            meta_notes=self._integrate(dialectic, register, shadow),
        )

    def _integrate(self, d, r, s) -> str:
        """What do all three perspectives reveal together?"""
        ...
```

---

## composition_of_archetypes

```python
spec Emergent Archetypes: Composition of Archetypes
```

These patterns combine naturally:

---

## the_meta_principle

```python
spec Emergent Archetypes: The Meta-Principle
```

These patterns emerge from the interaction of: - Bootstrap agents (Id, Compose, Judge, Ground, Contradict, Sublate, Fix) - Composition laws (associativity, identity) - The Symbiont pattern (logic + memory separation) - Entropy constraints (bounded recursion) - Observable protocol (self-representation) - H-gent traditions (Hegel, Lacan, Jung) and their composition patterns

---

## archetypes_as_flux_configurations

```python
spec Emergent Archetypes: Archetypes as Flux Configurations
```

The eight archetypes are **instantiations of the Flux functor** with specific configurations.

---

## see_also

```python
spec Emergent Archetypes: See Also
```

- [bootstrap.md](bootstrap.md) - The seven bootstrap agents - [anatomy.md](anatomy.md) - Symbiont and Hypnagogic patterns - [testing.md](testing.md) - T-gents taxonomy (Type IV Critics = Questioner) - [reliability.md](reliability.md) - Fallback patterns - [agents/flux.md](agents/flux.md) - Flux Functor specification

---

## spec.bootstrap

## bootstrap_agents

```python
spec Bootstrap Agents
```

The irreducible kernel from which all of kgents can be regenerated.

### Examples
```python
>>> BootstrapWitness:
    verify_bootstrap() -> BootstrapVerificationResult:
        - all_agents_exist: bool    # All 7 importable
        - identity_laws_hold: bool  # Id >> f ≡ f ≡ f >> Id
        - composition_laws_hold: bool  # Associativity
        - overall_verdict: Verdict
```
```python
>>> Id: A → A
Id(x) = x
```
```python
>>> Compose: (Agent, Agent) → Agent
Compose(f, g) = g ∘ f
```
```python
>>> Judge: (Agent, Principles) → Verdict
Judge(agent, principles) = {accept, reject, revise(how)}
```
```python
>>> Ground: Void → Facts
Ground() = {Kent's preferences, world state, initial conditions}
```

### Things to Know

⚠️ **Note:** Anti-pattern: ❌ Unbounded history accumulation in Fix (use bounded/sampled history)

⚠️ **Note:** Anti-pattern: ❌ Sequential execution of independent checks (parallelize Judge/Contradict)

⚠️ **Note:** Anti-pattern: ❌ Re-computing static Ground data (cache persona seed)

⚠️ **Note:** Anti-pattern: ❌ Deep composition chains without flattening (use flatten() for debugging)

⚠️ **Note:** Anti-pattern: ✅ Ground caching (v1.0+): cache=True parameter

⚠️ **Note:** Anti-pattern: ✅ Judge parallelization (v1.0+): parallel=True parameter

⚠️ **Note:** Anti-pattern: ⏳ Bounded Fix history: Future enhancement

⚠️ **Note:** Anti-pattern: ⏳ Id composition optimization: Future enhancement

---

## implementation_status_2025_12_16

```python
spec Bootstrap Agents: Implementation Status (2025-12-16)
```

The bootstrap spec defines **what** the agents are. The implementation is now distributed:

---

## the_bootstrap_problem

```python
spec Bootstrap Agents: The Bootstrap Problem
```

Recursion amplifies. Composition builds. Dialectic synthesizes. But each of these operations requires something to operate *on* and something to guide *when to stop*. The bootstrap agents are what remains when you strip away everything that can be derived.

---

## the_irreducibility_criterion

```python
spec Bootstrap Agents: The Irreducibility Criterion
```

An agent is **irreducible** if it cannot be: 1. Composed from other agents 2. Derived by recursion from simpler rules 3. Synthesized as the dialectic of existing elements 4. Generated by applying existing agents to existing data

---

## why_flux_is_not_a_bootstrap_agent

```python
spec Bootstrap Agents: Why Flux Is Not a Bootstrap Agent
```

**Question**: Should Flux be added to the bootstrap as the eighth irreducible agent?

### Examples
```python
>>> Flux(agent) ≅ Fix(
    transform=lambda stream: map_async(agent.invoke, stream),
    equality_check=lambda s1, s2: s1.exhausted and s2.exhausted
)
```

---

## performance_considerations

```python
spec Bootstrap Agents: Performance Considerations
```

The bootstrap agents are designed for correctness and composability first, performance second. However, certain patterns emerge from production use:

---

## generation_rules

```python
spec Bootstrap Agents: Generation Rules
```

From the seven bootstrap agents, all of kgents can be regenerated:

---

## self_description

```python
spec Bootstrap Agents: Self-Description
```

Can the bootstrap agents describe themselves?

### Examples
```python
>>> Bootstrap = {Id, Compose, Judge, Ground, Contradict, Sublate, Fix}

Is Bootstrap irreducible?
  = ¬∃S ⊂ Bootstrap. Generate(S) = Bootstrap

Is Bootstrap sufficient?
  = ∀A ∈ Kgents. ∃derivation. Bootstrap ⊢ A
```
```python
>>> Regenerate(Bootstrap) ≅ Bootstrap
```

---

## relationship_to_existing_spec

```python
spec Bootstrap Agents: Relationship to Existing Spec
```

| Bootstrap Agent | Primary Manifestation | Distributed Across | |-----------------|----------------------|-------------------| | Id | A-gents (identity agent) | All (composition unit) | | Compose | C-gents (composition.md) | All (composition is universal) | | Judge | Principles (principles.md) | All (every agent is judged) | | Ground | K-gent (persona.md) | B-gents (empirical data) | | Contradict | H-gents (pre-dialectic) | All (consistency checking) | | Sublate | H-hegel (hegel.md) | All (syst

---

## the_minimal_bootstrap

```python
spec Bootstrap Agents: The Minimal Bootstrap
```

If forced to choose the **absolute minimum**:

### Examples
```python
>>> MinimalBootstrap = {Compose, Judge, Ground}
```

---

## usage_regenerating_kgents

```python
spec Bootstrap Agents: Usage: Regenerating Kgents
```

To regenerate the project from bootstrap:

---

## applied_idioms

```python
spec Bootstrap Agents: Applied Idioms
```

The bootstrap agents are abstract. When applied to real systems, recurring patterns emerge. These idioms are not new agents—they are the seven agents in action.

---

## open_questions

```python
spec Bootstrap Agents: Open Questions
```

1. **Is Judge truly one agent or six?** The principles might be separately irreducible.

---

## see_also

```python
spec Bootstrap Agents: See Also
```

- [principles.md](principles.md) - Judge's criteria - [anatomy.md](anatomy.md) - What agents are - [agents/composition.md](agents/composition.md) - Compose formalized - [h-gents/hegel.md](h-gents/hegel.md) - Sublate in detail - [k-gent/persona.md](k-gent/persona.md) - Ground's primary output - `AUTONOMOUS_BOOTSTRAP_PROTOCOL.md` - Post-mortem and anti-patterns

---

## spec.principles

## design_principles

```python
spec Design Principles
```

These seven principles guide all kgents design decisions.

### Examples
```python
>>> # Traditional composition (Python)
pipeline = AgentA >> AgentB >> AgentC

# AGENTESE composition (paths)
pipeline = (
    logos.lift("world.document.manifest")
    >> logos.lift("concept.summary.refine")
    >> logos.lift("self.memory.engram")
)
```
```python
>>> # Path 1: Careful Design (intentional)
pipeline = soul_operad.compose(["ground", "introspect", "shadow", "dialectic"])

# Path 2: Chaotic Happenstance (void.* entropy)
pipeline = await void.compose.sip(
    primitives=PRIMITIVES,
    grammar=soul_operad,
    entropy=0.7
)
```
```python
>>> ┌─────────────────────────────────────────────────────┐
│                    AUTONOMOUS LOOP                  │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐      │
│   │ Perceive│ ──→ │  Act    │ ──→ │Feedback │ ─┐   │
│   └─────────┘     └─────────┘     └─────────┘  │   │
│        ▲                                       │   │
│        └───────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                        ↕ (can be interrupted/composed)
┌─────────────────────────────────────────────────────┐
│                   FUNCTIONAL MODE                   │
│        Input ────→ [Transform] ────→ Output         │
└─────────────────────────────────────────────────────┘
```
```python
>>> Static:  Agent: A → B           (a point transformation)
Dynamic: Flux(Agent): dA/dt → dB/dt  (a continuous flow)
```
```python
>>> Spec → Impl → Test → Validate → Spec (refined)
```

### Things to Know

⚠️ **Note:** Anti-pattern: Agents that do "everything"

⚠️ **Note:** Anti-pattern: Kitchen-sink configurations

⚠️ **Note:** Anti-pattern: Agents added "just in case"

---

## 1_tasteful

```python
spec Design Principles: 1. Tasteful
```

- **Say "no" more than "yes"**: Not every idea deserves an agent - **Avoid feature creep**: An agent does one thing well - **Aesthetic matters**: Interface and behavior should feel considered - **Justify existence**: Every agent must answer "why does this need to exist?"

---

## 2_curated

```python
spec Design Principles: 2. Curated
```

**Heritage Citation (TextGRAD):** The TextGRAD approach treats natural language feedback as "textual gradients" for improvement. Gradual refinement preserves quality—prompts improve incrementally, not through wholesale replacement. kgents' `rigidity` field (0.0-1.0) controls how much a section can change per improvement step, embodying curation through controlled evolution. See `spec/heritage.md` §9.

---

## 3_ethical

```python
spec Design Principles: 3. Ethical
```

- **Transparency**: Agents are honest about limitations and uncertainty - **Privacy-respecting by default**: No data hoarding, no surveillance - **Human agency preserved**: Critical decisions remain with humans - **No deception**: Agents don't pretend to be human unless explicitly role-playing

---

## 4_joy_inducing

```python
spec Design Principles: 4. Joy-Inducing
```

- **Personality encouraged**: Agents may have character (within ethical bounds) - **Surprise and serendipity welcome**: Discovery should feel rewarding - **Warmth over coldness**: Interaction should feel like collaboration, not transaction - **Humor when appropriate**: Levity is valuable

---

## 5_composable

```python
spec Design Principles: 5. Composable
```

This principle comes from the [categorical foundations](agents/) and applies to all agents.

---

## 6_heterarchical

```python
spec Design Principles: 6. Heterarchical
```

**Heritage Citation (Meta-Prompting):** The Meta-Prompting paper (arXiv:2311.11482) formalizes self-improvement as a **monad**—a categorical structure with unit, bind, and associativity. This is exactly the self-similar structure kgents uses for PolyAgents, Operads, and Sheaves. The prompt system improves itself via the same structure it implements. See `spec/heritage.md` §8.

---

## 7_generative

```python
spec Design Principles: 7. Generative
```

A well-formed specification captures the essential decisions, reducing implementation entropy. The zen-agents experiment achieved 60% code reduction compared to organic development—proof that spec-first design compresses accumulated wisdom into regenerable form.

---

## the_meta_principle_the_accursed_share

```python
spec Design Principles: The Meta-Principle: The Accursed Share
```

This principle operates ON the seven principles, not alongside them. It derives from Georges Bataille's theory that all systems accumulate surplus energy that must be *spent* rather than conserved.

### Examples
```python
>>> Slop → Filter → Curate → Cherish → Compost → Slop
       ↑                                ↓
       └──────── gratitude ─────────────┘
```

---

## the_meta_principle_agentese_no_view_from_nowhere

```python
spec Design Principles: The Meta-Principle: AGENTESE (No View From Nowhere)
```

AGENTESE is the verb-first ontology that operationalizes this meta-principle. It transforms agent-world interaction from noun-based queries to observer-dependent invocations.

---

## operational_principle_transparent_infrastructure

```python
spec Design Principles: Operational Principle: Transparent Infrastructure
```

This principle applies to all infrastructure work: CLI startup, database initialization, background processes, maintenance tasks.

---

## operational_principle_graceful_degradation

```python
spec Design Principles: Operational Principle: Graceful Degradation
```

Systems should detect their environment and adapt. Q-gent exemplifies this: when Kubernetes is unavailable, it falls back to subprocess execution. The user's code still runs.

---

## operational_principle_spec_driven_infrastructure

```python
spec Design Principles: Operational Principle: Spec-Driven Infrastructure
```

Infrastructure manifests should be derived from specs, not hand-crafted. When `spec/agents/b-gent.md` changes, the CRD, Deployment, and Service regenerate automatically.

### Examples
```python
>>> spec/agents/*.md  →  Generator  →  K8s Manifests  →  Running Pods
```

---

## operational_principle_event_driven_streaming

```python
spec Design Principles: Operational Principle: Event-Driven Streaming
```

This principle governs all agent streaming and asynchronous behavior. Agents that process continuous data should react to events, not poll on timers.

---

## applying_the_principles

```python
spec Design Principles: Applying the Principles
```

When designing or reviewing an agent, ask:

---

## architectural_decisions

```python
spec Design Principles: Architectural Decisions
```

These are binding decisions that shape implementation across kgents.

---

*49 symbols, 11 teaching moments*

*Generated by Living Docs — 2025-12-21*