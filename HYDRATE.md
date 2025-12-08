# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Phase 2.5c COMPLETE - Recovery layer integrated + T-gents created ✅
**Branch**: `main` (uncommitted: evolve.py + agents/t/ + spec/t-gents/)
**Mypy**: 0 errors (evolve.py type checks pass)
**Test results**: Recovery layer validated with test_recovery_layer.py
**Next**: Test in production + commit changes

---

## This Session: Phase 2.5c Integration + T-gents Creation (2025-12-08)

### Completed ✅

**1. Recovery Layer Integrated into evolve.py**

Added to `EvolveConfig` (lines 150-154):
```python
enable_retry: bool = True
max_retries: int = 2
enable_fallback: bool = True
enable_error_memory: bool = True
```

Added to `EvolutionPipeline.__init__()` (lines 195-203):
```python
self._retry_strategy = RetryStrategy(RetryConfig(...))
self._fallback_strategy = FallbackStrategy(FallbackConfig(...))
self._error_memory = ErrorMemory()
```

New method `_test_with_recovery()` (lines 608-717):
- Tests initial experiment
- Records failures in error memory with categorization
- Attempts retry with refined prompts (configurable max_retries)
- Falls back to minimal/type-only/docs strategies
- Returns (success, final_experiment) tuple

Updated `_process_module()` (lines 748-779):
- Replaces simple test() with _test_with_recovery()
- Uses successful retry/fallback experiments
- Records comprehensive failure details

**2. T-gents (Test-gents) Framework Created**

New directory: `impl/claude/agents/t/`
- `failing.py`: FailingAgent with configurable error types
- `mock.py`: MockAgent for pre-configured outputs
- `__init__.py`: Exports both agents

New spec: `spec/t-gents/README.md`
- Full specification for T-gents genus
- FailingAgent and MockAgent docs
- Composability examples
- Future T-gents roadmap

**3. Recovery Layer Test Suite**

New file: `test_recovery_layer.py`
- Test 1: Retry strategy (fail 2x → succeed)
- Test 2: Error memory pattern tracking
- ✅ All tests passing!
- Demonstrates T-gents + recovery layer working together

### Integration Verification

Type checking:
```bash
MYPYPATH=/Users/kentgang/git/kgents/impl/claude python -m mypy evolve.py
# Result: 0 errors ✓
```

Test suite:
```bash
python test_recovery_layer.py
# Result: ALL TESTS COMPLETE! ✓
```

---

## Previous: Phase 2.5a.2 - API Stub Extraction

### Completed (commit 85c566d)

Enhanced `impl/claude/agents/e/prompts.py` with API stub extraction to prevent LLM hallucinations:

**New Functions:**
- `extract_dataclass_fields()` - Extracts field definitions from dataclasses
- `extract_enum_values()` - Extracts enum member names
- `extract_api_signatures()` - Resolves imports and extracts API signatures
- `_extract_sigs_from_file()` - Helper to extract from specific files

**Updated:**
- `PromptContext` - Added `dataclass_fields`, `enum_values`, `imported_apis` fields
- `build_prompt_context()` - Populates API stub fields
- `build_improvement_prompt()` - Displays "API Reference" section with exact signatures

### API Reference Section

LLM prompts now include exact API signatures:
```
## API Reference (USE THESE EXACT SIGNATURES)

### Dataclass Constructors
  @dataclass CodeModule(name: str, category: str, path: Path)

### Enum Values
  ExperimentStatus: PENDING, RUNNING, PASSED, FAILED, HELD

### Imported Module APIs
  CodeModule fields: name: str, category: str, path: Path
  Agent.invoke: async def invoke(self, input: A) -> B

CRITICAL: Common mistakes to AVOID:
  - ❌ CodeModule.code → ✓ CodeModule.path
  - ❌ ExperimentStatus.REJECTED → ✓ PENDING/RUNNING/PASSED/FAILED/HELD
  - ❌ agent.run() → ✓ agent.invoke()
```

### Reverted Bad Commit

- Commit `0d511c0` accidentally deleted all of evolve.py → Reverted in `f976a09`
- Working tree clean after revert

---

## Next Session: Start Here

### Priority 1: Validate Recovery in Production ⚡

Test recovery layer with actual evolution runs:
```bash
# Run with higher hypothesis count to trigger failures
python evolve.py meta --hypotheses=5 --auto-apply

# Monitor recovery effectiveness in logs:
grep -E "Retry|Fallback|recovery" .evolve_logs/evolve_*.log
```

**Metrics to track:**
- % experiments passing on first try (baseline)
- % experiments recovering via retry (target: >30%)
- % experiments recovering via fallback (target: >10%)
- Total incorporation rate (target: >70%, was ~30-50%)
- Error memory pattern accumulation

### Priority 2: Commit Recovery Layer + T-gents

Once validated:
```bash
git status
git add evolve.py agents/t/ test_recovery_layer.py
git add spec/t-gents/ HYDRATE.md
git commit -m "feat: Integrate Phase 2.5c recovery layer + create T-gents

- Wire retry/fallback/error_memory into evolve.py pipeline
- Add T-gents (Test-gents) framework for controlled testing
- Create FailingAgent and MockAgent for test scenarios
- Add test_recovery_layer.py demonstrating recovery
- Write spec/t-gents/README.md specification
- Update HYDRATE.md with Phase 2.5c completion

Changes:
- evolve.py: Add recovery configuration + _test_with_recovery()
- agents/t/: New test agent genus
- test_recovery_layer.py: Recovery layer test suite"
```

### Priority 3: Expand T-gents Ecosystem

Add more test utilities to agents/t/:
- **DelayAgent**: Configurable delays for async testing
- **CounterAgent**: Track invocation counts
- **SpyAgent**: Record inputs/outputs for assertions
- **FlakyAgent**: Random failures for resilience testing
- **ValidationAgent**: Assert expected outputs

### Priority 4: Implement J-gents (Optional)

New untracked directory: `impl/claude/agents/j/`
See `spec/j-gents/JGENT_SPEC_PLAN.md` for Phase 1 plan

---

## What Exists (Phase 2.5 Layers)

**Layer 1: Prompt Engineering** (prompts.py) ✅ Complete
- Type-aware prompting with API stubs
- Dataclass field extraction
- Enum value extraction
- Imported API signature extraction

**Layer 2: Parsing** (parser.py) ✅ Complete
- Multi-strategy code extraction
- F-string repair for truncated outputs
- Parse error recovery

**Layer 3: Recovery & Learning** (retry.py, fallback.py, error_memory.py) ✅ Complete & Integrated
- Failure-aware prompt refinement with refined prompts
- Progressive simplification fallbacks (minimal → type → docs)
- Failure pattern tracking across sessions
- **FULLY INTEGRATED** into evolution pipeline (evolve.py:608-813)

**Other E-gent Tools:**
- validator.py - Pre-mypy schema validation
- repair.py - AST-based auto-fixes
- preflight.py - Module health validation
- ast_analyzer.py - Code structure analysis

---

## Session Log

**Dec 8 PM**: UNCOMMITTED - Phase 2.5c recovery layer + T-gents complete
  - Integrated retry/fallback/error_memory into evolve.py
  - Created T-gents (Test-gents) framework + spec
  - Added FailingAgent, MockAgent for controlled testing
  - Created test_recovery_layer.py test suite (passing)
  - Wrote spec/t-gents/README.md full specification
  - Updated HYDRATE.md with completion status

**Dec 8 PM**: c7fa76e - Updated HYDRATE.md for Phase 2.5a.2 session
**Dec 8 PM**: f976a09 - Reverted bad commit that deleted evolve.py
**Dec 8 PM**: 85c566d - Phase 2.5a.2 API stub extraction (prompts.py)
**Dec 8 PM**: e8295d5 - Evolve pipeline refactor for AI agents
**Dec 8 PM**: 05b56aa - Fixed MYPYPATH in SandboxTestAgent
**Dec 8 PM**: 53e073b - Exported Phase 2.5c components

---

## Quick Commands

```bash
# Test mode (fast, safe, single module)
python evolve.py

# Check status (AI-friendly output)
python evolve.py status

# Get suggestions
python evolve.py suggest

# Self-improve with auto-apply
python evolve.py meta --auto-apply

# Full evolution
python evolve.py full --auto-apply
```

---
