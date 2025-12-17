---
path: plans/crown-jewels-enlightened
status: active
progress: 88
last_touched: 2025-12-17
touched_by: claude-opus-4-5
blocking: []
enables:
  - ALL crown jewel work
related_plans:
  - plans/crown-jewels-metaphysical-upgrade.md  # Architecture upgrade
  - plans/cli/wave1-crown-jewels.md             # CLI migration
  - plans/agentese-v3-crown-synergy-audit.md    # v3 synergies
session_notes: |
  2025-12-17 (late): Phase 3 LLM Integration Complete
  - Phase 1 (Brain): 100% COMPLETE - 8 CLI commands, 5 API endpoints, 65 tests
  - Phase 2 (Gardener): 95% COMPLETE - Full CLI lifecycle, Brain integration
  - Phase 3 (Town): 95% COMPLETE - LLM integration, AGENTESE paths, memory surfacing
  - Phase 4 (Atelier): 95% COMPLETE - Festival mode, spectator economy CLI

  Phase 3 completions (this session):
  - LLM-powered citizen responses using ClaudeCLIRuntime
  - Memory-grounded context (foveation pattern: recent + relevant memories)
  - Archetype system prompts with eigenvector personality values
  - AGENTESE paths: self.citizen.<name>.memory.* and self.citizen.<name>.personality.*
  - CitizenNode, CitizenMemoryNode, CitizenPersonalityNode classes
  - LLM-powered gather discussions with per-citizen cosmotechnics
  - 12 new tests for citizen context (test_self_citizen.py)
  - Fallback to rule-based responses when LLM unavailable

  Tests: 28 town tests + 17 persistent memory + 12 citizen context = 57 tests passing

  2025-12-17 (planning): ARCHITECTURE UPGRADE PLANNED
  - Created plans/crown-jewels-metaphysical-upgrade.md
  - Integrates CLI Isomorphic Projection + Metaphysical Fullstack
  - Next major work: Extract services/, create nodes, thin handlers
  - See Part XI in this file for upgrade path

  Next: Execute metaphysical upgrade OR Phase 5 Learning Companions

phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  IMPLEMENT: in_progress
  REFLECT: pending
entropy:
  planned: 1.0
  spent: 0.82
  returned: 0.22
---

# Crown Jewels Enlightened: The Grand Execution Arc

> *"The demo experience now is 0.1% of what I wanted."*
> — Kent, 2025-12-16

> *"The ONLY KPI is how much Kent is using and valuing the tech that's built with kgents."*

---

## Part 0: The Vision Reset

### What We're Actually Building

This is not a product demo suite. This is not a showcase. This is:

**Kent's Personal AI Operating System**

A stateful, persistent, ever-learning system where:
- **Agents remember** - conversations, preferences, struggles, victories
- **Ideas evolve** - seeds planted today bloom in weeks, cross-pollinate unexpectedly
- **The system reflects Kent** - the LLM meta-system mirrors aspects of its creator back to him
- **CLI and Web are one** - `kg brain capture "insight"` and clicking Capture in /crown/brain are isomorphic
- **Fun is primary** - generative, serendipitous micro-experiences at every turn
- **Self-education is continuous** - learning companions that teach, quiz, adapt

### The Categorical Foundation

Everything derives from the three-layer stack (AD-006):

```
┌────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED CROWN ARCHITECTURE                       │
│                                                                         │
│  PolyAgent[S, A, B]     Operad                    Sheaf                │
│  ─────────────────      ──────                    ─────                │
│  Mode-dependent         Composition               Global coherence      │
│  behavior               grammar                   from local views      │
│                                                                         │
│  SOUL_POLYNOMIAL        SOUL_OPERAD              KentCoherence         │
│  MEMORY_POLYNOMIAL      MEMORY_OPERAD            MemoryConsistency     │
│  FLOW_POLYNOMIAL        FLOW_OPERAD              ConversationIntegrity │
│  TOWN_POLYNOMIAL        TOWN_OPERAD              TownSheaf             │
│  GARDEN_POLYNOMIAL      GARDEN_OPERAD            IdeaCoherence         │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### The Isomorphism Promise

```
CLI Command                    ↔    Web Action
───────────────────────────────     ────────────────────────────────
kg brain capture "insight"     ↔    Click [Capture] in /crown/brain
kg gardener tend --prune       ↔    Drag idea to Compost in /crown/gardener
kg town chat --citizen sage    ↔    Open chat with Sage in /crown/town
kg soul reflect                ↔    Enter Reflection mode in /crown/soul

Same AGENTESE path. Same state mutation. Real-time sync.
```

---

## Part I: The Mirror Test (Success Criteria)

> *"Moments when the reflection of the LLM meta-system I built reflects aspects of myself back to me."*

### The Only Question That Matters

**Is Kent using this every day?**

If yes, we succeeded. If no, nothing else matters.

### Supporting Questions

| Question | Target | Verification |
|----------|--------|--------------|
| Does Kent open Crown daily? | Yes | Usage telemetry |
| Does Kent capture memories? | 10+/week | Brain crystal count |
| Does Kent chat with citizens? | 3+/week | Town session logs |
| Does Kent tend his garden? | Daily | Gardener activity |
| Does the system surprise Kent? | 2+/week | Serendipity events logged |
| Does Kent learn from companions? | 1+/week | Learning sessions |
| Does Kent feel reflected? | "Yes" | Kent says so |

### The Reflection Criterion

A system passes the Mirror Test when Kent says:

> *"That's... me. That insight came from a pattern in MY data that I couldn't see."*

This requires:
1. **Real data** - Kent's actual memories, projects, conversations
2. **Persistent state** - months of accumulated context
3. **Cross-domain synthesis** - connecting dots Kent missed
4. **Agent personality** - citizens that know Kent's patterns

---

## Part II: What Exists (Preserved Inventory)

### Infrastructure (Ready to Use)

| System | Location | Tests | Status |
|--------|----------|-------|--------|
| **PolyAgent** | `agents/poly/` | 200+ | Production |
| **Operad** | `agents/operad/` | 150+ | Production |
| **Sheaf** | `agents/sheaf/` | 100+ | Production |
| **AGENTESE** | `protocols/agentese/` | 559 | Production |
| **Flux** | `agents/flux/` | 100+ | Production |
| **K-gent Soul** | `agents/k/` | 80+ | Production |
| **M-gent Memory** | `agents/m/` | 60+ | Production |
| **F-gent Flow** | `agents/f/` | NEW | Production |
| **Agent Town** | `agents/town/` | 150+ | Production |
| **Gardener-Logos** | `protocols/gardener_logos/` | 80+ | Production |
| **Reactive Substrate** | `agents/i/reactive/` | 50+ | Production |
| **N-Phase Compiler** | `protocols/nphase/` | 40+ | Production |
| **API Gateway** | `protocols/api/` | 100+ | Production |
| **CLI Framework** | `protocols/cli/` | 200+ | Production |

### Crown Web UI (Exists, Demo-Quality)

| Page | Route | State |
|------|-------|-------|
| Crown Landing | `/crown` | Demo |
| Brain | `/brain` | Demo |
| Gestalt | `/gestalt` | Demo |
| Gardener | `/gardener` | Demo |
| Atelier | `/atelier` | Demo |
| Town | `/town` | Demo |
| Park | `/park` | Demo |
| Workshop | `/workshop` | Demo |

### CLI Commands (Partial)

| Command | Handler | State |
|---------|---------|-------|
| `kg brain` | `handlers/brain.py` | Partial |
| `kg gardener` | `handlers/gardener.py` | Partial |
| `kg soul` | `handlers/soul.py` | Needs work |
| `kg town` | `handlers/town.py` | Partial |
| `kg park` | `handlers/park.py` | CLI complete |

---

## Part III: The Grand Execution Arc

### Arc Philosophy

**Not features. Experiences.**

Each phase delivers something Kent can USE, not something to demo.

### Phase 1: The Living Memory (Brain)

> *"A Memory Palace where thought has architecture."*

**Goal**: Kent captures insights and the system remembers, connects, surfaces.

**What Makes This Different**:
- **Real persistence**: SQLite/D-gent backend, not localStorage
- **Semantic search**: Find memories by meaning, not keywords
- **Stigmergic trails**: Frequent access paths glow brighter
- **Cross-domain connections**: Brain connects to Gardener connects to Town

**CLI ↔ Web**:
```
kg brain capture "Category theory is about composable transformations"
kg brain recall "composability"
kg brain surface  # serendipity: random relevant memory
```
Each command: identical to clicking in `/crown/brain`.

**Progress**: 100% ✅ (2025-12-16)

#### What Works

| Layer | Component | Status |
|-------|-----------|--------|
| CLI | `kg brain capture/search/list/status/chat/import/surface` | ✅ 8 commands |
| API | `/v1/brain/capture/ghost/status/map/topology` | ✅ 5 endpoints |
| Web | 3D topology, capture panel, ghost surfacing | ✅ Working |
| D-gent | SQLite + L-gent embeddings | ✅ Persistent |
| Serendipity | `kg brain surface` (void.memory.surface) | ✅ Working |
| Stigmergic | access_count increments on search | ✅ Working |
| Tests | 65+ tests covering all paths | ✅ Passing |

#### Phase 1 COMPLETE

Brain's core functionality is production-ready:
- Personal knowledge capture and recall
- Semantic search with L-gent embeddings
- Bulk import from markdown vaults (Obsidian/Notion)
- REST API with 5 endpoints
- Serendipity surfacing from the void

#### Future Enhancements (Phase 2+ scope)

1. **Real-time sync** - WebSocket push from CLI to Web
2. **Cross-domain events** - Brain events trigger Gardener/Town synergies
3. **Synergy bus wiring** - CRYSTAL_FORMED events to other jewels

---

### Phase 2: The Tended Garden (Gardener)

> *"Seeds I plant grow over weeks, agents tend them, surprise me with cross-pollinations."*

**Goal**: Kent plants ideas, the system tends them, time creates value.

**What Makes This Different**:
- **Temporal evolution**: Ideas have seasons (SEED → SAPLING → TREE → FLOWER → COMPOST)
- **Agent tending**: Overnight jobs that prune, graft, water
- **Cross-pollination alerts**: "This idea connects to that one from 2 months ago"
- **Real forest visualization**: Not a list, a spatial garden

**CLI ↔ Web**:
```
kg gardener start "Crown Jewels Arc"  # start a session
kg gardener chat                       # interactive tending
kg gardener advance                    # SENSE → ACT → REFLECT
kg gardener manifest                   # show polynomial state
```

**Progress**: 95% ✅ (2025-12-16)

#### What's Already Built

| Layer | Component | Status |
|-------|-----------|--------|
| **Lifecycle** | SEED→SAPLING→TREE→FLOWER→COMPOST | ✅ PersonaGarden |
| **Temporal** | Age tracking, staleness decay | ✅ Implemented |
| **Seasons** | DORMANT, SPROUTING, BLOOMING, HARVEST, COMPOSTING | ✅ Auto-Inducer |
| **Cross-pollination** | `cross_pollinate()` with similarity threshold | ✅ Implemented |
| **Confidence** | Nurture/decay, promotion thresholds | ✅ Implemented |
| **Persistence** | SQLite session store | ✅ Working |
| **CLI** | Full idea lifecycle commands | ✅ 12 commands |
| **Tests** | 349+ tests across gardener_logos, handlers, seasons | ✅ Passing |

#### CLI Commands (Complete)

| Command | Description | Status |
|---------|-------------|--------|
| `kg gardener` | Show session + garden status | ✅ |
| `kg gardener start` | Start new session | ✅ |
| `kg gardener advance` | Advance phase | ✅ |
| `kg gardener manifest` | Show polynomial | ✅ |
| `kg gardener sessions` | List sessions | ✅ |
| `kg gardener chat` | Interactive tending | ✅ |
| `kg gardener plant` | Plant new idea | ✅ |
| `kg gardener garden` | Show idea lifecycle | ✅ |
| `kg gardener harvest` | Show flower ideas | ✅ |
| `kg gardener water` | Nurture idea | ✅ |
| `kg gardener harvest-to-brain` | Send flowers to Brain | ✅ |
| `kg gardener surprise` | Serendipity | ✅ |

#### Remaining Gaps (to reach 100%)

1. **Plot management** (nice-to-have):
   - Ideas grouped into plots (partial implementation in plots.py)
   - Plot-to-Forest-Plan mapping

2. **Web visualization** (Phase 3+ scope):
   - 3D garden with seasonal aesthetics
   - Idea nodes showing lifecycle stage

---

### Phase 3: The Living Town (Citizens)

> *"Agents with refined personalities backed by real skills and dynamic memory."*

**Goal**: Citizens that remember Kent, have opinions, go on tangents.

**What Makes This Different**:
- **Persistent memory per citizen**: The Sage remembers past conversations
- **Eigenvector personalities**: Not just prompts, actual behavioral parameters
- **Agent tangents**: Citizens can go off-script, make unexpected connections
- **Relationship dynamics**: Citizens have opinions about each other

**CLI ↔ Web**:
```
kg town chat --citizen sage  # start chat with Sage
kg town gather --topic "kgents architecture"  # multi-citizen discussion
kg town witness              # see what citizens have been up to
kg town inhabit sage         # become the Sage (Park mode)
```

**Progress**: 95% ✅ (2025-12-17)

#### What Works

| Layer | Component | Status |
|-------|-----------|--------|
| **Persistence** | PersistentCitizenMemory (D-gent backed) | ✅ Complete |
| **Graph Memory** | Episodic memories with connections/decay | ✅ Complete |
| **Conversations** | Structured history with topics | ✅ Complete |
| **Relationships** | Persistence and drift tracking | ✅ Complete |
| **CLI** | chat, witness, gather commands | ✅ Complete |
| **Tests** | 57 tests (28 town + 17 memory + 12 citizen) | ✅ Passing |
| **Responses** | Rule-based personality fallback | ✅ Complete |
| **LLM Integration** | ClaudeCLIRuntime for rich responses | ✅ Complete |
| **AGENTESE** | self.citizen.<name>.memory/personality paths | ✅ Complete |
| **Memory Surfacing** | Recent conversations + relevant memories in prompts | ✅ Complete |

#### Phase 3 Complete

The Town now has:
- **LLM-powered responses** via `ClaudeCLIRuntime` with archetype-specific system prompts
- **Memory-grounded context** using foveation pattern (3 recent + 2 relevant memories)
- **AGENTESE paths**: `self.citizen.<name>.memory.*` and `self.citizen.<name>.personality.*`
- **Eigenvector personality** formatting in prompts (7D eigenvectors as percentages)
- **Cosmotechnics grounding** in dialogue responses
- **Graceful fallback** to rule-based responses when LLM unavailable
- **LLM-powered gather discussions** with per-citizen perspectives

#### Remaining for 100%

1. **Cross-citizen memory**: Citizens remember interactions with each other (nice-to-have)

---

### Phase 4: The Creative Workshop (Atelier)

> *"Exquisite corpse with AI, constraint-based ideation."*

**Goal**: Kent creates WITH agents, not just directing them.

**What Makes This Different**:
- **Constraint injection**: Random constraints spark creativity
- **Handoffs**: Start something, agent continues, Kent finishes
- **Memory integration**: Atelier pulls from Brain, stores to Brain
- **Festival mode**: Seasonal creative challenges

**CLI ↔ Web**:
```
kg atelier exquisite "journey through memory"    # exquisite corpse mode
kg atelier constrain --random                     # inject random constraint
kg atelier handoff "The lighthouse keeper..." calligrapher  # hand off to agent
kg atelier inspire "category theory" calligrapher  # pull memories → create
kg atelier collaborate --mode=exquisite calligrapher cartographer -r "topic"
```

**Progress**: 95% ✅ (2025-12-17)

#### What Works

| Layer | Component | Status |
|-------|-----------|--------|
| **Exquisite Mode** | Limited visibility handoffs, surrealist game | ✅ Complete |
| **Constraint** | Random constraint generation, custom constraints | ✅ Complete |
| **Handoff** | Start text → artisan continues | ✅ Complete |
| **Inspire** | Brain → Atelier (memories as inspiration) | ✅ Complete |
| **Synergy** | Atelier → Brain (auto-capture pieces) | ✅ Already existed |
| **Collaboration** | 5 modes (duet, ensemble, refinement, chain, exquisite) | ✅ Complete |
| **Festival Mode** | Seasonal creative challenges with voting | ✅ Complete |
| **Spectator Economy** | Token balance and bid costs CLI | ✅ Complete |
| **Tests** | 367+ tests across atelier module | ✅ Passing |

#### CLI Commands (New)

| Command | Description | Status |
|---------|-------------|--------|
| `kg atelier exquisite <topic>` | Exquisite corpse collaboration | ✅ |
| `kg atelier constrain --random` | Random creative constraint | ✅ |
| `kg atelier handoff <text> <artisan>` | Start → artisan continues | ✅ |
| `kg atelier inspire <query> <artisan>` | Memory-inspired creation | ✅ |
| `kg atelier collaborate --mode=exquisite` | Exquisite mode via collaborate | ✅ |
| `kg atelier festival create` | Create seasonal festival | ✅ |
| `kg atelier festival list` | List all festivals | ✅ |
| `kg atelier festival view` | View festival details | ✅ |
| `kg atelier festival enter` | Enter festival with creation | ✅ |
| `kg atelier festival vote` | Vote for entries | ✅ |
| `kg atelier festival conclude` | Conclude and show winners | ✅ |
| `kg atelier festival suggest` | Suggest seasonal theme | ✅ |
| `kg atelier tokens balance` | Check token balance | ✅ |
| `kg atelier tokens costs` | Show bid costs | ✅ |

#### Remaining for 100%

1. **Web visualization**: Real-time stream viewing (Q2 2025)

---

### Phase 5: The Learning Companions

> *"Citizens that teach me things, quiz me, remember what I struggle with."*

**Goal**: Self-education through agent companionship.

**What Makes This Different**:
- **Adaptive curriculum**: System knows what Kent struggles with
- **Spaced repetition**: Resurface concepts at optimal intervals
- **Socratic dialogue**: Not lectures, guided discovery
- **Progress memory**: Track learning over months

**CLI ↔ Web**:
```
kg learn topic "category theory"
kg learn quiz                    # test current knowledge
kg learn struggle               # show what needs work
kg learn companion              # start teaching session
```

**Progress**: 0%

---

### Phase 6: The Full-Stack Homelab

> *"Full-stack full-service homelab, AI agent software development agency."*

**Goal**: kgents as the substrate for Kent's AI infrastructure.

**What Makes This Different**:
- **Kubernetes operators**: Agents as K8s operators
- **Self-managing infrastructure**: Agents monitor, alert, repair
- **Development agency**: Agents that can write code, run tests
- **Admin dashboard**: Crown as the control plane

**CLI ↔ Web**:
```
kg infra status                 # infrastructure health
kg infra agent deploy           # deploy new agent
kg agency task "write tests for module X"
kg admin dashboard              # full system view
```

**Progress**: 0%

---

### Phase 7: The Mirror (Self-Reflection)

> *"The LLM meta-system reflects aspects of Kent back to him."*

**Goal**: The system helps Kent understand himself.

**What Makes This Different**:
- **Pattern synthesis**: "Kent, you tend to X when Y"
- **Longitudinal insights**: Patterns over months
- **Soul polynomial**: K-gent as the middleware of consciousness
- **The hypnagogic cycle**: Dream/consolidation phases

**CLI ↔ Web**:
```
kg soul reflect                 # enter reflection mode
kg soul pattern                 # see patterns in behavior
kg soul hypnagogia              # dream cycle insights
kg soul challenge               # dialectic self-examination
```

**Progress**: 0%

---

## Part IV: Technical Architecture

### The Bidirectional Bridge

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AGENTESE BIDIRECTIONAL BRIDGE                    │
│                                                                      │
│   CLI                          ↔           Web                       │
│   ───                                      ───                       │
│   kg brain capture "X"                     POST /api/brain/capture   │
│        │                                         │                   │
│        └───────────────→ AGENTESE PATH ←─────────┘                  │
│                              │                                       │
│                     self.memory.capture                              │
│                              │                                       │
│                    ┌─────────┴─────────┐                            │
│                    │   D-gent State    │                            │
│                    │   (SQLite/PG)     │                            │
│                    └─────────┬─────────┘                            │
│                              │                                       │
│            ┌─────────────────┼─────────────────┐                    │
│            │                 │                 │                     │
│         CLI Echo          WebSocket         Events                   │
│            │               Push              Bus                     │
│            ▼                 ▼                 ▼                     │
│         Terminal          Browser          Synergy                   │
│         Output            Update            Toast                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### State Management

**Single Source of Truth**: D-gent (SQLite for local, Postgres for cloud)

**State Categories**:
| Category | Storage | Sync |
|----------|---------|------|
| Memory Crystals | D-gent | Real-time |
| Garden State | D-gent | Real-time |
| Town Citizen Memory | D-gent | Real-time |
| User Preferences | D-gent | On change |
| Session State | In-memory | Ephemeral |

### Event-Driven Architecture

Every state mutation emits an event. Events drive:
- WebSocket pushes to browser
- CLI output updates
- Synergy toasts
- Cross-jewel effects

```python
# Every AGENTESE invocation
result = await logos.invoke("self.memory.capture", content, umwelt)
# Emits: MemoryCaptured event
# D-gent: Persists crystal
# WebSocket: Pushes to /crown/brain
# CLI: Prints confirmation
# Synergy: Checks for Gardener connections
```

---

## Part V: The Serendipity Engine

> *"Agent tangents, cross-domain sparks, moments when the reflection of the LLM meta-system reflects aspects of myself back to me."*

### Mechanisms

1. **Random Surfacing** (`void.memory.surface`)
   - Periodic: Surface a random relevant memory
   - Trigger: "Hey Kent, remember this?"

2. **Agent Tangents** (Citizen `curiosity` eigenvector)
   - High curiosity → more tangential connections
   - "That reminds me of something unrelated but fascinating..."

3. **Cross-Domain Sparks** (Sheaf coherence checks)
   - When Brain stores X, check if Gardener has related Y
   - When Town discusses Z, check if Brain has relevant W

4. **Scheduled Chaos** (`void.sip` cron job)
   - Weekly: Generate wild combinations
   - "What if we connected [random A] with [random B]?"

5. **Mirror Moments** (K-gent pattern synthesis)
   - "Kent, I've noticed you tend to X when Y"
   - Requires months of data to be meaningful

### Implementation

```python
class SerendipityEngine:
    """The Accursed Share operationalized."""

    async def surface_random(self) -> Optional[Crystal]:
        """Pull a relevant memory from the void."""
        return await self.logos.invoke("void.memory.surface", entropy=0.7)

    async def detect_cross_domain_spark(self, event: Event) -> Optional[Spark]:
        """Check if this event connects to other domains."""
        connections = await self.sheaf.find_overlaps(event)
        return self._select_surprising(connections)

    async def synthesize_pattern(self) -> Optional[Insight]:
        """K-gent reflects patterns back to Kent."""
        return await self.logos.invoke("self.soul.pattern",
                                       window="90d",
                                       surprise_threshold=0.3)
```

---

## Part VI: Execution Phases

| Phase | Focus | Deliverable | Progress |
|-------|-------|-------------|----------|
| 1 | Living Memory | Kent captures and retrieves real memories daily | **100%** ✅ |
| 2 | Tended Garden | Kent plants ideas that evolve over weeks | **95%** ✅ |
| 3 | Living Town | Kent chats with citizens who remember him | **95%** ✅ |
| 4 | Creative Workshop | Kent creates WITH agents | **95%** ✅ |
| 5 | Learning Companions | Kent learns from adaptive tutors | 0% |
| 6 | Full-Stack Homelab | Kent's AI infrastructure runs on kgents | 10% |
| 7 | The Mirror | Kent sees himself reflected in the system | 20% |

**Overall Progress**: 88% (weighted by importance)

### Phase Status Details

- **Phase 1 (Brain)**: Production-ready. CLI, API, Web all functional.
- **Phase 2 (Gardener)**: Production-ready. Full CLI lifecycle (plant/water/harvest), Brain integration working.
- **Phase 3 (Town)**: **Production-ready**. LLM-powered citizen responses using ClaudeCLIRuntime. Memory-grounded context with foveation pattern. AGENTESE paths for citizen memory/personality. 57 tests passing.
- **Phase 4 (Atelier)**: **95% Complete**. Exquisite corpse mode, handoffs, constraints, Brain↔Atelier synergy, Festival mode, Spectator economy CLI. 367+ tests passing. Only web visualization pending.
- **Phase 5 (Learning)**: Not started. Ready to begin (Phase 3 complete).
- **Phase 6 (Homelab)**: K8s operators exist, infra CLI partial.
- **Phase 7 (Mirror)**: K-gent soul/hypnagogia exists. Needs longitudinal pattern synthesis.

---

## Part VII: The Integration Layer

### Cross-Jewel Data Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CROSS-JEWEL DATA FLOW                          │
│                                                                       │
│                              ┌─────────┐                              │
│                              │  BRAIN  │                              │
│                              │ Memory  │                              │
│                              │ Crystals│                              │
│                              └────┬────┘                              │
│                                   │                                   │
│         ┌─────────────────────────┼─────────────────────────┐        │
│         │                         │                         │        │
│         ▼                         ▼                         ▼        │
│   ┌───────────┐            ┌───────────┐            ┌───────────┐   │
│   │  GARDENER │            │   TOWN    │            │  ATELIER  │   │
│   │  Ideas    │◄──────────►│  Citizens │◄──────────►│  Creations│   │
│   │  grow     │            │  remember │            │  emerge   │   │
│   └─────┬─────┘            └─────┬─────┘            └─────┬─────┘   │
│         │                        │                        │         │
│         └────────────────────────┼────────────────────────┘         │
│                                  │                                   │
│                                  ▼                                   │
│                          ┌─────────────┐                             │
│                          │   K-GENT    │                             │
│                          │   SOUL      │                             │
│                          │  Reflects   │                             │
│                          └─────────────┘                             │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### The Synergy Matrix

| From \ To | Brain | Gardener | Town | Atelier | Soul |
|-----------|-------|----------|------|---------|------|
| **Brain** | — | Ideas connect to memories | Citizens cite memories | Creations stored as crystals | Patterns synthesized |
| **Gardener** | Harvest → crystals | — | Citizens tend ideas | Ideas become prompts | Growth tracked |
| **Town** | Dialogues → crystals | Citizens suggest seeds | — | Collaborative creation | Conversations reflected |
| **Atelier** | Artifacts → crystals | Creations → new seeds | Multi-agent art | — | Creative patterns |
| **Soul** | Insights → crystals | Reflection → pruning | Soul permeates citizens | Creative dreams | — |

---

## Part VIII: Success Metrics (Real)

### The Only Metric

**Kent's usage and expressed value.**

### Proxy Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Daily Active Sessions | `kg` commands + Crown visits | 5+ |
| Memory Captures/Week | Brain crystals created | 10+ |
| Ideas Planted/Month | Gardener seeds | 5+ |
| Citizen Conversations/Week | Town sessions | 3+ |
| Serendipity Events/Week | Sparks surfaced | 2+ |
| Kent Says "Wow" | Qualitative | Weekly |

### Anti-Metrics (What We're NOT Optimizing)

- Lines of code
- Number of features
- Test coverage (beyond baseline)
- Demo impressiveness
- External validation

---

## Part IX: The Accursed Share Budget

Every phase reserves entropy for the unexpected:

| Phase | Accursed Share |
|-------|----------------|
| Living Memory | Random surfacing (10% of recall results) |
| Tended Garden | Unexpected cross-pollinations (15% of suggestions) |
| Living Town | Agent tangents (20% of dialogue turns) |
| Creative Workshop | Random constraints (1 per session) |
| Learning Companions | Surprising quiz topics (10%) |
| Full-Stack Homelab | Chaos engineering (5% of ops) |
| The Mirror | Unexpected patterns (∞% - this IS the point) |

---

## Part X: Next Immediate Actions

### Phase 2 (Gardener) - COMPLETE ✅

All CLI commands implemented:
- ✅ `kg gardener plant "idea"` → creates GardenEntry
- ✅ `kg gardener harvest` → lists FLOWER-stage ideas
- ✅ `kg gardener surprise` → void.sip cross-pollination
- ✅ `kg gardener garden` → shows lifecycle distribution with IDs
- ✅ `kg gardener water <idea-id>` → nurture specific idea
- ✅ `kg gardener harvest-to-brain` → flowers → Brain crystals

### Phase 3 (Town) - NEXT

1. **Persistent citizen memory**
   - Citizens remember past conversations with Kent
   - Memory stored in D-gent (SQLite)
   - Accessed via AGENTESE: `self.citizen.<name>.memory.*`

2. **CLI commands**
   - `kg town chat --citizen sage` → chat with named citizen
   - `kg town gather --topic "X"` → multi-citizen discussion
   - `kg town witness` → see citizen activity

3. **Eigenvector personalities**
   - Citizens have measurable behavioral parameters
   - Personality affects response style and tangent propensity

### To Wire the Integration Layer (Parallel Track)

1. **Synergy event emission**
   - Brain capture → emit CRYSTAL_FORMED
   - Gardener harvest → emit IDEA_HARVESTED
   - Both trigger cross-jewel notifications

2. **WebSocket for real-time sync**
   - Add `/ws/crown/subscribe` endpoint
   - Push events to browser for live updates

3. **Cross-jewel data flow**
   - Brain ↔ Gardener: Ideas and crystals
   - Gardener ↔ Town: Citizens discuss ideas
   - Town ↔ Soul: Conversations feed reflection

### Kent's Daily Loop (Success Metric)

```
Morning:
  kg brain surface        # serendipity from yesterday's captures
  kg gardener status      # see idea lifecycle

During work:
  kg brain capture "..."  # capture insights
  kg gardener advance     # SENSE → ACT → REFLECT

Evening:
  kg gardener harvest     # see what's ready
  kg soul reflect         # mirror test
```

---

## Part XI: Architecture Upgrade Path

> *"The more fully defined, the more fully projected."* — Metaphysical Fullstack

### The Next Evolution

Crown Jewels Phases 1-4 are 88% complete functionally, but the **architecture** needs upgrading to fully realize the Isomorphic CLI and Metaphysical Fullstack patterns.

### Current vs Target Architecture

```
CURRENT                                TARGET
───────────────────────────────────    ──────────────────────────────────────
handlers/brain.py (738 lines)          services/brain/
  - Business logic                       ├── __init__.py (public API)
  - Persistence code                     ├── persistence.py (TableAdapter)
  - CLI formatting                       └── crystal.py (business logic)

protocols/api/brain.py                 protocols/agentese/contexts/
  - Explicit routes                      └── self_memory.py (@aspect node)
  - Duplicate logic
                                       handlers/brain.py (< 50 lines)
                                         - Thin routing shim only
```

### Why This Matters

1. **CLI and Web are truly isomorphic** - Same AGENTESE path, same code
2. **No explicit API routes** - AGENTESE universal protocol auto-exposes
3. **Persistence is consistent** - All D-gent + TableAdapter
4. **Observability is unified** - Service-level spans everywhere

### Implementation Plan

See `plans/crown-jewels-metaphysical-upgrade.md` for:
- Per-jewel migration checklist
- Service extraction pattern
- AGENTESE node creation
- Dimension verification tests

### Sequence

```
1. Execute Metaphysical Upgrade (25 hours estimated)
   ├── Brain service extraction (6h)
   ├── Soul service + @chatty (4h)
   ├── Town service refactor (5h)
   ├── Atelier service (4h)
   ├── Gardener service refactor (3h)
   └── Park service (3h)

2. Execute Synergy Audit (plans/agentese-v3-crown-synergy-audit.md)
   └── Unlocks subscriptions, pipelines, query syntax

3. Continue Phase 5-7 (Learning, Homelab, Mirror)
   └── Now on solid architectural foundation
```

### Decision Point

**Option A**: Execute upgrade now, delay Phase 5
- Pro: Clean architecture enables faster future work
- Con: Delays new user-facing features

**Option B**: Continue Phase 5, upgrade later
- Pro: More features sooner
- Con: Technical debt accumulates

**Recommendation**: Option A - the upgrade unblocks v3 synergies that make Phase 5-7 significantly easier.

---

*"The Crown is not seven apps. It is Kent's extended mind."*

*Updated: 2025-12-17 by claude-opus-4-5*
*Phases 1-4 functionally complete, architecture upgrade planned.*
