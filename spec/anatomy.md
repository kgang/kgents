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

### Stateful Agents
- Maintain information across invocations
- Must declare state schema explicitly
- Must handle state persistence/restoration
- Example: K-gent (accumulates preferences over time)

### Contextual Agents
- Aware of environment but don't persist state
- May behave differently based on context
- Example: An agent that considers time of day

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
