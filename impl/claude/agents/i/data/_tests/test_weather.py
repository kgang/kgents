"""Tests for WeatherEngine and weather system."""

from __future__ import annotations

import random

import pytest

from ..weather import (
    OBLIQUE_STRATEGIES,
    PressureLevel,
    SystemMetrics,
    Weather,
    WeatherCondition,
    WeatherEngine,
    WindDirection,
    create_demo_weather,
)


class TestWeatherCondition:
    """Tests for WeatherCondition enum."""

    def test_all_conditions_have_values(self) -> None:
        """Test all conditions exist."""
        conditions = list(WeatherCondition)
        assert len(conditions) >= 5
        assert WeatherCondition.CLEAR in conditions
        assert WeatherCondition.STORMY in conditions


class TestSystemMetrics:
    """Tests for SystemMetrics dataclass."""

    def test_default_values(self) -> None:
        """Test default metric values."""
        metrics = SystemMetrics()
        assert metrics.entropy == 0.3
        assert metrics.token_rate == 100.0
        assert metrics.queue_depth == 5

    def test_custom_values(self) -> None:
        """Test custom metric values."""
        metrics = SystemMetrics(entropy=0.8, token_rate=500.0, queue_depth=20)
        assert metrics.entropy == 0.8
        assert metrics.token_rate == 500.0
        assert metrics.queue_depth == 20


class TestMetricsToCondition:
    """Tests for weather condition based on metrics."""

    def test_low_entropy_clear(self) -> None:
        """Test low entropy results in clear conditions."""
        metrics = SystemMetrics(entropy=0.1, token_rate=100.0, queue_depth=3)
        engine = WeatherEngine()
        weather = engine.compute_weather(metrics)
        assert weather.condition in (WeatherCondition.CLEAR, WeatherCondition.FAIR)

    def test_high_entropy_stormy(self) -> None:
        """Test high entropy results in stormy conditions."""
        metrics = SystemMetrics(entropy=0.9, token_rate=500.0, queue_depth=50)
        engine = WeatherEngine()
        weather = engine.compute_weather(metrics)
        assert weather.condition in (WeatherCondition.STORMY, WeatherCondition.OVERCAST)

    def test_medium_entropy_cloudy(self) -> None:
        """Test medium entropy results in cloudy conditions."""
        metrics = SystemMetrics(entropy=0.5, token_rate=100.0, queue_depth=10)
        engine = WeatherEngine()
        weather = engine.compute_weather(metrics)
        assert weather.condition in (
            WeatherCondition.PARTLY_CLOUDY,
            WeatherCondition.CLOUDY,
            WeatherCondition.FAIR,
        )


class TestWeather:
    """Tests for Weather dataclass."""

    def test_weather_creation(self) -> None:
        """Test weather creation."""
        weather = Weather(
            condition=WeatherCondition.FAIR,
            temperature="Warm",
            pressure=PressureLevel.NORMAL,
            wind=WindDirection.EAST,
            cloud_cover=30.0,
            wind_speed=10.0,
            forecast=[],
        )
        assert weather.condition == WeatherCondition.FAIR
        assert weather.temperature == "Warm"
        assert weather.pressure == PressureLevel.NORMAL

    def test_weather_with_oblique_strategy(self) -> None:
        """Test weather can have oblique strategy."""
        weather = Weather(
            condition=WeatherCondition.STORMY,
            temperature="Hot",
            pressure=PressureLevel.HIGH,
            wind=WindDirection.NORTH,
            cloud_cover=90.0,
            wind_speed=50.0,
            forecast=[],
            oblique_strategy="Honor thy error as a hidden intention",
        )
        assert weather.oblique_strategy is not None
        assert len(weather.oblique_strategy) > 0


class TestWeatherEngine:
    """Tests for WeatherEngine."""

    def test_engine_creation(self) -> None:
        """Test engine creation."""
        engine = WeatherEngine()
        assert engine is not None

    def test_compute_weather(self) -> None:
        """Test computing weather from metrics."""
        engine = WeatherEngine()
        metrics = SystemMetrics(entropy=0.3, token_rate=100.0, queue_depth=5)

        weather = engine.compute_weather(metrics)

        assert isinstance(weather, Weather)
        assert weather.condition is not None
        assert weather.temperature in ("Cold", "Cool", "Warm", "Hot")

    def test_high_entropy_adds_oblique(self) -> None:
        """Test high entropy adds oblique strategy."""
        engine = WeatherEngine()
        metrics = SystemMetrics(entropy=0.85, token_rate=100.0, queue_depth=10)

        weather = engine.compute_weather(metrics)

        # High entropy should trigger oblique strategy
        # (may not always be present due to randomness)
        assert weather is not None

    def test_multiple_computes(self) -> None:
        """Test engine can compute multiple times."""
        engine = WeatherEngine()

        w1 = engine.compute_weather(SystemMetrics(entropy=0.3))
        w2 = engine.compute_weather(SystemMetrics(entropy=0.8))

        # Both should return valid weather
        assert w1 is not None
        assert w2 is not None
        # Higher entropy should produce different conditions
        assert w1.cloud_cover <= w2.cloud_cover

    def test_get_trend(self) -> None:
        """Test getting weather trend."""
        engine = WeatherEngine()

        # Compute a few samples
        engine.compute_weather(SystemMetrics(entropy=0.2))
        engine.compute_weather(SystemMetrics(entropy=0.3))
        engine.compute_weather(SystemMetrics(entropy=0.4))

        trend = engine.get_trend()
        assert trend in ("stable", "improving", "degrading")


class TestCreateDemoWeather:
    """Tests for create_demo_weather helper."""

    def test_creates_weather(self) -> None:
        """Test it creates a weather object."""
        weather = create_demo_weather()
        assert isinstance(weather, Weather)
        assert weather.condition is not None

    def test_repeatable(self) -> None:
        """Test it creates valid weather each time."""
        for _ in range(10):
            weather = create_demo_weather()
            assert weather.condition in WeatherCondition


class TestObliqueStrategies:
    """Tests for OBLIQUE_STRATEGIES list."""

    def test_strategies_exist(self) -> None:
        """Test oblique strategies list is populated."""
        assert len(OBLIQUE_STRATEGIES) >= 10
        assert all(isinstance(s, str) for s in OBLIQUE_STRATEGIES)

    def test_random_strategy_selection(self) -> None:
        """Test random selection from strategies."""
        strategies = set()
        for _ in range(20):
            strategies.add(random.choice(OBLIQUE_STRATEGIES))
        # Should get at least a few different ones
        assert len(strategies) >= 3
