"""
Gallery Seeds: Pre-seeded sample pieces for new users.

These examples demonstrate the artisans' capabilities and provide
a starting point for the gallery experience.

Theme: Orisinal.com aesthetic—whimsical, minimal, melancholic but hopeful.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from agents.atelier.artisan import Choice, Piece, Provenance

if TYPE_CHECKING:
    from agents.atelier.gallery.store import Gallery


# =============================================================================
# Sample Pieces
# =============================================================================

SAMPLE_PIECES: list[dict[str, Any]] = [
    {
        "id": "seed001",
        "artisan": "calligrapher",
        "commission_id": "seed-commission-001",
        "form": "haiku",
        "content": """persistence calls
through fog of morning doubts—
one step, then another""",
        "provenance": {
            "interpretation": "A meditation on the quiet courage of continuing",
            "considerations": [
                "The word 'persistence' felt too formal at first",
                "Morning fog as metaphor for uncertainty",
                "The ending needed to feel actionable, not abstract",
            ],
            "choices": [
                {
                    "decision": "Use 'calls' instead of 'speaks'",
                    "reason": "Calls implies both urgency and invitation",
                    "alternatives": ["whispers", "speaks", "echoes"],
                },
                {
                    "decision": "End with concrete action",
                    "reason": "Abstract endings feel hollow; 'one step' is tangible",
                    "alternatives": ["hope remains", "light breaks through"],
                },
            ],
            "inspirations": [],
        },
    },
    {
        "id": "seed002",
        "artisan": "cartographer",
        "commission_id": "seed-commission-002",
        "form": "map",
        "content": """{
  "title": "A Morning Routine",
  "regions": [
    {"name": "The Bed", "mood": "reluctant warmth", "connections": ["The Floor"]},
    {"name": "The Floor", "mood": "cold clarity", "connections": ["The Kitchen", "The Bathroom"]},
    {"name": "The Kitchen", "mood": "ritual comfort", "connections": ["The Coffee"]},
    {"name": "The Coffee", "mood": "awakening", "connections": ["The Window"]},
    {"name": "The Window", "mood": "possibility", "connections": ["The World"]}
  ],
  "legend": "Each step is a small crossing"
}""",
        "provenance": {
            "interpretation": "A map of the daily journey from sleep to engagement",
            "considerations": [
                "Mornings are territories we traverse half-awake",
                "Each location has its own emotional weather",
                "The journey is familiar yet never quite the same",
            ],
            "choices": [
                {
                    "decision": "Include mood for each region",
                    "reason": "Maps of experience need emotional coordinates",
                    "alternatives": ["just locations", "time estimates"],
                },
                {
                    "decision": "End at 'The World'",
                    "reason": "The morning routine is preparation for engagement",
                    "alternatives": ["The Door", "The Day"],
                },
            ],
            "inspirations": [],
        },
    },
    {
        "id": "seed003",
        "artisan": "correspondent",
        "commission_id": "seed-commission-003",
        "form": "letter",
        "content": """Dear Future Self,

I write to you from a Tuesday that feels ordinary,
but I suspect you'll remember it differently.

The coffee is cooling beside me. Outside,
someone is learning to parallel park—badly.
These small things accumulate into a life.

I hope you're still curious. I hope you still
stop to notice how light falls through windows
at certain hours. I hope the bad parking
still makes you smile.

Be gentle with yourself.

— Your Present Self""",
        "provenance": {
            "interpretation": "A letter bridging temporal selves with tenderness",
            "considerations": [
                "Letters to future self often feel preachy",
                "Specific details anchor abstract sentiment",
                "Gentleness is underrated as advice",
            ],
            "choices": [
                {
                    "decision": "Include mundane details (parking, coffee)",
                    "reason": "Specificity creates resonance that abstraction cannot",
                    "alternatives": ["focus on achievements", "give advice"],
                },
                {
                    "decision": "End with self-compassion",
                    "reason": "We rarely tell ourselves to be gentle",
                    "alternatives": ["encouragement", "instructions"],
                },
            ],
            "inspirations": [],
        },
    },
]


# =============================================================================
# Seeding Functions
# =============================================================================


def create_sample_pieces() -> list[Piece]:
    """Create Piece objects from sample data."""
    pieces = []
    for data in SAMPLE_PIECES:
        provenance = Provenance(
            interpretation=data["provenance"]["interpretation"],
            considerations=data["provenance"]["considerations"],
            choices=[
                Choice(
                    decision=c["decision"],
                    reason=c["reason"],
                    alternatives=c.get("alternatives", []),
                )
                for c in data["provenance"]["choices"]
            ],
            inspirations=data["provenance"].get("inspirations", []),
        )
        piece = Piece(
            id=data["id"],
            content=data["content"],
            artisan=data["artisan"],
            commission_id=data["commission_id"],
            form=data["form"],
            provenance=provenance,
            created_at=datetime.now(),
        )
        pieces.append(piece)
    return pieces


async def seed_gallery(gallery: "Gallery", force: bool = False) -> list[str]:
    """
    Seed the gallery with sample pieces.

    Args:
        gallery: Gallery instance to seed
        force: If True, overwrite existing pieces with same IDs

    Returns:
        List of piece IDs that were added
    """
    added = []
    pieces = create_sample_pieces()

    for piece in pieces:
        existing = await gallery.get(piece.id)
        if existing and not force:
            continue
        await gallery.store(piece)
        added.append(piece.id)

    return added


async def clear_seeds(gallery: "Gallery") -> list[str]:
    """
    Remove seed pieces from gallery.

    Returns:
        List of piece IDs that were removed
    """
    removed = []
    for data in SAMPLE_PIECES:
        piece_id = data["id"]
        deleted = await gallery.delete(piece_id)
        if deleted:
            removed.append(piece_id)
    return removed


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SAMPLE_PIECES",
    "create_sample_pieces",
    "seed_gallery",
    "clear_seeds",
]
