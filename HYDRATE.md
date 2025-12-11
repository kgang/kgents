# HYDRATE.md - kgents Session Context

**Status**: 6,800+ tests | Branch: `main`

## Current: K-Terrarium Phase 1 (In Progress)

Kubernetes-native agent isolation. Transform from Python processes → container boundaries.

**K-Terrarium CLI** (coming soon):
```bash
kgents infra init       # Create Kind cluster (idempotent)
kgents infra status     # Show cluster state
kgents infra stop       # Pause cluster (docker pause)
kgents infra start      # Resume cluster
kgents infra destroy    # Remove cluster (--force to skip confirm)
```

**K-Terrarium Phase 1 Files** (in progress):
- `infra/k8s/exceptions.py` - TerrariumError hierarchy (done)
- `infra/k8s/detection.py` - Environment detection (done, 12 tests)
- `infra/k8s/cluster.py` - Kind cluster lifecycle (done, 18 tests)
- `infra/k8s/__init__.py` - Public API exports (done)
- `protocols/cli/handlers/infra.py` - CLI handler (pending)
- `impl/images/` - Docker images (pending)

**K-Terrarium Phases**:
| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Foundation (Kind bootstrap, CLI) | In Progress |
| 2 | Q-gent (disposable execution) | Pending |
| 3 | Agent Operator (CRD-driven deploy) | Pending |
| 4 | B-gent Integration (ResourceQuotas) | Pending |

---

## DevEx V4 (Complete through Phase 2)

**CLI Commands**:
```bash
# Phase 1: Foundation
kgents status           # Cortex health at a glance
kgents dream            # LucidDreamer morning briefing
kgents map              # M-gent HoloMap visualization
kgents signal           # SemanticField state

# Phase 2: Sensorium
kgents ghost            # Project to .kgents/ghost/
kgents ghost --daemon   # Background projection
```

**DevEx V4 Phases**:
| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Foundation (CLI entry points) | Complete |
| 2 | Sensorium (.kgents/ghost/) | Complete |
| 3 | Neural Link (keystroke dynamics) | Pending |
| 4 | Shadow (speculative execution) | Pending |
| 5 | Rituals (calibration/confessional) | Pending |

**Phase 1 Files** (CLI handlers):
- `protocols/cli/handlers/status.py` - CortexDashboard CLI
- `protocols/cli/handlers/dream.py` - LucidDreamer CLI
- `protocols/cli/handlers/map.py` - HoloMap CLI
- `protocols/cli/handlers/signal.py` - SemanticField CLI

**Phase 2 Files** (Sensorium):
- `protocols/cli/devex/ghost_writer.py` - Living Filesystem projection
- `protocols/cli/handlers/ghost.py` - Ghost CLI handler

**Feedback Loops (Meta-Bootstrap)**:
| Loop | Signal | Storage |
|------|--------|---------|
| Test Flinch | pytest failures | `FlinchStore` → ITelemetryStore + JSONL |
| CI Signals | GitHub Actions | `.kgents/ghost/ci_signals.jsonl` |
| Git Crystal | git log/diff | Native git |

**Quick Commands**:
```bash
git log --oneline --since="8 hours ago"  # Session narrative
git diff --stat HEAD~10                   # Churn map
cat .kgents/ghost/test_flinches.jsonl | tail -5  # Recent flinches
```

---

## Completed Systems

### Instance DB - Bicameral Engine (532 tests)

| Phase | Component | Key Files |
|-------|-----------|-----------|
| 1-2 | Core + Synapse + Hippocampus | `instance_db/{synapse,hippocampus}.py` |
| 3 | D-gent Adapters + Bicameral | `agents/d/{bicameral,infra_backends}.py` |
| 4 | Composting + Lethe | `instance_db/{compost,lethe}.py` |
| 5 | Lucid Dreaming + Neurogenesis | `instance_db/{dreamer,neurogenesis}.py` |
| 6 | Observability + Dashboard | `agents/o/cortex_observer.py`, `agents/w/cortex_dashboard.py` |

**Quick Start**:
```python
# Bicameral Memory (Left=relational, Right=vector)
bicameral = create_bicameral_memory(relational, vector, embedder, auto_heal_ghosts=True)
results = await bicameral.recall("query")  # Ghost memories auto-healed

# Synapse (Active Inference)
synapse = Synapse(store, SynapseConfig(surprise_threshold=0.5, flashbulb_threshold=0.9))
await synapse.fire(signal)  # Routes: flashbulb (>0.9), fast (>0.5), batch (<0.5)

# LucidDreamer (Interruptible maintenance)
dreamer = create_lucid_dreamer(synapse, hippocampus)
report = await dreamer.rem_cycle()
```

### Semantic Field (71 tests)

Stigmergic coordination via pheromones - agents emit/sense signals without direct imports.

| Agent | Emits | Senses |
|-------|-------|--------|
| Psi | METAPHOR | - |
| F | INTENT | METAPHOR |
| J | WARNING | - |
| B | OPPORTUNITY, SCARCITY | - |
| M | MEMORY | MEMORY |
| N | NARRATIVE | NARRATIVE |
| L | CAPABILITY | CAPABILITY |
| O | - | All types |

```python
field = create_semantic_field()
emitter = create_psi_emitter(field)
emitter.emit_metaphor("source", "target", strength=0.85, position=pos)
```

### M-gent Cartography (157 tests)

Memory-as-Orientation: HoloMap, Attractors, Desire Lines, Voids, Foveation.

```python
cartographer = create_cartographer(vector_search, trace_store)
holo_map = await cartographer.invoke(context_vector, Resolution.ADAPTIVE)
# → landmarks, desire_lines, voids, horizon
```

### W-gent Interceptors (125 tests)

Pipeline: Safety(50) → Metering(100) → Telemetry(200) → Persona(300)

---

## Agent Quick Reference

| Agent | Purpose | Key File |
|-------|---------|----------|
| B | Token economics | `agents/b/metered_functor.py` |
| D | State/Memory | `agents/d/bicameral.py` |
| E | Thermodynamic evolution | `agents/e/cycle.py` |
| I | Interface/TUI | `agents/i/semantic_field.py` |
| K | Kent simulacra | `agents/k/persona.py` |
| L | Semantic search | `agents/l/semantic_registry.py` |
| M | Context cartography | `agents/m/cartographer.py` |
| N | Narrative traces | `agents/n/chronicle.py` |
| O | Observation | `agents/o/observer.py` |
| Psi | Metaphor solving | `agents/psi/engine.py` |
| W | Wire protocol | `agents/w/bus.py` |

---

## Commands

```bash
pytest -m "not slow" -q              # Fast tests, quiet
pytest impl/claude/agents/d/ -v      # Specific agent
kgents check .                       # Validate
```

---

## Coding Gotchas

| Issue | Fix |
|-------|-----|
| Python 3.12 syntax | Use `Generic[A]` + `TypeVar`, not `class Foo[A]:` |
| Cross-agent imports | Use `*_integration.py` files or SemanticField |
| Forward refs | `from __future__ import annotations` + `TYPE_CHECKING` |

**Foundational agents** (can be imported anywhere): `shared`, `a`, `d`, `l`, `c`

---

## Tech Debt Inventory

**74 TODOs** across 33 files. Key clusters:

| Area | Count | Notes |
|------|-------|-------|
| J-gent templates | 8 | `templates.py` - placeholder implementations |
| T-gent MCP | 6 | `mcp_client.py`, `permissions.py` - HTTP transport, D/W-gent integration |
| CLI membrane | 3 | `membrane_cli.py` - history/persistence TODO |
| Concept context | 1 | `concept.py:452` - core ops unimplemented |

**56 skipped tests** (graceful): Redis/SQL backends, DSPy, external LLM deps.

**Low-priority**:
- ~289 `NotImplementedError`/`pass` stubs (many are intentional protocol placeholders)
- J-gent `templates.py` generates TODOs by design (JIT compilation markers)
