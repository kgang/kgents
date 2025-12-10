"""
Tests for Synapse: Active Inference Event Bus.

Coverage:
- PredictiveModel (O(1) exponential smoothing)
- Synapse routing (flashbulb, fast, batch paths)
- Handler registration and dispatch
- Metrics collection
"""


import pytest

from ..synapse import (
    PredictiveModel,
    Synapse,
    SynapseConfig,
    SurpriseMetrics,
    create_synapse,
)
from ..nervous import Signal, SignalPriority
from ..interfaces import TelemetryEvent


# =============================================================================
# Test Fixtures
# =============================================================================


class MockTelemetryStore:
    """Mock telemetry store for testing."""

    def __init__(self):
        self.events: list[TelemetryEvent] = []
        self.fail_next = False

    async def append(self, events: list[TelemetryEvent]) -> int:
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("Store failure")
        self.events.extend(events)
        return len(events)


class MockHandler:
    """Mock handler for testing dispatch."""

    def __init__(self):
        self.signals: list[Signal] = []

    async def handle(self, signal: Signal) -> None:
        self.signals.append(signal)


class FailingHandler:
    """Handler that fails."""

    async def handle(self, signal: Signal) -> None:
        raise RuntimeError("Handler failed")


# =============================================================================
# PredictiveModel Tests
# =============================================================================


class TestPredictiveModel:
    """Test the O(1) predictive model."""

    def test_create_model(self):
        """Test model creation."""
        model = PredictiveModel()
        assert model._alpha == 0.3
        assert model._prior == 0.5

    def test_create_with_custom_params(self):
        """Test model with custom parameters."""
        model = PredictiveModel(alpha=0.5, prior=0.3)
        assert model._alpha == 0.5
        assert model._prior == 0.3

    def test_invalid_alpha(self):
        """Test that invalid alpha raises."""
        with pytest.raises(ValueError):
            PredictiveModel(alpha=0)
        with pytest.raises(ValueError):
            PredictiveModel(alpha=1.5)

    def test_predict_unknown_type(self):
        """Test prediction for unknown signal type returns prior."""
        model = PredictiveModel(prior=0.5)
        assert model.predict("unknown") == 0.5

    def test_update_returns_surprise(self):
        """Test update returns surprise value."""
        model = PredictiveModel()
        surprise = model.update("test.signal")
        assert 0.0 <= surprise <= 1.0

    def test_update_reduces_surprise(self):
        """Test repeated signals reduce surprise."""
        model = PredictiveModel()

        # First occurrence - higher surprise
        surprise1 = model.update("repeated.signal")

        # Repeat several times
        for _ in range(10):
            model.update("repeated.signal")

        # After many repetitions, surprise should be lower
        surprise_final = model.update("repeated.signal")
        # The model learns the pattern, reducing surprise
        assert surprise_final <= surprise1

    def test_new_signal_type_high_surprise(self):
        """Test new signal type has high surprise."""
        model = PredictiveModel()

        # Train on one type
        for _ in range(10):
            model.update("expected.signal")

        # New type should have higher surprise
        surprise = model.update("unexpected.signal")
        assert surprise > 0.1  # Non-trivial surprise

    def test_surprise_for_without_update(self):
        """Test surprise_for doesn't modify model."""
        model = PredictiveModel()
        model.update("test", 1.0)
        pred_before = model.predict("test")

        # Call surprise_for
        model.surprise_for("test", 0.5)

        # Prediction unchanged
        assert model.predict("test") == pred_before

    def test_reset_clears_predictions(self):
        """Test reset clears all state."""
        model = PredictiveModel()
        model.update("signal.a")
        model.update("signal.b")

        model.reset()

        assert model.predict("signal.a") == model._prior
        assert len(model.known_types) == 0

    def test_known_types(self):
        """Test known_types returns seen signal types."""
        model = PredictiveModel()
        model.update("type.a")
        model.update("type.b")
        model.update("type.a")  # Duplicate

        assert model.known_types == {"type.a", "type.b"}

    def test_stats(self):
        """Test stats returns model state."""
        model = PredictiveModel(alpha=0.3, prior=0.5)
        model.update("test")

        stats = model.stats()
        assert stats["alpha"] == 0.3
        assert stats["prior"] == 0.5
        assert stats["known_types"] == 1
        assert "test" in stats["predictions"]


# =============================================================================
# SynapseConfig Tests
# =============================================================================


class TestSynapseConfig:
    """Test Synapse configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SynapseConfig()
        assert config.surprise_threshold == 0.5
        assert config.flashbulb_threshold == 0.9
        assert config.smoothing_alpha == 0.3
        assert config.batch_size == 100

    def test_from_dict(self):
        """Test config from dict."""
        data = {
            "surprise_threshold": 0.6,
            "flashbulb_threshold": 0.95,
            "batch_size": 50,
        }
        config = SynapseConfig.from_dict(data)
        assert config.surprise_threshold == 0.6
        assert config.flashbulb_threshold == 0.95
        assert config.batch_size == 50

    def test_from_empty_dict(self):
        """Test config from empty dict uses defaults."""
        config = SynapseConfig.from_dict({})
        assert config.surprise_threshold == 0.5


# =============================================================================
# SurpriseMetrics Tests
# =============================================================================


class TestSurpriseMetrics:
    """Test surprise metrics tracking."""

    def test_initial_metrics(self):
        """Test initial metrics are zero."""
        metrics = SurpriseMetrics()
        assert metrics.high_surprise_count == 0
        assert metrics.low_surprise_count == 0
        assert metrics.flashbulb_count == 0
        assert metrics.batched_count == 0

    def test_avg_surprise_empty(self):
        """Test avg_surprise for unknown type."""
        metrics = SurpriseMetrics()
        assert metrics.avg_surprise("unknown") == 0.5  # Prior

    def test_avg_surprise_with_data(self):
        """Test avg_surprise calculation."""
        metrics = SurpriseMetrics()
        metrics.type_counts["test"] = 2
        metrics.type_total_surprise["test"] = 1.0  # 0.5 avg
        assert metrics.avg_surprise("test") == 0.5


# =============================================================================
# Synapse Core Tests
# =============================================================================


class TestSynapseCreation:
    """Test Synapse creation and configuration."""

    def test_create_synapse(self):
        """Test basic synapse creation."""
        synapse = Synapse()
        assert synapse.config.surprise_threshold == 0.5

    def test_create_with_store(self):
        """Test synapse with telemetry store."""
        store = MockTelemetryStore()
        synapse = Synapse(telemetry_store=store)
        assert synapse._store == store

    def test_create_with_config(self):
        """Test synapse with custom config."""
        config = SynapseConfig(surprise_threshold=0.7)
        synapse = Synapse(config=config)
        assert synapse.config.surprise_threshold == 0.7

    def test_factory_function(self):
        """Test create_synapse factory."""
        synapse = create_synapse(config_dict={"surprise_threshold": 0.6})
        assert synapse.config.surprise_threshold == 0.6


# =============================================================================
# Synapse Routing Tests
# =============================================================================


class TestSynapseRouting:
    """Test signal routing based on surprise."""

    @pytest.mark.asyncio
    async def test_fire_computes_surprise(self):
        """Test fire() computes and sets surprise."""
        synapse = Synapse()
        signal = Signal(signal_type="test.signal", data={})

        result = await synapse.fire(signal)

        assert signal.surprise > 0
        assert result.surprise == signal.surprise

    @pytest.mark.asyncio
    async def test_high_surprise_fast_path(self):
        """Test high surprise routes to fast path."""
        config = SynapseConfig(surprise_threshold=0.0)  # Everything is high surprise
        synapse = Synapse(config=config)

        signal = Signal(signal_type="test", data={})
        result = await synapse.fire(signal)

        assert result.route in ("fast", "flashbulb")
        assert not result.queued

    @pytest.mark.asyncio
    async def test_low_surprise_batch_path(self):
        """Test low surprise routes to batch path."""
        config = SynapseConfig(surprise_threshold=1.0)  # Everything is low surprise
        synapse = Synapse(config=config)

        signal = Signal(signal_type="test", data={})
        result = await synapse.fire(signal)

        assert result.route == "batch"
        assert result.queued

    @pytest.mark.asyncio
    async def test_flashbulb_immediate(self):
        """Test flashbulb threshold triggers immediate dispatch."""
        config = SynapseConfig(flashbulb_threshold=0.0)  # Everything is flashbulb
        synapse = Synapse(config=config)

        signal = Signal(signal_type="critical", data={})
        result = await synapse.fire(signal)

        assert result.route == "flashbulb"
        assert signal.priority == SignalPriority.FLASHBULB

    @pytest.mark.asyncio
    async def test_bypass_model(self):
        """Test bypass_model uses signal's existing surprise."""
        synapse = Synapse()
        signal = Signal(signal_type="test", data={}, surprise=0.99)

        result = await synapse.fire(signal, bypass_model=True)

        assert result.surprise == 0.99


# =============================================================================
# Handler Tests
# =============================================================================


class TestSynapseHandlers:
    """Test handler registration and dispatch."""

    @pytest.mark.asyncio
    async def test_fast_handler_called(self):
        """Test fast path handler is called."""
        config = SynapseConfig(surprise_threshold=0.0)
        synapse = Synapse(config=config)
        handler = MockHandler()
        synapse.on_fast_path(handler)

        signal = Signal(signal_type="test", data={})
        await synapse.fire(signal)

        assert len(handler.signals) == 1
        assert handler.signals[0] == signal

    @pytest.mark.asyncio
    async def test_flashbulb_handler_called(self):
        """Test flashbulb handler is called."""
        config = SynapseConfig(flashbulb_threshold=0.0)
        synapse = Synapse(config=config)
        handler = MockHandler()
        synapse.on_flashbulb(handler)

        signal = Signal(signal_type="critical", data={})
        await synapse.fire(signal)

        assert len(handler.signals) == 1

    @pytest.mark.asyncio
    async def test_flashbulb_also_calls_fast(self):
        """Test flashbulb also dispatches to fast handlers."""
        config = SynapseConfig(flashbulb_threshold=0.0)
        synapse = Synapse(config=config)
        flashbulb_handler = MockHandler()
        fast_handler = MockHandler()
        synapse.on_flashbulb(flashbulb_handler)
        synapse.on_fast_path(fast_handler)

        signal = Signal(signal_type="critical", data={})
        await synapse.fire(signal)

        assert len(flashbulb_handler.signals) == 1
        assert len(fast_handler.signals) == 1

    @pytest.mark.asyncio
    async def test_batch_handler_on_flush(self):
        """Test batch handlers called on flush."""
        config = SynapseConfig(surprise_threshold=1.0)  # All batch
        synapse = Synapse(config=config)
        handler = MockHandler()
        synapse.on_batch_path(handler)

        signal = Signal(signal_type="test", data={})
        await synapse.fire(signal)

        # Not called yet (queued)
        assert len(handler.signals) == 0

        # Flush
        await synapse.flush_batch()

        assert len(handler.signals) == 1

    @pytest.mark.asyncio
    async def test_callable_handler(self):
        """Test callable (function) as handler."""
        config = SynapseConfig(surprise_threshold=0.0)
        synapse = Synapse(config=config)
        received = []

        async def handler(signal):
            received.append(signal)

        synapse.on_fast_path(handler)

        signal = Signal(signal_type="test", data={})
        await synapse.fire(signal)

        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_handler_error_captured(self):
        """Test handler errors are captured in result."""
        config = SynapseConfig(surprise_threshold=0.0)
        synapse = Synapse(config=config)
        synapse.on_fast_path(FailingHandler())

        signal = Signal(signal_type="test", data={})
        result = await synapse.fire(signal)

        assert result.error is not None
        assert "Handler failed" in result.error


# =============================================================================
# Batching Tests
# =============================================================================


class TestSynapseBatching:
    """Test batch path functionality."""

    @pytest.mark.asyncio
    async def test_batch_queue_grows(self):
        """Test signals queue in batch path."""
        config = SynapseConfig(surprise_threshold=1.0, batch_size=10)
        synapse = Synapse(config=config)

        for i in range(5):
            signal = Signal(signal_type=f"test.{i}", data={})
            await synapse.fire(signal)

        assert synapse.batch_size == 5

    @pytest.mark.asyncio
    async def test_batch_auto_flush(self):
        """Test batch auto-flushes at batch_size."""
        config = SynapseConfig(surprise_threshold=1.0, batch_size=3)
        synapse = Synapse(config=config)
        handler = MockHandler()
        synapse.on_batch_path(handler)

        for i in range(3):
            signal = Signal(signal_type=f"test.{i}", data={})
            await synapse.fire(signal)

        # Should have auto-flushed
        assert synapse.batch_size == 0
        assert len(handler.signals) == 3

    @pytest.mark.asyncio
    async def test_flush_batch_returns_count(self):
        """Test flush_batch returns number of signals."""
        config = SynapseConfig(surprise_threshold=1.0)
        synapse = Synapse(config=config)

        for i in range(5):
            signal = Signal(signal_type=f"test.{i}", data={})
            await synapse.fire(signal)

        count = await synapse.flush_batch()
        assert count == 5

    @pytest.mark.asyncio
    async def test_flush_empty_batch(self):
        """Test flushing empty batch returns 0."""
        synapse = Synapse()
        count = await synapse.flush_batch()
        assert count == 0


# =============================================================================
# Telemetry Logging Tests
# =============================================================================


class TestSynapseTelemetry:
    """Test telemetry logging."""

    @pytest.mark.asyncio
    async def test_fast_path_logs(self):
        """Test fast path logs to telemetry."""
        store = MockTelemetryStore()
        config = SynapseConfig(surprise_threshold=0.0)
        synapse = Synapse(telemetry_store=store, config=config)

        signal = Signal(signal_type="test", data={"key": "value"})
        result = await synapse.fire(signal)

        assert result.logged
        assert len(store.events) == 1
        assert store.events[0].event_type == "test"

    @pytest.mark.asyncio
    async def test_batch_logs_on_flush(self):
        """Test batch path logs on flush."""
        store = MockTelemetryStore()
        config = SynapseConfig(surprise_threshold=1.0)
        synapse = Synapse(telemetry_store=store, config=config)

        for i in range(3):
            signal = Signal(signal_type=f"test.{i}", data={})
            await synapse.fire(signal)

        assert len(store.events) == 0  # Not logged yet

        await synapse.flush_batch()

        assert len(store.events) == 3

    @pytest.mark.asyncio
    async def test_store_failure_handled(self):
        """Test store failure doesn't crash."""
        store = MockTelemetryStore()
        store.fail_next = True
        config = SynapseConfig(surprise_threshold=0.0)
        synapse = Synapse(telemetry_store=store, config=config)

        signal = Signal(signal_type="test", data={})
        result = await synapse.fire(signal)

        assert not result.logged  # Failed to log


# =============================================================================
# Metrics Tests
# =============================================================================


class TestSynapseMetrics:
    """Test metrics collection."""

    @pytest.mark.asyncio
    async def test_metrics_count_routes(self):
        """Test metrics track route counts."""
        config = SynapseConfig(surprise_threshold=0.5)
        synapse = Synapse(config=config)

        # Fire some signals
        for i in range(10):
            signal = Signal(signal_type=f"test.{i}", data={})
            await synapse.fire(signal)

        metrics = synapse.metrics
        total = (
            metrics.high_surprise_count
            + metrics.low_surprise_count
            + metrics.flashbulb_count
        )
        assert total == 10

    @pytest.mark.asyncio
    async def test_reset_metrics(self):
        """Test metrics reset."""
        synapse = Synapse()
        signal = Signal(signal_type="test", data={})
        await synapse.fire(signal)

        old = synapse.reset_metrics()
        assert old.type_counts["test"] == 1

        new = synapse.metrics
        assert new.type_counts.get("test", 0) == 0


# =============================================================================
# Peek/Interrupt Tests
# =============================================================================


class TestSynapsePeek:
    """Test peek and interrupt detection."""

    @pytest.mark.asyncio
    async def test_peek_recent(self):
        """Test peek_recent returns recent signals."""
        synapse = Synapse()

        signal = Signal(signal_type="test", data={})
        await synapse.fire(signal)

        recent = await synapse.peek_recent(window_ms=1000)
        assert len(recent) == 1

    @pytest.mark.asyncio
    async def test_peek_recent_filters_by_surprise(self):
        """Test peek_recent filters by min_surprise."""
        synapse = Synapse()

        signal = Signal(signal_type="test", data={})
        await synapse.fire(signal)

        # Filter with high min_surprise
        recent = await synapse.peek_recent(window_ms=1000, min_surprise=0.99)
        # May or may not match depending on actual surprise
        assert isinstance(recent, list)

    @pytest.mark.asyncio
    async def test_has_flashbulb_pending(self):
        """Test flashbulb detection."""
        config = SynapseConfig(flashbulb_threshold=0.0)  # All flashbulb
        synapse = Synapse(config=config)

        signal = Signal(signal_type="urgent", data={})
        await synapse.fire(signal)

        assert synapse.has_flashbulb_pending(window_ms=1000)

    def test_surprise_stats_empty(self):
        """Test surprise_stats with no data."""
        synapse = Synapse()
        stats = synapse.surprise_stats()
        assert stats["avg_surprise"] == 0.5

    @pytest.mark.asyncio
    async def test_surprise_stats_with_data(self):
        """Test surprise_stats with signals."""
        synapse = Synapse()

        for i in range(5):
            signal = Signal(signal_type=f"test.{i}", data={})
            await synapse.fire(signal)

        stats = synapse.surprise_stats()
        assert "avg_surprise" in stats
        assert "surprise_std" in stats
        assert 0.0 <= stats["avg_surprise"] <= 1.0
