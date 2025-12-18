"""
Tests for F-gent + L-gent integration (T1.1: Search before forge).

Tests the cross-pollination workflow:
- Search L-gent registry before forging
- Register forged artifacts in catalog
- Prevent duplicate creation (Curated principle)
"""

from __future__ import annotations

import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest

from agents.f.contract import Contract
from agents.f.forge_with_search import (
    ForgeDecision,
    forge_with_registration,
    register_forged_artifact,
    search_before_forge,
)
from agents.f.intent import Dependency, DependencyType, Intent
from agents.l.catalog import CatalogEntry, EntityType, Registry, Status


@pytest.fixture
def temp_registry() -> Generator[Registry, None, None]:
    """Create temporary registry for testing."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        registry = Registry(f.name)
        yield registry
        # Cleanup
        Path(f.name).unlink(missing_ok=True)


@pytest.fixture
async def populated_registry(temp_registry: Registry) -> AsyncGenerator[Registry, None]:
    """Registry with some pre-existing artifacts."""
    # Register a summarizer agent
    await temp_registry.register(
        CatalogEntry(
            id="PaperSummarizer",
            entity_type=EntityType.AGENT,
            name="PaperSummarizer",
            version="1.0.0",
            description="Summarize academic papers to concise abstracts",
            author="alice",
            keywords=["Summarize content", "Format output"],
            input_type="str",
            output_type="str",
            contracts_implemented=["Agent[str, str]"],
            status=Status.ACTIVE,
        )
    )

    # Register a weather agent
    await temp_registry.register(
        CatalogEntry(
            id="WeatherAgent",
            entity_type=EntityType.AGENT,
            name="WeatherAgent",
            version="1.0.0",
            description="Fetch weather data from API",
            author="bob",
            keywords=["Fetch data", "Query sources"],
            input_type="str",
            output_type="dict",
            contracts_implemented=["Agent[str, dict]"],
            relationships={"depends_on": ["WeatherAPI"]},
            status=Status.ACTIVE,
        )
    )

    yield temp_registry


# ============================================================================
# Test 1: Search before forge - No matches (proceed with forge)
# ============================================================================


@pytest.mark.asyncio
async def test_search_before_forge_no_matches(temp_registry: Registry) -> None:
    """When no similar artifacts exist, recommend forging new."""
    result = await search_before_forge(
        intent_text="Create an agent that validates email addresses",
        registry=temp_registry,  # type: ignore[arg-type]
        similarity_threshold=0.9,
    )

    assert result.decision == ForgeDecision.FORGE_NEW
    assert len(result.similar_artifacts) == 0
    assert "No similar artifacts found" in result.recommendation
    assert result.threshold_used == 0.9


# ============================================================================
# Test 2: Search before forge - Exact match found (recommend reuse)
# ============================================================================


@pytest.mark.asyncio
async def test_search_before_forge_exact_match(populated_registry: Registry) -> None:
    """When similar artifact exists, recommend reuse."""
    result = await search_before_forge(
        intent_text="Create an agent that summarizes papers",
        registry=populated_registry,  # type: ignore[arg-type]
        similarity_threshold=0.1,  # Low threshold for keyword matching
    )

    # Should find PaperSummarizer (score ~0.2 from description match)
    assert len(result.similar_artifacts) > 0
    assert any(r.entry.name == "PaperSummarizer" for r in result.similar_artifacts)
    assert "PaperSummarizer" in result.recommendation
    assert "reusing" in result.recommendation.lower() or "similar" in result.recommendation.lower()


# ============================================================================
# Test 3: Search before forge - Partial match (keyword overlap)
# ============================================================================


@pytest.mark.asyncio
async def test_search_before_forge_partial_match(populated_registry: Registry) -> None:
    """Keyword overlap should surface related artifacts."""
    result = await search_before_forge(
        intent_text="Create an agent that fetches weather forecasts",
        registry=populated_registry,  # type: ignore[arg-type]
        similarity_threshold=0.1,  # Low threshold for keyword matching
    )

    # Should find WeatherAgent based on "fetch" and "weather" in description
    assert len(result.similar_artifacts) > 0
    matches = [r.entry.name for r in result.similar_artifacts]
    assert "WeatherAgent" in matches


# ============================================================================
# Test 4: Forge with registration - Full workflow
# ============================================================================


@pytest.mark.asyncio
async def test_forge_with_registration_new_artifact(temp_registry: Registry) -> None:
    """Complete workflow: search → forge → register."""
    contract, search_result = await forge_with_registration(
        intent_text="Create an agent that validates JSON schemas",
        agent_name="JSONValidator",
        registry=temp_registry,  # type: ignore[arg-type]
        author="charlie",
        similarity_threshold=0.9,
    )

    # Check forge result
    assert contract.agent_name == "JSONValidator"
    assert "JSON" in contract.semantic_intent or "validate" in contract.semantic_intent.lower()

    # Check search result (should be FORGE_NEW since catalog was empty)
    assert search_result.decision == ForgeDecision.FORGE_NEW

    # Check registration
    entries = await temp_registry.list_all()
    assert len(entries) == 1
    assert entries[0].name == "JSONValidator"
    assert entries[0].entity_type == EntityType.CONTRACT
    assert entries[0].status == Status.DRAFT


# ============================================================================
# Test 5: Forge with registration - Duplicate detection
# ============================================================================


@pytest.mark.asyncio
async def test_forge_with_registration_duplicate_detection(
    populated_registry: Registry,
) -> None:
    """Attempting to forge similar artifact should trigger recommendation."""
    contract, search_result = await forge_with_registration(
        intent_text="Create an agent that summarizes research papers",
        agent_name="ResearchSummarizer",
        registry=populated_registry,  # type: ignore[arg-type]
        similarity_threshold=0.1,  # Low threshold for keyword matching
    )

    # Should detect similarity to PaperSummarizer (score ~0.4 from keywords + description)
    assert len(search_result.similar_artifacts) > 0
    assert any(r.entry.name == "PaperSummarizer" for r in search_result.similar_artifacts)

    # Contract should still be created (decision is a recommendation, not blocker)
    assert contract.agent_name == "ResearchSummarizer"


# ============================================================================
# Test 6: Register forged artifact - Contract to CatalogEntry
# ============================================================================


@pytest.mark.asyncio
async def test_register_forged_artifact(temp_registry: Registry) -> None:
    """Test standalone registration of a contract."""
    contract = Contract(
        agent_name="DataParser",
        input_type="str",
        output_type="dict",
        semantic_intent="Parse CSV data into structured dictionary",
        raw_intent=Intent(
            purpose="Parse CSV data",
            behavior=["Parse data", "Transform data"],
            constraints=["Type safety"],
            dependencies=[
                Dependency(
                    name="csv",
                    type=DependencyType.LIBRARY,
                    description="Python CSV library",
                )
            ],
        ),
    )

    entry = await register_forged_artifact(
        contract=contract,
        agent_name="DataParser",
        registry=temp_registry,  # type: ignore[arg-type]
        author="dave",
        keywords=["parsing", "CSV"],
    )

    # Check entry
    assert entry.name == "DataParser"
    assert entry.entity_type == EntityType.CONTRACT
    assert entry.input_type == "str"
    assert entry.output_type == "dict"
    assert "parsing" in entry.keywords
    assert "csv" in entry.relationships.get("depends_on", [])
    assert entry.status == Status.DRAFT

    # Check persistence
    retrieved = await temp_registry.get("DataParser")
    assert retrieved is not None
    assert retrieved.name == "DataParser"


# ============================================================================
# Test 7: Register artifact with no keywords (extract from invariants)
# ============================================================================


@pytest.mark.asyncio
async def test_register_artifact_auto_keywords(temp_registry: Registry) -> None:
    """Keywords should default to invariant descriptions."""
    from agents.f.contract import Invariant

    contract = Contract(
        agent_name="IdempotentAgent",
        input_type="int",
        output_type="int",
        invariants=[
            Invariant(
                description="Idempotency",
                property="f(f(x)) == f(x)",
                category="behavioral",
            ),
            Invariant(
                description="Type safety",
                property="isinstance(output, int)",
                category="structural",
            ),
        ],
    )

    entry = await register_forged_artifact(
        contract=contract,
        agent_name="IdempotentAgent",
        registry=temp_registry,  # type: ignore[arg-type]
        author="eve",
        keywords=None,  # Should extract from invariants
    )

    # Keywords should come from invariants
    assert "Idempotency" in entry.keywords
    assert "Type safety" in entry.keywords


# ============================================================================
# Test 8: Similarity threshold behavior
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "threshold,expected_matches",
    [
        (0.0, True),  # Very low threshold should find matches
        (0.2, True),  # Low threshold should find keyword matches (score ~0.4)
        (0.95, False),  # Very high threshold should filter most matches
    ],
)
async def test_similarity_threshold_tuning(
    populated_registry: Registry, threshold: float, expected_matches: bool
) -> None:
    """Test how similarity threshold affects match detection."""
    result = await search_before_forge(
        intent_text="Summarize content from papers",
        registry=populated_registry,  # type: ignore[arg-type]
        similarity_threshold=threshold,
    )

    if expected_matches:
        # Should find PaperSummarizer with lower thresholds
        assert len(result.similar_artifacts) > 0
    else:
        # High threshold should filter out keyword matches
        # (since we don't have semantic embeddings yet)
        assert len(result.similar_artifacts) == 0


# ============================================================================
# Test 9: Cross-pollination principle validation (Curated)
# ============================================================================


@pytest.mark.asyncio
async def test_curated_principle_duplicate_prevention(
    populated_registry: Registry,
) -> None:
    """Verify that search-before-forge embodies Curated principle."""
    # Attempt to forge duplicate weather agent
    result = await search_before_forge(
        intent_text="Create an agent that queries weather APIs",
        registry=populated_registry,  # type: ignore[arg-type]
        similarity_threshold=0.1,  # Low threshold for keyword matching
    )

    # Should find existing WeatherAgent (score ~0.2 from description)
    assert len(result.similar_artifacts) > 0
    weather_matches = [r for r in result.similar_artifacts if r.entry.name == "WeatherAgent"]
    assert len(weather_matches) > 0

    # Recommendation should encourage reuse (Curated)
    assert "reuse" in result.recommendation.lower() or "similar" in result.recommendation.lower()


# ============================================================================
# Test 10: Type signature compatibility (L-gent lattice preview)
# ============================================================================


@pytest.mark.asyncio
async def test_type_signature_consideration(temp_registry: Registry) -> None:
    """Test that type signatures are preserved in registration."""
    # Register agent with specific type signature
    contract, _ = await forge_with_registration(
        intent_text="Parse JSON string to dictionary",
        agent_name="JSONParser",
        registry=temp_registry,  # type: ignore[arg-type]
    )

    # Retrieve and check type signature
    entry = await temp_registry.get("JSONParser")
    assert entry is not None

    # Type signature should be captured
    # (Future: L-gent lattice will use this for composition planning)
    assert entry.input_type is not None
    assert entry.output_type is not None
    assert "str" in entry.input_type.lower() or "any" in entry.input_type.lower()


# ============================================================================
# Test 11: Integration with existing F-gent components
# ============================================================================


@pytest.mark.asyncio
async def test_integration_with_intent_parser(temp_registry: Registry) -> None:
    """Verify integration with F-gent intent parsing."""
    # Complex intent with dependencies and constraints
    complex_intent = """
    Create an agent that fetches data from REST APIs and validates the response.
    Must be idempotent and handle errors gracefully.
    Output should be JSON format.
    """

    contract, search_result = await forge_with_registration(
        intent_text=complex_intent,
        agent_name="APIValidator",
        registry=temp_registry,  # type: ignore[arg-type]
        author="frank",
    )

    # Check that intent parsing worked
    assert contract.raw_intent is not None
    assert len(contract.raw_intent.dependencies) > 0
    assert any(dep.type == DependencyType.REST_API for dep in contract.raw_intent.dependencies)

    # Check that invariants were extracted
    assert len(contract.invariants) > 0

    # Check that entry was registered with dependencies
    entry = await temp_registry.get("APIValidator")
    assert entry is not None
    assert len(entry.relationships.get("depends_on", [])) > 0
