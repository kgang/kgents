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

## Phase 2: Supporting Sensors

Add sensors for agents that consume field signals.

### 2.1 E-gent Sensor
- Senses: REFINEMENT (for optimization hints), OPPORTUNITY (for evolution targets)

### 2.2 R-gent Sensor
- Senses: MUTATION (for refinement candidates), MEMORY (for compression targets)

### 2.3 K-gent Sensor
- Senses: NARRATIVE (for persona-appropriate responses), WARNING (for cautious mode)

### 2.4 H-gent Sensor
- Senses: METAPHOR (for dialectical analysis), SYNTHESIS (from other H-gents)

---

## Phase 3: Infrastructure Agents

Field interfaces for core infrastructure agents.

### 3.1 D-gent (Data) - STATE signals

```python
class StatePayload:
    entity_id: str
    state_type: str  # "created", "updated", "deleted", "stale"
    key: str
    old_value_hash: str | None = None
    new_value_hash: str | None = None

class DataFieldEmitter:
    def emit_state_change(self, entity_id, state_type, key, position, ...)
```

### 3.2 T-gent (Testing) - TEST signals

```python
class TestPayload:
    test_id: str
    result: str  # "passed", "failed", "skipped"
    coverage_delta: float
    affected_agents: tuple[str, ...]

class TestFieldEmitter:
    def emit_test_result(self, test_id, result, position, ...)
    def emit_coverage_change(self, old_coverage, new_coverage, position, ...)
```

### 3.3 W-gent (Wire) - DISPATCH signals

```python
class DispatchPayload:
    message_id: str
    source: str
    target: str
    intercepted_by: tuple[str, ...]
    latency_ms: float

class WireFieldEmitter:
    def emit_dispatch(self, message_id, source, target, position, ...)
    def emit_blocked(self, message_id, blocker, reason, position, ...)
```

---

## Phase 4: Catalog Integration

### 4.1 L-gent (Semantic Catalog) - CAPABILITY signals

L-gent is special - it's both the semantic backbone AND needs field integration.

```python
class CapabilityPayload:
    agent_id: str
    capability_name: str
    input_type: str
    output_type: str
    cost_estimate: float

class CatalogFieldEmitter:
    def emit_capability_registered(self, agent_id, capability_name, position, ...)
    def emit_capability_deprecated(self, agent_id, capability_name, position, ...)
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
