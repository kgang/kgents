---
path: plans/core-apps-synthesis
status: active
progress: 35
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/core-apps/atelier-experience
  - plans/core-apps/coalition-forge
  - plans/core-apps/holographic-brain
  - plans/core-apps/punchdrunk-park
  - plans/core-apps/domain-simulation
  - plans/core-apps/gestalt-architecture-visualizer
  - plans/core-apps/the-gardener
session_notes: |
  2025-12-15: Complete concept inventory and cross-jewel pattern analysis.
  Identified 7 strongest overlapping patterns across all jewels.
  AGENTESE v3 emerges as THE unifying layer - every jewel speaks it natively.
  Ready for parallel execution across all 7 jewels.
  2025-12-15: EXECUTED shared infrastructure work:
  - Extended STANDARD_SHORTCUTS with all 7 Crown Jewel shortcuts (48 new shortcuts)
  - Created CrownJewelRegistry (58 AGENTESE paths registered across all jewels)
  - contexts/crown_jewels.py now exports per-jewel path registries
  - CLI shortcuts enable /forge, /brain, /park, /sim, /arch, /garden, etc.
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: touched
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: touched
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.07
  returned: 0.0
---

# The Seven Jewel Crown: kgents Reference Applications

> *"The noun is a lie. There is only the rate of change."*
>
> *"The Crown is our compass. Each jewel tests a meta-framework."*
>
> *"The garden tends itself, but only because we planted it together."*

---

## Executive Summary

This synthesis distills 30+ project ideas into **7 reference applications** that share a unified categorical foundation. The Crown is not 7 apps—it is **1 engine with 7 experience modes**. Progress on these jewels defines our project-level KPIs.

| Jewel | Frame | Revenue | Ready | Meta-Framework Stress |
|-------|-------|---------|-------|----------------------|
| **[Atelier](./core-apps/atelier-experience.md)** | Creative workshop + spectators | Token economy | 90% | **Flux** (streaming) |
| **[Coalition Forge](./core-apps/coalition-forge.md)** | Agent task completion | Per-task credits | 85% | **Operad** (composition) |
| **[Holographic Brain](./core-apps/holographic-brain.md)** | Living knowledge topology | $9/$29/$99 | 95% | **Sheaf** (coherence) |
| **[Punchdrunk Park](./core-apps/punchdrunk-park.md)** | Narrative + consent | Experience tickets | 80% | **Polynomial** (state) |
| **[Domain Simulation](./core-apps/domain-simulation.md)** | Enterprise B2B sims | $50-150k/yr | 75% | **Tenancy** (enterprise) |
| **[Gestalt](./core-apps/gestalt-architecture-visualizer.md)** | Living architecture viz | $29-199/seat | 5% | **Reactive** (projection) |
| **[The Gardener](./core-apps/the-gardener.md)** | Autopoietic dev interface | Internal | 60% | **N-Phase** (autopoiesis) |

**Key Insight**: All 7 jewels share the same patterns. Master one, understand all.

---

## Part I: The Seven Strongest Overlaps

These patterns appear in ALL or MOST jewels. They are the execution primitives.

### Pattern 1: AGENTESE v3 as Universal Surface (ALL 7)

**Every action flows through AGENTESE paths.** This is THE unifying principle.

| Context | Meaning | Example Paths |
|---------|---------|---------------|
| `world.*` | External entities | `world.atelier.session.*`, `world.coalition.*`, `world.town.*`, `world.codebase.*` |
| `self.*` | Internal state | `self.memory.*`, `self.soul.*`, `self.forest.*`, `self.tokens.*`, `self.consent.*` |
| `concept.*` | Abstract definitions | `concept.task.*`, `concept.nphase.*`, `concept.mask.*`, `concept.governance.*` |
| `void.*` | Entropy/serendipity | `void.entropy.sip`, `void.entropy.inject` |
| `time.*` | Temporal traces | `time.trace.witness`, `time.inhabit.witness`, `time.simulation.witness` |

**Observer-Dependent Perception** is the differentiator:

```python
# Same path, different observers, different views
await logos("world.town.manifest", architect_umwelt)  # → Power structures
await logos("world.town.manifest", poet_umwelt)       # → Relationship webs
await logos("world.town.manifest", economist_umwelt)  # → Resource flows
```

**Subscription Patterns** enable real-time across all jewels:

```python
# Pattern used by ALL jewels for streaming
sub = await logos.subscribe(
    "world.{jewel}.{entity}.*",
    delivery=DeliveryMode.AT_LEAST_ONCE,  # or AT_MOST_ONCE for non-critical
    buffer_size=100
)
```

**CLI Shortcuts** provide consistent UX:

```yaml
# Each jewel registers shortcuts in .kgents/shortcuts.yaml
atelier: world.atelier.manifest
forge: world.coalition.manifest
brain: self.memory.manifest
park: world.town.manifest
sim: world.simulation.manifest
arch: world.codebase.manifest
garden: concept.gardener.manifest
```

---

### Pattern 2: PolyAgent + Operad + Sheaf Foundation (ALL 7)

**Every jewel instantiates the same three-layer categorical structure.**

| Jewel | Polynomial | Operad | Sheaf |
|-------|------------|--------|-------|
| Atelier | `BuilderPolynomial` | `WORKSHOP_OPERAD` | `ArtifactCoherence` |
| Coalition | `TaskPolynomial` | `TASK_OPERAD` | `OutputCoherence` |
| Brain | `MemoryPolynomial` | `MEMORY_OPERAD` | `KnowledgeCoherence` |
| Punchdrunk | `CitizenPolynomial` | `TOWN_OPERAD` | `NarrativeCoherence` |
| Domain | `DomainPolynomial` | `DOMAIN_OPERAD` | `DomainCoherence` |
| Gestalt | `CodePolynomial` | `CODE_OPERAD` | `ArchitectureCoherence` |
| Gardener | `GardenerSession` | `GARDENER_OPERAD` | `SessionCoherence` |

**Implementation Pattern** (copy for each jewel):

```python
# Every jewel follows this structure
class JewelPolynomial(PolyAgent[State, Input, Output]):
    positions = frozenset(["POS_A", "POS_B", "POS_C"])

JEWEL_OPERAD = Operad(
    operations={
        "op_1": Operation(arity=1),
        "op_2": Operation(arity=2),
    },
    laws=STANDARD_LAWS  # identity, associativity
)

class JewelSheaf:
    def check_coherence(self, local_sections: list) -> GlobalSection:
        """Local views must compose to valid global view."""
```

---

### Pattern 3: Reactive Projection Protocol (ALL 7)

**Every jewel projects to multiple surfaces via the same functor.**

| Target | Q1 | Q2 | Q3+ | Notes |
|--------|----|----|-----|-------|
| CLI | ✓ All | ✓ All | ✓ All | Primary interface |
| Web | ✓ All | ✓ All | ✓ All | React dashboard |
| TUI | Coalition, Domain | All | All | Ops consoles |
| marimo | Brain, Domain | All | All | Analytics/notebooks |
| VR | — | — | Punchdrunk, Gestalt | Post-multiplayer gate |

**Implementation Pattern**:

```python
# Every widget/view has projection methods
class JewelWidget(Projectable):
    def to_cli(self) -> str: ...
    def to_web(self) -> dict: ...
    def to_marimo(self) -> mo.Element: ...
    def to_json(self) -> dict: ...  # Universal fallback

# Usage: same data, different surfaces
widget.project(target="cli")
widget.project(target="web")
```

---

### Pattern 4: Billing + Tenancy + Telemetry Stack (6 of 7)

**Every commercial jewel uses the same infrastructure stack.**

| Component | Usage | Jewels Using |
|-----------|-------|--------------|
| **Billing** (Stripe + OpenMeter) | Token economy, credits, subscriptions, contracts | All except Gardener |
| **Tenancy** (RLS) | User/team/org isolation | All except Gardener |
| **OTEL Spans** | Observability, debugging, audit | ALL 7 |
| **Action Metrics** | Usage tracking, billing triggers | All except Gardener |

**Implementation Pattern**:

```python
# Every jewel action emits spans
with SpanEmitter("jewel.action.name") as span:
    span.set_attribute("user_id", user_id)
    span.set_attribute("tenant_id", tenant_id)
    result = await perform_action()
    span.set_attribute("credits_used", result.credits)
```

---

### Pattern 5: M-gent Memory Integration (5 of 7)

**Memory is a cross-cutting concern, not just a Brain feature.**

| Jewel | Memory Usage | M-gent Components Used |
|-------|--------------|------------------------|
| **Brain** | Core system | HolographicMemory, MemoryCrystal, CartographerAgent, PheromoneField |
| **Atelier** | Artifact persistence | Gallery (memory-backed), artifact metadata |
| **Punchdrunk** | Character memory | Citizen state persistence across sessions |
| **Domain** | Scenario memory | Drill history, audit trails |
| **Gardener** | Session memory | N-Phase session state, forest sync |

**Cross-Jewel Synergy**: Brain crystals can seed other jewels

```python
# Atelier artifact → Brain crystal
await logos("self.memory.capture", umwelt, source="atelier:artifact:123")

# Brain crystal → Punchdrunk character backstory
await logos("world.town.citizen.backstory", umwelt, crystal_id="mem:456")
```

---

### Pattern 6: K-gent Dialogue + Personalization (4 of 7)

**K-gent provides soul/personality layer across jewels.**

| Jewel | K-gent Usage |
|-------|--------------|
| **Brain** | Personalization (learns user's thought patterns) |
| **Punchdrunk** | Dialogue generation + feedback analysis |
| **Gardener** | Proposal generation + session guidance |
| **Atelier** | (Future) Masked personas for builders |

**Cross-Jewel Pattern**: K-gent learns from ALL interactions

```python
# K-gent accumulates understanding across jewels
await logos("self.soul.learn", umwelt, context="atelier:session:789")
await logos("self.soul.learn", umwelt, context="punchdrunk:inhabit:456")
await logos("self.soul.learn", umwelt, context="brain:capture:123")

# Then provides personalized guidance
response = await logos("self.soul.dialogue", umwelt, query="what should I do next?")
# → Informed by ALL past interactions
```

---

### Pattern 7: Consent + Ethics Mechanics (3 of 7)

**Consent is a first-class citizen, not an afterthought.**

| Mechanic | Punchdrunk | Domain | Gardener |
|----------|------------|--------|----------|
| **Consent Debt** | Core: [0,1] continuous | Audit log entries | Respects agent consent in proposals |
| **Force Mechanic** | 3x cost, 3/session, logged | N/A | N/A (asks, doesn't force) |
| **Alignment Check** | Citizens resist misaligned requests | Role-based constraints | Session alignment with forest |
| **Audit Trail** | ConsentLedger | SpanEmitter + action_metrics | Forest sync |

**The Punchdrunk Principle** influences all jewels:

> *"Collaboration > control. Citizen refusal is a feature, not a bug."*

---

## Part II: The Jewels At-A-Glance

### 2.1 Atelier Experience Platform

> *"Live creation mode where builders work in a fishbowl visible to spectators."*

**Absorbs**: The Atelier, Exquisite Cadaver, Memory Theatre, Dreaming Garden, Builder Workshop Runtime, LiveOps Festivals

**Core Loop**: Builder creates → Spectators watch → Spectators bid tokens → Builder responds → Artifact saved

**Experience Modes**: Open Studio | Exquisite Mode | Memory Mode | Garden Mode | Masked Mode | Festival Mode

**AGENTESE Paths**:
- `world.atelier.session.manifest` / `world.atelier.session.bid`
- `world.atelier.gallery.manifest` / `world.atelier.gallery.acquire`
- `self.tokens.manifest` / `self.tokens.tithe`

**Full Plan**: `plans/core-apps/atelier-experience.md`

---

### 2.2 Coalition Forge

> *"A no-code tool for assembling agent coalitions that accomplish real tasks."*

**Absorbs**: Coalition Forge, Agent Town Marketplace, Research Guilds, Personality Marketplace

**Core Loop**: Describe task → Coalition forms (visible) → Task executes (streamed) → Output delivered

**Task Templates**: Research Report | Code Review | Content Creation | Decision Analysis | Competitive Intel

**AGENTESE Paths**:
- `concept.task.manifest` / `concept.task[type].manifest`
- `world.coalition.form` / `world.coalition[id].manifest`
- `world.coalition[id].dialogue.witness` / `world.coalition[id].inject`

**Full Plan**: `plans/core-apps/coalition-forge.md`

---

### 2.3 Holographic Second Brain

> *"Knowledge as living topology, not filing cabinet."*

**Absorbs**: Holographic Second Brain, Pheromone, WikiVerse, ArXivMind

**Core Loop**: Capture → Crystallize → Surface (ghost) → Decay

**Key Differentiators**: Crystals (compressed wisdom) | Cartography (shape of knowledge) | Ghost sync (proactive recall) | Stigmergy (usage shapes surfacing)

**AGENTESE Paths**:
- `self.memory.capture` / `self.memory.crystal.manifest`
- `self.memory.cartography.manifest` / `self.memory.ghost.surface`
- `self.memory.decay` / `self.memory.recall`

**Full Plan**: `plans/core-apps/holographic-brain.md`

---

### 2.4 Punchdrunk Park

> *"Westworld-like simulation where citizens can say no."*

**Absorbs**: Punchdrunk Park, Agent Academy, Learning Town, Simulation Dojo, Dialogue Masks

**Core Loop**: Select scenario → INHABIT citizen → Live narrative → Consent dynamics → K-gent feedback

**Scenario Types**: Mystery | Collaboration | Conflict | Emergence | Practice

**AGENTESE Paths**:
- `world.town.manifest` / `world.town.scenario[id].inhabit`
- `world.town.inhabit[id].act` / `world.town.inhabit[id].dialogue`
- `self.consent.manifest` / `self.consent.force`
- `concept.mask.manifest` / `concept.mask[name].don`

**Full Plan**: `plans/core-apps/punchdrunk-park.md`

---

### 2.5 Domain Simulation Engine

> *"Agent Town configured for any domain with enterprise requirements."*

**Absorbs**: Sim-Labs, Regulated Data Rooms, MetroMind, EconWeb, MoleculeGarden

**Core Loop**: Select/create drill → Assign roles → Execute simulation → Audit + debrief

**Verticals**: Crisis/Compliance | Urban Planning | Economic Policy | Drug Discovery

**AGENTESE Paths**:
- `world.simulation.manifest` / `world.simulation[id].inject`
- `concept.polynomial[type].manifest` / `concept.drill[type].manifest`
- `time.simulation[id].witness` / `time.simulation[id].export`

**Full Plan**: `plans/core-apps/domain-simulation.md`

---

### 2.6 Gestalt Architecture Visualizer

> *"Architecture diagrams that never rot because they never stop watching."*

**Absorbs**: Gestalt, code topology concepts from Pheromone

**Core Loop**: Index repo → Detect layers → Surface drift → Project to CLI/Web/VR

**Key Differentiators**: Live (reactive) | Policy-aware | Multi-target | Local-first | Explainable

**AGENTESE Paths**:
- `world.codebase.manifest` / `world.codebase.module[name].manifest`
- `world.codebase.drift.witness` / `world.codebase.health.manifest`
- `concept.governance.manifest` / `concept.governance.refine`

**Full Plan**: `plans/core-apps/gestalt-architecture-visualizer.md`

---

### 2.7 The Gardener

> *"The form that generates forms. The garden that tends itself."*

**Absorbs**: AGENTESE-first CLI mandate, N-Phase orchestration, autopoietic development

**Core Loop**: Intent → SENSE → ACT → REFLECT → Forest update

**Key Features**: AGENTESE-first CLI | Session persistence | Proactive proposals | Universal routing (weather, email, etc. via MCP)

**AGENTESE Paths**:
- `concept.gardener.session.create` / `concept.gardener.session.resume`
- `concept.gardener.propose` / `concept.gardener.route`
- `self.forest.evolve` / `self.meta.append`
- `world.external.*` → MCP bridge

**Full Plan**: `plans/core-apps/the-gardener.md`

---

## Part III: Unified Architecture

### 3.1 The Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROJECTION LAYER                                   │
│   CLI       Web/React      marimo       TUI/Textual        VR               │
│    └────────────┴────────────┴──────────────┴──────────────┘                │
│                              │                                              │
│                    Projection Functor (.to_cli | .to_web | .to_marimo)      │
├─────────────────────────────────────────────────────────────────────────────┤
│                           EXPERIENCE LAYER                                   │
│   ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐  │
│   │ Atelier │Coalition│  Brain  │Punchdrunk│ Domain  │ Gestalt │ Gardener│  │
│   └────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬────┘  │
│        └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘       │
│                              │                                              │
│                    Experience Mode Selection                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                          AGENTESE LAYER (v3)                                │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │     LOGOS (Parser → JIT → Resolver → Effects → Subscription)       │   │
│   │     world.* │ self.* │ concept.* │ void.* │ time.* │ ?query.*     │   │
│   └────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                            CORE ENGINE                                       │
│   ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐      │
│   │  Town    │  M-gent  │  K-gent  │ Reactive │ N-Phase  │   Flux   │      │
│   │  (sim)   │ (memory) │  (soul)  │ (widgets)│ (phases) │ (stream) │      │
│   └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘      │
│        └──────────┴──────────┴──────────┴──────────┴──────────┘            │
├─────────────────────────────────────────────────────────────────────────────┤
│                       CATEGORICAL FOUNDATION                                 │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │   PolyAgent[S, A, B]  ←→  Operad (grammar)  ←→  Sheaf (coherence) │   │
│   └────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                       SAAS INFRASTRUCTURE                                    │
│   Billing (Stripe)  │  Tenancy (RLS)  │  Terrarium (Gateway)  │  OTEL      │
│   OpenMeter (Usage) │  Licensing      │  API (FastAPI)        │  Metrics   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Cross-Jewel Synergy Matrix

| From ↓ / To → | Atelier | Coalition | Brain | Punchdrunk | Domain | Gestalt | Gardener |
|---------------|---------|-----------|-------|------------|--------|---------|----------|
| **Atelier** | — | Creative tasks | Artifacts→crystals | Performance→narrative | Creative sims | Code as art | Sessions track |
| **Coalition** | Builder coalitions | — | Output→knowledge | Character coalitions | Enterprise workflows | Review coalitions | Sessions track |
| **Brain** | Inspiration source | Knowledge for tasks | — | Character memory | Domain knowledge | Code knowledge | Session memory |
| **Punchdrunk** | Narrative exhibitions | Roleplay task mode | Story→memory | — | Training drills | Code narrative | Sessions track |
| **Domain** | Enterprise creativity | Enterprise tasks | Domain crystals | Enterprise drills | — | Architecture sims | Sessions track |
| **Gestalt** | Codebase UX | Code review tasks | Code topology | Code as world | Code compliance | — | Topology→proposals |
| **Gardener** | AGENTESE routing | AGENTESE routing | Session→crystal | AGENTESE routing | AGENTESE routing | Impl→refresh | — |

**Target**: >50% of features benefit 3+ jewels

---

## Part IV: Execution Roadmap

### 4.1 Parallel Execution Strategy

**All 7 jewels can progress in parallel** because they share the same foundation. Work on one accelerates all.

```
Q1 2025: Foundation
├── Atelier: Spectator economy MVP
├── Coalition: Task loop + 5 templates
├── Brain: Capture + crystal UI
├── Punchdrunk: Scenario framework + 5 scenarios
├── Domain: Crisis vertical MVP
├── Gestalt: CLI projection prototype
└── Gardener: AGENTESE-first CLI refactor

Q2 2025: Experience Depth
├── ALL: marimo projections
├── ALL: TUI ops consoles
├── Atelier: Experience modes
├── Coalition: Visibility layer
├── Brain: Cartography + ghost
├── Punchdrunk: Learning mechanics
├── Domain: Customization UI
├── Gestalt: Web dashboard
└── Gardener: Session persistence

Q3 2025: Scale + Social
├── Atelier: Festivals
├── Coalition: Marketplace
├── Brain: Team features
├── Punchdrunk: Multiplayer
├── Domain: Additional verticals
├── Gestalt: AGENTESE v3 full
└── Gardener: Universal routing

Q4 2025: Enterprise + Polish
├── ALL: Enterprise SSO
├── ALL: Cross-jewel synergies
├── Punchdrunk: VR prototype
├── Gestalt: VR prototype
└── Domain: Partner API
```

### 4.2 Immediate Actions (Next 30 Days)

**Shared Work** (accelerates all 7):
1. [ ] AGENTESE v3 subscription + pipeline operators stable
2. [ ] Projection functor validated (CLI + Web mandatory)
3. [ ] OTEL span coverage to 95%

**Per-Jewel** (each has first deliverable):
1. [ ] **Atelier**: TokenPool wired to Billing
2. [ ] **Coalition**: ForgeTask interface + 5 templates
3. [ ] **Brain**: Capture interface as AGENTESE verbs
4. [ ] **Punchdrunk**: Scenario template schema
5. [ ] **Domain**: CrisisPolynomial + 1 drill
6. [ ] **Gestalt**: `gestalt init` CLI command
7. [ ] **Gardener**: `kg <path>` direct invocation

---

## Part V: Success Metrics

### 5.1 Crown KPIs

| Metric | Definition | Target |
|--------|------------|--------|
| **Crown Completion** | Average % across all 7 jewels | 80% by Q2 2025 |
| **Crown Elegance** | Lines of jewel-specific code / total lines | <30% |
| **Crown Cross-Pollination** | Features that benefit 3+ jewels | >50% |
| **Crown Joy** | Subjective "would I use this?" score | 4.5/5 |

### 5.2 Native Adoption KPIs

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| AGENTESE verb coverage | 90%+ user actions | Consistent surface for all projections |
| Operad-instrumented flows | 95%+ per jewel | Composition grammar enforced |
| Sheaf coherence tests | Per-mode coverage | Local→global correctness |
| Projection targets | CLI + Web mandatory | No bespoke UIs |
| OTEL span coverage | 95%+ | Observability + debugging |

### 5.3 Per-Jewel KPIs

| Jewel | Primary Metric | Target |
|-------|----------------|--------|
| Atelier | MAU (spectators + builders) | 10K by Q4 |
| Coalition | Tasks completed | 100K by Q4 |
| Brain | Crystals formed | 50K by Q4 |
| Punchdrunk | Scenarios completed | 25K by Q4 |
| Domain | Enterprise contracts | 10 by Q4 |
| Gestalt | Repos analyzed | 1K by Q4 |
| Gardener | % Kent's dev via Gardener | 100% |

---

## Part VI: Open Questions (Research Backlog)

### Technical
- What's the optimal decay rate for crystals? (Brain)
- What coalition formation algorithm? (Coalition)
- How to integrate customer-provided LLMs? (Domain)
- How to measure skill improvement objectively? (Punchdrunk)

### Product
- What scenarios are ethically off-limits? (Punchdrunk) — **CRITICAL**
- How aggressive should ghost surfacing be? (Brain)
- Can users own artifacts as NFTs? (Atelier)
- What's the right multiplayer model? (Punchdrunk)

### Business
- Who are lighthouse customers? (Coalition, Domain) — **CRITICAL**
- What's the pricing validation? (All)
- What's the competitive moat? (All)

---

## Part VII: Radical Expansion Opportunities

### 7.1 Runtime Pivots

| Pivot | Upside | Priority |
|-------|--------|----------|
| **PyPy-First** | 5-10x agent loop speed | HIGH |
| **WASM Compilation** | Browser-native, edge compute | HIGH |
| **Local-LLM Native** | Privacy, zero API cost | HIGH |
| **mypyc Hot Paths** | 2-4x critical path speedup | MEDIUM |

### 7.2 Novel Deployments

| Topology | Crown Fit | Unlock |
|----------|-----------|--------|
| **Edge Functions** | Gestalt, Brain | Sub-50ms global |
| **P2P Mesh** | Punchdrunk, Atelier | Infinite scale |
| **Sovereign Compute** | Domain | BAA/HIPAA |

### 7.3 Hardware Integrations

| Hardware | Crown Fit | Timeline |
|----------|-----------|----------|
| **VR Headsets** | Punchdrunk, Gestalt | Post-Q3 |
| **Voice Assistants** | Brain, Coalition | Q3+ |
| **E-Ink Displays** | Brain (ambient) | Exploratory |

---

## Appendix A: Complete Idea Mapping

| Original Idea | Source | Destination Jewel | Status |
|---------------|--------|-------------------|--------|
| The Atelier | art-creativity | Atelier | Core |
| Exquisite Cadaver | art-creativity | Atelier | Mode |
| Memory Theatre | art-creativity | Atelier | Mode |
| Dreaming Garden | art-creativity | Atelier | Mode |
| Dialogue Masks | art-creativity | Punchdrunk | Mechanic |
| Sim-Labs | money-max | Domain | Vertical |
| Builder Workshop Runtime | money-max | Atelier | Merged |
| Personality Marketplace | money-max | Coalition | Merged |
| Holographic Second Brain | money-max | Brain | Core |
| Research Guilds | money-max | Coalition | Template |
| LiveOps Festivals | money-max | Atelier | Mode |
| Regulated Data Rooms | money-max | Domain | Feature |
| WikiVerse | open-dataset | Brain | Data source |
| MetroMind | open-dataset | Domain | Vertical |
| MoleculeGarden | open-dataset | Domain | Vertical |
| EconWeb | open-dataset | Domain | Vertical |
| ArXivMind | open-dataset | Brain | Data source |
| Agent Town Marketplace | project-proposals | Coalition | Merged |
| Generative UI Studio | project-proposals | Reactive Engine | Capability |
| Punchdrunk Park | project-proposals | Punchdrunk | Core |
| Agent Academy | project-proposals | Punchdrunk | Mode |
| Coalition Forge | project-proposals | Coalition | Core |
| Learning Town | self-education | Punchdrunk | Mode |
| Skill Forge | self-education | Punchdrunk | Mechanic |
| Focus Companion | self-education | Deferred | Unique |
| Simulation Dojo | self-education | Punchdrunk | Mode |
| Prism | dev-tools | Deferred | Code review |
| Pheromone | dev-tools | Brain | Code docs |
| Morphism | dev-tools | Deferred | Categorical tests |
| Hive | dev-tools | Deferred | Debug swarm |
| Gestalt | dev-tools | Gestalt | Core |

**Consolidation**: 30+ ideas → 7 jewels (77% reduction)

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Crown** | The 7 reference applications that prove kgents |
| **Jewel** | One of the 7 Crown applications |
| **AGENTESE** | Verb-first ontology for agent-world interaction |
| **Logos** | The AGENTESE resolver engine |
| **Polynomial** | State machine with mode-dependent behavior |
| **Operad** | Composition grammar with law verification |
| **Sheaf** | Local-to-global coherence (emergence) |
| **Crystal** | Compressed memory pattern with degradation |
| **Consent Debt** | Continuous [0,1] measure of agent willingness |
| **Ghost Surfacing** | Proactive recall of forgotten knowledge |
| **INHABIT** | Mode where user embodies a citizen |
| **Projection Functor** | Maps internal state to UI surfaces |

---

*"The noun is a lie. There is only the rate of change."*

*"The Crown is one engine, seven lenses."*

*Last updated: 2025-12-15*
