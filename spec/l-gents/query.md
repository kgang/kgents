# L-gent Query: Search & Resolution

**Purpose**: Define the three-brain search architecture and dependency resolution patterns.

---

## Overview

L-gent's query layer transforms the catalog into an **intelligent search engine**. It combines three retrieval strategies—keyword, semantic, and graph—into a unified interface that answers questions ranging from exact lookups to fuzzy intent matching.

The goal: **Make the right artifact findable**, whether the searcher knows its name, can describe what it does, or only knows what it needs to connect to.

## The Three-Brain Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Query Request                           │
│  "Find an agent that processes PDF financial documents"      │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Brain 1:      │ │   Brain 2:      │ │   Brain 3:      │
│   Keyword       │ │   Semantic      │ │   Graph         │
│   (BM25)        │ │   (Embeddings)  │ │   (Traversal)   │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ Exact matches   │ │ Intent match    │ │ Relationships   │
│ "PDF" in name   │ │ Similar to      │ │ Implements X    │
│ Tagged "finance"│ │ "document proc" │ │ Compatible with │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
                  ┌─────────────────────┐
                  │   Fusion Layer      │
                  │   Score & Rank      │
                  │   Explain & Suggest │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │   Query Results     │
                  │   + Serendipity     │
                  └─────────────────────┘
```

## Brain 1: Keyword Search (BM25)

**Strength**: Exact matches, known names, explicit tags.

### When It Excels

- User knows the artifact name: `"NewsParser"`
- Searching by explicit tag: `"authentication"`
- Version queries: `"v2.x"`
- Author queries: `"forged_by:F-gent"`

### Implementation

```python
class KeywordBrain:
    """BM25-based keyword search over catalog metadata."""

    def __init__(self, registry: Registry):
        self.index = BM25Index()
        self.registry = registry

    async def search(
        self,
        query: str,
        fields: list[str] = ["name", "description", "keywords"],
        filters: dict[str, Any] | None = None,
        limit: int = 10
    ) -> list[KeywordResult]:
        """
        Search using BM25 ranking.

        Query syntax:
        - Simple terms: "pdf parser"
        - Exact phrase: '"financial analysis"'
        - Field-specific: "name:Parser"
        - Boolean: "pdf AND (parser OR extractor)"
        - Wildcard: "News*"
        """
        # Parse query into terms
        terms = self._parse_query(query)

        # Search each field
        candidates = []
        for field in fields:
            matches = self.index.search(field, terms)
            candidates.extend(matches)

        # Apply filters
        if filters:
            candidates = self._apply_filters(candidates, filters)

        # Score and rank
        scored = self._bm25_score(candidates, terms)

        return sorted(scored, key=lambda r: r.score, reverse=True)[:limit]

    async def index_entry(self, entry: CatalogEntry) -> None:
        """Add or update entry in keyword index."""
        doc = {
            "id": entry.id,
            "name": entry.name,
            "description": entry.description,
            "keywords": " ".join(entry.keywords),
            "author": entry.author,
            "type": entry.entity_type.value
        }
        self.index.add_document(entry.id, doc)

@dataclass
class KeywordResult:
    """Result from keyword search."""
    id: str
    score: float           # BM25 score
    matched_fields: list[str]  # Which fields matched
    highlights: dict[str, str]  # Snippets with highlights
```

### Query Syntax Examples

```python
# Simple search
await keyword_brain.search("summarizer")

# Exact phrase
await keyword_brain.search('"executive summary"')

# Field-specific
await keyword_brain.search("author:F-gent type:agent")

# Boolean
await keyword_brain.search("(pdf OR html) AND parser")

# Wildcard
await keyword_brain.search("News* version:2.*")

# With filters
await keyword_brain.search(
    "parser",
    filters={"status": Status.ACTIVE, "entity_type": EntityType.AGENT}
)
```

## Brain 2: Semantic Search (Embeddings)

**Strength**: Intent matching, fuzzy discovery, "I don't know what it's called but..."

### When It Excels

- Describing desired behavior: "something that cleans up messy text"
- Cross-domain connections: "like a translator but for data formats"
- Discovery: "what exists for sentiment analysis?"

### Implementation

```python
class SemanticBrain:
    """Vector-based semantic search over artifact descriptions."""

    def __init__(self, vectors: VectorAgent, embedder: Embedder):
        self.vectors = vectors
        self.embedder = embedder

    async def search(
        self,
        intent: str,
        filters: dict[str, Any] | None = None,
        threshold: float = 0.5,
        limit: int = 10
    ) -> list[SemanticResult]:
        """
        Search by semantic similarity to intent.

        Steps:
        1. Embed the intent query
        2. Find nearest neighbors in vector space
        3. Apply filters
        4. Return ranked results with similarity scores
        """
        # Embed query
        query_embedding = await self.embedder.embed(intent)

        # Vector search (approximate nearest neighbors)
        neighbors = await self.vectors.search(
            vector=query_embedding,
            limit=limit * 2,  # Over-fetch for filtering
            threshold=threshold
        )

        # Apply filters
        if filters:
            neighbors = await self._filter_results(neighbors, filters)

        # Build results
        results = []
        for neighbor in neighbors[:limit]:
            entry = await self.registry.get(neighbor.id)
            results.append(SemanticResult(
                id=neighbor.id,
                score=neighbor.similarity,
                entry=entry,
                explanation=self._explain_match(intent, entry.description)
            ))

        return results

    async def find_similar(
        self,
        artifact_id: str,
        limit: int = 5
    ) -> list[SemanticResult]:
        """Find artifacts semantically similar to a given one."""
        entry = await self.registry.get(artifact_id)
        if not entry or not entry.embedding:
            return []

        neighbors = await self.vectors.search(
            vector=entry.embedding,
            limit=limit + 1  # Exclude self
        )

        return [
            SemanticResult(id=n.id, score=n.similarity)
            for n in neighbors if n.id != artifact_id
        ]

@dataclass
class SemanticResult:
    """Result from semantic search."""
    id: str
    score: float              # Cosine similarity (0-1)
    entry: CatalogEntry | None
    explanation: str | None   # Why this matched
```

### Embedding Strategy

```python
class CatalogEmbedder:
    """Generate embeddings for catalog entries."""

    def __init__(self, model: str = "text-embedding-ada-002"):
        self.model = model

    async def embed_entry(self, entry: CatalogEntry) -> list[float]:
        """
        Create embedding from entry metadata.

        Combines multiple fields for richer representation:
        - Name (weighted 2x)
        - Description (weighted 3x)
        - Keywords (weighted 1x)
        - Type signature (weighted 1x)
        """
        text = f"""
        Name: {entry.name}
        Name: {entry.name}
        Description: {entry.description}
        Description: {entry.description}
        Description: {entry.description}
        Keywords: {' '.join(entry.keywords)}
        Type: {entry.input_type} -> {entry.output_type}
        """
        return await self._embed(text.strip())

    async def embed_query(self, query: str) -> list[float]:
        """Embed a search query."""
        return await self._embed(query)
```

## Brain 3: Graph Search (Traversal)

**Strength**: Relationships, compatibility, "what works with X?"

### When It Excels

- Compatibility queries: "agents that can receive NewsParser output"
- Dependency queries: "what does StockTicker depend on?"
- Lineage queries: "what evolved from BaseScraper?"
- Composition planning: "path from RawHTML to Summary"

### Implementation

```python
class GraphBrain:
    """Graph-based search over artifact relationships."""

    def __init__(self, lineage: GraphAgent, lattice: LatticeAgent):
        self.lineage = lineage
        self.lattice = lattice

    async def find_compatible(
        self,
        artifact_id: str,
        direction: str = "downstream"  # or "upstream"
    ) -> list[GraphResult]:
        """
        Find artifacts that can compose with the given one.

        downstream: What can receive this artifact's output?
        upstream: What can feed into this artifact's input?
        """
        entry = await self.registry.get(artifact_id)
        if not entry:
            return []

        if direction == "downstream":
            # Find agents whose input_type is compatible with our output_type
            target_type = entry.output_type
            compatible = await self.lattice.find_subtypes(target_type)
            candidates = await self.registry.find_by_input_type(compatible)
        else:
            # Find agents whose output_type is compatible with our input_type
            target_type = entry.input_type
            compatible = await self.lattice.find_supertypes(target_type)
            candidates = await self.registry.find_by_output_type(compatible)

        return [
            GraphResult(
                id=c.id,
                relationship="compatible",
                path_length=1,
                explanation=f"Type {target_type} matches"
            )
            for c in candidates
        ]

    async def find_path(
        self,
        source_type: str,
        target_type: str,
        max_length: int = 5
    ) -> list[list[str]] | None:
        """
        Find composition paths from source to target type.

        Returns list of artifact IDs that form valid pipelines.
        """
        # BFS over type-compatible agents
        queue = [(source_type, [])]
        visited = {source_type}

        while queue:
            current_type, path = queue.pop(0)

            if len(path) >= max_length:
                continue

            # Find all agents that accept current_type
            agents = await self.registry.find_by_input_type(current_type)

            for agent in agents:
                new_path = path + [agent.id]

                # Check if we've reached target
                if self.lattice.is_subtype(agent.output_type, target_type):
                    return new_path

                # Continue search
                if agent.output_type not in visited:
                    visited.add(agent.output_type)
                    queue.append((agent.output_type, new_path))

        return None

    async def get_dependents(
        self,
        artifact_id: str,
        depth: int = 1
    ) -> list[GraphResult]:
        """Find artifacts that depend on the given one."""
        return await self.lineage.traverse(
            start=artifact_id,
            relationship="depended_on_by",
            max_depth=depth
        )

    async def get_ancestors(
        self,
        artifact_id: str,
        depth: int = -1  # -1 = unlimited
    ) -> list[GraphResult]:
        """Find the lineage ancestry of an artifact."""
        return await self.lineage.traverse(
            start=artifact_id,
            relationship="successor_to",
            max_depth=depth,
            direction="outbound"
        )

@dataclass
class GraphResult:
    """Result from graph search."""
    id: str
    relationship: str         # Type of relationship found
    path_length: int          # Distance from query origin
    path: list[str] | None    # Full path if relevant
    explanation: str | None
```

## Fusion Layer

The fusion layer combines results from all three brains:

```python
class QueryFusion:
    """Combine results from keyword, semantic, and graph search."""

    def __init__(
        self,
        keyword_brain: KeywordBrain,
        semantic_brain: SemanticBrain,
        graph_brain: GraphBrain
    ):
        self.keyword = keyword_brain
        self.semantic = semantic_brain
        self.graph = graph_brain

    async def search(
        self,
        query: str,
        constraints: list[str] | None = None,
        context: QueryContext | None = None,
        limit: int = 10
    ) -> QueryResponse:
        """
        Unified search across all three brains.

        Fusion strategy:
        1. Run all three searches in parallel
        2. Normalize scores to [0, 1]
        3. Apply weights based on query type
        4. Combine using reciprocal rank fusion
        5. Add serendipity suggestions
        """
        # Classify query type
        query_type = self._classify_query(query)

        # Run searches in parallel
        keyword_task = self.keyword.search(query, limit=limit*2)
        semantic_task = self.semantic.search(query, limit=limit*2)
        graph_task = self._graph_search_for_query(query, limit=limit*2)

        keyword_results, semantic_results, graph_results = await asyncio.gather(
            keyword_task, semantic_task, graph_task
        )

        # Apply constraints
        if constraints:
            keyword_results = self._filter_constraints(keyword_results, constraints)
            semantic_results = self._filter_constraints(semantic_results, constraints)
            graph_results = self._filter_constraints(graph_results, constraints)

        # Weight by query type
        weights = self._get_weights(query_type)

        # Reciprocal rank fusion
        fused = self._reciprocal_rank_fusion(
            [keyword_results, semantic_results, graph_results],
            weights
        )

        # Generate serendipity suggestions
        serendipity = await self._generate_serendipity(
            query, fused[:3], context
        )

        return QueryResponse(
            results=fused[:limit],
            serendipity=serendipity,
            query_interpretation=self._explain_interpretation(query, query_type)
        )

    def _classify_query(self, query: str) -> QueryType:
        """Determine which brain should be weighted highest."""
        # Exact name pattern
        if re.match(r'^[A-Z][a-zA-Z]*(_v\d+)?$', query):
            return QueryType.EXACT_NAME

        # Type signature pattern
        if '->' in query or 'input:' in query or 'output:' in query:
            return QueryType.TYPE_QUERY

        # Relationship pattern
        if any(kw in query.lower() for kw in ['depends', 'compatible', 'implements']):
            return QueryType.RELATIONSHIP

        # Default to semantic
        return QueryType.SEMANTIC_INTENT

    def _get_weights(self, query_type: QueryType) -> tuple[float, float, float]:
        """Get (keyword, semantic, graph) weights for query type."""
        return {
            QueryType.EXACT_NAME: (0.8, 0.1, 0.1),
            QueryType.TYPE_QUERY: (0.2, 0.2, 0.6),
            QueryType.RELATIONSHIP: (0.1, 0.2, 0.7),
            QueryType.SEMANTIC_INTENT: (0.2, 0.6, 0.2),
        }[query_type]

    def _reciprocal_rank_fusion(
        self,
        result_lists: list[list[Any]],
        weights: tuple[float, ...]
    ) -> list[FusedResult]:
        """
        Combine ranked lists using reciprocal rank fusion.

        RRF score = Σ (weight_i / (k + rank_i))
        where k = 60 (standard constant)
        """
        k = 60
        scores: dict[str, float] = {}
        sources: dict[str, list[str]] = {}

        for i, results in enumerate(result_lists):
            weight = weights[i]
            source_name = ["keyword", "semantic", "graph"][i]

            for rank, result in enumerate(results):
                id = result.id
                rrf_score = weight / (k + rank + 1)
                scores[id] = scores.get(id, 0) + rrf_score
                sources.setdefault(id, []).append(source_name)

        # Sort by combined score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [
            FusedResult(
                id=id,
                score=score,
                sources=sources[id]
            )
            for id, score in ranked
        ]

@dataclass
class QueryResponse:
    """Complete response from L-gent query."""
    results: list[FusedResult]
    serendipity: list[SerendipityItem]
    query_interpretation: str
    total_matches: int
    search_time_ms: float

@dataclass
class SerendipityItem:
    """Unexpected but potentially useful suggestion."""
    artifact_id: str
    reason: str        # Why this might be useful
    confidence: float  # How confident is the suggestion
```

## Dependency Resolution

Beyond search, L-gent resolves **type-level dependencies** at runtime:

```python
class DependencyResolver:
    """Resolve type requirements to concrete artifacts."""

    async def resolve(
        self,
        requirement: TypeRequirement,
        preferences: ResolutionPreferences | None = None
    ) -> CatalogEntry:
        """
        Find the best artifact satisfying a type requirement.

        Resolution strategy:
        1. Find all candidates matching type signature
        2. Filter by runtime constraints (status, health)
        3. Rank by preferences (recency, success_rate, usage)
        4. Return best match or raise DependencyError
        """
        # Find type-compatible candidates
        candidates = await self.lattice.find_satisfying(
            input_type=requirement.input_type,
            output_type=requirement.output_type,
            contracts=requirement.contracts
        )

        if not candidates:
            raise DependencyError(
                f"No artifact satisfies: {requirement.input_type} -> {requirement.output_type}"
            )

        # Filter by runtime constraints
        active_candidates = [
            c for c in candidates
            if c.status == Status.ACTIVE and c.success_rate > 0.5
        ]

        if not active_candidates:
            raise DependencyError(
                f"No healthy artifacts available for: {requirement}"
            )

        # Rank by preferences
        prefs = preferences or ResolutionPreferences()
        ranked = self._rank_candidates(active_candidates, prefs)

        return ranked[0]

    def _rank_candidates(
        self,
        candidates: list[CatalogEntry],
        prefs: ResolutionPreferences
    ) -> list[CatalogEntry]:
        """Rank candidates by preference weights."""

        def score(c: CatalogEntry) -> float:
            return (
                prefs.success_weight * c.success_rate +
                prefs.recency_weight * self._recency_score(c.last_used) +
                prefs.usage_weight * min(c.usage_count / 100, 1.0) +
                prefs.version_weight * self._version_score(c.version)
            )

        return sorted(candidates, key=score, reverse=True)

@dataclass
class TypeRequirement:
    """A type-level requirement for resolution."""
    input_type: str
    output_type: str
    contracts: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)

@dataclass
class ResolutionPreferences:
    """Weights for candidate ranking."""
    success_weight: float = 0.4
    recency_weight: float = 0.2
    usage_weight: float = 0.2
    version_weight: float = 0.2
```

## Usage Example: Complete Query Flow

```python
# User query
response = await l_gent.query(
    query="process financial PDFs and extract sentiment",
    constraints=["latency < 2s", "local execution"],
    context=QueryContext(
        user_history=["previously used Summarizer_v4"],
        current_pipeline=["DataSource", "???", "Database"]
    )
)

# Response:
# results:
#   1. FinancialPDFAnalyzer (0.95) - [semantic, graph]
#      "Extracts financial metrics from PDF documents"
#   2. PDFParser_v2 (0.82) - [keyword, semantic]
#      "General PDF text extraction"
#   3. SentimentEngine (0.78) - [semantic, graph]
#      "Sentiment analysis for text"
#
# serendipity:
#   - "Consider composing: PDFParser_v2 >> SentimentEngine
#      You've used Summarizer_v4 before - it composes well with both."
#
# query_interpretation:
#   "Understood as semantic intent for document processing + sentiment.
#    Applied constraints: latency (<2s filter), local (excluded cloud-only).
#    Graph search found type-compatible paths."

# Resolution for pipeline hole
resolved = await l_gent.resolve(
    TypeRequirement(
        input_type="PDF",
        output_type="SentimentScore",
        contracts=["deterministic"]
    )
)
# Returns: FinancialPDFAnalyzer (best match)
```

## Performance Optimization

### Caching Strategy

```python
class QueryCache:
    """Cache frequent queries and embeddings."""

    def __init__(self, ttl: int = 3600):
        self.query_cache = TTLCache(maxsize=1000, ttl=ttl)
        self.embedding_cache = TTLCache(maxsize=10000, ttl=ttl*24)

    async def get_or_search(
        self,
        query: str,
        search_fn: Callable
    ) -> QueryResponse:
        """Return cached result or execute search."""
        cache_key = self._hash_query(query)
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]

        result = await search_fn(query)
        self.query_cache[cache_key] = result
        return result
```

### Parallel Execution

All three brains execute in parallel:

```python
# Instead of sequential:
# keyword_results = await keyword.search(query)
# semantic_results = await semantic.search(query)
# graph_results = await graph.search(query)

# Execute in parallel:
keyword_results, semantic_results, graph_results = await asyncio.gather(
    keyword.search(query),
    semantic.search(query),
    graph.search(query)
)
```

## See Also

- [catalog.md](catalog.md) - The data structures being searched
- [lineage.md](lineage.md) - Graph relationships for traversal
- [lattice.md](lattice.md) - Type compatibility for resolution
- [../d-gents/vector.md](../d-gents/vector.md) - Vector storage backend
