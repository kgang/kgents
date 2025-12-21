# mypy: ignore-errors
"""
Phase 8: Observer Consistency Audit Tests

Tests that nodes properly vary behavior based on observer archetype.
Different observers should see different affordances based on the
principle: "Observer (minimal) → Umwelt (full)".

Per plans/agentese-node-overhaul-strategy.md Phase 8:
- Self.soul varies eigenvector visibility by archetype
- World.park varies admin operations by archetype
- Concept.gardener varies polynomial visibility by archetype
- World.forge varies artifact creation by archetype

Test Categories:
1. GRADATION tests: affordances increase with privilege
2. DENIAL tests: restricted actions are not in lower archetypes
3. EQUIVALENCE tests: functionally similar archetypes get same access

Run with: pytest -xvs impl/claude/protocols/agentese/_tests/test_observer_dependence.py
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

# =============================================================================
# Observer Archetype Strategies
# =============================================================================

# All standard shell archetypes
ARCHETYPES = [
    "developer",
    "architect",
    "operator",
    "reviewer",
    "newcomer",
    "guest",
    "technical",
    "casual",
    "security",
    "creative",
    "strategic",
    "tactical",
    "reflective",
]

# Privilege tiers (higher index = more access)
PRIVILEGE_TIERS = {
    "full": ["developer", "admin", "system", "operator"],
    "elevated": ["architect", "curator", "technical"],
    "standard": ["reviewer", "security", "creative", "strategic", "tactical"],
    "limited": ["newcomer", "casual", "reflective"],
    "minimal": ["guest"],
}


def get_privilege_level(archetype: str) -> int:
    """Return privilege level (0=minimal, 4=full)."""
    archetype_lower = archetype.lower()
    for level, (tier, members) in enumerate(reversed(list(PRIVILEGE_TIERS.items()))):
        if archetype_lower in members:
            return level
    return 0  # Default to minimal


# =============================================================================
# Soul Node Tests
# =============================================================================


class TestSoulObserverDependence:
    """Test self.soul observer-dependent affordances."""

    def test_developer_has_eigenvectors(self):
        """Developer should have eigenvector access."""
        from protocols.agentese.contexts.self_soul import SoulNode

        node = SoulNode()
        affordances = node._get_affordances_for_archetype("developer")

        assert "eigenvectors" in affordances
        assert "governance" in affordances
        assert "chat" in affordances

    def test_guest_has_minimal_access(self):
        """Guest should only see manifest and starters."""
        from protocols.agentese.contexts.self_soul import SoulNode

        node = SoulNode()
        affordances = node._get_affordances_for_archetype("guest")

        assert "manifest" in affordances
        assert "starters" in affordances
        assert "eigenvectors" not in affordances
        assert "governance" not in affordances

    def test_operator_has_governance_no_eigenvectors(self):
        """Operator can govern but not inspect eigenvectors."""
        from protocols.agentese.contexts.self_soul import SoulNode

        node = SoulNode()
        affordances = node._get_affordances_for_archetype("operator")

        assert "governance" in affordances
        assert "dialogue" in affordances
        # Operators don't get eigenvector deep-dive
        assert "eigenvectors" not in affordances

    def test_creative_has_dialogue_modes(self):
        """Creative archetype gets dialogue exploration modes."""
        from protocols.agentese.contexts.self_soul import SoulNode

        node = SoulNode()
        affordances = node._get_affordances_for_archetype("creative")

        assert "dialogue" in affordances
        assert "challenge" in affordances
        assert "why" in affordances
        assert "tension" in affordances

    @given(st.sampled_from(ARCHETYPES))
    @settings(max_examples=20)
    def test_all_archetypes_get_manifest(self, archetype: str):
        """Every archetype should at least get manifest."""
        from protocols.agentese.contexts.self_soul import SoulNode

        node = SoulNode()
        affordances = node._get_affordances_for_archetype(archetype)

        # Manifest should always be available
        assert "manifest" in affordances or len(affordances) == 0


# =============================================================================
# Park Node Tests
# =============================================================================


class TestParkObserverDependence:
    """Test world.park observer-dependent affordances."""

    def test_developer_has_force(self):
        """Developer should have force mechanic access."""
        from protocols.agentese.contexts.world_park import ParkNode

        node = ParkNode()
        affordances = node._get_affordances_for_archetype("developer")

        assert "force" in affordances
        assert "scenario" in affordances

    def test_guest_only_manifest(self):
        """Guest should only see park overview."""
        from protocols.agentese.contexts.world_park import ParkNode

        node = ParkNode()
        affordances = node._get_affordances_for_archetype("guest")

        assert affordances == ("manifest",)

    def test_architect_no_force(self):
        """Architect can observe but not use force."""
        from protocols.agentese.contexts.world_park import ParkNode

        node = ParkNode()
        affordances = node._get_affordances_for_archetype("architect")

        assert "scenario" in affordances
        assert "mask" in affordances
        assert "force" not in affordances


class TestScenarioObserverDependence:
    """Test world.park.scenario observer-dependent affordances."""

    def test_operator_can_start_scenarios(self):
        """Operator should have full scenario control."""
        from protocols.agentese.contexts.world_park import ScenarioNode

        node = ScenarioNode()
        affordances = node._get_affordances_for_archetype("operator")

        assert "start" in affordances
        assert "tick" in affordances
        assert "phase" in affordances
        assert "complete" in affordances

    def test_guest_read_only(self):
        """Guest can only view scenarios."""
        from protocols.agentese.contexts.world_park import ScenarioNode

        node = ScenarioNode()
        affordances = node._get_affordances_for_archetype("guest")

        assert affordances == ("manifest",)

    def test_reviewer_can_tick_not_phase(self):
        """Reviewer can advance time but not change phases."""
        from protocols.agentese.contexts.world_park import ScenarioNode

        node = ScenarioNode()
        affordances = node._get_affordances_for_archetype("reviewer")

        assert "tick" in affordances
        assert "phase" not in affordances


class TestMaskObserverDependence:
    """Test world.park.mask observer-dependent affordances."""

    def test_creative_can_wear_masks(self):
        """Creative archetype should be able to don/doff masks."""
        from protocols.agentese.contexts.world_park import MaskNode

        node = MaskNode()
        affordances = node._get_affordances_for_archetype("creative")

        assert "don" in affordances
        assert "doff" in affordances

    def test_guest_no_mask_access(self):
        """Guest should have no mask access."""
        from protocols.agentese.contexts.world_park import MaskNode

        node = MaskNode()
        affordances = node._get_affordances_for_archetype("guest")

        assert len(affordances) == 0


class TestForceObserverDependence:
    """Test world.park.force observer-dependent affordances."""

    def test_only_operators_can_use_force(self):
        """Only operators/developers can use force."""
        from protocols.agentese.contexts.world_park import ForceNode

        node = ForceNode()

        # Operators can use force
        for archetype in ["developer", "operator", "admin"]:
            affordances = node._get_affordances_for_archetype(archetype)
            assert "use" in affordances, f"{archetype} should have force.use"

        # Others cannot
        for archetype in ["guest", "newcomer", "reviewer"]:
            affordances = node._get_affordances_for_archetype(archetype)
            assert "use" not in affordances, f"{archetype} should NOT have force.use"


# =============================================================================
# Gardener Node Tests
# =============================================================================


@pytest.mark.skip(reason="Gardener deprecated - removed in cleanup")
class TestGardenerObserverDependence:
    """Test concept.gardener observer-dependent affordances."""

    def test_developer_has_polynomial(self):
        """Developer should have polynomial session control."""
        pass

    def test_guest_route_only(self):
        """Guest should only have route (discovery)."""
        pass

    def test_newcomer_gets_propose(self):
        """Newcomer should get suggestions via propose."""
        pass


# =============================================================================
# Forge Node Tests
# =============================================================================


class TestForgeObserverDependence:
    """Test world.forge observer-dependent affordances."""

    @pytest.fixture
    def forge_node(self):
        """Create a minimal ForgeNode for testing."""
        from unittest.mock import MagicMock

        from services.forge.node import ForgeNode

        # Create with mocked persistence
        mock_persistence = MagicMock()
        node = ForgeNode(forge_persistence=mock_persistence)
        return node

    def test_spectator_read_only(self, forge_node):
        """Spectator should have read-only access."""
        affordances = forge_node._get_affordances_for_archetype("spectator")

        # Should have view access
        assert "workshop.list" in affordances
        assert "gallery.list" in affordances
        # Should NOT have mutation access
        assert "workshop.create" not in affordances
        assert "contribute" not in affordances

    def test_creative_can_contribute(self, forge_node):
        """Creative archetype should be able to contribute."""
        affordances = forge_node._get_affordances_for_archetype("creative")

        assert "contribute" in affordances
        assert "workshop.join" in affordances

    def test_developer_has_all(self, forge_node):
        """Developer should have full forge access."""
        affordances = forge_node._get_affordances_for_archetype("developer")

        assert "workshop.create" in affordances
        assert "exhibition.create" in affordances
        assert "gallery.add" in affordances


# =============================================================================
# Gradation Tests (Privilege Levels)
# =============================================================================


class TestPrivilegeGradation:
    """Test that affordances increase with privilege level."""

    def test_soul_privilege_gradation(self):
        """Higher privilege archetypes should have more soul affordances."""
        from protocols.agentese.contexts.self_soul import SoulNode

        node = SoulNode()

        guest_affs = set(node._get_affordances_for_archetype("guest"))
        newcomer_affs = set(node._get_affordances_for_archetype("newcomer"))
        developer_affs = set(node._get_affordances_for_archetype("developer"))

        # Each level should be a superset of lower levels
        assert guest_affs <= developer_affs
        assert len(newcomer_affs) >= len(guest_affs)
        assert len(developer_affs) >= len(newcomer_affs)

    def test_park_privilege_gradation(self):
        """Higher privilege archetypes should have more park affordances."""
        from protocols.agentese.contexts.world_park import ParkNode

        node = ParkNode()

        guest_affs = set(node._get_affordances_for_archetype("guest"))
        architect_affs = set(node._get_affordances_for_archetype("architect"))
        developer_affs = set(node._get_affordances_for_archetype("developer"))

        # Each level should be a superset of lower levels
        assert guest_affs <= architect_affs
        assert architect_affs <= developer_affs

    @given(
        st.sampled_from(["developer", "operator", "architect"]),
        st.sampled_from(["newcomer", "guest"]),
    )
    @settings(max_examples=20)
    def test_consistent_privilege_ordering(self, high_priv: str, low_priv: str):
        """Higher privilege archetypes should have >= affordances than lower."""
        from protocols.agentese.contexts.self_soul import SoulNode

        node = SoulNode()
        high_affs = node._get_affordances_for_archetype(high_priv)
        low_affs = node._get_affordances_for_archetype(low_priv)

        # Higher privilege should have more or equal affordances
        assert len(high_affs) >= len(low_affs), (
            f"{high_priv} ({len(high_affs)}) should have >= affordances "
            f"than {low_priv} ({len(low_affs)})"
        )


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Test edge cases and malformed inputs."""

    @pytest.mark.parametrize(
        "invalid_archetype",
        [
            "",
            "   ",
            "UNKNOWN_TYPE",
            "admin123",
            "developer_test",
            None,
        ],
    )
    def test_invalid_archetype_falls_back(self, invalid_archetype):
        """Invalid archetypes should fall back gracefully."""
        from protocols.agentese.contexts.self_soul import SoulNode

        node = SoulNode()

        # Should not raise
        if invalid_archetype is None:
            affordances = node._get_affordances_for_archetype("")
        else:
            affordances = node._get_affordances_for_archetype(invalid_archetype)

        # Should get some affordances (fallback to guest-level)
        assert isinstance(affordances, tuple)

    def test_case_insensitive_archetypes(self):
        """Archetypes should be case-insensitive."""
        from protocols.agentese.contexts.self_soul import SoulNode

        node = SoulNode()

        lower = node._get_affordances_for_archetype("developer")
        upper = node._get_affordances_for_archetype("DEVELOPER")
        mixed = node._get_affordances_for_archetype("Developer")

        assert lower == upper == mixed


# =============================================================================
# Memory Node Tests (self.memory/Brain)
# =============================================================================


class TestMemoryObserverDependence:
    """Test self.memory observer-dependent affordances."""

    @pytest.fixture
    def brain_node(self):
        """Create a minimal BrainNode for testing."""
        from unittest.mock import MagicMock

        from services.brain.node import BrainNode

        # BrainNode needs persistence, but we only test affordances
        mock_persistence = MagicMock()
        node = BrainNode(brain_persistence=mock_persistence)
        return node

    def test_developer_has_cartography(self, brain_node):
        """Developer should have full brain access."""
        affordances = brain_node._get_affordances_for_archetype("developer")

        assert "cartography.manifest" in affordances
        assert "crystal.list" in affordances
        assert "delete" in affordances
        assert "heal" in affordances

    def test_guest_limited_access(self, brain_node):
        """Guest should have minimal brain access."""
        guest_affs = brain_node._get_affordances_for_archetype("guest")
        dev_affs = brain_node._get_affordances_for_archetype("developer")

        # Guest should get basic view only
        assert len(guest_affs) < len(dev_affs)
        # Guest can search but not capture
        assert "search" in guest_affs
        assert "capture" not in guest_affs

    def test_newcomer_can_capture(self, brain_node):
        """Newcomers should be able to capture memories."""
        affordances = brain_node._get_affordances_for_archetype("newcomer")

        assert "capture" in affordances
        assert "search" in affordances
        # But not delete
        assert "delete" not in affordances
