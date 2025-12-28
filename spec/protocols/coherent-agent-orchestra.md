# Coherent Agent Orchestra Protocol

> *"Three agents, one vision. The coherence is the composition. The flow is the proof."*

**Status**: Draft Specification
**Version**: 1.0
**Date**: 2025-12-27
**Principles**: Composable, Heterarchical, Generative, Joy-Inducing
**Problem**: Stop-and-go coordination kills creative momentum

---

## Abstract

The current pilot regeneration system uses a **file-based eventual consistency model** where CREATIVE, ADVERSARIAL, and PLAYER coordinate via `.focus`, `.needs`, `.offerings`, and `.pulse` files. While functional, this architecture creates:

1. **Stop-and-go coordination**: Agents pause to read partner state, breaking flow
2. **Context explosion**: Files grow monotonically (509+ lines by iteration 10)
3. **Coherence theater**: Outline claims coherence that reality doesn't support
4. **Lost state on compaction**: No mechanism to compress while preserving signal

This spec proposes the **Coherent Agent Orchestra Protocol (CAOP)**—a self-correcting adaptive system that maintains coherence through **shared state machines**, **progressive summarization**, and **resonance signals**.

**Core Insight**: Coherence isn't a property agents *have*; it's a property agents *compose into*. The orchestra produces coherence through the morphism of their interaction, not through file synchronization.

---

## Part I: The Problem (Deep Analysis)

### 1.1 Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│          FILE-BASED IPC (Eventual Consistency)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CREATIVE ────────→ .focus.creative.md (append-only)            │
│     │               .offerings.creative.md                       │
│     │               .pulse.creative                              │
│     │                                                             │
│     └──────────────← .needs.creative.md (from others)           │
│                                                                   │
│  ADVERSARIAL ─────→ .focus.adversarial.md (append-only)         │
│     │               .offerings.adversarial.md                    │
│     │               .pulse.adversarial                           │
│     │                                                             │
│     └──────────────← .needs.adversarial.md                       │
│                                                                   │
│  PLAYER ──────────→ .player.session.md (36KB!)                  │
│     │               .player.feedback.md (36KB!)                  │
│     │               .player.culture.log.md                       │
│     │                                                             │
│     └──────────────← .build.ready (signal from CREATIVE)        │
│                                                                   │
│  SHARED ──────────→ .outline.md (conflict-prone)                │
│                     /tmp/kgents-regen/{pilot}/.iteration        │
│                     /tmp/kgents-regen/{pilot}/.phase            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Why It's Stilted

| Symptom | Root Cause | Impact |
|---------|------------|--------|
| **5-10 min reading before working** | Agent must parse 500+ line focus files | Creative momentum destroyed |
| **False coherence** | Outline says X, focus says Y | Agents work on wrong assumptions |
| **Iteration drift** | Manual `.iteration` updates | Phase mismatch between agents |
| **Silent failures** | Stale pulse = ambiguous (paused? stuck? done?) | Undetected blocking |
| **Context explosion** | Append-only files, no compaction | LLM context window pressure |
| **Information burial** | Critical decisions buried in 36KB files | Signal lost in noise |

### 1.3 The One-Shot Paradox

Kent observes: *"The performance and richness is much better with one Claude Code session trying to one-shot it."*

Why? Because one session has:
- **Unified context**: No file parsing overhead
- **Continuous state**: No synchronization gaps
- **Natural compaction**: LLM naturally summarizes as context grows
- **Implicit coherence**: One mind = coherent vision

The three-agent system trades these for:
- **Parallel capacity**: Three agents work simultaneously
- **Specialized perspectives**: Each agent has a distinct voice
- **Dialectical synthesis**: Contradiction reveals emerge from opposition

**The challenge**: Preserve the benefits of multi-agent dialectic while achieving single-session flow.

---

## Part II: The Solution (Coherent Orchestra)

### 2.1 Core Principles

1. **Resonance Over Reading**: Agents don't read files; they sense resonance in a shared state
2. **Progressive Compression**: Every iteration compacts the previous; coherence compounds
3. **Witness-Backed Claims**: No status without evidence; marks prove completion
4. **Self-Correcting Drift Detection**: Agents detect and resolve their own incoherence
5. **Flow Over Sync**: Coordination happens in the background, not in foreground blocks

### 2.2 The Orchestra State Machine

Replace scattered files with a **single shared state machine**:

```python
@dataclass
class OrchestraState:
    """
    The shared state of the agent orchestra.

    This is THE source of truth. No agent owns it exclusively.
    All agents can READ freely. WRITE requires protocol.
    """

    # Phase tracking (source of truth)
    run_number: int
    iteration: int                          # 1-10 (or negotiated)
    phase: Literal["DESIGN", "EXECUTION", "REFLECTION"]

    # Agent liveness (not just pulse, but intent)
    agents: dict[str, AgentPresence]        # creative, adversarial, player

    # Compressed context (not append-only)
    context: CompressedContext              # Current iteration context
    history: list[IterationSummary]         # Compressed prior iterations

    # Resonance signals (replaces needs/offerings)
    resonance: ResonanceField               # What's active, what's blocked, what's resolved

    # The outline (generated from state, not manually maintained)
    @property
    def outline(self) -> str:
        """Generate outline from state—never stale."""
        return generate_outline(self)

    # Coherence check (self-correcting)
    def coherence_score(self) -> float:
        """How coherent are the agents right now?"""
        return calculate_coherence(self.agents, self.resonance)

    def detect_drift(self) -> list[DriftSignal]:
        """Identify where agents have drifted out of sync."""
        return detect_drift(self.agents, self.context, self.history)


@dataclass
class AgentPresence:
    """An agent's presence in the orchestra."""
    role: str                               # creative, adversarial, player
    status: Literal["active", "thinking", "blocked", "idle", "absent"]
    intent: str                             # What am I doing right now (1 sentence)
    focus: str                              # Current task (not a history log)
    last_action: datetime
    contribution_count: int                 # How many contributions this iteration

    def is_stale(self, threshold_minutes: int = 10) -> bool:
        return (datetime.now() - self.last_action).total_seconds() > threshold_minutes * 60


@dataclass
class CompressedContext:
    """
    The context for the current iteration.

    NOT append-only. Compressed and regenerated each iteration.
    """
    iteration: int
    mission: str                            # Restated mission for THIS iteration
    deliverables: list[Deliverable]         # What we're producing
    decisions: list[Decision]               # Decisions made this iteration (max 5)
    blockers: list[Blocker]                 # Active blockers
    artifacts: list[Artifact]               # Produced artifacts (with witness marks)

    @property
    def token_budget(self) -> int:
        """Context should fit in ~2000 tokens."""
        return 2000

    def compress_if_needed(self) -> "CompressedContext":
        """If context exceeds budget, compress."""
        if estimate_tokens(self) > self.token_budget:
            return self._compress()
        return self


@dataclass
class IterationSummary:
    """
    A compressed summary of a completed iteration.

    This is what survives compaction. ~200 tokens per iteration.
    """
    iteration: int
    phase: str
    one_sentence_summary: str               # What happened in one sentence
    key_decisions: list[str]                # Max 3 decision IDs
    artifacts_produced: list[str]           # File paths only
    blockers_resolved: list[str]            # What got unblocked
    witness_mark_ids: list[str]             # Proof of work

    @classmethod
    def from_context(cls, ctx: CompressedContext) -> "IterationSummary":
        """Compress a full context into a summary."""
        return cls(
            iteration=ctx.iteration,
            phase=derive_phase(ctx.iteration),
            one_sentence_summary=generate_summary(ctx),
            key_decisions=[d.id for d in ctx.decisions[:3]],
            artifacts_produced=[a.path for a in ctx.artifacts],
            blockers_resolved=[b.id for b in ctx.blockers if b.resolved],
            witness_mark_ids=[a.witness_mark_id for a in ctx.artifacts if a.witness_mark_id],
        )
```

### 2.3 Resonance Field (Replaces Needs/Offerings)

Instead of explicit "I need X from you" files, agents emit and sense **resonance signals**:

```python
@dataclass
class ResonanceField:
    """
    The resonance field is where agent intents interfere.

    Like a standing wave: when agents are in sync, they resonate.
    When out of sync, they create interference patterns that surface as blockers.
    """

    # Active signals (what's vibrating)
    active_signals: list[ResonanceSignal]

    # Interference patterns (where agents clash or block each other)
    interference: list[InterferencePattern]

    # Resolution history (how interference was resolved)
    resolutions: list[Resolution]

    def emit(self, agent: str, signal: ResonanceSignal) -> None:
        """Agent emits a signal into the field."""
        self.active_signals.append(signal)
        self._detect_interference()

    def sense(self, agent: str) -> list[ResonanceSignal]:
        """Agent senses signals relevant to them."""
        return [s for s in self.active_signals if s.affects(agent)]

    def _detect_interference(self) -> None:
        """Automatically detect when signals conflict."""
        for s1 in self.active_signals:
            for s2 in self.active_signals:
                if s1 != s2 and s1.interferes_with(s2):
                    self.interference.append(InterferencePattern(s1, s2))


@dataclass
class ResonanceSignal:
    """
    A single signal in the resonance field.

    Types:
    - INTENT: "I'm working on X" (broadcast)
    - NEED: "I'm blocked on Y" (request)
    - OFFER: "I've produced Z" (availability)
    - CLAIM: "I'm taking ownership of W" (lock)
    - RELEASE: "I'm done with W" (unlock)
    """

    source: str                             # creative, adversarial, player
    type: Literal["INTENT", "NEED", "OFFER", "CLAIM", "RELEASE"]
    topic: str                              # What this signal is about
    urgency: Literal["low", "normal", "high", "blocking"]
    timestamp: datetime
    expires_at: datetime | None             # Signals can expire
    evidence: str | None                    # Witness mark if applicable

    def affects(self, agent: str) -> bool:
        """Does this signal affect the given agent?"""
        # NEEDS affect everyone except source
        # OFFERS affect everyone
        # CLAIMS affect anyone who might claim the same topic
        # etc.
        return True  # Simplified; real logic depends on type

    def interferes_with(self, other: "ResonanceSignal") -> bool:
        """Does this signal interfere with another?"""
        # Two CLAIMs on same topic = interference
        # NEED + no OFFER on same topic = interference
        # etc.
        if self.type == "CLAIM" and other.type == "CLAIM":
            return self.topic == other.topic
        return False


@dataclass
class InterferencePattern:
    """When two signals conflict, this pattern emerges."""
    signal_a: ResonanceSignal
    signal_b: ResonanceSignal
    detected_at: datetime
    resolved: bool = False
    resolution: "Resolution | None" = None


@dataclass
class Resolution:
    """How an interference pattern was resolved."""
    pattern_id: str
    resolution_type: Literal["merge", "priority", "synthesis", "defer"]
    resolved_by: str                        # Which agent resolved it
    outcome: str                            # What was decided
    witness_mark_id: str                    # Proof
```

### 2.4 Progressive Compression Protocol

The key insight: **compress at iteration boundaries, not during work**.

```python
class ProgressiveCompressor:
    """
    Compresses orchestra state at iteration transitions.

    The compression protocol ensures:
    1. Current iteration has full context (~2000 tokens)
    2. Previous iteration has summary (~200 tokens)
    3. Older iterations have one-liner + mark IDs (~50 tokens)
    4. Total context never exceeds ~5000 tokens
    """

    def on_iteration_complete(self, state: OrchestraState) -> OrchestraState:
        """Called when iteration completes. Triggers compression."""

        # 1. Current context becomes history summary
        summary = IterationSummary.from_context(state.context)

        # 2. If history is getting long, compress older entries
        if len(state.history) > 5:
            state.history = self._compress_history(state.history)

        # 3. Add new summary to history
        state.history.append(summary)

        # 4. Clear context for new iteration
        state.context = CompressedContext(
            iteration=state.iteration + 1,
            mission="",  # Will be restated
            deliverables=[],
            decisions=[],
            blockers=[],
            artifacts=[],
        )

        # 5. Increment iteration
        state.iteration += 1

        return state

    def _compress_history(self, history: list[IterationSummary]) -> list[IterationSummary]:
        """
        Compress history when it gets too long.

        Strategy:
        - Keep last 3 iterations as full summaries
        - Compress earlier iterations to one-liners with mark IDs
        """
        if len(history) <= 3:
            return history

        # Keep recent
        recent = history[-3:]

        # Compress older
        older = history[:-3]
        compressed_older = [
            IterationSummary(
                iteration=s.iteration,
                phase=s.phase,
                one_sentence_summary=f"Iter {s.iteration}: {s.one_sentence_summary[:50]}...",
                key_decisions=[],  # Drop details
                artifacts_produced=[],
                blockers_resolved=[],
                witness_mark_ids=s.witness_mark_ids,  # Keep marks for recovery
            )
            for s in older
        ]

        return compressed_older + recent

    def recover_full_context(self, iteration: int, mark_ids: list[str]) -> CompressedContext:
        """
        Recover full context from witness marks if needed.

        This is the escape hatch: if compression loses something critical,
        we can always recover from the witness store.
        """
        # Fetch marks from witness store
        # Reconstruct context from mark evidence
        # Return full context
        pass
```

### 2.5 Self-Correcting Drift Detection

Agents don't wait for sync; they detect and resolve drift automatically:

```python
@dataclass
class DriftSignal:
    """A detected drift between agents."""
    type: Literal[
        "PHASE_MISMATCH",       # Agents think they're in different phases
        "ITERATION_MISMATCH",   # Agents think they're in different iterations
        "CONTEXT_DIVERGENCE",   # Agents have different understanding of context
        "INTENT_COLLISION",     # Agents working on same thing without knowing
        "STALE_AGENT",          # Agent hasn't acted in too long
    ]
    agents: list[str]           # Which agents are drifting
    description: str
    severity: Literal["info", "warning", "error"]
    auto_resolvable: bool


class DriftDetector:
    """Continuously monitors for drift and triggers resolution."""

    def detect(self, state: OrchestraState) -> list[DriftSignal]:
        """Detect all current drift signals."""
        signals = []

        # Phase mismatch: check if agents disagree on phase
        phases = [a.focus for a in state.agents.values() if "PHASE" in a.focus.upper()]
        if len(set(phases)) > 1:
            signals.append(DriftSignal(
                type="PHASE_MISMATCH",
                agents=list(state.agents.keys()),
                description=f"Agents report different phases: {phases}",
                severity="error",
                auto_resolvable=True,
            ))

        # Stale agent
        for name, agent in state.agents.items():
            if agent.is_stale(threshold_minutes=10):
                signals.append(DriftSignal(
                    type="STALE_AGENT",
                    agents=[name],
                    description=f"{name} hasn't acted in 10+ minutes",
                    severity="warning" if agent.status != "blocked" else "info",
                    auto_resolvable=False,
                ))

        # Intent collision
        intents = [(name, a.intent) for name, a in state.agents.items()]
        for (n1, i1), (n2, i2) in combinations(intents, 2):
            if self._intents_collide(i1, i2):
                signals.append(DriftSignal(
                    type="INTENT_COLLISION",
                    agents=[n1, n2],
                    description=f"Both working on similar task: {i1} vs {i2}",
                    severity="warning",
                    auto_resolvable=True,
                ))

        return signals

    def auto_resolve(self, signal: DriftSignal, state: OrchestraState) -> Resolution | None:
        """Attempt automatic resolution of drift."""
        if not signal.auto_resolvable:
            return None

        if signal.type == "PHASE_MISMATCH":
            # Canonical phase from iteration number
            canonical_phase = derive_phase(state.iteration)
            return Resolution(
                pattern_id=f"drift-{signal.type}",
                resolution_type="priority",
                resolved_by="system",
                outcome=f"Phase set to {canonical_phase} based on iteration {state.iteration}",
                witness_mark_id="auto",
            )

        if signal.type == "INTENT_COLLISION":
            # First-to-claim wins
            first = min(signal.agents, key=lambda a: state.agents[a].last_action)
            return Resolution(
                pattern_id=f"drift-{signal.type}",
                resolution_type="priority",
                resolved_by="system",
                outcome=f"{first} has priority (first to claim)",
                witness_mark_id="auto",
            )

        return None
```

---

## Part III: The Flow Protocol

### 3.1 From Stop-and-Go to Continuous Flow

**Old Model (Stop-and-Go)**:
```
CREATIVE: Read .focus.adversarial.md (509 lines) → 5 min
CREATIVE: Parse what changed → 2 min
CREATIVE: Work → 15 min
CREATIVE: Write .offerings.creative.md → 2 min
CREATIVE: Touch .pulse.creative → 1 sec
CREATIVE: Wait for ADVERSARIAL to read → ??? min
```

**New Model (Continuous Flow)**:
```
CREATIVE: Sense resonance field → 0.5 sec
CREATIVE: Emit INTENT signal → 0.5 sec
CREATIVE: Work → 15 min
CREATIVE: Emit OFFER signal (with mark) → 0.5 sec
// ADVERSARIAL senses OFFER in real-time
// No waiting, no file parsing
```

### 3.2 The Flow State Machine

```python
class FlowStateMachine:
    """
    Each agent runs this state machine.

    States:
    - SENSING: Checking resonance field
    - WORKING: Producing artifacts
    - EMITTING: Publishing signals
    - YIELDING: Waiting for interference resolution

    The machine never BLOCKS on other agents.
    It only YIELDS when interference is detected.
    """

    state: Literal["SENSING", "WORKING", "EMITTING", "YIELDING"]

    async def run(self, agent: str, orchestra: OrchestraState):
        """Main agent loop."""
        while orchestra.phase != "COMPLETE":
            match self.state:
                case "SENSING":
                    # Check for relevant signals
                    signals = orchestra.resonance.sense(agent)

                    # Check for blocking interference
                    blocking = [s for s in signals if s.urgency == "blocking"]
                    if blocking:
                        self.state = "YIELDING"
                        continue

                    # No blocks, proceed to work
                    self.state = "WORKING"

                case "WORKING":
                    # Do the actual work
                    # This is where CREATIVE builds, ADVERSARIAL tests, PLAYER plays
                    artifact = await self._do_work(agent, orchestra)

                    if artifact:
                        self.state = "EMITTING"
                    else:
                        self.state = "SENSING"  # Nothing produced, check again

                case "EMITTING":
                    # Emit signal about what we produced
                    orchestra.resonance.emit(agent, ResonanceSignal(
                        source=agent,
                        type="OFFER",
                        topic=artifact.name,
                        urgency="normal",
                        timestamp=datetime.now(),
                        expires_at=None,
                        evidence=artifact.witness_mark_id,
                    ))

                    self.state = "SENSING"

                case "YIELDING":
                    # Wait for interference resolution
                    await self._wait_for_resolution(orchestra)
                    self.state = "SENSING"
```

### 3.3 The Mission Restatement Ritual

At each iteration start, agents restate their mission. This is **generative compression**:

```python
def restate_mission(
    agent: str,
    iteration: int,
    history: list[IterationSummary],
    resonance: ResonanceField,
) -> str:
    """
    Generate a mission statement for this agent at this iteration.

    The restatement is NOT copied from previous iteration.
    It is GENERATED from:
    - The iteration number (determines phase focus)
    - The compressed history (what came before)
    - The resonance field (what's blocked, what's available)

    This is how context stays fresh without reading 500-line files.
    """
    phase = derive_phase(iteration)

    # What has been accomplished?
    accomplished = [h.one_sentence_summary for h in history[-3:]]

    # What's currently blocked?
    blocks = [s for s in resonance.active_signals
              if s.type == "NEED" and s.urgency == "blocking"]

    # What's available?
    offers = [s for s in resonance.active_signals if s.type == "OFFER"]

    # Generate mission
    if agent == "creative":
        if phase == "DESIGN":
            return f"Iteration {iteration}: Architecture and vision. Accomplished: {accomplished[-1] if accomplished else 'Starting fresh'}. Building: mood board, decisions, structure."
        elif phase == "EXECUTION":
            return f"Iteration {iteration}: Build with boldness. Recent: {accomplished[-1] if accomplished else 'Design complete'}. Priority: {blocks[0].topic if blocks else 'Continue building'}."
        else:
            return f"Iteration {iteration}: Polish and delight. Final touches on: {offers[-1].topic if offers else 'all systems'}."

    # Similar for adversarial and player...
    return f"Iteration {iteration}: {agent} at work."
```

---

## Part IV: Integration with kgents Primitives

### 4.1 PolyAgent Mapping

Each agent is a **PolyAgent** with positions = states in the flow machine:

```python
CREATIVE_ORCHESTRA_POLYNOMIAL = PolyAgent(
    name="CreativeOrchestra",
    positions=frozenset({"SENSING", "WORKING", "EMITTING", "YIELDING", "COMPLETE"}),
    _directions=lambda pos: match pos {
        "SENSING": frozenset({ResonanceSignal}),
        "WORKING": frozenset({Artifact, PartialWork}),
        "EMITTING": frozenset({ResonanceSignal}),
        "YIELDING": frozenset({Resolution}),
        "COMPLETE": frozenset(),
    },
    _transition=creative_orchestra_transition,
)
```

### 4.2 Operad Composition

The orchestra is an **operad expression**:

```
ORCHESTRA = dialectic(
    parallel(CREATIVE_POLY, ADVERSARIAL_POLY),
    player_overlay(PLAYER_POLY)
)
```

Where `dialectic` and `player_overlay` are operad operations that define how the agents compose.

### 4.3 Sheaf Coherence

The **OrchestraState** is the global section of a sheaf:

```
OrchestraSheaf:
  Base space: {creative, adversarial, player}
  Stalks: AgentPresence at each agent
  Sections: OrchestraState (consistent global state)

  Gluing conditions:
  - All agents agree on iteration number
  - All agents agree on phase
  - No unresolved blocking interference
  - Coherence score > 0.7
```

### 4.4 Witness Integration

Every artifact, decision, and resolution creates a witness mark:

```python
async def witness_orchestra_action(
    agent: str,
    action_type: str,
    action: Any,
    state: OrchestraState,
) -> str:
    """Witness an orchestra action."""
    mark = await witness.mark(
        action=f"[{agent}] {action_type}: {summarize(action)}",
        reasoning=f"Iteration {state.iteration}, Phase {state.phase}",
        tags=["orchestra", agent, state.phase.lower()],
        evidence={
            "iteration": state.iteration,
            "coherence_score": state.coherence_score(),
            "action_detail": action.to_dict() if hasattr(action, 'to_dict') else str(action),
        }
    )
    return mark.id
```

---

## Part V: Implementation Path

### 5.1 Migration Strategy

**Phase 1: Add OrchestraState alongside existing files**
- Create `.orchestra.json` that holds the new state
- Continue using `.focus`, `.needs`, etc. as fallback
- Agents read from OrchestraState first, fall back to files

**Phase 2: Migrate agents to FlowStateMachine**
- Update `generate_prompt.py` to generate flow-aware prompts
- Agents emit resonance signals instead of writing to files
- Files become write-only audit trail

**Phase 3: Remove file-based coordination**
- `.orchestra.json` is source of truth
- Files archived for debugging only
- Full continuous flow achieved

### 5.2 Prompt Changes

New prompt structure:

```markdown
# {ROLE} Orchestrator: {pilot}

**Iteration {N}/10 | Phase: {PHASE}**

## Your Mission (This Iteration)
{generated_mission}

## Context (Compressed)
{compressed_context}

## Resonance Field
Active signals: {count}
Blocking: {blocking_count}
Your pending: {your_pending}

## The Flow
1. SENSE: Check resonance field for blockers/offers
2. WORK: Produce artifacts with witness marks
3. EMIT: Signal what you produced
4. YIELD: If blocked, wait for resolution

## Quick Commands
```bash
kg orchestra sense             # See resonance field
kg orchestra emit --offer X    # Signal an offering
kg orchestra emit --need Y     # Signal a need
kg orchestra status            # Current coherence
```

---

*Flow, don't sync. Resonate, don't read. Compress, don't append.*
```

### 5.3 New Files

```
/tmp/kgents-regen/{pilot}/
  .orchestra.json              # OrchestraState (source of truth)
  .resonance.json              # ResonanceField (active signals)
  .history/
    iteration-001.json         # Compressed iteration summaries
    iteration-002.json
    ...
  .audit/                      # Legacy files for debugging
    .focus.creative.md
    ...
```

---

## Part VI: Expected Outcomes

### 6.1 Before vs After

| Metric | Before (File-Based) | After (Orchestra) |
|--------|---------------------|-------------------|
| Context at iteration 10 | 500+ lines per agent | ~200 tokens per agent |
| Sync overhead | 5-10 min per iteration | <1 sec (resonance sense) |
| Coherence detection | Manual (parse files) | Automatic (drift detector) |
| Recovery from drift | Manual reconciliation | Auto-resolution |
| Stale agent detection | Ambiguous pulse | Clear status + intent |
| Cross-agent blocking | Implicit (needs file) | Explicit (resonance signal) |

### 6.2 The Flow Experience

**Before**: "I need to read 509 lines to understand what ADVERSARIAL has been doing..."

**After**: "The resonance field shows ADVERSARIAL just offered `QualityOperad integration`. I can sense it's ready without reading anything."

**Before**: "I'll write to .needs.creative.md and hope CREATIVE reads it next iteration..."

**After**: "I'm emitting a NEED signal with urgency=blocking. CREATIVE will sense it immediately and either YIELD or resolve."

---

## Part VII: Open Questions

### 7.1 For Discussion

1. **How does PLAYER fit?** PLAYER's loop is different (IDLE → PLAY → ADVISE). Should PLAYER be a special case or fully integrated?

2. **What's the minimum viable orchestra?** Can we get 80% of benefit with 20% of complexity?

3. **Resonance signal persistence**: How long do signals live? Should they auto-expire?

4. **Cross-pilot coherence**: If multiple pilots run simultaneously, do they share a resonance field?

### 7.2 Risks

| Risk | Mitigation |
|------|------------|
| Complexity tax | Start with minimal OrchestraState, add features gradually |
| Resonance spam | Rate-limit signal emission, auto-expire old signals |
| Lost context | Keep witness marks as recovery mechanism |
| Agent confusion | Clear prompts explaining the new model |

---

## Appendix A: AGENTESE Paths

```
# Orchestra state
self.orchestra.state                        # Full OrchestraState
self.orchestra.coherence                    # Coherence score
self.orchestra.drift                        # Current drift signals

# Resonance
self.orchestra.resonance.sense              # Sense relevant signals
self.orchestra.resonance.emit               # Emit a signal
self.orchestra.resonance.interference       # Current interference

# Agent presence
self.orchestra.presence.{agent}             # AgentPresence for agent
self.orchestra.presence.update              # Update presence

# History
time.orchestra.history.{iteration}          # IterationSummary for iteration
time.orchestra.history.recover              # Recover full context from marks
```

---

## Appendix B: Example Run 023 Trace

```
[Iteration 1 Start]
OrchestraState: {iteration: 1, phase: DESIGN, coherence: 1.0}

CREATIVE: Sense → no signals
CREATIVE: Emit INTENT "Mood board and architecture"
CREATIVE: Work → produces mood board
CREATIVE: Emit OFFER "mood-board" (mark: m001)

ADVERSARIAL: Sense → sees CREATIVE's INTENT
ADVERSARIAL: Emit INTENT "Analyzing architecture options"
ADVERSARIAL: Work → produces spec analysis
ADVERSARIAL: Emit OFFER "spec-analysis" (mark: m002)

[Drift detected: none. Coherence: 0.95]

[Iteration 1 Complete]
History: ["Iter 1: Mood board + spec analysis complete. Decisions: DD-1, DD-2"]

[Iteration 2 Start]
CREATIVE: Sense → sees ADVERSARIAL's OFFER "spec-analysis"
CREATIVE: Incorporate spec insights
CREATIVE: Work → produces component interfaces
...

[Iteration 7]
PLAYER: Sense → sees OFFER "build-ready"
PLAYER: Work → plays game
PLAYER: Emit NEED "balance broken" urgency=blocking

CREATIVE: Sense → blocking NEED detected
CREATIVE: YIELD
CREATIVE: Resolve → "Adding debug death key + damage cap"
CREATIVE: Emit RESOLUTION
CREATIVE: Continue WORK

[Drift: PLAYER reports blocking, CREATIVE resolved in 2 min]
```

---

*"The orchestra doesn't synchronize. The orchestra resonates."*

---

## Cross-References

- `spec/protocols/algorithmic-todo.md` — Hierarchical todo with negotiation
- `spec/protocols/player-advocate.md` — PLAYER's unique loop
- `spec/protocols/regeneration-isomorphism.md` — PolyAgent/Operad/Sheaf mapping
- `spec/theory/experience-quality-operad.md` — Quality measurement framework
- `pilots/generate_prompt.py` — Current prompt generation

---

*Filed: 2025-12-27 | Version: 1.0 | Author: Claude (for Kent)*
