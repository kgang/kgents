"""
Tests for L-gent Lineage Layer - Phase 3

Comprehensive test coverage for:
- Relationship creation and types
- Ancestor/descendant traversal
- Path finding
- Cycle detection (DAG property)
- Deprecation
- Serialization
- Convenience functions
"""

import pytest

from agents.l import (
    LineageGraph,
    Relationship,
    RelationshipType,
    LineageError,
    record_evolution,
    record_fork,
    record_dependency,
)


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def graph():
    """Create empty lineage graph."""
    return LineageGraph()


@pytest.fixture
async def simple_graph():
    """
    Create simple lineage graph:

    v1.0 → v2.0 → v3.0
    """
    g = LineageGraph()
    await g.add_relationship("v2.0", "v1.0", RelationshipType.SUCCESSOR_TO, "evolution")
    await g.add_relationship("v3.0", "v2.0", RelationshipType.SUCCESSOR_TO, "evolution")
    return g


@pytest.fixture
async def fork_graph():
    """
    Create fork graph:

              base_v1.0
             /          \
       fork_a_v1.0   fork_b_v1.0
    """
    g = LineageGraph()
    await g.add_relationship("fork_a_v1.0", "base_v1.0", RelationshipType.FORKED_FROM)
    await g.add_relationship("fork_b_v1.0", "base_v1.0", RelationshipType.FORKED_FROM)
    return g


@pytest.fixture
async def complex_graph():
    """
    Create complex graph with multiple relationship types:

    BaseScraper_v1.0
         |
         | (successor_to)
         ↓
    BaseScraper_v2.0
         |
         | (forked_from)
         ↓
    NewsScraper_v1.0 ──(depends_on)──> NetworkClient_v1.0
         |
         | (tested_by)
         ↓
    NewsScraperTest_v1.0
    """
    g = LineageGraph()

    # Evolution chain
    await g.add_relationship(
        "BaseScraper_v2.0",
        "BaseScraper_v1.0",
        RelationshipType.SUCCESSOR_TO,
    )

    # Fork
    await g.add_relationship(
        "NewsScraper_v1.0",
        "BaseScraper_v2.0",
        RelationshipType.FORKED_FROM,
    )

    # Dependency
    await g.add_relationship(
        "NewsScraper_v1.0",
        "NetworkClient_v1.0",
        RelationshipType.DEPENDS_ON,
    )

    # Test relationship
    await g.add_relationship(
        "NewsScraper_v1.0",
        "NewsScraperTest_v1.0",
        RelationshipType.TESTED_BY,
    )

    return g


# ─────────────────────────────────────────────────────────────
# Test: Basic Relationship Operations
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_add_relationship(graph):
    """Test adding a basic relationship."""
    rel = await graph.add_relationship(
        source_id="v2.0",
        target_id="v1.0",
        relationship_type=RelationshipType.SUCCESSOR_TO,
        created_by="test_user",
        context={"change": "performance improvement"},
    )

    assert rel.source_id == "v2.0"
    assert rel.target_id == "v1.0"
    assert rel.relationship_type == RelationshipType.SUCCESSOR_TO
    assert rel.created_by == "test_user"
    assert rel.context["change"] == "performance improvement"
    assert not rel.deprecated


@pytest.mark.asyncio
async def test_add_relationship_with_string_type(graph):
    """Test adding relationship with string relationship type."""
    rel = await graph.add_relationship(
        source_id="v2.0",
        target_id="v1.0",
        relationship_type="successor_to",  # String instead of enum
        created_by="test",
    )

    assert rel.relationship_type == RelationshipType.SUCCESSOR_TO


@pytest.mark.asyncio
async def test_has_edge(simple_graph):
    """Test checking if edge exists."""
    assert await simple_graph.has_edge("v2.0", "v1.0", RelationshipType.SUCCESSOR_TO)
    assert await simple_graph.has_edge("v3.0", "v2.0", "successor_to")  # String variant
    assert not await simple_graph.has_edge(
        "v1.0", "v2.0", RelationshipType.SUCCESSOR_TO
    )


@pytest.mark.asyncio
async def test_all_nodes(simple_graph):
    """Test getting all nodes."""
    nodes = await simple_graph.all_nodes()
    assert set(nodes) == {"v1.0", "v2.0", "v3.0"}


# ─────────────────────────────────────────────────────────────
# Test: Cycle Detection
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cycle_detection_simple(graph):
    """Test that adding a cycle is prevented."""
    # Create chain: A → B → C
    await graph.add_relationship("B", "A", RelationshipType.SUCCESSOR_TO)
    await graph.add_relationship("C", "B", RelationshipType.SUCCESSOR_TO)

    # Try to add C → A (would create cycle)
    with pytest.raises(LineageError, match="would create cycle"):
        await graph.add_relationship("A", "C", RelationshipType.SUCCESSOR_TO)


@pytest.mark.asyncio
async def test_cycle_detection_self_loop(graph):
    """Test that self-loops are prevented."""
    with pytest.raises(LineageError, match="would create cycle"):
        await graph.add_relationship("A", "A", RelationshipType.SUCCESSOR_TO)


@pytest.mark.asyncio
async def test_cycle_detection_transitive(graph):
    """Test cycle detection across multiple hops."""
    # Create chain: A → B → C → D
    await graph.add_relationship("B", "A", RelationshipType.SUCCESSOR_TO)
    await graph.add_relationship("C", "B", RelationshipType.SUCCESSOR_TO)
    await graph.add_relationship("D", "C", RelationshipType.SUCCESSOR_TO)

    # Try to add D → A (would create cycle through multiple hops)
    with pytest.raises(LineageError, match="would create cycle"):
        await graph.add_relationship("A", "D", RelationshipType.SUCCESSOR_TO)


# ─────────────────────────────────────────────────────────────
# Test: Querying Relationships
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_relationships_by_source(complex_graph):
    """Test filtering relationships by source."""
    rels = await complex_graph.get_relationships(source_id="NewsScraper_v1.0")
    assert len(rels) == 3  # forked_from, depends_on, tested_by

    rel_types = {r.relationship_type for r in rels}
    assert rel_types == {
        RelationshipType.FORKED_FROM,
        RelationshipType.DEPENDS_ON,
        RelationshipType.TESTED_BY,
    }


@pytest.mark.asyncio
async def test_get_relationships_by_target(complex_graph):
    """Test filtering relationships by target."""
    rels = await complex_graph.get_relationships(target_id="BaseScraper_v1.0")
    assert len(rels) == 1
    assert rels[0].relationship_type == RelationshipType.SUCCESSOR_TO
    assert rels[0].source_id == "BaseScraper_v2.0"


@pytest.mark.asyncio
async def test_get_relationships_by_type(complex_graph):
    """Test filtering relationships by type."""
    rels = await complex_graph.get_relationships(
        relationship_type=RelationshipType.FORKED_FROM
    )
    assert len(rels) == 1
    assert rels[0].source_id == "NewsScraper_v1.0"
    assert rels[0].target_id == "BaseScraper_v2.0"


@pytest.mark.asyncio
async def test_get_relationships_combined_filters(complex_graph):
    """Test combining multiple filters."""
    rels = await complex_graph.get_relationships(
        source_id="NewsScraper_v1.0",
        relationship_type=RelationshipType.DEPENDS_ON,
    )
    assert len(rels) == 1
    assert rels[0].target_id == "NetworkClient_v1.0"


# ─────────────────────────────────────────────────────────────
# Test: Ancestor/Descendant Traversal
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_ancestors_simple(simple_graph):
    """Test getting ancestors in a linear chain."""
    ancestors = await simple_graph.get_ancestors("v3.0")
    assert set(ancestors) == {"v2.0", "v1.0"}


@pytest.mark.asyncio
async def test_get_ancestors_with_type_filter(complex_graph):
    """Test getting ancestors filtered by relationship type."""
    ancestors = await complex_graph.get_ancestors(
        "NewsScraper_v1.0",
        relationship_type=RelationshipType.FORKED_FROM,
    )
    assert set(ancestors) == {"BaseScraper_v2.0"}  # Only forked_from, not successor_to


@pytest.mark.asyncio
async def test_get_ancestors_with_max_depth(simple_graph):
    """Test limiting ancestor traversal depth."""
    ancestors = await simple_graph.get_ancestors("v3.0", max_depth=1)
    assert ancestors == ["v2.0"]  # Only 1 hop


@pytest.mark.asyncio
async def test_get_descendants_simple(simple_graph):
    """Test getting descendants in a linear chain."""
    descendants = await simple_graph.get_descendants("v1.0")
    assert set(descendants) == {"v2.0", "v3.0"}


@pytest.mark.asyncio
async def test_get_descendants_fork(fork_graph):
    """Test getting descendants in a fork."""
    descendants = await fork_graph.get_descendants("base_v1.0")
    assert set(descendants) == {"fork_a_v1.0", "fork_b_v1.0"}


@pytest.mark.asyncio
async def test_get_descendants_with_max_depth(simple_graph):
    """Test limiting descendant traversal depth."""
    descendants = await simple_graph.get_descendants("v1.0", max_depth=1)
    assert descendants == ["v2.0"]  # Only 1 hop


# ─────────────────────────────────────────────────────────────
# Test: Path Finding
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_path_exists(simple_graph):
    """Test finding a path that exists."""
    path = await simple_graph.get_path("v1.0", "v3.0")
    assert path == ["v1.0", "v2.0", "v3.0"]


@pytest.mark.asyncio
async def test_get_path_not_exists(simple_graph):
    """Test path finding when no path exists."""
    path = await simple_graph.get_path("v3.0", "v1.0")  # Reversed direction
    assert path is None


@pytest.mark.asyncio
async def test_get_path_with_type_filter(complex_graph):
    """Test path finding with relationship type filter."""
    # Path exists via successor_to → forked_from
    path = await complex_graph.get_path("BaseScraper_v1.0", "NewsScraper_v1.0")
    assert path == ["BaseScraper_v1.0", "BaseScraper_v2.0", "NewsScraper_v1.0"]

    # But not if we filter only successor_to
    path_filtered = await complex_graph.get_path(
        "BaseScraper_v1.0",
        "NewsScraper_v1.0",
        relationship_type=RelationshipType.SUCCESSOR_TO,
    )
    assert path_filtered is None  # Can't reach via successor_to alone


@pytest.mark.asyncio
async def test_get_path_self(graph):
    """Test path from node to itself."""
    await graph.add_relationship("A", "B", RelationshipType.SUCCESSOR_TO)
    path = await graph.get_path("A", "A")
    assert path == ["A"]


# ─────────────────────────────────────────────────────────────
# Test: Deprecation
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_deprecate_relationship(simple_graph):
    """Test deprecating a relationship."""
    success = await simple_graph.deprecate_relationship(
        source_id="v2.0",
        target_id="v1.0",
        relationship_type=RelationshipType.SUCCESSOR_TO,
        reason="Outdated evolution path",
    )
    assert success

    # Check it's deprecated
    rels = await simple_graph.get_relationships(
        source_id="v2.0",
        include_deprecated=True,
    )
    assert len(rels) == 1
    assert rels[0].deprecated
    assert rels[0].deprecation_reason == "Outdated evolution path"
    assert rels[0].deprecated_at is not None


@pytest.mark.asyncio
async def test_deprecate_relationship_not_found(graph):
    """Test deprecating a non-existent relationship."""
    success = await graph.deprecate_relationship(
        source_id="A",
        target_id="B",
        relationship_type=RelationshipType.SUCCESSOR_TO,
        reason="test",
    )
    assert not success


@pytest.mark.asyncio
async def test_deprecated_relationships_excluded_by_default(simple_graph):
    """Test that deprecated relationships are excluded by default."""
    await simple_graph.deprecate_relationship(
        "v2.0", "v1.0", RelationshipType.SUCCESSOR_TO, "test"
    )

    # Without include_deprecated, should not appear
    rels = await simple_graph.get_relationships(source_id="v2.0")
    assert len(rels) == 0

    # With include_deprecated=True, should appear
    rels_with_deprecated = await simple_graph.get_relationships(
        source_id="v2.0",
        include_deprecated=True,
    )
    assert len(rels_with_deprecated) == 1


# ─────────────────────────────────────────────────────────────
# Test: Serialization
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_relationship_serialization():
    """Test Relationship to_dict/from_dict round-trip."""
    rel = Relationship(
        source_id="A",
        target_id="B",
        relationship_type=RelationshipType.SUCCESSOR_TO,
        created_by="test",
        context={"version": "2.0"},
    )

    data = rel.to_dict()
    rel_restored = Relationship.from_dict(data)

    assert rel_restored.source_id == rel.source_id
    assert rel_restored.target_id == rel.target_id
    assert rel_restored.relationship_type == rel.relationship_type
    assert rel_restored.created_by == rel.created_by
    assert rel_restored.context == rel.context


@pytest.mark.asyncio
async def test_lineage_graph_serialization(complex_graph):
    """Test LineageGraph to_dict/from_dict round-trip."""
    data = complex_graph.to_dict()

    assert "edges" in data
    assert "nodes" in data
    assert len(data["edges"]) == 4
    assert len(data["nodes"]) == 5

    # Restore from dict
    restored_graph = LineageGraph.from_dict(data)

    # Verify structure preserved
    assert len(await restored_graph.get_relationships()) == 4
    assert len(await restored_graph.all_nodes()) == 5

    # Verify specific edge preserved
    assert await restored_graph.has_edge(
        "NewsScraper_v1.0",
        "BaseScraper_v2.0",
        RelationshipType.FORKED_FROM,
    )


# ─────────────────────────────────────────────────────────────
# Test: Convenience Functions
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_record_evolution(graph):
    """Test record_evolution convenience function."""
    rel = await record_evolution(
        graph=graph,
        parent_id="v1.0",
        child_id="v2.0",
        created_by="evolution_agent",
        change_summary="Performance optimization",
    )

    assert rel.source_id == "v2.0"
    assert rel.target_id == "v1.0"
    assert rel.relationship_type == RelationshipType.SUCCESSOR_TO
    assert rel.created_by == "evolution_agent"
    assert rel.context["change_summary"] == "Performance optimization"


@pytest.mark.asyncio
async def test_record_fork(graph):
    """Test record_fork convenience function."""
    rel = await record_fork(
        graph=graph,
        parent_id="base_v1.0",
        fork_id="specialized_v1.0",
        created_by="forge_agent",
        reason="Specialized for news domain",
    )

    assert rel.source_id == "specialized_v1.0"
    assert rel.target_id == "base_v1.0"
    assert rel.relationship_type == RelationshipType.FORKED_FROM
    assert rel.created_by == "forge_agent"
    assert rel.context["reason"] == "Specialized for news domain"


@pytest.mark.asyncio
async def test_record_dependency(graph):
    """Test record_dependency convenience function."""
    rel = await record_dependency(
        graph=graph,
        dependent_id="agent_a",
        dependency_id="agent_b",
        version_constraint=">=2.0",
    )

    assert rel.source_id == "agent_a"
    assert rel.target_id == "agent_b"
    assert rel.relationship_type == RelationshipType.DEPENDS_ON
    assert rel.context["version_constraint"] == ">=2.0"


@pytest.mark.asyncio
async def test_record_dependency_no_version(graph):
    """Test record_dependency without version constraint."""
    rel = await record_dependency(
        graph=graph,
        dependent_id="agent_a",
        dependency_id="agent_b",
    )

    assert rel.source_id == "agent_a"
    assert rel.target_id == "agent_b"
    assert rel.relationship_type == RelationshipType.DEPENDS_ON
    assert rel.context == {}


# ─────────────────────────────────────────────────────────────
# Test: Complex Scenarios
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_multi_generation_evolution():
    """Test tracking multiple generations of evolution."""
    g = LineageGraph()

    # Create evolution chain: v1.0 → v2.0 → v3.0 → v4.0
    await record_evolution(g, "v1.0", "v2.0", "agent", "Added feature X")
    await record_evolution(g, "v2.0", "v3.0", "agent", "Fixed bug Y")
    await record_evolution(g, "v3.0", "v4.0", "agent", "Performance boost")

    # Check full ancestry from v4.0
    ancestors = await g.get_ancestors("v4.0", RelationshipType.SUCCESSOR_TO)
    assert set(ancestors) == {"v3.0", "v2.0", "v1.0"}

    # Check path from origin to latest
    path = await g.get_path("v1.0", "v4.0")
    assert path == ["v1.0", "v2.0", "v3.0", "v4.0"]


@pytest.mark.asyncio
async def test_dependency_tree():
    """Test building and querying dependency trees."""
    g = LineageGraph()

    # Create dependency tree:
    # app → [lib_a, lib_b]
    # lib_a → lib_core
    # lib_b → lib_core
    await record_dependency(g, "app", "lib_a")
    await record_dependency(g, "app", "lib_b")
    await record_dependency(g, "lib_a", "lib_core")
    await record_dependency(g, "lib_b", "lib_core")

    # Find all dependencies of app (direct + transitive)
    all_deps = await g.get_ancestors("app", RelationshipType.DEPENDS_ON)
    assert set(all_deps) == {"lib_a", "lib_b", "lib_core"}

    # Find direct dependencies only
    direct_deps = await g.get_ancestors("app", RelationshipType.DEPENDS_ON, max_depth=1)
    assert set(direct_deps) == {"lib_a", "lib_b"}


@pytest.mark.asyncio
async def test_impact_analysis():
    """Test finding impacted artifacts when deprecating."""
    g = LineageGraph()

    # Create chain: base → [agent_a, agent_b, agent_c]
    await record_dependency(g, "agent_a", "base")
    await record_dependency(g, "agent_b", "base")
    await record_dependency(g, "agent_c", "base")

    # Find what depends on 'base' (impact analysis)
    impacted = await g.get_descendants("base", RelationshipType.DEPENDS_ON)
    assert set(impacted) == {"agent_a", "agent_b", "agent_c"}
