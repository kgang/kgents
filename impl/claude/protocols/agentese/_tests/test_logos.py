"""
Tests for AGENTESE Logos Resolver

Verifies:
- Path parsing and validation
- Context resolution (five strict contexts)
- Observer requirement enforcement
- Cache behavior
- JIT generation from specs
- Composition support
"""

import pytest

from ..exceptions import (
    AffordanceError,
    ObserverRequiredError,
    PathNotFoundError,
    PathSyntaxError,
)
from ..logos import (
    ComposedPath,
    Logos,
    PlaceholderNode,
    SimpleRegistry,
    create_logos,
)
from ..node import (
    AgentMeta,
    BasicRendering,
)


class TestSimpleRegistry:
    """Tests for SimpleRegistry."""

    def test_empty_registry(self):
        """Empty registry returns None for any handle."""
        registry = SimpleRegistry()
        assert registry.get("world.house") is None

    def test_register_and_get(self):
        """Can register and retrieve nodes."""
        registry = SimpleRegistry()
        node = PlaceholderNode(handle="world.house")
        registry.register("world.house", node)
        assert registry.get("world.house") is node

    def test_list_handles(self):
        """Can list all handles."""
        registry = SimpleRegistry()
        registry.register("world.house", PlaceholderNode(handle="world.house"))
        registry.register("world.garden", PlaceholderNode(handle="world.garden"))
        registry.register("concept.justice", PlaceholderNode(handle="concept.justice"))

        all_handles = registry.list_handles()
        assert len(all_handles) == 3
        assert "world.house" in all_handles

    def test_list_handles_with_prefix(self):
        """Can filter handles by prefix."""
        registry = SimpleRegistry()
        registry.register("world.house", PlaceholderNode(handle="world.house"))
        registry.register("world.garden", PlaceholderNode(handle="world.garden"))
        registry.register("concept.justice", PlaceholderNode(handle="concept.justice"))

        world_handles = registry.list_handles("world.")
        assert len(world_handles) == 2
        assert "world.house" in world_handles
        assert "concept.justice" not in world_handles


class TestPathParsing:
    """Tests for AGENTESE path parsing."""

    def test_valid_two_part_path(self, logos_with_nodes):
        """Two-part path (context.holon) is valid."""
        node = logos_with_nodes.resolve("world.house")
        assert node.handle == "world.house"

    def test_single_part_path_fails(self, logos):
        """Single-part path raises PathSyntaxError."""
        with pytest.raises(PathSyntaxError) as exc:
            logos.resolve("world")
        assert "incomplete" in str(exc.value)

    def test_empty_path_fails(self, logos):
        """Empty path raises PathSyntaxError."""
        with pytest.raises(PathSyntaxError):
            logos.resolve("")


class TestContextValidation:
    """Tests for five strict contexts."""

    @pytest.mark.parametrize("context", ["world", "self", "concept", "void", "time"])
    def test_valid_contexts_accepted(self, context, populated_registry):
        """All five contexts are accepted."""
        logos = Logos(registry=populated_registry)
        # Register a node for each context
        logos.register(f"{context}.test", PlaceholderNode(handle=f"{context}.test"))

        node = logos.resolve(f"{context}.test")
        assert node.handle == f"{context}.test"

    def test_invalid_context_rejected(self, logos):
        """Invalid context raises PathNotFoundError."""
        with pytest.raises(PathNotFoundError) as exc:
            logos.resolve("invalid.house")
        assert "Unknown context" in str(exc.value)
        assert "valid contexts" in str(exc.value).lower()

    def test_sixth_context_rejected(self, logos):
        """No sixth context allowed."""
        for invalid in ["system", "meta", "admin", "root", "global"]:
            with pytest.raises(PathNotFoundError):
                logos.resolve(f"{invalid}.test")


class TestObserverRequirement:
    """Tests for observer enforcement."""

    @pytest.mark.asyncio
    async def test_invoke_without_observer_fails(self, logos_with_nodes):
        """invoke() without observer raises ObserverRequiredError."""
        with pytest.raises(ObserverRequiredError) as exc:
            await logos_with_nodes.invoke("world.house.manifest", None)
        assert "no view from nowhere" in str(exc.value)

    @pytest.mark.asyncio
    async def test_invoke_with_observer_succeeds(self, logos_with_nodes, mock_umwelt):
        """invoke() with observer works."""
        result = await logos_with_nodes.invoke("world.house.manifest", mock_umwelt)
        assert result is not None

    def test_resolve_works_without_observer(self, logos_with_nodes):
        """resolve() doesn't require observer (affordance check is on invoke)."""
        node = logos_with_nodes.resolve("world.house")
        assert node is not None


class TestAffordanceEnforcement:
    """Tests for affordance checking on invoke."""

    @pytest.mark.asyncio
    async def test_allowed_affordance_succeeds(self, mock_umwelt):
        """Can invoke affordances available to observer."""
        registry = SimpleRegistry()
        registry.register(
            "world.house",
            PlaceholderNode(
                handle="world.house",
                archetype_affordances={"default": ("describe",)},
            ),
        )
        logos = Logos(registry=registry)

        # manifest is always available
        result = await logos.invoke("world.house.manifest", mock_umwelt)
        assert result is not None

    @pytest.mark.asyncio
    async def test_denied_affordance_fails(self, mock_umwelt):
        """Cannot invoke affordances not available to observer."""
        registry = SimpleRegistry()
        registry.register(
            "world.house",
            PlaceholderNode(
                handle="world.house",
                archetype_affordances={"architect": ("demolish",)},
            ),
        )
        logos = Logos(registry=registry)

        # default archetype doesn't have "demolish"
        with pytest.raises(AffordanceError) as exc:
            await logos.invoke("world.house.demolish", mock_umwelt)
        assert "demolish" in str(exc.value)
        assert "default" in str(exc.value)  # observer archetype

    @pytest.mark.asyncio
    async def test_affordance_error_lists_available(self, mock_umwelt):
        """AffordanceError shows what IS available."""
        registry = SimpleRegistry()
        registry.register(
            "world.house",
            PlaceholderNode(handle="world.house"),
        )
        logos = Logos(registry=registry)

        with pytest.raises(AffordanceError) as exc:
            await logos.invoke("world.house.demolish", mock_umwelt)
        # Should mention available affordances
        assert "manifest" in str(exc.value)


class TestCaching:
    """Tests for resolution cache behavior."""

    def test_resolved_node_is_cached(self, logos_with_nodes):
        """Resolved nodes are cached."""
        node1 = logos_with_nodes.resolve("world.house")
        node2 = logos_with_nodes.resolve("world.house")
        assert node1 is node2  # Same object

    def test_is_resolved_check(self, logos_with_nodes):
        """Can check if path is cached."""
        assert not logos_with_nodes.is_resolved("world.house")
        logos_with_nodes.resolve("world.house")
        assert logos_with_nodes.is_resolved("world.house")

    def test_clear_cache(self, logos_with_nodes):
        """Can clear the cache."""
        logos_with_nodes.resolve("world.house")
        assert logos_with_nodes.is_resolved("world.house")

        logos_with_nodes.clear_cache()
        assert not logos_with_nodes.is_resolved("world.house")


class TestJITGeneration:
    """Tests for spec-based JIT generation."""

    def test_generates_from_spec(self, logos_with_specs):
        """Node is generated when spec exists."""
        # Note: In Phase 2, context resolvers create placeholder nodes
        # JIT generation from spec happens at the resolver level
        node = logos_with_specs.resolve("world.library")
        assert node.handle == "world.library"
        # WorldNode created by resolver (JIT happens in Phase 4)

    def test_unknown_holon_creates_placeholder(self, logos):
        """Phase 2: Unknown holons create placeholder nodes for exploration."""
        # In Phase 2, context resolvers create explorable nodes
        node = logos.resolve("world.nonexistent")
        assert node.handle == "world.nonexistent"
        # Can still be explored via manifest, witness, etc.

    def test_placeholder_has_base_affordances(self, logos):
        """Placeholder nodes have base affordances for exploration."""
        node = logos.resolve("world.castle")
        meta = AgentMeta(name="test", archetype="default")
        affordances = node.affordances(meta)
        assert "manifest" in affordances
        assert "witness" in affordances


class TestLift:
    """Tests for lift() method."""

    def test_lift_requires_aspect(self, logos_with_nodes):
        """lift() requires full path with aspect."""
        with pytest.raises(PathSyntaxError) as exc:
            logos_with_nodes.lift("world.house")
        assert "requires aspect" in str(exc.value)

    def test_lift_returns_agent(self, logos_with_nodes):
        """lift() returns composable agent."""
        agent = logos_with_nodes.lift("world.house.manifest")
        assert agent is not None
        assert hasattr(agent, "invoke")

    @pytest.mark.asyncio
    async def test_lifted_agent_invokes(self, logos_with_nodes, mock_umwelt):
        """Lifted agent can be invoked with Umwelt."""
        agent = logos_with_nodes.lift("world.house.manifest")
        result = await agent.invoke(mock_umwelt)
        assert isinstance(result, BasicRendering)


class TestComposition:
    """Tests for path composition."""

    def test_compose_creates_composed_path(self, logos_with_nodes):
        """compose() creates ComposedPath."""
        path = logos_with_nodes.compose(
            "world.house.manifest",
            "concept.justice.manifest",
        )
        assert isinstance(path, ComposedPath)
        assert len(path.paths) == 2

    def test_composed_path_name(self, logos_with_nodes):
        """ComposedPath has readable name."""
        path = logos_with_nodes.compose(
            "world.house.manifest",
            "concept.justice.manifest",
        )
        assert "world.house.manifest" in path.name
        assert ">>" in path.name

    def test_composed_path_rshift(self, logos_with_nodes):
        """ComposedPath can be extended with >>."""
        path = logos_with_nodes.compose("world.house.manifest")
        extended = path >> "concept.justice.manifest"
        assert len(extended.paths) == 2

    @pytest.mark.asyncio
    async def test_composed_path_invokes(self, logos_with_nodes, mock_umwelt):
        """ComposedPath can be invoked as pipeline."""
        # Register a simple node that accepts any input
        logos_with_nodes.register(
            "concept.transform",
            PlaceholderNode(handle="concept.transform"),
        )

        path = logos_with_nodes.compose(
            "world.house.manifest",
        )
        result = await path.invoke(mock_umwelt)
        assert result is not None


class TestListHandles:
    """Tests for handle listing."""

    def test_list_all_handles(self, logos_with_nodes):
        """Can list all registered handles."""
        handles = logos_with_nodes.list_handles()
        assert "world.house" in handles
        assert "world.garden" in handles
        assert "concept.justice" in handles

    def test_list_handles_by_context(self, logos_with_nodes):
        """Can filter handles by context."""
        world_handles = logos_with_nodes.list_handles("world")
        assert "world.house" in world_handles
        assert "world.garden" in world_handles
        assert "concept.justice" not in world_handles


class TestFactoryFunction:
    """Tests for create_logos factory."""

    def test_creates_with_defaults(self):
        """Factory creates logos with defaults."""
        logos = create_logos()
        assert logos is not None
        assert isinstance(logos.registry, SimpleRegistry)

    def test_creates_with_custom_spec_root(self, temp_spec_dir):
        """Factory accepts custom spec root."""
        logos = create_logos(spec_root=temp_spec_dir)
        assert logos.spec_root == temp_spec_dir

    def test_creates_with_registry(self):
        """Factory accepts pre-populated registry."""
        registry = SimpleRegistry()
        registry.register("world.house", PlaceholderNode(handle="world.house"))

        logos = create_logos(registry=registry)
        node = logos.resolve("world.house")
        assert node.handle == "world.house"


class TestSympatheticErrors:
    """Tests ensuring all errors are sympathetic."""

    def test_unknown_holon_creates_explorable_node(self, logos):
        """Phase 2: Unknown holons create nodes for exploration (not errors)."""
        # In Phase 2, context resolvers create explorable placeholder nodes
        node = logos.resolve("world.mysterious")
        assert node.handle == "world.mysterious"
        # The node is explorable via standard affordances

    def test_invalid_context_suggests_valid_ones(self, logos):
        """Invalid context error lists valid contexts."""
        with pytest.raises(PathNotFoundError) as exc:
            logos.resolve("bogus.thing")
        error = str(exc.value)
        assert "world" in error
        assert "self" in error

    @pytest.mark.asyncio
    async def test_affordance_error_is_helpful(self, logos_with_nodes, mock_umwelt):
        """AffordanceError lists available alternatives."""
        with pytest.raises(AffordanceError) as exc:
            await logos_with_nodes.invoke("world.house.demolish", mock_umwelt)
        error = str(exc.value)
        # Should list what IS available
        assert "manifest" in error or "affordances" in error.lower()


class TestPlaceholderNode:
    """Tests for PlaceholderNode helper."""

    def test_placeholder_basic(self):
        """PlaceholderNode works for testing."""
        node = PlaceholderNode(handle="test.node")
        meta = AgentMeta(name="test", archetype="default")

        affs = node.affordances(meta)
        assert "manifest" in affs

    def test_placeholder_with_archetype_affordances(self):
        """PlaceholderNode supports archetype-specific affordances."""
        node = PlaceholderNode(
            handle="test.node",
            archetype_affordances={
                "admin": ("delete", "modify"),
                "user": ("read",),
            },
        )

        admin_meta = AgentMeta(name="admin", archetype="admin")
        admin_affs = node.affordances(admin_meta)
        assert "delete" in admin_affs
        assert "modify" in admin_affs

        user_meta = AgentMeta(name="user", archetype="user")
        user_affs = node.affordances(user_meta)
        assert "read" in user_affs
        assert "delete" not in user_affs

    @pytest.mark.asyncio
    async def test_placeholder_manifest(self, mock_umwelt):
        """PlaceholderNode returns BasicRendering on manifest."""
        node = PlaceholderNode(handle="test.placeholder")
        result = await node.manifest(mock_umwelt)
        assert isinstance(result, BasicRendering)
        assert "Placeholder" in result.summary
