# HYDRATE.md - kgents Session Context

Keep it concise—focus on current state and recent work.

---

## TL;DR

**Status**: All Tests Passing ✅ | **Branch**: `main` | **Tests**: 4909+ collected

**Recent Work**:
- **E-gent Dependencies** ← COMPLETE (L-gent 49 tests, B-gent 29 tests)
- E-gent Implementation Rebuild (PLANNING COMPLETE)
- Ψ-gent v1 (104 tests)

---

## E-gent Dependencies (COMPLETE)

### L-gent Integration (`agents/l/egent_integration.py`) - 49 tests

| Feature | Purpose |
|---------|---------|
| `MutationSchema` | Isomorphic transformation patterns with Gibbs ΔG |
| `STANDARD_SCHEMAS` | 14 schemas (substitute, extract, inline, annotate, restructure) |
| `CodeIntent` | Teleological field (embedding + source + confidence) |
| `infer_types()` | Static type inference for semantic stability |
| `types_compatible()` | Check mutation preserves type structure |
| `EgentSemanticRegistry` | Extended registry with archetype management |

### B-gent Integration (`agents/b/egent_integration.py`) - 29 tests

| Feature | Purpose |
|---------|---------|
| `PredictionMarket` | Betting on mutation success with AMM-style odds |
| `Sun` | Grant system for exogenous energy |
| `StakingPool` | Skin-in-the-game for infect operations |
| `EvolutionEconomics` | Combined system (bank + market + sun + staking) |

---

## E-gent Rebuild Plan

**Plan**: `docs/e-gent-rebuild-plan.md`

### Next Steps (Phase 0-7)

| Phase | Component | Status |
|-------|-----------|--------|
| 0 | `types.py` | ⏳ Pending |
| 1 | `demon.py` (Teleological Demon) | ⏳ Pending |
| 2 | `mutator.py` (Schema-based) | ⏳ Pending |
| 3 | `market.py` (uses B-gent PredictionMarket) | ✅ Dependency ready |
| 4 | `sun.py` (uses B-gent Sun) | ✅ Dependency ready |
| 5 | `library.py` (Viral Library) | ⏳ Pending |
| 6 | `phage.py` (Active mutation vectors) | ⏳ Pending |
| 7 | `cycle.py` (Thermodynamic cycle) | ⏳ Pending |

### Strategy

Build in `agents/e/v2/` parallel to existing, then cutover.

---

## E-gent Teleological Thermodynamics (v2)

Refined from v1 based on critique of "Blind Watchmaker Paradox":

### Key Additions

| Concept | Purpose |
|---------|---------|
| **Gibbs Free Energy** | ΔG = ΔH - TΔS selection criterion |
| **Teleological Demon** | Intent alignment check (prevents parasites) |
| **The Sun (Grants)** | Exogenous energy for high-risk work |
| **Semantic Schemas** | L-gent isomorphic mutations (not random) |
| **Four Laws** | Added Fourth Law: Teleology constrains thermodynamics |

### The Refined Motto

> *"The Sun gives (Energy/Intent). The Demon selects (Efficiency). The Phage adapts (Structure)."*
> *"Without the Sun, the Demon starves. Without the Demon, the Sun burns."*

### Five-Layer Selection

1. Syntactic viability (FREE)
2. Semantic stability (CHEAP) - L-gent type lattice
3. **Teleological alignment (CHEAP-ISH)** ← Prevents parasites
4. Thermodynamic viability (FREE) - Gibbs check
5. Economic viability (FREE) - Market quote

### Key Insight: Parasitic Code Prevention

Pure thermodynamics leads to parasitic code (lowest energy = empty/hardcoded).
The Teleological Field (Intent embedding) constrains evolution to PURPOSE.

---

## Ψ-gent v3.0 Implementation (NEW)

**Location**: `impl/claude/agents/psi/v3/`
**Plan**: `docs/psi-gent-v3-implementation-plan.md`
**Tests**: 104 passed

### Architecture

```
RETRIEVE → PROJECT → CHALLENGE → SOLVE → TRANSLATE → VERIFY
    ↑          ↑                              ↓
    └──────────┴──────────── LEARN ←─────────┘
```

### Files (~1500 lines total)

| File | Purpose | Tests |
|------|---------|-------|
| `types.py` | Core types (Problem, Metaphor, Distortion) | 30 |
| `corpus.py` | Standard metaphors (Plumbing, Ecosystem, etc.) | 20 |
| `engine.py` | Six-stage pipeline with backtracking | 33 |
| `learning.py` | Thompson sampling for retrieval | 21 |
| `integrations.py` | L/B/D/N/G-gent adapters | - |

### Key Improvements Over v2.0

| v2.0 | v3.0 | Benefit |
|------|------|---------|
| MHC 15 levels | `abstraction: 0.0-1.0` | Measurable |
| 4-axis tensor | 3 distortion metrics | Computable |
| PsychopompAgent | MetaphorEngine | 6-stage pipeline |
| String shadows | CHALLENGE stage | Adversarial testing |
| MetaphorUmwelt/DNA | Learning | Data-driven |

### Standard Corpus

6 metaphors with 3-5 operations each:
1. **Plumbing**: flow, constriction, reservoir, bypass
2. **Ecosystem**: niches, symbiosis, invasive species
3. **Traffic**: bottlenecks, lanes, signals, routing
4. **Medicine**: diagnosis, treatment, monitoring
5. **Architecture**: foundations, load-bearing, renovation
6. **Gardening**: growth, pruning, weeding

---

## Integration Map

| Integration | Status |
|-------------|--------|
| J×DNA, F×J, B×J, B×W, B×G | ✅ |
| D×L, D×M, M×L, M×B | ✅ |
| N×L, N×M, N×I, N×B | ✅ |
| O×W Panopticon | ✅ |
| **E×B (Market+Grants)** | 📋 Specified (v2) |
| **E×L (Schemas+Intent)** | 📋 Specified (v2) |
| **Ψ×L (Embeddings)** | ✅ Implemented (integrations.py) |
| **Ψ×B (Budgets)** | ✅ Implemented (integrations.py) |
| **Ψ×D (Learning persistence)** | ✅ Implemented (integrations.py) |
| **Ψ×N (Tracing)** | ✅ Implemented (integrations.py) |
| **Ψ×G (Prompts)** | ✅ Implemented (integrations.py) |
| **Ψ×E (Metaphor evolution)** | 📋 Specified |

---

## Test Infrastructure (Phase 6 Complete)

| Component | Status |
|-----------|--------|
| conftest.py hierarchy | ✅ 5 files (root, agents, bootstrap, testing, L-gent) |
| Law markers | ✅ **63 tests** via `-m "law"` |
| WitnessPlugin | ✅ `pytest --witness` |
| Accursed share tests | ✅ **23 chaos tests** |
| Property-based tests | ✅ `test_laws_property.py` (hypothesis) |
| CI laws workflow | ✅ `.github/workflows/laws.yml` |

### Phase 6 Additions

- **laws.yml**: CI workflow for law verification + property tests + chaos tests
- **test_laws_property.py**: Hypothesis-powered category law verification
- **test_accursed_share_extended.py**: 23 chaos tests for D/L/N/Cross-agent scenarios
- **L-gent conftest.py**: Shared `registry` and `lattice` fixtures
- **Law markers**: Added to test_lens.py, test_symbiont.py, test_lattice.py

---

## MCP Server (`impl/claude/protocols/cli/mcp/`)

| Tool | Agent | Status |
|------|-------|--------|
| `kgents_speak` | G-gent | ✅ Wired to Grammarian |
| `kgents_find` | L-gent | ✅ Wired to SemanticRegistry |
| `kgents_psi` | Psi-gent | ✅ NEW - Metaphor solving |
| `kgents_check` | Bootstrap | ✅ Works |
| `kgents_flow_run` | Flow | ✅ Works |

**Usage**: `kgents mcp serve` → stdio server for Claude/Cursor

---

## Key Docs

| Doc | Content |
|-----|---------|
| `docs/psi-gent-v3-implementation-plan.md` | **NEW** - v3.0 impl plan |
| `spec/e-gents/thermodynamics.md` | **v2** - Teleological thermodynamics |
| `spec/e-gents/README.md` | **v2** - Updated overview |
| `spec/e-gents/memory.md` | Viral Library spec |
| `spec/psi-gents/*.md` | v3.0 Morphic Engine spec (10 files) |
| `docs/plans-synthesis.md` | Consolidated architecture |
