# Chat Flow: Streaming Conversation

> *"Conversation is continuous. The pause between words is not silence—it is anticipation."*

---

## Overview

Chat Flow is the F-gent modality for streaming conversational interaction.

**Key characteristics**:
- Sequential turn-based messaging (user -> assistant -> user -> ...)
- Context window management with configurable strategies
- Token-level streaming output
- Linear history (no branching)

---

## The Chat Polynomial

```python
CHAT_POLYNOMIAL = FlowPolynomial(
    positions=frozenset([
        FlowState.DORMANT,      # Waiting for first message
        FlowState.STREAMING,    # Generating response tokens
        FlowState.DRAINING,     # Conversation ending
        FlowState.COLLAPSED,    # Error or context overflow
    ]),
    directions=lambda state: {
        FlowState.DORMANT: frozenset(["start", "configure"]),
        FlowState.STREAMING: frozenset(["message", "perturb", "stop"]),
        FlowState.DRAINING: frozenset(["stop"]),
        FlowState.COLLAPSED: frozenset(["reset"]),
    }[state],
    transition=chat_transition,
)
```

---

## Context Window Management

The context window is finite. Chat Flow must manage it.

### Context Strategies

| Strategy | Behavior | Trade-off |
|----------|----------|-----------|
| `sliding` | Drop oldest messages when full | Fast, loses early context |
| `summarize` | Compress old messages via LLM | Preserves essence, costs tokens |
| `forget` | Clear context entirely | Fresh start, loses all history |

### Sliding Window

```python
class SlidingContext:
    """Drop oldest messages to maintain window."""

    def __init__(self, window_size: int):
        self.window_size = window_size
        self.messages: deque[Message] = deque()
        self.token_count = 0

    def add(self, message: Message) -> None:
        self.messages.append(message)
        self.token_count += message.tokens

        while self.token_count > self.window_size:
            dropped = self.messages.popleft()
            self.token_count -= dropped.tokens
```

### Summarizing Context

```python
class SummarizingContext:
    """Compress old context when threshold reached."""

    def __init__(
        self,
        window_size: int,
        threshold: float = 0.8,
        summarizer: Agent[list[Message], str],
    ):
        self.window_size = window_size
        self.threshold = threshold
        self.summarizer = summarizer
        self.summary: str | None = None
        self.recent_messages: list[Message] = []

    async def add(self, message: Message) -> None:
        self.recent_messages.append(message)
        current_tokens = self._count_tokens()

        if current_tokens > self.window_size * self.threshold:
            await self._compress()

    async def _compress(self) -> None:
        """Summarize old messages into compressed form."""
        # Keep most recent N messages
        keep_count = len(self.recent_messages) // 3
        to_summarize = self.recent_messages[:-keep_count]
        to_keep = self.recent_messages[-keep_count:]

        # Generate summary
        new_summary = await self.summarizer.invoke(to_summarize)

        # Combine with existing summary
        if self.summary:
            self.summary = f"{self.summary}\n\n{new_summary}"
        else:
            self.summary = new_summary

        self.recent_messages = to_keep
```

---

## Turn Protocol

A **turn** is one message/response cycle.

```python
@dataclass
class Turn:
    """A single conversation turn."""
    turn_number: int
    user_message: Message
    assistant_response: Message
    started_at: datetime
    completed_at: datetime
    tokens_in: int
    tokens_out: int
    context_size_before: int
    context_size_after: int
```

### Turn Lifecycle

```
1. User sends message
2. Message added to context
3. Context checked for overflow (compress if needed)
4. Assistant generates response (streaming)
5. Response added to context
6. Turn completed
```

---

## Streaming Output

Chat Flow supports token-level streaming:

```python
async def stream_response(
    self,
    user_message: Message,
) -> AsyncIterator[str]:
    """
    Stream response tokens as they're generated.

    Yields individual tokens for real-time display.
    """
    self._state = FlowState.STREAMING

    # Add user message to context
    await self.context.add(user_message)

    # Stream assistant response
    async for token in self.inner.stream(self.context.render()):
        yield token
        self._partial_response += token

    # Complete turn
    response = Message(
        role="assistant",
        content=self._partial_response,
        tokens=count_tokens(self._partial_response),
    )
    await self.context.add(response)
    self._partial_response = ""
```

---

## Configuration

```python
@dataclass
class ChatConfig:
    """Chat-specific configuration."""

    # Context management
    context_window: int = 128_000
    context_strategy: Literal["sliding", "summarize", "forget"] = "summarize"
    summarization_threshold: float = 0.8
    summarizer: Agent[list[Message], str] | None = None

    # Turn behavior
    turn_timeout: float = 60.0  # Max seconds per response
    max_turns: int | None = None  # Max conversation length

    # System prompt
    system_prompt: str | None = None
    system_prompt_position: Literal["prepend", "inject"] = "prepend"

    # Streaming
    stream_tokens: bool = True
    min_chunk_size: int = 1  # Tokens per yield

    # Memory (D-gent integration)
    persist_history: bool = False
    memory_key: str | None = None
```

---

## System Prompt Handling

The system prompt sets context for the entire conversation.

### Prepend Strategy

System prompt is always first in context:

```
[System: You are a helpful assistant...]
[User: Hello]
[Assistant: Hi there!]
[User: What's the weather?]
...
```

### Inject Strategy

System prompt is re-injected periodically to reinforce behavior:

```
[System: You are a helpful assistant...]
[User: Hello]
[Assistant: Hi there!]
...
[System: Remember: You are a helpful assistant...]  # Injected after N turns
[User: What's the weather?]
...
```

---

## Integration with D-gent

Chat history can be persisted via D-gent Symbiont:

```python
from agents.f import Flow, ChatConfig
from agents.d import Symbiont

# Create chat with persistent memory
config = ChatConfig(
    persist_history=True,
    memory_key="conversation_12345",
)

persistent_chat = Symbiont(
    logic=Flow.lift(assistant, config),
    memory=DGentMemory(backend="postgres"),
)

# History survives across sessions
```

---

## Interruption Handling

Users may interrupt mid-response:

```python
async def handle_interruption(self, new_message: Message) -> None:
    """
    Handle user sending message while assistant is responding.

    Options:
    1. Complete current response, then process new message
    2. Abort current response, process new message
    3. Merge: incorporate interruption into response
    """
    match self.config.interruption_strategy:
        case "complete":
            # Finish current, queue new
            self._pending_messages.append(new_message)
        case "abort":
            # Cancel current, start new
            self._cancel_current()
            await self._process_message(new_message)
        case "merge":
            # Inject new message as perturbation
            await self.perturb(new_message)
```

---

## Error Handling

### Context Overflow

```python
if self.context.token_count > self.config.context_window:
    match self.config.overflow_behavior:
        case "summarize":
            await self.context.compress()
        case "truncate":
            self.context.truncate_oldest()
        case "error":
            raise ContextOverflowError(f"Context exceeded {self.config.context_window}")
```

### Generation Timeout

```python
try:
    async with asyncio.timeout(self.config.turn_timeout):
        async for token in self.inner.stream(context):
            yield token
except TimeoutError:
    yield "[Response truncated due to timeout]"
    self._state = FlowState.DRAINING
```

---

## Usage Examples

### Basic Chat

```python
from agents.f import Flow, FlowConfig

config = FlowConfig(modality="chat")
chat = Flow.lift(claude_agent, config)

async def converse():
    async for response in chat.start(user_input_stream()):
        print(f"Assistant: {response}")
```

### Chat with Custom Context

```python
config = FlowConfig(
    modality="chat",
    context_window=32_000,
    context_strategy="summarize",
    summarization_threshold=0.7,
)
```

### Chat with Streaming Display

```python
async for token in chat.stream_response(user_message):
    print(token, end="", flush=True)
print()  # Newline after complete response
```

---

## Metrics

| Metric | Description |
|--------|-------------|
| `turns_completed` | Total conversation turns |
| `tokens_in` | Total user input tokens |
| `tokens_out` | Total assistant output tokens |
| `context_compressions` | Times context was summarized |
| `average_turn_latency` | Mean response time |
| `context_utilization` | Current tokens / window size |

---

## See Also

- `README.md` - F-gent overview
- `context.md` - Detailed context management
- `spec/d-gents/symbiont.md` - Persistent state pattern
- `docs/skills/flux-agent.md` - Usage skill
