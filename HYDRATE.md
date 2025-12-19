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

**Categorical**: `agents/poly/` (PolyAgent) • `agents/operad/` • `agents/sheaf/` • `agents/flux/`
**Semantics**: `protocols/agentese/` (Logos, parser, JIT, wiring)
**Services**: `services/` (Brain, Town, Gardener, Park, Atelier, Coalition, Gestalt, Chat)
**Simulation**: `agents/town/` (CitizenPolynomial, TownOperad, k-clique)
**Soul**: `agents/k/` (LLM dialogue, hypnagogia, garden, gatekeeper)
**Memory**: `agents/m/` (crystals, cartography, stigmergy)
**UI**: `agents/i/reactive/` (Signal/Computed/Effect → CLI/TUI/marimo/JSON)
**SaaS**: `protocols/api/` • `protocols/billing/` • `protocols/licensing/` • `protocols/tenancy/`

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

## Metaphysical Fullstack (AD-009)

```
Projection → Container → AGENTESE Protocol → Node → Service → Infrastructure
```

**Key Rules**:
- `services/` = Crown Jewels (Brain, Town, Park...) — domain logic, adapters, frontend
- `agents/` = Infrastructure (PolyAgent, Operad, Flux, D-gent) — categorical primitives
- **No explicit backend routes** — AGENTESE universal protocol IS the API
- Main website = elastic container (shallow passthrough for service projections)

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

## Seven Jewel Crown

| Jewel | % | Vision |
|-------|---|--------|
| Brain | 100 | Spatial cathedral of memory |
| Gardener | 100 | Cultivation practice for ideas |
| Gestalt | 100 | Living garden where code breathes |
| **Forge** | 85 | **Developer's workshop for metaphysical fullstack agents** |
| Coalition | 55 | Workshop where agents collaborate visibly |
| Park | 40 | Westworld where hosts can say no |
| Domain | 0 | Enterprise categorical foundation |

**Design DNA**: Observer-dependent • Consent-first • Visible process • Composable • Joy-inducing

**Forge Status**: Phase 4 COMPLETE. All 4 creative artisans (Architect, Smith, Herald, Projector) = real work. 165 tests. Next: Sentinel, Witness.

**Habitat 2.0**: Layer 1 (Adaptive Habitat) COMPLETE. Layer 2 (MiniPolynomial) + Layer 3 (Ghosts) planned. AD-010 (Habitat Guarantee) ensures every AGENTESE path projects into at least a minimal experience.

---

## Status

**Tests**: 20,122 | **AGENTESE v3.1**: Self-doc, WiredLogos, aliases
**Archived**: E-gent, H-gent, Q-gent, R-gent, Psi-gent → `agents/_archived/`; Terrarium → `protocols/_archived/` (superseded by AUP)
**Differance**: 192 tests, Phase 5 complete → Phase 6 (Crown Jewel wiring) ready
**Router Consolidation**: 50% (P0+P1+P2 complete). Soul, K-gent sessions, N-Phase now via AGENTESE gateway

---

## Skills: Your First Stop (docs/skills/)

**Universal** (apply to ANY task): `metaphysical-fullstack.md` • `crown-jewel-patterns.md` • `test-patterns.md` • `elastic-ui-patterns.md`

**By Domain**:
- Foundation: `polynomial-agent.md` • `building-agent.md`
- Protocol: `agentese-path.md` • `agentese-node-registration.md`
- Architecture: `crown-jewel-patterns.md` • `metaphysical-fullstack.md` • `data-bus-integration.md`
- Process: `plan-file.md` • `spec-template.md` • `spec-hygiene.md`
- Projection: `projection-target.md` • `test-patterns.md` • `elastic-ui-patterns.md`

---

## Quick Commands

```bash
# Backend
cd impl/claude && uv run pytest -q && uv run mypy .

# Frontend (run typecheck before committing!)
cd impl/claude/web && npm run typecheck && npm run lint
```


*Lines: 136. Ceiling: 160.*
