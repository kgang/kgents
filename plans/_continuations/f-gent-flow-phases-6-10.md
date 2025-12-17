---
plan: f-gent-flow-phases-6-10
status: complete
priority: high
created: 2025-12-16
completed: 2025-12-16
estimated_sessions: 1
actual_sessions: 1
dependencies:
  - f-gent-flow-implementation (phases 1-5 complete)
session_notes: |
  KEY INSIGHT: agents.flux and agents.f are COMPLEMENTARY, not migration targets.
  - agents.flux = Streaming infrastructure (Flux Functor, streams, pipelines)
  - agents.f = Flow modalities (Chat, Research, Collaboration conversations)

  Phases 6/9 (Flux Migration/Cleanup) were SKIPPED because no migration needed.
  Phase 7 (AGENTESE) COMPLETE: self.flow.* paths with 21 tests.
  Phase 8 (Documentation) COMPLETE: flow-modalities.md + systems-reference.md.
  Phase 10 (Testing) COMPLETE: All tests pass.
---

# F-gent Flow Implementation: Phases 6-10

## Context

**Phases 1-5 are COMPLETE.** The core F-gent Flow implementation is done:

- Phase 1: Old Forge archived (backward-compatible exports preserved)
- Phase 2: Core infrastructure (state.py, config.py, polynomial.py, operad.py, flow.py, pipeline.py)
- Phase 3: Chat modality (context.py, chat.py) - 33 tests
- Phase 4: Research modality (hypothesis.py, research.py) - 34 tests
- Phase 5: Collaboration modality (blackboard.py, collaboration.py) - 24 tests

**All 365 F-gent tests pass.**

This continuation covers migration, AGENTESE integration, documentation, and cleanup.

---

## What's Already Built

### Core Files (`impl/claude/agents/f/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Exports new Flow API + deprecated Forge API |
| `state.py` | FlowState enum (DORMANT, STREAMING, BRANCHING, CONVERGING, DRAINING, COLLAPSED) |
| `config.py` | FlowConfig with ChatConfig, ResearchConfig, CollaborationConfig |
| `polynomial.py` | FlowPolynomial, CHAT_POLYNOMIAL, RESEARCH_POLYNOMIAL, COLLABORATION_POLYNOMIAL |
| `operad.py` | FLOW_OPERAD with 13 operations, modality-specific subsets |
| `flow.py` | Flow.lift(), Flow.lift_multi(), FlowAgent, FlowEvent |
| `pipeline.py` | FlowPipeline with `\|` operator |

### Modalities (`impl/claude/agents/f/modalities/`)

| File | Purpose |
|------|---------|
| `context.py` | SlidingContext, SummarizingContext, Message, count_tokens |
| `chat.py` | Turn, ChatFlow |
| `hypothesis.py` | Evidence, Hypothesis, HypothesisTree, Insight, Synthesis |
| `research.py` | ResearchFlow, exploration strategies, ResearchStats |
| `blackboard.py` | Contribution, Vote, Proposal, Decision, Query, AgentRole, Blackboard |
| `collaboration.py` | RoundRobinOrder, PriorityOrder, FreeFormOrder, CollaborationFlow |

### Old Forge API (Preserved for Backward Compatibility)

These are still exported from `agents.f` for backward compatibility:
- `Intent`, `Contract`, `Artifact`, `crystallize`, etc.
- Files: `intent.py`, `contract.py`, `crystallize.py`, `prototype.py`, `validate.py`, `j_integration.py`

---

## Phase 6: Migrate Existing Flux Code

### 6.1 Identify Flux Locations

```bash
# Find all flux references
rg -l "from agents.flux" impl/claude/
rg -l "from agents.town.flux" impl/claude/
rg -l "FluxAgent|FluxConfig|FluxState" impl/claude/
```

### 6.2 Create Compatibility Shim

Create `impl/claude/agents/flux/__init__.py` if it doesn't exist:

```python
"""
Compatibility shim - flux is now agents.f

See spec/f-gents/MIGRATION.md for migration guide.
"""
import warnings

warnings.warn(
    "agents.flux is deprecated. Use agents.f instead. "
    "See spec/f-gents/MIGRATION.md",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from agents.f import Flow as Flux
from agents.f import FlowAgent
from agents.f import FlowConfig as FluxConfig
from agents.f import FlowState as FluxState
from agents.f import FlowEvent
from agents.f import FlowPipeline

__all__ = [
    "Flux",
    "FluxConfig",
    "FluxAgent",
    "FluxState",
    "FlowEvent",
    "FlowPipeline",
]
```

### 6.3 Update TownFlux

Check `impl/claude/agents/town/flux.py`:
- If it imports from `agents.flux`, update to import from `agents.f`
- Keep TownFlux implementation, just update imports
- Ensure TownFlux tests still pass

### 6.4 Update All Consumers

For each file that imports from `agents.flux`:
1. Update import to `agents.f`
2. Rename `Flux` -> `Flow`, `FluxConfig` -> `FlowConfig` if needed
3. Run tests to verify

---

## Phase 7: Add AGENTESE Paths

### 7.1 Check Existing AGENTESE Structure

```bash
# Find where self.* paths are registered
rg "self\." impl/claude/protocols/agentese/contexts/
ls impl/claude/protocols/agentese/contexts/
```

### 7.2 Register Flow Paths

In `impl/claude/protocols/agentese/contexts/self_.py` or create new `self_flow.py`:

```python
"""AGENTESE paths for self.flow.* context."""

from typing import Any, Callable
from agents.f import FlowState

# Path handlers for self.flow.*
FLOW_PATHS: dict[str, Callable] = {
    "self.flow.state": lambda ctx: getattr(ctx, "flow_state", FlowState.DORMANT),
    "self.flow.entropy": lambda ctx: getattr(ctx, "flow_entropy", 1.0),
    "self.flow.context": lambda ctx: getattr(ctx, "flow_context", []),
    "self.flow.modality": lambda ctx: getattr(ctx, "flow_modality", "chat"),
    "self.flow.turn": lambda ctx: getattr(ctx, "flow_turn", 0),
    "self.flow.tree": lambda ctx: getattr(ctx, "flow_tree", None),  # Research
    "self.flow.board": lambda ctx: getattr(ctx, "flow_board", None),  # Collab
}

def register_flow_paths(registry: dict) -> None:
    """Register all self.flow.* paths with the AGENTESE registry."""
    registry.update(FLOW_PATHS)
```

### 7.3 Wire Into AGENTESE

Find where paths are registered and add flow paths:
```bash
rg "register.*paths" impl/claude/protocols/agentese/
```

### 7.4 Test AGENTESE Integration

Create `impl/claude/protocols/agentese/_tests/test_flow_paths.py`:

```python
"""Tests for self.flow.* AGENTESE paths."""
import pytest
from agents.f import FlowState

class TestFlowPaths:
    def test_flow_state_path(self):
        """self.flow.state returns current FlowState."""
        # Test implementation
        pass

    def test_flow_entropy_path(self):
        """self.flow.entropy returns remaining budget."""
        pass

    def test_flow_modality_path(self):
        """self.flow.modality returns current modality."""
        pass
```

---

## Phase 8: Update Documentation

### 8.1 Update Skill Doc

Update `docs/skills/flux-agent.md`:
- Change title to "Flow Agent Skill" or rename file to `flow-agent.md`
- Update all imports from `agents.flux` to `agents.f`
- Add sections for Chat, Research, Collaboration modalities
- Update verification commands
- Keep reference to old flux for migration guidance

### 8.2 Update Systems Reference

In `docs/systems-reference.md`, update the Flux/Streaming entry:

```markdown
| **Flow** | F-gent substrate for chat, research, collaboration | `agents.f` |
```

### 8.3 Update CLAUDE.md

Verify the F-gent entry in CLAUDE.md shows:
```
| F | Fgents | Flow (chat, research, collaboration substrate) | `FLOW_POLYNOMIAL` |
```

### 8.4 Create Migration Guide (if not exists)

Check if `spec/f-gents/MIGRATION.md` exists. If not, create it documenting:
- Old Forge API -> New Flow API mapping
- Old `agents.flux` -> New `agents.f` migration
- Code examples for updating imports

---

## Phase 9: Clean Up Old References

### 9.1 Search for Old References

```bash
# Find remaining old references
rg "spec/agents/flux" .
rg "spec/c-gents/flux" .
rg -i "forge" spec/ docs/ --glob '!*archived*'
rg "agents\.flux" impl/claude/ --glob '!flux/__init__.py'
```

### 9.2 Update Cross-References

- Update any cross-references to point to `spec/f-gents/`
- Update `spec/c-gents/functor-catalog.md` if it has flux entry

### 9.3 Archive Old Specs (if they exist)

```bash
# Check if old specs exist
ls spec/agents/flux.md 2>/dev/null
ls spec/c-gents/flux.md 2>/dev/null

# If they exist, archive them
mkdir -p spec/f-gents-archived
# mv spec/agents/flux.md spec/f-gents-archived/flux-original.md
# mv spec/c-gents/flux.md spec/f-gents-archived/flux-functor.md
```

---

## Phase 10: Testing and Verification

### 10.1 Run All F-gent Tests

```bash
cd impl/claude
uv run pytest agents/f/_tests/ -v
```

Expected: 365+ tests pass

### 10.2 Run TownFlux Tests (if applicable)

```bash
uv run pytest agents/town/_tests/test_flux.py -v 2>/dev/null || echo "No TownFlux tests"
```

### 10.3 Verify Imports

```python
# Test new imports work
from agents.f import Flow, FlowConfig, FlowState
from agents.f.modalities.chat import ChatFlow, Turn
from agents.f.modalities.research import ResearchFlow, HypothesisTree
from agents.f.modalities.collaboration import CollaborationFlow, Blackboard

# Verify polynomial and operad
from agents.f import FLOW_POLYNOMIAL, FLOW_OPERAD, get_polynomial, get_operad

# Test compatibility shim warns (if created)
import warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    from agents.flux import Flux
    assert len(w) == 1
    assert "deprecated" in str(w[0].message).lower()
```

### 10.4 Create Integration Test

Create `impl/claude/agents/f/_tests/test_integration.py`:

```python
"""End-to-end integration tests for all three modalities."""
import pytest
from agents.f import Flow, FlowConfig

class MockAgent:
    name = "MockAgent"
    async def invoke(self, input):
        return f"processed: {input}"

@pytest.mark.asyncio
async def test_chat_modality_e2e():
    """Chat modality end-to-end test."""
    agent = MockAgent()
    chat = Flow.lift(agent, FlowConfig(modality="chat"))

    async def messages():
        yield "Hello"
        yield "How are you?"

    responses = []
    async for event in chat.start(messages()):
        if event.event_type == "output":
            responses.append(event.value)

    assert len(responses) == 2

@pytest.mark.asyncio
async def test_research_modality_e2e():
    """Research modality end-to-end test."""
    agent = MockAgent()
    research = Flow.lift(agent, FlowConfig(modality="research"))

    async def questions():
        yield "What is the meaning of life?"

    insights = []
    async for event in research.start(questions()):
        if event.event_type == "output":
            insights.append(event.value)

    assert len(insights) >= 1

@pytest.mark.asyncio
async def test_collaboration_modality_e2e():
    """Collaboration modality end-to-end test."""
    agents = {
        "agent_1": MockAgent(),
        "agent_2": MockAgent(),
    }
    collab = Flow.lift_multi(agents, FlowConfig(modality="collaboration"))

    async def problems():
        yield "Design a system"

    contributions = []
    async for event in collab.start(problems()):
        if event.event_type == "output":
            contributions.append(event.value)

    assert len(contributions) >= 1
```

---

## Acceptance Criteria (Phases 6-10) — UPDATED

**KEY INSIGHT**: `agents.flux` and `agents.f` are COMPLEMENTARY systems:
- `agents.flux` = Streaming functor (Flux[A] = AsyncIterator[A])
- `agents.f` = Conversational modalities (Chat, Research, Collaboration)

No migration/deprecation needed. Criteria updated:

- [x] AGENTESE `self.flow.*` paths registered and tested (21 tests)
- [x] NEW `docs/skills/flow-modalities.md` created (Chat/Research/Collaboration)
- [x] `docs/systems-reference.md` updated with F-gent Flow section
- [x] All 365+ F-gent tests pass
- [x] `flux-agent.md` kept as-is (different system)
- [N/A] Compatibility shim — not needed (different systems)
- [N/A] TownFlux migration — not needed (uses agents.flux correctly)
- [N/A] Cleanup/archival — not needed (different systems)

---

## Notes

- **Don't break TownFlux**: It's actively used. Update imports carefully.
- **Deprecation, not deletion**: Keep `agents.flux` as shim with warning.
- **Test incrementally**: Run tests after each phase.
- **Check existing patterns**: Look at how other AGENTESE paths are registered.

## Estimated Effort

| Phase | Effort |
|-------|--------|
| Phase 6 (Flux Migration) | 20 min |
| Phase 7 (AGENTESE) | 30 min |
| Phase 8 (Documentation) | 20 min |
| Phase 9 (Cleanup) | 15 min |
| Phase 10 (Testing) | 15 min |
| **Total** | ~1.5 hours |

---

## Quick Start

```bash
# 1. Verify current state
cd impl/claude
uv run pytest agents/f/_tests/ -v --tb=short

# 2. Start with Phase 6
rg -l "from agents.flux" impl/claude/

# 3. Work through phases sequentially
# Each phase builds on the previous
```
