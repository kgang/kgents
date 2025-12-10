# HYDRATE.md - kgents Session Context

## TL;DR

**Status**: All Tests Passing ✅ | **Branch**: `main` | **Tests**: ~5,300+

## Recent Completions

- **Integration Tests Phase 3**: 65 E2E tests (Agent Creation, Tool Pipeline, Memory Recall)
- **E-gent v2**: 353 tests, thermodynamic evolution with safety guardrails
- **M-gent Cartography**: 114 tests, holographic maps for context injection
- **Ψ-gent v3.0**: 104 tests, metaphor engine with 6-stage pipeline
- **Cortex Assurance v2.0**: 73 tests, cybernetic immune system
- **CLI Auto-Bootstrap**: No setup needed, auto-creates `~/.local/share/kgents/`

## Architecture Quick Reference

| Agent | Purpose | Key File |
|-------|---------|----------|
| **E-gent** | Code evolution (thermodynamic) | `agents/e/cycle.py` |
| **M-gent** | Context cartography | `agents/m/cartographer.py` |
| **Ψ-gent** | Metaphor solving | `agents/psi/v3/engine.py` |
| **L-gent** | Semantic embeddings | `agents/l/semantic_registry.py` |
| **B-gent** | Token economics | `agents/b/metered_functor.py` |
| **N-gent** | Narrative traces | `agents/n/chronicle.py` |
| **O-gent** | Observation hierarchy | `agents/o/observer.py` |

## CLI Commands

```bash
kgents pulse          # Health check (auto-bootstraps DB)
kgents check .        # Validate project
kgents wipe global    # Remove global DB
kgents mcp serve      # MCP server for Claude/Cursor
```

## Test Commands

```bash
pytest -m "not slow" -n auto   # Fast (~6s, 4891 tests)
pytest -m "slow"               # Slow tests only
pytest -m "law"                # Property-based laws
```

## Integration Map (All ✅)

J×DNA, F×J, B×J, B×W, B×G, D×L, D×M, M×L, M×B, N×L, N×M, N×I, N×B, O×W, E×B, E×L, Ψ×L, Ψ×B, Ψ×D, Ψ×N, Ψ×G

## Key Docs

| Doc | Topic |
|-----|-------|
| `docs/agent-cross-pollination-final-proposal.md` | Integration architecture |
| `docs/instance-db-implementation-plan.md` | Unified Cortex |
| `docs/cortex-assurance-system.md` | Test intelligence |
| `spec/e-gents/thermodynamics.md` | E-gent theory |

## API Notes (from reconciliation)

- `CentralBank`: uses `max_balance`, not `initial_tokens`
- `EntropyBudget`: uses `initial/remaining`, not `max_depth`
- `Chronicle`: uses `get_agent_crystals()`, not `get_traces()`
- `HolographicMemory`: uses `retrieve()`, not `recall()`
