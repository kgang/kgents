# impl/ Improvement Plan

Generated: 2025-12-08 via systematic `evolve.py` analysis

---

## Executive Summary

Comprehensive static analysis of 50+ modules in `impl/claude/` reveals **systematic refactoring opportunities** across 4 priority tiers. The codebase has grown organically with J-gents/T-gents/E-gents, creating several large files (1000+ lines) with functions exceeding 100 lines.

**Key Metrics:**
- Total: ~27,000 lines across impl/claude/
- Files >500 lines: 18
- Functions >50 lines: 45+
- Classes >10 methods: 8

---

## Priority 1: Meta-Evolution (evolve.py)

**File:** `evolve.py` (1,286 lines) - The largest file, self-improvement target

### H1: Decompose EvolutionPipeline class (19 methods → 4 agents)

**Problem:** `EvolutionPipeline` has 19 methods, violating the morphism principle.

**Solution:** Extract into composable E-gent agents:
```
EvolutionPipeline → HypothesisStage >> ExperimentStage >> TestStage >> IncorporateStage
```

| Current Method | New Agent | Lines |
|----------------|-----------|-------|
| `generate_hypotheses` | `HypothesisAgent` | 83 |
| `experiment`, `_generate_improvement` | `ExperimentAgent` | 86 |
| `test`, `_test_with_recovery` | `TestRecoveryAgent` | 109 |
| `judge_experiment`, `synthesize` | `JudgeAgent` | ~80 |
| `incorporate` | Already exists | - |

**Impact:** Reduces evolve.py by ~400 lines, improves testability.

### H2: Extract `show_suggestions` into SuggestionAgent (56 lines)

**Current:** 56-line function with embedded AST analysis + formatting logic.

**Proposed:**
```python
# agents/e/suggestion.py
class SuggestionAgent(LLMAgent[SuggestInput, list[Suggestion]]):
    """Generate improvement suggestions without experiments."""
```

### H3: Extract `run_safe_evolution` into SafeEvolutionOrchestrator (102 lines)

**Current:** 102-line monolithic function handling safe self-evolution.

**Proposed:** Move to `agents/e/safe_evolution.py` alongside existing `SelfEvolutionAgent`.

### H4: Lazy imports refactor

**Current:** 57 imports at module top, many conditional.

**Proposed:** Use `typing.TYPE_CHECKING` + lazy factory pattern for runtime, agents, bootstrap imports.

---

## Priority 2: Runtime Layer

**File:** `runtime/base.py` (635 lines)

### H5: Extract JSON repair utilities (250 lines)

**Current:** `robust_json_parse`, `_repair_json`, `_extract_field_values`, `parse_structured_sections` are utility functions.

**Proposed:** New module `runtime/json_utils.py`:
```python
# runtime/json_utils.py
def robust_json_parse(response: str, allow_partial: bool = True) -> dict
def repair_json(text: str, opener: str, closer: str) -> str
def extract_field_values(text: str, fields: list[str]) -> dict
def parse_structured_sections(response: str, section_names: list[str]) -> dict
```

### H6: Consolidate Result types with bootstrap

**Current:** `Success`, `Error`, `Result` types duplicate patterns in `bootstrap/types.py`.

**Proposed:** Move to shared location or use bootstrap's Either pattern.

---

## Priority 2: E-gents Layer

### H7: agents/e/prompts.py (762 lines)

**Long functions:**
- `build_improvement_prompt`: 137 lines
- `extract_api_signatures`: 62 lines

**Proposed:** Split into:
- `prompts/base.py` - Core prompt templates
- `prompts/improvement.py` - Improvement-specific prompts
- `prompts/analysis.py` - API signature extraction

### H8: agents/e/parser.py (687 lines, CodeParser with 11 methods)

**Long functions:**
- `_parse_with_repair`: 74 lines
- `_parse_code_block`: 72 lines

**Proposed:** Extract parsing strategies:
```python
# agents/e/parsing/
├── strategies.py  # Strategy pattern for different response formats
├── repair.py      # JSON repair logic
└── extractors.py  # Code block extraction
```

### H9: agents/e/safety.py (656 lines)

**Long functions:** `invoke` (73 lines), `_evolve_once` (58 lines)

**Proposed:** Inline documentation + minor decomposition.

---

## Priority 3: J-gents Layer

### H10: agents/j/sandbox.py (460 lines)

**Long functions:**
- `execute_in_sandbox`: 150 lines (!)
- `build_namespace`: 103 lines

**Proposed:** Split into:
- `sandbox/executor.py` - Execution logic
- `sandbox/namespace.py` - Namespace building
- `sandbox/validation.py` - Safety validation

### H11: agents/j/chaosmonger.py (620 lines)

**Long function:** `analyze_stability` (93 lines)

**Proposed:** Extract sub-analyzers:
```python
ComplexityAnalyzer  # Cyclomatic complexity
DependencyAnalyzer  # Import graph
NestingAnalyzer     # Control flow depth
```

### H12: agents/j/meta_architect.py (607 lines, 13 methods)

**Long functions:** `_generate_*` methods (51-55 lines each)

**Proposed:** Template-based generation pattern to reduce duplication.

---

## Priority 3: B-gents Layer

### H13: agents/b/robin.py (570 lines)

**Long function:** `invoke` (107 lines)

**Proposed:** Decompose into:
```python
_prepare_research_context()
_generate_hypotheses()
_rank_and_filter()
```

### H14: agents/b/hypothesis.py (460 lines)

**Long function:** `parse_response` (112 lines)

**Proposed:** Extract hypothesis parsing into dedicated parser class.

---

## Priority 4: Shared Infrastructure

### H15: agents/shared/ast_utils.py (610 lines, ASTAnalysisKit with 12 methods)

**Long functions:**
- `extract_classes`: 72 lines
- `extract_functions`: 54 lines

**Proposed:** Already well-structured, but could benefit from:
- Visitor pattern for AST traversal
- Caching decorator for repeated analysis

### H16: bootstrap/types.py (510 lines)

**Status:** Core types, well-structured. No immediate changes needed.

### H17: bootstrap/judge.py (419 lines)

**Long function:** `finalize` (51 lines)

**Status:** Acceptable complexity for judge logic.

---

## Implementation Order

### Phase A: Quick Wins (1-2 sessions)

1. **H5**: Extract `runtime/json_utils.py` (no behavior change)
2. **H4**: Lazy imports in `evolve.py`
3. **H2**: Extract `SuggestionAgent`

### Phase B: Core Refactoring (2-3 sessions)

4. **H1**: Decompose `EvolutionPipeline`
5. **H7**: Split `prompts.py`
6. **H10**: Split `sandbox.py`

### Phase C: Deep Refactoring (3-4 sessions)

7. **H8**: Refactor `parser.py`
8. **H11**: Decompose `chaosmonger.py`
9. **H13**: Refactor `robin.py`

### Phase D: Polish

10. **H3, H6, H9, H12, H14, H15**: Remaining items

---

## Validation Strategy

For each improvement:

1. **Tests pass:** `python -m pytest -v`
2. **Type check:** `mypy --strict` on modified files
3. **Self-test:** Run `python evolve.py test` post-change
4. **Line count delta:** Net reduction in affected files

---

## Estimated Impact

| Metric | Current | Target |
|--------|---------|--------|
| Files >500 lines | 18 | 10 |
| Functions >50 lines | 45+ | <20 |
| Classes >10 methods | 8 | 3 |
| evolve.py lines | 1,286 | <800 |

---

## Next Steps

1. Review this plan
2. Run `python evolve.py meta --safe-mode --dry-run` to validate meta-improvements
3. Begin with Phase A quick wins
4. Update HYDRATE.md after each phase
