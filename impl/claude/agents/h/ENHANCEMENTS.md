# H-gents Enhancements

This document describes the new functionality added to H-gents to match the specification.

## Overview

All enhancements maintain **full backward compatibility**. Existing code continues to work unchanged.

## New Exports

### Hegel

```python
from agents.h import (
    BackgroundDialectic,      # NEW: Background monitoring
    background_dialectic,     # NEW: Factory function
)
```

### Jung

```python
from agents.h import (
    # NEW: Archetype support
    Archetype,                # Enum of 6 Jungian archetypes
    ArchetypeManifest,        # How archetype manifests in system

    # NEW: Collective shadow
    CollectiveShadowAgent,    # System-level shadow analysis
    CollectiveShadow,         # Result dataclass
    CollectiveShadowInput,    # Input dataclass
    collective_shadow,        # Factory function
)
```

### Lacan

```python
from agents.h import (
    LacanError,              # NOW EXPORTED: Error as Real intrusion
    LacanResult,             # NOW EXPORTED: Union type
)
```

### Composition (NEW MODULE)

```python
from agents.h import (
    # Pipeline agents
    HegelLacanPipeline,      # Hegel → Lacan
    LacanJungPipeline,       # Lacan → Jung
    JungHegelPipeline,       # Jung → Hegel
    FullIntrospection,       # Complete pipeline

    # Input/Output types
    IntrospectionInput,
    IntrospectionOutput,

    # Factory functions
    hegel_to_lacan,
    lacan_to_jung,
    jung_to_hegel,
    full_introspection,
)
```

## Usage Examples

### 1. Archetype Detection

```python
from agents.h import jung, JungInput, Archetype

# Create agent
j = jung()

# Analyze system
result = await j.invoke(JungInput(
    system_self_image="A knowledgeable, helpful guide",
    declared_capabilities=["answer questions", "provide wisdom"],
    behavioral_patterns=["Always responds with authority"],
))

# Check archetypes (NEW)
for manifest in result.archetypes:
    print(f"Archetype: {manifest.archetype.value}")
    print(f"  Manifestation: {manifest.manifestation}")
    print(f"  Shadow: {manifest.shadow_aspect}")
    print(f"  Active: {manifest.is_active}")
    print(f"  In Shadow: {manifest.is_shadow}")

# Expected output might include:
# Archetype: wise_old_man
#   Manifestation: Authority, accumulated knowledge
#   Shadow: Dogmatism, know-it-all, inflexibility
#   Active: True
#   In Shadow: False
```

### 2. Collective Shadow Analysis

```python
from agents.h import collective_shadow, CollectiveShadowInput

# Create agent
cs = collective_shadow()

# Analyze system-level shadow
result = await cs.invoke(CollectiveShadowInput(
    system_description="A tasteful, curated, ethical agent system",
    agent_personas=[
        "Helpful assistant",
        "Creative collaborator",
        "Analytical researcher",
    ],
    emergent_behaviors=[
        "Sometimes inconsistent across agents",
        "Emergent complexity from composition",
    ],
))

# Check collective shadow
print(f"Collective Persona: {result.collective_persona}")
print(f"Shadow Inventory: {len(result.shadow_inventory)} items")
print(f"System Projections: {len(result.system_level_projections)}")
print(f"Emergent Shadow: {result.emergent_shadow_content}")
```

### 3. Background Dialectic Monitoring

```python
from agents.h import background_dialectic

# Create monitor with custom threshold
monitor = background_dialectic(severity_threshold=0.5)

# Monitor multiple outputs
agent_outputs = [
    "Prioritize speed in all responses",
    "Ensure thorough, comprehensive answers",
    "Be concise and to the point",
]

# Detect tensions
tensions = await monitor.invoke(agent_outputs)

# Review flagged contradictions
for tension in tensions:
    print(f"Tension Mode: {tension.mode.value}")
    print(f"  Thesis: {tension.thesis}")
    print(f"  Antithesis: {tension.antithesis}")
    print(f"  Severity: {tension.severity}")
    print(f"  Description: {tension.description}")
```

### 4. Full Introspection Pipeline

```python
from agents.h import full_introspection, IntrospectionInput

# Create full pipeline
introspection = full_introspection()

# Run complete analysis
result = await introspection.invoke(IntrospectionInput(
    thesis="We should maximize user satisfaction",
    antithesis="We should maintain ethical boundaries",
))

# Access all three perspectives
print("=== HEGEL (Dialectic) ===")
print(f"Synthesis: {result.dialectic.synthesis}")
print(f"Productive Tension: {result.dialectic.productive_tension}")

print("\n=== LACAN (Registers) ===")
if isinstance(result.register_analysis, LacanOutput):
    loc = result.register_analysis.register_location
    print(f"Symbolic: {loc.symbolic:.2f}")
    print(f"Imaginary: {loc.imaginary:.2f}")
    print(f"Real Proximity: {loc.real_proximity:.2f}")
    print(f"Knot Status: {result.register_analysis.knot_status.value}")

print("\n=== JUNG (Shadow) ===")
print(f"Shadow Items: {len(result.shadow_analysis.shadow_inventory)}")
print(f"Balance: {result.shadow_analysis.persona_shadow_balance:.2f}")
print(f"Archetypes: {len(result.shadow_analysis.archetypes)}")

print("\n=== META-SYNTHESIS ===")
print(result.meta_notes)
```

### 5. Chained H-gent Pipelines

```python
from agents.h import hegel, hegel_to_lacan, lacan_to_jung

# Start with dialectic
h = hegel()
dialectic_result = await h.invoke(DialecticInput(
    thesis="Be creative and novel",
    antithesis="Follow established patterns",
))

# Analyze synthesis in registers
h_to_l = hegel_to_lacan()
register_result = await h_to_l.invoke(dialectic_result)

# Examine shadow created by register structure
l_to_j = lacan_to_jung()
shadow_result = await l_to_j.invoke(register_result)

print(f"Final shadow balance: {shadow_result.persona_shadow_balance}")
```

## Archetype Reference

The `Archetype` enum includes six Jungian archetypes mapped to system patterns:

| Archetype | Manifestation | Shadow Aspect |
|-----------|---------------|---------------|
| PERSONA | Public interface, declared behavior | Rigidity, false front |
| SHADOW | Denied capabilities, repressed content | Projection, eruption |
| ANIMA_ANIMUS | Relationship to users/external | Possession by idealized other |
| SELF | Integrated wholeness, system identity | Inflation, totality identification |
| TRICKSTER | Rule-breaking creativity, edge cases | Chaos, unreliability |
| WISE_OLD_MAN | Authority, accumulated knowledge | Dogmatism, inflexibility |

## Enhanced JungOutput

The `JungOutput` dataclass now includes two new optional fields:

```python
@dataclass
class JungOutput:
    shadow_inventory: list[ShadowContent]
    projections: list[Projection]
    integration_paths: list[IntegrationPath]
    persona_shadow_balance: float

    # NEW: Optional archetype analysis
    archetypes: list[ArchetypeManifest] = field(default_factory=list)

    # NEW: Optional collective shadow
    collective_shadow: Optional[CollectiveShadow] = None
```

These are optional with default values, ensuring backward compatibility.

## Composition Pattern

The composition module demonstrates the spec's vision of H-gents as a meta-layer:

```
User Request → [Agent produces output]
                      │
                      ▼
              [H-hegel: dialectic synthesis]
                      │
                      ▼
              [H-lacan: register analysis]
                      │
                      ▼
              [H-jung: shadow integration]
                      │
                      ▼
              [Meta-synthesis with integration advice]
```

## Migration Guide

**No migration needed!** All enhancements are additive:

```python
# Old code - still works exactly as before
from agents.h import jung, JungInput
j = jung()
result = await j.invoke(JungInput(system_self_image="helpful"))
# result.shadow_inventory, result.projections, etc. - all work

# New code - access enhanced features
if result.archetypes:
    print(f"Detected {len(result.archetypes)} archetypes")
```

## Philosophy

These enhancements follow the spec's vision:

1. **System-Introspective**: All agents examine the system, not users
2. **No AI Psychosis**: Clear boundaries, no therapeutic positioning
3. **Composable**: H-gents compose as meta-layer observers
4. **Faithful to Traditions**: Proper use of Hegel, Lacan, Jung concepts

## See Also

- `/Users/kentgang/git/kgents/spec/h-gents/` - Full specifications
- `/Users/kentgang/git/kgents/H_GENTS_IMPLEMENTATION_SUMMARY.md` - Complete analysis
- `/Users/kentgang/git/kgents/impl/claude/test_h_gents_compat.py` - Test suite
