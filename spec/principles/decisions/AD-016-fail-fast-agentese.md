# AD-016: Fail-Fast AGENTESE Resolution

**Date**: 2025-12-23
**Status**: Accepted
**Supersedes**: None

---

## Context

The AGENTESE system had a "JIT fallback" that generated placeholder responses when a node wasn't properly registered. This was designed as graceful degradation but **masked bugs**:

- When `registry.has(path)` returned False, the system fell back to Logos JIT generation
- JIT returned generic responses like `BasicRendering(summary='Concept: graph', content='The concept of graph.')`
- This hid registration failures, making debugging extremely difficult
- We spent significant time debugging why `kg graph` returned JIT fallback instead of actual data

The silent fallback violated several principles:
- **Ethical (Principle 3)**: "Transparency: Agents are honest about limitations and uncertainty." JIT fallback was dishonest—it pretended to have data when it didn't.
- **Operational Principle (Transparent Infrastructure)**: "Infrastructure should communicate what it's doing. Users should never wonder 'what just happened?'"
- **AD-011 (Registry as Single Source)**: "The registry IS the territory. Claims must be verified." JIT fallback let the CLI claim it handled paths that weren't registered.

---

## Decision

> **AGENTESE resolution SHALL fail fast on unregistered paths. JIT fallback as silent degradation is forbidden.**

When a path is not registered:
1. **Fail immediately** with `NodeNotRegisteredError`
2. **Include helpful information**: which path, similar registered paths, how to fix
3. **No silent JIT generation** for unregistered paths
4. **Preserve JIT for explicit use** (spec compilation, `void.jit.*`)

### The New Error Model

```python
class NodeNotRegisteredError(AgentesError):
    """
    Raised when an AGENTESE path is invoked but no @node is registered.

    AD-016: Silent fallback to JIT is forbidden.
    """

    def __init__(self, path: str, similar_paths: list[str]):
        self.path = path
        self.similar_paths = similar_paths
        super().__init__(
            f"Node '{path}' not registered",
            why="No @node decorator registered this path (AD-016: fail-fast resolution)",
            suggestion="Ensure @node decorator is applied and module is imported in setup_providers()",
            related=similar_paths[:5],
        )
```

### Gateway Response (HTTP)

```json
{
  "error": "Node 'concept.fake' not registered",
  "why": "No @node decorator registered this path (AD-016: fail-fast resolution)",
  "similar_paths": ["concept.graph", "concept.design", "concept.scope"],
  "suggestion": "1) Ensure @node decorator is applied, 2) Import module in providers.py",
  "discover_endpoint": "/agentese/discover"
}
```

---

## Changes Made

### 1. `protocols/agentese/exceptions.py`
- Added `NodeNotRegisteredError` class
- Added `node_not_registered()` convenience constructor

### 2. `protocols/cli/projection.py`
- Removed JIT fallback block (~50 lines)
- Replaced with fail-fast error that shows similar paths

### 3. `protocols/agentese/gateway.py`
- Changed `fallback_to_logos: bool = True` default to `False`
- Updated `_invoke_path()` to return HTTP 404 with helpful error details
- Updated factory function `create_gateway()` default

### 4. `protocols/agentese/logos.py`
- Removed "fallback to minimal JIT node on compilation failure"
- Now raises `TastefulnessError` on compilation failure (fail-fast)

---

## Consequences

### Positive
1. **Immediate feedback**: Unregistered paths error immediately with actionable message
2. **Reduced debugging time**: No more wondering why responses are generic
3. **Registration bugs caught early**: Missing imports surface immediately
4. **AD-011 enforced**: Registry is now actually the single source of truth

### Neutral
1. JIT remains available for explicit use (`logos._generate_from_spec()`)
2. Gateway can still use JIT for explicit JIT endpoints if needed

### Negative (Acceptable)
1. Code that relied on silent fallback will now error (intentional)
2. Some paths that "seemed to work" will now fail (revealing hidden bugs)

---

## Anti-patterns

- **Silent fallback to placeholder content**: The exact thing we're removing
- **Generic "not found" without suggestions**: Errors must help users fix the problem
- **Swallowing errors in fallback paths**: Let errors propagate
- **Using JIT as cover for missing implementations**: JIT is for explicit generation, not hiding bugs

---

## Verification

```bash
# Should error clearly with helpful message
uv run kg concept.fake.manifest

# Should still work (registered paths)
uv run kg graph
uv run kg concept.graph.manifest

# Tests should pass
uv run pytest protocols/agentese/_tests/ -q
```

---

## Connection to Other ADs

- **AD-011 (Registry Single Source)**: This AD enforces AD-011—if the registry doesn't have it, it doesn't exist
- **AD-010 (Habitat Guarantee)**: Habitat applies to **registered** paths; unregistered paths fail
- **AD-009 (Metaphysical Fullstack)**: Fail-fast is part of the stack—the error IS the projection

---

## The Zen Principle

> *"The river that refuses to pretend boulders are water finds the true path around them."*

Silent fallback is pretending. Fail-fast is truth.

---

*Filed: 2025-12-23*
