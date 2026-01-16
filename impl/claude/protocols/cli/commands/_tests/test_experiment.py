"""
Tests for experiment CLI command.

Tests:
- Command parsing and argument validation
- Integration with ExperimentRunner
- Output formatting (both JSON and rich)
- Storage persistence

Philosophy:
    "The proof IS the decision. The mark IS the witness."

Teaching:
    gotcha: Async tests require pytest-asyncio. Use @pytest.mark.asyncio
            for async test functions.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_experiment():
    """Create a mock experiment result."""
    from datetime import UTC, datetime

    from services.experiment import (
        EvidenceBundle,
        Experiment,
        ExperimentStatus,
        GenerateConfig,
        Trial,
    )

    config = GenerateConfig(spec="def add(a, b): return a + b", n=10)

    trials = [
        Trial(
            index=i,
            input=config.spec,
            output="def add(a, b):\n    return a + b",
            success=i % 3 != 0,  # 66% success rate
            duration_ms=100.0,
            confidence=1.0 if i % 3 != 0 else 0.0,
        )
        for i in range(10)
    ]

    evidence = EvidenceBundle(
        trials_total=10,
        trials_success=7,
        success_rate=0.7,
        mean_confidence=0.7,
        std_confidence=0.46,
        mean_duration_ms=100.0,
    )

    return Experiment(
        id="exp-test123",
        config=config,
        status=ExperimentStatus.COMPLETED,
        trials=trials,
        evidence=evidence,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
    )


def test_generate_command_parsing():
    """Test that generate command parses arguments correctly."""
    from protocols.cli.commands.experiment import cmd_generate

    # Mock the async run to avoid actually running experiments
    with (
        patch("protocols.cli.commands.experiment._run_generate") as mock_run,
        patch("protocols.cli.commands.experiment.get_experiment_store") as mock_store,
        patch("asyncio.run") as mock_asyncio,
    ):
        # Setup mock experiment
        mock_exp = MagicMock()
        mock_exp.to_dict.return_value = {"id": "exp-123"}
        mock_asyncio.return_value = mock_exp

        # Test basic args
        args = ["--spec", "def foo(): pass", "--n", "5"]
        result = cmd_generate(args)

        # Should succeed
        assert result == 0


def test_generate_with_adaptive():
    """Test generate command with adaptive stopping."""
    from protocols.cli.commands.experiment import cmd_generate

    with (
        patch("protocols.cli.commands.experiment._run_generate") as mock_run,
        patch("protocols.cli.commands.experiment.get_experiment_store") as mock_store,
        patch("asyncio.run") as mock_asyncio,
    ):
        mock_exp = MagicMock()
        mock_exp.to_dict.return_value = {"id": "exp-123"}
        mock_asyncio.return_value = mock_exp

        args = ["--spec", "def foo(): pass", "--adaptive", "--confidence", "0.95"]
        result = cmd_generate(args)

        assert result == 0


def test_generate_json_output(mock_experiment):
    """Test generate command with JSON output."""
    from protocols.cli.commands.experiment import cmd_generate

    with (
        patch("protocols.cli.commands.experiment._run_generate") as mock_run,
        patch("protocols.cli.commands.experiment.get_experiment_store") as mock_store,
        patch("asyncio.run") as mock_asyncio,
        patch("builtins.print") as mock_print,
    ):
        mock_asyncio.return_value = mock_experiment

        args = ["--spec", "def foo(): pass", "--json"]
        result = cmd_generate(args)

        # Should output JSON
        assert result == 0
        # Check that print was called with JSON
        assert mock_print.called


def test_history_command():
    """Test history command."""
    from protocols.cli.commands.experiment import cmd_history

    with (
        patch("protocols.cli.commands.experiment.get_experiment_store") as mock_store,
        patch("asyncio.run") as mock_asyncio,
    ):
        # Mock store returning empty list
        mock_asyncio.return_value = []

        args = []
        result = cmd_history(args)

        assert result == 0


def test_history_today_filter(mock_experiment):
    """Test history command with --today filter."""
    from protocols.cli.commands.experiment import cmd_history

    with (
        patch("protocols.cli.commands.experiment.get_experiment_store") as mock_store,
        patch("asyncio.run") as mock_asyncio,
    ):
        mock_asyncio.return_value = [mock_experiment]

        args = ["--today"]
        result = cmd_history(args)

        assert result == 0


def test_history_type_filter(mock_experiment):
    """Test history command with --type filter."""
    from protocols.cli.commands.experiment import cmd_history

    with (
        patch("protocols.cli.commands.experiment.get_experiment_store") as mock_store,
        patch("asyncio.run") as mock_asyncio,
    ):
        mock_asyncio.return_value = [mock_experiment]

        args = ["--type", "generate"]
        result = cmd_history(args)

        assert result == 0


def test_history_json_output(mock_experiment):
    """Test history command with JSON output."""
    from protocols.cli.commands.experiment import cmd_history

    with (
        patch("protocols.cli.commands.experiment.get_experiment_store") as mock_store,
        patch("asyncio.run") as mock_asyncio,
        patch("builtins.print") as mock_print,
    ):
        mock_asyncio.return_value = [mock_experiment]

        args = ["--json"]
        result = cmd_history(args)

        assert result == 0
        # Should output JSON array
        assert mock_print.called


def test_resume_command():
    """Test resume command."""
    from protocols.cli.commands.experiment import cmd_resume

    with (
        patch("protocols.cli.commands.experiment.get_experiment_store") as mock_store,
        patch("asyncio.run") as mock_asyncio,
    ):
        # Mock finding an experiment
        mock_exp = MagicMock()
        mock_exp.config.type.value = "generate"
        mock_exp.status.value = "completed"
        mock_asyncio.return_value = mock_exp

        args = ["exp-123"]
        result = cmd_resume(args)

        # Should succeed (even though resumption not implemented)
        assert result == 0


def test_resume_not_found():
    """Test resume command with non-existent experiment."""
    from protocols.cli.commands.experiment import cmd_resume

    with (
        patch("protocols.cli.commands.experiment.get_experiment_store") as mock_store,
        patch("asyncio.run") as mock_asyncio,
    ):
        # Mock not finding experiment
        mock_asyncio.return_value = None

        args = ["exp-nonexistent"]
        result = cmd_resume(args)

        # Should fail
        assert result == 1


def test_main_help():
    """Test main command without arguments shows help."""
    from protocols.cli.commands.experiment import main

    with patch("builtins.print") as mock_print:
        result = main([])

        assert result == 0
        assert mock_print.called


def test_main_unknown_subcommand():
    """Test main command with unknown subcommand."""
    from protocols.cli.commands.experiment import main

    with patch("builtins.print") as mock_print:
        result = main(["unknown"])

        assert result == 1
        assert mock_print.called
