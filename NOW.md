# NOW.md — What's Happening

> *Updated each session. No metadata. Just truth.*
> *Claude reads this first, updates it before ending.*

---

## Current Work

**Town Frontend** — 60% done. Backend is solid (1559 tests: Sheaf, Events, AGENTESE nodes). Frontend components exist: TownOverview, CitizenBrowser, CoalitionGraph. Need polish and the 3D canvas.

**Coalition/Atelier/Park** — All waiting on Town patterns. Once Town's consent model is proven, the others will follow fast.

**Brain & Gardener** — Production-ready. 100% complete. Could ship now.

**Gestalt** — 70%. Elastic UI works. Needs WebGL depth.

---

## What I'm Stuck On

**Voice dilution** — The project is losing its edge through LLM processing. Each Claude session smooths a little. Added Anti-Sausage Protocol to CLAUDE.md to address this.

**26 plan files were bureaucracy** — Killed them. This file replaces all of them.

---

## What I Want Next

Something **daring**. The Coalition visualization should feel like watching emergence happen—agents forming alliances in real-time, visible tension, consent as a first-class citizen.

*"Daring, bold, creative, opinionated but not gaudy"* — this is the bar.

---

## Crown Jewel Status (Quick Reference)

| Jewel | % | One-liner |
|-------|---|-----------|
| Brain | 100 | Spatial cathedral of memory. Ship-ready. |
| Gardener | 100 | Cultivation practice. Ship-ready. |
| Gestalt | 70 | Living garden where code breathes. |
| Atelier | 90 | Fishbowl where spectators collaborate. BidQueue done. |
| Town/Coalition | 55 | Workshop where agents collaborate visibly. |
| Park | 40 | Westworld where hosts can say no. |
| Domain | 0 | Enterprise. Dormant. |

---

## Session Notes

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

Next: Phase 2 — TRACED_OPERAD extension (deferred to future session)

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

*Last: 2025-12-18 late night*
