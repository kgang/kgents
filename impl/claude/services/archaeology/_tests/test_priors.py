"""
Tests for priors.py - ASHC prior extraction from archaeological analysis.

Tests cover:
- SpecPattern extraction and correlation
- EvolutionTrace phase detection
- CausalPrior calculation
- Report generation
"""

from datetime import datetime, timedelta, timezone

import pytest

from services.archaeology.classifier import FeatureStatus, FeatureTrajectory
from services.archaeology.mining import Commit
from services.archaeology.patterns import FeaturePattern
from services.archaeology.priors import (
    CausalPrior,
    EvolutionPhase,
    EvolutionTrace,
    SpecPattern,
    extract_causal_priors,
    extract_evolution_traces,
    extract_spec_patterns,
    generate_prior_report,
)

# Fixtures


def make_commit(
    sha: str = "abc123",
    message: str = "feat: add feature",
    files: tuple[str, ...] = ("src/foo.py",),
    days_ago: int = 0,
    insertions: int = 50,
    deletions: int = 10,
) -> Commit:
    """Create a test commit."""
    return Commit(
        sha=sha,
        message=message,
        author="test@example.com",
        timestamp=datetime.now(timezone.utc) - timedelta(days=days_ago),
        files_changed=files,
        insertions=insertions,
        deletions=deletions,
    )


def make_trajectory(
    name: str,
    status: FeatureStatus,
    commit_count: int = 10,
    has_tests: bool = True,
    test_count: int = 5,
    velocity: float = 0.5,
    spec_patterns: tuple[str, ...] = ("spec/foo/",),
    impl_patterns: tuple[str, ...] = ("impl/foo/",),
) -> FeatureTrajectory:
    """Create a test trajectory with given properties."""
    now = datetime.now(timezone.utc)

    # Generate commits spread over time
    commits = []
    for i in range(commit_count):
        # More recent commits if high velocity
        days_ago = i * (1 if velocity > 0.3 else 5)
        files = [f"impl/foo/file{i}.py"]
        if has_tests and i < test_count:
            files.append(f"impl/foo/test_file{i}.py")

        commits.append(
            make_commit(
                sha=f"commit{i}",
                message=f"feat({name.lower()}): commit {i}",
                files=tuple(files),
                days_ago=days_ago,
            )
        )

    pattern = FeaturePattern(
        name=name,
        impl_patterns=impl_patterns,
        spec_patterns=spec_patterns,
        test_patterns=(),
    )

    return FeatureTrajectory(
        name=name,
        pattern=pattern,
        commits=tuple(commits),
        status=status,
        has_tests=has_tests,
        test_count=test_count,
    )


# SpecPattern tests


class TestSpecPattern:
    """Tests for SpecPattern dataclass."""

    def test_pattern_is_frozen(self):
        """SpecPattern should be immutable."""
        pattern = SpecPattern(
            pattern_type="test",
            example_specs=("spec/a.md",),
            success_correlation=0.8,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            pattern.pattern_type = "changed"  # type: ignore

    def test_confidence_increases_with_samples(self):
        """More examples should increase confidence."""
        low_samples = SpecPattern(
            pattern_type="test",
            example_specs=("spec/a.md",),
            success_correlation=0.8,
        )
        high_samples = SpecPattern(
            pattern_type="test",
            example_specs=("spec/a.md", "spec/b.md", "spec/c.md", "spec/d.md", "spec/e.md"),
            success_correlation=0.8,
        )
        assert high_samples.confidence > low_samples.confidence

    def test_confidence_capped_at_correlation(self):
        """Confidence should not exceed correlation."""
        pattern = SpecPattern(
            pattern_type="test",
            example_specs=tuple(f"spec/{i}.md" for i in range(20)),
            success_correlation=0.5,
        )
        assert pattern.confidence <= 0.5


# EvolutionTrace tests


class TestEvolutionTrace:
    """Tests for EvolutionTrace dataclass."""

    def test_spec_first_detection(self):
        """Should detect when spec was written before impl."""
        commits = (
            make_commit(sha="1", files=("spec/foo.md",), days_ago=10),
            make_commit(sha="2", files=("impl/foo.py",), days_ago=5),
        )
        trace = EvolutionTrace(
            feature_name="Foo",
            spec_paths=("spec/foo",),
            impl_paths=("impl/foo",),
            commits=commits,
            phases=(EvolutionPhase.SPEC_DRAFT, EvolutionPhase.INITIAL_IMPL),
            final_status=FeatureStatus.STABLE,
        )
        assert trace.spec_first is True

    def test_impl_first_detection(self):
        """Should detect when impl was written before spec."""
        commits = (
            make_commit(sha="1", files=("impl/foo.py",), days_ago=10),
            make_commit(sha="2", files=("spec/foo.md",), days_ago=5),
        )
        trace = EvolutionTrace(
            feature_name="Foo",
            spec_paths=("spec/foo",),
            impl_paths=("impl/foo",),
            commits=commits,
            phases=(EvolutionPhase.INITIAL_IMPL, EvolutionPhase.SPEC_DRAFT),
            final_status=FeatureStatus.STABLE,
        )
        assert trace.spec_first is False

    def test_spec_impl_ratio(self):
        """Should calculate ratio of spec to impl commits."""
        commits = (
            make_commit(sha="1", files=("spec/foo.md",), days_ago=10),
            make_commit(sha="2", files=("impl/foo.py",), days_ago=9),
            make_commit(sha="3", files=("impl/foo.py",), days_ago=8),
        )
        trace = EvolutionTrace(
            feature_name="Foo",
            spec_paths=("spec/foo",),
            impl_paths=("impl/foo",),
            commits=commits,
            phases=(),
            final_status=FeatureStatus.STABLE,
        )
        assert trace.spec_impl_ratio == 0.5  # 1 spec / 2 impl

    def test_days_to_stabilize(self):
        """Should calculate days from first commit to first test."""
        commits = (
            make_commit(sha="1", files=("impl/foo.py",), days_ago=20),
            make_commit(sha="2", files=("impl/test_foo.py",), days_ago=10),
        )
        trace = EvolutionTrace(
            feature_name="Foo",
            spec_paths=(),
            impl_paths=("impl/",),
            commits=commits,
            phases=(),
            final_status=FeatureStatus.STABLE,
        )
        assert trace.days_to_stabilize == 10


# CausalPrior tests


class TestCausalPrior:
    """Tests for CausalPrior dataclass."""

    def test_positive_effect_direction(self):
        """Positive correlation should show as positive."""
        prior = CausalPrior(
            pattern="feat: prefix",
            outcome_correlation=0.2,
            sample_size=50,
            confidence=0.3,
        )
        assert prior.effect_direction == "positive"

    def test_negative_effect_direction(self):
        """Negative correlation should show as negative."""
        prior = CausalPrior(
            pattern="WIP prefix",
            outcome_correlation=-0.15,
            sample_size=20,
            confidence=0.2,
        )
        assert prior.effect_direction == "negative"

    def test_neutral_effect_direction(self):
        """Near-zero correlation should show as neutral."""
        prior = CausalPrior(
            pattern="minor: prefix",
            outcome_correlation=0.05,
            sample_size=30,
            confidence=0.3,
        )
        assert prior.effect_direction == "neutral"


# Extraction tests


class TestExtractSpecPatterns:
    """Tests for extract_spec_patterns."""

    def test_extracts_early_test_pattern(self):
        """Should extract early test adoption pattern."""
        trajectories = [
            make_trajectory("A", FeatureStatus.THRIVING, has_tests=True, test_count=5),
            make_trajectory("B", FeatureStatus.STABLE, has_tests=True, test_count=3),
            make_trajectory("C", FeatureStatus.ABANDONED, has_tests=False),
        ]

        patterns = extract_spec_patterns(trajectories)
        pattern_types = [p.pattern_type for p in patterns]

        assert "early_test_adoption" in pattern_types

    def test_extracts_high_velocity_pattern(self):
        """Should extract sustained momentum pattern."""
        trajectories = [
            make_trajectory("A", FeatureStatus.THRIVING, velocity=0.8),
            make_trajectory("B", FeatureStatus.THRIVING, velocity=0.6),
            make_trajectory("C", FeatureStatus.STABLE, velocity=0.2),
        ]

        patterns = extract_spec_patterns(trajectories)
        pattern_types = [p.pattern_type for p in patterns]

        assert "sustained_momentum" in pattern_types

    def test_no_patterns_from_empty_trajectories(self):
        """Should return empty list for no trajectories."""
        patterns = extract_spec_patterns([])
        assert patterns == []


class TestExtractEvolutionTraces:
    """Tests for extract_evolution_traces."""

    def test_creates_traces_with_phases(self):
        """Should create evolution traces with detected phases."""
        trajectories = [
            make_trajectory("A", FeatureStatus.THRIVING),
            make_trajectory("B", FeatureStatus.STABLE),
        ]

        traces = extract_evolution_traces(trajectories)

        assert len(traces) == 2
        for trace in traces:
            assert trace.feature_name in ["A", "B"]

    def test_skips_features_without_patterns(self):
        """Should skip features with no spec/impl patterns."""
        pattern = FeaturePattern(
            name="NoPatterns",
            impl_patterns=(),
            spec_patterns=(),
        )
        trajectory = FeatureTrajectory(
            name="NoPatterns",
            pattern=pattern,
            commits=(make_commit(),),
            status=FeatureStatus.ABANDONED,
        )

        traces = extract_evolution_traces([trajectory])

        assert len(traces) == 0


class TestExtractCausalPriors:
    """Tests for extract_causal_priors."""

    def test_extracts_feat_prefix_prior(self):
        """Should extract prior for feat: commits."""
        trajectories = [
            make_trajectory("A", FeatureStatus.THRIVING, commit_count=20),
            make_trajectory("B", FeatureStatus.STABLE, commit_count=15),
        ]

        priors = extract_causal_priors(trajectories)
        patterns = [p.pattern for p in priors]

        assert "feat: prefix" in patterns

    def test_prior_has_reasonable_confidence(self):
        """Archaeological priors should have lower confidence."""
        trajectories = [
            make_trajectory("A", FeatureStatus.THRIVING, commit_count=30),
        ]

        priors = extract_causal_priors(trajectories)

        for prior in priors:
            assert prior.confidence <= 0.5  # Archaeological confidence is lower


# Report tests


class TestGeneratePriorReport:
    """Tests for generate_prior_report."""

    def test_report_includes_header(self):
        """Report should include title."""
        report = generate_prior_report([], [], [])
        assert "# ASHC Prior Extraction Report" in report

    def test_report_includes_patterns(self):
        """Report should include pattern table."""
        patterns = [
            SpecPattern(
                pattern_type="early_test_adoption",
                example_specs=("A", "B"),
                success_correlation=0.75,
            )
        ]
        report = generate_prior_report(patterns, [], [])
        assert "early_test_adoption" in report
        assert "75%" in report

    def test_report_includes_priors(self):
        """Report should include causal priors."""
        priors = [
            CausalPrior(
                pattern="feat: prefix",
                outcome_correlation=0.15,
                sample_size=50,
                confidence=0.3,
            )
        ]
        report = generate_prior_report([], [], priors)
        assert "feat: prefix" in report
        assert "positive" in report
