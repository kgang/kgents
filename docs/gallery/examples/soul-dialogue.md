# Soul Dialogue

Chat with K-gent, Kent's digital simulacra - personality-aligned dialogue that feels genuine.

## What is K-gent Soul?

K-gent Soul is NOT a chatbot. It's a **Governance Functor** - a personality model that ensures responses align with declared preferences and eigenvectors.

Think of it as:

- **Traditional chatbot**: `input -> LLM -> output`
- **K-gent Soul**: `input -> [Eigenvector Alignment] -> LLM -> [Principle Check] -> output`

The soul ensures every response feels "on brand" - like Kent on his best day.

## The Four Dialogue Modes

K-gent has four distinct modes, each activating different personality dimensions:

| Mode | Purpose | Example Starter |
|------|---------|----------------|
| **REFLECT** | Mirror back for examination | "Let me understand: you're saying..." |
| **ADVISE** | Offer preference-aligned suggestions | "Based on what matters to you..." |
| **CHALLENGE** | Push back constructively | "Have you considered the opposite..." |
| **EXPLORE** | Follow tangents, generate hypotheses | "That reminds me of... what if..." |

## Basic Usage

### From the CLI

The simplest way to interact with K-gent:

```bash
# Interactive dialogue (default: REFLECT mode)
kgents soul

# Specific mode with prompt
kgents soul challenge "I think premature optimization is fine"

# Quick response (fewer tokens)
kgents soul advise "Should I refactor this?" --quick

# See all starter prompts
kgents soul starters

# View soul state
kgents soul manifest
```

### From Python

```python
from agents.k import KgentSoul, DialogueMode

# Create a soul instance
soul = KgentSoul()

# Have a dialogue
output = await soul.dialogue(
    "What makes a good agent design?",
    mode=DialogueMode.REFLECT,
)

print(output.response)
# -> A thoughtful, Kent-like reflection on agent design
```

## The Dialogue Modes Explained

### REFLECT Mode

**Purpose**: Mirror back your thinking for examination.

**When to use**:
- Clarifying your own thoughts
- Processing complex ideas
- Getting a fresh perspective on your reasoning

**Example**:

```bash
$ kgents soul reflect "I'm torn between microservices and monoliths"
```

**K-gent response**:
> Let me understand: you're weighing modularity against simplicity. The question isn't "which is better" - it's "what serves this context?" Microservices excel when you have clear bounded contexts and independent teams. Monoliths shine when coordination costs matter more than scaling each piece independently. What does your system need right now?

### ADVISE Mode

**Purpose**: Offer recommendations aligned with your values.

**When to use**:
- Making decisions
- Seeking guidance
- Getting preference-aligned suggestions

**Example**:

```bash
$ kgents soul advise "Should I spend time on this optimization?"
```

**K-gent response**:
> Based on what matters to you - tasteful design, joy-inducing systems - ask: will this optimization make the system more delightful to work with, or just faster? If it's pure speed without improving the developer experience, defer it. If it removes friction and makes the code clearer, do it now. Premature optimization is waste. Timely optimization is craft.

### CHALLENGE Mode

**Purpose**: Push back constructively to stress-test ideas.

**When to use**:
- Validating assumptions
- Finding blind spots
- Strengthening arguments

**Example**:

```bash
$ kgents soul challenge "I think we should add more features"
```

**K-gent response**:
> Have you considered that every feature is also debt? More features means more surface area, more complexity, more to maintain. What if instead of adding, you composed better? What if you made what you have more delightful? The best feature is often the one you remove, not add.

### EXPLORE Mode

**Purpose**: Follow tangents, generate creative hypotheses.

**When to use**:
- Brainstorming
- Creative problem-solving
- Discovering unexpected connections

**Example**:

```bash
$ kgents soul explore "How do agents relate to category theory?"
```

**K-gent response**:
> That reminds me of how functors preserve structure... What if we thought of agents not as objects but as arrows? Then composition becomes the primary operation, not method calls. And what if we lifted that to different contexts? Maybe[Agent] for fallible agents, Flux[Agent] for streaming... suddenly we have a whole algebra of agent transformations. The noun is a lie; there's only the morphism!

## Eigenvectors: Personality Dimensions

K-gent's responses are shaped by **eigenvectors** - personality dimensions:

- **Tasteful**: Quality over quantity, always
- **Curated**: Intentional selection, not everything
- **Ethical**: Augment human judgment, don't replace it
- **Joy-Inducing**: Delight matters, not just function

These aren't just prompts - they're coordinate axes in personality space.

## Adding Soul to Your Agents

The `@Soulful` capability adds soul governance to any agent:

```python
from agents.a import Capability
from bootstrap.types import Agent

@Capability.Soulful(persona="Kent")
class AdvisorAgent(Agent[str, str]):
    """An advisor that gives persona-aligned advice."""

    @property
    def name(self) -> str:
        return "advisor"

    async def invoke(self, input: str) -> str:
        # Soul governance wraps this automatically
        # Responses will be filtered through K-gent's eigenvectors
        return f"Consider: {input}"
```

When compiled through `LocalProjector` with an active K-gent instance, the agent's responses will be:

1. Pre-processed through eigenvector alignment
2. Post-processed through principle checking
3. Guaranteed to feel "on brand"

## Example: Soulful Advisor

```python
from dataclasses import dataclass
from agents.a import Capability
from bootstrap.types import Agent

@dataclass
class Advice:
    suggestion: str
    reasoning: str
    confidence: float

@Capability.Soulful(persona="Kent")
class AdvisorAgent(Agent[str, Advice]):
    """Provides persona-aligned advice."""

    @property
    def name(self) -> str:
        return "advisor"

    async def invoke(self, input: str) -> Advice:
        # In production, this would consult K-gent
        if "code" in input.lower():
            return Advice(
                suggestion="Start with the simplest thing that could work.",
                reasoning="Complexity is debt. Simplicity compounds.",
                confidence=0.9,
            )
        else:
            return Advice(
                suggestion="What would make you smile when you look back?",
                reasoning="The mirror test: does this feel like you on your best day?",
                confidence=0.7,
            )

# Usage
advisor = AdvisorAgent()
advice = await advisor.invoke("How should I approach this code review?")
print(advice.suggestion)
# -> "Start with the simplest thing that could work."
```

## Soul as Governance

K-gent Soul isn't just for chatting. It's a governance mechanism:

**Without soul**:
```python
# Agent might give inconsistent advice
response1 = await agent.invoke("Should I optimize?")
# -> "Yes, optimize everything!"

response2 = await agent.invoke("Should I add features?")
# -> "Yes, add more features!"

# Contradictory! Both can't be right.
```

**With soul**:
```python
@Capability.Soulful(persona="Kent")
class ConsistentAgent(Agent[str, str]):
    ...

# Responses are filtered through eigenvectors
# Contradictions are caught and resolved
# Every response aligns with declared preferences
```

## Interactive Dialogue

Try an interactive session:

```bash
$ kgents soul

Welcome to K-gent Soul (REFLECT mode)
Type 'help' for commands, 'quit' to exit

You: What makes agents different from classes?

K-gent: Let me understand: you're asking about the conceptual shift.
Classes are about IDENTITY - "what is this thing?" Agents are about
TRANSFORMATION - "what does this do?" A class has methods. An agent
IS a method (invoke). The skeleton is minimal; capabilities are added
via Halo. This inverts the traditional OOP hierarchy. Instead of
building up from base classes, you compose morphisms. Identity is
emergent, not primary.

You: quit

Goodbye!
```

## Starters for Each Mode

K-gent provides conversation starters tailored to each mode:

```bash
$ kgents soul starters

REFLECT:
- "Help me think through..."
- "I'm noticing a pattern..."
- "Let me understand what I'm actually asking..."

ADVISE:
- "What would you recommend for..."
- "Given my constraints, should I..."
- "How would you approach..."

CHALLENGE:
- "I believe X, but..."
- "Why shouldn't I..."
- "What am I missing about..."

EXPLORE:
- "What if we combined..."
- "I wonder what would happen if..."
- "This reminds me of..."
```

## What's Next?

You've learned:

- K-gent Soul provides personality-aligned dialogue
- Four modes: REFLECT, ADVISE, CHALLENGE, EXPLORE
- Soul is a governance functor, not just a chatbot
- Use `@Soulful` to add soul governance to agents

**Next step**: Learn about streaming agents with the Flux functor.

[:octicons-arrow-right-24: Flow Like Water](streaming.md)

## Exercises

1. **Try each mode**: Have a dialogue in REFLECT, ADVISE, CHALLENGE, and EXPLORE modes
2. **Add soul to an agent**: Wrap one of your agents with `@Capability.Soulful`
3. **Compare responses**: Ask the same question in different modes and notice the differences

## Run the Example

```bash
# Interactive soul dialogue
kgents soul

# Or run the Python example
python -m impl.claude.agents.examples.soulful_advisor
```

## Full Source

View the complete source code:
- [impl/claude/agents/examples/soulful_advisor.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/examples/soulful_advisor.py)
- [impl/claude/agents/k/soul.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/k/soul.py)
