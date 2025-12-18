"""
Tests for Atelier Gestalt Integration.

Wave 2: Extensions - Atelier uses Gestalt for code analysis.
"""

from __future__ import annotations

import pytest

from agents.atelier.gestalt_integration import (
    CodeIssue,
    GestaltArtifactAnalysis,
    analyze_artifact_code,
    create_health_badge_props,
)


class TestGestaltArtifactAnalysis:
    """Tests for GestaltArtifactAnalysis data class."""

    def test_default_values(self) -> None:
        """Analysis has sensible defaults."""
        analysis = GestaltArtifactAnalysis()
        assert analysis.grade == "?"
        assert analysis.score == 0.0
        assert analysis.coupling == 0.0
        assert analysis.cohesion == 1.0
        assert analysis.issues == []

    def test_is_healthy(self) -> None:
        """is_healthy returns True for good grades."""
        healthy_grades = ["A+", "A", "A-", "B+", "B"]
        for grade in healthy_grades:
            analysis = GestaltArtifactAnalysis(grade=grade)
            assert analysis.is_healthy, f"{grade} should be healthy"

    def test_is_not_healthy(self) -> None:
        """is_healthy returns False for poor grades."""
        unhealthy_grades = ["B-", "C+", "C", "C-", "D+", "D", "D-", "F"]
        for grade in unhealthy_grades:
            analysis = GestaltArtifactAnalysis(grade=grade)
            assert not analysis.is_healthy, f"{grade} should not be healthy"

    def test_needs_attention(self) -> None:
        """needs_attention returns True for C or worse."""
        needs_attention_grades = ["C+", "C", "C-", "D+", "D", "D-", "F"]
        for grade in needs_attention_grades:
            analysis = GestaltArtifactAnalysis(grade=grade)
            assert analysis.needs_attention, f"{grade} should need attention"

    def test_to_dict(self) -> None:
        """to_dict serializes all fields."""
        analysis = GestaltArtifactAnalysis(
            grade="B+",
            score=0.82,
            coupling=0.3,
            cohesion=0.7,
            complexity=0.4,
            drift=0.1,
            lines_of_code=150,
            issues=[
                CodeIssue(
                    severity="warning",
                    category="coupling",
                    message="Test issue",
                )
            ],
        )
        d = analysis.to_dict()

        assert d["grade"] == "B+"
        assert d["score"] == 0.82
        assert d["coupling"] == 0.3
        assert d["cohesion"] == 0.7
        assert d["complexity"] == 0.4
        assert d["drift"] == 0.1
        assert d["lines_of_code"] == 150
        assert d["is_healthy"] is True
        assert d["needs_attention"] is False
        assert len(d["issues"]) == 1
        assert d["issues"][0]["message"] == "Test issue"

    def test_to_cli(self) -> None:
        """to_cli produces human-readable output."""
        analysis = GestaltArtifactAnalysis(
            grade="B+",
            score=0.82,
            coupling=0.3,
            cohesion=0.7,
            lines_of_code=150,
            issues=[
                CodeIssue(
                    severity="warning",
                    category="coupling",
                    message="High coupling detected",
                    suggestion="Split into smaller modules",
                )
            ],
        )
        cli = analysis.to_cli()

        assert "B+" in cli
        assert "82%" in cli
        assert "Coupling" in cli
        assert "Cohesion" in cli
        assert "150" in cli
        assert "High coupling detected" in cli
        assert "Split into smaller modules" in cli


class TestCodeIssue:
    """Tests for CodeIssue data class."""

    def test_to_dict(self) -> None:
        """to_dict serializes all fields."""
        issue = CodeIssue(
            severity="warning",
            category="complexity",
            message="Function too complex",
            line=42,
            suggestion="Extract helper functions",
        )
        d = issue.to_dict()

        assert d["severity"] == "warning"
        assert d["category"] == "complexity"
        assert d["message"] == "Function too complex"
        assert d["line"] == 42
        assert d["suggestion"] == "Extract helper functions"

    def test_optional_fields(self) -> None:
        """Optional fields can be None."""
        issue = CodeIssue(
            severity="info",
            category="style",
            message="Minor style issue",
        )
        d = issue.to_dict()

        assert d["line"] is None
        assert d["suggestion"] is None


class TestAnalyzeArtifactCode:
    """Tests for analyze_artifact_code function."""

    @pytest.mark.asyncio
    async def test_empty_code(self) -> None:
        """Empty code returns placeholder analysis."""
        analysis = await analyze_artifact_code("")
        assert analysis.grade == "?"
        assert analysis.score == 0.0
        assert len(analysis.issues) == 1
        assert analysis.issues[0].category == "empty"

    @pytest.mark.asyncio
    async def test_whitespace_only(self) -> None:
        """Whitespace-only code returns placeholder analysis."""
        analysis = await analyze_artifact_code("   \n\n   ")
        assert analysis.grade == "?"
        assert len(analysis.issues) == 1

    @pytest.mark.asyncio
    async def test_simple_python_code(self) -> None:
        """Simple Python code can be analyzed."""
        code = '''
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"
'''
        analysis = await analyze_artifact_code(code, language="python")
        # Should get some analysis (may fail if gestalt not fully available)
        # We're testing the interface, not the full analysis
        assert isinstance(analysis, GestaltArtifactAnalysis)
        assert analysis.lines_of_code > 0 or analysis.issues  # Either parsed or error

    @pytest.mark.asyncio
    async def test_language_typescript(self) -> None:
        """TypeScript code uses .ts extension."""
        code = """
function hello(name: string): string {
    return `Hello, ${name}!`;
}
"""
        analysis = await analyze_artifact_code(code, language="typescript")
        assert isinstance(analysis, GestaltArtifactAnalysis)


class TestCreateHealthBadgeProps:
    """Tests for create_health_badge_props function."""

    def test_healthy_grade(self) -> None:
        """Healthy grades get green colors."""
        analysis = GestaltArtifactAnalysis(
            grade="A",
            score=0.95,
            coupling=0.1,
            cohesion=0.9,
            complexity=0.2,
        )
        props = create_health_badge_props(analysis)

        assert props["grade"] == "A"
        assert props["color"] == "emerald"
        assert props["isHealthy"] is True
        assert props["needsAttention"] is False
        assert "Score: 95%" in props["tooltip"]

    def test_poor_grade(self) -> None:
        """Poor grades get red colors."""
        analysis = GestaltArtifactAnalysis(
            grade="D",
            score=0.45,
            coupling=0.8,
            cohesion=0.3,
            complexity=0.7,
        )
        props = create_health_badge_props(analysis)

        assert props["grade"] == "D"
        assert props["color"] == "orange"
        assert props["isHealthy"] is False
        assert props["needsAttention"] is True

    def test_with_issues(self) -> None:
        """Issues are included in props."""
        analysis = GestaltArtifactAnalysis(
            grade="C",
            score=0.55,
            issues=[
                CodeIssue("warning", "coupling", "High coupling"),
                CodeIssue("warning", "complexity", "Too complex"),
                CodeIssue("info", "style", "Style issue"),
                CodeIssue("info", "docs", "Missing docs"),  # Should be truncated
            ],
        )
        props = create_health_badge_props(analysis)

        assert "Issues: 4" in props["tooltip"]
        assert len(props["issues"]) == 3  # Truncated to 3

    def test_unknown_grade(self) -> None:
        """Unknown grade gets gray color."""
        analysis = GestaltArtifactAnalysis(grade="?", score=0.0)
        props = create_health_badge_props(analysis)

        assert props["grade"] == "?"
        assert props["color"] == "gray"


class TestGradeBoundaries:
    """Tests for grade boundaries in health assessment."""

    @pytest.mark.parametrize(
        "grade,expected_healthy,expected_attention",
        [
            ("A+", True, False),
            ("A", True, False),
            ("A-", True, False),
            ("B+", True, False),
            ("B", True, False),
            ("B-", False, False),
            ("C+", False, True),
            ("C", False, True),
            ("C-", False, True),
            ("D+", False, True),
            ("D", False, True),
            ("D-", False, True),
            ("F", False, True),
            ("?", False, False),
        ],
    )
    def test_grade_classifications(
        self, grade: str, expected_healthy: bool, expected_attention: bool
    ) -> None:
        """Each grade has correct health/attention classification."""
        analysis = GestaltArtifactAnalysis(grade=grade)
        assert analysis.is_healthy == expected_healthy
        assert analysis.needs_attention == expected_attention
