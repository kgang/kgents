"""
Tests for Wave 4 habit encoding: GitPatternAnalyzer and PolicyVector.

These are de-risking tests to validate the prototypes before full Wave 4 implementation.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from protocols.prompt.habits.git_analyzer import (
    GitAnalyzerError,
    GitPattern,
    GitPatternAnalyzer,
    analyze_repo,
)
from protocols.prompt.habits.policy import PolicyVector

# =============================================================================
# GitPatternAnalyzer Tests
# =============================================================================


class TestGitPatternAnalyzer:
    """Tests for GitPatternAnalyzer prototype."""

    @pytest.fixture
    def analyzer(self, tmp_path: Path) -> GitPatternAnalyzer:
        """Create analyzer for a temporary path."""
        return GitPatternAnalyzer(repo_path=tmp_path, lookback_commits=50)

    def test_initialization(self, analyzer: GitPatternAnalyzer) -> None:
        """Test analyzer can be initialized."""
        assert analyzer.repo_path is not None
        assert analyzer.lookback_commits == 50

    @patch.object(GitPatternAnalyzer, "_run_git")
    def test_analyze_commit_style_conventional(
        self, mock_git: MagicMock, analyzer: GitPatternAnalyzer
    ) -> None:
        """Test detection of conventional commit style."""
        # Mock git log output with conventional commits
        mock_git.return_value = """abc123 feat: Add new feature
def456 fix: Fix bug in module
ghi789 docs: Update README
jkl012 chore: Update dependencies
mno345 feat(api): Add endpoint
pqr678 fix(cli): Handle edge case
stu901 test: Add unit tests
vwx234 refactor: Simplify logic
yza567 feat: Another feature
bcd890 fix: Another fix"""

        pattern = analyzer._analyze_commit_style()

        assert pattern.pattern_type == "commit_style"
        assert "conventional" in pattern.description.lower()
        assert pattern.confidence >= 0.7
        assert pattern.details["conventional_ratio"] >= 0.7

    @patch.object(GitPatternAnalyzer, "_run_git")
    def test_analyze_commit_style_emoji(
        self, mock_git: MagicMock, analyzer: GitPatternAnalyzer
    ) -> None:
        """Test detection of emoji commit style."""
        mock_git.return_value = """abc123 ✨ Add sparkles
def456 🐛 Fix bug
ghi789 📝 Update docs
jkl012 🔧 Configure stuff
mno345 ✨ More sparkles"""

        pattern = analyzer._analyze_commit_style()

        assert pattern.pattern_type == "commit_style"
        assert pattern.details["emoji_ratio"] >= 0.5

    @patch.object(GitPatternAnalyzer, "_run_git")
    def test_analyze_file_focus_concentrated(
        self, mock_git: MagicMock, analyzer: GitPatternAnalyzer
    ) -> None:
        """Test detection of concentrated file focus."""
        # Many changes in one directory
        mock_git.return_value = """impl/claude/protocols/prompt/compiler.py
impl/claude/protocols/prompt/section_base.py
impl/claude/protocols/prompt/polynomial.py
impl/claude/protocols/prompt/cli.py
impl/claude/protocols/prompt/sections/identity.py
impl/claude/protocols/prompt/sections/skills.py
impl/claude/protocols/agentese/parser.py
docs/README.md"""

        pattern = analyzer._analyze_file_focus()

        assert pattern.pattern_type == "file_focus"
        assert "impl/claude/" in pattern.evidence[0]
        # Should detect concentrated focus
        assert pattern.details["top_dir_ratio"] > 0.5

    @patch.object(GitPatternAnalyzer, "_run_git")
    def test_analyze_file_focus_distributed(
        self, mock_git: MagicMock, analyzer: GitPatternAnalyzer
    ) -> None:
        """Test detection of distributed file changes."""
        mock_git.return_value = """src/module1/file.py
tests/test_module1.py
docs/guide.md
config/settings.yaml
scripts/build.sh
lib/utils.py
api/routes.py
cli/main.py
web/app.tsx
db/migrations.sql"""

        pattern = analyzer._analyze_file_focus()

        assert pattern.pattern_type == "file_focus"
        assert pattern.details["unique_dirs"] >= 5
        # Lower confidence for distributed changes
        assert pattern.confidence <= 0.7

    @patch.object(GitPatternAnalyzer, "_run_git")
    def test_analyze_timing_morning(
        self, mock_git: MagicMock, analyzer: GitPatternAnalyzer
    ) -> None:
        """Test detection of morning commit pattern."""
        # Morning commits (8-11 AM)
        mock_git.return_value = """2025-01-15T08:30:00+00:00
2025-01-15T09:15:00+00:00
2025-01-15T10:00:00+00:00
2025-01-15T08:45:00+00:00
2025-01-15T11:00:00+00:00
2025-01-14T09:30:00+00:00
2025-01-14T10:15:00+00:00"""

        pattern = analyzer._analyze_timing()

        assert pattern.pattern_type == "timing"
        assert "morning" in pattern.description.lower()
        assert pattern.details["morning_ratio"] > 0.5

    @patch.object(GitPatternAnalyzer, "_run_git")
    def test_analyze_timing_weekday(
        self, mock_git: MagicMock, analyzer: GitPatternAnalyzer
    ) -> None:
        """Test detection of weekday commit pattern."""
        # All weekday commits (Mon-Fri)
        mock_git.return_value = """2025-01-13T10:00:00+00:00
2025-01-14T11:00:00+00:00
2025-01-15T09:00:00+00:00
2025-01-16T14:00:00+00:00
2025-01-17T16:00:00+00:00"""

        pattern = analyzer._analyze_timing()

        assert pattern.pattern_type == "timing"
        assert pattern.details["weekday_ratio"] > 0.9
        assert "weekday" in pattern.description.lower()

    def test_analyze_real_repo(self) -> None:
        """Test analysis on the actual kgents repo (integration test)."""
        # Find the repo root
        repo_path = Path(__file__).parent.parent.parent.parent.parent.parent
        if not (repo_path / ".git").exists():
            pytest.skip("Not in a git repository")

        patterns = analyze_repo(repo_path, lookback=50)

        # Should return multiple patterns
        assert len(patterns) >= 1

        # All patterns should have valid structure
        for pattern in patterns:
            assert pattern.pattern_type in {
                "commit_style",
                "file_focus",
                "timing",
                "collaboration",
            }
            assert 0.0 <= pattern.confidence <= 1.0
            assert isinstance(pattern.evidence, tuple)

    def test_validation_rejects_nonexistent_path(self, tmp_path: Path) -> None:
        """Test that validation rejects nonexistent path."""
        analyzer = GitPatternAnalyzer(repo_path=tmp_path / "nonexistent")

        with pytest.raises(GitAnalyzerError) as exc_info:
            analyzer.analyze()

        assert "does not exist" in str(exc_info.value)

    def test_validation_rejects_non_git_directory(self, tmp_path: Path) -> None:
        """Test that validation rejects directory without .git."""
        # Create a directory that's not a git repo
        non_repo = tmp_path / "not_a_repo"
        non_repo.mkdir()

        analyzer = GitPatternAnalyzer(repo_path=non_repo)

        with pytest.raises(GitAnalyzerError) as exc_info:
            analyzer.analyze()

        assert "Not a git repository" in str(exc_info.value)


# =============================================================================
# PolicyVector Tests
# =============================================================================


class TestPolicyVector:
    """Tests for PolicyVector dataclass."""

    def test_default_creation(self) -> None:
        """Test creating a default policy vector."""
        policy = PolicyVector.default()

        assert policy.verbosity == 0.5
        assert policy.formality == 0.6
        assert policy.confidence == 0.5
        assert "default" in policy.learned_from
        assert len(policy.section_weights) > 0

    def test_get_section_weight(self) -> None:
        """Test getting section weights."""
        policy = PolicyVector(
            section_weights=(
                ("identity", 1.0),
                ("skills", 0.7),
            )
        )

        assert policy.get_section_weight("identity") == 1.0
        assert policy.get_section_weight("skills") == 0.7
        assert policy.get_section_weight("unknown") == 0.5  # default

    def test_get_domain_focus(self) -> None:
        """Test getting domain focus."""
        policy = PolicyVector(
            domain_focus=(
                ("agentese", 0.9),
                ("cli", 0.6),
            )
        )

        assert policy.get_domain_focus("agentese") == 0.9
        assert policy.get_domain_focus("cli") == 0.6
        assert policy.get_domain_focus("unknown") == 0.5  # default

    def test_merge_equal_weight(self) -> None:
        """Test merging with equal weight."""
        policy1 = PolicyVector(
            verbosity=0.3,
            formality=0.4,
            section_weights=(("a", 1.0),),
            domain_focus=(("x", 0.8),),
            learned_from=("git",),
        )
        policy2 = PolicyVector(
            verbosity=0.7,
            formality=0.8,
            section_weights=(("b", 1.0),),
            domain_focus=(("y", 0.6),),
            learned_from=("sessions",),
        )

        merged = policy1.merge_with(policy2, weight=0.5)

        # Scalars should be averaged
        assert merged.verbosity == pytest.approx(0.5)
        assert merged.formality == pytest.approx(0.6)

        # Both sources should be present
        assert "git" in merged.learned_from
        assert "sessions" in merged.learned_from

        # Weights should be merged
        assert merged.get_section_weight("a") == pytest.approx(0.5)
        assert merged.get_section_weight("b") == pytest.approx(0.5)

    def test_merge_weighted_toward_other(self) -> None:
        """Test merging with weight toward other."""
        policy1 = PolicyVector(verbosity=0.0)
        policy2 = PolicyVector(verbosity=1.0)

        merged = policy1.merge_with(policy2, weight=0.8)

        # Should be closer to policy2
        assert merged.verbosity == pytest.approx(0.8)

    def test_merge_weighted_toward_self(self) -> None:
        """Test merging with weight toward self."""
        policy1 = PolicyVector(verbosity=0.0)
        policy2 = PolicyVector(verbosity=1.0)

        merged = policy1.merge_with(policy2, weight=0.2)

        # Should be closer to policy1
        assert merged.verbosity == pytest.approx(0.2)

    def test_with_trace(self) -> None:
        """Test adding reasoning trace."""
        policy = PolicyVector(reasoning_trace=("original",))
        updated = policy.with_trace("new trace")

        assert "original" in updated.reasoning_trace
        assert "new trace" in updated.reasoning_trace
        # Original should be unchanged
        assert "new trace" not in policy.reasoning_trace

    def test_immutability(self) -> None:
        """Test that PolicyVector is immutable."""
        policy = PolicyVector()

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            policy.verbosity = 0.9  # type: ignore

    def test_from_git_patterns_commit_style(self) -> None:
        """Test creating policy from git commit style pattern."""
        patterns = [
            GitPattern(
                pattern_type="commit_style",
                description="Uses conventional commits",
                confidence=0.8,
                evidence=(),
                details={
                    "conventional_ratio": 0.85,
                    "avg_length": 90,  # Long messages
                },
            )
        ]

        policy = PolicyVector.from_git_patterns(patterns)

        assert policy.formality == 0.8  # High due to conventional commits
        assert policy.verbosity == 0.7  # High due to long messages
        assert "git" in policy.learned_from
        assert policy.confidence == pytest.approx(0.8)

    def test_from_git_patterns_file_focus(self) -> None:
        """Test creating policy from git file focus pattern."""
        patterns = [
            GitPattern(
                pattern_type="file_focus",
                description="Concentrated focus",
                confidence=0.9,
                evidence=("protocols/: 50", "agents/: 20", "docs/: 10"),
                details={
                    "dir_0_ratio": 0.6,
                    "dir_1_ratio": 0.25,
                    "dir_2_ratio": 0.1,
                },
            )
        ]

        policy = PolicyVector.from_git_patterns(patterns)

        # Should have domain focus entries
        assert len(policy.domain_focus) > 0
        # Top directory should have highest focus
        domain_dict = dict(policy.domain_focus)
        assert "protocols" in domain_dict or any("protocols" in d for d in domain_dict)


# =============================================================================
# Integration Tests
# =============================================================================


class TestHabitEncodingIntegration:
    """Integration tests for habit encoding flow."""

    def test_full_flow_with_mock_git(self) -> None:
        """Test full flow from git analysis to policy vector."""
        with patch.object(GitPatternAnalyzer, "_run_git") as mock_git:
            # Setup mock responses
            def mock_git_responses(*args: str) -> str:
                if "oneline" in args:
                    return "abc123 feat: Add feature\ndef456 fix: Fix bug"
                elif "name-only" in args:
                    return "impl/claude/protocols/test.py\nimpl/claude/agents/agent.py"
                elif "format=%aI" in args:
                    return "2025-01-15T10:00:00+00:00\n2025-01-14T11:00:00+00:00"
                return ""

            mock_git.side_effect = mock_git_responses

            # Analyze
            analyzer = GitPatternAnalyzer(repo_path=Path("."), lookback_commits=10)
            patterns = analyzer.analyze()

            # Should have patterns
            assert len(patterns) >= 1

            # Create policy
            policy = PolicyVector.from_git_patterns(patterns)

            # Policy should be valid
            assert 0.0 <= policy.verbosity <= 1.0
            assert 0.0 <= policy.formality <= 1.0
            assert "git" in policy.learned_from
            assert len(policy.reasoning_trace) > 0
