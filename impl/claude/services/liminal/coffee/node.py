"""
Morning Coffee AGENTESE Node: time.coffee.*

The liminal transition protocol as an AGENTESE node.

Aspects:
- manifest: Current ritual state and last capture
- garden: Generate Garden View (Movement 1)
- weather: Generate Conceptual Weather (Movement 2)
- menu: Generate Challenge Menu (Movement 3)
- capture: Start/record voice capture (Movement 4)
- begin: Complete ritual, transition to work
- history: View past voice captures

Affordances by archetype:
- guest: manifest only
- observer: manifest, garden, weather
- participant: full ritual access
- architect: all + history patterns

AGENTESE: time.coffee.*

See: spec/services/morning-coffee.md
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, Effect, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import BaseLogosNode, BasicRendering, Renderable
from protocols.agentese.registry import node

from .core import CoffeeService, get_coffee_service
from .types import (
    MOVEMENTS,
    ChallengeLevel,
    ChallengeMenu,
    ConceptualWeather,
    GardenView,
    MorningVoice,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)


# =============================================================================
# Contract Types
# =============================================================================


@dataclass
class CoffeeManifestResponse:
    """Response for manifest aspect."""

    state: str
    is_active: bool
    current_movement: str | None
    today_voice: dict[str, Any] | None
    last_ritual: str | None
    movements: list[dict[str, Any]]


@dataclass
class GardenResponse:
    """Response for garden aspect."""

    harvest: list[dict[str, Any]]
    growing: list[dict[str, Any]]
    sprouting: list[dict[str, Any]]
    seeds: list[dict[str, Any]]
    generated_at: str


@dataclass
class WeatherResponse:
    """Response for weather aspect."""

    refactoring: list[dict[str, Any]]
    emerging: list[dict[str, Any]]
    scaffolding: list[dict[str, Any]]
    tension: list[dict[str, Any]]
    generated_at: str


@dataclass
class MenuResponse:
    """Response for menu aspect."""

    gentle: list[dict[str, Any]]
    focused: list[dict[str, Any]]
    intense: list[dict[str, Any]]
    serendipitous_prompt: str
    generated_at: str


@dataclass
class CaptureRequest:
    """Request for capture aspect."""

    non_code_thought: str | None = None
    eye_catch: str | None = None
    success_criteria: str | None = None
    raw_feeling: str | None = None
    chosen_challenge: str | None = None


@dataclass
class CaptureResponse:
    """Response for capture aspect."""

    captured: bool
    voice: dict[str, Any] | None
    saved_path: str | None


@dataclass
class BeginResponse:
    """Response for begin aspect."""

    transitioned: bool
    message: str


@dataclass
class HistoryRequest:
    """Request for history aspect."""

    limit: int = 7
    capture_date: str | None = None


@dataclass
class HistoryResponse:
    """Response for history aspect."""

    voices: list[dict[str, Any]]
    patterns: dict[str, Any] | None


# =============================================================================
# Node Definition
# =============================================================================


COFFEE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "guest": ("manifest",),
    "observer": ("manifest", "garden", "weather"),
    "participant": ("manifest", "garden", "weather", "menu", "capture", "begin"),
    "architect": ("manifest", "garden", "weather", "menu", "capture", "begin", "history"),
    # CLI has full access - it's the primary interface for Morning Coffee
    "cli": ("manifest", "garden", "weather", "menu", "capture", "begin", "history"),
    "developer": ("manifest", "garden", "weather", "menu", "capture", "begin", "history"),
}


@node(
    "time.coffee",
    description="Morning Coffee ritual — liminal transition from rest to work",
    singleton=True,
    contracts={
        "manifest": Response(CoffeeManifestResponse),
        "garden": Response(GardenResponse),
        "weather": Response(WeatherResponse),
        "menu": Response(MenuResponse),
        "capture": Contract(CaptureRequest, CaptureResponse),
        "begin": Response(BeginResponse),
        "history": Contract(HistoryRequest, HistoryResponse),
    },
    dependencies=("coffee_service",),
)
@dataclass
class CoffeeNode(BaseLogosNode):
    """
    time.coffee — Morning Coffee liminal transition protocol.

    The ritual honors the precious liminal state between rest and work
    through four movements:
    1. Garden View - "What grew while I slept?"
    2. Conceptual Weather - "What's shifting in the atmosphere?"
    3. Menu - "What suits my taste this morning?"
    4. Fresh Capture - "What's Kent saying before code takes over?"

    "The musician doesn't start with the hardest passage.
     She tunes, breathes, plays a scale."
    """

    _handle: str = "time.coffee"
    # NOTE: Field name MUST match @node(dependencies=(...)) declaration
    # The container injects by name: coffee_service=value
    coffee_service: CoffeeService | None = None

    def __post_init__(self) -> None:
        """Initialize with service."""
        if self.coffee_service is None:
            self.coffee_service = get_coffee_service()

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Get affordances based on observer archetype."""
        return COFFEE_AFFORDANCES.get(archetype, COFFEE_AFFORDANCES["guest"])

    # =========================================================================
    # Aspect Routing (Abstract Method Implementation)
    # =========================================================================

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect names to their implementations."""
        match aspect:
            case "manifest":
                return await self.manifest(observer)
            case "garden":
                return await self.garden(observer)
            case "weather":
                return await self.weather(observer)
            case "menu":
                return await self.menu(observer)
            case "capture":
                return await self.capture(observer, **kwargs)
            case "begin":
                return await self.begin(observer)
            case "history":
                return await self.history(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # =========================================================================
    # Manifest
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View current ritual state and last capture",
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View current ritual state."""
        assert self.coffee_service is not None

        data = self.coffee_service.manifest()

        # Build summary
        if data["today_voice"]:
            summary = "☕ Morning Coffee complete today"
        elif data["is_active"]:
            summary = f"☕ Ritual in progress: {data['current_movement']}"
        else:
            summary = "☕ Morning Coffee ready"

        return BasicRendering(
            summary=summary,
            content=json.dumps(data, indent=2, default=str),
            metadata={"route": "/coffee"},
        )

    # =========================================================================
    # Garden (Movement 1)
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("git"), Effect.READS("now_md")],
        help="View Garden: what grew while you slept",
    )
    async def garden(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Generate Garden View (Movement 1)."""
        assert self.coffee_service is not None

        view = await self.coffee_service.garden()

        return BasicRendering(
            summary=f"🌱 Garden: {view.total_items} items",
            content=json.dumps(view.to_dict(), indent=2, default=str),
            metadata={
                "movement": "garden",
                "is_empty": view.is_empty,
            },
        )

    # =========================================================================
    # Weather (Movement 2)
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("plans"), Effect.READS("git")],
        help="View Conceptual Weather: what's shifting in the atmosphere",
    )
    async def weather(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Generate Conceptual Weather (Movement 2)."""
        assert self.coffee_service is not None

        weather = await self.coffee_service.weather()

        pattern_count = len(weather.all_patterns)
        summary = f"🌤️ Weather: {pattern_count} patterns"

        return BasicRendering(
            summary=summary,
            content=json.dumps(weather.to_dict(), indent=2, default=str),
            metadata={
                "movement": "weather",
                "is_empty": weather.is_empty,
            },
        )

    # =========================================================================
    # Menu (Movement 3)
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("plans"), Effect.READS("now_md")],
        help="View Menu: challenge invitations for today",
    )
    async def menu(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Generate Challenge Menu (Movement 3)."""
        assert self.coffee_service is not None

        menu = await self.coffee_service.menu()

        item_count = len(menu.gentle) + len(menu.focused) + len(menu.intense)
        summary = f"🍳 Menu: {item_count} invitations"

        return BasicRendering(
            summary=summary,
            content=json.dumps(menu.to_dict(), indent=2, default=str),
            metadata={
                "movement": "menu",
                "is_empty": menu.is_empty,
            },
        )

    # =========================================================================
    # Capture (Movement 4)
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("voice")],
        help="Record morning voice capture",
    )
    async def capture(
        self,
        observer: "Umwelt[Any, Any]",
        *,
        non_code_thought: str | None = None,
        eye_catch: str | None = None,
        success_criteria: str | None = None,
        raw_feeling: str | None = None,
        chosen_challenge: str | None = None,
    ) -> Renderable:
        """
        Record voice capture (Movement 4).

        If any answers provided, create and save MorningVoice.
        Otherwise, return capture questions for interactive flow.
        """
        assert self.coffee_service is not None

        # If no answers, return questions for interactive flow
        if not any([non_code_thought, eye_catch, success_criteria, raw_feeling]):
            from .capture import CAPTURE_QUESTIONS

            questions_data = {
                "questions": [
                    {
                        "key": q.key,
                        "prompt": q.prompt,
                        "placeholder": q.placeholder,
                        "required": q.required,
                    }
                    for q in CAPTURE_QUESTIONS
                ],
            }
            return BasicRendering(
                summary="📝 Fresh Capture: 4 questions",
                content=json.dumps(questions_data, indent=2, default=str),
                metadata={"movement": "capture", "interactive": True},
            )

        # Create voice from provided answers
        challenge = ChallengeLevel(chosen_challenge) if chosen_challenge else None
        voice = MorningVoice(
            captured_date=date.today(),
            non_code_thought=non_code_thought,
            eye_catch=eye_catch,
            success_criteria=success_criteria,
            raw_feeling=raw_feeling,
            chosen_challenge=challenge,
        )

        # Save
        saved_path = await self.coffee_service.save_capture(voice)

        result_data = {
            "captured": True,
            "voice": voice.to_dict(),
            "saved_path": str(saved_path),
        }
        return BasicRendering(
            summary="✨ Voice captured",
            content=json.dumps(result_data, indent=2, default=str),
            metadata={
                "movement": "capture",
                "has_success_criteria": bool(success_criteria),
            },
        )

    # =========================================================================
    # Begin (Transition)
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[],
        help="Complete ritual and transition to work",
    )
    async def begin(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Complete ritual, transition to work."""
        result_data = {
            "transitioned": True,
            "message": "Alright, let's begin. The morning is yours.",
        }
        return BasicRendering(
            summary="☀️ Ready to begin",
            content=json.dumps(result_data, indent=2, default=str),
            metadata={"movement": "transition"},
        )

    # =========================================================================
    # History
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("voice")],
        help="View past voice captures and patterns",
    )
    async def history(
        self,
        observer: "Umwelt[Any, Any]",
        *,
        limit: int = 7,
        capture_date: str | None = None,
    ) -> Renderable:
        """View past voice captures."""
        assert self.coffee_service is not None

        if capture_date:
            # Get specific date
            dt = date.fromisoformat(capture_date)
            voice = self.coffee_service.get_voice(dt)
            voices = [voice] if voice else []
        else:
            # Get recent
            voices = self.coffee_service.get_recent_voices(limit=limit)

        # Extract patterns if we have enough data
        patterns = None
        if len(voices) >= 3:
            from .capture import extract_voice_patterns

            patterns = extract_voice_patterns(voices)

        result_data = {
            "voices": [v.to_dict() for v in voices],
            "patterns": patterns,
        }
        return BasicRendering(
            summary=f"📚 History: {len(voices)} captures",
            content=json.dumps(result_data, indent=2, default=str),
            metadata={"count": len(voices)},
        )


# =============================================================================
# Factory
# =============================================================================


_node: CoffeeNode | None = None


def get_coffee_node() -> CoffeeNode:
    """Get or create the CoffeeNode singleton."""
    global _node
    if _node is None:
        _node = CoffeeNode()
    return _node


def set_coffee_node(node: CoffeeNode) -> None:
    """Set the CoffeeNode singleton (for testing)."""
    global _node
    _node = node


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Node
    "CoffeeNode",
    "get_coffee_node",
    "set_coffee_node",
    # Contract types
    "CoffeeManifestResponse",
    "GardenResponse",
    "WeatherResponse",
    "MenuResponse",
    "CaptureRequest",
    "CaptureResponse",
    "BeginResponse",
    "HistoryRequest",
    "HistoryResponse",
    # Affordances
    "COFFEE_AFFORDANCES",
]
