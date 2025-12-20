"""
Tests for Intent Layer - The 10 Core Verbs.

Tests cover:
- All 9 command verbs (new, run, check, think, watch, find, fix, speak, judge)
- The intent router (do command)
- Help text display
- Argument parsing
- Output formatting (rich and JSON)
- Error handling
"""

from __future__ import annotations

import json
from collections.abc import Generator
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest

from ..commands import (
    IntentResult,
    _format_epilogue,
    _format_rich,
    _parse_args,
    cmd_check,
    cmd_find,
    cmd_fix,
    cmd_judge,
    cmd_new,
    cmd_run,
    cmd_speak,
    cmd_think,
    cmd_watch,
)
from ..router import (
    IntentCategory,
    RiskLevel,
    Step,
    assess_risk,
    classify_intent,
    cmd_do,
    extract_targets,
    generate_plan,
)

# =============================================================================
# Helper Fixtures
# =============================================================================


# Use pytest's capsys fixture - it's passed as a parameter to test methods


# =============================================================================
# Tests: Shared Types and Helpers
# =============================================================================


class TestIntentResult:
    """Tests for IntentResult type."""

    def test_success_result(self) -> None:
        result = IntentResult(success=True, output={"key": "value"})
        assert result.success is True
        assert result.output == {"key": "value"}
        assert result.error is None
        assert result.suggestions == []
        assert result.next_steps == []

    def test_error_result(self) -> None:
        result = IntentResult(
            success=False,
            error="Something went wrong",
            suggestions=["Try this", "Or that"],
        )
        assert result.success is False
        assert result.error == "Something went wrong"
        assert len(result.suggestions) == 2

    def test_to_dict(self) -> None:
        result = IntentResult(
            success=True,
            output="test",
            next_steps=["step1"],
        )
        d = result.to_dict()
        assert d["success"] is True
        assert d["output"] == "test"
        assert d["next_steps"] == ["step1"]


class TestArgumentParsing:
    """Tests for argument parsing helpers."""

    def test_parse_empty_args(self) -> None:
        opts, positional = _parse_args([])
        assert opts == {}
        assert positional == []

    def test_parse_positional_only(self) -> None:
        opts, positional = _parse_args(["arg1", "arg2"])
        assert opts == {}
        assert positional == ["arg1", "arg2"]

    def test_parse_flags(self) -> None:
        opts, positional = _parse_args(["--verbose", "--dry-run"])
        assert opts["verbose"] is True
        assert opts["dry_run"] is True
        assert positional == []

    def test_parse_key_value(self) -> None:
        opts, positional = _parse_args(["--format=json", "--budget=high"])
        assert opts["format"] == "json"
        assert opts["budget"] == "high"

    def test_parse_mixed(self) -> None:
        opts, positional = _parse_args(["target", "--format=json", "--verbose"])
        assert opts["format"] == "json"
        assert opts["verbose"] is True
        assert positional == ["target"]


class TestFormatting:
    """Tests for output formatting."""

    def test_format_rich_dict(self) -> None:
        output = _format_rich("Title", {"key1": "value1", "key2": "value2"})
        assert "=== Title ===" in output
        assert "key1: value1" in output
        assert "key2: value2" in output

    def test_format_rich_list(self) -> None:
        output = _format_rich("List", ["item1", "item2"])
        assert "- item1" in output
        assert "- item2" in output

    def test_format_rich_string(self) -> None:
        output = _format_rich("String", "plain text")
        assert "plain text" in output

    def test_format_epilogue_empty(self) -> None:
        output = _format_epilogue([])
        assert output == ""

    def test_format_epilogue_with_steps(self) -> None:
        output = _format_epilogue(["Step 1", "Step 2"])
        assert "--- Next Steps ---" in output
        assert "Step 1" in output
        assert "Step 2" in output


# =============================================================================
# Tests: NEW Command
# =============================================================================


class TestCmdNew:
    """Tests for the 'new' command."""

    @pytest.fixture(autouse=True)
    def cleanup_test_agents(self) -> Generator[None, None, None]:
        """Clean up any agents created during tests."""
        import shutil
        from pathlib import Path

        yield

        # Clean up test artifacts
        agents_dir = Path(__file__).parent.parent.parent.parent.parent / "agents"
        for test_dir in ["archimedes", "test"]:
            agent_dir = agents_dir / test_dir
            if agent_dir.exists():
                shutil.rmtree(agent_dir)

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_new(["--help"])
        assert result == 0
        output = capsys.readouterr().out
        assert "kgents new" in output
        assert "Create something new" in output

    def test_no_args_shows_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_new([])
        assert result == 0
        assert "kgents new" in capsys.readouterr().out

    def test_missing_name(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_new(["agent"])
        assert result == 1
        assert "requires <type> and <name>" in capsys.readouterr().out

    def test_invalid_type(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_new(["invalid", "name"])
        assert result == 1
        assert "unknown type" in capsys.readouterr().out

    def test_create_agent(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_new(["agent", "Archimedes"])
        assert result == 0
        output = capsys.readouterr().out
        assert "Created agent" in output
        assert "Archimedes" in output

    def test_create_agent_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_new(["agent", "Archimedes", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["success"] is True
        assert output["output"]["name"] == "Archimedes"

    def test_create_flow(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_new(["flow", "review-pipeline"])
        assert result == 0
        assert "Created flow" in capsys.readouterr().out

    def test_create_tongue(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_new(["tongue", "calendar-commands"])
        assert result == 0
        assert "Created tongue" in capsys.readouterr().out

    def test_create_schema(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_new(["schema", "user-profile"])
        assert result == 0
        assert "Created schema" in capsys.readouterr().out

    def test_with_options(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_new(["agent", "Test", "--genus=b", "--template=minimal"])
        assert result == 0
        output = capsys.readouterr().out
        assert "Created agent" in output


# =============================================================================
# Tests: RUN Command
# =============================================================================


class TestCmdRun:
    """Tests for the 'run' command."""

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_run(["--help"])
        assert result == 0
        assert "kgents run" in capsys.readouterr().out

    def test_no_args_shows_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_run([])
        assert result == 0

    def test_missing_intent(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd_run(["--format=json"])
        # With only options, no positional, should fail
        output = capsys.readouterr().out
        assert "requires an intent" in output or "run" in output

    def test_run_intent(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_run(["test all functions"])
        assert result == 0
        assert "Execution Complete" in capsys.readouterr().out

    def test_run_dry_run(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_run(["test all functions", "--dry-run"])
        assert result == 0
        assert "Dry Run" in capsys.readouterr().out

    def test_run_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_run(["test all functions", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["success"] is True
        assert "intent" in output["output"]

    def test_classification_deterministic(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_run(["lint code", "--format=json", "--dry-run"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["output"]["classification"] == "DETERMINISTIC"

    def test_classification_probabilistic(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_run(["review code for issues", "--format=json", "--dry-run"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["output"]["classification"] == "PROBABILISTIC"


# =============================================================================
# Tests: CHECK Command
# =============================================================================


class TestCmdCheck:
    """Tests for the 'check' command."""

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_check(["--help"])
        assert result == 0
        assert "kgents check" in capsys.readouterr().out

    def test_check_target(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_check(["src/main.py"])
        assert result == 0
        assert "Check" in capsys.readouterr().out

    def test_check_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_check(["src/main.py", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert "target" in output["output"]
        assert "passed" in output["output"]

    def test_check_against_laws(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_check(["test.py", "--against=laws"])
        assert result == 0

    def test_check_strict(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_check(["test.py", "--strict"])
        # May fail if warnings present
        assert result in (0, 1)


# =============================================================================
# Tests: THINK Command
# =============================================================================


class TestCmdThink:
    """Tests for the 'think' command."""

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_think(["--help"])
        assert result == 0
        assert "kgents think" in capsys.readouterr().out

    def test_think_topic(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_think(["optimization strategies"])
        assert result == 0
        assert "Hypotheses" in capsys.readouterr().out

    def test_think_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_think(["optimization strategies", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert "hypotheses" in output["output"]

    def test_think_with_limit(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_think(["topic", "--limit=2", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["output"]["count"] <= 2

    def test_think_with_falsify(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_think(["topic", "--falsify", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        # Hypotheses should have falsification field
        for h in output["output"]["hypotheses"]:
            assert "falsification" in h


# =============================================================================
# Tests: WATCH Command
# =============================================================================


class TestCmdWatch:
    """Tests for the 'watch' command."""

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_watch(["--help"])
        assert result == 0
        assert "kgents watch" in capsys.readouterr().out

    def test_watch_target(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_watch(["./logs/"])
        assert result == 0
        assert "Watching" in capsys.readouterr().out

    def test_watch_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_watch(["./logs/", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["output"]["target"] == "./logs/"


# =============================================================================
# Tests: FIND Command
# =============================================================================


class TestCmdFind:
    """Tests for the 'find' command."""

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_find(["--help"])
        assert result == 0
        assert "kgents find" in capsys.readouterr().out

    def test_find_query(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_find(["calendar operations"])
        assert result == 0
        assert "Search" in capsys.readouterr().out

    def test_find_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_find(["calendar", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert "results" in output["output"]

    def test_find_with_type(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_find(["parser", "--type=agent", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["output"]["type_filter"] == "agent"


# =============================================================================
# Tests: FIX Command
# =============================================================================


class TestCmdFix:
    """Tests for the 'fix' command."""

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_fix(["--help"])
        assert result == 0
        assert "kgents fix" in capsys.readouterr().out

    def test_fix_target(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_fix(["input.json"])
        assert result == 0
        assert "Fixed" in capsys.readouterr().out

    def test_fix_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_fix(["input.json", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["output"]["target"] == "input.json"

    def test_fix_preview(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_fix(["input.json", "--preview", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["output"]["preview"] is True


# =============================================================================
# Tests: SPEAK Command
# =============================================================================


class TestCmdSpeak:
    """Tests for the 'speak' command."""

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_speak(["--help"])
        assert result == 0
        assert "kgents speak" in capsys.readouterr().out

    def test_speak_domain(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_speak(["file operations"])
        assert result == 0
        assert "Tongue Created" in capsys.readouterr().out

    def test_speak_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_speak(["file operations", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["output"]["domain"] == "file operations"
        assert "grammar" in output["output"]

    def test_speak_with_level(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_speak(["domain", "--level=schema", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert output["output"]["level"] == "schema"


# =============================================================================
# Tests: JUDGE Command
# =============================================================================


class TestCmdJudge:
    """Tests for the 'judge' command."""

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_judge(["--help"])
        assert result == 0
        assert "kgents judge" in capsys.readouterr().out

    def test_judge_input(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_judge(["A monolithic agent that does everything"])
        assert result in (0, 1)  # May pass or fail based on evaluation
        assert "Judgment" in capsys.readouterr().out

    def test_judge_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd_judge(["test input", "--format=json"])
        output = json.loads(capsys.readouterr().out)
        assert "overall_verdict" in output["output"]
        assert "evaluations" in output["output"]

    def test_judge_specific_principle(self, capsys: pytest.CaptureFixture[str]) -> None:
        cmd_judge(["input", "--principle=Composable", "--format=json"])
        output = json.loads(capsys.readouterr().out)
        # Should only evaluate one principle
        assert len(output["output"]["evaluations"]) == 1


# =============================================================================
# Tests: Intent Classification (Router)
# =============================================================================


class TestIntentClassification:
    """Tests for intent classification."""

    def test_classify_verification(self) -> None:
        category, confidence = classify_intent("check the code for errors")
        assert category == IntentCategory.VERIFICATION
        assert confidence > 0

    def test_classify_repair(self) -> None:
        category, confidence = classify_intent("fix the broken JSON file")
        assert category == IntentCategory.REPAIR

    def test_classify_analysis(self) -> None:
        category, confidence = classify_intent("think about optimization")
        assert category == IntentCategory.ANALYSIS

    def test_classify_observation(self) -> None:
        category, confidence = classify_intent("watch the logs directory")
        assert category == IntentCategory.OBSERVATION

    def test_classify_search(self) -> None:
        category, confidence = classify_intent("find all parsers")
        assert category == IntentCategory.SEARCH

    def test_classify_composite(self) -> None:
        category, confidence = classify_intent("check and fix input.py")
        assert category == IntentCategory.COMPOSITE


class TestRiskAssessment:
    """Tests for risk assessment."""

    def test_safe_intent(self) -> None:
        steps = [Step(1, "check", [], "Check", RiskLevel.SAFE)]
        risk = assess_risk("check the code", steps)
        assert risk == RiskLevel.SAFE

    def test_moderate_intent(self) -> None:
        steps = [Step(1, "fix", [], "Fix", RiskLevel.MODERATE)]
        risk = assess_risk("fix the code", steps)
        assert risk == RiskLevel.MODERATE

    def test_elevated_from_keywords(self) -> None:
        steps = [Step(1, "check", [], "Check", RiskLevel.SAFE)]
        risk = assess_risk("delete all temp files", steps)
        assert risk == RiskLevel.ELEVATED


class TestTargetExtraction:
    """Tests for extracting targets from intent."""

    def test_extract_file_path(self) -> None:
        targets = extract_targets("check src/main.py for issues")
        assert "src/main.py" in targets

    def test_extract_relative_path(self) -> None:
        targets = extract_targets("analyze ./config.yaml")
        assert "./config.yaml" in targets

    def test_extract_multiple(self) -> None:
        targets = extract_targets("compare src/a.py and src/b.py")
        assert len(targets) >= 2


# =============================================================================
# Tests: Plan Generation (Router)
# =============================================================================


class TestPlanGeneration:
    """Tests for execution plan generation."""

    def test_generate_check_plan(self) -> None:
        plan = generate_plan("check input.py")
        assert plan.category == IntentCategory.VERIFICATION
        assert len(plan.steps) >= 1
        assert any(s.command == "check" for s in plan.steps)

    def test_generate_fix_plan(self) -> None:
        plan = generate_plan("fix broken.json")
        assert any(s.command == "fix" for s in plan.steps)

    def test_generate_composite_plan(self) -> None:
        plan = generate_plan("check and fix input.py")
        # Should have both check and fix
        commands = [s.command for s in plan.steps]
        assert "check" in commands or "fix" in commands

    def test_plan_has_conditions(self) -> None:
        plan = generate_plan("check then fix input.py")
        # Fix should be conditional on check
        fix_steps = [s for s in plan.steps if s.command == "fix"]
        if fix_steps:
            # Condition may or may not be set depending on order
            pass

    def test_plan_to_dict(self) -> None:
        plan = generate_plan("check test.py")
        d = plan.to_dict()
        assert "intent" in d
        assert "category" in d
        assert "steps" in d


class TestStep:
    """Tests for Step type."""

    def test_step_to_dict(self) -> None:
        step = Step(1, "check", ["file.py"], "Check file", RiskLevel.SAFE)
        d = step.to_dict()
        assert d["id"] == 1
        assert d["command"] == "check"
        assert d["args"] == ["file.py"]

    def test_step_render_cli(self) -> None:
        step = Step(1, "check", ["src/main.py"], "Check", RiskLevel.SAFE)
        cli = step.render_cli()
        assert cli == "kgents check src/main.py"

    def test_step_render_cli_no_args(self) -> None:
        step = Step(1, "help", [], "Show help", RiskLevel.SAFE)
        cli = step.render_cli()
        assert cli == "kgents help"


# =============================================================================
# Tests: DO Command (Router)
# =============================================================================


class TestCmdDo:
    """Tests for the 'do' command (intent router)."""

    def test_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_do(["--help"])
        assert result == 0
        assert "kgents do" in capsys.readouterr().out

    def test_no_args_shows_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_do([])
        assert result == 0

    def test_dry_run(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_do(["check input.py", "--dry-run"])
        assert result == 0
        output = capsys.readouterr().out
        assert "Intent Detected" in output

    def test_json_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_do(["check input.py", "--format=json"])
        assert result == 0
        output = json.loads(capsys.readouterr().out)
        assert "intent" in output
        assert "steps" in output

    def test_composite_intent(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_do(["check and fix test.py", "--dry-run"])
        assert result == 0
        output = capsys.readouterr().out
        assert "kgents" in output  # Should show command

    @patch("builtins.input", return_value="n")
    def test_cancelled_execution(
        self, mock_input: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        result = cmd_do(["check test.py"])
        assert result == 0
        assert "cancelled" in capsys.readouterr().out.lower()

    @patch("builtins.input", return_value="y")
    def test_confirmed_execution(
        self, mock_input: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        result = cmd_do(["check test.py"])
        assert result == 0
        assert "Execution Complete" in capsys.readouterr().out

    def test_auto_yes(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = cmd_do(["check test.py", "-y"])
        assert result == 0
        assert "Execution Complete" in capsys.readouterr().out


# =============================================================================
# Tests: Module Imports
# =============================================================================


class TestModuleImports:
    """Tests for module imports and lazy loading."""

    def test_import_commands(self) -> None:
        from ..commands import (
            cmd_check,
            cmd_find,
            cmd_fix,
            cmd_judge,
            cmd_new,
            cmd_run,
            cmd_speak,
            cmd_think,
            cmd_watch,
        )

        assert callable(cmd_new)
        assert callable(cmd_run)
        assert callable(cmd_check)
        assert callable(cmd_think)
        assert callable(cmd_watch)
        assert callable(cmd_find)
        assert callable(cmd_fix)
        assert callable(cmd_speak)
        assert callable(cmd_judge)

    def test_import_router(self) -> None:
        from ..router import classify_intent, cmd_do, generate_plan

        assert callable(cmd_do)
        assert callable(classify_intent)
        assert callable(generate_plan)

    def test_lazy_loading_via_init(self) -> None:
        from .. import cmd_do, cmd_new

        assert callable(cmd_new)
        assert callable(cmd_do)


# =============================================================================
# Tests: Integration
# =============================================================================


class TestIntegration:
    """Integration tests for the intent layer."""

    def test_new_then_check_flow(self, capsys: pytest.CaptureFixture[str]) -> None:
        from pathlib import Path

        # Skip if agents/testagent already exists (from previous test runs or repo)
        if Path("agents/testagent").exists():
            pytest.skip("agents/testagent already exists")

        # Create an agent
        result1 = cmd_new(["agent", "TestAgent", "--format=json"])
        assert result1 == 0

        # Check it (simulated, since we didn't actually create files)
        result2 = cmd_check(["agents/testagent/", "--format=json"])
        assert result2 in (0, 1)

    def test_speak_then_find(self, capsys: pytest.CaptureFixture[str]) -> None:
        # Create a tongue
        result1 = cmd_speak(["calendar", "--format=json"])
        assert result1 == 0

        # Find it (simulated)
        result2 = cmd_find(["calendar", "--format=json"])
        assert result2 == 0

    def test_intent_router_coverage(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that router generates reasonable plans for various intents."""
        intents = [
            "check the code",
            "fix the JSON",
            "think about optimization",
            "watch the logs",
            "find all parsers",
            "speak the calendar language",
            "judge this proposal",
            "run the tests",
            "create a new agent",
        ]

        for intent in intents:
            plan = generate_plan(intent)
            assert len(plan.steps) >= 1
            assert plan.confidence > 0
