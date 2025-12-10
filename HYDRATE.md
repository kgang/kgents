# HYDRATE.md - kgents Session Context

**Status**: All Tests Passing | ~5,620 tests | Branch: `main`

## Recent: Instance DB - Bicameral Engine (Phase 2-2.5)

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
pytest -m "not slow" -n auto   # Fast (~6s)
pytest protocols/cli/instance_db/_tests/ -v  # Instance DB tests
kgents check .                 # Validate (auto-bootstraps DB)
```

## API Notes

- `PredictiveModel.update(signal_type)` → returns surprise [0,1]
- `Synapse.fire(signal)` → DispatchResult with route
- `Hippocampus.flush_to_cortex()` → FlushResult with epoch_id
- Signal surprise thresholds: 0.5 (fast), 0.9 (flashbulb)
