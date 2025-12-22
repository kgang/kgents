"""
Crystal Generation: Create HistoryCrystals for Brain from archaeological analysis.

Crystals are crystallized memories of a feature's journey—compact, rich,
and ready for storage in Kent's Brain (self.memory).

Each crystal captures:
- What worked and what didn't
- Emotional valence (frustration to joy)
- Extractable lessons
- Related design principles

See: spec/protocols/repo-archaeology.md (Phase 4)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Sequence

from .classifier import FeatureStatus, FeatureTrajectory

if TYPE_CHECKING:
    from typing import Protocol

    class BrainCore(Protocol):
        """Protocol for Brain core to avoid import cycles."""

        async def capture(self, content: str, tags: list[str], metadata: dict[str, Any]) -> Any: ...


# Design principles from the Constitution (spec/principles.md)
DESIGN_PRINCIPLES = (
    "Tasteful",
    "Curated",
    "Ethical",
    "Joy-Inducing",
    "Composable",
    "Heterarchical",
    "Generative",
)


@dataclass(frozen=True)
class HistoryCrystal:
    """
    A crystallized memory of a feature's journey.

    These crystals are stored in Brain for long-term retrieval,
    enabling Kent (and K-gent) to learn from the project's history.
    """

    feature_name: str
    summary: str  # 2-3 sentence summary
    key_insights: tuple[str, ...]  # What worked, what didn't
    emotional_valence: float  # -1.0 (frustration) to 1.0 (joy)
    lessons: tuple[str, ...]  # Extractable wisdom
    related_principles: tuple[str, ...]  # Which design principles were at play
    status: FeatureStatus
    commit_count: int
    first_active: datetime | None
    last_active: datetime | None

    def to_brain_crystal(self) -> dict[str, Any]:
        """
        Format for Brain Crown Jewel storage.

        Compatible with self.memory.capture() API.
        """
        content_parts = [
            f"# {self.feature_name}: Feature Archaeology",
            "",
            self.summary,
            "",
            "## Key Insights",
            *[f"- {insight}" for insight in self.key_insights],
            "",
            "## Lessons Learned",
            *[f"- {lesson}" for lesson in self.lessons],
        ]

        if self.related_principles:
            content_parts.extend(
                [
                    "",
                    "## Related Principles",
                    *[f"- {p}" for p in self.related_principles],
                ]
            )

        return {
            "content": "\n".join(content_parts),
            "tags": ["archaeology", "history", self.feature_name.lower(), self.status.value],
            "metadata": {
                "type": "history_crystal",
                "feature": self.feature_name,
                "status": self.status.value,
                "valence": self.emotional_valence,
                "commit_count": self.commit_count,
                "first_active": self.first_active.isoformat() if self.first_active else None,
                "last_active": self.last_active.isoformat() if self.last_active else None,
            },
        }


def generate_history_crystal(trajectory: FeatureTrajectory) -> HistoryCrystal:
    """
    Generate a HistoryCrystal from a feature trajectory.

    This is a heuristic-based generator—for richer summaries,
    use LLM-assisted generation (see generate_history_crystals_llm).

    Args:
        trajectory: The classified feature trajectory

    Returns:
        A HistoryCrystal ready for Brain storage
    """
    # Generate summary based on status and metrics
    summary = _generate_summary(trajectory)

    # Extract insights from commit patterns
    insights = _extract_insights(trajectory)

    # Calculate emotional valence from status and trajectory
    valence = _calculate_valence(trajectory)

    # Extract lessons based on the journey
    lessons = _extract_lessons(trajectory)

    # Identify related principles
    principles = _identify_principles(trajectory)

    return HistoryCrystal(
        feature_name=trajectory.name,
        summary=summary,
        key_insights=tuple(insights),
        emotional_valence=valence,
        lessons=tuple(lessons),
        related_principles=tuple(principles),
        status=trajectory.status,
        commit_count=trajectory.total_commits,
        first_active=trajectory.first_commit.timestamp if trajectory.first_commit else None,
        last_active=trajectory.last_commit.timestamp if trajectory.last_commit else None,
    )


def generate_all_crystals(
    trajectories: Sequence[FeatureTrajectory],
    min_commits: int = 5,
) -> list[HistoryCrystal]:
    """
    Generate crystals for all significant features.

    Args:
        trajectories: All classified trajectories
        min_commits: Minimum commits for a crystal

    Returns:
        List of HistoryCrystals for storage
    """
    return [generate_history_crystal(t) for t in trajectories if t.total_commits >= min_commits]


async def store_crystals_in_brain(
    crystals: Sequence[HistoryCrystal],
    brain: "BrainCore",
) -> int:
    """
    Store crystals in Brain via self.memory.capture.

    Args:
        crystals: Crystals to store
        brain: Brain instance

    Returns:
        Number of crystals stored
    """
    stored = 0
    for crystal in crystals:
        brain_data = crystal.to_brain_crystal()
        await brain.capture(
            content=brain_data["content"],
            tags=brain_data["tags"],
            metadata=brain_data["metadata"],
        )
        stored += 1

    return stored


def generate_crystal_report(crystals: Sequence[HistoryCrystal]) -> str:
    """
    Generate a summary report of all crystals.

    Args:
        crystals: Generated crystals

    Returns:
        Markdown report
    """
    lines = [
        "# History Crystals Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Total Crystals: {len(crystals)}",
        "",
        "## By Status",
        "",
    ]

    # Group by status
    by_status: dict[FeatureStatus, list[HistoryCrystal]] = {}
    for c in crystals:
        by_status.setdefault(c.status, []).append(c)

    for status in [
        FeatureStatus.THRIVING,
        FeatureStatus.STABLE,
        FeatureStatus.LANGUISHING,
        FeatureStatus.OVER_ENGINEERED,
        FeatureStatus.ABANDONED,
    ]:
        if status not in by_status:
            continue

        lines.append(f"### {status.value.upper()}")
        lines.append("")

        for c in sorted(by_status[status], key=lambda x: x.commit_count, reverse=True):
            valence_emoji = (
                "😊" if c.emotional_valence > 0.3 else "😐" if c.emotional_valence > -0.3 else "😔"
            )
            lines.append(f"**{c.feature_name}** {valence_emoji} ({c.commit_count} commits)")
            lines.append(f"> {c.summary[:100]}...")
            if c.lessons:
                lines.append(f"> *Lesson: {c.lessons[0]}*")
            lines.append("")

    # Valence distribution
    lines.extend(
        [
            "## Emotional Landscape",
            "",
        ]
    )

    joyful = [c for c in crystals if c.emotional_valence > 0.3]
    neutral = [c for c in crystals if -0.3 <= c.emotional_valence <= 0.3]
    frustrated = [c for c in crystals if c.emotional_valence < -0.3]

    lines.append(f"- 😊 Joyful: {len(joyful)} features")
    lines.append(f"- 😐 Neutral: {len(neutral)} features")
    lines.append(f"- 😔 Frustrated: {len(frustrated)} features")
    lines.append("")

    return "\n".join(lines)


# Helper functions


def _generate_summary(t: FeatureTrajectory) -> str:
    """Generate a summary based on trajectory."""
    name = t.name
    commits = t.total_commits
    velocity = t.velocity
    status = t.status

    if status == FeatureStatus.THRIVING:
        return (
            f"{name} is actively thriving with {commits} commits and high velocity ({velocity:.0%}). "
            f"Recent development shows strong momentum and test coverage. "
            f"This is a core feature worth continued investment."
        )
    elif status == FeatureStatus.STABLE:
        return (
            f"{name} has reached stability with {commits} commits. "
            f"The feature is mature with solid test coverage. "
            f"Low recent activity indicates completion rather than abandonment."
        )
    elif status == FeatureStatus.LANGUISHING:
        return (
            f"{name} started strong but activity has dropped off ({commits} commits, {velocity:.0%} velocity). "
            f"Tests exist but feature may need revival or explicit deprecation decision."
        )
    elif status == FeatureStatus.OVER_ENGINEERED:
        return (
            f"{name} shows signs of over-engineering: {commits} commits, extensive tests, "
            f"but low actual usage. Consider simplification or archival."
        )
    else:  # ABANDONED
        return (
            f"{name} appears abandoned ({commits} commits, {t.days_since_last_activity} days stale). "
            f"May lack tests or recent activity. Candidate for cleanup or revival."
        )


def _extract_insights(t: FeatureTrajectory) -> list[str]:
    """Extract insights from trajectory patterns."""
    insights: list[str] = []

    # Velocity insight
    if t.velocity > 0.5:
        insights.append(
            "High recent velocity indicates active development and Kent's focused attention."
        )
    elif t.velocity < 0.1 and t.total_commits > 10:
        insights.append("Velocity dropped significantly—either mature or potentially stalled.")

    # Churn insight
    if t.churn > 200:
        insights.append(
            f"High churn ({t.churn:.0f} lines/commit) suggests major refactoring or instability."
        )
    elif t.churn < 50 and t.total_commits > 5:
        insights.append("Low churn indicates focused, incremental development.")

    # Test insight
    if t.has_tests and t.test_count > 20:
        insights.append(
            f"Extensive test coverage ({t.test_count} test files) shows investment in quality."
        )
    elif not t.has_tests and t.total_commits > 10:
        insights.append("Lack of tests despite significant development—technical debt risk.")

    # Age insight
    if t.age_days > 90 and t.status == FeatureStatus.THRIVING:
        insights.append("Long-lived and still thriving—a core pillar of the system.")

    if not insights:
        insights.append(f"Feature has {t.total_commits} commits over {t.age_days} days.")

    return insights


def _calculate_valence(t: FeatureTrajectory) -> float:
    """
    Calculate emotional valence from -1.0 (frustration) to 1.0 (joy).

    Based on:
    - Status (thriving = joy, abandoned = frustration)
    - Velocity (high velocity = engagement = joy)
    - Test presence (tests = confidence = joy)
    """
    base_valence = {
        FeatureStatus.THRIVING: 0.8,
        FeatureStatus.STABLE: 0.5,
        FeatureStatus.LANGUISHING: -0.2,
        FeatureStatus.OVER_ENGINEERED: -0.1,
        FeatureStatus.ABANDONED: -0.5,
    }

    valence = base_valence.get(t.status, 0.0)

    # Velocity modifier
    if t.velocity > 0.5:
        valence += 0.1
    elif t.velocity < 0.1:
        valence -= 0.1

    # Test modifier
    if t.has_tests:
        valence += 0.05
    else:
        valence -= 0.1

    # Clamp to [-1.0, 1.0]
    return max(-1.0, min(1.0, valence))


def _extract_lessons(t: FeatureTrajectory) -> list[str]:
    """Extract lessons from the feature's journey."""
    lessons: list[str] = []

    if t.status == FeatureStatus.THRIVING:
        if t.has_tests:
            lessons.append("Early test investment correlates with sustained development.")
        if t.velocity > 0.5:
            lessons.append("Momentum begets momentum—focused attention yields results.")

    elif t.status == FeatureStatus.STABLE:
        lessons.append("Stability is a feature, not stagnation—know when to stop iterating.")

    elif t.status == FeatureStatus.LANGUISHING:
        lessons.append("Features without clear champions risk becoming orphans.")
        if not t.has_tests:
            lessons.append("Lack of tests makes revival harder—test early.")

    elif t.status == FeatureStatus.OVER_ENGINEERED:
        lessons.append("Over-engineering teaches what matters—complexity without users is waste.")
        lessons.append("Beautiful mistakes can become foundations for better ideas.")

    elif t.status == FeatureStatus.ABANDONED:
        lessons.append(
            "Abandoned features aren't failures—they're pruned branches enabling growth elsewhere."
        )
        if t.total_commits > 20:
            lessons.append(
                "High investment with abandonment suggests scope mismatch—check alignment early."
            )

    if not lessons:
        lessons.append(
            f"This feature's journey from {t.first_commit.timestamp.date() if t.first_commit else 'inception'} to now is worth reflection."
        )

    return lessons


def _identify_principles(t: FeatureTrajectory) -> list[str]:
    """Identify which design principles are most relevant."""
    principles: list[str] = []

    # Tasteful: Clear purpose
    if t.status in (FeatureStatus.THRIVING, FeatureStatus.STABLE):
        principles.append("Tasteful")

    # Curated: Not everything survives
    if t.status == FeatureStatus.ABANDONED:
        principles.append("Curated")

    # Composable: High commit count often indicates integration
    if t.total_commits > 30:
        principles.append("Composable")

    # Joy-Inducing: High valence
    valence = _calculate_valence(t)
    if valence > 0.5:
        principles.append("Joy-Inducing")

    # Generative: Stable features often become foundations
    if t.status == FeatureStatus.STABLE and t.has_tests:
        principles.append("Generative")

    return principles[:3]  # Limit to top 3
