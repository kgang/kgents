"""
AGENTESE Phase 6: Integration Tests

Tests for:
1. Umwelt Integration - Observer handling, DNA archetype extraction
2. Membrane Integration - CLI command → AGENTESE path mapping
3. L-gent Integration - Registry lookup, node registration
4. G-gent Integration - Grammar validation, BNF parsing
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

import pytest

from ..affordances import ARCHETYPE_AFFORDANCES, ArchetypeDNA
from ..exceptions import PathNotFoundError, PathSyntaxError
from ..integration import (
    # G-gent Integration
    AGENTESE_BNF,
    AGENTESE_CONSTRAINTS,
    AGENTESE_EXAMPLES,
    # Membrane Integration
    MEMBRANE_AGENTESE_MAP,
    # Unified Factory
    create_agentese_integrations,
    create_ggent_integration,
    # L-gent Integration
    create_lgent_integration,
    create_membrane_bridge,
    # Umwelt Integration
    create_umwelt_integration,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@dataclass
class MockDNA:
    """Mock DNA for testing."""

    name: str = "test_agent"
    archetype: str = "default"
    capabilities: tuple[str, ...] = ()


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing."""

    dna: Any = field(default_factory=MockDNA)
    state: Any = None
    gravity: tuple[Any, ...] = ()


@dataclass
class MockCatalogEntry:
    """Mock L-gent CatalogEntry."""

    id: str
    entity_type: str = "agent"
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    keywords: list[str] = field(default_factory=list)
    author: str = "unknown"
    status: str = "active"
    usage_count: int = 0
    success_rate: float = 1.0


class MockLgentRegistry:
    """Mock L-gent registry for testing."""

    def __init__(self) -> None:
        self._entries: dict[str, MockCatalogEntry] = {}
        self._usage_log: list[tuple[str, bool, str | None]] = []

    async def get(self, entry_id: str) -> MockCatalogEntry | None:
        return self._entries.get(entry_id)

    async def register(self, entry: Any) -> None:
        self._entries[entry.id] = entry

    async def record_usage(
        self, entry_id: str, success: bool = True, error: str | None = None
    ) -> None:
        self._usage_log.append((entry_id, success, error))
        if entry_id in self._entries:
            self._entries[entry_id].usage_count += 1

    async def list_by_type(self, entity_type: Any) -> list[MockCatalogEntry]:
        return [e for e in self._entries.values() if e.entity_type == "agent"]


class MockLogos:
    """Mock Logos for testing."""

    def __init__(self) -> None:
        self.invocations: list[tuple[str, Any, dict[str, Any]]] = []
        self._results: dict[str, Any] = {}

    async def invoke(self, path: str, observer: Any, **kwargs: Any) -> Any:
        self.invocations.append((path, observer, kwargs))
        return self._results.get(path, {"path": path, "kwargs": kwargs})

    def set_result(self, path: str, result: Any) -> None:
        self._results[path] = result


@pytest.fixture
def mock_umwelt() -> Any:
    """Create a mock Umwelt."""
    return MockUmwelt()


@pytest.fixture
def architect_umwelt() -> Any:
    """Create an architect Umwelt."""
    return MockUmwelt(dna=MockDNA(name="architect_agent", archetype="architect"))


@pytest.fixture
def mock_logos() -> Any:
    """Create a mock Logos."""
    return MockLogos()


@pytest.fixture
def mock_registry() -> Any:
    """Create a mock L-gent registry."""
    return MockLgentRegistry()


# =============================================================================
# Part 1: Umwelt Integration Tests
# =============================================================================


class TestUmweltIntegration:
    """Tests for Umwelt integration."""

    def test_create_integration(self) -> None:
        """Test integration creation."""
        integration = create_umwelt_integration()
        assert integration is not None
        assert integration.adapter is not None
        assert integration.registry is not None

    def test_extract_meta_default(self, mock_umwelt: Any) -> None:
        """Test extracting meta from default DNA."""
        integration = create_umwelt_integration()
        meta = integration.extract_meta(mock_umwelt)

        assert meta.name == "test_agent"
        assert meta.archetype == "default"
        assert meta.capabilities == ()

    def test_extract_meta_architect(self, architect_umwelt: Any) -> None:
        """Test extracting meta from architect DNA."""
        integration = create_umwelt_integration()
        meta = integration.extract_meta(architect_umwelt)

        assert meta.archetype == "architect"

    def test_extract_meta_archetype_dna(self) -> None:
        """Test extracting meta from ArchetypeDNA."""
        integration = create_umwelt_integration()
        dna = ArchetypeDNA(
            name="custom_agent",
            archetype="scientist",
            capabilities=("experiment", "analyze"),
        )
        umwelt = MockUmwelt(dna=dna)
        meta = integration.extract_meta(cast(Any, umwelt))

        assert meta.name == "custom_agent"
        assert meta.archetype == "scientist"
        assert "experiment" in meta.capabilities

    def test_get_affordances_default(self, mock_umwelt: Any) -> None:
        """Test getting affordances for default archetype."""
        integration = create_umwelt_integration()
        affordances = integration.get_affordances(mock_umwelt)

        # Core affordances always available
        assert "manifest" in affordances
        assert "witness" in affordances
        assert "affordances" in affordances

    def test_get_affordances_architect(self, architect_umwelt: Any) -> None:
        """Test getting affordances for architect archetype."""
        integration = create_umwelt_integration()
        affordances = integration.get_affordances(architect_umwelt)

        # Architect-specific affordances
        assert "renovate" in affordances
        assert "measure" in affordances
        assert "blueprint" in affordances

    def test_can_invoke_core_aspect(self, mock_umwelt: Any) -> None:
        """Test can_invoke for core aspects."""
        integration = create_umwelt_integration()

        assert integration.can_invoke(mock_umwelt, "manifest") is True
        assert integration.can_invoke(mock_umwelt, "witness") is True

    def test_can_invoke_archetype_aspect(self, architect_umwelt: Any) -> None:
        """Test can_invoke for archetype-specific aspects."""
        integration = create_umwelt_integration()

        # Architect can renovate
        assert integration.can_invoke(architect_umwelt, "renovate") is True

    def test_cannot_invoke_restricted_aspect(self, mock_umwelt: Any) -> None:
        """Test that default cannot invoke restricted aspects."""
        integration = create_umwelt_integration()

        # Default cannot demolish (requires architect)
        assert integration.can_invoke(mock_umwelt, "demolish") is False

    @pytest.mark.parametrize("archetype", list(ARCHETYPE_AFFORDANCES.keys()))
    def test_all_archetypes_have_affordances(self, archetype: str) -> None:
        """Test that all standard archetypes return affordances."""
        integration = create_umwelt_integration()
        umwelt = MockUmwelt(dna=MockDNA(archetype=archetype))
        affordances = integration.get_affordances(cast(Any, umwelt))

        # All archetypes get core affordances
        assert "manifest" in affordances
        assert "witness" in affordances


# =============================================================================
# Part 2: Membrane Integration Tests
# =============================================================================


class TestMembraneIntegration:
    """Tests for Membrane CLI integration."""

    def test_membrane_map_exists(self) -> None:
        """Test that membrane command map is populated."""
        assert len(MEMBRANE_AGENTESE_MAP) > 0
        assert "observe" in MEMBRANE_AGENTESE_MAP
        assert "sense" in MEMBRANE_AGENTESE_MAP
        assert "dream" in MEMBRANE_AGENTESE_MAP

    def test_observe_maps_to_world_project_manifest(self) -> None:
        """Test observe command mapping."""
        assert MEMBRANE_AGENTESE_MAP["observe"] == "world.project.manifest"

    def test_sense_maps_to_world_project_sense(self) -> None:
        """Test sense command mapping."""
        assert MEMBRANE_AGENTESE_MAP["sense"] == "world.project.sense"

    def test_trace_maps_to_time_trace_witness(self) -> None:
        """Test trace command mapping."""
        assert MEMBRANE_AGENTESE_MAP["trace"] == "time.trace.witness"

    def test_dream_maps_to_self_memory_consolidate(self) -> None:
        """Test dream command mapping."""
        assert MEMBRANE_AGENTESE_MAP["dream"] == "self.memory.consolidate"

    def test_create_bridge(self, mock_logos: Any) -> None:
        """Test bridge creation."""
        bridge = create_membrane_bridge(mock_logos)
        assert bridge is not None
        assert bridge.logos is mock_logos

    @pytest.mark.asyncio
    async def test_execute_observe(self, mock_logos: Any, mock_umwelt: Any) -> None:
        """Test executing observe command."""
        bridge = create_membrane_bridge(mock_logos)
        result = await bridge.execute("observe", mock_umwelt)

        assert len(mock_logos.invocations) == 1
        path, observer, kwargs = mock_logos.invocations[0]
        assert path == "world.project.manifest"

    @pytest.mark.asyncio
    async def test_execute_trace_with_topic(
        self, mock_logos: Any, mock_umwelt: Any
    ) -> None:
        """Test executing trace command with topic."""
        bridge = create_membrane_bridge(mock_logos)
        result = await bridge.execute("trace", mock_umwelt, topic="authentication")

        path, observer, kwargs = mock_logos.invocations[0]
        assert path == "time.trace.witness"
        assert kwargs["topic"] == "authentication"

    @pytest.mark.asyncio
    async def test_execute_unknown_command_raises(
        self, mock_logos: Any, mock_umwelt: Any
    ) -> None:
        """Test that unknown command raises error."""
        bridge = create_membrane_bridge(mock_logos)

        with pytest.raises(PathNotFoundError) as exc_info:
            await bridge.execute("nonexistent", mock_umwelt)

        assert "nonexistent" in str(exc_info.value)

    def test_register_custom_command(self, mock_logos: Any) -> None:
        """Test registering custom command."""
        bridge = create_membrane_bridge(mock_logos)
        bridge.register_command("custom", "concept.custom.manifest")

        assert bridge.get_path("custom") == "concept.custom.manifest"

    def test_list_commands(self, mock_logos: Any) -> None:
        """Test listing commands."""
        bridge = create_membrane_bridge(mock_logos)
        commands = bridge.list_commands()

        assert len(commands) > 0
        assert any(cmd == "observe" for cmd, path in commands)

    def test_get_path_returns_none_for_unknown(self, mock_logos: Any) -> None:
        """Test get_path returns None for unknown command."""
        bridge = create_membrane_bridge(mock_logos)
        assert bridge.get_path("nonexistent") is None

    @pytest.mark.asyncio
    async def test_parameterized_path(self, mock_logos: Any, mock_umwelt: Any) -> None:
        """Test parameterized path resolution."""
        bridge = create_membrane_bridge(mock_logos)
        result = await bridge.execute("define", mock_umwelt, entity="garden")

        path, _, _ = mock_logos.invocations[0]
        assert path == "world.garden.define"


# =============================================================================
# Part 3: L-gent Integration Tests
# =============================================================================


class TestLgentIntegration:
    """Tests for L-gent registry integration."""

    def test_create_integration_without_registry(self) -> None:
        """Test creating integration without registry."""
        integration = create_lgent_integration()
        assert integration.registry is None

    def test_create_integration_with_registry(self, mock_registry: Any) -> None:
        """Test creating integration with registry."""
        integration = create_lgent_integration(mock_registry)
        assert integration.registry is mock_registry

    @pytest.mark.asyncio
    async def test_lookup_without_registry(self) -> None:
        """Test lookup returns None without registry."""
        integration = create_lgent_integration()
        result = await integration.lookup("world.house")
        assert result is None

    @pytest.mark.asyncio
    async def test_lookup_not_found(self, mock_registry: Any) -> None:
        """Test lookup returns None when not found."""
        integration = create_lgent_integration(mock_registry)
        result = await integration.lookup("world.nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_lookup_found(self, mock_registry: Any) -> None:
        """Test lookup returns entry when found."""
        entry = MockCatalogEntry(id="world.house", name="house")
        mock_registry._entries["world.house"] = entry

        integration = create_lgent_integration(mock_registry)
        result = await integration.lookup("world.house")

        assert result is not None
        assert result.id == "world.house"

    @pytest.mark.asyncio
    async def test_lookup_caches_result(self, mock_registry: Any) -> None:
        """Test that lookup caches results."""
        entry = MockCatalogEntry(id="world.house", name="house")
        mock_registry._entries["world.house"] = entry

        integration = create_lgent_integration(mock_registry)

        # First lookup
        result1 = await integration.lookup("world.house")
        assert result1 is not None

        # Remove from registry
        del mock_registry._entries["world.house"]

        # Second lookup should return cached
        result2 = await integration.lookup("world.house")
        assert result2 is not None
        assert result2.id == "world.house"

    @pytest.mark.asyncio
    async def test_record_invocation_without_registry(self) -> None:
        """Test record_invocation is no-op without registry."""
        integration = create_lgent_integration()
        # Should not raise
        await integration.record_invocation("world.house", success=True)

    @pytest.mark.asyncio
    async def test_record_invocation_with_registry(self, mock_registry: Any) -> None:
        """Test record_invocation logs to registry."""
        entry = MockCatalogEntry(id="world.house", name="house")
        mock_registry._entries["world.house"] = entry

        integration = create_lgent_integration(mock_registry)
        await integration.record_invocation("world.house", success=True)

        assert len(mock_registry._usage_log) == 1
        assert mock_registry._usage_log[0] == ("world.house", True, None)

    @pytest.mark.asyncio
    async def test_record_invocation_failure(self, mock_registry: Any) -> None:
        """Test record_invocation with failure."""
        entry = MockCatalogEntry(id="world.house", name="house")
        mock_registry._entries["world.house"] = entry

        integration = create_lgent_integration(mock_registry)
        await integration.record_invocation(
            "world.house",
            success=False,
            error="Test error",
        )

        assert mock_registry._usage_log[0][1] is False
        assert mock_registry._usage_log[0][2] == "Test error"

    @pytest.mark.asyncio
    async def test_list_handles_without_registry(self) -> None:
        """Test list_handles returns empty without registry."""
        integration = create_lgent_integration()
        handles = await integration.list_handles()
        assert handles == []

    @pytest.mark.asyncio
    async def test_list_handles_with_context(self, mock_registry: Any) -> None:
        """Test list_handles filters by context."""
        mock_registry._entries["world.house"] = MockCatalogEntry(id="world.house")
        mock_registry._entries["world.garden"] = MockCatalogEntry(id="world.garden")
        mock_registry._entries["self.memory"] = MockCatalogEntry(id="self.memory")

        integration = create_lgent_integration(mock_registry)
        handles = await integration.list_handles("world")

        assert "world.house" in handles
        assert "world.garden" in handles
        assert "self.memory" not in handles

    def test_clear_cache(self, mock_registry: Any) -> None:
        """Test clearing the cache."""
        integration = create_lgent_integration(mock_registry)
        integration._cache["test"] = cast(Any, MockCatalogEntry(id="test"))

        integration.clear_cache()
        assert len(integration._cache) == 0


# =============================================================================
# Part 4: G-gent Integration Tests
# =============================================================================


class TestGgentIntegration:
    """Tests for G-gent grammar integration."""

    def test_bnf_exists(self) -> None:
        """Test that BNF grammar is defined."""
        assert len(AGENTESE_BNF) > 0
        assert "PATH" in AGENTESE_BNF
        assert "CONTEXT" in AGENTESE_BNF

    def test_constraints_exist(self) -> None:
        """Test that constraints are defined."""
        assert len(AGENTESE_CONSTRAINTS) > 0
        assert any("five contexts" in c.lower() for c in AGENTESE_CONSTRAINTS)

    def test_examples_exist(self) -> None:
        """Test that examples are defined."""
        assert len(AGENTESE_EXAMPLES) > 0
        assert "world.house.manifest" in AGENTESE_EXAMPLES

    def test_create_integration_without_grammarian(self) -> None:
        """Test creating integration without grammarian."""
        integration = create_ggent_integration()
        assert integration.grammarian is None

    def test_validate_path_valid(self) -> None:
        """Test validating valid paths."""
        integration = create_ggent_integration()

        is_valid, error = integration.validate_path("world.house.manifest")
        assert is_valid is True
        assert error is None

    def test_validate_path_valid_without_aspect(self) -> None:
        """Test validating path without aspect."""
        integration = create_ggent_integration()

        is_valid, error = integration.validate_path("world.house")
        assert is_valid is True

    @pytest.mark.parametrize("path", AGENTESE_EXAMPLES)
    def test_validate_all_examples(self, path: str) -> None:
        """Test that all example paths are valid."""
        integration = create_ggent_integration()
        is_valid, error = integration.validate_path(path)
        assert is_valid is True, f"Example path '{path}' should be valid: {error}"

    def test_validate_path_invalid_context(self) -> None:
        """Test validating path with invalid context."""
        integration = create_ggent_integration()

        is_valid, error = integration.validate_path("invalid.house.manifest")
        assert is_valid is False
        assert error is not None
        assert "context" in error.lower()

    def test_validate_path_too_short(self) -> None:
        """Test validating path that's too short."""
        integration = create_ggent_integration()

        is_valid, error = integration.validate_path("world")
        assert is_valid is False
        assert error is not None
        assert "at least" in error.lower()

    def test_validate_path_invalid_identifier(self) -> None:
        """Test validating path with invalid identifier."""
        integration = create_ggent_integration()

        is_valid, error = integration.validate_path("world.House.manifest")
        assert is_valid is False
        assert error is not None
        assert "invalid" in error.lower()

    def test_validate_path_numeric_identifier(self) -> None:
        """Test validating path with numeric identifier."""
        integration = create_ggent_integration()

        is_valid, error = integration.validate_path("world.123.manifest")
        assert is_valid is False

    def test_parse_path_valid(self) -> None:
        """Test parsing valid path."""
        integration = create_ggent_integration()
        parsed = integration.parse_path("world.house.manifest")

        assert parsed["context"] == "world"
        assert parsed["holon"] == "house"
        assert parsed["aspect"] == "manifest"

    def test_parse_path_without_aspect(self) -> None:
        """Test parsing path without aspect."""
        integration = create_ggent_integration()
        parsed = integration.parse_path("world.house")

        assert parsed["context"] == "world"
        assert parsed["holon"] == "house"
        assert parsed["aspect"] is None

    def test_parse_path_invalid_raises(self) -> None:
        """Test parsing invalid path raises error."""
        integration = create_ggent_integration()

        with pytest.raises(PathSyntaxError):
            integration.parse_path("invalid.path")

    def test_get_bnf(self) -> None:
        """Test getting BNF grammar."""
        integration = create_ggent_integration()
        bnf = integration.get_bnf()

        assert "PATH" in bnf
        assert "CONTEXT" in bnf

    def test_get_constraints(self) -> None:
        """Test getting constraints."""
        integration = create_ggent_integration()
        constraints = integration.get_constraints()

        assert len(constraints) > 0
        # Should be a copy
        constraints.append("new constraint")
        assert len(integration.get_constraints()) == len(AGENTESE_CONSTRAINTS)

    def test_get_examples(self) -> None:
        """Test getting examples."""
        integration = create_ggent_integration()
        examples = integration.get_examples()

        assert len(examples) > 0
        # Should be a copy
        examples.append("new.example")
        assert len(integration.get_examples()) == len(AGENTESE_EXAMPLES)

    @pytest.mark.asyncio
    async def test_reify_without_grammarian_raises(self) -> None:
        """Test that reify raises without grammarian."""
        integration = create_ggent_integration()

        with pytest.raises(RuntimeError) as exc_info:
            await integration.reify_agentese_tongue()

        assert "G-gent not available" in str(exc_info.value)


# =============================================================================
# Part 5: Unified Integration Tests
# =============================================================================


class TestUnifiedIntegrations:
    """Tests for unified AgentesIntegrations."""

    def test_create_minimal(self) -> None:
        """Test creating minimal integrations."""
        integrations = create_agentese_integrations()

        assert integrations.umwelt is not None
        assert integrations.membrane is None
        assert integrations.lgent is not None
        assert integrations.ggent is not None

    def test_create_with_logos(self, mock_logos: Any) -> None:
        """Test creating with Logos for Membrane."""
        integrations = create_agentese_integrations(logos=mock_logos)

        assert integrations.membrane is not None
        assert integrations.membrane.logos is mock_logos

    def test_create_with_registry(self, mock_registry: Any) -> None:
        """Test creating with L-gent registry."""
        integrations = create_agentese_integrations(lgent_registry=mock_registry)

        assert integrations.lgent.registry is mock_registry

    def test_create_full(self, mock_logos: Any, mock_registry: Any) -> None:
        """Test creating with all components."""
        integrations = create_agentese_integrations(
            logos=mock_logos,
            lgent_registry=mock_registry,
        )

        assert integrations.membrane is not None
        assert integrations.lgent.registry is not None

    def test_is_fully_integrated_false(self) -> None:
        """Test is_fully_integrated returns False when missing components."""
        integrations = create_agentese_integrations()
        assert integrations.is_fully_integrated() is False

    def test_is_fully_integrated_true(
        self, mock_logos: Any, mock_registry: Any
    ) -> None:
        """Test is_fully_integrated returns True when all present."""

        # Mock grammarian
        class MockGrammarian:
            pass

        integrations = create_agentese_integrations(
            logos=mock_logos,
            lgent_registry=mock_registry,
            grammarian=MockGrammarian(),
        )
        assert integrations.is_fully_integrated() is True

    def test_available_integrations_minimal(self) -> None:
        """Test available_integrations with minimal setup."""
        integrations = create_agentese_integrations()
        available = integrations.available_integrations()

        assert "umwelt" in available
        assert "membrane" not in available

    def test_available_integrations_full(
        self, mock_logos: Any, mock_registry: Any
    ) -> None:
        """Test available_integrations with full setup."""

        class MockGrammarian:
            pass

        integrations = create_agentese_integrations(
            logos=mock_logos,
            lgent_registry=mock_registry,
            grammarian=MockGrammarian(),
        )
        available = integrations.available_integrations()

        assert "umwelt" in available
        assert "membrane" in available
        assert "lgent" in available
        assert "ggent" in available


# =============================================================================
# Part 6: Cross-Integration Tests
# =============================================================================


class TestCrossIntegration:
    """Tests for cross-integration scenarios."""

    @pytest.mark.asyncio
    async def test_membrane_to_logos_to_lgent(
        self, mock_logos: Any, mock_registry: Any, mock_umwelt: Any
    ) -> None:
        """Test Membrane → Logos → L-gent flow."""
        # Setup
        entry = MockCatalogEntry(id="world.project", name="project")
        mock_registry._entries["world.project"] = entry

        integrations = create_agentese_integrations(
            logos=mock_logos,
            lgent_registry=mock_registry,
        )

        # Execute observe via Membrane
        assert integrations.membrane is not None
        result = await integrations.membrane.execute("observe", mock_umwelt)

        # Verify Logos was called
        assert len(mock_logos.invocations) == 1
        path, _, _ = mock_logos.invocations[0]
        assert path == "world.project.manifest"

        # Record invocation in L-gent
        await integrations.lgent.record_invocation("world.project", success=True)
        assert mock_registry._usage_log[0][0] == "world.project"

    def test_umwelt_extract_for_affordance_check(self, architect_umwelt: Any) -> None:
        """Test extracting meta for affordance checking."""
        integrations = create_agentese_integrations()

        # Extract meta
        meta = integrations.umwelt.extract_meta(architect_umwelt)

        # Check affordances
        affordances = integrations.umwelt.get_affordances(architect_umwelt)

        # Validate with G-gent
        for path in ["world.house.renovate", "world.house.blueprint"]:
            is_valid, _ = integrations.ggent.validate_path(path)
            assert is_valid is True

            # Extract aspect
            parsed = integrations.ggent.parse_path(path)
            aspect = parsed["aspect"]

            # Check if architect can invoke this aspect
            can_invoke = aspect in affordances
            assert can_invoke is True

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, mock_umwelt: Any) -> None:
        """Test that integrations work even with missing components."""
        # Create with only Umwelt (minimal)
        integrations = create_agentese_integrations()

        # Umwelt still works
        meta = integrations.umwelt.extract_meta(mock_umwelt)
        assert meta.name == "test_agent"

        # L-gent lookup returns None (graceful)
        result = await integrations.lgent.lookup("world.house")
        assert result is None

        # L-gent record is no-op (graceful)
        await integrations.lgent.record_invocation("world.house", success=True)

        # G-gent validation still works (no grammarian needed)
        is_valid, _ = integrations.ggent.validate_path("world.house.manifest")
        assert is_valid is True
