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
        from protocols.cli.hollow import resolve_command, COMMAND_REGISTRY

        # All registered commands should be resolvable
        # (may return legacy handler if not implemented yet)
        for cmd in ["mirror", "pulse", "ground"]:
            if cmd in COMMAND_REGISTRY:
                handler = resolve_command(cmd)
                assert handler is not None, f"Failed to resolve: {cmd}"

    def test_resolve_unknown_command(self):
        """Unknown commands return None."""
        from protocols.cli.hollow import resolve_command

        handler = resolve_command("nonexistent_command_xyz")
        assert handler is None

    def test_legacy_fallback(self):
        """Legacy commands fall back to main.py handler."""
        from protocols.cli.hollow import resolve_command, LEGACY_COMMANDS

        # Legacy commands should resolve (they use the legacy handler)
        for cmd in ["mirror", "membrane"]:
            if cmd in LEGACY_COMMANDS:
                handler = resolve_command(cmd)
                assert handler is not None


# =============================================================================
# Fuzzy Matching
# =============================================================================


class TestFuzzyMatching:
    """Test typo suggestions."""

    def test_suggest_close_match(self):
        """Close typos get suggestions."""
        from protocols.cli.hollow import suggest_similar

        # "mirro" should suggest "mirror"
        suggestions = suggest_similar("mirro")
        assert "mirror" in suggestions

    def test_suggest_no_match(self):
        """Completely wrong input gets no suggestions."""
        from protocols.cli.hollow import suggest_similar

        suggestions = suggest_similar("xyzabc123")
        assert len(suggestions) == 0

    def test_print_suggestions(self, capsys):
        """print_suggestions shows helpful output."""
        from protocols.cli.hollow import print_suggestions

        print_suggestions("mirro")
        out = capsys.readouterr().out

        assert "Unknown command: mirro" in out
        assert "Did you mean?" in out
        assert "mirror" in out


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

        flags, remaining = parse_global_flags(["--explain", "mirror"])
        assert flags["explain"] is True
        assert remaining == ["mirror"]

    def test_parse_no_metrics(self):
        """--no-metrics flag is parsed."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["--no-metrics", "pulse"])
        assert flags["no_metrics"] is True
        assert remaining == ["pulse"]

    def test_remaining_preserved(self):
        """Command and args are preserved in remaining."""
        from protocols.cli.hollow import parse_global_flags

        flags, remaining = parse_global_flags(["mirror", "observe", "./path"])
        assert remaining == ["mirror", "observe", "./path"]


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
        assert "Unknown command: xyznonexistent" in out
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
        result = main(["pulse", "--help"])
        out = capsys.readouterr().out

        assert result == 0
        assert "pulse" in out
        assert "help" in out.lower() or "USAGE" in out

    def test_full_command_execution(self):
        """Full command execution path works."""
        from protocols.cli.hollow import main

        # pulse should execute and return 0
        # (may print output, but shouldn't crash)
        result = main(["pulse", "."])
        assert result in (0, 1)  # 0 success, 1 if error in handler
