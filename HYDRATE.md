# HYDRATE.md - kgents META CONTEXT

> *"To read is to invoke. There is no view from nowhere."*

## hydrate.invoke — READ THIS FIRST

**Leverage AGENTESE**: When working in this codebase, prefer AGENTESE paths over ad-hoc solutions.

| Instead of... | Use AGENTESE |
|---------------|--------------|
| Raw dict/JSON state | `self.memory.*` (D-gent handles) |
| Print debugging | `time.witness.*` (N-gent traces) |
| Hardcoded config | `self.umwelt.*` (observer context) |
| Global singletons | `world.*.lens` (composable agents) |
| Random/arbitrary | `void.sip` (entropy from Accursed Share) |
| Ad-hoc validation | `concept.*.refine` (dialectical challenge) |

**The Five Contexts** — all interaction flows through these:
```
world.*    — External (entities, environments, tools)
self.*     — Internal (memory, capability, state)
concept.*  — Abstract (platonics, definitions, logic)
void.*     — Accursed Share (entropy, serendipity, gratitude)
time.*     — Temporal (traces, forecasts, schedules)
```

**Key Aspects**: `manifest` (perceive) • `witness` (history) • `refine` (challenge) • `sip` (entropy) • `tithe` (gratitude) • `lens` (compose) • `define` (create)

---

## hydrate.protocol

```
hydrate.project.manifest   → View project status (observer-dependent)
hydrate.project.afford     → What can I do here? (synergies)
hydrate.project.block      → What blocks me? (blockers)
hydrate.concept.manifest   → Shared abstractions (principles, gotchas)
hydrate.void.sip           → Exploration budget, slop, tangents
hydrate.time.witness       → Temporal trace (git log, recent changes)
```

| Action | AGENTESE Path | Protocol |
|--------|---------------|----------|
| Add project | `hydrate.world.define` | Insert alphabetically; include `afford`/`block` |
| Update status | `hydrate.project.manifest` | Touch only your section |
| Note dependency | `hydrate.project.block` | Announce what blocks you |
| Note enablement | `hydrate.project.afford` | Announce what you enable |
| Update shared | `hydrate.concept.refine` | Prefix `[STALE?]` if uncertain |

**Status**: 7,767 tests | Branch: `main` | Mypy: Strict (0 errors)

---

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

| CRD | AGENTESE Path |
|-----|---------------|
| Agent | `world.agent.manifest` → Deployment + Service + NetworkPolicy |
| Pheromone | `world.pheromone.decay` → Stigmergic signal |
| Memory | `self.memory.persist` → PVC + retention |
| Umwelt | `self.umwelt.manifest` → Observer context + slop |
| Proposal | `world.proposal.refine` → Safe autopoiesis via dry-run |

**v4.0**: Five CRDs • Categorical composition • Workload classification • Trust gates

**Operationalization (Phase A-F)**:
```bash
# Phase A - Cluster setup (✅ DONE)
./impl/claude/infra/k8s/scripts/setup-cluster.sh

# Phase B - Operator deployment (✅ DONE)
./impl/claude/infra/k8s/scripts/deploy-operators.sh

# Phase C-D - L-gent deployment (✅ DONE)
# agents/l/server.py (HTTP wrapper) + agents/l/Dockerfile
# Endpoints: /health, /ready, /catalog, /stats

# Phase E - MCP Resources (✅ DONE)
# protocols/cli/mcp/resources.py - kgents:// URI scheme

# Phase F - LLM Integration (✅ DONE)
# infra/cortex/probes.py - CognitiveProbe, PathProbe
# infra/cortex/agents/ - DefineAgent, BlendAgent, CriticAgent
```

**Running Pods** (`kubectl get pods -n kgents-agents`):
- kgents-operator (1/1) • l-gent (1/1) • l-gent-postgres (1/1) • ping-agent (1/1)

**afford**: DevEx • W-gent wire • O-gent observability
**block**: None

---

### world.devex

```
kgents status    → self.manifest
kgents dream     → void.sip
kgents map       → self.map.manifest
kgents signal    → world.pheromone.emit
kgents ghost     → time.witness.stream
```

**manifest**: Phases 1-2 complete
**pending**: Neural Link • Shadow • Rituals (Phases 3-5)
**afford**: K8-gents Cortex Daemon • M-gent cartography
**block**: None

---

### world.context_sovereignty

> *"The brain that watches itself grow heavy is already dying."*

**handle**: `plans/context-sovereignty.md` (v3.0)

| Component | AGENTESE Path | Categorical Basis |
|-----------|---------------|-------------------|
| Context Comonad | `self.stream.*` | extract/extend/duplicate |
| Compression | `self.stream.compress` | Affine/Linear/Relevant |
| Pheromones | `time.trace.pulse` | Functor decomposition |
| Crystals | `self.memory.crystallize` | Comonad + Linear |
| Compost | `void.entropy.pour` | Affine consumption |

**afford**: Y-gent somatic topology • K-Terrarium controller • DevEx metacognition
**block**: None

---

## hydrate.self.manifest

| Agent | AGENTESE Handle | Tests |
|-------|-----------------|-------|
| Bicameral | `self.memory.*` | 532 |
| SemanticField | `world.pheromone.*` | 71 |
| Cartography | `self.map.*` | 157 |
| Interceptors | `world.wire.*` | 125 |

| Letter | Holon | Handle |
|--------|-------|--------|
| B | economics | `agents/b/metered_functor.py` |
| D | memory | `agents/d/bicameral.py` |
| L | registry | `agents/l/semantic_registry.py` |
| M | cartography | `agents/m/cartographer.py` |
| N | narrative | `agents/n/chronicle.py` |
| Ψ | metaphor | `agents/psi/engine.py` |

---

## hydrate.concept.refine

**commands**:
```bash
pytest -m "not slow" -q
cd impl/claude && uv run mypy .  # Uses mypy.ini
```

**session.enforce** (MANDATORY before commit):
```bash
cd impl/claude && uv run mypy .      # Must pass (0 errors)
cd impl/claude && uv run ruff check  # Must pass
pytest -m "not slow" -q              # Must pass (pre-existing failures exempt)
```
> *No partially complete commits. If checks fail, fix before committing or revert.*

**gotchas**:
- Python 3.12: `Generic[A]` + `TypeVar`, not `class Foo[A]:`
- Cross-agent: `*_integration.py` or SemanticField
- Foundational: `shared`, `a`, `d`, `l`, `c`
- Imports: Prefer absolute (`from agents.x import Y`)
- **Dockerfiles**: Use `__deps__.py` manifests; validate with `python impl/claude/infra/scripts/build_agent_image.py <module> --validate`

---

## hydrate.void.witness

**tech debt** (the accursed share—acknowledged, not ignored):
- Mypy: Strict (0 errors) - achieved 2025-12-11
- Tests: 7,767 passing (25 compression tests + 7 curator tests + 28 other)
- External stubs: Using `ignore_missing_imports` for redis, kubernetes, etc.

**phase.manifest**:
- Phase 0 (CLI Hollowing): Complete
- Phase 1 (Grammar/Accounting): Complete — `shared/capital.py`, `shared/costs.py`, `shared/budget.py`
- Phase 2 (Store Comonad): Complete — `agents/d/context_comonad.py`
- **Phase 5-8 (Creativity v2.5)**: Complete — See `plans/concept/creativity.md`
  - Phase 5: Wundt Curator (`middleware/curator.py`)
  - Phase 6: Conceptual Blending (`contexts/concept_blend.py`)
  - Phase 7: Critic's Loop (`contexts/self_judgment.py`)
  - Phase 8: Contract Melt + Pataphysics (`shared/melting.py`)
  - **Task 1**: MDL + Reconstruction Validation (`contexts/compression.py`) ✅ NEW
- **Creativity v2.5 Remaining** (3 items):
  - Task 2: Bidirectional Skeleton (PAYADOR)
  - Task 3: Wire Pataphysics Solver to LLM
  - Task 4: Auto-Wire WundtCurator Middleware (already in Logos.invoke!)

---

*To read is to invoke. To edit is to disturb. There is no view from nowhere.*
