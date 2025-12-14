---
path: devex/hotdata-infrastructure
status: active
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Initial creation. Implements AD-004 (Pre-Computed Richness).
  Demo kgents ARE kgents. LLM-once is cheap. Hotload everything.
---

# HotData Infrastructure: Rich Demo Data System

> *"The first spark costs nothing. The sustained fire requires fuel."*

**AGENTESE Context**: `void.fixture.*`, `self.demo.*`
**Status**: Proposed
**Principles**: AD-004 (Pre-Computed Richness), Generative, Accursed Share
**Cross-refs**: `spec/principles.md` §AD-004, `impl/claude/qa/`, `impl/claude/agents/i/data/`

AGENTESE pointer: keep handles/law guards in sync with `spec/protocols/agentese.md`; update this plan when canonical flow shifts.

---

## Core Insight

Any given LLM task done once is definitionally cheap. Demo systems that use hardcoded strings ("A placeholder summary") miss the soul. **Pre-generate rich data once, hotload forever**.

The key insight: **demo kgents ARE kgents**. There is no distinction between "demo" and "real" - demos should use the same data paths, the same richness, the same soul.

---

## The Three Truths

1. **Demo kgents ARE kgents**: No distinction between "demo" and "real"
2. **LLM-once is cheap**: One LLM call for fixture generation is negligible
3. **Hotload everything**: Pre-computed outputs swap at runtime for velocity

---

## Implementation Phases

### Phase 1: HotData Core (Foundation)

**Goal**: Create the HotData protocol for loading/refreshing pre-computed data.

**Files**:
```
impl/claude/shared/hotdata.py       # Core HotData class
impl/claude/shared/hotdata/_tests/  # Tests for hotdata
```

**Key Types**:

```python
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Generic, TypeVar, Callable, Awaitable, Protocol

T = TypeVar("T")

class Serializable(Protocol):
    """Protocol for types that can be serialized to/from JSON."""
    def to_json(self) -> str: ...
    @classmethod
    def from_json(cls, data: str) -> "Serializable": ...


@dataclass
class HotData(Generic[T]):
    """
    Hotloadable pre-computed data with optional refresh.

    Philosophy: LLM-once is cheap. Pre-compute rich data, hotload forever.
    Demo kgents ARE kgents.
    """
    path: Path
    schema: type[T]
    ttl: timedelta | None = None  # None = forever valid

    def exists(self) -> bool:
        """Check if pre-computed data exists."""
        return self.path.exists()

    def load(self) -> T:
        """Load from pre-computed file. Raises if not exists."""
        return self.schema.from_json(self.path.read_text())

    def load_or_default(self, default: T) -> T:
        """Load or return default."""
        if self.exists():
            return self.load()
        return default

    async def refresh(
        self,
        generator: Callable[[], Awaitable[T]],
        force: bool = False
    ) -> T:
        """
        Regenerate via LLM if stale or missing.

        The generator is the LLM call. It runs once to produce rich data.
        """
        if not force and self._is_fresh():
            return self.load()
        result = await generator()
        self._save(result)
        return result

    def _is_fresh(self) -> bool:
        """Check if data is within TTL."""
        if not self.exists():
            return False
        if self.ttl is None:
            return True
        # Check file mtime
        import time
        mtime = self.path.stat().st_mtime
        age = time.time() - mtime
        return age < self.ttl.total_seconds()

    def _save(self, data: T) -> None:
        """Save to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(data.to_json())


class HotDataRegistry:
    """
    Registry of all hotloadable fixtures.

    Allows bulk refresh, validation, and CLI integration.
    """

    def __init__(self) -> None:
        self._fixtures: dict[str, HotData] = {}

    def register(self, name: str, hotdata: HotData) -> None:
        """Register a fixture by name."""
        self._fixtures[name] = hotdata

    def get(self, name: str) -> HotData | None:
        """Get a fixture by name."""
        return self._fixtures.get(name)

    def list_stale(self) -> list[str]:
        """List all stale fixtures that need refresh."""
        return [
            name for name, hd in self._fixtures.items()
            if not hd._is_fresh()
        ]

    async def refresh_all_stale(self, generators: dict[str, Callable]) -> list[str]:
        """Refresh all stale fixtures. Returns list of refreshed names."""
        refreshed = []
        for name in self.list_stale():
            if name in generators:
                await self._fixtures[name].refresh(generators[name])
                refreshed.append(name)
        return refreshed
```

**Exit Criteria**:
- HotData class loads/saves JSON
- TTL-based freshness checking works
- Registry tracks multiple fixtures

---

### Phase 2: Fixture Generation Commands

**Goal**: CLI commands to generate and manage fixtures.

**Files**:
```
impl/claude/protocols/cli/handlers/fixture.py
impl/claude/fixtures/                         # Fixture storage directory
impl/claude/fixtures/README.md                # Fixture documentation
```

**Commands**:

```bash
# List all fixtures and their freshness status
kg fixture list

# Refresh a specific fixture
kg fixture refresh agent_snapshots/soul_deliberating

# Refresh all stale fixtures
kg fixture refresh --all

# Generate a new fixture from an AGENTESE path
kg fixture generate void.compose.sip --output fixtures/composed_agent.json

# Validate all fixtures against schemas
kg fixture validate
```

**Exit Criteria**:
- `kg fixture list` shows all registered fixtures
- `kg fixture refresh` regenerates via LLM
- Fixtures stored in `impl/claude/fixtures/`

---

### Phase 3: Demo System Integration

**Goal**: Migrate existing demo systems to use HotData.

**Files to Migrate**:
```
impl/claude/agents/i/data/state.py           # create_demo_flux_state()
impl/claude/agents/i/data/garden.py          # create_demo_gardens(), create_demo_polynomial_state()
impl/claude/agents/i/screens/cockpit.py      # create_demo_snapshot()
impl/claude/qa/demo_glass_terminal.py        # All demo functions
impl/claude/agents/i/demo_all_screens.py     # Demo application
```

**Migration Pattern**:

Before:
```python
def create_demo_snapshot() -> AgentSnapshot:
    return AgentSnapshot(
        id="demo-agent",
        name="Demo Agent",
        phase=Phase.ACTIVE,
        summary="A demonstration agent for the cockpit view.",
    )
```

After:
```python
from shared.hotdata import HotData, hotdata_registry

DEMO_SNAPSHOT_HOTDATA = HotData(
    path=FIXTURES_DIR / "agent_snapshots" / "cockpit_demo.json",
    schema=AgentSnapshot,
)
hotdata_registry.register("demo_snapshot", DEMO_SNAPSHOT_HOTDATA)

def create_demo_snapshot() -> AgentSnapshot:
    """Load demo snapshot from hotdata, or generate if missing."""
    if DEMO_SNAPSHOT_HOTDATA.exists():
        return DEMO_SNAPSHOT_HOTDATA.load()
    # Fallback to inline for first-run
    return AgentSnapshot(
        id="demo-agent",
        name="Demo Agent",
        phase=Phase.ACTIVE,
        summary="A demonstration agent for the cockpit view.",
    )
```

**Exit Criteria**:
- All demo functions use HotData
- Demos work with pre-computed fixtures
- Fallback to inline for missing fixtures

---

### Phase 4: LLM Fixture Generators

**Goal**: Create generator functions that use real agents to produce rich demo data.

**Files**:
```
impl/claude/fixtures/generators/__init__.py
impl/claude/fixtures/generators/agent_snapshots.py
impl/claude/fixtures/generators/garden_states.py
impl/claude/fixtures/generators/polynomial_states.py
impl/claude/fixtures/generators/thoughts_streams.py
```

**Generator Pattern**:

```python
async def generate_rich_agent_snapshot(
    agent_archetype: str = "deliberator",
    entropy: float = 0.8,
) -> AgentSnapshot:
    """
    Generate a rich agent snapshot using actual kgents.

    This is an LLM call - expensive per-call, but cheap once.
    The output is serialized and hotloaded forever.
    """
    from protocols.agentese import Logos
    from agents.k import KGent

    logos = Logos()

    # Use the Accursed Share to generate variation
    raw_output = await logos.invoke(
        f"void.compose.sip",
        context={
            "archetype": agent_archetype,
            "entropy": entropy,
            "output_schema": "AgentSnapshot",
        }
    )

    # Or use K-gent directly for personality-rich data
    kgent = KGent()
    response = await kgent.invoke({
        "request": f"Describe yourself as a {agent_archetype} agent",
        "format": "AgentSnapshot",
    })

    return AgentSnapshot(
        id=f"{agent_archetype}-{random_id()}",
        name=response.get("name", agent_archetype.title()),
        phase=Phase.ACTIVE,
        activity=random.uniform(0.5, 0.9),
        summary=response.get("summary", "..."),
        connections=response.get("connections", {}),
    )


# Registry of generators for bulk refresh
GENERATORS = {
    "demo_snapshot": lambda: generate_rich_agent_snapshot("deliberator"),
    "soul_in_crisis": lambda: generate_rich_agent_snapshot("crisis_manager", entropy=0.95),
    "garden_converging": lambda: generate_garden_state("converging"),
    "polynomial_transitioning": lambda: generate_polynomial_state("DELIBERATING"),
}
```

**Exit Criteria**:
- Generator functions produce rich, LLM-generated data
- Generators are registered for bulk refresh
- Output matches schema requirements

---

### Phase 5: Adaptive Hotloading

**Goal**: Runtime hot-swapping of fixtures for development velocity.

**Files**:
```
impl/claude/shared/hotdata/watcher.py    # File watcher for hot reload
impl/claude/shared/hotdata/dev_mode.py   # Development mode utilities
```

**Features**:

```python
class HotDataWatcher:
    """
    Watch fixture directory for changes and hot-reload.

    Philosophy: Everything can be hotloaded.
    """

    def __init__(self, fixtures_dir: Path) -> None:
        self.fixtures_dir = fixtures_dir
        self._watchers: dict[str, Callable] = {}

    async def watch(self) -> AsyncIterator[str]:
        """Watch for fixture changes, yield changed fixture names."""
        # Use watchfiles or similar
        async for changes in awatch(self.fixtures_dir):
            for change_type, path in changes:
                if path.suffix == ".json":
                    yield path.stem

    def on_change(self, name: str, callback: Callable[[T], None]) -> None:
        """Register callback for when a fixture changes."""
        self._watchers[name] = callback


# In demo apps:
if DEV_MODE:
    watcher = HotDataWatcher(FIXTURES_DIR)

    @watcher.on_change("demo_snapshot")
    def reload_demo_snapshot(new_data: AgentSnapshot):
        app.demo_snapshot = new_data
        app.refresh()  # Hot-reload the screen
```

**Exit Criteria**:
- File watcher detects fixture changes
- Demos hot-reload when fixtures change
- Zero restart required for fixture iteration

---

### Phase 6: Test Fixture Integration

**Goal**: Test fixtures use the same HotData infrastructure.

**Files**:
```
impl/claude/conftest.py                 # Update with HotData fixtures
impl/claude/fixtures/test/              # Test-specific fixtures
```

**Integration**:

```python
# In conftest.py

from shared.hotdata import HotData

TEST_AGENT_SNAPSHOT = HotData(
    path=FIXTURES_DIR / "test" / "agent_snapshot.json",
    schema=AgentSnapshot,
)

@pytest.fixture
def rich_agent_snapshot() -> AgentSnapshot:
    """
    Pre-computed rich agent snapshot for tests.

    Not synthetic stubs - actual LLM-generated data.
    """
    return TEST_AGENT_SNAPSHOT.load_or_default(
        AgentSnapshot(id="fallback", name="Fallback", phase=Phase.DORMANT)
    )
```

**Exit Criteria**:
- Test fixtures use HotData
- Tests run with rich pre-computed data
- Fallback for missing fixtures

---

## Directory Structure

After implementation:

```
impl/claude/
├── shared/
│   └── hotdata/
│       ├── __init__.py        # HotData, HotDataRegistry
│       ├── watcher.py         # HotDataWatcher for dev mode
│       └── _tests/            # HotData tests
├── fixtures/
│   ├── README.md              # Fixture documentation
│   ├── agent_snapshots/       # AgentSnapshot fixtures
│   │   ├── cockpit_demo.json
│   │   ├── soul_deliberating.json
│   │   └── soul_in_crisis.json
│   ├── garden_states/         # GardenSnapshot fixtures
│   │   ├── main_converging.json
│   │   └── experiment_diverging.json
│   ├── polynomial_states/     # PolynomialState fixtures
│   ├── thoughts_streams/      # ThoughtsStream fixtures
│   ├── generators/            # Generator functions
│   │   ├── __init__.py
│   │   ├── agent_snapshots.py
│   │   └── garden_states.py
│   └── test/                  # Test-specific fixtures
├── protocols/cli/handlers/
│   └── fixture.py             # kg fixture commands
└── qa/
    └── demo_glass_terminal.py # Updated to use HotData
```

---

## Cross-References

- **Spec**: `spec/principles.md` §AD-004 (Pre-Computed Richness)
- **Plan**: `plans/devex/dashboard.md` (archived - uses demo data)
- **Impl**: `impl/claude/agents/i/data/state.py` (current demo data)
- **Skill**: `plans/skills/test-patterns.md` (fixture patterns)

---

## Session Notes

Phase 0: Plan created. Ready for implementation.
