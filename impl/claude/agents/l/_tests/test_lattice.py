"""
Tests for L-gent Lattice Layer (Phase 4)

Tests type compatibility, composition verification, and composition planning.

Lattice Laws:
- Reflexivity: A ≤ A
- Transitivity: A ≤ B and B ≤ C implies A ≤ C
- Antisymmetry: A ≤ B and B ≤ A implies A = B (prevents cycles)

Meet/Join Laws:
- Commutativity: meet(A,B) = meet(B,A), join(A,B) = join(B,A)
"""

from __future__ import annotations

import pytest
from agents.l.lattice import (
    SubtypeEdge,
    TypeKind,
    TypeLattice,
    TypeNode,
    create_lattice,
)
from agents.l.registry import Registry
from agents.l.types import CatalogEntry, EntityType

# registry and lattice fixtures imported from conftest.py


# ─────────────────────────────────────────────────────────────
# TypeNode Tests
# ─────────────────────────────────────────────────────────────


def test_type_node_creation() -> None:
    """Test creating a TypeNode."""
    node = TypeNode(
        id="UserRecord",
        kind=TypeKind.RECORD,
        name="User Record",
        fields={"name": "str", "age": "int"},
    )

    assert node.id == "UserRecord"
    assert node.kind == TypeKind.RECORD
    assert node.fields == {"name": "str", "age": "int"}


def test_type_node_serialization() -> None:
    """Test TypeNode to_dict/from_dict round-trip."""
    node = TypeNode(
        id="ListInt",
        kind=TypeKind.CONTAINER,
        name="List of integers",
        element_type="int",
    )

    data = node.to_dict()
    restored = TypeNode.from_dict(data)

    assert restored.id == node.id
    assert restored.kind == node.kind
    assert restored.element_type == node.element_type


# ─────────────────────────────────────────────────────────────
# Lattice Initialization Tests
# ─────────────────────────────────────────────────────────────


def test_lattice_has_builtin_types(lattice: TypeLattice) -> None:
    """Test that lattice initializes with built-in types."""
    assert "Any" in lattice.types
    assert "Never" in lattice.types
    assert "str" in lattice.types
    assert "int" in lattice.types


def test_builtin_types_have_edges_to_any(lattice: TypeLattice) -> None:
    """Test that primitives are subtypes of Any."""
    assert lattice.is_subtype("str", "Any")
    assert lattice.is_subtype("int", "Any")
    assert lattice.is_subtype("float", "Any")


def test_never_is_subtype_of_all(lattice: TypeLattice) -> None:
    """Test that Never is subtype of all types."""
    assert lattice.is_subtype("Never", "str")
    assert lattice.is_subtype("Never", "int")
    assert lattice.is_subtype("Never", "Any")


# ─────────────────────────────────────────────────────────────
# Subtype Checking Tests (Law Verification)
# ─────────────────────────────────────────────────────────────


@pytest.mark.law("lattice")
class TestSubtypeLaws:
    """Tests for lattice subtype ordering laws."""

    def test_is_subtype_reflexive(self, lattice: TypeLattice) -> None:
        """Test reflexivity law: A ≤ A."""
        assert lattice.is_subtype("str", "str")
        assert lattice.is_subtype("int", "int")

    def test_is_subtype_transitive(self, lattice: TypeLattice) -> None:
        """Test transitivity law: If A ≤ B and B ≤ C then A ≤ C."""
        # Register types: SpecialInt ≤ int ≤ Any
        lattice.register_type(
            TypeNode(id="SpecialInt", kind=TypeKind.PRIMITIVE, name="Special Integer")
        )
        lattice.add_subtype_edge(
            SubtypeEdge(
                subtype_id="SpecialInt", supertype_id="int", reason="refinement of int"
            )
        )

        # Transitivity: SpecialInt ≤ int ≤ Any
        assert lattice.is_subtype("SpecialInt", "int")
        assert lattice.is_subtype("int", "Any")
        assert lattice.is_subtype("SpecialInt", "Any")  # Transitive

    def test_is_subtype_direct_edge(self, lattice: TypeLattice) -> None:
        """Test direct edge detection."""
        lattice.register_type(
            TypeNode(id="JSON", kind=TypeKind.RECORD, name="JSON Object")
        )
        lattice.add_subtype_edge(
            SubtypeEdge(
                subtype_id="JSON", supertype_id="str", reason="JSON is string-based"
            )
        )

        assert lattice.is_subtype("JSON", "str")

    def test_is_subtype_prevents_cycles(self, lattice: TypeLattice) -> None:
        """Test antisymmetry law enforcement: A ≤ B and B ≤ A implies A = B (prevents cycles)."""
        lattice.register_type(TypeNode(id="A", kind=TypeKind.PRIMITIVE, name="Type A"))
        lattice.register_type(TypeNode(id="B", kind=TypeKind.PRIMITIVE, name="Type B"))

        # Add A ≤ B
        lattice.add_subtype_edge(
            SubtypeEdge(subtype_id="A", supertype_id="B", reason="test")
        )

        # Try to add B ≤ A (would create cycle)
        with pytest.raises(ValueError, match="would create cycle"):
            lattice.add_subtype_edge(
                SubtypeEdge(subtype_id="B", supertype_id="A", reason="test")
            )


# ─────────────────────────────────────────────────────────────
# Meet/Join Tests (Law Verification)
# ─────────────────────────────────────────────────────────────


@pytest.mark.law("lattice")
class TestMeetJoinLaws:
    """Tests for meet/join lattice laws."""

    def test_meet_when_one_is_subtype(self, lattice: TypeLattice) -> None:
        """Test meet when A ≤ B: meet(A, B) = A."""
        assert lattice.meet("int", "Any") == "int"
        assert lattice.meet("str", "Any") == "str"

    def test_meet_symmetric(self, lattice: TypeLattice) -> None:
        """Test commutativity law: meet(A, B) = meet(B, A)."""
        result1 = lattice.meet("int", "str")
        result2 = lattice.meet("str", "int")
        assert result1 == result2

    def test_meet_no_common_subtype(self, lattice: TypeLattice) -> None:
        """Test meet when no common subtype exists: meet(A, B) = Never."""
        # int and str have no common subtype except Never
        assert lattice.meet("int", "str") == "Never"

    def test_join_when_one_is_subtype(self, lattice: TypeLattice) -> None:
        """Test join when A ≤ B: join(A, B) = B."""
        assert lattice.join("int", "Any") == "Any"
        assert lattice.join("str", "Any") == "Any"

    def test_join_symmetric(self, lattice: TypeLattice) -> None:
        """Test commutativity law: join(A, B) = join(B, A)."""
        result1 = lattice.join("int", "str")
        result2 = lattice.join("str", "int")
        assert result1 == result2

    def test_join_unrelated_types(self, lattice: TypeLattice) -> None:
        """Test join of unrelated types: join(A, B) = Any."""
        # int and str have Any as common supertype
        assert lattice.join("int", "str") == "Any"


# ─────────────────────────────────────────────────────────────
# Composition Verification Tests
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_can_compose_compatible_types(
    registry: Registry, lattice: TypeLattice
) -> None:
    """Test composition of compatible agents."""
    # Register agents
    await registry.register(
        CatalogEntry(
            id="parser",
            entity_type=EntityType.AGENT,
            name="HTMLParser",
            version="1.0.0",
            description="Parse HTML to text",
            input_type="str",
            output_type="str",
        )
    )

    await registry.register(
        CatalogEntry(
            id="analyzer",
            entity_type=EntityType.AGENT,
            name="TextAnalyzer",
            version="1.0.0",
            description="Analyze text sentiment",
            input_type="str",
            output_type="float",
        )
    )

    result = await lattice.can_compose("parser", "analyzer")
    assert result.compatible is True
    assert "subtype" in result.reason.lower()


@pytest.mark.asyncio
async def test_can_compose_incompatible_types(
    registry: Registry, lattice: TypeLattice
) -> None:
    """Test composition of incompatible agents."""
    await registry.register(
        CatalogEntry(
            id="counter",
            entity_type=EntityType.AGENT,
            name="Counter",
            version="1.0.0",
            description="Count items",
            input_type="str",
            output_type="int",
        )
    )

    await registry.register(
        CatalogEntry(
            id="formatter",
            entity_type=EntityType.AGENT,
            name="FloatFormatter",
            version="1.0.0",
            description="Format floats",
            input_type="float",
            output_type="str",
        )
    )

    result = await lattice.can_compose("counter", "formatter")
    assert result.compatible is False
    assert "mismatch" in result.reason.lower()
    assert result.suggested_fix is not None


@pytest.mark.asyncio
async def test_can_compose_missing_type_info(
    registry: Registry, lattice: TypeLattice
) -> None:
    """Test composition when type info is missing."""
    await registry.register(
        CatalogEntry(
            id="mystery",
            entity_type=EntityType.AGENT,
            name="Mystery",
            version="1.0.0",
            description="Unknown types",
            input_type=None,
            output_type=None,
        )
    )

    result = await lattice.can_compose("mystery", "mystery")
    assert result.compatible is False
    assert "missing type" in result.reason.lower()


@pytest.mark.asyncio
async def test_verify_pipeline_all_compatible(
    registry: Registry, lattice: TypeLattice
) -> None:
    """Test pipeline verification when all stages are compatible."""
    # Create chain: str → str → int
    await registry.register(
        CatalogEntry(
            id="step1",
            entity_type=EntityType.AGENT,
            name="Step1",
            version="1.0.0",
            description="First step",
            input_type="str",
            output_type="str",
        )
    )

    await registry.register(
        CatalogEntry(
            id="step2",
            entity_type=EntityType.AGENT,
            name="Step2",
            version="1.0.0",
            description="Second step",
            input_type="str",
            output_type="int",
        )
    )

    verification = await lattice.verify_pipeline(["step1", "step2"])
    assert verification.valid is True
    assert len(verification.stages) == 1
    assert verification.stages[0].result.compatible is True


@pytest.mark.asyncio
async def test_verify_pipeline_has_incompatible_stage(
    registry: Registry, lattice: TypeLattice
) -> None:
    """Test pipeline verification when a stage is incompatible."""
    await registry.register(
        CatalogEntry(
            id="a",
            entity_type=EntityType.AGENT,
            name="A",
            version="1.0.0",
            description="Agent A",
            input_type="str",
            output_type="int",
        )
    )

    await registry.register(
        CatalogEntry(
            id="b",
            entity_type=EntityType.AGENT,
            name="B",
            version="1.0.0",
            description="Agent B",
            input_type="str",
            output_type="float",
        )
    )

    verification = await lattice.verify_pipeline(["a", "b"])
    assert verification.valid is False
    assert len(verification.stages) == 1
    assert verification.stages[0].result.compatible is False


@pytest.mark.asyncio
async def test_verify_pipeline_empty(lattice: TypeLattice) -> None:
    """Test pipeline verification with less than 2 agents."""
    verification = await lattice.verify_pipeline([])
    assert verification.valid is True
    assert len(verification.stages) == 0

    verification = await lattice.verify_pipeline(["single"])
    assert verification.valid is True
    assert len(verification.stages) == 0


# ─────────────────────────────────────────────────────────────
# Composition Planning Tests
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_find_path_direct_compatibility(lattice: TypeLattice) -> None:
    """Test find_path when types are directly compatible."""
    paths = await lattice.find_path("str", "Any")
    assert paths == [[]]  # No agents needed, direct subtype


@pytest.mark.asyncio
async def test_find_path_via_agents(registry: Registry, lattice: TypeLattice) -> None:
    """Test find_path through a chain of agents."""
    # Create chain: TypeA → TypeB → TypeC
    lattice.register_type(TypeNode(id="TypeA", kind=TypeKind.PRIMITIVE, name="Type A"))
    lattice.register_type(TypeNode(id="TypeB", kind=TypeKind.PRIMITIVE, name="Type B"))
    lattice.register_type(TypeNode(id="TypeC", kind=TypeKind.PRIMITIVE, name="Type C"))

    await registry.register(
        CatalogEntry(
            id="ab",
            entity_type=EntityType.AGENT,
            name="A to B",
            version="1.0.0",
            description="Convert A to B",
            input_type="TypeA",
            output_type="TypeB",
        )
    )

    await registry.register(
        CatalogEntry(
            id="bc",
            entity_type=EntityType.AGENT,
            name="B to C",
            version="1.0.0",
            description="Convert B to C",
            input_type="TypeB",
            output_type="TypeC",
        )
    )

    paths = await lattice.find_path("TypeA", "TypeC", max_length=3)
    assert paths is not None
    assert len(paths) > 0
    assert paths[0] == ["ab", "bc"]  # Shortest path


@pytest.mark.asyncio
async def test_find_path_no_path_exists(lattice: TypeLattice) -> None:
    """Test find_path when no path exists."""
    lattice.register_type(
        TypeNode(id="IsolatedA", kind=TypeKind.PRIMITIVE, name="Isolated A")
    )
    lattice.register_type(
        TypeNode(id="IsolatedB", kind=TypeKind.PRIMITIVE, name="Isolated B")
    )

    paths = await lattice.find_path("IsolatedA", "IsolatedB")
    assert paths is None


@pytest.mark.asyncio
async def test_suggest_composition_valid_pipeline(
    registry: Registry, lattice: TypeLattice
) -> None:
    """Test suggest_composition finds valid compositions."""
    # Register types
    lattice.register_type(TypeNode(id="HTML", kind=TypeKind.PRIMITIVE, name="HTML"))
    lattice.register_type(TypeNode(id="Text", kind=TypeKind.PRIMITIVE, name="Text"))
    lattice.register_type(
        TypeNode(id="Sentiment", kind=TypeKind.PRIMITIVE, name="Sentiment")
    )

    # Register agents
    await registry.register(
        CatalogEntry(
            id="parse",
            entity_type=EntityType.AGENT,
            name="HTMLParser",
            version="1.0.0",
            description="Parse HTML",
            input_type="HTML",
            output_type="Text",
        )
    )

    await registry.register(
        CatalogEntry(
            id="analyze",
            entity_type=EntityType.AGENT,
            name="SentimentAnalyzer",
            version="1.0.0",
            description="Analyze sentiment",
            input_type="Text",
            output_type="Sentiment",
        )
    )

    suggestions = await lattice.suggest_composition(
        available=["parse", "analyze"], goal_input="HTML", goal_output="Sentiment"
    )

    assert len(suggestions) > 0
    assert suggestions[0].artifacts == ["parse", "analyze"]
    assert suggestions[0].length == 2


@pytest.mark.asyncio
async def test_suggest_composition_no_valid_composition(
    registry: Registry, lattice: TypeLattice
) -> None:
    """Test suggest_composition when no valid composition exists."""
    lattice.register_type(TypeNode(id="X", kind=TypeKind.PRIMITIVE, name="X"))
    lattice.register_type(TypeNode(id="Y", kind=TypeKind.PRIMITIVE, name="Y"))
    lattice.register_type(TypeNode(id="Z", kind=TypeKind.PRIMITIVE, name="Z"))

    await registry.register(
        CatalogEntry(
            id="xy",
            entity_type=EntityType.AGENT,
            name="X to Y",
            version="1.0.0",
            description="X to Y",
            input_type="X",
            output_type="Y",
        )
    )

    suggestions = await lattice.suggest_composition(
        available=["xy"], goal_input="X", goal_output="Z"
    )

    assert len(suggestions) == 0


@pytest.mark.asyncio
async def test_suggest_composition_prefers_shorter_pipelines(
    registry: Registry, lattice: TypeLattice
) -> None:
    """Test that suggest_composition prefers shorter pipelines."""
    # Create two paths: direct (1 agent) and indirect (2 agents)
    lattice.register_type(TypeNode(id="Start", kind=TypeKind.PRIMITIVE, name="Start"))
    lattice.register_type(TypeNode(id="Mid", kind=TypeKind.PRIMITIVE, name="Mid"))
    lattice.register_type(TypeNode(id="End", kind=TypeKind.PRIMITIVE, name="End"))

    await registry.register(
        CatalogEntry(
            id="direct",
            entity_type=EntityType.AGENT,
            name="Direct",
            version="1.0.0",
            description="Direct path",
            input_type="Start",
            output_type="End",
        )
    )

    await registry.register(
        CatalogEntry(
            id="step1",
            entity_type=EntityType.AGENT,
            name="Step1",
            version="1.0.0",
            description="First step",
            input_type="Start",
            output_type="Mid",
        )
    )

    await registry.register(
        CatalogEntry(
            id="step2",
            entity_type=EntityType.AGENT,
            name="Step2",
            version="1.0.0",
            description="Second step",
            input_type="Mid",
            output_type="End",
        )
    )

    suggestions = await lattice.suggest_composition(
        available=["direct", "step1", "step2"], goal_input="Start", goal_output="End"
    )

    assert len(suggestions) >= 2
    # Shortest should be first
    assert suggestions[0].length == 1
    assert suggestions[0].artifacts == ["direct"]


# ─────────────────────────────────────────────────────────────
# Edge Cases
# ─────────────────────────────────────────────────────────────


def test_register_type_creates_edges_to_any(lattice: TypeLattice) -> None:
    """Test that registering a type creates edges to Any."""
    lattice.register_type(
        TypeNode(id="CustomType", kind=TypeKind.RECORD, name="Custom Type")
    )

    assert lattice.is_subtype("CustomType", "Any")


def test_register_type_creates_edges_from_never(lattice: TypeLattice) -> None:
    """Test that registering a type creates edges from Never."""
    lattice.register_type(
        TypeNode(id="CustomType", kind=TypeKind.RECORD, name="Custom Type")
    )

    assert lattice.is_subtype("Never", "CustomType")


def test_add_subtype_edge_nonexistent_types(lattice: TypeLattice) -> None:
    """Test that adding edge with nonexistent types raises error."""
    with pytest.raises(ValueError, match="not registered"):
        lattice.add_subtype_edge(
            SubtypeEdge(
                subtype_id="Nonexistent1",
                supertype_id="Nonexistent2",
                reason="test",
            )
        )


@pytest.mark.asyncio
async def test_agents_accepting_finds_compatible_agents(
    registry: Registry, lattice: TypeLattice
) -> None:
    """Test _agents_accepting finds agents with compatible input types."""
    lattice.register_type(
        TypeNode(id="SpecialStr", kind=TypeKind.PRIMITIVE, name="Special String")
    )
    lattice.add_subtype_edge(
        SubtypeEdge(
            subtype_id="SpecialStr", supertype_id="str", reason="refinement of str"
        )
    )

    await registry.register(
        CatalogEntry(
            id="processor",
            entity_type=EntityType.AGENT,
            name="StringProcessor",
            version="1.0.0",
            description="Process strings",
            input_type="str",
            output_type="int",
        )
    )

    # Should find processor because SpecialStr ≤ str
    agents = await lattice._agents_accepting("SpecialStr")
    assert len(agents) == 1
    assert agents[0].id == "processor"


# ─────────────────────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_full_pipeline_planning_workflow(
    registry: Registry, lattice: TypeLattice
) -> None:
    """Test complete workflow: define types, register agents, plan pipeline."""
    # 1. Define custom types
    lattice.register_type(
        TypeNode(id="RawHTML", kind=TypeKind.PRIMITIVE, name="Raw HTML")
    )
    lattice.register_type(
        TypeNode(id="CleanText", kind=TypeKind.PRIMITIVE, name="Clean Text")
    )
    lattice.register_type(
        TypeNode(id="SentimentScore", kind=TypeKind.RECORD, name="Sentiment Score")
    )

    # 2. Register agents
    await registry.register(
        CatalogEntry(
            id="cleaner",
            entity_type=EntityType.AGENT,
            name="HTMLCleaner",
            version="1.0.0",
            description="Clean HTML to text",
            input_type="RawHTML",
            output_type="CleanText",
        )
    )

    await registry.register(
        CatalogEntry(
            id="sentiment",
            entity_type=EntityType.AGENT,
            name="SentimentAnalyzer",
            version="1.0.0",
            description="Analyze sentiment",
            input_type="CleanText",
            output_type="SentimentScore",
        )
    )

    # 3. Find composition path
    paths = await lattice.find_path("RawHTML", "SentimentScore")
    assert paths is not None
    assert len(paths) > 0

    # 4. Verify the pipeline
    pipeline = paths[0]
    verification = await lattice.verify_pipeline(pipeline)
    assert verification.valid is True

    # 5. Suggest compositions
    suggestions = await lattice.suggest_composition(
        available=["cleaner", "sentiment"],
        goal_input="RawHTML",
        goal_output="SentimentScore",
    )
    assert len(suggestions) > 0
    assert suggestions[0].artifacts == ["cleaner", "sentiment"]


def test_create_lattice_convenience_function(registry: Registry) -> None:
    """Test create_lattice convenience function."""
    lattice = create_lattice(registry)
    assert isinstance(lattice, TypeLattice)
    assert lattice.registry is registry
    assert "Any" in lattice.types
