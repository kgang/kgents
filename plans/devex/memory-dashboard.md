---
path: plans/devex/memory-dashboard
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Four Pillars Memory Dashboard

> **Status**: active
> **Progress**: Phase 4 in progress
> **Last touched**: 2025-12-13
> **Touched by**: claude-opus-4.5

AGENTESE pointer: canonical handle/law spec lives in `spec/protocols/agentese.md`; update this plan when handles change.

## Overview

The Four Pillars Memory Dashboard visualizes M-gent memory architecture through I-gent screens:

| Pillar | Component | Purpose |
|--------|-----------|---------|
| Memory Crystal | `MemoryCrystal[T]` | Holographic patterns with resolution levels |
| Pheromone Field | `PheromoneField` | Stigmergic traces and gradients |
| Active Inference | `ActiveInferenceAgent` | Free energy budgets and beliefs |
| Language Games | `LanguageGame[T]` | Wittgensteinian memory access |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    I-gent Dashboard Layer                    │
│  MemoryMapScreen (LOD 2) ← Cockpit ← Observatory            │
├─────────────────────────────────────────────────────────────┤
│                    MemoryDataProvider                        │
│  CrystalStats | FieldStats | InferenceStats | HealthReport  │
├─────────────────────────────────────────────────────────────┤
│                    M-gent Memory Layer                       │
│  MemoryCrystal | PheromoneField | ActiveInferenceAgent      │
├─────────────────────────────────────────────────────────────┤
│                    Ghost Infrastructure                      │
│  MemoryCollector → GlassCacheManager → ~/.kgents/ghost/     │
└─────────────────────────────────────────────────────────────┘
```

## Key Files

| File | Purpose |
|------|---------|
| `impl/claude/agents/i/data/memory_provider.py` | Central data provider for Four Pillars |
| `impl/claude/agents/i/screens/memory_map.py` | MemoryMapScreen (LOD 2 visualization) |
| `impl/claude/agents/i/data/pheromone.py` | Pheromone trail visualization |
| `impl/claude/infra/ghost/collectors.py` | Ghost collectors including MemoryCollector |
| `impl/claude/infra/ghost/cache.py` | GlassCacheManager for persistence |

## Implementation Phases

### Phase 1: Core Integration (COMPLETE)
- [x] MemoryDataProvider with demo mode
- [x] CrystalStats, FieldStats, InferenceStats TypedDicts
- [x] MemoryHealthReport with weighted scoring
- [x] Factory functions (sync and async)

### Phase 2: Screen Integration (COMPLETE)
- [x] MemoryMapScreen with 4-panel grid
- [x] Reactive data binding (crystal_data, field_data, inference_data)
- [x] Resolution heat map visualization
- [x] Pheromone gradient bars
- [x] Belief distribution visualization
- [x] Free energy budget indicators
- [x] Keyboard bindings (r=refresh, c=consolidate, d=decay)

### Phase 3: Persistence & Activity (COMPLETE)
- [x] MemoryHealthPanel in Cockpit
- [x] MRI crystal integration
- [x] MemoryCollector for Ghost infrastructure
- [x] _simulate_activity for real-time demo
- [x] This documentation

### Phase 4: Ghost Integration & CLI (IN PROGRESS)
- [x] memory_summary.json in Ghost Daemon projection
- [x] `kg memory status` CLI command
- [x] `kg memory detail` for full breakdown
- [x] `kg memory --ghost` for cached data
- [ ] Live agent memory connection (replace demo_mode with real M-gent data)

## MemoryDataProvider API

```python
from agents.i.data.memory_provider import (
    MemoryDataProvider,
    create_memory_provider,
    create_memory_provider_async,
)

# Demo mode with synthetic data
provider = create_memory_provider(demo_mode=True)

# Get statistics
crystal_stats = provider.get_crystal_stats()
field_stats = await provider.get_field_stats()
inference_stats = provider.get_inference_stats()

# Health computation
health = provider.compute_health()
# Returns: MemoryHealthReport with health_score, crystal_health, field_health, inference_health, status

# Status bar indicator
indicator = provider.render_health_indicator()
# Returns: "MEM: [#1dd1a1]85%[/]" (colored by status)
```

## Health Computation

The health score is a weighted average:

| Component | Weight | Metric |
|-----------|--------|--------|
| Crystal | 40% | Average resolution across patterns |
| Field | 30% | (deposits/10 + trace_exists)/2 |
| Inference | 30% | min(precision/1.5, 1.0) |

**Status Thresholds**:
- `HEALTHY`: score >= 0.7
- `DEGRADED`: score >= 0.4
- `CRITICAL`: score < 0.4

## Demo Data Patterns

In demo mode, MemoryDataProvider creates:

**Crystal Patterns**:
| Pattern | Resolution | Temperature |
|---------|------------|-------------|
| python_async | 0.90 | Hot |
| rust_ownership | 0.85 | Hot |
| typescript_generics | 0.60 | Warm |
| functional_patterns | 0.55 | Warm |
| docker_basics | 0.40 | Cool |
| old_api_notes | 0.20 (demoted) | Cold |

**Pheromone Traces**:
```
python:    coder(5.0) + reviewer(3.0) + test(2.0) = 10.0
rust:      coder(4.0) + test(1.5) = 5.5
typescript: coder(2.0) + reviewer(1.0) = 3.0
functional: coder(1.5) = 1.5
docker:    devops(0.5) = 0.5
```

**Belief Distribution**:
```
python: 35%  ████████████
rust: 25%   ██████████
typescript: 20%  ████████
functional: 12%  █████
other: 8%   ███
```

## Ghost Cache Integration

Memory state is persisted to Ghost Cache for cross-session continuity:

```python
# AGENTESE mapping
cache.write("memory/crystal", crystal_stats, agentese_path="self.memory.crystal.manifest")
cache.write("memory/field", field_stats, agentese_path="self.memory.field.manifest")
cache.write("memory/inference", inference_stats, agentese_path="self.memory.inference.manifest")
cache.write("memory/health", health_report, agentese_path="self.memory.health.manifest")
```

## Real-time Activity Simulation

The `_simulate_activity` method drives demo mode with realistic activity:

1. **Pattern Access**: Probabilistically access patterns (weighted by resolution)
2. **Pheromone Deposits**: Random trace deposits simulating agent activity
3. **Belief Updates**: Precision drift based on access patterns
4. **Decay**: Periodic evaporation of pheromone traces

## Open Questions

1. **Ghost Cache Granularity**: Full crystal patterns vs metadata only?
   - Full patterns: Enable cross-session recall
   - Metadata only: Reduce storage, faster loads
   - **Decision**: Start with metadata, add pattern export as feature

2. **Activity Simulation Rate**: How often should demo activity occur?
   - **Decision**: 100ms timer with variable activity probability

## Related Plans

- `plans/devex/hotdata-infrastructure.md` - HotData fixture system
- `plans/skills/polynomial-agent.md` - PolyAgent pattern
- `spec/protocols/agentese.md` - AGENTESE verb-first ontology
