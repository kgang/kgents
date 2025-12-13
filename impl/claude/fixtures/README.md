# HotData Fixtures

> *"The first spark costs nothing. The sustained fire requires fuel."*

Pre-computed rich data for demos, tests, and development.

## Philosophy (AD-004)

**The Three Truths:**
1. **Demo kgents ARE kgents** - No distinction between "demo" and "real"
2. **LLM-once is cheap** - One LLM call for fixture generation is negligible
3. **Hotload everything** - Pre-computed outputs swap at runtime for velocity

## Directory Structure

```
fixtures/
├── agent_snapshots/     # AgentSnapshot data for visualizations
│   ├── demo.json        # Default demo snapshot
│   └── soul_*.json      # K-gent soul states
├── garden_states/       # GardenSnapshot for Observatory
│   ├── main.json        # Main garden
│   └── experiment_*.json
├── polynomial_states/   # PolynomialState for Cockpit
├── yield_turns/         # YieldTurn pending actions
├── test/                # Test-specific fixtures
└── generators/          # Generator functions (Python)
    └── __init__.py
```

## Usage

### Loading Fixtures

```python
from shared.hotdata import HotData, FIXTURES_DIR, register_hotdata

# Define a hotdata source
DEMO_SNAPSHOT = HotData(
    path=FIXTURES_DIR / "agent_snapshots" / "demo.json",
    schema=AgentSnapshot,
)

# Register for CLI management
register_hotdata("demo_snapshot", DEMO_SNAPSHOT)

# Load in your demo function
def create_demo_snapshot() -> AgentSnapshot:
    return DEMO_SNAPSHOT.load_or_default(fallback_snapshot)
```

### CLI Commands

```bash
# List all fixtures
kg fixture list

# List only stale fixtures
kg fixture list --stale

# Refresh a specific fixture
kg fixture refresh demo_snapshot

# Refresh all stale fixtures
kg fixture refresh --all

# Validate fixture schemas
kg fixture validate

# Show fixture details
kg fixture info demo_snapshot
```

### Refreshing Fixtures

To regenerate fixtures with fresh LLM-generated content:

```bash
# Dry run (see what would be refreshed)
kg fixture refresh --all --dry-run

# Force refresh (even if fresh)
kg fixture refresh demo_snapshot --force
```

## Adding New Fixtures

1. Create the JSON file in the appropriate subdirectory
2. Register it in the relevant module using `register_hotdata()`
3. (Optional) Add a generator function for LLM refresh

## Format

All fixtures are JSON files with schema validation via DictSerializable or Serializable protocols.

Example `agent_snapshot`:
```json
{
  "id": "demo-agent",
  "name": "Demo Agent",
  "phase": "ACTIVE",
  "activity": 0.7,
  "summary": "A rich, LLM-generated description...",
  "connections": {"L-gent": 0.8}
}
```
