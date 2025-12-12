"""
Tests for Tether Protocol.

The tether makes K-Terrarium agents feel local:
- Signal forwarding (Ctrl+C → SIGTERM)
- stdout/stderr streaming
- Optional debugpy injection
"""

from __future__ import annotations

import asyncio
import signal
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from infra.k8s.tether import (
    TetherConfig,
    TetherProtocol,
    TetherResult,
    TetherSession,
    TetherState,
    create_tether,
)

# =============================================================================
# Unit Tests - TetherConfig
# =============================================================================


class TestTetherConfig:
    """Tests for TetherConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = TetherConfig()

        assert config.namespace == "kgents-agents"
        assert config.debug_port == 5678
        assert config.signal_timeout == 5.0
        assert config.reconnect_delay == 1.0
        assert config.max_reconnects == 3

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = TetherConfig(
            namespace="custom-ns",
            debug_port=9999,
            signal_timeout=10.0,
        )

        assert config.namespace == "custom-ns"
        assert config.debug_port == 9999
        assert config.signal_timeout == 10.0


# =============================================================================
# Unit Tests - TetherSession
# =============================================================================


class TestTetherSession:
    """Tests for TetherSession dataclass."""

    def test_session_creation(self) -> None:
        """Test session creation with required fields."""
        session = TetherSession(
            agent_id="b-gent",
            pod_name="b-gent-abc123",
            container="agent",
        )

        assert session.agent_id == "b-gent"
        assert session.pod_name == "b-gent-abc123"
        assert session.container == "agent"
        assert session.debug_enabled is False
        assert session.debug_port == 5678
        assert session.state == TetherState.DISCONNECTED
        assert session.process is None

    def test_session_with_debug(self) -> None:
        """Test session with debug enabled."""
        session = TetherSession(
            agent_id="l-gent",
            pod_name="l-gent-xyz789",
            container="main",
            debug_enabled=True,
            debug_port=5679,
        )

        assert session.debug_enabled is True
        assert session.debug_port == 5679


# =============================================================================
# Unit Tests - TetherProtocol
# =============================================================================


class TestTetherProtocol:
    """Tests for TetherProtocol class."""

    def test_create_tether(self) -> None:
        """Test factory function."""
        tether = create_tether()

        assert isinstance(tether, TetherProtocol)
        assert tether.config.namespace == "kgents-agents"
        assert tether._session is None

    def test_create_tether_with_callbacks(self) -> None:
        """Test factory with callbacks."""
        outputs: list[tuple[str, str]] = []
        states: list[TetherState] = []

        def on_output(stream: str, data: str) -> None:
            outputs.append((stream, data))

        def on_state_change(state: TetherState) -> None:
            states.append(state)

        tether = create_tether(
            on_output=on_output,
            on_state_change=on_state_change,
        )

        assert tether._on_output is not None
        assert tether._on_state_change is not None

    def test_normalize_agent_id_gent_suffix(self) -> None:
        """Test agent ID normalization with -gent suffix."""
        tether = TetherProtocol()

        assert tether._normalize_agent_id("B") == "b-gent"
        assert tether._normalize_agent_id("b") == "b-gent"
        assert tether._normalize_agent_id("b-gent") == "b-gent"
        assert tether._normalize_agent_id("B-GENT") == "b-gent"

    def test_normalize_agent_id_dev_suffix(self) -> None:
        """Test agent ID normalization with -dev suffix."""
        tether = TetherProtocol()

        assert tether._normalize_agent_id("b-gent-dev") == "b-gent-dev"


class TestTetherProtocolAsync:
    """Async tests for TetherProtocol."""

    @pytest.mark.asyncio
    async def test_attach_no_pod_found(self) -> None:
        """Test attach when no pod is found."""
        tether = TetherProtocol()

        # Mock _find_pod to return None
        with patch.object(tether, "_find_pod", new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None

            result = await tether.attach("nonexistent-agent")

            assert result.success is False
            assert "No pod found" in result.message
            assert result.state == TetherState.ERROR

    @pytest.mark.asyncio
    async def test_attach_success(self) -> None:
        """Test successful attach (mocked)."""
        tether = TetherProtocol()

        pod_info = {"name": "b-gent-abc123", "container": "agent"}

        with (
            patch.object(tether, "_find_pod", new_callable=AsyncMock) as mock_find,
            patch.object(tether, "_stream_logs", new_callable=AsyncMock) as mock_stream,
            patch.object(tether, "_register_signal_handler") as mock_signal,
            patch.object(tether, "detach", new_callable=AsyncMock) as mock_detach,
        ):
            mock_find.return_value = pod_info
            mock_stream.side_effect = KeyboardInterrupt()  # Simulate Ctrl+C
            mock_detach.return_value = TetherResult(
                success=True,
                message="Detached",
                state=TetherState.DISCONNECTED,
            )

            result = await tether.attach("b-gent")

            mock_find.assert_called_once()
            mock_signal.assert_called_once()
            mock_stream.assert_called_once()
            assert result.success is True

    @pytest.mark.asyncio
    async def test_attach_with_debug(self) -> None:
        """Test attach with debug enabled."""
        tether = TetherProtocol()

        pod_info = {"name": "l-gent-xyz789", "container": "main"}

        with (
            patch.object(tether, "_find_pod", new_callable=AsyncMock) as mock_find,
            patch.object(
                tether, "_inject_debugpy", new_callable=AsyncMock
            ) as mock_inject,
            patch.object(
                tether, "_start_port_forward", new_callable=AsyncMock
            ) as mock_pf,
            patch.object(tether, "_stream_logs", new_callable=AsyncMock) as mock_stream,
            patch.object(tether, "_register_signal_handler"),
            patch.object(tether, "detach", new_callable=AsyncMock) as mock_detach,
        ):
            mock_find.return_value = pod_info
            mock_inject.return_value = True
            mock_stream.side_effect = KeyboardInterrupt()
            mock_detach.return_value = TetherResult(
                success=True,
                message="Detached",
                state=TetherState.DISCONNECTED,
            )

            result = await tether.attach("l-gent", debug=True, debug_port=9999)

            mock_inject.assert_called_once_with("l-gent-xyz789", 9999)
            mock_pf.assert_called_once_with("l-gent-xyz789", 9999)

    @pytest.mark.asyncio
    async def test_detach_not_attached(self) -> None:
        """Test detach when not attached."""
        tether = TetherProtocol()

        result = await tether.detach()

        assert result.success is True
        assert result.message == "Not attached"
        assert result.state == TetherState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_detach_with_session(self) -> None:
        """Test detach with active session."""
        tether = TetherProtocol()

        # Create a mock session
        mock_process = MagicMock()
        mock_process.terminate = MagicMock()
        mock_process.wait = AsyncMock()

        tether._session = TetherSession(
            agent_id="b-gent",
            pod_name="b-gent-abc123",
            container="agent",
            process=mock_process,
        )

        result = await tether.detach()

        assert result.success is True
        assert "b-gent-abc123" in result.message
        assert tether._session is None
        mock_process.terminate.assert_called_once()

    @pytest.mark.asyncio
    async def test_forward_signal_not_attached(self) -> None:
        """Test signal forwarding when not attached."""
        tether = TetherProtocol()

        result = await tether.forward_signal(signal.SIGTERM)

        assert result is False

    @pytest.mark.asyncio
    async def test_forward_signal_success(self) -> None:
        """Test successful signal forwarding."""
        tether = TetherProtocol()

        tether._session = TetherSession(
            agent_id="b-gent",
            pod_name="b-gent-abc123",
            container="agent",
        )

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with patch(
            "asyncio.create_subprocess_exec", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = mock_proc

            result = await tether.forward_signal(signal.SIGTERM)

            assert result is True
            mock_exec.assert_called_once()


# =============================================================================
# Integration Tests (require kubectl)
# =============================================================================


class TestTetherIntegration:
    """Integration tests requiring kubectl (skipped if not available)."""

    @pytest.fixture
    def kubectl_available(self) -> bool:
        """Check if kubectl is available."""
        import subprocess

        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        True,  # Skip by default - enable for local testing
        reason="Requires running K-Terrarium cluster",
    )
    async def test_find_pod_real_cluster(self, kubectl_available: bool) -> None:
        """Test finding a pod on a real cluster."""
        if not kubectl_available:
            pytest.skip("kubectl not available")

        tether = TetherProtocol()
        pod_info = await tether._find_pod("b-gent")

        # This may or may not find a pod depending on cluster state
        # Just verify it returns the right type
        assert pod_info is None or isinstance(pod_info, dict)


# =============================================================================
# State Transition Tests
# =============================================================================


class TestTetherStateTransitions:
    """Tests for tether state machine transitions."""

    def test_state_callback(self) -> None:
        """Test that state changes trigger callback."""
        states: list[TetherState] = []

        def on_state_change(state: TetherState) -> None:
            states.append(state)

        tether = TetherProtocol(on_state_change=on_state_change)

        # Simulate state changes
        tether._set_state(TetherState.CONNECTING)
        tether._set_state(TetherState.ATTACHED)
        tether._set_state(TetherState.FORWARDING)
        tether._set_state(TetherState.DISCONNECTED)

        assert states == [
            TetherState.CONNECTING,
            TetherState.ATTACHED,
            TetherState.FORWARDING,
            TetherState.DISCONNECTED,
        ]
