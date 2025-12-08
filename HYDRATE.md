# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Spec-impl parity complete for K/C/H/E-gents + D-gents foundation ✅
**Branch**: `main` (pushed)
**Session**: 2025-12-08 - 4 parallel spec-impl fixes + D-gents Phase 1
**Achievement**: ~3000 lines added across 5 agent genera
**Next**: D-gents Phase 2 (PersistentAgent, LensAgent) or H7/H10 refactorings

---

## This Session: Spec-Implementation Parity (2025-12-08) ✅

### 4 Parallel Implementations Completed

| Agent | Gap | Solution | Lines |
|-------|-----|----------|-------|
| **K-gent** | evolution.py incomplete | ForgetHandler, ConflictDetector, ReviewHandler, BootstrapMode | +394 |
| **C-gents** | functor.py basic | ListAgent, AsyncAgent, LoggedAgent, PromiseAgent, law validators | +384 |
| **H-gents** | sparse implementations | BackgroundDialectic, Archetypes, CollectiveShadow, composition.py | +600 |
| **E-gents** | memory.py partial | Fuzzy matching (Levenshtein), get_failure_patterns(), get_stats() | +327 |

### D-gents Foundation (Bonus)

Created `impl/claude/agents/d/` with Phase 1 deliverables:
- `protocol.py` - DataAgent[S] async protocol
- `volatile.py` - VolatileAgent (in-memory state)
- `symbiont.py` - Symbiont pattern (pure logic + stateful memory)
- `errors.py` - StateError hierarchy
- `_tests/` - 15 passing tests

### Commits

```
071dcba fix: Regenerate uv.lock (remove stale claude-openrouter ref)
2af0c38 feat: Spec-impl parity for K/C/H/E-gents + D-gents foundation
0ab76b5 perf(bootstrap): Add bounded Fix history + test validation
```

---

## Next Session: Start Here

### Priority 1: D-gents Phase 2

Continue D-gent implementation per `DGENT_IMPLEMENTATION_PLAN.md`:
- `PersistentAgent` - File-backed state with JSON serialization
- `LensAgent` - Focused views into parent D-gent state
- Lens laws validation

### Priority 2: Remaining IMPROVEMENT_PLAN

| Task | File | Status |
|------|------|--------|
| H7 | `agents/e/prompts.py` (762 lines) | Split into prompts/{base,improvement,analysis}.py |
| H10 | `agents/j/sandbox.py` (460 lines) | Split into sandbox/{executor,namespace,validation}.py |

### Quick Verification

```bash
cd impl/claude
python -m pytest tests/ -v  # Should pass ~143 tests

# Verify new implementations
python -c "from agents.d import VolatileAgent, Symbiont; print('D-gents ✓')"
python -c "from agents.k.evolution import BootstrapMode, bootstrap_persona; print('K-gent ✓')"
python -c "from agents.c.functor import list_agent, logged; print('C-gents ✓')"
python -c "from agents.h import collective_shadow, background_dialectic; print('H-gents ✓')"
python -c "from agents.e.memory import EvolutionMemory; m = EvolutionMemory(); print('E-gents ✓')"
```

---

## Spec-Implementation Status

| Spec | Implementation | Status |
|------|---------------|--------|
| `spec/d-gents/` | `agents/d/` | Phase 1 ✅ (Phase 2 pending) |
| `spec/k-gent/evolution.md` | `agents/k/evolution.py` | ✅ Complete |
| `spec/c-gents/functors.md` | `agents/c/functor.py` | ✅ Complete |
| `spec/h-gents/` | `agents/h/` | ✅ Complete |
| `spec/e-gents/memory.md` | `agents/e/memory.py` | ✅ Complete |

---

## Architecture Summary

```
impl/claude/agents/
├── a/  # Abstract agents (skeleton, creativity)
├── b/  # Bio/Scientific (robin, hypothesis)
├── c/  # Category Theory (functor, monad, parallel, conditional)
├── d/  # Data Agents (NEW: volatile, symbiont)
├── e/  # Evolution (memory, parser, safety, prompts)
├── h/  # Hegelian (hegel, lacan, jung, composition)
├── j/  # JIT (jgent, sandbox, chaosmonger, meta_architect)
├── k/  # Kent simulacra (persona, evolution)
├── t/  # Testing (13 agents across 4 types)
└── shared/  # Common utilities (ast_utils)
```

---

## Test Suite Status

- **Total**: ~143 tests passing
- **J-gents**: 50/50 ✅
- **T-gents**: 75/75 ✅
- **Bootstrap**: All ✅
- **D-gents**: 15/15 ✅ (new)
