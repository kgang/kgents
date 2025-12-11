# HYDRATE.md - kgents Session Context

**Status**: ~6,683 tests passing | Branch: `main`

## Recent: New Agent Batch Refactoring (Complete)

Comprehensive review and refactoring of seven proposed agents (Q, S, U, V, X, Y, Z) against design principles and bootstrap derivability. **All changes executed.**

### Assessment Summary

| Agent | Status | Verdict | Key Issue |
|-------|--------|---------|-----------|
| **Q-gent** | Clean | KEEP | Cleanly derived (Ground + Contradict) |
| **S-gent** | Clean | KEEP | Cleanly derived (Ground + Compose) |
| **V-gent** | Clean | KEEP | Extends Judge bootstrap with user principles |
| **U-gent** | Heavy | SIMPLIFY | Complex machinery, could be infrastructure |
| **X-gent** | Infrastructure | RECONSIDER | MCP/OpenAPI is protocol, not agent genus |
| **Y-gent** | Overlap | MERGE | Graph composition overlaps C-gent + Fix |
| **Z-gent** | Overlap | MERGE | Context mgmt overlaps Cooled Functor + Lethe |

### Actions Completed

| Action | Status | Output |
|--------|--------|--------|
| KEEP Q-gent | Done | `spec/q-gents/README.md` |
| KEEP S-gent | Done | `spec/s-gents/README.md` |
| KEEP V-gent | Done | `spec/v-gents/README.md` |
| REFACTOR U-gent -> B-gent | Done | `spec/b-gents/distillation.md` |
| DELETE X-gent -> Infrastructure | Done | `docs/infrastructure/mcp-integration.md` |
| MERGE Y-gent -> C-gent | Done | `spec/c-gents/graph-composition.md` |
| DISTRIBUTE Z-gent | Done | `spec/c-gents/context-management.md` |

---

## Previous: Meta-Bootstrap Active

The system now observes itself during development. See `docs/meta-bootstrap-plan.md`.

**Active Feedback Loops**:
| Loop | Signal | Storage |
|------|--------|---------|
| Test Flinch | pytest failures | `.kgents/ghost/test_flinches.jsonl` |
| CI Signals | GitHub Actions | `.kgents/ghost/ci_signals.jsonl` (artifact) |
| HYDRATE Append | Key events | This file (bottom) |
| Git Crystallization | git log/diff | Native git |

**Quick Commands**:
```bash
# Session narrative (last 8 hours)
git log --oneline --since="8 hours ago"

# Churn map (volatility)
git diff --stat HEAD~10

# Prior drift (CLAUDE.md evolution)
git diff HEAD~5 CLAUDE.md

# Recent flinches
cat .kgents/ghost/test_flinches.jsonl | tail -5
```

**DevEx V4 (Deferred to Post-Bootstrap)**:
- `.kgents/ghost/` living filesystem
- Keystroke dynamics, Shadow Diff
- Morning Calibration, Evening Confessional
- See `docs/devex-unified-plan.md`

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

### Semantic Field (135 tests)

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
| **E** | **MUTATION** | **REFINEMENT** |
| **H** | **SYNTHESIS** | **PRIOR** |
| **K** | **PRIOR** | **SYNTHESIS** |
| **R** | **REFINEMENT** | **MUTATION** |
| **D** | **STATE** | **STATE** |
| **T** | **TEST** | **TEST** |
| **W** | **DISPATCH** | **DISPATCH** |

**Phase 1 Complete (MUTATION, SYNTHESIS, PRIOR, REFINEMENT emitters)**
**Phase 2 Complete (Supporting sensors for bidirectional coordination)**
**Phase 3 Complete (D-gent STATE, T-gent TEST, W-gent DISPATCH)**

```python
field = create_semantic_field()
emitter = create_psi_emitter(field)
emitter.emit_metaphor("source", "target", strength=0.85, position=pos)

# Phase 1 emitters
evolution = create_evolution_emitter(field)
evolution.emit_mutation("mut_001", fitness_delta=0.3, generation=5, position=pos)

hegel = create_hegel_emitter(field)
hegel.emit_synthesis("thesis", "antithesis", "synthesis", confidence=0.85, position=pos)

persona = create_persona_emitter(field)
persona.emit_prior_change("risk_tolerance", 0.7, "kent", position=pos)

refinery = create_refinery_emitter(field)
refinery.emit_refinement("target_id", "optimization", improvement_ratio=1.3, position=pos)

# Phase 2 sensors (bidirectional coordination)
evolution_sensor = create_evolution_sensor(field)
refinements = evolution_sensor.sense_refinements(pos)  # E-gent senses R-gent's improvements

refinery_sensor = create_refinery_sensor(field)
mutations = refinery_sensor.sense_mutations(pos)  # R-gent senses E-gent's discoveries

persona_sensor = create_persona_sensor(field)
syntheses = persona_sensor.sense_syntheses(pos)  # K-gent senses H-gent's insights

hegel_sensor = create_hegel_sensor(field)
priors = hegel_sensor.sense_priors(pos)  # H-gent senses K-gent's preferences

# Phase 3 emitters (Infrastructure Agents)
data = create_data_emitter(field)
data.emit_created("entity_001", "users/kent", pos)  # D-gent state change
data.emit_stale("entity_002", "old/key", "2024-01-01", 0.8, pos)  # Stale data

test = create_test_emitter(field)
test.emit_test_result("test_foo", "passed", pos, affected_agents=("d", "m"))
test.emit_coverage_change(0.75, 0.82, pos)  # Coverage improvement

wire = create_wire_emitter(field)
wire.emit_dispatch("msg_001", "source", "target", pos, intercepted_by=("safety",))
wire.emit_blocked("msg_002", "safety", "Policy violation", pos, severity="error")

# Phase 3 sensors
data_sensor = create_data_sensor(field)
changes = data_sensor.sense_state_changes(pos)
deletions = data_sensor.get_deletions(pos)

test_sensor = create_test_sensor(field)
failures = test_sensor.sense_failures(pos)
regressions = test_sensor.get_coverage_regressions(pos)

wire_sensor = create_wire_sensor(field)
blocks = wire_sensor.sense_blocked(pos)
blockers = wire_sensor.get_blockers(pos)
```

### M-gent Cartography (157 tests)

Memory-as-Orientation: HoloMap, Attractors, Desire Lines, Voids, Foveation.

```python
cartographer = create_cartographer(vector_search, trace_store)
holo_map = await cartographer.invoke(context_vector, Resolution.ADAPTIVE)
# -> landmarks, desire_lines, voids, horizon
```

### W-gent Interceptors (125 tests)

Pipeline: Safety(50) -> Metering(100) -> Telemetry(200) -> Persona(300)

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
