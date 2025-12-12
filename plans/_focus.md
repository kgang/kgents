---
type: next-session-prompt
created: 2025-12-12
focus: Post-Flux Priorities
plans:
  - concept/lattice
  - void/entropy
  - concept/creativity (Tasks 2-4)
---

# Next Session: Post-Flux Priorities

> *"The Flux Functor is complete. Agents can now be alive."*

## Just Completed: Flux Functor

**261 tests** | Location: `impl/claude/agents/flux/`

The Flux Functor lifts agents from discrete state to continuous flow:
```
Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]
Where Flux[T] = AsyncIterator[T]
```

Key features:
- Event-driven streams (no polling in core)
- `start()` returns `AsyncIterator[B]` (Living Pipelines)
- `invoke()` on FLOWING = perturbation (not bypass)
- Living Pipelines via `|` operator
- Ouroboric feedback configurable
- Entropy physics integration

---

## Track 1: concept/lattice (40% complete)

**Priority**: HIGH (foundational for autopoiesis)
**Effort**: Medium
**Unblocked**: Yes

### Goal
Wire lattice validation to `concept.*.define`. No concept can be created without lineage.

### Files to Modify
```
protocols/agentese/contexts/concept.py  # Add define_concept()
agents/l/lattice.py                     # Verify integration points
```

### Exit Criteria
```python
# This should FAIL:
await logos.invoke("concept.orphan.define", spec="...")
# → LineageError: Concepts cannot exist ex nihilo.

# This should WORK:
await logos.invoke(
    "concept.new_agent.define",
    spec="A specialized agent type",
    extends=["concept.agent"],
)
```

---

## Track 2: void/entropy (Research Complete, Now Unblocked)

**Priority**: HIGH (Flux enables this)
**Effort**: Medium
**Unblocked**: YES - Flux provides the stream infrastructure!

### Goal
Wire Metabolism to Flux. When a FluxAgent processes events, it should consume metabolic energy.

### Key Integration Points
```python
# In FluxAgent._process_flux():
async for event in self._merged_source(source):
    # Consume metabolic energy (NEW)
    if self._metabolism:
        await self._metabolism.consume(event)

    # Existing entropy check
    if not self._can_continue():
        self._collapse_to_ground()
        break
```

### Files to Create/Modify
```
agents/flux/metabolism.py          # FluxMetabolism adapter
protocols/agentese/metabolism/     # Already exists (36 tests)
```

---

## Track 3: Creativity Tasks 2-4 (90% complete)

**Priority**: LOW (polish work)
**Effort**: Low per task

### Task 2: Bidirectional Skeleton (PAYADOR)
When texture reveals structural issues, rewrite the skeleton.

### Task 3: Wire Pataphysics to LLM
Connect `void.pataphysics.solve` to actual LLM hallucination.

### Task 4: Auto-Wire Curator Middleware
Make WundtCurator optional middleware that can be enabled globally.

---

## Quick Start Commands

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Verify Flux tests pass
python -m pytest agents/flux/_tests/ -v

# Track 1: Lattice
python -m pytest protocols/agentese/lattice/_tests/ -v

# Track 2: Metabolism
python -m pytest protocols/agentese/metabolism/_tests/ -v

# Full verification
uv run mypy .
python -m pytest -m "not slow" -q
```

---

## Recommended Order

1. **Track 2 (void/entropy)** - Highest impact, Flux enables this NOW
2. **Track 1 (Lattice)** - Foundational, long dormant
3. **Track 3 (Creativity)** - Polish work, can be incremental

---

## Flux Implementation Summary (for reference)

Files created:
```
agents/flux/
├── __init__.py
├── state.py            # FluxState enum
├── errors.py           # FluxError, FluxStateError, FluxPipelineError
├── config.py           # FluxConfig dataclass
├── perturbation.py     # Perturbation handling
├── agent.py            # FluxAgent (the core)
├── functor.py          # Flux.lift() / Flux.unlift()
├── pipeline.py         # FluxPipeline, | operator
├── sources/
│   ├── __init__.py
│   ├── base.py         # FluxSource protocol
│   ├── events.py       # from_iterable, empty, single, repeat, range_source
│   ├── periodic.py     # periodic, countdown, tick
│   └── merged.py       # merged, filtered, mapped, batched, take, skip
└── _tests/
    ├── test_state.py
    ├── test_errors.py
    ├── test_config.py
    ├── test_perturbation.py
    ├── test_functor.py
    ├── test_agent.py
    ├── test_pipeline.py
    ├── test_sources.py
    └── test_integration.py
```

---

*"The noun is a lie. There is only the rate of change."*
