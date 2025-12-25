# Witness Protocol

> *"The proof IS the decision. The mark IS the witness."*

**Consolidated from**: witness-primitives.md, witness-supersession.md, witness-crystallization.md, witness-assurance-surface.md
**Date**: 2025-12-24
**Implementation**: `impl/claude/services/witness/` (64+ tests)
**Heritage**: Toulmin argumentation, Hegel's dialectic, CSA stigmergy, Zep temporal graphs

---

## Part I: Purpose & Core Insight

### Purpose

The Witness protocol forms the audit, traceability, and memory foundation of kgents. It answers:

1. **What happened?** — Every action is recorded
2. **Why did it happen?** — Causal links trace back to intent
3. **Who allowed it?** — Permission contracts are explicit
4. **What could it cost?** — Resource budgets are priced
5. **What can we remember?** — Crystallization compresses marks into wisdom

### The Core Insight

**An agent IS an entity that justifies its behavior.**

```
Without trace: stimulus → response (reflex)
With trace:    stimulus → reasoning → response (agency)
```

Every action leaves a mark. Every mark joins a walk. Every walk follows a playbook. Marks accumulate into crystals. Crystals accumulate into wisdom.

**Three levels of granularity:**

| Level | Primitive | What It Captures |
|-------|-----------|------------------|
| **Atomic** | Mark | Single stimulus → response |
| **Session** | Walk | Durable work stream |
| **Workflow** | Playbook | Orchestrated multi-phase process |

**Two contracts that enable workflow:**

| Contract | Primitive | What It Governs |
|----------|-----------|-----------------|
| **Permission** | Grant | What operations are permitted |
| **Resource** | Scope | What resources can be consumed |

**Memory compression:**

| Level | Primitive | What It Captures |
|-------|-----------|------------------|
| **Insight** | Crystal | Compressed understanding from marks |
| **Knowledge** | Lesson | Curated knowledge with versioning |

---

## Part II: Primitives

### Mark (formerly TraceNode)

```python
@dataclass(frozen=True)
class Mark:
    """Immutable record of action + reasoning."""
    id: MarkId
    timestamp: datetime

    # What
    stimulus: Stimulus          # What triggered it
    response: Response          # What resulted

    # Who
    origin: str                 # Jewel/agent name
    umwelt: UmweltSnapshot      # Observer context

    # Why (defeasible)
    reasoning: str | None
    principles: tuple[str, ...]

    # Chain
    links: tuple[MarkLink, ...]
    walk_id: WalkId | None
```

**Laws:**
- **Immutability**: Mark is frozen after creation (`frozen=True`)
- **Causality**: `target.timestamp > source.timestamp` for all links
- **Completeness**: Every AGENTESE invocation emits exactly one Mark

### Walk

```python
@dataclass
class Walk:
    """Durable work stream."""
    id: WalkId
    goal: str
    root_plan: PlanPath          # Forest plan file
    marks: list[Mark]            # Accumulates over time
    phase: Phase                 # N-Phase workflow position
    participants: list[Participant]
    status: WalkStatus
```

**Laws:**
- **Monotonicity**: Mark list only grows, never shrinks
- **Phase Coherence**: Phase transitions follow N-Phase grammar
- **Plan Binding**: `root_plan` must exist in Forest

### Playbook (formerly Ritual)

```python
@dataclass
class Playbook:
    """Curator-orchestrated workflow."""
    id: PlaybookId
    name: str
    grant: Grant                 # Permission contract (required)
    scope: Scope                 # Resource contract (required)
    phases: list[Phase]          # State machine
    guards: list[Guard]          # Checks at phase boundaries
```

**Laws:**
- **Grant Required**: Every Playbook has exactly one Grant
- **Scope Required**: Every Playbook has exactly one Scope
- **Guard Transparency**: Guards emit Marks on evaluation
- **Phase Ordering**: Phase transitions follow directed cycle

### Grant (formerly Covenant)

```python
@dataclass
class Grant:
    """Negotiated permission contract."""
    id: GrantId
    name: str
    permissions: list[str]       # e.g., ["write_code", "run_tests"]
    review_gates: list[ReviewGate]
    expiry: datetime | None
    status: GrantStatus          # proposed, granted, revoked, expired
```

**Laws:**
- **Required**: Sensitive operations require a granted Grant
- **Revocable**: Grants can be revoked at any time
- **Gated**: Review gates trigger on threshold

### Scope (formerly Offering)

```python
@dataclass
class Scope:
    """Resource budget context."""
    id: ScopeId
    handles: list[str]           # AGENTESE paths accessible
    budget: Budget               # tokens, time, operations, capital, entropy
    expiry: datetime | None
```

**Laws:**
- **Budget Enforcement**: Exceeding budget triggers review
- **Immutability**: Scopes are frozen after creation
- **Expiry Honored**: Expired Scopes deny access

### Crystal

```python
@dataclass(frozen=True)
class Crystal:
    """
    Compressed witness memory.

    A Crystal exists at a level in the compression hierarchy:
    - Level 0: Direct crystallization from marks (session boundary)
    - Level 1: Compression of level-0 crystals (day boundary)
    - Level 2: Compression of level-1 crystals (week boundary)
    - Level 3: Compression of level-2 crystals (epoch/milestone)
    """

    # Identity
    id: CrystalId
    level: int                              # 0, 1, 2, 3

    # Content
    insight: str                            # The compressed meaning
    significance: str                       # Why this matters
    principles: tuple[str, ...]             # Principles that emerged

    # Provenance (never broken)
    source_marks: tuple[MarkId, ...]        # Direct mark sources (level 0)
    source_crystals: tuple[CrystalId, ...]  # Crystal sources (level 1+)

    # Temporal bounds
    time_range: tuple[datetime, datetime]   # What period this covers
    crystallized_at: datetime               # When compression happened

    # Semantic handles
    topics: frozenset[str]                  # For retrieval
    mood: MoodVector                        # Affective signature

    # Metrics
    compression_ratio: float                # sources / 1
    confidence: float                       # Crystallizer's confidence
    token_estimate: int                     # For budget calculations
```

**Laws:**
- **Mark Immutability**: Marks are never deleted, even after crystallization
- **Provenance Chain**: Every crystal references its sources (marks or crystals)
- **Level Consistency**: Level N crystals only source from level N-1 (or marks for N=0)
- **Temporal Containment**: Crystal time_range contains all source time_ranges
- **Compression Monotonicity**: Higher levels are always denser (fewer, broader)

### Lesson (formerly Terrace)

```python
@dataclass(frozen=True)
class Lesson:
    """Curated knowledge with versioning."""
    id: LessonId
    topic: str
    content: str
    version: int
    history: tuple[LessonId, ...]  # Previous versions
    supersedes: LessonId | None
```

**Laws:**
- **Immutability**: Lessons are frozen after creation
- **Supersession**: New versions explicitly supersede old
- **History Preserved**: All versions kept for reference
- **Topic Uniqueness**: One current version per topic

### Proof (Toulmin Structure)

```python
@dataclass(frozen=True)
class Proof:
    data: str           # Evidence ("3 hours, 45K tokens")
    warrant: str        # Reasoning ("Infrastructure enables velocity")
    claim: str          # Conclusion ("This was worthwhile")
    backing: str        # Support ("CLAUDE.md: DI > mocking")
    qualifier: str      # Confidence ("Almost certainly")
    rebuttals: tuple[str, ...]  # Defeaters
```

### Evidence Hierarchy

```python
class EvidenceTier(Enum):
    CATEGORICAL = 1     # Mathematical (laws hold)
    EMPIRICAL = 2       # Scientific (ASHC runs)
    AESTHETIC = 3       # Hardy criteria (inevitability, unexpectedness, economy)
    GENEALOGICAL = 4    # Pattern archaeology (git history)
    SOMATIC = 5         # The Mirror Test (felt sense)
```

---

## Part III: Dialectical Governance

### Symmetric Agency

Kent and AI are modeled identically. Both are agents that justify behavior.

```
┌─────────────────────────────────────┐
│           FUSED SYSTEM              │
│   ┌─────────┐     ┌─────────┐      │
│   │  Kent   │◄───►│   AI    │      │
│   │ (Agent) │     │ (Agent) │      │
│   └────┬────┘     └────┬────┘      │
│        └───────┬───────┘           │
│                ▼                   │
│        ┌─────────────┐             │
│        │   Fusion    │             │
│        └─────────────┘             │
└─────────────────────────────────────┘
```

### Supersession Conditions

```python
def may_supersede(decision: Decision, by: Decision) -> bool:
    """
    Supersession requires ALL four conditions:
    1. PROOFS VALID - Sound inference
    2. ARGUMENTS SOUND - True premises
    3. EVIDENCE SUFFICIENT - Empirical support
    4. NO SOMATIC DISGUST - Ethical floor
    """
    return (
        by.proofs_valid() and
        by.arguments_sound() and
        by.evidence_sufficient() and
        not kent.feels_disgust(by)  # Absolute veto
    )
```

### Trust Gradient

```
L0: READ_ONLY      Never supersede (Kent reviews everything)
L1: BOUNDED        Supersede trivial (formatting, ordering)
L2: SUGGESTION     Supersede routine (code patterns)
L3: AUTONOMOUS     Supersede significant (architecture)
```

Trust earned through demonstrated alignment. Lost through misalignment. Disgust resets significantly.

### The Dialectical Engine

```
THESIS (Kent)
     │
     ▼
┌─────────────────────┐
│  DIALECTICAL ARENA  │
│                     │
│  Kent challenges AI │
│  AI challenges Kent │
│  Friction → Heat    │
│  Heat → Truth       │
└─────────────────────┘
     │
     ▼
ANTITHESIS (AI)
     │
     ▼
SYNTHESIS (Fusion)
```

**Fusion Quality:**

```
NO FUSION                              FULL FUSION
    │                                        │
    ▼                                        ▼
┌────────┬────────┬────────┬────────┬────────┐
│ Kent   │ Kent + │ Genuine│ AI +   │ AI     │
│ alone  │ AI adj │ synth  │ Kent   │ alone  │
└────────┴────────┴────────┴────────┴────────┘
    │         │         │         │         │
  Low      Medium     HIGH     Medium      Low
 value     value     VALUE     value     value
```

### Dialectical Laws

| Law | Statement |
|-----|-----------|
| **Symmetry** | Kent and AI proposals are structurally equivalent |
| **Challenge** | Every proposal may be challenged |
| **Fusion** | Synthesis differs from both thesis and antithesis |
| **Veto** | Somatic disgust cannot be overridden |

---

## Part IV: Memory Architecture

### The Crystallization Hierarchy

Marks are observations. Crystals are insights. The compression IS the understanding.

| Level | Name | Boundary | Typical Sources | Compression Ratio |
|-------|------|----------|-----------------|-------------------|
| 0 | Session | Session end / manual | 5-50 marks | 10:1 - 50:1 |
| 1 | Day | Midnight / manual | 2-10 level-0 crystals | 5:1 - 20:1 |
| 2 | Week | Sunday / manual | 5-7 level-1 crystals | 5:1 - 10:1 |
| 3 | Epoch | Milestone tag | Variable level-2 crystals | Variable |

### Crystallization Operations

```python
class Crystallizer:
    """Transforms marks/crystals into higher-level crystals."""

    async def crystallize_marks(
        self,
        marks: list[Mark],
        session_id: str | None = None,
    ) -> Crystal:
        """Level 0: Marks → Session Crystal."""

    async def crystallize_crystals(
        self,
        crystals: list[Crystal],
        level: int,
        label: str | None = None,
    ) -> Crystal:
        """Level N: Crystals → Higher Crystal."""

    async def auto_crystallize(
        self,
        since: datetime | None = None,
        level: int = 0,
    ) -> list[Crystal]:
        """Automatic crystallization based on boundaries."""
```

### Context Budget System

Agents need context but have limited budgets. Crystals solve this.

```python
async def get_context(
    budget_tokens: int = 2000,
    recency_weight: float = 0.7,
    relevance_query: str | None = None,
) -> list[Crystal]:
    """
    Get the best crystals that fit within token budget.

    Strategy:
    1. Start with highest-level crystals (most compressed)
    2. Score by recency × relevance
    3. Fill budget greedily by score
    4. Return ordered list
    """
```

### Stigmergic Memory

Patterns reinforce or decay based on usage:

```python
# Patterns reinforce or decay
trace.strength > 0.5  → proceed with confidence
trace.strength < -0.5 → avoid (anti-pattern)

# Decay over time
strength *= (1 - decay_rate) ** days_since_last_use
```

### Crystallization Triggers

| Trigger | Level | When | Automation |
|---------|-------|------|------------|
| `kg witness crystallize` | 0 | Manual | N/A |
| Session end | 0 | `/handoff`, timeout | Automatic |
| `kg witness crystallize --level day` | 1 | Manual | N/A |
| Midnight | 1 | Cron/daemon | Optional |
| `kg witness crystallize --level week` | 2 | Manual | N/A |
| Sunday midnight | 2 | Cron/daemon | Optional |
| Milestone marker | 3 | Mark tagged `#milestone` | Semi-auto |

---

## Part V: Projection Surface

### The Garden Metaphor

Trust is not a badge—it's a living organism. The UI doesn't display trust; it grows trust.

Every spec is a plant:
- **Evidence is soil depth** (more evidence → taller plant)
- **Confidence is health** (high → blooming, decayed → wilting)
- **Orphans are weeds** (visible at edges, inviting tending)

### The Trust Surface Functor

```
TrustSurface : WitnessGarden × AccountabilityLens × Density → Scene

where:
  WitnessGarden = PolyAgent[SpecHealth, Evidence, PlantVisual]
  AccountabilityLens = Audit | Author | Trust
  Density = compact | comfortable | spacious
  Scene = renderable structure (per AD-008)
```

### Accountability Lens

| Lens | What It Shows | Who It's For | Key Binding |
|------|---------------|--------------|-------------|
| **Audit** | Full evidence chain, all levels, rebuttals prominent | External reviewers | `A` |
| **Author** | My marks, my contributions, attention items | Contributors | `U` |
| **Trust** | Confidence only, green/yellow/red at a glance | Executives | `T` |

### Garden Types

```python
@dataclass(frozen=True)
class SpecPlant:
    """A spec rendered as a plant in the garden."""
    path: str
    status: SpecStatus
    confidence: float   # 0.0-1.0
    evidence_levels: EvidenceLevels
    height: int         # Taller = more evidence
    health: PlantHealth # blooming | healthy | wilting | dead

class PlantHealth(Enum):
    BLOOMING = "blooming"  # witnessed, high confidence
    HEALTHY = "healthy"    # in_progress, stable
    WILTING = "wilting"    # contested or decaying
    DEAD = "dead"          # superseded

@dataclass(frozen=True)
class OrphanWeed:
    """An artifact without prompt lineage."""
    path: str
    created_at: datetime
    suggested_prompt: str | None
```

### Evidence Ladder

Seven rungs from L-∞ (orphan) to L3 (economic bet):

```python
@dataclass(frozen=True)
class EvidenceLadder:
    """The complete evidence stack from L-∞ to L3."""
    orphan: int    # L-∞: Artifacts without lineage
    prompt: int    # L-2: PromptAncestor count
    trace: int     # L-1: TraceWitness count
    mark: int      # L0: Human marks
    test: int      # L1: Test artifacts
    proof: int     # L2: Formal proofs
    bet: int       # L3: Economic bets
```

### Confidence Pulse

```python
@dataclass(frozen=True)
class ConfidencePulse:
    """Heartbeat of trust for a spec."""
    confidence: float
    previous_confidence: float | None
    pulse_rate: PulseRate
    delta_direction: Literal["increasing", "decreasing", "stable"]

class PulseRate(Enum):
    FLATLINE = 0      # confidence < 0.3: no animation
    AWAKENING = 0.5   # confidence 0.3-0.6: slow pulse
    ALIVE = 1.0       # confidence 0.6-0.9: steady pulse
    THRIVING = 1.5    # confidence > 0.9: strong pulse
```

### Component Morphisms

Each component is a morphism from data to visual:

| Component | Signature | Purpose |
|-----------|-----------|---------|
| **EvidencePulse** | `Confidence → HeartbeatVisual` | Breathing animation (diagnostic, not decorative) |
| **EvidenceLadder** | `Evidence[] → StackVisual` | Seven rungs (Living Earth palette) |
| **ProvenanceTree** | `PromptAncestor[] → TreeVisual` | Genealogy (time flows left → right) |
| **SpecGarden** | `SpecPlant[] → GardenScene` | Plants grow from ground layers |
| **WitnessAssurance** | `(Garden, Lens, Density) → Page` | Complete dashboard |

### Surface Laws

| Law | Statement |
|-----|-----------|
| **Observer Law** | Same garden + different lens = different scene |
| **Monotonicity Law** | Plant height only increases (evidence accumulates) |
| **Health Dynamics Law** | `health = f(evidence_freshness, contradiction_count, prompt_fitness)` |
| **Orphan Visibility Law** | Orphans are ALWAYS visible (no "hide orphans" option) |
| **Heartbeat Fidelity Law** | Pulse rate reflects actual confidence (flatline at 0.28 is honest) |

---

## Part VI: Integration

### AGENTESE Paths

```
time.witness.*
  .mark         Create mark with action + reasoning
  .recent       Get recent marks
  .timeline     Session history
  .crystallize  Synthesize experience
  .crystal      Crystal operations (query, context, tree, expand)
  .stream       SSE stream of marks/crystals

self.witness.*
  .manifest     Witness status
  .thoughts     Thought stream
  .trust        Trust level query
  .capture      Store a thought
  .invoke       Cross-jewel invocation (L3)
  .pipeline     Multi-step workflow (L3)
  .garden       Garden visualization
  .ladder       Evidence ladder for spec
  .provenance   Provenance tree
  .pulse        Confidence pulse
  .orphans      Orphan weeds

self.fusion.*       (FUTURE)
  .propose      Either agent proposes
  .challenge    Challenge a proposal
  .synthesize   Attempt synthesis
  .veto         Kent's disgust veto

self.trust.*        (FUTURE)
  .level        Current trust level
  .history      Accumulation/loss record
```

### DataBus Integration

```python
# Marks flow through DataBus
mark = await witness.mark(action="...", reasoning="...")
# → DataBus emits WitnessMarkCreated
# → SynergyBus broadcasts to subscribed jewels
# → UI updates via SSE
```

### Module Paths

| Service | Path |
|---------|------|
| Core | `services/witness/mark.py`, `walk.py`, `playbook.py` |
| Contracts | `services/witness/grant.py`, `scope.py` |
| Memory | `services/witness/crystal.py`, `lesson.py` |
| Stores | `services/witness/trace_store.py`, `walk_store.py` |
| Nodes | `services/witness/node.py`, `crystallization_node.py` |
| Persistence | `services/witness/persistence.py` |
| Fusion | `services/fusion/types.py`, `engine.py`, `veto.py`, `service.py`, `node.py` |
| CLI | `services/fusion/cli.py` (`kg decide`) |

### Frontend Components

| Component | Path |
|-----------|------|
| Garden | `web/src/components/witness/SpecGarden.tsx` |
| Ladder | `web/src/components/witness/EvidenceLadder.tsx` |
| Pulse | `web/src/components/witness/EvidencePulse.tsx` |
| Provenance | `web/src/components/witness/ProvenanceTree.tsx` |
| Assurance | `web/src/components/witness/WitnessAssurance.tsx` |

---

## Part VII: Laws & Invariants

### Universal Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| **Immutability** | All witness primitives are `frozen=True` | Python dataclass enforcement |
| **Causality** | `target.timestamp > source.timestamp` for all links | Store validation |
| **Completeness** | Every AGENTESE invocation emits one Mark | Audit trail |
| **Provenance** | Every artifact traces to origin | Graph traversal |
| **Monotonicity** | Evidence only accumulates, never removed | Append-only stores |

### Workflow Laws

| Law | Statement |
|-----|-----------|
| **Grant Required** | Playbooks require exactly one Grant |
| **Scope Required** | Playbooks require exactly one Scope |
| **Guard Transparency** | All guards emit Marks on evaluation |
| **Phase Coherence** | Phase transitions follow N-Phase grammar |

### Memory Laws

| Law | Statement |
|-----|-----------|
| **Crystal Provenance** | Every crystal references sources |
| **Level Consistency** | Level N crystals source from level N-1 |
| **Temporal Containment** | Crystal time_range contains source ranges |
| **Compression Monotonicity** | Higher levels are denser |

### Governance Laws

| Law | Statement |
|-----|-----------|
| **Symmetry** | Kent and AI proposals structurally equivalent |
| **Challenge** | Every proposal may be challenged |
| **Fusion** | Synthesis differs from both inputs |
| **Veto** | Somatic disgust cannot be overridden |

### Surface Laws

| Law | Statement |
|-----|-----------|
| **Observer Law** | Same data + different lens = different scene |
| **Health Dynamics** | Health decays without fresh evidence |
| **Orphan Visibility** | Orphans always visible |
| **Heartbeat Fidelity** | Pulse reflects actual confidence |

---

## Anti-Patterns

**What these primitives are NOT:**

- **Mark** is not a log entry — it has causal links and umwelt context
- **Walk** is not just a session — it binds to plans and tracks N-Phase
- **Playbook** is not a pipeline — it has guards and requires contracts
- **Grant** is not an API key — it's negotiated and revocable
- **Scope** is not a context dump — it has explicit budget constraints
- **Crystal** is not a summary — it's semantic compression with provenance
- **Lesson** is not documentation — it's versioned knowledge that evolves
- **Garden** is not a dashboard — it's a living trust organism

**Governance anti-patterns:**

- **Silent actions**: Actions without marks are reflexes, not agent-actions
- **Sycophancy**: AI that only confirms Kent's views (violates Adversarial Cooperation)
- **Ego attachment**: Clinging to original proposal instead of seeking fusion
- **Override disguised as supersession**: Supersession requires valid proofs, not authority
- **Arguing away disgust**: Somatic veto cannot be evidence'd away

**Memory anti-patterns:**

- **Eager deletion**: Removing marks after crystallization (violates immutability)
- **Level skipping**: Compressing marks directly to level 2 (violates level consistency)
- **Template crutch**: Using templates when LLM would produce better results
- **LLM crutch**: Using LLM when simple aggregation suffices
- **Unbounded accumulation**: Never crystallizing (the museum anti-pattern)
- **Over-crystallization**: Crystallizing every few marks (noise, not signal)

**Surface anti-patterns:**

- **Spreadsheet aesthetics**: Garden, not ledger
- **Hiding orphans**: Weeds to tend, not shame to conceal
- **Static badges**: Trust has a heartbeat
- **Confetti celebrations**: Joy is warmth, not particles (tasteful, not gaudy)
- **Mode-specific components**: Use density dimension, not `isMobile` conditionals

---

## Example Usage

### Basic Witness

```python
# Leave a mark
mark = await witness.mark(
    action="Refactored DI container",
    reasoning="Enable Crown Jewel pattern",
    principles=["composable", "generative"],
)

# Query recent marks
recent = await witness.recent(limit=10)

# Crystallize session
crystal = await crystallizer.crystallize_marks(marks, session_id="session-abc")

# Get context within budget
context = await witness.get_context(budget_tokens=2000, relevance_query="DI")
```

### Dialectical Fusion

```python
# Kent proposes
thesis = Proposal(
    agent="kent",
    position="Use LangChain",
    reasoning="Scale, resources, production",
)

# AI challenges
antithesis = Proposal(
    agent="claude",
    position="Build kgents",
    reasoning="Novel contribution, joy-inducing",
)

# Synthesize
synthesis = await fusion.synthesize(
    thesis=thesis,
    antithesis=antithesis,
)
# Result: "Build minimal kernel, validate, then decide"
```

### Playbook with Contracts

```python
# Create contracts
grant = Grant.propose(
    name="Implement Feature",
    permissions=["write_code", "run_tests"],
)
scope = Scope.create(
    handles=["world.codebase.*"],
    budget=Budget(tokens=10000, operations=50),
)

# Create playbook
playbook = Playbook.create(
    name="Implement Feature",
    grant=grant,
    scope=scope,
)

# Start walk
walk = Walk.create(
    goal="Implement Mark primitive",
    root_plan=PlanPath("plans/witness-phase1.md"),
)

# Emit marks
mark = Mark.from_agentese(
    path="world.file",
    aspect="write",
    response_content="Wrote mark.py",
)
walk.advance(mark)
```

---

## Constitutional Integration

| Principle (Ontology) | Article (Governance) | Witness Embodiment |
|---------------------|----------------------|--------------------|
| 1. Tasteful | I. Symmetric Agency | Same Mark structure for Kent and AI |
| 2. Curated | II. Adversarial Cooperation | Challenge mechanism in fusion |
| 3. Ethical | III. Supersession Rights | Four conditions for supersession |
| 4. Joy-Inducing | IV. The Disgust Veto | Absolute somatic veto |
| 5. Composable | V. Trust Accumulation | Trust gradient (L0-L3) |
| 6. Heterarchical | VI. Fusion as Goal | Dialectical engine |
| 7. Generative | VII. Amendment | Garden evolves, dead plants compost |

---

## Implementation Phases

| Phase | Delivers | Status |
|-------|----------|--------|
| 0 | Mark, MarkStore, `time.witness.mark` | ✅ Complete |
| 1 | Walk, WalkStore, Proof (Toulmin), EvidenceTier | ✅ Complete |
| 2 | Crystallization (levels 0-3), context budget | In Progress |
| 3 | ASHC integration, causal learning | Planned |
| 4 | Dialectical engine, `self.fusion.*`, `kg decide` | ✅ Complete (Phase 0) |
| 5 | Garden UI, evidence ladder, provenance tree | In Progress |
| 6 | Back-solved coherence, value drift detection | Planned |

---

*"The proof IS the decision. The mark IS the witness. The garden IS the trust."*

*"The persona is a garden, not a museum."*

---

**Filed:** 2025-12-24
**Compression:** ~800 lines from 1,441 lines (45% reduction)
**Skills:** `docs/skills/witness-patterns.md`, `docs/skills/crown-jewel-patterns.md`
