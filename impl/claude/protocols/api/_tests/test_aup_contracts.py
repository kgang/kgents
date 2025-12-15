"""
AGENTESE Universal Protocol Contract Tests.

These tests verify the CONTRACT layer, not the implementation.
They ensure:
1. Pydantic models serialize/deserialize correctly
2. Bridge protocol signatures are correctly typed
3. Law assertions can be called
4. Error taxonomy is complete

DEVELOP Phase: These are stub tests that define expectations.
Implementation tests will be added in IMPLEMENT phase.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

# Skip all tests if dependencies not available
pytest.importorskip("pydantic")


class TestSerializerContracts:
    """Tests for Pydantic model contracts."""

    def test_observer_context_defaults(self) -> None:
        """ObserverContext has sensible defaults."""
        from protocols.api.serializers import ObserverContext

        observer = ObserverContext()

        assert observer.archetype == "viewer"
        assert observer.id == "anonymous"
        assert observer.capabilities == []

    def test_observer_context_custom(self) -> None:
        """ObserverContext accepts custom values."""
        from protocols.api.serializers import ObserverContext

        observer = ObserverContext(
            archetype="architect",
            id="user-123",
            capabilities=["define", "spawn"],
        )

        assert observer.archetype == "architect"
        assert observer.id == "user-123"
        assert observer.capabilities == ["define", "spawn"]

    def test_response_meta_required_fields(self) -> None:
        """ResponseMeta requires observer and span_id."""
        from protocols.api.serializers import ResponseMeta

        meta = ResponseMeta(
            observer="architect",
            span_id="abc123",
        )

        assert meta.observer == "architect"
        assert meta.span_id == "abc123"
        assert isinstance(meta.timestamp, datetime)
        assert meta.duration_ms is None
        assert meta.laws_verified == []

    def test_agentese_request_minimal(self) -> None:
        """AgenteseRequest works with minimal input."""
        from protocols.api.serializers import AgenteseRequest

        request = AgenteseRequest()

        assert request.kwargs == {}
        assert request.entropy_budget == 0.0
        assert request.observer is None

    def test_agentese_response_structure(self) -> None:
        """AgenteseResponse has correct structure."""
        from protocols.api.serializers import (
            AgenteseResponse,
            ResponseMeta,
        )

        response = AgenteseResponse(
            handle="world.field.manifest",
            result={"test": "data"},
            meta=ResponseMeta(
                observer="viewer",
                span_id="span-001",
            ),
        )

        assert response.handle == "world.field.manifest"
        assert response.result == {"test": "data"}
        assert response.meta.observer == "viewer"

    def test_composition_request_paths_required(self) -> None:
        """CompositionRequest requires at least one path."""
        from protocols.api.serializers import CompositionRequest

        # Valid with one path
        request = CompositionRequest(paths=["world.field.manifest"])
        assert len(request.paths) == 1

        # Multiple paths
        request = CompositionRequest(
            paths=["world.doc.manifest", "concept.sum.refine"],
        )
        assert len(request.paths) == 2

    def test_composition_response_includes_trace(self) -> None:
        """CompositionResponse includes pipeline trace."""
        from protocols.api.serializers import (
            CompositionResponse,
            PipelineStep,
            ResponseMeta,
        )

        response = CompositionResponse(
            result="final result",
            pipeline_trace=[
                PipelineStep(
                    path="world.doc.manifest",
                    span_id="span-001",
                    duration_ms=50,
                ),
                PipelineStep(
                    path="concept.sum.refine",
                    span_id="span-002",
                    duration_ms=100,
                ),
            ],
            laws_verified=["identity", "associativity"],
            meta=ResponseMeta(
                observer="developer",
                span_id="compose-span",
            ),
        )

        assert len(response.pipeline_trace) == 2
        assert response.laws_verified == ["identity", "associativity"]

    def test_law_verification_result_properties(self) -> None:
        """LawVerificationResult has all_laws_hold property."""
        from protocols.api.serializers import LawVerificationResult

        # All laws hold
        result = LawVerificationResult(
            identity_holds=True,
            associativity_holds=True,
            errors=[],
        )
        assert result.all_laws_hold is True

        # One law fails
        result = LawVerificationResult(
            identity_holds=True,
            associativity_holds=False,
            errors=["Associativity failed"],
        )
        assert result.all_laws_hold is False


class TestErrorTaxonomy:
    """Tests for error taxonomy completeness."""

    def test_all_error_codes_defined(self) -> None:
        """All error codes are defined in the type."""
        from protocols.api.serializers import ErrorCode

        # ErrorCode should be a Literal type with these values
        expected_codes = {
            "PATH_NOT_FOUND",
            "AFFORDANCE_DENIED",
            "OBSERVER_REQUIRED",
            "SYNTAX_ERROR",
            "LAW_VIOLATION",
            "BUDGET_EXHAUSTED",
            "COMPOSITION_ERROR",
            "INTERNAL_ERROR",
        }

        # We can't directly get Literal values, so we check via the mapping
        from protocols.api.bridge import ERROR_HTTP_STATUS

        assert set(ERROR_HTTP_STATUS.keys()) == expected_codes

    def test_error_response_structure(self) -> None:
        """ErrorResponse has all required fields."""
        from protocols.api.serializers import ErrorResponse

        error = ErrorResponse(
            error="Path not found",
            code="PATH_NOT_FOUND",
            path="world.nonexistent.manifest",
            suggestion="Check the path spelling",
            available=["world.field", "world.house"],
            why="No implementation in registry",
        )

        assert error.error == "Path not found"
        assert error.code == "PATH_NOT_FOUND"
        assert error.path == "world.nonexistent.manifest"
        assert error.suggestion is not None
        assert error.available is not None
        assert error.why is not None

    def test_http_status_mapping_complete(self) -> None:
        """All error codes map to HTTP status codes."""
        from protocols.api.bridge import ERROR_HTTP_STATUS, get_http_status

        # Test specific mappings
        assert get_http_status("PATH_NOT_FOUND") == 404
        assert get_http_status("AFFORDANCE_DENIED") == 403
        assert get_http_status("OBSERVER_REQUIRED") == 401
        assert get_http_status("SYNTAX_ERROR") == 400
        assert get_http_status("LAW_VIOLATION") == 422
        assert get_http_status("BUDGET_EXHAUSTED") == 402
        assert get_http_status("INTERNAL_ERROR") == 500

    def test_suggestions_defined_for_all_codes(self) -> None:
        """All error codes have default suggestions."""
        from protocols.api.bridge import ERROR_SUGGESTIONS, get_default_suggestion

        for code in ERROR_SUGGESTIONS:
            suggestion = get_default_suggestion(code)  # type: ignore[arg-type]
            assert suggestion, f"No suggestion for {code}"
            assert len(suggestion) > 10, f"Suggestion too short for {code}"


class TestSSETypes:
    """Tests for SSE streaming types."""

    def test_sse_chunk_structure(self) -> None:
        """SSEChunk has correct structure."""
        from protocols.api.serializers import SSEChunk

        chunk = SSEChunk(
            type="response",
            content="Hello ",
            partial=True,
            index=0,
        )

        assert chunk.type == "response"
        assert chunk.content == "Hello "
        assert chunk.partial is True
        assert chunk.index == 0

    def test_sse_complete_event_structure(self) -> None:
        """SSECompleteEvent has correct structure."""
        from protocols.api.serializers import SSECompleteEvent

        event = SSECompleteEvent(
            result="Complete response",
            span_id="span-001",
            chunks_count=5,
            duration_ms=150,
        )

        assert event.result == "Complete response"
        assert event.span_id == "span-001"
        assert event.chunks_count == 5
        assert event.duration_ms == 150

    def test_sse_event_serializes(self) -> None:
        """SSEEvent serializes to wire format."""
        from protocols.api.bridge import SSEEvent
        from protocols.api.serializers import SSEChunk

        chunk = SSEChunk(type="response", content="test", partial=True, index=0)
        event = SSEEvent(event="chunk", data=chunk)

        serialized = event.serialize()

        assert "event: chunk" in serialized
        assert "data:" in serialized
        assert "\n\n" in serialized


class TestWebSocketTypes:
    """Tests for WebSocket message types."""

    def test_ws_subscribe_message(self) -> None:
        """WSSubscribeMessage has correct structure."""
        from protocols.api.serializers import WSSubscribeMessage

        msg = WSSubscribeMessage(
            channel="garden",
            filter={"archetype": "architect"},
        )

        assert msg.type == "subscribe"
        assert msg.channel == "garden"
        assert msg.filter == {"archetype": "architect"}

    def test_ws_invoke_message(self) -> None:
        """WSInvokeMessage has correct structure."""
        from protocols.api.serializers import ObserverContext, WSInvokeMessage

        msg = WSInvokeMessage(
            id="req-001",
            handle="world.field.manifest",
            observer=ObserverContext(archetype="architect"),
            kwargs={"depth": 3},
        )

        assert msg.type == "invoke"
        assert msg.id == "req-001"
        assert msg.handle == "world.field.manifest"
        assert msg.observer.archetype == "architect"

    def test_ws_state_update(self) -> None:
        """WSStateUpdate has correct structure."""
        from protocols.api.serializers import WSStateUpdate

        update = WSStateUpdate(
            channel="garden",
            data={"entities": [], "pheromones": []},
        )

        assert update.type == "state_update"
        assert update.channel == "garden"
        assert "entities" in update.data

    def test_ws_invoke_result_success(self) -> None:
        """WSInvokeResult for success case."""
        from protocols.api.serializers import ResponseMeta, WSInvokeResult

        result = WSInvokeResult(
            id="req-001",
            success=True,
            result={"data": "test"},
            meta=ResponseMeta(observer="viewer", span_id="span-001"),
        )

        assert result.type == "invoke_result"
        assert result.success is True
        assert result.result == {"data": "test"}
        assert result.error is None

    def test_ws_invoke_result_error(self) -> None:
        """WSInvokeResult for error case."""
        from protocols.api.serializers import ErrorResponse, WSInvokeResult

        result = WSInvokeResult(
            id="req-001",
            success=False,
            error=ErrorResponse(
                error="Path not found",
                code="PATH_NOT_FOUND",
            ),
        )

        assert result.success is False
        assert result.error is not None
        assert result.error.code == "PATH_NOT_FOUND"


class TestGardenStateTypes:
    """Tests for garden/town state types."""

    def test_entity_state(self) -> None:
        """EntityState has correct structure."""
        from protocols.api.serializers import EntityState

        entity = EntityState(
            id="agent-001",
            glyph="🌱",
            x=100.0,
            y=200.0,
            color="#00ff00",
            archetype="citizen",
            phase="sensing",
        )

        assert entity.id == "agent-001"
        assert entity.glyph == "🌱"
        assert entity.x == 100.0
        assert entity.y == 200.0

    def test_pheromone_state(self) -> None:
        """PheromoneState has correct structure."""
        from protocols.api.serializers import PheromoneState

        pheromone = PheromoneState(
            x=150.0,
            y=250.0,
            radius=20.0,
            color="#ff0000",
            intensity=0.7,
            type="attraction",
        )

        assert pheromone.x == 150.0
        assert pheromone.intensity == 0.7

    def test_garden_state_complete(self) -> None:
        """GardenState combines entities and pheromones."""
        from protocols.api.serializers import (
            EntityState,
            GardenState,
            PheromoneState,
        )

        garden = GardenState(
            entities=[
                EntityState(id="a1", glyph="A", x=0, y=0),
                EntityState(id="a2", glyph="B", x=10, y=10),
            ],
            pheromones=[
                PheromoneState(x=5, y=5, radius=3, color="#fff", intensity=0.5),
            ],
            entropy=0.3,
            tick=42,
        )

        assert len(garden.entities) == 2
        assert len(garden.pheromones) == 1
        assert garden.entropy == 0.3
        assert garden.tick == 42


class TestBridgeProtocol:
    """Tests for AgenteseBridgeProtocol contract."""

    @pytest.mark.asyncio
    async def test_stub_bridge_invoke(self) -> None:
        """StubAgenteseBridge implements invoke."""
        from protocols.api.bridge import StubAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = StubAgenteseBridge()
        observer = ObserverContext(archetype="developer")

        response = await bridge.invoke("world.field.manifest", observer)

        assert response.handle == "world.field.manifest"
        assert response.meta.observer == "developer"
        assert "stub" in response.result

    @pytest.mark.asyncio
    async def test_stub_bridge_compose(self) -> None:
        """StubAgenteseBridge implements compose."""
        from protocols.api.bridge import StubAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = StubAgenteseBridge()
        observer = ObserverContext()

        response = await bridge.compose(
            paths=["world.doc.manifest", "concept.sum.refine"],
            observer=observer,
        )

        assert len(response.pipeline_trace) == 2
        assert "identity" in response.laws_verified
        assert "associativity" in response.laws_verified

    @pytest.mark.asyncio
    async def test_stub_bridge_stream(self) -> None:
        """StubAgenteseBridge implements stream."""
        from protocols.api.bridge import StubAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = StubAgenteseBridge()
        observer = ObserverContext()

        events = []
        async for event in bridge.stream("self.soul.challenge", observer):
            events.append(event)

        assert len(events) == 3  # 2 chunks + 1 done
        assert events[-1].event == "done"

    @pytest.mark.asyncio
    async def test_stub_bridge_verify_laws(self) -> None:
        """StubAgenteseBridge implements verify_laws."""
        from protocols.api.bridge import StubAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = StubAgenteseBridge()
        observer = ObserverContext()

        result = await bridge.verify_laws(
            composition=["a.b.c", "d.e.f"],
            observer=observer,
        )

        assert result.identity_holds is True
        assert result.associativity_holds is True
        assert result.all_laws_hold is True

    @pytest.mark.asyncio
    async def test_stub_bridge_resolve(self) -> None:
        """StubAgenteseBridge implements resolve."""
        from protocols.api.bridge import StubAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = StubAgenteseBridge()
        observer = ObserverContext()

        result = await bridge.resolve("world.field", observer)

        assert result["path"] == "world.field"
        assert result["context"] == "world"
        assert result["holon"] == "field"
        assert result["exists"] is True

    @pytest.mark.asyncio
    async def test_stub_bridge_affordances(self) -> None:
        """StubAgenteseBridge implements affordances."""
        from protocols.api.bridge import StubAgenteseBridge
        from protocols.api.serializers import ObserverContext

        bridge = StubAgenteseBridge()
        observer = ObserverContext()

        result = await bridge.affordances("world.field", observer)

        assert "manifest" in result
        assert "witness" in result


class TestLawAssertions:
    """Tests for category law assertion functions."""

    @pytest.mark.asyncio
    async def test_assert_identity_law(self) -> None:
        """assert_identity_law returns LawVerificationResult."""
        from protocols.api.bridge import StubAgenteseBridge, assert_identity_law
        from protocols.api.serializers import ObserverContext

        bridge = StubAgenteseBridge()
        observer = ObserverContext()

        result = await assert_identity_law(
            bridge,
            "world.field.manifest",
            observer,
        )

        assert result.identity_holds is True
        assert result.locus == "world.field.manifest"

    @pytest.mark.asyncio
    async def test_assert_associativity_law(self) -> None:
        """assert_associativity_law returns LawVerificationResult."""
        from protocols.api.bridge import StubAgenteseBridge, assert_associativity_law
        from protocols.api.serializers import ObserverContext

        bridge = StubAgenteseBridge()
        observer = ObserverContext()

        result = await assert_associativity_law(
            bridge,
            "a.b.c",
            "d.e.f",
            "g.h.i",
            observer,
        )

        assert result.associativity_holds is True
        assert "a.b.c >> d.e.f >> g.h.i" in result.locus

    @pytest.mark.asyncio
    async def test_assert_observer_polymorphism(self) -> None:
        """assert_observer_polymorphism checks different observers."""
        from protocols.api.bridge import (
            StubAgenteseBridge,
            assert_observer_polymorphism,
        )
        from protocols.api.serializers import ObserverContext

        bridge = StubAgenteseBridge()
        observer1 = ObserverContext(archetype="viewer")
        observer2 = ObserverContext(archetype="architect")

        works, explanation = await assert_observer_polymorphism(
            bridge,
            "world.field.manifest",
            observer1,
            observer2,
        )

        assert works is True
        assert "observers" in explanation.lower()


class TestErrorHelpers:
    """Tests for error helper functions."""

    def test_create_error_response(self) -> None:
        """create_error_response creates ErrorResponse."""
        from protocols.api.bridge import create_error_response

        error = create_error_response(
            "PATH_NOT_FOUND",
            "Path 'world.missing' not found",
            path="world.missing",
            suggestion="Check spelling",
            available=["world.field", "world.house"],
            why="No spec file exists",
        )

        assert error.code == "PATH_NOT_FOUND"
        assert error.path == "world.missing"
        assert error.suggestion == "Check spelling"
        assert len(error.available or []) == 2
