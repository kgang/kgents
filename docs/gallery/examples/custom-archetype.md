# Custom Archetype

Build production-ready agents with Kappa - the full-stack archetype.

## Archetypes: Pre-configured Agent Patterns

An **archetype** is a pre-configured agent with a specific set of capabilities. Think of it as a template for common use cases.

kgents provides several archetypes:

| Archetype | Capabilities | Use Case |
|-----------|-------------|----------|
| **Alpha (α)** | Stateless, Observable | Pure functions with tracing |
| **Beta (β)** | Stateful | Agents with memory |
| **Gamma (γ)** | Soulful | Personality-aligned responses |
| **Delta (δ)** | Stateful + Observable | Stateful with tracing |
| **Kappa (κ)** | Everything | Full-stack, production-ready |

## What is Kappa?

Kappa is the **batteries-included archetype**:

```
Kappa = Stateful + Soulful + Observable + Streamable
```

Use Kappa when you need:

- State management (conversation history, memory)
- Personality alignment (soul governance)
- Observability (traces, metrics, logs)
- Streaming support (process flows)

## Basic Kappa Agent

```python
from agents.a import Kappa
from dataclasses import dataclass

@dataclass
class Advice:
    suggestion: str
    reasoning: str
    confidence: float

class AdvisorAgent(Kappa[str, Advice]):
    """A full-stack advisor agent."""

    @property
    def name(self) -> str:
        return "kappa-advisor"

    async def invoke(self, input: str) -> Advice:
        # Access state (provided by Stateful capability)
        # State is automatically managed
        history = self.state.get("history", [])
        history.append(input)
        self.state["history"] = history

        # Generate advice
        # (Soul governance is automatically applied)
        return Advice(
            suggestion="Trust the process.",
            reasoning="Kappa agents have all capabilities. Use them wisely.",
            confidence=0.95,
        )
```

That's it. The Kappa archetype provides:

- `self.state` - Persistent state dictionary
- Soul governance - Responses filtered through K-gent
- Traces - Automatic observability
- Stream support - Can be lifted with Flux

## Capabilities in Detail

### 1. Stateful

Kappa agents have built-in state management:

```python
class StatefulCounter(Kappa[str, int]):
    @property
    def name(self) -> str:
        return "counter"

    async def invoke(self, input: str) -> int:
        # Get current count (default to 0)
        count = self.state.get("count", 0)

        # Increment
        count += 1

        # Store
        self.state["count"] = count

        return count

# Usage
counter = StatefulCounter()
await counter.invoke("increment")  # -> 1
await counter.invoke("increment")  # -> 2
await counter.invoke("increment")  # -> 3

# State persists across invocations
```

### 2. Soulful

Responses are filtered through soul governance:

```python
class PersonalityAgent(Kappa[str, str]):
    @property
    def name(self) -> str:
        return "personality"

    async def invoke(self, input: str) -> str:
        # Raw response
        response = f"You said: {input}"

        # Soul governance (automatic) ensures:
        # - Aligned with declared eigenvectors
        # - Consistent with persona
        # - Passes principle checks

        return response
```

### 3. Observable

Kappa agents are automatically instrumented:

```python
class TracedAgent(Kappa[str, str]):
    @property
    def name(self) -> str:
        return "traced"

    async def invoke(self, input: str) -> str:
        # Traces are automatically emitted:
        # - Input received
        # - Processing started
        # - Result produced
        # - Duration, status, metadata

        result = input.upper()
        return result

# View traces
# kgents trace show traced
```

### 4. Streamable

Kappa agents can be lifted to Flux:

```python
from agents.flux import Flux

kappa_agent = MyKappaAgent()

# Lift to streaming
flux_agent = Flux.lift(kappa_agent)

# Process streams
async for result in flux_agent.start(source):
    print(result)
```

## Building a Custom Archetype

What if Kappa is too much? Build your own archetype:

```python
from agents.a import Capability
from bootstrap.types import Agent

# Custom archetype: Stateful + Observable (no soul, no streaming)
class Sigma(Agent[A, B]):
    """Stateful + Observable archetype."""
    pass

# Decorate with capabilities
Sigma = Capability.Stateful(Sigma)
Sigma = Capability.Observable(Sigma)

# Use it
class MyAgent(Sigma[str, int]):
    @property
    def name(self) -> str:
        return "sigma-agent"

    async def invoke(self, input: str) -> int:
        # Has state and observability, but not soul
        return len(input)
```

## Capability Decorators

Capabilities are added via decorators:

```python
from agents.a import Capability

# Single capability
@Capability.Stateful
class Agent1(Agent[str, str]):
    ...

# Multiple capabilities
@Capability.Soulful(persona="Kent")
@Capability.Stateful
class Agent2(Agent[str, str]):
    ...

# All capabilities (equivalent to Kappa)
@Capability.Stateful
@Capability.Soulful(persona="Kent")
@Capability.Observable
class Agent3(Agent[str, str]):
    ...
```

## Inspecting Halos

Every agent has a **Halo** - the set of capabilities wrapping the skeleton:

```python
from agents.a import get_halo

class MyAgent(Kappa[str, str]):
    @property
    def name(self) -> str:
        return "my-agent"

    async def invoke(self, input: str) -> str:
        return input.upper()

# Get the halo
halo = get_halo(MyAgent)

# Inspect capabilities
for cap in halo:
    print(type(cap).__name__)
# -> StatefulCapability
# -> SoulfulCapability
# -> ObservableCapability
```

## Real-World Example: Conversational Agent

```python
from agents.a import Kappa
from dataclasses import dataclass
from typing import List

@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str

@dataclass
class Conversation:
    messages: List[Message]
    summary: str

class ConversationalAgent(Kappa[str, str]):
    """A conversational agent with memory and personality."""

    @property
    def name(self) -> str:
        return "conversational"

    async def invoke(self, user_input: str) -> str:
        # Get conversation history (Stateful)
        messages = self.state.get("messages", [])

        # Add user message
        messages.append(Message(role="user", content=user_input))

        # Generate response (with Soul governance)
        response = self._generate_response(messages)

        # Add assistant message
        messages.append(Message(role="assistant", content=response))

        # Update state
        self.state["messages"] = messages

        # Return response
        return response

    def _generate_response(self, messages: List[Message]) -> str:
        # In production, call an LLM here
        # For demo, simple echo
        last_user_message = messages[-1].content
        return f"You said: {last_user_message}. How interesting!"

# Usage
agent = ConversationalAgent()

response1 = await agent.invoke("Hello!")
# -> "You said: Hello!. How interesting!"

response2 = await agent.invoke("What's your name?")
# -> "You said: What's your name?. How interesting!"

# State persists - conversation history is maintained
history = agent.state.get("messages", [])
# -> [
#     Message(role="user", content="Hello!"),
#     Message(role="assistant", content="You said: Hello!..."),
#     Message(role="user", content="What's your name?"),
#     Message(role="assistant", content="You said: What's your name?..."),
# ]
```

## Production Checklist

When building production agents with Kappa:

- [ ] **State**: Define what needs to persist across invocations
- [ ] **Soul**: Ensure responses align with brand/persona
- [ ] **Traces**: Add custom spans for complex operations
- [ ] **Errors**: Handle errors gracefully (state rollback, error traces)
- [ ] **Tests**: Test each capability independently
- [ ] **Config**: Make agents configurable (don't hardcode)

## Halo Pattern: Separation of Concerns

The Halo pattern separates:

- **Skeleton**: Core transformation logic (Agent[A, B])
- **Capabilities**: Cross-cutting concerns (state, soul, traces)

```python
# BAD: Everything in one class
class MessyAgent(Agent[str, str]):
    def __init__(self):
        self.state = {}
        self.tracer = Tracer()
        self.soul = Soul()

    async def invoke(self, input: str) -> str:
        # State management
        # Soul governance
        # Trace emission
        # Business logic
        # All tangled together!
        ...

# GOOD: Capabilities separate from logic
class CleanAgent(Kappa[str, str]):
    async def invoke(self, input: str) -> str:
        # Just business logic
        # State, soul, traces handled by Halo
        return input.upper()
```

## Choosing an Archetype

| Need | Archetype | Why |
|------|-----------|-----|
| Pure function | Alpha (α) | Stateless, just tracing |
| Needs memory | Beta (β) | Stateful |
| Personality | Gamma (γ) | Soulful |
| Stateful + traced | Delta (δ) | State + observability |
| Production-ready | Kappa (κ) | Everything |
| Custom mix | Roll your own | Compose capabilities |

## What's Next?

You've learned:

- Kappa is the full-stack archetype (Stateful + Soulful + Observable + Streamable)
- Capabilities are added via decorators
- Halos separate skeleton from cross-cutting concerns
- Build custom archetypes by composing capabilities

**Next step**: Explore more examples in the gallery!

[:octicons-arrow-left-24: Back to Gallery](../index.md)

## Exercises

1. **Create a custom archetype**: Build an archetype with just Stateful + Observable
2. **Build a counter agent**: Use Kappa to build a stateful counter
3. **Add tracing**: View traces for your Kappa agent with `kgents trace show`

## Run the Example

```bash
python -m impl.claude.agents.examples.soulful_advisor
```

## Full Source

View the complete source code:
- [impl/claude/agents/examples/soulful_advisor.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/examples/soulful_advisor.py)
- [impl/claude/agents/a/archetype.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/a/archetype.py)
- [impl/claude/agents/a/capability.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/a/capability.py)
