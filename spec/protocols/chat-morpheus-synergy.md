# Chat-Morpheus Synergy: LLM Integration for Conversational Affordances

**Status:** Specification v1.0
**Date:** 2025-12-17
**Dependencies:** `spec/protocols/chat.md`, `spec/infrastructure/morpheus.md`, `spec/protocols/agentese.md`

---

## Epigraph

> *"The session is a coalgebra; the gateway is its interpreter."*
>
> *"Chat doesn't call Morpheus. Chat composes with Morpheus."*
>
> *"Same path, different observer, different model."*

---

## Part I: The Problem

### 1.1 Current State

The Chat Protocol (`spec/protocols/chat.md`) is fully specified with 207 tests. However:

```python
# In protocols/agentese/chat/factory.py:384
agent = EchoAgent()  # "In production, this would be the LLM agent"
```

Result: `kg soul chat` echoes input instead of invoking Claude.

### 1.2 The Wrong Approach

Creating a `MorpheusLLMAgent` adapter that:
- Lives in `protocols/agentese/chat/`
- Parses string format back to messages
- Directly calls `MorpheusPersistence.complete()`

**Why this is wrong:**
1. **Violates AD-009**: Adapters belong in service modules, not protocols
2. **Couples layers**: Protocol layer directly touches service persistence
3. **Misses composition**: Chat and Morpheus should compose, not interleave
4. **Loses observer context**: Direct calls don't preserve observer semantics

### 1.3 The Right Approach

Functor composition at the service level:

```
ChatCoalgebra ∘ MorpheusGateway : (State × Message) → (State × Response)
```

---

## Part II: Categorical Foundation

### 2.1 The Two Coalgebras

**ChatSession** is a coalgebra over session state:
```
ChatCoalgebra = (S_chat, step_chat : S_chat → (Response × S_chat))
```

Where `S_chat = Context × Turns × Entropy`.

**MorpheusGateway** is a coalgebra over provider state:
```
MorpheusCoalgebra = (S_morpheus, complete : S_morpheus × Request → Response × S_morpheus)
```

Where `S_morpheus` tracks rate limits, request counts, and circuit breakers.

### 2.2 The Composition

Their composition is **horizontal** (parallel state), not **vertical** (sequential):

```
(ChatCoalgebra ⊗ MorpheusCoalgebra) : (S_chat × S_morpheus) × Message → (S_chat × S_morpheus) × Response
```

**Key insight**: Chat and Morpheus each maintain their own state. Composition preserves both.

### 2.3 The Transform Functor

A **Transform Functor** T connects the two:

```python
T : ChatMessage → MorpheusRequest
T⁻¹ : MorpheusResponse → ChatResponse
```

This is NOT an adapter. It's a natural transformation between categories.

---

## Part III: Observer-Dependent LLM Selection

### 3.1 The Core Insight

Different observers should get different LLM behavior:

| Observer Archetype | Model | Temperature | Max Tokens |
|--------------------|-------|-------------|------------|
| `developer` | claude-sonnet-4 | 0.7 | 4096 |
| `guest` | claude-haiku | 0.5 | 1024 |
| `system` | claude-opus-4 | 0.3 | 8192 |
| `citizen` (NPC) | claude-haiku | 0.8 | 2048 |

### 3.2 Model Selection as Functor

Model selection is a functor from Observer to MorpheusConfig:

```python
ModelSelector : Observer → MorpheusConfig
```

```python
def select_model(observer: Observer, node_path: str) -> MorpheusConfig:
    """
    Select LLM configuration based on observer.

    This is observer-dependent behavior—the core AGENTESE insight.
    """
    match (observer.archetype, node_path):
        case ("system", _):
            return MorpheusConfig(model="claude-opus-4-20250514", temperature=0.3)
        case ("developer", "self.soul"):
            return MorpheusConfig(model="claude-sonnet-4-20250514", temperature=0.7)
        case ("guest", _):
            return MorpheusConfig(model="claude-3-haiku-20240307", temperature=0.5)
        case (_, path) if "citizen" in path:
            return MorpheusConfig(model="claude-3-haiku-20240307", temperature=0.8)
        case _:
            return MorpheusConfig(model="claude-sonnet-4-20250514", temperature=0.7)
```

### 3.3 Budget Derivation

Token budgets derive from observer tier:

```python
def derive_budget(observer: Observer) -> TokenBudget:
    """Derive token budget from observer tier."""
    tier = observer.capabilities.get("tier", "free")
    return TIER_BUDGETS.get(tier, FREE_BUDGET)

TIER_BUDGETS = {
    "free": TokenBudget(daily_tokens=10_000, per_request=1024),
    "pro": TokenBudget(daily_tokens=100_000, per_request=4096),
    "enterprise": TokenBudget(daily_tokens=1_000_000, per_request=16384),
}
```

---

## Part IV: Architecture

### 4.1 The Service Composition Pattern

Following AD-009 (Metaphysical Fullstack):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENTESE PATH LAYER                               │
│   self.soul.chat.send[message="..."]                                        │
│   world.town.citizen.elara.chat.send[message="..."]                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CHAT SERVICE MODULE                                │
│   services/chat/                                                            │
│   ├── node.py          # @node("*.chat") - Chat AGENTESE node               │
│   ├── composer.py      # ChatMorpheusComposer - The composition functor     │
│   └── transformer.py   # Message ↔ Request transforms                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                      ┌─────────────┴─────────────┐
                      ▼                           ▼
┌────────────────────────────────┐  ┌────────────────────────────────────────┐
│      CHAT INFRASTRUCTURE       │  │        MORPHEUS SERVICE                │
│   protocols/agentese/chat/     │  │   services/morpheus/                   │
│   ├── session.py               │  │   ├── persistence.py                   │
│   ├── context_projector.py     │  │   ├── gateway.py                       │
│   └── config.py                │  │   └── adapters/                        │
└────────────────────────────────┘  └────────────────────────────────────────┘
```

### 4.2 The ChatMorpheusComposer

The composer lives in the **chat service module**, not in protocols or adapters:

```python
# services/chat/composer.py

@dataclass
class ChatMorpheusComposer:
    """
    Composes ChatSession with MorpheusPersistence.

    This is NOT an adapter. It's a composition functor that:
    1. Transforms ChatMessage → MorpheusRequest
    2. Preserves observer context through the chain
    3. Transforms MorpheusResponse → ChatResponse
    4. Updates session state with actual token counts
    """

    morpheus: MorpheusPersistence
    model_selector: Callable[[Observer, str], MorpheusConfig]

    async def compose_turn(
        self,
        session: ChatSession,
        message: str,
        observer: Observer,
    ) -> TurnResult:
        """
        Execute a complete turn through the composition.

        ChatSession.send() delegates here; we don't replace ChatSession.
        """
        # 1. Get working context from session
        context = session.context.render()

        # 2. Select model based on observer
        config = self.model_selector(observer, session.node_path)

        # 3. Transform to Morpheus request
        request = self._to_morpheus_request(context, message, config)

        # 4. Invoke through Morpheus (preserves its state)
        result = await self.morpheus.complete(request, observer.archetype)

        # 5. Transform back to chat response
        response = self._from_morpheus_response(result)

        # 6. Session updates its own state with actual tokens
        return TurnResult(
            content=response.content,
            tokens_in=result.response.usage.prompt_tokens,
            tokens_out=result.response.usage.completion_tokens,
            latency_ms=result.latency_ms,
            model=config.model,
        )

    async def compose_stream(
        self,
        session: ChatSession,
        message: str,
        observer: Observer,
    ) -> AsyncIterator[str]:
        """Streaming composition."""
        context = session.context.render()
        config = self.model_selector(observer, session.node_path)
        request = self._to_morpheus_request(context, message, config)
        request.stream = True

        async for chunk in self.morpheus.stream(request, observer.archetype):
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### 4.3 Why Not Direct Wiring?

The alternative (rejected) approach wires ChatFlow directly to Morpheus:

```python
# WRONG: This couples protocol to service
class MorpheusLLMAgent:
    async def invoke(self, input: str) -> str:
        messages = self._parse_context_string(input)  # Re-parsing!
        ...
```

**Problems:**
1. **Re-parsing**: ChatFlow already has structured messages; re-parsing is wasteful and fragile
2. **Lost context**: The input string loses observer information
3. **Wrong location**: Agent adapters should be in services, not protocols
4. **Missing composition**: This replaces; proper design composes

---

## Part V: Integration Points

### 5.1 ChatSessionFactory Integration

```python
# services/chat/factory.py

class ChatServiceFactory:
    """
    Factory that creates sessions with Morpheus composition.

    Extends ChatSessionFactory with LLM integration.
    """

    def __init__(
        self,
        morpheus: MorpheusPersistence | None = None,
        model_selector: Callable | None = None,
    ):
        self._base_factory = ChatSessionFactory()
        self._morpheus = morpheus
        self._model_selector = model_selector or default_model_selector
        self._composer: ChatMorpheusComposer | None = None

    async def create_session(
        self,
        node_path: str,
        observer: Observer,
        **kwargs,
    ) -> ChatSession:
        """Create session with Morpheus composition attached."""
        session = await self._base_factory.create_session(node_path, observer, **kwargs)

        # Inject composer if Morpheus available
        if self._morpheus:
            composer = self._get_or_create_composer()
            session.set_composer(composer)

        return session
```

### 5.2 ChatSession Modification

The ChatSession needs a hook for external composition:

```python
# protocols/agentese/chat/session.py

class ChatSession:
    """Enhanced with composition hook."""

    _composer: "ChatMorpheusComposer | None" = None

    def set_composer(self, composer: "ChatMorpheusComposer") -> None:
        """Inject external turn composer."""
        self._composer = composer

    async def send(self, message: str) -> TurnResult:
        """Send message, using composer if available."""
        if self._composer:
            return await self._composer.compose_turn(self, message, self._observer)
        else:
            # Fallback to internal (echo) behavior
            return await self._internal_send(message)
```

### 5.3 Bootstrap Integration

```python
# services/bootstrap.py

async def get_service(name: str) -> Any:
    match name:
        case "chat_factory":
            morpheus = await get_service("morpheus_persistence")
            return ChatServiceFactory(morpheus=morpheus)

        case "morpheus_persistence":
            gateway = MorpheusGateway()
            gateway.register_provider(
                name="claude-cli",
                adapter=ClaudeCLIAdapter(),
                prefix="claude-",
            )
            return MorpheusPersistence(gateway=gateway)
```

---

## Part VI: Graceful Degradation

### 6.1 Fallback Cascade

When Morpheus is unavailable:

```
Morpheus.complete() unavailable
    ↓
ChatSession falls back to EchoAgent
    ↓
User sees: "[Echo] Your message: ..."
    ↓
Warning displayed: "LLM unavailable, running in echo mode"
```

### 6.2 Implementation

```python
async def compose_turn(self, ...) -> TurnResult:
    try:
        return await self._morpheus_compose(session, message, observer)
    except MorpheusUnavailableError:
        warn("LLM unavailable, falling back to echo mode")
        return TurnResult(
            content=f"[Echo] {message}",
            tokens_in=0,
            tokens_out=0,
            fallback=True,
        )
```

### 6.3 Existing Test Compatibility

All 207 existing chat tests continue to work because:
1. Tests don't configure Morpheus → fall back to EchoAgent
2. Composition is optional → base behavior unchanged
3. New tests verify Morpheus integration specifically

---

## Part VII: AGENTESE Path Grammar

### 7.1 Chat Affordances with LLM Effects

```python
@aspect(
    category=AspectCategory.MUTATION,
    effects=[
        Effect.CALLS("world.morpheus"),  # Calls Morpheus
        Effect.WRITES("chat_session"),
        Effect.CHARGES("tokens"),
    ],
    help="Send a message and receive a response",
)
async def send(self, observer: Observer, message: str) -> TurnResult:
    """Send message through composed ChatSession + Morpheus."""
    ...
```

### 7.2 Effect Composition Verification

The AGENTESE effect system verifies composition is valid:

```python
# Chat declares: CALLS(world.morpheus)
# Morpheus declares: CALLS(llm), CHARGES(tokens)
# Composition: CALLS(world.morpheus) → CALLS(llm), CHARGES(tokens)

def verify_composition(chat_effects, morpheus_effects):
    """Verify effect composition is safe."""
    # Chat's CALLS(world.morpheus) is resolved to morpheus_effects
    resolved = resolve_transitive_effects(chat_effects, {"world.morpheus": morpheus_effects})
    assert Effect.CALLS("llm") in resolved
    assert Effect.CHARGES("tokens") in resolved
```

---

## Part VIII: Observability

### 8.1 Trace Correlation

Chat and Morpheus traces are correlated:

```
chat.session (parent span)
├── chat.turn
│   ├── chat.context_render
│   ├── chat_morpheus.compose (composition span)
│   │   ├── model_selection
│   │   ├── transform.to_morpheus
│   │   ├── morpheus.complete (child span)
│   │   │   ├── morpheus.route
│   │   │   └── morpheus.adapter.complete
│   │   └── transform.from_morpheus
│   └── chat.context_update
```

### 8.2 Metrics

```python
# New metrics for composition
chat_morpheus_composition_total{node_path, observer_archetype, model, status}
chat_morpheus_composition_latency_seconds{node_path, quantile}
chat_morpheus_fallback_total{node_path, reason}
```

---

## Part IX: File Structure

```
services/chat/                          # NEW: Chat service module
├── __init__.py
├── composer.py                         # ChatMorpheusComposer
├── factory.py                          # ChatServiceFactory
├── transformer.py                      # Message ↔ Request transforms
├── model_selector.py                   # Observer → MorpheusConfig
└── _tests/
    ├── test_composer.py
    └── test_model_selector.py

protocols/agentese/chat/                # MODIFIED
├── session.py                          # Add set_composer() hook
└── ...                                 # Everything else unchanged

services/morpheus/                      # UNCHANGED
└── ...
```

---

## Part X: Success Criteria

### 10.1 Functional

- [ ] `kg soul chat` invokes Claude through Morpheus
- [ ] `kg town chat elara` routes through Morpheus with citizen personality
- [ ] Streaming shows real tokens (not simulated word chunks)
- [ ] Budget displays actual token counts from gateway
- [ ] All 207 existing chat tests pass unchanged
- [ ] Observer archetype affects model selection

### 10.2 Non-Functional

| Metric | Target |
|--------|--------|
| First response latency | < 2s |
| Streaming first token | < 500ms |
| Fallback detection | < 100ms |
| State consistency after error | Always preserved |

### 10.3 Architectural

- [ ] No new files in `protocols/agentese/chat/` (only modifications)
- [ ] Composer lives in `services/chat/`
- [ ] Effects are correctly declared and verified
- [ ] Trace correlation visible in observability

---

## Part XI: Anti-Patterns

### What This Spec Is NOT

1. **NOT an adapter pattern**: We don't create `MorpheusLLMAgent` that pretends to be a simple agent
2. **NOT string re-parsing**: We don't parse `[SYSTEM]\n...\n[USER]\n...` back to messages
3. **NOT direct coupling**: Chat doesn't import Morpheus internals
4. **NOT a replacement**: Composition extends, doesn't replace existing behavior

### What To Avoid

```python
# WRONG: Adapter in protocol layer
class MorpheusLLMAgent:
    async def invoke(self, input: str) -> str:
        messages = parse_string(input)  # Re-parsing!
        return await morpheus.complete(...)

# WRONG: Direct service import in protocol
from services.morpheus import MorpheusPersistence  # In protocols/!

# WRONG: Losing observer context
async def send(self, message: str) -> str:
    return await morpheus.complete(message)  # Where's observer?
```

---

## Appendix A: Transform Functions

```python
def to_morpheus_request(
    context: list[ChatMessage],
    message: str,
    config: MorpheusConfig,
) -> ChatRequest:
    """Transform chat context to Morpheus request."""
    messages = [
        {"role": m.role, "content": m.content}
        for m in context
    ]
    messages.append({"role": "user", "content": message})

    return ChatRequest(
        model=config.model,
        messages=messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

def from_morpheus_response(result: CompletionResult) -> str:
    """Extract content from Morpheus result."""
    return result.response.choices[0].message.content
```

---

## Appendix B: Decision Log

| Decision | Alternatives | Rationale |
|----------|--------------|-----------|
| Composition over adapter | MorpheusLLMAgent | Preserves categorical structure |
| Service layer | Protocol layer | AD-009 compliance |
| Hook injection | Subclass | Less invasive, testable |
| Model selection functor | Hardcoded | Observer-dependent behavior |
| Structured messages | String parsing | Avoids re-parsing, type-safe |

---

*"The best integration is the one that feels like it was always there."*

*Last updated: 2025-12-17*
