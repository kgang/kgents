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

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from testing.fixtures import as_umwelt

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

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
from .conftest import MockUmwelt


class TestSimpleRegistry:
    """Tests for SimpleRegistry."""

    def test_empty_registry(self) -> None:
        """Empty registry returns None for any handle."""
        registry = SimpleRegistry()
        assert registry.get("world.house") is None

    def test_register_and_get(self) -> None:
        """Can register and retrieve nodes."""
        registry = SimpleRegistry()
        node = PlaceholderNode(handle="world.house")
        registry.register("world.house", node)
        assert registry.get("world.house") is node

    def test_list_handles(self) -> None:
        """Can list all handles."""
        registry = SimpleRegistry()
        registry.register("world.house", PlaceholderNode(handle="world.house"))
        registry.register("world.garden", PlaceholderNode(handle="world.garden"))
        registry.register("concept.justice", PlaceholderNode(handle="concept.justice"))

        all_handles = registry.list_handles()
        assert len(all_handles) == 3
        assert "world.house" in all_handles

    def test_list_handles_with_prefix(self) -> None:
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

    def test_valid_two_part_path(self, logos_with_nodes: Logos) -> None:
        """Two-part path (context.holon) is valid."""
        node = logos_with_nodes.resolve("world.house")
        assert node.handle == "world.house"

    def test_single_part_path_fails(self, logos: Logos) -> None:
        """Single-part path raises PathSyntaxError."""
        with pytest.raises(PathSyntaxError) as exc:
            logos.resolve("world")
        assert "incomplete" in str(exc.value)

    def test_empty_path_fails(self, logos: Logos) -> None:
        """Empty path raises PathSyntaxError."""
        with pytest.raises(PathSyntaxError):
            logos.resolve("")


class TestContextValidation:
    """Tests for five strict contexts."""

    @pytest.mark.parametrize("context", ["world", "self", "concept", "void", "time"])
    def test_valid_contexts_accepted(
        self, context: str, populated_registry: SimpleRegistry
    ) -> None:
        """All five contexts are accepted."""
        logos = Logos(registry=populated_registry)
        # Register a node for each context
        logos.register(f"{context}.test", PlaceholderNode(handle=f"{context}.test"))

        node = logos.resolve(f"{context}.test")
        assert node.handle == f"{context}.test"

    def test_invalid_context_rejected(self, logos: Logos) -> None:
        """Invalid context raises PathNotFoundError."""
        with pytest.raises(PathNotFoundError) as exc:
            logos.resolve("invalid.house")
        assert "Unknown context" in str(exc.value)
        assert "valid contexts" in str(exc.value).lower()

    def test_sixth_context_rejected(self, logos: Logos) -> None:
        """No sixth context allowed."""
        for invalid in ["system", "meta", "admin", "root", "global"]:
            with pytest.raises(PathNotFoundError):
                logos.resolve(f"{invalid}.test")


class TestObserverRequirement:
    """Tests for observer enforcement."""

    @pytest.mark.asyncio
    async def test_invoke_without_observer_defaults_to_guest(
        self, logos_with_nodes: Logos
    ) -> None:
        """v3 API: invoke() without observer defaults to Observer.guest()."""
        # v3: None defaults to guest observer, not an error
        result = await logos_with_nodes.invoke("world.house.manifest", None)
        assert result is not None  # Guest observer can still get basic manifest

    @pytest.mark.asyncio
    async def test_invoke_with_observer_succeeds(
        self, logos_with_nodes: Logos, mock_umwelt: MockUmwelt
    ) -> None:
        """invoke() with observer works."""
        result = await logos_with_nodes.invoke(
            "world.house.manifest", as_umwelt(mock_umwelt)
        )
        assert result is not None

    def test_resolve_works_without_observer(self, logos_with_nodes: Logos) -> None:
        """resolve() doesn't require observer (affordance check is on invoke)."""
        node = logos_with_nodes.resolve("world.house")
        assert node is not None


class TestAffordanceEnforcement:
    """Tests for affordance checking on invoke."""

    @pytest.mark.asyncio
    async def test_allowed_affordance_succeeds(self, mock_umwelt: MockUmwelt) -> None:
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
        result = await logos.invoke("world.house.manifest", as_umwelt(mock_umwelt))
        assert result is not None

    @pytest.mark.asyncio
    async def test_denied_affordance_fails(self, mock_umwelt: MockUmwelt) -> None:
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
            await logos.invoke("world.house.demolish", as_umwelt(mock_umwelt))
        assert "demolish" in str(exc.value)
        assert "default" in str(exc.value)  # observer archetype

    @pytest.mark.asyncio
    async def test_affordance_error_lists_available(
        self, mock_umwelt: MockUmwelt
    ) -> None:
        """AffordanceError shows what IS available."""
        registry = SimpleRegistry()
        registry.register(
            "world.house",
            PlaceholderNode(handle="world.house"),
        )
        logos = Logos(registry=registry)

        with pytest.raises(AffordanceError) as exc:
            await logos.invoke("world.house.demolish", as_umwelt(mock_umwelt))
        # Should mention available affordances
        assert "manifest" in str(exc.value)


class TestCaching:
    """Tests for resolution cache behavior."""

    def test_resolved_node_is_cached(self, logos_with_nodes: Logos) -> None:
        """Resolved nodes are cached."""
        node1 = logos_with_nodes.resolve("world.house")
        node2 = logos_with_nodes.resolve("world.house")
        assert node1 is node2  # Same object

    def test_is_resolved_check(self, logos_with_nodes: Logos) -> None:
        """Can check if path is cached."""
        assert not logos_with_nodes.is_resolved("world.house")
        logos_with_nodes.resolve("world.house")
        assert logos_with_nodes.is_resolved("world.house")

    def test_clear_cache(self, logos_with_nodes: Logos) -> None:
        """Can clear the cache."""
        logos_with_nodes.resolve("world.house")
        assert logos_with_nodes.is_resolved("world.house")

        logos_with_nodes.clear_cache()
        assert not logos_with_nodes.is_resolved("world.house")


class TestJITGeneration:
    """Tests for spec-based JIT generation."""

    def test_generates_from_spec(self, logos_with_specs: Logos) -> None:
        """Node is generated when spec exists."""
        # Note: In Phase 2, context resolvers create placeholder nodes
        # JIT generation from spec happens at the resolver level
        node = logos_with_specs.resolve("world.library")
        assert node.handle == "world.library"
        # WorldNode created by resolver (JIT happens in Phase 4)

    def test_unknown_holon_creates_placeholder(self, logos: Logos) -> None:
        """Phase 2: Unknown holons create placeholder nodes for exploration."""
        # In Phase 2, context resolvers create explorable nodes
        node = logos.resolve("world.nonexistent")
        assert node.handle == "world.nonexistent"
        # Can still be explored via manifest, witness, etc.

    def test_placeholder_has_base_affordances(self, logos: Logos) -> None:
        """Placeholder nodes have base affordances for exploration."""
        node = logos.resolve("world.castle")
        meta = AgentMeta(name="test", archetype="default")
        affordances = node.affordances(meta)
        assert "manifest" in affordances
        assert "witness" in affordances


class TestLift:
    """Tests for lift() method."""

    def test_lift_requires_aspect(self, logos_with_nodes: Logos) -> None:
        """lift() requires full path with aspect."""
        with pytest.raises(PathSyntaxError) as exc:
            logos_with_nodes.lift("world.house")
        assert "requires aspect" in str(exc.value)

    def test_lift_returns_agent(self, logos_with_nodes: Logos) -> None:
        """lift() returns composable agent."""
        agent = logos_with_nodes.lift("world.house.manifest")
        assert agent is not None
        assert hasattr(agent, "invoke")

    @pytest.mark.asyncio
    async def test_lifted_agent_invokes(
        self, logos_with_nodes: Logos, mock_umwelt: MockUmwelt
    ) -> None:
        """Lifted agent can be invoked with Umwelt."""
        agent = logos_with_nodes.lift("world.house.manifest")
        result = await agent.invoke(mock_umwelt)
        assert isinstance(result, BasicRendering)


class TestComposition:
    """Tests for path composition."""

    def test_compose_creates_composed_path(self, logos_with_nodes: Logos) -> None:
        """compose() creates ComposedPath."""
        path = logos_with_nodes.compose(
            "world.house.manifest",
            "concept.justice.manifest",
        )
        assert isinstance(path, ComposedPath)
        assert len(path.paths) == 2

    def test_composed_path_name(self, logos_with_nodes: Logos) -> None:
        """ComposedPath has readable name."""
        path = logos_with_nodes.compose(
            "world.house.manifest",
            "concept.justice.manifest",
        )
        assert "world.house.manifest" in path.name
        assert ">>" in path.name

    def test_composed_path_rshift(self, logos_with_nodes: Logos) -> None:
        """ComposedPath can be extended with >>."""
        path = logos_with_nodes.compose("world.house.manifest")
        extended = path >> "concept.justice.manifest"
        assert len(extended.paths) == 2

    @pytest.mark.asyncio
    async def test_composed_path_invokes(
        self, logos_with_nodes: Logos, mock_umwelt: MockUmwelt
    ) -> None:
        """ComposedPath can be invoked as pipeline."""
        # Register a simple node that accepts any input
        logos_with_nodes.register(
            "concept.transform",
            PlaceholderNode(handle="concept.transform"),
        )

        path = logos_with_nodes.compose(
            "world.house.manifest",
        )
        result = await path.invoke(as_umwelt(mock_umwelt))
        assert result is not None


class TestListHandles:
    """Tests for handle listing."""

    def test_list_all_handles(self, logos_with_nodes: Logos) -> None:
        """Can list all registered handles."""
        handles = logos_with_nodes.list_handles()
        assert "world.house" in handles
        assert "world.garden" in handles
        assert "concept.justice" in handles

    def test_list_handles_by_context(self, logos_with_nodes: Logos) -> None:
        """Can filter handles by context."""
        world_handles = logos_with_nodes.list_handles("world")
        assert "world.house" in world_handles
        assert "world.garden" in world_handles
        assert "concept.justice" not in world_handles


class TestFactoryFunction:
    """Tests for create_logos factory."""

    def test_creates_with_defaults(self) -> None:
        """Factory creates logos with defaults."""
        logos = create_logos()
        assert logos is not None
        assert isinstance(logos.registry, SimpleRegistry)

    def test_creates_with_custom_spec_root(self, temp_spec_dir: Any) -> None:
        """Factory accepts custom spec root."""
        logos = create_logos(spec_root=temp_spec_dir)
        assert logos.spec_root == temp_spec_dir

    def test_creates_with_registry(self) -> None:
        """Factory accepts pre-populated registry."""
        registry = SimpleRegistry()
        registry.register("world.house", PlaceholderNode(handle="world.house"))

        logos = create_logos(registry=registry)
        node = logos.resolve("world.house")
        assert node.handle == "world.house"


class TestSympatheticErrors:
    """Tests ensuring all errors are sympathetic."""

    def test_unknown_holon_creates_explorable_node(self, logos: Logos) -> None:
        """Phase 2: Unknown holons create nodes for exploration (not errors)."""
        # In Phase 2, context resolvers create explorable placeholder nodes
        node = logos.resolve("world.mysterious")
        assert node.handle == "world.mysterious"
        # The node is explorable via standard affordances

    def test_invalid_context_suggests_valid_ones(self, logos: Logos) -> None:
        """Invalid context error lists valid contexts."""
        with pytest.raises(PathNotFoundError) as exc:
            logos.resolve("bogus.thing")
        error = str(exc.value)
        assert "world" in error
        assert "self" in error

    @pytest.mark.asyncio
    async def test_affordance_error_is_helpful(
        self, logos_with_nodes: Logos, mock_umwelt: MockUmwelt
    ) -> None:
        """AffordanceError lists available alternatives."""
        with pytest.raises(AffordanceError) as exc:
            await logos_with_nodes.invoke(
                "world.house.demolish", as_umwelt(mock_umwelt)
            )
        error = str(exc.value)
        # Should list what IS available
        assert "manifest" in error or "affordances" in error.lower()


class TestPlaceholderNode:
    """Tests for PlaceholderNode helper."""

    def test_placeholder_basic(self) -> None:
        """PlaceholderNode works for testing."""
        node = PlaceholderNode(handle="test.node")
        meta = AgentMeta(name="test", archetype="default")

        affs = node.affordances(meta)
        assert "manifest" in affs

    def test_placeholder_with_archetype_affordances(self) -> None:
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
    async def test_placeholder_manifest(self, mock_umwelt: MockUmwelt) -> None:
        """PlaceholderNode returns BasicRendering on manifest."""
        node = PlaceholderNode(handle="test.placeholder")
        result = await node.manifest(as_umwelt(mock_umwelt))
        assert isinstance(result, BasicRendering)
        assert "Placeholder" in result.summary


class TestCuratorMiddleware:
    """Tests for WundtCurator integration with Logos."""

    def test_with_curator_creates_new_instance(self, logos_with_nodes: Logos) -> None:
        """with_curator() creates a new Logos instance with curator set."""
        from protocols.agentese.middleware.curator import WundtCurator

        curator = WundtCurator()
        curated_logos = logos_with_nodes.with_curator(curator)

        # Should be a new instance
        assert curated_logos is not logos_with_nodes
        # Curator should be set
        assert curated_logos._curator is curator
        # Original should not have curator
        assert logos_with_nodes._curator is None

    def test_with_curator_preserves_registry(self, logos_with_nodes: Logos) -> None:
        """with_curator() preserves the registry."""
        from protocols.agentese.middleware.curator import WundtCurator

        curated_logos = logos_with_nodes.with_curator(WundtCurator())

        # Registry is shared
        assert curated_logos.registry is logos_with_nodes.registry

    @pytest.mark.asyncio
    async def test_curator_filter_called_on_invoke(
        self, mock_umwelt: MockUmwelt
    ) -> None:
        """Curator filter is called during invoke."""
        from unittest.mock import AsyncMock

        from protocols.agentese.middleware.curator import WundtCurator

        registry = SimpleRegistry()
        registry.register(
            "world.house",
            PlaceholderNode(handle="world.house"),
        )
        curator = WundtCurator()
        curator.filter = AsyncMock(return_value="filtered_result")  # type: ignore[method-assign]

        logos = Logos(registry=registry, _curator=curator)

        result = await logos.invoke("world.house.manifest", as_umwelt(mock_umwelt))

        # Curator filter was called
        curator.filter.assert_called_once()
        assert result == "filtered_result"

    @pytest.mark.asyncio
    async def test_invoke_without_curator_returns_raw(
        self, logos_with_nodes: Logos, mock_umwelt: MockUmwelt
    ) -> None:
        """invoke() without curator returns raw result."""
        result = await logos_with_nodes.invoke(
            "world.house.manifest", as_umwelt(mock_umwelt)
        )

        # Should be the raw result (BasicRendering)
        assert isinstance(result, BasicRendering)

    @pytest.mark.asyncio
    async def test_curator_exempt_paths_bypass_filter(
        self, mock_umwelt: MockUmwelt
    ) -> None:
        """Exempt paths bypass curator filtering."""
        from unittest.mock import AsyncMock

        from protocols.agentese.middleware.curator import WundtCurator

        registry = SimpleRegistry()
        registry.register(
            "void.entropy",
            PlaceholderNode(handle="void.entropy"),
        )
        curator = WundtCurator()

        # Track if filter is actually invoked
        original_filter = curator.filter
        filter_called = False

        async def tracking_filter(*args: Any, **kwargs: Any) -> Any:
            nonlocal filter_called
            filter_called = True
            return await original_filter(*args, **kwargs)

        curator.filter = tracking_filter  # type: ignore[method-assign]

        logos = Logos(registry=registry, _curator=curator)

        # void.* paths should be exempt
        result = await logos.invoke("void.entropy.manifest", as_umwelt(mock_umwelt))

        # Filter was called (Logos calls it), but curator internally exempts
        assert filter_called
        # Result should still be valid
        assert isinstance(result, BasicRendering)

    def test_create_logos_with_curator(self) -> None:
        """create_logos() accepts curator parameter."""
        from protocols.agentese.middleware.curator import WundtCurator

        curator = WundtCurator()
        logos = create_logos(curator=curator)

        assert logos._curator is curator

    def test_create_logos_without_curator(self) -> None:
        """create_logos() without curator has None curator."""
        logos = create_logos()
        assert logos._curator is None


# === Auto-Curator Tests (PAYADOR v2.5) ===


class TestAutoCurator:
    """Tests for automatic curator application on GENERATION aspects."""

    def test_generation_aspects_list_is_complete(self) -> None:
        """Verify all GENERATION aspects are in the auto-curate list."""
        logos = Logos()
        expected_generation = {
            "define",
            "spawn",
            "fork",
            "dream",
            "refine",
            "dialectic",
        }
        for aspect in expected_generation:
            assert logos._should_auto_curate(aspect), (
                f"{aspect} should be in GENERATION aspects"
            )

    def test_perception_aspects_not_auto_curated(self) -> None:
        """PERCEPTION aspects should NOT be auto-curated."""
        logos = Logos()
        perception_aspects = ["manifest", "witness", "sense", "map"]
        for aspect in perception_aspects:
            assert not logos._should_auto_curate(aspect), (
                f"{aspect} should NOT be auto-curated"
            )

    def test_mutation_aspects_not_auto_curated(self) -> None:
        """MUTATION aspects should NOT be auto-curated."""
        logos = Logos()
        mutation_aspects = ["transform", "renovate", "evolve", "repair"]
        for aspect in mutation_aspects:
            assert not logos._should_auto_curate(aspect), (
                f"{aspect} should NOT be auto-curated"
            )

    def test_blend_is_auto_curated(self) -> None:
        """blend is a GENERATION aspect and should be auto-curated."""
        logos = Logos()
        assert logos._should_auto_curate("blend")

    def test_solve_is_auto_curated(self) -> None:
        """solve (pataphysics) is a GENERATION aspect and should be auto-curated."""
        logos = Logos()
        assert logos._should_auto_curate("solve")

    @pytest.mark.asyncio
    async def test_auto_curate_applies_wundt_filter(
        self, mock_umwelt: MockUmwelt
    ) -> None:
        """_auto_curate should apply Wundt filtering."""
        logos = Logos()

        # String result should pass through curator
        result = await logos._auto_curate(
            "This is a test artifact with moderate complexity.",
            as_umwelt(mock_umwelt),
            "concept.test.define",
        )

        # Result should be unchanged (passes Wundt curve)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_auto_curate_conservative_thresholds(
        self, mock_umwelt: MockUmwelt
    ) -> None:
        """Auto-curator should use conservative (permissive) thresholds."""
        # Very simple content should pass conservative thresholds
        logos = Logos()

        result = await logos._auto_curate(
            "Simple.",  # Very boring content
            as_umwelt(mock_umwelt),
            "concept.test.define",
        )

        # Conservative thresholds (0.15 low) should pass short content
        assert result is not None

    @pytest.mark.asyncio
    async def test_generation_aspect_triggers_auto_curation(
        self, logos_with_nodes: Logos, mock_umwelt: MockUmwelt
    ) -> None:
        """GENERATION aspect without explicit curator triggers auto-curation flow."""
        # Directly test that _should_auto_curate returns True for generation aspects
        # and _auto_curate is called internally
        logos = logos_with_nodes

        # Verify the auto-curate logic is triggered for GENERATION aspects
        assert logos._should_auto_curate("define") is True
        assert logos._should_auto_curate("blend") is True
        assert logos._should_auto_curate("refine") is True

        # Verify non-GENERATION aspects don't trigger auto-curation
        assert logos._should_auto_curate("manifest") is False

        # Test _auto_curate directly returns filtered result
        # Use a string input to avoid complexity in dict depth calculation
        result = await logos._auto_curate(
            "This is a test definition with some content for curation.",
            as_umwelt(mock_umwelt),
            "concept.test.define",
        )
        assert result is not None

    @pytest.mark.asyncio
    async def test_explicit_curator_skips_auto_curation(
        self, mock_umwelt: MockUmwelt
    ) -> None:
        """When explicit curator is set, auto-curator should NOT be used."""
        from unittest.mock import AsyncMock, MagicMock

        registry = SimpleRegistry()
        # Use house with manifest (which we control)
        node = PlaceholderNode(
            handle="world.house",
        )
        registry.register("world.house", node)

        # Create mock curator
        mock_curator = MagicMock()
        mock_curator.filter = AsyncMock(return_value="explicit_curator_result")

        logos = Logos(registry=registry, _curator=mock_curator)

        # Invoke manifest - even though not a GENERATION aspect,
        # explicit curator should be called
        result = await logos.invoke(
            "world.house.manifest",
            as_umwelt(mock_umwelt),
        )

        # Mock curator should be called
        mock_curator.filter.assert_called_once()
        assert result == "explicit_curator_result"

    def test_generation_aspects_complete_set(self) -> None:
        """Verify _GENERATION_ASPECTS contains expected aspects."""
        logos = Logos()

        # Core GENERATION aspects from affordances.py
        expected = {"define", "spawn", "fork", "dream", "refine", "dialectic", "blend"}
        for aspect in expected:
            assert aspect in logos._GENERATION_ASPECTS, f"Missing: {aspect}"

        # Also includes solve (pataphysics generates creative content)
        assert "solve" in logos._GENERATION_ASPECTS
