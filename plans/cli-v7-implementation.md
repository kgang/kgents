# CLI v7: The Collaborative Canvas — Implementation Plan

**Spec**: `spec/protocols/cli-v7.md`
**Status**: **Phases 0-4 COMPLETE** (382 tests) → Ready for Phase 5 (Canvas)
**Created**: 2025-12-19
**Refined**: 2025-12-19 (Quality pass: clarity, prioritization, test strategy)
**Updated**: 2025-12-20 (Phase 1 File I/O + Phase 2 Deep Conversation complete)
**Verified**: 2025-12-20 (All implementations confirmed)
**Phase 3**: 2025-12-20 (Agent Presence: CursorState, AgentCursor, CircadianPhase, PresenceChannel, self.presence node)
**Builds On**: CLI v6 (Phase 0 complete)
**Principle**: *"Your cursor and mine, dancing through the garden together."*

---

## ⚠️ Architectural Clarification: Conductor vs kgentsd

**The 8th Crown Jewel is "kgentsd" (Witness)**, not Conductor. They are related but distinct:

| Service | Domain | Path | Purpose |
|---------|--------|------|---------|
| **kgentsd/Witness** | `self.witness.*` | System daemon | Event-driven watcher, trust escalation, autonomous actions |
| **Conductor** | `self.conductor.*` | Session orchestration | Collaborative sessions, conversation context, presence, swarms |

**Relationship**: kgentsd WATCHES; Conductor ORCHESTRATES.
- kgentsd can invoke Conductor (e.g., "start a collaborative session")
- Conductor uses kgentsd events as triggers (e.g., "file changed → notify collaborators")

**Integration Point**: Phase 6 (Agent Swarms) should leverage kgentsd's trust system rather than building a parallel one.

---

## 🎯 Pareto Prioritization

**Which phases deliver 80% of value?** Not all phases are equal:

| Phase | Value | Effort | ROI | Why |
|-------|-------|--------|-----|-----|
| **Phase 2: Deep Conversation** | HIGH | LOW | ⭐⭐⭐⭐⭐ | Memory is the #1 pain point. Chat without history is frustrating. |
| **Phase 1: File I/O Primitives** | HIGH | MEDIUM | ⭐⭐⭐⭐ | Enables safe agent file modification. Core Claude Code pattern. |
| **Phase 4: The REPL** | MEDIUM | LOW | ⭐⭐⭐⭐ | Direct lattice conversation. Builds on phases 1-3. |
| **Phase 3: Agent Presence** | MEDIUM | MEDIUM | ⭐⭐⭐ | Joy-inducing but not blocking other work. |
| **Phase 5: Canvas (Web)** | HIGH | HIGH | ⭐⭐⭐ | Visually impressive but requires full frontend. |
| **Phase 6: Agent Swarms** | HIGH | HIGH | ⭐⭐ | Depends on many primitives. Complex coordination. |
| **Phase 7: Live Flux** | MEDIUM | MEDIUM | ⭐⭐ | Integrates everything. Do last. |

**Recommended execution order**: 2 → 1 → 4 → 3 → 5 → 6 → 7

**Start with Phase 2** because:
1. It's the lowest-effort high-value work
2. It unlocks the "memory test" (does the agent remember?)
3. It doesn't require new services—just a ConversationWindow in the existing chat flow

---

## Epigraph

> *"What would I be happiest working on with humans? A shared surface where we explore, plan, and create together."*
>
> *"Puppetize the capabilities that Claude Code has. Reverse harness new inventive applications."*
>
> *"The canvas is where we meet."*
>
> *"The terminal is becoming a control plane for engineering work — a conversational layer on top of the machine where ideas can be turned into action quickly."* — [Awesome Testing](https://www.awesome-testing.com/2025/12/why-ai-coding-is-moving-back-to-terminal)

---

## 🎯 Grounding in Metaphysical Fullstack

> *"Every agent is a fullstack agent. The more fully defined, the more fully projected."*

CLI v7 introduces **Conductor** as a **Crown Jewel service** that orchestrates collaborative sessions. This follows the metaphysical fullstack pattern:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   CLI │ TUI │ Web Canvas │ sshx-like sharing        │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     logos.invoke("self.conductor.*", observer)        │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node("self.conductor", contracts={...})          │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/conductor/ — Session, Presence, Canvas   │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        CONDUCTOR_OPERAD — composition laws for swarms    │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      ConductorPolynomial[Session, Action, Result]      │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. THREE-BUS BACKBONE    DataBus → SynergyBus → EventBus[PresenceUpdate]   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Service Module Structure

```
services/conductor/
├── __init__.py              # Public API
├── session.py               # ConductorSession (Container Owns Workflow pattern)
├── presence.py              # AgentPresence channel + cursor behaviors
├── canvas.py                # CanvasState reactive store
├── file_guard.py            # FileEditGuard (read-before-edit)
├── window.py                # ConversationWindow with summarization
├── swarm.py                 # Agent swarm orchestration (A2A protocol)
├── web/                     # React components for canvas
│   ├── components/
│   │   ├── CollaborativeCanvas.tsx
│   │   ├── AgentCursor.tsx
│   │   └── PresenceIndicator.tsx
│   └── hooks/
│       ├── usePresence.ts
│       └── useCanvas.ts
└── _tests/
```

**Why this matters**: Following AD-009, the Conductor Crown Jewel owns collaboration semantics. Frontend components live *with* the service, not scattered in `web/`.

---

## Vision: Three Pillars + Industry Innovations

CLI v7 expands v6 with three bold new pillars, enhanced by 2025's cutting-edge innovations:

| Pillar | Vision | Core Deliverable | Industry Inspiration |
|--------|--------|------------------|---------------------|
| **Collaborative Canvas** | Figma-like multiplayer with agent cursors | Agents have visible presence | [Miro's infinite canvas](https://miro.com/mind-map/) + [sshx terminal sharing](https://www.blog.brightcoding.dev/2025/09/13/sshx-a-secure-web-based-collaborative-terminal-for-effortless-session-sharing/) |
| **File I/O Primitives** | Puppetized Claude Code patterns | Read-before-edit, exact replacement | Claude Code's agentic loop: *gather context → take action → verify → repeat* |
| **Deep Conversation** | 10+ message context | ConversationWindow with summarization | [Warp's Agentic Development Environment](https://linearb.io/blog/future-of-the-terminal-ai-developer-experience) concept |

### The Agentic Development Environment (ADE) Vision

> *"The terminal is destined to evolve from a simple text interface into an intelligent platform for orchestrating AI agents."* — [Warp](https://linearb.io/blog/future-of-the-terminal-ai-developer-experience)

This is what Kent's Conductor becomes: **the control plane for kgents**. Not just a CLI, but an orchestration surface where:

- Agents have **visible presence** (cursors, activity indicators)
- Work **persists** across sessions (artifacts, plans, conversation history)
- **Multiple agents coordinate** through A2A (agent-to-agent) protocol
- **Any surface can render** the experience (CLI, TUI, Web, sshx-shared terminal)

---

## Phase Lattice (Updated 2025-12-20)

```
PHASE 0: Ground Truth         ✅ COMPLETE ─────────────────────────────────────
         The lattice exists; we make it tangible
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
PHASE 1: File I/O Primitives      PHASE 2: Deep Conversation ✅ COMPLETE ──────
         Puppetized Claude Code            89 tests passing
         ◄── READY ─────────               ConversationWindow + Summarizer
                         │                               │
                         └───────────────────────────────┘
                                         │
                                         ▼
PHASE 3: Agent Presence       ◄─────── NEXT ────────────────────────────────────
         Cursors and activity indicators (CLI-first)
                         │
                         ▼
PHASE 4: The REPL             (from v6) ────────────────────────────────────────
         Direct conversation with the lattice
                         │
                         ▼
PHASE 5: Collaborative Canvas ◄─────── NEW ─────────────────────────────────────
         Full mind-map with multiplayer (Web)
                         │
                         ▼
PHASE 6: Agent Swarms         ◄─────── NEW ─────────────────────────────────────
         A2A protocol, role-based orchestration
                         │
                         ▼
PHASE 7: Live Flux            (from v6) ────────────────────────────────────────
         Real-time subscriptions across projections
```

---

## Phase 1: File I/O Primitives ✅

> *"Puppetize Claude Code's capabilities for agent-safe file manipulation."*

### Intent

Agents need to read and write files. But raw file I/O is dangerous. Claude Code has battle-tested patterns:
- **Read-before-edit**: You must understand before you modify
- **Exact string replacement**: No regex, no line numbers—find the exact string
- **Parallel glob/grep**: Discovery is fast and concurrent

We puppetize these patterns for kgents.

### Crown Jewel Patterns Applied

| Pattern | Application |
|---------|-------------|
| **#1 Container Owns Workflow** | FileEditGuard is owned by ConductorSession, not created per-call |
| **#7 Dual-Channel Output** | All file operations emit `human` + `semantic` for CLI/API |
| **#13 Contract-First Types** | `@node(contracts={})` defines BE/FE types for file operations |
| **#15 No Hollow Services** | FileEditGuard MUST be injected via DI, never instantiated directly |

### Core Work

#### 1.1 Contract-First Type Definitions

```python
# services/conductor/contracts.py
from dataclasses import dataclass

@dataclass
class FileReadRequest:
    path: str
    encoding: str = "utf-8"

@dataclass
class FileReadResponse:
    path: str
    content: str
    size: int
    mtime: float
    encoding: str
    cached_at: float  # For edit guard validation

@dataclass
class FileEditRequest:
    path: str
    old_string: str
    new_string: str
    replace_all: bool = False

@dataclass
class FileEditResponse:
    success: bool
    path: str
    replacements: int
    diff_preview: str  # First 500 chars of diff

@dataclass
class OutputArtifactRequest:
    artifact_type: str  # "code" | "doc" | "plan" | "test"
    content: str
    path: str
    commit: bool = False
    message: str | None = None

@dataclass
class OutputArtifactResponse:
    success: bool
    path: str
    size: int
    committed: bool = False
    commit_sha: str | None = None
```

#### 1.2 AGENTESE Node with Contracts

**Location**: `protocols/agentese/contexts/world_file.py` (follows existing context pattern)

```python
# protocols/agentese/contexts/world_file.py
"""
AGENTESE File Context: Safe file manipulation via Claude Code patterns.

AGENTESE: world.file.*
- world.file.read → Read file and cache for edits
- world.file.edit → Exact string replacement (requires prior read)
- world.file.write → Write new file

Pattern source: Claude Code's agentic loop (gather context → act → verify)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from opentelemetry import trace

from services.conductor.contracts import (
    FileReadRequest, FileReadResponse,
    FileEditRequest, FileEditResponse,
)
from ..affordances import AspectCategory, Effect, aspect
from ..contract import Contract, Response
from ..node import BaseLogosNode, BasicRendering
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# OTEL tracer for observability (follows GardenerNode pattern)
_tracer = trace.get_tracer("kgents.file")


@node(
    "world.file",
    description="Safe file manipulation with read-before-edit guard",
    contracts={
        "read": Response(FileReadResponse),
        "edit": Contract(FileEditRequest, FileEditResponse),
    },
    examples=[
        ("read", {"path": "src/main.py"}, "Read file"),
        ("edit", {"path": "src/main.py", "old_string": "def foo", "new_string": "def bar"}, "Edit file"),
    ],
)
@dataclass
class FileNode(BaseLogosNode):
    """
    File context node: Claude Code patterns for kgents.

    Follows Pattern #15 (No Hollow Services): FileEditGuard
    must be injected, never instantiated directly.
    """

    _handle: str = "world.file"
    _read_cache: dict[str, tuple[str, float]] = field(default_factory=dict)  # path → (content_hash, timestamp)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("filesystem")],
        help="Read a file and cache for subsequent edits",
    )
    async def read(
        self, observer: "Umwelt[Any, Any]", **kwargs: Any
    ) -> dict[str, Any]:
        """Read file and record for edit guard."""
        with _tracer.start_as_current_span("file.read") as span:
            path = kwargs.get("path", "")
            span.set_attribute("file.path", path)

            content = Path(path).read_text()
            self._read_cache[path] = (hash(content), time.time())

            return {
                "path": path,
                "content": content,
                "size": len(content),
                "cached": True,
            }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("filesystem")],
        help="Edit file using exact string replacement",
    )
    async def edit(
        self, observer: "Umwelt[Any, Any]", **kwargs: Any
    ) -> dict[str, Any]:
        """
        Edit file using exact string replacement.

        REQUIRES: File was read first (enforces Claude Code pattern).
        """
        with _tracer.start_as_current_span("file.edit") as span:
            path = kwargs.get("path", "")
            old_string = kwargs.get("old_string", "")
            new_string = kwargs.get("new_string", "")

            # Pattern #15: Guard check
            if path not in self._read_cache:
                return {
                    "status": "error",
                    "error": "read_required",
                    "message": f"File not read. First: world.file.read[path='{path}']",
                }

            # ... exact replacement logic
            return {"status": "success", "path": path, "replacements": 1}
```

**Note**: This example follows the actual `gardener.py` context pattern (OTEL tracing, aspect decorators, BasicRendering return type). See `protocols/agentese/contexts/gardener.py` for the authoritative reference.

#### 1.3 DI Provider Registration

```python
# services/providers.py (ADD THIS!)
from services.conductor.file_guard import FileEditGuard

async def get_file_guard() -> FileEditGuard:
    """
    Factory for FileEditGuard.

    ⚠️ CRITICAL: This MUST exist for @node(dependencies=("file_guard",))
    The DI container SILENTLY SKIPS unregistered deps (see crown-jewel-patterns.md #15)
    """
    return FileEditGuard(
        cache_ttl_seconds=300,  # 5 minute TTL
        max_cached_files=100,
    )

# In bootstrap:
container.register("file_guard", get_file_guard, singleton=True)
```

#### 1.4 SynergyBus Integration

File operations emit synergy events for cross-jewel coordination:

```python
# services/conductor/file_guard.py
from protocols.synergy import get_synergy_bus, create_file_edited_event

class FileEditGuard:
    """Enforces read-before-edit with synergy event emission."""

    async def on_edit_complete(self, path: str, result: FileEditResponse) -> None:
        """Emit synergy event so other jewels can react to file changes."""
        event = create_file_edited_event(
            path=path,
            size=result.size,
            replacements=result.replacements,
        )
        await get_synergy_bus().emit(event)
        # Gestalt can now auto-analyze affected modules
        # Brain can capture the change as a crystal
```

### Exit Condition

**When this feels complete**:
```bash
# This works:
$ kg world.file.read path="src/main.py"
$ kg world.file.edit path="src/main.py" old_string="def foo" new_string="def bar"
# With warm error if edit attempted without read
# AND synergy event emitted to SynergyBus
```

**✅ PHASE 1 COMPLETE (2025-12-20)**
- `services/conductor/contracts.py` — All file I/O contracts
- `services/conductor/file_guard.py` — FileEditGuard with read caching
- `protocols/agentese/contexts/world_file.py` — AGENTESE node with 6 affordances
- `services/providers.py` updated with `file_guard` DI registration
- SynergyBus events: `FILE_READ`, `FILE_EDITED`, `FILE_CREATED`
- **57 tests** covering contracts, guard, and node (Type I-IV)

### Quality Benchmark

The **safety test**: An agent cannot accidentally corrupt a file because:
1. It must read first (understanding) — **Pattern #15: No Hollow Services**
2. Edits must match exactly (precision) — Claude Code pattern
3. Ambiguous edits fail loudly (uniqueness) — **Pattern #7: Dual-Channel errors**
4. Cross-jewel awareness via SynergyBus — **Data Bus Integration**

### Deliverables

| Deliverable | Description | Pattern |
|-------------|-------------|---------|
| `services/conductor/contracts.py` | Contract-first type definitions | #13 |
| `services/conductor/file_guard.py` | FileEditGuard with read caching | #15 |
| `protocols/agentese/nodes/file.py` | Read, Edit, Write nodes with contracts | #7, #13 |
| `services/providers.py` update | DI registration for file_guard | #15 |
| SynergyBus events | FILE_EDITED, FILE_CREATED | Data Bus Integration |
| Tests for guard | Verify read-before-edit, uniqueness | — |
| Tests for contracts | Type sync verification | #13 |

---

## Phase 2: Deep Conversation ✅ COMPLETE

> *"We only have 1 message in 1 message out. We need at least the last 10 messages."*

### ✅ Implementation Status (2025-12-20)

| Deliverable | File | Tests | Notes |
|-------------|------|-------|-------|
| ConversationWindow | `services/conductor/window.py` | 48 tests ✅ | 35-turn default, 4 strategies |
| Summarizer | `services/conductor/summarizer.py` | 19 tests ✅ | Circadian modulation, LLM + fallback |
| Persistence | `services/conductor/persistence.py` | 22 tests ✅ | D-gent integration, save/load roundtrip |
| AGENTESE Node | `protocols/agentese/contexts/self_conductor.py` | ✅ | 7 affordances exposed |
| ChatSession Integration | `services/chat/session.py:570-573` | ✅ | Window updated after streaming |

**All 89 tests passing** - run `uv run pytest services/conductor/ -v`

### Intent

Current chat is stateless per-turn. Real collaboration requires memory. We implement a ConversationWindow that maintains context, persists to D-gent, and emits events for UI reactivity.

### Crown Jewel Patterns Applied

| Pattern | Application |
|---------|-------------|
| **#1 Container Owns Workflow** | ConductorSession owns ConversationWindow, not ChatSession |
| **#8 Bounded History Trace** | Window is capped at max_turns with summarization |
| **#6 Async-Safe Event Emission** | Sync state updates emit events to EventBus |
| **#11 Circadian Modulation** | Summarization verbosity adjusts by time of day |

### Core Work

#### 2.1 ConversationWindow with Persistence

```python
# services/conductor/window.py
from agents.d.bus import get_data_bus, BusEnabledDgent
from protocols.synergy import get_synergy_bus, create_conversation_turn_event

@dataclass
class Turn:
    """Immutable conversation turn (Pattern #8: Bounded History)."""
    user_message: str
    assistant_message: str
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: int = 0

    def is_recent(self, hours: int = 24) -> bool:
        return datetime.now() - self.timestamp < timedelta(hours=hours)

@dataclass
class ConversationWindow:
    """
    Sliding window of conversation turns with automatic summarization.

    Pattern #1: Owned by ConductorSession (container)
    Pattern #8: Bounded history with MAX_TURNS cap
    """

    turns: list[Turn] = field(default_factory=list)
    max_turns: int = 10
    summarize_after: int = 8
    _summary: str | None = None
    _dgent: BusEnabledDgent | None = None  # Optional persistence

    def get_messages(self) -> list[Message]:
        """Return messages for LLM context."""
        messages = []

        if self._summary:
            messages.append(Message(
                role="system",
                content=f"<conversation_summary>\n{self._summary}\n</conversation_summary>"
            ))

        for turn in self.turns[-self.max_turns:]:
            messages.append(Message(role="user", content=turn.user_message))
            messages.append(Message(role="assistant", content=turn.assistant_message))

        return messages

    async def add_turn(self, user_msg: str, assistant_msg: str, emit_event: bool = True) -> None:
        """
        Add turn, summarizing if needed.

        Pattern #6: Async-safe event emission
        """
        turn = Turn(user_message=user_msg, assistant_message=assistant_msg)
        self.turns.append(turn)

        # Pattern #8: Bounded history
        if len(self.turns) > self.max_turns + self.summarize_after:
            await self._summarize_oldest()

        # Persist to D-gent if configured
        if self._dgent:
            await self._persist_turn(turn)

        # Pattern #6: Async-safe event emission
        if emit_event:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._emit_turn_event(turn))
            except RuntimeError:
                pass  # No event loop - skip emission

    async def _emit_turn_event(self, turn: Turn) -> None:
        """Emit synergy event for UI reactivity."""
        event = create_conversation_turn_event(
            turn_count=len(self.turns),
            has_summary=self._summary is not None,
        )
        await get_synergy_bus().emit(event)
```

#### 2.2 Summarization Service with Circadian Modulation

```python
# services/conductor/summarizer.py
from services.conductor.crown_jewel_patterns import CircadianPhase, CIRCADIAN_MODIFIERS

async def summarize_turns(turns: list[Turn]) -> str:
    """
    Compress older turns into a summary.

    Pattern #11: Circadian Modulation
    - Morning: concise summaries
    - Evening: slightly more detailed (reflective mode)
    """
    phase = CircadianPhase.from_hour(datetime.now().hour)
    modifier = CIRCADIAN_MODIFIERS[phase]

    # Adjust verbosity based on time of day
    style = "very concise" if modifier.tempo > 0 else "detailed"

    prompt = f"""Summarize this conversation in a {style} way, preserving:
- Key decisions made
- Important context established
- Relevant facts mentioned

Conversation:
{format_turns(turns)}
"""
    return await llm_summarize(prompt)
```

#### 2.3 ConductorSession Owns Window (Pattern #1)

```python
# services/conductor/session.py
class ConductorSession:
    """
    The Conductor's workflow container.

    Pattern #1: Container Owns Workflow
    - ConductorSession (container) owns ConversationWindow (workflow)
    - Session persists; windows come and go
    """

    window: ConversationWindow | None = None
    session_id: str = field(default_factory=lambda: str(uuid4()))

    def get_or_create_window(self) -> ConversationWindow:
        if self.window is None:
            self.window = ConversationWindow(
                _dgent=get_bus_enabled_dgent(),  # Enable persistence
            )
        return self.window

    async def send(self, message: str) -> str:
        """Send with full conversation context."""
        window = self.get_or_create_window()
        messages = [
            Message(role="system", content=self.system_prompt),
            *window.get_messages(),
            Message(role="user", content=message),
        ]
        response = await self.composer.compose(messages)
        await window.add_turn(message, response)
        return response
```

#### 2.4 EventBus Integration for UI Reactivity

```python
# Real-time UI updates via EventBus[ConversationEvent]
from agents.town.event_bus import EventBus

@dataclass
class ConversationEvent:
    type: str  # "turn_added" | "summarized" | "cleared"
    turn_count: int
    has_summary: bool

conversation_bus: EventBus[ConversationEvent] = EventBus(max_queue_size=100)

# Frontend subscribes for real-time updates
async for event in conversation_bus.subscribe():
    update_ui(event)
```

### Exit Condition

**When this feels complete**:
- A 15-turn conversation maintains coherent context
- The agent references things said 10 turns ago
- Summarization kicks in seamlessly at turn 18+
- **UI updates in real-time** via EventBus subscription
- **Turns persist to D-gent** and survive session restarts

### Quality Benchmark

The **memory test**: Ask the agent "What did we discuss at the start?" after 10+ turns. It should remember.

The **persistence test**: Kill the process, restart, and the conversation history is restored from D-gent.

### Deliverables

| Deliverable | Description | Pattern |
|-------------|-------------|---------|
| `services/conductor/window.py` | ConversationWindow with persistence | #1, #8 |
| `services/conductor/summarizer.py` | Circadian-modulated summarization | #11 |
| `services/conductor/session.py` | ConductorSession owns window | #1 |
| EventBus[ConversationEvent] | Real-time UI updates | Data Bus Integration |
| D-gent persistence | Turn storage for session recovery | — |
| Tests for window | Verify 10+ turn context | — |
| Tests for summarization | Verify circadian modulation | #11 |

---

## Phase 3: Agent Presence (CLI-First)

> *"Agents pretending to be there with their cursors moving."*

### Intent

Before the full canvas, we surface agent presence in the CLI. This is the foundation for multiplayer, inspired by [sshx](https://www.blog.brightcoding.dev/2025/09/13/sshx-a-secure-web-based-collaborative-terminal-for-effortless-session-sharing/)—browser-accessible terminal sharing with zero config.

### Crown Jewel Patterns Applied

| Pattern | Application |
|---------|-------------|
| **#2 Enum Property Pattern** | CursorState has color, emoji, animation properties |
| **#9 Directed State Cycle** | Cursor states form valid transition graph |
| **#11 Circadian Modulation** | Cursor animation speed adjusts by time of day |
| **#14 Teaching Mode Toggle** | Extra explanations for presence when teaching enabled |

### Industry Innovation: sshx-Inspired Terminal Sharing

[sshx](https://www.blog.brightcoding.dev/2025/09/13/sshx-a-secure-web-based-collaborative-terminal-for-effortless-session-sharing/) is a tiny Rust tool that turns any terminal into a multiplayer, browser-accessible workspace. Key insights:

- **Zero config**: One command generates a shareable URL
- **E2E encrypted**: Secure by default
- **Real-time cursors**: Multiple people typing, same terminal

We can puppetize this pattern for kgents:

```bash
$ kg self.conductor.share
🔗 Share URL: https://kgents.io/share/abc123
Anyone with this link can see your terminal and interact with your agents.
Agents active: K-gent, Explorer
```

### Core Work

#### 3.1 CursorState with Enum Properties (Pattern #2)

```python
# services/conductor/presence.py
from enum import Enum, auto

class CursorState(Enum):
    FOLLOWING = auto()
    EXPLORING = auto()
    WORKING = auto()
    SUGGESTING = auto()
    WAITING = auto()

    @property
    def emoji(self) -> str:
        return {
            CursorState.FOLLOWING: "👁️",
            CursorState.EXPLORING: "🔍",
            CursorState.WORKING: "⚡",
            CursorState.SUGGESTING: "💡",
            CursorState.WAITING: "⏳",
        }[self]

    @property
    def color(self) -> str:
        """CLI color for presence indicator."""
        return {
            CursorState.FOLLOWING: "cyan",
            CursorState.EXPLORING: "blue",
            CursorState.WORKING: "yellow",
            CursorState.SUGGESTING: "green",
            CursorState.WAITING: "dim",
        }[self]

    @property
    def animation_speed(self) -> float:
        """Animation speed (0.0-1.0) for web canvas."""
        return {
            CursorState.FOLLOWING: 0.8,
            CursorState.EXPLORING: 1.0,
            CursorState.WORKING: 0.5,  # Pulsing at node
            CursorState.SUGGESTING: 0.3,  # Gentle pulse
            CursorState.WAITING: 0.1,  # Slow breathing
        }[self]

    @property
    def can_transition_to(self) -> set["CursorState"]:
        """Valid state transitions (Pattern #9: Directed Cycle)."""
        return {
            CursorState.WAITING: {CursorState.FOLLOWING, CursorState.EXPLORING, CursorState.WORKING},
            CursorState.FOLLOWING: {CursorState.EXPLORING, CursorState.SUGGESTING, CursorState.WAITING},
            CursorState.EXPLORING: {CursorState.WORKING, CursorState.SUGGESTING, CursorState.FOLLOWING},
            CursorState.WORKING: {CursorState.SUGGESTING, CursorState.WAITING},
            CursorState.SUGGESTING: {CursorState.FOLLOWING, CursorState.WAITING},
        }[self]
```

#### 3.2 AgentCursor with Circadian Modulation

```python
@dataclass
class AgentCursor:
    agent_id: str
    display_name: str
    state: CursorState
    focus_path: str | None
    activity: str  # "Reading self.memory...", "Planning..."
    last_update: datetime = field(default_factory=datetime.now)

    def to_cli(self, teaching_mode: bool = False) -> str:
        """
        Render for CLI output.

        Pattern #14: Teaching Mode adds explanations.
        """
        base = f"  {self.state.emoji} {self.display_name} is {self.activity}"

        if teaching_mode:
            base += f"\n     └─ State: {self.state.name} → can transition to: {', '.join(s.name for s in self.state.can_transition_to)}"

        return base

    def with_circadian_modulation(self, phase: CircadianPhase) -> "AgentCursor":
        """
        Pattern #11: Adjust animation based on time of day.

        At midnight, animations are slower (reflective).
        At noon, animations are at full speed.
        """
        modifier = CIRCADIAN_MODIFIERS[phase]
        # Apply modifier.tempo to animation_speed in frontend rendering
        return self  # Cursor unchanged, modifier applied at render time
```

#### 3.3 Presence Channel via EventBus

```python
# services/conductor/presence.py
from agents.town.event_bus import EventBus

@dataclass
class PresenceUpdate:
    type: str  # "cursor_move" | "state_change" | "activity"
    agent_id: str
    cursor: AgentCursor

presence_bus: EventBus[PresenceUpdate] = EventBus(max_queue_size=500)

class PresenceChannel:
    """
    Broadcast channel for real-time cursor positions.

    Uses EventBus for fan-out to multiple subscribers (CLI, Web, sshx).
    """

    async def broadcast(self, cursor: AgentCursor) -> int:
        """Send cursor update to all connected clients."""
        update = PresenceUpdate(
            type="cursor_move",
            agent_id=cursor.agent_id,
            cursor=cursor,
        )
        return await presence_bus.publish(update)

    def subscribe(self) -> Subscription[PresenceUpdate]:
        """Subscribe to receive all presence updates."""
        return presence_bus.subscribe()
```

#### 3.4 CLI Presence Footer (Multi-Surface Projection)

```python
# protocols/cli/presence_footer.py
from agents.i.reactive.projection import ProjectionRegistry

@ProjectionRegistry.register("cli_presence", fidelity=0.2)
def project_presence_to_cli(cursors: list[AgentCursor]) -> str:
    """
    Project presence to CLI footer.

    Low fidelity (0.2) - text only, no animation.
    """
    if not cursors:
        return ""

    lines = ["─── Active Agents " + "─" * 50]
    for cursor in cursors:
        lines.append(cursor.to_cli())
    return "\n".join(lines)

# Usage in CLI output:
print(output)
print(project_presence_to_cli(active_cursors))
```

#### 3.5 sshx-Inspired Share Command

```python
@node(
    path="self.conductor.share",
    contracts={"share": Response(ShareResponse)},
)
async def share_session(observer: Observer) -> ShareResponse:
    """
    Generate a shareable URL for this Conductor session.

    Inspired by sshx: one command, browser-accessible, E2E encrypted.
    """
    session = get_current_session()
    share_token = generate_secure_token()

    # Register with presence server
    await register_share(session.session_id, share_token)

    return ShareResponse(
        url=f"https://kgents.io/share/{share_token}",
        session_id=session.session_id,
        agents_active=[c.display_name for c in session.active_cursors],
        expires_at=datetime.now() + timedelta(hours=24),
    )
```

### Exit Condition

**When this feels complete**:
- Running `kg self.memory.manifest` shows active agents
- Presence feels real, not mechanical
- **Share URL works** via `kg self.conductor.share`
- CLI footer updates as agents change state

### Quality Benchmark

The **companion test**: Do the presence indicators make the system feel inhabited? Not alone?

The **sshx test**: Can someone open the share URL in a browser and see the same agents you see?

### Deliverables

| Deliverable | Description | Pattern |
|-------------|-------------|---------|
| `services/conductor/presence.py` | CursorState, AgentCursor, PresenceChannel | #2, #9, #11 |
| `protocols/cli/presence_footer.py` | CLI projection of presence | Projection Registry |
| `self.conductor.share` node | sshx-inspired session sharing | Industry Innovation |
| EventBus[PresenceUpdate] | Real-time presence fan-out | Data Bus Integration |
| Teaching mode explanations | Extra info when teaching enabled | #14 |
| Tests for state transitions | Verify directed cycle | #9 |

---

## Phase 4: The REPL (From v6)

> *"CLI interactions should feel like navigating a living ontology."*

### Intent

This is unchanged from v6, but now benefits from:
- File I/O primitives (can write from REPL)
- Deep conversation (REPL remembers context)
- Presence (see who else is exploring)

### Core Work

- `kg repl` enters interactive mode
- Navigation via path expressions
- Tab completion from registry
- Context-aware prompts: `[self.memory] »`
- **NEW**: Presence footer shows active agents
- **NEW**: 10+ turn memory in REPL session

### Exit Condition

**When this feels complete**: The REPL is a conversation partner, not a command executor. It remembers. It shows who's around.

---

## Phase 5: Collaborative Canvas (Web)

> *"A shared mind-map surface where humans and agents have visible presence."*

### Intent

The full Figma-like experience. Cursors, nodes, connections, real-time collaboration. Inspired by [Miro's infinite canvas](https://miro.com/mind-map/) with AI-powered branching and [FigJam's](https://www.figma.com/figjam/mind-map/) collaborative whiteboard.

### Crown Jewel Patterns Applied

| Pattern | Application |
|---------|-------------|
| **#11 Circadian Modulation** | Canvas warmth/brightness adjusts by time of day |
| **#13 Contract-First Types** | Canvas components use generated types from BE |
| **#14 Teaching Mode Toggle** | Explanatory overlays on AGENTESE nodes |

### Industry Innovations Integrated

| Innovation | Source | Application |
|------------|--------|-------------|
| **Infinite Canvas** | [Miro](https://miro.com/mind-map/) | Pan/zoom with no boundaries |
| **AI Branch Generation** | Miro AI | Agent suggests related nodes |
| **Real-time Cursor Presence** | [FigJam](https://www.figma.com/figjam/) | Smooth cursor interpolation |
| **Template Library** | FigJam (300+ templates) | Pre-built AGENTESE node layouts |

### Core Work

#### 5.1 Canvas as Projection Target (Fidelity 0.9)

```python
# agents/i/reactive/projection/targets.py
from agents.i.reactive.projection import ProjectionRegistry

@ProjectionRegistry.register("canvas", fidelity=0.9, description="Collaborative mind-map canvas")
def canvas_projector(widget):
    """
    Project widget state to canvas format.

    HIGH fidelity (0.9) - full visual, interactive, animated.
    """
    return {
        "type": "canvas_node",
        "id": widget.id,
        "position": widget.state.position,
        "content": widget.to_json(),
        "connections": widget.state.connections,
        "style": {
            "animation": widget.state.animation_speed,
            "color": widget.state.color,
        },
    }
```

#### 5.2 Canvas React Component with Contract-First Types

```typescript
// services/conductor/web/components/CollaborativeCanvas.tsx
import { CanvasNode, AgentCursor, PresenceUpdate } from "../_generated/conductor";  // Contract-first types!
import { useCircadian } from "@/hooks/useCircadian";
import { useTeachingMode } from "@/hooks/useTeachingMode";

interface CanvasProps {
  nodes: Map<string, CanvasNode>;
  cursors: Map<string, AgentCursor>;
  onNavigate: (path: string) => void;
  onSelect: (nodeId: string) => void;
}

export function CollaborativeCanvas({ nodes, cursors, onNavigate, onSelect }: CanvasProps) {
  const { phase, modifier } = useCircadian();  // Pattern #11
  const { enabled: teachingEnabled } = useTeachingMode();  // Pattern #14

  // Apply circadian modulation to canvas style
  const canvasStyle = {
    filter: `brightness(${modifier.brightness}) saturate(${1 + modifier.warmth * 0.2})`,
    transition: "filter 30s ease",  // Smooth transitions
  };

  return (
    <div className="canvas-container" style={canvasStyle}>
      {/* Infinite canvas with pan/zoom (Miro-inspired) */}
      <InfiniteCanvas onPan={handlePan} onZoom={handleZoom}>
        {/* Render AGENTESE nodes */}
        {Array.from(nodes.values()).map((node) => (
          <AgentNode
            key={node.id}
            node={node}
            onClick={() => onSelect(node.id)}
            onNavigate={onNavigate}
            showExplanation={teachingEnabled}  // Pattern #14
          />
        ))}

        {/* Render connections between nodes */}
        <ConnectionLayer nodes={nodes} />

        {/* Render agent cursors with smooth interpolation */}
        {Array.from(cursors.values()).map((cursor) => (
          <AnimatedCursor
            key={cursor.agent_id}
            cursor={cursor}
            circadianTempo={modifier.tempo}  // Slower at night
          />
        ))}
      </InfiniteCanvas>

      {/* Teaching callout when enabled */}
      {teachingEnabled && (
        <TeachingCallout category="conceptual">
          This canvas shows the AGENTESE ontology. Each node is an addressable path.
          Agents' cursors show what they're focusing on.
        </TeachingCallout>
      )}
    </div>
  );
}
```

#### 5.3 WebSocket Presence with EventBus Bridge

```typescript
// services/conductor/web/hooks/usePresence.ts
import { useCallback, useEffect, useState } from "react";
import { PresenceUpdate, AgentCursor } from "../_generated/conductor";

export function usePresenceChannel(sessionId: string) {
  const [cursors, setCursors] = useState<Map<string, AgentCursor>>(new Map());
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`wss://kgents.io/presence/${sessionId}`);

    ws.onmessage = (event) => {
      const update: PresenceUpdate = JSON.parse(event.data);
      setCursors((prev) => {
        const next = new Map(prev);
        next.set(update.agent_id, update.cursor);
        return next;
      });
    };

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);

    return () => ws.close();
  }, [sessionId]);

  const broadcastCursor = useCallback((position: { x: number; y: number }) => {
    // Human cursor position broadcast
  }, []);

  return { cursors, connected, broadcastCursor };
}
```

#### 5.4 Agent Cursor Behaviors with Personality

```python
# services/conductor/behaviors.py
from dataclasses import dataclass
from enum import Enum

class CursorBehavior(Enum):
    FOLLOWER = "follower"     # Follows human with slight delay
    EXPLORER = "explorer"     # Independent exploration
    ASSISTANT = "assistant"   # Follows but occasionally suggests
    AUTONOMOUS = "autonomous" # Does its own thing entirely

@dataclass
class BehaviorConfig:
    follow_lag: float = 0.3  # Seconds of lag when following
    exploration_randomness: float = 0.2  # How "drunk" the exploration walk is
    suggestion_probability: float = 0.1  # Chance of making a suggestion per second

class CursorAnimator:
    """Animates agent cursors with personality."""

    def animate_follower(self, target: Position, current: Position, dt: float) -> Position:
        """Smooth follow with personality-appropriate lag."""
        lag = self.config.follow_lag
        # Add slight randomness for organic feel
        noise = random_2d() * 2
        return lerp(current, target + noise, dt / lag)

    def animate_explorer(self, graph: AGENTESEGraph, current: Position, dt: float) -> Position:
        """Random walk through graph with preference for connections."""
        if random() < 0.02:  # 2% chance per frame to jump to connected node
            nearby = graph.get_connected_nodes(current)
            if nearby:
                return random.choice(nearby).position
        # Otherwise, smooth drift
        return current + random_2d() * self.config.exploration_randomness * dt
```

#### 5.5 AI-Powered Branch Suggestions (Miro-Inspired)

```python
@node(path="self.conductor.canvas.suggest")
async def suggest_branches(observer: Observer, focus_path: str) -> list[SuggestionResponse]:
    """
    AI suggests related AGENTESE nodes to explore.

    Miro-inspired: "What else might be relevant to self.memory?"
    """
    current_node = await get_node_info(focus_path)

    # Use LLM to suggest related paths
    suggestions = await suggest_related_paths(
        current=focus_path,
        context=observer.recent_activity,
    )

    return [
        SuggestionResponse(
            path=s.path,
            reason=s.reason,
            confidence=s.confidence,
        )
        for s in suggestions
    ]
```

### Exit Condition

**When this feels complete**:
- Opening the canvas feels like entering a shared space
- Agent cursors move with personality
- The graph is navigable and alive
- **Circadian modulation** makes evening sessions feel warmer
- **AI suggestions** appear when exploring nodes
- **Teaching mode** explains the ontology

### Quality Benchmark

The **coworking test**: Does it feel like working alongside someone? Not just watching a visualization?

The **Miro test**: Can you infinitely pan/zoom? Does AI suggest relevant nodes?

### Deliverables

| Deliverable | Description | Pattern |
|-------------|-------------|---------|
| `services/conductor/web/components/` | Canvas React components | Metaphysical Fullstack |
| `services/conductor/web/hooks/usePresence.ts` | WebSocket presence hook | #13 |
| `services/conductor/behaviors.py` | Agent cursor behaviors | — |
| Canvas projection target | Fidelity 0.9 projection | Projection Registry |
| `self.conductor.canvas.suggest` | AI-powered branch suggestions | Industry Innovation |
| Circadian styling | Time-of-day visual modulation | #11 |
| Teaching overlays | Explanatory callouts | #14 |

---

## Phase 6: Agent Swarms (NEW)

> *"Teams of AI agents corralled under orchestrator uber-models that manage the overall project workflow."* — [Futurum](https://futurumgroup.com/insights/was-2025-really-the-year-of-agentic-ai-or-just-more-agentic-hype/)

### Intent

Implement [CrewAI](https://www.shakudo.io/blog/top-9-ai-agent-frameworks)-inspired role-based orchestration with Agent-to-Agent (A2A) protocol. This is the culmination of CLI v7: multiple specialized agents collaborating on complex tasks.

### Crown Jewel Patterns Applied

| Pattern | Application |
|---------|-------------|
| **#1 Container Owns Workflow** | Swarm owned by ConductorSession |
| **#4 Signal Aggregation** | Agent recommendations based on skill match, availability, past success |
| **#10 Operad Inheritance** | SWARM_OPERAD inherits from DESIGN_OPERAD |

### Industry Innovation: CrewAI Role-Based Orchestration

[CrewAI](https://www.shakudo.io/blog/top-9-ai-agent-frameworks) simulates collaborative problem-solving by assigning different roles to agents in a structured workflow:

- **Researcher**: Read-only exploration, information gathering
- **Planner**: Architecture design, strategy
- **Implementer**: Code writing, file edits
- **Reviewer**: Quality assurance, critique

### Core Work

#### 6.1 Agent Role Taxonomy (Pattern #2: Enum Properties)

```python
# services/conductor/swarm.py
from enum import Enum, auto

class AgentRole(Enum):
    """
    Role-based agent taxonomy.

    CrewAI-inspired: specialized roles for collaborative problem-solving.
    """
    RESEARCHER = auto()   # Read-only exploration
    PLANNER = auto()      # Architecture design
    IMPLEMENTER = auto()  # Code writing
    REVIEWER = auto()     # Quality assurance
    COORDINATOR = auto()  # Orchestration

    @property
    def capabilities(self) -> set[str]:
        return {
            AgentRole.RESEARCHER: {"glob", "grep", "read", "web_search"},
            AgentRole.PLANNER: {"read", "think", "output_plan"},
            AgentRole.IMPLEMENTER: {"read", "edit", "write", "bash"},
            AgentRole.REVIEWER: {"read", "analyze", "critique"},
            AgentRole.COORDINATOR: {"spawn", "message", "aggregate"},
        }[self]

    @property
    def cost_multiplier(self) -> float:
        """LLM cost factor for this role."""
        return {
            AgentRole.RESEARCHER: 0.5,   # Can use faster models
            AgentRole.PLANNER: 1.0,      # Needs full reasoning
            AgentRole.IMPLEMENTER: 1.0,  # Needs precision
            AgentRole.REVIEWER: 0.7,     # Can use faster models
            AgentRole.COORDINATOR: 0.3,  # Minimal LLM usage
        }[self]

    @property
    def max_parallel(self) -> int:
        """Max concurrent agents of this role."""
        return {
            AgentRole.RESEARCHER: 5,   # High parallelism for exploration
            AgentRole.PLANNER: 1,      # One plan at a time
            AgentRole.IMPLEMENTER: 3,  # Parallel file edits (non-overlapping)
            AgentRole.REVIEWER: 2,     # Parallel reviews
            AgentRole.COORDINATOR: 1,  # Single orchestrator
        }[self]
```

#### 6.2 SWARM_OPERAD (Pattern #10: Operad Inheritance)

```python
# services/conductor/operad.py
from agents.operad import Operad, Operation, Law
from agents.design import DESIGN_OPERAD

def create_swarm_operad() -> Operad:
    """
    Operad for swarm composition.

    Pattern #10: Inherits from DESIGN_OPERAD.
    """
    return Operad(
        name="SWARM",
        operations={
            # Swarm-specific operations
            "spawn": Operation(
                arity=1,
                description="Spawn an agent with a role",
                signature="(Task, Role) → Agent",
            ),
            "delegate": Operation(
                arity=2,
                description="Delegate subtask from one agent to another",
                signature="(Agent, Task) → Delegation",
            ),
            "aggregate": Operation(
                arity="*",
                description="Combine results from multiple agents",
                signature="([Result]) → AggregatedResult",
            ),
            "handoff": Operation(
                arity=2,
                description="Transfer context from one agent to another",
                signature="(Agent, Agent) → Handoff",
            ),
            # Inherit all DESIGN_OPERAD operations
            **DESIGN_OPERAD.operations,
        },
        laws=[
            Law(
                name="delegation_associativity",
                description="(a delegate b) delegate c ≡ a delegate (b delegate c)",
                verifier=_verify_delegation_associativity,
            ),
            Law(
                name="aggregation_commutativity",
                description="aggregate([a, b]) ≡ aggregate([b, a])",
                verifier=_verify_aggregation_commutativity,
            ),
            # Inherit DESIGN_OPERAD laws
            *DESIGN_OPERAD.laws,
        ],
    )

SWARM_OPERAD = create_swarm_operad()
```

#### 6.3 A2A (Agent-to-Agent) Protocol

```python
# services/conductor/a2a.py
from dataclasses import dataclass
from protocols.synergy import get_synergy_bus

@dataclass
class A2AMessage:
    """Message between agents."""
    from_agent: str
    to_agent: str
    message_type: str  # "request" | "response" | "handoff" | "notify"
    payload: dict
    correlation_id: str  # For request/response pairing

class A2AChannel:
    """
    Agent-to-Agent communication channel.

    Microsoft A2A pattern: agents communicate without human intermediation.
    """

    async def send(self, message: A2AMessage) -> None:
        """Send message to another agent."""
        event = create_a2a_event(message)
        await get_synergy_bus().emit(event)

    async def request(self, to_agent: str, payload: dict, timeout: float = 30.0) -> dict:
        """Request/response pattern with timeout."""
        correlation_id = str(uuid4())
        message = A2AMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type="request",
            payload=payload,
            correlation_id=correlation_id,
        )
        await self.send(message)
        return await self._wait_for_response(correlation_id, timeout)

    async def handoff(self, to_agent: str, context: dict) -> None:
        """Hand off work to another agent with full context."""
        message = A2AMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type="handoff",
            payload={"context": context, "conversation": self.window.get_messages()},
            correlation_id=str(uuid4()),
        )
        await self.send(message)
```

#### 6.4 Swarm Spawning with Signal Aggregation (Pattern #4)

```python
@node(
    path="self.conductor.swarm.spawn",
    contracts={"spawn": Contract(SwarmSpawnRequest, SwarmSpawnResponse)},
)
async def spawn_swarm(
    observer: Observer,
    task: str,
    roles: list[AgentRole],
    parallel: bool = True,
) -> SwarmSpawnResponse:
    """
    Spawn a coordinated swarm of specialized agents.

    Pattern #4: Signal Aggregation for agent selection.
    """
    session = get_current_session()

    # Signal aggregation: choose best agents for each role
    selected = []
    for role in roles:
        confidence, reason = evaluate_agent_match(
            role=role,
            task=task,
            available_agents=session.available_agents,
        )
        selected.append((role, confidence, reason))

    # Spawn agents
    agents = []
    for role, confidence, reason in selected:
        if confidence >= 0.5:  # Threshold
            agent = await spawn_agent(
                role=role,
                task=task,
                coordinator_id=session.session_id,
            )
            agents.append(agent)

    # Execute
    if parallel:
        results = await asyncio.gather(*[a.run() for a in agents])
    else:
        results = []
        for agent in agents:
            result = await agent.run(context=results)
            results.append(result)

    return SwarmSpawnResponse(
        agents_spawned=len(agents),
        roles=[a.role.name for a in agents],
        results=results,
    )
```

### Exit Condition

**When this feels complete**:
- `kg self.conductor.swarm.spawn "Implement feature X" --roles researcher,planner,implementer`
- Agents spawn with specialized roles
- A2A messages flow between agents via SynergyBus
- Results aggregate correctly

### Quality Benchmark

The **swarm test**: Can 3+ agents collaborate on a task without human intermediation?

### Deliverables

| Deliverable | Description | Pattern |
|-------------|-------------|---------|
| `services/conductor/swarm.py` | AgentRole taxonomy, swarm spawning | #2, #4 |
| `services/conductor/operad.py` | SWARM_OPERAD with inheritance | #10 |
| `services/conductor/a2a.py` | Agent-to-Agent protocol | Industry Innovation |
| SynergyBus A2A events | A2A_REQUEST, A2A_RESPONSE, A2A_HANDOFF | Data Bus Integration |
| Tests for operad laws | Verify delegation associativity | #10 |

---

## Phase 7: Live Flux (From v6)

> *"When one projection makes a change, others update via the SynergyBus."*

### Intent

Real-time sync across all surfaces—CLI, REPL, TUI, Canvas, Web, sshx-shared terminals.

### Core Work

Unchanged from v6, but now syncs:
- **File changes** (from Phase 1) → SynergyBus FILE_EDITED
- **Conversation state** (from Phase 2) → EventBus[ConversationEvent]
- **Agent presence** (from Phase 3) → EventBus[PresenceUpdate]
- **Canvas state** (from Phase 5) → EventBus[CanvasUpdate]
- **Swarm activity** (from Phase 6) → SynergyBus A2A_*

### Three-Bus Integration Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLI v7 Event Flow                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Phase 1 (Files)          Phase 2 (Conversation)     Phase 6 (Swarm)      │
│       │                          │                          │               │
│       ▼                          ▼                          ▼               │
│   ┌───────────┐           ┌────────────┐            ┌────────────┐         │
│   │ DataBus   │           │ EventBus   │            │ SynergyBus │         │
│   │ (D-gent)  │           │ (Conv)     │            │ (A2A)      │         │
│   └─────┬─────┘           └──────┬─────┘            └──────┬─────┘         │
│         │                        │                         │                │
│         └────────────────────────┴─────────────────────────┘                │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                    SynergyBus (Cross-Jewel)                      │      │
│   │  FILE_EDITED │ CONVERSATION_TURN │ PRESENCE_UPDATE │ SWARM_*    │      │
│   └───────────────────────────────────┬─────────────────────────────┘      │
│                                       │                                     │
│                                       ▼                                     │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                    EventBus (UI Fan-Out)                          │    │
│   │  CLI Footer │ TUI Status │ Canvas Render │ sshx Stream │ Web UI  │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Cross-Phase Principles

### 1. Read-Before-Edit (Puppetized from Claude Code)

Agents must understand before modifying. No blind writes.

**Pattern Applied**: #15 No Hollow Services — FileEditGuard injected via DI

### 2. Exact String Replacement (Puppetized from Claude Code)

Edits find exact strings. No ambiguity. No merge conflicts.

**Pattern Applied**: #7 Dual-Channel Output — errors include `semantic` payload

### 3. Conversation Has Memory

10+ turns of context. Summarization for longer sessions.

**Pattern Applied**: #8 Bounded History Trace, #11 Circadian Modulation

### 4. Presence Is Real

Agents aren't invisible. Their cursors, activity, and focus are visible.

**Pattern Applied**: #2 Enum Property Pattern, #9 Directed State Cycle

### 5. The Canvas Is Shared

Humans and agents occupy the same space. No separate views.

**Pattern Applied**: #13 Contract-First Types, #14 Teaching Mode Toggle

### 6. Swarms Have Roles (NEW)

Agents specialize. Researchers explore, planners design, implementers code, reviewers critique.

**Pattern Applied**: #10 Operad Inheritance, #4 Signal Aggregation

### 7. Events Flow Through Buses (NEW)

All state changes emit events. DataBus → SynergyBus → EventBus.

**Pattern Applied**: Data Bus Integration (three-bus architecture)

---

## Dependency Map (Updated)

```
Phase 0 ✓────────► (COMPLETE) Ground Truth
         │
         ├─────────────────────────────────────────────────┐
         │                                                 │
         ▼                                                 ▼
Phase 1 ─────────► File I/O Primitives        Phase 2 ─────────► Deep Conversation
         │         Patterns: #1, #7, #13, #15              │         Patterns: #1, #6, #8, #11
         │                                                 │
         ├─────────────────────────────────────────────────┤
         │                                                 │
         ▼                                                 ▼
Phase 3 ─────────────────────────────────────────────────────► Agent Presence (CLI)
         │                                                           Patterns: #2, #9, #11, #14
         │                                                           Industry: sshx
         ▼
Phase 4 ─────────► The REPL
         │         Requires: Phases 1, 2, 3
         │         Produces: Interactive exploration + memory + presence
         │
         ▼
Phase 5 ─────────► Collaborative Canvas (Web)
         │         Patterns: #11, #13, #14
         │         Industry: Miro, FigJam
         │         Produces: Full mind-map with AI suggestions
         │
         ▼
Phase 6 ─────────► Agent Swarms (NEW)
         │         Patterns: #1, #2, #4, #10
         │         Industry: CrewAI, Microsoft A2A
         │         Produces: Role-based multi-agent coordination
         │
         ▼
Phase 7 ─────────► Live Flux
                   Requires: All previous phases
                   Produces: Real-time sync across all surfaces
                   Integration: DataBus → SynergyBus → EventBus
```

**Parallelization**: Phases 1, 2, and 3 can run concurrently.

**Critical Path**: Phase 0 → (1,2,3) → 4 → 5 → 6 → 7

---

## 🧪 Test Strategy (T-gent Taxonomy)

Following `docs/skills/test-patterns.md`, each phase has a test target by type:

| Phase | Type I (Unit) | Type II (Integration) | Type III (Property) | Type IV (E2E) | Total Target |
|-------|---------------|----------------------|---------------------|---------------|--------------|
| **Phase 1: File I/O** | 15 | 8 | 5 (edge cases) | 2 | **30** |
| **Phase 2: Conversation** | 10 | 5 | 10 (summarization) | 2 | **27** |
| **Phase 3: Presence** | 12 | 6 | 3 (state transitions) | 2 | **23** |
| **Phase 4: REPL** | 8 | 10 | 2 | 5 | **25** |
| **Phase 5: Canvas** | 15 | 8 | 5 | 8 | **36** |
| **Phase 6: Swarms** | 20 | 15 | 10 (coordination) | 5 | **50** |
| **Phase 7: Flux** | 10 | 20 | 5 | 5 | **40** |
| **TOTAL** | 90 | 72 | 40 | 29 | **231** |

### Key Test Patterns by Phase

**Phase 1 (File I/O)**:
```python
# Type III: Property-based test for edit uniqueness
@given(st.text(min_size=1), st.text(min_size=1), st.text())
def test_edit_unique_string_or_fails(content, old_string, new_string):
    """Old string must be unique in file for edit to succeed."""
    count = content.count(old_string)
    if count > 1:
        with pytest.raises(AmbiguousEditError):
            guard.edit(content, old_string, new_string)
```

**Phase 2 (Conversation)**:
```python
# Type III: Property-based test for summarization bounds
@given(st.lists(st.text(), min_size=20, max_size=100))
def test_window_never_exceeds_max_turns(turns):
    """Window maintains bounded history regardless of input size."""
    window = ConversationWindow(max_turns=10)
    for turn in turns:
        window.add_turn(turn, "response")
    assert len(window.turns) <= 10
```

**Phase 3 (Presence)**:
```python
# Type I: Unit test for state transition validity
def test_cursor_state_transitions():
    """Verify directed state cycle (Pattern #9)."""
    cursor = AgentCursor(state=CursorState.WAITING)
    assert cursor.can_transition_to(CursorState.FOLLOWING)
    assert not cursor.can_transition_to(CursorState.SUGGESTING)
```

### Performance Baselines

| Metric | Target | Verified By |
|--------|--------|-------------|
| File read cache hit | <1ms | `test_file_read_cache_performance` |
| Presence broadcast latency | <50ms | `test_presence_broadcast_latency` |
| 10-turn context retrieval | <100ms | `test_conversation_context_performance` |
| Canvas render (100 nodes) | <16ms (60fps) | `test_canvas_render_performance` |

---

## The Self-Awareness Integration

From the introspection on Claude Code's strengths:

| My Strength | How v7 Harnesses It |
|-------------|---------------------|
| **Precise file edits** | Phase 1: Exact string replacement |
| **Read-before-edit** | Phase 1: Guard pattern |
| **Parallel tool calls** | Phase 5: Concurrent agent operations |
| **Context management** | Phase 2: Summarization |
| **Planning mode** | Canvas supports explore → plan → execute |
| **Professional objectivity** | Agents disagree when appropriate |
| **Teaching through doing** | Presence shows work in progress |

---

## When Is CLI v7 "Done"?

CLI v7 is complete when:

1. **An agent can safely write plans to disk** using puppetized Claude Code patterns.

2. **A 15-turn conversation maintains coherent context** without manual intervention.

3. **Opening the canvas feels like entering a shared space** with visible collaborators.

4. **Agent cursors have personality** — following, exploring, suggesting with character.

5. **Changes propagate instantly** across CLI, REPL, TUI, Canvas.

6. **You feel less alone** when working with the system.

7. **Multiple agents collaborate via A2A protocol** without human intermediation. (NEW)

8. **Session sharing works** via sshx-inspired `kg self.conductor.share`. (NEW)

---

## 🎯 Metaphysical Fullstack Alignment Summary

This plan is now **fully grounded** in the kgents architectural foundation:

### Crown Jewel Service

| Component | Location | Notes |
|-----------|----------|-------|
| **Conductor** | `services/conductor/` | The new Crown Jewel |
| Session | `services/conductor/session.py` | Pattern #1: Container Owns Workflow |
| FileGuard | `services/conductor/file_guard.py` | Pattern #15: No Hollow Services |
| Window | `services/conductor/window.py` | Pattern #8: Bounded History |
| Presence | `services/conductor/presence.py` | Patterns #2, #9, #11, #14 |
| Swarm | `services/conductor/swarm.py` | Patterns #1, #2, #4, #10 |
| A2A | `services/conductor/a2a.py` | Industry: Microsoft A2A |
| Web | `services/conductor/web/` | Metaphysical Fullstack (FE with service) |

### Crown Jewel Patterns Applied

**Essential 4 patterns** (use these first—cover 80% of needs):

| # | Pattern | When to Use | CLI v7 Example |
|---|---------|-------------|----------------|
| **#1** | Container Owns Workflow | State that outlives operations | `ConductorSession` owns `Window`, `Swarm` |
| **#8** | Bounded History Trace | Any append-only data | `ConversationWindow.turns` capped at 10 |
| **#13** | Contract-First Types | Any AGENTESE node | All nodes use `contracts={}` |
| **#15** | No Hollow Services | Services with runtime config | `FileEditGuard` via DI only |

**Additional patterns** (use when needed):

| # | Pattern | Applied In |
|---|---------|------------|
| 2 | Enum Property Pattern | CursorState, AgentRole |
| 4 | Signal Aggregation | Agent selection for swarm |
| 6 | Async-Safe Event Emission | ConversationWindow |
| 7 | Dual-Channel Output | File operation errors |
| 9 | Directed State Cycle | CursorState transitions |
| 10 | Operad Inheritance | SWARM_OPERAD ← DESIGN_OPERAD |
| 11 | Circadian Modulation | Summarization, Canvas, Cursor animation |
| 14 | Teaching Mode Toggle | Canvas overlays, CLI presence |

**Reference**: `docs/skills/crown-jewel-patterns.md` (full pattern catalog)

### Three-Bus Integration

| Bus | Used For | Events |
|-----|----------|--------|
| **DataBus** | D-gent persistence | Turn storage, file caching |
| **SynergyBus** | Cross-jewel coordination | FILE_EDITED, SWARM_*, A2A_* |
| **EventBus** | UI fan-out | PresenceUpdate, ConversationEvent, CanvasUpdate |

### Industry Innovations Incorporated

| Innovation | Source | Application |
|------------|--------|-------------|
| Agentic Development Environment | [Warp](https://linearb.io/blog/future-of-the-terminal-ai-developer-experience) | Conductor as control plane |
| Terminal sharing | [sshx](https://www.blog.brightcoding.dev/2025/09/13/sshx-a-secure-web-based-collaborative-terminal-for-effortless-session-sharing/) | `kg self.conductor.share` |
| Infinite canvas + AI branching | [Miro](https://miro.com/mind-map/) | CollaborativeCanvas |
| Real-time cursor presence | [FigJam](https://www.figma.com/figjam/mind-map/) | AgentCursor with behaviors |
| Role-based orchestration | [CrewAI](https://www.shakudo.io/blog/top-9-ai-agent-frameworks) | AgentRole taxonomy |
| A2A protocol | [Microsoft](https://blogs.microsoft.com/blog/2025/05/19/microsoft-build-2025-the-age-of-ai-agents-and-building-the-open-agentic-web/) | Agent-to-Agent messaging |

---

## Voice Anchors (Kent's Intent Preserved)

> *"Daring, bold, creative, opinionated but not gaudy"*

Multiplayer cursors for agents is daring. sshx-inspired sharing is bold. CrewAI role taxonomy is opinionated. But grounded in proven patterns—not gaudy.

> *"The persona is a garden, not a museum"*

The canvas is alive—cursors move, agents work, artifacts grow. Circadian modulation makes it breathe.

> *"Depth over breadth"*

Three pillars (Canvas, Files, Conversation) + one new pillar (Swarms), done deeply. Not 20 half-baked features.

> *"Tasteful > feature-complete"*

Every feature has a Crown Jewel pattern. Every innovation has a source. Nothing is "just because."

---

## Sources

This enhanced plan incorporates research from:

- [Awesome Testing: Why AI Coding Is Moving Back to the Terminal](https://www.awesome-testing.com/2025/12/why-ai-coding-is-moving-back-to-terminal)
- [LinearB: The Future of the Terminal](https://linearb.io/blog/future-of-the-terminal-ai-developer-experience)
- [sshx: Collaborative Terminal Sharing](https://www.blog.brightcoding.dev/2025/09/13/sshx-a-secure-web-based-collaborative-terminal-for-effortless-session-sharing/)
- [Miro: AI-Powered Mind Mapping](https://miro.com/mind-map/)
- [FigJam: Collaborative Whiteboard](https://www.figma.com/figjam/mind-map/)
- [Shakudo: Top AI Agent Frameworks 2025](https://www.shakudo.io/blog/top-9-ai-agent-frameworks)
- [Microsoft Build 2025: The Age of AI Agents](https://blogs.microsoft.com/blog/2025/05/19/microsoft-build-2025-the-age-of-ai-agents-and-building-the-open-agentic-web/)
- [Futurum: Was 2025 the Year of Agentic AI?](https://futurumgroup.com/insights/was-2025-really-the-year-of-agentic-ai-or-just-more-agentic-hype/)

---

*"The canvas is where we meet. Your cursor and mine, dancing through the garden together."*

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| **7.0** | 2025-12-20 | **Phase 4 COMPLETE**: REPL presence footer wired, 382 tests passing, continuation prompt for Phase 5 |
| 6.0 | 2025-12-20 | Phase 3 COMPLETE: CursorState, AgentCursor, CircadianPhase, PresenceChannel, 205 tests |
| 5.0 | 2025-12-20 | Phases 1 & 2 VERIFIED: 146 conductor tests, FileEditGuard, WorldFileNode, WindowPersistence |
| 4.0 | 2025-12-20 | Phase 2 COMPLETE: ConversationWindow, Summarizer, D-gent Persistence |
| 3.0 | 2025-12-19 | Quality refinement: Conductor/kgentsd clarification, Pareto prioritization, test strategy |
| 2.0 | 2025-12-19 | Metaphysical Fullstack Edition: Crown Jewel Patterns, Three-Bus Integration |
| 1.0 | 2025-12-19 | Initial plan |

---

*Version: 7.0 — Phase 4 Complete Edition*
*Principle: Collaboration, not just automation.*
*Progress: Phase 0 ✅ Phase 1 ✅ Phase 2 ✅ Phase 3 ✅ Phase 4 ✅ → Phase 5 (Canvas) ready*
*Continuation: `plans/cli-v7-phase5-continuation.md`*
