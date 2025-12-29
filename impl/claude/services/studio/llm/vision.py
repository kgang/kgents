"""
LLM-powered VisionSynthesisFunctor: Generate creative vision from findings + principles.

> *"Daring, bold, creative, opinionated but not gaudy."*
> *"Tasteful > feature-complete; Joy-inducing > merely functional."*
> *"The persona is a garden, not a museum."*

This functor transforms archaeological findings and design principles into
unified creative visions. It employs iterative refinement with self-critique
using the Three Voices pattern:

    - Adversarial: Technical coherence check
    - Creative: Novelty and interest assessment
    - Advocate: Would Kent be delighted?

Pipeline:
    1. Summarize key patterns from findings
    2. Apply principles as constraints
    3. Generate vision components (colors, typography, motion, tone)
    4. Self-critique for coherence
    5. Iterate until coherent (max 3 iterations)

Usage:
    from services.studio.llm import LLMVisionFunctor
    from agents.k.llm import create_llm_client

    llm = create_llm_client()
    functor = LLMVisionFunctor(llm)

    vision = await functor.synthesize(findings, principles)
    style_guide = await functor.codify(vision)
    brand = await functor.brand(vision, "kgents", "Agents with taste")

See: spec/s-gents/studio.md
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from services.studio.types import (
    ArchaeologicalFindings,
    BrandIdentity,
    ColorPalette,
    CreativeVision,
    DesignPrinciple,
    IconographySpec,
    MotionSpec,
    StyleExample,
    StyleGuide,
    StyleRule,
    ToneSpec,
    TypographySpec,
)

if TYPE_CHECKING:
    from agents.k.llm import LLMClient, LLMResponse

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# LLM Client Protocol
# -----------------------------------------------------------------------------


@runtime_checkable
class LLMClientProtocol(Protocol):
    """Protocol for LLM clients compatible with vision functor."""

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Any:
        """Generate a response from the LLM."""
        ...


# -----------------------------------------------------------------------------
# Prompt Templates
# -----------------------------------------------------------------------------

KGENTS_VOICE = """You are a creative director for kgents, an agent framework with a distinct aesthetic philosophy:

CORE PRINCIPLES (quote these, don't paraphrase):
- "Daring, bold, creative, opinionated but not gaudy"
- "Tasteful > feature-complete; Joy-inducing > merely functional"
- "The persona is a garden, not a museum"
- "Depth over breadth"

THE MIRROR TEST: Does this feel like Kent on his best day?

ANTI-SAUSAGE PROTOCOL: Preserve rough edges. Don't smooth what should stay rough.
Don't add safe, generic choices. Be opinionated."""


VISION_SYNTHESIS_PROMPT = """You are synthesizing a creative vision from archaeological findings and design principles.

ARCHAEOLOGICAL FINDINGS:
{findings}

DESIGN PRINCIPLES:
{principles}

YOUR TASK: Generate a unified creative vision that:
1. Captures the essence of the findings in a single, memorable insight
2. Defines concrete aesthetic specifications (colors, typography, motion, tone)
3. Stays daring and opinionated - NOT safe and generic

OUTPUT FORMAT (JSON):
{{
  "core_insight": "One sentence that captures the essence - make it memorable and bold",
  "color_palette": {{
    "primary": "#hex - primary color with semantic meaning",
    "secondary": "#hex - secondary color",
    "accent": "#hex - accent for emphasis",
    "background": "#hex - background color",
    "foreground": "#hex - text color",
    "semantic": {{
      "success": "#hex",
      "warning": "#hex",
      "danger": "#hex",
      "info": "#hex"
    }}
  }},
  "typography": {{
    "heading_font": "Font family for headings (be specific, opinionated)",
    "body_font": "Font family for body text",
    "mono_font": "Font family for code",
    "scale": 1.25,
    "base_size": 16
  }},
  "motion": {{
    "timing_function": "CSS timing function or named preset",
    "duration_scale": 1.0,
    "easing": "default easing curve",
    "entrance_duration_ms": 200,
    "exit_duration_ms": 150,
    "emphasis_duration_ms": 300,
    "philosophy": "How should motion FEEL? Describe the personality."
  }},
  "tone": {{
    "voice": "Overall voice description - be specific",
    "personality": "Personality traits - be bold",
    "keywords": ["list", "of", "keywords"],
    "avoid": ["words", "tones", "to", "avoid"]
  }},
  "iconography": {{
    "style": "outlined|filled|dual-tone",
    "stroke_width": 2.0,
    "corner_radius": 0.0,
    "grid_size": 24
  }},
  "rationale": "Why this vision? Explain the creative reasoning."
}}

Remember: Tasteful > feature-complete. Joy-inducing > merely functional.
Be OPINIONATED. This should feel like Kent on his best day.

Return ONLY valid JSON, no markdown code blocks."""


CRITIQUE_PROMPT = """You are conducting a Three Voices critique of a creative vision.

VISION TO CRITIQUE:
{vision}

APPLY THREE VOICES:

1. ADVERSARIAL VOICE (Technical Coherence):
   - Do the colors have sufficient contrast for accessibility?
   - Does the typography scale work mathematically?
   - Are the motion timings technically sound?
   - Any internal contradictions?

2. CREATIVE VOICE (Novelty & Interest):
   - Is this vision interesting and novel?
   - Does it avoid cliches and generic choices?
   - Would this stand out or blend in?
   - Is there creative tension?

3. ADVOCATE VOICE (Kent's Delight):
   - Does this feel "daring, bold, creative, opinionated but not gaudy"?
   - Is it "tasteful > feature-complete"?
   - Would Kent be delighted or disappointed?
   - Does it pass the Mirror Test?

OUTPUT FORMAT:
{{
  "overall_score": 0.0-1.0,
  "adversarial": {{
    "score": 0.0-1.0,
    "issues": ["list of technical issues"],
    "strengths": ["list of technical strengths"]
  }},
  "creative": {{
    "score": 0.0-1.0,
    "issues": ["list of creative issues"],
    "strengths": ["list of creative strengths"]
  }},
  "advocate": {{
    "score": 0.0-1.0,
    "issues": ["issues from Kent's perspective"],
    "strengths": ["strengths from Kent's perspective"]
  }},
  "critique_summary": "Overall assessment in 2-3 sentences",
  "improvement_suggestions": ["specific", "actionable", "improvements"]
}}

Be honest and critical. Safe visions score lower on creative and advocate voices.

Return ONLY valid JSON."""


REFINE_PROMPT = """You are refining a creative vision based on critique feedback.

ORIGINAL VISION:
{vision}

CRITIQUE:
{critique}

YOUR TASK: Apply the critique to improve the vision while:
1. Preserving what's working (strengths identified in critique)
2. Fixing specific issues raised
3. Making bold improvements, not safe retreats
4. Keeping the core insight if it's strong, enhancing if weak

OUTPUT: Return the refined vision in the SAME JSON format as the original.
Include a "refinement_notes" field explaining what you changed and why.

Remember: Don't smooth rough edges that should stay rough. Be MORE opinionated, not less.

Return ONLY valid JSON."""


CODIFY_PROMPT = """You are transforming a creative vision into actionable style guide rules.

CREATIVE VISION:
{vision}

YOUR TASK: Generate concrete rules with rationale and examples.

OUTPUT FORMAT (JSON):
{{
  "rules": [
    {{
      "category": "color|typography|motion|tone|iconography",
      "rule": "Specific, actionable rule statement",
      "rationale": "Why this rule? Connect to the vision."
    }}
  ],
  "examples": [
    {{
      "title": "Example title",
      "description": "What this example demonstrates",
      "do_example": "Correct implementation",
      "dont_example": "What to avoid"
    }}
  ]
}}

RULES SHOULD BE:
- Specific enough to follow without interpretation
- Connected to the vision's core insight
- Opinionated (avoid "it depends" rules)

EXAMPLES SHOULD:
- Illustrate the difference between following and breaking the rule
- Be concrete and actionable
- Show the vision's personality in action

Return ONLY valid JSON."""


BRAND_PROMPT = """You are creating a brand identity from a creative vision.

CREATIVE VISION:
{vision}

BRAND NAME: {name}
{tagline_instruction}

YOUR TASK: Transform the vision into a complete brand identity.

OUTPUT FORMAT (JSON):
{{
  "tagline": "Brand tagline - memorable, distinctive, captures essence",
  "voice": "Complete voice description - how the brand speaks",
  "personality": "Brand personality - specific traits and characteristics",
  "values": ["list", "of", "core", "values"],
  "logo_guidelines": "Conceptual guidelines for logo design - be specific about:
    - What shapes/symbols would embody the brand
    - Color treatment
    - Typography treatment
    - What to avoid"
}}

Remember: The brand should feel "daring, bold, creative, opinionated but not gaudy."
Make choices that surprise but don't confuse.

Return ONLY valid JSON."""


# -----------------------------------------------------------------------------
# LLM Vision Functor
# -----------------------------------------------------------------------------


@dataclass
class LLMVisionFunctor:
    """
    LLM-powered creative vision synthesis.

    Uses liberal token budget for high-quality generation.
    Implements iterative refinement with self-critique.

    The functor is the mathematical morphism: Findings x Principles -> Vision

    Three operations:
    - synthesize: Generate vision from findings + principles
    - codify: Transform vision into style guide
    - brand: Transform vision into brand identity
    """

    llm: LLMClientProtocol
    max_iterations: int = 3
    coherence_threshold: float = 0.75
    temperature: float = 0.7
    max_tokens: int = 8000

    # Metrics tracking
    _synthesis_count: int = field(default=0, repr=False)
    _total_iterations: int = field(default=0, repr=False)

    async def synthesize(
        self,
        findings: ArchaeologicalFindings,
        principles: list[DesignPrinciple],
    ) -> CreativeVision:
        """
        Generate unified creative vision from findings + principles.

        Process:
        1. Summarize key patterns from findings
        2. Apply principles as constraints
        3. Generate vision components:
           - core_insight (one sentence)
           - color_palette (5-8 colors with semantic meaning)
           - typography (fonts, scale, hierarchy)
           - motion (timing, easing, philosophy)
           - tone (voice, personality, keywords)
        4. Self-critique for coherence
        5. Iterate until coherent (max 3 iterations)

        Args:
            findings: Archaeological findings with patterns and provenance
            principles: Design principles to apply as constraints

        Returns:
            CreativeVision representing the synthesized vision
        """
        logger.info(
            f"synthesize: Starting with {len(findings.patterns)} patterns, "
            f"{len(principles)} principles"
        )

        self._synthesis_count += 1

        # Format findings for prompt
        findings_text = self._format_findings(findings)
        principles_text = self._format_principles(principles)

        # Initial synthesis
        vision = await self._generate_vision(findings_text, principles_text)

        # Iterative refinement with self-critique
        for iteration in range(self.max_iterations):
            self._total_iterations += 1

            # Critique current vision
            score, critique = await self._critique_vision(vision)

            logger.info(
                f"synthesize: Iteration {iteration + 1}/{self.max_iterations}, score={score:.2f}"
            )

            if score >= self.coherence_threshold:
                logger.info(f"synthesize: Vision coherent at score {score:.2f}")
                break

            # Refine based on critique
            vision = await self._refine_vision(vision, critique)

        # Add principles to vision
        principle_stmts = tuple(p.statement for p in principles)
        vision = CreativeVision(
            core_insight=vision.core_insight,
            color_palette=vision.color_palette,
            typography=vision.typography,
            motion=vision.motion,
            tone=vision.tone,
            iconography=vision.iconography,
            principles=principle_stmts,
            timestamp=datetime.now(UTC),
        )

        logger.info(f"synthesize: Complete with insight: {vision.core_insight[:50]}...")
        return vision

    async def codify(self, vision: CreativeVision) -> StyleGuide:
        """
        Transform vision into actionable style guide.

        Generate:
        - Rules with rationale (why this constraint)
        - Do/Don't examples for each rule
        - Reference to vision for context

        Args:
            vision: Creative vision to codify

        Returns:
            StyleGuide with concrete rules and examples
        """
        logger.info("codify: Transforming vision to style guide")

        vision_json = json.dumps(vision.to_dict(), indent=2)

        prompt = CODIFY_PROMPT.format(vision=vision_json)

        response = await self.llm.generate(
            system=KGENTS_VOICE,
            user=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        data = self._parse_json_response(response.text)

        # Parse rules
        rules = tuple(
            StyleRule(
                category=r.get("category", ""),
                rule=r.get("rule", ""),
                rationale=r.get("rationale", ""),
            )
            for r in data.get("rules", [])
        )

        # Parse examples
        examples = tuple(
            StyleExample(
                title=e.get("title", ""),
                description=e.get("description", ""),
                do_example=e.get("do_example", ""),
                dont_example=e.get("dont_example", ""),
            )
            for e in data.get("examples", [])
        )

        style_guide = StyleGuide(
            vision=vision,
            rules=rules,
            examples=examples,
        )

        logger.info(f"codify: Generated {len(rules)} rules, {len(examples)} examples")
        return style_guide

    async def brand(
        self,
        vision: CreativeVision,
        name: str,
        tagline: str | None = None,
    ) -> BrandIdentity:
        """
        Transform vision into brand identity.

        Generate:
        - Tagline if not provided
        - Voice description
        - Personality traits
        - Core values
        - Logo guidelines (conceptual)

        Args:
            vision: Creative vision to transform
            name: Brand name
            tagline: Brand tagline (generated if not provided)

        Returns:
            BrandIdentity with complete brand specifications
        """
        logger.info(f"brand: Creating brand identity for '{name}'")

        vision_json = json.dumps(vision.to_dict(), indent=2)

        tagline_instruction = (
            f"EXISTING TAGLINE: {tagline} (enhance but preserve)"
            if tagline
            else "GENERATE TAGLINE: Create something memorable and distinctive"
        )

        prompt = BRAND_PROMPT.format(
            vision=vision_json,
            name=name,
            tagline_instruction=tagline_instruction,
        )

        response = await self.llm.generate(
            system=KGENTS_VOICE,
            user=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        data = self._parse_json_response(response.text)

        brand = BrandIdentity(
            name=name,
            tagline=tagline or data.get("tagline", f"{name} - vision realized"),
            colors=(
                vision.color_palette.primary,
                vision.color_palette.secondary,
                vision.color_palette.accent,
            ),
            fonts=(
                vision.typography.heading_font,
                vision.typography.body_font,
            ),
            voice=data.get("voice", vision.tone.voice),
            personality=data.get("personality", vision.tone.personality),
            values=tuple(data.get("values", [])),
            logo_guidelines=data.get("logo_guidelines", ""),
        )

        logger.info(f"brand: Created brand identity '{name}'")
        return brand

    async def _critique_vision(self, vision: CreativeVision) -> tuple[float, str]:
        """
        Self-critique using the Three Voices pattern.

        - Adversarial: Is it technically coherent?
        - Creative: Is it interesting and novel?
        - Advocate: Would Kent be delighted?

        Returns:
            Tuple of (score, critique_text) where score is 0-1
        """
        vision_json = json.dumps(vision.to_dict(), indent=2)

        prompt = CRITIQUE_PROMPT.format(vision=vision_json)

        response = await self.llm.generate(
            system=KGENTS_VOICE,
            user=prompt,
            temperature=0.3,  # Lower temperature for consistent critique
            max_tokens=4000,
        )

        data = self._parse_json_response(response.text)

        score = data.get("overall_score", 0.5)
        critique = json.dumps(data, indent=2)

        return score, critique

    async def _refine_vision(
        self,
        vision: CreativeVision,
        critique: str,
    ) -> CreativeVision:
        """
        Apply critique to improve vision.

        Uses TextGRAD-like feedback:
        - Parse critique into specific improvements
        - Apply improvements to vision components
        - Preserve what's working, fix what's not

        Args:
            vision: Current vision to refine
            critique: Critique text from self-critique

        Returns:
            Refined CreativeVision
        """
        vision_json = json.dumps(vision.to_dict(), indent=2)

        prompt = REFINE_PROMPT.format(
            vision=vision_json,
            critique=critique,
        )

        response = await self.llm.generate(
            system=KGENTS_VOICE,
            user=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        data = self._parse_json_response(response.text)

        return self._parse_vision_data(data)

    async def _generate_vision(
        self,
        findings_text: str,
        principles_text: str,
    ) -> CreativeVision:
        """Generate initial vision from findings and principles."""
        prompt = VISION_SYNTHESIS_PROMPT.format(
            findings=findings_text,
            principles=principles_text,
        )

        response = await self.llm.generate(
            system=KGENTS_VOICE,
            user=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        data = self._parse_json_response(response.text)

        return self._parse_vision_data(data)

    def _format_findings(self, findings: ArchaeologicalFindings) -> str:
        """Format findings for inclusion in prompts."""
        lines = [
            f"Sources Analyzed: {findings.sources_analyzed}",
            f"Focus: {findings.focus_used.value if findings.focus_used else 'none'}",
            "",
            "Patterns Found:",
        ]

        for pattern in findings.patterns:
            confidence_bar = "*" * int(pattern.confidence * 10)
            lines.append(
                f"  - [{pattern.name}] {pattern.description} "
                f"(confidence: {confidence_bar} {pattern.confidence:.0%})"
            )

        return "\n".join(lines)

    def _format_principles(self, principles: list[DesignPrinciple]) -> str:
        """Format principles for inclusion in prompts."""
        lines = ["Design Principles (in priority order):", ""]

        for i, p in enumerate(principles, 1):
            lines.append(f"  {i}. {p.statement}")
            if p.rationale:
                lines.append(f"     Rationale: {p.rationale}")

        return "\n".join(lines)

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """Parse JSON from LLM response, handling common quirks."""
        response = response.strip()

        # Try raw JSON first
        if response.startswith("{") and response.endswith("}"):
            try:
                result: dict[str, Any] = json.loads(response)
                return result
            except json.JSONDecodeError:
                pass

        # Try markdown code block
        code_block_patterns = [
            r"```json\s*\n?(.*?)\n?```",
            r"```\s*\n?(.*?)\n?```",
        ]

        for pattern in code_block_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                extracted = match.group(1).strip()
                try:
                    result = json.loads(extracted)
                    return result
                except json.JSONDecodeError:
                    continue

        # Try to find JSON object in the response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(0))
                return result
            except json.JSONDecodeError:
                pass

        # Last resort: return empty dict with error logged
        logger.warning(f"Failed to parse JSON response: {response[:200]}...")
        return {}

    def _parse_vision_data(self, data: dict[str, Any]) -> CreativeVision:
        """Parse vision data dict into CreativeVision object."""
        # Parse color palette
        cp_data = data.get("color_palette", {})
        color_palette = ColorPalette(
            primary=cp_data.get("primary", "#1a1a2e"),
            secondary=cp_data.get("secondary", "#16213e"),
            accent=cp_data.get("accent", "#0f3460"),
            semantic=cp_data.get("semantic", {}),
            background=cp_data.get("background", "#ffffff"),
            foreground=cp_data.get("foreground", "#000000"),
        )

        # Parse typography
        typo_data = data.get("typography", {})
        typography = TypographySpec(
            heading_font=typo_data.get("heading_font", "Inter"),
            body_font=typo_data.get("body_font", "Inter"),
            mono_font=typo_data.get("mono_font", "JetBrains Mono"),
            scale=typo_data.get("scale", 1.25),
            base_size=typo_data.get("base_size", 16),
        )

        # Parse motion
        motion_data = data.get("motion", {})
        motion = MotionSpec(
            timing_function=motion_data.get("timing_function", "ease-out"),
            duration_scale=motion_data.get("duration_scale", 1.0),
            easing=motion_data.get("easing", "ease-out"),
            entrance_duration_ms=motion_data.get("entrance_duration_ms", 200),
            exit_duration_ms=motion_data.get("exit_duration_ms", 150),
            emphasis_duration_ms=motion_data.get("emphasis_duration_ms", 300),
        )

        # Parse tone
        tone_data = data.get("tone", {})
        tone = ToneSpec(
            voice=tone_data.get("voice", ""),
            personality=tone_data.get("personality", ""),
            keywords=tuple(tone_data.get("keywords", [])),
            avoid=tuple(tone_data.get("avoid", [])),
        )

        # Parse iconography (optional)
        icon_data = data.get("iconography")
        iconography = None
        if icon_data:
            iconography = IconographySpec(
                style=icon_data.get("style", "outlined"),
                stroke_width=icon_data.get("stroke_width", 2.0),
                corner_radius=icon_data.get("corner_radius", 0.0),
                grid_size=icon_data.get("grid_size", 24),
            )

        return CreativeVision(
            core_insight=data.get("core_insight", "Vision synthesis in progress"),
            color_palette=color_palette,
            typography=typography,
            motion=motion,
            tone=tone,
            iconography=iconography,
            principles=(),  # Filled in by synthesize()
            timestamp=datetime.now(UTC),
        )

    def get_metrics(self) -> dict[str, Any]:
        """Get synthesis metrics."""
        avg_iterations = (
            self._total_iterations / self._synthesis_count if self._synthesis_count > 0 else 0
        )
        return {
            "synthesis_count": self._synthesis_count,
            "total_iterations": self._total_iterations,
            "average_iterations": avg_iterations,
        }


# -----------------------------------------------------------------------------
# Factory Functions
# -----------------------------------------------------------------------------


def create_vision_functor(
    llm: LLMClientProtocol | None = None,
    max_iterations: int = 3,
    coherence_threshold: float = 0.75,
) -> LLMVisionFunctor:
    """
    Create a configured LLMVisionFunctor.

    Args:
        llm: LLM client (auto-creates if None)
        max_iterations: Maximum refinement iterations
        coherence_threshold: Minimum score to accept vision

    Returns:
        Configured LLMVisionFunctor instance
    """
    if llm is None:
        from agents.k.llm import create_llm_client

        llm = create_llm_client()

    return LLMVisionFunctor(
        llm=llm,
        max_iterations=max_iterations,
        coherence_threshold=coherence_threshold,
    )


__all__ = [
    "LLMVisionFunctor",
    "LLMClientProtocol",
    "create_vision_functor",
    # Prompt templates (for customization)
    "KGENTS_VOICE",
    "VISION_SYNTHESIS_PROMPT",
    "CRITIQUE_PROMPT",
    "REFINE_PROMPT",
    "CODIFY_PROMPT",
    "BRAND_PROMPT",
]
