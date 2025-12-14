# Memory Dashboard Integration: Four Pillars in I-gent

> *"The dashboard should reveal memory's living architecture."*

## Mission

Integrate the Four Pillars memory visualization (`MemoryMapScreen`) into the kgents dashboard, ensuring it works both in demo mode and with real data. Then robustify the feature and explore deeper integration opportunities.

## Current State: What's Built

### Four Pillars Implementation (Phase 2 Complete)

| Component | File | Tests | Status |
|-----------|------|-------|--------|
| MemoryCrystal | `agents/m/crystal.py` | 34 | ✅ |
| PheromoneField | `agents/m/stigmergy.py` | 35 | ✅ |
| LanguageGame | `agents/m/games.py` | 46 | ✅ |
| ActiveInferenceAgent | `agents/m/inference.py` | 47 | ✅ |
| MemoryPolynomial | `agents/m/polynomial.py` | 26 | ✅ |
| **Total** | | **188** | ✅ |

### Visualization Built

| Component | File | Status |
|-----------|------|--------|
| MemoryMapScreen | `agents/i/screens/memory_map.py` | ✅ Created |
| MemoryCrystalWidget | `agents/i/screens/memory_map.py` | ✅ Created |
| PheromoneFieldWidget | `agents/i/screens/memory_map.py` | ✅ Created |
| LanguageGameWidget | `agents/i/screens/memory_map.py` | ✅ Created |

### AGENTESE Paths Wired

| Path | Purpose |
|------|---------|
| `self.memory.store` | Store to MemoryCrystal |
| `self.memory.retrieve` | Retrieve by resonance |
| `self.memory.compress` | Holographic compression |
| `self.memory.promote` | Increase resolution |
| `self.memory.demote` | Graceful forgetting |
| `self.memory.deposit` | Stigmergic trace deposit |
| `self.memory.sense` | Sense pheromone gradients |
| `self.memory.play` | Language game moves |
| `self.memory.evaluate` | Active inference evaluation |
| `self.memory.inference_consolidate` | Free energy-guided consolidation |

---

## Task 1: Dashboard Integration (Priority: Critical)

### 1.1 Wire MemoryMapScreen into Dashboard Navigation

The dashboard currently has LOD levels (Orbit → Surface → Internal). Add Memory Map as a new view accessible from the dashboard.

**Files to modify**:
- `impl/claude/agents/i/screens/dashboard.py` - Add navigation binding
- `impl/claude/qa/demo_glass_terminal.py` - Add demo mode support

**Implementation**:

```python
# In dashboard.py, add binding
BINDINGS = [
    ...
    Binding("m", "show_memory_map", "Memory Map", show=True),
]

async def action_show_memory_map(self) -> None:
    """Show the Four Pillars memory visualization."""
    from .memory_map import MemoryMapScreen

    # Get or create Four Pillars instances from data provider
    provider = self._get_data_provider()

    screen = MemoryMapScreen(
        crystal=provider.memory_crystal,
        field=provider.pheromone_field,
        inference=provider.inference_agent,
        games=provider.language_games,
        demo_mode=self._demo_mode,
    )
    await self.app.push_screen(screen)
```

### 1.2 Create Dashboard Data Provider for Four Pillars

**File**: `impl/claude/agents/i/data/memory_provider.py` (create)

```python
"""Data provider for Four Pillars memory visualization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agents.m import (
    ActiveInferenceAgent,
    Belief,
    LanguageGame,
    MemoryCrystal,
    PheromoneField,
    create_dialectical_game,
    create_recall_game,
)


@dataclass
class MemoryDataProvider:
    """
    Provides Four Pillars data to I-gent dashboard.

    In demo mode, creates synthetic data.
    In real mode, connects to live agent memory.
    """

    demo_mode: bool = False

    # Four Pillars instances
    memory_crystal: MemoryCrystal[Any] | None = None
    pheromone_field: PheromoneField | None = None
    inference_agent: ActiveInferenceAgent[Any] | None = None
    language_games: dict[str, LanguageGame[Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.demo_mode:
            self._setup_demo_data()

    def _setup_demo_data(self) -> None:
        """Create demo data for visualization."""
        # Crystal with varied resolutions
        self.memory_crystal = MemoryCrystal[str](dimension=64)

        # Hot patterns (frequently accessed)
        self.memory_crystal.store(
            "python_async",
            "Python async/await patterns for concurrent programming",
            [0.9] * 64
        )
        self.memory_crystal.store(
            "rust_ownership",
            "Rust ownership model and borrowing rules",
            [0.85] * 64
        )

        # Warm patterns
        self.memory_crystal.store(
            "typescript_generics",
            "TypeScript generic type patterns",
            [0.6] * 64
        )

        # Cold patterns (candidates for demotion)
        self.memory_crystal.store(
            "old_api_notes",
            "Notes about deprecated API v1",
            [0.2] * 64
        )
        self.memory_crystal.demote("old_api_notes", factor=0.3)

        # Pheromone field with traces
        self.pheromone_field = PheromoneField(decay_rate=0.1)

        # Inference agent
        belief = Belief(
            distribution={
                "python": 0.35,
                "rust": 0.25,
                "typescript": 0.20,
                "other": 0.20,
            },
            precision=1.2,
        )
        self.inference_agent = ActiveInferenceAgent(belief)

        # Language games
        self.language_games = {
            "recall": create_recall_game(),
            "dialectical": create_dialectical_game(),
        }

    async def deposit_demo_traces(self) -> None:
        """Deposit some demo pheromone traces."""
        if self.pheromone_field is None:
            return

        await self.pheromone_field.deposit("python", 3.0, "agent_a")
        await self.pheromone_field.deposit("python", 2.0, "agent_b")
        await self.pheromone_field.deposit("rust", 2.5, "agent_a")
        await self.pheromone_field.deposit("typescript", 1.0, "agent_c")


def create_memory_provider(demo_mode: bool = False) -> MemoryDataProvider:
    """Factory function for memory data provider."""
    return MemoryDataProvider(demo_mode=demo_mode)
```

### 1.3 Add Tests for Dashboard Integration

**File**: `impl/claude/agents/i/screens/_tests/test_memory_map.py` (create)

```python
"""Tests for MemoryMapScreen integration."""

import pytest
from agents.m import (
    MemoryCrystal,
    PheromoneField,
    ActiveInferenceAgent,
    Belief,
    create_recall_game,
)
from agents.i.screens.memory_map import (
    MemoryMapScreen,
    MemoryCrystalWidget,
    PheromoneFieldWidget,
    LanguageGameWidget,
)


class TestMemoryMapScreen:
    """Tests for MemoryMapScreen."""

    @pytest.fixture
    def demo_screen(self) -> MemoryMapScreen:
        """Create a demo mode screen."""
        return MemoryMapScreen(demo_mode=True)

    @pytest.fixture
    def real_screen(self) -> MemoryMapScreen:
        """Create a screen with real data."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("test", "Test content", [0.5] * 64)

        field = PheromoneField()

        belief = Belief(distribution={"test": 1.0})
        inference: ActiveInferenceAgent[str] = ActiveInferenceAgent(belief)

        games = {"recall": create_recall_game()}

        return MemoryMapScreen(
            crystal=crystal,
            field=field,
            inference=inference,
            games=games,
        )

    def test_demo_mode_creates_data(self, demo_screen: MemoryMapScreen) -> None:
        """Demo mode should create synthetic data."""
        assert demo_screen._crystal is not None
        assert demo_screen._field is not None
        assert demo_screen._inference is not None

    def test_real_mode_uses_provided_data(self, real_screen: MemoryMapScreen) -> None:
        """Real mode should use provided data."""
        assert real_screen._crystal is not None
        assert len(real_screen._crystal.concepts) == 1

    def test_render_crystal_panel(self, demo_screen: MemoryMapScreen) -> None:
        """Crystal panel should render."""
        content = demo_screen._render_crystal(demo_screen.crystal_data)
        assert "Resolution Distribution" in content or "No crystal" in content

    @pytest.mark.asyncio
    async def test_refresh_data(self, demo_screen: MemoryMapScreen) -> None:
        """Refresh should update reactive data."""
        await demo_screen._refresh_data()
        assert demo_screen.crystal_data is not None


class TestMemoryCrystalWidget:
    """Tests for MemoryCrystalWidget."""

    def test_compose_view_no_crystal(self) -> None:
        """Widget handles missing crystal."""
        widget = MemoryCrystalWidget(crystal=None)
        assert widget.compose_view() == "No crystal"

    def test_compose_view_with_crystal(self) -> None:
        """Widget renders crystal stats."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("a", "A", [0.5] * 64)

        widget = MemoryCrystalWidget(crystal=crystal)
        view = widget.compose_view()

        assert "Memory Crystal" in view
        assert "Concepts:" in view


class TestPheromoneFieldWidget:
    """Tests for PheromoneFieldWidget."""

    @pytest.mark.asyncio
    async def test_compose_view_no_field(self) -> None:
        """Widget handles missing field."""
        widget = PheromoneFieldWidget(field=None)
        view = await widget.compose_view()
        assert view == "No field"


class TestLanguageGameWidget:
    """Tests for LanguageGameWidget."""

    def test_compose_view_no_game(self) -> None:
        """Widget handles missing game."""
        widget = LanguageGameWidget(game=None, current_position="")
        assert widget.compose_view() == "No game"

    def test_compose_view_with_game(self) -> None:
        """Widget shows available moves."""
        game = create_recall_game()
        widget = LanguageGameWidget(game=game, current_position="test")
        view = widget.compose_view()

        assert "recall" in view.lower() or "Game" in view
        assert "Available Moves" in view
```

---

## Task 2: Demo Mode Polish (Priority: High)

### 2.1 Enhance Demo Data Generation

Make demo data more representative and interesting:

```python
async def _setup_rich_demo_data(self) -> None:
    """Create rich demo data showing all Four Pillars features."""

    # 1. Crystal with clear hot/warm/cold distribution
    concepts = [
        ("hot_concept_1", "Frequently accessed pattern", 1.0, True),
        ("hot_concept_2", "Another hot pattern", 0.95, True),
        ("warm_concept", "Moderate access pattern", 0.6, False),
        ("cool_concept", "Infrequently accessed", 0.3, False),
        ("cold_concept", "Candidate for forgetting", 0.1, False),
    ]

    for cid, content, resolution, is_hot in concepts:
        self.memory_crystal.store(cid, content, [resolution] * 64)
        if resolution < 0.5:
            self.memory_crystal.demote(cid, factor=resolution)

    # 2. Pheromone traces showing emergent patterns
    traces = [
        ("python", 5.0, "coder_agent"),
        ("python", 3.0, "reviewer_agent"),
        ("python", 2.0, "test_agent"),  # Clear gradient toward python
        ("rust", 4.0, "coder_agent"),
        ("rust", 1.0, "test_agent"),
        ("docs", 1.0, "writer_agent"),
    ]

    for concept, intensity, depositor in traces:
        await self.pheromone_field.deposit(concept, intensity, depositor)

    # 3. Inference beliefs reflecting usage patterns
    # Should align with pheromone gradients
    self.inference_agent.belief.distribution = {
        "python": 0.45,
        "rust": 0.30,
        "docs": 0.15,
        "other": 0.10,
    }
```

### 2.2 Add Real-Time Updates in Demo

```python
async def _simulate_activity(self) -> None:
    """Simulate memory activity for demo mode."""
    import asyncio
    import random

    while True:
        await asyncio.sleep(2.0)  # Update every 2 seconds

        # Randomly deposit a trace
        concepts = ["python", "rust", "docs", "test"]
        concept = random.choice(concepts)
        intensity = random.uniform(0.5, 2.0)

        await self._field.deposit(concept, intensity, "demo_agent")

        # Occasionally promote/demote
        if random.random() < 0.3:
            concepts = list(self._crystal.concepts)
            if concepts:
                cid = random.choice(concepts)
                if random.random() < 0.5:
                    self._crystal.promote(cid, factor=1.1)
                else:
                    self._crystal.demote(cid, factor=0.9)

        # Refresh display
        await self._refresh_data()
```

---

## Task 3: Robustification (Priority: High)

### 3.1 Error Handling

Add defensive error handling throughout:

```python
def _render_crystal(self, data: dict[str, Any]) -> str:
    """Render crystal data with error handling."""
    try:
        if not data:
            return "[#8b7ba5]No crystal data available[/]"

        # Validate data structure
        required_keys = ["dimension", "concept_count", "resolutions"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            return f"[#c97b84]Missing data: {missing}[/]"

        # ... render logic ...

    except Exception as e:
        return f"[#c97b84]Error rendering crystal: {e}[/]"
```

### 3.2 Type Safety

Ensure all components have proper type annotations:

```python
from typing import TypedDict

class CrystalStats(TypedDict):
    dimension: int
    concept_count: int
    hot_count: int
    avg_resolution: float
    min_resolution: float
    max_resolution: float

class FieldStats(TypedDict):
    concept_count: int
    trace_count: int
    deposit_count: int
    evaporation_count: int
    avg_intensity: float
    decay_rate: float
```

### 3.3 Performance Optimization

For large memory systems:

```python
async def _refresh_data(self, max_concepts: int = 50) -> None:
    """Refresh with pagination for large datasets."""

    # Limit crystal data
    if self._crystal:
        all_concepts = list(self._crystal.concepts)
        top_concepts = sorted(
            all_concepts,
            key=lambda c: self._crystal.resolution_levels.get(c, 0),
            reverse=True
        )[:max_concepts]

        self.crystal_data = {
            # ... only include top_concepts data ...
            "truncated": len(all_concepts) > max_concepts,
            "total_count": len(all_concepts),
        }
```

---

## Task 4: Deeper Integration (Priority: Medium)

### 4.1 MRI Screen Enhancement

Wire Four Pillars into existing MRI screen's Memory Crystals panel:

**File**: `impl/claude/agents/i/screens/mri.py`

Replace the placeholder with actual MemoryCrystalWidget:

```python
# Panel 4: Memory Crystals - Replace placeholder
with Container(classes="panel"):
    yield Static("[Memory Crystals]", classes="panel-title")
    yield Static("")

    if self._memory_provider and self._memory_provider.memory_crystal:
        crystal = self._memory_provider.memory_crystal
        stats = crystal.stats()
        yield Static(f"[#b3a89a]Concepts:[/] {stats['concept_count']}")
        yield Static(f"[#b3a89a]Hot:[/] {stats['hot_count']}")
        yield Static(f"[#b3a89a]Avg Resolution:[/] {stats['avg_resolution']:.2f}")
        yield Static("")

        # Show top 5 by resolution
        for cid, res in list(crystal.resolution_levels.items())[:5]:
            bar = "█" * int(res * 10)
            yield Static(f"  {cid[:12]:<12} [{bar:<10}] {res:.2f}")
    else:
        yield Static("[#8b7ba5]No memory crystal connected[/]")
```

### 4.2 Cockpit Integration

Add memory health indicator to CockpitScreen:

```python
# In cockpit.py, add to status bar
def _compose_memory_health(self) -> str:
    """Compose memory health indicator."""
    if not self._memory_provider:
        return "MEM: --"

    crystal = self._memory_provider.memory_crystal
    if not crystal:
        return "MEM: --"

    stats = crystal.stats()
    avg_res = stats["avg_resolution"]

    # Color based on health
    if avg_res >= 0.7:
        color = "#1dd1a1"  # Healthy
    elif avg_res >= 0.4:
        color = "#feca57"  # Warning
    else:
        color = "#ff6b6b"  # Critical

    return f"MEM: [{color}]{avg_res:.0%}[/]"
```

### 4.3 Ghost Cache Integration

Persist Four Pillars state to ghost cache for cross-session memory:

**File**: `impl/claude/infra/ghost/collectors.py` (extend)

```python
from agents.m import MemoryCrystal, PheromoneField

async def collect_four_pillars_state(
    crystal: MemoryCrystal | None,
    field: PheromoneField | None,
) -> dict:
    """Collect Four Pillars state for ghost cache."""
    result = {}

    if crystal:
        result["crystal"] = {
            "dimension": crystal.dimension,
            "concepts": {
                cid: {
                    "resolution": crystal.resolution_levels.get(cid, 1.0),
                    "is_hot": cid in crystal.hot_patterns,
                }
                for cid in list(crystal.concepts)[:100]
            },
            "stats": crystal.stats(),
        }

    if field:
        gradients = await field.sense()
        result["pheromones"] = {
            "decay_rate": field.decay_rate,
            "gradients": [
                {
                    "concept": g.concept,
                    "intensity": g.total_intensity,
                    "traces": g.trace_count,
                }
                for g in gradients[:50]
            ],
            "stats": field.stats(),
        }

    return result
```

---

## Task 5: Update Plans (Priority: Medium)

### 5.1 Create Memory Integration Plan

**File**: `plans/devex/memory-dashboard.md` (create)

Document:
- Four Pillars visualization architecture
- Dashboard integration patterns
- Demo mode design decisions
- Future enhancements

### 5.2 Update Forest Status

**File**: `plans/_status.md` (update)

Add Four Pillars Phase 2 completion:
- 188 tests passing
- AGENTESE paths wired
- I-gent visualization created
- PolyAgent integration complete

### 5.3 Capture Learnings

**File**: `plans/self/memory.md` (update)

Key learnings to capture:
1. Holographic compression is architecturally novel
2. Stigmergy enables multi-agent coordination without shared state
3. Language games provide a Wittgensteinian API for memory access
4. Active Inference completes the free energy picture
5. Polynomial functors unify memory and agents

---

## Verification Commands

```bash
# Run all Four Pillars tests
cd impl/claude
uv run pytest agents/m/_tests/ -v --tb=short

# Run I-gent tests
uv run pytest agents/i/screens/_tests/test_memory_map.py -v

# Type check
uv run mypy agents/m/inference.py agents/m/polynomial.py agents/i/screens/memory_map.py --ignore-missing-imports

# Demo the memory map screen
uv run python -c "
from agents.i.screens.memory_map import MemoryMapScreen
screen = MemoryMapScreen(demo_mode=True)
print('MemoryMapScreen created in demo mode')
print(f'Crystal: {screen._crystal is not None}')
print(f'Field: {screen._field is not None}')
print(f'Inference: {screen._inference is not None}')
print(f'Games: {list(screen._games.keys())}')
"

# Test dashboard integration (if dashboard command exists)
# uv run kgents dashboard --demo
```

---

## Exit Criteria

| Task | Criteria |
|------|----------|
| Dashboard Integration | Memory Map accessible via 'm' key from dashboard |
| Demo Mode | Rich, representative demo data with optional simulation |
| Robustification | All error paths handled, type-safe, performant |
| MRI Integration | Memory Crystals panel shows real data |
| Cockpit Integration | Memory health indicator in status bar |
| Ghost Cache | Four Pillars state persisted across sessions |
| Plans Updated | Documentation reflects current state |
| Tests | All integration tests passing |

---

## Key Files

| File | Purpose |
|------|---------|
| `agents/i/screens/memory_map.py` | Main visualization screen |
| `agents/i/screens/dashboard.py` | Dashboard navigation |
| `agents/i/data/memory_provider.py` | Data provider (to create) |
| `agents/i/screens/_tests/test_memory_map.py` | Integration tests (to create) |
| `agents/m/inference.py` | Active Inference |
| `agents/m/polynomial.py` | Memory Polynomial |
| `protocols/agentese/contexts/self_.py` | AGENTESE paths |
| `infra/ghost/collectors.py` | Ghost cache |

---

## Architectural Insight

The Four Pillars represent a fundamental rethinking of agent memory:

```
Traditional: Memory = Database (store/retrieve)
Four Pillars: Memory = Autopoietic System

     ┌─────────────┐
     │   Crystal   │  ← Holographic substrate
     │  (storage)  │
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │ Pheromones  │  ← Stigmergic coordination
     │  (traces)   │
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │   Games     │  ← Wittgensteinian access
     │  (grammar)  │
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │  Inference  │  ← Free energy retention
     │  (budget)   │
     └─────────────┘
```

The dashboard visualization makes this architecture visible, helping developers understand how memory actually works in kgents agents.

---

*"To see is to understand. The dashboard reveals memory's living architecture."*
