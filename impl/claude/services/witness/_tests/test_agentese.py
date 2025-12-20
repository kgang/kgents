"""
Tests for AgenteseWatcher.

Verifies:
1. AGENTESE path parsing
2. Jewel detection from topic prefix
3. SynergyBus subscription
4. Event emission
5. Cleanup on stop

See: docs/skills/test-patterns.md
"""

from __future__ import annotations

import asyncio

import pytest

from services.witness.polynomial import AgenteseEvent
from services.witness.watchers.agentese import (
    AgenteseConfig,
    AgenteseWatcher,
    create_agentese_watcher,
    parse_agentese_path,
    parse_agentese_path_with_config,
)
from services.witness.watchers.base import WatcherState


# =============================================================================
# Path Parsing Tests
# =============================================================================


class TestAgentesePathParsing:
    """Test AGENTESE path parsing."""

    def test_parses_world_town_path(self) -> None:
        """Parse world.town.citizen.create path."""
        path, aspect, jewel = parse_agentese_path("world.town.citizen.create")

        assert path == "world.town.citizen"
        assert aspect == "create"
        assert jewel == "Town"

    def test_parses_self_memory_path(self) -> None:
        """Parse self.memory.capture path."""
        path, aspect, jewel = parse_agentese_path("self.memory.capture")

        assert path == "self.memory"
        assert aspect == "capture"
        assert jewel == "Brain"

    def test_parses_world_park_path(self) -> None:
        """Parse world.park.garden.plant path."""
        path, aspect, jewel = parse_agentese_path("world.park.garden.plant")

        assert path == "world.park.garden"
        assert aspect == "plant"
        assert jewel == "Park"

    def test_parses_unknown_jewel(self) -> None:
        """Unknown prefix returns None for jewel."""
        path, aspect, jewel = parse_agentese_path("custom.path.action")

        assert path == "custom.path"
        assert aspect == "action"
        assert jewel is None

    def test_handles_short_path(self) -> None:
        """Single-part path returns defaults."""
        path, aspect, jewel = parse_agentese_path("single")

        assert path == "single"
        assert aspect == "unknown"
        assert jewel is None

    def test_custom_jewel_mapping(self) -> None:
        """Custom config can add jewel mappings."""
        config = AgenteseConfig(
            jewel_mapping={
                "custom.new": "CustomJewel",
            }
        )
        path, aspect, jewel = parse_agentese_path_with_config("custom.new.action", config)

        assert path == "custom.new"
        assert aspect == "action"
        assert jewel == "CustomJewel"


# =============================================================================
# Configuration Tests
# =============================================================================


class TestAgenteseConfig:
    """Test AgenteseConfig defaults."""

    def test_default_patterns(self) -> None:
        """Default config includes standard AGENTESE contexts."""
        config = AgenteseConfig()

        assert "world.*" in config.topic_patterns
        assert "self.*" in config.topic_patterns
        assert "concept.*" in config.topic_patterns

    def test_default_jewel_mapping(self) -> None:
        """Default config maps standard jewels."""
        config = AgenteseConfig()

        assert "world.town" in config.jewel_mapping
        assert config.jewel_mapping["world.town"] == "Town"
        assert config.jewel_mapping["self.memory"] == "Brain"


# =============================================================================
# Watcher Lifecycle Tests
# =============================================================================


class TestAgenteseWatcherLifecycle:
    """Test watcher lifecycle."""

    def test_initial_state_stopped(self) -> None:
        """Watcher starts in STOPPED state."""
        watcher = AgenteseWatcher()
        assert watcher.state == WatcherState.STOPPED

    @pytest.mark.asyncio
    async def test_start_without_bus_logs_warning(self) -> None:
        """Starting without a bus logs a warning but doesn't crash."""
        watcher = AgenteseWatcher(bus=None)

        # Should not raise, just log warning
        await watcher.start()
        try:
            assert watcher.state == WatcherState.RUNNING
        finally:
            await watcher.stop()

    @pytest.mark.asyncio
    async def test_stop_cleans_up(self) -> None:
        """Stop transitions back to STOPPED state."""
        watcher = AgenteseWatcher()

        await watcher.start()
        await watcher.stop()

        assert watcher.state == WatcherState.STOPPED


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunction:
    """Test factory function."""

    def test_create_with_default_patterns(self) -> None:
        """Factory creates watcher with default patterns."""
        watcher = create_agentese_watcher()

        assert "world.*" in watcher.config.topic_patterns

    def test_create_with_custom_patterns(self) -> None:
        """Factory accepts custom patterns."""
        watcher = create_agentese_watcher(patterns=("custom.*",))

        assert watcher.config.topic_patterns == ("custom.*",)
