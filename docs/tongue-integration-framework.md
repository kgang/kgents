# .tongue Integration Framework: A Research and Implementation Plan

*Declarative agent coordination through semantic field dynamics*

## Executive Summary

The `.tongue` DSL enables agent integration without code—agents coordinate through field dynamics, not function calls. This document proposes a comprehensive framework for three integration families:

1. **K-gent Priors**: Personality as structural bias (K→B, K→J, K→N)
2. **Memory Consolidation**: Sleep-like optimization (M×E×R)
3. **Test Archaeology**: Memory-aware testing (T×M)

Plus novel extensions:
4. **Narrative Crystallization**: Story-based memory compression (N×M×Psi)
5. **Economic Weather**: Market dynamics for resource allocation (B×I×O)
6. **Dialectic Gardening**: Contradiction cultivation for insight (H×Psi×F)

---

## Part I: Architecture Overview

### The Tongue Compilation Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   .tongue   │────▶│   Parser    │────▶│  Validator  │────▶│  Compiler   │
│    file     │     │ (syntax)    │     │ (semantics) │     │ (codegen)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                    ┌──────────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │                        OUTPUT ARTIFACTS                            │
    ├───────────────────┬───────────────────┬───────────────────────────┤
    │  W-gent           │  I-gent           │  C-gent                   │
    │  Interceptor      │  Field            │  Type                     │
    │  Registrations    │  Schemas          │  Contracts                │
    └───────────────────┴───────────────────┴───────────────────────────┘
```

### Integration Types

| Type | Mechanism | Example |
|------|-----------|---------|
| `PriorInjection` | W-gent interceptor modifies message context | K→B (personality biases economics) |
| `Stigmergic` | Agent emits pheromone; others sense it | Psi→Field→F (metaphor discovery) |
| `Temporal` | Triggered by time/idle conditions | M×E×R (sleep consolidation) |
| `Reactive` | Triggered by field state changes | T×M (test on memory change) |
| `Dialectic` | Thesis/antithesis synthesis | H×Psi (contradiction resolution) |

---

## Part II: K-gent Prior Integrations

### Philosophy: Personality as Bayesian Prior

K-gent's insight: Personality isn't cosmetic voice—it's *structural bias* in decision-making.

A "risk-averse" persona doesn't just *talk* carefully—it *decides* carefully. This manifests as:
- Lower discount rate in B-gent utility calculations
- Higher reality threshold in J-gent safety checks
- Conservative narrative framing in N-gent storytelling

### K→B: Economic Personality

```tongue
# integrations/k_economic_priors.tongue
version: "1.0"

integration k_economic_priors {
    emitter: k
    receiver: b
    pheromone: OPPORTUNITY

    context {
        domain: "economics"
        tags: ["decision-making", "utility", "risk"]
    }

    trigger {
        type: event
        on: "persona_query"
        condition: "aspect == 'economic'"
    }

    # The actual prior mapping
    priors {
        # Risk tolerance spectrum
        risk_mapping {
            "Conservative" {
                discount_rate: 0.95    # Very patient
                loss_aversion: 2.5     # Strongly loss-averse
                risk_tolerance: 0.2    # Low variance acceptance
            }
            "Balanced" {
                discount_rate: 0.90
                loss_aversion: 2.0
                risk_tolerance: 0.5
            }
            "Aggressive" {
                discount_rate: 0.80    # Impatient
                loss_aversion: 1.0     # Loss-neutral
                risk_tolerance: 0.8    # High variance OK
            }
        }

        # Time preference spectrum
        time_mapping {
            "Patient" {
                horizon_ticks: 1000
                future_weight: 0.95
            }
            "Impatient" {
                horizon_ticks: 10
                future_weight: 0.50
            }
        }
    }

    mechanism: interceptor
    interceptor_order: 300  # After safety (0-99), metering (100-199), telemetry (200-299)

    decay: 0.05   # Personality is persistent
    radius: 1.0   # Affects all economic decisions
    intensity: 1.0

    description: "Personality modifies economic utility functions"
}
```

### K→J: Safety Personality

```tongue
# integrations/k_safety_priors.tongue
version: "1.0"

integration k_safety_priors {
    emitter: k
    receiver: j
    pheromone: WARNING

    context {
        domain: "safety"
        tags: ["entropy", "reality", "creativity"]
    }

    trigger {
        type: event
        on: "persona_query"
        condition: "aspect == 'safety'"
    }

    priors {
        creativity_mapping {
            "Conservative" {
                max_entropy: 0.3       # Low randomness allowed
                reality_threshold: 0.9 # High grounding required
                max_recursion: 5       # Shallow exploration
            }
            "Exploratory" {
                max_entropy: 0.8       # High creativity allowed
                reality_threshold: 0.5 # Lower grounding OK
                max_recursion: 15      # Deep exploration OK
            }
            "Balanced" {
                max_entropy: 0.5
                reality_threshold: 0.7
                max_recursion: 10
            }
        }

        # Hallucination tolerance
        hallucination_policy {
            "Strict" {
                citation_required: true
                uncertainty_flagging: "always"
                speculation_allowed: false
            }
            "Permissive" {
                citation_required: false
                uncertainty_flagging: "high_confidence_only"
                speculation_allowed: true
            }
        }
    }

    mechanism: interceptor
    interceptor_order: 50  # Early in safety checks

    decay: 0.05
    radius: 1.0
    intensity: 1.0

    description: "Personality modifies safety thresholds"
}
```

### K→N: Narrative Personality

```tongue
# integrations/k_narrative_priors.tongue
version: "1.0"

integration k_narrative_priors {
    emitter: k
    receiver: n
    pheromone: NARRATIVE

    context {
        domain: "communication"
        tags: ["style", "genre", "voice"]
    }

    trigger {
        type: event
        on: "narrative_generation"
    }

    priors {
        style_mapping {
            "Academic" {
                formality: 0.9
                hedging: "frequent"
                citation_style: "inline"
                genre_preference: "expository"
            }
            "Casual" {
                formality: 0.3
                hedging: "minimal"
                citation_style: "none"
                genre_preference: "conversational"
            }
            "Technical" {
                formality: 0.7
                hedging: "precise"
                citation_style: "footnote"
                genre_preference: "documentation"
            }
        }

        # Analogy preferences (from Kent's persona seed)
        analogy_frequency {
            "High": { analogies_per_explanation: 2 }
            "Low": { analogies_per_explanation: 0 }
        }

        # Prose length preferences
        length_mapping {
            "Concise" {
                max_sentences_per_point: 2
                elaboration_depth: 1
            }
            "Detailed" {
                max_sentences_per_point: 5
                elaboration_depth: 3
            }
        }
    }

    mechanism: stigmergic  # N-gent senses from field, not intercepted

    decay: 0.1
    radius: 0.5
    intensity: 0.8

    description: "Personality shapes narrative voice and style"
}
```

### Novel Extension: K→Psi (Metaphor Personality)

```tongue
# integrations/k_metaphor_priors.tongue
version: "1.0"

integration k_metaphor_priors {
    emitter: k
    receiver: psi
    pheromone: METAPHOR

    context {
        domain: "cognition"
        tags: ["analogy", "creativity", "problem-solving"]
    }

    trigger {
        type: event
        on: "problem_submitted"
    }

    priors {
        # Preferred source domains for metaphors
        domain_preferences {
            "Kent" {
                preferred_sources: ["architecture", "gardening", "music", "mathematics"]
                avoided_sources: ["warfare", "sports_competition"]
                abstraction_level: "high"  # Prefers structural over surface similarity
            }
        }

        # Metaphor confidence thresholds
        confidence_mapping {
            "Conservative": { min_confidence: 0.8 }
            "Exploratory": { min_confidence: 0.5 }
        }
    }

    mechanism: stigmergic

    decay: 0.1
    radius: 0.5
    intensity: 0.7

    description: "Personality influences metaphor selection"
}
```

---

## Part III: Memory Consolidation (M×E×R)

### Philosophy: Computational Dreaming

The Hypnagogic Refinery implements "dreaming" for code systems:
- **M-gent** identifies cold memories (temperature < 0.2)
- **E-gent** retrieves actual artifacts
- **R-gent** compresses/optimizes with semantic preservation

This is inspired by biological memory consolidation during sleep.

### Core M×E×R Integration

```tongue
# integrations/m_consolidation.tongue
version: "1.0"

integration memory_consolidation {
    emitter: m
    receiver: e
    pheromone: MEMORY

    context {
        domain: "memory"
        tags: ["consolidation", "compression", "optimization"]
    }

    trigger {
        type: schedule
        interval: 1000  # Every 1000 ticks during idle
        condition: "system_load < 0.3"  # Only when system is quiet
    }

    # Temperature-based selection
    selection {
        temperature_threshold: 0.2  # Cold memories only
        min_age_days: 7             # At least a week old
        min_size_bytes: 1000        # Worth optimizing
        exclude_kinds: ["config"]   # Don't touch configuration
    }

    # Pipeline specification
    pipeline {
        stage_1 {
            agent: e
            action: retrieve
            input: "m.cold_memories"
            output: "retrieved_artifacts"
        }

        stage_2 {
            agent: r
            action: compress
            input: "retrieved_artifacts"
            objective: "size_reduction"
            constraints: ["preserve_semantics", "maintain_tests"]
            min_improvement: 0.1  # 10% minimum
            output: "optimized_artifacts"
        }

        stage_3 {
            agent: m
            action: store
            input: "optimized_artifacts"
            tier: "WARM"  # Promote to warmer tier after optimization
        }
    }

    # Economic constraints
    budget {
        source: "b.maintenance_reserve"
        max_tokens_per_cycle: 5000
        priority: "low"  # Yield to user requests
    }

    # Safety constraints
    safety {
        rollback_enabled: true
        test_before_apply: true
        max_changes_per_cycle: 10
    }

    decay: 0.08  # Memory pheromones persist
    radius: 0.3
    intensity: 0.5

    description: "Automatic memory optimization during system idle"
}
```

### Novel Extension: Tiered Consolidation

Different memory types need different consolidation strategies:

```tongue
# integrations/m_tiered_consolidation.tongue
version: "1.0"

# Tier 1: Code compression
integration code_consolidation {
    emitter: m
    receiver: r
    pheromone: MEMORY

    context {
        domain: "code"
        tags: ["compression", "refactoring"]
    }

    trigger {
        type: threshold
        metric: "memory_pressure"
        threshold: 0.7
    }

    selection {
        kind: "code"
        temperature_threshold: 0.15
    }

    optimization {
        strategies: ["remove_dead_code", "inline_constants", "simplify_logic"]
        preserve: ["public_api", "test_coverage"]
    }

    decay: 0.05
    description: "Compress cold code paths"
}

# Tier 2: Cache eviction
integration cache_consolidation {
    emitter: m
    receiver: e
    pheromone: MEMORY

    context {
        domain: "cache"
        tags: ["eviction", "regeneration"]
    }

    trigger {
        type: threshold
        metric: "cache_size"
        threshold: 0.9  # 90% full
    }

    selection {
        kind: "cache"
        temperature_threshold: 0.1
    }

    optimization {
        strategy: "evict"  # Remove entirely
        regeneration_on_demand: true
    }

    decay: 0.25  # Fast decay for cache signals
    description: "Evict cold cache entries"
}

# Tier 3: Trace archival
integration trace_consolidation {
    emitter: m
    receiver: n
    pheromone: MEMORY

    context {
        domain: "narrative"
        tags: ["archival", "crystallization"]
    }

    trigger {
        type: schedule
        interval: 10000  # Less frequent
    }

    selection {
        kind: "trace"
        age_threshold_days: 30
    }

    optimization {
        strategy: "crystallize"  # Compress to SemanticTrace
        preserve: ["determinism", "gas_consumed", "agent_genus"]
        discard: ["raw_inputs", "raw_outputs"]  # Keep only hashes
    }

    decay: 0.08
    description: "Archive old traces as crystals"
}
```

### Novel Extension: Dream Narratives (N×M×Psi)

Inspired by how dreams consolidate memories through narrative:

```tongue
# integrations/dream_narrative.tongue
version: "1.0"

integration dream_narrative {
    emitter: n
    receiver: psi
    pheromone: NARRATIVE

    context {
        domain: "consolidation"
        tags: ["dream", "story", "integration"]
    }

    trigger {
        type: schedule
        interval: 5000
        condition: "system_load < 0.2 AND time_of_day == 'night'"
    }

    # The dream process
    process {
        # 1. N-gent retrieves disconnected memory fragments
        gather {
            agent: n
            action: query_fragments
            criteria: {
                connection_score: "< 0.3"  # Poorly connected
                importance_score: "> 0.5"  # But important
            }
        }

        # 2. Psi-gent finds metaphorical connections
        connect {
            agent: psi
            action: find_bridges
            input: "fragments"
            min_confidence: 0.6
        }

        # 3. N-gent weaves into coherent narrative
        weave {
            agent: n
            action: crystallize_story
            input: "fragments + bridges"
            output: "dream_crystal"
        }

        # 4. M-gent stores new connections
        consolidate {
            agent: m
            action: strengthen_edges
            input: "dream_crystal.edges"
        }
    }

    # Dreams can be weird
    safety {
        reality_threshold: 0.3  # Lower than waking
        allow_novel_connections: true
    }

    decay: 0.15
    radius: 0.8
    intensity: 0.6

    description: "Story-based memory consolidation (dreaming)"
}
```

---

## Part IV: Test Archaeology (T×M)

### Philosophy: Tests as Memory Probes

Test archaeology treats the test suite as a *probe into memory*:
- Which code paths are exercised?
- Which memories are validated?
- Where are the gaps?

T-gent's categorical testing primitives become archaeological tools.

### Core T×M Integration

```tongue
# integrations/t_archaeology.tongue
version: "1.0"

integration test_archaeology {
    emitter: t
    receiver: m
    pheromone: MEMORY

    context {
        domain: "testing"
        tags: ["coverage", "archaeology", "memory-mapping"]
    }

    trigger {
        type: reactive
        on: "memory_change"
        condition: "change.kind == 'code' AND change.size > 100"
    }

    # Mapping tests to memories
    mapping {
        # For each test, track which memories it exercises
        test_memory_map {
            granularity: "function"  # Track at function level
            include_transitive: true  # Follow call chains
        }

        # For each memory, track which tests validate it
        memory_test_map {
            coverage_threshold: 0.8  # Flag under-tested memories
            staleness_threshold_days: 30  # Flag tests not run recently
        }
    }

    # Archaeological analysis
    analysis {
        # Find "dead" code (memories with no test coverage)
        find_dead_zones {
            output_pheromone: WARNING
            severity: "info"
        }

        # Find "fossil" tests (tests for removed code)
        find_fossils {
            output_pheromone: WARNING
            severity: "warning"
        }

        # Find "drift" (tests passing but code changed significantly)
        find_drift {
            embedding_distance_threshold: 0.5
            output_pheromone: WARNING
            severity: "warning"
        }
    }

    decay: 0.1
    radius: 0.4
    intensity: 0.7

    description: "Map tests to memories, find gaps"
}
```

### Novel Extension: Differential Archaeology

Using T-gent's OracleAgent for archaeological comparison:

```tongue
# integrations/t_differential_archaeology.tongue
version: "1.0"

integration differential_archaeology {
    emitter: t
    receiver: m
    pheromone: MEMORY

    context {
        domain: "testing"
        tags: ["differential", "oracle", "comparison"]
    }

    trigger {
        type: event
        on: "refactoring_complete"
    }

    # Use OracleAgent to compare before/after
    oracle {
        agents: ["original_implementation", "refactored_implementation"]

        comparison {
            input_source: "historical_inputs"  # From M-gent traces
            agreement_threshold: 0.95

            on_disagreement {
                emit_pheromone: WARNING
                severity: "error"
                action: "rollback_suggested"
            }
        }
    }

    # Track disagreement patterns
    analysis {
        cluster_disagreements: true
        find_edge_cases: true
        suggest_new_tests: true
    }

    decay: 0.2
    radius: 0.3
    intensity: 0.9

    description: "Compare implementations via historical inputs"
}
```

### Novel Extension: Law Archaeology

Using T-gent's LawValidator to verify categorical laws over time:

```tongue
# integrations/t_law_archaeology.tongue
version: "1.0"

integration law_archaeology {
    emitter: t
    receiver: c
    pheromone: WARNING

    context {
        domain: "category-theory"
        tags: ["laws", "verification", "drift"]
    }

    trigger {
        type: schedule
        interval: 500
    }

    # Verify categorical laws
    laws {
        associativity {
            # (h ∘ g) ∘ f == h ∘ (g ∘ f)
            sample_size: 100
            tolerance: 0.001
        }

        identity {
            # f ∘ id == f == id ∘ f
            sample_size: 100
        }

        functor {
            # F(g ∘ f) == F(g) ∘ F(f)
            # F(id) == id
            sample_size: 50
        }

        monad {
            # Left identity: return a >>= f == f a
            # Right identity: m >>= return == m
            # Associativity: (m >>= f) >>= g == m >>= (λx. f x >>= g)
            sample_size: 30
        }
    }

    # Track law violations over time
    archaeology {
        record_violations: true
        correlate_with_changes: true

        on_new_violation {
            emit_pheromone: WARNING
            severity: "error"
            bisect_to_find_cause: true
        }
    }

    decay: 0.05
    radius: 1.0
    intensity: 1.0

    description: "Verify categorical laws hold over time"
}
```

---

## Part V: Novel Integration Families

### Economic Weather (B×I×O)

Treating economic signals as a weather system:

```tongue
# integrations/economic_weather.tongue
version: "1.0"

integration economic_weather {
    emitter: b
    receiver: "*"  # Broadcast
    pheromone: OPPORTUNITY

    context {
        domain: "economics"
        tags: ["weather", "forecast", "allocation"]
    }

    trigger {
        type: schedule
        interval: 100
    }

    # Weather patterns
    weather {
        # Compute system-wide economic state
        compute_pressure {
            source: "b.treasury"
            factors: ["token_velocity", "deficit_ratio", "scarcity_events"]
        }

        # Forecast future state
        forecast {
            horizon_ticks: 50
            model: "exponential_smoothing"
            confidence_interval: 0.9
        }

        # Emit weather report
        report {
            pressure: "high | low | normal"
            trend: "rising | falling | stable"
            advisory: "spend | save | neutral"
        }
    }

    # O-gent observes the weather
    observation {
        agent: o
        metrics: ["pressure", "trend", "advisory"]
        emit_telemetry: true
    }

    # I-gent field visualization
    field_effect {
        high_pressure: { opportunity_decay: 0.5 }   # Opportunities fade fast
        low_pressure: { opportunity_decay: 0.05 }   # Opportunities persist
    }

    decay: 0.3
    radius: 1.0
    intensity: 0.8

    description: "Economic conditions as weather patterns"
}
```

### Dialectic Gardening (H×Psi×F)

Cultivating contradictions for insight:

```tongue
# integrations/dialectic_gardening.tongue
version: "1.0"

integration dialectic_gardening {
    emitter: h
    receiver: psi
    pheromone: METAPHOR

    context {
        domain: "dialectic"
        tags: ["contradiction", "synthesis", "cultivation"]
    }

    trigger {
        type: event
        on: "tension_detected"
        condition: "tension.severity > 0.5"
    }

    # Gardening metaphor
    cultivation {
        # Plant: H-gent detects contradictions
        plant {
            agent: h
            action: surface_tensions
            min_severity: 0.5
            output: "seeds"  # Contradiction seeds
        }

        # Water: Psi-gent finds metaphorical bridges
        water {
            agent: psi
            action: find_functor
            input: "seeds"
            domain_hints: ["gardening", "ecology", "growth"]
            output: "bridges"
        }

        # Harvest: F-gent forges synthesis artifact
        harvest {
            agent: f
            action: forge
            input: "seeds + bridges"
            wait_for_ripeness: true  # Don't force premature synthesis
            output: "fruit"
        }
    }

    # Some contradictions should be held, not resolved
    patience {
        hold_tension_threshold: 0.8
        max_cultivation_time_ticks: 1000

        on_timeout {
            action: "crystallize_as_productive_tension"
            emit_pheromone: NARRATIVE
        }
    }

    decay: 0.1
    radius: 0.6
    intensity: 0.7

    description: "Cultivate contradictions into insights"
}
```

### Attention Gradient (L×I×O)

Semantic attention as field dynamics:

```tongue
# integrations/attention_gradient.tongue
version: "1.0"

integration attention_gradient {
    emitter: l
    receiver: i
    pheromone: INTENT

    context {
        domain: "attention"
        tags: ["focus", "salience", "gradient"]
    }

    trigger {
        type: presence
        kind: INTENT
        threshold: 0.1
    }

    # Attention as a field gradient
    gradient {
        # L-gent computes salience from embeddings
        compute_salience {
            agent: l
            method: "cosine_similarity_to_focus"
            focus_source: "current_context"
        }

        # I-gent updates field with attention weights
        update_field {
            agent: i
            action: "apply_gradient"
            gradient_type: "gaussian"
            sigma: 0.3
        }

        # O-gent observes attention patterns
        observe {
            agent: o
            metrics: ["attention_entropy", "focus_stability", "drift_rate"]
        }
    }

    # Attention decay (forgetting)
    decay_dynamics {
        base_rate: 0.2
        salience_modifier: true  # High salience = slow decay
        recency_modifier: true   # Recent = slow decay
    }

    decay: 0.2
    radius: 0.5
    intensity: 0.8

    description: "Semantic attention as field gradient"
}
```

---

## Part VI: Implementation Roadmap

### Phase 1: Core K-gent Priors (2-3 days)

1. **K→B Economic Priors**
   - Implement risk_tolerance → discount_rate mapping
   - Wire PersonaInterceptor to modify BusMessage context
   - Tests: 20-30

2. **K→J Safety Priors**
   - Implement creativity → entropy_threshold mapping
   - Wire to SafetyInterceptor
   - Tests: 15-20

3. **K→N Narrative Priors**
   - Implement style → formality/hedging mapping
   - Stigmergic (N senses from field)
   - Tests: 15-20

### Phase 2: Memory Consolidation (2-3 days)

1. **Core M×E×R Pipeline**
   - Temperature-based selection
   - Retrieve → Compress → Store pipeline
   - Budget constraints from B-gent
   - Tests: 25-30

2. **Tiered Consolidation**
   - Code compression tier
   - Cache eviction tier
   - Trace archival tier
   - Tests: 20-25

### Phase 3: Test Archaeology (2-3 days)

1. **T×M Mapping**
   - Test → Memory mapping
   - Memory → Test mapping
   - Coverage gap detection
   - Tests: 20-25

2. **Archaeological Analysis**
   - Dead zone detection
   - Fossil test detection
   - Drift detection
   - Tests: 15-20

### Phase 4: Novel Extensions (3-4 days)

1. **Dream Narratives (N×M×Psi)**
   - Fragment gathering
   - Metaphorical bridge finding
   - Story crystallization
   - Tests: 25-30

2. **Economic Weather (B×I×O)**
   - Pressure computation
   - Forecast model
   - Field effect application
   - Tests: 20-25

3. **Dialectic Gardening (H×Psi×F)**
   - Contradiction cultivation
   - Patience/hold mechanisms
   - Synthesis harvesting
   - Tests: 20-25

### Phase 5: Compiler Enhancement (2-3 days)

1. **Extended Tongue Syntax**
   - `priors {}` block for prior mappings
   - `pipeline {}` block for multi-stage processes
   - `oracle {}` block for differential testing
   - `cultivation {}` block for dialectic processes

2. **Validation Extensions**
   - Prior type checking
   - Pipeline stage validation
   - Budget constraint validation

3. **Code Generation**
   - Generate interceptor registrations
   - Generate field schemas
   - Generate type contracts

---

## Part VII: Open Questions

### Semantic Questions

1. **How do priors compose?** When K→B and K→J both apply, do they interact?
2. **What's the dream/wake boundary?** When does consolidation end and active processing begin?
3. **How do tests "remember"?** What trace do tests leave in M-gent?

### Technical Questions

1. **Pheromone conflicts**: When multiple agents emit contradictory signals, who wins?
2. **Pipeline atomicity**: If stage 2 fails, how do we rollback stage 1?
3. **Budget coordination**: How do scheduled integrations share the maintenance reserve?

### Philosophical Questions

1. **Is dreaming necessary?** Could consolidation happen continuously?
2. **Should tests have memory?** Or should they be stateless probes?
3. **What is "productive tension"?** When should contradictions be held vs. resolved?

---

## Appendix A: Type Reference

### Pheromone Kinds

| Kind | Decay | Radius | Primary Emitter | Primary Consumer |
|------|-------|--------|-----------------|------------------|
| METAPHOR | 0.1 | 0.5 | Psi | F, R, E |
| INTENT | 0.2 | 0.3 | F | G, P |
| ARTIFACT | 0.05 | 0.4 | F | M, L |
| WARNING | 0.3 | 1.0 | J | All |
| OPPORTUNITY | 0.15 | 0.6 | B | E, R |
| SCARCITY | 0.25 | 0.8 | B | All |
| MEMORY | 0.08 | 0.3 | M | E, R, T |
| NARRATIVE | 0.12 | 0.4 | N | K, M |

### Prior Mappings

| Source | Target | Mapping |
|--------|--------|---------|
| K.risk_tolerance | B.discount_rate | Low→0.95, High→0.80 |
| K.risk_tolerance | B.loss_aversion | Low→2.5, High→1.0 |
| K.creativity | J.max_entropy | Conservative→0.3, Exploratory→0.8 |
| K.creativity | J.reality_threshold | Conservative→0.9, Exploratory→0.5 |
| K.style | N.formality | Academic→0.9, Casual→0.3 |

### Interceptor Order

| Range | Agent | Purpose |
|-------|-------|---------|
| 0-99 | J-gent | Safety (security first) |
| 100-199 | B-gent | Economics (metering) |
| 200-299 | O-gent | Telemetry (observability) |
| 300-399 | K-gent | Persona (prior injection) |
| 400+ | Custom | User-defined |

---

## Appendix B: Example .tongue Files

### Minimal Integration

```tongue
integration minimal_example {
    emitter: a
    receiver: b
    pheromone: INTENT
}
```

### Full-Featured Integration

```tongue
version: "1.0"

integration full_example {
    emitter: psi
    receiver: f
    pheromone: METAPHOR

    context {
        domain: "software"
        tags: ["problem-solving", "creative", "analogical"]
        embedding_dim: 128
    }

    trigger {
        type: event
        on: "problem_submitted"
        condition: "confidence > 0.7"
    }

    priors {
        source_preference {
            "preferred": ["architecture", "gardening"]
            "avoided": ["warfare"]
        }
    }

    pipeline {
        stage_1 {
            agent: psi
            action: find_functor
            output: "functor"
        }
        stage_2 {
            agent: f
            action: apply_functor
            input: "functor"
        }
    }

    budget {
        source: "b.exploration_reserve"
        max_tokens: 1000
    }

    safety {
        max_entropy: 0.7
        rollback_enabled: true
    }

    decay: 0.1
    radius: 0.5
    intensity: 1.0

    description: "Psi-gent metaphor discovery for F-gent forging"
}
```

---

*This framework is a living document. Novel ideas welcome.*
