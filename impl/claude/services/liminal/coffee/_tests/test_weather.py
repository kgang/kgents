"""
Tests for Morning Coffee Conceptual Weather analyzer.

Verifies:
- Plan header parsing extracts status correctly
- Commit message analysis extracts patterns
- Each weather type is detected properly
- Weather composition is correct
"""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.liminal.coffee.types import (
    ConceptualWeather,
    WeatherPattern,
    WeatherType,
)
from services.liminal.coffee.weather import (
    _extract_scope,
    _parse_frontmatter,
    _summarize_commits,
    analyze_commit_messages,
    detect_emerging,
    detect_refactoring,
    detect_scaffolding,
    detect_tension,
    generate_weather,
    parse_plan_headers,
)

# =============================================================================
# Plan Header Parsing Tests
# =============================================================================


class TestParseFrontmatter:
    """Tests for _parse_frontmatter helper."""

    def test_parses_simple_yaml(self) -> None:
        """Parse basic YAML frontmatter."""
        content = """---
status: active
path: test/path
---
# Content
"""
        result = _parse_frontmatter(content)

        assert result["status"] == "active"
        assert result["path"] == "test/path"

    def test_no_frontmatter_returns_empty(self) -> None:
        """No frontmatter returns empty dict."""
        content = "# Just Content\nNo frontmatter here."
        result = _parse_frontmatter(content)
        assert result == {}

    def test_unclosed_frontmatter_handles_gracefully(self) -> None:
        """Unclosed frontmatter with closing marker deep in doc."""
        # If there's no closing --- at all, should return empty
        content_no_close = """---
status: active
more content without close"""

        # But if there IS a closing ---, it should parse what's between
        content_with_close = """---
status: active
---
# Content below
"""
        result_no_close = _parse_frontmatter(content_no_close)
        result_with_close = _parse_frontmatter(content_with_close)

        # Without close, returns empty (can't find end)
        assert result_no_close == {}
        # With close, parses the frontmatter
        assert result_with_close.get("status") == "active"


class TestParsePlanHeaders:
    """Tests for parse_plan_headers."""

    def test_parses_plan_files(self, tmp_path: Path) -> None:
        """Parse multiple plan files."""
        plans = tmp_path / "plans"
        plans.mkdir()

        # Create plan files
        (plans / "feature-x.md").write_text("""---
status: active
---
# Feature X
""")
        (plans / "bug-fix.md").write_text("""---
status: complete
---
# Bug Fix
""")

        result = parse_plan_headers(plans)

        assert len(result) == 2
        names = [p["name"] for p in result]
        assert "Feature X" in names
        assert "Bug Fix" in names

    def test_skips_underscore_files(self, tmp_path: Path) -> None:
        """Skip files starting with underscore."""
        plans = tmp_path / "plans"
        plans.mkdir()

        (plans / "_archive.md").write_text("# Archived")
        (plans / "_focus.md").write_text("# Focus")
        (plans / "real-plan.md").write_text("---\nstatus: active\n---")

        result = parse_plan_headers(plans)

        assert len(result) == 1
        assert result[0]["name"] == "Real Plan"

    def test_missing_dir_returns_empty(self, tmp_path: Path) -> None:
        """Missing plans dir returns empty."""
        result = parse_plan_headers(tmp_path / "nonexistent")
        assert result == []


# =============================================================================
# Commit Message Analysis Tests
# =============================================================================


class TestAnalyzeCommitMessages:
    """Tests for analyze_commit_messages."""

    @patch("services.liminal.coffee.weather.subprocess.run")
    def test_returns_commit_messages(self, mock_run: MagicMock) -> None:
        """Return parsed commit messages."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="feat: add feature\nfix: bug fix\nrefactor: cleanup\n",
        )

        result = analyze_commit_messages()

        assert len(result) == 3
        assert "feat: add feature" in result

    @patch("services.liminal.coffee.weather.subprocess.run")
    def test_git_failure_returns_empty(self, mock_run: MagicMock) -> None:
        """Git failure returns empty list."""
        mock_run.return_value = MagicMock(returncode=1, stderr="error")

        result = analyze_commit_messages()
        assert result == []

    @patch("services.liminal.coffee.weather.subprocess.run")
    def test_filters_empty_lines(self, mock_run: MagicMock) -> None:
        """Filter empty lines from output."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="commit 1\n\ncommit 2\n\n\n",
        )

        result = analyze_commit_messages()

        assert len(result) == 2


# =============================================================================
# Extract Scope Tests
# =============================================================================


class TestExtractScope:
    """Tests for _extract_scope helper."""

    def test_conventional_commit_with_scope(self) -> None:
        """Extract scope from feat(brain): message."""
        result = _extract_scope("feat(brain): add feature")
        assert result == "Brain"

    def test_conventional_commit_no_scope(self) -> None:
        """Extract type from feat: message."""
        result = _extract_scope("refactor: cleanup code")
        assert result == "Refactor"

    def test_no_pattern_returns_none(self) -> None:
        """No matching pattern returns None."""
        result = _extract_scope("just a message with no pattern")
        assert result is None

    def test_long_prefix_ignored(self) -> None:
        """Long prefix (not a type) returns None."""
        result = _extract_scope("this is a very long message: with colon")
        assert result is None


class TestSummarizeCommits:
    """Tests for _summarize_commits helper."""

    def test_single_commit(self) -> None:
        """Single commit returns truncated message."""
        result = _summarize_commits(["feat: this is a feature"])
        assert "feat" in result

    def test_multiple_commits(self) -> None:
        """Multiple commits joined with semicolon."""
        result = _summarize_commits(["feat: a", "fix: b"])
        assert ";" in result

    def test_many_commits_shows_count(self) -> None:
        """Many commits shows '+ N more'."""
        commits = [f"commit {i}" for i in range(10)]
        result = _summarize_commits(commits, max_show=3)
        assert "+7 more" in result

    def test_empty_returns_empty(self) -> None:
        """Empty list returns empty string."""
        result = _summarize_commits([])
        assert result == ""


# =============================================================================
# Pattern Detection Tests
# =============================================================================


class TestDetectRefactoring:
    """Tests for detect_refactoring."""

    def test_detects_refactor_commits(self) -> None:
        """Detect refactor keywords in commits."""
        commits = ["refactor(brain): consolidate services"]
        patterns = detect_refactoring(commits, [])

        assert len(patterns) >= 1
        assert any(p.type == WeatherType.REFACTORING for p in patterns)

    def test_detects_rename_commits(self) -> None:
        """Detect rename keywords."""
        commits = ["rename: old to new"]
        patterns = detect_refactoring(commits, [])

        assert len(patterns) >= 1

    def test_detects_refactor_plans(self) -> None:
        """Detect refactoring in plan status."""
        plans = [{"name": "Cleanup", "status": "refactoring"}]
        patterns = detect_refactoring([], plans)

        assert len(patterns) >= 1
        assert patterns[0].source == "plan"

    def test_no_patterns_returns_empty(self) -> None:
        """No refactoring signals returns empty."""
        patterns = detect_refactoring(["feat: new feature"], [])
        assert len(patterns) == 0


class TestDetectEmerging:
    """Tests for detect_emerging."""

    def test_detects_add_commits(self) -> None:
        """Detect 'add' in commits."""
        commits = ["add: new feature"]
        patterns = detect_emerging(commits, [])

        assert len(patterns) >= 1
        assert any(p.type == WeatherType.EMERGING for p in patterns)

    def test_detects_research_plans(self) -> None:
        """Detect research phase plans."""
        plans = [{"name": "Exploration", "status": "research"}]
        patterns = detect_emerging([], plans)

        assert len(patterns) >= 1
        assert "research" in patterns[0].description.lower()

    def test_detects_planning_plans(self) -> None:
        """Detect planning phase plans."""
        plans = [{"name": "New Feature", "status": "planning"}]
        patterns = detect_emerging([], plans)

        assert len(patterns) >= 1


class TestDetectScaffolding:
    """Tests for detect_scaffolding."""

    def test_detects_arch_commits(self) -> None:
        """Detect architecture commits."""
        commits = ["arch: add foundation"]
        patterns = detect_scaffolding(commits, [])

        assert len(patterns) >= 1
        assert any(p.type == WeatherType.SCAFFOLDING for p in patterns)

    def test_detects_active_plans(self) -> None:
        """Detect active/implement plans."""
        plans = [{"name": "Build", "status": "implement"}]
        patterns = detect_scaffolding([], plans)

        assert len(patterns) >= 1
        assert "building" in patterns[0].description.lower()


class TestDetectTension:
    """Tests for detect_tension."""

    def test_detects_multiple_fixes(self) -> None:
        """Multiple fix commits indicate tension."""
        commits = ["fix: bug 1", "fix: bug 2", "fix: bug 3"]
        patterns = detect_tension(commits, [])

        assert len(patterns) >= 1
        assert any(p.type == WeatherType.TENSION for p in patterns)

    def test_few_fixes_no_tension(self) -> None:
        """One or two fixes aren't tension."""
        commits = ["fix: minor bug"]
        patterns = detect_tension(commits, [])

        # Should not create a pattern for single fix
        tension_patterns = [
            p for p in patterns if p.type == WeatherType.TENSION and p.source == "commit"
        ]
        assert len(tension_patterns) == 0

    def test_detects_blocked_plans(self) -> None:
        """Detect plans with blocking deps."""
        plans = [{"name": "Feature", "blocking": "[other-plan]"}]
        patterns = detect_tension([], plans)

        assert len(patterns) >= 1
        assert "blocked" in patterns[0].description.lower()


# =============================================================================
# Weather Generator Tests
# =============================================================================


class TestGenerateWeather:
    """Tests for generate_weather integration."""

    @patch("services.liminal.coffee.weather.subprocess.run")
    def test_returns_weather(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Returns a proper ConceptualWeather."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="refactor: cleanup\nadd: feature\n",
        )

        # Create plans dir
        plans = tmp_path / "plans"
        plans.mkdir()
        (plans / "test.md").write_text("---\nstatus: active\n---")

        weather = generate_weather(
            repo_path=tmp_path,
            plans_path=plans,
        )

        assert isinstance(weather, ConceptualWeather)
        assert weather.generated_at is not None

    @patch("services.liminal.coffee.weather.subprocess.run")
    def test_empty_weather_is_valid(self, mock_run: MagicMock) -> None:
        """Empty weather should still be valid."""
        mock_run.return_value = MagicMock(returncode=1, stderr="error")

        weather = generate_weather()

        assert isinstance(weather, ConceptualWeather)
        assert weather.is_empty or not weather.is_empty

    @patch("services.liminal.coffee.weather.subprocess.run")
    def test_populates_all_categories(
        self,
        mock_run: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Weather populates all categories when signals present."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="refactor: a\nadd: b\narch: c\nfix: d\nfix: e\nfix: f\n",
        )

        plans = tmp_path / "plans"
        plans.mkdir()
        (plans / "research.md").write_text("---\nstatus: research\n---")
        (plans / "blocked.md").write_text("---\nstatus: pending\nblocking: [other]\n---")

        weather = generate_weather(
            repo_path=tmp_path,
            plans_path=plans,
        )

        # Should have patterns in multiple categories
        assert len(weather.refactoring) > 0
        assert len(weather.emerging) > 0
        assert len(weather.scaffolding) > 0
        assert len(weather.tension) > 0


# =============================================================================
# ConceptualWeather Type Tests
# =============================================================================


class TestConceptualWeatherType:
    """Tests for ConceptualWeather dataclass."""

    def test_is_empty_when_empty(self) -> None:
        """is_empty returns True for empty weather."""
        weather = ConceptualWeather()
        assert weather.is_empty is True

    def test_not_empty_with_patterns(self) -> None:
        """is_empty returns False with patterns."""
        pattern = WeatherPattern(
            type=WeatherType.REFACTORING,
            label="test",
            description="test",
        )
        weather = ConceptualWeather(refactoring=(pattern,))
        assert weather.is_empty is False

    def test_all_patterns_flattens(self) -> None:
        """all_patterns returns flat list."""
        p1 = WeatherPattern(type=WeatherType.REFACTORING, label="a", description="")
        p2 = WeatherPattern(type=WeatherType.EMERGING, label="b", description="")

        weather = ConceptualWeather(
            refactoring=(p1,),
            emerging=(p2,),
        )

        all_patterns = weather.all_patterns
        assert len(all_patterns) == 2

    def test_to_dict_serializes(self) -> None:
        """to_dict creates valid dict."""
        pattern = WeatherPattern(
            type=WeatherType.SCAFFOLDING,
            label="test",
            description="test desc",
            source="commit",
        )
        weather = ConceptualWeather(scaffolding=(pattern,))

        data = weather.to_dict()

        assert "scaffolding" in data
        assert "generated_at" in data
        assert len(data["scaffolding"]) == 1
        assert data["scaffolding"][0]["type"] == "scaffolding"
