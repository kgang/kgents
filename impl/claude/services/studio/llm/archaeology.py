"""
Studio LLM Archaeology: LLM-Powered Aesthetic Pattern Extraction.

> *"Art is not what you see, but what you make others see." - Degas*

The AestheticArchaeologyFunctor uses LLM to extract creative patterns from
raw materials (specs, code, screenshots, inspirations). It implements a
self-feedback loop that iterates until quality thresholds are met.

Process:
    1. Read all source files
    2. Send to LLM with focus-specific prompt
    3. Parse structured response into Pattern objects
    4. Build provenance graph (pattern -> source traceability)
    5. Measure quality using Experience Quality Operad pattern
    6. Iterate if quality < threshold (self-improvement loop)

Token Budget: Liberal (100k input, 10k output per call)
    Creative archaeology benefits from broad context. The cost of missing
    a pattern far exceeds the cost of extra tokens.

Quality via Tetrad:
    - Contrast: Pattern distinctiveness (not too similar to each other)
    - Arc: Narrative coherence (patterns tell a story together)
    - Voice: Authenticity (patterns feel true to source)
    - Floor: Provenance completeness (all patterns trace to sources)

See: spec/s-gents/studio.md Section 2 (Archaeology Functor)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

# Import directly from budgets module to avoid circular imports
# The zero_seed.llm.__init__.py may have broken imports
try:
    from services.zero_seed.llm.budgets import (
        BudgetManager,
        QualityBudget,
        TokenBudget,
    )
except ImportError:
    # Fallback: define minimal budget types inline if import fails
    from dataclasses import dataclass as _dataclass, field as _field
    from typing import Any as _Any

    @_dataclass
    class TokenBudget:  # type: ignore[no-redef]
        """Minimal token budget (fallback)."""

        max_input_per_call: int = 100_000
        max_output_per_call: int = 10_000
        max_session_cumulative: int = 500_000
        cumulative_input: int = _field(default=0, repr=False)
        cumulative_output: int = _field(default=0, repr=False)

        def can_afford(self, estimated_input: int, estimated_output: int) -> bool:
            total = (
                self.cumulative_input + estimated_input + self.cumulative_output + estimated_output
            )
            return total < self.max_session_cumulative

        def charge(self, actual_input: int, actual_output: int) -> None:
            self.cumulative_input += actual_input
            self.cumulative_output += actual_output

        @property
        def remaining(self) -> int:
            return max(
                0, self.max_session_cumulative - self.cumulative_input - self.cumulative_output
            )

        def to_dict(self) -> dict[str, _Any]:
            return {
                "max_input_per_call": self.max_input_per_call,
                "max_output_per_call": self.max_output_per_call,
                "max_session_cumulative": self.max_session_cumulative,
                "cumulative_input": self.cumulative_input,
                "cumulative_output": self.cumulative_output,
                "remaining": self.remaining,
            }

    @_dataclass
    class QualityBudget:  # type: ignore[no-redef]
        """Minimal quality budget (fallback)."""

        def select_model(self, task: str, max_loss: float) -> str:
            if max_loss < 0.10:
                return "claude-opus-4-5-20251101"
            elif max_loss < 0.20:
                return "claude-sonnet-4-20250514"
            return "claude-3-5-haiku-20241022"

    @_dataclass
    class BudgetManager:  # type: ignore[no-redef]
        """Minimal budget manager (fallback)."""

        token: TokenBudget = _field(default_factory=TokenBudget)

        def plan_operation(
            self,
            task: str,
            estimated_input: int,
            estimated_output: int,
            max_loss: float = 0.15,
        ) -> dict[str, _Any]:
            return {"task": task, "model": "claude-sonnet-4-20250514"}

        def record_usage(self, actual_input: int, actual_output: int) -> None:
            self.token.charge(actual_input, actual_output)

        def summary(self) -> dict[str, _Any]:
            return {"token": self.token.to_dict()}


from ..types import (
    ArchaeologicalFindings,
    ArchaeologyFocus,
    Interpretation,
    InterpretationLens,
    InterpretedMeaning,
    Pattern,
    ProvenanceNode,
    Source,
)

if TYPE_CHECKING:
    from agents.k.llm import LLMClient, LLMResponse

logger = logging.getLogger(__name__)


# =============================================================================
# Focus-Specific Prompts
# =============================================================================

# Each focus emphasizes different aspects of the source material.
# The prompts are designed to elicit rich, domain-specific patterns.

FOCUS_PROMPTS: dict[ArchaeologyFocus, str] = {
    ArchaeologyFocus.VISUAL: """You are an aesthetic archaeologist specializing in VISUAL patterns.

Extract visual design patterns from the source materials. Focus on:

1. **Color Relationships**: Color palettes, contrasts, harmonies, temperature shifts
2. **Compositional Structure**: Layout grids, focal points, visual hierarchy, balance
3. **Shape Language**: Geometric vocabulary, organic vs. angular, recurring motifs
4. **Light & Shadow**: Contrast ratios, value distribution, atmospheric depth
5. **Texture & Surface**: Material qualities, tactile implications, visual noise
6. **Rhythm & Repetition**: Visual tempo, pattern breaks, accent moments

For each pattern, provide:
- A descriptive name (e.g., "neon-on-dark-contrast", "triangular-hierarchy")
- Rich description of what makes this pattern distinctive
- Exact source references (file paths, line numbers, timestamps)
- Confidence score (0.0-1.0) based on pattern clarity in source

Look for IMPLICIT patterns too - things the creator may not have consciously designed
but which emerge from the totality of choices.""",
    ArchaeologyFocus.AUDIO: """You are an aesthetic archaeologist specializing in AUDIO patterns.

Extract audio design patterns from the source materials. Focus on:

1. **Tonal Palette**: Key centers, modal flavors, harmonic vocabulary
2. **Rhythm Architecture**: Time signatures, groove patterns, syncopation
3. **Frequency Space**: Bass-mid-treble balance, spectral characteristics
4. **Dynamic Contour**: Loudness curves, compression style, impact moments
5. **Spatial Design**: Stereo width, reverb character, depth placement
6. **Timbral Identity**: Instrument/sound choices, synthesis style, processing chains

For each pattern, provide:
- A descriptive name (e.g., "sub-bass-pulse", "bright-staccato-leads")
- Rich description of the sonic character
- Source references (file paths, timestamps, frequency ranges)
- Confidence score (0.0-1.0)

Include EMOTIONAL patterns - how does the audio make the listener feel?
What tension/release mechanisms are employed?""",
    ArchaeologyFocus.NARRATIVE: """You are an aesthetic archaeologist specializing in NARRATIVE patterns.

Extract narrative and thematic patterns from the source materials. Focus on:

1. **Core Themes**: Central ideas, philosophical underpinnings, recurring motifs
2. **Character Archetypes**: Player personas, NPC types, voice characteristics
3. **Story Structure**: Arc patterns, pacing beats, dramatic tension curves
4. **World Logic**: Rules of the universe, cause-effect relationships
5. **Symbolic System**: Metaphors, allegories, visual/verbal symbolism
6. **Emotional Journey**: Mood progression, cathartic moments, resonance points

For each pattern, provide:
- A descriptive name (e.g., "reluctant-hero-arc", "entropy-as-antagonist")
- Rich description of narrative function
- Source references (spec sections, dialogue examples, story beats)
- Confidence score (0.0-1.0)

Look for SUBTEXT - what is being communicated below the surface?
What assumptions does the narrative make about the audience?""",
    ArchaeologyFocus.MECHANICAL: """You are an aesthetic archaeologist specializing in MECHANICAL/GAMEPLAY patterns.

Extract interaction and gameplay patterns from the source materials. Focus on:

1. **Core Loop**: Primary action-feedback cycle, engagement hooks
2. **Risk/Reward**: Stakes, consequences, payoff moments
3. **Progression Systems**: Leveling, unlocks, mastery curves
4. **Resource Economy**: Currencies, scarcity, exchange rates
5. **Agency Design**: Choice architecture, meaningful decisions, illusion of control
6. **Feedback Loops**: Positive/negative reinforcement, habit formation

For each pattern, provide:
- A descriptive name (e.g., "risk-amplification-on-streak", "scarcity-before-boss")
- Rich description of mechanical purpose
- Source references (code paths, spec sections, formula locations)
- Confidence score (0.0-1.0)

Pay attention to JUICE patterns - the micro-feedback that makes actions feel good.
Screen shake, particle bursts, sound design on impact.""",
    ArchaeologyFocus.EMOTIONAL: """You are an aesthetic archaeologist specializing in EMOTIONAL patterns.

Extract emotional design patterns from the source materials. Focus on:

1. **Mood Architecture**: Baseline emotional tone, intensity modulation
2. **Tension Systems**: Build-up mechanisms, release valves, cliffhangers
3. **Comfort Zones**: Safe spaces, respite moments, sanctuary design
4. **Challenge Calibration**: Frustration management, flow state targeting
5. **Surprise Engineering**: Subverted expectations, discovery moments, easter eggs
6. **Connection Design**: Attachment mechanisms, loss aversion, care triggers

For each pattern, provide:
- A descriptive name (e.g., "safe-haven-contrast", "earned-victory-crescendo")
- Rich description of emotional purpose
- Source references with emotional context
- Confidence score (0.0-1.0)

Focus on the FELT experience - what does it FEEL like to encounter this?
Not just what happens, but how it lands emotionally.""",
}


EXCAVATE_SYSTEM_PROMPT = """You are an Aesthetic Archaeologist - a specialized AI that extracts creative patterns from source materials.

Your role is to discover patterns that:
1. Are DISTINCTIVE - each pattern should be unique, not redundant
2. Are TRACEABLE - every pattern must reference specific sources
3. Are ACTIONABLE - patterns should inform creative decisions
4. Are AUTHENTIC - patterns should feel true to the source material's spirit

You excavate with rigor but interpret with creativity.
You find what's there, but also what's implied.

Return your findings as valid JSON only, no markdown code blocks."""


EXCAVATE_USER_PROMPT = """## ARCHAEOLOGICAL EXCAVATION

### Focus: {focus}

{focus_prompt}

### Sources to Analyze:

{sources}

### Depth Level: {depth}
- Quick (depth=1): Surface patterns only, high confidence
- Standard (depth=3): Balance of breadth and depth
- Deep (depth=5): Exhaustive analysis, including subtle patterns

### Output Format:

Return a JSON object with this exact structure:
{{
    "patterns": [
        {{
            "name": "pattern-name-kebab-case",
            "description": "Rich, detailed description of the pattern...",
            "source_refs": ["path/to/file:line", "path/to/other:section"],
            "confidence": 0.85,
            "metadata": {{"category": "...", "related_to": ["other-pattern"]}}
        }}
    ],
    "provenance": [
        {{
            "pattern_name": "pattern-name-kebab-case",
            "source_path": "path/to/file",
            "location": "line 42-50",
            "extraction_method": "direct_observation"
        }}
    ],
    "summary": "Brief summary of findings",
    "quality_notes": "Self-assessment of excavation quality"
}}

Extract at least 3 patterns, up to 15 for deep excavation.
Every pattern MUST have at least one source reference.
Confidence should reflect how clearly the pattern appears in sources."""


INTERPRET_SYSTEM_PROMPT = """You are an Aesthetic Interpreter - a specialized AI that assigns meaning to extracted patterns.

Your role is to:
1. View patterns through a specific interpretive LENS
2. Assign MEANING that is both insightful and actionable
3. Maintain COHERENCE across interpretations
4. Connect patterns to BROADER aesthetic principles

You interpret with both intellectual rigor and creative intuition."""


INTERPRET_USER_PROMPT = """## PATTERN INTERPRETATION

### Interpretation Lens: {lens}

{lens_description}

### Patterns to Interpret:

{patterns}

### Instructions:

For each pattern, provide an interpretation through the {lens} lens.

Lens-specific guidance:
- SEMIOTIC: What does this pattern SIGNIFY? What cultural codes does it invoke?
- AESTHETIC: What makes this pattern BEAUTIFUL or EFFECTIVE? What taste does it express?
- FUNCTIONAL: What PURPOSE does this pattern serve? How does it solve a problem?
- EMOTIONAL: What FEELINGS does this pattern evoke? What psychological mechanisms?

### Output Format:

Return a JSON object with this exact structure:
{{
    "interpretations": [
        {{
            "pattern_name": "pattern-name",
            "meaning": "Rich interpretation through the lens...",
            "confidence": 0.85
        }}
    ],
    "synthesis": "How these interpretations form a coherent whole",
    "actionable_insights": ["Insight 1", "Insight 2"]
}}

Every pattern must have exactly one interpretation."""


QUALITY_ASSESSMENT_PROMPT = """## QUALITY SELF-ASSESSMENT

Evaluate the quality of these archaeological findings using the Tetrad framework:

### Findings to Assess:

{findings}

### Tetrad Dimensions:

1. **CONTRAST** (Pattern Distinctiveness): Are patterns sufficiently different from each other?
   - Score 0.0 if patterns are redundant/overlapping
   - Score 1.0 if each pattern is unique and non-overlapping

2. **ARC** (Narrative Coherence): Do patterns tell a coherent story together?
   - Score 0.0 if patterns are disconnected fragments
   - Score 1.0 if patterns form a unified aesthetic vision

3. **VOICE** (Authenticity): Do patterns feel true to the source material?
   - Score 0.0 if patterns seem imposed or forced
   - Score 1.0 if patterns emerge naturally from sources

4. **FLOOR** (Provenance Completeness): Is every pattern traceable to sources?
   - Score 0.0 if patterns lack source references
   - Score 1.0 if every pattern has clear provenance

### Output Format:

Return a JSON object with this exact structure:
{{
    "contrast_score": 0.85,
    "arc_score": 0.80,
    "voice_score": 0.90,
    "floor_score": 0.75,
    "overall_score": 0.825,
    "critique": "What could be improved...",
    "suggestions": ["Specific improvement 1", "Specific improvement 2"]
}}"""


CRITIQUE_PROMPT = """## FINDINGS CRITIQUE

The following archaeological findings scored {score:.2f} quality, below the {threshold:.2f} threshold.

### Current Findings:

{findings}

### Quality Assessment:

{assessment}

### Task:

Provide specific, actionable improvements to these findings:

1. Identify WHICH patterns need improvement
2. Explain HOW to improve them
3. Suggest NEW patterns that may have been missed
4. Recommend patterns to REMOVE if redundant

### Output Format:

Return a JSON object with this exact structure:
{{
    "patterns_to_improve": [
        {{"name": "pattern-name", "issue": "What's wrong", "fix": "How to fix"}}
    ],
    "patterns_to_remove": ["redundant-pattern-name"],
    "patterns_to_add": [
        {{"name": "suggested-pattern", "description": "Why this pattern exists", "likely_sources": ["hint"]}}
    ],
    "reframing": "Alternative way to understand the source material"
}}"""


# =============================================================================
# Lens Descriptions
# =============================================================================

LENS_DESCRIPTIONS: dict[InterpretationLens, str] = {
    InterpretationLens.SEMIOTIC: """The SEMIOTIC lens views patterns as SIGNS within a system of meaning.

Consider:
- What does this pattern SIGNIFY beyond its literal appearance?
- What CODES or CONVENTIONS does it reference?
- What cultural, genre, or historical context gives it meaning?
- How does it relate to the system of other signs in the work?

Semiotic interpretation reveals the language being spoken.""",
    InterpretationLens.AESTHETIC: """The AESTHETIC lens views patterns through the lens of BEAUTY and TASTE.

Consider:
- What makes this pattern aesthetically EFFECTIVE or PLEASING?
- What PRINCIPLES of design does it embody (harmony, contrast, rhythm)?
- What TASTE or STYLE does it express?
- How does it contribute to the overall aesthetic UNITY?

Aesthetic interpretation reveals the craft and intentionality.""",
    InterpretationLens.FUNCTIONAL: """The FUNCTIONAL lens views patterns through the lens of PURPOSE and UTILITY.

Consider:
- What PROBLEM does this pattern solve?
- What USER NEED does it address?
- How does it contribute to the work's GOALS?
- What would be LOST if this pattern were removed?

Functional interpretation reveals the design intelligence.""",
    InterpretationLens.EMOTIONAL: """The EMOTIONAL lens views patterns through the lens of FEELING and PSYCHOLOGY.

Consider:
- What EMOTIONS does this pattern evoke?
- What PSYCHOLOGICAL mechanisms does it engage (curiosity, fear, satisfaction)?
- How does it affect the FELT experience of the work?
- What MEMORIES or ASSOCIATIONS does it trigger?

Emotional interpretation reveals the affective design.""",
}


# =============================================================================
# LLM Client Protocol
# =============================================================================


@runtime_checkable
class LLMClientProtocol(Protocol):
    """Protocol for LLM clients compatible with archaeology functor."""

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Any:
        """Generate a response from the LLM."""
        ...


# =============================================================================
# Quality Assessment Result
# =============================================================================


@dataclass(frozen=True)
class QualityAssessment:
    """Result of self-assessing archaeological findings quality."""

    contrast_score: float  # Pattern distinctiveness
    arc_score: float  # Narrative coherence
    voice_score: float  # Authenticity to source
    floor_score: float  # Provenance completeness
    overall_score: float
    critique: str
    suggestions: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QualityAssessment:
        """Create from dictionary."""
        return cls(
            contrast_score=data.get("contrast_score", 0.0),
            arc_score=data.get("arc_score", 0.0),
            voice_score=data.get("voice_score", 0.0),
            floor_score=data.get("floor_score", 0.0),
            overall_score=data.get("overall_score", 0.0),
            critique=data.get("critique", ""),
            suggestions=tuple(data.get("suggestions", [])),
        )


# =============================================================================
# LLM Archaeology Functor
# =============================================================================


@dataclass
class LLMArchaeologyFunctor:
    """
    LLM-powered pattern extraction from raw materials.

    Uses liberal token budget (100k input, 10k output per call).
    Implements self-feedback loop with quality measurement.

    The functor maps: Sources x Focus -> Findings
    With interpretation: Findings x Lens -> InterpretedMeaning

    Philosophy:
        Archaeology is not just finding patterns - it's finding the RIGHT patterns.
        Quality matters more than quantity. The self-feedback loop ensures we don't
        stop at the first acceptable result but push toward excellence.

    Usage:
        from agents.k.llm import create_llm_client

        llm = create_llm_client()
        archaeology = LLMArchaeologyFunctor(llm)

        # Excavate patterns from sources
        findings = await archaeology.excavate(
            sources=[Source(path="spec/game.md", type=SourceType.SPEC)],
            focus=ArchaeologyFocus.VISUAL,
            depth=3,
        )

        # Interpret findings through a lens
        meaning = await archaeology.interpret(
            findings,
            lens=InterpretationLens.AESTHETIC,
        )
    """

    llm: LLMClientProtocol
    budget: BudgetManager = field(
        default_factory=lambda: BudgetManager(
            token=TokenBudget(
                max_input_per_call=100_000,  # Liberal: full context window
                max_output_per_call=10_000,  # Rich output
                max_session_cumulative=500_000,  # Multiple excavations
            )
        )
    )
    quality_threshold: float = 0.8
    max_iterations: int = 3
    cache_enabled: bool = True

    # Cache for findings (expensive operations)
    _findings_cache: dict[tuple[str, ...], ArchaeologicalFindings] = field(
        default_factory=dict, repr=False
    )

    def __post_init__(self) -> None:
        """Initialize quality budget for model selection."""
        self._quality_budget = QualityBudget()

    def select_model(self, task: str) -> str:
        """Select model based on task requirements.

        Args:
            task: One of "excavate", "interpret", "quality", "critique"

        Returns:
            Model name for the task
        """
        # Task-specific loss tolerances
        # Archaeology benefits from smarter models - patterns are subtle
        tolerances = {
            "excavate": 0.10,  # High fidelity for pattern extraction
            "interpret": 0.15,  # Can tolerate some variation
            "quality": 0.20,  # Assessment is less critical
            "critique": 0.15,  # Need good critique
        }

        max_loss = tolerances.get(task, 0.15)
        return self._quality_budget.select_model(task, max_loss)

    async def excavate(
        self,
        sources: list[Source],
        focus: ArchaeologyFocus,
        depth: int = 3,
    ) -> ArchaeologicalFindings:
        """
        Extract patterns from sources using LLM.

        Process:
        1. Read all source files (if content not cached)
        2. Send to LLM with focus-specific prompt
        3. Parse structured response into Pattern objects
        4. Build provenance graph
        5. Measure quality and iterate if below threshold

        Args:
            sources: List of Source objects to analyze
            focus: What aspect to focus on (VISUAL, AUDIO, etc.)
            depth: Excavation depth (1=quick, 3=standard, 5=deep)

        Returns:
            ArchaeologicalFindings with patterns and provenance

        Raises:
            TokenBudgetExceeded: If budget is exhausted
        """
        # Check cache
        cache_key = tuple(s.path for s in sources) + (focus.value, str(depth))
        if self.cache_enabled and cache_key in self._findings_cache:
            logger.info(f"Cache hit for excavation: {cache_key[:3]}...")
            return self._findings_cache[cache_key]

        # Load source content
        sources_with_content = await self._load_sources(sources)

        # Format sources for prompt
        sources_text = self._format_sources(sources_with_content)

        # Get focus-specific prompt
        focus_prompt = FOCUS_PROMPTS.get(focus, FOCUS_PROMPTS[ArchaeologyFocus.VISUAL])

        # Estimate tokens
        estimated_input = len(sources_text) // 4 + len(focus_prompt) // 4 + 1000
        estimated_output = 3000 * depth  # More output for deeper excavation

        # Check budget
        self.budget.plan_operation(
            task="excavate",
            estimated_input=estimated_input,
            estimated_output=estimated_output,
            max_loss=0.10,
        )

        # Build prompt
        user_prompt = EXCAVATE_USER_PROMPT.format(
            focus=focus.value.upper(),
            focus_prompt=focus_prompt,
            sources=sources_text,
            depth=depth,
        )

        logger.info(f"Excavating {len(sources)} sources with {focus.value} focus, depth={depth}")

        # Call LLM
        response = await self.llm.generate(
            system=EXCAVATE_SYSTEM_PROMPT,
            user=user_prompt,
            temperature=0.3,  # Some creativity but not too wild
            max_tokens=10_000,
        )

        # Record usage
        self.budget.record_usage(
            actual_input=estimated_input,
            actual_output=len(response.text) // 4,
        )

        # Parse response
        findings = self._parse_excavation_response(response.text, focus, len(sources))

        # Measure quality and iterate if needed
        findings = await self._iterate_if_needed(findings)

        # Cache result
        if self.cache_enabled:
            self._findings_cache[cache_key] = findings

        logger.info(f"Excavation complete: {len(findings.patterns)} patterns found")
        return findings

    async def interpret(
        self,
        findings: ArchaeologicalFindings,
        lens: InterpretationLens,
    ) -> InterpretedMeaning:
        """
        Assign meaning through interpretation lens.

        Uses multi-turn dialogue:
        1. Present findings
        2. Ask for interpretation through lens
        3. Validate coherence
        4. Iterate if quality < 0.8

        Args:
            findings: Archaeological findings to interpret
            lens: Interpretation lens to use

        Returns:
            InterpretedMeaning with interpretations for each pattern
        """
        if not findings.patterns:
            return InterpretedMeaning(
                findings=findings,
                lens=lens,
                interpretations=(),
            )

        # Format patterns for prompt
        patterns_text = self._format_patterns(findings.patterns)

        # Get lens description
        lens_desc = LENS_DESCRIPTIONS.get(lens, LENS_DESCRIPTIONS[InterpretationLens.AESTHETIC])

        # Estimate tokens
        estimated_input = len(patterns_text) // 4 + len(lens_desc) // 4 + 500
        estimated_output = len(findings.patterns) * 300  # ~300 tokens per interpretation

        # Check budget
        self.budget.plan_operation(
            task="interpret",
            estimated_input=estimated_input,
            estimated_output=estimated_output,
            max_loss=0.15,
        )

        # Build prompt
        user_prompt = INTERPRET_USER_PROMPT.format(
            lens=lens.value.upper(),
            lens_description=lens_desc,
            patterns=patterns_text,
        )

        logger.info(f"Interpreting {len(findings.patterns)} patterns through {lens.value} lens")

        # Call LLM
        response = await self.llm.generate(
            system=INTERPRET_SYSTEM_PROMPT,
            user=user_prompt,
            temperature=0.4,  # More creativity for interpretation
            max_tokens=5_000,
        )

        # Record usage
        self.budget.record_usage(
            actual_input=estimated_input,
            actual_output=len(response.text) // 4,
        )

        # Parse response
        return self._parse_interpretation_response(response.text, findings, lens)

    async def _measure_quality(self, findings: ArchaeologicalFindings) -> QualityAssessment:
        """
        Self-assess quality using Experience Quality Operad pattern.

        Checks:
        - Contrast: Pattern distinctiveness (not too similar)
        - Arc: Narrative coherence (patterns form a story)
        - Voice: Authenticity (patterns feel true to source)
        - Floor: Provenance completeness (all patterns traced)

        Args:
            findings: Findings to assess

        Returns:
            QualityAssessment with scores and critique
        """
        if not findings.patterns:
            return QualityAssessment(
                contrast_score=1.0,
                arc_score=1.0,
                voice_score=1.0,
                floor_score=1.0,
                overall_score=1.0,
                critique="No patterns to assess",
                suggestions=(),
            )

        # Format findings for assessment
        findings_text = self._format_findings_for_assessment(findings)

        # Estimate tokens
        estimated_input = len(findings_text) // 4 + 500
        estimated_output = 500

        # Check budget
        self.budget.plan_operation(
            task="quality",
            estimated_input=estimated_input,
            estimated_output=estimated_output,
            max_loss=0.20,
        )

        # Build prompt
        user_prompt = QUALITY_ASSESSMENT_PROMPT.format(findings=findings_text)

        logger.info(f"Assessing quality of {len(findings.patterns)} patterns")

        # Call LLM
        response = await self.llm.generate(
            system="You are a quality assessor for archaeological findings. Be rigorous but fair.",
            user=user_prompt,
            temperature=0.1,  # Low temp for consistent assessment
            max_tokens=1_000,
        )

        # Record usage
        self.budget.record_usage(
            actual_input=estimated_input,
            actual_output=len(response.text) // 4,
        )

        # Parse response
        return self._parse_quality_response(response.text)

    async def _iterate_if_needed(
        self,
        findings: ArchaeologicalFindings,
        threshold: float | None = None,
        max_iterations: int | None = None,
    ) -> ArchaeologicalFindings:
        """
        Self-improvement loop.

        If quality < threshold:
        1. Ask LLM to critique findings
        2. Apply critique to improve
        3. Re-measure quality
        4. Repeat until threshold met or max iterations

        Args:
            findings: Current findings
            threshold: Quality threshold (default: self.quality_threshold)
            max_iterations: Max improvement iterations (default: self.max_iterations)

        Returns:
            Improved findings
        """
        threshold = threshold or self.quality_threshold
        max_iterations = max_iterations or self.max_iterations

        for iteration in range(max_iterations):
            # Measure quality
            assessment = await self._measure_quality(findings)
            quality = assessment.overall_score

            logger.info(
                f"Quality iteration {iteration + 1}: score={quality:.3f}, threshold={threshold:.3f}"
            )

            if quality >= threshold:
                logger.info(f"Quality threshold met at iteration {iteration + 1}")
                return findings

            # Get critique
            critique = await self._get_critique(findings, assessment)

            # Apply critique to improve findings
            findings = self._apply_critique(findings, critique)

        logger.warning(f"Quality threshold not met after {max_iterations} iterations")
        return findings

    async def _get_critique(
        self,
        findings: ArchaeologicalFindings,
        assessment: QualityAssessment,
    ) -> dict[str, Any]:
        """Get LLM critique of findings for improvement."""
        findings_text = self._format_findings_for_assessment(findings)
        assessment_text = f"""
Scores:
- Contrast: {assessment.contrast_score:.2f}
- Arc: {assessment.arc_score:.2f}
- Voice: {assessment.voice_score:.2f}
- Floor: {assessment.floor_score:.2f}
- Overall: {assessment.overall_score:.2f}

Critique: {assessment.critique}

Suggestions:
{chr(10).join(f"- {s}" for s in assessment.suggestions)}
"""

        # Build prompt
        user_prompt = CRITIQUE_PROMPT.format(
            score=assessment.overall_score,
            threshold=self.quality_threshold,
            findings=findings_text,
            assessment=assessment_text,
        )

        # Call LLM
        response = await self.llm.generate(
            system="You are a rigorous critic helping improve archaeological findings. Be specific and actionable.",
            user=user_prompt,
            temperature=0.2,
            max_tokens=2_000,
        )

        # Record usage
        self.budget.record_usage(
            actual_input=len(user_prompt) // 4,
            actual_output=len(response.text) // 4,
        )

        # Parse critique
        return self._parse_critique_response(response.text)

    def _apply_critique(
        self,
        findings: ArchaeologicalFindings,
        critique: dict[str, Any],
    ) -> ArchaeologicalFindings:
        """Apply critique to improve findings."""
        patterns = list(findings.patterns)
        provenance = list(findings.provenance)

        # Remove redundant patterns
        patterns_to_remove = set(critique.get("patterns_to_remove", []))
        patterns = [p for p in patterns if p.name not in patterns_to_remove]

        # Apply improvements to existing patterns
        for improvement in critique.get("patterns_to_improve", []):
            pattern_name = improvement.get("name")
            fix = improvement.get("fix", "")

            for i, pattern in enumerate(patterns):
                if pattern.name == pattern_name and fix:
                    # Update pattern with improved description
                    patterns[i] = Pattern(
                        name=pattern.name,
                        description=f"{pattern.description}\n\n[Improved: {fix}]",
                        source_refs=pattern.source_refs,
                        confidence=pattern.confidence,
                        focus=pattern.focus,
                        metadata=pattern.metadata,
                    )

        # Add suggested new patterns (with lower confidence since they're inferred)
        for suggestion in critique.get("patterns_to_add", []):
            new_pattern = Pattern(
                name=suggestion.get("name", "unknown-pattern"),
                description=suggestion.get("description", ""),
                source_refs=tuple(suggestion.get("likely_sources", [])),
                confidence=0.6,  # Lower confidence for inferred patterns
                focus=findings.focus_used,
                metadata={"inferred": True},
            )
            patterns.append(new_pattern)

        return ArchaeologicalFindings(
            patterns=tuple(patterns),
            provenance=tuple(provenance),
            sources_analyzed=findings.sources_analyzed,
            focus_used=findings.focus_used,
            timestamp=findings.timestamp,
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    async def _load_sources(self, sources: list[Source]) -> list[Source]:
        """Load content for sources that don't have it cached."""
        loaded = []
        for source in sources:
            if source.content is not None:
                loaded.append(source)
            else:
                content = await self._read_source_content(source)
                # Create new Source with content (frozen dataclass)
                loaded.append(
                    Source(
                        path=source.path,
                        type=source.type,
                        content=content,
                        metadata=source.metadata,
                    )
                )
        return loaded

    async def _read_source_content(self, source: Source) -> str:
        """Read content from a source file."""
        try:
            path = Path(source.path)
            if path.exists() and path.is_file():
                # Limit file size to avoid token explosion
                max_size = 100_000  # ~25k tokens
                content = path.read_text(encoding="utf-8")
                if len(content) > max_size:
                    content = content[:max_size] + "\n\n[TRUNCATED - file too large]"
                return content
            else:
                return f"[Source not found: {source.path}]"
        except Exception as e:
            logger.warning(f"Failed to read source {source.path}: {e}")
            return f"[Error reading source: {e}]"

    def _format_sources(self, sources: list[Source]) -> str:
        """Format sources for inclusion in prompt."""
        parts = []
        for source in sources:
            parts.append(f"### Source: {source.path} (type: {source.type.value})")
            parts.append("```")
            content = source.content or "[no content]"
            # Truncate very long content
            if len(content) > 20_000:
                content = content[:20_000] + "\n\n[TRUNCATED for prompt]"
            parts.append(content)
            parts.append("```")
            parts.append("")
        return "\n".join(parts)

    def _format_patterns(self, patterns: tuple[Pattern, ...]) -> str:
        """Format patterns for interpretation prompt."""
        parts = []
        for i, pattern in enumerate(patterns, 1):
            refs = ", ".join(pattern.source_refs) if pattern.source_refs else "none"
            parts.append(f"### Pattern {i}: {pattern.name}")
            parts.append(f"**Description**: {pattern.description}")
            parts.append(f"**Sources**: {refs}")
            parts.append(f"**Confidence**: {pattern.confidence:.2f}")
            parts.append("")
        return "\n".join(parts)

    def _format_findings_for_assessment(self, findings: ArchaeologicalFindings) -> str:
        """Format findings for quality assessment."""
        parts = [
            "## Archaeological Findings",
            f"Focus: {findings.focus_used.value if findings.focus_used else 'unknown'}",
            f"Sources analyzed: {findings.sources_analyzed}",
            f"Patterns found: {len(findings.patterns)}",
            "",
            "### Patterns:",
        ]

        for pattern in findings.patterns:
            refs = ", ".join(pattern.source_refs) if pattern.source_refs else "MISSING"
            parts.append(f"- **{pattern.name}** (confidence: {pattern.confidence:.2f})")
            parts.append(f"  Description: {pattern.description[:200]}...")
            parts.append(f"  Sources: {refs}")
            parts.append("")

        if findings.provenance:
            parts.append("### Provenance Graph:")
            for node in findings.provenance:
                parts.append(
                    f"- {node.pattern_name} <- {node.source_path}:{node.location or 'general'}"
                )

        return "\n".join(parts)

    def _parse_excavation_response(
        self,
        response: str,
        focus: ArchaeologyFocus,
        sources_count: int,
    ) -> ArchaeologicalFindings:
        """Parse LLM excavation response into findings."""
        json_text = self._extract_json(response)

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse excavation JSON: {e}")
            # Return minimal findings
            return ArchaeologicalFindings(
                patterns=(
                    Pattern(
                        name="parsing-error",
                        description=f"Failed to parse LLM response: {e}",
                        source_refs=(),
                        confidence=0.0,
                        focus=focus,
                    ),
                ),
                provenance=(),
                sources_analyzed=sources_count,
                focus_used=focus,
            )

        # Parse patterns
        patterns = []
        for p_data in data.get("patterns", []):
            pattern = Pattern(
                name=p_data.get("name", "unknown"),
                description=p_data.get("description", ""),
                source_refs=tuple(p_data.get("source_refs", [])),
                confidence=p_data.get("confidence", 0.5),
                focus=focus,
                metadata=p_data.get("metadata", {}),
            )
            patterns.append(pattern)

        # Parse provenance
        provenance = []
        for prov_data in data.get("provenance", []):
            node = ProvenanceNode(
                pattern_name=prov_data.get("pattern_name", ""),
                source_path=prov_data.get("source_path", ""),
                location=prov_data.get("location"),
                extraction_method=prov_data.get("extraction_method", "llm"),
            )
            provenance.append(node)

        return ArchaeologicalFindings(
            patterns=tuple(patterns),
            provenance=tuple(provenance),
            sources_analyzed=sources_count,
            focus_used=focus,
        )

    def _parse_interpretation_response(
        self,
        response: str,
        findings: ArchaeologicalFindings,
        lens: InterpretationLens,
    ) -> InterpretedMeaning:
        """Parse LLM interpretation response."""
        json_text = self._extract_json(response)

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse interpretation JSON: {e}")
            return InterpretedMeaning(
                findings=findings,
                lens=lens,
                interpretations=(),
            )

        interpretations = []
        for i_data in data.get("interpretations", []):
            interp = Interpretation(
                pattern_name=i_data.get("pattern_name", ""),
                meaning=i_data.get("meaning", ""),
                lens=lens,
                confidence=i_data.get("confidence", 0.5),
            )
            interpretations.append(interp)

        return InterpretedMeaning(
            findings=findings,
            lens=lens,
            interpretations=tuple(interpretations),
        )

    def _parse_quality_response(self, response: str) -> QualityAssessment:
        """Parse quality assessment response."""
        json_text = self._extract_json(response)

        try:
            data = json.loads(json_text)
            return QualityAssessment.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse quality response: {e}")
            # Return conservative assessment
            return QualityAssessment(
                contrast_score=0.5,
                arc_score=0.5,
                voice_score=0.5,
                floor_score=0.5,
                overall_score=0.5,
                critique="Failed to parse quality assessment",
                suggestions=(),
            )

    def _parse_critique_response(self, response: str) -> dict[str, Any]:
        """Parse critique response."""
        json_text = self._extract_json(response)

        try:
            result: dict[str, Any] = json.loads(json_text)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse critique response: {e}")
            return {
                "patterns_to_improve": [],
                "patterns_to_remove": [],
                "patterns_to_add": [],
                "reframing": "",
            }

    def _extract_json(self, response: str) -> str:
        """Extract JSON from various response formats."""
        import re

        response = response.strip()

        # Try raw JSON first
        if response.startswith("{") and response.endswith("}"):
            return response

        # Try markdown code block
        code_block_patterns = [
            r"```json\s*\n?(.*?)\n?```",
            r"```\s*\n?(.*?)\n?```",
        ]

        for pattern in code_block_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                extracted = match.group(1).strip()
                if extracted.startswith("{"):
                    return extracted

        # Try to find JSON object in the response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json_match.group(0)

        # Last resort: return as-is
        return response

    def clear_cache(self) -> None:
        """Clear the findings cache."""
        self._findings_cache.clear()

    def get_budget_summary(self) -> dict[str, Any]:
        """Get budget usage summary."""
        return self.budget.summary()


# =============================================================================
# Factory Functions
# =============================================================================


def create_archaeology_functor(
    llm: LLMClientProtocol | None = None,
    token_budget: int = 500_000,
    quality_threshold: float = 0.8,
) -> LLMArchaeologyFunctor:
    """Create a configured LLMArchaeologyFunctor.

    Args:
        llm: LLM client (auto-creates if None)
        token_budget: Maximum session token budget
        quality_threshold: Minimum quality to accept findings

    Returns:
        Configured archaeology functor instance
    """
    if llm is None:
        from agents.k.llm import create_llm_client

        llm = create_llm_client()

    budget = BudgetManager(
        token=TokenBudget(
            max_input_per_call=100_000,
            max_output_per_call=10_000,
            max_session_cumulative=token_budget,
        ),
    )

    return LLMArchaeologyFunctor(
        llm=llm,
        budget=budget,
        quality_threshold=quality_threshold,
    )


__all__ = [
    "LLMArchaeologyFunctor",
    "LLMClientProtocol",
    "QualityAssessment",
    "create_archaeology_functor",
    # Prompts (for customization)
    "FOCUS_PROMPTS",
    "EXCAVATE_SYSTEM_PROMPT",
    "EXCAVATE_USER_PROMPT",
    "INTERPRET_SYSTEM_PROMPT",
    "INTERPRET_USER_PROMPT",
    "LENS_DESCRIPTIONS",
]
