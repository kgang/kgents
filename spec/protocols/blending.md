# Conceptual Blending Protocol

> *"Creativity is the mapping of structure from Domain A to Domain B to create Blended Space C."*

**Status:** Specification v1.0
**Date:** 2025-12-11
**Prerequisites:** `agentese.md`, `../principles.md`
**Source:** Fauconnier & Turner's Conceptual Blending Theory, Koestler's Bisociation
**Integrations:** Logos, concept.blend.* context

---

## Prologue: The Act of Creation

Koestler's "bisociation" describes creativity as the intersection of two previously unconnected frames of reference. When a scientist sees falling apples and orbiting moons as instances of the same phenomenon, that's bisociation. When a comedian connects two unrelated contexts for a punchline, that's bisociation.

Fauconnier and Turner formalized this as **Conceptual Blending**: the cognitive operation of combining two "mental spaces" into a novel "blended space" with emergent properties.

```
    Input Space A          Input Space B
         \                    /
          \                  /
           \                /
            \              /
         Generic Space (shared structure)
                  |
                  v
           Blended Space
        (emergent features)
```

---

## Part I: Core Concepts

### 1.1 Mental Spaces

A **mental space** is a structured conceptual domain with:
- **Entities**: The objects/actors in the space
- **Relations**: How entities relate to each other
- **Properties**: Attributes of entities

Examples:
- "Argument as War" space: opponents, attacks, defenses, victory
- "Computer Desktop" space: files, folders, trash, windows

### 1.2 The Four Spaces

| Space | Role | Example (Surgeon-Butcher blend) |
|-------|------|----------------------------------|
| **Input Space A** | First concept | Surgeon: healer, scalpel, precision, life |
| **Input Space B** | Second concept | Butcher: cutter, cleaver, meat, death |
| **Generic Space** | Shared abstract structure | Cutter, tool, organic material |
| **Blended Space** | Novel synthesis | "That surgeon is a butcher" (criticism) |

### 1.3 Emergent Features

The blended space is not merely the sum of inputs. It has **emergent features**—properties that exist only in the blend:

- In "Surgeon-Butcher": incompetence, carelessness (neither surgeon nor butcher typically implies these)
- In "Computer Desktop": "throwing file in trash" (neither physical desktops nor trashcans involve this action)

---

## Part II: The BlendResult Structure

```python
@dataclass(frozen=True)
class BlendResult:
    """Result of conceptual blending operation."""

    input_space_a: str           # First mental space (concept path or description)
    input_space_b: str           # Second mental space (concept path or description)
    generic_space: list[str]     # Shared abstract structural relations
    blended_space: str           # The novel synthesis description
    emergent_features: list[str] # Properties that exist only in the blend
    alignment_score: float       # Structural isomorphism quality (0.0-1.0)
```

### 2.1 Field Definitions

**input_space_a / input_space_b**
- The source concepts being blended
- Can be AGENTESE paths (`concept.democracy`, `world.git`) or descriptions

**generic_space**
- The shared abstract structure between inputs
- Found via Structure Mapping Engine (SME) pattern
- Examples: "has_participants", "has_conflict", "produces_outcome"

**blended_space**
- The novel conceptual synthesis
- A description of the new concept that emerges

**emergent_features**
- Properties in the blend that don't exist in either input
- The "aha!" insight of creativity

**alignment_score**
- Quality metric for structural isomorphism
- `len(generic_space) / max(len(relations_a), len(relations_b))`
- Higher = better structural alignment

---

## Part III: AGENTESE Integration

### 3.1 The Blend Context

Blending operates within `concept.*` as a sub-context: `concept.blend.*`

| Path | Meaning | Returns |
|------|---------|---------|
| `concept.blend.forge` | Create blend from two inputs | `BlendResult` |
| `concept.blend.analyze` | Decompose an existing blend | Analysis dict |
| `concept.blend.generic` | Find generic space only | `list[str]` |
| `concept.blend.emergent` | Extract emergent features | `list[str]` |

### 3.2 Affordances

```python
BLEND_AFFORDANCES = {
    "blend": ("forge", "analyze", "generic", "emergent"),
}
```

All archetypes have access to blend operations, though results vary:
- **Philosophers**: Emphasize dialectical synthesis
- **Scientists**: Focus on structural isomorphism
- **Artists**: Prioritize emergent/surprising features

### 3.3 Usage Examples

```python
# Basic blending
result = await logos.invoke(
    "concept.blend.forge",
    observer,
    concept_a="concept.democracy",
    concept_b="world.git",
)
# → BlendResult(
#     input_space_a="concept.democracy",
#     input_space_b="world.git",
#     generic_space=["has_participants", "has_proposals", "has_voting"],
#     blended_space="Governance via Pull Requests",
#     emergent_features=["fork_as_secession", "merge_conflicts_as_debate"],
#     alignment_score=0.75,
# )

# Analyze existing blend
analysis = await logos.invoke(
    "concept.blend.analyze",
    observer,
    blend="computer desktop metaphor",
)
```

---

## Part IV: The Structure Mapping Engine (SME) Pattern

### 4.1 Relation Extraction

Before blending, extract relations from each concept:

```python
relations_a = await logos.invoke(f"{concept_a}.relations", observer)
# → ["has_citizens", "has_voting", "produces_laws", "has_representation"]

relations_b = await logos.invoke(f"{concept_b}.relations", observer)
# → ["has_contributors", "has_commits", "produces_code", "has_branches"]
```

### 4.2 Structural Alignment

Find structural isomorphism via token overlap and semantic similarity:

1. **Lexical matching**: "has_voting" ≈ "has_commits" (both involve choices)
2. **Role mapping**: "citizens" ↔ "contributors" (both are participants)
3. **Outcome mapping**: "laws" ↔ "code" (both are outputs)

### 4.3 Generic Space Construction

The generic space contains the abstract relations shared by both:

```
generic_space = [
    "has_participants",    # citizens/contributors
    "has_proposals",       # bills/pull requests
    "has_deliberation",    # debate/code review
    "produces_artifacts",  # laws/merged code
]
```

### 4.4 Emergent Feature Detection

Features that appear in the blend but not inputs:

```python
def identify_emergent(blend: str, relations_a: set, relations_b: set) -> list[str]:
    """Find novel properties in blend not present in inputs."""
    blend_tokens = extract_concepts(blend)
    input_tokens = relations_a | relations_b
    return [t for t in blend_tokens if t not in input_tokens]
```

---

## Part V: Integration with Creativity Pipeline

### 5.1 With Wundt Curator

Blending output should be filtered by the Curator:

```python
blend_result = await logos.invoke("concept.blend.forge", observer, ...)
taste = await logos.invoke("self.judgment.taste", observer, content=blend_result.blended_space)

if taste.verdict == "boring":
    # Blend is too predictable, try different inputs
    pass
elif taste.verdict == "chaotic":
    # Blend is incomprehensible, constrain more
    pass
```

### 5.2 As Remediation

The Curator uses blending to enhance boring output:

```python
# In WundtCurator._enhance():
enhanced = await logos.invoke(
    "concept.blend.forge",
    observer,
    concept_a=str(boring_result),
    concept_b=await logos.invoke("void.entropy.sip", observer),  # Random injection
)
```

### 5.3 With Critic's Loop (Phase 7)

Blends can be critiqued for novelty and utility:

```python
critique = await logos.invoke(
    "self.judgment.critique",
    observer,
    artifact=blend_result,
    criteria=["novelty", "utility", "coherence"],
)
```

---

## Part VI: Principle Alignment

| Principle | How Blending Aligns |
|-----------|---------------------|
| **Tasteful** | Alignment score ensures quality blends |
| **Curated** | Generic space extraction is selective |
| **Ethical** | Observer context shapes blend interpretation |
| **Joy-Inducing** | Emergent features create surprise |
| **Composable** | Blends can be inputs to further blends |
| **AGENTESE** | Observer-dependent blend interpretation |

---

## Appendix A: Implementation Notes

### A.1 Fallback Behavior

When concept relations cannot be extracted:
1. Use string tokenization as proxy for relations
2. Generic space = overlapping tokens
3. Emergent features = tokens in blend description not in inputs

### A.2 Alignment Score Interpretation

| Score | Meaning |
|-------|---------|
| 0.0-0.2 | Poor alignment, blends may be incoherent |
| 0.2-0.5 | Moderate alignment, creative but risky |
| 0.5-0.8 | Good alignment, balanced novelty |
| 0.8-1.0 | High alignment, may lack novelty |

### A.3 Caching Strategy

BlendResults are immutable (frozen dataclass) and can be cached:
- Key: `(input_space_a, input_space_b, observer.archetype)`
- TTL: Session-scoped or explicit invalidation

---

## References

1. Fauconnier, G. & Turner, M. (2002). *The Way We Think: Conceptual Blending and the Mind's Hidden Complexities*
2. Koestler, A. (1964). *The Act of Creation*
3. Gentner, D. (1983). Structure-Mapping: A Theoretical Framework for Analogy. *Cognitive Science*
4. Veale, T. (2012). *Exploding the Creativity Myth: The Computational Foundations of Linguistic Creativity*
