# HYDRATE.md - kgents META CONTEXT

> *"To read is to invoke. There is no view from nowhere."*

This document is an AGENTESE coordination surface. Projects are **holons**—grasping one yields affordances that depend on who is grasping.

## hydrate.protocol

```
hydrate.project.manifest   → View project status (observer-dependent)
hydrate.project.afford     → What can I do here? (synergies)
hydrate.project.block      → What blocks me? (blockers)
hydrate.concept.manifest   → Shared abstractions (principles, gotchas)
hydrate.void.sip           → Exploration budget, slop, tangents
hydrate.time.witness       → Temporal trace (git log, recent changes)
```

**Editing = Invocation**: When you edit, you disturb the field. Your edit carries your observer context.

| Action | AGENTESE Analog | Protocol |
|--------|-----------------|----------|
| Add project | `hydrate.world.define` | Insert alphabetically; include `afford`/`block` |
| Update status | `hydrate.project.manifest` | Touch only your section |
| Note dependency | `hydrate.project.block` | Announce what blocks you |
| Note enablement | `hydrate.project.afford` | Announce what you enable |
| Update shared | `hydrate.concept.refine` | Prefix `[STALE?]` if uncertain |

**Status**: 7,080+ tests | Branch: `main` | Mypy: 3,639 baselined
#################################################################################

## hydrate.concept.manifest

**Principles**: Tasteful • Curated • Ethical • Joy-Inducing • Composable • Heterarchical • Generative

**Meta**: AGENTESE (no view from nowhere) • Accursed Share (slop → curate → cherish) • Personality Space

**Ops**: Transparent Infrastructure • Graceful Degradation • Spec-Driven Infrastructure

---

## hydrate.world.manifest

Projects are holons. Grasping yields observer-dependent affordances.

### world.k8gents

> *"K8s primitives ARE agent primitives—a structural isomorphism."*

**handle**: `spec/k8-gents/` (README + 02-03)

| CRD | Purpose |
|-----|---------|
| Agent | Deployment + Service + NetworkPolicy |
| Pheromone | Decaying stigmergic signal |
| Memory | PVC + retention policy |
| Umwelt | Observer context + slop budget |
| Proposal | Safe autopoiesis via dry-run |

**v4.0 manifest**: Five CRDs • Categorical composition • Workload classification • Trust gates
**simplified from v3.1**: Removed semantic routing (deferred), removed surprise metrics (→ workload classification), moved horizon to research/

**spec structure**:
- `README.md`: Core thesis, CRDs, anatomy
- `02_evolution.md`: Proposal CRD, trust gates
- `03_interface.md`: Ghost, Tether, MCP
- `research/`: Speculative (not spec)

**afford**: DevEx • W-gent wire • O-gent observability
**block**: None

---

### world.devex

```
kgents status/dream/map/signal   # Phase 1
kgents ghost [--daemon]          # Phase 2
```

**manifest**: Phases 1-2 complete
**pending**: Neural Link • Shadow • Rituals (Phases 3-5)
**afford**: K8-gents Cortex Daemon (ghost feeds) • M-gent cartography (map uses)
**block**: None

---

## hydrate.self.manifest

| Agent | Handle | Tests |
|-------|--------|-------|
| Bicameral | `self.memory` | 532 |
| SemanticField | `world.pheromone` | 71 |
| Cartography | `self.map` | 157 |
| Interceptors | `world.wire` | 125 |

| Letter | Holon | Handle |
|--------|-------|--------|
| B | economics | `agents/b/metered_functor.py` |
| D | memory | `agents/d/bicameral.py` |
| L | registry | `agents/l/semantic_registry.py` |
| M | cartography | `agents/m/cartographer.py` |
| N | narrative | `agents/n/chronicle.py` |
| Psi | metaphor | `agents/psi/engine.py` |

---

## hydrate.concept.refine

**commands**:
```
pytest -m "not slow" -q
cd impl/claude && uv run mypy --strict --explicit-package-bases agents/ bootstrap/ runtime/ 2>&1 | uv run mypy-baseline filter
```

**gotchas**:
- Python 3.12: `Generic[A]` + `TypeVar`, not `class Foo[A]:`
- Cross-agent: `*_integration.py` or SemanticField
- Foundational: `shared`, `a`, `d`, `l`, `c`

---

## hydrate.void.witness

**tech debt** (the accursed share—acknowledged, not ignored):
- Mypy: 3,639 baselined (down from 7,516, up from 2,776 due to new files)
- TODOs: 74 across 33 files
- Skipped tests: 56 (external deps)

################################################################################
*To read is to invoke. To edit is to disturb. There is no view from nowhere.*