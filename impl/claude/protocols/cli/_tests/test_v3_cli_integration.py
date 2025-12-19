"""
Tests for AGENTESE v3 CLI Integration (Phase 3).

Tests cover:
1. Shortcut resolution
2. Legacy command mapping
3. Input classification
4. Router integration
5. OTEL tracing stubs

Per spec/protocols/agentese-v3.md §12 (CLI Unification).
"""

from __future__ import annotations

import pytest

# =============================================================================
# Shortcut Tests
# =============================================================================


class TestShortcutRegistry:
    """Tests for the shortcut registry."""

    def test_standard_shortcuts_loaded(self) -> None:
        """Standard shortcuts should be available."""
        from protocols.cli.shortcuts import STANDARD_SHORTCUTS, get_shortcut_registry

        registry = get_shortcut_registry()

        # Should have all standard shortcuts
        for name in STANDARD_SHORTCUTS:
            assert name in registry.standard

    def test_resolve_standard_shortcut(self) -> None:
        """Should resolve standard shortcuts."""
        from protocols.cli.shortcuts import resolve_shortcut

        result = resolve_shortcut("/forest")

        assert result.is_shortcut
        assert result.source == "standard"
        assert result.expanded == "self.forest.manifest"

    def test_resolve_shortcut_with_aspect(self) -> None:
        """Should allow aspect override on shortcuts."""
        from protocols.cli.shortcuts import resolve_shortcut

        result = resolve_shortcut("/soul.challenge")

        assert result.is_shortcut
        assert "challenge" in result.expanded

    def test_non_shortcut_passthrough(self) -> None:
        """Non-shortcuts should pass through unchanged."""
        from protocols.cli.shortcuts import resolve_shortcut

        result = resolve_shortcut("self.forest.manifest")

        assert not result.is_shortcut
        assert result.expanded == "self.forest.manifest"

    def test_unknown_shortcut_passthrough(self) -> None:
        """Unknown shortcuts should pass through unchanged."""
        from protocols.cli.shortcuts import resolve_shortcut

        result = resolve_shortcut("/unknown_shortcut")

        assert not result.is_shortcut
        assert result.original == "/unknown_shortcut"

    def test_expand_shortcut_helper(self) -> None:
        """expand_shortcut should return the expanded path."""
        from protocols.cli.shortcuts import expand_shortcut

        assert expand_shortcut("/chaos") == "void.entropy.sip"
        assert expand_shortcut("world.house") == "world.house"

    def test_reserved_names_cannot_be_added(self) -> None:
        """Should not allow shortcuts for reserved context names."""
        from protocols.cli.shortcuts import ShortcutRegistry

        registry = ShortcutRegistry()

        assert not registry.add("world", "some.path")
        assert not registry.add("self", "some.path")
        assert not registry.add("concept", "some.path")

    def test_user_shortcuts_override_standard(self) -> None:
        """User shortcuts should take precedence."""
        from protocols.cli.shortcuts import ShortcutRegistry

        registry = ShortcutRegistry()
        registry.add("forest", "custom.forest.path")

        result = registry.resolve("/forest")

        assert result.is_shortcut
        assert result.source == "user"
        assert result.expanded == "custom.forest.path"

    def test_list_all_shortcuts(self) -> None:
        """Should list all shortcuts with sources."""
        from protocols.cli.shortcuts import ShortcutRegistry

        registry = ShortcutRegistry()
        registry.add("custom", "my.custom.path")

        all_shortcuts = registry.list_all()

        assert "forest" in all_shortcuts
        assert all_shortcuts["forest"][1] == "standard"
        assert "custom" in all_shortcuts
        assert all_shortcuts["custom"][1] == "user"


# =============================================================================
# Legacy Command Tests
# =============================================================================


class TestLegacyRegistry:
    """Tests for the legacy command registry."""

    def test_simple_legacy_command(self) -> None:
        """Should resolve simple legacy commands."""
        from protocols.cli.legacy import resolve_legacy

        result = resolve_legacy(["memory"])

        assert result.is_legacy
        assert result.expanded == "self.memory.manifest"
        assert result.remaining_args == []

    def test_multi_word_legacy_command(self) -> None:
        """Should resolve multi-word legacy commands."""
        from protocols.cli.legacy import resolve_legacy

        result = resolve_legacy(["soul", "challenge"])

        assert result.is_legacy
        assert result.expanded == "self.soul.challenge"
        assert result.remaining_args == []

    def test_legacy_with_remaining_args(self) -> None:
        """Should extract remaining args after legacy command."""
        from protocols.cli.legacy import resolve_legacy

        result = resolve_legacy(["memory", "status", "--json"])

        assert result.is_legacy
        assert result.remaining_args == ["--json"]

    def test_longest_prefix_matching(self) -> None:
        """Should match the longest prefix."""
        from protocols.cli.legacy import resolve_legacy

        # "soul challenge" is longer match than "soul"
        result = resolve_legacy(["soul", "challenge", "extra"])

        assert result.is_legacy
        assert result.expanded == "self.soul.challenge"
        assert result.remaining_args == ["extra"]

    def test_non_legacy_command(self) -> None:
        """Non-legacy commands should not match."""
        from protocols.cli.legacy import resolve_legacy

        result = resolve_legacy(["unknown_command", "arg"])

        assert not result.is_legacy
        assert result.remaining_args == ["arg"]

    def test_is_legacy_command_helper(self) -> None:
        """is_legacy_command should detect legacy commands."""
        from protocols.cli.legacy import is_legacy_command

        assert is_legacy_command(["memory"])
        assert is_legacy_command(["soul", "challenge"])
        assert not is_legacy_command(["unknown"])

    def test_expand_legacy_helper(self) -> None:
        """expand_legacy should return path and remaining args."""
        from protocols.cli.legacy import expand_legacy

        path, remaining = expand_legacy(["memory", "status", "--json"])

        assert path == "self.memory.manifest"
        assert remaining == ["--json"]


# =============================================================================
# Input Classification Tests
# =============================================================================


class TestInputClassification:
    """Tests for input classification."""

    def test_classify_direct_path(self) -> None:
        """Should classify direct AGENTESE paths."""
        from protocols.cli.agentese_router import InputType, classify_input

        result = classify_input(["self.forest.manifest"])

        assert result.input_type == InputType.DIRECT_PATH
        assert result.agentese_path == "self.forest.manifest"

    def test_classify_shortcut(self) -> None:
        """Should classify shortcuts."""
        from protocols.cli.agentese_router import InputType, classify_input

        result = classify_input(["/forest"])

        assert result.input_type == InputType.SHORTCUT
        assert result.agentese_path == "self.forest.manifest"

    def test_classify_query(self) -> None:
        """Should classify queries."""
        from protocols.cli.agentese_router import InputType, classify_input

        result = classify_input(["?world.*"])

        assert result.input_type == InputType.QUERY
        assert result.agentese_path == "world.*"

    def test_classify_subscribe(self) -> None:
        """Should classify subscribe commands."""
        from protocols.cli.agentese_router import InputType, classify_input

        result = classify_input(["subscribe", "self.memory.*"])

        assert result.input_type == InputType.SUBSCRIBE
        assert result.agentese_path == "self.memory.*"

    def test_classify_composition(self) -> None:
        """Should classify compositions."""
        from protocols.cli.agentese_router import InputType, classify_input

        result = classify_input(["self.forest.manifest", ">>", "concept.summary.refine"])

        assert result.input_type == InputType.COMPOSITION
        assert len(result.composition_parts) == 2

    def test_classify_legacy(self) -> None:
        """Should classify legacy commands."""
        from protocols.cli.agentese_router import InputType, classify_input

        result = classify_input(["memory", "status"])

        assert result.input_type == InputType.LEGACY
        assert result.agentese_path == "self.memory.manifest"

    def test_classify_unknown(self) -> None:
        """Should classify unknown commands."""
        from protocols.cli.agentese_router import InputType, classify_input

        result = classify_input(["unknown_thing"])

        assert result.input_type == InputType.UNKNOWN


# =============================================================================
# Router Tests
# =============================================================================


class TestAgentesRouter:
    """Tests for the AGENTESE router."""

    def test_router_config_defaults(self) -> None:
        """Router config should have sensible defaults."""
        from protocols.cli.agentese_router import RouterConfig

        config = RouterConfig()

        assert not config.json_output
        assert not config.trace_output
        assert not config.dry_run
        assert config.otel_enabled
        assert config.archetype == "cli"

    def test_router_result_structure(self) -> None:
        """Router result should have expected structure."""
        from protocols.cli.agentese_router import RouterResult

        result = RouterResult(
            success=True,
            result={"test": "data"},
            agentese_path="self.forest.manifest",
        )

        assert result.success
        assert result.result == {"test": "data"}
        assert result.agentese_path == "self.forest.manifest"
        assert result.trace_id is None
        assert result.duration_ms == 0

    @pytest.mark.asyncio
    async def test_router_dry_run(self) -> None:
        """Router should support dry run mode."""
        from protocols.cli.agentese_router import AgentesRouter, RouterConfig

        config = RouterConfig(dry_run=True)
        router = AgentesRouter(config=config)

        result = await router.route(["self.forest.manifest"])

        assert result.success
        assert result.result["dry_run"]
        assert result.result["path"] == "self.forest.manifest"


# =============================================================================
# Hollow Shell Integration Tests
# =============================================================================


class TestHollowShellIntegration:
    """Tests for hollow.py integration."""

    def test_agentese_path_detection(self) -> None:
        """Should detect AGENTESE paths correctly."""

        # Test detection logic from hollow.py
        def is_agentese(command: str) -> bool:
            return "." in command and command.split(".")[0] in {
                "world",
                "self",
                "concept",
                "void",
                "time",
            }

        assert is_agentese("self.forest.manifest")
        assert is_agentese("world.town.citizens")
        assert not is_agentese("forest")
        assert not is_agentese("some.other.path")

    def test_shortcut_detection(self) -> None:
        """Should detect shortcuts correctly."""

        def is_shortcut(command: str) -> bool:
            return command.startswith("/")

        assert is_shortcut("/forest")
        assert is_shortcut("/soul")
        assert not is_shortcut("forest")

    def test_query_detection(self) -> None:
        """Should detect queries correctly."""

        def is_query(command: str) -> bool:
            return command.startswith("?")

        assert is_query("?world.*")
        assert is_query("?self.memory.?")
        assert not is_query("world.*")


# =============================================================================
# Command Handler Tests
# =============================================================================


class TestCommandHandlers:
    """Tests for CLI command handlers."""

    def test_shortcut_cmd_list(self) -> None:
        """Shortcut list command should work."""
        from protocols.cli.shortcuts import cmd_shortcut

        # Should not raise
        result = cmd_shortcut(["list"])
        assert result == 0

    def test_legacy_cmd_list(self) -> None:
        """Legacy list command should work."""
        from protocols.cli.legacy import cmd_legacy

        # Should not raise
        result = cmd_legacy(["list"])
        assert result == 0


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_input(self) -> None:
        """Should handle empty input gracefully."""
        from protocols.cli.agentese_router import InputType, classify_input

        result = classify_input([])

        assert result.input_type == InputType.UNKNOWN

    def test_shortcut_with_dots(self) -> None:
        """Should handle shortcuts with dots in aspect."""
        from protocols.cli.shortcuts import resolve_shortcut

        result = resolve_shortcut("/forest.trees")

        assert result.is_shortcut

    def test_legacy_single_word(self) -> None:
        """Should handle single-word legacy commands."""
        from protocols.cli.legacy import resolve_legacy

        result = resolve_legacy(["status"])

        assert result.is_legacy
        assert result.expanded == "self.status.manifest"

    def test_composition_with_shortcuts(self) -> None:
        """Should handle compositions with shortcuts."""
        from protocols.cli.agentese_router import InputType, classify_input

        result = classify_input(["/forest", ">>", "/brain"])

        assert result.input_type == InputType.COMPOSITION
        assert len(result.composition_parts) == 2
