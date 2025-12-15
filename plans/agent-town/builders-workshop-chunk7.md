---
path: agent-town/builders-workshop-chunk7
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town/builders-workshop
  - agent-town/builders-workshop-chunk8
session_notes: |
  CONTINUATION from Chunk 6 (WorkshopEnvironment complete, 93 tests).
  Now implementing WorkshopFlux - streaming execution layer.
phase_ledger:
  PLAN: touched
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: skipped  # Strategy set in parent plan
  CROSS-SYNERGIZE: pending  # TownFlux, DialogueEngine patterns
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: skipped  # Doc-only deferred
  MEASURE: deferred
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.0
  remaining: 0.10
---

# Builder's Workshop: Chunk 7 - WorkshopFlux

> *"The flux is not just time—it is expenditure. Each phase accumulates artifacts that must be integrated."*

**AGENTESE Context**: `world.workshop.flux.*`
**Phase**: RESEARCH → DEVELOP → IMPLEMENT → TEST
**Parent Plan**: `plans/agent-town/builders-workshop.md`
**Heritage**:
- `impl/claude/agents/town/flux.py` (TownFlux - primary pattern)
- `impl/claude/agents/town/workshop.py` (WorkshopEnvironment from Chunk 6)
- `impl/claude/agents/town/dialogue_engine.py` (LLM dialogue generation)
- `impl/claude/agents/town/event_bus.py` (EventBus for streaming)

---

## ATTACH

/hydrate plans/agent-town/builders-workshop.md

---

## Prior Session Summary (Chunks 4-6)

**Completed**:
- Chunk 4: `BUILDER_POLYNOMIAL` with 6 phases (71 tests)
- Chunk 5: 5 Builder classes (Sage, Spark, Steady, Scout, Sync) extending Citizen (132 tests)
- Chunk 6: `WorkshopEnvironment` with task routing, handoffs, events (93 tests)

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

impl/claude/agents/town/
└── workshop.py           # WorkshopEnvironment ✓ (93 tests)
```

**Total tests so far**: 225 (71 + 61 + 93)

---

## This Session: WorkshopFlux (Chunk 7)

### Goal

Create the streaming execution layer that runs workshop tasks as an async event stream. WorkshopFlux lifts WorkshopEnvironment into a continuous simulation, similar to how TownFlux lifts TownEnvironment.

### Core Concepts

| Concept | Description | Implementation |
|---------|-------------|----------------|
| **Flux** | Async stream of workshop events | `WorkshopFlux` |
| **Step** | One unit of work execution | `flux.step()` → yields events |
| **Run** | Execute task to completion | `flux.run()` → async iterator |
| **Perturbation** | External injection into flux | `flux.perturb()` |
| **Dialogue** | LLM-backed builder speech | Integration with DialogueEngine |

### Research Questions

1. How does `TownFlux` structure its `step()` method? (event generation pattern)
2. How does `TownFlux` integrate with `DialogueEngine`? (LLM dialogue in flux)
3. How does `TownFlux.perturb()` work? (perturbation principle)
4. What metrics does `TownFlux` track? (tokens, events, drama)
5. How should WorkshopFlux handle task completion vs continuous running?

### Deliverables

| Artifact | Location | Tests |
|----------|----------|-------|
| `WorkshopFlux` class | `agents/town/workshop.py` | 40+ |
| `step()` method | yields WorkshopEvents | 10+ |
| `run()` method | async iterator to completion | 10+ |
| `perturb()` method | inject events | 5+ |
| DialogueEngine integration | LLM builder speech | 10+ |
| Metrics tracking | tokens, artifacts, phases | 5+ |

**Total target: 80+ new tests** (total would be ~300+)

---

## WorkshopFlux State Machine

```
                    ┌─────────────┐
                    │    IDLE     │ ◀──────────────────┐
                    └──────┬──────┘                    │
                           │ start(task)              │ complete() or
                           ▼                          │ task finished
                    ┌─────────────┐                    │
              ┌────▶│   RUNNING   │────────────────────┘
              │     └──────┬──────┘
              │            │ step()
              │            ▼
              │     ┌─────────────┐
              │     │   WORKING   │ (yields events)
              │     └──────┬──────┘
              │            │ phase complete
              │            ▼
              │     ┌─────────────┐
              └─────│  ADVANCING  │ (handoff to next builder)
                    └─────────────┘
```

---

## Proposed API

### WorkshopFlux

```python
class WorkshopFlux:
    """
    Workshop execution as async event stream.

    Lifts WorkshopEnvironment into a continuous flux of events.
    Similar to TownFlux but task-centric rather than time-centric.

    From Bataille: The flux is expenditure.
    Each phase accumulates artifacts that must be integrated.
    """

    def __init__(
        self,
        workshop: WorkshopEnvironment,
        dialogue_engine: CitizenDialogueEngine | None = None,
        seed: int | None = None,
        auto_advance: bool = True,
        max_steps_per_phase: int = 5,
    ) -> None:
        """
        Initialize workshop flux.

        Args:
            workshop: The WorkshopEnvironment to execute.
            dialogue_engine: Optional LLM dialogue for builder speech.
            seed: Random seed for reproducibility.
            auto_advance: If True, automatically advance phases.
            max_steps_per_phase: Max work steps before auto-advancing.
        """
        ...

    @property
    def is_running(self) -> bool:
        """Check if flux is currently executing a task."""
        ...

    @property
    def current_phase(self) -> WorkshopPhase:
        """Current workshop phase."""
        ...

    @property
    def active_builder(self) -> Builder | None:
        """Currently active builder."""
        ...

    async def start(self, task: str | WorkshopTask, priority: int = 1) -> WorkshopPlan:
        """
        Start executing a task.

        Assigns task to workshop and prepares for streaming execution.
        """
        ...

    async def step(self) -> AsyncIterator[WorkshopEvent]:
        """
        Execute one step and yield events.

        A step involves:
        1. Active builder doing work
        2. Possibly generating dialogue (if engine available)
        3. Checking if phase should advance
        4. Emitting events for observability
        """
        ...

    async def run(self) -> AsyncIterator[WorkshopEvent]:
        """
        Run task to completion, yielding events.

        Continuously calls step() until task is complete.
        """
        ...

    async def perturb(
        self,
        action: str,
        builder: str | None = None,
        artifact: Any = None,
    ) -> WorkshopEvent:
        """
        Inject a perturbation into the flux.

        Perturbation Principle: inject events, never bypass state.

        Actions:
        - "advance": Force phase advancement
        - "handoff": Explicit handoff to builder
        - "complete": Force task completion
        - "inject_artifact": Add artifact to current phase
        """
        ...

    def get_status(self) -> dict[str, Any]:
        """Get current flux status including metrics."""
        ...

    def get_metrics(self) -> WorkshopMetrics:
        """Get execution metrics."""
        ...
```

### WorkshopMetrics

```python
@dataclass
class WorkshopMetrics:
    """Metrics tracked during workshop execution."""

    total_steps: int = 0
    total_events: int = 0
    total_tokens: int = 0
    dialogue_tokens: int = 0
    artifacts_produced: int = 0
    phases_completed: int = 0
    handoffs: int = 0
    perturbations: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration_seconds(self) -> float:
        """Execution duration in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    @property
    def events_per_second(self) -> float:
        """Event generation rate."""
        if self.duration_seconds == 0:
            return 0.0
        return self.total_events / self.duration_seconds
```

### WorkshopDialogueContext

```python
@dataclass
class WorkshopDialogueContext:
    """Context for builder dialogue generation."""

    task: WorkshopTask
    phase: WorkshopPhase
    builder: Builder
    artifacts_so_far: list[WorkshopArtifact]
    recent_events: list[str]
    step_count: int

    def to_prompt_context(self) -> str:
        """Render as prompt context for dialogue generation."""
        ...
```

---

## Dialogue Integration Strategy

Builders should speak during work. Integration with DialogueEngine:

```python
# In WorkshopFlux.step()
async def _generate_builder_dialogue(
    self,
    builder: Builder,
    action: str,  # "start_work", "continue", "handoff", "complete"
) -> DialogueResult | None:
    """Generate dialogue for builder action."""
    if self._dialogue_engine is None:
        return None

    # Create phantom listener (workshop itself or next builder)
    listener = self._get_dialogue_listener(action)

    return await self._dialogue_engine.generate(
        speaker=builder,
        listener=listener,
        operation=f"workshop_{action}",
        phase=self._map_workshop_to_town_phase(),
        recent_events=self._recent_events[-3:],
    )
```

### Dialogue Templates (for template fallback)

```python
WORKSHOP_DIALOGUE_TEMPLATES = {
    "Scout": {
        "start_work": [
            "Let me see what we're working with here...",
            "I'll start by exploring the landscape.",
            "Time to scout out the possibilities.",
        ],
        "continue": [
            "I found something interesting...",
            "There's more to discover here.",
            "Following this thread...",
        ],
        "handoff": [
            "I've mapped the territory. Over to you, {next_builder}.",
            "Here's what I found. {next_builder}, your turn.",
        ],
    },
    "Sage": {
        "start_work": [
            "Have we considered the architecture here?",
            "Let me think through the structure...",
            "The design should account for...",
        ],
        # ... etc
    },
    # ... other archetypes
}
```

---

## Test Categories

1. **Flux creation tests**: WorkshopFlux initialization
2. **Start tests**: start() creates plan, begins execution
3. **Step tests**: step() yields events, advances work
4. **Run tests**: run() completes task, yields all events
5. **Perturbation tests**: perturb() injects events correctly
6. **Dialogue tests**: Builder dialogue generation
7. **Metrics tests**: Metrics tracking accuracy
8. **Auto-advance tests**: Phase advancement triggers
9. **Integration tests**: Full task execution with dialogue
10. **Edge case tests**: Empty tasks, single-phase tasks, etc.

---

## Exit Criteria

- [ ] `WorkshopFlux` class with full API
- [ ] `step()` yields events correctly
- [ ] `run()` executes task to completion
- [ ] `perturb()` follows perturbation principle
- [ ] `WorkshopMetrics` tracks execution data
- [ ] DialogueEngine integration (optional, graceful degradation)
- [ ] Workshop dialogue templates for fallback
- [ ] 80+ new tests passing
- [ ] Mypy clean
- [ ] Integration with existing WorkshopEnvironment

---

## Phase: RESEARCH

<details>
<summary>Expand if PHASE=RESEARCH</summary>

### Mission
Understand TownFlux patterns before implementing WorkshopFlux.

### Actions
1. Read `impl/claude/agents/town/flux.py` deeply (TownFlux.step(), perturb())
2. Read `impl/claude/agents/town/dialogue_engine.py` (integration pattern)
3. Study how TownFlux tracks metrics
4. Understand perturbation principle implementation
5. Check dialogue template patterns in `dialogue_voice.py`

### Exit Criteria
- [ ] TownFlux.step() pattern understood
- [ ] DialogueEngine integration approach defined
- [ ] Metrics tracking strategy decided
- [ ] Perturbation implementation clear

### Minimum Artifact
Design notes in session_notes.

### Continuation
On completion: `[DEVELOP]`

</details>

---

## Phase: DEVELOP

<details>
<summary>Expand if PHASE=DEVELOP</summary>

### Mission
Design WorkshopFlux API and type signatures.

### Actions
1. Define `WorkshopMetrics` dataclass
2. Define `WorkshopDialogueContext` dataclass
3. Define `WorkshopFlux` class signature
4. Plan dialogue template structure
5. Design step() event generation logic

### Exit Criteria
- [ ] All type signatures defined
- [ ] Event generation logic planned
- [ ] Dialogue integration designed
- [ ] Test categories mapped

### Minimum Artifact
Type stubs added to workshop.py.

### Continuation
On completion: `[IMPLEMENT]`

</details>

---

## Phase: IMPLEMENT

<details>
<summary>Expand if PHASE=IMPLEMENT</summary>

### Mission
Write the full WorkshopFlux implementation.

### Actions
1. Add `WorkshopMetrics` to `workshop.py`
2. Add `WorkshopDialogueContext` to `workshop.py`
3. Implement `WorkshopFlux` class
4. Implement `step()` with event generation
5. Implement `run()` as async iterator
6. Implement `perturb()` following perturbation principle
7. Add dialogue templates for builders
8. Wire DialogueEngine integration

### Exit Criteria
- [ ] All code written
- [ ] No mypy errors
- [ ] Imports work

### Minimum Artifact
Working WorkshopFlux that can execute tasks.

### Continuation
On completion: `[TEST]`

</details>

---

## Phase: TEST

<details>
<summary>Expand if PHASE=TEST</summary>

### Mission
Verify WorkshopFlux with comprehensive tests.

### Actions
1. Add flux tests to `test_workshop.py` or create `test_workshop_flux.py`
2. Test flux creation
3. Test start/step/run lifecycle
4. Test perturbation
5. Test dialogue integration (mock + real)
6. Test metrics tracking
7. Test edge cases
8. Run full integration tests

### Exit Criteria
- [ ] 80+ new tests passing
- [ ] All test categories covered
- [ ] No regressions

### Minimum Artifact
Passing test suite.

### Continuation
On completion: `[REFLECT]`

</details>

---

## Phase: REFLECT

<details>
<summary>Expand if PHASE=REFLECT</summary>

### Mission
Document learnings and prepare for Chunk 8.

### Actions
1. Update `builders-workshop.md` progress
2. Add learnings to `plans/meta.md`
3. Update chunk7 status to complete
4. Identify Chunk 8 scope (Web UI integration? API endpoints?)

### Exit Criteria
- [ ] Parent plan updated
- [ ] Learnings captured
- [ ] Ready for Chunk 8

### Minimum Artifact
Updated session_notes.

### Continuation
`[COMPLETE]` - Chunk 7 done.

</details>

---

## Shared Context

### File Map

| Path | Lines | Purpose |
|------|-------|---------|
| `agents/town/workshop.py` | ~750 | WorkshopEnvironment (Chunk 6) |
| `agents/town/flux.py` | ~870 | TownFlux (reference) |
| `agents/town/dialogue_engine.py` | ~715 | DialogueEngine (reference) |
| `agents/town/dialogue_voice.py` | ~??? | Voice templates |
| `agents/town/builders/` | ~1200 | Builder classes (Chunks 4-5) |

### Import Pattern

```python
from agents.town.workshop import (
    WorkshopEnvironment,
    WorkshopPhase,
    WorkshopEvent,
    WorkshopEventType,
    WorkshopTask,
    WorkshopPlan,
    WorkshopArtifact,
    WorkshopState,
    WorkshopFlux,  # NEW in Chunk 7
    WorkshopMetrics,  # NEW in Chunk 7
    create_workshop,
)
from agents.town.dialogue_engine import (
    CitizenDialogueEngine,
    MockLLMClient,
    DialogueResult,
)
from agents.town.builders import (
    Builder,
    BuilderPhase,
    create_sage,
    create_scout,
    create_spark,
    create_steady,
    create_sync,
)
```

### Key Patterns from TownFlux to Reuse

1. **step() as async generator**: `async def step(self) -> AsyncIterator[TownEvent]`
2. **Perturbation principle**: `perturb()` injects, doesn't bypass
3. **Metrics tracking**: `total_events`, `total_tokens`, `get_status()`
4. **DialogueEngine optional**: Graceful degradation when None
5. **EventBus integration**: `await self._event_bus.publish(event)`

---

## Phase Accountability

| Phase | Status | Artifact |
|-------|--------|----------|
| PLAN | touched | This document |
| RESEARCH | pending | - |
| DEVELOP | pending | - |
| STRATEGIZE | skipped | - |
| CROSS-SYNERGIZE | pending | - |
| IMPLEMENT | pending | - |
| QA | pending | - |
| TEST | pending | - |
| EDUCATE | skipped | - |
| MEASURE | deferred | - |
| REFLECT | pending | - |

---

## Chunk 8 Preview

After WorkshopFlux, potential Chunk 8 directions:
1. **API Endpoints**: REST endpoints for workshop execution (`POST /workshop/task`, `GET /workshop/stream`)
2. **Web UI Components**: React components for workshop visualization
3. **CLI Handler**: `kg workshop` command for running workshops
4. **AGENTESE Integration**: `world.workshop.flux.*` paths

---

*"The flux coordinates; it does not command. Builders choose their rhythm within the stream."*
