# Streaming

Transform discrete agents into continuous processors with the Flux functor.

## The Insight

> "The noun is a lie. There is only the rate of change."

Traditional agents process **points** - discrete transformations:

```python
Agent[A, B]  # A point transformation: one input → one output
```

But what if you need to process **flows** - continuous streams?

```python
FluxAgent[A, B]  # A continuous transformation: stream A → stream B
```

The **Flux Functor** bridges these worlds.

## The Flux Functor

Flux transforms discrete agents into streaming processors:

```
Flux.lift: Agent[A, B] → FluxAgent[A, B]
```

A FluxAgent:

- Accepts a stream of inputs (`AsyncIterator[A]`)
- Produces a stream of outputs (`AsyncIterator[B]`)
- Maintains continuous processing (no blocking)

## Basic Example

```python
from agents.flux import Flux, FluxAgent
from bootstrap.types import Agent
from typing import AsyncIterator

class DoubleAgent(Agent[int, int]):
    """Doubles its input."""

    @property
    def name(self) -> str:
        return "doubler"

    async def invoke(self, input: int) -> int:
        return input * 2

# Create a discrete agent
doubler = DoubleAgent()

# Lift it to the flux domain
flux_doubler: FluxAgent[int, int] = Flux.lift(doubler)

# Create a stream source
async def number_source() -> AsyncIterator[int]:
    for i in range(1, 6):
        yield i

# Process the stream
async for result in flux_doubler.start(number_source()):
    print(result)  # 2, 4, 6, 8, 10
```

## How It Works

When you lift an agent with `Flux.lift()`:

1. **Start**: The flux agent accepts an async iterator
2. **Process**: For each item in the stream, invoke the underlying agent
3. **Yield**: Emit results as they're produced (no buffering)
4. **Continue**: Keep processing until the stream ends

```python
# Conceptual implementation
class FluxAgent:
    def __init__(self, agent: Agent[A, B]):
        self.agent = agent

    async def start(self, source: AsyncIterator[A]) -> AsyncIterator[B]:
        async for item in source:
            result = await self.agent.invoke(item)
            yield result
```

## Flux Configuration

FluxAgent accepts configuration for advanced behavior:

```python
from agents.flux import Flux, FluxConfig

config = FluxConfig(
    buffer_size=100,          # Internal buffer size
    feedback_fraction=0.0,    # Ouroboric feedback (advanced)
)

flux_agent = Flux.lift(doubler, config=config)
```

### Buffer Size

Controls how many items can be buffered internally:

```python
config = FluxConfig(buffer_size=10)
flux_agent = Flux.lift(doubler, config=config)

# If the source produces faster than the agent processes,
# items are buffered up to buffer_size
```

### Feedback Fraction (Advanced)

Enables **ouroboric feedback** - feeding output back as input:

```python
config = FluxConfig(feedback_fraction=0.1)
flux_agent = Flux.lift(doubler, config=config)

# 10% of output is fed back as input
# Creates a self-sustaining loop (use carefully!)
```

This is useful for:

- Evolutionary systems (output influences future input)
- Recursive refinement
- Self-organizing agents

## Stream Sources

You can create streams from many sources:

### Generator Function

```python
async def number_source(n: int) -> AsyncIterator[int]:
    for i in range(1, n + 1):
        yield i
        await asyncio.sleep(0.01)  # Simulate work
```

### File Streaming

```python
async def file_lines(path: str) -> AsyncIterator[str]:
    async with aiofiles.open(path) as f:
        async for line in f:
            yield line.strip()
```

### WebSocket Streaming

```python
async def websocket_messages(ws) -> AsyncIterator[str]:
    async for message in ws:
        yield message
```

### Event Streaming

```python
async def events(queue: asyncio.Queue) -> AsyncIterator[Event]:
    while True:
        event = await queue.get()
        if event is None:  # Sentinel value
            break
        yield event
```

## Composing Flux Agents

Flux agents compose just like regular agents:

```python
from agents.flux import Flux

# Create discrete agents
double = DoubleAgent()
filter_even = FilterEvenAgent()

# Lift to flux
flux_double = Flux.lift(double)
flux_filter = Flux.lift(filter_even)

# Compose them
# (Note: actual composition uses the >> operator on FluxPipeline)
# This shows the concept:

async def pipeline(source: AsyncIterator[int]) -> AsyncIterator[int]:
    # Double all numbers
    doubled = flux_double.start(source)
    # Filter to even numbers
    filtered = flux_filter.start(doubled)
    return filtered

# Use it
async for result in pipeline(number_source(5)):
    print(result)  # 2, 4, 6, 8, 10 (all even)
```

## Real-World Example: Log Processing

```python
from dataclasses import dataclass
from agents.flux import Flux
from bootstrap.types import Agent
from typing import AsyncIterator

@dataclass
class LogLine:
    timestamp: str
    level: str
    message: str

@dataclass
class ParsedLog:
    timestamp: str
    level: str
    message: str
    is_error: bool

class ParseLogAgent(Agent[str, ParsedLog]):
    """Parse a log line into structured data."""

    @property
    def name(self) -> str:
        return "parse-log"

    async def invoke(self, input: str) -> ParsedLog:
        # Simple parser (in reality, use regex or proper parser)
        parts = input.split(" ", 2)
        if len(parts) < 3:
            return ParsedLog("", "INFO", input, False)

        timestamp, level, message = parts
        return ParsedLog(
            timestamp=timestamp,
            level=level,
            message=message,
            is_error=(level == "ERROR"),
        )

class FilterErrorsAgent(Agent[ParsedLog, ParsedLog | None]):
    """Filter to only error logs."""

    @property
    def name(self) -> str:
        return "filter-errors"

    async def invoke(self, input: ParsedLog) -> ParsedLog | None:
        return input if input.is_error else None

class FormatLogAgent(Agent[ParsedLog, str]):
    """Format log for display."""

    @property
    def name(self) -> str:
        return "format-log"

    async def invoke(self, input: ParsedLog) -> str:
        return f"[{input.timestamp}] {input.level}: {input.message}"

# Create flux agents
flux_parse = Flux.lift(ParseLogAgent())
flux_filter = Flux.lift(FilterErrorsAgent())
flux_format = Flux.lift(FormatLogAgent())

# Stream log file
async def log_stream(path: str) -> AsyncIterator[str]:
    with open(path) as f:
        for line in f:
            yield line.strip()

# Process logs
async def process_logs(path: str):
    source = log_stream(path)
    parsed = flux_parse.start(source)
    errors = flux_filter.start(parsed)
    formatted = flux_format.start(errors)

    async for log in formatted:
        print(log)

# Run it
await process_logs("/var/log/app.log")
```

## Living Pipelines

Flux agents create **living pipelines** - continuously processing streams:

```python
# Traditional batch processing
logs = read_all_logs()
parsed = [parse(log) for log in logs]
errors = [log for log in parsed if is_error(log)]
formatted = [format(log) for log in errors]

# Memory intensive! Must load everything first.
```

vs

```python
# Flux streaming
source = log_stream()
parsed = flux_parse.start(source)
errors = flux_filter.start(parsed)
formatted = flux_format.start(errors)

async for log in formatted:
    process(log)

# Memory efficient! Process one item at a time.
# Pipeline is "alive" - always ready to process.
```

## The | Operator (FluxPipeline)

For complex pipelines, use `FluxPipeline`:

```python
from agents.flux import FluxPipeline

pipeline = (
    FluxPipeline.from_source(log_stream("/var/log/app.log"))
    | flux_parse
    | flux_filter
    | flux_format
)

async for result in pipeline:
    print(result)
```

This creates a declarative pipeline that's easy to read and modify.

## Flux vs. Traditional Async Iteration

**Traditional approach**:

```python
async def process_stream(source):
    async for item in source:
        doubled = await double(item)
        if doubled % 2 == 0:
            formatted = await format(doubled)
            print(formatted)
```

**Flux approach**:

```python
pipeline = flux_double >> flux_filter >> flux_format

async for result in pipeline.start(source):
    print(result)
```

Benefits:

- **Composable**: Build pipelines from reusable agents
- **Testable**: Test each agent independently
- **Declarative**: Pipeline structure is clear
- **Type-safe**: Types flow through the pipeline

## When to Use Flux

Use Flux when you have:

- **Continuous data**: Log streams, sensor data, user events
- **Large datasets**: Too big to fit in memory
- **Real-time processing**: Need results as data arrives
- **Long-running pipelines**: Always-on processors

**Don't** use Flux when:

- You need to process all data before returning (use batch agents)
- Order matters and you need backpressure (use explicit queues)
- The stream is finite and small (just use a list)

## What's Next?

You've learned:

- Flux transforms discrete agents into continuous processors
- `Flux.lift()` creates streaming agents
- FluxConfig controls buffer size and feedback
- Compose flux agents to build living pipelines

**Next step**: Build production-ready agents with the Kappa archetype.

[:octicons-arrow-right-24: Custom Archetype](custom-archetype.md)

## Exercises

1. **Create a streaming pipeline**: Build `flux_parse >> flux_transform >> flux_format`
2. **Process a file stream**: Use Flux to process a large file line-by-line
3. **Experiment with feedback**: Create a flux agent with `feedback_fraction > 0` and observe behavior

## Run the Example

```bash
python -m impl.claude.agents.examples.streaming_pipeline
```

## Full Source

View the complete source code:
- [impl/claude/agents/examples/streaming_pipeline.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/examples/streaming_pipeline.py)
- [impl/claude/agents/flux/functor.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/flux/functor.py)
