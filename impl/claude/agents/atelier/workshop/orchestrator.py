"""
Workshop: The central orchestrator for Tiny Atelier.

Combines:
- EventBus for streaming fan-out
- Artisan management
- Commission routing
- Gallery integration
- Collaboration coordination

The Workshop is the "TownFlux" equivalent for Atelier—
the streaming core that makes everything work together.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from agents.atelier.artisan import (
    Artisan,
    AtelierEvent,
    AtelierEventType,
    Commission,
    Piece,
)
from agents.atelier.artisans import ARTISAN_REGISTRY, get_artisan
from agents.atelier.gallery.store import Gallery, get_gallery
from agents.atelier.workshop.collaboration import Collaboration, CollaborationMode
from agents.atelier.workshop.commission import CommissionQueue, get_queue
from agents.town.event_bus import EventBus, Subscription


@dataclass
class WorkshopFlux:
    """
    The streaming core of Tiny Atelier.

    Like TownFlux, WorkshopFlux is the event stream that connects
    all components. Events flow:

        Commission → Artisan → EventBus → Subscribers
                                 ↓
                          CLI / Web / Gallery

    All operations are streaming-first: instead of request/response,
    everything yields events that can be observed in real-time.
    """

    gallery: Gallery = field(default_factory=get_gallery)
    queue: CommissionQueue = field(default_factory=get_queue)
    event_bus: EventBus[AtelierEvent] = field(default_factory=lambda: EventBus(max_queue_size=1000))

    # Statistics
    total_pieces: int = 0
    total_commissions: int = 0

    async def commission(
        self,
        artisan_name: str,
        request: str,
        patron: str = "wanderer",
        stream: bool = True,
    ) -> AsyncIterator[AtelierEvent]:
        """
        Commission an artisan, streaming events as work progresses.

        This is the primary entry point for creating pieces.
        Events are both yielded to the caller and published to the EventBus.

        Args:
            artisan_name: Name of the artisan to commission
            request: What to create
            patron: Who is requesting (for provenance)
            stream: Whether to yield events (True) or just publish to bus

        Yields:
            AtelierEvent instances as work progresses
        """
        self.total_commissions += 1

        # Get artisan
        artisan_cls = get_artisan(artisan_name)
        if not artisan_cls:
            error_event = AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan="Workshop",
                commission_id=None,
                message=f"Unknown artisan: {artisan_name}. Available: {', '.join(ARTISAN_REGISTRY.keys())}",
            )
            await self.event_bus.publish(error_event)
            if stream:
                yield error_event
            return

        artisan = artisan_cls()
        commission = Commission(request=request, patron=patron)

        # Stream work
        piece: Piece | None = None
        async for event in artisan.stream(commission):
            # Publish to event bus for all subscribers
            await self.event_bus.publish(event)

            # Yield for direct caller
            if stream:
                yield event

            # Capture the final piece
            if event.event_type == AtelierEventType.PIECE_COMPLETE:
                piece = Piece.from_dict(event.data["piece"])

        # Store piece in gallery
        if piece:
            await self.gallery.store(piece)
            self.total_pieces += 1

    async def collaborate(
        self,
        artisan_names: list[str],
        request: str,
        mode: CollaborationMode | str = CollaborationMode.DUET,
        patron: str = "wanderer",
        context: dict[str, Any] | None = None,
    ) -> AsyncIterator[AtelierEvent]:
        """
        Orchestrate a collaboration between artisans.

        Args:
            artisan_names: Names of artisans to collaborate
            request: What to create together
            mode: Collaboration mode (duet, ensemble, refinement, chain, exquisite)
            patron: Who is requesting
            context: Optional context dict (e.g., visibility_ratio for exquisite mode)

        Yields:
            AtelierEvent instances as collaboration progresses
        """
        self.total_commissions += 1

        # Get all artisans
        artisans: list[Artisan] = []
        for name in artisan_names:
            artisan_cls = get_artisan(name)
            if not artisan_cls:
                error_event = AtelierEvent(
                    event_type=AtelierEventType.ERROR,
                    artisan="Workshop",
                    commission_id=None,
                    message=f"Unknown artisan: {name}",
                )
                await self.event_bus.publish(error_event)
                yield error_event
                return
            artisans.append(artisan_cls())

        # Create collaboration
        collab = Collaboration(artisans, mode)
        commission = Commission(request=request, patron=patron, context=context or {})

        # Stream collaboration
        piece: Piece | None = None
        async for event in collab.execute(commission):
            await self.event_bus.publish(event)
            yield event

            if event.event_type == AtelierEventType.PIECE_COMPLETE:
                piece = Piece.from_dict(event.data["piece"])

        # Store final piece
        if piece:
            await self.gallery.store(piece)
            self.total_pieces += 1

    async def queue_commission(
        self,
        artisan_name: str,
        request: str,
        patron: str = "wanderer",
    ) -> Commission:
        """
        Queue a commission for background processing.

        Returns immediately with the commission ID.
        Use process_queue() to process queued items.
        """
        # Validate artisan
        if not get_artisan(artisan_name):
            raise ValueError(f"Unknown artisan: {artisan_name}")

        commission = Commission(request=request, patron=patron)
        await self.queue.enqueue(commission, artisan_name)

        return commission

    async def process_queue(self) -> AsyncIterator[AtelierEvent]:
        """Process all queued commissions, streaming events."""
        async for event in self.queue.process_all():
            await self.event_bus.publish(event)
            yield event

    def subscribe(self) -> Subscription[AtelierEvent]:
        """
        Subscribe to the workshop event stream.

        Returns a subscription that yields events as they occur.
        Use for building real-time UIs, logging, etc.

        Example:
            sub = workshop.subscribe()
            async for event in sub:
                print(f"{event.artisan}: {event.message}")
        """
        return self.event_bus.subscribe()

    def get_status(self) -> dict[str, Any]:
        """Get workshop status and statistics."""
        return {
            "total_pieces": self.total_pieces,
            "total_commissions": self.total_commissions,
            "available_artisans": list(ARTISAN_REGISTRY.keys()),
            "event_bus_subscribers": self.event_bus.subscriber_count,
        }

    def close(self) -> None:
        """Close the workshop and all subscriptions."""
        self.event_bus.close()


class Workshop:
    """
    High-level workshop interface for CLI use.

    Wraps WorkshopFlux with convenient synchronous-style methods.
    For streaming, use WorkshopFlux directly.
    """

    def __init__(self) -> None:
        self.flux = WorkshopFlux()

    async def commission(
        self,
        artisan_name: str,
        request: str,
        patron: str = "wanderer",
    ) -> Piece | None:
        """
        Commission an artisan and return the final piece.

        Consumes all events, returning only the final piece.
        """
        piece: Piece | None = None
        async for event in self.flux.commission(artisan_name, request, patron):
            if event.event_type == AtelierEventType.PIECE_COMPLETE:
                piece = Piece.from_dict(event.data["piece"])
            elif event.event_type == AtelierEventType.ERROR:
                raise RuntimeError(event.message)
        return piece

    async def collaborate(
        self,
        artisan_names: list[str],
        request: str,
        mode: CollaborationMode | str = CollaborationMode.DUET,
        patron: str = "wanderer",
    ) -> Piece | None:
        """
        Run a collaboration and return the final piece.
        """
        piece: Piece | None = None
        async for event in self.flux.collaborate(artisan_names, request, mode, patron):
            if event.event_type == AtelierEventType.PIECE_COMPLETE:
                piece = Piece.from_dict(event.data["piece"])
            elif event.event_type == AtelierEventType.ERROR:
                raise RuntimeError(event.message)
        return piece

    async def queue_commission(
        self,
        artisan_name: str,
        request: str,
        patron: str = "wanderer",
    ) -> Commission:
        """Queue a commission for background processing."""
        return await self.flux.queue_commission(artisan_name, request, patron)

    @property
    def gallery(self) -> Gallery:
        """Access the gallery."""
        return self.flux.gallery

    @property
    def queue(self) -> CommissionQueue:
        """Access the commission queue."""
        return self.flux.queue


# =============================================================================
# Singleton
# =============================================================================

_default_workshop: Workshop | None = None


def get_workshop() -> Workshop:
    """Get the default workshop instance."""
    global _default_workshop
    if _default_workshop is None:
        _default_workshop = Workshop()
    return _default_workshop


__all__ = [
    "Workshop",
    "WorkshopFlux",
    "get_workshop",
]
