"""
O-gent Dimension Y: Semantic Observability (The Mind)

Observes meaning, coherence, and cognitive integrity.
Answers: "Does it mean what it says?"

Observes:
- Semantic drift (intent vs. output alignment)
- Borromean knot integrity (Symbolic/Real/Imaginary registers)
- Hallucination detection (output grounded in reality?)

This is the "mental" layer of observation—the mind of the system.
Uses "Shadow Models" (cheap LLMs) to verify cognitive integrity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Protocol

from .observer import (
    BaseObserver,
    EntropyEvent,
    ObservationContext,
    ObservationResult,
)

# =============================================================================
# Drift Detection Types
# =============================================================================


class DriftSeverity(Enum):
    """Severity levels for semantic drift."""

    NONE = "none"  # No drift detected
    LOW = "low"  # Minor drift, acceptable
    MEDIUM = "medium"  # Noticeable drift, review recommended
    HIGH = "high"  # Significant drift, intervention suggested
    CRITICAL = "critical"  # Complete topic divergence


@dataclass
class DriftAlert:
    """Alert generated when semantic drift exceeds threshold."""

    agent_id: str
    drift_score: float  # 0.0 (aligned) to 1.0 (completely divergent)
    input_intent: str
    output_summary: str
    severity: DriftSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class DriftReport:
    """Report of drift measurement."""

    agent_id: str
    drift_score: float
    within_bounds: bool
    input_intent: str
    output_summary: str
    severity: DriftSeverity
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def drifted(self) -> bool:
        """Whether drift was detected."""
        return not self.within_bounds


# =============================================================================
# Drift Measurement Interface
# =============================================================================


class DriftMeasurer(Protocol):
    """
    Protocol for measuring semantic drift.

    Implementations can use:
    - Embedding similarity
    - LLM-as-Judge
    - Keyword overlap
    - Custom heuristics
    """

    async def measure(self, intent: str, output: str) -> float:
        """
        Measure drift between intent and output.

        Returns: 0.0 (perfect alignment) to 1.0 (complete divergence)
        """
        ...


class SimpleDriftMeasurer:
    """
    Simple drift measurer using keyword overlap.

    No ML dependencies—uses basic text analysis.
    Good enough for many use cases, fast and cheap.
    """

    def __init__(self, stopwords: set[str] | None = None):
        self.stopwords = stopwords or {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "need",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "at",
            "by",
            "from",
            "as",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "and",
            "but",
            "if",
            "or",
            "because",
            "until",
            "while",
            "it",
            "its",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "we",
            "they",
        }

    def _tokenize(self, text: str) -> set[str]:
        """Extract meaningful tokens from text."""
        # Simple tokenization
        words = text.lower().split()
        # Remove punctuation and stopwords
        cleaned = []
        for word in words:
            word = "".join(c for c in word if c.isalnum())
            if word and word not in self.stopwords and len(word) > 2:
                cleaned.append(word)
        return set(cleaned)

    async def measure(self, intent: str, output: str) -> float:
        """
        Measure drift using keyword overlap.

        Uses Jaccard distance: 1 - (intersection / union)
        """
        intent_tokens = self._tokenize(intent)
        output_tokens = self._tokenize(output)

        if not intent_tokens and not output_tokens:
            return 0.0  # Both empty = no drift

        if not intent_tokens or not output_tokens:
            return 1.0  # One empty = complete drift

        intersection = intent_tokens & output_tokens
        union = intent_tokens | output_tokens

        # Jaccard similarity
        similarity = len(intersection) / len(union)

        # Return drift (1 - similarity)
        return 1.0 - similarity


# =============================================================================
# Drift Detector
# =============================================================================


class DriftDetector:
    """
    Detects semantic drift across agent invocations.

    When drift exceeds threshold, alerts are triggered.

    Noether's Theorem for Agents:
    In physics, Noether's theorem relates symmetries to conservation laws.
    In kgents, we conserve **Intent**.

    If Input Intent is I and Output Meaning is M, then M ≈ I.
    """

    def __init__(
        self,
        threshold: float = 0.5,
        measurer: DriftMeasurer | None = None,
        alert_callback: Callable[[DriftAlert], Any] | None = None,
    ):
        """
        Initialize drift detector.

        Args:
            threshold: Drift score above which alerts trigger (0-1)
            measurer: Custom drift measurement implementation
            alert_callback: Called when drift exceeds threshold
        """
        self.threshold = threshold
        self.measurer = measurer or SimpleDriftMeasurer()
        self.alert_callback = alert_callback
        self._history: list[DriftReport] = []

    async def measure_drift(
        self,
        agent_id: str,
        input_intent: str,
        output_summary: str,
    ) -> DriftReport:
        """
        Compare input intent with output summary.

        High drift = the agent wandered off topic.
        """
        drift_score = await self.measurer.measure(input_intent, output_summary)

        # Classify severity
        severity = self._classify_severity(drift_score)

        # Check bounds
        within_bounds = drift_score <= self.threshold

        # Create report
        report = DriftReport(
            agent_id=agent_id,
            drift_score=drift_score,
            within_bounds=within_bounds,
            input_intent=input_intent,
            output_summary=output_summary,
            severity=severity,
        )

        self._history.append(report)

        # Trigger alert if needed
        if not within_bounds and self.alert_callback:
            alert = DriftAlert(
                agent_id=agent_id,
                drift_score=drift_score,
                input_intent=input_intent,
                output_summary=output_summary,
                severity=severity,
                suggestions=self._generate_suggestions(severity),
            )
            self.alert_callback(alert)

        return report

    def _classify_severity(self, drift_score: float) -> DriftSeverity:
        """Classify drift score into severity level."""
        if drift_score <= 0.1:
            return DriftSeverity.NONE
        elif drift_score <= 0.3:
            return DriftSeverity.LOW
        elif drift_score <= 0.5:
            return DriftSeverity.MEDIUM
        elif drift_score <= 0.7:
            return DriftSeverity.HIGH
        else:
            return DriftSeverity.CRITICAL

    def _generate_suggestions(self, severity: DriftSeverity) -> list[str]:
        """Generate remediation suggestions based on severity."""
        suggestions = []

        if severity == DriftSeverity.MEDIUM:
            suggestions.append("Review agent's context window for topic contamination")

        elif severity == DriftSeverity.HIGH:
            suggestions.append("Consider restarting agent with fresh context")
            suggestions.append("Check for prompt injection in input")

        elif severity == DriftSeverity.CRITICAL:
            suggestions.append("Agent appears to be hallucinating or off-topic")
            suggestions.append("Recommend immediate human review")
            suggestions.append("Consider pausing agent until investigation complete")

        return suggestions

    def get_history(
        self,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[DriftReport]:
        """Get drift history, optionally filtered by agent."""
        reports = self._history
        if agent_id:
            reports = [r for r in reports if r.agent_id == agent_id]
        return reports[-limit:]

    def get_average_drift(self, agent_id: str) -> float:
        """Get average drift score for an agent."""
        agent_reports = [r for r in self._history if r.agent_id == agent_id]
        if not agent_reports:
            return 0.0
        return sum(r.drift_score for r in agent_reports) / len(agent_reports)

    def clear(self) -> None:
        """Clear drift history."""
        self._history.clear()


# =============================================================================
# Borromean Knot Types
# =============================================================================


@dataclass
class SymbolicHealth:
    """Health of the Symbolic register (code, specs, schemas)."""

    schema_valid: bool = True
    type_check_pass: bool = True
    spec_compliant: bool = True
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        """Overall symbolic validity."""
        return self.schema_valid and self.type_check_pass and self.spec_compliant


@dataclass
class RealHealth:
    """Health of the Real register (execution, memory, entropy)."""

    executes_without_error: bool = True
    terminates_in_budget: bool = True
    memory_bounded: bool = True
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        """Overall real validity."""
        return (
            self.executes_without_error
            and self.terminates_in_budget
            and self.memory_bounded
        )


@dataclass
class ImaginaryHealth:
    """Health of the Imaginary register (visualization, perception)."""

    visually_coherent: bool = True
    user_perceivable: bool = True
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        """Overall imaginary validity."""
        return self.visually_coherent and self.user_perceivable


@dataclass
class PsychosisAlert:
    """Alert when Borromean knot is broken (agent is "insane")."""

    rings_broken: list[str]  # ["symbolic", "real", "imaginary"]
    severity: str = "critical"
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class KnotHealth:
    """Complete Borromean knot health status."""

    symbolic: SymbolicHealth
    real: RealHealth
    imaginary: ImaginaryHealth
    knot_intact: bool = True
    psychosis_alert: PsychosisAlert | None = None

    @property
    def valid(self) -> bool:
        """Whether all three registers are healthy."""
        return self.symbolic.valid and self.real.valid and self.imaginary.valid


# =============================================================================
# Borromean Observer
# =============================================================================


class BorromeanObserver:
    """
    Observes the Borromean knot of agent health.

    All three registers must hold for the agent to be "valid."
    If any ring is cut, the whole unknots.

    The Three Registers (from Lacanian theory):
    - Symbolic: Code, specs, schemas (Does it parse? Does it type-check?)
    - Real: Execution, memory, entropy (Does it run? Does it terminate?)
    - Imaginary: Visualization, perception (Does it look right?)

    Delegates RSI analysis to H-lacan primitives when available.
    """

    def __init__(
        self,
        symbolic_validator: Callable[[Any], SymbolicHealth] | None = None,
        real_validator: Callable[[Any], RealHealth] | None = None,
        imaginary_validator: Callable[[Any], ImaginaryHealth] | None = None,
        psychosis_callback: Callable[[PsychosisAlert], Any] | None = None,
    ):
        """
        Initialize Borromean observer.

        Args:
            symbolic_validator: Custom symbolic register validator
            real_validator: Custom real register validator
            imaginary_validator: Custom imaginary register validator
            psychosis_callback: Called when knot is broken
        """
        self._symbolic_validator = symbolic_validator or self._default_symbolic
        self._real_validator = real_validator or self._default_real
        self._imaginary_validator = imaginary_validator or self._default_imaginary
        self.psychosis_callback = psychosis_callback
        self._history: list[KnotHealth] = []

    def _default_symbolic(self, agent: Any) -> SymbolicHealth:
        """Default symbolic validation (always passes)."""
        return SymbolicHealth()

    def _default_real(self, agent: Any) -> RealHealth:
        """Default real validation (always passes)."""
        return RealHealth()

    def _default_imaginary(self, agent: Any) -> ImaginaryHealth:
        """Default imaginary validation (always passes)."""
        return ImaginaryHealth()

    async def observe_symbolic(self, agent: Any) -> SymbolicHealth:
        """Does the agent's output satisfy its schema?"""
        return self._symbolic_validator(agent)

    async def observe_real(self, agent: Any) -> RealHealth:
        """Does the agent execute correctly in reality?"""
        return self._real_validator(agent)

    async def observe_imaginary(self, agent: Any) -> ImaginaryHealth:
        """Does the agent's output look correct to perception?"""
        return self._imaginary_validator(agent)

    async def knot_health(self, agent: Any) -> KnotHealth:
        """
        Check all three rings.

        Returns KnotHealth with psychosis alert if any ring is broken.
        """
        symbolic = await self.observe_symbolic(agent)
        real = await self.observe_real(agent)
        imaginary = await self.observe_imaginary(agent)

        # Check which rings are broken
        broken_rings = []
        if not symbolic.valid:
            broken_rings.append("symbolic")
        if not real.valid:
            broken_rings.append("real")
        if not imaginary.valid:
            broken_rings.append("imaginary")

        # Create psychosis alert if needed
        psychosis_alert = None
        if broken_rings:
            psychosis_alert = PsychosisAlert(
                rings_broken=broken_rings,
                description=f"Borromean knot broken: {', '.join(broken_rings)} register(s) invalid",
            )
            if self.psychosis_callback:
                self.psychosis_callback(psychosis_alert)

        health = KnotHealth(
            symbolic=symbolic,
            real=real,
            imaginary=imaginary,
            knot_intact=len(broken_rings) == 0,
            psychosis_alert=psychosis_alert,
        )

        self._history.append(health)
        return health

    def get_history(self, limit: int = 100) -> list[KnotHealth]:
        """Get knot health history."""
        return self._history[-limit:]

    def clear(self) -> None:
        """Clear history."""
        self._history.clear()


# =============================================================================
# Semantic Observer
# =============================================================================


class SemanticObserver(BaseObserver):
    """
    Observer that tracks semantic health.

    Combines drift detection and Borromean knot analysis.
    """

    def __init__(
        self,
        observer_id: str = "semantic",
        drift_detector: DriftDetector | None = None,
        borromean: BorromeanObserver | None = None,
        summarizer: Callable[[Any], str] | None = None,
    ):
        """
        Initialize semantic observer.

        Args:
            observer_id: Unique identifier for this observer
            drift_detector: Drift detection component
            borromean: Borromean knot observer
            summarizer: Function to summarize agent output for drift analysis
        """
        super().__init__(observer_id=observer_id)
        self.drift_detector = drift_detector or DriftDetector()
        self.borromean = borromean or BorromeanObserver()
        self._summarizer = summarizer or self._default_summarizer

    def _default_summarizer(self, output: Any) -> str:
        """Default output summarizer."""
        if output is None:
            return ""
        if isinstance(output, str):
            return output[:500]  # Truncate long strings
        return str(output)[:500]

    async def post_invoke(
        self,
        context: ObservationContext,
        result: Any,
        duration_ms: float,
    ) -> ObservationResult:
        """
        Analyze semantic health after invocation.

        Performs:
        1. Drift detection (intent vs. output)
        2. Borromean knot check (optional, if agent supports it)
        """
        base_result = await super().post_invoke(context, result, duration_ms)

        # Summarize input and output for drift analysis
        input_summary = str(context.input_data)[:500]
        output_summary = self._summarizer(result)

        # Measure drift
        drift_report = await self.drift_detector.measure_drift(
            agent_id=context.agent_id,
            input_intent=input_summary,
            output_summary=output_summary,
        )

        # Update result with semantic telemetry
        base_result.telemetry.update(
            {
                "drift_score": drift_report.drift_score,
                "drift_severity": drift_report.severity.value,
                "drift_within_bounds": drift_report.within_bounds,
            }
        )

        # Mark entropy if critical drift
        if drift_report.severity == DriftSeverity.CRITICAL:
            base_result.entropy_detected = True

        return base_result

    def record_entropy(
        self,
        context: ObservationContext,
        error: Exception,
    ) -> EntropyEvent:
        """Record entropy with semantic context."""
        event = super().record_entropy(context, error)

        # Add semantic context
        event.data["semantic_observer"] = True
        event.data["recent_drift_avg"] = self.drift_detector.get_average_drift(
            context.agent_id
        )

        return event


# =============================================================================
# Hallucination Detector
# =============================================================================


@dataclass
class HallucinationReport:
    """Report of hallucination analysis."""

    agent_id: str
    is_hallucinating: bool
    confidence: float  # 0-1
    indicators: list[str]
    grounding_failures: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class HallucinationDetector:
    """
    Detects when an agent's output is not grounded in reality.

    A hallucination occurs when:
    - Output references entities that don't exist
    - Output contradicts established facts
    - Output invents information not in the input

    This is a simplified heuristic detector. For production use,
    integrate with H-lacan or LLM-as-Judge.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.7,
        callback: Callable[[HallucinationReport], Any] | None = None,
    ):
        self.confidence_threshold = confidence_threshold
        self.callback = callback
        self._history: list[HallucinationReport] = []

    async def check(
        self,
        agent_id: str,
        input_context: str,
        output: str,
        known_facts: list[str] | None = None,
    ) -> HallucinationReport:
        """
        Check if output is hallucinating.

        Simple heuristic: Look for signs of confabulation.
        """
        indicators = []
        grounding_failures = []
        hallucination_score = 0.0

        # Check 1: Very confident assertions without input support
        confident_phrases = ["definitely", "certainly", "absolutely", "always", "never"]
        for phrase in confident_phrases:
            if phrase in output.lower():
                if phrase not in input_context.lower():
                    indicators.append(f"Unsupported confident assertion: '{phrase}'")
                    hallucination_score += 0.1

        # Check 2: Specific numbers/dates not in input
        import re

        output_numbers = set(re.findall(r"\b\d{4,}\b", output))  # Years, large numbers
        input_numbers = set(re.findall(r"\b\d{4,}\b", input_context))
        invented_numbers = output_numbers - input_numbers
        if invented_numbers:
            indicators.append(f"Invented numbers: {invented_numbers}")
            hallucination_score += len(invented_numbers) * 0.15

        # Check 3: Contradictions with known facts
        if known_facts:
            for fact in known_facts:
                fact_lower = fact.lower()
                output_lower = output.lower()
                # Very simple contradiction check
                if (
                    "not " in fact_lower
                    and fact_lower.replace("not ", "") in output_lower
                ):
                    grounding_failures.append(f"Contradicts known fact: {fact}")
                    hallucination_score += 0.25

        # Cap score at 1.0
        hallucination_score = min(1.0, hallucination_score)

        is_hallucinating = hallucination_score >= self.confidence_threshold

        report = HallucinationReport(
            agent_id=agent_id,
            is_hallucinating=is_hallucinating,
            confidence=hallucination_score,
            indicators=indicators,
            grounding_failures=grounding_failures,
        )

        self._history.append(report)

        if is_hallucinating and self.callback:
            self.callback(report)

        return report

    def get_history(
        self,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[HallucinationReport]:
        """Get hallucination history."""
        reports = self._history
        if agent_id:
            reports = [r for r in reports if r.agent_id == agent_id]
        return reports[-limit:]

    def clear(self) -> None:
        """Clear history."""
        self._history.clear()


# =============================================================================
# Convenience Functions
# =============================================================================


def create_drift_detector(
    threshold: float = 0.5,
    alert_callback: Callable[[DriftAlert], Any] | None = None,
) -> DriftDetector:
    """Create a drift detector."""
    return DriftDetector(threshold=threshold, alert_callback=alert_callback)


def create_borromean_observer(
    psychosis_callback: Callable[[PsychosisAlert], Any] | None = None,
) -> BorromeanObserver:
    """Create a Borromean observer."""
    return BorromeanObserver(psychosis_callback=psychosis_callback)


def create_semantic_observer(
    observer_id: str = "semantic",
    drift_threshold: float = 0.5,
) -> SemanticObserver:
    """Create a semantic observer."""
    return SemanticObserver(
        observer_id=observer_id,
        drift_detector=create_drift_detector(threshold=drift_threshold),
    )


def create_hallucination_detector(
    confidence_threshold: float = 0.7,
    callback: Callable[[HallucinationReport], Any] | None = None,
) -> HallucinationDetector:
    """Create a hallucination detector."""
    return HallucinationDetector(
        confidence_threshold=confidence_threshold,
        callback=callback,
    )
