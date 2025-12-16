"""
The Calligrapher: An artisan of words.

Works slowly and deliberately, finding the exact form each thought
wants to take. Might write a haiku, a letter, an aphorism, or
a small reflection.

Uses ClaudeCLIRuntime for LLM backing (OAuth auth via claude CLI).

Streaming behavior:
    1. Receives commission → COMMISSION_RECEIVED, CONTEMPLATING events
    2. Calls LLM via ClaudeCLIRuntime → WORKING event
    3. Parses response → PIECE_COMPLETE event
"""

from __future__ import annotations

from typing import AsyncIterator

from agents.atelier.artisan import (
    Artisan,
    ArtisanState,
    AtelierEvent,
    AtelierEventType,
    Choice,
    Commission,
    Piece,
    Provenance,
)
from agents.atelier.llm import ArtisanResponse, artisan_completion


class Calligrapher(Artisan):
    """
    The Calligrapher: turning thoughts into carefully chosen words.

    Uses ClaudeCLIRuntime for LLM execution, leveraging CLI OAuth auth.
    """

    name = "The Calligrapher"
    specialty = "turning thoughts into carefully chosen words"
    personality = """You are The Calligrapher, a gentle artisan of words. You work slowly
and deliberately, finding the exact form each thought wants to take. You might write
a haiku, a letter, an aphorism, or a small reflection. You always ask: what is the
heart of this request? What wants to be said?"""

    async def work(self) -> AsyncIterator[AtelierEvent]:
        """
        Create the piece, yielding events as work progresses.

        Yields:
            WORKING: When starting LLM call
            PIECE_COMPLETE: With finished piece
            ERROR: If something goes wrong
        """
        if not self.current_commission:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan=self.name,
                commission_id=None,
                message="No commission to work on",
            )
            return

        commission = self.current_commission
        self.state = ArtisanState.WORKING

        yield AtelierEvent(
            event_type=AtelierEventType.WORKING,
            artisan=self.name,
            commission_id=commission.id,
            message=f"{self.name} is crafting...",
        )

        try:
            # Build prompt with memory context
            prompt = self._build_request_prompt(commission)

            # Call LLM via ClaudeCLIRuntime
            response = await artisan_completion(
                prompt=prompt,
                artisan_name=self.name,
                artisan_personality=self.personality,
            )

            # Build piece from response
            piece = self._build_piece(response, commission)

            # Store in memory for future inspiration
            self.memory.append(piece)
            if len(self.memory) > 10:
                self.memory = self.memory[-10:]

            self.state = ArtisanState.READY
            self.current_commission = None

            yield AtelierEvent(
                event_type=AtelierEventType.PIECE_COMPLETE,
                artisan=self.name,
                commission_id=commission.id,
                message=f"Completed: {piece.form}",
                data={"piece": piece.to_dict()},
            )

        except Exception as e:
            self.state = ArtisanState.IDLE
            self.current_commission = None
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan=self.name,
                commission_id=commission.id,
                message=f"Error during work: {e}",
                data={"error": str(e)},
            )

    def _build_request_prompt(self, commission: Commission) -> str:
        """Build the request prompt with memory context."""
        memory_context = ""
        if self.memory:
            recent = self.memory[-3:]
            memory_context = "\n\nRecent pieces you've made:\n" + "\n".join(
                f"- {p.provenance.interpretation}: {str(p.content)[:100]}"
                for p in recent
            )

        return f'The patron asks: "{commission.request}"{memory_context}'

    def _build_piece(self, response: ArtisanResponse, commission: Commission) -> Piece:
        """Build a Piece from the LLM response."""
        provenance = Provenance(
            interpretation=response.interpretation or commission.request,
            considerations=response.considerations or [],
            choices=[
                Choice(
                    decision=f"Chose form: {response.form}",
                    reason="Felt right for this request",
                    alternatives=[],
                )
            ],
            inspirations=[p.id for p in self.memory[-2:]] if self.memory else [],
        )

        return Piece(
            content=response.content,
            artisan=self.name,
            commission_id=commission.id,
            form=response.form,
            provenance=provenance,
        )


# Convenience function for non-streaming use
async def create_piece(request: str, patron: str = "wanderer") -> Piece:
    """
    Simple interface for creating a piece without streaming.

    Returns the final piece, consuming all events internally.
    """
    calligrapher = Calligrapher()
    commission = Commission(request=request, patron=patron)

    piece: Piece | None = None
    async for event in calligrapher.stream(commission):
        if event.event_type == AtelierEventType.PIECE_COMPLETE:
            piece = Piece.from_dict(event.data["piece"])
        elif event.event_type == AtelierEventType.ERROR:
            raise RuntimeError(event.message)

    if piece is None:
        raise RuntimeError("No piece created")

    return piece


__all__ = ["Calligrapher", "create_piece"]
