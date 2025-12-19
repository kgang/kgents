# AGENTESE Node Overhaul Strategy

> *Multi-session plan to bring all 24+ AGENTESE nodes to production parity*
> *"Tasteful > feature-complete; Joy-inducing > merely functional"*

---

## Executive Summary

**Audit Date**: 2025-12-19
**Last Updated**: 2025-12-19 (Phase 4 Complete)

### Current State (Post-Audit)

| Category | Count | Production-Ready | Needs Work |
|----------|-------|------------------|------------|
| **Core Service Nodes** | 9 | 8 (89%) | 1 |
| **Context Resolvers** | 15 | 12 (80%) | 3 |
| **Frontend Projections** | 24 paths | 13 (54%) | 11 |

### Session Progress

| Session | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| **Session 1** | Quick Wins | **COMPLETE** | +4 projections, Morpheus contracts, gallery docs |
| **Session 2** | Gardener Wiring | **COMPLETE** | useGardenQuery hooks, garden contracts, real data wiring |
| **Session 3** | Soul Wiring | **COMPLETE** | KgentSoul→SoulNode DI, 10 contracts, SoulPage, eigenvector viz |
| **Phase 4** | Missing Projections | **COMPLETE** | DesignSystemProjection + EmergenceProjection (registry wired) |
| **Phase 5** | Park Scenarios | **COMPLETE** | ScenarioService wiring, 9 aspects, consent debt (hosts can say no) |
| Session 6 | Unified Chat | Pending | Chat engine for all jewels, SSE streaming |
| Session 7-8 | Consistency Polish | Pending | Error UX, observer consistency |
| Session 9-10 | DevEx & Testing | Pending | CI gates, E2E tests |

---

## Session 3 Deliverables (COMPLETE)

### 3A: Key Discovery - Soul Wiring Gap

**Critical insight**: The `KgentSoul` is created in bootstrap but **never wired** to `SoulNode`:

```python
# bootstrap.py creates KgentSoul
if name == "kgent_soul":
    return KgentSoul(auto_llm=True)

# BUT providers.py never wires it to SoulNode._soul
# Result: SoulNode._soul is always None
# All soul aspects return "Soul not initialized"
```

**Wiring pattern** (from DifferanceStore precedent):
```python
# In setup_providers(), after services are bootstrapped:
soul = await get_service("kgent_soul")
set_soul(soul)  # Wires to singleton SoulNode
```

### 3B: Files Created

```
impl/claude/protocols/agentese/contexts/soul_contracts.py   # Contract types (10 contracts)
impl/claude/web/src/pages/Soul.tsx                          # Soul page with eigenvector viz
```

### 3C: Files Modified

```
impl/claude/services/providers.py                             # Added soul wiring (lines 342-352)
impl/claude/protocols/agentese/contexts/self_soul.py          # Added contracts + singleton helpers
impl/claude/web/src/shell/projections/registry.tsx            # SoulProjection registered
```

### 3D: Contract Types Added

10 contracts now registered on `self.soul`:
- `manifest` → `Response(SoulManifestResponse)`
- `eigenvectors` → `Response(EigenvectorsResponse)`
- `starters` → `Contract(StartersRequest, StartersResponse)`
- `mode` → `Contract(ModeRequest, ModeResponse)`
- `dialogue` → `Contract(DialogueRequest, DialogueResponse)`
- `challenge` → `Contract(ChallengeRequest, ChallengeResponse)`
- `reflect` → `Contract(ReflectRequest, ReflectResponse)`
- `why` → `Contract(WhyRequest, WhyResponse)`
- `tension` → `Contract(TensionRequest, TensionResponse)`
- `governance` → `Contract(GovernanceRequest, GovernanceResponse)`

### 3E: End-to-End Verified

```python
# Test output (KGENTS_NO_AUTO_LLM=1):
>>> node.invoke('manifest', observer)
BasicRendering(metadata={'mode': 'reflect', 'has_llm': False,
  'eigenvectors': {'aesthetic': 0.15, 'categorical': 0.92, ...}})

>>> node.invoke('dialogue', observer, message='What pattern am I seeing?')
{'response': "You've expressed before that you value: joy in creation...",
 'mode': 'reflect', 'tokens_used': 44, 'was_template': False, 'budget_tier': 'dialogue'}
```

### 3F: Learnings

1. **Singleton pattern**: `get_soul_node()` + `set_soul()` follows DifferanceStore precedent
2. **@aspect decorator**: Methods prefixed with `_` (e.g., `_dialogue`) are exposed by aspect name (`dialogue`)
3. **Contracts in decorator**: `@node(contracts={...})` requires importing all types from contracts module
4. **Frontend hooks**: Use `useAgentese` not `useAgentesePath`, and mutation returns `{ mutate, isLoading }` not `{ mutateAsync, isPending }`

---

## Session 2 Deliverables (COMPLETE)

### 2A: Key Discovery - Two Node Families

**Critical insight**: The Gardener2D visualization needs TWO AGENTESE node families:

| Node Family | Purpose | Data Shape |
|-------------|---------|------------|
| `concept.gardener.*` | **Session orchestration** (SENSE→ACT→REFLECT) | `ConceptGardenerSessionManifestResponse` |
| `self.garden.*` | **Garden state** (plots, seasons, gestures) | `GardenJSON` (from `project_garden_to_json()`) |

The mock data in Gardener.tsx was calling the wrong node! It needed `self.garden.manifest` (rich garden state), not `concept.gardener.manifest` (session status).

### 2B: Files Created

```
impl/claude/web/src/hooks/useGardenQuery.ts    # ~380 lines - hooks for self.garden.*
impl/claude/protocols/gardener_logos/contracts.py  # ~230 lines - type contracts
```

### 2C: Files Modified

```
impl/claude/web/src/hooks/index.ts             # Added garden hook exports
impl/claude/web/src/pages/Gardener.tsx         # Replaced mock data with real hooks
```

### 2D: Architecture Clarified

**Two-hook pattern for Gardener page**:
- `useGardenManifest()` → Full garden state (plots, seasons, metrics, gestures)
- `useGardenerSession()` → Session polynomial state (phase, intent, counts)

**Graceful fallback**: When API unavailable, shows `DEFAULT_GARDEN` and `DEFAULT_SESSION` with friendly error state.

### 2E: Tests Verified
- TypeScript typecheck: PASS
- ESLint: 0 errors (2 warnings - acceptable)
- Backend gardener_logos tests: 203 passed
- AGENTESE node tests: 36 passed

---

## Session 1 Deliverables (COMPLETE)

### 1A: Context Resolver Audit

**Finding: Architecture is 95% clean**. No true duplicates—intentional separation of concerns.

| Pair | Distinction | Action |
|------|-------------|--------|
| `world.gallery` vs `world.emergence.gallery` | Practical API vs Educational showcase | **DOCUMENTED** |
| `world.codebase` vs `world.gestalt.live` | Code analysis vs Infrastructure | Keep separate |
| `gardener.py` vs `garden.py` | Orchestrator vs State manager | Complementary |
| `world.workshop` vs `world.forge` | Event-driven builder vs Creative artisans | Different domains |

### 1B: Contract Coverage Audit

**Two architectural patterns identified:**

1. **Service Node Pattern** (8 services): Uses `@node()` with `contracts={}`
2. **Context Node Pattern** (Design, Emergence, Forest): Uses `@aspect` decorators

| Service | Path | Contracts | Status |
|---------|------|-----------|--------|
| Brain | `self.memory` | 9 aspects | COMPLIANT |
| Chat | `self.chat` | 11 aspects | GOLD STANDARD |
| Gestalt | `world.codebase` | 6 aspects | COMPLIANT |
| Park | `world.park` | 13 aspects | COMPLIANT |
| Town | `world.town` | 8 aspects | COMPLIANT |
| Forge | `world.forge` | 19 aspects | COMPLIANT |
| **Morpheus** | `world.morpheus` | 8 aspects | **FIXED** (Session 1) |
| Flow | `self.flow` | Incomplete | Needs work |

### 1C: Gardener Mock Data Audit

**Current State**: 3 mock functions (~200 lines) in Gardener.tsx

| Mock Function | Lines | Replacement Hook | Status |
|---------------|-------|------------------|--------|
| `createMockGarden()` | 27-153 | `useGardenerManifest()` | Pending |
| `createMockSession()` | 155-169 | `useGardenerSession()` | Pending |
| `createMockSuggestion()` | 172-193 | `useGardenerPropose()` | Pending |

**Blockers**:
- Backend types incomplete (`ConceptGardenerManifestResponse` has `unknown` fields)
- Missing mutation hooks for `tend`, `transition.accept`, `transition.dismiss`
- Type mismatch: `GardenJSON` ≠ API response structure

**Estimated Effort**: 10-14 hours

### 1D: Frontend Projection Coverage

**Coverage: 13/24 paths** (54%) have dedicated projections.

| Category | Paths | Status |
|----------|-------|--------|
| **Covered** | 13 | Brain, Chat, Gardener, Forge, Differance, Gestalt, Town (6 sub-paths), Park, Cockpit |
| **Newly Registered** | 4 | Garden, Gallery, Workshop, self.differance |
| **Using ConceptHome** | 7 | concept.design.*, world.emergence.*, self.forest, self.kgent, self.soul, self.system, time.branch |

---

## Session 1 Changes Made

### Files Created
```
impl/claude/services/morpheus/contracts.py  # 8 contract types for Morpheus
```

### Files Modified
```
impl/claude/web/src/shell/projections/registry.tsx
  - Added GardenProjection (self.garden.*)
  - Added GalleryProjection (world.gallery.*)
  - Added WorkshopProjection (world.workshop.*)
  - Added self.differance.* → DifferanceProjection

impl/claude/services/morpheus/node.py
  - Added contracts={} with 8 aspects
  - Imports from new contracts.py

impl/claude/protocols/agentese/contexts/world_gallery.py
  - Added distinction box documenting world.gallery vs world.emergence.gallery

impl/claude/protocols/agentese/contexts/world_gallery_api.py
  - Added matching distinction box
```

### Tests Verified
- Frontend typecheck: PASS
- Morpheus tests: 56 passed
- AGENTESE registry tests: 26 passed

---

## Remaining Phases

### Phase 2: Gardener Wiring (Session 2) ✅ COMPLETE

> *"The persona is a garden, not a museum."*

**Goal**: Replace all mock data in Gardener.tsx with real AGENTESE hooks.

**Tasks** (All Complete):
- [x] Replace `createMockGarden()` with `useGardenManifest()` (NEW: uses self.garden.* not concept.gardener.*)
- [x] Replace `createMockSession()` with `useGardenerSession()`
- [x] Replace `createMockSuggestion()` with `useGardenSuggest()` + `toTransitionSuggestion()`
- [x] Add loading/error states with graceful fallbacks
- [x] Test end-to-end: page → hook → API → backend → response

**Key Learnings**:
- Two node families needed: `self.garden.*` (state) + `concept.gardener.*` (session)
- Created new `useGardenQuery.ts` with hooks for self.garden.* endpoints
- Created `protocols/gardener_logos/contracts.py` for type safety
- Graceful fallback pattern: `DEFAULT_GARDEN` / `DEFAULT_SESSION` when API unavailable

---

### Phase 3: LLM Integration (Session 3-4)

> *"K-gent = Governance Functor, not chatbot"*

#### 3A: K-gent Soul Wiring

**Current State**:
- `self.soul` has `@chatty` decorator but K-gent Soul rarely invoked
- Frontend shows `KENT_EIGENVECTORS` fallback when Soul unavailable
- Town dialogue uses separate `DialogueService` with LLM

**Tasks**:
- [ ] Wire `KgentSoul` to `SoulNode` via DI
- [ ] Implement `soul.dialogue()` calls in SoulNode aspects
- [ ] Add eigenvector-influenced responses (aesthetic, categorical, gratitude)
- [ ] Create fallback chain: LLM → cached response → template

#### 3B: Unified Chat Protocol

**Tasks**:
- [ ] Make `self.chat` the chat engine for all jewels
- [ ] Town dialogue: `self.chat.create(node_path="world.town.citizen.{id}")`
- [ ] Soul dialogue: `self.chat.create(node_path="self.soul")`
- [ ] Standardize streaming: SSE for all chat endpoints

---

### Phase 4: Missing Projections (Session 5-6)

> *"Every path gets a home, not just a JSON dump."*

**Paths Needing Dedicated Projections**:

| Path | Current | Needed | Priority |
|------|---------|--------|----------|
| `concept.design.*` (5 paths) | ConceptHome | DesignSystemProjection | Medium |
| `world.emergence.*` (2 paths) | ConceptHome | EmergenceProjection | Medium |
| `self.forest` | ConceptHome | ForestProjection | Low |
| `self.kgent` | ConceptHome | KgentProjection | Low |
| `self.soul` | ConceptHome | SoulProjection | Medium |
| `time.branch` | ConceptHome | BranchProjection | Low |

**Tasks**:
- [ ] Create DesignSystemProjection for concept.design.* hierarchy
- [ ] Create EmergenceProjection for world.emergence.* (Cymatics design)
- [ ] Create SoulProjection for K-gent dialogue interface
- [ ] Register all new projections in registry.tsx

---

### Phase 5: Park Scenarios (Session 7)

> *"Westworld where hosts can say no."*

**Tasks**:
- [ ] Design `Scenario` dataclass with beats, hosts, locations
- [ ] Implement scenario state machine (OBSERVING → BUILDING_TENSION → INJECTING → COOLDOWN)
- [ ] Add consent mechanics (hosts can refuse beats, debt > 0.7 blocks injection)
- [ ] Wire Park hosts to `self.chat` protocol
- [ ] Create `ScenarioProjection.tsx` with beat visualization

---

### Phase 6: Consistency Polish (Session 8-9)

> *"Daring, bold, creative, opinionated but not gaudy"*

**Tasks**:
- [ ] Audit all endpoint responses for envelope consistency
- [ ] Create `ProjectionError.tsx` with actionable hints
- [ ] Add error categorization (network, not_found, validation, server)
- [ ] Audit all nodes for observer-dependent behavior
- [ ] Create `ObserverDebugPanel` for development

---

### Phase 7: DevEx & Testing (Session 10)

> *"Depth over breadth"*

**Tasks**:
- [ ] Add contract validation to CI (all service nodes must have contracts)
- [ ] Add projection coverage check (high-value nodes have projections)
- [ ] Create `test_e2e_agentese_flow.py` covering HTTP → Node → Response
- [ ] Add streaming tests (SSE, WebSocket)
- [ ] Performance baselines for manifest endpoints

---

## Node-by-Node Status (Updated)

### Core Service Nodes

| Node | Path | Status | Gap | Phase |
|------|------|--------|-----|-------|
| **Brain** | `self.memory` | 100% | — | Done |
| **Chat** | `self.chat` | 100% | — | Done |
| **Morpheus** | `world.morpheus` | 100% | — | **Done (Session 1)** |
| **Gestalt** | `world.codebase` | 100% | — | Done |
| **Town** | `world.town` | 90% | Unify chat | Phase 3 |
| **Forge** | `world.forge` | 85% | SSE streaming | Phase 6 |
| **Park** | `world.park` | 80% | Scenarios placeholder | Phase 5 |
| **Soul** | `self.soul` | 60% | LLM not wired | Phase 3 |
| **Gardener** | `concept.gardener` + `self.garden` | 95% | Real hooks wired | **Done (Session 2)** |

### Context Resolvers (Clarified)

| Resolver | Path | Purpose | Status |
|----------|------|---------|--------|
| `self_soul.py` | `self.soul` | K-gent personality, dialogue modes | OK |
| `self_kgent.py` | `self.kgent` | Session-based conversation (1:many) | OK (distinct) |
| `gardener.py` | `concept.gardener` | N-Phase orchestrator | OK |
| `garden.py` | `self.garden` | Garden lifecycle state | OK (complementary) |
| `world_gallery.py` | `world.emergence.gallery` | Educational categorical showcase | **DOCUMENTED** |
| `world_gallery_api.py` | `world.gallery` | Practical projection API | **DOCUMENTED** |
| `world_gestalt_live.py` | `world.gestalt.live` | Infrastructure topology | OK (distinct) |
| `world_workshop.py` | `world.workshop` | Event-driven Flux builder | OK |
| `design.py` | `concept.design.*` | Design Language System | Needs contracts |
| `world_emergence.py` | `world.emergence` | Cymatics design experience | Needs contracts |
| `forest.py` | `self.forest` | Forest Protocol state | OK |
| `time_differance.py` | `time.differance` | Temporal traces | OK |

---

## Anti-Sausage Checkpoints

At the end of each session, verify:

- [ ] **Mirror Test**: Does the change feel like Kent on his best day?
- [ ] **Opinionated Stances**: Did we preserve any controversial choices?
- [ ] **Rough Edges**: Did we smooth something that should stay rough?
- [ ] **Kent's Words**: Are we using his actual vocabulary?

**Voice Anchors**:
- *"Daring, bold, creative, opinionated but not gaudy"* — When making UX choices
- *"Tasteful > feature-complete"* — When scoping work
- *"The persona is a garden, not a museum"* — When discussing node evolution

---

## Files to Reference

**Backend**:
- `impl/claude/protocols/agentese/registry.py` — Node registration
- `impl/claude/protocols/agentese/gateway.py` — HTTP gateway
- `impl/claude/services/*/node.py` — Service nodes
- `impl/claude/services/morpheus/contracts.py` — Contract pattern example

**Frontend**:
- `impl/claude/web/src/shell/projections/registry.tsx` — Projection mapping
- `impl/claude/web/src/hooks/useGardenerQuery.ts` — Hook pattern example
- `impl/claude/web/src/pages/Gardener.tsx` — Mock data to replace

**Skills**:
- `docs/skills/agentese-node-registration.md` — @node patterns
- `docs/skills/crown-jewel-patterns.md` — Service patterns
- `docs/skills/metaphysical-fullstack.md` — Architecture

---

*Created: 2025-12-19*
*Session 1 Complete: 2025-12-19*
*Estimated Remaining: 9 sessions (~27-36 hours)*
*Priority: High — Foundational for all future Crown Jewel work*
