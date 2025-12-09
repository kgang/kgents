"""
Obsidian Tension Detector - H-gent for detecting contradictions.

This module implements the dialectical engine that finds tensions
between stated principles (Thesis) and observed patterns (Antithesis).

Detection Strategies:
1. Structural Analysis - Direct pattern matching (fast)
2. Semantic Analysis - LLM-powered deep analysis (future)
3. Temporal Analysis - Drift detection over time (future)

The Detector surfaces contradictions without judging—it reveals
the gap between stated and actual for human reflection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..types import (
    Antithesis,
    MirrorConfig,
    MirrorReport,
    PatternObservation,
    PatternType,
    Tension,
    TensionType,
    Thesis,
)


@dataclass
class TensionRule:
    """
    A rule for detecting tensions between principles and patterns.

    Each rule maps a principle pattern to an observation pattern
    and defines how to calculate divergence.
    """

    name: str
    description: str

    # Principle matching
    principle_keywords: tuple[str, ...]

    # Pattern matching
    pattern_types: tuple[PatternType, ...]

    # Tension calculation
    calculate_divergence: Callable[[Thesis, PatternObservation], float]

    # Tension classification
    tension_type: TensionType = TensionType.BEHAVIORAL

    # Interpretation template
    interpretation_template: str = ""


class ObsidianTensionDetector:
    """
    H-gent for detecting tensions in Obsidian vaults.

    Implements the Contradict operation from spec/h-gents/contradiction.md:
      Contradict: (Thesis, Observation) → Tension | None

    The detector uses predefined rules to match principles with patterns
    and calculate divergence scores.

    Category Theory:
      Contradict is a partial function from (Deontic × Ontic) to Tension.
      When thesis and observation align, No tension is returned.
    """

    def __init__(self, config: MirrorConfig | None = None):
        """Initialize detector with configuration."""
        self.config = config or MirrorConfig()
        self._rules = self._build_default_rules()

    def detect(
        self,
        principles: list[Thesis],
        observations: list[PatternObservation],
    ) -> list[Tension]:
        """
        Detect tensions between principles and observations.

        Args:
            principles: Extracted principles (Thesis)
            observations: Observed patterns (leading to Antithesis)

        Returns:
            List of detected Tensions, sorted by divergence (highest first)
        """
        tensions: list[Tension] = []

        for principle in principles:
            for observation in observations:
                tension = self._check_tension(principle, observation)
                if (
                    tension
                    and tension.divergence >= self.config.min_divergence_to_report
                ):
                    tensions.append(tension)

        # Sort by divergence (most significant first)
        tensions.sort(key=lambda t: t.divergence, reverse=True)

        # Limit results
        return tensions[: self.config.max_tensions_to_report]

    def _check_tension(
        self,
        principle: Thesis,
        observation: PatternObservation,
    ) -> Tension | None:
        """
        Check if there's a tension between a principle and observation.

        Returns None if no tension is detected.
        """
        for rule in self._rules:
            # Check if rule applies
            if not self._rule_matches(rule, principle, observation):
                continue

            # Calculate divergence
            divergence = rule.calculate_divergence(principle, observation)

            if divergence < self.config.min_divergence_to_report:
                continue

            # Build antithesis
            antithesis = Antithesis(
                pattern=observation.description,
                evidence=(observation,),
                frequency=self._observation_to_frequency(observation),
                severity=divergence,
            )

            # Generate interpretation
            interpretation = self._generate_interpretation(
                rule, principle, observation, divergence
            )

            return Tension(
                thesis=principle,
                antithesis=antithesis,
                divergence=divergence,
                tension_type=rule.tension_type,
                interpretation=interpretation,
            )

        return None

    def _rule_matches(
        self,
        rule: TensionRule,
        principle: Thesis,
        observation: PatternObservation,
    ) -> bool:
        """Check if a rule matches a principle-observation pair."""
        # Check pattern type match
        if observation.pattern_type not in rule.pattern_types:
            return False

        # Check principle keyword match
        principle_lower = principle.content.lower()
        return any(kw in principle_lower for kw in rule.principle_keywords)

    def _observation_to_frequency(self, observation: PatternObservation) -> float:
        """Convert observation value to frequency (0.0-1.0)."""
        if isinstance(observation.value, (int, float)):
            # Percentage values
            if 0 <= observation.value <= 100:
                return observation.value / 100
            # Normalize other values
            return min(1.0, observation.value / 100)
        return 0.5  # Default

    def _generate_interpretation(
        self,
        rule: TensionRule,
        principle: Thesis,
        observation: PatternObservation,
        divergence: float,
    ) -> str:
        """Generate human-readable interpretation of the tension."""
        if rule.interpretation_template:
            return rule.interpretation_template.format(
                principle=principle.content,
                observation=observation.description,
                value=observation.value,
                divergence=f"{divergence:.0%}",
            )

        # Default interpretation
        return (
            f"You stated '{principle.content}' but observation shows: "
            f"{observation.description} ({observation.value}). "
            f"Divergence: {divergence:.0%}"
        )

    def _build_default_rules(self) -> list[TensionRule]:
        """Build default tension detection rules."""
        return [
            # Rule 1: Daily notes commitment vs. orphan daily notes
            TensionRule(
                name="daily_note_abandonment",
                description="Detects abandoned daily note practice",
                principle_keywords=(
                    "daily",
                    "journal",
                    "reflection",
                    "morning",
                    "evening",
                ),
                pattern_types=(PatternType.DAILY_NOTE_USAGE, PatternType.ORPHAN_NOTES),
                calculate_divergence=self._calc_daily_note_divergence,
                tension_type=TensionType.BEHAVIORAL,
                interpretation_template=(
                    "You expressed commitment to daily notes ('{principle}'), "
                    "but {value}% of daily notes have no links, suggesting "
                    "they may not be integrated into your knowledge system."
                ),
            ),
            # Rule 2: Connection/linking commitment vs. orphan notes
            TensionRule(
                name="connection_gap",
                description="Detects gap between connection ideals and orphan notes",
                principle_keywords=(
                    "connect",
                    "link",
                    "network",
                    "relationship",
                    "evergreen",
                ),
                pattern_types=(
                    PatternType.ORPHAN_NOTES,
                    PatternType.CONNECTION_PATTERNS,
                ),
                calculate_divergence=self._calc_connection_divergence,
                tension_type=TensionType.BEHAVIORAL,
                interpretation_template=(
                    "You value connecting ideas ('{principle}'), "
                    "but {value}% of notes are orphans with no links. "
                    "This suggests a gap between connection ideals and practice."
                ),
            ),
            # Rule 3: Deep work/thinking vs. short notes
            TensionRule(
                name="depth_gap",
                description="Detects gap between depth ideals and shallow notes",
                principle_keywords=(
                    "deep",
                    "thorough",
                    "comprehensive",
                    "detailed",
                    "think",
                ),
                pattern_types=(PatternType.NOTE_LENGTH,),
                calculate_divergence=self._calc_depth_divergence,
                tension_type=TensionType.ASPIRATIONAL,
                interpretation_template=(
                    "You value deep work ('{principle}'), "
                    "but {value}% of notes are under 100 words. "
                    "Consider whether short notes serve your depth goals."
                ),
            ),
            # Rule 4: Living document vs. staleness
            TensionRule(
                name="staleness_gap",
                description="Detects gap between living docs and stale content",
                principle_keywords=(
                    "update",
                    "maintain",
                    "living",
                    "current",
                    "fresh",
                    "evolve",
                ),
                pattern_types=(PatternType.STALENESS, PatternType.UPDATE_FREQUENCY),
                calculate_divergence=self._calc_staleness_divergence,
                tension_type=TensionType.OUTDATED,
                interpretation_template=(
                    "You believe in living documents ('{principle}'), "
                    "but {value}% of notes haven't been updated in 90+ days. "
                    "Is this intentional archival or unintended decay?"
                ),
            ),
            # Rule 5: Organization/structure vs. tag chaos
            TensionRule(
                name="organization_gap",
                description="Detects gap between organization ideals and tag usage",
                principle_keywords=(
                    "organize",
                    "structure",
                    "categorize",
                    "tag",
                    "folder",
                    "system",
                ),
                pattern_types=(PatternType.TAG_USAGE, PatternType.FOLDER_STRUCTURE),
                calculate_divergence=self._calc_organization_divergence,
                tension_type=TensionType.BEHAVIORAL,
                interpretation_template=(
                    "You value organization ('{principle}'), "
                    "but only {value}% of notes have tags. "
                    "Consider if your tagging practice matches your organizational goals."
                ),
            ),
        ]

    # =========================================================================
    # Divergence Calculation Functions
    # =========================================================================

    def _calc_daily_note_divergence(
        self, principle: Thesis, observation: PatternObservation
    ) -> float:
        """Calculate divergence for daily note patterns."""
        if observation.pattern_type == PatternType.DAILY_NOTE_USAGE:
            if "links" in observation.description.lower():
                # Percentage of daily notes WITHOUT links indicates divergence
                if isinstance(observation.value, (int, float)):
                    # If 30% have links, 70% don't → 0.7 divergence
                    pct_with_links = observation.value / 100
                    return 1.0 - pct_with_links
        elif observation.pattern_type == PatternType.ORPHAN_NOTES:
            if isinstance(observation.value, (int, float)):
                return observation.value / 100
        return 0.0

    def _calc_connection_divergence(
        self, principle: Thesis, observation: PatternObservation
    ) -> float:
        """Calculate divergence for connection patterns."""
        if isinstance(observation.value, (int, float)):
            # Higher orphan % = higher divergence
            if observation.pattern_type == PatternType.ORPHAN_NOTES:
                return observation.value / 100
            # Higher % no links = higher divergence
            if observation.pattern_type == PatternType.CONNECTION_PATTERNS:
                return observation.value / 100
        return 0.0

    def _calc_depth_divergence(
        self, principle: Thesis, observation: PatternObservation
    ) -> float:
        """Calculate divergence for depth patterns."""
        if observation.pattern_type == PatternType.NOTE_LENGTH:
            if "under 100 words" in observation.description.lower():
                if isinstance(observation.value, (int, float)):
                    # High % short notes = high divergence
                    return observation.value / 100
            elif "average" in observation.description.lower():
                if isinstance(observation.value, (int, float)):
                    # Low average word count = high divergence
                    # Threshold: 200 words is "deep enough"
                    avg_words = observation.value
                    if avg_words < 50:
                        return 0.9
                    elif avg_words < 100:
                        return 0.7
                    elif avg_words < 200:
                        return 0.4
                    else:
                        return 0.1
        return 0.0

    def _calc_staleness_divergence(
        self, principle: Thesis, observation: PatternObservation
    ) -> float:
        """Calculate divergence for staleness patterns."""
        if observation.pattern_type == PatternType.STALENESS:
            if isinstance(observation.value, (int, float)):
                # High % stale = high divergence
                return observation.value / 100
        elif observation.pattern_type == PatternType.UPDATE_FREQUENCY:
            if (
                "average" in observation.description.lower()
                and "age" in observation.description.lower()
            ):
                if isinstance(observation.value, (int, float)):
                    # High average age = high divergence
                    avg_age_days = observation.value
                    if avg_age_days > 180:
                        return 0.9
                    elif avg_age_days > 90:
                        return 0.7
                    elif avg_age_days > 30:
                        return 0.4
                    else:
                        return 0.1
        return 0.0

    def _calc_organization_divergence(
        self, principle: Thesis, observation: PatternObservation
    ) -> float:
        """Calculate divergence for organization patterns."""
        if observation.pattern_type == PatternType.TAG_USAGE:
            if (
                "percentage" in observation.description.lower()
                and "tags" in observation.description.lower()
            ):
                if isinstance(observation.value, (int, float)):
                    # Low % tagged = high divergence
                    pct_tagged = observation.value / 100
                    return 1.0 - pct_tagged
        return 0.0


# =============================================================================
# Convenience Functions
# =============================================================================


def detect_tensions(
    principles: list[Thesis],
    observations: list[PatternObservation],
    config: MirrorConfig | None = None,
) -> list[Tension]:
    """
    Detect tensions between principles and observations.

    This is the main entry point for tension detection.

    Args:
        principles: Extracted principles
        observations: Observed patterns
        config: Optional configuration

    Returns:
        List of detected Tensions
    """
    detector = ObsidianTensionDetector(config)
    return detector.detect(principles, observations)


def generate_mirror_report(
    vault_path: str,
    principles: list[Thesis],
    observations: list[PatternObservation],
    tensions: list[Tension],
    duration_seconds: float = 0.0,
) -> MirrorReport:
    """
    Generate a Mirror Report from analysis results.

    Args:
        vault_path: Path to the analyzed vault
        principles: Extracted principles
        observations: Observed patterns
        tensions: Detected tensions
        duration_seconds: Analysis duration

    Returns:
        MirrorReport ready for display
    """
    if not tensions:
        # No tensions found - perfect alignment (rare!)
        return MirrorReport(
            thesis=principles[0]
            if principles
            else Thesis(
                content="No principles extracted",
                source=vault_path,
                confidence=0.0,
            ),
            antithesis=Antithesis(
                pattern="No contradictions detected",
                evidence=(),
            ),
            divergence=0.0,
            reflection="Your vault shows strong alignment between stated principles and actual patterns. This is rare—consider whether you're being honest with yourself.",
            all_tensions=[],
            all_principles=principles,
            all_patterns=observations,
            vault_path=vault_path,
            analysis_duration_seconds=duration_seconds,
        )

    # Use the most significant tension
    top_tension = tensions[0]

    # Generate reflection prompt
    reflection = _generate_reflection(top_tension)

    return MirrorReport(
        thesis=top_tension.thesis,
        antithesis=top_tension.antithesis,
        divergence=top_tension.divergence,
        reflection=reflection,
        all_tensions=tensions,
        all_principles=principles,
        all_patterns=observations,
        vault_path=vault_path,
        analysis_duration_seconds=duration_seconds,
    )


def _generate_reflection(tension: Tension) -> str:
    """Generate a reflection prompt for a tension."""
    if tension.interpretation:
        base = tension.interpretation
    else:
        base = (
            f"You wrote '{tension.thesis.content}' "
            f"but your vault shows: {tension.antithesis.pattern}."
        )

    # Add reflection questions based on tension type
    questions = {
        TensionType.BEHAVIORAL: "What would it take to align your behavior with this principle?",
        TensionType.ASPIRATIONAL: "Is this principle aspirational, or do you genuinely want to change?",
        TensionType.OUTDATED: "Has this principle served its purpose? Should it be revised?",
        TensionType.CONTEXTUAL: "In what contexts does this principle apply?",
        TensionType.FUNDAMENTAL: "This seems like a deep conflict. What choice are you making?",
    }

    question = questions.get(
        tension.tension_type, "What does this gap tell you about yourself?"
    )

    return f"{base}\n\n{question}"
