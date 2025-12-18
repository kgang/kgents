"""
Tests for AGENTESE REPL Tutorial Mode.

Wave 6: Auto-constructing tutorial with hot data caching.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from protocols.cli.repl_tutorial import (
    CONTEXT_DESCRIPTIONS,
    TutorialLesson,
    TutorialState,
    clear_progress,
    generate_lessons,
    generate_lessons_source,
    load_lessons,
    load_progress,
    regenerate_lessons_to_file,
    save_progress,
    validate_response,
)

# =============================================================================
# TutorialLesson Tests
# =============================================================================


class TestTutorialLesson:
    """Tests for TutorialLesson dataclass."""

    def test_lesson_creation(self) -> None:
        """TutorialLesson can be created with all fields."""
        lesson = TutorialLesson(
            name="test_lesson",
            context="root",
            prompt="Type 'hello':",
            expected=["hello"],
            hint="Try typing: hello",
            celebration="Well done!",
        )
        assert lesson.name == "test_lesson"
        assert lesson.context == "root"
        assert lesson.prompt == "Type 'hello':"
        assert lesson.expected == ["hello"]
        assert lesson.hint == "Try typing: hello"
        assert lesson.celebration == "Well done!"

    def test_from_context_generates_lesson(self) -> None:
        """from_context() generates a lesson for entering a context."""
        lesson = TutorialLesson.from_context("self", "internal state")
        assert lesson.name == "discover_self"
        assert lesson.context == "root"
        assert "self" in lesson.prompt.lower()
        assert "self" in lesson.expected
        assert "self" in lesson.hint.lower()

    def test_from_context_all_contexts(self) -> None:
        """from_context() works for all standard contexts."""
        contexts = ["self", "world", "concept", "void", "time"]
        for ctx in contexts:
            lesson = TutorialLesson.from_context(ctx, f"description of {ctx}")
            assert lesson.name == f"discover_{ctx}"
            assert ctx in lesson.expected

    def test_navigation_up_lesson(self) -> None:
        """navigation_up() generates correct lesson."""
        lesson = TutorialLesson.navigation_up()
        assert lesson.name == "navigate_up"
        assert ".." in lesson.expected
        assert ".." in lesson.hint

    def test_introspection_lesson(self) -> None:
        """introspection() generates correct lesson."""
        lesson = TutorialLesson.introspection()
        assert lesson.name == "introspection"
        assert "?" in lesson.expected
        assert "?" in lesson.hint

    def test_composition_lesson(self) -> None:
        """composition() generates correct lesson."""
        lesson = TutorialLesson.composition()
        assert lesson.name == "composition"
        assert ">>" in lesson.prompt
        assert any(">>" in exp for exp in lesson.expected)

    def test_to_dict_serialization(self) -> None:
        """to_dict() serializes all fields."""
        lesson = TutorialLesson(
            name="test",
            context="root",
            prompt="prompt",
            expected=["a", "b"],
            hint="hint",
            celebration="yay",
        )
        data = lesson.to_dict()
        assert data["name"] == "test"
        assert data["context"] == "root"
        assert data["prompt"] == "prompt"
        assert data["expected"] == ["a", "b"]
        assert data["hint"] == "hint"
        assert data["celebration"] == "yay"

    def test_from_dict_deserialization(self) -> None:
        """from_dict() deserializes correctly."""
        data = {
            "name": "test",
            "context": "any",
            "prompt": "do thing",
            "expected": ["x", "y"],
            "hint": "try x",
            "celebration": "nice",
        }
        lesson = TutorialLesson.from_dict(data)
        assert lesson.name == "test"
        assert lesson.context == "any"
        assert lesson.expected == ["x", "y"]

    def test_round_trip_serialization(self) -> None:
        """to_dict() and from_dict() are inverses."""
        original = TutorialLesson(
            name="roundtrip",
            context="self",
            prompt="test prompt",
            expected=["one", "two", "three"],
            hint="test hint",
            celebration="test celebration",
        )
        data = original.to_dict()
        restored = TutorialLesson.from_dict(data)
        assert restored.name == original.name
        assert restored.context == original.context
        assert restored.prompt == original.prompt
        assert restored.expected == original.expected
        assert restored.hint == original.hint
        assert restored.celebration == original.celebration


# =============================================================================
# TutorialState Tests
# =============================================================================


class TestTutorialState:
    """Tests for TutorialState dataclass."""

    def test_state_creation(self) -> None:
        """TutorialState can be created with lessons."""
        lessons = [TutorialLesson.from_context("self", "test")]
        state = TutorialState(lessons=lessons)
        assert len(state.lessons) == 1
        assert state.current_lesson == 0
        assert state.completed == []

    def test_is_complete_false_when_lessons_remain(self) -> None:
        """is_complete is False when lessons remain."""
        lessons = [
            TutorialLesson.from_context("self", "test"),
            TutorialLesson.from_context("world", "test"),
        ]
        state = TutorialState(lessons=lessons, current_lesson=0)
        assert not state.is_complete

    def test_is_complete_true_when_done(self) -> None:
        """is_complete is True when all lessons done."""
        lessons = [TutorialLesson.from_context("self", "test")]
        state = TutorialState(lessons=lessons, current_lesson=1)
        assert state.is_complete

    def test_is_complete_empty_lessons(self) -> None:
        """is_complete is True for empty lessons list."""
        state = TutorialState(lessons=[])
        assert state.is_complete

    def test_progress_percent_calculation(self) -> None:
        """progress_percent calculates correctly."""
        lessons = [
            TutorialLesson.from_context("self", "test"),
            TutorialLesson.from_context("world", "test"),
            TutorialLesson.from_context("void", "test"),
            TutorialLesson.from_context("time", "test"),
        ]
        state = TutorialState(lessons=lessons, current_lesson=2)
        assert state.progress_percent == 50

    def test_progress_percent_zero(self) -> None:
        """progress_percent is 0 at start."""
        lessons = [TutorialLesson.from_context("self", "test")]
        state = TutorialState(lessons=lessons, current_lesson=0)
        assert state.progress_percent == 0

    def test_progress_percent_hundred(self) -> None:
        """progress_percent is 100 at end."""
        lessons = [TutorialLesson.from_context("self", "test")]
        state = TutorialState(lessons=lessons, current_lesson=1)
        assert state.progress_percent == 100

    def test_progress_percent_empty_lessons(self) -> None:
        """progress_percent is 100 for empty lessons."""
        state = TutorialState(lessons=[])
        assert state.progress_percent == 100


# =============================================================================
# Lesson Generation Tests
# =============================================================================


class TestGenerateLessons:
    """Tests for auto-constructing lesson generation."""

    def test_generate_lessons_returns_list(self) -> None:
        """generate_lessons() returns a list of TutorialLessons."""
        lessons = generate_lessons()
        assert isinstance(lessons, list)
        assert all(isinstance(l, TutorialLesson) for l in lessons)

    def test_generate_lessons_covers_all_contexts(self) -> None:
        """generate_lessons() covers all five contexts."""
        lessons = generate_lessons()
        lesson_names = [l.name for l in lessons]
        assert "discover_self" in lesson_names
        assert "discover_world" in lesson_names
        assert "discover_concept" in lesson_names
        assert "discover_void" in lesson_names
        assert "discover_time" in lesson_names

    def test_generate_lessons_includes_navigation(self) -> None:
        """generate_lessons() includes navigation lesson."""
        lessons = generate_lessons()
        lesson_names = [l.name for l in lessons]
        assert "navigate_up" in lesson_names

    def test_generate_lessons_includes_introspection(self) -> None:
        """generate_lessons() includes introspection lesson."""
        lessons = generate_lessons()
        lesson_names = [l.name for l in lessons]
        assert "introspection" in lesson_names

    def test_generate_lessons_includes_composition(self) -> None:
        """generate_lessons() includes composition lesson."""
        lessons = generate_lessons()
        lesson_names = [l.name for l in lessons]
        assert "composition" in lesson_names

    def test_generate_lessons_pedagogical_order(self) -> None:
        """generate_lessons() orders lessons pedagogically."""
        lessons = generate_lessons()
        names = [l.name for l in lessons]

        # Self should come first (most relatable)
        self_idx = names.index("discover_self")
        assert self_idx == 0

        # Composition should come last (advanced)
        comp_idx = names.index("composition")
        assert comp_idx == len(lessons) - 1

    def test_generate_lessons_with_custom_contexts(self) -> None:
        """generate_lessons() accepts custom contexts."""
        custom_contexts = frozenset({"self", "world"})
        custom_holons = {"self": ["status"], "world": ["agents"]}
        lessons = generate_lessons(
            contexts=custom_contexts,
            context_holons=custom_holons,
        )
        lesson_names = [l.name for l in lessons]
        assert "discover_self" in lesson_names
        assert "discover_world" in lesson_names
        # Should not include contexts not in custom set
        assert "discover_concept" not in lesson_names


class TestGenerateLessonsSource:
    """Tests for generating Python source code."""

    def test_generate_lessons_source_is_valid_python(self) -> None:
        """generate_lessons_source() produces valid Python."""
        source = generate_lessons_source()
        # Should be compilable
        compile(source, "<string>", "exec")

    def test_generate_lessons_source_contains_cached_lessons(self) -> None:
        """generate_lessons_source() defines CACHED_LESSONS."""
        source = generate_lessons_source()
        assert "CACHED_LESSONS" in source
        assert "list[dict]" in source

    def test_generate_lessons_source_has_header(self) -> None:
        """generate_lessons_source() includes generation header."""
        source = generate_lessons_source()
        assert "Auto-generated" in source
        assert "DO NOT EDIT" in source


class TestRegenerateLessonsToFile:
    """Tests for hot data file regeneration."""

    def test_regenerate_creates_file(self) -> None:
        """regenerate_lessons_to_file() creates the output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test_lessons.py"
            result = regenerate_lessons_to_file(output)
            assert result == output
            assert output.exists()

    def test_regenerate_file_is_valid_python(self) -> None:
        """regenerate_lessons_to_file() creates valid Python."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test_lessons.py"
            regenerate_lessons_to_file(output)
            content = output.read_text()
            compile(content, str(output), "exec")

    def test_regenerate_creates_parent_directories(self) -> None:
        """regenerate_lessons_to_file() creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "nested" / "dir" / "lessons.py"
            regenerate_lessons_to_file(output)
            assert output.exists()


class TestLoadLessons:
    """Tests for lesson loading with hot data fallback."""

    def test_load_lessons_returns_list(self) -> None:
        """load_lessons() returns a list of TutorialLessons."""
        lessons = load_lessons()
        assert isinstance(lessons, list)
        assert all(isinstance(l, TutorialLesson) for l in lessons)

    def test_load_lessons_has_expected_count(self) -> None:
        """load_lessons() returns expected number of lessons."""
        lessons = load_lessons()
        # 5 contexts + navigation + introspection + composition = 8
        assert len(lessons) == 8


# =============================================================================
# Progress Persistence Tests
# =============================================================================


class TestProgressPersistence:
    """Tests for tutorial progress save/load."""

    def test_save_progress_creates_file(self) -> None:
        """save_progress() creates progress file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = Path(tmpdir) / "progress.json"
            state = TutorialState(
                lessons=[TutorialLesson.from_context("self", "test")],
                current_lesson=1,
                completed=["discover_self"],
            )
            result = save_progress(state, progress_file)
            assert result is True
            assert progress_file.exists()

    def test_save_progress_json_format(self) -> None:
        """save_progress() writes valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = Path(tmpdir) / "progress.json"
            state = TutorialState(
                lessons=[TutorialLesson.from_context("self", "test")],
                current_lesson=1,
                completed=["discover_self"],
            )
            save_progress(state, progress_file)
            data = json.loads(progress_file.read_text())
            assert data["current_lesson"] == 1
            assert data["completed"] == ["discover_self"]

    def test_load_progress_returns_none_for_missing_file(self) -> None:
        """load_progress() returns None if file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = Path(tmpdir) / "nonexistent.json"
            result = load_progress(progress_file)
            assert result is None

    def test_load_progress_returns_data(self) -> None:
        """load_progress() returns saved data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = Path(tmpdir) / "progress.json"
            state = TutorialState(
                lessons=[TutorialLesson.from_context("self", "test")],
                current_lesson=2,
                completed=["a", "b"],
            )
            save_progress(state, progress_file)
            data = load_progress(progress_file)
            assert data is not None
            assert data["current_lesson"] == 2
            assert data["completed"] == ["a", "b"]

    def test_load_progress_handles_invalid_json(self) -> None:
        """load_progress() returns None for invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = Path(tmpdir) / "progress.json"
            progress_file.write_text("not valid json {{{")
            result = load_progress(progress_file)
            assert result is None

    def test_clear_progress_removes_file(self) -> None:
        """clear_progress() removes the progress file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = Path(tmpdir) / "progress.json"
            progress_file.write_text("{}")
            result = clear_progress(progress_file)
            assert result is True
            assert not progress_file.exists()

    def test_clear_progress_returns_true_for_missing_file(self) -> None:
        """clear_progress() returns True if file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = Path(tmpdir) / "nonexistent.json"
            result = clear_progress(progress_file)
            assert result is True


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidateResponse:
    """Tests for response validation."""

    def test_validate_exact_match(self) -> None:
        """validate_response() accepts exact matches."""
        lesson = TutorialLesson(
            name="test",
            context="root",
            prompt="Type 'hello':",
            expected=["hello"],
            hint="hint",
            celebration="yay",
        )
        assert validate_response("hello", lesson) is True

    def test_validate_case_insensitive(self) -> None:
        """validate_response() is case-insensitive."""
        lesson = TutorialLesson(
            name="test",
            context="root",
            prompt="Type 'HELLO':",
            expected=["HELLO"],
            hint="hint",
            celebration="yay",
        )
        assert validate_response("hello", lesson) is True
        assert validate_response("HELLO", lesson) is True
        assert validate_response("HeLLo", lesson) is True

    def test_validate_strips_whitespace(self) -> None:
        """validate_response() strips leading/trailing whitespace."""
        lesson = TutorialLesson(
            name="test",
            context="root",
            prompt="Type 'self':",
            expected=["self"],
            hint="hint",
            celebration="yay",
        )
        assert validate_response("  self  ", lesson) is True
        assert validate_response("\tself\n", lesson) is True

    def test_validate_multiple_expected(self) -> None:
        """validate_response() accepts any of multiple expected values."""
        lesson = TutorialLesson(
            name="test",
            context="root",
            prompt="Type a command:",
            expected=["foo", "bar", "baz"],
            hint="hint",
            celebration="yay",
        )
        assert validate_response("foo", lesson) is True
        assert validate_response("bar", lesson) is True
        assert validate_response("baz", lesson) is True

    def test_validate_rejects_wrong_input(self) -> None:
        """validate_response() rejects incorrect input."""
        lesson = TutorialLesson(
            name="test",
            context="root",
            prompt="Type 'self':",
            expected=["self"],
            hint="hint",
            celebration="yay",
        )
        assert validate_response("world", lesson) is False
        assert validate_response("selfish", lesson) is False
        assert validate_response("", lesson) is False


# =============================================================================
# REPL Integration Tests
# =============================================================================


class TestReplIntegration:
    """Tests for REPL integration with tutorial mode."""

    def test_cmd_interactive_recognizes_tutorial_flag(self) -> None:
        """cmd_interactive() recognizes --tutorial flag."""
        from protocols.cli.repl import cmd_interactive

        # Just verify the function handles the flag without error
        # (We can't easily test the interactive flow)
        # This test verifies the import path works
        assert callable(cmd_interactive)

    def test_tutorial_module_importable(self) -> None:
        """Tutorial module is importable from REPL."""
        from protocols.cli.repl_tutorial import run_tutorial_mode

        assert callable(run_tutorial_mode)

    def test_generated_lessons_importable(self) -> None:
        """Generated lessons file is importable."""
        from protocols.cli.generated.tutorial_lessons import CACHED_LESSONS

        assert isinstance(CACHED_LESSONS, list)
        assert len(CACHED_LESSONS) > 0


# =============================================================================
# Context Descriptions Tests
# =============================================================================


class TestContextDescriptions:
    """Tests for context description constants."""

    def test_all_contexts_have_descriptions(self) -> None:
        """All standard contexts have descriptions."""
        contexts = ["self", "world", "concept", "void", "time"]
        for ctx in contexts:
            assert ctx in CONTEXT_DESCRIPTIONS
            assert len(CONTEXT_DESCRIPTIONS[ctx]) > 0

    def test_descriptions_are_human_readable(self) -> None:
        """Context descriptions are human-readable strings."""
        for ctx, desc in CONTEXT_DESCRIPTIONS.items():
            assert isinstance(desc, str)
            # Should be descriptive, not just the context name
            assert len(desc) > len(ctx)
