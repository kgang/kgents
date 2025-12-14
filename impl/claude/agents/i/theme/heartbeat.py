"""
HeartbeatMixin - Pulse animation for agent cards.

Every agent card pulses with life, indicating activity level.
The pulse rate (BPM) maps to agent event rate:
- Dormant agents: slow pulse (30-40 BPM)
- Active agents: moderate pulse (60-80 BPM)
- High activity: fast pulse (100-180 BPM)

The animation uses sinusoidal modulation for a natural heartbeat feel.

Performance:
- Animation automatically disabled if FPS drops below 30
- Batch updates across all animated widgets
- Minimal memory footprint
"""

from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from textual.app import App


class HeartbeatMixin:
    """
    Mixin that adds pulse animation to any widget.

    Usage:
        class AgentCard(Static, HeartbeatMixin):
            def __init__(self, ...):
                super().__init__(...)
                HeartbeatMixin.__init__(self)

            def render(self):
                opacity = self.get_pulse_opacity()
                # Use opacity for border/glow effect
    """

    def __init__(self) -> None:
        """Initialize heartbeat state."""
        self._pulse_phase: float = 0.0
        self._bpm: int = 60  # Default: calm
        self._last_update: float = time.monotonic()
        self._animation_enabled: bool = True

    def set_bpm(self, bpm: int) -> None:
        """
        Set beats per minute based on agent activity.

        Args:
            bpm: Beats per minute (clamped to 30-180)
        """
        self._bpm = max(30, min(180, bpm))

    def get_bpm(self) -> int:
        """Get current BPM."""
        return self._bpm

    def update_pulse(self, dt: float | None = None) -> None:
        """
        Update pulse phase based on elapsed time.

        Args:
            dt: Delta time in seconds. If None, calculated from last update.
        """
        if not self._animation_enabled:
            return

        now = time.monotonic()
        if dt is None:
            dt = now - self._last_update
        self._last_update = now

        # Calculate phase increment based on BPM
        # 60 BPM = 1 beat per second = 2π radians per second
        beats_per_second = self._bpm / 60.0
        radians_per_second = beats_per_second * 2 * math.pi
        self._pulse_phase += radians_per_second * dt

        # Keep phase in reasonable range
        if self._pulse_phase > 2 * math.pi:
            self._pulse_phase -= 2 * math.pi

    def get_pulse_opacity(self) -> float:
        """
        Return current opacity for pulse effect.

        Returns:
            Float between 0.7 and 1.0 (sinusoidal pulse)
        """
        if not self._animation_enabled:
            return 1.0

        # Sinusoidal pulse: varies between 0.7 and 1.0
        return 0.7 + 0.3 * math.sin(self._pulse_phase)

    def get_pulse_intensity(self) -> float:
        """
        Get pulse intensity as a 0-1 value.

        Useful for more dramatic effects like border glow.

        Returns:
            Float between 0.0 and 1.0
        """
        if not self._animation_enabled:
            return 0.5

        # Convert sin output (-1 to 1) to (0 to 1)
        return 0.5 + 0.5 * math.sin(self._pulse_phase)

    def get_pulse_border_char(self) -> str:
        """
        Get a border character that varies with pulse.

        Returns:
            Border character ('─', '═', or '━')
        """
        intensity = self.get_pulse_intensity()
        if intensity < 0.33:
            return "─"
        elif intensity < 0.66:
            return "═"
        else:
            return "━"

    def enable_animation(self) -> None:
        """Enable pulse animation."""
        self._animation_enabled = True
        self._last_update = time.monotonic()

    def disable_animation(self) -> None:
        """Disable pulse animation (for performance)."""
        self._animation_enabled = False

    def is_animation_enabled(self) -> bool:
        """Check if animation is enabled."""
        return self._animation_enabled

    @staticmethod
    def activity_to_bpm(activity: float) -> int:
        """
        Convert activity level (0-1) to BPM.

        Args:
            activity: Activity level from 0.0 to 1.0

        Returns:
            BPM value (30-180)
        """
        # Linear mapping: 0.0 → 30 BPM, 1.0 → 180 BPM
        return int(30 + activity * 150)

    @staticmethod
    def phase_to_bpm(phase: str) -> int:
        """
        Convert agent phase to suggested BPM.

        Args:
            phase: Agent phase name

        Returns:
            Suggested BPM
        """
        phase_bpm = {
            "DORMANT": 30,
            "WAKING": 50,
            "ACTIVE": 80,
            "WANING": 50,
            "VOID": 40,
        }
        return phase_bpm.get(phase.upper(), 60)


class HeartbeatController:
    """
    Controller that manages heartbeat animations across multiple widgets.

    Handles:
    - Batch updates for efficiency
    - FPS monitoring and automatic animation disable
    - Global animation control
    """

    # Singleton instance
    _instance: HeartbeatController | None = None

    def __init__(self) -> None:
        """Initialize the controller."""
        self._widgets: list[HeartbeatMixin] = []
        self._fps_samples: list[float] = []
        self._last_frame_time: float = time.monotonic()
        self._animation_enabled: bool = True
        self._fps_threshold: int = 30  # Disable below this FPS
        self._update_callback: Callable[[], None] | None = None

    @classmethod
    def get_instance(cls) -> HeartbeatController:
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = HeartbeatController()
        return cls._instance

    def register(self, widget: HeartbeatMixin) -> None:
        """
        Register a widget for heartbeat updates.

        Args:
            widget: Widget with HeartbeatMixin
        """
        if widget not in self._widgets:
            self._widgets.append(widget)

    def unregister(self, widget: HeartbeatMixin) -> None:
        """
        Unregister a widget from heartbeat updates.

        Args:
            widget: Widget to unregister
        """
        if widget in self._widgets:
            self._widgets.remove(widget)

    def update_all(self) -> None:
        """Update all registered widgets."""
        if not self._animation_enabled:
            return

        now = time.monotonic()
        dt = now - self._last_frame_time
        self._last_frame_time = now

        # Track FPS
        if dt > 0:
            fps = 1.0 / dt
            self._fps_samples.append(fps)
            self._fps_samples = self._fps_samples[-30:]  # Keep last 30 samples

            # Check if we should disable animation
            if len(self._fps_samples) >= 10:
                avg_fps = sum(self._fps_samples) / len(self._fps_samples)
                if avg_fps < self._fps_threshold:
                    self._disable_all_animations()
                    return

        # Update all widgets
        for widget in self._widgets:
            widget.update_pulse(dt)

    def get_average_fps(self) -> float:
        """Get average FPS from recent samples."""
        if not self._fps_samples:
            return 60.0
        return sum(self._fps_samples) / len(self._fps_samples)

    def enable_animations(self) -> None:
        """Enable animations globally."""
        self._animation_enabled = True
        for widget in self._widgets:
            widget.enable_animation()

    def disable_animations(self) -> None:
        """Disable animations globally."""
        self._animation_enabled = False
        self._disable_all_animations()

    def _disable_all_animations(self) -> None:
        """Disable animation on all widgets."""
        for widget in self._widgets:
            widget.disable_animation()

    def is_animation_healthy(self) -> bool:
        """Check if animation performance is healthy."""
        return self.get_average_fps() >= self._fps_threshold

    def get_widget_count(self) -> int:
        """Get number of registered widgets."""
        return len(self._widgets)


def get_heartbeat_controller() -> HeartbeatController:
    """Get the global heartbeat controller instance."""
    return HeartbeatController.get_instance()


__all__ = [
    "HeartbeatMixin",
    "HeartbeatController",
    "get_heartbeat_controller",
]
