---
entity: library
context: world
version: 1.0
author: J-gent (JIT reference spec)
---

# world.library

A collection of knowledge artifacts. Libraries are generative spaces where
concepts crystallize into documents and documents compose into understanding.

> *"A library is not a collection of books. It is a possibility space
> of thoughts waiting to be thought."*

## Purpose

The library entity represents organized knowledge storage. Unlike raw
file systems, a library has:
- **Curation**: Not everything belongs; items are selected
- **Organization**: Items relate through semantic proximity
- **Context**: The library knows its purpose and scope

## Affordances

```yaml
affordances:
  # Architects see structural organization
  architect:
    - blueprint      # View organizational structure
    - measure        # Assess capacity and utilization
    - renovate       # Reorganize structure
    - design         # Plan new sections

  # Developers see technical access
  developer:
    - query          # Search contents
    - index          # Build/rebuild indices
    - deploy         # Publish changes
    - test           # Validate integrity

  # Scientists see research potential
  scientist:
    - analyze        # Statistical analysis of contents
    - experiment     # Test hypotheses against corpus
    - validate       # Verify claims against sources
    - forecast       # Predict knowledge gaps

  # Poets see experiential space
  poet:
    - describe       # Aesthetic description
    - inhabit        # Immersive experience
    - metaphorize    # Find metaphoric connections
    - contemplate    # Reflective engagement

  # Philosophers see conceptual structure
  philosopher:
    - refine         # Sharpen definitions
    - dialectic      # Challenge assumptions
    - synthesize     # Connect disparate ideas
    - critique       # Evaluate coherence

  # Economists see value flows
  economist:
    - appraise       # Assess value
    - forecast       # Project usage trends
    - compare        # Benchmark against others
    - trade          # Exchange resources

  # Default: core affordances only
  default:
    - manifest       # Basic view
    - witness        # History
    - affordances    # Available verbs
```

## Manifest

```yaml
manifest:
  architect:
    type: blueprint
    fields:
      - sections: list[Section]
      - capacity: int
      - utilization: float
      - last_reorganized: datetime

  developer:
    type: technical
    fields:
      - index_status: str
      - item_count: int
      - query_performance: dict
      - last_indexed: datetime

  scientist:
    type: scientific
    fields:
      - corpus_stats: dict
      - topic_distribution: list
      - citation_network: dict
      - knowledge_gaps: list

  poet:
    type: poetic
    fields:
      - description: str
      - mood: str
      - metaphors: list[str]
      - atmosphere: str

  philosopher:
    type: dialectic
    fields:
      - thesis: str
      - antithesis: str
      - synthesis: str
      - related_concepts: list[str]

  economist:
    type: economic
    fields:
      - market_value: float
      - usage_trends: dict
      - cost_per_query: float
      - roi: float

  default:
    type: basic
    fields:
      - summary: str
      - item_count: int
      - created_at: datetime
```

## State Schema

```yaml
state:
  # Core identity
  name: str
  created_at: datetime
  owner: str

  # Contents
  sections: list[Section]
  items: list[Item]
  indices: dict[str, Index]

  # Metadata
  last_modified: datetime
  access_count: int
  query_history: list[Query]
```

## Relations

```yaml
relations:
  # What the library contains
  contains:
    - world.book
    - world.document
    - world.article
    - concept.*  # Can contain abstract concepts

  # Ownership
  owned_by:
    - self.identity

  # Temporal
  witnessed_by:
    - time.trace

  # Conceptual
  categorized_by:
    - concept.taxonomy
```

## Behavior

### blueprint (architect)
Returns a structural diagram of the library's organization:
- Section hierarchy
- Capacity per section
- Cross-references between sections

### query (developer)
Executes a search against the library's indices:
- Full-text search
- Semantic similarity
- Filter by metadata

### analyze (scientist)
Returns statistical analysis:
- Topic modeling
- Citation analysis
- Coverage assessment

### describe (poet)
Returns an evocative description:
- Sensory details
- Emotional tone
- Metaphoric framing

### refine (philosopher)
Challenges and sharpens definitions:
- Identifies ambiguities
- Proposes distinctions
- Synthesizes perspectives

### appraise (economist)
Assesses value:
- Direct utility
- Opportunity cost
- Comparative advantage

## Example Invocations

```python
# Architect views structure
await logos.invoke("world.library.blueprint", architect_umwelt)
# Returns: BlueprintRendering with sections, capacity, utilization

# Poet describes the space
await logos.invoke("world.library.describe", poet_umwelt)
# Returns: PoeticRendering with mood, metaphors, atmosphere

# Developer searches
await logos.invoke("world.library.query", dev_umwelt, query="machine learning")
# Returns: QueryResult with matches, relevance scores

# Philosopher challenges
await logos.invoke("world.library.refine", phil_umwelt, concept="knowledge")
# Returns: DialecticRendering with thesis/antithesis/synthesis
```

## Notes

This is a reference spec demonstrating the full structure. Most specs
will be simpler, focusing on the specific affordances and behaviors
relevant to that entity.
