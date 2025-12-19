# AGENTESE Node Overhaul Strategy

> *Multi-session plan to bring all 24+ AGENTESE nodes to production parity*
> *"Tasteful > feature-complete; Joy-inducing > merely functional"*

---

## Executive Summary

**Audit Date**: 2025-12-19
**Last Updated**: 2025-12-19 (Session 6 Complete)

### Current State (Post-Audit)

| Category | Count | Production-Ready | Needs Work |
|----------|-------|------------------|------------|
| **Core Service Nodes** | 9 | 9 (100%) | 0 |
| **Context Resolvers** | 15 | 12 (80%) | 3 |
| **Frontend Projections** | 24 paths | 14 (58%) | 10 |

### Session Progress

| Session | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| **Session 1** | Quick Wins | **COMPLETE** | +4 projections, Morpheus contracts, gallery docs |
| **Session 2** | Gardener Wiring | **COMPLETE** | useGardenQuery hooks, garden contracts, real data wiring |
| **Session 3** | Soul Wiring | **COMPLETE** | KgentSoul→SoulNode DI, 10 contracts, SoulPage, eigenvector viz |
| **Phase 4** | Missing Projections | **COMPLETE** | DesignSystemProjection + EmergenceProjection (registry wired) |
| **Phase 5** | Park Scenarios | **COMPLETE** | ScenarioService wiring, 9 aspects, consent debt (hosts can say no) |
| **Session 6** | SSE Chat Streaming | **COMPLETE** | AsyncIterator streaming, useChatStream hook, StreamChunk contracts |
| **Session 7** | Neutral Error UX | **COMPLETE** | Neutral titles, ErrorCategory enum, deprecate FriendlyError/EmpathyError |
| **Session 8** | Observer Audit | **COMPLETE** | ObserverDebugPanel, `_get_affordances_for_archetype` for all key nodes, test_observer_dependence.py |
| Session 9 | CI Contract Gates | **NEXT** | Contract coverage in CI |
| Session 10 | E2E + Performance | Pending | E2E tests, performance baselines |

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

### Phase 3: Soul Wiring (Session 3) ✅ COMPLETE

> *"K-gent = Governance Functor, not chatbot"*

**Completed**:
- [x] Wire `KgentSoul` to `SoulNode` via DI (`set_soul()` pattern)
- [x] Implement `soul.dialogue()` calls in SoulNode aspects
- [x] Add eigenvector-influenced responses
- [x] Create `SoulProjection.tsx` with eigenvector visualization

See Session 3 Deliverables above for details.

---

### Phase 4: Missing Projections ✅ COMPLETE

> *"Every path gets a home, not just a JSON dump."*

**Completed**:
- [x] DesignSystemProjection for `concept.design.*`
- [x] EmergenceProjection for `world.emergence.*`
- [x] SoulProjection for `self.soul`
- [x] All projections registered in `registry.tsx`

---

### Phase 5: Park Scenarios ✅ COMPLETE

> *"Westworld where hosts can say no."*

**Completed**:
- [x] ScenarioService with templates, sessions, phases
- [x] Consent debt mechanics (debt > 0.7 blocks injection)
- [x] 9 scenario aspects in ParkNode
- [x] 14 contract types

See Session Notes in NOW.md for details.

---

### Session 6: SSE Chat Streaming (COMPLETE)

> *"SSE is a priority. Support arbitrary node paths."*

**Kent's Decisions** (2025-12-19):
- SSE streaming is HIGH priority
- Support ANY `node_path`, not just curated list
- Errors should be NEUTRAL, not sympathetic

**Deliverables**:

#### 6A: Backend Streaming ✅
- [x] `ChatNode._stream_message()` now returns `AsyncIterator[dict[str, Any]]`
- [x] Gateway detects `hasattr(result, "__aiter__")` and wraps in SSE via `_generate_sse()`
- [x] Endpoint: `GET /agentese/self/chat/stream/stream` for SSE

**Key Implementation**:
```python
async def _stream_message(self, observer, **kwargs) -> AsyncIterator[dict[str, Any]]:
    session = self._get_or_create_session(...)
    async for token in session.stream(message):
        yield {
            "content": token,
            "session_id": session.session_id,
            "turn_number": turn_number,
            "is_complete": False,
        }
    yield {"is_complete": True, "full_response": full_response, ...}
```

#### 6B: Contract Types ✅
Added to `services/chat/contracts.py`:
- `StreamMessageRequest` — Request to stream a message
- `StreamChunk` — Single chunk in streaming response
- `StreamCompleteResponse` — Final message with metrics

#### 6C: Frontend Streaming Hook ✅
Created `web/src/hooks/useChatStream.ts`:
```typescript
export function useChatStream(options: UseChatStreamOptions = {}): UseChatStreamResult {
  // Returns: { send, chunks, fullResponse, isStreaming, error, sessionId, turnNumber, stop, clear }
}

export function useChatStreamPost(...) // Alternative for complex request bodies
```

**Exit Criteria**:
- [x] `self.chat:stream` returns real SSE events (via `ChatSession.stream()` → `ChatMorpheusComposer.compose_stream()`)
- [x] Works with any `node_path` (self.soul, world.town.citizen.*, etc.)
- [x] Frontend hook ready (`useChatStream`) with full state management
- [ ] ChatPage shows streaming tokens (UI wiring pending - Session 7)
- [ ] DialogueModal shows streaming tokens (UI wiring pending)

---

### Session 7: Neutral Error UX ✅ COMPLETE

> *"More neutral for errors."*

**Kent's Decision**: Drop sympathetic error language. Be clear and actionable.

**Deliverables**:

#### 7A: Error Constants
- [x] Created `ErrorCategory` enum in `constants/messages.ts`
- [x] Neutral `ERROR_TITLES` (e.g., "Connection Failed" not "Lost in the Ether")
- [x] Actionable `ERROR_HINTS` (e.g., "Check network connection")

#### 7B: Canonical Component
- [x] `ProjectionError.tsx` updated with neutral messaging
- [x] Uses `ErrorCategory` for classification
- [x] Exports `classifyError()` for reuse

#### 7C: Terminal
- [x] Renamed `_sympatheticError()` → `_formatError()`
- [x] Updated all error messages to neutral format
- [x] Added consent (451) and rate limit (429) handlers

#### 7D: Deprecated Components
- [x] `FriendlyError.tsx` — marked deprecated, uses neutral messaging
- [x] `EmpathyError.tsx` — marked deprecated, uses neutral messaging
- [x] Both now use `ERROR_TITLES`/`ERROR_HINTS` from messages.ts

#### 7E: Updated Pages
- [x] `NotFound.tsx` — "Page Not Found" (not "Lost in the Wilderness")
- [x] `ErrorBoundary.tsx` — neutral "Component Error" title, Lucide icon

**Files Modified**:
```
impl/claude/web/src/constants/messages.ts         # ErrorCategory, neutral titles/hints
impl/claude/web/src/shell/projections/ProjectionError.tsx  # Canonical, classifyError
impl/claude/web/src/shell/TerminalService.ts      # _formatError (renamed)
impl/claude/web/src/pages/NotFound.tsx            # Neutral title
impl/claude/web/src/components/error/FriendlyError.tsx     # Deprecated
impl/claude/web/src/components/joy/EmpathyError.tsx        # Deprecated
impl/claude/web/src/components/error/ErrorBoundary.tsx     # Neutral fallback
```

**Verification**: TypeScript typecheck PASS, ESLint 0 errors (5 warnings in pre-existing code)

---

### Session 8: Observer Consistency Audit ✅ COMPLETE

> *"Observer gradations: Observer (minimal) → Umwelt (full)"*

**Deliverables**:

#### 8A: ObserverDebugPanel
- [x] Created `web/src/components/dev/ObserverDebugPanel.tsx`
- [x] Shows current archetype and capabilities
- [x] Displays affordances available per node
- [x] Toggle with Ctrl+Shift+O (dev mode only)
- [x] Added to App.tsx

#### 8B: Node Observer Dependence
- [x] `self.soul` — eigenvector/governance access varies by archetype
- [x] `world.park` — force mechanics restricted to operators
- [x] `world.park.scenario` — start/phase limited to operators
- [x] `world.park.mask` — guests have no mask access
- [x] `world.park.force` — only operators can use force
- [x] `concept.gardener` — polynomial visibility varies
- [x] `world.forge` — spectator/artisan/curator/developer gradations
- [x] `self.memory` — cartography/crystal access varies

#### 8C: Test Coverage
- [x] Created `protocols/agentese/_tests/test_observer_dependence.py`
- [x] 33 tests covering all key nodes
- [x] Property-based tests with Hypothesis
- [x] Edge case tests (invalid archetypes, case sensitivity)
- [x] Privilege gradation tests

#### 8D: Documentation
- [x] All `_get_affordances_for_archetype` methods include "Phase 8 Observer Consistency" docstrings
- [x] Observer gradation principle documented in each node

**Files Created**:
```
impl/claude/web/src/components/dev/ObserverDebugPanel.tsx
impl/claude/web/src/components/dev/index.ts
impl/claude/protocols/agentese/_tests/test_observer_dependence.py
```

**Files Modified**:
```
impl/claude/web/src/App.tsx — Added ObserverDebugPanel
impl/claude/protocols/agentese/contexts/self_soul.py — Observer gradations
impl/claude/protocols/agentese/contexts/world_park.py — ParkNode, ScenarioNode, MaskNode, ForceNode
impl/claude/protocols/agentese/contexts/gardener.py — Role-based affordances
impl/claude/services/forge/node.py — Standard archetype mappings
impl/claude/services/brain/node.py — Guest/newcomer/developer gradations
```

**Verification**: 33 backend tests PASS, TypeScript typecheck PASS

---

### Session 9: CI Contract Gates

> *"Tests must pass before commit"*

**Tasks**:
- [ ] Create `test_all_nodes_have_contracts.py`:
  - Every `@node` decorator must have `contracts={}`
  - Every aspect must have Response or Contract entry
- [ ] Create `test_projection_coverage.py`:
  - High-value nodes (Brain, Gardener, Gestalt, Forge, Town, Park) have projections
- [ ] Create `test_contract_types_importable.py`:
  - All Response types can be imported
  - No dangling references
- [ ] Add to CI pipeline (fail build if contract missing)

**Estimated Effort**: 3-4 hours

---

### Session 10: E2E + Performance

> *"Performance baselines as assertions"*

**Tasks**:
- [ ] Create `test_e2e_agentese_flow.py`:
  ```python
  async def test_brain_e2e():
      # HTTP → Gateway → BrainNode → Response
      response = await client.get("/agentese/self/memory/manifest")
      assert response.status_code == 200
      assert "crystals" in response.json()["result"]
  ```
- [ ] Add streaming E2E tests:
  ```python
  async def test_chat_streaming_e2e():
      async with client.stream("/agentese/self/chat/stream", ...) as response:
          chunks = [chunk async for chunk in response.aiter_text()]
          assert len(chunks) > 1
  ```
- [ ] Performance baselines:
  ```python
  def test_manifest_performance():
      start = time.time()
      client.get("/agentese/self/memory/manifest")
      assert time.time() - start < 0.2  # 200ms
  ```
- [ ] Playwright tests for critical flows (optional)

**Estimated Effort**: 6-8 hours

---

## Node-by-Node Status (Updated 2025-12-19)

### Core Service Nodes

| Node | Path | Status | Gap | Phase |
|------|------|--------|-----|-------|
| **Brain** | `self.memory` | 100% | — | Done |
| **Chat** | `self.chat` | 100% | — | Done (Session 6) |
| **Morpheus** | `world.morpheus` | 100% | — | Done (Session 1) |
| **Gestalt** | `world.codebase` | 100% | — | Done |
| **Town** | `world.town` | 95% | DialogueModal UI wiring | Session 7 |
| **Forge** | `world.forge` | 90% | SSE for artisan progress | Session 8 |
| **Park** | `world.park` | 100% | — | Done (Phase 5) |
| **Soul** | `self.soul` | 100% | — | Done (Session 3) |
| **Gardener** | `concept.gardener` + `self.garden` | 100% | — | Done (Session 2) |

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

## Session 6 Quick Start

When starting Session 6, run these to orient:

```bash
# Backend streaming infrastructure
grep -l "stream_with_envelope" impl/claude/protocols/projection/streaming/

# Chat session (where streaming needs to happen)
code impl/claude/services/chat/session.py

# Gateway (where SSE endpoint goes)
code impl/claude/protocols/agentese/gateway.py

# Frontend streaming hook
code impl/claude/web/src/hooks/useAgentesePath.ts
```

**First task**: Make `ChatSession.stream()` yield real tokens instead of calling K-gent synchronously.

---

*Created: 2025-12-19*
*Sessions 1-6 + Phase 4-5 Complete: 2025-12-19*
*Estimated Remaining: 4 sessions (~20-25 hours)*
*Next: Session 7 — Neutral Error UX*
*Priority: Medium — Polish before shipping*
