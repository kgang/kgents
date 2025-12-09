# Anatomy of an Agent

What constitutes an agent in the kgents specification?

---

## Definition

> An **agent** is an autonomous entity that receives input, processes it according to its nature, and produces output—while maintaining the capacity for composition with other agents.

This definition is deliberately minimal. An agent is not:
- Required to use a particular LLM
- Required to have memory
- Required to use tools
- Required to be "intelligent"

An agent *is* required to:
- Have a defined interface (input/output types)
- Be composable (see [principles.md](principles.md#5-composable))
- Fulfill the ethical requirements of the specification

---

## The Minimal Agent

```
┌─────────────────────────────────────┐
│              Agent                  │
│                                     │
│  Input ────→ [Process] ────→ Output │
│                                     │
└─────────────────────────────────────┘
```

At minimum, an agent:
1. **Accepts input** of a declared type
2. **Processes** according to its specification
3. **Produces output** of a declared type

---

## The Compositional Core

The minimal agent is defined by THREE properties, not operations:

```python
Agent[A, B]:
    name: str                     # Identity
    invoke(input: A) -> B         # Behavior
    __rshift__ -> ComposedAgent   # Composition
```

Composition (`>>`) is not a "hook"—it is constitutive. An entity without `>>` is a function, not an agent.

**The Category-Theoretic Shift**:

| Paradigm | Definition | Implication |
|----------|------------|-------------|
| OOP (traditional) | Object defined by internal state + methods | Identity is fundamental |
| Category Theory (kgents) | Object defined by relationships (arrows) | **Interaction is fundamental** |

By defining `>>` as the skeleton, we assert that **interaction is more fundamental than identity**.

---

## Agent Components

Agents MAY include these components:

### Identity
- **Name**: Human-readable identifier
- **Genus**: Which letter category (A-gent, B-gent, etc.)
- **Purpose**: One-sentence description of why this agent exists

### Interface
- **Input Schema**: What the agent accepts
- **Output Schema**: What the agent produces
- **Error Schema**: How failures are communicated

### Behavior
- **Process Definition**: What transformation occurs
- **Constraints**: Boundaries on behavior
- **Guarantees**: What the agent promises

### State (Optional)
- **Memory**: Information retained across invocations
- **Configuration**: Parameters that modify behavior
- **Context**: Environmental awareness

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

### Composition Hooks (Required)
- **Pre-composition**: How to prepare for incoming composition
- **Post-composition**: How to prepare outgoing results
- **Identity composition**: Behavior when composed with identity agent

---

## Agent Types by Statefulness

### Stateless Agents
- Same input always produces same output
- Easiest to compose and reason about
- Example: A transformation agent that reformats text

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

**Traditional characteristics still apply**:
- Maintain information across invocations
- Must declare state schema explicitly
- Must handle state persistence/restoration
- Example: K-gent (accumulates preferences over time)

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

*Zen Principle: The mind that never rests, never learns.*

### Contextual Agents
- Aware of environment but don't persist state
- May behave differently based on context
- Example: An agent that considers time of day

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

**Why ephemeral?**

Ephemeral agents serve **immediate computational needs** without cluttering the specification. They are tools generated on-demand, not concepts worthy of permanent specification.

**Example**: A J-gent needs to "parse Java stack traces for OOM errors." Rather than create a permanent `JavaStackTraceParser` agent and add it to spec/, the J-gent:

1. Compiles an ephemeral agent for this specific task
2. Validates it (Chaosmonger → JITSafetyJudge)
3. Executes it in sandbox
4. Caches it (by hash) for reuse in this session
5. Garbage collects when session ends

**Principles still apply**: Ephemeral agents are still evaluated by Judge before execution. They still obey composition laws. They're just not **permanent** members of the specification.

**See**: `spec/j-gents/jit.md` for JIT compilation, `spec/j-gents/integration.md` for caching

---

## Agent Lifecycle

```
    ┌──────────┐
    │ Dormant  │
    └────┬─────┘
         │ activate
         ▼
    ┌──────────┐
    │  Ready   │◄────────────┐
    └────┬─────┘             │
         │ invoke            │
         ▼                   │
    ┌──────────┐             │
    │Processing│             │ complete
    └────┬─────┘             │
         │                   │
         └───────────────────┘
```

1. **Dormant**: Agent is defined but not instantiated
2. **Ready**: Agent is instantiated and awaiting input
3. **Processing**: Agent is handling an invocation
4. **Complete**: Returns to Ready (or Dormant if disposed)

---

## Composition

The key property that distinguishes kgents agents from arbitrary functions:

```
Agent A: Input_A → Output_A
Agent B: Input_B → Output_B

If Output_A is compatible with Input_B:
  A ∘ B: Input_A → Output_B
```

Composition MUST be:
- **Associative**: (A ∘ B) ∘ C = A ∘ (B ∘ C)
- **Respect identity**: A ∘ id = A, id ∘ A = A

See [c-gents/composition.md](c-gents/composition.md) for formal treatment.

---

## Anti-Anatomy: What An Agent Is Not

- **Not a chatbot**: Agents don't require conversational interface
- **Not a tool**: Tools are used *by* agents; agents are not tools themselves
- **Not a prompt**: A prompt may configure an agent; it is not the agent
- **Not a model**: LLMs may power agents; they are not agents themselves
- **Not omniscient**: Agents have bounded knowledge and capability
