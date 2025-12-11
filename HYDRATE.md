# HYDRATE.md - kgents Session Context

**Status**: All Tests Passing | ~6,122 tests | Branch: `main`

## Recent: AGENTESE Deep Integration + Observability Dashboard

**Status**: All Tests Passing ✅ | **Branch**: `main` | **Tests**: ~6,122+

**Recent Work**:
- **AGENTESE DEEPLY INTEGRATED** ← 617 tests total (was 559)
  - **NEW**: Agent Discovery (`world.agent.*` namespace) - 34 tests
    - `world.agent.manifest` → List all 20 agents
    - `world.agent.egent.manifest` → E-gent capabilities
    - `world.agent.search` → Search by theme/description
  - **NEW**: Integration tests demonstrating cross-agent composition - 24 tests
  - **NEW**: CLAUDE.md updated with AGENTESE as core protocol
  - **NEW**: spec/principles.md updated with AGENTESE meta-principle
  - Phase 8: Natural Language Adapter (`adapter.py`) - 71 tests
  - Phase 7: WiredLogos production resolver - 44 tests
  - Phase 6: Integration layer - 81 tests
  - Phase 5: Composition & category laws - 80 tests
  - Phase 4: JIT compilation - 39 tests
  - Phase 3: Polymorphic affordances - 66 tests
  - Phases 1-2: Foundation + Five Contexts - 178 tests
- Instance DB Phase 6: O-gent/W-gent/I-gent Observability - 117 tests
- AGENTESE Protocol SPEC COMPLETE (spec/protocols/agentese.md)
- Integration Tests Phase 2 COMPLETE ← 74 tests passing
- CLI Auto-Bootstrap NOW OPERATIONAL
- E-gent v2 COMPLETE (353 tests)
- M-gent Holographic Cartography COMPLETE (114 tests)
- Cortex Assurance v2.0 COMPLETE (73 tests)
- Ψ-gent v3.0 (104 tests)

---

## AGENTESE: The Verb-First Ontology (v2.0)

**Spec**: `spec/protocols/agentese.md` (v2.0)
**Impl**: `impl/claude/protocols/agentese/`
**Plan**: `docs/agentese-implementation-plan.md`
**Status**: DEEPLY INTEGRATED - 617 tests (Phase 9: Integration)

### The Core Insight

> *"The noun is a lie. There is only the rate of change."*

Traditional systems: `world.house` returns a JSON object.
AGENTESE: `world.house` returns a **handle**—a morphism that maps Observer → Interaction.

**Key Refinements in v2.0**:
- Renamed `chaos.*` → `void.*` (better Accursed Share alignment)
- Handles are **functors** (strict category theory)
- **No view from nowhere**: invoke() requires observer (hard error)
- **Minimal Output Principle**: No array returns (breaks composition)
- **Sympathetic errors**: All errors explain why + suggest fix

### The Five Strict Contexts

```
world.*    - The External (Heterarchical)
self.*     - The Internal (Ethical)
concept.*  - The Abstract (Generative)
void.*     - The Accursed Share (Meta-Principle)
time.*     - The Temporal (Heterarchical)
```

**No sixth context allowed without spec change.**

### Key Aspects

| Aspect | Category | Meaning |
|--------|----------|---------|
| `manifest` | Perception | Collapse to observer's view |
| `witness` | Perception | Show history (N-gent) |
| `refine` | Generation | Dialectical challenge |
| `sip` | Entropy | Draw from Accursed Share |
| `tithe` | Entropy | Pay for order (gratitude noop) |
| `lens` | Composition | Get composable agent |
| `define` | Generation | Autopoiesis (create new) |

### The Logos Resolver

```
H(Context) ──Logos──▶ Interaction

Three-layer resolution:
1. L-gent registry (known entities)
2. spec/ directory (J-gent JIT compilation)
3. PathNotFoundError (sympathetic)
```

### Category Laws (REQUIRED)

```python
# Identity
Id >> path == path == path >> Id

# Associativity
(a >> b) >> c == a >> (b >> c)
```

### Implementation Phases

| Phase | Focus | Status | Tests |
|-------|-------|--------|-------|
| 1 | Foundation | ✅ COMPLETE | 113 |
| 2 | Five Contexts | ✅ COMPLETE | 178 |
| 3 | Affordances | ✅ COMPLETE | 244 |
| 4 | JIT | ✅ COMPLETE | 283 |
| 5 | Composition | ✅ COMPLETE | 363 |
| 6 | Integration | ✅ COMPLETE | 444 |
| 7 | Wire to Logos | ✅ COMPLETE | 488 |
| 8 | Adapter | ✅ COMPLETE | 559 |
| 9 | Deep Integration | ✅ COMPLETE | 617 |

### Phase 9: Deep Integration (NEW)

**Files Created**:
```
impl/claude/protocols/agentese/contexts/
└── agents.py           # world.agent.* namespace (450 lines)

impl/claude/protocols/agentese/_tests/
├── test_agents.py              # 34 tests - agent discovery
└── test_agentese_integration.py # 24 tests - cross-context workflows
```

**Key Features**:
- `AgentContextResolver`: Discovers all 20 agents via AGENTESE
- `AgentNode`: Manifest agent capabilities per observer archetype
- `AgentListNode`: List, search, and compose agents
- Cross-context workflow tests (world → self → void)
- Documentation examples verified as tests

### Phase 1 Files (COMPLETE)

```
impl/claude/protocols/agentese/
├── __init__.py       # Public API exports
├── logos.py          # Logos resolver functor (113 lines)
├── node.py           # LogosNode protocol + types (409 lines)
├── exceptions.py     # Sympathetic errors (222 lines)
└── contexts/
    └── __init__.py   # VALID_CONTEXTS registry
```

### Phase 1 Test Files

```
impl/claude/protocols/agentese/_tests/
├── conftest.py           # MockUmwelt, MockNode, fixtures
├── test_exceptions.py    # 39 tests - sympathetic error patterns
├── test_node.py          # 31 tests - protocol compliance, JIT
└── test_logos.py         # 43 tests - resolver, caching, composition
```

### Phase 2 Files (COMPLETE)

```
impl/claude/protocols/agentese/contexts/
├── __init__.py     # Exports + create_context_resolvers()
├── world.py        # WorldNode, WorldContextResolver (287 lines)
├── self_.py        # MemoryNode, CapabilitiesNode, StateNode, IdentityNode (268 lines)
├── concept.py      # ConceptNode, ConceptContextResolver (dialectic, refine) (426 lines)
├── void.py         # EntropyPool, EntropyNode, SerendipityNode, GratitudeNode (422 lines)
└── time.py         # TraceNode, PastNode, FutureNode, ScheduleNode (424 lines)
```

### Phase 2 Test File

```
impl/claude/protocols/agentese/_tests/
└── test_contexts.py   # 65 tests - all five contexts
```

### Phase 3 Files (COMPLETE)

```
impl/claude/protocols/agentese/
├── affordances.py    # AffordanceRegistry, UmweltAdapter, ArchetypeDNA (560 lines)
└── renderings.py     # 7 new rendering types, StandardRenderingFactory (320 lines)
```

**Key Features**:
- `AffordanceRegistry`: Central registry for archetype → affordances mappings
- `UmweltAdapter`: Extract affordance-relevant info from Umwelt
- `ArchetypeDNA`: DNA type for archetype-based agent configuration
- 7 new rendering types: Scientific, Developer, Admin, Philosopher, Memory, Entropy, Temporal
- `StandardRenderingFactory`: Polymorphic rendering creation

**Archetypes Defined**: architect, developer, scientist, admin, poet, philosopher, economist, inhabitant, default

### Phase 3 Test File

```
impl/claude/protocols/agentese/_tests/
└── test_affordances.py   # 66 tests - polymorphic affordances
```

### Phase 4 Files (COMPLETE)

```
impl/claude/protocols/agentese/
└── jit.py            # SpecParser, SpecCompiler, JITCompiler, JITPromoter (600 lines)

spec/world/
├── README.md         # How JIT compilation works
└── library.md        # Reference spec for world.library entity
```

**Key Features**:
- `SpecParser`: Parse YAML front matter + markdown specs
- `SpecCompiler`: Generate Python source from ParsedSpec
- `JITCompiler`: Full pipeline (parse → compile → validate → JITLogosNode)
- `JITPromoter`: Graduate nodes to impl/ when usage threshold met
- `define_concept()`: Create new entities at runtime (autopoiesis)
- `promote_concept()`: Graduate JIT nodes to permanent implementations

### Phase 4 Test File

```
impl/claude/protocols/agentese/_tests/
└── test_jit.py       # 39 tests - spec parsing, compilation, promotion
```

### Phase 5 Files (COMPLETE)

```
impl/claude/protocols/agentese/
└── laws.py           # Category law verification, composition (450 lines)
```

**Key Features**:
- `Identity` / `Id`: Identity morphism (Id >> f == f == f >> Id)
- `Composed`: Composition of morphisms preserving associativity
- `CategoryLawVerifier`: Runtime law verification (identity, associativity)
- `is_single_logical_unit()`: Minimal Output Principle check
- `enforce_minimal_output()`: Raises `CompositionViolationError` on arrays
- `ComposedPath`: Enhanced with output enforcement, `lift_all()`, `without_enforcement()`
- `IdentityPath`: Identity for AGENTESE path composition
- `SimpleMorphism` + `@morphism` decorator: Test helpers

### Phase 5 Test File

```
impl/claude/protocols/agentese/_tests/
└── test_laws.py      # 80 tests - category laws, minimal output, composition
```

### Phase 6 Files (COMPLETE)

```
impl/claude/protocols/agentese/
└── integration.py    # Integration layer (600 lines)
```

**Key Features**:
- `UmweltIntegration`: Extract AgentMeta from Umwelt DNA, affordance checking
- `MembraneAgenteseBridge`: CLI command → AGENTESE path mapping
- `LgentIntegration`: Registry lookup, node registration, usage tracking
- `GgentIntegration`: BNF grammar validation, path parsing
- `AgentesIntegrations`: Unified container with graceful degradation

**Membrane Command Mappings**:
- `observe` → `world.project.manifest`
- `sense` → `world.project.sense`
- `trace` → `time.trace.witness`
- `dream` → `self.memory.consolidate`

### Phase 6 Test File

```
impl/claude/protocols/agentese/_tests/
└── test_integration.py   # 81 tests - all four integrations
```

### Phase 7 Files (COMPLETE)

```
impl/claude/protocols/agentese/
└── wiring.py         # WiredLogos + factory functions (400 lines)
```

**Key Features**:
- `WiredLogos`: Production resolver with all integrations wired
- G-gent path validation before resolve/invoke
- L-gent usage tracking after invocations
- UmweltIntegration for observer meta extraction
- Membrane bridge for CLI command translation
- Factory functions: `create_wired_logos()`, `wire_existing_logos()`, `create_minimal_wired_logos()`

### Phase 7 Test File

```
impl/claude/protocols/agentese/_tests/
└── test_wiring.py    # 44 tests - WiredLogos, integration wiring
```

### Phase 8 Files (COMPLETE)

```
impl/claude/protocols/agentese/
└── adapter.py         # Natural language adapter (500 lines)
```

**Key Features**:
- `TranslationResult`: Immutable result with path, confidence, source
- `TranslationError`: Sympathetic error with suggestions
- `PatternTranslator`: Fast path - 35+ rule-based patterns
- `LLMTranslator`: Slow path - few-shot prompting fallback
- `AgentesAdapter`: Unified orchestrator

### Phase 8 Test File

```
impl/claude/protocols/agentese/_tests/
└── test_adapter.py    # 71 tests - pattern translation, LLM, adapter
```

---

## Instance DB Phase 6: Observability + Dashboard (✅ COMPLETE)

Implemented Phase 6 of the Bicameral Engine: O-gent/W-gent/I-gent integration for real-time cortex health monitoring.

| Component | Description | Location | Tests |
|-----------|-------------|----------|-------|
| `CortexObserver` | O-gent observer for Bicameral ops | `agents/o/cortex_observer.py` | 29 |
| `MetricsExporter` | Prometheus/OpenTelemetry/JSON export | `agents/o/metrics_export.py` | 21 |
| `CortexDashboard` | W-gent wire protocol dashboard | `agents/w/cortex_dashboard.py` | 25 |
| `DreamReportRenderer` | I-gent rendering of dream reports | `agents/i/dream_view.py` | 42 |
| **Total Implemented** | | | **117** |

### CortexObserver (`agents/o/cortex_observer.py`)

```python
from agents.o import CortexObserver, create_cortex_observer

# Create observer wrapping bicameral memory
observer = create_cortex_observer(
    bicameral=bicameral_memory,
    synapse=synapse,
    hippocampus=hippocampus,
    dreamer=lucid_dreamer,
)

# Observe dimension health
health = observer.get_health()
# → CortexHealth(coherency, synapse, hippocampus status)

# Subscribe to health changes
unsubscribe = observer.on_health_change(lambda h: print(f"Health: {h}"))
```

### CortexDashboard (`agents/w/cortex_dashboard.py`)

```python
from agents.w import CortexDashboard, create_cortex_dashboard

dashboard = create_cortex_dashboard(observer=cortex_observer)
await dashboard.start()
# → Wire files at .wire/cortex-dashboard/

print(dashboard.render_compact())
# → [CORTEX] ✓ COHERENT | L:45ms R:12ms | H:45/100 | S:0.3 | Dreams:12
```

**Key Metrics:**
- `cortex_coherency_rate` - Cross-hemisphere validation success rate
- `cortex_ghost_healed_total` - Ghost memories auto-healed
- `cortex_synapse_surprise_avg` - Average surprise across signals
- `cortex_hippocampus_size` - Short-term memory utilization
- `cortex_dream_cycles_total` - REM cycles completed

---

## M-gent Holographic Cartography (COMPLETE)

**Location**: `impl/claude/agents/m/`
**Plan**: `docs/m-gent-cartography-enhancement-plan.md`
**Tests**: 114 passed

### The Core Question

> "What is the most perfect context injection that can be given to an agent for any given turn?"

**Answer**: Not a search result—a *map* that shows position, adjacency, and horizon.

### Architecture

```
L-gent (terrain)     N-gent (traces)     B-gent (budget)
      ↓                    ↓                    ↓
      └────────────────────┴────────────────────┘
                           ↓
                   CartographerAgent
                           ↓
                        HoloMap
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
       PathfinderAgent          ContextInjector
              ↓                         ↓
       NavigationPlan            OptimalContext
```

### Files

| File | Purpose | Tests |
|------|---------|-------|
| `cartography.py` | Core types (HoloMap, Attractor, WeightedEdge, Horizon) | 47 |
| `cartographer.py` | CartographerAgent + DesireLineComputer | 42 |
| `pathfinder.py` | PathfinderAgent + PathAnalysis | 11 |
| `context_injector.py` | ContextInjector + foveation | 14 |

### Key Concepts

| Concept | Definition | Source |
|---------|------------|--------|
| **Landmark (Attractor)** | Dense cluster of memories | L-gent clustering |
| **Desire Line** | Historical transition probability | N-gent traces |
| **Void** | Unexplored region ("Here be dragons") | Density analysis |
| **Horizon** | Progressive disclosure boundary | B-gent budget |
| **Foveation** | Sharp center, blurry edges | Human vision model |

### Integration Points

- **L-gent**: Provides embedding space via `VectorSearchable` protocol
- **N-gent**: Provides traces via `TraceQueryable` protocol
- **B-gent**: Constrains resolution via token budget

---

## Unified Cortex: Infrastructure Layer v2.0

**Plan**: `docs/instance-db-implementation-plan.md`
**Location**: `protocols/cli/instance_db/` (Phase 1 OPERATIONAL)

### Auto-Bootstrap (Default Behavior)

The CLI now **auto-bootstraps** the cortex on every command. No manual setup needed!

```bash
# Just run any command - DB is created automatically
kgents pulse     # Creates ~/.local/share/kgents/membrane.db on first run
kgents check .   # Instance registered, telemetry logged
```

**What happens on startup:**
1. Detects XDG paths (`~/.local/share/kgents/`, `~/.config/kgents/`)
2. Creates SQLite DB if config exists (or uses defaults)
3. Runs migrations (creates tables)
4. Registers instance (hostname, PID, project path)
5. Logs `instance.started` telemetry event

**What happens on shutdown:**
1. Marks instance as `terminated`
2. Logs `instance.stopped` telemetry event
3. Closes all DB connections

**Flags:**
- `--no-bootstrap`: Skip auto-bootstrap (run in degraded mode)
- `-v/--verbose`: Show bootstrap/shutdown details

**Messaging Hierarchy** (see `spec/principles.md` - Transparent Infrastructure):
- First run: Green message showing where data lives
- Degraded mode: Yellow warning
- Verbose mode: Gray details (instance ID, mode)
- Normal: Silent success

### Wipe Command

Remove databases with confirmation:

```bash
kgents wipe local          # Remove project DB (.kgents/) - requires confirmation
kgents wipe global         # Remove global DB (~/.local/share/kgents/) - requires confirmation
kgents wipe all            # Remove both - requires confirmation

kgents wipe global --force # Skip confirmation (use with caution!)
kgents wipe all --dry-run  # Show what would be deleted without deleting
```

### Manual Setup (Optional)

For custom configuration:

```bash
# Create infrastructure.yaml to customize providers
cat > ~/.config/kgents/infrastructure.yaml << 'EOF'
profile: local-canonical
providers:
  relational: { type: sqlite, connection: "${XDG_DATA_HOME}/kgents/membrane.db" }
  vector: { type: numpy, path: "${XDG_DATA_HOME}/kgents/vectors.json", dimensions: 384 }
  blob: { type: filesystem, path: "${XDG_DATA_HOME}/kgents/blobs" }
  telemetry: { type: sqlite, connection: "${XDG_DATA_HOME}/kgents/telemetry.db" }
EOF
```

### Phase Status

| Phase | Description | Status | Tests |
|-------|-------------|--------|-------|
| 1 | Core Infrastructure + Lifecycle | ✅ OPERATIONAL | 85 |
| 2 | Synapse + Active Inference | ✅ COMPLETE | 46 |
| 3 | D-gent Backend Adapters | ✅ COMPLETE | 69 |
| 4 | Composting + Lethe Protocol | ✅ COMPLETE | 73 |
| 5 | Dreaming + Maintenance | ✅ COMPLETE | 74 |
| 6 | Observability + Dashboard | ✅ COMPLETE | 117 |

### File Structure (`protocols/cli/instance_db/`)

| File | Purpose |
|------|---------|
| `interfaces.py` | IRelationalStore, IVectorStore, IBlobStore, ITelemetryStore |
| `storage.py` | XDGPaths, StorageProvider, InfrastructureConfig |
| `lifecycle.py` | LifecycleManager, OperationMode, quick_bootstrap |
| `providers/sqlite.py` | SQLite + Numpy + Filesystem implementations |

### Graceful Degradation

| Mode | Condition | Storage |
|------|-----------|---------|
| **FULL** | Global + Project DB exist | Both |
| **GLOBAL_ONLY** | `~/.local/share/kgents/membrane.db` exists | Global |
| **LOCAL_ONLY** | `.kgents/cortex.db` exists | Project |
| **DB_LESS** | No DB, no config | In-memory |

---

## Semantic Field: Current State

Base implementation with 43 tests covering:
- Psi-gent: METAPHOR emission
- F-gent: METAPHOR sensing + INTENT emission
- J-gent: WARNING emission
- B-gent: OPPORTUNITY/SCARCITY emission
- M-gent: MEMORY emission/sensing
- N-gent: NARRATIVE emission/sensing
- O-gent: Universal observer sensor

## Next: Semantic Field Phases 1-4 (Planned)

See `docs/semantic-field-integration-plan.md` for planned expansion:
- Phase 1: E-gent, H-gent, K-gent, R-gent emitters/sensors
- Phase 2: Cross-signal sensing
- Phase 3: D-gent, T-gent, W-gent infrastructure
- Phase 4: L-gent CAPABILITY signals

---

## Previous: Instance DB Phase 5 - Lucid Dreaming + Neurogenesis (✅ Complete)

Implemented Phase 5 of the Bicameral Engine: Interruptible maintenance and self-evolving schema.

| Component | Tests | Purpose |
|-----------|-------|---------|
| `dreamer.py` | 37 | LucidDreamer, NightWatch, DreamPhase, Morning Briefing |
| `neurogenesis.py` | 37 | SchemaNeurogenesis, TypeInferrer, MigrationProposal |
| **Total New** | **74** | |

### LucidDreamer (`protocols/cli/instance_db/dreamer.py`)

```python
from protocols.cli.instance_db import (
    LucidDreamer,
    DreamerConfig,
    create_lucid_dreamer,
)

# Create dreamer with synapse + hippocampus
dreamer = create_lucid_dreamer(
    synapse=synapse,
    hippocampus=hippocampus,
    config_dict={
        "interrupt_check_ms": 100,
        "flashbulb_wakes": True,
    },
)

# Run REM cycle (interruptible)
report = await dreamer.rem_cycle()
# → Flushes hippocampus, runs maintenance, generates questions

# Check morning briefing
for question in dreamer.morning_briefing:
    print(f"Q: {question.question_text}")
    dreamer.answer_question(question.question_id, "Yes")
```

### Schema Neurogenesis (`protocols/cli/instance_db/neurogenesis.py`)

```python
from protocols.cli.instance_db import (
    SchemaNeurogenesis,
    create_schema_neurogenesis,
)

# Create with introspector
neurogenesis = create_schema_neurogenesis(introspector)

# Analyze JSON blobs for patterns
proposals = await neurogenesis.analyze()

# Review proposals
for p in proposals:
    print(f"{p.action}: {p.column_name}")
    print(f"  Confidence: {p.confidence:.1%}")
    print(f"  SQL: {p.to_sql()}")

# Approve and execute
neurogenesis.approve(proposals[0].proposal_id)
await neurogenesis.execute_approved()
```

**Key Concepts:**
- **NightWatch**: Scheduler for REM cycles (configurable time, manual triggers)
- **Morning Briefing**: Questions accumulated during dreaming for human review
- **Interruptible**: Maintenance yields to high-surprise (flashbulb) signals
- **Pattern Clusters**: JSON key patterns with type inference
- **Migration Proposals**: Approved before execution (human-in-the-loop)

---

## Previous: M-gent Phase 5 Cartography (✅ Complete)

Implemented Holographic Cartography: Memory-as-Orientation instead of Memory-as-Retrieval.

| Component | Tests | Purpose |
|-----------|-------|---------|
| `cartography.py` | 47 | HoloMap, Attractor, WeightedEdge, Horizon, Void, ContextVector |
| `cartographer.py` | 42 | CartographerAgent, DesireLineComputer, clustering |
| `pathfinder.py` | 11 | PathfinderAgent, desire line navigation, bushwhacking |
| `context_injector.py` | 14 | ContextInjector, foveation, budget-constrained rendering |
| `cartography_integrations.py` | 43 | O-gent/Ψ-gent/I-gent integrations |
| **Total** | **157** | |

### CartographerAgent (`agents/m/cartographer.py`)

```python
from agents.m import (
    CartographerAgent,
    create_cartographer,
    create_mock_cartographer,
)

# Create cartographer with L-gent vector search + N-gent traces
cartographer = create_cartographer(
    vector_search=lgent_backend,
    trace_store=ngent_historian,
)

# Generate HoloMap centered on current context
holo_map = await cartographer.invoke(context_vector, Resolution.ADAPTIVE)

# Map contains:
# - landmarks: Dense memory clusters (Attractors)
# - desire_lines: Historical paths (WeightedEdges)
# - voids: Unexplored regions
# - horizon: Progressive disclosure boundary
```

### PathfinderAgent (`agents/m/pathfinder.py`)

```python
from agents.m import PathfinderAgent, create_pathfinder, Goal

pathfinder = create_pathfinder(cartographer=cartographer)

# Navigate via desire lines (historical paths)
plan = await pathfinder.invoke(Goal(
    current_context=here,
    target=there,
))

# plan.mode: "desire_line" (safe) or "exploration" (risky)
# plan.confidence: Based on path strength
# plan.waypoints: Landmarks to traverse
```

### ContextInjector (`agents/m/context_injector.py`)

```python
from agents.m import ContextInjector, inject_context

# The answer to: "What is the most perfect context injection?"
optimal = await inject_context(
    current_context=context_vector,
    goal=target_concept,
    budget=1000,  # Token budget
)

# Returns foveated view:
# - focal_memories: Full detail for current + goal
# - peripheral_summaries: Blurred adjacent areas
# - desire_lines: Navigation hints
# - void_warnings: "Here be dragons"
```

**Key Concepts:**
- **Landmark/Attractor**: Dense memory cluster
- **Desire Line**: Historical transition probability (from N-gent traces)
- **Void**: Unexplored region
- **Horizon**: Progressive disclosure boundary
- **Foveation**: High detail at center, blur at edges (like human vision)

### Phase 5 Polish: Cross-Agent Integrations (`agents/m/cartography_integrations.py`)

```python
from agents.m import (
    # O-gent: Map health monitoring
    CartographicObserver,
    create_cartographic_observer,
    MapHealth,

    # Ψ-gent: Metaphor discovery
    MetaphorLocator,
    create_metaphor_locator,

    # I-gent: Visualization
    MapRenderer,
    create_map_renderer,
    annotate_and_render,
)

# O-gent: Annotate map with health metrics
observer = create_cartographic_observer(telemetry_store=my_store)
annotated_map = observer.annotate_map(holo_map)
health = observer.assess_health(holo_map)
# health.overall_health, health.drifting_landmarks, health.stale_edges

# Ψ-gent: Find metaphors near a problem
locator = create_metaphor_locator(metaphor_registry=psi_corpus)
neighborhood = locator.find_metaphor_neighborhood(problem_embedding, holo_map)
best_metaphor = neighborhood.best_match

# I-gent: Render map to terminal
renderer = create_map_renderer()
ascii_map = renderer.render_ascii(holo_map)  # ASCII art map
summary = renderer.render_summary(holo_map)  # Text summary
health_panel = renderer.render_health_panel(health)  # Status display

# Convenience: All-in-one
annotated, summary, health = annotate_and_render(holo_map)
```

---

## Previous: Phase 4 Composting + Lethe (✅ Complete)

Implemented Instance DB Phase 4: Memory compression with sketching algorithms and cryptographic forgetting.

| Component | Tests | Purpose |
|-----------|-------|---------|
| `compost.py` | 34 | CompostBin, NutrientBlock, Count-Min Sketch, HyperLogLog, T-Digest |
| `lethe.py` | 31 | LetheStore, ForgetProof, RetentionPolicy, LetheGardener |
| `test_garden_integration.py` | 8 | MemoryGarden lifecycle integration |
| **Total New** | **73** | |

### Composting System (`protocols/cli/instance_db/compost.py`)

```python
from protocols.cli.instance_db import (
    CompostBin,
    NutrientBlock,
    create_compost_bin,
)

# Create compost bin with sketching algorithms
bin = CompostBin()
for signal in signals:
    bin.add(signal)

# Seal to create NutrientBlock (compressed statistics)
block = bin.seal("epoch-001")

# Query approximate statistics O(1)
freq = block.get_frequency("signal_type:error")  # Count-Min Sketch
cardinality = block.get_cardinality("user_id")   # HyperLogLog
p95 = block.get_quantile("latency", 0.95)        # T-Digest

# Merge blocks for hierarchical compression
combined = block1.merge(block2)
```

### Lethe Store (`protocols/cli/instance_db/lethe.py`)

```python
from protocols.cli.instance_db import (
    LetheStore,
    RetentionConfig,
    create_lethe_store,
)

# Create with retention policy
store = create_lethe_store(
    retention_config={
        "hot_days": 30,      # Keep fully accessible
        "warm_days": 365,    # Archive tier
        "compost_days": 730, # Compress to statistics only
    }
)

# Cryptographic forget with proof (GDPR compliant)
proof = await store.forget(epoch)
assert store.verify_proof(proof)  # Verifiable deletion

# Compost then forget (preserve nutrients, delete raw data)
block, proof = await store.compost_then_forget(epoch, signals)

# Audit log for compliance
log = store.get_audit_log(operation="forget")
```

**Retention Tiers:**
- **HOT** (< 30 days): Full access, no processing
- **WARM** (30-365 days): Archive, slower access
- **COMPOST** (365-730 days): Compress to statistics
- **FORGET** (> 730 days): Cryptographic deletion with proof

---

## Previous: Import Cleanup + SemanticField Integration Hardening (✅ Complete)

Fixed all 11 documented import violations and added SemanticField emitters/sensors for M-gent, N-gent, and O-gent.

### Import Violation Fixes

| Violation | Solution | Files Changed |
|-----------|----------|---------------|
| B×{K,H,A} (robin.py) | Renamed to `robin_integration.py` | `agents/b/` |
| B×{K,H} (robin_morphisms.py) | Renamed to `robin_morphisms_integration.py` | `agents/b/` |
| F×J (reality_contracts.py) | Renamed to `j_integration.py` | `agents/f/` |
| C×J (functor.py) | Extracted Promise to `j_integration.py` | `agents/c/` |
| B×A (hypothesis.py) | Made A-gent foundational | `test_ecosystem_verification.py` |
| shared×F (fixtures.py) | Renamed to `fixtures_integration.py` | `agents/shared/` |

**Foundational agents**: shared, **a**, d, l, c (A-gent added for skeleton types)

### SemanticField Integration (M/N/O-gent)

New emitters and sensors for decoupled agent coordination:

```python
from agents.i.semantic_field import (
    # M-gent: Memory consolidation signals
    create_memory_emitter, create_memory_sensor,
    MemoryPayload,

    # N-gent: Narrative/story signals
    create_narrative_emitter, create_narrative_sensor,
    NarrativePayload,

    # O-gent: Universal observer (sees all pheromones)
    create_observer_sensor,
    ObserverFieldSensor,
)

# M-gent emits memory consolidation signal
memory = create_memory_emitter(field)
memory.emit_consolidation("mem_001", importance=0.8, position=pos)

# N-gent emits story event
narrator = create_narrative_emitter(field)
narrator.emit_story_event("session", "climax", "User solved the bug!", pos)

# O-gent observes everything
observer = create_observer_sensor(field)
summary = observer.field_summary()  # {"metaphor": 2, "warning": 1, ...}
```

New tests: +13 (semantic_field.py now has 43 tests)

---

## Previous: Phase 3 D-gent Adapters + Bicameral Memory (✅ Complete)

Implemented Instance DB Phase 3: D-gent backend adapters and Bicameral Memory with ghost detection + self-healing.

| Component | Tests | Purpose |
|-----------|-------|---------|
| `infra_backends.py` | 35 | InstanceDBVectorBackend, InstanceDBRelationalBackend, CortexAdapter |
| `bicameral.py` | 34 | BicameralMemory, Coherency Protocol, Ghost Detection + Self-Healing |
| **Total New** | **69** | |

### Infrastructure Backends (`agents/d/infra_backends.py`)

```python
from agents.d import (
    InstanceDBVectorBackend,
    InstanceDBRelationalBackend,
    CortexAdapter,
    create_cortex_adapter,
)

# Create cortex adapter for Bicameral operations
adapter = create_cortex_adapter(
    relational_store=sqlite_store,  # Left Hemisphere
    vector_store=numpy_store,        # Right Hemisphere
)

# Store with both hemispheres
await adapter.store("insight-001", {"type": "insight", "text": "..."})

# Semantic recall with coherency validation
results = await adapter.recall("category theory patterns")
```

### Bicameral Memory (`agents/d/bicameral.py`)

```python
from agents.d import (
    BicameralMemory,
    create_bicameral_memory,
    CoherencyReport,
)

# Create bicameral memory with ghost healing
bicameral = create_bicameral_memory(
    relational_store=sqlite_store,
    vector_store=vector_store,
    embedding_provider=embedder,
    auto_heal_ghosts=True,        # Self-healing enabled
    flag_stale_on_recall=True,    # Staleness detection
)

# Semantic recall validates against relational (heals ghosts automatically)
results = await bicameral.recall("insight about X")
# → Ghost memories filtered out and healed

# Check coherency health
report = await bicameral.coherency_check(sample_size=100)
print(f"Coherency rate: {report.coherency_rate:.1%}")
```

**Coherency Protocol:**
- Left Hemisphere (relational) is source of truth
- Right Hemisphere (vector) validated on recall
- Ghost Memory: Vector → deleted row → auto-healed
- Stale Embedding: content_hash mismatch → flagged

---

## Previous: W-gent Interceptors + Integration Tests (✅ Complete)

New W-gent production interceptors and cross-agent integration tests:

| Component | Tests | Purpose |
|-----------|-------|---------|
| W-gent Interceptors | 45 | MeteringInterceptor (B), SafetyInterceptor (J), TelemetryInterceptor (O), PersonaInterceptor (K) |
| C-gent Integration | 35 | Functor/Monad laws, lifted composition |
| H-gent Integration | 25 | Hegel×Lacan×Jung pipelines, M-gent memory |
| K-gent Integration | 20 | Dialogue modes, persona persistence |
| **Total** | **125** | |

### W-gent Interceptors (`agents/w/interceptors.py`)

```python
from agents.w.interceptors import create_standard_interceptors

interceptors = create_standard_interceptors(
    treasury=my_treasury,       # B-gent token budget
    thresholds=SafetyThresholds(max_entropy=0.8),  # J-gent
    priors=PersonaPriors(risk_tolerance=0.3),      # K-gent
)
bus = create_bus(*interceptors)
```

Order: Safety(50) → Metering(100) → Telemetry(200) → Persona(300)

---

## Phase 5 Ecosystem Verification (✅ Complete)

Validates C-gent functor laws and import patterns:

| Test Suite | Tests | Status |
|------------|-------|--------|
| Functor Laws (Maybe, Either, List) | 6 | ✅ |
| Monad Laws (Left/Right Identity, Associativity) | 3 | ✅ |
| Category Laws (Composition Associativity) | 3 | ✅ |
| Import Audit | 4 | ✅ |
| SemanticField Usage | 4 | ✅ |
| **Total** | **20** | |

### Import Audit Summary

- **35 cross-agent imports** found
- **35 acceptable** (foundational agents A/D/L/C/shared, or *_integration.py files)
- **0 violations** (all fixed - see "Recent" section above)

### Integration-by-Field Pattern

Agents coordinate via `SemanticField` (pheromones) instead of direct imports:

```python
field = create_semantic_field()
psi = create_psi_emitter(field)
forge = create_forge_sensor(field)

# Psi emits metaphor (doesn't know about Forge)
psi.emit_metaphor("query optimization", "graph traversal", 0.85, position)

# Forge senses metaphor (doesn't know about Psi)
metaphors = forge.sense_metaphors(position, radius=1.0)
```

See: `protocols/_tests/test_ecosystem_verification.py`

---

## Instance DB - Bicameral Engine (Phase 1-6)

Implemented the Bicameral Engine with Active Inference, short-term memory, D-gent adapters, memory compression, lucid dreaming, and observability:

| Phase | Component | Tests | Status |
|-------|-----------|-------|--------|
| 1 | Core Infrastructure | 85 | ✅ |
| 1.5 | Spinal Cord (`nervous.py`) | 31 | ✅ |
| 2 | Synapse + Active Inference | 46 | ✅ |
| 2.5 | Hippocampus | 37 | ✅ |
| 3 | D-gent Adapters + Bicameral | 69 | ✅ |
| 4 | Composting + Lethe | 73 | ✅ |
| 5 | Lucid Dreaming + Neurogenesis | 74 | ✅ |
| 6 | Observability + Dashboard | 117 | ✅ |
| **Total** | | **532** | All Complete |

### Synapse (Active Inference Event Bus)

```python
synapse = Synapse(telemetry_store, SynapseConfig(
    surprise_threshold=0.5,
    flashbulb_threshold=0.9,
))
synapse.on_fast_path(handler)
await synapse.fire(Signal(signal_type="test", data={}))
```

- `PredictiveModel`: O(1) exponential smoothing
- Routes: flashbulb (>0.9), fast (>0.5), batch (<0.5)
- Automatic batching with `flush_batch()`
- `peek_recent()` / `has_flashbulb_pending()` for interrupts

### Hippocampus (Short-Term Memory)

```python
hippocampus = Hippocampus()
await hippocampus.remember(signal)
result = await hippocampus.flush_to_cortex()  # Creates LetheEpoch
```

- `LetheEpoch`: Sealed memory boundaries for forgetting
- Flush strategies: on_sleep, on_size, on_age, manual
- `SynapseHippocampusIntegration`: Wires synapse → hippocampus

## Instance DB Files

```
protocols/cli/instance_db/           # Infrastructure layer
├── interfaces.py    # IRelationalStore, IVectorStore, etc.
├── storage.py       # StorageProvider, XDGPaths
├── lifecycle.py     # LifecycleManager, OperationMode
├── nervous.py       # NervousSystem (Spinal Cord)
├── synapse.py       # Synapse (Active Inference)
├── hippocampus.py   # Hippocampus (Short-Term Memory)
├── compost.py       # CompostBin, NutrientBlock, Sketching algorithms
├── lethe.py         # LetheStore, ForgetProof, RetentionPolicy
├── dreamer.py       # LucidDreamer, NightWatch, REM cycles (Phase 5)
├── neurogenesis.py  # SchemaNeurogenesis, MigrationProposal (Phase 5)
└── providers/sqlite.py

agents/d/                            # D-gent adapters (Phase 3)
├── infra_backends.py  # InstanceDBVectorBackend, InstanceDBRelationalBackend, CortexAdapter
├── bicameral.py       # BicameralMemory, Coherency Protocol, Ghost Self-Healing
└── ...

agents/o/                            # O-gent observability (Phase 6)
├── cortex_observer.py  # CortexObserver, CortexHealthSnapshot
└── metrics_export.py   # PrometheusExporter, OpenTelemetryExporter, JSONExporter

agents/w/                            # W-gent dashboard (Phase 6)
└── cortex_dashboard.py  # CortexDashboard, SparklineData

agents/i/                            # I-gent rendering (Phase 6)
└── dream_view.py        # render_dream_report, render_morning_briefing
```

## Agent Reference

| Agent | Purpose | Key File |
|-------|---------|----------|
| W | Wire/Middleware Bus | `agents/w/bus.py` |
| E | Thermodynamic evolution | `agents/e/cycle.py` |
| M | Context cartography | `agents/m/cartographer.py` |
| Psi | Metaphor solving | `agents/psi/v3/engine.py` |
| L | Semantic embeddings | `agents/l/semantic_registry.py` |
| B | Token economics | `agents/b/metered_functor.py` |
| N | Narrative traces | `agents/n/chronicle.py` |
| O | Observation hierarchy | `agents/o/observer.py` |

## Commands

```bash
pytest -m "not slow" -q        # Fast, quiet output
pytest -m "not slow" -v        # Fast, verbose (local debugging only)
pytest protocols/cli/instance_db/_tests/ -v  # Instance DB tests
kgents check .                 # Validate (auto-bootstraps DB)
```

**CI Note**: CI uses `-q` (quiet) to reduce log verbosity. Use `-v` locally for debugging.

## API Notes

- `PredictiveModel.update(signal_type)` → returns surprise [0,1]
- `Synapse.fire(signal)` → DispatchResult with route
- `Hippocampus.flush_to_cortex()` → FlushResult with epoch_id
- Signal surprise thresholds: 0.5 (fast), 0.9 (flashbulb)
