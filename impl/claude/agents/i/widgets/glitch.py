"""
Glitch System - Making entropy visible.

The glitch effect is the visual manifestation of the Accursed Share.
When void.* is invoked or errors occur, the interface briefly corrupts.

"The void is not absence—it is the Accursed Share made visible."

Effects:
- Zalgo text corruption (combining characters)
- Color inversion flashes
- Random character substitution
- Border distortion
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult

# Zalgo combining characters for glitch effect
ZALGO_ABOVE = [
    "\u0300",
    "\u0301",
    "\u0302",
    "\u0303",
    "\u0304",
    "\u0305",
    "\u0306",
    "\u0307",
    "\u0308",
    "\u0309",
    "\u030a",
    "\u030b",
    "\u030c",
    "\u030d",
    "\u030e",
    "\u030f",
    "\u0310",
    "\u0311",
]
ZALGO_BELOW = [
    "\u0316",
    "\u0317",
    "\u0318",
    "\u0319",
    "\u031a",
    "\u031b",
    "\u031c",
    "\u031d",
    "\u031e",
    "\u031f",
    "\u0320",
    "\u0321",
    "\u0322",
    "\u0323",
    "\u0324",
    "\u0325",
    "\u0326",
    "\u0327",
]
ZALGO_MIDDLE = [
    "\u0334",
    "\u0335",
    "\u0336",
    "\u0337",
    "\u0338",
]

# Glitch substitution characters
GLITCH_CHARS = "▚▞▛▜▙▟▀▄█░▒▓"

# Corruption patterns
CORRUPTION_CHARS = "!@#$%^&*(){}[]|\\;:'\",.<>?/~`"


class GlitchType(Enum):
    """Types of glitch effects."""

    ZALGO = "zalgo"  # Combining character corruption
    SUBSTITUTE = "substitute"  # Random character substitution
    INVERT = "invert"  # Conceptual inversion (for colors)
    DISTORT = "distort"  # Border/shape distortion


@dataclass
class GlitchConfig:
    """Configuration for a glitch effect."""

    intensity: float = 0.3  # 0.0-1.0, how much corruption
    duration_ms: int = 200  # How long the glitch lasts
    glitch_type: GlitchType = GlitchType.ZALGO
    spread: bool = False  # Whether effect spreads to neighbors
    zalgo_depth: int = 2  # Max combining chars per character


def add_zalgo(
    text: str,
    intensity: float = 0.3,
    depth: int = 2,
) -> str:
    """
    Add Zalgo-style corruption to text.

    Args:
        text: The text to corrupt
        intensity: Probability of corrupting each character (0.0-1.0)
        depth: Maximum combining characters per character

    Returns:
        Corrupted text with Zalgo combining characters
    """
    result = []
    for char in text:
        result.append(char)
        if random.random() < intensity:
            # Add random combining characters
            num_above = random.randint(0, depth)
            num_below = random.randint(0, depth)
            num_middle = random.randint(0, max(1, depth // 2))

            for _ in range(num_above):
                result.append(random.choice(ZALGO_ABOVE))
            for _ in range(num_middle):
                result.append(random.choice(ZALGO_MIDDLE))
            for _ in range(num_below):
                result.append(random.choice(ZALGO_BELOW))

    return "".join(result)


def substitute_chars(
    text: str,
    intensity: float = 0.3,
    use_glitch: bool = True,
) -> str:
    """
    Randomly substitute characters with glitch characters.

    Args:
        text: The text to corrupt
        intensity: Probability of substituting each character
        use_glitch: Use block glitch chars vs ASCII corruption

    Returns:
        Text with random substitutions
    """
    chars = GLITCH_CHARS if use_glitch else CORRUPTION_CHARS
    result = []
    for char in text:
        if random.random() < intensity and char not in " \n\t":
            result.append(random.choice(chars))
        else:
            result.append(char)
    return "".join(result)


def distort_border(
    text: str,
    intensity: float = 0.3,
) -> str:
    """
    Distort border characters in text.

    Replaces box-drawing characters with corrupted versions.
    """
    border_chars = "─│┌┐└┘├┤┬┴┼"
    distorted = "═║╔╗╚╝╠╣╦╩╬"

    result = []
    for char in text:
        if char in border_chars and random.random() < intensity:
            idx = border_chars.index(char)
            result.append(
                distorted[idx] if random.random() > 0.5 else random.choice(GLITCH_CHARS)
            )
        else:
            result.append(char)
    return "".join(result)


def apply_glitch(
    text: str,
    config: GlitchConfig | None = None,
) -> str:
    """
    Apply glitch effect to text based on configuration.

    Args:
        text: The text to corrupt
        config: Glitch configuration (uses defaults if None)

    Returns:
        Corrupted text
    """
    if config is None:
        config = GlitchConfig()

    if config.glitch_type == GlitchType.ZALGO:
        return add_zalgo(text, config.intensity, config.zalgo_depth)
    elif config.glitch_type == GlitchType.SUBSTITUTE:
        return substitute_chars(text, config.intensity)
    elif config.glitch_type == GlitchType.DISTORT:
        return distort_border(text, config.intensity)
    else:
        return text


@dataclass
class GlitchEvent:
    """Record of a glitch event."""

    target_id: str  # Widget or agent ID
    glitch_type: GlitchType
    intensity: float
    duration_ms: int
    timestamp: float = field(
        default_factory=lambda: asyncio.get_event_loop().time()
        if asyncio.get_event_loop().is_running()
        else 0
    )
    source: str = ""  # What caused the glitch (e.g., "void.sip", "error")


class GlitchController:
    """
    Coordinates glitch effects across the UI.

    The GlitchController maintains state about active glitches and
    provides a unified API for triggering effects.

    Usage:
        controller = GlitchController()
        controller.subscribe(my_glitch_callback)

        # Trigger a glitch on a specific agent
        await controller.trigger_agent_glitch("robin", duration_ms=200)

        # Trigger a global glitch (void.sip)
        await controller.trigger_global_glitch(intensity=0.3)

        # Auto-trigger on error
        controller.on_error(some_exception)
    """

    def __init__(self) -> None:
        self._callbacks: list[Callable[[GlitchEvent], None]] = []
        self._active_glitches: dict[str, GlitchEvent] = {}
        self._history: list[GlitchEvent] = []
        self._max_history = 100

    def subscribe(self, callback: Callable[[GlitchEvent], None]) -> None:
        """Subscribe to glitch events."""
        self._callbacks.append(callback)

    def unsubscribe(self, callback: Callable[[GlitchEvent], None]) -> None:
        """Unsubscribe from glitch events."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _emit(self, event: GlitchEvent) -> None:
        """Emit a glitch event to all subscribers."""
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

        for callback in self._callbacks:
            try:
                callback(event)
            except Exception:
                pass  # Don't let callback errors break the controller

    async def trigger_agent_glitch(
        self,
        agent_id: str,
        duration_ms: int = 200,
        intensity: float = 0.3,
        glitch_type: GlitchType = GlitchType.ZALGO,
        source: str = "",
    ) -> None:
        """
        Trigger a glitch effect on a specific agent card.

        Args:
            agent_id: The ID of the agent to glitch
            duration_ms: How long the glitch lasts
            intensity: How intense the corruption is (0.0-1.0)
            glitch_type: Type of glitch effect
            source: What caused the glitch (for logging)
        """
        event = GlitchEvent(
            target_id=agent_id,
            glitch_type=glitch_type,
            intensity=intensity,
            duration_ms=duration_ms,
            source=source or "agent_glitch",
        )
        self._active_glitches[agent_id] = event
        self._emit(event)

        # Schedule cleanup
        await asyncio.sleep(duration_ms / 1000.0)

        if agent_id in self._active_glitches:
            del self._active_glitches[agent_id]

    async def trigger_global_glitch(
        self,
        intensity: float = 0.3,
        duration_ms: int = 100,
        source: str = "void.sip",
    ) -> None:
        """
        Trigger a brief screen-wide glitch.

        Used when void.sip is invoked or for dramatic effect.

        Args:
            intensity: How intense the corruption is
            duration_ms: How long the glitch lasts
            source: What caused the glitch
        """
        event = GlitchEvent(
            target_id="*",  # Special ID for global
            glitch_type=GlitchType.ZALGO,
            intensity=intensity,
            duration_ms=duration_ms,
            source=source,
        )
        self._active_glitches["*"] = event
        self._emit(event)

        await asyncio.sleep(duration_ms / 1000.0)

        if "*" in self._active_glitches:
            del self._active_glitches["*"]

    def on_error(
        self,
        error: Exception,
        target_id: str = "status_bar",
    ) -> GlitchEvent:
        """
        Auto-trigger a glitch on error.

        Returns the GlitchEvent for the caller to handle.
        Note: This is synchronous; caller should handle async if needed.

        Args:
            error: The exception that occurred
            target_id: Where to show the glitch (default: status bar)

        Returns:
            The glitch event that was created
        """
        event = GlitchEvent(
            target_id=target_id,
            glitch_type=GlitchType.SUBSTITUTE,
            intensity=0.5,
            duration_ms=300,
            source=f"error:{type(error).__name__}",
        )
        self._active_glitches[target_id] = event
        self._emit(event)
        return event

    def on_void_phase(self, agent_id: str) -> GlitchEvent:
        """
        Trigger glitch when agent enters VOID phase.

        Returns the GlitchEvent for the caller to handle.
        """
        event = GlitchEvent(
            target_id=agent_id,
            glitch_type=GlitchType.ZALGO,
            intensity=0.4,
            duration_ms=200,
            source="phase:VOID",
        )
        self._active_glitches[agent_id] = event
        self._emit(event)
        return event

    def is_glitching(self, target_id: str) -> bool:
        """Check if a target is currently glitching."""
        return target_id in self._active_glitches or "*" in self._active_glitches

    def get_active_glitches(self) -> dict[str, GlitchEvent]:
        """Get all currently active glitches."""
        return self._active_glitches.copy()

    def get_history(self) -> list[GlitchEvent]:
        """Get glitch history."""
        return self._history.copy()

    def clear_glitch(self, target_id: str) -> None:
        """Manually clear a glitch."""
        if target_id in self._active_glitches:
            del self._active_glitches[target_id]


class GlitchIndicator(Widget):
    """
    Visual indicator that glitch is active.

    Shows a small corruption indicator in the corner
    when glitch effects are happening.
    """

    DEFAULT_CSS = """
    GlitchIndicator {
        width: 3;
        height: 1;
        color: #9b59b6;
    }

    GlitchIndicator.active {
        color: #e88a8a;
    }
    """

    active: reactive[bool] = reactive(False)
    intensity: reactive[float] = reactive(0.0)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)

    def render(self) -> "RenderResult":
        """Render the glitch indicator."""
        if not self.active:
            return "   "

        # More glitchy as intensity increases
        if self.intensity > 0.7:
            return add_zalgo("▓", 0.8, 3)
        elif self.intensity > 0.4:
            return add_zalgo("▒", 0.5, 2)
        else:
            return add_zalgo("░", 0.3, 1)

    def watch_active(self, value: bool) -> None:
        """React to active state changes."""
        if value:
            self.add_class("active")
        else:
            self.remove_class("active")
        self.refresh()

    def watch_intensity(self, value: float) -> None:
        """React to intensity changes."""
        self.refresh()

    def set_glitch(self, active: bool, intensity: float = 0.3) -> None:
        """Set the glitch state."""
        self.active = active
        self.intensity = intensity


# Convenience function for creating glitched text for status messages
def glitch_message(
    message: str,
    intensity: float = 0.3,
) -> str:
    """
    Create a glitched version of a message.

    Use this for status bar messages, error displays, etc.

    Args:
        message: The message to glitch
        intensity: How much to corrupt (0.0-1.0)

    Returns:
        Glitched message string
    """
    return add_zalgo(message, intensity, depth=2)


# Singleton controller for app-wide glitch coordination
_global_controller: GlitchController | None = None


def get_glitch_controller() -> GlitchController:
    """Get the global glitch controller."""
    global _global_controller
    if _global_controller is None:
        _global_controller = GlitchController()
    return _global_controller
