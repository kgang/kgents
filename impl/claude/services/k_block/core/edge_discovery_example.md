# Edge Discovery Enhancement: Examples

> *"The edge IS the proof. The discovery IS the witness."*

This document demonstrates the enhanced edge discovery service that goes beyond simple markdown links.

## What Was Enhanced

The original integration protocol (`services/sovereign/integration.py`) only discovered explicit markdown links using a simple regex:

```python
# OLD: Only markdown links
link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
```

The new `EdgeDiscoveryService` (`services/k_block/core/edge_discovery.py`) discovers:

1. **Explicit edges** - Markdown links, portal tokens (with richer classification)
2. **Semantic edges** - Concept mentions, content similarity
3. **Structural edges** - Zero Seed layer relationships
4. **Contradiction edges** - Super-additive loss patterns

## Edge Types Discovered

### Explicit Edges

```python
from services.k_block.core.edge_discovery import EdgeKind

EdgeKind.DERIVES_FROM    # Parent-child derivation
EdgeKind.IMPLEMENTS      # Spec -> Impl
EdgeKind.TESTS           # Test -> Source
EdgeKind.REFERENCES      # Generic markdown link
EdgeKind.EXTENDS         # Extension relationship
```

**Example:**

```markdown
# Source
Implements [PolyAgent spec](spec/protocols/poly-agent.md).
See tests: [test_poly.py](_tests/test_poly.py)
```

**Discovered:**
- `IMPLEMENTS` edge: my-impl.py → spec/protocols/poly-agent.md (95% confidence)
- `TESTS` edge: my-impl.py → _tests/test_poly.py (95% confidence)

### Semantic Edges

```python
EdgeKind.MENTIONS        # Content mentions concepts from another K-Block
EdgeKind.SIMILAR_TO      # Semantically similar content
EdgeKind.RELATED_BY_LAYER # Same layer, related concepts
```

**Example:**

Document A (spec/poly-agent.md):
```markdown
A **PolyAgent** is a polynomial functor.
AXIOM POLY1: Agents are morphisms.
```

Document B (impl/agent.py):
```markdown
Using PolyAgent[S,A,B] pattern.
Following AXIOM POLY1 from the spec.
```

**Discovered:**
- `MENTIONS` edge: impl/agent.py → spec/poly-agent.md (75% confidence)
  - Reasoning: "Mentions concepts defined in target: PolyAgent, POLY1"
- `SIMILAR_TO` edge: impl/agent.py → spec/poly-agent.md (66% confidence)
  - Reasoning: "Semantically similar content (similarity=65.95%)"

### Structural Edges (Zero Seed Layers)

```python
EdgeKind.GROUNDS        # L1 → L2 (axiom grounds value)
EdgeKind.JUSTIFIES      # L2 → L3 (value justifies goal)
EdgeKind.SPECIFIES      # L3 → L4 (goal specifies spec)
EdgeKind.REALIZES       # L4 → L5 (spec realizes implementation)
EdgeKind.REFLECTS_ON    # L6 → L1-L5 (reflection on prior layers)
EdgeKind.REPRESENTS     # L7 → any (representation of content)
```

**Example:**

Document A (spec/axioms.md, Layer 1):
```markdown
AXIOM COMP: Agents compose.
```

Document B (spec/values.md, Layer 2):
```markdown
Value: Composition is essential.
```

**Discovered:**
- `GROUNDS` edge: spec/axioms.md → spec/values.md (65% confidence)
  - Reasoning: "Layer 1 grounds Layer 2"
  - Context: "Zero Seed layer relationship: L1 -> L2"

### Contradiction Edges

```python
EdgeKind.CONTRADICTS    # Semantic contradiction
EdgeKind.CONFLICTS_WITH # Structural conflict
```

**Example:**

Document A (spec/properties.md):
```markdown
Agents can compose. Composition is associative.
```

Document B (spec/counter.md):
```markdown
Agents cannot compose. Composition is not associative.
```

**Discovered:**
- `CONTRADICTS` edge: spec/counter.md → spec/properties.md (60% confidence)
  - Reasoning: "Potential contradiction: source negates 'compose', target asserts it"
  - Context: "Negated term: compose"
- `CONTRADICTS` edge: spec/counter.md → spec/properties.md (60% confidence)
  - Reasoning: "Potential contradiction: source negates 'associative', target asserts it"
  - Context: "Negated term: associative"

## Usage

### Basic Discovery (Explicit Only)

```python
from services.k_block.core.edge_discovery import get_edge_discovery_service

service = get_edge_discovery_service()

content = """
# My Spec
See [other spec](spec/other.md).
"""

edges = service.discover_edges(
    content=content,
    source_path="spec/my-spec.md",
)
# Returns: [DiscoveredEdge(REFERENCES, ...)]
```

### Full Discovery (With Corpus)

```python
# Build corpus from existing K-Blocks
corpus = {
    "spec/poly-agent.md": {
        "content": "PolyAgent definition...",
        "layer": 4,
    },
    "spec/axioms.md": {
        "content": "AXIOM COMP...",
        "layer": 1,
    },
}

edges = service.discover_edges(
    content=content,
    source_path="impl/agent.py",
    source_layer=5,
    corpus=corpus,
)
# Returns: [
#   DiscoveredEdge(MENTIONS, ...),
#   DiscoveredEdge(SIMILAR_TO, ...),
#   DiscoveredEdge(REALIZES, ...),
# ]
```

### Integration with Sovereign

The integration protocol now automatically uses `EdgeDiscoveryService`:

```python
# In services/sovereign/integration.py

async def _discover_edges(self, content: bytes, source_path: str) -> list[DiscoveredEdge]:
    """Step 4: Discover edges using enhanced service."""
    from services.k_block.core.edge_discovery import get_edge_discovery_service

    service = get_edge_discovery_service(self.kgents_root)
    discovered = service.discover_edges(
        content=text,
        source_path=source_path,
        source_layer=None,  # Will be assigned in step 2
        corpus=None,  # TODO: Build from existing K-Blocks
    )

    # Convert to integration.DiscoveredEdge format
    ...
```

## Confidence Scores

All edges return confidence scores `[0.0, 1.0]`:

| Edge Type | Confidence | Reasoning |
|-----------|------------|-----------|
| Explicit markdown links | 0.90-0.95 | High - user explicitly linked |
| Portal tokens | 0.90 | High - kgents-native reference |
| Concept mentions | 0.75 | Medium-high - shared concepts found |
| Semantic similarity | 0.50-0.85 | Variable - based on similarity score |
| Layer relationships | 0.65 | Medium - structural heuristic |
| Contradictions | 0.55-0.60 | Low-medium - needs Galois verification |

## Conversion to KBlockEdge

`DiscoveredEdge` can be converted to `KBlockEdge` format for persistence:

```python
edge = DiscoveredEdge(
    source_id="kb_abc123",
    target_id="kb_xyz789",
    kind=EdgeKind.IMPLEMENTS,
    confidence=0.85,
    reasoning="Implements the specification",
)

kblock_edge_dict = edge.to_kblock_edge()
# Returns dict suitable for KBlockEdge.from_dict()

kblock_edge = KBlockEdge.from_dict(kblock_edge_dict)
```

## Future Enhancements

1. **Galois Loss Integration**: Use `GaloisLossComputer` for super-additive loss detection
2. **Corpus Building**: Automatically build corpus from `Cosmos` K-Blocks
3. **Edge Strength Learning**: Train confidence scores from user feedback
4. **Multi-hop Reasoning**: Discover transitive relationships (A→B→C implies A relates to C)
5. **Temporal Edges**: Track how edges evolve over time (strengthening/weakening)

## Philosophy

> *"Every edge is a hypothesis with evidence."*

We don't assert edges—we suggest them with confidence scores. The user or system decides whether to accept the suggestion. This aligns with the Linear philosophy: suggestions, not assertions.

## Tests

See `services/k_block/_tests/test_edge_discovery.py` for comprehensive test coverage.

---

**Location**: `/Users/kentgang/git/kgents/impl/claude/services/k_block/core/edge_discovery.py`

**Wired into**: `services/sovereign/integration.py` (Step 4: Discover edges)

**Philosophy**: "The edge IS the proof. The discovery IS the witness."
