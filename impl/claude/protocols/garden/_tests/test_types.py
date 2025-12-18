"""
Tests for Garden Protocol types.

Tests cover:
- Season enum values and transitions
- Mood vocabulary
- Trajectory enum
- EntropyBudget mechanics (sip, tithe, exhaustion)
- GardenPlanHeader serialization/deserialization
- GardenPolynomial state machine behavior
- Forest → Garden migration
"""

from datetime import date

import pytest

from protocols.garden.types import (
    # Dataclasses
    EntropyBudget,
    EntropySip,
    GardenInput,
    GardenPlanHeader,
    # Polynomial
    GardenPolynomial,
    Gesture,
    GestureType,
    Mood,
    # Enums
    Season,
    SessionHeader,
    Trajectory,
    migrate_forest_to_garden,
    # Parser
    parse_garden_header,
)

# =============================================================================
# Season Tests
# =============================================================================


class TestSeason:
    """Tests for Season enum."""

    def test_all_seasons_defined(self):
        """All five seasons exist."""
        assert Season.SPROUTING.value == "sprouting"
        assert Season.BLOOMING.value == "blooming"
        assert Season.FRUITING.value == "fruiting"
        assert Season.COMPOSTING.value == "composting"
        assert Season.DORMANT.value == "dormant"

    def test_season_from_string(self):
        """Seasons can be created from strings."""
        assert Season("sprouting") == Season.SPROUTING
        assert Season("blooming") == Season.BLOOMING
        assert Season("fruiting") == Season.FRUITING
        assert Season("composting") == Season.COMPOSTING
        assert Season("dormant") == Season.DORMANT

    def test_season_count(self):
        """Exactly five seasons exist."""
        assert len(Season) == 5

    def test_season_invalid_value(self):
        """Invalid season values raise ValueError."""
        with pytest.raises(ValueError):
            Season("invalid")


# =============================================================================
# Trajectory Tests
# =============================================================================


class TestTrajectory:
    """Tests for Trajectory enum."""

    def test_all_trajectories_defined(self):
        """All four trajectories exist."""
        assert Trajectory.ACCELERATING.value == "accelerating"
        assert Trajectory.CRUISING.value == "cruising"
        assert Trajectory.DECELERATING.value == "decelerating"
        assert Trajectory.PARKED.value == "parked"

    def test_trajectory_count(self):
        """Exactly four trajectories exist."""
        assert len(Trajectory) == 4


# =============================================================================
# Mood Tests
# =============================================================================


class TestMood:
    """Tests for Mood vocabulary."""

    def test_all_moods_defined(self):
        """All nine moods exist."""
        assert Mood.EXCITED.value == "excited"
        assert Mood.CURIOUS.value == "curious"
        assert Mood.FOCUSED.value == "focused"
        assert Mood.SATISFIED.value == "satisfied"
        assert Mood.STUCK.value == "stuck"
        assert Mood.WAITING.value == "waiting"
        assert Mood.TIRED.value == "tired"
        assert Mood.DREAMING.value == "dreaming"
        assert Mood.COMPLETE.value == "complete"

    def test_mood_count(self):
        """Exactly nine moods exist."""
        assert len(Mood) == 9

    def test_mood_vocabulary_natural(self):
        """Moods use natural, unstrained words (spec requirement)."""
        # These should NOT be in the vocabulary (anti-pattern from spec)
        mood_values = {m.value for m in Mood}
        assert "vibing" not in mood_values
        assert "stoked" not in mood_values
        assert "effervescent" not in mood_values


# =============================================================================
# GardenInput Tests
# =============================================================================


class TestGardenInput:
    """Tests for GardenInput enum."""

    def test_sprouting_inputs(self):
        """SPROUTING accepts exploration inputs."""
        assert GardenInput.EXPLORE.value == "explore"
        assert GardenInput.DEFINE.value == "define"
        assert GardenInput.CONNECT.value == "connect"

    def test_blooming_inputs(self):
        """BLOOMING accepts development inputs."""
        assert GardenInput.BUILD.value == "build"
        assert GardenInput.TEST.value == "test"
        assert GardenInput.REFINE.value == "refine"

    def test_fruiting_inputs(self):
        """FRUITING accepts harvesting inputs."""
        assert GardenInput.DOCUMENT.value == "document"
        assert GardenInput.SHIP.value == "ship"
        assert GardenInput.CELEBRATE.value == "celebrate"

    def test_composting_inputs(self):
        """COMPOSTING accepts extraction inputs."""
        assert GardenInput.EXTRACT.value == "extract"
        assert GardenInput.ARCHIVE.value == "archive"
        assert GardenInput.TITHE.value == "tithe"

    def test_dormant_inputs(self):
        """DORMANT accepts dream/wake inputs."""
        assert GardenInput.DREAM.value == "dream"
        assert GardenInput.WAKE.value == "wake"


# =============================================================================
# EntropyBudget Tests
# =============================================================================


class TestEntropyBudget:
    """Tests for EntropyBudget mechanics."""

    def test_default_budget(self):
        """Default entropy budget is 0.10."""
        budget = EntropyBudget()
        assert budget.available == 0.10
        assert budget.spent == 0.0
        assert budget.remaining == 0.10
        assert not budget.exhausted
        assert budget.sips == []

    def test_sip_reduces_remaining(self):
        """Sip reduces remaining entropy."""
        budget = EntropyBudget(available=0.10, spent=0.0)
        result = budget.sip("Testing exploration", amount=0.02)

        assert result is True
        assert budget.spent == 0.02
        assert budget.remaining == 0.08
        assert len(budget.sips) == 1
        assert budget.sips[0].description == "Testing exploration"

    def test_sip_records_date(self):
        """Sip records current date."""
        budget = EntropyBudget()
        budget.sip("Test sip")

        assert budget.sips[0].date == date.today().isoformat()

    def test_sip_fails_when_exhausted(self):
        """Sip fails when budget exhausted."""
        budget = EntropyBudget(available=0.10, spent=0.10)
        assert budget.exhausted is True

        result = budget.sip("Should fail")
        assert result is False
        assert len(budget.sips) == 0

    def test_tithe_restores_budget(self):
        """Tithe restores available entropy."""
        budget = EntropyBudget(available=0.10, spent=0.08)
        budget.tithe(amount=0.05)

        assert abs(budget.available - 0.15) < 0.001
        assert abs(budget.remaining - 0.07) < 0.001

    def test_entropy_to_dict(self):
        """EntropyBudget serializes to dict."""
        budget = EntropyBudget(available=0.10, spent=0.03)
        budget.sips.append(EntropySip(date="2025-12-18", description="Test"))

        d = budget.to_dict()
        assert d["available"] == 0.10
        assert d["spent"] == 0.03
        assert d["sips"] == ["2025-12-18: Test"]

    def test_entropy_from_dict(self):
        """EntropyBudget deserializes from dict."""
        d = {
            "available": 0.15,
            "spent": 0.05,
            "sips": ["2025-12-18: Test sip"],
        }
        budget = EntropyBudget.from_dict(d)

        assert budget.available == 0.15
        assert budget.spent == 0.05
        assert len(budget.sips) == 1
        assert budget.sips[0].date == "2025-12-18"
        assert budget.sips[0].description == "Test sip"


# =============================================================================
# GardenPlanHeader Tests
# =============================================================================


class TestGardenPlanHeader:
    """Tests for GardenPlanHeader dataclass."""

    @pytest.fixture
    def sample_header(self) -> GardenPlanHeader:
        """Create a sample GardenPlanHeader for testing."""
        return GardenPlanHeader(
            path="self.forest.plan.coalition-forge",
            mood=Mood.EXCITED,
            momentum=0.7,
            trajectory=Trajectory.ACCELERATING,
            season=Season.BLOOMING,
            last_gardened=date(2025, 12, 18),
            gardener="claude-opus-4-5",
            letter="We made real progress today...",
            resonates_with=["atelier-experience", "punchdrunk-park"],
            entropy=EntropyBudget(available=0.10, spent=0.03),
        )

    def test_header_name_extraction(self, sample_header: GardenPlanHeader):
        """Name is extracted from AGENTESE path."""
        assert sample_header.name == "coalition-forge"

    def test_header_name_from_legacy_path(self):
        """Name extraction works for legacy paths."""
        header = GardenPlanHeader(
            path="plans/coalition-forge",
            mood=Mood.CURIOUS,
            momentum=0.5,
            trajectory=Trajectory.CRUISING,
            season=Season.SPROUTING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
        )
        assert header.name == "coalition-forge"

    def test_progress_equivalent(self, sample_header: GardenPlanHeader):
        """Progress equivalent maps momentum to percentage."""
        # BLOOMING with momentum 0.7 → should be in 20-80 range
        progress = sample_header.progress_equivalent
        assert 20 <= progress <= 80

    def test_progress_equivalent_sprouting(self):
        """SPROUTING caps progress at 20%."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.CURIOUS,
            momentum=0.9,  # High momentum
            trajectory=Trajectory.ACCELERATING,
            season=Season.SPROUTING,  # But still sprouting
            last_gardened=date.today(),
            gardener="test",
            letter="",
        )
        assert header.progress_equivalent <= 20

    def test_status_equivalent_active(self, sample_header: GardenPlanHeader):
        """BLOOMING maps to active status."""
        assert sample_header.status_equivalent == "active"

    def test_status_equivalent_dormant(self):
        """DORMANT season maps to dormant status."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.DREAMING,
            momentum=0.3,
            trajectory=Trajectory.PARKED,
            season=Season.DORMANT,
            last_gardened=date.today(),
            gardener="test",
            letter="",
        )
        assert header.status_equivalent == "dormant"

    def test_status_equivalent_complete(self):
        """COMPLETE mood maps to complete status."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.COMPLETE,
            momentum=1.0,
            trajectory=Trajectory.PARKED,
            season=Season.COMPOSTING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
        )
        assert header.status_equivalent == "complete"

    def test_status_equivalent_blocked(self):
        """WAITING mood maps to blocked status."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.WAITING,
            momentum=0.5,
            trajectory=Trajectory.PARKED,
            season=Season.BLOOMING,
            last_gardened=date.today(),
            gardener="test",
            letter="",
        )
        assert header.status_equivalent == "blocked"

    def test_header_to_dict(self, sample_header: GardenPlanHeader):
        """Header serializes to dict."""
        d = sample_header.to_dict()

        assert d["path"] == "self.forest.plan.coalition-forge"
        assert d["mood"] == "excited"
        assert d["momentum"] == 0.7
        assert d["trajectory"] == "accelerating"
        assert d["season"] == "BLOOMING"
        assert d["last_gardened"] == "2025-12-18"
        assert d["gardener"] == "claude-opus-4-5"
        assert d["letter"] == "We made real progress today..."
        assert d["resonates_with"] == ["atelier-experience", "punchdrunk-park"]
        assert "entropy" in d

    def test_header_from_dict(self):
        """Header deserializes from dict."""
        d = {
            "path": "self.forest.plan.test",
            "mood": "focused",
            "momentum": 0.6,
            "trajectory": "cruising",
            "season": "BLOOMING",
            "last_gardened": "2025-12-18",
            "gardener": "test-gardener",
            "letter": "Test letter",
            "resonates_with": ["other-plan"],
            "entropy": {"available": 0.10, "spent": 0.02},
        }
        header = GardenPlanHeader.from_dict(d)

        assert header.path == "self.forest.plan.test"
        assert header.mood == Mood.FOCUSED
        assert header.momentum == 0.6
        assert header.trajectory == Trajectory.CRUISING
        assert header.season == Season.BLOOMING
        assert header.last_gardened == date(2025, 12, 18)
        assert header.gardener == "test-gardener"
        assert header.letter == "Test letter"
        assert header.resonates_with == ["other-plan"]
        assert header.entropy.available == 0.10
        assert header.entropy.spent == 0.02

    def test_header_from_dict_handles_lowercase_season(self):
        """Season parsing handles lowercase."""
        d = {
            "path": "self.forest.plan.test",
            "mood": "curious",
            "season": "sprouting",  # lowercase
        }
        header = GardenPlanHeader.from_dict(d)
        assert header.season == Season.SPROUTING

    def test_header_from_dict_defaults(self):
        """Missing fields get sensible defaults."""
        d = {"path": "self.forest.plan.test"}
        header = GardenPlanHeader.from_dict(d)

        assert header.mood == Mood.CURIOUS
        assert header.momentum == 0.5
        assert header.trajectory == Trajectory.CRUISING
        assert header.season == Season.SPROUTING
        assert header.letter == ""
        assert header.resonates_with == []


# =============================================================================
# GardenPolynomial Tests
# =============================================================================


class TestGardenPolynomial:
    """Tests for GardenPolynomial state machine."""

    def test_polynomial_positions(self):
        """Polynomial has all seasons as positions."""
        assert Season.SPROUTING in GardenPolynomial.positions
        assert Season.BLOOMING in GardenPolynomial.positions
        assert Season.FRUITING in GardenPolynomial.positions
        assert Season.COMPOSTING in GardenPolynomial.positions
        assert Season.DORMANT in GardenPolynomial.positions

    def test_sprouting_directions(self):
        """SPROUTING accepts exploration inputs."""
        directions = GardenPolynomial.directions(Season.SPROUTING)

        assert GardenInput.EXPLORE in directions
        assert GardenInput.DEFINE in directions
        assert GardenInput.CONNECT in directions
        assert GardenInput.BUILD not in directions

    def test_blooming_directions(self):
        """BLOOMING accepts development inputs."""
        directions = GardenPolynomial.directions(Season.BLOOMING)

        assert GardenInput.BUILD in directions
        assert GardenInput.TEST in directions
        assert GardenInput.REFINE in directions
        assert GardenInput.EXPLORE not in directions

    def test_fruiting_directions(self):
        """FRUITING accepts harvesting inputs."""
        directions = GardenPolynomial.directions(Season.FRUITING)

        assert GardenInput.DOCUMENT in directions
        assert GardenInput.SHIP in directions
        assert GardenInput.CELEBRATE in directions
        assert GardenInput.BUILD not in directions

    def test_composting_directions(self):
        """COMPOSTING accepts extraction inputs."""
        directions = GardenPolynomial.directions(Season.COMPOSTING)

        assert GardenInput.EXTRACT in directions
        assert GardenInput.ARCHIVE in directions
        assert GardenInput.TITHE in directions

    def test_dormant_directions(self):
        """DORMANT accepts dream/wake inputs."""
        directions = GardenPolynomial.directions(Season.DORMANT)

        assert GardenInput.DREAM in directions
        assert GardenInput.WAKE in directions
        assert len(directions) == 2

    def test_dormant_wake_transitions_to_sprouting(self):
        """WAKE in DORMANT transitions to SPROUTING."""
        new_season, _ = GardenPolynomial.invoke(Season.DORMANT, GardenInput.WAKE)
        assert new_season == Season.SPROUTING

    def test_composting_archive_transitions_to_dormant(self):
        """ARCHIVE in COMPOSTING transitions to DORMANT."""
        new_season, _ = GardenPolynomial.invoke(Season.COMPOSTING, GardenInput.ARCHIVE)
        assert new_season == Season.DORMANT

    def test_invalid_input_raises(self):
        """Invalid input for season raises ValueError."""
        with pytest.raises(ValueError):
            GardenPolynomial.invoke(Season.DORMANT, GardenInput.BUILD)

    def test_run_through_lifecycle(self):
        """Run polynomial through a complete lifecycle."""
        # Start dormant, wake up
        season = Season.DORMANT
        season, _ = GardenPolynomial.invoke(season, GardenInput.WAKE)
        assert season == Season.SPROUTING

        # Explore and define
        season, _ = GardenPolynomial.invoke(season, GardenInput.EXPLORE)
        assert season == Season.SPROUTING  # Still sprouting


# =============================================================================
# Migration Tests
# =============================================================================


class TestMigration:
    """Tests for Forest → Garden migration."""

    def test_migrate_active_plan(self):
        """Active Forest plan migrates correctly."""
        forest = {
            "path": "plans/coalition-forge",
            "status": "active",
            "progress": 55,
            "last_touched": "2025-12-18",
            "touched_by": "claude-opus-4-5",
            "session_notes": "Working on events.",
            "blocking": [],
            "enables": ["atelier-experience"],
        }
        garden = migrate_forest_to_garden(forest)

        assert garden.path == "self.forest.plan.coalition-forge"
        assert garden.mood == Mood.FOCUSED  # active → focused
        assert garden.momentum == 0.55
        assert garden.season == Season.BLOOMING  # 55% → blooming
        assert garden.letter == "Working on events."
        assert "atelier-experience" in garden.resonates_with

    def test_migrate_dormant_plan(self):
        """Dormant Forest plan migrates correctly."""
        forest = {
            "path": "plans/old-plan",
            "status": "dormant",
            "progress": 30,
            "last_touched": "2025-11-01",
        }
        garden = migrate_forest_to_garden(forest)

        assert garden.mood == Mood.DREAMING
        assert garden.season == Season.DORMANT

    def test_migrate_complete_plan(self):
        """Complete Forest plan migrates correctly."""
        forest = {
            "path": "plans/finished",
            "status": "complete",
            "progress": 100,
        }
        garden = migrate_forest_to_garden(forest)

        assert garden.mood == Mood.COMPLETE
        assert garden.season == Season.COMPOSTING

    def test_migrate_blocked_plan(self):
        """Blocked Forest plan migrates correctly."""
        forest = {
            "path": "plans/waiting",
            "status": "blocked",
            "progress": 40,
            "blocking": ["dependency"],
        }
        garden = migrate_forest_to_garden(forest)

        assert garden.mood == Mood.WAITING
        assert "dependency" in garden.resonates_with

    def test_migrate_entropy(self):
        """Entropy budget migrates correctly."""
        forest = {
            "path": "plans/test",
            "status": "active",
            "progress": 50,
            "entropy": {
                "planned": 0.10,
                "spent": 0.03,
                "returned": 0.02,
            },
        }
        garden = migrate_forest_to_garden(forest)

        # available = planned + returned = 0.12
        assert abs(garden.entropy.available - 0.12) < 0.001
        assert abs(garden.entropy.spent - 0.03) < 0.001

    def test_migrate_preserves_date(self):
        """Date is preserved in migration."""
        forest = {
            "path": "plans/test",
            "status": "active",
            "progress": 50,
            "last_touched": "2025-12-15",
        }
        garden = migrate_forest_to_garden(forest)

        assert garden.last_gardened == date(2025, 12, 15)


# =============================================================================
# Gesture Tests
# =============================================================================


class TestGesture:
    """Tests for Gesture dataclass."""

    def test_gesture_to_dict(self):
        """Gesture serializes to dict."""
        gesture = Gesture(
            type=GestureType.CODE,
            plan="coalition-forge",
            summary="Added event emission",
            files=["services/town/events.py"],
        )
        d = gesture.to_dict()

        assert d["type"] == "code"
        assert d["plan"] == "coalition-forge"
        assert d["summary"] == "Added event emission"
        assert d["files"] == ["services/town/events.py"]

    def test_gesture_to_dict_no_files(self):
        """Gesture without files omits files key."""
        gesture = Gesture(
            type=GestureType.INSIGHT,
            plan="test",
            summary="Discovered pattern",
        )
        d = gesture.to_dict()

        assert "files" not in d


# =============================================================================
# SessionHeader Tests
# =============================================================================


class TestSessionHeader:
    """Tests for SessionHeader dataclass."""

    def test_session_to_dict(self):
        """SessionHeader serializes to dict."""
        session = SessionHeader(
            date=date(2025, 12, 18),
            period="morning",
            gardener="claude-opus-4-5",
            plans_tended=["coalition-forge (BLOOMING → BLOOMING, +0.1)"],
            gestures=[
                Gesture(
                    type=GestureType.CODE,
                    plan="coalition-forge",
                    summary="Test",
                )
            ],
            entropy_spent=0.02,
            letter="Test letter",
        )
        d = session.to_dict()

        assert d["date"] == "2025-12-18"
        assert d["period"] == "morning"
        assert d["gardener"] == "claude-opus-4-5"
        assert len(d["plans_tended"]) == 1
        assert len(d["gestures"]) == 1
        assert d["entropy_spent"] == 0.02


# =============================================================================
# Property-based tests (if hypothesis available)
# =============================================================================


try:
    from hypothesis import given, strategies as st

    class TestPropertyBased:
        """Property-based tests for Garden types."""

        @given(st.floats(min_value=0.0, max_value=1.0))
        def test_momentum_always_valid(self, momentum: float):
            """Momentum in [0,1] always produces valid progress."""
            header = GardenPlanHeader(
                path="self.forest.plan.test",
                mood=Mood.CURIOUS,
                momentum=momentum,
                trajectory=Trajectory.CRUISING,
                season=Season.BLOOMING,
                last_gardened=date.today(),
                gardener="test",
                letter="",
            )
            progress = header.progress_equivalent
            assert 0 <= progress <= 100

        @given(st.sampled_from(list(Season)))
        def test_all_seasons_have_directions(self, season: Season):
            """Every season has at least one valid input."""
            directions = GardenPolynomial.directions(season)
            assert len(directions) >= 1

except ImportError:
    pass  # hypothesis not installed, skip property tests
