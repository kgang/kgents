# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Parser f-string repair added + diagnostic logging
**Branch**: `main` (uncommitted changes in parser.py, evolve.py)
**Mypy**: 0 errors (55 source files, strict)
**Evolution**: Syntax errors 75% → 0%, Type errors remain at 75%

---

## This Session: Results

Ran `evolve meta --auto-apply` and analyzed failure patterns:

### Key Finding: Syntax Error Repair Works!

| Before Repair | After Repair |
|---------------|--------------|
| 3 syntax errors (75%) | 0 syntax errors |
| 1 type error (25%) | 3 type errors (75%) |
| 0 passed/held | 1 HELD (productive tension!) |

### Changes Made

1. **parser.py** - Added `_repair_truncated_strings()` + `_parse_with_repair()`
   - Closes unclosed triple-quoted f-strings
   - New `ParseStrategy.REPAIRED` enum value
2. **evolve.py** - Added `failed_experiments` to JSON output
   - Captures hypothesis, error, and test_results for diagnosis

### Root Cause of Type Errors

LLM hallucinates APIs that don't exist:
- `CodeModule.code` (should be `path`)
- `ExperimentStatus.REJECTED` (doesn't exist)
- `.run()` method (should be `.invoke()`)
- Wrong constructor args for `AgentContext`, `TestInput`, `JudgeInput`

**Next step**: Add API stubs to prompt context (Phase 2.5a.2)

---

## Next Session: Start Here

### Option 1: Add API Stubs to Prompts

Enhance `prompts.py` to include actual API signatures:
```python
# In build_prompt_context(), extract and format:
# - Dataclass field definitions
# - Function signatures from imported modules
# - Enum values
```

### Option 2: Wire Recovery Layer

Phase 2.5c modules exist but need integration:
- `retry.py`: Call on failures
- `fallback.py`: When retries exhausted
- `error_memory.py`: Track failure patterns

### Quick Retest

```bash
cd /Users/kentgang/git/kgents && source .venv/bin/activate && cd impl/claude
python evolve.py meta --auto-apply
```

---

## What Exists

**agents/e/parser.py** - Multi-strategy code extraction + f-string repair
**agents/e/validator.py** - Pre-mypy schema validation
**agents/e/repair.py** - AST-based auto-fixes
**agents/e/retry.py** - Failure-aware prompt refinement
**agents/e/fallback.py** - Progressive simplification
**agents/e/error_memory.py** - Failure pattern learning
**agents/e/prompts.py** - Rich context building (needs API stubs)
**agents/e/preflight.py** - Module health validation

---

## Session Log

**Dec 8 PM (current session)**: 53e073b - Exported Phase 2.5c components from agents/e
  - Updated __init__.py to export retry, fallback, error_memory modules
  - Created test_recovery_layer.py with 20/20 passing tests
  - Phase 2.5c implementation complete, ready for integration
**Dec 8 PM**: F-string repair in parser.py, diagnostic logging
**Dec 8 PM**: dd32fa7 - Phase 2.5c Recovery Layer
**Dec 8 PM**: d7d3e34 - Phase 2.5b Parsing Layer
**Dec 8 PM**: 0a7a751 - Fixed all mypy --strict errors
**Dec 8 PM**: 1ae1e78 - Phase 2.5a Prompt Engineering Layer

---
