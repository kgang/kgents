"""Tests for Morpheus Gateway server and adapter."""

import pytest
from infra.morpheus.adapter import AdapterConfig, MockAdapter
from infra.morpheus.server import GatewayConfig, MorpheusGateway
from infra.morpheus.types import ChatMessage, ChatRequest, ChatResponse


class TestMockAdapter:
    """Tests for MockAdapter."""

    @pytest.mark.asyncio
    async def test_default_response(self) -> None:
        """Test mock returns default response."""
        adapter = MockAdapter()
        request = ChatRequest(
            model="test-model",
            messages=[ChatMessage(role="user", content="Hello")],
        )
        response = await adapter.complete(request)
        assert response.choices[0].message.content == "Mock response from Morpheus"

    @pytest.mark.asyncio
    async def test_queued_responses(self) -> None:
        """Test mock returns queued responses in order."""
        adapter = MockAdapter(responses=["First", "Second", "Third"])
        request = ChatRequest(
            model="test",
            messages=[ChatMessage(role="user", content="Hi")],
        )

        r1 = await adapter.complete(request)
        assert r1.choices[0].message.content == "First"

        r2 = await adapter.complete(request)
        assert r2.choices[0].message.content == "Second"

        r3 = await adapter.complete(request)
        assert r3.choices[0].message.content == "Third"

        # Falls back to default after queue exhausted
        r4 = await adapter.complete(request)
        assert r4.choices[0].message.content == "Mock response from Morpheus"

    @pytest.mark.asyncio
    async def test_history_tracking(self) -> None:
        """Test mock tracks request history."""
        adapter = MockAdapter()
        request1 = ChatRequest(
            model="model-1",
            messages=[ChatMessage(role="user", content="First")],
        )
        request2 = ChatRequest(
            model="model-2",
            messages=[ChatMessage(role="user", content="Second")],
        )

        await adapter.complete(request1)
        await adapter.complete(request2)

        assert len(adapter.history) == 2
        assert adapter.history[0].model == "model-1"
        assert adapter.history[1].model == "model-2"

    def test_health_check(self) -> None:
        """Test mock health check."""
        adapter = MockAdapter()
        health = adapter.health_check()
        assert health["adapter"] == "mock"
        assert health["available"] is True


class TestMorpheusGateway:
    """Tests for MorpheusGateway."""

    def test_register_provider(self) -> None:
        """Test provider registration."""
        gateway = MorpheusGateway()
        adapter = MockAdapter()
        gateway.register_provider(
            name="test-provider",
            adapter=adapter,
            prefix="test-",
        )
        assert "test-provider" in gateway._providers

    @pytest.mark.asyncio
    async def test_route_by_prefix(self) -> None:
        """Test routing based on model prefix."""
        gateway = MorpheusGateway()

        mock1 = MockAdapter(default_response="Provider 1")
        mock2 = MockAdapter(default_response="Provider 2")

        gateway.register_provider("claude", mock1, prefix="claude-")
        gateway.register_provider("gpt", mock2, prefix="gpt-")

        # Route to claude provider
        request1 = ChatRequest(
            model="claude-sonnet",
            messages=[ChatMessage(role="user", content="Hi")],
        )
        response1 = await gateway.chat_completion(request1)
        assert response1.choices[0].message.content == "Provider 1"

        # Route to gpt provider
        request2 = ChatRequest(
            model="gpt-4",
            messages=[ChatMessage(role="user", content="Hi")],
        )
        response2 = await gateway.chat_completion(request2)
        assert response2.choices[0].message.content == "Provider 2"

    @pytest.mark.asyncio
    async def test_no_provider_error(self) -> None:
        """Test error when no provider matches."""
        gateway = MorpheusGateway()
        gateway.register_provider("claude", MockAdapter(), prefix="claude-")

        request = ChatRequest(
            model="unknown-model",
            messages=[ChatMessage(role="user", content="Hi")],
        )

        with pytest.raises(ValueError, match="No provider found"):
            await gateway.chat_completion(request)

    @pytest.mark.asyncio
    async def test_disabled_provider_skipped(self) -> None:
        """Test disabled providers are not routed to."""
        gateway = MorpheusGateway()
        gateway.register_provider(
            "disabled", MockAdapter(), prefix="test-", enabled=False
        )

        request = ChatRequest(
            model="test-model",
            messages=[ChatMessage(role="user", content="Hi")],
        )

        with pytest.raises(ValueError, match="No provider found"):
            await gateway.chat_completion(request)

    def test_health_check(self) -> None:
        """Test gateway health check."""
        gateway = MorpheusGateway()
        gateway.register_provider("mock", MockAdapter(), prefix="test-")

        health = gateway.health_check()
        assert health["status"] == "healthy"
        assert health["providers_healthy"] == 1
        assert health["providers_total"] == 1

    def test_health_check_no_providers(self) -> None:
        """Test health check with no providers."""
        gateway = MorpheusGateway()
        health = gateway.health_check()
        assert health["status"] == "degraded"
        assert health["providers_healthy"] == 0

    @pytest.mark.asyncio
    async def test_request_counting(self) -> None:
        """Test request and error counting."""
        gateway = MorpheusGateway()
        gateway.register_provider("mock", MockAdapter(), prefix="test-")

        request = ChatRequest(
            model="test-model",
            messages=[ChatMessage(role="user", content="Hi")],
        )

        await gateway.chat_completion(request)
        await gateway.chat_completion(request)

        assert gateway._request_count == 2
        assert gateway._error_count == 0


class TestAdapterConfig:
    """Tests for AdapterConfig."""

    def test_defaults(self) -> None:
        """Test default configuration values."""
        config = AdapterConfig()
        assert config.max_concurrent == 3
        assert config.timeout_seconds == 120.0
        assert config.verbose is False
