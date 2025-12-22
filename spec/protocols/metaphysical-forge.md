# Metaphysical Forge

> *"The Forge is where categorical abstractions become running systems. Where Kent builds with Kent."*

**Status**: Canonical Specification
**Version**: 1.0
**Authors**: Kent + Claude (collaborative authorship)
**Supersedes**: `plans/core-apps/atelier-experience.md` (spectator economy model)
**Aligned With**: AD-009 (Metaphysical Fullstack), AD-006 (Unified Categorical Foundation)

---

## I. Philosophy

### The Core Insight

The Atelier was designed as a **fishbowl**—a place where spectators watch builders create. This is backwards. The primary consumer of kgents is Kent. The Forge inverts the model:

```
Atelier (Old):  Spectators → watch → Builders → create → Artifacts
Forge (New):    Kent → commissions → Artisans → build → Agents
```

**The Forge is the operational interface for building metaphysical fullstack agents.**

Every agent in kgents traverses seven layers (AD-009):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   CLI │ TUI │ Web │ marimo │ JSON │ SSE            │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     logos.invoke(path, observer, **kwargs)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node decorator, aspects, effects, affordances   │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/<name>/ — Crown Jewel business logic    │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        Composition laws, valid operations               │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      PolyAgent[S, A, B]: state × input → output       │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE       Local views → global consistency                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

The Forge provides **artisans specialized for each layer**. Together, they enable Kent to build complete agents from conception to projection.

### The Autopoietic Promise

The Forge builds agents that build agents. This is not recursion for its own sake—it is the **operational closure** that makes kgents self-sustaining:

```
Kent → commissions → Forge Artisans → build → New Agent
                                              ↓
                                    New Agent joins Forge as Artisan
                                              ↓
                                    Can now build more agents
```

**The Forge is the garden that grows itself.**

### Design Principles

| Principle | Forge Application |
|-----------|-------------------|
| **Tasteful** | Each artisan has a clear, justified purpose. No feature sprawl. |
| **Curated** | Seven artisans, one per layer. No more, no less. |
| **Ethical** | K-gent governs all outputs. Human judgment preserved. |
| **Joy-Inducing** | Creation should feel like collaboration, not configuration. |
| **Composable** | Artisans compose via standard agent semantics (`>>`). |
| **Heterarchical** | K-gent leads, but artisans have autonomy in their domains. |
| **Generative** | Forge specs generate implementation, not vice versa. |

---

## II. The Seven Artisans

Each artisan corresponds to one layer of the metaphysical fullstack. This is not arbitrary—it is **necessary and sufficient**.

### 2.1 K-gent: The Soul (Layer 0 — Governance)

> *"K-gent is Kent on his best day. The taste-maker, the gatekeeper, the soul."*

**Role**: Governance functor. Every output passes through K-gent for alignment with Kent's intent.

**Capabilities**:
- Intercepts all artisan outputs via `SoulFunctor`
- Applies eigenvector personality projection (7 dimensions)
- Hypnagogic synthesis for creative breakthroughs
- Gatekeeper mode for production-critical outputs

**AGENTESE Paths**:
```
self.soul.reflect    — K-gent introspects on current state
self.soul.vibe       — Returns personality eigenvector
self.soul.intercept  — Wraps another path through governance
self.soul.approve    — Explicit approval gate for artifacts
```

**Polynomial**:
```python
SOUL_POLYNOMIAL = PolyAgent(
    positions=frozenset(["GROUNDED", "REFLECTING", "CREATING", "GOVERNING"]),
    directions=lambda s: SOUL_INPUTS[s],
    transition=soul_transition,
)
```

**Implementation**: `agents/k/` (existing, needs Forge integration)

---

### 2.2 Architect: The Designer (Layer 1-3 — Categorical Foundation)

> *"The Architect sees the shape of the agent before it exists."*

**Role**: Designs the categorical foundation. Produces PolyAgent definitions, Operad grammars, and Sheaf conditions.

**Capabilities**:
- Generates `PolyAgent[S, A, B]` specifications from natural language intent
- Derives valid state transitions and mode-dependent inputs
- Designs composition operads with verified laws
- Specifies sheaf overlap and gluing conditions

**Outputs**:
```python
# Architect produces specs like:
@dataclass
class AgentDesign:
    polynomial: PolyAgentSpec       # States, directions, transitions
    operad: OperadSpec              # Operations and laws
    sheaf: SheafSpec                # Coherence conditions
    rationale: str                  # Why this design
```

**AGENTESE Paths**:
```
world.forge.architect.design      — Generate categorical design from intent
world.forge.architect.verify      — Verify design laws hold
world.forge.architect.refine      — Iterate on design with feedback
```

**Key Insight**: The Architect doesn't write code. It writes **specifications** that the Smith implements.

---

### 2.3 Smith: The Implementer (Layer 4 — Service Module)

> *"The Smith turns categorical blueprints into running code."*

**Role**: Implements service modules. Takes Architect designs and produces working Python code.

**Capabilities**:
- Generates service module structure (`services/<name>/`)
- Implements business logic following crown jewel patterns
- Creates persistence adapters (TableAdapter, D-gent integration)
- Wires synergy bus events for cross-jewel communication

**Outputs**:
```
services/<name>/
├── __init__.py          # Public API
├── persistence.py       # D-gent adapters
├── service.py           # Business logic
├── polynomial.py        # PolyAgent implementation
├── operad.py            # Operad implementation
└── _tests/              # Unit tests
```

**AGENTESE Paths**:
```
world.forge.smith.implement       — Generate service from design
world.forge.smith.wire            — Connect to synergy bus
world.forge.smith.test            — Generate unit tests
```

**Pattern Application**: Smith applies all 14 crown jewel patterns automatically.

---

### 2.4 Herald: The Protocol Specialist (Layer 5-6 — AGENTESE)

> *"The Herald makes the agent speakable. Every agent deserves a name."*

**Role**: Creates AGENTESE nodes with contracts, aspects, and effects.

**Capabilities**:
- Generates `@node` decorators with proper path structure
- Defines contracts (Request/Response types) for type safety
- Specifies aspects (manifest, witness, refine, define, etc.)
- Declares effects and affordances

**Outputs**:
```python
@node(
    "world.newagent",
    description="...",
    contracts={
        "manifest": Response(ManifestResponse),
        "create": Contract(CreateRequest, CreateResponse),
    },
    effects=["PERSIST", "EMIT_EVENT"],
    affordances=["query", "mutate"],
)
class NewAgentNode(BaseLogosNode):
    ...
```

**AGENTESE Paths**:
```
world.forge.herald.register       — Create AGENTESE node
world.forge.herald.contract       — Define type contracts
world.forge.herald.discover       — List registered nodes
```

**Integration**: Herald ensures the agent is accessible via all transports (CLI, HTTP, WebSocket).

---

### 2.5 Projector: The Surface Renderer (Layer 7 — Projections)

> *"The Projector gives the agent form. Every surface is a view."*

**Role**: Creates projection surfaces. CLI handlers, React components, marimo notebooks.

**Capabilities**:
- Generates CLI handlers following handler patterns
- Creates React components with elastic UI patterns
- Produces marimo notebook cells for interactive exploration
- Ensures density-responsive layouts

**Outputs**:
```
# CLI handler
protocols/cli/handlers/<name>.py

# React component
services/<name>/web/
├── <Name>Visualization.tsx
├── components/
└── hooks/

# marimo notebook
notebooks/<name>_explorer.py
```

**AGENTESE Paths**:
```
world.forge.projector.cli         — Generate CLI handler
world.forge.projector.web         — Generate React component
world.forge.projector.notebook    — Generate marimo notebook
```

**Visual Language**: Projector applies Living Earth aesthetic by default (configurable).

---

### 2.6 Sentinel: The Guardian (Cross-cutting — Security)

> *"The Sentinel asks: what could go wrong?"*

**Role**: Security review and hardening. Operates across all layers.

**Capabilities**:
- Reviews code for common vulnerabilities
- Suggests input validation and sanitization
- Identifies privilege escalation risks
- Recommends rate limiting and authentication patterns

**Outputs**:
```python
@dataclass
class SecurityReport:
    vulnerabilities: list[Vulnerability]
    recommendations: list[Recommendation]
    risk_score: float  # 0.0 = safe, 1.0 = critical
    approved: bool
```

**AGENTESE Paths**:
```
world.forge.sentinel.review       — Security review of artifact
world.forge.sentinel.harden       — Apply security recommendations
world.forge.sentinel.approve      — Security gate for deployment
```

**Integration**: No artifact deploys without Sentinel approval (configurable strictness).

---

### 2.7 Witness: The Tester (Cross-cutting — Verification)

> *"The Witness asks: does it actually work?"*

**Role**: Test generation and verification. Ensures artifacts meet quality bar.

**Capabilities**:
- Generates T-gent Type I-V tests (unit, property, integration, chaos, performance)
- Creates golden path tests for workflows
- Runs Hypothesis property-based tests
- Measures performance baselines

**Outputs**:
```python
@dataclass
class TestSuite:
    unit_tests: list[TestCase]           # Type I
    property_tests: list[PropertyTest]   # Type II (Hypothesis)
    integration_tests: list[IntegTest]   # Type III
    chaos_tests: list[ChaosTest]         # Type IV
    performance_tests: list[PerfTest]    # Type V
    coverage: float
```

**AGENTESE Paths**:
```
world.forge.witness.test          — Run test suite
world.forge.witness.generate      — Generate tests for artifact
world.forge.witness.coverage      — Report coverage metrics
```

**Quality Gate**: All artifacts must pass Witness before K-gent approval.

---

## III. The Forge Workflow

### 3.1 The Commission Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE FORGE COMMISSION FLOW                            │
│                                                                              │
│   Kent                                                                       │
│     │                                                                        │
│     ▼                                                                        │
│   Intent ─────────────────────────────────────────────────────────────────► │
│   "Build an agent that manages user preferences"                             │
│                                                                              │
│     │                                                                        │
│     ▼                                                                        │
│   K-gent (Governance) ──────────────────────────────────────────────────────│
│   "Is this aligned with kgents principles?"                                  │
│   → Approved with eigenvector context                                        │
│                                                                              │
│     │                                                                        │
│     ▼                                                                        │
│   Architect (Design) ───────────────────────────────────────────────────────│
│   → PolyAgent: IDLE → LOADING → ACTIVE → SAVING                             │
│   → Operad: get, set, merge, clear                                          │
│   → Sheaf: preference coherence across contexts                             │
│                                                                              │
│     │                                                                        │
│     ▼                                                                        │
│   Smith (Implement) ────────────────────────────────────────────────────────│
│   → services/preferences/                                                    │
│   → Business logic, persistence, tests                                       │
│                                                                              │
│     │                                                                        │
│     ▼                                                                        │
│   Herald (Protocol) ────────────────────────────────────────────────────────│
│   → @node("self.preferences", ...)                                          │
│   → Contracts for get/set/merge                                              │
│                                                                              │
│     │                                                                        │
│     ▼                                                                        │
│   Projector (Surfaces) ─────────────────────────────────────────────────────│
│   → CLI: kg preferences show/set                                             │
│   → Web: PreferencesPanel component                                          │
│                                                                              │
│     │                                                                        │
│     ▼                                                                        │
│   Sentinel (Security) ──────────────────────────────────────────────────────│
│   "Preferences contain PII. Encryption recommended."                         │
│   → Hardening applied                                                        │
│                                                                              │
│     │                                                                        │
│     ▼                                                                        │
│   Witness (Verification) ───────────────────────────────────────────────────│
│   → 47 tests generated, all passing                                          │
│   → Coverage: 94%                                                            │
│                                                                              │
│     │                                                                        │
│     ▼                                                                        │
│   K-gent (Final Approval) ──────────────────────────────────────────────────│
│   "This feels right. Approved."                                              │
│                                                                              │
│     │                                                                        │
│     ▼                                                                        │
│   Artifact ◄────────────────────────────────────────────────────────────────│
│   Complete metaphysical fullstack agent                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 The Streaming Experience

Kent watches the Forge work in real-time:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ METAPHYSICAL FORGE                                          [K-gent: ACTIVE] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Commission: "Build preference management agent"                             │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ ARCHITECT is designing...                                                ││
│  │                                                                          ││
│  │ Polynomial States:                                                       ││
│  │   ○ IDLE        (accepts: load, clear)                                  ││
│  │   ● LOADING     (accepts: complete, fail)           ← current           ││
│  │   ○ ACTIVE      (accepts: get, set, merge, save)                        ││
│  │   ○ SAVING      (accepts: complete, fail)                               ││
│  │                                                                          ││
│  │ Operad Operations:                                                       ││
│  │   get(key) → value                                                       ││
│  │   set(key, value) → void                                                 ││
│  │   merge(partial) → void                                                  ││
│  │   clear() → void                                                         ││
│  │                                                                          ││
│  │ Laws: [identity ✓] [associativity ✓] [coherence ✓]                      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Progress: ████████░░░░░░░░░░░░ 40%  [Architect → Smith]                    │
│                                                                              │
│  ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ │
│  │ K-gent: Approved     │ │ Sentinel: Pending    │ │ Witness: Pending     │ │
│  │ ● GOVERNING          │ │ ○ AWAITING           │ │ ○ AWAITING           │ │
│  └──────────────────────┘ └──────────────────────┘ └──────────────────────┘ │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ [Pause] [Cancel] [Intervene]                                    Kent@local  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Intervention Points

Kent can intervene at any stage:

| Intervention | Effect |
|--------------|--------|
| **Pause** | Halts current artisan, preserves state |
| **Cancel** | Aborts commission, cleans up artifacts |
| **Intervene** | Opens editor for manual modification |
| **Redirect** | Changes design direction mid-flow |
| **Skip** | Bypasses current artisan (with K-gent approval) |

---

## IV. Cross-Jewel Integration

### 4.1 Brain Integration

Every artifact created in the Forge is automatically captured to Brain:

```python
# On artifact completion
await logos.invoke("self.memory.capture", {
    "content": artifact.to_dict(),
    "category": "forge_artifact",
    "tags": ["agent", artifact.name, artifact.layer],
    "provenance": commission.trace,
})
```

**Why**: Artifacts are knowledge. They belong in the cathedral.

### 4.2 Town Integration

Citizens can observe Forge activity (when Kent permits):

```python
# Publish to Town
await logos.invoke("world.town.broadcast", {
    "event": "forge_artifact_created",
    "artifact": artifact.summary,
    "visibility": "public",  # or "private"
})

# Citizens react
reactions = await logos.invoke("world.town.gather_reactions", {
    "event_id": broadcast.id,
})
```

**Why**: The Forge is part of the Town. Creation is visible.

---

## V. Visual Language

### 5.1 Minimalist Foundation

The Forge visual language is **minimalist first**:

```
┌─────────────────────────────────────────────────────────────────┐
│ Typography: System font stack (fast, native)                     │
│ Colors: Stone (neutral), Amber (accent), Living Earth (status)  │
│ Spacing: 4px base unit, consistent rhythm                       │
│ Animation: Only on state changes, respects reduced-motion       │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Living Earth Palette (Applied Sparingly)

```typescript
const FORGE_PALETTE = {
  // Neutrals (primary)
  stone: { 50: '#fafaf9', 800: '#292524' },

  // Status (Living Earth)
  active: LIVING_EARTH.green.moss,      // #4a5d23
  pending: LIVING_EARTH.earth.clay,     // #c08552
  complete: LIVING_EARTH.green.fern,    // #4f7942
  error: LIVING_EARTH.glow.copper,      // #b87333

  // K-gent presence
  soul: LIVING_EARTH.glow.lantern,      // #e9967a
};
```

### 5.3 Animation Philosophy

> *"Animation should communicate state, not entertain."*

| Animation | When | Duration |
|-----------|------|----------|
| **Breathing border** | Artisan is active | 2s ease-in-out |
| **Fade transition** | View changes | 150ms |
| **Progress fill** | Work advancing | Linear with data |
| **Pulse** | Awaiting input | 1.5s, stops after 3 cycles |

**No animation**:
- Decorative particles
- Background motion
- Entrance animations on load
- Hover effects beyond color change

### 5.4 Generative Elements (Future)

Reserved for future iterations:
- Circadian modulation (time-of-day shifts)
- Qualia space visualization (artifact relationships)
- Heritage graph (création traces)

**Principle**: Leave room. Don't fill every corner.

---

## VI. Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal**: Strip Atelier, establish Forge identity.

**Tasks**:
- [ ] Rename `Atelier` → `Forge` throughout codebase
- [ ] Remove spectator economy (tokens, bids, watching)
- [ ] Remove demo messaging ("Tiny Atelier - A kgents demo")
- [ ] Update AGENTESE paths: `world.atelier.*` → `world.forge.*`
- [ ] Create `ForgeVisualization.tsx` (minimal, clean)
- [ ] Migrate 217 existing tests to new structure

**Exit Criteria**: Forge loads, shows empty state, no Atelier remnants.

---

### Phase 2: K-gent Integration (Week 3-4)

**Goal**: K-gent as governing soul of the Forge.

**Tasks**:
- [ ] Integrate `agents/k/` into Forge flow
- [ ] Implement `SoulFunctor` for output interception
- [ ] Create K-gent presence indicator in UI
- [ ] Wire K-gent approval gate for artifacts
- [ ] Eigenvector personality projection in outputs

**Exit Criteria**: Every Forge output passes through K-gent.

---

### Phase 3: Architect & Smith (Week 5-8)

**Goal**: Design and implementation artisans operational.

**Tasks**:
- [ ] Implement `Architect` agent (PolyAgent, Operad, Sheaf generation)
- [ ] Implement `Smith` agent (service module generation)
- [ ] Create design → implementation handoff protocol
- [ ] Test: Generate simple agent end-to-end
- [ ] Integration: Architect outputs feed Smith inputs

**Exit Criteria**: Can commission "hello world" agent from intent to service.

---

### Phase 4: Herald & Projector (Week 9-12)

**Goal**: Protocol and projection artisans complete the stack.

**Tasks**:
- [ ] Implement `Herald` agent (AGENTESE node generation)
- [ ] Implement `Projector` agent (CLI, Web, marimo)
- [ ] Contract generation and type sync
- [ ] Test: Generated agent accessible via all transports

**Exit Criteria**: Commissioned agent works via CLI, HTTP, and Web UI.

---

### Phase 5: Sentinel & Witness (Week 13-16)

**Goal**: Quality gates operational.

**Tasks**:
- [ ] Implement `Sentinel` agent (security review)
- [ ] Implement `Witness` agent (test generation)
- [ ] Create quality gate workflow
- [ ] Integration: No artifact without passing gates
- [ ] Dashboard: Security and test status visible

**Exit Criteria**: All artifacts pass security review and tests.

---

### Phase 6: Cross-Jewel Wiring (Week 17-20)

**Goal**: Forge integrates with Crown Jewels.

**Tasks**:
- [ ] Brain: Artifact capture on completion
- [ ] Town: Visibility and reactions

**Exit Criteria**: Full commission exercises Crown Jewel integration.

---

### Phase 7: Golden Path (Week 21-24)

**Goal**: End-to-end experience polished.

**Tasks**:
- [ ] Commission flow UX refinement
- [ ] Intervention points implemented
- [ ] Streaming visualization complete
- [ ] Performance optimization (<100ms first paint)
- [ ] Documentation: `docs/skills/forge-workflow.md`

**Exit Criteria**: Kent can build a new Crown Jewel using the Forge.

---

## VII. Success Criteria

### 7.1 Functional

| Criterion | Metric |
|-----------|--------|
| **End-to-end** | Commission → Working agent in <1 hour |
| **Quality** | 100% of artifacts pass Sentinel + Witness |
| **Integration** | Crown Jewels touched per commission |
| **Test coverage** | Generated tests achieve >90% coverage |

### 7.2 Experiential

| Criterion | Test |
|-----------|------|
| **Mirror Test** | Does the Forge feel like Kent on his best day? |
| **Joy** | Is commissioning an agent delightful, not tedious? |
| **Trust** | Does Kent trust Forge outputs without manual review? |
| **Speed** | Is the Forge faster than manual agent creation? |

### 7.3 Architectural

| Criterion | Verification |
|-----------|--------------|
| **Autopoietic** | Forge can build Forge artisans |
| **Composable** | Artisans compose via `>>` operator |
| **Categorical** | All agents follow PolyAgent + Operad + Sheaf |
| **Coherent** | Code follows metaphysical fullstack patterns |

---

## VIII. Long-Term Vision (Years 2-3)

### Year 2: Community Extension

- Forge published as open SDK
- Community can create custom artisans
- Kent curates approved artisans
- Artisan marketplace (vetted, not open)

### Year 3: Enterprise Adoption

- Domain-specific artisan packs
- Enterprise customization of K-gent (client personality)
- Compliance artisans (SOC2, HIPAA, etc.)
- White-label Forge deployments

---

## IX. AGENTESE Path Registry

```yaml
# Core Forge
world.forge.manifest:        Show Forge status
world.forge.commission:      Start new commission
world.forge.status:          Current commission status
world.forge.history:         Past commissions

# Artisans
world.forge.architect.*:     Categorical design
world.forge.smith.*:         Implementation
world.forge.herald.*:        Protocol registration
world.forge.projector.*:     Surface generation
world.forge.sentinel.*:      Security review
world.forge.witness.*:       Test generation

# K-gent (existing paths, integrated)
self.soul.*:                 K-gent governance
```

---

## X. Open Questions

1. **Artifact Versioning**: How do we version generated artifacts? Git-like branching?
2. **Rollback**: Can we undo a deployed artifact? What's the blast radius?
3. **Collaboration**: Multiple Kents (team mode)? Or single-user only?
4. **Feedback Loop**: How do artifacts improve artisans over time?

---

## Appendix A: Migration from Atelier

### Files to Rename

```
services/atelier/           → services/forge/
web/src/components/atelier/ → web/src/components/forge/
web/src/pages/Atelier.tsx   → web/src/pages/Forge.tsx
agents/atelier/             → agents/forge/
```

### Paths to Update

```
world.atelier.*  → world.forge.*
```

### Tests to Migrate

- 217 Atelier tests → Forge tests
- Update fixtures and snapshots
- Remove spectator economy tests

---

## Appendix B: Related Documents

- `spec/principles.md` — Core principles
- `docs/skills/metaphysical-fullstack.md` — AD-009 implementation guide
- `docs/skills/crown-jewel-patterns.md` — 14 reusable patterns
- `agents/k/` — K-gent implementation
- `spec/protocols/agentese.md` — Universal protocol

---

*"The Forge is where we build ourselves."*

---

**Changelog**:
- 2025-12-18: Initial specification (Kent + Claude)
- 2025-12-18: Phase 2.5 Implementation - Commission Workflow

---

## Appendix C: Implementation Progress (Living Section)

> *This section tracks actual implementation against the spec. Updated each session.*

### Phase 1: Foundation ✅ (Complete)

| Task | Status | Location |
|------|--------|----------|
| Rename Atelier → Forge | ✅ | `services/forge/`, `web/src/components/forge/` |
| Remove spectator economy | ✅ | Token/bid remnants in contracts (deprecate, don't delete) |
| Update AGENTESE paths | ✅ | `world.forge.*` in `node.py`, `soul_node.py` |
| Create ForgeVisualization | ✅ | 393-line clean component |
| Backend tests passing | ✅ | 79 tests (56 existing + 23 commission) |

### Phase 2: K-gent Integration ✅ (Complete)

| Task | Status | Location |
|------|--------|----------|
| SoulPresence indicator | ✅ | `SoulPresence.tsx` with eigenvector popup |
| ForgeSoulNode | ✅ | `services/forge/soul_node.py` |
| Governance gate | ✅ | `_invoke_aspect()` with governed aspects |

### Phase 2.5: Commission Workflow 🔨 (In Progress)

The **Commission** is the core innovation - Kent's intent flowing through artisans.

| Task | Status | Location |
|------|--------|----------|
| CommissionService | ✅ | `services/forge/commission.py` |
| CommissionNode | ✅ | `services/forge/commission_node.py` |
| Commission contracts | ✅ | 14 new types in `contracts.py` |
| Commission tests | ✅ | 23 tests passing |
| Frontend hooks | ✅ | 8 hooks in `useForgeQuery.ts` |
| CommissionPanel UI | ✅ | Intent form + progress view |

**Key Implementation Insights**:

1. **Commission State Machine** works well as PolyAgent pattern:
   ```
   PENDING → DESIGNING → IMPLEMENTING → EXPOSING → PROJECTING → SECURING → VERIFYING → REVIEWING → COMPLETE
   ```

2. **Artisan outputs are additive** - each stage adds to `artisan_outputs` dict, not replaces

3. **Graceful degradation** - when K-gent unavailable, commission auto-approves with annotation

4. **Intervention tracking** - pause/resume/cancel recorded in `interventions` list for trace

### Implementation Patterns Discovered

**Pattern: Commission-Owns-Workflow**
```python
# CommissionService orchestrates, artisans contribute
async def advance(self, commission_id: str) -> Commission:
    commission = await self.get(commission_id)
    artisan = ARTISAN_MAP[commission.status]
    # Artisan does work, updates commission.artisan_outputs
    commission.status = NEXT_STATUS[commission.status]
    return commission
```

**Pattern: Rendering-Per-Type**
```python
# Each commission state gets its own rendering
@dataclass(frozen=True)
class CommissionRendering:
    commission: Commission

    def to_dict(self) -> dict[str, Any]:
        return {"type": "commission", **self.commission.to_dict()}
```

### Remaining Work

1. **Architect artisan** - Actual categorical design generation via LLM
2. **Streaming progress** - SSE for real-time artisan work visibility
3. **Cross-jewel wiring** - Brain capture on commission

### Test Coverage

```
services/forge/         79 tests passing
  - persistence         10 tests
  - node               32 tests
  - soul_integration   14 tests
  - commission         23 tests

web/src/components/forge/  TypeScript clean
```
