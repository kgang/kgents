"""
Pulse: Zero-Cost Vitality Signals for Agent Health Monitoring.

The Pulse is a lightweight health signal that costs zero LLM tokens.
It captures essential vitality information without requiring inference:

- Pressure: Context pressure (0-1) from ContextWindow
- Phase: Current agent phase (thinking, acting, waiting)
- Content Hash: For loop detection (repeated same operations)
- Turn Count: For progress tracking

VitalityAnalyzer processes pulse streams to detect:
- Loops: Repeated content hashes (agent doing same thing)
- Rising Pressure: Context exhaustion approaching
- Erratic Intervals: Unstable processing patterns

AGENTESE: self.stream.pulse

Phase 2.3 Implementation.
"""

from __future__ import annotations

import hashlib
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from statistics import mean, stdev
from typing import Any


class AgentPhase(str, Enum):
    """Current phase of agent operation."""

    THINKING = "thinking"  # Processing, reasoning
    ACTING = "acting"  # Executing tools, writing
    WAITING = "waiting"  # Idle, awaiting input
    YIELDING = "yielding"  # Semaphore yield (Rodizio)
    CRYSTALLIZING = "crystallizing"  # Creating checkpoint


@dataclass(frozen=True)
class Pulse:
    """
    A single heartbeat from an agent.

    Immutable to ensure log consistency.
    Zero LLM cost - all fields are locally computed.

    Attributes:
        agent: Agent identifier (e.g., "l-gent", "k-gent")
        timestamp: When this pulse was generated
        pressure: Context pressure ratio (0.0 - 1.0)
        phase: Current agent phase
        content_hash: Hash of recent content for loop detection
        turn_count: Number of turns in current session
        metadata: Optional additional data (not logged by default)
    """

    agent: str
    timestamp: datetime
    pressure: float
    phase: AgentPhase
    content_hash: str
    turn_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def hash_content(content: str, truncate: int = 8) -> str:
        """Generate truncated hash of content for loop detection."""
        return hashlib.md5(content.encode()).hexdigest()[:truncate]

    def to_log(self) -> str:
        """
        Serialize to structured log format.

        Format: PULSE|agent=X|pressure=0.45|phase=thinking|hash=abc12345|turns=42|ts=ISO
        """
        parts = [
            "PULSE",
            f"agent={self.agent}",
            f"pressure={self.pressure:.2f}",
            f"phase={self.phase.value}",
            f"hash={self.content_hash}",
            f"turns={self.turn_count}",
            f"ts={self.timestamp.isoformat()}",
        ]
        return "|".join(parts)

    @classmethod
    def from_log(cls, log_line: str) -> "Pulse":
        """
        Deserialize from structured log format.

        Raises ValueError if format is invalid.
        """
        parts = log_line.strip().split("|")
        if not parts or parts[0] != "PULSE":
            raise ValueError(f"Invalid pulse log line: {log_line}")

        data: dict[str, str] = {}
        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                data[key] = value

        return cls(
            agent=data.get("agent", "unknown"),
            timestamp=datetime.fromisoformat(data["ts"]),
            pressure=float(data.get("pressure", 0)),
            phase=AgentPhase(data.get("phase", "waiting")),
            content_hash=data.get("hash", ""),
            turn_count=int(data.get("turns", 0)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent": self.agent,
            "timestamp": self.timestamp.isoformat(),
            "pressure": self.pressure,
            "phase": self.phase.value,
            "content_hash": self.content_hash,
            "turn_count": self.turn_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pulse":
        """Create from dictionary."""
        return cls(
            agent=data["agent"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            pressure=data["pressure"],
            phase=AgentPhase(data["phase"]),
            content_hash=data["content_hash"],
            turn_count=data["turn_count"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class VitalityStatus:
    """
    Analysis result from VitalityAnalyzer.

    Describes the health status of an agent based on pulse stream.
    """

    healthy: bool
    loop_detected: bool = False
    loop_count: int = 0
    pressure_warning: bool = False
    pressure_critical: bool = False
    erratic_intervals: bool = False
    interval_cv: float = 0.0  # Coefficient of variation
    message: str = ""
    recommendations: list[str] = field(default_factory=list)

    @property
    def severity(self) -> str:
        """Get severity level."""
        if self.pressure_critical or self.loop_count >= 5:
            return "critical"
        if self.loop_detected or self.pressure_warning or self.erratic_intervals:
            return "warning"
        return "ok"


@dataclass
class VitalityAnalyzer:
    """
    Analyzes pulse streams to detect health issues.

    Zero LLM cost - all analysis is rule-based.

    Usage:
        analyzer = VitalityAnalyzer()

        for pulse in pulse_stream:
            status = analyzer.ingest(pulse)
            if not status.healthy:
                handle_unhealthy(status)

    Configuration:
        loop_threshold: How many repeated hashes trigger loop detection
        pressure_warning: Pressure level for warning
        pressure_critical: Pressure level for critical
        window_size: Number of pulses to keep in history
        interval_cv_threshold: Coefficient of variation for erratic detection
    """

    # Detection thresholds
    loop_threshold: int = 3
    pressure_warning: float = 0.7
    pressure_critical: float = 0.9
    window_size: int = 50
    interval_cv_threshold: float = 1.0  # CV > 1 = erratic

    # Internal state
    _history: deque[Pulse] = field(default_factory=lambda: deque(maxlen=50))
    _hash_counts: dict[str, int] = field(default_factory=dict)
    _intervals: deque[float] = field(default_factory=lambda: deque(maxlen=20))
    _last_timestamp: datetime | None = None

    def __post_init__(self) -> None:
        """Initialize with correct maxlen."""
        self._history = deque(maxlen=self.window_size)
        self._intervals = deque(maxlen=20)

    def ingest(self, pulse: Pulse) -> VitalityStatus:
        """
        Process a new pulse and return vitality status.

        This is the main entry point. Call for each pulse received.
        """
        # Update history
        self._history.append(pulse)

        # Track intervals
        if self._last_timestamp is not None:
            interval = (pulse.timestamp - self._last_timestamp).total_seconds()
            self._intervals.append(interval)
        self._last_timestamp = pulse.timestamp

        # Track hash counts for loop detection
        self._hash_counts[pulse.content_hash] = (
            self._hash_counts.get(pulse.content_hash, 0) + 1
        )

        # Run analyses
        loop_detected, loop_count = self._detect_loop()
        pressure_warning = pulse.pressure >= self.pressure_warning
        pressure_critical = pulse.pressure >= self.pressure_critical
        erratic, interval_cv = self._detect_erratic_intervals()

        # Determine overall health
        healthy = not (loop_detected or pressure_critical or erratic)

        # Build message and recommendations
        message_parts = []
        recommendations = []

        if loop_detected:
            message_parts.append(f"Loop detected ({loop_count} repeats)")
            recommendations.append("Consider varying approach or yielding")

        if pressure_critical:
            message_parts.append(f"Critical pressure ({pulse.pressure:.0%})")
            recommendations.append("Compress context immediately")
        elif pressure_warning:
            message_parts.append(f"Pressure warning ({pulse.pressure:.0%})")
            recommendations.append("Consider summarizing recent history")

        if erratic:
            message_parts.append(f"Erratic intervals (CV={interval_cv:.2f})")
            recommendations.append("Check for blocking operations")

        message = "; ".join(message_parts) if message_parts else "Agent healthy"

        return VitalityStatus(
            healthy=healthy,
            loop_detected=loop_detected,
            loop_count=loop_count,
            pressure_warning=pressure_warning,
            pressure_critical=pressure_critical,
            erratic_intervals=erratic,
            interval_cv=interval_cv,
            message=message,
            recommendations=recommendations,
        )

    def _detect_loop(self, threshold: int | None = None) -> tuple[bool, int]:
        """
        Detect repeated content hashes indicating a loop.

        Returns (detected, count) where count is max repetitions.
        """
        threshold = threshold or self.loop_threshold

        # Find max count in recent history
        if not self._hash_counts:
            return False, 0

        max_count = max(self._hash_counts.values())
        return max_count >= threshold, max_count

    def _detect_erratic_intervals(self) -> tuple[bool, float]:
        """
        Detect erratic timing patterns.

        Uses coefficient of variation (CV = stdev/mean).
        CV > 1 indicates high variability relative to mean.
        """
        if len(self._intervals) < 5:
            return False, 0.0

        intervals = list(self._intervals)
        avg = mean(intervals)
        if avg == 0:
            return False, 0.0

        try:
            sd = stdev(intervals)
            cv = sd / avg
            return cv > self.interval_cv_threshold, cv
        except Exception:
            return False, 0.0

    def reset(self) -> None:
        """Reset analyzer state."""
        self._history.clear()
        self._hash_counts.clear()
        self._intervals.clear()
        self._last_timestamp = None

    def decay_hash_counts(self, factor: float = 0.5) -> None:
        """
        Decay hash counts to reduce sensitivity to old patterns.

        Call periodically to prevent permanent loop detection.
        """
        decayed = {k: max(1, int(v * factor)) for k, v in self._hash_counts.items()}
        # Remove counts that dropped to 1
        self._hash_counts = {k: v for k, v in decayed.items() if v > 1}

    @property
    def history(self) -> list[Pulse]:
        """Get pulse history (oldest first)."""
        return list(self._history)

    @property
    def stats(self) -> dict[str, Any]:
        """Get analyzer statistics."""
        return {
            "pulse_count": len(self._history),
            "unique_hashes": len(self._hash_counts),
            "max_hash_count": max(self._hash_counts.values())
            if self._hash_counts
            else 0,
            "interval_count": len(self._intervals),
            "avg_interval": mean(self._intervals) if self._intervals else 0,
        }


# === Factory Functions ===


def create_pulse(
    agent: str,
    pressure: float,
    phase: AgentPhase,
    content: str,
    turn_count: int,
    metadata: dict[str, Any] | None = None,
) -> Pulse:
    """
    Create a new pulse from current agent state.

    Args:
        agent: Agent identifier
        pressure: Current context pressure (0-1)
        phase: Current agent phase
        content: Recent content for hash generation
        turn_count: Current turn count
        metadata: Optional additional data

    Returns:
        New Pulse instance
    """
    return Pulse(
        agent=agent,
        timestamp=datetime.now(UTC),
        pressure=pressure,
        phase=phase,
        content_hash=Pulse.hash_content(content),
        turn_count=turn_count,
        metadata=metadata or {},
    )


def create_pulse_from_window(
    agent: str,
    window: Any,  # ContextWindow
    phase: AgentPhase,
    metadata: dict[str, Any] | None = None,
) -> Pulse:
    """
    Create a pulse from a ContextWindow.

    Extracts pressure, turn count, and content hash from the window.
    """
    # Get most recent content for hash
    recent_content = ""
    if hasattr(window, "extract"):
        turn = window.extract()
        if turn is not None:
            recent_content = turn.content

    return Pulse(
        agent=agent,
        timestamp=datetime.now(UTC),
        pressure=window.pressure if hasattr(window, "pressure") else 0.0,
        phase=phase,
        content_hash=Pulse.hash_content(recent_content),
        turn_count=len(window) if hasattr(window, "__len__") else 0,
        metadata=metadata or {},
    )


def create_analyzer(
    loop_threshold: int = 3,
    pressure_warning: float = 0.7,
    pressure_critical: float = 0.9,
    window_size: int = 50,
) -> VitalityAnalyzer:
    """Create a configured VitalityAnalyzer."""
    return VitalityAnalyzer(
        loop_threshold=loop_threshold,
        pressure_warning=pressure_warning,
        pressure_critical=pressure_critical,
        window_size=window_size,
    )
