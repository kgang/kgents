# Semantic Field Integration Plan

Implementation plan for completing stigmergic field coverage across all kgents agents.

## Current State

The Semantic Field (I-gent) provides decoupled agent coordination via pheromones.
Agents emit signals; others sense them without direct coupling.

### Implemented Emitters/Sensors

| Agent | Emitter | Sensor | Pheromone Types |
|-------|---------|--------|-----------------|
| Psi | PsiFieldEmitter | - | METAPHOR |
| F | ForgeFieldSensor (emits too) | ForgeFieldSensor | INTENT, senses METAPHOR |
| J | SafetyFieldEmitter | - | WARNING |
| B | EconomicFieldEmitter | - | OPPORTUNITY, SCARCITY |
| M | MemoryFieldEmitter | MemoryFieldSensor | MEMORY |
| N | NarrativeFieldEmitter | NarrativeFieldSensor | NARRATIVE |
| O | - | ObserverFieldSensor | All types |

### Missing Coverage

Agents without field interfaces: A, C, D, E, G, H, K, L, P, R, T, W

---

## Phase 1: High-Priority Emitters/Sensors

Add field interfaces for agents that most benefit from stigmergic coordination.

### 1.1 E-gent (Evolution) - MUTATION signals

E-gent performs thermodynamic evolution. Should emit when:
- Mutations discovered (for R-gent refinement)
- Fitness changes detected (for O-gent observation)
- Evolution cycles complete (for M-gent consolidation)

```python
class EvolutionPayload:
    mutation_id: str
    fitness_delta: float  # Change in fitness
    generation: int
    parent_id: str | None = None
    mutation_type: str = "unknown"  # "crossover", "point", "structural"

class EvolutionFieldEmitter:
    def emit_mutation(self, mutation_id, fitness_delta, generation, position, ...)
    def emit_fitness_change(self, entity_id, old_fitness, new_fitness, position, ...)
    def emit_cycle_complete(self, generation, best_fitness, population_size, position, ...)
```

### 1.2 H-gent (Hegel) - SYNTHESIS signals

H-gent performs dialectical operations. Should emit when:
- Thesis/antithesis identified (for Psi-gent metaphor discovery)
- Synthesis achieved (for N-gent narrative)
- Contradictions detected (for J-gent safety)

```python
class SynthesisPayload:
    thesis: str
    antithesis: str
    synthesis: str
    confidence: float
    domain: str = ""

class HegelFieldEmitter:
    def emit_synthesis(self, thesis, antithesis, synthesis, position, ...)
    def emit_contradiction(self, statement_a, statement_b, severity, position, ...)
```

### 1.3 K-gent (Persona) - PRIOR signals

K-gent manages personality/priors. Should emit when:
- Persona changes (for all agents to adapt)
- Prior adjustments made (for B-gent, J-gent)

```python
class PriorPayload:
    prior_type: str  # "risk_tolerance", "time_preference", "creativity"
    value: float
    persona_id: str
    reason: str = ""

class PersonaFieldEmitter:
    def emit_prior_change(self, prior_type, value, persona_id, position, ...)
    def emit_persona_shift(self, old_persona, new_persona, position, ...)
```

### 1.4 R-gent (Refinery) - REFINEMENT signals

R-gent optimizes/compresses. Should emit when:
- Refinement opportunities found (for E-gent)
- Compression achieved (for M-gent)

```python
class RefinementPayload:
    target_id: str
    improvement_type: str  # "compression", "optimization", "simplification"
    improvement_ratio: float
    before_metrics: dict
    after_metrics: dict

class RefineryFieldEmitter:
    def emit_refinement(self, target_id, improvement_type, ratio, position, ...)
    def emit_opportunity(self, target_id, potential_improvement, position, ...)
```

---

## Phase 2: Supporting Sensors ✅ COMPLETE

Add sensors for agents to consume the Phase 1 signals.

| Agent  | Sensor               | Responds To                                        |
|--------|----------------------|----------------------------------------------------|
| E-gent | EvolutionFieldSensor | REFINEMENT (R-gent improvements inform evolution)  |
| R-gent | RefineryFieldSensor  | MUTATION (E-gent discoveries trigger optimization) |
| K-gent | PersonaFieldSensor   | SYNTHESIS (H-gent insights update priors)          |
| H-gent | HegelFieldSensor     | PRIOR (K-gent preferences guide dialectic)         |

### 2.1 E-gent EvolutionFieldSensor ✅
- Senses: REFINEMENT signals
- Methods: `sense_refinements()`, `sense_opportunities()`, `sense_by_target()`, `get_best_refinement()`

### 2.2 R-gent RefineryFieldSensor ✅
- Senses: MUTATION signals
- Methods: `sense_mutations()`, `sense_fitness_changes()`, `sense_cycle_completions()`, `get_strongest_mutation()`

### 2.3 K-gent PersonaFieldSensor ✅
- Senses: SYNTHESIS signals
- Methods: `sense_syntheses()`, `sense_contradictions()`, `sense_by_domain()`, `get_strongest_synthesis()`

### 2.4 H-gent HegelFieldSensor ✅
- Senses: PRIOR signals
- Methods: `sense_priors()`, `sense_persona_shifts()`, `sense_by_prior_type()`, `get_prior_value()`

---

## Phase 3: Infrastructure Agents ✅ COMPLETE

Field interfaces for core infrastructure agents.

### 3.1 D-gent (Data) - STATE signals ✅

```python
class StatePayload:
    entity_id: str
    state_type: str  # "created", "updated", "deleted", "stale"
    key: str
    old_value_hash: str | None = None
    new_value_hash: str | None = None
    store_id: str = ""

class StalePayload:
    entity_id: str
    key: str
    last_accessed: str  # ISO timestamp
    staleness_score: float
    recommended_action: str = ""

class DataFieldEmitter:
    def emit_state_change(self, entity_id, state_type, key, position, ...)
    def emit_created(self, entity_id, key, position, ...)
    def emit_updated(self, entity_id, key, position, ...)
    def emit_deleted(self, entity_id, key, position, ...)
    def emit_stale(self, entity_id, key, last_accessed, staleness_score, position, ...)

class DataFieldSensor:
    def sense_state_changes(self, position, ...) -> list[StatePayload]
    def sense_by_state_type(self, state_type, position, ...) -> list[StatePayload]
    def sense_by_entity(self, entity_id, position, ...) -> list[StatePayload]
    def sense_stale(self, position, min_staleness=0.0, ...) -> list[StalePayload]
    def get_deletions(self, position, ...) -> list[StatePayload]
```

### 3.2 T-gent (Testing) - TEST signals ✅

```python
class TestResultPayload:
    test_id: str
    result: str  # "passed", "failed", "skipped", "error"
    duration_ms: float = 0.0
    affected_agents: tuple[str, ...] = ()
    error_message: str = ""
    test_file: str = ""

class CoverageChangePayload:
    old_coverage: float
    new_coverage: float
    delta: float
    affected_files: tuple[str, ...] = ()

class TestFieldEmitter:
    def emit_test_result(self, test_id, result, position, ...)
    def emit_coverage_change(self, old_coverage, new_coverage, position, ...)
    def emit_test_suite_complete(self, suite_id, passed, failed, skipped, duration, position, ...)

class TestFieldSensor:
    def sense_test_results(self, position, ...) -> list[TestResultPayload]
    def sense_failures(self, position, ...) -> list[TestResultPayload]
    def sense_by_affected_agent(self, agent_id, position, ...) -> list[TestResultPayload]
    def sense_coverage_changes(self, position, ...) -> list[CoverageChangePayload]
    def get_coverage_regressions(self, position, ...) -> list[CoverageChangePayload]
    def has_failures(self, position, ...) -> bool
```

### 3.3 W-gent (Wire) - DISPATCH signals ✅

```python
class DispatchPayload:
    message_id: str
    source: str
    target: str
    intercepted_by: tuple[str, ...] = ()
    latency_ms: float = 0.0
    message_type: str = ""

class BlockedPayload:
    message_id: str
    blocker: str
    reason: str
    source: str = ""
    target: str = ""
    severity: str = "warning"

class WireFieldEmitter:
    def emit_dispatch(self, message_id, source, target, position, ...)
    def emit_blocked(self, message_id, blocker, reason, position, ...)
    def emit_routing_latency(self, route_id, source, target, latency_ms, position, ...)

class WireFieldSensor:
    def sense_dispatches(self, position, ...) -> list[DispatchPayload]
    def sense_blocked(self, position, ...) -> list[BlockedPayload]
    def sense_by_source(self, source, position, ...) -> list[DispatchPayload]
    def sense_by_target(self, target, position, ...) -> list[DispatchPayload]
    def sense_intercepted(self, position, ...) -> list[DispatchPayload]
    def get_blockers(self, position, ...) -> set[str]
    def has_blocks(self, position, ...) -> bool
```

---

## Phase 4: Catalog Integration ✅ COMPLETE

### 4.1 L-gent (Semantic Catalog) - CAPABILITY signals ✅

L-gent is special - it's both the semantic backbone AND needs field integration.

```python
class CapabilityPayload:
    agent_id: str
    capability_name: str
    input_type: str
    output_type: str
    cost_estimate: float = 0.0
    tags: tuple[str, ...] = ()
    description: str = ""
    version: str = "1.0"

class CapabilityDeprecationPayload:
    agent_id: str
    capability_name: str
    reason: str
    replacement: str | None = None
    deprecation_date: str = ""

class CapabilityRequestPayload:
    requester_id: str
    capability_pattern: str
    urgency: float = 0.5
    input_type: str | None = None
    output_type: str | None = None
    tags: tuple[str, ...] = ()

class CatalogFieldEmitter:
    def emit_capability_registered(self, agent_id, capability_name, input_type, output_type, position, ...)
    def emit_capability_deprecated(self, agent_id, capability_name, reason, position, ...)
    def emit_capability_updated(self, agent_id, capability_name, changes, position, ...)
    def emit_capability_request(self, requester_id, capability_pattern, urgency, position, ...)

class CatalogFieldSensor:
    def sense_capabilities(self, position, ...) -> list[CapabilityPayload]
    def sense_by_tags(self, position, tags, ...) -> list[CapabilityPayload]
    def sense_deprecations(self, position, ...) -> list[CapabilityDeprecationPayload]
    def sense_capability_requests(self, position, ...) -> list[CapabilityRequestPayload]
    def find_capability(self, capability_name, position, ...) -> CapabilityPayload | None
    def get_agent_capabilities(self, agent_id, position, ...) -> list[CapabilityPayload]
    def has_capability(self, capability_name, position, ...) -> bool
    def get_capability_count(self) -> int
```

---

## Implementation Notes

### New Pheromone Types Required

Add to `SemanticPheromoneKind`:
- MUTATION (E-gent)
- SYNTHESIS (H-gent)
- PRIOR (K-gent)
- REFINEMENT (R-gent)
- STATE (D-gent)
- TEST (T-gent)
- DISPATCH (W-gent)
- CAPABILITY (L-gent)

### Decay Rates by Category

| Category | Decay Rate | Rationale |
|----------|------------|-----------|
| WARNING | 0.3 | Urgent, short-lived |
| MUTATION | 0.2 | Medium persistence |
| SYNTHESIS | 0.1 | Slow decay - insights persist |
| PRIOR | 0.05 | Very slow - persona is stable |
| STATE | 0.15 | Medium - state changes matter |
| TEST | 0.25 | Fast - test results are ephemeral |
| DISPATCH | 0.4 | Very fast - operational signals |
| CAPABILITY | 0.02 | Very slow - capabilities are stable |

### Testing Strategy

Each phase adds ~25-35 tests per emitter/sensor pair:
- Emission tests (payload validation, intensity, position)
- Sensing tests (radius, filtering, sorting)
- Decay tests (time-based, threshold)
- Integration tests (emitter→sensor roundtrip)

---

## Success Criteria

- [ ] All 26 agents have field interfaces (emitter, sensor, or both)
- [ ] No agent imports another agent (field-only coordination)
- [ ] Test coverage >90% for semantic_field.py
- [ ] Integration tests verify cross-agent coordination via field
