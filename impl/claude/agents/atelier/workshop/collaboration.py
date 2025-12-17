"""
Collaboration: Multi-artisan composition with streaming.

Implements the composition patterns defined in ATELIER_OPERAD:
- Duet: A creates → B transforms
- Ensemble: All create in parallel → merge
- Refinement: A creates → B refines
- Chain: A → B → C → ...

All collaborations are streaming-first, yielding events as work progresses.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import AsyncIterator

from agents.atelier.artisan import (
    Artisan,
    AtelierEvent,
    AtelierEventType,
    Choice,
    Commission,
    Piece,
    Provenance,
)


class CollaborationMode(Enum):
    """Collaboration modes from ATELIER_OPERAD."""

    DUET = "duet"
    ENSEMBLE = "ensemble"
    REFINEMENT = "refinement"
    CHAIN = "chain"
    EXQUISITE = "exquisite"  # Exquisite corpse: limited visibility handoffs


@dataclass
class CollaborationResult:
    """Result of a collaboration."""

    piece: Piece
    participants: list[str]  # Artisan names
    mode: CollaborationMode
    intermediate_pieces: list[Piece]  # Pieces created along the way


class Collaboration:
    """
    Orchestrates multi-artisan collaboration with streaming.

    All methods yield AtelierEvents as work progresses,
    enabling real-time observation of the collaboration.
    """

    def __init__(
        self,
        artisans: list[Artisan],
        mode: CollaborationMode | str = CollaborationMode.DUET,
    ) -> None:
        self.artisans = artisans
        self.mode = CollaborationMode(mode) if isinstance(mode, str) else mode

    async def execute(self, commission: Commission) -> AsyncIterator[AtelierEvent]:
        """
        Execute the collaboration, streaming events.

        The final event will be PIECE_COMPLETE with the final piece.
        """
        if self.mode == CollaborationMode.DUET:
            async for event in self._duet(commission):
                yield event
        elif self.mode == CollaborationMode.ENSEMBLE:
            async for event in self._ensemble(commission):
                yield event
        elif self.mode == CollaborationMode.REFINEMENT:
            async for event in self._refinement(commission):
                yield event
        elif self.mode == CollaborationMode.CHAIN:
            async for event in self._chain(commission):
                yield event
        elif self.mode == CollaborationMode.EXQUISITE:
            async for event in self._exquisite(commission):
                yield event

    async def _duet(self, commission: Commission) -> AsyncIterator[AtelierEvent]:
        """
        Duet: First artisan creates, second transforms.

        Flow: A creates → B receives A's output → B creates final piece
        """
        if len(self.artisans) < 2:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan="Collaboration",
                commission_id=commission.id,
                message="Duet requires at least 2 artisans",
            )
            return

        first, second = self.artisans[:2]
        first_piece: Piece | None = None

        # First artisan creates
        yield AtelierEvent(
            event_type=AtelierEventType.CONTEMPLATING,
            artisan="Collaboration",
            commission_id=commission.id,
            message=f"Beginning duet: {first.name} → {second.name}",
        )

        async for event in first.stream(commission):
            yield event
            if event.event_type == AtelierEventType.PIECE_COMPLETE:
                first_piece = Piece.from_dict(event.data["piece"])
            elif event.event_type == AtelierEventType.ERROR:
                return

        if not first_piece:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan="Collaboration",
                commission_id=commission.id,
                message="First artisan produced no piece",
            )
            return

        # Second artisan transforms
        transform_commission = Commission(
            request=f"Transform and reimagine this in your own style:\n\n{first_piece.content}",
            patron=commission.patron,
            context={
                "source_piece_id": first_piece.id,
                "source_artisan": first.name,
                "collaboration": "duet",
            },
        )

        async for event in second.stream(transform_commission):
            if event.event_type == AtelierEventType.PIECE_COMPLETE:
                # Enhance provenance with collaboration info
                piece_data = event.data["piece"]
                piece_data["provenance"]["inspirations"].append(first_piece.id)
                piece_data["provenance"]["choices"].append(
                    {
                        "decision": f"Collaborated with {first.name}",
                        "reason": "Duet composition",
                        "alternatives": [],
                    }
                )
                event.data["piece"] = piece_data
            yield event

    async def _ensemble(self, commission: Commission) -> AsyncIterator[AtelierEvent]:
        """
        Ensemble: All artisans work in parallel, results merged.

        Flow: All create simultaneously → Archivist-style merge
        """
        yield AtelierEvent(
            event_type=AtelierEventType.CONTEMPLATING,
            artisan="Collaboration",
            commission_id=commission.id,
            message=f"Beginning ensemble with {len(self.artisans)} artisans",
        )

        # Run all artisans in parallel
        async def collect_piece(
            artisan: Artisan,
        ) -> tuple[list[AtelierEvent], Piece | None]:
            events: list[AtelierEvent] = []
            piece: Piece | None = None
            async for event in artisan.stream(commission):
                events.append(event)
                if event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
            return events, piece

        # Gather all results
        results = await asyncio.gather(
            *[collect_piece(artisan) for artisan in self.artisans]
        )

        # Yield events from all artisans (interleaved would be better, but complex)
        pieces: list[Piece] = []
        for events, piece in results:
            for event in events:
                yield event
            if piece:
                pieces.append(piece)

        if not pieces:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan="Collaboration",
                commission_id=commission.id,
                message="No pieces created by ensemble",
            )
            return

        # Merge pieces
        merged_content = "\n\n---\n\n".join(
            f"[{p.artisan}]\n{p.content}" for p in pieces
        )

        merged_piece = Piece(
            content=merged_content,
            artisan="Ensemble",
            commission_id=commission.id,
            form="collection",
            provenance=Provenance(
                interpretation=f"Ensemble of {len(pieces)} voices",
                considerations=[
                    f"{p.artisan}: {p.provenance.interpretation}" for p in pieces
                ],
                choices=[
                    Choice(
                        decision="Created ensemble collection",
                        reason="Multiple perspectives on the same theme",
                        alternatives=["Could have synthesized more deeply"],
                    )
                ],
                inspirations=[p.id for p in pieces],
            ),
        )

        yield AtelierEvent(
            event_type=AtelierEventType.PIECE_COMPLETE,
            artisan="Ensemble",
            commission_id=commission.id,
            message=f"Completed ensemble of {len(pieces)} pieces",
            data={"piece": merged_piece.to_dict()},
        )

    async def _refinement(self, commission: Commission) -> AsyncIterator[AtelierEvent]:
        """
        Refinement: First creates, second refines.

        Flow: A creates → B refines with explicit improvement goal
        """
        if len(self.artisans) < 2:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan="Collaboration",
                commission_id=commission.id,
                message="Refinement requires at least 2 artisans",
            )
            return

        first, second = self.artisans[:2]
        first_piece: Piece | None = None

        yield AtelierEvent(
            event_type=AtelierEventType.CONTEMPLATING,
            artisan="Collaboration",
            commission_id=commission.id,
            message=f"Beginning refinement: {first.name} → {second.name}",
        )

        # First artisan creates
        async for event in first.stream(commission):
            yield event
            if event.event_type == AtelierEventType.PIECE_COMPLETE:
                first_piece = Piece.from_dict(event.data["piece"])
            elif event.event_type == AtelierEventType.ERROR:
                return

        if not first_piece:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan="Collaboration",
                commission_id=commission.id,
                message="First artisan produced no piece",
            )
            return

        # Second artisan refines
        refine_commission = Commission(
            request=f"Refine and improve this work, keeping its essence but elevating it:\n\n{first_piece.content}",
            patron=commission.patron,
            context={
                "source_piece_id": first_piece.id,
                "source_artisan": first.name,
                "collaboration": "refinement",
                "refining": True,
            },
        )

        async for event in second.stream(refine_commission):
            if event.event_type == AtelierEventType.PIECE_COMPLETE:
                piece_data = event.data["piece"]
                piece_data["provenance"]["inspirations"].append(first_piece.id)
                piece_data["provenance"]["choices"].append(
                    {
                        "decision": f"Refined {first.name}'s work",
                        "reason": "Elevation while preserving essence",
                        "alternatives": [],
                    }
                )
                event.data["piece"] = piece_data
            yield event

    async def _chain(self, commission: Commission) -> AsyncIterator[AtelierEvent]:
        """
        Chain: Sequential pipeline where each transforms the previous.

        Flow: A → B → C → ... (each receives previous output)
        """
        if not self.artisans:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan="Collaboration",
                commission_id=commission.id,
                message="Chain requires at least 1 artisan",
            )
            return

        yield AtelierEvent(
            event_type=AtelierEventType.CONTEMPLATING,
            artisan="Collaboration",
            commission_id=commission.id,
            message=f"Beginning chain of {len(self.artisans)} artisans",
        )

        current_commission = commission
        previous_pieces: list[str] = []

        for i, artisan in enumerate(self.artisans):
            is_last = i == len(self.artisans) - 1

            async for event in artisan.stream(current_commission):
                yield event
                if event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    previous_pieces.append(piece.id)

                    if is_last:
                        # Final piece gets full lineage
                        piece.provenance.inspirations.extend(previous_pieces[:-1])
                        # piece is the final result (referenced via pieces[-1])
                    else:
                        # Prepare next commission
                        current_commission = Commission(
                            request=f"Continue this creative journey:\n\n{piece.content}",
                            patron=commission.patron,
                            context={
                                "source_piece_id": piece.id,
                                "chain_position": i + 1,
                                "collaboration": "chain",
                            },
                        )
                elif event.event_type == AtelierEventType.ERROR:
                    return

    async def _exquisite(self, commission: Commission) -> AsyncIterator[AtelierEvent]:
        """
        Exquisite Corpse: Limited visibility handoffs.

        Each artisan only sees the "edge" (last portion) of the previous work,
        creating surprising continuations. Inspired by the Surrealist game.

        Flow: A creates → B sees only last 10% → B continues → C sees only B's last 10% → ...

        The visibility_ratio can be customized in commission context.
        """
        if not self.artisans:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan="Collaboration",
                commission_id=commission.id,
                message="Exquisite corpse requires at least 1 artisan",
            )
            return

        # Default visibility: see only last 10% of previous work
        visibility_ratio = commission.context.get("visibility_ratio", 0.10)

        yield AtelierEvent(
            event_type=AtelierEventType.CONTEMPLATING,
            artisan="Collaboration",
            commission_id=commission.id,
            message=f"Beginning exquisite corpse with {len(self.artisans)} artisans (visibility: {int(visibility_ratio * 100)}%)",
        )

        current_commission = commission
        all_pieces: list[Piece] = []
        full_content_parts: list[str] = []  # Track full content for final reveal

        for i, artisan in enumerate(self.artisans):
            is_last = i == len(self.artisans) - 1

            async for event in artisan.stream(current_commission):
                yield event
                if event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                    all_pieces.append(piece)
                    full_content_parts.append(f"[{artisan.name}]\n{piece.content}")

                    if not is_last:
                        # Extract the visible edge for next artisan
                        visible_edge = _extract_edge(
                            str(piece.content), visibility_ratio
                        )

                        # Prepare next commission with limited visibility
                        current_commission = Commission(
                            request=f"Continue from this fragment (you can only see the edge of what came before):\n\n---\n{visible_edge}\n---\n\n{commission.request}",
                            patron=commission.patron,
                            context={
                                "source_piece_id": piece.id,
                                "exquisite_position": i + 1,
                                "collaboration": "exquisite",
                                "visibility_ratio": visibility_ratio,
                            },
                        )
                elif event.event_type == AtelierEventType.ERROR:
                    return

        # Create final merged piece with reveal
        if all_pieces:
            # The exquisite corpse reveals the full creation
            merged_content = "\n\n✧ ✧ ✧\n\n".join(full_content_parts)

            final_piece = Piece(
                content=merged_content,
                artisan="Exquisite Corpse",
                commission_id=commission.id,
                form="exquisite_corpse",
                provenance=Provenance(
                    interpretation=f"Exquisite corpse with {len(all_pieces)} contributors, each seeing only {int(visibility_ratio * 100)}% of the previous",
                    considerations=[
                        f"{p.artisan} contributed: {str(p.content)[:50]}..."
                        for p in all_pieces
                    ],
                    choices=[
                        Choice(
                            decision="Limited visibility handoffs",
                            reason="Surrealist technique for unexpected continuations",
                            alternatives=[
                                "Full visibility (chain mode)",
                                "No visibility (parallel)",
                            ],
                        )
                    ],
                    inspirations=[p.id for p in all_pieces],
                ),
            )

            yield AtelierEvent(
                event_type=AtelierEventType.PIECE_COMPLETE,
                artisan="Exquisite Corpse",
                commission_id=commission.id,
                message=f"✧ Exquisite corpse revealed! {len(all_pieces)} artisans contributed",
                data={"piece": final_piece.to_dict()},
            )


def _extract_edge(content: str, ratio: float = 0.10) -> str:
    """
    Extract the visible "edge" of content for exquisite corpse mode.

    For text: returns the last N% of characters/lines.
    The extraction preserves line boundaries when possible.
    """
    if not content:
        return ""

    lines = content.split("\n")

    if len(lines) <= 3:
        # For very short content, show at least the last line
        return lines[-1] if lines else ""

    # Calculate visible lines (minimum 1)
    visible_count = max(1, int(len(lines) * ratio))
    visible_lines = lines[-visible_count:]

    return "\n".join(visible_lines)


__all__ = ["Collaboration", "CollaborationMode", "CollaborationResult", "_extract_edge"]
