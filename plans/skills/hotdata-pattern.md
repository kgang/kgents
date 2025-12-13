# Skill: HotData Pattern (Pre-Computed Richness)

> Use pre-computed LLM outputs for demos and tests instead of synthetic stubs.

**Difficulty**: Easy
**Prerequisites**: Understanding of JSON serialization, async generators
**Files Touched**: `shared/hotdata/`, `fixtures/`, demo files

---

## Overview

The HotData pattern implements AD-004 (Pre-Computed Richness):

| Truth | Meaning |
|-------|---------|
| Demo kgents ARE kgents | No distinction between "demo" and "real" |
| LLM-once is cheap | One generation call is negligible |
| Hotload everything | Runtime swapping for velocity |

---

## Step-by-Step: Add a New Fixture

### Step 1: Define the Schema

Ensure your data type is serializable:

```python
# In your data module
from dataclasses import dataclass, asdict
import json

@dataclass
class MyData:
    id: str
    value: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data: str) -> "MyData":
        return cls(**json.loads(data))
```

### Step 2: Register with HotData

```python
from shared.hotdata import HotData, hotdata_registry
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

MY_DATA_HOTDATA = HotData(
    path=FIXTURES_DIR / "my_data" / "default.json",
    schema=MyData,
    ttl=None,  # Never expires (or timedelta(days=7) for weekly refresh)
)

hotdata_registry.register("my_data_default", MY_DATA_HOTDATA)
```

### Step 3: Load with Fallback

```python
def get_my_data() -> MyData:
    """Load from hotdata, fallback to inline."""
    if MY_DATA_HOTDATA.exists():
        return MY_DATA_HOTDATA.load()
    # Inline fallback for first-run
    return MyData(id="default", value="placeholder")
```

### Step 4: Create Generator (Optional)

For LLM-generated fixtures:

```python
# In fixtures/generators/my_data.py

async def generate_my_data(entropy: float = 0.7) -> MyData:
    """Generate rich data via LLM."""
    from protocols.agentese import Logos

    logos = Logos()
    result = await logos.invoke(
        "void.compose.sip",
        context={"schema": "MyData", "entropy": entropy}
    )

    return MyData(
        id=result["id"],
        value=result["value"],
    )
```

### Step 5: Create Initial Fixture

```bash
# Manual creation
echo '{"id": "demo", "value": "rich content here"}' > fixtures/my_data/default.json

# Or via CLI
kg fixture refresh my_data_default
```

---

## Step-by-Step: Migrate Demo Function

### Before (Anti-pattern)

```python
def create_demo_snapshot() -> AgentSnapshot:
    return AgentSnapshot(
        id="demo",
        name="Demo Agent",
        summary="A placeholder summary",  # Synthetic stub!
    )
```

### After (Correct)

```python
from shared.hotdata import HotData, hotdata_registry

DEMO_SNAPSHOT = HotData(
    path=FIXTURES_DIR / "agent_snapshots" / "demo.json",
    schema=AgentSnapshot,
)
hotdata_registry.register("demo_snapshot", DEMO_SNAPSHOT)

def create_demo_snapshot() -> AgentSnapshot:
    """Load from hotdata with fallback."""
    if DEMO_SNAPSHOT.exists():
        return DEMO_SNAPSHOT.load()
    return AgentSnapshot(
        id="demo",
        name="Demo Agent",
        summary="A placeholder summary",
    )
```

---

## Step-by-Step: Test with HotData

### In conftest.py

```python
from shared.hotdata import HotData

RICH_SNAPSHOT = HotData(
    path=FIXTURES_DIR / "test" / "rich_snapshot.json",
    schema=AgentSnapshot,
)

@pytest.fixture
def rich_agent_snapshot() -> AgentSnapshot:
    """Pre-computed rich snapshot for tests."""
    return RICH_SNAPSHOT.load_or_default(
        AgentSnapshot(id="fallback", name="Fallback")
    )
```

### In Tests

```python
def test_snapshot_processing(rich_agent_snapshot):
    """Test uses real pre-computed data."""
    result = process_snapshot(rich_agent_snapshot)
    assert result.is_valid()
```

---

## Verification

### Check 1: Fixture exists and validates

```bash
cd impl/claude
python -c "
from shared.hotdata import hotdata_registry
for name, hd in hotdata_registry._fixtures.items():
    status = '✓' if hd.exists() else '✗'
    fresh = '(fresh)' if hd._is_fresh() else '(stale)'
    print(f'{status} {name} {fresh}')
"
```

### Check 2: Demo uses hotdata

```bash
cd impl/claude && uv run python agents/i/demo_all_screens.py
# Should load from fixtures, not inline data
```

### Check 3: CLI works

```bash
kg fixture list
kg fixture refresh --all --dry-run
```

---

## Common Pitfalls

### 1. Missing fallback

**Symptom**: Demo crashes on fresh clone (no fixtures).

**Fix**: Always provide inline fallback:

```python
if HOTDATA.exists():
    return HOTDATA.load()
return inline_fallback()  # Required!
```

### 2. Schema mismatch

**Symptom**: `ValidationError` when loading fixture.

**Fix**: Ensure fixture JSON matches schema. Use `kg fixture validate`.

### 3. Stale fixtures

**Symptom**: Demo shows old data.

**Fix**: Set TTL or run `kg fixture refresh --all`.

### 4. Generator not async

**Symptom**: `RuntimeError: coroutine was never awaited`

**Fix**: Generator functions must be async:

```python
async def generate_my_data() -> MyData:  # async!
    ...
```

---

## The HotData Principle

```
Pre-compute → Serialize → Hotload → (Optionally) Refresh
     ↓             ↓          ↓                ↓
   LLM once    JSON/YAML   Near-zero      LLM only when stale
```

---

## Related Skills

- `test-patterns.md` - Testing conventions
- `handler-patterns.md` - CLI handler patterns

---

## Changelog

- 2025-12-13: Initial version based on AD-004
