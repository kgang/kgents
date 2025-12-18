# AGENTESE Contract Protocol

**Status:** Canonical Pattern
**Last Updated:** 2025-12-18
**Source:** Phase 7 of `plans/autopoietic-architecture.md`

---

## Overview

The AGENTESE Contract Protocol makes `@node(contracts={})` the **single source of truth** for BE/FE type synchronization. Backend defines contracts, frontend discovers schemas at build time.

> *"The @node decorator is the contract authority—BE defines, FE discovers, both stay sync'd."*

### The Problem

Before Phase 7:
- Python backends served JSON to TypeScript frontends
- Types were defined separately in both languages
- No automated sync → drift → runtime crashes

### The Solution

```
@node(contracts={}) ──→ /discover?include_schemas=true ──→ sync-types.ts ──→ _generated/*.ts
       │                         │                              │
    BE defines              JSON Schema                   FE discovers
```

---

## Quick Reference

### 1. Define Contracts on Your Node

```python
from dataclasses import dataclass
from protocols.agentese.contract import Contract, Response
from protocols.agentese.registry import node
from protocols.agentese.node import BaseLogosNode

# Define your contract types as dataclasses
@dataclass
class MyManifestResponse:
    """Response for manifest aspect."""
    name: str
    count: int
    is_active: bool

@dataclass
class ConfigureRequest:
    """Request for configure aspect."""
    setting_name: str
    value: str | None = None

@dataclass
class ConfigureResponse:
    """Response for configure aspect."""
    success: bool
    message: str

# Attach contracts to @node decorator
@node(
    "world.myfeature",
    description="My Feature Crown Jewel",
    contracts={
        # Perception aspects (no request needed)
        "manifest": Response(MyManifestResponse),
        # Mutation aspects (request + response)
        "configure": Contract(ConfigureRequest, ConfigureResponse),
    }
)
@dataclass
class MyFeatureNode(BaseLogosNode):
    ...
```

### 2. Contract Type Selection

| Type | Use When | Example |
|------|----------|---------|
| `Response(T)` | Perception aspects (no input) | `manifest`, `affordances`, `witness` |
| `Request(T)` | Fire-and-forget (rare) | `notify` |
| `Contract(Req, Resp)` | Mutation aspects | `capture`, `evolve`, `configure` |

### 3. Run Sync Types

```bash
# In web/ directory
npm run sync-types         # Generate types from BE
npm run sync-types:check   # Verify types are in sync (CI mode)
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENTESE CONTRACT FLOW                               │
│                                                                              │
│  Python Dataclass ───→ @node(contracts={}) ───→ NodeRegistry                │
│         │                                            │                       │
│         │                                            ▼                       │
│         ▼                                    /discover?include_schemas=true  │
│  schema_gen.py                                       │                       │
│  dataclass_to_schema()                               │                       │
│         │                                            ▼                       │
│         └───────────────────────────────────→ JSON Schema                   │
│                                                      │                       │
│                                                      ▼                       │
│                                           sync-types.ts (FE build)          │
│                                                      │                       │
│                                                      ▼                       │
│                                           web/src/api/types/_generated/     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Components

| File | Purpose |
|------|---------|
| `protocols/agentese/contract.py` | Contract, Response, Request types |
| `protocols/agentese/schema_gen.py` | dataclass → JSON Schema conversion |
| `protocols/agentese/registry.py` | @node with contracts={} parameter |
| `protocols/agentese/gateway.py` | /discover endpoint with include_schemas |
| `web/scripts/sync-types.ts` | FE build-time type generation |

---

## Step-by-Step: Adding Contracts to a Crown Jewel

### Step 1: Create Contract Dataclasses

```python
# services/myjewel/contracts.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ItemStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"

@dataclass
class ItemSummary:
    """Summary of an item for list views."""
    id: str
    name: str
    status: ItemStatus
    created_at: datetime

@dataclass
class ManifestResponse:
    """Response for manifest aspect."""
    total_items: int
    active_count: int
    items: list[ItemSummary]

@dataclass
class CreateItemRequest:
    """Request to create a new item."""
    name: str
    description: str | None = None

@dataclass
class CreateItemResponse:
    """Response after creating an item."""
    id: str
    name: str
    status: ItemStatus = field(default=ItemStatus.PENDING)
```

### Step 2: Register Contracts on Node

```python
# services/myjewel/node.py
from protocols.agentese.contract import Contract, Response
from protocols.agentese.registry import node
from .contracts import (
    ManifestResponse,
    CreateItemRequest,
    CreateItemResponse,
    ItemSummary,
)

@node(
    "world.myjewel",
    description="My Jewel Crown",
    contracts={
        "manifest": Response(ManifestResponse),
        "item.create": Contract(CreateItemRequest, CreateItemResponse),
        "item.list": Response(list[ItemSummary]),  # Can use list directly
    }
)
@dataclass
class MyJewelNode(BaseLogosNode):
    ...
```

### Step 3: Verify Discovery

```bash
cd impl/claude
uv run python -c "
from protocols.agentese.gateway import _import_node_modules
from protocols.agentese.registry import get_registry

_import_node_modules()
registry = get_registry()

# Check contracts registered
contracts = registry.get_contracts('world.myjewel')
print('Contracts for world.myjewel:')
for aspect, contract in contracts.items():
    print(f'  {aspect}: {contract}')
"
```

### Step 4: Generate Frontend Types

```bash
# Start backend (required for discovery)
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --port 8000 &

# Generate types
cd ../web
npm run sync-types

# Check generated file
cat src/api/types/_generated/world.myjewel.ts
```

---

## Type Separation Pattern

### Two Categories of Frontend Types

| Category | Location | Source | Example |
|----------|----------|--------|---------|
| **Contract Types** | `_generated/` | BE discovery | `WorldTownManifestResponse` |
| **Local Types** | `_local.ts` | FE-only | `BUILDER_COLORS`, `NPHASE_CONFIG` |

### Why Separate?

```typescript
// _generated/world.town.ts — FROM BACKEND (contract)
export interface WorldTownManifestResponse {
  name: string;
  citizen_count: number;
  regions: string[];
}

// _local.ts — FE ONLY (not from backend)
export const BUILDER_COLORS = {
  primary: '#3B82F6',
  secondary: '#10B981',
} as const;

export const PHASE_ICONS: Record<NPhase, string> = {
  SENSE: '👁',
  ACT: '⚡',
  REFLECT: '🪞',
};
```

### Re-Export Pattern

```typescript
// src/api/types.ts — Unified entry point
export * from './types/_generated/world.town';
export * from './types/_generated/self.memory';
// ...

// Type aliases for backwards compatibility
export type TownManifestContract = WorldTownManifestResponse;

// Re-export local types
export * from './types/_local';
```

---

## CI Integration

### Three Modes

| Mode | CI Behavior | When to Use |
|------|-------------|-------------|
| **Advisory** (default) | Warns, never blocks | Exploration, creative sessions |
| **Gatekeeping** (opt-in) | Blocks on drift | Pre-release, Crown Jewel stabilization |
| **Aspirational** | Tracks as metric | Quarterly planning, roadmaps |

### CI Workflow

```yaml
# .github/workflows/ci.yml (excerpt)
jobs:
  contract-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start Backend
        run: |
          cd impl/claude
          uv run uvicorn protocols.api.app:create_app --factory --port 8000 &
          sleep 5  # Wait for server

      - name: Check Contract Sync
        run: |
          cd impl/claude/web
          npm run sync-types:check
```

### Enabling Gatekeeping

```yaml
# In your plan frontmatter
specgraph_mode: gatekeeping
```

Or run explicitly:
```bash
npm run sync-types:check  # Fails CI if types drift
```

---

## JSON Schema Generation

### Supported Types

| Python Type | JSON Schema |
|-------------|-------------|
| `str` | `{"type": "string"}` |
| `int` | `{"type": "integer"}` |
| `float` | `{"type": "number"}` |
| `bool` | `{"type": "boolean"}` |
| `list[T]` | `{"type": "array", "items": {...}}` |
| `dict[K, V]` | `{"type": "object", "additionalProperties": {...}}` |
| `T \| None` | `{...type..., "nullable": true}` |
| `Enum` | `{"type": "string", "enum": [...values...]}` |
| `@dataclass` | Nested object schema |

### Example Conversion

```python
@dataclass
class TownManifest:
    name: str
    citizen_count: int
    is_active: bool
    regions: list[str]
    metadata: dict[str, Any] | None = None
```

Becomes:

```json
{
  "type": "object",
  "title": "TownManifest",
  "properties": {
    "name": {"type": "string"},
    "citizen_count": {"type": "integer"},
    "is_active": {"type": "boolean"},
    "regions": {"type": "array", "items": {"type": "string"}},
    "metadata": {"type": "object", "nullable": true}
  },
  "required": ["name", "citizen_count", "is_active", "regions"]
}
```

---

## Common Issues

### BE Not Running During Sync

**Symptom:** `sync-types` fails with connection refused.

**Fix:** Start backend first:
```bash
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --port 8000
```

### Node Not Showing Contracts

**Symptom:** Node exists but contracts empty in `/discover`.

**Causes:**
1. Missing `contracts={}` parameter on `@node`
2. Contract types not imported
3. Module not imported in `_import_node_modules()`

**Debug:**
```python
registry = get_registry()
print(registry.get_contracts("world.myjewel"))  # Should show contracts
```

### TypeScript Import Errors

**Symptom:** `Module not found: _generated/...`

**Cause:** TypeScript "bundler" moduleResolution requires explicit file paths.

**Fix:** Use explicit `.ts` extension in re-exports:
```typescript
// Correct
export * from './types/_generated/world.town';

// Wrong (may fail with bundler moduleResolution)
export * from './types/_generated/';
```

---

## Migration from Manual Types

### Before (Manual)

```typescript
// web/src/reactive/types.ts — hand-written
export interface TownManifest {
  name: string;
  citizen_count: number;  // May drift from backend!
}
```

### After (Generated)

```python
# services/town/contracts.py
@dataclass
class TownManifestResponse:
    name: str
    citizen_count: int
```

```typescript
// web/src/api/types/_generated/world.town.ts — auto-generated
export interface WorldTownManifestResponse {
  name: string;
  citizen_count: number;
}

// web/src/api/types.ts — re-export with alias
export type TownManifest = WorldTownManifestResponse;  // Backwards compatible
```

---

## Related Patterns

- **agentese-node-registration.md** — Node registration (prerequisite)
- **frontend-contracts.md** — Manual testing approach (pre-Phase 7)
- **crown-jewel-patterns.md** — Crown Jewel patterns (Pattern 13: Contract-First)
- **metaphysical-fullstack.md** — Full vertical slice architecture

---

## Critical Learnings

```
@node(contracts={}) makes node the contract authority—BE defines, FE discovers
BE running during FE build is acceptable; cached discovery JSON is more complex
Split types: _generated/ for contracts, _local.ts for FE-only (colors, icons)
Contract = Request + Response; Response() shorthand for perception aspects
Three modes: Advisory (warn), Gatekeeping (fail CI), Aspirational (track)
TypeScript "bundler" moduleResolution requires explicit file references
```

---

*Last updated: 2025-12-18 | Source: Phase 7, Autopoietic Architecture*
