"""
Tests for Garden Protocol ↔ Forest Protocol integration.

Phase 4 of Garden Protocol implementation.
Tests dual-format support in ForestNode.
"""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path

import pytest
from protocols.agentese.contexts.forest import (
    PlanFromHeader,
    parse_plan_yaml_header,
)
from protocols.garden.types import (
    EntropyBudget,
    GardenPlanHeader,
    Mood,
    Season,
    Trajectory,
    parse_garden_header,
)


class TestPlanFromHeaderFormats:
    """Test PlanFromHeader handles both formats."""

    def test_from_forest_protocol(self, tmp_path: Path) -> None:
        """Test parsing a Forest Protocol header."""
        plan_file = tmp_path / "test-plan.md"
        plan_file.write_text("""---
path: plans/test-plan
status: active
progress: 55
last_touched: 2025-12-18
touched_by: claude-opus-4-5
blocking: []
enables: []
session_notes: |
  Good progress today.
---

# Test Plan
""")

        header = parse_plan_yaml_header(plan_file)
        assert header is not None

        # Create PlanFromHeader with explicit path from header
        # (In real usage, file_path is only used as fallback when path not in header)
        last_touched_raw = header.get("last_touched", date.today())
        if isinstance(last_touched_raw, str):
            last_touched = date.fromisoformat(last_touched_raw)
        else:
            last_touched = last_touched_raw

        plan = PlanFromHeader(
            path=header.get("path", ""),
            progress=int(header.get("progress", 0)),
            status=header.get("status", "active"),
            last_touched=last_touched,
            notes=header.get("session_notes", "").split("\n")[0][:100],
            blocking=header.get("blocking", []) or [],
            enables=header.get("enables", []) or [],
            touched_by=header.get("touched_by", ""),
            format="forest",
            garden_header=None,
        )

        assert plan.format == "forest"
        assert plan.garden_header is None
        assert plan.path == "plans/test-plan"
        assert plan.progress == 55
        assert plan.status == "active"
        assert plan.touched_by == "claude-opus-4-5"

    def test_from_garden_protocol(self, tmp_path: Path) -> None:
        """Test parsing a Garden Protocol header."""
        plan_file = tmp_path / "test-plan.md"
        plan_file.write_text("""---
path: self.forest.plan.test-plan
mood: excited
momentum: 0.7
trajectory: accelerating
season: BLOOMING
last_gardened: 2025-12-18
gardener: claude-opus-4-5
letter: |
  We made real progress today. Coalition events feel elegant.
resonates_with:
  - atelier-experience
  - punchdrunk-park
entropy:
  available: 0.10
  spent: 0.03
  sips:
    - "2025-12-16: Noticed masks isomorphism"
---

# Test Plan
""")

        # First verify it parses as Garden Protocol
        garden = parse_garden_header(plan_file)
        assert garden is not None
        assert garden.mood == Mood.EXCITED
        assert garden.season == Season.BLOOMING

        # Now convert to PlanFromHeader
        plan = PlanFromHeader.from_garden_header(plan_file, garden)

        assert plan.format == "garden"
        assert plan.garden_header is garden
        assert plan.path == "self.forest.plan.test-plan"
        assert plan.progress == 70  # 0.7 momentum → 70% (capped by season)
        assert plan.status == "active"  # BLOOMING → active
        assert plan.touched_by == "claude-opus-4-5"
        assert "atelier-experience" in plan.enables
        assert "punchdrunk-park" in plan.enables

    def test_garden_to_forest_status_mapping(self) -> None:
        """Test Garden Protocol status equivalents."""
        # BLOOMING + excited → active
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.EXCITED,
            momentum=0.7,
            trajectory=Trajectory.ACCELERATING,
            season=Season.BLOOMING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=[],
        )
        assert header.status_equivalent == "active"

        # DORMANT → dormant
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.DREAMING,
            momentum=0.0,
            trajectory=Trajectory.PARKED,
            season=Season.DORMANT,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=[],
        )
        assert header.status_equivalent == "dormant"

        # COMPLETE mood → complete (regardless of season)
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.COMPLETE,
            momentum=1.0,
            trajectory=Trajectory.PARKED,
            season=Season.COMPOSTING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=[],
        )
        assert header.status_equivalent == "complete"

        # WAITING mood → blocked
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.WAITING,
            momentum=0.5,
            trajectory=Trajectory.PARKED,
            season=Season.BLOOMING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=[],
        )
        assert header.status_equivalent == "blocked"

    def test_garden_progress_equivalent_by_season(self) -> None:
        """Test Garden Protocol progress equivalents respect season caps."""
        # SPROUTING caps at 20%
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.CURIOUS,
            momentum=0.9,  # High momentum
            trajectory=Trajectory.ACCELERATING,
            season=Season.SPROUTING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=[],
        )
        assert header.progress_equivalent == 20  # Capped at 20

        # BLOOMING: 20-80 range
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.FOCUSED,
            momentum=0.5,
            trajectory=Trajectory.CRUISING,
            season=Season.BLOOMING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=[],
        )
        assert header.progress_equivalent == 50

        # FRUITING: 80-95 range
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.SATISFIED,
            momentum=0.5,  # 50% but fruiting caps at 80+
            trajectory=Trajectory.CRUISING,
            season=Season.FRUITING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=[],
        )
        assert header.progress_equivalent == 80  # Min 80 for FRUITING

        # COMPOSTING: 95+ range
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.SATISFIED,
            momentum=0.5,  # 50% but composting is 95+
            trajectory=Trajectory.DECELERATING,
            season=Season.COMPOSTING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=[],
        )
        assert header.progress_equivalent == 95  # Min 95 for COMPOSTING

    def test_letter_to_notes_extraction(self) -> None:
        """Test letter content is extracted as notes."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.EXCITED,
            momentum=0.7,
            trajectory=Trajectory.ACCELERATING,
            season=Season.BLOOMING,
            last_gardened=date.today(),
            gardener="test",
            letter="First line of the letter.\nSecond line with more detail.\nThird line.",
            resonates_with=[],
        )

        # Create temporary file for conversion

        with tempfile.NamedTemporaryFile(suffix=".md") as f:
            plan = PlanFromHeader.from_garden_header(Path(f.name), header)
            assert plan.notes == "First line of the letter."

    def test_empty_letter_gives_empty_notes(self) -> None:
        """Test empty letter produces empty notes."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.CURIOUS,
            momentum=0.5,
            trajectory=Trajectory.CRUISING,
            season=Season.SPROUTING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=[],
        )

        with tempfile.NamedTemporaryFile(suffix=".md") as f:
            plan = PlanFromHeader.from_garden_header(Path(f.name), header)
            assert plan.notes == ""


class TestMixedFormatParsing:
    """Test parsing mixed Forest and Garden Protocol files."""

    def test_garden_detected_by_mood_field(self, tmp_path: Path) -> None:
        """Garden Protocol is detected by presence of 'mood' field."""
        plan_file = tmp_path / "garden-plan.md"
        plan_file.write_text("""---
path: self.forest.plan.test
mood: excited
season: BLOOMING
---
""")

        garden = parse_garden_header(plan_file)
        forest = parse_plan_yaml_header(plan_file)

        assert garden is not None
        assert forest is not None
        assert garden.mood == Mood.EXCITED

    def test_garden_detected_by_season_field(self, tmp_path: Path) -> None:
        """Garden Protocol is detected by presence of 'season' field."""
        plan_file = tmp_path / "garden-plan.md"
        plan_file.write_text("""---
path: self.forest.plan.test
season: DORMANT
---
""")

        garden = parse_garden_header(plan_file)
        assert garden is not None
        assert garden.season == Season.DORMANT

    def test_forest_not_detected_as_garden(self, tmp_path: Path) -> None:
        """Forest Protocol files are not detected as Garden Protocol."""
        plan_file = tmp_path / "forest-plan.md"
        plan_file.write_text("""---
path: plans/test
status: active
progress: 50
---
""")

        garden = parse_garden_header(plan_file)
        forest = parse_plan_yaml_header(plan_file)

        assert garden is None  # No mood or season
        assert forest is not None
        assert forest["status"] == "active"

    def test_garden_defaults_for_missing_fields(self, tmp_path: Path) -> None:
        """Garden Protocol parser provides sensible defaults."""
        plan_file = tmp_path / "minimal-garden.md"
        plan_file.write_text("""---
path: self.forest.plan.minimal
mood: curious
---
""")

        garden = parse_garden_header(plan_file)
        assert garden is not None
        assert garden.mood == Mood.CURIOUS
        assert garden.season == Season.SPROUTING  # Default
        assert garden.momentum == 0.5  # Default
        assert garden.trajectory == Trajectory.CRUISING  # Default


class TestResonanceMapping:
    """Test resonates_with → enables mapping."""

    def test_resonates_with_becomes_enables(self) -> None:
        """resonates_with maps to enables for Forest Protocol compatibility."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.EXCITED,
            momentum=0.7,
            trajectory=Trajectory.ACCELERATING,
            season=Season.BLOOMING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=["plan-a", "plan-b", "plan-c"],
        )

        with tempfile.NamedTemporaryFile(suffix=".md") as f:
            plan = PlanFromHeader.from_garden_header(Path(f.name), header)
            assert set(plan.enables) == {"plan-a", "plan-b", "plan-c"}
            assert plan.blocking == []  # Garden doesn't use blocking

    def test_empty_resonates_with(self) -> None:
        """Empty resonates_with produces empty enables."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.CURIOUS,
            momentum=0.5,
            trajectory=Trajectory.CRUISING,
            season=Season.SPROUTING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=[],
        )

        with tempfile.NamedTemporaryFile(suffix=".md") as f:
            plan = PlanFromHeader.from_garden_header(Path(f.name), header)
            assert plan.enables == []
            assert plan.blocking == []


class TestEntropyHandling:
    """Test entropy budget is preserved through conversion."""

    def test_entropy_preserved(self, tmp_path: Path) -> None:
        """Entropy budget is accessible through garden_header."""
        plan_file = tmp_path / "entropy-plan.md"
        plan_file.write_text("""---
path: self.forest.plan.test
mood: curious
season: SPROUTING
entropy:
  available: 0.15
  spent: 0.05
  sips:
    - "2025-12-16: Explored tangent"
    - "2025-12-17: Another tangent"
---
""")

        garden = parse_garden_header(plan_file)
        assert garden is not None
        assert garden.entropy.available == 0.15
        assert garden.entropy.spent == 0.05
        assert len(garden.entropy.sips) == 2

        # After conversion, entropy is still accessible
        plan = PlanFromHeader.from_garden_header(plan_file, garden)
        assert plan.garden_header is not None
        assert plan.garden_header.entropy.remaining == pytest.approx(0.10)


class TestIntegration:
    """Integration tests for the full flow."""

    def test_round_trip_garden_plan(self, tmp_path: Path) -> None:
        """Garden Protocol plan can be parsed and converted."""
        plan_file = tmp_path / "full-garden.md"
        plan_file.write_text("""---
path: self.forest.plan.coalition-forge
mood: excited
momentum: 0.75
trajectory: accelerating
season: BLOOMING
last_gardened: 2025-12-18
gardener: claude-opus-4-5
letter: |
  Coalition events feel elegant. Natural emergence from citizen interactions.
  The Atelier synergy via exquisite corpse is particularly delightful.
resonates_with:
  - atelier-experience
  - punchdrunk-park
entropy:
  available: 0.10
  spent: 0.03
  sips:
    - "2025-12-16: Noticed masks → coalition identity isomorphism"
---

# Coalition Forge

The plan body content.
""")

        # Parse
        garden = parse_garden_header(plan_file)
        assert garden is not None

        # Convert
        plan = PlanFromHeader.from_garden_header(plan_file, garden)

        # Verify backwards compatibility
        assert plan.format == "garden"
        assert plan.status == "active"
        assert 20 <= plan.progress <= 80  # BLOOMING range
        assert plan.touched_by == "claude-opus-4-5"
        assert "atelier-experience" in plan.enables

        # Verify Garden Protocol data preserved
        assert plan.garden_header is not None
        assert plan.garden_header.mood == Mood.EXCITED
        assert plan.garden_header.season == Season.BLOOMING
        assert plan.garden_header.momentum == 0.75
        assert len(plan.garden_header.resonates_with) == 2

    def test_forest_plan_unchanged(self, tmp_path: Path) -> None:
        """Forest Protocol plan is parsed as before."""
        plan_file = tmp_path / "forest-plan.md"
        plan_file.write_text("""---
path: plans/old-plan
status: active
progress: 55
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - dependency-plan
session_notes: |
  Good progress on the old forest plan.
---

# Old Forest Plan
""")

        # Should not parse as Garden
        garden = parse_garden_header(plan_file)
        assert garden is None

        # Should parse as Forest
        header = parse_plan_yaml_header(plan_file)
        assert header is not None

        # Create PlanFromHeader with explicit path from header
        last_touched_raw = header.get("last_touched", date.today())
        if isinstance(last_touched_raw, str):
            last_touched = date.fromisoformat(last_touched_raw)
        else:
            last_touched = last_touched_raw

        plan = PlanFromHeader(
            path=header.get("path", ""),
            progress=int(header.get("progress", 0)),
            status=header.get("status", "active"),
            last_touched=last_touched,
            notes=header.get("session_notes", "").split("\n")[0][:100],
            blocking=header.get("blocking", []) or [],
            enables=header.get("enables", []) or [],
            touched_by=header.get("touched_by", ""),
            format="forest",
            garden_header=None,
        )
        assert plan.format == "forest"
        assert plan.garden_header is None
        assert plan.progress == 55
        assert plan.status == "active"
        assert "dependency-plan" in plan.enables
