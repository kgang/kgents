"""
Tests for Morning Coffee types.

Verifies:
- Enum properties (Pattern 2)
- Dataclass immutability (frozen)
- Serialization (to_dict/from_dict)
- Voice anchor conversion
"""

from datetime import date, datetime

import pytest

from services.liminal.coffee.types import (
    MOVEMENTS,
    ChallengeLevel,
    ChallengeMenu,
    CoffeeOutput,
    CoffeeState,
    ConceptualWeather,
    GardenCategory,
    GardenItem,
    GardenView,
    MenuItem,
    MorningVoice,
    Movement,
    RitualEvent,
    WeatherPattern,
    WeatherType,
)

# =============================================================================
# CoffeeState Tests
# =============================================================================


class TestCoffeeState:
    """Tests for CoffeeState enum."""

    def test_all_states_exist(self) -> None:
        """Verify all expected states are defined."""
        assert CoffeeState.DORMANT
        assert CoffeeState.GARDEN
        assert CoffeeState.WEATHER
        assert CoffeeState.MENU
        assert CoffeeState.CAPTURE
        assert CoffeeState.TRANSITION

    def test_state_count(self) -> None:
        """Verify we have exactly 6 states."""
        assert len(CoffeeState) == 6


# =============================================================================
# ChallengeLevel Tests (Pattern 2: Enum Property)
# =============================================================================


class TestChallengeLevel:
    """Tests for ChallengeLevel enum with properties."""

    def test_all_levels_exist(self) -> None:
        """Verify all challenge levels are defined."""
        assert ChallengeLevel.GENTLE
        assert ChallengeLevel.FOCUSED
        assert ChallengeLevel.INTENSE
        assert ChallengeLevel.SERENDIPITOUS

    def test_emoji_property(self) -> None:
        """Verify each level has an emoji (Pattern 2)."""
        assert ChallengeLevel.GENTLE.emoji == "🧘"
        assert ChallengeLevel.FOCUSED.emoji == "🎯"
        assert ChallengeLevel.INTENSE.emoji == "🔥"
        assert ChallengeLevel.SERENDIPITOUS.emoji == "🎲"

    def test_description_property(self) -> None:
        """Verify each level has a description."""
        assert "Warmup" in ChallengeLevel.GENTLE.description
        assert "Clear objective" in ChallengeLevel.FOCUSED.description
        assert "Deep work" in ChallengeLevel.INTENSE.description
        assert "curiosity" in ChallengeLevel.SERENDIPITOUS.description

    def test_cognitive_load_property(self) -> None:
        """Verify cognitive load increases with intensity."""
        assert ChallengeLevel.GENTLE.cognitive_load < ChallengeLevel.FOCUSED.cognitive_load
        assert ChallengeLevel.FOCUSED.cognitive_load < ChallengeLevel.INTENSE.cognitive_load

    def test_cognitive_load_range(self) -> None:
        """Verify cognitive load is in valid range."""
        for level in ChallengeLevel:
            assert 0.0 <= level.cognitive_load <= 1.0


# =============================================================================
# Movement Tests
# =============================================================================


class TestMovement:
    """Tests for Movement dataclass."""

    def test_movements_defined(self) -> None:
        """Verify all four movements are defined."""
        assert "garden" in MOVEMENTS
        assert "weather" in MOVEMENTS
        assert "menu" in MOVEMENTS
        assert "capture" in MOVEMENTS

    def test_movement_frozen(self) -> None:
        """Verify Movement is immutable."""
        movement = MOVEMENTS["garden"]
        with pytest.raises(AttributeError):
            movement.name = "changed"  # type: ignore

    def test_observation_movements_no_input(self) -> None:
        """Garden and Weather should not require input."""
        assert MOVEMENTS["garden"].requires_input is False
        assert MOVEMENTS["weather"].requires_input is False

    def test_interactive_movements_require_input(self) -> None:
        """Menu and Capture should require input."""
        assert MOVEMENTS["menu"].requires_input is True
        assert MOVEMENTS["capture"].requires_input is True

    def test_all_movements_skippable(self) -> None:
        """All movements should be skippable (ritual serves human)."""
        for movement in MOVEMENTS.values():
            assert movement.skippable is True

    def test_movement_to_dict(self) -> None:
        """Verify Movement serialization."""
        movement = MOVEMENTS["garden"]
        data = movement.to_dict()
        assert data["name"] == "Garden View"
        assert data["prompt"] == "What grew while I slept?"
        assert data["requires_input"] is False


# =============================================================================
# GardenView Tests
# =============================================================================


class TestGardenView:
    """Tests for Garden types."""

    def test_garden_item_frozen(self) -> None:
        """Verify GardenItem is immutable."""
        item = GardenItem(
            description="Test item",
            category=GardenCategory.HARVEST,
        )
        with pytest.raises(AttributeError):
            item.description = "changed"  # type: ignore

    def test_garden_item_to_dict(self) -> None:
        """Verify GardenItem serialization."""
        item = GardenItem(
            description="Added tests",
            category=GardenCategory.HARVEST,
            files_changed=3,
            source="git",
        )
        data = item.to_dict()
        assert data["description"] == "Added tests"
        assert data["category"] == "harvest"
        assert data["files_changed"] == 3

    def test_garden_view_frozen(self) -> None:
        """Verify GardenView is immutable."""
        view = GardenView()
        with pytest.raises(AttributeError):
            view.harvest = ()  # type: ignore

    def test_garden_view_empty(self) -> None:
        """Verify empty garden detection."""
        view = GardenView()
        assert view.is_empty is True
        assert view.total_items == 0

    def test_garden_view_with_items(self) -> None:
        """Verify garden with items."""
        item = GardenItem(description="Test", category=GardenCategory.GROWING)
        view = GardenView(growing=(item,))
        assert view.is_empty is False
        assert view.total_items == 1

    def test_garden_view_to_dict(self) -> None:
        """Verify GardenView serialization."""
        item = GardenItem(description="Test", category=GardenCategory.SEEDS)
        view = GardenView(seeds=(item,))
        data = view.to_dict()
        assert len(data["seeds"]) == 1
        assert "generated_at" in data


# =============================================================================
# ConceptualWeather Tests
# =============================================================================


class TestConceptualWeather:
    """Tests for Weather types."""

    def test_weather_type_emoji(self) -> None:
        """Verify WeatherType has emojis."""
        assert WeatherType.REFACTORING.emoji == "🔄"
        assert WeatherType.EMERGING.emoji == "🌊"
        assert WeatherType.SCAFFOLDING.emoji == "🏗️"
        assert WeatherType.TENSION.emoji == "⚡"

    def test_weather_pattern_frozen(self) -> None:
        """Verify WeatherPattern is immutable."""
        pattern = WeatherPattern(
            type=WeatherType.EMERGING,
            label="New pattern",
            description="Something emerging",
        )
        with pytest.raises(AttributeError):
            pattern.label = "changed"  # type: ignore

    def test_weather_pattern_to_dict(self) -> None:
        """Verify WeatherPattern serialization."""
        pattern = WeatherPattern(
            type=WeatherType.TENSION,
            label="Depth vs breadth",
            description="Competing concerns",
        )
        data = pattern.to_dict()
        assert data["type"] == "tension"
        assert data["emoji"] == "⚡"
        assert data["label"] == "Depth vs breadth"

    def test_conceptual_weather_empty(self) -> None:
        """Verify empty weather detection."""
        weather = ConceptualWeather()
        assert weather.is_empty is True
        assert len(weather.all_patterns) == 0

    def test_conceptual_weather_with_patterns(self) -> None:
        """Verify weather with patterns."""
        pattern = WeatherPattern(
            type=WeatherType.SCAFFOLDING,
            label="ASHC",
            description="Compiler architecture",
        )
        weather = ConceptualWeather(scaffolding=(pattern,))
        assert weather.is_empty is False
        assert len(weather.all_patterns) == 1


# =============================================================================
# ChallengeMenu Tests
# =============================================================================


class TestChallengeMenu:
    """Tests for Menu types."""

    def test_menu_item_frozen(self) -> None:
        """Verify MenuItem is immutable."""
        item = MenuItem(
            label="Write test",
            description="Low stakes",
            level=ChallengeLevel.GENTLE,
        )
        with pytest.raises(AttributeError):
            item.label = "changed"  # type: ignore

    def test_menu_item_to_dict(self) -> None:
        """Verify MenuItem serialization."""
        item = MenuItem(
            label="Implement feature",
            description="Core work",
            level=ChallengeLevel.FOCUSED,
            agentese_path="self.brain.capture",
        )
        data = item.to_dict()
        assert data["label"] == "Implement feature"
        assert data["level"] == "focused"
        assert data["level_emoji"] == "🎯"

    def test_challenge_menu_empty(self) -> None:
        """Verify empty menu detection (serendipity always available)."""
        menu = ChallengeMenu()
        assert menu.is_empty is True
        assert menu.serendipitous_prompt  # Always has a prompt

    def test_challenge_menu_get_items_by_level(self) -> None:
        """Verify getting items by level."""
        gentle_item = MenuItem(label="Test", description="Easy", level=ChallengeLevel.GENTLE)
        menu = ChallengeMenu(gentle=(gentle_item,))
        assert len(menu.get_items_by_level(ChallengeLevel.GENTLE)) == 1
        assert len(menu.get_items_by_level(ChallengeLevel.INTENSE)) == 0


# =============================================================================
# MorningVoice Tests
# =============================================================================


class TestMorningVoice:
    """Tests for Voice types."""

    def test_morning_voice_frozen(self) -> None:
        """Verify MorningVoice is immutable."""
        voice = MorningVoice(captured_date=date.today())
        with pytest.raises(AttributeError):
            voice.success_criteria = "changed"  # type: ignore

    def test_morning_voice_not_substantive_when_empty(self) -> None:
        """Verify empty voice is not substantive."""
        voice = MorningVoice(captured_date=date.today())
        assert voice.is_substantive is False

    def test_morning_voice_substantive_with_content(self) -> None:
        """Verify voice with content is substantive."""
        voice = MorningVoice(
            captured_date=date.today(),
            success_criteria="Ship one feature",
        )
        assert voice.is_substantive is True

    def test_morning_voice_to_dict(self) -> None:
        """Verify MorningVoice serialization."""
        voice = MorningVoice(
            captured_date=date(2025, 12, 21),
            non_code_thought="Thinking about music",
            success_criteria="Feel flow",
            chosen_challenge=ChallengeLevel.FOCUSED,
        )
        data = voice.to_dict()
        assert data["captured_date"] == "2025-12-21"
        assert data["non_code_thought"] == "Thinking about music"
        assert data["chosen_challenge"] == "focused"

    def test_morning_voice_from_dict(self) -> None:
        """Verify MorningVoice deserialization."""
        data = {
            "captured_date": "2025-12-21",
            "success_criteria": "Ship it",
            "chosen_challenge": "intense",
        }
        voice = MorningVoice.from_dict(data)
        assert voice.captured_date == date(2025, 12, 21)
        assert voice.success_criteria == "Ship it"
        assert voice.chosen_challenge == ChallengeLevel.INTENSE

    def test_morning_voice_as_voice_anchor(self) -> None:
        """Verify voice anchor conversion."""
        voice = MorningVoice(
            captured_date=date.today(),
            success_criteria="Feel productive",
        )
        anchor = voice.as_voice_anchor()
        assert anchor is not None
        assert anchor["text"] == "Feel productive"
        assert anchor["source"] == "morning_coffee"

    def test_morning_voice_no_anchor_without_criteria(self) -> None:
        """Verify no anchor without success criteria."""
        voice = MorningVoice(
            captured_date=date.today(),
            non_code_thought="Just thinking",
        )
        anchor = voice.as_voice_anchor()
        assert anchor is None


# =============================================================================
# RitualEvent and CoffeeOutput Tests
# =============================================================================


class TestRitualEvent:
    """Tests for RitualEvent."""

    def test_ritual_event_frozen(self) -> None:
        """Verify RitualEvent is immutable."""
        event = RitualEvent(command="wake")
        with pytest.raises(AttributeError):
            event.command = "changed"  # type: ignore

    def test_ritual_event_to_dict(self) -> None:
        """Verify RitualEvent serialization."""
        event = RitualEvent(command="continue", data={"key": "value"})
        data = event.to_dict()
        assert data["command"] == "continue"
        assert data["data"]["key"] == "value"


class TestCoffeeOutput:
    """Tests for CoffeeOutput."""

    def test_coffee_output_frozen(self) -> None:
        """Verify CoffeeOutput is immutable."""
        output = CoffeeOutput(status="ok", state=CoffeeState.GARDEN)
        with pytest.raises(AttributeError):
            output.status = "changed"  # type: ignore

    def test_coffee_output_to_dict(self) -> None:
        """Verify CoffeeOutput serialization."""
        output = CoffeeOutput(
            status="ok",
            state=CoffeeState.GARDEN,
            movement=MOVEMENTS["garden"],
            message="Hello",
        )
        data = output.to_dict()
        assert data["status"] == "ok"
        assert data["state"] == "GARDEN"
        assert data["movement"]["name"] == "Garden View"
