"""
Exhibition: Curated thematic collections in Tiny Atelier.

An Exhibition is a curated selection of pieces around a theme,
with a curator's note explaining the artistic vision.

This implements the "museum within the workshop" concept:
- Curators select pieces based on thematic coherence
- Each exhibition tells a story through juxtaposition
- Pieces can appear in multiple exhibitions
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from agents.atelier.artisan import Piece


@dataclass(frozen=True)
class Exhibition:
    """
    A curated collection of pieces around a theme.

    Attributes:
        id: Unique identifier
        title: Exhibition title
        theme: The unifying concept
        curator_note: The curator's artistic statement
        piece_ids: IDs of pieces in the exhibition
        created_at: When the exhibition was created
    """

    id: str
    title: str
    theme: str
    curator_note: str
    piece_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "theme": self.theme,
            "curator_note": self.curator_note,
            "piece_ids": list(self.piece_ids),
            "created_at": self.created_at.isoformat(),
        }


class ExhibitionCurator:
    """
    Curates exhibitions from gallery pieces.

    The curator selects pieces based on thematic coherence,
    using heuristics or LLM-based selection.

    Works with an in-memory piece store. Use load_from_gallery()
    to populate from a file-based Gallery.

    Example:
        curator = ExhibitionCurator()
        curator.pieces = {"p1": piece1, "p2": piece2}
        exhibition = await curator.curate(
            theme="ephemeral beauty",
            title="Transient Forms"
        )
    """

    def __init__(self) -> None:
        self.pieces: dict[str, Piece] = {}
        self.exhibitions: dict[str, Exhibition] = {}

    async def curate(
        self,
        theme: str,
        title: str | None = None,
        max_pieces: int = 7,
        curator_note: str | None = None,
    ) -> Exhibition:
        """
        Curate an exhibition around a theme.

        Selection strategy (heuristic):
        1. Search gallery for theme keywords in content/interpretation
        2. Prioritize diversity of artisans
        3. Limit to max_pieces

        Args:
            theme: The unifying concept (e.g., "impermanence", "APIs", "nature")
            title: Exhibition title (auto-generated if not provided)
            max_pieces: Maximum pieces to include
            curator_note: Curator's statement (auto-generated if not provided)

        Returns:
            The created Exhibition
        """
        # Find matching pieces
        all_pieces = list(self.pieces.values())
        matching = self._find_matching_pieces(all_pieces, theme)

        # Select with artisan diversity
        selected = self._select_diverse(matching, max_pieces)

        # Generate title if needed
        if not title:
            title = self._generate_title(theme, selected)

        # Generate curator note if needed
        if not curator_note:
            curator_note = self._generate_curator_note(theme, selected)

        # Create exhibition
        exhibition = Exhibition(
            id=f"ex-{uuid.uuid4().hex[:8]}",
            title=title,
            theme=theme,
            curator_note=curator_note,
            piece_ids=tuple(p.id for p in selected),
        )

        self.exhibitions[exhibition.id] = exhibition
        return exhibition

    def _find_matching_pieces(self, pieces: list[Piece], theme: str) -> list[Piece]:
        """Find pieces matching theme keywords."""
        theme_words = set(theme.lower().split())
        scored: list[tuple[Piece, int]] = []

        for piece in pieces:
            score = 0
            text = f"{piece.content} {piece.provenance.interpretation}".lower()

            # Score based on keyword matches
            for word in theme_words:
                if word in text:
                    score += 1

            # Bonus for exact theme match
            if theme.lower() in text:
                score += 3

            if score > 0:
                scored.append((piece, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored]

    def _select_diverse(self, pieces: list[Piece], max_count: int) -> list[Piece]:
        """Select pieces with artisan diversity."""
        selected: list[Piece] = []
        artisan_counts: dict[str, int] = {}
        max_per_artisan = max(1, max_count // 3)  # At most 1/3 from same artisan

        for piece in pieces:
            if len(selected) >= max_count:
                break

            # Check artisan diversity
            count = artisan_counts.get(piece.artisan, 0)
            if count < max_per_artisan:
                selected.append(piece)
                artisan_counts[piece.artisan] = count + 1

        return selected

    def _generate_title(self, theme: str, pieces: list[Piece]) -> str:
        """Generate exhibition title from theme and pieces."""
        # Simple heuristic: capitalize theme words, add evocative suffix
        words = theme.title().split()
        if len(words) == 1:
            suffixes = ["Variations", "Studies", "Reflections", "Echoes"]
            import random

            return f"{words[0]} {random.choice(suffixes)}"
        return " ".join(words)

    def _generate_curator_note(self, theme: str, pieces: list[Piece]) -> str:
        """Generate curator's statement."""
        artisans = set(p.artisan for p in pieces)
        forms = set(p.form for p in pieces)

        return (
            f"This exhibition explores {theme} through {len(pieces)} pieces "
            f"by {', '.join(artisans)}. "
            f"Working across {', '.join(forms)}, these works illuminate "
            f"different facets of the theme."
        )

    def get(self, exhibition_id: str) -> Exhibition | None:
        """Get exhibition by ID."""
        return self.exhibitions.get(exhibition_id)

    def list_exhibitions(self) -> list[Exhibition]:
        """List all exhibitions."""
        return sorted(self.exhibitions.values(), key=lambda e: e.created_at, reverse=True)

    def delete(self, exhibition_id: str) -> bool:
        """Delete an exhibition."""
        if exhibition_id in self.exhibitions:
            del self.exhibitions[exhibition_id]
            return True
        return False


__all__ = ["Exhibition", "ExhibitionCurator"]
