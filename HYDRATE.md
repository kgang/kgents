# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Phase 2.5a.2 complete - API stub extraction implemented
**Branch**: `main` (clean, pushed to c7fa76e)
**Mypy**: 0 errors (55 source files, strict)
**Next**: Test API stubs effectiveness + wire Phase 2.5c recovery layer

---

## This Session: Phase 2.5a.2 - API Stub Extraction

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

### Priority 1: Test API Stub Effectiveness

Run multiple experiments to measure impact:
```bash
cd /Users/kentgang/git/kgents/impl/claude
source ../../.venv/bin/activate
PYTHONPATH=/Users/kentgang/git/kgents/impl/claude python evolve.py meta --auto-apply
```

**Measure:**
- % of experiments with API hallucination errors (before: ~75%)
- Check logs for "API Reference" section presence
- Verify LLM sees correct signatures

### Priority 2: Wire Recovery Layer

Integrate Phase 2.5c into evolve.py:
```python
from agents.e import RetryStrategy, FallbackStrategy, ErrorMemory

# In _process_module() after test failure:
if not passed and should_retry(exp):
    refined_prompt = retry_strategy.refine_prompt(...)
    # Re-run experiment with refined prompt
elif retry_exhausted:
    fallback_prompt = fallback_strategy.generate_minimal_prompt(...)
    # Run fallback experiment
```

### Priority 3: Expand API Coverage

Add more types to extraction as hallucinations discovered:
- Add to `_extract_sigs_from_file()`: HypothesisInput, ASTAnalysisInput, etc.
- Monitor error patterns in failed experiments
- Update extraction lists incrementally

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

**Layer 3: Recovery & Learning** (retry.py, fallback.py, error_memory.py) ✅ Complete
- Failure-aware prompt refinement
- Progressive simplification fallbacks
- Failure pattern tracking
- **NOT YET INTEGRATED** into evolution pipeline

**Other E-gent Tools:**
- validator.py - Pre-mypy schema validation
- repair.py - AST-based auto-fixes
- preflight.py - Module health validation
- ast_analyzer.py - Code structure analysis

---

## Session Log

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
