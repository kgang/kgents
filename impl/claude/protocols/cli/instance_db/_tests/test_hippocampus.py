"""
Tests for Hippocampus: Short-Term Memory Consolidation.

Coverage:
- MemoryBackend (in-memory storage)
- Hippocampus core operations (remember, flush, peek)
- LetheEpoch creation and management
- Auto-flush strategies
- Synapse integration
"""

import pytest

from ..hippocampus import (
    Hippocampus,
    HippocampusConfig,
    LetheEpoch,
    MemoryBackend,
    SynapseHippocampusIntegration,
    create_hippocampus,
)
from ..nervous import Signal
from ..synapse import Synapse, SynapseConfig

# =============================================================================
# Test Fixtures
# =============================================================================


class MockCortex:
    """Mock Cortex for testing."""

    def __init__(self):
        self.signals: list[Signal] = []
        self.batch_calls = 0
        self.fail_next = False

    async def store_signal(self, signal: Signal) -> bool:
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("Cortex failure")
        self.signals.append(signal)
        return True

    async def store_batch(self, signals: list[Signal]) -> int:
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("Cortex batch failure")
        self.signals.extend(signals)
        self.batch_calls += 1
        return len(signals)


def make_signal(signal_type: str = "test", **kwargs) -> Signal:
    """Create a test signal."""
    return Signal(signal_type=signal_type, data=kwargs)


# =============================================================================
# LetheEpoch Tests
# =============================================================================


class TestLetheEpoch:
    """Test LetheEpoch data structure."""

    def test_create_epoch(self):
        """Test epoch creation."""
        epoch = LetheEpoch(
            epoch_id="test-123",
            created_at="2025-01-01T00:00:00",
            sealed_at="2025-01-01T01:00:00",
            signal_count=100,
            signal_types={"test.a", "test.b"},
        )
        assert epoch.epoch_id == "test-123"
        assert epoch.signal_count == 100
        assert len(epoch.signal_types) == 2

    def test_duration_hours(self):
        """Test duration calculation."""
        epoch = LetheEpoch(
            epoch_id="test",
            created_at="2025-01-01T00:00:00",
            sealed_at="2025-01-01T02:30:00",  # 2.5 hours later
            signal_count=10,
            signal_types=set(),
        )
        assert epoch.duration_hours == 2.5


# =============================================================================
# HippocampusConfig Tests
# =============================================================================


class TestHippocampusConfig:
    """Test Hippocampus configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = HippocampusConfig()
        assert config.backend == "memory"
        assert config.max_size == 10000
        assert config.flush_strategy == "on_sleep"
        assert config.create_epochs is True

    def test_from_dict(self):
        """Test config from dict."""
        data = {
            "backend": "redis",
            "max_size": 5000,
            "flush_strategy": "on_size",
        }
        config = HippocampusConfig.from_dict(data)
        assert config.backend == "redis"
        assert config.max_size == 5000
        assert config.flush_strategy == "on_size"

    def test_from_empty_dict(self):
        """Test config from empty dict uses defaults."""
        config = HippocampusConfig.from_dict({})
        assert config.backend == "memory"


# =============================================================================
# MemoryBackend Tests
# =============================================================================


class TestMemoryBackend:
    """Test in-memory storage backend."""

    @pytest.mark.asyncio
    async def test_append_and_size(self):
        """Test appending signals."""
        backend = MemoryBackend()
        signal = make_signal("test")

        await backend.append(signal)

        assert backend.size == 1

    @pytest.mark.asyncio
    async def test_signal_types_tracked(self):
        """Test signal types are tracked."""
        backend = MemoryBackend()

        await backend.append(make_signal("type.a"))
        await backend.append(make_signal("type.b"))
        await backend.append(make_signal("type.a"))

        assert backend.signal_types == {"type.a", "type.b"}

    @pytest.mark.asyncio
    async def test_drain_clears(self):
        """Test drain returns and clears signals."""
        backend = MemoryBackend()

        await backend.append(make_signal("test"))
        await backend.append(make_signal("test"))

        signals = await backend.drain()

        assert len(signals) == 2
        assert backend.size == 0
        assert len(backend.signal_types) == 0

    @pytest.mark.asyncio
    async def test_peek_non_destructive(self):
        """Test peek doesn't remove signals."""
        backend = MemoryBackend()

        await backend.append(make_signal("test"))

        peeked = await backend.peek()
        assert len(peeked) == 1
        assert backend.size == 1  # Still there

    @pytest.mark.asyncio
    async def test_max_size_enforced(self):
        """Test max_size limits queue."""
        backend = MemoryBackend(max_size=5)

        for i in range(10):
            await backend.append(make_signal(f"test.{i}"))

        assert backend.size == 5  # Capped at max


# =============================================================================
# Hippocampus Core Tests
# =============================================================================


class TestHippocampusCreation:
    """Test Hippocampus creation."""

    def test_create_hippocampus(self):
        """Test basic creation."""
        hippocampus = Hippocampus()
        assert hippocampus.size == 0

    def test_create_with_cortex(self):
        """Test creation with cortex."""
        cortex = MockCortex()
        hippocampus = Hippocampus(cortex=cortex)
        assert hippocampus._cortex == cortex

    def test_create_with_config(self):
        """Test creation with config."""
        config = HippocampusConfig(max_size=500)
        hippocampus = Hippocampus(config=config)
        assert hippocampus.config.max_size == 500

    def test_factory_function(self):
        """Test create_hippocampus factory."""
        hippocampus = create_hippocampus(config_dict={"max_size": 100})
        assert hippocampus.config.max_size == 100


class TestHippocampusRemember:
    """Test remembering signals."""

    @pytest.mark.asyncio
    async def test_remember_signal(self):
        """Test remembering a single signal."""
        hippocampus = Hippocampus()
        signal = make_signal("test")

        result = await hippocampus.remember(signal)

        assert result is True
        assert hippocampus.size == 1

    @pytest.mark.asyncio
    async def test_remember_batch(self):
        """Test remembering multiple signals."""
        hippocampus = Hippocampus()
        signals = [make_signal(f"test.{i}") for i in range(5)]

        count = await hippocampus.remember_batch(signals)

        assert count == 5
        assert hippocampus.size == 5

    @pytest.mark.asyncio
    async def test_signal_types_property(self):
        """Test signal_types property."""
        hippocampus = Hippocampus()

        await hippocampus.remember(make_signal("type.a"))
        await hippocampus.remember(make_signal("type.b"))

        assert hippocampus.signal_types == {"type.a", "type.b"}


class TestHippocampusFlush:
    """Test flushing to cortex."""

    @pytest.mark.asyncio
    async def test_flush_transfers_signals(self):
        """Test flush transfers signals to cortex."""
        cortex = MockCortex()
        hippocampus = Hippocampus(cortex=cortex)

        for i in range(3):
            await hippocampus.remember(make_signal(f"test.{i}"))

        result = await hippocampus.flush_to_cortex()

        assert result.signals_transferred == 3
        assert len(cortex.signals) == 3
        assert hippocampus.size == 0

    @pytest.mark.asyncio
    async def test_flush_creates_epoch(self):
        """Test flush creates LetheEpoch."""
        hippocampus = Hippocampus()

        await hippocampus.remember(make_signal("test"))
        result = await hippocampus.flush_to_cortex()

        assert result.epoch_id is not None
        assert len(hippocampus.epochs) == 1

        epoch = hippocampus.epochs[0]
        assert epoch.signal_count == 1

    @pytest.mark.asyncio
    async def test_flush_empty_returns_zero(self):
        """Test flushing empty hippocampus."""
        hippocampus = Hippocampus()

        result = await hippocampus.flush_to_cortex()

        assert result.signals_transferred == 0
        assert result.epoch_id is None

    @pytest.mark.asyncio
    async def test_flush_with_cortex_override(self):
        """Test flush with cortex override."""
        default_cortex = MockCortex()
        override_cortex = MockCortex()
        hippocampus = Hippocampus(cortex=default_cortex)

        await hippocampus.remember(make_signal("test"))
        await hippocampus.flush_to_cortex(cortex=override_cortex)

        assert len(default_cortex.signals) == 0
        assert len(override_cortex.signals) == 1

    @pytest.mark.asyncio
    async def test_flush_handles_cortex_error(self):
        """Test flush handles cortex errors."""
        cortex = MockCortex()
        cortex.fail_next = True
        hippocampus = Hippocampus(cortex=cortex)

        await hippocampus.remember(make_signal("test"))
        result = await hippocampus.flush_to_cortex()

        assert len(result.errors) > 0
        assert "Cortex batch failure" in result.errors[0]

    @pytest.mark.asyncio
    async def test_flush_no_epoch_when_disabled(self):
        """Test flush doesn't create epoch when disabled."""
        config = HippocampusConfig(create_epochs=False)
        hippocampus = Hippocampus(config=config)

        await hippocampus.remember(make_signal("test"))
        result = await hippocampus.flush_to_cortex()

        assert result.epoch_id is None
        assert len(hippocampus.epochs) == 0


class TestHippocampusPeek:
    """Test peeking at memories."""

    @pytest.mark.asyncio
    async def test_peek(self):
        """Test peeking at signals."""
        hippocampus = Hippocampus()

        await hippocampus.remember(make_signal("test"))

        signals = await hippocampus.peek()

        assert len(signals) == 1
        assert hippocampus.size == 1  # Still there

    @pytest.mark.asyncio
    async def test_peek_with_limit(self):
        """Test peek respects limit."""
        hippocampus = Hippocampus()

        for i in range(10):
            await hippocampus.remember(make_signal(f"test.{i}"))

        signals = await hippocampus.peek(limit=3)

        assert len(signals) == 3

    @pytest.mark.asyncio
    async def test_recall_by_type(self):
        """Test recalling by signal type."""
        hippocampus = Hippocampus()

        await hippocampus.remember(make_signal("type.a"))
        await hippocampus.remember(make_signal("type.b"))
        await hippocampus.remember(make_signal("type.a"))

        signals = await hippocampus.recall_by_type("type.a")

        assert len(signals) == 2
        assert all(s.signal_type == "type.a" for s in signals)


# =============================================================================
# Epoch Management Tests
# =============================================================================


class TestEpochManagement:
    """Test Lethe epoch management."""

    @pytest.mark.asyncio
    async def test_get_epoch(self):
        """Test getting epoch by ID."""
        hippocampus = Hippocampus()

        await hippocampus.remember(make_signal("test"))
        result = await hippocampus.flush_to_cortex()

        epoch = hippocampus.get_epoch(result.epoch_id)

        assert epoch is not None
        assert epoch.epoch_id == result.epoch_id

    @pytest.mark.asyncio
    async def test_get_epoch_not_found(self):
        """Test getting non-existent epoch."""
        hippocampus = Hippocampus()

        epoch = hippocampus.get_epoch("nonexistent")

        assert epoch is None

    @pytest.mark.asyncio
    async def test_forget_epoch(self):
        """Test forgetting an epoch."""
        hippocampus = Hippocampus()

        await hippocampus.remember(make_signal("test"))
        result = await hippocampus.flush_to_cortex()

        forgotten = hippocampus.forget_epoch(result.epoch_id)

        assert forgotten is True
        assert len(hippocampus.epochs) == 0

    @pytest.mark.asyncio
    async def test_forget_nonexistent_epoch(self):
        """Test forgetting non-existent epoch."""
        hippocampus = Hippocampus()

        forgotten = hippocampus.forget_epoch("nonexistent")

        assert forgotten is False


# =============================================================================
# Auto-Flush Tests
# =============================================================================


class TestAutoFlush:
    """Test auto-flush strategies."""

    @pytest.mark.asyncio
    async def test_auto_flush_on_size(self):
        """Test auto-flush when size threshold reached."""
        config = HippocampusConfig(max_size=5, flush_strategy="on_size")
        cortex = MockCortex()
        hippocampus = Hippocampus(cortex=cortex, config=config)

        # Add signals up to threshold
        for i in range(5):
            await hippocampus.remember(make_signal(f"test.{i}"))

        # Should have auto-flushed
        assert len(cortex.signals) == 5
        assert hippocampus.size == 0

    @pytest.mark.asyncio
    async def test_no_auto_flush_manual(self):
        """Test manual strategy doesn't auto-flush."""
        config = HippocampusConfig(max_size=5, flush_strategy="manual")
        cortex = MockCortex()
        hippocampus = Hippocampus(cortex=cortex, config=config)

        for i in range(10):
            await hippocampus.remember(make_signal(f"test.{i}"))

        # Should NOT have auto-flushed
        assert len(cortex.signals) == 0


# =============================================================================
# Statistics Tests
# =============================================================================


class TestHippocampusStats:
    """Test statistics collection."""

    @pytest.mark.asyncio
    async def test_age_seconds(self):
        """Test age calculation."""
        hippocampus = Hippocampus()

        # Should be very recent
        age = hippocampus.age_seconds()
        assert age >= 0
        assert age < 1  # Should be less than 1 second

    @pytest.mark.asyncio
    async def test_stats(self):
        """Test stats method."""
        hippocampus = Hippocampus()

        await hippocampus.remember(make_signal("test.a"))
        await hippocampus.remember(make_signal("test.b"))

        stats = hippocampus.stats()

        assert stats["size"] == 2
        assert "test.a" in stats["signal_types"]
        assert "test.b" in stats["signal_types"]
        assert "config" in stats


# =============================================================================
# Integration Tests
# =============================================================================


class TestSynapseIntegration:
    """Test Synapse-Hippocampus integration."""

    @pytest.mark.asyncio
    async def test_integration_wiring(self):
        """Test integration wires up correctly."""
        synapse = Synapse()
        hippocampus = Hippocampus()

        integration = SynapseHippocampusIntegration(synapse, hippocampus)

        assert integration.synapse == synapse
        assert integration.hippocampus == hippocampus

    @pytest.mark.asyncio
    async def test_fast_path_remembered(self):
        """Test fast path signals are remembered."""
        config = SynapseConfig(surprise_threshold=0.0)  # All fast
        synapse = Synapse(config=config)
        hippocampus = Hippocampus()

        _ = SynapseHippocampusIntegration(synapse, hippocampus)

        signal = Signal(signal_type="test", data={})
        await synapse.fire(signal)

        assert hippocampus.size == 1

    @pytest.mark.asyncio
    async def test_batch_path_remembered(self):
        """Test batch path signals are remembered on flush."""
        config = SynapseConfig(surprise_threshold=1.0)  # All batch
        synapse = Synapse(config=config)
        hippocampus = Hippocampus()

        _ = SynapseHippocampusIntegration(synapse, hippocampus)

        signal = Signal(signal_type="test", data={})
        await synapse.fire(signal)

        # Batch hasn't been dispatched yet
        assert hippocampus.size == 0

        # Flush synapse batch
        await synapse.flush_batch()

        # Now hippocampus should have it
        assert hippocampus.size == 1
