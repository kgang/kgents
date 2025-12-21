---
path: docs/skills/building-agent
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Skill: Building an Agent

> Create a well-formed agent that composes via functors and integrates with AGENTESE protocols.

**Difficulty**: Medium
**Prerequisites**: Understanding of Agent[A, B] protocol, composition laws, AGENTESE paths
**Files Touched**: `impl/claude/agents/<letter>/`, `impl/claude/protocols/agentese/`, tests
**References**: `docs/impl-guide.md`, `spec/principles.md`

---

## Overview

An agent in kgents is a **morphism A → B** in the category of agents. Building an agent well means:

1. **Defining clear input/output types** (A and B)
2. **Implementing the Agent protocol** (name, invoke)
3. **Composing linearly** via `>>` and functors
4. **Integrating with AGENTESE** paths where appropriate
5. **Writing specification-faithful tests**

This skill synthesizes patterns from recently developed agents (Flux, Semaphores, Creativity) and the design principles.

### When to Use Polynomial Agents Instead

If your agent needs **mode-dependent behavior**—different inputs/outputs based on internal state—use a **Polynomial Agent** instead of `Agent[A, B]`.

| Scenario | Use `Agent[A, B]` | Use `PolyAgent[S, A, B]` |
|----------|-------------------|--------------------------|
| Stateless transform | ✓ | ✓ (overkill) |
| State machine | ✗ | ✓ |
| Protocol phases | ✗ | ✓ |
| Mode-dependent I/O | ✗ | ✓ |

**See**: `docs/skills/polynomial-agent.md` for the polynomial agent skill guide.

---

## The Agent Protocol

Every agent implements the base protocol from `bootstrap/types.py`:

```python
from bootstrap.types import Agent
from typing import TypeVar

A = TypeVar("A")
B = TypeVar("B")

class MyAgent(Agent[A, B]):
    """One-line description of agent purpose."""

    @property
    def name(self) -> str:
        return "my-agent"

    async def invoke(self, input: A) -> B:
        # Transform input to output
        return result
```

### Category Laws (Required)

Your agent MUST satisfy these laws:

| Law | Requirement | How to Verify |
|-----|-------------|---------------|
| Identity | `Id >> f ≡ f ≡ f >> Id` | Test composition with Id agent |
| Associativity | `(f >> g) >> h ≡ f >> (g >> h)` | Test reordering doesn't change output |

**Implication**: Any agent that breaks these laws is NOT a valid agent.

---

## Step-by-Step: Creating an Agent

### Step 1: Define Domain Types

Start with clear input/output types. Use dataclasses for structured data.

**File**: `impl/claude/agents/<letter>/types.py` (or inline if simple)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Generic, TypeVar

@dataclass(frozen=True)
class MyInput:
    """Input to MyAgent. Frozen = immutable."""
    content: str
    context: dict[str, str] = field(default_factory=dict)

@dataclass
class MyOutput:
    """Output from MyAgent."""
    result: str
    confidence: float
    metadata: dict[str, str] = field(default_factory=dict)
```

**Best Practice**: Use `frozen=True` for inputs (immutability), regular dataclasses for outputs that may be enriched downstream.

### Step 2: Implement the Agent

**File**: `impl/claude/agents/<letter>/agent.py`

```python
"""
MyAgent: Brief description of purpose.

Longer description of what this agent does and why.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from bootstrap.types import Agent

if TYPE_CHECKING:
    # Heavy imports only for type hints
    from some_module import HeavyType

from .types import MyInput, MyOutput


@dataclass
class MyAgent(Agent[MyInput, MyOutput]):
    """
    Description of the agent.

    Example:
        >>> agent = MyAgent(config=MyConfig())
        >>> result = await agent.invoke(MyInput(content="test"))
    """

    # Configuration (immutable after construction)
    config: MyConfig = field(default_factory=MyConfig)

    # Runtime state (private, mutable)
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Initialize runtime state."""
        self._validate_config()
        self._initialized = True

    @property
    def name(self) -> str:
        return "my-agent"

    async def invoke(self, input: MyInput) -> MyOutput:
        """
        Transform input to output.

        Args:
            input: The input to process

        Returns:
            Transformed output

        Raises:
            ValueError: If input is invalid
        """
        # 1. Validate
        self._validate_input(input)

        # 2. Transform
        result = await self._process(input)

        # 3. Return
        return MyOutput(
            result=result,
            confidence=1.0,
        )

    # ─────────────────────────────────────────────────────────────
    # Private Methods
    # ─────────────────────────────────────────────────────────────

    def _validate_config(self) -> None:
        """Validate configuration."""
        if self.config.threshold < 0:
            raise ValueError("threshold must be non-negative")

    def _validate_input(self, input: MyInput) -> None:
        """Validate input."""
        if not input.content:
            raise ValueError("content cannot be empty")

    async def _process(self, input: MyInput) -> str:
        """Core processing logic."""
        return f"processed: {input.content}"
```

### Step 3: Add Composition Support

Agents compose via `>>`. The base class provides this, but you may want:

**1. Pipe operator for FluxAgents** (`|`):

```python
def __or__(self, other: "FluxAgent[B, C]") -> "FluxPipeline[A, C]":
    """Pipe operator for Living Pipelines."""
    from .pipeline import FluxPipeline
    return FluxPipeline([self, other])
```

**2. Functor lifting** (transform agent behavior):

```python
from agents.flux.functor import Flux

# Lift to streaming domain
flux_agent = Flux.lift(my_agent)

# Lift with config
flux_agent = Flux.lift(my_agent, FluxConfig(entropy_budget=2.0))
```

**3. Integration methods** (attach external systems):

```python
def attach_metabolism(self, metabolism: "FluxMetabolism[A, B]") -> None:
    """Attach metabolic adapter for resource tracking."""
    self._metabolism = metabolism

def detach_metabolism(self) -> None:
    """Detach metabolic adapter."""
    self._metabolism = None
```

### Step 4: Integrate with AGENTESE (Optional)

If your agent provides semantic affordances, register AGENTESE paths.

**File**: `impl/claude/protocols/agentese/contexts/<context>.py`

```python
# In the appropriate context (self_, world, concept, void, time)

async def my_affordance_manifest(
    self,
    observer: Umwelt,
    logos: "Logos",
    **kwargs: Any,
) -> Any:
    """
    world.myentity.manifest — Perceive entity through observer's lens.

    Different observers see different projections:
    - architect: sees structure
    - poet: sees metaphor
    - economist: sees value
    """
    # Get the entity
    entity = await self._get_entity(kwargs.get("entity_id"))

    # Project through observer's lens
    projection = await logos.project(entity, observer)

    return projection
```

**AGENTESE Path Patterns**:

| Context | Purpose | Example Paths |
|---------|---------|---------------|
| `world.*` | External entities, tools | `world.document.manifest`, `world.purgatory.resolve` |
| `self.*` | Internal state, memory | `self.memory.engram`, `self.judgment.critique` |
| `concept.*` | Abstract platonics | `concept.blend.forge`, `concept.summary.refine` |
| `void.*` | Entropy, accursed share | `void.pataphysics.solve`, `void.entropy.sip` |
| `time.*` | Temporal traces | `time.trace.witness`, `time.semaphore.deadline` |

### Step 5: Write Tests

**File**: `impl/claude/agents/<letter>/_tests/test_agent.py`

```python
"""
Tests for MyAgent.

Test Categories (T-gent Types I-V):
- Type I: Contracts (preconditions, postconditions)
- Type II: Saboteurs (property-based, fuzzing)
- Type III: Spies (behavior verification)
- Type IV: Judges (semantic assertions)
- Type V: Witnesses (integration, round-trip)
"""

from __future__ import annotations

import pytest

from ..agent import MyAgent
from ..types import MyConfig, MyInput, MyOutput


# ─────────────────────────────────────────────────────────────
# Type I: Contract Tests
# ─────────────────────────────────────────────────────────────


class TestMyAgentContracts:
    """Test agent satisfies contracts."""

    @pytest.fixture
    def agent(self) -> MyAgent:
        """Create test agent."""
        return MyAgent(config=MyConfig())

    async def test_name_is_stable(self, agent: MyAgent) -> None:
        """Agent name should be stable."""
        assert agent.name == "my-agent"
        assert agent.name == agent.name  # Idempotent

    async def test_invoke_returns_output_type(self, agent: MyAgent) -> None:
        """Invoke should return correct type."""
        result = await agent.invoke(MyInput(content="test"))
        assert isinstance(result, MyOutput)

    async def test_empty_input_rejected(self, agent: MyAgent) -> None:
        """Empty input should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await agent.invoke(MyInput(content=""))


# ─────────────────────────────────────────────────────────────
# Type II: Saboteur Tests (Property-Based)
# ─────────────────────────────────────────────────────────────


class TestMyAgentProperties:
    """Property-based tests for invariants."""

    @pytest.mark.parametrize("content", ["a", "ab", "a" * 100, "unicode: \u2603"])
    async def test_any_nonempty_string_accepted(self, content: str) -> None:
        """Any non-empty string should be processable."""
        agent = MyAgent()
        result = await agent.invoke(MyInput(content=content))
        assert result.result  # Non-empty output


# ─────────────────────────────────────────────────────────────
# Type V: Witness Tests (Integration)
# ─────────────────────────────────────────────────────────────


class TestMyAgentComposition:
    """Test composition with other agents."""

    async def test_identity_law_left(self) -> None:
        """Id >> f ≡ f."""
        from bootstrap.id import Id

        agent = MyAgent()
        composed = Id() >> agent
        input_data = MyInput(content="test")

        direct = await agent.invoke(input_data)
        via_id = await composed.invoke(input_data)

        assert direct.result == via_id.result

    async def test_identity_law_right(self) -> None:
        """f >> Id ≡ f."""
        from bootstrap.id import Id

        agent = MyAgent()
        composed = agent >> Id()
        input_data = MyInput(content="test")

        direct = await agent.invoke(input_data)
        via_id = await composed.invoke(input_data)

        assert direct.result == via_id.result
```

---

## Functor Catalog

These functors linearly modify agent behavior while preserving composition:

| Functor | Signature | Purpose | File |
|---------|-----------|---------|------|
| **Flux** | `Agent[A,B] → Agent[Flux[A],Flux[B]]` | Discrete → Streaming | `agents/flux/functor.py` |
| **Observer** | `Agent[A,B] → Agent[A,B]` | Add observation hooks | `agents/o/observer.py` |
| **Metered** | `Agent[A,B] → Agent[A,B]` | Token budget tracking | `agents/b/metered_functor.py` |
| **K** | `Agent[A,B] → Agent[A,B]` | Personality navigation | `agents/k/functor.py` |
| **Symbiont** | `Agent[A,B] × D → Agent[A,B]` | Pure logic + D-gent state | `agents/d/symbiont.py` |

### Using Functors

```python
from agents.flux.functor import Flux
from agents.o.observer import ObserverFunctor
from agents.b.metered_functor import MeteredFunctor

# Chain functors (order matters!)
agent = MyAgent()
observed = ObserverFunctor(agent, callbacks=[on_before, on_after])
metered = MeteredFunctor(observed, budget=1000)
flux = Flux.lift(metered)

# Or compose the lifts
pipeline = (
    Flux.lift(MyAgent())
    | Flux.lift(AnotherAgent())
)
```

---

## Protocols for Integration

| Protocol | Purpose | Integration Point |
|----------|---------|-------------------|
| **Metabolism** | Resource tracking (entropy, temperature) | `attach_metabolism()` |
| **Mirror** | Observability (Terrarium TUI) | `attach_mirror()` |
| **Purgatory** | Human-in-the-loop (semaphores) | `attach_purgatory()` |
| **SemanticField** | Stigmergic communication (pheromones) | `field.emit()`, `field.sense()` |

### Example: Semaphore Integration (Rodizio Pattern)

```python
from agents.flux.semaphore import SemaphoreToken, SemaphoreReason

class MyAgent(Agent[MyInput, MyOutput]):
    async def invoke(self, input: MyInput) -> MyOutput | SemaphoreToken:
        """May yield control to human."""
        if self._needs_human_review(input):
            # Return red card (Rodizio pattern)
            return SemaphoreToken.create(
                reason=SemaphoreReason.APPROVAL_NEEDED,
                prompt="Review this content before proceeding",
                frozen_state=self._freeze_state(),
            )
        return await self._process(input)

    async def resume(
        self,
        frozen_state: bytes,
        human_input: str,
    ) -> MyOutput:
        """Resume after human provides input."""
        state = self._thaw_state(frozen_state)
        return await self._process_with_human_input(state, human_input)
```

---

## Anti-Patterns to Avoid

### 1. Breaking Composition Laws

```python
# BAD: Agent with hidden state that breaks associativity
class BadAgent(Agent[A, B]):
    counter = 0  # Shared mutable state!

    async def invoke(self, input: A) -> B:
        BadAgent.counter += 1  # Side effect changes composition behavior
        ...
```

### 2. Monolithic Agents

```python
# BAD: God agent that does everything
class GodAgent(Agent[Any, Any]):
    async def invoke(self, input: Any) -> Any:
        if input.type == "summarize": ...
        elif input.type == "translate": ...
        elif input.type == "analyze": ...
        # Kitchen sink!
```

**Better**: Compose smaller, focused agents.

### 3. LLM Agents Returning Arrays

```python
# BAD: LLM prompted to return array
class BadLLMAgent(Agent[Document, list[Improvement]]):
    async def invoke(self, doc: Document) -> list[Improvement]:
        # Prompt: "List all improvements"
        ...

# GOOD: LLM returns single output, call N times
class GoodLLMAgent(Agent[tuple[Document, Hypothesis], Improvement]):
    async def invoke(self, input: tuple[Document, Hypothesis]) -> Improvement:
        # Prompt: "Evaluate this specific hypothesis"
        ...
```

### 4. Blocking in Async Context

```python
# BAD: Blocking call in async method
async def invoke(self, input: A) -> B:
    result = requests.get(url)  # BLOCKS!
    ...

# GOOD: Use async HTTP
async def invoke(self, input: A) -> B:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            ...
```

### 5. Heavy Module-Level Imports

```python
# BAD: Imported at module load
from heavy_ml_library import model  # 500ms import time

# GOOD: Lazy import
async def invoke(self, input: A) -> B:
    from heavy_ml_library import model  # Only when needed
    ...
```

---

## LLM-Backed Agents

For agents that invoke LLMs, use the `LLMAgent` base class from `runtime/`:

### The LLMAgent Protocol

```python
from runtime import LLMAgent, AgentContext, AgentResult

class MySummarizer(LLMAgent[Document, Summary]):
    """
    Summarize documents using an LLM.

    LLMAgent extends Agent with:
    - build_prompt(input) → AgentContext: Convert input to LLM prompt
    - parse_response(str) → output: Parse LLM text to structured output
    """

    @property
    def name(self) -> str:
        return "summarizer"

    async def invoke(self, input: Document) -> Summary:
        """Not used directly - runtime.execute() handles this."""
        raise NotImplementedError("Use runtime.execute()")

    def build_prompt(self, input: Document) -> AgentContext:
        """Convert input to LLM context."""
        return AgentContext(
            system_prompt="You are a precise summarization assistant.",
            messages=[{
                "role": "user",
                "content": f"Summarize this document:\n\n{input.content}"
            }],
            temperature=0.3,  # Lower for factual tasks
            max_tokens=1024,
        )

    def parse_response(self, response: str) -> Summary:
        """Parse LLM response to output type."""
        from runtime import robust_json_parse
        data = robust_json_parse(response)
        return Summary(
            content=data["summary"],
            key_points=data.get("key_points", []),
        )
```

### AgentContext Fields

| Field | Type | Purpose |
|-------|------|---------|
| `system_prompt` | `str` | System message defining agent behavior |
| `messages` | `list[dict]` | Conversation history (role: user/assistant) |
| `temperature` | `float` | Creativity (0.0-1.0, default 0.7) |
| `max_tokens` | `int` | Output limit (default 4096) |
| `facts` | `dict | None` | Grounded facts for RAG patterns |
| `metadata` | `dict | None` | Arbitrary execution metadata |

### Runtimes

Execute LLMAgents via runtimes:

```python
from runtime import ClaudeCLIRuntime, ClaudeRuntime, OpenRouterRuntime

# Via Claude Code CLI (uses OAuth, no API key needed)
runtime = ClaudeCLIRuntime()

# Via Claude API (requires ANTHROPIC_API_KEY)
runtime = ClaudeRuntime(api_key=os.environ["ANTHROPIC_API_KEY"])

# Via OpenRouter (requires OPENROUTER_API_KEY)
runtime = OpenRouterRuntime(model="anthropic/claude-3.5-sonnet")

# Execute
result: AgentResult[Summary] = await runtime.execute(summarizer, document)
print(result.output)  # Summary dataclass
print(result.usage)   # {"input_tokens": ..., "output_tokens": ..., ...}
```

### Robust JSON Parsing

LLM responses often have formatting issues. Use `robust_json_parse`:

```python
from runtime import robust_json_parse, parse_structured_sections

def parse_response(self, response: str) -> MyOutput:
    """
    robust_json_parse handles:
    - Markdown code blocks (```json ... ```)
    - Truncated JSON (auto-closes brackets)
    - Trailing commas
    - Extra text before/after JSON
    """
    data = robust_json_parse(response, allow_partial=True)
    return MyOutput(**data)

# Or for section-based responses:
def parse_response(self, response: str) -> MyOutput:
    """
    Parse structured sections:
    RESPONSES:
    1. First response
    2. Second response

    FOLLOW-UPS:
    - Question one?
    """
    sections = parse_structured_sections(
        response,
        ["responses", "follow-ups"]
    )
    return MyOutput(
        responses=sections.get("responses", []),
        follow_ups=sections.get("follow-ups", []),
    )
```

### Retry and Error Handling

`ClaudeCLIRuntime` implements the Fix pattern for retry:

```python
runtime = ClaudeCLIRuntime(
    max_retries=3,           # Retry on parse failures
    enable_coercion=True,    # Use AI to coerce malformed responses
    coercion_confidence=0.9, # Minimum confidence for coerced response
)

# Error types for retry classification:
# - TransientError: Rate limits, timeouts → retry with backoff
# - PermanentError: Auth, invalid input → fast fail
# - ParseError: Malformed output → retry with feedback
```

### Async Composition

LLMAgents compose asynchronously:

```python
from runtime.base import parallel_execute

# Sequential composition
pipeline = extract_facts.then_async(summarize).then_async(format_output)
result = await pipeline.execute_async(document, runtime)

# Parallel execution (for I/O-bound LLM calls)
results = await parallel_execute(
    agents=[summarize_agent] * len(documents),
    inputs=documents,
    runtime=runtime,
)
```

### LLMAgent Best Practices

1. **Single output per invoke** (Minimal Output Principle):
   ```python
   # BAD: Ask LLM to return array
   "List all improvements for this code"

   # GOOD: Call N times with specific hypotheses
   "Evaluate whether this specific change would improve readability"
   ```

2. **Low temperature for factual tasks**:
   ```python
   AgentContext(temperature=0.1)  # For extraction, parsing
   AgentContext(temperature=0.7)  # For creative generation
   ```

3. **Structured output hints in system prompt**:
   ```python
   system_prompt = """You are a code analyzer.

   OUTPUT FORMAT (JSON):
   {
       "issue": "description of the issue",
       "severity": "low|medium|high",
       "suggestion": "how to fix it"
   }
   """
   ```

4. **Graceful parse failures**:
   ```python
   def parse_response(self, response: str) -> MyOutput:
       try:
           data = robust_json_parse(response)
       except ValueError:
           # Fallback: extract what we can
           return MyOutput(
               content=response[:500],
               confidence=0.0,  # Mark as low confidence
           )
   ```

---

## Verification Checklist

Before considering your agent complete:

### All Agents
- [ ] `Agent[A, B]` protocol implemented (name, invoke)
- [ ] Input/output types are clear dataclasses
- [ ] Category laws verified (identity, associativity)
- [ ] Tests cover contracts, properties, and composition
- [ ] No module-level heavy imports (Hollow Shell pattern)
- [ ] No blocking calls in async methods
- [ ] Follows Minimal Output Principle (single output per invoke)
- [ ] Integrates with relevant protocols (Metabolism, Mirror, etc.)
- [ ] AGENTESE paths registered if providing semantic affordances
- [ ] Mypy strict passes (`uv run mypy .`)
- [ ] Ruff passes (`uv run ruff check`)

### LLMAgent-Specific
- [ ] `build_prompt()` returns well-formed `AgentContext`
- [ ] `parse_response()` uses `robust_json_parse` for JSON outputs
- [ ] System prompt includes explicit output format
- [ ] Temperature set appropriately (low for factual, higher for creative)
- [ ] Error handling for malformed LLM responses
- [ ] Tests mock the runtime (don't call real LLMs in unit tests)

---

## D-gent Memory Patterns

Agents needing durable state use D-gent patterns. Choose based on access patterns:

### Pattern Selection Guide

| Pattern | Use Case | Files |
|---------|----------|-------|
| **Symbiont** | Pure logic + stateful memory | `agents/d/symbiont.py` |
| **Bicameral** | Relational + vector (semantic search) | `agents/d/bicameral.py` |
| **StoreComonad** | Event-sourced with time-travel | `agents/d/context_comonad.py` |
| **LinearityMap** | Resource tracking for context compression | `agents/d/linearity.py` |

### Symbiont Pattern (Simplest)

The Symbiont fuses stateless logic with stateful memory. Your logic is pure; D-gent handles persistence.

```python
from agents.d import Symbiont, VolatileAgent

# 1. Define pure logic: (Input, State) → (Output, NewState)
def chat_logic(msg: str, history: list) -> tuple[str, list]:
    history.append(("user", msg))
    response = f"Echo: {msg}"
    history.append(("bot", response))
    return response, history

# 2. Create D-gent for persistence (Volatile = in-memory)
memory = VolatileAgent(_state=[])

# 3. Fuse into Symbiont (valid Agent, composes via >>)
chatbot = Symbiont(logic=chat_logic, memory=memory)

# 4. Use like any agent
result = await chatbot.invoke("Hello")  # Returns "Echo: Hello"
```

**Key Insight**: Logic is testable without mocks (pure function). Memory is swappable (volatile → SQLite → Redis).

### Bicameral Memory (Semantic Search)

For agents needing both exact queries AND semantic similarity:

```python
from agents.d import BicameralMemory, BicameralConfig

# Create with Left (relational) + Right (vector) hemispheres
bicameral = BicameralMemory(
    left_hemisphere=relational_store,   # Source of truth (ACID)
    right_hemisphere=vector_store,      # Semantic index
    embedding_provider=embedder,
    config=BicameralConfig(
        auto_heal_ghosts=True,          # Auto-delete stale vectors
        coherency_check_on_recall=True, # Validate on every recall
    ),
)

# Store (writes to both hemispheres)
await bicameral.store("insight-001", {
    "type": "insight",
    "content": "Category theory unifies all D-gent patterns",
})

# Semantic recall (validates against relational)
results = await bicameral.recall("category theory patterns")
# → Ghost memories auto-healed, stale embeddings flagged

# Direct fetch (bypasses vector, for known IDs)
data = await bicameral.fetch("insight-001")

# Health check
report = await bicameral.coherency_check()
print(f"Coherency rate: {report.coherency_rate:.1%}")
```

**Ghost Memory Problem**: Vector entry points to deleted relational row → hallucination.
**Solution**: Coherency Protocol validates on recall, auto-heals ghosts.

### StoreComonad (Event Sourcing with Time Travel)

For agents needing full history and replay:

```python
from agents.d import StoreComonad, create_ledger_store
from pathlib import Path

# Create event-sourced store
store = create_ledger_store(
    persistence_path=Path("~/.kgents/ledger.jsonl").expanduser()
)

# Append events (immutable history)
store.append({
    "event_type": "CREDIT",
    "agent": "b-gent",
    "amount": 0.1,
})

# Extract current state (comonad extract)
balances = store.extract()  # {"b-gent": 0.6}

# Time-travel: state at any position
historical_balances = store.replay_to(position=5)

# Track value over time (comonad extend)
def agent_balance(s: StoreComonad) -> float:
    return s.extract().get("b-gent", 0.0)

history = store.extend(agent_balance)  # [0.5, 0.6, 0.55, ...]

# Get all snapshots (comonad duplicate)
snapshots = store.duplicate()  # Full zipper over history
```

**Comonad Laws**: `extract . duplicate = id`, `fmap extract . duplicate = id`.

### LinearityMap (Resource Tracking)

For context compression—track which resources can be dropped:

```python
from agents.d import LinearityMap, ResourceClass

lm = LinearityMap()

# Tag resources by class
obs_id = lm.tag(
    "user clicked button",
    ResourceClass.DROPPABLE,  # Can be discarded
    provenance="ui_event",
)

dec_id = lm.tag(
    "chose option A",
    ResourceClass.REQUIRED,   # Must flow to output
    provenance="decision",
)

focus_id = lm.tag(
    "critical user instruction",
    ResourceClass.PRESERVED,  # Must survive verbatim
    provenance="user_input",
)

# Query what can be dropped
droppable_ids = lm.droppable()

# Promote (one-way, enforces monotonicity)
lm.promote(obs_id, ResourceClass.REQUIRED, "became decision-relevant")

# Bulk drop droppables (for context compression)
dropped_count = lm.drop_all_droppable()

# Partition for summarization
partition = lm.partition()
# {DROPPABLE: [...], REQUIRED: [...], PRESERVED: [...]}
```

**Resource Classes** (partial order: DROPPABLE < REQUIRED < PRESERVED):
- **DROPPABLE**: Observations, intermediate computations
- **REQUIRED**: Reasoning traces, decisions
- **PRESERVED**: User inputs, code blocks (verbatim)

---

## Related Skills

- [agentese-path](agentese-path.md) - Registering AGENTESE paths
- [polynomial-agent](polynomial-agent.md) - State machine patterns
- [test-patterns](test-patterns.md) - T-gent Types I-V testing
- [data-bus-integration](data-bus-integration.md) - Event-driven patterns

---

## Changelog

- 2025-12-12: Added D-gent memory patterns (Symbiont, Bicameral, StoreComonad, LinearityMap)
- 2025-12-12: Added LLMAgent section with runtime patterns, JSON parsing, and best practices
- 2025-12-12: Initial version synthesizing patterns from Flux, Semaphores, Creativity
