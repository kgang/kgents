# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Priority 1 complete - API stubs working + tested
**Branch**: `main` (1 commit ahead: 0d511c0)
**Mypy**: 0 errors (55 source files, strict)
**Last test**: Meta evolution passed (1 improvement incorporated)
**New**: API stub extraction operational in prompts.py

---

## Latest: 0d511c0 (evolution self-improvement)

Meta evolution incorporated an improvement using new API stub extraction.
Previous commit: 85c566d (API stubs + J-gents spec)

## Earlier: 85c566d

- **J-gents spec** (`spec/j-gents/`): JIT Agent Intelligence
  - Reality classification (D/P/C trichotomy)
  - Entropy budgets & Chaosmonger stability
  - Lazy promises & accountability
  - Implementation plan with phases

- **Phase 2.5a.2**: API stub extraction prevents LLM hallucinations
  - `extract_dataclass_fields()`, `extract_enum_values()`, `extract_api_signatures()`
  - Prompts now show exact signatures to LLM

---

## Next Session: Start Here

### Priority 2: Wire Recovery Layer (formerly Priority 2)

Integrate Phase 2.5c recovery components into evolve.py `_process_module()`:
```python
# After test failure:
if not passed and should_retry(exp, validation_report):
    refined_prompt = retry_strategy.refine_prompt(...)
    # Re-run experiment
elif retry_exhausted:
    fallback_prompt = fallback_strategy.generate_minimal_prompt(...)
    # Run fallback experiment
```

### Option 2: Implement J-gents

Start Phase 1 from `spec/j-gents/JGENT_SPEC_PLAN.md`:
```bash
mkdir -p impl/claude/agents/j
# Create: reality.py, promise.py, chaosmonger.py, jgent.py
```

### Option 3: Full Evolution Test

Run full evolution to validate API stub impact:
```bash
cd /Users/kentgang/git/kgents/impl/claude
source ../../.venv/bin/activate  # IMPORTANT: Use kgents venv for mypy
python evolve.py all --auto-apply  # Compare failure rate to previous 24%
```

---

## What Exists

**J-gents Spec** (`spec/j-gents/`)
- README.md, reality.md, stability.md, lazy.md, JGENT_SPEC_PLAN.md

**Evolution Pipeline** (`agents/e/`)
- prompts.py - API stubs prevent hallucinations
- parser.py - F-string repair
- retry.py, fallback.py, error_memory.py - Recovery layer (not yet wired)

---

## Quick Commands

```bash
python evolve.py          # Test mode (fast, safe)
python evolve.py status   # Check state
python evolve.py suggest  # Get suggestions
python evolve.py meta --auto-apply  # Self-improve
```

---
