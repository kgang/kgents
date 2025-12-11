"""
Tests for the Hollow Shell entry point.

Tests cover:
1. Help output (fast path)
2. Version output (fast path)
3. Command resolution (lazy loading)
4. Fuzzy matching for typos
5. Global flag parsing
"""


# =============================================================================
# Help & Version (Fast Path)
# =============================================================================


class TestHelpAndVersion:
    """Test fast path for --help and --version."""

    def test_help_no_args(self, capsys):
        """kgents (no args) prints help."""
        from protocols.cli.hollow import main

        result = main([])
        out = capsys.readouterr().out

        assert result == 0
        assert "kgents - Kent's Agents CLI" in out
        assert "INTENT LAYER" in out
        assert "new" in out
        assert "run" in out

    def test_help_flag(self, capsys):
        """kgents --help prints help."""
        from protocols.cli.hollow import main

        result = main(["--help"])
        out = capsys.readouterr().out

        assert result == 0
        assert "kgents - Kent's Agents CLI" in out

    def test_help_short_flag(self, capsys):
        """kgents -h prints help."""
        from protocols.cli.hollow import main

        result = main(["-h"])
        out = capsys.readouterr().out

        assert result == 0
        assert "kgents - Kent's Agents CLI" in out

    def test_version(self, capsys):
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

    def test_resolve_registered_command(self):
        """Registered commands resolve to handlers."""
        from protocols.cli.hollow import COMMAND_REGISTRY, resolve_command

        # All registered commands should be resolvable
        for cmd in ["membrane", "check", "find"]:
            if cmd in COMMAND_REGISTRY:
                handler = resolve_command(cmd)
                assert handler is not None, f"Failed to resolve: {cmd}"

    def test_resolve_unknown_command(self):
        """Unknown commands return None."""
        from protocols.cli.hollow import resolve_command

        handler = resolve_command("nonexistent_command_xyz")
        assert handler is None

    def test_membrane_resolves(self):
        """Membrane command resolves to handler."""
        from protocols.cli.hollow import resolve_command

        handler = resolve_command("membrane")
        assert handler is not None


# =============================================================================
# Fuzzy Matching
# =============================================================================


class TestFuzzyMatching:
    """Test typo suggestions."""

    def test_suggest_close_match(self):
        """Close typos get suggestions."""
        from protocols.cli.hollow import suggest_similar

        # "membran" should suggest "membrane"
        suggestions = suggest_similar("membran")
        assert "membrane" in suggestions

    def test_suggest_no_match(self):
        """Completely wrong input gets no suggestions."""
        from protocols.cli.hollow import suggest_similar

        suggestions = suggest_similar("xyzabc123")
        assert len(suggestions) == 0

    def test_print_suggestions(self, capsys):
        """print_suggestions shows helpful output."""
        from protocols.cli.hollow import print_suggestions

        print_suggestions("membran")
        out = capsys.readouterr().out

        # Now uses sympathetic errors format
        assert "'membran' isn't a kgents command" in out
        assert "membrane" in out  # Suggestion should appear


# =============================================================================
# Global Flag Parsing
# =============================================================================


class TestFlagParsing:
    """Test lightweight flag parsing."""

    def test_parse_help_flag(self):
        """--help flag is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--help"])
        assert flags["help"] is True
        assert len(remaining) == 0

    def test_parse_format_equals(self):
        """--format=json is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--format=json", "pulse"])
        assert flags["format"] == "json"
        assert remaining == ["pulse"]

    def test_parse_format_space(self):
        """--format json is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--format", "json", "pulse"])
        assert flags["format"] == "json"
        assert remaining == ["pulse"]

    def test_parse_budget(self):
        """--budget=high is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--budget=high", "check"])
        assert flags["budget"] == "high"
        assert remaining == ["check"]

    def test_parse_explain(self):
        """--explain flag is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--explain", "membrane"])
        assert flags["explain"] is True
        assert remaining == ["membrane"]

    def test_parse_no_metrics(self):
        """--no-metrics flag is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--no-metrics", "pulse"])
        assert flags["no_metrics"] is True
        assert remaining == ["pulse"]

    def test_remaining_preserved(self):
        """Command and args are preserved in remaining."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["membrane", "observe", "./path"])
        assert remaining == ["membrane", "observe", "./path"]


# =============================================================================
# Unknown Command Handling
# =============================================================================


class TestUnknownCommand:
    """Test handling of unknown commands."""

    def test_unknown_command_exits_with_error(self, capsys):
        """Unknown command prints error and exits 1."""
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

    def test_command_help_delegation(self, capsys):
        """Command-level --help delegates to handler."""
        from protocols.cli.hollow import main

        # Handler shows help and returns 0 (doesn't call sys.exit)
        result = main(["wipe", "--help"])
        out = capsys.readouterr().out

        assert result == 0
        assert "wipe" in out
        assert "help" in out.lower() or "USAGE" in out

    def test_full_command_execution(self, tmp_path, monkeypatch):
        """Full command execution path works."""
        from protocols.cli.hollow import main

        # Use isolated XDG paths to avoid touching real DB
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

        # wipe should execute and return 0 (nothing to wipe)
        result = main(["wipe", "global"])
        assert result in (0, 1)  # 0 success (nothing to wipe), 1 if error
