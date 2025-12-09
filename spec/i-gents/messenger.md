# The Messenger Protocol: Streaming Functor

> Chat is not request/response. Chat is a *stream* of events flowing in both directions.

---

## The Theory

Modern LLM interfaces (Claude.ai, ChatGPT, Cursor, Google AI Studio) all stream responses asynchronously. Messages are sent and received as discrete events, not blocking calls.

The Messenger Protocol is a **Functor Lift**:

```
Streaming: Agent[A, B] → Agent[A, AsyncIterator[Chunk[B]]]
```

This transforms any agent into a streaming agent while preserving composition laws.

---

## Core Types

### Message

```python
@dataclass(frozen=True)
class Message:
    """A discrete message in a conversation."""
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    metadata: dict = field(default_factory=dict)

    # Optional structured content
    tool_calls: list[ToolCall] | None = None
    tool_results: list[ToolResult] | None = None
```

### MessageChunk

```python
@dataclass(frozen=True)
class MessageChunk:
    """A streaming chunk (partial message)."""
    message_id: str
    delta: str              # Incremental content
    accumulated: str        # Full content so far
    done: bool = False      # Is this the final chunk?

    # Streaming metadata
    token_index: int = 0
    latency_ms: float = 0.0
```

### Conversation

```python
@dataclass(frozen=True)
class Conversation:
    """A stream of messages with identity."""
    id: str
    messages: list[Message]
    created_at: datetime
    metadata: dict = field(default_factory=dict)

    def append(self, message: Message) -> "Conversation":
        """Immutable append."""
        return Conversation(
            id=self.id,
            messages=[*self.messages, message],
            created_at=self.created_at,
            metadata=self.metadata
        )

    @property
    def last_message(self) -> Message | None:
        return self.messages[-1] if self.messages else None
```

---

## The Streaming Functor

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

---

## The Messenger Agent

```python
class MessengerAgent(Agent[Message, AsyncIterator[MessageChunk]]):
    """
    Agent that streams responses asynchronously.

    Matches the interface of Claude.ai, ChatGPT, Cursor, etc.
    """

    async def invoke(self, message: Message) -> AsyncIterator[MessageChunk]:
        """Stream response chunks as they arrive."""
        message_id = str(uuid4())
        accumulated = ""

        async for chunk in self.llm.stream(message):
            accumulated += chunk.text
            yield MessageChunk(
                message_id=message_id,
                delta=chunk.text,
                accumulated=accumulated,
                done=chunk.is_final,
                token_index=chunk.index,
                latency_ms=chunk.latency
            )

    async def send(self, content: str) -> Message:
        """Send a user message (non-blocking)."""
        message = Message(
            id=str(uuid4()),
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

---

## Backend Integrations

The Messenger Protocol adapts to various LLM backends:

| Service | Protocol | Adapter |
|---------|----------|---------|
| Claude.ai | SSE | `ClaudeMessenger` |
| ChatGPT | SSE | `OpenAIMessenger` |
| Cursor | WebSocket | `CursorMessenger` |
| Google AI Studio | SSE | `GeminiMessenger` |
| Local (Ollama) | HTTP chunked | `OllamaMessenger` |

### Adapter Interface

```python
class MessengerAdapter(Protocol):
    """Adapter for specific LLM backends."""

    async def stream(
        self,
        messages: list[Message],
        **kwargs
    ) -> AsyncIterator[MessageChunk]:
        """Stream response from backend."""
        ...

    async def send(self, message: Message) -> None:
        """Send message to backend."""
        ...

    def supports_tool_use(self) -> bool:
        """Does this backend support tool calling?"""
        ...

# Example: Claude adapter
class ClaudeMessenger(MessengerAdapter):
    async def stream(self, messages, **kwargs):
        async with self.client.messages.stream(
            model=self.model,
            messages=[m.to_claude_format() for m in messages],
            **kwargs
        ) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    yield MessageChunk(
                        delta=event.delta.text,
                        ...
                    )
```

---

## I-gent Visualization

The Messenger Protocol enables rich chat visualization:

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

### Streaming Metrics

```python
@dataclass
class StreamingMetrics:
    """Real-time streaming metrics for visualization."""
    tokens_per_second: float
    latency_first_token_ms: float
    latency_total_ms: float
    tokens_generated: int
    chunks_received: int

    @classmethod
    def from_chunks(cls, chunks: list[MessageChunk]) -> "StreamingMetrics":
        if not chunks:
            return cls(0, 0, 0, 0, 0)

        first_latency = chunks[0].latency_ms
        total_latency = sum(c.latency_ms for c in chunks)
        token_count = len(chunks)

        return cls(
            tokens_per_second=token_count / (total_latency / 1000) if total_latency > 0 else 0,
            latency_first_token_ms=first_latency,
            latency_total_ms=total_latency,
            tokens_generated=token_count,
            chunks_received=len(chunks)
        )
```

---

## Composition with Streaming

Streaming agents compose, preserving the functor laws:

```python
# Non-streaming composition
pipeline = agent_a >> agent_b >> agent_c

# Streaming composition (lifted)
streaming_pipeline = (
    Streaming(agent_a) >>
    Streaming(agent_b) >>
    Streaming(agent_c)
)

# Usage: Each step streams its output to the next
async for chunk in streaming_pipeline.invoke(input):
    print(chunk.delta, end="", flush=True)
```

### Functor Laws

```python
# Identity: Streaming(Id) ≅ Id
async for chunk in Streaming(Id).invoke(x):
    assert chunk.accumulated == x

# Composition: Streaming(f >> g) ≅ Streaming(f) >> Streaming(g)
# (Up to chunking boundaries)
```

---

## Error Handling

Streaming errors are also streamed:

```python
@dataclass
class StreamingError:
    """Error during streaming."""
    error_type: str
    message: str
    partial_output: str  # What was generated before failure
    recoverable: bool

async def stream_with_recovery(
    agent: MessengerAgent,
    message: Message
) -> AsyncIterator[MessageChunk | StreamingError]:
    """Stream with error recovery."""
    try:
        async for chunk in agent.invoke(message):
            yield chunk
    except StreamInterruptedError as e:
        yield StreamingError(
            error_type="interrupted",
            message=str(e),
            partial_output=e.accumulated,
            recoverable=True
        )
    except RateLimitError as e:
        yield StreamingError(
            error_type="rate_limit",
            message=f"Retry after {e.retry_after}s",
            partial_output="",
            recoverable=True
        )
```

---

## Anti-Patterns

- **Blocking on full response before rendering**: Stream immediately
- **Treating chat as stateless request/response**: Maintain conversation context
- **Losing message history on reconnect**: Persist conversation state
- **Ignoring streaming metrics**: Monitor latency and throughput
- **Not handling partial failures**: Provide partial output on interruption

---

*Zen Principle: The conversation flows; we observe its passage.*

---

## See Also

- [i-gents/README.md](README.md) - I-gent visualization overview
- [w-gents/stigmergy.md](../w-gents/stigmergy.md) - WebSocket coordination
- [view-functor.md](view-functor.md) - Widget rendering for streams
