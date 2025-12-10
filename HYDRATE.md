# HYDRATE.md - kgents Session Context

Keep it concise—focus on current state and recent work.

---

## TL;DR

**Status**: Ψ-gent FIXED ✅ | **Branch**: `main` | **Latest**: `2aa68ce`

**This Session**:
- ✅ Fixed all 45 Ψ-gent test failures (177 tests now passing)
- Key fixes: AxisType.Z_MHC, TensorPosition, MetaphorSolution, ComplexityMetrics, ShadowGenerator, DialecticalRotator

**Uncommitted**: Ψ-gent fixes (types.py, resolution_scaler.py, dialectical_rotator.py)

**Next Steps**: Commit Ψ-gent fixes | Integration tests | Full test run

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
