# impl/claude HYDRATE

**Last Updated:** 2025-12-08

## Current State

**Phase:** A (Quick Wins)
**Status:** H5 ✅ Complete | Proceeding with manual refactoring approach

## Recent Activity

### Session 2025-12-08 (This Session)
- ✅ **H5 Complete**: JSON utilities extracted to `runtime/json_utils.py` (commit cb98af8)
- ✅ Created HYDRATE.md to track implementation progress
- 📊 Reviewed IMPROVEMENT_PLAN.md priorities
- 🔍 Analyzed meta-evolution failures

### Meta-Evolution Attempts (Earlier Today)
- Ran `evolve.py meta --auto-apply` (3 attempts)
- Generated good hypotheses matching IMPROVEMENT_PLAN.md:
  - H3: Decompose EvolutionPipeline (19 methods → composable stages)
  - H4: Extract show_suggestions/show_status functions
  - H5: Lazy imports refactor
- **Result:** Timeouts and type errors in auto-generated code
- **Lesson:** Meta-evolution on evolve.py requires manual approach

## Implementation Progress (IMPROVEMENT_PLAN.md)

### Phase A: Quick Wins ⚡ In Progress
- [x] **H5**: Extract `runtime/json_utils.py` (250 lines from runtime/base.py) - ✅ **DONE** (commit cb98af8)
- [ ] **H2**: Extract `SuggestionAgent` from `show_suggestions` function - IN PROGRESS
- [ ] **H4**: Lazy imports in `evolve.py`

### Phase B: Core Refactoring (Not Started)
- [ ] **H1**: Decompose `EvolutionPipeline` (19 methods → 4 agents)
- [ ] **H7**: Split `prompts.py` (762 lines)
- [ ] **H10**: Split `sandbox.py` (460 lines)

### Phase C: Deep Refactoring (Not Started)
- [ ] **H8**: Refactor `parser.py` (687 lines)
- [ ] **H11**: Decompose `chaosmonger.py` (620 lines)
- [ ] **H13**: Refactor `robin.py` (570 lines)

### Phase D: Polish (Not Started)
- H3, H6, H9, H12, H14, H15

## Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Files >500 lines | 18 | 10 |
| Functions >50 lines | 45+ | <20 |
| Classes >10 methods | 8 | 3 |
| evolve.py lines | 1,286 | <800 |

## Next Session Priorities

**Recommended:** Continue with Phase A quick wins

### Option 1: H4 - Lazy Imports (Recommended)
**File:** `evolve.py` (1,286 lines)
**Task:** Refactor 57 imports to use `typing.TYPE_CHECKING` and lazy loading
**Impact:** Faster startup, better testability
**Approach:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.b.hypothesis import HypothesisEngine
    from agents.h.hegel import HegelAgent
    # ... other type-only imports

# Runtime imports in functions that use them
def _get_hypothesis_engine():
    from agents.b.hypothesis import HypothesisEngine
    return HypothesisEngine(...)
```

### Option 2: H2 - Extract SuggestionAgent
**File:** `evolve.py` lines 1005-1061 (56 lines)
**Task:** Extract `show_suggestions` into composable agent
**Note:** This might be over-engineering - consider simplifying instead

### Option 3: Skip to Phase B - H7 (prompts.py split)
**File:** `agents/e/prompts.py` (762 lines)
**Task:** Split into `prompts/base.py`, `prompts/improvement.py`, `prompts/analysis.py`
**Impact:** Better organization, clearer responsibilities
