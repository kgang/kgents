"""
CoffeeService: Orchestrates the Morning Coffee ritual.

Container Owns Workflow (Pattern 1): CoffeeService owns CaptureSession.
No Hollow Services (Pattern 15): Requires generators in constructor.

The service orchestrates the four movements:
1. Garden View - "What grew while I slept?"
2. Conceptual Weather - "What's shifting in the atmosphere?"
3. Menu - "What suits my taste this morning?"
4. Fresh Capture - "What's Kent saying before code takes over?"

Events emitted via SynergyBus:
- CoffeeRitualStarted
- CoffeeMovementCompleted
- CoffeeVoiceCaptured
- CoffeeRitualCompleted
- CoffeeRitualExited

See: spec/services/morning-coffee.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .capture import (
    CaptureSession,
    load_recent_voices,
    load_voice,
    save_voice,
    save_voice_async,
)
from .garden import generate_garden_view, generate_garden_view_async
from .menu import generate_menu, generate_menu_async
from .polynomial import COFFEE_POLYNOMIAL, coffee_transition
from .types import (
    MOVEMENTS,
    ChallengeLevel,
    ChallengeMenu,
    CoffeeOutput,
    CoffeeState,
    ConceptualWeather,
    GardenView,
    MenuItem,
    MorningVoice,
    RitualEvent,
)
from .weather import generate_weather, generate_weather_async

if TYPE_CHECKING:
    from protocols.synergy.bus import SynergyEventBus
    from services.brain.persistence import BrainPersistence

logger = logging.getLogger(__name__)


# =============================================================================
# Event Types (for SynergyBus)
# =============================================================================


@dataclass(frozen=True)
class CoffeeRitualStarted:
    """Emitted when the Morning Coffee ritual begins."""

    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class CoffeeMovementCompleted:
    """Emitted when a movement completes."""

    movement: str
    duration_seconds: int
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class CoffeeVoiceCaptured:
    """Emitted when a voice capture completes."""

    capture_id: str
    has_success_criteria: bool
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class CoffeeRitualCompleted:
    """Emitted when the ritual completes successfully."""

    session_id: str
    chosen_challenge: ChallengeLevel | None
    duration_seconds: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class CoffeeRitualExited:
    """Emitted when the ritual is exited early."""

    session_id: str
    at_movement: str
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# CoffeeService
# =============================================================================


class CoffeeService:
    """
    Orchestrates the Morning Coffee ritual.

    Container Owns Workflow (Pattern 1):
    - Service owns the CaptureSession lifecycle
    - Service coordinates polynomial state transitions
    - Service emits events for cross-jewel awareness

    No Hollow Services (Pattern 15):
    - Service requires paths for generators
    - All dependencies are explicit in constructor

    Usage:
        service = CoffeeService()

        # Full ritual
        async for output in service.run_ritual():
            handle_output(output)

        # Individual movements
        garden = await service.garden()
        weather = await service.weather()
        menu = await service.menu()

        # Voice capture
        session = service.start_capture()
        session.answer("Something non-code related")
        voice = session.build_voice()
        await service.save_capture(voice)
    """

    def __init__(
        self,
        repo_path: Path | str | None = None,
        now_md_path: Path | str | None = None,
        plans_path: Path | str | None = None,
        brainstorm_path: Path | str | None = None,
        voice_store_path: Path | str | None = None,
        synergy_bus: "SynergyEventBus | None" = None,
        brain_persistence: "BrainPersistence | None" = None,
    ) -> None:
        """
        Initialize CoffeeService.

        Args:
            repo_path: Path to git repository (defaults to cwd)
            now_md_path: Path to NOW.md (defaults to cwd/NOW.md)
            plans_path: Path to plans directory (defaults to cwd/plans)
            brainstorm_path: Path to brainstorming directory
            voice_store_path: Path for voice capture persistence
            synergy_bus: Optional SynergyBus for event emission
            brain_persistence: Optional Brain for voice archaeology
        """
        self.repo_path = Path(repo_path) if repo_path else None
        self.now_md_path = Path(now_md_path) if now_md_path else None
        self.plans_path = Path(plans_path) if plans_path else None
        self.brainstorm_path = Path(brainstorm_path) if brainstorm_path else None
        self.voice_store_path = Path(voice_store_path) if voice_store_path else None
        self.synergy_bus = synergy_bus
        self.brain_persistence = brain_persistence

        # State
        self._state: CoffeeState = CoffeeState.DORMANT
        self._session_id: str | None = None
        self._started_at: datetime | None = None
        self._capture_session: CaptureSession | None = None

        # Cached views (regenerated per ritual)
        self._garden_view: GardenView | None = None
        self._weather: ConceptualWeather | None = None
        self._menu: ChallengeMenu | None = None

    # =========================================================================
    # State Properties
    # =========================================================================

    @property
    def state(self) -> CoffeeState:
        """Current ritual state."""
        return self._state

    @property
    def is_active(self) -> bool:
        """Whether a ritual is currently active."""
        return self._state != CoffeeState.DORMANT

    @property
    def current_movement(self) -> str | None:
        """Current movement name, or None if dormant."""
        state_to_movement = {
            CoffeeState.GARDEN: "garden",
            CoffeeState.WEATHER: "weather",
            CoffeeState.MENU: "menu",
            CoffeeState.CAPTURE: "capture",
            CoffeeState.TRANSITION: "transition",
        }
        return state_to_movement.get(self._state)

    # =========================================================================
    # Manifest (Overview)
    # =========================================================================

    def manifest(self) -> dict[str, Any]:
        """
        Get ritual manifest — current state and last ritual info.

        Returns dict with:
        - state: Current CoffeeState
        - is_active: Whether ritual is running
        - current_movement: Current movement name
        - today_voice: Today's voice capture if exists
        - last_ritual: Last ritual date
        """
        today_voice = load_voice(date.today(), self.voice_store_path)
        recent = load_recent_voices(limit=1, store_path=self.voice_store_path)

        return {
            "state": self._state.name,
            "is_active": self.is_active,
            "current_movement": self.current_movement,
            "today_voice": today_voice.to_dict() if today_voice else None,
            "last_ritual": recent[0].captured_date.isoformat() if recent else None,
            "movements": [MOVEMENTS[k].to_dict() for k in ["garden", "weather", "menu", "capture"]],
        }

    # =========================================================================
    # Individual Movements
    # =========================================================================

    async def garden(self) -> GardenView:
        """
        Generate the Garden View (Movement 1).

        Non-demanding observation of yesterday's changes.
        """
        self._garden_view = await generate_garden_view_async(
            repo_path=self.repo_path,
            now_md_path=self.now_md_path,
            brainstorm_path=self.brainstorm_path,
        )
        return self._garden_view

    async def weather(self) -> ConceptualWeather:
        """
        Generate the Conceptual Weather (Movement 2).

        What's shifting in the atmosphere of the codebase.
        """
        self._weather = await generate_weather_async(
            repo_path=self.repo_path,
            plans_path=self.plans_path,
        )
        return self._weather

    async def menu(
        self,
        garden_view: GardenView | None = None,
        weather: ConceptualWeather | None = None,
    ) -> ChallengeMenu:
        """
        Generate the Challenge Menu (Movement 3).

        Presents invitations, not assignments.

        Args:
            garden_view: Optional GardenView for context
            weather: Optional ConceptualWeather for context
        """
        self._menu = await generate_menu_async(
            plans_path=self.plans_path,
            now_path=self.now_md_path,
            garden_view=garden_view or self._garden_view,
            weather=weather or self._weather,
        )
        return self._menu

    def start_capture(self) -> CaptureSession:
        """
        Start a voice capture session (Movement 4).

        Container Owns Workflow: CoffeeService owns the session.
        """
        self._capture_session = CaptureSession(captured_date=date.today())
        return self._capture_session

    async def save_capture(self, voice: MorningVoice) -> Path:
        """
        Save a completed voice capture.

        Saves to:
        1. Local JSON file (primary storage)
        2. Brain crystal if brain_persistence is available (voice archaeology)

        Args:
            voice: MorningVoice to save

        Returns:
            Path to saved file
        """
        # Save to local file system
        path = await save_voice_async(voice, self.voice_store_path)

        # Also store in Brain for voice archaeology
        if self.brain_persistence:
            await self._capture_to_brain(voice)

        return path

    async def _capture_to_brain(self, voice: MorningVoice) -> None:
        """
        Store voice capture as a Brain crystal.

        This enables voice archaeology: tracking patterns in morning thoughts
        over time, searching across voices, and correlating energy levels
        with productivity.

        Tags: morning_coffee, voice_anchor, date:YYYY-MM-DD
        """
        if not self.brain_persistence:
            return

        try:
            # Build content from voice
            parts = []

            if voice.success_criteria:
                parts.append(f"Today's goal: {voice.success_criteria}")

            if voice.non_code_thought:
                parts.append(f"Morning thought: {voice.non_code_thought}")

            if voice.eye_catch:
                parts.append(f"Caught my eye: {voice.eye_catch}")

            if voice.raw_feeling:
                parts.append(f"Feeling: {voice.raw_feeling}")

            content = "\n\n".join(parts) if parts else "Morning voice captured"

            # Build tags
            tags = [
                "morning_coffee",
                "voice_anchor",
                f"date:{voice.captured_date.isoformat()}",
            ]

            if voice.chosen_challenge:
                challenge_value = (
                    voice.chosen_challenge.value
                    if hasattr(voice.chosen_challenge, "value")
                    else str(voice.chosen_challenge)
                )
                tags.append(f"challenge:{challenge_value}")

            # Capture to brain
            await self.brain_persistence.capture(
                content=content,
                tags=tags,
                source_type="morning_coffee",
                source_ref=f"voice:{voice.captured_date.isoformat()}",
                metadata={
                    "captured_date": voice.captured_date.isoformat(),
                    "is_substantive": voice.is_substantive,
                },
            )

            logger.debug(f"Voice captured to Brain for {voice.captured_date}")

        except Exception as e:
            # Don't fail the capture if Brain is unavailable
            logger.warning(f"Failed to capture voice to Brain: {e}")

    async def search_voice_archaeology(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search past voice captures using semantic search.

        Voice archaeology: What did Kent care about? How has his language shifted?
        What success criteria appear repeatedly?

        Args:
            query: Search query (e.g., "what did I care about in December")
            limit: Maximum results

        Returns:
            List of matching voice captures with similarity scores
        """
        if not self.brain_persistence:
            logger.debug("Brain not available for voice archaeology")
            return []

        try:
            # Search Brain for morning_coffee tagged crystals
            results = await self.brain_persistence.search(
                query=query,
                limit=limit,
            )

            # Filter to morning_coffee sources
            voice_results = []
            for r in results:
                # Check if this is a morning coffee capture
                # The source_ref will be like "voice:2025-12-21"
                if hasattr(r, "content") and "morning" in r.content.lower():
                    voice_results.append(
                        {
                            "crystal_id": r.crystal_id,
                            "content": r.content,
                            "similarity": r.similarity,
                            "captured_at": r.captured_at,
                        }
                    )

            return voice_results

        except Exception as e:
            logger.warning(f"Voice archaeology search failed: {e}")
            return []

    async def get_voice_patterns_from_brain(self) -> dict[str, Any]:
        """
        Extract patterns from voice captures stored in Brain.

        Analyzes:
        - Common themes in success criteria
        - Challenge preferences over time
        - Energy patterns (if tracked)

        Returns:
            Pattern analysis dict
        """
        if not self.brain_persistence:
            return {"available": False}

        try:
            # Search for all morning coffee captures
            results = await self.brain_persistence.search(
                query="morning coffee voice",
                limit=100,
            )

            # Extract patterns
            success_criteria = []
            for r in results:
                if hasattr(r, "content"):
                    content = r.content
                    if "Today's goal:" in content:
                        goal_line = content.split("Today's goal:")[1].split("\n")[0]
                        success_criteria.append(goal_line.strip())

            # Find common themes
            themes: dict[str, int] = {}
            for criteria in success_criteria:
                words = criteria.lower().split()
                for word in words:
                    if len(word) > 4:  # Skip short words
                        themes[word] = themes.get(word, 0) + 1

            # Sort by frequency
            common_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "available": True,
                "total_voices": len(results),
                "common_themes": [theme for theme, _ in common_themes],
                "recent_goals": success_criteria[:5],
            }

        except Exception as e:
            logger.warning(f"Voice pattern extraction failed: {e}")
            return {"available": False, "error": str(e)}

    # =========================================================================
    # State Machine Operations
    # =========================================================================

    def wake(self) -> CoffeeOutput:
        """
        Start the ritual (DORMANT → GARDEN).

        Returns output with garden movement info.
        """
        import uuid

        self._session_id = str(uuid.uuid4())[:8]
        self._started_at = datetime.now()

        self._state, output = coffee_transition(self._state, "wake")

        # Emit event
        self._emit_event(
            CoffeeRitualStarted(
                session_id=self._session_id,
                timestamp=datetime.now(),
            )
        )

        return output

    def advance(self, command: str, **data: Any) -> CoffeeOutput:
        """
        Advance the ritual state machine.

        Args:
            command: Command to execute (continue, skip, select, etc.)
            **data: Additional data for the command

        Returns:
            CoffeeOutput with new state and any generated content
        """
        prev_state = self._state
        event = RitualEvent(command=command, data=data)

        self._state, output = coffee_transition(self._state, event)

        # Track movement completion
        if prev_state != self._state and self._started_at:
            movement_name = {
                CoffeeState.GARDEN: "garden",
                CoffeeState.WEATHER: "weather",
                CoffeeState.MENU: "menu",
                CoffeeState.CAPTURE: "capture",
            }.get(prev_state)

            if movement_name and self._session_id:
                duration = int((datetime.now() - self._started_at).total_seconds())
                self._emit_event(
                    CoffeeMovementCompleted(
                        movement=movement_name,
                        duration_seconds=duration,
                        session_id=self._session_id,
                    )
                )

        # Handle exit
        if output.status == "exited" and self._session_id:
            movement_name = self.current_movement or "dormant"
            self._emit_event(
                CoffeeRitualExited(
                    session_id=self._session_id,
                    at_movement=movement_name,
                )
            )
            self._reset_session()

        # Handle completion
        if self._state == CoffeeState.DORMANT and prev_state == CoffeeState.TRANSITION:
            if self._session_id and self._started_at:
                duration = int((datetime.now() - self._started_at).total_seconds())
                chosen = self._capture_session.chosen_challenge if self._capture_session else None
                self._emit_event(
                    CoffeeRitualCompleted(
                        session_id=self._session_id,
                        chosen_challenge=chosen,
                        duration_seconds=duration,
                    )
                )
            self._reset_session()

        return output

    def exit_ritual(self) -> CoffeeOutput:
        """Exit the ritual at any point. No guilt, no nagging."""
        return self.advance("exit")

    # =========================================================================
    # Quick Ritual (Garden + Menu)
    # =========================================================================

    async def quick(self) -> tuple[GardenView, ChallengeMenu]:
        """
        Run quick ritual: Garden + Menu only.

        Skips Weather and Capture for faster morning start.
        """
        garden = await self.garden()
        menu = await self.menu(garden_view=garden)
        return garden, menu

    # =========================================================================
    # History
    # =========================================================================

    def get_recent_voices(self, limit: int = 7) -> list[MorningVoice]:
        """Get recent voice captures."""
        return load_recent_voices(limit=limit, store_path=self.voice_store_path)

    def get_voice(self, capture_date: date) -> MorningVoice | None:
        """Get voice capture for a specific date."""
        return load_voice(capture_date, self.voice_store_path)

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _reset_session(self) -> None:
        """Reset session state after ritual ends."""
        self._state = CoffeeState.DORMANT
        self._session_id = None
        self._started_at = None
        self._capture_session = None
        self._garden_view = None
        self._weather = None
        self._menu = None

    def _emit_event(self, event: Any) -> None:
        """
        Emit event for ritual state changes.

        Currently logs the event. When Coffee is integrated as a Jewel,
        this will emit to SynergyEventBus for cross-jewel awareness.
        """
        event_name = type(event).__name__
        logger.info(f"Coffee event: {event_name}")

        # Future: When integrated into Jewel system, emit to SynergyEventBus
        if self.synergy_bus is not None:
            logger.debug("SynergyEventBus available but not yet wired for coffee events")


# =============================================================================
# Factory
# =============================================================================


_service: CoffeeService | None = None


def get_coffee_service() -> CoffeeService:
    """Get or create the global CoffeeService."""
    global _service
    if _service is None:
        _service = CoffeeService()
    return _service


def set_coffee_service(service: CoffeeService) -> None:
    """Set the global CoffeeService (for testing)."""
    global _service
    _service = service


def reset_coffee_service() -> None:
    """Reset the global CoffeeService."""
    global _service
    _service = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Service
    "CoffeeService",
    "get_coffee_service",
    "set_coffee_service",
    "reset_coffee_service",
    # Events
    "CoffeeRitualStarted",
    "CoffeeMovementCompleted",
    "CoffeeVoiceCaptured",
    "CoffeeRitualCompleted",
    "CoffeeRitualExited",
]
