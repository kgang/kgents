# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Phase 2.5a.2 complete - API stubs prevent hallucinations
**Branch**: `main` (uncommitted: `prompts.py`)
**Mypy**: 0 errors (55 source files, strict)
**Evolution**: Syntax errors 0%, API signatures now provided to LLM

---

## This Session: Phase 2.5a.2 - API Stub Extraction

### Completed Implementation

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

### API Reference Section in Prompts

LLM now receives exact API signatures:
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

### Impact

**Before:** LLM hallucinated `CodeModule.code`, `ExperimentStatus.REJECTED`, `agent.run()` → 75% type errors

**After:** LLM sees exact dataclass fields, enum values, method signatures in every prompt

### Next Steps

1. **Measure effectiveness**: Run multiple experiments to quantify type error reduction
2. **Phase 2.5c Integration**: Wire retry/fallback/error_memory into evolution pipeline  
3. **Expand coverage**: Add more types to extraction lists as hallucinations discovered

---

## Session Log

**Dec 8 PM (current)**: Phase 2.5a.2 - API stub extraction in prompts.py
  - Added extraction functions for dataclasses, enums, imported APIs
  - Enhanced prompts with "API Reference" section showing exact signatures
  - Handles multiple import patterns (agents.e, bootstrap.types, relative)
  - Tested: Correctly extracts CodeModule.path, ExperimentStatus values, Agent.invoke
**Dec 8 PM**: e8295d5 - Evolve pipeline refactor for AI agent ergonomics
**Dec 8 PM**: Full `evolve all --auto-apply`: 93 passed, 30 failed, 2 held
**Dec 8 PM**: 05b56aa - Fixed MYPYPATH in SandboxTestAgent
**Dec 8 PM**: 53e073b - Exported Phase 2.5c components

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

**Other E-gent Tools:**
- validator.py - Pre-mypy schema validation
- repair.py - AST-based auto-fixes
- preflight.py - Module health validation
- ast_analyzer.py - Code structure analysis

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
