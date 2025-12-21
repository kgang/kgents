"""
Tests for AgentFoundry core orchestrator.

Tests the forge pipeline: classify → generate → validate → project → cache
"""

import pytest

from services.foundry import (
    AgentFoundry,
    CacheEntry,
    EphemeralAgentCache,
    ForgeRequest,
    ForgeResponse,
    FoundryState,
    InspectRequest,
)


class TestForgeBasics:
    """Test basic forge operations."""

    @pytest.fixture
    def foundry(self) -> AgentFoundry:
        """Create a fresh foundry instance."""
        return AgentFoundry()

    @pytest.mark.asyncio
    async def test_forge_simple_intent(self, foundry: AgentFoundry) -> None:
        """Forge a simple deterministic intent."""
        request = ForgeRequest(
            intent="parse this text",
            context={},
        )

        response = await foundry.forge(request)

        assert response.success
        assert response.cache_key is not None
        assert response.target in ("local", "cli", "wasm")
        assert response.artifact is not None
        assert response.error is None

    @pytest.mark.asyncio
    async def test_forge_complex_intent(self, foundry: AgentFoundry) -> None:
        """Forge a complex probabilistic intent."""
        request = ForgeRequest(
            intent="analyze and summarize the document then extract key insights",
            context={},
        )

        response = await foundry.forge(request)

        assert response.success
        assert response.cache_key is not None
        assert response.reality in ("deterministic", "probabilistic", "chaotic")
        assert response.artifact is not None

    @pytest.mark.asyncio
    async def test_forge_chaotic_intent(self, foundry: AgentFoundry) -> None:
        """Forge a chaotic intent - should force WASM."""
        request = ForgeRequest(
            intent="do everything forever and always",
            context={},
        )

        response = await foundry.forge(request)

        # Chaotic reality should force WASM for safety
        if response.reality == "chaotic":
            assert response.target == "wasm"
            assert response.forced

    @pytest.mark.asyncio
    async def test_forge_with_interactive_context(self, foundry: AgentFoundry) -> None:
        """Forge with interactive context should prefer marimo."""
        request = ForgeRequest(
            intent="analyze data patterns",
            context={"interactive": True},
        )

        response = await foundry.forge(request)

        assert response.success
        # PROBABILISTIC + interactive → MARIMO
        if response.reality == "probabilistic":
            assert response.target == "marimo"

    @pytest.mark.asyncio
    async def test_forge_with_target_override(self, foundry: AgentFoundry) -> None:
        """Forge with explicit target override."""
        request = ForgeRequest(
            intent="parse JSON data",
            context={},
            target_override="docker",
        )

        response = await foundry.forge(request)

        assert response.success
        assert response.target == "docker"
        assert response.artifact_type == "dockerfile"


class TestForgeCache:
    """Test forge caching behavior."""

    @pytest.fixture
    def foundry(self) -> AgentFoundry:
        """Create a fresh foundry instance."""
        return AgentFoundry()

    @pytest.mark.asyncio
    async def test_cache_hit(self, foundry: AgentFoundry) -> None:
        """Same intent should return cached result."""
        request = ForgeRequest(
            intent="parse CSV files",
            context={},
        )

        # First forge
        response1 = await foundry.forge(request)
        assert response1.success
        key1 = response1.cache_key

        # Second forge - should be cache hit
        response2 = await foundry.forge(request)
        assert response2.success
        assert response2.cache_key == key1

    @pytest.mark.asyncio
    async def test_different_context_different_key(self, foundry: AgentFoundry) -> None:
        """Different context should produce different cache key."""
        request1 = ForgeRequest(
            intent="parse data",
            context={"interactive": True},
        )
        request2 = ForgeRequest(
            intent="parse data",
            context={"production": True},
        )

        response1 = await foundry.forge(request1)
        response2 = await foundry.forge(request2)

        # Same intent but different context → different cache keys
        assert response1.cache_key != response2.cache_key

    @pytest.mark.asyncio
    async def test_cache_stats(self, foundry: AgentFoundry) -> None:
        """Cache stats should update correctly."""
        request = ForgeRequest(intent="test intent")

        # First forge (miss)
        await foundry.forge(request)

        # Second forge (hit)
        await foundry.forge(request)

        manifest = foundry.manifest()
        assert manifest.total_forges == 2
        assert manifest.cache_hits == 1
        assert manifest.cache_hit_rate == 0.5


class TestInspect:
    """Test inspect operations."""

    @pytest.fixture
    def foundry(self) -> AgentFoundry:
        """Create a fresh foundry instance."""
        return AgentFoundry()

    @pytest.mark.asyncio
    async def test_inspect_cached_agent(self, foundry: AgentFoundry) -> None:
        """Inspect a cached ephemeral agent."""
        # First forge something
        request = ForgeRequest(intent="parse JSON")
        forge_response = await foundry.forge(request)
        assert forge_response.success

        # Now inspect it using cache key
        inspect_response = await foundry.inspect(
            InspectRequest(agent_name=forge_response.cache_key or "")
        )

        assert inspect_response.found
        assert inspect_response.is_ephemeral

    @pytest.mark.asyncio
    async def test_inspect_unknown_agent(self, foundry: AgentFoundry) -> None:
        """Inspect an agent that doesn't exist."""
        response = await foundry.inspect(InspectRequest(agent_name="nonexistent-agent-xyz"))

        assert not response.found


class TestFoundryState:
    """Test foundry state machine."""

    @pytest.fixture
    def foundry(self) -> AgentFoundry:
        """Create a fresh foundry instance."""
        return AgentFoundry()

    def test_initial_state(self, foundry: AgentFoundry) -> None:
        """Foundry should start in IDLE state."""
        assert foundry.state == FoundryState.IDLE

    @pytest.mark.asyncio
    async def test_state_returns_to_idle(self, foundry: AgentFoundry) -> None:
        """After forge, state should return to IDLE."""
        request = ForgeRequest(intent="test")
        await foundry.forge(request)

        assert foundry.state == FoundryState.IDLE


class TestManifest:
    """Test manifest generation."""

    @pytest.fixture
    def foundry(self) -> AgentFoundry:
        """Create a fresh foundry instance."""
        return AgentFoundry()

    def test_initial_manifest(self, foundry: AgentFoundry) -> None:
        """Initial manifest should show empty state."""
        manifest = foundry.manifest()

        assert manifest.cache_size == 0
        assert manifest.total_forges == 0
        assert manifest.cache_hits == 0
        assert manifest.status == "operational"

    @pytest.mark.asyncio
    async def test_manifest_after_forge(self, foundry: AgentFoundry) -> None:
        """Manifest should update after forge."""
        await foundry.forge(ForgeRequest(intent="test"))

        manifest = foundry.manifest()

        assert manifest.total_forges == 1
        assert manifest.cache_size == 1

    def test_manifest_to_dict(self, foundry: AgentFoundry) -> None:
        """Manifest to_dict should be JSON-serializable."""
        manifest = foundry.manifest()
        data = manifest.to_dict()

        assert "type" in data
        assert data["type"] == "foundry_manifest"
        assert "cache_size" in data
        assert "status" in data

    def test_manifest_to_text(self, foundry: AgentFoundry) -> None:
        """Manifest to_text should produce readable output."""
        manifest = foundry.manifest()
        text = manifest.to_text()

        assert "Foundry Status" in text
        assert "Cache:" in text
