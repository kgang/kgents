"""
Tests for AGENTESE Phase 7: Wire to Logos

Tests the WiredLogos class and its integration with:
- UmweltIntegration (observer handling)
- LgentIntegration (registry/catalog)
- GgentIntegration (grammar/validation)
- MembraneAgenteseBridge (CLI bridging)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from ..exceptions import (
    AffordanceError,
    ObserverRequiredError,
    PathNotFoundError,
    PathSyntaxError,
)
from ..integration import (
    AgentesIntegrations,
)
from ..logos import Logos, create_logos
from ..node import AgentMeta, BasicRendering
from ..wiring import (
    WiredLogos,
    create_minimal_wired_logos,
    create_wired_logos,
    wire_existing_logos,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@dataclass
class MockDNA:
    """Mock DNA for testing."""

    name: str = "test_agent"
    archetype: str = "architect"
    capabilities: tuple[str, ...] = ()


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing."""

    dna: MockDNA = field(default_factory=MockDNA)
    state: Any = None
    gravity: tuple = ()


@dataclass
class MockLgentEntry:
    """Mock L-gent catalog entry."""

    id: str
    name: str
    entity_type: str = "agent"
    status: str = "active"
    usage_count: int = 0
    success_count: int = 0


class MockLgentRegistry:
    """Mock L-gent registry for testing."""

    def __init__(self):
        self._entries: dict[str, MockLgentEntry] = {}
        self._usage_log: list[tuple[str, bool, str | None]] = []

    async def get(self, entry_id: str) -> MockLgentEntry | None:
        return self._entries.get(entry_id)

    async def register(self, entry: Any) -> None:
        self._entries[entry.id] = entry

    async def record_usage(
        self,
        entry_id: str,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        self._usage_log.append((entry_id, success, error))

    async def list_by_type(self, entity_type: Any) -> list[MockLgentEntry]:
        return list(self._entries.values())


class MockGrammarian:
    """Mock G-gent grammarian for testing."""

    async def reify(self, **kwargs) -> dict:
        return {"name": kwargs.get("name", "AgenteseTongue")}


@pytest.fixture
def mock_umwelt() -> MockUmwelt:
    """Create a mock Umwelt."""
    return MockUmwelt()


@pytest.fixture
def architect_umwelt() -> MockUmwelt:
    """Create an architect Umwelt."""
    return MockUmwelt(dna=MockDNA(archetype="architect"))


@pytest.fixture
def poet_umwelt() -> MockUmwelt:
    """Create a poet Umwelt."""
    return MockUmwelt(dna=MockDNA(archetype="poet"))


@pytest.fixture
def mock_lgent_registry() -> MockLgentRegistry:
    """Create a mock L-gent registry."""
    return MockLgentRegistry()


@pytest.fixture
def mock_grammarian() -> MockGrammarian:
    """Create a mock G-gent grammarian."""
    return MockGrammarian()


@pytest.fixture
def wired_logos(
    mock_lgent_registry: MockLgentRegistry,
    mock_grammarian: MockGrammarian,
) -> WiredLogos:
    """Create a fully wired Logos for testing."""
    return create_wired_logos(
        spec_root=Path("spec"),
        lgent_registry=mock_lgent_registry,
        grammarian=mock_grammarian,
    )


@pytest.fixture
def minimal_wired_logos() -> WiredLogos:
    """Create a minimal WiredLogos for testing."""
    return create_minimal_wired_logos()


# =============================================================================
# Test WiredLogos Creation
# =============================================================================


class TestWiredLogosCreation:
    """Tests for WiredLogos factory functions."""

    def test_create_wired_logos_basic(self) -> None:
        """Test creating a basic WiredLogos."""
        wired = create_wired_logos()
        assert isinstance(wired, WiredLogos)
        assert isinstance(wired.logos, Logos)
        assert isinstance(wired.integrations, AgentesIntegrations)

    def test_create_wired_logos_with_integrations(
        self,
        mock_lgent_registry: MockLgentRegistry,
        mock_grammarian: MockGrammarian,
    ):
        """Test creating WiredLogos with integrations."""
        wired = create_wired_logos(
            lgent_registry=mock_lgent_registry,
            grammarian=mock_grammarian,
        )
        assert wired.integrations.lgent.registry is not None
        assert wired.integrations.ggent.grammarian is not None

    def test_create_minimal_wired_logos(self) -> None:
        """Test creating minimal WiredLogos."""
        wired = create_minimal_wired_logos()
        assert wired.validate_paths is True
        assert wired.track_usage is False

    def test_wire_existing_logos(self, mock_lgent_registry: MockLgentRegistry) -> None:
        """Test wiring integrations to existing Logos."""
        logos = create_logos()
        wired = wire_existing_logos(logos, lgent_registry=mock_lgent_registry)
        assert wired.logos is logos
        assert wired.integrations.lgent.registry is not None

    def test_membrane_bridge_auto_created(self) -> None:
        """Test that membrane bridge is auto-created."""
        wired = create_wired_logos()
        assert wired.integrations.membrane is not None
        # The bridge's logos points to either the WiredLogos or inner Logos
        # What matters is that it's connected to a working resolver
        assert wired.integrations.membrane.logos is not None


# =============================================================================
# Test Path Validation (G-gent Integration)
# =============================================================================


class TestPathValidation:
    """Tests for G-gent path validation."""

    def test_valid_path_passes_validation(self, wired_logos: WiredLogos) -> None:
        """Test that valid paths pass validation."""
        # These should not raise
        wired_logos._validate_path("world.house")
        wired_logos._validate_path("world.house.manifest")
        wired_logos._validate_path("self.memory.consolidate")
        wired_logos._validate_path("concept.justice.refine")
        wired_logos._validate_path("void.entropy.sip")
        wired_logos._validate_path("time.trace.witness")

    def test_invalid_context_raises_error(self, wired_logos: WiredLogos) -> None:
        """Test that invalid context raises PathSyntaxError."""
        with pytest.raises(PathSyntaxError) as exc_info:
            wired_logos._validate_path("invalid.house.manifest")
        assert "Invalid context" in str(exc_info.value)

    def test_incomplete_path_raises_error(self, wired_logos: WiredLogos) -> None:
        """Test that incomplete path raises PathSyntaxError."""
        with pytest.raises(PathSyntaxError) as exc_info:
            wired_logos._validate_path("world")
        assert "at least context.holon" in str(exc_info.value)

    def test_invalid_identifier_raises_error(self, wired_logos: WiredLogos) -> None:
        """Test that invalid identifiers raise PathSyntaxError."""
        with pytest.raises(PathSyntaxError):
            wired_logos._validate_path("world.UPPERCASE.manifest")

        with pytest.raises(PathSyntaxError):
            wired_logos._validate_path("world.123invalid.manifest")

    def test_validation_can_be_disabled(self) -> None:
        """Test that validation can be disabled."""
        wired = create_wired_logos(validate_paths=False)
        # This would normally fail validation but shouldn't raise
        # Note: Still might fail on resolve(), but validation doesn't run
        assert wired.validate_paths is False


# =============================================================================
# Test Observer Meta Extraction (Umwelt Integration)
# =============================================================================


class TestUmweltIntegration:
    """Tests for UmweltIntegration in WiredLogos."""

    def test_extract_meta_from_umwelt(
        self,
        wired_logos: WiredLogos,
        architect_umwelt: MockUmwelt,
    ):
        """Test extracting AgentMeta from Umwelt."""
        meta = wired_logos.integrations.umwelt.extract_meta(architect_umwelt)
        assert isinstance(meta, AgentMeta)
        assert meta.archetype == "architect"

    def test_different_archetypes_have_different_affordances(
        self,
        wired_logos: WiredLogos,
        architect_umwelt: MockUmwelt,
        poet_umwelt: MockUmwelt,
    ):
        """Test that different archetypes get different affordances."""
        architect_affordances = wired_logos.integrations.umwelt.get_affordances(
            architect_umwelt
        )
        poet_affordances = wired_logos.integrations.umwelt.get_affordances(poet_umwelt)

        assert "renovate" in architect_affordances
        assert "renovate" not in poet_affordances
        assert "describe" in poet_affordances

    def test_can_invoke_checks_affordances(
        self,
        wired_logos: WiredLogos,
        architect_umwelt: MockUmwelt,
        poet_umwelt: MockUmwelt,
    ):
        """Test can_invoke checks observer affordances."""
        assert wired_logos.integrations.umwelt.can_invoke(architect_umwelt, "renovate")
        assert not wired_logos.integrations.umwelt.can_invoke(poet_umwelt, "renovate")


# =============================================================================
# Test Registry Lookup (L-gent Integration)
# =============================================================================


class TestLgentIntegration:
    """Tests for L-gent registry integration."""

    @pytest.mark.asyncio
    async def test_track_invocation_success(
        self,
        wired_logos: WiredLogos,
        mock_lgent_registry: MockLgentRegistry,
    ):
        """Test that successful invocations are tracked."""
        await wired_logos._track_invocation("world.house.manifest", True)
        assert len(mock_lgent_registry._usage_log) == 1
        assert mock_lgent_registry._usage_log[0] == ("world.house.manifest", True, None)

    @pytest.mark.asyncio
    async def test_track_invocation_failure(
        self,
        wired_logos: WiredLogos,
        mock_lgent_registry: MockLgentRegistry,
    ):
        """Test that failed invocations are tracked with error."""
        await wired_logos._track_invocation(
            "world.house.manifest",
            False,
            "Test error",
        )
        assert mock_lgent_registry._usage_log[0] == (
            "world.house.manifest",
            False,
            "Test error",
        )

    @pytest.mark.asyncio
    async def test_graceful_degradation_without_registry(self) -> None:
        """Test that missing L-gent doesn't break WiredLogos."""
        wired = create_wired_logos(lgent_registry=None)
        # Should not raise
        await wired._track_invocation("world.house.manifest", True)


# =============================================================================
# Test Membrane Bridge
# =============================================================================


class TestMembraneBridge:
    """Tests for Membrane-AGENTESE bridge."""

    def test_get_agentese_path(self, wired_logos: WiredLogos) -> None:
        """Test getting AGENTESE path from Membrane command."""
        assert wired_logos.get_agentese_path("observe") == "world.project.manifest"
        assert wired_logos.get_agentese_path("sense") == "world.project.sense"
        assert wired_logos.get_agentese_path("trace") == "time.trace.witness"
        assert wired_logos.get_agentese_path("dream") == "self.memory.consolidate"
        assert wired_logos.get_agentese_path("sip") == "void.entropy.sip"

    def test_unknown_command_returns_none(self, wired_logos: WiredLogos) -> None:
        """Test that unknown commands return None."""
        assert wired_logos.get_agentese_path("unknown_command") is None

    @pytest.mark.asyncio
    async def test_execute_membrane_command(
        self,
        wired_logos: WiredLogos,
        architect_umwelt: MockUmwelt,
    ):
        """Test executing Membrane command via AGENTESE."""
        # The "observe" command maps to "world.project.manifest"
        # WorldContextResolver creates placeholder nodes, so this succeeds
        result = await wired_logos.execute_membrane_command("observe", architect_umwelt)
        # For architects, should return BlueprintRendering
        assert result is not None

    @pytest.mark.asyncio
    async def test_execute_unknown_membrane_command_raises(
        self,
        wired_logos: WiredLogos,
        architect_umwelt: MockUmwelt,
    ):
        """Test that unknown Membrane commands raise PathNotFoundError."""
        with pytest.raises(PathNotFoundError):
            await wired_logos.execute_membrane_command("unknown_cmd", architect_umwelt)


# =============================================================================
# Test Integration Status
# =============================================================================


class TestIntegrationStatus:
    """Tests for integration status reporting."""

    def test_full_integration_status(
        self,
        mock_lgent_registry: MockLgentRegistry,
        mock_grammarian: MockGrammarian,
    ):
        """Test status when all integrations available."""
        wired = create_wired_logos(
            lgent_registry=mock_lgent_registry,
            grammarian=mock_grammarian,
        )
        status = wired.integration_status()
        assert status["umwelt"] is True
        assert status["lgent"] is True
        assert status["ggent"] is True
        assert status["membrane"] is True

    def test_minimal_integration_status(self) -> None:
        """Test status with minimal integrations."""
        wired = create_minimal_wired_logos()
        status = wired.integration_status()
        assert status["umwelt"] is True
        assert status["lgent"] is False
        assert status["ggent"] is False
        assert status["membrane"] is True  # Auto-created


# =============================================================================
# Test Composition
# =============================================================================


class TestComposition:
    """Tests for path composition with validation."""

    def test_compose_with_validation(self, wired_logos: WiredLogos) -> None:
        """Test that compose validates all paths."""
        composed = wired_logos.compose(
            "world.house.manifest",
            "concept.summary.refine",
        )
        assert len(composed) == 2

    def test_compose_invalid_path_raises(self, wired_logos: WiredLogos) -> None:
        """Test that compose fails on invalid path."""
        with pytest.raises(PathSyntaxError):
            wired_logos.compose(
                "world.house.manifest",
                "invalid.path",  # Invalid context
            )

    def test_compose_validation_disabled(self) -> None:
        """Test compose without validation."""
        wired = create_wired_logos(validate_paths=False)
        # Should not raise even with invalid path
        composed = wired.compose(
            "world.house.manifest",
            "invalid.path",
        )
        assert len(composed) == 2

    def test_identity(self, wired_logos: WiredLogos) -> None:
        """Test identity morphism."""
        identity = wired_logos.identity()
        assert identity.name == "Id"

    def test_path_creates_composed(self, wired_logos: WiredLogos) -> None:
        """Test path() creates ComposedPath."""
        composed = wired_logos.path("world.house.manifest")
        assert len(composed) == 1


# =============================================================================
# Test Autopoiesis (define_concept)
# =============================================================================


class TestAutopoiesis:
    """Tests for concept definition (autopoiesis)."""

    @pytest.mark.asyncio
    async def test_define_concept_validates_handle(
        self,
        wired_logos: WiredLogos,
        architect_umwelt: MockUmwelt,
    ):
        """Test that define_concept validates handle syntax."""
        with pytest.raises(PathSyntaxError):
            await wired_logos.define_concept(
                "invalid",  # Too short
                "spec content",
                architect_umwelt,
            )

    @pytest.mark.asyncio
    async def test_define_concept_checks_affordance(
        self,
        wired_logos: WiredLogos,
        poet_umwelt: MockUmwelt,
    ):
        """Test that define_concept checks observer affordance."""
        with pytest.raises(AffordanceError):
            await wired_logos.define_concept(
                "world.garden",
                "spec content",
                poet_umwelt,  # Poet cannot define
            )

    @pytest.mark.asyncio
    async def test_define_concept_registers_in_lgent(
        self,
        mock_lgent_registry: MockLgentRegistry,
        mock_grammarian: MockGrammarian,
        architect_umwelt: MockUmwelt,
    ):
        """Test that define_concept registers in L-gent."""
        wired = create_wired_logos(
            lgent_registry=mock_lgent_registry,
            grammarian=mock_grammarian,
        )

        # Define concept (will create JIT node)
        # Note: spec needs 'entity' field per JIT compiler requirements
        spec = """---
entity: garden
name: garden
handle: world.garden
affordances:
  default: [manifest, witness]
---
# Garden
A beautiful garden.
"""
        node = await wired.define_concept("world.garden", spec, architect_umwelt)

        # Check L-gent registration
        assert "world.garden" in mock_lgent_registry._entries


# =============================================================================
# Test Resolve with Integration
# =============================================================================


class TestResolve:
    """Tests for resolve() with integrations."""

    def test_resolve_validates_path(self, wired_logos: WiredLogos) -> None:
        """Test that resolve validates path first."""
        with pytest.raises(PathSyntaxError):
            wired_logos.resolve("invalid.path")

    def test_resolve_with_validation_disabled(self) -> None:
        """Test resolve without validation."""
        wired = create_wired_logos(validate_paths=False)
        # Should fail on context, not validation
        with pytest.raises(PathNotFoundError):
            wired.resolve("invalid.path")


# =============================================================================
# Test Invoke with Integration
# =============================================================================


class TestInvoke:
    """Tests for invoke() with integrations."""

    @pytest.mark.asyncio
    async def test_invoke_requires_observer(self, wired_logos: WiredLogos) -> None:
        """Test that invoke requires observer."""
        with pytest.raises(ObserverRequiredError):
            await wired_logos.invoke("world.house.manifest", None)

    @pytest.mark.asyncio
    async def test_invoke_validates_path(
        self,
        wired_logos: WiredLogos,
        architect_umwelt: MockUmwelt,
    ):
        """Test that invoke validates path."""
        with pytest.raises(PathSyntaxError):
            await wired_logos.invoke("invalid.path.manifest", architect_umwelt)

    @pytest.mark.asyncio
    async def test_invoke_tracks_success(
        self,
        wired_logos: WiredLogos,
        mock_lgent_registry: MockLgentRegistry,
        architect_umwelt: MockUmwelt,
    ):
        """Test that successful invoke tracks usage."""

        # Register a world node first
        @dataclass
        class TestNode:
            handle: str = "world.test"

            def affordances(self, observer):
                return ["manifest", "witness", "affordances"]

            def lens(self, aspect):
                return None

            async def manifest(self, observer):
                return BasicRendering(summary="Test", content="Test content")

            async def invoke(self, aspect, observer, **kwargs):
                if aspect == "manifest":
                    return await self.manifest(observer)
                return {"aspect": aspect}

        wired_logos.register("world.test", TestNode())

        result = await wired_logos.invoke("world.test.manifest", architect_umwelt)
        assert len(mock_lgent_registry._usage_log) == 1
        assert mock_lgent_registry._usage_log[0][1] is True  # success

    @pytest.mark.asyncio
    async def test_invoke_tracks_failure(
        self,
        wired_logos: WiredLogos,
        mock_lgent_registry: MockLgentRegistry,
        architect_umwelt: MockUmwelt,
    ):
        """Test that failed invoke tracks usage with error."""
        # Try to invoke with invalid path syntax (will definitely fail)
        with pytest.raises(PathSyntaxError):
            await wired_logos.invoke("invalid", architect_umwelt)

        # No tracking for syntax errors (they fail before invoke)
        # Let's test with a valid path but unavailable affordance instead
        mock_lgent_registry._usage_log.clear()

        # Register a node with limited affordances
        @dataclass
        class LimitedNode:
            handle: str = "world.limited"

            def affordances(self, observer):
                return ["manifest"]  # Only manifest, no "unavailable"

            def lens(self, aspect):
                return None

            async def manifest(self, observer):
                return BasicRendering(summary="Test", content="Test content")

            async def invoke(self, aspect, observer, **kwargs):
                if aspect == "manifest":
                    return await self.manifest(observer)
                raise AffordanceError(
                    f"Aspect '{aspect}' not available",
                    aspect=aspect,
                    observer_archetype="test",
                    available=["manifest"],
                )

        wired_logos.register("world.limited", LimitedNode())

        # Try to invoke unavailable aspect
        with pytest.raises(AffordanceError):
            await wired_logos.invoke("world.limited.unavailable", architect_umwelt)

        # Usage should be tracked with failure
        assert len(mock_lgent_registry._usage_log) == 1
        assert mock_lgent_registry._usage_log[0][1] is False  # failure


# =============================================================================
# Test Convenience Methods
# =============================================================================


class TestConvenienceMethods:
    """Tests for convenience methods."""

    def test_list_handles(self, wired_logos: WiredLogos) -> None:
        """Test listing handles."""
        handles = wired_logos.list_handles()
        assert isinstance(handles, list)

    def test_is_resolved(self, wired_logos: WiredLogos) -> None:
        """Test is_resolved check."""
        assert not wired_logos.is_resolved("world.house")

    def test_clear_cache(
        self,
        wired_logos: WiredLogos,
        mock_lgent_registry: MockLgentRegistry,
    ):
        """Test clearing cache."""
        # Add something to L-gent cache
        wired_logos.integrations.lgent._cache["test"] = "value"

        wired_logos.clear_cache()

        assert len(wired_logos.integrations.lgent._cache) == 0

    def test_get_jit_status(self, wired_logos: WiredLogos) -> None:
        """Test get_jit_status."""
        status = wired_logos.get_jit_status("world.house")
        assert status is None  # Not a JIT node

    def test_list_jit_nodes(self, wired_logos: WiredLogos) -> None:
        """Test list_jit_nodes."""
        nodes = wired_logos.list_jit_nodes()
        assert isinstance(nodes, list)


# =============================================================================
# Test Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_hydrate_lgent_entry_returns_none(self, wired_logos: WiredLogos) -> None:
        """Test that L-gent entries are hydrated via Logos."""
        result = wired_logos._hydrate_lgent_entry(
            MockLgentEntry("test", "test"), "test"
        )
        assert result is None  # Falls back to Logos

    def test_sync_lgent_lookup_no_registry(self) -> None:
        """Test sync lookup without registry returns None."""
        wired = create_minimal_wired_logos()
        result = wired._sync_lgent_lookup("world.house")
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_membrane_without_bridge(self) -> None:
        """Test execute_membrane raises without bridge."""
        wired = create_wired_logos()
        # Remove membrane for test
        wired.integrations = AgentesIntegrations(
            umwelt=wired.integrations.umwelt,
            membrane=None,
            lgent=wired.integrations.lgent,
            ggent=wired.integrations.ggent,
        )

        with pytest.raises(RuntimeError) as exc_info:
            await wired.execute_membrane_command("observe", MockUmwelt())
        assert "not available" in str(exc_info.value)
