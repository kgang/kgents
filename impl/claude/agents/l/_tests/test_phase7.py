"""
Tests for L-gent Phase 7: Three-Brain Hybrid Search

This test suite validates:
- GraphBrain: Relationship-based search
- QueryFusion: Combined keyword + semantic + graph search
- VectorSemanticBrain: VectorBackend integration
- Full three-brain workflow
"""

from __future__ import annotations

from datetime import datetime

import pytest

from agents.l import (
    # Vector backend
    CHROMADB_AVAILABLE,
    FAISS_AVAILABLE,
    CatalogEntry,
    EntityType,
    # Phase 7: Graph, Fusion, VectorSemantic
    GraphBrain,
    # Lineage & Lattice
    LineageGraph,
    QueryFusion,
    QueryType,
    # Core types
    Registry,
    RelationshipType,
    # Search components
    Search,
    SearchDirection,
    SemanticBrain,
    SimpleEmbedder,
    Status,
    TypeKind,
    TypeLattice,
    TypeNode,
    VectorSemanticBrain,
    create_graph_brain,
    create_query_fusion,
)

# Test fixtures


@pytest.fixture
async def sample_registry() -> Registry:
    """Create a registry with sample agents for testing."""
    registry = Registry()

    # Register sample agents with type signatures
    entries = [
        CatalogEntry(
            id="parser_1",
            entity_type=EntityType.AGENT,
            name="HTMLParser",
            description="Parse HTML documents into structured data",
            version="1.0",
            author="test",
            created_at=datetime.now(),
            status=Status.ACTIVE,
            input_type="RawHTML",
            output_type="StructuredData",
        ),
        CatalogEntry(
            id="cleaner_1",
            entity_type=EntityType.AGENT,
            name="TextCleaner",
            description="Clean and normalize text data",
            version="1.0",
            author="test",
            created_at=datetime.now(),
            status=Status.ACTIVE,
            input_type="StructuredData",
            output_type="CleanText",
        ),
        CatalogEntry(
            id="analyzer_1",
            entity_type=EntityType.AGENT,
            name="SentimentAnalyzer",
            description="Analyze sentiment of text",
            version="1.0",
            author="test",
            created_at=datetime.now(),
            status=Status.ACTIVE,
            input_type="CleanText",
            output_type="SentimentScore",
        ),
        CatalogEntry(
            id="summarizer_1",
            entity_type=EntityType.AGENT,
            name="DocumentSummarizer",
            description="Summarize documents into key points",
            version="1.0",
            author="test",
            created_at=datetime.now(),
            status=Status.ACTIVE,
            input_type="StructuredData",
            output_type="Summary",
        ),
    ]

    for entry in entries:
        await registry.register(entry)

    return registry


@pytest.fixture
async def sample_lineage() -> LineageGraph:
    """Create a lineage graph with sample relationships."""
    lineage = LineageGraph()

    # Add some evolution relationships
    await lineage.add_relationship(
        source_id="parser_1",
        target_id="parser_0",  # parser_1 is successor to parser_0
        relationship_type=RelationshipType.SUCCESSOR_TO,
    )

    # Add dependency
    await lineage.add_relationship(
        source_id="summarizer_1",
        target_id="cleaner_1",
        relationship_type=RelationshipType.DEPENDS_ON,
    )

    return lineage


@pytest.fixture
async def sample_lattice(sample_registry: Registry) -> TypeLattice:
    """Create a type lattice with sample types."""
    lattice = TypeLattice(sample_registry)

    # Register types
    types = [
        TypeNode(id="RawHTML", kind=TypeKind.PRIMITIVE, name="Raw HTML"),
        TypeNode(id="StructuredData", kind=TypeKind.RECORD, name="Structured Data"),
        TypeNode(id="CleanText", kind=TypeKind.PRIMITIVE, name="Clean Text"),
        TypeNode(id="SentimentScore", kind=TypeKind.PRIMITIVE, name="Sentiment Score"),
        TypeNode(id="Summary", kind=TypeKind.RECORD, name="Summary"),
    ]

    for type_node in types:
        lattice.register_type(type_node)

    return lattice


# GraphBrain tests


class TestGraphBrain:
    """Test GraphBrain functionality."""

    async def test_initialization(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test GraphBrain can be initialized."""
        brain = GraphBrain(sample_registry, sample_lineage, sample_lattice)
        assert brain.registry == sample_registry
        assert brain.lineage == sample_lineage
        assert brain.lattice == sample_lattice

    async def test_find_downstream_compatible(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test finding agents that can receive output."""
        brain = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        # Find what can receive HTMLParser's output (StructuredData)
        results = await brain.find_compatible("parser_1", SearchDirection.DOWNSTREAM)

        assert len(results) >= 1
        # Should find cleaner_1 and summarizer_1 (both accept StructuredData)
        ids = [r.id for r in results]
        assert "cleaner_1" in ids or "summarizer_1" in ids

    async def test_find_upstream_compatible(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test finding agents that can feed input."""
        brain = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        # Find what can feed into TextCleaner (needs StructuredData)
        results = await brain.find_compatible("cleaner_1", SearchDirection.UPSTREAM)

        assert len(results) >= 1
        ids = [r.id for r in results]
        assert "parser_1" in ids  # HTMLParser outputs StructuredData

    async def test_find_path(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test finding composition path from source to target type."""
        brain = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        # Find path from RawHTML to SentimentScore
        path = await brain.find_path("RawHTML", "SentimentScore", max_length=5)

        # Should find: parser_1 -> cleaner_1 -> analyzer_1
        assert path is not None
        assert "parser_1" in path
        assert "cleaner_1" in path
        assert "analyzer_1" in path

    async def test_get_dependents(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test finding dependents."""
        brain = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        # Find what depends on cleaner_1
        dependents = await brain.get_dependents("cleaner_1")

        # summarizer_1 depends on cleaner_1
        ids = [r.id for r in dependents]
        assert "summarizer_1" in ids

    async def test_get_ancestors(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test finding ancestors."""
        brain = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        # Find ancestors of parser_1
        ancestors = await brain.get_ancestors("parser_1")

        # Should handle gracefully (parser_0 not registered, but relationship exists)
        # In real usage, ancestor might not be in registry
        assert isinstance(ancestors, list)

    async def test_create_graph_brain(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test convenience function."""
        brain = await create_graph_brain(sample_registry, sample_lineage, sample_lattice)
        assert isinstance(brain, GraphBrain)


# QueryFusion tests


class TestQueryFusion:
    """Test QueryFusion functionality."""

    async def test_initialization(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test QueryFusion can be initialized."""
        keyword = Search(sample_registry)
        semantic = SemanticBrain(SimpleEmbedder())
        graph = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        fusion = QueryFusion(keyword, semantic, graph)
        assert fusion.keyword == keyword
        assert fusion.semantic == semantic
        assert fusion.graph == graph

    async def test_query_classification_exact_name(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test query type classification for exact names."""
        keyword = Search(sample_registry)
        semantic = SemanticBrain(SimpleEmbedder())
        graph = GraphBrain(sample_registry, sample_lineage, sample_lattice)
        fusion = QueryFusion(keyword, semantic, graph)

        # Exact name patterns
        assert fusion._classify_query("HTMLParser") == QueryType.EXACT_NAME
        assert fusion._classify_query("Summarizer_v2") == QueryType.EXACT_NAME

    async def test_query_classification_semantic(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test query type classification for semantic intent."""
        keyword = Search(sample_registry)
        semantic = SemanticBrain(SimpleEmbedder())
        graph = GraphBrain(sample_registry, sample_lineage, sample_lattice)
        fusion = QueryFusion(keyword, semantic, graph)

        # Semantic patterns
        assert fusion._classify_query("summarize documents") == QueryType.SEMANTIC_INTENT
        assert fusion._classify_query("analyze sentiment") == QueryType.SEMANTIC_INTENT

    async def test_query_classification_type_query(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test query type classification for type queries."""
        keyword = Search(sample_registry)
        semantic = SemanticBrain(SimpleEmbedder())
        graph = GraphBrain(sample_registry, sample_lineage, sample_lattice)
        fusion = QueryFusion(keyword, semantic, graph)

        # Type query patterns
        assert fusion._classify_query("RawHTML -> Summary") == QueryType.TYPE_QUERY
        assert fusion._classify_query("input:JSON output:Text") == QueryType.TYPE_QUERY

    async def test_query_classification_relationship(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test query type classification for relationships."""
        keyword = Search(sample_registry)
        semantic = SemanticBrain(SimpleEmbedder())
        graph = GraphBrain(sample_registry, sample_lineage, sample_lattice)
        fusion = QueryFusion(keyword, semantic, graph)

        # Relationship patterns
        assert fusion._classify_query("depends on cleaner") == QueryType.RELATIONSHIP
        assert fusion._classify_query("compatible with parser") == QueryType.RELATIONSHIP

    async def test_search_combines_results(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test that search combines results from all brains."""
        keyword = Search(sample_registry)
        semantic = SemanticBrain(SimpleEmbedder())
        entries_dict = {e.id: e for e in await sample_registry.list_entries()}
        await semantic.fit(entries_dict)
        graph = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        fusion = QueryFusion(keyword, semantic, graph)

        # Search for "parse HTML"
        response = await fusion.search("parse HTML", limit=5)

        # Should find results
        assert len(response.results) > 0
        assert response.query_type == QueryType.SEMANTIC_INTENT
        assert "parse" in response.query_interpretation.lower()

    async def test_create_query_fusion(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test convenience function."""
        keyword = Search(sample_registry)
        semantic = SemanticBrain(SimpleEmbedder())
        graph = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        fusion = await create_query_fusion(keyword, semantic, graph)
        assert isinstance(fusion, QueryFusion)


# VectorSemanticBrain tests


@pytest.mark.skipif(
    not (CHROMADB_AVAILABLE or FAISS_AVAILABLE), reason="No vector backend available"
)
class TestVectorSemanticBrain:
    """Test VectorSemanticBrain functionality."""

    async def test_add_and_search(self, sample_registry: Registry) -> None:
        """Test adding entries and searching."""
        from agents.l import create_vector_backend

        embedder = SimpleEmbedder(dimension=128)
        backend = create_vector_backend(dimension=128, backend_type="auto")
        brain = VectorSemanticBrain(embedder, backend)

        # Add entries
        entries = await sample_registry.list_entries()
        await brain.add_batch(entries)

        # Search
        results = await brain.search("parse HTML documents")

        assert len(results) > 0
        # Should find HTMLParser
        assert any("parse" in r.entry.description.lower() for r in results)

    async def test_remove_entry(self, sample_registry: Registry) -> None:
        """Test removing entries."""
        from agents.l import create_vector_backend

        embedder = SimpleEmbedder(dimension=128)
        backend = create_vector_backend(dimension=128, backend_type="auto")
        brain = VectorSemanticBrain(embedder, backend)

        # Add an entry
        all_entries = await sample_registry.list_entries()
        entry = all_entries[0]
        await brain.add_entry(entry)

        count_before = await brain.count()

        # Remove it
        await brain.remove_entry(entry.id)

        count_after = await brain.count()
        assert count_after < count_before


# Integration tests


class TestPhase7Integration:
    """Test full three-brain hybrid workflow."""

    async def test_full_workflow(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test complete three-brain search workflow."""
        # Setup all three brains
        keyword = Search(sample_registry)
        semantic = SemanticBrain(SimpleEmbedder())
        entries_dict = {e.id: e for e in await sample_registry.list_entries()}
        await semantic.fit(entries_dict)
        graph = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        # Create fusion
        fusion = QueryFusion(keyword, semantic, graph)

        # Search with semantic intent
        response = await fusion.search("analyze documents", limit=10)

        # Should have response structure (might be empty with limited test data)
        assert response is not None
        assert isinstance(response.results, list)
        # Should have interpretation
        assert len(response.query_interpretation) > 0
        # Should classify correctly
        assert response.query_type == QueryType.SEMANTIC_INTENT

    async def test_graph_brain_with_registry(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test GraphBrain integrated with Registry."""
        brain = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        # Find compatible agents
        results = await brain.find_compatible("parser_1", SearchDirection.BOTH)

        # Should find some compatible agents
        assert len(results) > 0
        # Each result should have valid entry
        for result in results:
            assert result.entry is not None
            assert await sample_registry.exists(result.entry.id)


# Edge cases


class TestPhase7EdgeCases:
    """Test edge cases and error handling."""

    async def test_empty_search(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test search with no results."""
        keyword = Search(sample_registry)
        semantic = SemanticBrain(SimpleEmbedder())
        graph = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        fusion = QueryFusion(keyword, semantic, graph)

        # Search for something that doesn't exist
        response = await fusion.search("quantum blockchain AI cryptocurrency", limit=10)

        # Should handle gracefully (no results is OK)
        assert response.results is not None
        assert isinstance(response.results, list)

    async def test_graph_brain_nonexistent_artifact(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test GraphBrain with nonexistent artifact."""
        brain = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        # Try to find compatible for nonexistent artifact
        results = await brain.find_compatible("nonexistent_id", SearchDirection.DOWNSTREAM)

        # Should return empty list
        assert results == []

    async def test_fusion_weights_sum_to_one(
        self,
        sample_registry: Registry,
        sample_lineage: LineageGraph,
        sample_lattice: TypeLattice,
    ) -> None:
        """Test that fusion weights always sum to 1.0."""
        keyword = Search(sample_registry)
        semantic = SemanticBrain(SimpleEmbedder())
        graph = GraphBrain(sample_registry, sample_lineage, sample_lattice)

        fusion = QueryFusion(keyword, semantic, graph)

        for query_type in QueryType:
            weights = fusion._get_weights(query_type)
            assert abs(sum(weights) - 1.0) < 0.001  # Floating point tolerance
