---
context: self
---

# Systems Reference — Built Infrastructure

> *"Agents: these systems exist and are tested. Use them."*

This document inventories all production-ready **backend** infrastructure in kgents. When planning features, CHECK HERE FIRST before assuming you need to build something new.

**Note (2025-12-21)**: Web UI has been pruned to focus on Brain, Galleries, and OS-Shell. Backend services (Town, Park, Forge, Gestalt, etc.) remain for future integration.

---

## Data Bus Infrastructure (Event-Driven Communication)

**The Reactive Data Flow Backbone** — Three-layer event bus architecture enabling agents to communicate without tight coupling.

| Bus | Location | Scope | Purpose |
|-----|----------|-------|---------|
| **DataBus** | `agents/d/bus.py` | Single process | D-gent storage events (PUT, DELETE, UPGRADE, DEGRADE) |
| **SynergyBus** | `protocols/synergy/bus.py` | Cross-jewel | Crown Jewel coordination (60+ event types) |
| **EventBus** | `agents/town/event_bus.py` | Fan-out | UI/streaming distribution with backpressure |

```python
# DataBus: React to storage operations
from agents.d.bus import get_data_bus, DataEventType

bus = get_data_bus()
bus.subscribe(DataEventType.PUT, async_handler)

# SynergyBus: Crown Jewel coordination
from protocols.synergy import get_synergy_bus, create_analysis_complete_event

synergy = get_synergy_bus()
await synergy.emit(create_analysis_complete_event(...))

# EventBus: Fan-out streaming
from agents.town.event_bus import EventBus

bus = EventBus[TownEvent](max_queue_size=1000)
sub = bus.subscribe()
async for event in sub:
    process(event)
```

**Key Integrations:**
- `BusEnabledDgent` — Wraps D-gent to auto-emit events
- `MgentBusListener` — Auto-indexes data as memories
- `wire_data_to_synergy()` — Bridges DataBus → SynergyBus
- `BusNode` — AGENTESE access via `self.bus.*`

**AGENTESE Paths:**
- `self.bus.manifest` — Bus state overview
- `self.bus.subscribe` — Subscribe to events
- `self.bus.replay` — Catch up on missed events
- `self.bus.latest` — Most recent event
- `self.bus.stats` — Bus statistics

**Skills**: `docs/skills/data-bus-integration.md`

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

## Différance Engine (Ghost Heritage Tracing)

**The Self-Knowing System** — Every output carries trace of what it IS and what it ALMOST WAS (ghosts).

| Component | Location | Purpose |
|-----------|----------|---------|
| **TraceMonoid** | `agents/differance/trace.py` | Monoidal composition of wiring decisions with ghost preservation |
| **DifferanceStore** | `agents/differance/store.py` | Append-only trace persistence via D-gent |
| **TRACED_OPERAD** | `agents/differance/operad.py` | Extends AGENT_OPERAD with traced composition |
| **DifferanceIntegration** | `agents/differance/integration.py` | Crown Jewel integration (fire-and-forget traces) |
| **GhostHeritageDAG** | `agents/differance/heritage.py` | Graph of choices + alternatives |

```python
from agents.differance import (
    Alternative, WiringTrace, TraceMonoid,
    DifferanceStore, DifferanceIntegration,
    traced_seq, traced_par,
)

# Record a trace with alternatives (ghosts)
trace = WiringTrace(
    operation="select_model",
    input_summary={"query": "..."},
    output_summary={"model": "claude-sonnet"},
    alternatives=[
        Alternative(
            operation="select_model",
            inputs={"query": "..."},
            reason_rejected="Cost constraint",
            could_revisit=True,
        )
    ],
)

# Store via D-gent
store = DifferanceStore(dgent_instance)
await store.append(trace)

# Reconstruct monoid from storage
monoid = await store.to_monoid()
ghosts = monoid.ghosts  # All alternatives considered
```

**AGENTESE Paths:**
- `time.differance.recent` — Recent traces (limit=20)
- `time.differance.why` — Explain why a decision was made
- `time.differance.at` — Get trace at specific timestamp
- `time.branch.create` — Create speculative branch
- `time.branch.explore` — Explore ghost alternative

**Laws Verified** (property-based tests):
- Identity: `ε ⊗ T = T = T ⊗ ε`
- Associativity: `(A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)`
- Ghost Preservation: `ghosts(a ⊗ b) ⊇ ghosts(a) ∪ ghosts(b)`
- Semantic Preservation: traced operations preserve base behavior

**Key Insight**: *"The ghost heritage graph is the UI innovation: seeing what almost was alongside what is."*

---

## Witness Crown Jewel (8th Jewel — Autonomous Agency)

**Kent's Developer Agency, Crystallized** — Event-driven daemon with trust-gated capabilities.

| Component | Location | Purpose |
|-----------|----------|---------|
| **WitnessPolynomial** | `services/witness/polynomial.py` | Trust-gated state machine (L0→L3) |
| **WITNESS_OPERAD** | `services/witness/operad.py` | Extends AGENT_OPERAD with witness operations |
| **GitWatcher** | `services/witness/watchers/git.py` | Event-driven Git observation (no timers!) |
| **WitnessNode** | `services/witness/node.py` | AGENTESE registration (pending) |

```python
from services.witness import (
    WitnessPolynomial, WitnessState, TrustLevel,
    WITNESS_OPERAD, GitWatcher,
)

# Trust levels gate capabilities
poly = WitnessPolynomial(initial_trust=TrustLevel.L0)

# L0: Observe only (suggest, no action)
# L1: Read + non-destructive (run tests, lint)
# L2: Write + reversible (git commit, but no push)
# L3: Full Kent (push, PR, invoke any Crown Jewel)

# Event-driven watching (Flux lifting, no timers)
watcher = GitWatcher(repo_path="/path/to/repo")
async for event in watcher.watch():
    # event: FileChanged | CommitCreated | BranchSwitched
    await process_event(event)
```

**Trust Level Semantics:**
| Level | Name | Capabilities | Example Actions |
|-------|------|-------------|-----------------|
| L0 | Observer | Suggest only | "I notice tests are failing" |
| L1 | Reader | Non-destructive | Run pytest, mypy, lint |
| L2 | Writer | Reversible writes | git commit, file edits |
| L3 | Kent | Full autonomy | git push, create PR, invoke any jewel |

**Key Insight**: *"At Trust Level 3, Witness can do everything Kent does—tests, fixes, commits, PRs."*

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

## F-gent Flow (Conversational Modalities)

**NEW 2025-12-16** — Chat, Research, and Collaboration substrates.

| Component | Purpose |
|-----------|---------|
| `ChatFlow` | Turn-based conversation with context management |
| `ResearchFlow` | Tree of thought exploration |
| `CollaborationFlow` | Multi-agent blackboard patterns |
| `FLOW_POLYNOMIAL` | Mode-dependent flow behavior |
| `FLOW_OPERAD` | 13 composition operations |

```python
from agents.f import (
    ChatFlow, Turn, ChatConfig,
    ResearchFlow, HypothesisTree,
    CollaborationFlow, Blackboard,
    FLOW_POLYNOMIAL, FLOW_OPERAD, FlowState,
)

# Chat modality (requires agent)
chat = ChatFlow(agent=my_agent, config=ChatConfig(context_window=128000))
response = await chat.send_message("Hello!")

# Research modality
research = ResearchFlow(agent=my_agent)
await research.branch("Hypothesis: X causes Y")
synthesis = await research.synthesize()

# Collaboration modality
collab = CollaborationFlow(agents={"a": agent_a, "b": agent_b})
await collab.post(agent_id="a", content="My idea", type="idea")
```

**AGENTESE Paths:**
- `self.flow.state` — Current flow state
- `self.flow.modality` — Active modality (chat/research/collaboration)
- `self.flow.chat.*` — Chat operations (context, history, turn)
- `self.flow.research.*` — Research operations (tree, branch, synthesize)
- `self.flow.collaboration.*` — Collaboration operations (board, post, vote)

**Note:** Flow (conversational modalities) is distinct from Flux (stream processing).

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

## 3D Projection Primitives (Three.js)

**Unified 3D visualization system** for topology graphs with theme-parameterized rendering.

| Component | Location | Purpose |
|-----------|----------|---------|
| `TopologyNode3D` | `web/src/components/three/primitives/` | Generic 3D node with theme slots |
| `TopologyEdge3D` | `web/src/components/three/primitives/` | Generic 3D edge (curved/straight) |
| `SelectionRing` | `web/src/components/three/primitives/` | Reusable selection indicator |
| `HoverRing` | `web/src/components/three/primitives/` | Reusable hover indicator |
| `FlowParticle` | `web/src/components/three/primitives/` | Animated flow particles |
| `NodeLabel3D` | `web/src/components/three/primitives/` | 3D text labels |
| `GrowthRings` | `web/src/components/three/primitives/` | Concentric ring indicators |
| **Themes** | `web/src/components/three/primitives/themes/` | Crystal (Brain), Forest (Gestalt) |
| **Animation** | `web/src/components/three/primitives/animation.ts` | Breathing, hover, selection presets |

```tsx
import {
  TopologyNode3D, TopologyEdge3D,
  CRYSTAL_THEME, FOREST_THEME,
  ANIMATION_PRESETS
} from '@/components/three/primitives';

// Generic node with crystal theme (Brain)
<TopologyNode3D
  position={[x, y, z]}
  theme={CRYSTAL_THEME}
  data={node}
  getTier={(n) => getResolutionTier(n)}
  getSize={(n, d) => calculateSize(n, d)}
  isSelected={isSelected}
  density={density}
  onClick={handleClick}
/>

// Generic edge with forest theme (Gestalt)
<TopologyEdge3D
  source={sourcePos}
  target={targetPos}
  theme={FOREST_THEME}
  strength={0.8}
  showFlowParticles={isActive}
/>
```

**Architecture**: `P[3D] : State x Theme x Quality -> Scene`

**Quality Levels**: `minimal` | `standard` | `high` | `cinematic`

**AGENTESE Paths**:
- `concept.projection.three.node.manifest` — Node primitive config
- `concept.projection.three.edge.manifest` — Edge primitive config
- `concept.projection.three.theme.list` — Available themes
- `concept.projection.three.quality.adapt` — Quality adaptation

**Skills**: `docs/skills/3d-projection-patterns.md`

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

## Terrarium (ARCHIVED - Superseded by AGENTESE Universal Protocol)

**Status**: Archived 2025-12-17. See `protocols/_archived/terrarium-archived/README.md`.

**Superseded by**:
- **AGENTESE Universal Gateway** (`protocols/agentese/gateway.py`) - Auto-exposes nodes via HTTP/WebSocket
- **Synergy Event Bus** (`protocols/synergy/bus.py`) - Cross-jewel communication

**Preserved in `agents/flux/`**:
- `HolographicBuffer` → `agents/flux/mirror.py`
- `TerriumEvent`, `SemaphoreEvent` → `agents/flux/terrarium_events.py`
- `SemanticMetricsCollector` → `agents/flux/semantic_metrics.py`

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

# Data Bus (event-driven communication)
from agents.d.bus import (
    DataBus, DataEvent, DataEventType,
    BusEnabledDgent, get_data_bus
)
from protocols.synergy import (
    get_synergy_bus, SynergyEventType, Jewel,
    create_analysis_complete_event, create_crystal_formed_event
)
from agents.town.event_bus import EventBus, Subscription

# SaaS
from protocols.api import create_app
from protocols.billing import StripeClient
from protocols.licensing import requires_tier
from protocols.tenancy import set_tenant_context
```

---

*Last updated: 2025-12-19*
