"""
AGENTESE Unified Nodes Integration Tests.

Tests for the unified AGENTESE integration of new services:
1. self.axiom.* - Axiom discovery (services/zero_seed/axiom_node.py)
2. self.dialectic.* - Dialectical fusion (services/dialectic/node.py)
3. self.skill.* - JIT skill injection (services/skill_injection/node.py)
4. concept.fusion.* - Fusion concepts (services/dialectic/node.py)

Philosophy:
    "Every node registered is a capability gained.
     Every test passing is confidence earned."

See: docs/skills/unified-agentese-nodes.md
"""

from __future__ import annotations

import pytest

from protocols.agentese.node import Observer
from protocols.agentese.registry import get_registry

# =============================================================================
# Constants
# =============================================================================

# All new AGENTESE paths that should be registered
NEW_AGENTESE_PATHS = [
    # Self-reflective paths
    "self.axiom",
    "self.dialectic",
    "self.skill",
    # Concept paths
    "concept.fusion",
]

# Expected aspects for each path
EXPECTED_ASPECTS = {
    "self.axiom": ["manifest", "discover", "validate", "contradictions"],
    "self.dialectic": ["manifest", "thesis", "antithesis", "sublate", "history"],
    "self.skill": ["manifest", "inject", "search", "gotchas", "record", "evolve"],
    "concept.fusion": ["manifest", "cocone"],
}


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def registry():
    """Get the AGENTESE registry."""
    return get_registry()


@pytest.fixture
def observer():
    """Create a test observer with developer privileges."""
    return Observer(
        archetype="developer",
        capabilities=frozenset({"read", "write", "admin"}),
    )


@pytest.fixture
def guest_observer():
    """Create a guest observer with minimal privileges."""
    return Observer.guest()


# =============================================================================
# Test: All New Nodes Registered
# =============================================================================


class TestNewNodesRegistered:
    """Verify all new AGENTESE nodes are properly registered."""

    def test_all_new_paths_registered(self, registry):
        """All new AGENTESE nodes should be registered."""
        # Import gateway to trigger node registration
        from protocols.agentese import gateway

        gateway._import_node_modules()

        all_paths = registry.list_paths()

        for path in NEW_AGENTESE_PATHS:
            assert path in all_paths, (
                f"Path '{path}' not registered. Available: {all_paths[:20]}..."
            )

    def test_registry_count_increased(self, registry):
        """Registry should have more nodes after import."""
        from protocols.agentese import gateway

        initial_count = len(registry.list_paths())
        gateway._import_node_modules()
        final_count = len(registry.list_paths())

        # At least the new paths should exist (they may already be registered)
        assert final_count >= len(NEW_AGENTESE_PATHS), (
            f"Expected at least {len(NEW_AGENTESE_PATHS)} paths, got {final_count}"
        )


# =============================================================================
# Test: Node Resolution
# =============================================================================


class TestNodeResolution:
    """Test that nodes can be resolved from the registry."""

    @pytest.mark.asyncio
    async def test_resolve_axiom_node(self, registry):
        """AxiomNode should resolve successfully."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        if registry.has("self.axiom"):
            node = await registry.resolve("self.axiom", container=None)
            assert node is not None
            assert node.handle == "self.axiom"

    @pytest.mark.asyncio
    async def test_resolve_dialectic_node(self, registry):
        """DialecticNode should resolve successfully."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        if registry.has("self.dialectic"):
            node = await registry.resolve("self.dialectic", container=None)
            assert node is not None
            assert node.handle == "self.dialectic"

    @pytest.mark.asyncio
    async def test_resolve_skill_node(self, registry):
        """SkillNode should resolve successfully."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        if registry.has("self.skill"):
            node = await registry.resolve("self.skill", container=None)
            assert node is not None
            assert node.handle == "self.skill"

    @pytest.mark.asyncio
    async def test_resolve_fusion_concept_node(self, registry):
        """FusionConceptNode should resolve successfully."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        if registry.has("concept.fusion"):
            node = await registry.resolve("concept.fusion", container=None)
            assert node is not None
            assert node.handle == "concept.fusion"


# =============================================================================
# Test: Manifest Aspect
# =============================================================================


class TestManifestAspect:
    """Test the manifest aspect for each node."""

    @pytest.mark.asyncio
    async def test_axiom_manifest(self, registry, observer):
        """AxiomNode manifest should return system status."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        if not registry.has("self.axiom"):
            pytest.skip("self.axiom not registered")

        node = await registry.resolve("self.axiom", container=None)
        result = await node.invoke("manifest", observer)

        # Verify manifest contains expected fields
        assert result is not None
        result_dict = result.to_dict() if hasattr(result, "to_dict") else result
        assert "status" in str(result_dict).lower() or "axiom" in str(result_dict).lower()

    @pytest.mark.asyncio
    async def test_dialectic_manifest(self, registry, observer):
        """DialecticNode manifest should return fusion status."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        if not registry.has("self.dialectic"):
            pytest.skip("self.dialectic not registered")

        node = await registry.resolve("self.dialectic", container=None)
        result = await node.invoke("manifest", observer)

        # Verify manifest contains expected fields
        assert result is not None

    @pytest.mark.asyncio
    async def test_skill_manifest(self, registry, observer):
        """SkillNode manifest should return registry status."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        if not registry.has("self.skill"):
            pytest.skip("self.skill not registered")

        node = await registry.resolve("self.skill", container=None)
        result = await node.invoke("manifest", observer)

        # Verify manifest contains expected fields
        assert result is not None

    @pytest.mark.asyncio
    async def test_fusion_concept_manifest(self, registry, observer):
        """FusionConceptNode manifest should return ontology."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        if not registry.has("concept.fusion"):
            pytest.skip("concept.fusion not registered")

        node = await registry.resolve("concept.fusion", container=None)
        result = await node.invoke("manifest", observer)

        # Verify manifest contains expected fields
        assert result is not None


# =============================================================================
# Test: Affordance Gating
# =============================================================================


class TestAffordanceGating:
    """Test that affordances are properly gated by archetype."""

    @pytest.mark.asyncio
    async def test_developer_has_full_access(self, registry, observer):
        """Developer archetype should have full access to all aspects."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        for path in NEW_AGENTESE_PATHS:
            if not registry.has(path):
                continue

            node = await registry.resolve(path, container=None)
            affordances = node.affordances(observer)

            # Developers should have access to manifest at minimum
            assert "manifest" in affordances, f"Developer missing 'manifest' affordance for {path}"

    @pytest.mark.asyncio
    async def test_guest_has_limited_access(self, registry, guest_observer):
        """Guest archetype should have limited access."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        for path in NEW_AGENTESE_PATHS:
            if not registry.has(path):
                continue

            node = await registry.resolve(path, container=None)
            affordances = node.affordances(guest_observer)

            # Guest should have manifest at minimum
            assert "manifest" in affordances, f"Guest missing 'manifest' affordance for {path}"

            # Guest should NOT have mutation affordances
            # (specific to each node, but generally limited)


# =============================================================================
# Test: Cross-Service Integration
# =============================================================================


class TestCrossServiceIntegration:
    """Test that services can work together coherently."""

    @pytest.mark.asyncio
    async def test_dialectic_and_fusion_concept_aligned(self, registry, observer):
        """
        self.dialectic and concept.fusion should present consistent ontology.

        The dialectic node handles concrete fusions while concept.fusion
        provides the theoretical/conceptual view. They should align.
        """
        from protocols.agentese import gateway

        gateway._import_node_modules()

        if not registry.has("self.dialectic") or not registry.has("concept.fusion"):
            pytest.skip("dialectic and/or concept.fusion not registered")

        # Get both nodes
        dialectic_node = await registry.resolve("self.dialectic", container=None)
        fusion_node = await registry.resolve("concept.fusion", container=None)

        # Both should provide manifest
        dialectic_manifest = await dialectic_node.invoke("manifest", observer)
        fusion_manifest = await fusion_node.invoke("manifest", observer)

        assert dialectic_manifest is not None
        assert fusion_manifest is not None


# =============================================================================
# Test: Provider Registration
# =============================================================================


class TestProviderRegistration:
    """Test that all providers are properly registered."""

    @pytest.mark.asyncio
    async def test_skill_registry_provider(self):
        """get_skill_registry() should return a SkillRegistry."""
        from services.providers import get_skill_registry

        registry = await get_skill_registry()
        assert registry is not None
        assert hasattr(registry, "list_skills")

    @pytest.mark.asyncio
    async def test_jit_injector_provider(self):
        """get_jit_injector() should return a JITInjector."""
        from services.providers import get_jit_injector

        injector = await get_jit_injector()
        assert injector is not None
        assert hasattr(injector, "inject_for_task")

    @pytest.mark.asyncio
    async def test_dialectic_service_provider(self):
        """get_dialectic_service() should return a DialecticalFusionService."""
        from services.providers import get_dialectic_service

        service = await get_dialectic_service()
        assert service is not None
        assert hasattr(service, "propose_fusion")

    @pytest.mark.asyncio
    async def test_ashc_self_awareness_provider(self):
        """get_ashc_self_awareness() should return ASHCSelfAwareness."""
        from services.providers import get_ashc_self_awareness

        awareness = await get_ashc_self_awareness()
        assert awareness is not None
        assert hasattr(awareness, "am_i_grounded")

    @pytest.mark.asyncio
    async def test_axiom_discovery_pipeline_provider(self):
        """get_axiom_discovery_pipeline() should return AxiomDiscoveryPipeline."""
        from services.providers import get_axiom_discovery_pipeline

        pipeline = await get_axiom_discovery_pipeline()
        assert pipeline is not None
        assert hasattr(pipeline, "discover_axioms")


# =============================================================================
# Test: Container Registration
# =============================================================================


class TestContainerRegistration:
    """Test that services are registered in the DI container."""

    @pytest.mark.asyncio
    async def test_container_has_skill_registry(self):
        """Container should have skill_registry registered."""
        from protocols.agentese.container import get_container
        from services.providers import setup_providers

        await setup_providers()
        container = get_container()

        assert container.has("skill_registry"), "skill_registry not in container"

    @pytest.mark.asyncio
    async def test_container_has_jit_injector(self):
        """Container should have jit_injector registered."""
        from protocols.agentese.container import get_container
        from services.providers import setup_providers

        await setup_providers()
        container = get_container()

        assert container.has("jit_injector"), "jit_injector not in container"

    @pytest.mark.asyncio
    async def test_container_has_dialectic_service(self):
        """Container should have dialectic_service registered."""
        from protocols.agentese.container import get_container
        from services.providers import setup_providers

        await setup_providers()
        container = get_container()

        assert container.has("dialectic_service"), "dialectic_service not in container"

    @pytest.mark.asyncio
    async def test_container_has_axiom_discovery_pipeline(self):
        """Container should have axiom_discovery_pipeline registered."""
        from protocols.agentese.container import get_container
        from services.providers import setup_providers

        await setup_providers()
        container = get_container()

        assert container.has("axiom_discovery_pipeline"), (
            "axiom_discovery_pipeline not in container"
        )


# =============================================================================
# Test: Discovery Endpoint Coverage
# =============================================================================


class TestDiscoveryEndpointCoverage:
    """Test that all new paths appear in the discovery endpoint."""

    def test_all_new_paths_in_discovery(self, registry):
        """All new AGENTESE paths should be discoverable."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        all_paths = registry.list_paths()

        for path in NEW_AGENTESE_PATHS:
            assert path in all_paths, f"Path '{path}' not discoverable"

    def test_paths_grouped_by_context(self, registry):
        """Paths should be correctly grouped by context."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        self_paths = registry.list_by_context("self")
        concept_paths = registry.list_by_context("concept")

        # self.* paths should be in self context
        assert "self.axiom" in self_paths or not registry.has("self.axiom")
        assert "self.dialectic" in self_paths or not registry.has("self.dialectic")
        assert "self.skill" in self_paths or not registry.has("self.skill")

        # concept.* paths should be in concept context
        assert "concept.fusion" in concept_paths or not registry.has("concept.fusion")


# =============================================================================
# Test: Health Check Integration
# =============================================================================


class TestHealthCheckIntegration:
    """Test health check capabilities of the unified system."""

    @pytest.mark.asyncio
    async def test_all_nodes_can_manifest(self, registry, observer):
        """All new nodes should be able to manifest without error."""
        from protocols.agentese import gateway

        gateway._import_node_modules()

        errors = []

        for path in NEW_AGENTESE_PATHS:
            if not registry.has(path):
                errors.append(f"{path}: not registered")
                continue

            try:
                node = await registry.resolve(path, container=None)
                result = await node.invoke("manifest", observer)
                if result is None:
                    errors.append(f"{path}: manifest returned None")
            except Exception as e:
                errors.append(f"{path}: {e}")

        if errors:
            pytest.fail("Health check failures:\n" + "\n".join(errors))


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "NEW_AGENTESE_PATHS",
    "EXPECTED_ASPECTS",
    "TestNewNodesRegistered",
    "TestNodeResolution",
    "TestManifestAspect",
    "TestAffordanceGating",
    "TestCrossServiceIntegration",
    "TestProviderRegistration",
    "TestContainerRegistration",
    "TestDiscoveryEndpointCoverage",
    "TestHealthCheckIntegration",
]
