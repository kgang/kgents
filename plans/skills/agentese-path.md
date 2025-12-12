# Skill: Adding an AGENTESE Path

> Add a new path to the AGENTESE system (e.g., `self.soul.*` or `world.calendar.*`).

**Difficulty**: Medium
**Prerequisites**: Understanding of AGENTESE ontology (`spec/protocols/agentese.md`), familiarity with Python dataclasses
**Files Touched**: `protocols/agentese/contexts/<context>.py`, `protocols/agentese/contexts/__init__.py`, tests

---

## Overview

AGENTESE paths follow the structure `<context>.<holon>.<aspect>`. There are exactly **five contexts**:

| Context | Purpose | Resolver File |
|---------|---------|---------------|
| `world.*` | External entities | `contexts/world.py` |
| `self.*` | Internal state | `contexts/self_.py` |
| `concept.*` | Abstract ideas | `contexts/concept.py` |
| `void.*` | Entropy/Accursed Share | `contexts/void.py` |
| `time.*` | Temporal operations | `contexts/time.py` |

Adding a new path involves:
1. **Adding to an existing context** (most common) - Add a new holon to a context
2. **Adding a new aspect** to an existing holon - Extend an existing node

---

## Step-by-Step: Add a Holon to Existing Context

This is the most common case: adding something like `self.semaphore.*` or `world.purgatory.*`.

### Step 1: Define Affordances

Add your holon's affordances to the context's affordance dict.

**File**: `impl/claude/protocols/agentese/contexts/<context>.py`

**Pattern** (using `self_.py` as example):
```python
# Near the top of the file, find or add the affordances dict
SELF_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "memory": ("consolidate", "prune", "checkpoint", "recall", "forget"),
    "capabilities": ("list", "acquire", "release"),
    # ... existing entries ...

    # ADD YOUR NEW HOLON HERE
    "semaphore": ("pending", "yield", "status"),
}
```

### Step 2: Create the Node Class

Create a dataclass that extends `BaseLogosNode`.

**File**: `impl/claude/protocols/agentese/contexts/<context>.py`

**Template**:
```python
@dataclass
class MyNewNode(BaseLogosNode):
    """
    <context>.<holon> - Brief description.

    Provides access to <what this does>:
    - aspect1: Description
    - aspect2: Description
    - aspect3: Description

    AGENTESE: <context>.<holon>.*
    """

    _handle: str = "<context>.<holon>"

    # Integration points (optional)
    _some_service: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return affordances for this holon."""
        # Option 1: Same for all archetypes
        return SELF_AFFORDANCES["<holon>"]

        # Option 2: Archetype-specific
        # if archetype in ("admin", "developer"):
        #     return ("aspect1", "aspect2", "aspect3")
        # return ("aspect1",)  # Read-only for others

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View current state."""
        return BasicRendering(
            summary="<Holon> State",
            content="Description of current state",
            metadata={"key": "value"},
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle holon-specific aspects."""
        match aspect:
            case "aspect1":
                return await self._handle_aspect1(observer, **kwargs)
            case "aspect2":
                return await self._handle_aspect2(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _handle_aspect1(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle aspect1 - describe what it does."""
        # Your implementation here
        return {"status": "ok"}

    async def _handle_aspect2(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle aspect2 - describe what it does."""
        # Your implementation here
        return {"status": "ok"}
```

### Step 3: Wire into Context Resolver

Add your node to the context resolver's `resolve()` method.

**File**: `impl/claude/protocols/agentese/contexts/<context>.py`

**Pattern** (for `SelfContextResolver`):
```python
@dataclass
class SelfContextResolver:
    """Resolver for self.* context."""

    # Add integration point if needed
    _purgatory: Any = None

    # Add singleton node field
    _semaphore: SemaphoreNode | None = None

    def __post_init__(self) -> None:
        """Initialize singleton nodes."""
        # ... existing nodes ...
        self._semaphore = SemaphoreNode(_purgatory=self._purgatory)

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """Resolve a self.* path to a node."""
        match holon:
            # ... existing cases ...
            case "semaphore":
                return self._semaphore or SemaphoreNode()
            case _:
                # Fallback for undefined holons
                return GenericSelfNode(holon)
```

### Step 4: Update Factory Function

If your node needs integration points, update the context's factory function.

**File**: `impl/claude/protocols/agentese/contexts/<context>.py`

**Pattern**:
```python
def create_self_resolver(
    d_gent: Any = None,
    n_gent: Any = None,
    purgatory: Any = None,  # ADD NEW PARAMETER
) -> SelfContextResolver:
    """Create a SelfContextResolver with optional integrations."""
    resolver = SelfContextResolver()
    resolver._d_gent = d_gent
    resolver._n_gent = n_gent
    resolver._purgatory = purgatory  # WIRE IT IN
    resolver.__post_init__()
    return resolver
```

### Step 5: Update `create_context_resolvers`

If you added new integration points, update the unified factory.

**File**: `impl/claude/protocols/agentese/contexts/__init__.py`

**Pattern**:
```python
def create_context_resolvers(
    # ... existing params ...
    purgatory: Any = None,  # ADD IF NEW
) -> dict[str, Any]:
    """Create all five context resolvers."""
    return {
        # ... existing resolvers ...
        "self": create_self_resolver(
            d_gent=d_gent,
            n_gent=narrator,
            purgatory=purgatory,  # PASS IT THROUGH
        ),
    }
```

### Step 6: Export from `__init__.py`

Export your new node class and any constants.

**File**: `impl/claude/protocols/agentese/contexts/__init__.py`

**Pattern**:
```python
from .self_ import (
    # ... existing exports ...
    SemaphoreNode,  # ADD
)

__all__ = [
    # ... existing exports ...
    "SemaphoreNode",  # ADD
]
```

### Step 7: Write Tests

Create tests for your new path.

**File**: `impl/claude/protocols/agentese/contexts/_tests/test_<holon>.py`

**Template**:
```python
"""
Tests for <context>.<holon>.* paths.

Tests verify:
1. Basic functionality of each aspect
2. Affordance filtering by archetype
3. Error handling
4. Integration with services (if applicable)
"""

from __future__ import annotations

from typing import Any, cast

import pytest
from bootstrap.umwelt import Umwelt

from ..<context> import (
    MyNewNode,
    create_<context>_resolver,
)


# === Test Fixtures ===

class MockDNA:
    """Mock DNA for testing."""
    def __init__(self, name: str = "test", archetype: str = "default") -> None:
        self.name = name
        self.archetype = archetype
        self.capabilities: tuple[str, ...] = ()


class MockUmwelt:
    """Mock Umwelt for testing."""
    def __init__(self, archetype: str = "default", name: str = "test") -> None:
        self.dna = MockDNA(name=name, archetype=archetype)
        self.gravity: tuple[Any, ...] = ()
        self.context: dict[str, Any] = {}


@pytest.fixture
def observer() -> Umwelt[Any, Any]:
    """Default observer."""
    return cast(Umwelt[Any, Any], MockUmwelt())


@pytest.fixture
def resolver() -> <Context>ContextResolver:
    """Context resolver."""
    return create_<context>_resolver()


# === Tests ===

class TestAspect1:
    """Tests for <context>.<holon>.aspect1"""

    @pytest.mark.asyncio
    async def test_aspect1_basic(
        self,
        resolver: <Context>ContextResolver,
        observer: Umwelt[Any, Any],
    ) -> None:
        """Basic test for aspect1."""
        node = resolver.resolve("<holon>", [])

        result = await node._invoke_aspect("aspect1", observer)

        assert result["status"] == "ok"


class TestAffordances:
    """Tests for affordance filtering."""

    def test_affordances_for_admin(self) -> None:
        """Admin has expected affordances."""
        node = MyNewNode()
        affordances = node._get_affordances_for_archetype("admin")

        assert "aspect1" in affordances
        assert "aspect2" in affordances
```

---

## Step-by-Step: Add Aspect to Existing Holon

If you need to add a new aspect to an existing holon (e.g., adding `self.memory.dream`):

### Step 1: Add to Affordances

**File**: `impl/claude/protocols/agentese/contexts/<context>.py`

```python
SELF_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "memory": ("consolidate", "prune", "checkpoint", "recall", "forget", "dream"),  # ADD
    # ...
}
```

### Step 2: Add Handler Method

```python
async def _invoke_aspect(
    self,
    aspect: str,
    observer: "Umwelt[Any, Any]",
    **kwargs: Any,
) -> Any:
    match aspect:
        # ... existing cases ...
        case "dream":
            return await self._dream(observer, **kwargs)

async def _dream(
    self,
    observer: "Umwelt[Any, Any]",
    **kwargs: Any,
) -> dict[str, Any]:
    """Handle dream aspect - hypnagogic memory consolidation."""
    # Implementation
    return {"dreamed": True}
```

### Step 3: Add Tests

Add test cases for the new aspect.

---

## Verification

### Test 1: Resolve path

```bash
cd impl/claude
uv run python -c "
from protocols.agentese import create_logos
logos = create_logos()
node = logos.resolve('<context>.<holon>')
print(f'Handle: {node.handle}')
"
```

### Test 2: Check affordances

```bash
uv run python -c "
from protocols.agentese import create_logos
from protocols.agentese.node import AgentMeta
logos = create_logos()
node = logos.resolve('<context>.<holon>')
meta = AgentMeta(name='test', archetype='admin')
print(f'Affordances: {node.affordances(meta)}')
"
```

### Test 3: Run tests

```bash
cd impl/claude
uv run pytest protocols/agentese/contexts/_tests/test_<holon>.py -v
```

### Test 4: Full invoke

```bash
uv run python -c "
import asyncio
from typing import Any, cast
from bootstrap.umwelt import Umwelt
from protocols.agentese import create_logos

class MockDNA:
    def __init__(self, archetype: str = 'admin'):
        self.name = 'test'
        self.archetype = archetype
        self.capabilities: tuple[str, ...] = ()

class MockUmwelt:
    def __init__(self, archetype: str = 'admin'):
        self.dna = MockDNA(archetype=archetype)
        self.gravity: tuple[Any, ...] = ()
        self.context: dict[str, Any] = {}

async def main():
    logos = create_logos()
    umwelt = cast(Umwelt[Any, Any], MockUmwelt(archetype='admin'))
    result = await logos.invoke('<context>.<holon>.<aspect>', umwelt)
    print(result)

asyncio.run(main())
"
```

---

## Common Pitfalls

### 1. Forgetting to export from `__init__.py`

**Symptom**: `ImportError` when trying to use your node elsewhere.

**Fix**: Add to both imports and `__all__` in `contexts/__init__.py`.

### 2. Not wiring integration points

**Symptom**: Your node always returns "not configured" errors.

**Fix**:
1. Add parameter to factory function
2. Pass through in `create_context_resolvers()`
3. Wire to resolver's `__post_init__()`

### 3. Missing `@property` on handle

**Symptom**: `AttributeError: 'MyNode' object has no attribute 'handle'`

**Fix**: Ensure `handle` is a property:
```python
@property
def handle(self) -> str:
    return self._handle
```

### 4. Blocking in async methods

**Symptom**: Performance issues, event loop blocked.

**Fix**: Use `await` for I/O operations, don't do heavy computation in aspect handlers.

### 5. Not handling unknown aspects

**Symptom**: `KeyError` or crashes on unrecognized aspects.

**Fix**: Always have a default case in your match statement:
```python
case _:
    return {"aspect": aspect, "status": "not implemented"}
```

### 6. Returning arrays instead of single values

**Symptom**: Breaks composition pipelines.

**Fix**: Return iterators or single values, never raw arrays (see Minimal Output Principle in spec).

---

## Real Example: Adding `self.semaphore.*`

The semaphore path was added in this order:

1. **Affordances** in `self_.py`:
   ```python
   "semaphore": ("pending", "yield", "status"),
   ```

2. **SemaphoreNode class** (100 lines) handling:
   - `pending`: List pending semaphores
   - `yield`: Create new semaphore
   - `status`: Get token status

3. **SelfContextResolver update**:
   - Added `_purgatory: Any = None` field
   - Added `_semaphore: SemaphoreNode | None = None` field
   - Added case in `resolve()` method
   - Updated `__post_init__()` to create node

4. **Factory update** in `create_self_resolver()`:
   - Added `purgatory` parameter
   - Wired to resolver

5. **`__init__.py` updates**:
   - Added `SemaphoreNode` import
   - Added to `__all__`
   - Updated `create_context_resolvers()` parameter

6. **Tests** in `contexts/_tests/test_semaphore_paths.py` (700 lines)

---

## Related Skills

- [cli-command](cli-command.md) - Adding CLI commands
- [handler-patterns](handler-patterns.md) - Common handler patterns
- [test-patterns](test-patterns.md) - Testing patterns

---

## Changelog

- 2025-12-12: Initial version based on `self.semaphore.*` and `world.purgatory.*` implementations
