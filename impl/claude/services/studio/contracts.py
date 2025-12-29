"""
Studio Contracts: Request/Response types for the Creative Production Studio.

These dataclasses define the typed contracts for AGENTESE node aspects.
Following the Phase 7 Autopoietic Architecture pattern from Brain/Witness/Foundry.

All contracts are FROZEN dataclasses: immutable after creation. This:
1. Prevents accidental mutation across layer boundaries
2. Enables safe caching (hashable keys)
3. Makes debugging easier (no spooky action at a distance)

AGENTESE: world.studio.* (manifest, archaeology, vision, production, assets, gallery)

Teaching:
    gotcha: All Request/Response types are frozen=True. This is intentional.
            If you need to modify a request, create a new one. Never use
            mutable dataclasses for cross-layer contracts.

    gotcha: The Studio has three functor domains:
            - Archaeology: excavate patterns from raw materials
            - Vision: synthesize creative direction from findings + principles
            - Production: produce assets from vision + requirements
            Each domain has its own request/response types.

Example:
    >>> request = ExcavateRequest(
    ...     sources=["/path/to/spec.md", "/path/to/code.py"],
    ...     focus="visual",
    ... )
    >>> # request.focus = "audio"  # ERROR: frozen dataclass
    >>> request.to_dict()  # Works for serialization
    {'sources': [...], 'focus': 'visual', ...}

See: spec/s-gents/studio.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

# =============================================================================
# Enums
# =============================================================================


class ArchaeologyFocus(str, Enum):
    """Focus areas for archaeological excavation."""

    VISUAL = "visual"  # Colors, shapes, composition
    AUDIO = "audio"  # Soundscapes, rhythms, tones
    NARRATIVE = "narrative"  # Themes, arcs, characters
    MECHANICAL = "mechanical"  # Interactions, feedback loops
    EMOTIONAL = "emotional"  # Feelings, moods, tensions


class AssetType(str, Enum):
    """Types of creative assets."""

    SPRITE = "sprite"  # Bitmap graphics
    ANIMATION = "animation"  # Frame sequences
    AUDIO = "audio"  # Sound files
    GRAPHICS = "graphics"  # Static visuals
    VIDEO = "video"  # Motion content
    WRITING = "writing"  # Text content
    STYLE_GUIDE = "style_guide"  # Design specifications
    VISION_DOCUMENT = "vision_document"  # Creative direction


class ExportFormat(str, Enum):
    """Export format options."""

    WEB = "web"  # Optimized for web
    MOBILE = "mobile"  # Optimized for mobile
    PRINT = "print"  # High resolution
    RAW = "raw"  # Unprocessed


# =============================================================================
# Manifest Response
# =============================================================================


@dataclass(frozen=True)
class StudioManifestResponse:
    """
    Status manifest for the Studio Crown Jewel.

    Shows studio capabilities, current phase, and active projects.
    """

    status: str  # "operational" | "degraded" | "error"
    current_phase: str  # ARCHAEOLOGY | SYNTHESIS | PRODUCTION | REVIEW | DELIVERY
    active_visions: int  # Number of active creative visions
    total_assets: int  # Total assets in registry
    gallery_size: int  # Assets in gallery
    capabilities: list[str]  # Available capabilities
    dependencies: dict[str, str]  # Dependency status (witness, brain, foundry)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": "studio_manifest",
            "status": self.status,
            "current_phase": self.current_phase,
            "active_visions": self.active_visions,
            "total_assets": self.total_assets,
            "gallery_size": self.gallery_size,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
        }

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        lines = [
            "Studio Status",
            "=============",
            f"Status: {self.status}",
            f"Current Phase: {self.current_phase}",
            f"Active Visions: {self.active_visions}",
            f"Total Assets: {self.total_assets}",
            f"Gallery Size: {self.gallery_size}",
        ]
        if self.capabilities:
            lines.append("")
            lines.append("Capabilities:")
            for cap in self.capabilities:
                lines.append(f"  - {cap}")
        return "\n".join(lines)


# =============================================================================
# Archaeology Contracts
# =============================================================================


@dataclass(frozen=True)
class ExcavateRequest:
    """
    Request to excavate patterns from source materials.

    The archaeology functor extracts creative patterns from raw materials:
    specs, code, screenshots, inspirations.
    """

    sources: tuple[str, ...]  # Paths to source materials
    focus: str = "visual"  # Focus area (visual, audio, narrative, mechanical, emotional)
    depth: str = "standard"  # "shallow" | "standard" | "deep"
    include_provenance: bool = True  # Track where patterns came from

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "sources": list(self.sources),
            "focus": self.focus,
            "depth": self.depth,
            "include_provenance": self.include_provenance,
        }


@dataclass(frozen=True)
class Pattern:
    """A pattern extracted from source material."""

    name: str
    category: str  # color, shape, rhythm, theme, etc.
    description: str
    source_refs: tuple[str, ...]  # References to source materials
    confidence: float  # 0.0-1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "source_refs": list(self.source_refs),
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class ArchaeologicalFindings:
    """
    Response from archaeological excavation.

    Contains extracted patterns and provenance graph.
    """

    patterns: tuple[Pattern, ...]
    provenance: dict[str, Any]  # Graph linking patterns to sources
    focus: str
    source_count: int
    excavation_timestamp: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": "archaeological_findings",
            "patterns": [p.to_dict() for p in self.patterns],
            "provenance": self.provenance,
            "focus": self.focus,
            "source_count": self.source_count,
            "excavation_timestamp": self.excavation_timestamp,
        }

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        lines = [
            f"Archaeological Findings ({self.focus})",
            "=" * (25 + len(self.focus)),
            f"Sources: {self.source_count}",
            f"Patterns Found: {len(self.patterns)}",
            "",
        ]
        for i, p in enumerate(self.patterns[:10], 1):
            lines.append(f"{i}. [{p.category}] {p.name}: {p.description[:60]}...")
        if len(self.patterns) > 10:
            lines.append(f"... and {len(self.patterns) - 10} more")
        return "\n".join(lines)


# =============================================================================
# Vision Contracts
# =============================================================================


@dataclass(frozen=True)
class DesignPrinciple:
    """A design principle to guide vision synthesis."""

    name: str
    description: str
    priority: int = 1  # 1-5, higher is more important

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
        }


@dataclass(frozen=True)
class SynthesizeRequest:
    """
    Request to synthesize creative vision from findings + principles.

    The vision functor transforms archaeological findings into actionable
    creative direction by applying design principles.
    """

    findings_id: str  # Reference to archaeological findings
    principles: tuple[DesignPrinciple, ...] = ()  # Design principles to apply
    target_domain: str = "general"  # Domain context (game, web, mobile, etc.)
    style_hints: tuple[str, ...] = ()  # Optional style direction hints

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "findings_id": self.findings_id,
            "principles": [p.to_dict() for p in self.principles],
            "target_domain": self.target_domain,
            "style_hints": list(self.style_hints),
        }


@dataclass(frozen=True)
class ColorPalette:
    """Color palette specification."""

    primary: str  # Hex color
    secondary: str
    accent: str
    background: str
    foreground: str
    semantic: dict[str, str] = field(default_factory=dict)  # e.g., {"success": "#00ff00"}

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "background": self.background,
            "foreground": self.foreground,
            "semantic": self.semantic,
        }


@dataclass(frozen=True)
class TypographySpec:
    """Typography specification."""

    heading_font: str
    body_font: str
    mono_font: str
    base_size: int  # in pixels
    scale_ratio: float  # e.g., 1.25 for major third

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "heading_font": self.heading_font,
            "body_font": self.body_font,
            "mono_font": self.mono_font,
            "base_size": self.base_size,
            "scale_ratio": self.scale_ratio,
        }


@dataclass(frozen=True)
class MotionSpec:
    """Motion/animation specification."""

    timing_function: str  # e.g., "ease-out", "spring"
    duration_unit: int  # base duration in ms
    stagger_delay: int  # delay between staggered animations

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "timing_function": self.timing_function,
            "duration_unit": self.duration_unit,
            "stagger_delay": self.stagger_delay,
        }


@dataclass(frozen=True)
class CreativeVision:
    """
    Response from vision synthesis.

    The creative vision is the unified direction for all assets.
    """

    vision_id: str
    core_insight: str  # The central creative idea
    color_palette: ColorPalette
    typography: TypographySpec
    motion: MotionSpec
    tone_of_voice: str  # Description of brand voice
    style_keywords: tuple[str, ...]  # Keywords describing the style
    synthesis_timestamp: str
    findings_ref: str  # Reference to source findings

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": "creative_vision",
            "vision_id": self.vision_id,
            "core_insight": self.core_insight,
            "color_palette": self.color_palette.to_dict(),
            "typography": self.typography.to_dict(),
            "motion": self.motion.to_dict(),
            "tone_of_voice": self.tone_of_voice,
            "style_keywords": list(self.style_keywords),
            "synthesis_timestamp": self.synthesis_timestamp,
            "findings_ref": self.findings_ref,
        }

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        lines = [
            "Creative Vision",
            "===============",
            f"ID: {self.vision_id}",
            "",
            f"Core Insight: {self.core_insight}",
            "",
            f"Style: {', '.join(self.style_keywords)}",
            "",
            f"Colors: {self.color_palette.primary} (primary)",
            f"Typography: {self.typography.heading_font}",
            f"Motion: {self.motion.timing_function}",
        ]
        return "\n".join(lines)


# =============================================================================
# Production Contracts
# =============================================================================


@dataclass(frozen=True)
class ProduceRequest:
    """
    Request to produce an asset from vision + requirement.

    The production functor creates concrete assets that embody the vision.
    """

    vision_id: str  # Reference to creative vision
    asset_type: str  # sprite, animation, audio, etc.
    name: str  # Asset name
    description: str  # What the asset should represent
    dimensions: tuple[int, int] | None = None  # Width x Height for visual assets
    duration_ms: int | None = None  # Duration for audio/animation
    style_overrides: dict[str, Any] = field(default_factory=dict)  # Local style overrides

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "vision_id": self.vision_id,
            "asset_type": self.asset_type,
            "name": self.name,
            "description": self.description,
            "dimensions": list(self.dimensions) if self.dimensions else None,
            "duration_ms": self.duration_ms,
            "style_overrides": self.style_overrides,
        }


@dataclass(frozen=True)
class Asset:
    """
    Response from asset production.

    A produced creative asset with metadata.
    """

    asset_id: str
    name: str
    asset_type: str
    description: str
    vision_id: str  # Reference to source vision
    file_path: str | None  # Path to produced file (if applicable)
    content: str | None  # Inline content (for text/small assets)
    metadata: dict[str, Any]  # Type-specific metadata
    quality_score: float  # 0.0-1.0
    production_timestamp: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": "asset",
            "asset_id": self.asset_id,
            "name": self.name,
            "asset_type": self.asset_type,
            "description": self.description,
            "vision_id": self.vision_id,
            "file_path": self.file_path,
            "content": self.content,
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "production_timestamp": self.production_timestamp,
        }

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        lines = [
            f"Asset: {self.name}",
            "=" * (7 + len(self.name)),
            f"ID: {self.asset_id}",
            f"Type: {self.asset_type}",
            f"Quality: {self.quality_score:.0%}",
        ]
        if self.file_path:
            lines.append(f"File: {self.file_path}")
        return "\n".join(lines)


# =============================================================================
# Export Contracts
# =============================================================================


@dataclass(frozen=True)
class ExportRequest:
    """
    Request to export an asset to a specific format.

    Export operations render assets for delivery.
    """

    asset_id: str  # Reference to asset
    format: str = "web"  # web, mobile, print, raw
    optimization: str = "standard"  # none, standard, aggressive
    output_path: str | None = None  # Optional output path override

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "asset_id": self.asset_id,
            "format": self.format,
            "optimization": self.optimization,
            "output_path": self.output_path,
        }


@dataclass(frozen=True)
class ExportedAsset:
    """
    Response from asset export.

    Contains the exported file path and metadata.
    """

    asset_id: str
    export_id: str
    format: str
    file_path: str
    file_size_bytes: int
    optimization_applied: str
    export_timestamp: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": "exported_asset",
            "asset_id": self.asset_id,
            "export_id": self.export_id,
            "format": self.format,
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "optimization_applied": self.optimization_applied,
            "export_timestamp": self.export_timestamp,
        }

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        size_kb = self.file_size_bytes / 1024
        lines = [
            f"Exported: {self.file_path}",
            f"Format: {self.format}",
            f"Size: {size_kb:.1f} KB",
            f"Optimization: {self.optimization_applied}",
        ]
        return "\n".join(lines)


# =============================================================================
# Gallery Contracts
# =============================================================================


@dataclass(frozen=True)
class PlaceRequest:
    """
    Request to place an asset in the gallery.

    Gallery placement makes assets visible for showcase.
    """

    asset_id: str  # Reference to asset
    category: str = "general"  # Gallery category
    featured: bool = False  # Whether to feature prominently
    tags: tuple[str, ...] = ()  # Tags for discovery

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "asset_id": self.asset_id,
            "category": self.category,
            "featured": self.featured,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class GalleryPlacement:
    """
    Response from gallery placement.

    Confirmation of asset placement in gallery.
    """

    placement_id: str
    asset_id: str
    category: str
    featured: bool
    gallery_url: str | None  # URL to view in gallery
    placement_timestamp: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": "gallery_placement",
            "placement_id": self.placement_id,
            "asset_id": self.asset_id,
            "category": self.category,
            "featured": self.featured,
            "gallery_url": self.gallery_url,
            "placement_timestamp": self.placement_timestamp,
        }

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        lines = [
            f"Gallery Placement: {self.placement_id}",
            f"Asset: {self.asset_id}",
            f"Category: {self.category}",
            f"Featured: {'Yes' if self.featured else 'No'}",
        ]
        if self.gallery_url:
            lines.append(f"URL: {self.gallery_url}")
        return "\n".join(lines)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "ArchaeologyFocus",
    "AssetType",
    "ExportFormat",
    # Manifest
    "StudioManifestResponse",
    # Archaeology
    "ExcavateRequest",
    "Pattern",
    "ArchaeologicalFindings",
    # Vision
    "DesignPrinciple",
    "SynthesizeRequest",
    "ColorPalette",
    "TypographySpec",
    "MotionSpec",
    "CreativeVision",
    # Production
    "ProduceRequest",
    "Asset",
    # Export
    "ExportRequest",
    "ExportedAsset",
    # Gallery
    "PlaceRequest",
    "GalleryPlacement",
]
