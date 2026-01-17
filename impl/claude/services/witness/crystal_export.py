"""
Crystal Export: Shareable Artifacts from Compressed Memory.

This module exports crystals as shareable artifacts:
- Markdown: Human-readable format for sharing
- Image (PNG): Social media friendly visual card
- URL: Shareable link (when hosted)

Philosophy:
    "The crystal ends as a shareable artifact."
    "Kent's proof of intention, made beautiful and honest."

Design Principles:
    - Minimal, elegant design (not gaudy)
    - "Daring, bold, creative, opinionated but not gaudy"
    - Honest disclosure of what was dropped
    - Warm, personal tone throughout

See: pilots/trail-to-crystal-daily-lab.md
See: plans/enlightened-synthesis/04-joy-integration.md
"""

from __future__ import annotations

import base64
import hashlib
import io
import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .crystal import Crystal, CrystalLevel

if TYPE_CHECKING:
    from PIL import Image as PILImage  # type: ignore[import-not-found]

    from .crystal_compression import CompressionResult

logger = logging.getLogger("kgents.witness.crystal_export")


# =============================================================================
# Constants
# =============================================================================

# Default image dimensions (optimized for social sharing)
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 630  # OG image aspect ratio

# Color palette (tasteful, not gaudy)
PALETTE = {
    "background": "#1a1a2e",  # Deep navy
    "surface": "#16213e",  # Darker navy
    "primary": "#0f3460",  # Blue accent
    "accent": "#e94560",  # Warm coral accent
    "text_primary": "#ffffff",
    "text_secondary": "#a8b0c5",
    "text_muted": "#6b7280",
}

# Principle colors (for visual weight)
PRINCIPLE_COLORS = {
    "tasteful": "#8b5cf6",  # Purple
    "curated": "#06b6d4",  # Cyan
    "ethical": "#10b981",  # Green
    "joy-inducing": "#f59e0b",  # Amber
    "composable": "#6366f1",  # Indigo
    "heterarchical": "#ec4899",  # Pink
    "generative": "#84cc16",  # Lime
}


# =============================================================================
# Exported Crystal Data Structure
# =============================================================================


@dataclass
class ExportedCrystal:
    """
    A crystal prepared for export as shareable artifact.

    This dataclass contains all the information needed to render
    a crystal in various export formats (markdown, image, URL).
    """

    id: str
    content: str  # The crystal summary (insight + significance)
    date: date
    coherence_score: float  # Galois loss inverted (1 - loss = coherence)
    principle_weights: dict[str, float]  # 7 principles with scores
    dropped_count: int  # Honesty: how much was lost
    dropped_summary: str  # What was dropped (warm disclosure)

    # Optional shareable links
    shareable_url: str | None = None
    image_path: str | None = None

    # Metadata
    level: CrystalLevel = CrystalLevel.DAY
    source_count: int = 0  # How many marks contributed
    confidence: float = 0.8  # Crystal confidence

    # Additional context
    mood_dominant: str = ""  # Dominant mood quality
    topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "date": self.date.isoformat(),
            "coherence_score": self.coherence_score,
            "principle_weights": self.principle_weights,
            "dropped_count": self.dropped_count,
            "dropped_summary": self.dropped_summary,
            "shareable_url": self.shareable_url,
            "image_path": self.image_path,
            "level": self.level.name,
            "source_count": self.source_count,
            "confidence": self.confidence,
            "mood_dominant": self.mood_dominant,
            "topics": self.topics,
        }


# =============================================================================
# Crystal Exporter
# =============================================================================


class CrystalExporter:
    """
    Exports crystals as shareable artifacts.

    Supports multiple export formats:
    - Markdown: Human-readable, shareable as text
    - Image (PNG): Visual card for social sharing
    - URL: Shareable link (when hosted)

    Design philosophy:
    - Minimal, elegant design
    - Honest disclosure (Amendment G)
    - Warm, personal tone
    """

    def __init__(
        self,
        base_url: str | None = None,
        export_dir: Path | None = None,
    ):
        """
        Initialize the exporter.

        Args:
            base_url: Base URL for shareable links (e.g., "https://kgents.dev/crystals/")
            export_dir: Directory for exported files (defaults to temp)
        """
        self._base_url = base_url
        self._export_dir = export_dir or Path.home() / ".kgents" / "exports"
        self._export_dir.mkdir(parents=True, exist_ok=True)

    def prepare_export(
        self,
        crystal: Crystal,
        compression_result: "CompressionResult | None" = None,
    ) -> ExportedCrystal:
        """
        Prepare a crystal for export.

        Args:
            crystal: The crystal to export
            compression_result: Optional compression result for detailed honesty

        Returns:
            ExportedCrystal ready for rendering
        """
        # Extract date from time range or crystallized_at
        if crystal.time_range:
            crystal_date = crystal.time_range[0].date()
        else:
            crystal_date = crystal.crystallized_at.date()

        # Compute coherence score (inverse of Galois loss)
        if compression_result:
            coherence_score = 1.0 - compression_result.honesty.galois_loss
            dropped_count = compression_result.dropped_count
            dropped_summary = compression_result.honesty.warm_disclosure
        else:
            coherence_score = crystal.confidence
            dropped_count = 0
            dropped_summary = "Full preservation."

        # Extract principle weights from constitutional meta
        principle_weights = self._extract_principle_weights(crystal)

        # Combine insight and significance for content
        content = f"{crystal.insight}\n\n{crystal.significance}"

        return ExportedCrystal(
            id=str(crystal.id),
            content=content,
            date=crystal_date,
            coherence_score=coherence_score,
            principle_weights=principle_weights,
            dropped_count=dropped_count,
            dropped_summary=dropped_summary,
            level=crystal.level,
            source_count=crystal.source_count,
            confidence=crystal.confidence,
            mood_dominant=crystal.mood.dominant_quality,
            topics=list(crystal.topics)[:5],
        )

    def _extract_principle_weights(self, crystal: Crystal) -> dict[str, float]:
        """Extract principle weights from crystal constitutional meta."""
        weights = {
            "tasteful": 0.5,
            "curated": 0.5,
            "ethical": 0.5,
            "joy-inducing": 0.5,
            "composable": 0.5,
            "heterarchical": 0.5,
            "generative": 0.5,
        }

        if crystal.constitutional_meta and crystal.constitutional_meta.principle_trends:
            for principle, score in crystal.constitutional_meta.principle_trends.items():
                key = principle.lower().replace("_", "-")
                if key in weights:
                    weights[key] = score

        return weights

    # =========================================================================
    # Markdown Export
    # =========================================================================

    async def export_as_markdown(
        self,
        crystal: Crystal,
        compression_result: "CompressionResult | None" = None,
        include_metadata: bool = True,
    ) -> str:
        """
        Export crystal as shareable markdown.

        Args:
            crystal: The crystal to export
            compression_result: Optional compression result for honesty details
            include_metadata: Whether to include metadata section

        Returns:
            Markdown string ready for sharing
        """
        exported = self.prepare_export(crystal, compression_result)

        lines = [
            f"# Crystal: {exported.date.strftime('%B %d, %Y')}",
            "",
        ]

        # Content section
        lines.append("## What Emerged")
        lines.append("")
        lines.append(crystal.insight)
        lines.append("")

        if crystal.significance:
            lines.append("## Why It Matters")
            lines.append("")
            lines.append(crystal.significance)
            lines.append("")

        # Principles section (visual weight)
        if crystal.principles:
            lines.append("## Principles")
            lines.append("")
            for principle in crystal.principles[:5]:
                weight = exported.principle_weights.get(principle, 0.5)
                bar = self._render_progress_bar(weight)
                lines.append(f"- **{principle.title()}**: {bar} {weight:.0%}")
            lines.append("")

        # Honesty disclosure (Amendment G)
        lines.append("## Honest Disclosure")
        lines.append("")
        lines.append(f"*{exported.dropped_summary}*")
        lines.append("")
        if exported.dropped_count > 0:
            lines.append(f"- Marks compressed: {exported.dropped_count}")
        lines.append(f"- Coherence: {exported.coherence_score:.0%}")
        lines.append("")

        # Metadata section
        if include_metadata:
            lines.append("---")
            lines.append("")
            lines.append(f"*Crystallized from {exported.source_count} marks*")
            lines.append(f"*Level: {exported.level.name.title()}*")
            lines.append(f"*Confidence: {exported.confidence:.0%}*")
            if exported.topics:
                lines.append(f"*Topics: {', '.join(exported.topics)}*")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Witnessed by kgents - turning days into proof of intention*")

        return "\n".join(lines)

    def _render_progress_bar(self, value: float, width: int = 10) -> str:
        """Render a text progress bar."""
        filled = int(value * width)
        empty = width - filled
        return "[" + "#" * filled + "-" * empty + "]"

    # =========================================================================
    # Image Export
    # =========================================================================

    async def export_as_image(
        self,
        crystal: Crystal,
        path: Path | None = None,
        compression_result: "CompressionResult | None" = None,
    ) -> Path:
        """
        Export crystal as image (PNG) for social sharing.

        Creates a minimal, elegant visual card suitable for social media.
        Uses pillow for image generation.

        Args:
            crystal: The crystal to export
            path: Output path (defaults to export_dir)
            compression_result: Optional compression result for honesty details

        Returns:
            Path to the generated image
        """
        # Prepare export data
        exported = self.prepare_export(crystal, compression_result)

        # Default path
        if path is None:
            filename = f"crystal_{exported.date.isoformat()}_{exported.id[:8]}.png"
            path = self._export_dir / filename

        # Try to use pillow, fall back to placeholder
        try:
            from PIL import Image, ImageDraw, ImageFont

            image = self._render_crystal_image(exported)
            image.save(path, "PNG")
            logger.info(f"Exported crystal image to {path}")
        except ImportError:
            # Pillow not available, create placeholder text file
            logger.warning("Pillow not available, creating placeholder")
            placeholder_path = path.with_suffix(".txt")
            placeholder_path.write_text(
                f"Crystal Image Placeholder\n"
                f"Date: {exported.date}\n"
                f"Content: {exported.content[:100]}...\n"
                f"Coherence: {exported.coherence_score:.0%}\n"
                f"\nInstall pillow for image export: pip install pillow"
            )
            return placeholder_path

        return path

    def _render_crystal_image(self, exported: ExportedCrystal) -> "PILImage.Image":
        """
        Render the crystal as a PIL Image.

        Design:
        - Dark background (PALETTE["background"])
        - Large date header
        - Crystal insight (main text)
        - Coherence bar
        - "Witnessed by kgents" footer
        """
        from PIL import Image, ImageDraw, ImageFont

        # Create image
        img = Image.new("RGB", (DEFAULT_WIDTH, DEFAULT_HEIGHT), PALETTE["background"])
        draw = ImageDraw.Draw(img)

        # Try to load fonts (fall back to default)
        try:
            font_large = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48
            )
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except (OSError, IOError):
            try:
                # macOS fallback
                font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
                font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
                font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            except (OSError, IOError):
                # Use default font
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()

        # Draw surface rectangle
        draw.rounded_rectangle(
            [40, 40, DEFAULT_WIDTH - 40, DEFAULT_HEIGHT - 40],
            radius=20,
            fill=PALETTE["surface"],
        )

        # Date header
        date_str = exported.date.strftime("%B %d, %Y")
        draw.text((80, 70), date_str, font=font_large, fill=PALETTE["text_primary"])

        # Crystal insight (wrap text)
        insight_text = exported.content.split("\n")[0][:150]
        if len(insight_text) == 150:
            insight_text += "..."

        # Simple text wrapping
        words = insight_text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            # Approximate width check
            if len(test_line) > 60:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        y_offset = 150
        for line in lines[:4]:  # Max 4 lines
            draw.text((80, y_offset), line, font=font_medium, fill=PALETTE["text_secondary"])
            y_offset += 40

        # Coherence bar
        bar_y = DEFAULT_HEIGHT - 180
        bar_width = DEFAULT_WIDTH - 160
        bar_height = 24

        # Background bar
        draw.rounded_rectangle(
            [80, bar_y, 80 + bar_width, bar_y + bar_height],
            radius=12,
            fill=PALETTE["primary"],
        )

        # Filled bar
        filled_width = int(bar_width * exported.coherence_score)
        if filled_width > 0:
            draw.rounded_rectangle(
                [80, bar_y, 80 + filled_width, bar_y + bar_height],
                radius=12,
                fill=PALETTE["accent"],
            )

        # Coherence label
        draw.text(
            (80, bar_y + 35),
            f"Coherence: {exported.coherence_score:.0%}",
            font=font_small,
            fill=PALETTE["text_muted"],
        )

        # Footer
        draw.text(
            (80, DEFAULT_HEIGHT - 80),
            "Witnessed by kgents",
            font=font_small,
            fill=PALETTE["text_muted"],
        )

        # Dropped count (honesty)
        if exported.dropped_count > 0:
            draw.text(
                (DEFAULT_WIDTH - 280, DEFAULT_HEIGHT - 80),
                f"({exported.dropped_count} marks compressed)",
                font=font_small,
                fill=PALETTE["text_muted"],
            )

        return img

    # =========================================================================
    # URL Export
    # =========================================================================

    async def export_as_url(
        self,
        crystal: Crystal,
        compression_result: "CompressionResult | None" = None,
    ) -> str:
        """
        Generate shareable URL for crystal.

        Note: This requires the base_url to be configured and
        assumes a hosting service is available.

        For local use, returns a data URI with base64-encoded content.

        Args:
            crystal: The crystal to export
            compression_result: Optional compression result

        Returns:
            Shareable URL string
        """
        exported = self.prepare_export(crystal, compression_result)

        if self._base_url:
            # Real URL with base
            return f"{self._base_url.rstrip('/')}/{exported.id}"

        # Generate a compact shareable hash
        content_hash = hashlib.sha256(
            f"{exported.id}{exported.content}{exported.date}".encode()
        ).hexdigest()[:12]

        # Return a local reference (would need to be served)
        return f"crystal://{content_hash}"

    # =========================================================================
    # Batch Export
    # =========================================================================

    async def export_batch(
        self,
        crystals: list[Crystal],
        format: str = "markdown",
        output_dir: Path | None = None,
    ) -> list[Path]:
        """
        Export multiple crystals.

        Args:
            crystals: List of crystals to export
            format: Export format ("markdown", "image")
            output_dir: Output directory

        Returns:
            List of paths to exported files
        """
        output_dir = output_dir or self._export_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        paths: list[Path] = []

        for crystal in crystals:
            if format == "markdown":
                content = await self.export_as_markdown(crystal)
                filename = (
                    f"crystal_{crystal.crystallized_at.date().isoformat()}_{str(crystal.id)[:8]}.md"
                )
                path = output_dir / filename
                path.write_text(content)
                paths.append(path)
            elif format == "image":
                path = await self.export_as_image(crystal)
                paths.append(path)

        return paths


# =============================================================================
# Factory Functions
# =============================================================================


_exporter: CrystalExporter | None = None


def get_crystal_exporter() -> CrystalExporter:
    """Get the singleton CrystalExporter instance."""
    global _exporter
    if _exporter is None:
        _exporter = CrystalExporter()
    return _exporter


def reset_crystal_exporter() -> None:
    """Reset the singleton (for testing)."""
    global _exporter
    _exporter = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Data types
    "ExportedCrystal",
    # Main class
    "CrystalExporter",
    # Factory
    "get_crystal_exporter",
    "reset_crystal_exporter",
    # Constants
    "DEFAULT_WIDTH",
    "DEFAULT_HEIGHT",
    "PALETTE",
    "PRINCIPLE_COLORS",
]
