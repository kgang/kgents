# N-Phase Native Integration: Implementation Meta-Prompt

> **For**: Claude Code agent (or equivalent)
> **From**: Prior planning session (2025-12-15)
> **Mission**: Implement native N-Phase orchestration across all kgents interfaces

---

## ATTACH

```
/hydrate nphase-native-integration
```

Read these files first:
1. `plans/nphase-native-integration.md` — The strategy memo (read completely)
2. `protocols/nphase/operad.py` — N-Phase enum, state, transitions
3. `protocols/nphase/compiler.py` — Existing compiler
4. `protocols/nphase/templates/__init__.py` — Phase templates
5. `protocols/api/sessions.py` — Existing sessions API
6. `agents/town/workshop.py` — Workshop orchestration pattern
7. `agents/town/builders/base.py` — Builder polynomial pattern
8. `protocols/agentese/logos.py` — AGENTESE handle resolution
9. `protocols/agentese/contexts/self_.py` — Self context affordances

---

## Context Summary

### What We're Building

An N-Phase Session Router that:
1. Maintains phase state (UNDERSTAND → ACT → REFLECT) across requests
2. Auto-detects phase transitions from LLM output (signifiers + heuristics)
3. Checkpoints at phase boundaries for resumption
4. Works identically across API, Web UI, and Claude Code
5. Handles context exhaustion automatically

### What Already Exists

| Component | Location | What It Does |
|-----------|----------|--------------|
| `NPhase` enum | `protocols/nphase/operad.py:27` | UNDERSTAND, ACT, REFLECT (SENSE alias) |
| `NPhaseState` | `protocols/nphase/operad.py:54` | current_phase, cycle_count, phase_outputs |
| `PHASE_FAMILIES` | `protocols/nphase/operad.py:40` | Detailed→compressed mapping |
| `is_valid_transition()` | `protocols/nphase/operad.py:328` | Validates phase transitions |
| `next_phase()` | `protocols/nphase/operad.py:350` | Gets next phase in cycle |
| Sessions API | `protocols/api/sessions.py` | Create/message/get sessions |
| Workshop | `agents/town/workshop.py` | Task orchestration with builder handoffs |
| BuilderPhase | `agents/town/builders/base.py` | EXPLORING→DESIGNING→PROTOTYPING→REFINING→INTEGRATING |
| Auto-inducer parser | `protocols/agentese/parser.py:741-933` | Parses ⟿/⟂/⤳ signifiers |
| EventBus | `agents/town/event_bus.py` | Fan-out event publishing |

### Key Design Decisions (Already Made)

1. **Phase state lives in Session Router**, not LLM context
2. **Support both explicit signifiers and heuristic detection**
3. **Reuse Workshop's builder handoff pattern** for development orchestration
4. **Checkpoint at phase boundaries** + on-demand
5. **Automatic crystallize → resume** for context exhaustion

---

## Implementation Waves

Execute these waves sequentially. Each wave has clear exit criteria.

---

### Wave 1: Session State Foundation

**Goal**: N-Phase sessions with state tracking, manual phase advancement.

**Files to create**:

#### 1.1 `protocols/nphase/session.py`

```python
"""
N-Phase Session State Management.

Provides stateful sessions that track phase progress across requests.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from protocols.nphase.operad import (
    NPhase,
    NPhaseState,
    is_valid_transition,
    next_phase,
)


@dataclass
class Handle:
    """A handle accumulated during a phase."""

    path: str  # AGENTESE path
    phase: NPhase  # Phase when acquired
    content: Any  # Resolved content
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PhaseLedgerEntry:
    """Record of a phase transition."""

    from_phase: NPhase
    to_phase: NPhase
    timestamp: datetime
    payload: Any  # What triggered the transition
    cycle_count: int


@dataclass
class SessionCheckpoint:
    """Snapshot of session state at a phase boundary."""

    id: str
    session_id: str
    phase: NPhase
    cycle_count: int
    handles: list[Handle]
    entropy_spent: dict[str, float]
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NPhaseSession:
    """Session with embedded N-Phase state."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    phase_state: NPhaseState = field(default_factory=NPhaseState)
    checkpoints: list[SessionCheckpoint] = field(default_factory=list)
    handles: list[Handle] = field(default_factory=list)
    ledger: list[PhaseLedgerEntry] = field(default_factory=list)
    entropy_spent: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_touched: datetime = field(default_factory=datetime.now)

    @property
    def current_phase(self) -> NPhase:
        """Get current phase."""
        return self.phase_state.current_phase

    @property
    def cycle_count(self) -> int:
        """Get current cycle count."""
        return self.phase_state.cycle_count

    def can_advance_to(self, target: NPhase) -> bool:
        """Check if transition to target is valid."""
        return is_valid_transition(self.current_phase, target)

    def advance_phase(
        self,
        target: NPhase | None = None,
        payload: Any = None,
    ) -> PhaseLedgerEntry:
        """
        Advance to target phase (or next phase if target is None).

        Returns ledger entry recording the transition.
        Raises ValueError if transition is invalid.
        """
        if target is None:
            target = next_phase(self.current_phase)

        if not self.can_advance_to(target):
            raise ValueError(
                f"Invalid transition: {self.current_phase.name} → {target.name}"
            )

        from_phase = self.current_phase

        # Check for cycle completion (REFLECT → UNDERSTAND)
        if from_phase == NPhase.REFLECT and target == NPhase.UNDERSTAND:
            self.phase_state.cycle_count += 1

        self.phase_state.current_phase = target
        self.last_touched = datetime.now()

        entry = PhaseLedgerEntry(
            from_phase=from_phase,
            to_phase=target,
            timestamp=self.last_touched,
            payload=payload,
            cycle_count=self.cycle_count,
        )
        self.ledger.append(entry)

        return entry

    def checkpoint(self, metadata: dict[str, Any] | None = None) -> SessionCheckpoint:
        """Create checkpoint at current state."""
        cp = SessionCheckpoint(
            id=str(uuid.uuid4()),
            session_id=self.id,
            phase=self.current_phase,
            cycle_count=self.cycle_count,
            handles=list(self.handles),  # Copy
            entropy_spent=dict(self.entropy_spent),  # Copy
            created_at=datetime.now(),
            metadata=metadata or {},
        )
        self.checkpoints.append(cp)
        return cp

    def restore(self, checkpoint_id: str) -> None:
        """Restore session state from checkpoint."""
        cp = next((c for c in self.checkpoints if c.id == checkpoint_id), None)
        if cp is None:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        self.phase_state.current_phase = cp.phase
        self.phase_state.cycle_count = cp.cycle_count
        self.handles = list(cp.handles)
        self.entropy_spent = dict(cp.entropy_spent)
        self.last_touched = datetime.now()

    def add_handle(self, path: str, content: Any) -> Handle:
        """Add a handle acquired in current phase."""
        handle = Handle(
            path=path,
            phase=self.current_phase,
            content=content,
        )
        self.handles.append(handle)
        return handle

    def get_handles_for_phase(self, phase: NPhase) -> list[Handle]:
        """Get all handles acquired in a specific phase."""
        return [h for h in self.handles if h.phase == phase]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "current_phase": self.current_phase.name,
            "cycle_count": self.cycle_count,
            "checkpoint_count": len(self.checkpoints),
            "handle_count": len(self.handles),
            "ledger_count": len(self.ledger),
            "entropy_spent": self.entropy_spent,
            "created_at": self.created_at.isoformat(),
            "last_touched": self.last_touched.isoformat(),
        }


# Session store (in-memory for now, replace with persistence later)
_session_store: dict[str, NPhaseSession] = {}


def create_session(title: str = "") -> NPhaseSession:
    """Create a new N-Phase session."""
    session = NPhaseSession(title=title)
    _session_store[session.id] = session
    return session


def get_session(session_id: str) -> NPhaseSession | None:
    """Get session by ID."""
    return _session_store.get(session_id)


def list_sessions() -> list[NPhaseSession]:
    """List all sessions."""
    return list(_session_store.values())


def delete_session(session_id: str) -> bool:
    """Delete session by ID."""
    if session_id in _session_store:
        del _session_store[session_id]
        return True
    return False
```

#### 1.2 `protocols/nphase/_tests/test_session.py`

Write comprehensive tests:
- `test_create_session` — session created with UNDERSTAND phase
- `test_advance_phase_valid` — UNDERSTAND → ACT → REFLECT works
- `test_advance_phase_invalid` — UNDERSTAND → REFLECT raises
- `test_cycle_completion` — REFLECT → UNDERSTAND increments cycle_count
- `test_checkpoint_restore` — state correctly restored
- `test_handle_tracking` — handles accumulated per phase
- `test_ledger_recording` — transitions recorded in ledger
- `test_session_store` — create/get/list/delete work

#### 1.3 Extend `protocols/api/sessions.py`

Add to existing file:
- Import `NPhaseSession` from `protocols.nphase.session`
- Add `nphase_state` field to `SessionResponse`
- Add endpoint: `POST /v1/sessions/{id}/phase` to advance phase
- Add endpoint: `POST /v1/sessions/{id}/checkpoint` to create checkpoint
- Add endpoint: `POST /v1/sessions/{id}/restore/{checkpoint_id}` to restore

**Exit criteria**:
- [ ] `NPhaseSession` dataclass with all methods
- [ ] Session store with CRUD operations
- [ ] Tests pass for session lifecycle
- [ ] API endpoints for phase/checkpoint operations
- [ ] Manual phase advancement works via API

---

### Wave 2: Phase Detection

**Goal**: Auto-detect phase transitions from LLM output.

**Files to create**:

#### 2.1 `protocols/nphase/detector.py`

```python
"""
Phase Detection from LLM Output.

Detects phase transitions using:
1. Explicit signifiers (⟿/⟂/⤳)
2. Heuristic patterns (file operations, test runs, etc.)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from protocols.nphase.operad import NPhase


class SignalAction(Enum):
    """Type of phase signal detected."""

    CONTINUE = auto()  # ⟿[PHASE] - advance to phase
    HALT = auto()  # ⟂[REASON] - stop, await human
    ELASTIC = auto()  # ⤳[OP:args] - elastic operation
    HEURISTIC = auto()  # Detected from patterns
    NONE = auto()  # No signal detected


@dataclass
class PhaseSignal:
    """Signal detected from LLM output."""

    action: SignalAction
    target_phase: NPhase | None = None
    reason: str | None = None
    elastic_op: str | None = None
    elastic_args: str | None = None
    confidence: float = 1.0  # 1.0 for explicit, <1.0 for heuristic


class PhaseDetector:
    """Detect phase transitions from LLM output."""

    # Signifier patterns (from spec/protocols/auto-inducer.md)
    CONTINUE_PATTERN = re.compile(r'⟿\[(\w+)\]')
    HALT_PATTERN = re.compile(r'⟂\[([^\]]+)\]')
    ELASTIC_PATTERN = re.compile(r'⤳\[(\w+):([^\]]+)\]')

    # Heuristic patterns for phase detection
    UNDERSTAND_PATTERNS = [
        re.compile(r'reading.*file', re.I),
        re.compile(r'exploring.*codebase', re.I),
        re.compile(r'searching.*for', re.I),
        re.compile(r'planning', re.I),
        re.compile(r'researching', re.I),
    ]

    ACT_PATTERNS = [
        re.compile(r'writing.*to.*file', re.I),
        re.compile(r'creating.*file', re.I),
        re.compile(r'editing.*file', re.I),
        re.compile(r'running.*test', re.I),
        re.compile(r'implementing', re.I),
        re.compile(r'git commit', re.I),
    ]

    REFLECT_PATTERNS = [
        re.compile(r'all.*tests.*pass', re.I),
        re.compile(r'implementation.*complete', re.I),
        re.compile(r'documenting', re.I),
        re.compile(r'writing.*epilogue', re.I),
        re.compile(r'learnings?:', re.I),
    ]

    # Phase name mapping
    PHASE_NAMES = {
        'UNDERSTAND': NPhase.UNDERSTAND,
        'SENSE': NPhase.UNDERSTAND,  # Alias
        'ACT': NPhase.ACT,
        'REFLECT': NPhase.REFLECT,
    }

    def detect(self, output: str, current_phase: NPhase) -> PhaseSignal:
        """
        Detect phase signal from LLM output.

        Priority:
        1. Explicit signifiers (highest confidence)
        2. Heuristic patterns (lower confidence)
        3. No signal
        """
        # Check explicit signifiers first
        if signal := self._detect_continue(output):
            return signal
        if signal := self._detect_halt(output):
            return signal
        if signal := self._detect_elastic(output):
            return signal

        # Fall back to heuristic detection
        return self._detect_heuristic(output, current_phase)

    def _detect_continue(self, output: str) -> PhaseSignal | None:
        """Detect ⟿[PHASE] continuation signifier."""
        match = self.CONTINUE_PATTERN.search(output)
        if match:
            phase_name = match.group(1).upper()
            target = self.PHASE_NAMES.get(phase_name)
            if target:
                return PhaseSignal(
                    action=SignalAction.CONTINUE,
                    target_phase=target,
                    confidence=1.0,
                )
        return None

    def _detect_halt(self, output: str) -> PhaseSignal | None:
        """Detect ⟂[REASON] halt signifier."""
        match = self.HALT_PATTERN.search(output)
        if match:
            return PhaseSignal(
                action=SignalAction.HALT,
                reason=match.group(1),
                confidence=1.0,
            )
        return None

    def _detect_elastic(self, output: str) -> PhaseSignal | None:
        """Detect ⤳[OP:args] elastic signifier."""
        match = self.ELASTIC_PATTERN.search(output)
        if match:
            return PhaseSignal(
                action=SignalAction.ELASTIC,
                elastic_op=match.group(1),
                elastic_args=match.group(2),
                confidence=1.0,
            )
        return None

    def _detect_heuristic(
        self, output: str, current_phase: NPhase
    ) -> PhaseSignal:
        """Detect phase from activity patterns."""
        # Count pattern matches for each phase
        understand_score = sum(
            1 for p in self.UNDERSTAND_PATTERNS if p.search(output)
        )
        act_score = sum(1 for p in self.ACT_PATTERNS if p.search(output))
        reflect_score = sum(1 for p in self.REFLECT_PATTERNS if p.search(output))

        # Determine suggested phase
        scores = {
            NPhase.UNDERSTAND: understand_score,
            NPhase.ACT: act_score,
            NPhase.REFLECT: reflect_score,
        }
        max_score = max(scores.values())

        if max_score == 0:
            return PhaseSignal(action=SignalAction.NONE)

        suggested = max(scores, key=scores.get)

        # Only suggest transition if different from current
        if suggested != current_phase:
            confidence = min(0.8, max_score * 0.2)  # Cap at 0.8 for heuristics
            return PhaseSignal(
                action=SignalAction.HEURISTIC,
                target_phase=suggested,
                confidence=confidence,
            )

        return PhaseSignal(action=SignalAction.NONE)


# Singleton instance
detector = PhaseDetector()
```

#### 2.2 `protocols/nphase/_tests/test_detector.py`

Write tests:
- `test_detect_continue_signifier` — ⟿[ACT] detected
- `test_detect_halt_signifier` — ⟂[needs input] detected
- `test_detect_elastic_signifier` — ⤳[COMPRESS:to ACT] detected
- `test_detect_heuristic_understand` — file reading patterns
- `test_detect_heuristic_act` — file writing patterns
- `test_detect_heuristic_reflect` — completion patterns
- `test_confidence_levels` — explicit=1.0, heuristic<1.0
- `test_phase_name_aliases` — SENSE maps to UNDERSTAND

#### 2.3 Wire into Session Router

Update `protocols/nphase/session.py`:
- Add `process_output(output: str) -> PhaseSignal` method to `NPhaseSession`
- Auto-advance on high-confidence signals (configurable threshold)
- Emit events for detected signals

#### 2.4 Add EventBus Integration

Create `protocols/nphase/events.py`:
```python
@dataclass
class PhaseTransitionEvent:
    session_id: str
    from_phase: NPhase
    to_phase: NPhase
    signal: PhaseSignal
    timestamp: datetime


@dataclass
class PhaseCheckpointEvent:
    session_id: str
    checkpoint_id: str
    phase: NPhase
    timestamp: datetime
```

Wire to `agents/town/event_bus.py` for fan-out.

**Exit criteria**:
- [ ] `PhaseDetector` with signifier + heuristic detection
- [ ] Tests pass for all detection patterns
- [ ] Session processes output and auto-advances
- [ ] Phase events emitted to EventBus

---

### Wave 3: Workshop Integration

**Goal**: Workshop orchestrates phase execution using builder pipeline.

**Files to create/modify**:

#### 3.1 `protocols/nphase/workshop.py`

```python
"""
Development Workshop: N-Phase orchestration via builder pipeline.

Maps N-Phase cycles to Workshop builder handoffs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agents.town.builders.base import Builder, BuilderPhase
from agents.town.workshop import Workshop, WorkshopTask
from protocols.nphase.operad import NPhase
from protocols.nphase.session import NPhaseSession


# Mapping from N-Phase to BuilderPhase sequences
PHASE_BUILDER_MAP: dict[NPhase, list[BuilderPhase]] = {
    NPhase.UNDERSTAND: [BuilderPhase.EXPLORING, BuilderPhase.DESIGNING],
    NPhase.ACT: [BuilderPhase.PROTOTYPING, BuilderPhase.REFINING],
    NPhase.REFLECT: [BuilderPhase.INTEGRATING],
}

# Reverse mapping for detection
BUILDER_TO_NPHASE: dict[BuilderPhase, NPhase] = {
    BuilderPhase.EXPLORING: NPhase.UNDERSTAND,
    BuilderPhase.DESIGNING: NPhase.UNDERSTAND,
    BuilderPhase.PROTOTYPING: NPhase.ACT,
    BuilderPhase.REFINING: NPhase.ACT,
    BuilderPhase.INTEGRATING: NPhase.REFLECT,
}


@dataclass
class PhaseOutput:
    """Output from executing an N-Phase."""

    phase: NPhase
    content: Any
    handles: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class DevelopmentWorkshop(Workshop):
    """Workshop specialized for N-Phase development."""

    def __init__(self, session: NPhaseSession):
        super().__init__()
        self.session = session

    async def execute_phase(
        self,
        phase: NPhase,
        context: dict[str, Any],
    ) -> PhaseOutput:
        """
        Execute an N-Phase using the builder pipeline.

        Each N-Phase maps to one or more BuilderPhases.
        Builders hand off artifacts sequentially.
        """
        builder_phases = PHASE_BUILDER_MAP[phase]
        current_context = context

        for bp in builder_phases:
            builder = self._get_or_create_builder(bp)
            artifact = await builder.execute(current_context)
            current_context = {"prior_artifact": artifact, **context}

        # Record phase completion
        output = PhaseOutput(
            phase=phase,
            content=current_context,
            handles=list(current_context.get("handles", [])),
            artifacts=list(current_context.get("artifacts", [])),
        )

        # Update session
        self.session.phase_state.phase_outputs[phase].append(output)

        return output

    async def run_cycle(self, initial_context: dict[str, Any]) -> list[PhaseOutput]:
        """
        Run a complete UNDERSTAND → ACT → REFLECT cycle.

        Returns outputs from all three phases.
        """
        outputs = []

        for phase in [NPhase.UNDERSTAND, NPhase.ACT, NPhase.REFLECT]:
            self.session.advance_phase(phase)
            output = await self.execute_phase(phase, initial_context)
            outputs.append(output)
            initial_context = {"prior_output": output, **initial_context}

        # Cycle complete, advance back to UNDERSTAND
        self.session.advance_phase(NPhase.UNDERSTAND)

        return outputs

    def _get_or_create_builder(self, phase: BuilderPhase) -> Builder:
        """Get builder for phase, creating if needed."""
        # Implementation depends on builder registry
        # For now, return a stub
        raise NotImplementedError("Wire to builder registry")
```

#### 3.2 Update `agents/town/workshop.py`

Add hooks for N-Phase integration:
- `on_phase_start(phase: BuilderPhase)` callback
- `on_phase_complete(phase: BuilderPhase, artifact: Any)` callback
- `on_handoff(from_builder: Builder, to_builder: Builder, artifact: Any)` callback

#### 3.3 `protocols/nphase/_tests/test_workshop.py`

Write tests:
- `test_phase_builder_mapping` — N-Phase maps to correct BuilderPhases
- `test_execute_understand_phase` — EXPLORING + DESIGNING executed
- `test_execute_act_phase` — PROTOTYPING + REFINING executed
- `test_execute_reflect_phase` — INTEGRATING executed
- `test_run_cycle` — complete cycle increments cycle_count
- `test_artifact_handoff` — artifacts passed between builders

**Exit criteria**:
- [ ] `DevelopmentWorkshop` maps N-Phase to BuilderPhase
- [ ] Phase execution uses builder pipeline
- [ ] Complete cycle runs through all phases
- [ ] Tests pass for workshop integration

---

### Wave 4: AGENTESE Integration

**Goal**: Phase-aware handle operations via `self.session.*` affordances.

**Files to modify**:

#### 4.1 Update `protocols/agentese/contexts/self_.py`

Add new affordances:

```python
# In SELF_AFFORDANCES, add:
"session.phase": Affordance(
    aspect="manifest",
    signature="() -> NPhase",
    description="Get current session phase",
),
"session.cycle": Affordance(
    aspect="manifest",
    signature="() -> int",
    description="Get current cycle count",
),
"session.advance": Affordance(
    aspect="invoke",
    signature="(target: NPhase) -> PhaseLedgerEntry",
    description="Advance to target phase",
),
"session.checkpoint": Affordance(
    aspect="invoke",
    signature="(metadata: dict) -> SessionCheckpoint",
    description="Create checkpoint at current state",
),
"session.restore": Affordance(
    aspect="invoke",
    signature="(checkpoint_id: str) -> None",
    description="Restore from checkpoint",
),
"session.handles": Affordance(
    aspect="manifest",
    signature="() -> list[Handle]",
    description="Get accumulated handles",
),
"session.continue": Affordance(
    aspect="invoke",
    signature="(target: NPhase) -> None",
    description="Emit continuation signifier and advance",
),
"session.halt": Affordance(
    aspect="invoke",
    signature="(reason: str) -> None",
    description="Emit halt signifier",
),
```

#### 4.2 Implement Session Node

Create `protocols/agentese/contexts/session.py`:

```python
"""
Session Context: Phase-aware session operations.

Provides self.session.* affordances for N-Phase orchestration.
"""

from protocols.agentese.node import LogosNode, NodeResult
from protocols.nphase.session import NPhaseSession, get_session


class SessionNode(LogosNode):
    """Node for session operations."""

    def __init__(self, session_id: str):
        self.session_id = session_id

    @property
    def session(self) -> NPhaseSession:
        session = get_session(self.session_id)
        if not session:
            raise ValueError(f"Session not found: {self.session_id}")
        return session

    async def manifest_phase(self, observer: Any) -> NodeResult:
        return NodeResult(value=self.session.current_phase)

    async def manifest_cycle(self, observer: Any) -> NodeResult:
        return NodeResult(value=self.session.cycle_count)

    async def invoke_advance(self, observer: Any, target: str) -> NodeResult:
        from protocols.nphase.operad import NPhase
        target_phase = NPhase[target.upper()]
        entry = self.session.advance_phase(target_phase)
        return NodeResult(value=entry)

    async def invoke_checkpoint(
        self, observer: Any, metadata: dict | None = None
    ) -> NodeResult:
        cp = self.session.checkpoint(metadata)
        return NodeResult(value=cp)

    async def invoke_restore(
        self, observer: Any, checkpoint_id: str
    ) -> NodeResult:
        self.session.restore(checkpoint_id)
        return NodeResult(value=None)

    async def manifest_handles(self, observer: Any) -> NodeResult:
        return NodeResult(value=self.session.handles)
```

#### 4.3 Wire into Logos

Update `protocols/agentese/logos.py`:
- Register `self.session.*` paths
- Route to SessionNode based on active session context

#### 4.4 `protocols/agentese/_tests/test_session_context.py`

Write tests:
- `test_self_session_phase` — returns current phase
- `test_self_session_advance` — advances phase
- `test_self_session_checkpoint` — creates checkpoint
- `test_self_session_restore` — restores from checkpoint
- `test_self_session_handles` — returns accumulated handles

**Exit criteria**:
- [ ] `self.session.*` affordances registered
- [ ] SessionNode implements all operations
- [ ] Logos routes session paths correctly
- [ ] Tests pass for session context

---

### Wave 5: API & Web UI

**Goal**: Full REST API and React integration.

**Files to create**:

#### 5.1 `protocols/api/nphase.py`

```python
"""
N-Phase API Endpoints.

REST API for N-Phase session management.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from protocols.nphase.session import (
    NPhaseSession,
    create_session,
    delete_session,
    get_session,
    list_sessions,
)
from protocols.nphase.operad import NPhase

router = APIRouter(prefix="/v1/nphase", tags=["nphase"])


class CreateSessionRequest(BaseModel):
    title: str = ""


class SessionResponse(BaseModel):
    id: str
    title: str
    current_phase: str
    cycle_count: int
    checkpoint_count: int
    handle_count: int


class AdvancePhaseRequest(BaseModel):
    target: str  # Phase name


class CheckpointRequest(BaseModel):
    metadata: dict = {}


@router.post("/session", response_model=SessionResponse)
async def create_nphase_session(request: CreateSessionRequest):
    """Create a new N-Phase session."""
    session = create_session(title=request.title)
    return _session_to_response(session)


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_nphase_session(session_id: str):
    """Get session by ID."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_to_response(session)


@router.get("/sessions", response_model=list[SessionResponse])
async def list_nphase_sessions():
    """List all sessions."""
    return [_session_to_response(s) for s in list_sessions()]


@router.delete("/session/{session_id}")
async def delete_nphase_session(session_id: str):
    """Delete session."""
    if not delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted"}


@router.post("/session/{session_id}/advance")
async def advance_phase(session_id: str, request: AdvancePhaseRequest):
    """Advance session to target phase."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        target = NPhase[request.target.upper()]
        entry = session.advance_phase(target)
        return {
            "from_phase": entry.from_phase.name,
            "to_phase": entry.to_phase.name,
            "cycle_count": entry.cycle_count,
        }
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/session/{session_id}/checkpoint")
async def create_checkpoint(session_id: str, request: CheckpointRequest):
    """Create checkpoint at current state."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    cp = session.checkpoint(request.metadata)
    return {
        "checkpoint_id": cp.id,
        "phase": cp.phase.name,
        "cycle_count": cp.cycle_count,
    }


@router.post("/session/{session_id}/restore/{checkpoint_id}")
async def restore_checkpoint(session_id: str, checkpoint_id: str):
    """Restore from checkpoint."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        session.restore(checkpoint_id)
        return {"status": "restored", "phase": session.current_phase.name}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/session/{session_id}/events")
async def session_events(session_id: str):
    """SSE stream of session events."""
    # Implementation: subscribe to EventBus for this session
    # Return Server-Sent Events stream
    raise NotImplementedError("Wire to EventBus")


def _session_to_response(session: NPhaseSession) -> SessionResponse:
    return SessionResponse(
        id=session.id,
        title=session.title,
        current_phase=session.current_phase.name,
        cycle_count=session.cycle_count,
        checkpoint_count=len(session.checkpoints),
        handle_count=len(session.handles),
    )
```

#### 5.2 Register Router

Update `protocols/api/app.py`:
```python
from protocols.api.nphase import router as nphase_router
app.include_router(nphase_router)
```

#### 5.3 React Components

Create in `web/src/components/nphase/`:

- `PhaseIndicator.tsx` — Shows current phase (UNDERSTAND/ACT/REFLECT)
- `PhaseLedger.tsx` — Shows phase transition history
- `CheckpointList.tsx` — Shows available checkpoints
- `HandleList.tsx` — Shows accumulated handles

Create in `web/src/pages/`:

- `NPhaseSession.tsx` — Full session view with phase management

#### 5.4 `protocols/api/_tests/test_nphase_api.py`

Write tests:
- `test_create_session` — POST /v1/nphase/session works
- `test_get_session` — GET /v1/nphase/session/{id} works
- `test_advance_phase` — POST /v1/nphase/session/{id}/advance works
- `test_checkpoint_restore` — checkpoint/restore round-trip works
- `test_invalid_transition` — returns 400 for invalid transition

**Exit criteria**:
- [ ] All N-Phase API endpoints implemented
- [ ] API tests pass
- [ ] React components render phase state
- [ ] SSE events stream phase transitions
- [ ] Web UI can manage full session lifecycle

---

### Wave 6: Claude Code Integration

**Goal**: Slash commands for Claude Code.

**Files to create**:

#### 6.1 `.claude/commands/nphase.md`

```markdown
# /nphase - N-Phase Session Management

Start, resume, or manage N-Phase development sessions.

## Protocol

1. **Check for active session** in `.claude/nphase-session.json`
2. **If no session**: Create new session, save state
3. **If active session**: Show status, offer actions

## Usage

```
/nphase                    # Show current session status
/nphase start [title]      # Start new session
/nphase end                # End session, export state
```

## Session State File

Location: `.claude/nphase-session.json`

```json
{
  "id": "uuid",
  "title": "Feature X Implementation",
  "current_phase": "ACT",
  "cycle_count": 1,
  "checkpoints": [...],
  "handles": [...],
  "created_at": "2025-12-15T10:00:00Z",
  "last_touched": "2025-12-15T14:30:00Z"
}
```

## On Start

1. Create session (API or local)
2. Run `/hydrate` for context
3. Display phase and cycle count
4. Begin UNDERSTAND phase

## On Resume

1. Load session state
2. Display accumulated handles
3. Show checkpoint history
4. Continue from current phase
```

#### 6.2 `.claude/commands/phase.md`

```markdown
# /phase - Phase Operations

Manage the current phase within an N-Phase session.

## Protocol

1. **Read session state** from `.claude/nphase-session.json`
2. **If no session**: Error - run `/nphase start` first
3. **Execute requested operation**
4. **Update session state**

## Usage

```
/phase                     # Show current phase
/phase advance [TARGET]    # Advance to target (or next) phase
/phase checkpoint [note]   # Create checkpoint with optional note
/phase restore [ID]        # Restore from checkpoint
/phase compress            # Compress remaining phases to 3-phase
/phase handles             # List accumulated handles
```

## Phase Advancement

Valid transitions:
- UNDERSTAND → ACT
- ACT → REFLECT
- REFLECT → UNDERSTAND (new cycle)

## Output Format

```
Phase: ACT (cycle 2)
Handles: 5 accumulated
Checkpoints: 3 available

Last transition: UNDERSTAND → ACT (2 hours ago)
```
```

#### 6.3 `.claude/commands/handles.md`

```markdown
# /handles - Handle Management

View and export handles accumulated during the session.

## Protocol

1. **Read session state**
2. **Display handles grouped by phase**
3. **Offer export options**

## Usage

```
/handles                   # List all handles
/handles phase [PHASE]     # List handles for specific phase
/handles export            # Export handles for session handoff
/handles add <path>        # Manually add handle
```

## Export Format

```markdown
# Session Handles Export

Session: Feature X Implementation
Exported: 2025-12-15T14:30:00Z
Cycle: 2, Phase: REFLECT

## UNDERSTAND Handles
- `protocols/nphase/session.py:1-100` — Session state management
- `protocols/api/nphase.py` — API endpoints

## ACT Handles
- `protocols/nphase/_tests/test_session.py` — Session tests
- `web/src/components/nphase/PhaseIndicator.tsx` — React component

## REFLECT Handles
- `plans/nphase-native-integration.md` — Strategy document
```
```

#### 6.4 Local State Management

Create `protocols/nphase/local_state.py`:

```python
"""
Local State Management for Claude Code.

Persists N-Phase session state to .claude/nphase-session.json.
"""

import json
from pathlib import Path
from typing import Any

from protocols.nphase.session import NPhaseSession, Handle
from protocols.nphase.operad import NPhase

STATE_FILE = Path(".claude/nphase-session.json")


def save_local_session(session: NPhaseSession) -> None:
    """Save session to local state file."""
    STATE_FILE.parent.mkdir(exist_ok=True)
    state = {
        "id": session.id,
        "title": session.title,
        "current_phase": session.current_phase.name,
        "cycle_count": session.cycle_count,
        "checkpoints": [
            {
                "id": cp.id,
                "phase": cp.phase.name,
                "cycle_count": cp.cycle_count,
                "created_at": cp.created_at.isoformat(),
            }
            for cp in session.checkpoints
        ],
        "handles": [
            {
                "path": h.path,
                "phase": h.phase.name,
                "created_at": h.created_at.isoformat(),
            }
            for h in session.handles
        ],
        "ledger": [
            {
                "from_phase": e.from_phase.name,
                "to_phase": e.to_phase.name,
                "timestamp": e.timestamp.isoformat(),
                "cycle_count": e.cycle_count,
            }
            for e in session.ledger
        ],
        "created_at": session.created_at.isoformat(),
        "last_touched": session.last_touched.isoformat(),
    }
    STATE_FILE.write_text(json.dumps(state, indent=2))


def load_local_session() -> NPhaseSession | None:
    """Load session from local state file."""
    if not STATE_FILE.exists():
        return None

    state = json.loads(STATE_FILE.read_text())
    # Reconstruct NPhaseSession from state
    # (Implementation details omitted for brevity)
    ...


def clear_local_session() -> None:
    """Clear local session state."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
```

**Exit criteria**:
- [ ] `/nphase` command starts/resumes sessions
- [ ] `/phase` command manages phase transitions
- [ ] `/handles` command shows accumulated handles
- [ ] Local state persists across Claude Code sessions
- [ ] Commands work without API connection (local-only mode)

---

## Success Criteria (All Waves)

### Minimum Viable

- [ ] N-Phase session with state tracking
- [ ] Manual phase advancement works
- [ ] Checkpoint/restore works
- [ ] At least one interface fully functional

### Full Integration

- [ ] Auto-detection from signifiers (⟿/⟂/⤳)
- [ ] Heuristic detection fallback
- [ ] All three interfaces work identically
- [ ] Workshop-based phase orchestration
- [ ] Phase events streamed to EventBus
- [ ] Handles accumulated and exportable
- [ ] Claude Code slash commands functional

### Quality Parity Test

Run the same feature implementation through:
1. Manual Claude Code (current workflow)
2. API-driven N-Phase session
3. Web UI N-Phase session
4. Claude Code with `/nphase` commands

All should produce equivalent quality with equal or less human effort.

---

## File Checklist

### Create (New Files)

- [ ] `protocols/nphase/session.py`
- [ ] `protocols/nphase/detector.py`
- [ ] `protocols/nphase/events.py`
- [ ] `protocols/nphase/workshop.py`
- [ ] `protocols/nphase/local_state.py`
- [ ] `protocols/nphase/_tests/test_session.py`
- [ ] `protocols/nphase/_tests/test_detector.py`
- [ ] `protocols/nphase/_tests/test_workshop.py`
- [ ] `protocols/api/nphase.py`
- [ ] `protocols/api/_tests/test_nphase_api.py`
- [ ] `protocols/agentese/contexts/session.py`
- [ ] `protocols/agentese/_tests/test_session_context.py`
- [ ] `.claude/commands/nphase.md`
- [ ] `.claude/commands/phase.md`
- [ ] `.claude/commands/handles.md`
- [ ] `web/src/components/nphase/PhaseIndicator.tsx`
- [ ] `web/src/components/nphase/PhaseLedger.tsx`
- [ ] `web/src/components/nphase/CheckpointList.tsx`
- [ ] `web/src/components/nphase/HandleList.tsx`
- [ ] `web/src/pages/NPhaseSession.tsx`

### Modify (Existing Files)

- [ ] `protocols/api/app.py` — Register nphase router
- [ ] `protocols/api/sessions.py` — Add phase state fields
- [ ] `protocols/agentese/contexts/self_.py` — Add session affordances
- [ ] `protocols/agentese/logos.py` — Register session paths
- [ ] `agents/town/workshop.py` — Add phase hooks

---

## Continuation Signifiers

When completing each wave, emit:

- `⟿[WAVE_N_COMPLETE]` — Wave N finished, continue to N+1
- `⟂[BLOCKED: reason]` — Blocked, need human input
- `⤳[CHECKPOINT: wave_N]` — Checkpoint created, safe to pause

---

*Generated by Claude Code (Opus 4.5) on 2025-12-15*
*Strategy source: plans/nphase-native-integration.md*
