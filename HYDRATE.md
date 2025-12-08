# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: 14 evolution improvements applied to bootstrap ✅
**Branch**: `main` (pushed, commit 798c8b9)
**Next**: Run evolution on `agents/` and `runtime/` modules

---

## Quick Start

```bash
cd /Users/kentgang/git/kgents
source .venv/bin/activate  # CRITICAL - always activate first
cd impl/claude
python evolve.py agents --dry-run --quick
```

**Verify venv**: `which python` should show `.../kgents/.venv/bin/python`

---

## Dec 8 Session: Evolution Applied

**14 improvements** incorporated across bootstrap modules:

| Module | Changes |
|--------|---------|
| **Id** | `__rlshift__`, `__rrshift__`, equality check relaxed |
| **Compose** | Either type for totality, decoupled refiner |
| **Types** | Iteration context for convergence |
| **Fix** | Proximity metric |
| **Judge** | Pure functions, immutable accumulator, principles delegation |
| **Contradict** | Circuit breaker, evidence tracking |
| **Ground** | Simplified (removed unused retry) |

**Bug fixes**: `evolve.py` verdict attribute, `ground.py` import path

---

## Next Priorities

1. **Evolution**: Run on `agents/` and `runtime/` modules
2. **Tests**: pytest for `agents/b/` (hypothesis.py, robin.py)
3. **Specs**: D-gents (Data), E-gents (Ethics/Evaluation)
4. **Package**: PyPI publish kgents-runtime

---

## Structure

```
kgents/
├── impl/claude/          # 27 modules
│   ├── bootstrap/        # 7 bootstrap agents (evolved)
│   ├── agents/           # A, B, C, H, K families
│   ├── runtime/          # LLM execution
│   └── evolve.py         # Evolution pipeline
├── spec/                 # Specifications
└── .venv/                # Must activate!
```

---

## Session Log

- **Dec 8**: 14 evolution improvements, bug fixes, HYDRATE.md cleanup
- **Dec 8 earlier**: Bootstrap Phase 6, evolution logging enhancements
- **Dec 7**: Type fixes, EvolutionAgent refactor, 100% pass rate
