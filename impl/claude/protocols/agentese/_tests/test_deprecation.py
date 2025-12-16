"""
Tests for AGENTESE Public API

Tests that the public API is correctly defined and accessible.
"""

from __future__ import annotations


class TestPublicAPI:
    """Tests for public API exports."""

    def test_exports_count(self) -> None:
        """__all__ has ~78 exports."""
        from protocols import agentese

        assert len(agentese.__all__) < 100
        assert len(agentese.__all__) > 50

    def test_core_symbols_in_all(self) -> None:
        """Core symbols are in __all__."""
        from protocols import agentese

        core_symbols = [
            "Logos",
            "create_logos",
            "Observer",
            "LogosNode",
            "path",
            "Path",
            "AgentesePath",
            "aspect",
            "Effect",
            "AspectCategory",
        ]
        for sym in core_symbols:
            assert sym in agentese.__all__, f"{sym} should be in __all__"

    def test_query_symbols_in_all(self) -> None:
        """Query system symbols are in __all__."""
        from protocols import agentese

        query_symbols = [
            "query",
            "QueryResult",
            "QueryBuilder",
            "QuerySyntaxError",
            "QueryBoundError",
        ]
        for sym in query_symbols:
            assert sym in agentese.__all__, f"{sym} should be in __all__"

    def test_subscription_symbols_in_all(self) -> None:
        """Subscription system symbols are in __all__."""
        from protocols import agentese

        sub_symbols = [
            "AgentesEvent",
            "EventType",
            "DeliveryMode",
            "Subscription",
            "SubscriptionManager",
        ]
        for sym in sub_symbols:
            assert sym in agentese.__all__, f"{sym} should be in __all__"

    def test_pipeline_symbols_in_all(self) -> None:
        """Pipeline symbols are in __all__."""
        from protocols import agentese

        pipeline_symbols = [
            "AspectPipeline",
            "PipelineResult",
            "create_pipeline",
        ]
        for sym in pipeline_symbols:
            assert sym in agentese.__all__, f"{sym} should be in __all__"


class TestRemovedV1Symbols:
    """Tests that v1 symbols are no longer accessible."""

    def test_pathparser_removed(self) -> None:
        """PathParser is no longer accessible (raises AttributeError)."""
        import pytest
        from protocols import agentese

        with pytest.raises(AttributeError, match="has no attribute 'PathParser'"):
            _ = agentese.PathParser  # type: ignore[attr-defined]

    def test_clause_removed(self) -> None:
        """Clause is no longer accessible."""
        import pytest
        from protocols import agentese

        with pytest.raises(AttributeError, match="has no attribute 'Clause'"):
            _ = agentese.Clause  # type: ignore[attr-defined]

    def test_phase_removed(self) -> None:
        """Phase is no longer accessible."""
        import pytest
        from protocols import agentese

        with pytest.raises(AttributeError, match="has no attribute 'Phase'"):
            _ = agentese.Phase  # type: ignore[attr-defined]

    def test_compose_removed(self) -> None:
        """compose() is no longer accessible (use >> instead)."""
        import pytest
        from protocols import agentese

        with pytest.raises(AttributeError, match="has no attribute 'compose'"):
            _ = agentese.compose  # type: ignore[attr-defined]

    def test_world_context_resolver_removed(self) -> None:
        """WorldContextResolver is no longer accessible."""
        import pytest
        from protocols import agentese

        with pytest.raises(
            AttributeError, match="has no attribute 'WorldContextResolver'"
        ):
            _ = agentese.WorldContextResolver  # type: ignore[attr-defined]


class TestImportability:
    """Tests that imports work correctly."""

    def test_core_imports_work(self) -> None:
        """Core imports work without warnings."""
        from protocols.agentese import (
            AgentesError,
            BasicRendering,
            Logos,
            PathNotFoundError,
            PathSyntaxError,
            WiredLogos,
            create_logos,
            create_minimal_wired_logos,
            create_wired_logos,
            wire_existing_logos,
        )

        assert Logos is not None
        assert create_logos is not None
        assert WiredLogos is not None

    def test_composition_imports_work(self) -> None:
        """Composition-related imports work."""
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

        assert Path is AgentesePath
        assert Observer is not None
        assert aspect is not None
