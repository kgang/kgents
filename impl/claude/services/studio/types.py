"""
S-gent Studio Types and Contracts.

Types for the Creative Production Studio — the two-functor pipeline that
transforms raw materials into creative and art assets.

Pipeline:
    f(Principles, Archaeology) -> (Vision, Strategy)
    f(Vision | Strategy) -> (Creative Assets | Art Assets)

The Three Functors:
    1. AestheticArchaeologyFunctor: Extract patterns from raw materials
    2. VisionSynthesisFunctor: Generate creative vision from findings + principles
    3. AssetProductionFunctor: Create assets from vision + requirements

Quality: Measured via Tetrad (Contrast, Arc, Voice, Floor) instantiated for
         creative domain (expression, consistency, surprise, provenance).

Philosophy:
    "Art is not what you see, but what you make others see." — Degas

    All contracts are FROZEN dataclasses — immutable after creation. This:
    1. Prevents accidental mutation across layer boundaries
    2. Enables safe caching (hashable keys)
    3. Makes debugging easier (no spooky action at a distance)

AGENTESE: world.studio.* (archaeology, vision, production, assets, gallery)

See: spec/s-gents/studio.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

# =============================================================================
# Source Types
# =============================================================================


class SourceType(Enum):
    """Type of source material for archaeology."""

    SPEC = "spec"  # Specification documents
    CODE = "code"  # Source code
    SCREENSHOT = "screenshot"  # Visual captures
    INSPIRATION = "inspiration"  # Reference materials
    ASSET = "asset"  # Existing assets
    AUDIO = "audio"  # Sound files
    VIDEO = "video"  # Video files
    TEXT = "text"  # Text documents


@dataclass(frozen=True)
class Source:
    """
    A source material for archaeological extraction.

    Sources are the raw materials that feed into the archaeology functor.
    Each source has a path, type, and optional cached content.
    """

    path: str  # Path to the source (file path or URL)
    type: SourceType  # Type of source material
    content: str | None = None  # Cached content (loaded lazily)
    metadata: dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "path": self.path,
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Source:
        """Create from dictionary."""
        return cls(
            path=data.get("path", ""),
            type=SourceType(data.get("type", "text")),
            content=data.get("content"),
            metadata=data.get("metadata", {}),
        )


class ArchaeologyFocus(Enum):
    """
    Focus type for archaeological extraction.

    Each focus emphasizes a different aspect of the source material.
    """

    VISUAL = "visual"  # Colors, shapes, composition
    AUDIO = "audio"  # Soundscapes, rhythms, tones
    NARRATIVE = "narrative"  # Themes, arcs, characters
    MECHANICAL = "mechanical"  # Interactions, feedback loops
    EMOTIONAL = "emotional"  # Feelings, moods, tensions


class InterpretationLens(Enum):
    """
    Lens for interpreting archaeological findings.

    Different lenses assign different meanings to patterns.
    """

    SEMIOTIC = "semiotic"  # Signs, symbols, signifiers
    AESTHETIC = "aesthetic"  # Beauty, taste, style
    FUNCTIONAL = "functional"  # Purpose, utility, flow
    EMOTIONAL = "emotional"  # Affect, resonance, impact


# =============================================================================
# Findings Types
# =============================================================================


@dataclass(frozen=True)
class Pattern:
    """
    A pattern extracted during archaeological excavation.

    Patterns are the atomic units of archaeological findings.
    They have a name, description, source references, and confidence.
    """

    name: str  # Pattern identifier
    description: str  # What this pattern represents
    source_refs: tuple[str, ...] = ()  # References to source materials
    confidence: float = 1.0  # Confidence in extraction [0, 1]
    focus: ArchaeologyFocus | None = None  # Which focus revealed this
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate confidence is in [0, 1]."""
        if not 0.0 <= self.confidence <= 1.0:
            object.__setattr__(self, "confidence", max(0.0, min(1.0, self.confidence)))

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "name": self.name,
            "description": self.description,
            "source_refs": list(self.source_refs),
            "confidence": self.confidence,
            "focus": self.focus.value if self.focus else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Pattern:
        """Create from dictionary."""
        focus = ArchaeologyFocus(data["focus"]) if data.get("focus") else None
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            source_refs=tuple(data.get("source_refs", [])),
            confidence=data.get("confidence", 1.0),
            focus=focus,
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class ProvenanceNode:
    """A node in the provenance graph linking patterns to sources."""

    pattern_name: str
    source_path: str
    location: str | None = None  # Line number, timestamp, etc.
    extraction_method: str = "manual"

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "pattern_name": self.pattern_name,
            "source_path": self.source_path,
            "location": self.location,
            "extraction_method": self.extraction_method,
        }


@dataclass(frozen=True)
class ArchaeologicalFindings:
    """
    Results from archaeological excavation.

    Contains extracted patterns and their provenance graph.
    """

    patterns: tuple[Pattern, ...] = ()
    provenance: tuple[ProvenanceNode, ...] = ()
    sources_analyzed: int = 0
    focus_used: ArchaeologyFocus | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "patterns": [p.to_dict() for p in self.patterns],
            "provenance": [n.to_dict() for n in self.provenance],
            "sources_analyzed": self.sources_analyzed,
            "focus_used": self.focus_used.value if self.focus_used else None,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArchaeologicalFindings:
        """Create from dictionary."""
        focus = ArchaeologyFocus(data["focus_used"]) if data.get("focus_used") else None
        return cls(
            patterns=tuple(Pattern.from_dict(p) for p in data.get("patterns", [])),
            provenance=tuple(ProvenanceNode(**n) for n in data.get("provenance", [])),
            sources_analyzed=data.get("sources_analyzed", 0),
            focus_used=focus,
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(),
        )

    @classmethod
    def empty(cls) -> ArchaeologicalFindings:
        """Return empty findings."""
        return cls()


@dataclass(frozen=True)
class Interpretation:
    """A single interpretation of findings through a lens."""

    pattern_name: str
    meaning: str
    lens: InterpretationLens
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "pattern_name": self.pattern_name,
            "meaning": self.meaning,
            "lens": self.lens.value,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class InterpretedMeaning:
    """
    Findings with assigned meanings through an interpretation lens.
    """

    findings: ArchaeologicalFindings
    lens: InterpretationLens
    interpretations: tuple[Interpretation, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "findings": self.findings.to_dict(),
            "lens": self.lens.value,
            "interpretations": [i.to_dict() for i in self.interpretations],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InterpretedMeaning:
        """Create from dictionary."""
        return cls(
            findings=ArchaeologicalFindings.from_dict(data.get("findings", {})),
            lens=InterpretationLens(data.get("lens", "aesthetic")),
            interpretations=tuple(
                Interpretation(
                    pattern_name=i["pattern_name"],
                    meaning=i["meaning"],
                    lens=InterpretationLens(i["lens"]),
                    confidence=i.get("confidence", 1.0),
                )
                for i in data.get("interpretations", [])
            ),
        )


# =============================================================================
# Vision Types
# =============================================================================


@dataclass(frozen=True)
class ColorPalette:
    """
    Color palette specification for a creative vision.

    Contains primary, secondary, accent colors and semantic mappings.
    """

    primary: str  # Primary color (hex)
    secondary: str  # Secondary color (hex)
    accent: str  # Accent color (hex)
    semantic: dict[str, str] = field(default_factory=dict)  # e.g., {"danger": "#ff0000"}
    background: str = "#ffffff"
    foreground: str = "#000000"

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "semantic": self.semantic,
            "background": self.background,
            "foreground": self.foreground,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ColorPalette:
        """Create from dictionary."""
        return cls(
            primary=data.get("primary", "#000000"),
            secondary=data.get("secondary", "#666666"),
            accent=data.get("accent", "#0066cc"),
            semantic=data.get("semantic", {}),
            background=data.get("background", "#ffffff"),
            foreground=data.get("foreground", "#000000"),
        )

    @classmethod
    def default(cls) -> ColorPalette:
        """Return a default palette."""
        return cls(
            primary="#1a1a2e",
            secondary="#16213e",
            accent="#0f3460",
        )


@dataclass(frozen=True)
class TypographySpec:
    """
    Typography specification for a creative vision.
    """

    heading_font: str  # Font family for headings
    body_font: str  # Font family for body text
    mono_font: str  # Font family for code/monospace
    scale: float = 1.25  # Type scale ratio (e.g., 1.25 = major third)
    base_size: int = 16  # Base font size in pixels

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "heading_font": self.heading_font,
            "body_font": self.body_font,
            "mono_font": self.mono_font,
            "scale": self.scale,
            "base_size": self.base_size,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TypographySpec:
        """Create from dictionary."""
        return cls(
            heading_font=data.get("heading_font", "Inter"),
            body_font=data.get("body_font", "Inter"),
            mono_font=data.get("mono_font", "JetBrains Mono"),
            scale=data.get("scale", 1.25),
            base_size=data.get("base_size", 16),
        )

    @classmethod
    def default(cls) -> TypographySpec:
        """Return default typography."""
        return cls(
            heading_font="Inter",
            body_font="Inter",
            mono_font="JetBrains Mono",
        )


@dataclass(frozen=True)
class MotionSpec:
    """
    Motion specification for a creative vision.

    Defines timing functions, duration scales, and easing.
    """

    timing_function: str  # CSS timing function or named preset
    duration_scale: float = 1.0  # Multiplier for all durations
    easing: str = "ease-out"  # Default easing
    entrance_duration_ms: int = 200
    exit_duration_ms: int = 150
    emphasis_duration_ms: int = 300

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "timing_function": self.timing_function,
            "duration_scale": self.duration_scale,
            "easing": self.easing,
            "entrance_duration_ms": self.entrance_duration_ms,
            "exit_duration_ms": self.exit_duration_ms,
            "emphasis_duration_ms": self.emphasis_duration_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MotionSpec:
        """Create from dictionary."""
        return cls(
            timing_function=data.get("timing_function", "ease-out"),
            duration_scale=data.get("duration_scale", 1.0),
            easing=data.get("easing", "ease-out"),
            entrance_duration_ms=data.get("entrance_duration_ms", 200),
            exit_duration_ms=data.get("exit_duration_ms", 150),
            emphasis_duration_ms=data.get("emphasis_duration_ms", 300),
        )

    @classmethod
    def default(cls) -> MotionSpec:
        """Return default motion spec."""
        return cls(timing_function="ease-out")


@dataclass(frozen=True)
class ToneSpec:
    """
    Tone of voice specification for a creative vision.
    """

    voice: str  # Overall voice description
    personality: str  # Personality traits
    keywords: tuple[str, ...] = ()  # Key descriptive words
    avoid: tuple[str, ...] = ()  # Words/tones to avoid

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "voice": self.voice,
            "personality": self.personality,
            "keywords": list(self.keywords),
            "avoid": list(self.avoid),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToneSpec:
        """Create from dictionary."""
        return cls(
            voice=data.get("voice", ""),
            personality=data.get("personality", ""),
            keywords=tuple(data.get("keywords", [])),
            avoid=tuple(data.get("avoid", [])),
        )

    @classmethod
    def default(cls) -> ToneSpec:
        """Return default tone."""
        return cls(
            voice="Professional yet approachable",
            personality="Confident, helpful, clear",
        )


@dataclass(frozen=True)
class IconographySpec:
    """Iconography specification for a creative vision."""

    style: str  # "outlined", "filled", "dual-tone"
    stroke_width: float = 2.0
    corner_radius: float = 0.0
    grid_size: int = 24

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "style": self.style,
            "stroke_width": self.stroke_width,
            "corner_radius": self.corner_radius,
            "grid_size": self.grid_size,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IconographySpec:
        """Create from dictionary."""
        return cls(
            style=data.get("style", "outlined"),
            stroke_width=data.get("stroke_width", 2.0),
            corner_radius=data.get("corner_radius", 0.0),
            grid_size=data.get("grid_size", 24),
        )

    @classmethod
    def default(cls) -> IconographySpec:
        """Return default iconography."""
        return cls(style="outlined")


@dataclass(frozen=True)
class CreativeVision:
    """
    The core creative vision synthesized from archaeological findings.

    This is the output of the VisionSynthesisFunctor and serves as
    input to both StyleGuide generation and AssetProduction.
    """

    core_insight: str  # The central creative insight
    color_palette: ColorPalette
    typography: TypographySpec
    motion: MotionSpec
    tone: ToneSpec
    iconography: IconographySpec | None = None
    principles: tuple[str, ...] = ()  # Design principles applied
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "core_insight": self.core_insight,
            "color_palette": self.color_palette.to_dict(),
            "typography": self.typography.to_dict(),
            "motion": self.motion.to_dict(),
            "tone": self.tone.to_dict(),
            "iconography": self.iconography.to_dict() if self.iconography else None,
            "principles": list(self.principles),
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreativeVision:
        """Create from dictionary."""
        return cls(
            core_insight=data.get("core_insight", ""),
            color_palette=ColorPalette.from_dict(data.get("color_palette", {})),
            typography=TypographySpec.from_dict(data.get("typography", {})),
            motion=MotionSpec.from_dict(data.get("motion", {})),
            tone=ToneSpec.from_dict(data.get("tone", {})),
            iconography=IconographySpec.from_dict(data["iconography"])
            if data.get("iconography")
            else None,
            principles=tuple(data.get("principles", [])),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(),
        )

    def to_style_guide(self) -> StyleGuide:
        """Convert vision to a style guide."""
        return StyleGuide(
            vision=self,
            rules=(),
            examples=(),
        )


@dataclass(frozen=True)
class StyleRule:
    """A single rule in a style guide."""

    category: str  # "color", "typography", "motion", "tone"
    rule: str  # The rule statement
    rationale: str = ""  # Why this rule exists

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "category": self.category,
            "rule": self.rule,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class StyleExample:
    """An example demonstrating style guide usage."""

    title: str
    description: str
    do_example: str  # What to do
    dont_example: str = ""  # What not to do

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "title": self.title,
            "description": self.description,
            "do_example": self.do_example,
            "dont_example": self.dont_example,
        }


@dataclass(frozen=True)
class StyleGuide:
    """
    A concrete style guide derived from a creative vision.

    Contains actionable rules and examples for implementing the vision.
    """

    vision: CreativeVision
    rules: tuple[StyleRule, ...] = ()
    examples: tuple[StyleExample, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "vision": self.vision.to_dict(),
            "rules": [r.to_dict() for r in self.rules],
            "examples": [e.to_dict() for e in self.examples],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StyleGuide:
        """Create from dictionary."""
        return cls(
            vision=CreativeVision.from_dict(data.get("vision", {})),
            rules=tuple(StyleRule(**r) for r in data.get("rules", [])),
            examples=tuple(StyleExample(**e) for e in data.get("examples", [])),
        )


@dataclass(frozen=True)
class BrandIdentity:
    """
    Complete brand identity derived from creative vision.
    """

    name: str  # Brand name
    tagline: str  # Brand tagline
    colors: tuple[str, ...]  # Brand colors (hex)
    fonts: tuple[str, ...]  # Brand fonts
    voice: str  # Brand voice description
    personality: str  # Brand personality
    values: tuple[str, ...] = ()  # Brand values
    logo_guidelines: str = ""  # Logo usage guidelines

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "name": self.name,
            "tagline": self.tagline,
            "colors": list(self.colors),
            "fonts": list(self.fonts),
            "voice": self.voice,
            "personality": self.personality,
            "values": list(self.values),
            "logo_guidelines": self.logo_guidelines,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BrandIdentity:
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            tagline=data.get("tagline", ""),
            colors=tuple(data.get("colors", [])),
            fonts=tuple(data.get("fonts", [])),
            voice=data.get("voice", ""),
            personality=data.get("personality", ""),
            values=tuple(data.get("values", [])),
            logo_guidelines=data.get("logo_guidelines", ""),
        )


# =============================================================================
# Asset Types
# =============================================================================


class AssetType(Enum):
    """Type of creative asset."""

    SPRITE = "sprite"  # Bitmap graphics (PNG, etc.)
    ANIMATION = "animation"  # Animation data (frames, sequences)
    AUDIO = "audio"  # Sound files (OGG, MP3)
    GRAPHIC = "graphic"  # Static visuals (UI elements, icons)
    VIDEO = "video"  # Motion content (MP4, WebM)
    WRITING = "writing"  # Text content (Markdown, JSON)


@dataclass(frozen=True)
class AssetSpec:
    """Technical specifications for an asset."""

    format: str  # File format
    dimensions: tuple[int, int] | None = None  # Width, height (for visual assets)
    fps: int | None = None  # Frames per second (for animations/video)
    sample_rate: int | None = None  # Sample rate (for audio)
    bit_depth: int | None = None  # Bit depth (for audio)
    lufs: float | None = None  # Target loudness (for audio)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "format": self.format,
            "dimensions": list(self.dimensions) if self.dimensions else None,
            "fps": self.fps,
            "sample_rate": self.sample_rate,
            "bit_depth": self.bit_depth,
            "lufs": self.lufs,
        }


@dataclass(frozen=True)
class AssetConstraint:
    """A constraint on asset creation."""

    name: str
    description: str
    value: str | int | float | bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value,
        }


@dataclass(frozen=True)
class AssetRequirement:
    """
    A requirement for asset production.

    Specifies what asset needs to be created, with technical specs and constraints.
    """

    type: AssetType  # Type of asset
    name: str  # Asset name/identifier
    description: str  # What this asset is for
    specs: AssetSpec  # Technical specifications
    constraints: tuple[AssetConstraint, ...] = ()  # Production constraints
    priority: int = 1  # Priority (1 = highest)
    tags: tuple[str, ...] = ()  # Tags for categorization

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "specs": self.specs.to_dict(),
            "constraints": [c.to_dict() for c in self.constraints],
            "priority": self.priority,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AssetRequirement:
        """Create from dictionary."""
        return cls(
            type=AssetType(data.get("type", "graphic")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            specs=AssetSpec(**data.get("specs", {"format": "png"})),
            constraints=tuple(AssetConstraint(**c) for c in data.get("constraints", [])),
            priority=data.get("priority", 1),
            tags=tuple(data.get("tags", [])),
        )


@dataclass(frozen=True)
class Asset:
    """
    A produced creative asset.

    Output of the AssetProductionFunctor.
    """

    id: str  # Unique identifier
    type: AssetType  # Type of asset
    name: str  # Asset name
    content: bytes | str | None = None  # Asset content (binary or text)
    content_path: str | None = None  # Path to asset file (if not inline)
    metadata: dict[str, Any] = field(default_factory=dict)  # Asset metadata
    quality_score: float = 1.0  # Quality score from Tetrad [0, 1]
    provenance: tuple[str, ...] = ()  # Pattern names this asset embodies
    created_at: datetime = field(default_factory=datetime.now)
    requirement_name: str | None = None  # Requirement this fulfills

    def __post_init__(self) -> None:
        """Validate quality score."""
        if not 0.0 <= self.quality_score <= 1.0:
            object.__setattr__(self, "quality_score", max(0.0, min(1.0, self.quality_score)))

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "content_path": self.content_path,
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "provenance": list(self.provenance),
            "created_at": self.created_at.isoformat(),
            "requirement_name": self.requirement_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Asset:
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            type=AssetType(data.get("type", "graphic")),
            name=data.get("name", ""),
            content_path=data.get("content_path"),
            metadata=data.get("metadata", {}),
            quality_score=data.get("quality_score", 1.0),
            provenance=tuple(data.get("provenance", [])),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
            requirement_name=data.get("requirement_name"),
        )


class ExportFormat(Enum):
    """Format for asset export."""

    WEB = "web"  # Optimized for web (compressed, lazy-loadable)
    MOBILE = "mobile"  # Optimized for mobile (smaller sizes)
    PRINT = "print"  # High resolution for print
    RAW = "raw"  # Uncompressed original


@dataclass(frozen=True)
class ExportedAsset:
    """
    An asset exported to a specific format.
    """

    asset: Asset  # Original asset
    format: ExportFormat  # Export format used
    path: str  # Path to exported file
    size_bytes: int  # File size in bytes
    optimization_applied: tuple[str, ...] = ()  # What optimizations were done

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "asset": self.asset.to_dict(),
            "format": self.format.value,
            "path": self.path,
            "size_bytes": self.size_bytes,
            "optimization_applied": list(self.optimization_applied),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExportedAsset:
        """Create from dictionary."""
        return cls(
            asset=Asset.from_dict(data.get("asset", {})),
            format=ExportFormat(data.get("format", "web")),
            path=data.get("path", ""),
            size_bytes=data.get("size_bytes", 0),
            optimization_applied=tuple(data.get("optimization_applied", [])),
        )


# =============================================================================
# Request/Response Contracts
# =============================================================================


@dataclass(frozen=True)
class ExcavateRequest:
    """
    Request to excavate patterns from sources.

    Input to AestheticArchaeologyFunctor.excavate()
    """

    sources: tuple[Source, ...]  # Sources to analyze
    focus: ArchaeologyFocus  # What to focus on
    depth: str = "standard"  # "quick", "standard", "deep"

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "sources": [s.to_dict() for s in self.sources],
            "focus": self.focus.value,
            "depth": self.depth,
        }


@dataclass(frozen=True)
class InterpretRequest:
    """Request to interpret archaeological findings."""

    findings: ArchaeologicalFindings
    lens: InterpretationLens

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "findings": self.findings.to_dict(),
            "lens": self.lens.value,
        }


@dataclass(frozen=True)
class DesignPrinciple:
    """A design principle for vision synthesis."""

    statement: str
    rationale: str = ""
    priority: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "statement": self.statement,
            "rationale": self.rationale,
            "priority": self.priority,
        }


@dataclass(frozen=True)
class SynthesizeRequest:
    """
    Request to synthesize creative vision from findings and principles.

    Input to VisionSynthesisFunctor.synthesize()
    """

    findings: ArchaeologicalFindings
    principles: tuple[DesignPrinciple, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "findings": self.findings.to_dict(),
            "principles": [p.to_dict() for p in self.principles],
        }


@dataclass(frozen=True)
class ProduceRequest:
    """
    Request to produce an asset from vision and requirement.

    Input to AssetProductionFunctor.produce()
    """

    vision: CreativeVision
    requirement: AssetRequirement

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "vision": self.vision.to_dict(),
            "requirement": self.requirement.to_dict(),
        }


@dataclass(frozen=True)
class Feedback:
    """Feedback for asset refinement."""

    asset_id: str
    type: str  # "correction", "enhancement", "rejection"
    description: str
    specifics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "asset_id": self.asset_id,
            "type": self.type,
            "description": self.description,
            "specifics": self.specifics,
        }


@dataclass(frozen=True)
class RefineRequest:
    """
    Request to refine an asset with feedback.

    Input to AssetProductionFunctor.refine()
    """

    asset: Asset
    feedback: Feedback

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "asset": self.asset.to_dict(),
            "feedback": self.feedback.to_dict(),
        }


@dataclass(frozen=True)
class ExportRequest:
    """
    Request to export an asset to a format.
    """

    asset: Asset
    format: ExportFormat
    output_path: str | None = None  # Desired output path (optional)
    optimization: str = "standard"  # "none", "standard", "aggressive"

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "asset": self.asset.to_dict(),
            "format": self.format.value,
            "output_path": self.output_path,
            "optimization": self.optimization,
        }


# =============================================================================
# Gallery Types
# =============================================================================


@dataclass(frozen=True)
class GalleryPlacement:
    """
    Placement of an asset in the gallery.
    """

    asset_id: str
    section: str  # "featured", "sprites", "audio", etc.
    position: int = 0  # Order within section
    caption: str = ""
    tags: tuple[str, ...] = ()
    placed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "asset_id": self.asset_id,
            "section": self.section,
            "position": self.position,
            "caption": self.caption,
            "tags": list(self.tags),
            "placed_at": self.placed_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GalleryPlacement:
        """Create from dictionary."""
        return cls(
            asset_id=data.get("asset_id", ""),
            section=data.get("section", ""),
            position=data.get("position", 0),
            caption=data.get("caption", ""),
            tags=tuple(data.get("tags", [])),
            placed_at=datetime.fromisoformat(data["placed_at"])
            if "placed_at" in data
            else datetime.now(),
        )


@dataclass(frozen=True)
class PlaceRequest:
    """Request to place an asset in the gallery."""

    asset: Asset
    section: str
    position: int | None = None
    caption: str = ""
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "asset": self.asset.to_dict(),
            "section": self.section,
            "position": self.position,
            "caption": self.caption,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class GalleryManifest:
    """
    Complete gallery manifest.
    """

    sections: tuple[str, ...]  # Available sections
    placements: tuple[GalleryPlacement, ...]  # All placements
    total_assets: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "sections": list(self.sections),
            "placements": [p.to_dict() for p in self.placements],
            "total_assets": self.total_assets,
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GalleryManifest:
        """Create from dictionary."""
        return cls(
            sections=tuple(data.get("sections", [])),
            placements=tuple(GalleryPlacement.from_dict(p) for p in data.get("placements", [])),
            total_assets=data.get("total_assets", 0),
            last_updated=datetime.fromisoformat(data["last_updated"])
            if "last_updated" in data
            else datetime.now(),
        )

    @classmethod
    def empty(cls) -> GalleryManifest:
        """Return an empty gallery."""
        return cls(
            sections=("featured", "sprites", "animations", "audio", "graphics", "writing"),
            placements=(),
            total_assets=0,
        )


# =============================================================================
# Studio Manifest Response
# =============================================================================


@dataclass(frozen=True)
class StudioManifestResponse:
    """
    Status manifest for the Studio Crown Jewel.

    Returned by world.studio.manifest AGENTESE path.
    """

    status: str  # "operational", "degraded", "error"
    phase: str  # Current studio phase
    vision_loaded: bool  # Is there an active vision?
    assets_count: int  # Number of produced assets
    pending_requirements: int  # Requirements not yet fulfilled
    gallery_sections: tuple[str, ...]  # Available gallery sections
    recent_activity: tuple[dict[str, Any], ...]  # Recent operations

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": "studio_manifest",
            "status": self.status,
            "phase": self.phase,
            "vision_loaded": self.vision_loaded,
            "assets_count": self.assets_count,
            "pending_requirements": self.pending_requirements,
            "gallery_sections": list(self.gallery_sections),
            "recent_activity": list(self.recent_activity),
        }

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        lines = [
            "Studio Status",
            "=============",
            f"Status: {self.status}",
            f"Phase: {self.phase}",
            f"Vision Loaded: {'Yes' if self.vision_loaded else 'No'}",
            f"Assets: {self.assets_count}",
            f"Pending Requirements: {self.pending_requirements}",
            f"Gallery Sections: {', '.join(self.gallery_sections)}",
        ]
        if self.recent_activity:
            lines.append("")
            lines.append("Recent Activity:")
            for activity in self.recent_activity[:5]:
                action = activity.get("action", "?")
                target = activity.get("target", "?")
                lines.append(f"  - {action}: {target}")
        return "\n".join(lines)


# =============================================================================
# Studio Phase (for Polynomial)
# =============================================================================


class StudioPhase(Enum):
    """
    Phases of the Studio polynomial state machine.
    """

    ARCHAEOLOGY = auto()  # Excavating raw materials, extracting patterns
    SYNTHESIS = auto()  # Generating creative vision, style guide
    PRODUCTION = auto()  # Creating assets (sprites, audio, etc.)
    REVIEW = auto()  # Quality assurance, iteration
    DELIVERY = auto()  # Export, handoff, gallery placement


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Source types
    "SourceType",
    "Source",
    "ArchaeologyFocus",
    "InterpretationLens",
    # Findings types
    "Pattern",
    "ProvenanceNode",
    "ArchaeologicalFindings",
    "Interpretation",
    "InterpretedMeaning",
    # Vision types
    "ColorPalette",
    "TypographySpec",
    "MotionSpec",
    "ToneSpec",
    "IconographySpec",
    "CreativeVision",
    "StyleRule",
    "StyleExample",
    "StyleGuide",
    "BrandIdentity",
    # Asset types
    "AssetType",
    "AssetSpec",
    "AssetConstraint",
    "AssetRequirement",
    "Asset",
    "ExportFormat",
    "ExportedAsset",
    # Request/Response contracts
    "ExcavateRequest",
    "InterpretRequest",
    "DesignPrinciple",
    "SynthesizeRequest",
    "ProduceRequest",
    "Feedback",
    "RefineRequest",
    "ExportRequest",
    # Gallery types
    "GalleryPlacement",
    "PlaceRequest",
    "GalleryManifest",
    # Manifest
    "StudioManifestResponse",
    # Phase enum
    "StudioPhase",
]
