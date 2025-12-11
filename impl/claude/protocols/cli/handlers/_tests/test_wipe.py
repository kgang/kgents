"""
Tests for wipe command.
"""

from unittest.mock import patch

from protocols.cli.handlers.wipe import (
    _collect_targets,
    _get_global_path,
    _get_size_str,
    cmd_wipe,
)


class TestGetSizeStr:
    """Tests for _get_size_str helper."""

    def test_nonexistent_path(self, tmp_path) -> None:
        """Should return '0 B' for nonexistent path."""
        assert _get_size_str(tmp_path / "nonexistent") == "0 B"

    def test_empty_file(self, tmp_path) -> None:
        """Should return '0.0 B' for empty file."""
        f = tmp_path / "empty"
        f.touch()
        assert _get_size_str(f) == "0.0 B"

    def test_small_file(self, tmp_path) -> None:
        """Should return bytes for small file."""
        f = tmp_path / "small"
        f.write_text("hello")
        assert "B" in _get_size_str(f)

    def test_directory(self, tmp_path) -> None:
        """Should sum files in directory."""
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")
        size_str = _get_size_str(tmp_path)
        assert "B" in size_str


class TestGetGlobalPath:
    """Tests for _get_global_path helper."""

    def test_default_path(self, monkeypatch) -> None:
        """Should use ~/.local/share/kgents by default."""
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        path = _get_global_path()
        assert path.name == "kgents"
        assert ".local/share" in str(path)

    def test_custom_xdg_data_home(self, monkeypatch, tmp_path) -> None:
        """Should respect XDG_DATA_HOME."""
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        path = _get_global_path()
        assert path == tmp_path / "kgents"


class TestCollectTargets:
    """Tests for _collect_targets helper."""

    def test_local_scope_no_db(self, tmp_path, monkeypatch) -> None:
        """Should return empty for local scope when no .kgents exists."""
        monkeypatch.chdir(tmp_path)
        targets = _collect_targets("local")
        assert targets == []

    def test_global_scope_no_db(self, tmp_path, monkeypatch) -> None:
        """Should return empty for global scope when no DB exists."""
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        targets = _collect_targets("global")
        assert targets == []

    def test_global_scope_with_db(self, tmp_path, monkeypatch) -> None:
        """Should return global target when DB exists."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        targets = _collect_targets("global")

        assert len(targets) == 1
        assert targets[0][0] == "global"
        assert targets[0][1] == data_dir

    def test_all_scope(self, tmp_path, monkeypatch) -> None:
        """Should return both targets for all scope."""
        # Set up global
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

        # Set up local
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".kgents").mkdir()
        (project_dir / ".kgents" / "cortex.db").touch()
        monkeypatch.chdir(project_dir)

        targets = _collect_targets("all")
        labels = [t[0] for t in targets]
        assert "global" in labels
        assert "local" in labels


class TestCmdWipe:
    """Tests for cmd_wipe command."""

    def test_help_flag(self, capsys) -> None:
        """Should print help and return 0."""
        result = cmd_wipe(["--help"])
        assert result == 0
        captured = capsys.readouterr()
        assert "kgents wipe" in captured.out
        assert "USAGE" in captured.out

    def test_missing_scope(self, capsys) -> None:
        """Should error when scope is missing."""
        result = cmd_wipe([])
        assert result == 1
        captured = capsys.readouterr()
        assert "Missing scope" in captured.out

    def test_invalid_scope(self, capsys) -> None:
        """Should error on invalid scope."""
        result = cmd_wipe(["invalid"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown scope" in captured.out

    def test_dry_run_global(self, tmp_path, monkeypatch, capsys) -> None:
        """Should show what would be deleted without deleting."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

        result = cmd_wipe(["global", "--dry-run"])
        assert result == 0
        assert data_dir.exists()  # Not deleted

        captured = capsys.readouterr()
        assert "dry-run" in captured.out
        assert "Would delete" in captured.out

    def test_force_skips_confirmation(self, tmp_path, monkeypatch, capsys) -> None:
        """Should skip confirmation with --force."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

        result = cmd_wipe(["global", "--force"])
        assert result == 0
        assert not data_dir.exists()  # Deleted

        captured = capsys.readouterr()
        assert "[wiped]" in captured.out

    def test_nothing_to_wipe(self, tmp_path, monkeypatch, capsys) -> None:
        """Should report nothing to wipe when DB doesn't exist."""
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "nonexistent"))

        result = cmd_wipe(["global"])
        assert result == 0

        captured = capsys.readouterr()
        assert "Nothing to wipe" in captured.out

    def test_confirmation_required_without_force(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        """Should require confirmation without --force."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

        # Simulate user typing 'no'
        with patch("builtins.input", return_value="no"):
            result = cmd_wipe(["global"])
            assert result == 1
            assert data_dir.exists()  # Not deleted

        captured = capsys.readouterr()
        assert "Aborted" in captured.out

    def test_confirmation_accepted(self, tmp_path, monkeypatch, capsys) -> None:
        """Should delete when user confirms with 'yes'."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

        # Simulate user typing 'yes'
        with patch("builtins.input", return_value="yes"):
            result = cmd_wipe(["global"])
            assert result == 0
            assert not data_dir.exists()  # Deleted

        captured = capsys.readouterr()
        assert "[wiped]" in captured.out
