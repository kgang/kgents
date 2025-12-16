# Systems Reference — Built Infrastructure

> *"Agents: these systems exist and are tested. Use them."*

This document inventories all production-ready infrastructure in kgents. When planning features, CHECK HERE FIRST before assuming you need to build something new.

---

## Gardener-Logos (NEW 2025-12-16)

**The Meta-Tending Substrate** — Unifies The Gardener Crown Jewel with Prompt Logos into a single system for tending the garden of prompts.

| Component | Location | Purpose |
|-----------|----------|---------|
| **Spec** | `spec/protocols/gardener-logos.md` | Full specification |
| **Garden State** | `protocols/gardener_logos/garden.py` | Seasons, metrics, unified state |
| **Tending Calculus** | `protocols/gardener_logos/tending.py` | 6 verbs: observe, prune, graft, water, rotate, wait |
| **Plots** | `protocols/gardener_logos/plots.py` | Named focus regions (crown jewels, plans) |
| **Personality** | `protocols/gardener_logos/personality.py` | Joy layer, contextual greetings |
| **Meta-Tending** | `protocols/gardener_logos/meta/` | Self-observation prompts |
| **ASCII Projection** | `protocols/gardener_logos/projections/ascii.py` | CLI rendering |

```python
from protocols.gardener_logos import (
    create_garden, GardenSeason,
    create_plot, create_crown_jewel_plots,
    observe, prune, graft, water, rotate, wait,
    TendingPersonality, default_personality,
)
from protocols.gardener_logos.projections import project_garden_to_ascii

garden = create_garden(name="my-project", season=GardenSeason.SPROUTING)
garden.plots = create_crown_jewel_plots()
garden.add_gesture(observe("concept.prompt.*"))
print(project_garden_to_ascii(garden))
```

**AGENTESE Paths:**
- `concept.gardener.manifest` — Garden overview
- `concept.gardener.tend` — Apply tending gestures
- `concept.gardener.season.*` — Season operations
- `concept.gardener.plot.*` — Plot management
- `concept.prompt.*` — Prompt Logos (delegated)

---

## Categorical Foundation (USE FOR ANY DOMAIN)

| Component | Location | Purpose | Tests |
|-----------|----------|---------|-------|
| **PolyAgent** | `agents/poly/` | State-dependent agents: `PolyAgent[S, A, B]` | 200+ |
| **Operad** | `agents/operad/` | Composition grammar with law verification | 150+ |
| **Sheaf** | `agents/sheaf/` | Emergence from local sections | 100+ |

```python
# PolyAgent: State machines with mode-dependent behavior
from agents.poly import PolyAgent, MANIFEST, WITNESS, SIP
poly = PolyAgent(initial_state, directions_fn, transition_fn)

# Operad: Programmable composition grammar
from agents.operad import AGENT_OPERAD, SOUL_OPERAD
SOUL_OPERAD.verify_laws()  # Proves composition is valid

# Sheaf: Emergence from local views
from agents.sheaf import KENT_SOUL, query_soul
result = query_soul("aesthetic", query)  # Gets local soul response
```

---

## AGENTESE (Verb-First Ontology)

| Phase | Module | Exports |
|-------|--------|---------|
| Core | `protocols/agentese/logos.py` | `Logos`, `create_logos` |
| Parser | `protocols/agentese/parser.py` | `PathParser`, `parse_path`, `ParsedPath` |
| Affordances | `protocols/agentese/affordances.py` | `AffordanceRegistry`, `ArchetypeDNA` |
| JIT | `protocols/agentese/jit.py` | `JITCompiler`, `compile_spec` |
| Laws | `protocols/agentese/laws.py` | `CategoryLawVerifier`, `compose`, `pipe` |
| Wiring | `protocols/agentese/wiring.py` | `WiredLogos`, `create_wired_logos` |
| Adapter | `protocols/agentese/adapter.py` | `AgentesAdapter`, `PatternTranslator` |

```python
from protocols.agentese import (
    Logos, create_logos, parse_path,
    AffordanceRegistry, create_wired_logos
)

# Create wired logos with all resolvers
logos = create_wired_logos()

# Invoke AGENTESE path
result = await logos.invoke("world.house.manifest", umwelt)

# Parse path for introspection
parsed = parse_path("self.memory.witness[phase=DEVELOP]")
```

---

## Flux (Stream Processing)

| Component | Purpose |
|-----------|---------|
| `FluxAgent` | Wrapped agent with stream capabilities |
| `FluxFunctor` | Lifts discrete → continuous |
| `FluxPipeline` | Chain of flux agents |
| `Perturbation` | Inject events into running flow |

```python
from agents.flux import Flux, FluxConfig, FluxPipeline

# Lift any agent to flux domain
flux_agent = Flux.lift(discrete_agent)

# Create pipeline
pipeline = flux_a | flux_b | flux_c

# Process stream
async for result in flux_agent.start(source):
    process(result)
```

---

## Agent Town (Multi-Agent Simulation)

| Component | Purpose |
|-----------|---------|
| `CitizenPolynomial` | Citizen state machine |
| `TOWN_OPERAD` | Interaction grammar |
| `TownFlux` | Simulation loop |
| `DialogueEngine` | LLM-backed citizen dialogue |
| `InhabitSession` | Player inhabits citizen |

```python
from agents.town import (
    Citizen, TownEnvironment, TownFlux,
    TOWN_OPERAD, CitizenPhase
)

# Create town
env = TownEnvironment(regions=[...])
flux = TownFlux(env, citizens=[...])

# Run simulation
async for event in flux.run():
    process(event)
```

---

## K-gent (Soul/Governance)

| Component | Purpose |
|-----------|---------|
| `KgentSoul` | Middleware of consciousness |
| `KgentFlux` | Soul streaming |
| `HypnagogicCycle` | Dream/consolidation |
| `SemanticGatekeeper` | Principle enforcement |
| `PersonaGarden` | Pattern storage |
| `SoulSession` | Cross-session identity |

```python
from agents.k import (
    soul, create_soul, KgentFlux,
    SemanticGatekeeper, validate_content
)

# Quick dialogue
response = soul.dialogue("What do you believe?", mode="reflect")

# Validate content against principles
result = validate_content(code, file_path)
```

---

## M-gent (Memory)

| Component | Purpose |
|-----------|---------|
| `HolographicMemory` | Core memory with compression |
| `MemoryCrystal` | Pattern storage with degradation |
| `CartographerAgent` | Generate HoloMaps |
| `PheromoneField` | Stigmergic coordination |
| `SemanticRouter` | Memory routing |
| `SharedSubstrate` | Multi-agent memory |

```python
from agents.m import (
    HolographicMemory, MemoryCrystal,
    create_semantic_router, SharedSubstrate
)

# Create memory with budget
memory = HolographicMemory(compression_level=3)

# Semantic routing
router = create_semantic_router(providers=[...])
result = await router.route(query)
```

---

## Reactive Substrate (Widgets)

| Component | Purpose |
|-----------|---------|
| `Signal[T]` | Observable state |
| `Computed[T]` | Derived state |
| `Effect` | Side effects |
| `KgentsWidget[S]` | Base widget class |
| `HStack/VStack` | Composition containers |

```python
from agents.i.reactive import (
    Signal, Computed, Effect,
    AgentCardWidget, AgentCardState,
    HStack, VStack
)

# Create widget
card = AgentCardWidget(AgentCardState(
    name="Agent", phase="active", capability=0.85
))

# Project to any target
card.to_cli()      # Terminal
card.to_marimo()   # Notebook
card.to_json()     # API
```

---

## Elastic Primitives (Responsive Layout)

| Component | Location | Purpose |
|-----------|----------|---------|
| `ElasticContainer` | `web/src/components/elastic/` | Self-arranging grid/stack/flow layouts |
| `ElasticCard` | `web/src/components/elastic/` | Priority-aware cards with content degradation |
| `ElasticSplit` | `web/src/components/elastic/` | Two-pane layout, collapses at 768px |
| `ElasticPlaceholder` | `web/src/components/elastic/` | Loading/empty/error states |
| `useWindowLayout` | `web/src/hooks/useLayoutContext.ts` | Window-level density/breakpoint info |
| `useLayoutMeasure` | `web/src/hooks/useLayoutContext.ts` | Container-level size measurement |
| `WidgetLayoutHints` | `web/src/reactive/types.ts` | Layout metadata for widgets |

```tsx
import { ElasticContainer, ElasticSplit, ElasticCard } from '@/components/elastic';
import { useWindowLayout } from '@/hooks/useLayoutContext';

// Get density context
const { density, isMobile, isTablet, isDesktop } = useWindowLayout();
// density: 'compact' | 'comfortable' | 'spacious'

// Self-arranging grid
<ElasticContainer layout="grid" minItemWidth={200}>
  {widgets.map(w => <ElasticCard key={w.id} priority={w.priority} {...w} />)}
</ElasticContainer>

// Two-pane with collapse
<ElasticSplit
  direction="horizontal"
  defaultRatio={0.7}
  collapseAt={768}
  resizable={isDesktop}
  primary={<MainPanel density={density} />}
  secondary={<Sidebar density={density} />}
/>
```

**Key Insight**: Density-Content Isomorphism — pass `density` down, let components decide what it means.

**Breakpoints**:
- 640px (sm/compact) — Mobile, drawers, touch targets
- 768px (md) — ElasticSplit collapse threshold
- 1024px (lg/spacious) — Full desktop layout

**Content Levels**: icon (<60px), title (<150px), summary (<280px), full (≥400px)

**Tests**: 32+ (17 chaos, 10 performance, 15+ E2E visual regression)

**Skills**: `docs/skills/elastic-ui-patterns.md`, `docs/skills/ui-isomorphism-detection.md`

---

## Projection Gallery

| Component | Location | Purpose |
|-----------|----------|---------|
| `Pilot` | `protocols/projection/gallery/pilots.py` | Pre-configured widget demo |
| `Gallery` | `protocols/projection/gallery/runner.py` | Render orchestrator |
| `GalleryOverrides` | `protocols/projection/gallery/overrides.py` | Override injection |
| `GalleryAPI` | `protocols/api/gallery.py` | REST endpoints |
| `GalleryPage` | `web/src/pages/GalleryPage.tsx` | React frontend |

```python
from protocols.projection.gallery import Gallery, GalleryOverrides, PILOT_REGISTRY

# CLI gallery
gallery = Gallery()
gallery.show_all(target=RenderTarget.CLI)  # All 25 pilots
gallery.show("agent_card_active", overrides={"entropy": 0.5})

# With global overrides
gallery = Gallery(GalleryOverrides(entropy=0.3, seed=42))
```

**Web Gallery**: `http://localhost:3000/gallery`

**API Endpoints**:
- `GET /api/gallery` - All pilots with projections
- `GET /api/gallery/{name}` - Single pilot
- `GET /api/gallery/categories` - Category metadata

---

## N-Phase Compiler

| Component | Purpose |
|-----------|---------|
| `NPhasePromptCompiler` | YAML → prompt |
| `ProjectDefinition` | Schema for projects |
| `NPhaseStateUpdater` | Track phase progress |

```python
from protocols.nphase import (
    compiler, ProjectDefinition,
    NPhaseStateUpdater, state_updater
)

# Compile from YAML
prompt = compiler.compile_from_yaml_file("project.yaml")

# Track state
updater = state_updater(project)
state = updater.advance_phase("DEVELOP", outputs)
```

---

## Evergreen Prompt System (Self-Cultivating CLAUDE.md)

| Component | Location | Purpose |
|-----------|----------|---------|
| `PromptCompiler` | `protocols/prompt/compiler.py` | Section-based CLAUDE.md compilation |
| `PromptM` | `protocols/prompt/monad.py` | Prompt Monad with unit/bind/map |
| `SoftSection` | `protocols/prompt/soft_section.py` | Rigidity spectrum (0.0-1.0) |
| `RollbackRegistry` | `protocols/prompt/rollback/` | Full history with instant rollback |
| CLI | `protocols/prompt/cli.py` | compile, history, rollback, diff |

```python
from protocols.prompt import (
    PromptCompiler, CompilationContext,
    PromptM, Source, sequence,
    RollbackRegistry, get_default_registry
)
from protocols.prompt.sections import get_default_compilers

# Compile CLAUDE.md
compiler = PromptCompiler(section_compilers=get_default_compilers(), version=1)
context = CompilationContext(project_root=Path("/path/to/project"))
result = compiler.compile(context)

# Use PromptM monad for composable transformations
section = Section(name="test", content="hello", token_cost=5, required=True)
transformed = (
    PromptM.unit(section)
    .with_provenance(Source.TEMPLATE)
    .map(lambda s: s.with_content(s.content.upper()))
    .with_trace("Uppercased content")
)

# Checkpoint and rollback
registry = get_default_registry()
checkpoint_id = registry.checkpoint(
    before_content="old",
    after_content="new",
    before_sections=(),
    after_sections=(),
    reason="Test change"
)
result = registry.rollback(checkpoint_id)
```

**CLI Commands**:
```bash
# Compile with checkpoint
uv run python -m protocols.prompt.cli compile --reason "Update"

# View history
uv run python -m protocols.prompt.cli history

# Rollback
uv run python -m protocols.prompt.cli rollback 26b96d66
```

**Category Laws** (verified with 216 tests):
- Left Identity: `unit(x).bind(f) == f(x)`
- Right Identity: `m.bind(unit) == m`
- Associativity: `m.bind(f).bind(g) == m.bind(λx. f(x).bind(g))`
- Rollback Invertibility: `rollback(checkpoint(p)).content == p`

---

## SaaS Infrastructure

### API (`protocols/api/`)
```python
from protocols.api import create_app, GovernanceRequest
app = create_app()  # FastAPI app with auth, routes, middleware
```

### Billing (`protocols/billing/`)
```python
from protocols.billing import (
    StripeClient, CustomerManager, SubscriptionManager,
    OpenMeterClient
)
```

### Licensing (`protocols/licensing/`)
```python
from protocols.licensing import (
    LicenseTier, requires_tier, is_feature_enabled
)

@requires_tier(LicenseTier.PRO)
def pro_feature(): ...
```

### Tenancy (`protocols/tenancy/`)
```python
from protocols.tenancy import (
    TenantContext, set_tenant_context, ApiKeyService
)

with set_tenant_context(tenant_id):
    # All queries scoped to tenant
    ...
```

---

## Terrarium (Agent Gateway)

```python
from protocols.terrarium import (
    Terrarium, HolographicBuffer, PrismRestBridge
)

# Create gateway
terrarium = Terrarium()
terrarium.register_agent(agent_id, flux_agent)

# Mount CLI agent as REST
bridge = PrismRestBridge()
bridge.mount(terrarium.app, cli_agent)
```

---

## Infra (Kubernetes)

| Directory | Purpose |
|-----------|---------|
| `infra/k8s/manifests/` | Kubernetes YAMLs |
| `infra/k8s/images/` | Dockerfiles |
| `infra/k8s/scripts/` | Setup scripts |
| `infra/cortex/` | Agent orchestration |
| `infra/morpheus/` | Dream infrastructure |

---

## Key Import Patterns

```python
# Categorical foundation
from agents.poly import PolyAgent, MANIFEST, WITNESS
from agents.operad import AGENT_OPERAD, Operation
from agents.sheaf import KENT_SOUL, query_soul

# Stream processing
from agents.flux import Flux, FluxPipeline

# AGENTESE
from protocols.agentese import Logos, create_wired_logos, parse_path

# Reactive
from agents.i.reactive import Signal, Computed, KgentsWidget

# Town
from agents.town import Citizen, TownFlux, TOWN_OPERAD

# Soul
from agents.k import soul, KgentFlux, SemanticGatekeeper

# Memory
from agents.m import HolographicMemory, MemoryCrystal, SemanticRouter

# SaaS
from protocols.api import create_app
from protocols.billing import StripeClient
from protocols.licensing import requires_tier
from protocols.tenancy import set_tenant_context
```

---

*Last updated: 2025-12-16*
