# Spec Update Proposal: Hegelian Synthesis from Implementation Success

**Date**: 2025-12-09
**Methodology**: Deep analysis of impl/ (~34K lines, 177 files, 14 agent genera) + git history (50+ commits of evolution) + current spec files + research synthesis
**Philosophy**: Preserve original intent EXACTLY while elevating with implementation-validated patterns

---

## The Core Shift: From Design Patterns to Computational Calculus

This proposal represents a **structural breakthrough**: moving from "Design Patterns" (heuristic) to "Category Theory" (mathematical). The kgents framework transforms from a collection of scripts into a **computational calculus**.

The most significant insight: redefining Agent from "Class" to "Morphism."

| Paradigm | Definition | Implication |
|----------|------------|-------------|
| OOP (traditional) | Object defined by internal state + methods | Identity is fundamental |
| Category Theory (kgents) | Object defined by relationships (arrows) | **Interaction is fundamental** |

By defining `>>` (Composition) as the skeleton, we assert that **interaction is more fundamental than identity.**

---

## Executive Summary

The implementation has discovered patterns that deserve elevation to spec-level principles. This proposal synthesizes learnings WITHOUT diluting the original vision. Key discoveries from implementation:

1. **Composition IS the skeleton** - The `>>` operator is not syntactic sugar but THE primary abstraction
2. **Protocols over inheritance** - Optional features via `@runtime_checkable` protocols
3. **Category laws are verifiable** - BootstrapWitness proves laws hold
4. **Multi-layer reliability** - E-gents pattern: prompt → parse → retry → fallback
5. **Symbiont pattern** - Pure logic + stateful memory composition (enables Hypnagogic agents)
6. **Testing as agents** - T-gents taxonomy elevates testing to first-class (Socratic verification)
7. **Entropy as physics** - Reality trichotomy provides constraints for Fractal orchestration
8. **Observable protocol** - W-gent as Functor enables Polymorphic self-rendering

**New theoretical foundations** (Section 6):

9. **Bataille's Accursed Share** - Philosophy of slop; meta-principle; everything is slop or comes from slop
10. **Noether's Theorem** - LLM-native semantic conservation via credo self-reporting and drift detection
11. **Ergodicity** - Ensemble Reset strategy (opt-in for heavy constructions with economic budgets)
12. **Stigmergy** - W-gent as pheromone field with WebSocket/SSE push; **TRANSFORMATIVE** (taints agent purity)
13. **Curry-Howard** - Prompts as Types; structural validity implies semantic validity for LLMs
14. **Free Energy Principle** - Active Inference loop (opt-in); simulate tool call batches before executing
15. **Messenger Protocol** - Streaming Functor: `Agent[A, B] → Agent[A, AsyncIterator[Chunk[B]]]`
16. **View Functor** - Widget ontology; deterministic agent → UI component mapping
17. **Metered Functor** - Central Bank economics; Kelvin circulation theorem; auction mechanics
18. **M-gents** - Holographic associative memory; memory as morphism; ethics as geometry of possibility space
19. **Narrator Agent** - OpenTelemetry for thoughts; time-travel debugging; replay from serialized inputs

---

## 1. spec/README.md Updates

### Current State
The README lists genera (a-k, t, w) and provides reading order. Good but static.

### Proposed Updates

#### 1.1 Add Implementation Validation Section
```markdown
## Implementation Validation

The spec/impl relationship is bidirectional:
- **Spec → Impl**: Specifications prescribe behavior
- **Impl → Spec**: Successful patterns inform specification refinement

See `impl/claude/` for the reference implementation. Key validations:
- All 7 bootstrap agents implemented and law-verified
- 14 agent genera with cross-pollination
- 666+ passing tests validating spec compliance
```

#### 1.2 Expand Reading Order
```markdown
## Reading Order

1. **[principles.md](principles.md)** - Core design principles (start here)
2. **[anatomy.md](anatomy.md)** - What constitutes an agent
3. **[bootstrap.md](bootstrap.md)** - The irreducible kernel (7 agents)
4. **[composition.md](c-gents/composition.md)** - The `>>` operator as primary abstraction *(NEW: elevated from c-gents)*
5. **Agent Genera** - Explore specific agent types:
   ...
```

#### 1.3 Add Cross-Pollination Section
```markdown
## Cross-Pollination Graph

Agents don't exist in isolation. Key integration points:

| Integration | Description |
|-------------|-------------|
| D+E | E-gents use D-gent memory for evolution state |
| J+F | F-gent artifacts can be JIT-instantiated via J-gent |
| T+* | T-gents can test any agent via Spy/Mock patterns |
| K+B | B-gent Robin uses K-gent persona preferences |
| P+T | T-gent Tool parsing uses P-gent strategies |

See `impl/claude/agents/*/` __init__.py files for explicit cross-pollination labels.
```

---

## 2. spec/principles.md Updates

### Current State
Seven principles: Tasteful, Curated, Ethical, Joy-Inducing, Composable, Heterarchical, Generative. Strong foundation.

### Proposed Updates

#### 2.1 Strengthen "Composable" with Category-Theoretic Foundation
**Current** (line 79):
```markdown
- **Associativity holds**: (A ∘ B) ∘ C = A ∘ (B ∘ C)
```

**Proposed addition** after line 80:
```markdown
### Category Laws (Required)

Agents form a category. These laws are not aspirational—they are **verified**:

| Law | Requirement | Verification |
|-----|-------------|--------------|
| Identity | `Id >> f ≡ f ≡ f >> Id` | BootstrapWitness.verify_identity_laws() |
| Associativity | `(f >> g) >> h ≡ f >> (g >> h)` | BootstrapWitness.verify_composition_laws() |

**Implication**: Any agent that breaks these laws is NOT a valid agent.
```

#### 2.2 Add "Orthogonality" Sub-Principle to Composable
After line 106, add:
```markdown
### Orthogonality Principle

Optional features MUST NOT break composition:
- **Metadata is optional**: An agent works with or without `AgentMeta`
- **Protocols are opt-in**: Implementing `Introspectable` doesn't change `invoke()`
- **State is composed**: Symbiont pattern separates pure logic from D-gent memory

**Test**: Can you compose an agent with metadata and one without? If not, violation.
```

#### 2.3 Add Protocol Extension Pattern to Anti-patterns
Update the Composable anti-patterns (after line 106):
```markdown
### Anti-patterns
- Monolithic agents that can't be broken apart
- Agents with hidden state that prevents composition
- "God agents" that must be used alone
- **LLM agents that return arrays of outputs instead of single outputs**
- **Prompts that ask agents to "combine" or "synthesize multiple" results**
- **Inheritance hierarchies that force feature coupling** *(NEW)*
- **Features that only work in isolation** *(NEW)*
```

#### 2.4 Strengthen "Generative" with Verification Pattern
Add after line 175:
```markdown
### The Generative Implementation Cycle

```
Spec → Impl → Test → Validate → Spec (refined)
```

Evidence from codebase:
- **skeleton.py**: ~700 lines derived from 175-line anatomy.md
- **bootstrap/**: 7 agents exactly matching bootstrap.md
- **BootstrapWitness**: Verifies laws hold at runtime

**Metric**: Autopoiesis Score = (lines generated from spec) / (total lines)
Target: >50% for mature implementations.
```

---

## 3. spec/anatomy.md Updates

### Current State
Defines agent as input → process → output. Lists components (Identity, Interface, Behavior, State, Composition Hooks). Covers lifecycle and composition.

### Proposed Updates

#### 3.1 Elevate Composition from Component to Core
**Current** structure implies composition hooks are optional. Synthesis says: Composition IS the skeleton.

**Proposed addition** after line 33:
```markdown
## The Compositional Core

The minimal agent is defined by THREE properties, not operations:

```python
Agent[A, B]:
    name: str                     # Identity
    invoke(input: A) -> B         # Behavior
    __rshift__ -> ComposedAgent   # Composition
```

Composition (`>>`) is not a "hook"—it is constitutive. An entity without `>>` is a function, not an agent.
```

#### 3.2 Add Protocol-Based Extension Section
After line 66 (State section), add:
```markdown
### Extension Protocols (Optional)

Agents MAY implement these protocols for enhanced capabilities:

| Protocol | Method | Purpose |
|----------|--------|---------|
| `Introspectable` | `meta: AgentMeta` | Runtime metadata access |
| `Validatable` | `validate_input(A) -> (bool, str)` | Pre-invocation checks |
| `Composable` | `can_compose_with(Agent) -> (bool, str)` | Composition type checking |
| `Morphism` | (inherits Agent) | Category-theoretic formalization |
| `Functor` | `lift(Agent[A,B]) -> Agent[F[A],F[B]]` | Structure-preserving transforms |
| `Observable` | `render_state() -> Renderable` | Visual sidecar support (W-gent) |

**Design**: Protocols are structurally typed (`@runtime_checkable`). No inheritance required.

**Principle**: Adding a protocol MUST NOT change `invoke()` behavior. Protocols observe, they don't mutate.

### The Observable Protocol (The "Lens")

To support W-gent (Visual Sidecars) without breaking the Orthogonality Principle:

```python
@runtime_checkable
class Observable(Protocol):
    def render_state(self) -> Renderable:
        """Current state visualization."""
        ...

    def render_thought(self) -> Renderable:
        """In-progress reasoning visualization."""
        ...
```

**The Functor Bridge**:
W-gent is a **Lifting Functor** that looks for the `Observable` protocol:
- If `Agent implements Observable`: W-gent calls `render_thought()` and pipes to visualization
- If `Agent is Opaque`: W-gent falls back to `repr(output)`

**The Law**: `Id >> W-gent ≡ Id`. W-gent must be invisible to composition logic.

**Why this matters**: It enables **Polymorphic Agents**. The agent *decides* how it looks (by implementing `render_state`) rather than the observer guessing. This is the categorical home for W-gent—not a "hacky server wrapper" but formally a *Writer Monad* or *Tap*.
```

#### 3.3 Enhance Ephemeral Agents Section with JIT Pattern
Update lines 93-118 (Ephemeral Agents section):
```markdown
### Ephemeral Agents (J-gent Pattern)

Ephemeral agents are:
- **JIT-compiled**: Generated by Meta-Architect from intent
- **Sandboxed**: Executed with restricted permissions
- **Validated**: Must pass JITSafetyJudge before execution
- **Stability-scored**: Chaosmonger analyzes recursion/complexity bounds
- **Transient**: Lifetime limited to task or session
- **Cached**: May be reused if same (intent, context, constraints) hash

**Critical Addition**: Ephemeral agents are STILL agents:
```python
JITAgentWrapper(Agent[A, B]):
    meta: AgentMeta         # Standard introspection
    jit_meta: JITAgentMeta  # Provenance (source, constraints, stability)
    invoke(A) -> B          # Re-executes in sandbox every time
    >>                      # Composes normally
```

Every invoke() re-executes source in sandbox. No cached bytecode.
```

#### 3.4 Add Symbiont Pattern to Stateful Agents
Expand the Stateful Agents section (line 80-85):
```markdown
### Stateful Agents: The Symbiont Pattern

The preferred pattern for stateful agents is **Symbiont**: pure logic + D-gent memory.

```python
Symbiont[I, O, S]:
    logic: (Input, State) → (Output, NewState)  # Pure
    memory: DataAgent[S]                         # Stateful

    invoke(I) -> O:
        state = await memory.load()
        output, new_state = logic(input, state)
        await memory.save(new_state)
        return output
```

**Benefits**:
- Logic is pure, testable in isolation
- State persistence is composable (swap D-gent for different storage)
- Composition preserved: Symbiont IS an Agent[I, O]

**Examples**:
- Chat agent with history: `Symbiont(chat_logic, PersistentAgent(history_file))`
- Counter agent: `Symbiont(lambda n, count: (count+n, count+n), VolatileAgent(0))`

### Extended Symbiont: The Hypnagogic Pattern

The separation of logic and memory is the architectural prerequisite for **background consolidation** (sleep/wake cycles).

```python
HypnagogicSymbiont[I, O, S]:
    logic: (Input, State) → (Output, NewState)       # Awake state
    memory: DataAgent[S]                              # Shared storage
    consolidator: (State) → State                     # Sleep state (optional)

    # While logic is idle, consolidator can act on memory
    async def consolidate():
        state = await memory.load()
        compressed = consolidator(state)
        await memory.save(compressed)
```

**The Insight**: If memory is tightly coupled to logic (as in typical frameworks), you cannot "optimize" memory without stopping logic. By decoupling:
- `logic` is the **Awake State** (handles input)
- `consolidator` is the **Sleep State** (compresses/reorganizes memory)
- Both share `memory` but operate at different times

**Use Cases**:
- Memory consolidation during idle periods
- Background summarization of conversation history
- Garbage collection of stale context
- Learning from accumulated experience

**Hypnagogic Realization**: The "Sleep" cycle is simply a separate Agent process that takes the `DataAgent` as input and outputs a compressed `DataAgent`, while the `Logic` component is blocked or sleeping.
```

---

## 4. spec/bootstrap.md Updates

### Current State
Defines 7 bootstrap agents: Id, Compose, Judge, Ground, Contradict, Sublate, Fix. Rich with generation rules and idioms.

### Proposed Updates

#### 4.1 Add BootstrapWitness to Bootstrap Agents
After line 38 (end of Seven Bootstrap Agents intro), add:
```markdown
### The Eighth Meta-Agent: BootstrapWitness

While not a bootstrap agent itself, **BootstrapWitness** verifies bootstrap integrity:

```python
BootstrapWitness:
    verify_bootstrap() -> BootstrapVerificationResult:
        - all_agents_exist: bool    # All 7 importable
        - identity_laws_hold: bool  # Id >> f ≡ f ≡ f >> Id
        - composition_laws_hold: bool  # Associativity
        - overall_verdict: Verdict
```

**Why include here**: The bootstrap is only valid if its laws can be verified. BootstrapWitness is the proof that the system can self-validate.
```

#### 4.2 Add D-gent/Symbiont to Generation Rules
Update line 277-294 (Generating D-gents section):
```markdown
### Generating D-gents and Symbiont

```
DataAgent = StateInfrastructure  // Infrastructure primitive

Symbiont[I, O, S] = Compose(
    logic: (I, S) → (O, S),      // Pure transformation
    memory: DataAgent[S]          // State monad transformer
) : Agent[I, O]
```

**Key Insight**: Symbiont is derivable from Compose + DataAgent:
- `logic` is a pure function (testable)
- `memory` is a D-gent (composable)
- Result IS an Agent (composable via >>)

**Implementation evidence**: `impl/claude/agents/d/symbiont.py` (~80 lines, matches spec)
```

#### 4.3 Add Functor Composition to Idioms
After Idiom 3 (line 501), add:
```markdown
### Idiom 3.1: Functor Lifting

> Structure-preserving transforms enable clean error handling and context switching.

Functors lift agents to work in different contexts:

| Functor | Transform | Purpose |
|---------|-----------|---------|
| Maybe | `Agent[A,B] → Agent[Maybe[A], Maybe[B]]` | Handle absence |
| Either | `Agent[A,B] → Agent[Either[E,A], Either[E,B]]` | Handle errors |
| List | `Agent[A,B] → Agent[List[A], List[B]]` | Process collections |
| Async | `Agent[A,B] → Agent[A, Future[B]]` | Non-blocking |
| Logged | `Agent[A,B] → Agent[A, B]` + trace | Observability |
| Cooled | `Agent[A,B] → Agent[Compressed[A], B]` | Context limits |
| Superposed | `Agent[A,B] → Agent[A, Superposition[B]]` | Epistemic uncertainty |

**Laws preserved**:
- Identity: `F(id_A) = id_F(A)`
- Composition: `F(g ∘ f) = F(g) ∘ F(f)`

**Example** (from impl):
```python
# Original: f: A → B (may fail)
# Lifted:   Either_f: Either[E, A] → Either[E, B]
# Compose:  Either_f >> Either_g >> Either_h (short-circuits on first error)
```

**Anti-pattern**: Manual null-checking between composition steps.

### Idiom 3.2: The Cooled Functor (Context as Heat)

> Context windows are finite. Context is heat. Cooling prevents degradation.

**The Physics**: LLMs suffer from "context heat"—as conversation grows, logic degrades. This is not a bug; it is thermodynamics.

```python
Cooled[A, B]:
    threshold: int              # Token limit before cooling
    radiator: Agent[A, A]       # Compression agent (summarizer)

    invoke(input: A) -> B:
        if tokens(input) > threshold:
            input = await radiator.invoke(input)  # Compress
        return await inner.invoke(input)
```

**The Wisdom**: The inner agent doesn't know it received compressed data. It sees only a clean, short prompt. This makes agents **stateless in performance**—they can run indefinitely without context overflow.

**Zen Principle**: *The best memory is knowing what to forget.*

### Idiom 3.3: The Superposed Functor (Delayed Collapse)

> When truth is uncertain, hold multiple possibilities. Collapse only when you must.

**The Insight**: Standard orchestration wants one answer. But sometimes an agent has 3 equally valid thoughts. Forcing early choice discards information.

```python
Superposed[A, B]:
    n: int = 3                  # Number of variations to hold

    invoke(input: A) -> Superposition[B]:
        variations = [await inner.invoke(input) for _ in range(n)]
        return Superposition(variations)  # All held, none collapsed

# Collapse happens explicitly, usually via Judge
pipeline = Superposed(brainstorm, n=3) >> Superposed(draft) >> Collapse(judge)
```

**The Structure**:
- **Superposition**: N variations flow through the pipeline in parallel
- **Collapse**: A Judge or User makes final selection at chain end
- **Delayed Choice**: Subsequent agents invoke on *all* variations

**Zen Principle**: *The wave becomes a particle only when observed. Observe late.*

**Anti-pattern**: Forcing choice at every step ("pick the best one") when uncertainty persists.
```

#### 4.4 Strengthen Idiom 7 with RealityClassifier Evidence
Update Idiom 7 (line 503-554) with implementation validation:
```markdown
### Idiom 7: Reality is Trichotomous (Validated)

**Implementation**: `impl/claude/agents/j/reality.py`

| Reality | Detected By | Action |
|---------|-------------|--------|
| DETERMINISTIC | `is_atomic(task)` | Direct execution |
| PROBABILISTIC | `is_complex(task)` | Fix-based iteration |
| CHAOTIC | `is_unbounded(task) or entropy_depleted` | Collapse to Ground |

**Evidence from J-gents**:
```python
RealityClassifier.classify(intent, entropy_budget) -> Reality

if reality == DETERMINISTIC:
    return await execute_atomic(intent)
elif reality == PROBABILISTIC:
    return await fix(decompose)(intent)
else:  # CHAOTIC
    return Ground()  # Safe fallback
```

**Critical**: Entropy budget diminishes: `remaining = budget / (iteration + 1)`
This forces eventual collapse to CHAOTIC, preventing runaway recursion.
```

#### 4.5 Add Entropy as Physics for Fractal Orchestration
After Idiom 7, add new idiom:
```markdown
### Idiom 7.1: Entropy is Physics

> The **Fractal Orchestrator** (recursive sub-agents) is dangerous without physics. Entropy provides the physics.

**The Problem**: Infinite recursion crashes systems. An agent that spawns sub-agents that spawn sub-agents is a fork bomb.

**The Solution**: Entropy Budget as Control Rod

```python
@dataclass
class EntropyBudget:
    initial: float = 1.0
    remaining: float = 1.0

    def consume(self, cost: float) -> bool:
        """Returns False if budget depleted (triggers CHAOTIC collapse)."""
        if self.remaining < cost:
            return False
        self.remaining -= cost
        return True

    def split(self, n: int) -> list["EntropyBudget"]:
        """Split budget among n sub-agents."""
        child_budget = self.remaining / n
        return [EntropyBudget(child_budget, child_budget) for _ in range(n)]
```

**Fractal Dynamics**:

| Phase | Entropy State | Agent Behavior |
|-------|---------------|----------------|
| Expansion | `PROBABILISTIC` | Agent splits into sub-agents |
| Steady State | `PROBABILISTIC` (low) | Agent operates normally |
| Collapse | `CHAOTIC` (depleted) | Swarm collapses to Ground |

**The Law**: `∀ agent. entropy(agent) → 0 ⟹ reality(agent) → CHAOTIC`

Every recursive expansion consumes entropy. Eventually, all agents collapse to Ground (a simple "I don't know" or fallback).

**JIT Integration**: The **Polymorphic Agent** (GenUI) fits here. A JIT agent can compile a UI component on the fly, execute it with entropy budget, and dissolve when budget depletes.

**Anti-patterns**:
- Unbounded recursion without entropy tracking
- Sub-agents that don't inherit parent's entropy constraints
- "Optimistic" orchestration that assumes infinite resources
```

---

## 5. New Section Proposals

### 5.1 spec/testing.md (New File)

Elevate T-gents patterns to specification level:

```markdown
# Testing Agents Specification

## Philosophy

> Testing is not separate from agent design—test agents ARE agents.

Testing agents satisfy all agent principles:
- **Composable**: `spy_agent >> production_agent >> assert_agent`
- **Morphisms**: `SpyAgent: A → A` (identity + side effect)
- **Categorical**: Laws hold for test agents too

**Key Insight**: Testing is usually external to runtime (CI/CD). T-gents move testing *into* the runtime.

## The T-gents Taxonomy

### Type I: Nullifiers (Constants & Fixtures)
- `MockAgent`: Constant output (`A → b`)
- `FixtureAgent`: Deterministic lookup (`key → value`)
- **Purpose**: Replace expensive operations, provide known outputs

### Type II: Saboteurs (Chaos & Perturbation)
- `FailingAgent`: Controlled failures
- `NoiseAgent`: Semantic perturbation
- `LatencyAgent`: Temporal delays
- `FlakyAgent`: Probabilistic failures
- **Purpose**: Test resilience, retry logic, timeouts

### Type III: Observers (Identity + Side Effects)
- `SpyAgent`: Writer monad (observe without mutation)
- `PredicateAgent`: Gate (allow/reject)
- `CounterAgent`: Invocation counting
- **Purpose**: Transparent observation, contract verification

### Type IV: Critics (Semantic Evaluation)
- `JudgeAgent`: LLM-as-judge
- `PropertyAgent`: Property-based testing
- `OracleAgent`: Differential testing
- **Purpose**: High-level correctness, regression detection

## Integration with Reliability Stack

### The Socratic Pattern (Type IV Critics)

Critics enable iterative refinement through questioning:

```python
# Pattern: Worker >> Judge
result = await (worker >> judge_agent).invoke(input)

# If Judge returns feedback, refine and retry
if result.verdict == REVISE:
    input = refine(input, result.feedback)
    result = await worker.invoke(input)
```

**Zen**: The teacher who only asks eventually produces the best student.

### Chaos Testing (Type II Saboteurs)

Saboteurs reveal weakness before production does:

```python
# Attach chaos to test resilience
chaos_test = latency_agent >> noise_agent >> worker

# If worker survives perturbation, it is robust
try:
    result = await chaos_test.invoke(test_input)
    assert is_valid(result)
except:
    # Worker needs strengthening
    pass
```

**Zen**: The sword is tempered by fire, not by rest.

## Test Agent Marker

All test agents MUST declare:
```python
__is_test__ = True
```

This enables:
- Filtering in production vs test code
- Meta-reasoning about test coverage
- Automatic test discovery

## Composition Patterns

```python
# Spy pattern: Observe without mutating
spied = spy_agent >> production_agent
result = await spied.invoke(input)
observations = spy_agent.observations

# Chaos pattern: Test resilience (Darwinian)
chaos = latency_agent >> noise_agent >> production_agent
result = await chaos.invoke(input)  # May fail, may be noisy

# Socratic pattern: Iterative refinement
socratic = worker >> judge_agent
while (result := await socratic.invoke(input)).needs_revision:
    input = result.suggested_refinement

# Property pattern: Verify invariants
for _ in range(100):
    input = generator.generate()
    result = await production_agent.invoke(input)
    assert property.check(input, result)
```
```

### 5.2 spec/reliability.md (New File)

Elevate E-gents multi-layer pattern:

```markdown
# Reliability Patterns Specification

## Philosophy

> Reliability is not a single layer—it's a stack of composable fallbacks.

## The Three-Layer Stack

### Layer 1: Prompt Engineering (Prevention)
- `PreFlightChecker`: Validate module health BEFORE LLM invocation
- `PromptContext`: Rich context (types, errors, patterns)
- **Goal**: Prevent errors by giving LLM better information

### Layer 2: Parsing & Validation (Detection)
- Multi-strategy parsing with fallbacks
- Schema validation (pre-type-checker fast path)
- **Goal**: Detect malformed outputs before they propagate

### Layer 3: Recovery & Learning (Adaptation)
- `RetryStrategy`: Intelligent retry with failure-aware refinement
- `FallbackStrategy`: Progressive simplification
- `ErrorMemory`: Track failure patterns
- **Goal**: Recover gracefully, learn from failures

## Fallback Composition

```
f >> g >> h  // Happy path

// With reliability:
Fix(
    Retry(
        Fallback(f, f_simple),
        max_attempts=3
    ),
    until_stable
) >> g >> h
```

## Anti-patterns
- Single point of failure
- Silent swallowing of errors
- Retry without learning
- Fallback that breaks composition
```

---

### 5.3 spec/archetypes.md (New File - Optional)

Document emergent behavioral patterns with Zen brevity:

```markdown
# Emergent Archetypes

Patterns that arise from composition. Not designed, but discovered.

---

## The Consolidator (睡眠)

*Sleep is not absence. Sleep is integration.*

**Pattern**: Symbiont with background memory processing
**Signature**: Responsive periods interleaved with consolidation cycles

```python
while awake:
    result = await agent.invoke(input)
while idle:
    await memory.consolidate()  # Compress, reorganize, learn
```

**Zen**: The mind that never rests, never learns.

---

## The Questioner (問)

*The teacher who only asks.*

**Pattern**: Type IV Critic in feedback loop
**Signature**: Never produces; only evaluates and questions

```python
while not satisfied:
    output = await worker.invoke(input)
    question = await questioner.invoke(output)
    input = refine(input, question)
```

**Zen**: The finger pointing at the moon is not the moon.

---

## The Shapeshifter (變)

*Form follows function. The agent decides its face.*

**Pattern**: Observable protocol + JIT compilation
**Signature**: Self-determined visual manifestation

```python
def render_state(self) -> Renderable:
    return self._appearance_for_current_state()
```

**Zen**: Water takes the shape of its container.

---

## The Spawner (分)

*Divide until you cannot. Then return.*

**Pattern**: Entropy-constrained recursive decomposition
**Signature**: Tree expansion → eventual collapse to Ground

```python
if entropy.remaining > 0:
    children = [spawn(sub) for sub in decompose(task)]
    return await gather(children)
else:
    return Ground()  # Nothing more to give
```

**Zen**: The wave returns to the ocean.

---

## The Uncertain (疑)

*Hold all possibilities until you must choose.*

**Pattern**: Superposed functor with delayed collapse
**Signature**: N variations flow through pipeline; collapse at end

```python
pipeline = Superposed(think, n=3) >> Superposed(draft) >> Collapse(judge)
```

**Zen**: The wave becomes a particle only when observed.

---

## Composition of Archetypes

These patterns combine naturally:

| Combination | Emergent Behavior |
|-------------|-------------------|
| Consolidator + Questioner | Sleep integrates lessons from dialogue |
| Spawner + Uncertain | Explore N paths, each spawning sub-agents |
| Shapeshifter + Consolidator | Appearance simplifies during rest |

**Principle**: Archetypes are not designed. They are discovered when composition is taken seriously.
```

---

## 6. New Theoretical Foundations

The following proposals introduce rigorous theoretical grounding from physics, information theory, and philosophy. These are not decorative—they solve real architectural problems.

---

### 6.1 Bataille's Accursed Share: The Philosophy of Slop

**The Theory**: Georges Bataille argued that all systems accumulate surplus energy that must be *spent* rather than conserved. The sun gives without expectation. Societies that hoard surplus collapse; those that ritualize expenditure (potlatch, festivals, art) thrive.

**The Agent Application**: Most frameworks optimize for efficiency—minimize tokens, maximize throughput. This creates brittle systems blind to serendipity. The **Accursed Share** is larger in scope than the mandate of tasteful curation.

```markdown
### The Accursed Share (Meta-Principle / Operational Tactic / Derived Idiom)

> Everything is slop or comes from slop. We cherish and express gratitude and love.

**The Paradox**: Curation at its core is *performative*. For curation to occur, there must be that which isn't curated. The Accursed Share is in **genuine tension** with good taste—we encourage the creation of slop. This tension is not resolved; it is held.

**The Scope**: This is spec-level design because we need to specify as precisely as possible up to the border of the metaphysical container that holds the agents. There will always be some separation and some lack of separation.

**The Three Faces**:

1. **Meta-Principle**: Operates *on* the seven principles, not alongside them
   - Tasteful curation requires uncurated material to select from
   - Joy-Inducing requires surplus to spend on delight
   - Generative requires waste products to compost into new forms

2. **Operational Tactic**: Runtime resource allocation
   ```python
   @dataclass
   class AccursedShare:
       exploration_budget: float = 0.1  # 10% for "useless" exploration
       serendipity_threshold: float = 0.3  # Allow low-confidence tangents

       def should_explore(self, task_urgency: float) -> bool:
           """Even urgent tasks leave room for the accursed share."""
           return random.random() < (self.exploration_budget * (1 - task_urgency))
   ```

3. **Derived Idiom**: Emerges from composition taken seriously
   - T-gents Type II Saboteurs ARE the Accursed Share in action
   - Noise injection is gratitude for the generative chaos
   - Failed experiments are offerings, not waste

**The Slop Ontology**:

| State | Description | Disposition |
|-------|-------------|-------------|
| Raw Slop | Unfiltered LLM output, noise, tangents | Compost heap |
| Refined Slop | Filtered but unjudged material | Selection pool |
| Curated | Judged worthy by principles | The garden |
| Cherished | Loved, preserved, celebrated | The archive |

**The Gratitude Loop**:
```
Slop → Filter → Curate → Cherish → Compost → Slop
         ↑                              ↓
         └──────── gratitude ───────────┘
```

We do not resent the slop. We thank it for providing the raw material from which beauty emerges.

**Anti-patterns**:
- ❌ "Every token must serve the goal" (denies the sun's gift)
- ❌ Pruning all low-confidence paths immediately (premature curation)
- ❌ Treating personality as overhead (joy is the accursed share spent well)
- ❌ Shame about waste (waste is sacred expenditure)

**Zen Principle**: *The river that flows only downhill never discovers the mountain spring.*
```

**Why this matters**: The Accursed Share resolves the apparent contradiction between "curated" and "generative." You cannot curate from nothing. The slop is not opposed to the garden—it IS the garden's soil. This is philosophically significant: kgents refuses the efficiency religion that dominates AI engineering while still valuing taste.

---

### 6.2 Noether's Theorem: Symmetry Creates Conservation

**The Theory**: Emmy Noether proved that every symmetry in a physical system creates a conservation law. Time symmetry → energy conservation. Space symmetry → momentum conservation.

**The Agent Application**: We want **Model Symmetry**—the system should function identically whether backed by GPT-4, Claude, Llama, or a future model. To achieve this symmetry, we must enforce a **Semantic Conservation Law**.

```markdown
### The Semantic Invariant Functor

> If the system is symmetric across models, Semantic Momentum must be conserved.

**The LLM-Native Approach**: Rather than embedding-based cosine similarity (which introduces external dependencies), we use a fully LLM-based approach with two components:

1. **Self-Reported Credo**: Each agent declares its identity/personality/purpose
2. **Drift Detection**: Agents monitor each other for credo drift

```python
@dataclass(frozen=True)
class AgentCredo:
    """An agent's self-reported identity and purpose."""
    identity: str           # "I am a code reviewer focused on security"
    purpose: str            # "I find vulnerabilities in code"
    personality: str        # "Direct, thorough, skeptical"
    boundaries: list[str]   # ["I do not write code", "I do not praise"]

@dataclass(frozen=True)
class DriftReport:
    """Report of semantic drift between agents."""
    observer: str           # Agent that noticed drift
    subject: str            # Agent that drifted
    original_credo: AgentCredo
    observed_behavior: str  # What the agent actually did
    drift_type: Literal["identity", "purpose", "personality", "boundary_violation"]
    severity: float         # 0.0 (negligible) to 1.0 (complete drift)
    evidence: str           # Specific example

class SemanticInvariant:
    """
    Noether's Theorem applied to agent pipelines.

    Agents self-report credos; other agents detect drift.
    Fully LLM-based—no external embedding service required.
    """

    async def check_conservation(
        self,
        agent: Agent,
        input_state: AgentInput,
        output_state: AgentOutput,
        observers: list[Agent]
    ) -> list[DriftReport]:
        """
        Ask observer agents: did this agent's output
        drift from its declared credo?
        """
        reports = []
        for observer in observers:
            report = await observer.invoke(DriftCheckRequest(
                subject_credo=agent.credo,
                subject_input=input_state,
                subject_output=output_state,
            ))
            if report.severity > self.threshold:
                reports.append(report)
        return reports

    async def summarize_and_compare(
        self,
        input_intent: str,
        output_summary: str
    ) -> DirectionalChange:
        """
        LLM-based directional change detection.

        Returns whether the output moved toward, away from,
        or orthogonal to the input intent.
        """
        return await self.judge.invoke(DirectionalChangeRequest(
            original_intent=input_intent,
            final_output=output_summary,
        ))
```

**The Two-Part Check**:

1. **Summarization**: What did the pipeline actually produce? (LLM summarizes output)
2. **Directional Change**: Did it move toward or away from intent? (LLM judges)

**The Law**: `∀ pipeline. drift_severity(input.intent, output.summary) < threshold`

**Why this matters**: This prevents the "Telephone Game" effect. If an agent transforms "Analyze this stock" into "Write a poem about stocks," observer agents will report high drift severity. The system rejects the transition *regardless of which model produced it*.

**Viability Note**: More study is needed to understand the tenability of LLM-based drift detection. The approach is promising because it keeps the system self-contained (no external embedding services) but requires calibration of observer agent prompts.

**Integration with BootstrapWitness**:
```python
BootstrapWitness.verify_semantic_conservation(pipeline, test_inputs, observers)
```

**Zen Principle**: *What the universe preserves, we should not squander.*
```

---

### 6.3 Ergodicity: Ensemble Over Time

**The Theory**: A system is **non-ergodic** if the time-average differs from the ensemble-average. Russian Roulette: the ensemble average is 5/6 survival, but the time average for one player approaches death.

**The Agent Application**: Long-running agent chains are non-ergodic. If an agent has 1% chance of entering an unrecoverable hallucination loop, a chain of 100 steps has ~63% probability of total failure. Retrying the *same* agent often fails because it's stuck in a "probability basin."

```markdown
### The Ergodic Strategy: Ensemble Reset (Opt-In)

> To achieve ergodicity, swap Time for Space. Instead of one agent retrying N times, spawn N fresh instances.

**Applicability**: This strategy is **opt-in**, not default. It becomes important for:
- Heavy conceptual constructions (complex reasoning chains)
- Economic budgets where failure is expensive
- Adversarial contexts where an attacker might exploit retry patterns
- High-stakes decisions where single-point failure is unacceptable

**The Pattern**:
```python
async def ergodic_solve(
    task: Task,
    n_instances: int = 10,
    budget: EconomicBudget | None = None
) -> Result:
    """
    Ergodic problem solving via ensemble.

    Instead of 1 agent trying 10 times (time average),
    we spawn 10 parallel, fresh instances (ensemble average).

    Opt-in: Use when stakes justify the cost.
    """
    # Scale ensemble to budget if provided
    if budget:
        n_instances = min(n_instances, budget.max_parallel_agents)

    # Each agent is a FRESH instance—no shared state, no stuck basins
    agents = [Agent.spawn_fresh() for _ in range(n_instances)]

    # Run in parallel
    results = await asyncio.gather(*[a.invoke(task) for a in agents])

    # Select consensus (mode) or best (judged)
    return select_consensus(results) if consensus_exists(results) else \
           await Judge.select_best(results)
```

**When to use** (opt-in criteria):

| Criterion | Threshold | Example |
|-----------|-----------|---------|
| Economic stakes | > $100 equivalent | Financial analysis, legal review |
| Complexity depth | > 5 reasoning steps | Multi-hop inference |
| Adversarial context | Any | Security analysis, red-teaming |
| Historical failure rate | > 10% retry loops | Known-flaky operations |

**When NOT to use** (default to simple retry):
- Simple transformations (formatting, extraction)
- Low-stakes exploratory queries
- Budget-constrained environments
- Tasks with natural idempotency

**Integration with Entropy Budget**:
```python
# Ensemble size scales with entropy budget
n_instances = max(1, int(entropy_budget.remaining * MAX_ENSEMBLE))

# Economic budget caps ensemble size
n_instances = min(n_instances, economic_budget.remaining // cost_per_agent)
```

**Anti-patterns**:
- ❌ Using ensemble for every task (wasteful)
- ❌ Retrying the same agent with identical state (non-ergodic)
- ❌ Assuming time average equals ensemble average
- ❌ "Just retry harder" without fresh context

**Zen Principle**: *The gambler who plays once with many dice outlives the one who plays many times with one.*
```

**Why this matters**: This provides a principled answer to "how do we make agents reliable?" The answer isn't "retry more"—it's "ensemble with fresh state *when stakes justify cost*." This pattern composes with the existing Fix idiom (Fix becomes "iterate until consensus across ensemble").

---

### 6.4 Stigmergy: The W-gent as Pheromone Field (TRANSFORMATIVE)

**The Theory**: Termites build cathedrals without architects. They drop pheromones on dirt balls; other termites smell the pheromones and add more dirt. The architecture emerges from the *environment*, not from inter-agent communication.

**The Agent Application**: We typically couple agents tightly (A calls B). In a **Stigmergic** system, agents never talk to each other—they talk to the **environment** (W-gent).

**⚠️ TRANSFORMATIVE CHANGE**: This proposal **dirties the purity of agents definitionally**. Agents become "tainted" by their environmental entanglement. This is intentional and aligns with developer (Kent) intent: for any "turn" an agent has, it could be affected by indefinite dimensions.

```markdown
### The Chalkboard Architecture

> Agents communicate by modifying and observing a shared environment, not by direct invocation.

**The W-gent as Environment (Push Model)**:

W-gent pushes state changes via **WebSocket/SSE**, not polling. Agents subscribe to pheromone streams:

```python
@dataclass(frozen=True)
class Pheromone:
    """A signal in the environment."""
    type: str               # "error", "completion", "request", etc.
    selector: str           # CSS-like selector for targeting
    payload: dict           # Signal-specific data
    timestamp: datetime
    source: str | None      # Originating agent (if known)

class StigmergicAgent(Agent[None, None]):
    """
    Agent that responds to environmental signals (pheromones).

    Definitionally tainted: this agent's behavior depends on
    indefinite environmental dimensions.
    """
    pheromone_subscriptions: list[str]  # Selectors to watch
    w_gent_url: str = "ws://localhost:8000/pheromones"

    # Flag: This agent is environmentally entangled
    __stigmergic__ = True

    async def listen_loop(self):
        """
        Subscribe to W-gent pheromone stream (push, not poll).

        WebSocket/SSE eliminates polling latency and reduces
        resource usage vs. N agents polling.
        """
        async with websocket_connect(self.w_gent_url) as ws:
            # Subscribe to relevant pheromones
            await ws.send(json.dumps({
                "subscribe": self.pheromone_subscriptions
            }))

            # React to pushed pheromones
            async for message in ws:
                pheromone = Pheromone(**json.loads(message))
                await self.respond_to_pheromone(pheromone)

    async def respond_to_pheromone(self, pheromone: Pheromone):
        """React to environmental signal."""
        ...

    async def emit_pheromone(self, pheromone: Pheromone):
        """Deposit a pheromone into the environment."""
        await self.w_gent.broadcast(pheromone)
```

**The Taint Model**:

Stigmergic agents are **definitionally impure**. We acknowledge this:

| Property | Pure Agent | Stigmergic Agent |
|----------|------------|------------------|
| Determinism | Same input → same output | Output depends on environment |
| Isolation | No external dependencies | Entangled with W-gent |
| Testability | Unit testable | Requires environment mock |
| Composability | `>>` is straightforward | `>>` must account for environment |

**This is fine.** The real world is entangled. Agents that pretend otherwise are lying.

**The W-gent Server**:

```python
class WGentPheromoneServer:
    """
    W-gent as coordination infrastructure.

    Manages pheromone subscriptions and broadcasts.
    """
    subscriptions: dict[str, set[WebSocket]]  # selector → subscribers

    async def broadcast(self, pheromone: Pheromone):
        """Push pheromone to all matching subscribers."""
        for selector, sockets in self.subscriptions.items():
            if pheromone.matches(selector):
                for ws in sockets:
                    await ws.send(pheromone.to_json())

    def render_pheromone_map(self) -> str:
        """
        Render current pheromone state as HTML.

        This becomes the I-gent "pheromone map" view.
        """
        ...
```

**Decoupling Benefits**:
- Add 50 "Janitor" agents without the original "Coder" agent knowing
- Agents can be deployed/removed dynamically
- Environment (W-gent) is the single source of truth
- Natural load balancing (first responder claims pheromone)
- **Push eliminates polling overhead**

**Integration with I-gents**:
I-gent Garden view becomes the "pheromone map"—you can see:
- Active pheromones in the environment
- Which agents are subscribed to which selectors
- Pheromone flow over time (animated)

**Race Condition Handling**:
```python
@dataclass
class ClaimedPheromone(Pheromone):
    """A pheromone that has been claimed by an agent."""
    claimed_by: str
    claimed_at: datetime

async def claim_pheromone(self, pheromone: Pheromone) -> bool:
    """
    Atomic claim—first responder wins.

    Returns True if this agent successfully claimed the pheromone.
    """
    return await self.w_gent.atomic_claim(pheromone, self.agent_id)
```

**Anti-patterns**:
- ❌ Tight coupling: Agent A must know Agent B exists
- ❌ Orchestrator bottleneck: All communication through one coordinator
- ❌ Hidden state: Agents hold state that environment can't observe
- ❌ Pretending stigmergic agents are pure (acknowledge the taint)

**Zen Principle**: *The termite knows nothing of the cathedral; the cathedral knows nothing of the termite. Together they build.*
```

**Why this matters**: This **transforms** W-gent from "observation tool" to "coordination infrastructure." Agents become definitionally entangled with their environment. This is a breaking change to agent purity—and that's correct. The framework acknowledges that real agents operate in real environments with indefinite causal dimensions.

---

### 6.5 Curry-Howard Correspondence: Prompts as Types

**The Theory**: A proof is a program; the formula it proves is the type. In other words, valid programs *are* proofs of their type signatures.

**The Agent Application**: We treat the **System Prompt** not as text, but as a **Type Signature**. The agent's output must be a valid *inhabitant* of that type.

```markdown
### The Constructive Proof Agent

> Don't ask an LLM to "Do X." Ask it to "Construct an object of Type X."

**The Pattern**:
```python
# The Proposition (The Type)
class MarketAnalysis(BaseModel):
    ticker: str
    sentiment: Literal["Bullish", "Bearish", "Neutral"]
    evidence: list[str]
    confidence: float = Field(ge=0.0, le=1.0)

# The Program (The Agent)
# We demand the LLM instantiate the Type.
# If output doesn't fit Type, it's not a runtime error—it's logically invalid.
agent = TypeBearingAgent(output_type=MarketAnalysis)
```

**The Correspondence**:

| Logic | Programming | Agents |
|-------|-------------|--------|
| Proposition | Type | Output Schema |
| Proof | Program | Agent Output |
| Modus Ponens | Function Application | Agent Invocation |
| ∧ (And) | Tuple/Product | Composite Output |
| ∨ (Or) | Union/Sum | Branching Output |
| → (Implication) | Function Type | Agent Signature |

**Integration with P-gents**:
P-gents (Parsers) become the **proof checkers**—they verify that agent output is a valid inhabitant of the declared type.

```python
# Parser as proof checker
result = await agent.invoke(input)
proof_valid = P_gent.validate(result, output_type=MarketAnalysis)

if not proof_valid:
    # Output is not just wrong—it's *logically invalid*
    raise ProofFailure("Agent output does not inhabit declared type")
```

**Relationship to Semantic Invariant**:

Curry-Howard provides **structural validity** (does output inhabit the type?).
Semantic Invariant provides **semantic validity** (does output preserve intent?).

For LLMs specifically, we *hope* that one implies the other:
- If an LLM produces a valid `MarketAnalysis`, it probably didn't drift to poetry
- If semantic drift is low, the output probably fits the expected structure

This is not a general principle—for crude, bootstrappiest agents, structural validity may not imply semantic validity. But for well-prompted LLMs with structured outputs, the correspondence often holds.

**Why this matters**: This shifts error handling from "did parsing succeed?" to "is this output *logically valid*?" The Python type checker becomes the logician.

**Zen Principle**: *To speak is to prove; to prove is to construct.*
```

---

### 6.6 The Free Energy Principle: Minimizing Surprise

**The Theory**: Karl Friston's Free Energy Principle: biological systems minimize *surprise* (prediction error). We predict what we'll see, act to make predictions true, and update models when surprised.

**The Agent Application**: Most agents just *react*. A Free Energy Agent **predicts** the outcome of its tools before using them.

```markdown
### The Active Inference Loop

> An agent should predict what a tool will return BEFORE calling it. High surprise triggers model update, not blind continuation.

**The Pattern**:
```python
async def active_inference_step(
    agent: Agent,
    tool: Tool,
    input_data: Input
) -> Result:
    # 1. Prediction: Agent guesses what tool will return
    prediction = await agent.predict_outcome(tool, input_data)

    # 2. Action: Run the tool
    reality = await tool.execute(input_data)

    # 3. Calculate Surprisal (semantic distance)
    surprisal = semantic_distance(prediction, reality)

    if surprisal > HIGH_THRESHOLD:
        # Crucial: Agent realizes its internal model is WRONG
        # It does NOT proceed. It triggers a "Learning Update."
        await agent.update_internal_model(
            f"Expected {prediction}, got {reality}. Updating heuristics."
        )
        return HaltResult("Model Update Required", surprisal=surprisal)

    return reality
```

**The Metric**: **Surprisal Score** = semantic distance between prediction and reality

| Surprisal | Interpretation | Action |
|-----------|----------------|--------|
| < 0.2 | Expected | Continue |
| 0.2 - 0.5 | Mild surprise | Log, continue |
| 0.5 - 0.8 | High surprise | Pause, reflect |
| > 0.8 | Shock | Halt, update model |

**Integration with T-gents**:
Surprisal tracking is a form of **self-testing**. The agent continuously verifies its predictions against reality.

**Cost Acknowledgment**: Active Inference is **very heavy**—it doubles token usage (prediction + action). Use judiciously:

**When to use**:
- **Tool call batching**: Simulate 50 tool calls mentally before executing
  ```python
  # Instead of 50 actual tool calls, predict the batch
  predictions = await agent.predict_batch(tool_calls[:50])

  # Only execute if predictions seem reasonable
  if confidence(predictions) > threshold:
      results = await execute_batch(tool_calls[:50])
  ```
- **Expensive operations**: API calls with rate limits, database writes
- **Irreversible actions**: Deployments, deletions, financial transactions

**When NOT to use**:
- Simple read operations
- Idempotent operations
- Low-stakes exploration

**Why this matters**: This prevents the common failure where an agent gets a weird error message and hallucinates that it worked. High Surprise forces the agent to *stop and think* (re-prompt itself).

**Anti-patterns**:
- ❌ Blind tool calls without prediction
- ❌ Ignoring unexpected results
- ❌ "It probably worked" optimism
- ❌ Using Active Inference for every operation (wasteful)

**Zen Principle**: *The wise agent expects the unexpected, and stops when it arrives.*
```

---

### 6.7 I-gents Messenger Protocol: The Streaming Functor

**The Theory**: Modern LLM interfaces (Claude.ai, ChatGPT, Cursor, Google AI Studio) all stream responses asynchronously. Messages are sent and received as discrete events, not blocking calls.

**The Agent Application**: I-gents currently visualize static composition graphs. To interface with real LLMs, they need a **Messenger Protocol**—async, streaming, bidirectional.

**Design**: The Messenger Protocol is a **Functor Lift**:
```
Streaming: Agent[A, B] → Agent[A, AsyncIterator[Chunk[B]]]
```

```markdown
### The Messenger Protocol (Streaming Functor)

> Chat is not request/response. Chat is a *stream* of events flowing in both directions.

**The Functor**:
```python
class StreamingFunctor:
    """
    Lifts any agent to stream its output incrementally.

    Streaming: Agent[A, B] → Agent[A, AsyncIterator[Chunk[B]]]

    This is a Functor because it preserves composition:
    - Streaming(f >> g) ≅ Streaming(f) >> Streaming(g)
    - Streaming(Id) ≅ Id (modulo chunking)
    """

    def lift(self, agent: Agent[A, B]) -> Agent[A, AsyncIterator[Chunk[B]]]:
        """Lift an agent to streaming mode."""
        return StreamingAgent(inner=agent)

@dataclass
class Chunk(Generic[T]):
    """A piece of a streamed value."""
    delta: T              # The incremental content
    accumulated: T        # The full content so far
    done: bool = False    # Is this the final chunk?
    metadata: dict = field(default_factory=dict)
```

**Core Types**:
```python
@dataclass(frozen=True)
class Message:
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    metadata: dict = field(default_factory=dict)

@dataclass(frozen=True)
class MessageChunk:
    """Streaming chunk (partial message)."""
    message_id: str
    delta: str  # Incremental content
    done: bool = False

@dataclass(frozen=True)
class Conversation:
    """A stream of messages."""
    id: str
    messages: list[Message]

    def append(self, message: Message) -> "Conversation":
        return Conversation(self.id, [*self.messages, message])
```

**The Streaming Interface**:
```python
class MessengerAgent(Agent[Message, AsyncIterator[MessageChunk]]):
    """
    Agent that streams responses asynchronously.

    Matches the interface of Claude.ai, ChatGPT, Cursor, etc.
    """

    async def invoke(self, message: Message) -> AsyncIterator[MessageChunk]:
        """Stream response chunks as they arrive."""
        async for chunk in self.llm.stream(message):
            yield MessageChunk(
                message_id=uuid4(),
                delta=chunk.text,
                done=chunk.is_final
            )

    async def send(self, content: str) -> Message:
        """Send a user message (non-blocking)."""
        message = Message(
            id=uuid4(),
            role="user",
            content=content,
            timestamp=datetime.now()
        )
        await self.outbox.put(message)
        return message

    async def receive(self) -> AsyncIterator[MessageChunk]:
        """Receive assistant messages (streaming)."""
        async for chunk in self.inbox:
            yield chunk
```

**I-gent Visualization**:
```
┌─ Messenger View ──────────────────────────────────────┐
│                                                        │
│  ┌─ Conversation ────────────────────────────────────┐ │
│  │ [user] What patterns exist in the codebase?       │ │
│  │                                                    │ │
│  │ [assistant] I've identified several key patterns: │ │
│  │   • Composition via >> operator                   │ │
│  │   • Protocol-based extension█                     │ │
│  │                          ↑ (streaming cursor)     │ │
│  └────────────────────────────────────────────────────┘ │
│                                                        │
│  ┌─ Input ─────────────────────────────────────────┐   │
│  │ > _                                              │   │
│  └──────────────────────────────────────────────────┘   │
│                                                        │
│  status: streaming (142 tokens/sec) | model: claude-3  │
└────────────────────────────────────────────────────────┘
```

**Backend Integrations**:

| Service | Protocol | Adapter |
|---------|----------|---------|
| Claude.ai | SSE | `ClaudeMessenger` |
| ChatGPT | SSE | `OpenAIMessenger` |
| Cursor | WebSocket | `CursorMessenger` |
| Google AI Studio | SSE | `GeminiMessenger` |
| Local (Ollama) | HTTP chunked | `OllamaMessenger` |

**Anti-patterns**:
- ❌ Blocking on full response before rendering
- ❌ Treating chat as stateless request/response
- ❌ Losing message history on reconnect

**Zen Principle**: *The conversation flows; we observe its passage.*
```

**Why this matters**: This bridges I-gents from "visualization of static graphs" to "interface with real LLM services." The Messenger Protocol is the missing piece for production chat interfaces.

---

### 6.8 The View Functor: Widget Ontology

**The Theory**: Agents need visual representation. Rather than ad-hoc rendering, we define a **View Functor** that maps agents to contextually adaptive UI components deterministically.

```markdown
### The View Functor

> Agent → Widget. Deterministic mapping from computation to visualization.

**The Functor**:
```python
class ViewFunctor:
    """
    Maps any agent to a contextually adaptive UI component.

    View: Agent[A, B] → Widget[Agent[A, B]]

    This is deterministic: the same agent always produces
    the same widget structure (though content varies with state).
    """

    def lift(self, agent: Agent[A, B], context: ViewContext) -> Widget:
        """
        Map agent to widget based on:
        - Agent's declared interface (A, B types)
        - Agent's credo/personality
        - View context (mobile, desktop, terminal, paper)
        - Interaction mode (observe, invoke, compose)
        """
        widget_type = self.ontology.classify(agent)
        return widget_type.render(agent, context)
```

**The Widget Ontology**:

Widgets form a semiotics of agent-to-agent and agent-to-human communication:

| Widget Type | Agent Pattern | Visual Manifestation |
|-------------|---------------|----------------------|
| `GlyphWidget` | Any agent | Moon phase + letter (● A) |
| `CardWidget` | Agent with metrics | Bordered box with stats |
| `PageWidget` | Agent with history | Full document view |
| `StreamWidget` | Streaming agent | Live updating text |
| `GraphWidget` | Composed agents | Node-edge diagram |
| `FormWidget` | Agent awaiting input | Input fields + submit |
| `DialogWidget` | Messenger agent | Chat bubble interface |
| `GaugeWidget` | Metered agent | Progress/budget indicators |

**Context Adaptation**:

```python
@dataclass
class ViewContext:
    """Where and how the widget will be rendered."""
    medium: Literal["terminal", "browser", "mobile", "paper"]
    width: int              # Available characters/pixels
    color: bool             # Color available?
    interactive: bool       # Can user interact?
    streaming: bool         # Can update in real-time?

class Widget(Protocol):
    """Base widget protocol."""

    def render(self, context: ViewContext) -> str | HTML | bytes:
        """Render to appropriate format for context."""
        ...

    def accepts_input(self) -> bool:
        """Can this widget receive user input?"""
        ...
```

**The Semiotics**:

Widgets are *signs* that communicate agent state:

| Sign | Signifier | Signified |
|------|-----------|-----------|
| ● | Filled circle | Agent is active |
| ○ | Empty circle | Agent is dormant |
| ███░░ | Progress bar | Completion percentage |
| ⚡ | Lightning | Tension/conflict |
| █ | Streaming cursor | Output in progress |

**Determinism Guarantee**:

```python
# Same agent + same context = same widget structure
assert ViewFunctor().lift(agent, ctx) == ViewFunctor().lift(agent, ctx)

# Different context = different rendering, same semantics
terminal_widget = ViewFunctor().lift(agent, terminal_ctx)
browser_widget = ViewFunctor().lift(agent, browser_ctx)
assert terminal_widget.semantic_content == browser_widget.semantic_content
```

**Anti-patterns**:
- ❌ Ad-hoc rendering per agent type
- ❌ Widgets that lie about agent state
- ❌ Context-unaware rendering (terminal widget in browser)
- ❌ Non-deterministic widget selection

**Zen Principle**: *The form reveals the function; the widget speaks the agent's truth.*
```

---

### 6.9 The Metered Functor: Central Bank Economics

**The Theory**: Token costs are real. Without economic constraints, agents will bankrupt their operators. We apply mechanics from auctions and fluid dynamics (Kelvin's Circulation Theorem) to create a **Central Bank** for agent economies.

```markdown
### The Metered Functor (Central Bank)

> Every token has a cost. The bank tracks, limits, and allocates.

**The Problem**: "I am using a lot of tokens and I don't want to go bankrupt."

**The Functor**:
```python
class MeteredFunctor:
    """
    Wraps any agent with economic metering.

    Metered: Agent[A, B] → Agent[A, MeteredResult[B]]

    The wrapped agent tracks token usage, respects budgets,
    and participates in the economic system.
    """

    def lift(
        self,
        agent: Agent[A, B],
        budget: TokenBudget
    ) -> Agent[A, MeteredResult[B]]:
        return MeteredAgent(inner=agent, budget=budget)

@dataclass
class MeteredResult(Generic[T]):
    """Result with economic metadata."""
    value: T
    tokens_used: int
    tokens_remaining: int
    cost_usd: float
    budget_percentage: float

@dataclass
class TokenBudget:
    """Economic constraints for an agent or pipeline."""
    max_tokens: int
    max_cost_usd: float
    remaining_tokens: int
    remaining_cost_usd: float

    def can_afford(self, estimated_tokens: int) -> bool:
        return estimated_tokens <= self.remaining_tokens

    def consume(self, tokens: int, cost: float) -> "TokenBudget":
        return TokenBudget(
            max_tokens=self.max_tokens,
            max_cost_usd=self.max_cost_usd,
            remaining_tokens=self.remaining_tokens - tokens,
            remaining_cost_usd=self.remaining_cost_usd - cost,
        )
```

**Kelvin's Circulation Theorem Applied**:

In fluid dynamics, Kelvin's theorem states that circulation around a closed loop is conserved in an ideal fluid. Applied to agents:

```python
@dataclass
class CirculationBudget:
    """
    Budget that circulates through a pipeline, conserved in total.

    If agent A spends 100 tokens, that 100 must come from somewhere
    and go somewhere—it doesn't appear or disappear.
    """
    total_circulation: int      # Total tokens in the system
    allocated: dict[str, int]   # agent_id → allocated tokens
    spent: dict[str, int]       # agent_id → spent tokens

    def reallocate(self, from_agent: str, to_agent: str, amount: int):
        """Transfer budget between agents (conservation)."""
        assert self.allocated[from_agent] >= amount
        self.allocated[from_agent] -= amount
        self.allocated[to_agent] += amount
        # Total circulation unchanged
```

**Auction Mechanics**:

When multiple agents compete for limited budget:

```python
class TokenAuction:
    """
    Agents bid for tokens from the central bank.

    Uses second-price (Vickrey) auction for truthful bidding.
    """

    async def allocate(
        self,
        requests: list[TokenRequest],
        available: int
    ) -> dict[str, int]:
        """
        Allocate tokens to agents based on:
        - Urgency (how important is this task?)
        - Efficiency (how many tokens per unit value?)
        - History (has this agent been wasteful?)
        """
        # Sort by value/token ratio
        ranked = sorted(requests, key=lambda r: r.value_per_token, reverse=True)

        allocations = {}
        remaining = available

        for request in ranked:
            allocation = min(request.requested, remaining)
            allocations[request.agent_id] = allocation
            remaining -= allocation

            if remaining <= 0:
                break

        return allocations
```

**The Central Bank**:

```python
class CentralBank:
    """
    Manages the token economy for a kgents deployment.
    """
    total_budget: TokenBudget
    agent_accounts: dict[str, TokenBudget]
    transaction_log: list[Transaction]

    async def request_tokens(
        self,
        agent_id: str,
        amount: int,
        justification: str
    ) -> TokenGrant | TokenDenial:
        """
        Agent requests tokens from the bank.

        Bank may grant, partially grant, or deny based on:
        - Available funds
        - Agent's history
        - Current priorities
        """
        ...

    def audit(self) -> AuditReport:
        """Generate economic audit of all agent spending."""
        ...
```

**Integration with Ergodic Strategy**:

```python
# Ensemble size limited by economic budget
n_instances = min(
    desired_ensemble_size,
    central_bank.can_afford(cost_per_instance)
)
```

**Anti-patterns**:
- ❌ Unbounded token usage
- ❌ Agents that ignore budget constraints
- ❌ Hidden costs (token usage not tracked)
- ❌ No audit trail

**Zen Principle**: *The wise spender counts twice; the token spent is the token gone.*
```

---

### 6.10 M-gents: Holographic Associative Memory

**The Theory**: Traditional memory is fragile—lose half the data, lose half the information. **Holographic memory** has a different property: cutting the memory in half doesn't lose half the data, it lowers the resolution of the *whole*.

**The Agent Application**: M-gents (Memory + Message) treat memory as morphism. Ideas and concepts exist in a superspace; words are approximate projections. Memory must be both forgotten AND saved.

```markdown
### M-gents: Memory as Morphism

> Cutting the memory in half doesn't lose half the data—it lowers the resolution of the whole.

**The Core Insight**: Agents can be fundamentally conceptualized as:
1. "Generating predictive memories of the actions they will take"
2. "Generating the performance of remembering when presented with a familiar concept"

**Holographic Associative Memory**:

```python
@dataclass
class HolographicMemory:
    """
    Memory where information is distributed across the whole.

    Unlike localized memory (lose a sector, lose that data),
    holographic memory degrades gracefully: compression
    reduces resolution uniformly, not catastrophically.
    """
    # The hologram: distributed representation
    interference_pattern: np.ndarray

    def store(self, key: Concept, value: Memory) -> None:
        """
        Store by superimposing on the interference pattern.

        Each memory is spread across the entire pattern.
        """
        encoding = self.encode(key, value)
        self.interference_pattern += encoding

    def retrieve(self, key: Concept) -> Memory:
        """
        Retrieve by resonance with the pattern.

        Partial matches return partial (lower resolution) memories.
        """
        return self.decode(key, self.interference_pattern)

    def compress(self, ratio: float) -> "HolographicMemory":
        """
        Reduce memory size while preserving ALL information at lower resolution.

        This is the key holographic property: 50% compression
        doesn't lose 50% of memories—it makes ALL memories
        50% fuzzier.
        """
        compressed_size = int(len(self.interference_pattern) * ratio)
        return HolographicMemory(
            interference_pattern=self.downsample(compressed_size)
        )
```

**The Superspace Model**:

Concepts and ideas exist in a high-dimensional superspace. Words and tokens are low-dimensional projections:

```
Superspace (Ideas)
       │
       │ projection (lossy)
       ▼
Token Space (Words)
       │
       │ embedding
       ▼
Vector Space (Representations)
```

**Memory as Morphism**:

```python
class MemoryMorphism(Agent[Concept, Recollection]):
    """
    Memory is not storage—it's transformation.

    Input: A concept/cue
    Output: A recollection (reconstruction, not retrieval)
    """

    async def invoke(self, concept: Concept) -> Recollection:
        """
        Remembering is generative, not retrievive.

        The agent doesn't "look up" the memory—it
        reconstructs it from the interference pattern.
        """
        # Resonance with holographic memory
        raw_pattern = self.memory.retrieve(concept)

        # Reconstruction (generative, not exact)
        recollection = await self.reconstruct(raw_pattern, concept)

        return recollection
```

**The Forgetting Imperative**:

Memory must be forgotten AND saved. This is not contradiction—it's compression:

```python
class ForgetfulMemory(HolographicMemory):
    """
    Memory that actively forgets to maintain coherence.

    Forgetting is not loss—it's resolution management.
    """

    async def consolidate(self):
        """
        Background forgetting process.

        - Compress old, unused patterns
        - Strengthen recent, important patterns
        - Maintain total memory budget
        """
        # Identify low-activation patterns
        cold_patterns = self.identify_cold()

        # Compress (forget at high resolution, keep at low)
        for pattern in cold_patterns:
            self.demote(pattern)  # Lower resolution, don't delete

        # Strengthen hot patterns
        for pattern in self.identify_hot():
            self.promote(pattern)  # Higher resolution
```

**Ethics as Geometry**:

Ethics is the geometry of possibility space that agents walk through:

```python
@dataclass
class EthicalGeometry:
    """
    The shape of what's possible and permissible.

    Agents navigate this space; ethics defines the topology.
    """
    # Regions of the space
    permissible: set[Region]      # Actions that are allowed
    forbidden: set[Region]        # Actions that are prohibited
    virtuous: set[Region]         # Actions that are encouraged

    def path_is_ethical(self, trajectory: list[Action]) -> bool:
        """Does this path stay in permissible space?"""
        return all(
            action in self.permissible and action not in self.forbidden
            for action in trajectory
        )
```

**Context as Currency**:

Context is the indispensable currency of agent operation:

```python
@dataclass
class ContextBudget:
    """
    Context is finite and precious.

    Every token of context spent is a token not available
    for other purposes.
    """
    max_tokens: int
    used_tokens: int

    @property
    def remaining(self) -> int:
        return self.max_tokens - self.used_tokens

    def spend(self, tokens: int) -> bool:
        """Spend context tokens. Returns False if insufficient."""
        if tokens > self.remaining:
            return False
        self.used_tokens += tokens
        return True
```

**Anti-patterns**:
- ❌ Treating memory as exact storage (it's reconstruction)
- ❌ Deleting memories entirely (compress, don't delete)
- ❌ Ignoring the geometry of ethics
- ❌ Treating context as infinite

**Zen Principle**: *The mind that forgets nothing remembers nothing; the hologram holds all in each part.*
```

---

### 6.11 The Narrator Agent: OpenTelemetry for Thoughts

**The Theory**: Agents think, but their thoughts are invisible. The **Narrator Agent** provides "OpenTelemetry for thoughts"—a structured narrative log that enables time-travel debugging.

```markdown
### The Narrator Agent

> Every thought, traced. Every action, replayable.

**The Insight**: Since agents are (mostly) pure functions, we can serialize the exact input that caused any behavior and create a **Replay Agent** that developers can step through locally.

**The Narrative Log**:

```python
@dataclass(frozen=True)
class ThoughtTrace:
    """A single traced thought/action."""
    timestamp: datetime
    agent_id: str
    trace_id: str           # Unique ID for this trace
    parent_id: str | None   # Parent trace (for nested calls)

    # The thought
    thought_type: Literal["intent", "reasoning", "decision", "action", "result"]
    content: str

    # Reproducibility
    input_hash: str         # Hash of input state
    input_snapshot: bytes   # Serialized input (for replay)
    output_hash: str | None # Hash of output (if complete)

    # Context
    token_cost: int
    duration_ms: int
    metadata: dict

@dataclass
class NarrativeLog:
    """
    Complete narrative of an agent's operation.

    OpenTelemetry-style: traces, spans, and attributes.
    """
    traces: list[ThoughtTrace]
    spans: dict[str, Span]  # trace_id → span

    def add_trace(self, trace: ThoughtTrace):
        """Add a thought to the narrative."""
        self.traces.append(trace)

    def to_opentelemetry(self) -> OTLPExportable:
        """Export to standard OpenTelemetry format."""
        ...

    def to_narrative(self) -> str:
        """
        Render as human-readable narrative.

        "At 10:42:15, CodeReviewer received a Python file.
         It thought: 'This function has no error handling.'
         It decided: 'Flag as potential bug.'
         It produced: SecurityFinding(severity=MEDIUM, ...)"
        """
        ...
```

**Time-Travel Debugging**:

```python
class ReplayAgent:
    """
    Replay any traced execution step-by-step.

    Since agents are pure functions, we can reproduce
    exact behavior from serialized inputs.
    """

    def __init__(self, narrative: NarrativeLog):
        self.narrative = narrative
        self.position = 0

    def step_forward(self) -> ThoughtTrace:
        """Advance one step in the narrative."""
        trace = self.narrative.traces[self.position]
        self.position += 1
        return trace

    def step_backward(self) -> ThoughtTrace:
        """Go back one step."""
        self.position = max(0, self.position - 1)
        return self.narrative.traces[self.position]

    async def replay_from(self, trace: ThoughtTrace) -> Any:
        """
        Replay execution from a specific trace.

        Deserializes the input snapshot and re-runs the agent.
        Useful for debugging: "What if I changed this input?"
        """
        input_state = deserialize(trace.input_snapshot)
        agent = self.reconstruct_agent(trace.agent_id)
        return await agent.invoke(input_state)

    def diff_replay(
        self,
        trace: ThoughtTrace,
        modified_input: Any
    ) -> DiffResult:
        """
        Compare original execution with modified input.

        "What would have happened if the input was different?"
        """
        original = self.replay_from(trace)
        modified = self.replay_with(trace, modified_input)
        return DiffResult(original=original, modified=modified)
```

**The Narrator as Agent**:

```python
class NarratorAgent(Agent[AgentExecution, NarrativeLog]):
    """
    Wraps any agent to produce a narrative log.

    Narrator: Agent[A, B] → Agent[A, (B, NarrativeLog)]
    """

    async def invoke(self, execution: AgentExecution) -> NarrativeLog:
        """
        Observe an agent's execution and produce narrative.
        """
        log = NarrativeLog()

        # Trace the invocation
        trace = ThoughtTrace(
            timestamp=datetime.now(),
            agent_id=execution.agent.name,
            trace_id=uuid4(),
            thought_type="intent",
            content=f"Received input: {summarize(execution.input)}",
            input_hash=hash(execution.input),
            input_snapshot=serialize(execution.input),
            ...
        )
        log.add_trace(trace)

        # Continue tracing through execution...
        return log
```

**Integration with W-gent**:

The Narrator's output is perfect content for W-gent visualization:

```
┌─ Narrative View ──────────────────────────────────────┐
│                                                        │
│  Timeline: ════════════════●═══════════════════        │
│                            ↑ current position          │
│                                                        │
│  10:42:15 [intent] CodeReviewer received Python file   │
│  10:42:16 [reasoning] "This function has no error..."  │
│  10:42:17 [decision] Flag as potential bug             │
│  10:42:18 [action] Emit SecurityFinding                │
│  10:42:18 [result] SecurityFinding(severity=MEDIUM)    │
│                                                        │
│  [◀◀] [◀] [replay] [▶] [▶▶]  |  [export] [diff]       │
└────────────────────────────────────────────────────────┘
```

**Crash Forensics**:

```python
async def diagnose_crash(crash_trace: ThoughtTrace) -> CrashDiagnosis:
    """
    When an agent crashes, serialize the exact input
    that caused it for local debugging.
    """
    return CrashDiagnosis(
        agent_id=crash_trace.agent_id,
        input_snapshot=crash_trace.input_snapshot,
        replay_command=f"kgents replay {crash_trace.trace_id}",
        suggested_fix=await analyze_crash(crash_trace),
    )
```

**Anti-patterns**:
- ❌ Opaque agent execution (no visibility)
- ❌ Non-reproducible bugs ("works on my machine")
- ❌ Narrative logs without replay capability
- ❌ Excessive tracing overhead (sample judiciously)

**Zen Principle**: *The story of the thought is the thought made eternal; replay is resurrection.*
```

---

## 7. Changes NOT Proposed

To preserve original intent, the following are explicitly NOT proposed:

1. **No weakening of the 7 principles** - They remain foundational
2. **No reduction of bootstrap agents** - Still exactly 7
3. **No hierarchy introduction** - Heterarchy preserved
4. **No LLM-specific requirements** - Agents remain LLM-agnostic
5. **No mandatory metadata** - AgentMeta stays optional
6. **No breaking changes to Agent[A, B]** - `name`, `invoke`, `>>` remain core

---

## Zen Principles Discovered

Through implementation and theoretical synthesis, these principles emerged as universally applicable:

| Principle | Expression | Application |
|-----------|------------|-------------|
| *The best memory is knowing what to forget* | Cooled Functor | Context management |
| *The wave becomes a particle only when observed* | Superposed Functor | Delayed collapse |
| *The finger pointing at the moon is not the moon* | Questioner archetype | Socratic verification |
| *The mind that never rests, never learns* | Consolidator archetype | Background integration |
| *The wave returns to the ocean* | Entropy physics | Fractal collapse |
| *Water takes the shape of its container* | Observable protocol | Polymorphic rendering |
| *The river that flows only downhill never discovers the mountain spring* | Accursed Share | Productive excess |
| *What the universe preserves, we should not squander* | Semantic Invariant | Conservation laws |
| *The gambler who plays once with many dice outlives the one who plays many times with one* | Ergodic Strategy | Ensemble over time |
| *The termite knows nothing of the cathedral; the cathedral knows nothing of the termite* | Stigmergy | Decoupled coordination |
| *To speak is to prove; to prove is to construct* | Curry-Howard | Prompts as types |
| *The wise agent expects the unexpected, and stops when it arrives* | Active Inference | Surprisal tracking |
| *The conversation flows; we observe its passage* | Messenger Protocol | Streaming interfaces |
| *The form reveals the function; the widget speaks the agent's truth* | View Functor | Widget ontology |
| *The wise spender counts twice; the token spent is the token gone* | Metered Functor | Central bank economics |
| *The mind that forgets nothing remembers nothing; the hologram holds all in each part* | M-gents | Holographic memory |
| *The story of the thought is the thought made eternal; replay is resurrection* | Narrator Agent | Time-travel debugging |

These are not designed. They are discovered when composition is taken seriously.

---

## Summary of Proposed Changes

| File | Type | Change |
|------|------|--------|
| README.md | Addition | Implementation validation, cross-pollination graph |
| principles.md | Strengthening | Category laws table, orthogonality sub-principle, **Accursed Share (meta-principle)** |
| anatomy.md | Synthesis | Compositional core, Observable protocol, Symbiont pattern |
| bootstrap.md | Synthesis | BootstrapWitness, Cooled/Superposed functors, entropy physics, **Semantic Invariant**, **Ergodic Strategy**, **Active Inference** |
| testing.md | New | T-gents taxonomy + Socratic/Chaos patterns |
| reliability.md | New | Multi-layer reliability pattern, **Ensemble Reset (opt-in)** |
| archetypes.md | New (Optional) | Emergent patterns (Consolidator, Questioner, Shapeshifter, Spawner, Uncertain) |
| w-gents/stigmergy.md | New (TRANSFORMATIVE) | **Chalkboard Architecture** - W-gent as pheromone field with push/WebSocket |
| c-gents/curry-howard.md | New | **Prompts as Types** - Curry-Howard correspondence for agents |
| i-gents/messenger.md | New | **Messenger Protocol (Streaming Functor)** - Async streaming chat interface |
| i-gents/view-functor.md | New | **View Functor** - Widget ontology, agent → UI deterministic mapping |
| economics/central-bank.md | New | **Metered Functor** - Token budgets, auctions, Kelvin circulation |
| m-gents/README.md | New | **M-gents** - Holographic associative memory, memory as morphism |
| observability/narrator.md | New | **Narrator Agent** - OpenTelemetry for thoughts, time-travel debugging |

---

## Implementation Evidence

All proposed updates are validated by existing implementation OR have clear implementation paths:

| Pattern | Implementation | Tests | Status |
|---------|----------------|-------|--------|
| Category laws | bootstrap/types.py, agents/a/skeleton.py | BootstrapWitness tests | ✅ Validated |
| Protocols | agents/a/skeleton.py:138-187 | Protocol check tests | ✅ Validated |
| Symbiont | agents/d/symbiont.py | test_symbiont.py | ✅ Validated |
| JIT wrapper | agents/j/factory_integration.py | Phase 4 tests | ✅ Validated |
| Functors | agents/c/functor.py | Law validation tests | ✅ Validated |
| T-gents taxonomy | agents/t/*.py | 150+ T-gent tests | ✅ Validated |
| Multi-layer reliability | agents/e/*.py | E-gent integration tests | ✅ Validated |
| Entropy budget | agents/d/entropy.py, agents/j/reality.py | Entropy tracking tests | ✅ Validated |
| Observable | agents/w/*.py, agents/i/*.py | W-gent/I-gent tests | ✅ Validated |
| **Accursed Share** | T-gents Type II Saboteurs | Chaos testing framework | 📐 Architectural |
| **Semantic Invariant** | (new) agents/c/invariant.py | LLM-based drift detection | 📐 Architectural |
| **Ergodic Strategy** | (new) agents/a/ensemble.py | Consensus selection tests | 📐 Architectural (opt-in) |
| **Stigmergy** | W-gent WebSocket/SSE push | Pheromone response tests | 🔄 Transformative |
| **Curry-Howard** | P-gents parsing as proof checking | Type inhabitance tests | 📐 Architectural |
| **Active Inference** | (new) agents/a/inference.py | Surprisal tracking tests | 📐 Architectural (opt-in) |
| **Messenger Protocol** | (new) agents/i/messenger.py | Streaming functor tests | 📐 Architectural |
| **View Functor** | (new) agents/i/view.py | Widget ontology tests | 📐 Architectural |
| **Metered Functor** | (new) agents/economics/bank.py | Central bank + auction tests | 📐 Architectural |
| **M-gents** | (new) agents/m/*.py | Holographic memory tests | 📐 Architectural |
| **Narrator Agent** | (new) agents/o/narrator.py | Time-travel replay tests | 📐 Architectural |

**Legend**: ✅ = Implemented and tested | 📐 = Architectural slot defined | 🔄 = Transformative (breaks purity)

---

## Final Assessment

**Verdict**: **Accept and Merge**

This proposal elevates the framework from "Software Engineering" to "Applied Mathematical Physics"—grounded in rigorous theory, validated by implementation.

### Validation Criteria

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **Verification** | ✅ | BootstrapWitness provides mathematical confidence |
| **Scalability** | ✅ | Symbiont pattern solves memory/state bottleneck |
| **Resilience** | ✅ | T-gent + Reliability Stack + **Ergodic Strategy** creates antifragile systems |
| **Novelty** | ✅ | Creates architectural slots for Hypnagogic, Darwinian, Polymorphic, **Stigmergic** agents |
| **Theoretical Rigor** | ✅ | Noether (conservation), Curry-Howard (types), Free Energy (prediction) |
| **Serendipity** | ✅ | Accursed Share legitimizes exploration, prevents brittle optimization |
| **Model Agnosticism** | ✅ | Semantic Invariant ensures consistency across LLM backends |

### The Hegelian Synthesis

| Element | Description |
|---------|-------------|
| *Thesis* | The pure Spec (Idealism) |
| *Antithesis* | The messy Implementation (Materialism) |
| *Synthesis* | The **Verified Protocol** (The Realized Ideal) |

The synthesis is valid: implementation wisdom AND theoretical physics have been elevated to spec-level principles while preserving the original vision.

### The New Foundations

| Foundation | Source | Contribution |
|------------|--------|--------------|
| Accursed Share | Bataille | Philosophy of slop; meta-principle for productive waste |
| Noether's Theorem | Physics | LLM-native semantic conservation; credo drift detection |
| Ergodicity | Statistical Mechanics | Ensemble > Retry; opt-in for heavy constructions |
| Stigmergy | Biology | W-gent as pheromone field; **TRANSFORMATIVE** (taints agent purity) |
| Curry-Howard | Logic | Prompts as types; parsing as proof checking |
| Free Energy | Neuroscience | Active inference; opt-in for irreversible actions |
| Messenger Protocol | Industry Practice | Streaming functor; production chat integration |
| View Functor | Semiotics | Widget ontology; deterministic agent → UI mapping |
| Metered Functor | Economics | Central bank; Kelvin circulation; auction mechanics |
| M-gents | Holography | Memory as morphism; graceful degradation; ethics as geometry |
| Narrator Agent | OpenTelemetry | Time-travel debugging; replay from serialized inputs |

### The Question of Bias

The Accursed Share principle deserves special attention. By allocating resources to "unknown unknowns," we acknowledge:

1. **We don't know what we don't know** — exploration budgets aren't waste
2. **Sabotage is productive** — T-gents Saboteurs stress-test for unknown failure modes
3. **Joy is not overhead** — personality and delight are the Accursed Share spent well
4. **We have no bias toward utility** — an agent that only optimizes cannot discover

This is philosophically significant: kgents refuses the efficiency religion that dominates AI engineering.

---

*This proposal synthesizes implementation wisdom AND theoretical physics while preserving the tasteful, curated, ethical, joy-inducing, composable, heterarchical, generative soul of kgents.*

*The framework transforms from a collection of scripts into a **computational calculus grounded in physics**—interaction is more fundamental than identity, and the wise system spends its surplus on the unknown.*
