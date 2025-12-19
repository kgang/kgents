"""
Tests for Ghost Integration (v3.2) - alternatives aspect.

Tests the _get_alternatives method on BaseLogosNode, ensuring that:
1. alternatives returns sibling aspects minus invoked
2. alternatives respects max 5 limit
3. alternatives excludes introspection aspects
4. hints are populated correctly
5. categories are mapped correctly
"""

import pytest

from bootstrap.umwelt import Umwelt
from protocols.agentese.affordances import STANDARD_ASPECTS, AspectCategory
from protocols.agentese.node import AgentMeta, BaseLogosNode, Ghost, Observer, Renderable

# === Test Node Implementation ===


class TestNode(BaseLogosNode):
    """Test node with multiple affordances."""

    @property
    def handle(self) -> str:
        return "test.node"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Provide archetype-specific affordances."""
        if archetype == "developer":
            return ("build", "test", "refactor")
        return ()

    async def manifest(self, observer: "Umwelt[object, object]") -> Renderable:
        """Test manifest implementation."""
        from protocols.agentese.node import BasicRendering

        return BasicRendering(summary="Test Node")

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[object, object]",
        **kwargs: object,
    ) -> object:
        """Test aspect invocation."""
        return f"Invoked {aspect}"


# === Fixtures ===


@pytest.fixture
def test_node() -> TestNode:
    """Create a test node instance."""
    return TestNode()


@pytest.fixture
def developer_meta() -> AgentMeta:
    """Create developer archetype metadata."""
    return AgentMeta(name="tester", archetype="developer", capabilities=())


@pytest.fixture
def default_meta() -> AgentMeta:
    """Create default archetype metadata."""
    return AgentMeta(name="guest", archetype="default", capabilities=())


# === Tests ===


def test_alternatives_returns_sibling_aspects(
    test_node: TestNode, developer_meta: AgentMeta
) -> None:
    """Test that alternatives returns sibling aspects excluding invoked."""
    # Developer has: manifest, witness, affordances, help, alternatives, build, test, refactor
    # Invoke manifest, should get back: witness, build, test, refactor (max 5, excluding introspection)
    alternatives = test_node._get_alternatives("manifest", developer_meta)

    assert isinstance(alternatives, list)
    assert len(alternatives) > 0

    # Check that invoked aspect is excluded
    aspect_names = [alt["aspect"] for alt in alternatives]
    assert "manifest" not in aspect_names

    # Check that introspection aspects are excluded
    assert "alternatives" not in aspect_names
    assert "affordances" not in aspect_names
    assert "help" not in aspect_names

    # Should include developer-specific aspects
    assert "build" in aspect_names or "test" in aspect_names or "refactor" in aspect_names


def test_alternatives_max_five_limit(test_node: TestNode, developer_meta: AgentMeta) -> None:
    """Test that alternatives respects max 5 limit."""
    alternatives = test_node._get_alternatives(None, developer_meta)

    assert len(alternatives) <= 5


def test_alternatives_excludes_introspection(
    test_node: TestNode, developer_meta: AgentMeta
) -> None:
    """Test that introspection aspects are always excluded."""
    alternatives = test_node._get_alternatives(None, developer_meta)

    aspect_names = [alt["aspect"] for alt in alternatives]

    # These should never appear in alternatives
    assert "alternatives" not in aspect_names
    assert "affordances" not in aspect_names
    assert "help" not in aspect_names


def test_alternatives_structure(test_node: TestNode, developer_meta: AgentMeta) -> None:
    """Test that each alternative has the correct structure."""
    alternatives = test_node._get_alternatives("manifest", developer_meta)

    for alt in alternatives:
        # Check dictionary structure
        assert "aspect" in alt
        assert "hint" in alt
        assert "category" in alt

        # Check types
        assert isinstance(alt["aspect"], str)
        assert isinstance(alt["hint"], str)
        assert isinstance(alt["category"], str)

        # Category should be a valid AspectCategory name
        try:
            AspectCategory[alt["category"]]
        except KeyError:
            # UNKNOWN is also acceptable
            assert alt["category"] == "UNKNOWN"


def test_alternatives_hints_populated(test_node: TestNode, developer_meta: AgentMeta) -> None:
    """Test that hints are populated from ASPECT_HINTS or registry."""
    alternatives = test_node._get_alternatives("manifest", developer_meta)

    for alt in alternatives:
        hint = alt["hint"]
        # Hint should not be empty
        assert hint
        assert len(hint) > 0

        # Should be a descriptive string
        assert isinstance(hint, str)


def test_alternatives_with_no_invoked(test_node: TestNode, developer_meta: AgentMeta) -> None:
    """Test alternatives when no aspect was invoked."""
    alternatives = test_node._get_alternatives(None, developer_meta)

    # Should still exclude introspection aspects
    aspect_names = [alt["aspect"] for alt in alternatives]
    assert "alternatives" not in aspect_names
    assert "affordances" not in aspect_names
    assert "help" not in aspect_names


def test_alternatives_default_archetype(test_node: TestNode, default_meta: AgentMeta) -> None:
    """Test alternatives for default archetype with fewer affordances."""
    # Default has: manifest, witness, affordances, help, alternatives
    alternatives = test_node._get_alternatives("manifest", default_meta)

    aspect_names = [alt["aspect"] for alt in alternatives]

    # Should have witness at minimum
    assert "witness" in aspect_names

    # Should not have developer-specific aspects
    assert "build" not in aspect_names
    assert "test" not in aspect_names
    assert "refactor" not in aspect_names


def test_ghost_dataclass() -> None:
    """Test Ghost dataclass."""
    ghost = Ghost(aspect="witness", hint="View history", category="PERCEPTION")

    assert ghost.aspect == "witness"
    assert ghost.hint == "View history"
    assert ghost.category == "PERCEPTION"

    # Test to_dict
    ghost_dict = ghost.to_dict()
    assert ghost_dict == {
        "aspect": "witness",
        "hint": "View history",
        "category": "PERCEPTION",
    }


def test_ghost_dataclass_frozen() -> None:
    """Test that Ghost is frozen (immutable)."""
    ghost = Ghost(aspect="witness", hint="View history")

    with pytest.raises(Exception):  # dataclass FrozenInstanceError
        ghost.aspect = "manifest"  # type: ignore[misc]


def test_alternatives_categories_correct(test_node: TestNode, developer_meta: AgentMeta) -> None:
    """Test that categories are correctly mapped from STANDARD_ASPECTS."""
    alternatives = test_node._get_alternatives("manifest", developer_meta)

    for alt in alternatives:
        aspect_name = alt["aspect"]
        category = alt["category"]

        # Check against STANDARD_ASPECTS if available
        if aspect_name in STANDARD_ASPECTS:
            expected_category = STANDARD_ASPECTS[aspect_name].category.name
            assert category == expected_category
        else:
            # Custom aspects should have UNKNOWN category
            assert category == "UNKNOWN"
