# kgentsd Event Architecture

> *"The daemon does not poll. The daemon listens."*

**Status**: PLANNING
**Parent**: `plans/kgentsd-crown-jewel.md`
**Focus**: Event-driven core, watcher implementations, Flux integration

---

## Core Principle: No Timers

The old Ghost used a 3-minute timer loop. This is fundamentally wrong:

```python
# ANTI-PATTERN: Timer-driven
while running:
    await asyncio.sleep(180)  # What if nothing changed?
    await project_once()       # Waste of cycles
```

**kgentsd reacts to events**. If nothing happens, daemon does nothing. If 100 things happen in 1 second, daemon handles them all.

---

## Event Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EVENT SOURCES                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │Filesystem│ │   Git   │ │  Tests  │ │AGENTESE │ │   CI    │       │
│  │ inotify  │ │  hooks  │ │ pytest  │ │SynergyBus│ │webhook │       │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │
└───────┼──────────┼──────────┼──────────┼──────────┼────────────────┘
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EVENT BUS (asyncio.Queue)                       │
│                                                                      │
│  Priority queue with event types:                                    │
│  - CRITICAL: Test failures, CI failures, errors                      │
│  - HIGH: Git commits, AGENTESE mutations                             │
│  - NORMAL: File changes, observations                                │
│  - LOW: Periodic health checks, stats                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUX PROCESSOR (DaemonFlux)                       │
│                                                                      │
│  async for event in event_bus:                                       │
│      action = await daemon_polynomial.react(event)                   │
│      if action.requires_trust(current_trust):                        │
│          await execute_action(action)                                │
│      else:                                                           │
│          await queue_for_escalation(action)                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ACTION EXECUTOR                                 │
│                                                                      │
│  Based on trust level:                                               │
│  - Level 0: Observe and log only                                     │
│  - Level 1: Write to .kgents/ directory                              │
│  - Level 2: Propose and await confirmation                           │
│  - Level 3: Execute autonomously (with logging)                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Event Type Hierarchy

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

class EventPriority(Enum):
    CRITICAL = 0  # Process immediately
    HIGH = 1      # Process soon
    NORMAL = 2    # Process in order
    LOW = 3       # Process when idle


@dataclass
class SystemEvent:
    """Base class for all daemon events."""
    timestamp: datetime
    source: str
    priority: EventPriority = EventPriority.NORMAL
    metadata: dict[str, Any] = None


# === Filesystem Events ===

@dataclass
class FileCreated(SystemEvent):
    path: str
    size: int

@dataclass
class FileModified(SystemEvent):
    path: str
    old_size: int
    new_size: int

@dataclass
class FileDeleted(SystemEvent):
    path: str

@dataclass
class FileRenamed(SystemEvent):
    old_path: str
    new_path: str


# === Git Events ===

@dataclass
class GitCommit(SystemEvent):
    sha: str
    message: str
    author: str
    files_changed: list[str]
    priority: EventPriority = EventPriority.HIGH

@dataclass
class GitPush(SystemEvent):
    branch: str
    commits: list[str]
    priority: EventPriority = EventPriority.HIGH

@dataclass
class GitPull(SystemEvent):
    branch: str
    commits_received: int

@dataclass
class GitBranchSwitch(SystemEvent):
    from_branch: str
    to_branch: str


# === Test Events ===

@dataclass
class TestStarted(SystemEvent):
    test_id: str
    file: str
    line: int

@dataclass
class TestPassed(SystemEvent):
    test_id: str
    duration_ms: float

@dataclass
class TestFailed(SystemEvent):
    test_id: str
    error: str
    traceback: str
    priority: EventPriority = EventPriority.CRITICAL

@dataclass
class TestSessionComplete(SystemEvent):
    passed: int
    failed: int
    skipped: int
    duration_ms: float
    priority: EventPriority = EventPriority.HIGH


# === AGENTESE Events ===

@dataclass
class AgenteseInvocation(SystemEvent):
    path: str
    aspect: str
    observer: str
    duration_ms: float
    success: bool

@dataclass
class AgenteseError(SystemEvent):
    path: str
    aspect: str
    error: str
    priority: EventPriority = EventPriority.HIGH


# === CI Events ===

@dataclass
class CIWorkflowStarted(SystemEvent):
    workflow: str
    run_id: str
    trigger: str

@dataclass
class CIJobCompleted(SystemEvent):
    workflow: str
    job: str
    status: str  # "success", "failure", "cancelled"
    duration_ms: float

@dataclass
class CIWorkflowCompleted(SystemEvent):
    workflow: str
    run_id: str
    status: str
    duration_ms: float
    priority: EventPriority = EventPriority.HIGH


# === Daemon Internal Events ===

@dataclass
class TrustEscalation(SystemEvent):
    from_level: int
    to_level: int
    reason: str
    priority: EventPriority = EventPriority.HIGH

@dataclass
class ActionExecuted(SystemEvent):
    action_id: str
    action_type: str
    success: bool
    details: dict[str, Any]
```

---

## Watcher Implementations

### Filesystem Watcher

```python
# services/daemon/watchers/filesystem.py

import asyncio
from pathlib import Path
from typing import AsyncGenerator

# Platform-specific imports
try:
    import inotify.adapters
    HAS_INOTIFY = True
except ImportError:
    HAS_INOTIFY = False

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False


class FilesystemWatcher:
    """
    Cross-platform filesystem watcher.

    Uses inotify on Linux, FSEvents on macOS (via watchdog),
    with fallback to polling if neither available.
    """

    WATCH_PATTERNS = [
        "**/*.py",
        "**/*.ts",
        "**/*.tsx",
        "**/*.md",
        "**/pyproject.toml",
        "**/package.json",
    ]

    IGNORE_PATTERNS = [
        "**/__pycache__/**",
        "**/node_modules/**",
        "**/.git/**",
        "**/.venv/**",
        "**/dist/**",
        "**/build/**",
    ]

    def __init__(self, root: Path):
        self.root = root
        self._running = False

    async def watch(self) -> AsyncGenerator[SystemEvent, None]:
        """Yield filesystem events as they occur."""
        self._running = True

        if HAS_INOTIFY:
            async for event in self._watch_inotify():
                yield event
        elif HAS_WATCHDOG:
            async for event in self._watch_watchdog():
                yield event
        else:
            async for event in self._watch_polling():
                yield event

    async def _watch_inotify(self) -> AsyncGenerator[SystemEvent, None]:
        """Linux inotify-based watching."""
        i = inotify.adapters.InotifyTree(str(self.root))

        for event in i.event_gen(yield_nones=False):
            if not self._running:
                break

            (_, type_names, path, filename) = event
            full_path = Path(path) / filename

            if self._should_ignore(full_path):
                continue

            if "IN_CREATE" in type_names:
                yield FileCreated(
                    timestamp=datetime.now(),
                    source="filesystem",
                    path=str(full_path),
                    size=full_path.stat().st_size if full_path.exists() else 0,
                )
            elif "IN_MODIFY" in type_names:
                yield FileModified(
                    timestamp=datetime.now(),
                    source="filesystem",
                    path=str(full_path),
                    old_size=0,  # Would need to track
                    new_size=full_path.stat().st_size if full_path.exists() else 0,
                )
            elif "IN_DELETE" in type_names:
                yield FileDeleted(
                    timestamp=datetime.now(),
                    source="filesystem",
                    path=str(full_path),
                )

            await asyncio.sleep(0)  # Yield control

    def _should_ignore(self, path: Path) -> bool:
        """Check if path matches ignore patterns."""
        path_str = str(path)
        for pattern in self.IGNORE_PATTERNS:
            if fnmatch.fnmatch(path_str, pattern):
                return True
        return False

    def stop(self):
        """Stop watching."""
        self._running = False
```

### Git Watcher

```python
# services/daemon/watchers/git.py

import asyncio
import subprocess
from pathlib import Path
from typing import AsyncGenerator


class GitWatcher:
    """
    Watches git operations.

    Two modes:
    1. Hook-based: Install hooks that notify daemon
    2. Polling-based: Poll git status periodically (fallback)
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self._running = False
        self._last_head = None

    async def watch(self) -> AsyncGenerator[SystemEvent, None]:
        """Yield git events."""
        self._running = True
        self._last_head = await self._get_head()

        while self._running:
            # Check for HEAD changes (commits, checkouts)
            current_head = await self._get_head()
            if current_head != self._last_head:
                yield await self._analyze_head_change(self._last_head, current_head)
                self._last_head = current_head

            # Check for uncommitted changes
            status = await self._get_status()
            if status["dirty"]:
                # Could emit FileModified events for dirty files
                pass

            await asyncio.sleep(1)  # Check every second

    async def _get_head(self) -> str:
        """Get current HEAD commit."""
        proc = await asyncio.create_subprocess_exec(
            "git", "rev-parse", "HEAD",
            cwd=self.repo_path,
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        return stdout.decode().strip()

    async def _get_status(self) -> dict:
        """Get git status summary."""
        proc = await asyncio.create_subprocess_exec(
            "git", "status", "--porcelain",
            cwd=self.repo_path,
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        lines = stdout.decode().strip().split("\n")
        return {
            "dirty": bool(lines and lines[0]),
            "staged": len([l for l in lines if l and l[0] != " " and l[0] != "?"]),
            "unstaged": len([l for l in lines if l and len(l) > 1 and l[1] != " "]),
            "untracked": len([l for l in lines if l.startswith("??")]),
        }

    async def _analyze_head_change(self, old: str, new: str) -> SystemEvent:
        """Analyze what changed between commits."""
        proc = await asyncio.create_subprocess_exec(
            "git", "log", "--oneline", f"{old}..{new}",
            cwd=self.repo_path,
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        commits = stdout.decode().strip().split("\n")

        if len(commits) == 1:
            # Single commit
            sha, message = commits[0].split(" ", 1)
            return GitCommit(
                timestamp=datetime.now(),
                source="git",
                sha=sha,
                message=message,
                author=await self._get_author(sha),
                files_changed=await self._get_changed_files(sha),
            )
        else:
            # Multiple commits (pull/merge)
            return GitPull(
                timestamp=datetime.now(),
                source="git",
                branch=await self._get_branch(),
                commits_received=len(commits),
            )
```

### Test Watcher (pytest plugin)

```python
# services/daemon/watchers/tests.py
# Also requires conftest.py integration

import asyncio
from typing import AsyncGenerator


class TestWatcher:
    """
    Watches pytest test execution.

    Receives events from pytest hooks via a queue.
    The conftest.py plugin pushes events to this queue.
    """

    def __init__(self):
        self._queue: asyncio.Queue[SystemEvent] = asyncio.Queue()
        self._running = False

    async def watch(self) -> AsyncGenerator[SystemEvent, None]:
        """Yield test events from queue."""
        self._running = True

        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                yield event
            except asyncio.TimeoutError:
                continue

    def push_event(self, event: SystemEvent):
        """Called by pytest hooks to push events."""
        self._queue.put_nowait(event)


# === conftest.py integration ===

# In conftest.py:
# from services.daemon.watchers.tests import get_test_watcher
#
# @pytest.hookimpl
# def pytest_runtest_logreport(report):
#     watcher = get_test_watcher()
#     if report.when == "call":
#         if report.passed:
#             watcher.push_event(TestPassed(...))
#         elif report.failed:
#             watcher.push_event(TestFailed(...))
```

### AGENTESE Watcher

```python
# services/daemon/watchers/agentese.py

from typing import AsyncGenerator
from protocols.event_bus import SynergyBus


class AgenteseWatcher:
    """
    Watches all AGENTESE invocations via SynergyBus.

    Subscribes to cross-jewel events and daemon-relevant paths.
    """

    SUBSCRIPTIONS = [
        "world.**",      # All world events
        "self.**",       # All self events
        "concept.**",    # All concept events
        "time.**",       # All time events
        "void.entropy",  # Entropy sips
    ]

    def __init__(self, synergy_bus: SynergyBus):
        self.bus = synergy_bus
        self._running = False

    async def watch(self) -> AsyncGenerator[SystemEvent, None]:
        """Yield AGENTESE events from SynergyBus."""
        self._running = True

        async for event in self.bus.subscribe(self.SUBSCRIPTIONS):
            if not self._running:
                break

            yield AgenteseInvocation(
                timestamp=datetime.now(),
                source="agentese",
                path=event.path,
                aspect=event.aspect,
                observer=event.observer.archetype,
                duration_ms=event.duration_ms,
                success=event.success,
            )
```

---

## Flux Integration

```python
# services/daemon/flux.py

from agents.flux import Flux, FluxAgent
from typing import AsyncGenerator


class DaemonFlux(FluxAgent[DaemonState, SystemEvent, DaemonAction]):
    """
    Event-driven daemon core using Flux lifting.

    Transforms discrete SystemEvents into continuous DaemonActions.
    """

    def __init__(self, polynomial: DaemonPolynomial):
        self.polynomial = polynomial

    async def process(
        self,
        events: AsyncGenerator[SystemEvent, None]
    ) -> AsyncGenerator[DaemonAction, None]:
        """Process event stream, yield actions."""

        async for event in events:
            # Let polynomial react based on current mode (trust level)
            action = await self.polynomial.react(event)

            if action is not None:
                yield action

    async def start(self, watchers: list[Watcher]) -> AsyncGenerator[DaemonAction, None]:
        """Start daemon with all watchers."""

        # Merge all watcher streams
        async def merged_events():
            tasks = [asyncio.create_task(self._watch(w)) for w in watchers]
            queue = asyncio.Queue()

            async def forward(watcher):
                async for event in watcher.watch():
                    await queue.put(event)

            for w in watchers:
                asyncio.create_task(forward(w))

            while True:
                event = await queue.get()
                yield event

        async for action in self.process(merged_events()):
            yield action
```

---

## Debouncing and Backpressure

```python
# services/daemon/debounce.py

import asyncio
from collections import defaultdict
from typing import AsyncGenerator


class EventDebouncer:
    """
    Debounces rapid-fire events.

    Multiple filesystem events for the same file within debounce_ms
    are coalesced into a single event.
    """

    def __init__(self, debounce_ms: float = 100):
        self.debounce_ms = debounce_ms
        self._pending: dict[str, SystemEvent] = {}
        self._timers: dict[str, asyncio.Task] = {}

    async def debounce(
        self,
        events: AsyncGenerator[SystemEvent, None]
    ) -> AsyncGenerator[SystemEvent, None]:
        """Debounce event stream."""
        output_queue: asyncio.Queue[SystemEvent] = asyncio.Queue()

        async def emit_after_delay(key: str):
            await asyncio.sleep(self.debounce_ms / 1000)
            if key in self._pending:
                await output_queue.put(self._pending.pop(key))
                del self._timers[key]

        async def process():
            async for event in events:
                key = self._event_key(event)

                # Cancel existing timer
                if key in self._timers:
                    self._timers[key].cancel()

                # Store latest event
                self._pending[key] = event

                # Start new timer
                self._timers[key] = asyncio.create_task(emit_after_delay(key))

        asyncio.create_task(process())

        while True:
            yield await output_queue.get()

    def _event_key(self, event: SystemEvent) -> str:
        """Generate deduplication key for event."""
        if isinstance(event, (FileCreated, FileModified, FileDeleted)):
            return f"file:{event.path}"
        elif isinstance(event, GitCommit):
            return f"git:commit:{event.sha}"
        else:
            return f"{event.source}:{id(event)}"
```

---

## Priority Queue

```python
# services/daemon/priority.py

import asyncio
import heapq
from dataclasses import dataclass, field
from typing import AsyncGenerator, Any


@dataclass(order=True)
class PrioritizedEvent:
    priority: int
    sequence: int  # Tie-breaker for same priority
    event: SystemEvent = field(compare=False)


class PriorityEventQueue:
    """
    Priority queue for daemon events.

    Critical events (test failures, errors) are processed first.
    """

    def __init__(self):
        self._heap: list[PrioritizedEvent] = []
        self._sequence = 0
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Event()

    async def put(self, event: SystemEvent):
        """Add event to queue."""
        async with self._lock:
            self._sequence += 1
            heapq.heappush(
                self._heap,
                PrioritizedEvent(
                    priority=event.priority.value,
                    sequence=self._sequence,
                    event=event,
                )
            )
            self._not_empty.set()

    async def get(self) -> SystemEvent:
        """Get highest priority event."""
        while True:
            async with self._lock:
                if self._heap:
                    item = heapq.heappop(self._heap)
                    if not self._heap:
                        self._not_empty.clear()
                    return item.event
            await self._not_empty.wait()

    async def stream(self) -> AsyncGenerator[SystemEvent, None]:
        """Stream events in priority order."""
        while True:
            yield await self.get()
```

---

## Implementation Checklist

### Week 2 Deliverables

- [ ] `services/daemon/events.py` — Event type definitions
- [ ] `services/daemon/watchers/__init__.py` — Watcher registry
- [ ] `services/daemon/watchers/filesystem.py` — Filesystem watcher
- [ ] `services/daemon/watchers/git.py` — Git watcher
- [ ] `services/daemon/watchers/tests.py` — Test watcher
- [ ] `services/daemon/watchers/agentese.py` — AGENTESE watcher
- [ ] `services/daemon/watchers/ci.py` — CI watcher
- [ ] `services/daemon/flux.py` — Flux integration
- [ ] `services/daemon/debounce.py` — Event debouncing
- [ ] `services/daemon/priority.py` — Priority queue
- [ ] `services/daemon/_tests/test_watchers.py` — Watcher tests
- [ ] `services/daemon/_tests/test_flux.py` — Flux tests

---

*"Events flow like water; the daemon is the riverbed."*
