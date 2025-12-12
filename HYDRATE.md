# HYDRATE.md — kgents Context Seed

> *"To read is to invoke. There is no view from nowhere."*

## Agent Boundaries

**Before editing any meta file, read `plans/_focus.md`** — Kent's intent. Never overwrite.

| File | Agent May | Agent Must NOT |
|------|-----------|----------------|
| `plans/_focus.md` | Read | Write |
| `plans/_forest.md` | Regenerate | Add prose |
| `plans/meta.md` | Append (one line) | Expand (50-line cap) |
| `HYDRATE.md` | Update facts | Bloat |

---

## Status

**Tests**: 8,714+ | **Mypy**: Strict (0 errors) | **Branch**: `main`

---

## AGENTESE (The Five Contexts)

```
world.*    — External (entities, tools)
self.*     — Internal (memory, state)
concept.*  — Abstract (platonics, logic)
void.*     — Accursed Share (entropy, slop)
time.*     — Temporal (traces, forecasts)
```

**Aspects**: `manifest` • `witness` • `refine` • `sip` • `tithe` • `lens` • `define`

---

## Active Plans (see `plans/_forest.md`)

| Plan | Progress | Next |
|------|----------|------|
| `concept/lattice` | 60% | Wire to `concept.*.define` |
| `concept/creativity` | 90% | Tasks 2-4 |

## Completed (Recent)

- **Flux Functor** — `agents/flux/` (261 tests): Living Pipelines, perturbation
- **Metabolism v1** — `protocols/agentese/metabolism/` (36 tests)
- **I-gent v2.5** — Phases 1-5 (137 tests)
- **Reflector Pattern** — Terminal/Headless/Flux (36 tests)

---

## Commands

```bash
cd impl/claude && uv run mypy .       # Must pass
cd impl/claude && uv run ruff check   # Must pass
pytest -m "not slow" -q               # Must pass
```

---

## Agent Registry (23 agents)

A(abstract) B(economics) C(category) D(memory) E(evolution) F(futures) G(generation) H(dialectics) I(interface) J(judgment) K(simulacra) L(registry) M(cartography) N(narrative) O(observation) P(personality) Ψ(metaphor) Q(quantum) R(resilience) T(testing) U(utility) W(wire) **Flux**(streams)

---

## Gotchas

- Python 3.12: `Generic[A]` + `TypeVar`, not `class Foo[A]:`
- Imports: Prefer absolute (`from agents.x import Y`)
- Cross-agent: `*_integration.py` or SemanticField
- Foundational modules: `shared`, `a`, `d`, `l`, `c`

---

## Deep Dive

For details beyond this seed:
- **Forest canopy**: `plans/_forest.md`
- **Human intent**: `plans/_focus.md`
- **Learnings**: `plans/meta.md`
- **Status matrix**: `plans/_status.md`
- **Principles**: `spec/principles.md`

---

*Compress, don't expand. If this file exceeds 100 lines, prune it.*
