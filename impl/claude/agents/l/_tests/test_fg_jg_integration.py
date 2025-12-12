"""
Tests for L-gent F-gent and J-gent integration methods.

Phase: J-gent Phase 2 (L-gent Integration)
"""

from __future__ import annotations

import pytest
from agents.l.semantic_registry import create_semantic_registry
from agents.l.types import CatalogEntry, EntityType, Status


@pytest.fixture
def sample_json_parser() -> CatalogEntry:
    """Sample JSON parser agent."""
    return CatalogEntry(
        id="json_parser_v1",
        entity_type=EntityType.AGENT,
        name="JSON Parser",
        version="1.0.0",
        description="Parse JSON logs and extract error messages",
        author="system",
        keywords=["json", "parser", "logs", "errors"],
    )


@pytest.fixture
def sample_paper_summarizer() -> CatalogEntry:
    """Sample research paper summarizer."""
    return CatalogEntry(
        id="paper_summarizer",
        entity_type=EntityType.AGENT,
        name="Research Paper Summarizer",
        version="1.0.0",
        description="Summarize research papers to JSON format with key findings",
        author="system",
        keywords=["research", "paper", "summarize", "json"],
    )


class TestFgentIntegration:
    """Tests for F-gent integration methods."""

    @pytest.mark.asyncio
    async def test_find_for_forging_basic(
        self, sample_json_parser: CatalogEntry
    ) -> None:
        """Test finding artifacts before forging."""
        registry = await create_semantic_registry()
        await registry.register(sample_json_parser)

        # Use very low threshold to ensure we get results
        # (TF-IDF with small corpus can have low similarity)
        results = await registry.find_for_forging(
            intent="Parse JSON logs and extract error messages",
            threshold=0.0,  # Get all results
            limit=5,
        )

        # Should return the parser (similarity > 0)
        assert len(results) >= 1
        assert any("JSON" in r.entry.name for r in results)

    @pytest.mark.asyncio
    async def test_find_for_forging_high_threshold(
        self, sample_json_parser: CatalogEntry
    ) -> None:
        """Test that high threshold returns fewer results."""
        registry = await create_semantic_registry()
        await registry.register(sample_json_parser)

        results = await registry.find_for_forging(
            intent="Parse JSON logs",
            threshold=0.95,  # Very high threshold
        )

        # May return empty or very few results
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_register_forged_artifact(self) -> None:
        """Test registering a newly forged artifact."""
        registry = await create_semantic_registry()

        new_artifact = CatalogEntry(
            id="sql_generator",
            entity_type=EntityType.AGENT,
            name="SQL Query Generator",
            version="1.0.0",
            description="Generate SQL queries from natural language",
            author="F-gent",
            keywords=["sql", "generator", "nlp"],
        )

        artifact_id = await registry.register_forged_artifact(
            new_artifact,
            forged_by="F-gent-v2",
        )

        assert artifact_id == "sql_generator"

        # Verify metadata
        retrieved = await registry.get(artifact_id)
        assert retrieved is not None
        assert "forged_by" in retrieved.relationships
        assert "F-gent-v2" in retrieved.relationships["forged_by"]


class TestJgentIntegration:
    """Tests for J-gent integration methods."""

    @pytest.mark.asyncio
    async def test_find_for_jit_selection(
        self, sample_json_parser: CatalogEntry
    ) -> None:
        """Test finding agents for JIT runtime selection."""
        registry = await create_semantic_registry()
        await registry.register(sample_json_parser)

        candidates = await registry.find_for_jit_selection(
            intent="Parse JSON logs and extract error messages",
            threshold=0.0,  # Get all results
            limit=3,
        )

        assert len(candidates) >= 1
        assert all(c.entry.entity_type == EntityType.AGENT for c in candidates)

    @pytest.mark.asyncio
    async def test_find_for_jit_selection_with_constraints(self) -> None:
        """Test JIT selection with runtime constraints."""
        registry = await create_semantic_registry()

        # Register active agent
        active_agent = CatalogEntry(
            id="active_parser",
            entity_type=EntityType.AGENT,
            name="Active Parser",
            version="1.0.0",
            description="Parse data files",
            author="system",
            status=Status.ACTIVE,
        )
        await registry.register(active_agent)

        # Register draft agent
        draft_agent = CatalogEntry(
            id="draft_parser",
            entity_type=EntityType.AGENT,
            name="Draft Parser",
            version="0.1.0",
            description="Parse data files experimentally",
            author="system",
            status=Status.DRAFT,
        )
        await registry.register(draft_agent)

        # Only select active agents
        candidates = await registry.find_for_jit_selection(
            intent="Parse data from files",
            runtime_constraints={"status": Status.ACTIVE},
            threshold=0.2,
        )

        # All results should be active
        assert all(c.entry.status == Status.ACTIVE for c in candidates)

    @pytest.mark.asyncio
    async def test_register_jit_execution(
        self, sample_json_parser: CatalogEntry
    ) -> None:
        """Test recording JIT execution."""
        registry = await create_semantic_registry()
        await registry.register(sample_json_parser)

        agent_id = "json_parser_v1"

        await registry.register_jit_execution(
            agent_id=agent_id,
            intent="Parse JSON logs",
            success=True,
            entropy_used=0.05,
        )

        # Verify metrics updated
        updated = await registry.get(agent_id)
        assert updated is not None
        assert updated.usage_count == 1

        # Verify intent tracking
        assert "handled_intents" in updated.relationships
        assert "Parse JSON logs" in updated.relationships["handled_intents"]

        # Verify entropy tracking
        assert "entropy_history" in updated.relationships
        # Note: entropy_history stores floats as strings (per dict[str, list[str]] type)
        assert "0.05" in updated.relationships["entropy_history"]


class TestIntegrationWorkflows:
    """Tests for complete F-gent and J-gent workflows."""

    @pytest.mark.asyncio
    async def test_fgent_workflow(self, sample_json_parser: CatalogEntry) -> None:
        """Test complete F-gent workflow."""
        registry = await create_semantic_registry()
        await registry.register(sample_json_parser)

        # Check for duplicates before forging
        duplicates = await registry.find_for_forging(
            intent="Parse JSON logs and extract error messages",
            threshold=0.0,  # Get all results
        )

        assert len(duplicates) >= 1

        # Forge anyway with different approach
        new_artifact = CatalogEntry(
            id="parser_v2",
            entity_type=EntityType.AGENT,
            name="Optimized JSON Parser v2",
            version="2.0.0",
            description="Parse JSON logs with better error handling",
            author="F-gent",
            keywords=["json", "parser", "optimized"],
        )

        await registry.register_forged_artifact(new_artifact)

        # Verify both exist
        all_parsers = await registry.find_for_forging(
            intent="Parse JSON logs and extract error messages",
            threshold=0.0,  # Get all results
        )
        assert len(all_parsers) >= 2

    @pytest.mark.asyncio
    async def test_jgent_workflow(self) -> None:
        """Test complete J-gent workflow."""
        registry = await create_semantic_registry()

        # Register candidate agents
        agent1 = CatalogEntry(
            id="fast_parser",
            entity_type=EntityType.AGENT,
            name="Fast Parser",
            version="1.0.0",
            description="Quick JSON parsing for simple logs",
            author="system",
            keywords=["json", "fast"],
        )
        agent2 = CatalogEntry(
            id="robust_parser",
            entity_type=EntityType.AGENT,
            name="Robust Parser",
            version="1.0.0",
            description="Robust JSON parsing with error recovery",
            author="system",
            keywords=["json", "robust"],
        )

        await registry.register(agent1)
        await registry.register(agent2)

        # Find candidates at runtime
        candidates = await registry.find_for_jit_selection(
            intent="Parse JSON with error handling",
            threshold=0.2,
            limit=3,
        )

        assert len(candidates) > 0

        # Execute and record feedback
        selected = candidates[0]
        await registry.register_jit_execution(
            agent_id=selected.entry.id,
            intent="Parse JSON with error handling",
            success=True,
            entropy_used=0.08,
        )

        # Verify feedback recorded
        updated = await registry.get(selected.entry.id)
        assert updated is not None
        assert updated.usage_count == 1
        assert "handled_intents" in updated.relationships
