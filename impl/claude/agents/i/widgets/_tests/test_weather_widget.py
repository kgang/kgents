"""Tests for WeatherWidget."""

from __future__ import annotations

import pytest

from ...data.weather import PressureLevel, Weather, WeatherCondition, WindDirection
from ..weather_widget import CompactWeatherWidget, WeatherWidget


class TestWeatherWidget:
    """Tests for WeatherWidget."""

    def test_widget_creation(self) -> None:
        """Test widget creation."""
        widget = WeatherWidget()
        assert widget is not None

    def test_widget_demo_mode(self) -> None:
        """Test widget in demo mode."""
        widget = WeatherWidget(demo_mode=True)
        assert widget._weather is not None

    def test_widget_with_weather(self) -> None:
        """Test widget with specific weather."""
        weather = Weather(
            condition=WeatherCondition.CLEAR,
            temperature="Warm",
            pressure=PressureLevel.NORMAL,
            wind=WindDirection.EAST,
            cloud_cover=10.0,
            wind_speed=5.0,
            forecast=[],
        )
        widget = WeatherWidget(weather=weather)
        assert widget._weather.condition == WeatherCondition.CLEAR

    def test_update_metrics(self) -> None:
        """Test updating metrics."""
        widget = WeatherWidget()
        initial_weather = widget._weather

        widget.update_metrics(entropy=0.9, token_rate=500.0, queue_depth=50)

        # Weather should be recomputed
        assert widget._weather is not None

    def test_update_weather_directly(self) -> None:
        """Test updating weather directly."""
        widget = WeatherWidget()
        new_weather = Weather(
            condition=WeatherCondition.STORMY,
            temperature="Hot",
            pressure=PressureLevel.HIGH,
            wind=WindDirection.SOUTH,
            cloud_cover=95.0,
            wind_speed=50.0,
            forecast=[],
        )

        widget.update_weather(new_weather)
        assert widget._weather.condition == WeatherCondition.STORMY

    def test_current_weather_property(self) -> None:
        """Test current_weather property."""
        widget = WeatherWidget(demo_mode=True)
        weather = widget.current_weather
        assert isinstance(weather, Weather)

    def test_trend_property(self) -> None:
        """Test trend property."""
        widget = WeatherWidget()
        trend = widget.trend
        assert trend in ("stable", "improving", "degrading")

    def test_render(self) -> None:
        """Test rendering."""
        widget = WeatherWidget(demo_mode=True)
        rendered = widget.render()
        assert isinstance(rendered, str)
        assert len(rendered) > 0


class TestCompactWeatherWidget:
    """Tests for CompactWeatherWidget."""

    def test_widget_creation(self) -> None:
        """Test compact widget creation."""
        widget = CompactWeatherWidget()
        assert widget is not None

    def test_widget_with_weather(self) -> None:
        """Test compact widget with weather."""
        weather = Weather(
            condition=WeatherCondition.CLOUDY,
            temperature="Cool",
            pressure=PressureLevel.LOW,
            wind=WindDirection.WEST,
            cloud_cover=70.0,
            wind_speed=20.0,
            forecast=[],
        )
        widget = CompactWeatherWidget(weather=weather)
        assert widget._weather.condition == WeatherCondition.CLOUDY

    def test_update_weather(self) -> None:
        """Test updating weather."""
        widget = CompactWeatherWidget()
        new_weather = Weather(
            condition=WeatherCondition.FAIR,
            temperature="Warm",
            pressure=PressureLevel.NORMAL,
            wind=WindDirection.NORTH,
            cloud_cover=20.0,
            wind_speed=15.0,
            forecast=[],
        )

        widget.update_weather(new_weather)
        assert widget._weather.condition == WeatherCondition.FAIR

    def test_render(self) -> None:
        """Test compact rendering."""
        widget = CompactWeatherWidget()
        rendered = widget.render()
        assert isinstance(rendered, str)
        # Compact widget should be short
        assert len(rendered) < 30
