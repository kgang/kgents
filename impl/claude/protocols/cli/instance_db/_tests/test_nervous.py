"""
Tests for the Nervous System (Spinal Cord).

Tests cover:
1. Signal classification (reflex vs cortical)
2. Routing behavior (bypass vs synapse)
3. Fast store integration
4. Batch processing
5. Metrics tracking
6. Dynamic configuration
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from ..nervous import (
    ISynapse,
    NervousSystem,
    NervousSystemConfig,
    NullSynapse,
    Signal,
    SignalPriority,
    create_nervous_system,
)


class TestSignal:
    """Tests for Signal dataclass."""

    def test_create_signal_minimal(self):
        """Signal can be created with just type and data."""
        signal = Signal(signal_type="test.signal", data={"value": 42})

        assert signal.signal_type == "test.signal"
        assert signal.data == {"value": 42}
        assert signal.timestamp is not None
        assert signal.priority == SignalPriority.CORTICAL

    def test_create_signal_full(self):
        """Signal can be created with all fields."""
        ts = datetime.now().isoformat()
        signal = Signal(
            signal_type="test.signal",
            data={"value": 42},
            timestamp=ts,
            instance_id="inst-123",
            project_hash="abcd1234",
            priority=SignalPriority.REFLEX,
            surprise=0.5,
        )

        assert signal.signal_type == "test.signal"
        assert signal.timestamp == ts
        assert signal.instance_id == "inst-123"
        assert signal.project_hash == "abcd1234"
        assert signal.priority == SignalPriority.REFLEX
        assert signal.surprise == 0.5


class TestSignalPriority:
    """Tests for SignalPriority enum."""

    def test_priority_values(self):
        """All priority levels exist."""
        assert SignalPriority.REFLEX.value == "reflex"
        assert SignalPriority.CORTICAL.value == "cortical"
        assert SignalPriority.FLASHBULB.value == "flashbulb"


class TestNervousSystemConfig:
    """Tests for NervousSystemConfig."""

    def test_default_config(self):
        """Default config has expected reflex patterns."""
        config = NervousSystemConfig()

        assert "telemetry.heartbeat" in config.spinal_reflexes
        assert "io.raw.read" in config.spinal_reflexes
        assert "system.cpu_metrics" in config.spinal_reflexes
        assert config.log_reflexes is True

    def test_default_flashbulb_patterns(self):
        """Default config has expected flashbulb patterns."""
        config = NervousSystemConfig()

        assert "user.input" in config.flashbulb_patterns
        assert "error.critical" in config.flashbulb_patterns
        assert "security.alert" in config.flashbulb_patterns

    def test_config_from_dict(self):
        """Config can be created from dict."""
        config = NervousSystemConfig.from_dict(
            {
                "spinal_reflexes": ["custom.reflex"],
                "flashbulb_patterns": ["custom.flash"],
                "log_reflexes": False,
            }
        )

        assert config.spinal_reflexes == {"custom.reflex"}
        assert config.flashbulb_patterns == {"custom.flash"}
        assert config.log_reflexes is False

    def test_config_from_empty_dict(self):
        """Empty dict gives default config."""
        config = NervousSystemConfig.from_dict({})

        assert "telemetry.heartbeat" in config.spinal_reflexes
        assert config.log_reflexes is True


class TestNullSynapse:
    """Tests for NullSynapse."""

    @pytest.mark.asyncio
    async def test_null_synapse_drops_signals(self):
        """NullSynapse accepts signals without error."""
        synapse = NullSynapse()
        signal = Signal(signal_type="test", data={})

        # Should not raise
        await synapse.fire(signal)


class TestNervousSystemClassification:
    """Tests for signal classification."""

    def test_classify_reflex_signal(self):
        """Reflex signals are classified as REFLEX."""
        nervous = NervousSystem()
        signal = Signal(signal_type="telemetry.heartbeat", data={})

        priority = nervous.classify_signal(signal)

        assert priority == SignalPriority.REFLEX

    def test_classify_cortical_signal(self):
        """Unknown signals are classified as CORTICAL."""
        nervous = NervousSystem()
        signal = Signal(signal_type="shape.observed", data={})

        priority = nervous.classify_signal(signal)

        assert priority == SignalPriority.CORTICAL

    def test_classify_flashbulb_signal(self):
        """Flashbulb signals are classified as FLASHBULB."""
        nervous = NervousSystem()
        signal = Signal(signal_type="user.input", data={})

        priority = nervous.classify_signal(signal)

        assert priority == SignalPriority.FLASHBULB

    def test_flashbulb_takes_precedence(self):
        """Flashbulb patterns override reflex patterns."""
        config = NervousSystemConfig(
            spinal_reflexes={"priority.test"},
            flashbulb_patterns={"priority.test"},
        )
        nervous = NervousSystem(config=config)
        signal = Signal(signal_type="priority.test", data={})

        # Flashbulb should take precedence
        priority = nervous.classify_signal(signal)

        assert priority == SignalPriority.FLASHBULB

    def test_is_reflex_helper(self):
        """is_reflex helper works correctly."""
        nervous = NervousSystem()

        assert nervous.is_reflex("telemetry.heartbeat") is True
        assert nervous.is_reflex("shape.observed") is False
        assert nervous.is_reflex("io.raw.read") is True


class TestNervousSystemRouting:
    """Tests for signal routing."""

    @pytest.mark.asyncio
    async def test_reflex_routes_to_fast_store(self):
        """Reflex signals go to fast store."""
        mock_store = AsyncMock()
        nervous = NervousSystem(fast_store=mock_store)

        signal = Signal(signal_type="telemetry.heartbeat", data={"cpu": 45.2})
        result = await nervous.transmit(signal)

        assert result.routed_to == "reflex"
        assert result.logged is True
        mock_store.append.assert_called_once()

    @pytest.mark.asyncio
    async def test_cortical_routes_to_synapse(self):
        """Cortical signals go to Synapse."""
        mock_synapse = AsyncMock(spec=ISynapse)
        nervous = NervousSystem(synapse=mock_synapse)

        signal = Signal(signal_type="shape.observed", data={"type": "insight"})
        result = await nervous.transmit(signal)

        assert result.routed_to == "synapse"
        mock_synapse.fire.assert_called_once_with(signal)

    @pytest.mark.asyncio
    async def test_reflex_without_store(self):
        """Reflex signals work without store (not logged)."""
        nervous = NervousSystem()

        signal = Signal(signal_type="telemetry.heartbeat", data={})
        result = await nervous.transmit(signal)

        assert result.routed_to == "reflex"
        assert result.logged is False

    @pytest.mark.asyncio
    async def test_reflex_with_logging_disabled(self):
        """Reflex signals can skip logging."""
        mock_store = AsyncMock()
        config = NervousSystemConfig(log_reflexes=False)
        nervous = NervousSystem(fast_store=mock_store, config=config)

        signal = Signal(signal_type="telemetry.heartbeat", data={})
        result = await nervous.transmit(signal)

        assert result.routed_to == "reflex"
        assert result.logged is False
        mock_store.append.assert_not_called()

    @pytest.mark.asyncio
    async def test_synapse_error_marks_dropped(self):
        """Synapse errors mark signal as dropped."""
        mock_synapse = AsyncMock(spec=ISynapse)
        mock_synapse.fire.side_effect = RuntimeError("Synapse error")
        nervous = NervousSystem(synapse=mock_synapse)

        signal = Signal(signal_type="shape.observed", data={})
        result = await nervous.transmit(signal)

        assert result.routed_to == "dropped"
        assert result.error is not None


class TestNervousSystemBatch:
    """Tests for batch transmission."""

    @pytest.mark.asyncio
    async def test_batch_reflex_signals(self):
        """Batch reflex signals use single append."""
        mock_store = AsyncMock()
        nervous = NervousSystem(fast_store=mock_store)

        signals = [
            Signal(signal_type="telemetry.heartbeat", data={"i": 1}),
            Signal(signal_type="system.cpu_metrics", data={"i": 2}),
            Signal(signal_type="io.raw.read", data={"i": 3}),
        ]
        results = await nervous.transmit_batch(signals)

        # Should batch all reflex signals into one append
        assert mock_store.append.call_count == 1
        assert len(results) == 3
        assert all(r.routed_to == "reflex" for r in results)

    @pytest.mark.asyncio
    async def test_batch_mixed_signals(self):
        """Batch handles mixed reflex and cortical signals."""
        mock_store = AsyncMock()
        mock_synapse = AsyncMock(spec=ISynapse)
        nervous = NervousSystem(fast_store=mock_store, synapse=mock_synapse)

        signals = [
            Signal(signal_type="telemetry.heartbeat", data={}),
            Signal(signal_type="shape.observed", data={}),
            Signal(signal_type="io.raw.read", data={}),
        ]
        results = await nervous.transmit_batch(signals)

        # 2 reflex (batched), 1 cortical
        assert mock_store.append.call_count == 1
        assert mock_synapse.fire.call_count == 1
        assert len(results) == 3


class TestNervousSystemMetrics:
    """Tests for metrics tracking."""

    @pytest.mark.asyncio
    async def test_metrics_track_reflex(self):
        """Metrics track reflex signals."""
        nervous = NervousSystem()

        await nervous.transmit(Signal(signal_type="telemetry.heartbeat", data={}))
        await nervous.transmit(Signal(signal_type="io.raw.read", data={}))

        metrics = nervous.metrics
        assert metrics["reflex_count"] == 2
        assert metrics["cortical_count"] == 0
        assert metrics["total"] == 2

    @pytest.mark.asyncio
    async def test_metrics_track_cortical(self):
        """Metrics track cortical signals."""
        nervous = NervousSystem()

        await nervous.transmit(Signal(signal_type="shape.observed", data={}))

        metrics = nervous.metrics
        assert metrics["cortical_count"] == 1
        assert metrics["reflex_count"] == 0

    @pytest.mark.asyncio
    async def test_metrics_reset(self):
        """Metrics can be reset."""
        nervous = NervousSystem()

        await nervous.transmit(Signal(signal_type="telemetry.heartbeat", data={}))

        old_metrics = nervous.reset_metrics()
        new_metrics = nervous.metrics

        assert old_metrics["reflex_count"] == 1
        assert new_metrics["reflex_count"] == 0


class TestNervousSystemDynamic:
    """Tests for dynamic configuration."""

    def test_add_reflex_pattern(self):
        """Can add reflex patterns dynamically."""
        nervous = NervousSystem()

        nervous.add_reflex_pattern("custom.signal")

        assert nervous.is_reflex("custom.signal") is True

    def test_remove_reflex_pattern(self):
        """Can remove reflex patterns dynamically."""
        nervous = NervousSystem()

        nervous.remove_reflex_pattern("telemetry.heartbeat")

        assert nervous.is_reflex("telemetry.heartbeat") is False

    def test_add_flashbulb_pattern(self):
        """Can add flashbulb patterns dynamically."""
        nervous = NervousSystem()
        nervous.add_flashbulb_pattern("custom.urgent")

        signal = Signal(signal_type="custom.urgent", data={})
        priority = nervous.classify_signal(signal)

        assert priority == SignalPriority.FLASHBULB

    def test_set_synapse(self):
        """Can set synapse after construction."""
        nervous = NervousSystem()
        mock_synapse = AsyncMock(spec=ISynapse)

        nervous.set_synapse(mock_synapse)

        assert nervous._synapse == mock_synapse

    def test_set_fast_store(self):
        """Can set fast store after construction."""
        nervous = NervousSystem()
        mock_store = AsyncMock()

        nervous.set_fast_store(mock_store)

        assert nervous._fast_store == mock_store


class TestCreateNervousSystem:
    """Tests for factory function."""

    def test_create_with_defaults(self):
        """Factory creates system with defaults."""
        nervous = create_nervous_system()

        assert nervous.is_reflex("telemetry.heartbeat") is True
        assert nervous.config.log_reflexes is True

    def test_create_with_config(self):
        """Factory accepts config dict."""
        nervous = create_nervous_system(
            config_dict={
                "spinal_reflexes": ["custom.only"],
                "log_reflexes": False,
            }
        )

        assert nervous.is_reflex("custom.only") is True
        assert nervous.is_reflex("telemetry.heartbeat") is False
        assert nervous.config.log_reflexes is False

    def test_create_with_store(self):
        """Factory accepts telemetry store."""
        mock_store = MagicMock()
        nervous = create_nervous_system(telemetry_store=mock_store)

        assert nervous._fast_store == mock_store
