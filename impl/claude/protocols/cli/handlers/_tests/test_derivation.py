"""
Tests for the derivation CLI handler.

Verifies:
- Subcommand routing (show, ancestors, dependents, tree, principles, why, propagate)
- Agent name normalization (brain -> Brain, k-gent -> K-gent)
- AGENTESE path mapping
- JSON output mode
- Help text

Teaching:
    gotcha: Each test resets the derivation registry to avoid cross-test pollution.
            Always reset in fixtures, not at module level.
            (Evidence: test_derivation_handler.py::test_fixture_isolation)
"""

from __future__ import annotations

import json
import sys
from io import StringIO

import pytest

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset derivation registry before each test."""
    from protocols.derivation import reset_registry as _reset

    _reset()
    yield
    _reset()


@pytest.fixture
def registry_with_derived():
    """Registry with some derived agents."""
    from protocols.derivation import (
        DerivationTier,
        EvidenceType,
        PrincipleDraw,
        get_registry,
    )

    registry = get_registry()

    # Register Flux as a FUNCTOR tier agent
    registry.register(
        agent_name="Flux",
        derives_from=("Fix", "Compose"),
        principle_draws=(
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.95,
                evidence_type=EvidenceType.CATEGORICAL,
                evidence_sources=("flux-associativity-test",),
            ),
            PrincipleDraw(
                principle="Heterarchical",
                draw_strength=0.85,
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=("flux-dual-mode-ashc-runs",),
            ),
        ),
        tier=DerivationTier.FUNCTOR,
    )

    # Update with evidence
    registry.update_evidence("Flux", ashc_score=0.88, usage_count=5000)

    return registry


# =============================================================================
# Agent Name Normalization
# =============================================================================


class TestAgentNameNormalization:
    """Test agent name normalization."""

    def test_lowercase_normalized(self):
        """Test that lowercase names are normalized to Titlecase."""
        from protocols.cli.handlers.derivation import normalize_agent_name

        assert normalize_agent_name("brain") == "Brain"
        assert normalize_agent_name("flux") == "Flux"
        assert normalize_agent_name("witness") == "Witness"

    def test_uppercase_normalized(self):
        """Test that uppercase names are normalized."""
        from protocols.cli.handlers.derivation import normalize_agent_name

        assert normalize_agent_name("BRAIN") == "Brain"
        assert normalize_agent_name("FLUX") == "Flux"

    def test_mixed_case_normalized(self):
        """Test that mixed case names are normalized."""
        from protocols.cli.handlers.derivation import normalize_agent_name

        assert normalize_agent_name("BrAiN") == "Brain"

    def test_hyphenated_names_preserved(self):
        """Test that hyphenated names like K-gent are handled."""
        from protocols.cli.handlers.derivation import normalize_agent_name

        assert normalize_agent_name("k-gent") == "K-Gent"
        assert normalize_agent_name("m-gent") == "M-Gent"

    def test_none_returns_none(self):
        """Test that None input returns None."""
        from protocols.cli.handlers.derivation import normalize_agent_name

        assert normalize_agent_name(None) is None

    def test_empty_returns_none(self):
        """Test that empty string returns None."""
        from protocols.cli.handlers.derivation import normalize_agent_name

        assert normalize_agent_name("") is None


# =============================================================================
# Subcommand Routing
# =============================================================================


class TestSubcommandRouting:
    """Test subcommand to AGENTESE path routing."""

    def test_show_routes_to_query(self):
        """Test 'show' routes to concept.derivation.query."""
        from protocols.cli.handlers.derivation import (
            DERIVATION_SUBCOMMAND_TO_PATH,
        )

        assert DERIVATION_SUBCOMMAND_TO_PATH["show"] == "concept.derivation.query"

    def test_ancestors_routes_to_navigate(self):
        """Test 'ancestors' routes to concept.derivation.navigate."""
        from protocols.cli.handlers.derivation import (
            DERIVATION_SUBCOMMAND_TO_PATH,
        )

        assert DERIVATION_SUBCOMMAND_TO_PATH["ancestors"] == "concept.derivation.navigate"

    def test_dependents_routes_to_navigate(self):
        """Test 'dependents' routes to concept.derivation.navigate."""
        from protocols.cli.handlers.derivation import (
            DERIVATION_SUBCOMMAND_TO_PATH,
        )

        assert DERIVATION_SUBCOMMAND_TO_PATH["dependents"] == "concept.derivation.navigate"

    def test_tree_routes_to_dag(self):
        """Test 'tree' routes to concept.derivation.dag."""
        from protocols.cli.handlers.derivation import (
            DERIVATION_SUBCOMMAND_TO_PATH,
        )

        assert DERIVATION_SUBCOMMAND_TO_PATH["tree"] == "concept.derivation.dag"

    def test_principles_routes_to_principles(self):
        """Test 'principles' routes to concept.derivation.principles."""
        from protocols.cli.handlers.derivation import (
            DERIVATION_SUBCOMMAND_TO_PATH,
        )

        assert DERIVATION_SUBCOMMAND_TO_PATH["principles"] == "concept.derivation.principles"

    def test_why_routes_to_confidence(self):
        """Test 'why' routes to concept.derivation.confidence."""
        from protocols.cli.handlers.derivation import (
            DERIVATION_SUBCOMMAND_TO_PATH,
        )

        assert DERIVATION_SUBCOMMAND_TO_PATH["why"] == "concept.derivation.confidence"

    def test_edges_routes_to_edges(self):
        """Test 'edges' routes to concept.derivation.edges (Phase 3D)."""
        from protocols.cli.handlers.derivation import (
            DERIVATION_SUBCOMMAND_TO_PATH,
        )

        assert DERIVATION_SUBCOMMAND_TO_PATH["edges"] == "concept.derivation.edges"


# =============================================================================
# Argument Parsing
# =============================================================================


class TestArgumentParsing:
    """Test argument parsing helpers."""

    def test_parse_subcommand_extracts_first_arg(self):
        """Test subcommand extraction."""
        from protocols.cli.handlers.derivation import _parse_subcommand

        assert _parse_subcommand(["show", "Brain"]) == "show"
        assert _parse_subcommand(["tree"]) == "tree"

    def test_parse_subcommand_skips_flags(self):
        """Test subcommand skips flags."""
        from protocols.cli.handlers.derivation import _parse_subcommand

        assert _parse_subcommand(["--json", "show", "Brain"]) == "show"
        assert _parse_subcommand(["--help"]) == "status"

    def test_parse_subcommand_defaults_to_status(self):
        """Test subcommand defaults when no args."""
        from protocols.cli.handlers.derivation import _parse_subcommand

        assert _parse_subcommand([]) == "status"
        assert _parse_subcommand(["--json"]) == "status"

    def test_extract_agent_name(self):
        """Test agent name extraction."""
        from protocols.cli.handlers.derivation import _extract_agent_name

        assert _extract_agent_name(["show", "Brain"], "show") == "Brain"
        assert _extract_agent_name(["show", "flux"], "show") == "flux"

    def test_extract_agent_name_skips_flags(self):
        """Test agent name extraction skips flags."""
        from protocols.cli.handlers.derivation import _extract_agent_name

        assert _extract_agent_name(["show", "--json", "Brain"], "show") == "Brain"

    def test_build_kwargs_includes_agent_name(self):
        """Test kwargs building includes normalized agent name."""
        from protocols.cli.handlers.derivation import _build_kwargs

        kwargs = _build_kwargs(["show", "brain"], "show")
        assert kwargs.get("agent_name") == "Brain"

    def test_build_kwargs_ancestors_edge(self):
        """Test ancestors sets edge=derives_from."""
        from protocols.cli.handlers.derivation import _build_kwargs

        kwargs = _build_kwargs(["ancestors", "Flux"], "ancestors")
        assert kwargs.get("edge") == "derives_from"

    def test_build_kwargs_dependents_edge(self):
        """Test dependents sets edge=dependents."""
        from protocols.cli.handlers.derivation import _build_kwargs

        kwargs = _build_kwargs(["dependents", "Id"], "dependents")
        assert kwargs.get("edge") == "dependents"

    def test_build_kwargs_with_tier_flag(self):
        """Test tier flag parsing."""
        from protocols.cli.handlers.derivation import _build_kwargs

        kwargs = _build_kwargs(["tree", "--tier", "jewel"], "tree")
        assert kwargs.get("tier") == "jewel"

    def test_build_kwargs_with_focus_flag(self):
        """Test focus flag parsing."""
        from protocols.cli.handlers.derivation import _build_kwargs

        kwargs = _build_kwargs(["tree", "--focus", "brain"], "tree")
        assert kwargs.get("focus") == "Brain"

    def test_build_kwargs_with_source_flag(self):
        """Test --source flag parsing."""
        from protocols.cli.handlers.derivation import _build_kwargs

        kwargs = _build_kwargs(["edges", "--source", "fix"], "edges")
        assert kwargs.get("source") == "Fix"

    def test_build_kwargs_with_target_flag(self):
        """Test --target flag parsing (Phase 3D)."""
        from protocols.cli.handlers.derivation import _build_kwargs

        kwargs = _build_kwargs(["edges", "--target", "brain"], "edges")
        assert kwargs.get("target") == "Brain"

    def test_build_kwargs_with_source_equals_syntax(self):
        """Test --source=X syntax parsing."""
        from protocols.cli.handlers.derivation import _build_kwargs

        kwargs = _build_kwargs(["edges", "--source=fix"], "edges")
        assert kwargs.get("source") == "Fix"

    def test_build_kwargs_with_target_equals_syntax(self):
        """Test --target=X syntax parsing (Phase 3D)."""
        from protocols.cli.handlers.derivation import _build_kwargs

        kwargs = _build_kwargs(["edges", "--target=brain"], "edges")
        assert kwargs.get("target") == "Brain"

    def test_build_kwargs_edges_with_both_source_and_target(self):
        """Test edges with both --source and --target (Phase 3D)."""
        from protocols.cli.handlers.derivation import _build_kwargs

        kwargs = _build_kwargs(["edges", "--source=fix", "--target=brain"], "edges")
        assert kwargs.get("source") == "Fix"
        assert kwargs.get("target") == "Brain"


# =============================================================================
# Help and Basic Commands
# =============================================================================


class TestHelpAndBasicCommands:
    """Test help and basic commands."""

    def test_help_flag(self, capsys):
        """Test that --help shows help text."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["--help"])
        assert result == 0

        captured = capsys.readouterr()
        # Help shows either dynamic (concept.derivation) or static (kg derivation) format
        assert "derivation" in captured.out.lower()
        # Shows aspect commands
        assert "query" in captured.out or "show" in captured.out
        # Shows AGENTESE context
        assert "concept.derivation" in captured.out or "AGENTESE" in captured.out

    def test_h_flag(self, capsys):
        """Test that -h shows help text."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["-h"])
        assert result == 0

        captured = capsys.readouterr()
        # Help shows derivation info in some format
        assert "derivation" in captured.out.lower() or "Derivation" in captured.out


# =============================================================================
# Command Execution (Integration with AGENTESE)
# =============================================================================


class TestCommandExecution:
    """Test command execution through AGENTESE."""

    def test_no_args_shows_manifest(self, capsys):
        """Test that no args shows framework status."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation([])
        assert result == 0

        captured = capsys.readouterr()
        # Should show bootstrap or derivation info
        assert "bootstrap" in captured.out.lower() or "derivation" in captured.out.lower()

    def test_show_bootstrap_agent(self, capsys):
        """Test showing a bootstrap agent."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["show", "Id"])
        assert result == 0

        captured = capsys.readouterr()
        assert "Id" in captured.out
        assert "bootstrap" in captured.out.lower()

    def test_show_derived_agent(self, capsys, registry_with_derived):
        """Test showing a derived agent."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["show", "Flux"])
        assert result == 0

        captured = capsys.readouterr()
        assert "Flux" in captured.out
        assert "functor" in captured.out.lower()

    def test_tree_command(self, capsys):
        """Test tree command shows DAG."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["tree"])
        assert result == 0

        captured = capsys.readouterr()
        # Should show nodes/edges or tier information
        assert "node" in captured.out.lower() or "tier" in captured.out.lower()

    def test_ancestors_command(self, capsys, registry_with_derived):
        """Test ancestors command."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["ancestors", "Flux"])
        assert result == 0

        captured = capsys.readouterr()
        # Should show Fix and Compose as ancestors
        assert "Fix" in captured.out or "Compose" in captured.out

    def test_dependents_command(self, capsys):
        """Test dependents command."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["dependents", "Compose"])
        assert result == 0

        captured = capsys.readouterr()
        # Should show some output about dependents
        assert "Compose" in captured.out or "dependents" in captured.out.lower()

    def test_principles_command(self, capsys, registry_with_derived):
        """Test principles command."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["principles", "Flux"])
        assert result == 0

        captured = capsys.readouterr()
        # Should show principle breakdown
        assert "Principle" in captured.out or "Composable" in captured.out

    def test_why_command(self, capsys, registry_with_derived):
        """Test why/confidence command."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["why", "Flux"])
        assert result == 0

        captured = capsys.readouterr()
        # Should show confidence breakdown
        assert "confidence" in captured.out.lower() or "inherited" in captured.out.lower()


# =============================================================================
# JSON Output
# =============================================================================


class TestJSONOutput:
    """Test JSON output mode."""

    def test_json_flag_valid_output(self, capsys):
        """Test that --json produces valid JSON."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["show", "Id", "--json"])
        assert result == 0

        captured = capsys.readouterr()
        # Should be valid JSON
        data = json.loads(captured.out)
        assert isinstance(data, dict)

    def test_json_tree_output(self, capsys, registry_with_derived):
        """Test JSON output for tree command."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["tree", "--json"])
        assert result == 0

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, dict)


# =============================================================================
# Registry in Hollow Shell
# =============================================================================


class TestHollowShellRegistration:
    """Test command registration in hollow.py."""

    def test_derivation_registered(self):
        """Test that 'derivation' is in command registry."""
        from protocols.cli.hollow import COMMAND_REGISTRY

        assert "derivation" in COMMAND_REGISTRY
        assert "cmd_derivation" in COMMAND_REGISTRY["derivation"]

    def test_derive_alias_registered(self):
        """Test that 'derive' alias is registered."""
        from protocols.cli.hollow import COMMAND_REGISTRY

        assert "derive" in COMMAND_REGISTRY
        assert "cmd_derivation" in COMMAND_REGISTRY["derive"]

    def test_command_resolves(self):
        """Test that command resolves to callable."""
        from protocols.cli.hollow import resolve_command

        handler = resolve_command("derivation")
        assert handler is not None
        assert callable(handler)


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases."""

    def test_nonexistent_agent_handled(self, capsys):
        """Test handling of nonexistent agent."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation(["show", "NonexistentAgent"])
        # Should complete without error (may show "not found" message)
        assert result in (0, 1)

        captured = capsys.readouterr()
        # Should have some output (error or usage)
        assert len(captured.out) > 0 or len(captured.err) > 0

    def test_case_insensitive_agent_lookup(self, capsys, registry_with_derived):
        """Test case insensitive agent lookup."""
        from protocols.cli.handlers.derivation import cmd_derivation

        # These should all work
        for name in ["flux", "FLUX", "Flux", "FLux"]:
            result = cmd_derivation(["show", name])
            assert result == 0

    def test_empty_subcommand_list(self, capsys):
        """Test empty subcommand list defaults to manifest."""
        from protocols.cli.handlers.derivation import cmd_derivation

        result = cmd_derivation([])
        assert result == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests verifying full CLI -> AGENTESE flow."""

    def test_full_workflow(self, capsys, registry_with_derived):
        """Test full workflow through CLI."""
        from protocols.cli.handlers.derivation import cmd_derivation

        # 1. Show status
        assert cmd_derivation([]) == 0

        # 2. Query specific agent
        assert cmd_derivation(["show", "Flux"]) == 0

        # 3. Check ancestors
        assert cmd_derivation(["ancestors", "Flux"]) == 0

        # 4. Check principles
        assert cmd_derivation(["principles", "Flux"]) == 0

        # 5. Explain confidence
        assert cmd_derivation(["why", "Flux"]) == 0

    def test_routes_to_agentese(self):
        """Test that handler routes to AGENTESE (not direct implementation)."""
        from protocols.cli.handlers.derivation import DERIVATION_SUBCOMMAND_TO_PATH

        # All paths should start with concept.derivation
        for path in DERIVATION_SUBCOMMAND_TO_PATH.values():
            assert path.startswith("concept.derivation.")
