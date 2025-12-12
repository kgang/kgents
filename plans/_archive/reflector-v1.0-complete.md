---
path: self/reflector
status: active
progress: 40
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [self/cli-refactor, self/interface]
session_notes: |
  Option A from _focus.md. Deep integration of CLI and I-gent
  through a shared Reflector abstraction.

  Phase 1-3 COMPLETE:
  - Reflector Protocol defined
  - RuntimeEvent types (10+ event types)
  - InvocationContext with FD3 support
  - TerminalReflector (stdout + FD3)
  - HeadlessReflector (test capture)
  - 36 tests passing, mypy clean

  Next: hollow.py integration, status.py pilot
---

# The Reflector Pattern: Unified Runtime Surface

> *"The Reflector is the observer between User and Command. It manages the cognitive space, not the execution."*

## Executive Summary

The CLI (`hollow.py`) and TUI (`FluxApp`) are not separate interfaces—they are **two projections of the same Collaborative Runtime Environment**. This plan extracts a shared `Reflector` component that both can consume.

## Part I: The Core Insight

### What CLI and I-gent Share

| CLI Concept | I-gent Concept | Unified Concept |
|-------------|----------------|-----------------|
| `print()` calls | `FluxScreen.render()` | **Surface** - where output goes |
| Status handler | Registry events | **Events** - what happened |
| `InvocationContext` | `AgentSnapshot` | **Manifest** - agent state |
| stdout/stderr | Widget updates | **Channels** - data flows |
| (not yet) | `StatusBar` | **Inbox** - pending proposals |

### The Key Abstraction

```python
class Reflector(Protocol):
    """
    The observer between Runtime and User.

    Does NOT execute logic—mediates the "Space Between."
    Multiple implementations render to different surfaces.
    """

    # Event handling
    async def on_command_start(self, ctx: InvocationContext) -> None: ...
    async def on_command_end(self, result: InvocationResult) -> None: ...
    async def on_agent_event(self, event: RuntimeEvent) -> None: ...

    # Output channels
    def emit_human(self, text: str) -> None: ...
    def emit_semantic(self, data: dict[str, Any]) -> None: ...

    # Prompt management
    def render_prompt(self) -> str: ...
    def get_prompt_state(self) -> PromptState: ...
```

---

## Part II: Architecture

### Component Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         RUNTIME                                     │
│   (Cortex daemon, handlers, registry, pheromones)                  │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            │ RuntimeEvents
                            ▼
                    ┌───────────────┐
                    │   Reflector   │ ← Protocol (abstract)
                    │   Protocol    │
                    └───────┬───────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Terminal   │  │    Flux     │  │   Headless  │
    │  Reflector  │  │  Reflector  │  │  Reflector  │
    │             │  │             │  │             │
    │  stdout +   │  │  Textual    │  │  Log file   │
    │  FD3 pipe   │  │  widgets    │  │  or JSONL   │
    └─────────────┘  └─────────────┘  └─────────────┘
           │                │                │
           ▼                ▼                ▼
        Terminal          TUI            CI/Batch
```

### File Structure

```
impl/claude/protocols/cli/
├── reflector/
│   ├── __init__.py          # Public exports
│   ├── protocol.py          # Reflector Protocol + types
│   ├── events.py            # RuntimeEvent types
│   ├── terminal.py          # TerminalReflector implementation
│   ├── headless.py          # HeadlessReflector (for tests/CI)
│   └── _tests/
│       ├── test_protocol.py
│       ├── test_terminal.py
│       └── test_events.py
│
impl/claude/agents/i/
├── reflector/
│   ├── __init__.py
│   └── flux_reflector.py    # FluxReflector adapter
```

---

## Part III: Type Definitions

### RuntimeEvent Hierarchy

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

class EventType(Enum):
    """Types of runtime events."""
    COMMAND_START = "command_start"
    COMMAND_END = "command_end"
    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    AGENT_HEALTH_UPDATE = "agent_health_update"
    PROPOSAL_ADDED = "proposal_added"
    PROPOSAL_RESOLVED = "proposal_resolved"
    PHEROMONE_EMITTED = "pheromone_emitted"
    ERROR = "error"

@dataclass(frozen=True)
class RuntimeEvent:
    """Base event from the runtime."""
    event_type: EventType
    timestamp: datetime
    source: str  # e.g., "cortex", "d-gent", "status-handler"
    data: dict[str, Any]

@dataclass(frozen=True)
class CommandStartEvent(RuntimeEvent):
    """Emitted when a command begins."""
    command: str
    args: list[str]
    invoker: str  # "human" | "agent" | "scheduled"

@dataclass(frozen=True)
class CommandEndEvent(RuntimeEvent):
    """Emitted when a command completes."""
    command: str
    exit_code: int
    duration_ms: int
    human_output: str
    semantic_output: dict[str, Any]

@dataclass(frozen=True)
class AgentHealthEvent(RuntimeEvent):
    """Emitted when agent health changes."""
    agent_id: str
    agent_name: str
    health: dict[str, float]  # {"x": 0.9, "y": 0.8, "z": 0.7}
    phase: str  # "active", "dormant", etc.
```

### InvocationContext (Extended)

```python
@dataclass
class InvocationContext:
    """Rich context for command invocation."""

    # Identity
    command: str
    args: list[str]
    invoker: Invoker  # HUMAN | AGENT | SCHEDULED
    trace_id: str

    # State
    started_at: datetime
    budget: BudgetStatus

    # Channels (FD3 Protocol)
    fd3: IO[str] | None = None  # Semantic side-channel

    # Reflector reference (set by hollow.py)
    reflector: Reflector | None = None

    def emit_human(self, text: str) -> None:
        """Write to human channel (FD1/stdout)."""
        if self.reflector:
            self.reflector.emit_human(text)
        else:
            print(text)

    def emit_semantic(self, data: dict[str, Any]) -> None:
        """Write to semantic channel (FD3) if available."""
        if self.fd3:
            import json
            self.fd3.write(json.dumps(data) + "\n")
            self.fd3.flush()
        if self.reflector:
            self.reflector.emit_semantic(data)

    def output(self, human: str, semantic: dict[str, Any]) -> None:
        """Emit to both channels atomically."""
        self.emit_human(human)
        self.emit_semantic(semantic)
```

### PromptState

```python
class PromptState(Enum):
    """Current state of the prompt."""
    QUIET = "quiet"           # Normal: kgents >
    PENDING = "pending"       # Has proposals: kgents [2] >
    CRITICAL = "critical"     # Alert: kgents [⚠ DRIFT] >
    TYPING = "typing"         # Agent typing: kgents [d-gent...] >

@dataclass
class PromptInfo:
    """Information for rendering the prompt."""
    state: PromptState
    proposal_count: int = 0
    critical_message: str | None = None
    typing_agent: str | None = None

    def render(self) -> str:
        """Render prompt string."""
        if self.state == PromptState.CRITICAL and self.critical_message:
            return f"kgents [⚠ {self.critical_message}] > "
        elif self.state == PromptState.PENDING:
            s = "s" if self.proposal_count > 1 else ""
            return f"kgents [{self.proposal_count} proposal{s}] > "
        elif self.state == PromptState.TYPING and self.typing_agent:
            return f"kgents [{self.typing_agent}...] > "
        else:
            return "kgents > "
```

---

## Part IV: Implementation Phases

### Phase 1: Protocol & Types (This Session)

**Goal:** Define the Reflector protocol and core event types.

**Deliverables:**
1. `protocols/cli/reflector/protocol.py` - Reflector Protocol
2. `protocols/cli/reflector/events.py` - RuntimeEvent types
3. `protocols/cli/reflector/__init__.py` - Public exports
4. Basic tests

**Exit Criteria:**
- Types are importable and mypy-clean
- Tests verify event creation and protocol compliance

### Phase 2: TerminalReflector (This Session)

**Goal:** Implement the CLI-specific reflector.

**Deliverables:**
1. `protocols/cli/reflector/terminal.py` - TerminalReflector
2. FD3 file handling (KGENTS_FD3 env var)
3. Integration with hollow.py

**Exit Criteria:**
```bash
# Human sees pretty text
$ kgents status
[CORTEX] OK HEALTHY | instance:a8f3b2

# Agent gets JSON via FD3
$ KGENTS_FD3=/tmp/out.json kgents status && cat /tmp/out.json
{"health": "healthy", ...}
```

### Phase 3: HeadlessReflector (This Session)

**Goal:** Implement a test-friendly reflector.

**Deliverables:**
1. `protocols/cli/reflector/headless.py` - HeadlessReflector
2. Captures all events in memory
3. Useful for testing and CI

**Exit Criteria:**
- Tests can inject HeadlessReflector
- Events are captured and inspectable

### Phase 4: FluxReflector (Future Session)

**Goal:** Connect I-gent to the Reflector system.

**Deliverables:**
1. `agents/i/reflector/flux_reflector.py` - FluxReflector
2. Bridges RuntimeEvents to Textual widgets
3. Updates FluxScreen when events arrive

**Exit Criteria:**
- Running `kgents status` triggers update in FluxApp
- Agent health updates appear in I-gent
- Same events visible in CLI and TUI

### Phase 5: Event Bus Integration (Future Session)

**Goal:** Connect to real runtime events.

**Deliverables:**
1. Event subscription in hollow.py
2. Registry integration (agent add/remove)
3. Pheromone integration

**Exit Criteria:**
- Reflector receives real events from registry
- Multiple reflectors can subscribe
- Events flow from daemon to all surfaces

---

## Part V: Migration Strategy

### Non-Breaking Changes

All changes are additive:
1. Handlers continue to use `print()` - still works
2. `InvocationContext.output()` is optional - handlers opt-in
3. FD3 is only opened if `KGENTS_FD3` env var is set
4. Reflector is None if not configured

### Gradual Handler Migration

```python
# Before (still works):
def cmd_status(args: list[str]) -> int:
    print("[CORTEX] OK HEALTHY")
    return 0

# After (opt-in to dual output):
def cmd_status(args: list[str], ctx: InvocationContext = None) -> int:
    if ctx:
        ctx.output(
            human="[CORTEX] OK HEALTHY",
            semantic={"health": "healthy", ...}
        )
    else:
        print("[CORTEX] OK HEALTHY")
    return 0
```

### Testing Strategy

```python
def test_status_with_reflector():
    """Test that status handler uses reflector when available."""
    reflector = HeadlessReflector()
    ctx = InvocationContext(
        command="status",
        args=[],
        reflector=reflector,
    )

    result = cmd_status(ctx.args, ctx)

    assert result == 0
    assert len(reflector.events) == 2  # start + end
    assert reflector.semantic_output["health"] == "healthy"
```

---

## Part VI: Connection to Other Plans

| Plan | How Reflector Enables It |
|------|-------------------------|
| `self/cli-refactor` | Reflector IS the core abstraction from that plan |
| `self/interface` | FluxReflector connects I-gent to runtime events |
| `self/memory` | Merkle traces use RuntimeEvents as source |
| `void/entropy` | Pheromone events flow through Reflector |
| `agents/t-gent` | HeadlessReflector enables deterministic testing |

---

## Part VII: Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Handlers using ctx.output() | 0 | 1 (status) |
| FD3 support | no | yes |
| Reflector implementations | 0 | 3 (Terminal, Headless, Flux) |
| Shared events CLI↔TUI | 0 | all |
| Tests | 0 | >20 |

---

## Part VIII: Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Circular imports | Medium | High | Careful module structure |
| Performance overhead | Low | Medium | Lazy initialization |
| Event ordering | Medium | Medium | Timestamps + sequence numbers |
| Migration complexity | Low | Low | All changes additive |

---

## Part IX: Implementation Order (This Session)

1. Create `protocols/cli/reflector/` directory structure
2. Define `RuntimeEvent` types in `events.py`
3. Define `Reflector` Protocol in `protocol.py`
4. Implement `TerminalReflector` in `terminal.py`
5. Implement `HeadlessReflector` in `headless.py`
6. Add FD3 support to `InvocationContext`
7. Update `hollow.py` to create Reflector
8. Update `status.py` to use `ctx.output()`
9. Write tests
10. Run mypy and fix issues

---

*"The Reflector is not a window—it is the weather station that reports the weather to all surfaces."*
