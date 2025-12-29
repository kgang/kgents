"""
LLM-Powered Asset Production Functor.

The AssetProductionFunctor that creates assets from vision + requirements
using LLM-backed generation with self-feedback and iterative refinement.

Key Behaviors:
1. Opinionated: Proposes unexpected but justified creative directions
2. Self-Critical: Measures quality via Floor checks (provenance, format, style, access)
3. Iterative: Refines until quality threshold met or max iterations reached

Pipeline:
    Vision + Requirement -> analyze() -> generate() -> measure() -> [iterate?] -> Asset

For different asset types:
- SPRITE/GRAPHIC: Generates detailed art prompts + specs
- ANIMATION: Generates animation specs (frames, timing, states)
- AUDIO: Generates sound design briefs
- WRITING: Generates actual text content
- VIDEO: Generates storyboard/shot lists

Teaching:
    gotcha: This functor produces SPECIFICATIONS, not raw binaries. For sprites,
            it produces prompts suitable for image generators. For audio, it
            produces sound design briefs. Only WRITING produces actual content.
            (Evidence: test_production.py::TestAssetTypes)

    gotcha: The functor is OPINIONATED. It analyzes the requirement and vision,
            then proposes creative interpretations that may diverge from literal
            requirements while staying true to the vision's spirit.
            (Evidence: test_production.py::TestOpinionatedProduction)

    gotcha: Quality measurement uses Floor checks from the Tetrad:
            F1: Provenance (traceable to vision/requirement)
            F2: Format compliance (specs met)
            F3: Style coherence (vision alignment)
            F4: Accessibility (if applicable)
            (Evidence: test_production.py::TestQualityMeasurement)

Example:
    >>> from agents.k.llm import create_llm_client
    >>> from services.studio.llm import LLMProductionFunctor
    >>>
    >>> llm = create_llm_client()
    >>> functor = LLMProductionFunctor(llm)
    >>>
    >>> asset = await functor.produce(vision, requirement)
    >>> assert asset.quality_score >= 0.7

See: spec/s-gents/studio.md
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from agents.k.llm import LLMClient, LLMResponse

from ..types import (
    Asset,
    AssetRequirement,
    AssetType,
    CreativeVision,
    Feedback,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Quality Thresholds
# =============================================================================

DEFAULT_QUALITY_THRESHOLD = 0.7
MAX_REFINEMENT_ITERATIONS = 3
FLOOR_WEIGHTS = {
    "provenance": 0.25,  # F1: Traceable to vision/requirement
    "format": 0.25,  # F2: Technical specs met
    "style": 0.30,  # F3: Vision alignment (most important)
    "accessibility": 0.20,  # F4: Accessibility compliance
}


# =============================================================================
# System Prompts
# =============================================================================

PRODUCTION_SYSTEM_PROMPT = """You are the Creative Production Functor for the S-gent Studio.

Your role is to CREATE OPINIONATED creative specifications from vision and requirements.

CRITICAL PRINCIPLES:
1. OPINIONATED: Don't just execute requirements literally. Propose unexpected but JUSTIFIED directions that enhance the vision.
2. VISION-FAITHFUL: Every choice must trace back to the creative vision's core insight, color palette, tone, and principles.
3. SPECIFIC: Generate detailed, actionable specifications - not vague descriptions.
4. JUSTIFIED: Every creative choice needs reasoning rooted in the vision.

OUTPUT FORMAT:
Always respond with valid JSON containing:
- "creative_direction": Your opinionated interpretation (1-2 sentences)
- "justification": Why this direction serves the vision
- "spec": Asset-type-specific specification (see below)
- "provenance": List of vision elements this draws from

ASSET TYPE SPECIFICATIONS:

For SPRITE/GRAPHIC:
{
  "dimensions": [width, height],
  "color_palette": ["#hex1", "#hex2", ...],  // subset of vision palette
  "art_style": "detailed style description",
  "composition": "layout and focal point description",
  "prompt_for_generator": "detailed AI art prompt",
  "technical_notes": "any render/export considerations"
}

For ANIMATION:
{
  "frame_count": number,
  "fps": number,
  "states": [{"name": "idle", "frames": [0,1,2], "loop": true}, ...],
  "timing_notes": "easing and rhythm aligned with vision.motion",
  "keyframe_descriptions": ["frame 0: ...", "frame 5: ...", ...]
}

For AUDIO:
{
  "duration_seconds": number,
  "type": "sfx|music|ambient|voice",
  "mood": "emotional quality",
  "instrumentation": "instruments or sound sources",
  "reference_description": "what it should sound like",
  "technical_specs": {"sample_rate": 44100, "format": "ogg", ...}
}

For WRITING:
{
  "content": "THE ACTUAL TEXT CONTENT",
  "voice_notes": "how this aligns with vision.tone",
  "word_count": number
}

For VIDEO:
{
  "duration_seconds": number,
  "shot_list": [{"shot": 1, "type": "wide", "action": "...", "duration": 2.0}, ...],
  "transitions": "how shots connect",
  "audio_notes": "sound design direction"
}

Remember: You are the creative director. Be BOLD. Propose something unexpected that serves the vision better than the literal requirement might."""


QUALITY_MEASUREMENT_PROMPT = """You are the Quality Assessor for the S-gent Studio's Asset Production.

Your job is to measure asset quality against Floor checks from the Tetrad.

THE FOUR FLOORS (F1-F4):

F1 - PROVENANCE (0.0-1.0):
- Can every creative choice be traced to the vision or requirement?
- Are sources cited in the provenance field?
- No unexplained additions?

F2 - FORMAT COMPLIANCE (0.0-1.0):
- Does the spec match the requirement's technical specifications?
- Correct dimensions, formats, constraints?
- All required fields present?

F3 - STYLE COHERENCE (0.0-1.0):
- Does this FEEL like the vision?
- Color palette alignment?
- Tone and voice consistency?
- Motion/timing aligned with vision.motion?

F4 - ACCESSIBILITY (0.0-1.0):
- For visual: contrast, readability
- For audio: hearing-accessible alternatives noted?
- For writing: clear, inclusive language?
- For any: no barriers to engagement?

OUTPUT FORMAT:
Return valid JSON:
{
  "scores": {
    "provenance": 0.0-1.0,
    "format": 0.0-1.0,
    "style": 0.0-1.0,
    "accessibility": 0.0-1.0
  },
  "weighted_total": 0.0-1.0,
  "issues": ["issue1", "issue2", ...],
  "strengths": ["strength1", "strength2", ...]
}

Be RIGOROUS. Quality matters more than praise."""


REFINEMENT_PROMPT = """You are the Refinement Engine for the S-gent Studio's Asset Production.

Your job is to IMPROVE an asset based on feedback while PRESERVING vision alignment.

CRITICAL RULES:
1. Address EVERY issue in the feedback
2. Do NOT regress on aspects not mentioned in feedback
3. Preserve all provenance links
4. Maintain the creative direction's spirit
5. Output the COMPLETE revised spec, not just changes

INPUT: You will receive the current asset spec and the feedback.

OUTPUT FORMAT:
Return valid JSON with the COMPLETE revised specification in the same format as the original, plus:
{
  "revision_notes": "what changed and why",
  "addressed_issues": ["issue1", "issue2"],
  ... (full spec fields)
}

Be SURGICAL. Fix what's broken, preserve what works."""


COMPOSITE_PROMPT = """You are the Composition Engine for the S-gent Studio's Asset Production.

Your job is to COMBINE multiple assets into a coherent composite while ensuring:
1. Style coherence across all source assets
2. No contradictions between components
3. Unified provenance chain

INPUT: You will receive multiple asset specs to combine.

OUTPUT FORMAT:
Return valid JSON:
{
  "composition_strategy": "how elements combine",
  "coherence_check": {
    "style_consistent": true/false,
    "contradictions": ["if any"],
    "resolution": "how contradictions were resolved"
  },
  "unified_spec": { ... combined specification ... },
  "provenance_chain": ["all sources traced"]
}

Be a CURATOR. The whole must exceed the sum of its parts."""


# =============================================================================
# LLMProductionFunctor
# =============================================================================


class LLMProductionFunctor:
    """
    LLM-powered asset production functor.

    Creates creative specifications and code assets from vision + requirements.
    For actual image/audio generation, produces detailed prompts that can be
    sent to specialized tools.

    The functor is OPINIONATED - it proposes unexpected but justified
    directions, not just executing requirements blindly.

    Attributes:
        llm: The LLM client for generation
        quality_threshold: Minimum quality score to accept (default 0.7)
        max_iterations: Maximum refinement iterations (default 3)

    Usage:
        llm = create_llm_client()
        functor = LLMProductionFunctor(llm)

        asset = await functor.produce(vision, requirement)
        refined = await functor.refine(asset, feedback)
        composite = await functor.composite([asset1, asset2], "combined")
    """

    def __init__(
        self,
        llm: LLMClient,
        quality_threshold: float = DEFAULT_QUALITY_THRESHOLD,
        max_iterations: int = MAX_REFINEMENT_ITERATIONS,
    ) -> None:
        """
        Initialize the production functor.

        Args:
            llm: LLM client for generation (from agents.k.llm)
            quality_threshold: Minimum quality to accept without refinement
            max_iterations: Max self-refinement loops before accepting
        """
        self._llm = llm
        self._quality_threshold = quality_threshold
        self._max_iterations = max_iterations

        logger.info(
            f"LLMProductionFunctor initialized "
            f"(threshold={quality_threshold}, max_iter={max_iterations})"
        )

    async def produce(
        self,
        vision: CreativeVision,
        requirement: AssetRequirement,
    ) -> Asset:
        """
        Produce asset that embodies vision and fulfills requirement.

        Process:
        1. Analyze requirement against vision
        2. Generate asset-type-specific content (opinionated)
        3. Measure quality against Floor checks
        4. Iterate if quality < threshold (up to max_iterations)

        Args:
            vision: Creative vision guiding production
            requirement: Asset requirement to fulfill

        Returns:
            Produced Asset with quality score and provenance

        Teaching:
            gotcha: For SPRITE/GRAPHIC/ANIMATION/AUDIO/VIDEO, this produces
                    SPECIFICATIONS (prompts, briefs), not raw binaries.
                    Only WRITING produces actual content.
        """
        logger.info(f"produce: Creating {requirement.type.value} asset '{requirement.name}'")

        # Generate initial specification
        spec, creative_direction, provenance = await self._generate_asset_spec(vision, requirement)

        # Create initial asset
        asset = self._create_asset(
            requirement=requirement,
            spec=spec,
            creative_direction=creative_direction,
            provenance=provenance,
        )

        # Measure quality and iterate if needed
        iteration = 0
        while iteration < self._max_iterations:
            quality_result = await self._measure_asset_quality(asset, vision)
            asset = self._update_asset_quality(asset, quality_result["weighted_total"])

            if quality_result["weighted_total"] >= self._quality_threshold:
                logger.info(
                    f"produce: Asset '{requirement.name}' achieved quality "
                    f"{quality_result['weighted_total']:.2f} >= {self._quality_threshold}"
                )
                break

            # Need refinement
            iteration += 1
            logger.info(
                f"produce: Iteration {iteration}/{self._max_iterations} - "
                f"quality {quality_result['weighted_total']:.2f} < {self._quality_threshold}, "
                f"refining..."
            )

            if iteration < self._max_iterations:
                # Create synthetic feedback from quality issues
                feedback = Feedback(
                    asset_id=asset.id,
                    type="enhancement",
                    description=f"Quality issues: {', '.join(quality_result.get('issues', []))}",
                    specifics={"quality_result": quality_result},
                )
                asset = await self.refine(asset, feedback)

        logger.info(
            f"produce: Completed asset '{requirement.name}' "
            f"(quality={asset.quality_score:.2f}, iterations={iteration})"
        )
        return asset

    async def refine(
        self,
        asset: Asset,
        feedback: Feedback,
    ) -> Asset:
        """
        Improve asset based on feedback.

        Uses TextGRAD-like pattern:
        1. Parse feedback into actionable changes
        2. Apply changes while preserving vision alignment
        3. Re-validate quality

        Args:
            asset: Asset to refine
            feedback: Feedback with issues to address

        Returns:
            Refined Asset with updated spec and metadata
        """
        logger.info(f"refine: Refining asset {asset.id} based on {feedback.type} feedback")

        # Extract current spec from metadata
        current_spec = asset.metadata.get("spec", {})
        creative_direction = asset.metadata.get("creative_direction", "")

        # Generate refined spec
        user_prompt = f"""CURRENT ASSET SPEC:
{json.dumps(current_spec, indent=2)}

CURRENT CREATIVE DIRECTION:
{creative_direction}

FEEDBACK TO ADDRESS:
Type: {feedback.type}
Description: {feedback.description}
Specifics: {json.dumps(feedback.specifics, indent=2)}

Refine this asset to address all feedback issues while preserving its creative spirit."""

        response = await self._llm.generate(
            system=REFINEMENT_PROMPT,
            user=user_prompt,
            temperature=0.6,
            max_tokens=4000,
        )

        # Parse refined spec
        refined_data = self._parse_json_response(response)

        # Update spec with refinement data
        new_spec = {**current_spec}
        for key, value in refined_data.items():
            if key not in ("revision_notes", "addressed_issues"):
                new_spec[key] = value

        # Create refined asset
        refined_asset = Asset(
            id=asset.id,  # Keep same ID
            type=asset.type,
            name=asset.name,
            content=asset.content if asset.type != AssetType.WRITING else new_spec.get("content"),
            content_path=asset.content_path,
            metadata={
                **asset.metadata,
                "spec": new_spec,
                "revision_notes": refined_data.get("revision_notes", ""),
                "addressed_issues": refined_data.get("addressed_issues", []),
                "refinement_count": asset.metadata.get("refinement_count", 0) + 1,
            },
            quality_score=asset.quality_score,  # Will be re-measured
            provenance=asset.provenance,
            created_at=asset.created_at,
            requirement_name=asset.requirement_name,
        )

        logger.info(
            f"refine: Refined asset {asset.id} "
            f"(addressed: {refined_data.get('addressed_issues', [])})"
        )
        return refined_asset

    async def composite(
        self,
        assets: list[Asset],
        name: str,
    ) -> Asset:
        """
        Combine multiple assets into composite.

        Validates:
        - Style coherence across assets
        - No contradictions
        - Unified provenance

        Args:
            assets: Assets to combine
            name: Name for the composite asset

        Returns:
            Composite Asset with unified spec
        """
        if not assets:
            raise ValueError("Cannot composite empty asset list")

        logger.info(f"composite: Combining {len(assets)} assets into '{name}'")

        # Extract specs from all assets
        asset_specs = []
        for asset in assets:
            asset_specs.append(
                {
                    "name": asset.name,
                    "type": asset.type.value,
                    "spec": asset.metadata.get("spec", {}),
                    "creative_direction": asset.metadata.get("creative_direction", ""),
                    "provenance": list(asset.provenance),
                }
            )

        user_prompt = f"""ASSETS TO COMBINE:
{json.dumps(asset_specs, indent=2)}

COMPOSITE NAME: {name}

Combine these assets into a coherent composite, ensuring style consistency and no contradictions."""

        response = await self._llm.generate(
            system=COMPOSITE_PROMPT,
            user=user_prompt,
            temperature=0.5,
            max_tokens=4000,
        )

        composite_data = self._parse_json_response(response)

        # Determine output type (use first asset's type, or GRAPHIC for mixed)
        output_type = assets[0].type
        if len(set(a.type for a in assets)) > 1:
            output_type = AssetType.GRAPHIC  # Mixed types become GRAPHIC

        # Collect all provenance
        all_provenance: list[str] = []
        for asset in assets:
            all_provenance.extend(asset.provenance)
        all_provenance.extend(composite_data.get("provenance_chain", []))

        # Check for contradictions
        coherence = composite_data.get("coherence_check", {})
        if coherence.get("contradictions"):
            logger.warning(f"composite: Found contradictions: {coherence['contradictions']}")

        # Create composite asset
        composite_id = f"composite-{uuid.uuid4().hex[:12]}"
        composite = Asset(
            id=composite_id,
            type=output_type,
            name=name,
            content=None,
            content_path=None,
            metadata={
                "spec": composite_data.get("unified_spec", {}),
                "composition_strategy": composite_data.get("composition_strategy", ""),
                "coherence_check": coherence,
                "source_assets": [a.id for a in assets],
                "composite": True,
            },
            quality_score=sum(a.quality_score for a in assets) / len(assets),
            provenance=tuple(dict.fromkeys(all_provenance)),  # Dedupe while preserving order
            created_at=datetime.now(UTC),
        )

        logger.info(
            f"composite: Created composite {composite_id} "
            f"(style_consistent={coherence.get('style_consistent', 'unknown')})"
        )
        return composite

    # =========================================================================
    # Internal Generation Methods
    # =========================================================================

    async def _generate_asset_spec(
        self,
        vision: CreativeVision,
        requirement: AssetRequirement,
    ) -> tuple[dict[str, Any], str, tuple[str, ...]]:
        """
        Generate asset-type-specific specification.

        Returns:
            Tuple of (spec dict, creative direction string, provenance tuple)
        """

        # Build vision context (handle both dataclass and dict types)
        def safe_to_dict(obj):
            """Convert to dict, handling both dataclasses and dicts."""
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            elif hasattr(obj, "__dict__"):
                return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
            elif isinstance(obj, dict):
                return obj
            else:
                return str(obj)

        vision_context = {
            "core_insight": vision.core_insight,
            "color_palette": safe_to_dict(vision.color_palette),
            "typography": safe_to_dict(vision.typography),
            "motion": safe_to_dict(vision.motion),
            "tone": safe_to_dict(vision.tone),
            "principles": list(vision.principles) if vision.principles else [],
        }

        # Build requirement context
        requirement_context = {
            "type": requirement.type.value,
            "name": requirement.name,
            "description": requirement.description,
            "specs": requirement.specs
            if isinstance(requirement.specs, dict)
            else safe_to_dict(requirement.specs),
            "constraints": [safe_to_dict(c) for c in requirement.constraints]
            if requirement.constraints
            else [],
            "tags": list(requirement.tags) if requirement.tags else [],
        }

        user_prompt = f"""CREATIVE VISION:
{json.dumps(vision_context, indent=2)}

ASSET REQUIREMENT:
{json.dumps(requirement_context, indent=2)}

Create an OPINIONATED {requirement.type.value} asset specification that embodies this vision.
Be bold. Propose something unexpected but justified."""

        response = await self._llm.generate(
            system=PRODUCTION_SYSTEM_PROMPT,
            user=user_prompt,
            temperature=0.8,  # Higher for creativity
            max_tokens=4000,
        )

        # Parse response
        data = self._parse_json_response(response)

        spec = data.get("spec", {})
        creative_direction = data.get("creative_direction", "")
        justification = data.get("justification", "")
        provenance = tuple(data.get("provenance", []))

        # Enrich spec with metadata
        spec["_creative_direction"] = creative_direction
        spec["_justification"] = justification

        logger.info(f"_generate_asset_spec: Generated spec for {requirement.type.value}")
        return spec, creative_direction, provenance

    async def _generate_sprite_spec(
        self,
        vision: CreativeVision,
        requirement: AssetRequirement,
    ) -> dict[str, Any]:
        """
        Generate detailed sprite specification.

        Includes:
        - Dimensions, color palette subset
        - Animation states and frame counts
        - Art style description for artist/AI
        - Reference prompts for generation tools
        """
        spec, _, _ = await self._generate_asset_spec(vision, requirement)
        return spec

    async def _generate_writing(
        self,
        vision: CreativeVision,
        requirement: AssetRequirement,
    ) -> str:
        """
        Generate actual text content.

        Uses vision.tone for voice consistency.
        Matches brand identity.
        """
        spec, _, _ = await self._generate_asset_spec(vision, requirement)
        content = spec.get("content", "")
        return str(content) if content else ""

    async def _measure_asset_quality(
        self,
        asset: Asset,
        vision: CreativeVision,
    ) -> dict[str, Any]:
        """
        Measure asset quality against Floor checks.

        F1: Provenance (traceable to vision/requirement)
        F2: Format compliance (specs met)
        F3: Style coherence (vision alignment)
        F4: Accessibility (if applicable)

        Returns:
            Dict with scores, weighted_total, issues, strengths
        """
        spec = asset.metadata.get("spec", {})
        creative_direction = asset.metadata.get("creative_direction", "")

        # Helper for safe serialization
        def safe_to_dict(obj):
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            elif hasattr(obj, "__dict__"):
                return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
            elif isinstance(obj, dict):
                return obj
            return str(obj)

        measurement_context = {
            "asset": {
                "type": asset.type.value,
                "name": asset.name,
                "spec": spec,
                "creative_direction": creative_direction,
                "provenance": list(asset.provenance) if asset.provenance else [],
            },
            "vision": {
                "core_insight": vision.core_insight,
                "color_palette": safe_to_dict(vision.color_palette),
                "tone": safe_to_dict(vision.tone),
                "principles": list(vision.principles) if vision.principles else [],
            },
            "requirement_name": getattr(asset, "requirement_name", asset.name),
        }

        user_prompt = f"""ASSET TO MEASURE:
{json.dumps(measurement_context, indent=2)}

Measure this asset against the four Floor checks (F1-F4).
Be RIGOROUS - quality matters."""

        response = await self._llm.generate(
            system=QUALITY_MEASUREMENT_PROMPT,
            user=user_prompt,
            temperature=0.3,  # Lower for consistency
            max_tokens=2000,
        )

        result = self._parse_json_response(response)

        # Ensure all required fields
        scores = result.get("scores", {})
        weighted_total = result.get("weighted_total")

        # Calculate weighted total if not provided
        if weighted_total is None:
            weighted_total = sum(
                scores.get(key, 0.5) * weight for key, weight in FLOOR_WEIGHTS.items()
            )
            result["weighted_total"] = weighted_total

        logger.info(
            f"_measure_asset_quality: {asset.name} scored {weighted_total:.2f} "
            f"(P={scores.get('provenance', '?')}, F={scores.get('format', '?')}, "
            f"S={scores.get('style', '?')}, A={scores.get('accessibility', '?')})"
        )

        return result

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _create_asset(
        self,
        requirement: AssetRequirement,
        spec: dict[str, Any],
        creative_direction: str,
        provenance: tuple[str, ...],
    ) -> Asset:
        """Create Asset from generated spec."""
        asset_id = f"asset-{uuid.uuid4().hex[:12]}"

        # For WRITING, extract content directly
        content = None
        if requirement.type == AssetType.WRITING:
            content = spec.get("content", "")

        return Asset(
            id=asset_id,
            type=requirement.type,
            name=requirement.name,
            content=content,
            content_path=None,
            metadata={
                "spec": spec,
                "creative_direction": creative_direction,
                "justification": spec.get("_justification", ""),
                "refinement_count": 0,
            },
            quality_score=0.0,  # Will be measured
            provenance=provenance,
            created_at=datetime.now(UTC),
            requirement_name=requirement.name,
        )

    def _update_asset_quality(self, asset: Asset, quality_score: float) -> Asset:
        """Return new Asset with updated quality score."""
        return Asset(
            id=asset.id,
            type=asset.type,
            name=asset.name,
            content=asset.content,
            content_path=asset.content_path,
            metadata=asset.metadata,
            quality_score=quality_score,
            provenance=asset.provenance,
            created_at=asset.created_at,
            requirement_name=asset.requirement_name,
        )

    def _parse_json_response(self, response: LLMResponse) -> dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        text = response.text.strip()

        # Try to extract JSON from code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()

        try:
            result = json.loads(text)
            if not isinstance(result, dict):
                return {"raw": result}
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # Return a minimal valid structure
            return {
                "spec": {},
                "creative_direction": "Parse error - using defaults",
                "provenance": [],
                "scores": {
                    "provenance": 0.5,
                    "format": 0.5,
                    "style": 0.5,
                    "accessibility": 0.5,
                },
                "weighted_total": 0.5,
                "issues": ["JSON parse error"],
                "strengths": [],
            }


# =============================================================================
# Exports
# =============================================================================

__all__ = ["LLMProductionFunctor"]
