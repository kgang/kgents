"""
N-gent Phase 6: Epistemic Features.

The UnreliableNarrator and RashomonNarrator embody epistemic humility:
- LLMs can hallucinate. Stories can be wrong.
- Multiple perspectives on the same events yield different truths.
- Confidence annotations mark uncertainty.

Philosophy:
    The Rashomon pattern: Same events, different stories.
    The Unreliable pattern: Acknowledge the story might be wrong.

    Together they form the epistemic substrate of narrative—
    acknowledging that truth is perspectival and confidence is quantifiable.

Components:
    - ReliabilityAnnotation: Confidence + corroboration tracking
    - UnreliableTrace: A trace with reliability metadata
    - HallucinationIndicator: Signs of potential hallucination
    - UnreliableNarrator: Narrator with epistemic humility
    - PerspectiveSpec: Configuration for one perspective
    - RashomonNarrative: Multiple perspectives on same events
    - RashomonNarrator: Multi-perspective story generation
    - GroundTruth: Verified facts for reconciliation
    - GroundTruthReconciler: Compare stories against facts

Example:
    >>> from agents.n import UnreliableNarrator, RashomonNarrator
    >>>
    >>> # Single narrator with confidence annotations
    >>> narrator = UnreliableNarrator(llm)
    >>> result = await narrator.narrate(request)
    >>> print(f"Confidence: {result.overall_confidence}")
    >>> for h in result.hallucination_indicators:
    ...     print(f"  Warning: {h.description}")
    >>>
    >>> # Multi-perspective narration
    >>> rashomon = RashomonNarrator([tech_narrator, noir_narrator, sysadmin_narrator])
    >>> perspectives = await rashomon.narrate(request)
    >>>
    >>> consensus = perspectives.consensus  # What all agree on
    >>> contradictions = perspectives.contradictions  # Where they disagree
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .bard import (
    Bard,
    LLMProvider,
    Narrative,
    NarrativeGenre,
    NarrativeRequest,
    Perspective,
)
from .types import SemanticTrace

# =============================================================================
# Reliability Types
# =============================================================================


class ConfidenceLevel(Enum):
    """Discrete confidence levels for human interpretability."""

    CERTAIN = "certain"  # > 0.95 - Verified fact
    HIGH = "high"  # 0.8 - 0.95 - Strong evidence
    MODERATE = "moderate"  # 0.5 - 0.8 - Reasonable inference
    LOW = "low"  # 0.2 - 0.5 - Speculation
    UNCERTAIN = "uncertain"  # < 0.2 - Guess at best

    @classmethod
    def from_score(cls, score: float) -> ConfidenceLevel:
        """Convert numeric confidence to level."""
        if score >= 0.95:
            return cls.CERTAIN
        elif score >= 0.8:
            return cls.HIGH
        elif score >= 0.5:
            return cls.MODERATE
        elif score >= 0.2:
            return cls.LOW
        else:
            return cls.UNCERTAIN


@dataclass
class ReliabilityAnnotation:
    """
    Reliability metadata for a narrative segment.

    Tracks:
    - Confidence: How sure are we this is true?
    - Corroboration: What other evidence supports this?
    - Contradictions: What evidence contradicts this?
    - Source reliability: How reliable is the source agent?
    """

    confidence: float  # 0.0 - 1.0
    corroborated_by: list[str] = field(default_factory=list)  # trace_ids
    contradicted_by: list[str] = field(default_factory=list)  # trace_ids
    source_reliability: float = 1.0  # Reliability of narrating agent

    @property
    def level(self) -> ConfidenceLevel:
        """Get discrete confidence level."""
        return ConfidenceLevel.from_score(self.adjusted_confidence)

    @property
    def adjusted_confidence(self) -> float:
        """
        Confidence adjusted for corroboration and contradiction.

        Corroboration boosts confidence (up to 20% boost).
        Contradiction penalizes confidence (up to 50% penalty).
        """
        base = self.confidence * self.source_reliability

        # Corroboration boost: +5% per corroborating trace, max +20%
        corroboration_boost = min(0.20, len(self.corroborated_by) * 0.05)

        # Contradiction penalty: -15% per contradicting trace, max -50%
        contradiction_penalty = min(0.50, len(self.contradicted_by) * 0.15)

        adjusted = base + corroboration_boost - contradiction_penalty
        return max(0.0, min(1.0, adjusted))

    @property
    def is_contested(self) -> bool:
        """Is this annotation contested (has contradictions)?"""
        return len(self.contradicted_by) > 0


@dataclass
class UnreliableTrace:
    """
    A trace with reliability annotations.

    Wraps a SemanticTrace with epistemic metadata.
    """

    trace: SemanticTrace
    reliability: ReliabilityAnnotation
    interpretation: str = ""  # The narrator's interpretation

    @property
    def trace_id(self) -> str:
        return self.trace.trace_id

    @property
    def agent_id(self) -> str:
        return self.trace.agent_id

    @property
    def confidence(self) -> float:
        return self.reliability.adjusted_confidence

    @property
    def level(self) -> ConfidenceLevel:
        return self.reliability.level


# =============================================================================
# Hallucination Detection
# =============================================================================


class HallucinationType(Enum):
    """Types of potential hallucination."""

    CONFABULATION = "confabulation"  # Filling gaps with plausible but false info
    OVERCONFIDENCE = "overconfidence"  # High confidence without evidence
    CONTRADICTION = "contradiction"  # Contradicts known facts
    TEMPORAL = "temporal"  # Timeline inconsistency
    ATTRIBUTION = "attribution"  # Wrong source attribution
    SPECIFICITY = "specificity"  # Suspiciously specific without source


@dataclass
class HallucinationIndicator:
    """
    A potential hallucination detected in the narrative.

    These are warnings, not certainties. Human judgment needed.
    """

    type: HallucinationType
    description: str
    affected_traces: list[str]  # trace_ids
    severity: float  # 0.0 - 1.0
    evidence: str = ""  # Why we suspect this

    @property
    def is_severe(self) -> bool:
        """Is this a severe hallucination indicator?"""
        return self.severity >= 0.7

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "description": self.description,
            "affected_traces": self.affected_traces,
            "severity": self.severity,
            "evidence": self.evidence,
        }


class HallucinationDetector:
    """
    Detects potential hallucinations in narratives.

    Uses heuristics to flag suspicious patterns:
    - High confidence + zero corroboration
    - Contradictions with known ground truth
    - Suspiciously specific claims without source
    - Temporal inconsistencies
    """

    def detect(
        self,
        traces: list[UnreliableTrace],
        ground_truth: list[GroundTruth] | None = None,
    ) -> list[HallucinationIndicator]:
        """
        Detect potential hallucinations.

        Args:
            traces: Traces with reliability annotations
            ground_truth: Optional verified facts for comparison

        Returns:
            List of potential hallucination indicators
        """
        indicators: list[HallucinationIndicator] = []

        # Check for overconfidence pattern
        indicators.extend(self._detect_overconfidence(traces))

        # Check for contradictions
        indicators.extend(self._detect_contradictions(traces))

        # Check against ground truth
        if ground_truth:
            indicators.extend(self._check_ground_truth(traces, ground_truth))

        # Check temporal consistency
        indicators.extend(self._detect_temporal_issues(traces))

        return sorted(indicators, key=lambda i: -i.severity)

    def _detect_overconfidence(
        self, traces: list[UnreliableTrace]
    ) -> list[HallucinationIndicator]:
        """Detect high confidence without corroboration."""
        indicators = []

        for t in traces:
            if (
                t.reliability.confidence > 0.8
                and len(t.reliability.corroborated_by) == 0
            ):
                indicators.append(
                    HallucinationIndicator(
                        type=HallucinationType.OVERCONFIDENCE,
                        description=f"High confidence ({t.reliability.confidence:.2f}) without corroboration",
                        affected_traces=[t.trace_id],
                        severity=0.5,
                        evidence=f"Trace {t.trace_id} claims confidence {t.reliability.confidence:.2f} "
                        f"but has no corroborating evidence",
                    )
                )

        return indicators

    def _detect_contradictions(
        self, traces: list[UnreliableTrace]
    ) -> list[HallucinationIndicator]:
        """Detect internal contradictions."""
        indicators = []

        # Group traces by agent
        by_agent: dict[str, list[UnreliableTrace]] = {}
        for t in traces:
            by_agent.setdefault(t.agent_id, []).append(t)

        # Check for same agent contradicting itself
        for agent_id, agent_traces in by_agent.items():
            if len(agent_traces) < 2:
                continue

            for t in agent_traces:
                if len(t.reliability.contradicted_by) > 0:
                    indicators.append(
                        HallucinationIndicator(
                            type=HallucinationType.CONTRADICTION,
                            description=f"Agent {agent_id} has contradicting claims",
                            affected_traces=[t.trace_id]
                            + t.reliability.contradicted_by,
                            severity=0.7,
                            evidence=f"Trace {t.trace_id} contradicted by {t.reliability.contradicted_by}",
                        )
                    )

        return indicators

    def _check_ground_truth(
        self,
        traces: list[UnreliableTrace],
        ground_truth: list[GroundTruth],
    ) -> list[HallucinationIndicator]:
        """Check traces against verified ground truth."""
        indicators = []

        gt_by_trace = {gt.trace_id: gt for gt in ground_truth}

        for t in traces:
            if t.trace_id not in gt_by_trace:
                continue

            gt = gt_by_trace[t.trace_id]

            # Compare interpretation against verified fact
            if gt.verified_interpretation and t.interpretation:
                if gt.verified_interpretation.lower() != t.interpretation.lower():
                    indicators.append(
                        HallucinationIndicator(
                            type=HallucinationType.CONFABULATION,
                            description="Interpretation differs from verified ground truth",
                            affected_traces=[t.trace_id],
                            severity=0.9,
                            evidence=f"Narrator said: '{t.interpretation[:100]}...'; "
                            f"Ground truth: '{gt.verified_interpretation[:100]}...'",
                        )
                    )

        return indicators

    def _detect_temporal_issues(
        self, traces: list[UnreliableTrace]
    ) -> list[HallucinationIndicator]:
        """Detect temporal inconsistencies."""
        indicators = []

        if len(traces) < 2:
            return indicators

        # Sort by timestamp
        sorted_traces = sorted(traces, key=lambda t: t.trace.timestamp)

        for i in range(1, len(sorted_traces)):
            curr = sorted_traces[i]

            # Check if interpretation claims something happened before it could
            if curr.interpretation:
                # Simple heuristic: if interpretation mentions "before" when
                # referencing a later event
                if "before" in curr.interpretation.lower():
                    # Could be suspicious - needs context
                    pass  # More sophisticated analysis would go here

        return indicators


# =============================================================================
# Unreliable Narrator
# =============================================================================


@dataclass
class UnreliableNarrative:
    """
    A narrative with epistemic annotations.

    Extends Narrative with:
    - Reliability annotations per trace
    - Overall confidence score
    - Hallucination indicators
    """

    narrative: Narrative
    annotated_traces: list[UnreliableTrace]
    hallucination_indicators: list[HallucinationIndicator]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        return self.narrative.text

    @property
    def overall_confidence(self) -> float:
        """Aggregate confidence across all traces."""
        if not self.annotated_traces:
            return 0.0
        return sum(t.confidence for t in self.annotated_traces) / len(
            self.annotated_traces
        )

    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Discrete confidence level."""
        return ConfidenceLevel.from_score(self.overall_confidence)

    @property
    def contested_traces(self) -> list[UnreliableTrace]:
        """Traces with contradictions."""
        return [t for t in self.annotated_traces if t.reliability.is_contested]

    @property
    def has_hallucination_warnings(self) -> bool:
        """Are there any hallucination indicators?"""
        return len(self.hallucination_indicators) > 0

    @property
    def severe_warnings(self) -> list[HallucinationIndicator]:
        """Get only severe hallucination indicators."""
        return [h for h in self.hallucination_indicators if h.is_severe]

    def render_with_confidence(self, format: str = "text") -> str:
        """Render narrative with confidence annotations."""
        base = self.narrative.render(format)

        # Add confidence summary
        summary = f"\n\n---\nConfidence: {self.overall_confidence:.2f} ({self.confidence_level.value})"

        if self.has_hallucination_warnings:
            summary += f"\nWarnings: {len(self.hallucination_indicators)}"
            for h in self.severe_warnings:
                summary += f"\n  - [{h.type.value}] {h.description}"

        return base + summary


class UnreliableNarrator(Bard):
    """
    A narrator that knows it might be wrong.

    Produces narratives with:
    - Confidence annotations per trace
    - Corroboration/contradiction tracking
    - Hallucination detection

    This is EPISTEMIC HUMILITY encoded in architecture.

    Usage:
        narrator = UnreliableNarrator(llm)
        result = await narrator.narrate(request)

        if result.overall_confidence < 0.5:
            print("Warning: Low confidence narrative")

        for warning in result.hallucination_indicators:
            print(f"Potential issue: {warning.description}")
    """

    def __init__(
        self,
        llm: LLMProvider | None = None,
        base_confidence: float = 0.7,
        hallucination_detector: HallucinationDetector | None = None,
    ):
        """
        Initialize the Unreliable Narrator.

        Args:
            llm: LLM provider for narrative generation
            base_confidence: Default confidence for traces
            hallucination_detector: Optional custom detector
        """
        super().__init__(llm)
        self.base_confidence = base_confidence
        self.detector = hallucination_detector or HallucinationDetector()

    async def narrate(
        self,
        request: NarrativeRequest,
        ground_truth: list[GroundTruth] | None = None,
    ) -> UnreliableNarrative:
        """
        Produce a narrative with reliability annotations.

        Args:
            request: What to narrate
            ground_truth: Optional verified facts for comparison

        Returns:
            UnreliableNarrative with confidence and hallucination data
        """
        # Generate base narrative
        narrative = await self.invoke(request)

        # Annotate traces
        traces = request.filtered_traces()
        annotated = self._annotate_traces(traces)

        # Detect hallucinations
        indicators = self.detector.detect(annotated, ground_truth)

        return UnreliableNarrative(
            narrative=narrative,
            annotated_traces=annotated,
            hallucination_indicators=indicators,
            metadata={
                "base_confidence": self.base_confidence,
                "ground_truth_provided": ground_truth is not None,
            },
        )

    def _annotate_traces(self, traces: list[SemanticTrace]) -> list[UnreliableTrace]:
        """Add reliability annotations to traces."""
        annotated: list[UnreliableTrace] = []

        for trace in traces:
            # Calculate base confidence from trace properties
            confidence = self._calculate_confidence(trace)

            # Find corroborating traces (same agent, similar action, close in time)
            corroborated_by = self._find_corroboration(trace, traces)

            # Find contradicting traces
            contradicted_by = self._find_contradictions(trace, traces)

            reliability = ReliabilityAnnotation(
                confidence=confidence,
                corroborated_by=[t.trace_id for t in corroborated_by],
                contradicted_by=[t.trace_id for t in contradicted_by],
                source_reliability=self._assess_source_reliability(trace),
            )

            annotated.append(
                UnreliableTrace(
                    trace=trace,
                    reliability=reliability,
                    interpretation=self._generate_interpretation(trace),
                )
            )

        return annotated

    def _calculate_confidence(self, trace: SemanticTrace) -> float:
        """Calculate confidence for a trace."""
        from .types import Determinism

        confidence = self.base_confidence

        # Deterministic traces get higher confidence
        if trace.determinism == Determinism.DETERMINISTIC:
            confidence += 0.15
        elif trace.determinism == Determinism.CHAOTIC:
            confidence -= 0.2

        # Traces with outputs are more verifiable
        if trace.outputs:
            confidence += 0.05

        # Long-running traces might be less reliable
        if trace.duration_ms > 5000:
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    def _find_corroboration(
        self,
        trace: SemanticTrace,
        all_traces: list[SemanticTrace],
    ) -> list[SemanticTrace]:
        """Find traces that corroborate this one."""
        corroborating = []

        for other in all_traces:
            if other.trace_id == trace.trace_id:
                continue

            # Same agent, same action type = corroboration
            if other.agent_id == trace.agent_id and other.action == trace.action:
                time_diff = abs((other.timestamp - trace.timestamp).total_seconds())
                if time_diff < 60:  # Within 1 minute
                    corroborating.append(other)

        return corroborating

    def _find_contradictions(
        self,
        trace: SemanticTrace,
        all_traces: list[SemanticTrace],
    ) -> list[SemanticTrace]:
        """Find traces that contradict this one."""
        contradicting = []

        for other in all_traces:
            if other.trace_id == trace.trace_id:
                continue

            # Same agent, error vs success = contradiction
            if other.agent_id == trace.agent_id:
                is_trace_error = trace.action == "ERROR"
                is_other_error = other.action == "ERROR"

                # One error, one success on same input = contradiction
                if is_trace_error != is_other_error:
                    if trace.inputs == other.inputs:
                        contradicting.append(other)

        return contradicting

    def _assess_source_reliability(self, trace: SemanticTrace) -> float:
        """Assess reliability of the source agent."""
        # This could be extended to track historical reliability per agent
        from .types import Determinism

        # Deterministic agents are more reliable
        if trace.determinism == Determinism.DETERMINISTIC:
            return 1.0
        elif trace.determinism == Determinism.PROBABILISTIC:
            return 0.9
        else:  # CHAOTIC
            return 0.7

    def _generate_interpretation(self, trace: SemanticTrace) -> str:
        """Generate a simple interpretation of the trace."""
        return f"{trace.agent_id} performed {trace.action}"


# =============================================================================
# Rashomon Narrator (Multi-Perspective)
# =============================================================================


@dataclass
class PerspectiveSpec:
    """
    Configuration for one perspective in the Rashomon narrative.

    Each perspective has:
    - A narrator identity (who's telling the story)
    - A genre (how they tell it)
    - A reliability score (how much to trust this narrator)
    """

    narrator_id: str
    genre: NarrativeGenre
    perspective: Perspective = Perspective.THIRD_PERSON
    reliability: float = 1.0  # How reliable is this narrator?
    focus_agents: list[str] | None = None  # Which agents they focus on
    bias: str = ""  # Known bias of this narrator


@dataclass
class Contradiction:
    """
    A point where perspectives disagree.

    Useful for investigation and reconciliation.
    """

    trace_id: str
    perspectives: dict[str, str]  # narrator_id -> their interpretation
    severity: float  # 0.0 - 1.0 (how significant is this disagreement?)

    @property
    def narrator_ids(self) -> list[str]:
        """Get narrators involved in this contradiction."""
        return list(self.perspectives.keys())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "perspectives": self.perspectives,
            "severity": self.severity,
        }


@dataclass
class RashomonNarrative:
    """
    Multiple perspectives on the same events.

    Like Kurosawa's film—multiple narrators tell their version of events.
    The truth emerges from comparing and contrasting.
    """

    perspectives: dict[str, UnreliableNarrative]  # narrator_id -> narrative
    specs: dict[str, PerspectiveSpec]  # narrator_id -> spec
    traces: list[SemanticTrace]  # Original traces
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def narrator_ids(self) -> list[str]:
        """Get all narrator IDs."""
        return list(self.perspectives.keys())

    @property
    def consensus(self) -> list[UnreliableTrace]:
        """
        Find traces all perspectives agree on.

        Consensus = traces where all narrators have similar confidence.
        """
        if not self.perspectives:
            return []

        # Get first perspective's traces as reference
        first_id = self.narrator_ids[0]
        first_traces = self.perspectives[first_id].annotated_traces

        consensus_traces = []

        for trace in first_traces:
            # Check if all perspectives have similar confidence for this trace
            confidences = []
            for narrator_id, narrative in self.perspectives.items():
                for t in narrative.annotated_traces:
                    if t.trace_id == trace.trace_id:
                        confidences.append(t.confidence)
                        break

            if len(confidences) == len(self.perspectives):
                # All perspectives have this trace
                variance = max(confidences) - min(confidences)
                if variance < 0.2:  # Similar confidence (within 20%)
                    consensus_traces.append(trace)

        return consensus_traces

    @property
    def contradictions(self) -> list[Contradiction]:
        """
        Find where perspectives disagree.

        Contradictions = traces where narrators have very different confidence.
        """
        if len(self.perspectives) < 2:
            return []

        contradictions = []

        # Compare each trace across perspectives
        first_id = self.narrator_ids[0]
        first_traces = self.perspectives[first_id].annotated_traces

        for trace in first_traces:
            interpretations: dict[str, str] = {}
            confidences: dict[str, float] = {}

            for narrator_id, narrative in self.perspectives.items():
                for t in narrative.annotated_traces:
                    if t.trace_id == trace.trace_id:
                        interpretations[narrator_id] = t.interpretation
                        confidences[narrator_id] = t.confidence
                        break

            if len(confidences) >= 2:
                variance = max(confidences.values()) - min(confidences.values())
                if variance > 0.3:  # Significant disagreement
                    contradictions.append(
                        Contradiction(
                            trace_id=trace.trace_id,
                            perspectives=interpretations,
                            severity=variance,
                        )
                    )

        return sorted(contradictions, key=lambda c: -c.severity)

    def get_perspective(self, narrator_id: str) -> UnreliableNarrative | None:
        """Get a specific perspective."""
        return self.perspectives.get(narrator_id)

    def weighted_confidence(self) -> float:
        """
        Calculate weighted confidence across all perspectives.

        Weights by each narrator's reliability.
        """
        if not self.perspectives:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for narrator_id, narrative in self.perspectives.items():
            spec = self.specs.get(narrator_id)
            weight = spec.reliability if spec else 1.0

            total_weight += weight
            weighted_sum += narrative.overall_confidence * weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0


class RashomonNarrator:
    """
    Generate multiple perspectives on the same events.

    Named after Kurosawa's film where multiple characters tell
    conflicting accounts of the same events.

    Usage:
        # Define perspectives
        specs = [
            PerspectiveSpec("tech", NarrativeGenre.TECHNICAL, reliability=0.9),
            PerspectiveSpec("noir", NarrativeGenre.NOIR, reliability=0.7),
            PerspectiveSpec("ops", NarrativeGenre.SYSADMIN, reliability=0.95),
        ]

        # Create narrators
        rashomon = RashomonNarrator(llm, specs)

        # Generate multi-perspective narrative
        result = await rashomon.narrate(request)

        # Analyze consensus and contradictions
        print(f"Consensus traces: {len(result.consensus)}")
        print(f"Contradictions: {len(result.contradictions)}")
    """

    def __init__(
        self,
        llm: LLMProvider | None = None,
        specs: list[PerspectiveSpec] | None = None,
    ):
        """
        Initialize the Rashomon Narrator.

        Args:
            llm: LLM provider for narrative generation
            specs: Perspective specifications (one per narrator)
        """
        self.llm = llm
        self.specs = {s.narrator_id: s for s in (specs or [])}

        # Create unreliable narrator per perspective
        self.narrators: dict[str, UnreliableNarrator] = {}
        for spec in specs or []:
            self.narrators[spec.narrator_id] = UnreliableNarrator(
                llm=llm,
                base_confidence=spec.reliability,
            )

    def add_perspective(self, spec: PerspectiveSpec) -> None:
        """Add a new perspective."""
        self.specs[spec.narrator_id] = spec
        self.narrators[spec.narrator_id] = UnreliableNarrator(
            llm=self.llm,
            base_confidence=spec.reliability,
        )

    async def narrate(
        self,
        request: NarrativeRequest,
        ground_truth: list[GroundTruth] | None = None,
    ) -> RashomonNarrative:
        """
        Generate narratives from all perspectives.

        Args:
            request: Base narrative request
            ground_truth: Optional verified facts for all perspectives

        Returns:
            RashomonNarrative with all perspectives
        """
        perspectives: dict[str, UnreliableNarrative] = {}

        for narrator_id, spec in self.specs.items():
            # Customize request for this perspective
            perspective_request = NarrativeRequest(
                traces=request.traces,
                genre=spec.genre,
                perspective=spec.perspective,
                verbosity=request.verbosity,
                focus_agents=spec.focus_agents or request.focus_agents,
                filter_actions=request.filter_actions,
                exclude_actions=request.exclude_actions,
                title=request.title,
                custom_prompt=request.custom_prompt,
            )

            # Generate this perspective's narrative
            narrator = self.narrators[narrator_id]
            narrative = await narrator.narrate(perspective_request, ground_truth)

            perspectives[narrator_id] = narrative

        return RashomonNarrative(
            perspectives=perspectives,
            specs=self.specs,
            traces=request.filtered_traces(),
            metadata={
                "narrator_count": len(perspectives),
                "ground_truth_provided": ground_truth is not None,
            },
        )


# =============================================================================
# Ground Truth Reconciliation
# =============================================================================


@dataclass
class GroundTruth:
    """
    A verified fact for narrative reconciliation.

    Ground truths are known facts against which narratives can be checked.
    """

    trace_id: str
    verified_interpretation: str
    source: str = "human"  # Who verified this?
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0  # How certain is this ground truth?

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "verified_interpretation": self.verified_interpretation,
            "source": self.source,
            "verified_at": self.verified_at.isoformat(),
            "confidence": self.confidence,
        }


@dataclass
class ReconciliationResult:
    """
    Result of reconciling narrative against ground truth.
    """

    matches: list[tuple[str, str]]  # (trace_id, matched_text)
    mismatches: list[tuple[str, str, str]]  # (trace_id, narrative_text, ground_truth)
    unverified: list[str]  # trace_ids without ground truth
    accuracy: float  # Proportion of matches

    @property
    def has_errors(self) -> bool:
        """Are there any mismatches?"""
        return len(self.mismatches) > 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "matches": self.matches,
            "mismatches": [
                {"trace_id": t, "narrative": n, "ground_truth": g}
                for t, n, g in self.mismatches
            ],
            "unverified": self.unverified,
            "accuracy": self.accuracy,
        }


class GroundTruthReconciler:
    """
    Compare narratives against verified ground truth.

    Useful for:
    - Detecting narrative drift from reality
    - Evaluating narrator reliability
    - Building trust in narrative systems
    """

    def __init__(self, ground_truths: list[GroundTruth] | None = None):
        """
        Initialize reconciler.

        Args:
            ground_truths: Initial set of verified facts
        """
        self.ground_truths: dict[str, GroundTruth] = {}
        for gt in ground_truths or []:
            self.ground_truths[gt.trace_id] = gt

    def add_ground_truth(self, gt: GroundTruth) -> None:
        """Add a verified fact."""
        self.ground_truths[gt.trace_id] = gt

    def reconcile(
        self,
        narrative: UnreliableNarrative,
        similarity_threshold: float = 0.8,
    ) -> ReconciliationResult:
        """
        Reconcile narrative against ground truth.

        Args:
            narrative: The narrative to check
            similarity_threshold: Min similarity for match (simple comparison for now)

        Returns:
            ReconciliationResult with matches and mismatches
        """
        matches: list[tuple[str, str]] = []
        mismatches: list[tuple[str, str, str]] = []
        unverified: list[str] = []

        for trace in narrative.annotated_traces:
            gt = self.ground_truths.get(trace.trace_id)

            if gt is None:
                unverified.append(trace.trace_id)
                continue

            # Compare interpretation against ground truth
            if self._is_similar(
                trace.interpretation, gt.verified_interpretation, similarity_threshold
            ):
                matches.append((trace.trace_id, trace.interpretation))
            else:
                mismatches.append(
                    (
                        trace.trace_id,
                        trace.interpretation,
                        gt.verified_interpretation,
                    )
                )

        total_verified = len(matches) + len(mismatches)
        accuracy = len(matches) / total_verified if total_verified > 0 else 1.0

        return ReconciliationResult(
            matches=matches,
            mismatches=mismatches,
            unverified=unverified,
            accuracy=accuracy,
        )

    def _is_similar(self, text1: str, text2: str, threshold: float) -> bool:
        """Check if two texts are similar enough."""
        # Simple case-insensitive comparison for now
        # Could be enhanced with embedding similarity
        t1 = text1.lower().strip()
        t2 = text2.lower().strip()

        if t1 == t2:
            return True

        # Check if one contains the other
        if t1 in t2 or t2 in t1:
            return True

        # Word overlap
        words1 = set(t1.split())
        words2 = set(t2.split())

        if not words1 or not words2:
            return False

        overlap = len(words1 & words2) / len(words1 | words2)
        return overlap >= threshold


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Reliability
    "ConfidenceLevel",
    "ReliabilityAnnotation",
    "UnreliableTrace",
    # Hallucination
    "HallucinationType",
    "HallucinationIndicator",
    "HallucinationDetector",
    # Unreliable Narrator
    "UnreliableNarrative",
    "UnreliableNarrator",
    # Rashomon
    "PerspectiveSpec",
    "Contradiction",
    "RashomonNarrative",
    "RashomonNarrator",
    # Ground Truth
    "GroundTruth",
    "ReconciliationResult",
    "GroundTruthReconciler",
]
