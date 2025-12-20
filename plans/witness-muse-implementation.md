---
path: plans/witness-muse-implementation
status: active
progress: 70
last_touched: 2025-12-19
touched_by: claude-opus-4-5
blocking: []
enables: [kgentsd-crown-jewel, cross-jewel-synergy]
session_notes: |
  Generated from brainstorming/2025-12-19-the-witness-and-the-muse.md
  Two oblique Crown Jewels that run passively via kgentsd.
  Witness captures experience → Muse interprets patterns → Whispers guidance.

  2025-12-19 AUDIT: Witness service already has 177 tests, comprehensive
  polynomial, operad, watchers, trust system. Key insight: self.witness
  (trust-gated agency) + time.witness (experience crystallization) are
  COMPLEMENTARY visions—extend, don't replace.

  2025-12-19 IMPLEMENTATION:
  - Added ExperienceCrystal, MoodVector, TopologySnapshot, Narrative (28 tests)
  - Created services/muse/ with MusePolynomial, ArcPhase, WhisperEngine (33 tests)
  - Total: 314 tests pass (Witness 205 + Muse 33 + related)

  2025-12-19 P0.2 COMPLETE:
  - Added WitnessSheaf for crystallization gluing (36 tests)
  - EventSource enum for watcher contexts
  - LocalObservation dataclass for per-source views
  - Sheaf law verification (identity, associativity)
  - Total: 317 tests pass in Witness service

  Phase 0-2 COMPLETE:
  - P0: Crystal (28) + Sheaf (36) + Muse polynomial (33) = 97 new tests
  - P1: Subsumed by P0 (crystal already had all P1 items)
  - P2: Subsumed by P0.3 (arc.py + whisper.py already complete)
  - Ready for Phase 3 (AGENTESE node registration)
phase_ledger:
  PLAN: complete
  AUDIT: complete
  PHASE0: complete (crystal + sheaf + muse foundation)
  PHASE1: complete (subsumed by P0)
  PHASE2: complete (subsumed by P0)
  PHASE3: complete (AGENTESE integration - time.witness + self.muse nodes)
---

# The Witness and The Muse: Implementation Plan

> *"The Witness sees. The Muse speaks. Together, they make work meaningful."*

---

## 🔍 Infrastructure Audit (2025-12-19)

### Existing Witness Service: `services/witness/`

**Already Built** (177 tests):
| Component | Status | What It Does |
|-----------|--------|--------------|
| `polynomial.py` | ✅ Complete | TrustLevel (L0-L3), WitnessPhase, WitnessState, transition functions |
| `operad.py` | ✅ Complete | WITNESS_OPERAD with sense/analyze/suggest/act/invoke operations |
| `node.py` | ✅ Complete | @node("self.witness") with 7 aspects, affordance matrix |
| `persistence.py` | ✅ Complete | Thought/Action/Trust persistence via D-gent |
| `contracts.py` | ✅ Complete | Request/Response dataclasses for all aspects |
| `watchers/` | ✅ Complete | Git, Filesystem, Test, CI, AGENTESE watchers with BaseWatcher |
| `trust/` | ✅ Complete | ActionGate, BoundaryChecker, EscalationCriteria, ConfirmationManager |
| `bus.py` | ✅ Complete | SynergyBus integration |
| `daemon.py` | ✅ Complete | kgentsd integration scaffold |

**Key Insight**: The existing Witness focuses on **trust-gated autonomous agency** (kgentsd 8th Crown Jewel). The brainstorming doc's vision adds **experience crystallization** as a complementary layer.

### Two Witness Aspects (Complementary, Not Conflicting)

| Aspect | AGENTESE Path | Purpose | Status |
|--------|---------------|---------|--------|
| **Trust Agency** | `self.witness` | Earn trust → Act autonomously | ✅ Built (177 tests) |
| **Experience Crystallization** | `time.witness` | Capture → Synthesize → Crystal | ❌ Not built |

**Revised Strategy**: Extend `services/witness/` with crystallization capabilities, not create a parallel service.

### Muse Service: `services/muse/`

**Status**: ❌ Not built—needs full implementation.

### Infrastructure Available

| Component | Location | Use For |
|-----------|----------|---------|
| FluxAgent | `agents/flux/` | Stream processing for passive observation |
| BaseWatcher | `services/witness/watchers/base.py` | Event source pattern |
| SynergyBus | Already wired | Cross-jewel events |
| D-gent | Already integrated | Crystal persistence |
| K-gent | `agents/k/` | Narrative synthesis, encouragement |

---

## Revised Implementation Strategy

**Principle**: *"Wiring > Creation"* — Extend existing infrastructure, don't rebuild.

### Phase 0: Foundation (Reduced Scope)

The existing Witness already has polynomial, operad, watchers. Focus on:
1. **Experience Crystal** dataclass and sheaf (new)
2. **Muse polynomial** (new service)
3. **Integration hooks** for crystallization trigger

### Phase 1-5: As Originally Planned

But with awareness that watchers, persistence, and event flow already work.

---

## Overview

Two complementary Crown Jewel extensions:

| Jewel | Purpose | AGENTESE Context | Passive? |
|-------|---------|------------------|----------|
| **The Witness** (extended) | Add crystallization to existing | `time.witness` | Yes |
| **The Muse** (new) | Story arc, whispers | `self.muse` | Yes |

**Key Architecture Decision**: Both run passively via kgentsd. Witness already has watchers—crystallization hooks into existing event flow.

---

## Dependencies

| Dependency | Status | Required For |
|------------|--------|--------------|
| Existing Witness service | ✅ **Complete** (177 tests) | Foundation |
| kgentsd event architecture | Planning | Event sources already exist via watchers |
| D-gent persistence | ✅ Complete | Crystal storage |
| K-gent LLM integration | ✅ Complete | Narrative synthesis, encouragement |
| SynergyBus | ✅ Complete | Cross-jewel events |
| FluxAgent | ✅ Complete | Continuous processing |

**Critical Path**: Crystallization module → Muse polynomial → Integration

---

## Phase 0: Foundation (Revised)

### P0.1: Experience Crystal (NEW) ✅ COMPLETE

**Goal**: Define the atomic memory unit for crystallization.

- [x] `ExperienceCrystal` frozen dataclass with semantic fields
- [x] `MoodVector` for affective signature (7 dimensions)
- [x] `TopologySnapshot` for codebase position
- [x] `as_memory()` → DgentEntry projection
- [x] `Narrative` with template fallback
- [x] Topic extraction from existing Thought stream

**Files**:
```
impl/claude/services/witness/
├── crystal.py          # ExperienceCrystal, MoodVector, TopologySnapshot, Narrative
└── _tests/
    └── test_crystal.py  # 28 tests
```

**Tests**: 28 ✅

### P0.2: Witness Sheaf for Crystallization (NEW) ✅ COMPLETE

**Goal**: Glue local views into coherent crystals.

- [x] `WitnessSheaf` implementing Sheaf protocol
- [x] `EventSource` enum for watcher contexts (Git, Filesystem, Tests, AGENTESE, CI, User)
- [x] `LocalObservation` dataclass for per-source views
- [x] `overlap()` for event source capability overlap
- [x] `compatible()` for temporal consistency (with tolerance)
- [x] `glue()` fusing observations → ExperienceCrystal
- [x] `restrict()` for inverse extraction (crystal → source)
- [x] Property tests for sheaf laws (identity, associativity)

**Files**:
```
impl/claude/services/witness/
├── sheaf.py            # WitnessSheaf, EventSource, LocalObservation
└── _tests/
    └── test_sheaf.py   # 36 tests
```

**Tests**: 36 ✅

### P0.3: Muse Polynomial (NEW SERVICE) ✅ COMPLETE

**Goal**: Define state machine for Muse lifecycle.

- [x] Define `MuseState` enum (SILENT, CONTEMPLATING, WHISPERING, RESONATING, REFLECTING, DORMANT)
- [x] Implement `MUSE_POLYNOMIAL` with positions and directions
- [x] Write `muse_transition` function
- [x] Key insight: SILENT ≠ DORMANT (actively observing vs cooldown)
- [x] ArcPhase (Freytag's Pyramid) and StoryArcDetector
- [x] WhisperEngine with DismissalMemory

**Files**:
```
impl/claude/services/muse/
├── __init__.py
├── polynomial.py       # MuseState, MUSE_POLYNOMIAL, transition handlers
├── arc.py              # ArcPhase, StoryArc, StoryArcDetector
├── whisper.py          # Whisper, WhisperEngine, DismissalMemory
└── _tests/
    └── test_polynomial.py  # 33 tests
```

**Tests**: 33 ✅

---

## Phase 1: Crystallization (Week 2) ✅ COMPLETE (merged into P0)

> **Note**: P1.1-P1.3 were completed as part of Phase 0. The original plan had overlap.

### P1.1: Experience Crystal ✅ COMPLETE (see P0.1)

Completed in crystal.py with 28 tests.

### P1.2: Narrative Synthesis ✅ COMPLETE (see P0.1)

Completed in crystal.py - `Narrative` dataclass with `template_fallback()`.
K-gent LLM integration deferred to Phase 4 (wiring).

### P1.3: Witness Sheaf ✅ COMPLETE (see P0.2)

Completed in sheaf.py with 36 tests.

---

## Phase 2: Muse Core (Week 3) ✅ COMPLETE (merged into P0.3)

> **Note**: P2.1-P2.2 were completed as part of Phase 0.3 (Muse foundation).

### P2.1: Story Arc Detection ✅ COMPLETE (see P0.3)

Completed in arc.py:
- [x] `ArcPhase` enum (Freytag's Pyramid: EXPOSITION→RISING_ACTION→CLIMAX→FALLING_ACTION→DENOUEMENT)
- [x] `StoryArc` dataclass with phase, confidence, tension, momentum
- [x] `StoryArcDetector` using signal aggregation

### P2.2: Whisper Engine ✅ COMPLETE (see P0.3)

Completed in whisper.py + polynomial.py:
- [x] `Whisper` frozen dataclass
- [x] `Suggestion` dataclass with confidence, urgency, context_hash
- [x] `DismissalMemory` with category tracking and decay
- [x] `WhisperEngine` with generate_suggestion(), should_deliver(), deliver()
- [x] `MusePolynomial` with full state machine (6 states, 10 input types)

---

## Phase 3: AGENTESE Integration (Week 4) ✅ COMPLETE

### P3.1: Time Witness Node ✅ COMPLETE

**Goal**: Register time.witness in AGENTESE for crystallization.

- [x] `@node("time.witness")` registration
- [x] Contract definitions:
  - `manifest` → TimeWitnessManifestResponse
  - `attune` → AttuneRequest/AttuneResponse
  - `mark` → MarkRequest/MarkResponse
  - `crystallize` → CrystallizeRequest/CrystallizeResponse
  - `timeline` → TimelineRequest/TimelineResponse
  - `crystal` → CrystalQueryRequest/CrystalQueryResponse
  - `territory` → TerritoryRequest/TerritoryResponse
- [x] Affordance matrix by observer archetype
- [x] All aspect implementations

**Files**:
```
impl/claude/services/witness/
├── crystallization_node.py  # @node("time.witness") registration
├── contracts.py             # Crystallization contracts added
└── _tests/
    └── test_node.py
```

**Key Implementation Notes**:
- time.witness is SEPARATE from self.witness (trust-gated agency)
- Crystallization transforms ephemeral Thoughts → durable ExperienceCrystals
- Uses WitnessSheaf for gluing multiple event sources

### P3.2: Muse Node ✅ COMPLETE

**Goal**: Register Muse in AGENTESE for story arc and whispers.

- [x] `@node("self.muse")` registration
- [x] Contract definitions:
  - `manifest` → MuseManifestResponse
  - `arc` → ArcRequest/ArcResponse
  - `tension` → TensionRequest/TensionResponse
  - `whisper` → WhisperRequest/WhisperResponse
  - `encourage` → EncourageRequest/EncourageResponse
  - `reframe` → ReframeRequest/ReframeResponse
  - `summon` → SummonRequest/SummonResponse
  - `dismiss` → DismissRequest/DismissResponse
  - `accept` → AcceptRequest/AcceptResponse
  - `history` → HistoryRequest/HistoryResponse
- [x] Affordance matrix
- [x] All aspect implementations (10 aspects)

**Files**:
```
impl/claude/services/muse/
├── node.py              # @node("self.muse") registration
├── contracts.py         # All Muse contracts
└── _tests/
    └── test_polynomial.py  # 33 tests
```

**Key Implementation Notes**:
- Muse uses MusePolynomial state machine for whisper lifecycle
- Integrates with StoryArcDetector for Freytag's Pyramid phases
- WhisperEngine handles dismissal memory and cooldowns

### Phase 3 Summary

**Total**: 448 tests pass (Witness 415 + Muse 33)

**AGENTESE Paths Added**:
- `time.witness.manifest` (crystallization status)
- `time.witness.attune` (start observation)
- `time.witness.mark` (user markers)
- `time.witness.crystallize` (trigger crystallization)
- `time.witness.timeline` (crystal history)
- `time.witness.crystal` (query crystals)
- `time.witness.territory` (codebase heat map)
- `self.muse.manifest` (Muse state)
- `self.muse.arc` (story arc phase)
- `self.muse.tension` (tension level)
- `self.muse.whisper` (current whisper)
- `self.muse.encourage` (request encouragement)
- `self.muse.reframe` (request perspective shift)
- `self.muse.summon` (force suggestion)
- `self.muse.dismiss` (dismiss whisper)
- `self.muse.accept` (accept whisper)
- `self.muse.history` (whisper history)

---

## Phase 4: kgentsd Wiring (Week 5)

### P4.1: WitnessFlux

**Goal**: Wire Witness to kgentsd event stream.

- [ ] `WitnessFlux` extending FluxAgent
- [ ] Event source subscriptions:
  - AGENTESE invocations
  - Filesystem events
  - Git events
  - User markers
- [ ] Crystallization trigger logic
- [ ] D-gent storage integration
- [ ] Tests with mock event sources

**Files**:
```
impl/claude/services/witness/
├── flux.py             # WitnessFlux
├── persistence.py      # D-gent adapter
└── _tests/
    └── test_flux.py
```

**Tests**: 20+

### P4.2: MuseFlux

**Goal**: Wire Muse to Witness crystal stream.

- [ ] `MuseFlux` extending FluxAgent
- [ ] Crystal subscription (from WitnessFlux output)
- [ ] Arc update emission
- [ ] Whisper generation on pattern detection
- [ ] State transitions
- [ ] Tests with mock crystal stream

**Files**:
```
impl/claude/services/muse/
├── flux.py             # MuseFlux
└── _tests/
    └── test_flux.py
```

**Tests**: 15+

### P4.3: Cross-Jewel Events

**Goal**: Wire to SynergyBus for other jewels.

- [ ] `WitnessCrystalEmitted` event
- [ ] `WitnessMarkerCreated` event
- [ ] `MuseWhisperCreated` event
- [ ] `MuseWhisperDismissed` event
- [ ] `MuseArcChanged` event
- [ ] Brain integration: `brain.capture_from_witness()`
- [ ] Gardener integration: Season hints from tension

**Files**:
```
impl/claude/services/witness/
├── synergy.py          # Witness SynergyBus events
└── _tests/
    └── test_synergy.py

impl/claude/services/muse/
├── synergy.py          # Muse SynergyBus events
└── _tests/
    └── test_synergy.py
```

**Tests**: 15+

---

## Phase 5: Projections (Week 6)

### P5.1: CLI Projection

**Goal**: Terminal visualizations for both jewels.

- [ ] Witness CLI:
  - Timeline view with heat indicators
  - Territory view with 🔥/●/○ legend
  - Crystal list with summaries
  - Quick marker command
- [ ] Muse CLI:
  - Story arc ASCII visualization
  - Tension meter
  - Whisper overlay
- [ ] Integration with existing CLI handlers

**Files**:
```
impl/claude/protocols/cli/handlers/
├── witness.py          # Witness CLI handlers
└── muse.py             # Muse CLI handlers
```

**Tests**: 15+

### P5.2: Web Projection

**Goal**: React components for both jewels.

**Witness Components**:
- [ ] `WitnessChamber.tsx` — Main container
- [ ] `Timeline.tsx` — Event timeline with heat
- [ ] `TerritoryMap.tsx` — Codebase topology
- [ ] `CrystalViewer.tsx` — Crystal inspection
- [ ] `MarkerInput.tsx` — Quick marker creation
- [ ] `useWitness.ts` hook

**Muse Components**:
- [ ] `MuseDashboard.tsx` — Main container
- [ ] `StoryArc.tsx` — Arc visualization
- [ ] `WhisperToast.tsx` — Floating suggestion
- [ ] `TensionMeter.tsx` — Current tension
- [ ] `EncouragementCard.tsx` — Earned encouragement
- [ ] `useMuse.ts` hook

**Files**:
```
impl/claude/services/witness/web/
├── index.ts
├── WitnessChamber.tsx
├── Timeline.tsx
├── TerritoryMap.tsx
├── CrystalViewer.tsx
├── MarkerInput.tsx
└── hooks/
    └── useWitness.ts

impl/claude/services/muse/web/
├── index.ts
├── MuseDashboard.tsx
├── StoryArc.tsx
├── WhisperToast.tsx
├── TensionMeter.tsx
├── EncouragementCard.tsx
└── hooks/
    └── useMuse.ts
```

**Tests**: 20+ (component + hook tests)

---

## Success Criteria

### Test Coverage

| Component | Target | Minimum |
|-----------|--------|---------|
| Witness Polynomial | 20 | 15 |
| Witness Crystal | 25 | 20 |
| Witness Sheaf | 20 | 15 |
| Witness Node | 25 | 20 |
| Witness Flux | 25 | 20 |
| Muse Polynomial | 20 | 15 |
| Muse Arc | 30 | 25 |
| Muse Whisper | 30 | 25 |
| Muse Node | 25 | 20 |
| Muse Flux | 20 | 15 |
| **Total** | **240** | **190** |

### AGENTESE Paths

| Path | Registered | Contracts |
|------|------------|-----------|
| `time.witness.manifest` | ✓ | ✓ |
| `time.witness.attune` | ✓ | ✓ |
| `time.witness.mark` | ✓ | ✓ |
| `time.witness.crystallize` | ✓ | ✓ |
| `time.witness.timeline` | ✓ | ✓ |
| `time.witness.crystal` | ✓ | ✓ |
| `time.witness.territory` | ✓ | ✓ |
| `self.muse.manifest` | ✓ | ✓ |
| `self.muse.arc` | ✓ | ✓ |
| `self.muse.tension` | ✓ | ✓ |
| `self.muse.whisper` | ✓ | ✓ |
| `self.muse.encourage` | ✓ | ✓ |
| `self.muse.reframe` | ✓ | ✓ |
| `self.muse.summon` | ✓ | ✓ |

### Integration Checkpoints

- [ ] kgentsd starts both fluxes automatically
- [ ] Witness captures events without explicit invocation
- [ ] Crystals persist to D-gent
- [ ] Muse receives crystals from Witness
- [ ] Whispers appear when patterns detected
- [ ] Dismissal cooldown works (4h)
- [ ] Cross-jewel events flow via SynergyBus
- [ ] CLI projections render correctly
- [ ] Web components work in main app

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| kgentsd not ready | High | Can test with mock event sources |
| LLM latency in narrative | Medium | Async synthesis, don't block capture |
| Too many whispers | Medium | Strict relevance threshold (0.7+) |
| Crystal size unbounded | Medium | Force crystallize at 100 events |
| Phase detection inaccurate | Low | Conservative confidence thresholds |

---

## Anti-Sausage Check

Before implementation:

- [ ] Preserved opinionated stances from brainstorm?
  - "Whispers, not shouts" — law enforced
  - "Earned encouragement" — structural law
  - "Passive by default" — fundamental architecture
- [ ] Used Kent's voice anchors?
  - *"Daring, bold, creative, opinionated but not gaudy"* — two jewels, not seven
  - *"Tasteful > feature-complete"* — deep integration over many features
- [ ] Still daring/bold/creative?
  - Experience Crystallization is novel
  - Story Arc detection is creative
  - Passive observation is daring for UX
- [ ] Wired to existing infrastructure?
  - PolyAgent, Operad, Sheaf stack: ✓
  - D-gent for persistence: ✓
  - K-gent for LLM: ✓
  - FluxAgent for streaming: ✓
  - SynergyBus for events: ✓

---

## Related Plans

- `plans/kgentsd-event-architecture.md` — Event sources for Witness
- `plans/kgentsd-crown-jewel.md` — kgentsd as 8th Crown Jewel
- `plans/crown-jewels-enlightened.md` — Master Crown Jewel plan

---

*"Two from Seven. Depth over Breadth."*

*Created: 2025-12-19 | Source: brainstorming/2025-12-19-the-witness-and-the-muse.md*
