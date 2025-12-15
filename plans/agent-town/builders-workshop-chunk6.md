---
path: agent-town/builders-workshop-chunk6
status: complete
progress: 100
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town/builders-workshop
  - agent-town/builders-workshop-chunk7
session_notes: |
  COMPLETE: WorkshopEnvironment implemented with 93 passing tests.
  Key patterns: task routing (keyword MVP), phase-archetype mapping,
  event streaming via EventBus, dual polynomial (citizen+builder).
  Ready for Chunk 7 (WorkshopFlux streaming).
phase_ledger:
  PLAN: touched
  RESEARCH: touched  # Studied TownEnvironment, DialogueEngine, TownFlux
  DEVELOP: touched  # All types defined
  STRATEGIZE: skipped  # Strategy set in parent plan
  CROSS-SYNERGIZE: touched  # Reused EventBus, Builder patterns
  IMPLEMENT: touched  # workshop.py created
  QA: touched  # mypy clean
  TEST: touched  # 93 tests passing
  EDUCATE: skipped  # Doc-only deferred
  MEASURE: deferred
  REFLECT: touched
entropy:
  planned: 0.10
  spent: 0.08
  remaining: 0.02
---

# Builder's Workshop: Chunk 6 - WorkshopEnvironment

> *"The workshop is not a place but a coordination protocol. Builders don't inhabit space—they inhabit tasks."*

**AGENTESE Context**: `world.workshop.*`
**Phase**: RESEARCH → DEVELOP → IMPLEMENT → TEST
**Parent Plan**: `plans/agent-town/builders-workshop.md`
**Heritage**:
- `impl/claude/agents/town/environment.py` (TownEnvironment base)
- `impl/claude/agents/town/builders/` (Builder classes from Chunk 5)
- `impl/claude/agents/town/dialogue.py` (DialogueEngine)
- `impl/claude/agents/town/flux.py` (TownFlux streaming)

---

## ATTACH

/hydrate plans/agent-town/builders-workshop.md

---

## Prior Session Summary (Chunks 4-5)

**Completed**:
- Chunk 4: `BUILDER_POLYNOMIAL` with 6 phases (71 tests)
- Chunk 5: 5 Builder classes (Sage, Spark, Steady, Scout, Sync) extending Citizen (132 tests total)

**Key Files Created**:
```
impl/claude/agents/town/builders/
├── __init__.py           # Full exports
├── polynomial.py         # BUILDER_POLYNOMIAL ✓
├── base.py               # Builder(Citizen) ✓
├── cosmotechnics.py      # 5 cosmotechnics ✓
├── voice.py              # 5 voice patterns ✓
├── sage.py               # create_sage() ✓
├── spark.py              # create_spark() ✓
├── steady.py             # create_steady() ✓
├── scout.py              # create_scout() ✓
├── sync.py               # create_sync() ✓
└── _tests/
    ├── test_builder_polynomial.py  # 71 tests ✓
    └── test_builders.py            # 61 tests ✓
```

---

## This Session: WorkshopEnvironment (Chunk 6)

### Goal

Create the collaborative workshop environment where the 5 builders work together on tasks. The environment orchestrates task distribution, tracks progress, and enables builder collaboration.

### Core Concepts

| Concept | Description | Implementation |
|---------|-------------|----------------|
| **Workshop** | A collaborative task execution context | `WorkshopEnvironment` |
| **Task** | A unit of work to be completed | `WorkshopTask` dataclass |
| **Plan** | How a task is distributed to builders | `WorkshopPlan` |
| **Artifact** | Output produced during work | `WorkshopArtifact` |
| **Event** | Observable workshop activity | `WorkshopEvent` |

### Research Questions

1. How does `TownEnvironment` work? (base class patterns)
2. How does `DialogueEngine` integrate for builder conversations?
3. How does task routing work? (keyword → builder, or smarter?)
4. What events should the workshop emit for observability?
5. How do builders hand off work to each other?

### Deliverables

| Artifact | Location | Tests |
|----------|----------|-------|
| `WorkshopTask` dataclass | `agents/town/workshop.py` | 5+ |
| `WorkshopPlan` dataclass | `agents/town/workshop.py` | 5+ |
| `WorkshopArtifact` dataclass | `agents/town/workshop.py` | 5+ |
| `WorkshopEvent` types | `agents/town/workshop.py` | 5+ |
| `WorkshopState` dataclass | `agents/town/workshop.py` | 5+ |
| `WorkshopEnvironment` class | `agents/town/workshop.py` | 25+ |
| Integration tests | `agents/town/_tests/test_workshop.py` | 15+ |

**Total target: 65+ tests**

---

## Workshop State Machine

```
                    ┌─────────────┐
                    │    IDLE     │
                    └──────┬──────┘
                           │ assign_task()
                           ▼
                    ┌─────────────┐
              ┌────▶│  EXPLORING  │◀────┐
              │     └──────┬──────┘     │
              │            │ plan_ready │ need_more_research
              │            ▼            │
              │     ┌─────────────┐     │
              │     │  DESIGNING  │─────┘
              │     └──────┬──────┘
              │            │ design_approved
              │            ▼
              │     ┌─────────────┐
              │     │ PROTOTYPING │
              │     └──────┬──────┘
              │            │ prototype_works
              │            ▼
              │     ┌─────────────┐
              │     │  REFINING   │
              │     └──────┬──────┘
              │            │ quality_approved
              │            ▼
              │     ┌─────────────┐
              └─────│ INTEGRATING │
        (new task)  └──────┬──────┘
                           │ complete()
                           ▼
                    ┌─────────────┐
                    │  COMPLETE   │
                    └─────────────┘
```

---

## Proposed API

### WorkshopTask

```python
@dataclass(frozen=True)
class WorkshopTask:
    """A unit of work for the workshop."""

    id: str
    description: str
    priority: int = 1  # 1=low, 2=medium, 3=high
    context: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, description: str, priority: int = 1, **context: Any) -> WorkshopTask:
        """Factory for creating tasks."""
        return cls(
            id=str(uuid4())[:8],
            description=description,
            priority=priority,
            context=context,
        )
```

### WorkshopPlan

```python
@dataclass
class WorkshopPlan:
    """How a task is distributed across builders."""

    task: WorkshopTask
    assignments: dict[str, list[str]]  # builder_archetype -> subtasks
    estimated_phases: list[BuilderPhase]
    lead_builder: str  # Who coordinates

    def get_subtasks_for(self, archetype: str) -> list[str]:
        """Get subtasks assigned to a builder archetype."""
        return self.assignments.get(archetype, [])
```

### WorkshopState

```python
@dataclass
class WorkshopState:
    """Current state of the workshop."""

    phase: WorkshopPhase
    builders: tuple[Builder, ...]
    active_task: WorkshopTask | None
    plan: WorkshopPlan | None
    artifacts: list[WorkshopArtifact]
    events: list[WorkshopEvent]

    @property
    def is_idle(self) -> bool:
        return self.phase == WorkshopPhase.IDLE

    @property
    def active_builder(self) -> Builder | None:
        """The builder currently working (based on phase)."""
        phase_to_archetype = {
            WorkshopPhase.EXPLORING: "Scout",
            WorkshopPhase.DESIGNING: "Sage",
            WorkshopPhase.PROTOTYPING: "Spark",
            WorkshopPhase.REFINING: "Steady",
            WorkshopPhase.INTEGRATING: "Sync",
        }
        archetype = phase_to_archetype.get(self.phase)
        if archetype:
            return next((b for b in self.builders if b.archetype == archetype), None)
        return None
```

### WorkshopEnvironment

```python
class WorkshopEnvironment:
    """
    The collaborative workshop where builders work together.

    This is the coordination layer that:
    - Accepts tasks from users
    - Creates plans for how to execute tasks
    - Routes work to appropriate builders
    - Tracks progress and artifacts
    - Emits events for observability
    """

    def __init__(
        self,
        builders: tuple[Builder, ...] | None = None,
        dialogue_engine: DialogueEngine | None = None,
    ) -> None:
        """Initialize workshop with builders."""
        ...

    @property
    def state(self) -> WorkshopState:
        """Current workshop state."""
        ...

    async def assign_task(self, task: str | WorkshopTask, priority: int = 1) -> WorkshopPlan:
        """
        Assign a task to the workshop.

        Creates a plan and begins execution with Scout exploring.
        """
        ...

    async def advance(self) -> WorkshopEvent:
        """
        Advance the workshop by one step.

        This triggers the current active builder to work,
        potentially producing artifacts or triggering handoffs.
        """
        ...

    async def handoff(self, from_builder: str, to_builder: str, artifact: Any = None) -> WorkshopEvent:
        """
        Explicit handoff between builders.
        """
        ...

    async def complete(self, summary: str = "") -> WorkshopEvent:
        """Mark the current task as complete."""
        ...

    def get_builder(self, archetype: str) -> Builder | None:
        """Get a builder by archetype name."""
        ...

    def observe(self) -> AsyncIterator[WorkshopEvent]:
        """Stream workshop events."""
        ...

    def manifest(self, lod: int = 0) -> dict[str, Any]:
        """Manifest workshop state at Level of Detail."""
        ...
```

---

## Workshop Events

```python
class WorkshopEventType(Enum):
    """Types of workshop events."""
    TASK_ASSIGNED = auto()
    PLAN_CREATED = auto()
    PHASE_STARTED = auto()
    PHASE_COMPLETED = auto()
    HANDOFF = auto()
    ARTIFACT_PRODUCED = auto()
    USER_QUERY = auto()
    USER_RESPONSE = auto()
    TASK_COMPLETED = auto()
    ERROR = auto()

@dataclass
class WorkshopEvent:
    """An observable workshop event."""
    type: WorkshopEventType
    timestamp: datetime
    builder: str | None  # Which builder triggered
    phase: WorkshopPhase
    message: str
    artifact: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

---

## Task Routing Strategy

For MVP, use keyword-based routing:

```python
KEYWORD_ROUTING = {
    "research": "Scout",
    "find": "Scout",
    "explore": "Scout",
    "design": "Sage",
    "architect": "Sage",
    "plan": "Sage",
    "prototype": "Spark",
    "experiment": "Spark",
    "try": "Spark",
    "test": "Steady",
    "polish": "Steady",
    "refine": "Steady",
    "integrate": "Sync",
    "coordinate": "Sync",
    "merge": "Sync",
}

def route_task(task: WorkshopTask) -> str:
    """Determine which builder should lead based on task description."""
    description_lower = task.description.lower()
    for keyword, archetype in KEYWORD_ROUTING.items():
        if keyword in description_lower:
            return archetype
    # Default: Scout explores first
    return "Scout"
```

---

## Test Categories

1. **Task creation tests**: WorkshopTask factory, validation
2. **Plan creation tests**: Task → Plan mapping
3. **State tests**: WorkshopState properties, phase tracking
4. **Environment creation tests**: Default builders, custom builders
5. **Task assignment tests**: assign_task() creates plan, starts exploration
6. **Advance tests**: advance() moves through phases correctly
7. **Handoff tests**: Explicit handoffs between builders
8. **Completion tests**: complete() produces final artifact
9. **Event tests**: Events emitted correctly
10. **Keyword routing tests**: Task routing by keywords
11. **Integration tests**: Full task lifecycle

---

## Exit Criteria

- [ ] `WorkshopTask`, `WorkshopPlan`, `WorkshopArtifact`, `WorkshopEvent` dataclasses
- [ ] `WorkshopPhase` enum (IDLE, EXPLORING, DESIGNING, PROTOTYPING, REFINING, INTEGRATING, COMPLETE)
- [ ] `WorkshopState` dataclass with properties
- [ ] `WorkshopEnvironment` class with full API
- [ ] Keyword-based task routing (MVP)
- [ ] Event streaming via `observe()`
- [ ] 65+ tests passing
- [ ] Mypy clean
- [ ] Integration with existing Builder classes

---

## Phase: RESEARCH

<details>
<summary>Expand if PHASE=RESEARCH</summary>

### Mission
Understand TownEnvironment and DialogueEngine patterns before implementing workshop.

### Actions
1. Read `impl/claude/agents/town/environment.py` (if exists, or find equivalent)
2. Read `impl/claude/agents/town/dialogue.py` (DialogueEngine)
3. Check how existing Town tests structure environment tests
4. Review `impl/claude/agents/town/flux.py` for streaming patterns

### Exit Criteria
- [ ] TownEnvironment patterns understood (or decision to build fresh)
- [ ] DialogueEngine integration approach defined
- [ ] Event streaming pattern chosen
- [ ] Test structure decided

### Minimum Artifact
Design decision documented in session notes.

### Continuation
On completion: `[DEVELOP]`

</details>

---

## Phase: DEVELOP

<details>
<summary>Expand if PHASE=DEVELOP</summary>

### Mission
Design the Workshop API and type signatures.

### Actions
1. Define `WorkshopPhase` enum
2. Define `WorkshopTask`, `WorkshopPlan`, `WorkshopArtifact`, `WorkshopEvent` dataclasses
3. Define `WorkshopState` dataclass
4. Define `WorkshopEnvironment` class signature
5. Plan test structure

### Exit Criteria
- [ ] All type signatures defined
- [ ] Event types defined
- [ ] Keyword routing strategy defined
- [ ] Test categories planned

### Minimum Artifact
Type stubs in `workshop.py`.

### Continuation
On completion: `[IMPLEMENT]`

</details>

---

## Phase: IMPLEMENT

<details>
<summary>Expand if PHASE=IMPLEMENT</summary>

### Mission
Write the full WorkshopEnvironment implementation.

### Actions
1. Create `agents/town/workshop.py` with all types
2. Implement `WorkshopEnvironment` class
3. Implement keyword routing
4. Implement event streaming
5. Wire up DialogueEngine (if applicable)
6. Update `agents/town/__init__.py` to export workshop

### Exit Criteria
- [ ] All files created
- [ ] No mypy errors
- [ ] Imports work from `agents.town`

### Minimum Artifact
Working workshop that can assign and execute tasks.

### Continuation
On completion: `[TEST]`

</details>

---

## Phase: TEST

<details>
<summary>Expand if PHASE=TEST</summary>

### Mission
Verify workshop correctness with comprehensive tests.

### Actions
1. Create `agents/town/_tests/test_workshop.py`
2. Test all dataclasses
3. Test environment creation
4. Test task assignment and planning
5. Test phase transitions
6. Test handoffs
7. Test event streaming
8. Test full task lifecycle

### Exit Criteria
- [ ] 65+ tests passing
- [ ] All test categories covered
- [ ] No regressions in existing town tests

### Minimum Artifact
Test file with passing tests.

### Continuation
On completion: `[REFLECT]`

</details>

---

## Phase: REFLECT

<details>
<summary>Expand if PHASE=REFLECT</summary>

### Mission
Document learnings and prepare for Chunk 7 (WorkshopFlux).

### Actions
1. Update `builders-workshop.md` session_notes
2. Add learnings to `plans/meta.md`
3. Update chunk6 status to complete
4. Identify what Chunk 7 (WorkshopFlux) needs

### Exit Criteria
- [ ] Parent plan updated with progress
- [ ] Learnings captured
- [ ] Ready for Chunk 7

### Minimum Artifact
Updated session_notes in parent plan.

### Continuation
`[COMPLETE]` - Chunk 6 done.

</details>

---

## Shared Context

### File Map

| Path | Lines | Purpose |
|------|-------|---------|
| `agents/town/builders/` | ~1200 | Builder classes (Chunk 4-5) |
| `agents/town/citizen.py` | ~690 | Citizen base class |
| `agents/town/polynomial.py` | ~400 | CitizenPolynomial |
| `agents/town/dialogue.py` | ~??? | DialogueEngine |
| `agents/town/flux.py` | ~??? | TownFlux streaming |

### Import Pattern

```python
from agents.town.builders import (
    Builder,
    BuilderPhase,
    BuilderInput,
    BuilderOutput,
    BUILDER_POLYNOMIAL,
    create_sage,
    create_spark,
    create_steady,
    create_scout,
    create_sync,
)
from agents.town.citizen import Citizen, Eigenvectors
```

### Existing Town Patterns to Reuse

From `agents/town/`:
- `TownEnvironment` (if exists) for base patterns
- `DialogueEngine` for builder conversations
- `TownFlux` for streaming patterns
- Event types and structures

---

## Phase Accountability

| Phase | Status | Artifact |
|-------|--------|----------|
| PLAN | touched | This document |
| RESEARCH | touched | Studied TownEnvironment, DialogueEngine, TownFlux, EventBus |
| DEVELOP | touched | All types defined in workshop.py |
| STRATEGIZE | skipped | Strategy set in parent plan |
| CROSS-SYNERGIZE | touched | Reused EventBus, Builder polynomial patterns |
| IMPLEMENT | touched | agents/town/workshop.py (750+ lines) |
| QA | touched | mypy clean |
| TEST | touched | 93 tests passing |
| EDUCATE | skipped | Doc-only deferred |
| MEASURE | deferred | - |
| REFLECT | touched | Learnings captured |

---

*"The workshop coordinates; it does not command. Builders choose their rhythm within the plan."*
