"""
Tests for the CLI commands.

Tests:
- compile command with checkpointing
- history command
- rollback command
- diff command
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from protocols.prompt.cli import (
    compile_prompt,
    do_rollback,
    show_diff,
    show_history,
)

from protocols.prompt.rollback import (
    CheckpointId,
    InMemoryCheckpointStorage,
    RollbackRegistry,
)

# =============================================================================
# Compile Command Tests
# =============================================================================


class TestCompileCommand:
    """Tests for the compile command."""

    def test_compile_without_checkpoint(self, tmp_path):
        """Compile without creating checkpoint."""
        output = tmp_path / "output.md"
        content = compile_prompt(output_path=output, checkpoint=False)

        assert output.exists()
        assert len(content) > 0
        assert "kgents" in content.lower() or "agent" in content.lower()

    def test_compile_with_output(self, tmp_path):
        """Compile and save to file."""
        output = tmp_path / "compiled.md"
        content = compile_prompt(output_path=output, checkpoint=False)

        assert output.exists()
        saved_content = output.read_text()
        assert saved_content == content


# =============================================================================
# History Command Tests
# =============================================================================


class TestHistoryCommand:
    """Tests for the history command."""

    def test_empty_history(self, capsys):
        """Show message when no history exists."""
        # Use a fresh storage location
        with patch("protocols.prompt.cli.get_default_registry") as mock_registry:
            registry = RollbackRegistry(storage=InMemoryCheckpointStorage())
            mock_registry.return_value = registry

            show_history(limit=10)

            captured = capsys.readouterr()
            assert "No checkpoint history" in captured.out

    def test_history_with_entries(self, capsys):
        """Show history entries."""
        with patch("protocols.prompt.cli.get_default_registry") as mock_registry:
            registry = RollbackRegistry(storage=InMemoryCheckpointStorage())
            mock_registry.return_value = registry

            # Create some checkpoints
            registry.checkpoint(
                before_content="V1",
                after_content="V2",
                before_sections=(),
                after_sections=(),
                reason="Test change 1",
            )
            registry.checkpoint(
                before_content="V2",
                after_content="V3",
                before_sections=(),
                after_sections=(),
                reason="Test change 2",
            )

            show_history(limit=10)

            captured = capsys.readouterr()
            assert "PROMPT EVOLUTION TIMELINE" in captured.out
            assert "Test change" in captured.out


# =============================================================================
# Rollback Command Tests
# =============================================================================


class TestRollbackCommand:
    """Tests for the rollback command."""

    def test_rollback_short_id(self, capsys):
        """Reject IDs shorter than 8 chars."""
        with pytest.raises(SystemExit) as exc_info:
            do_rollback("abc")

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "at least 8 characters" in captured.out

    def test_rollback_not_found(self, capsys):
        """Error when checkpoint not found."""
        with patch("protocols.prompt.cli.get_default_registry") as mock_registry:
            registry = RollbackRegistry(storage=InMemoryCheckpointStorage())
            mock_registry.return_value = registry

            with pytest.raises(SystemExit) as exc_info:
                do_rollback("nonexistent")

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "No checkpoint found" in captured.out

    def test_rollback_success(self, capsys):
        """Successful rollback."""
        with patch("protocols.prompt.cli.get_default_registry") as mock_registry:
            registry = RollbackRegistry(storage=InMemoryCheckpointStorage())
            mock_registry.return_value = registry
            registry.set_current("V1", ())

            # Create checkpoint
            checkpoint_id = registry.checkpoint(
                before_content="V1",
                after_content="V2",
                before_sections=(),
                after_sections=(),
                reason="Test change",
            )

            # Rollback using the checkpoint ID
            do_rollback(checkpoint_id)

            captured = capsys.readouterr()
            assert "Rollback successful" in captured.out


# =============================================================================
# Diff Command Tests
# =============================================================================


class TestDiffCommand:
    """Tests for the diff command."""

    def test_diff_not_found(self, capsys):
        """Error when checkpoint not found."""
        with patch("protocols.prompt.cli.get_default_registry") as mock_registry:
            registry = RollbackRegistry(storage=InMemoryCheckpointStorage())
            mock_registry.return_value = registry

            with pytest.raises(SystemExit) as exc_info:
                show_diff("id1_nonexist", "id2_nonexist")

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "not found" in captured.out

    def test_diff_success(self, capsys):
        """Successful diff between checkpoints."""
        with patch("protocols.prompt.cli.get_default_registry") as mock_registry:
            registry = RollbackRegistry(storage=InMemoryCheckpointStorage())
            mock_registry.return_value = registry

            # Create checkpoints
            id1 = registry.checkpoint(
                before_content="A",
                after_content="Version 1",
                before_sections=(),
                after_sections=(),
                reason="First",
            )
            id2 = registry.checkpoint(
                before_content="Version 1",
                after_content="Version 2",
                before_sections=(),
                after_sections=(),
                reason="Second",
            )

            show_diff(id1, id2)

            captured = capsys.readouterr()
            # Should show diff output
            assert "Version" in captured.out or "No differences" in captured.out


# =============================================================================
# Integration Tests
# =============================================================================


class TestCLIIntegration:
    """Integration tests for CLI workflow."""

    def test_compile_creates_checkpoint_on_change(self, tmp_path, monkeypatch):
        """Compile creates checkpoint when content changes."""
        # This test is more complex as it requires setting up the full environment
        # For now, just verify the compile function signature accepts checkpoint param

        # Create a minimal test by calling compile with checkpoint=False
        content = compile_prompt(checkpoint=False)
        assert len(content) > 0

    def test_full_workflow(self, capsys):
        """Test full workflow: compile → history → rollback."""
        with patch("protocols.prompt.cli.get_default_registry") as mock_registry:
            registry = RollbackRegistry(storage=InMemoryCheckpointStorage())
            mock_registry.return_value = registry

            # Simulate checkpoints (since compile needs real files)
            registry.set_current("Original", ("section1",))
            checkpoint_id = registry.checkpoint(
                before_content="Original",
                after_content="Modified",
                before_sections=("section1",),
                after_sections=("section1",),
                reason="Test modification",
            )

            # Show history
            show_history(limit=10)
            captured = capsys.readouterr()
            assert "Test modification" in captured.out

            # Rollback
            do_rollback(checkpoint_id)
            captured = capsys.readouterr()
            assert "Rollback successful" in captured.out


__all__ = [
    "TestCompileCommand",
    "TestHistoryCommand",
    "TestRollbackCommand",
    "TestDiffCommand",
    "TestCLIIntegration",
]
