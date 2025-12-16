"""
Atelier Widgets: Target-agnostic reactive widgets for Tiny Atelier.

These widgets follow the KgentsWidget protocol:
- Signal[S] holds state
- project() renders to any target (CLI, JSON, marimo)

Theme: Orisinal.com aesthetic - gentle ASCII art, soft tones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

# =============================================================================
# State Types
# =============================================================================


@dataclass(frozen=True)
class PieceState:
    """State for a single piece widget."""

    id: str
    artisan: str
    form: str
    content: str
    interpretation: str
    created_at: str
    inspirations: tuple[str, ...] = ()


@dataclass(frozen=True)
class GalleryState:
    """State for a gallery widget."""

    pieces: tuple[PieceState, ...] = ()
    total: int = 0
    filter_artisan: str | None = None
    filter_form: str | None = None


@dataclass(frozen=True)
class AtelierState:
    """State for the workshop status widget."""

    total_commissions: int = 0
    total_pieces: int = 0
    pending_queue: int = 0
    artisans: tuple[str, ...] = ()
    status: str = "idle"


# =============================================================================
# Widgets
# =============================================================================


class PieceWidget(KgentsWidget[PieceState]):
    """
    Widget for displaying a single piece.

    Shows:
    - Content preview
    - Artisan attribution
    - Form type
    - Interpretation
    """

    def __init__(self, state: PieceState) -> None:
        self.state = Signal.of(state)

    def project(self, target: RenderTarget) -> Any:
        s = self.state.value

        if target == RenderTarget.CLI:
            lines = [
                f"┌─ {s.form} by {s.artisan} ─┐",
                "",
            ]
            # Wrap content at 60 chars
            content_lines = s.content.split("\n")
            for line in content_lines[:8]:  # Limit preview
                lines.append(f"  {line[:60]}")
            if len(content_lines) > 8:
                lines.append("  ...")
            lines.extend(
                [
                    "",
                    f"  ─ {s.interpretation[:50]}..."
                    if len(s.interpretation) > 50
                    else f"  ─ {s.interpretation}",
                    f"└─ {s.id[:8]}... ─┘",
                ]
            )
            return "\n".join(lines)

        elif target == RenderTarget.JSON:
            return {
                "type": "piece",
                "id": s.id,
                "artisan": s.artisan,
                "form": s.form,
                "content": s.content,
                "interpretation": s.interpretation,
                "created_at": s.created_at,
                "inspirations": list(s.inspirations),
            }

        elif target == RenderTarget.MARIMO:
            # Return HTML for marimo display
            return f"""
            <div style="font-family: serif; padding: 1rem; border: 1px solid #e7e5e4; border-radius: 0.5rem;">
                <div style="color: #78716c; font-size: 0.75rem; text-transform: uppercase;">{s.form}</div>
                <div style="margin: 0.5rem 0; color: #44403c; white-space: pre-wrap;">{s.content[:500]}</div>
                <div style="color: #a8a29e; font-size: 0.875rem; font-style: italic;">{s.interpretation}</div>
                <div style="margin-top: 0.5rem; color: #d6d3d1; font-size: 0.75rem;">by {s.artisan}</div>
            </div>
            """

        return str(s.content)


class GalleryWidget(KgentsWidget[GalleryState]):
    """
    Widget for displaying a gallery of pieces.

    Shows:
    - Grid of piece previews
    - Total count
    - Filter status
    """

    def __init__(self, state: GalleryState | None = None) -> None:
        self.state = Signal.of(state or GalleryState())

    def add_piece(self, piece: PieceState) -> None:
        """Add a piece to the gallery."""
        current = self.state.value
        self.state.set(
            GalleryState(
                pieces=current.pieces + (piece,),
                total=current.total + 1,
                filter_artisan=current.filter_artisan,
                filter_form=current.filter_form,
            )
        )

    def set_filter(self, artisan: str | None = None, form: str | None = None) -> None:
        """Set gallery filter."""
        current = self.state.value
        self.state.set(
            GalleryState(
                pieces=current.pieces,
                total=current.total,
                filter_artisan=artisan,
                filter_form=form,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        s = self.state.value
        pieces = s.pieces

        # Apply filters
        if s.filter_artisan:
            pieces = tuple(p for p in pieces if p.artisan == s.filter_artisan)
        if s.filter_form:
            pieces = tuple(p for p in pieces if p.form == s.filter_form)

        if target == RenderTarget.CLI:
            if not pieces:
                return "◇ The gallery awaits its first piece."

            lines = [f"Gallery ({len(pieces)} of {s.total} pieces)", "=" * 40, ""]

            for p in pieces[:10]:  # Show first 10
                preview = p.content[:40].replace("\n", " ")
                lines.append(f"  [{p.artisan}] {preview}...")

            if len(pieces) > 10:
                lines.append(f"  ... and {len(pieces) - 10} more")

            return "\n".join(lines)

        elif target == RenderTarget.JSON:
            return {
                "type": "gallery",
                "pieces": [
                    {
                        "id": p.id,
                        "artisan": p.artisan,
                        "form": p.form,
                        "preview": p.content[:100],
                    }
                    for p in pieces
                ],
                "total": s.total,
                "displayed": len(pieces),
                "filter_artisan": s.filter_artisan,
                "filter_form": s.filter_form,
            }

        elif target == RenderTarget.MARIMO:
            if not pieces:
                return '<div style="text-align: center; color: #a8a29e; padding: 2rem;">◇ The gallery awaits its first piece.</div>'

            items = []
            for p in pieces[:12]:
                items.append(
                    f"""
                    <div style="padding: 1rem; border: 1px solid #e7e5e4; border-radius: 0.5rem; background: white;">
                        <div style="color: #78716c; font-size: 0.75rem;">{p.artisan} · {p.form}</div>
                        <div style="margin-top: 0.5rem; color: #44403c; font-size: 0.875rem; line-height: 1.4;">{p.content[:80]}...</div>
                    </div>
                    """
                )
            return f"""
            <div>
                <div style="color: #78716c; margin-bottom: 1rem;">{len(pieces)} pieces</div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                    {"".join(items)}
                </div>
            </div>
            """

        return f"Gallery: {len(pieces)} pieces"


class AtelierWidget(KgentsWidget[AtelierState]):
    """
    Widget for workshop status dashboard.

    Shows:
    - Commissions count
    - Pieces count
    - Queue depth
    - Available artisans
    - Status indicator
    """

    def __init__(self, state: AtelierState | None = None) -> None:
        self.state = Signal.of(state or AtelierState())

    def update_status(
        self,
        total_commissions: int | None = None,
        total_pieces: int | None = None,
        pending_queue: int | None = None,
        status: str | None = None,
    ) -> None:
        """Update workshop status."""
        current = self.state.value
        self.state.set(
            AtelierState(
                total_commissions=total_commissions
                if total_commissions is not None
                else current.total_commissions,
                total_pieces=total_pieces
                if total_pieces is not None
                else current.total_pieces,
                pending_queue=pending_queue
                if pending_queue is not None
                else current.pending_queue,
                artisans=current.artisans,
                status=status if status is not None else current.status,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        s = self.state.value

        # Status indicator
        status_icon = {
            "idle": "○",
            "busy": "◐",
            "error": "✗",
        }.get(s.status, "○")

        if target == RenderTarget.CLI:
            lines = [
                "╭─────────────────────────────────╮",
                "│       Tiny Atelier              │",
                "├─────────────────────────────────┤",
                f"│  Status: {status_icon} {s.status:24}│",
                f"│  Commissions: {s.total_commissions:18}│",
                f"│  Pieces: {s.total_pieces:23}│",
                f"│  Queue: {s.pending_queue:24}│",
                "├─────────────────────────────────┤",
                "│  Artisans:                      │",
            ]
            for artisan in s.artisans[:5]:
                lines.append(f"│    · {artisan:26}│")
            lines.append("╰─────────────────────────────────╯")
            return "\n".join(lines)

        elif target == RenderTarget.JSON:
            return {
                "type": "atelier_status",
                "status": s.status,
                "total_commissions": s.total_commissions,
                "total_pieces": s.total_pieces,
                "pending_queue": s.pending_queue,
                "artisans": list(s.artisans),
            }

        elif target == RenderTarget.MARIMO:
            artisan_list = "".join(f"<li>{a}</li>" for a in s.artisans)
            return f"""
            <div style="font-family: sans-serif; padding: 1.5rem; background: linear-gradient(135deg, #fef3c7 0%, #fafaf9 100%); border-radius: 0.75rem;">
                <h2 style="margin: 0 0 1rem 0; color: #44403c; font-size: 1.25rem;">Tiny Atelier</h2>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: white; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; color: #44403c;">{s.total_commissions}</div>
                        <div style="font-size: 0.75rem; color: #78716c;">Commissions</div>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; color: #44403c;">{s.total_pieces}</div>
                        <div style="font-size: 0.75rem; color: #78716c;">Pieces</div>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; color: #44403c;">{s.pending_queue}</div>
                        <div style="font-size: 0.75rem; color: #78716c;">Queue</div>
                    </div>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 0.5rem;">
                    <div style="font-size: 0.75rem; color: #78716c; margin-bottom: 0.5rem;">Artisans</div>
                    <ul style="margin: 0; padding-left: 1.25rem; color: #44403c;">{artisan_list}</ul>
                </div>
            </div>
            """

        return f"Atelier: {s.status}"


__all__ = [
    "AtelierWidget",
    "GalleryWidget",
    "PieceWidget",
    "AtelierState",
    "GalleryState",
    "PieceState",
]
