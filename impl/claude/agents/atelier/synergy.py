"""
Atelier Synergy: Cross-jewel integration for Wave 2.

This module provides the integration between Atelier and other Crown Jewels:
- Atelier → Brain: Auto-capture created pieces to memory
- Atelier → Coalition: Surface relevant creations as context

Usage:
    from agents.atelier.synergy import emit_piece_created

    # After a piece is completed
    await emit_piece_created(
        piece=completed_piece,
        session_id="session-abc",
        spectator_count=5,
        bid_count=2,
    )

The synergy bus will automatically:
1. Format the piece as a memory crystal
2. Capture it to Brain
3. Notify any interested listeners
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.atelier.artisan import Piece


async def emit_piece_created(
    piece: "Piece",
    session_id: str,
    spectator_count: int = 0,
    bid_count: int = 0,
) -> None:
    """
    Emit a synergy event when an Atelier piece is created.

    This triggers the Atelier → Brain synergy handler which
    automatically captures the piece to memory.

    Args:
        piece: The completed Piece object
        session_id: The Atelier session ID
        spectator_count: Number of spectators watching
        bid_count: Number of accepted spectator bids
    """
    from protocols.synergy import create_piece_created_event, get_synergy_bus

    event = create_piece_created_event(
        piece_id=piece.id,
        piece_type=piece.form,
        title=piece.provenance.interpretation[:50] if piece.provenance.interpretation else "Untitled",
        builder_id=piece.artisan,
        session_id=session_id,
        spectator_count=spectator_count,
        bid_count=bid_count,
    )

    bus = get_synergy_bus()
    await bus.emit(event)


async def emit_bid_accepted(
    bid_id: str,
    session_id: str,
    spectator_id: str,
    bid_type: str,
    content: str,
    tokens_spent: int,
) -> None:
    """
    Emit a synergy event when a bid is accepted.

    Args:
        bid_id: The bid ID
        session_id: The Atelier session ID
        spectator_id: The spectator who made the bid
        bid_type: Type of bid (suggest_direction, challenge, etc.)
        content: The bid content
        tokens_spent: Tokens spent on this bid
    """
    from protocols.synergy import create_bid_accepted_event, get_synergy_bus

    event = create_bid_accepted_event(
        bid_id=bid_id,
        session_id=session_id,
        spectator_id=spectator_id,
        bid_type=bid_type,
        content=content,
        tokens_spent=tokens_spent,
    )

    bus = get_synergy_bus()
    await bus.emit(event)


class SynergyAwareWorkshop:
    """
    Mixin that adds synergy emission to Workshop operations.

    Usage:
        class MyWorkshop(Workshop, SynergyAwareWorkshop):
            async def on_piece_complete(self, piece, session):
                await self.emit_piece_synergy(piece, session)
    """

    async def emit_piece_synergy(
        self,
        piece: "Piece",
        session_id: str,
        spectator_count: int = 0,
        bid_count: int = 0,
    ) -> None:
        """Emit synergy event for a completed piece."""
        await emit_piece_created(
            piece=piece,
            session_id=session_id,
            spectator_count=spectator_count,
            bid_count=bid_count,
        )


def wrap_stream_with_synergy(
    artisan_stream,
    session_id: str,
    spectator_count: int = 0,
    bid_count: int = 0,
):
    """
    Wrap an artisan stream to automatically emit synergy events.

    This decorator observes the stream and when a PIECE_COMPLETE
    event is yielded, it automatically emits the synergy event.

    Usage:
        async for event in wrap_stream_with_synergy(
            artisan.stream(commission),
            session_id="session-abc",
        ):
            yield event
    """

    async def wrapped():
        from agents.atelier.artisan import AtelierEventType, Piece

        async for event in artisan_stream:
            yield event

            # When piece completes, emit synergy
            if event.event_type == AtelierEventType.PIECE_COMPLETE:
                piece_data = event.data.get("piece")
                if piece_data:
                    # Reconstruct piece from dict if needed
                    if isinstance(piece_data, dict):
                        piece = Piece.from_dict(piece_data)
                    else:
                        piece = piece_data

                    # Emit synergy in background (non-blocking)
                    asyncio.create_task(
                        emit_piece_created(
                            piece=piece,
                            session_id=session_id,
                            spectator_count=spectator_count,
                            bid_count=bid_count,
                        )
                    )

    return wrapped()


__all__ = [
    "emit_piece_created",
    "emit_bid_accepted",
    "SynergyAwareWorkshop",
    "wrap_stream_with_synergy",
]
