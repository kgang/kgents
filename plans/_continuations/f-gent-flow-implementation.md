---
plan: f-gent-flow-implementation
status: ready
priority: high
created: 2025-12-16
estimated_sessions: 3-4
dependencies: []
---

# F-gent Flow Implementation

## Context

The F-gent specification has been overhauled:
- **Old**: F-gent = "Forge" (artifact synthesis) - underutilized, overlapping
- **New**: F-gent = "Flow" (chat, research, collaboration substrate)

The spec is complete in `spec/f-gents/`. This continuation implements it.

## Relevant Specs

Read these FIRST before implementing:
- `spec/f-gents/README.md` - Core Flow spec (FlowPolynomial, FLOW_OPERAD)
- `spec/f-gents/chat.md` - Chat modality
- `spec/f-gents/research.md` - Tree of thought modality
- `spec/f-gents/collaboration.md` - Blackboard modality
- `spec/f-gents/MIGRATION.md` - Migration guide

## Phase 1: Remove Old Forge Implementation (if any exists)

### 1.1 Check for Forge Implementation
```bash
# Search for any Forge-related code
rg -l "Forge|forge" impl/claude/agents/
rg -l "ALO|alo" impl/claude/agents/
```

### 1.2 Remove Old F-gent Code
If `impl/claude/agents/f/` exists with Forge code:
```bash
# Archive it first
mv impl/claude/agents/f impl/claude/agents/_archived/f-forge
```

### 1.3 Clean Up Old Spec References
Update any files that reference the old Forge spec:
- Search for `spec/f-gents/forge.md`
- Search for `spec/f-gents/contracts.md`
- Search for `spec/f-gents/artifacts.md`
- Update to point to `spec/f-gents-archived/` or remove references

---

## Phase 2: Create F-gent (Flow) Implementation Structure

### 2.1 Create Directory Structure
```bash
mkdir -p impl/claude/agents/f
mkdir -p impl/claude/agents/f/modalities
mkdir -p impl/claude/agents/f/sources
mkdir -p impl/claude/agents/f/_tests
```

### 2.2 Create Core Files

**`impl/claude/agents/f/__init__.py`**:
```python
"""
F-gents: Flow Agents

The unified substrate for continuous agent interaction:
- Chat: Streaming conversation with context management
- Research: Tree of thought exploration
- Collaboration: Multi-agent blackboard patterns

See: spec/f-gents/README.md
"""

from agents.f.flow import Flow, FlowAgent
from agents.f.config import FlowConfig
from agents.f.state import FlowState
from agents.f.polynomial import FlowPolynomial
from agents.f.operad import FLOW_OPERAD
from agents.f.pipeline import FlowPipeline

__all__ = [
    "Flow",
    "FlowAgent",
    "FlowConfig",
    "FlowState",
    "FlowPolynomial",
    "FLOW_OPERAD",
    "FlowPipeline",
]
```

**`impl/claude/agents/f/state.py`**:
```python
"""Flow lifecycle states."""
from enum import Enum, auto

class FlowState(Enum):
    """Lifecycle states of a flow agent."""
    DORMANT = "dormant"       # Created, not started
    STREAMING = "streaming"   # Processing continuous input
    BRANCHING = "branching"   # Exploring alternatives (research)
    CONVERGING = "converging" # Merging branches (research)
    DRAINING = "draining"     # Source exhausted, flushing
    COLLAPSED = "collapsed"   # Entropy depleted or error
```

**`impl/claude/agents/f/config.py`**:
Implement FlowConfig from spec with all three modality configurations.

**`impl/claude/agents/f/polynomial.py`**:
Implement FlowPolynomial following PolyAgent pattern.

**`impl/claude/agents/f/operad.py`**:
Implement FLOW_OPERAD with all 13 operations.

**`impl/claude/agents/f/flow.py`**:
Core Flow class with `lift()`, `lift_multi()`, `start()`, `invoke()`.

**`impl/claude/agents/f/perturbation.py`**:
Perturbation handling - inject into stream, never bypass.

**`impl/claude/agents/f/pipeline.py`**:
FlowPipeline with `|` operator for composition.

---

## Phase 3: Implement Chat Modality

### 3.1 Create Chat Files

**`impl/claude/agents/f/modalities/chat.py`**:
- Context window management (SlidingContext, SummarizingContext)
- Turn protocol
- Token-level streaming
- System prompt handling

**`impl/claude/agents/f/modalities/context.py`**:
- Context strategies: sliding, summarize, forget
- Token counting
- Compression logic

### 3.2 Chat Tests

**`impl/claude/agents/f/_tests/test_chat.py`**:
- Test context overflow handling
- Test summarization trigger
- Test turn completion
- Test streaming output

---

## Phase 4: Implement Research Modality

### 4.1 Create Research Files

**`impl/claude/agents/f/modalities/research.py`**:
- Hypothesis tree structure
- Branching logic
- Pruning logic
- Merging strategies

**`impl/claude/agents/f/modalities/hypothesis.py`**:
- Hypothesis dataclass
- Evidence dataclass
- HypothesisTree class

### 4.2 Research Tests

**`impl/claude/agents/f/_tests/test_research.py`**:
- Test branching
- Test pruning threshold
- Test merge strategies
- Test exploration strategies (depth-first, breadth-first, best-first)

---

## Phase 5: Implement Collaboration Modality

### 5.1 Create Collaboration Files

**`impl/claude/agents/f/modalities/collaboration.py`**:
- Blackboard class
- Contribution ordering
- Consensus mechanisms

**`impl/claude/agents/f/modalities/blackboard.py`**:
- Blackboard dataclass
- Contribution dataclass
- AgentRole dataclass
- Permission enum

### 5.2 Collaboration Tests

**`impl/claude/agents/f/_tests/test_collaboration.py`**:
- Test round-robin ordering
- Test voting consensus
- Test moderator decisions
- Test contribution posting/reading

---

## Phase 6: Migrate Existing Flux Code

### 6.1 Identify Flux Locations
```bash
# Find all flux references
rg -l "from agents.flux" impl/claude/
rg -l "from agents.town.flux" impl/claude/
```

### 6.2 Create Compatibility Shim

**`impl/claude/agents/flux/__init__.py`**:
```python
"""Compatibility shim - flux is now agents.f"""
import warnings

warnings.warn(
    "agents.flux is deprecated. Use agents.f instead. "
    "See spec/f-gents/MIGRATION.md",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from agents.f import Flow as Flux
from agents.f import FlowConfig as FluxConfig
from agents.f import FlowAgent
from agents.f import FlowState as FluxState

__all__ = ["Flux", "FluxConfig", "FluxAgent", "FluxState"]
```

### 6.3 Update TownFlux

Update `impl/claude/agents/town/flux.py` to import from `agents.f`:
```python
from agents.f import FlowState, FlowConfig
# Keep TownFlux implementation, just update imports
```

### 6.4 Update All Consumers

For each file that imports from `agents.flux`:
1. Update import to `agents.f`
2. Rename `Flux` -> `Flow`, `FluxConfig` -> `FlowConfig`
3. Run tests to verify

---

## Phase 7: Add AGENTESE Paths

### 7.1 Register Flow Paths

In `impl/claude/protocols/agentese/contexts/self_.py` or new file:

```python
# self.flow.* paths
FLOW_PATHS = {
    "self.flow.state": lambda ctx: ctx.flow_state,
    "self.flow.entropy": lambda ctx: ctx.flow_entropy,
    "self.flow.context": lambda ctx: ctx.flow_context,
    "self.flow.modality": lambda ctx: ctx.flow_modality,
    "self.flow.turn": lambda ctx: ctx.flow_turn,
    "self.flow.tree": lambda ctx: ctx.flow_tree,
    "self.flow.board": lambda ctx: ctx.flow_board,
}
```

### 7.2 Test AGENTESE Integration

**`impl/claude/protocols/agentese/_tests/test_flow_paths.py`**:
- Test `self.flow.state` returns current FlowState
- Test `self.flow.entropy` returns remaining budget
- Test modality-specific paths

---

## Phase 8: Update Documentation

### 8.1 Update Skill Doc

Update `docs/skills/flux-agent.md`:
- Change title to "Flow Agent Skill"
- Update all imports to `agents.f`
- Add sections for Chat, Research, Collaboration modalities
- Update verification commands

### 8.2 Update Systems Reference

In `docs/systems-reference.md`, update Flux entry:
```markdown
| **Flow** | F-gent substrate for chat, research, collaboration | `agents.f` |
```

### 8.3 Add New Skill Docs (Optional)

Consider creating:
- `docs/skills/chat-flow.md`
- `docs/skills/research-flow.md`
- `docs/skills/collaboration-flow.md`

---

## Phase 9: Clean Up Old References

### 9.1 Search and Update

```bash
# Find remaining old references
rg "spec/agents/flux" .
rg "spec/c-gents/flux" .
rg "Forge|forge" spec/ docs/
```

### 9.2 Update or Remove

- Update cross-references to point to `spec/f-gents/`
- Remove or archive `spec/agents/flux.md` (if not already)
- Update `spec/c-gents/functor-catalog.md` flux entry

### 9.3 Archive Old Flux Specs

```bash
# If spec/agents/flux.md exists
mv spec/agents/flux.md spec/f-gents-archived/flux-original.md

# If spec/c-gents/flux.md exists
mv spec/c-gents/flux.md spec/f-gents-archived/flux-functor.md
```

---

## Phase 10: Testing and Verification

### 10.1 Run All Tests

```bash
cd impl/claude
uv run pytest agents/f/_tests/ -v
uv run pytest agents/town/_tests/test_flux.py -v  # TownFlux still works
```

### 10.2 Verify Imports

```python
# Test new imports work
from agents.f import Flow, FlowConfig, FlowState
from agents.f.modalities.chat import ChatFlow
from agents.f.modalities.research import ResearchFlow
from agents.f.modalities.collaboration import CollaborationFlow

# Test compatibility shim warns
from agents.flux import Flux  # Should warn
```

### 10.3 Integration Test

Create end-to-end test showing all three modalities:
```python
# Chat
chat = Flow.lift(agent, FlowConfig(modality="chat"))
async for response in chat.start(messages):
    print(response)

# Research
research = Flow.lift(agent, FlowConfig(modality="research"))
async for insight in research.start([question]):
    print(insight)

# Collaboration
collab = Flow.lift_multi(agents, FlowConfig(modality="collaboration"))
async for contribution in collab.start([problem]):
    print(contribution)
```

---

## Acceptance Criteria

- [ ] Old Forge implementation removed/archived
- [ ] `agents.f` module exists with Flow, FlowConfig, FlowState
- [ ] FlowPolynomial implemented with 6 states
- [ ] FLOW_OPERAD implemented with 13 operations
- [ ] Chat modality: context management, turns, streaming
- [ ] Research modality: branching, pruning, merging
- [ ] Collaboration modality: blackboard, roles, consensus
- [ ] Compatibility shim in `agents.flux` with deprecation warning
- [ ] TownFlux updated to use new imports
- [ ] AGENTESE `self.flow.*` paths registered
- [ ] All tests pass
- [ ] Documentation updated

---

## Notes

- **Don't break TownFlux**: It's actively used. Update imports only.
- **Deprecation, not deletion**: Keep `agents.flux` as shim for now.
- **Follow existing patterns**: Look at `agents/poly/` for PolyAgent patterns.
- **Test incrementally**: Run tests after each phase.

## Estimated Effort

| Phase | Effort |
|-------|--------|
| Phase 1 (Cleanup) | 0.5 session |
| Phase 2 (Structure) | 0.5 session |
| Phase 3 (Chat) | 1 session |
| Phase 4 (Research) | 1 session |
| Phase 5 (Collab) | 1 session |
| Phase 6-10 (Migration) | 1 session |
| **Total** | 5 sessions |

Can parallelize Phases 3-5 if working with swarm.
