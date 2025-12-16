"""
Tests for path_display module (Wave 0 Foundation 1).

Tests the AGENTESE path visibility utilities that make the categorical
magic visible to users.
"""

import pytest
from protocols.cli.path_display import (
    CLI_TO_PATH_MAP,
    PathDisplayConfig,
    PathInfo,
    _reset_config,
    get_aspect_for_subcommand,
    get_path_display_config,
    get_path_for_command,
    parse_path_flags,
    set_path_display_config,
)


class TestPathInfo:
    """Tests for PathInfo dataclass."""

    def test_auto_detects_context_from_path(self) -> None:
        """PathInfo should auto-detect context from path."""
        info = PathInfo(path="self.memory.capture", aspect="define")
        assert info.context == "self"

    def test_all_contexts_detected(self) -> None:
        """All five AGENTESE contexts should be detected."""
        contexts = {
            "self.memory.capture": "self",
            "world.codebase.manifest": "world",
            "concept.gardener.session": "concept",
            "void.entropy.sip": "void",
            "time.trace.witness": "time",
        }
        for path, expected_context in contexts.items():
            info = PathInfo(path=path)
            assert info.context == expected_context, f"Failed for {path}"

    def test_effects_default_to_empty(self) -> None:
        """Effects should default to empty list."""
        info = PathInfo(path="self.test")
        assert info.effects == []

    def test_explicit_context_overrides_auto(self) -> None:
        """Explicit context should override auto-detection."""
        info = PathInfo(path="self.memory", context="custom")
        assert info.context == "custom"


class TestPathDisplayConfig:
    """Tests for PathDisplayConfig."""

    def setup_method(self) -> None:
        """Reset config before each test."""
        _reset_config()

    def teardown_method(self) -> None:
        """Reset config after each test."""
        _reset_config()

    def test_default_config(self) -> None:
        """Default config should have expected values."""
        config = get_path_display_config()
        assert config.enabled is True
        assert config.verbose is False
        assert config.show_tip is True
        assert config.use_color is True
        assert config.compact is False

    def test_set_enabled(self) -> None:
        """Should be able to disable path display."""
        set_path_display_config(enabled=False)
        config = get_path_display_config()
        assert config.enabled is False

    def test_set_verbose(self) -> None:
        """Should be able to enable verbose mode."""
        set_path_display_config(verbose=True)
        config = get_path_display_config()
        assert config.verbose is True

    def test_set_multiple_options(self) -> None:
        """Should be able to set multiple options at once."""
        set_path_display_config(enabled=True, verbose=True, compact=True)
        config = get_path_display_config()
        assert config.enabled is True
        assert config.verbose is True
        assert config.compact is True


class TestParsePathFlags:
    """Tests for parse_path_flags."""

    def test_no_flags(self) -> None:
        """No flags should return defaults."""
        args, show_paths, trace = parse_path_flags(["capture", "content"])
        assert args == ["capture", "content"]
        assert show_paths is True  # Default on
        assert trace is False

    def test_show_paths_flag(self) -> None:
        """--show-paths flag should enable path display."""
        args, show_paths, trace = parse_path_flags(["--show-paths", "capture"])
        assert args == ["capture"]
        assert show_paths is True
        assert trace is False

    def test_no_paths_flag(self) -> None:
        """--no-paths flag should disable path display."""
        args, show_paths, trace = parse_path_flags(["--no-paths", "capture"])
        assert args == ["capture"]
        assert show_paths is False
        assert trace is False

    def test_trace_flag(self) -> None:
        """--trace flag should enable trace mode."""
        args, show_paths, trace = parse_path_flags(["--trace", "status"])
        assert args == ["status"]
        assert show_paths is True
        assert trace is True

    def test_combined_flags(self) -> None:
        """Multiple flags should be parsed correctly."""
        args, show_paths, trace = parse_path_flags(
            ["--show-paths", "--trace", "capture", "content"]
        )
        assert args == ["capture", "content"]
        assert show_paths is True
        assert trace is True

    def test_flags_at_end(self) -> None:
        """Flags at end of args should still be parsed."""
        args, show_paths, trace = parse_path_flags(["capture", "content", "--trace"])
        assert args == ["capture", "content"]
        assert trace is True


class TestPathMapping:
    """Tests for CLI-to-AGENTESE path mapping."""

    def test_brain_commands_mapped(self) -> None:
        """Brain commands should map to self.memory paths."""
        assert get_path_for_command("brain", "capture") == "self.memory.capture"
        assert get_path_for_command("brain", "ghost") == "self.memory.ghost.surface"
        assert (
            get_path_for_command("brain", "map") == "self.memory.cartography.manifest"
        )
        assert get_path_for_command("brain", "status") == "self.memory.manifest"

    def test_gestalt_commands_mapped(self) -> None:
        """Gestalt commands should map to world.codebase paths."""
        assert get_path_for_command("world codebase") == "world.codebase.manifest"
        assert (
            get_path_for_command("world codebase", "health")
            == "world.codebase.health.manifest"
        )
        assert (
            get_path_for_command("world codebase", "drift")
            == "world.codebase.drift.witness"
        )

    def test_unknown_command_returns_none(self) -> None:
        """Unknown commands should return None."""
        assert get_path_for_command("unknown") is None

    def test_unknown_subcommand_falls_back_to_parent(self) -> None:
        """Unknown subcommands should fall back to parent command path."""
        # brain with unknown subcommand falls back to brain path
        assert get_path_for_command("brain", "unknown") == "self.memory"

    def test_fallback_to_parent_command(self) -> None:
        """Should fall back to parent command if subcommand not found."""
        assert get_path_for_command("brain") == "self.memory"


class TestAspectInference:
    """Tests for aspect inference from subcommands."""

    def test_manifest_aspects(self) -> None:
        """Status/show/list commands should infer manifest aspect."""
        assert get_aspect_for_subcommand("status") == "manifest"
        assert get_aspect_for_subcommand("show") == "manifest"
        assert get_aspect_for_subcommand("list") == "manifest"
        assert get_aspect_for_subcommand("map") == "manifest"
        assert get_aspect_for_subcommand("health") == "manifest"

    def test_witness_aspects(self) -> None:
        """Ghost/history/drift commands should infer witness aspect."""
        assert get_aspect_for_subcommand("ghost") == "witness"
        assert get_aspect_for_subcommand("history") == "witness"
        assert get_aspect_for_subcommand("drift") == "witness"
        assert get_aspect_for_subcommand("log") == "witness"

    def test_define_aspects(self) -> None:
        """Capture/create/add commands should infer define aspect."""
        assert get_aspect_for_subcommand("capture") == "define"
        assert get_aspect_for_subcommand("create") == "define"
        assert get_aspect_for_subcommand("add") == "define"
        assert get_aspect_for_subcommand("import") == "define"

    def test_entropy_aspects(self) -> None:
        """Tithe/sip commands should infer entropy aspects."""
        assert get_aspect_for_subcommand("tithe") == "tithe"
        assert get_aspect_for_subcommand("sip") == "sip"

    def test_unknown_defaults_to_manifest(self) -> None:
        """Unknown subcommands should default to manifest."""
        assert get_aspect_for_subcommand("unknown") == "manifest"


class TestCLIToPathMap:
    """Tests for CLI_TO_PATH_MAP completeness."""

    def test_brain_paths_exist(self) -> None:
        """Brain-related paths should be in the map."""
        brain_paths = [k for k in CLI_TO_PATH_MAP if "brain" in k.lower()]
        assert len(brain_paths) >= 4

    def test_gestalt_paths_exist(self) -> None:
        """Gestalt-related paths should be in the map."""
        gestalt_paths = [k for k in CLI_TO_PATH_MAP if "codebase" in k.lower()]
        assert len(gestalt_paths) >= 4

    def test_all_paths_have_valid_format(self) -> None:
        """All mapped paths should have valid AGENTESE format."""
        for cli_cmd, path in CLI_TO_PATH_MAP.items():
            assert "." in path, f"Path {path} for {cli_cmd} should contain '.'"
            parts = path.split(".")
            assert parts[0] in {"self", "world", "concept", "void", "time"}, (
                f"Path {path} should start with valid context"
            )
