# HYDRATE.md - kgents Session Context

**Status**: All Tests Passing | ~5,897 tests | Branch: `main`

## Recent: Instance DB Phase 5 - Lucid Dreaming + Neurogenesis (✅ Complete)

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

## Instance DB - Bicameral Engine (Phase 1-5)

Implemented the Bicameral Engine with Active Inference, short-term memory, D-gent adapters, memory compression, and lucid dreaming:

| Phase | Component | Tests | Status |
|-------|-----------|-------|--------|
| 1 | Core Infrastructure | 85 | ✅ |
| 1.5 | Spinal Cord (`nervous.py`) | 31 | ✅ |
| 2 | Synapse + Active Inference | 46 | ✅ |
| 2.5 | Hippocampus | 37 | ✅ |
| 3 | D-gent Adapters + Bicameral | 69 | ✅ |
| 4 | Composting + Lethe | 73 | ✅ |
| 5 | Lucid Dreaming + Neurogenesis | 74 | ✅ |
| **Total** | | **415** | |

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
