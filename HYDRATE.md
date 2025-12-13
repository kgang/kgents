# HYDRATE.md — kgents Context Seed

> *"To read is to invoke. There is no view from nowhere."*

## Agent Boundaries

**Before editing any meta file, read `plans/_focus.md`** — Kent's intent. Never overwrite.

| File | Agent May | Agent Must NOT |
|------|-----------|----------------|
| `plans/_focus.md` | Read | Write Things Non-personal to Kent |
| `plans/_forest.md` | Regenerate | Add prose |
| `plans/meta.md` | Append (one line) | Expand (50-line cap) |
| `HYDRATE.md` | Update facts | Bloat |

---

## Status

**Tests**: 12,015 | **Mypy**: Strict (0 errors) | **Branch**: `main`

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
| `architecture/polyfunctor` | 100% | Ready to archive |
| `devex/trace-integration` | 25% | **P1** — Hardened, next: Ghost/Status/Dashboard |
| `devex/telemetry` | 0% | **P5** — OpenTelemetry export |

## Completed (Recent)

- **DevEx Dashboard** — `kg dashboard`, 4-panel TUI, graceful degradation, 50+ tests
- **DevEx Watch Mode** — `kg soul watch`, 5 heuristics (complexity, naming, patterns, tests, docs), 28 tests
- **DevEx Gallery** — MkDocs site, 6 examples (composition, functors, soul, streaming), GitHub Actions
- **OTEL Visibility** — K8s observability stack (Tempo/Prometheus/Grafana), `agentese.invoke` spans
- **DevEx Playground** — `kgents play`, 4 tutorials + REPL, 32 tests
- **Alethic Architecture** — 337 tests, Phases 1-6 (Functor, Halo, Archetypes, Projectors)

## Sprint Prompts

| Sprint | Prompt |
|--------|--------|
| Polyfunctor | `prompts/polyfunctor-realization.md` — Spec poly/operad/sheaf, migrate genera |
| DevEx | `prompts/devex-continuation.md` — Dashboard, watch-mode, gallery |
| Trace Integration | `prompts/trace-integration-hardening-continuation.md` — Hardened, next phases |

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
- Foundational modules: `shared`, `a`, `d`, `l`, `c`, `poly`, `operad`, `sheaf`

---

## Deep Dive

For details beyond this seed:
- **Functor Field Guide**: `docs/functor-field-guide.md` — Alethic Algebra without category theory
- **Operator's Guide**: `docs/operators-guide.md` — Scenarios, eigenvectors, stigmergic surface
- **Categorical Foundations**: `docs/categorical-foundations.md` — Category theory, principles
- **Forest canopy**: `plans/_forest.md`
- **Human intent**: `plans/_focus.md`
- **Principles**: `spec/principles.md`
- **Skills**: `plans/skills/` — patterns for common tasks
- **DevEx**: `/harden`, `/trace`, `/diff-spec`, `/debt`

---

*Compress, don't expand. If this file exceeds 125 lines, prune it immediately.*
