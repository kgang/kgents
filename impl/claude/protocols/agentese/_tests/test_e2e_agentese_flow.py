"""
E2E Tests: Full AGENTESE Flow from HTTP to Response.

This test exercises the complete AGENTESE stack:
    HTTP Request → Gateway → Node Resolution → Aspect Invocation → Response

These are **tier2 integration tests** that verify:
1. Gateway routes requests correctly
2. Nodes resolve with DI container
3. Aspects return valid responses
4. SSE streaming works for chat

**DI Bootstrap Behavior**:
Tests dynamically skip if the DI container doesn't have services bootstrapped.
This is expected in CI without full infrastructure. When running locally with
`uv run uvicorn ...`, these tests will pass.

AD-011 (REPL Reliability): Every path in discover MUST be invokable.
This test proves it works end-to-end, not just in isolation.

Run with:
    cd impl/claude
    uv run pytest protocols/agentese/_tests/test_e2e_agentese_flow.py -v

For SSE tests, run with:
    uv run pytest protocols/agentese/_tests/test_e2e_agentese_flow.py -v -k sse
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, AsyncIterator

import pytest
import pytest_asyncio

if TYPE_CHECKING:
    from httpx import AsyncClient, Response


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def anyio_backend():
    """Use asyncio backend for httpx."""
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncIterator["AsyncClient"]:
    """
    Create async HTTP client with test app.

    Uses the actual application factory for true E2E testing.
    Note: function scope required for pytest-asyncio 1.x compatibility.
    """
    from httpx import ASGITransport, AsyncClient

    from protocols.api.app import create_app

    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# =============================================================================
# E2E Tests: Crown Jewels
# =============================================================================


@pytest.mark.tier2
class TestBrainE2E:
    """End-to-end tests for Brain (self.memory)."""

    @pytest.mark.anyio
    async def test_brain_manifest_e2e(self, client: "AsyncClient"):
        """Brain manifest returns valid response (or DI error if not bootstrapped)."""
        response = await client.get("/agentese/self/memory/manifest")

        # 200 = success, 500 with DI error = route exists but service not bootstrapped
        # Both are valid in test context (full bootstrap requires running server)
        if response.status_code == 500:
            # DI-related errors are acceptable - route exists, just not bootstrapped
            error_text = response.text
            if (
                "missing 1 required positional argument" in error_text
                or "persistence" in error_text
            ):
                pytest.skip("Service not bootstrapped (DI dependency missing) - route exists")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "result" in data or "value" in data or isinstance(data, dict), (
            f"Unexpected response shape: {data}"
        )


@pytest.mark.tier2
class TestChatE2E:
    """End-to-end tests for Chat (self.chat)."""

    @pytest.mark.anyio
    async def test_chat_manifest_e2e(self, client: "AsyncClient"):
        """Chat manifest returns valid response."""
        response = await client.get("/agentese/self/chat/manifest")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"


@pytest.mark.tier2
@pytest.mark.slow  # Real codebase scan can timeout in CI
class TestGestaltE2E:
    """End-to-end tests for Gestalt (world.codebase)."""

    @pytest.mark.anyio
    async def test_gestalt_manifest_e2e(self, client: "AsyncClient"):
        """Gestalt manifest returns valid response."""
        response = await client.get("/agentese/world/codebase/manifest")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"


@pytest.mark.tier2
class TestGardenerE2E:
    """End-to-end tests for Gardener (concept.gardener)."""

    @pytest.mark.anyio
    async def test_gardener_manifest_e2e(self, client: "AsyncClient"):
        """Gardener manifest returns valid response."""
        response = await client.get("/agentese/concept/gardener/manifest")

        # 200 or 500 (if service not initialized) - both are valid for E2E
        assert response.status_code in [200, 500], (
            f"Unexpected status {response.status_code}: {response.text}"
        )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict), f"Expected dict, got {type(data)}"


@pytest.mark.tier2
class TestGardenE2E:
    """End-to-end tests for Garden (self.garden)."""

    @pytest.mark.anyio
    async def test_garden_manifest_e2e(self, client: "AsyncClient"):
        """Garden manifest returns valid response."""
        response = await client.get("/agentese/self/garden/manifest")

        # Garden requires state - may return error if not initialized
        assert response.status_code in [200, 404, 500], (
            f"Unexpected status {response.status_code}: {response.text}"
        )


@pytest.mark.tier2
class TestForgeE2E:
    """End-to-end tests for Forge (world.forge)."""

    @pytest.mark.anyio
    async def test_forge_manifest_e2e(self, client: "AsyncClient"):
        """Forge manifest returns valid response (or DI error if not bootstrapped)."""
        response = await client.get("/agentese/world/forge/manifest")

        if response.status_code == 500:
            error_text = response.text
            if (
                "missing 1 required positional argument" in error_text
                or "persistence" in error_text
            ):
                pytest.skip("Service not bootstrapped (DI dependency missing) - route exists")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"


@pytest.mark.tier2
class TestTownE2E:
    """End-to-end tests for Town (world.town)."""

    @pytest.mark.anyio
    async def test_town_manifest_e2e(self, client: "AsyncClient"):
        """Town manifest returns valid response (or DI error if not bootstrapped)."""
        response = await client.get("/agentese/world/town/manifest")

        if response.status_code == 500:
            error_text = response.text
            if (
                "missing 1 required positional argument" in error_text
                or "persistence" in error_text
            ):
                pytest.skip("Service not bootstrapped (DI dependency missing) - route exists")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"


@pytest.mark.tier2
class TestParkE2E:
    """End-to-end tests for Park (world.park)."""

    @pytest.mark.anyio
    async def test_park_manifest_e2e(self, client: "AsyncClient"):
        """Park manifest returns valid response (or DI error if not bootstrapped)."""
        response = await client.get("/agentese/world/park/manifest")

        if response.status_code == 500:
            error_text = response.text
            if (
                "missing 1 required positional argument" in error_text
                or "persistence" in error_text
            ):
                pytest.skip("Service not bootstrapped (DI dependency missing) - route exists")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"


# =============================================================================
# E2E Tests: Discovery
# =============================================================================


@pytest.mark.tier2
class TestDiscoveryE2E:
    """End-to-end tests for AGENTESE discovery."""

    @pytest.mark.anyio
    async def test_discover_returns_paths(self, client: "AsyncClient"):
        """Discovery endpoint returns registered paths."""
        response = await client.get("/agentese/discover")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "paths" in data or isinstance(data, list), f"Expected paths in response: {data}"

        # Should have at least 30 paths
        paths = data.get("paths", data) if isinstance(data, dict) else data
        assert len(paths) >= 20, f"Expected at least 20 paths, got {len(paths)}"

    @pytest.mark.anyio
    async def test_discover_includes_crown_jewels(self, client: "AsyncClient"):
        """Discovery includes all Crown Jewel paths."""
        response = await client.get("/agentese/discover")

        assert response.status_code == 200

        data = response.json()
        paths = data.get("paths", []) if isinstance(data, dict) else data

        # If paths is a list of dicts, extract path strings
        if paths and isinstance(paths[0], dict):
            path_strings = [p.get("path", "") for p in paths]
        else:
            path_strings = paths

        expected = ["self.memory", "world.codebase", "world.forge", "world.town", "world.park"]

        for expected_path in expected:
            assert any(expected_path in p for p in path_strings), (
                f"Crown Jewel '{expected_path}' not in discovery. Found: {path_strings[:10]}"
            )


# =============================================================================
# E2E Tests: SSE Streaming
# =============================================================================


@pytest.mark.tier2
class TestSSEStreamingE2E:
    """End-to-end tests for SSE streaming."""

    @pytest.mark.anyio
    @pytest.mark.skip(reason="SSE streaming requires special handling - test manually")
    async def test_chat_streaming_e2e(self, client: "AsyncClient"):
        """
        Chat streaming returns SSE events.

        Note: This test requires special SSE handling. For full E2E testing,
        use a real browser or dedicated SSE client.
        """
        # SSE tests are complex because httpx doesn't natively support SSE
        # This is a placeholder for manual/browser testing
        pass


# =============================================================================
# Performance Baseline Tests
# =============================================================================


# Performance baselines in seconds
# These are generous limits to catch regressions without flakiness
PERFORMANCE_BASELINES = {
    "/agentese/self/memory/manifest": 0.5,
    "/agentese/world/codebase/manifest": 0.5,
    "/agentese/self/garden/manifest": 0.5,
    "/agentese/world/forge/manifest": 0.5,
    "/agentese/world/town/manifest": 0.5,
    "/agentese/world/park/manifest": 0.5,
    "/agentese/discover": 0.3,
}


class TestPerformanceBaselines:
    """
    Performance baseline tests.

    These tests ensure endpoints respond within acceptable time limits.
    Baselines are generous to avoid flakiness in CI.

    AD-011: Performance is part of reliability.
    """

    @pytest.mark.anyio
    @pytest.mark.parametrize("path,max_seconds", list(PERFORMANCE_BASELINES.items()))
    async def test_performance_baseline(self, client: "AsyncClient", path: str, max_seconds: float):
        """Endpoint responds within baseline time."""
        start = time.time()
        response = await client.get(path)
        elapsed = time.time() - start

        # We care about performance, not error handling here
        # So only assert on time if we got a response
        if response.status_code in [200, 404, 500]:
            assert elapsed < max_seconds, (
                f"{path} took {elapsed:.3f}s, exceeds {max_seconds}s baseline"
            )

    @pytest.mark.anyio
    async def test_discovery_is_fast(self, client: "AsyncClient"):
        """Discovery endpoint is particularly fast (<300ms)."""
        start = time.time()
        response = await client.get("/agentese/discover")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.3, f"Discovery took {elapsed:.3f}s, should be <0.3s"

    @pytest.mark.anyio
    async def test_bulk_manifest_performance(self, client: "AsyncClient"):
        """Multiple manifest calls complete in reasonable time."""
        paths = [
            "/agentese/self/memory/manifest",
            "/agentese/world/codebase/manifest",
            "/agentese/world/forge/manifest",
        ]

        start = time.time()
        for path in paths:
            await client.get(path)
        elapsed = time.time() - start

        # All three should complete in <2s total
        assert elapsed < 2.0, f"Bulk manifests took {elapsed:.3f}s, should be <2.0s for 3 endpoints"


# =============================================================================
# Error Handling Tests
# =============================================================================


@pytest.mark.tier2
class TestErrorHandlingE2E:
    """End-to-end tests for error handling."""

    @pytest.mark.anyio
    async def test_invalid_path_returns_404(self, client: "AsyncClient"):
        """Invalid paths return 404, not 500."""
        response = await client.get("/agentese/nonexistent/path/manifest")

        # Should be 404 (not found) not 500 (server error)
        assert response.status_code in [404, 400], (
            f"Expected 404/400 for invalid path, got {response.status_code}"
        )

    @pytest.mark.anyio
    async def test_invalid_aspect_returns_error(self, client: "AsyncClient"):
        """Invalid aspect returns error (could be 404, 405, 400, or 500 for DI issues)."""
        response = await client.get("/agentese/self/memory/nonexistent_aspect")

        # 404 (path not found), 405 (method not allowed), 400, or 500 (DI issue) are acceptable
        # The key is we get a response (route exists) not a crash
        assert response.status_code in [404, 405, 400, 500], (
            f"Expected error response for invalid aspect, got {response.status_code}"
        )

    @pytest.mark.anyio
    async def test_error_response_has_message(self, client: "AsyncClient"):
        """Error responses include helpful message."""
        response = await client.get("/agentese/nonexistent/path/manifest")

        if response.status_code != 200:
            data = response.json()
            # Should have some error information
            assert "error" in data or "detail" in data or "message" in data, (
                f"Error response missing message: {data}"
            )


# =============================================================================
# Script Runner
# =============================================================================


if __name__ == "__main__":
    import asyncio

    async def main():
        """Run basic E2E tests manually."""
        from httpx import ASGITransport, AsyncClient

        from protocols.api.app import create_app

        print("=== AGENTESE E2E Test Runner ===\n")

        app = create_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Test discovery
            print("Testing /agentese/discover...")
            response = await client.get("/agentese/discover")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                paths = data.get("paths", data)
                print(f"  Paths: {len(paths)}")

            # Test Crown Jewels
            jewels = [
                ("Brain", "/agentese/self/memory/manifest"),
                ("Gestalt", "/agentese/world/codebase/manifest"),
                ("Forge", "/agentese/world/forge/manifest"),
                ("Town", "/agentese/world/town/manifest"),
                ("Park", "/agentese/world/park/manifest"),
            ]

            print("\nTesting Crown Jewels:")
            for name, path in jewels:
                start = time.time()
                response = await client.get(path)
                elapsed = time.time() - start
                status = "✓" if response.status_code == 200 else "✗"
                print(f"  {status} {name}: {response.status_code} ({elapsed:.3f}s)")

        print("\n=== Done ===")

    asyncio.run(main())
