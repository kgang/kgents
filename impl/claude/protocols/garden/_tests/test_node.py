"""
Tests for Garden Protocol PlanNode.

Tests cover:
- Node registration at self.forest.plan
- Aspect handlers: manifest, letter, tend, dream
- Helper functions: load_plan, find_resonances
- Season-dependent polynomial behavior via aspects
- Entropy budget integration
"""

from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import protocols.garden.node as garden_node_module
from protocols.garden.node import (
    PLAN_AFFORDANCES,
    PlanNode,
    find_resonances,
    get_plan_node,
    load_plan,
)
from protocols.garden.types import (
    EntropyBudget,
    GardenInput,
    GardenPlanHeader,
    GestureType,
    Mood,
    Season,
    Trajectory,
)


@pytest.fixture(autouse=True)
def reset_plan_node_singleton():
    """Reset the singleton before each test."""
    garden_node_module._plan_node = None
    yield
    garden_node_module._plan_node = None


# =============================================================================
# Node Registration Tests
# =============================================================================


class TestNodeRegistration:
    """Tests for PlanNode registration."""

    def test_node_exists(self):
        """PlanNode class exists and is importable."""
        assert PlanNode is not None

    def test_node_handle(self):
        """PlanNode has correct handle."""
        node = get_plan_node()
        assert node.handle == "self.forest.plan"

    def test_affordances_defined(self):
        """All four affordances are defined."""
        assert "manifest" in PLAN_AFFORDANCES
        assert "letter" in PLAN_AFFORDANCES
        assert "tend" in PLAN_AFFORDANCES
        assert "dream" in PLAN_AFFORDANCES
        assert len(PLAN_AFFORDANCES) == 4

    def test_singleton_factory(self):
        """get_plan_node returns singleton."""
        node1 = get_plan_node()
        node2 = get_plan_node()
        assert node1 is node2

    def test_affordances_by_role(self):
        """Role-based affordances are returned correctly."""
        node = get_plan_node()

        # Guest role gets read-only affordances
        guest_affordances = node._get_affordances_for_archetype("guest")
        assert "manifest" in guest_affordances
        assert "letter" in guest_affordances
        assert "tend" not in guest_affordances
        assert "dream" not in guest_affordances

        # Meta role gets all affordances
        meta_affordances = node._get_affordances_for_archetype("meta")
        assert "manifest" in meta_affordances
        assert "letter" in meta_affordances
        assert "tend" in meta_affordances
        assert "dream" in meta_affordances


# =============================================================================
# Load Plan Tests
# =============================================================================


class TestLoadPlan:
    """Tests for load_plan helper."""

    @pytest.mark.asyncio
    async def test_load_nonexistent_plan(self):
        """Loading nonexistent plan returns None."""
        result = await load_plan("nonexistent-plan-xyz-123")
        assert result is None

    @pytest.mark.asyncio
    async def test_load_plan_creates_minimal_header(self, tmp_path: Path):
        """Loading existing file without Garden header creates minimal header."""
        # Create a plan file without Garden Protocol header
        plan_file = tmp_path / "test-plan.md"
        plan_file.write_text("# Test Plan\n\nSome content.")

        # Patch project root to use tmp_path
        with patch("protocols.garden.node._get_plans_dir", return_value=tmp_path):
            result = await load_plan("test-plan")

        # Should return a minimal header since file exists but no Garden header
        assert result is not None
        assert result.name == "test-plan"
        assert result.season == Season.DORMANT  # Default for unparseable
        assert result.mood == Mood.CURIOUS


# =============================================================================
# Find Resonances Tests
# =============================================================================


class TestFindResonances:
    """Tests for find_resonances helper."""

    @pytest.mark.asyncio
    async def test_find_resonances_empty(self, tmp_path: Path):
        """Empty plans directory returns no resonances."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.DREAMING,
            momentum=0.0,
            trajectory=Trajectory.PARKED,
            season=Season.DORMANT,
            last_gardened=date.today(),
            gardener="test",
            letter="",
        )

        with patch("protocols.garden.node._get_plans_dir", return_value=tmp_path):
            result = await find_resonances(header, entropy_amount=0.05)

        assert result == []

    @pytest.mark.asyncio
    async def test_find_resonances_with_shared_words(self, tmp_path: Path):
        """Plans with shared words are discovered."""
        # Create plan files
        (tmp_path / "coalition-forge.md").write_text("# Coalition Forge")
        (tmp_path / "coalition-events.md").write_text("# Coalition Events")
        (tmp_path / "unrelated-plan.md").write_text("# Unrelated")

        header = GardenPlanHeader(
            path="self.forest.plan.coalition-forge",
            mood=Mood.DREAMING,
            momentum=0.0,
            trajectory=Trajectory.PARKED,
            season=Season.DORMANT,
            last_gardened=date.today(),
            gardener="test",
            letter="",
        )

        with patch("protocols.garden.node._get_plans_dir", return_value=tmp_path):
            result = await find_resonances(header, entropy_amount=0.10)

        # Should find coalition-events due to shared "coalition" word
        plan_names = [c["plan_name"] for c in result]
        assert "coalition-events" in plan_names
        assert "coalition-forge" not in plan_names  # Self is excluded
        assert "unrelated-plan" not in plan_names

    @pytest.mark.asyncio
    async def test_find_resonances_respects_entropy_budget(self, tmp_path: Path):
        """Entropy budget limits number of connections returned."""
        # Create many plan files
        for i in range(10):
            (tmp_path / f"test-plan-{i}.md").write_text(f"# Test Plan {i}")

        header = GardenPlanHeader(
            path="self.forest.plan.test-plan-main",
            mood=Mood.DREAMING,
            momentum=0.0,
            trajectory=Trajectory.PARKED,
            season=Season.DORMANT,
            last_gardened=date.today(),
            gardener="test",
            letter="",
        )

        # With very low entropy, should get limited connections
        with patch("protocols.garden.node._get_plans_dir", return_value=tmp_path):
            result = await find_resonances(header, entropy_amount=0.02)

        # Each connection costs 0.01, so max 2 with 0.02 budget
        assert len(result) <= 2


# =============================================================================
# Manifest Aspect Tests
# =============================================================================


class TestManifestAspect:
    """Tests for manifest aspect."""

    @pytest.fixture
    def mock_observer(self):
        """Create a mock observer."""
        observer = MagicMock()
        observer.name = "test-observer"
        return observer

    @pytest.fixture
    def sample_header(self):
        """Create a sample GardenPlanHeader."""
        return GardenPlanHeader(
            path="self.forest.plan.test-plan",
            mood=Mood.EXCITED,
            momentum=0.7,
            trajectory=Trajectory.ACCELERATING,
            season=Season.BLOOMING,
            last_gardened=date(2025, 12, 18),
            gardener="claude",
            letter="Great progress on testing!",
            resonates_with=["other-plan"],
            entropy=EntropyBudget(available=0.10, spent=0.03),
        )

    @pytest.mark.asyncio
    async def test_manifest_not_found(self, mock_observer):
        """Manifest returns not_found for missing plan."""
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=None):
            result = await node._manifest_impl(mock_observer, "nonexistent")

        assert result.metadata["status"] == "not_found"
        assert "nonexistent" in result.content

    @pytest.mark.asyncio
    async def test_manifest_returns_plan_state(self, mock_observer, sample_header):
        """Manifest returns complete plan state."""
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=sample_header):
            result = await node._manifest_impl(mock_observer, "test-plan")

        assert result.metadata["status"] == "live"
        assert result.metadata["plan_name"] == "test-plan"
        assert result.metadata["mood"] == "excited"
        assert result.metadata["momentum"] == 0.7
        assert result.metadata["season"] == "blooming"

    @pytest.mark.asyncio
    async def test_manifest_includes_valid_inputs(self, mock_observer, sample_header):
        """Manifest includes season-appropriate valid inputs."""
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=sample_header):
            result = await node._manifest_impl(mock_observer, "test-plan")

        valid_inputs = result.metadata["valid_inputs"]
        # BLOOMING should accept build, test, refine
        assert "build" in valid_inputs
        assert "test" in valid_inputs
        assert "refine" in valid_inputs
        # But not exploration inputs
        assert "explore" not in valid_inputs


# =============================================================================
# Letter Aspect Tests
# =============================================================================


class TestLetterAspect:
    """Tests for letter aspect."""

    @pytest.fixture
    def mock_observer(self):
        observer = MagicMock()
        observer.name = "test-observer"
        return observer

    @pytest.mark.asyncio
    async def test_letter_not_found(self, mock_observer):
        """Letter returns not_found for missing plan."""
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=None):
            result = await node._letter(mock_observer, "nonexistent")

        assert result.metadata["status"] == "not_found"

    @pytest.mark.asyncio
    async def test_letter_empty(self, mock_observer):
        """Letter returns empty status when no letter written."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.CURIOUS,
            momentum=0.5,
            trajectory=Trajectory.CRUISING,
            season=Season.SPROUTING,
            last_gardened=date.today(),
            gardener="test",
            letter="",  # Empty letter
        )
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=header):
            result = await node._letter(mock_observer, "test")

        assert result.metadata["status"] == "empty"
        assert "no letter" in result.content.lower()

    @pytest.mark.asyncio
    async def test_letter_returns_content(self, mock_observer):
        """Letter returns full letter content."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.EXCITED,
            momentum=0.8,
            trajectory=Trajectory.ACCELERATING,
            season=Season.BLOOMING,
            last_gardened=date.today(),
            gardener="test",
            letter="We made real progress today. The tests are passing.",
        )
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=header):
            result = await node._letter(mock_observer, "test")

        assert result.metadata["status"] == "live"
        assert "real progress" in result.content


# =============================================================================
# Tend Aspect Tests
# =============================================================================


class TestTendAspect:
    """Tests for tend aspect."""

    @pytest.fixture
    def mock_observer(self):
        observer = MagicMock()
        observer.name = "test-gardener"
        return observer

    @pytest.fixture
    def blooming_header(self):
        """Create a BLOOMING plan header."""
        return GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.FOCUSED,
            momentum=0.6,
            trajectory=Trajectory.CRUISING,
            season=Season.BLOOMING,
            last_gardened=date(2025, 12, 17),
            gardener="previous",
            letter="Old letter",
            entropy=EntropyBudget(available=0.10, spent=0.02),
        )

    @pytest.mark.asyncio
    async def test_tend_not_found(self, mock_observer):
        """Tend returns not_found for missing plan."""
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=None):
            result = await node._tend(
                mock_observer,
                "nonexistent",
                gesture_type="code",
                summary="Test",
            )

        assert result.metadata["status"] == "not_found"

    @pytest.mark.asyncio
    async def test_tend_invalid_gesture_type(self, mock_observer, blooming_header):
        """Tend rejects invalid gesture types."""
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=blooming_header):
            result = await node._tend(
                mock_observer,
                "test",
                gesture_type="invalid_gesture",
                summary="Test",
            )

        assert result.metadata["status"] == "error"
        assert "invalid_gesture_type" in result.metadata["error"]

    @pytest.mark.asyncio
    async def test_tend_code_gesture(self, mock_observer, blooming_header):
        """Tend accepts code gesture in BLOOMING season."""
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=blooming_header):
            result = await node._tend(
                mock_observer,
                "test",
                gesture_type="code",
                summary="Added new feature",
                files=["test.py"],
            )

        assert result.metadata["status"] == "ok"
        assert result.metadata["gesture_type"] == "code"
        assert result.metadata["summary"] == "Added new feature"
        assert "test.py" in result.metadata["files"]

    @pytest.mark.asyncio
    async def test_tend_momentum_adjustment(self, mock_observer, blooming_header):
        """Tend adjusts momentum when specified."""
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=blooming_header):
            result = await node._tend(
                mock_observer,
                "test",
                gesture_type="code",
                summary="Big progress",
                momentum_delta=0.1,
            )

        assert result.metadata["new_momentum"] == pytest.approx(0.7)

    @pytest.mark.asyncio
    async def test_tend_mood_change(self, mock_observer, blooming_header):
        """Tend changes mood when specified."""
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=blooming_header):
            result = await node._tend(
                mock_observer,
                "test",
                gesture_type="code",
                summary="Exciting progress",
                mood="excited",
            )

        assert result.metadata["new_mood"] == "excited"

    @pytest.mark.asyncio
    async def test_tend_entropy_sip(self, mock_observer, blooming_header):
        """Tend handles void_sip gesture with entropy."""
        # Put plan in dormant for dreaming
        blooming_header.season = Season.DORMANT
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=blooming_header):
            result = await node._tend(
                mock_observer,
                "test",
                gesture_type="void_sip",
                summary="Exploring tangent",
            )

        assert result.metadata["status"] == "ok"
        assert result.metadata["entropy_spent"] == pytest.approx(0.02)

    @pytest.mark.asyncio
    async def test_tend_entropy_exhausted(self, mock_observer):
        """Tend rejects void_sip when entropy exhausted."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.TIRED,
            momentum=0.3,
            trajectory=Trajectory.DECELERATING,
            season=Season.DORMANT,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            entropy=EntropyBudget(available=0.05, spent=0.05),  # Exhausted
        )
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=header):
            result = await node._tend(
                mock_observer,
                "test",
                gesture_type="void_sip",
                summary="Should fail",
            )

        assert result.metadata["status"] == "error"
        assert result.metadata["error"] == "entropy_exhausted"


# =============================================================================
# Dream Aspect Tests
# =============================================================================


class TestDreamAspect:
    """Tests for dream aspect."""

    @pytest.fixture
    def mock_observer(self):
        observer = MagicMock()
        observer.name = "test-observer"
        return observer

    @pytest.mark.asyncio
    async def test_dream_not_found(self, mock_observer):
        """Dream returns not_found for missing plan."""
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=None):
            result = await node._dream(mock_observer, "nonexistent")

        assert result.metadata["status"] == "not_found"

    @pytest.mark.asyncio
    async def test_dream_requires_dormant(self, mock_observer):
        """Dream rejects non-dormant plans."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.FOCUSED,
            momentum=0.7,
            trajectory=Trajectory.CRUISING,
            season=Season.BLOOMING,  # Not dormant
            last_gardened=date.today(),
            gardener="test",
            letter="",
        )
        node = get_plan_node()

        with patch("protocols.garden.node.load_plan", return_value=header):
            result = await node._dream(mock_observer, "test")

        assert result.metadata["status"] == "error"
        assert result.metadata["error"] == "not_dormant"

    @pytest.mark.asyncio
    async def test_dream_finds_connections(self, mock_observer, tmp_path: Path):
        """Dream finds connections for dormant plans."""
        header = GardenPlanHeader(
            path="self.forest.plan.test",
            mood=Mood.DREAMING,
            momentum=0.0,
            trajectory=Trajectory.PARKED,
            season=Season.DORMANT,
            last_gardened=date.today(),
            gardener="test",
            letter="",
            resonates_with=["existing-resonance"],
        )

        # Create some plan files
        (tmp_path / "test.md").write_text("# Test")
        (tmp_path / "existing-resonance.md").write_text("# Existing")

        node = get_plan_node()

        with (
            patch("protocols.garden.node.load_plan", return_value=header),
            patch("protocols.garden.node._get_plans_dir", return_value=tmp_path),
        ):
            result = await node._dream(mock_observer, "test")

        assert result.metadata["status"] in ["live", "empty"]


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for PlanNode."""

    def test_node_in_registry(self):
        """PlanNode is registered in node registry."""
        from protocols.agentese.registry import get_registry

        registry = get_registry()
        paths = registry.list_paths()

        # After import, self.forest.plan should be registered
        assert "self.forest.plan" in paths

    @pytest.mark.asyncio
    async def test_invoke_aspect_routing(self):
        """_invoke_aspect routes to correct handlers."""
        node = get_plan_node()
        observer = MagicMock()
        observer.name = "test"

        with patch("protocols.garden.node.load_plan", return_value=None):
            # Should route to _manifest
            result = await node._invoke_aspect("manifest", observer, plan_name="test")
            assert "not_found" in str(result.metadata.get("status", ""))

            # Should route to _letter
            result = await node._invoke_aspect("letter", observer, plan_name="test")
            assert "not_found" in str(result.metadata.get("status", ""))

            # Should route to _tend
            result = await node._invoke_aspect(
                "tend", observer, plan_name="test", gesture_type="code", summary="x"
            )
            assert "not_found" in str(result.metadata.get("status", ""))

            # Should route to _dream
            result = await node._invoke_aspect("dream", observer, plan_name="test")
            assert "not_found" in str(result.metadata.get("status", ""))

            # Unknown aspect returns not implemented
            result = await node._invoke_aspect("unknown", observer, plan_name="test")
            assert result["status"] == "not implemented"
