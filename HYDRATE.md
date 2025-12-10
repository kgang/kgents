# HYDRATE.md - kgents Session Context

**Status**: All Tests Passing | ~5,595 tests | Branch: `main`

## Recent: W-gent Interceptors + Integration Tests (✅ Complete)

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
- **24 acceptable** (foundational agents D/L/C/shared, or *_integration.py files)
- **11 violations** documented (B×{A,K,H}, C×J, F×J, shared×F)

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

## Instance DB - Bicameral Engine (Phase 2-2.5)

Implemented the Active Inference event bus and short-term memory:

| Phase | Component | Tests | Status |
|-------|-----------|-------|--------|
| 1 | Core Infrastructure | 85 | ✅ |
| 1.5 | Spinal Cord (`nervous.py`) | 31 | ✅ |
| 2 | Synapse + Active Inference | 46 | ✅ |
| 2.5 | Hippocampus | 37 | ✅ |
| **Total** | | **199** | |

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
protocols/cli/instance_db/
├── interfaces.py    # IRelationalStore, IVectorStore, etc.
├── storage.py       # StorageProvider, XDGPaths
├── lifecycle.py     # LifecycleManager, OperationMode
├── nervous.py       # NervousSystem (Spinal Cord)
├── synapse.py       # Synapse (Active Inference)
├── hippocampus.py   # Hippocampus (Short-Term Memory)
└── providers/sqlite.py
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
