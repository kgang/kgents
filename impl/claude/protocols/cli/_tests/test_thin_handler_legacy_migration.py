"""
Tests for thin handler legacy migration to AGENTESE router.

Verifies that all thin handler commands (brain, witness, coffee, docs, graph)
properly expand to AGENTESE paths via the legacy command system.

This enables:
1. Backward compatibility - existing commands continue to work
2. Unified routing - all commands go through AGENTESE router
3. Better tracing - commands can be traced through protocol layer
"""

from __future__ import annotations

import pytest


class TestBrainLegacyMappings:
    """Test brain command legacy mappings to self.memory.*"""

    def test_brain_default(self) -> None:
        """brain → self.memory.manifest"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["brain"])
        assert path == "self.memory.manifest"
        assert remaining == []

    def test_brain_capture(self) -> None:
        """brain capture → self.memory.capture"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["brain", "capture"])
        assert path == "self.memory.capture"
        assert remaining == []

    def test_brain_search(self) -> None:
        """brain search → self.memory.recall"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["brain", "search"])
        assert path == "self.memory.recall"
        assert remaining == []

    def test_brain_ghost(self) -> None:
        """brain ghost → self.memory.ghost.surface"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["brain", "ghost"])
        assert path == "self.memory.ghost.surface"
        assert remaining == []

    def test_brain_with_remaining_args(self) -> None:
        """brain capture --json → self.memory.capture + ['--json']"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["brain", "capture", "--json", "test"])
        assert path == "self.memory.capture"
        assert remaining == ["--json", "test"]


class TestWitnessLegacyMappings:
    """Test witness command legacy mappings to self.witness.*"""

    def test_witness_default(self) -> None:
        """witness → self.witness.manifest"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["witness"])
        assert path == "self.witness.manifest"
        assert remaining == []

    def test_witness_mark(self) -> None:
        """witness mark → self.witness.mark"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["witness", "mark"])
        assert path == "self.witness.mark"
        assert remaining == []

    def test_witness_show(self) -> None:
        """witness show → self.witness.show"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["witness", "show"])
        assert path == "self.witness.show"
        assert remaining == []

    def test_witness_recent_alias(self) -> None:
        """witness recent → self.witness.show (alias)"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["witness", "recent"])
        assert path == "self.witness.show"
        assert remaining == []

    def test_witness_crystallize(self) -> None:
        """witness crystallize → self.witness.crystallize"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["witness", "crystallize"])
        assert path == "self.witness.crystallize"
        assert remaining == []


class TestCoffeeLegacyMappings:
    """Test coffee command legacy mappings to time.coffee.*"""

    def test_coffee_default(self) -> None:
        """coffee → time.coffee.manifest"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["coffee"])
        assert path == "time.coffee.manifest"
        assert remaining == []

    def test_coffee_garden(self) -> None:
        """coffee garden → time.coffee.garden"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["coffee", "garden"])
        assert path == "time.coffee.garden"
        assert remaining == []

    def test_coffee_weather(self) -> None:
        """coffee weather → time.coffee.weather"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["coffee", "weather"])
        assert path == "time.coffee.weather"
        assert remaining == []

    def test_coffee_menu(self) -> None:
        """coffee menu → time.coffee.menu"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["coffee", "menu"])
        assert path == "time.coffee.menu"
        assert remaining == []


class TestDocsLegacyMappings:
    """Test docs command legacy mappings to concept.docs.*"""

    def test_docs_default(self) -> None:
        """docs → concept.docs.manifest"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["docs"])
        assert path == "concept.docs.manifest"
        assert remaining == []

    def test_docs_generate(self) -> None:
        """docs generate → concept.docs.generate"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["docs", "generate"])
        assert path == "concept.docs.generate"
        assert remaining == []

    def test_docs_teaching(self) -> None:
        """docs teaching → concept.docs.teaching"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["docs", "teaching"])
        assert path == "concept.docs.teaching"
        assert remaining == []

    def test_docs_verify(self) -> None:
        """docs verify → concept.docs.verify"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["docs", "verify"])
        assert path == "concept.docs.verify"
        assert remaining == []


class TestGraphThinHandler:
    """
    Test graph command routing.

    Graph commands are NOT legacy - they route through thin handler (graph_thin.py)
    which properly bootstraps service providers before AGENTESE invocation.
    See legacy.py lines 76-80 for explanation of why graph was removed from legacy.

    These tests verify graph does NOT expand as legacy (it's a thin handler).
    """

    def test_graph_is_not_legacy(self) -> None:
        """graph is NOT a legacy command - it uses thin handler."""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["graph"])
        # Should NOT expand - graph is handled by thin handler, not legacy
        assert path == "graph"
        assert remaining == []

    def test_graph_subcommands_not_legacy(self) -> None:
        """graph subcommands are NOT legacy - thin handler handles them."""
        from protocols.cli.legacy import expand_legacy

        for subcommand in ["manifest", "neighbors", "evidence", "trace", "search"]:
            path, remaining = expand_legacy(["graph", subcommand])
            # Should NOT expand - thin handler routes these
            assert path == "graph"
            assert remaining == [subcommand]


class TestRouterIntegration:
    """Test that router correctly classifies thin handler legacy commands."""

    def test_brain_routes_as_legacy(self) -> None:
        """Router should classify brain commands as LEGACY."""
        from protocols.cli.agentese_router import classify_input

        result = classify_input(["brain", "capture"])
        assert str(result.input_type) == "legacy"
        assert result.agentese_path == "self.memory.capture"

    def test_witness_routes_as_legacy(self) -> None:
        """Router should classify witness commands as LEGACY."""
        from protocols.cli.agentese_router import classify_input

        result = classify_input(["witness", "mark"])
        assert str(result.input_type) == "legacy"
        assert result.agentese_path == "self.witness.mark"

    def test_coffee_routes_as_legacy(self) -> None:
        """Router should classify coffee commands as LEGACY."""
        from protocols.cli.agentese_router import classify_input

        result = classify_input(["coffee", "garden"])
        assert str(result.input_type) == "legacy"
        assert result.agentese_path == "time.coffee.garden"

    def test_docs_routes_as_legacy(self) -> None:
        """Router should classify docs commands as LEGACY."""
        from protocols.cli.agentese_router import classify_input

        result = classify_input(["docs", "generate"])
        assert str(result.input_type) == "legacy"
        assert result.agentese_path == "concept.docs.generate"

    def test_graph_not_legacy(self) -> None:
        """Router should NOT classify graph as LEGACY - it's a thin handler."""
        from protocols.cli.agentese_router import classify_input

        result = classify_input(["graph", "neighbors"])
        # Graph uses thin handler (COMMAND_REGISTRY), not legacy expansion
        # Router classifies as UNKNOWN because it doesn't know about thin handlers
        # The hollow.py COMMAND_REGISTRY handles "graph" before router is called
        assert str(result.input_type) != "legacy"


class TestLongestPrefixMatching:
    """Test that longest prefix matching works correctly for thin handlers."""

    def test_brain_capture_over_brain(self) -> None:
        """Should match 'brain capture' not just 'brain'."""
        from protocols.cli.legacy import resolve_legacy

        result = resolve_legacy(["brain", "capture", "extra"])
        assert result.is_legacy
        assert result.expanded == "self.memory.capture"
        assert result.remaining_args == ["extra"]

    def test_witness_show_over_witness(self) -> None:
        """Should match 'witness show' not just 'witness'."""
        from protocols.cli.legacy import resolve_legacy

        result = resolve_legacy(["witness", "show", "--json"])
        assert result.is_legacy
        assert result.expanded == "self.witness.show"
        assert result.remaining_args == ["--json"]

    def test_coffee_garden_over_coffee(self) -> None:
        """Should match 'coffee garden' not just 'coffee'."""
        from protocols.cli.legacy import resolve_legacy

        result = resolve_legacy(["coffee", "garden", "extra"])
        assert result.is_legacy
        assert result.expanded == "time.coffee.garden"
        assert result.remaining_args == ["extra"]


class TestBackwardCompatibility:
    """Ensure existing legacy commands still work after migration."""

    def test_memory_still_works(self) -> None:
        """memory → self.memory.manifest (pre-existing)"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["memory"])
        assert path == "self.memory.manifest"

    def test_soul_challenge_still_works(self) -> None:
        """soul challenge → self.soul.challenge (pre-existing)"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["soul", "challenge"])
        assert path == "self.soul.challenge"

    def test_town_citizens_still_works(self) -> None:
        """town citizens → world.town.citizens (pre-existing)"""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["town", "citizens"])
        assert path == "world.town.citizens"
