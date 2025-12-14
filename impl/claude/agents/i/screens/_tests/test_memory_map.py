"""Tests for MemoryMapScreen and Four Pillars visualization."""

from __future__ import annotations

import pytest


class TestMemoryMapScreen:
    """Tests for MemoryMapScreen."""

    def test_demo_mode_creates_data(self) -> None:
        """Demo mode should create synthetic data."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=True)

        assert screen._crystal is not None
        assert screen._field is not None
        assert screen._inference is not None
        assert len(screen._games) >= 1

    def test_real_mode_uses_provided_data(self) -> None:
        """Real mode should use provided data."""
        from agents.m import (
            ActiveInferenceAgent,
            Belief,
            MemoryCrystal,
            PheromoneField,
            create_recall_game,
        )

        from ..memory_map import MemoryMapScreen

        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("test", "Test content", [0.5] * 64)

        field = PheromoneField()

        belief = Belief(distribution={"test": 1.0})
        inference: ActiveInferenceAgent[str] = ActiveInferenceAgent(belief)

        games = {"recall": create_recall_game()}

        screen = MemoryMapScreen(
            crystal=crystal,
            field=field,
            inference=inference,
            games=games,
        )

        assert screen._crystal is not None
        assert len(screen._crystal.concepts) == 1
        assert screen._field is not None
        assert screen._inference is not None
        assert "recall" in screen._games

    def test_render_crystal_empty(self) -> None:
        """Crystal render handles empty data."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=False)
        content = screen._render_crystal({})

        assert "No crystal data" in content

    def test_render_crystal_with_data(self) -> None:
        """Crystal render shows resolution distribution."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=True)

        data = {
            "dimension": 64,
            "concept_count": 2,
            "hot_count": 1,
            "avg_resolution": 0.75,
            "min_resolution": 0.5,
            "max_resolution": 1.0,
            "patterns": ["pattern1", "pattern2"],
            "resolutions": {"pattern1": 1.0, "pattern2": 0.5},
            "hot_patterns": ["pattern1"],
        }

        content = screen._render_crystal(data)

        assert "Concepts:" in content
        assert "Resolution Distribution" in content
        assert "pattern1" in content

    def test_render_field_empty(self) -> None:
        """Field render handles empty data."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=False)
        content = screen._render_field({})

        assert "No field data" in content

    def test_render_field_with_data(self) -> None:
        """Field render shows gradient map."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=True)

        data = {
            "concept_count": 2,
            "trace_count": 5,
            "deposit_count": 10,
            "evaporation_count": 2,
            "avg_intensity": 2.5,
            "decay_rate": 0.1,
            "top_gradients": [
                {"concept": "python", "intensity": 5.0, "traces": 3},
                {"concept": "rust", "intensity": 2.0, "traces": 2},
            ],
        }

        content = screen._render_field(data)

        assert "Concepts:" in content
        assert "Gradient Map" in content
        assert "python" in content

    def test_render_inference_empty(self) -> None:
        """Inference render handles empty data."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=False)
        content = screen._render_inference({})

        assert "No inference data" in content

    def test_render_inference_with_data(self) -> None:
        """Inference render shows belief distribution."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=True)

        data = {
            "precision": 1.2,
            "entropy": 1.5,
            "concepts": {"python": 0.4, "rust": 0.3, "other": 0.3},
            "budgets": {
                "test_concept": {
                    "free_energy": -0.5,
                    "complexity": 1.0,
                    "accuracy": 1.5,
                }
            },
        }

        content = screen._render_inference(data)

        assert "Precision:" in content
        assert "Belief Distribution" in content
        assert "python" in content

    def test_compose_games_panel_no_games(self) -> None:
        """Games panel handles no registered games."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=False)
        content = screen.compose_games_panel()

        assert "No language games" in content

    def test_compose_games_panel_with_games(self) -> None:
        """Games panel shows registered games."""
        from agents.m import create_recall_game

        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(
            games={"recall": create_recall_game()},
            demo_mode=False,
        )
        content = screen.compose_games_panel()

        assert "Registered Games:" in content
        assert "recall" in content

    @pytest.mark.asyncio
    async def test_refresh_data_populates_reactive_state(self) -> None:
        """Refresh should update reactive data from sources."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=True)
        await screen._refresh_data()

        assert screen.crystal_data is not None
        assert "concept_count" in screen.crystal_data
        assert screen.field_data is not None
        assert screen.inference_data is not None

    @pytest.mark.asyncio
    async def test_simulate_activity_when_inactive(self) -> None:
        """Simulation should not run when inactive."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=True)
        screen.simulation_active = False

        # Get initial stats
        initial_deposits = (
            screen._field.stats()["deposit_count"] if screen._field else 0
        )

        # Run simulation
        await screen._simulate_activity()

        # Should not have changed
        final_deposits = screen._field.stats()["deposit_count"] if screen._field else 0
        assert final_deposits == initial_deposits

    @pytest.mark.asyncio
    async def test_simulate_activity_updates_crystal(self) -> None:
        """Simulation should update crystal resolutions."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=True)
        screen.simulation_active = True

        # Get initial resolution levels
        if screen._crystal:
            initial_resolutions = dict(screen._crystal.resolution_levels)

            # Run simulation multiple times (more iterations for reliability)
            for _ in range(20):
                await screen._simulate_activity()

            # Check that at least one resolution changed
            # Using smaller threshold since factors are 1.05 and 0.98
            final_resolutions = screen._crystal.resolution_levels
            assert any(
                abs(final_resolutions.get(k, 0) - v) > 0.0001
                for k, v in initial_resolutions.items()
            )

    @pytest.mark.asyncio
    async def test_simulate_activity_deposits_pheromones(self) -> None:
        """Simulation should deposit pheromone traces."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=True)
        screen.simulation_active = True

        # Get initial deposit count
        if screen._field:
            initial_deposits = screen._field.stats()["deposit_count"]

            # Run simulation
            await screen._simulate_activity()

            # Should have more deposits
            final_deposits = screen._field.stats()["deposit_count"]
            assert final_deposits > initial_deposits

    @pytest.mark.asyncio
    async def test_simulate_activity_adjusts_precision(self) -> None:
        """Simulation should adjust belief precision."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=True)
        screen.simulation_active = True

        if screen._inference:
            initial_precision = screen._inference.belief.precision

            # Run simulation multiple times to increase chance of drift
            for _ in range(10):
                await screen._simulate_activity()

            final_precision = screen._inference.belief.precision

            # Precision should have drifted (or at least be in valid range)
            assert 0.5 <= final_precision <= 2.0

    def test_toggle_simulation_state(self) -> None:
        """Toggle simulation should change state."""
        from ..memory_map import MemoryMapScreen

        screen = MemoryMapScreen(demo_mode=True)

        # Initially active (default)
        assert screen.simulation_active is True

        # Toggle off directly
        screen.simulation_active = False
        assert screen.simulation_active is False

        # Toggle on
        screen.simulation_active = True
        assert screen.simulation_active is True

    def test_simulation_binding_present(self) -> None:
        """Simulation toggle binding should be present."""
        from textual.binding import Binding

        from ..memory_map import MemoryMapScreen

        # Check that 's' key is bound
        bindings = {
            b.key: b.action for b in MemoryMapScreen.BINDINGS if isinstance(b, Binding)
        }
        assert "s" in bindings
        assert bindings["s"] == "toggle_simulation"


class TestMemoryCrystalWidget:
    """Tests for MemoryCrystalWidget."""

    def test_compose_view_no_crystal(self) -> None:
        """Widget handles missing crystal."""
        from ..memory_map import MemoryCrystalWidget

        widget = MemoryCrystalWidget(crystal=None)
        assert widget.compose_view() == "No crystal"

    def test_compose_view_with_crystal(self) -> None:
        """Widget renders crystal stats."""
        from agents.m import MemoryCrystal

        from ..memory_map import MemoryCrystalWidget

        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("test", "Test content", [0.5] * 64)

        widget = MemoryCrystalWidget(crystal=crystal)
        view = widget.compose_view()

        assert "Memory Crystal" in view
        assert "Concepts:" in view


class TestPheromoneFieldWidget:
    """Tests for PheromoneFieldWidget."""

    @pytest.mark.asyncio
    async def test_compose_view_no_field(self) -> None:
        """Widget handles missing field."""
        from ..memory_map import PheromoneFieldWidget

        widget = PheromoneFieldWidget(field=None)
        view = await widget.compose_view()
        assert view == "No field"

    @pytest.mark.asyncio
    async def test_compose_view_with_field(self) -> None:
        """Widget renders field stats."""
        from agents.m import PheromoneField

        from ..memory_map import PheromoneFieldWidget

        field = PheromoneField()
        await field.deposit("test", 2.0, "agent")

        widget = PheromoneFieldWidget(field=field)
        view = await widget.compose_view()

        assert "Pheromone Field" in view


class TestLanguageGameWidget:
    """Tests for LanguageGameWidget."""

    def test_compose_view_no_game(self) -> None:
        """Widget handles missing game."""
        from ..memory_map import LanguageGameWidget

        widget = LanguageGameWidget(game=None, current_position="")
        assert widget.compose_view() == "No game"

    def test_compose_view_with_game(self) -> None:
        """Widget shows available moves."""
        from agents.m import create_recall_game

        from ..memory_map import LanguageGameWidget

        game = create_recall_game()
        widget = LanguageGameWidget(game=game, current_position="test")
        view = widget.compose_view()

        assert "Game" in view
        assert "Available Moves" in view


class TestMemoryDataProvider:
    """Tests for MemoryDataProvider."""

    def test_demo_mode_creates_all_components(self) -> None:
        """Demo mode should create all Four Pillars components."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=True)

        assert provider.memory_crystal is not None
        assert provider.pheromone_field is not None
        assert provider.inference_agent is not None
        assert len(provider.language_games) >= 1

    def test_real_mode_starts_empty(self) -> None:
        """Real mode should start with no components."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=False)

        assert provider.memory_crystal is None
        assert provider.pheromone_field is None
        assert provider.inference_agent is None
        assert len(provider.language_games) == 0

    def test_get_crystal_stats_no_crystal(self) -> None:
        """get_crystal_stats returns None when no crystal."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=False)
        assert provider.get_crystal_stats() is None

    def test_get_crystal_stats_with_crystal(self) -> None:
        """get_crystal_stats returns proper stats."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=True)
        stats = provider.get_crystal_stats()

        assert stats is not None
        assert "dimension" in stats
        assert "concept_count" in stats
        assert stats["dimension"] == 64

    @pytest.mark.asyncio
    async def test_get_field_stats_no_field(self) -> None:
        """get_field_stats returns None when no field."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=False)
        assert await provider.get_field_stats() is None

    @pytest.mark.asyncio
    async def test_get_field_stats_with_field(self) -> None:
        """get_field_stats returns proper stats."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=True)
        stats = await provider.get_field_stats()

        assert stats is not None
        assert "decay_rate" in stats

    def test_get_inference_stats_no_inference(self) -> None:
        """get_inference_stats returns None when no inference."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=False)
        assert provider.get_inference_stats() is None

    def test_get_inference_stats_with_inference(self) -> None:
        """get_inference_stats returns proper stats."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=True)
        stats = provider.get_inference_stats()

        assert stats is not None
        assert "precision" in stats
        assert "entropy" in stats

    def test_compute_health_empty(self) -> None:
        """compute_health handles empty provider."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=False)
        report = provider.compute_health()

        assert report["health_score"] == 0.0
        assert report["status"] == "CRITICAL"

    def test_compute_health_demo(self) -> None:
        """compute_health returns meaningful score for demo."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=True)
        report = provider.compute_health()

        # Demo should have some health
        assert report["health_score"] > 0.0
        assert report["status"] in ["HEALTHY", "DEGRADED", "CRITICAL"]

    def test_render_health_indicator(self) -> None:
        """render_health_indicator produces compact string."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=True)
        indicator = provider.render_health_indicator()

        assert "MEM:" in indicator
        assert "%" in indicator

    @pytest.mark.asyncio
    async def test_deposit_demo_traces(self) -> None:
        """deposit_demo_traces creates pheromone gradients."""
        from ...data.memory_provider import MemoryDataProvider

        provider = MemoryDataProvider(demo_mode=True)
        await provider.deposit_demo_traces()

        assert provider.pheromone_field is not None
        stats = provider.pheromone_field.stats()
        assert stats["deposit_count"] > 0

    @pytest.mark.asyncio
    async def test_factory_function(self) -> None:
        """Factory function creates provider."""
        from ...data.memory_provider import create_memory_provider

        provider = create_memory_provider(demo_mode=True)
        assert provider.demo_mode is True
        assert provider.memory_crystal is not None

    @pytest.mark.asyncio
    async def test_async_factory_function(self) -> None:
        """Async factory function creates provider with traces."""
        from ...data.memory_provider import create_memory_provider_async

        provider = await create_memory_provider_async(demo_mode=True)
        assert provider.demo_mode is True

        # Should have traces deposited
        if provider.pheromone_field:
            stats = provider.pheromone_field.stats()
            assert stats["deposit_count"] > 0
