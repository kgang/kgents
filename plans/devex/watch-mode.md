---
path: devex/watch-mode
status: planned
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Plan created from strategic recommendations.
  Priority 5 of 6 DevEx improvements.
---

# K-gent Watch Mode: `kgents soul watch`

> *"K-gent as ambient pair programmer."*

**Goal**: Transform K-gent from a command to a companion that watches development and offers contextual guidance.
**Priority**: 5 (very high impact, medium effort)

---

## The Problem

K-gent exists but requires explicit invocation. It's a tool, not a presence. The soul should be ambient, not summoned.

---

## The Solution

```bash
$ kgents soul watch

K-gent is watching... (Ctrl+C to stop)

[K-gent notices you edited agents/k/persona.py]
  > "The soul file touched. Run `kgents soul validate` before committing?"

[K-gent notices 3 new files without tests]
  > "Untested code is unverified belief. Consider tests for:
     - agents/weather_agent/agent.py
     - agents/weather_agent/types.py"

[K-gent notices high pressure (82%)]
  > "The system runs hot. Try `kgents tithe` or take a walk."

[K-gent notices you've been coding for 3 hours]
  > "Even the river rests in eddies. Stretch?"
```

---

## Research & References

### Python Watchdog Library
- Cross-platform filesystem monitoring
- Watcher + Handler architecture
- Event types: created, modified, deleted, moved
- Source: [Watchdog PyPI](https://pypi.org/project/watchdog/)
- Source: [Watchdog GitHub](https://github.com/gorakhargosh/watchdog)

### Developer Experience Patterns
- Real-time feedback during development
- Automatic server reload (common pattern)
- Source: [KDnuggets Watchdog Guide](https://www.kdnuggets.com/monitor-your-file-system-with-pythons-watchdog)

### Use Case: CI/CD Pipelines
- Trigger tests on file change
- Process documents on arrival
- Source: [DEV.to Watchdog Tutorial](https://dev.to/devasservice/mastering-file-system-monitoring-with-watchdog-in-python-483c)

---

## Implementation Outline

### Phase 1: File Watcher (~100 LOC)
```python
# agents/k/watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class KgentFileHandler(FileSystemEventHandler):
    """Handle file events with K-gent awareness."""

    def __init__(self, soul: Soul, heuristics: list[Heuristic]):
        self.soul = soul
        self.heuristics = heuristics

    def on_modified(self, event):
        if event.is_directory:
            return
        for heuristic in self.heuristics:
            if heuristic.matches(event.src_path):
                self._notify(heuristic.message(event))

    def _notify(self, message: str) -> None:
        # Use K-gent dialogue for the notification
        response = self.soul.quick_response(message)
        console.print(f"[K-gent] {response}")
```

### Phase 2: Heuristics Engine (~150 LOC)
```python
# agents/k/heuristics.py
from abc import ABC, abstractmethod

class Heuristic(ABC):
    """Base class for watch heuristics."""

    @abstractmethod
    def matches(self, path: str) -> bool: ...

    @abstractmethod
    def message(self, event: FileSystemEvent) -> str: ...


class SoulFileHeuristic(Heuristic):
    """Detect edits to K-gent soul files."""

    SOUL_PATTERNS = ["persona.py", "eigenvectors.py", "garden.py"]

    def matches(self, path: str) -> bool:
        return any(p in path for p in self.SOUL_PATTERNS)

    def message(self, event) -> str:
        return f"Soul file edited: {event.src_path}. Validate?"


class UntestedCodeHeuristic(Heuristic):
    """Detect new code files without corresponding tests."""

    def matches(self, path: str) -> bool:
        if not path.endswith(".py"):
            return False
        if "_tests" in path or "test_" in path:
            return False
        test_path = self._expected_test_path(path)
        return not Path(test_path).exists()


class HighPressureHeuristic(Heuristic):
    """Check metabolic pressure periodically."""

    def __init__(self, metabolism: MetabolicEngine):
        self.metabolism = metabolism

    def check_periodic(self) -> str | None:
        if self.metabolism.pressure > 0.8:
            return f"Pressure at {self.metabolism.pressure:.0%}. Tithe?"
        return None
```

### Phase 3: CLI Handler (~80 LOC)
```python
# protocols/cli/handlers/soul.py (extend)

@expose(help="Watch mode - K-gent as ambient presence")
async def watch(self, ctx: CommandContext) -> None:
    """Start K-gent watch mode."""
    soul = await self._get_soul(ctx)
    heuristics = [
        SoulFileHeuristic(),
        UntestedCodeHeuristic(),
        HighPressureHeuristic(ctx.get_service("metabolism")),
        LongSessionHeuristic(),
    ]

    handler = KgentFileHandler(soul, heuristics)
    observer = Observer()
    observer.schedule(handler, str(ctx.project_root), recursive=True)
    observer.start()

    ctx.output("[K-gent] Watching... (Ctrl+C to stop)")

    try:
        while True:
            await asyncio.sleep(60)
            # Periodic checks
            for h in heuristics:
                if hasattr(h, "check_periodic"):
                    msg = h.check_periodic()
                    if msg:
                        ctx.output(f"[K-gent] {msg}")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

### Phase 4: Configuration (~50 LOC)
```yaml
# ~/.kgents/watch.yaml
heuristics:
  soul_files: true
  untested_code: true
  high_pressure: true
  long_session: true
  session_limit_hours: 3

notifications:
  sound: false
  desktop: false  # Future: system notifications

ignored_patterns:
  - "*.pyc"
  - "__pycache__"
  - ".git"
```

---

## Heuristics Catalog

| Heuristic | Trigger | Message Template |
|-----------|---------|------------------|
| Soul files | Edit to `persona.py`, etc. | "Soul file touched. Validate?" |
| Untested code | New `.py` without test | "Untested code is unverified belief" |
| High pressure | Metabolism > 80% | "System runs hot. Tithe?" |
| Long session | > 3 hours coding | "Even the river rests. Stretch?" |
| Principle violation | Edit to `spec/principles.md` | "Principle changed. Check drift?" |
| Large file | File > 500 lines | "This file grows heavy. Split?" |

---

## File Structure

```
agents/k/
├── watcher.py        # File watcher integration
├── heuristics.py     # Heuristic definitions
└── watch_config.py   # Configuration loading

protocols/cli/handlers/
└── soul.py           # Extended with watch command
```

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| Startup time | < 1 second |
| CPU overhead | < 1% idle |
| Notification relevance | > 80% useful |
| Kent's approval | "This feels like pair programming" |

---

## Testing Strategy

| Test Type | Coverage |
|-----------|----------|
| Unit | Individual heuristics |
| Integration | Watcher + handler flow |
| Smoke | `kgents soul watch` starts |
| Manual | Kent uses for 1 hour |

---

## Dependencies

- `watchdog` — Filesystem monitoring (add to deps)
- Existing K-gent soul system
- Existing metabolism system

---

## Cross-References

- **Strategic Recommendations**: `plans/ideas/strategic-recommendations-2025-12-13.md`
- **K-gent Plan**: `plans/agents/k-gent.md`
- **Metabolism**: `plans/void/entropy.md`
- **Watchdog**: https://github.com/gorakhargosh/watchdog

---

*"The best pair programmer never sleeps, never judges, and always remembers your principles."*
