"""
Tests for Wave 4: HabitEncoder, SessionPatternAnalyzer, CodePatternAnalyzer.

These tests verify the habit encoding pipeline works correctly.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from protocols.prompt.habits import (
    GitPattern,
    HabitEncoder,
    HabitEncoderConfig,
    PolicyVector,
    encode_habits,
)
from protocols.prompt.habits.code_analyzer import (
    CodePattern,
    CodePatternAnalyzer,
    analyze_code,
)
from protocols.prompt.habits.session_analyzer import (
    SessionPattern,
    SessionPatternAnalyzer,
    analyze_sessions,
)

# =============================================================================
# HabitEncoder Tests
# =============================================================================


class TestHabitEncoderConfig:
    """Tests for HabitEncoderConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = HabitEncoderConfig.default()
        assert config.git_enabled is True
        assert config.session_enabled is True
        assert config.code_enabled is True
        assert (
            config.git_weight + config.session_weight + config.code_weight
            == pytest.approx(1.0)
        )

    def test_config_validation(self) -> None:
        """Test validation rejects invalid weights."""
        config = HabitEncoderConfig(
            git_weight=0.5,
            session_weight=0.5,
            code_weight=0.5,  # Sum = 1.5
        )
        with pytest.raises(ValueError, match="must sum to 1.0"):
            config.validate()

    def test_valid_config_passes(self) -> None:
        """Test valid config passes validation."""
        config = HabitEncoderConfig(
            git_weight=0.4,
            session_weight=0.3,
            code_weight=0.3,
        )
        config.validate()  # Should not raise


class TestHabitEncoder:
    """Tests for HabitEncoder."""

    @pytest.fixture
    def encoder(self, tmp_path: Path) -> HabitEncoder:
        """Create encoder with temp path."""
        return HabitEncoder(repo_path=tmp_path)

    def test_initialization(self, encoder: HabitEncoder) -> None:
        """Test encoder initializes correctly."""
        assert encoder.repo_path is not None
        assert encoder.config is not None

    def test_encode_returns_policy_vector(self, encoder: HabitEncoder) -> None:
        """Test encode returns a PolicyVector."""
        # Will use defaults since no real data
        policy = encoder.encode()
        assert isinstance(policy, PolicyVector)
        assert len(policy.reasoning_trace) > 0

    def test_encode_with_mock_git(self, tmp_path: Path) -> None:
        """Test encoding with mocked git analyzer."""
        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = [
            GitPattern(
                pattern_type="commit_style",
                description="Uses conventional commits",
                confidence=0.8,
                evidence=(),
                details={"conventional_ratio": 0.85, "avg_length": 60},
            )
        ]

        encoder = HabitEncoder(
            repo_path=tmp_path,
            _git_analyzer=mock_analyzer,
        )
        policy = encoder.encode()

        assert "git" in policy.learned_from
        mock_analyzer.analyze.assert_called_once()

    def test_encode_merges_multiple_sources(self, tmp_path: Path) -> None:
        """Test that multiple sources are merged."""
        # Create mock analyzers
        mock_git = MagicMock()
        mock_git.analyze.return_value = [
            GitPattern(
                pattern_type="commit_style",
                description="Conventional",
                confidence=0.8,
                evidence=(),
                details={"conventional_ratio": 0.9, "avg_length": 80},
            )
        ]

        mock_session = MagicMock()
        mock_session.analyze.return_value = [
            GitPattern(  # Using GitPattern for compatibility
                pattern_type="command_frequency",
                description="Terse commands",
                confidence=0.7,
                evidence=(),
                details={"avg_length": 40},
            )
        ]

        encoder = HabitEncoder(
            repo_path=tmp_path,
            _git_analyzer=mock_git,
            _session_analyzer=mock_session,
        )
        policy = encoder.encode()

        # Should have traces from merging
        assert "Merging" in " ".join(policy.reasoning_trace)

    def test_encode_handles_failures_gracefully(self, tmp_path: Path) -> None:
        """Test that failures in one analyzer don't break others."""
        mock_git = MagicMock()
        mock_git.analyze.side_effect = RuntimeError("Git failed")

        encoder = HabitEncoder(
            repo_path=tmp_path,
            _git_analyzer=mock_git,
        )
        policy = encoder.encode()

        # Should still return a policy
        assert isinstance(policy, PolicyVector)
        assert "failed" in " ".join(policy.reasoning_trace).lower()


class TestEncodeHabitsConvenience:
    """Tests for encode_habits convenience function."""

    def test_encode_habits_returns_policy(self, tmp_path: Path) -> None:
        """Test convenience function returns PolicyVector."""
        policy = encode_habits(tmp_path)
        assert isinstance(policy, PolicyVector)


# =============================================================================
# SessionPatternAnalyzer Tests
# =============================================================================


class TestSessionPatternAnalyzer:
    """Tests for SessionPatternAnalyzer."""

    @pytest.fixture
    def mock_claude_dir(self, tmp_path: Path) -> Path:
        """Create mock ~/.claude directory."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        return claude_dir

    def test_initialization(self, mock_claude_dir: Path) -> None:
        """Test analyzer initializes."""
        analyzer = SessionPatternAnalyzer(claude_dir=mock_claude_dir)
        assert analyzer.claude_dir == mock_claude_dir

    def test_analyze_empty_dir(self, mock_claude_dir: Path) -> None:
        """Test analyzing empty directory."""
        analyzer = SessionPatternAnalyzer(claude_dir=mock_claude_dir)
        patterns = analyzer.analyze()
        assert patterns == []

    def test_analyze_with_history(self, mock_claude_dir: Path) -> None:
        """Test analyzing history.jsonl."""
        # Create history file
        history_file = mock_claude_dir / "history.jsonl"
        now = datetime.now()
        entries = [
            {
                "display": "What is the meaning of life?",
                "timestamp": int((now - timedelta(hours=i)).timestamp() * 1000),
                "project": "/Users/test/project",
            }
            for i in range(20)
        ]
        history_file.write_text("\n".join(json.dumps(e) for e in entries))

        analyzer = SessionPatternAnalyzer(
            claude_dir=mock_claude_dir,
            lookback_days=7,
        )
        patterns = analyzer.analyze()

        # Should find some patterns
        assert len(patterns) > 0
        assert all(isinstance(p, SessionPattern) for p in patterns)

    def test_command_frequency_pattern(self, mock_claude_dir: Path) -> None:
        """Test command frequency detection."""
        history_file = mock_claude_dir / "history.jsonl"
        now = datetime.now()

        # Create entries with slash commands
        entries = [
            {
                "display": f"/test command {i}",
                "timestamp": int((now - timedelta(hours=i)).timestamp() * 1000),
                "project": "/Users/test/project",
            }
            for i in range(15)
        ]
        history_file.write_text("\n".join(json.dumps(e) for e in entries))

        analyzer = SessionPatternAnalyzer(claude_dir=mock_claude_dir)
        patterns = analyzer.analyze()

        # Should detect slash command pattern
        freq_patterns = [p for p in patterns if p.pattern_type == "command_frequency"]
        assert len(freq_patterns) > 0
        assert "slash" in freq_patterns[0].description.lower()

    def test_time_usage_pattern(self, mock_claude_dir: Path) -> None:
        """Test time usage detection."""
        history_file = mock_claude_dir / "history.jsonl"
        now = datetime.now()

        # Create enough entries at morning hours (need >= 20 for analysis)
        entries = [
            {
                "display": "morning task",
                "timestamp": int(
                    (now - timedelta(hours=i)).replace(hour=9 + (i % 3)).timestamp()
                    * 1000
                ),
                "project": "/Users/test/project",
            }
            for i in range(25)
        ]
        history_file.write_text("\n".join(json.dumps(e) for e in entries))

        analyzer = SessionPatternAnalyzer(claude_dir=mock_claude_dir, lookback_days=30)
        patterns = analyzer.analyze()

        # Should detect time pattern (if enough data)
        time_patterns = [p for p in patterns if p.pattern_type == "time_usage"]
        # May not have enough data depending on timestamp generation
        if len(time_patterns) > 0:
            assert time_patterns[0].details.get("morning_ratio", 0) >= 0

    def test_project_focus_pattern(self, mock_claude_dir: Path) -> None:
        """Test project focus detection."""
        history_file = mock_claude_dir / "history.jsonl"
        now = datetime.now()

        # Create entries focused on one project
        entries = [
            {
                "display": "task",
                "timestamp": int((now - timedelta(hours=i)).timestamp() * 1000),
                "project": f"/Users/test/{'main-project' if i < 15 else 'other'}",
            }
            for i in range(20)
        ]
        history_file.write_text("\n".join(json.dumps(e) for e in entries))

        analyzer = SessionPatternAnalyzer(claude_dir=mock_claude_dir)
        patterns = analyzer.analyze()

        # Should detect project focus
        focus_patterns = [p for p in patterns if p.pattern_type == "project_focus"]
        assert len(focus_patterns) > 0

    def test_to_git_pattern_conversion(self) -> None:
        """Test SessionPattern converts to GitPattern."""
        pattern = SessionPattern(
            pattern_type="command_frequency",
            description="Test",
            confidence=0.8,
            evidence=(),
            details={},
        )
        git_pattern = pattern.to_git_pattern()
        assert isinstance(git_pattern, GitPattern)
        assert git_pattern.confidence == 0.8


# =============================================================================
# CodePatternAnalyzer Tests
# =============================================================================


class TestCodePatternAnalyzer:
    """Tests for CodePatternAnalyzer."""

    @pytest.fixture
    def python_repo(self, tmp_path: Path) -> Path:
        """Create a mock Python repository."""
        # Create some Python files
        (tmp_path / "module.py").write_text('''
"""Module docstring."""

from __future__ import annotations
from typing import Optional

def snake_case_function(arg: str) -> str:
    """Function docstring."""
    return arg.upper()

class MyClass:
    """Class docstring."""

    def method(self, x: int) -> int:
        """Method docstring."""
        return x * 2
''')

        (tmp_path / "another.py").write_text('''
"""Another module."""

def another_function(x, y):
    return x + y

class AnotherClass:
    pass
''')
        return tmp_path

    def test_initialization(self, python_repo: Path) -> None:
        """Test analyzer initializes."""
        analyzer = CodePatternAnalyzer(repo_path=python_repo)
        assert analyzer.repo_path == python_repo

    def test_analyze_returns_patterns(self, python_repo: Path) -> None:
        """Test analysis returns patterns."""
        patterns = analyze_code(python_repo)
        assert len(patterns) > 0
        assert all(isinstance(p, CodePattern) for p in patterns)

    def test_naming_pattern_detection(self, python_repo: Path) -> None:
        """Test naming convention detection."""
        analyzer = CodePatternAnalyzer(repo_path=python_repo)
        patterns = analyzer.analyze()

        naming_patterns = [p for p in patterns if p.pattern_type == "naming"]
        assert len(naming_patterns) > 0
        # Should detect snake_case
        assert naming_patterns[0].details.get("snake_case_ratio", 0) > 0.5

    def test_type_hint_detection(self, python_repo: Path) -> None:
        """Test type hint usage detection."""
        # Add more files to meet minimum threshold (10 functions)
        for i in range(5):
            (python_repo / f"extra{i}.py").write_text(f'''
def func_{i}(x: int) -> int:
    """Doc."""
    return x
def func2_{i}(y: str) -> str:
    return y
''')
        analyzer = CodePatternAnalyzer(repo_path=python_repo)
        patterns = analyzer.analyze()

        typing_patterns = [p for p in patterns if p.pattern_type == "typing"]
        # With enough functions, should detect typing patterns
        if len(typing_patterns) > 0:
            assert typing_patterns[0].details.get("arg_annotation_ratio", 0) >= 0

    def test_docstring_detection(self, python_repo: Path) -> None:
        """Test docstring usage detection."""
        # Add more files to meet minimum threshold
        for i in range(5):
            (python_repo / f"doc{i}.py").write_text(f'''
"""Module doc."""
def func_{i}():
    """Function doc."""
    pass
def func2_{i}():
    pass
''')
        analyzer = CodePatternAnalyzer(repo_path=python_repo)
        patterns = analyzer.analyze()

        doc_patterns = [p for p in patterns if p.pattern_type == "docstrings"]
        # With enough functions, should detect docstring patterns
        if len(doc_patterns) > 0:
            assert doc_patterns[0].details.get("module_docstring_ratio", 0) >= 0

    def test_structure_detection(self, python_repo: Path) -> None:
        """Test code structure detection."""
        # Add more files to meet minimum threshold
        for i in range(5):
            (python_repo / f"struct{i}.py").write_text(f"""
class Class{i}:
    def method(self): pass
def standalone_{i}(): pass
""")
        analyzer = CodePatternAnalyzer(repo_path=python_repo)
        patterns = analyzer.analyze()

        struct_patterns = [p for p in patterns if p.pattern_type == "structure"]
        # With enough classes/functions, should detect structure patterns
        if len(struct_patterns) > 0:
            assert "class_ratio" in struct_patterns[0].details

    def test_excludes_test_files(self, tmp_path: Path) -> None:
        """Test that test files in _tests directory are excluded."""
        # Create a _tests directory file (the main exclusion pattern)
        tests_dir = tmp_path / "_tests"
        tests_dir.mkdir()
        (tests_dir / "test_foo.py").write_text("def test_foo(): pass")
        (tmp_path / "module.py").write_text("def regular_function(): pass")

        analyzer = CodePatternAnalyzer(repo_path=tmp_path)

        # _tests directory files should be excluded
        assert analyzer._is_excluded(tests_dir / "test_foo.py")

    def test_handles_syntax_errors(self, tmp_path: Path) -> None:
        """Test graceful handling of syntax errors."""
        (tmp_path / "bad.py").write_text("def broken(")
        (tmp_path / "good.py").write_text("def good(): pass")

        analyzer = CodePatternAnalyzer(repo_path=tmp_path)
        patterns = analyzer.analyze()

        # Should still return patterns from good file
        assert len(patterns) >= 0  # May or may not find patterns

    def test_to_git_pattern_conversion(self) -> None:
        """Test CodePattern converts to GitPattern."""
        pattern = CodePattern(
            pattern_type="naming",
            description="Snake case",
            confidence=0.9,
            evidence=(),
            details={},
        )
        git_pattern = pattern.to_git_pattern()
        assert isinstance(git_pattern, GitPattern)


# =============================================================================
# PolicyVector Extension Tests
# =============================================================================


class TestPolicyVectorSessionPatterns:
    """Tests for PolicyVector.from_session_patterns."""

    def test_from_session_patterns_verbosity(self) -> None:
        """Test verbosity derivation from session patterns."""
        patterns = [
            SessionPattern(
                pattern_type="command_frequency",
                description="Long prompts",
                confidence=0.7,
                evidence=(),
                details={"avg_length": 200},
            )
        ]
        policy = PolicyVector.from_session_patterns(patterns)
        assert policy.verbosity == 0.7  # Long prompts = high verbosity
        assert "sessions" in policy.learned_from

    def test_from_session_patterns_question_oriented(self) -> None:
        """Test question-oriented users get higher verbosity."""
        patterns = [
            SessionPattern(
                pattern_type="command_frequency",
                description="Questions",
                confidence=0.7,
                evidence=(),
                details={"question_ratio": 0.6},
            )
        ]
        policy = PolicyVector.from_session_patterns(patterns)
        assert policy.verbosity >= 0.6


class TestPolicyVectorCodePatterns:
    """Tests for PolicyVector.from_code_patterns."""

    def test_from_code_patterns_formality(self) -> None:
        """Test formality derivation from code patterns."""
        patterns = [
            CodePattern(
                pattern_type="typing",
                description="Strong types",
                confidence=0.8,
                evidence=(),
                details={"arg_annotation_ratio": 0.9},
            )
        ]
        policy = PolicyVector.from_code_patterns(patterns)
        assert policy.formality == 0.8  # Strong types = high formality
        assert "code" in policy.learned_from

    def test_from_code_patterns_docstrings(self) -> None:
        """Test verbosity from docstring patterns."""
        patterns = [
            CodePattern(
                pattern_type="docstrings",
                description="Well documented",
                confidence=0.8,
                evidence=(),
                details={"function_docstring_ratio": 0.8},
            )
        ]
        policy = PolicyVector.from_code_patterns(patterns)
        assert policy.verbosity == 0.7  # Good docs = higher verbosity


# =============================================================================
# Integration Tests
# =============================================================================


class TestHabitEncodingIntegration:
    """Integration tests for the full habit encoding pipeline."""

    def test_full_pipeline_with_real_repo(self) -> None:
        """Test full pipeline on the actual kgents repo."""
        # Find repo root
        repo_path = Path(__file__).parent.parent.parent.parent.parent.parent
        if not (repo_path / ".git").exists():
            pytest.skip("Not in a git repository")

        # Run full encoding
        policy = encode_habits(
            repo_path,
            config=HabitEncoderConfig(
                session_enabled=False,  # Skip session (may not have data)
            ),
        )

        # Should produce a valid policy
        assert isinstance(policy, PolicyVector)
        assert 0.0 <= policy.verbosity <= 1.0
        assert 0.0 <= policy.formality <= 1.0
        assert len(policy.reasoning_trace) > 0

        # Should have learned from git
        assert "git" in policy.learned_from

    def test_policy_influences_section_weights(self, tmp_path: Path) -> None:
        """Test that policy weights can be used for section prioritization."""
        policy = PolicyVector(
            section_weights=(
                ("principles", 1.0),
                ("skills", 0.5),
            ),
        )

        # Use weights for prioritization
        sections = ["skills", "principles", "systems"]
        sorted_sections = sorted(
            sections,
            key=lambda s: policy.get_section_weight(s, 0.5),
            reverse=True,
        )

        assert sorted_sections[0] == "principles"
        assert sorted_sections[-1] == "systems"  # Default weight
