"""
Synapse: Active Inference Event Bus for the Bicameral Engine.

The Synapse routes signals based on "surprise" - the difference between
expected and actual signal patterns. This implements Active Inference:
- High surprise → Fast path (immediate dispatch)
- Low surprise  → Batch path (garden queue for later)
- Flashbulb threshold → Priority persistence

Design Constraints:
- PredictiveModel MUST be O(1) - exponential smoothing, NOT heavy ML
- Synapse latency trap prevention: No blocking on prediction
- Surprise computed incrementally per signal type

From the implementation plan:
> "A cortex doesn't just store; it predicts, forgets, and hallucinates."

References:
- Friston, K. (2010). "The free-energy principle: a unified brain theory?"
- Active Inference: Organisms minimize surprise by either updating
  beliefs (perception) or acting on the world (action)
"""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean, stdev
from typing import Any, Callable, Protocol, runtime_checkable

from .interfaces import ITelemetryStore, TelemetryEvent
from .nervous import Signal, SignalPriority


@dataclass
class SurpriseMetrics:
    """Metrics about surprise distribution across signal types."""

    type_counts: dict[str, int] = field(default_factory=dict)
    type_total_surprise: dict[str, float] = field(default_factory=dict)
    high_surprise_count: int = 0
    low_surprise_count: int = 0
    flashbulb_count: int = 0
    batched_count: int = 0

    def avg_surprise(self, signal_type: str) -> float:
        """Average surprise for a signal type."""
        count = self.type_counts.get(signal_type, 0)
        if count == 0:
            return 0.5  # Prior: uncertain
        return self.type_total_surprise.get(signal_type, 0.0) / count


@dataclass
class SynapseConfig:
    """Configuration for the Synapse."""

    # Surprise thresholds
    surprise_threshold: float = 0.5  # Above this = high surprise
    flashbulb_threshold: float = 0.9  # Above this = interrupt dreaming

    # Predictive model parameters
    smoothing_alpha: float = 0.3  # Exponential smoothing factor (0 < α ≤ 1)
    prior_surprise: float = 0.5  # Prior for new signal types

    # Batching configuration
    batch_size: int = 100  # Max signals before flush
    batch_interval_ms: int = 100  # Flush interval

    # History size for statistics
    history_size: int = 1000  # Rolling window for surprise stats

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SynapseConfig":
        """Create from configuration dict."""
        return cls(
            surprise_threshold=data.get("surprise_threshold", 0.5),
            flashbulb_threshold=data.get("flashbulb_threshold", 0.9),
            smoothing_alpha=data.get("smoothing_alpha", 0.3),
            prior_surprise=data.get("prior_surprise", 0.5),
            batch_size=data.get("batch_size", 100),
            batch_interval_ms=data.get("batch_interval_ms", 100),
            history_size=data.get("history_size", 1000),
        )


class PredictiveModel:
    """
    O(1) Exponential Smoothing Predictive Model.

    Predicts the next signal's "intensity" based on history.
    Surprise = |actual - predicted| normalized to [0, 1].

    This is NOT machine learning - it's simple exponential smoothing
    that runs in O(1) time with O(n) space where n = number of signal types.

    Design rationale:
    - Heavy ML models (even T-Digest) add latency
    - We want instant surprise computation
    - Exponential smoothing is surprisingly effective for this use case

    Usage:
        model = PredictiveModel()
        surprise = model.update("telemetry.heartbeat", 1.0)  # Returns surprise
        surprise = model.update("telemetry.heartbeat", 1.0)  # Lower surprise now
        surprise = model.update("error.critical", 1.0)  # High surprise (new type)
    """

    def __init__(
        self,
        alpha: float = 0.3,
        prior: float = 0.5,
    ):
        """
        Initialize the predictive model.

        Args:
            alpha: Smoothing factor (0 < α ≤ 1). Higher = more reactive.
            prior: Prior prediction for unseen signal types.
        """
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in (0, 1]")
        self._alpha = alpha
        self._prior = prior
        # Current prediction per signal type
        self._predictions: dict[str, float] = {}
        # Variance estimates for normalization
        self._variances: dict[str, float] = {}

    def predict(self, signal_type: str) -> float:
        """
        Get current prediction for a signal type.

        Args:
            signal_type: The signal type to predict

        Returns:
            Predicted intensity [0, 1]
        """
        return self._predictions.get(signal_type, self._prior)

    def update(self, signal_type: str, actual: float = 1.0) -> float:
        """
        Update prediction and compute surprise (O(1) operation).

        This is the core Active Inference computation:
        1. Get prediction (O(1) dict lookup)
        2. Compute surprise = |actual - predicted|
        3. Update prediction with exponential smoothing
        4. Update variance estimate for normalization

        Args:
            signal_type: The signal type observed
            actual: Actual intensity (default 1.0 for presence)

        Returns:
            Surprise value [0, 1]
        """
        # Step 1: Get prediction
        predicted = self._predictions.get(signal_type, self._prior)

        # Step 2: Compute raw surprise
        raw_surprise = abs(actual - predicted)

        # Step 3: Update prediction (exponential smoothing)
        # new_pred = α × actual + (1 - α) × old_pred
        self._predictions[signal_type] = (
            self._alpha * actual + (1 - self._alpha) * predicted
        )

        # Step 4: Update variance estimate for normalization
        # Using exponential smoothing on squared error
        old_var = self._variances.get(signal_type, 0.25)  # Prior variance
        self._variances[signal_type] = (
            self._alpha * (raw_surprise**2) + (1 - self._alpha) * old_var
        )

        # Step 5: Normalize surprise (optional, but helps with thresholding)
        # Use Z-score-ish normalization: surprise / (1 + σ)
        sigma = max(0.01, self._variances[signal_type] ** 0.5)
        normalized = min(1.0, raw_surprise / (1 + sigma))

        return normalized

    def surprise_for(self, signal_type: str, actual: float = 1.0) -> float:
        """
        Compute surprise WITHOUT updating the model.

        Useful for peek-ahead decisions.

        Args:
            signal_type: The signal type
            actual: Actual intensity

        Returns:
            Surprise value [0, 1]
        """
        predicted = self._predictions.get(signal_type, self._prior)
        raw_surprise = abs(actual - predicted)
        sigma = max(0.01, self._variances.get(signal_type, 0.25) ** 0.5)
        return min(1.0, raw_surprise / (1 + sigma))

    def reset(self) -> None:
        """Reset all predictions to prior."""
        self._predictions.clear()
        self._variances.clear()

    @property
    def known_types(self) -> set[str]:
        """Get all signal types with predictions."""
        return set(self._predictions.keys())

    def stats(self) -> dict[str, Any]:
        """Get model statistics."""
        return {
            "known_types": len(self._predictions),
            "predictions": dict(self._predictions),
            "variances": dict(self._variances),
            "alpha": self._alpha,
            "prior": self._prior,
        }


@runtime_checkable
class ISynapseHandler(Protocol):
    """Protocol for signal handlers."""

    async def handle(self, signal: Signal) -> None:
        """Handle a signal."""
        ...


@dataclass
class DispatchResult:
    """Result of signal dispatch through Synapse."""

    signal: Signal
    surprise: float
    route: str  # "fast", "batch", "flashbulb"
    queued: bool
    logged: bool
    error: str | None = None


class Synapse:
    """
    Active Inference Event Bus.

    Routes signals based on surprise:
    - Flashbulb (surprise > 0.9) → Immediate + interrupt dreaming
    - High surprise (> 0.5) → Fast path (immediate dispatch)
    - Low surprise (< 0.5) → Batch path (queue for later)

    The Synapse is the "corpus callosum" connecting different parts
    of the cognitive system. It decides what deserves attention NOW
    vs. what can wait.

    Usage:
        synapse = Synapse(telemetry_store, config)

        # Register handlers for fast-path signals
        synapse.on_fast_path(my_handler)

        # Fire a signal
        result = await synapse.fire(Signal(
            signal_type="shape.observed",
            data={"shape_type": "insight"}
        ))
        # → Computes surprise, routes to fast or batch path
    """

    def __init__(
        self,
        telemetry_store: ITelemetryStore | None = None,
        config: SynapseConfig | None = None,
    ):
        """
        Initialize the Synapse.

        Args:
            telemetry_store: Store for logging signals
            config: Synapse configuration
        """
        self._store = telemetry_store
        self._config = config or SynapseConfig()

        # Core components
        self._model = PredictiveModel(
            alpha=self._config.smoothing_alpha,
            prior=self._config.prior_surprise,
        )
        self._metrics = SurpriseMetrics()

        # Batching
        self._batch_queue: deque[Signal] = deque()
        self._batch_lock = asyncio.Lock()
        self._flush_task: asyncio.Task | None = None

        # Handlers
        self._fast_handlers: list[ISynapseHandler | Callable] = []
        self._batch_handlers: list[ISynapseHandler | Callable] = []
        self._flashbulb_handlers: list[ISynapseHandler | Callable] = []

        # Recent signals for interrupt checking (sliding window)
        self._recent: deque[tuple[Signal, float]] = deque(
            maxlen=self._config.history_size
        )

    @property
    def config(self) -> SynapseConfig:
        """Get synapse configuration."""
        return self._config

    @property
    def metrics(self) -> SurpriseMetrics:
        """Get current metrics."""
        return self._metrics

    @property
    def model(self) -> PredictiveModel:
        """Get the predictive model."""
        return self._model

    @property
    def batch_size(self) -> int:
        """Current batch queue size."""
        return len(self._batch_queue)

    def on_fast_path(self, handler: ISynapseHandler | Callable) -> None:
        """Register handler for fast-path signals."""
        self._fast_handlers.append(handler)

    def on_batch_path(self, handler: ISynapseHandler | Callable) -> None:
        """Register handler for batch-path signals."""
        self._batch_handlers.append(handler)

    def on_flashbulb(self, handler: ISynapseHandler | Callable) -> None:
        """Register handler for flashbulb signals (highest priority)."""
        self._flashbulb_handlers.append(handler)

    async def fire(
        self,
        signal: Signal,
        bypass_model: bool = False,
    ) -> DispatchResult:
        """
        Fire a signal through the Synapse.

        This is the main entry point:
        1. Compute surprise (O(1))
        2. Route based on thresholds
        3. Log to telemetry
        4. Dispatch to handlers

        Args:
            signal: The signal to fire
            bypass_model: If True, use signal.surprise directly (for re-routing)

        Returns:
            DispatchResult with routing info
        """
        # Step 1: Compute surprise
        if bypass_model:
            surprise = signal.surprise
        else:
            surprise = self._model.update(signal.signal_type)
            signal.surprise = surprise

        # Update metrics
        self._metrics.type_counts[signal.signal_type] = (
            self._metrics.type_counts.get(signal.signal_type, 0) + 1
        )
        self._metrics.type_total_surprise[signal.signal_type] = (
            self._metrics.type_total_surprise.get(signal.signal_type, 0.0) + surprise
        )

        # Add to recent window
        self._recent.append((signal, datetime.now().timestamp()))

        # Step 2: Route based on surprise
        if surprise >= self._config.flashbulb_threshold:
            return await self._dispatch_flashbulb(signal, surprise)
        elif surprise >= self._config.surprise_threshold:
            return await self._dispatch_fast(signal, surprise)
        else:
            return await self._dispatch_batch(signal, surprise)

    async def _dispatch_flashbulb(
        self, signal: Signal, surprise: float
    ) -> DispatchResult:
        """Dispatch flashbulb signal (highest priority)."""
        signal.priority = SignalPriority.FLASHBULB
        self._metrics.flashbulb_count += 1

        logged = await self._log_signal(signal)
        error = None

        # Dispatch to flashbulb handlers
        for handler in self._flashbulb_handlers:
            try:
                if hasattr(handler, "handle"):
                    await handler.handle(signal)  # type: ignore
                else:
                    result = handler(signal)
                    if asyncio.iscoroutine(result):
                        await result
            except Exception as e:
                error = str(e)

        # Also dispatch to fast handlers (flashbulb is superset of fast)
        for handler in self._fast_handlers:
            try:
                if hasattr(handler, "handle"):
                    await handler.handle(signal)  # type: ignore
                else:
                    result = handler(signal)
                    if asyncio.iscoroutine(result):
                        await result
            except Exception as e:
                if not error:
                    error = str(e)

        return DispatchResult(
            signal=signal,
            surprise=surprise,
            route="flashbulb",
            queued=False,
            logged=logged,
            error=error,
        )

    async def _dispatch_fast(self, signal: Signal, surprise: float) -> DispatchResult:
        """Dispatch high-surprise signal (fast path)."""
        self._metrics.high_surprise_count += 1

        logged = await self._log_signal(signal)
        error = None

        # Dispatch to fast handlers
        for handler in self._fast_handlers:
            try:
                if hasattr(handler, "handle"):
                    await handler.handle(signal)  # type: ignore
                else:
                    result = handler(signal)
                    if asyncio.iscoroutine(result):
                        await result
            except Exception as e:
                error = str(e)

        return DispatchResult(
            signal=signal,
            surprise=surprise,
            route="fast",
            queued=False,
            logged=logged,
            error=error,
        )

    async def _dispatch_batch(self, signal: Signal, surprise: float) -> DispatchResult:
        """Dispatch low-surprise signal (batch path)."""
        self._metrics.low_surprise_count += 1
        self._metrics.batched_count += 1

        # Queue for batching
        async with self._batch_lock:
            self._batch_queue.append(signal)

            # Check if we should flush
            should_flush = len(self._batch_queue) >= self._config.batch_size

        if should_flush:
            await self.flush_batch()

        return DispatchResult(
            signal=signal,
            surprise=surprise,
            route="batch",
            queued=True,
            logged=False,  # Will be logged on flush
            error=None,
        )

    async def _log_signal(self, signal: Signal) -> bool:
        """Log signal to telemetry store."""
        if not self._store:
            return False

        try:
            event = TelemetryEvent(
                event_type=signal.signal_type,
                timestamp=signal.timestamp,
                data={
                    **signal.data,
                    "surprise": signal.surprise,
                    "priority": signal.priority.value,
                },
                instance_id=signal.instance_id,
                project_hash=signal.project_hash,
            )
            await self._store.append([event])
            return True
        except Exception:
            return False

    async def flush_batch(self) -> int:
        """
        Flush batched signals.

        Returns:
            Number of signals flushed
        """
        async with self._batch_lock:
            if not self._batch_queue:
                return 0

            signals = list(self._batch_queue)
            self._batch_queue.clear()

        # Log all signals
        if self._store:
            events = [
                TelemetryEvent(
                    event_type=s.signal_type,
                    timestamp=s.timestamp,
                    data={
                        **s.data,
                        "surprise": s.surprise,
                        "priority": s.priority.value,
                    },
                    instance_id=s.instance_id,
                    project_hash=s.project_hash,
                )
                for s in signals
            ]
            await self._store.append(events)

        # Dispatch to batch handlers
        for handler in self._batch_handlers:
            try:
                for signal in signals:
                    if hasattr(handler, "handle"):
                        await handler.handle(signal)  # type: ignore
                    else:
                        result = handler(signal)
                        if asyncio.iscoroutine(result):
                            await result
            except Exception:
                pass  # Don't fail flush on handler errors

        return len(signals)

    async def peek_recent(
        self,
        window_ms: int = 100,
        min_surprise: float = 0.0,
    ) -> list[Signal]:
        """
        Peek at recent signals (for interrupt checking).

        Args:
            window_ms: Look back this many milliseconds
            min_surprise: Filter signals with surprise above this

        Returns:
            List of recent signals matching criteria
        """
        now = datetime.now().timestamp()
        cutoff = now - (window_ms / 1000.0)

        return [
            signal
            for signal, ts in self._recent
            if ts >= cutoff and signal.surprise >= min_surprise
        ]

    def has_flashbulb_pending(self, window_ms: int = 100) -> bool:
        """
        Check if any flashbulb signals in recent window.

        Used by LucidDreamer to check for interrupts.

        Args:
            window_ms: Look back window

        Returns:
            True if flashbulb signal detected
        """
        now = datetime.now().timestamp()
        cutoff = now - (window_ms / 1000.0)

        for signal, ts in self._recent:
            if ts >= cutoff and signal.surprise >= self._config.flashbulb_threshold:
                return True
        return False

    def surprise_stats(self) -> dict[str, float]:
        """
        Get surprise statistics.

        Returns:
            Dict with avg_surprise, surprise_variance, etc.
        """
        if not self._recent:
            return {
                "avg_surprise": 0.5,
                "min_surprise": 0.0,
                "max_surprise": 1.0,
                "surprise_std": 0.0,
            }

        surprises = [s.surprise for s, _ in self._recent]
        return {
            "avg_surprise": mean(surprises),
            "min_surprise": min(surprises),
            "max_surprise": max(surprises),
            "surprise_std": stdev(surprises) if len(surprises) > 1 else 0.0,
        }

    def reset_metrics(self) -> SurpriseMetrics:
        """Reset and return current metrics."""
        old = self._metrics
        self._metrics = SurpriseMetrics()
        return old


# Factory function
def create_synapse(
    telemetry_store: ITelemetryStore | None = None,
    config_dict: dict[str, Any] | None = None,
) -> Synapse:
    """
    Create a Synapse with optional configuration.

    Args:
        telemetry_store: Store for logging
        config_dict: Configuration dict (from YAML)

    Returns:
        Configured Synapse
    """
    config = SynapseConfig.from_dict(config_dict) if config_dict else SynapseConfig()
    return Synapse(telemetry_store=telemetry_store, config=config)
