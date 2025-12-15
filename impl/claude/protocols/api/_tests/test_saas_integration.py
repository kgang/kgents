"""
Integration tests for SaaS infrastructure.

Tests:
- SaaSConfig loading from environment
- SaaSClients lifecycle
- Health check endpoints
- Circuit breaker behavior
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Test config module
from protocols.config.saas import (
    SaaSConfig,
    _parse_bool,
    _parse_servers,
    get_saas_config,
    reset_cached_config,
)


class TestSaaSConfig:
    """Test SaaSConfig loading and validation."""

    def test_parse_bool_true_values(self) -> None:
        """Test boolean parsing for true values."""
        assert _parse_bool("true") is True
        assert _parse_bool("True") is True
        assert _parse_bool("TRUE") is True
        assert _parse_bool("1") is True
        assert _parse_bool("yes") is True
        assert _parse_bool("on") is True

    def test_parse_bool_false_values(self) -> None:
        """Test boolean parsing for false values."""
        assert _parse_bool("false") is False
        assert _parse_bool("0") is False
        assert _parse_bool("no") is False
        assert _parse_bool("") is False
        assert _parse_bool("", default=True) is True

    def test_parse_servers_single(self) -> None:
        """Test server list parsing for single server."""
        result = _parse_servers("nats://host:4222")
        assert result == ("nats://host:4222",)

    def test_parse_servers_multiple(self) -> None:
        """Test server list parsing for multiple servers."""
        result = _parse_servers("nats://host1:4222, nats://host2:4222")
        assert result == ("nats://host1:4222", "nats://host2:4222")

    def test_parse_servers_empty(self) -> None:
        """Test server list parsing for empty string."""
        result = _parse_servers("")
        assert result == ("nats://localhost:4222",)

    def test_get_saas_config_defaults(self) -> None:
        """Test config with default values."""
        # Clear environment
        env_vars = [
            "NATS_SERVERS",
            "NATS_ENABLED",
            "NATS_STREAM_NAME",
            "NATS_MAX_RECONNECT",
            "OPENMETER_API_KEY",
            "OPENMETER_BASE_URL",
            "OPENMETER_ENABLED",
            "OPENMETER_BATCH_SIZE",
            "OPENMETER_FLUSH_INTERVAL",
        ]
        with patch.dict(os.environ, {}, clear=True):
            for var in env_vars:
                os.environ.pop(var, None)

            reset_cached_config()
            config = get_saas_config()

            assert config.nats_servers == ("nats://localhost:4222",)
            assert config.nats_enabled is False
            assert config.nats_stream_name == "kgent-events"
            assert config.nats_max_reconnect == 10

            assert config.openmeter_api_key == ""
            assert config.openmeter_base_url == "https://openmeter.cloud"
            assert config.openmeter_enabled is False
            assert config.openmeter_batch_size == 100
            assert config.openmeter_flush_interval == 1.0

    def test_get_saas_config_from_env(self) -> None:
        """Test config loading from environment."""
        env = {
            "NATS_SERVERS": "nats://prod:4222",
            "NATS_ENABLED": "true",
            "NATS_STREAM_NAME": "prod-events",
            "NATS_MAX_RECONNECT": "20",
            "OPENMETER_API_KEY": "om_test_key",
            "OPENMETER_BASE_URL": "https://api.openmeter.cloud",
            "OPENMETER_ENABLED": "true",
            "OPENMETER_BATCH_SIZE": "50",
            "OPENMETER_FLUSH_INTERVAL": "2.5",
        }
        with patch.dict(os.environ, env, clear=False):
            reset_cached_config()
            config = get_saas_config()

            assert config.nats_servers == ("nats://prod:4222",)
            assert config.nats_enabled is True
            assert config.nats_stream_name == "prod-events"
            assert config.nats_max_reconnect == 20

            assert config.openmeter_api_key == "om_test_key"
            assert config.openmeter_base_url == "https://api.openmeter.cloud"
            assert config.openmeter_enabled is True
            assert config.openmeter_batch_size == 50
            assert config.openmeter_flush_interval == 2.5

    def test_is_nats_configured(self) -> None:
        """Test NATS configuration check."""
        config = SaaSConfig(
            nats_servers=("nats://localhost:4222",),
            nats_enabled=True,
            nats_stream_name="test",
            nats_max_reconnect=10,
            openmeter_api_key="",
            openmeter_base_url="",
            openmeter_enabled=False,
            openmeter_batch_size=100,
            openmeter_flush_interval=1.0,
        )
        assert config.is_nats_configured is True

        config_disabled = SaaSConfig(
            nats_servers=("nats://localhost:4222",),
            nats_enabled=False,  # Disabled
            nats_stream_name="test",
            nats_max_reconnect=10,
            openmeter_api_key="",
            openmeter_base_url="",
            openmeter_enabled=False,
            openmeter_batch_size=100,
            openmeter_flush_interval=1.0,
        )
        assert config_disabled.is_nats_configured is False

    def test_is_openmeter_configured(self) -> None:
        """Test OpenMeter configuration check."""
        config = SaaSConfig(
            nats_servers=(),
            nats_enabled=False,
            nats_stream_name="",
            nats_max_reconnect=0,
            openmeter_api_key="om_key",
            openmeter_base_url="https://api.openmeter.cloud",
            openmeter_enabled=True,
            openmeter_batch_size=100,
            openmeter_flush_interval=1.0,
        )
        assert config.is_openmeter_configured is True

        config_no_key = SaaSConfig(
            nats_servers=(),
            nats_enabled=False,
            nats_stream_name="",
            nats_max_reconnect=0,
            openmeter_api_key="",  # No key
            openmeter_base_url="https://api.openmeter.cloud",
            openmeter_enabled=True,
            openmeter_batch_size=100,
            openmeter_flush_interval=1.0,
        )
        assert config_no_key.is_openmeter_configured is False


class TestCircuitBreaker:
    """Test circuit breaker behavior."""

    def test_circuit_starts_closed(self) -> None:
        """Test circuit breaker starts in closed state."""
        from protocols.streaming.nats_bridge import CircuitBreaker, CircuitState

        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.is_closed is True
        assert cb.should_allow_request() is True

    def test_circuit_opens_after_failures(self) -> None:
        """Test circuit breaker opens after failure threshold."""
        from protocols.streaming.nats_bridge import CircuitBreaker, CircuitState

        cb = CircuitBreaker(failure_threshold=3)

        # Record failures
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN  # type: ignore[comparison-overlap]
        assert cb.should_allow_request() is False

    def test_circuit_success_resets_failures(self) -> None:
        """Test success resets failure count."""
        from protocols.streaming.nats_bridge import CircuitBreaker, CircuitState

        cb = CircuitBreaker(failure_threshold=3)

        # Partial failures
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED

        # Success resets
        cb.record_success()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED  # Still closed

    def test_circuit_half_open_recovery(self) -> None:
        """Test circuit recovers through half-open state."""
        from protocols.streaming.nats_bridge import CircuitBreaker, CircuitState

        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.0)

        # Open circuit
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN

        # Trigger half-open (recovery_timeout=0 allows immediate)
        cb.should_allow_request()  # This should transition to half-open
        assert cb.state == CircuitState.HALF_OPEN  # type: ignore[comparison-overlap]

        # Successful requests close circuit
        cb.record_success()
        cb.record_success()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_circuit_half_open_failure_reopens(self) -> None:
        """Test failure in half-open reopens circuit."""
        from protocols.streaming.nats_bridge import CircuitBreaker, CircuitState

        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.0)

        # Open circuit
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN

        # Enter half-open
        cb.should_allow_request()
        assert cb.state == CircuitState.HALF_OPEN  # type: ignore[comparison-overlap]

        # Failure reopens
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_circuit_to_dict(self) -> None:
        """Test circuit breaker status serialization."""
        from protocols.streaming.nats_bridge import CircuitBreaker

        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=30.0)
        status = cb.to_dict()

        assert status["state"] == "closed"
        assert status["failures"] == 0
        assert status["last_failure"] is None
        assert status["failure_threshold"] == 5
        assert status["recovery_timeout"] == 30.0


class TestSaaSClientsLifecycle:
    """Test SaaSClients lifecycle management."""

    @pytest.mark.asyncio
    async def test_clients_not_started_initially(self) -> None:
        """Test clients are not started before start() is called."""
        from protocols.config.clients import SaaSClients

        config = SaaSConfig(
            nats_servers=(),
            nats_enabled=False,
            nats_stream_name="",
            nats_max_reconnect=0,
            openmeter_api_key="",
            openmeter_base_url="",
            openmeter_enabled=False,
            openmeter_batch_size=100,
            openmeter_flush_interval=1.0,
        )
        clients = SaaSClients(config=config)

        assert clients.is_started is False
        assert clients.openmeter is None
        assert clients.nats is None

    @pytest.mark.asyncio
    async def test_start_stop_idempotent(self) -> None:
        """Test start/stop are idempotent."""
        from protocols.config.clients import SaaSClients

        config = SaaSConfig(
            nats_servers=(),
            nats_enabled=False,
            nats_stream_name="",
            nats_max_reconnect=0,
            openmeter_api_key="",
            openmeter_base_url="",
            openmeter_enabled=False,
            openmeter_batch_size=100,
            openmeter_flush_interval=1.0,
        )
        clients = SaaSClients(config=config)

        # Multiple starts should be safe
        await clients.start()
        await clients.start()
        assert clients.is_started is True

        # Multiple stops should be safe
        await clients.stop()
        await clients.stop()
        assert clients.is_started is False

    @pytest.mark.asyncio
    async def test_health_check_not_started(self) -> None:
        """Test health check when not started."""
        from protocols.config.clients import SaaSClients

        config = SaaSConfig(
            nats_servers=(),
            nats_enabled=False,
            nats_stream_name="",
            nats_max_reconnect=0,
            openmeter_api_key="",
            openmeter_base_url="",
            openmeter_enabled=False,
            openmeter_batch_size=100,
            openmeter_flush_interval=1.0,
        )
        clients = SaaSClients(config=config)

        health = await clients.health_check()
        assert health["started"] is False
        assert health["openmeter"]["status"] == "disabled"
        assert health["nats"]["status"] == "disabled"


class TestHealthEndpoint:
    """Test health check endpoint integration."""

    @pytest.mark.asyncio
    async def test_saas_health_endpoint_not_configured(self) -> None:
        """Test /health/saas when SaaS not configured."""
        pytest.importorskip("fastapi")
        from fastapi.testclient import TestClient
        from protocols.api.app import create_app
        from protocols.config.clients import reset_saas_clients
        from protocols.config.saas import reset_cached_config

        # Ensure clean state
        reset_cached_config()
        reset_saas_clients()

        app = create_app()
        client = TestClient(app)

        response = client.get("/health/saas")
        assert response.status_code == 200

        data = response.json()
        # Should report not_started or disabled
        assert data["status"] in ("not_started", "not_configured", "ok")
