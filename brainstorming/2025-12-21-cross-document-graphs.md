# Cross-Document Graphs: The Knowledge Cathedral

> *"Every AGENTESE path is an edge. Every document is a node. The codebase is a navigable graph."*

---

## The Vision

Documents aren't isolated files—they're **nodes in a knowledge graph** connected by AGENTESE paths, requirements, references, and imports. You can navigate the graph visually, see what depends on what, and discover connections you didn't know existed.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE GRAPH VIEW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│     CLAUDE.md ─────references──────▶ spec/principles.md                     │
│         │                                   │                                │
│         │                                   ▼                                │
│         │                           Constitution.md                          │
│         │                                   │                                │
│         └──────includes───────▶ docs/skills/test-patterns.md                │
│                                        │                                     │
│                                        ▼                                     │
│                              impl/claude/services/brain/                     │
│                                   ┌────┴────┐                                │
│                                   │         │                                │
│                                   ▼         ▼                                │
│                              core.py    _tests/test_brain.py                │
│                                   │                                          │
│                                   │ imports                                  │
│                                   ▼                                          │
│                              persistence.py                                  │
│                                                                              │
│  [Focus: CLAUDE.md] [Depth: 3] [Show: references, imports] [Hide: tests]    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Synergies with Recent Work

### 1. Brain Spatial Cathedral

**Location**: `services/brain/`, `spec/agents/brain.md`

Brain Phase 3-4 already has:
- **Spatial Indexing**: Vector embeddings for semantic proximity
- **Cathedral Metaphor**: Memories organized in navigable space
- **Cartography**: Map of related concepts

**Synergy**: Brain's spatial index IS the graph. AGENTESE paths are edges. Semantic similarity adds implicit edges.

```python
# Brain already supports graph-like queries
await logos.invoke("self.brain.cartography", umwelt,
    center="CLAUDE.md",
    radius=3,  # Depth
)

# NEW: Make edges explicit
@dataclass(frozen=True)
class DocumentEdge:
    """An edge in the document graph."""
    source: Path
    target: Path
    edge_type: Literal["references", "imports", "includes", "tests", "implements"]
    weight: float = 1.0  # Based on reference count or semantic similarity
    agentese_path: str | None = None  # If edge is an AGENTESE path

# Brain indexes edges alongside content
await brain.index_edges(document, extract_edges(document))
```

### 2. AGENTESE-as-Route

**Location**: `spec/protocols/agentese-as-route.md`, `web/src/shell/`

AGENTESE-as-route already has:
- Every URL is an AGENTESE path
- UniversalProjection catches all paths
- Navigation is invocation

**Synergy**: Graph navigation IS AGENTESE navigation. Click an edge → navigate to target via AGENTESE path.

```typescript
// Graph node click → AGENTESE navigation
const handleNodeClick = (node: GraphNode) => {
  if (node.agentesePath) {
    navigate(`/${node.agentesePath}`);  // self.document.graph → /self.document.graph
  } else {
    navigate(`/self.document.view?path=${node.path}`);
  }
};
```

### 3. Living Docs Cross-References

**Location**: `services/living_docs/`, `plans/living-docs-reference-generation.md`

Living Docs already extracts:
- Module documentation
- "Gotchas" and best practices
- Evidence links (spec → test)

**Synergy**: Living Docs provides the edges. Graph visualization renders them.

```python
# Living Docs already extracts references
from services.living_docs import extract_references

refs = await extract_references("CLAUDE.md")
# [
#   Reference(source="CLAUDE.md", target="spec/principles.md", type="references"),
#   Reference(source="CLAUDE.md", target="docs/skills/", type="includes"),
# ]

# These become graph edges
edges = [
    DocumentEdge(
        source=ref.source,
        target=ref.target,
        edge_type=ref.type,
    )
    for ref in refs
]
```

### 4. Interactive Text AGENTESE Paths

**Location**: `services/interactive_text/tokens/agentese_path.py`

Interactive Text already:
- Recognizes AGENTESE paths in text
- Provides navigation affordance
- Tracks source position

**Synergy**: Every AGENTESE path token is a potential edge. Extract paths → build graph.

```python
# Extract AGENTESE paths from document
from services.interactive_text import parse_markdown

doc = parse_markdown(content)
agentese_tokens = [t for t in doc.tokens if t.token_type == "agentese_path"]

# Each path is an edge to its target
edges = []
for token in agentese_tokens:
    path = token.token_match.groups()[0]  # e.g., "self.brain.capture"
    target = resolve_agentese_path(path)  # → services/brain/core.py
    if target:
        edges.append(DocumentEdge(
            source=document_path,
            target=target,
            edge_type="references",
            agentese_path=path,
        ))
```

### 5. Servo SceneGraph

**Location**: `protocols/agentese/projection/scene.py`, `web/src/components/servo/`

Servo already has:
- SceneGraph with nodes and edges
- SceneEdge for connections
- Layout algorithms

**Synergy**: Document graph → SceneGraph → Servo renders it.

```python
# Document graph → SceneGraph
def document_graph_to_scene(graph: DocumentGraph) -> SceneGraph:
    nodes = [
        SceneNode(
            id=generate_node_id(),
            kind=SceneNodeKind.PANEL,
            content={"path": str(doc.path), "title": doc.title},
            label=doc.path.name,
            metadata={"document_type": doc.type},
        )
        for doc in graph.documents
    ]

    edges = [
        SceneEdge(
            source=edge.source_id,
            target=edge.target_id,
            label=edge.edge_type,
            metadata={"agentese_path": edge.agentese_path},
        )
        for edge in graph.edges
    ]

    return SceneGraph.from_nodes(
        nodes=nodes,
        edges=edges,
        layout=LayoutDirective.free(),  # Force-directed layout
    )
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DOCUMENT GRAPH SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Edge Extractors (Multiple Sources)                                  │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │  - AGENTESE Path Tokens → edges to resolved targets                 │    │
│  │  - Python imports → edges to imported modules                       │    │
│  │  - Markdown links → edges to linked files                           │    │
│  │  - Requirement refs → edges to spec files                           │    │
│  │  - Test files → edges to tested modules                             │    │
│  │  - Semantic similarity → implicit edges (Brain)                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Graph Index (Brain + Custom)                                        │    │
│  │  - Nodes: documents, modules, functions                             │    │
│  │  - Edges: typed, weighted, directional                              │    │
│  │  - Queries: neighbors, paths, clusters                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  AGENTESE Interface (concept.graph.*)                                │    │
│  │  - concept.graph.neighbors(node, depth)                             │    │
│  │  - concept.graph.path(from, to)                                     │    │
│  │  - concept.graph.cluster(topic)                                     │    │
│  │  - concept.graph.visualize(center, options)                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  SceneGraph Projection                                               │    │
│  │  - Nodes as SceneNodes (PANEL kind)                                 │    │
│  │  - Edges as SceneEdges (styled by type)                             │    │
│  │  - Force-directed layout (free mode)                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Servo Visualization                                                 │    │
│  │  - Interactive graph view                                           │    │
│  │  - Click node → navigate                                            │    │
│  │  - Hover edge → show path                                           │    │
│  │  - Filter by edge type                                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Edge Types

| Type | Source | Example |
|------|--------|---------|
| `references` | AGENTESE paths, markdown links | `self.brain.capture` → `services/brain/core.py` |
| `imports` | Python imports | `from services.brain import Brain` |
| `tests` | Test file naming convention | `_tests/test_brain.py` → `brain/core.py` |
| `implements` | Spec → impl mapping | `spec/agents/brain.md` → `services/brain/` |
| `includes` | Directory references | `docs/skills/` in CLAUDE.md |
| `similar` | Semantic similarity (Brain) | High cosine similarity |
| `derives` | Principle/requirement derivation | `[P1]` → `spec/principles.md#1` |

---

## Implementation Phases

### Phase 1: Edge Extraction
- Extract AGENTESE paths from all documents
- Extract Python imports from all .py files
- Extract markdown links from all .md files
- Store as `DocumentEdge` in graph index

### Phase 2: Graph Index
- Build adjacency list from edges
- Add to Brain for vector queries
- Create `concept.graph.*` AGENTESE nodes

### Phase 3: Basic Visualization
- `concept.graph.neighbors` → SceneGraph
- Servo renders as force-directed graph
- Click node → navigate

### Phase 4: Advanced Queries
- Find path between any two documents
- Cluster by topic (semantic similarity)
- Find orphan documents (no incoming edges)

### Phase 5: Interactive Explorer
- Full-page graph explorer at `/_/graph`
- Filters by edge type, depth
- Search nodes by name or content

---

## Query Examples

```python
# What does CLAUDE.md reference?
neighbors = await logos.invoke("concept.graph.neighbors", umwelt,
    node="CLAUDE.md",
    direction="outgoing",
    depth=1,
)

# How do I get from CLAUDE.md to test_brain.py?
path = await logos.invoke("concept.graph.path", umwelt,
    from_node="CLAUDE.md",
    to_node="services/brain/_tests/test_brain.py",
)
# → CLAUDE.md → services/brain/ → services/brain/_tests/test_brain.py

# What documents cluster around "memory"?
cluster = await logos.invoke("concept.graph.cluster", umwelt,
    topic="memory storage retrieval",
    limit=10,
)
# → services/brain/, spec/agents/m-gent.md, services/memory/...

# Find orphan documents (not referenced by anything)
orphans = await logos.invoke("concept.graph.orphans", umwelt)
# → [brainstorming/old-idea.md, docs/deprecated/...]

# Visualize the graph centered on a node
scene = await logos.invoke("concept.graph.visualize", umwelt,
    center="CLAUDE.md",
    depth=2,
    edge_types=["references", "implements"],
)
# → SceneGraph for Servo rendering
```

---

## Open Questions

1. **Granularity**: Document-level? Function-level? Line-level?

2. **Edge Direction**: Always directional? Some bidirectional?

3. **Weight Calculation**: Reference count? Semantic similarity? Recency?

4. **Layout Algorithm**: Force-directed? Hierarchical? User choice?

5. **Scale**: How to handle 1000+ documents? Pagination? LOD (level of detail)?

6. **Live Updates**: Rebuild on every change? Incremental? Background?

---

## Research Cues

### Knowledge Graphs
- **RDF/OWL**: Semantic web standards
- **Neo4j**: Graph database
- **Knowledge Graph Embeddings**: TransE, RotatE
- 🔍 *Search: "knowledge graph construction from code repositories"*

### Code Navigation
- **Sourcegraph**: Code search and navigation
- **GitHub code navigation**: "Find references"
- **LSP (Language Server Protocol)**: Go to definition, find references
- 🔍 *Search: "semantic code navigation tools 2024"*

### Personal Knowledge Management
- **Roam Research**: Bidirectional linking
- **Obsidian**: Graph view, backlinks
- **Notion**: Relational databases
- 🔍 *Search: "obsidian graph view algorithms"*

### Graph Visualization
- **D3.js force-directed**: Classic approach
- **Cytoscape.js**: Scientific graph viz
- **Sigma.js**: Large graph rendering
- **Graphviz**: DOT language, layered layout
- 🔍 *Search: "interactive graph visualization large datasets"*

### Graph Algorithms
- **PageRank**: Node importance
- **Community Detection**: Louvain, Girvan-Newman
- **Shortest Path**: Dijkstra, A*
- **Centrality Measures**: Betweenness, closeness
- 🔍 *Search: "graph algorithms knowledge base navigation"*

---

## Maximum Value Opportunities

### 1. "Where Is This Used?"
Click any function, class, or document → see all references instantly. No grep needed.

### 2. Impact Analysis
"If I change brain.py, what else might break?" → Follow the graph.

### 3. Documentation Discovery
"I know CLAUDE.md exists, but what else should I read?" → Follow references.

### 4. Onboarding Path
Auto-generate reading order: "Start here → then this → then this." Based on graph topology.

### 5. Orphan Detection
Find documents no one references. Either delete or connect them.

### 6. Dependency Visualization
See import graph. Find circular dependencies. Understand architecture at a glance.

### 7. Semantic Clustering
"Show me everything related to authentication." Graph clusters by topic.

---

## Voice Anchors

> *"The verb is the fundamental unit"* — Edges (verbs: references, imports, tests) matter more than nodes (nouns).

> *"Composable"* — Graph is just another projection. Same data, different view.

> *"Heterarchical"* — No single root. Multiple entry points. Peer-to-peer connections.

---

## Connection to Constitution

From Principle 5 (Composable):
> "Agents can be combined: A + B → AB (composition)"

Documents compose the same way. CLAUDE.md + skills + services = the system.

From Principle 4 (Joy-Inducing):
> "Surprise and serendipity welcome: Discovery should feel rewarding"

Graph view enables serendipitous discovery. "Oh, I didn't know these were connected!"

---

## Connection to Brain Architecture

Brain's "Spatial Cathedral" metaphor maps perfectly:

| Brain Concept | Graph Concept |
|---------------|---------------|
| Memory | Document node |
| Vector embedding | Node position |
| Semantic similarity | Implicit edge |
| Cartography | Graph visualization |
| Surface (query) | Graph traversal |

The graph IS the cathedral. Documents are rooms. Edges are hallways.

---

*Created: 2025-12-21 | Building on: Brain, AGENTESE-as-route, Living Docs, Interactive Text, Servo*
*Next: Research Obsidian graph algorithm, prototype edge extraction*
