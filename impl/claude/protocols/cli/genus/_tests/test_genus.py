"""
Tests for CLI Genus Layer (Phase 5).

Tests the Genera CLI handlers:
- G-gent (grammar): reify, parse, evolve, list, show, validate, infer
- J-gent (jit): compile, classify, defer, execute, stability, budget
- P-gent (parse): extract, repair, validate, stream, compose
- L-gent (library): catalog, discover, register, show, lineage, compose
- W-gent (witness): watch, fidelity, sample, serve, dashboard, log

NOTE: I-gent (garden) tests removed - see agents/i/screens/dashboard.py
"""

import json
import sys
from io import StringIO

# =============================================================================
# G-gent Tests (Grammar CLI)
# =============================================================================


class TestGGentCLI:
    """Tests for G-gent grammar CLI commands."""

    def test_grammar_help(self) -> None:
        """Test grammar help display."""
        from protocols.cli.genus.g_gent import cmd_grammar

        # Capture stdout
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_grammar(["--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "grammar" in output.lower()
        assert "reify" in output.lower()

    def test_grammar_unknown_subcommand(self) -> None:
        """Test unknown subcommand handling."""
        from protocols.cli.genus.g_gent import cmd_grammar

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_grammar(["nonexistent"])
        finally:
            sys.stdout = old_stdout

        # Prism uses argparse which returns exit code 2 for errors
        assert result == 2

    def test_grammar_reify_help(self) -> None:
        """Test reify subcommand help."""
        from protocols.cli.genus.g_gent import cmd_grammar

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_grammar(["reify", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "reify" in output.lower()
        assert "domain" in output.lower()

    def test_grammar_reify_no_domain(self) -> None:
        """Test reify without domain fails."""
        from protocols.cli.genus.g_gent import cmd_grammar

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_grammar(["reify"])
        finally:
            sys.stdout = old_stdout

        # Prism/argparse returns 2 for missing required arguments
        assert result == 2

    def test_grammar_parse_help(self) -> None:
        """Test parse subcommand help."""
        from protocols.cli.genus.g_gent import cmd_grammar

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_grammar(["parse", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "parse" in output.lower()

    def test_grammar_list_help(self) -> None:
        """Test list subcommand help."""
        from protocols.cli.genus.g_gent import cmd_grammar

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_grammar(["list", "--help"])
        finally:
            sys.stdout = old_stdout

        captured.getvalue()
        assert result == 0

    def test_grammar_validate_help(self) -> None:
        """Test validate subcommand help."""
        from protocols.cli.genus.g_gent import cmd_grammar

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_grammar(["validate", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "validate" in output.lower()

    def test_grammar_infer_help(self) -> None:
        """Test infer subcommand help."""
        from protocols.cli.genus.g_gent import cmd_grammar

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_grammar(["infer", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "infer" in output.lower()


# =============================================================================
# I-gent Tests (Garden CLI) - REMOVED
# =============================================================================
# NOTE: TestIGentCLI removed - kgents garden has been superseded by kgents dashboard
# See: agents/i/screens/dashboard.py


# =============================================================================
# J-gent Tests (JIT CLI)
# =============================================================================


class TestJGentCLI:
    """Tests for J-gent JIT CLI commands."""

    def test_jit_help(self) -> None:
        """Test jit help display."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "jit" in output.lower()
        assert "compile" in output.lower()
        assert "classify" in output.lower()

    def test_jit_unknown_subcommand(self) -> None:
        """Test unknown subcommand handling."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["nonexistent"])
        finally:
            sys.stdout = old_stdout

        # Prism uses argparse which returns exit code 2 for errors
        assert result == 2

    def test_jit_compile_help(self) -> None:
        """Test compile subcommand help."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["compile", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "compile" in output.lower()

    def test_jit_classify_help(self) -> None:
        """Test classify subcommand help."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["classify", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "classify" in output.lower()
        assert "DETERMINISTIC" in output

    def test_jit_defer_help(self) -> None:
        """Test defer subcommand help."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["defer", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "defer" in output.lower()

    def test_jit_execute_help(self) -> None:
        """Test execute subcommand help."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["execute", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "execute" in output.lower()

    def test_jit_stability_help(self) -> None:
        """Test stability subcommand help."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["stability", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "stability" in output.lower()

    def test_jit_budget_help(self) -> None:
        """Test budget subcommand help."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["budget", "--help"])
        finally:
            sys.stdout = old_stdout

        captured.getvalue()
        assert result == 0

    def test_jit_budget_display(self) -> None:
        """Test budget display."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["budget"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        # Prism outputs structured data with keys like "total", "remaining"
        assert "total" in output or "remaining" in output

    def test_jit_defer_creates_promise(self) -> None:
        """Test defer creates promise info."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["defer", "load config"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "DEFERRED" in output or "Promise" in output


# =============================================================================
# P-gent Tests (Parser CLI)
# =============================================================================


class TestPGentCLI:
    """Tests for P-gent parser CLI commands."""

    def test_parse_help(self) -> None:
        """Test parse help display."""
        from protocols.cli.genus.p_gent import cmd_parse

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_parse(["--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "parse" in output.lower()
        assert "extract" in output.lower()

    def test_parse_unknown_subcommand(self) -> None:
        """Test unknown subcommand handling."""
        from protocols.cli.genus.p_gent import cmd_parse

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_parse(["nonexistent"])
        finally:
            sys.stdout = old_stdout

        # Prism uses argparse which returns exit code 2 for errors
        assert result == 2

    def test_parse_extract_help(self) -> None:
        """Test extract subcommand help."""
        from protocols.cli.genus.p_gent import cmd_parse

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_parse(["extract", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "extract" in output.lower()

    def test_parse_repair_help(self) -> None:
        """Test repair subcommand help."""
        from protocols.cli.genus.p_gent import cmd_parse

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_parse(["repair", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "repair" in output.lower()

    def test_parse_validate_help(self) -> None:
        """Test validate subcommand help."""
        from protocols.cli.genus.p_gent import cmd_parse

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_parse(["validate", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "validate" in output.lower()

    def test_parse_stream_help(self) -> None:
        """Test stream subcommand help."""
        from protocols.cli.genus.p_gent import cmd_parse

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_parse(["stream", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "stream" in output.lower()

    def test_parse_compose_help(self) -> None:
        """Test compose subcommand help."""
        from protocols.cli.genus.p_gent import cmd_parse

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_parse(["compose", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "compose" in output.lower()

    def test_parse_compose_fallback(self) -> None:
        """Test compose fallback mode."""
        from protocols.cli.genus.p_gent import cmd_parse

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_parse(["compose", "fallback", "--parsers=anchor,stack"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "COMPOSITION" in output or "fallback" in output.lower()


# =============================================================================
# L-gent Tests (Library CLI)
# =============================================================================


class TestLGentCLI:
    """Tests for L-gent library CLI commands."""

    def test_library_help(self) -> None:
        """Test library help display."""
        from protocols.cli.genus.l_gent import cmd_library

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_library(["--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "library" in output.lower()
        assert "catalog" in output.lower()

    def test_library_unknown_subcommand(self) -> None:
        """Test unknown subcommand handling."""
        from protocols.cli.genus.l_gent import cmd_library

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_library(["nonexistent"])
        finally:
            sys.stdout = old_stdout

        # Prism uses argparse which returns exit code 2 for errors
        assert result == 2

    def test_library_catalog_help(self) -> None:
        """Test catalog subcommand help."""
        from protocols.cli.genus.l_gent import cmd_library

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_library(["catalog", "--help"])
        finally:
            sys.stdout = old_stdout

        captured.getvalue()
        assert result == 0

    def test_library_discover_help(self) -> None:
        """Test discover subcommand help."""
        from protocols.cli.genus.l_gent import cmd_library

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_library(["discover", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "discover" in output.lower()

    def test_library_register_help(self) -> None:
        """Test register subcommand help."""
        from protocols.cli.genus.l_gent import cmd_library

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_library(["register", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "register" in output.lower()

    def test_library_show_help(self) -> None:
        """Test show subcommand help."""
        from protocols.cli.genus.l_gent import cmd_library

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_library(["show", "--help"])
        finally:
            sys.stdout = old_stdout

        captured.getvalue()
        assert result == 0

    def test_library_lineage_help(self) -> None:
        """Test lineage subcommand help."""
        from protocols.cli.genus.l_gent import cmd_library

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_library(["lineage", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "lineage" in output.lower()

    def test_library_compose_help(self) -> None:
        """Test compose subcommand help."""
        from protocols.cli.genus.l_gent import cmd_library

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_library(["compose", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "compose" in output.lower()

    def test_library_types_help(self) -> None:
        """Test types subcommand help."""
        from protocols.cli.genus.l_gent import cmd_library

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_library(["types", "--help"])
        finally:
            sys.stdout = old_stdout

        captured.getvalue()
        assert result == 0

    def test_library_stats_help(self) -> None:
        """Test stats subcommand help."""
        from protocols.cli.genus.l_gent import cmd_library

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_library(["stats", "--help"])
        finally:
            sys.stdout = old_stdout

        captured.getvalue()
        assert result == 0


# =============================================================================
# W-gent Tests (Witness CLI)
# =============================================================================


class TestWGentCLI:
    """Tests for W-gent witness CLI commands."""

    def test_witness_help(self) -> None:
        """Test witness help display."""
        from protocols.cli.genus.w_gent import cmd_witness

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_witness(["--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "witness" in output.lower()
        assert "watch" in output.lower()

    def test_witness_unknown_subcommand(self) -> None:
        """Test unknown subcommand handling."""
        from protocols.cli.genus.w_gent import cmd_witness

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_witness(["nonexistent"])
        finally:
            sys.stdout = old_stdout

        # Prism uses argparse which returns exit code 2 for errors
        assert result == 2

    def test_witness_watch_help(self) -> None:
        """Test watch subcommand help."""
        from protocols.cli.genus.w_gent import cmd_witness

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_witness(["watch", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "watch" in output.lower()

    def test_witness_fidelity_help(self) -> None:
        """Test fidelity subcommand help."""
        from protocols.cli.genus.w_gent import cmd_witness

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_witness(["fidelity", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "fidelity" in output.lower()

    def test_witness_sample_help(self) -> None:
        """Test sample subcommand help."""
        from protocols.cli.genus.w_gent import cmd_witness

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_witness(["sample", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "sample" in output.lower()

    def test_witness_serve_help(self) -> None:
        """Test serve subcommand help."""
        from protocols.cli.genus.w_gent import cmd_witness

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_witness(["serve", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "serve" in output.lower()

    def test_witness_dashboard_help(self) -> None:
        """Test dashboard subcommand help."""
        from protocols.cli.genus.w_gent import cmd_witness

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_witness(["dashboard", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "dashboard" in output.lower()

    def test_witness_log_help(self) -> None:
        """Test log subcommand help."""
        from protocols.cli.genus.w_gent import cmd_witness

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_witness(["log", "--help"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        assert "log" in output.lower()

    def test_witness_log_display(self) -> None:
        """Test log display."""
        from protocols.cli.genus.w_gent import cmd_witness

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_witness(["log", "test-agent"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0
        # Prism outputs structured data with keys like "entries" and "target"
        assert "entries" in output or "target" in output


# =============================================================================
# Module Import Tests
# =============================================================================


class TestGenusModuleImports:
    """Test that genus module exports are correct."""

    def test_genus_init_imports(self) -> None:
        """Test genus __init__.py imports work."""
        from protocols.cli.genus import (
            # NOTE: cmd_garden removed - superseded by kgents dashboard
            cmd_grammar,
            cmd_jit,
            cmd_library,
            cmd_parse,
            cmd_witness,
        )

        assert callable(cmd_grammar)
        assert callable(cmd_jit)
        assert callable(cmd_parse)
        assert callable(cmd_library)
        assert callable(cmd_witness)

    def test_individual_module_imports(self) -> None:
        """Test individual module imports."""
        from protocols.cli.genus.g_gent import cmd_grammar

        # NOTE: i_gent removed - superseded by kgents dashboard
        from protocols.cli.genus.j_gent import cmd_jit
        from protocols.cli.genus.l_gent import cmd_library
        from protocols.cli.genus.p_gent import cmd_parse
        from protocols.cli.genus.w_gent import cmd_witness

        assert callable(cmd_grammar)
        assert callable(cmd_jit)
        assert callable(cmd_parse)
        assert callable(cmd_library)
        assert callable(cmd_witness)


# =============================================================================
# Integration Tests
# =============================================================================


class TestGenusIntegration:
    """Integration tests for genus layer."""

    def test_all_genera_have_help(self) -> None:
        """All genera should have --help support."""
        from protocols.cli.genus import (
            # NOTE: cmd_garden removed - superseded by kgents dashboard
            cmd_grammar,
            cmd_jit,
            cmd_library,
            cmd_parse,
            cmd_witness,
        )

        for cmd in [
            cmd_grammar,
            cmd_jit,
            cmd_parse,
            cmd_library,
            cmd_witness,
        ]:
            captured = StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured

            try:
                result = cmd(["--help"])
            finally:
                sys.stdout = old_stdout

            assert result == 0, f"{cmd.__name__} --help failed"
            assert len(captured.getvalue()) > 100, f"{cmd.__name__} help too short"

    def test_all_genera_handle_unknown(self) -> None:
        """All genera should handle unknown subcommands gracefully."""
        from protocols.cli.genus import (
            # NOTE: cmd_garden removed - superseded by kgents dashboard
            cmd_grammar,
            cmd_jit,
            cmd_library,
            cmd_parse,
            cmd_witness,
        )

        for cmd in [
            cmd_grammar,
            cmd_jit,
            cmd_parse,
            cmd_library,
            cmd_witness,
        ]:
            captured = StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured

            try:
                result = cmd(["definitely_not_a_command_xyz"])
            finally:
                sys.stdout = old_stdout

            # Prism uses argparse which returns exit code 2 for errors
            assert result == 2, f"{cmd.__name__} should fail on unknown subcommand"

    def test_genus_json_output_format(self) -> None:
        """Test that JSON format flag works."""
        from protocols.cli.genus.j_gent import cmd_jit

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = cmd_jit(["budget", "--format=json"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert result == 0

        # Should be valid JSON
        data = json.loads(output)
        assert "total" in data
        assert "remaining" in data
