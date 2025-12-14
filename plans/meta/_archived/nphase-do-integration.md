---
path: plans/meta/nphase-do-integration
status: active
progress: 0
importance: crown_jewel
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [plans/devex/cli-unification]
session_notes: |
  CROWN JEWEL: Deep integration of nphase compiler with kg do.

  Key operations: show forest, list trees, show tree, stream agent,
  check completeness, audit statuses, log milestone, show stats.

  Rhizome propagation from nphase-prompt-compiler development.
phase_ledger:
  PLAN: pending
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.75
  spent: 0.00
  returned: 0.00
---

# N-Phase Deep Integration: `kg do` + Forest + NPhase Compiler

> *"The prompt that grows prompts. The forest that tends itself."*

**AGENTESE Context**: `concept.nphase.*`, `time.forest.*`
**Status**: Active (0 tests)
**Principles**: Composable, Joy-Inducing, AGENTESE
**Cross-refs**: `protocols/nphase/`, `protocols/cli/intent/router.py`, `plans/_forest.md`

---

## Core Insight

The N-Phase Prompt Compiler generates structured prompts. The Forest Protocol manages multi-session plans. The Intent Router (`kg do`) provides natural language interface. **The rhizome propagation**: unite these three systems so that `kg do "show forest"` or `kg do "stream soul agent"` works seamlessly.

**The 8 Key Operations**:

| # | Operation | Intent Pattern | Description |
|---|-----------|----------------|-------------|
| 1 | show forest | "show forest", "forest health" | Display forest health summary |
| 2 | list trees | "list trees", "show plans" | List all plans with status |
| 3 | show tree | "show tree X", "detail X" | Deep view of single plan |
| 4 | stream agent | "stream X", "watch agent X" | Live agent execution stream |
| 5 | check completeness | "check stage", "audit phase" | Pre-generated completeness check |
| 6 | audit statuses | "audit", "rebuild statuses" | Sync statuses from impl/metrics |
| 7 | log milestone | "log milestone", "record" | One-line summary logging |
| 8 | show stats | "stats", "metrics" | Trees completed, progress, etc. |

---

## Implementation Phases

### Phase 1: Foundation (Wave 1)

**Goal**: Intent patterns, completeness auditor, milestone logger, forest stats.

**Components**:
- C1: IntentPatterns (Forest) - `protocols/cli/intent/router.py`
- C5: CompletenessAuditor - `protocols/nphase/auditor.py`
- C7: MilestoneLogger - `protocols/nphase/milestone.py`
- C8: ForestStats - `protocols/cli/handlers/forest.py`

**Exit Criteria**: `kg do "show forest"` recognized as forest intent.

### Phase 2: Forest Ops (Wave 2)

**Goal**: Forest commands and status reconciliation.

**Components**:
- C2: ForestCommands - `protocols/cli/intent/forest_ops.py`
- C6: StatusReconciler - `protocols/nphase/reconciler.py`

**Exit Criteria**: `kg do "audit statuses"` reconciles impl→plan.

### Phase 3: Streaming (Wave 3)

**Goal**: Agent stream view with turn-gent decision points.

**Components**:
- C3: AgentStreamView - `agents/i/reactive/streams/`
- C4: TurnGentDecisionUI - `agents/i/reactive/screens/`

**Exit Criteria**: `kg do "stream soul"` shows live execution with YIELD intercepts.

### Phase 4: Integration (Wave 4)

**Goal**: Unified `kg do` handler bringing it all together.

**Components**:
- C9: UnifiedDoHandler - `protocols/cli/intent/router.py`

**Exit Criteria**: All 8 operations work via `kg do`.

---

## Key Types / API

```python
# C1: Intent pattern extension
class IntentCategory(Enum):
    FOREST = "forest"  # NEW

INTENT_PATTERNS[IntentCategory.FOREST] = [
    r"\b(forest|trees?|plans?|status|health)\b",
    r"\b(show|list|audit|stream|check)\b",
]

# C5: Completeness auditor
@dataclass
class CompletenessReport:
    phase: str
    is_complete: bool
    missing: list[str]  # Missing minimum artifacts
    violations: list[str]  # Principle violations

class CompletenessAuditor:
    def audit_phase(self, project: ProjectDefinition, phase: str) -> CompletenessReport:
        ...

# C3: Agent stream view
class AgentStreamView:
    async def stream(self, agent_id: str) -> AsyncIterator[Turn]:
        ...

    def on_yield(self, turn: YieldTurn) -> None:
        """Handle YIELD turn - show decision UI."""
        ...
```

---

## Checkpoints

| CP | Name | Criteria |
|----|------|----------|
| CP1 | Intent Recognition | `kg do "show forest"` produces forest view |
| CP2 | Completeness Audit | `kg do "check phase"` validates current stage |
| CP3 | Agent Streaming | `kg do "stream soul"` shows live execution |
| CP4 | Full Integration | All 8 operations work via `kg do` |

---

## Resources

- **Prompt**: `prompts/nphase-do-deep-integration.md`
- **Definition**: `protocols/nphase/examples/do-integration.yaml`
- **Compile**: `kg nphase compile protocols/nphase/examples/do-integration.yaml`

---

## Cross-References

- **Spec**: `spec/protocols/agentese.md` (AGENTESE context system)
- **Plan**: `plans/meta/nphase-prompt-compiler` (prior work)
- **Plan**: `plans/devex/cli-unification` (enabled by this)
- **Impl**: `protocols/nphase/` (N-Phase Compiler)
- **Impl**: `protocols/cli/intent/router.py` (Intent Router)
- **Impl**: `protocols/cli/handlers/forest.py` (Forest Protocol)
