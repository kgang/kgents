"""
Compliance Timers: Regulatory Deadline Management.

Crisis simulations must respect real-world compliance requirements.
This module provides timers for:
- GDPR 72-hour breach notification
- SEC 4-day disclosure
- HIPAA breach notification
- Custom organizational SLAs

From Immersive Labs: "Challenge teams to prioritize actions,
assess risks, and make decisions under tight time constraints."

See: plans/core-apps/domain-simulation.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Callable

# =============================================================================
# Timer Types
# =============================================================================


class TimerType(Enum):
    """Types of compliance timers."""

    GDPR_72H = auto()  # GDPR Article 33 - 72 hours
    SEC_4DAY = auto()  # SEC 8-K filing - 4 business days
    HIPAA_60DAY = auto()  # HIPAA breach notification - 60 days
    INTERNAL_SLA = auto()  # Custom internal SLA
    CUSTOM = auto()  # User-defined deadline


class TimerStatus(Enum):
    """Timer status."""

    PENDING = auto()  # Not yet started
    ACTIVE = auto()  # Running
    WARNING = auto()  # Approaching deadline
    CRITICAL = auto()  # Very close to deadline
    EXPIRED = auto()  # Deadline passed
    COMPLETED = auto()  # Timer stopped successfully
    PAUSED = auto()  # Timer paused (rare)


# =============================================================================
# Timer Configuration
# =============================================================================


@dataclass(frozen=True)
class TimerConfig:
    """Configuration for a compliance timer."""

    timer_type: TimerType
    name: str
    description: str
    duration: timedelta
    warning_threshold: float = 0.75  # % of time elapsed before warning
    critical_threshold: float = 0.90  # % of time elapsed before critical
    can_pause: bool = False  # Most compliance timers cannot be paused
    extensions_allowed: int = 0  # Number of extensions permitted


# Predefined timer configurations
GDPR_72H_CONFIG = TimerConfig(
    timer_type=TimerType.GDPR_72H,
    name="GDPR 72-Hour Notification",
    description="Article 33 requires notification to supervisory authority within 72 hours of becoming aware of a personal data breach.",
    duration=timedelta(hours=72),
    warning_threshold=0.75,  # 54 hours
    critical_threshold=0.90,  # 64.8 hours
    can_pause=False,
    extensions_allowed=0,
)

SEC_4DAY_CONFIG = TimerConfig(
    timer_type=TimerType.SEC_4DAY,
    name="SEC 8-K Disclosure",
    description="Item 1.05 requires disclosure of material cybersecurity incidents within 4 business days.",
    duration=timedelta(days=4),
    warning_threshold=0.70,
    critical_threshold=0.85,
    can_pause=False,
    extensions_allowed=0,
)

HIPAA_60DAY_CONFIG = TimerConfig(
    timer_type=TimerType.HIPAA_60DAY,
    name="HIPAA Breach Notification",
    description="HIPAA Breach Notification Rule requires notification within 60 days.",
    duration=timedelta(days=60),
    warning_threshold=0.80,
    critical_threshold=0.95,
    can_pause=False,
    extensions_allowed=0,
)

TIMER_CONFIGS: dict[TimerType, TimerConfig] = {
    TimerType.GDPR_72H: GDPR_72H_CONFIG,
    TimerType.SEC_4DAY: SEC_4DAY_CONFIG,
    TimerType.HIPAA_60DAY: HIPAA_60DAY_CONFIG,
}


# =============================================================================
# Timer State
# =============================================================================


@dataclass
class TimerState:
    """
    Runtime state of a compliance timer.

    Tracks elapsed time, status, and any pauses/extensions.
    """

    config: TimerConfig
    status: TimerStatus = TimerStatus.PENDING
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    paused_at: datetime | None = None
    total_paused_duration: timedelta = field(default_factory=lambda: timedelta())
    extensions_used: int = 0

    @property
    def is_active(self) -> bool:
        """Check if timer is currently active."""
        return self.status in (
            TimerStatus.ACTIVE,
            TimerStatus.WARNING,
            TimerStatus.CRITICAL,
        )

    @property
    def elapsed(self) -> timedelta:
        """Get elapsed time (excluding pauses)."""
        if self.started_at is None:
            return timedelta()

        if self.stopped_at is not None:
            end = self.stopped_at
        elif self.paused_at is not None:
            end = self.paused_at
        else:
            end = datetime.now()

        return end - self.started_at - self.total_paused_duration

    @property
    def remaining(self) -> timedelta:
        """Get remaining time."""
        if self.status == TimerStatus.EXPIRED:
            return timedelta()
        return max(timedelta(), self.config.duration - self.elapsed)

    @property
    def progress(self) -> float:
        """Get progress as fraction (0.0 to 1.0+)."""
        if self.config.duration.total_seconds() == 0:
            return 1.0
        return self.elapsed.total_seconds() / self.config.duration.total_seconds()

    def start(self) -> None:
        """Start the timer."""
        if self.status != TimerStatus.PENDING:
            raise ValueError(f"Cannot start timer in status: {self.status}")
        self.started_at = datetime.now()
        self.status = TimerStatus.ACTIVE

    def stop(self, success: bool = True) -> None:
        """Stop the timer."""
        if not self.is_active and self.status != TimerStatus.PAUSED:
            raise ValueError(f"Cannot stop timer in status: {self.status}")
        self.stopped_at = datetime.now()
        self.status = TimerStatus.COMPLETED if success else TimerStatus.EXPIRED

    def pause(self) -> None:
        """Pause the timer (if allowed)."""
        if not self.config.can_pause:
            raise ValueError("This timer cannot be paused")
        if not self.is_active:
            raise ValueError(f"Cannot pause timer in status: {self.status}")
        self.paused_at = datetime.now()
        self.status = TimerStatus.PAUSED

    def resume(self) -> None:
        """Resume a paused timer."""
        if self.status != TimerStatus.PAUSED:
            raise ValueError(f"Cannot resume timer in status: {self.status}")
        if self.paused_at is not None:
            pause_duration = datetime.now() - self.paused_at
            self.total_paused_duration += pause_duration
            self.paused_at = None
        self.status = TimerStatus.ACTIVE
        self._update_status()

    def tick(self) -> TimerStatus:
        """
        Update timer status based on current time.

        Should be called periodically to update warning/critical/expired states.
        """
        self._update_status()
        return self.status

    def _update_status(self) -> None:
        """Internal status update based on progress."""
        if self.status in (
            TimerStatus.PENDING,
            TimerStatus.COMPLETED,
            TimerStatus.PAUSED,
        ):
            return

        progress = self.progress

        if progress >= 1.0:
            self.status = TimerStatus.EXPIRED
            self.stopped_at = (
                self.started_at + self.config.duration if self.started_at else None
            )
        elif progress >= self.config.critical_threshold:
            self.status = TimerStatus.CRITICAL
        elif progress >= self.config.warning_threshold:
            self.status = TimerStatus.WARNING
        else:
            self.status = TimerStatus.ACTIVE

    def extend(self, duration: timedelta) -> None:
        """Extend the timer deadline (if allowed)."""
        if self.extensions_used >= self.config.extensions_allowed:
            raise ValueError("No extensions remaining")
        # This would modify the config, but configs are frozen
        # In practice, we'd track this differently
        self.extensions_used += 1

    def manifest(self) -> dict[str, Any]:
        """Get timer state as dictionary for display."""
        remaining = self.remaining
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        seconds = int(remaining.total_seconds() % 60)

        return {
            "name": self.config.name,
            "type": self.config.timer_type.name,
            "status": self.status.name,
            "remaining": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            "remaining_seconds": remaining.total_seconds(),
            "progress": self.progress,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "elapsed_seconds": self.elapsed.total_seconds(),
            "warning_at": self.config.warning_threshold,
            "critical_at": self.config.critical_threshold,
        }


# =============================================================================
# Timer Factory
# =============================================================================


def create_timer(
    timer_type: TimerType,
    custom_duration: timedelta | None = None,
    custom_name: str | None = None,
) -> TimerState:
    """
    Create a timer of the specified type.

    Args:
        timer_type: The type of compliance timer
        custom_duration: Override duration (for CUSTOM type)
        custom_name: Override name (for CUSTOM type)

    Returns:
        Configured TimerState ready to start
    """
    if timer_type == TimerType.CUSTOM:
        if custom_duration is None:
            raise ValueError("Custom timer requires duration")
        config = TimerConfig(
            timer_type=TimerType.CUSTOM,
            name=custom_name or "Custom Timer",
            description="User-defined deadline",
            duration=custom_duration,
            can_pause=True,
            extensions_allowed=1,
        )
    elif timer_type == TimerType.INTERNAL_SLA:
        config = TimerConfig(
            timer_type=TimerType.INTERNAL_SLA,
            name=custom_name or "Internal SLA",
            description="Organization-specific service level agreement",
            duration=custom_duration or timedelta(hours=4),
            can_pause=True,
            extensions_allowed=2,
        )
    else:
        maybe_config = TIMER_CONFIGS.get(timer_type)
        if maybe_config is None:
            raise ValueError(f"Unknown timer type: {timer_type}")
        config = maybe_config

    return TimerState(config=config)


def create_gdpr_timer() -> TimerState:
    """Create a GDPR 72-hour timer."""
    return create_timer(TimerType.GDPR_72H)


def create_sec_timer() -> TimerState:
    """Create an SEC 4-day timer."""
    return create_timer(TimerType.SEC_4DAY)


def create_hipaa_timer() -> TimerState:
    """Create a HIPAA 60-day timer."""
    return create_timer(TimerType.HIPAA_60DAY)


# =============================================================================
# Timer Display Utilities
# =============================================================================


def format_countdown(timer: TimerState) -> str:
    """Format timer as countdown string."""
    remaining = timer.remaining
    hours = int(remaining.total_seconds() // 3600)
    minutes = int((remaining.total_seconds() % 3600) // 60)
    seconds = int(remaining.total_seconds() % 60)

    if timer.status == TimerStatus.EXPIRED:
        return "⏰ EXPIRED"
    elif timer.status == TimerStatus.CRITICAL:
        return f"🚨 {hours:02d}:{minutes:02d}:{seconds:02d}"
    elif timer.status == TimerStatus.WARNING:
        return f"⚠️ {hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"⏱️ {hours:02d}:{minutes:02d}:{seconds:02d}"


def get_status_color(timer: TimerState) -> str:
    """Get color code for timer status (for UI)."""
    status_colors = {
        TimerStatus.PENDING: "gray",
        TimerStatus.ACTIVE: "green",
        TimerStatus.WARNING: "yellow",
        TimerStatus.CRITICAL: "red",
        TimerStatus.EXPIRED: "darkred",
        TimerStatus.COMPLETED: "blue",
        TimerStatus.PAUSED: "orange",
    }
    return status_colors.get(timer.status, "gray")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "TimerType",
    "TimerStatus",
    # Config
    "TimerConfig",
    "GDPR_72H_CONFIG",
    "SEC_4DAY_CONFIG",
    "HIPAA_60DAY_CONFIG",
    "TIMER_CONFIGS",
    # State
    "TimerState",
    # Factory
    "create_timer",
    "create_gdpr_timer",
    "create_sec_timer",
    "create_hipaa_timer",
    # Display
    "format_countdown",
    "get_status_color",
]
