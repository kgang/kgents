"""
Tests for Phase 6: Portal Token → Derivation Bridge.

Verifies:
- Path extraction from AGENTESE paths
- Law 6.2a: Portal Usage Accumulates
- Law 6.2b: Trust Bounded by Confidence
- Bidirectional sync
- Convenience functions

See: spec/protocols/derivation-framework.md §6.2
"""

import pytest

from ..portal_bridge import (
    path_to_agent_name,
    agent_name_to_paths,
    PortalOpenSignal,
    PortalDerivationSync,
    portal_expansion_to_derivation,
    derivation_to_portal_trust,
    sync_portal_expansion,
    get_trust_for_path,
)
from ..types import Derivation, DerivationTier
from ..registry import DerivationRegistry


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def registry() -> DerivationRegistry:
    """Fresh registry for each test."""
    return DerivationRegistry()


@pytest.fixture
def test_agent(registry: DerivationRegistry) -> Derivation:
    """Register a test agent with known confidence."""
    return registry.register(
        agent_name="Brain",
        derives_from=("Compose",),
        principle_draws=(),
        tier=DerivationTier.JEWEL,
    )


# =============================================================================
# Path Extraction Tests
# =============================================================================


class TestPathToAgentName:
    """Tests for path_to_agent_name()."""

    def test_world_path_extraction(self):
        """world.* paths extract and capitalize."""
        assert path_to_agent_name("world.brain") == "Brain"
        assert path_to_agent_name("world.witness") == "Witness"
        assert path_to_agent_name("world.park") == "Park"

    def test_self_path_extraction(self):
        """self.* paths extract and capitalize."""
        assert path_to_agent_name("self.brain") == "Brain"
        assert path_to_agent_name("self.memory") == "Memory"

    def test_concept_agent_path_extraction(self):
        """concept.agent.* paths extract directly."""
        assert path_to_agent_name("concept.agent.Flux") == "Flux"
        assert path_to_agent_name("concept.agent.Brain") == "Brain"

    def test_deep_path_takes_first_component(self):
        """Deep paths take first component after prefix."""
        assert path_to_agent_name("world.brain.persistence") == "Brain"
        assert path_to_agent_name("world.witness.mark") == "Witness"

    def test_empty_path_returns_none(self):
        """Empty path returns None."""
        assert path_to_agent_name("") is None

    def test_unknown_prefix_returns_none(self):
        """Unknown prefix returns None."""
        assert path_to_agent_name("foo.bar") is None
        assert path_to_agent_name("bar") is None


class TestAgentNameToPaths:
    """Tests for agent_name_to_paths()."""

    def test_generates_all_path_variants(self):
        """Generates world, self, and concept paths."""
        paths = agent_name_to_paths("Brain")

        assert "world.brain" in paths
        assert "self.brain" in paths
        assert "concept.agent.Brain" in paths

    def test_lowercase_conversion(self):
        """World and self paths are lowercase."""
        paths = agent_name_to_paths("MyAgent")

        assert "world.myagent" in paths
        assert "self.myagent" in paths


# =============================================================================
# Portal Open Signal Tests
# =============================================================================


class TestPortalOpenSignal:
    """Tests for PortalOpenSignal."""

    def test_from_expansion_creates_signal(self):
        """from_expansion creates signal with all fields."""
        signal = PortalOpenSignal.from_expansion(
            portal_path="world.brain",
            files_opened=["world.witness", "world.park"],
            edge_type="derives_from",
            depth=1,
        )

        assert signal.parent_path == "world.brain"
        assert signal.paths_opened == ("world.witness", "world.park")
        assert signal.edge_type == "derives_from"
        assert signal.depth == 1

    def test_list_converted_to_tuple(self):
        """Files list is converted to tuple."""
        signal = PortalOpenSignal.from_expansion(
            portal_path="x",
            files_opened=["a", "b"],
        )

        assert isinstance(signal.paths_opened, tuple)


# =============================================================================
# Portal → Derivation Tests (Law 6.2a)
# =============================================================================


class TestPortalExpansionToDerivation:
    """Tests for portal expansion → derivation updates."""

    def test_expansion_increments_usage(self, registry: DerivationRegistry, test_agent: Derivation):
        """Portal expansion increments usage count."""
        initial_count = registry.get_usage_count("Brain")

        signal = PortalOpenSignal.from_expansion(
            portal_path="parent",
            files_opened=["world.brain"],
        )
        PortalDerivationSync.portal_expansion_to_derivation(signal, registry)

        assert registry.get_usage_count("Brain") == initial_count + 1

    def test_multiple_paths_increment_each(self, registry: DerivationRegistry):
        """Multiple paths in signal increment each agent."""
        registry.register(
            agent_name="Brain",
            derives_from=("Compose",),
            principle_draws=(),
            tier=DerivationTier.JEWEL,
        )
        registry.register(
            agent_name="Witness",
            derives_from=("Compose",),
            principle_draws=(),
            tier=DerivationTier.JEWEL,
        )

        signal = PortalOpenSignal.from_expansion(
            portal_path="parent",
            files_opened=["world.brain", "world.witness"],
        )
        updated = PortalDerivationSync.portal_expansion_to_derivation(signal, registry)

        assert "Brain" in updated
        assert "Witness" in updated

    def test_unknown_path_ignored(self, registry: DerivationRegistry, test_agent: Derivation):
        """Unknown paths don't cause errors."""
        signal = PortalOpenSignal.from_expansion(
            portal_path="parent",
            files_opened=["world.unknown_agent", "world.brain"],
        )
        updated = PortalDerivationSync.portal_expansion_to_derivation(signal, registry)

        assert "Brain" in updated
        assert "Unknown_agent" not in updated  # Capitalized form

    def test_returns_updated_agents(self, registry: DerivationRegistry, test_agent: Derivation):
        """Returns list of updated agent names."""
        signal = PortalOpenSignal.from_expansion(
            portal_path="parent",
            files_opened=["world.brain"],
        )
        updated = PortalDerivationSync.portal_expansion_to_derivation(signal, registry)

        assert updated == ["Brain"]


# =============================================================================
# Derivation → Portal Tests (Law 6.2b)
# =============================================================================


class TestDerivationToPortalTrust:
    """Tests for derivation → portal trust."""

    def test_unknown_agent_low_trust(self, registry: DerivationRegistry):
        """Unknown agent gets 0.3 trust."""
        trust = PortalDerivationSync.derivation_to_portal_trust("Unknown", registry)
        assert trust == 0.3

    def test_trust_bounded_by_confidence(self, registry: DerivationRegistry, test_agent: Derivation):
        """Trust is bounded by agent confidence."""
        trust = PortalDerivationSync.derivation_to_portal_trust("Brain", registry)

        derivation = registry.get("Brain")
        assert trust <= derivation.total_confidence

    def test_trust_conservative(self, registry: DerivationRegistry, test_agent: Derivation):
        """Trust has 0.9 factor (more conservative than confidence)."""
        trust = PortalDerivationSync.derivation_to_portal_trust("Brain", registry)

        derivation = registry.get("Brain")
        tier_ceiling = derivation.tier.ceiling

        # Trust should be bounded by tier.ceiling * 0.9
        assert trust <= tier_ceiling * 0.9

    def test_bootstrap_agent_high_trust(self, registry: DerivationRegistry):
        """Bootstrap agents have high trust."""
        trust = PortalDerivationSync.derivation_to_portal_trust("Compose", registry)

        # Bootstrap ceiling is 1.0, so trust is 0.9
        assert trust == min(1.0, 1.0 * 0.9)  # 0.9

    def test_bulk_compute_trust(self, registry: DerivationRegistry, test_agent: Derivation):
        """Bulk compute works for multiple agents."""
        trusts = PortalDerivationSync.bulk_compute_trust(
            ["Brain", "Compose", "Unknown"],
            registry,
        )

        assert "Brain" in trusts
        assert "Compose" in trusts
        assert "Unknown" in trusts
        assert trusts["Unknown"] == 0.3


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience wrapper functions."""

    def test_portal_expansion_to_derivation_wrapper(self, registry: DerivationRegistry, test_agent: Derivation):
        """Wrapper function works correctly."""
        signal = PortalOpenSignal.from_expansion(
            portal_path="parent",
            files_opened=["world.brain"],
        )
        updated = portal_expansion_to_derivation(signal, registry)

        assert "Brain" in updated

    def test_derivation_to_portal_trust_wrapper(self, registry: DerivationRegistry, test_agent: Derivation):
        """Wrapper function works correctly."""
        trust = derivation_to_portal_trust("Brain", registry)
        assert 0 < trust <= 1.0

    def test_sync_portal_expansion(self, registry: DerivationRegistry, test_agent: Derivation):
        """One-shot sync function works."""
        updated = sync_portal_expansion(
            portal_path="parent",
            files_opened=["world.brain"],
            registry=registry,
            edge_type="test",
            depth=0,
        )

        assert "Brain" in updated

    def test_get_trust_for_path(self, registry: DerivationRegistry, test_agent: Derivation):
        """Path-based trust lookup works."""
        trust = get_trust_for_path("world.brain", registry)
        assert 0 < trust <= 1.0

    def test_get_trust_for_unknown_path(self, registry: DerivationRegistry):
        """Unknown path returns 0.3."""
        trust = get_trust_for_path("world.unknown", registry)
        assert trust == 0.3


# =============================================================================
# Bidirectional Sync Integration Tests
# =============================================================================


class TestBidirectionalSync:
    """Integration tests for bidirectional sync."""

    def test_usage_increases_stigmergic_confidence(self, registry: DerivationRegistry, test_agent: Derivation):
        """Many usages increase stigmergic confidence over time."""
        initial_trust = derivation_to_portal_trust("Brain", registry)

        # Simulate many expansions
        for _ in range(100):
            signal = PortalOpenSignal.from_expansion(
                portal_path="parent",
                files_opened=["world.brain"],
            )
            portal_expansion_to_derivation(signal, registry)

        # Usage count should be high
        assert registry.get_usage_count("Brain") >= 100

        # Stigmergic confidence should have updated
        derivation = registry.get("Brain")
        assert derivation.stigmergic_confidence > 0

    def test_trust_reflects_derivation_updates(self, registry: DerivationRegistry, test_agent: Derivation):
        """Trust updates when derivation confidence changes."""
        initial_trust = derivation_to_portal_trust("Brain", registry)

        # Update with evidence
        registry.update_evidence("Brain", ashc_score=0.9)

        updated_trust = derivation_to_portal_trust("Brain", registry)

        # Trust should reflect the updated confidence
        derivation = registry.get("Brain")
        assert updated_trust <= derivation.total_confidence
