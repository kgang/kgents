# NOW.md — What's Happening

> *Updated each session. No metadata. Just truth.*
> *Claude reads this first, updates it before ending.*

---

## Current Work

**🔥 METAPHYSICAL FORGE** — NEW. Transforming Atelier from spectator fishbowl to developer's forge. The Forge is where Kent builds metaphysical fullstack agents using categorical artisans. Spec: `spec/protocols/metaphysical-forge.md`. This is the **multi-year strategic direction**.

**Core Vision**: Seven artisans (K-gent, Architect, Smith, Herald, Projector, Sentinel, Witness) that help Kent commission, design, implement, expose, project, secure, and test new agents. Every artifact traverses all Crown Jewels.

**2D Renaissance Phase 3** — COMPLETE. Gestalt2D fully implemented with Living Earth aesthetic. 4 new components (~800 lines), 28 passing tests. Spec: `spec/protocols/2d-renaissance.md`.

**Town Frontend** — 60% done. Backend is solid (1559 tests: Sheaf, Events, AGENTESE nodes). Frontend components exist: TownOverview, CitizenBrowser, CoalitionGraph. Mesa (2D) is the visualization now.

**Coalition/Park** — Waiting on Town patterns. Once Town's consent model is proven, the others will follow fast.

**Brain & Gardener** — Production-ready. 100% complete. Could ship now. (3D canvases mothballed, 2D placeholders active)

**Gestalt** — 85%. Full Gestalt2D with layer cards, violation feed, module detail. Living Earth aesthetic applied.

---

## What I'm Stuck On

**Voice dilution** — The project is losing its edge through LLM processing. Each Claude session smooths a little. Added Anti-Sausage Protocol to CLAUDE.md to address this.

**26 plan files were bureaucracy** — Killed them. This file replaces all of them.

---

## What I Want Next

**Metaphysical Forge Phase 1**: Strip Atelier → Establish Forge identity. Remove spectator economy, demo messaging, token gates. Rename to Forge. Create minimal ForgeVisualization.tsx. K-gent integration comes next.

*"The Forge is where we build ourselves."*

---

## Crown Jewel Status (Quick Reference)

| Jewel | % | One-liner |
|-------|---|-----------|
| Brain | 100 | Spatial cathedral of memory. Ship-ready. |
| Gardener | 100 | Cultivation practice. Ship-ready. |
| Gestalt | 85 | Living garden where code breathes. Gestalt2D COMPLETE. |
| **Forge** | 0 | **NEW**. Developer's workshop for metaphysical fullstack agents. |
| Town/Coalition | 55 | Workshop where agents collaborate visibly. |
| Park | 40 | Westworld where hosts can say no. |
| Domain | 0 | Enterprise. Dormant. |

**Note**: Atelier (100%) → Forge (0%) is intentional. We're rebuilding from first principles.

---

## Session Notes

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

*Last: 2025-12-18 night (Metaphysical Forge spec created)*
