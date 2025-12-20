"""
Atelier to Brain Handler: Auto-capture created pieces.

Wave 2: Extensions - Atelier → Brain synergy.

When a builder completes a piece in the Atelier, this handler
automatically captures it to Brain as a memory crystal.

This enables:
- Historical artifact tracking
- Cross-session creative context
- Gardener awareness of past creations
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..events import SynergyEvent, SynergyEventType, SynergyResult
from .base import BaseSynergyHandler


class AtelierToBrainHandler(BaseSynergyHandler):
    """
    Handler that captures Atelier pieces to Brain.

    When a builder completes a piece:
    1. Creates a summary of the creation
    2. Captures it to Brain as a memory crystal
    3. Returns the crystal ID for reference

    The crystal content includes:
    - Piece type and title
    - Builder and session info
    - Spectator engagement metrics
    - Timestamp for historical tracking
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
        return "AtelierToBrainHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle an Atelier piece created event."""
        if event.event_type != SynergyEventType.PIECE_CREATED:
            return self.skip(f"Not handling {event.event_type.value}")

        payload = event.payload
        piece_type = payload.get("piece_type", "unknown")
        title = payload.get("title", "Untitled")
        builder_id = payload.get("builder_id", "anonymous")
        session_id = payload.get("session_id", "")
        spectator_count = payload.get("spectator_count", 0)
        bid_count = payload.get("bid_count", 0)

        # Create crystal content
        content = self._create_crystal_content(
            piece_id=event.source_id,
            piece_type=piece_type,
            title=title,
            builder_id=builder_id,
            session_id=session_id,
            spectator_count=spectator_count,
            bid_count=bid_count,
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture: {content[:100]}...")
            return self.success(
                message="Dry run - would capture Atelier piece",
                metadata={
                    "content_preview": content[:100],
                    "piece_type": piece_type,
                    "title": title,
                },
            )

        # Actually capture to Brain
        try:
            crystal_id = await self._capture_to_brain(content, event.source_id, piece_type, event)
            self._logger.info(f"Captured Atelier piece: {crystal_id}")
            return self.success(
                message="Atelier piece captured to Brain",
                artifact_id=crystal_id,
                metadata={
                    "piece_type": piece_type,
                    "title": title,
                    "spectator_count": spectator_count,
                    "bid_count": bid_count,
                },
            )
        except Exception as e:
            self._logger.error(f"Failed to capture to Brain: {e}")
            return self.failure(f"Capture failed: {e}")

    def _create_crystal_content(
        self,
        piece_id: str,
        piece_type: str,
        title: str,
        builder_id: str,
        session_id: str,
        spectator_count: int,
        bid_count: int,
        timestamp: datetime,
    ) -> str:
        """Create the content to capture as a crystal."""
        engagement = (
            "No spectators"
            if spectator_count == 0
            else (f"{spectator_count} spectators, {bid_count} bids accepted")
        )

        return f"""Atelier Creation: {title}

Timestamp: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Details:
- Type: {piece_type}
- Piece ID: {piece_id}
- Builder: {builder_id}
- Session: {session_id}
- Engagement: {engagement}

This creation was automatically captured by the Atelier → Brain synergy.
Use this for:
- Creative history tracking
- Inspiration surfacing
- Session context
"""

    async def _capture_to_brain(
        self,
        content: str,
        piece_id: str,
        piece_type: str,
        event: SynergyEvent,
    ) -> str:
        """Capture content to Brain and return crystal ID."""
        # Import here to avoid circular imports
        from protocols.agentese import create_logos
        from protocols.agentese.node import Observer

        # Create a minimal logos for capture
        logos = create_logos()
        observer = Observer.guest()

        # Create concept ID based on piece info
        date_str = event.timestamp.strftime("%Y-%m-%d")
        concept_id = f"atelier-{piece_type}-{piece_id[:8]}-{date_str}"

        result = await logos.invoke(
            "self.memory.capture",
            observer,
            content=content,
            concept_id=concept_id,
        )

        # Return the concept ID
        returned_id: str = str(result.get("concept_id", concept_id))
        return returned_id


__all__ = ["AtelierToBrainHandler"]
