"""
Spinal Cord: Fast-Path Signal Routing for the Bicameral Engine.

The Nervous System provides two-tier signal routing:
1. Spinal Reflexes: O(1) pattern-matched signals bypass cortical processing
   - Heartbeats, raw I/O, CPU metrics → direct to fast store
2. Ascending Pathway: Semantic signals → Synapse for cortical processing

This prevents the "Synapse Latency Trap" where evaluating every signal
through a predictive model creates bottlenecks (10,000 × 1ms = 10s blocking).

Design: Fast path for noise, slow path for signal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from .interfaces import ITelemetryStore, TelemetryEvent


class SignalPriority(Enum):
    """Signal priority levels for routing decisions."""

    # Bypass cortex entirely (O(1) routing)
    REFLEX = "reflex"
    # Normal cortical processing via Synapse
    CORTICAL = "cortical"
    # High-priority: interrupt dreaming if needed
    FLASHBULB = "flashbulb"


@dataclass
class Signal:
    """
    A signal in the nervous system.

    Signals are routed based on type:
    - Reflex patterns → fast store (bypass cortex)
    - Other signals → Synapse (cortical processing)
    """

    signal_type: str
    data: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    instance_id: str | None = None
    project_hash: str | None = None
    # Computed during routing
    priority: SignalPriority = SignalPriority.CORTICAL
    surprise: float = 0.0  # Will be set by Synapse if cortical


@runtime_checkable
class ISynapse(Protocol):
    """
    Protocol for the Synapse (Event Bus).

    The Synapse handles cortical signal processing with Active Inference.
    This protocol allows NervousSystem to route signals without
    depending on the full Synapse implementation.
    """

    async def fire(self, signal: Signal) -> None:
        """
        Fire a signal through the Synapse for cortical processing.

        The Synapse will:
        1. Compute surprise via predictive model
        2. Route high-surprise to fast path
        3. Route low-surprise to batch path
        """
        ...


class NullSynapse:
    """
    Null Synapse for when no Synapse is configured.

    Drops cortical signals silently. Used in early phases
    before Synapse is implemented.
    """

    async def fire(self, signal: Signal) -> None:
        """Drop the signal (no-op)."""
        pass


@dataclass
class NervousSystemConfig:
    """Configuration for the Nervous System."""

    # Signal types that bypass cortex (O(1) routing)
    spinal_reflexes: set[str] = field(
        default_factory=lambda: {
            "telemetry.heartbeat",
            "io.raw.read",
            "io.raw.write",
            "system.cpu_metrics",
            "system.memory_metrics",
            "system.disk_metrics",
            "system.network_metrics",
        }
    )

    # Signal types that are always flashbulb priority
    flashbulb_patterns: set[str] = field(
        default_factory=lambda: {
            "user.input",
            "error.critical",
            "security.alert",
        }
    )

    # Whether to log reflex signals to telemetry
    log_reflexes: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NervousSystemConfig":
        """Create from configuration dict (e.g., from YAML)."""
        return cls(
            spinal_reflexes=set(data.get("spinal_reflexes", cls().spinal_reflexes)),
            flashbulb_patterns=set(data.get("flashbulb_patterns", cls().flashbulb_patterns)),
            log_reflexes=data.get("log_reflexes", True),
        )


@dataclass
class TransmissionResult:
    """Result of signal transmission."""

    signal: Signal
    routed_to: str  # "reflex", "synapse", "dropped"
    logged: bool
    error: str | None = None


class NervousSystem:
    """
    Two-tier signal routing: Reflexes vs. Cortical processing.

    The Spinal Cord keeps the system responsive by routing noise
    away from the brain. High-frequency telemetry signals bypass
    cortical processing entirely.

    Usage:
        nervous = NervousSystem(telemetry_store, config)
        await nervous.transmit(Signal(
            signal_type="telemetry.heartbeat",
            data={"cpu": 45.2}
        ))
        # → Routed directly to telemetry (reflex path)

        await nervous.transmit(Signal(
            signal_type="shape.observed",
            data={"shape_type": "insight"}
        ))
        # → Routed to Synapse (cortical path)
    """

    def __init__(
        self,
        fast_store: ITelemetryStore | None = None,
        synapse: ISynapse | None = None,
        config: NervousSystemConfig | None = None,
    ):
        """
        Initialize the Nervous System.

        Args:
            fast_store: Telemetry store for reflex signals (bypass cortex)
            synapse: Synapse for cortical processing (can be None initially)
            config: Configuration for routing rules
        """
        self._fast_store = fast_store
        self._synapse = synapse or NullSynapse()
        self._config = config or NervousSystemConfig()
        # Metrics
        self._reflex_count = 0
        self._cortical_count = 0
        self._dropped_count = 0

    @property
    def config(self) -> NervousSystemConfig:
        """Get the nervous system configuration."""
        return self._config

    @property
    def metrics(self) -> dict[str, int]:
        """Get routing metrics."""
        return {
            "reflex_count": self._reflex_count,
            "cortical_count": self._cortical_count,
            "dropped_count": self._dropped_count,
            "total": self._reflex_count + self._cortical_count + self._dropped_count,
        }

    def set_synapse(self, synapse: ISynapse) -> None:
        """
        Set the Synapse for cortical processing.

        Called when Synapse becomes available (Phase 2).
        """
        self._synapse = synapse

    def set_fast_store(self, store: ITelemetryStore) -> None:
        """
        Set the fast store for reflex signals.

        Called during bootstrap when storage is initialized.
        """
        self._fast_store = store

    def classify_signal(self, signal: Signal) -> SignalPriority:
        """
        Classify a signal's priority (O(1) operation).

        Uses set membership for fast pattern matching.

        Args:
            signal: The signal to classify

        Returns:
            SignalPriority indicating routing destination
        """
        # Check flashbulb patterns first (highest priority)
        if signal.signal_type in self._config.flashbulb_patterns:
            return SignalPriority.FLASHBULB

        # Check reflex patterns (bypass cortex)
        if signal.signal_type in self._config.spinal_reflexes:
            return SignalPriority.REFLEX

        # Default to cortical processing
        return SignalPriority.CORTICAL

    def is_reflex(self, signal_type: str) -> bool:
        """
        Check if a signal type is a reflex (O(1)).

        Args:
            signal_type: The signal type to check

        Returns:
            True if the signal bypasses cortex
        """
        return signal_type in self._config.spinal_reflexes

    async def transmit(self, signal: Signal) -> TransmissionResult:
        """
        Route a signal through the nervous system.

        Routing logic:
        1. Classify signal priority (O(1) set lookup)
        2. REFLEX → Fast store (bypass cortex)
        3. FLASHBULB → Synapse with interrupt flag
        4. CORTICAL → Synapse for normal processing

        Args:
            signal: The signal to transmit

        Returns:
            TransmissionResult with routing info
        """
        # Step 1: Classify (O(1))
        priority = self.classify_signal(signal)
        signal.priority = priority

        # Step 2: Route based on priority
        if priority == SignalPriority.REFLEX:
            return await self._handle_reflex(signal)
        else:
            return await self._handle_cortical(signal)

    async def _handle_reflex(self, signal: Signal) -> TransmissionResult:
        """
        Handle reflex signal: bypass cortex, go to fast store.

        This is the "spinal cord" path - fast, direct, no thinking.
        """
        logged = False
        error = None

        if self._fast_store and self._config.log_reflexes:
            try:
                event = TelemetryEvent(
                    event_type=signal.signal_type,
                    timestamp=signal.timestamp,
                    data=signal.data,
                    instance_id=signal.instance_id,
                    project_hash=signal.project_hash,
                )
                await self._fast_store.append([event])
                logged = True
            except Exception as e:
                error = str(e)

        self._reflex_count += 1
        return TransmissionResult(
            signal=signal,
            routed_to="reflex",
            logged=logged,
            error=error,
        )

    async def _handle_cortical(self, signal: Signal) -> TransmissionResult:
        """
        Handle cortical signal: send to Synapse for processing.

        This is the "ascending pathway" - signals that need thinking.
        """
        error = None

        try:
            await self._synapse.fire(signal)
        except Exception as e:
            error = str(e)
            self._dropped_count += 1
            return TransmissionResult(
                signal=signal,
                routed_to="dropped",
                logged=False,
                error=error,
            )

        self._cortical_count += 1
        return TransmissionResult(
            signal=signal,
            routed_to="synapse",
            logged=True,  # Synapse handles logging
            error=error,
        )

    async def transmit_batch(self, signals: list[Signal]) -> list[TransmissionResult]:
        """
        Transmit multiple signals efficiently.

        Batches reflex signals for single telemetry append.

        Args:
            signals: List of signals to transmit

        Returns:
            List of TransmissionResults
        """
        results = []
        reflex_signals = []
        cortical_signals = []

        # Classify all signals first
        for signal in signals:
            priority = self.classify_signal(signal)
            signal.priority = priority
            if priority == SignalPriority.REFLEX:
                reflex_signals.append(signal)
            else:
                cortical_signals.append(signal)

        # Batch reflex signals
        if reflex_signals and self._fast_store and self._config.log_reflexes:
            events = [
                TelemetryEvent(
                    event_type=s.signal_type,
                    timestamp=s.timestamp,
                    data=s.data,
                    instance_id=s.instance_id,
                    project_hash=s.project_hash,
                )
                for s in reflex_signals
            ]
            try:
                await self._fast_store.append(events)
                for signal in reflex_signals:
                    results.append(
                        TransmissionResult(signal=signal, routed_to="reflex", logged=True)
                    )
                    self._reflex_count += 1
            except Exception as e:
                for signal in reflex_signals:
                    results.append(
                        TransmissionResult(
                            signal=signal,
                            routed_to="reflex",
                            logged=False,
                            error=str(e),
                        )
                    )
                    self._reflex_count += 1

        # Process cortical signals (can't batch - each needs individual processing)
        for signal in cortical_signals:
            result = await self._handle_cortical(signal)
            results.append(result)

        return results

    def add_reflex_pattern(self, pattern: str) -> None:
        """
        Dynamically add a reflex pattern.

        Useful for runtime configuration.

        Args:
            pattern: Signal type to add as reflex
        """
        self._config.spinal_reflexes.add(pattern)

    def remove_reflex_pattern(self, pattern: str) -> None:
        """
        Remove a reflex pattern.

        Args:
            pattern: Signal type to remove from reflexes
        """
        self._config.spinal_reflexes.discard(pattern)

    def add_flashbulb_pattern(self, pattern: str) -> None:
        """
        Add a flashbulb pattern (high-priority, interrupt dreaming).

        Args:
            pattern: Signal type to add as flashbulb
        """
        self._config.flashbulb_patterns.add(pattern)

    def reset_metrics(self) -> dict[str, int]:
        """
        Reset and return current metrics.

        Returns:
            Metrics before reset
        """
        metrics = self.metrics
        self._reflex_count = 0
        self._cortical_count = 0
        self._dropped_count = 0
        return metrics


# Convenience factory
def create_nervous_system(
    telemetry_store: ITelemetryStore | None = None,
    config_dict: dict[str, Any] | None = None,
) -> NervousSystem:
    """
    Create a NervousSystem with optional configuration.

    Args:
        telemetry_store: Fast store for reflex signals
        config_dict: Configuration dict (from YAML)

    Returns:
        Configured NervousSystem
    """
    config = NervousSystemConfig.from_dict(config_dict) if config_dict else NervousSystemConfig()
    return NervousSystem(fast_store=telemetry_store, config=config)
