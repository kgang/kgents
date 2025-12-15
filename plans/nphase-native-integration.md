# N-Phase Native Integration Strategy

> *"The human is not the scheduler. The human is the gardener."*

**Author**: Claude Code (Opus 4.5)
**Date**: 2025-12-15
**Status**: First iteration, awaiting review

---

## Executive Summary

This memo analyzes how to natively integrate the N-Phase compiler into kgents development, eliminating the need for manual session jockeying. The goal: whether Kent uses the API, web UI, or Claude Code with tmux, the development experience maintains or increases quality and creativity.

**Key insight**: 90% of the infrastructure already exists. We need to wire together:
1. **Workshop** (builder handoffs) → phase orchestration
2. **AGENTESE** (phase-aware paths) → handle-based state
3. **Sessions API** (phase state) → resumable continuations
4. **N-Phase compiler** (YAML→prompts) → project definition

**Estimated integration effort**: M (medium) - primarily wiring, minimal new abstractions.

---

## Part I: Current State Analysis

### What Kent Does Now (Manual Orchestration)

```
┌─────────────────────────────────────────────────────────────┐
│                     KENT (Human Scheduler)                   │
│                                                              │
│  1. Opens Claude Code session                                │
│  2. Runs /hydrate to load context                           │
│  3. Manually guides through UNDERSTAND → ACT → REFLECT      │
│  4. Detects phase transitions by reading output             │
│  5. Decides when to compress (11→3 phases)                  │
│  6. Manages session context exhaustion                      │
│  7. Copies handles to next session                          │
│  8. Writes epilogues manually                               │
└─────────────────────────────────────────────────────────────┘
```

**Pain points**:
- Context exhaustion requires manual DETACH/ATTACH
- Phase detection is implicit (Kent reads and decides)
- No automatic checkpoint at phase boundaries
- Session state doesn't persist phase progress
- Multiple interfaces (API, web, CLI) are disconnected

### What Exists in kgents

| Component | Capability | Gap |
|-----------|-----------|-----|
| **Workshop** | Builder handoffs (Scout→Sage→Spark→Steady→Sync) | Not wired to N-Phase |
| **Citizen.nphase_state** | Tracks UNDERSTAND/ACT/REFLECT + cycle_count | Only for simulation, not dev sessions |
| **AGENTESE parser** | `[phase=DEVELOP]` clause support | Not used in session routing |
| **self.memory.checkpoint** | Phase boundary snapshots | Not triggered automatically |
| **Sessions API** | Session create/message/get | No phase state tracking |
| **N-Phase compiler** | YAML→structured prompts | Standalone, not session-aware |
| **Auto-inducer signifiers** | ⟿/⟂/⤳ parsed in specs | Not consumed by Logos |
| **Flux + EventBus** | Real-time event streaming | Could emit phase transitions |

**Key observation**: The pieces exist but aren't connected. This is a wiring problem, not a missing-abstraction problem.

---

## Part II: Target Architecture

### Vision: The Orchestrated Development Session

```
┌────────────────────────────────────────────────────────────────┐
│                     KENT (Human Gardener)                       │
│                                                                 │
│  Provides: Intent, feedback, course corrections                 │
│  Does NOT provide: Phase scheduling, context management         │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                   N-PHASE SESSION ROUTER                        │
│                                                                 │
│  • Maintains phase state across requests                        │
│  • Auto-detects phase transitions from LLM output              │
│  • Checkpoints at phase boundaries                             │
│  • Emits phase events to EventBus                              │
│  • Handles context exhaustion with automatic DETACH/ATTACH     │
└────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐       ┌──────────┐       ┌──────────┐
    │ API      │       │ Web UI   │       │ Claude   │
    │ Sessions │       │ (React)  │       │ Code CLI │
    └──────────┘       └──────────┘       └──────────┘
          │                   │                   │
          └───────────────────┴───────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ AGENTESE Logos   │
                    │ (Phase-Aware)    │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ D-gent Memory    │
                    │ (Crystals/Ghost) │
                    └──────────────────┘
```

### Three Interface Modes

| Interface | Entry Point | Phase Orchestration |
|-----------|-------------|---------------------|
| **API** | `POST /v1/nphase/session` | Router manages state server-side |
| **Web UI** | React components + SSE | Router streams phase events |
| **Claude Code** | Slash commands (`/phase`, `/checkpoint`) | Router via MCP or local state |

All three share the same N-Phase Session Router, ensuring identical behavior.

---

## Part III: Integration Strategy

### Layer 1: N-Phase Session State

**New file**: `protocols/nphase/session.py`

```python
@dataclass
class NPhaseSession:
    """Session with embedded N-Phase state."""

    id: str
    project: ProjectDefinition | None  # From YAML if compiled
    phase_state: NPhaseState  # Current phase + cycle_count
    checkpoints: list[SessionCheckpoint]  # Phase boundary snapshots
    handles: list[Handle]  # Accumulated across phases
    entropy_spent: dict[NPhase, float]
    created_at: datetime
    last_touched: datetime

    def advance_phase(self, target: NPhase, payload: Any) -> PhaseLedgerEntry:
        """Advance to target phase, record transition."""
        ...

    def checkpoint(self) -> SessionCheckpoint:
        """Snapshot current state at phase boundary."""
        ...

    def restore(self, checkpoint_id: str) -> None:
        """Restore from checkpoint (rollback)."""
        ...
```

**Integration with existing Sessions API** (`protocols/api/sessions.py`):
- Add `nphase_state` field to `SessionResponse`
- Add `phase` parameter to `MessageRequest`
- Emit phase transitions to EventBus

### Layer 2: Phase Detection Middleware

**New file**: `protocols/nphase/detector.py`

```python
class PhaseDetector:
    """Detect phase transitions from LLM output."""

    # Pattern matching for auto-inducer signifiers
    CONTINUE_PATTERN = re.compile(r'⟿\[(\w+)\]')  # ⟿[ACT]
    HALT_PATTERN = re.compile(r'⟂\[(.+?)\]')       # ⟂[needs clarification]
    ELASTIC_PATTERN = re.compile(r'⤳\[(\w+):(.+?)\]')  # ⤳[COMPRESS:to ACT]

    def detect(self, output: str, current_phase: NPhase) -> PhaseSignal:
        """Detect phase signal from LLM output."""
        if match := self.CONTINUE_PATTERN.search(output):
            return PhaseSignal(action="continue", target=match.group(1))
        if match := self.HALT_PATTERN.search(output):
            return PhaseSignal(action="halt", reason=match.group(1))
        if match := self.ELASTIC_PATTERN.search(output):
            return PhaseSignal(action="elastic", op=match.group(1), args=match.group(2))

        # Heuristic detection from activity patterns
        return self._heuristic_detect(output, current_phase)

    def _heuristic_detect(self, output: str, current: NPhase) -> PhaseSignal:
        """Fallback: detect from file operations, test runs, etc."""
        ...
```

**Integration with Logos** (`protocols/agentese/logos.py`):
- Wrap `invoke()` with phase detection post-processing
- Emit detected transitions to session router

### Layer 3: Workshop-Based Phase Orchestration

**Insight**: The Workshop's builder handoff pattern maps directly to N-Phase:

| N-Phase | Workshop Phase | Builder Specialty |
|---------|---------------|-------------------|
| UNDERSTAND (PLAN) | EXPLORING | Scout |
| UNDERSTAND (DEVELOP) | DESIGNING | Sage |
| ACT (IMPLEMENT) | PROTOTYPING | Spark |
| ACT (TEST) | REFINING | Steady |
| REFLECT | INTEGRATING | Sync |

**Strategy**: Use Workshop as the orchestration backbone for development sessions.

```python
# In workshop.py, add:
class DevelopmentWorkshop(Workshop):
    """Workshop specialized for N-Phase development."""

    def __init__(self, project: ProjectDefinition):
        super().__init__()
        self.project = project
        self.phase_mapping = {
            NPhase.UNDERSTAND: [BuilderPhase.EXPLORING, BuilderPhase.DESIGNING],
            NPhase.ACT: [BuilderPhase.PROTOTYPING, BuilderPhase.REFINING],
            NPhase.REFLECT: [BuilderPhase.INTEGRATING],
        }

    async def execute_phase(self, phase: NPhase, context: dict) -> PhaseOutput:
        """Execute N-Phase using builder pipeline."""
        builder_phases = self.phase_mapping[phase]
        for bp in builder_phases:
            builder = self.get_builder_for_phase(bp)
            await builder.execute(context)
            context = builder.handoff_artifact
        return PhaseOutput(phase=phase, content=context)
```

### Layer 4: AGENTESE Phase-Aware Handles

**Extend handle syntax for phase context**:

```python
# Current: concept.feature.define
# Extended: concept.feature.define[phase=IMPLEMENT]@session=abc123

# In self context, add phase-aware memory:
"self.session.phase"           # Current phase
"self.session.checkpoint"      # Create checkpoint
"self.session.handles"         # Accumulated handles
"self.session.continue[ACT]"   # Advance to ACT
"self.session.halt[reason]"    # Halt, await human
```

**Integration**:
- Parser already supports `[phase=X]` clauses
- Add `self.session.*` affordances to self context
- Route through N-Phase Session Router

### Layer 5: API Endpoints

**New endpoints** in `protocols/api/nphase.py`:

```python
# Session lifecycle
POST   /v1/nphase/session          # Create with optional ProjectDefinition
GET    /v1/nphase/session/{id}     # Get session + phase state
DELETE /v1/nphase/session/{id}     # End session, persist final state

# Phase operations
POST   /v1/nphase/session/{id}/message   # Send message, phase auto-detected
POST   /v1/nphase/session/{id}/advance   # Force phase transition
POST   /v1/nphase/session/{id}/checkpoint  # Manual checkpoint
POST   /v1/nphase/session/{id}/restore/{checkpoint_id}  # Rollback

# Project compilation
POST   /v1/nphase/compile          # Compile YAML → prompt (existing)
POST   /v1/nphase/bootstrap        # Bootstrap session from plan.md

# Events
GET    /v1/nphase/session/{id}/events  # SSE stream of phase events
```

### Layer 6: Claude Code Integration

**Option A: MCP Server** (recommended)
- Expose N-Phase Session Router as MCP server
- Claude Code connects via MCP protocol
- Same state management as API/Web

**Option B: Local State File**
- Session state in `.claude/nphase-session.json`
- Slash commands read/write local state
- Syncs to API on explicit save

**New slash commands**:

```markdown
# /nphase - Start/resume N-Phase session
Start or resume an N-Phase development session.

## Usage
/nphase                    # Resume current session
/nphase start <project.yaml>  # Start from compiled project
/nphase bootstrap <plan.md>   # Bootstrap from plan file

# /phase - Phase operations
/phase                     # Show current phase
/phase advance [TARGET]    # Advance to target phase
/phase checkpoint          # Create checkpoint
/phase restore [ID]        # Restore from checkpoint
/phase compress            # Compress remaining to 3-phase

# /handles - Handle management
/handles                   # List accumulated handles
/handles add <path>        # Manually add handle
/handles export            # Export for session handoff
```

---

## Part IV: Implementation Waves

### Wave 1: Session State Foundation (S effort)

**Goal**: N-Phase sessions with state tracking, no auto-detection yet.

1. Create `protocols/nphase/session.py` with `NPhaseSession`
2. Add phase state to Sessions API
3. Implement manual phase advance
4. Add checkpoint/restore
5. Tests for session lifecycle

**Exit criterion**: Can create session, manually advance phases, checkpoint/restore.

### Wave 2: Phase Detection (M effort)

**Goal**: Auto-detect phase transitions from LLM output.

1. Create `protocols/nphase/detector.py`
2. Implement signifier detection (⟿/⟂/⤳)
3. Implement heuristic detection (file ops, test runs)
4. Wire into Logos invoke wrapper
5. Emit events to EventBus

**Exit criterion**: Phase transitions detected and emitted automatically.

### Wave 3: Workshop Integration (M effort)

**Goal**: Workshop orchestrates phase execution.

1. Create `DevelopmentWorkshop` subclass
2. Map N-Phase → BuilderPhase
3. Implement phase execution pipeline
4. Integrate with session state
5. Tests for full cycle (UNDERSTAND → ACT → REFLECT)

**Exit criterion**: Can run complete development cycle through Workshop.

### Wave 4: AGENTESE Integration (S effort)

**Goal**: Phase-aware handle operations.

1. Add `self.session.*` affordances
2. Wire phase clauses through Logos
3. Implement phase-aware checkpointing
4. Tests for handle + phase interaction

**Exit criterion**: `self.session.continue[ACT]` advances phase.

### Wave 5: API & Web UI (M effort)

**Goal**: Full API and React integration.

1. Create `protocols/api/nphase.py` endpoints
2. Add SSE endpoint for phase events
3. React components for phase visualization
4. Phase progress indicator in web UI
5. Integration tests

**Exit criterion**: Can run N-Phase session through web UI with real-time phase display.

### Wave 6: Claude Code Integration (S effort)

**Goal**: Slash commands for Claude Code.

1. Create MCP server for N-Phase (or local state file)
2. Implement `/nphase`, `/phase`, `/handles` commands
3. Wire to session router
4. Test in Claude Code environment

**Exit criterion**: Can run N-Phase session entirely from Claude Code.

---

## Part V: Key Design Decisions

### D1: Phase State Location

**Decision**: Phase state lives in Session Router, not in LLM context.

**Rationale**:
- LLM context is ephemeral (summarization, context exhaustion)
- Session Router persists across context boundaries
- Multiple interfaces share same state

**Trade-off**: Requires explicit state sync between LLM output and router.

### D2: Auto-Detection vs Explicit Signifiers

**Decision**: Support both; prefer explicit signifiers when present.

**Rationale**:
- Explicit signifiers (⟿[ACT]) are unambiguous
- Heuristic detection provides fallback
- Training can improve signifier emission over time

**Trade-off**: Heuristic detection may be inaccurate.

### D3: Workshop as Orchestration Backbone

**Decision**: Reuse Workshop's builder handoff pattern for development.

**Rationale**:
- Workshop already implements phase-based coordination
- Builder specialties map to N-Phase naturally
- Avoids building parallel orchestration system

**Trade-off**: Development sessions look like Agent Town simulations internally.

### D4: Checkpoint Granularity

**Decision**: Checkpoint at phase boundaries + on-demand.

**Rationale**:
- Phase boundaries are natural checkpoint points
- Manual checkpoints for mid-phase saves
- Balances storage vs recoverability

**Trade-off**: Mid-phase work may be lost on rollback.

### D5: Context Exhaustion Handling

**Decision**: Automatic crystallize → new session → resume from crystal.

**Rationale**:
- D-gent memory already supports crystallization
- Session Router coordinates the handoff
- Human doesn't need to manage context

**Trade-off**: Some context loss at crystallization boundary.

---

## Part VI: Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Phase detection inaccuracy | Train on explicit signifiers; human override via `/phase advance` |
| Context loss at boundaries | Rich checkpoints with handle export |
| API/CLI/Web divergence | Single Session Router serves all interfaces |
| Workshop complexity | Start with simple mapping, add sophistication later |
| MCP integration friction | Fallback to local state file for Claude Code |

---

## Part VII: Success Criteria

### Minimum Viable Integration

- [ ] N-Phase session with manual phase advance
- [ ] Checkpoint/restore works
- [ ] Single interface (API or CLI) fully functional

### Full Integration

- [ ] Auto-detection from signifiers
- [ ] Heuristic detection fallback
- [ ] All three interfaces (API, Web, CLI) work identically
- [ ] Workshop-based orchestration
- [ ] Context exhaustion handled automatically
- [ ] Phase events streamed to UI
- [ ] Handles accumulated and exported

### Quality Parity Test

Kent can develop a feature using:
1. Manual Claude Code (current)
2. API-driven session
3. Web UI session

All three produce equivalent quality output with equivalent or less human effort.

---

## Part VIII: First Iteration Tasks

For immediate implementation, I propose starting with **Wave 1** (Session State Foundation):

```
1. Create protocols/nphase/session.py
   - NPhaseSession dataclass
   - SessionCheckpoint dataclass
   - advance_phase(), checkpoint(), restore() methods

2. Extend protocols/api/sessions.py
   - Add phase_state to SessionResponse
   - Add POST /v1/sessions/{id}/phase endpoint

3. Create protocols/nphase/_tests/test_session.py
   - Test session lifecycle
   - Test phase advancement
   - Test checkpoint/restore

4. Add /phase slash command (manual)
   - /phase → show current
   - /phase advance [TARGET] → advance
   - /phase checkpoint → save
```

**Estimated effort**: S (small) - 1-2 focused sessions.

---

## Conclusion

The N-Phase compiler is currently a prompt generator. This strategy transforms it into an **orchestration backbone** that:

1. **Tracks phase state** across sessions and interfaces
2. **Detects phase transitions** automatically from LLM output
3. **Coordinates work** using Workshop's builder handoff pattern
4. **Preserves context** through checkpoints and crystallization
5. **Unifies interfaces** so API, Web, and CLI behave identically

Kent's role shifts from **scheduler** (managing sessions, tracking phases, copying handles) to **gardener** (providing intent, giving feedback, course-correcting).

The infrastructure exists. We just need to wire it together.

---

*⟿[REFLECT] — Strategy complete. Awaiting human review.*
