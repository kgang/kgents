"""
Tests for Phase 2.5c - Recovery & Learning Layer

Tests the retry, fallback, and error memory components that provide
intelligent recovery from failed experiments.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from agents.e.ast_analyzer import CodeStructure
from agents.e.error_memory import ErrorMemory, ErrorPattern, ErrorWarning
from agents.e.experiment import (
    CodeImprovement,
    CodeModule,
    Experiment,
    ExperimentStatus,
)
from agents.e.fallback import FallbackStrategy, FallbackConfig
from agents.e.prompts import PromptContext
from agents.e.retry import RetryStrategy, RetryConfig
from agents.e.validator import (
    Issue,
    IssueCategory,
    IssueSeverity,
    ValidationReport,
)


# --- Fixtures ---


@pytest.fixture
def mock_module() -> CodeModule:
    """Create a mock code module for testing."""
    # Create a temporary file
    temp_file = Path(tempfile.mktemp(suffix=".py"))
    temp_file.write_text("""
def example_function(x):
    return x * 2

class ExampleClass:
    def method(self):
        pass
""")

    module = CodeModule(
        name="test_module",
        category="agents",
        path=temp_file
    )

    yield module

    # Cleanup
    temp_file.unlink()


@pytest.fixture
def mock_prompt_context(mock_module: CodeModule) -> PromptContext:
    """Create a mock prompt context."""
    ast_structure = CodeStructure.from_lists(
        module_name="test_module",
        classes=[{"name": "ExampleClass", "line": 5, "methods": ["method"]}],
        functions=[{"name": "example_function", "line": 2, "params": ["x"]}],
        imports=["typing"],
        docstring="Test module",
        line_count=10,
        complexity_hints=["simple module"],
    )

    return PromptContext(
        module_path=mock_module.path,
        current_code=mock_module.path.read_text(),
        ast_structure=ast_structure,
        type_annotations={"example_function": "(x: int) -> int"},
        imports=["from typing import Optional"],
        pre_existing_errors=[],
        similar_patterns=[],
        principles=["Test principle 1", "Test principle 2"],
    )


@pytest.fixture
def failed_experiment(mock_module: CodeModule) -> Experiment:
    """Create a failed experiment for testing."""
    improvement = CodeImprovement(
        description="Test improvement",
        rationale="Test rationale",
        improvement_type="refactor",
        code="def broken():\n    return [",  # Syntax error
        confidence=0.8,
    )

    return Experiment(
        id="test_001",
        module=mock_module,
        improvement=improvement,
        hypothesis="Improve example function",
        status=ExperimentStatus.FAILED,
        error="Syntax error: unclosed bracket",
    )


# --- RetryStrategy Tests ---


def test_retry_categorize_failure_syntax():
    """Test failure categorization for syntax errors."""
    strategy = RetryStrategy()

    category = strategy.categorize_failure(
        "Syntax error: unclosed bracket on line 10",
        None
    )

    assert category == "syntax"


def test_retry_categorize_failure_type():
    """Test failure categorization for type errors."""
    strategy = RetryStrategy()

    issues = [
        Issue(
            severity=IssueSeverity.ERROR,
            category=IssueCategory.GENERIC_TYPE,
            message="Incomplete generic type: Maybe[",
            line=5,
        )
    ]
    report = ValidationReport(is_valid=False, issues=issues)

    category = strategy.categorize_failure(
        "Type validation failed",
        report
    )

    assert category == "type"


def test_retry_categorize_failure_import():
    """Test failure categorization for import errors."""
    strategy = RetryStrategy()

    issues = [
        Issue(
            severity=IssueSeverity.ERROR,
            category=IssueCategory.IMPORT,
            message="Missing import: Optional",
            line=1,
        )
    ]
    report = ValidationReport(is_valid=False, issues=issues)

    category = strategy.categorize_failure(
        "Import error",
        report
    )

    assert category == "import"


def test_retry_should_retry_with_few_errors(mock_module: CodeModule):
    """Test that experiments with few errors should be retried."""
    strategy = RetryStrategy()

    experiment = Experiment(
        id="test_001",
        module=mock_module,
        improvement=CodeImprovement("desc", "rat", "refactor", "code", 0.8),
        hypothesis="Test hypothesis",
        status=ExperimentStatus.FAILED,
    )

    issues = [
        Issue(
            severity=IssueSeverity.ERROR,
            category=IssueCategory.IMPORT,
            message="Missing import",
            line=1,
        )
    ]
    report = ValidationReport(is_valid=False, issues=issues)

    assert strategy.should_retry(experiment, report) is True


def test_retry_should_not_retry_with_many_errors(mock_module: CodeModule):
    """Test that experiments with too many errors should not be retried."""
    strategy = RetryStrategy()

    experiment = Experiment(
        id="test_001",
        module=mock_module,
        improvement=CodeImprovement("desc", "rat", "refactor", "code", 0.8),
        hypothesis="Test hypothesis",
        status=ExperimentStatus.FAILED,
    )

    # Create 15 critical errors
    issues = [
        Issue(
            severity=IssueSeverity.ERROR,
            category=IssueCategory.IMPORT,
            message=f"Error {i}",
            line=i,
        )
        for i in range(15)
    ]
    report = ValidationReport(is_valid=False, issues=issues)

    assert strategy.should_retry(experiment, report) is False


def test_retry_refine_prompt_syntax(
    mock_prompt_context: PromptContext,
    failed_experiment: Experiment
):
    """Test prompt refinement for syntax errors."""
    strategy = RetryStrategy()

    refined = strategy.refine_prompt(
        original_hypothesis="Improve function",
        failure_reason="Syntax error: unclosed bracket",
        attempt=0,
        context=mock_prompt_context,
        validation_report=None,
    )

    # Should contain retry attempt info
    assert "RETRY ATTEMPT 1/3" in refined

    # Should contain syntax-specific constraints
    assert "SYNTAX" in refined.upper()
    assert "bracket" in refined.lower()

    # Should contain the original error
    assert "unclosed bracket" in refined


def test_retry_refine_prompt_type(
    mock_prompt_context: PromptContext
):
    """Test prompt refinement for type errors."""
    strategy = RetryStrategy()

    issues = [
        Issue(
            severity=IssueSeverity.ERROR,
            category=IssueCategory.GENERIC_TYPE,
            message="Incomplete generic: Maybe[",
            line=10,
        )
    ]
    report = ValidationReport(is_valid=False, issues=issues)

    refined = strategy.refine_prompt(
        original_hypothesis="Add type hints",
        failure_reason="Type validation failed",
        attempt=1,
        context=mock_prompt_context,
        validation_report=report,
    )

    # Should contain type-specific constraints
    assert "TYPE" in refined.upper()
    assert "annotation" in refined.lower()

    # Should mention the specific issue
    assert "Line 10" in refined or "generic" in refined.lower()


# --- FallbackStrategy Tests ---


def test_fallback_should_fallback_after_retry_exhausted(
    failed_experiment: Experiment
):
    """Test that fallback activates after retry is exhausted."""
    strategy = FallbackStrategy()

    assert strategy.should_fallback(failed_experiment, retry_exhausted=True) is True
    assert strategy.should_fallback(failed_experiment, retry_exhausted=False) is False


def test_fallback_identify_primary_target():
    """Test identifying primary target from hypothesis."""
    strategy = FallbackStrategy()

    ast_structure = CodeStructure.from_lists(
        module_name="test",
        classes=[{"name": "MyClass", "line": 10, "methods": ["foo"]}],
        functions=[{"name": "my_function", "line": 5, "params": []}],
        imports=[],
        docstring=None,
        line_count=20,
        complexity_hints=[],
    )

    # Test with explicit function mention
    target = strategy._identify_primary_target(
        "Improve my_function to handle edge cases",
        ast_structure
    )
    assert target == "my_function"

    # Test with explicit class mention
    target = strategy._identify_primary_target(
        "Refactor MyClass for better testability",
        ast_structure
    )
    assert target == "MyClass"


def test_fallback_find_missing_type_annotations():
    """Test finding functions missing type annotations."""
    strategy = FallbackStrategy()

    code = """
def annotated_func(x: int) -> str:
    return str(x)

def missing_annotations(y):
    return y * 2

def partial_annotations(z: int):
    return z + 1
"""

    missing = strategy._find_missing_type_annotations(code)

    assert "missing_annotations" in missing
    assert "partial_annotations" in missing
    assert "annotated_func" not in missing


def test_fallback_find_missing_docstrings():
    """Test finding functions/classes missing docstrings."""
    strategy = FallbackStrategy()

    code = '''
def with_docstring():
    """This has a docstring."""
    pass

def without_docstring():
    pass

class WithDocstring:
    """This class has a docstring."""
    pass

class WithoutDocstring:
    pass
'''

    missing = strategy._find_missing_docstrings(code)

    assert "without_docstring" in missing
    assert "WithoutDocstring" in missing
    assert "with_docstring" not in missing
    assert "WithDocstring" not in missing


def test_fallback_generate_minimal_prompt(
    mock_prompt_context: PromptContext
):
    """Test generating minimal improvement prompt."""
    strategy = FallbackStrategy()

    prompt = strategy.generate_minimal_prompt(
        original_hypothesis="Refactor all functions",
        context=mock_prompt_context,
        target_symbol="example_function"
    )

    # Should mention it's a fallback
    assert "Minimal" in prompt or "fallback" in prompt.lower()

    # Should focus on single target
    assert "example_function" in prompt
    assert "ONLY" in prompt

    # Should preserve other code
    assert "preserve" in prompt.lower() or "unchanged" in prompt.lower()


def test_fallback_generate_type_only_prompt(
    mock_prompt_context: PromptContext
):
    """Test generating type-only improvement prompt."""
    strategy = FallbackStrategy()

    prompt = strategy.generate_type_only_prompt(
        original_hypothesis="Add comprehensive improvements",
        context=mock_prompt_context
    )

    # Should be type-focused
    assert "type" in prompt.lower() and "annotation" in prompt.lower()

    # Should emphasize no logic changes
    assert "DO NOT change any logic" in prompt or "logic" in prompt.lower()

    # Should be marked as safe
    assert "safe" in prompt.lower() or "Safe" in prompt


def test_fallback_generate_docs_only_prompt(
    mock_prompt_context: PromptContext
):
    """Test generating documentation-only prompt."""
    strategy = FallbackStrategy()

    prompt = strategy.generate_docs_only_prompt(
        original_hypothesis="Make comprehensive improvements",
        context=mock_prompt_context
    )

    # Should be docs-focused
    assert "doc" in prompt.lower() or "comment" in prompt.lower()

    # Should emphasize no code changes
    assert "DO NOT change any code" in prompt

    # Should be marked as safest
    assert "safest" in prompt.lower() or "Safest" in prompt


# --- ErrorMemory Tests ---


def test_error_memory_record_failure():
    """Test recording a failure pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_errors.json"
        memory = ErrorMemory(storage_path)

        memory.record_failure(
            module_category="agents",
            module_name="test_module",
            hypothesis="Add type hints",
            failure_type="type",
            failure_details="Incomplete generic type: Maybe["
        )

        # Should be persisted
        assert storage_path.exists()

        # Should be in memory
        assert len(memory.error_patterns) == 1
        assert "agents:type" in memory.error_patterns


def test_error_memory_get_warnings():
    """Test getting warnings for common patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_errors.json"
        memory = ErrorMemory(storage_path)

        # Record same failure 5 times
        for i in range(5):
            memory.record_failure(
                module_category="agents",
                module_name=f"module_{i}",
                hypothesis=f"Hypothesis {i}",
                failure_type="syntax",
                failure_details="Unclosed bracket on line 10"
            )

        warnings = memory.get_warnings_for_module("agents", threshold=3)

        # Should generate warning for repeated pattern
        assert len(warnings) == 1
        assert warnings[0].pattern_type == "syntax"
        assert warnings[0].occurrences == 5
        assert "bracket" in warnings[0].common_detail.lower()


def test_error_memory_format_warnings():
    """Test formatting warnings for prompts."""
    memory = ErrorMemory()

    warnings = [
        ErrorWarning(
            pattern_type="syntax",
            occurrences=10,
            common_detail="unclosed bracket",
            severity="high",
            recommendation="Check all brackets"
        ),
        ErrorWarning(
            pattern_type="type",
            occurrences=3,
            common_detail="incomplete generic",
            severity="low",
            recommendation="Complete all generics"
        )
    ]

    formatted = memory.format_warnings_for_prompt(warnings)

    # Should contain warning header
    assert "COMMON PITFALLS" in formatted

    # Should include all warnings
    assert "syntax" in formatted.lower()
    assert "type" in formatted.lower()

    # Should include severity indicators
    assert "🔴" in formatted  # High severity
    assert "🟢" in formatted  # Low severity


def test_error_memory_get_stats():
    """Test getting error memory statistics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_errors.json"
        memory = ErrorMemory(storage_path)

        # Record various failures
        memory.record_failure("agents", "mod1", "hyp1", "syntax", "error1")
        memory.record_failure("agents", "mod2", "hyp2", "type", "error2")
        memory.record_failure("runtime", "mod3", "hyp3", "syntax", "error3")

        stats = memory.get_stats()

        assert stats.total_failures == 3
        assert stats.unique_patterns == 3
        assert len(stats.categories_affected) == 2
        assert "agents" in stats.categories_affected
        assert "runtime" in stats.categories_affected


def test_error_memory_clear_old_patterns():
    """Test clearing old error patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_errors.json"
        memory = ErrorMemory(storage_path)

        # Record old failure manually
        old_pattern = ErrorPattern(
            module_category="agents",
            module_name="old_module",
            hypothesis_type="refactor",
            failure_type="syntax",
            failure_details="Old error",
            timestamp=(datetime.now() - timedelta(days=100)).isoformat(),
            hypothesis_hash="old_hash"
        )

        # Record recent failure
        memory.record_failure(
            "agents", "new_module", "New hypothesis",
            "type", "Recent error"
        )

        # Add old pattern directly
        memory.error_patterns["agents:syntax"].append(old_pattern)
        memory._persist()

        # Clear patterns older than 90 days
        removed = memory.clear_old_patterns(days_to_keep=90)

        # Should remove 1 old pattern
        assert removed == 1

        # Recent pattern should remain
        stats = memory.get_stats()
        assert stats.total_failures == 1


def test_error_memory_persistence():
    """Test that error memory persists across instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_errors.json"

        # Create first instance and record
        memory1 = ErrorMemory(storage_path)
        memory1.record_failure(
            "agents", "test", "hyp", "syntax", "error"
        )

        # Create second instance - should load from disk
        memory2 = ErrorMemory(storage_path)

        assert len(memory2.error_patterns) == 1
        assert "agents:syntax" in memory2.error_patterns
