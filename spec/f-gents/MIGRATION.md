# F-gent Migration Guide

This document describes the migration from the scattered Flux implementation to the unified F-gent (Flow) spec.

---

## What Changed

### Before (Scattered)

Flux was defined in multiple locations:
- `spec/agents/flux.md` - Main spec
- `spec/c-gents/flux.md` - Functor catalog entry
- `impl/claude/agents/town/flux.py` - TownFlux implementation
- `docs/skills/flux-agent.md` - Usage skill

The F-letter was occupied by "Forge" agents (artifact synthesis) which had:
- Minimal implementation
- Significant overlap with J-gent, E-gent, L-gent
- No active development

### After (Unified)

F-gent now represents **Flow** agents:
- `spec/f-gents/README.md` - Core Flow spec
- `spec/f-gents/chat.md` - Chat modality
- `spec/f-gents/research.md` - Tree of thought modality
- `spec/f-gents/collaboration.md` - Blackboard modality

Old Forge specs are archived in `spec/f-gents-archived/`.

---

## Import Migration

### Python Imports

```python
# OLD (will be deprecated)
from agents.flux import Flux, FluxConfig, FluxAgent
from agents.town.flux import TownFlux

# NEW (preferred)
from agents.f import Flow, FlowConfig, FlowAgent
from agents.town.flux import TownFlux  # TownFlux stays in town module
```

### Deprecation Timeline

1. **Phase 1 (Current)**: Both imports work, old imports log warning
2. **Phase 2 (v2.0)**: Old imports raise DeprecationWarning
3. **Phase 3 (v3.0)**: Old imports removed

### Compatibility Shim

Add to `impl/claude/agents/flux/__init__.py`:

```python
"""Compatibility shim for flux -> f migration."""
import warnings
from agents.f import Flow as Flux, FlowConfig as FluxConfig, FlowAgent

warnings.warn(
    "agents.flux is deprecated. Use agents.f instead. "
    "See spec/f-gents/MIGRATION.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["Flux", "FluxConfig", "FluxAgent"]
```

---

## Spec References

### Old References to Update

| Old Path | New Path |
|----------|----------|
| `spec/agents/flux.md` | `spec/f-gents/README.md` |
| `spec/c-gents/flux.md` | `spec/f-gents/README.md` (consolidated) |
| `spec/f-gents/README.md` (Forge) | `spec/f-gents-archived/README.md` |
| `spec/f-gents/forge.md` | `spec/f-gents-archived/forge.md` |
| `spec/f-gents/contracts.md` | `spec/f-gents-archived/contracts.md` |
| `spec/f-gents/artifacts.md` | `spec/f-gents-archived/artifacts.md` |

### Cross-References to Update

Files that reference the old Flux spec:
- `spec/principles.md` - References `spec/agents/flux.md`
- `spec/c-gents/functor-catalog.md` - References flux functor
- `docs/skills/flux-agent.md` - Uses old patterns
- `spec/archetypes.md` - References flux configurations

---

## API Changes

### FluxConfig -> FlowConfig

```python
# OLD
config = FluxConfig(
    entropy_budget=1.0,
    buffer_size=100,
)

# NEW (same API, new name)
config = FlowConfig(
    entropy_budget=1.0,
    buffer_size=100,
)
```

### New Modality Parameter

```python
# NEW: Specify modality explicitly
chat_config = FlowConfig(modality="chat", context_window=128000)
research_config = FlowConfig(modality="research", max_branches=5)
collab_config = FlowConfig(modality="collaboration", agents=["a", "b"])
```

### New Methods

```python
# Chat-specific streaming
async for token in flow.stream_response(message):
    ...

# Research branching
children = await flow.branch(hypothesis)

# Collaboration posting
await flow.post(contribution)
```

---

## TownFlux Compatibility

TownFlux remains in `agents/town/flux.py` but now imports from F-gent:

```python
# In agents/town/flux.py
from agents.f import FlowPolynomial, FlowState, FlowConfig

class TownFlux:
    """Town simulation as Flow stream."""
    # Implementation unchanged
```

No breaking changes to TownFlux API.

---

## Where Old Forge Concepts Went

| Forge Concept | New Location | Rationale |
|---------------|--------------|-----------|
| Intent analysis | J-gent | JIT compilation from NL |
| Contract synthesis | C-gent | Type composition |
| Artifact versioning | L-gent | Library cataloging |
| Drift detection | E-gent | Evolutionary adaptation |
| ALO format | Deprecated | Too complex |
| Forge Loop | Archived | Bootstrap agents sufficient |

---

## Testing Migration

### Update Test Imports

```python
# OLD
from agents.flux import Flux
from agents.flux._tests import fixtures

# NEW
from agents.f import Flow
from agents.f._tests import fixtures
```

### Test Files to Update

- `agents/flux/_tests/` -> Keep as compatibility tests
- Add `agents/f/_tests/` with new modality tests

---

## Skill Updates Required

The skill doc `docs/skills/flux-agent.md` needs updates:

1. Update imports to use `agents.f`
2. Add sections for new modalities (chat, research, collaboration)
3. Reference new spec locations
4. Update verification commands

---

## Questions?

See:
- `spec/f-gents/README.md` - New Flow specification
- `spec/f-gents-archived/` - Old Forge specs (historical reference)
- `docs/skills/flux-agent.md` - Updated usage patterns
