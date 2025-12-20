"""
Garden to Brain Handler: Auto-capture garden state changes.

When garden seasons transition or significant gestures are applied,
this handler automatically captures the state change to Brain.

This enables:
- Historical garden state tracking
- Season transition history
- Significant gesture chronicle
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..events import SynergyEvent, SynergyEventType, SynergyResult
from .base import BaseSynergyHandler


class GardenToBrainHandler(BaseSynergyHandler):
    """
    Handler that captures garden state changes to Brain.

    Handles:
    1. SEASON_CHANGED: Captures season transitions for historical tracking
    2. GESTURE_APPLIED: Captures significant gestures (state-changing only)
    3. PLOT_PROGRESS_UPDATED: Captures plot progress milestones

    The crystal content includes contextual information for
    cross-session garden history.
    """

    def __init__(self, auto_capture: bool = True) -> None:
        """
        Initialize the handler.

        Args:
            auto_capture: If True, automatically captures to Brain.
                         If False, just logs (useful for testing).
        """
        super().__init__()
        self._auto_capture = auto_capture

    @property
    def name(self) -> str:
        return "GardenToBrainHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle a garden synergy event."""
        if event.event_type == SynergyEventType.SEASON_CHANGED:
            return await self._handle_season_changed(event)
        elif event.event_type == SynergyEventType.GESTURE_APPLIED:
            return await self._handle_gesture_applied(event)
        elif event.event_type == SynergyEventType.PLOT_PROGRESS_UPDATED:
            return await self._handle_plot_progress(event)
        else:
            return self.skip(f"Not handling {event.event_type.value}")

    async def _handle_season_changed(self, event: SynergyEvent) -> SynergyResult:
        """Handle a season changed event."""
        payload = event.payload
        garden_name = payload.get("garden_name", "Unknown")
        old_season = payload.get("old_season", "?")
        new_season = payload.get("new_season", "?")
        reason = payload.get("reason", "")

        # Create crystal content
        content = self._create_season_crystal_content(
            garden_name=garden_name,
            old_season=old_season,
            new_season=new_season,
            reason=reason,
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture season change: {old_season} → {new_season}")
            return self.success(
                message="Dry run - would capture season transition",
                metadata={
                    "old_season": old_season,
                    "new_season": new_season,
                },
            )

        # Actually capture to Brain
        try:
            concept_id = (
                f"garden-season-{event.source_id}-{event.timestamp.strftime('%Y%m%d-%H%M%S')}"
            )
            crystal_id = await self._capture_to_brain(
                content=content,
                concept_id=concept_id,
            )
            self._logger.info(f"Captured season transition: {crystal_id}")
            return self.success(
                message=f"Season transition captured: {old_season} → {new_season}",
                artifact_id=crystal_id,
                metadata={
                    "old_season": old_season,
                    "new_season": new_season,
                    "garden_name": garden_name,
                },
            )
        except Exception as e:
            self._logger.error(f"Failed to capture season change: {e}")
            return self.failure(f"Capture failed: {e}")

    async def _handle_gesture_applied(self, event: SynergyEvent) -> SynergyResult:
        """
        Handle a gesture applied event.

        Only captures gestures that changed state (not observation or wait).
        """
        payload = event.payload
        verb = payload.get("verb", "?")
        target = payload.get("target", "?")
        state_changed = payload.get("state_changed", False)
        reasoning = payload.get("reasoning", "")

        # Skip non-state-changing gestures
        if not state_changed:
            return self.skip(f"Gesture {verb} did not change state")

        # Skip low-significance gestures (OBSERVE, WAIT already filtered by tending.py)
        # but double-check here
        if verb in {"OBSERVE", "WAIT"}:
            return self.skip(f"Not capturing {verb} gestures")

        # Create crystal content
        content = self._create_gesture_crystal_content(
            verb=verb,
            target=target,
            reasoning=reasoning,
            synergies=payload.get("synergies_triggered", []),
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture gesture: {verb} on {target}")
            return self.success(
                message=f"Dry run - would capture {verb} gesture",
                metadata={"verb": verb, "target": target},
            )

        # Capture to Brain
        try:
            concept_id = (
                f"garden-gesture-{event.source_id}-{event.timestamp.strftime('%Y%m%d-%H%M%S')}"
            )
            crystal_id = await self._capture_to_brain(
                content=content,
                concept_id=concept_id,
            )
            self._logger.info(f"Captured gesture: {crystal_id}")
            return self.success(
                message=f"Gesture captured: {verb} on {target}",
                artifact_id=crystal_id,
                metadata={"verb": verb, "target": target},
            )
        except Exception as e:
            self._logger.error(f"Failed to capture gesture: {e}")
            return self.failure(f"Capture failed: {e}")

    async def _handle_plot_progress(self, event: SynergyEvent) -> SynergyResult:
        """
        Handle a plot progress updated event.

        Only captures significant progress changes (>= 10% delta or milestones).
        """
        payload = event.payload
        plot_name = payload.get("plot_name", "?")
        old_progress = payload.get("old_progress", 0.0)
        new_progress = payload.get("new_progress", 0.0)
        progress_delta = payload.get("progress_delta", 0.0)

        # Only capture significant progress changes
        # >= 10% change OR milestone crossings (25%, 50%, 75%, 100%)
        milestones = {0.25, 0.5, 0.75, 1.0}
        crossed_milestone = any(
            old_progress < m <= new_progress or new_progress < m <= old_progress for m in milestones
        )

        if abs(progress_delta) < 0.1 and not crossed_milestone:
            return self.skip(f"Progress change too small: {progress_delta:.1%}")

        # Create crystal content
        content = self._create_progress_crystal_content(
            plot_name=plot_name,
            old_progress=old_progress,
            new_progress=new_progress,
            plan_path=payload.get("plan_path"),
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture progress: {plot_name} → {new_progress:.0%}")
            return self.success(
                message="Dry run - would capture progress",
                metadata={"plot_name": plot_name, "new_progress": new_progress},
            )

        # Capture to Brain
        try:
            concept_id = f"garden-progress-{plot_name}-{event.timestamp.strftime('%Y%m%d')}"
            crystal_id = await self._capture_to_brain(
                content=content,
                concept_id=concept_id,
            )
            self._logger.info(f"Captured progress: {crystal_id}")
            return self.success(
                message=f"Progress captured: {plot_name} at {new_progress:.0%}",
                artifact_id=crystal_id,
                metadata={"plot_name": plot_name, "new_progress": new_progress},
            )
        except Exception as e:
            self._logger.error(f"Failed to capture progress: {e}")
            return self.failure(f"Capture failed: {e}")

    # =========================================================================
    # Crystal Content Generators
    # =========================================================================

    def _create_season_crystal_content(
        self,
        garden_name: str,
        old_season: str,
        new_season: str,
        reason: str,
        timestamp: datetime,
    ) -> str:
        """Create crystal content for a season transition."""
        # Season emojis
        emoji_map = {
            "DORMANT": "💤",
            "SPROUTING": "🌱",
            "BLOOMING": "🌸",
            "HARVEST": "🌾",
            "COMPOSTING": "🍂",
        }
        old_emoji = emoji_map.get(old_season, "?")
        new_emoji = emoji_map.get(new_season, "?")

        return f"""Garden Season Transition: {garden_name}

Timestamp: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Transition:
  {old_emoji} {old_season} → {new_emoji} {new_season}

Reason: {reason or "(no reason specified)"}

This snapshot was automatically captured by the Garden → Brain synergy.
Use this for:
- Season history tracking
- Development rhythm analysis
- Garden health trends
"""

    def _create_gesture_crystal_content(
        self,
        verb: str,
        target: str,
        reasoning: str,
        synergies: list[str],
        timestamp: datetime,
    ) -> str:
        """Create crystal content for a gesture application."""
        # Verb emojis
        emoji_map = {
            "PRUNE": "✂️",
            "GRAFT": "🌿",
            "WATER": "💧",
            "ROTATE": "🔄",
        }
        emoji = emoji_map.get(verb, "🌱")

        synergy_str = "\n  - ".join(synergies) if synergies else "(none)"

        return f"""Garden Gesture: {emoji} {verb}

Timestamp: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Target: {target}
Reasoning: {reasoning or "(no reasoning)"}

Synergies Triggered:
  - {synergy_str}

This snapshot was automatically captured by the Garden → Brain synergy.
Use this for:
- Tending history tracking
- Gesture pattern analysis
- Garden evolution chronicle
"""

    def _create_progress_crystal_content(
        self,
        plot_name: str,
        old_progress: float,
        new_progress: float,
        plan_path: str | None,
        timestamp: datetime,
    ) -> str:
        """Create crystal content for a progress update."""
        delta = new_progress - old_progress
        direction = "📈" if delta > 0 else "📉"

        # Progress bar visualization
        filled = int(new_progress * 20)
        bar = "█" * filled + "░" * (20 - filled)

        return f"""Garden Plot Progress: {plot_name}

Timestamp: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Progress: {direction} {old_progress:.0%} → {new_progress:.0%} (Δ{delta:+.0%})
[{bar}] {new_progress:.0%}

Plan File: {plan_path or "(not linked)"}

This snapshot was automatically captured by the Garden → Brain synergy.
Use this for:
- Plan progress tracking
- Development velocity analysis
- Forest health trends
"""

    # =========================================================================
    # Brain Integration
    # =========================================================================

    async def _capture_to_brain(self, content: str, concept_id: str) -> str:
        """Capture content to Brain and return crystal ID."""
        # Import here to avoid circular imports
        from protocols.agentese import create_logos
        from protocols.agentese.node import Observer

        # Create a minimal logos for capture
        logos = create_logos()
        observer = Observer.guest()

        result = await logos.invoke(
            "self.memory.capture",
            observer,
            content=content,
            concept_id=concept_id,
        )

        # Return the concept ID
        returned_id: str = str(result.get("concept_id", concept_id))
        return returned_id


__all__ = ["GardenToBrainHandler"]
