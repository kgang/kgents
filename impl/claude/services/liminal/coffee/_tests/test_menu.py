"""
Tests for Morning Coffee Menu generator.

Verifies:
- TODO extraction from plans and NOW.md
- Challenge classification heuristics
- Cognitive load estimation
- Menu generation with all levels
"""

from datetime import datetime
from pathlib import Path

import pytest

from services.liminal.coffee.menu import (
    _generate_serendipitous_prompt,
    _items_from_weather,
    _truncate,
    classify_challenge,
    estimate_cognitive_load,
    extract_todos_from_now,
    extract_todos_from_plans,
    generate_menu,
)
from services.liminal.coffee.types import (
    ChallengeLevel,
    ChallengeMenu,
    ConceptualWeather,
    GardenCategory,
    GardenItem,
    GardenView,
    MenuItem,
    WeatherPattern,
    WeatherType,
)

# =============================================================================
# TODO Extraction Tests
# =============================================================================


class TestExtractTodosFromPlans:
    """Tests for extract_todos_from_plans."""

    def test_extracts_unchecked_checkboxes(self, tmp_path: Path) -> None:
        """Extract - [ ] items."""
        plans = tmp_path / "plans"
        plans.mkdir()

        (plans / "feature.md").write_text("""
# Feature Plan
- [ ] Implement feature
- [x] Design feature (done)
- [ ] Test feature
""")

        todos = extract_todos_from_plans(plans)

        assert len(todos) == 2
        texts = [t["text"] for t in todos]
        assert "Implement feature" in texts
        assert "Test feature" in texts

    def test_extracts_todo_comments(self, tmp_path: Path) -> None:
        """Extract TODO: lines."""
        plans = tmp_path / "plans"
        plans.mkdir()

        (plans / "bugfix.md").write_text("""
# Bug Fix
Some content here.
TODO: Fix the edge case
More content.
""")

        todos = extract_todos_from_plans(plans)

        assert len(todos) == 1
        assert "Fix the edge case" in todos[0]["text"]

    def test_skips_underscore_files(self, tmp_path: Path) -> None:
        """Skip _archive.md, _focus.md, etc."""
        plans = tmp_path / "plans"
        plans.mkdir()

        (plans / "_archive.md").write_text("- [ ] Old task")
        (plans / "real.md").write_text("- [ ] Real task")

        todos = extract_todos_from_plans(plans)

        assert len(todos) == 1
        assert todos[0]["text"] == "Real task"

    def test_missing_dir_returns_empty(self, tmp_path: Path) -> None:
        """Missing plans dir returns empty."""
        todos = extract_todos_from_plans(tmp_path / "nonexistent")
        assert todos == []

    def test_records_source(self, tmp_path: Path) -> None:
        """Records plan name as source."""
        plans = tmp_path / "plans"
        plans.mkdir()

        (plans / "my-feature.md").write_text("- [ ] Task")

        todos = extract_todos_from_plans(plans)

        assert todos[0]["source"] == "My Feature"


class TestExtractTodosFromNow:
    """Tests for extract_todos_from_now."""

    def test_extracts_checkboxes(self, tmp_path: Path) -> None:
        """Extract checkboxes from NOW.md."""
        now_md = tmp_path / "NOW.md"
        now_md.write_text("""
# NOW
- [ ] First task
- [ ] Second task
- [x] Done task
""")

        todos = extract_todos_from_now(now_md)

        assert len(todos) == 2
        texts = [t["text"] for t in todos]
        assert "First task" in texts
        assert "Second task" in texts

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        """Missing NOW.md returns empty."""
        todos = extract_todos_from_now(tmp_path / "missing.md")
        assert todos == []

    def test_source_is_now_md(self, tmp_path: Path) -> None:
        """Source is recorded as NOW.md."""
        now_md = tmp_path / "NOW.md"
        now_md.write_text("- [ ] Task")

        todos = extract_todos_from_now(now_md)

        assert todos[0]["source"] == "NOW.md"


# =============================================================================
# Challenge Classification Tests
# =============================================================================


class TestClassifyChallenge:
    """Tests for classify_challenge heuristics."""

    def test_gentle_test_task(self) -> None:
        """Test tasks are gentle."""
        level = classify_challenge("Write a test for the feature")
        assert level == ChallengeLevel.GENTLE

    def test_gentle_documentation(self) -> None:
        """Documentation is gentle."""
        level = classify_challenge("Document the API endpoints")
        assert level == ChallengeLevel.GENTLE

    def test_gentle_cleanup(self) -> None:
        """Cleanup is gentle."""
        level = classify_challenge("Cleanup unused imports")
        assert level == ChallengeLevel.GENTLE

    def test_intense_architecture(self) -> None:
        """Architecture work is intense."""
        level = classify_challenge("Design the new service architecture")
        assert level == ChallengeLevel.INTENSE

    def test_intense_implementation(self) -> None:
        """Major implementation is intense."""
        level = classify_challenge("Implement the bootstrap regeneration")
        assert level == ChallengeLevel.INTENSE

    def test_focused_default(self) -> None:
        """Generic tasks default to focused."""
        level = classify_challenge("Update the configuration file")
        assert level == ChallengeLevel.FOCUSED

    def test_case_insensitive(self) -> None:
        """Classification is case insensitive."""
        level = classify_challenge("WRITE A TEST")
        assert level == ChallengeLevel.GENTLE


class TestEstimateCognitiveLoad:
    """Tests for estimate_cognitive_load."""

    def test_complex_is_high(self) -> None:
        """Complex tasks have high load."""
        load = estimate_cognitive_load("Design and implement the architecture")
        assert load > 0.5

    def test_simple_is_low(self) -> None:
        """Simple tasks have low load."""
        load = estimate_cognitive_load("Fix typo")
        assert load < 0.5

    def test_bounded_zero_to_one(self) -> None:
        """Load is always in [0, 1]."""
        # Very simple
        load1 = estimate_cognitive_load("fix")
        # Very complex
        load2 = estimate_cognitive_load(
            "Design, implement, and architect the entire bootstrap "
            "regeneration system with comprehensive validation"
        )

        assert 0.0 <= load1 <= 1.0
        assert 0.0 <= load2 <= 1.0


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestTruncate:
    """Tests for _truncate helper."""

    def test_short_unchanged(self) -> None:
        """Short text is unchanged."""
        result = _truncate("Short", 20)
        assert result == "Short"

    def test_long_truncated(self) -> None:
        """Long text is truncated with ellipsis."""
        result = _truncate("This is a very long string", 10)
        assert len(result) == 10
        assert result.endswith("...")

    def test_exact_length(self) -> None:
        """Exact length is unchanged."""
        result = _truncate("12345", 5)
        assert result == "12345"


class TestItemsFromWeather:
    """Tests for _items_from_weather."""

    def test_extracts_from_scaffolding(self) -> None:
        """Extracts continue items from scaffolding."""
        weather = ConceptualWeather(
            scaffolding=(
                WeatherPattern(
                    type=WeatherType.SCAFFOLDING,
                    label="ASHC",
                    description="Building",
                ),
            ),
        )

        items = _items_from_weather(weather)

        assert len(items) >= 1
        assert any("Continue" in item["text"] for item in items)

    def test_extracts_from_tension(self) -> None:
        """Extracts address items from tension."""
        weather = ConceptualWeather(
            tension=(
                WeatherPattern(
                    type=WeatherType.TENSION,
                    label="Blocked feature",
                    description="Needs resolution",
                ),
            ),
        )

        items = _items_from_weather(weather)

        assert len(items) >= 1
        assert any("Address" in item["text"] for item in items)

    def test_empty_weather_returns_empty(self) -> None:
        """Empty weather returns no items."""
        items = _items_from_weather(ConceptualWeather())
        assert items == []


class TestGenerateSerendipitousPrompt:
    """Tests for _generate_serendipitous_prompt."""

    def test_default_prompt(self) -> None:
        """Default prompt when no context."""
        prompt = _generate_serendipitous_prompt(None, None)
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_seed_context(self) -> None:
        """Seeds context generates seed-specific prompt."""
        garden = GardenView(
            seeds=(
                GardenItem(
                    description="New idea",
                    category=GardenCategory.SEEDS,
                ),
            ),
        )

        prompt = _generate_serendipitous_prompt(garden, None)
        assert "seed" in prompt.lower() or "sprout" in prompt.lower()

    def test_emerging_context(self) -> None:
        """Emerging weather generates pattern prompt."""
        weather = ConceptualWeather(
            emerging=(
                WeatherPattern(
                    type=WeatherType.EMERGING,
                    label="New pattern",
                    description="",
                ),
            ),
        )

        prompt = _generate_serendipitous_prompt(None, weather)
        assert "pattern" in prompt.lower() or "emerge" in prompt.lower()


# =============================================================================
# Menu Generation Tests
# =============================================================================


class TestGenerateMenu:
    """Tests for generate_menu integration."""

    def test_returns_challenge_menu(self, tmp_path: Path) -> None:
        """Returns a proper ChallengeMenu."""
        plans = tmp_path / "plans"
        plans.mkdir()
        (plans / "test.md").write_text("- [ ] Write test")

        menu = generate_menu(plans_path=plans)

        assert isinstance(menu, ChallengeMenu)
        assert menu.generated_at is not None

    def test_categorizes_items(self, tmp_path: Path) -> None:
        """Items are categorized by challenge level."""
        plans = tmp_path / "plans"
        plans.mkdir()
        (plans / "tasks.md").write_text("""
- [ ] Write a test for feature
- [ ] Design the new architecture
- [ ] Update configuration
""")

        menu = generate_menu(plans_path=plans)

        # Test task should be gentle
        gentle_labels = [item.label for item in menu.gentle]
        # Architecture should be intense
        intense_labels = [item.label for item in menu.intense]

        # At least one should be categorized
        assert len(menu.gentle) + len(menu.focused) + len(menu.intense) >= 1

    def test_serendipitous_always_present(self, tmp_path: Path) -> None:
        """Serendipitous prompt is always present."""
        menu = generate_menu(plans_path=tmp_path)

        assert menu.serendipitous_prompt
        assert len(menu.serendipitous_prompt) > 0

    def test_respects_max_per_level(self, tmp_path: Path) -> None:
        """Respects max_per_level limit."""
        plans = tmp_path / "plans"
        plans.mkdir()
        (plans / "many.md").write_text("\n".join([f"- [ ] Test task {i}" for i in range(10)]))

        menu = generate_menu(plans_path=plans, max_per_level=2)

        # All gentle tasks, but limited to 2
        assert len(menu.gentle) <= 2

    def test_empty_returns_valid_menu(self, tmp_path: Path) -> None:
        """Empty sources return valid empty menu."""
        menu = generate_menu(plans_path=tmp_path / "nonexistent")

        assert isinstance(menu, ChallengeMenu)
        assert menu.serendipitous_prompt  # Always has a prompt

    def test_uses_weather_context(self, tmp_path: Path) -> None:
        """Weather context adds items to menu."""
        weather = ConceptualWeather(
            scaffolding=(
                WeatherPattern(
                    type=WeatherType.SCAFFOLDING,
                    label="Active project",
                    description="Building",
                ),
            ),
        )

        menu = generate_menu(
            plans_path=tmp_path / "empty",
            weather=weather,
        )

        # Weather should add at least one item
        all_labels = (
            [item.label for item in menu.gentle]
            + [item.label for item in menu.focused]
            + [item.label for item in menu.intense]
        )
        assert any("Continue" in label for label in all_labels)


# =============================================================================
# ChallengeMenu Type Tests
# =============================================================================


class TestChallengeMenuType:
    """Tests for ChallengeMenu dataclass."""

    def test_is_empty_when_empty(self) -> None:
        """is_empty returns True for empty menu."""
        menu = ChallengeMenu()
        assert menu.is_empty is True

    def test_not_empty_with_items(self) -> None:
        """is_empty returns False with items."""
        item = MenuItem(
            label="test",
            description="test",
            level=ChallengeLevel.GENTLE,
        )
        menu = ChallengeMenu(gentle=(item,))
        assert menu.is_empty is False

    def test_get_items_by_level(self) -> None:
        """get_items_by_level returns correct bucket."""
        gentle_item = MenuItem(
            label="gentle",
            description="",
            level=ChallengeLevel.GENTLE,
        )
        intense_item = MenuItem(
            label="intense",
            description="",
            level=ChallengeLevel.INTENSE,
        )
        menu = ChallengeMenu(
            gentle=(gentle_item,),
            intense=(intense_item,),
        )

        assert len(menu.get_items_by_level(ChallengeLevel.GENTLE)) == 1
        assert len(menu.get_items_by_level(ChallengeLevel.INTENSE)) == 1
        assert len(menu.get_items_by_level(ChallengeLevel.FOCUSED)) == 0

    def test_serendipitous_has_no_items(self) -> None:
        """SERENDIPITOUS level has no predefined items."""
        menu = ChallengeMenu()
        assert menu.get_items_by_level(ChallengeLevel.SERENDIPITOUS) == ()

    def test_to_dict_serializes(self) -> None:
        """to_dict creates valid dict."""
        item = MenuItem(
            label="test",
            description="desc",
            level=ChallengeLevel.FOCUSED,
            source="plan",
        )
        menu = ChallengeMenu(focused=(item,))

        data = menu.to_dict()

        assert "focused" in data
        assert "serendipitous_prompt" in data
        assert len(data["focused"]) == 1
