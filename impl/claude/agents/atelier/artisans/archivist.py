"""
The Archivist: A keeper of fragments and connections.

Collects, organizes, and synthesizes. The Archivist doesn't create
from nothing—they weave together what exists into new meaning.

Special ability: Can work with pieces from other artisans,
creating syntheses and collections.

Uses ClaudeCLIRuntime for LLM backing (OAuth auth via claude CLI).
"""

from __future__ import annotations

import json
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
from agents.atelier.llm import raw_completion


class Archivist(Artisan):
    """
    The Archivist: weaving fragments into meaning.

    Unlike other artisans who create from prompts, the Archivist
    excels at synthesis—combining and contextualizing existing work.

    Uses ClaudeCLIRuntime for LLM execution.
    """

    name = "The Archivist"
    specialty = "collecting fragments and weaving them into meaning"
    personality = """You are The Archivist, a gentle curator of meaning. You don't create
from nothing—you find the threads that connect disparate things and weave them together.
You see patterns in collections, meaning in juxtapositions. When given pieces to organize,
you create new understanding. When given a request, you search your memory for resonances."""

    def __init__(self) -> None:
        super().__init__()
        self.archive: list[Piece] = []  # Extended memory for synthesis

    def add_to_archive(self, piece: Piece) -> None:
        """Add a piece to the archive for future synthesis."""
        self.archive.append(piece)
        if len(self.archive) > 50:
            self.archive = self.archive[-50:]

    def _build_prompts(self, commission: Commission) -> tuple[str, str]:
        """Build archivist-specific prompts for raw_completion."""
        archive_context = ""
        if self.archive:
            # Select relevant pieces from archive
            recent = self.archive[-5:]
            archive_context = "\n\nFrom your archive:\n" + "\n".join(
                f'- [{p.artisan}] "{str(p.content)[:80]}..." ({p.form})' for p in recent
            )

        source_pieces = commission.context.get("source_pieces", [])
        source_context = ""
        if source_pieces:
            source_context = "\n\nPieces to work with:\n" + "\n".join(
                f'- [{p.get("artisan", "unknown")}] "{str(p.get("content", ""))[:80]}..."'
                for p in source_pieces
            )

        system_prompt = f"""{self.personality}

Create an archival piece. Respond with valid JSON only (no markdown code blocks):
{{
  "interpretation": "how you understood this request",
  "considerations": ["what themes you noticed"],
  "content": "your synthesis or collection",
  "form": "synthesis|collection|annotation|exhibition",
  "threads": ["themes or connections you found"]
}}"""

        user_message = (
            f'The patron asks: "{commission.request}"{archive_context}{source_context}'
        )

        return system_prompt, user_message

    async def work(self) -> AsyncIterator[AtelierEvent]:
        """Create the archival piece, yielding events as work progresses."""
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
            message=f"{self.name} is searching the archive...",
        )

        try:
            # Build archivist-specific prompts
            system_prompt, user_message = self._build_prompts(commission)

            # Call LLM via ClaudeCLIRuntime
            response_text, _ = await raw_completion(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.7,
                max_tokens=1500,
            )

            # Parse and build piece
            piece = self._parse_response(response_text, commission)

            # Archivist stores everything
            self.memory.append(piece)
            self.archive.append(piece)
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

    def _parse_response(self, text: str, commission: Commission) -> Piece:
        """Parse LLM response into a Piece."""
        # Extract JSON from response
        cleaned = text.strip()
        if "```json" in cleaned:
            start = cleaned.find("```json") + 7
            end = cleaned.find("```", start)
            if end > start:
                cleaned = cleaned[start:end].strip()
        elif "```" in cleaned:
            start = cleaned.find("```") + 3
            end = cleaned.find("```", start)
            if end > start:
                cleaned = cleaned[start:end].strip()

        if "{" in cleaned:
            start = cleaned.find("{")
            depth = 0
            end = start
            for i, char in enumerate(cleaned[start:], start):
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            cleaned = cleaned[start:end]

        try:
            data = json.loads(cleaned)
            threads = data.get("threads", [])

            provenance = Provenance(
                interpretation=data.get("interpretation", commission.request),
                considerations=data.get("considerations", []),
                choices=[
                    Choice(
                        decision=f"Created {data.get('form', 'synthesis')}",
                        reason=f"Found threads: {', '.join(threads[:3])}"
                        if threads
                        else "Patterns emerged",
                        alternatives=[],
                    )
                ],
                inspirations=[p.id for p in self.archive[-3:]] if self.archive else [],
            )

            return Piece(
                content=data.get("content", text),
                artisan=self.name,
                commission_id=commission.id,
                form=data.get("form", "synthesis"),
                provenance=provenance,
            )
        except json.JSONDecodeError:
            return Piece(
                content=text,
                artisan=self.name,
                commission_id=commission.id,
                form="fragment",
                provenance=Provenance(
                    interpretation=commission.request,
                    considerations=[],
                    choices=[],
                    inspirations=[],
                ),
            )

    async def synthesize(
        self, pieces: list[Piece], theme: str
    ) -> AsyncIterator[AtelierEvent]:
        """
        Special method: synthesize multiple pieces into one.

        This is the Archivist's unique ability—creating meaning
        from existing work rather than from scratch.
        """
        # Add pieces to context
        commission = Commission(
            request=f"Synthesize these pieces around the theme: {theme}",
            context={"source_pieces": [p.to_dict() for p in pieces]},
        )

        async for event in self.stream(commission):
            yield event


__all__ = ["Archivist"]
