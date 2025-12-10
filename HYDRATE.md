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

**Status**: O-gent Phase 4 W-gent Integration COMPLETE ✅
**Branch**: `main`
**Latest Commit**: `8f51bbc` feat(i-gent): Stigmergic Field + TUI Renderer (37 tests, ~1,900 lines)

**Current State**:
- **O-gent Phase 4**: ✅ COMPLETE - W-gent integration (40 tests)
- **I-gent Stigmergic Field**: ✅ COMPLETE - Full rewrite from first principles (69 tests)
- **D-gent Phase 5**: ✅ COMMITTED - SQL/Redis backends (41 tests)
- **O-gent Phase 3**: ✅ COMPLETE - Panopticon Integration (137 tests)
- **B×G Phases 1-6**: ✅ COMPLETE (575 tests)

**Uncommitted**:
- `impl/claude/agents/o/observable_panopticon.py` - W-gent integration (NEW)
- `impl/claude/agents/o/_tests/test_observable_panopticon.py` - Tests (40 tests)

**Next Steps**:
1. **Commit**: O-gent Phase 4 W-gent integration
2. Proceed to next agent phase or consolidation

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
| 7 | TUI Dashboard | ⏳ NEXT |

**Key Features**: 10 Intent Verbs, Flowfiles (YAML), Sympathetic Errors, MCP Bidirectional

---

## Spec/Impl Gap Analysis

| Agent | Impl % | Key Gap |
|-------|--------|---------|
| **B-gents** | ~100% | ✅ All 6 B×G phases complete (575 tests) |
| **D-gents** | ~95% | ✅ Phase 5 SQL/Redis complete (276 tests) |
| **L-gents** | ~70% | Vector DB integration |
| **G-gents** | ~90% | Phase 7 done |
| **O-gents** | ~95% | ✅ Phase 4 complete (177 tests), W-gent integration |
| **I-gents** | ~70% | ✅ Stigmergic Field (69 tests), forge/timeline pending |
| **F-gents** | ~40% | Forge loop, ALO format |
| **M/N/psi** | 0% | Missing |

---

## Current Session

### Session: I-gent Stigmergic Field (2025-12-09)

**Status**: ✅ COMPLETE - Full rewrite from first principles

**Reference**: `~/git/kgents-garden-interface/` (demo frontend)

**Design Philosophy**: Stigmergic emergence—indirect coordination through shared environment
- Traditional: "What is the state?" → Stigmergic: "What traces are being left?"
- Three Layers: Physical (entities/positions), Topological (gravity/tension), Semantic (intent/values)

**Spec** (`spec/i-gents/README.md`):
- Stigmergic field substrate with pheromone traces
- Bootstrap agents: I/C/G/J/X/S/F (from spec/bootstrap.md)
- Task attractors: Tasks, Hypotheses, Artifacts
- Dialectic phases: DORMANT → FLUX → TENSION → SUBLATE → FIX → COOLING
- Field dynamics: Brownian motion, context gravity, tension repulsion
- Compost Heap: Event log celebrating "accursed share"
- W-gent integration via [observe] action

**Implementation** (~1500 lines):
- `impl/claude/agents/i/field.py`: Entity, Pheromone, FieldState, FieldSimulator
- `impl/claude/agents/i/tui.py`: FieldRenderer, TUIApplication, KeyHandler
- `impl/claude/protocols/cli/genus/i_gent.py`: Garden CLI commands

**CLI Commands**:
- `kgents garden` - Launch interactive field view
- `kgents garden forge` - Composition pipeline view
- `kgents garden export <file.md>` - Export to markdown
- `kgents garden demo` - Run demo simulation

**Test Coverage** (69 tests):
- test_field.py: 37 tests (Entity, Pheromone, FieldState, Simulator)
- test_tui.py: 32 tests (Renderer, Colors, KeyHandler, Edge cases)

---

## Recent Sessions

### Session: O-gent Phase 3 - Panopticon Integration (2025-12-09)

- `panopticon.py`: Unified dashboard with 3D + Bootstrap observers
- 50 tests, real-time streaming via async generator

### Session: D-gent Phase 5 - SQL/Redis Backends (2025-12-09) ✅ COMMITTED

- `sql_agent.py`: SQLite + PostgreSQL backends with versioned state
- `redis_agent.py`: Redis/Valkey with TTL, pub/sub, history
- Commit: `7e4fba1` - 41 tests (36 skip when deps missing)

### Session: B×G Phase 6 - JIT Efficiency (2025-12-09) ✅ COMMITTED

- `jit_efficiency.py`: JIT compilers (Regex, JumpTable, Bytecode)
- Commit: `ce5dd8d` - 84 tests, HFTongueBuilder

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
| G-gent | L-gent | Tongue Catalog | ✅ |
| G-gent | F-gent | InterfaceTongue | ✅ |
| D-gent | L-gent | PersistentRegistry | ✅ |
| L-gent | Search | Three-Brain Hybrid | ✅ |

---

## Test Summary

| Module | Tests | Status |
|--------|-------|--------|
| B-gent | 575 | ✅ |
| D-gent | 271 | ✅ (9 skipped) |
| G-gent | 200+ | ✅ |
| I-gent | 69 | ✅ (Stigmergic Field) |
| L-gent | 177 | ✅ |
| O-gent | 137 | ✅ (+50 Phase 3) |
| CLI | 415 | ✅ |
| **Total** | 2520+ | ✅ |
