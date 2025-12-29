"""
Studio AGENTESE Node: @node("world.studio")

Wraps the Creative Production Studio as an AGENTESE node for universal gateway access.

AGENTESE: world.studio.*

Aspects:
- world.studio.manifest           - Studio capabilities and status
- world.studio.archaeology.excavate - Extract patterns from sources
- world.studio.vision.synthesize  - Generate vision from findings + principles
- world.studio.production.produce - Create asset from vision + requirement
- world.studio.assets.export      - Export asset to format
- world.studio.gallery.place      - Place asset in gallery

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Teaching:
    gotcha: The @node decorator with dependencies=("witness", "brain") requires
            get_witness() and get_brain_persistence() to be registered in
            providers.py BEFORE import. If dependencies aren't registered,
            the node gets None injected (see CLAUDE.md "DI Container" pattern).

    gotcha: Foundry is an OPTIONAL dependency (default=None in __init__).
            This allows Studio to operate without JIT tool compilation.
            When foundry is available, it enables dynamic creative tool synthesis.

    gotcha: Rendering classes provide BOTH to_dict() for JSON and to_text()
            for CLI. _invoke_aspect() returns the dict form; manifest() returns
            the Renderable directly.

Example (CLI):
    kg studio manifest
    kg studio archaeology excavate --sources spec/game.md
    kg studio vision synthesize --findings-id abc123
    kg studio production produce --vision-id xyz789 --asset-type sprite

Example (HTTP):
    POST /agentese/world.studio:manifest
    POST /agentese/world.studio.archaeology:excavate
    {"sources": ["spec/game.md"], "focus": "visual"}

Example (Python):
    >>> from protocols.agentese.logos import create_logos
    >>> logos = create_logos()
    >>> result = await logos.invoke("world.studio", umwelt, aspect="manifest")

See: docs/skills/metaphysical-fullstack.md, docs/skills/agentese-node-registration.md
See: spec/s-gents/studio.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    ArchaeologicalFindings,
    Asset,
    ColorPalette,
    CreativeVision,
    ExcavateRequest,
    ExportedAsset,
    ExportRequest,
    GalleryPlacement,
    MotionSpec,
    Pattern,
    PlaceRequest,
    ProduceRequest,
    StudioManifestResponse,
    SynthesizeRequest,
    TypographySpec,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from services.brain import BrainPersistence
    from services.foundry import AgentFoundry
    from services.witness import WitnessPersistence


# =============================================================================
# Rendering Classes
# =============================================================================


@dataclass(frozen=True)
class StudioManifestRendering:
    """Rendering for studio status manifest."""

    response: StudioManifestResponse

    def to_dict(self) -> dict[str, Any]:
        """JSON for HTTP/WebSocket."""
        return self.response.to_dict()

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        return self.response.to_text()


@dataclass(frozen=True)
class ArchaeologyRendering:
    """Rendering for archaeological findings."""

    response: ArchaeologicalFindings

    def to_dict(self) -> dict[str, Any]:
        """JSON for HTTP/WebSocket."""
        return self.response.to_dict()

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        return self.response.to_text()


@dataclass(frozen=True)
class VisionRendering:
    """Rendering for creative vision."""

    response: CreativeVision

    def to_dict(self) -> dict[str, Any]:
        """JSON for HTTP/WebSocket."""
        return self.response.to_dict()

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        return self.response.to_text()


@dataclass(frozen=True)
class AssetRendering:
    """Rendering for produced asset."""

    response: Asset

    def to_dict(self) -> dict[str, Any]:
        """JSON for HTTP/WebSocket."""
        return self.response.to_dict()

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        return self.response.to_text()


@dataclass(frozen=True)
class ExportRendering:
    """Rendering for exported asset."""

    response: ExportedAsset

    def to_dict(self) -> dict[str, Any]:
        """JSON for HTTP/WebSocket."""
        return self.response.to_dict()

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        return self.response.to_text()


@dataclass(frozen=True)
class GalleryRendering:
    """Rendering for gallery placement."""

    response: GalleryPlacement

    def to_dict(self) -> dict[str, Any]:
        """JSON for HTTP/WebSocket."""
        return self.response.to_dict()

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        return self.response.to_text()


# =============================================================================
# AGENTESE Node
# =============================================================================


@node(
    "world.studio",
    description="Creative Production Studio - Archaeological vision to asset production",
    dependencies=("witness", "brain"),
    contracts={
        "manifest": Response(StudioManifestResponse),
        "archaeology.excavate": Contract(ExcavateRequest, ArchaeologicalFindings),
        "vision.synthesize": Contract(SynthesizeRequest, CreativeVision),
        "production.produce": Contract(ProduceRequest, Asset),
        "assets.export": Contract(ExportRequest, ExportedAsset),
        "gallery.place": Contract(PlaceRequest, GalleryPlacement),
    },
    examples=[
        ("manifest", {}, "Show studio status"),
        (
            "archaeology.excavate",
            {"sources": ["spec/game.md"], "focus": "visual"},
            "Extract visual patterns from spec",
        ),
        (
            "vision.synthesize",
            {"findings_id": "find-123", "target_domain": "game"},
            "Synthesize creative vision from findings",
        ),
        (
            "production.produce",
            {"vision_id": "vis-123", "asset_type": "sprite", "name": "player_idle"},
            "Produce a sprite asset",
        ),
        (
            "assets.export",
            {"asset_id": "asset-123", "format": "web"},
            "Export asset for web",
        ),
        (
            "gallery.place",
            {"asset_id": "asset-123", "category": "characters", "featured": True},
            "Place asset in gallery",
        ),
    ],
)
class StudioNode(BaseLogosNode):
    """
    AGENTESE node for Creative Production Studio Crown Jewel.

    Provides universal access to the Studio via any transport:
    - CLI: kg studio manifest
    - HTTP: POST /agentese/world.studio:manifest
    - WebSocket: {"path": "world.studio", "aspect": "manifest", ...}

    The Studio implements the two-functor pipeline:
    1. Archaeology: Extract patterns from raw materials
    2. Vision: Synthesize creative direction from findings + principles
    3. Production: Create assets from vision + requirements

    Dependencies:
    - witness: Decision tracking for creative choices
    - brain: Artifact storage for assets and visions
    - foundry (optional): JIT tool compilation for creative tools
    """

    def __init__(
        self,
        witness: "WitnessPersistence",
        brain: "BrainPersistence",
        foundry: "AgentFoundry | None" = None,
    ) -> None:
        """
        Initialize with injected dependencies.

        Args:
            witness: WitnessPersistence for decision tracking (required)
            brain: BrainPersistence for artifact storage (required)
            foundry: AgentFoundry for JIT tool compilation (optional)

        The witness and brain are REQUIRED dependencies. Foundry is optional
        and enables advanced creative tool synthesis when available.
        """
        self._witness = witness
        self._brain = brain
        self._foundry = foundry

        # In-memory state (would be persisted via Brain in full implementation)
        self._visions: dict[str, CreativeVision] = {}
        self._assets: dict[str, Asset] = {}
        self._findings: dict[str, ArchaeologicalFindings] = {}
        self._placements: dict[str, GalleryPlacement] = {}

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        return "world.studio"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Developer/Admin: Full access including production and gallery
        Artist/Designer: Creative operations (archaeology, vision, production)
        Guest: Read-only (manifest only)
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        if archetype_lower in ("developer", "operator", "admin", "system"):
            return (
                "manifest",
                "archaeology.excavate",
                "vision.synthesize",
                "production.produce",
                "assets.export",
                "gallery.place",
            )

        if archetype_lower in ("artist", "designer", "architect"):
            return (
                "manifest",
                "archaeology.excavate",
                "vision.synthesize",
                "production.produce",
                "assets.export",
            )

        # Guest users can only view manifest
        return ("manifest",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Show studio status to observer.

        Returns capabilities, current phase, active projects, and dependency status.
        """
        # Determine dependency status
        dependencies = {
            "witness": "connected" if self._witness else "unavailable",
            "brain": "connected" if self._brain else "unavailable",
            "foundry": "connected" if self._foundry else "unavailable",
        }

        response = StudioManifestResponse(
            status="operational",
            current_phase="READY",  # Would be tracked by StudioPolynomial
            active_visions=len(self._visions),
            total_assets=len(self._assets),
            gallery_size=len(self._placements),
            capabilities=[
                "archaeology.excavate",
                "vision.synthesize",
                "production.produce",
                "assets.export",
                "gallery.place",
            ],
            dependencies=dependencies,
        )
        return StudioManifestRendering(response=response)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to Studio methods."""
        match aspect:
            case "archaeology.excavate":
                return await self._excavate(observer, **kwargs)

            case "vision.synthesize":
                return await self._synthesize(observer, **kwargs)

            case "production.produce":
                return await self._produce(observer, **kwargs)

            case "assets.export":
                return await self._export(observer, **kwargs)

            case "gallery.place":
                return await self._place(observer, **kwargs)

            case _:
                return {"error": f"Unknown aspect: {aspect}"}

    async def _excavate(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Extract patterns from source materials.

        AGENTESE: world.studio.archaeology.excavate
        """
        # Parse request
        sources = kwargs.get("sources", [])
        if isinstance(sources, str):
            sources = [sources]
        sources = tuple(sources)

        focus = kwargs.get("focus", "visual")
        depth = kwargs.get("depth", "standard")

        if not sources:
            return {"error": "sources required"}

        # Create request for witness tracking
        request = ExcavateRequest(
            sources=sources,
            focus=focus,
            depth=depth,
        )

        # Placeholder: Actual excavation would analyze the source files
        # and extract patterns using LLM or rule-based analysis
        patterns = [
            Pattern(
                name="placeholder_pattern",
                category=focus,
                description=f"Pattern extracted from {len(sources)} source(s)",
                source_refs=sources,
                confidence=0.8,
            ),
        ]

        findings_id = f"find-{uuid4().hex[:8]}"
        timestamp = datetime.now(UTC).isoformat()

        findings = ArchaeologicalFindings(
            patterns=tuple(patterns),
            provenance={"sources": list(sources), "focus": focus},
            focus=focus,
            source_count=len(sources),
            excavation_timestamp=timestamp,
        )

        # Store findings
        self._findings[findings_id] = findings

        # Would witness the decision
        if self._witness:
            # await self._witness.save_thought(...) for decision tracking
            pass

        result = findings.to_dict()
        result["findings_id"] = findings_id
        return result

    async def _synthesize(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Synthesize creative vision from findings + principles.

        AGENTESE: world.studio.vision.synthesize
        """
        findings_id = kwargs.get("findings_id", "")
        target_domain = kwargs.get("target_domain", "general")
        style_hints = kwargs.get("style_hints", [])
        if isinstance(style_hints, str):
            style_hints = [style_hints]

        if not findings_id:
            return {"error": "findings_id required"}

        # Look up findings (in real impl, would fetch from Brain)
        findings = self._findings.get(findings_id)
        if not findings:
            return {"error": f"Findings not found: {findings_id}"}

        # Placeholder: Actual synthesis would use LLM to generate vision
        vision_id = f"vis-{uuid4().hex[:8]}"
        timestamp = datetime.now(UTC).isoformat()

        vision = CreativeVision(
            vision_id=vision_id,
            core_insight=f"Creative direction for {target_domain}",
            color_palette=ColorPalette(
                primary="#4A90D9",
                secondary="#2E5A8C",
                accent="#FF6B35",
                background="#1A1A2E",
                foreground="#EAEAEA",
                semantic={},
            ),
            typography=TypographySpec(
                heading_font="Inter",
                body_font="Inter",
                mono_font="JetBrains Mono",
                base_size=16,
                scale_ratio=1.25,
            ),
            motion=MotionSpec(
                timing_function="ease-out",
                duration_unit=200,
                stagger_delay=50,
            ),
            tone_of_voice="Professional yet approachable",
            style_keywords=tuple(style_hints) if style_hints else ("modern", "clean"),
            synthesis_timestamp=timestamp,
            findings_ref=findings_id,
        )

        # Store vision
        self._visions[vision_id] = vision

        return vision.to_dict()

    async def _produce(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Produce asset from vision + requirement.

        AGENTESE: world.studio.production.produce
        """
        vision_id = kwargs.get("vision_id", "")
        asset_type = kwargs.get("asset_type", "sprite")
        name = kwargs.get("name", "")
        description = kwargs.get("description", "")

        if not vision_id:
            return {"error": "vision_id required"}
        if not name:
            return {"error": "name required"}

        # Look up vision (in real impl, would fetch from Brain)
        vision = self._visions.get(vision_id)
        if not vision:
            return {"error": f"Vision not found: {vision_id}"}

        # Placeholder: Actual production would generate the asset
        asset_id = f"asset-{uuid4().hex[:8]}"
        timestamp = datetime.now(UTC).isoformat()

        asset = Asset(
            asset_id=asset_id,
            name=name,
            asset_type=asset_type,
            description=description or f"{asset_type} asset",
            vision_id=vision_id,
            file_path=None,  # Would be set after generation
            content=None,
            metadata={"vision_ref": vision_id},
            quality_score=0.85,  # Would be computed
            production_timestamp=timestamp,
        )

        # Store asset
        self._assets[asset_id] = asset

        return asset.to_dict()

    async def _export(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Export asset to format.

        AGENTESE: world.studio.assets.export
        """
        asset_id = kwargs.get("asset_id", "")
        format_type = kwargs.get("format", "web")
        optimization = kwargs.get("optimization", "standard")
        output_path = kwargs.get("output_path")

        if not asset_id:
            return {"error": "asset_id required"}

        # Look up asset
        asset = self._assets.get(asset_id)
        if not asset:
            return {"error": f"Asset not found: {asset_id}"}

        # Placeholder: Actual export would render the asset
        export_id = f"exp-{uuid4().hex[:8]}"
        timestamp = datetime.now(UTC).isoformat()
        file_path = output_path or f"assets/exports/{asset.name}.{format_type}"

        exported = ExportedAsset(
            asset_id=asset_id,
            export_id=export_id,
            format=format_type,
            file_path=file_path,
            file_size_bytes=1024,  # Placeholder
            optimization_applied=optimization,
            export_timestamp=timestamp,
        )

        return exported.to_dict()

    async def _place(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Place asset in gallery.

        AGENTESE: world.studio.gallery.place
        """
        asset_id = kwargs.get("asset_id", "")
        category = kwargs.get("category", "general")
        featured = kwargs.get("featured", False)
        tags = kwargs.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]

        if not asset_id:
            return {"error": "asset_id required"}

        # Look up asset
        asset = self._assets.get(asset_id)
        if not asset:
            return {"error": f"Asset not found: {asset_id}"}

        # Create placement
        placement_id = f"place-{uuid4().hex[:8]}"
        timestamp = datetime.now(UTC).isoformat()

        placement = GalleryPlacement(
            placement_id=placement_id,
            asset_id=asset_id,
            category=category,
            featured=featured,
            gallery_url=f"/gallery/{category}/{asset.name}",
            placement_timestamp=timestamp,
        )

        # Store placement
        self._placements[placement_id] = placement

        return placement.to_dict()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "StudioNode",
    "StudioManifestRendering",
    "ArchaeologyRendering",
    "VisionRendering",
    "AssetRendering",
    "ExportRendering",
    "GalleryRendering",
]
