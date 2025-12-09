"""
Tests for L-gent search functionality.
"""

import pytest
import tempfile
import os

from agents.l.catalog import CatalogEntry, EntityType, Registry
from agents.l.search import Search, SearchStrategy


@pytest.fixture
def temp_storage():
    """Temporary storage file for testing."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
async def populated_registry(temp_storage):
    """Registry populated with test data."""
    registry = Registry(storage_path=temp_storage)

    # Create diverse test entries
    entries = [
        CatalogEntry(
            id="summarizer-1",
            entity_type=EntityType.AGENT,
            name="SummarizerAgent",
            version="1.0.0",
            description="Summarizes long documents into concise text",
            keywords=["summarize", "text", "nlp"],
            input_type="str",
            output_type="str",
            author="alice",
        ),
        CatalogEntry(
            id="translator-1",
            entity_type=EntityType.AGENT,
            name="TranslatorAgent",
            version="1.0.0",
            description="Translates text between languages",
            keywords=["translate", "language", "nlp"],
            input_type="str",
            output_type="str",
            author="bob",
        ),
        CatalogEntry(
            id="parser-1",
            entity_type=EntityType.AGENT,
            name="JSONParser",
            version="1.0.0",
            description="Parses JSON strings into Python dictionaries",
            keywords=["json", "parse", "data"],
            input_type="str",
            output_type="dict",
            author="alice",
        ),
        CatalogEntry(
            id="validator-1",
            entity_type=EntityType.AGENT,
            name="SchemaValidator",
            version="1.0.0",
            description="Validates data against JSON schema",
            keywords=["validate", "schema", "json"],
            input_type="dict",
            output_type="bool",
            author="charlie",
        ),
        CatalogEntry(
            id="contract-1",
            entity_type=EntityType.CONTRACT,
            name="NLPContract",
            version="1.0.0",
            description="Contract for natural language processing agents",
            keywords=["nlp", "contract", "interface"],
            author="alice",
        ),
    ]

    for entry in entries:
        await registry.register(entry)

    return registry


@pytest.mark.asyncio
async def test_keyword_search_by_name(populated_registry):
    """Test searching by agent name."""
    search = Search(populated_registry)

    results = await search.find("SummarizerAgent", strategy=SearchStrategy.KEYWORD)

    assert len(results) > 0
    assert results[0].entry.name == "SummarizerAgent"
    assert results[0].score > 0


@pytest.mark.asyncio
async def test_keyword_search_by_keyword(populated_registry):
    """Test searching by keywords."""
    search = Search(populated_registry)

    results = await search.find("json", strategy=SearchStrategy.KEYWORD)

    assert len(results) >= 2  # parser-1 and validator-1 both have "json"
    names = [r.entry.name for r in results]
    assert "JSONParser" in names or "SchemaValidator" in names


@pytest.mark.asyncio
async def test_keyword_search_by_description(populated_registry):
    """Test searching within descriptions."""
    search = Search(populated_registry)

    results = await search.find("translates", strategy=SearchStrategy.KEYWORD)

    assert len(results) > 0
    assert any(r.entry.name == "TranslatorAgent" for r in results)


@pytest.mark.asyncio
async def test_search_with_filters(populated_registry):
    """Test search with type filters."""
    search = Search(populated_registry)

    # Search only for agents
    results = await search.find(
        "nlp",
        strategy=SearchStrategy.KEYWORD,
        filters={"entity_type": EntityType.AGENT},
    )

    assert all(r.entry.entity_type == EntityType.AGENT for r in results)
    assert not any(r.entry.entity_type == EntityType.CONTRACT for r in results)


@pytest.mark.asyncio
async def test_search_with_author_filter(populated_registry):
    """Test filtering by author."""
    search = Search(populated_registry)

    results = await search.find(
        "agent", strategy=SearchStrategy.KEYWORD, filters={"author": "alice"}
    )

    assert all(r.entry.author == "alice" for r in results)


@pytest.mark.asyncio
async def test_search_result_ordering(populated_registry):
    """Test that results are ordered by relevance score."""
    search = Search(populated_registry)

    results = await search.find("json", strategy=SearchStrategy.KEYWORD)

    # Scores should be in descending order
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_search_limit(populated_registry):
    """Test search result limit."""
    search = Search(populated_registry)

    results = await search.find("agent", strategy=SearchStrategy.KEYWORD, limit=2)

    assert len(results) <= 2


@pytest.mark.asyncio
async def test_find_by_type_signature(populated_registry):
    """Test finding agents by type signature."""
    search = Search(populated_registry)

    # Find agents: str → str
    results = await search.find_by_type_signature(input_type="str", output_type="str")

    assert len(results) >= 2  # SummarizerAgent and TranslatorAgent
    assert all(r.entry.input_type == "str" for r in results)
    assert all(r.entry.output_type == "str" for r in results)


@pytest.mark.asyncio
async def test_find_by_type_signature_partial(populated_registry):
    """Test finding agents by partial type signature."""
    search = Search(populated_registry)

    # Find agents with any input, but dict output
    results = await search.find_by_type_signature(input_type=None, output_type="dict")

    assert len(results) >= 1  # JSONParser
    assert all(r.entry.output_type == "dict" for r in results)


@pytest.mark.asyncio
async def test_find_similar(populated_registry):
    """Test finding similar entries."""
    search = Search(populated_registry)

    # Find entries similar to SummarizerAgent
    results = await search.find_similar("summarizer-1", limit=3)

    # Should not include the original entry
    assert not any(r.entry.id == "summarizer-1" for r in results)

    # Should find TranslatorAgent (both have "nlp" keyword)
    assert any(r.entry.name == "TranslatorAgent" for r in results)


@pytest.mark.asyncio
async def test_search_no_results(populated_registry):
    """Test search with no matching results."""
    search = Search(populated_registry)

    results = await search.find("nonexistent", strategy=SearchStrategy.KEYWORD)

    assert len(results) == 0


@pytest.mark.asyncio
async def test_semantic_search_not_implemented(populated_registry):
    """Test that semantic search raises NotImplementedError."""
    search = Search(populated_registry)

    with pytest.raises(NotImplementedError):
        await search.find("query", strategy=SearchStrategy.SEMANTIC)


@pytest.mark.asyncio
async def test_graph_search_not_implemented(populated_registry):
    """Test that graph search raises NotImplementedError."""
    search = Search(populated_registry)

    with pytest.raises(NotImplementedError):
        await search.find("query", strategy=SearchStrategy.GRAPH)
