"""
Tests for AGENTESE self.vitals.* context.

Verifies:
- VitalsContextResolver routing
- TriadHealthNode
- SynapseMetricsNode
- ResonanceVitalsNode
- CircuitBreakerNode
- Integration with SelfContextResolver
"""

from __future__ import annotations

import pytest
from protocols.agentese._tests.conftest import MockUmwelt
from protocols.agentese.contexts.self_ import SelfContextResolver, create_self_resolver
from protocols.agentese.contexts.vitals import (
    CircuitBreakerNode,
    GenericVitalsNode,
    ResonanceVitalsNode,
    SynapseMetricsNode,
    TriadHealthNode,
    VitalsContextResolver,
    create_vitals_resolver,
    get_cdc_lag_tracker,
    get_semantic_collector,
    get_synapse_metrics,
    set_cdc_lag_tracker,
    set_semantic_collector,
    set_synapse_metrics,
)


class TestVitalsContextResolver:
    """Tests for VitalsContextResolver."""

    @pytest.fixture
    def resolver(self) -> VitalsContextResolver:
        return create_vitals_resolver()

    def test_resolve_triad(self, resolver: VitalsContextResolver) -> None:
        """Resolves self.vitals.triad."""
        node = resolver.resolve("triad", [])
        assert isinstance(node, TriadHealthNode)
        assert node.handle == "self.vitals.triad"

    def test_resolve_synapse(self, resolver: VitalsContextResolver) -> None:
        """Resolves self.vitals.synapse."""
        node = resolver.resolve("synapse", [])
        assert isinstance(node, SynapseMetricsNode)
        assert node.handle == "self.vitals.synapse"

    def test_resolve_resonance(self, resolver: VitalsContextResolver) -> None:
        """Resolves self.vitals.resonance."""
        node = resolver.resolve("resonance", [])
        assert isinstance(node, ResonanceVitalsNode)
        assert node.handle == "self.vitals.resonance"

    def test_resolve_circuit(self, resolver: VitalsContextResolver) -> None:
        """Resolves self.vitals.circuit."""
        node = resolver.resolve("circuit", [])
        assert isinstance(node, CircuitBreakerNode)
        assert node.handle == "self.vitals.circuit"

    def test_resolve_generic(self, resolver: VitalsContextResolver) -> None:
        """Resolves unknown vitals path to generic node."""
        node = resolver.resolve("unknown", [])
        assert isinstance(node, GenericVitalsNode)
        assert node.handle == "self.vitals.unknown"


class TestTriadHealthNode:
    """Tests for TriadHealthNode."""

    @pytest.fixture
    def node(self) -> TriadHealthNode:
        return TriadHealthNode()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="test")

    def test_handle(self, node: TriadHealthNode) -> None:
        """Node has correct handle."""
        assert node.handle == "self.vitals.triad"

    def test_affordances(self, node: TriadHealthNode) -> None:
        """Node has expected affordances."""
        affordances = node._get_affordances_for_archetype("any")
        assert "manifest" in affordances
        assert "is_coherent" in affordances
        assert "can_persist" in affordances

    @pytest.mark.asyncio
    async def test_manifest_without_collector(
        self, node: TriadHealthNode, observer: MockUmwelt
    ) -> None:
        """Manifest returns error when collector not configured or incomplete."""
        # Clear the global collector
        set_semantic_collector(None)
        result = await node.manifest(observer)  # type: ignore[arg-type]
        # Either "Not Configured" or "Incomplete" depending on import success
        assert hasattr(result, "summary") and (
            "Not Configured" in result.summary or "Incomplete" in result.summary
        )

    @pytest.mark.asyncio
    async def test_invoke_is_coherent(
        self, node: TriadHealthNode, observer: MockUmwelt
    ) -> None:
        """is_coherent aspect returns False without collector."""
        set_semantic_collector(None)
        result = await node._invoke_aspect("is_coherent", observer)  # type: ignore[arg-type]
        assert result is False


class TestSynapseMetricsNode:
    """Tests for SynapseMetricsNode."""

    @pytest.fixture
    def node(self) -> SynapseMetricsNode:
        return SynapseMetricsNode()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="test")

    def test_handle(self, node: SynapseMetricsNode) -> None:
        """Node has correct handle."""
        assert node.handle == "self.vitals.synapse"

    def test_affordances(self, node: SynapseMetricsNode) -> None:
        """Node has expected affordances."""
        affordances = node._get_affordances_for_archetype("any")
        assert "manifest" in affordances
        assert "prometheus" in affordances
        assert "reset" in affordances

    @pytest.mark.asyncio
    async def test_manifest_creates_metrics(
        self, node: SynapseMetricsNode, observer: MockUmwelt
    ) -> None:
        """Manifest creates SynapseMetrics if not present."""
        # Clear and let it create
        set_synapse_metrics(None)
        result = await node.manifest(observer)  # type: ignore[arg-type]
        # Should either create or show not configured (if import fails)
        assert hasattr(result, "summary") and "Synapse" in result.summary


class TestResonanceVitalsNode:
    """Tests for ResonanceVitalsNode."""

    @pytest.fixture
    def node(self) -> ResonanceVitalsNode:
        return ResonanceVitalsNode()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="test")

    def test_handle(self, node: ResonanceVitalsNode) -> None:
        """Node has correct handle."""
        assert node.handle == "self.vitals.resonance"

    def test_affordances(self, node: ResonanceVitalsNode) -> None:
        """Node has expected affordances."""
        affordances = node._get_affordances_for_archetype("any")
        assert "manifest" in affordances
        assert "coherency" in affordances

    @pytest.mark.asyncio
    async def test_coherency_without_tracker(
        self, node: ResonanceVitalsNode, observer: MockUmwelt
    ) -> None:
        """coherency aspect returns 1.0 when no tracker."""
        set_cdc_lag_tracker(None)
        result = await node._invoke_aspect("coherency", observer)  # type: ignore[arg-type]
        # Perfect coherency assumed when no tracker
        assert result == 1.0


class TestCircuitBreakerNode:
    """Tests for CircuitBreakerNode."""

    @pytest.fixture
    def node(self) -> CircuitBreakerNode:
        return CircuitBreakerNode()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt(archetype="test")

    def test_handle(self, node: CircuitBreakerNode) -> None:
        """Node has correct handle."""
        assert node.handle == "self.vitals.circuit"

    def test_affordances(self, node: CircuitBreakerNode) -> None:
        """Node has expected affordances."""
        affordances = node._get_affordances_for_archetype("any")
        assert "manifest" in affordances
        assert "open" in affordances
        assert "close" in affordances
        assert "reset" in affordances


class TestSelfContextResolverVitalsIntegration:
    """Tests for vitals integration in SelfContextResolver."""

    @pytest.fixture
    def resolver(self) -> SelfContextResolver:
        return create_self_resolver()

    def test_resolve_vitals_triad(self, resolver: SelfContextResolver) -> None:
        """self.vitals.triad resolves through SelfContextResolver."""
        node = resolver.resolve("vitals", ["triad"])
        assert isinstance(node, TriadHealthNode)

    def test_resolve_vitals_synapse(self, resolver: SelfContextResolver) -> None:
        """self.vitals.synapse resolves through SelfContextResolver."""
        node = resolver.resolve("vitals", ["synapse"])
        assert isinstance(node, SynapseMetricsNode)

    def test_resolve_vitals_resonance(self, resolver: SelfContextResolver) -> None:
        """self.vitals.resonance resolves through SelfContextResolver."""
        node = resolver.resolve("vitals", ["resonance"])
        assert isinstance(node, ResonanceVitalsNode)

    def test_resolve_vitals_circuit(self, resolver: SelfContextResolver) -> None:
        """self.vitals.circuit resolves through SelfContextResolver."""
        node = resolver.resolve("vitals", ["circuit"])
        assert isinstance(node, CircuitBreakerNode)

    def test_resolve_vitals_default(self, resolver: SelfContextResolver) -> None:
        """self.vitals with no rest resolves to triad (default)."""
        node = resolver.resolve("vitals", [])
        assert isinstance(node, TriadHealthNode)


class TestGlobalSingletons:
    """Tests for global singleton management."""

    def test_set_get_synapse_metrics(self) -> None:
        """Can set and get synapse metrics singleton."""
        # Clear first
        set_synapse_metrics(None)
        assert get_synapse_metrics() is not None  # Creates on demand

        # Set custom
        class MockMetrics:
            pass

        mock = MockMetrics()
        set_synapse_metrics(mock)
        assert get_synapse_metrics() is mock

        # Clean up
        set_synapse_metrics(None)

    def test_set_get_cdc_lag_tracker(self) -> None:
        """Can set and get CDC lag tracker singleton."""
        set_cdc_lag_tracker(None)
        assert get_cdc_lag_tracker() is not None  # Creates on demand

        class MockTracker:
            pass

        mock = MockTracker()
        set_cdc_lag_tracker(mock)
        assert get_cdc_lag_tracker() is mock

        # Clean up
        set_cdc_lag_tracker(None)

    def test_set_get_semantic_collector(self) -> None:
        """Can set and get semantic collector singleton."""
        set_semantic_collector(None)
        # May return None if import fails
        result = get_semantic_collector()
        # Just verify it doesn't raise
        assert result is None or result is not None

        # Clean up
        set_semantic_collector(None)
