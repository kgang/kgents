---
path: agent-town/builders-workshop
status: active
progress: 45
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town-monetization-mvp
  - agent-town-web-ui
  - agent-town-inhabit
  - revenue/first-dollar
session_notes: |
  SESSION 2025-12-15 (continued): Chunk 5 COMPLETE (5 Builder Classes)

  COMPLETED:
  - Chunk 1: TelegramNotifier (agents/town/telegram_notifier.py, 400 lines, 27 tests)
  - Chunk 2: Webhook→Telegram wire (protocols/api/webhooks.py modified)
  - Chunk 3: CLI handler (`kg town telegram status|test|payment`)
  - Chunk 4: BUILDER_POLYNOMIAL (agents/town/builders/polynomial.py, ~400 lines, 71 tests)
  - Chunk 5: 5 Builder classes (sage, spark, steady, scout, sync) + base.py, cosmotechnics.py, voice.py (132 tests total)

  CHUNK 5 NEW FILES:
  - agents/town/builders/base.py (Builder class extending Citizen)
  - agents/town/builders/cosmotechnics.py (5 builder cosmotechnics)
  - agents/town/builders/voice.py (5 voice pattern tuples)
  - agents/town/builders/sage.py (create_sage factory)
  - agents/town/builders/spark.py (create_spark factory)
  - agents/town/builders/steady.py (create_steady factory)
  - agents/town/builders/scout.py (create_scout factory)
  - agents/town/builders/sync.py (create_sync factory)
  - agents/town/builders/_tests/test_builders.py (61 tests)

  KEY DESIGN DECISIONS:
  - Builder extends Citizen (composition, not wrapper) adding specialty, voice_patterns, _builder_phase
  - Dual state machines: CitizenPolynomial (life phases) + BuilderPolynomial (work phases) operate in parallel
  - 5 cosmotechnics: ARCHITECTURE, EXPERIMENTATION, CRAFTSMANSHIP, DISCOVERY, ORCHESTRATION
  - Eigenvector profiles tuned for distinct personalities (e.g., Spark: high creativity 0.95, low patience 0.3)
  - Factory pattern: create_sage(), create_spark(), etc.

  NEXT: Chunk 6 (WorkshopEnvironment)

  REMAINING CHUNKS (6-9):
  6. WorkshopEnvironment
  7. WorkshopFlux
  8. Web projection
  9. Public metrics dashboard

  BLOCKERS (Kent action still required):
  - Telegram: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID from @BotFather
  - Stripe: STRIPE_SECRET_KEY, product/price IDs
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: touched
  CROSS-SYNERGIZE: pending
  IMPLEMENT: complete
  QA: pending
  TEST: complete
  EDUCATE: pending
  MEASURE: pending
  REFLECT: touched
entropy:
  planned: 0.15
  spent: 0.07
  remaining: 0.08
---

# Builder's Workshop: The Default Agent Town

> *"Chefs in a kitchen. Cooks in a garden. Kids on a playground. But they're building software."*

**AGENTESE Context**: `world.workshop.*`, `world.builder.*`
**Status**: Dormant (ready for PLAN phase)
**Principles**: Joy-Inducing, Composable, Tasteful, Ethical
**Cross-refs**:
- `docs/vision-unified-systems-enhancements.md` §5.0
- `plans/agent-town/grand-strategy.md`
- `plans/agent-town/phase8-inhabit.md`
- `spec/principles.md` (AD-006: Unified Categorical Foundation)

---

## Core Insight

The default Agent Town should not be a passive simulation to observe—it should be a **collaborative software workshop** where AI builder personas actively help you create.

This shifts the value proposition from "watch AI agents" to "work with AI teammates."

---

## The Vision

### The Five Core Builders

| Builder | Archetype | Polynomial Position | Specialty | Voice |
|---------|-----------|---------------------|-----------|-------|
| **Sage** | Architect | DESIGNING | System design, patterns, tradeoffs | "Have we considered..." |
| **Spark** | Experimenter | PROTOTYPING | Spikes, wild ideas, rapid iteration | "What if we tried..." |
| **Steady** | Craftsperson | REFINING | Clean code, tests, documentation | "Let me polish this..." |
| **Scout** | Researcher | EXPLORING | Prior art, libraries, alternatives | "I found something..." |
| **Sync** | Coordinator | INTEGRATING | Dependencies, blockers, handoffs | "Here's the plan..." |

### The Three Metaphors

**Chefs in a Kitchen**:
- Builders have specialties (mise en place)
- They prep components before the rush
- Coordination is implicit, expertise is explicit
- The kitchen has stations; each builder owns theirs

**Cooks in a Garden**:
- Some work is slow-growing (architecture decisions)
- Builders tend long-running tasks overnight
- Seasonal rhythms: burst of activity, then cultivation
- The garden produces; the cooks enable

**Kids on a Playground**:
- Creativity emerges from safe play
- Builders try wild ideas without fear
- Joy is the medium, not just the outcome
- The playground has rules, but play is free

---

## Implementation Phases

### Phase 1: Builder Polynomials (Foundation)

**Goal**: Define builders as polynomial agents with state-dependent behavior.

**Files**:
```
impl/claude/agents/town/builders/
├── __init__.py
├── polynomial.py      # BUILDER_POLYNOMIAL
├── sage.py            # Sage builder implementation
├── spark.py           # Spark builder implementation
├── steady.py          # Steady builder implementation
├── scout.py           # Scout builder implementation
├── sync.py            # Sync builder implementation
└── _tests/
    └── test_builders.py
```

**Key Types**:
```python
BUILDER_POLYNOMIAL = PolyAgent(
    positions=frozenset([
        "IDLE",        # Awaiting task
        "EXPLORING",   # Scout's specialty
        "DESIGNING",   # Sage's specialty
        "PROTOTYPING", # Spark's specialty
        "REFINING",    # Steady's specialty
        "INTEGRATING", # Sync's specialty
    ]),
    directions=builder_directions,
    transition=builder_transition,
)

@dataclass(frozen=True)
class Builder:
    """A workshop builder with personality and expertise."""
    name: str
    archetype: str
    eigenvectors: tuple[float, ...]  # 7D personality space
    specialty: BuilderPhase
    voice_patterns: tuple[str, ...]
```

**Exit Criteria**:
- [ ] BUILDER_POLYNOMIAL defined and tested
- [ ] Five builder classes instantiated
- [ ] Eigenvectors tuned for distinct personalities
- [ ] 50+ tests passing

### Phase 2: Workshop Environment

**Goal**: Create the workshop as a specialized Town environment.

**Files**:
```
impl/claude/agents/town/workshop.py        # WorkshopEnvironment
impl/claude/agents/town/workshop_flux.py   # WorkshopFlux (streaming)
```

**Key Types**:
```python
@dataclass(frozen=True)
class WorkshopState:
    """State of the builder's workshop."""
    builders: tuple[BuilderState, ...]
    active_task: Task | None
    artifacts: tuple[Artifact, ...]
    phase: WorkshopPhase  # IDLE, RESEARCHING, DESIGNING, BUILDING, REVIEWING

class WorkshopEnvironment(TownEnvironment):
    """Specialized environment for collaborative building."""

    async def assign_task(self, task: str) -> WorkshopPlan:
        """Distribute task across builders."""
        ...

    async def observe_progress(self) -> AsyncIterator[WorkshopEvent]:
        """Stream workshop activity."""
        ...
```

**Exit Criteria**:
- [ ] WorkshopEnvironment extends TownEnvironment
- [ ] Task assignment distributes work to appropriate builders
- [ ] Streaming events flow through WorkshopFlux
- [ ] 40+ tests passing

### Phase 3: CLI Integration

**Goal**: `kg town` defaults to Builder's Workshop.

**Files**:
```
impl/claude/protocols/cli/handlers/workshop.py
```

**Commands**:
```bash
kg town                    # Opens Builder's Workshop (default)
kg town workshop           # Explicit workshop
kg town observe            # Legacy: generic town simulation
kg town workshop --task "add dark mode"  # Start with task
kg workshop sage           # INHABIT the Sage builder
```

**Exit Criteria**:
- [ ] `kg town` launches workshop by default
- [ ] Task can be provided via --task flag
- [ ] INHABIT works with builders
- [ ] Help text explains the workshop concept

### Phase 4: Dialogue & Collaboration

**Goal**: Builders talk to each other and to the user naturally.

**Integration with existing DialogueEngine**:
```python
WORKSHOP_DIALOGUE_OPERAD = Operad(
    operations={
        "handoff": ...,      # One builder passes to another
        "consult": ...,      # Builder asks another for input
        "celebrate": ...,    # Builders acknowledge success
        "debate": ...,       # Constructive disagreement
        "user_query": ...,   # Builder asks user for clarification
    }
)
```

**Exit Criteria**:
- [ ] Builders converse naturally during task execution
- [ ] Handoffs are explicit and logged
- [ ] User can be queried when needed
- [ ] Dialogue feels playful, not robotic

### Phase 5: Web Projection

**Goal**: Workshop renders in web UI with builder personas visible.

**Integration with existing town web UI work**:
- Builders shown as characters in isometric view
- Current activity visible per builder
- Click to WHISPER or INHABIT
- Task progress visible as artifact stream

**Exit Criteria**:
- [ ] Workshop renders in web UI
- [ ] Builder status visible
- [ ] Interactions work (whisper, inhabit)
- [ ] Task artifacts stream to UI

---

## Workshop Operad

```python
WORKSHOP_OPERAD = Operad(
    operations={
        # Task flow
        "assign": Operation(arity=1, compose=assign_compose),
        "handoff": Operation(arity=2, compose=handoff_compose),
        "complete": Operation(arity=1, compose=complete_compose),

        # Collaboration
        "consult": Operation(arity=2, compose=consult_compose),
        "debate": Operation(arity=2, compose=debate_compose),
        "celebrate": Operation(arity=0, compose=celebrate_compose),

        # User interaction
        "query_user": Operation(arity=1, compose=query_user_compose),
        "present": Operation(arity=1, compose=present_compose),
    },
    laws=[
        # Identity: empty task = no change
        # Associativity: (assign >> handoff) >> complete = assign >> (handoff >> complete)
        # Locality: builders only affect their specialty phase
    ],
)
```

---

## AGENTESE Paths

| Path | Meaning | Returns |
|------|---------|---------|
| `world.workshop.manifest` | Current workshop state | WorkshopState |
| `world.workshop.task.assign` | Assign new task | WorkshopPlan |
| `world.builder.sage.manifest` | Sage's current state | BuilderState |
| `world.builder.sage.whisper` | Send message to Sage | Response |
| `world.builder.*.handoff` | Builder hands off to another | HandoffEvent |

---

## Monetization Integration

| Tier | Builders | Features |
|------|----------|----------|
| **Free** | 2 (Sage, Steady) | Basic workshop |
| **Resident** | 5 (all core) | Full workshop, WHISPER |
| **Citizen** | 5 + custom | INHABIT, custom builders |
| **Enterprise** | Unlimited | Private workshops, team builders |

---

## Cross-References

- **Spec**: `spec/protocols/agentese.md`, `spec/principles.md` (AD-006)
- **Plan**: `plans/agent-town/grand-strategy.md`, `plans/agent-town/phase8-inhabit.md`
- **Impl**: `impl/claude/agents/town/`, `impl/claude/protocols/cli/handlers/town.py`
- **Vision**: `docs/vision-unified-systems-enhancements.md` §5.0

---

## Success Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Task completion time | <5 min for simple tasks | Productive collaboration |
| User satisfaction | NPS >50 | Joy-inducing experience |
| Return sessions | >3 per user | People come back |
| "Kent says amazing" | Yes | The Mirror Test |

---

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Builders feel generic | Medium | Strong eigenvector tuning, distinct voice patterns |
| Task routing is dumb | Medium | Start simple (keyword matching), iterate to smart |
| Too much coordination overhead | Low | Haiku for routine, Sonnet for complex |
| Users don't understand the metaphor | Low | Clear onboarding, helpful Sage explains |

---

*"The workshop isn't a feature. It's the soul of Agent Town made productive."*
