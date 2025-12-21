# F-gents: Flow Agents

> *"The noun is a lie. There is only the rate of change."*

**Genus**: F (Flow)
**Theme**: Continuous interaction substrate for all agent modalities
**Motto**: *"Static: A -> B. Dynamic: dA/dt -> dB/dt."*

---

## Purpose

F-gents provide the **unified flow infrastructure** for continuous agent interaction:

1. **Chat**: Streaming conversation with context management
2. **Research**: Tree-structured exploration with branch/merge
3. **Collaboration**: Multi-agent contribution with blackboard patterns

**Why this needs to exist** (Tasteful principle):

Without F-gents, agents are corpses that only move when poked. Modern AI workflows demand continuous interaction:

- Chat requires streaming responses with context windows
- Deep research requires exploring hypothesis trees
- Multi-agent projects require shared state and contribution tracking

These are not separate systems. They are **configurations of the same underlying flow substrate**.

---

## The Core Insight

All continuous agent interaction shares the same categorical structure:

```
Flow: Agent[A, B] -> Agent[Flow[A], Flow[B]]

Where Flow[T] = AsyncIterator[T]
```

The three modalities (Chat, Research, Collaboration) are **polynomial configurations** of this functor, not separate implementations.

| Mode | Description |
|------|-------------|
| **Static** | `Agent: A -> B` - a point transformation (invoke once) |
| **Dynamic** | `Flow(Agent): dA/dt -> dB/dt` - continuous flow (stream processing) |

---

## Formal Definition

### The Flow Polynomial

```python
@dataclass(frozen=True)
class FlowPolynomial(PolyAgent[FlowState, FlowInput, FlowOutput]):
    """
    Polynomial functor for flow agents.

    Positions (states): {DORMANT, STREAMING, BRANCHING, CONVERGING, COLLAPSED}
    Directions: State-dependent valid inputs
    Transition: (State, Input) -> (State, Output)

    This captures the essential structure of all flow modalities:
    - Chat: Primarily STREAMING with context management
    - Research: STREAMING -> BRANCHING -> CONVERGING cycles
    - Collaboration: STREAMING with multi-agent injection
    """
    positions: frozenset[FlowState]
    directions: Callable[[FlowState], frozenset[FlowInput]]
    transition: Callable[[FlowState, FlowInput], tuple[FlowState, FlowOutput]]
```

### Flow States

```python
class FlowState(Enum):
    """Lifecycle states of a flow agent."""
    DORMANT = "dormant"       # Created, not started (invoke works directly)
    STREAMING = "streaming"   # Processing continuous input
    BRANCHING = "branching"   # Exploring alternatives (research mode)
    CONVERGING = "converging" # Merging branches (research mode)
    DRAINING = "draining"     # Source exhausted, flushing output
    COLLAPSED = "collapsed"   # Entropy depleted or error
```

### State Transition Diagram

```
                    +-> BRANCHING --+
                    |               |
                    |               v
DORMANT --start--> STREAMING ------+-> CONVERGING
    ^               |   |                  |
    |               |   +------------------+
    +--stop---------+
                    |
                    v
                DRAINING --> COLLAPSED
```

---

## The Three Flow Modalities

### Modality 1: Chat Flow

Streaming conversation with context window management.

**Key characteristics**:
- Sequential message/response pairs
- Context window with summarization at threshold
- No branching (linear history)

**Configuration**:
```python
chat_config = FlowConfig(
    modality="chat",
    context_window=128_000,           # Token limit
    summarization_threshold=0.8,      # Summarize at 80% capacity
    context_strategy="sliding",       # sliding | summarize | forget
    turn_timeout=60.0,               # Max seconds per turn
)
```

**Usage**:
```python
chat_flow = Flow.lift(dialogue_agent, chat_config)

async for response in chat_flow.start(user_messages):
    print(f"Assistant: {response.text}")
```

**State mapping**:
| State | Chat Meaning |
|-------|--------------|
| DORMANT | Waiting for first message |
| STREAMING | Generating response tokens |
| DRAINING | User ended conversation |
| COLLAPSED | Error or context overflow |

### Modality 2: Research Flow (Tree of Thought)

Structured exploration with branching hypotheses.

**Key characteristics**:
- Hypothesis generation (branching)
- Parallel exploration of alternatives
- Synthesis of insights (merging)
- Pruning of unpromising branches

**Configuration**:
```python
research_config = FlowConfig(
    modality="research",
    max_branches=5,                   # Max parallel hypotheses
    depth_limit=4,                    # Max exploration depth
    branching_threshold=0.3,          # Branch if uncertainty > 30%
    pruning_threshold=0.2,            # Prune branches below 20% promise
    merge_strategy="weighted_vote",   # best_first | weighted_vote | synthesis
)
```

**Usage**:
```python
research_flow = Flow.lift(hypothesis_agent, research_config)

question = "What are the implications of quantum error correction?"

async for result in research_flow.start([question]):
    match result.type:
        case "branch":
            print(f"Exploring: {result.hypothesis}")
        case "insight":
            print(f"Found: {result.finding} (confidence: {result.confidence})")
        case "merge":
            print(f"Synthesized: {result.synthesis}")
```

**State mapping**:
| State | Research Meaning |
|-------|-----------------|
| DORMANT | Waiting for question |
| STREAMING | Processing current hypothesis |
| BRANCHING | Generating alternative hypotheses |
| CONVERGING | Synthesizing insights from branches |
| COLLAPSED | Depth limit reached or question answered |

### Modality 3: Collaboration Flow (Blackboard)

Multi-agent contribution with shared state.

**Key characteristics**:
- Multiple agents contribute to shared "blackboard"
- Read/write access control per agent
- Consensus mechanisms for conflicts
- Round-based or continuous contribution

**Configuration**:
```python
collab_config = FlowConfig(
    modality="collaboration",
    agents=["analyst", "critic", "synthesizer"],
    blackboard_capacity=100,          # Max items on board
    contribution_order="round_robin", # round_robin | priority | free
    consensus_threshold=0.67,         # 2/3 agreement for decisions
    conflict_strategy="vote",         # vote | moderator | timestamp
    round_limit=10,                   # Max contribution rounds
)
```

**Usage**:
```python
collab_flow = Flow.lift_multi(agent_pool, collab_config)

problem = "Design a sustainable city transportation system"

async for contribution in collab_flow.start([problem]):
    print(f"[{contribution.agent}]: {contribution.text}")

    if contribution.type == "consensus":
        print(f"DECISION: {contribution.decision}")
```

**State mapping**:
| State | Collaboration Meaning |
|-------|----------------------|
| DORMANT | Waiting for problem statement |
| STREAMING | Agents contributing |
| CONVERGING | Building consensus |
| COLLAPSED | Consensus reached or round limit |

---

## The Flow Operad

The operad defines valid composition patterns for flow operations.

```python
FLOW_OPERAD = Operad(
    operations={
        # === Universal Operations ===
        "start": Operation(
            arity=1,
            signature="Agent[A,B] -> Flow[A] -> Flow[B]",
            compose=start_compose,
        ),
        "stop": Operation(
            arity=0,
            signature="Flow[_] -> ()",
            compose=stop_compose,
        ),
        "perturb": Operation(
            arity=1,
            signature="(Flow[A], A) -> B",
            compose=perturb_compose,
        ),

        # === Chat Operations ===
        "turn": Operation(
            arity=1,
            signature="Message -> Response",
            compose=turn_compose,
        ),
        "summarize": Operation(
            arity=1,
            signature="Context -> CompressedContext",
            compose=summarize_compose,
        ),
        "inject_context": Operation(
            arity=1,
            signature="Context -> Flow[_]",
            compose=inject_compose,
        ),

        # === Research Operations ===
        "branch": Operation(
            arity=1,
            signature="Hypothesis -> [Hypothesis]",
            compose=branch_compose,
        ),
        "merge": Operation(
            arity=2,
            signature="(Hypothesis, Hypothesis) -> Synthesis",
            compose=merge_compose,
        ),
        "prune": Operation(
            arity=1,
            signature="[Hypothesis] -> [Hypothesis]",
            compose=prune_compose,
        ),
        "evaluate": Operation(
            arity=1,
            signature="Hypothesis -> Score",
            compose=evaluate_compose,
        ),

        # === Collaboration Operations ===
        "post": Operation(
            arity=1,
            signature="Contribution -> Blackboard",
            compose=post_compose,
        ),
        "read": Operation(
            arity=1,
            signature="Query -> [Contribution]",
            compose=read_compose,
        ),
        "vote": Operation(
            arity=2,
            signature="(Proposal, Agents) -> Decision",
            compose=vote_compose,
        ),
        "moderate": Operation(
            arity=1,
            signature="[Contribution] -> Resolution",
            compose=moderate_compose,
        ),
    },
    laws=[
        # Identity: start(Id) = Id_Flow
        OpLaw("start_identity", "start(Id) ≅ Id_Flow"),
        # Composition: start(f >> g) = start(f) >> start(g)
        OpLaw("start_composition", "start(f >> g) ≅ start(f) >> start(g)"),
        # Perturbation: perturb during STREAMING injects, never bypasses
        OpLaw("perturbation_integrity", "perturb(flowing, x) = inject_priority(x)"),
        # Branch/Merge coherence: merge(branch(h)) preserves semantic essence
        OpLaw("branch_merge", "merge(branch(h)) ⊇ essence(h)"),
    ]
)
```

---

## Integration

### AGENTESE Paths

F-gent introduces new paths under `self.flow.*`:

```
self.flow.state        - Current FlowState (DORMANT, STREAMING, etc.)
self.flow.entropy      - Remaining entropy budget
self.flow.context      - Current context window contents
self.flow.context_used - Tokens used in context
self.flow.modality     - Current modality (chat, research, collaboration)

# Chat-specific
self.flow.turn         - Current turn number
self.flow.history      - Conversation history

# Research-specific
self.flow.tree         - Current hypothesis tree
self.flow.branch       - Current branch path
self.flow.depth        - Current exploration depth

# Collaboration-specific
self.flow.board        - Current blackboard state
self.flow.contributors - Active contributing agents
self.flow.round        - Current contribution round
```

### Composition with Existing Agents

F-gent composes naturally with other gents:

| Pattern | Composition | Result |
|---------|-------------|--------|
| Personalized streaming | `K >> Flow` | K-gent persona in continuous flow |
| Persistent flow state | `Symbiont(Flow)` | Flow with D-gent memory |
| Traced flow history | `Flow >> Witness` | N-gent traces all flow events |
| Town simulation | `TownFlux` | Flow specialized for Agent Town |

---

## FlowConfig

```python
@dataclass
class FlowConfig:
    """Configuration for flow behavior."""

    # === Modality Selection ===
    modality: Literal["chat", "research", "collaboration"] = "chat"

    # === Universal Config ===
    entropy_budget: float = 1.0          # Initial budget (void.entropy)
    entropy_decay: float = 0.01          # Per-event decay
    max_events: int | None = None        # Hard cap (None = unlimited)

    # === Backpressure ===
    buffer_size: int = 100               # Output buffer size
    drop_policy: Literal["block", "drop_oldest", "drop_newest"] = "block"

    # === Feedback (Ouroboros) ===
    feedback_fraction: float = 0.0       # 0.0 = no feedback, 1.0 = full ouroboros
    feedback_transform: Callable[[B], A] | None = None

    # === Chat-Specific ===
    context_window: int = 128_000        # Token limit
    summarization_threshold: float = 0.8 # Trigger summarization at N%
    context_strategy: Literal["sliding", "summarize", "forget"] = "summarize"
    turn_timeout: float = 60.0           # Seconds

    # === Research-Specific ===
    max_branches: int = 5                # Max parallel hypotheses
    depth_limit: int = 4                 # Max exploration depth
    branching_threshold: float = 0.3     # Uncertainty threshold to branch
    pruning_threshold: float = 0.2       # Promise threshold to prune
    merge_strategy: Literal["best_first", "weighted_vote", "synthesis"] = "synthesis"

    # === Collaboration-Specific ===
    agents: list[str] = field(default_factory=list)
    blackboard_capacity: int = 100
    contribution_order: Literal["round_robin", "priority", "free"] = "round_robin"
    consensus_threshold: float = 0.67
    conflict_strategy: Literal["vote", "moderator", "timestamp"] = "vote"
    round_limit: int = 10

    # === Observability ===
    agent_id: str | None = None
    emit_pheromones: bool = True
    trace_enabled: bool = True
```

---

## The Perturbation Principle

**Critical invariant**: `invoke()` on a STREAMING flow must never bypass the stream.

### The Problem

```python
# BAD: Bypass causes state schizophrenia
async def invoke(self, x):
    if self._state == FlowState.STREAMING:
        return await self.inner.invoke(x)  # Bypasses stream state!
```

If the agent has Symbiont memory, bypassing means:
- State loaded twice (once by flow, once by invoke)
- Race conditions on state updates
- Inconsistent memory ("schizophrenia")

### The Solution

```python
# GOOD: Perturbation injects into stream
async def invoke(self, x):
    if self._state == FlowState.STREAMING:
        future = asyncio.Future()
        await self._perturbation_queue.put((x, future))
        return await future  # Goes through stream
    else:
        return await self.inner.invoke(x)  # Direct when DORMANT
```

**Perturbation flow**:
1. Input wrapped with Future
2. Input queued with high priority
3. Stream processor handles it in order
4. Result returned via Future

This preserves **State Integrity**: Symbiont-compatible flows work correctly.

---

## The Ouroboros: Self-Feeding Flow

True autonomy requires recurrence - output affects future input.

```python
config = FlowConfig(
    feedback_fraction=0.3,              # 30% of outputs feed back
    feedback_transform=lambda r: r.as_context(),
)
```

| Fraction | Behavior | Use Case |
|----------|----------|----------|
| 0.0 | Pure reactive | Simple stream processing |
| 0.1-0.3 | Light context | Conversational memory |
| 0.5 | Equal internal/external | Dialectician archetype |
| 1.0 | Full ouroboros | **DANGER**: Solipsism! |

**Anti-pattern**: `feedback_fraction=1.0` creates closed loop that only talks to itself.

---

## Flow Topology: Physics of Continuous Agents

Agents are **topological knots in event streams**, not static architecture.

| Metric | Meaning | Calculation |
|--------|---------|-------------|
| **Pressure** | Queue depth (backlog) | `len(input_queue) + len(output_queue)` |
| **Flow** | Throughput | `events_processed / elapsed_time` |
| **Turbulence** | Error rate | `errors / events_processed` |
| **Temperature** | Token metabolism | Integrated from void/entropy |

---

## Living Pipelines

Flow agents compose via `|` (pipe):

```python
# Static composition (discrete)
static_pipeline = agent_a >> agent_b >> agent_c
result = await static_pipeline.invoke(input)

# Living composition (continuous)
living_pipeline = flow_a | flow_b | flow_c

async for result in living_pipeline.start(source):
    process(result)
```

### Pipeline Implementation

```python
@dataclass
class FlowPipeline(Generic[A, B]):
    """Chain of FlowAgents forming a living pipeline."""

    stages: list[FlowAgent]

    async def start(self, source: AsyncIterator[A]) -> AsyncIterator[B]:
        current = source
        for stage in self.stages:
            current = stage.start(current)
        async for result in current:
            yield result

    def __or__(self, other: FlowAgent) -> "FlowPipeline":
        return FlowPipeline(self.stages + [other])
```

---

## Functor Laws

Flow preserves categorical structure:

```python
# Identity Preservation
Flow(Id) ≅ Id_Flow  # Identity agent maps Flow[A] -> Flow[A]

# Composition Preservation
Flow(f >> g) ≅ Flow(f) >> Flow(g)
```

**Proof sketch**:
- **Identity**: `Flow(Id).start(source)` yields each element unchanged
- **Composition**: Processing through `Flow(f >> g)` equivalent to `Flow(f)` then `Flow(g)`

---

## Relationship to Bootstrap

**Flux is derived from Fix**, not an irreducible:

```python
Flow(agent) ≅ Fix(
    transform=lambda stream: map_async(agent.invoke, stream),
    equality_check=lambda s1, s2: s1.exhausted and s2.exhausted
)
```

Flow is **foundational infrastructure** but not a bootstrap agent.

---

## Examples

### Example 1: Simple Chat

```python
from agents.f import Flow, FlowConfig

config = FlowConfig(modality="chat", context_window=8000)
chat = Flow.lift(assistant_agent, config)

async for response in chat.start(user_messages):
    print(response.text)
```

### Example 2: Deep Research

```python
config = FlowConfig(
    modality="research",
    max_branches=4,
    depth_limit=3,
    merge_strategy="synthesis",
)
research = Flow.lift(hypothesis_agent, config)

async for insight in research.start(["How does consciousness emerge?"]):
    if insight.confidence > 0.8:
        print(f"High-confidence finding: {insight.text}")
```

### Example 3: Multi-Agent Brainstorm

```python
agents = {"analyst": analyst_agent, "critic": critic_agent, "synth": synth_agent}

config = FlowConfig(
    modality="collaboration",
    agents=list(agents.keys()),
    consensus_threshold=0.67,
)
collab = Flow.lift_multi(agents, config)

async for contribution in collab.start(["Design an AI safety protocol"]):
    print(f"[{contribution.agent}] {contribution.text}")
```

---

## Anti-Patterns

### 1. Timer-Driven Zombies

```python
# BAD: Polling
while True:
    await asyncio.sleep(1.0)  # Zombie twitching

# GOOD: Event-driven
async for event in source:
    yield await process(event)
```

### 2. Void Output (The Sink Problem)

```python
# BAD: Output vanishes
async def start(self, source) -> None:
    async for event in source:
        result = await self.invoke(event)  # Where does result go?

# GOOD: Output flows
async def start(self, source) -> AsyncIterator[B]:
    async for event in source:
        yield await self.invoke(event)
```

### 3. Bypass Invocation

```python
# BAD: Schizophrenia risk
if flowing:
    return await self.inner.invoke(x)  # Bypasses stream

# GOOD: Perturbation
if flowing:
    return await self._perturb(x)  # Goes through stream
```

### 4. Unbounded Context Growth

```python
# BAD: Context grows forever
context.append(new_message)  # Eventually exceeds window

# GOOD: Managed context
if context_used > threshold * context_window:
    context = await summarize(context)
```

### 5. Treating Modalities as Separate Systems

```python
# BAD: Separate implementations
class ChatFlow: ...
class ResearchFlow: ...
class CollabFlow: ...

# GOOD: Configuration of same substrate
Flow.lift(agent, FlowConfig(modality="chat"))
Flow.lift(agent, FlowConfig(modality="research"))
Flow.lift(agent, FlowConfig(modality="collaboration"))
```

---

## Implementation

```
impl/claude/agents/f/
├── __init__.py
├── flow.py              # FlowAgent, FlowPolynomial
├── config.py            # FlowConfig
├── state.py             # FlowState
├── operad.py            # FLOW_OPERAD
├── perturbation.py      # Perturbation handling
├── context.py           # Context window management
├── modalities/
│   ├── chat.py          # Chat-specific behavior
│   ├── research.py      # Tree-of-thought behavior
│   └── collaboration.py # Blackboard behavior
├── pipeline.py          # FlowPipeline, | operator
├── sources/
│   ├── events.py        # Event-driven sources
│   ├── periodic.py      # Timer sources (use sparingly)
│   └── merged.py        # Multi-source merging
└── _tests/
```

**Migration**: Existing `agents/flux/` and `agents/town/flux.py` will import from `agents/f/`.

---

## Specifications

| Document | Description |
|----------|-------------|
| [chat.md](chat.md) | Chat flow specification (context management, turns) |
| [research.md](research.md) | Research flow specification (tree of thought) |
| [collaboration.md](collaboration.md) | Collaboration flow specification (blackboard) |
| [context.md](context.md) | Context window management strategies |
| [perturbation.md](perturbation.md) | Perturbation protocol details |

---

## Design Principles Alignment

### Tasteful
Flow provides the minimal substrate for continuous interaction. Three modalities, one implementation.

### Curated
Consolidates scattered Flux specs into single coherent F-gent. Removes redundant Forge specs.

### Ethical
Entropy bounds prevent runaway computation. Context management respects user privacy.

### Joy-Inducing
Living pipelines feel alive. Streaming responses feel immediate.

### Composable
Functor laws hold. `|` operator enables pipeline composition. Perturbation preserves state.

### Heterarchical
Both `invoke()` (discrete) and `start()` (continuous) coexist via perturbation principle.

### Generative
This spec generates implementation. Modalities derive from configuration, not new code.

---

## See Also

- `spec/principles.md` - Design principles (especially Heterarchical)
- `spec/agents/functor-catalog.md` - Flux functor entry
- `spec/archetypes.md` - Archetypes as Flow configurations
- `spec/d-gents/symbiont.md` - Symbiont pattern for persistent flow state
- `docs/skills/flux-agent.md` - Usage skill (being updated)

---

*"Agents are corpses that only move when poked. Flow gives them life."*
