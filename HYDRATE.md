# HYDRATE.md - kgents Session Context

Keep it concise—focus on current state and recent work.

---

## TL;DR

**Status**: All Tests Passing ✅ | **Branch**: `main` | **Tests**: 4722 collected, 4613 passed, 110 skipped

**Recent Work**:
- **Ψ-gent v3.0 Spec Rewrite** ← CURRENT
- E-gent Thermodynamic Reconceptualization
- Test evolution plan EXECUTED (all 5 phases)

---

## Ψ-gent v3.0 Spec (NEW)

Complete rewrite of `spec/psi-gents/` based on first-principles analysis.

### Key Changes

| v2.0 | v3.0 | Why |
|------|------|-----|
| MHC 15 levels | `abstraction: 0.0-1.0` | Cargo cult → continuous |
| Jungian Shadow | CHALLENGE stage | String manipulation → adversarial testing |
| Lacanian RSI | VERIFY structural checks | Ceremonial → measurable |
| 5 value dimensions | 3 distortion metrics | Aspirational → computable |
| MetaphorUmwelt/DNA | Removed | Over-specified → learn from data |
| PsychopompAgent | MetaphorEngine | 4-axis tensor → 6-stage pipeline |

### New Architecture

```
RETRIEVE → PROJECT → CHALLENGE → SOLVE → TRANSLATE → VERIFY
    ↑          ↑                              ↓
    └──────────┴──────────── LEARN ←─────────┘
```

### New Spec Files

| File | Content |
|------|---------|
| `README.md` | Philosophy, overview, migration guide |
| `types.md` | Minimal, measurable types |
| `retrieval.md` | Embedding + learning-based retrieval |
| `projection.md` | LLM-mediated concept mapping |
| `challenge.md` | Adversarial testing (4 challenge types) |
| `solving.md` | Executable operations with state tracking |
| `translation.md` | Reverse mapping with constraint verification |
| `verification.md` | 3-dimensional distortion measurement |
| `learning.md` | Contextual bandits for metaphor selection |
| `integration.md` | L/B/D/N/G/E-gent integration |

### Core Improvements

1. **LLM-in-the-loop**: All semantic operations use LLM
2. **Real search**: Backtracking on failure, not linear iteration
3. **Measurable distortion**: structural_loss + round_trip_error + prediction_failures
4. **Learning**: Thompson sampling for retrieval, abstraction learning

---

## Integration Map

| Integration | Status |
|-------------|--------|
| J×DNA, F×J, B×J, B×W, B×G | ✅ |
| D×L, D×M, M×L, M×B | ✅ |
| N×L, N×M, N×I, N×B | ✅ |
| O×W Panopticon | ✅ |
| E×B (PredictionMarket) | 📋 Specified |
| **Ψ×L (Embeddings)** | 📋 Specified |
| **Ψ×B (Budgets)** | 📋 Specified |
| **Ψ×D (Learning persistence)** | 📋 Specified |
| **Ψ×N (Tracing)** | 📋 Specified |
| **Ψ×G (Prompts)** | 📋 Specified |
| **Ψ×E (Metaphor evolution)** | 📋 Specified |

---

## Test Infrastructure

| Component | Status |
|-----------|--------|
| conftest.py hierarchy | ✅ 4 files |
| Law markers | ✅ 22 tests via `-m "law"` |
| WitnessPlugin | ✅ `pytest --witness` |
| Accursed share tests | ✅ 6 chaos tests |

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
| `spec/psi-gents/*.md` | v3.0 Morphic Engine spec (10 files) |
| `spec/e-gents/thermodynamics.md` | Thermodynamic evolution model |
| `docs/plans-synthesis.md` | Consolidated architecture (7 docs → 150 lines) |
| `docs/test-evolution-plan.md` | 5-phase test strategy (EXECUTED) |
