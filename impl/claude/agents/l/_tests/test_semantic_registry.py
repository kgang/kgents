"""
Tests for L-gent SemanticRegistry (Phase 5).

Test Coverage:
- SemanticRegistry initialization and fitting
- Auto-indexing on register/delete
- Semantic search (find_semantic)
- Hybrid search (find_hybrid)
- Integration with existing Registry features
"""

import pytest

from agents.l.registry import Registry
from agents.l.semantic_registry import SemanticRegistry, create_semantic_registry
from agents.l.types import CatalogEntry, EntityType, Status


class TestSemanticRegistry:
    """Test SemanticRegistry with auto-indexing."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test creating SemanticRegistry."""
        registry = SemanticRegistry()

        assert registry is not None
        assert registry.auto_index is True
        assert registry._fitted is False

    @pytest.mark.asyncio
    async def test_register_auto_indexes(self):
        """Test that register() auto-indexes entries."""
        registry = SemanticRegistry()

        entry = CatalogEntry(
            id="test1",
            entity_type=EntityType.AGENT,
            name="TestAgent",
            description="Test agent for semantic search",
            version="1.0.0",
            author="test",
        )

        await registry.register(entry)

        # Should be fitted after first registration
        assert registry._fitted is True

        # Should be searchable semantically
        results = await registry.find_semantic("test agent", threshold=0.0, limit=5)
        assert len(results) > 0
        assert results[0].entry.id == "test1"

    @pytest.mark.asyncio
    async def test_delete_removes_from_index(self):
        """Test that delete() removes entries from semantic index."""
        registry = SemanticRegistry()

        entry = CatalogEntry(
            id="test1",
            entity_type=EntityType.AGENT,
            name="ToDelete",
            description="This will be deleted",
            version="1.0.0",
            author="test",
        )

        await registry.register(entry)
        await registry.delete("test1")

        # Should not be found in semantic search
        results = await registry.find_semantic("ToDelete", threshold=0.0, limit=5)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_find_semantic_with_filters(self):
        """Test semantic search with entity type filtering."""
        registry = SemanticRegistry()

        # Register an agent
        await registry.register(
            CatalogEntry(
                id="agent1",
                entity_type=EntityType.AGENT,
                name="TextProcessor",
                description="Process text documents",
                version="1.0.0",
                author="test",
            )
        )

        # Register a contract
        await registry.register(
            CatalogEntry(
                id="contract1",
                entity_type=EntityType.CONTRACT,
                name="TextContract",
                description="Contract for text processing",
                version="1.0.0",
                author="test",
            )
        )

        # Search only for agents
        results = await registry.find_semantic(
            "text processing",
            filters={"entity_type": EntityType.AGENT},
            limit=5,
        )

        assert all(r.entry.entity_type == EntityType.AGENT for r in results)

    @pytest.mark.asyncio
    async def test_find_semantic_with_threshold(self):
        """Test semantic search threshold filtering."""
        registry = SemanticRegistry()

        await registry.register(
            CatalogEntry(
                id="test1",
                entity_type=EntityType.AGENT,
                name="Analyzer",
                description="Analyze data patterns",
                version="1.0.0",
                author="test",
            )
        )

        # High threshold - fewer results
        results_high = await registry.find_semantic(
            "pattern recognition", threshold=0.8, limit=10
        )

        # Low threshold - more results
        results_low = await registry.find_semantic(
            "pattern recognition", threshold=0.1, limit=10
        )

        assert len(results_high) <= len(results_low)

    @pytest.mark.asyncio
    async def test_hybrid_search_combines_results(self):
        """Test that hybrid search combines keyword + semantic."""
        registry = SemanticRegistry()

        # Register entries
        await registry.register(
            CatalogEntry(
                id="pdf_parser",
                entity_type=EntityType.AGENT,
                name="PDFParser",
                description="Extract text from PDF documents",
                version="1.0.0",
                author="test",
            )
        )

        await registry.register(
            CatalogEntry(
                id="doc_analyzer",
                entity_type=EntityType.AGENT,
                name="DocumentAnalyzer",
                description="Analyze document structure and content",
                version="1.0.0",
                author="test",
            )
        )

        # Hybrid search
        results = await registry.find_hybrid("PDF analysis", limit=5)

        # Should find both (PDFParser via keyword, both via semantic)
        assert len(results) > 0
        assert all(r.match_type == "hybrid" for r in results)

    @pytest.mark.asyncio
    async def test_hybrid_search_weights(self):
        """Test hybrid search weighting."""
        registry = SemanticRegistry()

        await registry.register(
            CatalogEntry(
                id="exact_match",
                entity_type=EntityType.AGENT,
                name="ExactMatchAgent",
                description="Different description",
                version="1.0.0",
                author="test",
            )
        )

        await registry.register(
            CatalogEntry(
                id="semantic_match",
                entity_type=EntityType.AGENT,
                name="SemanticAgent",
                description="This is about exact matching algorithms",
                version="1.0.0",
                author="test",
            )
        )

        # Keyword-heavy search (favor exact name match)
        keyword_heavy = await registry.find_hybrid(
            "ExactMatch", semantic_weight=0.2, limit=5
        )

        # Semantic-heavy search (favor description match)
        semantic_heavy = await registry.find_hybrid(
            "exact matching", semantic_weight=0.8, limit=5
        )

        # Keyword-heavy should rank ExactMatchAgent higher
        if len(keyword_heavy) > 0:
            assert keyword_heavy[0].entry.id == "exact_match"

    @pytest.mark.asyncio
    async def test_hybrid_search_invalid_weight(self):
        """Test that invalid weights raise ValueError."""
        registry = SemanticRegistry()

        with pytest.raises(ValueError, match="semantic_weight"):
            await registry.find_hybrid("query", semantic_weight=1.5)

        with pytest.raises(ValueError, match="semantic_weight"):
            await registry.find_hybrid("query", semantic_weight=-0.1)

    @pytest.mark.asyncio
    async def test_manual_fit(self):
        """Test manual fitting when auto_index=False."""
        registry = SemanticRegistry(auto_index=False)

        # Register without auto-indexing
        await registry.register(
            CatalogEntry(
                id="test1",
                entity_type=EntityType.AGENT,
                name="ManualTest",
                description="Test manual fitting",
                version="1.0.0",
                author="test",
            )
        )

        # Manual fit
        await registry.fit()

        assert registry._fitted is True

        # Should now be searchable
        results = await registry.find_semantic("manual", threshold=0.0, limit=5)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_maintains_registry_functionality(self):
        """Test that SemanticRegistry maintains parent Registry features."""
        registry = SemanticRegistry()

        entry = CatalogEntry(
            id="test1",
            entity_type=EntityType.AGENT,
            name="TestAgent",
            description="Test description",
            version="1.0.0",
            author="test",
        )

        # Register
        entry_id = await registry.register(entry)
        assert entry_id == "test1"

        # Get
        retrieved = await registry.get("test1")
        assert retrieved is not None
        assert retrieved.name == "TestAgent"

        # Exists
        assert await registry.exists("test1") is True

        # List
        entries = await registry.list(entity_type=EntityType.AGENT)
        assert len(entries) > 0

        # Find (keyword search)
        keyword_results = await registry.find(query="Test", limit=5)
        assert len(keyword_results) > 0

        # Update usage
        await registry.update_usage("test1", success=True)
        updated = await registry.get("test1")
        assert updated.usage_count == 1

        # Deprecate
        await registry.deprecate("test1", reason="outdated")
        deprecated = await registry.get("test1")
        assert deprecated.status == Status.DEPRECATED

    @pytest.mark.asyncio
    async def test_incremental_indexing(self):
        """Test incremental indexing on multiple registrations."""
        registry = SemanticRegistry()

        # Register first entry
        await registry.register(
            CatalogEntry(
                id="first",
                entity_type=EntityType.AGENT,
                name="First",
                description="First entry",
                version="1.0.0",
                author="test",
            )
        )

        # Register second entry (should incrementally index)
        await registry.register(
            CatalogEntry(
                id="second",
                entity_type=EntityType.AGENT,
                name="Second",
                description="Second entry",
                version="1.0.0",
                author="test",
            )
        )

        # Both should be searchable
        results = await registry.find_semantic("entry", threshold=0.0, limit=10)
        assert len(results) == 2


class TestSemanticRegistryConvenience:
    """Test convenience functions."""

    @pytest.mark.asyncio
    async def test_create_semantic_registry(self):
        """Test convenience function for creating registry."""
        registry = await create_semantic_registry()

        assert isinstance(registry, SemanticRegistry)

    @pytest.mark.asyncio
    async def test_create_with_existing_catalog(self):
        """Test creating registry with existing catalog."""
        # Create first registry
        registry1 = SemanticRegistry()
        await registry1.register(
            CatalogEntry(
                id="test1",
                entity_type=EntityType.AGENT,
                name="ExistingAgent",
                description="Pre-existing",
                version="1.0.0",
                author="test",
            )
        )

        # Export catalog
        catalog_dict = registry1.to_dict()

        # Create new registry from catalog
        registry2 = await create_semantic_registry(
            catalog=Registry.from_dict(catalog_dict).catalog
        )

        # Should be fitted and searchable
        results = await registry2.find_semantic("existing", threshold=0.0, limit=5)
        assert len(results) > 0
        assert results[0].entry.id == "test1"


class TestSemanticRegistryIntegration:
    """Test integration scenarios."""

    @pytest.mark.asyncio
    async def test_real_world_agent_discovery(self):
        """Test realistic agent discovery scenario."""
        registry = SemanticRegistry()

        # Register various agents
        agents = [
            CatalogEntry(
                id="pdf_extractor",
                entity_type=EntityType.AGENT,
                name="PDFExtractor",
                description="Extract text and metadata from PDF files",
                version="1.0.0",
                author="F-gent",
                input_type="PDF",
                output_type="Text",
            ),
            CatalogEntry(
                id="sentiment_analyzer",
                entity_type=EntityType.AGENT,
                name="SentimentAnalyzer",
                description="Analyze sentiment and emotion in text",
                version="2.0.0",
                author="F-gent",
                input_type="Text",
                output_type="SentimentScore",
            ),
            CatalogEntry(
                id="document_summarizer",
                entity_type=EntityType.AGENT,
                name="DocumentSummarizer",
                description="Create concise summaries of long documents",
                version="1.5.0",
                author="F-gent",
                input_type="Text",
                output_type="Summary",
            ),
        ]

        for agent in agents:
            await registry.register(agent)

        # User intent: "I want to summarize PDF documents"
        # Hybrid search should find relevant agents
        results = await registry.find_hybrid(
            "summarize PDF documents", semantic_weight=0.7, limit=5
        )

        # Should find both PDFExtractor and DocumentSummarizer
        found_ids = {r.entry.id for r in results}
        assert "pdf_extractor" in found_ids
        assert "document_summarizer" in found_ids

    @pytest.mark.asyncio
    async def test_tongue_discovery(self):
        """Test discovering tongues by domain."""
        registry = SemanticRegistry()

        # Register tongues
        await registry.register(
            CatalogEntry(
                id="calendar_tongue",
                entity_type=EntityType.TONGUE,
                name="CalendarTongue",
                description="DSL for calendar operations",
                version="1.0.0",
                author="G-gent",
                tongue_domain="calendar scheduling",
            )
        )

        await registry.register(
            CatalogEntry(
                id="email_tongue",
                entity_type=EntityType.TONGUE,
                name="EmailTongue",
                description="DSL for email management",
                version="1.0.0",
                author="G-gent",
                tongue_domain="email communication",
            )
        )

        # Search by domain
        results = await registry.find_semantic(
            "schedule appointments",
            filters={"entity_type": EntityType.TONGUE},
            threshold=0.0,
            limit=5,
        )

        # Should find calendar tongue
        assert any(r.entry.id == "calendar_tongue" for r in results)
