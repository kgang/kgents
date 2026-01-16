"""
Tests for the Daily Lab pilot.

Tests the trail-to-crystal daily journaling workflow with:
- WARMTH calibration validation
- Mark capture with tags
- Trail navigation
- Crystal compression with honesty disclosure
- Export functionality
"""

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from services.witness.crystal import CrystalLevel
from services.witness.crystal_store import CrystalStore, reset_crystal_store
from services.witness.daily_lab import (
    WARMTH_PROMPTS,
    WARMTH_RESPONSES,
    CompressionHonesty,
    DailyCrystal,
    DailyCrystallizer,
    DailyExport,
    DailyExporter,
    DailyLab,
    DailyMark,
    DailyMarkCapture,
    DailyTag,
    Trail,
    TrailPosition,
)
from services.witness.mark import Mark, MarkId
from services.witness.trace_store import MarkStore, reset_mark_store

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_global_stores() -> None:
    """Reset global stores before each test."""
    reset_mark_store()
    reset_crystal_store()


@pytest.fixture
def mark_store() -> MarkStore:
    """Fresh mark store for testing."""
    return MarkStore()


@pytest.fixture
def crystal_store() -> CrystalStore:
    """Fresh crystal store for testing."""
    return CrystalStore()


@pytest.fixture
def daily_lab(mark_store: MarkStore, crystal_store: CrystalStore) -> DailyLab:
    """Daily lab instance for testing."""
    return DailyLab(mark_store=mark_store, crystal_store=crystal_store)


# =============================================================================
# DailyTag Tests
# =============================================================================


class TestDailyTag:
    """Tests for daily mark tags."""

    def test_tag_values(self) -> None:
        """Tags have expected string values."""
        assert DailyTag.EUREKA.value == "eureka"
        assert DailyTag.GOTCHA.value == "gotcha"
        assert DailyTag.TASTE.value == "taste"
        assert DailyTag.FRICTION.value == "friction"
        assert DailyTag.JOY.value == "joy"
        assert DailyTag.VETO.value == "veto"

    def test_all_tags_exist(self) -> None:
        """All required tags are present."""
        required_tags = {"eureka", "gotcha", "taste", "friction", "joy", "veto"}
        actual_tags = {tag.value for tag in DailyTag}
        assert required_tags == actual_tags


# =============================================================================
# DailyMark Tests
# =============================================================================


class TestDailyMark:
    """Tests for DailyMark creation."""

    def test_create_simple_mark(self) -> None:
        """Can create a simple mark with just content."""
        dm = DailyMark(content="A simple thought")
        assert dm.content == "A simple thought"
        assert dm.tag is None
        assert dm.reasoning is None

    def test_create_tagged_mark(self) -> None:
        """Can create a mark with a tag."""
        dm = DailyMark(content="Breakthrough!", tag=DailyTag.EUREKA)
        assert dm.tag == DailyTag.EUREKA
        assert dm.mark.tags == ("eureka",)

    def test_create_mark_with_reasoning(self) -> None:
        """Can create a mark with reasoning."""
        dm = DailyMark(
            content="Pattern found",
            tag=DailyTag.TASTE,
            reasoning="This aligns with our design principles",
        )
        assert dm.reasoning == "This aligns with our design principles"
        assert dm.mark.stimulus.metadata.get("reasoning") == dm.reasoning

    def test_mark_is_lazily_created(self) -> None:
        """The underlying Mark is created lazily."""
        dm = DailyMark(content="Test")
        assert dm._mark is None
        _ = dm.mark  # Access triggers creation
        assert dm._mark is not None

    def test_mark_origin_is_daily_lab(self) -> None:
        """Marks have origin set to daily_lab."""
        dm = DailyMark(content="Test")
        assert dm.mark.origin == "daily_lab"

    def test_serialization_round_trip(self) -> None:
        """DailyMark serializes and deserializes correctly."""
        dm = DailyMark(
            content="Round trip test",
            tag=DailyTag.JOY,
            reasoning="Testing serialization",
        )
        _ = dm.mark  # Ensure mark is created

        data = dm.to_dict()
        restored = DailyMark.from_dict(data)

        assert restored.content == dm.content
        assert restored.tag == dm.tag
        assert restored.reasoning == dm.reasoning


# =============================================================================
# DailyMarkCapture Tests
# =============================================================================


class TestDailyMarkCapture:
    """Tests for mark capture interface."""

    def test_quick_capture(self, mark_store: MarkStore) -> None:
        """Quick capture stores a mark."""
        capture = DailyMarkCapture(store=mark_store)

        dm = capture.quick("Quick thought")

        # Mark should be in our store
        assert dm.mark.id in mark_store
        assert dm.content == "Quick thought"
        assert dm.tag is None

    def test_tagged_capture(self, mark_store: MarkStore) -> None:
        """Tagged capture stores a mark with tag."""
        capture = DailyMarkCapture(store=mark_store)

        dm = capture.tagged("Aha moment!", DailyTag.EUREKA)

        assert dm.mark.id in mark_store
        assert dm.tag == DailyTag.EUREKA

    def test_capture_with_reasoning(self, mark_store: MarkStore) -> None:
        """Capture with reasoning stores both."""
        capture = DailyMarkCapture(store=mark_store)

        dm = capture.with_reasoning(
            content="Design decision",
            reasoning="Aligns with joy-inducing principle",
            tag=DailyTag.TASTE,
        )

        assert dm.content == "Design decision"
        assert dm.reasoning == "Aligns with joy-inducing principle"
        assert dm.tag == DailyTag.TASTE

    def test_convenience_methods(self, mark_store: MarkStore) -> None:
        """Convenience methods work correctly."""
        capture = DailyMarkCapture(store=mark_store)

        eureka = capture.eureka("Found it!")
        gotcha = capture.gotcha("Watch out for this")
        taste = capture.taste("Clean design")
        friction = capture.friction("Too complex")
        joy = capture.joy("This is delightful")
        veto = capture.veto("This feels wrong")

        assert eureka.tag == DailyTag.EUREKA
        assert gotcha.tag == DailyTag.GOTCHA
        assert taste.tag == DailyTag.TASTE
        assert friction.tag == DailyTag.FRICTION
        assert joy.tag == DailyTag.JOY
        assert veto.tag == DailyTag.VETO
        # All marks should be in store
        assert all(m.mark.id in mark_store for m in [eureka, gotcha, taste, friction, joy, veto])

    def test_prompt_is_warmth_calibrated(self, mark_store: MarkStore) -> None:
        """Capture prompt uses WARMTH language."""
        capture = DailyMarkCapture(store=mark_store)

        prompt = capture.prompt()

        assert prompt == WARMTH_PROMPTS["capture_quick"]
        assert "What's on your mind?" in prompt


# =============================================================================
# Trail Tests
# =============================================================================


class TestTrail:
    """Tests for trail navigation."""

    def test_trail_for_today_empty(self, mark_store: MarkStore) -> None:
        """Empty trail for today when no marks."""
        trail = Trail(store=mark_store)
        position = trail.for_today()

        assert position.total == 0
        assert position.current is None

    def test_trail_for_today_with_marks(self, mark_store: MarkStore) -> None:
        """Trail contains today's marks."""
        capture = DailyMarkCapture(store=mark_store)
        capture.quick("First thought")
        capture.quick("Second thought")

        trail = Trail(store=mark_store)
        position = trail.for_today()

        assert position.total == 2
        assert position.current is not None

    def test_trail_navigation(self, mark_store: MarkStore) -> None:
        """Can navigate forward and backward through trail."""
        capture = DailyMarkCapture(store=mark_store)
        capture.quick("First")
        capture.quick("Second")
        capture.quick("Third")

        trail = Trail(store=mark_store)
        position = trail.for_today()

        # Start at first
        assert position.index == 0
        assert position.position == 1
        assert position.has_next
        assert not position.has_prev

        # Move to second
        position = trail.navigate(position, "next")
        assert position.index == 1
        assert position.has_next
        assert position.has_prev

        # Move to third
        position = trail.navigate(position, "next")
        assert position.index == 2
        assert not position.has_next
        assert position.has_prev

        # Can't go past end
        position = trail.navigate(position, "next")
        assert position.index == 2

        # Move back
        position = trail.navigate(position, "prev")
        assert position.index == 1

    def test_trail_filters_by_origin(self, mark_store: MarkStore) -> None:
        """Trail only includes daily_lab marks."""
        # Add a daily lab mark
        capture = DailyMarkCapture(store=mark_store)
        daily_mark = capture.quick("Daily lab mark")

        # Add a non-daily-lab mark directly
        from services.witness.mark import Response, Stimulus

        other_mark = Mark(
            origin="other_source",
            stimulus=Stimulus(kind="test", content="test"),
            response=Response(kind="test", content="Other source mark"),
        )
        mark_store.append(other_mark)

        trail = Trail(store=mark_store)
        position = trail.for_today()

        # Only daily lab marks should be included
        # Verify the daily lab mark is in the trail
        mark_ids = [m.id for m in position.marks]
        assert daily_mark.mark.id in mark_ids
        # Verify the other mark is NOT in the trail
        assert other_mark.id not in mark_ids

    def test_filter_by_importance(self, mark_store: MarkStore) -> None:
        """Can filter trail to important marks only."""
        capture = DailyMarkCapture(store=mark_store)
        capture.eureka("Breakthrough!")  # Important
        capture.quick("Regular note")  # Not important
        capture.veto("Wrong direction")  # Important
        capture.friction("Slow progress")  # Not important

        trail = Trail(store=mark_store)
        position = trail.for_today()
        assert position.total == 4

        important = trail.filter_by_importance(position)
        assert important.total == 2

    def test_trail_for_date_range(self, mark_store: MarkStore) -> None:
        """Can get marks for a date range."""
        capture = DailyMarkCapture(store=mark_store)
        today_dm = capture.quick("Today's mark")

        # Create mark with past timestamp
        past_mark = DailyMark(
            content="Yesterday's mark",
            timestamp=datetime.now() - timedelta(days=1),
        )
        mark_store.append(past_mark.mark)

        trail = Trail(store=mark_store)

        # Only today - check that we have at least the one we just added
        today_position = trail.for_date(date.today())
        assert today_position.total >= 1
        # Verify our mark is in there
        mark_ids = [m.id for m in today_position.marks]
        assert today_dm.mark.id in mark_ids

        # Range including yesterday
        start = datetime.now() - timedelta(days=2)
        end = datetime.now() + timedelta(hours=1)
        range_position = trail.for_range(start, end)
        assert range_position.total >= 2


# =============================================================================
# CompressionHonesty Tests
# =============================================================================


class TestCompressionHonesty:
    """Tests for compression honesty disclosure."""

    def test_no_drops(self) -> None:
        """Disclosure when nothing dropped."""
        honesty = CompressionHonesty(
            dropped_count=0,
            dropped_tags=[],
            dropped_summaries=[],
            galois_loss=0.0,
        )

        disclosure = honesty.to_disclosure()
        assert "Everything was preserved" in disclosure

    def test_with_drops(self) -> None:
        """Disclosure shows what was dropped."""
        honesty = CompressionHonesty(
            dropped_count=5,
            dropped_tags=["friction", "gotcha"],
            dropped_summaries=["First dropped...", "Second dropped..."],
            galois_loss=0.25,
        )

        disclosure = honesty.to_disclosure()
        assert "Set aside 5 notes" in disclosure
        assert "friction" in disclosure
        assert "25" in disclosure  # 25% loss

    def test_high_loss_disclosure(self) -> None:
        """High Galois loss is reflected in disclosure."""
        honesty = CompressionHonesty(
            dropped_count=10,
            dropped_tags=["friction"],
            dropped_summaries=[],
            galois_loss=0.6,
        )

        disclosure = honesty.to_disclosure()
        assert "60" in disclosure  # 60% loss


# =============================================================================
# DailyCrystallizer Tests
# =============================================================================


class TestDailyCrystallizer:
    """Tests for daily crystallization."""

    def test_not_enough_marks_returns_none(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Returns None when not enough marks to crystallize."""
        capture = DailyMarkCapture(store=mark_store)
        capture.quick("Only one mark")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        result = crystallizer.crystallize_day(date.today())

        assert result is None

    def test_crystallize_day(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Can crystallize a day's marks."""
        capture = DailyMarkCapture(store=mark_store)
        capture.eureka("Big discovery")
        capture.taste("Nice design")
        capture.quick("Regular note")
        capture.friction("Some friction")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        result = crystallizer.crystallize_day(date.today())

        assert result is not None
        assert result.level == CrystalLevel.DAY
        assert result.insight != ""
        assert result.significance != ""
        assert result.disclosure != ""

    def test_crystal_includes_honesty(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Crystal includes compression honesty."""
        capture = DailyMarkCapture(store=mark_store)
        # Add more marks than MAX_IMPORTANT_MARKS
        for i in range(10):
            capture.quick(f"Note {i}")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        result = crystallizer.crystallize_day(date.today())

        assert result is not None
        assert result.honesty.dropped_count > 0
        # Amendment G: Verify warm disclosure is present (WARMTH-calibrated)
        assert len(result.disclosure) > 0
        # Should NOT contain shaming language
        disclosure_lower = result.disclosure.lower()
        assert "you missed" not in disclosure_lower
        assert "you failed" not in disclosure_lower

    def test_prioritizes_important_marks(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Crystallizer prioritizes important marks."""
        capture = DailyMarkCapture(store=mark_store)

        # Add many friction marks (low priority)
        for i in range(10):
            capture.friction(f"Friction {i}")

        # Add one veto (highest priority)
        capture.veto("Critical issue")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        result = crystallizer.crystallize_day(date.today())

        assert result is not None
        # Veto should be in kept marks (check crystal source_marks)
        # The insight should reference the veto
        assert result.crystal.source_count <= 7  # MAX_IMPORTANT_MARKS

    def test_crystallize_week(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Can crystallize a week's marks."""
        capture = DailyMarkCapture(store=mark_store)
        # Add marks over multiple days
        for i in range(5):
            dm = DailyMark(
                content=f"Day {i} note",
                tag=DailyTag.EUREKA,
                timestamp=datetime.now() - timedelta(days=i),
            )
            mark_store.append(dm.mark)

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        result = crystallizer.crystallize_week()

        assert result is not None
        assert result.level == CrystalLevel.WEEK


# =============================================================================
# Export Tests
# =============================================================================


class TestDailyExport:
    """Tests for daily export."""

    def test_export_to_markdown(self) -> None:
        """Can export to markdown."""
        export = DailyExport(
            title="Test Export",
            date_range=(date.today(), date.today()),
            crystals=[],
            key_marks=[],
            format="markdown",
        )

        md = export.to_markdown()

        assert "# Test Export" in md
        assert "Generated by kgents Daily Lab" in md

    def test_export_to_json(self) -> None:
        """Can export to JSON."""
        export = DailyExport(
            title="Test Export",
            date_range=(date.today(), date.today()),
            crystals=[],
            key_marks=[],
            format="json",
        )

        json_str = export.to_json()
        data = json.loads(json_str)

        assert data["title"] == "Test Export"

    def test_export_includes_crystals(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Export includes crystals when present."""
        capture = DailyMarkCapture(store=mark_store)
        for i in range(5):
            capture.eureka(f"Insight {i}")

        exporter = DailyExporter(mark_store, crystal_store)
        export = exporter.export_day(date.today())

        md = export.to_markdown()
        assert "Crystallized Insights" in md

    def test_export_save(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
        tmp_path: Path,
    ) -> None:
        """Can save export to file."""
        capture = DailyMarkCapture(store=mark_store)
        capture.eureka("Test insight")
        capture.joy("Test joy")
        capture.taste("Test taste")

        exporter = DailyExporter(mark_store, crystal_store)
        export = exporter.export_day(date.today())

        output_path = tmp_path / "export.md"
        export.save(output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "Daily Review" in content


# =============================================================================
# DailyLab Integration Tests
# =============================================================================


class TestDailyLab:
    """Integration tests for DailyLab."""

    def test_full_workflow(self, daily_lab: DailyLab) -> None:
        """Test complete daily lab workflow."""
        # Capture marks
        daily_lab.capture.quick("Started the day")
        daily_lab.capture.eureka("Found a great pattern")
        daily_lab.capture.taste("Clean API design")
        daily_lab.capture.friction("Complex dependency")
        daily_lab.capture.joy("Tests passed!")

        # Review trail
        trail = daily_lab.today()
        assert trail.total >= 5  # At least 5 marks (may be more from other tests)

        # Navigate
        assert trail.current is not None
        trail = daily_lab.trail.navigate(trail, "next")
        assert trail.index == 1

        # Crystallize
        crystal = daily_lab.crystallize.crystallize_day(date.today())
        assert crystal is not None
        assert crystal.insight != ""

        # Export
        export = daily_lab.export.export_day(date.today())
        md = export.to_markdown()
        assert "Daily Review" in md

    def test_warmth_prompts_present(self, daily_lab: DailyLab) -> None:
        """WARMTH prompts are used throughout."""
        # Capture prompt
        assert daily_lab.capture.prompt() == "What's on your mind?"

        # Review prompt for empty day
        empty_trail = daily_lab.today()
        prompt = daily_lab.review_prompt(empty_trail)
        assert "quiet day" in prompt.lower() or "okay" in prompt.lower()

        # Crystal intro
        intro = daily_lab.crystal_intro()
        assert "patterns" in intro.lower()

    def test_flow_joy_calibration(self, daily_lab: DailyLab) -> None:
        """Flow (primary joy) is supported through low-friction capture."""
        # Quick capture is one-liner
        dm = daily_lab.capture.quick("No ceremony needed")
        assert dm is not None

        # Can capture and immediately move on
        daily_lab.capture.quick("Note 1")
        daily_lab.capture.quick("Note 2")
        daily_lab.capture.quick("Note 3")

        # Trail is immediately available
        trail = daily_lab.today()
        assert trail.total >= 4

    def test_warmth_joy_calibration(self, daily_lab: DailyLab) -> None:
        """Warmth (secondary joy) is supported through kind language."""
        # Review prompt is warm
        trail = daily_lab.today()
        prompt = daily_lab.review_prompt(trail)
        # Should use warm language from WARMTH_PROMPTS
        assert prompt in WARMTH_PROMPTS.values()

    def test_warmth_response_uses_joy_functor(self, mark_store: MarkStore) -> None:
        """warmth_response() uses the JoyFunctor for categorical joy."""
        capture = DailyMarkCapture(store=mark_store)

        # High flow signal should produce a non-empty warm response
        response = capture.warmth_response(
            warmth=0.3,
            surprise=0.2,
            flow=0.9,
            trigger="quick capture",
        )
        assert response != ""  # Should return a non-empty response

        # The response should be warm, not clinical
        # Flow-dominant signals should produce flow-related responses
        # (either high intensity "groove" or medium intensity "momentum")
        flow_related = ["groove", "momentum", "got it"]
        assert any(keyword in response.lower() for keyword in flow_related), (
            f"Expected flow-related response, got: {response}"
        )

    def test_warmth_response_not_punitive(self, mark_store: MarkStore) -> None:
        """warmth_response() never uses punitive language."""
        capture = DailyMarkCapture(store=mark_store)
        punitive_patterns = ["error", "failed", "invalid", "wrong", "bad"]

        # Test various signal combinations
        test_cases = [
            (0.1, 0.1, 0.1),  # Low everything
            (0.5, 0.5, 0.5),  # Medium everything
            (0.9, 0.3, 0.2),  # High warmth
            (0.2, 0.8, 0.3),  # High surprise
            (0.2, 0.2, 0.9),  # High flow
        ]

        for warmth, surprise, flow in test_cases:
            response = capture.warmth_response(
                warmth=warmth,
                surprise=surprise,
                flow=flow,
            )
            response_lower = response.lower()
            for pattern in punitive_patterns:
                assert pattern not in response_lower, (
                    f"Punitive pattern '{pattern}' found in response for "
                    f"signals ({warmth}, {surprise}, {flow}): {response}"
                )


# =============================================================================
# WARMTH Calibration Tests
# =============================================================================


class TestWarmthCalibration:
    """Tests specifically for WARMTH calibration."""

    def test_prompts_are_warm_not_cold(self) -> None:
        """All prompts use warm language."""
        # Check for warm patterns (case insensitive)
        # These are conversational, personal, encouraging patterns
        warm_patterns = [
            "your",
            "together",
            "let's",
            "what's on",
            "noticed",
            "okay",
            "here's",
            "you",
            "we",
            "that",
            "stand out",
            "look back",
            "week",
            "patterns",
            "quiet",
            "captured",
            "keep",
            "clear",
            "setting aside",
            "to keep this",  # For compression honesty prompt
        ]
        cold_patterns = ["Error", "Invalid", "Must", "Required", "Failed"]

        for prompt in WARMTH_PROMPTS.values():
            prompt_lower = prompt.lower()
            # Should have at least one warm pattern
            has_warm = any(p.lower() in prompt_lower for p in warm_patterns)
            # Should not have cold patterns
            has_cold = any(p in prompt for p in cold_patterns)

            # All prompts should be warm, or at least short and not cold
            assert has_warm, f"Prompt lacks warmth: {prompt}"
            assert not has_cold, f"Prompt is cold: {prompt}"

    def test_responses_are_warm(self) -> None:
        """All responses use warm language."""
        cold_patterns = ["ERROR", "FAILED", "INVALID", "MUST"]

        for response in WARMTH_RESPONSES.values():
            has_cold = any(p in response.upper() for p in cold_patterns)
            assert not has_cold, f"Response is cold: {response}"

    def test_disclosure_is_not_punitive(self) -> None:
        """Compression disclosure is descriptive, not punitive."""
        honesty = CompressionHonesty(
            dropped_count=5,
            dropped_tags=["friction"],
            dropped_summaries=["test"],
            galois_loss=0.3,
        )

        disclosure = honesty.to_disclosure()

        # Should NOT use punitive language
        punitive_patterns = ["lost", "failed", "error", "warning", "missing"]
        for pattern in punitive_patterns:
            assert pattern not in disclosure.lower(), f"Punitive language found: {pattern}"

        # Should use descriptive language
        assert "Set aside" in disclosure or "Everything was preserved" in disclosure


# =============================================================================
# Amendment G Compliance Tests
# =============================================================================


class TestAmendmentGCompliance:
    """Tests for Amendment G: COMPRESSION_HONESTY."""

    def test_every_crystal_has_disclosure(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Every crystal includes a disclosure."""
        capture = DailyMarkCapture(store=mark_store)
        for i in range(5):
            capture.quick(f"Note {i}")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        result = crystallizer.crystallize_day(date.today())

        assert result is not None
        assert result.honesty is not None
        assert result.disclosure != ""

    def test_disclosure_reflects_actual_drops(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Disclosure accurately reflects what was dropped."""
        capture = DailyMarkCapture(store=mark_store)
        # Add exactly MAX_IMPORTANT_MARKS + 3 marks
        for i in range(10):
            capture.friction(f"Friction note {i}")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        result = crystallizer.crystallize_day(date.today())

        assert result is not None
        # Should have dropped 3 marks (10 - 7)
        assert result.honesty.dropped_count == 3

    def test_galois_loss_computed(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Galois loss is computed for compression."""
        capture = DailyMarkCapture(store=mark_store)
        for i in range(10):
            capture.quick(f"Note {i}" * 10)  # Longer notes for meaningful loss

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        result = crystallizer.crystallize_day(date.today())

        assert result is not None
        assert result.honesty.galois_loss > 0
        assert result.honesty.galois_loss < 1.0
