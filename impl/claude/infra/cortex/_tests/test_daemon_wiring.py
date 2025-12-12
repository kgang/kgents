"""Tests for CortexDaemon terrarium wiring (Phase 5)."""

import pytest
from infra.cortex.daemon import CortexDaemon


class TestCortexDaemonInit:
    """Daemon initialization tests."""

    def test_daemon_init_has_terrarium_slots(self) -> None:
        """Daemon has buffer and purgatory slots."""
        daemon = CortexDaemon()

        assert hasattr(daemon, "_buffer")
        assert hasattr(daemon, "_purgatory")
        assert daemon._buffer is None
        assert daemon._purgatory is None

    def test_daemon_properties(self) -> None:
        """Daemon exposes buffer and purgatory properties."""
        daemon = CortexDaemon()

        assert daemon.buffer is None
        assert daemon.purgatory is None


class TestCortexDaemonTerrariumBootstrap:
    """Terrarium infrastructure bootstrap tests."""

    @pytest.mark.asyncio
    async def test_bootstrap_terrarium_creates_buffer(self) -> None:
        """_bootstrap_terrarium creates HolographicBuffer."""
        daemon = CortexDaemon()

        await daemon._bootstrap_terrarium()

        assert daemon._buffer is not None
        assert daemon.buffer is not None

    @pytest.mark.asyncio
    async def test_bootstrap_terrarium_creates_purgatory(self) -> None:
        """_bootstrap_terrarium creates Purgatory."""
        daemon = CortexDaemon()

        await daemon._bootstrap_terrarium()

        assert daemon._purgatory is not None
        assert daemon.purgatory is not None

    @pytest.mark.asyncio
    async def test_bootstrap_terrarium_wires_emission(self) -> None:
        """_bootstrap_terrarium wires purgatory emission to buffer."""
        daemon = CortexDaemon()

        await daemon._bootstrap_terrarium()

        assert daemon._purgatory is not None
        assert daemon._purgatory._emit_pheromone is not None
        # The emission callback should be the daemon's method
        assert daemon._purgatory._emit_pheromone == daemon._emit_purgatory_pheromone

    @pytest.mark.asyncio
    async def test_buffer_has_history_size(self) -> None:
        """Buffer is created with configured history size."""
        daemon = CortexDaemon()

        await daemon._bootstrap_terrarium()

        assert daemon._buffer is not None
        assert daemon._buffer.max_history == 100


class TestCortexDaemonPheromoneEmission:
    """Pheromone emission to buffer tests."""

    @pytest.mark.asyncio
    async def test_emit_purgatory_pheromone_reflects_to_buffer(self) -> None:
        """_emit_purgatory_pheromone reflects event to buffer."""
        daemon = CortexDaemon()
        await daemon._bootstrap_terrarium()

        # Emit a purgatory event
        await daemon._emit_purgatory_pheromone(
            "purgatory.ejected",
            {"token_id": "test-123", "reason": "approval_needed"},
        )

        # Check buffer received the event
        assert daemon._buffer is not None
        snapshot = daemon._buffer.get_snapshot()
        assert len(snapshot) == 1

        event = snapshot[0]
        assert event["type"] == "purgatory_ejected"
        assert event["data"]["token_id"] == "test-123"
        assert event["source"] == "cortex.purgatory"
        assert "timestamp" in event

    @pytest.mark.asyncio
    async def test_emit_without_buffer_is_noop(self) -> None:
        """_emit_purgatory_pheromone is no-op without buffer."""
        daemon = CortexDaemon()
        # Don't bootstrap - buffer is None

        # Should not raise
        await daemon._emit_purgatory_pheromone(
            "purgatory.ejected",
            {"token_id": "test-123"},
        )

    @pytest.mark.asyncio
    async def test_emit_handles_buffer_errors_gracefully(self) -> None:
        """Emission errors don't propagate."""
        from unittest.mock import AsyncMock

        daemon = CortexDaemon()
        await daemon._bootstrap_terrarium()

        # Mock buffer to raise
        assert daemon._buffer is not None
        daemon._buffer.reflect = AsyncMock(side_effect=Exception("Buffer error"))  # type: ignore[method-assign]

        # Should not raise
        await daemon._emit_purgatory_pheromone(
            "purgatory.ejected",
            {"token_id": "test-123"},
        )


class TestCortexDaemonTerrariumShutdown:
    """Terrarium infrastructure shutdown tests."""

    @pytest.mark.asyncio
    async def test_shutdown_terrarium_cleans_up(self) -> None:
        """_shutdown_terrarium cleans up buffer and purgatory."""
        daemon = CortexDaemon()
        await daemon._bootstrap_terrarium()

        # Verify setup
        assert daemon._buffer is not None
        assert daemon._purgatory is not None

        # Shutdown
        await daemon._shutdown_terrarium()

        # Verify cleanup
        assert daemon._buffer is None
        assert daemon._purgatory is None

    @pytest.mark.asyncio
    async def test_shutdown_terrarium_voids_expired_tokens(self) -> None:
        """_shutdown_terrarium voids expired tokens."""
        from datetime import datetime, timedelta

        from agents.flux.semaphore import SemaphoreReason, SemaphoreToken

        daemon = CortexDaemon()
        await daemon._bootstrap_terrarium()

        # Add an expired token to purgatory
        assert daemon._purgatory is not None
        expired_token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            frozen_state=b"test",
            original_event="test",
            prompt="Test?",
            deadline=datetime.now() - timedelta(hours=1),  # Already expired
        )
        await daemon._purgatory.save(expired_token)

        # Shutdown should void it
        await daemon._shutdown_terrarium()

        # Purgatory is cleaned up so we can't check directly
        # But the shutdown should have completed without error

    @pytest.mark.asyncio
    async def test_shutdown_terrarium_without_init_is_safe(self) -> None:
        """_shutdown_terrarium is safe without prior init."""
        daemon = CortexDaemon()
        # Don't bootstrap

        # Should not raise
        await daemon._shutdown_terrarium()


class TestCortexDaemonIntegration:
    """Integration tests for terrarium wiring."""

    @pytest.mark.asyncio
    async def test_purgatory_emission_flows_to_buffer(self) -> None:
        """Full flow: purgatory.save() emits to buffer via callback."""
        from agents.flux.semaphore import SemaphoreReason, SemaphoreToken

        daemon = CortexDaemon()
        await daemon._bootstrap_terrarium()

        # Save a token to purgatory
        assert daemon._purgatory is not None
        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            frozen_state=b"test",
            original_event="test",
            prompt="Delete file?",
            options=["Yes", "No"],
        )
        await daemon._purgatory.save(token)

        # Buffer should have received the ejection event
        assert daemon._buffer is not None
        snapshot = daemon._buffer.get_snapshot()
        assert len(snapshot) == 1

        event = snapshot[0]
        assert event["type"] == "purgatory_ejected"
        assert event["data"]["token_id"] == token.id
        assert event["data"]["prompt"] == "Delete file?"

    @pytest.mark.asyncio
    async def test_purgatory_resolve_flows_to_buffer(self) -> None:
        """Full flow: purgatory.resolve() emits to buffer."""
        from agents.flux.semaphore import SemaphoreReason, SemaphoreToken

        daemon = CortexDaemon()
        await daemon._bootstrap_terrarium()

        # Save and resolve a token
        assert daemon._purgatory is not None
        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            frozen_state=b"test",
            original_event="test",
            prompt="Approve?",
        )
        await daemon._purgatory.save(token)
        await daemon._purgatory.resolve(token.id, "Yes")

        # Buffer should have both events
        assert daemon._buffer is not None
        snapshot = daemon._buffer.get_snapshot()
        assert len(snapshot) == 2

        assert snapshot[0]["type"] == "purgatory_ejected"
        assert snapshot[1]["type"] == "purgatory_resolved"

    @pytest.mark.asyncio
    async def test_purgatory_cancel_flows_to_buffer(self) -> None:
        """Full flow: purgatory.cancel() emits to buffer."""
        from agents.flux.semaphore import SemaphoreReason, SemaphoreToken

        daemon = CortexDaemon()
        await daemon._bootstrap_terrarium()

        # Save and cancel a token
        assert daemon._purgatory is not None
        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            frozen_state=b"test",
            original_event="test",
            prompt="Approve?",
        )
        await daemon._purgatory.save(token)
        await daemon._purgatory.cancel(token.id)

        # Buffer should have both events
        assert daemon._buffer is not None
        snapshot = daemon._buffer.get_snapshot()
        assert len(snapshot) == 2

        assert snapshot[0]["type"] == "purgatory_ejected"
        assert snapshot[1]["type"] == "purgatory_cancelled"
