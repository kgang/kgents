---
path: protocols/warp-primitives
status: partial_impl
spec_type: protocol
category: core
dependencies: [protocols/n-phase-cycle, protocols/agentese]
enables: [services/witness-warp, protocols/servo-substrate]
agentese_paths:
  - time.trace.node.*
  - time.walk.*
  - self.ritual.*
  - concept.offering.*
  - concept.intent.*
  - self.covenant.*
  - brain.terrace.*
  - self.voice.gate.*
last_touched: 2025-12-20
touched_by: claude-opus-4
---

# WARP Primitives Protocol

**Status:** Partial Implementation
**Implementation:** `impl/claude/services/witness/` + `impl/claude/protocols/agentese/contexts/` (230+ tests)

> *"Every action is a TraceNode. Every session is a Walk. Every workflow is a Ritual."*

---

## Purpose

Establish the foundational primitives that enable WARP-grade ergonomics within kgents while preserving categorical laws and constitutional alignment. These primitives form the substrate for trace-first history, explicit context contracts, and lawful workflow orchestration.

---

## Core Insight

**The block is the atom.** WARP's brilliance is making every interaction traceable, replayable, and composable. kgents must do the same, but under Witness + Time + Category Theory.

---

## Type Signatures

### TraceNode (WARP Block → `time.trace.*`)

```python
@dataclass(frozen=True)
class TraceNode:
    """Atomic unit of execution artifact."""
    id: TraceNodeId
    origin: JewelOrAgent       # What emitted it
    stimulus: Stimulus         # Prompt, command, or event
    response: Response         # Output, diff, or state transition
    umwelt: UmweltSnapshot     # Observer capabilities at emission
    links: list[TraceLink]     # Causal edges (plan → node, node → node)
    timestamp: datetime
    phase: NPhase | None       # If within N-Phase workflow

@dataclass(frozen=True)
class TraceLink:
    """Causal edge between TraceNodes or to plans."""
    source: TraceNodeId | PlanPath
    target: TraceNodeId
    relation: LinkRelation     # CAUSES, CONTINUES, BRANCHES, FULFILLS
```

### Walk (WARP Conversation → `time.walk.*`)

```python
@dataclass
class Walk:
    """Durable work stream tied to Forest plans."""
    id: WalkId
    goal: IntentId             # What we're trying to achieve
    root_plan: PlanPath        # Plans/*.md leaf
    trace_nodes: list[TraceNodeId]  # Ordered execution history
    participants: list[ParticipantId]  # Agents + umwelts
    phase: NPhase              # Current N-Phase position
    started_at: datetime
    status: WalkStatus         # ACTIVE, PAUSED, COMPLETE, ABANDONED
```

### Ritual (WARP Agent Mode → `self.ritual.*`)

```python
@dataclass
class Ritual:
    """Curator-orchestrated workflow with explicit gates."""
    id: RitualId
    intent: IntentId
    phases: list[RitualPhase]  # State machine (N-Phase compatible)
    guards: list[SentinelGuard]  # Checks at each boundary
    tools: list[AgentCapability]  # Registered capabilities
    covenant: CovenantId       # Permission context
    offering: OfferingId       # Resource context
    status: RitualStatus

@dataclass
class RitualPhase:
    """Single phase in ritual state machine."""
    name: str
    entry_guards: list[GuardId]
    exit_guards: list[GuardId]
    allowed_actions: list[ActionPattern]
    timeout: timedelta | None
```

### Offering (WARP Context → `concept.offering.*`)

```python
@dataclass
class Offering:
    """Explicitly priced and scoped context."""
    id: OfferingId
    handles: list[HandlePattern]  # brain.*, world.file.*, plans.*, time.trace.*
    budget: Budget             # Capital, entropy, token constraints
    contracts: list[CapabilityContract]  # Read/write caps by agent
    expires_at: datetime | None

@dataclass
class Budget:
    """Resource constraints for an Offering."""
    capital: float | None      # Max cost
    entropy: float | None      # Max entropy consumption
    tokens: int | None         # Max LLM tokens
    time: timedelta | None     # Max wall-clock time
```

### IntentTree (WARP Tasks → `concept.intent.*`)

```python
class IntentType(Enum):
    """Typed intent categories."""
    EXPLORE = auto()
    DESIGN = auto()
    IMPLEMENT = auto()
    REFINE = auto()
    VERIFY = auto()
    ARCHIVE = auto()

@dataclass
class Intent:
    """Typed goal node in the intent graph."""
    id: IntentId
    type: IntentType
    description: str
    parent: IntentId | None
    children: list[IntentId]
    dependencies: list[IntentId]
    capabilities_required: list[CapabilityPattern]
    status: IntentStatus       # PENDING, ACTIVE, COMPLETE, BLOCKED

@dataclass
class IntentTree:
    """Typed intent graph with dependencies."""
    root: IntentId
    nodes: dict[IntentId, Intent]
    edges: list[IntentEdge]    # Dependencies with capability requirements
```

### Covenant (WARP Permissions → `self.covenant.*`)

```python
@dataclass
class Covenant:
    """Negotiated permission contract."""
    id: CovenantId
    allowed_handles: list[HandlePattern]
    budget: Budget
    review_gates: list[ReviewGate]  # Human or K-gent checkpoints
    degradation_tiers: list[DegradationTier]  # Fallback under stress
    granted_at: datetime
    expires_at: datetime | None
    amended_by: list[CovenantAmendment]

@dataclass
class ReviewGate:
    """Explicit approval checkpoint."""
    trigger: GateTrigger       # ON_MUTATION, ON_BUDGET_EXCEED, ON_EXTERNAL
    reviewer: ReviewerId       # Human or K-gent
    timeout: timedelta
    fallback: GateFallback     # DENY, ALLOW_LIMITED, ESCALATE
```

### Terrace (Versioned Knowledge → `brain.terrace.*`)

> *Design Refinement*: The original vision of Terrace as a container for workflow artifacts was refined during implementation. The "installable workflow bundle" use case is served by `WorkflowTemplate` (see `impl/claude/services/witness/workflows.py`). Terrace focuses on versioned knowledge documents — capturing learnings that evolve across sessions.

```python
@dataclass(frozen=True)
class Terrace:
    """Curated, versioned knowledge document."""
    id: TerraceId
    topic: str                    # e.g., "AGENTESE registration"
    content: str                  # The curated knowledge
    version: int
    supersedes: TerraceId | None  # Previous version this replaces
    status: TerraceStatus         # CURRENT, SUPERSEDED, DEPRECATED, ARCHIVED
    tags: tuple[str, ...]
    source: str                   # Where this knowledge came from
    confidence: float             # 0.0-1.0
    created_at: datetime

class TerraceStatus(Enum):
    CURRENT = auto()      # The active version for its topic
    SUPERSEDED = auto()   # Replaced by a newer version
    DEPRECATED = auto()   # Marked as no longer recommended
    ARCHIVED = auto()     # Kept for historical reference only
```

**Philosophy**: Knowledge crystallizes over time. A Terrace captures what we've learned, versioned for evolution. Like geological terraces, each layer builds on the last.

**Use Cases**:
- "I learned X about AGENTESE registration" → `Terrace.create(topic="AGENTESE registration", content="...")`
- "I found a better pattern" → `terrace.evolve(content="...", reason="Added silent skip warning")`
- "What do we know about testing?" → `store.search("testing")`
- "How did this knowledge evolve?" → `store.history("AGENTESE registration")`

**Note**: For bundling workflows, intents, and traces into installable packages, see `WorkflowTemplate` which provides composable pipelines with category taxonomy and trust levels.

### VoiceGate (WARP NL Detection → `self.voice.gate.*`)

```python
@dataclass
class VoiceGate:
    """Anti-Sausage enforcement point."""
    id: VoiceGateId
    rules: list[VoiceRule]
    anchors: list[VoiceAnchor]  # Kent's voice patterns
    denylists: list[DenyPattern]  # Sausage patterns to reject

@dataclass
class VoiceRule:
    """Single voice constraint."""
    pattern: str               # Regex or semantic pattern
    action: VoiceAction        # PASS, WARN, BLOCK, TRANSFORM
    reason: str
```

### TerrariumView (WARP Panes → `world.terrarium.view.*`)

```python
@dataclass
class TerrariumView:
    """Configured projection over substrate."""
    id: TerrariumViewId
    name: str
    selection: SelectionQuery  # What to show
    lens: LensConfig           # How to transform
    target: ProjectionTarget   # Where to render (servo, cli, marimo)
    layout: LayoutConfig       # Spatial arrangement
```

---

## Laws/Invariants

### TraceNode Laws

```
Law 1 (Immutability): TraceNodes are frozen after creation
Law 2 (Causality): link.target.timestamp > link.source.timestamp
Law 3 (Completeness): Every AGENTESE invocation emits exactly one TraceNode
```

### Walk Laws

```
Law 1 (Monotonicity): trace_nodes only grows, never shrinks
Law 2 (Phase Coherence): phase transitions follow N-Phase grammar
Law 3 (Plan Binding): root_plan must exist in Forest
```

### Ritual Laws

```
Law 1 (Covenant Required): Every Ritual has exactly one Covenant
Law 2 (Offering Required): Every Ritual has exactly one Offering
Law 3 (Guard Transparency): Guards emit TraceNodes on evaluation
Law 4 (Phase Ordering): Phase transitions follow directed cycle (Pattern 9)
```

### Offering Laws

```
Law 1 (Budget Enforcement): Exceeding budget triggers Covenant review
Law 2 (Handle Scoping): Only handles in scope are accessible
Law 3 (Expiry Honored): Expired Offerings deny all access
```

### Terrace Laws

```
Law 1 (Immutability): Terraces are frozen after creation
Law 2 (Supersession): New versions explicitly supersede old via supersedes field
Law 3 (History Preserved): All versions are kept for reference
Law 4 (Topic Uniqueness): One CURRENT version per topic at any time
```

---

## Integration

### AGENTESE Paths

| Primitive | Path | Aspects |
|-----------|------|---------|
| TraceNode | `time.trace.node.*` | manifest, capture, query, replay |
| Walk | `time.walk.*` | manifest, create, advance, pause, complete |
| Ritual | `self.ritual.*` | manifest, begin, advance, guard, complete |
| Offering | `concept.offering.*` | manifest, create, consume, extend, expire |
| IntentTree | `concept.intent.*` | manifest, create, decompose, fulfill |
| Covenant | `self.covenant.*` | manifest, propose, negotiate, grant, amend |
| Terrace | `brain.terrace.*` | manifest, create, evolve, search, history |
| VoiceGate | `self.voice.gate.*` | check, enforce, report |
| TerrariumView | `world.terrarium.view.*` | manifest, create, update, project |

### CLI v7 Wiring

| CLI Component | WARP Primitive |
|---------------|----------------|
| Conversation Window | TraceNode feed |
| Session | Walk |
| Conductor | Ritual orchestrator |
| Context Preview | Offering projection |
| Task Decomposition | IntentTree |
| Collaborative Canvas | TerrariumView |

---

## Anti-Patterns

1. **TraceNodes without links**: Every TraceNode must trace causality
2. **Rituals without Covenants**: Permissions must be explicit, not assumed
3. **Offerings without budgets**: Context must be priced
4. **Walks without plans**: Sessions must anchor to Forest
5. **VoiceGate bypass**: All entrypoints must pass Anti-Sausage check

---

## Implementation Reference

See:
- `impl/claude/services/witness/` (TraceNode, Walk)
- `impl/claude/protocols/agentese/contexts/self_ritual.py` (Ritual)
- `impl/claude/protocols/agentese/contexts/concept_offering.py` (Offering)
- `impl/claude/protocols/agentese/contexts/concept_intent.py` (IntentTree)
- `impl/claude/protocols/agentese/contexts/self_covenant.py` (Covenant)
- `impl/claude/services/witness/terrace.py` (Terrace) — 61 tests
- `impl/claude/services/witness/voice_gate.py` (VoiceGate) — 75 tests
- `impl/claude/services/witness/workflows.py` (WorkflowTemplate) — bundled pipelines
- `impl/claude/protocols/agentese/contexts/brain_terrace.py` (TerraceNode) — AGENTESE node
- `impl/claude/protocols/agentese/contexts/self_voice.py` (VoiceGateNode) — AGENTESE node
- `impl/claude/protocols/agentese/projection/` (SceneGraph, TerrariumView) — 95 tests

---

*"Servo supplies the surface; Rust supplies the laws."*
