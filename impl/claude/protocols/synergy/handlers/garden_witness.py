"""
Garden to Witness Handler: Auto-capture garden gestures to Witness thought stream.

When garden gestures are applied, this handler automatically captures
the gesture as a thought in the Witness's thought stream.

This enables:
- Real-time visibility of tending activity in the WitnessOverlay
- Historical gesture tracking in the thought stream
- Cross-jewel awareness between Garden and Witness

Phase 2: Witness Integration for Self.Garden.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..events import SynergyEvent, SynergyEventType, SynergyResult
from .base import BaseSynergyHandler

if TYPE_CHECKING:
    from services.witness.persistence import WitnessPersistence


class GardenToWitnessHandler(BaseSynergyHandler):
    """
    Handler that captures garden gestures to Witness thought stream.

    Handles:
    1. GESTURE_APPLIED: Captures gestures as thoughts with source='gardener'

    The thought content includes the gesture verb, target, and reasoning
    for visibility in the WitnessOverlay.
    """

    # Events this handler subscribes to
    SUPPORTED_EVENTS = frozenset({SynergyEventType.GESTURE_APPLIED})

    def __init__(
        self,
        witness_persistence: "WitnessPersistence | None" = None,
    ) -> None:
        """
        Initialize the handler.

        Args:
            witness_persistence: Optional WitnessPersistence instance.
                                If None, will attempt to get from DI container.
        """
        super().__init__()
        self._witness_persistence = witness_persistence

    @property
    def name(self) -> str:
        return "GardenToWitnessHandler"

    async def _get_persistence(self) -> "WitnessPersistence | None":
        """Get or create WitnessPersistence instance."""
        if self._witness_persistence is not None:
            return self._witness_persistence

        try:
            # Use the DI provider pattern
            from services.providers import get_witness_persistence

            self._witness_persistence = await get_witness_persistence()
            return self._witness_persistence
        except Exception as e:
            self._logger.error(f"Failed to get WitnessPersistence: {e}")
            return None

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle a garden synergy event."""
        if event.event_type == SynergyEventType.GESTURE_APPLIED:
            return await self._handle_gesture_applied(event)
        else:
            return self.skip(f"Not handling {event.event_type.value}")

    async def _handle_gesture_applied(self, event: SynergyEvent) -> SynergyResult:
        """
        Handle a gesture applied event.

        Captures the gesture as a thought in the Witness thought stream.
        """
        payload = event.payload
        verb = payload.get("verb", "?")
        target = payload.get("target", "?")
        state_changed = payload.get("state_changed", False)
        reasoning = payload.get("reasoning", "")
        entropy_cost = payload.get("entropy_cost", 0.0)

        # Create thought content
        # Use emoji for verb
        verb_emoji = {
            "OBSERVE": "👁️",
            "PRUNE": "✂️",
            "GRAFT": "🌿",
            "WATER": "💧",
            "ROTATE": "🔄",
            "WAIT": "⏳",
        }.get(verb, "🌱")

        # Build thought content
        if reasoning:
            content = f"{verb_emoji} {verb} on {target}: {reasoning}"
        else:
            content = f"{verb_emoji} {verb} on {target}"

        # Determine tags based on gesture
        tags = ["tending", verb.lower()]
        if state_changed:
            tags.append("state-change")

        # Get persistence
        persistence = await self._get_persistence()
        if persistence is None:
            return self.skip("WitnessPersistence not available")

        try:
            # Import Thought type
            from services.witness.polynomial import Thought

            # Create and save the thought
            thought = Thought(
                content=content,
                source="gardener",
                tags=tuple(tags),
                timestamp=event.timestamp,
            )

            await persistence.save_thought(thought)

            self._logger.debug(f"Captured gesture to witness: {verb} on {target}")

            return self.success(
                message=f"Gesture captured: {verb} on {target}",
                metadata={
                    "verb": verb,
                    "target": target,
                    "state_changed": state_changed,
                    "entropy_cost": entropy_cost,
                },
            )

        except Exception as e:
            self._logger.error(f"Failed to capture gesture to witness: {e}")
            return self.failure(f"Capture failed: {e}")


__all__ = ["GardenToWitnessHandler"]
