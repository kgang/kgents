"""
LogosAgenteseBridge Unit Tests.

Tests the bridge implementation in isolation:
1. Observer → Umwelt translation
2. Exception → ErrorResponse mapping
3. Law verification
4. SSE event generation
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# Skip if pydantic not available
pytest.importorskip("pydantic")


class TestObserverTranslation:
    """Tests for _observer_to_umwelt translation."""

    def test_translates_archetype(self) -> None:
        """Observer archetype becomes DNA archetype."""
        from protocols.api.bridge_impl import _observer_to_umwelt
        from protocols.api.serializers import ObserverContext

        observer = ObserverContext(
            archetype="architect",
            id="user-123",
            capabilities=[],
        )

        umwelt = _observer_to_umwelt(observer)

        assert umwelt.dna.archetype == "architect"
        assert umwelt.dna.name == "user-123"

    def test_translates_capabilities(self) -> None:
        """Observer capabilities become DNA capabilities tuple."""
        from protocols.api.bridge_impl import _observer_to_umwelt
        from protocols.api.serializers import ObserverContext

        observer = ObserverContext(
            archetype="developer",
            id="dev-1",
            capabilities=["define", "spawn", "dialectic"],
        )

        umwelt = _observer_to_umwelt(observer)

        assert umwelt.dna.capabilities == ("define", "spawn", "dialectic")

    def test_handles_defaults(self) -> None:
        """Default observer values are preserved."""
        from protocols.api.bridge_impl import _observer_to_umwelt
        from protocols.api.serializers import ObserverContext

        observer = ObserverContext()  # All defaults

        umwelt = _observer_to_umwelt(observer)

        assert umwelt.dna.archetype == "viewer"
        assert umwelt.dna.name == "anonymous"
        assert umwelt.dna.capabilities == ()


class TestExceptionMapping:
    """Tests for _exception_to_error_code mapping."""

    def test_maps_path_not_found(self) -> None:
        """PathNotFoundError maps to PATH_NOT_FOUND."""
        from protocols.api.bridge_impl import _exception_to_error_code

        class PathNotFoundError(Exception):
            pass

        exc = PathNotFoundError("not found")
        code = _exception_to_error_code(exc)

        assert code == "PATH_NOT_FOUND"

    def test_maps_affordance_error(self) -> None:
        """AffordanceError maps to AFFORDANCE_DENIED."""
        from protocols.api.bridge_impl import _exception_to_error_code

        class AffordanceError(Exception):
            pass

        exc = AffordanceError("denied")
        code = _exception_to_error_code(exc)

        assert code == "AFFORDANCE_DENIED"

    def test_maps_unknown_to_internal(self) -> None:
        """Unknown exceptions map to INTERNAL_ERROR."""
        from protocols.api.bridge_impl import _exception_to_error_code

        exc = ValueError("something went wrong")
        code = _exception_to_error_code(exc)

        assert code == "INTERNAL_ERROR"

    def test_exception_to_response_includes_attributes(self) -> None:
        """ErrorResponse includes exception attributes."""
        from protocols.api.bridge_impl import _exception_to_error_response

        class TestError(Exception):
            def __init__(self) -> None:
                self.available = ["a", "b"]
                self.why = "because"
                self.suggestion = "try this"
                super().__init__("Test error")

        exc = TestError()
        error = _exception_to_error_response(exc, path="test.path", span_id="span-1")

        assert error.path == "test.path"
        assert error.span_id == "span-1"
        assert error.available == ["a", "b"]
        assert error.why == "because"
        assert error.suggestion == "try this"


class TestBridgeInvoke:
    """Tests for LogosAgenteseBridge.invoke()."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos."""
        logos = MagicMock()

        async def mock_invoke(
            path: str, observer: Any, **kwargs: Any
        ) -> dict[str, Any]:
            return {"invoked": path, "kwargs": kwargs}

        logos.invoke = AsyncMock(side_effect=mock_invoke)
        logos.is_resolved.return_value = False

        return logos

    @pytest.mark.asyncio
    async def test_invoke_returns_response_envelope(
        self, mock_logos: MagicMock
    ) -> None:
        """Invoke returns proper AgenteseResponse structure."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext(archetype="developer")

        response = await bridge.invoke("world.field.manifest", observer)

        assert response.handle == "world.field.manifest"
        assert isinstance(response.result, dict)
        assert response.meta.observer == "developer"
        assert response.meta.span_id is not None
        assert response.meta.timestamp is not None
        assert response.meta.duration_ms is not None
        assert response.meta.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_invoke_passes_kwargs(self, mock_logos: MagicMock) -> None:
        """Invoke passes kwargs to Logos."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        await bridge.invoke(
            "concept.justice.refine",
            observer,
            {"challenge": "test", "depth": 3},
        )

        mock_logos.invoke.assert_called_once()
        call_kwargs = mock_logos.invoke.call_args[1]
        assert call_kwargs["challenge"] == "test"
        assert call_kwargs["depth"] == 3

    @pytest.mark.asyncio
    async def test_invoke_raises_bridge_error(self, mock_logos: MagicMock) -> None:
        """Invoke raises BridgeError on Logos exception."""
        from protocols.agentese.exceptions import PathNotFoundError
        from protocols.api.bridge_impl import BridgeError, LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        mock_logos.invoke.side_effect = PathNotFoundError(
            "not found", path="missing.path"
        )

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        with pytest.raises(BridgeError) as exc_info:
            await bridge.invoke("missing.path.manifest", observer)

        assert exc_info.value.error.code == "PATH_NOT_FOUND"


class TestBridgeCompose:
    """Tests for LogosAgenteseBridge.compose()."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos for compose tests."""
        logos = MagicMock()

        call_count = 0

        async def mock_invoke(
            path: str, observer: Any, **kwargs: Any
        ) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            return {"step": call_count, "path": path}

        logos.invoke = AsyncMock(side_effect=mock_invoke)

        mock_composed = MagicMock()
        logos.compose.return_value = mock_composed

        return logos

    @pytest.mark.asyncio
    async def test_compose_returns_response_with_trace(
        self, mock_logos: MagicMock
    ) -> None:
        """Compose returns CompositionResponse with pipeline trace."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        response = await bridge.compose(
            paths=["world.a.manifest", "concept.b.refine", "self.c.engram"],
            observer=observer,
            emit_law_check=True,
        )

        assert len(response.pipeline_trace) == 3
        assert response.pipeline_trace[0].path == "world.a.manifest"
        assert response.pipeline_trace[1].path == "concept.b.refine"
        assert response.pipeline_trace[2].path == "self.c.engram"

    @pytest.mark.asyncio
    async def test_compose_verifies_laws(self, mock_logos: MagicMock) -> None:
        """Compose includes law verification when emit_law_check=True."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        response = await bridge.compose(
            paths=["world.a.manifest", "concept.b.refine"],
            observer=observer,
            emit_law_check=True,
        )

        assert "identity" in response.laws_verified
        assert "associativity" in response.laws_verified

    @pytest.mark.asyncio
    async def test_compose_skips_laws_when_disabled(
        self, mock_logos: MagicMock
    ) -> None:
        """Compose skips law verification when emit_law_check=False."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        response = await bridge.compose(
            paths=["world.a.manifest"],
            observer=observer,
            emit_law_check=False,
        )

        assert response.laws_verified == []


class TestBridgeStream:
    """Tests for LogosAgenteseBridge.stream()."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos for stream tests."""
        logos = MagicMock()

        async def mock_invoke(path: str, observer: Any, **kwargs: Any) -> str:
            return "Streamed result"

        logos.invoke = AsyncMock(side_effect=mock_invoke)

        return logos

    @pytest.mark.asyncio
    async def test_stream_yields_events(self, mock_logos: MagicMock) -> None:
        """Stream yields SSE events."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        events = []
        async for event in bridge.stream("world.field.manifest", observer):
            events.append(event)

        # Should have chunk + done
        assert len(events) >= 1
        assert events[-1].event == "done"

    @pytest.mark.asyncio
    async def test_stream_serializes_events(self, mock_logos: MagicMock) -> None:
        """Stream events serialize to SSE wire format."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        events = []
        async for event in bridge.stream("world.field.manifest", observer):
            events.append(event)

        # All events should serialize
        for event in events:
            serialized = event.serialize()
            assert "event:" in serialized
            assert "data:" in serialized
            assert "\n\n" in serialized


class TestBridgeVerifyLaws:
    """Tests for LogosAgenteseBridge.verify_laws()."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos for law verification."""
        logos = MagicMock()

        # Consistent results for identity check
        async def mock_invoke(
            path: str, observer: Any, **kwargs: Any
        ) -> dict[str, Any]:
            return {"path": path, "stable": True}

        logos.invoke = AsyncMock(side_effect=mock_invoke)

        mock_composed = MagicMock()

        async def mock_composed_invoke(observer: Any, initial_input: Any = None) -> Any:
            return {"composed": True}

        mock_composed.invoke = AsyncMock(side_effect=mock_composed_invoke)
        logos.compose.return_value = mock_composed

        return logos

    @pytest.mark.asyncio
    async def test_verify_laws_checks_identity(self, mock_logos: MagicMock) -> None:
        """verify_laws checks identity for each path."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        result = await bridge.verify_laws(
            composition=["world.a.manifest"],
            observer=observer,
        )

        # Should invoke twice for identity check
        assert mock_logos.invoke.call_count == 2
        assert result.identity_holds is True

    @pytest.mark.asyncio
    async def test_verify_laws_checks_associativity(
        self, mock_logos: MagicMock
    ) -> None:
        """verify_laws checks associativity for 3+ paths."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        result = await bridge.verify_laws(
            composition=["world.a.manifest", "concept.b.refine", "self.c.engram"],
            observer=observer,
        )

        # Should check associativity
        assert result.associativity_holds is True


class TestBridgeAffordances:
    """Tests for LogosAgenteseBridge.affordances()."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos with affordances."""
        logos = MagicMock()

        mock_node = MagicMock()
        mock_node.affordances.return_value = ["manifest", "witness", "define", "spawn"]
        logos.resolve.return_value = mock_node

        return logos

    @pytest.mark.asyncio
    async def test_affordances_returns_list(self, mock_logos: MagicMock) -> None:
        """affordances returns list from node."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext(archetype="architect")

        result = await bridge.affordances("world.house", observer)

        assert "manifest" in result
        assert "witness" in result
        assert "define" in result

    @pytest.mark.asyncio
    async def test_affordances_handles_missing_path(
        self, mock_logos: MagicMock
    ) -> None:
        """affordances returns empty list for missing paths."""
        from protocols.agentese.exceptions import PathNotFoundError
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        mock_logos.resolve.side_effect = PathNotFoundError("not found")

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        result = await bridge.affordances("world.missing", observer)

        assert result == []


class TestBridgeResolve:
    """Tests for LogosAgenteseBridge.resolve()."""

    @pytest.fixture
    def mock_logos(self) -> MagicMock:
        """Create a mock Logos for resolve."""
        logos = MagicMock()

        mock_node = MagicMock()
        mock_node.affordances.return_value = ["manifest", "witness"]
        logos.resolve.return_value = mock_node

        return logos

    @pytest.mark.asyncio
    async def test_resolve_returns_metadata(self, mock_logos: MagicMock) -> None:
        """resolve returns path metadata."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        result = await bridge.resolve("world.field", observer)

        assert result["path"] == "world.field"
        assert result["context"] == "world"
        assert result["holon"] == "field"
        assert result["exists"] is True
        assert "affordances" in result

    @pytest.mark.asyncio
    async def test_resolve_handles_missing(self, mock_logos: MagicMock) -> None:
        """resolve returns exists=False for missing paths."""
        from protocols.agentese.exceptions import PathNotFoundError
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        mock_logos.resolve.side_effect = PathNotFoundError("not found")

        bridge = LogosAgenteseBridge(logos=mock_logos, telemetry_enabled=False)
        observer = ObserverContext()

        result = await bridge.resolve("world.missing", observer)

        assert result["exists"] is False


class TestResultSerialization:
    """Tests for _serialize_result helper."""

    def test_serializes_pydantic_model(self) -> None:
        """Pydantic models are serialized via model_dump."""
        from protocols.api.bridge_impl import LogosAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = LogosAgenteseBridge(logos=MagicMock(), telemetry_enabled=False)

        # ObserverContext is a Pydantic model
        observer = ObserverContext(archetype="test")
        result = bridge._serialize_result(observer)

        assert isinstance(result, dict)
        assert result["archetype"] == "test"

    def test_serializes_dict_passthrough(self) -> None:
        """Dicts pass through unchanged."""
        from protocols.api.bridge_impl import LogosAgenteseBridge

        bridge = LogosAgenteseBridge(logos=MagicMock(), telemetry_enabled=False)

        data = {"key": "value", "number": 42}
        result = bridge._serialize_result(data)

        assert result == data

    def test_serializes_primitives_passthrough(self) -> None:
        """Primitives pass through unchanged."""
        from protocols.api.bridge_impl import LogosAgenteseBridge

        bridge = LogosAgenteseBridge(logos=MagicMock(), telemetry_enabled=False)

        assert bridge._serialize_result("string") == "string"
        assert bridge._serialize_result(42) == 42
        assert bridge._serialize_result(3.14) == 3.14
        assert bridge._serialize_result(True) is True
        assert bridge._serialize_result(None) is None


class TestResultEquivalence:
    """Tests for _results_equivalent helper."""

    def test_equal_dicts_are_equivalent(self) -> None:
        """Identical dicts are equivalent."""
        from protocols.api.bridge_impl import LogosAgenteseBridge

        bridge = LogosAgenteseBridge(logos=MagicMock(), telemetry_enabled=False)

        d1 = {"a": 1, "b": 2}
        d2 = {"a": 1, "b": 2}

        assert bridge._results_equivalent(d1, d2) is True

    def test_ignores_volatile_keys(self) -> None:
        """Volatile keys (timestamp, span_id) are ignored."""
        from protocols.api.bridge_impl import LogosAgenteseBridge

        bridge = LogosAgenteseBridge(logos=MagicMock(), telemetry_enabled=False)

        d1 = {"a": 1, "timestamp": "2025-01-01", "span_id": "abc"}
        d2 = {"a": 1, "timestamp": "2025-01-02", "span_id": "xyz"}

        assert bridge._results_equivalent(d1, d2) is True

    def test_different_values_not_equivalent(self) -> None:
        """Different values are not equivalent."""
        from protocols.api.bridge_impl import LogosAgenteseBridge

        bridge = LogosAgenteseBridge(logos=MagicMock(), telemetry_enabled=False)

        d1 = {"a": 1}
        d2 = {"a": 2}

        assert bridge._results_equivalent(d1, d2) is False
