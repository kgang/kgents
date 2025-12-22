"""
Prior Extraction: Build causal priors for ASHC from archaeological analysis.

Extracts patterns from successful features to guide the metacompiler:
- SpecPattern: Patterns that correlate with feature success
- EvolutionTrace: How spec/impl pairs evolved over time
- CausalPrior: Nudge → outcome relationships

See: spec/protocols/repo-archaeology.md (Phase 3)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Sequence

from .classifier import FeatureStatus, FeatureTrajectory
from .mining import Commit


class EvolutionPhase(Enum):
    """Phases in a feature's evolution from spec to implementation."""

    SPEC_DRAFT = "spec_draft"  # Initial spec written
    INITIAL_IMPL = "initial_impl"  # First implementation
    ITERATION = "iteration"  # Spec-impl back-and-forth
    STABILIZATION = "stabilization"  # Tests passing, bugs fixed
    POLISH = "polish"  # Docs, cleanup, refinement
    ABANDONMENT = "abandonment"  # Activity stops


@dataclass(frozen=True)
class SpecPattern:
    """
    A pattern extracted from successful specs.

    These patterns become priors for ASHC's causal graph,
    guiding which spec structures lead to successful features.
    """

    pattern_type: str  # e.g., "polynomial_definition", "agentese_integration"
    example_specs: tuple[str, ...]  # Paths to specs that use this pattern
    success_correlation: float  # How often specs with this pattern succeeded (0.0 to 1.0)
    description: str = ""  # Human-readable description

    @property
    def confidence(self) -> float:
        """Confidence based on sample size and correlation."""
        # More examples = higher confidence (up to 0.9)
        sample_factor = min(len(self.example_specs) / 5.0, 0.9)
        return self.success_correlation * sample_factor


@dataclass(frozen=True)
class EvolutionTrace:
    """
    How a spec/impl pair evolved over time.

    Tracks the full lifecycle from initial spec to current state,
    identifying phase transitions and key commits.
    """

    feature_name: str
    spec_paths: tuple[str, ...]
    impl_paths: tuple[str, ...]
    commits: tuple[Commit, ...]
    phases: tuple[EvolutionPhase, ...]
    final_status: FeatureStatus

    @property
    def spec_first(self) -> bool:
        """Was the spec written before implementation?"""
        spec_commits = [
            c
            for c in self.commits
            if any(sp in f for sp in self.spec_paths for f in c.files_changed)
        ]
        impl_commits = [
            c
            for c in self.commits
            if any(ip in f for ip in self.impl_paths for f in c.files_changed)
        ]

        if not spec_commits or not impl_commits:
            return False

        first_spec = min(spec_commits, key=lambda c: c.timestamp)
        first_impl = min(impl_commits, key=lambda c: c.timestamp)
        return first_spec.timestamp < first_impl.timestamp

    @property
    def spec_impl_ratio(self) -> float:
        """Ratio of spec commits to impl commits."""
        spec_count = sum(
            1
            for c in self.commits
            if any(sp in f for sp in self.spec_paths for f in c.files_changed)
        )
        impl_count = sum(
            1
            for c in self.commits
            if any(ip in f for ip in self.impl_paths for f in c.files_changed)
        )
        if impl_count == 0:
            return float("inf") if spec_count > 0 else 0.0
        return spec_count / impl_count

    @property
    def days_to_stabilize(self) -> int:
        """Days from first commit to first test commit."""
        if not self.commits:
            return -1

        first = min(self.commits, key=lambda c: c.timestamp)
        test_commits = [
            c for c in self.commits if any("test" in f.lower() for f in c.files_changed)
        ]

        if not test_commits:
            return -1

        first_test = min(test_commits, key=lambda c: c.timestamp)
        return (first_test.timestamp - first.timestamp).days


@dataclass(frozen=True)
class CausalPrior:
    """
    A causal relationship from archaeological evidence.

    Maps nudge patterns (commit types, message patterns) to outcomes (feature status).
    Lower confidence than runtime ASHC evidence, but provides initial priors.
    """

    pattern: str  # The nudge pattern (e.g., "feat(X): ", "WIP")
    outcome_correlation: float  # -1.0 (negative) to 1.0 (positive)
    sample_size: int  # Number of observations
    confidence: float  # Archaeological confidence (lower than runtime)

    @property
    def effect_direction(self) -> str:
        """Human-readable effect direction."""
        if self.outcome_correlation > 0.1:
            return "positive"
        elif self.outcome_correlation < -0.1:
            return "negative"
        return "neutral"


def extract_spec_patterns(
    trajectories: Sequence[FeatureTrajectory],
) -> list[SpecPattern]:
    """
    Extract spec patterns that correlate with success.

    Args:
        trajectories: All classified feature trajectories

    Returns:
        List of SpecPattern with success correlations
    """
    successful = [
        t for t in trajectories if t.status in (FeatureStatus.THRIVING, FeatureStatus.STABLE)
    ]
    total_features = len([t for t in trajectories if t.total_commits > 0])

    if total_features == 0:
        return []

    patterns: list[SpecPattern] = []

    # Pattern: Tests present within first 10 commits
    early_tests = [t for t in successful if t.has_tests and _has_early_tests(t)]
    if len(early_tests) >= 2:
        patterns.append(
            SpecPattern(
                pattern_type="early_test_adoption",
                example_specs=tuple(t.name for t in early_tests[:5]),
                success_correlation=len(early_tests) / max(len(successful), 1),
                description="Tests added within first 10 commits",
            )
        )

    # Pattern: High velocity sustained
    high_velocity = [t for t in successful if t.velocity > 0.5]
    if len(high_velocity) >= 2:
        patterns.append(
            SpecPattern(
                pattern_type="sustained_momentum",
                example_specs=tuple(t.name for t in high_velocity[:5]),
                success_correlation=len(high_velocity) / max(len(successful), 1),
                description="High velocity (>0.5) sustained through development",
            )
        )

    # Pattern: Low churn (focused development)
    low_churn = [t for t in successful if 0 < t.churn < 100]
    if len(low_churn) >= 2:
        patterns.append(
            SpecPattern(
                pattern_type="focused_development",
                example_specs=tuple(t.name for t in low_churn[:5]),
                success_correlation=len(low_churn) / max(len(successful), 1),
                description="Low churn (<100 lines/commit average)",
            )
        )

    # Pattern: Conventional commits
    conventional = [t for t in successful if _uses_conventional_commits(t)]
    if len(conventional) >= 2:
        patterns.append(
            SpecPattern(
                pattern_type="conventional_commits",
                example_specs=tuple(t.name for t in conventional[:5]),
                success_correlation=len(conventional) / max(len(successful), 1),
                description="Uses conventional commit messages (feat:, fix:, etc.)",
            )
        )

    # Pattern: Spec and impl co-evolution
    co_evolved = [t for t in successful if _has_spec_impl_coevolution(t)]
    if len(co_evolved) >= 2:
        patterns.append(
            SpecPattern(
                pattern_type="spec_impl_coevolution",
                example_specs=tuple(t.name for t in co_evolved[:5]),
                success_correlation=len(co_evolved) / max(len(successful), 1),
                description="Spec and impl files evolve together",
            )
        )

    return patterns


def extract_evolution_traces(
    trajectories: Sequence[FeatureTrajectory],
) -> list[EvolutionTrace]:
    """
    Build evolution traces for features with both spec and impl.

    Args:
        trajectories: All classified feature trajectories

    Returns:
        List of EvolutionTrace with phase analysis
    """
    traces: list[EvolutionTrace] = []

    for t in trajectories:
        if not t.commits:
            continue

        # Collect spec and impl paths from pattern
        spec_paths = t.pattern.spec_patterns
        impl_paths = t.pattern.impl_patterns

        if not spec_paths and not impl_paths:
            continue

        # Determine phases based on commit patterns
        phases = _determine_phases(t.commits, spec_paths, impl_paths)

        traces.append(
            EvolutionTrace(
                feature_name=t.name,
                spec_paths=spec_paths,
                impl_paths=impl_paths,
                commits=t.commits,
                phases=tuple(phases),
                final_status=t.status,
            )
        )

    return traces


def extract_causal_priors(
    trajectories: Sequence[FeatureTrajectory],
) -> list[CausalPrior]:
    """
    Extract causal priors from commit patterns.

    Args:
        trajectories: All classified feature trajectories

    Returns:
        List of CausalPrior with outcome correlations
    """
    priors: list[CausalPrior] = []

    # Collect all commits with their outcome
    commit_outcomes: list[tuple[Commit, bool]] = []
    for t in trajectories:
        is_success = t.status in (FeatureStatus.THRIVING, FeatureStatus.STABLE)
        for c in t.commits:
            commit_outcomes.append((c, is_success))

    if not commit_outcomes:
        return priors

    # Pattern: "feat:" prefix
    feat_commits = [(c, o) for c, o in commit_outcomes if c.commit_type == "feat"]
    if len(feat_commits) >= 5:
        success_rate = sum(1 for _, o in feat_commits if o) / len(feat_commits)
        baseline = sum(1 for _, o in commit_outcomes if o) / len(commit_outcomes)
        priors.append(
            CausalPrior(
                pattern="feat: prefix",
                outcome_correlation=success_rate - baseline,
                sample_size=len(feat_commits),
                confidence=0.3,  # Archaeological confidence
            )
        )

    # Pattern: "fix:" prefix
    fix_commits = [(c, o) for c, o in commit_outcomes if c.commit_type == "fix"]
    if len(fix_commits) >= 5:
        success_rate = sum(1 for _, o in fix_commits if o) / len(fix_commits)
        baseline = sum(1 for _, o in commit_outcomes if o) / len(commit_outcomes)
        priors.append(
            CausalPrior(
                pattern="fix: prefix",
                outcome_correlation=success_rate - baseline,
                sample_size=len(fix_commits),
                confidence=0.3,
            )
        )

    # Pattern: "refactor:" prefix
    refactor_commits = [(c, o) for c, o in commit_outcomes if c.commit_type == "refactor"]
    if len(refactor_commits) >= 5:
        success_rate = sum(1 for _, o in refactor_commits if o) / len(refactor_commits)
        baseline = sum(1 for _, o in commit_outcomes if o) / len(commit_outcomes)
        priors.append(
            CausalPrior(
                pattern="refactor: prefix",
                outcome_correlation=success_rate - baseline,
                sample_size=len(refactor_commits),
                confidence=0.3,
            )
        )

    # Pattern: Small commits (is_fix property)
    small_commits = [(c, o) for c, o in commit_outcomes if c.is_fix]
    if len(small_commits) >= 5:
        success_rate = sum(1 for _, o in small_commits if o) / len(small_commits)
        baseline = sum(1 for _, o in commit_outcomes if o) / len(commit_outcomes)
        priors.append(
            CausalPrior(
                pattern="small_targeted_changes",
                outcome_correlation=success_rate - baseline,
                sample_size=len(small_commits),
                confidence=0.25,
            )
        )

    # Pattern: High churn commits
    high_churn = [(c, o) for c, o in commit_outcomes if c.churn > 500]
    if len(high_churn) >= 5:
        success_rate = sum(1 for _, o in high_churn if o) / len(high_churn)
        baseline = sum(1 for _, o in commit_outcomes if o) / len(commit_outcomes)
        priors.append(
            CausalPrior(
                pattern="high_churn_commits",
                outcome_correlation=success_rate - baseline,
                sample_size=len(high_churn),
                confidence=0.25,
            )
        )

    return priors


def generate_prior_report(
    patterns: Sequence[SpecPattern],
    traces: Sequence[EvolutionTrace],
    priors: Sequence[CausalPrior],
) -> str:
    """
    Generate a human-readable prior extraction report.

    Args:
        patterns: Extracted spec patterns
        traces: Evolution traces
        priors: Causal priors

    Returns:
        Markdown-formatted report
    """
    lines = [
        "# ASHC Prior Extraction Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Spec Patterns Correlated with Success",
        "",
        "| Pattern | Success Rate | Confidence | Examples |",
        "|---------|--------------|------------|----------|",
    ]

    for spec_pattern in sorted(patterns, key=lambda x: x.success_correlation, reverse=True):
        examples = ", ".join(spec_pattern.example_specs[:3])
        lines.append(
            f"| {spec_pattern.pattern_type} | {spec_pattern.success_correlation:.0%} | "
            f"{spec_pattern.confidence:.0%} | {examples} |"
        )

    lines.extend(
        [
            "",
            "## Evolution Insights",
            "",
        ]
    )

    spec_first_count = sum(1 for t in traces if t.spec_first)
    total_traces = len(traces)
    if total_traces > 0:
        lines.append(f"- **Spec-first development**: {spec_first_count}/{total_traces} features")

    successful_traces = [
        t for t in traces if t.final_status in (FeatureStatus.THRIVING, FeatureStatus.STABLE)
    ]
    if successful_traces:
        avg_days = sum(t.days_to_stabilize for t in successful_traces if t.days_to_stabilize >= 0)
        count = sum(1 for t in successful_traces if t.days_to_stabilize >= 0)
        if count > 0:
            lines.append(f"- **Average days to first test**: {avg_days / count:.0f}")

    lines.extend(
        [
            "",
            "## Causal Priors (for ASHC CausalGraph)",
            "",
            "| Pattern | Correlation | Direction | Sample Size |",
            "|---------|-------------|-----------|-------------|",
        ]
    )

    for causal_prior in sorted(priors, key=lambda x: abs(x.outcome_correlation), reverse=True):
        direction = (
            "+"
            if causal_prior.outcome_correlation > 0
            else "-"
            if causal_prior.outcome_correlation < 0
            else "~"
        )
        lines.append(
            f"| {causal_prior.pattern} | {direction}{abs(causal_prior.outcome_correlation):.0%} | "
            f"{causal_prior.effect_direction} | {causal_prior.sample_size} |"
        )

    lines.append("")
    return "\n".join(lines)


# Helper functions


def _has_early_tests(trajectory: FeatureTrajectory) -> bool:
    """Check if tests were added within first 10 commits."""
    sorted_commits = sorted(trajectory.commits, key=lambda c: c.timestamp)
    first_10 = sorted_commits[:10]
    return any("test" in f.lower() or "_tests" in f for c in first_10 for f in c.files_changed)


def _uses_conventional_commits(trajectory: FeatureTrajectory) -> bool:
    """Check if feature uses conventional commit messages."""
    conventional_types = {"feat", "fix", "refactor", "docs", "test", "chore", "style"}
    conventional_count = sum(1 for c in trajectory.commits if c.commit_type in conventional_types)
    return conventional_count > len(trajectory.commits) * 0.5


def _has_spec_impl_coevolution(trajectory: FeatureTrajectory) -> bool:
    """Check if spec and impl files evolved together."""
    spec_patterns = trajectory.pattern.spec_patterns
    impl_patterns = trajectory.pattern.impl_patterns

    if not spec_patterns or not impl_patterns:
        return False

    # Count commits that touch both spec and impl
    both_count = 0
    for c in trajectory.commits:
        has_spec = any(sp in f for sp in spec_patterns for f in c.files_changed)
        has_impl = any(ip in f for ip in impl_patterns for f in c.files_changed)
        if has_spec and has_impl:
            both_count += 1

    return both_count >= 2


def _determine_phases(
    commits: tuple[Commit, ...],
    spec_paths: tuple[str, ...],
    impl_paths: tuple[str, ...],
) -> list[EvolutionPhase]:
    """Determine evolution phases from commit sequence."""
    if not commits:
        return []

    phases: list[EvolutionPhase] = []
    sorted_commits = sorted(commits, key=lambda c: c.timestamp)

    # Track what we've seen
    seen_spec = False
    seen_impl = False
    seen_test = False

    for c in sorted_commits:
        has_spec = any(sp in f for sp in spec_paths for f in c.files_changed)
        has_impl = any(ip in f for ip in impl_paths for f in c.files_changed)
        has_test = any("test" in f.lower() for f in c.files_changed)

        if has_spec and not seen_spec:
            phases.append(EvolutionPhase.SPEC_DRAFT)
            seen_spec = True
        elif has_impl and not seen_impl:
            phases.append(EvolutionPhase.INITIAL_IMPL)
            seen_impl = True
        elif has_spec and has_impl:
            if EvolutionPhase.ITERATION not in phases:
                phases.append(EvolutionPhase.ITERATION)
        elif has_test and not seen_test:
            phases.append(EvolutionPhase.STABILIZATION)
            seen_test = True

    # Check for polish phase (docs, cleanup in late commits)
    late_commits = sorted_commits[-3:]
    for c in late_commits:
        if c.commit_type in ("docs", "chore", "style"):
            if EvolutionPhase.POLISH not in phases:
                phases.append(EvolutionPhase.POLISH)
            break

    return phases
