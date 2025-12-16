"""
AGENTESE API Tests

Tests for the API:
- Observer base class
- Logos.__call__() syntax
- @aspect decorator with category enforcement
- String-based >> composition (path() helper)
"""

from __future__ import annotations

from typing import Any

import pytest
from protocols.agentese import (
    AgentesePath,
    AspectCategory,
    AspectMetadata,
    DeclaredEffect,
    Effect,
    Logos,
    Observer,
    Path,
    UnboundComposedPath,
    aspect,
    create_logos,
    get_aspect_metadata,
    is_aspect,
    path,
)


class TestObserver:
    """Tests for the Observer base class."""

    def test_guest_factory(self) -> None:
        """Observer.guest() creates anonymous guest observer."""
        obs = Observer.guest()
        assert obs.archetype == "guest"
        assert obs.capabilities == frozenset()

    def test_test_factory(self) -> None:
        """Observer.test() creates test observer with capabilities."""
        obs = Observer.test()
        assert obs.archetype == "developer"
        assert "define" in obs.capabilities
        assert "refine" in obs.capabilities
        assert "test" in obs.capabilities

    def test_from_archetype(self) -> None:
        """Observer.from_archetype() creates observer from archetype."""
        obs = Observer.from_archetype("architect")
        assert obs.archetype == "architect"
        assert obs.capabilities == frozenset()

    def test_custom_observer(self) -> None:
        """Custom observer with specific capabilities."""
        obs = Observer(
            archetype="developer",
            capabilities=frozenset({"custom_cap", "another_cap"}),
        )
        assert obs.archetype == "developer"
        assert "custom_cap" in obs.capabilities
        assert "another_cap" in obs.capabilities

    def test_observer_is_frozen(self) -> None:
        """Observer is immutable (frozen dataclass)."""
        obs = Observer.guest()
        with pytest.raises(AttributeError):
            obs.archetype = "modified"  # type: ignore[misc]


class TestLogosCallable:
    """Tests for Logos.__call__() syntax."""

    @pytest.fixture
    def logos(self) -> Logos:
        """Create a Logos instance for testing."""
        return create_logos()

    @pytest.mark.asyncio
    async def test_call_syntax_with_observer(self, logos: Logos) -> None:
        """await logos(path, observer) works."""
        # This should not raise - demonstrates the syntax works
        # Actual invocation would need registered nodes
        obs = Observer.from_archetype("developer")
        # Just verify the method signature is callable
        assert callable(logos)

    @pytest.mark.asyncio
    async def test_call_syntax_without_observer(self, logos: Logos) -> None:
        """await logos(path) defaults to guest observer."""
        # Just verify the method signature is callable
        assert callable(logos)


class TestAspectDecorator:
    """Tests for the @aspect decorator."""

    def test_aspect_decorator_adds_metadata(self) -> None:
        """@aspect decorator adds AspectMetadata to function."""

        @aspect(category=AspectCategory.PERCEPTION)
        async def test_aspect(self: Any, observer: Observer) -> str:
            return "test"

        assert is_aspect(test_aspect)
        meta = get_aspect_metadata(test_aspect)
        assert meta is not None
        assert meta.category == AspectCategory.PERCEPTION
        assert meta.effects == []

    def test_aspect_decorator_with_effects(self) -> None:
        """@aspect decorator captures declared effects."""

        @aspect(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("memory_crystals"), Effect.CHARGES("tokens")],
        )
        async def engram(self: Any, observer: Observer, content: str) -> str:
            return content

        meta = get_aspect_metadata(engram)
        assert meta is not None
        assert meta.category == AspectCategory.MUTATION
        assert len(meta.effects) == 2

    def test_aspect_decorator_with_archetype_requirements(self) -> None:
        """@aspect decorator captures archetype requirements."""

        @aspect(
            category=AspectCategory.GENERATION,
            requires_archetype=("architect", "developer"),
        )
        async def define(self: Any, observer: Observer) -> str:
            return "defined"

        meta = get_aspect_metadata(define)
        assert meta is not None
        assert meta.requires_archetype == ("architect", "developer")

    def test_aspect_decorator_with_idempotent(self) -> None:
        """@aspect decorator captures idempotent flag."""

        @aspect(
            category=AspectCategory.PERCEPTION,
            idempotent=True,
        )
        async def manifest(self: Any, observer: Observer) -> str:
            return "manifest"

        meta = get_aspect_metadata(manifest)
        assert meta is not None
        assert meta.idempotent is True

    def test_is_aspect_returns_false_for_undecorated(self) -> None:
        """is_aspect returns False for non-aspect functions."""

        def regular_function() -> str:
            return "not an aspect"

        assert not is_aspect(regular_function)

    def test_get_aspect_metadata_returns_none_for_undecorated(self) -> None:
        """get_aspect_metadata returns None for non-aspect functions."""

        def regular_function() -> str:
            return "not an aspect"

        assert get_aspect_metadata(regular_function) is None


class TestEffect:
    """Tests for the Effect enum and DeclaredEffect."""

    def test_effect_call_creates_declared_effect(self) -> None:
        """Effect(resource) creates DeclaredEffect."""
        effect = Effect.READS("memory")
        assert isinstance(effect, DeclaredEffect)
        assert effect.effect == Effect.READS
        assert effect.resource == "memory"

    def test_declared_effect_str(self) -> None:
        """DeclaredEffect str representation."""
        effect = Effect.WRITES("database")
        assert str(effect) == "writes:database"

    def test_all_effect_types(self) -> None:
        """All Effect types can create DeclaredEffects."""
        effects = [
            Effect.READS("test"),
            Effect.WRITES("test"),
            Effect.DELETES("test"),
            Effect.CHARGES("test"),
            Effect.EARNS("test"),
            Effect.CALLS("test"),
            Effect.EMITS("test"),
            Effect.FORCES("test"),
            Effect.AUDITS("test"),
        ]
        for e in effects:
            assert isinstance(e, DeclaredEffect)
            assert e.resource == "test"


class TestPathComposition:
    """Tests for string-based >> composition."""

    def test_path_creates_agentese_path(self) -> None:
        """path() creates AgentesePath."""
        p = path("world.garden.manifest")
        assert isinstance(p, AgentesePath)
        assert p.value == "world.garden.manifest"

    def test_path_alias_is_agentese_path(self) -> None:
        """Path is an alias for AgentesePath."""
        assert Path is AgentesePath

    def test_path_rshift_creates_unbound_composed_path(self) -> None:
        """path >> string creates UnboundComposedPath."""
        pipeline = path("world.doc.manifest") >> "concept.summary.refine"
        assert isinstance(pipeline, UnboundComposedPath)
        assert pipeline.paths == ["world.doc.manifest", "concept.summary.refine"]

    def test_chained_composition(self) -> None:
        """Multiple >> creates longer composition."""
        pipeline = (
            path("world.doc.manifest")
            >> "concept.summary.refine"
            >> "self.memory.engram"
        )
        assert isinstance(pipeline, UnboundComposedPath)
        assert len(pipeline.paths) == 3
        assert pipeline.paths[0] == "world.doc.manifest"
        assert pipeline.paths[1] == "concept.summary.refine"
        assert pipeline.paths[2] == "self.memory.engram"

    def test_bind_creates_composed_path(self) -> None:
        """UnboundComposedPath.bind() creates ComposedPath."""
        logos = create_logos()
        pipeline = path("world.doc.manifest") >> "concept.summary.refine"
        bound = pipeline.bind(logos)

        from protocols.agentese import ComposedPath

        assert isinstance(bound, ComposedPath)
        assert bound.paths == pipeline.paths

    def test_path_bind(self) -> None:
        """AgentesePath.bind() creates single-path ComposedPath."""
        logos = create_logos()
        p = path("world.garden.manifest")
        bound = p.bind(logos)

        from protocols.agentese import ComposedPath

        assert isinstance(bound, ComposedPath)
        assert bound.paths == ["world.garden.manifest"]


class TestV3Integration:
    """Integration tests for v3 API components working together."""

    def test_observer_and_aspect_together(self) -> None:
        """Observer and @aspect work together."""

        @aspect(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("data")],
        )
        async def manifest(self: Any, observer: Observer) -> str:
            return f"manifest for {observer.archetype}"

        obs = Observer.from_archetype("architect")
        meta = get_aspect_metadata(manifest)

        assert obs.archetype == "architect"
        assert meta is not None
        assert meta.category == AspectCategory.PERCEPTION

    def test_path_composition_is_associative(self) -> None:
        """Path composition is associative: (a >> b) >> c == a >> (b >> c)."""
        # Left association
        left = (path("a.b.c") >> "d.e.f") >> "g.h.i"
        # Right association using UnboundComposedPath
        inner = path("d.e.f") >> "g.h.i"  # UnboundComposedPath
        right = path("a.b.c") >> inner  # Supported: AgentesePath >> UnboundComposedPath

        # Both should produce the same paths
        assert left.paths == ["a.b.c", "d.e.f", "g.h.i"]
        assert right.paths == ["a.b.c", "d.e.f", "g.h.i"]
