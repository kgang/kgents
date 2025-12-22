# AGENTESE Node Registration

**Status:** Canonical Pattern
**Last Updated:** 2025-12-21

---

## The Core Principle (AD-011)

> **The AGENTESE registry is the SINGLE SOURCE OF TRUTH.**
> If a path isn't registered via `@node`, it doesn't exist.

See `spec/principles.md` AD-011 for the full architectural decision.

```
SINGLE SOURCE OF TRUTH

    @node("world.town")           ◄─── This is the ONLY place a path is defined
           │
           ▼
    ┌──────────────────────────────────────────────────────┐
    │              AGENTESE Registry                        │
    │   get_registry().list_paths() → ["world.town", ...]   │
    └──────────────────────────────────────────────────────┘
           │
           ├──────────────► NavigationTree.tsx (MUST match)
           ├──────────────► Cockpit.tsx (MUST match)
           ├──────────────► CLI handlers (MUST match)
           ├──────────────► API routes (auto-generated)
           └──────────────► Documentation (derived)
```

---

## Overview

This skill documents how to register AGENTESE nodes so they appear in:
1. `/agentese/discover` endpoint
2. NavigationTree in the UI
3. CLI tab completion
4. **Contract-based type generation** (see `agentese-contract-protocol.md`)

## The Problem

AGENTESE has two disconnected mechanisms for defining paths:

```
crown_jewels.py (PATHS dicts) ────→ Documentation only (NOT discoverable)

@node decorator ──→ NodeRegistry ──→ /discover ──→ NavigationTree
```

**Solution:** Use `@node` decorator on node classes for automatic registration.

**Phase 7 Enhancement:** Add `contracts={}` parameter for BE/FE type sync. See `agentese-contract-protocol.md` for full details.

---

## Quick Reference

### 1. Add `@node` Decorator to Your Node

```python
# In your node file (e.g., world_emergence.py)
from protocols.agentese.registry import node
from protocols.agentese.node import BaseLogosNode

@node("world.emergence", description="Cymatics Design Sampler")
@dataclass
class EmergenceNode(BaseLogosNode):
    """world.emergence - Your node description."""

    _handle: str = "world.emergence"

    @property
    def handle(self) -> str:
        return self._handle
```

### 1b. Add Contracts for BE/FE Type Sync (Recommended)

```python
from dataclasses import dataclass
from protocols.agentese.contract import Contract, Response
from protocols.agentese.registry import node

# Define contract types as dataclasses
@dataclass
class ManifestResponse:
    name: str
    status: str
    count: int

@dataclass
class ConfigureRequest:
    setting: str
    value: str | None = None

@dataclass
class ConfigureResponse:
    success: bool

# Add contracts={} to @node
@node(
    "world.emergence",
    description="Cymatics Design Sampler",
    contracts={
        "manifest": Response(ManifestResponse),
        "configure": Contract(ConfigureRequest, ConfigureResponse),
    }
)
@dataclass
class EmergenceNode(BaseLogosNode):
    ...
```

**See:** `agentese-contract-protocol.md` for complete contract documentation.

### 2. Ensure Module Is Imported at Startup

The `@node` decorator runs at **import time**. Modules must be imported for registration.

Add your module to `gateway.py`:

```python
# In protocols/agentese/gateway.py

def _import_node_modules() -> None:
    """Import all AGENTESE node modules to trigger @node registration."""
    try:
        from . import contexts
        from .contexts import world_myfeature      # ADD YOUR MODULE HERE
        from .contexts import self_memory
        logger.debug("AGENTESE node modules imported for registration")
    except ImportError as e:
        logger.warning(f"Could not import some node modules: {e}")
```

### 3. Add Route Mapping to NavigationTree (Frontend)

```typescript
// In web/src/shell/NavigationTree.tsx

// Route → AGENTESE path mapping
const routeToPath: Record<string, string> = {
  '/brain': 'self.memory',
  '/myfeature': 'world.myfeature',     // ADD YOUR MAPPING
  // ...
};

// AGENTESE path → Route mapping (reverse)
const pathToRoute: Record<string, string> = {
  'self.memory': '/brain',
  'world.myfeature': '/myfeature',     // ADD YOUR MAPPING
  // ...
};
```

---

## Architecture

```
                    Import Time                    Runtime
                    ───────────                    ───────
                         │
Module with @node ───────┤
        │                │
        ▼                │
@node decorator ─────────┼───→ NodeRegistry
                         │            │
_import_node_modules() ──┘            │
        │                             ▼
        ▼                      /agentese/discover
gateway.mount_on()                    │
                                      ▼
                              NavigationTree
                              (builds tree from paths)
```

### Key Insight

The `@node` decorator is a **side effect at import time**. If a module isn't imported, its nodes won't be registered, and they won't appear in discovery.

---

## Complete Example

### Step 1: Create the Node File

```python
# protocols/agentese/contexts/world_myfeature.py
"""
AGENTESE MyFeature Context.

world.myfeature.* paths for the MyFeature Crown Jewel.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


MYFEATURE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "configure",
)


@node("world.myfeature", description="My awesome feature")
@dataclass
class MyFeatureNode(BaseLogosNode):
    """world.myfeature - Interface for MyFeature."""

    _handle: str = "world.myfeature"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return MYFEATURE_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View MyFeature status",
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        return BasicRendering(
            summary="MyFeature Status",
            content="Everything is working!",
            metadata={"status": "ok", "route": "/myfeature"},
        )


# Factory functions
_node: MyFeatureNode | None = None

def get_myfeature_node() -> MyFeatureNode:
    global _node
    if _node is None:
        _node = MyFeatureNode()
    return _node


__all__ = [
    "MYFEATURE_AFFORDANCES",
    "MyFeatureNode",
    "get_myfeature_node",
]
```

### Step 2: Export from `__init__.py`

```python
# In protocols/agentese/contexts/__init__.py

from .world_myfeature import (
    MYFEATURE_AFFORDANCES,
    MyFeatureNode,
    get_myfeature_node,
)

# Add to __all__
__all__ = [
    # ... existing exports ...
    "MYFEATURE_AFFORDANCES",
    "MyFeatureNode",
    "get_myfeature_node",
]
```

### Step 3: Import in Gateway

```python
# In protocols/agentese/gateway.py

def _import_node_modules() -> None:
    try:
        from . import contexts
        from .contexts import world_myfeature  # ADD THIS LINE
        # ...
    except ImportError as e:
        logger.warning(f"Could not import some node modules: {e}")
```

### Step 4: Add Frontend Route Mapping

```typescript
// In NavigationTree.tsx

const routeToPath: Record<string, string> = {
  // ... existing ...
  '/myfeature': 'world.myfeature',
};

const pathToRoute: Record<string, string> = {
  // ... existing ...
  'world.myfeature': '/myfeature',
};
```

### Step 5: Verify Registration

```bash
cd impl/claude
uv run python -c "
from protocols.agentese.gateway import _import_node_modules
from protocols.agentese.registry import get_registry

_import_node_modules()
registry = get_registry()
paths = registry.list_paths()

print('Registered paths:')
for p in sorted(paths):
    print(f'  {p}')

print(f'world.myfeature registered: {\"world.myfeature\" in paths}')
"
```

---

## Common Issues

### Node Not Appearing in Discovery

**Symptom:** Path doesn't show in `/agentese/discover` or NavigationTree.

**Causes:**
1. Missing `@node` decorator on class
2. Module not imported in `_import_node_modules()`
3. Import error (check logs for warnings)

**Debug:**
```python
from protocols.agentese.registry import get_registry
registry = get_registry()
print(registry.list_paths())
```

### Node Appears in Discovery but Not Clickable

**Symptom:** Path shows in tree but clicking doesn't navigate.

**Cause:** Missing route mapping in NavigationTree.tsx.

**Fix:** Add both `routeToPath` and `pathToRoute` mappings.

### Decorator Order Matters

```python
# CORRECT: @node before @dataclass
@node("world.myfeature")
@dataclass
class MyNode: ...

# WRONG: @dataclass before @node
@dataclass
@node("world.myfeature")  # May not work correctly
class MyNode: ...
```

---

## Anti-Patterns

### Don't: Hardcode paths without @node

```python
# BAD: This won't be discoverable
MYFEATURE_PATHS = {
    "world.myfeature.manifest": {"aspect": "manifest", ...}
}
```

### Don't: Forget to import the module

```python
# BAD: Module exists but @node never runs
# (no import in _import_node_modules)
```

### Don't: Create circular imports

```python
# BAD: Importing heavy dependencies at module level
from services.myfeature import HeavyService  # Avoid if causes circular import

# GOOD: Import inside methods or use TYPE_CHECKING
if TYPE_CHECKING:
    from services.myfeature import HeavyService
```

---

## Dependency Injection for Nodes

When a node requires dependencies (services, persistence layers, etc.), you must:

### ✅ Enlightened Resolution (2025-12-21)

The container respects Python's signature semantics:

| Signature | Resolution | Behavior |
|-----------|------------|----------|
| `def __init__(self, service: SomeService):` | **Required** | Fails immediately with actionable error if not registered |
| `def __init__(self, service: SomeService \| None = None):` | **Optional** | Skipped gracefully if not registered (uses default) |
| `@node(dependencies=("service",))` | **All Required** | Declared deps are always required |

```python
# Missing REQUIRED dependency → DependencyNotFoundError with helpful message:
#
# DependencyNotFoundError: Missing required dependency 'inhabit_service' for InhabitNode.
#
# This usually means the provider wasn't registered during startup.
#
# Fix: In services/providers.py, add:
#     container.register("inhabit_service", get_inhabit_service, singleton=True)
#
# If this dependency should be optional, update the node's __init__:
#     def __init__(self, inhabit_service: InhabitService | None = None): ...
```

**The fix is ALWAYS the same:**
1. Every dependency in `@node(dependencies=(...))` MUST have a matching provider
2. Provider MUST be registered in `services/providers.py` → `setup_providers()`

### 1. Declare dependencies in @node decorator

```python
@node(
    "world.myfeature.action",
    description="Action workflow for MyFeature",
    dependencies=("myfeature_service",),  # REQUIRED: explicit declaration
    contracts={...},
)
class MyFeatureActionNode(BaseLogosNode):
    def __init__(self, myfeature_service: MyFeatureService) -> None:
        self.service = myfeature_service
```

### 2. Register providers in `services/providers.py`

```python
# Add provider function
async def get_myfeature_service() -> "MyFeatureService":
    """Get the MyFeatureService."""
    from services.myfeature.service import MyFeatureService
    return MyFeatureService()

# Register in setup_providers()
async def setup_providers() -> None:
    container = get_container()
    # ...existing registrations...
    container.register("myfeature_service", get_myfeature_service, singleton=True)
```

### 3. Container resolution flow

```
┌─────────────────────────────────────────────────────────────────┐
│  @node(dependencies=("commission_service",))                     │
│         │                                                        │
│         ▼                                                        │
│  container.create_node(cls, meta)                               │
│         │                                                        │
│         ├──→ Check meta.dependencies (all REQUIRED)             │
│         │         │                                              │
│         │         ▼                                              │
│         │    For each REQUIRED dep:                              │
│         │         │                                              │
│         │    container.has(name)?                                │
│         │    YES → container.resolve(name) → add to kwargs      │
│         │    NO  → ❌ DependencyNotFoundError (immediate!)       │
│         │                                                        │
│         ├──→ Check __init__ signature for OPTIONAL deps         │
│         │         │                                              │
│         │    container.has(name)?                                │
│         │    YES → container.resolve(name) → add to kwargs      │
│         │    NO  → ✓ skip gracefully (use __init__ default)     │
│         │                                                        │
│         ▼                                                        │
│  cls(**resolved_kwargs) → Node instance ✓                       │
└─────────────────────────────────────────────────────────────────┘
```

### Common DI Error

```
DependencyNotFoundError: Missing required dependency 'inhabit_service' for InhabitNode.

This usually means the provider wasn't registered during startup.

Fix: In services/providers.py, add:
    container.register("inhabit_service", get_inhabit_service, singleton=True)

If this dependency should be optional, update the node's __init__:
    def __init__(self, inhabit_service: InhabitService | None = None): ...
```

**Cause:** Node declares/requires a dependency that isn't registered in the container.

**Debugging checklist:**
1. ✓ Does `@node` have `dependencies=("inhabit_service",)` or does `__init__` require it?
2. ✓ Does `services/providers.py` have `get_inhabit_service()`?
3. ✓ Is it registered in `setup_providers()` with `container.register("inhabit_service", ...)`?
4. ✓ Is the name EXACTLY the same (case-sensitive)?

**Fix (if truly required):**
1. Add provider function `get_service_name()` to `services/providers.py`
2. Register: `container.register("service_name", get_service_name, singleton=True)`

**Fix (if optional - graceful degradation is OK):**
1. Update `__init__` signature: `def __init__(self, service: Service | None = None): ...`
2. Handle `None` case in node code

### Quick Validation

```bash
# Check what providers are registered:
cd impl/claude
uv run python -c "
from protocols.agentese.container import get_container
from services.providers import setup_providers
import asyncio

async def check():
    await setup_providers()
    container = get_container()
    print('Registered providers:')
    for name in sorted(container.list_providers()):
        print(f'  {name}')

asyncio.run(check())
"
```

### The DI Contract

```
┌────────────────────────────────────────────────────────────────┐
│                    THE DI CONTRACT                              │
│                                                                 │
│  For EVERY dependency in @node(dependencies=("foo", "bar")):   │
│                                                                 │
│    1. MUST exist: get_foo() in services/providers.py           │
│    2. MUST register: container.register("foo", get_foo, ...)   │
│    3. MUST match: Name in @node == Name in register()          │
│                                                                 │
│  If ANY of these are missing → DependencyNotFoundError (fast!) │
└────────────────────────────────────────────────────────────────┘
```

---

## SSE Streaming Aspects

When adding a streaming aspect (e.g., `stream` for real-time updates):

### 1. Define the Async Generator

```python
from typing import AsyncGenerator

@aspect(
    category=AspectCategory.PERCEPTION,
    description="SSE stream of events",
    streaming=True,  # Mark as streaming
)
async def stream(
    self, observer: "Observer", **kwargs: Any
) -> AsyncGenerator[dict[str, Any], None]:
    """Stream events via SSE.

    Yields raw dictionaries - the gateway's _generate_sse() handles formatting.

    Teaching:
        gotcha: Don't pre-format SSE data! The gateway wraps async generator
                output with `data: {json}\n\n`. Pre-formatting causes double-wrap.
                (Evidence: curl shows `data: "data: {...}"` if you format here)
    """
    # Yield raw dicts, NOT formatted strings
    yield {"type": "status", "data": {...}}
    yield {"type": "heartbeat", "timestamp": datetime.now().isoformat()}
```

### 2. Handle Async Generator in _invoke_aspect

```python
async def _invoke_aspect(
    self,
    aspect: str,
    observer: "Observer",
    **kwargs: Any,
) -> Any:
    """Invoke an aspect method by name.

    Teaching:
        gotcha: Async generator methods (like `stream`) must NOT be awaited.
                Calling them returns the generator directly. Awaiting fails with:
                "object async_generator can't be used in 'await' expression"
    """
    method = getattr(self, aspect, None)
    if method is not None:
        # For stream aspect, return the generator directly (don't await)
        if aspect == "stream":
            return method(observer, **kwargs)  # NO await!
        return await method(observer, **kwargs)
    raise ValueError(f"Unknown aspect: {aspect}")
```

### 3. Frontend Connection

```typescript
// CORRECT: aspect is at /{context}/{holon}/{aspect}
const stream = new EventSource('/agentese/self/collaboration/stream');

// WRONG: don't add extra /stream suffix
// const stream = new EventSource('/agentese/self/collaboration/stream/stream');

stream.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case 'status': /* handle */ break;
    case 'heartbeat': /* handle */ break;
  }
};
```

### SSE Streaming Gotchas

| Issue | Symptom | Fix |
|-------|---------|-----|
| Await async generator | "object async_generator can't be used in 'await' expression" | `return method()` not `await method()` |
| Pre-format SSE | Double-wrapped: `data: "data: {...}"` | Yield raw dicts, let gateway format |
| Wrong URL | 404 or connection refused | Use `/{aspect}` not `/{aspect}/stream` |
| Stale closures in React | Old callbacks, state doesn't update | Use refs for callbacks |

---

## Related Patterns

- **agentese-path.md** - Adding new AGENTESE paths
- **agentese-contract-protocol.md** - BE/FE type sync via contracts (Phase 7)
- **crown-jewel-patterns.md** - Crown Jewel architecture
- **metaphysical-fullstack.md** - The protocol IS the API

---

## Critical Learnings

```
@node runs at import time: If not imported, not registered
_import_node_modules(): Gateway calls this to ensure all nodes load
Two-way mapping needed: AGENTESE path ↔ React route
Discovery is pull-based: Frontend fetches /agentese/discover
contracts={} enables BE/FE type sync: JSON Schema generation at build time
Registry is single source of truth: Frontend MUST NOT reference unregistered paths (AD-011)
dependencies= must match providers: If @node declares deps, register them in setup_providers()
```

---

## Validation (AD-011)

The registry is the single source of truth. Validate that frontend paths match backend:

```bash
cd impl/claude
uv run python scripts/validate_path_alignment.py
```

**What it checks:**
1. All paths in `NavigationTree.tsx` have `@node` registrations
2. All paths in `Cockpit.tsx` have `@node` registrations
3. All hardcoded AGENTESE paths in frontend match backend

**Example output:**
```
=== AGENTESE Path Alignment Validator ===

Loading backend registry...
Found 39 registered paths

Checking web/src/shell/NavigationTree.tsx...
  OK: All 10 paths registered
Checking web/src/pages/Cockpit.tsx...
  OK: All 7 paths registered

=== Validation Summary ===

Backend registry: 39 paths
Frontend references: 17 paths
Valid: 17

PASSED: All frontend paths are registered in backend
```

**CI Integration:**

Add to `.github/workflows/ci.yml`:

```yaml
- name: Validate AGENTESE path alignment
  run: cd impl/claude && uv run python scripts/validate_path_alignment.py
```

**The Strict Protocol:**

1. **No aliases**: If a path doesn't exist as `@node`, it doesn't exist
2. **No workarounds**: Frontend can only reference registered paths
3. **Warnings are failures**: `logger.warning` for import failures, not `logger.debug`
4. **Dead links are bugs**: Fix frontend or add the node—no middle ground

---

*Last updated: 2025-12-22 (SSE streaming section added)*
