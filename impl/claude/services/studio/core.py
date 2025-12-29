"""
CreativeStudioService — The Crown Jewel Orchestrator for S-gent Studio.

The Creative Studio synthesizes archaeological findings with creative vision
to produce art assets. It orchestrates the three functors:

1. AestheticArchaeologyFunctor: Extract patterns from raw materials
2. VisionSynthesisFunctor: Generate vision from findings + principles
3. AssetProductionFunctor: Create assets from vision + requirements

AGENTESE: world.studio.*

Pipeline:
    RawMaterial -> excavate() -> findings -> synthesize() -> vision -> produce() -> assets

Key Responsibilities:
1. Archaeology: excavate(), interpret(), trace()
2. Vision: synthesize(), codify(), brand()
3. Production: produce(), refine(), composite()
4. Delivery: export(), gallery_place(), handoff()

Teaching:
    gotcha: Dependencies are injected via __init__. Witness is required for
            provenance tracking, Brain is required for artifact storage.
            Foundry is optional (used for JIT tool compilation).
            (Evidence: TBD - test_core.py::TestStudioInit)

    gotcha: All functor methods are async. Even if the scaffold implementation
            is synchronous, maintain async signature for future LLM integration.
            (Evidence: TBD - test_core.py::TestFunctorMethods)

    gotcha: manifest() returns StudioManifestResponse which implements both
            to_dict() for JSON and to_text() for CLI. Use the right one.
            (Evidence: TBD - test_core.py::TestManifest)

Example:
    >>> from services.studio import CreativeStudioService
    >>> studio = CreativeStudioService(witness=witness, brain=brain)
    >>> findings = await studio.excavate(sources, focus=ArchaeologyFocus.VISUAL)
    >>> vision = await studio.synthesize(findings, principles)
    >>> asset = await studio.produce(vision, requirement)

See: spec/s-gents/studio.md
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .types import (
    ArchaeologicalFindings,
    ArchaeologyFocus,
    Asset,
    AssetRequirement,
    AssetType,
    BrandIdentity,
    ColorPalette,
    CreativeVision,
    DesignPrinciple,
    ExportedAsset,
    ExportFormat,
    Feedback,
    GalleryManifest,
    GalleryPlacement,
    Interpretation,
    InterpretationLens,
    InterpretedMeaning,
    MotionSpec,
    Pattern,
    ProvenanceNode,
    Source,
    StudioManifestResponse,
    StudioPhase,
    StyleGuide,
    StyleRule,
    ToneSpec,
    TypographySpec,
)

if TYPE_CHECKING:
    from services.brain.persistence import BrainPersistence
    from services.foundry import AgentFoundry
    from services.witness import WitnessPersistence

logger = logging.getLogger(__name__)


class CreativeStudioService:
    """
    The Creative Studio Crown Jewel.

    Orchestrates the full creative production pipeline:
    Archaeology -> Vision -> Production -> Delivery

    The Studio implements three functors:
    - AestheticArchaeologyFunctor: Extract patterns from sources
    - VisionSynthesisFunctor: Generate vision from findings + principles
    - AssetProductionFunctor: Create assets from vision + requirements

    LLM Integration:
        When use_llm=True and credentials are available, the Studio uses
        LLM-powered functors for intelligent pattern extraction, vision
        synthesis, and asset production with self-feedback loops.

        When LLM is unavailable, it gracefully degrades to scaffold
        implementations that produce placeholder outputs.

    Usage:
        studio = CreativeStudioService(witness=witness, brain=brain)

        # Archaeology
        findings = await studio.excavate(sources, focus)
        meaning = await studio.interpret(findings, lens)

        # Vision
        vision = await studio.synthesize(findings, principles)
        style_guide = await studio.codify(vision)

        # Production
        asset = await studio.produce(vision, requirement)
        refined = await studio.refine(asset, feedback)

        # Delivery
        exported = await studio.export(asset, format)
        placement = await studio.gallery_place(asset, section)

    Teaching:
        gotcha: LLM integration requires credentials (Claude CLI or Morpheus).
                Check studio.use_llm property to verify LLM is active.
                (Evidence: TBD - test_core.py::TestLLMIntegration)

        gotcha: Self-feedback loops in production can be expensive. Use
                use_llm=False for testing or when scaffold output is sufficient.
                (Evidence: TBD - test_core.py::TestGracefulDegradation)
    """

    def __init__(
        self,
        witness: "WitnessPersistence | None" = None,
        brain: "BrainPersistence | None" = None,
        foundry: "AgentFoundry | None" = None,
        use_llm: bool = True,
    ) -> None:
        """
        Initialize the Creative Studio.

        Args:
            witness: Witness service for decision tracking (recommended)
            brain: Brain service for artifact storage (recommended)
            foundry: Foundry service for JIT tool compilation (optional)
            use_llm: Enable LLM integration (default True). Falls back to
                     scaffold implementations if credentials unavailable.
        """
        self._witness = witness
        self._brain = brain
        self._foundry = foundry

        # State tracking
        self._current_phase = StudioPhase.ARCHAEOLOGY
        self._current_vision: CreativeVision | None = None
        self._assets: dict[str, Asset] = {}
        self._gallery: GalleryManifest = GalleryManifest.empty()
        self._recent_activity: list[dict[str, Any]] = []
        self._max_recent = 20

        # LLM integration with graceful degradation
        self._use_llm = False
        self._archaeology_functor: Any = None
        self._vision_functor: Any = None
        self._production_functor: Any = None

        if use_llm:
            try:
                from .llm import (
                    LLMArchaeologyFunctor,
                    LLMProductionFunctor,
                    LLMVisionFunctor,
                    create_llm_client,
                    has_llm_credentials,
                )

                if has_llm_credentials():
                    llm = create_llm_client()
                    self._archaeology_functor = LLMArchaeologyFunctor(llm=llm)
                    self._vision_functor = LLMVisionFunctor(llm=llm)
                    self._production_functor = LLMProductionFunctor(llm=llm)
                    self._use_llm = True
                    logger.info("LLM functors initialized successfully")
                else:
                    logger.warning("LLM credentials not found, falling back to scaffold mode")
            except ImportError as e:
                logger.warning(f"LLM module import failed: {e}, using scaffold mode")
            except Exception as e:
                logger.warning(f"LLM initialization failed: {e}, using scaffold mode")

        logger.info(
            "CreativeStudioService initialized "
            f"(witness={'ok' if witness else 'none'}, "
            f"brain={'ok' if brain else 'none'}, "
            f"foundry={'ok' if foundry else 'none'}, "
            f"llm={'active' if self._use_llm else 'scaffold'})"
        )

    @property
    def use_llm(self) -> bool:
        """Whether LLM integration is active."""
        return self._use_llm

    @property
    def phase(self) -> StudioPhase:
        """Current phase of the studio pipeline."""
        return self._current_phase

    @property
    def vision(self) -> CreativeVision | None:
        """Currently loaded creative vision."""
        return self._current_vision

    @property
    def asset_count(self) -> int:
        """Number of produced assets."""
        return len(self._assets)

    # =========================================================================
    # Archaeology Functor: excavate(), interpret(), trace()
    # =========================================================================

    async def excavate(
        self,
        sources: list[Source],
        focus: ArchaeologyFocus,
        depth: str = "standard",
    ) -> ArchaeologicalFindings:
        """
        Extract patterns from sources.

        AGENTESE: world.studio.archaeology.excavate

        The excavate operation is the entry point to the archaeology functor.
        It analyzes source materials and extracts patterns relevant to the
        specified focus type.

        Args:
            sources: List of source materials to analyze
            focus: What aspect to focus on (VISUAL, AUDIO, NARRATIVE, etc.)
            depth: Extraction depth ("quick", "standard", "deep")

        Returns:
            ArchaeologicalFindings containing extracted patterns

        Teaching:
            gotcha: When LLM is available, uses intelligent pattern extraction
                    with self-feedback. Falls back to scaffold when unavailable.
                    (Evidence: TBD - test_core.py::TestExcavate)
        """
        logger.info(
            f"excavate: Analyzing {len(sources)} sources with focus={focus.value}, "
            f"depth={depth} (llm={'active' if self._use_llm else 'scaffold'})"
        )

        self._current_phase = StudioPhase.ARCHAEOLOGY
        self._record_activity("excavate", f"{len(sources)} sources, focus={focus.value}")

        # Use LLM functor if available
        if self._use_llm and self._archaeology_functor is not None:
            try:
                # Convert depth string to int for LLM functor
                depth_map = {"quick": 1, "standard": 3, "deep": 5}
                depth_int = depth_map.get(depth, 3)

                findings = await self._archaeology_functor.excavate(
                    sources=sources,
                    focus=focus,
                    depth=depth_int,
                )

                # Witness the excavation if available
                if self._witness:
                    try:
                        await self._witness_action(
                            "excavate",
                            f"LLM excavated {len(findings.patterns)} patterns from {len(sources)} sources",
                            {"focus": focus.value, "depth": depth, "llm": True},
                        )
                    except Exception as e:
                        logger.warning(f"Failed to witness excavation: {e}")

                logger.info(f"excavate: LLM found {len(findings.patterns)} patterns")
                return findings

            except Exception as e:
                logger.warning(f"LLM excavation failed: {e}, falling back to scaffold")

        # Scaffold: Generate placeholder patterns
        patterns: list[Pattern] = []
        provenance: list[ProvenanceNode] = []

        for i, source in enumerate(sources):
            # Create a placeholder pattern for each source
            pattern = Pattern(
                name=f"pattern_{i}_{focus.value}",
                description=f"Placeholder pattern extracted from {source.path}",
                source_refs=(source.path,),
                confidence=0.8,
                focus=focus,
                metadata={
                    "source_type": source.type.value if hasattr(source, "type") else "unknown"
                },
            )
            patterns.append(pattern)

            # Track provenance
            prov = ProvenanceNode(
                pattern_name=pattern.name,
                source_path=source.path,
                extraction_method="scaffold",
            )
            provenance.append(prov)

        findings = ArchaeologicalFindings(
            patterns=tuple(patterns),
            provenance=tuple(provenance),
            sources_analyzed=len(sources),
            focus_used=focus,
            timestamp=datetime.now(UTC),
        )

        # Witness the excavation if available
        if self._witness:
            try:
                await self._witness_action(
                    "excavate",
                    f"Excavated {len(patterns)} patterns from {len(sources)} sources",
                    {"focus": focus.value, "depth": depth, "llm": False},
                )
            except Exception as e:
                logger.warning(f"Failed to witness excavation: {e}")

        logger.info(f"excavate: Found {len(patterns)} patterns")
        return findings

    async def interpret(
        self,
        findings: ArchaeologicalFindings,
        lens: InterpretationLens,
    ) -> InterpretedMeaning:
        """
        Assign meaning to archaeological findings.

        AGENTESE: world.studio.archaeology.interpret

        The interpret operation applies an interpretation lens to findings,
        assigning semantic meaning to extracted patterns.

        Args:
            findings: Archaeological findings to interpret
            lens: Interpretation lens to apply (SEMIOTIC, AESTHETIC, etc.)

        Returns:
            InterpretedMeaning with assigned meanings

        Teaching:
            gotcha: Interpretation is lens-dependent. The same findings
                    will yield different meanings through different lenses.
        """
        logger.info(
            f"interpret: Applying {lens.value} lens to {len(findings.patterns)} patterns "
            f"(llm={'active' if self._use_llm else 'scaffold'})"
        )

        self._record_activity(
            "interpret", f"{lens.value} lens on {len(findings.patterns)} patterns"
        )

        # Use LLM functor if available
        if self._use_llm and self._archaeology_functor is not None:
            try:
                meaning = await self._archaeology_functor.interpret(
                    findings=findings,
                    lens=lens,
                )
                logger.info(
                    f"interpret: LLM generated {len(meaning.interpretations)} interpretations"
                )
                return meaning
            except Exception as e:
                logger.warning(f"LLM interpretation failed: {e}, falling back to scaffold")

        # Scaffold: Generate placeholder interpretations
        interpretations: list[Interpretation] = []
        for pattern in findings.patterns:
            interp = Interpretation(
                pattern_name=pattern.name,
                meaning=f"[{lens.value}] {pattern.description}",
                lens=lens,
                confidence=pattern.confidence * 0.9,  # Slightly lower confidence
            )
            interpretations.append(interp)

        meaning = InterpretedMeaning(
            findings=findings,
            lens=lens,
            interpretations=tuple(interpretations),
        )

        logger.info(f"interpret: Generated {len(interpretations)} interpretations")
        return meaning

    async def trace(
        self,
        pattern_name: str,
        findings: ArchaeologicalFindings,
    ) -> list[ProvenanceNode]:
        """
        Trace provenance of a pattern back to sources.

        AGENTESE: world.studio.archaeology.trace

        Args:
            pattern_name: Name of pattern to trace
            findings: Findings containing the pattern

        Returns:
            List of provenance nodes linking pattern to sources
        """
        logger.info(f"trace: Tracing provenance for pattern '{pattern_name}'")

        self._record_activity("trace", f"pattern={pattern_name}")

        # Find provenance nodes for this pattern
        nodes = [p for p in findings.provenance if p.pattern_name == pattern_name]

        logger.info(f"trace: Found {len(nodes)} provenance nodes")
        return nodes

    # =========================================================================
    # Vision Functor: synthesize(), codify(), brand()
    # =========================================================================

    async def synthesize(
        self,
        findings: ArchaeologicalFindings,
        principles: list[DesignPrinciple],
    ) -> CreativeVision:
        """
        Generate creative vision from findings and principles.

        AGENTESE: world.studio.vision.synthesize

        The synthesize operation is the core of the vision functor. It combines
        archaeological findings with design principles to create a coherent
        creative vision.

        Args:
            findings: Archaeological findings to synthesize from
            principles: Design principles to apply

        Returns:
            CreativeVision representing the synthesized vision

        Teaching:
            gotcha: Vision synthesis is not extraction - it's transformation.
                    Findings are raw material; principles are the forge.

            gotcha: When LLM is active, uses iterative refinement with Three Voices
                    self-critique (Adversarial, Creative, Advocate) until coherent.
                    (Evidence: TBD - test_core.py::TestSynthesize)
        """
        logger.info(
            f"synthesize: Combining {len(findings.patterns)} patterns with "
            f"{len(principles)} principles (llm={'active' if self._use_llm else 'scaffold'})"
        )

        self._current_phase = StudioPhase.SYNTHESIS
        self._record_activity(
            "synthesize", f"{len(findings.patterns)} patterns + {len(principles)} principles"
        )

        # Use LLM functor if available
        if self._use_llm and self._vision_functor is not None:
            try:
                vision = await self._vision_functor.synthesize(
                    findings=findings,
                    principles=principles,
                )

                # Store as current vision
                self._current_vision = vision

                # Witness the synthesis if available
                if self._witness:
                    try:
                        await self._witness_action(
                            "synthesize",
                            f"LLM synthesized vision: {vision.core_insight[:100]}",
                            {
                                "patterns": len(findings.patterns),
                                "principles": len(principles),
                                "llm": True,
                            },
                        )
                    except Exception as e:
                        logger.warning(f"Failed to witness synthesis: {e}")

                logger.info(
                    f"synthesize: LLM created vision with insight: {vision.core_insight[:50]}..."
                )
                return vision

            except Exception as e:
                logger.warning(f"LLM vision synthesis failed: {e}, falling back to scaffold")

        # Scaffold: Create placeholder vision
        # Extract principle statements for vision
        principle_stmts = tuple(p.statement for p in principles)

        # Derive core insight from findings
        if findings.patterns:
            core_insight = f"Vision synthesized from {len(findings.patterns)} patterns"
            if principles:
                core_insight += f" guided by {len(principles)} principles"
        else:
            core_insight = "Placeholder vision - no patterns provided"

        vision = CreativeVision(
            core_insight=core_insight,
            color_palette=ColorPalette.default(),
            typography=TypographySpec.default(),
            motion=MotionSpec.default(),
            tone=ToneSpec.default(),
            principles=principle_stmts,
            timestamp=datetime.now(UTC),
        )

        # Store as current vision
        self._current_vision = vision

        # Witness the synthesis if available
        if self._witness:
            try:
                await self._witness_action(
                    "synthesize",
                    f"Synthesized vision: {core_insight[:100]}",
                    {
                        "patterns": len(findings.patterns),
                        "principles": len(principles),
                        "llm": False,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to witness synthesis: {e}")

        logger.info(f"synthesize: Created vision with insight: {core_insight[:50]}...")
        return vision

    async def codify(
        self,
        vision: CreativeVision,
    ) -> StyleGuide:
        """
        Transform vision into actionable style guide.

        AGENTESE: world.studio.vision.codify

        Args:
            vision: Creative vision to codify

        Returns:
            StyleGuide with concrete rules and examples
        """
        logger.info(
            f"codify: Transforming vision to style guide "
            f"(llm={'active' if self._use_llm else 'scaffold'})"
        )

        self._record_activity("codify", f"vision: {vision.core_insight[:50]}...")

        # Use LLM functor if available
        if self._use_llm and self._vision_functor is not None:
            try:
                style_guide = await self._vision_functor.codify(vision)
                logger.info(
                    f"codify: LLM generated style guide with {len(style_guide.rules)} rules"
                )
                return style_guide
            except Exception as e:
                logger.warning(f"LLM codify failed: {e}, falling back to scaffold")

        # Scaffold: Generate placeholder style guide
        rules = [
            StyleRule(
                category="color",
                rule=f"Use primary color {vision.color_palette.primary} for emphasis",
                rationale="Derived from vision color palette",
            ),
            StyleRule(
                category="typography",
                rule=f"Use {vision.typography.heading_font} for headings",
                rationale="Derived from vision typography",
            ),
            StyleRule(
                category="motion",
                rule=f"Use {vision.motion.easing} easing for all transitions",
                rationale="Derived from vision motion spec",
            ),
        ]

        style_guide = StyleGuide(
            vision=vision,
            rules=tuple(rules),
            examples=(),
        )

        logger.info(f"codify: Generated style guide with {len(rules)} rules")
        return style_guide

    async def brand(
        self,
        vision: CreativeVision,
        name: str,
        tagline: str = "",
    ) -> BrandIdentity:
        """
        Transform vision into brand identity.

        AGENTESE: world.studio.vision.brand

        Args:
            vision: Creative vision to transform
            name: Brand name
            tagline: Brand tagline

        Returns:
            BrandIdentity with full brand specifications
        """
        logger.info(
            f"brand: Creating brand identity for '{name}' "
            f"(llm={'active' if self._use_llm else 'scaffold'})"
        )

        self._record_activity("brand", f"name={name}")

        # Use LLM functor if available
        if self._use_llm and self._vision_functor is not None:
            try:
                brand_identity = await self._vision_functor.brand(
                    vision=vision,
                    name=name,
                    tagline=tagline if tagline else None,
                )
                logger.info(f"brand: LLM created brand identity '{name}'")
                return brand_identity
            except Exception as e:
                logger.warning(f"LLM brand failed: {e}, falling back to scaffold")

        # Scaffold: Generate placeholder brand identity
        brand = BrandIdentity(
            name=name,
            tagline=tagline or f"{name} - powered by vision",
            colors=(
                vision.color_palette.primary,
                vision.color_palette.secondary,
                vision.color_palette.accent,
            ),
            fonts=(
                vision.typography.heading_font,
                vision.typography.body_font,
            ),
            voice=vision.tone.voice,
            personality=vision.tone.personality,
            values=vision.principles,
        )

        logger.info(f"brand: Created brand identity '{name}'")
        return brand

    # =========================================================================
    # Production Functor: produce(), refine(), composite()
    # =========================================================================

    async def produce(
        self,
        vision: CreativeVision,
        requirement: AssetRequirement,
    ) -> Asset:
        """
        Create asset from vision and requirement.

        AGENTESE: world.studio.production.produce

        The produce operation creates a new asset that embodies the vision
        and fulfills the requirement. The producer is opinionated - it
        proposes unexpected but justified directions.

        Args:
            vision: Creative vision guiding production
            requirement: Asset requirement to fulfill

        Returns:
            Produced Asset

        Teaching:
            gotcha: When LLM is active, uses self-feedback loop with quality
                    measurement (Floor checks) and iterative refinement.
                    (Evidence: TBD - test_core.py::TestProduce)

            gotcha: For SPRITE/GRAPHIC/ANIMATION/AUDIO/VIDEO, LLM produces
                    SPECIFICATIONS (prompts, briefs). Only WRITING produces
                    actual content.
        """
        logger.info(
            f"produce: Creating {requirement.type.value} asset '{requirement.name}' "
            f"(llm={'active' if self._use_llm else 'scaffold'})"
        )

        self._current_phase = StudioPhase.PRODUCTION
        self._record_activity("produce", f"{requirement.type.value}: {requirement.name}")

        # Use LLM functor if available
        if self._use_llm and self._production_functor is not None:
            try:
                asset = await self._production_functor.produce(
                    vision=vision,
                    requirement=requirement,
                )

                # Store asset
                self._assets[asset.id] = asset

                # Witness the production if available
                if self._witness:
                    try:
                        await self._witness_action(
                            "produce",
                            f"LLM produced {requirement.type.value}: {requirement.name}",
                            {"asset_id": asset.id, "type": requirement.type.value, "llm": True},
                        )
                    except Exception as e:
                        logger.warning(f"Failed to witness production: {e}")

                # Store in Brain if available
                if self._brain:
                    try:
                        await self._brain.capture(
                            content=f"Asset: {requirement.name}\nType: {requirement.type.value}\n"
                            f"Description: {requirement.description}\n"
                            f"Quality: {asset.quality_score:.2f}",
                            tags=["studio", "asset", requirement.type.value, "llm"],
                            source_type="studio_production",
                            source_ref=asset.id,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to store asset in brain: {e}")

                logger.info(
                    f"produce: LLM created asset {asset.id} (quality={asset.quality_score:.2f})"
                )
                return asset

            except Exception as e:
                logger.warning(f"LLM production failed: {e}, falling back to scaffold")

        # Generate asset ID
        asset_id = f"asset-{uuid.uuid4().hex[:12]}"

        # Scaffold: Create placeholder asset
        asset = Asset(
            id=asset_id,
            type=requirement.type,
            name=requirement.name,
            content=None,  # Placeholder - no actual content
            content_path=None,
            metadata={
                "vision_insight": vision.core_insight[:100],
                "requirement": requirement.description,
                "scaffold": True,
            },
            quality_score=0.8,  # Placeholder quality
            provenance=vision.principles[:3],  # Use principles as provenance
            created_at=datetime.now(UTC),
            requirement_name=requirement.name,
        )

        # Store asset
        self._assets[asset_id] = asset

        # Witness the production if available
        if self._witness:
            try:
                await self._witness_action(
                    "produce",
                    f"Produced {requirement.type.value}: {requirement.name}",
                    {"asset_id": asset_id, "type": requirement.type.value, "llm": False},
                )
            except Exception as e:
                logger.warning(f"Failed to witness production: {e}")

        # Store in Brain if available
        if self._brain:
            try:
                await self._brain.capture(
                    content=f"Asset: {requirement.name}\nType: {requirement.type.value}\n"
                    f"Description: {requirement.description}",
                    tags=["studio", "asset", requirement.type.value],
                    source_type="studio_production",
                    source_ref=asset_id,
                )
            except Exception as e:
                logger.warning(f"Failed to store asset in brain: {e}")

        logger.info(f"produce: Created asset {asset_id}")
        return asset

    async def refine(
        self,
        asset: Asset,
        feedback: Feedback,
    ) -> Asset:
        """
        Improve asset based on feedback.

        AGENTESE: world.studio.production.refine

        Args:
            asset: Asset to refine
            feedback: Feedback to apply

        Returns:
            Refined Asset

        Teaching:
            gotcha: Refinement is additive - it preserves the original
                    while incorporating feedback. Quality should improve.

            gotcha: When LLM is active, uses TextGRAD-like pattern to parse
                    feedback into specific changes while preserving vision alignment.
                    (Evidence: TBD - test_core.py::TestRefine)
        """
        logger.info(
            f"refine: Refining asset {asset.id} with {feedback.type} feedback "
            f"(llm={'active' if self._use_llm else 'scaffold'})"
        )

        self._current_phase = StudioPhase.REVIEW
        self._record_activity("refine", f"asset={asset.id}, feedback={feedback.type}")

        # Use LLM functor if available
        if self._use_llm and self._production_functor is not None:
            try:
                refined_asset = await self._production_functor.refine(
                    asset=asset,
                    feedback=feedback,
                )

                # Update stored asset
                self._assets[asset.id] = refined_asset

                logger.info(f"refine: LLM refined asset {asset.id}")
                return refined_asset

            except Exception as e:
                logger.warning(f"LLM refinement failed: {e}, falling back to scaffold")

        # Scaffold: Create new asset with updated metadata
        refined_asset = Asset(
            id=asset.id,  # Keep same ID (it's the same asset, refined)
            type=asset.type,
            name=asset.name,
            content=asset.content,
            content_path=asset.content_path,
            metadata={
                **asset.metadata,
                "refined": True,
                "feedback_type": feedback.type,
                "feedback_description": feedback.description[:100],
            },
            quality_score=min(1.0, asset.quality_score + 0.1),  # Slight improvement
            provenance=asset.provenance,
            created_at=asset.created_at,
            requirement_name=asset.requirement_name,
        )

        # Update stored asset
        self._assets[asset.id] = refined_asset

        logger.info(f"refine: Refined asset {asset.id}")
        return refined_asset

    async def composite(
        self,
        assets: list[Asset],
        name: str,
        output_type: AssetType = AssetType.GRAPHIC,
    ) -> Asset:
        """
        Combine multiple assets into one.

        AGENTESE: world.studio.production.composite

        Args:
            assets: Assets to combine
            name: Name for composite asset
            output_type: Type of output asset

        Returns:
            Composite Asset

        Teaching:
            gotcha: When LLM is active, validates style coherence across assets
                    and resolves any contradictions before combining.
                    (Evidence: TBD - test_core.py::TestComposite)
        """
        logger.info(
            f"composite: Combining {len(assets)} assets into '{name}' "
            f"(llm={'active' if self._use_llm else 'scaffold'})"
        )

        self._record_activity("composite", f"{len(assets)} assets -> {name}")

        # Use LLM functor if available
        if self._use_llm and self._production_functor is not None:
            try:
                composite = await self._production_functor.composite(
                    assets=assets,
                    name=name,
                )

                # Store composite
                self._assets[composite.id] = composite

                logger.info(f"composite: LLM created composite {composite.id}")
                return composite

            except Exception as e:
                logger.warning(f"LLM composite failed: {e}, falling back to scaffold")

        # Generate composite ID
        composite_id = f"composite-{uuid.uuid4().hex[:12]}"

        # Scaffold: Create placeholder composite
        composite = Asset(
            id=composite_id,
            type=output_type,
            name=name,
            content=None,
            content_path=None,
            metadata={
                "source_assets": [a.id for a in assets],
                "composite": True,
                "scaffold": True,
            },
            quality_score=sum(a.quality_score for a in assets) / len(assets) if assets else 0.5,
            provenance=tuple(a.name for a in assets),
            created_at=datetime.now(UTC),
        )

        # Store composite
        self._assets[composite_id] = composite

        logger.info(f"composite: Created composite {composite_id}")
        return composite

    # =========================================================================
    # Delivery Methods: export(), gallery_place(), handoff()
    # =========================================================================

    async def export(
        self,
        asset: Asset,
        format: ExportFormat,
        output_path: str | None = None,
        optimization: str = "standard",
    ) -> ExportedAsset:
        """
        Export asset to specified format.

        AGENTESE: world.studio.assets.export

        Args:
            asset: Asset to export
            format: Export format
            output_path: Desired output path (optional)
            optimization: Optimization level ("none", "standard", "aggressive")

        Returns:
            ExportedAsset with export details
        """
        logger.info(
            f"export: Exporting asset {asset.id} to {format.value} (optimization={optimization})"
        )

        self._current_phase = StudioPhase.DELIVERY
        self._record_activity("export", f"asset={asset.id}, format={format.value}")

        # Generate export path if not provided
        if not output_path:
            output_path = f"exports/{asset.name}.{format.value}"

        # Scaffold: Create placeholder export
        exported = ExportedAsset(
            asset=asset,
            format=format,
            path=output_path,
            size_bytes=1024,  # Placeholder size
            optimization_applied=(optimization,) if optimization != "none" else (),
        )

        logger.info(f"export: Exported to {output_path}")
        return exported

    async def gallery_place(
        self,
        asset: Asset,
        section: str,
        position: int | None = None,
        caption: str = "",
        tags: tuple[str, ...] = (),
    ) -> GalleryPlacement:
        """
        Place asset in the gallery.

        AGENTESE: world.studio.gallery.place

        Args:
            asset: Asset to place
            section: Gallery section ("featured", "sprites", etc.)
            position: Position within section (optional)
            caption: Caption for display
            tags: Tags for categorization

        Returns:
            GalleryPlacement confirmation
        """
        logger.info(f"gallery_place: Placing asset {asset.id} in section '{section}'")

        self._record_activity("gallery_place", f"asset={asset.id}, section={section}")

        # Determine position if not provided
        if position is None:
            existing = [p for p in self._gallery.placements if p.section == section]
            position = len(existing)

        # Create placement
        placement = GalleryPlacement(
            asset_id=asset.id,
            section=section,
            position=position,
            caption=caption,
            tags=tags,
            placed_at=datetime.now(UTC),
        )

        # Update gallery
        new_placements = self._gallery.placements + (placement,)
        self._gallery = GalleryManifest(
            sections=self._gallery.sections,
            placements=new_placements,
            total_assets=len(new_placements),
            last_updated=datetime.now(UTC),
        )

        logger.info(f"gallery_place: Placed in {section} at position {position}")
        return placement

    async def handoff(
        self,
        assets: list[Asset],
        recipient: str,
        notes: str = "",
    ) -> dict[str, Any]:
        """
        Hand off assets to a recipient.

        AGENTESE: world.studio.delivery.handoff

        Args:
            assets: Assets to hand off
            recipient: Recipient identifier
            notes: Delivery notes

        Returns:
            Handoff confirmation with package details
        """
        logger.info(f"handoff: Handing off {len(assets)} assets to '{recipient}'")

        self._record_activity("handoff", f"{len(assets)} assets -> {recipient}")

        # Create handoff package
        package_id = f"handoff-{uuid.uuid4().hex[:12]}"

        result = {
            "package_id": package_id,
            "recipient": recipient,
            "asset_count": len(assets),
            "asset_ids": [a.id for a in assets],
            "notes": notes,
            "handed_off_at": datetime.now(UTC).isoformat(),
        }

        # Witness the handoff if available
        if self._witness:
            try:
                await self._witness_action(
                    "handoff",
                    f"Handed off {len(assets)} assets to {recipient}",
                    {"package_id": package_id, "recipient": recipient},
                )
            except Exception as e:
                logger.warning(f"Failed to witness handoff: {e}")

        logger.info(f"handoff: Created package {package_id}")
        return result

    # =========================================================================
    # Manifest
    # =========================================================================

    async def manifest(self) -> StudioManifestResponse:
        """
        Get studio status manifest.

        AGENTESE: world.studio.manifest

        Returns:
            StudioManifestResponse with current status
        """
        return StudioManifestResponse(
            status="operational",
            phase=self._current_phase.name,
            vision_loaded=self._current_vision is not None,
            assets_count=len(self._assets),
            pending_requirements=0,  # Scaffold: no requirement tracking yet
            gallery_sections=self._gallery.sections,
            recent_activity=tuple(self._recent_activity[-10:]),
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _record_activity(self, action: str, target: str) -> None:
        """Record activity for recent activity log."""
        self._recent_activity.append(
            {
                "action": action,
                "target": target,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        # Keep only last N entries
        if len(self._recent_activity) > self._max_recent:
            self._recent_activity = self._recent_activity[-self._max_recent :]

    async def _witness_action(
        self,
        action: str,
        reasoning: str,
        context: dict[str, Any],
    ) -> None:
        """Record action via Witness service."""
        if self._witness is None:
            return

        # Use capture_thought if available, otherwise log
        if hasattr(self._witness, "capture_thought"):
            await self._witness.capture_thought(
                content=f"Studio {action}: {reasoning}",
                context=context,
            )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "CreativeStudioService",
]
