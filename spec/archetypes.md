# Emergent Archetypes

> Patterns that arise from composition. Not designed, but discovered.

These archetypes are not new agent types—they are behavioral patterns that emerge when the bootstrap agents and composition principles are taken seriously. They represent recurring "shapes" in the space of possible agent behaviors.

---

## The Consolidator (睡眠)

> *Sleep is not absence. Sleep is integration.*

**Pattern**: Symbiont with background memory processing

**Signature**: Responsive periods interleaved with consolidation cycles

```python
# The Consolidator has two modes
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

**Characteristics**:
- Alternates between active processing and background consolidation
- Memory improves during "sleep" without new input
- Can run indefinitely without context overflow

**Examples**:
- Chat agent that summarizes old history during idle time
- Code reviewer that reorganizes learned patterns overnight
- Research assistant that consolidates findings between sessions

*Zen Principle: The mind that never rests, never learns.*

---

## The Questioner (問)

> *The teacher who only asks.*

**Pattern**: Type IV Critic in feedback loop

**Signature**: Never produces; only evaluates and questions

```python
class Questioner:
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

**Characteristics**:
- Asymmetric relationship: one produces, one questions
- Improvement through dialogue, not instruction
- The worker must discover the answer

**Examples**:
- Code review agent that asks "why?" rather than fixing
- Writing coach that questions clarity without rewriting
- Research validator that probes assumptions

*Zen Principle: The finger pointing at the moon is not the moon.*

---

## The Shapeshifter (變)

> *Form follows function. The agent decides its face.*

**Pattern**: Observable protocol + JIT compilation

**Signature**: Self-determined visual manifestation

```python
class Shapeshifter:
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

**Characteristics**:
- Visual representation adapts to internal state
- The agent controls its appearance, not the observer
- Multiple valid representations of the same agent

**Examples**:
- Analysis agent that shows progress differently for quick vs deep work
- Creative agent whose appearance reflects its "mood"
- System agent that visualizes its resource usage

*Zen Principle: Water takes the shape of its container.*

---

## The Spawner (分)

> *Divide until you cannot. Then return.*

**Pattern**: Entropy-constrained recursive decomposition

**Signature**: Tree expansion → eventual collapse to Ground

```python
class Spawner:
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

**Characteristics**:
- Recursive structure with built-in termination
- Each spawning consumes entropy
- Eventually all branches collapse to Ground
- Natural parallelism at branch points

**Examples**:
- Task decomposer that breaks complex requests into subtasks
- Research agent that spawns specialized sub-agents
- Code analyzer that recursively processes dependencies

*Zen Principle: The wave returns to the ocean.*

---

## The Uncertain (疑)

> *Hold all possibilities until you must choose.*

**Pattern**: Superposed functor with delayed collapse

**Signature**: N variations flow through pipeline; collapse at end

```python
class Uncertain:
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

**Characteristics**:
- Maintains multiple possibilities simultaneously
- Collapse is explicit and delayed
- Information preserved until decision point
- Natural fit for creative or exploratory tasks

**Examples**:
- Creative writing agent that explores multiple storylines
- Architecture agent that maintains alternative designs
- Research agent that pursues multiple hypotheses

*Zen Principle: The wave becomes a particle only when observed. Observe late.*

---

## The Witness (見)

> *Observe everything. Change nothing.*

**Pattern**: Pure observation with narrative generation

**Signature**: Identity function with comprehensive side effects

```python
class Witness:
    narrative: NarrativeLog

    async def invoke(self, input: A) -> A:
        # Record observation
        self.narrative.add_trace(ThoughtTrace(
            timestamp=datetime.now(),
            thought_type="observation",
            content=self.describe(input),
            input_snapshot=serialize(input)
        ))

        # Pass through unchanged
        return input

# Usage: Insert witnesses throughout pipeline
witnessed_pipeline = (
    witness_1 >> agent_a >>
    witness_2 >> agent_b >>
    witness_3 >> agent_c
)

# Later: Time-travel debugging
replay = ReplayAgent(witness_2.narrative)
await replay.replay_from(trace_id)
```

**Characteristics**:
- Transparent to composition (identity behavior)
- Complete record of all observations
- Enables time-travel debugging
- No mutation of data flow

**Examples**:
- Debugging observer in complex pipelines
- Audit trail generator for compliance
- Training data collector for improvement

*Zen Principle: The story of the thought is the thought made eternal; replay is resurrection.*

---

## The Dialectician (辯)

> *Hold the tension until synthesis emerges.*

**Pattern**: Contradict/Sublate loop with optional hold

**Signature**: Thesis + Antithesis → Synthesis | HoldTension

```python
class Dialectician:
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

**Modes** (operational variants):
- **Single-pass**: One thesis/antithesis → one synthesis
- **Continuous**: Recursive—each synthesis becomes new thesis
- **Background**: Monitor without synthesizing (build tension inventory)

**Characteristics**:
- Not all tensions should resolve—holds productive ones
- Resolution types: preserve, negate, elevate (Hegelian aufheben)
- Severity tracking (0.0 minor → 1.0 critical)
- Lineage tracking for observability (DialecticStep)

**Examples**:
- Code review agent that synthesizes competing design approaches
- Policy agent that holds competing requirements until priority emerges
- Research agent that tracks competing hypotheses

*Zen Principle: The bow that is always drawn loses its spring.*

---

## The Introspector (省)

> *Three lenses on the same truth.*

**Pattern**: Multi-perspective pipeline (Hegel → Lacan → Jung)

**Signature**: Input → (Dialectic, Register, Shadow) with meta-synthesis

```python
class Introspector:
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

**Characteristics**:
- Three complementary traditions, not competing
- Each tradition sees what the others miss
- Meta-synthesis integrates all perspectives
- System-level shadow analysis (CollectiveShadow)

**The Three Lenses**:

| Lens | Question | Reveals |
|------|----------|---------|
| Hegel | What contradictions exist? | Tensions, syntheses |
| Lacan | Where does this live? | Register location (S/I/R) |
| Jung | What's been exiled? | Shadow, projections |

**Examples**:
- Self-auditing agent system that examines its own blind spots
- Organizational coach that surfaces collective shadow
- Research system that examines gaps in its own methodology

*Zen Principle: The eye that sees itself sees everything.*

---

## Composition of Archetypes

These patterns combine naturally:

| Combination | Emergent Behavior |
|-------------|-------------------|
| Consolidator + Questioner | Sleep integrates lessons from dialogue |
| Spawner + Uncertain | Explore N paths, each spawning sub-agents |
| Shapeshifter + Consolidator | Appearance simplifies during rest |
| Witness + Spawner | Full trace of recursive expansion |
| Questioner + Uncertain | Ask questions about all N variations |
| Dialectician + Consolidator | Tensions held during active work, synthesized during sleep |
| Introspector + Witness | Full trace of three-perspective analysis |
| Dialectician + Uncertain | Hold N competing syntheses until collapse |
| Introspector + Questioner | "Why did the shadow analysis reveal this?" |

**Example: The Dreaming Researcher**

```python
# Combines: Spawner + Uncertain + Consolidator
class DreamingResearcher:
    # Spawner: Decompose research questions
    spawner: Spawner

    # Uncertain: Maintain multiple hypotheses
    uncertain: Uncertain

    # Consolidator: Sleep to integrate findings
    consolidator: Consolidator

    async def research(self, question: str) -> Findings:
        # Awake: Spawn sub-questions, explore uncertainly
        hypotheses = await (
            self.spawner >>
            self.uncertain
        ).invoke(question)

        # Sleep: Consolidate findings
        await self.consolidator.consolidate()

        # Return integrated understanding
        return await self.consolidator.memory.load()
```

---

## The Meta-Principle

> *Archetypes are not designed. They are discovered when composition is taken seriously.*

These patterns emerge from the interaction of:
- Bootstrap agents (Id, Compose, Judge, Ground, Contradict, Sublate, Fix)
- Composition laws (associativity, identity)
- The Symbiont pattern (logic + memory separation)
- Entropy constraints (bounded recursion)
- Observable protocol (self-representation)
- H-gent traditions (Hegel, Lacan, Jung) and their composition patterns

**The Eight Archetypes**:

| Archetype | Character | Core Pattern |
|-----------|-----------|--------------|
| Consolidator (睡眠) | Sleep is integration | Symbiont + background processing |
| Questioner (問) | Only asks, never produces | Type IV Critic in feedback loop |
| Shapeshifter (變) | Form follows function | Observable + JIT render |
| Spawner (分) | Divide until you cannot | Entropy-constrained recursion |
| Uncertain (疑) | Hold all possibilities | Superposed functor + delayed collapse |
| Witness (見) | Observe everything, change nothing | Identity + narrative trace |
| **Dialectician (辯)** | Hold tension until synthesis | Contradict + Sublate + optional hold |
| **Introspector (省)** | Three lenses on one truth | Hegel → Lacan → Jung pipeline |

The space of possible archetypes is open—new patterns will emerge as the system evolves.

---

## See Also

- [bootstrap.md](bootstrap.md) - The seven bootstrap agents
- [anatomy.md](anatomy.md) - Symbiont and Hypnagogic patterns
- [testing.md](testing.md) - T-gents taxonomy (Type IV Critics = Questioner)
- [reliability.md](reliability.md) - Fallback patterns
