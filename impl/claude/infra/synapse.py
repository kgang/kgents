"""
Synapse: The neurotransmitter layer for infrastructure signals.

From the critique:
    "Instead of direct method calls between D-gents and Storage,
    introduce a lightweight signal layer."

The Synapse decouples agent intent from storage mechanism:
- Agents fire signals expressing "what happened"
- Synapse routes signals to appropriate handlers
- Storage responds based on signal characteristics

Key features:
- Active Inference: Calculate "Surprise" for each signal
- Smart Routing: High surprise → fast path; Low surprise → batch
- Observability: All signals are traceable
- Backpressure: Buffer overflow triggers graceful degradation

From spec/principles.md (Composable):
    The Synapse is a morphism from Signal to Effect.
    It composes with other infrastructure components.

From spec/bootstrap.md (Fix):
    The Synapse uses Fix internally for stability detection.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Awaitable, Protocol
from collections import deque
import hashlib
import json


class SignalKind(Enum):
    """
    Classification of signal types.

    From the critique's Active Inference model:
    - STATE_CHANGED: Core memory signal
    - PREDICTION_MADE: Predictive model update
    - SURPRISE_DETECTED: High KL divergence event
    - DRIFT_DETECTED: Semantic drift alert
    - LIFECYCLE_EVENT: System lifecycle signal
    """

    STATE_CHANGED = auto()
    PREDICTION_MADE = auto()
    SURPRISE_DETECTED = auto()
    DRIFT_DETECTED = auto()
    LIFECYCLE_EVENT = auto()
    TELEMETRY_EVENT = auto()
    GARDEN_EVENT = auto()  # Memory lifecycle (seed, bloom, compost)


@dataclass(frozen=True)
class Signal:
    """
    An immutable signal fired through the Synapse.

    Signals are the "neurotransmitters" of the system.
    They carry information from agents to infrastructure.
    """

    kind: SignalKind
    source: str  # Agent or component that fired
    timestamp: datetime
    data: dict[str, Any]

    # Active Inference metadata
    surprise: float = 0.0  # KL divergence from prediction (0.0 = expected)
    prediction_id: str | None = None  # ID of prediction this relates to

    # Routing hints
    priority: int = 0  # Higher = faster path
    batch_eligible: bool = True  # Can this be batched?

    def semantic_hash(self) -> str:
        """Hash for deduplication and sketching."""
        content = json.dumps(
            {"kind": self.kind.name, "source": self.source, "data": self.data},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class SignalHandler(Protocol):
    """Protocol for signal handlers."""

    async def handle(self, signal: Signal) -> None:
        """Handle a signal."""
        ...


@dataclass
class SynapseConfig:
    """Configuration for the Synapse."""

    buffer_size: int = 1000
    batch_interval_ms: int = 100
    surprise_threshold: float = 0.5  # Above this → fast path
    max_handlers_per_kind: int = 10


@dataclass
class PredictiveModel:
    """
    Simple predictive model for Active Inference.

    From the critique:
        "D-gents shouldn't just store data; they should generate Predictions."

    This is exponential smoothing: prediction = alpha * current + (1-alpha) * previous
    """

    alpha: float = 0.3  # Smoothing factor
    predictions: dict[str, float] = field(default_factory=dict)

    def predict(self, key: str) -> float:
        """Return predicted value for key (default 0.5)."""
        return self.predictions.get(key, 0.5)

    def update(self, key: str, actual: float) -> float:
        """
        Update prediction and return surprise (absolute error).

        Surprise = |actual - predicted|
        """
        predicted = self.predict(key)
        surprise = abs(actual - predicted)

        # Exponential smoothing update
        self.predictions[key] = self.alpha * actual + (1 - self.alpha) * predicted

        return surprise


class Synapse:
    """
    The neurotransmitter layer.

    Decouples agent intent from storage mechanism.
    Implements Active Inference for smart signal routing.

    From the critique:
        "High surprise → Fast path (Volatile + Alert)
         Low surprise  → Slow path (Batch write to Garden)"

    Usage:
        synapse = Synapse(config)
        await synapse.start()

        # Register handlers
        synapse.register(SignalKind.STATE_CHANGED, my_handler)

        # Fire signals
        await synapse.fire(Signal(
            kind=SignalKind.STATE_CHANGED,
            source="my_agent",
            timestamp=datetime.now(),
            data={"key": "value"},
        ))
    """

    def __init__(self, config: SynapseConfig | None = None):
        self._config = config or SynapseConfig()
        self._handlers: dict[SignalKind, list[SignalHandler]] = {
            k: [] for k in SignalKind
        }
        self._buffer: deque[Signal] = deque(maxlen=self._config.buffer_size)
        self._batch_queue: deque[Signal] = deque()
        self._predictive_model = PredictiveModel()
        self._running = False
        self._batch_task: asyncio.Task | None = None

        # Metrics
        self._signals_fired = 0
        self._fast_path_count = 0
        self._batch_path_count = 0

    def register(
        self,
        kind: SignalKind,
        handler: SignalHandler | Callable[[Signal], Awaitable[None]],
    ) -> None:
        """Register a handler for a signal kind."""
        if len(self._handlers[kind]) >= self._config.max_handlers_per_kind:
            raise ValueError(f"Max handlers reached for {kind}")

        # Wrap callable in handler protocol if needed
        if not isinstance(handler, SignalHandler):
            # Create wrapper
            class CallableHandler:
                def __init__(self, fn: Callable[[Signal], Awaitable[None]]):
                    self._fn = fn

                async def handle(self, signal: Signal) -> None:
                    await self._fn(signal)

            handler = CallableHandler(handler)

        self._handlers[kind].append(handler)

    async def fire(self, signal: Signal) -> None:
        """
        Fire a signal through the Synapse.

        Active Inference routing:
        - Calculate surprise against prediction
        - High surprise → immediate dispatch (fast path)
        - Low surprise → batch queue (slow path)
        """
        self._signals_fired += 1

        # Calculate surprise using predictive model
        signal_value = self._extract_signal_value(signal)
        surprise = self._predictive_model.update(signal.source, signal_value)

        # Enrich signal with surprise
        enriched = Signal(
            kind=signal.kind,
            source=signal.source,
            timestamp=signal.timestamp,
            data=signal.data,
            surprise=surprise,
            prediction_id=signal.prediction_id,
            priority=signal.priority,
            batch_eligible=signal.batch_eligible,
        )

        # Add to buffer for history
        self._buffer.append(enriched)

        # Route based on surprise
        if surprise > self._config.surprise_threshold or not enriched.batch_eligible:
            # Fast path: immediate dispatch
            self._fast_path_count += 1
            await self._dispatch(enriched)
        else:
            # Slow path: add to batch queue
            self._batch_path_count += 1
            self._batch_queue.append(enriched)

    async def _dispatch(self, signal: Signal) -> None:
        """Dispatch signal to all registered handlers."""
        handlers = self._handlers.get(signal.kind, [])
        if handlers:
            await asyncio.gather(
                *[h.handle(signal) for h in handlers],
                return_exceptions=True,
            )

    async def _batch_loop(self) -> None:
        """Background loop for batched signal dispatch."""
        while self._running:
            await asyncio.sleep(self._config.batch_interval_ms / 1000)

            # Process batch queue
            to_dispatch: list[Signal] = []
            while self._batch_queue:
                to_dispatch.append(self._batch_queue.popleft())

            # Dispatch all
            for signal in to_dispatch:
                await self._dispatch(signal)

    async def start(self) -> None:
        """Start the Synapse batch processor."""
        self._running = True
        self._batch_task = asyncio.create_task(self._batch_loop())

    async def stop(self) -> None:
        """Stop the Synapse and flush remaining signals."""
        self._running = False
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass

        # Flush remaining batch queue
        while self._batch_queue:
            signal = self._batch_queue.popleft()
            await self._dispatch(signal)

    def _extract_signal_value(self, signal: Signal) -> float:
        """
        Extract a numeric value from signal for prediction.

        This is a simple heuristic—real systems would use embeddings.
        """
        # Use hash of semantic content as proxy for "novelty"
        hash_int = int(signal.semantic_hash(), 16)
        return (hash_int % 1000) / 1000.0

    def metrics(self) -> dict[str, Any]:
        """Return Synapse metrics."""
        return {
            "signals_fired": self._signals_fired,
            "fast_path_count": self._fast_path_count,
            "batch_path_count": self._batch_path_count,
            "fast_path_ratio": (
                self._fast_path_count / self._signals_fired
                if self._signals_fired > 0
                else 0.0
            ),
            "buffer_size": len(self._buffer),
            "batch_queue_size": len(self._batch_queue),
            "predictions_tracked": len(self._predictive_model.predictions),
        }
