# HYDRATE.md - kgents Session Context

Keep it concise—focus on current state and recent work.

---

## TL;DR

**Status**: Ψ-gent + Integration Tests ✅ | **Branch**: `main` | **Latest**: `bac0baf`

**This Session**:
- ✅ Fixed all 45 Ψ-gent test failures (177 tests passing)
- ✅ Integration tests Phase 1-3 (109 tests passing)
- ✅ New features: F-gent reality_contracts, L-gent advanced_lattice, I-gent components

**Uncommitted**: 8 failing integration test files (API mismatches)

**Next Steps**: Fix remaining integration test API mismatches (O×W, N×M, B×G)

---

## Spec/Impl Status

| Agent | % | Tests | Status |
|-------|---|-------|--------|
| B | 100 | 575 | ✅ B×G complete |
| D | 95 | 276 | ✅ SQL/Redis |
| G | 90 | 200+ | ✅ Phase 7 |
| L | 90 | 234 | ✅ AdvancedLattice |
| O | 95 | 177 | ✅ W-gent |
| I | 90 | 183 | ✅ UI Components |
| F | 75 | 151 | ✅ Reality Contracts |
| M | 95 | 148 | ✅ Phase 4 |
| N | 100 | 304 | ✅ Phase 1-6 |
| J | 100 | 184 | ✅ DNA migration |
| Ψ | 100 | 177 | ✅ All passing |
| **Total** | - | **3000+** | ✅ |

---

## N-gent Phase 6: Epistemic Features

### Components
- `ConfidenceLevel`: Discrete confidence levels (CERTAIN/HIGH/MODERATE/LOW/UNCERTAIN)
- `ReliabilityAnnotation`: Confidence + corroboration/contradiction tracking
- `UnreliableTrace`: Trace with reliability metadata
- `HallucinationType`: Types of potential hallucination
- `HallucinationIndicator`: Signs of potential hallucination
- `HallucinationDetector`: Detects overconfidence, contradictions, confabulation
- `UnreliableNarrative`: Narrative with epistemic annotations
- `UnreliableNarrator`: Narrator with epistemic humility
- `PerspectiveSpec`: Configuration for one perspective
- `Contradiction`: Where perspectives disagree
- `RashomonNarrative`: Multiple perspectives on same events
- `RashomonNarrator`: Multi-perspective story generation
- `GroundTruth`: Verified fact for reconciliation
- `ReconciliationResult`: Ground truth comparison result
- `GroundTruthReconciler`: Compare narratives against facts

### Philosophy
The UnreliableNarrator and RashomonNarrator embody epistemic humility:
- LLMs can hallucinate. Stories can be wrong.
- Multiple perspectives on the same events yield different truths.
- Confidence annotations mark uncertainty.

---

## Integration Tests

**Created from docs/integration-test-plan.md**:

| File | Tests | Status |
|------|-------|--------|
| test_parser_pipeline_integration.py | 21 | ✅ P×G×E×F |
| test_factory_pipeline_integration.py | 26 | ✅ J×F×T×L×B |
| test_memory_pipeline_integration.py | 23 | ✅ M×D×L×B×N |
| test_agent_creation_e2e.py | 20 | ✅ Spec→DNA→Impl→Exec |
| test_tool_pipeline_e2e.py | 19 | ✅ F→J→T→O→N |
| **Phase 1-3 Total** | **109** | ✅ All passing |

**Uncommitted Tests (API mismatches - 65 failures)**:
- test_observation_stack_integration.py - O×W: ObservationStatus, AlertSeverity, WireObservable
- test_narrative_stack_integration.py - N×M: Historian.end_trace(output→outputs), Verbosity.BRIEF
- test_economics_stack_integration.py - B×G: SharedEntropyBudget, BudgetedMemory, VoIOptimizer
- test_dna_lifecycle.py - Bootstrap: Grounded/Fix API updates
- test_composition_laws.py - C-gent: Category law APIs
- test_h_gent_integration.py - H-gent: Dialectic APIs
- test_c_gent_integration.py - C-gent: Composition APIs
- test_k_gent_integration.py - K-gent: Persona APIs

---

## Integration Map

| Integration | Status |
|-------------|--------|
| J×DNA | ✅ JGentConfig extends JGentDNA |
| F×J RealityGate | ✅ Reality-aware gravity contracts |
| B×J SharedEntropyBudget | ✅ |
| B×W ValueDashboard | ✅ |
| B×G Syntax/Compression | ✅ |
| D×L VectorCatalog | ✅ |
| D×M UnifiedMemory | ✅ |
| M×L VectorHolographic | ✅ |
| M×B BudgetedMemory | ✅ |
| N×L IndexedCrystalStore | ✅ |
| N×M ResonantCrystalStore | ✅ |
| N×I VisualizableBard | ✅ |
| N×B BudgetedBard | ✅ |
| O×W Panopticon | ✅ |

---

## Key Docs

| Doc | Content |
|-----|---------|
| `docs/m-gent-treatment.md` | Holographic memory spec (~850 lines) |
| `docs/n-gent-treatment.md` | Historian/Bard architecture |
| `docs/psi-gent-synthesis.md` | Cross-pollination roadmap |
| `docs/24hr-retrospective-and-synthesis.md` | Harmonic Lattice proposal |
