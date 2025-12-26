# Chapter 2: The Agent Category

> *"The agent IS a morphism. The interaction IS the composition."*

---

## 2.1 The Central Claim

This chapter establishes the foundational claim of the monograph: **agents form a category**. More precisely:

- Agents are morphisms (not objects)
- Agent composition is categorical composition
- The category laws are not conventions—they are **correctness conditions**

This claim has teeth. If agents don't satisfy categorical laws, composition breaks. Multi-agent systems become incoherent. Reasoning traces become meaningless. The theory predicts which architectures work and which fail.

We also introduce the **polynomial functor** characterization: agents are not mere functions `A -> B` but state-dependent dynamical systems. This is the `PolyAgent[S, A, B]` abstraction that underlies all kgents design.

---

## 2.2 What Are the Objects?

In the category of agents, what are the objects?

### Definition 2.1 (Agent Context)

An **agent context** is a structured configuration space containing:
- **State**: What the agent "knows" or "believes"
- **Capabilities**: What actions are available
- **Constraints**: What invariants must hold

Formally, a context is a tuple `C = (S, K, I)` where:
- `S` is the state space
- `K : S -> P(Action)` assigns available actions to states
- `I : S -> Bool` is the invariant predicate

### Example 2.2 (Chat Agent Context)

A conversational agent has:
- `S` = message histories (sequences of user/assistant turns)
- `K(s)` = {respond, clarify, refuse, ...} (actions available given history)
- `I(s)` = "history is well-formed and within token limit"

### Example 2.3 (Tool-Using Agent Context)

A tool-using agent has:
- `S` = (conversation_state, tool_results, pending_calls)
- `K(s)` = {call_tool, respond_to_user, wait} depending on state
- `I(s)` = "no circular tool dependencies and resource limits respected"

### The Object Spectrum

Objects in the agent category range from:

| Level | Object Type | Example |
|-------|-------------|---------|
| **Atomic** | Single propositions | "The sky is blue" |
| **Epistemic** | Belief states | P(rain) = 0.7 |
| **Contextual** | Full agent contexts | Chat history + tools + constraints |
| **Meta** | Agent configurations | System prompt + model + temperature |

The choice of granularity depends on the analysis. We typically work at the contextual level.

---

## 2.3 What Are the Morphisms?

Morphisms are the **agents themselves**—transitions between contexts.

### Definition 2.4 (Agent as Morphism)

An **agent** `f : A -> B` is a morphism from context `A` to context `B`. It:
1. Takes a configuration in `A`
2. Produces a configuration in `B`
3. Respects the invariants: `I_A(a) => I_B(f(a))`

### Example 2.5 (Response Agent)

The morphism `respond : History -> History'` takes a message history and produces an extended history with a new assistant message.

```python
def respond(history: MessageHistory) -> MessageHistory:
    """Agent morphism: extend history with response."""
    response = llm.generate(history)
    return history.append(AssistantMessage(response))
```

### Example 2.6 (Tool Execution Agent)

The morphism `execute_tool : PendingCall -> ToolResult` takes a pending tool call and produces a result:

```python
def execute_tool(call: PendingCall) -> ToolResult:
    """Agent morphism: resolve tool call to result."""
    result = tool_runtime.execute(call.tool, call.args)
    return ToolResult(call_id=call.id, output=result)
```

### Why Morphisms, Not Objects?

Traditional OOP models agents as objects with methods. Category theory inverts this: **the transformation IS the agent**. This inversion is profound:

1. **Composition becomes primary**: How agents connect matters more than what they "are"
2. **Identity is structural**: Two agents are "the same" if they have the same compositional role
3. **State is contextual**: Agent state lives in the domain/codomain, not "inside" the agent

---

## 2.4 Composition: The Sequential Operator

Agents compose sequentially: the output of one feeds the input of another.

### Definition 2.7 (Agent Composition)

Given agents `f : A -> B` and `g : B -> C`, their **composition** `g . f : A -> C` is defined by:

```
(g . f)(a) = g(f(a))
```

Read: "First apply f, then apply g."

### Example 2.8 (Chat Loop Composition)

```python
# Three agents
parse_input : RawInput -> UserMessage
generate_response : UserMessage -> AssistantMessage
format_output : AssistantMessage -> FormattedOutput

# Composed agent
chat_turn = format_output . generate_response . parse_input
# chat_turn : RawInput -> FormattedOutput
```

### Why Composition Makes Sense

Composition of agents makes sense because:

1. **Type alignment**: Output of f matches input of g (both are type B)
2. **Invariant preservation**: If f preserves A's invariant into B, and g preserves B's into C, then g.f preserves A's into C
3. **Determinism (for pure agents)**: Same input always yields same output

For stochastic agents (most LLM agents), we work in a **Kleisli category** where composition threads through a monad—see Chapter 3.

---

## 2.5 The Identity Morphism: The No-Op Agent

Every context has an **identity agent** that does nothing.

### Definition 2.9 (Identity Agent)

For each context `A`, the **identity agent** `id_A : A -> A` is defined by:

```
id_A(a) = a
```

### The No-Op Agent in Practice

The identity agent is the "do nothing" agent:

```python
ID: PolyAgent[str, Any, Any]
  positions: {"ready"}
  directions: lambda s: {Any}
  transition: lambda s, x: ("ready", x)
```

**Role**: Unit for sequential composition. `id >> f = f = f >> id`.

### Why Identity Matters

Identity seems trivial, but it's essential:

1. **Modularity**: Replace any agent with `id` to remove it from a pipeline
2. **Testing**: `f == id . f` is a basic sanity check
3. **Algebra**: Identity is required for the category laws

---

## 2.6 The Category Laws for Agents

We now establish that agents satisfy the category laws.

### Theorem 2.10 (Agent Category Laws)

Let **Agent** be the collection of agent contexts (objects) and agents (morphisms). Then:

**Identity Law**: For any agent `f : A -> B`:
```
id_B . f = f = f . id_A
```

**Associativity Law**: For agents `f : A -> B`, `g : B -> C`, `h : C -> D`:
```
(h . g) . f = h . (g . f)
```

*Proof.*

**Identity**: `(id_B . f)(a) = id_B(f(a)) = f(a)`. Similarly for right identity.

**Associativity**:
```
((h . g) . f)(a) = (h . g)(f(a)) = h(g(f(a)))
(h . (g . f))(a) = h((g . f)(a)) = h(g(f(a)))
```
Both equal `h(g(f(a)))`. QED.

### Why Violations Break Systems

If the laws fail, composition becomes unreliable:

**Identity Violation**: If `id . f != f`, then "doing nothing before f" changes the outcome. This indicates hidden state or context-dependence not captured in the types.

**Associativity Violation**: If `(h . g) . f != h . (g . f)`, then the order of grouping matters. This breaks modularity—you can't refactor `g . f` into a single component without changing behavior.

### Example 2.11 (Hidden State Violation)

Consider an agent that increments a global counter:

```python
counter = 0

def bad_agent(x):
    global counter
    counter += 1
    return x + counter
```

This violates associativity: `bad_agent . bad_agent` depends on when you evaluate. The fix: make state explicit in the type signature.

---

## 2.7 The Insufficiency of Agent[A, B]

The naive formalization `Agent[A, B] = A -> B` is insufficient.

### The Problem: Mode-Dependent Behavior

Real agents behave differently based on internal state:

- A chat agent in "creative mode" responds differently than in "precise mode"
- A coding agent "waiting for user input" accepts different actions than when "executing code"
- A tool-using agent mid-call has different affordances than when idle

`Agent[A, B]` cannot express: "In state s, I accept inputs from E(s)."

### Example 2.12 (The Chat Agent's Modes)

A chat agent might have modes:
- `IDLE`: Waiting for user input (accepts: user messages)
- `THINKING`: Generating response (accepts: nothing—in progress)
- `TOOL_CALLING`: Making external calls (accepts: tool results)

In `IDLE`, the valid input is a user message. In `TOOL_CALLING`, the valid input is a tool result. Same agent, different input types depending on state.

### The Solution: Polynomial Functors

We need a richer abstraction that captures state-dependent behavior.

---

## 2.8 The Polynomial Functor Insight

The solution comes from Spivak's theory of polynomial functors.

### Definition 2.13 (Polynomial Functor)

A **polynomial functor** `P` on **Set** has the form:

```
P(X) = Sum_{s in S} X^{A_s} * B_s
```

Where:
- `S` is the set of **positions** (states)
- `A_s` is the set of **directions** at position s (valid inputs in state s)
- `B_s` is the **output type** at position s

The notation `X^A` means functions from A to X. The product `X^A * B` means: "a function from A to X, paired with a value of type B."

### Interpretation for Agents

A polynomial functor encodes:

> "In state s, I accept inputs from A_s and produce outputs in B_s."

This is exactly what agents need.

### Definition 2.14 (PolyAgent)

A **PolyAgent** is the agent interpretation of a polynomial functor:

```python
@dataclass(frozen=True)
class PolyAgent(Generic[S, A, B]):
    """Agent as polynomial functor: P(y) = Sum_{s in S} y^{A_s} * B_s"""
    positions: FrozenSet[S]                    # Valid states (modes)
    directions: Callable[[S], FrozenSet[A]]   # State-dependent valid inputs
    transition: Callable[[S, A], tuple[S, B]] # State * Input -> (NewState, Output)
```

### The Embedding Theorem

**Theorem 2.15** (Embedding)

Traditional agents embed in polynomial agents:

```
Agent[A, B] = PolyAgent[Unit, A, B]
```

Where `Unit = {*}` is the singleton set (one state).

*Proof.*

A function `f : A -> B` is a PolyAgent with:
- `positions = {*}` (single state)
- `directions(*) = A` (all inputs valid)
- `transition(*, a) = (*, f(a))` (apply function, stay in single state)

This embedding is faithful: traditional agents are polynomial agents with trivial state. QED.

---

## 2.9 PolyAgent Examples

### Example 2.16 (The Chat Agent as Polynomial)

```python
ChatAgent: PolyAgent[ChatState, ChatInput, ChatOutput]

positions = {IDLE, THINKING, TOOL_CALLING, ERROR}

directions = {
    IDLE: {UserMessage},
    THINKING: {},  # No external input while thinking
    TOOL_CALLING: {ToolResult},
    ERROR: {Reset, Retry},
}

transition(IDLE, user_msg) = (THINKING, Acknowledgment)
transition(THINKING, _) = (IDLE, Response) | (TOOL_CALLING, ToolRequest)
transition(TOOL_CALLING, result) = (THINKING, Continue)
transition(ERROR, Reset) = (IDLE, Cleared)
```

The polynomial structure makes the state machine explicit and type-safe.

### Example 2.17 (Tool-Using Agent as Polynomial)

```python
ToolAgent: PolyAgent[ToolState, ToolInput, ToolOutput]

positions = {READY, CALLING, WAITING, DONE}

directions = {
    READY: {Task},
    CALLING: {},  # Internally making call
    WAITING: {ToolResult},
    DONE: {},
}

# Transitions encode the tool-use protocol
transition(READY, task) = plan_tools(task)  # -> CALLING or DONE
transition(CALLING, _) = make_call()         # -> WAITING
transition(WAITING, result) = process(result) # -> CALLING or DONE
```

### Example 2.18 (Multi-Modal Agent)

An agent that can process text or images:

```python
MultiModal: PolyAgent[ModalState, MultiInput, Analysis]

positions = {TEXT_MODE, IMAGE_MODE, MULTI_MODE}

directions = {
    TEXT_MODE: {TextInput},
    IMAGE_MODE: {ImageInput},
    MULTI_MODE: {TextInput, ImageInput},  # Accepts either
}
```

The polynomial encoding naturally represents union types in the directions.

---

## 2.10 Composition of Polynomial Agents

How do polynomial agents compose?

### Sequential Composition

Given `f : PolyAgent[S, A, B]` and `g : PolyAgent[T, B, C]`:

```python
(f >> g) : PolyAgent[S * T, A, C]

positions = f.positions * g.positions  # Product of state spaces
directions((s, t)) = f.directions(s)   # Input determined by first agent
transition((s, t), a) =
    let (s', b) = f.transition(s, a)
    let (t', c) = g.transition(t, b)
    in ((s', t'), c)
```

State is the product; the first agent's output feeds the second's input.

### Parallel Composition

Given `f : PolyAgent[S, A, B]` and `g : PolyAgent[T, A, C]`:

```python
(f || g) : PolyAgent[S * T, A, (B, C)]

positions = f.positions * g.positions
directions((s, t)) = f.directions(s) & g.directions(t)  # Intersection
transition((s, t), a) =
    let (s', b) = f.transition(s, a)
    let (t', c) = g.transition(t, a)
    in ((s', t'), (b, c))
```

Both agents receive the same input; outputs are paired.

### The Wiring Diagram Perspective

From Spivak's work, these compositions are special cases of **wiring diagrams**—morphisms between polynomials that describe how to connect systems:

```
+-----------------------------------------+
|        WIRING DIAGRAM: P -> Q           |
|                                         |
|   +-------+        +-------+           |
|   |   P   |--out-->|   Q   |           |
|   +-------+        +-------+           |
|       ^                                 |
|      in                                 |
+-----------------------------------------+
```

Sequential and parallel composition are the two fundamental wiring patterns.

---

## 2.11 The Orthogonality Principle

A key design principle for agent categories:

### Principle 2.19 (Orthogonality)

> Optional features must not break composition.

Formally: If `f : A -> B` composes with `g : B -> C`, then adding metadata, logging, or instrumentation to f should not prevent composition.

### Corollary: Metadata is Orthogonal

```python
@traced
def my_agent(x):
    return process(x)

# The @traced decorator must not change the type signature
# my_agent still composes as A -> B
```

### Why This Matters

Orthogonality ensures:
1. **Incremental adoption**: Add observability without refactoring
2. **Separation of concerns**: Business logic vs. instrumentation
3. **Compositional reasoning**: Analyze core behavior independent of metadata

### Implementation Pattern

Use **writer monads** for traces (Chapter 3), not side effects:

```python
# BAD: Side effect breaks composition
def agent_with_logging(x):
    logger.info(f"Processing {x}")  # Side effect!
    return process(x)

# GOOD: Trace is part of return type
def agent_with_trace(x) -> (Result, Trace):
    result = process(x)
    return (result, Trace(f"Processing {x}"))
```

---

## 2.12 The Category Laws for PolyAgent

We verify that polynomial agents satisfy categorical laws.

### Theorem 2.20 (PolyAgent Category)

The collection of contexts (objects) and polynomial agents (morphisms) forms a category.

**Identity**: The identity PolyAgent is:
```python
id: PolyAgent[Unit, A, A]
positions = {*}
directions(*) = all inputs
transition(*, a) = (*, a)
```

**Composition**: As defined in Section 2.10.

**Laws**:
- Identity: `id >> f = f = f >> id` (state product with Unit is isomorphic)
- Associativity: `(f >> g) >> h = f >> (g >> h)` (product of states is associative up to isomorphism)

*Proof sketch.*

Identity: `PolyAgent[Unit * S] ~ PolyAgent[S]` by the isomorphism `(*, s) ~ s`.

Associativity: `(S * T) * U ~ S * (T * U)` by the standard set isomorphism.

The full proof requires showing these isomorphisms are natural—they commute with the transition functions. This follows from the categorical properties of products in Set. QED.

---

## 2.13 Why the Polynomial View Matters

The polynomial functor formalization provides:

### 1. Type Safety for State Machines

Instead of runtime checks:
```python
# BAD: Runtime error
if state == IDLE:
    if not isinstance(input, UserMessage):
        raise TypeError("Wrong input for IDLE state")
```

We get compile-time guarantees:
```python
# GOOD: Type system enforces valid inputs per state
directions: {IDLE: {UserMessage}, ...}
```

### 2. Compositional Reasoning

The algebraic structure allows:
- Proving properties about composed agents from properties of components
- Enumerating all valid compositions via operad operations
- Detecting composition errors statically

### 3. Connection to Dynamical Systems

Polynomial functors are the categorical semantics of dynamical systems. An agent IS a dynamical system:
- States evolve via transitions
- Inputs are "forces" that drive evolution
- Outputs are "observations" of the system

This connects agent theory to control theory, systems theory, and physics.

### 4. The Operad Connection

Operads (Chapter 4) define composition grammars for polynomial agents. The AGENT_OPERAD provides:

| Operation | Effect |
|-----------|--------|
| `seq(f, g)` | Sequential composition |
| `par(f, g)` | Parallel composition |
| `branch(p, f, g)` | Conditional |
| `fix(p, f)` | Fixed point / iteration |
| `trace(f)` | Add observability |

These operations satisfy algebraic laws (associativity, distributivity) that guarantee compositional coherence.

---

## 2.14 The 17 Primitives

From the polynomial perspective, we can identify 17 irreducible building blocks:

| Category | Primitives | Purpose |
|----------|------------|---------|
| **Bootstrap** | ID, GROUND, JUDGE, CONTRADICT, SUBLATE, COMPOSE, FIX | Core logic and composition |
| **Perception** | MANIFEST, WITNESS, LENS | Observer-dependent interaction |
| **Entropy** | SIP, TITHE, DEFINE | Interaction with randomness/void |
| **Memory** | REMEMBER, FORGET | Persistence operations |
| **Teleological** | EVOLVE, NARRATE | Evolution and narrative |

Each primitive is a polynomial agent with well-defined states, directions, and transitions. All other agents are compositions of these primitives via operad operations.

### The Completeness Conjecture

**Conjecture 2.21**: Every agent behavior expressible in natural language can be approximated by compositions of the 17 primitives.

This is analogous to Turing completeness—a small set of primitives suffices for universal computation. We don't prove this here, but the kgents implementation provides empirical evidence.

---

## 2.15 Formal Summary

### Theorem 2.22 (The Agent Category)

**Agent** is a category where:
- **Objects**: Agent contexts `(S, K, I)` with state space, capabilities, and invariants
- **Morphisms**: Agents as transformations between contexts
- **Composition**: Sequential application `(g . f)(a) = g(f(a))`
- **Identity**: No-op agent `id_A(a) = a`

The category laws (identity and associativity) are necessary conditions for compositional agent systems.

### Theorem 2.23 (Polynomial Agent Characterization)

Agents with mode-dependent behavior are characterized by polynomial functors:

```
PolyAgent[S, A, B] ~ P(X) = Sum_{s in S} X^{A_s} * B_s
```

This captures:
- **S**: The state space (agent modes)
- **A_s**: Valid inputs in state s
- **B**: Output type
- **Transition**: How state and output evolve from state and input

### Corollary 2.24 (Embedding)

Simple agents embed:
```
Agent[A, B] = PolyAgent[Unit, A, B]
```

Polynomial agents generalize simple agents while maintaining categorical structure.

---

## 2.16 Looking Ahead

We have established that agents form a category with polynomial functor structure. But:

- **Effects**: Real agents have uncertainty, branching, traces—Chapter 3 (Monads)
- **Multi-input operations**: Agents can take multiple inputs—Chapter 4 (Operads)
- **Global coherence**: Multi-agent systems must agree—Chapter 5 (Sheaves)

The polynomial functor gives us the **static** structure. The next chapters add **dynamic** structure for effects and composition grammar.

---

*Previous: [Chapter 1: Mathematical Preliminaries](./01-preliminaries.md)*
*Next: [Chapter 3: The Monad of Extended Reasoning](./03-monadic-reasoning.md)*
