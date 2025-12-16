# HYDRATE.md — The Seed

> *"To read is to invoke. There is no view from nowhere."*

## Principles

Tasteful • Curated • Ethical • Joy-Inducing • Composable • Heterarchical • Generative

---

## AGENTESE (Five Contexts)

`world.*` `self.*` `concept.*` `void.*` `time.*`
**Aspects**: `manifest` • `witness` • `refine` • `sip` • `tithe` • `lens` • `define`

---

## Built Systems (USE THESE!)

| System | Module | What It Does |
|--------|--------|--------------|
| **AGENTESE** | `protocols/agentese/` | Verb-first ontology: Logos resolver, path parser, JIT compiler, wiring |
| **PolyAgent** | `agents/poly/` | State-dependent agents: 17 primitives (MANIFEST, WITNESS, SIP, TITHE...) |
| **Operad** | `agents/operad/` | Composition grammar: AGENT_OPERAD, SOUL_OPERAD, CLI/Test algebras |
| **Sheaf** | `agents/sheaf/` | Emergence: KENT_SOUL glues 6 local souls (aesthetic, joy, gratitude...) |
| **Flux** | `agents/flux/` | Stream processing: `Agent[A,B] → Agent[Flux[A], Flux[B]]` |
| **Town** | `agents/town/` | Multi-agent sim: CitizenPolynomial, TownOperad, k-clique coalitions |
| **K-gent** | `agents/k/` | Soul middleware: LLM dialogue, hypnagogia, garden, gatekeeper |
| **M-gent** | `agents/m/` | Holographic memory: crystals, cartography, stigmergy, routing |
| **Reactive** | `agents/i/reactive/` | Widgets: Signal/Computed/Effect, multi-target (CLI/TUI/marimo/JSON) |
| **N-Phase** | `protocols/nphase/` | Prompt compiler: YAML→prompt, state tracking, 11-phase lifecycle |
| **Terrarium** | `protocols/terrarium/` | Agent gateway: HolographicBuffer, PrismRestBridge, metrics |
| **API** | `protocols/api/` | FastAPI: `/v1/soul/governance`, `/v1/soul/dialogue`, auth |
| **Billing** | `protocols/billing/` | Stripe: subscriptions, customers, OpenMeter usage |
| **Licensing** | `protocols/licensing/` | Tiers: FREE/PRO/ENTERPRISE, feature flags, decorators |
| **Tenancy** | `protocols/tenancy/` | Multi-tenant: API keys, RLS context, usage events |
| **Atelier** | `agents/atelier/` | Creative workshop: streaming artisans, gallery, collaboration, exhibitions |

---

## Composition Patterns

```python
# 1. Agent composition
pipeline = AgentA >> AgentB >> AgentC

# 2. Flux lifting
flux_agent = Flux.lift(discrete_agent)
async for result in flux_agent.start(source): ...

# 3. AGENTESE paths
await logos.invoke("world.house.manifest", umwelt)

# 4. PolyAgent modes
poly = PolyAgent[S, A, B](state, directions, transition)

# 5. Widget projection
widget.to_cli() | widget.to_marimo() | widget.to_json()
```

---

## Three Phases

`SENSE → ACT → REFLECT → (loop)`
Full 11-phase: `docs/skills/n-phase-cycle/`

---

## Forest Protocol

| `_focus.md` | Human intent (never overwrite) |
| `_forest.md` | Canopy (regenerate) |
| `meta.md` | Learnings (append, 200-line cap) |
| `_epilogues/` | Session records |

---

## Seven Jewel Crown (Project KPIs)

| Jewel | Progress | Status |
|-------|----------|--------|
| **Brain** | 100% | ✅ COMPLETE - Production-ready |
| **Gestalt** | 70% | Elastic UI, OTEL, 146 tests |
| **Atelier** | 65% | Wave 2 synergies, 296 tests |
| **Coalition** | 55% | Brain+Gardener integration, 221 tests |
| **Gardener** | 40% | Gardener-Logos spec, 39 tests |
| **Park** | 40% | DirectorAgent, masks, 64 tests |
| **Domain** | 0% | Stub plan only |

**Crown Avg**: 53% | **Hero Path**: 70% (Brain+Gestalt+Gardener) | **Target**: 80% by Q2 2025

---

## Status

**Tests**: 18,600+ | **Reactive**: 627 tests | **Mypy**: 78 notes | **Web**: 9K LOC | Agents: A-Z + Flux/Atelier
**AGENTESE v3.1**: Self-doc (`help` aspect), WiredLogos in REPL, aliases (`/alias`), query API for `?`, docs/guides/
**Projection**: WidgetEnvelope (error boundary, streaming), 7 widgets + Gestalt (Topology/Governance), chrome, SSE, 4 surfaces
**Reactive Substrate**: COMPLETE — Error boundary in to_envelope(), streaming envelopes, property-based tests, <20% overhead

---

## Skills (docs/skills/)

agentese-path • building-agent • cli-command • flux-agent • polynomial-agent • plan-file • test-patterns • reactive-primitives • modal-scope-branching • turn-projectors • saas-patterns • agent-town-*

---

## Quick Commands

```bash
cd impl/claude && uv run pytest -q && uv run mypy .
```

---

*Lines: 90. Ceiling: 120.*
