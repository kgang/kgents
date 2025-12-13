# HotData Infrastructure Realization

> *"The first spark costs nothing. The sustained fire requires fuel."*

**Plan Reference**: `plans/devex/hotdata-infrastructure.md`
**Principle**: AD-004 (Pre-Computed Richness)
**Prerequisites**: Read `spec/principles.md` §AD-004, understand demo systems in `impl/claude/agents/i/data/`

---

## Part 1: Foundation (HotData Core)

**Goal**: Implement the HotData protocol for loading and refreshing pre-computed data.

### Tasks

1. **Create `shared/hotdata/__init__.py`** with:
   - `HotData[T]` generic class with `load()`, `load_or_default()`, `refresh()`, `exists()`
   - TTL-based freshness via `_is_fresh()` checking file mtime
   - JSON serialization with schema validation
   - `HotDataRegistry` singleton for tracking fixtures

2. **Create `shared/hotdata/_tests/test_hotdata.py`** with:
   - Test loading existing fixture
   - Test TTL expiration
   - Test refresh with mock generator
   - Test registry operations (register, get, list_stale)

3. **Define the Serializable protocol**:
   - `to_json() -> str`
   - `from_json(cls, data: str) -> T`
   - Make `AgentSnapshot`, `FluxState`, etc. implement this protocol

### Exit Criteria
- `uv run pytest shared/hotdata/_tests/` passes
- Can load/save JSON fixtures with TTL checking

### Verification
```bash
cd impl/claude && uv run pytest shared/hotdata/_tests/ -v
```

---

## Part 2: CLI Integration

**Goal**: Create `kg fixture` commands for managing fixtures.

### Tasks

1. **Create `protocols/cli/handlers/fixture.py`** with handlers:
   - `cmd_fixture_list()` - Show all registered fixtures with status
   - `cmd_fixture_refresh(args)` - Refresh specific or all stale fixtures
   - `cmd_fixture_validate()` - Validate fixtures against schemas

2. **Wire to CLI** in `protocols/cli/hollow.py`:
   - Add `fixture` subcommand group
   - Route to handler functions

3. **Create fixtures directory structure**:
   ```
   impl/claude/fixtures/
   ├── README.md
   ├── agent_snapshots/
   ├── garden_states/
   ├── polynomial_states/
   └── test/
   ```

### Exit Criteria
- `kg fixture list` shows fixture registry
- `kg fixture refresh --all` regenerates stale fixtures
- Directory structure exists

### Verification
```bash
kg fixture list
kg fixture refresh --help
```

---

## Part 3: Demo Migration

**Goal**: Migrate existing demo functions to use HotData.

### Tasks

1. **Migrate `agents/i/data/state.py`**:
   - `create_demo_flux_state()` → Load from `fixtures/flux_states/demo.json`
   - Add inline fallback for missing fixture

2. **Migrate `agents/i/data/garden.py`**:
   - `create_demo_gardens()` → Load from `fixtures/garden_states/`
   - `create_demo_polynomial_state()` → Load from `fixtures/polynomial_states/`
   - `create_demo_yield_turns()` → Load from `fixtures/yield_turns/`

3. **Migrate `agents/i/screens/cockpit.py`**:
   - `create_demo_snapshot()` → Use hotdata with fallback

4. **Update demo apps**:
   - `demo_all_screens.py` - Use hotloaded data
   - `qa/demo_glass_terminal.py` - Use hotloaded data

5. **Create initial fixtures**:
   - Generate JSON files for each fixture type
   - Use existing inline data as starting point

### Exit Criteria
- All demo functions check for hotdata first
- Demos work with fixtures present
- Demos fall back gracefully when fixtures missing
- `uv run python impl/claude/agents/i/demo_all_screens.py` works

### Verification
```bash
cd impl/claude && uv run python agents/i/demo_all_screens.py
```

---

## Part 4: Rich Generator Functions

**Goal**: Create LLM-powered generators that produce rich fixture data.

### Tasks

1. **Create `fixtures/generators/__init__.py`** with:
   - Generator registry mapping fixture names to async generator functions
   - Base `generate_with_entropy(agent, entropy)` helper

2. **Create agent snapshot generators**:
   ```python
   async def generate_rich_agent_snapshot(
       archetype: str,
       entropy: float = 0.7
   ) -> AgentSnapshot:
       """Generate via K-gent or void.compose.sip"""
   ```

3. **Create garden state generators**:
   ```python
   async def generate_garden_state(
       orchestration: str  # converging, diverging, stable
   ) -> GardenSnapshot:
       """Generate garden with multiple agents in specified state"""
   ```

4. **Create thought stream generators**:
   ```python
   async def generate_thought_stream(
       context: str,  # deliberation, crisis, exploration
       count: int = 10
   ) -> list[Thought]:
       """Generate coherent thought sequence"""
   ```

5. **Wire generators to refresh command**:
   - `kg fixture refresh agent_snapshots/soul_deliberating`
   - Calls appropriate generator, serializes output

### Exit Criteria
- Generator functions produce rich, varied data
- `kg fixture refresh <name>` calls generators
- Output validates against schemas

### Verification
```bash
kg fixture refresh agent_snapshots/soul_deliberating --dry-run
```

---

## Part 5: Hot Reload for Development

**Goal**: Enable live fixture updates without restart.

### Tasks

1. **Create `shared/hotdata/watcher.py`**:
   - File watcher for fixtures directory
   - Async generator yielding changed fixture names
   - Callback registration for change events

2. **Integrate with demo apps**:
   - Check `DEV_MODE` environment variable
   - Start watcher in background
   - Hot-reload screens when fixtures change

3. **Create dev mode utilities**:
   ```python
   if os.getenv("KGENTS_DEV_MODE"):
       from shared.hotdata.watcher import HotDataWatcher
       watcher = HotDataWatcher(FIXTURES_DIR)
       watcher.start_watching()
   ```

### Exit Criteria
- Changing a fixture JSON auto-reloads in demo app
- No restart required for iteration
- Works with Textual apps

### Verification
```bash
KGENTS_DEV_MODE=1 uv run python impl/claude/agents/i/demo_all_screens.py
# In another terminal: edit fixtures/agent_snapshots/demo.json
# Watch demo app update
```

---

## Part 6: Test Fixture Integration

**Goal**: Test fixtures use the same infrastructure.

### Tasks

1. **Update `conftest.py`**:
   - Add HotData-based fixtures
   - `rich_agent_snapshot` fixture using pre-computed data
   - `rich_flux_state` fixture using pre-computed data

2. **Create test fixtures**:
   ```
   impl/claude/fixtures/test/
   ├── agent_snapshot_simple.json
   ├── agent_snapshot_complex.json
   ├── flux_state_multi_agent.json
   └── garden_converging.json
   ```

3. **Verify tests use rich data**:
   - Update tests that currently use synthetic data
   - Ensure fallback for CI where fixtures may not exist

### Exit Criteria
- Tests can use pre-computed fixtures
- CI passes (fallback for missing fixtures)
- Rich data improves test quality

### Verification
```bash
cd impl/claude && uv run pytest -v -k "demo or snapshot"
```

---

## Integration Checklist

After all parts complete:

- [ ] `HotData` class in `shared/hotdata/`
- [ ] `HotDataRegistry` tracks all fixtures
- [ ] `kg fixture list` shows status
- [ ] `kg fixture refresh` regenerates via LLM
- [ ] All demo functions use hotdata
- [ ] Generator functions produce rich data
- [ ] File watcher enables hot reload
- [ ] Test fixtures use same infrastructure
- [ ] All tests pass

---

## The Three Truths (Remind Yourself)

1. **Demo kgents ARE kgents**: No artificial distinction
2. **LLM-once is cheap**: Generate rich data once, use forever
3. **Hotload everything**: Runtime swapping for velocity

---

## Command to Start

```bash
# Read the principle first
cat spec/principles.md | grep -A 50 "AD-004"

# Then start with Part 1
cd impl/claude
mkdir -p shared/hotdata/_tests
```

---

*Execute /hydrate before each session to maintain context.*
