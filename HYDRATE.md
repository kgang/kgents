# HYDRATE.md - kgents Session Context

Hydrate context with this file. Keep it concise—focus on current state and recent work.

## Meta-Instructions

**WHEN ADDING NEW SESSIONS**:
- Add to "Current Session" with date
- Move previous to "Recent Sessions" (keep only 3)
- Delete older sessions
- Update TL;DR with new status/commits

**AVOID**: Verbose descriptions, duplicating git info, code snippets, paragraphs (use tables/lists)
**UPDATE**: In small chunks of 2-3 lines with references to more information.
**CLEANUP**: Run when file is >1500 lines. Target: **< 700 lines total**

---

## TL;DR

**Status**: F-gent × I-gent Forge View COMPLETE ✅
**Branch**: `main`
**Latest Commit**: `6bd9b63` feat: Protocol Specs v2.0 + L-gent Vector DB

**Current State**:
- **F-gent × I-gent Forge View**: ✅ COMPLETE - Pipeline composition UI (69 tests)
- **L-gent Phase 8**: ✅ COMMITTED `6bd9b63` - D-gent Vector DB (23 tests)
- **O-gent Phase 4**: ✅ COMMITTED `dd153d3` - W-gent integration (40 tests)
- **I-gent Total**: 138 tests (Stigmergic Field + Forge View)

**Uncommitted**:
- `impl/claude/agents/i/forge_view.py` - Forge View (~700 lines)
- `impl/claude/agents/i/_tests/test_forge_view.py` - 69 tests
- `impl/claude/protocols/cli/genus/i_gent.py` - Updated with full forge cmd

**Next Steps**:
1. **Commit**: F-gent × I-gent Forge View
2. **Implement**: ALO format in F-gent

---

## CLI: "The Conscious Shell" v2.0

**Plan**: `docs/cli-integration-plan.md`

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Hollow Shell + `.kgents` context | ✅ DONE |
| 2 | Bootstrap & Laws | ✅ DONE |
| 3 | Flow Engine | ✅ DONE |
| 4 | MCP Server | ✅ DONE (42 tests) |
| 5 | Big 5 Genera (G, J, P, L, W) | ✅ DONE (50 tests) |
| 6 | Intent Layer (10 verbs) | ✅ DONE (94 tests) |
| 7 | TUI Dashboard | ✅ DONE (73 tests) |

**Key Features**: 10 Intent Verbs, Flowfiles (YAML), Sympathetic Errors, MCP Bidirectional

---

## Spec/Impl Gap Analysis

| Agent | Impl % | Key Gap |
|-------|--------|---------|
| **B-gents** | ~100% | ✅ All 6 B×G phases complete (575 tests) |
| **D-gents** | ~95% | ✅ Phase 5 SQL/Redis complete (276 tests) |
| **L-gents** | ~85% | ✅ Phase 8 D-gent Vector DB complete (23 tests) |
| **G-gents** | ~90% | Phase 7 done |
| **O-gents** | ~95% | ✅ Phase 4 complete (177 tests), W-gent integration |
| **I-gents** | ~85% | ✅ Stigmergic Field + Forge View (138 tests) |
| **F-gents** | ~55% | ✅ Forge View (69 tests), ALO format pending |
| **M/N/psi** | 0% | Missing |

---

## Current Session

### Session: F-gent × I-gent Forge View (2025-12-09)

**Status**: ✅ COMPLETE - Pipeline composition UI for I-gent

**New Files**:
- `impl/claude/agents/i/forge_view.py` - Forge View implementation (~700 lines)
- `impl/claude/agents/i/_tests/test_forge_view.py` - 69 tests

**Key Components**:
1. **Archetype**: Agent template from L-gent catalog (id, symbol, level, types)
2. **Pipeline**: Composition chain (A >> B >> C) with type checking
3. **ForgeViewState**: Inventory + pipeline + cursor/selection state
4. **ForgeViewRenderer**: Two-panel TUI (inventory | pipeline)
5. **L-gent Integration**: `archetype_from_catalog_entry()`, `load_archetypes_from_entries()`

**CLI**: `kgents garden forge` - Interactive pipeline builder

**I-gent Tests**: 138 total (69 Forge View + 69 Field/TUI)

---

## Recent Sessions

### Session: L-gent Phase 8 - D-gent Vector DB (2025-12-09) ✅ COMMITTED

- `vector_db.py`: D-gent VectorBackend, VectorCatalog, migration utilities
- 23 tests, commit: `6bd9b63`

### Session: O-gent Phase 4 - W-gent Integration (2025-12-09) ✅ COMMITTED

- `observable_panopticon.py`: WireObservable mixin, TUI dashboard
- 40 tests, commit: `dd153d3`

### Session: I-gent Stigmergic Field (2025-12-09) ✅ COMMITTED

- `field.py`: Entity, Pheromone, FieldState, FieldSimulator
- `tui.py`: FieldRenderer with sparklines, TUIApplication
- Commit: `8f51bbc` - 69 tests (37 field + 32 TUI)

---

<details>
<summary>📦 Archive: Older Sessions (click to expand)</summary>

### Session: D-gent Phase 5 - SQL/Redis Backends (2025-12-09) ✅ COMMITTED

- `sql_agent.py`: SQLite + PostgreSQL backends with versioned state
- `redis_agent.py`: Redis/Valkey with TTL, pub/sub, history
- Commit: `7e4fba1` - 41 tests (36 skip when deps missing)

---

<details>
<summary>📦 Archive: Older Sessions (click to expand)</summary>

### B×G Phase 1 - Compression Economy (2025-12-09)
- `compression_economy.py`: Semantic Zipper, ROI calculation, pidgin commissioning
- 48 tests

### CLI Phase 2 - Bootstrap & Laws (2025-12-09)
- `bootstrap/laws.py`: 7 Category Laws with verification
- `bootstrap/principles.py`: 7 Design Principles with evaluation
- 48 tests

### G-gent Phase 7 - Pattern Inference (2025-12-09)
- `pattern_inference.py`: W-gent pattern → grammar synthesis
- 46 tests

### G-gent Phase 5 - F-gent Forge (2025-12-09)
- `forge_integration.py`: InterfaceTongue, TongueEmbedding
- 36 tests

### L-gent Phase 4 - Lattice Layer (2025-12-09)
- `lattice.py`: TypeLattice, subtype checking, composition verification
- 33 tests

### L-gent Phase 3 - Lineage Layer (2025-12-09)
- `lineage.py`: DAG-based provenance, cycle detection
- 33 tests

### L-gent Phase 2 - Persistence (2025-12-09)
- `persistence.py`: PersistentRegistry with D-gent storage
- 26 tests

### D-gent Phase 3 - Extended Protocols (2025-12-09)
- `transactional.py`, `queryable.py`, `observable.py`, `unified.py`
- 51 tests

### G-gent Phase 3 - P/J Integration (2025-12-09)
- `parser.py`, `interpreter.py`, `renderer.py`
- Parse → Execute → Render pipeline

### B-gent Phase 2 - D/L Integration (2025-12-09)
- `catalog_integration.py`: Hypothesis catalog + lineage tracking
- 45 tests

</details>

---

## Cross-Agent Integration Map

| From | To | Integration | Status |
|------|-----|-------------|--------|
| B-gent | J-gent | SharedEntropyBudget | ✅ |
| B-gent | W-gent | ValueDashboard | ✅ |
| B-gent | G-gent | Syntax Tax, Compression, JIT Efficiency | ✅ Complete |
| B-gent | O-gent | VoI Economics | ✅ Ready |
| O-gent | W-gent | ObservablePanopticon | ✅ Phase 4 |
| G-gent | L-gent | Tongue Catalog | ✅ |
| G-gent | F-gent | InterfaceTongue | ✅ |
| D-gent | L-gent | PersistentRegistry | ✅ |
| D-gent | L-gent | VectorCatalog (Phase 8) | ✅ |
| L-gent | Search | Three-Brain Hybrid | ✅ |

---

## Test Summary

| Module | Tests | Status |
|--------|-------|--------|
| B-gent | 575 | ✅ |
| D-gent | 271 | ✅ (9 skipped) |
| G-gent | 200+ | ✅ |
| I-gent | 69 | ✅ (Stigmergic Field) |
| L-gent | 200 | ✅ (Phase 8: +23) |
| O-gent | 177 | ✅ (Phase 4 complete) |
| CLI | 415 | ✅ |
| **Total** | 2560+ | ✅ |
