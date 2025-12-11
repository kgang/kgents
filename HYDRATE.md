# HYDRATE.md - kgents Session Context

**Status**: ~6,122 tests passing | Branch: `main`

## Current: DevEx Bootstrap Plan v2 (📋 PLANNING)

See `docs/devex-bootstrap-plan.md` - MCP sidecar architecture for developer-system metacognition.

**Key Points**:
- MCP sidecar (not middleware) - Claude *perceives* kgents via `kgents://` resources
- Pre-computed context via background daemons (<50ms latency)
- K-gent Mirror + Coach modes (prevents echo chamber)
- `kgents wake` / `kgents sleep` rituals

**Next**: Kent reviews plan → Phase 1 MCP implementation.

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
