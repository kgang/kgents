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

**Status**: CLI Phase 5 (Genus Layer) COMPLETE ✅
**Branch**: `main`
**Latest Commit**: uncommitted (CLI Phase 5 - Genus Layer)

**Current State**:
- **CLI Phase 5**: ✅ Genus Layer (50 tests) - `protocols/cli/genus/`
  - G-gent (grammar): reify, parse, evolve, list, show, validate, infer
  - J-gent (jit): compile, classify, defer, execute, stability, budget
  - P-gent (parse): extract, repair, validate, stream, compose
  - L-gent (library): catalog, discover, register, show, lineage, compose
  - W-gent (witness): watch, fidelity, sample, serve, dashboard, log
- **CLI Phases 1-4**: ✅ COMPLETE (271 tests)
- **B×G Phases 1-4**: ✅ COMPLETE (Compression, Fiscal, Syntax Tax, Inflation)
- D-gent Phase 4 (Noosphere): ✅ COMPLETE
- L-gent Phases 1-7: ✅ COMPLETE
- G-gent Phases 1-7: ✅ COMPLETE

**Next Steps**:
1. **CLI Phase 6**: Intent Layer (10 verbs: new, run, check, think, watch, find, fix, speak, judge, do)
2. **CLI Phase 7**: TUI Dashboard (Textual-based DVR)
3. **B×G Phase 5**: Grammar Insurance or JIT Efficiency

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
| 6 | Intent Layer (10 verbs) | ⏳ NEXT |
| 7 | TUI Dashboard | ⏳ PENDING |

**Key Features**: 10 Intent Verbs, Flowfiles (YAML), Sympathetic Errors, MCP Bidirectional

---

## Spec/Impl Gap Analysis

| Agent | Impl % | Key Gap |
|-------|--------|---------|
| **B-gents** | ~95% | B×G Phase 5 (JIT/Grammar Insurance) |
| **D-gents** | ~80% | Minor SQL/Redis backends |
| **L-gents** | ~70% | Vector DB integration |
| **G-gents** | ~90% | Phase 7 done |
| **O-gents** | ~70% | Phase 1 complete (62 tests), BootstrapWitness integration |
| **I-gents** | ~10% | TUI, evolve.py, sessions |
| **F-gents** | ~40% | Forge loop, ALO format |
| **M/N/psi** | 0% | Missing |

---

## Current Session

### Session: CLI Phase 5 - Genus Layer (2025-12-09)

**Status**: ✅ COMPLETE - Big 5 Genera CLI Commands

**Spec Reference**: `docs/cli-integration-plan.md` Part 6 (Genus Layer)

**New Files Created** (~2,200 lines):
- `impl/claude/protocols/cli/genus/__init__.py`: Module exports with lazy loading
- `impl/claude/protocols/cli/genus/g_gent.py` (~750 lines): Grammar/DSL CLI
  - Subcommands: reify, parse, evolve, list, show, validate, infer
- `impl/claude/protocols/cli/genus/j_gent.py` (~620 lines): JIT Intelligence CLI
  - Subcommands: compile, classify, defer, execute, stability, budget
- `impl/claude/protocols/cli/genus/p_gent.py` (~580 lines): Parser CLI
  - Subcommands: extract, repair, validate, stream, compose
- `impl/claude/protocols/cli/genus/l_gent.py` (~720 lines): Library/Catalog CLI
  - Subcommands: catalog, discover, register, show, lineage, compose, types, stats
- `impl/claude/protocols/cli/genus/w_gent.py` (~640 lines): Witness/Wire CLI
  - Subcommands: watch, fidelity, sample, serve, dashboard, log
- `impl/claude/protocols/cli/genus/_tests/test_genus.py` (~700 lines): 50 tests

**Test Coverage** (50 tests, 100% pass):
- G-gent: 8 tests, J-gent: 10 tests, P-gent: 8 tests, L-gent: 10 tests, W-gent: 9 tests
- Module imports: 2 tests, Integration: 3 tests

**CLI Tests Total**: 321 passed (50 new)

---

## Recent Sessions

### Session: O-gent Phase 1 - VoI-Based Observation (2025-12-09)

**Status**: ✅ COMPLETE - Full O-gent implementation using VoI Economics

**Spec Reference**: `spec/o-gents/README.md` (The Epistemic Substrate)

**New Files Created** (~2,400 lines):
- `impl/claude/agents/o/observer.py` (~600 lines): Core observer functor
  - `ObserverFunctor`: O: Agent[A,B] → Agent[A,B] (lifts agents into observation)
  - `ProprioceptiveWrapper`: Transparent wrapper that observes without mutating
  - `ObserverHierarchy`: Stratified observation (prevents "who watches watchers" regress)
- `impl/claude/agents/o/telemetry.py` (~550 lines): Dimension X (The Body)
  - `MetricsCollector`: Counter, Gauge, Histogram (OpenTelemetry-compatible)
  - `TelemetryObserver`: Latency, errors, throughput tracking
  - `TopologyMapper`: Agent composition graph, hot paths, bottlenecks
- `impl/claude/agents/o/semantic.py` (~700 lines): Dimension Y (The Mind)
  - `DriftDetector`: Semantic drift (Noether's theorem for agents)
  - `BorromeanObserver`: Lacanian RSI health (Symbolic/Real/Imaginary)
  - `HallucinationDetector`: Grounding failure detection
- `impl/claude/agents/o/axiological.py` (~720 lines): Dimension Z (The Soul)
  - `ValueLedgerObserver`: System GDP, agent rankings by RoC
  - `RoCMonitor`: Real-time Return on Compute monitoring
  - `LedgerAuditor`: Bankruptcy detection, suspicious activity
- `impl/claude/agents/o/voi_observer.py` (~600 lines): VoI Integration
  - `VoIAwareObserver`: Budget-aware observation depth selection
  - `Panopticon`: Unified 3-dimension dashboard (ASCII render)
- `impl/claude/agents/o/_tests/test_o_gent.py` (~1,000 lines): 62 comprehensive tests

**Core Concepts**:
- **Three Dimensions**: Telemetry (running?), Semantic (meaningful?), Axiological (profitable?)
- **Observer Functor**: O(f) ≅ f (observation invisible to observed)
- **VoI Integration**: Each observation must justify its cost
- **Heisenberg Constraint**: Observation consumes tokens → optimize VoI

**Test Coverage** (62 tests, 100% pass):
- Core Observer: 13 tests (functor, hierarchy, composite)
- Telemetry (X): 11 tests (metrics, topology)
- Semantics (Y): 11 tests (drift, Borromean, hallucination)
- Axiology (Z): 12 tests (ledger, RoC, auditing)
- VoI Integration: 8 tests (budget, depth selection, stats)
- Integration/Edge: 7 tests

**O-gent Total**: 62 tests passed

---

## Recent Sessions

### Session: B×G Phase 4 - Semantic Inflation (2025-12-09)

- `semantic_inflation.py`: Complexity → Verbosity, DeflationNegotiator, SemanticCPIMonitor
- 78 tests

### Session: B×G Phase 3 - Syntax Tax (2025-12-09)

- `syntax_tax.py`: Chomsky-based pricing (Type 0-3), GrammarClassifier, Escrow for Turing
- 60 tests

### Session: B-gent Phase 4 - VoI Economics (2025-12-09)

- `voi_economics.py`: Value of Information, EpistemicCapital, VoIOptimizer, AdaptiveObserver
- 51 tests

### D-gent Finalization (2025-12-09) - Commit f6a35cc

- Lenses: Prism, Traversal, LensValidation
- Persistence: Schema versioning, Backup/restore
- 49 tests

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
| B-gent | G-gent | Syntax Tax, Compression Economy | ✅ Partial |
| B-gent | O-gent | VoI Economics | ✅ Ready |
| G-gent | L-gent | Tongue Catalog | ✅ |
| G-gent | F-gent | InterfaceTongue | ✅ |
| D-gent | L-gent | PersistentRegistry | ✅ |
| L-gent | Search | Three-Brain Hybrid | ✅ |

---

## Test Summary

| Module | Tests | Status |
|--------|-------|--------|
| B-gent | 349 | ✅ |
| D-gent | 271 | ✅ (9 skipped) |
| G-gent | 200+ | ✅ |
| L-gent | 177 | ✅ |
| CLI | 271 | ✅ |
| **Total** | 2000+ | ✅ |
