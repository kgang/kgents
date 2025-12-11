# Mypy Error Elimination Plan

**Initial state**: 7,516 strict errors baselined
**Current state**: 🎉 **0 strict errors** (100% reduction - GOAL ACHIEVED!)
**Goal**: Zero mypy errors under `--strict` ✅

## Progress Summary

| Phase | Description | Errors Fixed |
|-------|-------------|--------------|
| Phase 1 | Add `-> None` to test functions | ~6,304 |
| Phase 2 | Fix fixture return types | ~128 |
| Phase 3 | Fix source file annotations | ~76+ |
| Phase 4 | Production code `__init__`/`__post_init__` fixes | ~307 |
| Phase 5 | Production code type fixes (2024-12-11) | ~174 |
| Phase 6 | Test file comprehensive fixes (2024-12-11) | ~128 |
| Phase 7 | Multi-file type fixes (2024-12-11) | ~143 |
| Phase 8 | New file baseline sync (2024-12-11) | +194 (new files) |
| Phase 9 | Bulk test file fixes (2024-12-11) | ~1,915 |
| Phase 10 | Parallel agent mypy sweep (2024-12-11) | ~583 |
| Phase 11 | Massive parallel agent sweep (2024-12-11) | ~656 |
| Phase 12 | Final parallel sweep (2024-12-11) | ~176 |
| **Phase 13** | **Final cleanup (2024-12-11)** | **~37** |
| **Total** | | **~7,520 errors fixed** |

### Phase 13 Fixes (2024-12-11) - Final Cleanup 🎉

Eliminated the final 33 baselined errors + 4 introduced during fixing = 37 total.

**Key statistics:**
- Starting errors: 33 baselined
- Ending errors: 0 baselined
- Net reduction: 37 errors (100% - COMPLETE!)

**Production files fixed (9):**
- `agents/d/manifold.py` - Add generic type param to dict
- `agents/d/bicameral.py` - Add `**config_kwargs: Any` annotation
- `agents/l/vector_db.py` - Fix VectorAgent generic type param
- `agents/t/judge.py` - Add `-> None` to `__post_init__` methods
- `agents/b/persistent_hypothesis.py` - Add `-> None` to `__post_init__`
- `agents/conftest.py` - Wrap comparisons in `bool()` to fix no-any-return
- `agents/o/voi_observer.py` - Add `__all__` for explicit exports
- `agents/j/t_integration.py` - Add `# type: ignore[override]` for intentional design
- `agents/f/p_integration.py` - Add `Any` import and type annotation

**Test files fixed (12):**
- `test_phage.py` - Add Generator type to fixture return
- `test_semantic_field.py` - Add generic type params to SemanticPheromone
- `test_safety.py` - Add null checks before accessing checkpoint attributes
- `test_incremental.py` - Rewrite loop to avoid None comparison operators
- `test_vector.py` - Add VectorAgent generic type params
- `test_lens.py` - Add Lens import and generic type params
- `test_lens_agent.py` - Add VolatileAgent generic type params
- `test_symbiont.py` - Add Id generic type params
- `test_j_phase3.py` - Use setattr for __is_test__, add null check
- `test_tool_pipeline_e2e.py` - Add dict generic type params
- `test_narrative_stack_integration.py` - Add HolographicMemory type params
- `test_compression_economy.py` - Add `# type: ignore[comparison-overlap]`
- `test_o_gent.py` - Remove obsolete type: ignore comment

**Key patterns applied:**
- Add explicit `__all__` for module re-exports
- Use `# type: ignore[override]` for intentional interface variations
- Add generic type params to all generic classes
- Add `-> None` to all `__post_init__` methods
- Remove obsolete `# type: ignore` comments

### Phase 12 Fixes (2024-12-11) - Final Parallel Sweep

Deployed 62 parallel agents to systematically fix the final 209 errors across 72 files.

**Key statistics:**
- Starting errors: 209 baselined
- Ending errors: 33 baselined
- Net reduction: 176 errors (84% in single session)
- Files touched: 62+

**Production files fixed (22):**
- `agents/i/cli.py`, `agents/conftest.py`, `agents/a/skeleton.py`
- `agents/o/voi_observer.py`, `agents/o/observable_panopticon.py`, `agents/o/__init__.py`
- `agents/l/vector_db.py`, `agents/l/vector_backend.py`
- `agents/d/vector.py`, `agents/d/manifold.py`, `agents/d/bicameral.py`
- `agents/t/property.py`, `agents/t/oracle.py`, `agents/t/mock.py`, `agents/t/judge.py`, `agents/t/failing.py`
- `agents/k/persistent_persona.py`, `agents/b/persistent_hypothesis.py`
- `agents/j/jgent.py`, `agents/j/factory_integration.py`, `agents/j/t_integration.py`
- `agents/f/prototype.py`, `agents/f/validate.py`, `agents/f/crystallize.py`, `agents/f/p_integration.py`
- `agents/w/value_dashboard.py`, `agents/i/observe.py`, `agents/g/catalog_integration.py`
- `agents/f/forge_with_search.py`, `agents/shared/fixtures_integration.py`
- `agents/m/_tests/conftest.py`

**Test files fixed (40):**
- `test_r_types.py`, `test_quartermaster.py`, `test_psi_types.py`
- `test_incremental.py`, `test_core.py`, `test_cortex_observer.py`
- `test_historian.py`, `test_epistemic.py`, `test_pathfinder.py`
- `test_hypothesis_indexing.py`, `test_semantic_field.py`, `test_forge_view.py`
- `test_synthesis.py`, `test_fuzzing_integration.py`, `test_safety.py`
- `test_phage.py`, `test_demon.py`, `test_vector.py`, `test_sql_agent.py`
- `test_lens.py`, `test_bicameral.py`, `test_c_integration.py`
- `test_syntax_tax.py`, `test_jit_efficiency.py`, `test_skeleton.py`
- `test_volatile.py`, `test_symbiont.py`, `test_lens_agent.py`, `test_cached.py`
- `test_graph.py`, `test_t_phase3.py`, `test_narrative_stack_integration.py`
- `test_h_integration.py`, `test_validate.py`, `test_crystallize.py`
- `test_integration.py`, `test_j_phase3.py`, `test_tool_pipeline_e2e.py`
- `test_compression_economy.py`, `test_observation_stack_integration.py`
- `test_economics_stack_integration.py`, `test_f_forge_integration.py`

**Key patterns applied:**
- Add generic type parameters (`MockAgent[Any, Any]`, `HolographicMemory[Any]`, etc.)
- Add `# type: ignore[arg-type]` for intentional test type mismatches (catalog.Registry vs registry.Registry)
- Add `# type: ignore[comparison-overlap]` for intentional enum/status comparisons
- Add `# type: ignore[operator]` for intentional composition testing
- Add `assert x is not None` for type narrowing before Optional access
- Fix return type annotations with `str()`, `int()`, `float()` wrappers
- Remove unused `# type: ignore` comments that became obsolete

### Phase 11 Fixes (2024-12-11) - Massive Parallel Agent Sweep

Deployed 116+ parallel agents to systematically fix remaining errors across 116 files.

**Key statistics:**
- Starting errors: 865 baselined
- Ending errors: 209 baselined
- Net reduction: 656 errors (76% in single session)
- Files touched: 116+

**Production files fixed (70+):**
- `l/search.py`, `l/advanced_lattice.py`, `l/fusion.py`, `l/persistence.py`, `l/embedders.py`, `l/graph_search.py`
- `m/cartographer.py`, `m/prospective.py`, `m/memory_budget.py`, `m/dgent_backend.py`, `m/tiered.py`
- `n/tap.py`, `n/bard.py`, `n/historian.py`, `n/chronicle.py`, `n/dgent_store.py`
- `r/refinery.py`, `r/advanced.py`, `r/dspy_backend.py`, `r/integrations.py`
- `t/law_validator.py`, `t/permissions.py`, `t/executor.py`
- `p/strategies/lazy_validation.py`, `p/cli.py`
- `g/types.py`, `g/tongue.py`, `g/forge_integration.py`, `g/cli.py`
- `d/graph.py`, `d/infra_backends.py`, `d/redis_agent.py`, `d/persistent.py`, `d/stream.py`
- `w/bus.py`, `w/protocol.py`, `w/observer.py`
- `b/compression_economy.py`, `b/fiscal_constitution.py`, `b/grammar_insurance.py`, `b/semantic_inflation.py`
- `psi/integrations.py`, `psi/engine.py`
- `bootstrap/umwelt.py`, `bootstrap/telemetry.py`, `bootstrap/types.py`
- And many more...

**Test files fixed (46+):**
- `test_learning.py`, `test_factory_integration.py`, `test_dna_lifecycle.py`
- `test_types.py`, `test_phase7.py`, `test_embedders.py`, `test_j_forge_integration.py`
- `test_pattern_inference.py`, `test_infra_backends.py`, `test_library.py`
- `test_semantic_inflation.py`, `test_factory_pipeline.py`, `test_umwelt.py`
- `test_cortex_dashboard.py`, `test_advanced_lattice.py`, `test_demon.py`
- `test_bicameral.py`, `test_safety.py`, `test_search.py`, `test_law_validator.py`
- And many more...

**Key patterns applied:**
- Add `from __future__ import annotations` to all files
- Add `-> None` to all `__init__`, `__post_init__`, test functions
- Add generic type parameters (`dict[str, Any]`, `list[Any]`, `Generator[T, None, None]`)
- Add `assert x is not None` for type narrowing before Optional access
- Use `isinstance(result, Ok)` for Result union-attr narrowing
- Remove unused `# type: ignore` comments that became obsolete
- Add `# type: ignore[arg-type]` for intentional mock mismatches in tests
- Add `# type: ignore[comparison-overlap]` for intentional enum comparisons

### Phase 10 Fixes (2024-12-11) - Parallel Agent Sweep

Used 40+ parallel agents to fix high-error files systematically. Fixed 40 files:

**Production files (24):**
- `law_validator.py`, `t/registry.py`, `bootstrap_witness.py`, `l/registry.py`
- `gravity.py`, `observable.py`, `axiological.py`
- `queryable.py`, `tongue.py`, `contract_validator.py`
- `graph.py`, `infra_backends.py`, `lattice.py`, `jung.py`
- `dspy_backend.py`, `r/integrations.py`, `vector_holographic.py`
- `j/cli.py`, `dgent_store.py`, `p/cli.py`, `n/integrations.py`, `n/store.py`

**Test files (16):**
- `test_o_gent.py`, `test_stream.py`, `test_noosphere.py`
- `test_refinery.py`, `test_interceptors.py`
- `test_memory_recall_e2e.py`, `test_memory_pipeline_integration.py`
- `test_phase3_pipeline.py`, `n/test_integrations.py`, `test_executor.py`
- `test_cartography.py`, `test_d_gent_finalization.py`, `test_bus.py`
- `test_vector_backend.py`, `test_semantic.py`, `test_search.py`
- `test_catalog.py`, `test_persistent.py`, `test_persistent_hypothesis.py`

Key patterns applied:
- Add generic type parameters (`HolographicMemory[str]`, `RefineryAgent[Any, Any]`, etc.)
- Add `# type: ignore[operator]` for intentional composition tests
- Add `isinstance()` checks for Result type narrowing (Ok vs Err)
- Fix fixture return types with `Generator[T, None, None]`
- Add null checks with `assert x is not None` before Optional access
- Remove unused `# type: ignore` comments after fixing source issues

### Phase 9 Fixes (2024-12-11) - Major Cleanup

Systematic fixing of 50+ test and production files. Key patterns:
- Add `from __future__ import annotations` to all files
- Add `-> None` to all test functions and `__init__` methods
- Add fixture return type annotations
- Add type annotations to fixture parameters in test methods
- Add `assert x is not None` for type narrowing before Optional access
- Add generic type parameters (`dict[str, Any]`, `list[Any]`, etc.)
- Fix `no-any-return` with `bool()`, `int()`, `float()`, `str()` or `cast()`

Files fixed include:
- Production: `l/cli.py`, `g/cli.py`, `w/cli.py`, `g/forge_integration.py`, `m/cartographer.py`, `d/queryable.py`, etc.
- Tests: 50+ test files across all agent directories

### Phase 7 Fixes (2024-12-11)

Key files fixed:
- `agents/t/_tests/test_t_phase3.py` - Agent base class fixes, name properties, 58 → 0 errors
- `agents/t/_tests/test_p_integration.py` - Result value null checks, 49 → 0 errors
- Various production files: `no-any-return` fixes, unused ignores cleanup

Key patterns applied:
- Import Agent from `bootstrap.types` (not `agents.a`)
- Agent classes need `@property def name(self) -> str:` not instance variable
- Add `assert result.value is not None` after `assert result.success` for mypy type narrowing
- Use explicit type annotations for variable assignments to fix `no-any-return`
- Remove unused `# type: ignore` comments
- Fix variable shadowing (e.g., `result` reuse in loops)

### Phase 6 Fixes (2024-12-11)

Key files fixed:
- `agents/d/_tests/test_phase3.py` - Full fixture + test method annotations, 66 → 0 errors
- `agents/m/test_m_gents.py` - Comprehensive type annotations, 62 → 0 errors

Key patterns applied:
- Add `from __future__ import annotations` for forward references
- Add explicit generic type parameters: `VolatileAgent[dict[str, Any]]`
- Add type annotations to all fixture parameters
- Add return type annotations to all fixtures: `-> TransactionalDataAgent[dict[str, Any]]`
- Use `# type: ignore[comparison-overlap]` for intentional mutation tests
- Use `# type: ignore[arg-type]` for API mismatches that are intentional in tests

### Phase 5 Fixes (2024-12-11)

Key files fixed:
- `agents/r/_tests/test_advanced.py` - Fixture annotations, 45+ errors
- `agents/t/registry.py` - `Tool[Any, Any]` generic params, 14 errors
- `agents/g/tongue.py` - `InterpreterConfig` semantics, 14 errors
- `agents/l/embedders.py` - Return type casts, 6 errors
- `agents/l/fusion.py` - Loop variable types, 8 errors
- `agents/l/vector_backend.py` - Unused ignores, return types, 6 errors
- `agents/l/vector_db.py` - Generic params, var annotations, 6 errors
- `agents/d/observable.py` - `Change[Any]` type params, 3 errors

### Phase 8 Baseline Update (2024-12-11)

New untracked files added to baseline:
- `agents/i/terrarium_tui.py` - Terrarium TUI with Textual integration
- `agents/i/_tests/test_terrarium_tui.py` - Tests for Terrarium TUI

Production code fixes:
- `agents/d/observable.py`: `-> None` annotations for inner functions, `dict[str, Any]` type params

## Remaining Error Distribution (209 errors across 72 files)

Run this command to see current distribution:
```bash
cd impl/claude && uv run mypy --strict --explicit-package-bases agents/ bootstrap/ runtime/ 2>&1 | uv run mypy-baseline filter
```

Remaining errors are primarily in complex/generated files or require deeper architectural changes.

## Phase 1: Automated Test Function Annotations (~5,000 errors)

**Strategy**: Create script to add `-> None` to all test functions missing return types.

Target files (by error count):
1. `agents/m/test_m_gents.py` (293)
2. `agents/o/_tests/test_o_gent.py` (291)
3. `agents/i/_tests/test_semantic_field.py` (270)
4. `agents/r/_tests/test_advanced.py` (189)
5. `agents/b/_tests/test_jit_efficiency.py` (184)
... (25+ more test files with 80+ errors each)

**Automation approach**:
```python
# Pattern: def test_xxx(...): → def test_xxx(...) -> None:
# Pattern: async def test_xxx(...): → async def test_xxx(...) -> None:
```

## Phase 2: Source File Type Annotations (~500 errors)

Key source files needing attention:
- `agents/p/core.py` - Parser base class
- `agents/d/lens.py` - Missing dict type params
- `agents/d/queryable.py` - Any returns
- `agents/b/jit_efficiency.py` - Missing annotations
- `agents/p/strategies/*.py` - Various issues

## Phase 3: Generic Type Parameters (~200 errors)

- Replace `dict` → `dict[str, Any]`
- Replace `list` → `list[Any]`
- Replace `Callable` → `Callable[..., Any]`

## Phase 4: Complex Type Issues (~200 errors)

- Union attribute access (`union-attr`)
- Index type mismatches
- Return type overrides
- Liskov substitution violations

## Commands

```bash
# Check current errors
cd impl/claude && uv run mypy --strict --explicit-package-bases agents/ bootstrap/ runtime/ 2>&1 | uv run mypy-baseline filter

# Re-sync baseline after fixes
cd impl/claude && uv run mypy --strict --explicit-package-bases agents/ bootstrap/ runtime/ 2>&1 | uv run mypy-baseline sync
```
