"""
Tests for the Hollow Shell entry point.

Tests cover:
1. Help output (fast path)
2. Version output (fast path)
3. Command resolution (lazy loading)
4. Fuzzy matching for typos
5. Global flag parsing
"""

from pathlib import Path

import pytest

# =============================================================================
# Help & Version (Fast Path)
# =============================================================================


class TestHelpAndVersion:
    """Test fast path for --help and --version."""

    def test_help_no_args(self, capsys: pytest.CaptureFixture[str]) -> None:
        """kgents (no args) prints help."""
        from protocols.cli.hollow import main

        result = main([])
        out = capsys.readouterr().out

        assert result == 0
        # New help format: "Tasteful, curated, ethical agents"
        assert "kgents" in out
        assert "Tasteful" in out or "Crown Jewels" in out
        assert "brain" in out
        # Only commands with registered handlers are shown
        assert "town" in out or "witness" in out

    def test_help_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """kgents --help prints help."""
        from protocols.cli.hollow import main

        result = main(["--help"])
        out = capsys.readouterr().out

        assert result == 0
        assert "kgents" in out
        assert "brain" in out or "Crown Jewels" in out

    def test_help_short_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """kgents -h prints help."""
        from protocols.cli.hollow import main

        result = main(["-h"])
        out = capsys.readouterr().out

        assert result == 0
        assert "kgents" in out
        assert "brain" in out or "Crown Jewels" in out

    def test_version(self, capsys: pytest.CaptureFixture[str]) -> None:
        """kgents --version prints version."""
        from protocols.cli.hollow import main

        result = main(["--version"])
        out = capsys.readouterr().out

        assert result == 0
        assert "kgents 0.2.0" in out


# =============================================================================
# Command Resolution
# =============================================================================


class TestCommandResolution:
    """Test lazy command resolution."""

    def test_resolve_registered_command(self) -> None:
        """Registered commands resolve to handlers."""
        from protocols.cli.hollow import COMMAND_REGISTRY, resolve_command

        # All registered commands should be resolvable
        for cmd in [
            "self",
            "world",
            "concept",
            "void",
            "time",
            "do",
            "flow",
            "init",
            "wipe",
        ]:
            if cmd in COMMAND_REGISTRY:
                handler = resolve_command(cmd)
                assert handler is not None, f"Failed to resolve: {cmd}"

    def test_resolve_unknown_command(self) -> None:
        """Unknown commands return None."""
        from protocols.cli.hollow import resolve_command

        handler = resolve_command("nonexistent_command_xyz")
        assert handler is None

    def test_context_commands_resolve(self) -> None:
        """AGENTESE context commands resolve to handlers."""
        from protocols.cli.hollow import resolve_command

        # Context commands are the primary interface
        for cmd in ["self", "world", "concept", "void", "time"]:
            handler = resolve_command(cmd)
            assert handler is not None, f"Context command '{cmd}' should resolve"

    def test_deprecated_commands_removed(self) -> None:
        """Old deprecated commands no longer resolve."""
        from protocols.cli.hollow import resolve_command

        # These were deprecated and are now removed
        deprecated = ["soul", "status", "trace", "infra", "laws", "shadow"]
        for cmd in deprecated:
            handler = resolve_command(cmd)
            assert handler is None, f"Deprecated command '{cmd}' should not resolve"


# =============================================================================
# Fuzzy Matching
# =============================================================================


class TestFuzzyMatching:
    """Test typo suggestions."""

    def test_suggest_close_match(self) -> None:
        """Close typos get suggestions."""
        from protocols.cli.hollow import suggest_similar

        # "sel" should suggest "self"
        suggestions = suggest_similar("sel")
        assert "self" in suggestions

    def test_suggest_no_match(self) -> None:
        """Completely wrong input gets no suggestions."""
        from protocols.cli.hollow import suggest_similar

        suggestions = suggest_similar("xyzabc123")
        assert len(suggestions) == 0

    def test_print_suggestions(self, capsys: pytest.CaptureFixture[str]) -> None:
        """print_suggestions shows helpful output."""
        from protocols.cli.hollow import print_suggestions

        print_suggestions("selff")
        out = capsys.readouterr().out

        # Now uses sympathetic errors format
        assert "'selff' isn't a kgents command" in out
        assert "self" in out  # Suggestion should appear


# =============================================================================
# Global Flag Parsing
# =============================================================================


class TestFlagParsing:
    """Test lightweight flag parsing."""

    def test_parse_help_flag(self) -> None:
        """--help flag is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--help"])
        assert flags["help"] is True
        assert len(remaining) == 0

    def test_parse_format_equals(self) -> None:
        """--format=json is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--format=json", "self"])
        assert flags["format"] == "json"
        assert remaining == ["self"]

    def test_parse_format_space(self) -> None:
        """--format json is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--format", "json", "self"])
        assert flags["format"] == "json"
        assert remaining == ["self"]

    def test_parse_budget(self) -> None:
        """--budget=high is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--budget=high", "concept"])
        assert flags["budget"] == "high"
        assert remaining == ["concept"]

    def test_parse_explain(self) -> None:
        """--explain flag is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--explain", "self"])
        assert flags["explain"] is True
        assert remaining == ["self"]

    def test_parse_no_metrics(self) -> None:
        """--no-metrics flag is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--no-metrics", "world"])
        assert flags["no_metrics"] is True
        assert remaining == ["world"]

    def test_remaining_preserved(self) -> None:
        """Command and args are preserved in remaining."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["self", "status", "./path"])
        assert remaining == ["self", "status", "./path"]


# =============================================================================
# Unknown Command Handling
# =============================================================================


class TestUnknownCommand:
    """Test handling of unknown commands."""

    def test_unknown_command_exits_with_error(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Unknown command prints error and exits 1."""
        # Skip daemon check to test local command resolution
        monkeypatch.setenv("KGENTS_NO_DAEMON", "1")

        from protocols.cli.hollow import main

        result = main(["xyznonexistent"])
        out = capsys.readouterr().out

        assert result == 1
        # Now uses sympathetic errors format
        assert "'xyznonexistent' isn't a kgents command" in out
        assert "kgents --help" in out


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for full command flow."""

    def test_command_help_delegation(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Command-level --help delegates to handler."""
        from protocols.cli.hollow import main

        # Handler shows help and returns 0 (doesn't call sys.exit)
        result = main(["wipe", "--help"])
        out = capsys.readouterr().out

        assert result == 0
        assert "wipe" in out
        assert "help" in out.lower() or "USAGE" in out

    def test_full_command_execution(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Full command execution path works."""
        from protocols.cli.hollow import main

        # Use isolated XDG paths to avoid touching real DB
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

        # wipe should execute and return 0 (nothing to wipe)
        result = main(["wipe", "global"])
        assert result in (0, 1)  # 0 success (nothing to wipe), 1 if error
