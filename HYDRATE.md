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

**Status**: 8,714+ tests | Branch: `main` | Mypy: Strict (0 errors)

**Recent** (2025-12-12):
- **Flux Functor** — `agents/flux/` complete: Agent[A,B] → Agent[Flux[A], Flux[B]] (**261 tests**)
  - Event-driven streams, not timer-driven loops
  - Living Pipelines via `|` operator
  - Perturbation principle (invoke on FLOWING injects, not bypasses)
  - Ouroboric feedback configurable
- **Metabolism v1** — MetabolicEngine, FeverEvent, FeverStream (36 tests) + `kgents tithe` CLI
- **FluxReflector** — I-gent bridge to Reflector events (`agents/i/reflector/`)
- **Lattice v1** — Genealogical enforcement (`protocols/agentese/lattice/`)
- I-gent v2.5 Phase 5 — Polish, FD3 bridge (137 tests)
- Reflector Pattern (Phases 1-4 complete) — Protocol, Events, Terminal/Headless/Flux Reflectors (36 tests)
- U-gent complete — Tool/MCP/Executor migrated from T-gent; deprecation bridge in place
- K8-Terrarium v2.0 complete — Passive Stigmergy, LogosResolver, StigmergyStore

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

**handle**: `spec/k8-gents/` (README + ontology + protocols)

| CRD | AGENTESE Path |
|-----|---------------|
| Agent | `world.agent.manifest` → Deployment + Service + NetworkPolicy |
| Pheromone | `world.pheromone.decay` → Stigmergic signal |
| Memory | `self.memory.persist` → PVC + retention |
| Umwelt | `self.umwelt.manifest` → Observer context + slop |
| Proposal | `world.proposal.refine` → Safe autopoiesis via dry-run |

**v2.0 Complete** (Passive Stigmergy):
- LogosResolver: Stateless AGENTESE→K8s translation (536 lines)
- StigmergyStore: Redis-backed ephemeral pheromones (`infra/stigmergy/`)
- Pheromone intensity calculated on read, not stored
- Spec extracted to `spec/k8-gents/protocols/{logos,stigmergy}.md`

**Infrastructure Scripts**:
```bash
./impl/claude/infra/k8s/scripts/setup-cluster.sh      # Phase A
./impl/claude/infra/k8s/scripts/deploy-operators.sh   # Phase B
./impl/claude/infra/k8s/scripts/deploy-lgent.sh       # Phase C-D
```

**Running Pods** (`kubectl get pods -n kgents-agents`):
- kgents-operator (1/1) • l-gent (1/1) • l-gent-postgres (1/1) • ping-agent (1/1)

**afford**: DevEx • W-gent wire • O-gent observability
**block**: None

---

### world.cortex

> *"LLM health != HTTP 200. Cognitive probes measure actual reasoning."*

**handle**: `impl/claude/infra/cortex/`

| Component | Purpose |
|-----------|---------|
| `probes.py` | CognitiveProbe, PathProbe — health via reasoning tasks |
| `agents/blend.py` | BlendAgent — conceptual blending via LLM |
| `agents/critic.py` | CriticAgent — dialectical refinement |
| `agents/define.py` | DefineAgent — autopoiesis (new concept creation) |
| `logos_resolver.py` | Stateless AGENTESE→K8s resolver |
| `service.py` | CortexService orchestrator |

**afford**: K8s liveness probes • AGENTESE LLM integration
**block**: None

---

### world.devex

```
kgents status    → self.manifest
kgents dream     → void.sip
kgents map       → self.map.manifest
kgents signal    → world.pheromone.emit
kgents ghost     → time.witness.stream
kgents capital   → self.capital.balance (NEW)
```

**manifest**: Phases 1-2 complete + Capital CLI
**pending**: Neural Link • Shadow • Rituals (Phases 3-5)
**afford**: K8-gents Cortex Daemon • M-gent cartography
**block**: None

---

### world.mcp

> *"MCP Resources expose the semantic graph to external agents."*

**handle**: `impl/claude/protocols/cli/mcp/`

| Resource | URI | Purpose |
|----------|-----|---------|
| Catalog | `kgents://catalog` | All registered agents |
| Agent | `kgents://agent/{id}` | Single agent details |
| Pheromones | `kgents://pheromones` | Active signals |
| Capital | `kgents://capital/{agent}` | Trust balance |

**afford**: Claude Code integration • External tooling
**block**: None

---

### world.context_sovereignty

> *"The brain that watches itself grow heavy is already dying."*

**handle**: `plans/self/stream.md`

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

### Agent Registry (22+ agents)

| Letter | Holon | Handle | Key Files |
|--------|-------|--------|-----------|
| A | abstract/art | `agents/a/` | `__deps__.py` |
| B | economics | `agents/b/` | `metered_functor.py` |
| C | category | `agents/c/` | composability |
| D | memory | `agents/d/` | `bicameral.py`, `context_comonad.py`, `context_window.py`, `linearity.py`, `projector.py` |
| E | evolution | `agents/e/` | teleological thermodynamics |
| F | futures | `agents/f/` | promises |
| G | generation | `agents/g/` | autopoiesis |
| H | dialectics | `agents/h/` | Hegel/Jung/Lacan |
| I | interface | `agents/i/` | `app.py`, `widgets/`, `screens/`, `data/` |
| J | judgment | `agents/j/` | `t_integration.py` |
| K | simulacra | `agents/k/` | Kent persona |
| L | registry | `agents/l/` | `semantic_registry.py`, `server.py`, `Dockerfile` |
| M | cartography | `agents/m/` | `cartographer.py` |
| N | narrative | `agents/n/` | `chronicle.py` |
| O | observation | `agents/o/` | telemetry |
| P | personality | `agents/p/` | persona space |
| Ψ | metaphor | `agents/psi/` | `engine.py` |
| Q | quantum | `agents/q/` | superposition |
| R | resilience | `agents/r/` | `integrations.py` |
| T | testing | `agents/t/` | `trustgate.py`, mock, spy, judge, property |
| U | utility | `agents/u/` | `core.py`, `mcp.py`, `executor.py`, `orchestration.py`, `permissions.py` |
| W | wire | `agents/w/` | interceptors |
| Flux | flux | `agents/flux/` | stream transformer (Agent[A,B] → Agent[Flux[A], Flux[B]]) |

### Core Subsystems

| Subsystem | Handle | Tests |
|-----------|--------|-------|
| Bicameral | `self.memory.*` | 532 |
| SemanticField | `world.pheromone.*` | 71 |
| Cartography | `self.map.*` | 157 |
| Interceptors | `world.wire.*` | 125 |
| ContextWindow | `agents/d/context_window.py` | 41 |
| LinearityMap | `agents/d/linearity.py` | 38 |
| ContextProjector | `agents/d/projector.py` | 28 |
| ContextComonad | `agents/d/context_comonad.py` | 35 |
| TrustGate | `agents/t/trustgate.py` | 50+ |
| **Flux** | `agents/flux/` | **261** |

### Protocol Contexts

| Context | Handle | Tests |
|---------|--------|-------|
| MDL Compression | `protocols/agentese/contexts/compression.py` | 43 |
| Stream Context | `protocols/agentese/contexts/stream.py` | 31 |
| Concept Blending | `protocols/agentese/contexts/concept_blend.py` | 40+ |
| Self Judgment | `protocols/agentese/contexts/self_judgment.py` | 60+ |
| WundtCurator | `protocols/agentese/middleware/curator.py` | 30+ |

### Shared Modules

| Module | Purpose |
|--------|---------|
| `shared/capital.py` | Trust accounting (event-sourced) |
| `shared/costs.py` | Operation cost definitions |
| `shared/budget.py` | Budget allocation |
| `shared/melting.py` | Contract dissolution |
| `shared/pataphysics.py` | Exception semantics |

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
- Tests: 8,714 passing
- External stubs: Using `ignore_missing_imports` for redis, kubernetes, etc.

**phase.manifest**:

| Phase | Status | Location |
|-------|--------|----------|
| CLI Hollowing | Complete | `plans/_archive/cli-hollowing-v1.0-complete.md` |
| Capital Ledger | Complete | `plans/_archive/capital-ledger-v1.0-complete.md` |
| K8-Terrarium v2.0 | Complete | `plans/_archive/k8-terrarium-v2.0-complete.md` |
| T/U-gent Separation | Complete | Files moved: `agents/t/` → `agents/u/` |
| I-gent v2.5 (1-5) | Complete | FluxApp + Glitch + FD3 bridge (137 tests) |
| Reflector Pattern | Complete | Protocol + Terminal/Headless/Flux (36 tests) |
| Lattice v1 | 60% | `protocols/agentese/lattice/` (checker, lineage, errors, 63 tests) |
| Creativity v2.5 | 90% | Phases 5-8 done; Tasks 2-4 remaining |
| Metabolism v1 | Complete | `protocols/agentese/metabolism/` (engine, fever, 36 tests) |
| Flux Functor | Complete | `agents/flux/` (261 tests, living pipelines, perturbation) |

**Active work**:
- **Lattice**: Genealogical enforcement for `concept.*.define` (60% → wiring to Logos)
- **Creativity Tasks 2-4**: Bidirectional Skeleton, Wire Pataphysics, Auto-Wire Curator

**Next priorities** (see `plans/_forest.md` for canopy, `plans/_focus.md` for primary focus):
1. Lattice wiring — Connect to `concept.*.define` (60% complete)
2. Flux integration — Wire Flux to archetypes (Consolidator, Spawner, Witness, etc.)
3. Creativity Tasks 2-4 — Bidirectional Skeleton, Wire Pataphysics

---

## hydrate.time.witness

**Recent commits** (2025-12-12):
```
922a636 feat(i-gent,agentese): Add FluxReflector and creativity polish
3563383 feat(lattice): Implement concept lineage and genealogical enforcement
b6f1a5d fix(i-gent): Use time.time() for GlitchEvent timestamp
2445e7a feat(i-gent): Add I-gent v2.5 TUI with Phase 5 polish and FD3 bridge
c2dce87 feat(u-gent): Migrate tool code from T-gent to U-gent + fix mypy
```

**New specs added**:
- `spec/k8-gents/ontology.md` — K8s/Agent structural isomorphism
- `spec/k8-gents/protocols/logos.md` — AGENTESE→K8s translation
- `spec/k8-gents/protocols/stigmergy.md` — Passive pheromone mechanics
- `spec/protocols/curator.md` — Wundt aesthetic filtering
- `spec/protocols/blending.md` — Conceptual integration
- `spec/protocols/critic.md` — Dialectical refinement

**New implementations**:
- **`impl/claude/agents/flux/`** — Flux Functor (261 tests):
  - `agent.py` — FluxAgent core (event-driven stream processing)
  - `functor.py` — Flux.lift() / Flux.unlift()
  - `pipeline.py` — FluxPipeline with `|` operator
  - `sources/` — from_iterable, periodic, merged, filtered, mapped, take, skip
- `impl/claude/protocols/agentese/metabolism/` — Metabolic engine (engine, fever, 36 tests)
- `impl/claude/protocols/agentese/lattice/` — Genealogical typing (checker, lineage, errors)
- `impl/claude/agents/i/reflector/` — FluxReflector (TUI event bridge)
- `impl/claude/protocols/cli/reflector/` — Reflector Protocol (terminal, headless, events)
- `impl/claude/agents/i/widgets/glitch.py` — Glitch system (Zalgo, GlitchController)
- `impl/claude/agents/u/` — Utility agents (tool, mcp, executor)
- `impl/claude/infra/cortex/` — LLM integration layer
- `impl/claude/infra/stigmergy/` — Redis-backed pheromone store

**New plans**:
- `plans/agents/loop.md` — Flux Functor plan: Agent[A,B] → Agent[Flux[A], Flux[B]]
- `docs/spec-change-proposal.md` — Conservative spec changes for Flux

---

## hydrate.structure.manifest

```
kgents/
├── spec/                           # The specification (conceptual)
│   ├── protocols/
│   │   ├── agentese.md             # AGENTESE meta-protocol
│   │   ├── curator.md              # Wundt aesthetic filtering
│   │   ├── blending.md             # Conceptual integration
│   │   └── critic.md               # Dialectical refinement
│   ├── k8-gents/
│   │   ├── README.md               # K8s CRD overview
│   │   ├── ontology.md             # K8s/Agent isomorphism
│   │   └── protocols/
│   │       ├── logos.md            # AGENTESE→K8s translation
│   │       └── stigmergy.md        # Passive pheromone mechanics
│   └── {a-z}-gents/                # Per-agent specs
├── impl/claude/                    # Reference implementation
│   ├── agents/
│   │   ├── {a-z,psi}/              # Agent implementations
│   │   ├── flux/                   # Flux Functor (stream transformer)
│   │   ├── t/                      # Testing (mock, spy, trustgate)
│   │   └── u/                      # Utility (tool, mcp, executor)
│   ├── protocols/
│   │   ├── agentese/               # AGENTESE (595+ tests)
│   │   │   ├── contexts/           # Stream, Blend, Judgment, Compression
│   │   │   ├── lattice/            # Genealogical typing (checker, lineage, errors)
│   │   │   ├── metabolism/         # Metabolic engine, fever, oblique strategies
│   │   │   └── middleware/         # Curator
│   │   └── cli/
│   │       ├── reflector/          # Reflector Protocol (terminal, headless, events)
│   │       ├── mcp/                # MCP server + resources
│   │       └── genus/              # CLI commands (c_gent.py)
│   ├── infra/
│   │   ├── cortex/                 # LLM integration
│   │   │   ├── probes.py           # Cognitive health probes
│   │   │   ├── logos_resolver.py   # AGENTESE→K8s resolver
│   │   │   └── agents/             # Blend, Critic, Define
│   │   ├── stigmergy/              # Redis pheromone store
│   │   └── k8s/
│   │       ├── crds/               # CRD definitions
│   │       ├── operators/          # Agent, Pheromone operators
│   │       ├── manifests/          # Deployment YAMLs
│   │       └── scripts/            # Setup, deploy, verify
│   └── shared/
│       ├── capital.py              # Trust accounting
│       ├── costs.py                # Operation costs
│       ├── budget.py               # Budget allocation
│       ├── melting.py              # Contract dissolution
│       └── pataphysics.py          # Exception semantics
├── plans/
│   ├── _forest.md                  # Canopy view (session start)
│   ├── _status.md                  # Implementation matrix
│   ├── _focus.md                   # Current session focus
│   ├── README.md                   # Plans overview + decisions
│   ├── self/
│   │   ├── reflector.md            # Reflector Pattern (CLI/TUI bridge)
│   │   ├── interface.md            # I-gent v2.5 (Semantic Flux)
│   │   ├── stream.md               # Context sovereignty
│   │   └── memory.md               # StateCrystal
│   ├── concept/
│   │   ├── creativity.md           # Phases 5-8
│   │   └── lattice.md              # Genealogical typing
│   ├── agents/
│   │   ├── t-gent.md               # Testing agents
│   │   └── u-gent.md               # Utility agents
│   └── _archive/                   # Completed plans
│       ├── cli-hollowing-v1.0-complete.md
│       ├── capital-ledger-v1.0-complete.md
│       └── k8-terrarium-v2.0-complete.md
└── docs/                           # Supporting documentation
```

---

*To read is to invoke. To edit is to disturb. There is no view from nowhere.*
