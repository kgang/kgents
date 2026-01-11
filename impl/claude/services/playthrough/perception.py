"""
Perception Sheaf: Local observations → Global game understanding.

Categorical Structure:
    Sheaf gluing: Section_visual ⊗ Section_api ⊗ Section_audio → UnifiedPercept

Each section provides a local view of the game state.
The sheaf gluing combines them into a coherent global percept.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Protocol


class GameInterface(Protocol):
    """Protocol for game interface."""

    async def capture_screen(self) -> bytes:
        """Capture current screen."""
        ...

    async def get_debug_state(self) -> dict[str, Any]:
        """Get debug API state."""
        ...

    async def get_audio_cues(self) -> list[dict[str, Any]]:
        """Get recent audio cues."""
        ...


@dataclass
class UnifiedPercept:
    """
    Global percept from sheaf gluing.

    This is the unified understanding of the game state,
    combining visual, API, and audio sections.
    """

    # Player state
    player: dict[str, Any] = field(default_factory=dict)

    # Entity lists
    enemies: list[dict[str, Any]] = field(default_factory=list)
    projectiles: list[dict[str, Any]] = field(default_factory=list)
    pickups: list[dict[str, Any]] = field(default_factory=list)

    # Game state
    upgrades: list[dict[str, Any]] = field(default_factory=list)
    wave: dict[str, Any] = field(default_factory=dict)

    # Audio cues
    audio_cues: list[dict[str, Any]] = field(default_factory=list)

    # Metadata
    screen_hash: str = ""
    timestamp_ms: float = 0.0

    @property
    def has_upgrade_available(self) -> bool:
        """Check if upgrades are available to select."""
        return len(self.upgrades) > 0

    @property
    def threat_level(self) -> float:
        """Compute overall threat level."""
        enemy_threat = sum(1.0 / max(e.get("distance", 500), 1) for e in self.enemies)
        projectile_threat = sum(
            1.0 / max(p.get("time_to_impact_ms", 1000), 1) for p in self.projectiles
        )
        health_factor = (100 - self.player.get("health", 100)) / 100

        return float(min(1.0, enemy_threat * 0.1 + projectile_threat * 0.01 + health_factor * 0.5))


class PerceptionSheaf:
    """
    Sheaf for game perception.

    Glues local sections (visual, API, audio) into global percept.
    """

    def __init__(self) -> None:
        self._last_screen_hash: str = ""
        self._cached_visual: dict[str, Any] | None = None

    async def perceive(self, game: GameInterface) -> UnifiedPercept:
        """
        Perform sheaf gluing to create unified percept.

        Section hierarchy:
        1. API section (most accurate, but limited)
        2. Visual section (comprehensive, but slower)
        3. Audio section (real-time cues)
        """
        # Section 1: API state (primary source of truth)
        api_state = await self._section_api(game)

        # Section 2: Visual state (supplements API)
        visual_state = await self._section_visual(game)

        # Section 3: Audio cues (real-time signals)
        audio_cues = await self._section_audio(game)

        # Glue sections into unified percept
        return self._glue(api_state, visual_state, audio_cues)

    async def _section_api(self, game: GameInterface) -> dict[str, Any]:
        """
        API section: Direct game state from debug API.

        This is the most accurate source but may not be available
        in production builds.
        """
        try:
            return await game.get_debug_state()
        except Exception:
            return {}

    async def _section_visual(self, game: GameInterface) -> dict[str, Any]:
        """
        Visual section: State extracted from screen capture.

        Used when API is unavailable or to supplement API data.
        """
        try:
            screen = await game.capture_screen()
            screen_hash = hashlib.md5(screen).hexdigest()

            # Cache visual processing if screen unchanged
            if screen_hash == self._last_screen_hash and self._cached_visual:
                return self._cached_visual

            self._last_screen_hash = screen_hash

            # Visual processing would go here
            # For now, just return hash for tracking
            self._cached_visual = {"screen_hash": screen_hash}
            return self._cached_visual

        except Exception:
            return {}

    async def _section_audio(self, game: GameInterface) -> list[dict[str, Any]]:
        """
        Audio section: Sound cues for game events.

        Audio cues can signal events before they're visible:
        - Telegraph sounds
        - Damage sounds
        - Pickup sounds
        """
        try:
            return await game.get_audio_cues()
        except Exception:
            return []

    def _glue(
        self,
        api_state: dict[str, Any],
        visual_state: dict[str, Any],
        audio_cues: list[dict[str, Any]],
    ) -> UnifiedPercept:
        """
        Sheaf gluing: Combine sections into unified percept.

        Conflict resolution:
        - API takes precedence for entity data
        - Visual fills gaps in API
        - Audio provides real-time cues
        """
        # Extract player state (prefer API)
        player = api_state.get("player", {})

        # Extract enemies with distance calculation
        enemies = []
        for enemy in api_state.get("enemies", []):
            # Calculate distance if positions available
            if "position" in enemy and "position" in player:
                dx = enemy["position"].get("x", 0) - player.get("position", {}).get("x", 0)
                dy = enemy["position"].get("y", 0) - player.get("position", {}).get("y", 0)
                enemy["distance"] = (dx**2 + dy**2) ** 0.5
            enemies.append(enemy)

        # Extract projectiles with time-to-impact
        projectiles = []
        for proj in api_state.get("projectiles", []):
            # Estimate time to impact
            if "velocity" in proj and "position" in proj and "position" in player:
                # Simple linear estimate
                dx = player.get("position", {}).get("x", 0) - proj["position"].get("x", 0)
                dy = player.get("position", {}).get("y", 0) - proj["position"].get("y", 0)
                dist = (dx**2 + dy**2) ** 0.5

                speed = (
                    proj["velocity"].get("x", 0) ** 2 + proj["velocity"].get("y", 0) ** 2
                ) ** 0.5
                if speed > 0:
                    proj["time_to_impact_ms"] = (dist / speed) * 1000
            projectiles.append(proj)

        return UnifiedPercept(
            player=player,
            enemies=enemies,
            projectiles=projectiles,
            pickups=api_state.get("pickups", []),
            upgrades=api_state.get("upgrades", api_state.get("available_upgrades", [])),
            wave=api_state.get("wave", {}),
            audio_cues=audio_cues,
            screen_hash=visual_state.get("screen_hash", ""),
            timestamp_ms=time.time() * 1000,
        )
