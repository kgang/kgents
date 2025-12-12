---
path: agents/semaphores
status: active
progress: 95
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [void/entropy]
session_notes: |
  Phases 1-5 COMPLETE (138 tests):
  - Phase 1: SemaphoreToken, ReentryContext, Purgatory (49 tests)
  - Phase 2: Flux Integration - JSON serialization, deadline checking,
    pheromone emission, SemaphoreMixin, flux_integration.py (70 tests)
  - Phase 3: DurablePurgatory with D-gent backing (19 tests)
  - Phase 4: AGENTESE paths - self.semaphore.*, world.purgatory.*
  - Phase 5: CLI handler - kgents semaphore list/resolve/cancel/inspect/void

  Remaining: QA integration testing, wire CLI to Cortex daemon singleton
---

# Agent Semaphores: The Rodizio Pattern

> *"The diner flips the card. The gaucho waits. This is not blocking—this is respect."*

**AGENTESE Context**: `self.semaphore.*`, `world.purgatory.*`
**Status**: Phase 1 Complete, Phase 2 Ready
**Principles**: Ethical (human agency), Heterarchical (neither boss), Composable (generators)
**Cross-refs**: `void/entropy` (metabolism pressure), Flux (perturbation queue)

---

## Core Insight

Traditional human-in-the-loop is binary: ask question, wait for answer, continue. This is the **interrupt model**.

Agent Semaphores embrace the **yield model**:
- The agent yields a **SemaphoreToken** (the red card)
- Execution suspends **indefinitely** (not timeout)
- Human hydrates context (flips to green)
- Agent resumes with enriched state
- The whole interaction is a **Python generator** (conceptually)

```
Agent Flow                    Human                     Agent Flow
┌──────────┐                 ┌────────┐                ┌──────────┐
│ Process  │                 │        │                │ Resume   │
│ Events   │───yield card───▶│ Review │───flip green──▶│ With     │
│ ...      │     (RED)       │ Approve│    (GREEN)     │ Context  │
└──────────┘                 │ Enrich │                └──────────┘
     │                       └────────┘                      │
     └───────────────── Time (indefinite) ──────────────────┘

Key: The agent does NOT poll. It yields. The human acts when ready.
```

---

## The Purgatory Pattern (Critical Architecture)

The theoretical generator encoding is elegant but **not directly implementable** in Python:

1. **Python generators cannot be pickled**—if the server restarts, the stack frame is lost
2. **Head-of-line blocking**—one semaphore blocks the entire Flux stream

**Resolution**: The Purgatory Pattern.

Instead of pausing the generator, we **eject** the state:

```
Flux Stream        Purgatory         Human           Flux Stream
┌──────────┐      ┌──────────┐      ┌────────┐      ┌──────────┐
│ Event A  │──────│  Eject   │      │        │      │ Context  │
│ needs    │ ──→  │  & Save  │ ──→  │ Review │ ──→  │ Re-inject│
│ human    │      │ state    │      │ & Flip │      │ as Perturb│
└──────────┘      └──────────┘      └────────┘      └──────────┘
     │                                                    │
     │               ┌──────────┐                         │
     └──────────────▶│ Event B  │◀────────────────────────┘
                     │ proceeds │
                     └──────────┘

Key: Stream CONTINUES. Blocked event waits in Purgatory, not in flux.
```

**The Mechanism**:
1. **Detect**: Agent returns `f(Event) → SemaphoreToken`
2. **Eject**: FluxAgent saves `(Event, PartialState)` to Purgatory (D-gent backed)
3. **Continue**: Stream yields `None`, proceeds to Event B
4. **Resolve**: Human flips the card (Green)
5. **Re-inject**: Purgatory injects `ReentryContext` as high-priority Perturbation
6. **Resume**: Agent processes context via `resume(state, human_input) → Result`

---

## Semaphore Types (The Taxonomy)

| Type | Icon | Use Case | Example |
|------|------|----------|---------|
| **Approval** | SHIELD | Sensitive actions requiring explicit approval | "Delete 47 user records?" |
| **Context** | BOOK | Agent needs information only human has | "Which database environment?" |
| **Ambiguity** | THINK | Multiple valid interpretations | "'Bank' means financial or river?" |
| **Resource** | MONEY | Resource allocation decision | "Scaling requires 4 GPUs ($2,400/day)" |
| **Recovery** | WRENCH | Error occurred, human guidance needed | "API rate limited. Wait or switch?" |

---

## AGENTESE Path Integration

| Path | Operation | Returns |
|------|-----------|---------|
| `self.semaphore.yield` | Create semaphore token | SemaphoreToken |
| `self.semaphore.pending` | List pending semaphores | SemaphoreToken[] |
| `self.semaphore.resolve` | Provide human context | ResolveResult |
| `self.semaphore.cancel` | Cancel pending semaphore | CancelResult |
| `world.purgatory.manifest` | View all ejected tokens | SemaphoreToken[] |
| `world.purgatory.resolve` | Resolve with context | ResolveResult |
| `world.purgatory.gc` | Garbage collect stale | GCResult |
| `world.semaphore.escalate` | Route to another human | EscalationResult |
| `time.semaphore.deadline` | Set/check deadline | DeadlineStatus |

---

## Integration Points

### With Flux (Perturbation Reuse)

Semaphores reuse the existing perturbation queue:

```python
# Resolution: inject ReentryContext as Perturbation
perturbation = create_perturbation(reentry, priority=200)  # High priority
await flux_agent._perturbation_queue.put(perturbation)
```

### With Symbiont (Durability)

Purgatory persists to D-gent:
- State is checkpointed before yield
- State is recovered on restart
- Human response is applied to correct checkpoint

### With Metabolism (void.entropy.*)

Semaphores exist in a separate queue from data events:
- They don't contribute to Flux pressure metrics
- They DO contribute to system-wide metabolism (`void.entropy.pressure`)

---

## Implementation Phases

### Phase 1: SemaphoreToken, ReentryContext, and Purgatory

**Goal**: Define core types and the Purgatory store.

**Files**:
```
impl/claude/agents/flux/
├── semaphore/
│   ├── __init__.py
│   ├── token.py            # SemaphoreToken dataclass
│   ├── reentry.py          # ReentryContext dataclass
│   ├── purgatory.py        # Purgatory store (D-gent backed)
│   ├── reason.py           # SemaphoreReason enum
│   └── _tests/
```

**Exit Criteria**: Agent can return token, test handler can resolve.

### Phase 2: Flux Integration with Purgatory

**Goal**: Integrate semaphores into FluxAgent's event loop.

**Key**: We do NOT block the stream. We eject to Purgatory and continue.

**Files**:
```
impl/claude/agents/flux/
├── agent.py                # Add semaphore detection and ejection
└── semaphore/
    ├── mixin.py            # SemaphoreMixin for agents that yield
    ├── flux_integration.py # Extended _process_event logic
```

**Exit Criteria**: FluxAgent can eject and resume.

### Phase 3: Symbiont Integration (Durability)

**Goal**: Persist semaphore state for crash recovery.

**Files**:
```
impl/claude/agents/flux/semaphore/
├── durable.py          # DurableSemaphoreState
├── symbiont.py         # SemaphoreSymbiont
```

**Exit Criteria**: Agent restart preserves pending semaphores.

### Phase 4: AGENTESE Paths

**Goal**: Wire `self.semaphore.*` and `world.purgatory.*` paths.

**Files**:
```
impl/claude/protocols/agentese/contexts/
└── self.py             # Add self.semaphore.* paths
```

**Exit Criteria**: Human can resolve semaphore via Logos invocation.

### Phase 5: CLI Integration

**Goal**: `kgents semaphore` commands for human interaction.

**Commands**:
```bash
kgents semaphore list
kgents semaphore show sem-abc123
kgents semaphore resolve sem-abc123 --context '{"env": "staging"}'
kgents semaphore cancel sem-abc123
kgents semaphore resolve sem-abc123 --interactive
```

**Exit Criteria**: Human can resolve semaphore via CLI.

---

## Key Types

```python
@dataclass
class SemaphoreToken(Generic[R]):
    """The Red Card. Return this to flip red."""
    id: str  # sem-{uuid}
    reason: SemaphoreReason
    frozen_state: bytes  # Pickled agent state at ejection
    original_event: Any
    required_type: type[R] | None = None
    deadline: datetime | None = None
    escalation: str | None = None
    # UI metadata
    prompt: str = ""
    options: list[str] = field(default_factory=list)
    severity: str = "info"  # "info" | "warning" | "critical"

@dataclass
class ReentryContext(Generic[R]):
    """The Green Card. Injected back as Perturbation."""
    token_id: str
    frozen_state: bytes
    human_input: R
    original_event: Any

class SemaphoreCapable(Protocol):
    """Protocol for agents that can yield semaphores."""
    async def resume(self, frozen_state: bytes, human_input: Any) -> B: ...
```

---

## Principle Assessment

| Principle | Assessment |
|-----------|------------|
| **Tasteful** | Single pattern: return → wait → resume |
| **Curated** | Not a workflow engine, just the yield primitive |
| **Ethical** | EXPLICIT human agency: agent cannot proceed without human |
| **Joy-Inducing** | The card flip is satisfying; the metaphor is delightful |
| **Composable** | Works with Flux and Symbiont via Perturbation |
| **Heterarchical** | Neither agent nor human is "boss"—they collaborate |
| **Generative** | Five semaphore types derive from base pattern |

---

## Self-Debate Resolutions

### Q: Why not just use asyncio.Event?

Events are volatile. If the process restarts, the event is gone. Agent Semaphores are DURABLE via the Symbiont pattern.

### Q: Isn't this just Temporal signals?

Agent Semaphores are the **kgents-native** equivalent. Lighter weight (no Temporal server), integrated with AGENTESE paths, composable with other kgents patterns.

### Q: What about timeout and cleanup?

The rodizio pattern IS indefinite. Optional `deadline` and `escalation` fields enable:
- Auto-escalation after deadline
- GC for old unresolved semaphores

### Q: What about multiple yields?

Each yield becomes an independent ejection. Multiple events can be in Purgatory simultaneously. Ordering semantics = resolution order, not yield order.

---

## Cross-References

- **Spec**: `spec/c-gents/flux.md` — FluxAgent foundation
- **Spec**: `spec/d-gents/symbiont.md` — Durable state pattern
- **Spec**: `spec/principles.md` S3 (Ethical) — Human agency preserved
- **Plan**: `plans/void/entropy.md` — Metabolism integration
- **Impl**: `impl/claude/agents/flux/` — FluxAgent implementation
- **Impl**: `impl/claude/agents/flux/perturbation.py` — Perturbation pattern (reused)

---

*"The card speaks. The gaucho listens. The purgatory remembers. This is the protocol."*
