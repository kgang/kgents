# D-gent Schemas

Versioned data contracts for the Crystal system.

## Overview

Schemas are frozen dataclasses that define the structure of data independent of database models. Each schema has:

- A qualified name (e.g., `trail.trail`, `witness.mark`)
- A version number (monotonically increasing)
- A frozen dataclass contract
- Optional migration functions for version upgrades

## Available Schemas

### Trail Schemas

First-class knowledge artifacts for exploration and navigation.

| Schema | Version | Purpose |
|--------|---------|---------|
| `trail.trail` | v1 | Trail metadata (name, description, fork info) |
| `trail.step` | v1 | Single navigation action in a trail |
| `trail.commitment` | v1 | Claim with commitment level (speculative/moderate/strong/definitive) |
| `trail.annotation` | v1 | Comment or annotation on a trail step |

### Witness Schemas

Crown Jewel schemas for the Witness system.

| Schema | Version | Purpose |
|--------|---------|---------|
| `witness.mark` | v1 | Single witnessed action |
| `witness.trust` | v1 | Trust score for an action |
| `witness.thought` | v1 | Reflective thought |
| `witness.action` | v1 | Recorded action |
| `witness.escalation` | v1 | Escalation event |

## Usage

```python
from agents.d.schemas.trail import Trail, TRAIL_SCHEMA

# Create a trail
trail = Trail(
    name="Bug Investigation",
    description="Investigating auth timeout",
    created_by_id="developer-42",
    is_active=True,
)

# Serialize to dict with metadata
trail_dict = TRAIL_SCHEMA.to_dict(trail)
# -> {'name': '...', ..., '_schema': 'trail.trail', '_version': 1}

# Parse back from dict
reconstructed = TRAIL_SCHEMA.parse(trail_dict)
assert reconstructed == trail
```

## Schema Evolution

When you need to evolve a schema:

1. Create a new version of the frozen dataclass
2. Increment the version number
3. Add a migration function

```python
@dataclass(frozen=True)
class TrailV2:
    name: str
    description: str
    created_by_id: str
    is_active: bool = True
    forked_from_id: str | None = None
    parent_step_index: int | None = None
    tags: tuple[str, ...] = ()  # NEW field

TRAIL_SCHEMA_V2 = Schema(
    name="trail.trail",
    version=2,
    contract=TrailV2,
    migrations={
        1: lambda d: {**d, "tags": ()},  # v1 -> v2 migration
    },
)
```

## Testing

Run the demo:
```bash
uv run python agents/d/schemas/_demo_trail.py
```

## Philosophy

Schemas in kgents are code, not database DDL:

- **Frozen dataclasses**: Immutable, hashable, type-safe
- **Version as code**: Schemas version like code, not like databases
- **Lazy upgrades**: Old data auto-upgrades on read
- **Graceful degradation**: Unknown schemas fall back to raw Datum

See: `spec/protocols/unified-data-crystal.md`
