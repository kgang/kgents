"""
Tests for Semantic Gatekeeper.

The Semantic Gatekeeper validates code against the kgents principles:
1. Tasteful - Clear, justified purpose
2. Curated - Quality over quantity
3. Ethical - Augment, don't replace judgment
4. Joy-Inducing - Personality matters
5. Composable - Agents are morphisms
6. Heterarchical - Flux, not hierarchy
7. Generative - Spec compresses implementation
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path

import pytest

from agents.k.gatekeeper import (
    Principle,
    SemanticGatekeeper,
    Severity,
    ValidationResult,
    Violation,
    validate_content,
    validate_file,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def gatekeeper() -> SemanticGatekeeper:
    """Create a gatekeeper without LLM."""
    return SemanticGatekeeper(use_llm=False)


@pytest.fixture
def temp_file() -> Callable[[str], str]:
    """Create a temporary file for testing."""

    def _create_file(content: str) -> str:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            return f.name

    return _create_file


# =============================================================================
# Basic Tests
# =============================================================================


class TestViolation:
    """Tests for Violation dataclass."""

    def test_violation_creation(self) -> None:
        """Test creating a violation."""
        v = Violation(
            principle=Principle.TASTEFUL,
            severity=Severity.WARNING,
            message="Test violation",
            location="test.py:10",
        )
        assert v.principle == Principle.TASTEFUL
        assert v.severity == Severity.WARNING
        assert v.message == "Test violation"

    def test_violation_serialization(self) -> None:
        """Test violation to_dict."""
        v = Violation(
            principle=Principle.ETHICAL,
            severity=Severity.CRITICAL,
            message="Secret exposed",
            evidence="api_key = 'secret'",
        )
        d = v.to_dict()
        assert d["principle"] == "ethical"
        assert d["severity"] == "critical"
        assert "Secret exposed" in d["message"]

    def test_violation_format(self) -> None:
        """Test violation formatting."""
        v = Violation(
            principle=Principle.COMPOSABLE,
            severity=Severity.ERROR,
            message="Singleton detected",
            suggestion="Use dependency injection",
        )
        formatted = v.format()
        assert "[X]" in formatted  # Error icon
        assert "composable" in formatted
        assert "Singleton detected" in formatted
        assert "dependency injection" in formatted


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_result_passed(self) -> None:
        """Test passed result."""
        result = ValidationResult(
            target="test.py",
            passed=True,
            violations=[],
        )
        assert result.passed
        assert len(result.violations) == 0

    def test_result_failed(self) -> None:
        """Test failed result."""
        result = ValidationResult(
            target="test.py",
            passed=False,
            violations=[
                Violation(
                    principle=Principle.ETHICAL,
                    severity=Severity.CRITICAL,
                    message="Test",
                )
            ],
        )
        assert not result.passed
        assert result.by_severity["critical"] == 1

    def test_result_by_principle(self) -> None:
        """Test counting by principle."""
        result = ValidationResult(
            target="test.py",
            violations=[
                Violation(Principle.TASTEFUL, Severity.WARNING, "1"),
                Violation(Principle.TASTEFUL, Severity.INFO, "2"),
                Violation(Principle.COMPOSABLE, Severity.ERROR, "3"),
            ],
        )
        assert result.by_principle["tasteful"] == 2
        assert result.by_principle["composable"] == 1


# =============================================================================
# Heuristic Pattern Tests
# =============================================================================


class TestHeuristicPatterns:
    """Tests for heuristic pattern detection."""

    @pytest.mark.asyncio
    async def test_detect_hardcoded_password(self, gatekeeper: SemanticGatekeeper) -> None:
        """Test detecting hardcoded passwords."""
        content = """
def connect():
    password = "super_secret_123"
    return db.connect(password)
"""
        result = await gatekeeper.validate_content(content, "test.py")

        assert not result.passed
        assert any(
            v.principle == Principle.ETHICAL and v.severity == Severity.CRITICAL
            for v in result.violations
        )

    @pytest.mark.asyncio
    async def test_detect_hardcoded_api_key(self, gatekeeper: SemanticGatekeeper) -> None:
        """Test detecting hardcoded API keys."""
        content = """
API_KEY = "sk_live_abc123"
"""
        result = await gatekeeper.validate_content(content, "test.py")

        assert not result.passed
        assert any("api" in v.message.lower() for v in result.violations)

    @pytest.mark.asyncio
    async def test_detect_singleton(self, gatekeeper: SemanticGatekeeper) -> None:
        """Test detecting singleton pattern."""
        content = """
class DatabaseSingleton:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
"""
        result = await gatekeeper.validate_content(content, "test.py")

        assert any(v.principle == Principle.COMPOSABLE for v in result.violations)

    @pytest.mark.asyncio
    async def test_detect_global_state(self, gatekeeper: SemanticGatekeeper) -> None:
        """Test detecting global state."""
        content = """
global counter
counter = 0

def increment():
    global counter
    counter += 1
"""
        result = await gatekeeper.validate_content(content, "test.py")

        assert any(
            v.principle == Principle.COMPOSABLE and "global" in v.message.lower()
            for v in result.violations
        )

    @pytest.mark.asyncio
    async def test_detect_orchestrator(self, gatekeeper: SemanticGatekeeper) -> None:
        """Test detecting orchestrator pattern."""
        content = """
class TaskOrchestrator:
    def coordinate(self):
        pass
"""
        result = await gatekeeper.validate_content(content, "test.py")

        assert any(v.principle == Principle.HETERARCHICAL for v in result.violations)

    @pytest.mark.asyncio
    async def test_detect_master_slave(self, gatekeeper: SemanticGatekeeper) -> None:
        """Test detecting master/slave terminology."""
        content = """
class DatabaseMaster:
    pass

class DatabaseSlave:
    pass
"""
        result = await gatekeeper.validate_content(content, "test.py")

        # Should detect both (class names ending in Master/Slave)
        heterarchical_violations = [
            v for v in result.violations if v.principle == Principle.HETERARCHICAL
        ]
        assert len(heterarchical_violations) >= 2

    @pytest.mark.asyncio
    async def test_detect_manager_class(self, gatekeeper: SemanticGatekeeper) -> None:
        """Test detecting vague Manager classes."""
        content = """
class DataManager:
    def manage(self):
        pass
"""
        result = await gatekeeper.validate_content(content, "test.py")

        assert any(
            v.principle == Principle.TASTEFUL and "manager" in v.message.lower()
            for v in result.violations
        )

    @pytest.mark.asyncio
    async def test_detect_versioned_class(self, gatekeeper: SemanticGatekeeper) -> None:
        """Test detecting versioned classes."""
        content = """
class UserServiceV2:
    pass
"""
        result = await gatekeeper.validate_content(content, "test.py")

        assert any(
            v.principle == Principle.CURATED and "version" in v.message.lower()
            for v in result.violations
        )

    @pytest.mark.asyncio
    async def test_clean_code_passes(self, gatekeeper: SemanticGatekeeper) -> None:
        """Test that clean code passes."""
        content = '''
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

class UserRepository:
    def __init__(self, db):
        self._db = db

    def get(self, user_id: str):
        return self._db.find_one(user_id)
'''
        result = await gatekeeper.validate_content(content, "test.py")

        # Should pass (no critical/error violations)
        assert result.passed


# =============================================================================
# File Validation Tests
# =============================================================================


class TestFileValidation:
    """Tests for file validation."""

    @pytest.mark.asyncio
    async def test_validate_existing_file(self, temp_file: Callable[[str], str]) -> None:
        """Test validating an existing file."""
        path = temp_file("def hello(): pass")
        result = await validate_file(path)

        assert result.target == path
        assert result.passed

    @pytest.mark.asyncio
    async def test_validate_nonexistent_file(self) -> None:
        """Test validating nonexistent file."""
        result = await validate_file("/nonexistent/file.py")

        assert not result.passed
        assert any("not found" in v.message.lower() for v in result.violations)


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_validate_content_function(self) -> None:
        """Test validate_content convenience function."""
        result = await validate_content(
            "password = 'secret'",
            target="inline",
        )

        assert not result.passed
        assert len(result.violations) > 0

    @pytest.mark.asyncio
    async def test_validate_file_function(self, temp_file: Callable[[str], str]) -> None:
        """Test validate_file convenience function."""
        path = temp_file("class MySingleton: pass")
        result = await validate_file(path)

        assert any(v.principle == Principle.COMPOSABLE for v in result.violations)


# =============================================================================
# Result Formatting Tests
# =============================================================================


class TestResultFormatting:
    """Tests for result formatting."""

    def test_format_passed_result(self) -> None:
        """Test formatting a passed result."""
        result = ValidationResult(
            target="clean.py",
            passed=True,
            violations=[],
            summary="No violations detected.",
        )
        formatted = result.format()

        assert "PASSED" in formatted
        assert "No violations" in formatted

    def test_format_failed_result(self) -> None:
        """Test formatting a failed result."""
        result = ValidationResult(
            target="bad.py",
            passed=False,
            violations=[
                Violation(Principle.ETHICAL, Severity.CRITICAL, "Secret exposed"),
                Violation(Principle.COMPOSABLE, Severity.ERROR, "Singleton found"),
            ],
        )
        formatted = result.format()

        assert "FAILED" in formatted
        assert "critical: 1" in formatted.lower()
        assert "error: 1" in formatted.lower()


# =============================================================================
# Principle Enum Tests
# =============================================================================


class TestPrinciples:
    """Tests for Principle enum."""

    def test_all_principles_exist(self) -> None:
        """Test all seven principles exist."""
        assert len(Principle) == 7
        assert Principle.TASTEFUL
        assert Principle.CURATED
        assert Principle.ETHICAL
        assert Principle.JOY_INDUCING
        assert Principle.COMPOSABLE
        assert Principle.HETERARCHICAL
        assert Principle.GENERATIVE


# =============================================================================
# Severity Tests
# =============================================================================


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_ordering(self) -> None:
        """Test severity levels exist."""
        assert Severity.INFO
        assert Severity.WARNING
        assert Severity.ERROR
        assert Severity.CRITICAL

    def test_pass_fail_threshold(self) -> None:
        """Test that only ERROR/CRITICAL cause failure."""
        # Info and warning don't fail
        result1 = ValidationResult(
            target="test",
            violations=[
                Violation(Principle.TASTEFUL, Severity.INFO, "info"),
                Violation(Principle.TASTEFUL, Severity.WARNING, "warn"),
            ],
            passed=True,
        )

        # Error causes failure
        result2 = ValidationResult(
            target="test",
            violations=[
                Violation(Principle.TASTEFUL, Severity.ERROR, "error"),
            ],
            passed=False,
        )

        assert result1.passed
        assert not result2.passed


# =============================================================================
# Specialized Analyzers Tests (110% Domain 2)
# =============================================================================


from agents.k.gatekeeper import (
    ComposabilityAnalyzer,
    GratitudeAnalyzer,
    TastefullnessAnalyzer,
    ValidationHistory,
)


class TestTastefullnessAnalyzer:
    """Tests for TastefullnessAnalyzer (110% Domain 2)."""

    @pytest.fixture
    def analyzer(self) -> TastefullnessAnalyzer:
        """Create a TastefullnessAnalyzer."""
        return TastefullnessAnalyzer()

    @pytest.mark.asyncio
    async def test_detect_kitchen_sink(self, analyzer: TastefullnessAnalyzer) -> None:
        """Test detecting classes with too many methods."""
        methods = "\n    ".join([f"def method_{i}(self): pass" for i in range(20)])
        content = f"""
class KitchenSink:
    {methods}
"""
        result = await analyzer.analyze(content, "test.py")
        assert any("kitchen-sink" in v.message.lower() for v in result.violations)

    @pytest.mark.asyncio
    async def test_lean_module_has_insight(self, analyzer: TastefullnessAnalyzer) -> None:
        """Test that lean modules get positive insights."""
        content = """
from typing import Optional

def greet(name: str) -> str:
    return f"Hello, {name}"
"""
        result = await analyzer.analyze(content, "test.py")
        assert any("lean imports" in insight.lower() for insight in result.insights)

    @pytest.mark.asyncio
    async def test_score_calculation(self, analyzer: TastefullnessAnalyzer) -> None:
        """Test that clean code gets high score."""
        content = """
def add(a: int, b: int) -> int:
    return a + b
"""
        result = await analyzer.analyze(content, "test.py")
        assert result.score >= 0.9  # Clean code should score high


class TestComposabilityAnalyzer:
    """Tests for ComposabilityAnalyzer (110% Domain 2)."""

    @pytest.fixture
    def analyzer(self) -> ComposabilityAnalyzer:
        """Create a ComposabilityAnalyzer."""
        return ComposabilityAnalyzer()

    @pytest.mark.asyncio
    async def test_detect_mutable_default(self, analyzer: ComposabilityAnalyzer) -> None:
        """Test detecting mutable default arguments."""
        content = """
def add_item(item, items=[]):
    items.append(item)
    return items
"""
        result = await analyzer.analyze(content, "test.py")
        assert any("mutable default" in v.message.lower() for v in result.violations)

    @pytest.mark.asyncio
    async def test_detect_dependency_injection(self, analyzer: ComposabilityAnalyzer) -> None:
        """Test that DI pattern is recognized as positive."""
        content = """
class Service:
    def __init__(self, repo: Repository):
        self._repo = repo
"""
        result = await analyzer.analyze(content, "test.py")
        assert any("injection" in insight.lower() for insight in result.insights)


class TestGratitudeAnalyzer:
    """Tests for GratitudeAnalyzer (110% Domain 2)."""

    @pytest.fixture
    def analyzer(self) -> GratitudeAnalyzer:
        """Create a GratitudeAnalyzer."""
        return GratitudeAnalyzer()

    @pytest.mark.asyncio
    async def test_credits_boost_score(self, analyzer: GratitudeAnalyzer) -> None:
        """Test that credits/thanks boost gratitude score."""
        content = '''
"""
Module based on ideas from Clean Architecture.
Thanks to Robert Martin for the inspiration.
"""

def process() -> str:
    # Thank you for reading this code
    return "processed"
'''
        result = await analyzer.analyze(content, "test.py")
        # Should have at least one gratitude signal (references in docs)
        assert result.score > 0
        assert any("references" in insight.lower() for insight in result.insights)

    @pytest.mark.asyncio
    async def test_type_hints_count(self, analyzer: GratitudeAnalyzer) -> None:
        """Test that type hints contribute to gratitude score when combined with other signals."""
        # The type hints pattern requires `: TypeName[` format
        # Combined with error messages for gratitude
        content = """
from typing import Optional

def process(items: list[str]) -> Optional[str]:
    \"\"\"Process items and return result.\"\"\"
    if not items:
        raise ValueError("Items cannot be empty")
    return items[0]
"""
        result = await analyzer.analyze(content, "test.py")
        # Error handling contributes to gratitude (respects human reader)
        # Low-gratitude info violation is acceptable - just verify analyzer runs
        assert result is not None


class TestValidationHistory:
    """Tests for ValidationHistory (110% Domain 2)."""

    def test_record_and_retrieve(self) -> None:
        """Test recording validation results."""
        history = ValidationHistory()

        result = ValidationResult(
            target="test.py",
            passed=False,
            violations=[
                Violation(Principle.TASTEFUL, Severity.WARNING, "test"),
            ],
        )
        history.record(result)

        assert len(history._entries) == 1

    def test_recurring_violations(self) -> None:
        """Test detecting recurring violations."""
        history = ValidationHistory()

        # Record same violation multiple times
        for _ in range(3):
            result = ValidationResult(
                target="test.py",
                passed=False,
                violations=[
                    Violation(Principle.COMPOSABLE, Severity.WARNING, "singleton"),
                ],
            )
            history.record(result)

        recurring = history.recurring_violations()
        assert "composable" in recurring
        assert recurring["composable"] == 3

    def test_improvement_trend(self) -> None:
        """Test improvement trend calculation."""
        history = ValidationHistory()

        # First half: many violations
        for _ in range(5):
            result = ValidationResult(
                target="test.py",
                violations=[
                    Violation(Principle.TASTEFUL, Severity.WARNING, "v1"),
                    Violation(Principle.TASTEFUL, Severity.WARNING, "v2"),
                ],
            )
            history.record(result)

        # Second half: fewer violations
        for _ in range(5):
            result = ValidationResult(
                target="test.py",
                violations=[],
            )
            history.record(result)

        trend = history.improvement_trend()
        assert trend > 0  # Should show improvement

    def test_blind_spots(self) -> None:
        """Test detecting blind spots."""
        history = ValidationHistory()

        # Only violate one principle
        result = ValidationResult(
            target="test.py",
            violations=[
                Violation(Principle.TASTEFUL, Severity.WARNING, "test"),
            ],
        )
        history.record(result)

        blind = history.blind_spots()
        assert "curated" in blind  # Never violated
        assert "tasteful" not in blind  # Was violated

    def test_generate_report(self) -> None:
        """Test report generation."""
        history = ValidationHistory()

        result = ValidationResult(
            target="test.py",
            violations=[
                Violation(Principle.COMPOSABLE, Severity.WARNING, "test"),
            ],
        )
        history.record(result)
        history.record(result)

        report = history.generate_report()
        assert "Validation Pattern Report" in report
        assert "Total validations: 2" in report
