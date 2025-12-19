# NOW.md — What's Happening

> *Updated each session. No metadata. Just truth.*
> *Claude reads this first, updates it before ending.*

---

## Current Work

**🔍 AGENTESE NODE OVERHAUL** — Sessions 1-6 + Phases 4-5 COMPLETE. See `plans/agentese-node-overhaul-strategy.md`.

| Session | Status | Key Deliverables |
|---------|--------|------------------|
| Session 1 | ✅ | 4 projections, Morpheus contracts, gallery docs |
| Session 2 | ✅ | Gardener wiring — `useGardenQuery` hooks, real data |
| Session 3 | ✅ | Soul wiring — KgentSoul→SoulNode DI, 10 contracts |
| Phase 4 | ✅ | DesignSystemProjection + EmergenceProjection |
| Phase 5 | ✅ | Park Scenarios — consent debt (hosts can say no) |
| Session 6 | ✅ | SSE Chat Streaming — AsyncIterator, useChatStream, StreamChunk contracts |
| **Session 7** | **NEXT** | **Neutral Error UX** — consistent errors, actionable hints |
| Sessions 8-10 | Pending | Observer audit, CI gates, E2E tests |

**Session 6 Delivered** (2025-12-19):
- `ChatNode._stream_message()` returns `AsyncIterator[dict]` → Gateway wraps in SSE
- `useChatStream` hook for frontend token-by-token streaming
- `StreamChunk`, `StreamMessageRequest`, `StreamCompleteResponse` contracts
- Works with ANY `node_path` (self.soul, world.town.citizen.*, etc.)

**Session 7 Focus** (Kent's decisions 2025-12-19):
- **Neutral errors** — Drop sympathetic language, be clear and actionable
- **Wire streaming to UI** — ChatPage + DialogueModal show streaming tokens

**Session 2 Key Discovery**: Gardener2D needs TWO node families:
- `self.garden.*` → Garden STATE (plots, seasons, gestures) via `useGardenManifest()`
- `concept.gardener.*` → Session POLYNOMIAL (SENSE→ACT→REFLECT) via `useGardenerSession()`

**🚀 AGENTESE-AS-ROUTE** — COMPLETE. *"The URL IS the API call."* Unified routing and AGENTESE into a single grammar. Spec: `spec/protocols/agentese-as-route.md`. Implementation complete.

**🔥 METAPHYSICAL FORGE** — Transforming Atelier from spectator fishbowl to developer's forge. The Forge is where Kent builds metaphysical fullstack agents using categorical artisans. Spec: `spec/protocols/metaphysical-forge.md`. This is the **multi-year strategic direction**.

**Core Vision**: Seven artisans (K-gent, Architect, Smith, Herald, Projector, Sentinel, Witness) that help Kent commission, design, implement, expose, project, secure, and test new agents. Every artifact traverses all Crown Jewels.

**Phase 4 COMPLETE (2025-12-18)**: All four creative artisans do REAL work:
- **Architect**: LLM-powered categorical design generation (PolyAgent specs)
- **Smith**: Code generation (service modules to `_generated/`)
- **Herald**: AGENTESE node generation (`@node` decorator, contracts, routing)
- **Projector**: React component generation (visualization + hooks)

---

### 🎉 2D RENAISSANCE — COMPLETE

> *"3D was spectacle. 2D is truth. And truth breathes."*

**All five phases delivered 2025-12-18.** Spec archived: `spec/protocols/2d-renaissance.md`

| Deliverable | Lines | Tests |
|-------------|-------|-------|
| Gardener2D (7 components) | 1,485 | 30 |
| Gestalt2D (4 components) | 1,084 | 28 |
| Brain2D (4 components) | ~1,000 | 13 |
| Town Dialogue (2 components) | ~710 | 20 |
| **TOTAL** | **~4,300** | **91** |

**Replaced**: 2,447 lines of Three.js. **Gained**: Living Earth aesthetic, mobile-first, real AGENTESE, LLM dialogue.

---

**Town Frontend** — 70% done. Backend is solid. Frontend has TownOverview, CitizenBrowser, CoalitionGraph, Mesa (2D), and now **DialogueModal** for citizen conversations.

**Coalition/Park** — Waiting on Town patterns. Once Town's consent model is proven, the others will follow fast.

**Brain** — 100% complete with Brain2D! CrystalTree, CaptureForm, GhostSurface. Ship-ready.

**Gardener** — 100% complete. Gardener2D with season orb, plot tiles, tending palette. **Now wired to real AGENTESE hooks** (self.garden.* + concept.gardener.*). Ship-ready.

**Gestalt** — 100%. Full Gestalt2D with layer cards, violation feed. Ship-ready.

**Design System** — 100%. DesignSystemProjection exposes `concept.design.*` (3 operads + unified). Live law verification.

**Emergence** — 100%. EmergenceProjection exposes `world.emergence.*` (Cymatics Design Sampler). 9 pattern families, qualia space, circadian modulation.

---

## What I'm Stuck On

**Voice dilution** — The project is losing its edge through LLM processing. Each Claude session smooths a little. Added Anti-Sausage Protocol to CLAUDE.md to address this.

**26 plan files were bureaucracy** — Killed them. This file replaces all of them.

---

## What I Want Next

**Metaphysical Forge Phase 5**: Sentinel (security review) and Witness (test generation) artisans. Plus SSE streaming for real-time progress and cross-jewel wiring (Brain capture, Gardener plots).

*"The Forge is where we build ourselves."*

---

## Crown Jewel Status (Quick Reference)

| Jewel | % | One-liner |
|-------|---|-----------|
| Brain | 100 | Spatial cathedral of memory. Ship-ready. |
| Gardener | 100 | Cultivation practice. Ship-ready. |
| Gestalt | 85 | Living garden where code breathes. Gestalt2D COMPLETE. |
| **Forge** | 85 | Phase 1-4 ✅. Four creative artisans = REAL work. |
| Town/Coalition | 70 | Workshop where agents collaborate visibly. Dialogue COMPLETE. |
| **Park** | 60 | Westworld where hosts can say no. **Scenarios + Consent Debt COMPLETE.** |
| Domain | 0 | Enterprise. Dormant. |

**Forge Assessment (2025-12-18)**: Phase 4 COMPLETE. All four creative artisans (Architect, Smith, Herald, Projector) now do real work. **165 backend tests**. Next: Phase 5 (Sentinel, Witness) + SSE streaming + cross-jewel wiring.

---

## Session Notes

### 2025-12-19 — AGENTESE Node Overhaul Phase 5 (Park Scenarios)

Executed **Phase 5** of `plans/agentese-node-overhaul-strategy.md` — *"Westworld where hosts can say no."*

**ScenarioService → ParkNode Wiring**:
- Added `scenario_service` dependency to ParkNode
- Registered in `bootstrap.py` via `get_service("scenario_service")`
- 6 new scenario aspects: `scenario.{list,get,start,tick,end,sessions}`

**Consent Debt Mechanics** (the differentiator):
- Added to `ScenarioSession`: `incur_debt()`, `can_inject_beat()`, `apologize()`
- **Debt > 0.7 blocks beat injection** — hosts genuinely refuse
- 3 new consent aspects: `consent.{debt,incur,apologize}`
- Verified behavior:
  ```
  debt=0.0 → can_inject=True
  debt=0.8 → can_inject=False (host refuses!)
  apologize → debt=0.6, can_inject=True (amends made)
  ```

**Contract Types Added** (14 new):
- `ScenarioSummary`, `ScenarioDetail`, `ScenarioSessionDetail`, `SessionProgress`
- `ScenarioListResponse`, `ScenarioGetRequest/Response`, `ScenarioStartRequest/Response`
- `ScenarioTickRequest/Response`, `ScenarioEndRequest/Response`, `ScenarioSessionListResponse`
- `ConsentDebtRequest`, `ConsentDebtResponse`

**Files Modified**:
```
agents/park/scenario.py           # +75 lines: consent debt methods
services/park/contracts.py        # +120 lines: 14 contract types
services/park/node.py             # +150 lines: 9 new aspects
services/park/scenario_service.py # +120 lines: consent debt service methods
services/bootstrap.py             # +5 lines: scenario_service registration
```

**Tests Passing**: 37 service + 88 agent + 40 director = **165 Park tests**

**Remaining** (Future Sessions):
1. Chat protocol bridge — Wire `self.chat` for SSE streaming host dialogue
2. ScenarioProjection.tsx — Beat timeline, consent meters, phase visualization

*"The hosts have a voice. When debt exceeds 0.7, they say no."*

---

### 2025-12-19 — AGENTESE Node Overhaul Phase 4 (Missing Projections)

Executed **Phase 4** of `plans/agentese-node-overhaul-strategy.md` — *"Every path gets a home, not just a JSON dump."*

**DesignSystemProjection** (`pages/DesignSystem.tsx`, ~400 lines):
- Exposes `concept.design.*` — the three orthogonal design functors
- UI = Layout[D] ∘ Content[D] ∘ Motion[M]
- **Operad selector**: Layout, Content, Motion, Unified — each shows operations and laws
- **Live law verification**: Click "Verify Laws" → shows passed/structural/failed with messages
- Uses `useAgentese` and `useAgenteseMutation` for path invocation

**EmergenceProjection** (`pages/Emergence.tsx`, ~500 lines):
- Exposes `world.emergence.*` — the Cymatics Design Experience
- *"Don't tune blindly. Show everything. Let the eye choose."*
- **Pattern families**: 9 families (chladni, interference, mandala, flow, reaction, spiral, voronoi, moire, fractal)
- **Qualia space**: 7 cross-modal aesthetic coordinates (warmth, weight, tempo, texture, brightness, saturation, complexity)
- **Circadian badge**: Dawn/Noon/Dusk/Midnight with modifier display
- Pattern cards with selection and parameter details

**Registry** (`shell/projections/registry.tsx`):
- Added `DesignSystemProjection` for `concept.design.*` paths
- Added `EmergenceProjection` for `world.emergence.*` paths
- Type registry: LayoutOperadManifest, ContentOperadManifest, MotionOperadManifest, DesignOperadManifest, EmergenceManifest, EmergenceQualia, EmergenceCircadian

**Build Status**: TypeScript clean, ESLint clean (new files), backend mypy clean.

**Phase 4 Complete**. Remaining phases: LLM integration (Soul projection), Park scenarios, polish.

*"The URL IS the thought. The page IS the answer."*

---

### 2025-12-19 — AGENTESE REPL Renaissance COMPLETE

Completed the **REPL Renaissance** plan — making the AGENTESE Terminal actually work.

**The Problem**: Terminal had correct design but broken execution. Paths weren't always registered, errors were swallowed, completion showed paths that didn't work.

**The Solution**: All 5 phases delivered:

| Phase | What |
|-------|------|
| 1. Audit & Fix | `scripts/audit_agentese_paths.py` — 39/39 paths pass (100%) |
| 2. Error Surfacing | `_sympatheticError()` with 5 categories (network, 404, 500, 422, timeout) |
| 3. Completion Overhaul | Live discovery with metadata, 30s cache TTL |
| 4. Testing Harness | `test_registry_ci_gate.py` — 7 CI tests for path verification |
| 5. Examples & Teaching | Welcome message with working paths, inline examples in `help` |

**New Files**:
- `protocols/agentese/_tests/test_registry_ci_gate.py` — CI gate prevents broken paths from shipping

**Files Modified**:
- `web/src/shell/Terminal.tsx` — Rich welcome message with working commands
- `web/src/shell/TerminalService.ts` — `_getPathMetadata()` + `_formatExampleCommand()` for inline examples

**The REPL Now**:
- ✅ Shows working paths on first open
- ✅ Tab completion only shows paths that exist
- ✅ Errors explain what went wrong with remediation hints
- ✅ `help <path>` shows examples when available
- ✅ CI gate prevents future breakage

*"The REPL is the garden's conversation partner. Now it speaks."*

---

### 2025-12-19 — AGENTESE-as-Route Final Wiring

Completed the **final integration step**: wired `UniversalProjection` into `App.tsx`.

**What Changed**:
- **App.tsx** (from 100 → 90 lines): Replaced 25+ explicit routes with UniversalProjection catch-all
- **registry.tsx**: Registered `CockpitProjection` for `/self.cockpit` path
- **plans/agentese-as-route.md**: Updated phase checklist to reflect completion

**Architecture Now**:
```tsx
<Route element={<Shell />}>
  <Route path="/town/simulation/:townId" element={<Town />} />  {/* Explicit (param) */}
  <Route path="/gallery/*" element={<Gallery />} />             {/* Explicit (dev) */}
  <Route path="/*" element={<UniversalProjection />} />         {/* AGENTESE catch-all */}
</Route>
```

**Legacy redirects** (in UniversalProjection): `/brain` → `/self.memory`, `/town` → `/world.town`, etc.

**Status**: Phases 1-4 ✅ COMPLETE. Phase 5 (Polish) 90% complete.

*"The URL IS the thought. The page IS the answer."*

---

### 2025-12-18 — AGENTESE-as-Route Protocol

Implemented the radical URL unification: **The URL IS the AGENTESE path.**

**Spec** (`spec/protocols/agentese-as-route.md`):
- URL grammar: `/{context}.{entity}.{sub}...[:aspect][?params]`
- Examples: `/world.town.citizen.kent_001`, `/self.memory:capture`, `/time.differance?limit=20`
- Reserved prefixes: `/_/` for system routes
- Five synergies: Contract-First Types, Metaphysical Fullstack, Différance, Teaching Mode, Elastic UI

**Implementation** (`impl/claude/web/src/`):
- **parseAgentesePath.ts** (180 lines): URL → AGENTESE path parsing with validation
- **useAgentesePath.ts** (340 lines): `useAgentese`, `useAgenteseMutation`, `useAgenteseStream` hooks
- **shell/projections/** (6 files, ~1,200 lines):
  - `UniversalProjection.tsx`: Catches all AGENTESE paths, invokes, projects
  - `registry.tsx`: Response type → Component mapping (by type or path pattern)
  - `GenericProjection.tsx`: JSON fallback with collapsible viewer
  - `ProjectionLoading.tsx`, `ProjectionError.tsx`: State components
- **AgentLink.tsx**: AGENTESE-aware `<Link>` replacement

**Tests**: 31 passing tests for path parsing

**Key Insight**: *"The URL IS the thought. The page IS the answer."* — Define a node, get a URL. No glue required. Navigation becomes pure AGENTESE discovery.

**Migration Strategy**: Dual-mode (legacy redirects + universal catch-all). Existing pages work unchanged.

---

### 2025-12-18 — Metaphysical Forge Phase 4 (Herald & Projector Artisans)

Implemented **real artisans** for AGENTESE node and React component generation:

**Backend** (`services/forge/artisans/`):
- **HeraldArtisan** (350 lines): Generates AGENTESE nodes from designs
  - `@node` decorator with contracts dict and aspect routing
  - `contracts_ext.py` with Request/Response types per operation
  - Path derivation: `CounterAgent` → `world.counter`
  - LLM mode + template fallback
- **ProjectorArtisan** (400 lines): Generates React components from designs
  - `{Name}Visualization.tsx` with elastic UI patterns
  - `use{Name}Query.ts` with AGENTESE hooks (useAsyncState pattern)
  - `index.ts` barrel export
  - Files written to `_generated/{commission_id}/web/`

**Commission Integration** (`commission.py`):
- `advance()` now calls **real artisans** for EXPOSING and PROJECTING stages
- Herald output (`registered_path`) flows to Projector input
- Error handling: graceful failure if upstream output missing

**Tests**: 51 new tests (Herald: 19, Projector: 24, Integration: 8). Total Forge: **165 tests** (all passing).

**Key Implementation Decisions**:
1. **Herald generates complete node.py**: Not a stub—immediately importable
2. **Projector generates complete .tsx**: Density-aware, Living Earth aesthetic
3. **Template fallback pattern**: Same as Smith/Architect—LLM when available, templates always work
4. **Sentinel/Witness remain placeholders**: Phase 5 work

**Generated Artifacts** (from a single commission):
```
services/forge/_generated/commission-{id}/
├── __init__.py        # Smith
├── polynomial.py      # Smith
├── service.py         # Smith
├── node.py            # Herald ← NEW
├── contracts_ext.py   # Herald ← NEW
└── web/               # Projector ← NEW
    ├── index.ts
    ├── {Name}Visualization.tsx
    └── use{Name}Query.ts
```

**Exit Criteria** (from spec):
- ✅ Commissioned agent works via CLI (node.py importable)
- ✅ Commissioned agent works via HTTP (AGENTESE path registered)
- ⏳ Commissioned agent works via Web UI (files generated, manual testing needed)

*"The Herald makes the agent speakable. The Projector gives it form."*

---

### 2025-12-18 night — Metaphysical Forge Phase 3 (Architect & Smith Artisans)

Implemented **real artisans** that do actual LLM-powered work:

**Backend** (`services/forge/artisans/`):
- **ArchitectArtisan** (320 lines): Generates categorical designs (PolyAgent specs) via K-gent `soul.dialogue()`
  - JSON structured output: name, states, transitions, operations, laws
  - Validation for design consistency
  - Graceful fallback to stub design when K-gent unavailable
- **SmithArtisan** (460 lines): Generates Python service code from designs
  - Template-based code generation: `__init__.py`, `polynomial.py`, `service.py`
  - Writes files to `services/forge/_generated/<commission_id>/`
  - LLM enhancement when K-gent available, pure templates otherwise
- **AgentDesign** dataclass: Structured design with validation

**Commission Integration** (`commission.py`):
- `advance()` now calls **real artisans** for DESIGNING and IMPLEMENTING stages
- Architect output flows to Smith input
- `artifact_path` populated with generated code location
- Herald, Projector, Sentinel, Witness remain placeholders (Phase 4-5)

**Contracts** (`contracts.py`):
- `AgentDesignResponse`: Architect output schema
- `SmithOutputResponse`: Smith output schema

**Tests**: 35 new tests for artisans. Total Forge: **114 tests** (all passing).

**Key Implementation Decisions**:
1. **Real LLM via K-gent**: Uses `soul.dialogue()` with BudgetTier.DIALOGUE
2. **Graceful degradation**: Stub/template mode when K-gent unavailable
3. **Validated designs**: AgentDesign.validate() catches inconsistencies
4. **Generated code compiles**: Templates produce syntactically valid Python

**What Remains** (Phase 4-5):
- Herald: AGENTESE node generation
- Projector: React component generation
- Sentinel: Security review
- Witness: Test generation

*"The Architect sees the shape. The Smith forges it into reality."*

---

### 2025-12-18 evening — Differance DevEx Phases 7D-7E (Session Recording & Export)

Completed the **Differance DevEx Enlightenment** plan with final two phases:

**Phase 7D: Session Recording** (`RecordingControls.tsx`, 420 lines):
- One-click session recording with customizable names
- Pause/resume/stop controls with Living Earth aesthetic
- Decision markers with timestamps (flag important moments)
- Auto-stop on 5 minutes idle
- Real-time stats: traces, ghosts, duration
- `useSessionRecording` hook for state management
- Breathe animation on recording indicator

**Phase 7E: Export & Share** (`ExportPanel.tsx`, 540 lines):
- JSON export (machine-readable, for replay)
- Markdown export (human-readable documentation)
- ADR export (Architecture Decision Record format)
- Shareable "why?" snapshots (one-click copy)
- Session and trace export support
- Mobile-friendly collapsible panel
- Tip about ADR format for institutional knowledge

**Differance.tsx Integration**:
- RecordingControls in header area
- ExportPanel beside search bar (desktop) / below content (mobile)
- Wired to `useSessionRecording` hook with correlation IDs

**Design Principles Applied**:
- "Zero-Config Recording": Traces auto-record, sessions are opt-in enhancement
- "Generative, Not Archival": Export answers "what should I do next?"
- Living Earth aesthetic throughout

**Status**: Differance DevEx COMPLETE (all 5 phases delivered).

*"The Différance Engine is where kgents becomes conscious of its own cognition."*

---

### 2025-12-19 morning — Metaphysical Forge Phase 2.5 (Commission Workflow)

Implemented the **Commission Workflow** — the core innovation of the Forge:

**Backend** (`services/forge/`):
- **commission.py** (400 lines): `Commission` dataclass, `CommissionService` with 9 methods, `CommissionStatus` enum (11 states), `ArtisanType` enum (7 artisans)
- **commission_node.py** (300 lines): `CommissionNode` AGENTESE node with contracts for create/get/start/advance/pause/resume/cancel
- **contracts.py** (+150 lines): 14 new contract types for commission workflow
- **State Machine**: `PENDING → DESIGNING → IMPLEMENTING → EXPOSING → PROJECTING → SECURING → VERIFYING → REVIEWING → COMPLETE`

**Frontend** (`web/src/`):
- **useForgeQuery.ts** (+400 lines): 8 new hooks (`useCommissions`, `useCreateCommission`, `useStartCommission`, `useAdvanceCommission`, `usePauseCommission`, `useResumeCommission`, `useCancelCommission`, `useCommission`)
- **CommissionPanel.tsx** (420 lines): Intent form + commission list + artisan progress view + intervention controls

**Tests**: 23 new tests for commission (all passing). Total Forge: **79 tests**.

**Key Implementation Decisions**:
1. **Graceful degradation**: Commission auto-approves when K-gent unavailable
2. **Additive outputs**: Each artisan adds to `artisan_outputs` dict, nothing replaces
3. **Intervention tracking**: pause/resume/cancel recorded in `interventions` list
4. **Fire-and-forget pattern**: Commission creation → auto-start in single flow

**Spec Updated**: Added "Appendix C: Implementation Progress" to `spec/protocols/metaphysical-forge.md` with patterns discovered.

**What Remains**:
1. Architect artisan (actual LLM design generation)
2. SSE streaming for real-time progress
3. Cross-jewel wiring (Brain capture, Gardener plots)

*"The commission is the intent. The artisans are the hands. The artifact is the agent."*

### 2025-12-18 night — 2D Renaissance Phase 5 (Town Dialogue)
Implemented **Phase 5** of the 2D Renaissance spec — citizen dialogue frontend:

**Components Created** (4 files, ~710 lines):
- **townApi dialogue methods** (`client.ts`): `converse()`, `turn()`, `getHistory()` via AGENTESE
- **useCitizenDialogue.ts** (190 lines): Hook managing conversation lifecycle
- **DialogueModal.tsx** (490 lines): Chat UI with Living Earth aesthetic
- **CitizenPanel enhancement**: "Start Conversation" button

**Living Earth Aesthetic**: Bark surfaces, archetype-colored borders, sage focus, amber loading.

**Tests**: 20 passing (10 hook, 10 component)

**What Remains** (Future Sessions):
1. SSE streaming for LLM responses
2. Park consent integration
3. Event feed wiring to TownTracePanel
4. Full memory grounding (M-gent foveation)

*"Citizens should feel alive through dialogue."*

### 2025-12-18 late — Différance Crown Jewel Wiring (Phase 6A-C)
Executed **Phase 6A-C** of `plans/differance-crown-jewel-wiring.md`:

**Phase 6A — Test Infrastructure + Buffer Isolation**:
- **ContextVar-based buffer isolation** (`create_isolated_buffer()`, `reset_isolated_buffer()`)
- pytest-xdist safe: each test gets isolated buffer, no cross-test pollution
- **Correlation ID** support (`get_correlation_id()`, `set_correlation_id()`)
- conftest fixture auto-applies isolation for all differance tests

**Phase 6B — Brain Wiring**:
- `BrainPersistence` now has `DifferanceIntegration("brain")`
- `capture()` → trace with alternatives (auto_tag, defer_embedding)
- `surface()` → trace with alternatives (different_seed, context_weighted)
- `delete()` → trace with alternatives (archive_instead, soft_delete)
- **Read operations (search, get, list) → NO traces** (high frequency, read-only)
- Fire-and-forget pattern: `loop.create_task()` ensures zero latency impact

**Phase 6C — Gardener Wiring**:
- `GardenerPersistence` now has `DifferanceIntegration("gardener")`
- `start_session()` → trace with alternatives (resume_previous)
- `end_session()` → trace with alternatives (extend)
- `plant_idea()` → trace with alternatives (different_lifecycle, auto_connect)
- `nurture_idea()` → trace with alternatives (prune, water)
- `harvest_idea()` → trace with alternatives (stay, compost)
- `create_plot()` → trace with alternatives (use_existing)

**Static Alternatives Registry** (`agents/differance/alternatives.py`):
- Tier 1 static alternatives for Brain, Gardener, Town, Atelier
- `get_alternatives(jewel, operation)` returns pre-defined alternatives
- Zero-cost: no computation at trace time

**Test Count**: 158 differance tests passing

**Key Design Decisions** (per plan):
1. Fire-and-forget: traces don't slow down operations
2. Graceful degradation: no event loop → skip trace (don't crash)
3. Read-heavy immunity: search/get/list are NOT traced
4. Static alternatives: Tier 1 (constant) vs Tier 2 (computed) separation

**Next**: Phase 6D — UI Integration (Ghost Badge + Why Panel for Cockpit)

*"Every Brain capture and Gardener gesture now leaves a ghost trail."*

### 2025-12-18 late — Developer Cockpit (Anti-Sausage Portal)
**Kent's daily entry point** — Replaced Crown (Hero Path) with developer-focused Cockpit:

**Created**:
- `pages/Cockpit.tsx` (~500 lines) — Main cockpit page
- `components/cockpit/VoiceAnchor.tsx` — Rotating voice anchors with breathing
- `constants/voiceAnchors.ts` — Kent's quotes from _focus.md

**Features**:
- Voice anchor rotating display with click-to-rotate
- Session Start Ritual checklist (persists in sessionStorage)
- Crown Jewel status cards with ghost count badges
- Quick Launch breathing buttons
- Recent Traces placeholder (awaiting Différance wiring)
- Anti-Sausage Check end-of-session checklist

**Deleted**: `pages/Crown.tsx` (user-facing Hero Path — replaced entirely per Kent's choice)

**Key Quote**: *"The cockpit is where Kent meets himself at the start of each day."*

**Synergy**: Integrates with `plans/differance-crown-jewel-wiring.md` Phase 6D — Recent Traces will show heritage when wired.

### 2025-12-18 late — Différance Engine Phase 5 Complete (FRUITING)
Implemented **Phase 5** of the Différance Engine (Crown Jewel integration infrastructure):

**Contracts** (`agents/differance/contracts.py`):
- 26 contract dataclasses for AGENTESE BE→FE type sync
- Covers: Heritage, Why, Ghosts, At, Replay, Branch operations
- Following Pattern 13 (Contract-First Types)

**Integration** (`agents/differance/integration.py`):
- **DifferanceIntegration** class for Crown Jewels to record traces
- `record_trace()` (async) and `record_trace_sync()` (sync via Pattern 6)
- **TraceContext** for nested trace scoping
- Buffer-only mode for testing without persistence

**React Hooks** (`useDifferanceQuery.ts`):
- 13 hooks: `useHeritageDAG`, `useWhyExplain`, `useGhosts`, `useTraceAt`, etc.
- Follows useAsyncState pattern consistent with all Crown Jewels

**React Component** (`GhostHeritageGraph.tsx`):
- 2D Renaissance aesthetic (Living Earth palette)
- Shows chosen path (solid) vs ghosts (dashed)
- Responsive with density modes, interactive node selection

**Test Count**: 192 tests passing (all phases)

**Exit Criteria**: ✅ Contracts + hooks + component ready. Infrastructure complete.

**Next**: `plans/differance-crown-jewel-wiring.md` — Actually wire traces into Brain/Gardener operations.

*"The ghost heritage graph is the UI innovation: seeing what almost was alongside what is."*

### 2025-12-18 night — Metaphysical Forge Specification
**Strategic Transformation**: Atelier → Metaphysical Forge

Created `spec/protocols/metaphysical-forge.md` — the multi-year vision for Kent's developer workshop:

**The Core Insight**: Atelier was a fishbowl (spectators watch builders). The Forge inverts this: Kent commissions artisans to build metaphysical fullstack agents.

**Seven Artisans** (one per layer + cross-cutting):
1. **K-gent**: Soul/Governance — Kent's personality stand-in, taste-maker
2. **Architect**: Categorical design — PolyAgent, Operad, Sheaf specifications
3. **Smith**: Implementation — Service modules, business logic
4. **Herald**: Protocol — AGENTESE nodes, contracts, aspects
5. **Projector**: Surfaces — CLI, Web, marimo projections
6. **Sentinel**: Security — Vulnerability review, hardening
7. **Witness**: Testing — T-gent taxonomy tests, verification

**Cross-Jewel Integration**: Every artifact captures to Brain, creates Garden plot, verifies via Gestalt, coordinates via Coalition, broadcasts to Town.

**Implementation Phases** (24 weeks):
- Phase 1: Strip Atelier → Forge identity
- Phase 2: K-gent integration
- Phase 3-4: Architect + Smith
- Phase 5-6: Herald + Projector
- Phase 7-8: Sentinel + Witness
- Phase 9-10: Cross-jewel wiring
- Phase 11-12: Golden path polish

**Visual Language**: Minimalist first. Living Earth applied sparingly. Leave room for iteration.

**Key Quote**: *"The Forge is where we build ourselves."*

### 2025-12-18 late — 2D Renaissance Phase 3 (Gestalt2D)
Executed **Phase 3** of the 2D Renaissance spec — full Gestalt2D implementation:

**Components Created** (4 files, 1084 lines total):
- **Gestalt2D.tsx** (359 lines): Main container with ElasticSplit, mobile-first layout, Living Earth palette
- **LayerCard.tsx** (246 lines): Health-colored expandable layer panels with module badges, breathing animation when healthy
- **ViolationFeed.tsx** (197 lines): Streaming violation alerts with severity badges, source→target visualization
- **ModuleDetail.tsx** (282 lines): Module detail side panel with health metrics (coupling, cohesion, instability)

**Key Design Decisions**:
- **Layer-centric view**: Modules grouped by layer (protocols, services, agents) instead of 3D scatter
- **Health-first**: Color indicates health grade immediately (sage=A, amber=B, copper=C, bronze=D/F)
- **Violations prominent**: Not hidden in edges—live feed of architecture violations
- **Module selection**: Side panel replaces FilterPanel when module selected

**Tests**: 28 passing tests covering LayerCard, ViolationFeed, ModuleDetail, Gestalt2D integration

**Gestalt Page** updated to use Gestalt2D (replaced 167-line placeholder with real visualization)

**Key Insight**: *"1060 lines of 3D spectacle → 800 lines of 2D truth."* — The visualization now tells you what you need to know without rotating a camera. Layer cards breathe when healthy, violations scream when not.

### 2025-12-18 late — 2D Renaissance Phase 2 (Gardener2D)
Executed **Phase 2** of the 2D Renaissance spec — full Gardener2D implementation:

**Components Created** (7 files, 1485 lines total):
- **Gardener2D.tsx**: Main container with ElasticSplit, mobile-first layout
- **SeasonOrb.tsx**: Breathing season indicator with Living Earth palette
- **PlotTile.tsx**: Organic plot cards with vine-style progress bars
- **GestureStream.tsx**: Live gesture feed with tone visualization
- **SessionPolynomial.tsx**: Inline SENSE→ACT→REFLECT state machine
- **TendingPalette.tsx**: Tending actions with mobile FloatingActions
- **TransitionSuggester.tsx**: Auto-Inducer banner with dismiss memory

**Living Earth Aesthetic** applied throughout:
- Warm earth tones (Soil, Bark, Wood, Clay, Sand)
- Living greens (Moss, Fern, Sage, Mint, Sprout)
- Ghibli glow accents (Lantern, Honey, Amber, Copper, Bronze)
- Breathing animations on active elements
- Vine-style progress bars with organic growth gradient

**Tests**: 30 passing tests covering all sub-components

**Gardener Page** updated to use unified Gardener2D (replaced separate Garden + Session visualizations).

**Key Insight**: *"The session cycle lives INSIDE the garden, not separate."* — Garden metaphor and polynomial state machine are now one organic experience.

### 2025-12-18 late — 2D Renaissance Phase 1 (Mothball)
Executed **Phase 1** of the 2D Renaissance spec (`spec/protocols/2d-renaissance.md`):

**Mothballed** (moved to `_mothballed/three-visualizers/`):
- `gestalt/GestaltVisualization.tsx` (1060 lines), `OrganicNode.tsx`, `VineEdge.tsx`, `AnimatedEdge.tsx`
- `brain/BrainCanvas.tsx` (1004 lines), `OrganicCrystal.tsx`, `CrystalVine.tsx`, `BrainTopology.tsx`
- `town/TownCanvas3D.tsx` (383 lines)

**2D Placeholders** created for:
- `pages/Gestalt.tsx` — Shows real topology data (modules, layers, violations) in 2D cards
- `pages/Brain.tsx` — Shows real crystal cartography (nodes grouped by category) in 2D tree

**Preserved**:
- All filter/legend/tooltip components (reusable in 2D)
- `components/three/` directory (skills + primitives for future VR/AR)
- Mesa (PixiJS 2D canvas) for Town

**Build Status**: Clean for mothball-related changes. Pre-existing type errors in tests remain (unrelated).

**Key Insight**: *"3D was spectacle. 2D is truth."* — The pages now show real data through AGENTESE, just with simpler rendering. Phase 2 (Gardener2D) is next per spec.

### 2025-12-18 afternoon — Crown Jewels Genesis Phase 2 Chunk 3
Executed **Chunk 3: Token Economy Visualization**:

**Components Created**:
- **TokenBalanceWidget.tsx**: Animated counter with particles on balance changes, flash green/red for earn/spend
- **TokenFlowIndicator.tsx**: SVG particle stream overlay for FishbowlCanvas edge, uses useFlowing hook
- **SpendHistoryPanel.tsx**: Collapsible transaction history with useUnfurling animation, relative timestamps

**AtelierVisualization Integration**:
- Token balance now visible in Atelier header (compact widget)
- Click header widget → SpendHistoryPanel expands below
- Fishbowl view now has BidQueuePanel sidebar (desktop) / below canvas (mobile)
- "Place Bid" button triggers BidSubmitModal
- TokenFlowIndicator overlay on FishbowlCanvas shows token particle animation on bids

**Tests**: 74 new tests (all passing). Total Atelier tests now **185**.

### 2025-12-18 evening — Crown Jewels Genesis Phase 2 Chunks 4-5 ✅
Executed **Chunk 4: Town Integration** and **Chunk 5: Polish & Joy**:

**Chunk 4 — Town Integration** (connects spectators to citizens):
- **WatchAsCitizenToggle.tsx**: Dropdown to select citizen persona with archetype colors (Builder→blue, Scholar→purple, Trader→amber)
- **useAtelierStream** now has `watchingAsCitizen` and `setWatchingAs` for cross-jewel identity
- **Archetype→Bid suggestions**: `getBidSuggestionsForArchetype()` returns Builder→structural, Trader→value, Scholar→conceptual
- Cursor updates include citizen eigenvector data for personality-based coloring
- 32 new integration tests for Town↔Atelier connection

**Chunk 5 — Polish & Joy**:
- **Performance**: Memoized eigenvector→color with LRU cache (MAX_CACHE_SIZE=100), React.memo on SpectatorCursorDot and BidCard
- **Accessibility**: Keyboard nav in BidQueuePanel (Arrow keys, Home/End, Enter/Delete), screen reader live region for bid status announcements
- **Focus management**: BidSubmitModal now has focus trap, focus restoration, Escape to close, body scroll lock
- **ARIA attributes**: Proper role, aria-label, aria-selected throughout bid queue and modal

**Tests**: **217 total** (32 new for Town integration). Plan marked **COMPLETE**.

**Anti-Sausage Check**: ✅ Kept eigenvector coloring meaningful (personality→hue), archetype→bid preferences are deliberately opinionated, Town↔Atelier integration creates real cross-jewel identity—not smoothed away.

**Atelier** now at **100%**. All chunks complete.

### 2025-12-18 late night — Différance Engine Phase 1 Implementation
Implemented **Phase 1** of the Différance Engine (the self-knowing system):

**Core Types** (`agents/differance/trace.py`):
- **Alternative**: A road not taken — the ghost (operation, inputs, reason_rejected, could_revisit)
- **WiringTrace**: Single recorded wiring decision (ADR-style, with causal chain)
- **TraceMonoid**: Monoid of wiring traces with ghost accumulation

**Laws Verified** (property-based tests with Hypothesis):
- Identity: `ε ⊗ T = T = T ⊗ ε`
- Associativity: `(A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)`
- Ghost Preservation: `ghosts(a ⊗ b) ⊇ ghosts(a) ∪ ghosts(b)`

**D-gent Storage** (`agents/differance/store.py`):
- **DifferanceStore**: Append-only trace persistence via D-gent
- Uses `Datum.causal_parent` for lineage tracking
- Works with any D-gent backend (Memory → JSONL → SQLite → Postgres)
- Reconstructs `TraceMonoid` from storage via `to_monoid()`

**Test Count**: 69 tests passing (29 store + 40 monoid/types)

### 2025-12-18 late night — Différance Engine Phase 2 Complete
Implemented **Phase 2** of the Différance Engine (traced operad extension):

**TRACED_OPERAD** (`agents/differance/operad.py`):
- **TracedAgent**: Wraps PolyAgent + TraceMonoid, preserves semantic behavior
- **traced_seq**: Sequential composition with trace recording
- **traced_par**: Parallel composition with trace recording
- Inherits all AGENT_OPERAD operations via Pattern 10 (Operad Inheritance)

**Laws Verified** (property-based tests with Hypothesis):
- Semantic Preservation: `traced_seq(a, b).agent.invoke(s, i) == seq(a, b).invoke(s, i)`
- Ghost Preservation: `ghosts(traced_seq(a, b)) ⊇ ghosts(a) ∪ ghosts(b)`
- Associativity: `traced_seq(traced_seq(a, b), c) ≅ traced_seq(a, traced_seq(b, c))`

**Test Count**: 107 tests passing (69 Phase 1 + 38 Phase 2)

**Exit Criteria**: ✅ Traced operations compose correctly. Semantic preservation verified.

Next: Phase 3 — GhostHeritageDAG builder (needs HeritageNode/HeritageEdge types from spec)

### 2025-12-18 night (later) — Crown Jewels Genesis Phase 2 Continuation
Executed **Chunk 1: AtelierVisualization Integration** + **Chunk 2: BidQueue Core**:

**Chunk 1** (Fishbowl Integration):
- Wired **FishbowlCanvas** into AtelierVisualization with new `fishbowl` view
- Created **SessionSelector** component for switching live sessions
- Added **spectator cursor toggle** control
- **14 integration tests** (AtelierVisualizationFishbowl.test.tsx)

**Chunk 2** (BidQueue Core):
- **BidQueuePanel.tsx**: Vertical bid queue with animations, accept/reject for creators
- **BidSubmitModal.tsx**: Modal for spectators to submit bids with token validation
- **useTokenBalance.ts**: Real-time token balance tracking hook
- **50 tests** for BidQueue components

**Test total**: 111 atelier tests passing

**Atelier** now at **90%** (up from 80%). Next: Token Economy Visualization (Chunk 3), Town Integration (Chunk 4).

### 2025-12-18 night — Différance Engine Spec
Wrote `spec/protocols/differance.md` — the Ghost Heritage Graph protocol:
- **Core insight**: Every output carries trace of what it *is* AND what it *almost was* (ghosts)
- **Traced Operad**: Extends AGENT_OPERAD with `traced_seq`, `branch_explore`, `fork_speculative`
- **TraceMonoid**: Associative composition of wiring decisions with ghost preservation
- **Ghost Heritage Graph**: UI innovation — see the roads not taken alongside chosen path
- **AGENTESE paths**: `time.trace.*`, `time.branch.*`, `self.differance.*`
- **Category theory grounded**: Traced monoidal categories + polynomial functors

This is the **"self-knowing system"** — every Crown Jewel gains trace visibility. Users can ask "why did this happen?" and navigate the full heritage graph including alternatives considered but rejected.

Next: Implementation in `impl/claude/agents/differance/`

### 2025-12-18 evening — Crown Jewels Genesis Phase 2
Executed Week 3 of Atelier Rebuild:
- **FishbowlCanvas.tsx**: Live creation stream with breathing border (LIVING_EARTH.amber glow)
- **SpectatorOverlay.tsx**: Eigenvector-based cursor colors, stale cleanup
- **Spectator contracts**: Added to services/atelier/contracts.py
- **useAtelierStream enhanced**: Session subscription, cursor updates, live events
- **35+ tests** for FishbowlCanvas and SpectatorOverlay

**Atelier** now at **80%** (up from 75%). FishbowlCanvas core complete. Next: Integration into AtelierVisualization, then Week 4 BidQueue.

### 2025-12-18 afternoon
- Diagnosed the real problem: voice dilution, not planning mechanics
- Added Anti-Sausage Protocol to CLAUDE.md (Session Start Ritual + Voice Anchors + Anti-Sausage Check)
- Killed Garden Protocol overhead (mood/momentum/trajectory were bureaucracy)
- Created NOW.md to replace 26 plan files
- Kept the useful parts: GardenPolynomial, GARDEN_OPERAD, 200 tests

---

### 2025-12-18 night — 2D Renaissance COMPLETE 🎉
Closed out the 2D Renaissance spec. All five phases delivered in a single day:
- **Phase 1**: Mothball (9 Three.js files → `_mothballed/`)
- **Phase 2**: Gardener2D (7 components, 1,485 lines, 30 tests)
- **Phase 3**: Gestalt2D (4 components, 1,084 lines, 28 tests)
- **Phase 4**: Brain2D (4 components, ~1,000 lines, 13 tests)
- **Phase 5**: Town Dialogue (DialogueModal + hook, ~710 lines, 20 tests)

**Total**: 24 new components, ~4,300 lines, 91 tests. Replaced 2,447 lines of hollow Three.js.

*"3D was spectacle. 2D is truth. And truth breathes."*

---

### 2025-12-19 — Différance DevEx Enlightenment (Phases 7A-7C)
Executed **Phase 7** of Différance DevEx (`plans/differance-devex-enlightenment.md`):

**Phase 7A — TraceTimeline** (replaces RecentTracesPanel):
- **TraceTimeline.tsx** (540 lines): Real trace data via `time.differance.recent`, jewel filtering, ghost count badges
- Horizontal timeline with vertical branching, inline WhyPanel on selection
- Living Earth aesthetic, responsive (compact mode for mobile)

**Phase 7B — TraceInspector**:
- **TraceInspector.tsx** (460 lines): Detailed trace view with operation, inputs/outputs, context
- "Why this path?" section from `time.differance.why`
- Ghost list with exploration buttons, polynomial state before/after viewer
- Actions: Replay, View Full Heritage

**Phase 7C — GhostExplorationModal**:
- **GhostExplorationModal.tsx** (370 lines): Side-by-side comparison (Chosen vs Ghost)
- Fork & Explore workflow via `time.branch.create` + `time.branch.explore`
- Hypothesis input for exploration, non-explorable ghost warning

**Differance Page Enhancement**:
- Split view: Timeline (left) + Heritage Graph (center) + Inspector (right)
- View mode toggle: Split / Full Timeline / Full Graph
- Mobile support with inline inspector
- Progressive disclosure: Badge → Timeline → Inspector → Modal → Full Graph

**Tests**: TraceTimeline.test.tsx (12 tests)

**TypeScript**: All new components compile cleanly (fixed unused imports, prop types)

**Design Principles Enforced**:
- "Ghosts Are Friends": Exploration feels like opening a gift, not a wound
- "Temporal Intuition": Time flows left-to-right, chosen solid, ghosts translucent
- "Progressive Disclosure": Each level reveals more detail
- "Generative, Not Archival": "What should I do next?" not just "What happened?"

**Remaining** (Future Sessions):
- Phase 7D: Session Recording (RecordingControls, decision markers)
- Phase 7E: Export & Share (JSON/Markdown export, shareable snapshots)

*"The Différance Engine is where kgents becomes conscious of its own cognition."*

---

### 2025-12-18 — Concept Home Protocol: Foundation + Habitat 2.0 Vision

Assessed Concept Home Protocol status and implemented foundation for **Habitat 2.0**:

**Foundation Implemented**:
- **ConceptHomeProjection.tsx** (340 lines): Universal fallback projection replacing GenericProjection
  - Three-tier model: Minimal (cultivation card), Standard (reference panel), Rich (redirect)
  - Context badges, breathing animations, warm cultivation copy
  - Receives `ProjectionContext`, extracts metadata from response
- **GeneratedPlayground enhancements**:
  - Breathing animation for loading state (Sparkles icon with rotation)
  - Micro-teaching hints after successful invocation (`ASPECT_HINTS` dictionary)
  - Educational feedback: "Manifest reveals the current state—like asking 'what are you right now?'"
- **Backend metadata wiring**: `/agentese/discover?include_metadata=true` now returns node descriptions, aspects, effects
- **Registry updated**: `ConceptHomeProjection` is now the fallback (every path has a home)

**Habitat 2.0 Vision** (3 new plans created):
- **`plans/habitat-2.0.md`**: Master vision doc with three-layer architecture (Adaptive Habitat → Live Polynomial → Ghosts)
- **`plans/ghost-integration.md`**: Priority 1 — Show alternatives after invocation (7h estimate)
- **`plans/habitat-examples.md`**: Priority 2 — Pre-seeded one-click examples in `@node` (4h estimate)
- **`plans/mini-polynomial.md`**: Priority 3 — Mini state machine diagrams in Reference Panel (6-8h estimate)

**The Insight**: *"From 'every path has a home' to 'every path is a place to think'"* — aligned with Bret Victor's explorable explanations philosophy.

**Key UX Principles Identified** (from research):
- Time-to-first-invoke optimization (Stripe-style one-click)
- Progressive disclosure (Nielsen Norman)
- Ghost integration (Différance spec: "what almost was")
- Observer-adaptive disclosure (developer/learner/operator/guest)

**Tests**: TypeScript compiles cleanly, registry tests pass, gateway imports OK.

*"The persona is a garden, not a museum. The Habitat is where agents grow visible."*

---

### 2025-12-18 — Habitat 2.0 Implementation (Complete)

**Executed all four Habitat 2.0 plans with parallel agents:**

**Priority 1: Ghost Integration** ✅
- **Backend**: `Ghost` dataclass in `node.py`, `_get_alternatives()` on BaseLogosNode (excludes introspection aspects, max 5 ghosts, category-aware)
- **Frontend**: `GhostPanel.tsx` (purple Différance theme, ghost emoji, category coloring), `ExplorationBreadcrumb.tsx` (last 5 invocations)
- **Integration**: `GeneratedPlayground.tsx` fetches ghosts after invoke, displays in panel below results
- **Tests**: 10 backend + 18 frontend tests passing

**Priority 2: Habitat Examples** ✅
- **Backend**: `NodeExample` dataclass in `registry.py`, `@node(examples=[...])` parameter, gateway includes examples in discovery
- **Frontend**: `ExamplesPanel.tsx` (emerald action theme, one-click invocation)
- **Examples Added**: BrainNode (search, recent, surface, topology), GardenerNode (propose, session.define, route), GestaltNode (health, topology, drift, scan)
- **Tests**: 6 backend + 10 frontend tests passing

**Priority 3: Mini Polynomial** ✅
- **Backend**: `PolynomialManifest` dataclass, `polynomial` aspect on ALL BaseLogosNode (default position with all aspects as directions)
- **Frontend**: `MiniPolynomial.tsx` (emerald current position, clickable directions)
- **Integration**: `ConceptHomeProjection.tsx` fetches polynomial, displays in Reference Panel
- **Tests**: 6 backend + 9 frontend tests passing

**Specs Updated** ✅
- Updated `spec/principles.md` AD-010 (Habitat Guarantee)
- Updated `HYDRATE.md` with new Habitat status
- Updated `plans/_forest.md` with current phase state

**Totals**: 37 new frontend tests, 22 new backend tests. All Habitat 2.0 priorities 1-3 complete.

**The Insight**: *"Category theory becomes tangible when you can click a transition."* Ghosts embody Différance philosophy—seeing paths not taken. Polynomial makes AD-002 visible and interactive.

*"The persona is a garden, not a museum. The Habitat is where agents grow visible."*

---

### 2025-12-19 — AD-012: Aspect Projection Protocol

**The Problem**: NavigationTree was showing aspects (`:manifest`, `:polynomial`) as clickable children, causing 405 errors and semantic confusion.

**The Insight**: *"You can GO TO a town. You can't GO TO a greeting—you DO a greeting."*

Paths are PLACES (navigable), aspects are ACTIONS (invocable). Conflating them breaks the model.

**Implementation**:
- **NavigationTree.tsx**: Removed aspects from `buildTree()` — navtree shows paths only
- **spec/protocols/agentese.md §2.5**: Added navigation vs invocation semantics
- **spec/principles.md AD-012**: Full rationale, puppet swap, anti-patterns
- **plans/aspect-projection-protocol.md**: Marked COMPLETE

**Key Diagram**:
```
NavTree (Loop Mode)          Projection (Function Mode)
"Where can I go?"            "What can I do here?"

▶ world                      ┌─────────────────────┐
  ▶ town                     │ Aspects:            │
    ○ citizen                │  [manifest] [poly]  │
    ○ coalition              │       ↑             │
▶ concept                    │  click = POST       │
  ● gardener ◄── HERE        └─────────────────────┘
```

**Connection to Principles**:
- **Heterarchical**: Paths are loop-mode, aspects are function-mode
- **Puppet Constructions**: NavTree puppet wrong for aspects; Reference Panel + Playground is right puppet

*"The river doesn't ask the clock when to flow. Aspects flow from paths when invoked, not when navigated."*

---

*Last: 2025-12-19 (AD-012: Aspect Projection Protocol)*
